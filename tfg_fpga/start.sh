#!/bin/bash
# Levanta toda la aplicación en el servidor (sin Docker)
# Uso: bash start.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/venv"
UART_PORT="${UART_PORT:-}"
ES_PORT=9200
GRAFANA_PORT=3000
KIBANA_PORT=5601
API_PORT=8000

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

info "Comprobando puerto serie $UART_PORT..."
if [ ! -e "$UART_PORT" ]; then
    err "Puerto $UART_PORT no encontrado. ¿Está la FPGA conectada?\nPuertos disponibles: $(ls /dev/ttyUSB* 2>/dev/null || echo 'ninguno')"
fi
ok "Puerto serie detectado: $UART_PORT"



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

sudo \
    MODE=real \
    UART_PORT="$UART_PORT" \
    ES_HOST="http://localhost:$ES_PORT" \
    GRAFANA_URL="http://localhost:$GRAFANA_PORT" \
    GRAFANA_USER=admin \
    GRAFANA_PASS=admin \
    "$PYTHON" -m uvicorn main:app --host 0.0.0.0 --port $API_PORT &

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
ok "Colector de datos arrancado"

wait
