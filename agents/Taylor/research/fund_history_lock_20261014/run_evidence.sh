#!/usr/bin/env bash
# Dựng lại TOÀN BỘ bằng chứng nghiệm thu trên BẢN SAO dữ liệu thật trong /tmp, bằng code hiện tại
# của worktree. KHÔNG ghi vào data/ thật. Chạy: bash run_evidence.sh
set -uo pipefail
R="$(cd "$(dirname "$0")" && pwd)"
BASE=/tmp/fundlock_1014/final_base; APP=/tmp/fundlock_1014/final_applied
ACC="so du chup ~04:50 = so du luc dong cua: 0 lenh khop ngay 08-24, phan du dang thuc tien hai cua so ke <= 33d; gia = BQ Price 08-24 (ra soat job Taylor_20261014_020334)"
"$R/mk_sandbox.sh" "$BASE"; "$R/mk_sandbox.sh" "$APP"
run() { echo "\$ $*" | sed "s#$BASE#<base>#g; s#$APP#<applied>#g; s#$R#<research>#g"; "$@" 2>&1 | sed "s#$BASE#<base>#g; s#$APP#<applied>#g; s#$R#<research>#g"; echo "rc=${PIPESTATUS[0]}"; }

# ---- 1. số công bố trên bản sao CHƯA sửa
for a in SpaceX ZaloPay; do for d in 2026-10-09 2026-10-12 2026-10-13; do
  "$R/sbx.sh" "$BASE" nav_period_returns.py --account $a --report-date $d > "$R/acceptance/npr_base_${a}_$d.json" 2> "$R/acceptance/npr_base_${a}_$d.err"
done; "$R/sbx.sh" "$BASE" cash_identity.py --account $a --json > "$R/acceptance/ci_base_$a.json" 2>/dev/null; done

# ---- 2. sổ CHƯA sửa không chốt được (cổng)
{ for a in SpaceX ZaloPay; do
    run "$R/sbx.sh" "$BASE" nav_unit_ledger.py --account $a --seal --real-data --tail 0
  done; } > "$R/C_seal/log_base_refused.txt"

# ---- 3. D: đo tác động (dry-run, chỉ đọc) rồi áp vào bản sao
for a in SpaceX ZaloPay; do
  "$R/sbx.sh" "$APP" fund_restatement.py impact --account $a --correction "$R/corrections/correction_${a}_AB.json" \
      --out "$R/D_impact/impact_${a}_AB.json" > "$R/D_impact/impact_${a}_AB.txt" 2>&1; echo "impact $a rc=$?"
done
{ for a in SpaceX ZaloPay; do
    run "$R/sbx.sh" "$APP" fund_restatement.py apply --account $a --nav-dir "$APP/data/execution_logs" \
        --correction "$R/corrections/correction_${a}_AB.json" --impact-report "$R/D_impact/impact_${a}_AB.json" --approved-by "THU NGHIEM tren ban sao /tmp (Taylor)"
    run "$R/sbx.sh" "$APP" fund_restatement.py apply --account $a --nav-dir "$APP/data/execution_logs" --real-data \
        --correction "$R/corrections/correction_${a}_AB.json" --impact-report "$R/D_impact/impact_${a}_AB.json" --approved-by "THU NGHIEM tren ban sao /tmp (Taylor)"
    run "$R/sbx.sh" "$APP" fund_restatement.py apply --account $a --nav-dir "$APP/data/execution_logs" --real-data \
        --correction "$R/corrections/correction_${a}_AB.json" --impact-report "$R/D_impact/impact_${a}_AB.json" --approved-by "THU NGHIEM tren ban sao /tmp (Taylor)"
  done; } > "$R/D_impact/apply_log.txt"
cp "$R/corrections/cash_identity_acks_PROPOSED.json" "$APP/data/cash_identity_acks.json"
for a in SpaceX ZaloPay; do
  diff "$BASE/data/execution_logs/nav_history_$a.csv" "$APP/data/execution_logs/nav_history_$a.csv" > "$R/corrections/nav_history_${a}_AB.diff"
  for d in 2026-10-09 2026-10-12 2026-10-13; do
    "$R/sbx.sh" "$APP" nav_period_returns.py --account $a --report-date $d > "$R/acceptance/npr_applied_${a}_$d.json" 2> "$R/acceptance/npr_applied_${a}_$d.err"
  done
  "$R/sbx.sh" "$APP" cash_identity.py --account $a --json > "$R/acceptance/ci_applied_$a.json" 2>/dev/null
done

# ---- 4. C: chốt sổ trên bản sao đã áp A+B
{ for a in SpaceX ZaloPay; do
    run "$R/sbx.sh" "$APP" nav_unit_ledger.py --account $a --seal --tail 0
    run "$R/sbx.sh" "$APP" nav_unit_ledger.py --account $a --seal --real-data --tail 0
    run "$R/sbx.sh" "$APP" nav_unit_ledger.py --account $a --seal --real-data --tail 3 --accept-preclose "2026-08-24=$ACC"
    run "$R/sbx.sh" "$APP" nav_unit_ledger.py --account $a --seal --real-data --tail 0 --accept-preclose "2026-08-24=$ACC"
    run "$R/sbx.sh" "$APP" nav_unit_ledger.py --account $a --seal --real-data --tail 0
    run "$R/sbx.sh" "$APP" nav_unit_ledger.py --account $a --ledger-dir "$APP/data/execution_logs" --tail 0
    run md5sum "$APP/data/execution_logs/nav_unit_ledger_$a.csv"
    run wc -l "$APP/data/execution_logs/nav_unit_ledger_$a.csv"
    run cat "$APP/data/execution_logs/nav_unit_ledger_$a.csv.manifest.jsonl"
  done; } > "$R/C_seal/log.txt"
ls -la "$APP/data/execution_logs/" | grep -E "nav_unit_ledger|corrections" | sed "s#$APP#<applied>#g" >> "$R/C_seal/log.txt"
echo done
