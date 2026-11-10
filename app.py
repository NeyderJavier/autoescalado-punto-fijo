"""
Integración Numérica: Trapecio, Simpson 1/3 y Simpson 3/8.

    pip install -r requirements.txt
    streamlit run app.py
"""
import streamlit as st

st.set_page_config(page_title="Integración Numérica", page_icon="∫", layout="wide")

paginas = st.navigation([
    st.Page("paginas/inicio.py", title="Inicio", icon="🏠", default=True),
    st.Page("paginas/modulo_trapecio.py", title="1 · Trapecio", icon="📐"),
    st.Page("paginas/modulo_simpson13.py", title="2 · Simpson 1/3", icon="🌿"),
    st.Page("paginas/modulo_simpson38.py", title="3 · Simpson 3/8", icon="☀️"),
])
paginas.run()
