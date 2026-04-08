from elasticsearch import Elasticsearch
from back.port.infrastructure.elasticsearch.elasticshearchPortCounters import (
    elasticsearchPortCountersDomain,
)
from datetime import datetime


class ElasticsearchAdapter:
    """Adapter para guardar y consultar contadores en Elasticsearch."""

    def __init__(self, hosts=["http://localhost:9200"]):
        self.es = Elasticsearch(
            hosts,
            meta_header=False,
            verify_certs=False,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )
        self.index_name = "port_counters"

    def publish_counters(self, port_id: int, counters: dict) -> str | None:
        """Envía contadores a Elasticsearch."""
        document = {
            "@timestamp": datetime.utcnow().isoformat(),
            "port_id": port_id,
            "rx_port_in_frames": counters.get("rx_port_in_frames", 0),
            "rx_port_out_frames": counters.get("rx_port_out_frames", 0),
            "rx_port_gen_frames": counters.get("rx_port_gen_frames", 0),
            "rx_port_in_true_frames": counters.get("rx_port_in_true_frames", 0),
            "rx_port_gen_true_frames": counters.get("rx_port_gen_true_frames", 0),
            "tx_port_in_frames": counters.get("tx_port_in_frames", 0),
            "tx_port_out_frames": counters.get("tx_port_out_frames", 0),
            "tx_port_in_true_frames": counters.get("tx_port_in_true_frames", 0),
            "gen_frames": counters.get("gen_frames", 0),
        }

        try:
            res = self.es.index(index=self.index_name, document=document)
            return res["result"]
        except Exception as e:
            print(f"Error enviando a Elasticsearch: {e}")
            return None

    def get_history(
        self, port_id: int, start_time: str, end_time: str, limit: int = 100
    ) -> list[dict]:
        """Obtiene historial de contadores para un puerto."""
        try:
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"port_id": port_id}},
                            {
                                "range": {
                                    "@timestamp": {"gte": start_time, "lte": end_time}
                                }
                            },
                        ]
                    }
                },
                "sort": [{"@timestamp": {"order": "desc"}}],
                "size": limit,
            }

            result = self.es.search(index=self.index_name, body=query)
            hits = result.get("hits", {}).get("hits", [])

            return [hit["_source"] for hit in hits]

        except Exception as e:
            print(f"Error consultando historial: {e}")
            return []

    def get_latest(self, port_id: int) -> dict | None:
        """Obtiene el último registro para un puerto."""
        try:
            query = {
                "query": {"term": {"port_id": port_id}},
                "sort": [{"@timestamp": {"order": "desc"}}],
                "size": 1,
            }

            result = self.es.search(index=self.index_name, body=query)
            hits = result.get("hits", {}).get("hits", [])

            if hits:
                return hits[0]["_source"]
            return None

        except Exception as e:
            print(f"Error consultando último registro: {e}")
            return None
