import time
import sys
# Importamos los componentes de tu arquitectura
from back.port.infrastructure.outbound.mock_register_bank import bank
from back.port.infrastructure.outbound.MockHardwareAdapter import MockHardwareAdapter
from back.port.application.PortCountersService import PortCountersService
from back.port.infrastructure.elasticsearch.adapter.elasticshearchAdapter import ElasticsearchAdapter
# Importamos tu adaptador

def main():
    # 1. Montamos la arquitectura de capas
    adaptador_hw = MockHardwareAdapter(bank)
    servicio = PortCountersService(adaptador_hw)
    
    # 2. Inicializamos el conector con Elasticsearch
    es_adapter = ElasticsearchAdapter()

    print("="*75)
    print(f"{'MUESTRA':<10} | {'PUERTO 0 (RX)':<15} | {'PUERTO 1 (RX)':<15} | {'ESTADO P1'}")
    print("-" * 75)

    i = 0  # <--- IMPORTANTE: Inicializamos el contador aquí

    try:
        while True:
            # Leemos los contadores de ambos puertos desde el servicio
            p0 = servicio.get_counters(0)
            p1 = servicio.get_counters(1)
            
            # Enviamos los datos a Elasticsearch
            es_adapter.publish_counters(0, p0)
            es_adapter.publish_counters(1, p1)

            # Lógica visual
            estado_p1 = "OFF" if p1.rx_in_frames == 0 else "ON (Generando)"
            
            # Imprimimos la fila de datos
            print(f"Muestra {i+1:<3} | {p0.rx_in_frames:<15,} | {p1.rx_in_frames:<15,} | {estado_p1}")

            # --- SIMULACIÓN DE EVENTO EN LA MUESTRA 5 ---
            if i == 5:
                print("\n>>> [SISTEMA] Activando generador de tráfico en Puerto 1...")
                bank.write((1, "RX_MUX"), "gen")
                bank.write((1, "GEN_ENABLE"), 1)
                print("-" * 75)

            i += 1
            time.sleep(1) # Esperamos 1 segundo entre lecturas
            
    except KeyboardInterrupt:
        print("\n\n>>> Simulación detenida por el usuario.")

if __name__ == "__main__":
    main()

