import time
from dataclasses import dataclass, field
from typing import Dict
from unittest.mock import Mock


@dataclass(frozen=True)
class PortCounters:
    # RX
    rx_in_frames: int
    rx_out_frames: int
    rx_gen_frames: int
    rx_in_true_frames: int
    rx_gen_true_frames: int

    # TX
    tx_in_frames: int
    tx_out_frames: int
    tx_in_true_frames: int

    # Extra (si quieres ver el total gen)
    gen_frames: int


@dataclass
class PortState:
    # configuración (mock)
    rx_mux: str = "null"   # "null" | "mac" | "gen"
    tx_mux: str = "null"   # "null" | "mac"
    gen_enabled: bool = False
    length: int = 64
    counter: int = 1
    counter_frac: int = 0

    # contadores (mock)
    rx_in_frames: int = 0
    rx_out_frames: int = 0
    rx_gen_frames: int = 0
    rx_in_true_frames: int = 0
    rx_gen_true_frames: int = 0

    tx_in_frames: int = 0
    tx_out_frames: int = 0
    tx_in_true_frames: int = 0

    gen_frames: int = 0

    _last_tick: float = field(default_factory=time.time)


class MockRegisterBank:
    """
    Simula una FPGA con N puertos.
    Ofrece read(addr, length) y write(addr, value) como si fueran accesos a registros.
    """
    def __init__(self, port_count: int = 4):
        self.port_count = port_count
        self.ports: Dict[int, PortState] = {i: PortState() for i in range(port_count)}
    self.globals: Dict[str, int] = {"PORT_COUNT": port_count}

    def read(self, addr, length: int = 4):
        """
        addr puede ser:
          - ("GLOBAL", "PORT_COUNT")
          - (port_id, "RX_IN_FRAMES"), etc.
        """
        if isinstance(addr, tuple) and len(addr) == 2:
            scope, name = addr
            if scope == "GLOBAL":
                return self.globals.get(name, 0)

            port_id = scope
            p = self.ports[port_id]
            return getattr(p, name.lower(), 0)

        return 0

    def write(self, addr, value):
        """
        addr puede ser:
          - (port_id, "GEN_ENABLE") / (port_id, "RX_MUX"), etc.
        """
        if isinstance(addr, tuple) and len(addr) == 2:
            port_id, name = addr
            p = self.ports[port_id]

            name = name.upper()
            if name == "GEN_ENABLE":
                p.gen_enabled = bool(value)
                return
            if name == "RX_MUX":
                p.rx_mux = str(value)
                return
            if name == "TX_MUX":
                p.tx_mux = str(value)
                return
            if name == "LENGTH":
                p.length = int(value)
                return
            if name == "COUNTER":
                p.counter = max(1, int(value))
                return
            if name == "COUNTER_FRAC":
                p.counter_frac = int(value)
                return

        return

    def tick(self):
        """Simula el paso del tiempo e incrementa contadores si el generador está activo."""
        for p in self.ports.values():
            now = time.time()
            dt = now - p._last_tick
            p._last_tick = now

            if not p.gen_enabled:
                continue

            base_fps = 500
            fps = base_fps / max(1, p.counter)
            inc = int(fps * dt)
            if inc <= 0:
                continue

            p.gen_frames += inc

            p.rx_gen_frames += inc

            p.rx_gen_true_frames += inc
            p.tx_in_true_frames += inc

            if p.rx_mux == "gen":
                p.rx_in_frames += inc
                p.rx_out_frames += inc
                p.rx_in_true_frames += inc

            p.tx_in_frames += inc
            p.tx_out_frames += inc

    
    def read_counters(self, port_id: int) -> PortCounters:
        p = self.ports[port_id]
        return PortCounters(
            rx_in_frames=p.rx_in_frames,
            rx_out_frames=p.rx_out_frames,
            rx_gen_frames=p.rx_gen_frames,
            rx_in_true_frames=p.rx_in_true_frames,
            rx_gen_true_frames=p.rx_gen_true_frames,
            tx_in_frames=p.tx_in_frames,
            tx_out_frames=p.tx_out_frames,
            tx_in_true_frames=p.tx_in_true_frames,
            gen_frames=p.gen_frames,
        )


bank = MockRegisterBank(port_count=4)

read_func = Mock(side_effect=bank.read)
write_func = Mock(side_effect=bank.write)


if __name__ == "__main__":
    write_func((0, "RX_MUX"), "gen")
    write_func((0, "TX_MUX"), "mac")
    write_func((0, "GEN_ENABLE"), 1)
    write_func((0, "COUNTER"), 1)

    for _ in range(5):
        time.sleep(1)
        bank.tick()
        counters = bank.read_counters(0)
        print("Port0 counters:", counters)