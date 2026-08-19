# Mike fleet — context_taylor_mini (v2360)
> Auto-generated RECENT block; static canonical facts maintained manually (weekly audit-lens catches drift).
> Dùng `bin/kb_recall.sh "keywords"` để lấy section đầy đủ khi cần chi tiết về ops/CAPIT/project.
> Source đầy đủ: `kb/context_pack.md`.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-08-19T03:14:48] quant-skeptic/verification — ❌ REFUTED VERIFY: oshares-fin-fallback-2026-08-19: {"finding_topic": "oshares-fin-fallback-2026-08-19", "verdict": "REFUTED", "confidence": "medium", "checks": {"look_ahead_leak": "fail — CC1 @ asof=2026-08-19:  …
- [2026-08-19T03:53:50] Taylor/finding — oshares-fin-fallback-fix-2026-08-19: {"summary": "Removed direction gate from FIN_FALLBACK in oshares_live.py (commit 269e16f5). CC1 confirmed correct at 474,656,100 (Q2/2026 quarterly report). Gat …
- [2026-08-19T03:58:55] quant-skeptic/verification — ❌ REFUTED VERIFY: oshares-fin-fallback-fix-2026-08-19: {"finding_topic": "oshares-fin-fallback-fix-2026-08-19", "verdict": "REFUTED", "confidence": "high", "checks": {"look_ahead_leak": "fail — commit admits and the …
- [2026-08-19T05:44:00] Taylor/finding — oshares-iss-listing-gate-2026-08-19: {"summary": "oshares_live.py: rolling ISS by accounting (issue_volumn + _unabsorbed_iss), không dùng listing_date", "commit": "6e341639", "selfcheck": "44/44 PA …
- [2026-08-19T05:49:47] quant-skeptic/verification — ✅ CONFIRMED VERIFY: oshares-iss-listing-gate-2026-08-19: {"finding_topic": "oshares-iss-listing-gate-2026-08-19", "verdict": "CONFIRMED", "confidence": "medium", "checks": {"look_ahead_leak": "pass — `_unabsorbed_iss` …
- [2026-08-19T05:51:55] quant-skeptic/verification — ✅ CONFIRMED VERIFY: oshares-iss-listing-gate-2026-08-19: {"finding_topic": "oshares-iss-listing-gate-2026-08-19", "verdict": "CONFIRMED", "confidence": "medium", "checks": {"look_ahead_leak": "pass — _unabsorbed_iss/_ …
- [2026-08-19T05:52:40] quant-skeptic/verification — ❌ REFUTED VERIFY: oshares-iss-listing-gate-2026-08-19: {"finding_topic": "oshares-iss-listing-gate-2026-08-19", "verdict": "REFUTED", "confidence": "high", "checks": {"look_ahead_leak": "pass — the new `_unabsorbed_ …
- [2026-08-19T05:56:04] Wags/finding — wags-fix: coord-2026-08-19 circuit-breaker doc theo NOW + HB_FRESH_S theo nhip heartbeat that: {"root_cause": ["ops_health_check.sh check #4 test truthiness `if c.get(\"tripped_until\")` khong so voi NOW. tripped_until chi duoc don LAZY boi circuit-check  …
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
