#!/bin/bash

# Cambia PORT_GEN_TRAFFIC_COMMON_COUNT a 10 en el fileset sources_1 y reconstruye
# synth_1 -> impl_1 (bitstream incluido). Tarda 30min-2h+. Pensado para lanzarse
# en segundo plano y no depender de que la terminal siga abierta.
# execution example: nohup bash fix_generator_count.sh > fix_generator_count.log 2>&1 &

source /opt/Xilinx/Vivado/2024.1/settings64.sh
vivado -nojournal -nolog -mode batch -source fix_generator_count.tcl
