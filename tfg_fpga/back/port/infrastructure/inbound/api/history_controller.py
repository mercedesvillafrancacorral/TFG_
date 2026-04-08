from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from typing import Optional

from back.port.infrastructure.inbound.api.dependecies import get_port_service
from back.port.application.PortCountersService import PortCountersService
from back.port.infrastructure.elasticsearch.adapter.elasticshearchAdapter import (
    ElasticsearchAdapter,
)

router = APIRouter(prefix="/ports", tags=["history"])

es_adapter = ElasticsearchAdapter()


@router.get("/{port_id}/history")
def get_port_history(
    port_id: int,
    from_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    to_time: Optional[str] = Query(None, description="End time (ISO format)"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    service: PortCountersService = Depends(get_port_service),
):
    try:
        service.get_counters(port_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        if from_time:
            start = from_time
        else:
            dt = datetime.now()
            dt = dt.replace(hour=dt.hour - 1)
            start = dt.isoformat()

        if to_time:
            end = to_time
        else:
            end = datetime.now().isoformat()

        results = es_adapter.get_history(
            port_id=port_id, start_time=start, end_time=end, limit=limit
        )

        return {
            "port_id": port_id,
            "from": start,
            "to": end,
            "count": len(results),
            "data": results,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{port_id}/history/latest")
def get_latest_counters(
    port_id: int,
    service: PortCountersService = Depends(get_port_service),
):
    try:
        counters = service.get_counters(port_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        latest = es_adapter.get_latest(port_id)
        return {
            "port_id": port_id,
            "current": {
                "rx_port_in_frames": counters.rx_port_in_frames,
                "rx_port_out_frames": counters.rx_port_out_frames,
                "rx_port_gen_frames": counters.rx_port_gen_frames,
                "tx_port_in_frames": counters.tx_port_in_frames,
                "tx_port_out_frames": counters.tx_port_out_frames,
                "gen_frames": counters.gen_frames,
            },
            "last_indexed": latest,
        }
    except Exception as e:
        return {
            "port_id": port_id,
            "current": {
                "rx_port_in_frames": counters.rx_port_in_frames,
                "rx_port_out_frames": counters.rx_port_out_frames,
                "rx_port_gen_frames": counters.rx_port_gen_frames,
                "tx_port_in_frames": counters.tx_port_in_frames,
                "tx_port_out_frames": counters.tx_port_out_frames,
                "gen_frames": counters.gen_frames,
            },
            "last_indexed": None,
        }
