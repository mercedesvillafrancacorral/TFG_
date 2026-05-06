#!/bin/bash
# Levanta toda la aplicación en el servidor (sin Docker)
# Uso: bash start.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/venv"
UART_PORT="${UART_PORT:-/dev/ttyUSB2}"
ES_PORT=9200
GRAFANA_PORT=3000
API_PORT=8000

# ─── Colores ────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
info() { echo -e "${YELLOW}[..] $1${NC}"; }
err()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

echo "========================================"
echo "  TFG FPGA — Arranque completo"
echo "========================================"

# ─── 1. Entorno virtual ──────────────────────────────────────────────────────
info "Comprobando entorno virtual..."
if [ ! -d "$VENV" ]; then
    info "Creando venv..."
    python3 -m venv "$VENV"
fi
source "$VENV/bin/activate"
pip install -q -r "$SCRIPT_DIR/requirements.txt"
ok "Entorno virtual listo"

# ─── 2. Puerto serie ─────────────────────────────────────────────────────────
info "Comprobando puerto serie $UART_PORT..."
if [ ! -e "$UART_PORT" ]; then
    err "Puerto $UART_PORT no encontrado. ¿Está la FPGA conectada?\nPuertos disponibles: $(ls /dev/ttyUSB* 2>/dev/null || echo 'ninguno')"
fi
ok "Puerto serie detectado: $UART_PORT"

# ─── 3. Elasticsearch ────────────────────────────────────────────────────────
info "Comprobando Elasticsearch en puerto $ES_PORT..."
if curl -s "http://localhost:$ES_PORT" > /dev/null 2>&1; then
    ok "Elasticsearch ya está corriendo"
else
    info "Arrancando Elasticsearch..."
    if command -v systemctl &> /dev/null && systemctl list-units --type=service | grep -q elasticsearch; then
        sudo systemctl start elasticsearch
    elif command -v elasticsearch &> /dev/null; then
        elasticsearch -d -p /tmp/elasticsearch.pid
    else
        err "Elasticsearch no está instalado. Instálalo con:\n  sudo apt install elasticsearch"
    fi
    info "Esperando a que Elasticsearch arranque..."
    for i in $(seq 1 15); do
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

# ─── 4. Grafana ──────────────────────────────────────────────────────────────
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

# ─── 5. API FastAPI ──────────────────────────────────────────────────────────
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
    GRAFANA_EXTERNAL_URL="http://localhost:$GRAFANA_PORT" \
    "$PYTHON" -m uvicorn main:app --host 0.0.0.0 --port $API_PORT
