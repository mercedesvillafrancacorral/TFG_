#!/usr/bin/env python
"""

Copyright (c) 2026 Carlos Megías Núñez

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

from control_methods import *

import math


class Port():
    _type="Port"

    def __init__(self, read_func, write_func, offset: int = 0x0):

        self.read_func = read_func
        self.write_func = write_func
        
        self.offset = offset

    def initialize(self):
        """
        Prepare Port
        """

        # Read all constant architectural parameters (non-changing over time)
        self.PORT_ID                 = self.read_conf_int(addr=RB_PORT_ID)
        self.PORT_RATE               = self.read_conf_int(addr=RB_PORT_RATE)
        self.FEATURES                = self.read_conf_int(addr=RB_PORT_FEATURES)
        self.RX_VALID                = self.read_conf_int(addr=RB_PORT_RX_VALID)
        self.GEN_TRAFFIC_COMMON_COUNT = self.read_conf_int(addr=RB_PORT_GEN_TRAFFIC_COMMON_COUNT)
        self.GEN_COUNTER_WIDTH       = self.read_conf_int(addr=RB_PORT_GEN_COUNTER_WIDTH)
        self.GEN_COUNTER_FRAC_WIDTH  = self.read_conf_int(addr=RB_PORT_GEN_COUNTER_FRAC_WIDTH)
        self.GEN_MIN_FRAME_LENGTH    = self.read_conf_int(addr=RB_PORT_GEN_MIN_FRAME_LENGTH)
        self.READ_WIDTH              = self.read_conf_int(addr=RB_PORT_READ_WIDTH)
        self.RX_WRITE_WIDTH          = 1 + 146 + 2 + self.GEN_COUNTER_WIDTH + self.GEN_COUNTER_FRAC_WIDTH + math.ceil(math.log2(self.GEN_TRAFFIC_COMMON_COUNT))
        self.TX_WRITE_WIDTH          = 1 + 8 + 1

        self.RX_TRAFFIC_ENABLE       = (self.FEATURES & (1 << 0)) >> 0
        self.TX_TRAFFIC_ENABLE       = (self.FEATURES & (1 << 1)) >> 1
        self.GEN_TRAFFIC_ENABLE      = (self.FEATURES & (1 << 2)) >> 2
        self.GEN_OUTPUT_REGISTER     = (self.FEATURES & (1 << 3)) >> 3

        self.gen_common_count_width   = math.ceil(math.log2(self.GEN_TRAFFIC_COMMON_COUNT)) if self.GEN_TRAFFIC_COMMON_COUNT > 1 else 0

    # Low level configuration methods
    def write_int(self, offset: int = 0, addr: int = 0, value: int = 0):
        write_conf_reg_int(write_func=self.write_func, offset=self.offset + offset, address=addr, data=value)

    def read_int(self, offset: int = 0, addr: int = 0):
        return read_conf_reg_int(read_func=self.read_func, offset=self.offset + offset, address=addr, length=4)

    def read_conf_int(self, addr: int = 0):
        return self.read_int(offset=0x0, addr=addr)


    # RX configuration methods
    def set_rx_null_mux(self):
        """Set null as multiplexing for RX"""
        write_port_rx_mux(write_func=self.write_func, offset=self.offset, value=0, write_width=self.RX_WRITE_WIDTH)
        
    def set_rx_mac_mux(self):
        """Set RX side from MAC as multiplexing for RX"""
        write_port_rx_mux(write_func=self.write_func, offset=self.offset, value=1, write_width=self.RX_WRITE_WIDTH)

    def set_rx_gen_mux(self):
        """Set traffic generator as multiplexing for RX"""
        write_port_rx_mux(write_func=self.write_func, offset=self.offset, value=2, write_width=self.RX_WRITE_WIDTH)

    def set_rx_gen_common_counter(self, target: int = 0, enable: int =1, counter: int = 100, counter_frac: int = 0, length: int = 64, common_type: int = 0, vlan_enable:int = 0, destination_mac_address:int = 0x0, 
        source_mac_address:int = 0x0, vlan_id:int = 0x1, vlan_pcp:int = 0x0, vlan_dei:int = 0x0, ether_type:int = 0x0001):
        """Create (enable) or disable (disable) RX traffic generator common counter"""
        write_port_rx_gen_common_counter(read_func=self.read_func, write_func=self.write_func, offset=self.offset, target=target, target_width=self.gen_common_count_width,
            enable=enable, counter=counter, counter_width=self.GEN_COUNTER_WIDTH, counter_frac=counter_frac, counter_frac_width=self.GEN_COUNTER_FRAC_WIDTH, length=length, length_width=16, common_type=common_type, common_type_width=1, 
            vlan_enable=vlan_enable, destination_mac_address=destination_mac_address, source_mac_address=source_mac_address, vlan_id=vlan_id, vlan_pcp=vlan_pcp, vlan_dei=vlan_dei, ether_type=ether_type)

    def delete_rx_gen_common_counter(self, target: int = 0):
        """Delete (disable) RX traffic generator common counter"""
        self.set_rx_gen_common_counter(target=target, enable=0)

    def delete_rx_gen_basic_counter(self, target: int = 0, counter: int = 100, counter_frac: int = 0, length: int = 64, vlan_enable:int = 0, destination_mac_address:int = 0x0, 
        source_mac_address:int = 0x0, vlan_id:int = 0x1, vlan_pcp:int = 0x0, vlan_dei:int = 0x0, ether_type:int = 0x0001):
        """Create (enable) RX traffic generator basic common counter"""
        self.set_rx_gen_common_counter(target=target, enable=0, counter=counter, counter_frac=counter_frac, length=length, common_type=0, vlan_enable=vlan_enable, 
            destination_mac_address=destination_mac_address, source_mac_address=source_mac_address, vlan_id=vlan_id, vlan_pcp=vlan_pcp, vlan_dei=vlan_dei, ether_type=ether_type)

    def create_rx_gen_common_counter(self, target: int = 0, counter: int = 100, counter_frac: int = 0, length: int = 64, common_type: int = 0, vlan_enable:int = 0, destination_mac_address:int = 0x0, 
        source_mac_address:int = 0x0, vlan_id:int = 0x1, vlan_pcp:int = 0x0, vlan_dei:int = 0x0, ether_type:int = 0x0001):
        """Create (enable) RX traffic generator common counter"""
        self.set_rx_gen_common_counter(target=target, enable=1, counter=counter, counter_frac=counter_frac, length=length, common_type=common_type, vlan_enable=vlan_enable, 
            destination_mac_address=destination_mac_address, source_mac_address=source_mac_address, vlan_id=vlan_id, vlan_pcp=vlan_pcp, vlan_dei=vlan_dei, ether_type=ether_type)

    def create_rx_gen_basic_counter(self, target: int = 0, counter: int = 100, counter_frac: int = 0, length: int = 64, vlan_enable:int = 0, destination_mac_address:int = 0x0, 
        source_mac_address:int = 0x0, vlan_id:int = 0x1, vlan_pcp:int = 0x0, vlan_dei:int = 0x0, ether_type:int = 0x0001):
        """Create (enable) RX traffic generator basic common counter"""
        self.set_rx_gen_common_counter(target=target, enable=1, counter=counter, counter_frac=counter_frac, length=length, common_type=0, vlan_enable=vlan_enable, 
            destination_mac_address=destination_mac_address, source_mac_address=source_mac_address, vlan_id=vlan_id, vlan_pcp=vlan_pcp, vlan_dei=vlan_dei, ether_type=ether_type)

    def create_rx_gen_random_smac_counter(self, target: int = 0, counter: int = 100, counter_frac: int = 0, length: int = 64, vlan_enable:int = 0, destination_mac_address:int = 0x0, 
        source_mac_address:int = 0x0, vlan_id:int = 0x1, vlan_pcp:int = 0x0, vlan_dei:int = 0x0, ether_type:int = 0x0001):
        """Create (enable) RX traffic generator random source MAC address common counter"""
        self.set_rx_gen_common_counter(target=target, enable=1, counter=counter, counter_frac=counter_frac, length=length, common_type=1, vlan_enable=vlan_enable, 
            destination_mac_address=destination_mac_address, source_mac_address=source_mac_address, vlan_id=vlan_id, vlan_pcp=vlan_pcp, vlan_dei=vlan_dei, ether_type=ether_type)

    def get_rx_counter(self, field_addr: int = 0x0):
        """ Get counter value from RX"""
        return read_port_rx_counter(write_func=self.write_func, read_func=self.read_func, offset=self.offset, field_addr=field_addr, read_width=self.READ_WIDTH)

    def get_rx_port_out_frame_counter(self):
        """ Get rx_port_out_frame_counter value from RX"""
        return self.get_rx_counter(field_addr=RB_PORT_RX_PORT_OUT_FRAME_COUNTER)

    def get_rx_port_in_frame_counter(self):
        """ Get rx_port_in_frame_counter value from RX"""
        return self.get_rx_counter(field_addr=RB_PORT_RX_PORT_IN_FRAME_COUNTER)

    def get_rx_port_gen_frame_counter(self):
        """ Get rx_port_gen_frame_counter value from RX"""
        return self.get_rx_counter(field_addr=RB_PORT_RX_PORT_GEN_FRAME_COUNTER)

    def get_rx_port_in_true_frame_counter(self):
        """ Get rx_port_in_true_frame_counter value from RX"""
        return self.get_rx_counter(field_addr=RB_PORT_RX_PORT_IN_TRUE_FRAME_COUNTER)

    def get_rx_port_gen_true_frame_counter(self):
        """ Get rx_port_gen_true_frame_counter value from RX"""
        return self.get_rx_counter(field_addr=RB_PORT_RX_PORT_GEN_TRUE_FRAME_COUNTER)


    # TX configuration methods
    def set_tx_null_mux(self):
        """Set null as multiplexing for TX"""
        write_port_tx_mux(write_func=self.write_func, offset=self.offset, value=0, write_width=self.TX_WRITE_WIDTH)
        
    def set_tx_mac_mux(self):
        """Set TX side from MAC as multiplexing for TX"""
        write_port_tx_mux(write_func=self.write_func, offset=self.offset, value=1, write_width=self.TX_WRITE_WIDTH)

    def get_tx_counter(self, field_addr: int = 0x0):
        """ Get counter value from RX"""
        return read_port_tx_counter(write_func=self.write_func, read_func=self.read_func, offset=self.offset, field_addr=field_addr, read_width=self.READ_WIDTH)

    def get_tx_port_out_frame_counter(self):
        """ Get tx_port_out_frame_counter value from TX"""
        return self.get_tx_counter(field_addr=RB_PORT_TX_PORT_OUT_FRAME_COUNTER)

    def get_tx_port_in_frame_counter(self):
        """ Get tx_port_in_frame_counter value from TX"""
        return self.get_tx_counter(field_addr=RB_PORT_TX_PORT_IN_FRAME_COUNTER)

    def get_tx_port_in_true_frame_counter(self):
        """ Get tx_port_in_true_frame_counter value from TX"""
        return self.get_tx_counter(field_addr=RB_PORT_TX_PORT_IN_TRUE_FRAME_COUNTER)


    # Additional methods
    def get_parameters(self):
        """Get Port architectural parameters"""
        return {
                    "PORT_ID": self.PORT_ID,
                    "PORT_RATE (Mbps)": self.PORT_RATE,
                    "READ_WIDTH": self.READ_WIDTH,
                    "RX_WRITE_WIDTH": self.RX_WRITE_WIDTH,
                    "TX_WRITE_WIDTH": self.TX_WRITE_WIDTH,                    
                    "RX_VALID": self.RX_VALID,
                    "GEN_TRAFFIC_COMMON_COUNT": self.GEN_TRAFFIC_COMMON_COUNT,
                    "GEN_COUNTER_WIDTH": self.GEN_COUNTER_WIDTH,
                    "GEN_COUNTER_FRAC_WIDTH": self.GEN_COUNTER_FRAC_WIDTH,
                    "GEN_MIN_FRAME_LENGTH": self.GEN_MIN_FRAME_LENGTH,
                    "RX_TRAFFIC_ENABLE": self.RX_TRAFFIC_ENABLE,
                    "TX_TRAFFIC_ENABLE": self.TX_TRAFFIC_ENABLE,
                    "GEN_TRAFFIC_ENABLE": self.GEN_TRAFFIC_ENABLE,
                    "GEN_OUTPUT_REGISTER": self.GEN_OUTPUT_REGISTER
                }

    def show_parameters(self):
        """Print Port architectural parameters"""
        for param_str, param_value in self.get_parameters().items():
            print(f'\t{param_str}: {param_value}')


    def __str__(self):
        return self.get_parameters()


class TrafficGenerator():
    _type = "TrafficGenerator"

    def __init__(self, read_func, write_func, offset:int = 0x0, port_offset:int = 0x0, port_stride:int = 0x0, port_enable_sum:int = 2, port_25G_enable_sum:int = 1, port_100G_enable_sum:int = 1):
        
        self.read_func = read_func
        self.write_func = write_func

        self.offset = offset

        # Port (modules) attrbutes
        self.port_offset = port_offset
        self.port_stride = port_stride
        self.port_dict = {}
        self.port_module_offset = {}
        self.port_module_count = port_enable_sum
        self.port_25g_module_count = port_25G_enable_sum
        self.port_100g_module_count = port_100G_enable_sum


    def initialize(self):
        """
        Prepare Ports
        """
        self.degraded_ports = {}

        # Instantiate port modules
        if self.port_module_count:
            for i in range(self.port_module_count):
                port = Port(write_func=self.write_func, read_func=self.read_func, offset=self.port_offset + i*self.port_stride)
                try:
                    port.initialize()
                except Exception as e:
                    port_id = getattr(port, "PORT_ID", i)
                    print(f"AVISO: puerto {port_id} no disponible ({e}); probable reconfiguración parcial pendiente de recarga completa")
                    self.degraded_ports[port_id] = str(e)
                    continue
                self.port_dict[port.PORT_ID] = port
                self.port_module_offset[port.PORT_ID] = self.port_offset + i*self.port_stride


    @classmethod
    def fromRegisters(cls, write_func, read_func, offset: int = 0x0):
        """
        Traffic generator initialization by reading from its RB control registers
        """

        port_enable_sum      = read_conf_reg_int(read_func=read_func, offset=offset, address=0x10, length=4)
        port_25G_enable_sum  = read_conf_reg_int(read_func=read_func, offset=offset, address=0x14, length=4)
        port_100G_enable_sum = read_conf_reg_int(read_func=read_func, offset=offset, address=0x18, length=4)
        port_offset          = read_conf_reg_int(read_func=read_func, offset=offset, address=0x1C, length=4)
        port_stride          = read_conf_reg_int(read_func=read_func, offset=offset, address=0x20, length=4)

        self = cls(read_func=read_func, write_func=write_func, offset=offset, port_offset=port_offset, port_stride=port_stride, port_enable_sum=port_enable_sum, port_25G_enable_sum=port_25G_enable_sum, port_100G_enable_sum=port_100G_enable_sum)
    
        self.initialize()

        return self


    # Low level configuration methods
    def write_int(self, offset: int = 0, addr: int = 0, value: int = 0):
        write_conf_reg_int(write_func=self.write_func, offset=self.offset + offset, address=addr, data=value)

    def read_int(self, offset: int = 0, addr: int = 0):
        return read_conf_reg_int(read_func=self.read_func, offset=self.offset + offset, address=addr, length=4)

    def read_conf_int(self, addr: int = 0):
        return self.read_int(offset=0x0, addr=addr)


    # Port configuration methods
    def set_rx_mac_mux(self):
        """Set RX side from MAC as multiplexing for RX for all port modules"""
        for port in self.port_dict.values():
            port.set_rx_mac_mux()

    def set_rx_gen_mux(self):
        """Set taffic generator as multiplexing for RX for all port modules"""
        for port in self.port_dict.values():
            port.set_rx_gen_mux()

    def set_rx_null_mux(self):
        """Set null as multiplexing for RX for all port modules"""
        for port in self.port_dict.values():
            port.set_rx_null_mux()

    def set_tx_mac_mux(self):
        """Set TX side from MAC as multiplexing for TX for all port modules"""
        for port in self.port_dict.values():
            port.set_tx_mac_mux()

    def set_tx_null_mux(self):
        """Set null as multiplexing for TX for all port modules"""
        for port in self.port_dict.values():
            port.set_tx_null_mux()

    def get_bandwidth_l2_counters(self, port: int, clk_freq: float, bandwidth: float, frame_length: int):
        # obtain the counter frequency for generating frames and fractional part
        counter = clk_freq * frame_length * 8 / bandwidth
        counter_ach = math.ceil(counter)
        counter_debt = counter_ach-counter
        counter_frac = math.floor(((2**self.port_dict[0].GEN_COUNTER_FRAC_WIDTH-1) / counter) * (counter_debt))
        return counter_ach, counter_frac

    def get_parameters_port(self, port: int = 0):
        """Get architectural parameters for specified port module"""
        if port in self.port_dict:
            return self.port_dict[port].get_parameters()

    def show_parameters_port(self, port: int = 0):
        """Print architectural parameters for specified port module"""
        if port in self.port_dict:
            self.port_dict[port].show_parameters()

    def get_parameters_all_port(self):
        """ Get architectural parameters for all port modules"""
        return {port:self.get_parameters_port(port=port) for port in self.port_dict.keys()}

    def show_parameters_all_port(self):
        """
        Show parameters of port modules belonging to the traffic generator
        """
        for port in self.port_dict.values():
            port.show_parameters()
            print("\n")

    def get_parameters(self):
        """Get traffic generator architectural parameters"""
        return {
                    "PORT_ENABLE_SUM": self.port_module_count,
                    "PORT_25G_ENABLE_SUM": self.port_25g_module_count,
                    "PORT_100G_ENABLE_SUM": self.port_100g_module_count
                }
        
    def show_parameters(self):
        """Print traffic generator architectural parameters"""
        for param_str, param_value in self.get_parameters().items():
            print(f'\t{param_str}: {param_value}')

    def __str__(self):
        return self.get_parameters()
