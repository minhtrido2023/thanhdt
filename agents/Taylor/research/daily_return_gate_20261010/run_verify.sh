#!/usr/bin/env bash
# Mục kiểm chứng (2)-(5): chạy cổng (bản cuối của nhánh) trên bản sinh thử, đối chứng sửa tay,
# báo cáo ngày CŨ và 2 nháp tuần. Chỉ ĐỌC mike/reports; mọi output vào research/.
set -uo pipefail
W=/home/trido/thanhdt/WorkingClaude/wt-dailyreturn-1010
M=/home/trido/thanhdt/WorkingClaude/mike
R=$M/agents/Taylor/research/daily_return_gate_20261010
V=$R/verify
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
cd /home/trido/thanhdt/WorkingClaude
MEMO="$(mktemp -d /tmp/taylor_k1_memo.XXXXXX)"; export DAR_BQ_MEMO_DIR="$MEMO"
g() { # nhãn, file
  local t0; t0=$(date +%s)
  python3 $W/bin/report_return_gate.py --report "$2" > "$V/$1.txt" 2>&1; local rc=$?
  echo "VERIFY $1 rc=$rc $(( $(date +%s)-t0 ))s | $(grep -m1 'Đã kiểm' "$V/$1.txt" | cut -c1-110) | $(grep -c '^   • ' "$V/$1.txt") mục"
}
for A in ZaloPay SpaceX; do for D in 2026-10-02 2026-10-09; do g "trial_${A}_${D}" "$R/trial/${A}_daily_report_${D}.md"; done; done
# (3) đối chứng: sửa tay MỘT tỉ suất trong bản sinh thử
mkdir -p "$V/tamper"
for A in ZaloPay SpaceX; do
  F="$V/tamper/${A}_daily_report_2026-10-02.md"
  python3 - "$R/trial/${A}_daily_report_2026-10-02.md" "$F" <<'PY'
import re, sys
s = open(sys.argv[1], encoding="utf-8").read()
m = re.search(r"([A-Z][A-Z0-9]{2}) (\d[\d.,]*M), ([+-]\d+\.\d\d)%", s)
new = f"{float(m.group(3)) + 1.5:+.2f}"
open(sys.argv[2], "w", encoding="utf-8").write(s[:m.start(3)] + new + s[m.end(3):])
print(f"TAMPER {sys.argv[2].split('/')[-1]}: {m.group(1)} {m.group(3)}% -> {new}%")
PY
  g "tamper_${A}_2026-10-02" "$F"
done
# (4) báo cáo ngày CŨ đã gửi
for D in 2026-10-01 2026-10-02 2026-10-09; do for A in ZaloPay SpaceX; do g "old_${A}_${D}" "$M/reports/${A}_daily_report_${D}.md"; done; done
# (5) 2 nháp tuần
for F in /home/trido/thanhdt/WorkingClaude/wt-1558282936489611354/reports/*_weekly_report_2026-10-05_to_2026-10-09.md; do g "weekly_$(basename "$F" .md)" "$F"; done
rm -rf "$MEMO"
echo ALLDONE
