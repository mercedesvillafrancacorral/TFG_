import time
from back.port.infrastructure.outbound.mock_register_bank import bank
from back.port.infrastructure.outbound.MockHardwareAdapter import MockHardwareAdapter
from back.port.application.PortCountersServiceImpl import PortCountersServiceImpl
from tfg_fpga.back.port.infrastructure.elasticshearch.adapter.elasticshearchAdapter import elasticsearchAdapter# 1. Montamos la arquitectura
adaptador = MockHardwareAdapter(bank)
servicio = PortCountersServiceImpl(adaptador)
es_adapter = elasticsearchAdapter()
print("="*70)
print(f"{'LECTURA':<10} | {'PUERTO 0 (RX)':<15} | {'PUERTO 1 (RX)':<15} | {'ESTADO P1'}")
print("-" * 70)
i = 0  # LA 'i' FUERA DEL BUCLE
while True:
    p0 = servicio.get_counters(0)
    p1 = servicio.get_counters(1)
    
    es_adapter.publish_counters(0, p0)
    es_adapter.publish_counters(1, p1)

    estado_p1 = "off" if p1.rx_in_frames == 0 else "on"
    
    print(f"Muestra {i+1:<3} | {p0.rx_in_frames:<15,} | {p1.rx_in_frames:<15,} | {estado_p1}")

    if i == 5:
        print("\n>>> [ORDEN] Activando generador en el Puerto 1...")
        bank.write((1, "RX_MUX"), "gen")
        bank.write((1, "GEN_ENABLE"), 1)

    i += 1  # SUMAMOS 1 A LA i PARA QUE CAMBIE LA MUESTRA
    time.sleep(1)