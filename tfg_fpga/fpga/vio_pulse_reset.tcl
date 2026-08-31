open_hw_manager
connect_hw_server
open_hw_target
current_hw_device [get_hw_devices xczu9_0]
set_property PROBES.FILE {config1_v3.ltx} [current_hw_device]
set_property FULL_PROBES.FILE {config1_v3.ltx} [current_hw_device]
refresh_hw_device [current_hw_device]
set_property OUTPUT_VALUE 1 [get_hw_probes core_inst/dbg_rp_reset]
commit_hw_vio [get_hw_probes core_inst/dbg_rp_reset]
puts "=== reset pulsed HIGH ==="
set_property OUTPUT_VALUE 0 [get_hw_probes core_inst/dbg_rp_reset]
commit_hw_vio [get_hw_probes core_inst/dbg_rp_reset]
puts "=== reset back LOW ==="
set_property OUTPUT_VALUE 0 [get_hw_probes core_inst/dbg_rp_decouple]
commit_hw_vio [get_hw_probes core_inst/dbg_rp_decouple]
puts "=== decouple set to 0 ==="
