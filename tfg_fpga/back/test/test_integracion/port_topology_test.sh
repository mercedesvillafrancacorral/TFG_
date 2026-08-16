#!/bin/bash
# Descubre empiricamente el emparejamiento fisico (loopback) real entre puertos:
# genera trafico en un puerto cada vez y mide en que otros puertos se recibe.
# Uso: bash port_topology_test.sh | tee port_topology_results.log

set -u

API="http://localhost:8000"
PORTS=(0 1 2 3)
TARGET=0
LENGTH=64
BW_GBPS=1
STABILIZE=2
WINDOW=6

get_counter() {
  local port=$1 field=$2
  curl -s -m 5 "$API/ports/$port/counters" | grep -o "\"$field\":[0-9]*" | grep -o '[0-9]*$'
}

set_rx_mac() {
  local port=$1
  curl -s -m 5 -X POST "$API/ports/$port/mux" \
    -H "Content-Type: application/json" \
    -d '{"rx_mux": "mac"}' > /dev/null
}

configure_flow() {
  local port=$1 enabled=$2
  curl -s -m 5 -X POST "$API/ports/$port/generator/$TARGET/bandwidth" \
    -H "Content-Type: application/json" \
    -d "{\"enabled\":$enabled,\"length\":$LENGTH,\"bandwidth_gbps\":$BW_GBPS}" > /dev/null
}

echo "Estado inicial de los puertos:"
curl -s "$API/ports"
echo
echo

for tx in "${PORTS[@]}"; do
  echo "=== Generando trafico en puerto $tx, midiendo recepcion en el resto ==="

  # aseguramos rx en modo mac en todos los demas puertos para no confundir
  # 'sin conexion fisica' con 'mux en modo null'
  for rx in "${PORTS[@]}"; do
    if [ "$rx" != "$tx" ]; then
      set_rx_mac "$rx"
    fi
  done

  configure_flow "$tx" true
  sleep "$STABILIZE"

  declare -A before after
  for rx in "${PORTS[@]}"; do
    if [ "$rx" != "$tx" ]; then
      before[$rx]=$(get_counter "$rx" "rx_port_in_frames")
    fi
  done

  sleep "$WINDOW"

  for rx in "${PORTS[@]}"; do
    if [ "$rx" != "$tx" ]; then
      after[$rx]=$(get_counter "$rx" "rx_port_in_frames")
      delta=$(( ${after[$rx]:-0} - ${before[$rx]:-0} ))
      if [ "$delta" -gt 0 ]; then
        echo "  puerto $tx -> puerto $rx : RECIBE trafico (delta=$delta tramas en ${WINDOW}s)"
      else
        echo "  puerto $tx -> puerto $rx : nada (delta=0)"
      fi
    fi
  done

  configure_flow "$tx" false
  unset before after
  echo
done

echo "Comprobación terminada"
