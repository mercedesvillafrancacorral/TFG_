"""
test_ethernet_switch.py

Prueba completa: conecta MockSwitchRegisters con EthernetSwitch
"""

import sys
import os
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

sys.path.insert(0, os.path.join(project_root, 'lib', 'xfcp', 'python'))

from communication.mock_switch_registers import MockSwitchRegisters
from communication.ethernet_switch import EthernetSwitch



def main():
    print("=== Creando MockSwitchRegisters ===")
    mock = MockSwitchRegisters(port_count=4)
    print(f"Mock creado con {mock._port_count} puertos")
    
    print("\n=== Creando EthernetSwitch ===")
    switch = EthernetSwitch(
        read_func=mock.read_func,
        write_func=mock.write_func,
        offset=0x0,
        vc_count={0: 4},
        fcl_x_ch_count={0: 1},
        fcl_offset=0x1000,
        fcl_stride=0x10000000,
        prio_count=1,
        drop_corrupted_frames=1,
        egress_pipeline_register=1,
        ingress_fifo_depth=32,
        egress_fifo_depth=16
    )
    
    print("\n=== Inicializando Switch ===")
    switch.initialize()
    print(f"Switch inicializado")
    print(f"  - CH_COUNT: {switch.CH_COUNT}")
    print(f"  - PORT_COUNT: {switch.PORT_COUNT}")
    print(f"  - FCL_COUNT: {switch.FCL_COUNT}")
    
    print("\n=== Descubriendo puertos ===")
    switch.discover_port_modules(
        port_offset=0x10000000,
        port_stride=0x100,
        port_count=4,
        port_id_offset=0
    )
    print(f"Puertos descubiertos: {list(switch.port_dict.keys())}")
    
    for port_id in switch.port_dict:
        port = switch.port_dict[port_id]
        print(f"  Puerto {port_id}:")
        print(f"    - PORT_ID: {port.PORT_ID}")
        print(f"    - PORT_RATE: {port.PORT_RATE}")
        print(f"    - FEATURES: {port.FEATURES}")
    
    print("\n=== Leyendo contadores en tiempo real ===")
    print("Puerto 0 - RX frames cada segundo:")
    
    for i in range(5):
        rx_count = switch.port_dict[0].get_rx_port_in_frame_counter()
        tx_count = switch.port_dict[0].get_tx_port_out_frame_counter()
        print(f"  Lectura {i+1}: RX={rx_count}, TX={tx_count}")
        mock.tick()
        time.sleep(1)
    
    print("\n¡Prueba completada con exito!")


if __name__ == "__main__":
    main()
