# set bit_file "fpga_learn_1_100g_port_N_4.bit"
set bit_file "fpga.bit"

if {[info exists ::env(BIT_FILE)]} {
    set bit_file $::env(BIT_FILE)
}

open_hw
connect_hw_server
set targets [get_hw_targets]
put $targets
set target [lindex [get_hw_targets] 0]
put $target
open_hw_target $target
set devices [get_hw_devices]
put $devices
current_hw_device [lindex [get_hw_devices] 0]
set devices [get_hw_devices -of_objects [current_hw_target]]
put $devices
refresh_hw_device -update_hw_probes false [current_hw_device]
puts $bit_file
set_property PROGRAM.FILE $bit_file [current_hw_device]
program_hw_devices [current_hw_device]
exit
