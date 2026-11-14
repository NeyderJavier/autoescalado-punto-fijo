import streamlit as st

import componentes as ui
from metodos import trapecio
from problemas import CARRO

st.title("📐 Módulo 1 · Regla del Trapecio")
st.markdown("##### Une los puntos con **líneas rectas** y suma el área de los trapecios que se forman.")

# 1. La idea ---------------------------------------------------------------
st.header("1 · La idea")
st.markdown("Un **trapecio** tiene dos lados paralelos. Su área es *el promedio de las dos alturas por la base*. La regla del trapecio reemplaza la curva por una recta (versión corta) o por muchas rectas pequeñas (versión extendida).")
st.info("**Pesos de cada punto:** 1, 2, 2, …, 2, 1  ·  **n:** cualquier entero ≥ 1  ·  **Es exacto para:** rectas")

# 2. El problema -----------------------------------------------------------
st.header("2 · El problema")
p = ui.elegir_problema(CARRO, "trap")

# 3. Versión corta (regla simple) -----------------------------------------
st.header("3 · Versión corta (regla simple)")
st.markdown("Se usa **un solo trapecio** sobre todo el intervalo: solo se necesitan los dos extremos, **a** y **b** (n = 1, h = b − a).")
st.latex(r"I \approx \frac{h}{2}\Big[f(x_0) + f(x_1)\Big] = \frac{b-a}{2}\Big[f(a) + f(b)\Big]")
ui.grafica(p, trapecio, 1)
with st.container(border=True):
    st.markdown("#### ✍️ Solución paso a paso · versión corta")
    corta = ui.resolver(p, trapecio, 1)

# 4. Versión extendida (regla compuesta) ----------------------------------
st.header("4 · Versión extendida (regla compuesta)")
st.markdown("Se divide el intervalo en **n franjas** y se usa un trapecio en cada una. Los puntos de adentro se cuentan **dos veces** porque pertenecen a dos trapecios.")
st.latex(r"I \approx \frac{h}{2}\Big[f(x_0) + 2f(x_1) + 2f(x_2) + \cdots + 2f(x_{n-1}) + f(x_n)\Big]")
n = ui.elegir_n(trapecio, p, minimo=1, paso=1, maximo=30, clave="trap")
ui.grafica(p, trapecio, n)
with st.container(border=True):
    st.markdown(f"#### ✍️ Solución paso a paso · versión extendida con n = {n}")
    larga = ui.resolver(p, trapecio, n)

# 5. Figura por figura -----------------------------------------------------
st.header("5 · Figura por figura")
st.markdown("Presiona **Siguiente ▶** para agregar un trapecio a la vez y ver cómo se acumula el área.")
ui.animacion(p, trapecio, n, "trap")

# 6. Corta vs extendida ----------------------------------------------------
st.header("6 · Versión corta vs versión extendida")
ui.comparar_versiones(p, trapecio, 1, corta, n, larga)
ui.resultado(p, larga)

st.header("🧠 Para recordar")
st.markdown("""
- **Versión corta:** un trapecio, **(b − a)/2 · [f(a) + f(b)]**.
- **Versión extendida:** **h/2 · [primero + 2·(los de adentro) + último]**, con cualquier n.
- Si **duplicas n**, el error baja **unas 4 veces**.
""")
