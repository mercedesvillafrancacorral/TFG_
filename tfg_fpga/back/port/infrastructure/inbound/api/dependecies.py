from back.port.infrastructure.outbound.mock_register_bank import MockRegisterBank
from back.port.infrastructure.outbound.MockHardwareAdapter import MockHardwareAdapter
from back.port.application.PortCountersService import PortCountersService

# Instancia única compartida del simulador
bank = MockRegisterBank(port_count=4, auto_start=True)

# Adaptador concreto que implementa IPortHardware
hardware = MockHardwareAdapter(bank)

# Servicio de aplicación
service = PortCountersService(hardware)

def get_port_service() -> PortCountersService:
    return service