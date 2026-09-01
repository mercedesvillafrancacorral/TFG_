"""
Test latencia para medir el tiempo de respuesta de la API
"""

import argparse
import csv
import math
import statistics
import time
import httpx


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("Debe ser un entero mayor que cero.")
    return number


def percentile(data, p):
    """Percentil mediante el método de rango más próximo."""
    ordered = sorted(data)
    index = max(0, math.ceil(len(ordered) * p / 100) - 1)
    return ordered[index]


def measure_latency(url, port_id, n, csv_path):
    endpoint = f"{url.rstrip('/')}/ports/{port_id}/counters"
    latencies = []
    failures = 0

    print(f"Endpoint: {endpoint}")
    print(f"Peticiones secuenciales: {n}")
    print(f"Archivo de resultados: {csv_path}")

    
    with open(csv_path, "x", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "peticion",
            "endpoint",
            "duracion_ms",
            "estado_http",
            "resultado",
            "detalle",
        ])

        with httpx.Client(timeout=10.0) as client:
            for i in range(1, n + 1):
                status_code = ""
                detail = ""

                t0 = time.perf_counter()

                try:
                    response = client.get(endpoint)
                except httpx.RequestError as exc:
                    elapsed_ms = (time.perf_counter() - t0) * 1000
                    result = (
                        "timeout"
                        if isinstance(exc, httpx.TimeoutException)
                        else "error_conexion"
                    )
                    detail = f"{type(exc).__name__}: {exc}"
                else:
                    elapsed_ms = (time.perf_counter() - t0) * 1000
                    status_code = response.status_code

                    # Este endpoint debe devolver HTTP 200.
                    if status_code == 200:
                        result = "ok"
                        latencies.append(elapsed_ms)
                    else:
                        result = "estado_http_inesperado"
                        detail = f"Se esperaba HTTP 200; recibido {status_code}"

                if result != "ok":
                    failures += 1

                writer.writerow([
                    i,
                    endpoint,
                    elapsed_ms,
                    status_code,
                    result,
                    detail,
                ])
                file.flush()

                print(f"[{i:>3}/{n}] {elapsed_ms:.2f} ms — {result}")

    return latencies, failures


def report(latencies, failures):
    total = len(latencies) + failures

    print("\n" + "=" * 45)
    print("RESULTADOS")
    print("=" * 45)
    print(f"Peticiones realizadas: {total}")
    print(f"Respuestas HTTP 200:   {len(latencies)}")
    print(f"Fallos:                {failures}")
    print(f"Porcentaje de fallos:  {100 * failures / total:.2f}%")

    if not latencies:
        print("No hay respuestas HTTP 200 para calcular estadísticas.")
        return

    print("\nTiempo de respuesta de las peticiones HTTP 200:")
    print(f"Mínima:  {min(latencies):.2f} ms")
    print(f"Máxima:  {max(latencies):.2f} ms")
    print(f"Media:   {statistics.mean(latencies):.2f} ms")
    print(f"Mediana: {statistics.median(latencies):.2f} ms")

    if len(latencies) >= 2:
        print(f"Desviación típica muestral: "
              f"{statistics.stdev(latencies):.2f} ms")
    else:
        print("Desviación típica muestral: no disponible")

    for p in (90, 95, 99):
        print(f"P{p}: {percentile(latencies, p):.2f} ms")

    print("Método de percentiles: rango más próximo.")
    print("La primera petición está incluida en las estadísticas.")
    print("=" * 45)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Medición del tiempo de respuesta de la API."
    )
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--n", type=positive_int, default=100)
    parser.add_argument("--csv", default="latencias.csv")
    args = parser.parse_args()

    if args.port < 0:
        parser.error("--port no puede ser negativo.")

    try:
        latencies, failures = measure_latency(
            args.url, args.port, args.n, args.csv
        )
    except FileExistsError:
        parser.error("El archivo CSV ya existe. Utiliza otro nombre.")
    else:
        report(latencies, failures)