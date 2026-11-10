"""
Problemas de ejemplo. Cada uno tiene una función con integral exacta conocida,
para poder medir el error de cada método.
"""
import math
from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass
class Problema:
    titulo: str
    historia: str            # el problema contado en palabras
    f: Callable              # la función que se integra
    formula: str             # la función escrita en LaTeX
    a: float
    b: float
    exacta: float            # valor exacto de la integral
    eje_x: str
    eje_y: str
    resultado: str           # cómo se llama lo que da la integral
    unidad: str              # unidad del resultado
    n_defecto: int
    nota: str = ""
    invertir_y: bool = False   # True: dibujar hacia abajo (profundidad)


# --------------------------------------------------------------------------
# Problemas con contexto (uno por módulo)
# --------------------------------------------------------------------------
CARRO = Problema(
    titulo="🚗 Distancia recorrida por un carro",
    historia=("Un carro arranca desde cero y acelera durante un minuto. El velocímetro "
              "registra la velocidad cada cierto tiempo. ¿Cuántos metros recorrió? "
              "La distancia es el **área bajo la curva de velocidad**."),
    f=lambda t: 30 * (1 - np.exp(-t / 15)),
    formula=r"v(t) = 30\,(1 - e^{-t/15})",
    a=0, b=60,
    exacta=30 * (45 + 15 * math.exp(-4)),
    eje_x="tiempo t (s)", eje_y="velocidad v (m/s)",
    resultado="Distancia recorrida", unidad="m",
    n_defecto=6,
    nota="Con n = 6 equivale a leer el velocímetro cada 10 segundos.",
)

RIO = Problema(
    titulo="🌊 Sección de un río",
    historia=("Para saber cuánta agua lleva un río, se tiende una cuerda de orilla a orilla (40 m) "
              "y se mide la **profundidad** cada cierta distancia. El área de la sección (el \"corte\" "
              "del río) es el **área bajo la curva de profundidad**. Multiplicada por la velocidad "
              "del agua da el **caudal**."),
    f=lambda x: 3 * np.sin(np.pi * x / 40) * (0.6 + 0.01 * x),
    formula=r"\text{profundidad}(x) = 3\,\mathrm{sen}\!\left(\tfrac{\pi x}{40}\right)\,(0.6 + 0.01x)",
    a=0, b=40,
    exacta=192 / math.pi,
    eje_x="distancia desde la orilla x (m)", eje_y="profundidad (m)",
    resultado="Área de la sección", unidad="m²",
    n_defecto=8,
    nota="Con n = 8 equivale a medir la profundidad cada 5 metros. Si el agua va a 0.8 m/s, "
         "el caudal es área × 0.8 ≈ 48.9 m³ por segundo.",
    invertir_y=True,
)

PANEL = Problema(
    titulo="☀️ Energía de un panel solar en un día",
    historia=("Un panel solar produce poca potencia en la mañana, mucha al mediodía y poca "
              "en la tarde. Un medidor registra la potencia cada cierto tiempo entre las 6:00 "
              "y las 18:00. ¿Cuánta energía produjo en el día? La energía es el **área bajo "
              "la curva de potencia**."),
    f=lambda t: 4.5 * np.exp(-((t - 12) / 3) ** 2),
    formula=r"P(t) = 4.5\,e^{-\left(\frac{t-12}{3}\right)^2}",
    a=6, b=18,
    exacta=4.5 * 3 * math.sqrt(math.pi) * math.erf(2),
    eje_x="hora del día t (h)", eje_y="potencia P (kW)",
    resultado="Energía producida", unidad="kWh",
    n_defecto=6,
    nota="Con n = 6 equivale a leer el medidor cada 2 horas.",
)

# --------------------------------------------------------------------------
# Funciones matemáticas para practicar
# --------------------------------------------------------------------------
def _mate(titulo, f, formula, a, b, exacta, n):
    return Problema(titulo=titulo, historia="Función matemática para practicar.", f=f, formula=formula,
                    a=a, b=b, exacta=exacta, eje_x="x", eje_y="f(x)", resultado="Integral",
                    unidad="", n_defecto=n)


MATEMATICAS = [
    _mate("x² entre 0 y 3", lambda x: x**2, r"f(x) = x^2", 0, 3, 9.0, 6),
    _mate("x³ entre 0 y 2", lambda x: x**3, r"f(x) = x^3", 0, 2, 4.0, 6),
    _mate("sen(x) entre 0 y π", np.sin, r"f(x) = \mathrm{sen}(x)", 0, math.pi, 2.0, 6),
    _mate("eˣ entre 0 y 1", np.exp, r"f(x) = e^{x}", 0, 1, math.e - 1, 6),
    _mate("1/(1+x²) entre 0 y 1", lambda x: 1 / (1 + x**2), r"f(x) = \frac{1}{1+x^2}", 0, 1, math.pi / 4, 6),
    _mate("e^(−x²) entre 0 y 1 (no tiene antiderivada simple)", lambda x: np.exp(-x**2),
          r"f(x) = e^{-x^2}", 0, 1, math.sqrt(math.pi) / 2 * math.erf(1), 6),
]

TODOS = [CARRO, RIO, PANEL] + MATEMATICAS
