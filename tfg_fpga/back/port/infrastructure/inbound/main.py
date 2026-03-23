import asyncio
from fastapi import FastAPI, HTTPException

from tfg_fpga.back.application.use_cases import ReadCountersUseCase
from tfg_fpga.back.infrastructure.outbound.fpga.mock_gateway import MockCountersGateway
from tfg_fpga.back.infrastructure.outbound.fpga.mock_register_bank import bank

app = FastAPI(title="TFG - Monitorización Mock")

uc = ReadCountersUseCase(hw=MockCountersGateway())

async def tick_loop():
    while True:
        bank.tick()
        await asyncio.sleep(1.0)

@app.on_event("startup")
async def startup():
    asyncio.create_task(tick_loop())

@app.get("/ports")
def list_ports():
    return {"ports": uc.list_ports()}

@app.get("/ports/{port_id}/counters")
def get_counters(port_id: int):
    try:
        c = uc.get(port_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Port not found")
    return c.__dict__