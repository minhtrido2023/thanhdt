---
name: daily-report-dt5g-v4-2026
description: Daily 18:00 Telegram report — DT5G regime; [REDACTED]12 recentered on V2.3 picks (golive_recommend_v23), V4 demoted to benchmark control arm; empty-window bq() crash fixed
metadata: 
  node_type: memory
  type: project
  originSessionId: dec0d0c3-c676-436d-a5ed-829764035ee4
---

**UPDATE [REDACTED]12 — report recentered on V2.3 (production), V4 demoted to benchmark:**
- NEW `deploy_golive_dt5g_v4/golive_recommend_v23.py` = LAYER-2 recommender cho V2.3: BAL picks (SIGNAL_V11 + D1 + SV_TIGHT + overheat + **AVOID_exbull** + 8L≥4 half-size in BEAR/CRISIS), LAG/PEAD entries due (T+5, LAG_HI/LO), **allocator w_LAG target-vs-current** (đọc `data/pt_v22_dt5g_logs.csv`, band ±10pp), CAPIT v2 monitor (breadth gate 30% + grind + dd52w/rv10 + golden basket). Outputs `out/golive_v23_recommendations_<DATE>.{md,csv}` + `data/golive_v23_status.json`. Wired vào `papertrade_daily.bat` **[4c2]** (SAU pt_v22_dt5g để allocator đọc NAV mới nhất). Bước [0e] golive V4 cũ RETIRED khỏi daily (script giữ nguyên).
- `telegram_recommend.py`: headline = "V2.3 (DT5G) REPORT"; books = BAL + LAG (đọc golive_v23 CSV + status json); KHÔNG còn early-return full-cash BEAR/CRISIS (V2.3 giữ BAL Fresh-Q + LAG defund qua allocator); thêm block allocator + CAPIT; `build_dt5g_section` giờ headline = V2.3 NAV forward track, V4 12.1 + V11/V12/V121×2 gộp 1 bảng "Benchmark / control arms" (V4 ⭐ = control của OOS showdown).
- **Hand-off production:** `deploy_golive_dt5g_v4/dist/v23_dt5g_recommender.zip` (ZIP3, 8.2MB/14 file, build qua `_build_zips.py`) THAY THẾ `v4_dt5g_recommender.zip` gửi 29/05. Gồm golive_recommend_v23 + golive_daily.bat (đã trỏ v23) + simulate_holistic_nav (bq fix, đè bản ZIP1) + earnings pkl/csv + telegram report mới + recommend_holistic/fundamental_rating_all/rating_8l (report deps). Delta notes = `README_zip3_v23.md`; README.md chính đã update V2.3. ⚠️ ZIP2 (v4) trong dist giờ build lại chứa bat trỏ-v23 → KHÔNG gửi lại ZIP2.
- **BUG FIX quan trọng (pre-existing):** `bq()` trong `simulate_holistic_nav.py` crash EmptyDataError khi query 0 dòng (bq --format=csv không in cả header) → fixed trả DataFrame rỗng. `pt_v4_dt5g.py` CHẾT MỖI NGÀY từ 06-01 vì query Release_Date trong cửa sổ track = 0 dòng giữa mùa BCTC; đồng thời lookback release chỉ TRONG window → days_since_release NaN → SV_TIGHT chặn nhầm mọi buy. Fixed cả `pt_v4_dt5g.py` + `pt_v22_dt5g.py`: lookback `DATE_SUB(START, 120 DAY)` + guard rỗng; thêm explicit columns cho sched_lag rỗng (pt_v4). V4 track rebuild OK: 06-01→06-10, −2.24%, 8 phiên.

Switched the daily 18:00 Telegram desk report to the **DT5G** market-detection engine and added the **V4 12.1** paper-trade track ([REDACTED]01).

**Why:** user asked to (a) fix the report that "stopped working", (b) make DT5G the market-detection system, (c) add V4 12.1 paper-trade from today.

**How it works now:**
- `telegram_recommend.py` headline regime + book gating come from BQ `tav2_bq.vnindex_5state_dt5g_live` (via `get_dt5g_state()`), **not** TQ34b. Falls back to TQ34b SCORE_SQL state only if DT5G query fails. The old TQ34b-vs-DT_10_25_25 comparison section was removed and replaced by `build_dt5g_section` (engine status + source DT5G_macro/DT4_only + transitions + systems list incl. V4 12.1).
- **V4 12.1** = `pt_v4_dt5g.py` (forked from `pt_v121_ensemble.py`): V121_ENS + BASE parking {3:0.7} on DT5G state, fresh 50B from `START_DATE="[REDACTED]01"`. Has an empty-window guard `_seed_empty_track()` that writes a 50B seed row when `END_DATE < START_DATE` (no trading data yet). Outputs `data/pt_v4_dt5g_*`. Wired into `papertrade_daily.bat` [4b] + `papertrade_compare.py` (key `V4_DT5G`, with a <2-session seed guard).
- **DT5G freshness gap fixed:** `golive_daily.bat` (the deploy package's publisher) was never scheduled, so DT5G live BQ was stale. Added `[0d] python deploy_golive_dt5g_v4\publish_gated_state.py` to `papertrade_daily.bat` right after `macro_healthcheck` [0c] (its precondition), so the 15:30 run republishes DT5G before the 18:00 report reads it.

**Root cause of "report not working":** scripts were fine (manual runs OK). The Surface was **asleep on battery** at 15:30/18:00 and **DC "Allow wake timers" was Disabled** (AC was Enable) → Task Scheduler `WakeToRun` couldn't wake it → both `BA-System Telegram Daily 1800` and `PaperTrade3Sys` missed, then advanced to next day. Fixed: `powercfg /SETDCVALUEINDEX SCHEME_CURRENT SUB_SLEEP RTCWAKE 1` (both AC+DC = Enable now).

Related: [[dt5g_walkforward_event_audit]] (DT5G engine), [[v5_prodspec_integrity_audit]] (V4=BASE recommended over V5=KELLY on real ETF).
