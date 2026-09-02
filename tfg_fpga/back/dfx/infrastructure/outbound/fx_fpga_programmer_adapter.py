import os
import subprocess
from back.dfx.application.i_fpga_dfx_programmer import IFpgaDfxProgrammer

FPGA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "fpga")
)


class VivadoFpgaProgrammerAdapter(IFpgaDfxProgrammer):
    def program(self, bit_filename: str) -> None:
        script = os.path.join(FPGA_DIR, "program.sh")
        bit_path = os.path.join(FPGA_DIR, bit_filename)
        result = subprocess.run(
            ["bash", script, bit_path],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=FPGA_DIR,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Error al programar la FPGA: {result.stderr[-2000:]}")

    def run_vio_script(self, script_name: str) -> None:
        cmd = (
            "source /opt/Xilinx/Vivado/2024.1/settings64.sh && "
            f"vivado -nojournal -nolog -mode batch -source {script_name}"
        )
        result = subprocess.run(
            ["bash", "-c", cmd],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=FPGA_DIR,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Error ejecutando {script_name}: {result.stderr[-2000:]}")