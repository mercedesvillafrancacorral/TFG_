from abc import ABC, abstractmethod
from back.port.domain.PortCounters import PortCounters
class IPortHardware(ABC):
    @abstractmethod
    def read_counters(self, port_id: int) -> PortCounters:
        pass