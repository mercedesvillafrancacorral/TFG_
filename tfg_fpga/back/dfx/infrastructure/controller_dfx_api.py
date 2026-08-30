from fastapi import APIRouter, Depends, HTTPException

from back.dfx.application.fpga_dfx_config_service import FpgaDfxConfigService
from back.dfx.infrastructure.inbound.dependencies import get_fpga_dfx_config_service

router = APIRouter(prefix="/dfx", tags=["Reconfiguración dinámica"])


@router.get("/list_available_configurations")
def list_configurations(service: FpgaDfxConfigService = Depends(get_fpga_dfx_config_service)):
    configs = service.list_configs()
    return {
        "message": f"Configurations found: {', '.join(configs)}",
        "configs": configs,
    }

@router.get("/current_configuration")
def get_current_configuration(service: FpgaDfxConfigService = Depends(get_fpga_dfx_config_service)):
    current = service.get_current_config()
    if current is None:
        return {
            "message": "No valid configuration is currently loaded.",
            "current_config": None,
            "is_dfx": None,
        }
    is_dfx = service.is_current_config_dfx()
    return {
        "message": f"f"Current configuration: {current} ({'DFX mode' if is_dfx else 'static mode'})",
        "current_config": current,
        "is_dfx": is_dfx,
    }
    
@router.post("/load_configuration/{name}")
def load_config(name: str, service: FpgaDfxConfigService = Depends(get_fpga_dfx_config_service)):
    try:
        link_ready = service.load_config(name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    message = f"Configuration '{name}' loaded successfully"
    if not link_ready:
        message += (
            ". The FPGA was reprogrammed successfully, but the connection to the "
            "ports hasn't stabilized yet — please retry in a few seconds."
        )
    return {"message": message}