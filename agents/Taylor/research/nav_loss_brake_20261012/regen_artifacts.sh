#!/usr/bin/env bash
# Dựng lại TOÀN BỘ artifact của thư mục này từ dữ liệu thật (chỉ ĐỌC data/ thật; mọi thứ ghi vào
# thư mục tạm + thư mục này; cảnh báo đi vào file sink, KHÔNG gửi Discord):
#   seed/  ·  replay_full_history.txt  ·  real_run_and_dgc_case.txt  ·  sink_real_run.jsonl
# Dùng: bash regen_artifacts.sh   (chạy từ bất kỳ đâu)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN="$(cd "$HERE/../../../../bin" && pwd)"
CSV="$HERE/bq_price_DGC_20260706_20261009.csv"
UNTIL=2026-10-09                      # ngày cuối CSV có giá
NOW=2026-10-12T22:05:00               # đồng hồ giả lập của lượt cron tối 12/10 (dữ liệu 12/10 đã đủ)
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
MON="python3 $BIN/nav_loss_brake_monitor.py"

# ---- 1) seed: chuỗi mã loại trừ (BQ) + sổ gốc + bản khai market_only kiểm bằng máy
S="$T/seed"; mkdir -p "$S"
python3 "$BIN/nav_loss_brake_backfill_excluded.py" --price-csv "$CSV" --out-dir "$S" --until "$UNTIL" > "$T/backfill.log"
cp "$HERE/seed_inputs/managed_sleeve_flows.json" "$HERE/seed_inputs/episodes.json" \
   "$HERE/seed_inputs/excluded_ticker_exchange.json" "$S/"
python3 "$HERE/gen_sleeve_declarations.py" --price-csv "$CSV" --state-dir "$S" --now "${UNTIL}T22:05:00" --write > "$T/declare.log"
rm -f "$S/.lock"
rm -rf "$HERE/seed"; cp -r "$S" "$HERE/seed"

# ---- 2) chạy thật tối 12/10 trên bản sao seed (monitor tự ghi dòng 12/10 từ active_nav cùng ngày)
L="$T/live"; cp -r "$S" "$L"
export MIKE_LOSS_BRAKE_ALERT_SINK="$T/sink.jsonl"; : > "$MIKE_LOSS_BRAKE_ALERT_SINK"
{
  echo "### 0) dựng seed"; cat "$T/backfill.log" "$T/declare.log"
  echo; echo "### 1) CHẠY THẬT trên dữ liệu thật (state = bản sao seed, cảnh báo → sink), --now $NOW"
  $MON --state-dir "$L" --now "$NOW" 2>&1 && echo "rc=0" || echo "rc=$?"
  echo "--- lần 2, lượt 00:15 hôm sau (idempotent)"
  $MON --state-dir "$L" --now 2026-10-13T00:15:00 2>&1 && echo "rc=0" || echo "rc=$?"
  echo "sink lines: $(wc -l < "$MIKE_LOSS_BRAKE_ALERT_SINK")"
  echo "run_log.jsonl:"; cat "$L/run_log.jsonl"
  echo; echo "### 2) dòng ops_health sáng 13/10 (đọc status.json vừa ghi)"
  for a in SpaceX ZaloPay; do
    $MON --state-dir "$L" --now 2026-10-13T08:20:00 --health-line --account "$a" 2>&1 && echo "rc=0" || echo "rc=$?"
  done
  echo; echo "### 3) --date của phiên cũ ⇒ CHẠY KHÔ (không ghi status, không gửi)"
  $MON --state-dir "$L" --now "$NOW" --date 2026-10-09 2>&1 && echo "rc=0" || echo "rc=$?"
  echo "sink lines: $(wc -l < "$MIKE_LOSS_BRAKE_ALERT_SINK")"
  echo; echo "### 4a) CHƯA SEED gì (state rỗng)"
  E="$T/empty"; mkdir -p "$E"
  $MON --state-dir "$E" --now "$NOW" 2>&1 && echo "rc=0" || echo "rc=$?"
  echo; echo "### 4b) có sổ khai nhưng CHƯA vá chuỗi mã loại trừ ⇒ chuỗi bắt đầu muộn: KHÔNG âm thầm đặt lại đỉnh"
  E2="$T/noseed"; mkdir -p "$E2"
  cp "$HERE/seed_inputs/managed_sleeve_flows.json" "$HERE/seed_inputs/episodes.json" "$E2/"
  $MON --state-dir "$E2" --now "$NOW" 2>&1 && echo "rc=0" || echo "rc=$?"
  echo; echo "### 5) CA DGC — bỏ bản khai cổ tức 80tr (2026-09-14) khỏi managed_sleeve_flows.json"
  D="$T/dgc"; cp -r "$S" "$D"
  python3 - "$D/managed_sleeve_flows.json" <<'PY'
import json, sys
p = sys.argv[1]; d = json.load(open(p, encoding="utf-8"))
d["ZaloPay"] = [r for r in d["ZaloPay"] if r["date"] != "2026-09-14"]
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
PY
  : > "$T/sink_dgc.jsonl"
  MIKE_LOSS_BRAKE_ALERT_SINK="$T/sink_dgc.jsonl" $MON --state-dir "$D" --now "$NOW" --account ZaloPay --date 2026-09-14 --write-backdated 2>&1 && echo "rc=0" || echo "rc=$?"
  python3 -c "import json,sys; [print(json.loads(l)['text']) for l in open(sys.argv[1], encoding='utf-8')]" "$T/sink_dgc.jsonl"
} > "$HERE/real_run_and_dgc_case.txt"
cp "$MIKE_LOSS_BRAKE_ALERT_SINK" "$HERE/sink_real_run.jsonl"

# ---- 3) replay toàn lịch sử trên state sau lượt chạy thật (đã có dòng 12/10)
$MON --state-dir "$L" --now "$NOW" --replay > "$HERE/replay_full_history.txt" 2>&1 || true
sed -i "s|$T|<tmp>|g" "$HERE/real_run_and_dgc_case.txt" "$HERE/replay_full_history.txt" "$HERE/sink_real_run.jsonl"
grep -E "===|phiên im lặng" "$HERE/replay_full_history.txt"
