from fastapi import APIRouter
from back.port.infrastructure.controller.PortCounterController import router as port_router

# Router principal que agrupa todos los sub-routers
router = APIRouter()
router.include_router(port_router)
