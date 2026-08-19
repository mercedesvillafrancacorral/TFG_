"""Tests unitarios para dashboard_builder.py"""

"""Funciones  que construyen dicts para la API de Grafana"""

from back.grafana.dashboard_builder import (
    build_port_dashboard,
    _es_target,
    _timeseries_panel,
    _max_metrics,
    _avg_metrics,
)

def test_max_metrics_builds_one_entry_per_field():
    result = _max_metrics(["a", "b"])
    assert result == [
        {"type": "max", "field": "a", "id": "1"},
        {"type": "max", "field": "b", "id": "2"},
    ]


def test_avg_metrics_builds_one_entry_per_field():
    result = _avg_metrics(["x"])
    assert result == [{"type": "avg", "field": "x", "id": "1"}]

def test_es_target_filters_by_port_id():
    target = _es_target(port_id=2, metrics=[], bucket_id="10")
    assert target["query"] == "port_id:[2 TO 2]"
    assert target["bucketAggs"][0]["id"] == "10"

def test_timeseries_panel_has_expected_position_and_title():
    panel = _timeseries_panel(panel_id=1, title="RX", port_id=0, metrics=[], x=0, y=8)
    assert panel["title"] == "RX"
    assert panel["gridPos"] == {"x": 0, "y": 8, "h": 8, "w": 12}
    assert panel["type"] == "timeseries"

def test_build_port_dashboard_has_three_panels_for_port():
    dashboard = build_port_dashboard(3)
    assert dashboard["uid"] == "port-3"
    assert "port-3" in dashboard["tags"]
    assert len(dashboard["panels"]) == 3
    titles = [p["title"] for p in dashboard["panels"]]
    assert titles == [
        "Puerto 3 — RX Frames",
        "Puerto 3 — TX Frames",
        "Puerto 3 — Throughput (fps)",
    ]




