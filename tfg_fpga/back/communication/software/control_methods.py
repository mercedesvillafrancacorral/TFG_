#!/usr/bin/env python
"""

Copyright (c) 2024-2026 Carlos Megías Núñez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

import re

from control_registers import *

# Write register
def write_conf_reg(write_func, offset=0x0, address=0x0, data=0x0):
    write_func(offset + address, data)

# Write integer register
def write_conf_reg_int(write_func, offset=0x0, address=0x0, data=0x0):
    bits = "{0:b}".format(data)

    # fill with 0s at the beginning to first byte
    bits = bits.zfill(int((len(bits)+7)/8)*8)

    # invert byte order to match bus ordering
    bits_sorted = ''
    for i in range(len(bits), 0, -8):
        if (i >= 8):
            bits_sorted = bits_sorted + bits[i - 8 : i]
        else:
            bits_sorted = bits_sorted + bits[i - i%8 : i]

    # complete last byte with 0s at the end if needed
    bits_sorted = bits_sorted.ljust(int((len(bits_sorted)+7)/8)*8, '0')

    #convert 8-bit groups to bytes
    data = bytes(int(bits_sorted[i : i + 8], 2) for i in range(0, len(bits_sorted), 8))

    write_conf_reg(write_func, offset, address, bytearray(list(data)))

# Change multiplexing at RX side of port module
def write_port_rx_mux(write_func, offset:int = 0x0, value:int = 0x0, write_width:int = 172):

    # bit to indicate if the target is port rx module or the traffic generator
    self_bit = "{0:b}".format(0)
    # bits to indicate the field of port rx to write
    field_bits = "{0:b}".format(RB_PORT_RX_MUX).zfill(8)
    # value to write
    value_bit = "{0:b}".format(value)

    destination_bits = value_bit + field_bits + self_bit
    destination_bits = destination_bits.zfill(write_width)
    destination_bits = destination_bits.zfill(int((len(destination_bits)+7)/8)*8)

    destination_bits_sorted = ''
    for i in range(len(destination_bits), 0, -8):
        if (i >= 8):
            destination_bits_sorted = destination_bits_sorted + destination_bits[i - 8 : i]
        else:
            destination_bits_sorted = destination_bits_sorted + destination_bits[i - i%8 : i]

    # concatenate the whole bit stream
    bits = destination_bits_sorted
    bits = bits.ljust(int((len(bits)+7)/8)*8, '0')
    # take care of last byte if it is not complete
    # convert to bytes each 8 bits
    c = bytes(int(bits[i : i + 8], 2) for i in range(0, len(bits), 8))

    write_conf_reg(write_func, offset, RB_PORT_WRITE_DATA, bytearray(list(c)))
    write_conf_reg(write_func, offset, RB_PORT_WRITE_CONTROL, bytearray([0x2]))

# Configure common counter of Port traffic generator
def write_port_rx_gen_common_counter(read_func, write_func, offset:int = 0x0, target:int = 0x0, target_width:int = 0x1, enable:int = 1, counter:int = 1000, counter_width:int = 16, counter_frac: int = 0, counter_frac_width:int = 16, length:int = 64, length_width:int = 64, common_type:int = 0, common_type_width:int = 1, vlan_enable:int = 0, destination_mac_address:int = 0x0, source_mac_address:int = 0x0, vlan_id:int = 0x1, vlan_pcp:int = 0x0, vlan_dei:int = 0x0, ether_type:int = 0x0001):

    # bit to indicate if the target is the traffic generator
    self_one_bit = "{0:b}".format(1)
    # bit to indicate that the target is one of the traffic generator submodules
    self_two_bit = "{0:b}".format(1)
    # bits to indicate the concrete traffic generator to apply the configuration (only if more than one)
    target_bits = "{0:b}".format(target).zfill(target_width)
    if target_width == 0:
        target_bits = ""
    # enable to write
    enable_bit = "{0:b}".format(enable)
    # counter bits
    counter_bits = "{0:b}".format(counter).zfill(counter_width)
    # counter_frac bits
    counter_frac_bits = "{0:b}".format(counter_frac).zfill(counter_frac_width)
    # length bits
    length_bits = "{0:b}".format(length).zfill(length_width)
    # type bits
    common_type_bits = "{0:b}".format(common_type).zfill(common_type_width)
    # VLAN enable to write
    vlan_enable_bit = "{0:b}".format(vlan_enable)
    # destination mac address to write
    destination_mac_address_bits = "{0:b}".format(destination_mac_address).zfill(48)
    destination_mac_address_bits = "".join([destination_mac_address_bits[i-8:i] for i in range(48, -8, -8)])
    # source mac address to write
    source_mac_address_bits = "{0:b}".format(source_mac_address).zfill(48)
    source_mac_address_bits = "".join([source_mac_address_bits[i-8:i] for i in range(48, -8, -8)])
    # VLAN tag
    vlan_pcp_bits = "{0:b}".format(vlan_pcp).zfill(3)
    vlan_dei_bit = "{0:b}".format(vlan_dei)
    vlan_id_bits = "{0:b}".format(vlan_id).zfill(12)
    vlan_tag_bits = vlan_id_bits[4:12] + vlan_pcp_bits + vlan_dei_bit + vlan_id_bits[0:4]
    # ethertype to write
    ether_type_bits = "{0:b}".format(ether_type).zfill(16)
    ether_type_bits = "".join([ether_type_bits[i-8:i] for i in range(16, -8, -8)])

    destination_bits = ether_type_bits + vlan_tag_bits + source_mac_address_bits + destination_mac_address_bits + vlan_enable_bit + common_type_bits + length_bits + counter_frac_bits + counter_bits + enable_bit + target_bits + self_two_bit + self_one_bit
    destination_bits = destination_bits.zfill(int((len(destination_bits)+7)/8)*8)

    destination_bits_sorted = ''
    for i in range(len(destination_bits), 0, -8):
        if (i >= 8):
            destination_bits_sorted = destination_bits_sorted + destination_bits[i - 8 : i]
        else:
            destination_bits_sorted = destination_bits_sorted + destination_bits[i - i%8 : i]

    # concatenate the whole bit stream
    bits = destination_bits_sorted
    bits = bits.ljust(int((len(bits)+7)/8)*8, '0')
    # take care of last byte if it is not complete
    # convert to bytes each 8 bits
    c = bytes(int(bits[i : i + 8], 2) for i in range(0, len(bits), 8))

    # wait until rx valid is high
    req_complete = 0
    while not req_complete:
        req_complete = read_conf_reg_int(read_func=read_func, offset=offset, address=RB_PORT_RX_VALID, length=4)

    write_conf_reg(write_func, offset, RB_PORT_WRITE_DATA, bytearray(list(c)))
    write_conf_reg(write_func, offset, RB_PORT_WRITE_CONTROL, bytearray([0x2]))

# Change multiplexing at TX side of port module
def write_port_tx_mux(write_func, offset:int = 0x0, value:int = 0x0, write_width:int = 10):

    # bit to indicate if the target is port rx module or the traffic generator
    self_bit = "{0:b}".format(0)
    # bits to indicate the field of port rx to write
    field_bits = "{0:b}".format(RB_PORT_TX_MUX).zfill(8)
    # value to write
    value_bit = "{0:b}".format(value)

    destination_bits = value_bit + field_bits + self_bit
    destination_bits = destination_bits.zfill(write_width)
    destination_bits = destination_bits.zfill(int((len(destination_bits)+7)/8)*8)

    destination_bits_sorted = ''
    for i in range(len(destination_bits), 0, -8):
        if (i >= 8):
            destination_bits_sorted = destination_bits_sorted + destination_bits[i - 8 : i]
        else:
            destination_bits_sorted = destination_bits_sorted + destination_bits[i - i%8 : i]

    # concatenate the whole bit stream
    bits = destination_bits_sorted
    bits = bits.ljust(int((len(bits)+7)/8)*8, '0')
    # take care of last byte if it is not complete
    # convert to bytes each 8 bits
    c = bytes(int(bits[i : i + 8], 2) for i in range(0, len(bits), 8))

    write_conf_reg(write_func, offset, RB_PORT_WRITE_DATA, bytearray(list(c)))
    write_conf_reg(write_func, offset, RB_PORT_WRITE_CONTROL, bytearray([0x3]))

# Read register
def read_conf_reg(read_func, offset=0x0, address=0x0, length=4):
    response = read_func(offset + address, length)
    return response

# Read integer register
def read_conf_reg_int(read_func, offset=0x0, address=0x0, length=4):
    data = read_conf_reg(read_func, offset, address, length)
    return int.from_bytes(data, 'little')

# Read Port RX counter value
def read_port_rx_counter(write_func, read_func, offset:int =0x0, field_addr:int = 0x0, read_width:int = 64):

    # bit to indicate if the target is port rx module or the traffic generator
    self_bit = "{0:b}".format(0)
    # bits to indicate the field of port rx to write
    field_bits = "{0:b}".format(field_addr).zfill(8)

    destination_bits = field_bits + self_bit
    destination_bits = destination_bits.zfill(int((len(destination_bits)+7)/8)*8)

    destination_bits_sorted = ''
    for i in range(len(destination_bits), 0, -8):
        if (i >= 8):
            destination_bits_sorted = destination_bits_sorted + destination_bits[i - 8 : i]
        else:
            destination_bits_sorted = destination_bits_sorted + destination_bits[i - i%8 : i]

    # concatenate the whole bit stream
    bits = destination_bits_sorted
    bits = bits.ljust(int((len(bits)+7)/8)*8, '0')
    # take care of last byte if it is not complete
    # convert to bytes each 8 bits
    c = bytes(int(bits[i : i + 8], 2) for i in range(0, len(bits), 8))

    write_conf_reg(write_func, offset, RB_PORT_WRITE_DATA, bytearray(list(c)))
    write_conf_reg(write_func, offset, RB_PORT_WRITE_CONTROL, bytearray([0x2]))
    
    # wait until read has finished
    req_complete = 0
    while not req_complete:
        req_complete = read_conf_reg_int(read_func=read_func, offset=offset, address=RB_PORT_RX_READ_COMPLETE, length=4)

    # read lookup response
    read_bytes_count = (read_width + 7) // 8

    data = read_conf_reg_int(read_func, offset, RB_PORT_RX_READ_DATA, length=read_bytes_count)

    # signal all data has been read
    write_conf_reg(write_func, offset, RB_PORT_RX_READ_READY, bytearray([0x1]))

    return data

# Read Port TX counter value
def read_port_tx_counter(write_func, read_func, offset:int =0x0, field_addr:int = 0x0, read_width:int = 64):

    # bit to indicate if the target is port rx module or the traffic generator
    self_bit = "{0:b}".format(0)
    # bits to indicate the field of port rx to write
    field_bits = "{0:b}".format(field_addr).zfill(8)

    destination_bits = field_bits + self_bit
    destination_bits = destination_bits.zfill(int((len(destination_bits)+7)/8)*8)

    destination_bits_sorted = ''
    for i in range(len(destination_bits), 0, -8):
        if (i >= 8):
            destination_bits_sorted = destination_bits_sorted + destination_bits[i - 8 : i]
        else:
            destination_bits_sorted = destination_bits_sorted + destination_bits[i - i%8 : i]

    # concatenate the whole bit stream
    bits = destination_bits_sorted
    bits = bits.ljust(int((len(bits)+7)/8)*8, '0')
    # take care of last byte if it is not complete
    # convert to bytes each 8 bits
    c = bytes(int(bits[i : i + 8], 2) for i in range(0, len(bits), 8))

    write_conf_reg(write_func, offset, RB_PORT_WRITE_DATA, bytearray(list(c)))
    write_conf_reg(write_func, offset, RB_PORT_WRITE_CONTROL, bytearray([0x3]))
    
    # wait until read has finished
    req_complete = 0
    while not req_complete:
        req_complete = read_conf_reg_int(read_func=read_func, offset=offset, address=RB_PORT_TX_READ_COMPLETE, length=4)

    # read lookup response
    read_bytes_count = (read_width + 7) // 8

    data = read_conf_reg_int(read_func, offset, RB_PORT_TX_READ_DATA, length=read_bytes_count)

    # signal all data has been read
    write_conf_reg(write_func, offset, RB_PORT_TX_READ_READY, bytearray([0x1]))

    return data

def convert_mac_to_int(mac_address):
    """
    Convert a MAC address into integer.
    """

    if type(mac_address) is int:
        return mac_address
    elif type(mac_address) is str and re.match("0+x|x?[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac_address.lower()):
        return int(mac_address.replace("0x", '').replace("x", '').replace("-", '').replace(":", ''), 16)
    else:
        return mac_address