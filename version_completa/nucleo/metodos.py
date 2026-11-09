"""
Métodos numéricos implementados desde cero (sin scipy) para que cada paso
sea visible en la sustentación.

Todos devuelven un `Resultado` con el historial completo de iteraciones.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Callable

Funcion = Callable[[float], float]


@dataclass
class Iteracion:
    k: int
    x: float
    error_abs: float
    error_rel: float
    extra: dict = field(default_factory=dict)


@dataclass
class Resultado:
    metodo: str
    raiz: float
    convergio: bool
    iteraciones: list[Iteracion]
    evaluaciones: int
    tiempo_ms: float
    motivo: str = ""

    @property
    def n_iter(self) -> int:
        return len(self.iteraciones)

    @property
    def error_final(self) -> float:
        return self.iteraciones[-1].error_rel if self.iteraciones else math.nan


def _err_rel(nuevo: float, viejo: float) -> tuple[float, float]:
    ea = abs(nuevo - viejo)
    return ea, ea / abs(nuevo) if nuevo != 0 else ea


# ----------------------------------------------------------------------------
# 1. Punto fijo
# ----------------------------------------------------------------------------
def punto_fijo(g: Funcion, x0: float, tol: float = 1e-8, max_iter: int = 200,
               limite: float = 1e6) -> Resultado:
    t0 = time.perf_counter()
    x, hist, ev = x0, [], 0
    for k in range(1, max_iter + 1):
        xn = g(x); ev += 1
        if not math.isfinite(xn) or abs(xn) > limite:
            return Resultado("Punto fijo", xn, False, hist, ev,
                             (time.perf_counter() - t0) * 1e3, "divergió")
        ea, er = _err_rel(xn, x)
        hist.append(Iteracion(k, xn, ea, er, {"x_prev": x}))
        x = xn
        if er < tol:
            return Resultado("Punto fijo", x, True, hist, ev, (time.perf_counter() - t0) * 1e3)
    return Resultado("Punto fijo", x, False, hist, ev,
                     (time.perf_counter() - t0) * 1e3, "máx. iteraciones")


# ----------------------------------------------------------------------------
# 2. Steffensen (punto fijo acelerado con Δ² de Aitken)
# ----------------------------------------------------------------------------
def steffensen(g: Funcion, x0: float, tol: float = 1e-8, max_iter: int = 100,
               limite: float = 1e6) -> Resultado:
    t0 = time.perf_counter()
    x, hist, ev = x0, [], 0
    for k in range(1, max_iter + 1):
        x1 = g(x); x2 = g(x1); ev += 2
        den = x2 - 2 * x1 + x
        if not (math.isfinite(x1) and math.isfinite(x2)):
            return Resultado("Steffensen", x, False, hist, ev,
                             (time.perf_counter() - t0) * 1e3, "divergió")
        if den == 0:
            xn = x2
        else:
            xn = x - (x1 - x) ** 2 / den
        if not math.isfinite(xn) or abs(xn) > limite:
            return Resultado("Steffensen", xn, False, hist, ev,
                             (time.perf_counter() - t0) * 1e3, "divergió")
        ea, er = _err_rel(xn, x)
        hist.append(Iteracion(k, xn, ea, er))
        x = xn
        if er < tol:
            return Resultado("Steffensen", x, True, hist, ev, (time.perf_counter() - t0) * 1e3)
    return Resultado("Steffensen", x, False, hist, ev,
                     (time.perf_counter() - t0) * 1e3, "máx. iteraciones")


# ----------------------------------------------------------------------------
# 3. Newton-Raphson
# ----------------------------------------------------------------------------
def newton(f: Funcion, df: Funcion, x0: float, tol: float = 1e-8,
           max_iter: int = 100, limite: float = 1e6) -> Resultado:
    t0 = time.perf_counter()
    x, hist, ev = x0, [], 0
    for k in range(1, max_iter + 1):
        fx, dfx = f(x), df(x); ev += 2
        if dfx == 0 or not math.isfinite(dfx):
            return Resultado("Newton-Raphson", x, False, hist, ev,
                             (time.perf_counter() - t0) * 1e3, "derivada nula")
        xn = x - fx / dfx
        if not math.isfinite(xn) or abs(xn) > limite:
            return Resultado("Newton-Raphson", xn, False, hist, ev,
                             (time.perf_counter() - t0) * 1e3, "divergió")
        ea, er = _err_rel(xn, x)
        hist.append(Iteracion(k, xn, ea, er))
        x = xn
        if er < tol:
            return Resultado("Newton-Raphson", x, True, hist, ev, (time.perf_counter() - t0) * 1e3)
    return Resultado("Newton-Raphson", x, False, hist, ev,
                     (time.perf_counter() - t0) * 1e3, "máx. iteraciones")


# ----------------------------------------------------------------------------
# 4. Secante
# ----------------------------------------------------------------------------
def secante(f: Funcion, x0: float, x1: float, tol: float = 1e-8,
            max_iter: int = 100, limite: float = 1e6) -> Resultado:
    t0 = time.perf_counter()
    f0, f1, ev, hist = f(x0), f(x1), 2, []
    for k in range(1, max_iter + 1):
        if f1 == f0:
            return Resultado("Secante", x1, False, hist, ev,
                             (time.perf_counter() - t0) * 1e3, "división por cero")
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        if not math.isfinite(x2) or abs(x2) > limite:
            return Resultado("Secante", x2, False, hist, ev,
                             (time.perf_counter() - t0) * 1e3, "divergió")
        ea, er = _err_rel(x2, x1)
        hist.append(Iteracion(k, x2, ea, er))
        x0, f0, x1 = x1, f1, x2
        f1 = f(x1); ev += 1
        if er < tol:
            return Resultado("Secante", x1, True, hist, ev, (time.perf_counter() - t0) * 1e3)
    return Resultado("Secante", x1, False, hist, ev,
                     (time.perf_counter() - t0) * 1e3, "máx. iteraciones")


# ----------------------------------------------------------------------------
# 5. Bisección
# ----------------------------------------------------------------------------
def biseccion(f: Funcion, a: float, b: float, tol: float = 1e-8,
              max_iter: int = 200) -> Resultado:
    t0 = time.perf_counter()
    fa, fb, ev, hist = f(a), f(b), 2, []
    if fa * fb > 0:
        return Resultado("Bisección", math.nan, False, hist, ev,
                         (time.perf_counter() - t0) * 1e3, "sin cambio de signo en [a, b]")
    c_prev = a
    for k in range(1, max_iter + 1):
        c = (a + b) / 2
        fc = f(c); ev += 1
        ea, er = _err_rel(c, c_prev)
        hist.append(Iteracion(k, c, ea, er, {"a": a, "b": b}))
        if fc == 0 or er < tol:
            return Resultado("Bisección", c, True, hist, ev, (time.perf_counter() - t0) * 1e3)
        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc
        c_prev = c
    return Resultado("Bisección", c, False, hist, ev,
                     (time.perf_counter() - t0) * 1e3, "máx. iteraciones")


# ----------------------------------------------------------------------------
# 6. Sección dorada (optimización: dónde está el pico de capacidad)
# ----------------------------------------------------------------------------
def seccion_dorada_max(f: Funcion, a: float, b: float, tol: float = 1e-6,
                       max_iter: int = 200) -> tuple[float, int]:
    """Máximo de una función unimodal en [a, b]. Devuelve (x*, iteraciones)."""
    phi = (math.sqrt(5) - 1) / 2
    c, d = b - phi * (b - a), a + phi * (b - a)
    fc, fd = f(c), f(d)
    k = 0
    while (b - a) > tol * max(1.0, abs(a) + abs(b)) and k < max_iter:
        k += 1
        if fc > fd:
            b, d, fd = d, c, fc
            c = b - phi * (b - a); fc = f(c)
        else:
            a, c, fc = c, d, fd
            d = a + phi * (b - a); fd = f(d)
    return (a + b) / 2, k


# ----------------------------------------------------------------------------
# Orden de convergencia experimental
# ----------------------------------------------------------------------------
def orden_convergencia(res: Resultado, raiz_ref: float | None = None) -> float:
    """
    Estima p con  p ≈ ln(e_{k+1}/e_k) / ln(e_k/e_{k-1}),  e_k = |x_k − x*|.
    Se promedian las últimas estimaciones confiables.
    """
    xr = res.raiz if raiz_ref is None else raiz_ref
    e = [abs(it.x - xr) for it in res.iteraciones]
    e = [v for v in e if v > 1e-13 * max(1.0, abs(xr))]
    ps = []
    for k in range(1, len(e) - 1):
        num, den = math.log(e[k + 1] / e[k]), math.log(e[k] / e[k - 1])
        if den != 0 and math.isfinite(num / den):
            ps.append(num / den)
    if not ps:
        return math.nan
    ultimos = ps[-3:]
    return sum(ultimos) / len(ultimos)
