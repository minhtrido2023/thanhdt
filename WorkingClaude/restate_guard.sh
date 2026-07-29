#!/usr/bin/env bash
# restate_guard.sh — cảnh báo LỊCH SỬ BỊ VIẾT LẠI sau mỗi lần deploy state table.
#
# Bối cảnh (RCA mike/agents/Winston/research/dt5g_history_restate_rca_20260729.md):
# pipeline DT5G rebuild TOÀN BỘ lịch sử mỗi đêm rồi `bq load --replace` đè bảng. Upstream
# (`ticker`, `ticker_prune`) là DROP+CREATE mỗi ngày, nên mọi backfill/điều chỉnh hồi tố
# (PE backfill 2006+, corp-action re-adjust Close, ticker_prune membership) lan qua các
# cửa sổ EXPANDING (pe_p90 override + expanding_pct_rank + rank-of-rank) và viết lại state
# của những phiên đã đóng từ nhiều năm trước. Ngày 2026-07-29: 134 phiên đổi ở
# vnindex_5state, 101 ở vnindex_5state_dt5g_live (35 phiên lệch >=2 tier, có phiên đổi
# CRISIS->BULL) — và sự kiện này LỌT QUA HOÀN TOÀN IM LẶNG, chỉ tình cờ được phát hiện.
# BQ time-travel không cứu được (upstream DROP+CREATE xoá sạch mỗi sáng), nên cách duy nhất
# là so bảng vừa deploy với bản archive predeploy chụp NGAY TRƯỚC khi ghi đè.
#
# Script này KHÔNG chặn deploy (chạy SAU khi đã ghi) — nó chỉ đảm bảo sự kiện restate không
# bao giờ trôi qua im lặng nữa. Nó cũng KHÔNG đụng mô hình (đó là việc của Taylor).
#
# Usage: restate_guard.sh <new_table> <archive_table> <label>
#   <new_table>     : bảng vừa deploy, dạng project.dataset.table
#   <archive_table> : bản snapshot NGAY TRƯỚC khi ghi đè, cùng schema (time,state,state_raw)
#   <label>         : nhãn hiển thị trong log/alert (vd "vnindex_5state (base v3.4b)")
#
# exit 0 = số phiên lịch sử đổi <= ngưỡng (quiet-heartbeat: chỉ ghi log + history jsonl)
# exit 2 = VƯỢT ngưỡng -> đã bắn bus event + Telegram + Discord Architecture topic
# exit 1 = bản thân check không chạy được (thiếu tham số / bq lỗi) -> caller ghi WARN,
#          KHÔNG die (guard là advisory, không được làm hỏng chuỗi refresh production)
#
# NGƯỠNG 5 — biên hẹp hơn tưởng (quant-skeptic 2026-07-29, verdict CONFIRMED/medium):
# churn NỀN đo thật trên 4 cặp archive predeploy liên tiếp (cùng metric hợp state-HOẶC-raw,
# cùng cửa sổ time < T-30) = 1 · 0 · 0 · **4**. Tức đã có 1 ngày thường chạm 4, chỉ dưới ngưỡng
# 1 đơn vị ⇒ alert dương-tính-giả trên churn corp-action bình thường là chuyện SẼ xảy ra, không
# phải chuyện hiếm. Giữ 5 vì đây là alert-only (giá của 1 tin thừa << giá của 1 lần restate lọt
# im lặng — chính là sự cố 2026-07-29). Nếu nhiễu: chỉnh RESTATE_ALERT_THRESHOLD (env, không cần
# sửa code); nên dựa trên phân bố `data/restate_guard_history.jsonl` tích luỹ được, đừng đoán.
#
# Env override: RESTATE_ALERT_THRESHOLD (5) · RESTATE_LOOKBACK_DAYS (30) ·
#               RESTATE_ARCH_TOPIC (1521475726329516122) · RESTATE_GUARD_DRYRUN=1 (không gửi)
# Test: restate_guard_selfcheck.sh (mô phỏng lại đúng sự kiện 2026-07-29).
set -uo pipefail

MIKE_BIN="/home/trido/thanhdt/WorkingClaude/mike/bin"
PJ="${PJ:-lithe-record-440915-m9}"
THRESH="${RESTATE_ALERT_THRESHOLD:-5}"
LOOKBACK="${RESTATE_LOOKBACK_DAYS:-30}"
# Architecture topic — sự cố hệ thống/toàn vẹn dữ liệu (khác Trading Daily = alert vận hành
# sống trong phiên). Xác nhận: kb/ops_runbook.md dòng "báo hoàn tất vào TOPIC ARCHITECTURE
# (1521475726329516122)" + memory feedback-architecture-topic-routing-needs-mechanism.
ARCH_TOPIC="${RESTATE_ARCH_TOPIC:-1521475726329516122}"
HIST="${RESTATE_GUARD_HISTORY:-/home/trido/thanhdt/WorkingClaude/data/restate_guard_history.jsonl}"

if [ "$#" -lt 3 ]; then
  echo "usage: $0 <new_table> <archive_table> <label>" >&2
  exit 1
fi
NEW_TBL="$1"; OLD_TBL="$2"; LABEL="$3"

CUTOFF="$(TZ='Asia/Ho_Chi_Minh' date -d "-${LOOKBACK} days" +%Y-%m-%d)"
NOW_ICT="$(TZ='Asia/Ho_Chi_Minh' date '+%Y-%m-%d %H:%M ICT')"

# FULL OUTER JOIN: dòng lịch sử BIẾN MẤT hoặc XUẤT HIỆN THÊM cũng là restate, không chỉ
# dòng đổi giá trị. `IS DISTINCT FROM` để NULL != giá trị được tính là đổi.
SQL="WITH o AS (SELECT time, state, state_raw FROM \`${OLD_TBL}\`),
     n AS (SELECT time, state, state_raw FROM \`${NEW_TBL}\`),
     j AS (
       SELECT COALESCE(o.time, n.time) AS t,
              o.state AS os, o.state_raw AS orw,
              n.state AS ns, n.state_raw AS nrw,
              o.time IS NULL AS added, n.time IS NULL AS dropped
       FROM o FULL OUTER JOIN n ON o.time = n.time
     ),
     f AS (SELECT *, (NOT added AND NOT dropped) AS common FROM j WHERE t < DATE('${CUTOFF}'))
SELECT
  COUNTIF(common AND (os IS DISTINCT FROM ns OR orw IS DISTINCT FROM nrw)) AS n_changed,
  COUNTIF(common AND os IS DISTINCT FROM ns)   AS n_state,
  COUNTIF(common AND orw IS DISTINCT FROM nrw) AS n_raw,
  COUNTIF(added)   AS n_added,
  COUNTIF(dropped) AS n_dropped,
  COUNT(*)         AS n_rows,
  IFNULL(ARRAY_TO_STRING(ARRAY_AGG(
    IF(common AND os IS DISTINCT FROM ns, FORMAT('%t %d->%d', t, os, ns), NULL)
    IGNORE NULLS ORDER BY t LIMIT 8), ' | '), '') AS sample
FROM f"

out="$(bq query --use_legacy_sql=false --project_id="$PJ" --format=csv --quiet "$SQL" 2>&1)"
rc=$?
row="$(printf '%s\n' "$out" | tail -1)"
if [ "$rc" -ne 0 ] || [ -z "$row" ]; then
  echo "  WARN restate_guard[$LABEL]: bq query FAILED (rc=$rc) — không kiểm tra được restate"
  printf '%s\n' "$out" | tail -5
  exit 1
fi

# parse CSV (7 cột; chỉ cột 'sample' cuối có thể bị quote — không chứa dấu phẩy nên an toàn)
IFS=',' read -r n_changed n_state n_raw n_added n_dropped n_rows sample <<< "$row"
sample="${sample%\"}"; sample="${sample#\"}"
case "${n_changed}${n_added}${n_dropped}" in
  ''|*[!0-9]*) echo "  WARN restate_guard[$LABEL]: không parse được kết quả: $row"; exit 1 ;;
esac

n_total=$(( n_changed + n_added + n_dropped ))

# lịch sử churn hằng ngày (RCA đo được nền ~0-1 phiên/ngày; file này biến nó thành số liệu
# quan sát được thay vì phải đào archive thủ công)
mkdir -p "$(dirname "$HIST")" 2>/dev/null
printf '{"ts":"%s","label":"%s","new":"%s","old":"%s","cutoff":"%s","n_changed":%s,"n_state":%s,"n_raw":%s,"n_added":%s,"n_dropped":%s,"n_total":%s,"threshold":%s}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$LABEL" "$NEW_TBL" "$OLD_TBL" "$CUTOFF" \
  "$n_changed" "$n_state" "$n_raw" "$n_added" "$n_dropped" "$n_total" "$THRESH" >> "$HIST" 2>/dev/null

echo "  restate_guard[$LABEL]: $n_total phiên lịch sử đổi (time < $CUTOFF, so $n_rows dòng)"
echo "    state đổi=$n_state · state_raw đổi=$n_raw · hợp=$n_changed · dòng thêm=$n_added · dòng mất=$n_dropped · ngưỡng=$THRESH"
[ -n "$sample" ] && echo "    mẫu: $sample"

if [ "$n_total" -le "$THRESH" ]; then
  echo "    OK (<= ngưỡng) — churn nền bình thường, không alert"
  exit 0
fi

MSG="🔁 RESTATE LỊCH SỬ $NOW_ICT — ${LABEL}: **$n_total phiên đã đóng bị VIẾT LẠI** trong lần refresh này (ngưỡng $THRESH).
· state đổi: $n_state · state_raw đổi: $n_raw · hợp (state HOẶC state_raw): $n_changed · dòng thêm: $n_added · dòng mất: $n_dropped
· cửa sổ: time < $CUTOFF (T-${LOOKBACK}, đã loại phần gần đây có thể đổi hợp lệ)
· so: $NEW_TBL (vừa deploy) vs $OLD_TBL (bản ngay trước khi ghi đè)
· mẫu (cũ→mới): ${sample:-n/a}
Nguyên nhân đã biết: upstream backfill/điều chỉnh hồi tố (PE, corp-action, ticker_prune membership) lan qua expanding-window → mọi backtest/audit trích DT5G lịch sử trước hôm nay CẦN CHẠY LẠI.
RCA: mike/agents/Winston/research/dt5g_history_restate_rca_20260729.md"

PAYLOAD="$(python3 - "$LABEL" "$NEW_TBL" "$OLD_TBL" "$CUTOFF" "$n_changed" "$n_state" "$n_raw" "$n_added" "$n_dropped" "$n_total" "$THRESH" "$sample" <<'PY'
import json, sys
k = ["label","new_table","archive_table","cutoff","n_changed","n_state","n_raw",
     "n_added","n_dropped","n_total","threshold","sample"]
v = sys.argv[1:13]
d = dict(zip(k, v))
for f in ("n_changed","n_state","n_raw","n_added","n_dropped","n_total","threshold"):
    d[f] = int(d[f])
d["rca"] = "mike/agents/Winston/research/dt5g_history_restate_rca_20260729.md"
d["impact"] = "moi ket qua backtest/audit trich DT5G lich su truoc lan refresh nay can chay lai"
print(json.dumps(d, ensure_ascii=False))
PY
)"

echo "    !!! VƯỢT NGƯỠNG — bắn alert (bus + Telegram + Architecture topic $ARCH_TOPIC)"
if [ "${RESTATE_GUARD_DRYRUN:-0}" = "1" ]; then
  echo "    [DRYRUN] bus payload: $PAYLOAD"
  echo "    [DRYRUN] message:"; printf '%s\n' "$MSG" | sed 's/^/      /'
  exit 2
fi

"$MIKE_BIN/append_event.sh" Winston error "dt5g-history-restate" "$PAYLOAD" 2>/dev/null \
  || echo "    WARN: append_event.sh failed"
"$MIKE_BIN/notify.sh" "$MSG" 2>/dev/null || echo "    WARN: notify.sh failed"
"$MIKE_BIN/notify_thread.sh" "$MSG" "$ARCH_TOPIC" 2>/dev/null || echo "    WARN: notify_thread.sh failed"
exit 2
