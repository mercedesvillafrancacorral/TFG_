import time

from back.port.application.PortCountersService import PortCountersService
from back.port.infrastructure.outbound.TutorPortHardwareAdapter import TutorPortHardwareAdapter
from back.port.application.PortCountersRepository import PortCountersRepository


class DummyRepository(PortCountersRepository):
    def save(self, port_id: int, counters):
        pass

    def get_history(self, port_id: int, limit: int = 100):
        return []

    def get_latest(self, port_id: int):
        return None


def main():
    hw = TutorPortHardwareAdapter(port_count=4)
    repo = DummyRepository()
    service = PortCountersService(hw, repo)

    print("PORTS:", service.get_ports())
    print("ANTES:", service.get_counters(0))

    service.configure_mux(0, rx_mux="gen", tx_mux="mac")
    service.configure_generator(0, enabled=True, length=128, counter=10, counter_frac=0)

    for i in range(5):
        time.sleep(1)
        print(f"LECTURA {i+1}:", service.get_counters(0))


if __name__ == "__main__":
    main()