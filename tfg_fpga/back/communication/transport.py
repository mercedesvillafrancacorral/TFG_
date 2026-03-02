from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Optional


class Transport(Protocol):
    def request(self, payload: bytes) -> bytes:
        ...


@dataclass
class SerialTransport:
    port: str
    baudrate: int = 115200
    timeout: float = 1.0
    _ser: Optional[object] = None

    def __post_init__(self) -> None:
        import serial  # import diferido
        self._ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)

    def request(self, payload: bytes) -> bytes:
        assert self._ser is not None
        self._ser.write(payload)
        self._ser.flush()
        # Ajusta longitud/terminador según tu framing real
        resp = self._ser.read(9)
        if not resp:
            raise TimeoutError("Sin respuesta UART")
        return resp

    def close(self) -> None:
        if self._ser:
            self._ser.close()


@dataclass
class MockTransport:
    registers: dict[int, int]

    def request(self, payload: bytes) -> bytes:
        # Protocolo simple demo:
        # [op(1)][addr(4 LE)][value(4 LE opcional)]
        op = payload[0]
        addr = int.from_bytes(payload[1:5], "little")
        if op == 0x01:  # read
            value = self.registers.get(addr, 0)
            return bytes([0x81]) + value.to_bytes(4, "little")
        if op == 0x02:  # write
            value = int.from_bytes(payload[5:9], "little")
            self.registers[addr] = value
            return bytes([0x82]) + value.to_bytes(4, "little")
        raise ValueError("Operación no soportada")