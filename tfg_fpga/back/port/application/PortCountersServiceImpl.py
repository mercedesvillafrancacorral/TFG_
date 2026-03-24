
from back.port.domain import PortCounters
from back.port.application import IPortHardware

"Implementamos una clase abstracta que es lo mas parecido a una interfaz en java"
from abc import ABC
 
class PortCountersServiceImpl:
      def __init__(self, hw: IPortHardware):
        self.hw = hw

      

      def get_counters(self, port_id: int) -> PortCounters:
        return self.hw.read_counters(port_id)