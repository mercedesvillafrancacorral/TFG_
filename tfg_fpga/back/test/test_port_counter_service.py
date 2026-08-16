"""Tests unitarios de PortCountersService.

Verifican la lógica de negocio de la capa de aplicación (validaciones y
cálculo de métricas) de forma aislada, sin depender del hardware real ni
del banco de registros simulado (mock_register_bank), que incorpora un
hilo de auto-tick y estado global no apto para tests deterministas.

"""

import pytest
from back.port.application.PortCountersService import PortCountersService
from back.port.application.PortCountersRepository import PortCountersRepository
from back.port.domain.PortCounters import PortCounters


class Hardware:
    """ 
    Doble de test para el puerto i_port_hardware.

    Simula 4 puertos  con contadores siempre a cero. Los métodos de
    configuración (set_generator, set_generator_traffic, set_mux) son no-op:
    los tests de esta suite verifican la lógica de PortCountersService

    """

     def __init__(self, ports=(0, 1, 2, 3)):
        self._ports = list(ports)
        self.calls = []

     def set_generator(self, **kwargs):
        self.calls.append(("set_generator", kwargs))  # antes: pass

    def get_ports(self):
        """Devuelve los identificadores de puerto configurados."""
        return self._ports

    def read_counters(self, port_id):
        """Devuelve una lectura de contadores vacía (todo a cero)."""
        return _counters()


     def set_generator_traffic(self, **kwargs):
        self.calls.append(("set_generator_traffic", kwargs))  # antes: pass

     def set_mux(self, **kwargs):
        self.calls.append(("set_mux", kwargs))

    def get_clk_freq(self, port_id):
        """Devuelve una frecuencia de reloj fija (156.25 MHz) para los cálculos de ancho de banda."""
        return 156_250_000

    def get_counter_frac_width(self, port_id):
        """Devuelve una anchura fija (16 bits) para la parte fraccionaria del contador."""
        return 16


class Repository(PortCountersRepository):
    """Doble de test para el puerto port_counters_repository.
    """

    def save(self, port_id, counters, info=None):
        """No-op: no se verifica la persistencia en estos tests."""
        pass

    def get_history(self, port_id, limit=100):
        """Devuelve siempre una lista vacía."""
        return []

    def get_latest(self, port_id):
        """Devuelve siempre None (sin lecturas previas)."""
        return None


def _counters(rx_gen=0, rx_gen_true=0, tx_out=0, rx_in=0, rx_in_true=0, tx_in=0, tx_in_true=0, rx_out=0):
    """Construye un PortCounters de test con todos los contadores a cero por defecto.

    Args:
        rx_gen, rx_gen_true, tx_out, rx_in, rx_in_true, tx_in, tx_in_true, rx_out:
            Atajos con nombre corto para fijar solo los contadores relevantes
            en cada test, sin tener que repetir los ocho campos completos.

    Returns:
        Una instancia de PortCounters con los valores indicados.
    """
    return PortCounters(
        rx_port_in_frames=rx_in,
        rx_port_out_frames=rx_out,
        rx_port_gen_frames=rx_gen,
        rx_port_in_true_frames=rx_in_true,
        rx_port_gen_true_frames=rx_gen_true,
        tx_port_in_frames=tx_in,
        tx_port_out_frames=tx_out,
        tx_port_in_true_frames=tx_in_true,
    )


@pytest.fixture
def service():
    """PortCountersService construido sobre los dobles de test"""
    return PortCountersService(Hardware(), Repository())


def test_get_ports_returns_hardware_ports(service):
    """get_ports() debe delegar en el hardware y devolver sus puertos tal cual"""
    assert service.get_ports() == [0, 1, 2, 3]


def test_get_counters_rejects_unknown_port(service):
    """get_counters() debe rechazar un port_id que el hardware no reporta como disponible."""
    with pytest.raises(ValueError):
        service.get_counters(99)


def test_configure_generator_rejects_zero_length(service):
    """configure_generator() debe rechazar una longitud de trama de 0 bytes."""
    with pytest.raises(ValueError):
        service.configure_generator(0, enabled=True, length=0, counter=10, counter_frac=0)


def test_configure_generator_rejects_zero_counter(service):
    """configure_generator() debe rechazar una tasa de generación (counter) de 0."""
    with pytest.raises(ValueError):
        service.configure_generator(0, enabled=True, length=64, counter=0, counter_frac=0)


def test_configure_mux_rejects_invalid_rx_mode(service):
    """configure_mux() debe rechazar un modo RX fuera de {null, mac, gen}."""
    with pytest.raises(ValueError):
        service.configure_mux(0, rx_mux="not_a_mode", tx_mux=None)


def test_calculate_throughput_zero_when_no_new_frames(service):
    """El throughput debe ser 0 fps si los contadores no han variado entre dos lecturas."""
    c = _counters(rx_gen=100, tx_out=100)
    result = service.calculate_throughput(c, c, total_time=1.0)
    assert result["rx_port_gen_fps"] == 0
    assert result["tx_port_out_fps"] == 0


def test_calculate_packet_loss_rate_detects_dropped_frames(service):
    """El packet loss rate debe reflejar el porcentaje de tramas generadas que no se transmitieron."""
    prev = _counters(rx_gen=0, tx_out=0)
    curr = _counters(rx_gen=100, tx_out=90)
    result = service.calculate_packet_loss_rate(curr, prev)
    assert result["packet_loss_rate"] == pytest.approx(10.0)


def test_calculate_frame_error_rate_detects_invalid_frames(service):
    """El frame error rate debe reflejar el porcentaje de tramas generadas que no son válidas."""
    prev = _counters(rx_gen=0, rx_gen_true=0)
    curr = _counters(rx_gen=100, rx_gen_true=95)
    result = service.calculate_frame_error_rate(curr, prev)
    assert result["frame_error_rate"] == pytest.approx(5.0)

def test_configure_generator_calls_hardware_when_valid(service):
    """Con parámetros válidos, configure_generator() debe invocar hardware.set_generator()."""
    service.configure_generator(0, enabled=True, length=128, counter=10, counter_frac=0)
    assert ("set_generator", {"port_id": 0, "enabled": True, "length": 128, "counter": 10, "counter_frac": 0}) in service.hardware.calls
def test_get_counters_persists_reading(service):
    """get_counters() debe guardar la lectura en el repositorio, no solo devolverla."""
    service.get_counters(0)
    assert len(service.repository.saved) == 1
    saved_port_id, _, _ = service.repository.saved[0]
    assert saved_port_id == 0


def test_calculate_packet_loss_rate_empty_when_no_new_frames(service):
    """Sin tramas generadas nuevas desde la lectura anterior, no debe calcularse packet_loss_rate."""
    prev = _counters(rx_gen=100, tx_out=90)
    curr = _counters(rx_gen=100, tx_out=90)
    result = service.calculate_packet_loss_rate(curr, prev)
    assert result == {}


def test_calculate_frame_error_rate_empty_when_no_new_frames(service):
    """Sin tramas generadas nuevas desde la lectura anterior, no debe calcularse frame_error_rate."""
    prev = _counters(rx_gen=100, rx_gen_true=95)
    curr = _counters(rx_gen=100, rx_gen_true=95)
    result = service.calculate_frame_error_rate(curr, prev)
    assert result == {}


def test_calculate_bandwidth_params_returns_positive_counter(service):
    """Para un ancho de banda objetivo válido, debe devolver un counter positivo y un counter_frac no negativo."""
    counter, counter_frac = service.calculate_bandwidth_params(
        clk_freq=156_250_000, bandwidth_gbps=1.0, frame_length=64, frac_width=16
    )
    assert counter > 0
    assert counter_frac >= 0
