
"Atributos que nos manda la FPGA/ que podemos enviar a la FPGA" "Los atributos "
"están sacados de la clase port del ethernet_switch -> metodos GET "
"Nos estamos centrando en la MONITORIZACIÓN solamente en esta clase "
from dataclasses import dataclass

@dataclass
class PortCounters:
    
    "contador de frames totales que han entrado al puerto"
    rx_port_in_frames: int
    "contador de frames totales que han salen al puerto"
    rx_port_out_frames: int
    "contador de frames totales que han sido generados en el puerto internamente"
    rx_port_gen_frames: int
    "contador de frames totales que han entrado al puerto y han sido válidos"
    rx_port_in_true_frames: int
    "contador de frames totales que han sigo generados  al puerto y han sido válidos"
    rx_port_gen_true_frames: int
  
    tx_port_in_frames: int
    tx_port_out_frames: int
    tx_port_in_true_frames: int
    gen_frames: int



    
    

