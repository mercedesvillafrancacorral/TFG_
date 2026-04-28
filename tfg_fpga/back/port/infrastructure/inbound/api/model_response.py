from pydantic import BaseModel, Field


class PortsResponse(BaseModel):
    ports: list[int]


class PortCountersResponse(BaseModel):
    rx_port_in_frames: int
    rx_port_out_frames: int
    rx_port_gen_frames: int
    rx_port_in_true_frames: int
    rx_port_gen_true_frames: int
    tx_port_in_frames: int
    tx_port_out_frames: int
    tx_port_in_true_frames: int


class GeneratorConfigRequest(BaseModel):
    enabled: bool = Field(default=True, description="Enable/disable generator")
    length: int = Field(default=64, ge=64, le=9000, description="Frame length in bytes")
    counter: int = Field(default=1, ge=1, description="Frame counter interval")
    counter_frac: int = Field(default=0, ge=0, description="Fractional counter")


class MuxConfigRequest(BaseModel):
    rx_mux: str | None = Field(default=None, description="RX mux: null, mac or gen")
    tx_mux: str | None = Field(default=None, description="TX mux: null or mac")


class MessageResponse(BaseModel):
    message: str
