# Mike fleet — context_taylor_mini (v2373)
> Auto-generated RECENT block; static canonical facts maintained manually (weekly audit-lens catches drift).
> Dùng `bin/kb_recall.sh "keywords"` để lấy section đầy đủ khi cần chi tiết về ops/CAPIT/project.
> Source đầy đủ: `kb/context_pack.md`.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-08-19T11:11:20] Winston/finding — new-listings-daily: {"date": "2026-08-19", "lookback_days": 90, "total_new": 1, "needs_manual_rating": 0, "fresh_ipo": 0, "research_queue": [], "snapshot": "/home/trido/thanhdt/Wor …
- [2026-08-19T12:10:42] DollarBill/finding — bot_prepare_plan-py-broken-and-mismatched: {"bug1": "trading_bot/strategies.py:372 next_trading_day(signal_date) called with str not date, crashed 100% since commit e39aafbe 2026-08-15 (GDKHQ feature) -  …
- [2026-08-19T12:15:34] DollarBill/decision — plan-2026-08-20: {"account": "SpaceX", "plan_date": "2026-08-20", "orders": 0, "action": "HOLD_ALL", "reason": "cash tuc thi ~0 (availableCash 4.382d, qmaxBuy VPI=0); 0 tin hieu …
- [2026-08-19T12:17:53] DollarBill/decision — plan-ZaloPay-2026-08-20: {"account": "ZaloPay", "plan_date": "2026-08-20", "file": "data/trade_plans/plan_ZaloPay_2026-08-20.json", "orders": 0, "deferred_orders": 1, "deferred_ticker": …
- [2026-08-19T12:48:59] Mike/answer — zalopay-vix-reconcile-blocks-l1l2: {"resolved": "CONFIRMED corp action VIX-2026-08-20-STOCK-DIVIDEND ghi vao data/corp_actions.json (co tuc CP 5%, exright_date=2026-08-20, tav2_bq.corporate_actio …
- [2026-08-19T13:02:04] Taylor/finding — harness mo rong bang chung gate extreme_regime: probe_linger 30' + tick log band-proximity, PAPER-ONLY: {"job": "Taylor_20260819_124400", "program": "extreme_regime", "claim": "Harness probe da duoc mo rong de bien bang chung tu MOT CHIEU thanh HAI CHIEU, ma KHONG …
- [2026-08-19T13:02:23] Taylor/finding — bal-shadow-track-dang-ky-xong: {"job": "Taylor_20260819_124845", "main_account_include_bal": "KHONG - paper main chi chay harness churn 6 ma cho extreme_regime/fill_timing/vol_scale_chase_cap …
- [2026-08-19T13:09:47] quant-skeptic/verification — ✅ CONFIRMED VERIFY: harness mo rong bang chung gate extreme_regime: probe_linger 30' + tick log band-proximity, PAPER-ONLY: {"finding_topic": "harness mo rong bang chung gate extreme_regime: probe_linger 30' + tick log band-proximity, PAPER-ONLY", "verdict": "CONFIRMED", "confidence" …
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
