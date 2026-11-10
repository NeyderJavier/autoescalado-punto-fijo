"""
Integración Numérica: Trapecio, Simpson 1/3 y Simpson 3/8.

    pip install -r requirements.txt
    streamlit run app.py

El menú de la izquierda elige qué módulo mostrar. Cada módulo es un archivo
de la carpeta paginas/. (Se usa un menú propio en vez de las páginas de
Streamlit para que la dirección web no cambie y funcione en GitHub Pages.)
"""
import runpy
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Integración Numérica", page_icon="∫", layout="wide")

# Oculta el menú ⋮ de Streamlit (viene en inglés y no hace falta para la clase)
st.markdown("""<style>
#MainMenu, [data-testid="stMainMenu"], [data-testid="stStatusWidget"], footer {display: none !important;}
</style>""", unsafe_allow_html=True)

CARPETA = Path(__file__).parent / "paginas"
MODULOS = {
    "🏠 Inicio": "inicio.py",
    "📐 1 · Trapecio": "modulo_trapecio.py",
    "🌿 2 · Simpson 1/3": "modulo_simpson13.py",
    "☀️ 3 · Simpson 3/8": "modulo_simpson38.py",
}

st.sidebar.title("∫ Integración Numérica")
eleccion = st.sidebar.radio("Elige un módulo", list(MODULOS), key="modulo")
st.sidebar.caption("Trapecio · Simpson 1/3 · Simpson 3/8")

runpy.run_path(str(CARPETA / MODULOS[eleccion]), run_name="__main__")
