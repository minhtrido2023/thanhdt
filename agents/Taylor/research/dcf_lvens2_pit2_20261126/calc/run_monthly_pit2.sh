#!/usr/bin/env bash
# ĐỀ XUẤT — CHƯA cài cron. Một lượt hằng tháng: extract CA → lvens2 (stepcar) → sổ → commit khối tháng vào git (mốc chống sửa lén; .md5 cạnh file không đủ).
# Đã có tháng trong sổ ⇒ thoát 0, KHÔNG dựng lại (không ghi đè parquet đã dùng). Sổ khác bản đã commit ⇒ rc 3.
# Env cho selfcheck: PCM_LEDGER, OUT_MONTHLY, CA_DIR, NO_GIT=1, PCM_NOW_ICT (bị từ chối với sổ chính), ASOF_YM, CA_YM, ALERT_CMD.
# rc≠0 ⇒ cảnh báo Discord kèm đuôi log (mất cả cửa sổ ngày 1–5 = mất tháng đó vĩnh viễn). Lượt thử (PCM_LEDGER/PCM_NOW_ICT/NO_GIT) không gửi thật trừ khi tự khai ALERT_CMD.
set -euo pipefail
if [ -z "${RUN_MONTHLY_PIT2_INNER:-}" ]; then
  log=$(mktemp); set +e
  RUN_MONTHLY_PIT2_INNER=1 bash "$0" "$@" 2>&1 | tee "$log"; rc=${PIPESTATUS[0]}
  set -e
  if [ "$rc" -ne 0 ]; then
    msg="🔴 lvens2 pit2 sổ forward LỖI rc=$rc ($(TZ=Asia/Ho_Chi_Minh date '+%d/%m %H:%M ICT')). Cron chạy lại mỗi ngày tới ngày 5; hết ngày 5 vẫn lỗi = MẤT tháng đó vĩnh viễn. Đuôi log:
$(tail -n 6 "$log" | cut -c1-300)"
    if [ -n "${ALERT_CMD:-}" ]; then "$ALERT_CMD" "$msg" || echo "ALERT_FAILED: $ALERT_CMD rc=$?" >&2
    elif [ -z "${PCM_LEDGER:-}${PCM_NOW_ICT:-}${NO_GIT:-}" ]; then
      /home/trido/thanhdt/WorkingClaude/mike/bin/notify_thread.sh "$msg" architecture || echo "ALERT_FAILED: notify_thread.sh rc=$?" >&2
    else echo "ALERT_SKIPPED: lượt thử, không gửi"; fi
  fi
  rm -f "$log"; exit "$rc"
fi
BASE=$(cd "$(dirname "$0")/.." && pwd); cd "$BASE"
PY=${PY:-/home/trido/thanhdt/wc_venv/bin/python}
export LVENS2_FROZEN=${LVENS2_FROZEN:-/home/trido/thanhdt/WorkingClaude/data/research_frozen/dcf_v31_inputs/out} PYTHONHASHSEED=0
this_first=$(TZ=Asia/Ho_Chi_Minh date +%Y-%m-01)
YM=${ASOF_YM:-$(date -u -d "$this_first -1 day" +%Y-%m)}
CAYM=${CA_YM:-$(TZ=Asia/Ho_Chi_Minh date +%Y%m)}
LEDGER=${PCM_LEDGER:-out/paper_cell_ledger_pit2.csv}; MON=${OUT_MONTHLY:-out/monthly}; CADIR=${CA_DIR:-out/ca}
echo "=== run_monthly_pit2 as-of $YM, extract $CAYM, $(TZ=Asia/Ho_Chi_Minh date '+%F %T ICT') ==="
if [ -z "${NO_GIT:-}" ] && git ls-files --error-unmatch "$LEDGER" >/dev/null 2>&1; then
  git diff --quiet HEAD -- "$LEDGER" "$LEDGER.blocks.jsonl" || { echo "FAIL-CLOSED: $LEDGER hoặc sidecar khác bản đã commit (git diff HEAD) — kiểm thủ công trước" >&2; exit 3; }
fi
if [ -f "$LEDGER" ] && grep -q "^$YM," "$LEDGER"; then echo "SKIP: $YM đã có trong sổ"; exit 0; fi
if [ ! -f "$CADIR/ca_extract_$CAYM.csv.md5" ]; then
  set +u
  # shellcheck disable=SC1091
  . /home/trido/thanhdt/WorkingClaude/wc_env.sh >/dev/null; set -u; cd "$BASE"    # wc_env.sh đổi thư mục
fi
"$PY" calc/make_ca_extract.py --ym "$CAYM" --out-dir "$CADIR"
export LVENS2_CA="$CADIR/ca_extract_$CAYM.csv"
LVENS2_CA_MD5=$(cut -d' ' -f1 "$LVENS2_CA.md5"); export LVENS2_CA_MD5
timeout 900 "$PY" calc/lvens2_pit2.py --asof-ym "$YM" --mc-pit stepcar --out-dir "$MON"
timeout 300 "$PY" calc/paper_cell_monthly_pit2.py --asof-ym "$YM" --ledger "$LEDGER" --lvens2-from "$MON/lvens2_${YM}_mcstepcar.parquet"
if [ -z "${NO_GIT:-}" ]; then
  files=("$LEDGER" "$LEDGER.blocks.jsonl" "$(dirname "$LEDGER")"/ledger_inputs/lvens2_"$YM"_* "$LVENS2_CA" "$LVENS2_CA.md5")
  [ -f "$LVENS2_CA.meta.json" ] && files+=("$LVENS2_CA.meta.json")
  git add -f -- "${files[@]}"
  git commit -q -m "lvens2 pit2 sổ forward: khối $YM (ca_extract $CAYM md5 ${LVENS2_CA_MD5:0:8})" -- "${files[@]}"
  echo "ĐÃ COMMIT $(git rev-parse --short HEAD)"
fi
