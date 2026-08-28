import pytest

from back.dfx.application import fpga_dfx_config_service as fpga_dfx_config_service_module
from back.dfx.application.fpga_dfx_config_service import FpgaDfxConfigService


class Hardware:
    def __init__(self):
        self.begin_calls = 0
        self.finish_calls = 0
        self.register_layout = None

    def begin_reconfiguration(self):
        self.begin_calls += 1

    def finish_reconfiguration(self):
        self.finish_calls += 1

    def set_register_layout(self, extended: bool) -> None:
        self.register_layout = extended


class Programmer:
    def __init__(self):
        self.calls = []

    def program(self, bit_filename: str) -> None:
        self.calls.append(("program", bit_filename))

    def run_vio_script(self, script_name: str) -> None:
        self.calls.append(("vio", script_name))


class CountersService:
    def __init__(self, link_ready: bool = True):
        self.link_ready = link_ready

    def wait_for_retry_connection(self) -> bool:
        return self.link_ready


def test_list_configs_returns_known_names():
    service = FpgaDfxConfigService(Programmer(), CountersService())
    assert service.list_configs() == ["normal", "dfx_normal", "dfx_vlan"]


def test_load_normal_config_does_not_touch_vio():
    programmer = Programmer()
    service = FpgaDfxConfigService(programmer, CountersService())

    service.load_config("normal")

    assert programmer.calls == [("program", "fpga.bit")]


def test_load_dfx_config_follows_decouple_program_reset_order():
    programmer = Programmer()
    service = FpgaDfxConfigService(programmer, CountersService())

    service.load_config("dfx_vlan")

    assert programmer.calls == [
        ("vio", "vio_decouple_on.tcl"),
       ("program", "config2_v3_partial.bit"),
        ("vio", "vio_pulse_reset.tcl"),
    ]


def test_load_unknown_config_raises_value_error():
    service = FpgaDfxConfigService(Programmer(), CountersService())

    with pytest.raises(ValueError):
        service.load_config("no_existe")


def test_load_config_propagates_link_ready_result():
    service_ready = FpgaDfxConfigService(Programmer(), CountersService(link_ready=True))
    service_not_ready = FpgaDfxConfigService(Programmer(), CountersService(link_ready=False))

    assert service_ready.load_config("normal") is True
    assert service_not_ready.load_config("normal") is False


def test_load_config_without_hardware_skips_reconnect():
    service = FpgaDfxConfigService(Programmer(), CountersService())

    assert service.load_config("dfx_vlan") is True


def test_load_config_reconnects_hardware_after_programming(monkeypatch):
    monkeypatch.setattr(fpga_dfx_config_service_module.time, "sleep", lambda _seconds: None)
    hardware = Hardware()
    service = FpgaDfxConfigService(Programmer(), CountersService(), hardware)

    service.load_config("dfx_vlan")

    assert hardware.begin_calls == 1
    assert hardware.finish_calls == 1
    assert hardware.register_layout is True


def test_load_normal_config_uses_classic_register_layout(monkeypatch):
    monkeypatch.setattr(fpga_dfx_config_service_module.time, "sleep", lambda _seconds: None)
    hardware = Hardware()
    service = FpgaDfxConfigService(Programmer(), CountersService(), hardware)

    service.load_config("normal")

    assert hardware.register_layout is False