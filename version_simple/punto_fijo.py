"""
¿Cuántos servidores necesito para que trabajen al 80 %?
Versión simple para la presentación: todo el cálculo está en este archivo.

IDEA
  - Cada servidor atiende C peticiones por segundo.
  - Pero con más servidores se pierde tiempo coordinándolos (pérdida p).
  - Capacidad real de N servidores:   X(N) = C·N / (1 + p·N·(N−1))
  - Queremos que trabajen al 80 %:     0.8 · X(N) = λ
  - Despejando N queda en forma de punto fijo:
        N = g(N) = λ / (0.8·C) · (1 + p·N·(N−1))
"""
import math


def g(N, lam, C, p, rho=0.8):
    """Función de punto fijo."""
    return lam / (rho * C) * (1 + p * N * (N - 1))


def derivada_g(N, lam, C, p, rho=0.8):
    """g'(N). Si |g'(N*)| < 1, el método converge."""
    return lam / (rho * C) * p * (2 * N - 1)


def capacidad(N, C, p):
    """Peticiones por segundo que atienden N servidores en total."""
    return C * N / (1 + p * N * (N - 1))


def punto_fijo(lam, C, p, rho=0.8, tol=1e-6, max_iter=100):
    """
    Método de punto fijo:  N(k+1) = g(N(k))
    Devuelve (N*, tabla de iteraciones, convergió?)
    """
    N = lam / (rho * C)          # Valor inicial: como si no hubiera pérdidas
    tabla = []
    for k in range(1, max_iter + 1):
        N_nuevo = g(N, lam, C, p, rho)
        error = abs(N_nuevo - N) / abs(N_nuevo)
        tabla.append({"k": k, "N_k": N, "g(N_k)": N_nuevo, "error": error})
        if N_nuevo > 10_000:     # Se disparó: no hay solución
            return None, tabla, False
        N = N_nuevo
        if error < tol:
            return N, tabla, True
    return None, tabla, False


def solucion_exacta(lam, C, p, rho=0.8):
    """
    Comprobación: la ecuación también es cuadrática,
        p·k·N² − (1 + p·k)·N + k = 0,   con k = λ/(ρ·C)
    así que podemos verificar el resultado con la fórmula general.
    """
    k = lam / (rho * C)
    a, b, c = p * k, -(1 + p * k), k
    disc = b * b - 4 * a * c
    if disc < 0:
        return None                       # no hay solución: servidores saturados
    return (-b - math.sqrt(disc)) / (2 * a)  # raíz pequeña = la útil


def trafico_maximo(C, p, rho=0.8):
    """Más allá de N = 1/√p, agregar servidores ya no aumenta la capacidad."""
    N_pico = 1 / math.sqrt(p)
    return N_pico, rho * capacidad(N_pico, C, p)


def recursos(N_estrella, lam, C, p, vcpu=2, ram_gb=4):
    """Convierte N* en recursos concretos."""
    servidores = math.ceil(N_estrella)
    uso = lam / capacidad(servidores, C, p)
    return {"servidores": servidores, "vcpu": servidores * vcpu,
            "ram_gb": servidores * ram_gb, "uso": uso}


def simular(lam0, r, C, p, minutos=60, rho=0.8):
    """El tráfico crece λ(t) = λ0·e^(r·t); en cada minuto se resuelve con punto fijo."""
    filas = []
    for t in range(minutos + 1):
        lam = lam0 * math.exp(r * t)
        N, tabla, ok = punto_fijo(lam, C, p, rho)
        if ok:
            rec = recursos(N, lam, C, p)
            filas.append({"minuto": t, "trafico": lam, "N*": N, "servidores": rec["servidores"],
                          "uso": rec["uso"], "iteraciones": len(tabla), "estado": "OK"})
        else:
            filas.append({"minuto": t, "trafico": lam, "N*": None, "servidores": None,
                          "uso": None, "iteraciones": len(tabla), "estado": "SATURADO"})
    return filas


if __name__ == "__main__":
    lam, C, p = 600, 100, 0.002
    N, tabla, ok = punto_fijo(lam, C, p)
    print(f"Tráfico = {lam} req/s, capacidad por servidor = {C} req/s, pérdida p = {p}\n")
    print(f"{'k':>3} {'N_k':>12} {'g(N_k)':>12} {'error':>10}")
    for f in tabla:
        print(f"{f['k']:>3} {f['N_k']:>12.6f} {f['g(N_k)']:>12.6f} {f['error']:>10.2e}")
    print(f"\nPunto fijo:      N* = {N:.6f}  ({len(tabla)} iteraciones)")
    print(f"Fórmula exacta:  N  = {solucion_exacta(lam, C, p):.6f}")
    print(f"g'(N*) = {derivada_g(N, lam, C, p):.3f}  (< 1 → converge)")
    rec = recursos(N, lam, C, p)
    print(f"Asignar: {rec['servidores']} servidores, {rec['vcpu']} vCPU, {rec['ram_gb']} GB RAM, uso real {rec['uso']:.1%}")
    Np, lmax = trafico_maximo(C, p)
    print(f"Tráfico máximo que se puede atender al 80 %: {lmax:.0f} req/s (con {Np:.1f} servidores)")
