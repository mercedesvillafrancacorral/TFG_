#!/bin/bash

# Comprueba que Vivado puede conectar con hw_server y ver el dispositivo JTAG,
# sin programar nada. Util para verificar que Vivado sigue sano tras un fallo
# (p.ej. un segfault) antes de reintentar una reconfiguracion real.
# execution example: bash check_hw_health.sh

source /opt/Xilinx/Vivado/2024.1/settings64.sh
vivado -nojournal -nolog -mode batch -source check_hw_health.tcl
