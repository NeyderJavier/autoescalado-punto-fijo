"""Piezas de pantalla que usan los tres módulos (para no repetir código)."""
import io

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from graficas import dibujar
from problemas import TODOS


def _fmt(v, unidad=""):
    texto = f"{v:,.6f}".rstrip("0").rstrip(".") if abs(v) < 1000 else f"{v:,.2f}"
    return f"{texto} {unidad}".strip()


def elegir_problema(defecto, clave):
    """Selector de problema; empieza en el problema propio del módulo."""
    titulos = [p.titulo for p in TODOS]
    titulo = st.selectbox("Problema", titulos, index=titulos.index(defecto.titulo), key=f"prob_{clave}")
    p = next(p for p in TODOS if p.titulo == titulo)
    st.markdown(p.historia)
    c1, c2 = st.columns([3, 2])
    c1.latex(p.formula)
    c2.markdown(f"**Intervalo:** desde **{p.a:g}** hasta **{p.b:g}**  \n**Eje x:** {p.eje_x}  \n**Eje y:** {p.eje_y}")
    return p


def elegir_n(metodo, p, minimo, paso, maximo, clave):
    """Slider de n que solo deja valores válidos para el método."""
    defecto = p.n_defecto if (p.n_defecto >= minimo and (p.n_defecto - minimo) % paso == 0) else minimo * 2
    defecto = min(defecto, maximo)
    n = st.slider("n (número de subintervalos)", minimo, maximo, defecto, paso, key=f"n_{clave}_{p.titulo}")
    h = (p.b - p.a) / n
    st.caption(f"Regla: {metodo.REGLA_N}.  Con n = {n}, el ancho de cada franja es "
               f"h = ({p.b:g} − {p.a:g}) / {n} = **{h:g}** y se usan **{n + 1} puntos**.")
    if p.nota and n == p.n_defecto:
        st.caption(p.nota)
    return n


@st.cache_data(max_entries=300, show_spinner=False)
def _imagen(titulo, metodo_nombre, n, hasta=None):
    """Dibuja la gráfica UNA sola vez y la guarda; las siguientes veces se reutiliza."""
    p = next(p for p in TODOS if p.titulo == titulo)
    fig = dibujar(p, metodo_nombre, n, hasta=hasta)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=95)
    plt.close(fig)
    return buf.getvalue()


def imagen(p, metodo, n, hasta=None):
    with st.spinner("Dibujando…"):
        st.image(_imagen(p.titulo, metodo.NOMBRE, n, hasta))


def grafica(p, metodo, n):
    imagen(p, metodo, n)


def paso_a_paso(p, metodo, n):
    filas, h, suma, resultado = metodo.paso_a_paso(p.f, p.a, p.b, n)
    df = pd.DataFrame(filas)
    st.dataframe(df.round(6), hide_index=True, use_container_width=True, height=min(38 * (len(df) + 1) + 4, 420))
    factor = {"h/2": f"{h:g}/2", "h/3": f"{h:g}/3", "3h/8": f"3·{h:g}/8"}[metodo.FACTOR]
    st.markdown(f"**Suma de la última columna:** {suma:,.6f}")
    st.markdown(f"**Resultado:** {metodo.FACTOR} × suma = {factor} × {suma:,.6f} = **{resultado:,.6f}**")
    return resultado


def resultado(p, aprox):
    err = abs(aprox - p.exacta)
    rel = 100 * err / abs(p.exacta)
    c = st.columns(4)
    c[0].metric(f"{p.resultado} (aproximado)", _fmt(aprox, p.unidad))
    c[1].metric("Valor exacto", _fmt(p.exacta, p.unidad))
    c[2].metric("Error absoluto", f"{err:.2e}")
    c[3].metric("Error relativo", f"{rel:.4f} %")
    if p.unidad:
        st.success(f"**{p.resultado} ≈ {_fmt(aprox, p.unidad)}**. El valor exacto es {_fmt(p.exacta, p.unidad)}: "
                   f"el método se equivoca en un {rel:.3f} %.")


# st.fragment hace que los botones de la animación solo recarguen esta sección
_fragmento = getattr(st, "fragment", lambda f: f)


@_fragmento
def animacion(p, metodo, n, clave):
    """Muestra las figuras una por una y cómo se va sumando el área."""
    paso = {"Trapecio": 1, "Simpson 1/3": 2, "Simpson 3/8": 3}[metodo.NOMBRE]
    total = n // paso
    nombre = {"Trapecio": "trapecio", "Simpson 1/3": "parábola", "Simpson 3/8": "cúbica"}[metodo.NOMBRE]
    k_estado = f"anim_{clave}_{p.titulo}_{n}"
    if k_estado not in st.session_state:
        st.session_state[k_estado] = 1

    b = st.columns([1, 1, 1, 1, 3])
    if b[0].button("⏮ Inicio", key=f"{k_estado}_ini", use_container_width=True):
        st.session_state[k_estado] = 1
    if b[1].button("◀ Atrás", key=f"{k_estado}_atr", use_container_width=True):
        st.session_state[k_estado] = max(1, st.session_state[k_estado] - 1)
    if b[2].button("Siguiente ▶", key=f"{k_estado}_sig", use_container_width=True, type="primary"):
        st.session_state[k_estado] = min(total, st.session_state[k_estado] + 1)
    if b[3].button("Todas ⏭", key=f"{k_estado}_fin", use_container_width=True):
        st.session_state[k_estado] = total
    k = st.session_state[k_estado]

    # Área de cada figura: el mismo método aplicado solo a ese pedacito
    h = (p.b - p.a) / n
    filas, acumulada = [], 0.0
    for j in range(k):
        x0, x1 = p.a + j * paso * h, p.a + (j + 1) * paso * h
        area = metodo.integrar(p.f, x0, x1, paso)
        acumulada += area
        filas.append({"figura": j + 1, "desde x": x0, "hasta x": x1, f"área de la {nombre}": area,
                      "área acumulada": acumulada})

    b[4].markdown(f"**{nombre.capitalize()} {k} de {total}** · área acumulada: "
                  f"**{acumulada:,.4f} {p.unidad}**")
    imagen(p, metodo, n, hasta=k)
    st.dataframe(pd.DataFrame(filas).round(4), hide_index=True, use_container_width=True)
    if k == total:
        st.success(f"Sumando las {total} figuras se obtiene **{acumulada:,.6f} {p.unidad}**, "
                   "el mismo resultado de la fórmula completa.")


# ---------------------------------------------------------------------------
# Resolución paso a paso (sirve para la versión corta y la extendida)
# ---------------------------------------------------------------------------
_FACTOR = {  # cómo se escribe el factor en símbolos y con números
    "Trapecio": (r"\frac{h}{2}", lambda h: rf"\frac{{{_g(h)}}}{{2}}", lambda h: h / 2),
    "Simpson 1/3": (r"\frac{h}{3}", lambda h: rf"\frac{{{_g(h)}}}{{3}}", lambda h: h / 3),
    "Simpson 3/8": (r"\frac{3h}{8}", lambda h: rf"\frac{{3({_g(h)})}}{{8}}", lambda h: 3 * h / 8),
}


def _g(v):
    """Número corto: 10 en vez de 10.0, 6.6667 en vez de 6.666666666."""
    return f"{v:.4f}".rstrip("0").rstrip(".") if v != int(v) else str(int(v))


def _grupo(indices, valores, simbolico):
    """Escribe f(x1)+f(x3)+... (o sus valores), abreviando si son muchos."""
    if simbolico:
        items = [f"f(x_{{{i}}})" for i in indices]
    else:
        items = [f"{valores[i]:.4f}" for i in indices]
    if len(items) > 5:
        items = items[:2] + [r"\cdots"] + items[-1:]
    return " + ".join(items)


def _expresion(cs, ys, simbolico):
    """Arma f(x0) + 4[...] + 2[...] + f(xn) agrupando los puntos por su peso."""
    n = len(cs) - 1
    primero = "f(x_{0})" if simbolico else f"{ys[0]:.4f}"
    ultimo = f"f(x_{{{n}}})" if simbolico else f"{ys[n]:.4f}"
    partes = [primero]
    for peso in sorted({c for c in cs[1:-1]}, reverse=True):
        idx = [i for i in range(1, n) if cs[i] == peso]
        dentro = _grupo(idx, ys, simbolico)
        if len(idx) == 1:
            partes.append(f"{peso}{dentro}" if simbolico else f"{peso}({dentro})")
        else:
            partes.append(f"{peso}\\left[{dentro}\\right]")
    partes.append(ultimo)
    return " + ".join(partes)


def resolver(p, metodo, n):
    """Muestra los 6 pasos de la solución, con los números reemplazados."""
    h = (p.b - p.a) / n
    xs = [p.a + i * h for i in range(n + 1)]
    ys = [float(p.f(x)) for x in xs]
    cs = metodo.coeficientes(n)
    f_sim, f_num, f_val = _FACTOR[metodo.NOMBRE]
    suma = sum(c * y for c, y in zip(cs, ys))
    aprox = f_val(h) * suma
    if not p.unidad:
        u = ""
    elif p.unidad.endswith("²"):
        u = rf"\ \text{{{p.unidad[:-1]}}}^2"
    else:
        u = rf"\ \text{{{p.unidad}}}"

    st.markdown("**Paso 1 · Calcular el ancho de cada franja**")
    st.latex(rf"h = \frac{{b - a}}{{n}} = \frac{{{_g(p.b)} - {_g(p.a)}}}{{{n}}} = {_g(h)}")

    st.markdown("**Paso 2 · Ubicar los puntos** con x<sub>i</sub> = a + i·h", unsafe_allow_html=True)
    puntos = [rf"x_{{{i}}} = {_g(x)}" for i, x in enumerate(xs)]
    if len(puntos) > 10:
        puntos = puntos[:3] + [r"\ldots"] + puntos[-2:]
    st.latex(r",\quad ".join(puntos))

    st.markdown("**Paso 3 · Evaluar la función en cada punto** (y anotar el peso de cada uno)")
    st.dataframe(pd.DataFrame({"i": range(n + 1), "x_i": [round(x, 4) for x in xs],
                               "f(x_i)": [round(y, 4) for y in ys], "peso": cs}),
                 hide_index=True, use_container_width=True, height=min(36 * (n + 2) + 4, 360))

    st.markdown("**Paso 4 · Reemplazar en la fórmula**")
    st.latex(rf"I \approx {f_sim}\left[{_expresion(cs, ys, True)}\right]")
    st.latex(rf"I \approx {f_num(h)}\left[{_expresion(cs, ys, False)}\right]")

    st.markdown("**Paso 5 · Operar** (primero se suma cada grupo, luego se multiplica)")
    grupos = [f"{ys[0]:.4f}"]
    for peso in sorted({c for c in cs[1:-1]}, reverse=True):
        sub = sum(y for c, y in zip(cs[1:-1], ys[1:-1]) if c == peso)
        grupos.append(f"{peso}({sub:.4f})")
    grupos.append(f"{ys[-1]:.4f}")
    hay_grupos = any(cs[1:-1].count(c) > 1 for c in set(cs[1:-1]))
    if hay_grupos:
        st.latex(rf"I \approx {f_num(h)}\left[{' + '.join(grupos)}\right]")
    st.latex(rf"I \approx {f_num(h)}\,({suma:.4f}) = \mathbf{{{aprox:.4f}}}{u}")

    st.markdown("**Paso 6 · Calcular el error** (comparando con el valor exacto)")
    err = abs(p.exacta - aprox)
    rel = 100 * err / abs(p.exacta)
    st.latex(rf"E = \left|{p.exacta:.4f} - {aprox:.4f}\right| = {err:.4f}{u}"
             rf"\qquad E_{{\%}} = \frac{{{err:.4f}}}{{{p.exacta:.4f}}}\times 100 = {rel:.3f}\,\%")
    return aprox


def comparar_versiones(p, metodo, n_corta, corta, n_larga, larga):
    """Tabla final: versión corta vs versión extendida."""
    e1, e2 = abs(corta - p.exacta), abs(larga - p.exacta)
    c = st.columns(3)
    c[0].metric(f"Versión corta (n = {n_corta})", _fmt(corta, p.unidad),
                f"error {100 * e1 / abs(p.exacta):.3f} %", delta_color="off")
    c[1].metric(f"Versión extendida (n = {n_larga})", _fmt(larga, p.unidad),
                f"error {100 * e2 / abs(p.exacta):.3f} %", delta_color="off")
    c[2].metric("Valor exacto", _fmt(p.exacta, p.unidad))
    if e2 > 0 and e1 > e2:
        st.success(f"Con la versión extendida el error es **{e1 / e2:,.0f} veces más pequeño** que con la corta. "
                   "Más franjas = figuras más pequeñas = mejor ajuste a la curva.")
    elif e1 == 0 or e2 == 0:
        st.success("El resultado es exacto: esta función es un polinomio que el método integra sin error.")
