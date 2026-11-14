import streamlit as st

import componentes as ui
from metodos import simpson_13
from problemas import RIO

st.title("🌿 Módulo 2 · Regla de Simpson 1/3")
st.markdown("##### Toma los puntos **de a tres** y pasa una **parábola** por ellos. La parábola sigue mejor las curvas.")

# 1. La idea ---------------------------------------------------------------
st.header("1 · La idea")
st.markdown("Por **3 puntos** siempre pasa una **parábola**. Simpson 1/3 reemplaza la curva por una parábola (versión corta) o por varias parábolas, una cada dos franjas (versión extendida).")
st.info("**Pesos de cada punto:** 1, 4, 2, 4, …, 4, 1  ·  **n:** debe ser **par**  ·  **Es exacto para:** polinomios hasta de grado 3")

# 2. El problema -----------------------------------------------------------
st.header("2 · El problema")
p = ui.elegir_problema(RIO, "s13")

# 3. Versión corta (regla simple) -----------------------------------------
st.header("3 · Versión corta (regla simple)")
st.markdown("Se usa **una sola parábola** sobre todo el intervalo: se necesitan 3 puntos, los extremos y el **punto medio** (n = 2, h = (b − a)/2).")
st.latex(r"I \approx \frac{h}{3}\Big[f(x_0) + 4f(x_1) + f(x_2)\Big]")
ui.grafica(p, simpson_13, 2)
with st.container(border=True):
    st.markdown("#### ✍️ Solución paso a paso · versión corta")
    corta = ui.resolver(p, simpson_13, 2)

# 4. Versión extendida (regla compuesta) ----------------------------------
st.header("4 · Versión extendida (regla compuesta)")
st.markdown("Se divide el intervalo en **n franjas (n par)** y se usa una parábola cada dos franjas. Los centros de cada parábola (i impar) pesan **4** y las uniones (i par) pesan **2**.")
st.latex(r"I \approx \frac{h}{3}\Big[f(x_0) + 4f(x_1) + 2f(x_2) + 4f(x_3) + \cdots + 4f(x_{n-1}) + f(x_n)\Big]")
n = ui.elegir_n(simpson_13, p, minimo=2, paso=2, maximo=30, clave="s13")
ui.grafica(p, simpson_13, n)
with st.container(border=True):
    st.markdown(f"#### ✍️ Solución paso a paso · versión extendida con n = {n}")
    larga = ui.resolver(p, simpson_13, n)

# 5. Figura por figura -----------------------------------------------------
st.header("5 · Figura por figura")
st.markdown("Presiona **Siguiente ▶** para agregar una parábola a la vez. Cada una cubre **dos franjas**.")
ui.animacion(p, simpson_13, n, "s13")

# 6. Corta vs extendida ----------------------------------------------------
st.header("6 · Versión corta vs versión extendida")
ui.comparar_versiones(p, simpson_13, 2, corta, n, larga)
ui.resultado(p, larga)

st.header("🧠 Para recordar")
st.markdown("""
- **Versión corta:** una parábola, **h/3 · [f(x₀) + 4f(x₁) + f(x₂)]** con h = (b − a)/2.
- **Versión extendida:** **h/3 · [primero + 4·(impares) + 2·(pares) + último]**, con **n par**.
- Si **duplicas n**, el error baja **unas 16 veces**.
""")
