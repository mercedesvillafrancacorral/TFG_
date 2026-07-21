import math

from back.port.domain.PortCounters import PortCounters
from back.port.application.IPortHardware import IPortHardware
from back.port.application.PortCountersRepository import PortCountersRepository

class PortCountersService:

    def __init__(self,hardware :IPortHardware, repository: PortCountersRepository):
        self.hardware=hardware
        self.repository = repository
        self._generators: dict[int, dict[int, dict]] ={}
    
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
        self._follow_generator(port_id, target=0, enabled=enabled, length=length, counter=counter, counter_frac=counter_frac)

    def configure_generator_traffic(
        self,
        port_id: int,
        enabled: bool,
        length: int,
        counter: int,
        counter_frac: int,
        target: int,
        
    ) -> None:
        self._validate_port_id(port_id)
        if length <= 0:
            raise ValueError("length debe ser mayor que 0")
        if counter <= 0:
            raise ValueError("counter debe ser mayor que 0")

        self.hardware.set_generator_traffic(
            port_id=port_id,
            enabled=enabled,
            length=length,
            counter=counter,
            counter_frac=counter_frac,
            target=target
        )
        self._follow_generator(port_id, target=target, enabled=enabled, length=length, counter=counter, counter_frac=counter_frac)
    def configure_generator_bandwidth(
        self,
        port_id: int,
        enabled: bool,
        bandwidth_gbps: float,
        length: int,
        target: int,
    ) -> tuple[int, int]:
        self._validate_port_id(port_id)

        if length <= 0:
            raise ValueError("length debe ser mayor que 0")

        if bandwidth_gbps <= 0:
            raise ValueError("bandwidth_gbps debe ser mayor que 0")

        if not 0 <= target < 10:
            raise ValueError("target debe ser un número entre 0 y 9")

        clk_freq = self.hardware.get_clk_freq(port_id)
        frac_width = self.hardware.get_counter_frac_width(port_id)
        counter, counter_frac = self.calculate_bandwidth_params(
            clk_freq=clk_freq,
            bandwidth_gbps=bandwidth_gbps,
            frame_length=length,
            frac_width=frac_width,
        )

        self.hardware.set_generator_traffic(
            port_id=port_id,
            enabled=enabled,
            length=length,
            counter=counter,
            counter_frac=counter_frac,
            target=target,
        )
        self._follow_generator(port_id, target=target, enabled=enabled, length=length, counter=counter, counter_frac=counter_frac, bandwidth_gbps=bandwidth_gbps)

        return counter, counter_frac
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

    def _follow_generator(
        self,
        port_id: int,
        target: int,
        enabled: bool,
        length: int,
        counter: int,
        counter_frac: int,
        bandwidth_gbps: float | None = None,
    ) -> None:
        port_generators = self._generators.setdefault(port_id, {})
        if enabled:
            entry = {"target": target, "length": length, "counter": counter, "counter_frac": counter_frac}
            if bandwidth_gbps is not None:
                entry["bandwidth_gbps"] = bandwidth_gbps
            port_generators[target] = entry
        else:
            port_generators.pop(target, None)
                   
    
        
    def get_history(self, port_id: int, limit: int = 100):
     self._validate_port_id(port_id)
     return self.repository.get_history(port_id, limit)

    def get_latest(self, port_id: int):
     self._validate_port_id(port_id)
     return self.repository.get_latest(port_id)

    
    def calculate_bandwidth_params(
        self, clk_freq: float, bandwidth_gbps: float, frame_length: int, frac_width: int
    ) -> tuple[int, int]:
        bandwidth_bps = bandwidth_gbps * 1e9
        counter = clk_freq * frame_length * 8 / bandwidth_bps
        counter_ach = math.ceil(counter)
        counter_debt = counter_ach - counter
        counter_frac = math.floor(((2 ** frac_width - 1) / counter) * counter_debt)
        return counter_ach, counter_frac
    
    def get_generator_info(
        self,
        port_id: int
    ) -> list [dict]:
        self._validate_port_id(port_id)
        return list(self._generators.get(port_id, {}).values())