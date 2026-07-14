from abc import ABC, abstractmethod

from back.port.domain.PortCounters import PortCounters


class PortCountersRepository(ABC):

    @abstractmethod
    def save(self, port_id: int, counters: PortCounters):
        pass

    @abstractmethod
    def get_history(self, port_id: int, limit: int = 100):
        pass

    @abstractmethod
    def get_latest(self, port_id: int):
        pass
    
    
  