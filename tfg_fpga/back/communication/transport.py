from dataclasses import dataclass
from typing import Protocol, Optional

class Transport(Protocol):
    def request(self, payload: bytes) -> bytes: ...

@dataclass
class SerialTransport:
    port: str
    baudrate: int = 115200
    timeout: float = 1.0
    _ser: Optional[object] = None

    def __post_init__(self) -> None:
        import serial
        self._ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)

    def request(self, payload: bytes) -> bytes:
        assert self._ser is not None
        self._ser.write(payload)
        self._ser.flush()
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
        op = payload[0]
        addr = int.from_bytes(payload[1:5], "little")
        if op == 0x01:
            value = self.registers.get(addr, 0)
            return bytes([0x81]) + value.to_bytes(4, "little")
        if op == 0x02:
            value = int.from_bytes(payload[5:9], "little")
            self.registers[addr] = value
            return bytes([0x82]) + value.to_bytes(4, "little")
        raise ValueError("Operación no soportada")

if __name__ == "__main__":
    t = MockTransport(registers={0x10: 123})

    payload = bytes([0x01]) + (0x10).to_bytes(4, "little")
    print(t.request(payload))

    payload = bytes([0x02]) + (0x10).to_bytes(4, "little") + (999).to_bytes(4, "little")
    print(t.request(payload))

    payload = bytes([0x01]) + (0x10).to_bytes(4, "little")
    print(t.request(payload))