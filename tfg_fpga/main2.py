import time
from back.port.infrastructure.outbound.mock_register_bank import bank
from back.port.infrastructure.outbound.MockHardwareAdapter import MockHardwareAdapter
from back.port.application.PortCountersServiceImpl import PortCountersServiceImpl

# 1. Montamos la arquitectura
adaptador = MockHardwareAdapter(bank)
servicio = PortCountersServiceImpl(adaptador)

print("="*70)
print(f"{'LECTURA':<10} | {'PUERTO 0 (RX)':<15} | {'PUERTO 1 (RX)':<15} | {'ESTADO P1'}")
print("-" * 70)

for i in range(12):
    # Leemos ambos puertos a través del servicio
    p0 = servicio.get_counters(0)
    p1 = servicio.get_counters(1)
    
    estado_p1 = "off" if p1.rx_in_frames == 0 else "on"
    
    # Imprimimos los datos alineados
    print(f"Muestra {i+1:<3} | {p0.rx_in_frames:<15,} | {p1.rx_in_frames:<15,} | {estado_p1}")

    # --- MAGIA: En la muestra 5, activamos el Puerto 1 ---
    if i == 5:
        print("\n>>> [ORDEN] Activando generador en el Puerto 1...")
        # Usamos el banco para escribir en el registro (como haría la FPGA)
        bank.write((1, "RX_MUX"), "gen")
        bank.write((1, "GEN_ENABLE"), 1)
        print("-" * 70)

    time.sleep(1)

print("="*70)
print(">>> Simulación multipuerto completada con éxito.")