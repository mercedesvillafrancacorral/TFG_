#!/bin/bash

# Como v3 (PORT_GEN_TRAFFIC_COMMON_COUNT=10) pero con PORT_GEN_TRAFFIC_RAM_COUNT=0,
# para aislar si el generador basado en RAM es lo que impide que el generador
# arranque. Con RAM_COUNT=0 el mapa de registros vuelve al "clasico", que es el
# unico con el que se ha visto trafico real.
# execution example: nohup bash fix_generator_count_v4_noram.sh > fix_v4_noram.log 2>&1 &

source /opt/Xilinx/Vivado/2024.1/settings64.sh
vivado -nojournal -nolog -mode batch -source fix_generator_count_v4_noram.tcl
