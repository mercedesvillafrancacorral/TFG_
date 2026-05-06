from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from back.port.infrastructure.inbound.api.controller_api import router

from back.port.infrastructure.inbound.api.grafana_controller import (
    router as grafana_router,
)

app = FastAPI(
    title="TFG",
    description="configuración y monitorización de red de altas prestaciones",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(grafana_router)


@app.get("/")
def root():
    return {"message": "TFG FPGA API - Configuración y Monitorización"}


@app.get("/health")
def health():
    import os
    return {"status": "ok", "mode": os.getenv("MODE", "simulation").lower()}
