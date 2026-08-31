#!/bin/bash

# Descubre empíricamente el emparejamiento físico entre puertos.
# Genera tráfico en un puerto cada vez y observa qué otros puertos lo reciben.

set -u

API="http://localhost:8000"
PORTS=(0 1 2 3)

TARGET=0
LENGTH=64
BW_GBPS=1

STABILIZE=3
WINDOW=30

# Evita considerar tráfico residual como tráfico generado
MIN_DELTA=100000

check_api() {
    local code

    code=$(curl -s -m 5 -o /dev/null -w "%{http_code}" "$API/ports")

    if [ "$code" != "200" ]; then
        echo "ERROR: no se puede contactar con la API en $API (http_code=$code)." >&2
        exit 1
    fi
}

get_counter() {
    local port=$1
    local field=$2

    curl -s -m 5 "$API/ports/$port/counters" |
        grep -o "\"$field\":[0-9]*" |
        grep -o '[0-9]*$'
}

configure_flow() {
    local port=$1
    local enabled=$2

    curl -s -m 5 \
        -X POST "$API/ports/$port/generator/$TARGET/bandwidth" \
        -H "Content-Type: application/json" \
        -d "{\"enabled\":$enabled,\"length\":$LENGTH,\"bandwidth_gbps\":$BW_GBPS}" \
        > /dev/null
}

reset_all_flows() {
    local p

    for p in "${PORTS[@]}"; do
        configure_flow "$p" false
    done

    sleep "$STABILIZE"
}

set_rx_mac() {
    local port=$1

    curl -s -m 5 \
        -X POST "$API/ports/$port/mux" \
        -H "Content-Type: application/json" \
        -d '{"rx_mux":"mac","tx_mux":"mac"}' \
        > /dev/null
}

set_tx_generator() {
    local port=$1

    curl -s -m 5 \
        -X POST "$API/ports/$port/mux" \
        -H "Content-Type: application/json" \
        -d '{"rx_mux":"gen","tx_mux":"mac"}' \
        > /dev/null
}

echo "Comprobando API..."
check_api
echo "API disponible."

echo "Deshabilitando todos los flujos..."
reset_all_flows

echo
echo "Estado inicial de los puertos:"
curl -s "$API/ports"
echo
echo

for tx in "${PORTS[@]}"; do

    echo "============================================================"
    echo "Generando tráfico en puerto $tx"
    echo "Ventana de medida: ${WINDOW}s"
    echo "============================================================"

    # Los puertos receptores toman tráfico del MAC
    for rx in "${PORTS[@]}"; do
        if [ "$rx" != "$tx" ]; then
            set_rx_mac "$rx"
        fi
    done

    # El puerto bajo prueba toma tráfico del generador
    echo "Conectando generador al puerto $tx..."
    set_tx_generator "$tx"

    echo "Habilitando flujo $TARGET del puerto $tx a ${BW_GBPS} Gbps..."
    configure_flow "$tx" true

    echo "Esperando ${STABILIZE}s para estabilización..."
    sleep "$STABILIZE"

    declare -A before
    declare -A after

    echo
    echo "Contadores antes de la medida:"

    for rx in "${PORTS[@]}"; do
        if [ "$rx" != "$tx" ]; then
            before[$rx]=$(get_counter "$rx" "rx_port_in_frames")
            echo "  Puerto $rx: ${before[$rx]:-0}"
        fi
    done

    echo
    echo "Midiendo durante ${WINDOW}s..."
    sleep "$WINDOW"

    echo
    echo "Resultados:"

    for rx in "${PORTS[@]}"; do
        if [ "$rx" != "$tx" ]; then

            after[$rx]=$(get_counter "$rx" "rx_port_in_frames")

            delta=$(( ${after[$rx]:-0} - ${before[$rx]:-0} ))

            if [ "$delta" -gt "$MIN_DELTA" ]; then
                echo "  puerto $tx -> puerto $rx : RECIBE TRAFICO (delta=$delta tramas)"
            else
                echo "  puerto $tx -> puerto $rx : sin tráfico significativo (delta=$delta)"
            fi
        fi
    done

    echo
    echo "Deshabilitando flujo del puerto $tx..."
    configure_flow "$tx" false

    unset before
    unset after

    sleep "$STABILIZE"
    echo
done

echo "============================================================"
echo "Comprobación terminada"
echo "============================================================"
