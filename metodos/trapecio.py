"""
MÓDULO 1 · Regla del Trapecio (compuesta)

Idea: dividir el área bajo la curva en n franjas y aproximar cada franja
con un TRAPECIO (unir los puntos con líneas rectas).

    Área ≈ h/2 · [ f(x0) + 2f(x1) + 2f(x2) + ... + 2f(x_{n-1}) + f(xn) ]

    h = (b − a) / n     (ancho de cada franja)
    n = cualquier número entero ≥ 1
"""

NOMBRE = "Trapecio"
FACTOR = "h/2"
REGLA_N = "n puede ser cualquier entero mayor o igual que 1"


def validar_n(n):
    """El trapecio funciona con cualquier n ≥ 1."""
    if n < 1:
        raise ValueError("El trapecio necesita al menos 1 subintervalo (n ≥ 1).")


def coeficientes(n):
    """Pesos de cada punto: 1, 2, 2, ..., 2, 1"""
    validar_n(n)
    return [1] + [2] * (n - 1) + [1]


def integrar(f, a, b, n):
    """Aproxima la integral de f entre a y b con n trapecios."""
    validar_n(n)
    h = (b - a) / n
    suma = f(a) + f(b)                 # los extremos van una sola vez
    for i in range(1, n):
        suma += 2 * f(a + i * h)       # los puntos de adentro van dos veces
    return h / 2 * suma


def paso_a_paso(f, a, b, n):
    """Tabla para hacer el cálculo como en el cuaderno."""
    h = (b - a) / n
    filas = []
    for i, c in enumerate(coeficientes(n)):
        x = a + i * h
        filas.append({"i": i, "x_i": x, "f(x_i)": f(x), "coeficiente": c, "c · f(x_i)": c * f(x)})
    suma = sum(fila["c · f(x_i)"] for fila in filas)
    return filas, h, suma, h / 2 * suma
