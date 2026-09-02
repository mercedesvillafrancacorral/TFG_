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


class FailingProgrammer:
    def program(self, bit_filename: str) -> None:
        raise OSError("vivado no responde")

    def run_vio_script(self, script_name: str) -> None:
        pass


def test_list_configs_returns_known_names():
    service = FpgaDfxConfigService(Programmer(), CountersService())
    assert service.list_configs() == [
    "normal",
    "dfx_estatica",
    "dfx_dinamica_vlan",
    "dfx_dinamica_5_generadores_p0",
    "dfx_dinamica_2_generadores_p0",
]

def test_load_normal_config_does_not_touch_vio():
    programmer = Programmer()
    service = FpgaDfxConfigService(programmer, CountersService())

    service.load_config("normal")

    assert programmer.calls == [("program", "fpga.bit")]


def test_load_dfx_config_follows_decouple_program_reset_order():
    programmer = Programmer()
    service = FpgaDfxConfigService(programmer, CountersService())

    service.load_config("dfx_dinamica_vlan")

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

    assert service.load_config("dfx_dinamica_vlan") is True


def test_load_config_reconnects_hardware_after_programming(monkeypatch):
    monkeypatch.setattr(fpga_dfx_config_service_module.time, "sleep", lambda _seconds: None)
    hardware = Hardware()
    service = FpgaDfxConfigService(Programmer(), CountersService(), hardware)

    service.load_config("dfx_dinamica_vlan")

    assert hardware.begin_calls == 1
    assert hardware.finish_calls == 1
    assert hardware.register_layout is True


def test_load_normal_config_uses_classic_register_layout(monkeypatch):
    monkeypatch.setattr(fpga_dfx_config_service_module.time, "sleep", lambda _seconds: None)
    hardware = Hardware()
    service = FpgaDfxConfigService(Programmer(), CountersService(), hardware)

    service.load_config("normal")

    assert hardware.register_layout is False

def test_load_dfx_two_generators_uses_expected_partial_bitstream():
    programmer = Programmer()
    service = FpgaDfxConfigService(programmer, CountersService())

    service.load_config("dfx_dinamica_2_generadores_p0")

    assert programmer.calls == [
        ("vio", "vio_decouple_on.tcl"),
        ("program", "config2_generators2_v5_partial.bit"),
        ("vio", "vio_pulse_reset.tcl"),
    ]

def test_load_dfx_five_generators_uses_expected_partial_bitstream():
    programmer = Programmer()
    service = FpgaDfxConfigService(programmer, CountersService())

    service.load_config("dfx_dinamica_5_generadores_p0")

    assert programmer.calls == [
        ("vio", "vio_decouple_on.tcl"),
        ("program", "config2_generators5_v4_partial.bit"),
        ("vio", "vio_pulse_reset.tcl"),
    ]

def test_is_current_config_dfx_is_none_before_any_load():
    service = FpgaDfxConfigService(Programmer(), CountersService())
    assert service.is_current_config_dfx() is None

def test_is_current_config_dfx_true_for_dfx_config():
    service = FpgaDfxConfigService(Programmer(), CountersService())
    service.load_config("dfx_dinamica_vlan")
    assert service.is_current_config_dfx() is True

def test_is_current_config_dfx_false_for_normal_config():
    service = FpgaDfxConfigService(Programmer(), CountersService())
    service.load_config("normal")
    assert service.is_current_config_dfx() is False


def test_load_config_wraps_programmer_failure_in_runtime_error():
    service = FpgaDfxConfigService(FailingProgrammer(), CountersService())

    with pytest.raises(RuntimeError, match="dfx_dinamica_vlan"):
        service.load_config("dfx_dinamica_vlan")


def test_current_config_resets_to_none_after_programmer_failure():
    service = FpgaDfxConfigService(Programmer(), CountersService())
    service.load_config("dfx_estatica")

    service.programmer = FailingProgrammer()
    with pytest.raises(RuntimeError):
        service.load_config("dfx_dinamica_vlan")

    assert service.get_current_config() is None
    assert service.is_current_config_dfx() is None
