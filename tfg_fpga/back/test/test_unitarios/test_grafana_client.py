""" Test unitarios de GrafanaClient"""
""" Solo se testea la lógica de construcción de URLs,
sin tocar los métodos que hacen peticiones HTTP reales (_get/_post/health/...).
"""

from back.grafana.grafana_client import GrafanaClient


def test_external_base_prefers_explicit_env_override(monkeypatch):
    monkeypatch.setattr("back.grafana.grafana_client.GRAFANA_EXTERNAL_URL", "http://mi-dominio.com")
    client = GrafanaClient(request_host="192.168.1.5:8000")
    assert client._external_base() == "http://mi-dominio.com"


def test_external_base_falls_back_to_request_host(monkeypatch):
    monkeypatch.setattr("back.grafana.grafana_client.GRAFANA_EXTERNAL_URL", "")
    client = GrafanaClient(request_host="192.168.1.5:8000")
    assert client._external_base() == "http://192.168.1.5:3000"


def test_external_base_falls_back_to_localhost_without_request_host(monkeypatch):
    monkeypatch.setattr("back.grafana.grafana_client.GRAFANA_EXTERNAL_URL", "")
    client = GrafanaClient(request_host=None)
    assert client._external_base() == "http://localhost:3000"

def test_dashboard_url_includes_uid(monkeypatch):
    monkeypatch.setattr("back.grafana.grafana_client.GRAFANA_EXTERNAL_URL", "")
    client = GrafanaClient(request_host=None)
    url = client.dashboard_url("port-2")
    assert url.startswith("http://localhost:3000/d/port-2")