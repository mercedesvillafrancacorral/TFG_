import time

from back.dfx.application.i_fpga_dfx_programmer import IFpgaDfxProgrammer
from back.dfx.domain.dfx_configuration import FpgaConfiguration
from back.port.application.IPortHardware import IPortHardware
from back.port.application.PortCountersService import PortCountersService

RECONNECT_SETTLE_SECONDS = 6


class FpgaDfxConfigService:
    def __init__(
        self,
        programmer: IFpgaDfxProgrammer,
        counters_service: PortCountersService,
        hardware: IPortHardware | None = None,
    ):
        self.programmer = programmer
        self.counters_service = counters_service
        self.hardware = hardware
        # is_dfx marks *partial* bitstreams, which need the VIO decouple/reset dance
        # around them. config1_v2.bit is a full image (static shell + VIO core) that
        # loads like any other full bitstream, so it's is_dfx=False despite the name.
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

        if self.hardware is not None:
            # Reprogramar la FPGA tira el enlace UART, igual que en /ports/reset_fpga:
            # sin reabrirlo aquí, las lecturas posteriores van contra una conexión obsoleta.
            time.sleep(RECONNECT_SETTLE_SECONDS)
            self.hardware.reconnect()

        return self.counters_service.wait_for_retry_connection()