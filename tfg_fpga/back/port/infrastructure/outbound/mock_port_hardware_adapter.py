from back.port.application.IPortHardware import IPortHardware
from back.port.domain.PortCounters import PortCounters
from back.communication.ethernet_switch import Port
from back.port.infrastructure.outbound.mock_register_bank import read_func, write_func


class PortHardwareAdapter(IPortHardware):
    RX_MULTIPLEXOR_NULL = "null"
    RX_MULTIPLEXOR_MAC = "mac"
    RX_MULTIPLEXOR_GENERATOR = "gen"
    TX_MULTIPLEXOR_NULL = "null"
    TX_MULTIPLEXOR_MAC = "mac"

    def __init__(self, port_count: int = 4, port_stride: int = 0x100):
        self.port_count = port_count
        self.port_stride = port_stride
        self.ports: dict[int, Port] = {}

        for port_id in range(port_count):
            offset = port_id * self.port_stride
            port = Port(read_func=read_func, write_func=write_func, offset=offset)
            port.initialize()
            self.ports[port_id] = port

    def get_ports(self) -> list[int]:
        return list(self.ports.keys())

    def read_counters(self, port_id: int) -> PortCounters:
        port = self.ports[port_id]
        return PortCounters(
            rx_port_in_frames=port.get_rx_port_in_frame_counter(),
            rx_port_out_frames=port.get_rx_port_out_frame_counter(),
            rx_port_gen_frames=port.get_rx_port_gen_frame_counter(),
            rx_port_in_true_frames=port.get_rx_port_in_true_frame_counter(),
            rx_port_gen_true_frames=port.get_rx_port_gen_true_frame_counter(),
            tx_port_in_frames=port.get_tx_port_in_frame_counter(),
            tx_port_out_frames=port.get_tx_port_out_frame_counter(),
            tx_port_in_true_frames=port.get_tx_port_in_true_frame_counter(),
        
        )

    def set_generator(
        self,
        port_id: int,
        enabled: bool,
        length: int,
        counter: int,
        counter_frac: int
    ) -> None:
        port = self.ports[port_id]

        if enabled:
            port.create_rx_gen_common_counter(
                counter=counter,
                counter_frac=counter_frac,
                length=length,
            )
        else:
            port.delete_rx_gen_common_counter()

    def set_mux(
        self,
        port_id: int,
        rx_mux: str | None = None,
        tx_mux: str | None = None
    ) -> None:
        port = self.ports[port_id]

        if rx_mux == self.RX_MULTIPLEXOR_NULL:
            port.set_rx_null_mux()
        elif rx_mux == self.RX_MULTIPLEXOR_MAC:
            port.set_rx_mac_mux()
        elif rx_mux == self.RX_MULTIPLEXOR_GENERATOR:
            port.set_rx_gen_mux()
        elif rx_mux is not None:
         raise ValueError(f" rx_mux value no válido: {rx_mux}")

        if tx_mux == self.TX_MULTIPLEXOR_NULL:
            port.set_tx_null_mux()
        elif tx_mux == self.TX_MULTIPLEXOR_MAC:
            port.set_tx_mac_mux()
        elif tx_mux is not None:
         raise ValueError(f" tx_mux value no válido: {tx_mux}")