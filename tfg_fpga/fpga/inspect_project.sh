#!/bin/bash

# Inspecciona filesets/runs de project_1.xpr, para saber donde vive de verdad
# PORT_GEN_TRAFFIC_COMMON_COUNT antes de tocarlo. Solo lectura, no sintetiza nada.
# execution example: bash inspect_project.sh

source /opt/Xilinx/Vivado/2024.1/settings64.sh
vivado -nojournal -nolog -mode batch -source inspect_project.tcl
