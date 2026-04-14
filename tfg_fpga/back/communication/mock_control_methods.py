# mock_control_methods.py
from __future__ import annotations
from back.port.infrastructure.outbound.mock_register_bank import bank

from back.communication.control_registers import (
    RB_PORT_ID,
    RB_PORT_RATE,
    RB_PORT_FEATURES,
    RB_PORT_RX_VALID,
    RB_PORT_GEN_TRAFFIC_COMMON_COUNT,
    RB_PORT_GEN_COUNTER_WIDTH,
    RB_PORT_GEN_COUNTER_FRAC_WIDTH,
    RB_PORT_GEN_MIN_FRAME_LENGTH,
    RB_PORT_READ_WIDTH,
    RB_PORT_FEATURE_RX_TRAFFIC_ENABLE,
    RB_PORT_FEATURE_TX_TRAFFIC_ENABLE,
    RB_PORT_FEATURE_GEN_TRAFFIC_ENABLE,
    RB_PORT_FEATURE_GEN_OUTPUT_REGISTER,
    RB_PORT_RX_PORT_OUT_FRAME_COUNTER,
    RB_PORT_RX_PORT_IN_FRAME_COUNTER,
    RB_PORT_RX_PORT_GEN_FRAME_COUNTER,
    RB_PORT_RX_PORT_IN_TRUE_FRAME_COUNTER,
    RB_PORT_RX_PORT_GEN_TRUE_FRAME_COUNTER,
    RB_PORT_TX_PORT_OUT_FRAME_COUNTER,
    RB_PORT_TX_PORT_IN_FRAME_COUNTER,
    RB_PORT_TX_PORT_IN_TRUE_FRAME_COUNTER,
)



# Ajusta esto si más adelante descubres otro stride real
PORT_STRIDE = 0x100


def _offset_to_port_id(offset: int) -> int:
    """
    Convierte el offset del módulo Port al port_id del mock.
    Ejemplos:
      0x000 -> 0
      0x100 -> 1
      0x200 -> 2
    """
    if offset < 0:
        raise ValueError(f"Offset inválido: {offset}")
    return offset // PORT_STRIDE


def _get_port_state(port_id: int):
    if port_id not in bank.ports:
        raise KeyError(f"Puerto {port_id} no existe en MockRegisterBank")
    return bank.ports[port_id]


def _default_port_features() -> int:
    return (
        RB_PORT_FEATURE_RX_TRAFFIC_ENABLE
        | RB_PORT_FEATURE_TX_TRAFFIC_ENABLE
        | RB_PORT_FEATURE_GEN_TRAFFIC_ENABLE
        | RB_PORT_FEATURE_GEN_OUTPUT_REGISTER
    )


def _read_port_arch_reg(port_id: int, address: int) -> int:
    """
    Devuelve registros "arquitectónicos" fijos o casi fijos que Port.initialize() espera.
    """
    if address == RB_PORT_ID:
        return port_id

    if address == RB_PORT_RATE:
        # Mbps simulados; cambia esto si quieres otra cifra
        return 10000

    if address == RB_PORT_FEATURES:
        return _default_port_features()

    if address == RB_PORT_RX_VALID:
        return 1

    if address == RB_PORT_GEN_TRAFFIC_COMMON_COUNT:
        # Tu mock actual no modela múltiples "targets", así que 1 encaja bien
        return 1

    if address == RB_PORT_GEN_COUNTER_WIDTH:
        return 16

    if address == RB_PORT_GEN_COUNTER_FRAC_WIDTH:
        return 8

    if address == RB_PORT_GEN_MIN_FRAME_LENGTH:
        return 64

    if address == RB_PORT_READ_WIDTH:
        return 32

    return 0


def _read_rx_counter(port_id: int, field_addr: int) -> int:
    p = _get_port_state(port_id)

    if field_addr == RB_PORT_RX_PORT_OUT_FRAME_COUNTER:
        return p.rx_out_frames
    if field_addr == RB_PORT_RX_PORT_IN_FRAME_COUNTER:
        return p.rx_in_frames
    if field_addr == RB_PORT_RX_PORT_GEN_FRAME_COUNTER:
        return p.rx_gen_frames
    if field_addr == RB_PORT_RX_PORT_IN_TRUE_FRAME_COUNTER:
        return p.rx_in_true_frames
    if field_addr == RB_PORT_RX_PORT_GEN_TRUE_FRAME_COUNTER:
        return p.rx_gen_true_frames

    return 0


def _read_tx_counter(port_id: int, field_addr: int) -> int:
    p = _get_port_state(port_id)

    if field_addr == RB_PORT_TX_PORT_OUT_FRAME_COUNTER:
        return p.tx_out_frames
    if field_addr == RB_PORT_TX_PORT_IN_FRAME_COUNTER:
        return p.tx_in_frames
    if field_addr == RB_PORT_TX_PORT_IN_TRUE_FRAME_COUNTER:
        return p.tx_in_true_frames

    return 0


def read_conf_reg_int(read_func, offset: int, address: int, length: int = 4) -> int:
    """
    Compatibilidad mínima con ethernet_switch.Port.
    Ignoramos read_func porque el backend real del mock es bank.
    """
    del read_func, length

    port_id = _offset_to_port_id(offset)
    return _read_port_arch_reg(port_id, address)


def write_conf_reg_int(write_func, offset: int, address: int, data: int) -> None:
    """
    Escritura genérica mínima.
    Port apenas la usa de forma directa en el trozo que nos interesa,
    pero dejamos soporte básico para parámetros simples.
    """
    del write_func

    port_id = _offset_to_port_id(offset)

    # Solo mapeamos lo que tenga sentido en el mock actual
    if address == RB_PORT_GEN_MIN_FRAME_LENGTH:
        bank.write((port_id, "LENGTH"), int(data))
        return

    # Si más adelante quieres soportar más escrituras genéricas, añádelas aquí.
    return


def write_port_rx_mux(write_func, offset: int, value: int, write_width: int) -> None:
    del write_func, write_width

    port_id = _offset_to_port_id(offset)

    mux_map = {
        0: "null",
        1: "mac",
        2: "gen",
    }

    mux = mux_map.get(value)
    if mux is None:
        raise ValueError(f"Valor RX mux no soportado: {value}")

    bank.write((port_id, "RX_MUX"), mux)


def write_port_tx_mux(write_func, offset: int, value: int, write_width: int) -> None:
    del write_func, write_width

    port_id = _offset_to_port_id(offset)

    mux_map = {
        0: "null",
        1: "mac",
    }

    mux = mux_map.get(value)
    if mux is None:
        raise ValueError(f"Valor TX mux no soportado: {value}")

    bank.write((port_id, "TX_MUX"), mux)


def write_port_rx_gen_common_counter(
    read_func,
    write_func,
    offset: int,
    target: int,
    target_width: int,
    enable: int,
    counter: int,
    counter_width: int,
    counter_frac: int,
    counter_frac_width: int,
    length: int,
    length_width: int,
    common_type: int,
    common_type_width: int,
    vlan_enable: int,
    destination_mac_address: int,
    source_mac_address: int,
    vlan_id: int,
    vlan_pcp: int,
    vlan_dei: int,
    ether_type: int,
) -> None:
    """
    Implementación mínima compatible con Port.set_rx_gen_common_counter(...)

    En el mock actual:
    - ignoramos target y campos Ethernet/VLAN
    - guardamos enable, counter, counter_frac y length
    """
    del (
        read_func,
        write_func,
        target,
        target_width,
        counter_width,
        counter_frac_width,
        length_width,
        common_type,
        common_type_width,
        vlan_enable,
        destination_mac_address,
        source_mac_address,
        vlan_id,
        vlan_pcp,
        vlan_dei,
        ether_type,
    )

    port_id = _offset_to_port_id(offset)

    bank.write((port_id, "GEN_ENABLE"), 1 if enable else 0)
    bank.write((port_id, "COUNTER"), int(counter))
    bank.write((port_id, "COUNTER_FRAC"), int(counter_frac))
    bank.write((port_id, "LENGTH"), int(length))


def read_port_rx_counter(write_func, read_func, offset: int, field_addr: int, read_width: int) -> int:
    del write_func, read_func, read_width

    port_id = _offset_to_port_id(offset)
    return _read_rx_counter(port_id, field_addr)


def read_port_tx_counter(write_func, read_func, offset: int, field_addr: int, read_width: int) -> int:
    del write_func, read_func, read_width

    port_id = _offset_to_port_id(offset)
    return _read_tx_counter(port_id, field_addr)