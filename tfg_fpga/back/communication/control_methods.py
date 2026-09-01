"""
control_methods.py - Capa de acceso a registros de la FPGA

Este módulo proporciona funciones para leer y escribir registros en la FPGA.
Acepta:
- read_func/write_func: funciones directas (compatible con ethernet_switch.py)
- transport: objeto con método request() (para mock/serial transport)
"""

from typing import Optional, Callable
from transport import Transport
from control_registers import *


def read_conf_reg_int(
    read_func: Optional[Callable] = None,
    offset: int = 0,
    address: int = 0,
    length: int = 4,
    write_func: Optional[Callable] = None,
    transport: Optional[Transport] = None,
) -> int:
    """
    Lee un registro de configuración de la FPGA.
    
    Args:
        read_func: Función de lectura directa (addr, length) -> value
        offset: Offset base del módulo
        address: Dirección del registro
        length: Longitud en bytes (default 4)
        write_func: Función de escritura (no usada aquí, para compatibilidad)
        transport: Transport con método request()
    
    Returns:
        Valor del registro leído
    """
    addr = offset + address
    
    if read_func is not None:
        return read_func(addr, length)
    
    if transport is not None:
        payload = bytes([0x01]) + addr.to_bytes(4, "little") + length.to_bytes(4, "little")
        response = transport.request(payload)
        if len(response) >= 5:
            return int.from_bytes(response[1:5], "little")
    
    return 0


def write_conf_reg_int(
    write_func: Optional[Callable] = None,
    offset: int = 0,
    address: int = 0,
    data: int = 0,
    read_func: Optional[Callable] = None,
    transport: Optional[Transport] = None,
) -> None:
    """
    Escribe un registro de configuración en la FPGA.
    
    Args:
        write_func: Función de escritura directa (addr, value)
        offset: Offset base del módulo
        address: Dirección del registro
        data: Valor a escribir
        read_func: Función de lectura (no usada aquí)
        transport: Transport con método request()
    """
    addr = offset + address
    
    if write_func is not None:
        write_func(addr, data)
        return
    
    if transport is not None:
        payload = bytes([0x02]) + addr.to_bytes(4, "little") + data.to_bytes(4, "little")
        transport.request(payload)


def read_conf_reg_list(
    read_func: Optional[Callable] = None,
    write_func: Optional[Callable] = None,
    transport: Optional[Transport] = None,
    offset: int = 0,
    address: int = 0,
    length: int = 4,
    count: int = 8,
    bits_width: int = 1
) -> list:
    """
    Lee una lista de registros de configuración.
    
    Args:
        read_func: Función de lectura directa
        write_func: Función de escritura (no usada aquí)
        transport: Transport con método request()
        offset: Offset base del módulo
        address: Dirección inicial
        length: Longitud en bytes
        count: Número de elementos
        bits_width: Ancho de bits por elemento
    
    Returns:
        Lista de valores leídos
    """
    results = []
    for i in range(count):
        value = read_conf_reg_int(
            read_func=read_func,
            write_func=write_func,
            transport=transport,
            offset=offset,
            address=address + i * (length // count),
            length=length // count
        )
        results.append(value)
    return results


def write_conf_reg_list(
    read_func: Optional[Callable] = None,
    write_func: Optional[Callable] = None,
    transport: Optional[Transport] = None,
    offset: int = 0,
    address: int = 0,
    data: Optional[list] = None,
    bits_width: int = 1
) -> None:
    """
    Escribe una lista de registros de configuración.
    
    Args:
        read_func: Función de lectura (no usada aquí)
        write_func: Función de escritura directa
        transport: Transport con método request()
        offset: Offset base del módulo
        address: Dirección inicial
        data: Lista de valores a escribir
        bits_width: Ancho de bits por elemento
    """
    if data is None:
        data = [0] * 8
    for i, value in enumerate(data):
        write_conf_reg_int(
            read_func=read_func,
            write_func=write_func,
            transport=transport,
            offset=offset,
            address=address + i * 4,
            data=value
        )


def read_port_rx_counter(
    read_func: Optional[Callable] = None,
    write_func: Optional[Callable] = None,
    transport: Optional[Transport] = None,
    offset: int = 0,
    field_addr: int = 0,
    read_width: int = 0
) -> int:
    """
    Lee un contador RX de un puerto.
    
    Args:
        read_func: Función de lectura directa
        write_func: Función de escritura (no usada)
        transport: Transport con método request()
        offset: Offset del puerto
        field_addr: Dirección del campo contador
        read_width: Ancho de lectura
    
    Returns:
        Valor del contador
    """
    return read_conf_reg_int(
        read_func=read_func,
        write_func=write_func,
        transport=transport,
        offset=offset,
        address=field_addr,
        length=4
    )


def read_port_tx_counter(
    read_func: Optional[Callable] = None,
    write_func: Optional[Callable] = None,
    transport: Optional[Transport] = None,
    offset: int = 0,
    field_addr: int = 0,
    read_width: int = 0
) -> int:
    """
    Lee un contador TX de un puerto.
    
    Args:
        read_func: Función de lectura directa
        write_func: Función de escritura (no usada)
        transport: Transport con método request()
        offset: Offset del puerto
        field_addr: Dirección del campo contador
        read_width: Ancho de lectura
    
    Returns:
        Valor del contador
    """
    return read_conf_reg_int(
        read_func=read_func,
        write_func=write_func,
        transport=transport,
        offset=offset,
        address=field_addr,
        length=4
    )


def write_port_rx_mux(
    read_func: Optional[Callable] = None,
    write_func: Optional[Callable] = None,
    transport: Optional[Transport] = None,
    offset: int = 0,
    value: int = 0,
    write_width: int = 0
) -> None:
    """
    Escribe el MUX RX de un puerto.
    
    Args:
        read_func: Función de lectura (no usada)
        write_func: Función de escritura directa
        transport: Transport con método request()
        offset: Offset del puerto
        value: Valor del MUX (0=null, 1=mac, 2=gen)
        write_width: Ancho de escritura
    """
    from control_registers import RB_PORT_WRITE_DATA
    write_conf_reg_int(
        read_func=read_func,
        write_func=write_func,
        transport=transport,
        offset=offset,
        address=RB_PORT_WRITE_DATA,
        data=value
    )


def write_port_tx_mux(
    read_func: Optional[Callable] = None,
    write_func: Optional[Callable] = None,
    transport: Optional[Transport] = None,
    offset: int = 0,
    value: int = 0,
    write_width: int = 0
) -> None:
    """
    Escribe el MUX TX de un puerto.
    
    Args:
        read_func: Función de lectura (no usada)
        write_func: Función de escritura directa
        transport: Transport con método request()
        offset: Offset del puerto
        value: Valor del MUX (0=null, 1=mac)
        write_width: Ancho de escritura
    """
    from control_registers import RB_PORT_WRITE_DATA
    write_conf_reg_int(
        read_func=read_func,
        write_func=write_func,
        transport=transport,
        offset=offset,
        address=RB_PORT_WRITE_DATA,
        data=value
    )


def write_port_rx_gen_common_counter(
    read_func: Optional[Callable] = None,
    write_func: Optional[Callable] = None,
    transport: Optional[Transport] = None,
    offset: int = 0,
    target: int = 0,
    target_width: int = 0,
    enable: int = 1,
    counter: int = 100,
    counter_width: int = 32,
    counter_frac: int = 0,
    counter_frac_width: int = 0,
    length: int = 64,
    length_width: int = 16,
    common_type: int = 0,
    common_type_width: int = 1,
    vlan_enable: int = 0,
    destination_mac_address: int = 0,
    source_mac_address: int = 0,
    vlan_id: int = 1,
    vlan_pcp: int = 0,
    vlan_dei: int = 0,
    ether_type: int = 1
) -> None:
    """
    Configura el generador de tráfico RX de un puerto.
    """
    from control_registers import RB_PORT_WRITE_DATA
    
    word = 0
    shift = 0
    
    word |= (target & ((1 << target_width) - 1)) << shift
    shift += target_width
    
    word |= (enable & 1) << shift
    shift += 1
    
    word |= (counter & ((1 << counter_width) - 1)) << shift
    shift += counter_width
    
    word |= (counter_frac & ((1 << counter_frac_width) - 1)) << shift
    shift += counter_frac_width
    
    word |= (length & ((1 << length_width) - 1)) << shift
    shift += length_width
    
    word |= (common_type & ((1 << common_type_width) - 1)) << shift
    shift += common_type_width
    
    write_conf_reg_int(
        write_func=write_func,
        offset=offset,
        address=RB_PORT_WRITE_DATA,
        data=word,
        read_func=read_func,
        transport=transport
    )


def write_vlan_association(
    read_func: Optional[Callable] = None,
    write_func: Optional[Callable] = None,
    transport: Optional[Transport] = None,
    offset: int = 0,
    vlan_id: int = 1,
    dest_dict: Optional[dict] = None,
    active: int = 1,
    vc_global_count: Optional[dict] = None
) -> None:
    """
    Crea o elimina una asociación VLAN.
    """
    from control_registers import RB_FCL_STATIC_WRITE_DATA
    
    if dest_dict is None:
        dest_dict = {}
    if vc_global_count is None:
        vc_global_count = {0: 4}
    
    word = vlan_id & 0xFFF
    word |= (active & 1) << 12
    
    bit_pos = 13
    for ch in range(len(vc_global_count)):
        vcs = dest_dict.get(ch, [])
        for vc in range(vc_global_count.get(ch, 1)):
            if vc in vcs:
                word |= (1 << bit_pos)
            bit_pos += 1
    
    write_conf_reg_int(
        read_func=read_func,
        write_func=write_func,
        transport=transport,
        offset=offset,
        address=RB_FCL_STATIC_WRITE_DATA,
        data=word
    )


def write_vlan_fid_association(
    read_func: Optional[Callable] = None,
    write_func: Optional[Callable] = None,
    transport: Optional[Transport] = None,
    offset: int = 0,
    fid: int = 1,
    vlan_id: int = 1,
    fid_width: int = 12
) -> None:
    """
    Establece la asociación VID a FID.
    """
    from control_registers import RB_FCL_STATIC_WRITE_DATA
    
    word = (fid & ((1 << fid_width) - 1)) | ((vlan_id & 0xFFF) << fid_width)
    write_conf_reg_int(
        read_func=read_func,
        write_func=write_func,
        transport=transport,
        offset=offset,
        address=RB_FCL_STATIC_WRITE_DATA,
        data=word
    )


def write_address_association_shared(
    read_func: Optional[Callable] = None,
    write_func: Optional[Callable] = None,
    transport: Optional[Transport] = None,
    offset: int = 0,
    mac_address: int = 0,
    dest_dict: Optional[dict] = None,
    prio: int = 0,
    active: int = 1,
    vc_global_count: Optional[dict] = None,
    prio_enable: int = 0,
    prio_width: int = 1
) -> None:
    """
    Crea/elimina una dirección MAC (tipo shared).
    """
    from control_registers import RB_FCL_STATIC_WRITE_DATA
    
    if dest_dict is None:
        dest_dict = {}
    if vc_global_count is None:
        vc_global_count = {0: 4}
    
    word = mac_address & 0xFFFFFFFFFFFF
    word |= (active & 1) << 48
    
    bit_pos = 49
    for ch in range(len(vc_global_count)):
        vcs = dest_dict.get(ch, [])
        for vc in range(vc_global_count.get(ch, 1)):
            if vc in vcs:
                word |= (1 << bit_pos)
            bit_pos += 1
    
    if prio_enable:
        word |= (prio & ((1 << prio_width) - 1)) << bit_pos
    
    write_conf_reg_int(
        write_func=write_func,
        offset=offset,
        address=RB_FCL_STATIC_WRITE_DATA,
        data=word,
        read_func=read_func,
        transport=transport
    )


def write_address_association_independent(
    read_func: Optional[Callable] = None,
    write_func: Optional[Callable] = None,
    transport: Optional[Transport] = None,
    offset: int = 0,
    mac_address: int = 0,
    vlan_id: int = 1,
    dest_dict: Optional[dict] = None,
    prio: int = 0,
    active: int = 1,
    vc_global_count: Optional[dict] = None,
    prio_enable: int = 0,
    prio_width: int = 1
) -> None:
    """
    Crea/elimina una dirección MAC (tipo independent).
    """
    from control_registers import RB_FCL_STATIC_WRITE_DATA
    
    if dest_dict is None:
        dest_dict = {}
    if vc_global_count is None:
        vc_global_count = {0: 4}
    
    word = mac_address & 0xFFFFFFFFFFFF
    word |= (vlan_id & 0xFFF) << 48
    word |= (active & 1) << 60
    
    bit_pos = 61
    for ch in range(len(vc_global_count)):
        vcs = dest_dict.get(ch, [])
        for vc in range(vc_global_count.get(ch, 1)):
            if vc in vcs:
                word |= (1 << bit_pos)
            bit_pos += 1
    
    if prio_enable:
        word |= (prio & ((1 << prio_width) - 1)) << bit_pos
    
    write_conf_reg_int(
        read_func=read_func,
        write_func=write_func,
        transport=transport,
        offset=offset,
        address=RB_FCL_STATIC_WRITE_DATA,
        data=word
    )


def write_address_association_mixed(
    read_func: Optional[Callable] = None,
    write_func: Optional[Callable] = None,
    transport: Optional[Transport] = None,
    offset: int = 0,
    mac_address: int = 0,
    vlan_id: int = 1,
    vlan_id_width: int = 12,
    dest_dict: Optional[dict] = None,
    prio: int = 0,
    active: int = 1,
    vc_global_count: Optional[dict] = None,
    prio_enable: int = 0,
    prio_width: int = 1
) -> None:
    """
    Crea/elimina una dirección MAC (tipo mixed).
    """
    from control_registers import RB_FCL_STATIC_WRITE_DATA
    
    if dest_dict is None:
        dest_dict = {}
    if vc_global_count is None:
        vc_global_count = {0: 4}
    
    word = mac_address & 0xFFFFFFFFFFFF
    word |= (vlan_id & ((1 << vlan_id_width) - 1)) << 48
    word |= (active & 1) << (48 + vlan_id_width)
    
    bit_pos = 49 + vlan_id_width
    for ch in range(len(vc_global_count)):
        vcs = dest_dict.get(ch, [])
        for vc in range(vc_global_count.get(ch, 1)):
            if vc in vcs:
                word |= (1 << bit_pos)
            bit_pos += 1
    
    if prio_enable:
        word |= (prio & ((1 << prio_width) - 1)) << bit_pos
    
    write_conf_reg_int(
        read_func=read_func,
        write_func=write_func,
        transport=transport,
        offset=offset,
        address=RB_FCL_STATIC_WRITE_DATA,
        data=word
    )


def read_address_association_shared(
    read_func: Optional[Callable] = None,
    write_func: Optional[Callable] = None,
    transport: Optional[Transport] = None,
    offset: int = 0,
    mac_address: int = 0,
    vc_global_count: Optional[dict] = None
) -> tuple:
    """
    Lee una dirección MAC (tipo shared).
    
    Returns:
        (dest_dict, error)
    """
    from control_registers import RB_FCL_STATIC_WRITE_DATA
    
    if vc_global_count is None:
        vc_global_count = {0: 4}
    
    value = read_conf_reg_int(
        read_func=read_func,
        write_func=write_func,
        transport=transport,
        offset=offset,
        address=RB_FCL_STATIC_WRITE_DATA,
        length=4
    )
    
    dest_dict = {}
    active = (value >> 48) & 1
    
    bit_pos = 49
    for ch in range(len(vc_global_count)):
        vcs = []
        for vc in range(vc_global_count.get(ch, 1)):
            if (value >> bit_pos) & 1:
                vcs.append(vc)
            bit_pos += 1
        if vcs:
            dest_dict[ch] = vcs
    
    return dest_dict, 0


def read_address_association_independent(
    read_func: Optional[Callable] = None,
    write_func: Optional[Callable] = None,
    transport: Optional[Transport] = None,
    offset: int = 0,
    mac_address: int = 0,
    vlan_id: int = 1,
    vc_global_count: Optional[dict] = None
) -> tuple:
    """
    Lee una dirección MAC (tipo independent).
    """
    return read_address_association_shared(
        read_func=read_func,
        write_func=write_func,
        transport=transport,
        offset=offset,
        mac_address=mac_address,
        vc_global_count=vc_global_count
    )


def read_address_association_mixed(
    read_func: Optional[Callable] = None,
    write_func: Optional[Callable] = None,
    transport: Optional[Transport] = None,
    offset: int = 0,
    mac_address: int = 0,
    vlan_id: int = 1,
    vlan_id_width: int = 12,
    vc_global_count: Optional[dict] = None
) -> tuple:
    """
    Lee una dirección MAC (tipo mixed).
    """
    return read_address_association_shared(
        read_func=read_func,
        write_func=write_func,
        transport=transport,
        offset=offset,
        mac_address=mac_address,
        vc_global_count=vc_global_count
    )


def write_vlan_egress_tag_association(
    read_func: Optional[Callable] = None,
    write_func: Optional[Callable] = None,
    transport: Optional[Transport] = None,
    offset: int = 0,
    vlan_id: int = 1,
    dest_dict: Optional[dict] = None,
    ch_count: int = 1,
    vc_count: Optional[dict] = None
) -> None:
    """
    Configura el tagging VLAN de egress.
    """
    from control_registers import RB_FCL_STATIC_WRITE_DATA
    
    if dest_dict is None:
        dest_dict = {}
    if vc_count is None:
        vc_count = {0: 4}
    
    word = vlan_id & 0xFFF
    
    bit_pos = 12
    for ch in range(ch_count):
        vcs = dest_dict.get(ch, [])
        for vc in range(vc_count.get(ch, 1)):
            if vc in vcs:
                word |= (1 << bit_pos)
            bit_pos += 1
    
    write_conf_reg_int(
        read_func=read_func,
        write_func=write_func,
        transport=transport,
        offset=offset,
        address=RB_FCL_STATIC_WRITE_DATA,
        data=word
    )
