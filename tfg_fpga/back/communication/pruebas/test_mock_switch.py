"""
test_mock_switch.py

Script de prueba para verificar que MockSwitchRegisters funciona
con EthernetSwitch y control_methods.
"""

import time
from mock_switch_registers import MockSwitchRegisters


def test_basic_read():
    """Prueba básica de lectura."""
    mock = MockSwitchRegisters(port_count=4)
    
    print("=== Prueba de lectura básica ===")
    
    rx_value = mock.read_func(0x10000008)
    print(f"RX frames puerto 0: {rx_value}")
    
    tx_value = mock.read_func(0x1000000C)
    print(f"TX frames puerto 0: {tx_value}")


def test_timed_read():
    """Prueba de lectura en tiempo real (los contadores suben)."""
    mock = MockSwitchRegisters(port_count=4)
    
    print("\n=== Prueba de lectura en tiempo real ===")
    
    print("Leyendo contador RX del puerto 0 cada segundo...")
    
    for i in range(5):
        rx_value = mock.read_func(0x10000008)
        print(f"  Lectura {i+1}: {rx_value}")
        mock.tick()
        time.sleep(1)


def test_control_methods():
    """Prueba con control_methods."""
    from control_methods import read_conf_reg_int
    
    mock = MockSwitchRegisters(port_count=4)
    
    print("\n=== Prueba con control_methods ===")
    
    value = read_conf_reg_int(
        read_func=mock.read_func,
        offset=0x10000000,
        address=0x08,
        length=4
    )
    print(f"Valor leído con control_methods: {value}")


if __name__ == "__main__":
    test_basic_read()
    test_timed_read()
    test_control_methods()
    print("\n¡Todas las pruebas pasaron!")
