#!/bin/bash

# Copyright 2024, Carlos Megías Núñez.
# execution example: bash program.sh

# default bitstream
default_bit="fpga.bit"

# read first argument: bitstream
bit=$1

if [ -z "$bit" ]; then
    echo "Warning: no bitstream specified, using default $default_bit"
    bit=$default_bit
fi

# make the parameter visible to tcl
export BIT_FILE=$bit

# call vivado
source /opt/Xilinx/Vivado/2024.1/settings64.sh
vivado -nojournal -nolog -mode batch -source program.tcl