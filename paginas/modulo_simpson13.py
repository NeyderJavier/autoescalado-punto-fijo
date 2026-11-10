import streamlit as st

import componentes as ui
from metodos import simpson_13
from problemas import RIO

st.title("🌿 Módulo 2 · Regla de Simpson 1/3")
st.markdown("##### Toma los puntos **de a tres** y pasa una **parábola** por ellos. La parábola sigue mejor las curvas.")

# 1. La idea ---------------------------------------------------------------
st.header("1 · La idea")
c1, c2 = st.columns(2)
with c1:
    st.markdown("Por **3 puntos** siempre pasa una parábola. Al calcular el área bajo esa parábola en **dos franjas** se obtiene:")
    st.latex(r"\text{Área} = \frac{h}{3}\Big[f(x_0) + 4f(x_1) + f(x_2)\Big]")
with c2:
    st.markdown("Repitiendo con cada par de franjas, el punto del **centro** de cada parábola pesa 4 y los puntos de **unión** pesan 2:")
    st.latex(r"\int_a^b f(x)\,dx \approx \frac{h}{3}\Big[f(x_0) + 4f(x_1) + 2f(x_2) + \cdots + 4f(x_{n-1}) + f(x_n)\Big]")
st.info("**Pesos de cada punto:** 1, 4, 2, 4, …, 4, 1  ·  **n:** debe ser **par**, porque cada parábola usa 2 franjas  ·  **Es exacto para:** polinomios hasta de grado 3")

# 2. El problema -----------------------------------------------------------
st.header("2 · El problema")
p = ui.elegir_problema(RIO, "s13")

# 3. Divide y dibuja --------------------------------------------------------
st.header("3 · Divide y dibuja")
n = ui.elegir_n(simpson_13, p, minimo=2, paso=2, maximo=30, clave="s13")
ui.grafica(p, simpson_13, n)
st.caption("Cada zona verde es una parábola que cubre dos franjas. Casi no se distingue de la curva negra.")

# 4. Animación ---------------------------------------------------------------
st.header("4 · Figura por figura")
st.markdown("Presiona **Siguiente ▶** para agregar una parábola a la vez. Cada una cubre **dos franjas** (3 puntos).")
ui.animacion(p, simpson_13, n, "s13")

# 5. Paso a paso -----------------------------------------------------------
st.header("5 · El cálculo paso a paso")
st.markdown("Los puntos con **i impar** son el centro de una parábola (peso **4**); los de **i par** unen dos parábolas (peso **2**).")
aprox = ui.paso_a_paso(p, simpson_13, n)

# 6. Resultado -------------------------------------------------------------
st.header("6 · Resultado")
ui.resultado(p, aprox)

st.header("🧠 Para recordar")
st.markdown("""
- Simpson 1/3 aproxima la curva con **parábolas** (3 puntos cada una).
- Fórmula: **h/3 · [primero + 4·(impares) + 2·(pares) + último]**.
- **n debe ser par**.
- Si **duplicas n**, el error baja **unas 16 veces**.
""")
