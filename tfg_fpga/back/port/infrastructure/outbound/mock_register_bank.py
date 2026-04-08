import time
import threading
from dataclasses import dataclass, field
from typing import Dict
from unittest.mock import Mock
from back.port.domain.PortCounters import PortCounters

@dataclass
class PortState:
    """Estado interno del Simulador para cada puerto."""

    rx_mux: str = "null"  # "null" | "mac" | "gen"
    tx_mux: str = "null"  # "null" | "mac"
    gen_enabled: bool = False
    length: int = 64
    counter: int = 1
    counter_frac: int = 0

    # Contadores acumulados
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
    Simula una FPGA con N puertos que genera datos de forma autónoma.
    """

    def __init__(self, port_count: int = 4, auto_start: bool = True):
        self.port_count = port_count
        self.ports: Dict[int, PortState] = {i: PortState() for i in range(port_count)}
        self.globals: Dict[str, int] = {"PORT_COUNT": port_count}

        # --- MOTOR AUTÓNOMO ---
        if auto_start:
            # Activamos el puerto 0 por defecto para que haya tráfico inmediato
            self.write((0, "RX_MUX"), "gen")
            self.write((0, "GEN_ENABLE"), 1)

            # Lanzamos el hilo que hace los 'ticks' en segundo plano
            self._thread = threading.Thread(target=self._auto_tick_worker, daemon=True)
            self._thread.start()

    def _auto_tick_worker(self):
        """Bucle que corre en segundo plano simulando el paso del tiempo."""
        while True:
            self.tick()
            time.sleep(0.5)  # Actualiza cada medio segundo para mayor fluidez

    def read(self, addr, length: int = 4):
        """Lectura simulada de registros."""
        if isinstance(addr, tuple) and len(addr) == 2:
            scope, name = addr
            if scope == "GLOBAL":
                return self.globals.get(name, 0)

            port_id = scope
            p = self.ports[port_id]
            return getattr(p, name.lower(), 0)
        return 0

    def write(self, addr, value):
        """Escritura simulada de registros."""
        if isinstance(addr, tuple) and len(addr) == 2:
            port_id, name = addr
            p = self.ports[port_id]

            name = name.upper()
            if name == "GEN_ENABLE":
                p.gen_enabled = bool(value)
            elif name == "RX_MUX":
                p.rx_mux = str(value)
            elif name == "TX_MUX":
                p.tx_mux = str(value)
            elif name == "LENGTH":
                p.length = int(value)
            elif name == "COUNTER":
                p.counter = max(1, int(value))
            elif name == "COUNTER_FRAC":
                p.counter_frac = int(value)

    def tick(self):
        """Lógica matemática que incrementa los contadores según el tiempo transcurrido."""
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

            # Incrementos de contadores
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
        """Devuelve una foto fija de los contadores actuales del puerto."""
        portCounter = self.ports[port_id]
        return PortCounters(
            rx_port_in_frames=portCounter.rx_in_frames,
            rx_port_out_frames=portCounter.rx_out_frames,
            rx_port_gen_frames=portCounter.rx_gen_frames,
            rx_port_in_true_frames=portCounter.rx_in_true_frames,
            rx_port_gen_true_frames=portCounter.rx_gen_true_frames,
            tx_port_in_frames=portCounter.tx_in_frames,
            tx_port_out_frames=portCounter.tx_out_frames,
            tx_port_in_true_frames=portCounter.tx_in_true_frames,
            gen_frames=portCounter.gen_frames,
        )


# Instancia global para que al importar este archivo ya tengas una "FPGA" lista
bank = MockRegisterBank(port_count=4)

# Mocks para compatibilidad con código que use funciones de lectura/escritura directas
read_func = Mock(side_effect=bank.read)
write_func = Mock(side_effect=bank.write)


