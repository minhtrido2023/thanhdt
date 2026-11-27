---
kind: project
owner: Taylor
status: active
updated: 2026-11-27
title: "Kế hoạch Nghiên cứu Chọn Lựa Ứng Cử Viên CAPIT v2 (`CAPIT-Select v2`: Cơ bản × Hành vi Kỹ thuật × Quản trị)"
---
# Kế hoạch Nghiên cứu Chọn Lựa Ứng Cử Viên CAPIT v2 (`CAPIT-Select v2`)

> **Ngày lập:** 2026-11-27 · **Trạng thái:** ĐANG TRIỂN KHAI (`P0 → P1`, user chốt 4 định hướng thiết kế `2026-11-27`) · **Phạm vi:** Nghiên cứu thuần (`RESEARCH-ONLY`), tuyệt đối không sửa code production/bot/registry khi chưa qua kiểm toán `quant-skeptic` và user duyệt.
> **Hồ sơ liên quan:** [`capitulation_shadow.md`](../paper_programs_charter/capitulation_shadow.md) · [`dri-technical-timing-research-plan-20261127.md`](dri-technical-timing-research-plan-20261127.md) · [`capit-margin-hold-20261013.md`](capit-margin-hold-20261013.md) · [`capit_dividend_gate_framework.md`](../../agents/Taylor/capit_dividend_gate_framework.md) · [`exp_capitdcf/RESULT_RANKPRIMARY.md`](../../agents/Taylor/exp_capitdcf/RESULT_RANKPRIMARY.md) · [`exp_capitgate/RESULT.md`](../../agents/Taylor/exp_capitgate/RESULT.md) · [`exp_capitexit/RESULT.md`](../../agents/Taylor/exp_capitexit/RESULT.md) · [`exp_capittrig/RESULT.md`](../../agents/Taylor/exp_capittrig/RESULT.md) · [`capit_flag_blacklist_20261127/REPORT.md`](../../agents/Mike/capit_flag_blacklist_20261127/REPORT.md)

---

## 0. Quyết định Thiết kế đã Chốt (User duyệt `2026-11-27`)

1. **Mở rộng phạm vi ngành để thử nghiệm:** Mở toàn bộ các nhóm ngành đủ chuẩn chất lượng (`BANK`, `CYCLICAL`, `COMPOUNDER`, `POWER`, `INSURANCE`, `REALESTATE`; `SECURITIES` được kiểm soát tự nhiên qua `QUALITY_OK` / `CF_OA_3Y > 0`) kèm **trần tập trung ngành cứng** (`max ≤ 3` mã mỗi nhóm ngành ICB xác định).
2. **Kích thước rổ mục tiêu:** **`K = 6–8` mã** (mốc chính `K = 8`, kiểm định độ nhạy `K = 6` và `K = 10` trong `PREREG`), tăng đa dạng hoá và mở rộng dung lượng cho cả quy mô hiện tại (`~1,5 tỷ`) lẫn tương lai (`10–50 tỷ`).
3. **Mục tiêu ưu tiên (A) — Xác suất thắng & Kiểm soát đuôi trái hơn CAGR thô:** Do cỡ mẫu sự kiện CAPIT lịch sử nhỏ (`19` cụm `2014–2026`), ưu tiên **tỷ lệ thắng cấp đợt và cấp vị thế (`> 0` và `> tiền gửi`)**, **tỷ lệ đợt vượt `C0`**, **chặt đuôi trái (`P(ret60 ≤ −15%)`, `P(≤ −20%)`, `P5`, `intra_mdd60`, `worst-event`)**, và **Sharpe/Calmar**, trong khi vẫn giữ **non-inferiority về CAGR**.
4. **Cơ chế Tầng 3 Tác nghiệp Live:** Lúc `19:00` ngày CAPIT fire, xuất **Top-K Khuyến nghị + Top-5 Băng ghế Dự bị (Reserve Bench)** kèm bảng chẩn đoán 4 trụ (*Cơ bản/Định giá · Hành vi Kỹ thuật · DD Price Zone/Hàng hoá · Cờ Quản trị/Bất thường*) để user duyệt/hoán đổi trước `11:00` phiên sau mà không làm co rổ hay vỡ sizing.

---

## 1. Chẩn đoán Hiện trạng CAPIT & Dữ liệu Nền Đã Đo

### Phần tốt cần giữ nguyên
- **Trigger mua vào (`golive_recommend_v23.py`):** `D_RSI < 0,3` trên Top-250 thanh khoản `universe_pit_q` đạt `≥ 31%` (`br_pit >= 0,31`) là bước nhảy đuôi sâu ổn định (`+8%/60` phiên, win `83%`, `first-touch` tốt hơn chờ xác nhận; [`exp_capittrig/RESULT.md`](../../agents/Taylor/exp_capittrig/RESULT.md)).
- **Thời gian giữ `60` phiên cố định & trần `%ADV` (`10% × ADV20_pre × 2 phiên`):** 6/6 quy tắc thoát sớm đều mất sóng hồi (`−6,4 → −9,0pp`); giữ nguyên cap thanh khoản [`exp_capitadvcap/REPORT.md`](../../agents/Taylor/exp_capitadvcap/REPORT.md).

### 5 điểm nghẽn của khâu chọn candidate hiện hành (`C0`: `ticker_prune` golden + `pb_z < −1`)
Đo mô tả trên toàn bộ **19 cụm CAPIT PIT (`2014–2026`)** (chưa đụng lợi suất):
1. **Pool siêu mỏng → Zero Selection Slack:** `ticker_prune` (bảng `TRAP`) + 3 ngưỡng cứng `ROE_Min5Y ≥ 12% ∧ ROIC5Y ≥ 10% ∧ FSCORE ≥ 6 ∧ TV_1d ≥ 2B` chỉ cho trung vị **11 mã thô** và **5 mã được chọn** (trần `15` mã ràng buộc `0/19` đợt). Do `ROIC5Y = 0` trong BQ với ngân hàng, `100% BANK` bị loại (mất trung vị **16 ngân hàng `rating_8l ≤ 3`** mỗi đợt), đồng thời loại nhầm đầu ngành chu kỳ (`HPG`, `DCM`) và compounder (`SCS`, `HAH`). Ngược lại, `universe_pit_q` (`QUALITY_OK` ∧ `ADV3M ≥ 2B`) có trung vị **107 mã** (`rating ≤ 2`: **58,5 mã**; `D_RSI < 0,35 ∧ pb_z < 0`: **42,5 mã** — rộng gấp **~8,5×**).
2. **Đứt gãy giữa `pb_z` và trạng thái quá bán:** Trung vị chỉ **3/5 mã** rổ `C0` thực sự có `D_RSI < 0,35` (`2022-11-04`: `0/5`). Trong pool chất lượng, `pb_z` đơn lẻ có `IC ≈ 0 (−0,008)`, trong khi **`1/PE` (`ey`)** là nhân tố trội ở VN (`IC = +0,125, t = 11,0`) và `pb_z` phát huy tốt nhất ở vai trò trực giao kèm `1/PE` (`marginal IC +0,050`, [`results_registry.md`](../../../data/results_registry.md)).
3. **Mù cấu trúc Kỹ thuật & Hành vi NĐT:** Chưa tách bán tháo hệ thống vs sập đặc thù doanh nghiệp (`idio_20d`, case `PNJ`), chưa lọc xả vol lớn chưa cạn cung (`vol_r5`, case `SIP`), chưa xét vùng kẹp hàng `VAP3M` và lọc bằng `TV 1 ngày` thay vì `ADV20_pre` (lỗ hổng `HVT`/`NCT`).
4. **Chưa nối kho tri thức & vệ sinh quản trị:** Chưa tích hợp cứng `BANNED`, `forensic_flags`, pha loãng `dil_pit`/`lam_cs`, `dd_price_zones.json`, và xu hướng hàng hoá (`TSR20`, `Brent`, `urea`, `BDI`...) cho nhóm chu kỳ.
5. **Giòn cơ học khi loại cờ:** Loại 1–2 mã cờ dễ kéo rổ dưới `3` mã làm huỷ cả đợt hoặc co deploy (`−1,77pp` CAGR cơ học, [`capit_flag_gate_20261103/REPORT_exp_.md`](../../agents/Taylor/research/capit_flag_gate_20261103/REPORT_exp_.md)).

---

## 2. Bản đồ Dữ liệu & Kỷ luật PIT (`data_registry` Compliant)

- **Nguồn PIT (`2014–2026`) cho P0–P2:**
  - `data/bq_cache/ticker/*.parquet` (giá điều chỉnh `Open/High/Low/Close`, giá thô `Price`, `Volume`, `ICB_Code` PIT, `D_RSI`, `MA50`, `MA200`, `VAP3M`, `Volume_3M_P50`, `PB`, `PE`, `EVEB`, `PB_MA5Y/PB_SD5Y`, `ROE*`, `ROIC*`, `FSCORE`, `Dividend_Min3Y`, `Debt_Eq_P0`).
  - `data/bq_cache/universe_pit_q/*.parquet` (`in_universe`, `quality_flag`, `banned`, `pass_golden_floor`, `rating_8l`), `data/bq_cache/fa_ratings_8l.parquet` *(lưu ý: `route` không có vintage trước `2026` — mọi phân ngành lịch sử dùng `ICB_Code` từ `ticker`)*.
  - `data/bq_cache/ticker_financial.parquet` (strict `Release_Date <= signal_date`, fallback `90/120d` nếu null — tính `FSCORE_P1`, `NP_P0..P5` cho `ΔNP_R`), `mike/data/fiinprox_oshares_pit_20260926.csv` (strict `date <= signal_date` cho pha loãng `dil_3y_pit`), `data/forensic_flags.csv` (strict `date <= signal_date`), `data/bq_cache/risk_rating.parquet`, `data/bq_cache/vnindex_5state_dt5g_live.parquet`, `deposit_rate_vn.py` / `data/deposit_rate_vn_events.csv`, và chuỗi hàng hoá cục bộ với trễ công bố (`brent_monthly.csv`, `rubber_monthly.csv`, `urea_monthly.csv`, `sugar_monthly.csv`, `bdi_daily_real.csv`, `hog_price_vn.csv`, `rubber_tsr20_te_daily.csv`).
- **Nguồn Live-only cho Tầng 3 (`2026-11-26` mockup, KHÔNG backtest ngược):** `mike/kb/dd_price_zones.json`, `mike/kb/thesis_cards.json`, `data/{anomaly_flags.json, anomaly_clearances.json, capit_user_exclusions.json, insider_flags.json, moat_tags.csv, margin_cycle_detector.csv}`.
- **Cấm tuyệt đối:** `profit_*`, `PC1W..PC2M`, `O1W..O2Y`, `Open_1D`, `Pattern_*_3Y`, `VNINDEX` / `VNINDEX_PE` (cột mirror trên dòng cổ phiếu), `OShares` restate cho chuỗi lịch sử.
- **Lệnh cấm vận OOS (`2021–2026`):** Trong P0–P1 chỉ dựng nhãn đến hết `2020-12-31` (`exit_date <= 2020-12-31`). Tuyệt đối không tính hay nhìn lợi suất OOS cho tới khi `PREREG_P2.md` được user duyệt và khoá MD5.

---

## 3. Kiến trúc Phễu 4 Tầng `CAPIT-Select v2`

- **Tầng 0 (Mở vũ trụ sạch & Thanh khoản nhân quả):** `universe_pit_q` (`in_universe ∧ quality_flag == 'QUALITY_OK'`) + `ADV20_pre ≥ 2 tỷ` (trên `Price × Volume` thô `[t-20..t-1]`) ∧ `ADV3M ≥ 2 tỷ`.
- **Tầng 1 (Chặn bẫy Quản trị × Dao rơi Hành vi):** Loại `BANNED` / `forensic_flags` / pha loãng `dil_3y_pit` cực đoan; lọc "dao rơi đặc thù" (`idio20` / `pit_crash_flag_20d` / xả vol lớn chưa cạn `vol_r5`).
- **Tầng 2 (Xếp hạng Đa trục + Trần ngành & Sizing):** Chỉ xét mã có áp lực bán (`D_RSI < 0,35` hoặc `dd60 ≤ −10%`), xếp hạng kết hợp:
  - **F-Val:** `1/PE` chuẩn hoá theo `sector_group` + `−pb_z`;
  - **F-Qual:** `FSCORE` + `ΔNP_R` + `Dividend_Min3Y > 0` (đã có độ dư để thu hoạch);
  - **T-Behav:** `dist_VAP3M` (tránh treo cung sâu), `vol_r5` (tránh xả tháo), `ATR20%` (kiểm soát biến động & thử nghiệm `1/ATR20%` sizing), cộng **trần ngành ≤ 3 mã / `sector_group`** với **`K = 8`** (nhạy `K = 6, 10`) + **Reserve Bench (Top-5)**.
- **Tầng 3 (Live Operational Overlay):** Bảng 4 trụ + cơ chế thay thế 1-click từ Reserve Bench khi có cờ đỏ / user loại tay.

---

## 4. Lộ trình Kiểm định 4 Pha (`P0 → P3`)

- **P0 — Panel PIT & Audit (`p0_build_panel.py`):** Dựng Stress Panel (`br_pit ≥ 0,15`, 40 cụm) + tập nhãn **IS-only (`exit_date ≤ 2020-12-31`)**; kiểm tra tỷ lệ `Open/Close/Price` tại ngày GDKHQ; kiểm đối khớp `C0` ngày `2026-11-26`.
- **P1 — Giải phẫu IS `2014–2020` (`p1_is_anatomy.py`):** Đo IC đơn nhân tố, kiểm định `Dividend_Min3Y` & các biến hành vi trên IS Stress Panel, chạy thang Ablation `C0..C7`, dựng Mockup `2026-11-26`, chạy `selfcheck_p0_p1.py` + 3-TZ determinism, và xuất `REPORT_P0_P1.md` + `PREREG_P2_DRAFT.md` trình user duyệt.
- **P2 — Kiểm định OOS Hai Tầng (`2021–2026`, Zero-Retune sau khoá MD5):**
  - *Tầng A:* OOS Stress Panel (`br_pit ≥ 0,15` & nhạy `0,20`) với episode-cluster bootstrap CI95, DSR, PBO (CSCV), BH-FDR, LOO theo năm, ma sát `1,10%` và stress `1,80%`.
  - *Tầng B:* Chuyển giao 0-tinh-chỉnh sang bản sao cô lập `pt_v23_audit_2014.py` (19 cụm CAPIT thật, `threads=1`, self-check `0 VND`) tại `1,5B / 10B / 50B`.
- **P3 — Phản biện `quant-skeptic` (8 đòn) & Triển khai Có kiểm soát:** Bắt buộc `CONFIRMED` trước khi đề xuất wire vào `golive_recommend_v23.py` (kèm rollback 1 dòng và cổng chỉ cutover khi không có đợt CAPIT đang mở).
