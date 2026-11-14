import streamlit as st

import componentes as ui
from metodos import simpson_38
from problemas import PANEL

st.title("☀️ Módulo 3 · Regla de Simpson 3/8")
st.markdown("##### Toma los puntos **de a cuatro** y pasa una **cúbica** (polinomio de grado 3) por ellos.")

# 1. La idea ---------------------------------------------------------------
st.header("1 · La idea")
st.markdown("Por **4 puntos** siempre pasa una **cúbica**. Simpson 3/8 reemplaza la curva por una cúbica (versión corta) o por varias cúbicas, una cada tres franjas (versión extendida).")
st.info("**Pesos de cada punto:** 1, 3, 3, 2, 3, 3, 2, …, 3, 3, 1  ·  **n:** debe ser **múltiplo de 3**  ·  **Es exacto para:** polinomios hasta de grado 3")

# 2. El problema -----------------------------------------------------------
st.header("2 · El problema")
p = ui.elegir_problema(PANEL, "s38")

# 3. Versión corta (regla simple) -----------------------------------------
st.header("3 · Versión corta (regla simple)")
st.markdown("Se usa **una sola cúbica** sobre todo el intervalo: se necesitan 4 puntos igualmente espaciados (n = 3, h = (b − a)/3).")
st.latex(r"I \approx \frac{3h}{8}\Big[f(x_0) + 3f(x_1) + 3f(x_2) + f(x_3)\Big]")
ui.grafica(p, simpson_38, 3)
with st.container(border=True):
    st.markdown("#### ✍️ Solución paso a paso · versión corta")
    corta = ui.resolver(p, simpson_38, 3)

# 4. Versión extendida (regla compuesta) ----------------------------------
st.header("4 · Versión extendida (regla compuesta)")
st.markdown("Se divide el intervalo en **n franjas (múltiplo de 3)** y se usa una cúbica cada tres franjas. Las uniones entre cúbicas (i = 3, 6, 9, …) pesan **2** y los demás puntos de adentro pesan **3**.")
st.latex(r"I \approx \frac{3h}{8}\Big[f(x_0) + 3f(x_1) + 3f(x_2) + 2f(x_3) + \cdots + 3f(x_{n-1}) + f(x_n)\Big]")
n = ui.elegir_n(simpson_38, p, minimo=3, paso=3, maximo=30, clave="s38")
ui.grafica(p, simpson_38, n)
with st.container(border=True):
    st.markdown(f"#### ✍️ Solución paso a paso · versión extendida con n = {n}")
    larga = ui.resolver(p, simpson_38, n)

# 5. Figura por figura -----------------------------------------------------
st.header("5 · Figura por figura")
st.markdown("Presiona **Siguiente ▶** para agregar una cúbica a la vez. Cada una cubre **tres franjas**.")
ui.animacion(p, simpson_38, n, "s38")

# 6. Corta vs extendida ----------------------------------------------------
st.header("6 · Versión corta vs versión extendida")
ui.comparar_versiones(p, simpson_38, 3, corta, n, larga)
ui.resultado(p, larga)

st.header("🧠 Para recordar")
st.markdown("""
- **Versión corta:** una cúbica, **3h/8 · [f(x₀) + 3f(x₁) + 3f(x₂) + f(x₃)]** con h = (b − a)/3.
- **Versión extendida:** **3h/8 · [primero + 3·(los de adentro) + 2·(las uniones) + último]**, con **n múltiplo de 3**.
- Si **duplicas n**, el error baja **unas 16 veces**.
""")
