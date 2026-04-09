import time

from back.port.infrastructure.outbound.mock_register_bank import bank
from back.port.infrastructure.outbound.MockHardwareAdapter import MockHardwareAdapter
from back.port.infrastructure.elasticsearch.repository.elasticsearchRepository import ElasticsearchRepository
from back.port.application.PortCountersService import PortCountersService


def wait_for_elasticsearch(repository, retries=30, delay=2):
    for _ in range(retries):
        try:
            if repository.es.ping():
                print("✅ Elasticsearch disponible")
                return True
        except Exception:
            pass

        print("⏳ Esperando Elasticsearch...")
        time.sleep(delay)

    print("❌ No se pudo conectar a Elasticsearch")
    return False


def main():
    print("🚀 Iniciando recolector de datos...")

    hardware = MockHardwareAdapter(bank)
    repository = ElasticsearchRepository()

    if not wait_for_elasticsearch(repository):
        raise RuntimeError("Elasticsearch no está disponible")

    service = PortCountersService(hardware, repository)
    ports = service.get_ports()

    print(f"📡 Puertos detectados: {ports}")
    print("📊 Enviando datos a Elasticsearch...\n")

    try:
        while True:
            for port_id in ports:
                counters = service.get_counters(port_id)
                repository.save(port_id, counters)

                print(
                    f"Puerto {port_id} | RX: {counters.rx_port_in_frames} | GEN: {counters.gen_frames}"
                )

            print("-" * 50)
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Recolector detenido")


if __name__ == "__main__":
    main()