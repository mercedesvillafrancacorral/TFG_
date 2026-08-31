# TFG : Desarrollo de herramienta de configuración y monitorización para redes de altas prestaciones

 En este repositorio se encuentra la implementación del Trabajo Fin de Grado titulado **"Desarrollo de herramienta de configuración y monitorización para redes de altas prestaciones"**.

El proyecto proporciona una herramienta para la configuración y monitorización en tiempo real de un generador de tráfico implementado sobre FPGA. Permite trabajar tanto con un modelo simulado del hardware como con una FPGA real, proporcionando una API REST común para ambos casos. Además, incorpora almacenamiento de métricas mediante Elasticsearch, visualización mediante Grafana, ejecución automatizada de pruebas y soporte para la reconfiguración dinámica de la FPGA mediante DFX (*Dynamic Function eXchange*).

## Características principales
- Desarrollada en Python y una API REST desarrollada con FastAPI.
- Detección y configuración de los puertos disponibles.
- Lectura de contadores hardware.
- Configuración de: tamaño de trama, ancho de banda, estado de los generadores,  multiplexores RX/TX.
- Cálculo de métricas a partir de los contadores: throughput, pérdida de paquetes, tasa de tramas erróneas.
- Visualización y generación de dashboards con Grafana.
- Pipeline CI/CD mediante GitHub Actions.
- Soporte para reconfiguración dinámica mediante DFX.
  
## Arquitectura
El backend sigue una arquitectura hexagonal, separando la lógica de aplicación y dominio de los mecanismos concretos utilizados para acceder al hardware y a los servicios externos, gracias a esta organización se pueden realizar modificaciones sin tener que modificar otros módulos o hardware.

Los módulos principales relacionados con puertos y DFX mantienen la separación:

```text
back/
├── port/
│   ├── application/
│   ├── domain/
│   └── infrastructure/
│
├── dfx/
│   ├── application/
│   ├── domain/
│   └── infrastructure/
│
├── communication/
├── grafana/
└── test/
```
## Tecnologías utilizadas

### Backend

Para el backend se utiliza:

- Python
- FastAPI
- Uvicorn
- Pydantic

### FPGA

- Xilinx FPGA
- XFCP
- Comunicación serie mediante `pyserial`
- Vivado 2024.1
- Dynamic Function eXchange (DFX)

### Monitorización

- Elasticsearch
- Grafana
- Colector de métricas en Python

### Pruebas y despliegue

- pytest
- GitHub Actions

# API

FastAPI genera automáticamente la documentación interactiva de la API, disponible en:

`http://localhost:8000/docs` o http://10.22.10.2:8000/docs ( si estamos en el servidor )
