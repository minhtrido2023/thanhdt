#!/usr/bin/env bash
# Nghiệm thu vòng 2 (job Taylor_20261014_033336) — trên BẢN SAO dữ liệu thật trong /tmp, bằng code
# hiện tại của worktree. KHÔNG ghi vào data/ thật (chỉ ĐỌC data/ thật ở mục 1).
# ⚠️ Phải chạy trong khung 09:00–18:30 ICT: `apply` trên bản sao (thư mục có dnse_raw ⇒ "thật") không
# nhận giờ giả. Chạy: bash run_acceptance_round2.sh
set -uo pipefail
H="$(cd "$(dirname "$0")" && pwd)"            # round2/
R="$(dirname "$H")"                           # fund_history_lock_20261014/ (trong worktree)
WT="$(git -C "$H" rev-parse --show-toplevel)"
REAL=/home/trido/thanhdt/WorkingClaude
OLD=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/fund_history_lock_20261014
BASE=/tmp/fl2/base; APP=/tmp/fl2/app; OUT="$H/acceptance"
ACC="so du chup ~04:50 = so du luc dong cua: 0 lenh khop ngay 08-24, phan du dang thuc tien hai cua so ke <= 33d; gia = BQ Price 08-24 (ra soat job Taylor_20261014_020334)"
mkdir -p "$OUT"; rm -f "$OUT"/*
sb() { local S="$1"; shift; local P="$1"; shift; WC_ROOT="$S" TZ=Asia/Ho_Chi_Minh python3 "$S/mike/bin/$P" "$@"; }
run() { echo "\$ $*" | sed "s#$BASE#<base>#g; s#$APP#<app>#g; s#$R#<research>#g"; "$@" 2>&1 | sed "s#$BASE#<base>#g; s#$APP#<app>#g; s#$R#<research>#g"; echo "rc=${PIPESTATUS[0]}"; }
"$OLD/mk_sandbox.sh" "$BASE" "$WT" >/dev/null; "$OLD/mk_sandbox.sh" "$APP" "$WT" >/dev/null
md5sum "$REAL"/data/execution_logs/nav_history_{SpaceX,ZaloPay}.csv > "$OUT/real_md5_before.txt"

# ---- 1. 18 số công bố: dữ liệu THẬT (chỉ đọc) + code NHÁNH; bản sao chưa sửa; bản sao đã áp
pub() {   # $1 nhãn, $2 WC_ROOT, $3 thư mục bin
  for a in SpaceX ZaloPay; do for d in 2026-10-09 2026-10-12 2026-10-13; do
    WC_ROOT="$2" TZ=Asia/Ho_Chi_Minh python3 "$3/nav_period_returns.py" --account $a --report-date $d 2>/dev/null \
      | python3 -c "import json,sys; j=json.load(sys.stdin); print('$1 $a $d', *(f\"{j[k]['return_pct']:+.3f}\" for k in ('inception','mtd','wtd')))"
  done; done; }
pub real_data_branch_code "$REAL" "$WT/bin" > "$OUT/published_18.txt"
pub base_copy "$BASE" "$BASE/mike/bin" >> "$OUT/published_18.txt"

# ---- 2. đo tác động (chỉ đọc) + áp vào bản sao
for a in SpaceX ZaloPay; do
  sb "$APP" fund_restatement.py impact --account $a --correction "$R/corrections/correction_${a}_AB.json" \
     --out "$OUT/impact_${a}_AB.json" > "$OUT/impact_${a}_AB.txt" 2>&1; echo "impact $a rc=$?" >> "$OUT/impact_rc.txt"
done
{ for a in SpaceX ZaloPay; do
    A=(apply --account $a --nav-dir "$APP/data/execution_logs" --correction "$R/corrections/correction_${a}_AB.json"
       --impact-report "$OUT/impact_${a}_AB.json" --approved-by "THU NGHIEM tren ban sao /tmp (Taylor, vong 2)")
    echo "## B2: thư mục có dnse_raw_*.jsonl (bản sao) mà thiếu --real-data ⇒ rc=3"
    run sb "$APP" fund_restatement.py "${A[@]}"
    echo "## B2: WC_ROOT = sandbox RỖNG khác, --nav-dir = bản sao có dnse_raw ⇒ vẫn rc=3"
    run env WC_ROOT=/tmp/fl2/empty TZ=Asia/Ho_Chi_Minh python3 "$APP/mike/bin/fund_restatement.py" "${A[@]}"
    echo "## B4: giờ giả bị từ chối ở thư mục dữ liệu thật (NAV_HISTORY_DIR của WC_ROOT)"
    run env FUND_RESTATEMENT_TEST_NOW_ICT=2026-10-14T10:00:00 WC_ROOT="$APP" TZ=Asia/Ho_Chi_Minh python3 "$APP/mike/bin/fund_restatement.py" "${A[@]}" --real-data
    echo "## áp thật trên bản sao (giờ thật, trong khung)"
    run sb "$APP" fund_restatement.py "${A[@]}" --real-data
    echo "## áp lần hai ⇒ ĐÃ ÁP từ trước"
    run sb "$APP" fund_restatement.py "${A[@]}" --real-data
  done; } > "$OUT/apply_log.txt"
for a in SpaceX ZaloPay; do
  diff "$BASE/data/execution_logs/nav_history_$a.csv" "$APP/data/execution_logs/nav_history_$a.csv" > "$OUT/nav_history_${a}_AB.diff"
  echo "$a dòng đổi: $(grep -c '^>' "$OUT/nav_history_${a}_AB.diff")" >> "$OUT/backup_check.txt"
  for f in "$APP"/data/execution_logs/restatement_backups/${a}_*.csv; do
    cmp -s "$f" "$BASE/data/execution_logs/nav_history_$a.csv" && echo "$a sao lưu $(basename "$f") = NGUYÊN BYTE nav_history trước khi áp" >> "$OUT/backup_check.txt"
  done
done
cp "$APP/data/execution_logs/nav_history_corrections.jsonl" "$OUT/nav_history_corrections.jsonl"
pub applied_copy "$APP" "$APP/mike/bin" >> "$OUT/published_18.txt"

# ---- 3. cash_identity cho CẢ HAI tài khoản với từng phương án B3 (+ file acks hiện hành)
for opt in current option1_rekey option2_keep_old_add_new; do
  case $opt in current) src="$REAL/data/cash_identity_acks.json";; *) src="$R/corrections/cash_identity_acks_B3_${opt}.json";; esac
  for a in SpaceX ZaloPay; do
    sb "$APP" cash_identity.py --account $a --json --acks-path "$src" 2>/dev/null | python3 -c "
import json,sys; j=json.load(sys.stdin); w=j.get('windows') or []
sus=[x for x in w if x.get('suspect')]
print('$opt $a', 'cua_so', len(w), 'nghi_van', len(sus), [(x.get('snap0'),x.get('snap1'),x.get('kind')) for x in sus][:3])" >> "$OUT/cash_identity_B3.txt" 2>&1
  done
done

# ---- 4. chốt sổ trên bản sao đã áp (SEAL_MD5) + B12/B13
{ for a in SpaceX ZaloPay; do
    run sb "$APP" nav_unit_ledger.py --account $a --seal --tail 0
    run sb "$APP" nav_unit_ledger.py --account $a --seal --real-data --tail 0
    run sb "$APP" nav_unit_ledger.py --account $a --seal --real-data --tail 0 --accept-preclose "2026-08-24=$ACC"
    run sb "$APP" nav_unit_ledger.py --account $a --ledger-dir "$APP/data/execution_logs" --tail 0
    run md5sum "$APP/data/execution_logs/nav_unit_ledger_$a.csv" "$APP/data/execution_logs/nav_unit_ledger_$a.csv.manifest.jsonl"
  done; } > "$OUT/seal_log.txt"

# ---- 5. tái hiện B6 (demo của reviewer, dựng lại bằng code mới): nhận "NAV 1010 lúc 10:00", rồi dòng đổi thành "NAV 1005 lúc 11:00"
D=/tmp/fl2/demo_b6; rm -rf "$D"; mkdir -p "$D/L" "$D/old" "$D/rep"
echo '{"T": {"inception_date": "2026-07-01", "starting_capital": 1000}}' > "$D/inc.json"; echo '{"T": []}' > "$D/flows.json"
H1='date,nav,mtm_stock,cash,margin_debt,offbook_assets,egg_assets,balance_ts,cum_dividend_excl,nav_is_estimate,nav_source'
printf '%s\n2026-07-02,1010,0,1010,0,,,2026-07-02T10:00:00,,,\n2026-07-03,1020,0,1020,0,,,2026-07-03T19:10:00,,,\n' "$H1" > "$D/nav_history_T.csv"
cp "$D/nav_history_T.csv" "$D/old/"
L=(--account T --nav-dir "$D" --inception-path "$D/inc.json" --flows-path "$D/flows.json" --ledger-dir "$D/L" --tail 0)
{ run env WC_ROOT=/tmp/fl2/empty python3 "$WT/bin/nav_unit_ledger.py" "${L[@]}" --immutable --seal --accept-preclose "2026-07-02=đã rà NAV 1010 là giá chốt"
  printf '%s\n2026-07-02,1005,0,1005,0,,,2026-07-02T11:00:00,,,\n2026-07-03,1020,0,1020,0,,,2026-07-03T19:10:00,,,\n' "$H1" > "$D/nav_history_T.csv"
  run env WC_ROOT=/tmp/fl2/empty python3 "$WT/bin/fund_restatement.py" impact --account T --old-nav-dir "$D/old" --new-nav-dir "$D" \
      --inception-path "$D/inc.json" --flows-path "$D/flows.json" --reports-dir "$D/rep" --sealed-ledger "$D/L/nav_unit_ledger_T.csv" --out "$D/imp.json"
  echo "## restate KHÔNG nhận lại ⇒ phải bị CHẶN (lời nhận cũ là của dòng NAV 1010 lúc 10:00)"
  run env WC_ROOT=/tmp/fl2/empty python3 "$WT/bin/nav_unit_ledger.py" "${L[@]}" --restate --impact-report "$D/imp.json" --reason x --approved-by x
  echo "## nhận lại tường minh ⇒ qua"
  run env WC_ROOT=/tmp/fl2/empty python3 "$WT/bin/nav_unit_ledger.py" "${L[@]}" --restate --impact-report "$D/imp.json" --reason x --approved-by x \
      --accept-preclose "2026-07-02=rà lại: NAV 1005 lúc 11:00"
  run tail -1 "$D/L/nav_unit_ledger_T.csv.manifest.jsonl"; } > "$OUT/demo_B6.txt" 2>&1

md5sum "$REAL"/data/execution_logs/nav_history_{SpaceX,ZaloPay}.csv > "$OUT/real_md5_after.txt"
cmp -s "$OUT/real_md5_before.txt" "$OUT/real_md5_after.txt" && echo "data/ thật KHÔNG đổi" > "$OUT/real_untouched.txt"
echo done
