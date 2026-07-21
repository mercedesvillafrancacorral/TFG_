DS_UID = "es-port-counters"
DS_REF = {"type": "elasticsearch", "uid": DS_UID}


def _es_target(port_id: int, metrics: list, bucket_id: str) -> dict:
    return {
        "datasource": DS_REF,
        "query": f"port_id:[{port_id} TO {port_id}]",
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
                "custom": {"drawStyle": "line", "lineWidth": 1, "fillOpacity": 10,"spanNulls": True},
                "color": {"mode": "palette-classic"},
            }
        },
        "options": {"legend": {"displayMode": "list", "placement": "bottom"}},
    }


def _max_metrics(fields: list) -> list:
    metrics = []
    for i, field in enumerate(fields):
        metrics.append({"type": "max", "field": field, "id": str(i + 1)})
    return metrics


def build_port_dashboard(port_id: int) -> dict:
    rx_metrics = _max_metrics([
        "rx_port_gen_frames",
        "rx_port_out_frames",
        "rx_port_in_frames",
    ])
    tx_metrics = _max_metrics([
        "tx_port_in_frames",
        "tx_port_out_frames",
        "tx_port_in_true_frames",
    ])
    throughput_metrics = _avg_metrics([
        "rx_port_gen_fps",
        "tx_port_out_fps",
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
            _timeseries_panel(3, f"Puerto {port_id} — Throughput (fps)", port_id, throughput_metrics, 0, 8),
        ],
    }
def _avg_metrics(fields: list) -> list:
    metrics = []
    for i, field in enumerate(fields):
        metrics.append({"type": "avg", "field": field, "id": str(i + 1)})
    return metrics
