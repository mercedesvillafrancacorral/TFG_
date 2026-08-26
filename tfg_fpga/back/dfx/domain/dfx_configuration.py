
from dataclasses import dataclass
@dataclass(frozen=True)
class FpgaConfiguration:
    name: str
    bit_filename: str
    is_dfx: bool
    # True para config1_v2.bit/config2_v2_partial.bit: su port_sync.v tiene el banco
    # de registros de puerto desplazado respecto a fpga.bit (ver Port.initialize en
    # traffic_generator.py). Independiente de is_dfx: dfx_normal no es parcial pero
    # sí usa este mapa, porque comparte la misma shell estática que dfx_vlan.
    uses_dfx_register_layout: bool = False
