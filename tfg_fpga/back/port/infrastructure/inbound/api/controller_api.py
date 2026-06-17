from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
from typing import Optional
import subprocess
import os
from back.port.application.PortCountersService import PortCountersService
from back.port.infrastructure.inbound.api.dependencies import get_port_service
from back.port.infrastructure.inbound.api.model_response import (
    PortsResponse,
    PortCountersResponse,
    GeneratorConfigRequest,
    MuxConfigRequest,
    MessageResponse,
)

FPGA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "fpga"))

router = APIRouter(prefix="/ports", tags=["ports"])


@router.get("", response_model=PortsResponse)
def get_ports(service: PortCountersService = Depends(get_port_service)):
    return PortsResponse(ports=service.get_ports())


@router.get("/{port_id}/counters", response_model=PortCountersResponse)
def get_counters(port_id: int, service: PortCountersService = Depends(get_port_service)):
    try:
        counters = service.get_counters(port_id)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return PortCountersResponse(
            rx_port_in_frames=counters.rx_port_in_frames,
            rx_port_out_frames=counters.rx_port_out_frames,
            rx_port_gen_frames=counters.rx_port_gen_frames,
            rx_port_in_true_frames=counters.rx_port_in_true_frames,
            rx_port_gen_true_frames=counters.rx_port_gen_true_frames,
            tx_port_in_frames=counters.tx_port_in_frames,
            tx_port_out_frames=counters.tx_port_out_frames,
            tx_port_in_true_frames=counters.tx_port_in_true_frames,
        
        )
    
    

@router.post("/{port_id}/generator", response_model=MessageResponse)
def configure_generator(
    port_id: int,
    request: GeneratorConfigRequest,
    service: PortCountersService = Depends(get_port_service),
):  
    
    try:
        service.configure_generator(
            port_id=port_id,
            enabled=request.enabled,
            length=request.length,
            counter=request.counter,
            counter_frac=request.counter_frac,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    generator_state = "enabled" if request.enabled else "disabled"
    return MessageResponse(
        message=f"Traffic generator {generator_state} for port {port_id}"
    )


@router.post("/{port_id}/mux", response_model=MessageResponse)
def configure_mux(
    port_id: int,
    request: MuxConfigRequest,
    service: PortCountersService = Depends(get_port_service),
):
    try:
        service.configure_mux(
            port_id=port_id,
            rx_mux=request.rx_mux,
            tx_mux=request.tx_mux,
        )
        return MessageResponse(message=f"Mux configurado en el puerto {port_id}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# @router.get("/{port_id}/history")
# def get_port_history(
#     port_id: int,
#     from_time: Optional[str] = Query(None, description="Start time (ISO format)"),
#     to_time: Optional[str] = Query(None, description="End time (ISO format)"),
#     limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
#     service: PortCountersService = Depends(get_port_service),
# ):
#     try:

#         start = from_time if from_time else (datetime.now() - timedelta(hours=1)).isoformat()
#         end = to_time if to_time else datetime.now().isoformat()
#         results = service.get_history(port_id=port_id, limit=limit)
#         return {
#             "port_id": port_id,
#             "from": start,
#             "to": end,
#             "count": len(results),
#             "data": results,
#         }
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/{port_id}/history/latest")
# def get_latest_counters(
#     port_id: int,
#     service: PortCountersService = Depends(get_port_service),
# ):
#     try:
#         counters = service.get_counters(port_id)
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))

#     try:
#         latest =service.get_latest(port_id)
#         return {
#             "port_id": port_id,
#             "current": {
#                 "rx_port_in_frames": counters.rx_port_in_frames,
#                 "rx_port_out_frames": counters.rx_port_out_frames,
#                 "rx_port_gen_frames": counters.rx_port_gen_frames,
#                 "tx_port_in_frames": counters.tx_port_in_frames,
#                 "tx_port_out_frames": counters.tx_port_out_frames,
                
#             },
#             "last_indexed": latest,
#         }
#     except Exception as e:
#         return {
#             "port_id": port_id,
#             "current": {
#                 "rx_port_in_frames": counters.rx_port_in_frames,
#                 "rx_port_out_frames": counters.rx_port_out_frames,
#                 "rx_port_gen_frames": counters.rx_port_gen_frames,
#                 "tx_port_in_frames": counters.tx_port_in_frames,
#                 "tx_port_out_frames": counters.tx_port_out_frames,
                
#             },
#             "last_indexed": None,
#         }
@router.post("/reset_fpga")
def reset_fpga():
    script = os.path.join(FPGA_DIR, "program.sh")
    bit = os.path.join(FPGA_DIR, "fpga.bit")
    try:
        result = subprocess.run(
            ["bash", script, bit],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=FPGA_DIR,
        )
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail="Error al programar la FPGA")

        if os.getenv("MODE", "simulation").lower() == "real":
            import time
            from back.port.infrastructure.inbound.api.dependencies import hardware
            time.sleep(5)
            hardware._connect()

        return MessageResponse(message="FPGA reseteada correctamente")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
