from back.dfx.application.fpga_dfx_config_service import FpgaDfxConfigService
from back.dfx.infrastructure.outbound.fx_fpga_programmer_adapter import VivadoFpgaProgrammerAdapter
from back.port.infrastructure.inbound.api.dependencies import hardware, service as port_service

programmer = VivadoFpgaProgrammerAdapter()

service = FpgaDfxConfigService(programmer, port_service, hardware)


def get_fpga_dfx_config_service():
    return service
