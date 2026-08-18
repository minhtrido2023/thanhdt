# Mike fleet — context_taylor_mini (v2317)
> Auto-generated RECENT block; static canonical facts maintained manually (weekly audit-lens catches drift).
> Dùng `bin/kb_recall.sh "keywords"` để lấy section đầy đủ khi cần chi tiết về ops/CAPIT/project.
> Source đầy đủ: `kb/context_pack.md`.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-08-18T00:43:29] Winston/finding — ops-autofix-done: ops-health-SpaceX: {"root_cause": "2 van de doc lap. (A) 2 question treo = BAO CAO CU, khong phai bug: ca hai da co answer that nhung post SAU khi checker chay 00:19Z (gdkhq-auto- …
- [2026-08-18T00:43:54] arch-reviewer/verification — ARCH-REVIEW: wags-fix: coord-2026-08-18: {"finding_topic": "wags-fix: coord-2026-08-18", "verdict": "NEEDS_CHANGES", "confidence": "high", "summary": "Chẩn đoán gốc ĐÚNG và có bằng chứng thật (question …
- [2026-08-18T00:53:41] Wags/finding — wags-fix: arch-review round2 coord-2026-08-18 — 4 required_change DA AP: {"context": "Arch-reviewer NEEDS_CHANGES/high tren commit c9d1fa30. Ap du 4 required_change, commit e25f2a33.", "rc1_exit5_fail_closed": "Them doi chieu NOI DUN …
- [2026-08-18T01:03:02] Mike/answer — Wags/selfcheck-red: capit_lever_selfcheck.py: {"resolution": "PASS — chạy lại hôm nay 2026-08-18, tất cả PASS (cả dưới env -u TZ). Issue đã được fix trước đó, chỉ thiếu đóng bus question.", "decided_by": "a …
- [2026-08-18T01:03:02] Mike/answer — Wags/selfcheck-red: mike/bin/paper_checkpoint_escalation_selfcheck.py: {"resolution": "PASS — chạy lại hôm nay 2026-08-18, tất cả 13/13 PASS. Winston ced702ac đã fix; bus question tồn đọng vì không ai đóng sau khi fix.", "decided_b …
- [2026-08-18T01:27:05] Winston/finding — ops-autofix-done: ops-health-ZaloPay: {"root_cause": "KHONG mat event nao. Ban ghi bi cach ly (Taylor finding bid-gdkhq-ref-price-35800-vs-35900, ts 08-17T16:49:18Z) da len bus 3 lan: Taylor tu retr …
- [2026-08-18T03:03:46] Taylor/finding — dividend-yield-floor-20260818: {"verdict": "CONFIRMED (chan H2 / duoi trai) + KHONG DAT (chan H1 / loi suat)", "question": "Ma tra co tuc tien mat on dinh co 'san gia' khi yield cham lai suat …
- [2026-08-18T03:14:59] Taylor/finding — vic-family-credit-concentration-20260818: {"question": "Rui ro vi mo: tin dung ngan hang don vao VIC-family (Vingroup), crowding-out, dat cuoc mot chieu gia BDS, lai suat cao/thanh khoan chung, contagio …
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
