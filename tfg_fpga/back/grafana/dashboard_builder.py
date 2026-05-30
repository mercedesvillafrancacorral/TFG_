DS_UID = "es-port-counters"
DS_REF = {"type": "elasticsearch", "uid": DS_UID}


def _es_target(port_id: int, metrics: list, bucket_id: str) -> dict:
    return {
        "datasource": DS_REF,
        "query": f"port_id:{port_id}",
        "alias": "{{field}}",
        "timeField": "@timestamp",
        "metrics": metrics,
        "bucketAggs": [
            {
                "type": "date_histogram",
                "field": "@timestamp",
                "id": bucket_id,
                "settings": {"interval": "auto", "min_doc_count": "0"},
            }
        ],
        "refId": "A",
    }


def _timeseries_panel(panel_id: int, title: str, port_id: int, metrics: list, x: int, y: int) -> dict:
    return {
        "id": panel_id,
        "type": "timeseries",
        "title": title,
        "gridPos": {"x": x, "y": y, "h": 8, "w": 12},
        "datasource": DS_REF,
        "targets": [_es_target(port_id, metrics, str(panel_id * 10))],
        "fieldConfig": {
            "defaults": {
                "custom": {"drawStyle": "line", "lineWidth": 1, "fillOpacity": 10},
                "color": {"mode": "palette-classic"},
            }
        },
        "options": {"legend": {"displayMode": "list", "placement": "bottom"}},
    }


def _rate_metrics(fields: list) -> list:
    """Devuelve métricas de tasa (frames/s) usando max + derivative por campo."""
    metrics = []
    for i, field in enumerate(fields):
        max_id = str(i * 2 + 1)
        deriv_id = str(i * 2 + 2)
        metrics.append({"type": "max", "field": field, "id": max_id})
        metrics.append({
            "type": "derivative",
            "id": deriv_id,
            "pipelineAgg": max_id,
            "settings": {"unit": "1s"},
        })
    return metrics


def build_port_dashboard(port_id: int) -> dict:
    rx_metrics = _rate_metrics([
        "rx_port_in_frames",
        "rx_port_out_frames",
        "rx_port_gen_frames",
    ])
    tx_metrics = _rate_metrics([
        "tx_port_in_frames",
        "tx_port_out_frames",
        "tx_port_in_true_frames",
    ])

    return {
        "uid": f"port-{port_id}",
        "title": f"Puerto {port_id} — Contadores de tráfico",
        "tags": ["tfg", "fpga", f"port-{port_id}"],
        "timezone": "browser",
        "refresh": "5s",
        "time": {"from": "now-1h", "to": "now"},
        "schemaVersion": 38,
        "panels": [
            _timeseries_panel(1, f"Puerto {port_id} — RX Frames", port_id, rx_metrics, 0, 0),
            _timeseries_panel(2, f"Puerto {port_id} — TX Frames", port_id, tx_metrics, 12, 0),
        ],
    }
