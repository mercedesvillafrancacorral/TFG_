#!/usr/bin/env python3
import sys
import os
import threading
from typing import Optional

# Añadir software/ al path para que traffic_generator.py pueda importar control_methods
_software_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', 'communication', 'software')
)
_xfcp_dir = os.path.join(_software_dir, 'xfcp', 'python')
for _p in (_software_dir, _xfcp_dir):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from xfcp.interface import SerialInterface       # noqa: E402
from traffic_generator import TrafficGenerator   # noqa: E402
from control_methods import read_conf_reg_int    # noqa: E402
from control_registers import (                  # noqa: E402
    RB_BOARD_REG_PORT_ENABLE_COUNT,
    RB_BOARD_REG_PORT_25G_COUNT,
    RB_BOARD_REG_PORT_100G_COUNT,
    RB_BOARD_REG_PORT_OFFSET,
    RB_BOARD_REG_PORT_STRIDE,
    RB_BOARD_REG_SWITCH_COUNT,
    RB_BOARD_REG_SWITCH_OFFSET,
    RB_BOARD_REG_SWITCH_STRIDE,
)
from back.port.application.IPortHardware import IPortHardware
from back.port.domain.PortCounters import PortCounters



# ============================================================================
# ADAPTADOR FPGA
# ============================================================================

class FPGATrafficGeneratorAdapter(IPortHardware):
    """
    Adaptador que conecta tu aplicación FastAPI con la FPGA real.
    
    Usa el TrafficGenerator del tutor e implementa tu interfaz IPortHardware.
    """
    
    def __init__(
        self,
        uart_port: str = "/dev/ttyUSB2",
        baud_rate: int = 115200,
        clk_freq: float = 350e6
    ):
        """
        Inicializa conexión con la FPGA.
        
        Args:
            uart_port: Puerto serie donde está la FPGA (default: /dev/ttyUSB2)
            baud_rate: Velocidad de comunicación (default: 115200)
            clk_freq: Frecuencia de reloj del sistema en Hz (default: 350 MHz)
        """
        self.uart_port = uart_port
        self.baud_rate = baud_rate
        self.clk_freq = clk_freq
        
        self.interface = None
        self.node = None
        self.traffic_generator = None
        self._lock = threading.Lock()

        self._connect()
    
    def reconnect(self):
        """Cierra la conexión actual y reconecta. Seguro para llamar con el data_collector activo."""
        with self._lock:
            try:
                self.interface.serial_port.close()
            except Exception:
                pass
            self.interface = None
            self.node = None
            self.traffic_generator = None
            self._connect()

    def _connect(self):
        """Establece conexión con la FPGA vía XFCP/UART"""
        try:
            print(f"\n{'='*60}")
            print(f" Conectando a FPGA")
            print(f"{'='*60}")
            print(f"Puerto: {self.uart_port}")
            print(f"Baud rate: {self.baud_rate}")
            
            # Crear interfaz XFCP
            self.interface = SerialInterface(
                self.uart_port,
                self.baud_rate
            )
            print("✓ Interfaz XFCP creada")
            
            # Enumerar dispositivos
            self.node = self.interface.enumerate()
            print(" Dispositivo XFCP detectado")
            
            # Crear TrafficGenerator usando código del tutor
            self.traffic_generator = TrafficGenerator.fromRegisters(
                write_func=self.node.write,
                read_func=self.node.read,
                offset=0x0
            )
            print(" TrafficGenerator inicializado")
            
            # Mostrar información de puertos detectados
            num_ports = len(self.traffic_generator.port_dict)
            print(f"\n Hardware detectado:")
            print(f"   Total de puertos: {num_ports}")
            
            for port_id, port in self.traffic_generator.port_dict.items():
                print(f"\n   Puerto {port_id}:")
                print(f"      Velocidad: {port.PORT_RATE} Mbps ({port.PORT_RATE/1000} Gbps)")
                print(f"      Generadores: {port.GEN_TRAFFIC_COMMON_COUNT}")
                print(f"      RX habilitado: {bool(port.RX_TRAFFIC_ENABLE)}")
                print(f"      TX habilitado: {bool(port.TX_TRAFFIC_ENABLE)}")
                print(f"      GEN habilitado: {bool(port.GEN_TRAFFIC_ENABLE)}")
            
            print(f"\n{'='*60}")
            print(f" Conexión con FPGA exitosa")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"\n{'='*60}")
            print(f" ERROR AL CONECTAR CON FPGA")
            print(f"{'='*60}")
            raise ConnectionError(
                f"No se pudo conectar con la FPGA en {self.uart_port}\n\n"
               
            )
    
    # ========================================================================
    # IMPLEMENTACIÓN DE IPortHardware
    # ========================================================================
    
    def get_ports(self) -> list[int]:
        """
        Retorna lista de IDs de puertos disponibles.

        Returns:
            Lista de IDs (ej: [0, 1, 2, 3])
        """
        with self._lock:
            if not self.traffic_generator:
                raise RuntimeError("TrafficGenerator no inicializado")
            return list(self.traffic_generator.port_dict.keys())
    
    def read_counters(self, port_id: int) -> PortCounters:
        """
        Lee contadores REALES desde la FPGA.
        
        Args:
            port_id: ID del puerto (0, 1, 2, 3...)
        
        Returns:
            PortCounters con valores reales de la FPGA
        
        Raises:
            ValueError: Si el puerto no existe
            RuntimeError: Si hay error al leer
        """
        if not self.traffic_generator:
            raise RuntimeError("TrafficGenerator no inicializado")
        
        if port_id not in self.traffic_generator.port_dict:
            available = list(self.traffic_generator.port_dict.keys())
            raise ValueError(
                f"Puerto {port_id} no existe. "
                f"Puertos disponibles: {available}"
            )
        
        port = self.traffic_generator.port_dict[port_id]

        try:
            with self._lock:
                return PortCounters(
                    rx_port_in_frames=port.get_rx_port_in_frame_counter(),
                    rx_port_out_frames=port.get_rx_port_out_frame_counter(),
                    rx_port_gen_frames=port.get_rx_port_gen_frame_counter(),
                    rx_port_in_true_frames=port.get_rx_port_in_true_frame_counter(),
                    rx_port_gen_true_frames=port.get_rx_port_gen_true_frame_counter(),
                    tx_port_in_frames=port.get_tx_port_in_frame_counter(),
                    tx_port_out_frames=port.get_tx_port_out_frame_counter(),
                    tx_port_in_true_frames=port.get_tx_port_in_true_frame_counter(),
                )
        except Exception as e:
            raise RuntimeError(
                f"Error al leer contadores del puerto {port_id}: {e}"
            )
    
    def set_generator(
        self,
        port_id: int,
        enabled: bool,
        length: int,
        counter: int,
        counter_frac: int
    ) -> None:
        """
        Configura el generador de tráfico REAL.
        
        Args:
            port_id: ID del puerto
            enabled: True para activar, False para desactivar
            length: Longitud del frame en bytes
            counter: Valor del contador (calculado según bandwidth)
            counter_frac: Valor del contador fraccional
        
        Raises:
            ValueError: Si el puerto no existe
            RuntimeError: Si hay error al configurar
        """
        if not self.traffic_generator:
            raise RuntimeError("TrafficGenerator no inicializado")
        
        if port_id not in self.traffic_generator.port_dict:
            available = list(self.traffic_generator.port_dict.keys())
            raise ValueError(
                f"Puerto {port_id} no existe. "
                f"Puertos disponibles: {available}"
            )
        
        port = self.traffic_generator.port_dict[port_id]

        try:
            with self._lock:
                if enabled:
                    print(f"\n  Activando generador en puerto {port_id}:")
                    print(f"   Frame length: {length} bytes")
                    print(f"   Counter: {counter}")
                    print(f"   Counter frac: {counter_frac}")

                    port.set_rx_gen_mux()
                    port.set_tx_mac_mux()

                    port.create_rx_gen_basic_counter(
                        target=0,
                        counter=counter,
                        counter_frac=counter_frac,
                        length=length,
                        destination_mac_address=0x001122334455,
                        source_mac_address=0xAABBCCDDEEFF,
                        ether_type=0x0800
                    )
                    print(f"✓ Generador activado en puerto {port_id}\n")

                else:
                    print(f"\n  Desactivando generador en puerto {port_id}...")
                    port.delete_rx_gen_common_counter(target=0)
                    port.set_rx_mac_mux()
                    print(f"✓ Generador desactivado en puerto {port_id}\n")

        except Exception as e:
            raise RuntimeError(
                f"Error al configurar generador en puerto {port_id}: {e}"
            )
    
    def set_mux(
        self,
        port_id: int,
        rx_mux: Optional[str] = None,
        tx_mux: Optional[str] = None
    ) -> None:
        """
        Configura multiplexores REALES.
        
        Args:
            port_id: ID del puerto
            rx_mux: Modo RX ('null', 'mac', 'gen') o None
            tx_mux: Modo TX ('null', 'mac') o None
        
        Raises:
            ValueError: Si el puerto no existe o modo inválido
            RuntimeError: Si hay error al configurar
        """
        if not self.traffic_generator:
            raise RuntimeError("TrafficGenerator no inicializado")
        
        if port_id not in self.traffic_generator.port_dict:
            available = list(self.traffic_generator.port_dict.keys())
            raise ValueError(
                f"Puerto {port_id} no existe. "
                f"Puertos disponibles: {available}"
            )
        
        port = self.traffic_generator.port_dict[port_id]

        try:
            with self._lock:
                if rx_mux is not None:
                    print(f"  Puerto {port_id} - RX MUX: {rx_mux}")
                    if rx_mux == "null":
                        port.set_rx_null_mux()
                    elif rx_mux == "mac":
                        port.set_rx_mac_mux()
                    elif rx_mux == "gen":
                        port.set_rx_gen_mux()
                    else:
                        raise ValueError(
                            f"rx_mux inválido: '{rx_mux}'. "
                            f"Valores válidos: 'null', 'mac', 'gen'"
                        )
                    print(f"✓ RX MUX configurado\n")

                if tx_mux is not None:
                    print(f"  Puerto {port_id} - TX MUX: {tx_mux}")
                    if tx_mux == "null":
                        port.set_tx_null_mux()
                    elif tx_mux == "mac":
                        port.set_tx_mac_mux()
                    else:
                        raise ValueError(
                            f"tx_mux inválido: '{tx_mux}'. "
                            f"Valores válidos: 'null', 'mac'"
                        )
                    print(f"✓ TX MUX configurado\n")

        except Exception as e:
            raise RuntimeError(
                f"Error al configurar multiplexores del puerto {port_id}: {e}"
            )
    def set_generator_traffic(self,
        port_id: int,
        enabled: bool,
        length: int,
        counter: int,
        counter_frac: int,
        target: int,
    ) -> None:
        if not self.traffic_generator:
            raise RuntimeError("TrafficGenerator no inicializado")
        if port_id  not in self.traffic_generator.port_dict:
              available = list(self.traffic_generator.port_dict.keys())
              raise ValueError(f"Puerto {port_id} no existe. Puertos disponibles: {available}")
        port = self.traffic_generator.port_dict[port_id]

        if not (0 <= target < port.GEN_TRAFFIC_COMMON_COUNT):
            raise ValueError(
                f"target {target} fuera de rango"
            )
        try:
            with self._lock:
                if enabled:
                    port.set_rx_gen_mux()
                    port.set_tx_mac_mux()
                    port.create_rx_gen_basic_counter(
                        target=target,
                        counter=counter,
                        counter_frac=counter_frac,
                        length=length,
                        destination_mac_address=0x001122334455,
                        source_mac_address=0xAABBCCDDEEFF,
                        ether_type=0x0800,
                    )
                else:
                    port.delete_rx_gen_common_counter(target=target)
        except Exception as e:
            raise RuntimeError(f"Error al configurar el flujo {target} del puerto {port_id}: {e}")
    def get_clk_freq(self, port_id: int) -> float:
        if not self.traffic_generator:
            raise RuntimeError("TrafficGenerator no inicializado")
        if port_id not in self.traffic_generator.port_dict:
            raise ValueError(f"Puerto {port_id} no existe")
        return self.clk_freq

    def get_counter_frac_width(self, port_id: int) -> int:
        if not self.traffic_generator:
            raise RuntimeError("TrafficGenerator no inicializado")
        if port_id not in self.traffic_generator.port_dict:
            raise ValueError(f"Puerto {port_id} no existe")
        return self.traffic_generator.port_dict[port_id].GEN_COUNTER_FRAC_WIDTH

    # ========================================================================
    # MÉTODOS ADICIONALES ÚTILES
    # ========================================================================
    
    def get_port_info(self, port_id: int) -> dict:
        """
        Obtiene información detallada de un puerto.
        
        Útil para debugging y diagnóstico.
        
        Args:
            port_id: ID del puerto
        
        Returns:
            Dict con información del puerto
        """
        if port_id not in self.traffic_generator.port_dict:
            raise ValueError(f"Puerto {port_id} no existe")
        
        port = self.traffic_generator.port_dict[port_id]
        
        return {
            "port_id": port.PORT_ID,
            "port_rate_mbps": port.PORT_RATE,
            "port_rate_gbps": port.PORT_RATE / 1000,
            "rx_enabled": bool(port.RX_TRAFFIC_ENABLE),
            "tx_enabled": bool(port.TX_TRAFFIC_ENABLE),
            "gen_enabled": bool(port.GEN_TRAFFIC_ENABLE),
            "generators_count": port.GEN_TRAFFIC_COMMON_COUNT,
            "counter_width": port.GEN_COUNTER_WIDTH,
            "counter_frac_width": port.GEN_COUNTER_FRAC_WIDTH,
            "min_frame_length": port.GEN_MIN_FRAME_LENGTH,
            "read_width": port.READ_WIDTH,
        }

    def get_board_registers(self) -> dict:
        """
        Diagnostico: registros crudos de nivel de placa (offset 0x0), leidos
        directamente sin pasar por Port/TrafficGenerator. Compara esto entre
        configuraciones (normal vs. dfx_normal vs. dfx_vlan) para ver si el
        bloque de puertos o el de switch/FCL se desplazaron de direccion.
        """
        if not self.node:
            raise RuntimeError("TrafficGenerator no inicializado")

        read = self.node.read
        return {
            "port_enable_count": read_conf_reg_int(read_func=read, offset=0x0, address=RB_BOARD_REG_PORT_ENABLE_COUNT),
            "port_25g_count": read_conf_reg_int(read_func=read, offset=0x0, address=RB_BOARD_REG_PORT_25G_COUNT),
            "port_100g_count": read_conf_reg_int(read_func=read, offset=0x0, address=RB_BOARD_REG_PORT_100G_COUNT),
            "port_offset": read_conf_reg_int(read_func=read, offset=0x0, address=RB_BOARD_REG_PORT_OFFSET),
            "port_stride": read_conf_reg_int(read_func=read, offset=0x0, address=RB_BOARD_REG_PORT_STRIDE),
            "switch_count": read_conf_reg_int(read_func=read, offset=0x0, address=RB_BOARD_REG_SWITCH_COUNT),
            "switch_offset": read_conf_reg_int(read_func=read, offset=0x0, address=RB_BOARD_REG_SWITCH_OFFSET),
            "switch_stride": read_conf_reg_int(read_func=read, offset=0x0, address=RB_BOARD_REG_SWITCH_STRIDE),
        }

    def __del__(self):
        """Cleanup al destruir el objeto"""
        if self.interface:
            try:
                print("\n🔌 Cerrando conexión con FPGA...")
            except:
                pass
