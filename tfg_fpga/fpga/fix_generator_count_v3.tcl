set project_path "/home/mvillafranca/traffic_generator_mercedes/fpga/tool/ZCU102/fpga_traffic_generator/fpga/fpga.xpr"
open_project $project_path

set current_generics [get_property generic [get_filesets sources_1]]
puts "Generic antes (completo): $current_generics"

set new_generics {}
foreach g $current_generics {
    if {[string match "PORT_GEN_TRAFFIC_COMMON_COUNT=*" $g]} {
        lappend new_generics "PORT_GEN_TRAFFIC_COMMON_COUNT=10"
    } else {
        lappend new_generics $g
    }
}
set_property generic $new_generics [get_filesets sources_1]

puts "Generic despues (completo): [get_property generic [get_filesets sources_1]]"

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
