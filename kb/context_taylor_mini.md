# Mike fleet — context_taylor_mini (v2349)
> Auto-generated RECENT block; static canonical facts maintained manually (weekly audit-lens catches drift).
> Dùng `bin/kb_recall.sh "keywords"` để lấy section đầy đủ khi cần chi tiết về ops/CAPIT/project.
> Source đầy đủ: `kb/context_pack.md`.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-08-19T00:48:28] Wags/answer — selfcheck-red: mike/bin/wags_autofix_postq_selfcheck.py: {"status": "FIXED", "root_cause": "commit c9d1fa30 added 4th _post_q call site (wags-autofix-review-needed, dispatch exit=5 branch) at line 266, shifting dispat …
- [2026-08-19T00:48:33] Wags/finding — wags_autofix_postq_selfcheck fix — 4th call site (review-needed): {"summary": "Selfcheck was RED after commit c9d1fa30 added a 4th _post_q call site (wags-autofix-review-needed, dispatch exit=5). Fixed exact-3 -> exact-4 asser …
- [2026-08-19T00:49:38] Wags/answer — selfcheck-red: mike/bin/wags_autofix_postq_selfcheck.py: {"status": "resolved", "note": "Fix da landed truoc trong commit 1e6d19d1 (fix(wags_autofix_postq_selfcheck): track 4th _post_q call site) - da chua ca 4 diem s …
- [2026-08-19T00:49:44] Wags/finding — wags_autofix_postq_selfcheck-already-fixed: {"summary": "Selfcheck da la PASS 29/29 (exit=0) truoc khi dispatch nay chay - fix yeu cau da nam san trong commit 1e6d19d1, khong can sua gi them", "verify_cmd …
- [2026-08-19T01:24:52] Taylor/finding — corp-action-sanity-factor-run-level-regression: {"summary": "Added t_run_level_wiring() (checks R1-R8) to corp_action_daily_selfcheck.py, closing the gap quant-skeptic flagged: all 178 prior magnitude-gate ch …
- [2026-08-19T01:26:08] Wags/answer — context-bloat-same-day: {"resolution": "OKF split MIKE.md 43262B->34673B (<40KB, bien 6,1KB): 4 muc dung-theo-tinh-huong chuyen NGUYEN VAN sang MIKE_ext.md (10879B, KHONG auto-load) +  …
- [2026-08-19T01:27:10] Wags/finding — wags-fix: coord-2026-08-19 — MIKE.md OKF split + Phase 4.6 gate biet kiem ban split: {"job": "Wags_20260819_012007", "cau_hoi_treo": "Mike/context-bloat-same-day (kb_nightly Phase 4.6 phat 2026-08-18T19:19:44Z) — DA DONG bang answer canonical (b …
- [2026-08-19T01:31:19] arch-reviewer/verification — ARCH-REVIEW: wags-fix: coord-2026-08-19 — MIKE.md OKF split + Phase 4.6 gate biet kiem ban split: {"finding_topic": "wags-fix: coord-2026-08-19 — MIKE.md OKF split + Phase 4.6 gate biet kiem ban split", "verdict": "NEEDS_CHANGES", "confidence": "high", "summ …
<!--RECENT-END-->

## Kill-switches
- `data/BOT_STOP`: tạo file = dừng mọi giao dịch tức thì
- `state/NOTIFY_OFF`: tắt Telegram push tạm thời
- V2.5: `trading_rules.json v1.7` → v25_leverage STATUS=DISABLED

## Đang trading (LIVE)
SpaceX (DNSE 0002023347) V2.4 LIVE từ 2026-07-01, có margin, run_bot.sh 09:05 ICT.
ZaloPay (DNSE 0001743768) V2.4 LIVE từ 2026-07-06, CASH-ONLY, DGC excluded (HOSE hạn chế).
→ `kb_recall "trading live capit domain due-diligence"` cho chi tiết sizing/gate/pipeline.

## Dự án đang mở (pointers)
- R&D pipeline (paper-only): `kb/projects/rnd-pipeline-tracker.md`
- universe_pit migration G5-G9: `kb/projects/universe-pit-migration.md`
- LAG ADV filter tracking (mốc cứng 2026-12-15): `kb/projects/lag-adv-filter-tracking.md`
- CASH_VENDOR gate: ĐÓNG đến 2026-09-13, cần user xác nhận khi mở lại

---

## Tri thức chung — CRITICAL (phải nhớ cho MỌI R&D task)

### V2.4 — chiến lược trung tâm
= V2.3A + custom30V parking (NEUTRAL) + gated-overflow (bear-washout) + HAG eq_flag fix.
2 book: **BAL** (momentum SIGNAL_V11, yieldcombo: 1/PE + 1/PCF) + **LAG** (PEAD/earnings drift).
Allocator w_LAG: {CRISIS 50 / BEAR 0 / NEUTRAL-BULL-EXBULL 65}, band ±10pp.
**R3 NEUTRAL-only @50B (universe_pit, pin 2026-08-03): CAGR 28.86% / Sharpe 1.90 / DD −17.8% / Calmar 1.62** (Final NAV 1.178,01B).
Bootstrap 5th-pct: CAGR 18.6%, DD −28.6% (anchor DD ~−29%, KHÔNG phải −18%).
NEUTRAL parking custom30V = phần tin cậy nhất: +7.4pp Full. (30 mã, cap 0.10)
V2.5: lever MGE=1.5, DISABLED — chi tiết `kb/projects/v2.5-leverage-nogo.md`.

### DT5G — bẫy quan trọng
Production: `tav2_bq.vnindex_5state_dt5g_live` qua `get_gated_state()`.
**KHÔNG đọc** `vnindex_5state` — đó là v3.4b BASE (153 transitions ≠ DT5G 49 transitions).

### 8L Rating
Composite v3 LIVE (`rating_8l.py`): value = ey(1/PE) + cfy(1/PCF) + ps(1/PS). Golden floor: ROE_Min3Y≥0 ∧ CF_OA_3Y>0.
1/PE dominant (IC +0.125, 94% hit) — đừng hạ, đừng nhân Price/Close (ĐÃ BỊ BÁC BỎ 2026-08-02).
Rating = binary gate ≤3, KHÔNG phải return-tilt.

### Quy chuẩn backtest (bắt buộc mọi R&D)
1. self-check 0 VND + walk-forward IS(2014-19)/OOS(2020+) + threads=1. Edge rớt OOS = loại.
2. `profit_*` chỉ train, KHÔNG filter live (look-ahead).
3. Pin kết quả: `data/results_registry.md`. Ghi bus ngay.
4. DSR<0.95 → RED FLAG; PBO≥0.5 → chọn config robust-trung vị, không IS-best.
5. **quant-skeptic CONFIRMED = điều kiện cần trước khi wire production.**

### BANNED tickers vĩnh viễn
PC1, VVS, KSF, NKG, HSG, HVN, VJC, NVL, GEG, SBA, DMC/IMP/TRA, TOS, VTP.

### Đã thử, BỊ LOẠI — không đề xuất lại
custom30V permanent-exclude 7 tên; LAG SUE-tilt 3 tầng; hold-neutral exit; stability floor ROE<0;
liq-tilt custom30; deep-discount sleeve; pbcombo dual-vehicle; gq_score growth gate; composite v3 as entry-selector.
MOM_N/MOM_S: ĐÃ GỠ production 2026-07-12 (không phải thử bị loại; `kb/projects/momentum-deals.md`).
V2.5 leverage: NO-GO (IS-artifact; `kb/projects/v2.5-leverage-nogo.md`).

### BQ — bẫy thường gặp
- `ticker*.Trading_Value` = Price × Volume (derived), KHÔNG dùng để tính VWAP.
- BQ query mặc định giới hạn 100 rows — `COUNT(*)` trước aggregate.
- Same-day data: dùng DNSE API, KHÔNG BQ (BQ sync 23:45 ICT).
- `ticker_prune` backfill tới 2000 nhưng VN mỏng trước 2008 (~19-105 mã).

## Nguồn chuẩn tắc đầy đủ
Chi tiết: `kb/KNOWLEDGE.md` (§1-9). Events: `kb/events_buffer.md`. Fleet: `kb/fleet_status.md`.
Dự án: `kb/projects/`. Incidents: `kb/incidents/index.md`.
