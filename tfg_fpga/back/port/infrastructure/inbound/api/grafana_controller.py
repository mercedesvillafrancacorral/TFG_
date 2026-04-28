from fastapi import APIRouter, HTTPException
import httpx

from back.grafana.client import GrafanaClient
from back.grafana.dashboard_builder import build_port_dashboard

router = APIRouter(prefix="/grafana", tags=["grafana"])


def _client() -> GrafanaClient:
    return GrafanaClient()


@router.get("/health")
def grafana_health():
    try:
        return _client().health()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=f"Grafana no disponible: {e}")


# @router.get("/dashboards")
# def list_dashboards():
#     try:
#         return _client().list_dashboards()
#     except httpx.HTTPError as e:
#         raise HTTPException(status_code=503, detail=str(e))


# @router.get("/dashboard/{uid}")
# def get_dashboard(uid: str):
#     try:
#         return _client().get_dashboard(uid)
#     except httpx.HTTPStatusError as e:
#         if e.response.status_code == 404:
#             raise HTTPException(status_code=404, detail=f"Dashboard '{uid}' no encontrado")
#         raise HTTPException(status_code=503, detail=str(e))


# @router.get("/ports/{port_id}/dashboard")
# def get_or_create_port_dashboard(port_id: int):
#     client = _client()
#     uid = f"port-{port_id}"
#     try:
#         return client.get_dashboard(uid)
#     except httpx.HTTPStatusError as e:
#         if e.response.status_code != 404:
#             raise HTTPException(status_code=503, detail=str(e))

#     try:
#         result = client.create_or_update_dashboard(build_port_dashboard(port_id))
#         return {"created": True, "uid": uid, "url": result.get("url")}
#     except httpx.HTTPError as e:
#         raise HTTPException(status_code=503, detail=str(e))


@router.post("/ports/{port_id}/dashboard")
def create_port_dashboard(port_id: int):
    try:
        result = _client().create_or_update_dashboard(build_port_dashboard(port_id))
        return {"uid": f"port-{port_id}", "url": result.get("url"), "status": result.get("status")}
    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/ports/dashboards/all")
def create_all_port_dashboards(port_count: int = 4):
    client = _client()
    results = []
    for port_id in range(port_count):
        try:
            result = client.create_or_update_dashboard(build_port_dashboard(port_id))
            results.append({"port_id": port_id, "uid": f"port-{port_id}", "status": result.get("status"), "url": result.get("url")})
        except httpx.HTTPError as e:
            results.append({"port_id": port_id, "status": "error", "detail": str(e)})
    return {"created": len([r for r in results if r["status"] != "error"]), "results": results}


@router.get("/ports/{port_id}/embed-urls")
def get_port_embed_urls(port_id: int):
    client = _client()
    uid = f"port-{port_id}"

    try:
        client.get_dashboard(uid)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            try:
                client.create_or_update_dashboard(build_port_dashboard(port_id))
            except httpx.HTTPError as create_err:
                raise HTTPException(status_code=503, detail=str(create_err))
        else:
            raise HTTPException(status_code=503, detail=str(e))
    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return {
        "port_id": port_id,
        "dashboard_url": client.dashboard_url(uid),
        "rx_panel_url": client.panel_embed_url(uid, panel_id=1),
        "tx_panel_url": client.panel_embed_url(uid, panel_id=2),
    }
