from back.port.infrastructure.outbound.mock_register_bank import MockRegisterBank, PortCounters, bank
from back.port.infrastructure.outbound.mock_register_bank import PortCounters, bank
from back.port.application.IPortHardware import IPortHardware

class MockHardwareAdapter(IPortHardware):
    def __init__(self, bank: MockRegisterBank):
        # Recibimos el simulador por el constructor
        self.bank = bank

    def read_counters(self, port_id: int) -> PortCounters:
        """
        Este método cumple con el contrato de la Aplicación
        pero saca los datos de tu Mock.
        """
        # Llamamos al método read_counters que ya definiste en tu Mock
        return self.bank.read_counters(port_id)

    def list_ports(self) -> list[int]:
        # Si el servicio necesita saber cuántos puertos hay
        return list(range(self.bank.port_count))