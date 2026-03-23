
from tfg_fpga.back.application.ports import CountersReaderPort
from tfg_fpga.back.domain.models import PortCounters
from tfg_fpga.back.infrastructure.outbound.fpga.mock_register_bank import
from tfg_fpga.back.port.application.PortCountersService import PortCountersService 
"Implementamos una clase abstracta que es lo mas parecido a una interfaz en java"
from abc import ABC

class PortCountersServiceImpl:

    def __init__(self, hw: CountersReaderPort):
        self.hw = hw

    def list_ports(self) -> list[int]:
        return self.hw.list_ports()

    def get(self, port_id: int) -> PortCounters:
        return self.hw.read_counters(port_id)