from elasticsearch import Elasticsearch
from back.port.infrastructure.elasticshearch.elasticshearchPortCountersDomain import (
    elasticsearchPortCountersDomain,
)
from datetime import datetime


class ElasticsearchAdapter:
    """Adapter para guardar contadores en Elasticsearch."""

    def __init__(self, hosts=["http://localhost:9200"]):
        self.es = Elasticsearch(
            hosts,
            meta_header=False,
            verify_certs=False,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )
        self.index_name = "port_counters"

    def publish_counters(self, domain: elasticsearchPortCountersDomain) -> str | None:
        """Envía el Domain a Elasticsearch para Grafana."""
        document = {
            "@timestamp": datetime.utcnow().isoformat(),
            "port_id": domain.port_id,
            "rx_port_in_frames": domain.rx_port_in_frames,
            "rx_port_out_frames": domain.rx_port_out_frames,
            "rx_port_gen_frames": domain.rx_port_gen_frames,
            "rx_port_in_true_frames": domain.rx_port_in_true_frames,
            "rx_port_gen_true_frames": domain.rx_port_gen_true_frames,
            "tx_port_in_frames": domain.tx_port_in_frames,
            "tx_port_out_frames": domain.tx_port_out_frames,
            "tx_port_in_true_frames": domain.tx_port_in_true_frames,
        }

        try:
            res = self.es.index(index=self.index_name, document=document)
            return res["result"]
        except Exception as e:
            print(f"Error enviando a Elasticsearch: {e}")
            return None
