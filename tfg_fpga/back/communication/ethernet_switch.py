# #!/usr/bin/env python
# """

# Copyright (c) 2024-2025 Carlos Megías Núñez

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# """

# import os
# import sys


# CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
# XFCP_PYTHON_ROOT = os.path.abspath(
#     os.path.join(CURRENT_DIR, "..", "libs", "xfcp", "python")
# )


# if XFCP_PYTHON_ROOT not in sys.path:
#     sys.path.insert(0, XFCP_PYTHON_ROOT)

# import back.communication.lib.xfcp.python.xfcp.interface
# from back.communication.lib.xfcp.python.xfcp.node import Node
# from back.communication.lib.xfcp.python.xfcp.i2c_node import I2CNode


# import serial

# #from control_methods import *
# from back.communication.mock_control_methods import *
# from back.communication.control_registers import *
# import threading

# import time

# import math

# from multiprocessing import Process

# # dict for mapping VLAN learning type
# VLAN_LEARNING_TYPE_DICT = {0: "shared", 1: "independent", 2: "shared"}


# class Port():
#     _type="Port"

#     def __init__(self, read_func, write_func, offset: int = 0x0):

#         self.read_func = read_func
#         self.write_func = write_func
        
#         self.offset = offset

#     def initialize(self):
#         """
#         Prepare Port
#         """

#         # Read all constant architectural parameters (non-changing over time)
#         self.PORT_ID                 = self.read_conf_int(addr=RB_PORT_ID)
#         self.PORT_RATE               = self.read_conf_int(addr=RB_PORT_RATE)
#         self.FEATURES                = self.read_conf_int(addr=RB_PORT_FEATURES)
#         self.RX_VALID                = self.read_conf_int(addr=RB_PORT_RX_VALID)
#         self.GEN_TRAFFIC_COMMON_COUNT = self.read_conf_int(addr=RB_PORT_GEN_TRAFFIC_COMMON_COUNT)
#         self.GEN_COUNTER_WIDTH       = self.read_conf_int(addr=RB_PORT_GEN_COUNTER_WIDTH)
#         self.GEN_COUNTER_FRAC_WIDTH  = self.read_conf_int(addr=RB_PORT_GEN_COUNTER_FRAC_WIDTH)
#         self.GEN_MIN_FRAME_LENGTH    = self.read_conf_int(addr=RB_PORT_GEN_MIN_FRAME_LENGTH)
#         self.READ_WIDTH              = self.read_conf_int(addr=RB_PORT_READ_WIDTH)
#         self.RX_WRITE_WIDTH          = 1 + 146 + 2 + self.GEN_COUNTER_WIDTH + self.GEN_COUNTER_FRAC_WIDTH + math.ceil(math.log2(self.GEN_TRAFFIC_COMMON_COUNT))
#         self.TX_WRITE_WIDTH          = 1 + 8 + 1

#         self.RX_TRAFFIC_ENABLE       = (self.FEATURES & (1 << 0)) >> 0
#         self.TX_TRAFFIC_ENABLE       = (self.FEATURES & (1 << 1)) >> 1
#         self.GEN_TRAFFIC_ENABLE      = (self.FEATURES & (1 << 2)) >> 2
#         self.GEN_OUTPUT_REGISTER     = (self.FEATURES & (1 << 3)) >> 3

#         self.gen_common_count_width   = math.ceil(math.log2(self.GEN_TRAFFIC_COMMON_COUNT)) if self.GEN_TRAFFIC_COMMON_COUNT > 1 else 0

#     # Low level configuration methods
#     def write_int(self, offset: int = 0, addr: int = 0, value: int = 0):
#         write_conf_reg_int(write_func=self.write_func, offset=self.offset + offset, address=addr, data=value)

#     def read_int(self, offset: int = 0, addr: int = 0):
#         return read_conf_reg_int(read_func=self.read_func, offset=self.offset + offset, address=addr, length=4)

#     def read_conf_int(self, addr: int = 0):
#         return self.read_int(offset=0x0, addr=addr)


#     # Port configuration methods


#     # RX configuration methods
#     def set_rx_null_mux(self):
#         """Set null as multiplexing for RX"""
#         write_port_rx_mux(write_func=self.write_func, offset=self.offset, value=0, write_width=self.RX_WRITE_WIDTH)
        
#     def set_rx_mac_mux(self):
#         """Set RX side from MAC as multiplexing for RX"""
#         write_port_rx_mux(write_func=self.write_func, offset=self.offset, value=1, write_width=self.RX_WRITE_WIDTH)

#     def set_rx_gen_mux(self):
#         """Set traffic generator as multiplexing for RX"""
#         write_port_rx_mux(write_func=self.write_func, offset=self.offset, value=2, write_width=self.RX_WRITE_WIDTH)

#     def set_rx_gen_common_counter(self, target: int = 0, enable: int =1, counter: int = 100, counter_frac: int = 0, length: int = 64, common_type: int = 0, vlan_enable:int = 0, destination_mac_address:int = 0x0, 
#         source_mac_address:int = 0x0, vlan_id:int = 0x1, vlan_pcp:int = 0x0, vlan_dei:int = 0x0, ether_type:int = 0x0001):
#         """Create (enable) or disable (disable) RX traffic generator common counter"""
#         write_port_rx_gen_common_counter(read_func=self.read_func, write_func=self.write_func, offset=self.offset, target=target, target_width=self.gen_common_count_width,
#             enable=enable, counter=counter, counter_width=self.GEN_COUNTER_WIDTH, counter_frac=counter_frac, counter_frac_width=self.GEN_COUNTER_FRAC_WIDTH, length=length, length_width=16, common_type=common_type, common_type_width=1, 
#             vlan_enable=vlan_enable, destination_mac_address=destination_mac_address, source_mac_address=source_mac_address, vlan_id=vlan_id, vlan_pcp=vlan_pcp, vlan_dei=vlan_dei, ether_type=ether_type)

#     def delete_rx_gen_common_counter(self, target: int = 0):
#         """Delete (disable) RX traffic generator common counter"""
#         self.set_rx_gen_common_counter(target=target, enable=0)

#     def delete_rx_gen_basic_counter(self, target: int = 0, counter: int = 100, counter_frac: int = 0, length: int = 64, vlan_enable:int = 0, destination_mac_address:int = 0x0, 
#         source_mac_address:int = 0x0, vlan_id:int = 0x1, vlan_pcp:int = 0x0, vlan_dei:int = 0x0, ether_type:int = 0x0001):
#         """Create (enable) RX traffic generator basic common counter"""
#         self.set_rx_gen_common_counter(target=target, enable=0, counter=counter, counter_frac=counter_frac, length=length, common_type=0, vlan_enable=vlan_enable, 
#             destination_mac_address=destination_mac_address, source_mac_address=source_mac_address, vlan_id=vlan_id, vlan_pcp=vlan_pcp, vlan_dei=vlan_dei, ether_type=ether_type)

#     def create_rx_gen_common_counter(self, target: int = 0, counter: int = 100, counter_frac: int = 0, length: int = 64, common_type: int = 0, vlan_enable:int = 0, destination_mac_address:int = 0x0, 
#         source_mac_address:int = 0x0, vlan_id:int = 0x1, vlan_pcp:int = 0x0, vlan_dei:int = 0x0, ether_type:int = 0x0001):
#         """Create (enable) RX traffic generator common counter"""
#         self.set_rx_gen_common_counter(target=target, enable=1, counter=counter, counter_frac=counter_frac, length=length, common_type=common_type, vlan_enable=vlan_enable, 
#             destination_mac_address=destination_mac_address, source_mac_address=source_mac_address, vlan_id=vlan_id, vlan_pcp=vlan_pcp, vlan_dei=vlan_dei, ether_type=ether_type)

#     def create_rx_gen_basic_counter(self, target: int = 0, counter: int = 100, counter_frac: int = 0, length: int = 64, vlan_enable:int = 0, destination_mac_address:int = 0x0, 
#         source_mac_address:int = 0x0, vlan_id:int = 0x1, vlan_pcp:int = 0x0, vlan_dei:int = 0x0, ether_type:int = 0x0001):
#         """Create (enable) RX traffic generator basic common counter"""
#         self.set_rx_gen_common_counter(target=target, enable=1, counter=counter, counter_frac=counter_frac, length=length, common_type=0, vlan_enable=vlan_enable, 
#             destination_mac_address=destination_mac_address, source_mac_address=source_mac_address, vlan_id=vlan_id, vlan_pcp=vlan_pcp, vlan_dei=vlan_dei, ether_type=ether_type)

#     def create_rx_gen_random_smac_counter(self, target: int = 0, counter: int = 100, counter_frac: int = 0, length: int = 64, vlan_enable:int = 0, destination_mac_address:int = 0x0, 
#         source_mac_address:int = 0x0, vlan_id:int = 0x1, vlan_pcp:int = 0x0, vlan_dei:int = 0x0, ether_type:int = 0x0001):
#         """Create (enable) RX traffic generator random source MAC address common counter"""
#         self.set_rx_gen_common_counter(target=target, enable=1, counter=counter, counter_frac=counter_frac, length=length, common_type=1, vlan_enable=vlan_enable, 
#             destination_mac_address=destination_mac_address, source_mac_address=source_mac_address, vlan_id=vlan_id, vlan_pcp=vlan_pcp, vlan_dei=vlan_dei, ether_type=ether_type)

#     def get_rx_counter(self, field_addr: int = 0x0):
#         """ Get counter value from RX"""
#         return read_port_rx_counter(write_func=self.write_func, read_func=self.read_func, offset=self.offset, field_addr=field_addr, read_width=self.READ_WIDTH)

#     def get_rx_port_out_frame_counter(self):
#         """ Get rx_port_out_frame_counter value from RX"""
#         return self.get_rx_counter(field_addr=RB_PORT_RX_PORT_OUT_FRAME_COUNTER)

#     def get_rx_port_in_frame_counter(self):
#         """ Get rx_port_in_frame_counter value from RX"""
#         return self.get_rx_counter(field_addr=RB_PORT_RX_PORT_IN_FRAME_COUNTER)

#     def get_rx_port_gen_frame_counter(self):
#         """ Get rx_port_gen_frame_counter value from RX"""
#         return self.get_rx_counter(field_addr=RB_PORT_RX_PORT_GEN_FRAME_COUNTER)

#     def get_rx_port_in_true_frame_counter(self):
#         """ Get rx_port_in_true_frame_counter value from RX"""
#         return self.get_rx_counter(field_addr=RB_PORT_RX_PORT_IN_TRUE_FRAME_COUNTER)

#     def get_rx_port_gen_true_frame_counter(self):
#         """ Get rx_port_gen_true_frame_counter value from RX"""
#         return self.get_rx_counter(field_addr=RB_PORT_RX_PORT_GEN_TRUE_FRAME_COUNTER)


#     # TX configuration methods
#     def set_tx_null_mux(self):
#         """Set null as multiplexing for TX"""
#         write_port_tx_mux(write_func=self.write_func, offset=self.offset, value=0, write_width=self.TX_WRITE_WIDTH)
        
#     def set_tx_mac_mux(self):
#         """Set TX side from MAC as multiplexing for TX"""
#         write_port_tx_mux(write_func=self.write_func, offset=self.offset, value=1, write_width=self.TX_WRITE_WIDTH)

#     def get_tx_counter(self, field_addr: int = 0x0):
#         """ Get counter value from RX"""
#         return read_port_tx_counter(write_func=self.write_func, read_func=self.read_func, offset=self.offset, field_addr=field_addr, read_width=self.READ_WIDTH)

#     def get_tx_port_out_frame_counter(self):
#         """ Get rx_port_out_frame_counter value from RX"""
#         return self.get_tx_counter(field_addr=RB_PORT_TX_PORT_OUT_FRAME_COUNTER)

#     def get_tx_port_in_frame_counter(self):
#         """ Get rx_port_in_frame_counter value from RX"""
#         return self.get_tx_counter(field_addr=RB_PORT_TX_PORT_IN_FRAME_COUNTER)

#     def get_tx_port_in_true_frame_counter(self):
#         """ Get rx_port_in_true_frame_counter value from RX"""
#         return self.get_tx_counter(field_addr=RB_PORT_TX_PORT_IN_TRUE_FRAME_COUNTER)


#     # Additional methods
#     def get_parameters(self):
#         """Get Port architectural parameters"""
#         return {
#                     "PORT_ID": self.PORT_ID,
#                     "PORT_RATE (Mbps)": self.PORT_RATE,
#                     "READ_WIDTH": self.READ_WIDTH,
#                     "RX_WRITE_WIDTH": self.RX_WRITE_WIDTH,
#                     "TX_WRITE_WIDTH": self.TX_WRITE_WIDTH,                    
#                     "RX_VALID": self.RX_VALID,
#                     "GEN_TRAFFIC_COMMON_COUNT": self.GEN_TRAFFIC_COMMON_COUNT,
#                     "GEN_COUNTER_WIDTH": self.GEN_COUNTER_WIDTH,
#                     "GEN_COUNTER_FRAC_WIDTH": self.GEN_COUNTER_FRAC_WIDTH,
#                     "GEN_MIN_FRAME_LENGTH": self.GEN_MIN_FRAME_LENGTH,
#                     "RX_TRAFFIC_ENABLE": self.RX_TRAFFIC_ENABLE,
#                     "TX_TRAFFIC_ENABLE": self.TX_TRAFFIC_ENABLE,
#                     "GEN_TRAFFIC_ENABLE": self.GEN_TRAFFIC_ENABLE,
#                     "GEN_OUTPUT_REGISTER": self.GEN_OUTPUT_REGISTER
#                 }

#     def show_parameters(self):
#         """Print Port architectural parameters"""
#         for param_str, param_value in self.get_parameters().items():
#             print(f'\t{param_str}: {param_value}')


#     def __str__(self):
#         return self.get_parameters()


# class FCL():
#     _type="FCL"

#     def __init__(self, read_func, write_func, offset: int = 0x0, vc_global_count={0: 4}, prio_count=1):

#         self.read_func = read_func
#         self.write_func = write_func
        
#         self.offset = offset
        
#         self.VC_GLOBAL_COUNT = vc_global_count
#         self.CH_GLOBAL_COUNT = len(vc_global_count)
        
#         self.PRIO_COUNT = prio_count
#         self.prio_width = math.ceil(math.log2(prio_count)) if self.PRIO_COUNT > 1 else 1

#         # Architectural parameters
#         self.FEATURES                   = 0
#         self.CH_COUNT                   = 0
#         self.CH_GLOBAL_OFFSET           = 0
#         self.CH_LOCAL_OFFSET            = 0
#         self.VC_COUNT                   = {}
#         self.PORT_COUNT                 = 0
#         self.RX_FIFO_DEPTH              = 0
#         self.TX_FIFO_DEPTH              = 0
#         self.TABLE_DEPTH                = 0
#         self.TABLE_COUNT                = 0
#         self.TABLE_PRIO_WIDTH           = 0
#         self.TABLE_LOOP_COUNT           = 0
#         self.TABLE_AGING_PERIOD         = 0
#         self.TABLE_AGING_FREQ           = 0
#         self.TABLE_AGING_MAX_PRIO       = 0
#         self.FID_COUNT                  = 0
        
#         self.VLAN_ENABLE                = 0
#         self.STATIC_ENABLE              = 0
#         self.TABLE_PRIO_ENABLE          = 0
#         self.TABLE_AGING_ENABLE         = 0
#         self.TABLE_CONFIG_ENABLE        = 0
#         self.TABLE_REGISTER_STORE_STATE = 0
#         self.VLAN_LEARNING_TYPE         = 0
#         self.LOOPBACK_ENABLE            = 0

#         self.vlan_id_width              = 0
        
#         # static offset
#         self.static_offset = 0

#         # port(s) offset
#         self.port_offset = {}
        
#         # filtering database offset
#         self.fd_offset = 0

#     def initialize(self):
#         """
#         Prepare FCL and its submodules
#         """

#         # Read all constant architectural parameters (non-changing over time)
#         self.FEATURES                   = self.read_conf_int(addr=RB_FCL_FEATURES)
#         self.CH_COUNT                   = self.read_conf_int(addr=RB_FCL_CH_COUNT)
#         self.CH_GLOBAL_OFFSET           = self.read_conf_int(addr=RB_FCL_CH_GLOBAL_OFFSET)
#         self.CH_LOCAL_OFFSET            = self.read_conf_int(addr=RB_FCL_CH_LOCAL_OFFSET)
#         self.PORT_COUNT                 = self.read_conf_int(addr=RB_FCL_PORT_COUNT)
#         self.RX_FIFO_DEPTH              = self.read_conf_int(addr=RB_FCL_RX_FIFO_DEPTH)
#         self.TX_FIFO_DEPTH              = self.read_conf_int(addr=RB_FCL_TX_FIFO_DEPTH)
#         self.TABLE_DEPTH                = self.read_conf_int(addr=RB_FCL_TABLE_DEPTH)
#         self.TABLE_COUNT                = self.read_conf_int(addr=RB_FCL_TABLE_COUNT)
#         self.TABLE_PRIO_WIDTH           = self.read_conf_int(addr=RB_FCL_TABLE_PRIO_WIDTH)
#         self.TABLE_LOOP_COUNT           = self.read_conf_int(addr=RB_FCL_TABLE_LOOP_COUNT)
#         self.TABLE_AGING_PERIOD         = self.read_conf_int(addr=RB_FCL_TABLE_AGING_PERIOD)
#         self.TABLE_AGING_FREQ           = self.read_conf_int(addr=RB_FCL_TABLE_AGING_FREQ)
#         self.TABLE_AGING_MAX_PRIO       = self.read_conf_int(addr=RB_FCL_TABLE_AGING_MAX_PRIO)
#         self.FID_COUNT                  = self.read_conf_int(addr=RB_FCL_FID_COUNT)

#         self.VLAN_ENABLE                = (self.FEATURES & (1 << 0)) >> 0
#         self.STATIC_ENABLE              = (self.FEATURES & (1 << 1)) >> 1
#         self.TABLE_PRIO_ENABLE          = (self.FEATURES & (1 << 2)) >> 2
#         self.TABLE_AGING_ENABLE         = (self.FEATURES & (1 << 3)) >> 3
#         self.TABLE_CONFIG_ENABLE        = (self.FEATURES & (1 << 4)) >> 4
#         self.TABLE_REGISTER_STORE_STATE = (self.FEATURES & (1 << 5)) >> 5
#         self.VLAN_LEARNING_TYPE         = (self.FEATURES & RB_FCL_FEATURE_VLAN_LEARNING_TYPE) >> 6
#         self.LOOPBACK_ENABLE            = (self.FEATURES & RB_FCL_FEATURE_LOOPBACK_ENABLE) >> 8

#         self.VC_COUNT = {(k-int(self.CH_GLOBAL_OFFSET)):v for k, v in self.VC_GLOBAL_COUNT.items() if k >= int(self.CH_GLOBAL_OFFSET) and k < int(self.CH_GLOBAL_OFFSET) + self.CH_COUNT}

#         self.vlan_id_width              = 12 if (not self.VLAN_ENABLE or self.VLAN_LEARNING_TYPE != 2) else (math.ceil(math.log2(self.FID_COUNT)) if self.FID_COUNT > 1 else 1)
        
#         # Read offsets for each submodule
#         self.static_offset = self.read_conf_int(addr=RB_REG_NEXT_PTR)
        
#         self.port_offset[0] = self.read_static_int(addr=RB_REG_NEXT_PTR) if self.STATIC_ENABLE else self.static_offset
#         for i in range(1, self.PORT_COUNT):
#             self.port_offset[i] = self.read_port_int(port=i-1, addr=RB_REG_NEXT_PTR)

#         self.fd_offset = self.read_port_int(port=self.PORT_COUNT-1, addr=RB_REG_NEXT_PTR)


#     # Low level configuration methods
#     def write_int(self, offset: int = 0, addr: int = 0, value: int = 0):
#         write_conf_reg_int(write_func=self.write_func, offset=self.offset + offset, address=addr, data=value)

#     def write_static_int(self, addr: int = 0, value: int = 0):
#         self.write_int(offset=self.static_offset, addr=addr, value=value)
    
#     def write_port_int(self, port: int = 0, addr: int = 0, value: int = 0):
#         self.write_int(offset=self.port_offset[port], addr=addr, value=value)

#     def write_fd_int(self, addr: int = 0, value: int = 0):
#         self.write_int(offset=self.fd_offset, addr=addr, value=value)

#     def write_list(self, offset: int = 0, addr: int = 0, value: list = [0]*8, bits_width:int = 1):
#         write_conf_reg_list(write_func=self.write_func, offset=self.offset + offset, address=addr, data=value, bits_width=bits_width)
        
#     def write_conf_list(self, addr: int = 0, value: list = [0]*8, bits_width:int = 1):
#         self.write_list(offset=0x0, addr=addr, value=value, bits_width=bits_width)

#     def read_int(self, offset: int = 0, addr: int = 0):
#         return read_conf_reg_int(read_func=self.read_func, offset=self.offset + offset, address=addr, length=4)

#     def read_conf_int(self, addr: int = 0):
#         return self.read_int(offset=0x0, addr=addr)

#     def read_static_int(self, addr: int = 0):
#         return self.read_int(offset=self.static_offset, addr=addr)

#     def read_port_int(self, port: int = 0, addr: int = 0):
#         return self.read_int(offset=self.port_offset[port], addr=addr)

#     def read_fd_int(self, addr: int = 0):
#         return self.read_int(offset=self.fd_offset, addr=addr)
    
#     def read_list(self, offset: int = 0, addr: int = 0, count: int = 8, bits_width:int = 1):
#         return read_conf_reg_list(read_func=self.read_func, offset=self.offset + offset, address=addr, length=4, count=count, bits_width=bits_width)
        
#     def read_conf_list(self, addr: int = 0, count: int = 8, bits_width:int = 1):
#         return self.read_list(offset=0x0, addr=addr, count=count, bits_width=bits_width)

    
#     # VLAN configuration
#     def set_vlan(self, vlan_id: int = 0x1, dest_dict:dict = {0:[0]}, active: int = 1):
#         """Create or delete VLAN association"""
#         write_vlan_association(write_func=self.write_func, offset=self.offset+self.static_offset, vlan_id=vlan_id, dest_dict=dest_dict, 
#                                            active=active, vc_global_count=self.VC_GLOBAL_COUNT)

#     def create_vlan(self, vlan_id: int = 0x1, dest_dict:dict = {0:[0]}):
#         """ Create VLAN association"""
#         self.set_vlan(vlan_id=vlan_id, dest_dict=dest_dict, active=1)

#     def delete_vlan(self, vlan_id: int = 0x1):
#         """ Delete VLAN association"""
#         self.set_vlan(vlan_id=vlan_id, active=0)
    

#     # VLAN FID configuration
#     def set_vlan_fid(self, fid:int = 0x1, vlan_id: int = 0x1):
#         """Set VID to FID grouping"""
#         write_vlan_fid_association(write_func=self.write_func, offset=self.offset+self.static_offset, fid=fid, vlan_id=vlan_id, fid_width=self.vlan_id_width)


#     # Address configuration
#     def set_address(self, mac_address: int = 0x0, vlan_id: int = 0x1, dest_dict: dict = {0:[0]}, prio: int = 0x1, active: int = 1):
#         """Create or delete address association"""
#         if not self.VLAN_ENABLE or self.VLAN_LEARNING_TYPE == 0:
#             write_address_association_shared(write_func=self.write_func, offset=self.offset+self.static_offset, mac_address=mac_address, dest_dict=dest_dict, 
#                                             prio=prio, active=active, vc_global_count=self.VC_GLOBAL_COUNT,
#                                             prio_enable=self.TABLE_PRIO_ENABLE, prio_width=self.TABLE_PRIO_WIDTH)
#         elif self.VLAN_LEARNING_TYPE == 1:
#             write_address_association_independent(write_func=self.write_func, offset=self.offset+self.static_offset, mac_address=mac_address, vlan_id=vlan_id, 
#                                             dest_dict=dest_dict, prio=prio, active=active, vc_global_count=self.VC_GLOBAL_COUNT, 
#                                             prio_enable=self.TABLE_PRIO_ENABLE, prio_width=self.TABLE_PRIO_WIDTH)
#         else:
#             write_address_association_mixed(write_func=self.write_func, offset=self.offset+self.static_offset, mac_address=mac_address, vlan_id=vlan_id,
#                                             vlan_id_width=self.vlan_id_width, dest_dict=dest_dict, prio=prio, active=active, 
#                                             vc_global_count=self.VC_GLOBAL_COUNT, prio_enable=self.TABLE_PRIO_ENABLE, prio_width=self.TABLE_PRIO_WIDTH)       

#     def create_address(self, mac_address: int = 0x0, vlan_id: int = 0x1, dest_dict: dict = {0:[0]}, prio: int = 0x1):
#         """ Create address association"""
#         self.set_address(mac_address=mac_address, vlan_id=vlan_id, dest_dict=dest_dict, prio=prio, active=1)

#     def delete_address(self, mac_address: int = 0x0, vlan_id: int = 0x1):
#         """ Delete address association"""
#         self.set_address(mac_address=mac_address, vlan_id=vlan_id, active=0)

#     def get_address(self, mac_address: int = 0x0, vlan_id: int = 0x1):
#         """ Get address association"""
#         if not self.VLAN_ENABLE or self.VLAN_LEARNING_TYPE == 0:
#             return read_address_association_shared(write_func=self.write_func, read_func=self.read_func, offset=self.offset+self.static_offset, mac_address=mac_address, 
#                                             vc_global_count=self.VC_GLOBAL_COUNT)
#         elif self.VLAN_LEARNING_TYPE == 1:
#             return read_address_association_independent(write_func=self.write_func, read_func=self.read_func, offset=self.offset+self.static_offset, mac_address=mac_address, vlan_id=vlan_id, 
#                                             vc_global_count=self.VC_GLOBAL_COUNT)
#         else:
#             return read_address_association_mixed(write_func=self.write_func, read_func=self.read_func, offset=self.offset+self.static_offset, mac_address=mac_address, vlan_id=vlan_id,
#                                             vlan_id_width=self.vlan_id_width, vc_global_count=self.VC_GLOBAL_COUNT)               


#     # Egress VLAN tagging configuration
#     def set_egress_tag(self, vlan_id: int = 0x1, dest_dict:dict = {0:[0]}):
#         """Create or delete egress VLAN tagging"""
#         write_vlan_egress_tag_association(write_func=self.write_func, offset=self.offset+self.static_offset, vlan_id=vlan_id, dest_dict=dest_dict,
#                                             ch_count=self.CH_COUNT, vc_count = self.VC_COUNT)
        
#     def create_egress_tag(self, vlan_id: int = 0x1, dest_dict:dict = {0:[0]}):
#         """ Create egress VLAN tagging"""
#         self.set_egress_tag(vlan_id=vlan_id, dest_dict=dest_dict)

#     def delete_egress_tag(self, vlan_id: int = 0x1):
#         """ Delete egress VLAN tagging"""
#         self.set_egress_tag(vlan_id=vlan_id, dest_dict={})


#     # Port configuration
#     def set_ppcp(self, port: int = 0, value: int = 0):
#         """Set default priority for specified port"""
#         self.write_port_int(port=port, addr=RB_FCL_PORT_PPCP, value=value)

#     def set_pvid(self, port: int = 0, value: int = 0):
#         """Set default VLAN ID for specified port"""
#         self.write_port_int(port=port, addr=RB_FCL_PORT_PVID, value=value)

#     def set_ingress_filtering(self, port: int = 0, value: int = 0):
#         """Set VLAN filtering for specified port"""
#         self.write_port_int(port=port, addr=RB_FCL_PORT_INGRESS_FILT, value=value)

#     def enable_ingress_filtering(self, port: int = 0):
#         """Enable VLAN filtering for specified port"""
#         self.set_ingress_filtering(port=port, value=1)

#     def disable_ingress_filtering(self, port: int = 0):
#         """Disable VLAN filtering for specified port"""
#         self.set_ingress_filtering(port=port, value=0)

#     def set_loopback_mode(self, port: int = 0, value: int = 0):
#         """Set loopback mode for specified port"""
#         self.write_port_int(port=port, addr=RB_FCL_PORT_LOOPBACK, value=value)

#     def enable_loopback_mode(self, port: int = 0):
#         """Enable loopback mode for specified port"""
#         self.set_loopback_mode(port=port, value=1)

#     def disable_loopback_mode(self, port: int = 0):
#         """Disable loopback mode for specified port"""
#         self.set_loopback_mode(port=port, value=0)

#     def set_port_lookup_counter(self, port: int = 0, value: int = 0):
#         """Set lookup operation counter for specified port"""
#         self.write_port_int(port=port, addr=RB_FCL_PORT_LOOKUP_COUNTER, value=value)

#     def set_port_write_counter(self, port: int = 0, value: int = 0):
#         """Set write operation counter for specified port"""
#         self.write_port_int(port=port, addr=RB_FCL_PORT_WRITE_COUNTER, value=value)

#     def get_ppcp(self, port: int = 0):
#         """Get default priority for specified port"""
#         return self.read_port_int(port=port, addr=RB_FCL_PORT_PPCP)

#     def get_pvid(self, port: int = 0):
#         """Get default VLAN ID for specified port"""
#         return self.read_port_int(port=port, addr=RB_FCL_PORT_PVID)

#     def get_ingress_filtering(self, port: int = 0):
#         """Get status of VLAN ingress filtering for specified port"""
#         return self.read_port_int(port=port, addr=RB_FCL_PORT_INGRESS_FILT)

#     def get_loopback_mode(self, port: int = 0):
#         """Get status of loopback mode for specified port"""
#         return self.read_port_int(port=port, addr=RB_FCL_PORT_LOOPBACK)

#     def get_rx_in_counter_port(self, port: int = 0):
#         """Get RX in frame counter for specified port"""
#         return self.read_port_int(port=port, addr=RB_FCL_PORT_RX_IN_COUNTER)

#     def get_rx_in_drop_counter_port(self, port: int = 0):
#         """Get RX in drop frame counter for specified port"""
#         return self.read_port_int(port=port, addr=RB_FCL_PORT_RX_IN_DROP_COUNTER)

#     def get_tx_out_counter_port(self, port: int = 0):
#         """Get TX out frame counter for specified port"""
#         return self.read_port_int(port=port, addr=RB_FCL_PORT_TX_OUT_COUNTER)

#     def get_lookup_counter_port(self, port: int = 0):
#         """Get lookup operation counter for specified port"""
#         return self.read_port_int(port=port, addr=RB_FCL_PORT_LOOKUP_COUNTER)

#     def get_write_counter_port(self, port: int = 0):
#         """Get write operation counter for specified port"""
#         return self.read_port_int(port=port, addr=RB_FCL_PORT_WRITE_COUNTER)


#     # FCL configuration
#     def set_prio_map(self, value: dict = {pcp:0 for pcp in range(8)}):
#         """Set PCP to priority mapping"""
#         value_list = list(dict(sorted(value.items())).values())
#         self.write_conf_list(addr=RB_FCL_PRIO_MAP, value=value_list, bits_width=self.prio_width)

#     def get_prio_map(self):
#         """Get PCP to priority mapping"""
#         return self.read_conf_list(addr=RB_FCL_PRIO_MAP, count=8, bits_width=self.prio_width)


#     # FD configuration
#     def set_acc_util_fd(self, value: int = 0):
#         """Set accelerated threshold utilization for aging of MAC address table"""
#         self.write_fd_int(addr=RB_FD_ACC_UTIL, value=value)

#     def set_min_util_fd(self, value: int = 0):
#         """Set minimum threshold utilization for aging of MAC address table"""
#         self.write_fd_int(addr=RB_FD_MIN_UTIL, value=value)

#     def set_max_util_fd(self, value: int = 0):
#         """Set maximum threshold utilization for aging of MAC address table"""
#         self.write_fd_int(addr=RB_FD_MAX_UTIL, value=value)

#     def set_period_aging_fd(self, value: int = 0):
#         """Set period of aging of MAC address table"""
#         self.write_fd_int(addr=RB_FD_PERIOD_AGING, value=value)
    
#     def set_freq_aging_fd(self, value: int = 0):
#         """Set frequency of aging of MAC address table"""
#         self.write_fd_int(addr=RB_FD_FREQ_AGING, value=value)

#     def set_config_depth_mask_fd(self, value: int = 0):
#         """Set depth mask of each parallel table of the MAC address table"""
#         self.write_fd_int(addr=RB_FD_CONFIG_DEPTH_MASK, value=value)

#     def set_config_table_count_fd(self, value: int = 0):
#         """Set active number of tables of the MAC address table"""
#         self.write_fd_int(addr=RB_FD_CONFIG_TABLE_COUNT, value=value)

#     def set_config_max_util_fd(self, value: int = 0):
#         """Set maximum number of entries (utilization) of the MAC address table"""
#         self.write_fd_int(addr=RB_FD_CONFIG_MAX_UTIL, value=value)

#     def set_max_loop_hit_util(self, value: int = 0):
#         """Set register with number of entries inside the MAC address table before the first hit of LOOP_COUNT: use for resetting the capture (setting value 0)"""
#         self.write_fd_int(addr=RB_FD_CONFIG_MAX_LOOP_HIT_UTIL, value=value)

#     def set_config_max_loop_count_fd(self, value: int = 0):
#         """Set maximum number of iterations for an insertion (LOOP_COUNT) of the MAC address table"""
#         self.write_fd_int(addr=RB_FD_CONFIG_MAX_LOOP_COUNT, value=value)

#     def clear_mac_table_fd(self):
#         """Clear MAC address table"""
#         self.write_fd_int(addr=RB_FD_CLEAR, value=RB_FD_CLEAR_ADDRESS)

#     def clear_vlan_table_fd(self):
#         """Clear VLAN table"""
#         self.write_fd_int(addr=RB_FD_CLEAR, value=RB_FD_CLEAR_VLAN)

#     def clear_tag_table_fd(self):
#         """Clear tag table"""
#         self.write_fd_int(addr=RB_FD_CLEAR, value=RB_FD_CLEAR_TAG)

#     def clear_fid_table_fd(self):
#         """Clear fid table"""
#         self.write_fd_int(addr=RB_FD_CLEAR, value=RB_FD_CLEAR_FID)

#     def get_util_fd(self):
#         """Get current utilization of MAC address table"""
#         return self.read_fd_int(addr=RB_FD_CURR_UTIL)

#     def get_util_t0_fd(self):
#         """Get current utilization of table 0 of  MAC address table"""
#         return self.read_fd_int(addr=RB_FD_CURR_UTIL_T0)

#     def get_util_t1_fd(self):
#         """Get current utilization of table 1 of  MAC address table"""
#         return self.read_fd_int(addr=RB_FD_CURR_UTIL_T1)

#     def get_util_t2_fd(self):
#         """Get current utilization of table 2 of  MAC address table"""
#         return self.read_fd_int(addr=RB_FD_CURR_UTIL_T2)

#     def get_util_t3_fd(self):
#         """Get current utilization of table 3 of  MAC address table"""
#         return self.read_fd_int(addr=RB_FD_CURR_UTIL_T3)

#     def get_util_t4_fd(self):
#         """Get current utilization of table 4 of  MAC address table"""
#         return self.read_fd_int(addr=RB_FD_CURR_UTIL_T4)

#     def get_acc_util_fd(self):
#         """Get current accelerated threshold utilization for aging of MAC address table"""
#         return self.read_fd_int(addr=RB_FD_ACC_UTIL)

#     def get_min_util_fd(self):
#         """Get current minimum threshold utilization for aging of MAC address table"""
#         return self.read_fd_int(addr=RB_FD_MIN_UTIL)

#     def get_max_util_fd(self):
#         """Get current maximum threshold utilization for aging of MAC address table"""
#         return self.read_fd_int(addr=RB_FD_MAX_UTIL)

#     def get_period_aging_fd(self):
#         """Get current period for aging of MAC address table"""
#         return self.read_fd_int(addr=RB_FD_PERIOD_AGING)
    
#     def get_freq_aging_fd(self):
#         """Get current frequency for aging of MAC address table"""
#         return self.read_fd_int(addr=RB_FD_FREQ_AGING)

#     def get_config_depth_mask_fd(self):
#         """Get current depth mask of each parallel table of the MAC address table"""
#         return self.read_fd_int(addr=RB_FD_CONFIG_DEPTH_MASK)

#     def get_config_table_count_fd(self):
#         """Get current active number of parallel tables of the MAC address table"""
#         return self.read_fd_int(addr=RB_FD_CONFIG_TABLE_COUNT)

#     def get_config_max_util_fd(self):
#         """Get current maximum utilization of the MAC address table"""
#         return self.read_fd_int(addr=RB_FD_CONFIG_MAX_UTIL)

#     def get_config_max_util_tx_out_counter_fd(self):
#         """Get counter with number of frames needed for reaching the maximum utilization (set_config_max_util_fd) of the MAC address table"""
#         return self.read_fd_int(addr=RB_FD_CONFIG_MAX_UTIL_TX_OUT_COUNTER)

#     def get_max_loop_hit_util_fd(self):
#         """Get number of entries inside the MAC address table before the first hit of LOOP_COUNT (like infinite loop)"""
#         return self.read_fd_int(addr=RB_FD_CONFIG_MAX_LOOP_HIT_UTIL)

#     def get_max_loop_hit_counter_fd(self):
#         """Get counter of number times that the LOOP_COUNT threshold has been reach during insertions (like infinite loop)"""
#         return self.read_fd_int(addr=RB_FD_MAX_LOOP_HIT_COUNTER)

#     def get_config_max_loop_count_fd(self):
#         """Get maximum number of iterations for an insertion (LOOP_COUNT) of the MAC address table"""
#         return self.read_fd_int(addr=RB_FD_CONFIG_MAX_LOOP_COUNT)


#     # Static port configuration
#     def get_static_address_write_counter(self):
#         """Get address write operation counter using static port"""
#         return self.read_static_int(RB_FCL_STATIC_ADDRESS_ACTIVE_COUNTER)

#     def get_static_address_delete_counter(self):
#         """Get address delete operation counter using static port"""
#         return self.read_static_int(RB_FCL_STATIC_ADDRESS_DELETE_COUNTER)
    
#     def get_static_vlan_write_counter(self):
#         """Get VLAN write operation counter using static port"""
#         return self.read_static_int(RB_FCL_STATIC_VLAN_ACTIVE_COUNTER)

#     def get_static_vlan_delete_counter(self):
#         """Get VLAN delete operation counter using static port"""
#         return self.read_static_int(RB_FCL_STATIC_VLAN_DELETE_COUNTER)

#     def get_static_address_write_status(self):
#         """Get address write/delete operation status for static port"""
#         return self.read_static_int(RB_FCL_STATIC_ADDRESS_VALID)

#     def get_static_vlan_write_status(self):
#         """Get VLAN write/delete operation status for static port"""
#         return self.read_static_int(RB_FCL_STATIC_VLAN_VALID)

#     def get_static_tag_write_status(self):
#         """Get Tag write operation status for static port"""
#         return self.read_static_int(RB_FCL_STATIC_TAG_VALID)

#     def get_static_fid_write_status(self):
#         """Get FID write operation status for static port"""
#         return self.read_static_int(RB_FCL_STATIC_FID_VALID)

#     # Additional methods
#     def get_parameters(self):
#         """Get FCL architectural parameters"""
#         return {
#                     "CH_COUNT": self.CH_COUNT,
#                     "CH_GLOBAL_OFFSET": self.CH_GLOBAL_OFFSET,
#                     "CH_LOCAL_OFFSET": self.CH_LOCAL_OFFSET,
#                     "PORT_COUNT": self.PORT_COUNT,
#                     "VC_COUNT": self.VC_COUNT,
#                     "RX_FIFO_DEPTH": self.RX_FIFO_DEPTH,
#                     "TX_FIFO_DEPTH": self.TX_FIFO_DEPTH,
#                     "TABLE_DEPTH": self.TABLE_DEPTH,
#                     "TABLE_COUNT": self.TABLE_COUNT,
#                     "TABLE_PRIO_WIDTH": self.TABLE_PRIO_WIDTH,
#                     "TABLE_LOOP_COUNT": self.TABLE_LOOP_COUNT,
#                     "TABLE_AGING_PERIOD": self.TABLE_AGING_PERIOD,
#                     "TABLE_AGING_FREQ": self.TABLE_AGING_FREQ,
#                     "TABLE_AGING_MAX_PRIO": self.TABLE_AGING_MAX_PRIO,
#                     "FID_COUNT": self.FID_COUNT,
#                     "VLAN_ENABLE": self.VLAN_ENABLE,
#                     "STATIC_ENABLE": self.STATIC_ENABLE,
#                     "TABLE_PRIO_ENABLE": self.TABLE_PRIO_ENABLE,
#                     "TABLE_AGING_ENABLE": self.TABLE_AGING_ENABLE,
#                     "TABLE_CONFIG_ENABLE": self.TABLE_CONFIG_ENABLE,
#                     "TABLE_REGISTER_STORE_STATE": self.TABLE_REGISTER_STORE_STATE,
#                     "VLAN_LEARNING_TYPE": VLAN_LEARNING_TYPE_DICT[self.VLAN_LEARNING_TYPE],
#                     "LOOPBACK_ENABLE": self.LOOPBACK_ENABLE
#                 }


#     def show_parameters(self):
#         """Print FCL architectural parameters"""
#         for param_str, param_value in self.get_parameters().items():
#             print(f'\t{param_str}: {param_value}')


#     def __str__(self):
#         return self.get_parameters()


# class EthernetSwitch():
#     _type = "EthernetSwitch"

#     def __init__(self, read_func, write_func, offset:int = 0x0, vc_count:dict = {0:4}, fcl_x_ch_count:dict = {0:1}, 
#                  row_x_fcl_count:dict = {0:1}, col_x_fcl_count:dict = {0:1}, fcl_offset:int = 0x0, fcl_stride:int = 2**12, 
#                  prio_count:int = 1, drop_corrupted_frames:int = 1, egress_pipeline_register:int = 1, ingress_fifo_depth:int = 32,
#                  egress_fifo_depth:int = 16):

#         self.read_func = read_func
#         self.write_func = write_func

#         self.offset = offset

#         self.CH_COUNT = len(vc_count)
#         self.VC_COUNT = vc_count
#         self.PORT_COUNT = sum(list(vc_count.values()))

#         self.FCL_COUNT = len(fcl_x_ch_count)
#         self.ROW_COUNT = len(row_x_fcl_count)
#         self.COL_COUNT = len(col_x_fcl_count)

#         self.fcl_x_ch_count = fcl_x_ch_count
#         self.row_x_fcl_count = row_x_fcl_count
#         self.col_x_fcl_count = col_x_fcl_count

#         self.fcl_offset = fcl_offset
#         self.fcl_stride = fcl_stride
        
#         self.PRIO_COUNT = prio_count
#         self.DROP_CORRUPTED_FRAMES = drop_corrupted_frames
#         self.EGRESS_PIPELINE_REGISTER = egress_pipeline_register
#         self.INGRESS_FIFO_DEPTH = ingress_fifo_depth
#         self.EGRESS_FIFO_DEPTH = egress_fifo_depth

#         # Prepare FCL and port mapping attributes
#         self.fcl_dict = {fcl:None for fcl in range(self.FCL_COUNT)}
#         self.ch_x_fcl = {}
#         self.ch_vc_x_fcl = {}
#         self.port_x_fcl = {}
#         self.port_global_x_port_local = {}
#         self.fcl_x_ch_list = {}
#         self.port_x_ch_vc = {}

#         # Port (modules) attrbutes
#         self.port_dict = {}
#         self.port_module_offset = {}
#         self.port_module_count = 0
#         self.port_stride = 0

#         self.register_size = 32
#         self.register_max = 2**self.register_size
        
#         # Prepare attributes for statistics and configuration
#         self.fd_util = {fcl:0 for fcl in range(self.FCL_COUNT)}
#         self.fd_acc_util = {fcl:0 for fcl in range(self.FCL_COUNT)}
#         self.fd_min_util = {fcl:0 for fcl in range(self.FCL_COUNT)}
#         self.fd_max_util = {fcl:0 for fcl in range(self.FCL_COUNT)}
#         self.fd_period_aging = {fcl:0 for fcl in range(self.FCL_COUNT)}
#         self.fd_freq_aging = {fcl:0 for fcl in range(self.FCL_COUNT)}

#         self.port_ppcp = {port:0 for port in range(self.PORT_COUNT)}
#         self.port_pvid = {port:0 for port in range(self.PORT_COUNT)}
#         self.port_lookup_counter = {port:0 for port in range(self.PORT_COUNT)}
#         self.port_write_counter = {port:0 for port in range(self.PORT_COUNT)}
        
#         # Initilization and connection
#         self.run_run = False


#     def initialize(self):
#         """
#         Prepare modules belonging to the switch
#         """

#         # Prepare a bunch of useful attributes
#         # list of channels belonging to each FCL
        
        
#         # Read some registers
        
        
#         # Instantiate FCL modules
#         self.fcl_dict = {fcl:FCL(read_func=self.read_func, write_func=self.write_func, offset=self.offset + self.fcl_offset + self.fcl_stride*fcl, 
#                             vc_global_count=self.VC_COUNT, prio_count=self.PRIO_COUNT) for fcl in range(self.FCL_COUNT)}

#         # Get relation between channels and FCL modules and initialize FCLs
#         for i in range(self.FCL_COUNT):
#             fcl = self.fcl_dict[i]
#             fcl.initialize()
#             # dicts for mapping a channel, virtual channel and port to an FCL (fcl to ch mapping)
#             for ch in range(fcl.CH_COUNT):
#                 self.ch_x_fcl[ch + fcl.CH_GLOBAL_OFFSET] = i

#                 port_global_offset = sum(list(self.VC_COUNT.values())[:ch + fcl.CH_GLOBAL_OFFSET])
#                 port_local_offset = sum(list(self.VC_COUNT.values())[fcl.CH_GLOBAL_OFFSET:ch + fcl.CH_GLOBAL_OFFSET])
#                 self.ch_vc_x_fcl[ch + fcl.CH_GLOBAL_OFFSET] = {}
#                 for vc in range(self.VC_COUNT[ch + fcl.CH_GLOBAL_OFFSET]):
#                     self.ch_vc_x_fcl[ch + fcl.CH_GLOBAL_OFFSET][vc] = i
#                     self.port_x_fcl[port_global_offset + vc] = i
#                     # dict for mapping a global port to a local port inside an FCL
#                     self.port_global_x_port_local[port_global_offset + vc] = port_local_offset + vc
#                     # dict for mapping a global port to a channel and virtual channel
#                     self.port_x_ch_vc[port_global_offset + vc] = (ch + fcl.CH_GLOBAL_OFFSET, vc)
            
#             # dict for mapping an FCL to a set of channels
#             self.fcl_x_ch_list[i] = list(range(fcl.CH_GLOBAL_OFFSET, fcl.CH_GLOBAL_OFFSET + fcl.CH_COUNT))
        
#         self.ready = True


#     @classmethod
#     def fromRegisters(cls, write_func, read_func, offset: int = 0x0):
#         """
#         Switch initializatin by reading from its RB control registers
#         """

#         ch_count = read_conf_reg_int(read_func=read_func, offset=offset, address=RB_SWITCH_CH_GLOBAL_COUNT, length=4)
#         fcl_count = read_conf_reg_int(read_func=read_func, offset=offset, address=RB_SWITCH_FCL_COUNT, length=4)
#         row_count = read_conf_reg_int(read_func=read_func, offset=offset, address=RB_SWITCH_ROW_COUNT, length=4)
#         col_count = read_conf_reg_int(read_func=read_func, offset=offset, address=RB_SWITCH_COL_COUNT, length=4)
#         fcl_offset = read_conf_reg_int(read_func=read_func, offset=offset, address=RB_SWITCH_FCL_OFFSET, length=4)
#         fcl_stride = read_conf_reg_int(read_func=read_func, offset=offset, address=RB_SWITCH_FCL_STRIDE, length=4)
#         vc_count_offset = read_conf_reg_int(read_func=read_func, offset=offset, address=RB_SWITCH_VC_GLOBAL_COUNT_OFFSET, length=4)
#         fcl_x_ch_count_offset = read_conf_reg_int(read_func=read_func, offset=offset, address=RB_SWITCH_FCL_X_CH_COUNT_OFFSET, length=4)
#         row_x_fcl_count_offset = read_conf_reg_int(read_func=read_func, offset=offset, address=RB_SWITCH_ROW_X_FCL_COUNT_OFFSET, length=4)
#         col_x_fcl_count_offset = read_conf_reg_int(read_func=read_func, offset=offset, address=RB_SWITCH_COL_X_FCL_COUNT_OFFSET, length=4)

#         # build dictionaries
#         vc_count = {}
#         for i in range(ch_count):
#             vc_count[i] = read_conf_reg_int(read_func=read_func, offset=offset, address=vc_count_offset + i*4 , length=4)

#         fcl_x_ch_count = {}
#         for i in range(fcl_count):
#             fcl_x_ch_count[i] = read_conf_reg_int(read_func=read_func, offset=offset, address=fcl_x_ch_count_offset + i*4 , length=4)
        
#         row_x_fcl_count = {}
#         for i in range(row_count):
#             row_x_fcl_count[i] = read_conf_reg_int(read_func=read_func, offset=offset, address=row_x_fcl_count_offset + i*4 , length=4)
        
#         col_x_fcl_count = {}
#         for i in range(col_count):
#             col_x_fcl_count[i] = read_conf_reg_int(read_func=read_func, offset=offset, address=col_x_fcl_count_offset + i*4 , length=4)

#         prio_count = read_conf_reg_int(read_func=read_func, offset=offset, address=RB_SWITCH_PRIO_COUNT, length=4)
#         drop_corrupted_frames = read_conf_reg_int(read_func=read_func, offset=offset, address=RB_SWITCH_DROP_CORRUPTED_FRAMES, length=4)
#         egress_pipeline_register = read_conf_reg_int(read_func=read_func, offset=offset, address=RB_SWITCH_EGRESS_PIPELINE_REGISTER, length=4)
#         ingress_fifo_depth = read_conf_reg_int(read_func=read_func, offset=offset, address=RB_SWITCH_INGRESS_FIFO_DEPTH, length=4)
#         egress_fifo_depth = read_conf_reg_int(read_func=read_func, offset=offset, address=RB_SWITCH_EGRESS_FIFO_DEPTH, length=4)

#         self = cls(read_func=read_func, write_func=write_func, offset=offset, vc_count=vc_count, fcl_x_ch_count=fcl_x_ch_count, 
#             row_x_fcl_count=row_x_fcl_count, col_x_fcl_count=col_x_fcl_count, fcl_offset=fcl_offset, fcl_stride=fcl_stride, 
#             prio_count=prio_count, drop_corrupted_frames=drop_corrupted_frames, egress_pipeline_register=egress_pipeline_register,
#             ingress_fifo_depth=ingress_fifo_depth, egress_fifo_depth=egress_fifo_depth)
    
#         self.initialize()

#         return self


#     # Port module configuration
#     def discover_port_modules(self, port_offset: int = 0x0, port_stride: int = 0x100, port_count: int = 0x0, port_id_offset: int = 0):
#         """
#         Discover port modules belonging to the switch
#         """

#         # Port registers
#         self.port_module_count = port_count
#         self.port_stride = port_stride

#         # Instantiate port modules
#         if self.port_module_count:
#             for i in range(self.port_module_count):
#                 port = Port(write_func=self.write_func, read_func=self.read_func, offset=port_offset + i*self.port_stride)
#                 port.initialize()
#                 self.port_dict[port.PORT_ID - port_id_offset] = port
#                 self.port_module_offset[port.PORT_ID - port_id_offset] = port_offset + i*self.port_stride

#     def set_rx_mac_mux(self):
#         """Set RX side from MAC as multiplexing for RX for all port modules"""
#         for port in self.port_dict.values():
#             port.set_rx_mac_mux()

#     def set_rx_gen_mux(self):
#         """Set taffic generator as multiplexing for RX for all port modules"""
#         for port in self.port_dict.values():
#             port.set_rx_gen_mux()

#     def set_rx_null_mux(self):
#         """Set null as multiplexing for RX for all port modules"""
#         for port in self.port_dict.values():
#             port.set_rx_null_mux()

#     def set_tx_mac_mux(self):
#         """Set TX side from MAC as multiplexing for TX for all port modules"""
#         for port in self.port_dict.values():
#             port.set_tx_mac_mux()

#     def set_tx_null_mux(self):
#         """Set null as multiplexing for TX for all port modules"""
#         for port in self.port_dict.values():
#             port.set_tx_null_mux()


#     # VLAN configuration: configure and delete
#     def create_vlan_fcl(self, fcl: int = 0, vlan_id: int = 0x1, dest_dict:dict = {0:[0]}):
#         """Create VLAN association for specified FCL"""
#         self.fcl_dict[fcl].create_vlan(vlan_id=vlan_id, dest_dict=dest_dict)

#     def create_vlan(self, vlan_id: int = 0x1, dest_dict:dict = {0:[0]}):
#         """Create VLAN association for all FCLs"""
#         for fcl in range(self.FCL_COUNT):
#             self.create_vlan_fcl(fcl=fcl, vlan_id=vlan_id, dest_dict=dest_dict)

#     def delete_vlan_fcl(self, fcl: int = 0, vlan_id: int = 0x1):
#         """Delete VLAN association for specified FCL"""
#         self.fcl_dict[fcl].delete_vlan(vlan_id=vlan_id, dest_width=self.PORT_COUNT)

#     def delete_vlan(self, vlan_id: int = 0x1):
#         """Delete VLAN association for all FCLs"""
#         for fcl in range(self.FCL_COUNT):
#             self.delete_vlan(fcl=fcl, vlan_id=vlan_id)
            
#     def get_vlan_fcl(self, fcl: int = 0, vlan_id: int = 0x0):
#         """Get VLAN configuration (and VID/FID) for specified FCL"""
#         address_dest_dict, address_error, vlan_dest_dict, vlan_error = self.fcl_dict[fcl].get_address(mac_address=0x0, vlan_id=vlan_id)

#         return vlan_dest_dict, vlan_error


#     # VLAN FID configuration
#     def set_vlan_fid_fcl(self, fcl:int = 0, fid:int = 0x1, vlan_id: int = 0x1):
#         """Set VID to FID grouping for the specified FCL"""
#         self.fcl_dict[fcl].set_vlan_fid(fid=fid, vlan_id=vlan_id)

#     def set_vlan_fid(self, fid:int = 0x1, vlan_id: int = 0x1):
#         """Set VID to FID grouping for the all FCLs"""
#         for fcl in range(self.FCL_COUNT):
#             self.set_vlan_fid_fcl(fcl=fcl, fid=fid, vlan_id=vlan_id)


#     # Address associations (destination MAC address and port(s)) configuration: add and delete
#     def create_address_fcl(self, fcl: int = 0, mac_address: int = 0x0, vlan_id: int = 0x0, 
#                                 dest_dict: dict = {0:[0]}, prio: int = 0x0):
#         """Create MAC address to ports association for specified FCL"""
#         self.fcl_dict[fcl].create_address(mac_address=mac_address, vlan_id=vlan_id, dest_dict=dest_dict, prio=prio)

#     def create_address(self, mac_address: int = 0x0, vlan_id: int = 0x0, 
#                                 dest_dict: dict = {0:[0]}, prio: int = 0x0):
#         """Create MAC address to ports association for all FCL"""
#         for fcl in range(self.FCL_COUNT):
#             self.create_address_fcl(fcl=fcl, mac_address=mac_address, vlan_id=vlan_id, dest_dict=dest_dict, prio=prio)

#     def delete_address_fcl(self, fcl: int = 0, mac_address: int = 0x0, vlan_id: int = 0x1):
#         """Delete MAC address to ports association for specified FCL"""
#         self.fcl_dict[fcl].delete_address(mac_address=mac_address, vlan_id=vlan_id)

#     def delete_address(self, mac_address: int = 0x0, vlan_id: int = 0x1):
#         """Delete MAC address to ports association for all FCL"""
#         for fcl in range(self.FCL_COUNT):
#             self.delete_address_fcl(fcl=fcl, mac_address=mac_address, vlan_id=vlan_id)

#     def get_address_fcl(self, fcl: int = 0, mac_address: int = 0x0, vlan_id: int = 0x0):
#         """Get ports associated with a MAC address (and VID/FID) for specified FCL"""
#         address_dest_dict, address_error, vlan_dest_dict, vlan_error =  self.fcl_dict[fcl].get_address(mac_address=mac_address, vlan_id=vlan_id)

#         return address_dest_dict, address_error


#     # Egress VLAN tagging association
#     def create_egress_tag_fcl(self, fcl: int = 0, vlan_id: int = 0x1, dest_dict:dict = {0:[0]}):
#         """Create egress VLAN tagging for specified FCL"""
#         self.fcl_dict[fcl].create_egress_tag(vlan_id=vlan_id, dest_dict=dest_dict)

#     def create_egress_tag(self, vlan_id: int = 0x1, dest_dict:dict = {0:[0]}):
#         """Create egress VLAN tagging for all FCLs"""
#         for fcl in range(self.FCL_COUNT):
#             self.create_egress_tag_fcl(fcl=fcl, vlan_id=vlan_id, dest_dict=dest_dict)

#     def delete_egress_tag_fcl(self, fcl: int = 0, vlan_id: int = 0x1):
#         """Create egress VLAN tagging for specified FCL"""
#         self.fcl_dict[fcl].delete_egress_tag(vlan_id=vlan_id)

#     def delete_egress_tag(self, vlan_id: int = 0x1):
#         """Create egress VLAN tagging association for all FCLs"""
#         for fcl in range(self.FCL_COUNT):
#             self.delete_egress_tag_fcl(fcl=fcl, vlan_id=vlan_id)


#     # Port configuration
#     def set_ppcp_port(self, port: int = 0, value: int = 0):
#         """Set default priority for specified port"""
#         self.fcl_dict[self.port_x_fcl[port]].set_ppcp(port=self.port_global_x_port_local[port], value=value)

#     def set_ppcp(self, value: int = 0):
#         """Set default priority for all ports"""
#         for port in range(self.PORT_COUNT):
#             self.set_ppcp_port(port=port, value=value)

#     def set_pvid_port(self, port: int = 0, value: int = 0):
#         """Set default VLAN ID for specified port"""
#         self.fcl_dict[self.port_x_fcl[port]].set_pvid(port=self.port_global_x_port_local[port], value=value)

#     def set_pvid(self, value: int = 0):
#         """Set default VLAN ID for all ports"""
#         for port in range(self.PORT_COUNT):
#             self.set_pvid_port(port=port, value=value)

#     def enable_ingress_filtering_port(self, port: int = 0):
#         """Enable VLAN ingress filtering for specified port"""
#         self.fcl_dict[self.port_x_fcl[port]].enable_ingress_filtering(port=self.port_global_x_port_local[port])

#     def enable_ingress_filtering(self):
#         """Enable VLAN ingress filtering for all ports"""
#         for port in range(self.PORT_COUNT):
#             self.enable_ingress_filtering_port(port=port)

#     def disable_ingress_filtering_port(self, port: int = 0):
#         """Disable VLAN ingress filtering for specified port"""
#         self.fcl_dict[self.port_x_fcl[port]].disable_ingress_filtering(port=self.port_global_x_port_local[port])

#     def disable_ingress_filtering(self):
#         """Disable VLAN ingress filtering for all ports"""
#         for port in range(self.PORT_COUNT):
#             self.disable_ingress_filtering_port(port=port)

#     def enable_loopback_mode_port(self, port: int = 0):
#         """Enable loopback mode for specified port"""
#         self.fcl_dict[self.port_x_fcl[port]].enable_loopback_mode(port=self.port_global_x_port_local[port])

#     def enable_loopback_mode(self):
#         """Enable loopback mode for all ports"""
#         for port in range(self.PORT_COUNT):
#             self.enable_loopback_mode_port(port=port)

#     def disable_loopback_mode_port(self, port: int = 0):
#         """Disable loopback mode for specified port"""
#         self.fcl_dict[self.port_x_fcl[port]].disable_loopback_mode(port=self.port_global_x_port_local[port])

#     def disable_loopback_mode(self):
#         """Disable loopback mode for all ports"""
#         for port in range(self.PORT_COUNT):
#             self.disable_loopback_mode_port(port=port)

#     def set_port_lookup_counter_port(self, port: int = 0, value: int = 0):
#         """Set lookup operation counter for specified port"""
#         self.fcl_dict[self.port_x_fcl[port]].set_port_lookup_counter(port=self.port_global_x_port_local[port], value=value)

#     def set_port_lookup_counter(self, value: int = 0):
#         """Set lookup operation counter for all ports"""
#         for port in range(self.PORT_COUNT):
#             self.set_port_lookup_counter_port(port=port, value=value)

#     def set_port_write_counter_port(self, port: int = 0, value: int = 0):
#         """Set write operation counter for specified port"""
#         self.fcl_dict[self.port_x_fcl[port]].set_port_write_counter(port=self.port_global_x_port_local[port], value=value)

#     def set_port_write_counter(self, value: int = 0):
#         """Set write operation counter for all ports"""
#         for port in range(self.PORT_COUNT):
#             self.set_port_write_counter_port(port=port, value=value)

#     def get_ppcp_port(self, port: int = 0):
#         """Get default priority for specified port"""
#         return self.fcl_dict[self.port_x_fcl[port]].get_ppcp(port=self.port_global_x_port_local[port])

#     def get_pvid_port(self, port: int = 0):
#         """Get default VLAN ID for specified port"""
#         return self.fcl_dict[self.port_x_fcl[port]].get_pvid(port=self.port_global_x_port_local[port])

#     def get_ingress_filtering_port(self, port: int = 0):
#         """Get status of VLAN ingress filtering for specified port"""
#         return self.fcl_dict[self.port_x_fcl[port]].get_ingress_filtering(port=self.port_global_x_port_local[port])

#     def get_loopback_mode_port(self, port: int = 0):
#         """Get status of VLAN ingress filtering for specified port"""
#         return self.fcl_dict[self.port_x_fcl[port]].get_loopback_mode(port=self.port_global_x_port_local[port])

#     def get_rx_in_counter_port(self, port: int = 0):
#         """Get RX in frame counter for specified port"""
#         return self.fcl_dict[self.port_x_fcl[port]].get_rx_in_counter_port(port=self.port_global_x_port_local[port])

#     def get_rx_in_drop_counter_port(self, port: int = 0):
#         """Get RX in drop frame counter for specified port"""
#         return self.fcl_dict[self.port_x_fcl[port]].get_rx_in_drop_counter_port(port=self.port_global_x_port_local[port])

#     def get_tx_out_counter_port(self, port: int = 0):
#         """Get TX out frame counter for specified port"""
#         return self.fcl_dict[self.port_x_fcl[port]].get_tx_out_counter_port(port=self.port_global_x_port_local[port])

#     def get_lookup_counter_port(self, port: int = 0):
#         """Get lookup operation counter for specified port"""
#         return self.fcl_dict[self.port_x_fcl[port]].get_lookup_counter_port(port=self.port_global_x_port_local[port])

#     def get_write_counter_port(self, port: int = 0):
#         """Get write operation counter for specified port"""
#         return self.fcl_dict[self.port_x_fcl[port]].get_write_counter_port(port=self.port_global_x_port_local[port])

#     def get_ppcp_fcl_port(self, fcl: int = 0, port: int = 0):
#         """Similar to get_port_ppcp but specifying fcl and local port"""
#         return self.fcl_dict[fcl].get_ppcp(port=port)

#     def get_pvid_fcl_port(self, fcl: int = 0, port: int = 0):
#         """Similar to get_port_pvid but specifying fcl and local port"""
#         return self.fcl_dict[fcl].get_pvid(port=port)

#     def get_rx_in_counter_fcl_port(self, fcl: int = 0, port: int = 0):
#         """Similar to get_rx_in_counter_port but specifying fcl and local port"""
#         return self.fcl_dict[fcl].get_rx_in_counter_port(port=port)

#     def get_rx_in_drop_counter_fcl_port(self, fcl: int = 0, port: int = 0):
#         """Similar to get_rx_in_drop_counter_port but specifying fcl and local port"""
#         return self.fcl_dict[fcl].get_rx_in_drop_counter_port(port=port)

#     def get_tx_out_counter_fcl_port(self, fcl: int = 0, port: int = 0):
#         """Similar to get_tx_out_counter_port but specifying fcl and local port"""
#         return self.fcl_dict[fcl].get_tx_out_counter_port(port=port)

#     def get_lookup_counter_fcl_port(self, fcl: int = 0, port: int = 0):
#         """Similar to get_lookup_counter_port but specifying fcl and local port"""
#         return self.fcl_dict[fcl].get_lookup_counter_port(port=port)

#     def get_write_counter_fcl_port(self, fcl: int = 0, port: int = 0):
#         """Similar get_write_counter_port but specifying fcl and local port"""
#         return self.fcl_dict[fcl].get_write_counter_port(port=port)


#     # FCL configuration
#     def set_prio_map_fcl(self, fcl: int = 0, value: dict = {pcp:0 for pcp in range(8)}):
#         """Set PCP to switch priority mapping for the specified FCL"""
#         self.fcl_dict[fcl].set_prio_map(value=value)

#     def set_prio_map(self, value: dict = {pcp:0 for pcp in range(8)}):
#         """Set PCP to switch priority mapping for all FCLs"""
#         for fcl in range(self.FCL_COUNT):
#             self.fcl_dict[fcl].set_prio_map(value=value)

#     def get_prio_map_fcl(self, fcl: int = 0):
#         """Get PCP to priority mapping for the specified FCL"""
#         return self.fcl_dict[fcl].get_prio_map()


#     # FD configuration
#     def set_acc_util_fd(self, fcl: int = 0, value: int = 0):
#         """Set accelerated threshold utilization for aging of MAC address table"""
#         self.fcl_dict[fcl].set_acc_util_fd(value=value)

#     def set_min_util_fd(self, fcl: int = 0, value: int = 0):
#         """Set minimum threshold utilization for aging of MAC address table"""
#         self.fcl_dict[fcl].set_min_util_fd(value=value)

#     def set_max_util_fd(self, fcl: int = 0, value: int = 0):
#         """Set maximum threshold utilization for aging of MAC address table"""
#         self.fcl_dict[fcl].set_max_util_fd(value=value)

#     def set_period_aging_fd(self, fcl: int = 0, value: int = 0):
#         """Set period of aging of MAC address table"""
#         self.fcl_dict[fcl].set_period_aging_fd(value=value)
    
#     def set_freq_aging_fd(self, fcl: int = 0, value: int = 0):
#         """Set frequency of aging of MAC address table"""
#         self.fcl_dict[fcl].set_freq_aging_fd(value=value)

#     def set_config_depth_mask_fd(self, fcl: int = 0, value: int = 0):
#         """Set depth mask of each parallel table of the MAC address table"""
#         self.fcl_dict[fcl].set_config_depth_mask_fd(value=value)

#     def set_config_table_count_fd(self, fcl: int = 0, value: int = 0):
#         """Set active number of tables of the MAC address table"""
#         self.fcl_dict[fcl].set_config_table_count_fd(value=value)

#     def set_config_max_util_fd(self, fcl: int = 0, value: int = 0):
#         """Set maximum number of entries (utilization) of the MAC address table"""
#         self.fcl_dict[fcl].set_config_max_util_fd(value=value)

#     def set_max_loop_hit_util(self, fcl: int = 0, value: int = 0):
#         """Set register with number of entries inside the MAC address table before the first hit of LOOP_COUNT: use for resetting the capture (setting value 0)"""
#         self.fcl_dict[fcl].set_max_loop_hit_util(value=value)

#     def set_config_max_loop_count_fd(self, fcl: int = 0, value: int = 0):
#         """Set maximum number of iterations for an insertion (LOOP_COUNT) of the MAC address table"""
#         self.fcl_dict[fcl].set_config_max_loop_count_fd(value=value)

#     def clear_mac_table_fd(self, fcl: int = 0):
#         """Clear MAC address table"""
#         self.fcl_dict[fcl].clear_mac_table_fd()

#     def clear_vlan_table_fd(self, fcl: int = 0):
#         """Clear VLAN table"""
#         self.fcl_dict[fcl].clear_vlan_table_fd()

#     def clear_tag_table_fd(self, fcl: int = 0):
#         """Clear tag table"""
#         self.fcl_dict[fcl].clear_tag_table_fd()

#     def clear_fid_table_fd(self, fcl: int = 0):
#         """Clear fid table"""
#         self.fcl_dict[fcl].clear_fid_table_fd()

#     def get_util_fd(self, fcl: int = 0):
#         """Get current utilization of MAC address table"""
#         return self.fcl_dict[fcl].get_util_fd()
    
#     def get_acc_util_fd(self, fcl: int = 0):
#         """Get current accelerated threshold utilization for aging of MAC address table"""
#         return self.fcl_dict[fcl].get_acc_util_fd()

#     def get_min_util_fd(self, fcl: int = 0):
#         """Get current minimum threshold utilization for aging of MAC address table"""
#         return self.fcl_dict[fcl].get_min_util_fd()

#     def get_max_util_fd(self, fcl: int = 0):
#         """Get current maximum threshold utilization for aging of MAC address table"""
#         return self.fcl_dict[fcl].get_max_util_fd()

#     def get_period_aging_fd(self, fcl: int = 0):
#         """Get current period for aging of MAC address table"""
#         return self.fcl_dict[fcl].get_period_aging_fd()
    
#     def get_freq_aging_fd(self, fcl: int = 0):
#         """Get current frequency for aging of MAC address table"""
#         return self.fcl_dict[fcl].get_freq_aging_fd()

#     def get_config_depth_mask_fd(self, fcl: int = 0):
#         """Get current depth mask of each parallel table of the MAC address table"""
#         return self.fcl_dict[fcl].get_config_depth_mask_fd()

#     def get_config_table_count_fd(self, fcl: int = 0):
#         """Get current active number of parallel tables of the MAC address table"""
#         return self.fcl_dict[fcl].get_config_table_count_fd()

#     def get_config_max_util_fd(self, fcl: int = 0):
#         """Get current maximum utilization of the MAC address table"""
#         return self.fcl_dict[fcl].get_config_max_util_fd()

#     def get_config_max_util_tx_out_counter_fd(self, fcl: int = 0):
#         """Get counter with number of frames needed for reaching the maximum utilization (set_config_max_util_fd) of the MAC address table"""
#         return self.fcl_dict[fcl].get_config_max_util_tx_out_counter_fd()

#     def get_max_loop_hit_util_fd(self, fcl: int = 0):
#         """Get number of entries inside the MAC address table before the first hit of LOOP_COUNT (like infinite loop)"""
#         return self.fcl_dict[fcl].get_max_loop_hit_util_fd()

#     def get_max_loop_hit_counter_fd(self, fcl: int = 0):
#         """Get counter of number times that the LOOP_COUNT threshold has been reach during insertions (like infinite loop)"""
#         return self.fcl_dict[fcl].get_max_loop_hit_counter_fd()

#     def get_config_max_loop_count_fd(self, fcl: int = 0):
#         """Get maximum number of iterations for an insertion (LOOP_COUNT) of the MAC address table"""
#         return self.fcl_dict[fcl].get_config_max_loop_count_fd()


#     # Static port configuration
#     def get_static_address_write_counter(self, fcl: int = 0):
#         """Get address write operation counter using static port"""
#         return self.fcl_dict[fcl].get_static_address_write_counter()

#     def get_static_address_delete_counter(self, fcl: int = 0):
#         """Get address delete operation counter using static port"""
#         return self.fcl_dict[fcl].get_static_address_delete_counter()
    
#     def get_static_vlan_write_counter(self, fcl: int = 0):
#         """Get VLAN write operation counter using static port"""
#         return self.fcl_dict[fcl].get_static_vlan_write_counter()

#     def get_static_vlan_delete_counter(self, fcl: int = 0):
#         """Get VLAN delete operation counter using static port"""
#         return self.fcl_dict[fcl].get_static_vlan_delete_counter()

#     def get_static_address_write_status(self, fcl: int = 0):
#         """Get address write/delete operation status for static port"""
#         return self.fcl_dict[fcl].get_static_address_write_status()

#     def get_static_vlan_write_status(self, fcl: int = 0):
#         """Get VLAN write/delete operation status for static port"""
#         return self.fcl_dict[fcl].get_static_vlan_write_status()

#     def get_static_tag_write_status(self, fcl: int = 0):
#         """Get VLAN write/delete operation status for static port"""
#         return self.fcl_dict[fcl].get_static_tag_write_status()

#     def get_static_fid_write_status(self, fcl: int = 0):
#         """Get VLAN write/delete operation status for static port"""
#         return self.fcl_dict[fcl].get_static_fid_write_status()


#     # Additional parameters
#     def get_parameters_fcl(self, fcl: int = 0):
#         """Get architectural parameters for specified FCL"""
#         return self.fcl_dict[fcl].get_parameters()

#     def show_parameters_fcl(self, fcl: int = 0):
#         """Print architectural parameters for specified FCL"""
#         self.fcl_dict[fcl].show_parameters()

#     def get_parameters_all_fcl(self):
#         """ Get architectural parameters for all FCLs"""
#         return {fcl:self.get_parameters_fcl(fcl) for fcl in range(self.FCL_COUNT)}

#     def show_parameters_all_fcl(self):
#         """
#         Show parameters of all FCLs
#         """
#         for fcl in self.fcl_dict.values():
#             fcl.show_parameters()
#             print("\n")

#     def get_parameters_port(self, port: int = 0):
#         """Get architectural parameters for specified port module"""
#         if port in self.port_dict:
#             return self.port_dict[port].get_parameters()

#     def show_parameters_port(self, port: int = 0):
#         """Print architectural parameters for specified port module"""
#         if port in self.port_dict:
#             self.port_dict[port].show_parameters()

#     def get_parameters_all_port(self):
#         """ Get architectural parameters for all port modules"""
#         return {port:self.get_parameters_port(port=port) for port in self.port_dict.keys()}

#     def show_parameters_all_port(self):
#         """
#         Show parameters of port modules belonging to the switch
#         """
#         for port in self.port_dict.values():
#             port.show_parameters()
#             print("\n")

#     def get_all_params_or_regs(self, prefix: int = '#FCL', parameters: dict = {}):
#         fcl_parameters_str = ""
#         for element in range(len(parameters)):
#             parameters_str = ""
#             for param_str, param_value in parameters[element].items():
#                 parameters_str +=f',{param_str},{param_value}'
#             fcl_parameters_str += f'{prefix},{element}{parameters_str},'
        
#         fcl_parameters_str = fcl_parameters_str[:-1]
            
#         return fcl_parameters_str

#     def get_parameters_all_fcl_str(self, prefix: int = '#FCL'):
#         return self.get_all_params_or_regs(prefix=prefix, parameters=self.get_parameters_all_fcl())
    
#     def get_registers_all_fcl(self):
#         return {fcl:{"fd_util":self.fd_util[fcl], "fd_acc_util":self.fd_acc_util[fcl], "fd_min_util":self.fd_min_util[fcl],
#                 "fd_max_util":self.fd_max_util[fcl], "fd_period_aging":self.fd_period_aging[fcl], "fd_freq_aging":self.fd_freq_aging[fcl]}
#                 for fcl in range(self.FCL_COUNT)}

#     def get_registers_all_fcl_str(self, prefix: int = '#FCL'):
#         return self.get_all_params_or_regs(prefix=prefix, parameters=self.get_registers_all_fcl())

#     def get_registers_all_port(self):
#         return {port:{"port_ppcp":self.port_ppcp[port], "port_pvid":self.port_pvid[port], "port_lookup_counter":self.port_lookup_counter[port],
#                 "port_write_counter":self.port_write_counter[port]} for port in range(self.PORT_COUNT)}

#     def get_registers_all_port_str(self, prefix: int = '#Port'):
#         return self.get_all_params_or_regs(prefix=prefix, parameters=self.get_registers_all_port())

#     def get_parameters(self):
#         """Get switch architectural parameters"""
#         return {
#                     "CH_COUNT": self.CH_COUNT,
#                     "VC_COUNT": self.VC_COUNT,
#                     "PORT_COUNT": self.PORT_COUNT,
#                     "FCL_COUNT": self.FCL_COUNT,
#                     "ROW_COUNT": self.ROW_COUNT,
#                     "COL_COUNT": self.COL_COUNT,
#                     "PRIO_COUNT": self.PRIO_COUNT,
#                     "DROP_CORRUPTED_FRAMES": self.DROP_CORRUPTED_FRAMES,
#                     "EGRESS_PIPELINE_REGISTER": self.EGRESS_PIPELINE_REGISTER,
#                     "INGRESS_FIFO_DEPTH": self.INGRESS_FIFO_DEPTH,
#                     "EGRESS_FIFO_DEPTH": self.EGRESS_FIFO_DEPTH,
#                     "row_x_fcl_count": self.row_x_fcl_count,
#                     "col_x_fcl_count": self.col_x_fcl_count,
#                     "ch_x_fcl": self.ch_x_fcl,
#                     "ch_vc_x_fcl": self.ch_vc_x_fcl,
#                     "port_x_fcl": self.port_x_fcl,
#                     "port_global_x_port_local": self.port_global_x_port_local,
#                     "fcl_x_ch_list": self.fcl_x_ch_list,
#                     "port_x_ch_vc": self.port_x_ch_vc
#                 }
        
#     def show_parameters(self):
#         """Print switch architectural parameters"""
#         for param_str, param_value in self.get_parameters().items():
#             print(f'\t{param_str}: {param_value}')
        
#     def increase_counter_wrap(self, read: int, last: int):
#         """Increase counter taking into account possible wrap arounds due to register overflow"""
#         if read < last:
#             return read + self.register_max - last
#         else:
#            return read - last


#     def run(self, period: float = 0):
#         """Starts thread for _run method and handle all other set and get operations"""
#         run_thread = threading.Thread(target=self._run, args=(period, ), daemon=True)
#         run_thread.start()

#     def _run(self, period: int = 1):
#         """Collects all statistics in a continuous manner for FCLs and ports"""
        
#         self.run_run = True

#         # values that may wrap around    
#         port_lookup_counter_read = [0]*self.PORT_COUNT
#         port_lookup_counter_last = [0]*self.PORT_COUNT
        
#         port_write_counter_read = [0]*self.PORT_COUNT
#         port_write_counter_last = [0]*self.PORT_COUNT
        
#         # initial register values (to avoid setting them to 0)
#         for port in range(self.PORT_COUNT):
#             port_lookup_counter_last[port] = self.get_lookup_counter_port(port=port)
#             port_write_counter_last[port] = self.get_write_counter_port(port=port)

#         while self.run_run:
#             # read values
#             for fcl in range(self.FCL_COUNT):
#                 self.fd_util[fcl]     = self.get_util_fd(fcl=fcl)
#                 self.fd_acc_util[fcl] = self.get_acc_util_fd(fcl=fcl)
#                 self.fd_min_util[fcl] = self.get_min_util_fd(fcl=fcl)
#                 self.fd_max_util[fcl] = self.get_max_util_fd(fcl=fcl)
#                 self.fd_period_aging[fcl] = self.get_period_aging_fd(fcl=fcl)
#                 self.fd_freq_aging[fcl] = self.get_freq_aging_fd(fcl=fcl)
                
#             for port in range(self.PORT_COUNT):
#                 self.port_ppcp[port] = self.get_ppcp_port(port)
#                 self.port_pvid[port]  = self.get_pvid_port(port)
#                 port_lookup_counter_read[port]  = self.get_lookup_counter_port(port)
#                 port_write_counter_read[port]  = self.get_write_counter_port(port)
            
#             # counters handling: sum difference between last two readings and handle possible wrap arounds
#             for port in range(self.PORT_COUNT):
#                 self.port_lookup_counter[port] += self.increase_counter_wrap(port_lookup_counter_read[port], port_lookup_counter_last[port])
#                 self.port_write_counter[port] += self.increase_counter_wrap(port_write_counter_read[port], port_write_counter_last[port])

#                 # update last variable
#                 port_lookup_counter_last[port] = port_lookup_counter_read[port]
#                 port_write_counter_last[port] = port_write_counter_read[port]
            
#             time.sleep(period)


#     def show_rt_fd(self, fcl: list = [0]):
#         line_width = 25 + len(fcl)*10 + 2
#         header = f'{"FCL #":{25}}' + ''.join([f'{i:10}' for i in fcl]) + '\n'
#         line = f'{"":-<{line_width}}\n'
#         fd_curr = f'{"Table utilization":{25}}'     + ''.join([f'{self.get_util_fd(i):10}' for i in fcl]) + '\n'
#         fd_acc  = f'{"Accelerated threshold":{25}}' + ''.join([f'{self.get_acc_util_fd(i):10}' for i in fcl]) + '\n'
#         fd_max  = f'{"Minimum threshold":{25}}'     + ''.join([f'{self.get_min_util_fd(i):10}' for i in fcl]) + '\n'
#         fd_min  = f'{"Maximum threshold":{25}}'     + ''.join([f'{self.get_max_util_fd(i):10}' for i in fcl]) + '\n'
#         lookup  = f'{"Lookup operations":{25}}'     + ''.join([f'{self.get_lookup_counter_port(i):10.2E}' for i in fcl]) + '\n'
#         write   = f'{"Write operations":{25}}'      + ''.join([f'{self.get_write_counter_port(i):10.2E}' for i in fcl]) + '\n'
        
#         prio_map = f'{"Priority to VC mapping":{25}}' + ''.join(["  " + "".join(str(j) for j in self.get_prio_map_fcl(i)) for i in fcl]) + '\n'

#         print(header + line + fd_curr + fd_acc + fd_max + fd_min + lookup + write + prio_map)


#     def get_statistics(self, print_results: bool = False):
#         """Retrieve all statistics: hash table utilization and write and lookup counters, from all FCLs."""
        
#         # iterate over all fcl instances
#         for i in range(self.fcl_count):
#             fcl_dict = {
#                 'fd_util'    : f'{self.get_util_fd(i)}',
#                 'fd_acc_util': f'{self.get_acc_util_fd(i):10}',
#                 'fd_min_util': f'{self.get_min_util_fd(i):10}',
#                 'fd_max_util': f'{self.get_max_util_fd(i):10}',
#             }
            
#             for j in range(self.fcl_list[i].PORT_COUNT):
#                 port_dict = {
#                     'port_lookup_counter': f'{self.get_lookup_counter_fcl_port(i, j):10}',
#                     'port_write_counter': f'{self.get_write_counter_fcl_port(i, j):10}',
#                 }
        
#         return dict()


#     def __str__(self):
#         return self.get_parameters()


#     def __repr__(self):
#         return(
#                 f'EthernetSwitch().fromRegisters(write_func={self.write_func}, read_func={self.read_func}, offset={self.offset})'
#             )
