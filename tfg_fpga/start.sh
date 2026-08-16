#!/bin/bash
# Levanta toda la aplicación en el servidor (sin Docker)
# Uso: bash start.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/venv"
#UART_PORT="${UART_PORT:-/dev/ttyUSB5}"
ES_PORT=9200
GRAFANA_PORT=3000
KIBANA_PORT=5601
API_PORT=8000

API_PID=""
COLLECTOR_PID=""

cleanup() {
    info "Deteniendo procesos..."
    [ -n "$COLLECTOR_PID" ] && kill "$COLLECTOR_PID" 2>/dev/null
    if [ -n "$API_PID" ]; then
        sudo kill "$API_PID" 2>/dev/null
        sudo pkill -f "uvicorn main:app" 2>/dev/null
    fi
}
trap cleanup EXIT
trap 'cleanup; exit 1' INT TERM

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
info() { echo -e "${YELLOW}[..] $1${NC}"; }
err()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }



# ─── 1. Entorno virtual ──────────────────────────────────────────────────────
info "Comprobando entorno virtual..."
if [ ! -d "$VENV" ]; then
    info "Creando venv..."
    python3 -m venv "$VENV"
fi
source "$VENV/bin/activate"
pip install -q -r "$SCRIPT_DIR/requirements.txt"
ok "Entorno virtual listo"

info "Detectando si la FPGA se encuentra conectada"

if [  -n "$UART_PORT" ]; then
    if [ ! -e "$UART_PORT" ]; then
        err "Puerto $UART_PORT no encontrado. ¿Está la FPGA conectada?\nPuertos disponibles: $(ls /dev/ttyUSB* 2>/dev/null || echo 'ninguno')"
    fi
    ok "Puerto serie detectado: $UART_PORT"
else 
   BYID_DIR="/dev/serial/by-id"
   CANDIDATES=()
    if [ -d "$BYID_DIR" ]; then
        for dev in "$BYID_DIR"/*; do
            [ -e "$dev" ] && CANDIDATES+=("$dev")
        done
    fi
    if [ ${#CANDIDATES[@]} -gt 1 ]; then
        # De los adaptadores serie conectados, la FPGA habla XFCP por la
        # interfaz if02 del CP2108 (comprobado con dmesg: era el ttyUSB5
        # que antes estaba hardcodeado). Las demás interfaces del propio
        # CP2108 y el pod Xilinx (JTAG/depuración) no sirven para esto.
        FILTERED=()
        for c in "${CANDIDATES[@]}"; do
            case "$c" in
                *CP2108*if02*) FILTERED+=("$c") ;;
            esac
        done
        if [ ${#FILTERED[@]} -eq 1 ]; then
            CANDIDATES=("${FILTERED[@]}")
        fi
    fi
     if [ ${#CANDIDATES[@]} -eq 0 ]; then
        for dev in /dev/ttyUSB* /dev/ttyACM*; do
            [ -e "$dev" ] && CANDIDATES+=("$dev")
    
        done
    fi
    
    if [ ${#CANDIDATES[@]} -eq 0 ]; then
        err "No se ha detectado ningún puerto serie. ¿Está la FPGA conectada y encendida?"
    elif [ ${#CANDIDATES[@]} -eq 1 ]; then
        UART_PORT="${CANDIDATES[0]}"
        ok "FPGA detectada automáticamente en: $UART_PORT"
    else
        info "Se han detectado varios puertos serie:"
        for c in "${CANDIDATES[@]}"; do echo "    - $c"; done
        err "Hay más de un dispositivo serie conectado, no se puede elegir automáticamente.\nExporta UART_PORT con el correcto, p.ej.:\n  UART_PORT=${CANDIDATES[0]} bash start.sh"
    fi
    
fi
ok "Puerto serie a usar: $UART_PORT"





info "Comprobando Elasticsearch en puerto $ES_PORT..."
if curl -s "http://localhost:$ES_PORT" > /dev/null 2>&1; then
    ok "Elasticsearch ya está corriendo"
else
    info "Arrancando Elasticsearch..."
    if systemctl list-unit-files 2>/dev/null | grep -q elasticsearch; then
        sudo systemctl start elasticsearch
    else
        err "Elasticsearch no está instalado. Instálalo con:\n  sudo apt install elasticsearch"
    fi
    info "Esperando a que Elasticsearch arranque..."
    for i in $(seq 1 30); do
        sleep 2
        if curl -s "http://localhost:$ES_PORT" > /dev/null 2>&1; then
            ok "Elasticsearch listo"
            break
        fi
        if [ $i -eq 15 ]; then
            err "Elasticsearch no arrancó a tiempo"
        fi
    done
fi

info "Comprobando Grafana en puerto $GRAFANA_PORT..."
if curl -s "http://localhost:$GRAFANA_PORT" > /dev/null 2>&1; then
    ok "Grafana ya está corriendo"
else
    info "Arrancando Grafana..."
    if command -v systemctl &> /dev/null && systemctl list-units --type=service | grep -q grafana; then
        sudo systemctl start grafana-server
    else
        err "Grafana no está instalado. Instálalo con:\n  sudo apt install grafana"
    fi
    sleep 3
    ok "Grafana listo (http://localhost:$GRAFANA_PORT)"
fi

info "Configurando datasource de Elasticsearch en Grafana..."
DS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    "http://admin:admin@localhost:$GRAFANA_PORT/api/datasources/uid/es-port-counters")
if [ "$DS_RESPONSE" = "200" ]; then
    ok "Datasource 'es-port-counters' ya existe en Grafana"
else
    curl -s -X POST "http://admin:admin@localhost:$GRAFANA_PORT/api/datasources" \
        -H "Content-Type: application/json" \
        -d "{
            \"name\": \"Elasticsearch Port Counters\",
            \"type\": \"elasticsearch\",
            \"uid\": \"es-port-counters\",
            \"url\": \"http://localhost:$ES_PORT\",
            \"access\": \"proxy\",
            \"jsonData\": {
                \"index\": \"port_counters\",
                \"timeField\": \"@timestamp\",
                \"esVersion\": \"8.0.0\"
            }
        }" > /dev/null
    ok "Datasource 'es-port-counters' creado en Grafana"
fi

info "Comprobando Kibana en puerto $KIBANA_PORT..."
if curl -s "http://localhost:$KIBANA_PORT" > /dev/null 2>&1; then
    ok "Kibana ya está corriendo"
else
    info "Arrancando Kibana..."
    if systemctl list-unit-files 2>/dev/null | grep -q kibana; then
        sudo systemctl start kibana
    else
        err "Kibana no está instalado. Instálalo con:\n  sudo apt install kibana"
    fi
    info "Esperando a que Kibana arranque..."
    for i in $(seq 1 30); do
        sleep 2
        if curl -s "http://localhost:$KIBANA_PORT" > /dev/null 2>&1; then
            ok "Kibana listo (http://localhost:$KIBANA_PORT)"
            break
        fi
        if [ $i -eq 15 ]; then
            err "Kibana no arrancó a tiempo"
        fi
    done
fi

# ─── 5. API FastAPI ──────────────────────────────────────────────
info "Arrancando API FastAPI (MODE=real)..."
cd "$SCRIPT_DIR"

PYTHON="$VENV/bin/python"
mkdir -p "$SCRIPT_DIR/logs"
sudo \
    MODE=real \
    UART_PORT="$UART_PORT" \
    ES_HOST="http://localhost:$ES_PORT" \
    GRAFANA_URL="http://localhost:$GRAFANA_PORT" \
    GRAFANA_USER=admin \
    GRAFANA_PASS=admin \
     "$PYTHON" -m uvicorn main:app --host 0.0.0.0 --port $API_PORT \
    > "$SCRIPT_DIR/logs/api.log" 2>&1 &
API_PID=$!

API_URL=http://localhost:$API_PORT "$PYTHON" "$SCRIPT_DIR/data_collector.py" \
    > "$SCRIPT_DIR/logs/collector.log" 2>&1 &
COLLECTOR_PID=$!
ok "Colector de datos arrancado"
info "Logs: tail -f $SCRIPT_DIR/logs/api.log   |   tail -f $SCRIPT_DIR/logs/collector.log"
# ─── 6. Colector de datos ─────────────────────────────────────────
info "Esperando a que la API esté lista..."
for i in $(seq 1 30); do
    sleep 2
    if curl -s "http://localhost:$API_PORT/health" > /dev/null 2>&1; then
        ok "API lista"
        break
    fi
    if [ $i -eq 15 ]; then
        err "La API no arrancó a tiempo"
    fi
done

info "Arrancando colector de datos..."
API_URL=http://localhost:$API_PORT "$PYTHON" "$SCRIPT_DIR/data_collector.py" &
COLLECTOR_PID=$!
ok "Colector de datos arrancado"

EXIT_CODE=0
wait -n "$API_PID" "$COLLECTOR_PID" || EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    err "Un proceso ha terminado inesperadamente (código $EXIT_CODE)"
fi
info "Un proceso ha terminado, deteniendo el resto..."
