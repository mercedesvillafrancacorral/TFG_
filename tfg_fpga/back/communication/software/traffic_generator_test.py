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

import os
import sys
import time
import argparse
import math
import serial
import random
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'xfcp', 'python')))
import xfcp.interface

from traffic_generator import TrafficGenerator

from control_methods import convert_mac_to_int


def get_traffic_generator(uart_port: str, baud_rate: int, clk_frequency_if_traffic_generator: int, results_file: str):
    """
    Get the switch object from the UART port.
    """
    interface = None
    node = None

    # check XFCP configuration
    try:
        interface = xfcp.interface.SerialInterface(uart_port, baud_rate)
        node = interface.enumerate()
        print("XFCP node tree:")
        node.print_tree()
    except serial.serialutil.SerialException as e:
        print(f'Could not connect and initialize switch through serial port at: {uart_port}')
        print(str(e))
        print(repr(e))
        sys.exit(1)


    # Traffic generator object and ports definitions
    TRAFFIC_GENERATOR_SWITCH_OFFSET = 0X0

    # traffic_generator definition
    traffic_generator = TrafficGenerator.fromRegisters(write_func=node.write, read_func=node.read, offset=TRAFFIC_GENERATOR_SWITCH_OFFSET)

    traffic_generator.show_parameters_all_port()

    # get additional dictionaries
    port_type_dict = {}
    port_rate_dict = {}
    port_phy_dict = {}
    port_rate_100_count = 0
    port_rate_25_count = 0
    port_rate_10_count = 0
    for port in traffic_generator.port_dict.values():
        port_type_dict[port.PORT_ID] = port.RX_TRAFFIC_ENABLE
        port_rate_dict[port.PORT_ID] = port.PORT_RATE*10**6
        port_phy_dict[port.PORT_ID] = port.RX_TRAFFIC_ENABLE or port.TX_TRAFFIC_ENABLE
        port_rate_100_count = port_rate_100_count + (1 if port.PORT_RATE == 100000 else 0)
        port_rate_25_count = port_rate_25_count + (1 if port.PORT_RATE == 25000 else 0)
        port_rate_10_count = port_rate_10_count + (1 if port.PORT_RATE == 10000 else 0)

    # clock frequency of each port module
    clk_frequency_port = {}
    for i, phy in port_phy_dict.items():
        assert phy

        if port_rate_dict[port.PORT_ID] == 100000:
            clk_frequency_port[i] = 322.266e6
        elif port_rate_dict[port.PORT_ID] == 25000:
            clk_frequency_port[i] = 390.625e6
        else:
            clk_frequency_port[i] = 161.1328125e6


    # Write traffic_generator configuration to file
    # get parameters of traffic_generator and all ports and write to file header
    traffic_generator_params_str = "#element,traffic_generator,subelement,traffic_generator," + ",".join([f'{k},{v}' for k, v in traffic_generator.get_parameters().items()]) + '\n'
    
    port_module_params_str = ""
    for i, port in traffic_generator.port_dict.items():
        port_module_params_str = port_module_params_str + f'#element,traffic_generator,subelement,port_{i},clk_frequency_port,{clk_frequency_port[i]},' + ",".join([f'{k},{v}' for k, v in port.get_parameters().items()]) + '\n'

    design_params_str = f'#element,traffic_generator,subelement,design,clk_frequency_if_traffic_generator,{clk_frequency_if_traffic_generator}' + '\n'

    file_header = design_params_str + traffic_generator_params_str + port_module_params_str
    f = open(f'{results_file}', 'a+')
    f.write(file_header)
    f.close()
    
    return traffic_generator


def main(results_dir: str = "results", test_name: str = None, design_throughput: int = 10e9, desired_throughput: int = 1e9, frame_length: int = 60, clk_frequency_if_traffic_generator: int = 350e6):
    """
    Prepare and launch test.
        
    Inputs:
        test_name: default name for the test results.
        frame_length: length of the frames (without CRC) to be sent (in bytes)
        clk_frequency_if_traffic_generator (Hz): clock frequency of the traffic generator
    """

    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument('-us', '--uart_port', type=str, default="/dev/ttyUSB2", help="specify uart port")

    args = parser.parse_args()

    uart_port = (args.__dict__["uart_port"])

    baud_rate = 115200

    # name of results file
    results_file = f'{results_dir}/{test_name}.csv'
    Path(f'{results_dir}').mkdir(parents=True, exist_ok=True)

    # get traffic_generator object
    traffic_generator = get_traffic_generator(uart_port=uart_port, clk_frequency_if_traffic_generator=clk_frequency_if_traffic_generator, baud_rate=baud_rate, results_file=results_file)

    # set port states: enable both RX and TX MAC paths, and disable loopback mode
    traffic_generator.set_rx_mac_mux()
    traffic_generator.set_tx_mac_mux()

    # set port states: traffic generator in RX and TX MAC path
    for port in traffic_generator.port_dict.values():
        port.set_rx_gen_mux()
        port.set_tx_mac_mux()

    # Prepare tests
    # deactivate RX traffic generation in all tool ports
    for port in traffic_generator.port_dict.values():
        for gen in range(port.GEN_TRAFFIC_COMMON_COUNT):
            port.delete_rx_gen_common_counter(target=gen)

    # assign a mac address to each port and define common frame parameters for traffic generation
    smac_addresses = {port:{gen: f'70:60:50:40:{gen%2**8:02}:{port%2**8:02}' for gen in range(traffic_generator.port_dict[port].GEN_TRAFFIC_COMMON_COUNT)} for port in range(0, len(traffic_generator.port_dict))}
    dmac_addresses = {port:{gen: f'40:50:60:70:{gen%2**8:02}:{port%2**8:02}' for gen in range(traffic_generator.port_dict[port].GEN_TRAFFIC_COMMON_COUNT)} for port in range(0, len(traffic_generator.port_dict))}

    # desired total bandwidth
    bandwidth_l1 = desired_throughput
    assert bandwidth_l1 <= design_throughput

    # actual bandwidth in layer 2
    bandwidth_l2 = bandwidth_l1 * ((frame_length + 4) / (frame_length + 24))

    # port configuration dict
    port_conf_dict = {}

    for i, port in traffic_generator.port_dict.items():
        # add entry to port configuration dict
        port_conf_dict[port.PORT_ID] = {}

        # actual bandwidth in layer 2 without CRC
        bandwidth = bandwidth_l1 * (frame_length / (frame_length + 24)) / port.GEN_TRAFFIC_COMMON_COUNT

        counter_ach, counter_frac = traffic_generator.get_bandwidth_l2_counters(port=port.PORT_ID, clk_freq=clk_frequency_if_traffic_generator, bandwidth=bandwidth, frame_length=frame_length)

        # generate all flows for current port
        for gen in range(0, port.GEN_TRAFFIC_COMMON_COUNT):
            port_conf_dict[port.PORT_ID][gen] = {"target": gen, "counter": counter_ach, "counter_frac": counter_frac, "length": frame_length, "vlan_enable": 0, 
                    "destination_mac_address": convert_mac_to_int(dmac_addresses[port.PORT_ID][gen]), "source_mac_address": convert_mac_to_int(smac_addresses[port.PORT_ID][i]),
                    "vlan_id": 1, "vlan_pcp": 1, "vlan_dei": 0, "ether_type": 0x1111}

    # read counter registers in switch
    rx_gen_init_traffic_generator = {}
    tx_init_traffic_generator = {}
    rx_in_init_traffic_generator = {}
    for i, port in traffic_generator.port_dict.items():
        rx_gen_init_traffic_generator[i] = traffic_generator.port_dict[i].get_rx_port_gen_frame_counter()
        tx_init_traffic_generator[i] = traffic_generator.port_dict[i].get_tx_port_out_frame_counter()
        rx_in_init_traffic_generator[i] = traffic_generator.port_dict[i].get_rx_port_in_frame_counter()

    # configure traffic generators
    for port in traffic_generator.port_dict.values():
        if port.PORT_ID in port_conf_dict:
            # for each flow of each port
            for mesh_port, flow in port_conf_dict[port.PORT_ID].items():
                port.create_rx_gen_basic_counter(**flow)

    time.sleep(10)

    for port in traffic_generator.port_dict.values():
        for gen in range(port.GEN_TRAFFIC_COMMON_COUNT):
            port.delete_rx_gen_common_counter(target=gen)

    time.sleep(0.5)

    rx_gen_end_traffic_generator = {}
    tx_end_traffic_generator = {}
    rx_in_end_traffic_generator = {}
    rx_gen_diff_traffic_generator = {}
    tx_diff_traffic_generator = {}
    rx_in_diff_traffic_generator = {}
    for i, port in traffic_generator.port_dict.items():
        rx_gen_end_traffic_generator[i] = traffic_generator.port_dict[i].get_rx_port_gen_frame_counter()
        tx_end_traffic_generator[i] = traffic_generator.port_dict[i].get_tx_port_out_frame_counter()
        rx_in_end_traffic_generator[i] = traffic_generator.port_dict[i].get_rx_port_in_frame_counter()

        rx_gen_diff_traffic_generator[i] = (rx_gen_end_traffic_generator[i]-rx_gen_init_traffic_generator[i])
        tx_diff_traffic_generator[i] = (tx_end_traffic_generator[i]-tx_init_traffic_generator[i])
        rx_in_diff_traffic_generator[i] = (rx_in_end_traffic_generator[i]-rx_in_init_traffic_generator[i])

    print("rx_gen_diff_traffic_generator", rx_gen_diff_traffic_generator)
    print("tx_diff_traffic_generator", tx_diff_traffic_generator)
    print("rx_in_diff_traffic_generator", rx_in_diff_traffic_generator)


if __name__ == "__main__":
    """
    Run tests indicating the main frequencies used in the design
    """
    main(results_dir = "traffic_generator", test_name="a", design_throughput = 10e9, desired_throughput = 1e9, frame_length=60, clk_frequency_if_traffic_generator=350e6)
