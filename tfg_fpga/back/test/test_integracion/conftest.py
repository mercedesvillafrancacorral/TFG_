""" Pieza de configuración reutilizable entre todos los tests """

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from back.port.application.PortCountersService import PortCountersService
from back.port.application.PortCountersRepository import PortCountersRepository
from back.port.domain.PortCounters import PortCounters

# Para simular el servicio de Elasticsearch se utiliza MagicMock.
sim_elasticsearch = MagicMock()
sim_elasticsearch.ping.return_value = True
patch("elasticsearch.Elasticsearch", return_value=sim_elasticsearch).start()

import sys
import types

_sim_hardware_module = types.ModuleType(
    "back.port.infrastructure.outbound.mock_port_hardware_adapter"
)


class _DummyPortHardwareAdapter:
    def __init__(self, port_count=4):
        pass


_sim_hardware_module.PortHardwareAdapter = _DummyPortHardwareAdapter
sys.modules["back.port.infrastructure.outbound.mock_port_hardware_adapter"] = _sim_hardware_module

from main import app
from back.port.infrastructure.inbound.api.dependencies import get_port_service
from back.dfx.infrastructure.inbound.dependencies import get_fpga_dfx_config_service


class _SimHardware:
    """Sustituto de hardware para los tests: en vez de una FPGA real, devuelve
    siempre valores fijos y no hace nada al configurar (solo lo apunta en
    self.calls). Así el test es 100% predecible, sin depender de hardware
    ni de simuladores con comportamiento variable en el tiempo.
    """
    def __init__(self, ports=(0, 1, 2, 3)):
        self._ports = list(ports)
        self.calls = []

    def get_ports(self):
        return self._ports

    def read_counters(self, port_id):
        return PortCounters(
            rx_port_in_frames=0,
            rx_port_out_frames=0,
            rx_port_gen_frames=0,
            rx_port_in_true_frames=0,
            rx_port_gen_true_frames=0,
            tx_port_in_frames=0,
            tx_port_out_frames=0,
            tx_port_in_true_frames=0,
        )

    def set_generator(self, **kwargs):
        self.calls.append(("set_generator", kwargs))  # no-op, solo queda registrado

    def set_generator_traffic(self, **kwargs):
        self.calls.append(("set_generator_traffic", kwargs))

    def set_mux(self, **kwargs):
        self.calls.append(("set_mux", kwargs))

    def get_clk_freq(self, port_id):
        return 156_250_000  # valor fijo, igual que en los tests unitarios

    def get_counter_frac_width(self, port_id):
        return 16


class _SimRepository(PortCountersRepository):
    """Doble del repositorio: no escribe en ningún sitio, solo cumple la interfaz."""

    def save(self, port_id, counters, info=None):
        pass  # normalmente escribiría en Elasticsearch; aquí no hace nada

    def get_history(self, port_id, limit=100):
        return []

    def get_latest(self, port_id):
        return None


@pytest.fixture
def api_service():
    return PortCountersService(_SimHardware(), _SimRepository())


@pytest.fixture
def client(api_service):
    app.dependency_overrides[get_port_service] = lambda: api_service

    with TestClient(app) as c:
        yield c  # el test recibe "c" (client) aquí y hace sus peticiones

    app.dependency_overrides.clear()


class _SimDfxService:
    def __init__(self, configs=None, link_ready=True, raise_on=None, dfx_configs=None):
        self._configs = configs or ["normal", "dfx_dinamica_vlan"]
        self._link_ready = link_ready
        self._raise_on = raise_on or {}
        self._dfx_configs = dfx_configs or {"dfx_dinamica_vlan"}
        self._current = None

    def list_configs(self):
        return self._configs

    def load_config(self, name):
        if name in self._raise_on:
            self._current = None
            raise self._raise_on[name]
        if name not in self._configs:
            raise ValueError(f"Configuración desconocida: {name}")
        self._current = name
        return self._link_ready

    def get_current_config(self):
        return self._current

    def is_current_config_dfx(self):
        if self._current is None:
            return None
        return self._current in self._dfx_configs


@pytest.fixture
def dfx_client():
    sim_service = _SimDfxService()
    app.dependency_overrides[get_fpga_dfx_config_service] = lambda: sim_service

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def dfx_client_with_failure():
    sim_service = _SimDfxService(
        configs=["normal", "config_falla"],
        raise_on={"config_falla": RuntimeError("fallo simulado del programador")},
    )
    app.dependency_overrides[get_fpga_dfx_config_service] = lambda: sim_service

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def dfx_client_link_not_ready():
    sim_service = _SimDfxService(link_ready=False)
    app.dependency_overrides[get_fpga_dfx_config_service] = lambda: sim_service

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
