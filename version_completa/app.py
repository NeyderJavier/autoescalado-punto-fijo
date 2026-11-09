"""
Panel DevOps de autoescalado por métodos numéricos.

    pip install -r requirements.txt
    streamlit run app.py
"""
import time
from dataclasses import replace

import numpy as np
import pandas as pd
import streamlit as st

from nucleo import balance as bl
from nucleo import graficas as gr
from nucleo import modelo as md
from nucleo import simulador as sm

st.set_page_config(page_title="Autoescalado · Métodos Numéricos", page_icon="🖥️", layout="wide")


# ============================================================================
# Barra lateral: parámetros
# ============================================================================
sb = st.sidebar
sb.title("⚙️ Parámetros")

sb.subheader("Tráfico λ(t)")
modelo_txt = sb.selectbox("Modelo de crecimiento", ["Exponencial", "Logarítmico", "Datos CSV"])
pt = md.ParametrosTrafico()
pt.modelo = {"Exponencial": "exponencial", "Logarítmico": "logaritmico", "Datos CSV": "csv"}[modelo_txt]
if pt.modelo == "csv":
    archivo = sb.file_uploader("CSV con columna 'req_s' (una fila por minuto)", type="csv")
    try:
        datos = pd.read_csv(archivo) if archivo else pd.read_csv("datos/trafico_ejemplo.csv")
        col = "req_s" if "req_s" in datos.columns else datos.select_dtypes("number").columns[-1]
        pt.datos_csv = datos[col].to_numpy(dtype=float)
        if not archivo:
            sb.caption("Usando datos/trafico_ejemplo.csv (sintético).")
    except Exception as e:
        sb.error(f"No se pudo leer el CSV: {e}")
        st.stop()
else:
    pt.lambda0 = sb.slider("λ₀ tráfico inicial (req/s)", 20, 1000, 200, 10)
    if pt.modelo == "exponencial":
        pt.r = sb.slider("r tasa de crecimiento (1/min)", 0.001, 0.05, 0.010, 0.001, format="%.3f")
    else:
        pt.A = sb.slider("A amplitud (req/s)", 50, 1000, 200, 10)
        pt.b = sb.slider("b escala", 0.05, 2.0, 0.5, 0.05)
pt.ruido = sb.slider("Ruido aleatorio (±)", 0.0, 0.2, 0.05, 0.01)
if sb.checkbox("Pico de tráfico (evento viral / ataque)", value=True):
    c1, c2, c3 = sb.columns(3)
    pt.picos = [(c1.number_input("Inicio", 0, 1000, 90), c2.number_input("Duración", 1, 120, 8),
                 c3.number_input("Factor", 1.0, 5.0, 1.6, 0.1))]
pt.semilla = sb.number_input("Semilla aleatoria", 0, 9999, 7)

sb.subheader("Servidor")
s = md.ParametrosServidor()
s.X1 = sb.slider("X₁ capacidad por réplica (req/s)", 40, 400, 120, 10)
s.sigma = sb.slider("σ contención", 0.0, 0.15, 0.03, 0.005, format="%.3f")
s.kappa = sb.slider("κ coherencia", 0.0001, 0.003, 0.0004, 0.0001, format="%.4f")
s.rho = sb.slider("ρ utilización objetivo", 0.5, 0.95, 0.80, 0.01)
s.termico = sb.checkbox("Modelo térmico (throttling por calor del rack)", value=True)
if s.termico:
    s.T_throttle = sb.slider("T de throttling (°C)", 55.0, 85.0, 70.0, 1.0)
    s.h_rack = sb.slider("Calor por réplica en el rack (°C)", 0.0, 1.0, 0.35, 0.05)

sb.subheader("Autoescalador")
cfg = sm.ConfigSimulacion()
cfg.minutos = sb.slider("Duración (min)", 30, 480, 180, 10)
cfg.estrategia = sb.radio("Estrategia", ["reactiva", "predictiva"], horizontal=True)
cfg.metodo = sb.selectbox("Método numérico del autoescalador", bl.METODOS)
cfg.warm_start = sb.checkbox("Warm start (usar N* anterior como semilla)", value=True)
cfg.arranque_min = sb.slider("Arranque en frío de un contenedor (min)", 0, 10, 3)
cfg.cooldown_min = sb.slider("Cooldown para reducir réplicas (min)", 0, 20, 5)
cfg.tol = 10.0 ** sb.slider("Tolerancia 10^x", -12, -3, -8)
cfg.max_iter = sb.slider("Máx. iteraciones", 20, 500, 200, 10)


# ============================================================================
# Cálculos cacheados
# ============================================================================
@st.cache_data(show_spinner="Simulando…")
def correr(pt_, s_, cfg_):
    lam = md.serie_trafico(pt_, cfg_.minutos)
    return lam, sm.simular(lam, s_, cfg_)


@st.cache_resource(show_spinner="Calculando mapa de sensibilidad…")
def fig_mapa(s_):
    return gr.mapa_sensibilidad(s_)


@st.cache_resource(show_spinner="Barriendo λ…")
def fig_conv(s_, tol):
    return gr.convergencia_vs_lambda(s_, tol)


lam_serie, df = correr(pt, s, cfg)
lim = bl.limites(s)

# ============================================================================
# Encabezado
# ============================================================================
st.title("🖥️ Autoescalado de contenedores con métodos numéricos")
st.caption("Ecuación de balance  ρ·X_eff(N) = λ(t)  resuelta en cada minuto · "
           f"pico de capacidad N = {lim.n_pico:.1f} réplicas · λ_máx sostenible = {lim.lambda_max:,.0f} req/s")

tabs = st.tabs(["📟 Panel en vivo", "🧮 Métodos numéricos", "⚖️ Reactivo vs predictivo",
                "🔬 Análisis de convergencia", "📚 Fundamento teórico"])


# ============================================================================
# 1. Panel en vivo
# ============================================================================
def eventos(d: pd.DataFrame) -> list[str]:
    log = []
    prev, sat_prev = None, False
    for _, f in d.iterrows():
        t, n = int(f.minuto), int(f.activas + f.en_arranque)
        if prev is not None and n != prev:
            accion = "⬆️ Scale-up" if n > prev else "⬇️ Scale-down"
            log.append(f"`t={t:>3}` {accion}: {prev} → {n} réplicas (λ={f['lambda']:.0f} req/s, "
                       f"{int(f.iteraciones)} iter.)")
        if f.saturado and not sat_prev:
            log.append(f"`t={t:>3}` 🔴 **Saturación**: λ supera λ_máx; el método no tiene punto fijo estable.")
        if f.violacion_sla and not f.saturado:
            log.append(f"`t={t:>3}` 🟠 Utilización {f.utilizacion:.0%} (réplicas aún arrancando).")
        prev, sat_prev = n, f.saturado
    return log[::-1]


with tabs[0]:
    c1, c2 = st.columns([4, 1])
    minuto = c1.slider("Minuto a inspeccionar", 0, cfg.minutos - 1, cfg.minutos - 1)
    reproducir = c2.button("▶ Reproducir", use_container_width=True)
    paso = c2.number_input("Paso", 1, 20, 3, label_visibility="collapsed")

    zona_kpi = st.empty()
    g1, g2 = st.columns(2)
    zona_traf, zona_rep = g1.empty(), g2.empty()
    g3, g4 = st.columns(2)
    zona_ut, zona_log = g3.empty(), g4.empty()

    def pintar(t):
        f = df.iloc[t]
        with zona_kpi.container():
            k = st.columns(8)
            k[0].metric("Tráfico λ", f"{f['lambda']:,.0f} req/s")
            k[1].metric("Réplicas activas", int(f.activas),
                        delta=f"+{int(f.en_arranque)} arrancando" if f.en_arranque else None)
            k[2].metric("N*", "—" if f.saturado else f"{f.n_star:.4f}")
            k[3].metric("CPU", f"{int(f.vcpu)} vCPU")
            k[4].metric("RAM", f"{f.ram_gb:.2f} GB")
            k[5].metric("Utilización", f"{f.utilizacion:.1%}",
                        delta=f"{(f.utilizacion - s.rho) * 100:+.1f} pp vs objetivo", delta_color="inverse")
            k[6].metric("Temperatura", f"{f.temperatura:.1f} °C")
            k[7].metric("Iteraciones", int(f.iteraciones),
                        delta=f"{int(f.iteraciones - f.iter_sin_warm)} por warm start" if cfg.warm_start else None,
                        delta_color="inverse")
            if f.saturado:
                st.error("🔴 SATURADO: el tráfico supera la capacidad máxima del clúster. Añadir réplicas "
                         "ya no ayuda (escalado retrógrado) → hay que escalar verticalmente o limitar tráfico.")
            elif f.violacion_sla:
                st.warning("🟠 Utilización por encima del SLA: las réplicas nuevas todavía están arrancando.")
            else:
                st.success(f"🟢 Estable · utilización cerca del {s.rho:.0%} objetivo · |g′(N*)| = {f.dg:.3f} < 1")
        for zona, fn in ((zona_traf, gr.trafico), (zona_rep, gr.replicas)):
            fig = fn(df, hasta=t); zona.pyplot(fig); gr.plt.close(fig)
        fig = gr.utilizacion_temperatura(df, s, hasta=t); zona_ut.pyplot(fig); gr.plt.close(fig)
        with zona_log.container(height=330):
            st.markdown("**Registro de eventos**")
            for linea in eventos(df[df.minuto <= t])[:60]:
                st.markdown(linea)

    if reproducir:
        for t in range(0, cfg.minutos, int(paso)):
            pintar(t); time.sleep(0.02)
        pintar(cfg.minutos - 1)
    else:
        pintar(minuto)

    with st.expander("Resumen de la simulación y datos"):
        st.dataframe(pd.Series(sm.resumen(df), name="valor").to_frame().style.format("{:,.2f}"))
        st.download_button("⬇️ Descargar simulación (CSV)", df.to_csv(index=False).encode(),
                           "simulacion.csv", "text/csv")


# ============================================================================
# 2. Métodos numéricos
# ============================================================================
with tabs[1]:
    st.markdown("Resuelve la ecuación de balance para un tráfico dado con **cinco métodos** "
                "y compara iteraciones, evaluaciones de función y orden de convergencia.")
    c1, c2, c3 = st.columns(3)
    lam_m = c1.number_input("λ (req/s)", 1.0, 100000.0, float(round(df.iloc[minuto]["lambda"], 1)), 10.0)
    tol_m = 10.0 ** c2.slider("Tolerancia 10^x ", -14, -3, -8)
    x0_m = c3.number_input("Semilla N₀ (0 = automática λ/(ρX₁))", 0.0, 1000.0, 0.0)
    x0_m = None if x0_m == 0 else x0_m

    if lam_m > lim.lambda_max:
        st.error(f"λ = {lam_m:,.0f} supera λ_máx = {lim.lambda_max:,.0f}: la ecuación no tiene solución "
                 "en la rama estable. Observa cómo diverge Punto Fijo y falla la bisección.")

    comp = bl.comparar(lam_m, s, tol=tol_m, x0=x0_m)
    tabla = pd.DataFrame([{
        "Método": r.metodo, "N*": r.raiz, "Convergió": "✅" if r.convergio else f"❌ {r.motivo}",
        "Iteraciones": r.n_iter, "Evaluaciones f/g": r.evaluaciones,
        "Error relativo final": r.error_final, "Orden estimado p": p,
        "Orden teórico": bl.ORDEN_TEORICO[r.metodo], "Tiempo (ms)": r.tiempo_ms,
    } for r, p in comp])
    st.dataframe(tabla.style.format({"N*": "{:.10f}", "Error relativo final": "{:.2e}",
                                     "Orden estimado p": "{:.3f}", "Tiempo (ms)": "{:.4f}"}, na_rep="—"),
                 use_container_width=True, hide_index=True)

    a, b = st.columns(2)
    fig = gr.errores([r for r, _ in comp], tol=tol_m); a.pyplot(fig); gr.plt.close(fig)
    rpf = comp[0][0]
    fig = gr.telarana(lam_m, s, rpf, x0=x0_m); b.pyplot(fig); gr.plt.close(fig)

    met = st.selectbox("Ver tabla de iteraciones de:", bl.METODOS)
    r_sel = next(r for r, _ in comp if r.metodo == met)
    st.dataframe(pd.DataFrame([{"k": it.k, "N_k": it.x, "|N_k − N_k−1|": it.error_abs,
                                "Error relativo": it.error_rel, **it.extra} for it in r_sel.iteraciones])
                 .style.format(precision=10), use_container_width=True, hide_index=True, height=300)
    if rpf.convergio:
        st.info(f"Punto fijo: g′(N*) = {float(md.dg(rpf.raiz, lam_m, s)):.4f}. El error se multiplica por "
                "ese factor en cada iteración (convergencia lineal). Steffensen aplica la aceleración Δ² "
                "de Aitken a la MISMA g(N) y obtiene convergencia cuadrática.")


# ============================================================================
# 3. Reactivo vs predictivo
# ============================================================================
with tabs[2]:
    st.markdown("Un contenedor nuevo tarda en arrancar. La estrategia **reactiva** escala con el tráfico "
                "actual; la **predictiva** ajusta por **mínimos cuadrados** (lineal, exponencial o "
                "logarítmico) la ventana reciente y escala para el tráfico que habrá cuando la réplica esté lista.")
    _, df_r = correr(pt, s, replace(cfg, estrategia="reactiva"))
    _, df_p = correr(pt, s, replace(cfg, estrategia="predictiva"))
    R, P = sm.resumen(df_r), sm.resumen(df_p)
    k = st.columns(4)
    k[0].metric("Peticiones perdidas (predictiva)", f"{P['Peticiones perdidas']:,.0f}",
                delta=f"{P['Peticiones perdidas'] - R['Peticiones perdidas']:,.0f} vs reactiva", delta_color="inverse")
    k[1].metric("Costo (predictiva)", f"US$ {P['Costo total (USD)']:.2f}",
                delta=f"{P['Costo total (USD)'] - R['Costo total (USD)']:+.2f} vs reactiva", delta_color="inverse")
    k[2].metric("Minutos con SLA violado", P["Minutos con violación SLA"],
                delta=int(P["Minutos con violación SLA"] - R["Minutos con violación SLA"]), delta_color="inverse")
    k[3].metric("Utilización promedio", f"{P['Utilización promedio (%)']:.1f} %",
                delta=f"{P['Utilización promedio (%)'] - R['Utilización promedio (%)']:+.1f} pp")
    fig = gr.comparar_estrategias(df_r, df_p); st.pyplot(fig); gr.plt.close(fig)
    st.dataframe(pd.DataFrame({"Reactiva": R, "Predictiva": P}).style.format("{:,.2f}"), use_container_width=True)
    st.caption("Compromiso: la predictiva paga un poco más de infraestructura a cambio de perder menos peticiones.")


# ============================================================================
# 4. Análisis de convergencia
# ============================================================================
with tabs[3]:
    a, b = st.columns(2)
    with a:
        st.markdown("**Curva de capacidad del clúster.** El pico se encuentra con **sección dorada**. "
                    "Más allá del pico, cada réplica extra *reduce* la capacidad.")
        fig = gr.curva_capacidad(s, float(df.iloc[minuto]["lambda"])); st.pyplot(fig); gr.plt.close(fig)
    with b:
        st.markdown("**Región de convergencia** de Punto Fijo en el plano (λ, κ). "
                    "La frontera coincide con λ_máx: matemáticas y física dicen lo mismo.")
        st.pyplot(fig_mapa(s))
    st.markdown("**g′(N\\*) e iteraciones al acercarse al límite.** Cuando g′ → 1 el método se vuelve lento: "
                "el número de iteraciones funciona como **alarma temprana** de saturación.")
    st.pyplot(fig_conv(s, cfg.tol))
    fig = gr.iteraciones_tiempo(df)
    st.markdown("**Warm start:** usar el N\\* del minuto anterior como semilla reduce iteraciones.")
    st.pyplot(fig); gr.plt.close(fig)


# ============================================================================
# 5. Teoría
# ============================================================================
with tabs[4]:
    st.markdown("### 1. Capacidad real: Ley de Escalabilidad Universal")
    st.latex(r"X(N)=\frac{N\,X_1}{1+\sigma(N-1)+\kappa N(N-1)}")
    st.markdown("σ = contención (colas, bloqueos); κ = coherencia (sincronización entre réplicas). "
                "Con el modelo térmico se multiplica por la eficiencia η(N):")
    st.latex(r"T(N)=T_{amb}+\Delta T\,\rho+h\,N,\qquad "
             r"\eta(N)=1-\beta s\,\ln\!\left(1+e^{(T(N)-T_{thr})/s}\right)")
    st.markdown("### 2. Ecuación de balance y forma de punto fijo")
    st.latex(r"\rho\,X_{eff}(N)=\lambda(t)\;\Longrightarrow\;"
             r"N=g(N)=\frac{\lambda\,[1+\sigma(N-1)+\kappa N(N-1)]}{\rho\,X_1\,\eta(N)}")
    st.markdown("### 3. Criterio de convergencia")
    st.latex(r"|g'(N^*)|<1,\qquad g'(N)=\frac{\lambda}{\rho X_1}\cdot\frac{D'(N)\eta(N)-D(N)\eta'(N)}{\eta(N)^2}")
    st.markdown("En el punto fijo se cumple que **g′(N\\*) < 1 ⇔ dX_eff/dN > 0**, es decir, el sistema está "
                "en la rama donde añadir réplicas sí aumenta la capacidad. Si λ > λ_máx no hay punto fijo "
                "estable y el método diverge: la divergencia numérica *es* la saturación física.")
    st.markdown("### 4. Métodos comparados")
    st.markdown("""
| Método | Iteración | Orden |
|---|---|---|
| Punto fijo | N₍ₖ₊₁₎ = g(Nₖ) | 1 |
| Steffensen | Nₖ − (g(Nₖ)−Nₖ)² / (g(g(Nₖ)) − 2g(Nₖ) + Nₖ) | 2 |
| Newton-Raphson | Nₖ − F(Nₖ)/F′(Nₖ) | 2 |
| Secante | Nₖ − F(Nₖ)(Nₖ−Nₖ₋₁)/(F(Nₖ)−F(Nₖ₋₁)) | 1.618 |
| Bisección | punto medio de [a, b] con cambio de signo | 1 |
| Sección dorada | (optimización) pico de X_eff(N) | lineal, razón 0.618 |
| Mínimos cuadrados + Gauss | pronóstico de λ(t) | — |
""")
    st.markdown("### 5. Recursos derivados")
    st.latex(r"\text{réplicas}=\lceil N^*\rceil,\quad L=\lambda W,\quad W=\frac{1}{X_1(1-U)},"
             r"\quad \text{RAM}=N\,M_{base}+L\,m_{conn}")
