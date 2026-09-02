import os

from back.port.application.PortCountersService import PortCountersService
from back.port.infrastructure.elasticsearch.repository.elasticsearchRepository import ElasticsearchRepository

repo = ElasticsearchRepository()

mode = os.getenv("MODE", "simulation").lower()

if mode == "real":
    from back.port.infrastructure.outbound.fpga_real_adapter import FPGATrafficGeneratorAdapter
    uart_port = os.getenv("UART_PORT")
    if not uart_port:
        raise RuntimeError("MODE=real requiere UART_PORT (arráncalo con start.sh, que lo detecta automáticamente)")
    extended_register_layout = os.getenv("EXTENDED_REGISTER_LAYOUT", "false").lower() == "true"
    hardware = FPGATrafficGeneratorAdapter(
        uart_port=uart_port,
        extended_register_layout=extended_register_layout,
    )
else:
    # Fase 1: Simulación local — ZCU102=4 puertos, Alveo U200=2 puertos
    from back.port.infrastructure.outbound.mock_port_hardware_adapter import PortHardwareAdapter
    hardware = PortHardwareAdapter(port_count=4)

service = PortCountersService(hardware, repo)


def get_port_service():
    return service