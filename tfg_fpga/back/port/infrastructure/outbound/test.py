from back.port.infrastructure.outbound.mock_port_hardware_adapter import PortHardwareAdapter

import time

def main():
    hw = PortHardwareAdapter(port_count=4)

    print("PORTS:", hw.get_ports())
    print("ANTES:", hw.read_counters(0))

    hw.set_mux(0, rx_mux="gen", tx_mux="mac")
    hw.set_generator(0, enabled=True, length=128, counter=10, counter_frac=0)

    for i in range(5):
        time.sleep(1)
        print(f"LECTURA {i+1}:", hw.read_counters(0))

if __name__ == "__main__":
    main()