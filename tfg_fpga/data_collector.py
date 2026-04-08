import time

from back.port.infrastructure.outbound.mock_register_bank import bank
from back.port.infrastructure.outbound.MockHardwareAdapter import MockHardwareAdapter
from back.port.infrastructure.elasticsearch.repository.elasticsearchRepository import ElasticsearchRepository
from back.port.application.PortCountersService import PortCountersService



def main():

    print("🚀 Iniciando recolector de datos...")

    # 1. Montar arquitectura
    hardware = MockHardwareAdapter(bank)
    repository = ElasticsearchRepository()
    service = PortCountersService(hardware, repository)

    ports = service.get_ports()

    print(f"📡 Puertos detectados: {ports}")
    print("📊 Enviando datos a Elasticsearch...\n")

    try:
        while True:
            for port_id in ports:
                counters = service.get_counters(port_id)

                # Guardar en Elasticsearch
                service.repository.save(port_id, counters)

                print(
                    f"Puerto {port_id} | RX: {counters.rx_port_in_frames} | GEN: {counters.gen_frames}"
                )

            print("-" * 50)
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Recolector detenido")


    if __name__ == "__main__":
          main()
