"""
Modelo físico-computacional del clúster.

- Tráfico λ(t): exponencial, logarítmico o datos de un CSV.
- Capacidad: Ley de Escalabilidad Universal (USL, N. Gunther) con
  penalización térmica opcional (throttling por calor del rack).
- Ecuación de balance:   ρ · X_eff(N) = λ
  Forma de punto fijo:   N = g(N) = λ·D(N) / (ρ·X₁·η(N))
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np


# ----------------------------------------------------------------------------
# Parámetros
# ----------------------------------------------------------------------------
@dataclass
class ParametrosServidor:
    X1: float = 120.0          # req/s que atiende UNA réplica al 100 %
    sigma: float = 0.03        # contención (colas, bloqueos)
    kappa: float = 0.0004      # coherencia (sincronización entre réplicas)
    rho: float = 0.80          # utilización objetivo

    # Recursos por réplica
    vcpu_por_replica: int = 2
    ram_base_mb: float = 512.0     # RAM fija de cada contenedor
    ram_conexion_mb: float = 4.0   # RAM por petición concurrente

    # Modelo térmico (rack compartido)
    termico: bool = True
    T_ambiente: float = 24.0       # °C de la sala
    dT_utilizacion: float = 45.0   # °C que sube un nodo al 100 % de uso
    h_rack: float = 0.35           # °C extra por cada réplica en el rack
    T_throttle: float = 70.0       # °C donde empieza a bajar la frecuencia
    beta: float = 0.02             # pérdida de rendimiento por °C sobre el umbral
    suavizado: float = 2.0         # suaviza el umbral (softplus) → derivable
    T_limite: float = 85.0         # °C máximo seguro

    # Costos (USD por hora)
    costo_vcpu_h: float = 0.040
    costo_gb_h: float = 0.005


@dataclass
class ParametrosTrafico:
    modelo: str = "exponencial"    # "exponencial" | "logaritmico" | "csv"
    lambda0: float = 200.0         # req/s en t = 0
    r: float = 0.01                # tasa exponencial (1/min)
    A: float = 300.0               # amplitud logarítmica (req/s)
    b: float = 0.5                 # escala logarítmica
    ruido: float = 0.05            # ±5 % de ruido uniforme
    picos: list[tuple[int, int, float]] = field(default_factory=list)  # (inicio, duración, factor)
    datos_csv: np.ndarray | None = None
    semilla: int = 7


# ----------------------------------------------------------------------------
# Tráfico
# ----------------------------------------------------------------------------
def serie_trafico(p: ParametrosTrafico, minutos: int) -> np.ndarray:
    """Devuelve λ(t) en req/s para t = 0..minutos-1."""
    t = np.arange(minutos, dtype=float)
    if p.modelo == "exponencial":
        lam = p.lambda0 * np.exp(p.r * t)
    elif p.modelo == "logaritmico":
        lam = p.lambda0 + p.A * np.log1p(p.b * t)
    elif p.modelo == "csv":
        if p.datos_csv is None or len(p.datos_csv) == 0:
            raise ValueError("No se cargaron datos de tráfico.")
        datos = np.asarray(p.datos_csv, dtype=float)
        lam = np.resize(datos, minutos) if len(datos) < minutos else datos[:minutos].copy()
    else:
        raise ValueError(f"Modelo de tráfico desconocido: {p.modelo}")

    for inicio, dur, factor in p.picos:
        lam[inicio:inicio + dur] *= factor

    if p.ruido > 0:
        rng = np.random.default_rng(p.semilla)
        lam *= 1 + rng.uniform(-p.ruido, p.ruido, size=minutos)
    return np.maximum(lam, 1.0)


# ----------------------------------------------------------------------------
# Capacidad (USL + térmico) y sus derivadas analíticas
# ----------------------------------------------------------------------------
def D(N, s: ParametrosServidor):
    """Denominador USL: 1 + σ(N−1) + κN(N−1)."""
    return 1 + s.sigma * (N - 1) + s.kappa * N * (N - 1)


def dD(N, s: ParametrosServidor):
    return s.sigma + s.kappa * (2 * N - 1)


def temperatura(N, s: ParametrosServidor, U=None):
    """Temperatura estimada del nodo (°C). Si U es None se usa el objetivo ρ."""
    U = s.rho if U is None else U
    return s.T_ambiente + s.dT_utilizacion * U + s.h_rack * N


def _softplus(z):
    return np.logaddexp(0.0, z)


def _sigmoide(z):
    return 0.5 * (1 + np.tanh(z / 2))


def eta(N, s: ParametrosServidor):
    """Eficiencia térmica η(N) ∈ (0, 1]: 1 = sin throttling."""
    if not s.termico:
        return np.ones_like(np.asarray(N, dtype=float)) if np.ndim(N) else 1.0
    z = (temperatura(N, s) - s.T_throttle) / s.suavizado
    return np.maximum(1 - s.beta * s.suavizado * _softplus(z), 0.05)


def deta(N, s: ParametrosServidor):
    if not s.termico:
        return np.zeros_like(np.asarray(N, dtype=float)) if np.ndim(N) else 0.0
    z = (temperatura(N, s) - s.T_throttle) / s.suavizado
    return -s.beta * s.h_rack * _sigmoide(z)


def capacidad(N, s: ParametrosServidor):
    """Throughput efectivo X_eff(N) en req/s."""
    return s.X1 * N * eta(N, s) / D(N, s)


def dcapacidad(N, s: ParametrosServidor):
    e, de, d, dd = eta(N, s), deta(N, s), D(N, s), dD(N, s)
    return s.X1 * ((e + N * de) * d - N * e * dd) / d**2


# ----------------------------------------------------------------------------
# Ecuación de balance en sus dos formas
# ----------------------------------------------------------------------------
def g(N, lam, s: ParametrosServidor):
    """Forma de punto fijo  N = g(N)."""
    return lam * D(N, s) / (s.rho * s.X1 * eta(N, s))


def dg(N, lam, s: ParametrosServidor):
    e, de = eta(N, s), deta(N, s)
    return lam / (s.rho * s.X1) * (dD(N, s) * e - D(N, s) * de) / e**2


def F(N, lam, s: ParametrosServidor):
    """Forma de raíz  F(N) = ρ·X_eff(N) − λ = 0."""
    return s.rho * capacidad(N, s) - lam


def dF(N, lam, s: ParametrosServidor):
    return s.rho * dcapacidad(N, s)


# ----------------------------------------------------------------------------
# Recursos derivados de N
# ----------------------------------------------------------------------------
@dataclass
class Recursos:
    replicas: int
    vcpu: int
    ram_gb: float
    utilizacion: float
    temperatura: float
    conexiones: float
    costo_h: float


def recursos(replicas: int, lam: float, s: ParametrosServidor) -> Recursos:
    cap = float(capacidad(replicas, s))
    U = lam / cap
    Ue = min(U, 0.99)
    # Ley de Little: L = λ·W, con W = 1/(X1·(1−U)) (cola M/M/1)
    L = lam / (s.X1 * (1 - Ue))
    ram_gb = (replicas * s.ram_base_mb + L * s.ram_conexion_mb) / 1024
    vcpu = replicas * s.vcpu_por_replica
    T = float(temperatura(replicas, s, U=min(U, 1.3)))
    costo = vcpu * s.costo_vcpu_h + ram_gb * s.costo_gb_h
    return Recursos(replicas, vcpu, ram_gb, U, T, L, costo)


def n_inicial(lam: float, s: ParametrosServidor) -> float:
    """Estimación lineal ideal (sin sobrecostos): N₀ = λ/(ρ·X₁)."""
    return lam / (s.rho * s.X1)


def lambda_maximo(s: ParametrosServidor, n_pico: float) -> float:
    return float(s.rho * capacidad(n_pico, s))


def n_pico_analitico(s: ParametrosServidor) -> float:
    """Pico de la USL pura (sin térmico): √((1−σ)/κ)."""
    return math.sqrt((1 - s.sigma) / s.kappa) if s.kappa > 0 else math.inf
