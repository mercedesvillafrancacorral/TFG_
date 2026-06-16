"""
Medición de latencia de la API REST.
Uso: python latency_test.py [--url URL] [--port PORT_ID] [--n N_REQUESTS]
"""
import time
import argparse
import statistics
import httpx


def measure_latency(url: str, port_id: int, n: int) -> list[float]:
    latencies = []
    endpoint = f"{url}/ports/{port_id}/counters"
    print(f"Midiendo latencia en {endpoint} ({n} peticiones)...\n")

    with httpx.Client(timeout=10) as client:
        for i in range(n):
            t0 = time.perf_counter()
            r = client.get(endpoint)
            t1 = time.perf_counter()
            r.raise_for_status()
            ms = (t1 - t0) * 1000
            latencies.append(ms)
            print(f"  [{i+1:>3}/{n}] {ms:.2f} ms")

    return latencies


def report(latencies: list[float]):
    latencies_sorted = sorted(latencies)
    n = len(latencies)

    def percentile(data, p):
        idx = int(len(data) * p / 100)
        return data[min(idx, len(data) - 1)]

    print("\n" + "=" * 40)
    print("RESULTADOS DE LATENCIA")
    print("=" * 40)
    print(f"  Peticiones:  {n}")
    print(f"  Mínima:      {min(latencies):.2f} ms")
    print(f"  Máxima:      {max(latencies):.2f} ms")
    print(f"  Media:       {statistics.mean(latencies):.2f} ms")
    print(f"  Mediana:     {statistics.median(latencies):.2f} ms")
    print(f"  Desv. típ.:  {statistics.stdev(latencies):.2f} ms")
    print(f"  P90:         {percentile(latencies_sorted, 90):.2f} ms")
    print(f"  P95:         {percentile(latencies_sorted, 95):.2f} ms")
    print(f"  P99:         {percentile(latencies_sorted, 99):.2f} ms")
    print("=" * 40)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--n", type=int, default=50)
    args = parser.parse_args()

    latencies = measure_latency(args.url, args.port, args.n)
    report(latencies)
