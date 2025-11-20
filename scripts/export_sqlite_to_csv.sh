#!/usr/bin/env bash
set -euo pipefail

DB_FILE="db.sqlite3"
OUT_DIR="export"

mkdir -p "$OUT_DIR"

echo "Exporting tables from $DB_FILE to $OUT_DIR (CSV)..."

run_export() {
  local query="$1"
  local file="$2"
  echo " - $file"
  sqlite3 "$DB_FILE" -header -csv "$query" > "$OUT_DIR/$file"
}

run_export "select id, username, email, date_joined from auth_user;" auth_user.csv
run_export "select * from core_ambiente;" core_ambiente.csv
run_export "select * from core_dispositivo;" core_dispositivo.csv
run_export "select * from core_tiposensor;" core_tiposensor.csv
run_export "select * from core_sensor;" core_sensor.csv
run_export "select * from core_leiturasensor;" core_leiturasensor.csv
run_export "select * from ar_condicionado_arcondicionado;" ar_condicionado.csv

echo "Done. Upload CSV files to Supabase staging tables."
