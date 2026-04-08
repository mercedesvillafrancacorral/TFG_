from back.port.infrastructure.outbound.mock_register_bank import MockRegisterBank, bank
from back.port.application.IPortHardware import IPortHardware
from back.port.domain.PortCounters import PortCounters
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

    def get_ports(self) -> list[int]:
        # Si el servicio necesita saber cuántos puertos hay
        return list(range(self.bank.port_count))
    
    def set_generator(
        self,
        port_id: int,
        enabled: bool,
        length: int,
        counter: int,
        counter_frac: int
    ) -> None:
        self.bank.write((port_id, "GEN_ENABLE"), 1 if enabled else 0)
        self.bank.write((port_id, "LENGTH"), length)
        self.bank.write((port_id, "COUNTER"), counter)
        self.bank.write((port_id, "COUNTER_FRAC"), counter_frac)

    def set_mux(self, port_id: int, rx_mux: str | None = None, tx_mux: str | None = None) -> None:
        if rx_mux is not None:
            self.bank.write((port_id, "RX_MUX"), rx_mux)
        if tx_mux is not None:
            self.bank.write((port_id, "TX_MUX"), tx_mux)