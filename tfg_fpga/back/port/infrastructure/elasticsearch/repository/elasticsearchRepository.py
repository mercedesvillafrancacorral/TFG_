import os

from elasticsearch import Elasticsearch
from time import time
from back.port.domain.PortCounters import PortCounters
from back.port.application.PortCountersRepository import PortCountersRepository


class ElasticsearchRepository(PortCountersRepository):
    def __init__(self, hosts=None):
        if hosts is None:
            hosts = [os.getenv("ES_HOST", "http://elasticsearch:9200")]

        self.es = Elasticsearch(hosts, verify_certs=False)
        self.index_name = "port_counters"

        # 🔁 Esperar a que Elasticsearch esté listo
        for i in range(10):
            try:
                if self.es.ping():
                    print("✅ Conectado a Elasticsearch")
                    break
            except Exception:
                pass

            print("⏳ Esperando Elasticsearch...")
            time.sleep(2)
        else:
            print("⚠️ No se pudo conectar a Elasticsearch")
    def save(self, port_id: int, counters: PortCounters):
        document = {
            "@timestamp": datetime.utcnow().isoformat(),
            "port_id": port_id,
            "rx_port_in_frames": counters.rx_port_in_frames,
            "rx_port_out_frames": counters.rx_port_out_frames,
            "rx_port_gen_frames": counters.rx_port_gen_frames,
            "rx_port_in_true_frames": counters.rx_port_in_true_frames,
            "rx_port_gen_true_frames": counters.rx_port_gen_true_frames,
            "tx_port_in_frames": counters.tx_port_in_frames,
            "tx_port_out_frames": counters.tx_port_out_frames,
            "tx_port_in_true_frames": counters.tx_port_in_true_frames,
            "gen_frames": counters.gen_frames,
        }

        return self.es.index(index=self.index_name, document=document)

    def get_history(self, port_id: int, limit: int = 100):
        query = {
            "query": {
                "term": {"port_id": port_id}
            },
            "sort": [{"@timestamp": {"order": "desc"}}],
            "size": limit
        }

        result = self.es.search(index=self.index_name, body=query)
        hits = result.get("hits", {}).get("hits", [])

        return [hit["_source"] for hit in hits]

    def get_latest(self, port_id: int):
        query = {
            "query": {"term": {"port_id": port_id}},
            "sort": [{"@timestamp": {"order": "desc"}}],
            "size": 1
        }

        result = self.es.search(index=self.index_name, body=query)
        hits = result.get("hits", {}).get("hits", [])

        if hits:
            return hits[0]["_source"]
        return None