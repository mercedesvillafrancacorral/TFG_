set project_path "/home/mvillafranca/traffic_generator_mercedes/fpga/tool/ZCU102/fpga_traffic_generator/fpga/fpga.xpr"
open_project $project_path

puts "Generic antes: [get_property generic [get_filesets sources_1]]"

# Igual que v3 (PORT_GEN_TRAFFIC_COMMON_COUNT=10) pero con
# PORT_GEN_TRAFFIC_RAM_COUNT=0, para volver al mapa de registros "clasico"
# que es el unico con el que se ha visto trafico real (fpga.bit original).
# Sirve para aislar si el generador basado en RAM es lo que impide que el
# generador arranque, o si el problema es independiente de eso.
set full_generics [list \
    "AXIS_ETH_100G_DATA_WIDTH=512" \
    "AXIS_ETH_100G_KEEP_WIDTH=64" \
    "AXIS_ETH_25G_DATA_WIDTH=64" \
    "AXIS_ETH_25G_KEEP_WIDTH=8" \
    {PHY_ENABLE=4'b1111} \
    {PORT_ENABLE=4'b1111} \
    "PORT_READ_WIDTH=64" \
    "PORT_RX_TRAFFIC_ENABLE=1" \
    "PORT_TX_TRAFFIC_ENABLE=1" \
    "PORT_GEN_TRAFFIC_ENABLE=1" \
    "PORT_GEN_TRAFFIC_COMMON_COUNT=10" \
    "PORT_GEN_TRAFFIC_RAM_COUNT=0" \
    "PORT_GEN_TRAFFIC_RAM_TARGET_COUNT=512" \
    "PORT_GEN_COUNTER_WIDTH=16" \
    "PORT_GEN_COUNTER_FRAC_WIDTH=16" \
    "PORT_GEN_MIN_FRAME_LENGTH=60" \
    "PORT_GEN_OUTPUT_REGISTER=1" \
    "CH_COUNT=4" \
    {VC_COUNT=32'h01010101} \
    {VC_RATE=32'h00000000} \
    "INGRESS_25G_FIFO_DEPTH=2048" \
    "EGRESS_25G_FIFO_DEPTH=16384" \
    "INGRESS_100G_FIFO_DEPTH=2048" \
    "EGRESS_100G_FIFO_DEPTH=16384" \
    "INTERMEDIATE_FREQUENCY=250000000" \
    "BAUD_RATE=115200" \
    "TEST_AXIL_PIPE_COUNT=0" \
    "PORT_AXIL_PIPE_COUNT=0" \
]

set_property generic $full_generics [get_filesets sources_1]

puts "Generic despues (RAM_COUNT=0): [get_property generic [get_filesets sources_1]]"

reset_run synth_1
launch_runs synth_1 -jobs 8
wait_on_run synth_1

if {[get_property PROGRESS [get_runs synth_1]] != "100%"} {
    puts "ERROR: synth_1 no llego al 100%, revisa el log antes de seguir con impl_1"
    close_project
    exit 1
}

puts "OK: synth_1 completo. Lanzando impl_1..."

reset_run impl_1
launch_runs impl_1 -to_step write_bitstream -jobs 8
wait_on_run impl_1

if {[get_property PROGRESS [get_runs impl_1]] != "100%"} {
    puts "ERROR: impl_1 no llego al 100%, revisa el log"
    close_project
    exit 1
}

puts "OK: bitstream generado en [get_property DIRECTORY [get_runs impl_1]]"
close_project
exit 0
