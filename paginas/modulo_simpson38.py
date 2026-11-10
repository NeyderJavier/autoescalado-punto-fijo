import streamlit as st

import componentes as ui
from metodos import simpson_38
from problemas import PANEL

st.title("☀️ Módulo 3 · Regla de Simpson 3/8")
st.markdown("##### Toma los puntos **de a cuatro** y pasa una **cúbica** (polinomio de grado 3) por ellos.")

# 1. La idea ---------------------------------------------------------------
st.header("1 · La idea")
c1, c2 = st.columns(2)
with c1:
    st.markdown("Por **4 puntos** siempre pasa una cúbica. Al calcular el área bajo esa cúbica en **tres franjas** se obtiene:")
    st.latex(r"\text{Área} = \frac{3h}{8}\Big[f(x_0) + 3f(x_1) + 3f(x_2) + f(x_3)\Big]")
with c2:
    st.markdown("Repitiendo con cada grupo de tres franjas, los puntos de **adentro** pesan 3 y los de **unión** pesan 2:")
    st.latex(r"\int_a^b f(x)\,dx \approx \frac{3h}{8}\Big[f(x_0) + 3f(x_1) + 3f(x_2) + 2f(x_3) + \cdots + 3f(x_{n-1}) + f(x_n)\Big]")
st.info("**Pesos de cada punto:** 1, 3, 3, 2, 3, 3, 2, …, 3, 3, 1  ·  **n:** debe ser **múltiplo de 3**, porque cada cúbica usa 3 franjas  ·  **Es exacto para:** polinomios hasta de grado 3")

# 2. El problema -----------------------------------------------------------
st.header("2 · El problema")
p = ui.elegir_problema(PANEL, "s38")

# 3. Divide y dibuja --------------------------------------------------------
st.header("3 · Divide y dibuja")
n = ui.elegir_n(simpson_38, p, minimo=3, paso=3, maximo=30, clave="s38")
ui.grafica(p, simpson_38, n)
st.caption("Cada zona morada es una cúbica que cubre tres franjas.")

# 4. Animación ---------------------------------------------------------------
st.header("4 · Figura por figura")
st.markdown("Presiona **Siguiente ▶** para agregar una cúbica a la vez. Cada una cubre **tres franjas** (4 puntos).")
ui.animacion(p, simpson_38, n, "s38")

# 5. Paso a paso -----------------------------------------------------------
st.header("5 · El cálculo paso a paso")
st.markdown("Los puntos de **unión** entre cúbicas (i = 3, 6, 9, …) pesan **2**; los demás puntos de adentro pesan **3**.")
aprox = ui.paso_a_paso(p, simpson_38, n)

# 6. Resultado -------------------------------------------------------------
st.header("6 · Resultado")
ui.resultado(p, aprox)

st.header("🧠 Para recordar")
st.markdown("""
- Simpson 3/8 aproxima la curva con **cúbicas** (4 puntos cada una).
- Fórmula: **3h/8 · [primero + 3·(los de adentro) + 2·(las uniones) + último]**.
- **n debe ser múltiplo de 3**.
- Es útil cuando el número de franjas es **impar**, como 3 o 9, donde Simpson 1/3 no se puede usar.
""")
