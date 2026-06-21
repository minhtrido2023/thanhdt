# RESULTS REGISTRY — nguồn-sự-thật cho mọi con số đã công bố (chống "không tái lập được")

> **VÌ SAO CÓ FILE NÀY:** backtest chạy live-forward → `END_DATE = detect_end_date()` (data mới nhất) DỊCH mỗi ngày,
> và các bảng as-of (`custom30v_8l`, `fa_ratings_8l`) được republish → CÙNG config nhưng KHÁC session ra số khác
> (vd baseline 30.96 → 31.69 sau 5 phiên). Đó là lý do "session trước không tái tạo được kết quả".
> File này KHỬ vấn đề đó: mỗi kết quả công bố được PIN với (a) lệnh chạy ĐẦY ĐỦ, (b) AUDIT_END cố định,
> (c) đường dẫn CSV đông cứng. **ĐỌC FILE NÀY TRƯỚC khi tái chạy/đối chứng — đừng tái dựng config từ trí nhớ.**

## QUY TẮC TÁI LẬP (bắt buộc từ 2026-06-19)
1. **Số "công bố" PHẢI pin `AUDIT_END`** (vd `AUDIT_END=2026-06-19`). Không pin = số sẽ trôi theo data → vô nghĩa để đối chứng.
2. **CSV LÀ ARTIFACT ĐÔNG CỨNG** (ghi ra rồi là bất biến; mỗi dòng TX dò được vs BQ thô). "Đối chứng" = `python extract_peryear.py <csv>` recompute từ CSV (KHÔNG trôi). "Tái lập" = chạy lại lệnh đã pin.
3. **Lưu ý mutation as-of**: kể cả pin AUDIT_END, nếu `custom30v_8l`/`fa_ratings_8l` bị republish sau đó, tái-chạy có thể lệch nhẹ → khi đó **CSV mới là chuẩn**. Muốn đông cứng tuyệt đối: giữ CSV (đã đủ cho đối chứng từng VND).
4. **Mọi số mới đáng nhớ → thêm 1 dòng vào bảng dưới** (label, lệnh, AUDIT_END, CSV, metric, self-check). Đây là việc bắt buộc, không tùy hứng.
5. Self-check 0 VND (BAL+LAG cash-flow identity + final-NAV identity) là điều kiện CẦN để một dòng được ghi.

## MÔI TRƯỜNG
```bash
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh   # set $DNA_PYEXE (wc_venv, pandas 3.x đọc được pickle), bq trên PATH
# Harness: pt_v23_audit_2014.py  (T+1 Open, BQ-thuần, self-check, xuất CSV data/v23_golive_audit_*.csv)
```
**argv:** `v23a <cap> <maturity> <ew2d_shrink> <edge>` — production = `v23a none postbull 0 edge`
(MODE=v23a allocator+capit; cap=none; maturity=postbull-gate; shrink=0=hard-block; edge=edge-conditional LAG allocator).
**env:** `NAV_TOTAL_B` | `ETF_LIQ`(parking vehicle: off=E1VFVN30 / custompitg=custom basket) | `BASKET_WT`(capwt/namecap) |
`BASKET_SELECT`(blend=rổ cũ / yieldcombo=custom30V) | `PARK_STATES`("3:0.7"=NEUTRAL-only / "3:0.7,4:0.7"=+BULL) |
`AUDIT_END`(PIN!) | `AUDIT_START`(default 2014-01-02) | `CAPIT_BEAR_OVERFLOW`(0/1) | `CAPIT_DEPTH_SIZING`(0/1).

## ⭐ CONFIG TỐT NHẤT = **V2.4** (đặt tên 2026-06-20, go-live 2026-06-30)
**V2.4 = V2.3A + custom30V parking + gated-overflow + HAG eq_flag fix** (NEUTRAL-only parking <150B; conditional bull-park dormant opt-in). Tên gọi chính thức cho cấu hình deploy lõi.
Họ config = **V2.3A (argv `v23a none postbull 0 edge`) + custom30V parking (ETF_LIQ=custompitg, BASKET_WT=namecap, BASKET_SELECT=yieldcombo)**. Không config nào khác vượt robust (branch-C 32.95 LOẠI: depth-sizing IS −1.60; value-book/megacap-sleeve/panic-sleeve đều LOẠI).
- **DEPLOY (live <150B) = R3: NEUTRAL-only** — CAGR 28.26%/**Sharpe 1.87**/DD−18.8/Cal1.50 @50B. + gated-overflow ON (insurance +1.17pp OOS, paper-gated 2026-06-30).
- **Bull-park (N0.7+B0.7) = tùy chọn ≥150B** — R2 @50B 29.24%/Cal1.56 nhưng **Sharpe THẤP hơn (1.82)** + lumpy (hại 2024/25). KHÔNG mặc định <150B.
- Capacity: nhỏ NAV cao hơn (R1 @20B 31.69 > R2 @50B 29.24), decay theo vốn.

## BẢNG KẾT QUẢ ĐÃ PIN

### R1 — custom30V N0.7+B0.7 @20B, no-C (= "Baseline (no C)" trong bảng so sánh nhánh C)
- **Lệnh:**
  ```bash
  NAV_TOTAL_B=20 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7,4:0.7" \
  AUDIT_END=2026-06-19 $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge
  ```
- **CSV:** `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-70_4-70_wtnamecap_nav20B.csv`
- **Metric (snapshot 2026-06-19):** CAGR **31.69%** / Sharpe 1.91 / MaxDD −20.1% / Calmar 1.58 | self-check **0 VND** (BAL+LAG)
- **Đối chứng:** `$DNA_PYEXE extract_peryear.py <CSV>` → FULL 31.69% (khớp).
- *Ghi chú:* đây là config NGHIÊN CỨU (bull-park BẬT @20B để vẽ capacity curve), KHÁC config LIVE <150B (NEUTRAL-only). Số cũ 30.96 = snapshot ~2026-06-15 (đã trôi +0.7pp do data dịch — KHÔNG phải lỗi).

### R2 — custom30V N0.7+B0.7 @50B, no-C
- **Lệnh:**
  ```bash
  NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7,4:0.7" \
  AUDIT_END=2026-06-19 $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge
  ```
- **CSV:** `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-70_4-70_wtnamecap.csv` (⚠️ @50B = default → KHÔNG có hậu tố `_nav50B`).
- **Metric (snapshot 2026-06-19):** CAGR **29.24%** / Sharpe 1.82 / MaxDD −18.8% / Calmar 1.56 | self-check **0 VND** (BAL+LAG)
- **Đối chứng:** `$DNA_PYEXE extract_peryear.py <CSV>` → FULL 29.24% (khớp); per-year 2021 +102 / 2022 −5 / 2025 +31.
- *Ghi chú:* @20B 31.69 > @50B 29.24 = decay theo NAV (capacity), khớp curve item 13 (20B 30.96 / 50B 28.77 ở snapshot cũ). Config nghiên cứu (bull-park BẬT); live <150B = NEUTRAL-only.

### R3 — custom30V NEUTRAL-only @50B, no-C  ⭐ = CONFIG LIVE <150B (production deploy)
- **Lệnh:**
  ```bash
  NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" \
  AUDIT_END=2026-06-19 $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge
  ```
- **CSV:** `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap.csv`
- **Metric (snapshot 2026-06-19):** CAGR **28.26%** / Sharpe **1.87** / MaxDD −18.8% / Calmar 1.50 | self-check **0 VND** (BAL+LAG)
- **Đối chứng:** `extract_peryear.py <CSV>` → FULL 28.26% (khớp); IS 27.84 / OOS 28.62; 2021 +90 / 2022 −5 / 2025 +36.
- *So R2:* NEUTRAL-only Sharpe 1.87 > bull-park 1.82, CAGR 28.26 < 29.24 → bull-park đổi +1pp CAGR lấy −0.05 Sharpe + lag 2024/25. Live <150B chọn R3.

### R5 — conditional bull-park @50B (tùy chọn CAGR-tilt, robust nhưng marginal)
- **Lệnh:**
  ```bash
  NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" \
  BULL_PARK_COND=1 AUDIT_END=2026-06-19 $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge
  ```
- **CSV:** `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_bullpark60f70.csv`
- **Metric (2026-06-19):** CAGR **28.75%** / Sharpe 1.84 / MaxDD −18.8% / Calmar 1.53 | self-check **0 VND** | fired 356 bull-days
- **vs R3 NEUTRAL-only (28.26/Sh1.87):** IS +0.22 / OOS +0.72 = **PASS chữ-ký** (cả hai dương). Robust nhưng nhỏ (+0.49pp CAGR, −0.03 Sharpe).
- *Cơ chế:* deploy custom30V trong BULL/EXBULL khi breadth≥0.60, soft-taper extension. Default OFF (BULL_PARK_COND unset) = byte-identical R3. **Tùy chọn**, không mặc định.

### R6 — custom30B BULL VEHICLE (faithful dual-vehicle) @50B & @20B  [2026-06-20]
custom30V parking trong NEUTRAL + **custom30B trong BULL/EXBULL** (state-spliced vn30_underlying, ADV cũng splice → 20%-ADV cap ép thật). Spec custom30B = `BASKET_SELECT=pemom MOM_W=1.0 LIQ_FLOOR_B=5 namecap`. env mới: `BULL_VEHICLE_C30B=1 C30B_FLOOR=5`.
- **Lệnh (@50B):**
  ```bash
  NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7,4:0.7" \
  BULL_VEHICLE_C30B=1 C30B_FLOOR=5 AUDIT_END=2026-06-19 $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge
  ```
- **CSV @50B:** `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-70_4-70_wtnamecap_c30bfl5.csv`
- **CSV @20B:** `...park3-70_4-70_wtnamecap_c30bfl5_nav20B.csv` (NAV_TOTAL_B=20)
- **Metric @50B:** CAGR **29.23%** / Sharpe 1.81 / MaxDD −18.8 / Calmar 1.56 | self-check **0 VND**
- **Metric @20B:** CAGR **32.26%** / Sharpe 1.94 / MaxDD −20.1 / Calmar 1.61 | self-check **0 VND**
- **VERDICT (vehicle custom30B vs custom30V, cùng PARK 3+4):** @20B **+0.57pp** (R1 31.69 → 32.26, Sh1.91→1.94, edge SỐNG khi capacity chưa ép) | @50B **WASH** (R2 29.24 → 29.23, Sh1.82→1.81 — floor-5B rổ mỏng → 20%-ADV cap ăn hết edge). → custom30B là tính-năng ACCOUNT-NHỎ; ở NAV ref (50B) ngang custom30V. Bull-park lever tổng: @50B +0.98pp vs NEUTRAL-only (R3 28.26→29.24/3).

## KẾT QUẢ THAM CHIẾU phiên 2026-06-19 (số đã verify; chi tiết ở [[settled_decisions_capit_8l_2026]]; ⚠️ CSV có thể đã bị ghi đè bởi run sau — RE-RUN lệnh pinned để tái tạo)
| finding | config khác R1-R3 | số chính | nguồn |
|---|---|---|---|
| Parking ablation @50B (đóng góp NEUTRAL park) | argv `v23a` THUẦN (no postbull/edge) | OFF 19.12 / NEUTRAL 26.51 / NEU+BULL 27.03 | item 17, `run_park_ablation.sh` |
| custom30V vs rổ cũ blend @50B | như trên, BASKET_SELECT=blend | blend 22.81 → yieldcombo 26.51 (**+3.7pp**) | item 17 |
| Branch-C decompose @20B | ETF_LIQ=off (**E1VFVN30** parking), argv `v23a` | baseline 22.53 / gated-overflow IS+0.00 OOS+1.17 / depth IS−1.60 | item 15 |
| Live-config window 2025-06→nay @50B | custompitg+namecap+yieldcombo+NEUTRAL+overflow ON, argv `v23a` | +10.8% vs VNI +37 (grind −26pp) | item 18 |
| Value-book standalone @20B | `pt_value_book.py` | 11.0%/Cal0.29; blend vào prod LÀM TỆ | item 19 |
| Megacap sleeve Stage-1 @20B | `blend_megacap_stage1.py` | regret-cut tối đa +1.3pp → KILL | item 20 |
