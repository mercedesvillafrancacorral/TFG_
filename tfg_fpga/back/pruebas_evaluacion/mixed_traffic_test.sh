
""" Experimento de trafico mixto: valida throughput agregado, packet loss rate y
 frame error rate del generador bajo escenarios con multiples flujos concurrentes
 en el puerto 0, midiendo a traves del enlace fisico loopback puerto0<->puerto2."""

set -u


API="http://localhost:8000"
TX_PORT=0     
RX_PORT=2    
STABILIZE=2
WINDOW=10
REPEATS=5
RESULTS_DIR="results/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RESULTS_DIR"

check_api() {
  local code
  code=$(curl -s -m 5 -o /dev/null -w "%{http_code}" "$API/ports")
  if [ "$code" != "200" ]; then
    echo "ERROR: no se puede contactar con la API en $API (http_code=$code)." >&2
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
  local tx_out gen rx_in gen_true
  tx_out=$(get_counter "$TX_PORT" "tx_port_out_frames")
  gen=$(get_counter "$TX_PORT" "rx_port_gen_frames")
  rx_in=$(get_counter "$RX_PORT" "rx_port_in_frames")
  gen_true=$(get_counter "$TX_PORT" "rx_port_gen_true_frames")
  echo "$tx_out $gen $rx_in $gen_true"
}

run_scenario() {
  local name="$1" slug="$2"; shift 2
  local flows=("$@")   # cada elemento "target:length:bw"

  echo "=== Escenario: $name ==="
  local RAW_CSV="$RESULTS_DIR/${slug}.csv"
  echo "rep,dt,gen_frames,tx_out,rx_in,gen_true_frames,fps_meas,internal_loss_pct,link_loss_pct,frame_error_pct" > "$RAW_CSV"

  local bw_theory_sum=0 fps_theory_sum=0
  for f in "${flows[@]}"; do
    IFS=: read -r target length bw <<< "$f"
    bw_theory_sum=$(awk -v a="$bw_theory_sum" -v b="$bw" 'BEGIN{print a+b}')
    fps_theory_sum=$(awk -v a="$fps_theory_sum" -v bw="$bw" -v len="$length" 'BEGIN{print a + (bw*1e9)/(8*len)}')
  done
  echo "Ancho de banda objetivo agregado: ${bw_theory_sum} Gbps (${#flows[@]} flujos)  ->  fps teorico agregado: $(awk -v f="$fps_theory_sum" 'BEGIN{printf "%.2f", f}')"

  for rep in $(seq 1 $REPEATS); do
    for f in "${flows[@]}"; do
      IFS=: read -r target length bw <<< "$f"
      configure_flow "$target" "$length" "$bw" true
    done
    sleep "$STABILIZE"

    read -r tx_out1 gen1 rx_in1 gen_true1 <<< "$(snapshot)"
    t1=$(date +%s.%N)
    sleep "$WINDOW"
    read -r tx_out2 gen2 rx_in2 gen_true2 <<< "$(snapshot)"
    t2=$(date +%s.%N)

    for f in "${flows[@]}"; do
      IFS=: read -r target length bw <<< "$f"
      configure_flow "$target" "$length" "$bw" false
    done

    awk -v rep="$rep" -v t1="$t1" -v t2="$t2" \
        -v tx_out1="$tx_out1" -v tx_out2="$tx_out2" \
        -v gen1="$gen1" -v gen2="$gen2" \
        -v rx_in1="$rx_in1" -v rx_in2="$rx_in2" \
        -v gen_true1="$gen_true1" -v gen_true2="$gen_true2" \
        -v raw_csv="$RAW_CSV" '
      BEGIN {
        dt = t2 - t1
        dgen = gen2 - gen1
        dtx  = tx_out2 - tx_out1
        drx  = rx_in2 - rx_in1
        dgen_true = gen_true2 - gen_true1

        fps_meas = dgen / dt
        """perdida interna: generado por el port_traffic_gen pero no llega a salir por tx"""
        internal_loss = (dgen > 0) ? (dgen - dtx) / dgen * 100 : 0
        """ perdida en el enlace fisico: sale de TX_PORT pero no llega a RX_PORT"""
        link_loss = (dtx > 0) ? (dtx - drx) / dtx * 100 : 0
        """ frame error rate: generadas vs validas en propio contador "true" """
        err_rate  = (dgen > 0) ? (dgen - dgen_true) / dgen * 100 : 0

        printf "  rep=%d  dt=%.2fs  gen_frames=%d  tx_out=%d  rx_in=%d  gen_true_frames=%d  fps_meas=%.2f  internal_loss=%.4f%%  link_loss=%.4f%%  frame_error=%.4f%%\n", \
          rep, dt, dgen, dtx, drx, dgen_true, fps_meas, internal_loss, link_loss, err_rate

        printf "%d,%.4f,%d,%d,%d,%d,%.4f,%.4f,%.4f,%.4f\n", \
          rep, dt, dgen, dtx, drx, dgen_true, fps_meas, internal_loss, link_loss, err_rate >> raw_csv
      }'
  done

  
  awk -F, -v scenario="$name" -v fps_theory="$fps_theory_sum" '
    NR==1 { next }  # salta cabecera
    {
      n++
      fps=$7; il=$8; ll=$9; fe=$10
      sum[1]+=fps; sumsq[1]+=fps*fps
      sum[2]+=il;  sumsq[2]+=il*il
      sum[3]+=ll;  sumsq[3]+=ll*ll
      sum[4]+=fe;  sumsq[4]+=fe*fe
    }
    END {
      if (n==0) { print "  (sin datos)"; exit }
      names[1]="fps_meas"; names[2]="internal_loss%"; names[3]="link_loss%"; names[4]="frame_error%"
      printf "  --- resumen (n=%d) ---\n", n
      for (i=1;i<=4;i++) {
        mean[i] = sum[i]/n
        var = (n>1) ? (sumsq[i]/n - mean[i]*mean[i]) * n/(n-1) : 0
        if (var < 0) var = 0
        sd = sqrt(var)
        printf "  %-15s media=%.4f  desv.tip=%.4f\n", names[i], mean[i], sd
      }
      dev_pct = (fps_theory > 0) ? (mean[1] - fps_theory) / fps_theory * 100 : 0
      printf "  %-15s teorico=%.2f  medido=%.2f  desviacion=%+.3f%%\n", "fps (bw/size/rate)", fps_theory, mean[1], dev_pct
    }' "$RAW_CSV"
  echo
}

reset_all_flows() {
  # asegura estado limpio: deshabilita todos los targets posibles en TX_PORT
  # por si una ejecucion anterior (interrumpida o de otra sesion) dejo alguno
  # activo, lo que falsearia el escenario de un unico flujo
  local t
  for t in 0 1 2 3; do
    configure_flow "$t" 64 1 false
  done
  sleep "$STABILIZE"
}

# ---- Matriz de escenarios ----

check_api
reset_all_flows

run_scenario "1-flujo (crosscheck single-flow)" "1_flujo_crosscheck" "0:64:1"

run_scenario "2-flujos asimetricos (64B@1G + 512B@3G)" "2_flujos_asimetricos" "0:64:1" "1:512:3"

run_scenario "2-flujos simetricos (64B@1G x2, control)" "2_flujos_simetricos" "0:64:1" "1:64:1"

run_scenario "3-flujos concurrentes" "3_flujos_concurrentes" "0:64:1" "1:512:3" "2:256:2"

run_scenario "Saturacion (~11 Gbps agregados, sobre linea de 10G)" "saturacion_11G" "0:64:2" "1:512:3" "2:256:3" "3:128:3"

echo "Fin del experimento."
echo "Resultados estructurados (CSV) en: $RESULTS_DIR/ -- un fichero por escenario, con las repeticiones individuales."
