#!/usr/bin/env bash
# daily_refresh_v34b_linux.sh
# ============================================================================
# Linux-native daily refresh of the v3.4b BASE + DT5G live state on the server.
# Replaces the Windows daily_refresh_v3_4b.bat chain (whose deploy step uses
# backticks that /bin/sh mis-parses on Linux). Runs the full rebuild locally,
# loads to BQ tav2_bq.vnindex_5state, SYNCS _v34b_clean (nothing else does),
# then republishes vnindex_5state_dt5g_live.
#
# Auth: sources wc_env.sh -> CLOUDSDK_CONFIG = dtienthanh@gmail.com (read-WRITE).
# Schedule: cron Mon-Fri 18:30 ICT (after market close + ticker ingest; moved from a
# drifted 23:15 ICT slot 2026-07-10 — verified ticker_prune/ticker ingest actually completes
# well before 18:45 on a normal day, matching this script's own long-standing "~18:05" intent
# that the crontab had silently drifted ~5h away from). Step [0] below verifies the day's
# ingest is actually complete before computing, rather than trusting the clock alone.
# Log: data/refresh_v34b_linux_<YYYY-MM-DD>.log  (rolling, 30-day cleanup)
# ============================================================================
set -uo pipefail

source /home/trido/thanhdt/WorkingClaude/wc_env.sh
export STATE_WORKDIR="$WORKDIR_8L"
PY="$DNA_PYEXE"
PJ="lithe-record-440915-m9"
cd "$WORKDIR_8L"

LOG="data/refresh_v34b_linux_$(date +%Y-%m-%d).log"
exec >>"$LOG" 2>&1
echo "==================================================================="
echo "v3.4b/DT5G Linux refresh START $(date)  acct=$(gcloud config get-value account 2>/dev/null)"
echo "==================================================================="

die() { echo "!!! ABORT: $* (at $(date))"; exit 1; }
step() { echo; echo "--- $* ---"; }

# --- 0. freshness precheck: verify TODAY's ticker_prune ingest is actually complete before
# computing on it. Found 2026-07-10 (user asked "does this really need to wait for the full
# BQ sync?"): ticker_prune/ticker were BOTH already complete (normal-range row counts) well
# before this job's old 23:15 ICT slot — the schedule had drifted ~5h later than this script's
# own documented "~18:05 ICT" intent for no discovered reason, silently masked by
# bq_freshness_check.sh's MAX_STATE_LAG=2 tolerance (1-day-stale always passed as "fine").
# Rather than just picking a new fixed clock time and hoping it's always ready, verify the
# real artifact: retry with a bounded wait instead of computing on an incomplete/stale day.
step "[0] freshness precheck: today's ticker_prune ingest complete?"
TODAY_ICT="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"
MIN_TICKERS=200   # historical daily count is ~260-270; 200 comfortably excludes a partial trickle
ready=0
for attempt in $(seq 1 6); do
  n="$(bq query --use_legacy_sql=false --project_id="$PJ" --format=csv --quiet \
    "SELECT COUNT(DISTINCT ticker) FROM tav2_bq.ticker_prune WHERE time = DATE('$TODAY_ICT')" \
    2>/dev/null | tail -1)"
  n="${n:-0}"
  if [ "$n" -ge "$MIN_TICKERS" ] 2>/dev/null; then
    echo "  ready: ticker_prune has $n tickers for $TODAY_ICT (attempt $attempt)"
    ready=1; break
  fi
  echo "  not ready yet: ticker_prune has ${n:-0} tickers for $TODAY_ICT (need >=$MIN_TICKERS) — attempt $attempt/6, waiting 15m"
  [ "$attempt" -lt 6 ] && sleep 900
done
[ "$ready" = 1 ] || die "ticker_prune still incomplete for $TODAY_ICT after 6 attempts (~1.5h) — refusing to compute DT5G on a stale/partial day. bq_freshness_check.sh's own gate will BLOCK DollarBill downstream since vnindex_5state_dt5g_live won't advance today."

# --- 1. upstream local rebuild (produces vnindex_5state_tam_quan_v3_4b_full_history.csv) ---
# Mốc thời gian cho post-chain freshness assertion (step [8b] dưới): mọi file output kỳ
# vọng phải có mtime >= mốc này, nếu không chain die TRƯỚC khi publish BQ. Đặt SAU step
# [0] (precheck có thể chờ tới ~1.5h) để không nới lỏng assertion oan.
CHAIN_START_EPOCH="$(date +%s)"

step "[1] clear pkl caches"
rm -f data/_cache_vnindex_2000_now.pkl data/_cache_universe_2013_now.pkl

step "[2] pull_us_market.py"
$PY pull_us_market.py || die "pull_us_market"

step "[3] ew_v1 (BQ ticker pull; retry x3 on flaky failure)"
ok=0
for try in 1 2 3; do
  if $PY vnindex_5state_ew_v1.py; then ok=1; break; fi
  echo "  ew_v1 attempt $try failed; clearing cache + retry"; rm -f _cache_universe_2013_now.pkl; sleep 5
done
[ "$ok" = 1 ] || die "ew_v1 failed after 3 attempts"

step "[4] build_concentration_history.py"; $PY build_concentration_history.py || die "concentration"
step "[5] vnindex_5state_dual_v3.py";      $PY vnindex_5state_dual_v3.py      || die "dual_v3"
step "[6] build_v3_1_clean.py";            $PY deploy_v3_4b_package/build_v3_1_clean.py || die "v3_1_clean"
cp data/vnindex_5state_tam_quan_v3_1_clean.csv data/vnindex_5state_tam_quan_v3_1_full_history.csv || die "cp v3_1"
step "[7] build_v3_4_bull_aware.py";       $PY deploy_v3_4b_package/build_v3_4_bull_aware.py || die "v3_4b"
# build_v3_4_bull_aware.py ghi root CHỦ ĐÍCH (bq load bên dưới đọc root) — mirror sang
# data/ để ~30 script research + build_dt_4gate.py (đọc data/) không bao giờ đọc bản
# đóng băng nữa (audit Winston_20260710_173031: data/v3_4b frozen Jun-30 trong khi root
# tươi hằng đêm → dt_4gate build lại mỗi đêm từ base cũ). Cùng pattern cp v3_1 ở trên.
cp vnindex_5state_tam_quan_v3_4b_full_history.csv data/vnindex_5state_tam_quan_v3_4b_full_history.csv || die "cp v3_4b -> data/"
step "[8] build_dt_4gate.py (local, non-fatal)"; $PY build_dt_4gate.py || echo "  WARN: dt_4gate failed (non-fatal)"

# --- 1b. post-chain output freshness assertion (audit Winston_20260710_173031) ---
# Cơ chế tổng quát chống writer-ghi-sai-path/step-sót: MỌI file output kỳ vọng của chain
# compute (step 2-8) phải có mtime >= CHAIN_START_EPOCH. Thiếu/cũ → die + alert TRƯỚC
# backup/deploy, để dữ liệu stale không bao giờ lên BQ production. Đây chính là lỗ hổng
# để bug EW-leg (writer ghi root, chain đọc data/ frozen 06-19) sống 3 tuần không ai thấy.
step "[8b] post-chain freshness assertion (mtime >= chain start)"
REQUIRED_OUTPUTS=(
  data/us_market_history.csv                             # step 2
  data/vnindex_5state_ew_full.csv                        # step 3
  data/vnindex_5state_ew_staging.csv                     # step 3
  data/concentration_history.csv                         # step 4
  data/vnindex_5state_dual_v3_staging.csv                # step 5
  data/vnindex_5state_dual_v3_full.csv                   # step 5
  data/vnindex_5state_tam_quan_v3_1_clean.csv            # step 6
  data/vnindex_5state_tam_quan_v3_1_full_history.csv     # step 6 cp
  vnindex_5state_tam_quan_v3_4b_full_history.csv         # step 7 (root, chủ đích — bq load đọc)
  data/vnindex_5state_tam_quan_v3_4b_full_history.csv    # step 7 cp mirror
)
if ! ./assert_chain_outputs.sh "$CHAIN_START_EPOCH" "${REQUIRED_OUTPUTS[@]}"; then
  ALERT="🛑 daily_refresh_v34b ABORT $(TZ='Asia/Ho_Chi_Minh' date '+%Y-%m-%d %H:%M ICT'): post-chain freshness assertion FAIL — có file output MISSING/STALE (writer sót hoặc ghi sai path). KHÔNG publish BQ. Xem $LOG."
  /home/trido/thanhdt/WorkingClaude/mike/bin/notify.sh "$ALERT" 2>/dev/null || true
  /home/trido/thanhdt/WorkingClaude/mike/bin/notify_thread.sh "$ALERT" "1521470705563340910" 2>/dev/null || true
  die "post-chain freshness assertion FAILED — stale/missing intermediate, refusing to publish"
fi
# dt_4gate: ADVISORY only (step [8] non-fatal by design, consumer chỉ research/test —
# audit xác nhận không nằm trên đường publish BQ). Stale/thiếu → alert rõ ràng nhưng
# KHÔNG chặn publish production.
if ! ./assert_chain_outputs.sh "$CHAIN_START_EPOCH" data/vnindex_5state_dt_4gate.csv; then
  WMSG="⚠️ daily_refresh_v34b $(TZ='Asia/Ho_Chi_Minh' date '+%Y-%m-%d %H:%M ICT'): data/vnindex_5state_dt_4gate.csv MISSING/STALE (step [8] non-fatal, research-only) — chain vẫn tiếp tục publish, nhưng cần xem $LOG."
  echo "  WARN: dt_4gate output stale/missing (advisory, không chặn publish)"
  /home/trido/thanhdt/WorkingClaude/mike/bin/notify.sh "$WMSG" 2>/dev/null || true
fi

CSV="vnindex_5state_tam_quan_v3_4b_full_history.csv"  # build_v3_4_bull_aware.py saves to WORKDIR root (not data/)
LOCAL_MAX="$(tail -1 "$CSV" | cut -d, -f1)"
echo "local v3.4b CSV max date = $LOCAL_MAX"
[ -n "$LOCAL_MAX" ] || die "v3.4b CSV empty"

# --- 2. backup (dated, keep last 5) ---
step "[9] backup vnindex_5state + dt5g_live (dated)"
TS="$(date +%Y%m%d_%H%M%S)"
bq query --use_legacy_sql=false --project_id="$PJ" \
  "CREATE TABLE \`$PJ.tav2_bq.vnindex_5state_archive_predeploy_$TS\` AS SELECT * FROM \`$PJ.tav2_bq.vnindex_5state\`" || die "backup bare"
# prune: keep newest 5 predeploy backups of the bare table
for old in $(bq ls --max_results=1000 tav2_bq 2>/dev/null | grep -oE 'vnindex_5state_archive_predeploy_[0-9_]+' | sort | head -n -5); do
  echo "  prune old backup $old"; bq rm -f -t "$PJ:tav2_bq.$old"
done
# dt5g_live cũng cần bản predeploy: step [12] publish đè thẳng bảng production mà trước đây
# KHÔNG có snapshot dated nào (RCA 2026-07-29 mục 6 ưu tiên 2) ⇒ không có gì để so khi lịch
# sử bị viết lại, và BQ time-travel thì đã chết vì upstream DROP+CREATE mỗi sáng. Chụp ở
# ĐÂY (trước publish) để step [12b] diff được bản-ngay-trước-khi-ghi-đè. Non-fatal: thiếu
# backup chỉ làm mất guard, không được chặn publish production.
bq query --use_legacy_sql=false --project_id="$PJ" \
  "CREATE TABLE \`$PJ.tav2_bq.vnindex_5state_dt5g_live_archive_predeploy_$TS\` AS SELECT * FROM \`$PJ.tav2_bq.vnindex_5state_dt5g_live\`" \
  || echo "  WARN: backup dt5g_live predeploy FAILED (step [12b] restate guard sẽ skip)"
for old in $(bq ls --max_results=1000 tav2_bq 2>/dev/null | grep -oE 'vnindex_5state_dt5g_live_archive_predeploy_[0-9_]+' | sort | head -n -5); do
  echo "  prune old backup $old"; bq rm -f -t "$PJ:tav2_bq.$old"
done

# --- 3. deploy: load bare, sync _v34b_clean ---
# ── BẢNG CÔNG BỐ BẤT BIẾN (2026-07-30, job Taylor_20260730_013951) ──────────────────────
# TRƯỚC: `bq load --replace` đè TOÀN BỘ bảng mỗi đêm ⇒ mọi restate upstream (PE backfill,
# corp-action re-adjust, ticker_prune membership) lan qua cửa sổ EXPANDING và VIẾT LẠI state
# của phiên đã đóng nhiều năm trước, im lặng (2026-07-29: 134 phiên ở bảng này).
# GIỜ: append phiên mới + recompute đuôi 25 phiên chưa chốt; phần đã chốt bất khả xâm phạm.
# CÔNG THỨC KHÔNG ĐỔI một dòng nào — chỉ đổi CÁCH GHI. Cơ sở N=25 + thiết kế: docstring
# state_publish_immutable.py. Abort => die (bảng giữ bản hôm qua, gate freshness chặn hạ nguồn).
step "[10] publish BẤT BIẾN -> vnindex_5state (append + recompute đuôi 25 phiên)"
$PY state_publish_immutable.py --csv "$WORKDIR_8L/$CSV" \
    --table tav2_bq.vnindex_5state \
    --label "vnindex_5state (base v3.4b)" || die "immutable publish bare"

step "[11] sync _v34b_clean <- vnindex_5state"
# Cột PHẢI liệt kê TƯỜNG MINH, KHÔNG `SELECT *` (sửa 2026-07-30, quant-skeptic bắt được):
# publisher bất biến thêm cột audit `asof_date` vào `vnindex_5state`. `SELECT *` sẽ âm thầm
# nhân bản cột đó sang `_v34b_clean` — bảng có ~50 consumer chưa ai audit về giả định số cột.
# `asof_date` là metadata CỦA HÀNH ĐỘNG CÔNG BỐ, không thuộc đặc tả chuỗi state, nên nó không
# có việc gì ở bảng hạ nguồn. Ghim 3 cột giữ đúng hợp đồng "_v34b_clean == vnindex_5state"
# (CLAUDE.md) cho mọi consumer, và mọi cột audit thêm sau này cũng tự động không lan xuống.
bq query --use_legacy_sql=false --project_id="$PJ" \
  'CREATE OR REPLACE TABLE tav2_bq.vnindex_5state_tam_quan_v34b_clean AS SELECT time, state, state_raw FROM tav2_bq.vnindex_5state' || die "sync _v34b_clean"

# --- 3b. restate guard: lịch sử đã đóng có bị viết lại không? ---
# RCA dt5g_history_restate_rca_20260729.md: chain này rebuild TOÀN BỘ lịch sử mỗi đêm từ
# upstream có thể restate (PE backfill, corp-action re-adjust, ticker_prune membership) qua
# expanding-window, rồi bq load --replace đè bảng — nên state của phiên đã đóng nhiều năm
# trước vẫn đổi được. 2026-07-29: 134 phiên base + 101 phiên dt5g_live bị viết lại và
# KHÔNG có gì cảnh báo. Guard chạy SAU deploy (alert-only, không chặn) và cố ý là advisory:
# guard hỏng thì chain vẫn phải chạy tiếp.
# Hai env override dưới đây là BẮT BUỘC sau khi bật publish bất biến, và phải giống nhau ở CẢ
# HAI lần gọi guard ([11b] base + [12b] dt5g_live) — cả hai bảng giờ đều publish bất biến:
#
# RESTATE_LOOKBACK_DAYS=45 (mặc định 30): cửa sổ chốt của publisher là 25 phiên GIAO DỊCH
#   (~35 ngày lịch, hơn nữa nếu rơi vào Tết), còn guard cắt theo NGÀY LỊCH. Để mặc định 30 ngày
#   lịch (~21 phiên) thì guard soi cả dải 21-25 phiên vốn CHƯA CHỐT và được phép tính lại hợp lệ
#   mỗi đêm ⇒ alert dương-tính-giả đều đặn. 45 ngày lịch (>=26 phiên kể cả tuần Tết) nằm trọn
#   trong vùng đã chốt.
# RESTATE_ALERT_THRESHOLD=0 (mặc định 5): ngưỡng 5 được đặt cho THỜI `bq load --replace`, khi
#   churn nền 0-4 phiên/đêm là chuyện thường ngày. Với publish bất biến, kỳ vọng ở vùng đã chốt
#   là ĐÚNG 0 — để nguyên 5 thì một bug tương lai ghi đè 1-5 phiên đã chốt sẽ bị guard LÀM NGƠ,
#   tức lưới an toàn có lỗ rộng 5 phiên đúng ở chỗ nó phải bắt. Guard so `n_total <= THRESH` nên
#   0 = alert khi có BẤT KỲ phiên đã chốt nào đổi/thêm/mất.
# ⇒ Guard trở lại đúng vai trò: dây bẫy chỉ kêu khi có BUG ghi đè phần đã chốt.
step "[11b] restate guard: vnindex_5state vs archive_predeploy_$TS"
RESTATE_LOOKBACK_DAYS=45 RESTATE_ALERT_THRESHOLD=0 \
./restate_guard.sh "$PJ.tav2_bq.vnindex_5state" \
                   "$PJ.tav2_bq.vnindex_5state_archive_predeploy_$TS" \
                   "vnindex_5state (base v3.4b)"
case $? in 0) : ;; 2) echo "  restate ALERT đã gửi (base)" ;; *) echo "  WARN: restate guard (base) không chạy được" ;; esac

# --- 4. republish DT5G live ---
# publish_gated_state.py giờ exit!=0 khi publish BQ hỏng (trước đây chỉ in WARNING rồi exit 0
# ⇒ thất bại lặng lẽ). KHÔNG `die`: cần step [14] macro_healthcheck vẫn chạy — health report
# đứng im sẽ khiến get_gated_state fail-closed về DT4, tức BỎ macro cap (kém phòng thủ hơn).
# Bảng giữ nguyên bản hôm qua ⇒ bq_freshness_check chặn hạ nguồn đúng như thiết kế.
step "[12] publish_gated_state.py -> dt5g_live (bất biến)"
if ! $PY deploy_golive_dt5g_v4/publish_gated_state.py; then
  PMSG="🛑 daily_refresh_v34b $(TZ='Asia/Ho_Chi_Minh' date '+%Y-%m-%d %H:%M ICT'): publish_gated_state THẤT BẠI — vnindex_5state_dt5g_live GIỮ NGUYÊN bản hôm qua. Hạ nguồn sẽ bị bq_freshness_check chặn. Xem $LOG."
  echo "  !!! publish_gated_state FAILED (chain vẫn tiếp tục để macro_healthcheck chạy)"
  /home/trido/thanhdt/WorkingClaude/mike/bin/notify.sh "$PMSG" 2>/dev/null || true
  /home/trido/thanhdt/WorkingClaude/mike/bin/notify_thread.sh "$PMSG" "1521470705563340910" 2>/dev/null || true
fi

step "[12b] restate guard: dt5g_live vs archive_predeploy_$TS"
# Cùng override như [11b] — dt5g_live cũng publish bất biến (seal_n=25 phiên giao dịch), nên để
# mặc định 30 ngày/ngưỡng 5 sẽ vừa báo dương-tính-giả ở đuôi chưa chốt, vừa bỏ qua bug ghi đè
# <=5 phiên đã chốt. Xem giải thích đầy đủ ở [11b].
RESTATE_LOOKBACK_DAYS=45 RESTATE_ALERT_THRESHOLD=0 \
./restate_guard.sh "$PJ.tav2_bq.vnindex_5state_dt5g_live" \
                   "$PJ.tav2_bq.vnindex_5state_dt5g_live_archive_predeploy_$TS" \
                   "vnindex_5state_dt5g_live (PRODUCTION)"
case $? in 0) : ;; 2) echo "  restate ALERT đã gửi (dt5g_live)" ;; *) echo "  WARN: restate guard (dt5g_live) không chạy được" ;; esac

# --- 5. verify ---
step "[13] verify freshness (base should match local CSV max=$LOCAL_MAX)"
BASE_MAX="$(bq query --use_legacy_sql=false --format=csv --project_id="$PJ" \
  'SELECT MAX(time) FROM tav2_bq.vnindex_5state_tam_quan_v34b_clean' 2>/dev/null | tail -1)"
LIVE_MAX="$(bq query --use_legacy_sql=false --format=csv --project_id="$PJ" \
  'SELECT MAX(time) FROM tav2_bq.vnindex_5state_dt5g_live' 2>/dev/null | tail -1)"
echo "  _v34b_clean max=$BASE_MAX   dt5g_live max=$LIVE_MAX   (local=$LOCAL_MAX)"
[ "$BASE_MAX" = "$LOCAL_MAX" ] || echo "  WARN: base BQ ($BASE_MAX) != local ($LOCAL_MAX)"

# --- 6. update macro_health ---
step "[14] macro_healthcheck.py (update macro_health.json)"
$PY macro_healthcheck.py || echo "  WARN: macro_healthcheck failed (non-fatal)"

# --- 7. local BQ snapshot (cache for Taylor experiments) ---
step "[15] Building local BQ snapshot..."
cd "$WORKDIR_8L" && $PY scripts/build_snapshot.py >> data/daily_refresh.log 2>&1 \
  && echo "  snapshot OK" || echo "  WARN: build_snapshot failed (non-fatal)"

# rolling 30-day log cleanup
find data -name 'refresh_v34b_linux_*.log' -mtime +30 -delete 2>/dev/null

echo; echo "==================================================================="
echo "v3.4b/DT5G Linux refresh DONE $(date)  base=$BASE_MAX live=$LIVE_MAX"
echo "==================================================================="
