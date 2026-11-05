#!/usr/bin/env bash
# Start/stop/status the local Galactica Workshop (web + worker) in the background.
# Usage: ./scripts/local.sh {start|stop|restart|status|logs}
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="8001"
LOG_DIR="/tmp/opencode"
WEB_LOG="$LOG_DIR/galactica-server.log"
WORKER_LOG="$LOG_DIR/galactica-worker.log"
PIDFILE="$LOG_DIR/galactica.pids"

cd "$APP_DIR"
mkdir -p "$LOG_DIR"

# Match on the command line, not a stale pidfile.
pids() {
  pgrep -f "manage.py (runserver 127.0.0.1:$PORT|run_worker)" || true
}

start() {
  if [ -n "$(pids)" ]; then
    echo "already running: $(pids | tr '\n' ' ')"
    return 0
  fi
  nohup .venv/bin/python manage.py runserver "127.0.0.1:$PORT" --noreload >"$WEB_LOG" 2>&1 &
  nohup .venv/bin/python manage.py run_worker >"$WORKER_LOG" 2>&1 &
  sleep 3
  pids >"$PIDFILE"
  echo "started: $(pids | tr '\n' ' ')"
  echo "web: http://127.0.0.1:$PORT/"
}

stop() {
  local found
  found="$(pids)"
  if [ -z "$found" ]; then
    echo "not running"
    return 0
  fi
  kill $found 2>/dev/null || true
  sleep 1
  found="$(pids)"
  [ -n "$found" ] && kill -9 $found 2>/dev/null || true
  rm -f "$PIDFILE"
  echo "stopped"
}

status() {
  local found
  found="$(pids)"
  if [ -z "$found" ]; then
    echo "not running"
    return 1
  fi
  ps -o pid,lstart,args -p $(echo "$found" | paste -sd, -)
}

case "${1:-start}" in
  start) start ;;
  stop) stop ;;
  restart) stop; start ;;
  status) status ;;
  logs) tail -n 40 "$WEB_LOG" "$WORKER_LOG" ;;
  *) echo "usage: $0 {start|stop|restart|status|logs}" >&2; exit 2 ;;
esac
