open_hw
connect_hw_server
set targets [get_hw_targets]
puts "Hardware targets: $targets"
if {[llength $targets] == 0} {
    puts "ERROR: no se detecta ningun target JTAG"
    disconnect_hw_server
    exit 1
}
set target [lindex $targets 0]
open_hw_target $target
set devices [get_hw_devices]
puts "Hardware devices: $devices"
foreach dev $devices {
    puts "  $dev -> PROGRAM.STATE = [get_property PROGRAM.STATE $dev]"
}
close_hw_target
disconnect_hw_server
puts "OK: hw_server y JTAG responden con normalidad"
exit 0
