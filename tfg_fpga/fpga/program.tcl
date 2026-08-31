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

# Una carga completa del bitstream reinicia el VIO de control DFX a su valor
# de fabrica, que deja el puerto 0 con el bus AXI-Lite desacoplado (ver
# dbg_rp_decouple en fpga_core.v). Si el .ltx que acompana a este bitstream
# existe, intentamos recouplear aqui mismo para no depender de acordarnos
# a mano. Si el bitstream no trae ese VIO (p.ej. un build sin DFX), esto
# simplemente no encuentra el probe y se salta sin romper el programado.
set ltx_file [string map {".bit" ".ltx"} $bit_file]
if {[file exists $ltx_file]} {
    if {[catch {
        set_property PROBES.FILE $ltx_file [current_hw_device]
        set_property FULL_PROBES.FILE $ltx_file [current_hw_device]
        refresh_hw_device [current_hw_device]
        set_property OUTPUT_VALUE 0 [get_hw_probes core_inst/dbg_rp_decouple]
        commit_hw_vio [get_hw_probes core_inst/dbg_rp_decouple]
        puts "=== dbg_rp_decouple recoupleado a 0 tras el programado ==="
    } err]} {
        puts "AVISO: no se pudo recouplear dbg_rp_decouple tras programar ($err) — probablemente este bitstream no tiene el VIO de control DFX."
    }
} else {
    puts "AVISO: no existe $ltx_file junto al bitstream, no se comprueba dbg_rp_decouple."
}

exit
