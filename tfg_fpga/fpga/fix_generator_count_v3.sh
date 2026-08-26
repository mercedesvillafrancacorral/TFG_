#!/bin/bash

# Igual que v2 pero corrigiendo el bug real: modifica solo
# PORT_GEN_TRAFFIC_COMMON_COUNT dentro de la lista de generics existente,
# en vez de reemplazar toda la lista (lo que borraba el resto de generics
# y los dejaba en sus valores por defecto del RTL, causando el fallo de
# VC_SUM/axis_async_fifo que vimos en v1 y v2 - nada que ver con el valor 10).
# execution example: nohup bash fix_generator_count_v3.sh > fix_generator_count_v3.log 2>&1 &

source /opt/Xilinx/Vivado/2024.1/settings64.sh
vivado -nojournal -nolog -mode batch -source fix_generator_count_v3.tcl
