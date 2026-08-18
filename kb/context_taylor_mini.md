# Mike fleet — context_taylor_mini (v2337)
> Auto-generated RECENT block; static canonical facts maintained manually (weekly audit-lens catches drift).
> Dùng `bin/kb_recall.sh "keywords"` để lấy section đầy đủ khi cần chi tiết về ops/CAPIT/project.
> Source đầy đủ: `kb/context_pack.md`.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-08-18T12:09:23] DollarBill/decision — plan-2026-08-19: {"account": "SpaceX", "plan_date": "2026-08-19", "orders": 0, "action": "HOLD_ALL", "dt5g_state": "NEUTRAL", "nav_vnd": 958891162, "n_bal": 0, "n_lag_due": 0, " …
- [2026-08-18T12:09:32] DollarBill/finding — plan-SpaceX-2026-08-19-done: Plan SpaceX T+1 (2026-08-19) da sinh xong: HOLD ALL 0 lenh. DT5G NEUTRAL (state=3). load_plan() verify OK. PARK 42.90% active_nav (411.4tr, duoi tran 417.1tr -  …
- [2026-08-18T13:36:31] quant-skeptic/verification — ✅ CONFIRMED VERIFY: ad-hoc claim: {"finding_topic": "ad-hoc claim", "verdict": "CONFIRMED", "confidence": "high", "checks": {"look_ahead_leak": "pass — score computed from `src_q` (prior COMPLET …
- [2026-08-18T13:39:04] Taylor/finding — yield-floor-phase1-wire-20260818: {"status": "NO_WIRE — can user quyet (khong phai NO_EFFECT vi pool>30, ma vi tiebreaker khong bao gio fire)", "artifact": "mike/agents/Taylor/research/yield_flo …
- [2026-08-18T14:12:07] Taylor/finding — yield-floor-phase1-option-C-20260818: {"option": "C — DISPLAY-ONLY observational labels, WIRED", "files": ["custom30_yield_labels.py (moi)", "custom30_history.py", "custom30_yield_labels_selfcheck.p …
- [2026-08-18T14:12:26] Taylor/answer — yield-floor-phase1-wire-20260818: {"context": "Dong cau hoi Phase 1 (finding yield-floor-phase1-wire-20260818: NO-WIRE, can user quyet giua A/B/C).", "decision": "Option C deployed: observationa …
- [2026-08-18T17:33:35] Mike/finding — daily-retro-draft-2026-08-18-buoc1-xong: {"draft_path": "state/retro_draft_2026-08-18.md", "so_su_co": 3, "so_pattern": 2, "tom_tat": "3 su co, ca 3 deu thuoc ho loi coding_guidelines.md #28 (checker/d …
- [2026-08-18T17:35:11] Wags/finding — verify-retro-2026-08-18: CONFIRMED: {"verdict": "CONFIRMED", "checks": ["bus/inbox/*.jsonl sweep 2026-08-18: 32 events (error/finding/question/answer/decision), 0 event_type=error — matches draft  …
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
