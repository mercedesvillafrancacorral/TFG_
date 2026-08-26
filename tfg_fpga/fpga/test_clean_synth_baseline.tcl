set project_path "/home/mvillafranca/traffic_generator_mercedes/fpga/tool/ZCU102/fpga_traffic_generator/fpga/project_1/project_1.xpr"
open_project $project_path

puts "Generic antes: [get_property generic [get_filesets sources_1]]"

# Vuelve el generic al valor original (3) - solo queremos aislar si una
# sintesis LIMPIA (reset_run) falla incluso sin tocar nada del generic.
set_property generic {PORT_GEN_TRAFFIC_COMMON_COUNT=3} [get_filesets sources_1]

puts "Generic despues: [get_property generic [get_filesets sources_1]]"

reset_run synth_1
launch_runs synth_1 -jobs 8
wait_on_run synth_1

set prog [get_property PROGRESS [get_runs synth_1]]
if {$prog != "100%"} {
    puts "RESULTADO: synth_1 con generic=3 tambien FALLA limpio (progress=$prog) -> problema preexistente, no relacionado con el generic"
} else {
    puts "RESULTADO: synth_1 con generic=3 SI compila limpio -> el problema es especifico del valor 10"
}

close_project
exit 0
