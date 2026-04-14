
from back.port.domain.PortCounters import PortCounters
from back.port.application.IPortHardware import IPortHardware
from back.port.application.PortCountersRepository import PortCountersRepository

class PortCountersService:

    def __init__(self,hardware :IPortHardware, repository: PortCountersRepository):
        self.hardware=hardware
        self.repository = repository
    
    def get_ports(self)->list[int]:
        return self.hardware.get_ports()
    
    def get_counters(self, port_id: int) -> PortCounters:
        self._validate_port_id(port_id)
        counters = self.hardware.read_counters(port_id)
        self.repository.save(port_id, counters)
        return counters

    def configure_generator(
        self,
        port_id: int,
        enabled: bool,
        length: int,
        counter: int,
        counter_frac: int
    ) -> None:
        self._validate_port_id(port_id)
        if length <= 0:
            raise ValueError("length debe ser mayor que 0")
        if counter <= 0:
            raise ValueError("counter debe ser mayor que 0")

        self.hardware.set_generator(
            port_id=port_id,
            enabled=enabled,
            length=length,
            counter=counter,
            counter_frac=counter_frac,
        )

    def configure_mux(self, port_id: int, rx_mux: str | None = None, tx_mux: str | None = None) -> None:
        self._validate_port_id(port_id)
        allowed_rx = {"null", "mac", "gen"}
        allowed_tx = {"null", "mac"}

        if rx_mux is not None and rx_mux not in allowed_rx:
            raise ValueError(f"rx_mux inválido: {rx_mux}")
        if tx_mux is not None and tx_mux not in allowed_tx:
            raise ValueError(f"tx_mux inválido: {tx_mux}")

        self.hardware.set_mux(port_id=port_id, rx_mux=rx_mux, tx_mux=tx_mux)

    def _validate_port_id(self, port_id: int) -> None:
        if port_id not in self.hardware.get_ports():
            raise ValueError(f"Puerto no válido: {port_id}")
        
    def get_history(self, port_id: int, limit: int = 100):
     self._validate_port_id(port_id)
     return self.repository.get_history(port_id, limit)

    def get_latest(self, port_id: int):
     self._validate_port_id(port_id)
     return self.repository.get_latest(port_id)