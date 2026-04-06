"""
Script de prueba del flujo completo: Mock -> DTO -> Mapper -> Service -> Elasticsearch
"""

from back.port.infrastructure.outbound.mock_register_bank import bank
from back.port.infrastructure.dto.MockInputDto import MockInputDto
from back.port.application.PortCountersService import PortCountersService
from back.port.infrastructure.elasticshearch.adapter.elasticshearchAdapter import (
    ElasticsearchAdapter,
)


def test_full_flow():
    print("=" * 60)
    print("TEST: Flujo completo - DTO -> Domain -> Elasticsearch")
    print("=" * 60)

    service = PortCountersService(max_ports=4)
    es_adapter = ElasticsearchAdapter()

    print("\n[1] Obteniendo contadores del MockRegisterBank...")
    raw_counters = bank.read_counters(0)
    print(f"    Raw counters: {raw_counters}")

    print("\n[2] Convirtiendo a MockInputDto...")
    dto = MockInputDto(
        port_id=0,
        rx_port_in_frames=raw_counters.rx_port_in_frames,
        rx_port_out_frames=raw_counters.rx_port_out_frames,
        rx_port_gen_frames=raw_counters.rx_port_gen_frames,
        rx_port_in_true_frames=raw_counters.rx_port_in_true_frames,
        rx_port_gen_true_frames=raw_counters.rx_port_gen_true_frames,
        tx_port_in_frames=raw_counters.tx_port_in_frames,
        tx_port_out_frames=raw_counters.tx_port_out_frames,
        tx_port_in_true_frames=raw_counters.tx_port_in_true_frames,
        gen_frames=raw_counters.gen_frames,
    )
    print(f"    DTO: rx_in={dto.rx_port_in_frames}, gen={dto.gen_frames}")

    print("\n[3] Ejecutando Service (validacion + mapeo)...")
    es_domain = service.save_counters(dto, port_id=0)
    print(
        f"    ElasticsearchDomain: port_id={es_domain.port_id}, rx_in={es_domain.rx_port_in_frames}"
    )

    print("\n[4] Guardando en Elasticsearch...")
    result = es_adapter.publish_counters(es_domain)
    print(f"    Resultado: {result}")

    print("\n" + "=" * 60)
    print("[OK] Flujo completado correctamente!")
    print("=" * 60)


if __name__ == "__main__":
    test_full_flow()
