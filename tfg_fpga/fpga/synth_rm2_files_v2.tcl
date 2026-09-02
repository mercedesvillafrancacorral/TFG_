# Sintesis out-of-context del modulo reconfigurable (port_sync) para DFX.


read_verilog defines.v
read_verilog ../rtl/fpga.v
read_verilog ../rtl/fpga_core.v
read_verilog ../rtl/traffic_generator.v
read_verilog ../../../../common/rtl/port_sync.v
read_verilog ../../../../common/rtl/port_rx.v
read_verilog ../../../../common/rtl/port_traffic_gen_v2.v
read_verilog ../../../../common/rtl/port_tx.v
read_verilog ../rtl/eth_xcvr_phy_wrapper.v
read_verilog ../rtl/eth_xcvr_phy_quad_wrapper.v
read_verilog ../rtl/debounce_switch.v
read_verilog ../rtl/sync_signal.v
read_verilog ../lib/switch/lib/eth/rtl/eth_mac_10g_fifo.v
read_verilog ../lib/switch/lib/eth/rtl/eth_mac_10g.v
read_verilog ../lib/switch/lib/eth/rtl/axis_xgmii_rx_64.v
read_verilog ../lib/switch/lib/eth/rtl/axis_xgmii_tx_64.v
read_verilog ../lib/switch/lib/eth/rtl/eth_phy_10g.v
read_verilog ../lib/switch/lib/eth/rtl/eth_phy_10g_rx.v
read_verilog ../lib/switch/lib/eth/rtl/eth_phy_10g_rx_if.v
read_verilog ../lib/switch/lib/eth/rtl/eth_phy_10g_rx_frame_sync.v
read_verilog ../lib/switch/lib/eth/rtl/eth_phy_10g_rx_ber_mon.v
read_verilog ../lib/switch/lib/eth/rtl/eth_phy_10g_rx_watchdog.v
read_verilog ../lib/switch/lib/eth/rtl/eth_phy_10g_tx.v
read_verilog ../lib/switch/lib/eth/rtl/eth_phy_10g_tx_if.v
read_verilog ../lib/switch/lib/eth/rtl/xgmii_baser_dec_64.v
read_verilog ../lib/switch/lib/eth/rtl/xgmii_baser_enc_64.v
read_verilog ../lib/switch/lib/axis/rtl/sync_reset.v
read_verilog ../lib/switch/lib/corundum/rb_drp.v
read_verilog ../lib/switch/lib/corundum/cmac_gty_wrapper.v
read_verilog ../lib/switch/lib/corundum/cmac_gty_ch_wrapper.v
read_verilog ../lib/switch/lib/corundum/cmac_pad.v
read_verilog ../lib/switch/lib/corundum/mac_ts_insert.v
read_verilog ../lib/switch/lib/uart/rtl/uart.v
read_verilog ../lib/switch/lib/uart/rtl/uart_rx.v
read_verilog ../lib/switch/lib/uart/rtl/uart_tx.v
read_verilog ../lib/switch/lib/xfcp/rtl/xfcp_interface_uart.v
read_verilog ../lib/switch/lib/xfcp/rtl/xfcp_mod_axil.v
read_verilog ../lib/switch/lib/axi/rtl/axil_crossbar_wr.v
read_verilog ../lib/switch/lib/axi/rtl/axil_crossbar_rd.v
read_verilog ../lib/switch/lib/axi/rtl/axil_crossbar_addr.v
read_verilog ../lib/switch/lib/axi/rtl/axil_register_rd.v
read_verilog ../lib/switch/lib/axi/rtl/axil_register_wr.v
read_verilog ../lib/switch/lib/axi/rtl/axil_register.v
read_verilog ../lib/switch/lib/axi/rtl/axil_crossbar.v
read_verilog ../lib/switch/lib/axis/rtl/axis_cobs_encode.v
read_verilog ../lib/switch/lib/axis/rtl/axis_cobs_decode.v
read_verilog ../lib/switch/lib/axis/rtl/axis_fifo.v
read_verilog ../lib/switch/lib/axis/rtl/axis_adapter.v
read_verilog ../lib/switch/lib/axis/rtl/axis_async_fifo.v
read_verilog ../lib/switch/lib/axis/rtl/axis_async_fifo_adapter.v
read_verilog ../lib/switch/lib/axis/rtl/priority_encoder.v
read_verilog ../lib/switch/lib/axis/rtl/arbiter.v
read_verilog ../lib/switch/lib/eth/rtl/lfsr.v
read_verilog ../lib/switch/lib/axi/rtl/axil_reg_if_rd.v
read_verilog ../lib/switch/lib/axi/rtl/axil_reg_if_wr.v
read_verilog ../lib/switch/lib/axi/rtl/axil_reg_if.v

synth_design -mode out_of_context -top port_sync \
    -generic AXIS_DATA_WIDTH=512 \
    -generic AXIS_KEEP_WIDTH=64 \
    -generic PORT_ID=0 \
    -generic PORT_RATE=10000 \
    -generic READ_WIDTH=64 \
    -generic RX_TRAFFIC_ENABLE=1 \
    -generic TX_TRAFFIC_ENABLE=1 \
    -generic GEN_TRAFFIC_ENABLE=1 \
    -generic GEN_TRAFFIC_COMMON_COUNT=10 \
    -generic GEN_TRAFFIC_RAM_COUNT=0 \
    -generic GEN_TRAFFIC_RAM_TARGET_COUNT=512 \
    -generic GEN_COUNTER_WIDTH=16 \
    -generic GEN_COUNTER_FRAC_WIDTH=16 \
    -generic GEN_MIN_FRAME_LENGTH=60 \
    -generic GEN_OUTPUT_REGISTER=1 \
    -generic AXIL_DATA_WIDTH=32 \
    -generic AXIL_ADDR_WIDTH=12 \
    -generic AXIL_STRB_WIDTH=4

write_checkpoint -force rm2_synth.dcp
