from back.dfx.application.i_fpga_dfx_programmer import IFpgaDfxProgrammer
from back.dfx.domain.dfx_configuration import FpgaConfiguration
from back.port.application.PortCountersService import PortCountersService


class FpgaDfxConfigService:
    def __init__(self, programmer: IFpgaDfxProgrammer, counters_service: PortCountersService):
        self.programmer = programmer
        self.counters_service = counters_service
        self._library: dict[str, FpgaConfiguration] = {
            "normal": FpgaConfiguration(name="normal", bit_filename="fpga.bit", is_dfx=False),
            "dfx_normal": FpgaConfiguration(name="dfx_normal", bit_filename="config1_v2.bit", is_dfx=False),
            "dfx_vlan": FpgaConfiguration(name="dfx_vlan", bit_filename="config2_v2_partial.bit", is_dfx=True),
        }

    def list_configs(self) -> list[str]:
        return list(self._library)

    def load_config(self, name: str) -> bool:
        config = self._library.get(name)
        if config is None:
            raise ValueError(f"Configuración desconocida: {name}. Disponibles: {list(self._library)}")

        if config.is_dfx:
            self.programmer.run_vio_script("vio_decouple_on.tcl")

        self.programmer.program(config.bit_filename)

        if config.is_dfx:
            self.programmer.run_vio_script("vio_pulse_reset.tcl")

        return self.counters_service.wait_for_retry_connection()