#!/bin/bash

# Prueba de control: vuelve PORT_GEN_TRAFFIC_COMMON_COUNT a 3 (el valor original)
# y fuerza una sintesis limpia igualmente, para aislar si el fallo de VC_SUM /
# axis_async_fifo es preexistente (independiente del generic) o especifico de 10.
# Solo sintesis (no implementacion/bitstream), deberia tardar ~5 min.
# execution example: nohup bash test_clean_synth_baseline.sh > test_clean_synth_baseline.log 2>&1 &

source /opt/Xilinx/Vivado/2024.1/settings64.sh
vivado -nojournal -nolog -mode batch -source test_clean_synth_baseline.tcl
