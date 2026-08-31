from unittest.mock import MagicMock, patch

import pytest

from back.dfx.infrastructure.outbound.fx_fpga_programmer_adapter import (
    FPGA_DIR,
    VivadoFpgaProgrammerAdapter,
)


def _completed_process(returncode, stderr=""):
    result = MagicMock()
    result.returncode = returncode
    result.stderr = stderr
    return result


@patch("back.dfx.infrastructure.outbound.fx_fpga_programmer_adapter.subprocess.run")
def test_program_calls_program_sh_with_bit_path(mock_run):
    mock_run.return_value = _completed_process(0)
    adapter = VivadoFpgaProgrammerAdapter()

    adapter.program("config2_v2_partial.bit")

    args, kwargs = mock_run.call_args
    command = args[0]
    assert command[0] == "bash"
    assert command[1].endswith("program.sh")
    assert command[2].endswith("config2_v2_partial.bit")
    assert kwargs["cwd"] == FPGA_DIR


@patch("back.dfx.infrastructure.outbound.fx_fpga_programmer_adapter.subprocess.run")
def test_program_raises_runtime_error_on_failure(mock_run):
    mock_run.return_value = _completed_process(1, stderr="boom")
    adapter = VivadoFpgaProgrammerAdapter()

    with pytest.raises(RuntimeError):
        adapter.program("fpga.bit")


@patch("back.dfx.infrastructure.outbound.fx_fpga_programmer_adapter.subprocess.run")
def test_run_vio_script_sources_settings_and_runs_vivado_batch(mock_run):
    mock_run.return_value = _completed_process(0)
    adapter = VivadoFpgaProgrammerAdapter()

    adapter.run_vio_script("vio_decouple_on.tcl")

    args, kwargs = mock_run.call_args
    command = args[0]
    assert command[0] == "bash"
    assert command[1] == "-c"
    assert "settings64.sh" in command[2]
    assert "vivado" in command[2]
    assert "vio_decouple_on.tcl" in command[2]


@patch("back.dfx.infrastructure.outbound.fx_fpga_programmer_adapter.subprocess.run")
def test_run_vio_script_raises_runtime_error_on_failure(mock_run):
    mock_run.return_value = _completed_process(1, stderr="tcl error")
    adapter = VivadoFpgaProgrammerAdapter()

    with pytest.raises(RuntimeError):
        adapter.run_vio_script("vio_pulse_reset.tcl")