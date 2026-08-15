#!/bin/bash
# Experimento de trafico mixto: valida throughput agregado, packet loss rate y
# frame error rate del generador bajo escenarios con multiples flujos concurrentes
# en el puerto 0, midiendo a traves del enlace fisico loopback puerto0<->puerto1.
#
# Uso: bash mixed_traffic_test.sh | tee mixed_traffic_results.log
# Requiere: curl, awk. Apunta por defecto a la API en real mode (10.22.10.2:8000).

set -u

# Si se ejecuta directamente en el servidor (switch-dev-1), usar localhost.
# Si se ejecuta desde fuera via VPN, cambiar a http://10.22.10.2:8000
API="http://localhost:8000"
TX_PORT=0     # puerto donde se configuran los flujos (transmite)
RX_PORT=1     # puerto emparejado por loopback (recibe)
STABILIZE=2
WINDOW=10
REPEATS=5

check_api() {
  local code
  code=$(curl -s -m 5 -o /dev/null -w "%{http_code}" "$API/ports")
  if [ "$code" != "200" ]; then
    echo "ERROR: no se puede contactar con la API en $API (http_code=$code)." >&2
    echo "Comprueba que la API esta arrancada (ps aux | grep uvicorn) y que la IP/puerto son correctos." >&2
    exit 1
  fi
}

get_counter() {
  local port=$1 field=$2
  curl -s -m 5 "$API/ports/$port/counters" | grep -o "\"$field\":[0-9]*" | grep -o '[0-9]*$'
}

configure_flow() {
  local target=$1 length=$2 bw_gbps=$3 enabled=$4
  curl -s -m 5 -X POST "$API/ports/$TX_PORT/generator/$target/bandwidth" \
    -H "Content-Type: application/json" \
    -d "{\"enabled\":$enabled,\"length\":$length,\"bandwidth_gbps\":$bw_gbps}" > /dev/null
}

snapshot() {
  local tx_out gen rx_in rx_true
  tx_out=$(get_counter "$TX_PORT" "tx_port_out_frames")
  gen=$(get_counter "$TX_PORT" "rx_port_gen_frames")
  rx_in=$(get_counter "$RX_PORT" "rx_port_in_frames")
  rx_true=$(get_counter "$RX_PORT" "rx_port_in_true_frames")
  echo "$tx_out $gen $rx_in $rx_true"
}

run_scenario() {
  local name="$1"; shift
  local flows=("$@")   # cada elemento "target:length:bw"

  echo "=== Escenario: $name ==="
  local bw_theory_sum=0
  for f in "${flows[@]}"; do
    IFS=: read -r target length bw <<< "$f"
    bw_theory_sum=$(awk -v a="$bw_theory_sum" -v b="$bw" 'BEGIN{print a+b}')
  done
  echo "Ancho de banda objetivo agregado: ${bw_theory_sum} Gbps (${#flows[@]} flujos)"

  for rep in $(seq 1 $REPEATS); do
    for f in "${flows[@]}"; do
      IFS=: read -r target length bw <<< "$f"
      configure_flow "$target" "$length" "$bw" true
    done
    sleep "$STABILIZE"

    read -r tx_out1 gen1 rx_in1 rx_true1 <<< "$(snapshot)"
    t1=$(date +%s.%N)
    sleep "$WINDOW"
    read -r tx_out2 gen2 rx_in2 rx_true2 <<< "$(snapshot)"
    t2=$(date +%s.%N)

    for f in "${flows[@]}"; do
      IFS=: read -r target length bw <<< "$f"
      configure_flow "$target" "$length" "$bw" false
    done

    awk -v rep="$rep" -v t1="$t1" -v t2="$t2" \
        -v tx_out1="$tx_out1" -v tx_out2="$tx_out2" \
        -v gen1="$gen1" -v gen2="$gen2" \
        -v rx_in1="$rx_in1" -v rx_in2="$rx_in2" \
        -v rx_true1="$rx_true1" -v rx_true2="$rx_true2" '
      BEGIN {
        dt = t2 - t1
        dgen = gen2 - gen1
        dtx  = tx_out2 - tx_out1
        drx  = rx_in2 - rx_in1
        drxt = rx_true2 - rx_true1

        fps_meas = dgen / dt
        loss_rate = (dtx > 0) ? (dtx - drx) / dtx * 100 : 0
        err_rate  = (drx > 0) ? (drx - drxt) / drx * 100 : 0

        printf "  rep=%d  dt=%.2fs  gen_frames=%d  tx_out=%d  rx_in=%d  rx_in_true=%d  fps_meas=%.2f  packet_loss=%.4f%%  frame_error=%.4f%%\n", \
          rep, dt, dgen, dtx, drx, drxt, fps_meas, loss_rate, err_rate
      }'
  done
  echo
}

# ---- Matriz de escenarios ----

check_api

run_scenario "1-flujo (crosscheck single-flow)" "0:64:1"

run_scenario "2-flujos asimetricos (64B@1G + 512B@3G)" "0:64:1" "1:512:3"

run_scenario "2-flujos simetricos (64B@1G x2, control)" "0:64:1" "1:64:1"

run_scenario "3-flujos concurrentes" "0:64:1" "1:512:3" "2:256:2"

run_scenario "Saturacion (~11 Gbps agregados, sobre linea de 10G)" "0:64:2" "1:512:3" "2:256:3" "3:128:3"

echo "Fin del experimento."
