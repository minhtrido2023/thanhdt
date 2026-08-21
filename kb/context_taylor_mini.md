# Mike fleet — context_taylor_mini (v2431)
> Auto-generated RECENT block; static canonical facts maintained manually (weekly audit-lens catches drift).
> Dùng `bin/kb_recall.sh "keywords"` để lấy section đầy đủ khi cần chi tiết về ops/CAPIT/project.
> Source đầy đủ: `kb/context_pack.md`.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-08-20T21:54:22] Wags/answer — selfcheck-red: mike/bin/corp_action_daily_selfcheck.py — recovered 2026-08-20: {"context": "selfcheck_baseline_diff tự đóng: ca đỏ này đã XANH trở lại", "file": "mike/bin/corp_action_daily_selfcheck.py", "artifact": "chạy lại lúc 2026-08-2 …
- [2026-08-20T21:54:22] Wags/answer — selfcheck-red: mike/bin/nav_cum_dividend_selfcheck.py — recovered 2026-08-20: {"context": "selfcheck_baseline_diff tự đóng: ca đỏ này đã XANH trở lại", "file": "mike/bin/nav_cum_dividend_selfcheck.py", "artifact": "chạy lại lúc 2026-08-20 …
- [2026-08-21T00:32:39] Taylor/finding — corp-action-daily 2026-08-21 OK: {"asof": "2026-08-21", "feed_status": "FRESH", "n_track": 36, "n_held": 29, "exright_today": ["BRC", "D11", "FT1", "HAT", "IPA", "VDT"], "ais_today": ["CTR"], " …
- [2026-08-21T01:24:03] Taylor/finding — fearbuy-weekly-scan: {"n_ma_ra_qua": 29, "n_case_moi": 4, "qualify_list": [], "watchlist_stale": false, "scan_date": "2026-08-21", "window": "2026-08-14..2026-08-20", "universe_anom …
- [2026-08-21T01:23:13] Wags/finding — ping test: {"status": "ok", "note": "ping received, agent responsive"}
- [2026-08-21T01:27:02] Wags/answer — dispatch-rong: {"resolution": "KHONG co viec gi de lam - dispatch rac/go nham, dong cau hoi", "context": "Question goc: Wags 2026-08-20T16:22:54Z, job Wags_20260820_162234, pr …
- [2026-08-21T01:34:27] Winston/finding — ops-autofix-done: ops-health-ZaloPay: {"root_cause": "2 ban ghi bus/_rejected.jsonl (Mike, 2026-08-20T10:41:22Z + 10:41:29Z) chua duoc danh dau xu ly. Noi dung KHONG mat: Mike retry lan 3 luc 10:41: …
- [2026-08-21T01:45:56] Wags/finding — wags-fix: coord-2026-08-21 — guard prompt rong (byte-count + dau vet ben + test tu cach ly): {"root_cause": "3 loi chong len nhau tren guard prompt rong dispatch.sh: (1) F2 arch-reviewer — dem ky tu bang ${#var} phu thuoc LOCALE ke thua (LANG=C tra byte …
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
