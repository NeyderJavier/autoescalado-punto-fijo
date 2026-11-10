import streamlit as st

import componentes as ui
from metodos import trapecio
from problemas import CARRO

st.title("📐 Módulo 1 · Regla del Trapecio")
st.markdown("##### Une los puntos con **líneas rectas** y suma el área de los trapecios que se forman.")

# 1. La idea ---------------------------------------------------------------
st.header("1 · La idea")
c1, c2 = st.columns(2)
with c1:
    st.markdown("Un **trapecio** tiene dos lados paralelos. Su área es *el promedio de las dos alturas por la base*:")
    st.latex(r"\text{Área} = \frac{f(x_0) + f(x_1)}{2}\cdot h")
with c2:
    st.markdown("Si dividimos el intervalo en **n franjas** de ancho **h** y sumamos todos los trapecios, los puntos de adentro se cuentan **dos veces**:")
    st.latex(r"\int_a^b f(x)\,dx \approx \frac{h}{2}\Big[f(x_0) + 2f(x_1) + \cdots + 2f(x_{n-1}) + f(x_n)\Big]")
st.info("**Pesos de cada punto:** 1, 2, 2, …, 2, 1  ·  **n:** cualquier entero ≥ 1  ·  **Es exacto para:** rectas")

# 2. El problema -----------------------------------------------------------
st.header("2 · El problema")
p = ui.elegir_problema(CARRO, "trap")

# 3. Divide y dibuja --------------------------------------------------------
st.header("3 · Divide y dibuja")
n = ui.elegir_n(trapecio, p, minimo=1, paso=1, maximo=30, clave="trap")
ui.grafica(p, trapecio, n)
st.caption("El espacio entre la curva negra y las rectas azules es el error del método. Sube n y mira cómo se reduce.")

# 4. Animación ---------------------------------------------------------------
st.header("4 · Figura por figura")
st.markdown("Presiona **Siguiente ▶** para agregar un trapecio a la vez. La tabla muestra el área de cada uno y cómo se va acumulando.")
ui.animacion(p, trapecio, n, "trap")

# 5. Paso a paso -----------------------------------------------------------
st.header("5 · El cálculo paso a paso")
st.markdown("Así se hace en el cuaderno: evaluar la función en cada punto, multiplicar por su peso y sumar.")
aprox = ui.paso_a_paso(p, trapecio, n)

# 6. Resultado -------------------------------------------------------------
st.header("6 · Resultado")
ui.resultado(p, aprox)

st.header("🧠 Para recordar")
st.markdown("""
- El trapecio aproxima la curva con **rectas**.
- Fórmula: **h/2 · [primero + 2·(los de adentro) + último]**.
- Funciona con **cualquier n**.
- Si **duplicas n**, el error baja **unas 4 veces**.
""")
