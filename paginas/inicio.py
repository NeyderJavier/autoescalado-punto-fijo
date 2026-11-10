import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from problemas import CARRO

st.title("∫ Integración Numérica")
st.markdown("##### Aprende tres formas de calcular el **área bajo una curva**: Trapecio, Simpson 1/3 y Simpson 3/8.")

# ¿Qué es integrar? -----------------------------------------------------------
st.header("¿Qué es integrar?")
c1, c2 = st.columns([1, 1])
with c1:
    st.markdown(
        "Integrar una función entre **a** y **b** es calcular el **área que queda debajo de su curva**.\n\n"
        "Ese área casi siempre significa algo real:\n"
        "- debajo de la **velocidad** de un carro está la **distancia** recorrida;\n"
        "- debajo de la **profundidad** de un río está el **área de su sección**;\n"
        "- debajo de la **potencia** de un panel solar está la **energía** producida."
    )
    st.latex(r"\int_a^b f(x)\,dx = \text{área bajo la curva}")
with c2:
    fig, ax = plt.subplots(figsize=(6, 3.6), dpi=110)
    x = np.linspace(CARRO.a, CARRO.b, 300)
    ax.fill_between(x, CARRO.f(x), color="#2563eb", alpha=.25)
    ax.plot(x, CARRO.f(x), color="#111827", lw=2)
    ax.text(32, 11, "área = distancia\nrecorrida", ha="center", fontsize=12, color="#1e3a8a")
    ax.set_xlabel(CARRO.eje_x); ax.set_ylabel(CARRO.eje_y)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); st.pyplot(fig); plt.close(fig)

# ¿Por qué numérica? ----------------------------------------------------------
st.header("¿Por qué hacerlo numéricamente?")
c = st.columns(2)
c[0].info("📏 **Solo tenemos mediciones.** Un velocímetro, un sensor o un topógrafo nos dan puntos sueltos, "
          "no una fórmula. No hay nada que integrar \"a mano\".")
c[1].info("🧮 **Algunas funciones no se pueden integrar a mano.** Por ejemplo, e^(−x²) no tiene antiderivada "
          "con funciones conocidas.")
st.markdown("La idea de los tres métodos es la misma: **dividir el intervalo en n franjas iguales**, "
            "reemplazar la curva por figuras sencillas y **sumar sus áreas**.")

# Los tres módulos -----------------------------------------------------------
st.header("Los tres módulos")
st.markdown("""
| Módulo | Reemplaza la curva por… | Puntos por figura | n permitido | Problema | Si duplicas n, el error… |
|---|---|---|---|---|---|
| 📐 **1 · Trapecio** | rectas | 2 | cualquiera | 🚗 distancia de un carro | baja ~4 veces |
| 🌿 **2 · Simpson 1/3** | parábolas | 3 | par | 🌊 sección de un río | baja ~16 veces |
| ☀️ **3 · Simpson 3/8** | cúbicas | 4 | múltiplo de 3 | ☀️ energía de un panel solar | baja ~16 veces |
""")
st.markdown("Los tres usan la misma fórmula general. Solo cambian los **pesos** de cada punto y el factor de adelante:")
st.latex(r"\int_a^b f(x)\,dx \approx \text{factor}\cdot\sum_{i=0}^{n} c_i\, f(x_i), \qquad h = \frac{b-a}{n},\quad x_i = a + i\,h")

# Cómo usar -------------------------------------------------------------------
st.header("Cómo usar esta app")
st.markdown("""
1. Elige un módulo en el **menú de la izquierda**.
2. Lee **la idea** del método y **el problema**.
3. Mueve el control de **n** y mira cómo cambian las figuras.
4. En **Figura por figura**, presiona **Siguiente ▶** para ver cómo se suma el área.
5. Revisa el **paso a paso** y compara el **resultado** con el valor exacto.

En cada módulo también puedes elegir otros problemas, como x³ o sen(x), para practicar.
""")
