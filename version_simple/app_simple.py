"""
Versión simple para presentar.      streamlit run app_simple.py
"""
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from punto_fijo import (capacidad, derivada_g, g, punto_fijo, recursos,
                        simular, solucion_exacta, trafico_maximo)

st.set_page_config(page_title="¿Cuántos servidores necesito?", page_icon="🖥️", layout="wide")

# Estilo de las gráficas
AZUL, VERDE, NARANJA, ROJO, GRIS = "#4ea8ff", "#3ddc97", "#ffb547", "#ff5d6c", "#8193a8"
plt.rcParams.update({"figure.facecolor": "#121820", "axes.facecolor": "#121820",
                     "axes.edgecolor": "#243040", "axes.labelcolor": GRIS, "text.color": "#dbe4ee",
                     "xtick.color": GRIS, "ytick.color": GRIS, "grid.color": "#243040",
                     "axes.grid": True, "legend.frameon": False, "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False})

# ---------------------------------------------------------------- controles
st.sidebar.header("⚙️ Datos del problema")
lam = st.sidebar.slider("Tráfico actual λ (peticiones/seg)", 100, 1000, 600, 10)
C = st.sidebar.slider("Capacidad de 1 servidor C (peticiones/seg)", 50, 300, 100, 10)
p = st.sidebar.slider("Pérdida por coordinación p", 0.0005, 0.01, 0.002, 0.0005, format="%.4f")
tol = st.sidebar.select_slider("Tolerancia del error", [1e-3, 1e-4, 1e-6, 1e-8], value=1e-6)
st.sidebar.caption("Objetivo fijo: que los servidores trabajen al **80 %**.")

st.title("🖥️ ¿Cuántos servidores necesito?")
st.markdown("##### Asignación automática de servidores en la nube con el **método de Punto Fijo**")

# ---------------------------------------------------------------- 1. problema
st.header("1 · El problema")
c1, c2, c3 = st.columns(3)
c1.info("📈 **El tráfico de una app crece** y hay que decidir cuántos servidores encender.")
c2.warning("⚠️ **Pocos servidores** → se saturan y la app se cae.  \n**Muchos** → se paga de más.")
c3.success("🎯 **Meta:** que cada servidor trabaje al **80 %**, con margen para picos.")

# ---------------------------------------------------------------- 2. ecuación
st.header("2 · La ecuación")
st.markdown("Con más servidores se pierde tiempo **coordinándolos**, así que no rinden el 100 %. "
            "La capacidad real de **N** servidores es:")
st.latex(r"X(N)=\frac{C\cdot N}{1+p\,N(N-1)}")
st.markdown("Queremos que trabajen al 80 %:  **0.8 · X(N) = λ**.  Despejando N:")
st.latex(r"N = g(N)=\frac{\lambda}{0.8\,C}\left(1+p\,N(N-1)\right)")
st.markdown(f"Con los datos actuales:  **N = {lam/(0.8*C):.3f} · (1 + {p} · N(N − 1))**. "
            "N aparece en los dos lados → se resuelve **iterando**:")
st.latex(r"N_{k+1}=g(N_k),\qquad N_0=\frac{\lambda}{0.8\,C}\;\text{(como si no hubiera pérdidas)}")

# ---------------------------------------------------------------- 3. iteraciones
st.header("3 · Resolviendo con Punto Fijo")
N, tabla, ok = punto_fijo(lam, C, p, tol=tol)
N_pico, lam_max = trafico_maximo(C, p)

if not ok:
    st.error(f"🔴 **No hay solución:** el tráfico ({lam} req/s) supera el máximo que pueden atender los "
             f"servidores al 80 % (**{lam_max:.0f} req/s**). Agregar más servidores ya no ayuda, "
             "porque se pierde más tiempo coordinándolos de lo que se gana. El método **diverge**.")
else:
    rec = recursos(N, lam, C, p)
    m = st.columns(5)
    m[0].metric("Resultado N*", f"{N:.4f}")
    m[1].metric("Servidores a encender", rec["servidores"], help="Se redondea hacia arriba")
    m[2].metric("CPU / RAM", f"{rec['vcpu']} vCPU · {rec['ram_gb']} GB")
    m[3].metric("Uso real", f"{rec['uso']:.1%}")
    m[4].metric("Iteraciones", len(tabla))

izq, der = st.columns([1, 1])
with izq:
    st.markdown("**Tabla de iteraciones**")
    df = pd.DataFrame(tabla)
    st.dataframe(df.style.format({"N_k": "{:.6f}", "g(N_k)": "{:.6f}", "error": "{:.2e}"}),
                 hide_index=True, use_container_width=True, height=360)
    if ok:
        exacta = solucion_exacta(lam, C, p)
        st.success(f"✅ **Comprobación:** la ecuación también es cuadrática. Con la fórmula general "
                   f"N = {exacta:.6f}. Diferencia con punto fijo: {abs(exacta - N):.1e}")

with der:
    st.markdown("**Diagrama de telaraña:** cada escalón es una iteración")
    xs = [tabla[0]["N_k"]] + [f["g(N_k)"] for f in tabla]
    if ok:   # zoom a la zona de las iteraciones para que se vean los escalones
        xmin, xmax = min(xs) * 0.93, max(xs) * 1.04
    else:
        xmin, xmax = 0, N_pico * 2.5
    fig, ax = plt.subplots(figsize=(6, 4.6), dpi=110)
    x = np.linspace(xmin, xmax, 300)
    ax.plot(x, g(x, lam, C, p), color=AZUL, lw=2.5, label="y = g(N)")
    ax.plot([xmin, xmax], [xmin, xmax], "--", color=GRIS, label="y = N")
    wx, wy = [xs[0]], [xmin]
    for a, b in zip(xs[:-1], xs[1:]):
        if b > xmax * 2:
            break
        wx += [a, b]; wy += [b, b]
    ax.plot(wx, wy, color=NARANJA, lw=1.4, marker="o", ms=3, label="iteraciones")
    if ok:
        ax.plot(N, N, "o", color=VERDE, ms=11, label=f"N* = {N:.3f}")
    ax.set_xlim(xmin, xmax); ax.set_ylim(xmin, xmax); ax.set_xlabel("N"); ax.set_ylabel("g(N)")
    ax.legend(loc="lower right"); fig.tight_layout()
    st.pyplot(fig); plt.close(fig)

# ---------------------------------------------------------------- 4. por qué converge
st.header("4 · ¿Por qué converge?")
st.markdown("El teorema del punto fijo dice que el método converge si **|g′(N\\*)| < 1**:")
st.latex(r"g'(N)=\frac{\lambda}{0.8\,C}\;p\,(2N-1)")
if ok:
    d = derivada_g(N, lam, C, p)
    st.markdown(f"Aquí **g′(N\\*) = {d:.3f} < 1 ✅**. En cada iteración el error se multiplica "
                f"aproximadamente por {d:.2f}.")
st.markdown(f"**Lo interesante:** g′ < 1 pasa justo cuando agregar servidores **todavía sirve**. "
            f"Con estos datos, el máximo es **{lam_max:.0f} req/s** (con {N_pico:.1f} servidores). "
            "Si el tráfico pasa ese límite, el método diverge, y eso es justo lo que le ocurre "
            "al sistema: **se satura**.")

# ---------------------------------------------------------------- 5. simulación
st.header("5 · Simulación: el tráfico crece exponencialmente")
c1, c2 = st.columns(2)
lam0 = c1.slider("Tráfico inicial λ₀", 50, 500, 200, 10)
r = c2.slider("Velocidad de crecimiento r (por minuto)", 0.01, 0.06, 0.03, 0.005)
st.markdown(f"λ(t) = {lam0} · e^({r}·t).  Cada minuto el programa vuelve a resolver la ecuación con Punto Fijo.")
sim = pd.DataFrame(simular(lam0, r, C, p, minutos=60))

fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4), dpi=110)
sat = sim[sim["estado"] == "SATURADO"]
for ax in (a1, a2):
    if len(sat):
        ax.axvspan(sat["minuto"].min() - 0.5, 60.5, color=ROJO, alpha=.13, label="saturado")
a1.plot(sim["minuto"], sim["trafico"], color=AZUL, lw=2, label="tráfico λ(t)")
a1.axhline(lam_max, color=ROJO, ls="--", lw=1.2, label=f"máximo {lam_max:.0f} req/s")
a1.set_xlabel("minuto"); a1.set_ylabel("peticiones/seg"); a1.legend(); a1.set_title("Tráfico", fontsize=11)
a2.step(sim["minuto"], sim["servidores"], where="mid", color=VERDE, lw=2, label="servidores encendidos")
a2b = a2.twinx()
a2b.plot(sim["minuto"], sim["iteraciones"], color=NARANJA, lw=1.2, ls=":", label="iteraciones")
a2b.set_ylabel("iteraciones", color=NARANJA); a2b.tick_params(colors=NARANJA); a2b.grid(False)
a2.set_xlabel("minuto"); a2.set_ylabel("servidores"); a2.set_title("Servidores e iteraciones", fontsize=11)
h1, l1 = a2.get_legend_handles_labels(); h2, l2 = a2b.get_legend_handles_labels()
a2.legend(h1 + h2, l1 + l2, loc="upper left")
fig.tight_layout(); st.pyplot(fig); plt.close(fig)

if len(sat):
    st.error(f"🔴 En el minuto **{int(sat['minuto'].min())}** el tráfico supera el máximo: hay que usar "
             "servidores más potentes (subir C) o limitar el tráfico.")
st.info("💡 Fíjate en las **iteraciones**: suben cuando el sistema se acerca al límite. "
        "El método numérico avisa **antes** de que el servidor colapse.")

# ---------------------------------------------------------------- conclusiones
st.header("6 · Conclusiones")
st.markdown("""
1. El problema de **cuántos servidores encender** se convierte en una ecuación **N = g(N)**.
2. El **método de Punto Fijo** la resuelve en pocas iteraciones y coincide con la solución exacta.
3. La condición **|g′| < 1** tiene un significado real: mientras se cumple, el sistema puede crecer.
4. Cuando el método **diverge**, el sistema está **saturado**. La matemática detecta el problema.
""")
