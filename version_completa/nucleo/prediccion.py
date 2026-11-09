"""
Pronóstico de tráfico por mínimos cuadrados (otro método numérico).

Se ajustan tres modelos sobre una ventana de datos recientes y se escoge el
de menor error cuadrático:
  - lineal:       λ = a + b·t
  - exponencial:  ln λ = a + b·t           (linealización)
  - logarítmico:  λ = a + b·ln(1 + t − t₀)
Las ecuaciones normales (AᵀA)c = Aᵀy se resuelven por eliminación de Gauss.
"""
from __future__ import annotations

import numpy as np


def _gauss(A: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Eliminación gaussiana con pivoteo parcial (2x2 o más)."""
    M = np.hstack([A.astype(float), y.reshape(-1, 1).astype(float)])
    n = len(M)
    for i in range(n):
        p = i + int(np.argmax(np.abs(M[i:, i])))
        M[[i, p]] = M[[p, i]]
        if M[i, i] == 0:
            raise np.linalg.LinAlgError("Sistema singular")
        for j in range(i + 1, n):
            M[j] -= M[j, i] / M[i, i] * M[i]
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (M[i, -1] - M[i, i + 1:n] @ x[i + 1:]) / M[i, i]
    return x


def _ajuste(phi: np.ndarray, y: np.ndarray) -> np.ndarray:
    A = np.column_stack([np.ones_like(phi), phi])
    return _gauss(A.T @ A, A.T @ y)


def pronosticar(t: np.ndarray, lam: np.ndarray, horizonte: float) -> tuple[float, str]:
    """Pronostica λ(t_final + horizonte). Devuelve (valor, modelo_elegido)."""
    if len(t) < 3:
        return float(lam[-1]), "último valor"
    t0 = t[0]
    tt = t - t0
    th = tt[-1] + horizonte
    candidatos = {}

    c = _ajuste(tt, lam)
    candidatos["lineal"] = (c[0] + c[1] * tt, c[0] + c[1] * th)

    c = _ajuste(tt, np.log(lam))
    candidatos["exponencial"] = (np.exp(c[0] + c[1] * tt), np.exp(c[0] + c[1] * th))

    c = _ajuste(np.log1p(tt), lam)
    candidatos["logarítmico"] = (c[0] + c[1] * np.log1p(tt), c[0] + c[1] * np.log1p(th))

    mejor = min(candidatos, key=lambda k: float(np.sum((candidatos[k][0] - lam) ** 2)))
    valor = float(candidatos[mejor][1])
    # Protección: un pronóstico no debería caer por debajo del 50 % del valor actual
    return max(valor, 0.5 * float(lam[-1])), mejor
