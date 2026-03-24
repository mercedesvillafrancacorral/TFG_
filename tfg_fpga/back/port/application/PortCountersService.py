
from back.port.domain.PortCounters import PortCounters

"Implementamos una clase abstracta que es lo mas parecido a una interfaz en java"
from abc import ABC, abstractmethod

class PortCountersService(ABC):
    
    @abstractmethod
    def get_counters(self, port_id: int) -> PortCounters:
        pass