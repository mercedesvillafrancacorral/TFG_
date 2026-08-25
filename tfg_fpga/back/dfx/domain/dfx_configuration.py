
from dataclasses import dataclass
@dataclass(frozen=True)
class FpgaConfiguration:
    name: str
    bit_filename: str
    is_dfx: bool
