"""
MÓDULO 2 · Regla de Simpson 1/3 (compuesta)

Idea: tomar las franjas DE A DOS y pasar una PARÁBOLA por cada 3 puntos.
La parábola se adapta mejor a las curvas que una línea recta.

    Área ≈ h/3 · [ f(x0) + 4f(x1) + 2f(x2) + 4f(x3) + ... + 4f(x_{n-1}) + f(xn) ]

    h = (b − a) / n
    n = debe ser PAR (cada parábola usa 2 franjas)
"""

NOMBRE = "Simpson 1/3"
FACTOR = "h/3"
REGLA_N = "n debe ser par (2, 4, 6, ...)"


def validar_n(n):
    if n < 2 or n % 2 != 0:
        raise ValueError(f"Simpson 1/3 necesita un número PAR de subintervalos; recibió n = {n}.")


def coeficientes(n):
    """Pesos de cada punto: 1, 4, 2, 4, 2, ..., 4, 1"""
    validar_n(n)
    centro = [4 if i % 2 == 1 else 2 for i in range(1, n)]
    return [1] + centro + [1]


def integrar(f, a, b, n):
    """Aproxima la integral de f entre a y b con n/2 parábolas."""
    validar_n(n)
    h = (b - a) / n
    suma = f(a) + f(b)
    for i in range(1, n):
        x = a + i * h
        if i % 2 == 1:
            suma += 4 * f(x)    # puntos impares: centro de cada parábola
        else:
            suma += 2 * f(x)    # puntos pares: unión entre dos parábolas
    return h / 3 * suma


def paso_a_paso(f, a, b, n):
    h = (b - a) / n
    filas = []
    for i, c in enumerate(coeficientes(n)):
        x = a + i * h
        filas.append({"i": i, "x_i": x, "f(x_i)": f(x), "coeficiente": c, "c · f(x_i)": c * f(x)})
    suma = sum(fila["c · f(x_i)"] for fila in filas)
    return filas, h, suma, h / 3 * suma
