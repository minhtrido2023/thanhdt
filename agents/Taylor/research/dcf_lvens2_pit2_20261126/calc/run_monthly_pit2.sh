#!/usr/bin/env bash
# Cron 08:20 ICT ngày 1–5 (kb/cron_registry.md). Một lượt hằng tháng: extract CA → lvens2 (stepcar) → sổ → commit khối tháng vào git (mốc chống sửa lén; .md5 cạnh file không đủ).
# Đã có tháng trong sổ ⇒ KHÔNG dựng lại (không ghi đè parquet đã dùng), chỉ commit bù file còn thiếu. Sổ khác bản đã commit ⇒ rc 3; commit không được sau mọi lần thử ⇒ rc 4.
# Env cho selfcheck: PCM_LEDGER, OUT_MONTHLY, CA_DIR, NO_GIT=1, PCM_NOW_ICT (bị từ chối với sổ chính), ASOF_YM, CA_YM, ALERT_CMD, GIT_TRIES, GIT_RETRY_S.
# rc≠0 ⇒ cảnh báo Discord kèm đuôi log (mất cả cửa sổ ngày 1–5 = mất tháng đó vĩnh viễn). Lượt thử (PCM_LEDGER/PCM_NOW_ICT/NO_GIT) không gửi thật trừ khi tự khai ALERT_CMD.
set -euo pipefail
if [ -z "${RUN_MONTHLY_PIT2_INNER:-}" ]; then
  log=$(mktemp); set +e
  RUN_MONTHLY_PIT2_INNER=1 bash "$0" "$@" 2>&1 | tee "$log"; rc=${PIPESTATUS[0]}
  set -e
  if [ "$rc" -ne 0 ]; then
    msg="🔴 lvens2 pit2 sổ forward LỖI rc=$rc ($(TZ=Asia/Ho_Chi_Minh date '+%d/%m %H:%M ICT')). Cron chạy lại mỗi ngày tới ngày 5; hết ngày 5 vẫn lỗi = MẤT tháng đó vĩnh viễn. Đuôi log:
$(tail -n 6 "$log" | cut -c1-300)"
    if [ -n "${ALERT_CMD:-}" ]; then "$ALERT_CMD" "$msg" || echo "NOTIFY_FAILED: $ALERT_CMD rc=$?" >&2
    elif [ -z "${PCM_LEDGER:-}${PCM_NOW_ICT:-}${NO_GIT:-}" ]; then
      /home/trido/thanhdt/WorkingClaude/mike/bin/notify_thread.sh "$msg" architecture || echo "NOTIFY_FAILED: notify_thread.sh rc=$?" >&2
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
# commit khối tháng + bản sao đầu vào (parquet bị .gitignore chặn nên PHẢI add -f); thử lại vì consolidate.sh giữ index.lock lúc :07 mỗi giờ.
commit_month() {
  [ -n "${NO_GIT:-}" ] && return 0
  local files=() f i ca="$CADIR/ca_extract_$CAYM.csv" md
  for f in "$LEDGER" "$LEDGER.blocks.jsonl" "$(dirname "$LEDGER")"/ledger_inputs/lvens2_"$YM"_* "$ca" "$ca.md5" "$ca.meta.json"; do
    if [ -f "$f" ]; then files+=("$f"); fi
  done
  md=$(cut -c1-8 "$ca.md5" 2>/dev/null || echo "?")
  for i in $(seq 1 "${GIT_TRIES:-30}"); do
    if git add -f -- "${files[@]}"; then
      if git diff --cached --quiet -- "${files[@]}"; then return 0; fi
      if git commit -q -m "lvens2 pit2 sổ forward: khối $YM (ca_extract $CAYM md5 $md)" -- "${files[@]}"; then
        echo "ĐÃ COMMIT $(git rev-parse --short HEAD)"; return 0
      fi
    fi
    echo "git chưa commit được (lần $i/${GIT_TRIES:-30}), thử lại"; sleep "${GIT_RETRY_S:-10}"
  done
  echo "FAIL: không commit được khối $YM sau ${GIT_TRIES:-30} lần (xem lỗi git phía trên)" >&2; return 4
}
if [ -f "$LEDGER" ] && grep -q "^$YM," "$LEDGER"; then echo "SKIP: $YM đã có trong sổ"; commit_month; exit 0; fi
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
commit_month
