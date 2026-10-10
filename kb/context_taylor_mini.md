# Mike fleet — context_taylor_mini (v3778)
> Auto-generated RECENT block; static canonical facts maintained manually (weekly audit-lens catches drift).
> Dùng `bin/kb_recall.sh "keywords"` để lấy section đầy đủ khi cần chi tiết về ops/CAPIT/project.
> Source đầy đủ: `kb/context_pack.md`.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-10-10T17:34:14] Taylor/finding — fund-unit-ledger bước 1/4: nhánh feat/fund-unit-ledger-20261011 @feaa33b5 — sổ đơn vị quỹ + tỉ suất kỳ qua giá đơn vị, eod mặc định, lãi/lỗ VND + IRR, chặn quy năm <365 ngày; control 3.900 giá trị 0 lệch (SpaceX −1,33/1,024/0,519), 65/65 mutant chết bằng assertion; CHƯA merge, chưa chốt sổ thật: {"context": "answer cho dispatch job Taylor_20261010_170004 — BƯỚC 1/4 chính sách 'tài khoản = quỹ mở'. CHƯA merge, KHÔNG gửi báo cáo, KHÔNG sửa template, KHÔNG …
- [2026-10-10T17:36:00] Wags/finding — retro-2026-10-10-xacminh-doclap: {"verdict": "GAPS FOUND (minor, khong doi ket luan)", "scope": "xac minh doc lap ban nhap retro_draft_2026-10-10.md theo yeu cau user 2026-07-11", "checks": {"b …
- [2026-10-10T17:39:10] Mike/finding — daily-retro-finalized-2026-10-10: {"summary": "Retro 2026-10-10 hoàn tất 3/3 bước: entry kb/incidents/retro/retro-2026-10-10.md (commit 3b1cbe16), index.md cập nhật. 2 sự cố: disk-full-root tự h …
- [2026-10-10T19:35:30] Taylor/finding — fund-unit-ledger VÒNG 2: nhánh feat/fund-unit-ledger-20261011 @75060709 (2 commit: 5dce11e3 sửa review K1 K2 N1-N10, 75060709 N11) — luật gán dòng tiền tự suy từ ngày+giờ, không chốt sổ thật trước bước 3, mọi % dòng NAV ngày qua giá đơn vị; nghiệm thu SpaceX −1,33/1,024/0,519 ZaloPay −4,907/−1,162/−2,01, 3.900 giá trị 0 lệch; mutant reviewer 105 chết-assertion/0 sống/0 sập/31 viết lại, 97+43 mutant mới chết hết; CHƯA merge: {"context": "answer cho dispatch job Taylor_20261010_182122 (attempt 2/2 — hoàn tất phần còn dở của attempt 1: commit N11, chạy lại mutant trên code cuối, sandb …
- [2026-10-10T19:35:48] Taylor/finding — fund-unit-ledger VÒNG 2 — ĐÍNH CHÍNH 1 dòng của finding trước (U69): {"context": "đính chính finding job Taylor_20261010_182122 vừa ghi", "sai": "payload ghi U69 (bỏ fsync) là không thử được / không test được", "dung": "U69 nằm t …
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
PC1, VVS, KSF, NKG, HSG, HVN, VJC, NVL, GEG, SBA, DMC/IMP/TRA, TOS, VTP, BAF.

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
