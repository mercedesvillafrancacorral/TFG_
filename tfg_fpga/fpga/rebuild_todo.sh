#!/bin/bash
set -e
echo "########## 1. PROYECTO ##########"
bash fix_generator_count_v4_noram.sh
echo "########## 2. CADENA DFX ##########"
cd ~/traffic_generator_mercedes/fpga/tool/ZCU102/fpga_traffic_generator/fpga
bash dfx_rebuild_v3.sh
echo "########## 3. PROBES ##########"
source /opt/Xilinx/Vivado/2024.1/settings64.sh
vivado -nojournal -nolog -mode batch -source gen_ltx_v3.tcl
echo "########## TODO LISTO ##########"
