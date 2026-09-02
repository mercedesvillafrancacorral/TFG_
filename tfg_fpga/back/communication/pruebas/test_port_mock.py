from back.communication.ethernet_switch import Port
from back.port.infrastructure.outbound.mock_register_bank import read_func, write_func


def main():
    port0 = Port(read_func=read_func, write_func=write_func, offset=0x0)
    port0.initialize()

    print("PARAMS:")
    print(port0.get_parameters())

    port0.set_rx_gen_mux()
    port0.set_tx_mac_mux()
    port0.create_rx_gen_common_counter(counter=10, counter_frac=0, length=128)

    print("RX IN:", port0.get_rx_port_in_frame_counter())
    print("RX GEN:", port0.get_rx_port_gen_frame_counter())
    print("TX OUT:", port0.get_tx_port_out_frame_counter())


if __name__ == "__main__":
    main()