import os
import httpx

GRAFANA_URL = os.getenv("GRAFANA_URL", "http://grafana:3000")
GRAFANA_USER = os.getenv("GRAFANA_USER", "admin")
GRAFANA_PASS = os.getenv("GRAFANA_PASS", "admin")
GRAFANA_EXTERNAL_URL = os.getenv("GRAFANA_EXTERNAL_URL", "http://localhost:3001")


class GrafanaClient:
    def __init__(self):
        self.base = GRAFANA_URL.rstrip("/")
        self.auth = (GRAFANA_USER, GRAFANA_PASS)

    def _get(self, path: str):
        with httpx.Client() as c:
            r = c.get(f"{self.base}{path}", auth=self.auth)
            r.raise_for_status()
            return r.json()

    def _post(self, path: str, body: dict):
        with httpx.Client() as c:
            r = c.post(f"{self.base}{path}", json=body, auth=self.auth)
            r.raise_for_status()
            return r.json()

    def health(self) -> dict:
        return self._get("/api/health")

    def list_dashboards(self) -> list:
        return self._get("/api/search?type=dash-db")

    def get_dashboard(self, uid: str) -> dict:
        return self._get(f"/api/dashboards/uid/{uid}")

    def create_or_update_dashboard(self, dashboard: dict) -> dict:
        return self._post("/api/dashboards/db", {
            "dashboard": dashboard,
            "overwrite": True,
        })

    def panel_embed_url(self, dashboard_uid: str, panel_id: int) -> str:
        return (
            f"{GRAFANA_EXTERNAL_URL}/d/{dashboard_uid}"
            f"?orgId=1&viewPanel={panel_id}&from=now-1h&to=now&refresh=5s&kiosk"
        )

    def dashboard_url(self, dashboard_uid: str) -> str:
        return f"{GRAFANA_EXTERNAL_URL}/d/{dashboard_uid}?orgId=1&from=now-1h&to=now&refresh=5s"
