from __future__ import annotations
from abc import ABC, abstractmethod
from back.port.domain.PortCounters import PortCounters



class IPortHardware(ABC):
    @abstractmethod
    def read_counters(self, port_id: int) -> PortCounters:
        pass 

    @abstractmethod
    def get_ports(self)->list[int]:
        pass

    "para configuracion"
    @abstractmethod
    def set_generator (
        self,port_id:int, enabled:bool,length:int, counter:int, counter_frac :int
    )-> None: 
        pass

    @abstractmethod
    def set_generator_traffic (
        self,port_id:int, enabled:bool,length:int, counter:int, counter_frac :int, target :int
    )-> None: 
        pass
    @abstractmethod
    def get_clk_freq(self, port_id: int) -> float:
        pass

    @abstractmethod
    def get_counter_frac_width(self, port_id: int) -> int:
        pass

    @abstractmethod
    def set_mux(self,port_id:int, rx_mux:str | None=None,  tx_mux: str | None = None) -> None:
        pass

    @abstractmethod
    def set_register_layout(self, extended: bool) -> None:
        pass

    @abstractmethod
    def begin_reconfiguration(self) -> None:
        pass

    @abstractmethod
    def finish_reconfiguration(self) -> None:
        pass
