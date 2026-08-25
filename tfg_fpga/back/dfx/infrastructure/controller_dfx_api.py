from fastapi import APIRouter, Depends, HTTPException

from back.dfx.application.fpga_dfx_config_service import FpgaDfxConfigService
from back.dfx.infrastructure.inbound.dependencies import get_fpga_dfx_config_service

router = APIRouter(prefix="/dfx", tags=["Reconfiguración dinámica"])


@router.get("/configurations")
def list_configs(service: FpgaDfxConfigService = Depends(get_fpga_dfx_config_service)):
    return {"configs": service.list_configs()}


@router.post("/load_configuration/{name}")
def load_config(name: str, service: FpgaDfxConfigService = Depends(get_fpga_dfx_config_service)):
    try:
        link_ready = service.load_config(name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    message = f"Configuración '{name}' cargada correctamente"
    if not link_ready:
        message += (
            ". La FPGA se ha reprogramado correctamente, pero la conexión con "
            "los puertos todavía no se ha estabilizado — reintenta en unos segundos."
        )
    return {"message": message}