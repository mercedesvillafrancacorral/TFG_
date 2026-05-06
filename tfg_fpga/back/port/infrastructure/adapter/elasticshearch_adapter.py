import os
from elasticsearch import Elasticsearch
from datetime import datetime


class ElasticSearchAdapter:
    def __init__(self, hosts=["http://localhost:9200"]):
        # Con la versión <8.0.0, esto no dará errores de cabeceras
       host = os.getenv("ES_HOST", "http://localhost:9200")
       self.es = Elasticsearch([host])
       self.index_name = "fpg_metrics_index"

    def publish_counters(self, port_id: int, counters):
        document = {
            "@timestamp": datetime.utcnow().isoformat(),
            "port_id": port_id,
            "rx_in_frames": counters.rx_in_frames,
            "rx_out_frames": counters.rx_out_frames,
            "tx_in_frames": counters.tx_in_frames,
            "tx_out_frames": counters.tx_out_frames,
            "gen_frames": counters.gen_frames
        }
        try:
            self.es.index(index=self.index_name, body=document) # Nota: En v7 es 'body'
            return True
        except Exception as e:
            print(f"Error enviando a Elasticsearch: {e}")
            return False