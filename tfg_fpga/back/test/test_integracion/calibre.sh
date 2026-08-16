#!/bin/bash
# Barrido de calibracion del registro `counter` del generador de trafico FPGA.
# Mide fps real (rx_port_gen_frames) para varios (length, counter) y lo compara
# contra el modelo teorico fps_teorico = clk_asumido / counter (clk_asumido=350MHz).
#
# Uso: bash calibrate_counter.sh
# Requiere: curl, awk. Apunta por defecto a la API en real mode (10.22.10.2:8000);
# cambia API si lo ejecutas en localhost del propio servidor.
set -u

API="http://10.22.10.2:8000"
PORT_ID=0
TARGET=0
STABILIZE=2
WINDOW=8
CLK_ASSUMED=350000000

get_gen_frames() {
  curl -s -m 5 "$API/ports/$PORT_ID/counters" | grep -o '"rx_port_gen_frames":[0-9]*' | grep -o '[0-9]*$'
}

configure() {
  local enabled=$1 length=$2 counter=$3 counter_frac=$4
  curl -s -m 5 -X POST "$API/ports/$PORT_ID/generator/$TARGET" \
    -H "Content-Type: application/json" \
    -d "{\"enabled\":$enabled,\"length\":$length,\"counter\":$counter,\"counter_frac\":$counter_frac}" > /dev/null
}

run_case() {
  local length=$1 counter=$2
  configure true "$length" "$counter" 0
  sleep "$STABILIZE"

  n1=$(get_gen_frames)
  t1=$(date +%s.%N)
  sleep "$WINDOW"
  n2=$(get_gen_frames)
  t2=$(date +%s.%N)

  configure false "$length" "$counter" 0

  awk -v n1="$n1" -v n2="$n2" -v t1="$t1" -v t2="$t2" -v flen="$length" -v counter="$counter" -v clk="$CLK_ASSUMED" '
    BEGIN {
      dt = t2 - t1
      fps_meas = (n2 - n1) / dt
      fps_theory = clk / counter
      dev_pct = (fps_meas - fps_theory) / fps_theory * 100
      clk_implied = fps_meas * counter
      bw_meas_gbps = fps_meas * flen * 8 / 1e9
      printf "length=%-5d counter=%-6d  fps_meas=%.2f  fps_teorico=%.2f  dev=%+.3f%%  clk_implied=%.0f Hz  bw_meas=%.4f Gbps  (dt=%.2fs, dN=%d)\n", \
        flen, counter, fps_meas, fps_theory, dev_pct, clk_implied, bw_meas_gbps, dt, (n2-n1)
    }'
}

echo "=== Barrido raw counter (aisla la formula, sin pasar por bandwidth_gbps) ==="
for length in 64 512; do
  for counter in 179 350 1750; do
    run_case "$length" "$counter"
  done
done

echo
echo "=== Cross-check via endpoint /bandwidth (formula completa con clk=350MHz asumido) ==="

run_bw_case() {
  local length=$1 bw_gbps=$2
  resp=$(curl -s -m 5 -X POST "$API/ports/$PORT_ID/generator/$TARGET/bandwidth" \
    -H "Content-Type: application/json" \
    -d "{\"enabled\":true,\"length\":$length,\"bandwidth_gbps\":$bw_gbps}")
  counter=$(echo "$resp" | grep -o '"counter":[0-9]*' | grep -o '[0-9]*$')

  sleep "$STABILIZE"
  n1=$(get_gen_frames)
  t1=$(date +%s.%N)
  sleep "$WINDOW"
  n2=$(get_gen_frames)
  t2=$(date +%s.%N)

  configure false "$length" "${counter:-1}" 0

  awk -v n1="$n1" -v n2="$n2" -v t1="$t1" -v t2="$t2" -v flen="$length" -v bw_req="$bw_gbps" -v counter="$counter" '
    BEGIN {
      dt = t2 - t1
      fps_meas = (n2 - n1) / dt
      bw_meas_gbps = fps_meas * flen * 8 / 1e9
      dev_pct = (bw_meas_gbps - bw_req) / bw_req * 100
      printf "length=%-5d bw_req=%-6s Gbps  counter=%-6s  fps_meas=%.2f  bw_meas=%.4f Gbps  dev=%+.3f%%\n", \
        flen, bw_req, counter, fps_meas, bw_meas_gbps, dev_pct
    }'
}

for length in 64 512; do
  for bw in 1 5; do
    run_bw_case "$length" "$bw"
  done
done

echo
echo "Limpieza: desactivando generador..."
configure false 64 350 0
echo "Listo."
