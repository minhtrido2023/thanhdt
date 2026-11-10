#!/bin/bash
# Dựng sandbox chạy R3: code = wt-balgate-1110 @33f005209 (code control byte-identical hôm nay, có knob
# IDLE_CARRY_TIER), data = symlink tới data/ canonical; chân adj ghi đè 4 file LAG bằng bản dẫn xuất
# từ pkl adjusted. Script engine được CHÉP vào sandbox, chỉ đổi dòng WORKDIR. Usage: make_sandbox.sh ctrl|adj
set -euo pipefail
R="$(cd "$(dirname "$0")" && pwd)"; TAG="$1"
CODE=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-balgate-1110/WorkingClaude
WC=/home/trido/thanhdt/WorkingClaude
HEAD_ENGINE=$(git -C "$CODE" rev-parse HEAD)   # tái lập: engine PHẢI đúng 33f005209 (control byte-identical pin 2026-10-08)
case "$HEAD_ENGINE" in 33f005209*) ;; *) echo "DỪNG: HEAD engine $HEAD_ENGINE != 33f005209 — control sẽ không tái hiện pin" >&2; exit 7;; esac
S="$R/sandbox_$TAG"; rm -rf "$S"; mkdir -p "$S/data"
for f in "$CODE"/*; do b=$(basename "$f"); [ "$b" = data ] || ln -s "$f" "$S/$b"; done
for f in "$WC"/data/*; do ln -s "$f" "$S/data/$(basename "$f")"; done
for f in "$WC"/data/.[!.]*; do [ -e "$f" ] && ln -s "$f" "$S/data/$(basename "$f")"; done
rm "$S/pt_v23_audit_2014.py"
sed "s#^WORKDIR = r\"/home/trido/thanhdt/WorkingClaude\"#WORKDIR = r\"$S\"#" "$CODE/pt_v23_audit_2014.py" > "$S/pt_v23_audit_2014.py"
grep -q "^WORKDIR = r\"$S\"" "$S/pt_v23_audit_2014.py"
if [ "$TAG" = adj ]; then
  for f in earnings_events_classified.csv lag_edge_health.csv; do
    rm "$S/data/$f"; cp "$R/derived/${f%.csv}_adj.csv" "$S/data/$f"; done
  rm "$S/data/earnings_px.pkl" "$S/data/lagged_pos_ov.pkl"
  cp "$R/earnings_px_adj.pkl" "$S/data/earnings_px.pkl"; cp "$R/lagged_pos_ov_adj.pkl" "$S/data/lagged_pos_ov.pkl"
fi
echo "sandbox $S ready"
