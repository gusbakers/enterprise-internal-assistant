#!/usr/bin/env bash
set -euo pipefail
PG_STARTED=0
APP_PID=""
cleanup() {
  if [[ -n "$APP_PID" ]]; then kill "$APP_PID" 2>/dev/null || true; fi
  if [[ "$PG_STARTED" == "1" ]]; then pg_ctl -D "$CRESTLINE_PGDATA" -m fast -w stop >/dev/null 2>&1 || true; fi
}
trap cleanup EXIT
trap 'exit 143' TERM INT
if [[ -z "${DATABASE_URL:-}" ]]; then
  export CRESTLINE_PGDATA="${CRESTLINE_PGDATA:-/tmp/crestline-pgdata}"
  socket=/tmp/crestline-socket
  mkdir -p "$socket"
  chmod 700 "$socket"
  if [[ ! -s "$CRESTLINE_PGDATA/PG_VERSION" ]]; then
    initdb -D "$CRESTLINE_PGDATA" --username=app --auth-local=trust --auth-host=reject >/dev/null
  fi
  pg_ctl -D "$CRESTLINE_PGDATA" -l /tmp/crestline-postgres.log \
    -o "-c listen_addresses='' -c unix_socket_directories='$socket' -c unix_socket_permissions=0700" -w start
  PG_STARTED=1
  if ! psql -h "$socket" -U app -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='crestline'" | grep -q 1; then
    createdb -h "$socket" -U app crestline
  fi
  export DATABASE_URL="postgresql:///crestline?host=$socket&user=app"
fi
python -m crestline.database
streamlit run app.py --server.address 0.0.0.0 --server.port 7860 --server.headless true &
APP_PID=$!
wait "$APP_PID"
