"""Piezas de pantalla que usan los tres módulos (para no repetir código)."""
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


def grafica(p, metodo, n):
    fig = dibujar(p, metodo.NOMBRE, n)
    st.pyplot(fig)
    plt.close(fig)


def paso_a_paso(p, metodo, n):
    filas, h, suma, resultado = metodo.paso_a_paso(p.f, p.a, p.b, n)
    df = pd.DataFrame(filas)
    st.dataframe(df.style.format({"x_i": "{:g}", "f(x_i)": "{:.6f}", "c · f(x_i)": "{:.6f}"}),
                 hide_index=True, use_container_width=True, height=min(38 * (len(df) + 1) + 4, 420))
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
    fig = dibujar(p, metodo.NOMBRE, n, hasta=k)
    st.pyplot(fig)
    plt.close(fig)
    st.dataframe(pd.DataFrame(filas).style.format({"desde x": "{:g}", "hasta x": "{:g}",
                                                   f"área de la {nombre}": "{:,.4f}", "área acumulada": "{:,.4f}"}),
                 hide_index=True, use_container_width=True)
    if k == total:
        st.success(f"Sumando las {total} figuras se obtiene **{acumulada:,.6f} {p.unidad}**, "
                   "el mismo resultado de la fórmula completa.")
