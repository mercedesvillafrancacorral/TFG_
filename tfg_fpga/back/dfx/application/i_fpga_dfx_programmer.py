from abc import ABC, abstractmethod


class IFpgaDfxProgrammer(ABC):
    @abstractmethod
    def program(self, bit_filename: str) -> None:
        pass

    @abstractmethod
    def run_vio_script(self, script_name: str) -> None:
        pass