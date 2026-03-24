import sys
import os
import time
from back.port.infrastructure.outbound.mock_register_bank import MockRegisterBank
# Configuramos la ruta para que Python vea la carpeta 'back'
ruta_actual = os.path.dirname(os.path.abspath(__file__))
if ruta_actual not in sys.path:
    sys.path.insert(0, ruta_actual)

print(f">>> Ejecutando desde: {ruta_actual}")

try:
    # IMPORTANTE: Observa que ponemos 'nombre_archivo.NombreClase'
    # 1. Carpeta 'application' -> Archivo 'PortCountersServiceImpl' -> Clase 'PortCountersServiceImpl'
    from back.port.application.PortCountersServiceImpl import PortCountersServiceImpl
    
    # 2. Carpeta 'outbound' -> Archivo 'adapter_mock' -> Clase 'MockHardwareAdapter'
    from back.port.infrastructure.outbound.MockHardwareAdapter import MockHardwareAdapter
    
    # 3. Carpeta 'outbound' -> Archivo 'mock_register_bank' -> Clase 'MockRegisterBank'
    from back.port.infrastructure.outbound.mock_register_bank import MockRegisterBank
    
    print("✅ ¡LOGRADO! Todos los módulos cargados.")

    # Inicialización (Arquitectura Hexagonal)
    mi_mock = MockRegisterBank(port_count=4)
    adaptador = MockHardwareAdapter(mi_mock)
    servicio = PortCountersServiceImpl(adaptador)
    
    print(">>> Leyendo contadores (5 iteraciones)...")

    for i in range(5):
        mi_mock.tick()
        for _ in range(10): mi_mock.tick()
        # Asumiendo que el método se llama get_counters y el puerto es el 0
        datos = servicio.get_counters(0)
        print(f"LECTURA {i+1}: {datos}")
        time.sleep(1)

except Exception as e:
    print(f"\n❌ ERROR EN EJECUCIÓN: {e}")
    import traceback
    traceback.print_exc()

input("\nPresiona ENTER para finalizar...")