"""
MÓDULO 3 · Regla de Simpson 3/8 (compuesta)

Idea: tomar las franjas DE A TRES y pasar una CÚBICA (polinomio de grado 3)
por cada 4 puntos.

    Área ≈ 3h/8 · [ f(x0) + 3f(x1) + 3f(x2) + 2f(x3) + 3f(x4) + ... + 3f(x_{n-1}) + f(xn) ]

    h = (b − a) / n
    n = debe ser MÚLTIPLO DE 3 (cada cúbica usa 3 franjas)
"""

NOMBRE = "Simpson 3/8"
FACTOR = "3h/8"
REGLA_N = "n debe ser múltiplo de 3 (3, 6, 9, ...)"


def validar_n(n):
    if n < 3 or n % 3 != 0:
        raise ValueError(f"Simpson 3/8 necesita un número de subintervalos MÚLTIPLO DE 3; recibió n = {n}.")


def coeficientes(n):
    """Pesos de cada punto: 1, 3, 3, 2, 3, 3, 2, ..., 3, 3, 1"""
    validar_n(n)
    centro = [2 if i % 3 == 0 else 3 for i in range(1, n)]
    return [1] + centro + [1]


def integrar(f, a, b, n):
    """Aproxima la integral de f entre a y b con n/3 cúbicas."""
    validar_n(n)
    h = (b - a) / n
    suma = f(a) + f(b)
    for i in range(1, n):
        x = a + i * h
        if i % 3 == 0:
            suma += 2 * f(x)    # unión entre dos cúbicas
        else:
            suma += 3 * f(x)    # puntos internos de cada cúbica
    return 3 * h / 8 * suma


def paso_a_paso(f, a, b, n):
    h = (b - a) / n
    filas = []
    for i, c in enumerate(coeficientes(n)):
        x = a + i * h
        filas.append({"i": i, "x_i": x, "f(x_i)": f(x), "coeficiente": c, "c · f(x_i)": c * f(x)})
    suma = sum(fila["c · f(x_i)"] for fila in filas)
    return filas, h, suma, 3 * h / 8 * suma
