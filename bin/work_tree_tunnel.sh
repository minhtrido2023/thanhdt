#!/usr/bin/env bash
# Quick tunnel Cloudflare (không cần tài khoản) đưa webapp Work-Tree ra Internet.
# URL *.trycloudflare.com ĐỔI mỗi lần tunnel khởi động; ghi vào state/work_tree/public_url.txt
# (daily_decision_topic.py đọc file này). File bị xoá khi tunnel tắt. Muốn URL cố định: tunnel có tên + tên miền.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${WT_PORT:-8610}"
CF="${CLOUDFLARED:-$HOME/.local/bin/cloudflared}"
OUT="$ROOT/state/work_tree/public_url.txt"
LOG="$ROOT/logs/work_tree_tunnel.log"
mkdir -p "$ROOT/state/work_tree" "$ROOT/logs"
rm -f "$OUT"
trap 'rm -f "$OUT"' EXIT
: > "$LOG"
"$CF" tunnel --no-autoupdate --url "http://127.0.0.1:${PORT}" >"$LOG" 2>&1 &
cfpid=$!
for _ in $(seq 1 60); do
  url="$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' "$LOG" | head -1 || true)"
  if [ -n "$url" ]; then printf '%s\n' "$url" > "$OUT.tmp" && mv "$OUT.tmp" "$OUT"; break; fi
  kill -0 "$cfpid" 2>/dev/null || { echo "cloudflared thoát sớm; xem $LOG" >&2; exit 1; }
  sleep 1
done
[ -s "$OUT" ] || { echo "không lấy được URL tunnel sau 60s; xem $LOG" >&2; kill "$cfpid" 2>/dev/null; exit 1; }
wait "$cfpid"
