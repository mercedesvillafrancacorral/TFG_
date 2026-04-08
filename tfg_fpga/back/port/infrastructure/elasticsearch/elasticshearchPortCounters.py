from dataclasses import dataclass


@dataclass 
class elasticsearchPortCounters:
    rx_port_in_frames: int
    rx_port_out_frames: int
    rx_port_gen_frames: int
    rx_port_in_true_frames: int
    rx_port_gen_true_frames: int
    tx_port_in_frames: int
    tx_port_out_frames: int
    tx_port_in_true_frames: int
    generate_frames: int
    port_id: int