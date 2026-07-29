#!/usr/bin/env bash
# papertrade_daily.sh  — Linux port of papertrade_daily.bat
# Daily EOD: refresh feeds -> 4 sims + V2.3/V4 prod -> dashboards/alerts.
# DT5G publish + recommends đã CHUYỂN sang bq_freshness_check.sh (17:30 ICT).
# Continue-on-error per step (one bad step must not kill the rest), each step logged.
# Schedule via cron ~15:30 ICT trading days.
#
# NOTE: the Windows [0a2] rebuild_state_from_ticker.bat step is omitted — the
# v3.4b base + local state CSVs are refreshed nightly by daily_refresh_v34b_linux.sh.
set -uo pipefail
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
export STATE_WORKDIR="$WORKDIR_8L"
PY="$DNA_PYEXE"; cd "$WORKDIR_8L"
LOG="data/papertrade_run_$(date +%Y-%m-%d).log"
exec >>"$LOG" 2>&1
echo "===== papertrade_daily (linux) START $(TZ='Asia/Ho_Chi_Minh' date +'%Y-%m-%d %H:%M ICT') acct=$(gcloud config get-value account 2>/dev/null) ====="

# FAIL vẫn continue-on-error (by design — 1 step hỏng không giết cả chain), NHƯNG đếm +
# alert cuối chain: trước 2026-07-11 [FAIL] chỉ nằm trong log không ai biết (audit
# Winston_20260711_031745 #4 — nếu custom30_history/[6b] chết thì PARK basket production
# đóng băng im lặng đúng kiểu bug custom30v_8l 06-18→07-11).
FAILS=0; FAILED_STEPS=""
run() {  # run() "<label>" <script> [args...]   -- never aborts the pipeline
  echo; echo "--- $1 ---"
  local lbl="$1"; shift
  if $PY "$@"; then echo "  [ok] $*"; else echo "  [FAIL exit $?] $*"; FAILS=$((FAILS+1)); FAILED_STEPS="$FAILED_STEPS $lbl"; fi
}

# Gọi cuối chain: >0 step FAIL → alert Telegram + Discord Trading Daily. Không đổi
# continue-on-error, không làm chain exit≠0 — chỉ đảm bảo KHÔNG còn fail im lặng.
notify_fails() {
  local chain="$1"
  [ "$FAILS" -eq 0 ] && return 0
  local msg="⚠️ $chain $(date +%F): $FAILS step FAIL:$FAILED_STEPS — chi tiết: grep '\[FAIL' $WORKDIR_8L/$LOG"
  # NOTIFY_BIN/NOTIFY_THREAD_BIN override được qua env — CHỈ dùng cho selfcheck (test hàm
  # thật với stub, không gửi alert thật); production để trống = đường dẫn thật.
  "${NOTIFY_BIN:-/home/trido/thanhdt/WorkingClaude/mike/bin/notify.sh}" "$msg" 2>/dev/null || true
  "${NOTIFY_THREAD_BIN:-/home/trido/thanhdt/WorkingClaude/mike/bin/notify_thread.sh}" "$msg" "1521470705563340910" 2>/dev/null || true
}

# --- feeds + state ---
run "[1] pull_us_market"        pull_us_market.py
run "[2] refresh_lagged_caches" refresh_lagged_caches.py
run "[3] snapshot_state_vintage" snapshot_state_vintage.py
run "[4] macro_healthcheck"     macro_healthcheck.py
run "[6] custom30_history"      custom30_history.py
# [6b] custom30V (yieldcombo) -> tav2_bq.custom30v_8l — the V2.4 PRODUCTION parking basket
# (golive_recommend_v23.py reads this table; [6] custom30_8l = legacy blend, kept for audits).
# Writer was orphaned 2026-06-18..2026-07-11 (shadow publish dropped after the 06-30 cutover);
# revived 2026-07-11 (job Taylor_20260711_035824) — without it the table goes stale at the
# next quarterly rebalance (~2026-08-05).
echo; echo "--- [6b] custom30v_history (yieldcombo -> custom30v_8l) ---"
if BASKET_SELECT=yieldcombo \
   CUSTOM30_TABLE=lithe-record-440915-m9:tav2_bq.custom30v_8l \
   CUSTOM30_CSV=custom30v_8l_publish.csv \
   $PY custom30_history.py; then
  echo "  [ok] custom30v_history"
else
  echo "  [FAIL exit $?] custom30v_history"; FAILS=$((FAILS+1)); FAILED_STEPS="$FAILED_STEPS [6b]"
fi
# --- sims + production books ---
run "[7] pt_v11_tq34b"          pt_v11_tq34b.py
run "[8] pt_v12_macro"          pt_v12_macro.py
# [9] pt_v121_ensemble / [10] pt_v121_ens_q2 REMOVED 2026-06-16 — ensemble edge is a
# reduced-harness artifact (faithful audit 16.85% < V11/V2.3); dropped from daily comparison.
run "[11] pt_v4_dt5g"           pt_v4_dt5g.py
run "[12] pt_v22_dt5g (V2.3)"   pt_v22_dt5g.py
run "[14] papertrade_compare"   papertrade_compare.py
# --- sleeves / shadows / alerts ---
# [15][16] RETIRED 2026-07-07 (job Taylor_20260707_132048) — paper window ĐÃ KẾT THÚC
# 2026-06-30 (ENDDATE trong script); Telegram section đã gỡ 2026-06-26. Script/data giữ
# nguyên cho audit — bỏ comment để chạy lại.
#run "[15] vol_spike_hedge_pt"   vol_spike_hedge_pt.py
#run "[16] f_sleeve_pt"          f_sleeve_pt.py
run "[17] orb_pt"               orb_pt.py
# [18] RETIRED 2026-07-07 (Taylor_20260707_132048) — câu hỏi A/B "foundation nào go-live"
# đã QUYẾT 2026-05-29 (DT5G live từ 06-02); không còn quyết định nào đọc report này.
#run "[18] pt_dt4_vs_tq34b_ab"   pt_dt4_vs_tq34b_ab.py
# [19] crisis_alert_push CHUYỂN sang mike/bin/paper_late_feeds.sh (20:05 ICT) — 2026-07-29,
# job Winston_20260729_103816. Nó tự query BQ LIVE (ticker_prune JOIN dt5g_live), không đọc
# artifact của step nào khác → ở 15:30 asof luôn = T-1 (ingest tav2 xong ~17:2x, publish DT5G
# 19:0x); chạy 20:05 thì asof = T. Không step nào trong chain này đọc output của nó (nó chỉ
# push Telegram) → gỡ ra không phá thứ tự.
#run "[19] crisis_alert_push"    crisis_alert_push.py
run "[20] pt_capitulation_shadow" pt_capitulation_shadow.py
# [21] GIỮ ở đây (dù đọc web live) vì script chỉ lấy ngày MỚI NHẤT trên trang: bỏ 1 phiên =
# mất ngày đó vĩnh viễn. paper_late_feeds.sh 20:05 chạy LẠI cùng script để bắt được ngày T khi
# Baltic đã công bố (~19:00-20:00 ICT); dedup theo date nên 2 lần/ngày là idempotent.
run "[21] fetch_bdi_daily"      fetch_bdi_daily.py
run "[22] edge_health_monitor"  edge_health_monitor.py --refresh
# [23][24][25] RETIRED 2026-07-07 (Taylor_20260707_132048) — arc V6 "Tứ Trụ"/AMH không
# nằm trên roadmap production (V2.4→V2.5); amh_cockpit mất kênh gửi từ cleanup Telegram
# 2026-06-26; pt_sleeve_allocator đọc V5 (V121_Kelly) trong compare5 vốn đã ngừng cập nhật
# từ 2026-06-16 → input frozen. ecology_dashboard chạy lại ad-hoc khi cần macro-view.
# Scripts/data giữ nguyên — bỏ comment để chạy lại.
#run "[23] ecology_dashboard"    ecology_dashboard.py --refresh
#run "[24] amh_cockpit"          amh_cockpit.py
#run "[25] pt_sleeve_allocator"  pt_sleeve_allocator.py
# --- weekly: phosphorus (Friday only; ICT Friday = dow 5) ---
if [ "$(date +%u)" = "5" ]; then
  run "[26] phosphorus_dgc_weekly (Fri)" phosphorus_dgc_weekly.py
else
  echo; echo "--- [26] phosphorus_dgc_weekly skipped (not Friday) ---"
fi

notify_fails "papertrade_daily"

# rolling 30-day log cleanup
find data -name 'papertrade_run_*.log' -mtime +30 -delete 2>/dev/null
echo; echo "===== papertrade_daily (linux) DONE $(TZ='Asia/Ho_Chi_Minh' date +'%Y-%m-%d %H:%M ICT') — FAILS=$FAILS ====="
