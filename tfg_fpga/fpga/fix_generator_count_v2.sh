#!/bin/bash

# Igual que fix_generator_count.sh pero contra fpga.xpr (el proyecto real,
# confirmado por tener el fileset vio_dfx_ctrl que project_1.xpr no tenia).
# execution example: nohup bash fix_generator_count_v2.sh > fix_generator_count_v2.log 2>&1 &

source /opt/Xilinx/Vivado/2024.1/settings64.sh
vivado -nojournal -nolog -mode batch -source fix_generator_count_v2.tcl
