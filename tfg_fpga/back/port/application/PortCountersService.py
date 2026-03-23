from tfg_fpga.back.application.ports import CountersReaderPort
from tfg_fpga.back.domain.models import PortCounters
from tfg_fpga.back.infrastructure.outbound.fpga.mock_register_bank import 
"Implementamos una clase abstracta que es lo mas parecido a una interfaz en java"
from abc import ABC

class PortCountersService(ABC):
    
    def list_ports(self) -> list[int]:
        return list(bank.ports.keys())

    def read_counters(self, port_id: int) -> PortCounters:
        return bank.read_counters(port_id)