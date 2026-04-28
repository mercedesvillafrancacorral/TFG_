import time
import os
import logging
import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

API_URL = os.getenv("API_URL", "http://api:8000")


def wait_for_api(retries=30, delay=2):
    for _ in range(retries):
        try:
            r = httpx.get(f"{API_URL}/health", timeout=2)
            if r.status_code == 200:
                logger.info("API disponible")
                return True
        except Exception:
            pass
        logger.warning("Esperando API...")
        time.sleep(delay)
    logger.error("No se pudo conectar a la API")
    return False


def get_ports() -> list:
    r = httpx.get(f"{API_URL}/ports", timeout=5)
    r.raise_for_status()
    return r.json()["ports"]


def collect_once(ports: list):
    for port_id in ports:
        try:
            r = httpx.get(f"{API_URL}/ports/{port_id}/counters", timeout=5)
            r.raise_for_status()
            data = r.json()
            logger.info(f"Puerto {port_id} | RX: {data['rx_port_in_frames']} | GEN: {data['rx_port_gen_frames']}")

        except Exception as e:
            logger.error(f"Puerto {port_id} | Error: {e}")


def main():
    logger.info("Iniciando recolector de datos...")

    if not wait_for_api():
        raise RuntimeError("API no está disponible")

    ports = get_ports()
    logger.info(f"Puertos detectados: {ports}")
    logger.info("Recolectando y guardando en Elasticsearch...")

    try:
        while True:
            collect_once(ports)
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Recolector detenido")


if __name__ == "__main__":
    main()
