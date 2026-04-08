from fastapi import APIRouter, Depends, HTTPException

from back.port.application.PortCountersService import PortCountersService
from back.port.infrastructure.inbound.api.dependecies import get_port_service
from back.port.infrastructure.inbound.api.model_response import (
    PortsResponse,
    PortCountersResponse,
    GeneratorConfigRequest,
    MuxConfigRequest,
    MessageResponse,
)

router = APIRouter(prefix="/ports", tags=["ports"])


@router.get("", response_model=PortsResponse)
def get_ports(service: PortCountersService = Depends(get_port_service)):
    return PortsResponse(ports=service.get_ports())


@router.get("/{port_id}/counters", response_model=PortCountersResponse)
def get_counters(port_id: int, service: PortCountersService = Depends(get_port_service)):
    try:
        counters = service.get_counters(port_id)
        return PortCountersResponse(
            rx_port_in_frames=counters.rx_port_in_frames,
            rx_port_out_frames=counters.rx_port_out_frames,
            rx_port_gen_frames=counters.rx_port_gen_frames,
            rx_port_in_true_frames=counters.rx_port_in_true_frames,
            rx_port_gen_true_frames=counters.rx_port_gen_true_frames,
            tx_port_in_frames=counters.tx_port_in_frames,
            tx_port_out_frames=counters.tx_port_out_frames,
            tx_port_in_true_frames=counters.tx_port_in_true_frames,
            gen_frames=counters.gen_frames,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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
        return MessageResponse(message=f"Generador configurado en el puerto {port_id}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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
    
    
@router.get("/{port_id}/history")
def get_history(port_id: int, service: PortCountersService = Depends(get_port_service)):
    return service.get_history(port_id)