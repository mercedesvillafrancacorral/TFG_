#!/usr/bin/env python
"""

Copyright (c) 2024-2025 Carlos Megías Núñez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

from math import log, ceil

# Configuration registers

## Common registers
RB_REG_TYPE                                  = 0x00
RB_REG_VER                                   = 0x04
RB_REG_NEXT_PTR                              = 0x08


## Board configuration
RB_BOARD_OFFSET                              = 0x0

RB_BOARD_TYPE                                = 0x00000001
RB_BOARD_VER                                 = 0x00000001

RB_BOARD_REG_PORT_ENABLE_COUNT               = 0x10
RB_BOARD_REG_PORT_25G_COUNT                  = 0x14
RB_BOARD_REG_PORT_100G_COUNT                 = 0x18
RB_BOARD_REG_PORT_OFFSET                     = 0x1C
RB_BOARD_REG_PORT_STRIDE                     = 0x20

RB_BOARD_REG_SWITCH_COUNT                    = 0x30
RB_BOARD_REG_SWITCH_OFFSET                   = 0x34
RB_BOARD_REG_SWITCH_STRIDE                   = 0x38

## Switch configuration
RB_SWITCH_TYPE                               = 0x00000002
RB_SWITCH_VER                                = 0x00000001
RB_SWITCH_CH_GLOBAL_COUNT                    = 0x10
RB_SWITCH_FCL_COUNT                          = 0x14
RB_SWITCH_ROW_COUNT                          = 0x18
RB_SWITCH_COL_COUNT                          = 0x1C

RB_SWITCH_FCL_OFFSET                         = 0x20
RB_SWITCH_FCL_STRIDE                         = 0x24

RB_SWITCH_VC_GLOBAL_COUNT_OFFSET             = 0x30
RB_SWITCH_FCL_X_CH_COUNT_OFFSET              = 0x34
RB_SWITCH_ROW_X_FCL_COUNT_OFFSET             = 0x38
RB_SWITCH_COL_X_FCL_COUNT_OFFSET             = 0x3C

RB_SWITCH_PRIO_COUNT                         = 0x40
RB_SWITCH_DROP_CORRUPTED_FRAMES              = 0x44
RB_SWITCH_EGRESS_PIPELINE_REGISTER           = 0x48
RB_SWITCH_INGRESS_FIFO_DEPTH                 = 0x4C
RB_SWITCH_EGRESS_FIFO_DEPTH                  = 0x50


## FCL configuration
RB_FCL_TYPE                                  = 0x00000003
RB_FCL_VER                                   = 0x00000001

RB_FCL_FEATURES                              = 0x0C
RB_FCL_CH_COUNT                              = 0x10
RB_FCL_CH_GLOBAL_OFFSET                      = 0x14
RB_FCL_CH_LOCAL_OFFSET                       = 0x18
RB_FCL_PORT_COUNT                            = 0x1C
RB_FCL_RX_FIFO_DEPTH                         = 0x20
RB_FCL_TX_FIFO_DEPTH                         = 0x24
RB_FCL_TABLE_DEPTH                           = 0x28
RB_FCL_TABLE_COUNT                           = 0x2C
RB_FCL_TABLE_PRIO_WIDTH                      = 0x30
RB_FCL_TABLE_LOOP_COUNT                      = 0x34
RB_FCL_PRIO_MAP                              = 0x38

RB_FCL_TABLE_INSERTION_INITIAL_FILTER        = 0x3C
RB_FCL_TABLE_INSERTION_INITIAL_STRATEGY      = 0x40
RB_FCL_TABLE_INSERTION_REALLOCATE_FILTER     = 0x44
RB_FCL_TABLE_INSERTION_REALLOCATE_STRATEGY   = 0x48

RB_FCL_TABLE_AGING_PERIOD_WIDTH              = 0x50
RB_FCL_TABLE_AGING_FREQ_WIDTH                = 0x54
RB_FCL_FID_COUNT                             = 0x58

RB_FCL_FEATURE_VLAN_ENABLE                   = (1 << 0)
RB_FCL_FEATURE_STATIC_ENABLE                 = (1 << 1)
RB_FCL_FEATURE_TABLE_PRIO_ENABLE             = (1 << 2)
RB_FCL_FEATURE_TABLE_AGING_ENABLE            = (1 << 3)
RB_FCL_FEATURE_TABLE_CONFIG_ENABLE           = (1 << 4)
RB_FCL_FEATURE_TABLE_REGISTER_STORE_STATE    = (1 << 5) | (1 << 6)
RB_FCL_FEATURE_TABLE_REGISTER_OUTPUT_INSERTION = (1 << 7)
RB_FCL_FEATURE_VLAN_LEARNING_TYPE            = (1 << 8) | (1 << 9)
RB_FCL_FEATURE_LOOPBACK_ENABLE               = (1 << 10)

# static port configuration
RB_FCL_STATIC_TYPE                           = 0x00000004
RB_FCL_STATIC_VER                            = 0x00000000

RB_FCL_STATIC_ADDRESS_VALID                  = 0x0C
RB_FCL_STATIC_VLAN_VALID                     = 0x10
RB_FCL_STATIC_TAG_VALID                      = 0x14
RB_FCL_STATIC_FID_VALID                      = 0x1C
RB_FCL_STATIC_ADDRESS_LOOKUP_VALID           = 0x20
RB_FCL_STATIC_ADDRESS_ACTIVE_COUNTER         = 0x24
RB_FCL_STATIC_ADDRESS_DELETE_COUNTER         = 0x28
RB_FCL_STATIC_VLAN_ACTIVE_COUNTER            = 0x2C
RB_FCL_STATIC_VLAN_DELETE_COUNTER            = 0x30
RB_FCL_STATIC_ADDRESS_LOOKUP_REQ_COMPLETE    = 0x34
RB_FCL_STATIC_ADDRESS_LOOKUP_REQ_DATA        = 0x38
RB_FCL_STATIC_ADDRESS_LOOKUP_RES_COMPLETE    = 0x50

RB_FCL_STATIC_WRITE_CONTROL                  = 0x00
RB_FCL_STATIC_WRITE_DATA                     = 0x04

# (data) port configuration
RB_FCL_PORT_TYPE                             = 0x00000005
RB_FCL_PORT_VER                              = 0x00000000

RB_FCL_PORT_RX_IN_COUNTER                    = 0x10
RB_FCL_PORT_RX_IN_DROP_COUNTER               = 0x14
RB_FCL_PORT_TX_OUT_COUNTER                   = 0x1C
RB_FCL_PORT_LOOKUP_COUNTER                   = 0x20
RB_FCL_PORT_WRITE_COUNTER                    = 0x24
RB_FCL_PORT_PPCP                             = 0x40
RB_FCL_PORT_PVID                             = 0x44
RB_FCL_PORT_INGRESS_FILT                     = 0x48
RB_FCL_PORT_LOOPBACK                         = 0x4C

# filtering database
RB_FCL_PORT_TYPE                             = 0x00000006
RB_FCL_PORT_VER                              = 0x00000000

RB_FD_MAX_LOOP_HIT_COUNTER                   = 0x1C
RB_FD_CURR_UTIL                              = 0x20
RB_FD_CURR_UTIL_T0                           = 0x24
RB_FD_CURR_UTIL_T1                           = 0x28
RB_FD_CURR_UTIL_T2                           = 0x2C
RB_FD_CURR_UTIL_T3                           = 0x30
RB_FD_CURR_UTIL_T4                           = 0x34
RB_FD_CLEAR                                  = 0x40
RB_FD_CLEAR_ADDRESS                          = 1 << 0
RB_FD_CLEAR_VLAN                             = 1 << 8
RB_FD_CLEAR_TAG                              = 1 << 16
RB_FD_CLEAR_FID                              = 1 << 24

RB_FD_ACC_UTIL                               = 0x44
RB_FD_MIN_UTIL                               = 0x48
RB_FD_MAX_UTIL                               = 0x4C
RB_FD_PERIOD_AGING                           = 0x50
RB_FD_FREQ_AGING                             = 0x54
RB_FD_PRIO_AGING                             = 0x58
RB_FD_ACTIVE_AGING                           = 0x5C

RB_FD_CONFIG_DEPTH_MASK                      = 0x60
RB_FD_CONFIG_TABLE_COUNT                     = 0x64
RB_FD_CONFIG_MAX_UTIL                        = 0x68
RB_FD_CONFIG_MAX_UTIL_TX_OUT_COUNTER         = 0x6C
RB_FD_CONFIG_MAX_LOOP_HIT_UTIL               = 0x70
RB_FD_CONFIG_MAX_LOOP_COUNT                  = 0x74

## Port module configuration
RB_PORT_TYPE                                 = 0x10000000
RB_PORT_VER                                  = 0x00000000

RB_PORT_ID                                   = 0x0C
RB_PORT_RATE                                 = 0x10
RB_PORT_FEATURES                             = 0x14
RB_PORT_RX_VALID                             = 0x18
RB_PORT_GEN_TRAFFIC_COMMON_COUNT             = 0x2C
RB_PORT_GEN_COUNTER_WIDTH                    = 0x30
RB_PORT_GEN_COUNTER_FRAC_WIDTH               = 0x34
RB_PORT_GEN_MIN_FRAME_LENGTH                 = 0x38
RB_PORT_READ_WIDTH                           = 0x3C

# Mapa alternativo: algunos bitstreams (p.ej. config1_v2.bit / config2_v2_partial.bit)
# tienen un port_sync.v que inserta dos registros de generador por RAM entre
# GEN_TRAFFIC_COMMON_COUNT y GEN_COUNTER_WIDTH, desplazando el resto del banco
# 2 registros respecto al mapa "clasico" de arriba (el que usa fpga.bit).
RB_PORT_GEN_TRAFFIC_RAM_COUNT_EXT            = 0x30
RB_PORT_GEN_TRAFFIC_RAM_TARGET_COUNT_EXT     = 0x34
RB_PORT_GEN_COUNTER_WIDTH_EXT                = 0x38
RB_PORT_GEN_COUNTER_FRAC_WIDTH_EXT           = 0x3C
RB_PORT_GEN_MIN_FRAME_LENGTH_EXT             = 0x40
RB_PORT_READ_WIDTH_EXT                       = 0x44

RB_PORT_RX_READ_COMPLETE                     = 0x50
RB_PORT_RX_READ_DATA                         = 0x54
RB_PORT_RX_READ_READY                        = 0x50

RB_PORT_TX_READ_COMPLETE                     = 0x80
RB_PORT_TX_READ_DATA                         = 0x84
RB_PORT_TX_READ_READY                        = 0x54

RB_PORT_FEATURE_RX_TRAFFIC_ENABLE            = (1 << 0)
RB_PORT_FEATURE_TX_TRAFFIC_ENABLE            = (1 << 1)
RB_PORT_FEATURE_GEN_TRAFFIC_ENABLE           = (1 << 2)
RB_PORT_FEATURE_GEN_OUTPUT_REGISTER          = (1 << 3)

RB_PORT_WRITE_CONTROL                        = 0x00
RB_PORT_WRITE_DATA                           = 0x04

# port rx
RB_PORT_RX_MUX                               = 0x00
RB_PORT_RX_PORT_OUT_FRAME_COUNTER            = 0x04
RB_PORT_RX_PORT_IN_FRAME_COUNTER             = 0x08
RB_PORT_RX_PORT_GEN_FRAME_COUNTER            = 0x0C
RB_PORT_RX_PORT_IN_TRUE_FRAME_COUNTER        = 0x10
RB_PORT_RX_PORT_GEN_TRUE_FRAME_COUNTER       = 0x14

# port tx
RB_PORT_TX_MUX                               = 0x00
RB_PORT_TX_PORT_OUT_FRAME_COUNTER            = 0x04
RB_PORT_TX_PORT_IN_FRAME_COUNTER             = 0x08
RB_PORT_TX_PORT_IN_TRUE_FRAME_COUNTER        = 0x0C










# Forwarding computation logic: switch_router.v / switch_router_port_static.v / switch_router_port.v / filtering_database.v
SWITCH_RB_STRIDE                             = 0x100

SWITCH_RB_ROUTER_CTRL_TYPE                   = 0x00000001
SWITCH_RB_ROUTER_CTRL_VER                    = 0x00000001
SWITCH_RB_ROUTER_CTRL_NEXT                   = 0x08

SWITCH_RB_ROUTER_CTRL_FEATURES               = 0x0C
SWITCH_RB_ROUTER_CTRL_PORT_COUNT             = 0x10
SWITCH_RB_ROUTER_CTRL_FIFO_DEPTH             = 0x14
SWITCH_RB_ROUTER_CTRL_TABLE_DEPTH            = 0x20
SWITCH_RB_ROUTER_CTRL_TABLE_COUNT            = 0x24
SWITCH_RB_ROUTER_CTRL_TABLE_PRIO_WIDTH       = 0x28
SWITCH_RB_ROUTER_CTRL_TABLE_LOOP_COUNT       = 0x2C
SWITCH_RB_ROUTER_CTRL_TABLE_AGING_PERIOD     = 0x30
SWITCH_RB_ROUTER_CTRL_TABLE_AGING_FREQ       = 0x34
SWITCH_RB_ROUTER_CTRL_TABLE_AGING_MAX_PRIO   = 0x38
SWITCH_RB_ROUTER_CTRL_FID_COUNT              = 0x3C
SWITCH_RB_ROUTER_CTRL_PRIO_MAP               = 0x40

SWITCH_RB_ROUTER_FEATURE_VLAN_ENABLE                 = (1 << 0)
SWITCH_RB_ROUTER_FEATURE_STATIC_ENABLE               = (1 << 1)
SWITCH_RB_ROUTER_FEATURE_TABLE_PRIO_ENABLE           = (1 << 2)
SWITCH_RB_ROUTER_FEATURE_TABLE_AGING_ENABLE          = (1 << 3)
SWITCH_RB_ROUTER_FEATURE_TABLE_CONFIG_ENABLE         = (1 << 4)
SWITCH_RB_ROUTER_FEATURE_TABLE_REGISTER_STORE_STATE  = (1 << 5)
SWITCH_RB_ROUTER_FEATURE_VLAN_LEARNING_TYPE          = (1 << 6) | (1 << 7)

SWITCH_RB_ROUTER_OFFSET = 0

# Static port
SWITCH_RB_STATIC_CTRL_TYPE                   = 0x00000002
SWITCH_RB_STATIC_CTRL_VER                    = 0x00000000
SWITCH_RB_STATIC_CTRL_NEXT                   = 0x08

SWITCH_RB_STATIC_CTRL_ADDRESS_VALID          = 0x0C
SWITCH_RB_STATIC_CTRL_VLAN_VALID             = 0x10
SWITCH_RB_STATIC_CTRL_TAG_VALID              = 0x14
SWITCH_RB_STATIC_CTRL_FID_VALID              = 0x1C
SWITCH_RB_STATIC_CTRL_ADDRESS_ACTIVE_COUNTER = 0x20
SWITCH_RB_STATIC_CTRL_ADDRESS_DELETE_COUNTER = 0x24
SWITCH_RB_STATIC_CTRL_VLAN_ACTIVE_COUNTER    = 0x28
SWITCH_RB_STATIC_CTRL_VLAN_DELETE_COUNTER    = 0x2C

SWITCH_RB_STATIC_CTRL_WRITE_CONTROL          = 0x00
SWITCH_RB_STATIC_CTRL_WRITE_DATA             = 0x04

# Port (switch)
SWITCH_RB_PORT_CTRL_TYPE                     = 0x00000003
SWITCH_RB_PORT_CTRL_VER                      = 0x00000000
SWITCH_RB_PORT_CTRL_NEXT                     = 0x08

SWITCH_RB_PORT_CTRL_LOOKUP_COUNTER           = 0x20
SWITCH_RB_PORT_CTRL_WRITE_COUNTER            = 0x24
SWITCH_RB_PORT_CTRL_PVID                     = 0x40
SWITCH_RB_PORT_CTRL_PPCP                     = 0x44

# Filtering database
SWITCH_RB_FD_CTRL_CURR_UTIL                  = 0x20
SWITCH_RB_FD_CTRL_CLEAR                      = 0x40
SWITCH_RB_FD_CTRL_ACC_UTIL                   = 0x44
SWITCH_RB_FD_CTRL_MIN_UTIL                   = 0x48
SWITCH_RB_FD_CTRL_MAX_UTIL                   = 0x4C
SWITCH_RB_FD_CTRL_PERIOD_AGING               = 0x50
SWITCH_RB_FD_CTRL_FREQ_AGING                 = 0x54
SWITCH_RB_FD_CTRL_CONFIG_DEPTH_MASK          = 0x58
SWITCH_RB_FD_CTRL_CONFIG_TABLE_COUNT         = 0x5C

SWITCH_RB_FD_CTRL_CLEAR_ADDRESS              = 1 << 0
SWITCH_RB_FD_CTRL_CLEAR_VLAN                 = 1 << 8
SWITCH_RB_FD_CTRL_CLEAR_TAG                  = 1 << 16
SWITCH_RB_FD_CTRL_CLEAR_FID                  = 1 << 24

# Control register dicts
SWITCH_RB_ROUTER = {
    "stride": SWITCH_RB_STRIDE,
    "type": SWITCH_RB_ROUTER_CTRL_TYPE,
    "ver": SWITCH_RB_ROUTER_CTRL_VER,
    "next": SWITCH_RB_ROUTER_CTRL_NEXT,
    
    "FEATURES": SWITCH_RB_ROUTER_CTRL_FEATURES,
    "PORT_COUNT": SWITCH_RB_ROUTER_CTRL_PORT_COUNT,
    "FIFO_DEPTH": SWITCH_RB_ROUTER_CTRL_FIFO_DEPTH,
    "TABLE_DEPTH": SWITCH_RB_ROUTER_CTRL_TABLE_DEPTH,
    "TABLE_COUNT": SWITCH_RB_ROUTER_CTRL_TABLE_COUNT,
    "TABLE_PRIO_WIDTH": SWITCH_RB_ROUTER_CTRL_TABLE_PRIO_WIDTH,
    "TABLE_LOOP_COUNT": SWITCH_RB_ROUTER_CTRL_TABLE_LOOP_COUNT,
    "TABLE_AGING_PERIOD": SWITCH_RB_ROUTER_CTRL_TABLE_AGING_PERIOD,
    "TABLE_AGING_FREQ": SWITCH_RB_ROUTER_CTRL_TABLE_AGING_FREQ,
    "TABLE_AGING_MAX_PRIO": SWITCH_RB_ROUTER_CTRL_TABLE_AGING_MAX_PRIO,
    "FID_COUNT": SWITCH_RB_ROUTER_CTRL_FID_COUNT,
    "PRIO_MAP": SWITCH_RB_ROUTER_CTRL_PRIO_MAP,
    
    "VLAN_ENABLE" : SWITCH_RB_ROUTER_FEATURE_VLAN_ENABLE,
    "STATIC_ENABLE" : SWITCH_RB_ROUTER_FEATURE_STATIC_ENABLE,
    "TABLE_PRIO_ENABLE" : SWITCH_RB_ROUTER_FEATURE_TABLE_PRIO_ENABLE,
    "TABLE_AGING_ENABLE" : SWITCH_RB_ROUTER_FEATURE_TABLE_AGING_ENABLE,
    "TABLE_CONFIG_ENABLE" : SWITCH_RB_ROUTER_FEATURE_TABLE_CONFIG_ENABLE,
    "TABLE_REGISTER_STORE_STATE" : SWITCH_RB_ROUTER_FEATURE_TABLE_REGISTER_STORE_STATE,
    "VLAN_LEARNING_TYPE" : SWITCH_RB_ROUTER_FEATURE_VLAN_LEARNING_TYPE,
}