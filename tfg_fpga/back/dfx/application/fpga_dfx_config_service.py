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

        self._library: dict[str, FpgaConfiguration] = {
            "normal": FpgaConfiguration(
                name="normal",
                bit_filename="fpga.bit",
                is_dfx=False,
                uses_dfx_register_layout=False,
            ),
            "dfx_estatica": FpgaConfiguration(
                name="dfx_estatica",
                bit_filename="config1_v3.bit",
                is_dfx=False,
                uses_dfx_register_layout=True,
            ),

            "dfx_dinamica_base": FpgaConfiguration(
                name="dfx_dinamica_base",
                bit_filename="config1_v3_pblock_p_0__partial.bit",
                is_dfx=True,
                uses_dfx_register_layout=True,

            ),
            "dfx_dinamica_vlan": FpgaConfiguration(
                name="dfx_dinamica_vlan",
                bit_filename="config2_v3_partial.bit",
                is_dfx=True,
                uses_dfx_register_layout=True,
            ),
            "dfx_dinamica_5_generadores_p0": FpgaConfiguration(
                 name="dfx_generadores_5_p0",
                 bit_filename="config2_generators5_v4_partial.bit",
                 is_dfx=True,
                 uses_dfx_register_layout=True,
            ),
            "dfx_dinamica_2_generadores_p0": FpgaConfiguration(
                name="dfx_dinamica_2_generadores_p0",
                bit_filename="config2_generators2_v5_partial.bit",
                is_dfx=True,
                uses_dfx_register_layout=True,
),
            
        }

    def list_configs(self) -> list[str]:
        return list(self._library)

    def load_config(self, name: str) -> bool:
        config = self._library.get(name)

        if config is None:
            raise ValueError(
                f"Configuración desconocida: {name}. "
                f"Disponibles: {list(self._library)}"
            )

        if self.hardware is not None:
            self.hardware.begin_reconfiguration()

        try:
            if config.is_dfx:
                print("[DFX] Desacoplando RP...")
                self.programmer.run_vio_script("vio_decouple_on.tcl")

            print(f"[DFX] Programando {config.bit_filename}...")
            self.programmer.program(config.bit_filename)

            if config.is_dfx:
                print("[DFX] Aplicando reset y reacoplando RP...")
                self.programmer.run_vio_script("vio_pulse_reset.tcl")

            if self.hardware is not None:
                self.hardware.set_register_layout(
                    extended=config.uses_dfx_register_layout
                )

                print(
                    f"[DFX] Esperando {RECONNECT_SETTLE_SECONDS} s "
                    "a que el hardware se estabilice..."
                )
                time.sleep(RECONNECT_SETTLE_SECONDS)

                print("[DFX] Reconectando XFCP...")
                self.hardware.finish_reconfiguration()

            return self.counters_service.wait_for_retry_connection()

        except Exception as e:
            print(f"[DFX] ERROR: {e}")
            print(
                "[DFX] El acceso normal a la FPGA permanece bloqueado "
                "hasta realizar una reconfiguración válida."
            )
            raise RuntimeError(
                f"Error durante la carga de la configuración '{name}': {e}"
            ) from e
