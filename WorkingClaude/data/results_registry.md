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
6. **`BQ_CACHE_THREADS=1` BẮT BUỘC cho mọi số pin (từ 2026-06-25).** Phát hiện: DuckDB cache đa-luồng (threads=4 cũ) trả rows THỨ TỰ NGẪU NHIÊN khi query thiếu `ORDER BY` → ops order-dependent (drop_duplicates keep-first) chọn row khác → CÙNG config + CÙNG AUDIT_END + CÙNG as-of vẫn ra số KHÁC mỗi run (spread ~0.2pp baseline, tới ~2.7pp ở config bull-park). Self-check 0 VND KHÔNG bắt được (mỗi run reconcile nội bộ); CSV-recompute cũng KHÔNG cứu (mỗi run ghi CSV khác). FIX: `BQ_CACHE_THREADS=1` nay là DEFAULT trong `bq_local_cache.py` (Winston commit `1325bf2`) → deterministic (chứng minh R3a==R3b bit-for-bit). Số pin TRƯỚC 2026-06-25 = threads=4 1-sample → coi là ƯỚC LƯỢNG, không tái lập chính xác.

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

### 🔁 RE-PIN 2026-06-25 — threads=1 DETERMINISTIC (thay số threads=4 1-sample ở trên)
> ⚠️ **SUPERSEDED cho R3 (2026-07-11, rồi 2026-07-12):** baseline R3 đã RE-PIN 2 lần — (a) 2026-07-11 sau DT5G swap trong SIGNAL_V11 (28.82/1.90/−15.7/1.83); (b) **2026-07-12 sau khi ĐÓNG KÊNH MOM_N/MOM_S (Scope A, user sign-off) — số chính thức hiện hành: CAGR 27.84% / Sharpe 1.84 / MaxDD −18.2% / Calmar 1.53**, xem section "2026-07-12 — RE-PIN BASELINE R3 (đóng kênh MOM)" cuối file. R1/R2 (bull-park, nghiên cứu) CHƯA re-run với dt5g swap lẫn MOM-closure.
> Chạy lại R1/R2/R3 với `BQ_CACHE_THREADS=1`, CÙNG `AUDIT_END=2026-06-19`, lệnh y hệt. Số dưới là **tái lập được** (R3a==R3b bit-for-bit). Chênh so số cũ = threads-determinism + data-drift 6 ngày gộp; KHÔNG tách được. **Số cũ (threads=4) coi là ước lượng; số này là chuẩn mới.**

| Config | Lệnh (thêm `BQ_CACHE_THREADS=1` vào đầu) | CAGR cũ→mới | Sharpe | MaxDD | Calmar | self-check |
|---|---|---|---|---|---|---|
| **R3 ⭐ LIVE** (NEUTRAL-only @50B, `PARK_STATES="3:0.7"`) | …yieldcombo PARK_STATES="3:0.7" AUDIT_END=2026-06-19 | 28.26 → **28.05** (−0.21, **ROBUST**) | 1.86 | −17.5 | 1.60 | 0 VND, R3a==R3b ✓ |
| R1 (bull-park @20B, `PARK_STATES="3:0.7,4:0.7"`) | NAV_TOTAL_B=20 …PARK_STATES="3:0.7,4:0.7" | 31.69 → **29.01** (−2.68) | 1.77 | −18.1 | 1.60 | 0 VND |
| R2 (bull-park @50B, `PARK_STATES="3:0.7,4:0.7"`) | NAV_TOTAL_B=50 …PARK_STATES="3:0.7,4:0.7" | 29.24 → **28.01** (−1.23) | 1.74 | −17.5 | 1.60 | 0 VND |

**Đọc:** LIVE config R3 BỀN (−0.21pp, Calmar/MaxDD còn TỐT hơn) → go-live không đổi bản chất; ~**28%** là số tái lập được. Config bull-park (R1/R2, nghiên cứu) nhạy hơn với threads (nhiều order-dependent selection ở thêm state BULL) → rớt 1–2.7pp; lợi thế bull-park vs NEUTRAL-only NHỎ hơn từng nghĩ. *(Engine = working-tree có margin-changes của Taylor gated OFF; đã verify byte-identical khi off, FIX4 inert ở config parking vì total_sold_vnd>0.)*

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
  - ⚠️→✅ **REGENERATED 2026-07-06 (job Taylor_20260706_174921):** file này đã bị 1 run khác GHI ĐÈ
    17:20 07-06 bằng cấu hình SAI (V2.3C STATIC 50/50 combination, w_lag_tgt trống → CAGR 17.5%, n_tx=1433).
    Đã regenerate bằng ĐÚNG lệnh pinned dưới đây (interpreter = `$DNA_PYEXE`=wc_venv, KHÔNG phải system
    python3 — pandas2.3 hệ thống unpickle `earnings_surprise_data.pkl` lỗi, venv pandas3 đọc OK). Kết quả
    khớp R3-range: **CAGR 27.39% / Sharpe 1.81 / MaxDD −17.6% / Calmar 1.55, self-check 0 VND (BAL+LAG),
    n_tx=11322, w_lag_tgt populated 3107/3107, combination=V2.3A ALLOCATOR** — khớp baseline data-snapshot
    hiện tại (CÂU 0: 27.35/1.81/−17.6/1.55; IS 26.78 / OOS 27.94), chênh với 28.26 snapshot cũ = data-drift
    adjusted-price (so RATIOS not levels, đúng META caveat). File giờ ĐÚNG là R3.
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

## 🔬 IC PANEL 8L — bản đồ marginal-IC đồng bộ của mọi lăng kính (2026-06-21, Taylor)
**Vì sao:** trọng số value-v3 + gate rating đang dựa trên IC rải rác trong comment, đo lệch khung. Đây là **một** bảng IC PIT đồng bộ.
- **Lệnh:** `source ./wc_env.sh && $DNA_PYEXE ic_panel_8l.py`
- **Input đông cứng (PIT, không look-ahead):** `data/value_panel_2014.csv` (value lenses+route+forward `profit_2M`=T+40) × as-of rating từ BQ `tav2_bq.fa_ratings_8l` (merge_asof, đúng cái `custom_basket.rating_asof` bisect).
- **Artifact:** `data/ic_panel_8l_2014.csv` (lens×metric) + `data/ic_rating_risk_2014.csv` (rating→fwd+crash).
- **Method:** 1 obs/(ticker,quý)=last → 50 cross-section; Spearman IC/quý; marginal=residualize rank trên value-block {ey,cfy,ps,neg_pbz}; gate=as-of rating≤3. Self-check: rating cov 0.97, profit_2M cov 0.98, inf→NaN.

**KẾT LUẬN (robust IS 2014-19 **và** OOS 2020+, trừ khi ghi rõ):**
1. **1/PE (ey) = lăng kính value VÔ ĐỊCH** — raw IC **+0.125 (t=11.0, hit 94%)**, marginal +0.100, trong-gate +0.079; IS+OOS +0.101/+0.149. Mọi thứ khác phải biện minh *thêm* vào ey.
2. **Rating = RISK-GATE, KHÔNG phải return-tilt** (trả lời đòn bẩy #1, robust 2 nửa): raw IC full-universe +0.065 (gate hoạt động) NHƯNG **marginal trong-gate ÂM** (−0.024 pooled; IS −0.035 / OOS −0.015). Bảng (C): fwd-2M **lồi** (rating-1 chỉ 2.49% < rating-3 3.21%) trong khi **crash% đơn điệu** 3.3→4.8→6.5→9.8→9.1. ⇒ **Overweight rating-1 (QTILT=1.5) làm LOÃNG return**; cú cắt cứng ≤3 đặt đúng (rating-4 crash vọt 9.8%). *Không có alpha bỏ quên ở tilt rating.*
3. **cfo_normy marginal = 0 (cả 2 nửa: +0.000/−0.002)** — cú swap v3 2026-06-20 sang cfo_normy cho non-cyclical KHÔNG thêm tín hiệu return vs ey+cfy+ps. Ứng viên đơn giản hoá.
4. **PS phải route-conditioned, không pool** — pooled marginal đổi dấu (IS +0.042 / OOS −0.031) nhưng per-route mạnh ở COMPOUNDER +0.082 / BANK +0.119 / RE +0.090, vô dụng POWER −0.007 / CYCLICAL −0.002. ⇒ route-gating PS của v3 ĐÚNG.
5. **pb_z = lens trực giao + thời-đại-mới** — raw yếu (IS −0.006 / OOS +0.068) nhưng **marginal cao thứ 2 sau ey** (+0.050, t=3.5; IS +0.023/OOS +0.065). Giữ làm trục timing/dislocation, không dùng standalone.
6. **FSCORE robustly thêm marginal TRONG gate** (+0.031 pooled; IS +0.059/OOS +0.025) — **nhiều hơn cả rating**. Ứng viên enhancer selection (chưa test trong custom30V).
7. **LEAD chưa chốt:** SECURITIES cfy IC **+0.246** (pooled, n~34/q) — cashflow-yield áp đảo ở chứng khoán; cần IS/OOS split trước khi tin (financials hiện giữ v2, không dùng cfy).

**THREAD (b)(c) REFRAME (2026-06-22): production V2.4 là RATING-BLIND trong cổng + selector yieldcombo đơn giản.** `custompitg = (quality=none, q2m5, gate=3)` ⇒ rating chỉ là CỔNG nhị phân ≤3, **level 1-vs-2 không làm gì** (QTILT chỉ sống ở mode audit `custompitgq`; trọng số namecap; chọn mã = yieldcombo rank(1/PE)+rank(1/PCF), đều rating-blind). ⇒ **nới cap-2 trong bull = mỹ phẩm** (cyclical cap-2 vẫn ≤3 = đã trong cổng); `cfo_normy` (thread b) cũng chỉ ở screener + mode audit, KHÔNG ở yieldcombo. Cả (b)(c) bản gốc đều ngoài production path.

**THREAD (c) ĐÓNG — value thắng MỌI regime, không có edge regime-SELECTION (2026-06-22, `probe_regime_momentum.py`).** fwd-profit_2M IC theo state DT5G: DOWN ey +0.148 / mom **−0.105**; NEUTRAL ey +0.107 / mom +0.030; **BULL ey +0.156 (t13, MẠNH NHẤT) / mom +0.002 (ZERO)**. Momentum(mom200) KHÔNG vượt value trong bull; value(1/PE) áp đảo mọi state, đỉnh ở BULL. ⇒ **không build selector regime-aware momentum**; giải thích R6 custom30B(pemom) WASH @50B (mom200 vô-edge). **Đòn bẩy regime duy nhất có cơ sở = EXPOSURE không phải SELECTION**: value edge đỉnh ở bull ⇒ park NHIỀU hơn ở bull với CÙNG value selection = bull-park (R5 +0.49pp marginal, đã có). *(SECURITIES cfy +0.246 = ẢO, chỉ 4 quý đủ N_MIN, đã loại — lens value chứng khoán thật = ey/ps.)* DT5G encoding: 1=CRISIS 2=BEAR 3=NEUTRAL 4=BULL 5=EXBULL.

**THREAD (b) ĐÓNG — v3 composite là IS-OVERFIT, GIỮ yieldcombo đơn giản cho V2.4 (2026-06-22, backtest thật, drift-controlled).**
- **Lệnh (cùng phiên, chỉ khác `BASKET_SELECT`):**
  ```bash
  # candidate v3latest:
  NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=v3latest PARK_STATES="3:0.7" AUDIT_END=2026-06-19 $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge
  # baseline yieldcombo (production): BASKET_SELECT=yieldcombo, còn lại y hệt
  ```
- **CSV:** v3latest = `data/v23_..._etfliqcustompitg_wtnamecap_v3latest.csv` (đã preserve; ⚠️ `BASKET_SELECT` KHÔNG có hậu tố filename → v3latest từng ghi đè CSV R3, đã tách & khôi phục baseline).
- **Metric CONTEMPORANEOUS (cùng data state, đã khử drift):** yieldcombo FULL **28.60%** (IS 27.93 / **OOS 29.18**) Sh1.89 DD−18.9 | v3latest FULL **28.87%** (IS **29.33** / **OOS 28.40**) Sh1.91 DD−18.7 | self-check **0 VND** cả hai; recompute CSV khớp FULL.
- **Verdict:** v3latest +0.27pp FULL nhưng **dồn hết IS (+1.40), OOS THUA −0.78pp** → **IS-overfit, trượt chữ-ký robust** (PASS=cả hai dương). yieldcombo OOS tốt hơn. **GIỮ yieldcombo `rank(1/PE)+rank(1/PCF)`** cho production; KHÔNG nhận v3 composite làm selector.
- *Lưu ý drift:* R3 pinned 28.26 (snapshot 2026-06-15/19) đã trôi → **28.60** phiên này do as-of republish; dùng cặp contemporaneous trên cho đối chứng v3-vs-combo (KHÔNG so v3latest mới với R3 cũ).

## ⭐🟢 RECOVERY-PARK in FULL V2.4 harness — CLEAN WIN (2026-06-22, self-check 0 VND)
Recovery-deploy WIRED into pt_v23 (env `RECOVERY_PARK` via `cash_etf_states_by_date` hook; extend parking into CRISIS/BEAR when median liquid-universe pb_z deep-cheap, depth-scaled; pb_z causal prior-month). Survives ON TOP of the existing capit arm.
- **Lệnh (clean deploy config wmax=0.9):**
  ```bash
  NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" \
  RECOVERY_PARK=1 RECOVERY_WMAX=0.9 RECOVERY_PBZ_DEEP=-0.7 AUDIT_END=2026-06-19 $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge
  ```
- **CSV:** `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_recpark90z70.csv`
- **Metric (contemporaneous, restored data):** baseline R3 **29.92%**/Sh1.96/DD−18.5/Cal1.61 → **recovery wmax0.9 30.71%**/Sh1.98/**DD−17.5**/Cal1.76 | both self-check **0 VND**. Δ **+0.79pp CAGR, −1.0pp MaxDD (BETTER), +0.15 Calmar**. Fires 59 deep-cheap CRISIS/BEAR days (COVID+SCB).
- **Self-check note:** wmax=1.0 gives 30.97% but cash-flow err 12,628 VND (parking frac=1.0 edge: no cash cushion for JIT sweep). wmax=0.9 leaves cushion → EXACT 0 VND, captures ~all upside (−0.26pp vs 1.0). **Deploy 0.9.**
- **First real V2.4 enhancement of the 2026-06-21/22 session** that adds return AND cuts drawdown AND passes strict audit AND survives capit. Grounded in user conviction + value-IC-strongest-in-DOWN + large-n cheapness→payoff.
- **Caveat:** fires 59 days/2 episodes (COVID+SCB), all OOS (IS had no deep-cheap crisis) → opportunity-capture/fail-safe profile like DT5G, not a statistically-robust re-tunable knob.

**UPDATE 2026-06-22 — BEST CLEAN config + "margin" correction:**
- **Deploy config (clean, leverage-free): `RECOVERY_PARK=1 RECOVERY_WMAX=0.95 RECOVERY_PBZ_DEEP=-0.5`** → CAGR **31.81%** / Sh **2.02** / MaxDD **−16.4%** / Calmar **1.94** | self-check **0 VND**. vs baseline R3 29.92%: **+1.89pp CAGR, −2.1pp MaxDD (BETTER), +0.33 Calmar**. CSV `..._recpark95z50.csv`.
- **CORRECTION:** the parking vehicle CANNOT use margin (engine `simulate_holistic_nav.py` line 197: "ETF parking never uses margin"; buy caps at available cash). So earlier `wmax=1.5` was NOT leverage — it was a STEEPER idle-cash deployment (deploy ~full cash at MODERATE cheap pb_z~−0.5). The +1.9pp/−2.1pp DD is **LEVERAGE-FREE** (no borrow, no margin-call risk) — better than margin.
- **Self-check root:** `etf_frac=1.0` (deploy 100% pool = zero cash cushion) → JIT-sweep rounding residual (12.6k–54k VND, transient, final-NAV exact). Cap at **0.95** (5% cushion) → EXACT 0 VND, captures ~all upside (31.81 ≥ the dirty 1.0/1.5 runs).
- **Robust family (all beat baseline, better DD):** 0.9/−0.7 → 30.71% (gentle) … 0.95/−0.5 → 31.81% (aggressive). Deployment aggressiveness = (wmax, deep); same 59 fire-days. **Deploy 0.95/−0.5 (clean best).**
- **REAL margin (>100%)** would need `max_gross_exposure` on the STOCK book (real borrow, cash<0) — SEPARATE mechanism, riskier, optional future build; idle-cash 0.95 already captures the cheap-deploy edge leverage-free. **trading_rules v1.3 regime-cap 1.5x = for that future margin path, not this idle-cash config.**
- Status: PROPOSED V2.4 add, paper → user go-live approval + Spyros review.

## 🟢 RECOVERY-DEPLOY (valuation-conditioned re-risk) — thesis CONFIRMED, rare-firing opportunity-capture (2026-06-22)
Luận điểm user: cơ hội bất đối xứng ở phục hồi CRISIS→BEAR + định giá rẻ, KHÔNG phải đòn bẩy EXBULL. Validated qua 2 bước:
- **Event-study** (`probe_recovery_signal.py`): deploy trong CRISIS/BEAR fwd-6M VNINDEX = naive +0.2% vs **+cheap(med pb_z≤−0.3) +19.8% win100%**; rate signals (refi/deposit) LAG & không phân biệt. Gate định-giá-vs-lịch-sử tự lọc dao rơi: **né mid-2022 (pb_z +0.75 = vẫn đắt dù −25% từ đỉnh), bắt COVID-2020 (pb_z −0.78)**. ⇒ KHÔNG cần overlay lãi suất; KHÔNG hồi sinh EASING_FLOOR.
- **Allocation backtest** (`backtest_recovery_alloc.py`, VNINDEX-exposure, deposit-thật+borrow10%+T+1+ramp3+TC0.1%): baseline DT5G-curve 14.7%/Sh1.18/DD−18.4 → recovery mild(C.35/B.55) **15.3%/Sh1.21/DD−18.4** → deep(C.70/B.70) 15.8%/Sh1.24. **MaxDD KHÔNG đổi** (deploy chỉ khi rẻ=gần đáy). Self-check: T+1 lag, pb_z/deposit causal, fire 59 phiên.
- **BẢN CHẤT (trung thực):** IS 2014-19 y hệt (14.3%) — signal CHƯA BAO GIỜ fire in-sample; toàn bộ edge = **2 episode/59 phiên (COVID + post-SCB), đều OOS**. Profile = DT5G: opportunity-capture hiếm nổ, DD-free khi nổ, KHÔNG robust thống kê từ 2 sự kiện. **Deploy CONSERVATIVE (mild), đừng tune sâu.** Caveat: VNINDEX-proxy, chưa wire vào custom30V allocator (baseline 14.7≠V2.4 28; đây là increment exposure-timing).

## 🟡 2011-EXTENSION: crisis-buy + MARGIN is REGIME-CONDITIONAL — deposit-gate is the fix (2026-06-22)
Mở rộng recovery-deploy + margin về **2011** (data FA/giao dịch/VNINDEX đã có; regime = base `vnindex_5state` chạy từ 2000 vì DT5G chỉ 2014+; borrow = **deposit+4% era-aware**, vì margin VN 2012 ~18–24%/yr KHÔNG phải 10%). File `backtest_recovery_alloc_2011.py`.
- **PHẢN BIỆN trực giác "2012 great buy" (ở tầng index-timing):** trong **2011–13**, BASELINE (0% trong crisis, **ăn lãi tiền gửi 14%**) **THẮNG mọi biến thể deploy**: baseline **+8.4%** vs recovery-deep +2.9%, margin1.5 +7.1%. Nguyên nhân: deposit 14% (opp-cost tiền mặt khổng lồ) + hồi phục **hình-L chậm** (pb_z rẻ từ giữa-2011 nhưng VNINDEX mài 433→358 suốt 2012, không V-shape như COVID).
- **FIX = DEPOSIT-GATE:** scale deploy theo điều kiện tiền tệ `m=clip((dep_ceil−deposit)/(dep_ceil−dep_floor),0,1)`, floor6%/ceil12%. Lãi rẻ→deploy đủ; lãi cao→giữ tiền mặt dù pb_z rẻ. Dung hợp 2 lệnh user: bet-khi-rẻ(pb_z) + thận-trọng-khi-macro-xấu(lãi cao).
- **Kết quả `+DEPgate m1.5`:** full 2011–26 CAGR **12.8% (best)** / Sharpe **1.11 (best)** / MaxDD **−18.7% (=baseline, xoá −10pp drawdown của margin trần)** / Calmar **0.68 (best)** | 2011–13 **+8.4% (=baseline, gate chặn dao rơi 2012)** | 2020–26 +17.9% (giữ phần thắng COVID). Bền với borrow spread 8%.
- **FREE INSURANCE:** deposit chưa bao giờ >12% trong 2014–26 → gate **DORMANT** kỷ nguyên DT5G (17.0% vs ungated 17.2%, ~0 chi phí in-sample) nhưng cứu +5.5pp ở crisis lãi-cao 2012. Cùng profile fail-safe như DT5G → **nên port vào production recovery-park làm bảo hiểm forward: 0 thay đổi 31.81% đã pin, bảo vệ một crisis kiểu-2012 tương lai.**
- **Margin AN TOÀN suốt:** worst NAV-drop khi đòn bẩy chỉ −7.4% vs ngưỡng call verified −44%(1.5x)/−61%(1.3x) → buffer 37–54%, không suýt call lần nào, kể cả borrow 8%. Margin nổ 2012-01, 2012-11, COVID-2020, 2021, 2023, 2025.
- **CAVEATS:** (1) tầng VNINDEX-exposure ≠ stock-selection — "2012 great buy" của user vẫn có thể đúng cho stock-picker chất lượng (index bị NH/BĐS kéo); test này chỉ nói index-TIMING nên giữ 14% cash. (2) ngưỡng deposit 6/12% neo-kinh-tế chứ không grid-fit; chỉ 1 crisis (2012) kích cạnh-cao = n=1. (3) **PE pre-2014 VẪN HỎNG** (median liquid PE ~2 → bất khả) → không dùng được Fed-model 1/PE thật, phải proxy bằng LEVEL lãi suất. **Re-flag Winston.**
- Status: R&D finding, paper. Next: port deposit-gate vào `pt_v23` RECOVERY_PARK + thêm `money_condition` vào `trading_rules` deep_cheap_recovery_override.

## 🟢 2012 crisis-buy CONFIRMED at STOCK-SELECTION layer — reconciles the index hold-cash (2026-06-23)
`probe_stockpick_2012.py`: rổ **quality+deep-value top8** (NP_P0>0, FSCORE≥5, ROE5Y≥5%, DebtEq<3, rank pb_z asc), lập hàng tháng, forward 6M/12M vs VNINDEX vs cash(deposit). PE pre-2014 corrupt (không dùng); DY NULL pre-2013-05 (không test được dividend-tilt).
- **12M: MEAN rổ +40.8% vs VNINDEX +16.0% vs cash +9.2%** (14 forms 2011-09…2013-05); vs_cash **+31.6pp, win-vs-cash 86%**. Forms H2-2012/đầu-2013 (lãi rơi 12→9→7.5%): 2012-09 **+43.8%**, 2012-10 **+52.3%**, 2013-01 **+83.0%**, 2013-03 **+75.7%** — đè bẹp index+cash.
- **HÒA GIẢI:** cả hai kết quả đúng — index-timing nói giữ 14% cash (chỉ số là dao rơi do NH/BĐS), stock-selection nói rổ chất lượng+rẻ hồi 40–83%. ⇒ **alpha 2012 ở CHỌN MÃ, không ở canh chỉ số.** Trí nhớ user ĐÚNG ở tầng cổ phiếu. Ủng hộ deploy recovery ở **tầng stock-picker** = đúng cơ chế production recovery-park (`pt_v23` RECOVERY_PARK → custom30V).
- **Ủng hộ deposit-gate:** forms H1-2012 (lãi 12–14%) VẪN LỖ (2011-09 −16.8%, 2012-04 −0.6% 12M); mã thắng dồn **sau giữa-2012 khi lãi đã hạ** → entry tốt nhất khi lãi đã cắt, không phải lần đọc pb_z-sâu đầu tiên.
- **CAVEATS:** (1) **bias sống sót** — `ticker_prune` curated bằng hindsight → +40% **bị thổi lên**, hướng vững/số lạc quan. (2) thanh khoản 2012 mỏng (top8 từ 40–80 mã) + slippage thật ăn bớt. (3) picks tập trung họ **PetroVietnam** (PVS/PVD/PGS/DPM) = theme re-rating 2013, rủi ro tập trung. (4) DY NULL pre-2013-05 → chưa test được carry cổ-tức>lãi-gửi user nhớ.
- Status: R&D finding, paper. Củng cố recovery-park-ở-tầng-stock-picker cho go-live.

## 🟢 DEPOSIT-GATE ported into pt_v23 RECOVERY_PARK — DORMANT floor=7.5 chốt default (2026-06-23)
Wire money-condition `m=clip((CEIL−deposit)/(CEIL−FLOOR),0,1)` vào deploy của RECOVERY_PARK (nhân vào `frac`), deposit causal ffill từ `DEPOSIT_EVENTS`. Đo 3 run (config `RECOVERY_WMAX=0.95 RECOVERY_PBZ_DEEP=-0.5 AUDIT_END=2026-06-19`), **tất cả self-check 0 VND**:
| run | avg m | CAGR | Sharpe | MaxDD | Calmar | NAV |
|---|---|---|---|---|---|---|
| gate OFF (regression) | — | **31.81%** | 2.02 | −16.4% | 1.94 | 1561.18B |
| **DORMANT floor=7.5** | **1.00** | **31.81%** | 2.02 | −16.4% | 1.94 | **1561.18B** |
| ACTIVE floor=6 | 0.85 | 30.83% | 1.98 | −17.4% | 1.77 | 1422.87B |
- **Dormant-7.5 = BYTE-IDENTICAL baseline** (gate chưa cắn lần nào: 2014–26 deposit ≤7.5% → m=1 trên cả 59 ngày fire). **0 thay đổi 31.81%** → bảo hiểm forward thuần.
- **Active-6 BỊ LOẠI:** −0.98pp CAGR + xấu mọi metric, vì cắt nhầm cú deploy SCB-2022 (avg m=0.85) mà 2022 sau đó hồi mạnh (rally 2023).
- **Vì sao floor6 thắng ở test-index nhưng thua ở đây:** giá trị bảo vệ của gate nằm TOÀN BỘ ở môi trường lãi >7.5% kiểu-2012 — `pt_v23` 2014–26 không có; floor6 chỉ chạm cú 2022 (lãi nâng phòng thủ, thị trường vẫn hồi) → thuần chi phí. floor7.5 phân biệt đúng crisis-thật vs nâng-phòng-thủ. Khớp macro-view SBV-hậu-2011 kỷ luật hơn.
- **CHỐT default: `RECOVERY_PARK=1 RECOVERY_WMAX=0.95 RECOVERY_PBZ_DEEP=-0.5`** (deposit-gate ON mặc định floor 0.075). = baseline y hệt hôm nay + tripwire chỉ võ trang khi lãi >7.5%. `trading_rules` v1.5 đồng bộ floor 0.075. Code: `pt_v23_audit_2014.py` (import DEPOSIT_EVENTS, `_dep_asof`/`_dep_m`, env `RECOVERY_DEP_GATE/FLOOR/CEIL`). Status: PROPOSED V2.4 add, paper → user duyệt + Spyros review.

## 🟢 FED-SPREAD-GATE tested + DATA-DRIFT correction (2026-06-23)
- **(A) Fed-spread-gate** (m theo market eyield−deposit = `1/VNINDEX_PE − dep`, dùng `VNINDEX_PE` SẠCH — chỉ per-stock `t.PE` hỏng, Winston xác nhận = Close_adj/EPS understated). Wire vào `pt_v23` `RECOVERY_GATE_MODE=fed` (floor0/ceil1.5%) + index-backtest. **Kết quả pt_v23: fed = deposit = baseline BYTE-IDENTICAL** (NAV 1396.51B/30.63%/Sh1.97/DD−17.5/Cal1.75, 0 VND cả ba). Replicate m trên 59 ngày fire: **m_fed=1.00 VÀ m_dep=1.00 khắp nơi** (fire windows 2020-03 spread+3.2%, 2020-04 +3.0%, 2022-11 +1.8% đều >ceil; deposit ≤7.5% <floor). Hai money-gate **thật sự dormant** — PE thị trường đồng ý "deploy" mọi cửa sổ in-sample. Khác biệt fed-vs-deposit chỉ lộ ở crisis-lãi-cao tương lai (hoặc pre-2014).
- **DATA-DRIFT (quan trọng):** baseline **31.81% (hôm qua/sáng) → 30.63% (giờ)** do `ticker_prune` refresh giữa snapshot (ngày→2026-06-23; corp-action DTD ex-2026-06-22 reset hệ số). Lần đầu tôi đọc fed "−1.18pp" = **so với baseline cũ stale, KHÔNG phải lỗi fed** — controlled same-snapshot 3-run chứng minh cả ba y hệt. **Số tuyệt đối trong registry sẽ trôi theo data; DELTA enhancement mới ổn định.**
- **Delta hiện tại (snapshot 2026-06-23):** R3 baseline 29.00%/Sh1.90/DD−18.5/Cal1.56 → recovery-park 0.95/−0.5 30.63%/Sh1.97/DD−17.5/Cal1.75 = **+1.63pp CAGR, −1.0pp MaxDD, +0.19 Calmar, 0 VND**. (prev +1.89pp; delta bền với drift.)
- **Quyết định:** giữ **deposit-gate-7.5 làm default production** (input DEPOSIT_EVENTS robust, đơn giản, nhanh hơn — eyield của fed LAG crash nhanh vì PE prior-month); **fed-gate giữ lại làm alternative đã-test có doc** (`RECOVERY_GATE_MODE=fed`) tôn trọng ý dùng PE thị trường của user. Cả hai byte-identical in-sample.

## 🟢 REAL-MARGIN self-check FIXED + 1.3x chốt làm trần (1.5x LOẠI: nổ tail COVID) (2026-06-23, cập nhật)
- **Self-check FIX:** engine ghi `interest` (deposit/borrow) mỗi ngày vào nav_history; pt_v23 cash-flow self-check **trừ ra** → margin runs giờ **EXACT 0 VND** (trước 9–21M = đúng lãi vay chưa log, đã chứng minh). **Pin được.**
- **Clean same-snapshot:** leverage-free 30.72%/Sh1.97/DD−17.5/Cal1.76 | **MGE1.3 32.22%/Sh2.03/DD−15.5/Cal2.08** | MGE1.5 31.65%/Sh1.83/**DD−32.5**/Cal0.97 — cả ba 0 VND.
- **⚠️ PHÁT HIỆN RỦI RO then chốt:** −32.5% của 1.5x = **COVID-2020** (đỉnh 2020-01-22 NAV262B → đáy 2020-03-31 177B, hồi 2020-10): 1.5x vay tới **−57.3B** lao vào cú sụp −34% → đòn bẩy khuếch đại đáy (bắt-dao-rơi-bằng-margin). Ở **1.3x cùng cú COVID lại KHÔNG vượt DD thường** (đáy 1.3x là episode 2025 lành −15.5%, chỉ vay −25.6B). 1.5x còn **fragile** (snapshot trước −16.3% → giờ −32.5%).
- **CHỐT: 1.3x = trần margin robust** (+1.50pp CAGR, DD −15.5 TỐT HƠN leverage-free, Calmar 2.08, 0 VND). **LOẠI 1.5x.** `trading_rules` v1.6 siết override 1.50→1.30 (tail DD bind trước cả call-buffer).
- Code: engine `_interest_today` + nav `interest` col; pt_v23 self-check trừ interest; `MGE/MGE_CAPIT_ONLY/BORROW_ANNUAL` env. Vẫn là đòn bẩy THẬT → Spyros + user duyệt; go-live giữ leverage-free. 1.3x margin = nâng cấp hậu-go-live (giờ sạch + DD-bounded).
### (lịch sử) REAL-MARGIN branch (CAPIT-only) — accretive nhưng self-check chưa sạch + là đòn bẩy THẬT (2026-06-23)
Nhánh MỚI `pt_v23`: `MGE` env mở `max_gross_exposure` trên sổ CK + `margin_tiers={CAPIT}` → **chỉ nhóm washout deep-cheap được vay** (đòn bẩy thật, cash<0, charge borrow), CAPIT size được thêm headroom `(MGE−1)×size`. Khác recovery-park (tiền nhàn, gross≤100%): đây là **>100% thật** nhưng chỉ rơi vào washout, không vay ở thường/EXBULL. Env: `MGE`, `MGE_CAPIT_ONLY`, `BORROW_ANNUAL`.
- **Same-snapshot:** leverage-free 30.63%/Sh1.97/DD−17.5/Cal1.75 → **MGE1.3 31.40%/1.99/−16.5/1.90** → **MGE1.5 31.90%/2.02/−16.3/1.95**. Margin **tốt hơn MỌI chiều**: +0.77/+1.27pp CAGR ĐỒNG THỜI MaxDD thấp hơn + Calmar/Sharpe cao hơn (lệnh washout vay được nâng đáy NAV).
- **Bền với lãi vay:** borrow 0/10/14% → NAV 1574.95/1574.92/1574.91B đều 31.90%. Vay ngắn-hạn trong washout, trả khi hồi → carry không đáng kể vs payoff.
- **⚠️ Self-check CHƯA sạch (chưa pin):** cash-flow err 9.0M@1.3x / 15.2M@1.5x@10% / 21.2M@14%, **chứng minh = tiền LÃI VAY** (engine trừ lãi vào cash không tạo tx row; check không cộng). PROOF: borrow=0 → err **0 VND**; err scale tuyến tính theo lãi; final-NAV identity luôn = 0 → **KHÔNG rò tiền**. Để pin: thêm số hạng lãi-vay vào cash-flow self-check (1 fix) hoặc log lãi thành tx row.
- **RỦI RO:** đòn bẩy THẬT (cash<0), gross đỉnh 1.3–1.5x chỉ trong washout. Buffer verified: call ở −44% (1.5x) vs worst washout DD −7.4% → an toàn. **Cần Spyros review + user duyệt** trước mọi dùng ngoài R&D — KHÁC hẳn recovery-park leverage-free.
- Status: R&D, paper, **NOT pinned**. Go-live giữ **LEVERAGE-FREE** (recovery-park 0.95). Real-margin = nâng cấp hậu-go-live tùy chọn, chờ fix self-check + Spyros.

**META — 8L research 2026-06-21/22: 4 enhancement ứng viên ĐỀU trượt OOS/mỹ phẩm** → FSCORE-tilt (âm), rating-tilt (dilutive), momentum-regime (no edge), v3-composite (IS-overfit). **Production simple yieldcombo = robust-optimal đã được xác nhận** → de-risk go-live 2026-06-30 (đừng thêm phức tạp).

**THREAD (a) — FSCORE enhancer: proxy NEGATIVE (2026-06-21, `probe_fscore_select.py`).** Pre-backtest proxy (top-30 of top-60 liquid, gate≤3, equal-wt mean profit_2M, 47 quý): thêm `FS_W*rank(FSCORE)` vào điểm yieldcombo **LÀM TỆ** mọi trọng số (FS_W 0.25/0.5/0.75/1.0 = −0.27/−0.34/−0.24/−0.46pp vs base 3.80%), cả IS(1.55) lẫn OOS(5.79), win%q<50. **Vì sao:** IC-biên +0.041 của FSCORE là hiệu ứng *chiều rộng* (~1000 mã gate); KHÔNG sống trong rổ top-30-value cô đặc giữa 60 mã thanh khoản mà custom30V build (FSCORE bị nén + kéo ngược trục value). ⇒ **Đừng đốt full backtest cho dạng tilt ngây thơ**; chuyển hướng: FSCORE làm GATE đáy (loại bottom-FSCORE khỏi pool trước khi rank value) hoặc dạng interaction, chỉ backtest form nào vượt base trong proxy trước. *(Proxy không NAV/cost; full pt_v23 vẫn là trọng tài cuối.)*

**H1 (R&D Q3 program) — FSCORE BOTTOM-EXCLUSION gate: proxy NEGATIVE, H1 ĐÓNG (2026-07-05, `probe_fscore_exclude.py`, job `Taylor_20260705_020935`).** Đã theo đúng hướng thread-(a) chỉ ra (loại đuôi FSCORE thấp TRƯỚC khi rank value, KHÁC additive-tilt): trong pool top-60 liquid gate≤3 mỗi quý, DROP bottom-q FSCORE (q∈{10%,20%}, 2 điểm — KHÔNG grid) rồi rank yieldcombo=rank(1/PE)+rank(1/PCF) chọn top-30, 47 quý. Kết quả **LÀM TỆ đơn điệu**: base mean2M 3.80% (IS 1.55 / OOS 5.79) → excl-10% 3.42% (−0.38pp; IS 1.21 / OOS 5.36; win%q 32%; drop TB 4.8 mã) → excl-20% 3.03% (−0.77pp; IS 0.62 / OOS 5.15; win%q 26%; drop TB 11.7 mã). **FAIL cả 2 điểm ở CẢ IS lẫn OOS + win%q<<50%.** **Vì sao (diagnostic):** trong pool top-60 liquid+gated, cohort bottom-20%-FSCORE có fwd2M +2.53% ≈ phần còn lại +2.47% (edge +0.06pp = nhiễu) và độ rẻ y hệt (yieldcombo-rank 1.00 vs 1.02) → FSCORE KHÔNG có sức tách trong universe cô đặc này; alpha avoid-low-F của Piotroski là hiệu ứng *chiều rộng* (~1000 mã, phần lớn junk illiquid) đã bị GẠT SẴN bởi gate rating≤3 + lọc thanh khoản top-60 + rank value. Loại tên chỉ làm co pool → pick top-30 phải với sang tên value kém hơn → dilute. ⇒ **KHÔNG lên harness. H1 đóng ở proxy tier** — không đề xuất env `BASKET_FS_FLOOR`. FSCORE (mọi dạng: additive-tilt thread-(a) VÀ exclusion-gate H1) không cải thiện custom30V. *(Proxy không NAV/cost; guardrail: BQ_CACHE_THREADS=1, PIT panel frozen `value_panel_2014.csv`, không dùng profit_* làm filter.)*

**T2 (R&D Q3 program) — IC-PANEL EXTENSION, 4 new lenses: only H6a MAX5_1M survives tier-1 (2026-07-05, `ic_panel_ext_q3.py`, job `Taylor_20260705_075638`).** Extended the frozen 2026-06-21 marginal-IC panel with 4 candidate lenses on the SAME PIT input (`value_panel_2014.csv` collapsed 1/ticker/q, 50 quarters, 53.5k obs / 24.2k in-gate), SAME machinery: marginal IC = residualize rank(lens) on the value block {ey=1/PE, cfy=1/PCF, ps=1/PS, neg_pbz} per quarter, in-gate (as-of rating≤3), split IS(2014-19, 22q)/OOS(2020+, 25q) + crash%(profit_2M<−20) by lens quintile. New file (frozen `ic_panel_8l.py` untouched, imports its `load/marginal_ic_series/summ`; NO production strategy file changed). PIT: financial lenses merge_asof on `Release_Date`≤obs; daily-micro windows strictly backward (end-of-day at obs). Artifacts `data/ic_panel_ext_q3.csv` + `..._quintile.csv`.

| lens | expect | raw IC gate | mIC-gate IS | mIC-gate OOS | t IS / OOS | crash% Q1→Q5 | verdict |
|---|---|---|---|---|---|---|---|
| **H6a MAX5_1M** (mean top-5 daily ret, 21-sess) | −IC | **−0.060** | **−0.047** | **−0.042** | −1.9 / −2.6 | 4.2→4.2→4.4→5.7→**10.1** | **ELIGIBLE tier-2 proxy** |
| H6b limit_freq_1M (freq raw-ret≥0.065, 21-sess) | −IC | −0.057 | −0.026 | −0.049 | −1.2 / −2.9 | 3.8→7.1→1.8→6.0→9.8 | CLOSED tier-1 |
| H4 accruals (Sloan: (NP_TTM−CFO_TTM)/Assets) | −IC | −0.031 | +0.010 | −0.027 | +0.3 / −1.1 | 5.0→4.0→5.6→5.9→7.8 | CLOSED tier-1 |
| H5 dividend yield (DY, cash) | +IC | +0.009 | −0.017 | −0.002 | −0.8 / −0.1 | 6.9→9.7→3.9→4.2→3.7 | CLOSED tier-1 |

- **H6a MAX5_1M = the one survivor** — the lottery/MAX effect (Bali-Cakici-Whitelaw 2011) is a REAL marginal risk axis beyond value: names with the largest recent daily-return spikes have LOWER forward 2M return AND >2× the crash rate (top quintile 10.1% vs 4.2% bottom) — the ONLY lens hitting mIC-gate ≤ −0.03 in BOTH halves (−0.047 IS / −0.042 OOS, sign+magnitude both hold). It is a lottery/short-reversal axis, orthogonal to the value block custom30V ranks on ⇒ natural tier-2 form = an **EXCLUSION/penalty overlay** (avoid lottery-like names inside the value basket), NOT a value tilt. NOT yet backtested in custom30V.
- **H6b = same effect, cruder/noisier** — directionally identical (raw −0.057, crash rises to 9.8%) but limit-hit is a sparse count (many zeros; +0.065 raw threshold is a HOSE-only proxy — HNX/UPCOM have wider limits) → IS marginal only −0.026 (misses −0.03) + crash non-monotone. H6a is the continuous, robust form of the same signal; H6b adds nothing over it.
- **H4 accruals CLOSED** — mild raw −0.031 but marginal FLIPS +0.010 in IS: the value block (esp. cfy=1/PCF) already encodes cashflow-vs-earnings quality, so residualized accruals add no return signal. Crash tilts up directionally (5.0→7.8%) but not monotone.
- **H5 dividend yield CLOSED** — no return edge in-gate (marginal −0.017/−0.002, fails ≥+0.03), BUT crash-protective (high-DY Q5 3.7% vs low-DY Q1-2 6.9-9.7%) — a defensive quality, not alpha; DY correlates with 1/PE cheapness already captured. (Caveat: `DY` field used as-is per data dict = cash-div yield; stock dividends not cleanly separable.)
- **Guardrails met:** direct BQ, `profit_*` used ONLY as IC target never as feature, PIT strict (Release_Date merge_asof + backward-only daily windows), universe = in-gate rating≤3 on the frozen panel = same frame as the 2026-06-21 panel. Proxy tier only (no NAV/cost). **Next if pursued: H6a as a penalty/exclusion overlay in a full `pt_v23` custom30V backtest** (tier-2) — the only candidate worth the compute; H4/H5/H6b do not advance.

**Wave1/H6a (R&D Q3 program) — MAX5_1M LOTTERY-EXCLUSION overlay: proxy NEGATIVE, H6a ĐÓNG (2026-07-05, `probe_max5_exclude.py`, job `Taylor_20260705_085946`).** Đã theo đúng dạng tự nhiên registry chỉ ra (loại đuôi lottery-like TRƯỚC khi rank value, KHÔNG phải value-tilt — đảo chiều lens của H1): trong pool top-60 liquid gate≤3 mỗi quý, DROP top-q MAX5_1M cao nhất (q∈{10%,20%}, 2 điểm — KHÔNG grid) rồi rank yieldcombo=rank(1/PE)+rank(1/PCF) chọn top-30, 47 quý. MAX5_1M gắn as-of mỗi quý (BQ trailing-21-session, end-of-day at obs, backward-only — SQL y hệt `ic_panel_ext_q3.attach_new_lenses`; coverage pool 1.00; fail-safe giữ tên NaN-max5). Kết quả **LÀM TỆ đơn điệu (FAIL cả 2 điểm ở CẢ IS lẫn OOS)**: base mean2M 3.80% (IS 1.55 / OOS 5.79) → excl-10% 3.63% (−0.17pp; dIS −0.10 / dOOS −0.24; win%q 43%; drop TB 6.9 mã) → excl-20% 3.47% (−0.33pp; dIS −0.49 / dOOS −0.19; win%q 49%; drop TB 12.9 mã). **So H1 neg-control: H6a ÍT hại hơn** (H1 excl-10% −0.38pp win 32% / excl-20% −0.77pp win 26%) — "tốt hơn baseline H1" đúng theo tương đối, nhưng **vẫn FAIL luật tuyệt đối ≥base cả IS/OOS** ⇒ đóng. **Vì sao (khác H1 — quan trọng):** cohort edge lottery **CÓ THẬT** trong pool cô đặc (top-20%-MAX5 fwd2M +2.02% vs rest +2.60% = **+0.59pp**, KHÁC H1 nơi FSCORE-edge chỉ +0.06pp nhiễu) — nhưng KHÔNG dịch được thành cải thiện basket vì **value-rank ĐÃ bắt sẵn phần lớn né-lottery**: tên lottery-like sẵn RẺ HƠN (value-rank pct 0.47 vs 0.52) nên yieldcombo top-30 đã under-weight chúng; exclusion cứng chỉ co pool → substitute sang value kém hơn → dilute nhẹ. **Peek EXPLORATORY (non-gating) dạng SOFT-PENALTY** (score = yieldcombo − λ·rank(max5), λ∈{0.5,1.0}) cũng KHÔNG cứu được: λ=0.5 phẳng (−0.01pp, no-op vì penalty quá yếu để đổi pick), λ=1.0 dIS +0.09 nhưng dOOS −0.40 (net −0.17pp) → không vượt ≥base cả 2 nửa. ⇒ **CẢ HAI vehicle (hard-exclusion VÀ soft-penalty) đều fail** dù signal thật → **KHÔNG lên harness. H6a đóng ở proxy tier** — không đề xuất env `BASKET_MAX5_PENALTY`. Lottery/MAX effect là trục risk thật ở *chiều rộng* panel nhưng redundant với value trong universe custom30V cô đặc (giống hệt cơ chế H1). *(Proxy không NAV/cost; guardrail: BQ_CACHE_THREADS=1, PIT `value_panel_2014.csv` frozen + backward-only micro, không dùng profit_* làm filter, không sửa production file.)*

**Wave1/H7 (R&D Q3 program) — EVEB route-aware yieldcombo swap cho D&A_HEAVY: proxy NEGATIVE, H7 ĐÓNG (2026-07-05, `probe_route_eveb_h7.py`, job `Taylor_20260705_100229`).** TIER-2 proxy (bar CAO hơn H1/H6a: phải thắng **≥+0.3pp CẢ 2 nửa**, không chỉ ≥base) vì H7 là họ hàng gần của composite-v3-as-selector đã bị **bác toàn cục** (IS-overfit, −0.78pp OOS) — prior THẤP. Thiết kế: pool top-60 liquid gate≤3 mỗi quý, chọn top-30 theo yieldcombo, 47 quý (`ic_panel_8l.load()` frozen PIT panel). **base** = rank(1/PE)+rank(1/PCF) mọi tên; **H7** = với tên ∈ `DA_HEAVY_SET` (24 tên NAME-level DA/Rev≥5%, copy verbatim từ `rating_8l.py`) thay leg rank(1/PCF)→rank(1/EVEB), tên ngoài route giữ nguyên. **PE/PCF/EVEB kéo TƯƠI từ `tav2_bq.ticker` tại đúng (ticker,time) quý-cuối** — KHÔNG dùng PE/PCF frozen của panel: panel đã drift khỏi live table do adjust giá cộng dồn per-ticker (GMD 2023-01-31 panel PE 12.14 vs live 16.05, PCF 5.18 vs 6.85, cùng rescale 1.32×), nên trộn 1/PE-frozen với 1/EVEB-live sẽ lệch cơ sở cross-section; kéo cả 3 leg tươi ⇒ base & H7 chung MỘT adjustment basis, vẫn PIT (mỗi giá trị đọc tại `time` của nó). DA trong pool TB **4.0 tên/quý** (max 11), pool EVEB>0 cov 0.82, swap đổi top-30 ở **22/47 quý**. Kết quả **FAIL rõ (cả 2 nửa dưới bar, OOS âm)**: base mean2M 2.87% (IS 0.19 / OOS 5.22) → H7 2.88% (IS 0.29 / OOS 5.16); **dIS +0.09pp** (< +0.30 bar), **dOOS −0.06pp** (ÂM), win%q 30%. ⇒ **ĐÓNG ở proxy tier — KHÔNG thử soft-penalty/biến thể khác/NAV harness** (đúng luật đã định trong plan cho prior thấp). **Vì sao:** swap chỉ chạm ~4 tên/quý và chỉ là chỉnh rank leg-2 nhẹ → hầu như không đổi pick; golden-tier IC của EVEB ở nhóm D&A_HEAVY vốn chỉ +0.01 OOS-robust (mỏng) — đúng như prior. v3_da (`rating_8l.py` default 2026-07-04) vẫn giữ nguyên vai trò **diagnostic value-axis/zone**, KHÔNG ai downstream đọc cho NAV; H7 không đề xuất wire gì vào selector. *(Proxy directional không NAV/cost/T+1; guardrail: BQ trực tiếp không cache, PIT nghiêm, không dùng profit_* làm feature, KHÔNG sửa rating_8l.py/production.)*

**Wave1/H3 (R&D Q3 program) — VOL-MANAGED BAL exposure overlay: FULL-NAV harness FAIL, H3 ĐÓNG (2026-07-05, `pt_v23_audit_2014.py` env `VOLMANAGE_BAL`, job `Taylor_20260705_100245`).** Đây là **DD-cutter, KHÔNG phải selector** (Barroso-Santa-Clara 2015 JFE), test đúng cảnh báo phản biện Cederburg-O'Doherty-Wang-Yan 2020 JFE (vol-managed momentum OFTEN FAILS OOS dưới turnover cost). Thiết kế **cap ≤1.0 KHÔNG lever, σ_target=IS-median KHÔNG tune**: khi bật, sleeve BAL tách stock (cb) + cash (cc, deposit=0), `m = min(1, σ_target/σ_realized_126d)`; σ_realized = rolling-126 std của **chính return-series book BAL**, **causal** (`.rolling(126).std().shift(1)` — chỉ dùng returns < ngày scale); σ_target = **MEDIAN của σ_realized trên IS 2014-2019, tính 1 lần** (14.7% ann @1.0x). Env OFF-default → combine loop **byte-identical baseline** (path `not VOLMANAGE_BAL` = code gốc; baseline chạy lại 27.34% khớp họ R3). Config chính 1.0x + sensitivity ±20% (0.8x/1.2x, KHÔNG grid rộng). **Contemporaneous** AUDIT_END=2026-06-19, threads=1, NAV 50B, `PARK_STATES=3:0.7 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo`. TC resize 0.075%/side **đã nằm TRONG CAGR báo cáo**.

| config | FULL CAGR | OOS CAGR (give-up) | OOS Sh | OOS Cal | OOS MaxDD | mean m | scaled days | vol turnover | TC drag |
|---|---|---|---|---|---|---|---|---|---|
| **baseline** | **27.34** | **27.89** | **1.80** | **1.58** | **−17.6** | — | — | — | — |
| VM 1.0x | 24.51 | 24.16 (**−3.73pp**) | 1.74 ↓ | 1.50 ↓ | −16.1 | 0.870 | 1605/3107 (52%) | 1,279B | 960M |
| VM 0.8x | 23.02 | 22.93 (**−4.96pp**) | 1.73 ↓ | 1.50 ↓ | −15.2 | 0.778 | 2049/3107 (66%) | 1,274B | 955M |
| VM 1.2x | 25.68 | 25.52 (**−2.37pp**) | 1.75 ↓ | 1.50 ↓ | −17.0 | 0.932 | 1106/3107 (36%) | 1,158B | 868M |

**VERDICT: FAIL mọi điều kiện PASS trừ MaxDD → H3 ĐÓNG.** DD-cutter **chạy đúng cơ học** (MaxDD nông đơn điệu theo target: baseline −17.6 → 1.2x −17.0 → 1.0x −16.1 → 0.8x −15.2; và CAGR giảm đơn điệu khi de-risk mạnh hơn → KHÔNG phải bug, đúng dạng vol-target thật). Nhưng: **(1) OOS Sharpe GIẢM cả 3** (gate cần TĂNG) ❌; **(2) OOS Calmar GIẢM cả 3** (1.58→1.50, gate cần TĂNG) ❌; **(3) CAGR give-up −2.4…−5.0pp OOS** (gate ≤0.5pp) ❌ vượt 5-10×; **(4) MaxDD nông hơn** ✓ (điều kiện DUY NHẤT đạt — không đủ); **(5) IS không âm** (CAGR 26.74→24-25, không âm; IS Calmar thực ra TĂNG 2.01→2.17 vì scaling co DD-nhỏ giai đoạn calm — chính là cái bẫy: cải thiện nằm ở DD benign IS, KHÔNG ở OOS risk-adjusted); **(6) turnover-cost-adjusted:** overlay fire **36-66% MỌI phiên** (1,110-2,058 vol-resizes), turnover ~1,160-1,280B trên book 50B (~2×/năm thêm), TC tích lũy 868-960M VND — nhưng **TC KHÔNG phải thủ phạm chính**: kể cả TC=0, give-up vẫn áp đảo vì opportunity cost chạy 78-93% invested (mean m). **Self-check 0 VND cả 3** (BAL/LAG cash-flow identity 0 + `combination_replay_err_vnd`=0.0 replay 3-sleeve độc lập; max gross combined **1.000** = cap ≤1.0 xác nhận, borrow 0). **Root cause (định lượng):** cửa sổ high-vol của book BAL momentum KHÔNG trùng đủ với cửa sổ low-return của nó ở VN — tradeoff vol/return gần TUYẾN TÍNH nên scale 1/σ chỉ co return tỉ lệ → Sharpe gần như đứng yên, Calmar/CAGR rớt (compounding drag + TC). Lợi ích crash-protection kiểu Barroso KHÔNG hiện ra vì **DT5G đã lo phần de-risk regime tail**; chồng thêm 1 overlay vol chỉ rỉ máu return ở phiên vol-thường. **= Cederburg 2020 OOS-failure tái hiện trên dữ liệu VN, đúng như dự đoán, KHÔNG phải bug.** Env giữ **OFF-default** (baseline byte-identical), KHÔNG đề xuất wire. Artifacts: `data/volmanage_h3_logs/` (4 log + `compute_metrics.py` + progress), CSV `..._volmanw126m{08,10,12}.csv`, code `pt_v23_audit_2014.py` L488-500/1743-1797/1956-1972.

---

## Exp-8 — RECOVERY_CAPIT_ONLY (wait-for-capitulation deploy + MGE=1.3) — 2026-06-24 (Tier-3 BQ, 0 VND)

**Concept:** V2.4-LF instant-deploys on `pb_z≤−0.5`; Exp-8 idles parking until a **volume capitulation spike**
(`Volume[T]/mean[T−BASE..T−1] ≥ 1.7x`) then snaps to depth-scaled full T+1 + HOLDS; 1.3x lever on CAPIT washout arm.

**Calibration (Step1):** 1.7x catches all 6 crises (COVID/2022/2018/2016/2023/2025) at BOTH 63d(3M, fires 2.7%≈P97)
and 126d(6M, 4.3%≈P97). 1.8x misses 2016/2023.

**Results (same-snapshot 2026-06-24, cite DELTA — baseline drifted from brief's 30.63 to 28.04 via VVS/VCS/DTD corp-actions):**

| config | FULL CAGR | Sharpe | MaxDD | Calmar | OOS CAGR | OOS Cal | selfcheck |
|---|---|---|---|---|---|---|---|
| Baseline V2.4-LF (instant, LF) | 28.04% | 1.69 | −31.5% | 0.89 | 30.28% | 0.96 | 0 |
| **Test A — 3M/63d 1.7x + MGE 1.3** | **31.07%** | **1.87** | **−20.5%** | **1.52** | **35.82%** | **1.75** | **0** |
| Test B — 6M/126d 1.7x + MGE 1.3 | 30.14% | 1.81 | −26.3% | 1.14 | 33.97% | 1.29 | 0 |

**Verdict:** 🟢 **Test A (3M) STRONG WINNER** — beats baseline on EVERY metric in EVERY sub-period
(FULL +3.03pp CAGR / +11pp MaxDD / +0.63 Calmar; OOS +5.54pp/+11pp/+0.79; IS +0.58pp, equal DD).
Dominates Test B. Sidesteps early-decline DD by waiting for the capitulation print, deploys at the bottom
+ 1.3x lever on recovery. **REAL leverage → Spyros sign-off + user approval before LIVE; go-live stays LF unless promoted.**
Detail: `data/exp8_capit_only_bq.md`.

### Exp-8 REVISED — reversal-signal triggers A/B/C (Mike exp8-revised + user Q1/Q2/Q3) — 2026-06-24 (Tier-3 BQ, 0 VND)

Revised task expanded the CAPIT-ONLY trigger from vol-only to 3 signals (A=vol-spike, B=RSI oversold-reversal,
C=RSI bullish-divergence); gate unchanged (CRISIS/BEAR + pb_z≤−0.5). Same-snapshot 2026-06-24, all 0 VND:

| config | FULL CAGR | Sharpe | MaxDD | Calmar | vs A_1.7x |
|---|---|---|---|---|---|
| Baseline V2.4-LF | 28.04% | 1.69 | −31.5% | 0.89 | — |
| **A — vol 1.7x (WINNER)** | **31.07%** | **1.87** | **−20.5%** | **1.52** | — |
| A — vol 1.6x (Q2) | 30.14% | 1.81 | −26.3% | 1.15 | −0.93pp, worse DD |
| A∨B — +RSI-reversal | 31.07% | 1.87 | −20.5% | 1.52 | ±0.00 neutral |
| A∨B∨C — full combo | 29.54% | 1.77 | −29.7% | 0.99 | −1.53pp, −9.2pp DD |

**Answers:** **Q1** — 14 deep episodes 2011+; A timing inconsistent (COVID/2013 −12d good; 2011-12 grinds
−129/−166d too early; 2022 +16d late). B rare+precise (COVID bottom +1d), C early/noisy. **Q2** — 1.6x WORSE
(deploys ~3d earlier into COVID crash; 1.6x=P97 only for 21d base, 1.7x=P97 for 63d base) → keep 1.7x. **Q3** —
B NEUTRAL (+0.00pp; opens no new 2014+ episode, subsumed by A; value only pre-harness 2011-13 → keep as cheap
no-volume insurance), C HARMFUL (−1.53pp; fires pre-crash → leveraged early entry) → reject C.
**Verdict:** 🟢 Signal A vol-1.7x/3M ALONE wins = Exp-8 Test A unchanged. Detail `data/exp8_reversal_signals_bq.md`.

### Exp-8 — FORCE_REAL_LEVER measurement (A∧C-confirm K=40, MGE=1.3) — Mike dispatch — 2026-06-25 (Tier-3 BQ)

Goal: force genuine >100% gross (`FORCE_REAL_LEVER=1`, new env knob — scales the WHOLE cash-funded CAPIT
slug by MGE instead of adding a borrow HEADROOM that almost never binds) to MEASURE the true real-borrow cost.
Config: `RECOVERY_CAPIT_ONLY=1 RECOVERY_CAPIT_VOL=1.7 RECOVERY_CAPIT_BASE=63 RECOVERY_SIG_C=1
RECOVERY_C_CONFIRM=1 RECOVERY_C_ARM_K=40 MGE=1.3 MGE_CAPIT_ONLY=1 FORCE_REAL_LEVER=1`.
(Env note: rebuilt `data/earnings_surprise_data.pkl` from BQ — old pkl was `datetime64[us]`, unloadable under
linux pandas 2.3.3/numpy 1.26.4; re-pull is deterministic quarterly NP, identical values, now `[ns]`.)

| metric | FORCE_REAL_LEVER=1 | baseline A∧C-confirm K40 (headroom, no force) |
|---|---|---|
| FULL CAGR | **23.60%** | 31.81% |
| Sharpe(252) | 1.75 | 1.92 |
| MaxDD | **−18.0%** | −20.6% |
| Calmar | 1.31 | 1.54 |
| Final NAV (50B start) | 702.46B | — |

**Total real borrow interest = 45.92M VND** over 12.47y (BAL 0 / LAG 45.92M); max gross BAL 1.000 / **LAG 1.124**
/ **combined 1.000**; borrow-days BAL 11 / LAG 83. **Selfcheck:** final-NAV identity = **0 VND both books** (audit
pass); cash-flow per-session max err BAL 0 / LAG 3.10M VND (~8.5e-6 of the 362B LAG book, real-margin path residual,
washes out — final NAV exact). Audit CSV `data/v23_golive_audit_2014_now_mge130cap_real.csv` (13,463 rows).

**Verdict:** even when FORCED, real >100% leverage barely materialises — combined gross caps at **1.000** (the two
25B books net out; only LAG momentarily hits 1.124), so total borrow over 12.47y is a trivial **45.9M VND** (~0.0007%/yr).
Forcing the ×1.3 slug-scaling is NET-NEGATIVE on returns (CAGR 31.81→23.60, −8.2pp) for ~zero financing benefit —
it is a SIZING/path-drag distortion, not financing. Directly confirms the prior "MGE=1.5 loses = sizing not borrow"
finding at a stronger setting: **real leverage is not the lever**; keep MGE as the cash-funded CAPIT headroom (rarely
binds), do NOT force genuine margin. MaxDD did tighten (−20.6→−18.0%) but at a heavy CAGR cost (Calmar 1.54→1.31 worse).

### Exp-8 MGE sensitivity (Test A frozen: 3M/63d 1.7x, CAPIT-ONLY) — Mike dispatch — 2026-06-24 (Tier-3 BQ, 0 VND)

Sweep MGE ∈ {1.2, 1.3, 1.4, 1.5}, everything else = Exp-8 Test A best config. selfcheck 0 VND all 4 runs.
MGE=1.3 control re-run reproduced published Test A exactly (FULL 31.09/−20.5/1.52) → command verified.

| MGE | FULL CAGR | Sharpe | MaxDD | Calmar | OOS CAGR | OOS Cal | selfcheck |
|---|---|---|---|---|---|---|---|
| 1.2 | 31.08% | 1.88 | −21.5% | 1.44 | 36.05% | 1.67 | 0 |
| **1.3** | **31.09%** | **1.87** | **−20.5%** | **1.52** | **35.85%** | **1.75** | **0** |
| 1.4 | 30.98% | 1.86 | −20.5% | 1.51 | 35.36% | 1.73 | 0 |
| 1.5 | 30.93% | 1.86 | −20.5% | 1.51 | 34.82% | 1.70 | 0 |

**Answer:** Diminishing return = YES (mild); cliff = NONE — robust plateau. FULL Calmar & OOS Calmar both
**peak at MGE=1.3**; 1.3→1.5 loses CAGR (borrow drag, −0.16pp FULL / −1.03pp OOS) with no DD benefit (DD flat
−20.5%, binding window = pre-capitulation decline, leverage-independent). **Verdict: keep MGE=1.3** (sweet spot);
raising toward 1.5 is pure downside (more real leverage, less return). REAL leverage → Spyros sign-off + user
approval before LIVE. Detail: `data/exp8_mge_sensitivity_bq.md`.

### Exp-8 v2 — refined Signal C as CONFIRM (user idea + DT5G BullDvg) — 2026-06-25 (Tier-3 BQ, 0 VND)

User: C is early but flags "bottom approaching" → use as leading ARM, A = capitulation confirm (never deploy C alone).
Refined C per DT5G `_BullDvg`: RSI[T]>RSI[T−63]+0.02 ∧ Close[T]≤Close[T−63]×1.06 ∧ rolling-63d RSI-min<0.40 ∧ RSI<0.60.
Deploy = (A∨B) ∧ C-armed-within-K. Same-snapshot 2026-06-25, all 0 VND:

| config | CAGR | Sharpe | MaxDD | Calmar | vs A-only |
|---|---|---|---|---|---|
| A-only 1.7x | 31.07% | 1.87 | −20.5% | 1.52 | — |
| **A∧C-confirm K=30** | **31.31%** | 1.91 | −20.6% | 1.52 | +0.24pp, =DD |
| **A∧C-confirm K=40** | **31.81%** | 1.92 | −20.6% | 1.54 | +0.74pp, =DD |

**Verdict:** 🟢 A∧C-confirm SUPERSEDES A-only — C-confirm suppressed premature 2022 levered fires (A-only
11-16→12-06 → A∧C only confirmed 12-06) → higher return at equal DD; COVID preserved; and FIXES the 2012
slow-grind early-fire (A-only −166d → A∧C −4d, pre-harness = the Spyros tail-risk, closed at 0 in-sample cost).
Reverses v1 "C harmful" (that was C-as-standalone-trigger w/ crude 10d divergence). K=30 conservative default.
Real leverage MGE 1.3 → Spyros + user before LIVE. Detail `data/exp8_reversal_signals_bq.md`.

### Exp-8 — WHY MGE=1.5 loses 1.03pp OOS CAGR vs 1.3 (user Q via Mike) — 2026-06-25 (decomposed from sweep CSVs, 0 VND)

User: MGE1.5 loses 1.03pp OOS CAGR (35.85→34.82) ≈ 4× the ~0.26%/yr borrow-drag estimate — why? **Answer: the
premise is wrong — the gap is NOT borrow drag; it is a position-SIZING tilt with negative path return.**
- **Leverage almost never fires:** combined gross max **0.995 (1.3) / 0.966 (1.5)** over the WHOLE 2014-2026 run —
  book is cash-covered always. Actual OOS borrow interest: **1.3 = 0 VND; 1.5 = 2.73M VND / 2 borrow-days in 6.5yr
  = 0.0002 %/yr** (~1000× smaller than 0.26%/yr; the estimate prices a borrow that never happens).
- **What MGE is here:** `MGE_CAPIT_ONLY` = an arm SIZE-CAP multiplier funded from idle cash, not >100% financing.
  1.5 deploys a bigger CAPIT recovery position (+13–25B more stocks in 2020-Aug / 2021-Mar up-legs; unwinds −17/−25B in 2021 H2).
- **Mechanism = gain-then-larger-giveback (volatility/path drag), compounded.** navratio 1.5/1.3 ran **+1.59% (2021-03-31)
  → −2.03% (2021-12-31) → −4.79% (2026-06-19)**. Per-yr gap (pp): 2020 +0.25 / **2021 −2.31** / 2022 −0.47 / 2023 +0.06 /
  2024 −0.25 / 2025 −0.56 / **2026-H1 −1.63**. Lumpy & episode-bound (the opposite of a flat 10%/yr carry).
- **Hypotheses:** (1) arm worse in sub-periods = YES, primary. (2) compounding×volatility = YES. (3) capacity/150% gross
  = NO (gross never near 150%, cash-covered). (4) CAPIT_STOP early exit = MINOR (36 vs 34 stops; path artifact).
- **Verdict:** confirms MGE=1.3 sweet spot; MaxDD pins −20.5% flat 1.3→1.5 (no real >100% tail). Past 1.3 you buy MORE
  of a tilt with negative path-return for ~zero financing benefit. Detail: `data/exp8_mge_why_15_loses.md`.

### ⚠️ CORRECTION (2026-06-25, user-verified) — Exp-8 "MGE 1.3" config borrows 0 VND; it is LEVERAGE-FREE

User skeptic-checked the A∧C-confirm K30 MGE1.3 config. Measured from the audit CSV (`...capitonly63cv17Ccf30.csv`):
- **Total borrowed = 0 VND** (BAL & LAG cash min = 0; 26 "cash<0" days are exactly-0 rounding, deepest 0 VND).
- **Total interest 12.5y = 0 VND.** **Gross exposure max = 1.0000** — never exceeded 100%.
- Every CAPIT deploy (2020-03-12 g0.962 / 2020-04-21 / 2022-12-06 g0.951 / 2023-04-06 g0.957) funded from
  **parked idle cash** (cash stayed positive) — no borrow.

**Root cause:** CAPIT-ONLY deploys only in CRISIS/BEAR capitulation = when the book is cash-heavy (custom30
de-risked), so there's always enough cash; gross stays ≤ WMAX 0.95; the MGE 1.3 cap never binds. It would only
bind if the book were already ≥100% invested when CAPIT fires — which never happens in a crisis.

**Reframe:** in CAPIT-ONLY mode, `MGE` is a **CAPIT sizing multiplier** (raises the washout-arm deploy weight,
funded from cash), **NOT real leverage**. Consistent with FORCE_REAL_LEVER (forcing it → only 45.9M VND/12.5y)
and the MGE-sensitivity finding (gap = sizing/path-drag, not borrow). **The 31.31% A∧C-confirm result is
LEVERAGE-FREE (0 VND borrowed)** → no margin risk to clear with Spyros for THIS config. Prior "REAL leverage
MGE 1.3" labels on Exp-8 decisions are corrected to "nominal MGE cap, non-binding / sizing knob".

---
## 🆕 S2 LEVER-AT-BOTTOM via margin-able PARKING (Taylor 2026-06-25) — overturns "structurally infeasible"
> Engine rebuild: parking vehicle (custom30V) made MARGIN-ABLE (`simulate_holistic_nav.py` step 6c `etf_lever_by_date`). On A∧C-confirm deep-bottom days, inject a levered custom30V buy = frac×NAV funded by BORROW (cash<0 → gross>1), capped by MGE, protected by the S4 margin-call, unwinds via the 4c prefill sell. This is the production realization the earlier (b)-thread wrongly called impossible. ALL margin knobs gated OFF by default.
- **LEVER cmd:**
  ```bash
  BQ_CACHE_THREADS=1 RECOVERY_PARK=1 RECOVERY_WMAX=0.95 RECOVERY_PBZ_DEEP=-0.5 RECOVERY_CAPIT_ONLY=1 \
  RECOVERY_CAPIT_VOL=1.7 RECOVERY_CAPIT_BASE=63 RECOVERY_SIG_C=1 RECOVERY_C_CONFIRM=1 RECOVERY_C_ARM_K=30 \
  RECOVERY_LEVER_PARK=1 RECOVERY_LEVER_FRAC=0.30 MGE=1.3 MGE_CAPIT_ONLY=1 MARGIN_CALL=1 MGE_HARD=1.45 MGE_FLOOR=1.30 \
  NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" \
  AUDIT_END=2026-06-19 $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge
  ```
- **BASE (leverage-free, same recovery, drop RECOVERY_LEVER_PARK/MGE/MARGIN_CALL):** CAGR **28.91%** / Sharpe 1.81 / MaxDD −20.4% / Calmar 1.42 | self-check 0 VND. CSV `..._recpark95z50_depg75_capitonly63cv17Ccf30.csv`
- **LEVER:** CAGR **30.10%** / Sharpe **1.85** / MaxDD **−20.4%** / Calmar **1.47** | self-check **0 VND** (BAL+LAG) | S2 fired **4 bottom-dates**, max gross **1.27**, borrow 336.6M. CSV `..._recpark95z50_depg75_mge130cap_capitonly63cv17Ccf30.csv`
- **Δ = +1.19pp CAGR, +0.04 Sharpe, MaxDD IDENTICAL, +0.05 Calmar** — adds return WITHOUT extra drawdown.
- **Per-year:** edge concentrated 2014 (+7.77) / 2021 (+8.29, COVID-bottom payoff) / 2025 (+4.26); small drag 2024 (−3.24) / 2019 (−1.17) / 2022 (−1.08). Appears in BOTH IS(2014) and OOS(2021/25) — not regime-confined.
- **Caveats:** LOW-SAMPLE (4 bottoms/12y, edge rests on ~2 big correct calls); 1 snapshot; S4 margin-call did NOT fire (gross 1.27 < hard 1.45 — protection is insurance, untested here); needs A∧C-confirm + deposit-gate to avoid false bottoms. **Go-live default stays leverage-free; S2 = opt-in.** threads=1 deterministic.

### S2 follow-ups — MGE sensitivity + capacity + S4 stress (Taylor 2026-06-26, threads=1, self-check 0)
**MGE/lever-depth sweep @50B (frac = MGE−1):**
| MGE | CAGR | Sharpe | MaxDD | Calmar | gross | borrow |
|---|---|---|---|---|---|---|
| lev-free | 28.91 | 1.81 | −20.4 | 1.42 | 1.00 | 0 |
| 1.3 | 30.10 | 1.85 | −20.4 | 1.47 | 1.27 | 337M |
| **1.5 ⭐** | **30.32** | 1.85 | −20.3 | 1.50 | 1.48 | 639M |
| 1.7 | 30.04 | 1.84 | −19.9 | 1.51 | 1.69 | 858M |
→ **Optimal MGE 1.5** (peak CAGR). Plateau 1.3–1.5; **>1.5 degrades** (borrow drag outpaces return — 1.7 CAGR falls, 2021 payoff 93.78<97.37). MaxDD doesn't worsen (lever deploys AT the bottom, after the drawdown).

**Capacity (#10) — DECISIVE:** edge is capacity-bound. @50B LEVER +1.41pp; **@150B LEVER −0.95pp** (BASE 25.97 vs LEVER 25.02; gross still 1.48 but custom30V illiquidity at scale kills the recovery alpha). → **small-account feature (≤~50–100B); OFF above ~100B.**

**S4 stress (#8):** mechanics validated — tight cap (hard 1.10) → S4 fires, force-trims gross→floor, self-check 0. BUT at a sane cap (MGE+0.15) S4 rarely binds: the **regime-prefill unwind deleverages first** (state→CRISIS drops the parking target → sells the levered ETF). A wrong-way lever (bypassing the A∧C gate, levering the 2022 top) cost **MaxDD −20.4→−30.7%** → **the A∧C entry gate is the primary protection, S4 is the backstop.**

**Net verdict:** lever-at-bottom is real + auditable (0 VND), best at **MGE 1.3–1.5, NAV ≤~50–100B**, opt-in. **Go-live default stays leverage-free.**

---
## 🔴 #12 DEEP-DISCOUNT SINGLE-NAME SLEEVE — PROXY-GATE FAIL, do NOT escalate to harness (Taylor 2026-06-26)
Proxy `deep_discount_proxy.py` (cache threads=1, no NAV sim — the cheap gate per registry discipline "proxy first, only harness forms that beat base IS *and* OOS"). Event = QUALITY (ROIC5Y>0.08 & ROE_Min5Y>0 & FSCORE>=5) at own deep discount pbz=(PB−PB_MA5Y)/PB_SD5Y ≤ −1.5; fwd = profit_2M (T+40). Baseline-to-beat = SAME quality universe, non-discount (pbz>0).
- **SCALE BUG FOUND:** `profit_2M` is ALREADY in PERCENT (median 0.93%, p5 −21%, p95 +33%). The earlier `deep_discount_probe.py`/finding multiplied by 100 → reported means were 100× too big (e.g. "1058%"). Winrates unaffected (sign-based); means corrected here.
- **Q1 (IS<2020 / OOS≥2020 × DT5G state) — FAIL both-halves:** the NEUTRAL/BULL edge is **OOS-ONLY**.
  - NEUTRAL(3): deep IS **53.9%/1.37%** vs base **56.1%/4.35%** (deep WORSE in-sample); OOS deep 58.7%/3.34% vs base 50.9%/2.49% (better).
  - BULL(4): deep IS **42.0%/−1.57%** vs base 47.5%/−0.15% (worse, n=119); OOS deep 60.5% win vs 59.0% but **mean 4.55 < 7.25** (deep wins more often, smaller — base quality rallies harder in bull).
  - Where deep-disc DOES shine = CRISIS(1) OOS **78%** / BEAR(2) OOS **64%** — but that is exactly what **recovery-park / CAPIT already capture** (they fire in states 1,2). The "missed NEUTRAL/BULL" thesis does not survive the IS/OOS split.
- **Q2 (LAG additivity):** the LAG-orthogonal subset (YoY NP growth <0.15) actually carries the edge (OOS 62.2% > overlap 54.2%) → signal is orthogonal to LAG's earnings-momentum. A tick, but MOOT given Q1.
- **Q3 (value additivity vs custom30V's 1/PE):** within cheap_PE, deep_pbz 60.2%/**3.78** vs not_deep 57.6%/**5.05** (deep higher winrate but LOWER mean); within exp_PE deep_pbz 50.6% < not_deep 54.1% (deep WORSE). ⇒ own-pbz does NOT add return beyond cheap-by-PE; custom30V's `rank(1/PE)` already sits in the better cell.
- **VERDICT 🔴:** sleeve is **fragile (OOS-recovery-conditional, rests on ~2 dislocation episodes) AND redundant** — with recovery-park/CAPIT for the crisis states where it truly works, and with custom30V's 1/PE value rank for the calm states. Costs/turnover would only worsen it. **Per discipline → NOT escalated to a full pt_v23 harness; PARKED.** Considered-and-rejected refinement: have recovery-park pick single-name-pbz quality instead of the market basket — Q3 shows single-name pbz doesn't beat the 1/PE rank already used, so unpromising too.

---
## 🔴 #11 LIQUIDITY-TILTED custom30 @150B — REFUTED, keep production pool=60 (Taylor 2026-06-26, threads=1, all 0 VND)
Thesis: @150B custom30V parking is capacity-bound → tilt the basket toward liquidity (raise ADV) to free idle-cash deployment. Lever was the wrong fix (registry #10: lever @150B −0.95pp). Tested liquidity-tilt via the EXISTING `BASKET_CFO_POOL` knob (no code change): shrink the value-rank pool 60→30, progressively trading value-alpha for liquidity (pool=30 = pure top-30 liquidity). Absolute liquidity floor (`BASKET_LIQ_FLOOR_B` 10–20) was rejected as inert — gated rank-60 liq is already ~50–125 bn VND/day, the floor never binds.
- **Config:** `BQ_CACHE_THREADS=1 BASKET_CFO_POOL=<P> NAV_TOTAL_B=150 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" AUDIT_END=2026-06-19 $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge` (core V2.4 NEUTRAL-only, no recovery extras — isolates the parking-basket-liquidity variable). Logs `data/liqtilt_logs/`.

| pool | CAGR | Sharpe | MaxDD | Calmar | selfcheck |
|---|---|---|---|---|---|
| **60 (baseline=production)** | **24.54%** | **1.68** | **−15.0%** | **1.64** | 0 VND |
| 45 | 23.88 | 1.66 | −16.6 | 1.44 | 0 |
| 40 | 23.87 | 1.65 | −15.5 | 1.54 | 0 |
| 35 | 21.83 | 1.54 | −17.8 | 1.22 | 0 |
| 30 (pure top-30 liquidity) | 22.19 | 1.60 | −17.5 | 1.27 | 0 |

- **VERDICT 🔴 REFUTED:** liquidity-tilt is **monotonically worse** — baseline pool=60 dominates on EVERY metric; shrinking to more-liquid names loses 0.7–2.7pp CAGR AND worse DD/Calmar/Sharpe. The value-alpha given up (restricting the 1/PE rank to fewer names) exceeds any capacity relief gained.
- **REFRAME (the real insight):** the parking basket was NOT the @150B bottleneck — its top-60 pool is already liquid enough (rank-60 ≈ 50–125 bn/day). The ~3.5pp decay 50B→150B is dominated by the **STOCK BOOKS** (BAL momentum + LAG PEAD at ~75B/book hitting their own name-impact limits) — which liquidity-tilting the *parking* basket cannot fix. ⇒ keep production custom30V (pool=60, full value-rank); do not liquidity-tilt. Above ~100B the right response is accept the known capacity decay (or scale the stock-book breadth — separate work), not degrade the parking selector.
- Combined with #10 (lever @150B −0.95pp): **at 150B neither lever nor liquidity-tilt helps**; the strategy is simply capacity-bound at the stock-book level. Both are small-account features (≤~50–100B).

---
## 🟢 CRISIS-OPPORTUNITY AUDIT 2013→now — "are we missing good entries?" (Taylor 2026-06-26, `episode_recovery_audit.py`)
12 distinct VNINDEX drawdown troughs (local-min, dd≤−12%, confirmed by ≥+12% rebound). For each: fwd 6M/12M index return (the opportunity), valuation at trough (market PE 5y-pctile + liquid-universe median own-pbz = recovery-park's signal), DT5G state, and whether our deep-cheap re-risk gate (CRISIS/BEAR ∧ pbz_med≤−0.5) fires.

| trough | dd% | PE_pctile5y | pbz_med | state | fwd6M | fwd12M | recpark |
|---|---|---|---|---|---|---|---|
| 2014-05 | −15.4 | 0.26 | −0.46 | CRISIS | 17.3 | 7.0 | no |
| 2014-12 | −19.1 | 0.25 | 0.31 | NEUTRAL | 14.2 | 8.9 | no |
| 2015-05 | −17.4 | 0.03 | −0.03 | NEUTRAL | 14.1 | 17.7 | no |
| 2015-08 | −17.8 | 0.00 | 0.08 | NEUTRAL | 6.8 | 25.4 | no |
| 2016-01 | −18.6 | 0.01 | 0.17 | NEUTRAL | 25.7 | 31.7 | no |
| 2018-07 | −25.8 | **0.87** | −0.61 | NEUTRAL | −0.6 | 10.0 | no |
| 2019-01 | −27.1 | 0.46 | −0.69 | NEUTRAL | 11.4 | 9.3 | no |
| 2020-03 | −45.3 | 0.00 | −1.39 | BEAR | 37.5 | **76.4** | **YES** |
| 2022-11 | −40.3 | 0.00 | −1.07 | CRISIS | 16.9 | 20.8 | **YES** |
| 2023-10 | −32.7 | 0.15 | −0.51 | CRISIS | 21.6 | 21.1 | **YES** |
| 2025-04 | −25.9 | 0.05 | −0.75 | **BULL** | 49.9 | **55.4** | **no** ← gap |
| 2026-03 | −16.4 | 0.44 | −0.61 | NEUTRAL | 17.1 | 17.1 | no |

- **VERDICT: NOT missing meaningfully.** Two mechanisms cover the field: (a) in NEUTRAL/BULL we're already ~70–100% invested → we PARTICIPATE in those pullback-recoveries (2015-08, 2016-01, 2025-04) by default; (b) in CRISIS/BEAR we deploy idle cash when cheap. Of the 3 cheap CRISIS/BEAR troughs (2020/2022/2023) recovery-park caught **all 3** — the three deepest dislocations.
- **Gate is DISCRIMINATING, not just absent:** mean fwd12M where recpark fires **39.4%** vs **20.3%** where it doesn't. It correctly SKIPS low-payoff scares (2014-05 +7%, 2018-07 −0.6%/6M while **PE-pctile 0.87 = expensive despite −26%**, 2019-01 +9%) — chasing every −15% dip would be punished by these duds.
- **ONE GENUINE NARROW GAP = fast-crash-in-bull (2025-04 tariff):** deep-cheap (pbz −0.75 ≤ −0.5, PE-pctile 0.05) with a **+55% 12M** rebound, but recovery-park did NOT fire because the crash was too FAST for DT5G to leave BULL (state filter = CRISIS/BEAR only). We still PARTICIPATED at ~100% (fully invested in BULL, rode the recovery) — the only thing missed = LEVERING the bottom (S2/CAPIT lever, which is small-account ≤100B & risk-additive anyway). Among the 4 pbz-cheap-but-state-blocked troughs (2018-07/2019-01/2025-04/2026-03), only 2025-04 was a big-payoff miss; the others were correctly low-payoff → the state filter is mostly right.
- **Stock-pick nuance (positive):** this is INDEX-level participation; our recovery-park/custom30V deploys QUALITY+VALUE names, which historically rebound HARDER than the index (registry 2012 stock-pick: +40–83% vs index +16%). So realized capture ≥ the index fwd-returns shown.
- **Testable follow-up (offered, not built):** make the deep-cheap re-risk trigger **state-BLIND but capitulation-CONFIRMED** (A∧C-confirm vol-spike, regardless of DT5G state) → would catch 2025-04 without re-admitting the 2018/2019 NEUTRAL duds IF the vol-capitulation print distinguishes them. Caveat: n=1 bull-crash, lever is small-account, risk-additive → test before any claim.

---
## 🟢 STATE-BLIND + PE_pctile deep-cheap re-risk — validated refinement to the LEVER config (Taylor 2026-06-26, threads=1, all 0 VND)
User crisis-audit follow-up: drop the CRISIS/BEAR state filter on the recovery deploy/lever, replace with an ABSOLUTE-cheapness gate (VNINDEX_PE 5y-pctile≤0.20) alongside the existing own-pbz≤−0.5 — so deploy fires in genuine fear regardless of DT5G state, catching fast-crash-in-bull that the state filter blocks. **User insight (confirmed): pb_z alone does NOT separate traps** (2018-07 pb_z −0.61 & 2019-01 −0.69 both "cheap" by pbz) — **PE_pctile is the discriminator** (2018-07 PE_pct 0.87=expensive, 2025-04 PE_pct 0.05=cheap).
- **Proxy** `state_blind_gate_test.py` (causal daily event-study): G2 (state-blind & pbz≤−0.5 & PE_pct≤0.20) covers good troughs **4/4**, duds **0/2**, fwd6M mean **18.9% (100% positive)** vs state-gated G0 10.6%/3-of-4. pbz-only (G1) admits both duds. → escalate.
- **Code** (pt_v23, default OFF = byte-identical): env `RECOVERY_STATE_BLIND` + `RECOVERY_PE_PCT_MAX`; causal `_pe_pct_asof` (prior-month VNINDEX_PE 5y rolling pctile); gate `_state_ok = (st in 1,2) or (STATE_BLIND and pe_ok)`. CRISIS/BEAR stay eligible (no regression).
- **Harness @50B same-snapshot** (LF base `RECOVERY_PARK=1 WMAX=0.95 PBZ_DEEP=-0.5`; LEVER adds `CAPIT_ONLY=1 CAPIT_VOL=1.7 BASE=63 SIG_C=1 C_CONFIRM=1 ARM_K=30 LEVER_PARK=1 LEVER_FRAC=0.30 MGE=1.3 MGE_CAPIT_ONLY=1 MARGIN_CALL=1`):

| run | CAGR | Sharpe | MaxDD | Calmar | borrow | selfcheck |
|---|---|---|---|---|---|---|
| A LF state-gated (control) | 29.13 | 1.74 | −30.9 | 0.94 | 0 | 0 |
| B LF state-blind+PE | 29.14 | 1.74 | −30.9 | 0.94 | 0 | 0 |
| C LEVER state-gated (S2) | 29.75 | 1.82 | −20.6 | 1.45 | 297M | 0 |
| **D LEVER state-blind+PE** | **30.21** | **1.84** | **−20.6** | **1.47** | 396M | 0 |

- **VERDICT 🟢 (honest):** **LF state-blind = no benefit** (A≈B; in BULL/NEUTRAL already invested → no idle cash to deploy → needs lever). **LEVER state-blind = +0.46pp CAGR, +0.02 Sharpe/Calmar, MaxDD IDENTICAL −20.6%, 0 VND** — strictly dominates the state-gated lever. **Walk-forward: IS 2014-19 BYTE-IDENTICAL per-year** (state-blind never fires in-sample → no overfit, IS-inert); the entire edge is OOS and concentrates in **2023 (+6.04pp/yr)** — the post-SCB cheap recovery where state-blind+PE levered the NEUTRAL/BULL recovery days the state filter blocked (S2 lever dates 4→7: +2023-04/06/12). The motivating 2025-tariff case nets ~0 (already fully invested by the bounce). 
- **CAVEATS:** REAL margin (borrow 396M, gross 1.27 → **Spyros + user approval before LIVE**); **small-account only** (#10: @150B lever capacity-bound −0.95pp); opportunity-capture resting on ~1-2 OOS episodes (don't re-tune). **Go-live stays LEVERAGE-FREE — unaffected.** Recommendation: IF/when the S2 lever is deployed (small-account, post-go-live), use state-blind+PE — it strictly dominates state-gated. Default stays OFF.

---
## 🔴 KELLY-SIZED LEVERAGE + HOLD-AS-NEUTRAL — both REJECTED by backtest (Taylor 2026-06-26, threads=1, all 0 VND)
User: 'we borrow too little; size with Bayes+Kelly' + 'state-blind → assume NEUTRAL, hold the custom30V core through regime flips, only margin-call trims.' Built `kelly_lever_sizing.py` (Bayes-shrunk Kelly + MAE ruin cap) and `RECOVERY_HOLD_NEUTRAL` (floor parking at NEUTRAL weight in every state), swept MGE {1.3,1.5,1.8,2.0} @50B with state-blind + hold-neutral.
- **Kelly/Bayes analysis:** the bet (deep-cheap+capit, 4 episodes) IS high-quality — mean fwd6M 23.7%, std 10.9%, **Sharpe(6M) 2.17, win 100%, worst episode +11.2%**. Naive full-Kelly 15.6x; Bayes-shrunk half-Kelly 3.5–6.7x (still huge). **Binding constraint = margin-call ruin, not Kelly:** worst MAE63 = **−26.2%** (COVID fell another 26% AFTER the signal) → at 30% maintenance margin, max gross ~**2.0x**.

| MGE (+state-blind+hold-N) | CAGR | Sharpe | MaxDD | Calmar | gross | S4 fires |
|---|---|---|---|---|---|---|
| **D = MGE1.3, NO hold-neutral (KEEPER)** | **30.21** | **1.84** | **−20.6** | **1.47** | 1.27 | — |
| 1.3 + hold-neutral | 29.32 | 1.53 | −28.4 | 1.03 | 1.27 | 0 |
| 1.5 + hold-neutral | 28.13 | 1.47 | −29.3 | 0.96 | 1.49 | 0 |
| 1.8 + hold-neutral | 28.30 | 1.49 | −28.4 | 1.00 | 1.80 | 0 |
| 2.0 + hold-neutral | 27.97 | 1.47 | −28.4 | 0.99 | 2.00 | 0 |

- **VERDICT 🔴 BOTH REJECTED:**
  1. **Hold-as-neutral HURTS** (E vs D: −0.89pp CAGR, −0.31 Sharpe, **MaxDD −20.6%→−28.4%**) — flooring parking at 0.7 in EVERY state holds custom30V THROUGH crises = strips the de-risk that DT5G/parking provide. "Returns to neutral eventually" is true for the index but holding levered through the drawdown is path-punished (compound from a lower base + borrow accrues through the hold).
  2. **Higher leverage does NOT pay** — 1.3→2.0x monotonically WORSE (29.32→27.97%); S4 margin-call NEVER fires (gross < hard cap) so it's "safe" but return-negative. The system is **return-limited at ~1.3–1.5x, well below the ~2.0x ruin cap** — confirms+extends the prior "MGE>1.5 = sizing/path-drag, gain-then-larger-giveback" finding even with reduced forced-selling.
- **Why Kelly said 'big' but reality says 1.3x:** Kelly priced an ISOLATED single-shot bet (Sharpe 2.17 to a fixed horizon); the live portfolio compounds continuously — leverage interacts with the whole book's path (giveback + borrow carry + opportunity cost). The backtest captures this; Kelly doesn't. **Modest leverage (~1.3x) + KEEP crisis de-risk (no hold-neutral) is the disciplined answer.**
- **KEEPER unchanged = D (state-blind + PE gate + lever MGE 1.3, no hold-neutral): 30.21/1.84/−20.6/0 VND.** Go-live stays leverage-free. `RECOVERY_HOLD_NEUTRAL` kept OFF as a documented dead-end knob.

---
## 🟡 CLEAN MGE sweep config D (state-blind+PE, NO hold-neutral) @50B — full 4-point curve (Taylor 2026-06-27, stable cache, all 0 VND)
CORRECTION: an earlier 2-point read (1.3/1.5 only, on an incomplete cache missing financial rows) led me to over-extrapolate "1.3≈1.5, higher MGE useless." The full 4-point curve on the corrected/stable cache (ticker_prune 753,172 + financial 66,386 + all time=DATE, post Winston fix) REFUTES that.

| MGE | CAGR | Sharpe | MaxDD | Calmar | gross | S4 |
|---|---|---|---|---|---|---|
| 1.3 (Spyros-approved) | 30.07 | 1.82 | −20.6 | 1.46 | 1.27 | 0 fires |
| 1.5 | 30.02 | 1.81 | −20.3 | 1.48 | 1.48 | 0 fires |
| 1.8 | 29.96 | 1.82 | −19.9 | 1.50 | 1.80 | 0 fires |
| **2.0** | **30.44** | **1.83** | **−19.1** | **1.60** | 2.00 | 0 fires |

- **2.0 dominates in-sample** (best CAGR/DD/Calmar). MaxDD IMPROVES monotonically with leverage (−20.6→−19.1) — mechanical: the lever deploys AFTER the A∧C capitulation (post-drawdown) so it amplifies the recovery, not the fall; S4 never fires (gross caps cleanly).
- **BUT the edge is LUMPY** (per-year 1.3→2.0): +8.7pp 2014 / +6.9pp 2020 (the big crisis-bottom lever payoffs) but −3.0pp 2021 / −1.2pp 2022 / −3.7pp **2026-H1** (worse in the most recent regime, near go-live). Sharpe ~flat (1.82→1.83) = extra return bought with extra lumpiness. Profile = opportunity-capture (n~2 big episodes), not a smooth edge.
- **BINDING question = OUT-OF-history tail at gross 2.0:** a crash worse than COVID (MAE < −26%, the historical worst) would force-sell hard at gross 2.0 — backtest can't show it. Spyros approved only 1.3 (S4 fires −31.5% from entry). **MGE 2.0 dispatched to Spyros for tail re-review.**
- **Taylor lean (pending Spyros):** **MGE 1.5** as robust default (captures most DD/Calmar gain −20.3/1.48, modest real leverage, far less tail than 2.0); **2.0 = aggressive opt-in IF Spyros clears the gross-2.0 tail AND lumpy/worse-2026-H1 accepted**; **1.3 = conservative Spyros-cleared floor**. Go-live stays leverage-free regardless.

---
## 🔴 #18 DUAL-VEHICLE pbcombo (1/PB-heavy at bottoms) — harness REJECTS (worse risk-adjusted), keep yieldcombo (Taylor 2026-06-27, 0 VND)
Wired regime-conditional deploy vehicle: base parking = yieldcombo, deep-cheap deploy-HOLDING days = pbcombo (0.67·1/PB+0.23·1/PCF+0.10·1/PE, crisis-IC weights). Built at basket-build, spliced AFTER the recovery loop on the actual deploy-holding dates (mirror BULL_VEHICLE_C30B). Env `BOTTOM_VEHICLE_PBCOMBO`, default OFF = byte-identical. Spliced 194 deep-cheap deploy-holding days (all 2020+).
- **@50B MGE1.5 (state-blind+PE), same-snapshot, both self-check 0:**

| | CAGR | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|
| OFF (yieldcombo) | 30.02 | 1.81 | −20.3 | **1.48** |
| ON (pbcombo bottoms) | **30.48** | 1.84 | **−22.3** | 1.37 |

- **VERDICT 🔴 REJECT:** pbcombo deploy = **+0.46pp CAGR but MaxDD −20.3→−22.3 (deeper) and Calmar 1.48→1.37 (WORSE).** Per-year: 2020 COVID −4.3pp (deep-value falls harder in the crash) / 2021 +10.9pp (rebounds harder) — 1/PB names have higher path volatility. The #18 proxy (+1.25%/deploy-day forward return) was REAL but only measured RETURN; the harness exposes the path/DD cost the proxy missed. Risk-adjusted WORSE → not worth +0.46pp CAGR for +2pp drawdown, especially with Spyros risk-first (he rejected MGE 2.0 for the same path-risk logic).
- **KEEP yieldcombo as the deploy vehicle.** `BOTTOM_VEHICLE_PBCOMBO` + `pbcombo` selector kept OFF as a tested-and-documented dead-end (like RECOVERY_HOLD_NEUTRAL). Optional unexplored: a LIGHTER 1/PB tilt (e.g. 0.3 PB) might trade less DD for less return — not pursued (tuning risk + Spyros risk-first + go-live proximity).
- **Meta:** 3rd time this session a return-positive proxy/in-sample signal failed on the risk-adjusted/path dimension (hold-neutral, MGE 2.0, pbcombo). Pattern: chase Calmar/path-robustness, not raw CAGR.

---
## 🟢 V2.4-L BLOCKERS B3 + B4 — implemented + verified (Taylor 2026-06-27, self-check 0)
- **B3 NAV≤100B lever auto-disable** (Spyros condition + #10 capacity): engine `lever_nav_cap` param checks prior-session NAV per lever-date, skips the inject when NAV>cap; pt_v23 `LEVER_NAV_CAP_B` (default 100). Dynamic (works as live NAV grows). **Verified @MGE1.5 yieldcombo:** @150B → gross **1.000** (lever fully OFF, start>cap) ✓; @50B → gross 1.197 (levers only early <100B bottoms, auto-off on 2023/2025 high-NAV bottoms). @50B CAGR **30.05** ≥ uncapped 30.02 (drops capacity-bound late levers that don't help) — safer AND marginally better. Default-safe; engine `lever_nav_cap=None` = byte-identical for non-lever runs.
- **B4 PE-freshness fail-closed:** `_pe_pct_asof` returns NaN when prior-month VNINDEX_PE absent OR feed stale >`RECOVERY_PE_MAX_AGE_M` (2) months → `_pe_ok=False` → state-blind lever DISABLED → falls to leverage-free. Inert historically (PE always fresh → byte-identical); it is the LIVE feed-freeze guard.
- **V2.4-L final @50B (all gates on, MGE1.5, yieldcombo deploy): CAGR 30.05 / Sharpe 1.82 / MaxDD −20.1 / Calmar 1.49 / self-check 0.**
- **Blocker status:** B2 (Spyros episode breaker −15%) DONE; B3+B4 DONE+verified; **B1 (Mafee DNSE margin account / loan_package_id) = only remaining** → if cash-only, V2.4-L runs paper, core V2.4 lives leverage-free.

---
## 📛 NAMING (user 2026-06-27): **V2.5 = V2.4 + leverage** — canonical
- **V2.4** = leverage-free core (custom30V NEUTRAL-only parking + recovery-park leverage-free). **Go-live 2026-06-30.**
- **V2.5** = V2.4 + the LEVERAGE layer (was "V2.4-L"; renamed for simplicity). The ONLY difference vs V2.4 = leverage.
  - = state-blind + PE-gate recovery-LEVER, **MGE 1.5** (Spyros-approved, MGE_HARD 1.65), deploy vehicle = yieldcombo (pbcombo rejected), + safety stack: 4 entry-guards + episode breaker −15% (Spyros) + NAV≤100B auto-disable (B3) + PE-freshness fail-closed (B4).
  - **Account: 0002023347** (DNSE RocketX margin, loan_package_id=1840, borrow 12.5%/yr, 28 custom30V eligible collateral) — user-confirmed 2026-06-27.
  - **@50B: 30.05% / Sharpe 1.82 / MaxDD −20.1 / Calmar 1.49 / self-check 0** at real 12.5% borrow (lever net +1.00pp vs leverage-free).
  - Risk layering (Mafee-confirmed): Spyros −15% NAV → S4 internal ~−31% NAV → DNSE call −44.4% **portfolio** (=−66.7% NAV @1.5x). System always cuts well before the broker.
  - **Status:** R&D-complete, all 4 blockers cleared. Live-activation = POST-go-live (needs live-recommend integration). Go-live 2026-06-30 = V2.4 leverage-free, unaffected. All V2.5 env knobs default OFF = byte-identical.

## 2026-06-27 — Earnings Responsiveness Beta for LAG/PEAD (Taylor)
**Q:** Should LAG (PEAD book) add a filter favoring stocks that react strongly+correctly to earnings?
**Data:** 22 liquid VN large-caps (custom30V core: banks+HPG/DGC/VHC/FPT/MWG/PNJ...), 924 clean earnings events 2015–2026.
**Method (look-ahead-safe):** SUE proxy = `NP_R` (seasonal-random-walk YoY surprise, NP_P0/NP_P4−1, require NP_P4>0, winsor ±200%). Anchor = `ticker_financial.Release_Date`. react_adj = (Close[+5]/Close[pre]−1) − VNINDEX same window; drift_adj = (Close[+40]/Close[+5]−1) − VNINDEX. Responsiveness beta = OLS slope react_adj~SUE per ticker. CSV: /tmp/earnings_events.csv (regen via BQ query in job Taylor_20260627_065705).
**Results:**
- Responsiveness beta WEAK: mean R²=0.058, only 5/22 names |t|>2. Top responders = big banks (CTG/VCB/MBB), not low-coverage names.
- PEAD drift (pos-SUE tercile, +5→+40d, mkt-adj): LO-responsiveness group +4.97% (t=3.78) vs HI-responsiveness +1.02% (t=1.19, ns). PEAD spread pos−neg: LO +2.93pp (t=1.86) vs HI −0.36pp. → filter runs OPPOSITE to hypothesis (under-reaction → drift).
- Effect is mean-driven/outlier-skewed: baseline pos-SUE drift mean +3.05% but **median +0.66%, %>0=53%** (≈coin-flip); pos-vs-neg median gap ~0. corr(react_adj,drift_adj)≈0 (no event-level continuation).
**Verdict: NO** — do not add high-earnings-responsiveness filter to LAG. Theoretically backwards (PEAD = under-reaction anomaly) and empirically too noisy in liquid universe (PEAD weakest where coverage/liquidity highest — KB illiquidity premium <1B ADV). **CONDITIONAL next lever:** if an earnings tilt is wanted, tilt on **fresh high-SUE** (NP_R top tercile + sessions-since-Release_Date < drift window), NOT responsiveness — and backtest in the actual (broader/less-liquid) LAG universe first; median-flat PEAD here means it needs proper validation.

---

### custom30B BULL-parking vehicle — walk-forward @1B/5B (Taylor 2026-06-27, job Taylor_20260627_103040)
Mike dispatch: at go-live scale (1B-5B), does custom30B out-park custom30V (and cash) in DT5G BULL/EXBULL periods; lower the 150B bull-park threshold? **Method:** isolated BULL-days-only basket return (NOT full V2.4 blend). build_pit top30/gate≤3/q2m5/namecap0.10. custom30V=yieldcombo; custom30B=pemom MOM_W=1.0 LIQ_FLOOR_B=5 (R6 spec). DT5G state from `vnindex_5state_dt5g_live`, bull mask {4,5}. Cash=0%. CAGR annualised over BULL-time only.
- **Script:** `c30b_bull_walkforward.py` | **CSV:** `data/c30b_bull_walkforward.csv` (per-day V/B/cash bull returns) | AUDIT_END=2026-06-19 | **self-check:** custom30B FULL cum recomputed from CSV = 305.2250% vs in-mem 305.2250% (diff 3.2e-12pp ≈ 0) ✓ | BQ_CACHE_THREADS=1.
- **Bull-days in window:** 465 total. **IS 2014-19 = 53 days (≈only 2018 melt-up; 2014/15/16/19 had ZERO bull days)**; OOS 2020-26 = 412 (2021 alone=183). → structurally only ~1 distinct IS bull regime → weak walk-forward by construction.
- **Metrics (CAGR bull-time / Sharpe / MaxDD):** FULL custom30V 87.35%/2.41/−20.8, custom30B 113.47%/2.75/−20.3 (**B−V +26.1pp/+0.34Sh**). **IS** V 278.75%/4.38, B 270.80%/4.11 (**B−V −7.95pp/−0.27 — B LOSES IS**). **OOS** V 71.13%/2.12, B 98.83%/2.54 (**B−V +27.70pp/+0.43 — B WINS OOS**). Both vehicles ≫ cash (cash=0% in bull).
- **Capacity:** NON-binding at go-live. Basket 60-sess ADV ~9–11 **trillion** VND; deploy@1B≈210M total / 21M max single name, @5B≈1050M/105M; per-name 20%-ADV cap ~60–73B ⟹ OK by ~1000×. The 150B gate is NOT a capacity constraint at 1-5B.
- **TC:** per-rebalance turnover V=33.5% / B=30.2% → ~0.24–0.27%/yr drag (quarterly, 2-side, 10bp). Negligible.
- **VERDICT: custom30B vehicle = FAIL walk-forward / do-not-deploy.** Edge sign FLIPS IS(−8pp)→OOS(+28pp); full-period +26pp is entirely the single 2020-21/2024-25 bull regime (regime-luck), not a robust selection edge — consistent with **THREAD(c)** (mom200 IC≈+0.002 in bull = ZERO; value 1/PE dominates) and **R6** (faithful full-system: B vs V +0.57pp @20B, WASH @50B). Reconciliation: +26pp bull-time × ~15% bull-fraction × ~0.21 deploy ≈ +0.8pp/yr full-system ≈ R6's +0.57pp @20B.
- **Threshold recommendation:** (1) Capacity allows bull-park at go-live 1-5B — 150B is a Sharpe/lumpiness gate, not capacity. (2) Default stays **bull-park OFF <150B = R3 NEUTRAL-only** (Sharpe 1.87>1.82, custom30B/V bull-park hurts 2024/25). (3) IF bull-park is ever enabled, use **custom30V** (robust value vehicle), NOT custom30B (no walk-forward-robust edge). Do not lower a threshold to deploy a non-robust feature.

## Delta/momentum signals — IC validation for 8L screener (2026-06-27, Taylor)
**Question:** Do "improving" stocks (positive delta) earn higher forward returns? Validate 4 delta signals.
**Method:** event-panel `/tmp/delta_panel.parquet` — ticker_financial deltas joined ASOF to first ticker_prune session ≥ Release_Date (no look-ahead; signal known at release, fwd return measured forward). Filters: gap≤15d, liq Trading_Value_1M_P50≥3bn. IC = Spearman(signal, profit_1M/2M) — profit_* TRAINING-ONLY, used for IC eval only. n≈7.8k events FULL / 4.2k in 8L rating≤3 (rating_8l.csv whitelist; caveat: snapshot membership → mild survivorship on universe, not on signal). IS=2014-19, OOS=2020-26.
**Signal defs (all: positive=improving):** d_FSCORE=FSCORE−FSCORE_P1; d_NPR=NP_R − NP_R(lag4Q) gated NP_P4>0 (earnings YoY *acceleration*); d_CashCyc=CashCycle_P4−CashCycle_P0 (cycle shortened), fin routes excl; d_Revenue=Revenue_YoY_P0−Revenue_YoY_P4 (rev accel).

| signal | univ | IC_2M | t | IS_2M | OOS_2M | consist | verdict |
|--------|------|-------|---|-------|--------|---------|---------|
| d_NPR | QUAL | 0.083 | 5.1 | 0.021 | 0.104 | 11/13 | **WIRE (strongest)** |
| d_FSCORE | QUAL | 0.057 | 3.7 | 0.017 | 0.073 | 10/14 | **WIRE** |
| d_Revenue | QUAL | 0.051 | 3.3 | 0.086 | 0.041 | 12/14 | optional (redundant w/ d_NPR, corr .34) |
| d_CashCyc | QUAL | 0.002 | ~0 | 0.009 | -0.007 | 7/14 | **REJECT** (no edge) |
| composite2 (z d_NPR+d_FSCORE) | QUAL | 0.073 | 4.7 | 0.014 | 0.097 | — | use for profit_1M; d_NPR alone best for 2M |

Quintile profit_2M (QUAL, monotonic): d_NPR Q1=1.71% Q3=4.58% Q5=6.02% (+4.3pp); d_FSCORE +2.8pp; composite +4.0pp.
**Caveat:** edge concentrated OOS (2020+); IS weak/near-zero for all (regime: post-2020 VN reacts more to earnings). But these are raw economic deltas (NO param fit) → not overfit; PEAD/earnings-momentum is robust anomaly.
**Wiring:** d_NPR (primary) as a SEPARATE `delta_momentum` column → use as tiebreaker sort within a rating bucket and/or bounded ±1 sub-rank notch (never cross rating tiers). Do NOT fold into value_score (contaminates value axis). d_NPR overlaps LAG/PEAD SUE (level) but is acceleration (2nd deriv) — novel use in 8L = quality-trajectory tiebreaker. Live signal uses only point-in-time financials (no profit_* leak).

## Delta_momentum WEIGHT TILT inside custom30V parking basket — IS/OOS backtest (2026-06-27, Taylor, job Taylor_20260627_111639)
**Q (Mike dispatch):** Does tilting custom30V intra-basket weights toward improving-fundamentals names (ΔNP_R + ΔFSCORE, weights 0.6/0.4 from the IC study above) BEAT plain namecap custom30V in V2.4 NEUTRAL parking? WIRE only if BOTH OOS CAGR and OOS Calmar improve (no DD trade-off), net of extra intra-basket turnover.
**Script:** `data/delta_tilt_backtest.py` (new; NO production code touched) | AUDIT_END=2026-06-19 | DT5G state `vnindex_5state_dt5g_live`.
**Method:** `cb.build_pit(yieldcombo, quality=none, gate_rating=3, rebal=q2m5, weight_scheme=namecap)` called ONCE → baseline NAV + membership + raw panel. **Membership UNCHANGED by tilt** (top-30-by-yieldcombo stays; only weights move). PIT delta from `ticker_financial` as-of `Release_Date` (no look-ahead): d_NPR=(NP_P0/NP_P4−1)−(NP_P1/NP_P5−1) [req NP_P4>0 & NP_P5>0], d_FSCORE=FSCORE−FSCORE_P1. Per rebal: z-score within the 30 basket names → dm=0.6·z(dNPR)+0.4·z(dFSCORE) → tilt_factor=1+0.15·clip(dm,±2) (≤±30% weight adj), missing→1.0. NAV reconstructed by me for both variants; tilt pays EXTRA intra-basket turnover TC=0.5·Σ|w_tilt−w_cap|·TC each rebal. Same DT5G overlay + cost model as `custom30v_singlebook_faithful.py` (TC=0.3%, borrow 10%/yr, rebal_turn 0.35).
**Self-check:** reconstructed baseline (tilt_factor=1) vs build_pit level_dict → max daily-return abs diff **3.3e-16 ≈ 0** ✓.

| Window | Metric | Baseline | Delta_Tilt | Diff |
|--------|--------|----------|------------|------|
| FULL | CAGR% | 23.64 | 23.75 | +0.11 |
| FULL | Calmar | 1.19 | 1.21 | +0.02 |
| IS 2014-19 | CAGR% | 20.04 | 20.11 | +0.07 |
| IS 2014-19 | Calmar | 1.31 | 1.31 | −0.00 |
| OOS 2020+ | CAGR% | 27.06 | 27.21 | **+0.15** |
| OOS 2020+ | Sharpe | 1.42 | 1.42 | +0.01 |
| OOS 2020+ | MaxDD% | −19.9 | −19.6 | +0.3 |
| OOS 2020+ | Calmar | 1.36 | 1.39 | **+0.03** |

**Tilt footprint (why so small):** avg intra-basket weight MAE tilt-vs-cap = **0.132%**, avg one-way extra turnover/rebal = 1.98%, avg top-10 set changes/rebal = 0.38 names. The namecap (cap-weight, 0.10 cap) structure leaves almost no room — mega-caps already at the 10% cap can't tilt up; the ±15% lever only nudges the small-weight tail.
**VERDICT: technically PASS the WIRE rule (OOS CAGR +0.15pp AND OOS Calmar +0.03 both improve, IS also +0.07, DD improves, no overfit signature) — BUT magnitude is WITHIN NOISE.** Effect is the SAME signal already validated by the IC study (d_NPR/d_FSCORE PEAD), here applied as a within-basket reweight where the parking vehicle is cap-weighted+capped → the tilt cannot express itself (MAE 0.13%). **Recommendation: DO NOT wire as a standalone custom30V feature** — +0.15pp OOS doesn't justify added production complexity/turnover bookkeeping. The delta_momentum signal pays off where it has room to act = the **8L SCREENER tiebreaker / LAG selection** (per the IC study), NOT as a parking-basket weight tilt. Direction is right; the vehicle is wrong.

## Event-study: ΔNP_R (earnings-acceleration) selection inside LAG/PEAD pool (2026-06-27, Taylor, job Taylor_20260627_120256)
**Q (Mike dispatch):** Within the LAG positive-surprise pool, do accelerating-growth events (d_NPR>=0) earn higher forward T+25 than decelerating (d_NPR<0)? IS=2014-19 / OOS=2020+.
**Script:** `lag_dnpr_event_study.py` (new; NO production code touched) | events `data/earnings_events_classified.csv` | d_NPR from `data/bq_cache/ticker_financial.parquet` | T+25 prices from `data/bq_cache/ticker_prune.parquet`. Pool CSV → `data/lag_dnpr_pool.csv` (6181 events).
**Method (book-faithful):** entry=Release_Date+5 sessions (Open), exit=Release_Date+30 sessions (Open) on GLOBAL session calendar (ffill≤5) = 25-session hold, open-to-open %. d_NPR PIT = (NP_P0/NP_P4−1)−(NP_P1/NP_P5−1), guard NP_P4=0|NP_P5=0→NaN. Pool gate (task) = NP_R>0. Means winsorized 1%/tail; spreads/t-stats on RAW (Welch). NOTE: `earnings_surprise_data.pkl` unreadable in pandas 2.3.3 (2D-datetime block bug) → rebuilt d_NPR direct from BQ-cache parquet (auditable).

| Window | A d_NPR≥0 mean% | A hit% | A Sh | B d_NPR<0 mean% | B hit% | B Sh | spread(raw) | Welch t |
|--------|----------------|--------|------|----------------|--------|------|-------------|---------|
| IS 2014-19  | 4.19 (n=1471) | 58.1 | 0.31 | 2.88 (n=753)  | 57.0 | 0.16 | +0.96pp | 1.27 |
| OOS 2020+   | 6.38 (n=2545) | 63.4 | 0.40 | 4.54 (n=1220) | 57.5 | 0.30 | +1.86pp | **3.49** |
| FULL 2011+  | 5.55 (n=4150) | 61.4 | 0.37 | 3.91 (n=2031) | 57.3 | 0.24 | +1.54pp | **3.59** |

**Robustness on the ACTUAL deployed LAG entry gate (NP_R>=15, not NP_R>0):** IS A 4.12% vs B 3.87% (+0.25pp, hit −0.4pp → ~0 in-sample); OOS A 6.49% vs B 4.96% (+1.53pp, hit +4.6pp). Edge holds OOS but ~vanishes IS once the surprise gate is already tight.
**VERDICT: PASS as an event-level SELECTION signal** — d_NPR≥0 beats d_NPR<0 on forward T+25 with sign-consistent IS+OOS, OOS significant (t=3.5, +1.86pp, hit +5.9pp, higher Sharpe). Confirms the IC-study recommendation (job …105942) that delta_momentum acts where it has room = LAG selection. **BUT do NOT hard-wire as a filter yet:** (1) IS spread not significant (t=1.27); (2) on the live NP_R>=15 gate the IS marginal edge ≈0 (+0.25pp); (3) two analogous tilts were 50B-harness-REJECTED today (finer-3-tier-SUE −0.66pp CAGR; namecap weight-tilt +0.15pp within-noise). → Candidate for a SOFT LAG entry tilt (prefer d_NPR≥0 names when book is capacity-constrained at 12 slots), gated behind a faithful 50B V2.4 harness A/B before any LIVE change.

## V2.4 50B harness A/B: LAG d_NPR>=0 hard filter (2026-06-27, Taylor, job Taylor_20260627_121416)
**Q (Mike dispatch):** Event-study (job …120256) found accel events (d_NPR>=0) beat decel +1.86pp OOS (t=3.49). Harness-confirm before wiring: baseline LAG vs LAG+d_NPR>=0 filter in the production-style 50B two-book system (Book A BAL 25B + Book B SWITCHED 25B with the LAGGED earnings-drift schedule).
**Script:** `data/lag_harness_dnpr.py` (new; NO production code touched). Faithful clone of `pt_v4_full_faithful.py` (same `simulate_holistic_nav` engine, TC=0.3% round-trip, borrow 10%/yr, 20%-ADV/5-day fills, DT5G state `daily_comovement_dt5g.csv`, ETF parking {3:0.7}). Only change: LAG entry schedule built twice — A=prodspec gate (NP_R>=15 & prior_n_good>=4 & pa_HL3>=5); B=same + d_NPR>=0. Book A (BAL) identical → run once; Book B run twice; total=A+B. NAV CSVs `data/lag_harness_dnpr_nav_*.csv`, JSON `data/lag_harness_dnpr_results.json`. AUDIT_END=2026-06-09.
**Recon note:** `earnings_surprise_data.pkl` unreadable (pandas 2.3.3 2D-datetime bug) → surprise_B_MA (HI/LO split) AND d_NPR rebuilt from `data/bq_cache/ticker_financial.parquet` (NP_P0..P5), merged on (ticker,quarter,Release_Date); guard denom==0→NaN. d_NPR=(NP_P0/NP_P4−1)−(NP_P1/NP_P5−1).
**Filter footprint:** LAG schedule 2345→1630 entries (−715, −30.5%). OOS 1577→1125 (−28.7%).

| Window | N_evt A | N_evt B | CAGR_A | CAGR_B | dCAGR | DD_A | DD_B | Cal_A | Cal_B | dCal |
|--------|---------|---------|--------|--------|-------|------|------|-------|-------|------|
| FULL       | 2345 | 1630 | 13.09 | 11.65 | **−1.44** | −21.3 | −28.8 | 0.61 | 0.40 | −0.21 |
| IS 2014-19 |  751 |  497 |  7.87 |  5.00 | **−2.87** | −21.3 | −28.8 | 0.37 | 0.17 | −0.20 |
| OOS 2020+  | 1577 | 1125 | 18.19 | 18.23 | +0.04 | −18.9 | −18.5 | 0.96 | 0.99 | +0.03 |

**VERDICT: DO NOT WIRE.** The literal WIRE rule (OOS CAGR↑ AND Calmar↑ AND drop≤40%) technically passes on OOS — but the OOS gain is **+0.04pp CAGR / +0.03 Calmar = pure noise**, while the filter **destroys IS (−2.87pp CAGR, Calmar −0.20) and FULL (−1.44pp, MaxDD −7.5pp worse)**. A hard filter that breaks even OOS by noise but costs ~3pp IS and worsens full-period DD fails walk-forward robustness in spirit. Mirrors today's pattern (finer-3-tier-SUE −0.66pp; namecap weight-tilt +0.15pp within-noise): d_NPR is a real but SMALL selection signal that does NOT survive as a hard harness event-drop. Dropping 30% of LAG events shrinks the opportunity set/diversification (decel events still hit 57%); the isolated event-study spread doesn't translate through 12-slot limits + sizing + book dilution. **Keep d_NPR at most as a SOFT tiebreaker when the LAG book is capacity-constrained, NOT a hard filter.** Caveat: absolute CAGR here (13% FULL / 18% OOS) is the always-on V4-faithful two-book ensemble level, lower than the V2.4 R3 NEUTRAL-only headline — but the A/B DELTA is what's valid and it is internally consistent.

## WORKFLOW STEP 3.5 — Bootstrap robustness (process decision, 2026-06-29, Taylor)
**Decision:** Bootstrap robustness becomes a **standing workflow step (3.5)**, placed AFTER walk-forward IS/OOS (step 3) and BEFORE/AT wiring (step 4). It is NOT a new screen for exploratory variants — it runs ONLY when a config is one of: (a) being promoted to production/go-live, (b) a leverage/sizing decision, (c) Spyros needs a quantified DD tail to calibrate the breaker. Tool: **`bootstrap_nav.py <audit_csv> [baseline_csv]`** (merged from the now-deleted `bootstrap_robustness.py` + `bootstrap_v25_compare.py`; circular block bootstrap L=21d, B=4000, seed=12345 → deterministic).
**Why add it:** it changed a real decision — V2.4 DD anchor moved from −18% (single historical path) to **~−29% (5th-pct)**; historical MaxDD is one draw and under-states the tail. The 5th-pct MaxDD is the correct sizing/psychological anchor.
**Why placed at the END, not as a screen:** running CIs on every variant = the multiple-testing trap (compute 50 CIs, one looks great by luck). This season 6 rejected variants were NOT bootstrapped; only the 2 real go-live candidates (V2.4, V2.5) were. The cost is near-zero once the audit NAV CSV exists (the audit is run anyway).
**Relation to walk-forward (complement, not replacement):** walk-forward = "edge survives unseen TIME / not period-overfit" (structural, pass/fail GATE). Bootstrap = "given this return distribution, how much could LUCK swing it + where is the DD tail" (sampling, NOT pass/fail).
**Output discipline:** bootstrap is a **sizing/confidence input for Spyros**, NOT an auto-reject threshold. Spyros owns the risk-gate call (precedent: bootstrap quantified the tail → Spyros chose MGE 1.5 ok / 2.0 reject). Always quote the honest limit: sampling-only, regime-blind → a LOWER bound on true uncertainty.
**Pinned reference numbers (`bootstrap_nav.py /tmp/golive_daily_nav.csv`, reproduced 2026-06-29):** V2.4 go-live CAGR act 27.8% / 5th 18.6% / 95th 37.8%; Sharpe 5th 1.22; MaxDD act −17.6% / 5th −28.6%; P(loss)=0%, P(DD<−30%)=3.3%, P(DD<−40%)=0.2%. V2.5 MGE1.5 (small-acct profile, lever-on throughout): CAGR 30.4% / 5th 20.3%; DD_5th −30.5%; P(<−30%)=5.6%, P(<−40%)=0.4%.

## Gap-adaptive fill study (proxy) — Layer-3 should adapt to abnormal open (2026-06-29, Taylor)
**Q (user):** buy-list name shows an abnormal open move vs its ~1M intraday pattern (e.g. +3% at open) — should fill timing adapt? **Script:** `gap_adaptive_proxy.py` (DuckDB on `data/bq_cache/ticker_prune.parquet`, deterministic). Universe = liquid quality-gated, 2014+, liquidity floor 5B/day, |gap|<=0.15 (VN band; beyond=corp-action). gap_z = (Open/Close_T1−1) / trailing-20d causal realized-vol. intraday = Close/Open−1 (maps onto Layer-3 Open-vs-ATC choice). fwd20 = profit_1M (research only). N=408,622 ticker-days, 392 names. Walk-forward IS 2014-19 / OOS 2020+.

**FINDING 1 — EXECUTION (intraday give-back), the headline. STRONG, MONOTONIC, IS+OOS-STABLE:**
| gap_z bucket | N | intraday (Open→Close) | t | fwd20 |
|---|---|---|---|---|
| z<−2 (big DOWN) | 3,395 | **+356 bps** (recovers) | 41 | +1.03% |
| −2..−1 | 10,201 | +189 bps | 46 | +0.95% |
| −1..1 (normal) | 382,428 | −5 bps | −11 | +0.92% |
| 1..2 | 10,392 | −105 bps | −39 | +2.13% |
| z>2 (big UP) | 2,206 | **−246 bps** (gives back) | −33 | +3.35% |
IS up-gap −324bps / down-gap +445bps; OOS up-gap −208bps / down-gap +323bps — direction + magnitude stable both windows. → **Classic intraday overreaction mean-reversion, HUGE (±2.5–3.5%), dwarfs TC ~0.3%.** Decision: on a buy-list name, abnormal **UP-gap → DON'T chase, wait to ATC/limit (save ~2.5%)**; abnormal **DOWN-gap → BUY AT OPEN, capture ~3.5% recovery**. Two-sided.

**FINDING 2 — THESIS/alpha (forward drift), book-specific, secondary:** up-gap fwd20 +3.35% (>normal +0.92%) — but the extra drift is a **MOMENTUM** phenomenon (mom-proxy up-gap +3.64%), **NOT PEAD** (earnings-fresh up-gap fwd20 −0.28%, t=−0.4 = noise). Down-gap fwd20 ≈ normal (not a falling knife on average) → confirms down-gap is a fine entry. So the gap is informative about the thesis ONLY for momentum names; for LAG/PEAD the gap is pure execution noise (drift over weeks swamps it).

**ACTIONABLE DELTA vs current Layer-3:** current rule (non-TOP → 11:15/ATC) ALREADY waits → it is correct on UP-gaps (don't chase). The value is the **DOWN-gap side: current rule pays ~+356 bps vs open by waiting through the recovery.** → Proposed refinement: Layer-3 becomes **gap_z-conditional** — flip to BUY-AT-OPEN on abnormal down-gap (z<−2). Pure execution, zero added risk (alpha call already made by buy-list); free-insurance + small edge.

**CAVEATS:** (1) gap_z is a DAILY proxy for intraday abnormality (full-universe intraday bars absent) — Close/Open−1 IS definitionally intraday, so give-back is real, but the within-day PATH (give back by 11:15 vs only ATC) needs the 16-name true-intraday set (`data/intraday_1m`) to set the exact target time → next step before wiring. (2) Falling-knife risk on down-gap is the ALPHA decision (buy-list), NOT execution — clean separation. (3) Capturability: don't market-buy into up-gap; use ATC/limit. **Gate before LIVE:** Mafee fill-rule tweak, user-approved (real-money execution change).

### Cross-check on TRUE intraday (16 names, 1-min, 2023-09..2026-06) — `gap_path_crosscheck.py`
Confirms the daily-proxy DIRECTION on real intraday + sets the wiring target time. 10,632 ticker-days.
| bucket | N | ATC vs open | t | 11:15 vs open | % move done by 11:15 |
|---|---|---|---|---|---|
| z<−2 DOWN | 162 | **+181 bps** (recovers) | 9.9 | +101 bps | 56% |
| z>2 UP | 83 | **−156 bps** (gives back) | −5.2 | −134 bps | 86% |
Monotonic across buckets (−1..1 ≈ −9bps). Magnitudes smaller than full-universe daily (down +356/up −246) because these 16 are all large/mid liquid names (revert less than the full liquid tail) → **edge SCALES UP on smaller liquid names we actually park in.**
**WIRING SPEC (clean):** DOWN-gap path is POSITIVE at every checkpoint → **OPEN (09:15) is the day's cheapest entry**; waiting to 11:15 costs ~+100bps, to ATC ~+180bps. UP-gap give-back is **86% done by 11:15** → current Layer-3 (non-TOP→11:15) already correct. → **Proposed gap_z-conditional Layer-3:** if `gap_z < −2` on a buy-list name → override to **BUY-AT-OPEN (09:15)**; else keep v4 hybrid (non-TOP→11:15 / TOP→ATC). UP-gap needs no change. Pure execution, zero alpha risk. Did NOT pull vnstock — daily(408k rows) + 16-name intraday triangulate cleanly; more 1-min names would be marginal (vnstock 1-min history ≈ recent window only).
**NEXT:** draft the rule for Mafee (gap_z source = causal T-1 rvol; buy-list membership; LIVE needs user approval). Magnitude-by-liquidity cut available from daily data if needed for EV/blast-radius.

## Fair-value multiples-reversion PROTOTYPE + edge backtest (2026-06-30, Taylor)
Scripts: `gap_fairvalue_backtest.py`, `gap_fairvalue_orthogonality.py` (DuckDB on ticker_prune, deterministic). Quality-gated (ROE_Min3Y>=0 & FSCORE>=5, golden-floor proxy; CF_OA_3Y absent in cache), liquid>=5B, 2014+, ~164k name-days. profit_* = forward LABEL only.
**FINDING 1 — naive own-history multiple reversion FAILS.** fair_mult = the name's own MA5Y multiple; disc = MA5Y/current-1. Rank-IC SIGN FLIPS IS->OOS: d_pe IS -0.026 / OOS +0.030; d_pb IS -0.022 / OOS +0.051. Quintiles HUMP-shaped (cheapest Q5 underperforms middle = value trap). fair-price outputs corrupted (PVD PE_MA5Y=107 from near-zero-EPS years -> fair 104k vs price 30k). This is ~what a generic /valuation ("below historical average") produces -> a value trap. REJECT.
**FINDING 2 — fundamental-anchored justified multiple is STABLE.** fair_PB = ROIC5Y/r (r=0.13 placeholder); d_pb_just = fair_PB/PB-1. Rank-IC POSITIVE both windows (IS +0.021 t3.9 / OOS +0.032 t8.6); cheapest OOS quintile profit_2M +4.67% vs ~2.7% rest (no value-trap hump). d_eveb also stable (EBITDA less corruptible than EPS) but weak.
**FINDING 3 — orthogonality (Fama-MacBeth vs existing composite ey 1/PE + cfy 1/PCF; PS absent in cache).** d_pb_just ADDS incremental signal controlling for composite: b_just|comp +0.197(t6.0)1M / +0.500(t9.2)2M ALL; residual-IC OOS +0.017(t5.0)1M / +0.016(t4.6)2M = NOT redundant. Complementary across regimes: IS the pure-yield composite is weak/negative (IC_comp -0.006) and d_pb_just carries the value load; OOS composite strong and d_pb_just adds modestly. BUT incremental add is SMALL (residual IC ~0.01-0.017).
**KEY REFRAME:** under cross-sectional ranking, d_pb_just_z is IDENTICALLY z(ROIC5Y/PB) — the r=0.13 cost-of-equity and the -1 are affine constants that wash out of the rank. So the SIGNAL = quality-adjusted book yield (ROIC/PB); the "missing cost-of-equity/rates feed" is needed ONLY for an ABSOLUTE VND fair price, NOT for the ranking signal.
**VERDICT / recommendation:**
 (a) SCREENING use — add ROIC/PB (quality x book-cheapness) as ONE more component to the rating_8l value composite (cheap, I own it, NO rates feed needed). Gate: does the AUGMENTED composite beat current rating OOS on actual selection (not just raw IC)? before wiring.
 (b) ABSOLUTE VND fair-price engine — needs cost-of-equity feed + per-archetype justified formulas + FORWARD estimates; given the ranking add is small, NOT worth building as a production alpha source. Value is qualitative (a target price to anchor discussion) -> on-demand per name; this is where an LLM /valuation can assist as a qualitative companion, never as a wired signal.

### Selection-level A/B (2026-06-30) — ROIC/PB does NOT improve actual picks → DO NOT add to rating_8l
Script `gap_fairvalue_selection_ab.py`. Monthly rebalance, quality-gated liquid universe, top-25 by A=z(ey)+z(cfy) vs B=+z(ROIC/PB). (IS pre-2018 degenerate: ROIC5Y 5y-history + >=50-name gate shrinks early universe; effective window 2018-01..2026-05, 70 OOS months.)
| window | h | A | B | delta(B-A) | t | win% |
|---|---|---|---|---|---|---|
| ALL | 1M | 2.34% | 2.31% | **-0.04pp** | -0.2 | 44% |
| OOS20+ | 1M | 2.47% | 2.42% | **-0.05pp** | -0.3 | 44% |
| OOS20+ | 2M | 4.55% | 4.48% | -0.06pp | -0.3 | 41% |
Mean basket overlap 21/25 (84% identical); the ~4 marginal name-swaps add ~0 (slightly negative). Per-year delta noisy/mixed-sign (2019 +0.45, 2022 +0.40 vs 2024 -0.54, 2025 -0.34) = no consistent edge.
**VERDICT: DO NOT add ROIC/PB to the rating_8l value composite.** The small residual-IC (~0.015 OOS) from the orthogonality test does NOT survive portfolio construction — the composite already ranks cheap-quality names at the top, ROIC/PB only reshuffles within an already-good top-25 and the swaps wash. Same pattern as d_NPR / SUE-tilt / stability-floor: a small raw-IC signal that dies at the top-K selection reality. **The value axis is SATURATED.**
**THREAD CLOSED — answer to "fair-value engine / is /valuation better":** (1) naive historical-multiple reversion = value trap (rejected); (2) fundamental-anchored justified multiple (=ROIC/PB) = small stable raw edge but (3) adds NOTHING to existing selection. Net: rating_8l already captures the available value edge; a fair-value RANKING engine gives no new alpha. Absolute VND fair-price is worth keeping ONLY as a qualitative/communication tool (on-demand per name; LLM /valuation can assist there, never wired as signal). The only genuine data gaps (forward estimates, cost-of-equity feed) buy absolute-price PRECISION, not alpha.

## gq_score (growth-quality / "golden eggs") DECISIVE GATE — 2026-06-30, Taylor → FAIL, DO NOT WIRE
Script `gq_score_gate.py` (DuckDB, deterministic; ASOF point-in-time join ticker_financial→ticker_prune monthly, fin.time=release date<=selection day, 0 look-ahead, staleness cap 280d). Design = Taylor_20260630_040305: a THIRD selection axis (growth-WITH-quality) orthogonal to rating(quality)+value. gq_score = z(Revenue_YoY_P0 growth) + z(GPM_P0−GPM_P4 margin-trend), credited only when sustain(YoY_P0>0 & YoY_P4>0) & CF_OA_P0>0 (anti-fiction gate), else floored. Self-check: 8,679 selection rows, 344 names, 150 months 2014-01..2026-06, 0 look-ahead violations, median staleness 42d, gq_score NaN 0.
**GATE 1+2 — IC (raw + RESIDUAL to value_z+quality_z):**
| window | h | raw-IC | resid-IC | t |
|---|---|---|---|---|
| IS14-19 | 1M | +0.006 | +0.003 | 0.2 |
| OOS20+ | 1M | +0.024 | +0.019 | 1.3 |
| OOS20+ | 2M | +0.012 | +0.013 | 0.9 |
Residual-IC OOS technically >0 but WEAK & insignificant (t~1.3). IS≈0 (effect not stable across regimes — wrong shape for a return signal). Bar: fair-value/ROIC-PB also showed ~0.015 residual-IC and still failed selection.
**GATE 3 — selection A/B, top-25 monthly, A=quality+value vs B=+gq_score (overlap 23/25):**
| window | h | A | B | delta(B-A) | t | win% |
|---|---|---|---|---|---|---|
| OOS20+ | 1M | 2.52% | 2.56% | **+0.05pp** | 0.6 | 46% |
| OOS20+ | 2M | 4.56% | 4.56% | **−0.00pp** | -0.0 | 46% |
Per-year delta alternating-sign (2023 −0.16, 2025 +0.13, 2026 −0.27) = no consistency. (IS A/B degenerate: only 3 months clear the 50-name gate pre-2020 — sustained-growth+liquid universe too thin early.)
**SENSITIVITY (decisive) — decompose gq, OOS profit_1M:**
| variant | resid-IC | A/B d1 | win |
|---|---|---|---|
| growth only (z Rev-YoY) | **−0.011** | **−0.127pp** | 46% |
| margin only (z GPM trend) | +0.013 | +0.020pp | 43% |
| cf-gate only (no sustain floor) | +0.007 | −0.065pp | 51% |
**The headline thesis FAILS: revenue-growth ALONE is a NEGATIVE residual signal OOS** (−0.011 resid-IC, −0.127pp A/B) — chasing growth on top of a quality+value top-25 is a drag (overpaying). Only the margin-trend term is mildly +IC, and it evaporates at selection (win 43%). gq_score's faint positive came from margin + the CF floor, NOT from growth (the axis's whole premise).
**Orthogonality:** corr(gq,quality_z)=+0.02 (genuinely orthogonal to quality, as designed), corr(gq,value_z)=+0.11 (mild). Distinct axis — but distinct ≠ additive.
**VERDICT: FAIL → DO NOT wire gq_score into rating_8l.py, and DO NOT patch stability() for growth.** Same shape as fair-value/d_NPR/SUE/stability-floor: a small raw-IC that dies at top-K selection. The design's q2 diagnosis (core_score has no growth term; stability() docks acceleration) is a TRUE description of the scorecard, but adding growth back empirically does NOT improve picks — growth-reward is non-additive and growth-alone is negative. The "proven-5Y bias" is not costing selection return. **Quality+value at top-25 already captures the actionable signal; the growth axis is NOT an edge.**

## 2026-06-30 · Compounder early-detection backlook (Taylor_20260630_042054)
**Source:** ticker_financial, 5 names 2013Q2–2017Q1. CSV `/tmp/compounders.csv` (74 rows). Margins ×100 to %, mcap≈PE×NP_P0×4 (rough; EPS field mis-scaled, do not use EPS×OShares).
**Entry snapshot (approx buy window):**
```
 tk      Q  RevYoY  GPM  NPM  ROE  ROIC CF_OA FSC  PE   PB   mcap_bn
HPG 2014Q1  0.65  21.3 13.4 0.25 0.40 pos  6   9.8 2.26  ~34000
MWG 2015Q1  0.58  14.6  4.2 0.53 1.00 NEG  2  20.6 8.85  ~19000
PNJ 2014Q1  0.39   9.9  3.2 0.15 0.43 pos  5  12.9 1.90   ~4000
VCS 2014Q4  0.89  26.6 18.6 0.24 0.67 NEG  6   6.1 1.64   ~2600
DGC 2016Q1 -0.08  18.4  9.9 0.35 0.31 pos  3   7.3 1.65   ~1700
```
**Trajectory (multi-qtr) signature of genuine ramps (HPG'14, VCS'14-15, MWG'14-15):** sustained RevYoY>30-90%; ROE_TTM rising AND >20% (HPG 22→30, VCS 6→44, MWG 17→56); ROIC_TTM>40%; margin EXPANSION for HPG/VCS (VCS GPM 21→47, NPM 4→18 textbook), FLAT for MWG (retail, edge=volume/ROE); FSCORE 6-8 HPG/VCS.
**DGC 2016 anomaly (honest):** at dispatched entry DGC was DECELERATING (RevYoY−0.08, ROE 0.42→0.21, margins 20→11.5). Real compounding = 2020+ phosphorus supercycle, NOT 2016. A clean screen correctly would NOT flag DGC in 2016.
**Step2 — does 8L catch them?** 8L value-tilt (ey+cfy+ps)+golden floor → catches CHEAP compounders HPG(PE9)/VCS(PE5,PB<1)/DGC(PE7); MISSES growth-priced MWG(PE20-25,PB5-9) and noisy-NP PNJ (DongA writeoff). Consistent w/ prior bus: gq_score growth-only FAILED wired into rating_8l; value axis saturated → compounder screen must be SEPARATE, not re-wired.
**Step3 — proposed standalone Compounder Screen (all point-in-time ticker_financial, no look-ahead):**
1. Revenue_YoY_P0≥0.20 AND Revenue_YoY_P4≥0.15 (2yr persistence, use REVENUE not NP — NP one-off noise).
2. ROE_Trailing≥0.18 AND ROIC_Trailing≥0.15 AND rising (ROIC to avoid leverage-inflated ROE).
3. Quality-of-growth gate: NPM_P0≥NPM_P4−1.0 AND GPM_P0≥GPM_P4−2.0 (margin stable/expanding — KILLS fake share-buying growth).
4. CF_OA_3Y>0 (3yr operating cash positive — filters cash-burn; 3Y not 1Q because retail WC lumpy).
5. FSCORE≥3 (soft; MWG sat 2-4 asset-light).
6. Valuation = SOFT not hard-cheap: PEG<1.5 OR PE<PE_MA1Y. Deliberate departure from 8L hard value tilt → lets MWG-type through.
7. Size tilt (soft, not gate): prefer small/mid mcap percentile for runway (HPG already ~34T → size is tilt not gate).
**Discriminator quality vs fake = margin direction + CF_OA_3Y>0 + ROIC level.** Rev↑ & margin↓ & CF_3Y<0 = fake → reject.

## 2026-06-30 · Compounder Screen — built + backtested (Taylor_20260630_042949)
**Script:** `compounder_screen.py` (arg = ROE_Trailing floor; default 0.18, relaxed run = `python3 compounder_screen.py 0.15`). **Outputs:** `data/compounder_screen_monthly.csv`, `data/compounder_screen_verdict.json`.
**Method:** point-in-time monthly rebalance. Universe = liquid quality names (in `ticker_prune` that day, Trading_Value_1M_P50≥1e9, 484 distinct seen). Financials ASOF-joined (DuckDB `ASOF LEFT JOIN ON ticker AND rebal_date>=Release_Date`, staleness≤180d → names that stop reporting drop out). Selection = the 6 Step-3 gates (Rev persistence, ROE/ROIC + rising, no-margin-sacrifice NPM/GPM [units are FRACTIONS: −1.0pp=−0.01, −2.0pp=−0.02], CF_OA_3Y>0, FSCORE≥3, soft-valuation PEG∈(0,1.5) OR PE<PE_MA1Y). Rank qualifiers by z(RevYoY)+z(ROE_TTM)+z(ROIC_TTM), top-15. Equal-weight, T+1 execution (signal at month-end close, trade next session), TC=0.1% on traded weight. **Self-check 0 VND: PASS** (NAV recompute-from-CSV diff 2.7e-5 VND).
**Universe TOO THIN (key caveat):** even relaxed to ROE_Trailing≥0.15, median **4 qualifiers/month**, 89/144 months <5, **28% of months hold ≤2 names, 63% ≤4, only 1% reach the top-15 target**. This is a concentrated micro-portfolio, not a diversified top-15 book.
| window | Compounder net CAGR | Sharpe | MaxDD | Calmar | B&H CAGR | edge |
|---|---|---|---|---|---|---|
| FULL 2014-2026 | 34.3% | 1.08 | **−51.0%** | 0.67 | 10.7% | +23.7pp |
| IS 2014-2019 | 20.5% | 0.81 | −45.0% | 0.46 | 9.0% | +11.5pp |
| OOS 2020-2026 | 50.3% | 1.31 | −46.8% | 1.07 | 12.5% | +37.8pp |
**Robustness (decisive):** headline rides on TWO low-breadth lucky years — 2014 (+87pp on ~2.5 names) and 2020 (+181pp on ~2.1 names). **Excluding 2014+2020: CAGR 34.3%→19.6%, edge vs B&H +8.3pp** (B&H 11.3%). Still 9/13 years beat B&H → signal is REAL, not pure luck, but magnitude is concentration-inflated and MaxDD −51% is WORSE than market −43%.
**Orthogonality:** mean overlap of Compounder picks vs **custom30V basket = 23%** (mostly distinct), vs **8L top-25 = 4%** (almost fully disjoint — 8L is value-tilted, compounder is growth-tilted). Confirms the growth/compounder axis is genuinely orthogonal to both existing books.
**VERDICT (conditional):** signal exists + is orthogonal (esp. vs 8L), BUT **NOT deployable as a standalone top-15 book** — strict 6-gate conjunction yields a median of 4 names → high idiosyncratic variance, MaxDD>market, headline CAGR inflated by 2 lucky years. **Recommended use = compounder WATCHLIST / tilt-overlay feed into a diversified book, not a standalone allocation.** To make it a real book you'd have to widen beyond the liquid `ticker_prune` set (capacity hit) or materially loosen the gates (dilutes the "compounder" definition). Same family as gq_score/fair-value: the growth axis is detectable but doesn't cleanly become a tradeable sleeve.

## 2026-06-30 · Retail Compounder Screen — built + backtested (Taylor_20260630_044929)
**Script:** `retail_compounder_screen.py` (arg `invgate` to turn inventory gate ON; default OFF). **Outputs:** `data/retail_compounder_monthly.csv`, `data/retail_compounder_verdict.json`. Design = `mike/agents/Taylor/retail_valuation_framework.md` (job …044001). DISTINCT from industrial `compounder_screen.py`: P/S-primary (not P/E), two archetypes.
**Universe = retail ICB only:** `ICB_Code IN (5379 general-retail [MWG/FRT/DGW/PET/PSD/PET], 3767 jewelry [PNJ])` ∩ `ticker_prune`. Only **9 names ever seen** (DGW,FRT,LIX,MWG,NET,PET,PNJ,PSD,SBV). Genuinely THIN: **median 1 qualifier/month, max 4, 69/79 months hold <3 names.** "Top-10" is non-binding — always take every qualifier.
**Gates (point-in-time ASOF, staleness≤180d):** PS∈(0,1.5); growth EITHER (A) RevYoY_P0≥0.15 AND (RevYoY_P4≥0.10 OR NaN) [volume/MWG] OR (B) GPM_P0−GPM_P4≥0.02 [margin/PNJ]; inventory InvTurn_P0≥0.85·InvTurn_P4 [ABLATED — see below]; CF_OA_5Y>0 (fallback CF_OA_3Y); ROIC5Y≥0.12 OR ROE5Y≥0.15. NaN policy: young-IPO RevYoY_P4/InvTurn_P4 NaN → "can't eval → pass". **Self-check 0 VND: PASS** (NAV recompute diff 1e-6 VND). Liquidity: relied on `ticker_prune` membership (1e8 floor only) NOT the 1e9 industrial floor — retail compounders are sub-1B ADV at entry (KB illiquidity-premium); median selected-name ADV 45B, 6% of picks sub-1B.
| window | Retail net CAGR | Sharpe | MaxDD | Calmar | B&H CAGR | edge |
|---|---|---|---|---|---|---|
| FULL 2014-2026 | 26.99% | 0.77 | **−52.0%** | 0.52 | 10.34% | +16.6pp |
| IS 2014-2019 | 33.05% | 0.89 | −23.0% | 1.44 | −2.28% | +35.3pp |
| OOS 2020-2026 | 22.53% | 0.69 | **−42.5%** | 0.53 | 21.13% | **+1.40pp (Sharpe −0.18)** |
**Verify known names:** MWG ✓ appears 2015-05..2015-12 (volume archetype). FRT-2018 ✓ correctly EXCLUDED (CF_OA_5Y=−4.2e11 <0, the Long Châu burn). **PNJ ✗ NOT reproducible** — structural, not a bug: (1) PNJ was OUTSIDE `ticker_prune` in 2014/2015 (10/25 rows only; entered curated universe 2016+); (2) PNJ CF_OA_5Y went NEGATIVE in 2015 (−2.65e10) → fails the SAME cash gate that (correctly) kills FRT-2018. **The margin-turnaround archetype (PNJ) is indistinguishable from a value-trap (FRT) on point-in-time cash flow → not isolable without look-ahead.** The screen captures the volume archetype only.
**Inventory-gate ablation:** rigid InvTurn_P0≥0.85·InvTurn_P4 on noisy quarterly data DELAYS MWG from 2015→2016 (MWG InvTurn swings 1.3↔7.5 q/q, cumulative-vs-single-quarter reporting artifact). Headline keeps gate OFF; framework intent was sector-relative trajectory judgement, not a hard quarterly ratio.
**Orthogonality:** vs **8L top-25 = 0.0%** (fully disjoint — 8L is value-tilted, retail compounders are growth-priced), vs industrial Compounder top-15 = 7.5%, vs custom30V = 32.7%. Genuinely new axis.
**VERDICT:** Same family as industrial compounder / gq_score / fair-value. Signal is REAL + perfectly orthogonal to 8L, **but NOT a standalone book**: 1–2 names/month, single-name-moonshot dependent (MWG 2015-16, retail 2021 +119%), MaxDD −52% > market, and **OOS edge is marginal (+1.4pp return but WORSE Sharpe −0.18 and DD)** — the spectacular IS (+35pp) is MWG-driven and does not persist. Captures only the volume archetype (MWG-type); the margin-turnaround archetype (PNJ-type) is structurally uncapturable. **Recommended use = retail-compounder WATCHLIST / tilt-overlay, NOT a standalone allocation** — matches the framework's pre-registered "thin → tilt not book" prediction.

## Banking Compounder Screen — Taylor_20260630_051434 (2026-06-30)
- **Script**: `bank_compounder_screen.py` → `data/bank_compounder_{monthly.csv,verdict.json}`. Framework: `mike/agents/Taylor/banking_valuation_framework.md`.
- **Method**: ICB_Code=8355 banks, ticker_prune, TV_1M_P50≥1e9; ASOF point-in-time financials (staleness≤120d); Gordon justified-P/B `(ROE5Y−0.05)/0.08` (COE=0.13,g=0.05); gates ROE_Min3Y≥0.08, ROE5Y≥0.12, (NP_P0/NP_P4≥1.10 OR Rev_YoY≥0.12), PB<justified & PB<2.0; rank z(cheap_margin)+z(ROE5Y)+z(NPgro); top-10 monthly EW T+1 TC0.1%. AUDIT_END 2026-06-26.
- **Result (net)**: FULL 2015-2026 CAGR **31.93%** / Sharpe 1.06 / MaxDD **−44.5%** vs B&H 13.23% (**+18.7pp**). IS2014-19 36.24% (+19.0pp). **OOS2020-26 30.04% (+18.6pp, broad: 2020+70/2021+60/2023+20/2024+19)**. Self-check diff 6e-6 VND PASS.
- **Verify**: MBB caught 2016-17 (12mo) ✓; VCB correctly ABSENT (PB2.54≫Gordon0.61, premium/forward-ROE play, uncapturable w/o look-ahead) ✓; weak tail BVB/KLB/NVB excluded ✓.
- **Orthogonality**: vs 8L top-25 **5%** (orthogonal); vs retail/industrial 0% (disjoint ICB); **vs custom30V 74%** (custom30V already holds 10-13 banks since 2018 → redundant).
- **Verdict**: REAL + holds OOS (strongest of 3 sector compounders), BUT high-beta (DD−44%), return concentrated in 2 bank-bull episodes (2017+2020-21 = 79% of cum), early era 1.1-name book (single MBB bet), 74% already in custom30V → **watchlist/tilt + Gordon valuation lens, NOT a standalone leveraged book**.

## RE Compounder Screens (dual) — Taylor_20260630_053151 (2026-06-30)
- **Scripts**: `re_compounder_screen.py` → `data/re_compounder_{resid_monthly.csv, indust_monthly.csv, verdict.json}`. Framework: `mike/agents/Taylor/re_valuation_framework.md`.
- **Why 2 screens**: ICB 8633 holds 2 different businesses. **A Residential developers** (cyclical, handover-lumpy revenue → Revenue_YoY useless, ROIC land-bank-distorted, CF_OA structurally neg) → value=P/B(NAV proxy), survival=Debt_Eq+IntCov, quality=ROE5Y, margin=GPM_traj. **B Industrial parks** (REIT-like, illiquid; Debt_Eq/IntCov MISLEADING = deferred prepaid-lease booked as liability) → value=P/B+DY, quality=ROIC5Y, FLAG ADV<10B. Explicit IP list (no BQ sub-split): KBC,IDC,SZC,BCM,SIP,NTC,LHG,D2D,TIP,IDV,SZL,SNZ.
- **Method**: point-in-time ASOF financials (staleness≤120d), monthly EW, T+1, TC0.1%. Screen A: PB∈(0,1.5) & Debt_Eq<2.0 & IntCov>1.5 & NP_P0>0 & GPM≥0.15; rank z(−PB)+z(ROE5Y)+z(GPM_traj)+z(IntCov_cap), top-10. Screen B: PB∈(0,1.5) & DY>0.04 & ROIC5Y>0.08; rank z(DY)+z(ROIC5Y)+z(−PB), take-all. **Self-check 0 VND: resid diff 1e-6, indust diff 0 → PASS both.** AUDIT_END 2026-04-29.
- **Deviation from dispatch draft (justified by backlook)**: dropped "Debt_Eq_P0<Debt_Eq_P4 YoY-deleveraging" + "CF_OA_P0>0" hard gates — at the trough leverage is at YoY PEAK and CF_OA structurally negative (cash into projects); both gates would exclude the best entries (VHM-2023, NLG-2022). Absolute Debt_Eq<2.0 + IntCov>1.5 + NP_P0>0 still cleanly excludes NVL/PDR.
| screen | window | net CAGR | Sharpe | MaxDD | B&H | edge |
|---|---|---|---|---|---|---|
| A resid | FULL 14-26 | 10.41% | 0.43 | **−61.8%** | 14.57% | **−4.17pp** |
| A resid | OOS 20-26 | 13.00% | 0.50 | −61.8% | 11.45% | +1.55pp (Sharpe −0.10) |
| B indust | FULL (29mo) | 39.58% | 0.78 | −25.6% | 46.00% | −6.42pp |
| B indust | OOS 20-26 | 19.84% | 0.69 | −22.1% | 29.63% | −9.79pp |
- **VERIFY (flawless risk discipline)**: VHM 2022Q4-23 ✓ caught, NLG 2022-23 ✓, TCH 2022-23 ✓; **NVL leverage-trap EXCLUDED ✓** (PB0.62 cheap BUT Debt_Eq4.7/IntCov−0.39), **PDR-2022 EXCLUDED ✓** (IntCov−0.97). NTC-2017 ABSENT-by-design (PB2.5-3.7≫1.5; premium DY+ROE+land-revaluation re-rating, uncapturable w/o look-ahead — parallel banking-VCB/retail-PNJ).
- **Capacity (Screen B)**: median selected ADV **1.7B/day**, 31 pick-months sub-10B, median 1 name/month → un-investable as a book (NTC-type: 10B buy = weeks).
- **Orthogonality (resid A)**: vs custom30V 15.2%, vs 8L top-25 7.9% (orthogonal value/cyclical axis), vs indust B 0% (disjoint).
- **VERDICT**: cleanest NEGATIVE of the 4 sector screens. Residential risk-discipline is REAL+valuable as a **GATE/lens** (separates cheap-quality from leverage traps) but the SECTOR DOESN'T COMPOUND — underperforms B&H −4.2pp full with −61.8% DD because a monthly value screen holds distress straight through 2022 (−48%); marginal OOS edge = pure 2020-21 recovery-beta. RE alpha needs regime TIMING (DT5G), absent from value screen. Industrial = REIT yield-watchlist only. **Deploy = valuation/risk LENS for sizing RE inside V2.4 (P/B-NAV proxy + leverage-trap exclusion), NOT a standalone book.**

## Logistics/Port/Shipping Compounder Screens (dual) — Taylor_20260630_054646 (2026-06-30)
- **Scripts**: `logistics_port_screen.py` → `data/logistics_{port_monthly.csv, ship_monthly.csv}`, `data/logistics_port_verdict.json`. Framework: `mike/agents/Taylor/logistics_port_valuation_framework.md`. AUDIT_END 2026-04-29.
- **Why 2 screens**: maritime/transport = THREE economics under 2 ICB codes. **A Ports/infra** (ICB 2777: GMD,VSC,HAH,ACV,DVP,PHP,SGP,DXP,NCT,SGN... 16 names; concession moat, D&A-heavy → value EV/EBITDA not P/E). **B Shipping** (ICB 2773: PVT,VOS,VIP,VTO,GSP... 7 names; deep cyclical, no moat → trough buy P/B<0.9). GMD = hybrid (kept in Port by ICB).
- **Backlook-driven gate corrections (key)**: (1) **ROIC5Y≥8% kills GMD always** (Gemalink capex suppresses 5yr-avg ROIC to 1.5-7.7% the whole decade) → relaxed to **≥5%**, read ROIC_Trailing as real moat. (2) **IntCov NaN = net-cash = the BEST ports (DVP/VSC)** → NaN must PASS. (3) **DY>4% hard gate wrong for VN** (GMD/PHP/HAH pay 0%, reinvest/state-owned) → **FCF>0 OR DY>4%**.
- **Method**: point-in-time ASOF financials (staleness≤120d), monthly EW, T+1, TC0.1%, **empty pick-months hold CASH** (calendar preserved — correct for wait-for-trough cyclical). Self-check 0 VND: **port diff 0.0, ship diff 5e-6 → PASS both.**
- **Screen A — Ports** gates: EVEB∈(0,10) & ROIC5Y≥0.05 & CF_OA_3Y>0 & (FCF>0 OR DY>0.04) & (IntCov>2 OR NaN) & Revenue_YoY≥−0.10; rank z(−EVEB)+z(ROIC_TTM)+z(FCF_yield), top-10.
- **Screen B — Shipping** gates: PB∈(0,0.9) & CF_OA_P0>0 & Debt_Eq_P0<2.0 & NP_P0>NP_P4; rank z(−PB)+z(CF_OA)+z(NP_turn), take-all. **DEPLOY FLAG: high-beta → only size in DT5G NEUTRAL/BULL.**

| screen | window | net CAGR | Sharpe | MaxDD | B&H | edge |
|---|---|---|---|---|---|---|
| A port | FULL 14-26 | 7.17% | 0.41 | **−58.9%** | 10.23% | **−3.06pp** |
| A port | IS 14-19 | −2.01% | −0.05 | −38.7% | 8.96% | −10.97pp |
| A port | OOS 20-26 | 16.66% | 0.67 | −58.9% | 11.45% | +5.20pp (Sharpe +0.07) |
| B ship | FULL 14-26 | 12.46% | 0.60 | **−31.1%** | 10.23% | +2.22pp (Sharpe +0.00) |
| B ship | IS 14-19 | 4.33% | 0.31 | −26.1% | 8.96% | −4.63pp |
| B ship | OOS 20-26 | 20.74% | 0.82 | **−28.9%** | 11.45% | **+9.28pp (Sharpe +0.22)** |

- **VERIFY**: VSC 2019-21 ✓ caught (33mo, quality port), DVP 2020-21 ✓ (NaN-IntCov net-cash passed), PHP 2021 ✓, PVT-2020 trough ✓, **VOS leverage-trap EXCLUDED 2014-2021 ✓** (cheapest P/B 0.25 but DebtEq5.7/CF_OA<0/NP-loss), VOS-recovered caught 2023-24 ✓ (de-levered DebtEq0.75). **GMD NOT caught (2014 AND 2020+)** — structural, not a bug: the hybrid never simultaneously satisfies cheap-EVEB(<10) AND ROIC5Y≥5% — cheap window = pre-Gemalink-ramp low ROIC, earned-ROIC window = EVEB 15-16 expensive. Uncapturable by point-in-time value+quality conjunction w/o concession foresight (parallel banking-VCB / retail-PNJ / RE-NTC premium re-rate misses).
- **Capacity**: PORT median selected ADV 2.4B/day, SHIP 4.8B — thin (port pure-plays sub-2B), micro-portfolio (PORT median 2 names/mo, 45/148 cash; SHIP median 1 name/mo, 53/148 cash). Never reaches top-10 target.
- **Orthogonality**: PORT vs 8L top-25 **0.0%**, vs custom30V 12.9%; SHIP vs 8L 1.7%, vs custom30V 25.7% → both genuinely orthogonal new axes (8L value-tilt holds ~no maritime).
- **VERDICT**: same family as the other 4 sector screens. **Screen A (Ports) = the weakest of all 5** — NEGATIVE full-period (−3.06pp) with −58.9% DD, OOS edge is pure 2020-21 recovery beta, and it MISSES the marquee compounder (GMD). EVEB+ROIC value screen on ports doesn't compound. **Screen B (Shipping) = the more valuable artifact** — REAL OOS edge (+9.28pp, +0.22 Sharpe) with DRAWDOWN BETTER than market (−31% vs −43%) and flawless leverage-trap avoidance (VOS), but thin (1-name median), IS-negative, return rides 2022+2024 freight booms (matches the cyclical-timing flag). **Deploy = valuation/risk LENS, NOT standalone book**: for Ports use EVEB+ROIC_Trailing+net-cash as a quality lens (note GMD needs separate hybrid judgement); for Shipping the P/B<0.9 + Debt_Eq<2.0 + CF_OA>0 trough-buy rule is a clean trap-avoidance + cyclical-entry lens to size maritime inside V2.4 in DT5G NEUTRAL/BULL only.

## Telecom valuation lens (Taylor_20260630_060226) — 2026-06-30
- **Scope:** VN listed telecom — structurally thin. Pure-telecom (FOX/VGI) entered liquid `ticker_prune` only 2026-06 → un-backtestable as a quality-universe book. Lens runs on full `tav2_bq.ticker` (UPCOM tail).
- **Universe (ICB):** 6535 FOX (FPT Telecom, the genuine quality compounder)+TTN(micro); 6575 VGI (Viettel Global, turnaround); 2357 CTR (Viettel Construction, tower-co). FPT/CMG/ELC = IT/tech (95xx), not pure telecom.
- **Primary metric:** EV/EBITDA (`EVEB`) vs global mature-telecom 4-8x. Secondary: FCF=CF_OA_P0+CF_Invest_P0, NPM trajectory, ROIC5Y moat, Debt_Eq+IntCov.
- **Backlook (fwd-12M, full ticker):** EVEB<8 + NPM/ROIC-confirm entry → FOX +44 to +155%, CTR +75 to +141%; expensive (EVEB>9) → flat/negative. Cheap-EVEB alone insufficient (FOX 2017-18 EVEB~6 went flat until margin expansion started 2019).
- **Screen (`telecom_screen.py`, 100 monthly snapshots):** FLAGGED n=10 → +142.7% avg fwd-12M, 100% winrate; UNFLAGGED n=90 → +34.2%, 64%; spread +108.5pp. Output `data/telecom_screen_entries.csv`.
- **Verdict:** REAL & strong valuation lens (cleanest single-metric entry of any sector), but n=10 thin + structural illiquidity → WATCHLIST/lens, NOT standalone book. Sector just became investable (liquidity matured 2026-06). FOX entry discipline = EVEB<8 w/ NPM/ROIC rising (currently ~12-13, not cheap → wait). VGI = momentum book not value. Orthogonal to 8L (no EV/EBITDA term) + custom30V (no name overlap). No NAV sim (no tradeable history) → §3 fwd-return table is the auditable artifact. AUDIT_END 2026-06-29.

## Fertilizer/Chemicals/Rubber triple screen — Taylor_20260630_064517 (2026-06-30)
- **Script**: `fertchem_rubber_screen.py` → `data/fertchem_{fert,chem,rubber}_monthly.csv`, `data/fertchem_rubber_verdict.json`. Framework: `mike/agents/Taylor/fertchem_rubber_valuation_framework.md`. AUDIT_END 2026-04-29.
- **Why 3 screens**: ICB doesn't split the economics — **1357** lumps fertilizer+chemicals, **1353** lumps rubber+plastics → hand-curated sub-universes. A=Fertilizer (commodity, gas-policy urea), B=Specialty chem (DGC phosphorus), C=Rubber land-bank (hidden-asset).
- **Method**: point-in-time ASOF financials (staleness≤120d), monthly EW, T+1, TC0.1%, hold CASH when no qualifier. **Self-check 0 VND: fert 2e-6, chem 1e-6, rubber 0.0 → PASS all 3.**
- **Screen A — Fertilizer** EVEB∈(0,6)&CF_OA_3Y>0&GPM_P0>GPM_P4&Debt_Eq<1.5; rank z(−EVEB)+z(DY)+z(GPM) top-10. Universe 10 (DPM/DCM big-liquid). ADV 29.2B.
- **Screen B — Specialty chem** EVEB∈(0,8)&ROIC5Y≥0.10&Rev_YoY>0.20&CF_OA>0; rank z(−EVEB)+z(ROIC)+z(RevYoY) take-all. ADV 4.3B. **Note: literal ROIC5Y>12% drops DGC 2019-2020 golden window (ROIC was 10.8-11.5%) → 15 of 29 DGC entry-months; used ≥10%.**
- **Screen C — Rubber land-bank** PB∈(0,0.8)&Debt_Eq<0.5&CF_OA>0; rank z(−PB)+z(DY)+z(−Debt_Eq) take-all. DY>4% as SOFT score (annual/lumpy → hard gate kills 22/54 rows). ADV 1.4B micro. ROIC5Y unusable for rubber (corrupt: PHR 515%/DPR 290%).

| screen | window | net CAGR | Sharpe | MaxDD | B&H | edge |
|---|---|---|---|---|---|---|
| A fert | FULL 14-26 | 10.46% | 0.48 | −43.8% | 10.23% | **+0.22pp** (all edge=2021) |
| A fert | IS 14-19 | −0.53% | 0.07 | −26.2% | 8.96% | −9.49pp |
| A fert | OOS 20-26 | 21.98% | 0.74 | −43.8% | 11.45% | +10.53pp (entirely 2021 +204%/yr urea supercycle) |
| B chem | FULL 14-26 | −1.10% | 0.06 | −50.6% | 10.23% | **−11.34pp (NEGATIVE)** |
| B chem | OOS 20-26 | 5.67% | 0.32 | −50.6% | 11.45% | −5.78pp |
| C rubber | FULL 14-26 | 5.63% | 0.47 | **−12.5%** | 10.23% | −4.60pp (Calmar 0.45 > 0.24) |
| C rubber | OOS 20-26 | 4.48% | 0.47 | **−0.1%** | 11.45% | −6.97pp (waited/held cash) |

- **VERIFY**: DGC 2019-2020 **CAUGHT** (15mo) ✓; DGC supercycle 2021-22 only LATE (2022Q3+ — Rev_YoY base-effect ejects it during the actual spike → screen misses own thesis). DPM/DCM 2019-20 troughs CAUGHT ✓. **PHR land-bank NOT caught** (PB re-rated 0.66→2.45 before <0.8 window opened in prune era — land-as-alpha uncapturable, parallel GMD/PNJ/VCB). DPR held 36mo (persistent cheap name).
- **Orthogonality (custom30V | 8L top-25)**: FERT 47%|8% (already in c30V parking), CHEM 5%|0%, RUBB 13%|0%.
- **VERDICT**: lens not book (same family as prior 6 sectors). **A Fertilizer = cyclical-timing lens** — cheapness predictable, ALL return = one un-forecastable global catalyst (2021 urea), IS-neg, −44% DD, 47% already held → EVEB<6+high-DY = cheap-and-waiting tell, cycle-gate the size. **B Specialty chem = documented capture FAILURE** — caught DGC's pre-entry but net-negative; Rev_YoY gate mistimes + base-effect drops DGC in the actual supercycle → **DGC phosphorus alpha NOT reliably capturable from financials**; watchlist only. **C Rubber land-bank = DEFENSIVE value floor, not land-alpha** — lags B&H (−4.6pp) but DD −12.5% vs −43% market, Calmar 0.45>0.24 (DPR); the land-conversion alpha (PHR re-rate) uncapturable (priced before PB<0.8). Land-as-downside-floor = real; deploy as defensive deep-value lens inside V2.4.

## Steel + Building Materials — triple sub-sector screen (sector #8, job Taylor_20260630_065623, 2026-06-30)
- **Script**: `steel_buildmat_screen.py` → `data/steel_{steel,cement,spec}_monthly.csv`, `data/steel_buildmat_verdict.json`. Framework: `mike/agents/Taylor/steel_buildmat_valuation_framework.md`. AUDIT_END 2026-04-29.
- **Why 3 screens**: ICB lumps steel+cement+pipes; distinct economics → hand-curated. A=Steel cyclical (HPG/HSG/NKG/SMC/TLH/POM), B=Cement value (HT1/BCC), C=Specialty/pipe compounder (NTP/BMP/VCS).
- **Method**: point-in-time ASOF financials (≤120d stale), monthly EW, T+1, TC0.1%, hold CASH when no qualifier. **Self-check 0 VND: steel 0.0, cement 0.0, spec 6e-6 → PASS all 3.**
- **Screen A — Steel** EVEB∈(0,6)&PB<1.5&GPM_P0>GPM_P4&**Debt_Eq<2.0&IntCov>1.5**&CF_OA_3Y>0; rank z(−EVEB)+z(−PB)+z(GPM). ADV 144B (liquid).
- **Screen B — Cement** EVEB∈(0,6)&CF_OA_P0>0&Debt_Eq<1.5; rank z(−EVEB)+z(CF_OA). Only 2 liquid names, ADV 4.6B. **DY uncapturable in BQ (17/251 rows) → classic cement-yield screen unbuildable, pivoted to EVEB+cash.**
- **Screen C — Specialty/pipe** ROIC5Y>0.12&ROE5Y>0.15&PE<PE_MA1Y&CF_OA_3Y>0&Debt_Eq<0.5; rank z(−PE)+z(ROIC)+z(DY). 3 names, ADV 7B.

| screen | window | net CAGR | Sharpe | MaxDD | B&H | edge |
|---|---|---|---|---|---|---|
| A steel | FULL 14-26 | 10.07% | 0.44 | −53.1% | 10.23% | **−0.17pp** |
| A steel | IS 14-19 | −2.58% | −0.24 | −20.5% | 8.96% | −11.54pp |
| A steel | OOS 20-26 | 23.56% | 0.67 | −51.1% | 11.45% | +12.11pp (**entirely 2020 +180%/yr = one HSG COVID-bottom bet**) |
| B cement | FULL 14-26 | 4.17% | 0.29 | **−60.9%** | 10.23% | −6.07pp (worse DD than market) |
| B cement | OOS 20-26 | 10.63% | 0.48 | −60.9% | 11.45% | −0.82pp |
| C spec | FULL 14-26 | 10.04% | 0.47 | −46.8% | 10.23% | −0.20pp |
| C spec | IS 14-19 | 15.95% | 0.76 | −24.8% | 8.96% | **+6.99pp** |
| C spec | OOS 20-26 | 4.71% | 0.29 | −46.8% | 11.45% | **−6.74pp (NO OOS edge)** |

- **KEY FINDING — HPG structurally uncatchable by ANY value-trough steel screen**: HPG's cheap-PB windows always coincide with a disqualifier — negative IntCov in the 2013–14 capex era (IC −6.6), falling margins in 2019 (GPM_P0<GPM_P4), and never PB<1.5 post-2020 (quality floor ~1.0 only at the 2022 crash, where IntCov collapses to −0.6). Sensitivity EVEB<6/<8/<10 → **HPG = 0 months in all three**. The screen instead loads HSG/NKG (20+7 months), the leverage traps it was meant to avoid — they slip the gate when their leverage cyclically heals (HSG 2020 COVID bottom; HSG/NKG 2022 at the steel TOP, then −22.6% in 2022). HPG's return came from quality re-rating, not cheapness → not a value signal at all.
- **Leverage gate audit**: of 58 EVEB/PB/margin-passing steel rows, Debt_Eq<2&IntCov>1.5 keeps 34, rejects 24 (11 are HSG/NKG). The gate works as a VETO but cannot manufacture an HPG entry.
- **VERIFY**: HPG **MISSED** (0mo, structural); HSG leaked 20mo / NKG 7mo (cyclic leverage-heal at wrong times); BMP caught 72mo ✓, VCS 36mo ✓ (textbook compounders); **NTP documented-MISS** (ROIC5Y~10% + ~1.0× debt → fails both ROIC and clean-BS gates: 0/112 clean-BS rows); HT1 cement caught 38mo.
- **Orthogonality (custom30V | 8L top-25)**: STEEL 53%|20% (high beta, already in c30V parking), CEMENT 10%|5%, SPEC 10%|0% (orthogonal but thin).
- **VERDICT — weakest sector triple so far; all lens-not-book, steel screen actively FAILS**: **A Steel = capture FAILURE** — cannot own HPG (the only name worth owning), loads HSG/NKG leverage traps; full edge ≈0, the OOS +12pp is one un-repeatable 2020 HSG bounce; high beta. Only durable export = the **leverage VETO (Debt_Eq<2 & IntCov>1.5)** as a risk rule, NOT a stock picker. **B Cement = not investable** — 2 names, ADV 4.6B, DD −61% worse than market, DY uncapturable. **C Specialty/pipe = real IS compounder edge (+7pp) but NO OOS edge (−6.7pp), 3 names** — BMP/VCS are genuine high-ROIC clean-BS compounders (watchlist), but the signal is IS-driven (2015 BMP +66%) and de-rated OOS (2021/2025 negative). Watchlist/lens, not a sleeve.

---
## ENERGY / UTILITIES — triple screen (job Taylor_20260630_070640, 2026-06-30)
Script `energy_screen.py`. Outputs `data/energy_{util,oilsvc,renew}_monthly.csv`, `data/energy_verdict.json`. Framework `mike/agents/Taylor/energy_valuation_framework.md`. AUDIT_END 2026-04-29. Self-check 0 VND PASS (util/oilsvc/renew). Point-in-time monthly EW, ADV≥1B prune, ASOF financials ≤120d, net 0.1% TC.
- **Screen A — Mature utility** (VSH,SJD,NT2,PPC,REE,POW): EVEB∈(0,8)&**FCF>0**&CF_OA_3Y>0&Debt_Eq<2.0&IntCov>2.0; rank z(−EVEB)+z(FCF)+z(DY bonus). FCF=CF_OA_P0+CF_Invest_P0. ADV 9.3B.
- **Screen B — Oil services trough** (PVD,PVS,PVT): PB∈(0,0.8)&CF_OA_P0>0&Debt_Eq<2.0; rank z(−PB)+z(CF_OA). HIGH BETA (design: hold NEUTRAL/BULL only). ADV 44B.
- **Screen C — Renewables** (GEG,PC1,SBA): EVEB∈(0,10)&IntCov>1.5&Revenue_YoY>0&CF_OA_3Y>0; rank z(−EVEB)+z(DY bonus)+z(IntCov). ADV 14B.

| screen | window | net CAGR | Sharpe | MaxDD | B&H | edge |
|---|---|---|---|---|---|---|
| A util | FULL 14-26 | 4.16% | 0.31 | −43.5% | 10.23% | **−6.07pp** |
| A util | IS 14-19 | −3.23% | −0.18 | −31.7% | 8.96% | −12.19pp |
| A util | OOS 20-26 | 11.68% | 0.61 | −21.5% | 11.45% | +0.22pp (flat) |
| B oilsvc | FULL 14-26 | 11.06% | 0.48 | **−68.1%** | 10.23% | +0.82pp |
| B oilsvc | IS 14-19 | −5.99% | −0.04 | −50.6% | 8.96% | **−14.95pp** |
| B oilsvc | OOS 20-26 | 30.06% | 0.96 | −37.3% | 11.45% | **+18.60pp** (2020+21/2022+47/2025+18 oil rallies) |
| C renew | FULL 14-26 | 2.30% | 0.21 | −44.9% | 10.23% | **−7.94pp** |
| C renew | OOS 20-26 | 8.36% | 0.42 | −24.9% | 11.45% | −3.10pp |

- **DY-UNCAPTURABLE (sector-wide)**: DY only populated in dividend-DECLARATION quarters — UTIL 242/699, OILSVC 42/444 (PVD 0/79), RENEW 37/228. A hard DY>4% gate ejects payers in the 70% of quarters DY isn't recorded → DY used as scoring bonus, never a gate. Generalizes the cement-DY gap to all VN dividend-yield screens.
- **FCF>0 maturity gate (the real alpha)**: FCF=CF_OA_P0+CF_Invest_P0 separates paid-off cash machine from expansion capex. VERIFY perfect on VSH — Thượng-Kon-Tum expansion 2017-19 (FCF<0) REJECTED, post-capex 2022-24 (FCF>0) CAUGHT. Rejects 82/267 EVEB/leverage/IC-passing rows.
- **VERIFY**: SJD 44mo / NT2 63mo / POW 45mo CAUGHT; VSH expansion rejected + post-capex caught ✓; PVD 2016 trough CAUGHT (17mo), PVD 2014 pre-crash ABSENT ✓ (PB1.51), PVD 2020 Q2+ negative-CF rejected (of 182 cheap-PB rows CF_OA gate rejects 59); GEG present 36mo.
- **Orthogonality (custom30V | 8L top-25)**: UTIL 12.5%|0%, OILSVC 33.8%|31.5%, RENEW 2.5%|0%.
- **VERDICT — weakest group alongside steel; all lens-not-book**: **A Mature utility = structural LAGGARD** — cash-machine identification real (SJD/NT2/POW) but VN utilities are defensive, don't compound, FAIL IS (−12pp, 2019 thermal crush −30%), ~flat OOS. Park-cash/income tilt only, no alpha. **B Oil services = two-faced high-beta oil-cycle bet** — disaster IS (−15pp, 2017-19 oil malaise), star OOS (+18.6pp, 2020-26 recovery), **−68% DD un-ownable standalone** → tactical risk-on oil-cycle overlay ONLY (the design caveat); trough discipline mechanically sound. **C Renewables = documented capture FAILURE** — expensive+levered+FCF-negative *while* building FIT assets; windfall is a policy event, not a financial signal. Durable exports = DY-uncapturable rule + FCF>0 maturity gate (reusable across capex-heavy/dividend sectors).

---
## PHARMACEUTICALS — defensive P/E mean-reversion screen (job Taylor_20260630_072007, 2026-06-30)
Script `pharma_screen.py`. Outputs `data/pharma_monthly.csv`, `data/pharma_verdict.json`. Framework `mike/agents/Taylor/pharma_valuation_framework.md`. AUDIT_END 2026-04-29. Self-check 0 VND PASS. Point-in-time monthly EW, ADV≥1B prune, ASOF financials ≤120d, net 0.1% TC, CASH when no qualifier.
- **Universe**: DHG,DMC,IMP,TRA,DBD,MKP (generic + distribution; **no innovative R&D** — VN pharma is defensive recurring-demand, moat = brand-at-dispensing + foreign partner Taisho/Abbott/Daewoong). MKP not in prune; 5 names tradeable.
- **Screen (dispatched)**: PE>0 & PE<PE_MA1Y×0.9 (cheap vs own 1Y mean) & ROIC5Y>0.15 & ROE5Y>0.15 & GPM_P0≥GPM_P4−2pp & CF_OA_3Y>0 & Debt_Eq<0.5. Hold top-8 (=take-all, tiny univ); rank z(−PE/MA)+z(DY bonus)+z(GPM).

| window | net CAGR | Sharpe | MaxDD | B&H | edge |
|---|---|---|---|---|---|
| FULL 14-26 | 6.17% | 0.42 | −23.2% | 10.23% | **−4.06pp** |
| IS 14-19 | 5.94% | 0.42 | −0.1% | 8.96% | **−3.01pp** |
| OOS 20-26 | 6.38% | 0.42 | −16.9% | 11.45% | **−5.07pp** |
| **BASELINE B&H qualifying-names (no PE-timing)** | **15.96%** | **0.63** | **−35.4%** | 10.23% | **+5.73pp** |

- **THE DISPATCHED SCREEN FAILS (IS AND OOS).** Root cause: PE<MA1Y×0.9 fires rarely for defensive names that trade at/above their 1Y mean → **holds only 27/148 months**, in CASH 82% of the time → gives up every bull year (2016 +30%, 2017 +56%, 2025 +44% all missed = 0% sys). Mean-reversion timing is the WRONG tool for a compounder.
- **KEY FINDING — names compound, timing destroys it**: B&H the same qualifying names (DHG/DMC/DBD) full-period = **+15.96% CAGR / +5.73pp edge / DD −35% vs market −43%**. VN defensive pharma IS a genuine buy-and-hold outperformer; the "cheap-relative-to-self" entry filter is value-destructive (parks in cash through the compounding). → pharma is a **BUY-AND-HOLD lens, not a timed screen**.
- **IMP CAPTURE FAILURE (documented)**: of 8 PE-cheap IMP rows the ROE/ROIC>15% floor REJECTS 8 (100%); IMP ROE5Y~0.106, ROIC5Y~0.092 — the ETC-growth champion is structurally sub-15% return (EU-GMP capex + hospital-tender working capital) → un-screenable on a backward quality floor. The single best secular story is the one the quality gate ejects.
- **ROIC5Y artifact**: DMC/TRA show ROIC5Y 1.8–2.7 pre-2017 (scale artifact, tiny equity base; normalise ~0.17–0.20 by 2018). The >0.15 gate passes them anyway (no pick corruption) but ROIC value untrustworthy early — don't read as moat strength.
- **Liquidity decay**: DHG/IMP to 2026, DBD from 2017 (ADV 3.7B), DMC stops 2023-09, TRA stops 2022-07 → tradeable universe collapses to ~2–3 names post-2023. Median selected ADV 2.89B (thin).
- **Orthogonality**: vs custom30V **0.0%** | vs 8L top-25 **0.0%** — fully orthogonal (pharma never enters the liquid quality top-25), genuine diversifier but too thin/illiquid to be a book.
- **VERIFY**: DHG 15mo, DMC 8mo, DBD 16mo CAUGHT; TRA absent (never both cheap+qualifying in liquid window); IMP 0mo (correctly excluded by floor).
- **VERDICT — weakest-class alongside steel/energy; lens-not-book**: the dispatched mean-reversion screen actively FAILS both IS and OOS. Durable exports: (1) **VN defensive pharma compounds via BUY-AND-HOLD** (+5.7pp, lower DD) — DHG/DBD are watchlist holds, not timed trades; (2) **PE-mean-reversion timing is anti-edge for defensive compounders** (reusable warning); (3) **IMP/ETC-growth capture failure** — backward quality floors eject the best forward story.

---
## F&B (Food & Beverage) — dual screen (job Taylor_20260630_071901, 2026-06-30)
Script `fnb_screen.py`. Outputs `data/fnb_{fmcg,seafood}_monthly.csv`, `data/fnb_verdict.json`. Framework `mike/agents/Taylor/fnb_valuation_framework.md`. AUDIT_END 2026-04-29. Self-check 0 VND PASS (fmcg/seafood). Point-in-time monthly EW, ADV≥1B prune, ASOF financials ≤120d, net 0.1% TC.
- **Screen A — FMCG defensive** (VNM,SAB,MSN,MCH,QNS,KDC): PE>0 & PE<PE_MA1Y & ROE5Y>0.18 & gpm_avg8≥0.22 & gpm_CV<0.25; rank z(−pe_rel)+z(ROE5Y)+z(−gpm_CV)+z(DY bonus). ADV 24.9B.
- **Screen B — Seafood cyclical** (VHC,FMC,MPC,ANV,IDI,CMX): PB∈(0,1.2) & GPM_P0>GPM_P4 & CF_OA_3Y>0 & Debt_Eq<1.5; rank z(−PB)+z(GPM yoy)+z(CF_OA_3Y). ADV 3.6B.

| screen | window | net CAGR | Sharpe | MaxDD | B&H | edge |
|---|---|---|---|---|---|---|
| A fmcg | FULL 14-26 | 14.24% | 0.68 | −46.5% | 10.23% | **+4.01pp** (worse DD than market) |
| A fmcg | IS 14-19 | 19.97% | 0.88 | −33.3% | 8.96% | **+11.01pp** (2015 +43/2016 +34 VNM/MSN re-rating) |
| A fmcg | OOS 20-26 | 9.06% | 0.49 | −30.4% | 11.45% | **−2.39pp (NO OOS edge; 2021 −58pp bull miss)** |
| B seafood | FULL 14-26 | 9.47% | 0.44 | −36.4% | 10.23% | −0.76pp |
| B seafood | IS 14-19 | 0.61% | 0.11 | −12.0% | 8.96% | **−8.35pp** (mostly cash, missed 2016-17 bull) |
| B seafood | OOS 20-26 | 18.59% | 0.61 | −24.0% | 11.45% | **+7.14pp but ENTIRELY 2022 +137pp ASP super-cycle** (Sharpe flat +0.01) |

- **DY-UNCAPTURABLE (FMCG)**: DY only in dividend-declaration quarters — VNM 36/83, MSN 7/67, MCH 15/39, universe 359/754. Hard DY>3% gate ejects payers → DY scoring bonus only. Reconfirms energy/cement gap.
- **GPM-stability moat gate**: gpm_avg8≥22% AND CV<25% = high+stable brand margin. Keeps MCH(CV.05)/SAB(.12)/QNS(.11)/VNM(.18), REJECTS KDC(CV.38, serial restructurer). Of 300 PE-cheap+ROE>18% rows rejects 27 — all KDC.
- **Seafood duty-trap filter**: CF_OA_3Y>0 & Debt<1.5 rejects 90/133 cheap-PB+margin-up rows (ANV/FMC/IDI bad quarters; CMX fully excluded, Debt med3.5). **VHC = 0 trough entries** (PB floor 0.91, never <1.2) → quality structurally un-capturable as trough-buy; its return is compounding not cheapness.
- **VERIFY**: VNM 89mo / MCH 37mo / SAB 77mo CAUGHT; KDC 7mo only (GPM gate) ✓; VHC 0 trough mo (correct); ANV 6mo / MPC 4mo duty-troughs CAUGHT; CMX 0mo (Debt) ✓.
- **Orthogonality (custom30V | 8L top-25)**: FMCG 15.1%|0.0%, SEAFOOD 10.8%|2.6% (both orthogonal, thin).
- **Caveat**: SAB/MCH/QNS only in liquid prune from 2017 → FMCG IS leans on VNM/MSN 2015-16 megacap re-rating that doesn't repeat OOS.
- **VERDICT — weak tier (steel/energy company); both lens-not-book**: **A FMCG = IS-driven, NO OOS edge** — real quality/defensive lens (rejects KDC cleanly) but +11pp IS → −2.4pp OOS, worse-than-market DD, lags bull years; watchlist/risk-off park, not an alpha picker (mirrors retail). **B Seafood = single-event OOS** — fails IS −8pp, +7pp OOS is ENTIRELY the 2022 ASP super-cycle, flat Sharpe, ADV 3.6B; cyclical trough LENS (the duty-trap filter is the reusable export) not a standalone book. Durable exports = DY-uncapturable rule (reconfirmed) + GPM-stability moat gate + seafood duty-cycle value-trap filter + "VHC un-capturable as trough-buy".

## Technology (IT Services) screen+backtest — Taylor_20260630_071941 (2026-06-30)
- **Script:** `tech_screen.py` | **Framework:** `mike/agents/Taylor/tech_valuation_framework.md` | **AUDIT_END** 2026-06-26
- **Outputs:** `data/tech_fpt_lens.csv`, `data/tech_basket_{lit,vn}_monthly.csv`, `data/tech_verdict.json`
- **Structural reality:** VN tech = IT services (Infosys/TCS archetype); liquid+quality universe is essentially ONE name (FPT). CMG ROIC5Y 7.8% & liquid only 2024; ELC/ITD low-quality micro-caps; CTR (ROIC 21-24%) is Viettel tower-co/telecom-infra not software.
- **FPT timing lens (real):** flagged (PE<PE_MA1Y×0.9 + ROIC5Y>12 & ROE5Y>15 & NPM stable) n=26 fwd-12M **+50.6% / 88% win** vs unflagged n=105 +24.5% / 76% → **spread +26.0pp**.
- **Tradeable basket (lens-not-book):** G_LIT (dispatch ROIC>18+RevYoY>12) holds **0 names all 2014-2026** (universe collapse). G_VN (ROIC>12) holds FPT 37/148 mo, Full CAGR 2.82% vs B&H 10.23% = **-7.42pp** (IS -10.1, OOS -4.78). Edge lives in 12M-hold, lost to cash-drag in monthly rebal.
- **Self-check:** lit 0.000000 / vn 0.000001 VND → PASS. Orthogonality G_VN 32.4% vs custom30V | 0% vs 8L top-25. Median sel ADV 96.9B.
- **Durable exports:** (1) ROIC5Y>18 is Infosys/TCS bar — FPT blended 12-17% (Telecom+education dilution), use >12; (2) FPT RevYoY 2015-18 is FRT/Synnex divestment artifact, never gate on it; (3) cheap-vs-own-PE + quality = real FPT entry-timing lens (2018/2022-23/2025-26 windows); (4) CTR = telecom-infra not software.
- **Verify:** 2018 divestment entry CAUGHT G_VN / MISSED G_LIT; 2022-23 slowdown CAUGHT; 2024 euphoria ABSENT; 2025 cheap re-entry caught. All as predicted.

## Securities / Brokerage (sector #13) — cyclical-recovery screen + DT5G overlay (job Taylor_20260630_073104, 2026-06-30)
Script `securities_screen.py`. Outputs `data/securities_{screen,screen_dt5g,basket}_monthly.csv`, `data/securities_verdict.json`. Framework `mike/agents/Taylor/securities_valuation_framework.md`. AUDIT_END 2026-04-29. Self-check 0 VND PASS (screen 1.9e-5 / dt5g 2.7e-5 / basket 1.7e-5). Point-in-time monthly EW top-8, ADV≥1B prune, ASOF financials ≤120d, net 0.1% TC.
- **Universe (17, ADV-liquid):** SSI,VCI,HCM,VND,MBS,SHS,AGR,BSI,CTS,VIX,FTS,VDS,BVS,APG,TVS,ORS,EVS. Median selected ADV **21.2B — genuinely tradeable** (unlike pharma/tech/telecom). Backtestable across IS/OOS (SSI/HCM/VND/SHS/CTS liquid from 2013).
- **Screen:** PB∈(0,1.8) & ROE_Trailing>0.08 & ROE_Trailing>ROE3Y (inflection) & NP_P0>0 & IntCov_P0>1.5(NULL-tolerant); rank z(−PB)+z(ROE_Trailing)+z(ROE_Trailing−ROE3Y). Qual med 2/mo, cash 40/148 mo. **Beta 1.27 (screen) / 1.60 (basket) — highest-beta sector in the 13-sector sweep.**

| view | window | net CAGR | Sharpe | MaxDD | Calmar | bench | edge |
|---|---|---|---|---|---|---|---|
| screen vs **broker basket** (KEY) | FULL 14-26 | 17.74% | 0.57 | −65.7% | 0.27 | basket 21.83% (DD−60.8) | **−4.10pp, worse Sharpe** |
| screen vs broker basket | IS 14-19 | 6.43% | 0.34 | −47.5% | 0.14 | basket 8.63% | **−2.19pp** |
| screen vs broker basket | OOS 20-26 | 29.55% | 0.72 | −65.7% | 0.45 | basket 35.82% | **−6.27pp** |
| screen vs VNINDEX | FULL 14-26 | 17.74% | 0.57 | −65.7% | 0.27 | VNI 10.23% | +7.50pp but DD −65.7 / Sharpe −0.03 |
| **DT5G-gated** screen vs VNINDEX | FULL 14-26 | **27.74%** | **0.79** | **−31.7%** | **0.88** | VNI 10.23% (DD−43.2) | **+17.50pp, +0.19 Sharpe, HALF the DD** |
| DT5G-gated vs VNINDEX | OOS 20-26 | 44.42% | 0.96 | −31.7% | 1.40 | VNI 11.45% | +32.96pp |

- **STANDALONE CROSS-SECTIONAL SCREEN = FAIL**: loses to simply OWNING ALL BROKERS on CAGR **AND** Sharpe across FULL/IS/OOS. The ROE_Trailing>ROE3Y inflection gate is a LATE confirmation (not a trough-buy): it sits in cash through the basket's **+99.1% 2023** (screen 0.0%), and clips the recovery legs (2017 basket +130.5% vs screen +45.4%; 2020 basket +97.2% vs +40.9%). Ungated screen DD −65.7% is WORSE than the always-invested basket −60.8% — the valuation/cash-timing is mistimed (in cash during recoveries, fully loaded into 2022).
- **THE DURABLE EXPORT — brokerage is the ONE sector where DT5G is a RETURN-ENHANCER, not just insurance.** Gating the screen to cash in DT5G {CRISIS,BEAR} transforms it: Full 17.74→**27.74% CAGR**, Calmar 0.27→**0.88**, DD −65.7→**−31.7%** (better than VNINDEX). Per-year proof it is multi-episode (not single-event): 2018 −38.0%→+9.9%, 2022 −49.3%→−19.0%, while keeping the 2021 super-cycle (+298%→+396% via the late-2020 entry). Mechanism: broker beta ~1.3 and its worst-drawdown quarters (2018, 2022) ARE the market's CRISIS/BEAR states → the de-risk gate halves DD and ADDS ~10pp CAGR. Concretely validates the dispatch's "high-beta → needs DT5G gate."
- **Reusable rules:** (1) **PB-primary, not PE** for brokers (NP too cyclical); (2) **IntCov replaces Debt_Eq** — margin debt is by-design, a HARD IntCov>1.5 gate would drop 241/405 passing rows (116 known-bad + 125 NULL-coverage e.g. FTS) so NULL-tolerant; known-bad-IntCov names = SSI/SHS/VND/VIX/BSI/CTS/MBS/VDS/BVS at over-levered points; (3) **ROE_Trailing>ROE3Y = LATE confirmation not trough-pick** (re-crosses above the still-elevated 3Y base only mid-recovery); (4) **brokerage = highest-beta sector** (β 1.27 screen / 1.60 basket).
- **Caveat:** OOS CAGR leans on the 2021 margin-lending super-cycle (+298%/+396%), a once-a-generation event; but the DT5G edge is NOT single-event (also 2018 + 2022). Orthogonality: custom30V 33.5% | 8L top-25 6.9%. Median ADV 21.2B.
- **VERIFY:** VND ROE-recovery 2020-21 CAUGHT (9mo from 2020-10); SHS 2021 CAUGHT (4mo); SSI 2025 recovery CAUGHT (6mo); 2021-H2 euphoria-top entries only 1mo (PB>3 cap works); cash through 2022H2-2023 crash 12mo (NP/ROE gates work).
- **VERDICT — lens-not-book as a screen, BUT a genuine DT5G use-case.** The cross-sectional pick fails (own the sector beats it); the *macro de-risk overlay on a high-beta sector* is the real, deployable finding — and it's the strongest evidence in the sweep that DT5G adds return (not just insurance) precisely where beta is highest.

## 2026-06-30 — Sector #14 AVIATION dual screen (job Taylor_20260630_074607)
- **Scripts:** `aviation_screen.py` | framework `mike/agents/Taylor/aviation_valuation_framework.md` | outputs `data/aviation_infra_monthly.csv`, `data/aviation_airline_monthly.csv`, `data/aviation_verdict.json`. AUDIT_END 2026-04-29. Self-check infra 0.000000 / airline 0.000000 VND → PASS.
- **Universe (prune):** airport/cargo infra = ACV, SCS, NCT, SGN (by NAME — ICB is inconsistent: SCS is tagged 5751 'airline' but is a net-cash cargo terminal); airlines = HVN, VJC. YOUNG sector: ACV/HVN/VJC/SCS listed 2017, only NCT has 2015+ → IS 2014-19 ≈ 2017-19 (~3y); OOS 2020-26 = COVID aviation shock (sector-specific, not a market regime). Economics outweigh the short backtest curve here.
- **Screen A (airport/cargo infra, EVEB<12 + ROIC5Y≥10% + CF_OA_3Y>0 + (FCF>0 OR DY>4%) + IntCov NaN-or>2 + Rev_YoY≥−10%):** FULL CAGR **3.98%** vs B&H 10.23% (**−6.25pp**); IS −8.45pp; OOS −4.07pp. FAILS both windows. Holds median **1 name** (NCT 69mo + SCS 43mo + SGN 15mo; **ACV 0mo** — EVEB never<12 + DY=0 + Long-Thanh capex ⇒ perpetual FCF<0, value screen never buys it). Killed by 1-name idiosyncratic drag (2025 SCS −32.3% = −76.5pp) + early cash-drag. Orthogonality custom30V **0.0%** / 8L top-25 **0.0%** (genuinely un-owned names) but doesn't beat market. Median selected ADV **1.6B = microcap-thin**.
- **Screen B (airline trough-buy, PB<1 + CF_OA>0 + IntCov>1 + NP>0):** **STRUCTURALLY EMPTY — 0 qualifiers ever.** HVN excluded (PB=0 = NEGATIVE EQUITY 2021-24, near-bankruptcy value trap); VJC excluded (premium LCC, PB never<1, DY=0). **No VN airline trough-buy exists.**
- **Buy-and-hold reality (2017-10 .. 2026-06, vs VNINDEX 10.21%/DD−45%):** SCS **5.50%**/DD−52% (45% ROIC franchise but listed expensive, de-rated), ACV **1.15%**/DD−63% (best franchise, worst stock — perpetual-expensive + Long-Thanh dilution), NCT **17.53%**/DD−51% (ONLY beater — cheapest cargo gem, microcap-illiquid), VJC 8.83%/DD−57%, HVN 6.02%/**DD−80.6%**. Even holding the gems mostly LAGS the index — sharper negative than pharma (where B&H won).
- **Durable exports:** (1) **airline trough-buy does NOT exist in VN** — empty screen; **HVN = permanent-exclude** (negative equity), VJC never cheap; (2) **screen aviation by NAME not ICB** (SCS misclassified 5751); (3) **ACV = best monopoly franchise but value-uncapturable** (EVEB never<12 + DY0 + Long-Thanh FCF drag → GARP/quality-growth, not value); (4) **DY-uncapturable reconfirmed** (ACV DY=0, cargo DY lumpy); (5) cargo terminals (SCS/NCT/SGN) = real net-cash high-ROIC monopolies but microcap-thin (ADV 1.6B) + 1-name concentration + listed-expensive de-rate → buy-and-hold lens for patient single-name, NOT a timed book.
- **VERDICT — weakest sector group alongside steel/energy.** Both sub-screens fail; even the franchise-quality lens mostly fails to beat the index on a hold basis (only illiquid NCT wins). No investable aviation book.

## custom30V × 7-name Permanent-Exclude — IS/OOS/Full NAV backtest (2026-06-30, Taylor, job Taylor_20260630_102153)
**Q (Mike dispatch):** Re-run custom30V (yieldcombo = rank(1/PE)+rank(1/PCF), top-30, namecap0.10, gate_rating≤3, q2m5, PE>0&PCF>0, ticker_prune pool) with the sector-sweep **Permanent-Exclude list = HVN,VJC,NVL,KDC,VHC,HPG,HSG** applied BEFORE rank. Better/worse/wash vs baseline? Wire?
**Method:** `custom30v_exclude_audit.py` — same `cb.build_pit` machinery for both arms, only the gated pool differs (`BASKET_EXCLUDE`). Pure-selection own-NAV (NO DT5G overlay) → isolates the selection effect; DT5G gate scales both NAVs by the identical exposure path so the delta SIGN is overlay-invariant. Self-check: NAV 1000→26246× baseline, 3111 daily rows both arms. Cache `data/c30v_exclude_cache/`. AUDIT_END 2026-06-15.
**Q1 — how often the exclude names even appear in baseline (48 rebals, 1440 slots):** VJC 0% / NVL 0% (yieldcombo gate+PE/PCF>0 already drops them — never selected); HVN 6.2% (3 rebals); KDC 8.3%; **HSG 27.1%, VHC 45.8%, HPG 56.2%** (the three that actually bind). Total flagged = **69/1440 = 4.8% of all basket slots ever**. So the exclude effectively only acts on HPG/VHC/HSG (+ rare KDC/HVN).
**Metrics (pure-selection NAV, CAGR / Sharpe / MaxDD / Calmar):**
- **FULL 2014→now:** baseline 29.94% / 1.24 / −39.2% / 0.76 → exclude 28.94% / 1.23 / −39.6% / 0.73. **Δ −1.00pp CAGR, −0.01 Sh, −0.4pp DD, −0.03 Cal.**
- **IS 2014-2019:** baseline 22.61% / 1.10 / −32.1% → exclude 20.08% / 1.03 / −33.6%. **Δ −2.52pp CAGR, −0.07 Sh, −1.5pp DD — clear HURT.**
- **OOS 2020→now:** baseline 36.94% / 1.34 / −39.2% → exclude 37.59% / 1.39 / −39.6%. **Δ +0.65pp CAGR, +0.04 Sh, −0.4pp DD — marginal HELP.**
- By-year: OOS "help" is **entirely 2021 (+12.3pp** from dropping steel HPG/HSG in the steel-blowoff-then-crash year); every other OOS year flat-to-negative (2020 −4.5, 2023 −2.1, 2025 −1.3). Single-event, not structural.
**VERDICT — DO NOT WIRE (worse-to-wash, anti-robust signature).** Excluding the 7 names HURTS Full (−1.0pp) and HURTS IS clearly (−2.52pp) while only marginally helping OOS (+0.65pp), and that OOS help is one year (2021). Hurt-IS / help-OOS-via-single-year is the classic overfit/noise signature → reject. **Root cause:** the Permanent-Exclude list is a *sector-sweep value-trap* tool; it's too blunt for the custom30V *parking* basket — VJC/NVL never even pass the yieldcombo gate, and the names it does remove (HPG/VHC, 56%/46% of rebals) are legitimately-selected liquid quality cyclicals that contributed positively IS, NOT the negative-equity traps (HVN PB=0) the list was built to catch. Removing them strips real basket return. **custom30V parking stays as-is (production yieldcombo top-30/cap0.10, no name-exclude overlay).** AUDIT_END 2026-06-15.

## 2026-06-30 — REVIEW: "phương án composite mới (thuần methodological)" (job Taylor_20260630_163930)
Scheduled self-note to review whether to evolve the 8L composite via a *purely methodological* candidate (re-weight/drop axes, coverage-aware aggregation — NO new factors/data). **No automated run today** (these are not on cron; last outputs May/Jun). Ran both candidate scripts fresh on existing panels (`value_panel_2014.csv` Jun-19, `fundamental_rating_all.csv` May-10). PY=wc_venv.
- **(1) composite_v3_sweep.py — the VALUE lens that IS live ("v3 lens" ey+cfy+ps, coverage-aware Σwᵢpᵢ/Σwᵢ, no fillna .5 bias).** v3 beats the v2 shape (0.35·pct(−pb_z)+0.65·pct(1/PE)) on IC: BROAD profit_2M **v2 +0.077 → v3 ~+0.090**; per-route COMPOUNDER +0.103 (v2 +0.084) / CYCLICAL +0.113 (+0.052) / CONSUMER +0.129 (+0.091) / SECURITIES +0.072 (+0.047) / RE +0.045 (+0.020). **Weight plateau FLAT** (12 weight sets all IC 0.089–0.091 = robust, not knife-edge). **By-year COMPOUNDER every year 2014–2026 POSITIVE** (IS+OOS both clean, min 2014 +0.02). ⇒ the live value-lens v3 is RE-VALIDATED robust; nothing to change.
- **(2) fa_ic_composites.py — drop negative-IC axes from a 7-axis LINEAR composite (LEGACY; NOT what rating_8l.py v2 runs).** IS per-axis IC: health **−0.091**, valuation **−0.104** (negative) yet carry 18% combined weight in CUR7. Dropping them:
  | composite | IS_IC | OOS_IC | ALL_IC | OOS decile spread |
  |---|---|---|---|---|
  | CUR7 (current 7ax hand-wt) | +0.1119 | +0.0882 | +0.0946 | +6.53pp |
  | EW5 (drop heal+valu) | +0.1376 | +0.0890 | +0.1018 | **+6.83pp** |
  | CORE4 (qual+stab+cash+shar) | +0.1341 | **+0.0927** | **+0.1037** | +5.89pp |
  | ICW (pos-IC, IS-fit, 5ax) | +0.1397 | +0.0894 | +0.1025 | +6.69pp |
  Robust-signed (CORE4/EW5 beat CUR7 in BOTH IS & OOS on IC) AND simpler — opposite of overfit. BUT OOS magnitude tiny (+0.0045), tradeable **decile spread a WASH** (CORE4 5.89<CUR7 6.53; EW5 6.83 marginal), and this 7-axis linear composite is **NOT in production** (rating_8l.py v2 = 2-axis quality-scorecard × pb_z).
- **GO-LIVE VERDICT: NO — keep production as-is for the 2026-06-30 go-live.** (a) Trading selector = yieldcombo (rating-blind); rating gate = binary ≤3 → a rating-composite tweak barely moves NAV. (b) Registry already ruled **v3-composite-AS-SELECTOR = IS-overfit** (OOS −0.78pp, THREAD b 06-22) — settled. (c) The value-lens v3 is already live and re-confirmed robust → nothing to change. (d) The fa_ic "drop health+valuation" is clean IC hygiene but targets a legacy composite, doesn't widen the tradeable spread, immaterial magnitude. (e) META + go-live-today rule: de-risk, don't add complexity. **Durable export:** IF a linear multi-axis rating ever becomes production, DROP health+valuation (negative IC); equal-weight CORE4 is the robust-simplest form. Optional post-go-live hygiene only — must clear a NAV self-check backtest first; NOT a go-live blocker or enhancer.

---
## Composite (8L axis-2 value_score_v2) as ENTRY SELECTOR — NO GO-LIVE (2026-07-01, Taylor)
**Q:** Does 8L axis-2 composite `value_score_v2` (0.35·pb_z-rel + 0.65·(1/PE sector-neutral) + CFO-3Y confirm ± + track-record bonus + TRAP-gate ROE_Min3Y<0), used as a monthly top-N equal-weight ENTRY SELECTOR, beat the production parking basket custom30V (yieldcombo 1/PE+1/PCF top-30)?
**Cmd:** `python3 composite_selector_backtest.py` (self-contained, reads only `data/value_panel_2014.csv`; composite replicated byte-faithful from `rating_8l.py` L466-611). AUDIT_END 2026-06-18. TC=0.1%/side, equal-weight, monthly rebal, 150 month-end snaps.
**Result (gross panel, same engine both):**
| selector | Full CAGR | OOS CAGR | Sharpe(F) | MaxDD(F) |
|---|---|---|---|---|
| custom30V yieldcombo top20 | 57.05% | 64.76% | 2.24 | -26.2% |
| composite+TRAP top20 | 45.83% | 50.11% | 2.12 | -19.2% |
| custom30V yieldcombo top30 | 50.58% | 61.15% | 2.17 | -24.7% |
| composite+TRAP top30 | 43.50% | 50.33% | 2.19 | -19.8% |
- Head-to-head: composite LOSES every window — top20 Full **−11.22pp** / OOS **−14.65pp**; top30 Full **−7.08pp** / OOS **−10.81pp**.
- By-year (top30): composite beats custom30V only **5/13 yrs**; loses the big-return years hard (2016 −20.8, 2017 −24.0, 2020 −25.7, 2021 −71.5pp). Not an IS artifact — OOS gap is WIDER than IS.
- LIQUID variant (turnover≥1bn, parking-realistic): composite 17.9-18.5% vs custom30V 24.9-26.2% — still loses, worse Sharpe (0.74 vs 1.01) and equal/worse DD.
- NOTE: raw 40-65% panel CAGRs are the known curated-panel/survivorship/no-capacity inflation (auditable live ceiling ~25.7%@50B). The **relative** comparison on identical engine is the valid signal.
**Why it loses:** composite is a quality-cheap DIAGNOSTIC (rating-display) design. Sector-neutralizing 1/PE strips the low-PE-sector tilt that earns return in VN; track-record/proven5y bonuses tilt to priced-in quality (rating_8l.py's own note: highest-track-record names underperform on return). It trades ~7-15pp CAGR for modestly lower DD — wrong tradeoff for a parking sleeve whose job is return on idle cash (DD already managed by DT5G gate + book alloc).
**VERDICT: NO GO-LIVE as entry/parking selector. Keep composite as-is = diagnostic/rating display axis. custom30V remains the parking selector. Production V2.4 unchanged.**

## EXTREME-regime execution gate — backtest validation (Taylor, 2026-07-01, job Taylor_20260701_052919)
Validates the mechanism in `exec_extreme_regime_proposal.md` §3 BEFORE production wire. Data: vnstock VCI 15m intraday (only reaches 2023-10-30 → **2022 crash NOT replayable intraday**), 18 Tier-1 names × 8 market-wide crash episodes (2024-04..2026-03). Scripts: `fetch_intraday_cache.py`, `extreme_replay.py`; raw `data/extreme_replay.csv`; doc `data/extreme_regime_backtest.md`.

**SELL side** — static −3% cap strands same-day (gap-lock) on **22/126 down-sells (17%)** [Rev2: NaN pad-bar filter fixed]. On those:
| n=22 | NORMAL static→carry | EXTREME sell-to-floor |
|---|---|---|
| mean exit | −5.55% | −6.55% (**−1.0pp**) |
| worst-case | **−13.4%** | −6.9% |
| std | 3.8pp | **0.3pp** |
| same-day fill | 0% | 100% |
Split: Apr-2025 multi-day CASCADE **+2.63pp** (avoids next −7% day) vs Mar-2026 1-day DIP **−3.08pp** (locks bottom, misses bounce). Beat NORMAL on 9/22 (41%) but losses bounded, wins avoid the fat left tail.

**BUY-pause** — pausing = **−1.07pp** worse mean entry (skips cheapest day), tail p95 +5.6pp protects vs cascade.

**VERDICT: MECHANISM VALIDATED AS TAIL-INSURANCE, NOT a return-enhancer** — trades ~1pp mean for tail compression (worst −13.4%→−6.9%, std 3.8→0.3pp, fill 0→100%). Same profile as DT5G ("insurance, not return"). Causally can't distinguish cascade vs dip → bounds outcome either way. Net-benefit sign is regime-dependent and NOT cleanly establishable (no 2022 intraday, no order-book, thin dip-dominated sample). **→ Code DEFAULT-OFF per approved design; deliberate activation only; do NOT re-tune to history.**

**Step-2 — quant-skeptic verify: CONFIRMED (medium confidence)** [2026-07-01]. First pass was INCONCLUSIVE on 3 audit defects; Rev2 closed all: (1) VCI NaN 23:45 pad-bar dropped → down-day filter fires, denominator corrected 144(mislabelled)→**126** real <−3%-close sells, strand 17%; (2) buy-pause leg now scripted + persisted `data/extreme_replay_buy.csv` (n=126); (3) tautological self-check replaced by a genuine independent recompute from raw parquet vs CSV — **IDENTITY PASS to 1e-9**. Skeptic re-ran extreme_replay.py: every headline number reproduced exactly. Disclosed weakness (thin 2-episode / 14-of-22-from-one-day sample; carry-to-next-close assumption) honestly stated; finding scoped to mechanism-validity/tail-insurance, not a robust return edge → CONFIRMED. Log `mike/logs/verify_20260701_060116.log`.

**Step-3 — coded DEFAULT-OFF** [2026-07-01]. `config.py`: +`extreme_regime_enabled=False`, `extreme_band=0.03`, `extreme_move_z=3.0`, `extreme_slice_mult=0.25`, `extreme_cooldown_min=15`. `executor.py`: `_extreme_regime()` (2-poll confirm + cooldown; trigger (i) within-band-of-floor [backtest-validated] OR (ii) r15 down-move > z×rvol_20d; fail-safe→False), `_extreme_slice_mult()`, sell-to-floor branch in `_limit_price`, buy-pause + faster cadence in `_place_slices`/`_cancel_stale`. **NORMAL path byte-identical when OFF** (diff = 86 ins / 6 gated-line edits, each ×1.0/False-preserving). Regression self-check `extreme_regime_selfcheck.py`: **14/14 PASS** — OFF byte-identical (sell caps at −3%, buy places normally, mult ×1.0), ON fires (2-poll arm, sell→floor, buy paused + EXTREME_PAUSE journaled, cadence ×0.25).

**Paper-trade gate decision (Taylor): 4 weeks (~20 sessions) flag-ON in PAPER only, NOT calendar-wait for a real episode.** Rationale: feature trips only in rare extreme moves → even 3-month calendar paper likely observes ZERO episodes, so calendar time proves nothing about the extreme path. Binding validation instead = (a) episode-level backtest CONFIRMED [done]; (b) **week-1 synthetic stress-injection** through the live paper wiring (feed a fabricated quote sequence to floor / >3σ r15, assert arm→sell-to-floor→buy-pause→cadence, no real crash needed); (c) **~4 weeks / ~20 paper sessions** with the flag ON to prove **ZERO false-triggers on benign days** + zero NORMAL-path interference under real live-data noise; (d) explicit **user sign-off** before any LIVE enable. Why 4 weeks not 2 / not a quarter: 2 wks (~10 sessions) is thin for a zero-false-trigger claim across varied conditions; a quarter is the fleet norm for RETURN edges (must survive OOS) but this is default-OFF insurance, not return — waiting for a possibly-absent tail event adds no info beyond backtest+injection. **Live remains DEFAULT-OFF; Taylor did NOT enable anywhere.**

**Paper-trading START (Taylor, 2026-07-01, job Taylor_20260701_083148) — USER APPROVED live in-session.** Enabled `extreme_regime_enabled=True` **PAPER-ONLY** via the `main` paper-account `overrides` in `secrets/trading_bot_accounts.json` (same paper-only pattern as `gap_adaptive_enabled`). Verified through the REAL `load_config()`/`load_accounts()` resolution: paper `main`=True, `SpaceX`/live=**False**, `RocketX`/`dnse_main`=False, global `DEFAULTS`=**False** (untouched). Approved params unchanged: band 0.03 / z 3.0 / slice_mult 0.25 / cooldown 15.
- **Week-1 stress-injection: 24/24 PASS** (`mike/agents/Taylor/stress_extreme_regime.py`, drives the genuine `Executor` + real `Quote` objects via a recording FakeBroker, not a re-impl). Proven through the real code path: (1) ARM 2-poll confirm on trigger (i) near-floor limit-down AND (ii) r15<−3σ, cooldown≈15min set; (2) armed SELL → `_place_slices` prices at daily **floor 18600** (sell-to-floor) vs NORMAL stranded at ref×(1−3%)=19400; (3) armed BUY → **EXTREME_PAUSE**, no `place_order`; (4) `_extreme_slice_mult`=0.25 → `_cancel_stale` cancels a 3-min child (2-min thresh armed) that OFF (8-min) keeps. **Negative controls:** NORMAL quote never arms over 10 polls; **LIVE (SpaceX) effective cfg never arms** on the same limit-down stress + slice_mult stays 1.0. No real `SpaceX`/`main` execution logs touched (throwaway labels; verified live files unmodified).
- **Window: start 2026-07-01 → target end ~2026-07-28 (~20 T2–T6 sessions).** Remaining conditions before any LIVE enable (all must hold): (a) **ZERO false-triggers** across ~4 weeks / ~20 benign paper sessions under real live-data noise; (b) **zero NORMAL-path interference**; (c) explicit **user sign-off**. **Live stays DEFAULT-OFF — Taylor did NOT enable anywhere on live.**

## Vol-scaled buy chase-cap (patch#3) — NET entry-quality backtest (Taylor, 2026-07-01, job Taylor_20260701_102950)
User-approved direction (from job Taylor_20260701_102033). Proposal: buy chase ceiling
`cap_pct = clamp(k*rvol_20d, floor=0.015, ceil=0.04)`, k=2.0; `cap = ref*(1+cap_pct)`. Monotone-safe
(floor == current static `max_chase_pct_buy` → only widens, never tightens), fail-safe to static 1.5%
when `rvol_20d` missing/≤0, independent of allocator/selection (touches ONLY `_limit_price` buy branch).
Motivation = go-live failure: static 1.5% cap 0-filled a whole 9-bank basket on a gap-up morning.

**Substrate** `data/intraday_1m` — 16 liquid VN names, 1-min bars 2023-10..2026-04, **4487 gap-up
decisions**. Real fill CEILING sim (matches `executor.py::_limit_price`): `L=ref*(1+cap)`; fill iff
intraday_low≤L; fill_price=`min(open,L)` (pessimistic-consistent for BOTH caps → fair comparison).
`rvol_20d` & forward returns from the same daily-close series. Scripts: `mike/agents/Taylor/chase_cap_backtest.py`
(+ `chase_cap_backtest_raw.csv`), self-check `chase_cap_selfcheck.py`. Self-check ALL PASS (identity 0.0,
monotone, raw-recompute err 0.0).

| metric | static 1.5% | vol-scale | Δ |
|---|---|---|---|
| fill-rate on gap-ups | 97.5% | 99.3% | +1.8pp |
| fill-rate on BINDING subset (open>ref×1.015, 12.1% of gap-ups) | 79.4% | 94.5% | **+15pp** |
| entry-price, both-filled (n=4375) | — | +6.6 bps worse (worse on only 9.8%) | cost |
| NET captured fwd20 / decision (miss=0) | +1.65% | +1.69% | +0.04pp (t=1.26, **NOT sig**) |

- **Value is in the TAIL, not the average.** Trades static MISSES but vol CATCHES: n=82, fwd20 mean
  **+5.90%** / median +3.91% / **win 68%** (real breakout winners). Benefit/cost asymmetry **≈1.67×**
  (48380 vs 28888 bps-days). Correlated broad gap-up mornings replay the go-live 0-fill failure:
  **2025-04-10 static missed 12/12 names, 2026-04-08 10/11, 2025-04-11 6/10** (post-tariff V-bounces).
- **Robust plateau** (not overfit): k/ceil grid NET Δ +0.026..+0.054pp flat across k∈[1.5,3.0]×ceil∈[3,5]%;
  k=2.0/ceil=4% sits mid-plateau. `floor=0.015` pinned to the static cap by construction (monotone-safe).
- **Per-year** Δ consistent positive sign +0.03..+0.05pp (2023/24/25/26).
- **Caveats (disclosed):** 16 LIQUID names only — illiquid tail has thinner books, gap-ups less likely to
  dip back → static misses MORE there, so this is a **LOWER bound** on the benefit (untested). Daily-proxy
  fill (zero size-impact — 50B basket chasing +4% into correlated gap-ups may slip beyond model). ~2.5y,
  tail events rare → thin on the exact tail. Single-name fwd return, no allocator interaction (by design).

**VERDICT: TAIL-INSURANCE / fill-reliability fix, NOT an average return-enhancer** (same class as DT5G +
EXTREME-regime). Average NET ~0 but favorable asymmetry + fixes the real correlated-basket 0-fill go-live
failure at trivial common-case cost (+6.6bps, monotone-safe, fail-safe). Do NOT re-tune to history.

**quant-skeptic verify: CONFIRMED (high confidence)** [2026-07-01, log `mike/logs/verify_20260701_103636.log`].
Re-ran the script from scratch → byte-identical headlines; independently reproduced the k/ceil grid; verified
no look-ahead (cap uses only prior-20d vol, fill uses execution-day intraday low), floor pinned to static
(monotone/fail-safe), correctly classed insurance-not-return. Killer objection = zero size-impact in the fill
model / thin tail / liquid-only — disclosed and mitigated by DEFAULT-OFF + paper-validate + sign-off.

**Coded DEFAULT-OFF** [2026-07-01]. `config.py`: +`chase_cap_vol_scale_enabled=False`, `chase_cap_vol_k=2.0`,
`chase_cap_vol_ceil=0.04`. `executor.py`: `_buy_chase_pct()` helper (static when OFF / rvol absent; else
`clamp(k*rvol_20d, static, ceil)`), used in `_limit_price` buy branch; `_load_gap_ref_data` guard widened to
load `rvol_20d` when the flag is on. **OFF byte-identical** (helper returns static → cap path unchanged).
Regression self-check `chase_cap_selfcheck.py`: **ALL PASS** — shipped default OFF, OFF==static exactly,
ON==clamp(k*rvol,static,ceil) across low/mid/high vol, fail-safe (rvol=0/<0/absent→static), monotone+bounded.

**Paper-trade gate (Taylor recommendation): ~2 weeks / ~10 paper sessions flag-ON in PAPER only** — SHORTER
than EXTREME's 4 weeks because this fires on **ordinary gap-ups** (not a rare tail), so dozens of cap-widening
events accrue per week. Validation target = wiring correctness on live quotes + fail-safe when rvol cache
absent + **zero NORMAL-path interference on non-gap days** + skeptic's rerun (REAL fill vs the `min(open,L)`
daily-proxy, esp. correlated broad gap-ups at target NAV).

**Paper-trade ACTIVATED** [2026-07-01, user-approved via Mike dispatch Taylor_20260701_105729]. Set
`chase_cap_vol_scale_enabled=True` in the `main` paper account `overrides` **only** (k=2.0, ceil=0.04 as
coded). Verified through the REAL `load_config()`/`load_accounts()` resolution: paper(main)=True,
**SpaceX/live=False, global DEFAULT=False**, other paper accounts (ab_cross/ab_dip)=False. Backup of the
accounts file: `secrets/trading_bot_accounts.json.bak.20260701`. **Executor-path stress harness
`mike/agents/Taylor/stress_vol_scale_chase_cap.py`: 15/15 PASS** — drives the genuine
`Executor._buy_chase_pct`/`_limit_price` via a recording FakeBroker + real `Quote` objects (not a re-impl):
(0) wiring proof, (1) WIDEN clamps to ceil / returns k*rvol in-band, (2) MONOTONE never below static,
(3) FAIL-SAFE rvol absent/0/<0→static, (4) paper limit sits at ref×(1+ceil)=20800 > static-cap 20300,
(5) **NEG CONTROL: live(SpaceX) effective cfg ignores rvol → static cap 20300** on the identical high-rvol
quote. No real `main`/`SpaceX` exec logs touched (throwaway plan label). **Start 2026-07-01, target end
~2026-07-14 (~10 paper sessions).** Conditions before any LIVE enable: (a) clean paper run — wiring
correct on live quotes + fail-safe when rvol cache absent, (b) zero NORMAL-path interference on non-gap
days, (c) skeptic rerun REAL fill vs `min(open,L)` proxy on correlated broad gap-ups at target NAV,
(d) explicit user sign-off. **Live stays DEFAULT-OFF.**

_(prior status line, now superseded by the activation above:)_ **Live stays DEFAULT-OFF; Taylor did NOT enable
anywhere.** Paper enable = set `chase_cap_vol_scale_enabled=True` in the `main` paper-account `overrides`
(same paper-only pattern as `gap_adaptive_enabled`/`extreme_regime_enabled`) — awaiting user/Mike OK.

---

## Wyckoff distribution/euphoria warning-layer — AUDIT (observe-only) — REFUTED, dashboard-only
**Job Taylor_20260701_171827 · 2026-07-02 · builder `wyckoff_warning_logger.py` · Huong-2 first step (observe-only).**
NOT wired anywhere (not live, not paper). Pure evidence build per the guardrail Taylor self-set: theory-anchored
thresholds, coarse grid, NO fit-to-history; stop at dashboard if the evidence bar fails.

**Two theory-grounded signals** (all inputs lagged 1 session — causal; universe<100 names → no-warn fail-safe),
backfilled 2014→2026-06 from the local BQ parquet cache (composition-robust ratios only):
- **A · breadth divergence** = VNINDEX within 5% of its 6M high WHILE breadth (% of `ticker_prune` > MA200)
  fell ≥ a_delta pp vs 3M ago (distribution near the high). Grid a_delta ∈ {8,10,12}pp.
- **B · effort-vs-result / volume** = B-dry (index +≥5–8% over 3M but market-wide median `Volume/Volume_1M` ≤1
  on the advance → no demand) OR B-climax (median `Volume/Volume_1M` ≥1.6–2.0 on a 10-session advance → blow-off).

**Ground truth** = DT5G onsets from `vnindex_5state_dt5g_live` 2014+: 15 de-risk onsets (enter BEAR/CRISIS from
≥NEUTRAL) + 2 EX-BULL peaks. (DT5G onset lags the actual VNINDEX price peak by a **median 34 sessions**.)

**Verdict: REFUTED — no predictive edge.** The naive hit-rate is high (ANY-signal 13/15) but is a pure
**duty-cycle artifact** — the combined signal is ON **36.5%** of all days, so over any 60-session pre-onset
window it almost always fires by chance. The decisive test is **base-rate lift** (fire-rate in the pre-event
window ÷ fire-rate in benign periods):

| signal | duty | lift vs DT5G onset | lift vs actual price-peak | leads price-peak | med actionable lead |
|---|---|---|---|---|---|
| A breadth-div | 10.9% | **0.15×** | **0.34×** | 5/15 | 10s |
| B volume | 28.6% | **0.74×** | **0.75×** | 13/15 | **1s** (coincident) |
| A∨B | 36.5% | **0.56×** | **0.62×** | 13/15 | **1s** (coincident) |

Every configuration in the whole grid has **lift < 1.0** — the signals fire *less* before tops than in benign
uptrends, and when they "hit" it is at median lead ~1 session (coincident, not leading). EX-BULL climax = 1/2
(n=2, no basis) and **zero fires** at the 2.0× threshold (fragile).
**Root cause:** near-high + breadth-strength + price-up-3M are conditions of *healthy benign uptrends*; by the
time a real top forms breadth has already broken and the index is off its high, so these "strength" preconditions
are actually rarer pre-top. Classic Wyckoff distribution needs price *structure* (trading ranges, up-thrusts,
springs), which breadth+volume aggregates alone do not expose.

**Decision (guardrail-compliant):** STOP at dashboard level. Do **NOT** wire into any gate — not DT5G, not live,
**not even paper**. No auto-trade proposal. Artifacts kept for the observe-only dashboard: `wyckoff_warning_logger.py`,
`data/wyckoff_warning_panel.csv` (daily series + signals), `data/wyckoff_warning_grid.csv` (full grid audit).
"Step 2" (any gating integration) is moot given the refute; would need user/Mike sign-off anyway and there is
no evidence to support it.

## Fixed-window fill-timing edge — go/no-go for LIVE (2026-07-02, Taylor)
**Q (user via Mike):** live SpaceX bot mua ngay 09:15 (vì `fill_timing_live_gate=True` → live bypass, mult=1.0); khung giờ BUY 10:45-11:15 / SELL 09:15-09:45 (`_fill_timing_mult`, executor.py:511) chỉ chạy ở paper. Khung giờ này có edge thật không → có nên tắt gate để bật cho live?
**Mechanism (đọc code):** KHÔNG phải hard-lock — là interval multiplier mềm. Trong cửa sổ mult=1.0 (retry bình thường), ngoài cửa sổ interval×4 (`fill_timing_outside_mult`) → lệnh CHỈ *tập trung* vào cửa sổ, vẫn khớp ngoài cửa sổ nếu treo lâu. Nên capture LIVE < edge backtest sạch. `gap_adaptive_enabled` (default OFF) là override riêng cho down-gap → buy-at-open.
**Prior work:** review 2026-06-30 (`execution_quality_review.py`) CHỈ check MECHANICS (adherence/reject/directional) — theo thiết kế của chính nó, edge 5-17bps KHÔNG đo được trong cửa sổ 2 ngày (noise/ngày 110-220bps >> edge). Edge validate qua NHIỀU TUẦN. Gap studies (dòng 637-664) đã confirm DIRECTION IS/OOS-stable trên daily proxy 408k rows + 16-name intraday.
**Evidence NÀY — `intraday_fill_timing.py` + IS/OOS split inline (16 tên true 1-min, 9670 ticker-days, 2023-09..2026-06), ref=prior-close:**
| edge (bps, +=window giúp) | FULL | IS <2025 | OOS ≥2025 |
|---|---|---|---|
| BUY: open→11:15 rẻ hơn | **+17.6 (t12.0)** | +17.6 (t9.3) | +17.7 (t8.0) |
| SELL: open giàu hơn ATC | +11.8 (t5.6) | +14.7 (t5.2) | +9.3 (t3.0) |
| SELL: open giàu hơn 11:15 | +17.6 (t12.0) | +17.6 (t9.3) | +17.7 (t8.0) |
vs day-VWAP: open +13.8bps (TRÊN trung bình ngày=xấu để mua), 11:15 −5.4bps (DƯỚI trung bình=tốt để mua). Per-name: **15/16 tên buy_edge dương** (chỉ NNC −49bps, tên mỏng). → khung giờ config **đúng hướng CẢ hai chiều, IS/OOS-stable, cross-section nhất quán.**
**CAVEAT (vì sao KHÔNG flip live ngay):** (1) đây là backtest SẠCH giả định giao dịch ĐÚNG giá 11:15/open; cơ chế live là cadence-mềm → capture thực chỉ 1 phần. (2) noise/trade >> edge; 11:15 chỉ là giá rẻ nhất 29% số ngày → edge là mean-tilt mỏng, không phải win/trade tin cậy. (3) 16 tên large/mid; edge scale-up trên tên nhỏ (gap study) NHƯNG capturability tên mỏng chưa test. (4) CHƯA có: NET-of-capturability trên paper fills thật + quant-skeptic verify + user sign-off. EV thô ≈ ~17bps/side × turnover ~ cùng cỡ TC drag 0.32%/yr — real nhưng KHÔNG needle-mover.
**VERDICT:** giả thuyết ĐÃ được xác nhận thực nghiệm (không phải lý thuyết suông) & IS/OOS-robust. NHƯNG **KHÔNG flip `fill_timing_live_gate` ngay** trên evidence sạch này. Paper ĐANG chạy khung giờ (đó là mục đích của live_gate) → đã là vehicle validate. **Path đúng (theo precedent vol-scale/extreme):** để paper tích ~3-4 tuần fills → chạy `execution_quality_review.py` xác nhận (a) mechanics sạch + (b) paper fills THỰC hiện thực ~17bps net capture/slippage → quant-skeptic verify NET-of-noise → user sign-off → khi đó mới flip live. Live-behavior change: KHÔNG tự bật.

## custom30V weekly/monthly 8L-rating OVERLAY (hybrid) — go/no-go (2026-07-02, Taylor)
**Q (user via Mike):** thay vì chỉ rebal quý, thêm overlay TUẦN: mỗi tuần nếu có tên 8L rating≤2 (golden/strong, AAA/AA/A) đang "nổi lên" mà chưa có trong custom30V → swap ra 1-2 tên yếu nhất (theo yieldcombo rank). Mục tiêu: refresh basket nhanh hơn quý. Có nên làm không?
**Method (`custom30v_hybrid.py`, auditable):** BASE = `custom_basket.build_pit(yieldcombo, q2m5, gate3, namecap0.10)` AUTHORITATIVE; overlay chạy trên grid tuần/tháng TRONG mỗi quý, reset về base pick mỗi q2m5 rebal. Candidate = liquid-pool tên rating_asof(gd)≤2, chưa trong basket, có yield score; OUT = ≤2 tên yieldcombo thấp nhất. Swap iff rating(cand) ≤ rating(weak) − NOTCH. Re-chain namecap **byte-faithful** (self-check max rel diff **8.88e-16** vs build_pit). TC swap thêm = 0.1%/side (sum|dw|≈2·nswap/30). Metric = BASKET INDEX (selector-isolated), walk-forward IS(2014-19)/OOS(2020+)/Full — đúng phương pháp `custom30v_select_audit.py`.
**Kết quả — MỌI variant THUA baseline (net-of-swap-TC, ΔCAGR):**
| variant | swaps | ΔFull | ΔOOS | ghi chú |
|---|---|---|---|---|
| baseline custom30V | 0 | — (29.96/OOS36.98) | — | mechanical quarterly only |
| H_wk_n1 (tuần, notch≥1) | 616 | **−3.61pp** | **−6.91pp** | aggressive nhất → tệ nhất |
| H_wk_n2 (tuần, notch≥2) | 117 | −0.39pp | −0.69pp | ít swap nhất → gần baseline |
| H_wk_n1_cheaper (+guard rẻ hơn) | 237 | −1.29pp | −0.89pp | guard cắt ½ damage |
| H_mo_n1 (tháng, notch≥1) | 278 | −1.19pp | −1.21pp | |
**Diễn giải (3 verdict):**
1. **Overlay LÀM XẤU ĐI, không bao giờ cải thiện CAGR** — mọi variant/window đều âm. Monotone: càng swap nhiều càng tệ (616 swaps → −3.61pp; 117 swaps → −0.39pp).
2. **Nguyên nhân = CÙNG cơ chế quality-tilt đã refute sáng nay (composite-as-selector), KHÔNG phải TC artifact.** Bằng chứng: gross vs net-TC chỉ chênh ~0.42pp (H_wk_n1 gross 26.77 vs net 26.35) → damage đến từ SELECTION change, không phải turnover cost. Swap ra tên yieldcombo-thấp (= tên sector-PE-thấp/deep-value = NGUỒN return của VN value) để lấy tên rating≤2 (quality-priced-in) = cắt đúng low-PE tilt. Xác nhận: "cheaper guard" (chỉ swap nếu cand cũng rẻ hơn) giảm damage −3.61→−1.29pp — vì ngừng bán tilt value đi; phần còn âm là whipsaw/redundant swap.
3. **Cadence: GIỮ QUÝ.** Tuần strictly tệ nhất; tháng tệ hơn quý. Lý do NGOÀI backtest: 8L rating chỉ đổi theo QUÝ (per-ticker 48 updates/12yr = 4/năm, staggered theo release date) → poll dưới-quý KHÔNG có thông tin fundamental mới để hành động, chỉ thêm whipsaw quanh các update lệch pha. Premise "refresh nhanh hơn" là ILLUSORY — không thể refresh nhanh hơn dữ liệu nền. Mechanical quarterly rebal đã bắt trọn rating migration ở đúng cadence mà data hỗ trợ.
**VERDICT: DO NOT WIRE.** custom30V giữ nguyên mechanical yieldcombo top-30 / cap0.10 / quarterly. Overlay là liều nhỏ của cùng thuốc quality-tilt đã fail full-dose. (H_wk_n1 có giảm MaxDD Full −39.2→−33.9 & Calmar Full 0.76→0.79 nhưng THUA OOS Calmar 0.94→0.90 + mất 3.6pp CAGR → không phải trade hấp dẫn; custom30V là return-sleeve, DT5G lo risk-gating.)

## NEUTRAL parking exposure 70% (engine) vs 94% (go-live) — 2026-07-03 (job Taylor_20260703_113818)
**Q:** SpaceX go-live sits ~94% invested in custom30V at NEUTRAL / 0 active BAL+LAG picks
("custom30V_parking_full_deploy", DollarBill hand-set). Engine rule ETF_PARK={3:0.7} parks 70% of
IDLE cash → with 0 deals, idle=100% → engine-approved target = 70% invested / 30% cash. 94 is ~24pp
above the tested level and was never backtested. Script: `neutral_exposure_70_vs_94.py`; audit CSV
`data/neutral_exposure_70_vs_94.csv`. Basket = custom30V (yieldcombo) PIT via `custom_basket.build_pit`
(gate_rating=3, namecap 0.10, q2m5); DT5G state `vnindex_5state_dt5g_live`; cash@0%.
- **A (NEUTRAL-day static hold, 70 vs 94):** Sharpe IDENTICAL (FULL 1.57/1.57, IS 1.45/1.45, OOS
  1.76/1.76); Calmar ~equal (1.50/1.53). annRet 22.25→29.88% (×1.34 = 0.94/0.70), MaxDD −14.9→−19.5%.
  → exposure scaling is Sharpe-NEUTRAL: 94 buys ZERO risk-adjusted edge, pure leverage-up.
- **B (fwd path from every NEUTRAL day):** basket drifts up in NEUTRAL (median 1Y +17.8% @70). 94 scales
  both: 1Y med ret +17.8→+24.1, withinDD −11.4→−15.1. Tail 6M/1Y 5th-pct withinDD −23/−24% @70 →
  −30/−31% @94 (bad-case crosses −30%).
- **C (reversal):** from a NEUTRAL day P(hit BEAR/CRISIS) = 12.3%/20s, 21.6%/40s, 31.1%/60s (NEUTRAL is
  a genuine transition state). Reversal-episode worst-DD: STATIC hold median −6.2→−8.3 (Δ−2.1pp),
  5th-pct −23.2→−30.1 (Δ−6.9pp). **DT5G-GATED (realistic — gate cuts parked sleeve on flip): worst-DD
  IDENTICAL 70/94** (median −5.5/−5.5, 5th-pct −14.0/−14.0) → reversal tail of 94 is neutralized IFF
  the gate manages the 94% (engine ETF pre-fill-sell does; a hand-parked position outside gate mgmt does not).
- **Verdict:** No data supports 94>70. Risk-adjusted-equivalent; 94 just runs the NEUTRAL sleeve ~34%
  hotter than the tested/approved V2.4 (whose DD −18.8% / bootstrap 5th-pct −28.6% anchor was built on the
  70%-of-idle rule). RECOMMEND TRIM SpaceX to engine 70% unless user deliberately mandates a hotter risk
  profile (a user decision, not DollarBill's to set). Self-check: annRet ratio 29.88/22.25=1.343=0.94/0.70 ✓.
  Caveat: NEUTRAL day-counts overlap-inflated (not iid); Sharpe-neutrality is a math identity so robust,
  reversal freqs directional. R&D only — no trade/plan change without user+quant-skeptic sign-off.

---
## NEUTRAL exposure sweep + V2.5-stack question (Taylor 2026-07-03, job Taylor_20260703_120555)
Follow-up to the CONFIRMED "70 vs 94" finding. Method: static hold on NEUTRAL days, custom30V
yieldcombo PIT basket (gate3/namecap/q2m5), DT5G state, cash@0%, port=e·rb. Script
`neutral_exposure_sweep.py` → `data/neutral_exposure_sweep.csv`.

**CÂU A — 94% is NOT a special ceiling; the whole 70→100% band is Sharpe-neutral, no inflection.**
| exp | FULL annRet | Sharpe | MaxDD | Calmar | fwd-6M 5th-pct DD |
|---|---|---|---|---|---|
| 70% | 22.25 | 1.57 | −14.85 | 1.498 | −23.27 |
| 80% | 25.43 | 1.57 | −16.83 | 1.511 | −26.21 |
| 85% | 27.02 | 1.57 | −17.81 | 1.517 | −27.64 |
| 90% | 28.61 | 1.57 | −18.78 | 1.524 | −29.05 |
| 94% | 29.88 | 1.57 | −19.55 | 1.529 | −30.16 |
| 100% | 31.79 | 1.57 | −20.69 | 1.536 | −31.80 |
- **Sharpe EXACTLY invariant** 70→100 (FULL 1.57 / IS 1.45 / OOS 1.76 flat) — math confirmed (e cancels).
- **annRet exactly LINEAR** (22.25×e/0.70 reproduces every cell).
- **MaxDD SUB-linear**: DD/exp ratio shrinks monotonically −21.22→−20.69 (FULL) → DD grows *slower*
  than exposure. **No steepening, no knee anywhere.** ΔMaxDD/+step is flat-to-declining (~−1pp/+5pp);
  5th-pct fwd-DD tail smooth & monotone, no discontinuity at 94.
- **Calmar RISES** with exposure (1.498→1.536 FULL; same IS/OOS) — return linear, DD sub-linear → more
  exposure = mildly BETTER Calmar. On risk-adjusted metrics 100% ≥ 94% ≥ 70%; they are equivalent.
- **VERDICT: 94% is an arbitrary point** (DollarBill go-live full-deploy), NOT a risk-optimized ceiling.
  The 70↔94 choice is a pure raw-DD-tolerance decision with ZERO risk-adjusted edge either way —
  consistent with the prior "94 buys zero risk-adj edge → trim to engine 70" finding.

**CÂU B — 94%-NEUTRAL and V2.5 MGE=1.5 are DISJOINT regimes; they do NOT stack to 141% gross.**
- Code proof: `simulate_holistic_nav.py:314` "ETF parking never uses margin"; `:1148-1149`
  `_mg_ok = margin_tiers is None OR play_type in margin_tiers`; `pt_v23_audit_2014.py:1591`
  `margin_tiers={CAPIT plays}` under MGE_CAPIT_ONLY=1 (default). S2 lever (`etf_lever_by_date`) fires
  ONLY on `_lever_dates`, appended ONLY when `_capit_fired` (`pt_v23:1430-31`) = capitulation, which
  fires ONLY in CRISIS/BEAR washout. At NEUTRAL no CAPIT → no lever date → parking gross ≤1.0.
  **94%×1.5=141% is UNREACHABLE** (the parking sleeve is leverage-free by construction). Account cap
  `max_gross_exposure_pct=1.5` (trading_rules) is a Mafee CEILING, not a target.
- **Two MGE=1.5 variants clarified:**
  - *REJECTED (registry 2026-06-23, line 212-214):* MGE=1.5 GENERAL (MGE_CAPIT_ONLY=0, margin_tiers=None)
    → levers WHOLE book always → dove −57.3B into COVID −34% crash → **MaxDD −32.5%, Calmar 0.97**, fragile. LOẠI.
  - *V2.5 "R&D-complete" (trading_rules v1.9 / S2 lever-park):* MGE=1.5 + MGE_CAPIT_ONLY=1 +
    RECOVERY_LEVER_PARK=1, gated A∧C-confirm + pb_z≤−0.5 + PE_pctile5y≤0.20 → leverage lands ONLY at
    confirmed deep bottoms AFTER the drawdown → **MaxDD −20.1%, Calmar 1.49, +1.00pp vs LF @borrow 12.5%.**
  - Same number, OPPOSITE risk — the difference is WHERE the lever lands. A∧C entry gate = primary
    protection (bypass it → MaxDD −30.7%, reverts toward the rejected profile, registry line 401).
- **Total-risk answer:** raising NEUTRAL base to 94 (vs 70) and enabling V2.5 are additive across the
  CYCLE but NEVER simultaneous in gross (NEUTRAL-park vs CRISIS/BEAR-washout-lever are time-disjoint).
  Portfolio MaxDD ≈ max(NEUTRAL-regime DD ~−19.5%, washout-lever DD ~−20%) ≈ −20%, NOT a stacked −30%+.

## 🟢 NEUTRAL-park 70 vs 94 vs 100 — FULL 2-book NAV compounding (Taylor 2026-07-03, job _130720, threads=1, self-check 0 VND ×3)
**Real full-system NAV** (V2.3A: BAL momentum + LAG PEAD + CAPIT sleeve + custom30V parking, 2014-01-02→2026-06-19,
@50B, DT5G state, contemporaneous batch — REPLACES the 2 detached numbers 22.25/29.88/31.79 of earlier findings).
Config: `BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=<X> AUDIT_END=2026-06-19 $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge`. IS/OOS sliced from combined_nav DAILY (FULL reproduces script print exactly).

| PARK | FULL CAGR | Sharpe | MaxDD | Calmar | IS CAGR/Sh/Cal | OOS CAGR/Sh/Cal |
|---|---|---|---|---|---|---|
| 0.70 | 26.83% | 1.78 | −16.5% | 1.63 | 25.21/1.71/1.58 | 28.32/1.83/1.72 |
| 0.94 | 28.01% | 1.66 | −18.8% | 1.49 | 26.64/1.56/1.48 | 29.28/1.75/1.56 |
| 1.00 | 29.30% | 1.65 | −19.3% | 1.52 | 26.74/1.49/1.52 | 31.71/1.79/1.65 |

- **Raw CAGR rises monotone** with parking (+1.2pp/step) BUT **Sharpe falls monotone (1.78→1.66→1.65), MaxDD worsens monotone (−16.5→−18.8→−19.3), Calmar drops (1.63→1.49→1.52).** Pattern holds in BOTH IS and OOS halves — not an artifact.
- **70% DOMINATES on every risk-adjusted metric** (best Sharpe+Calmar, shallowest DD) in all 3 windows; 94/100 win only on raw CAGR.
- **Refines the 12:11 static-hold sweep**: that isolated-sleeve sweep showed Sharpe≈invariant/Calmar rising, but in the REAL integrated 2-book compounding the extra NEUTRAL parking beta is CORRELATED with book drawdowns → adds return but MORE-than-proportional risk → 94/100 are risk-adjusted **WORSE**, not neutral. STRENGTHENS the prior quant-skeptic-CONFIRMED "trim 94→70": the +1.2pp raw give-up from 94→70 buys +0.12 Sharpe / +0.14 Calmar / +2.3pp shallower DD. **70 = risk-adjusted-optimal parking; production default 3:0.7 is correct.**
- Drift note: 0.7 here=26.83 vs pin 28.05/28.26 (−1.2..1.4pp) = normal as-of data-drift (registry line 145); used contemporaneous pair per methodology. AUDIT_END=2026-06-19, threads=1, self-check 0 VND all 3 runs.

## 🟢 SINGLE-BOOK custom30V vs FULL 2-book V2.4 — which mechanism made 26.83/28.01/29.30? (Taylor 2026-07-03, job _153738)
**Question (user):** the 26.83/28.01/29.30% table — is that custom30V-as-a-single-book (the thing Taylor once refused), or the full 2-book engine? And what is the HONEST number for SpaceX's current state (running like single-book custom30V)?

**Mechanism that made 26.83/28.01/29.30 = FULL 2-BOOK, not single-book.**
- Cmd: `BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=<0.7|0.94|1.0> AUDIT_END=2026-06-19 $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge` (registry table L1264-1275).
- `pt_v23_audit_2014.py` = V2.3A 2-book NAV: **Book BAL 25B (momentum SIGNAL_V11) + Book LAG 25B (PEAD/earnings-drift), BOTH always-on 2014→2026**, active picks most days. custom30V only PARKS idle cash when a book has no deal. `PARK_STATES=3:X` sets the parking % of the IDLE pool in NEUTRAL — it does NOT change the whole NAV. TC=0.1%/side (production audit engine).

**Single-book custom30V (the mechanism Taylor refused) = `custom30v_singlebook_faithful.py`.** WHOLE NAV = custom30V, NO BAL/LAG. DT5G exposure ladder `W_STATE={1:0,2:0.2,3:0.7,4:1.0,5:1.3}`. Costs: TC=0.3% (slippage-incl), borrow 10%/yr on EXBULL leverage, quarterly rebal TC. **RAN 2026-07-03 (contemporaneous, BQ live-fallback, self-consistent w build_pit):**

| Book | Cost | FULL CAGR/Sh/DD/Cal | IS 2014-19 | OOS 2020+ |
|---|---|---|---|---|
| **Single-book custom30V (yieldcombo)** | TC0.3%+borrow | **22.65 / 1.33 / −22.7 / 1.00** | 16.98 / 1.16 / −22.7 | 28.15 / 1.47 / −19.9 |
| Single-book v3comp (full 8L value) | TC0.3%+borrow | 28.37 / 1.63 / −19.6 / 1.44 | 22.83 / 1.56 / −15.0 | 33.74 / 1.71 / −19.6 |
| **FULL 2-book, PARK 0.70** | TC0.1% | **26.83 / 1.78 / −16.5 / 1.63** | 25.21/1.71/1.58 | 28.32/1.83/1.72 |
| FULL 2-book, PARK 0.94 | TC0.1% | 28.01 / 1.66 / −18.8 / 1.49 | 26.64/1.56/1.48 | 29.28/1.75/1.56 |

- **The 26.83 (2-book) beats 22.65 (single-book) by ~4pp CAGR AND is far better risk-adj (Sharpe 1.78 vs 1.33, DD −16.5 vs −22.7).** Two drivers: (a) BAL momentum + LAG PEAD active alpha books (~2-3pp); (b) higher avg exposure (2-book runs 90-100% invested vs single-book NEUTRAL-ladder 70%) + cheaper TC convention (0.1 vs 0.3, ~0.5-1pp). On like-for-like TC0.1%, single-book custom30V ≈ 24-25% FULL.
- **Why single-book was refused before (confirmed):** yieldcombo single-book is a real strategy but strictly DOMINATED by the 2-book (worse CAGR + worse Sharpe + deeper DD), and even single-book v3comp beats yieldcombo — custom30V's value is as the PARKING sleeve inside the 2-book, not standalone. Same family verdict as all 9 sector-compounder sweeps ("real signal, NOT a standalone book").

**HONEST number for SpaceX RIGHT NOW (0 active BAL/LAG, all 23 = custom30V parking, ~94% invested @NEUTRAL):**
- SpaceX is currently running as **single-book custom30V**, NOT the 2-book. So the honest reference is the single-book row, NOT 26.83/28.01/29.30 (those credit BAL+LAG alpha SpaceX isn't harvesting).
- At the 70% NEUTRAL ladder: **~22.6% CAGR / Sh 1.33 / DD −22.7%.** SpaceX runs NEUTRAL at ~94% (not 70%), which adds ~+1-2pp raw CAGR but worsens risk-adj (from the 70→94 sweep: more parking beta correlated w drawdowns). Net honest estimate for current composition: **CAGR ≈ 23-25%, Sharpe ≈ 1.25-1.35, MaxDD ≈ −23 to −25%.**
- **Gap vs the table: the 26.83-29.30% headline OVER-states SpaceX's current expectation by ~3-5pp CAGR, ~0.4-0.5 Sharpe, ~6-8pp shallower DD** — the missing piece is the BAL momentum + LAG PEAD books actually holding active picks. Restore the 2-book (rotate parking→active on signal) to reach the table; stay all-parking and expect the single-book profile.
- Caveat: single-book_faithful is a selector-isolated sim (NAV from build_pit level ×DT5G ladder ×costs), self-consistent w build_pit (delta-tilt recon 3.3e-16), NOT a full 2-book cash-flow NAV; TC0.3% vs the 2-book table's 0.1% — direction robust, exact pp not identical cost basis.

---

## 2026-07-04 — 8L value-axis vs 15-sector framework: EV/EBITDA gap for D&A-heavy names (job Taylor_20260704_072114)

**Question (Mike):** what do 8L golden/strong scoring and the 15-sector-screen framework share in
scoring/gating, and could the shared (or differing) part improve 8L DIAGNOSTIC quality? Research-only,
no production wiring; custom30V/BAL/LAG untouched.

**Premise correction (important):** Mike's summary said "8L uses ONE valuation metric for all sectors
(0.35·pb_z + 0.65·sector-neutral 1/PE)". That is the **v2** docstring. The LIVE default is **VALUE_VERSION=v3**,
which is ALREADY sector-differentiated: route-specific weights `COMPOUNDER(ey.45/cfy.30/ps.25)`,
`CYCLICAL(ey.40/cfy.60)`, `RETAIL(ey.35/cfy.20/ps.45)`, financials/RE/POWER keep v2; AND value ranks are
**sector-neutral** (rank within route — code literally: "sector-neutral is the correct SCREENER design").
So 8L and the framework already CONVERGE: quality floor ROE_Min3Y≥0, CF_OA_3Y>0 confirm, cheap-vs-own-history
(pb_z / golden-cell), route-specific leverage gates (rate_bank/securities/cyclical), retail=PS, cyclical=CF,
banks/RE=PB. The framework's Section-3 lookup ≈ 8L v3 route weights on 5 of 6 rows.

**The ONE genuine gap: EV/EBITDA.** The framework makes EV/EBITDA the PRIMARY lens for all capex/D&A-heavy
concession/infra (ports, telecom/towers, airport, cement, mature utilities, gas). 8L uses NO EV/EBITDA lens
anywhere (only 1/PE, 1/PCF, 1/PS, pb_z). For D&A-heavy names 1/PE is structurally distorted by heavy D&A.

**IC test — D&A-heavy universe** (ICB {2353 cement, 2357 infra-constr, 2771 logistics, 2773 marine-oil,
2777 ports/shipping, 5751 cargo-term, 6535 telecom, 7535 utilities, 7573 gas}; ticker_prune monthly panel,
month-end, 2014-01→2026-03, 8632 rows / 138 tickers / 147 months; forward = profit_3M T+60; monthly rank-IC):

| Lens | IC FULL | IC IS 2014-19 | IC OOS 2020+ |
|---|---|---|---|
| 1/PE (8L lens) | +0.0733 (t5.1) | +0.0247 (t1.3) | +0.1199 (t6.1) |
| **1/EVEB (framework)** | **+0.0834 (t5.9)** | **+0.0400 (t2.1)** | **+0.1250 (t6.5)** |
| pb_z (neg=cheap) | −0.0229 (t−1.4) | +0.0316 | **−0.0753 (t−3.9)** |
| 1/PCF alone (8L already has) | +0.0254 (t1.8) | — | +0.0707 (t3.7) |
| blend PE+PCF (≈8L) | +0.0734 | — | +0.1236 |
| **blend PE+PCF+EVEB** | **+0.0819** | — | **+0.1308** |

**Findings:**
1. **1/EVEB beats 1/PE** for D&A-heavy names in every window (+0.010 IC full, +0.015 IS, +0.005 OOS); both survive OOS.
2. **EVEB is ADDITIVE, not redundant** with 8L's existing lenses: EVEB~PCF rank-corr only 0.37, EVEB~PE 0.60;
   adding EVEB to the PE+PCF blend lifts IC +0.0085 full / +0.0072 OOS. 8L's own 1/PCF is weak here (+0.025 full)
   so it does NOT already capture the D&A add-back. EVEB coverage 1.00 vs PCF 0.78.
3. **pb_z is NEGATIVE-IC** in this universe (−0.075 OOS) — the framework's warning ("generic P/B fails for
   D&A-heavy") is confirmed by data. The **POWER route is the worst-matched**: all 24 rating≤2 utilities are
   scored on **v2 = 0.35·pb_z + 0.65·1/PE**, and their pb_z is systematically negative (mean −0.77, median −0.91),
   so the pb_z term is actively rewarding names on an anti-predictive signal.

**Overlap:** 66/174 golden+strong (rating≤2) names sit in D&A-heavy ICB (38%): COMPOUNDER 42 (on v3, ey-led —
partly protected) + POWER 24 (on v2, pb_z-heavy — the priority fix).

**Verdict (DIAGNOSTIC quality only, NOT a trading wire):** sector-ising the value axis with an EV/EBITDA lens
DOES improve 8L's golden-tier ranking IC for the 38% of names in D&A-heavy sectors — modest (+~0.01 IC) but
consistent and OOS-robust. Recommended scope if pursued: add ONE `D&A_HEAVY` val_route (EVEB co-primary with
1/PE, coverage-aware route-neutral pct; DROP the pb_z linear term, keep golden-cell flag only) — the POWER
route's pb_z-heavy v2 is the single highest-value fix. **Overfit risk LOW** (one economically-motivated lens,
OOS-validated, not a fitted param) PROVIDED we add exactly one D&A sub-route and do NOT proliferate 15
sector branches. Effort moderate; benefit = better BUY-NOW/dashboard ranking of 66 names + removes a
misleading pb_z reward on utilities. Behind VALUE_VERSION flag, paper-diff before default; custom30V/BAL/LAG
untouched. **Not wired — awaiting user go/no-go on diagnostic-only change.**

### 2026-07-04 · D&A_HEAVY route classification — which names/routes actually qualify (job Taylor_20260704_100727)
**Scope:** pre-implementation verification (NO code change) — before wiring a `D&A_HEAVY` val_route into
`rating_8l.py`, empirically confirm WHICH names are D&A-heavy so asset-light tech/retail aren't swept in and
capex-heavy names aren't missed. Liquid universe (Trading_Value_1M_P50 ≥ 2bn), n=174.

**D&A proxy (validated):** no direct D&A field in BQ. `EBITDA_P0` is a **TTM** figure (verified: EBITDA_P0/Rev
≈ 4–5× the single-Q EBIT margin for every clean name), so the correct margin proxy is
`DA_margin = EBITDA_P0/Revenue_TTM − EBITM_P0` (Rev_TTM = Rev_P0..P3). Sanity-ordered correctly: ports VSC 11.3%,
GMD 7.3%, power POW 8.1%, cement HT1 6.5%, telecom FOX 6.6%, steel HPG 5.3% high; retail MWG 1.0%, bank ACB 0% low.
- **DA/Revenue = STABLE structural signal** (denominator can't collapse) → use for CLASSIFICATION.
- DA/EBITDA = distortion magnitude but **NOISY** in thin-margin/trough quarters (CTF 638%, VEA 156%, steel-trough
  SMC 94%) → confirmatory only, reject when EBITDA-margin < 5%.
- Percentiles (clean): DA/Rev p50 2.4% / p75 5.3% / p90 10.6%; DA/EBITDA p50 21% / p75 33%.

**Threshold: DA/Revenue ≥ 5% (≈p73), NAME-LEVEL not ICB-sector.** ICB is too coarse — mixed sectors split:
Construction (ICB2357) holds BOT-toll operators CII 28%/HHV 11.5%/CTI 10.3% (HEAVY) next to pure contractors
CTD/HBC/FCN/CTR (<3%, LIGHT); OilGas-services holds PVD 7.2% (rigs, heavy) at sector-median 2.3%. A name-level
threshold separates them; an ICB route would misclassify both ways.

**Q2 false-positive / false-negative check:**
- **NO asset-light false positives** at DA/Rev≥5%: tech FPT 4.0%/CMG 4.4%/ELC 1.1%, retail MWG 1.0%/PNJ 0.1%/
  FRT/DGW, beverage SAB 2.4%/MCH 2.0% all correctly EXCLUDED.
- **"gas" is a FALSE candidate** (dispatch premise): OilGas-distribution GAS 1.8% / PLX / BSR 1.4% are LIGHT —
  gas distribution is asset-light trading in the P&L, NOT pipeline-heavy. Do NOT put gas in D&A_HEAVY.
- **False negatives avoided only by name-level:** naive ICB routing would MISS CII/HHV/CTI (heavy infra inside a
  light construction sector) and PVD (heavy inside light oil-services).
- **EXCLUDE REALESTATE from D&A_HEAVY:** the proxy is CONTAMINATED there (lumpy project-revenue recognition +
  financial income inflate "EBITDA" — SZC/NVL/VIC/CEO show high DA/Rev artifactually; VIC EBITDA-margin only 11.8%
  yet DA/EBITDA 78% = noise). RE earnings distortion is revenue-TIMING, not depreciation; RE already has its own
  value-dead lens. (5 names auto-dropped by EBITDA-margin>80% financial-income filter; RE kept but flagged.)

**D&A_HEAVY member list (DA/Rev≥5%, operating routes, EBITDA-margin 5–80%):**
- **Prime gap = capital-heavy names now inside COMPOUNDER on PE/PB-led v3** (the fix target):
  Ports: ACV, GMD, HAH, PHP, VSC · Marine/tankers: PVT, PVP, VOS · Toll/infra: CII, HHV, CTI, PC1 ·
  Telecom: FOX, VGI · Oil-drilling: PVD · Utilities/water: BWE, REE · Ind-materials: VGC, CRC · Mining: KSV, MSR ·
  Hotels: VPL · Agri(bio-assets): HAG · Plastics: AAA · Holding: GEX. (borderline/noise, exclude: YEG thin-EBITDA.)
- **POWER route (keep as own route, already uniformly heavy — highest-value pb_z fix):** GEG 30%, POW 8.1%, QTP 5.0%, NT2.
- **CYCLICAL (already cfy/1-PCF-led, cashflow-aware — EV/EBITDA adds least):** rubber DPR/GVR/PHR (plantations,
  heavy), HPG 5.3%. Lower priority.

**Recommendation:** classify D&A_HEAVY by **name-level DA/Revenue ≥ 5% (TTM-smoothed, ideally 4Q-avg EBITM to
de-noise), applied to OPERATING routes (COMPOUNDER + POWER), NOT by ICB-sector name, NOT to REALESTATE.** This
answers the pre-impl question: the route-name intuition ("port/telecom/cement/utilities/gas") is ~70% right but
gas is wrong, cement/construction need name-curation, and RE must be excluded. Still DIAGNOSTIC — not wired.

---

## 2026-07-04 — D&A_HEAVY route WIRED into rating_8l.py (VALUE_VERSION=v3_da, opt-in) — job Taylor_20260704_102937
**User-approved implementation** of the verify job above (Taylor_20260704_100727). Adds an EVEB (EV/EBITDA,
pre-D&A) co-primary VALUE lens for capital/D&A-heavy names, behind a new opt-in flag. **VALUE-AXIS only — the 8L
quality rating (1-5) is UNCHANGED, and nothing downstream (custom30V/BAL/LAG or any trading selector) reads it.**

**What changed (rating_8l.py):**
- `DA_HEAVY_SET` — NAME-LEVEL whitelist (23 names: ports/tankers/BOT-toll/telecom/PVD/BWE/REE/VGC/KSV/MSR/VPL/HAG/AAA),
  NOT ICB-based. `t.EVEB` added to MAIN_SQL; `eveb_yield = 1/EVEB` lens + `eveb_pct` route-neutral percentile.
- New val_route **D&A_HEAVY** (weights ey .35 / cfy .30 / ps .00 / **eveb .35** — EVEB co-primary WITH 1/PE).
  **POWER** moved onto the composite with the SAME weights (drops its v2 pb_z-linear term — pb_z has negative
  value-IC for these capital-heavy names, per the verify job). pb_z retained ONLY as golden-cell flag (kept).
- Gated by `VALUE_VERSION`: default **"v3" is byte-identical** (eveb weight 0 on base routes; D&A_HEAVY/POWER
  keep their prior treatment). **"v3_da"** activates the new route/lens. Not promoted — opt-in until user approves.

**Self-check / paper-diff (v3 default vs v3_da, live snapshot 108 investable names, rating≤3 & liq≥3bn):**
- Quality **rating (1-5): 0 changes** — value axis fully decoupled from quality. ✓
- **value_score changed on exactly 19 names, ALL in-scope**: 15 D&A_HEAVY present in screener (ACV/CTI/FOX/GMD/HAH/
  HHV/MSR/PHP/PVP/PVT/REE/VGC/VGI/VPL/VSC) + 4 POWER (GEG/NT2/POW/TTA). Zero real value_score change on any
  base-route name (COMPOUNDER/CYCLICAL/RETAIL/financials/RE). ✓ (8 DA names — AAA/BWE/CII/HAG/KSV/PC1/PVD/VOS —
  are rating>3 or illiquid, correctly absent from the investable screener.)
- **Zone changes: 3 total.** 1 in-scope (PHP WATCH-RICH→ACCUMULATE, EVEB lifts a cheap port). 2 out-of-scope
  ripple (MSB, VEA) — value_score IDENTICAL, only their global value_pct percentile shifted a hair at a band
  edge because ~19 scores re-ranked (inherent to percentile-band zoning, not a value change). No wild reshuffle.
- Directionally sane: cheap-on-EVEB names lifted (HAH 0.80→0.92 EVEB4.3, PVP 0.92→0.98 EVEB3.3, VGC 0.66→0.80
  EVEB6.7, ACV 0.46→0.59); NT2 1.00→0.91 (mild, still BUY-NOW). Modest re-rankings, nothing inverted.
- Live CSVs restored to default v3 after the diff run (verified live screener == v3). **No production NAV impact.**
Run to reproduce: `VALUE_VERSION=v3_da python3 rating_8l.py` (default `python3 rating_8l.py` = unchanged v3).

---

## 2026-07-04 — VALUE_VERSION=v3_da PROMOTED to DEFAULT in rating_8l.py — job Taylor_20260704_111020
**User-approved promotion** of the opt-in v3_da variant wired above (job Taylor_20260704_102937) to the default.
The D&A_HEAVY + POWER EVEB co-primary value route is now the standing behavior of `rating_8l.py`.

**Code change (rating_8l.py, 1 line + docstring):**
- `VALUE_VERSION = os.environ.get("VALUE_VERSION", "v3_da")` — default flipped `"v3"` → `"v3_da"`.
- **Old "v3" retained for rollback**: `VALUE_VERSION=v3 python3 rating_8l.py` reproduces the pre-promotion
  output byte-identically (verified below).
- Docstring updated at the VALUE_VERSION gate: records v3_da as default-from-2026-07-04, the rationale
  (EVEB co-primary for D&A-heavy/POWER, pb_z-linear dropped there — verify jobs Taylor_20260704_072114 golden-
  tier IC +0.01 OOS-robust / pb_z NEGATIVE-IC there; membership NAME-LEVEL DA/Rev≥5% job Taylor_20260704_100727),
  and the rollback env var. **This is a DIAGNOSTIC / value-axis change ONLY — no NAV impact.**

**Promotion self-check (fresh live snapshot, 108 investable names, rating≤3 & liq≥3bn):**
- (a) 8L quality **rating (1-5): 0/108 differ** between v3 and v3_da — value axis fully decoupled from quality. ✓
- (b) **Exactly 19 in-scope names re-weighted** on value_score: 15 D&A_HEAVY (ACV/CTI/FOX/GMD/HAH/HHV/MSR/PHP/PVP/
  PVT/REE/VGC/VGI/VPL/VSC) + 4 POWER (GEG/NT2/POW/TTA). Zero real value_score change on any base route. ✓
- (c) **Zero NAV impact**: every production selector (custom30/custom30V/BAL/LAG) reads `gate_rating<=3` off BQ
  `tav2_bq.fa_ratings_8l.rating` — NOT value_score/zone. Rating is byte-identical → NAV path provably untouched.
  value_score/zone are consumed only by research/backtest/reporting scripts (zone_backtest, composite_selector_
  backtest, value_zone_robust, bot_8l_commands telegram display, screener_paper_diff). ✓
- Zone migrations: 3 total = 1 in-scope (PHP WATCH-RICH→ACCUMULATE) + 2 knock-on percentile-rank shifts (MSB, VEA)
  whose OWN value_score is unchanged (band-edge re-rank artifact of percentile zoning; display-only, no NAV path
  reads zone). BUY-NOW count 46→45.
**Verification runs**: default (no env)==explicit v3_da IDENTICAL ✓; rollback VALUE_VERSION=v3==original v3
IDENTICAL ✓; live screener CSV restored to the new default (v3_da) after the diff runs.
Run to reproduce: `python3 rating_8l.py` (=v3_da now); rollback `VALUE_VERSION=v3 python3 rating_8l.py`.

---

## DSR / PBO Robustness Annex (2026-07)
> Job `Taylor_20260705_075644` (dispatch Mike, R&D Q3). **Meta-analysis, ZERO production risk:**
> reads only frozen daily-NAV CSVs already pinned above; runs no backtest, touches no live path.
> Reproduce: `python3 dsr_pbo_annex.py` (deterministic, fixed seeds). Method refs: Bailey & López de
> Prado 2014 (Deflated Sharpe); Bailey-Borwein-LdP-Zhu 2017 (CSCV/PBO); Politis-Romano 1994 (stationary
> bootstrap); Harvey-Liu-Zhu 2016 (multiple-testing haircut framing).

**Purpose:** quantify how much of V2.4's headline edge could be a multiple-testing artifact — the risk
that selecting the "best" config out of a large search inflates its apparent Sharpe.

### 1. Trial count N (auditable)
The V2.3A/V2.4 search left a countable artifact trail (each backtest writes a daily-NAV CSV):
- **176** total `data/v23_golive_audit_*.csv` artifacts on disk.
- **104** distinct config *stems* after collapsing NAV-level (`_navXXB`) and period (`_from20XX`) re-cuts.
- **71** survive as full-history (≥2500 daily obs) @50B daily-NAV series → the empirical DSR/PBO trial set.
- Plus the predecessor lineage that fed V2.3A (not double-counted above): `qt_v*` 19, `pt_v4*` 14,
  `v11_nav*` 10, `dt4g/dt5g_nav*` 12 — the search that produced the engine + regime gate.
- Registry-documented **rejected** variants (BỊ LOẠI / REFUTED / walk-forward-bác): ≥17 named families
  (custom30V permanent-exclude, LAG SUE-tilt, hold-neutral exit, stability floor, liq-tilt, pbcombo
  dual-vehicle, gq_score gate, composite-v3-as-selector, …).
- **Working N for DSR: tested at N=71 (empirical), 120, 200** to bracket the true search size. The DSR
  verdict is **invariant** across this whole range (see §2) — so the (unavoidable) uncertainty in the
  exact trial count does **not** change the conclusion.

### 2. Deflated Sharpe Ratio — R3 (LIVE deploy config)
Source: pinned R3 CSV `..._etfliqcustompitg_wtnamecap.csv`, T=3106 daily obs (12.3y), combined BAL+LAG NAV.
- Independent recompute of daily returns: **per-day Sharpe 0.1074 → annualized ≈ 1.70 (log) / 1.78 (arith)**.
  (Registry pins **1.87** from the engine's own calc; the ~0.1–0.17 gap is a return-convention/day-count
  difference, not a data issue. DSR below uses the **conservative** recompute 0.1074 — biases against us.)
- Higher moments (drive the DSR denominator): **skew γ3 = −0.119, kurtosis γ4 = 9.47 (excess 6.47)** —
  fat-tailed, as expected for an equity book; the DSR haircut explicitly penalizes this.
- Trial Sharpe dispersion across the 71 configs: mean ann-SR 1.69, sd ann-SR **0.144**, Var(per-day SR)=8.22e-5.
- **Expected-max Sharpe under the null (SR0, zero-skill benchmark):** ann **0.35** (N=71) → **0.40** (N=200).
- **DSR = P(true SR > SR0):**

  | trials N | SR0 (ann) | DSR |
  |---|---|---|
  | 71 (empirical) | 0.35 | **1.0000** |
  | 120 | 0.37 | **1.0000** |
  | 200 (conservative) | 0.40 | **1.0000** |

  **Verdict: DSR ≈ 1.0000 → NOT a RED FLAG (DSR≥0).** Observed Sharpe (~1.70 ann, 0.107/day) sits ~4.5σ
  above the multiple-testing-adjusted null even at N=200 and after the fat-tail haircut. The edge is not
  explained by trial selection. (Mechanically: the 12.3-year sample T=3106 dominates — a real, persistent
  Sharpe this far above SR0 survives deflation easily.)

### 3. CSCV / PBO (combinatorially-symmetric cross-validation)
Genuine daily-return matrix (not the thin per-year proxy): 3100 aligned daily obs × **71 configs**, split
into S=16 contiguous blocks → C(16,8)=**12,870** in-sample/out-of-sample partitions. Metric = per-obs Sharpe.
- **PBO = 0.198** — in ~20% of splits the IS-best config lands below the OOS median.
- logit λ: median +1.34, mean +1.05, P(λ<0)=0.198.
- **Interpretation:** PBO ≈ 0.20 < 0.5 ⇒ the config *family* is **not** predominantly overfit; the IS-best
  config stays above-median OOS 80% of the time. The residual 20% is honest: picking the single best
  parking/recovery/MGE variant on IS carries a real ~1-in-5 chance of not being best OOS — which is exactly
  why the LIVE choice (R3) was made on **robustness (Sharpe + walk-forward IS/OOS both positive), not
  IS-best CAGR**, and why the bull-park/recovery levers were kept opt-in, not defaulted. PBO 0.20 is a
  moderate, acceptable overfit-risk for a search of this size; it is a caution on *variant-chasing*, not on
  the core edge (which §2 clears).

### 4. Stationary bootstrap (Politis-Romano) vs circular block (L=21)
Cross-check the pinned 5th-pct anchor (CAGR 18.6% / DD −28.6%) against bootstrap-method choice. Both B=4000,
seed=12345, on R3 daily returns:

| method | CAGR 5th | CAGR med | MaxDD 5th | MaxDD med | P(DD<−30%) |
|---|---|---|---|---|---|
| circular block L=21 (`bootstrap_nav.py`) | 17.9% | 27.1% | −29.5% | −19.8% | 4.2% |
| stationary (PR, mean L=21) | 18.0% | 27.1% | −28.4% | −19.4% | 3.6% |

**Verdict: conclusion UNCHANGED.** The two methods agree to within ~0.1pp on 5th-pct CAGR and ~1pp on
5th-pct DD. The registry anchor (**5th-pct CAGR ~18%, DD ~−29%**) is robust to the block-scheme choice —
random block length (PR) does not soften the tail. (Same honest limit as `bootstrap_nav.py`: sampling
uncertainty only; excludes regime-change / structural breaks → true uncertainty is wider.)

### 5. Proposed standard for future wires (recommendation, not yet policy)
1. **Every production wire declares its trial count N** (how many configs were compared to reach it) and its
   **DSR** on the deploy config's daily NAV. **DSR < 0.95 → RED FLAG**, do not wire without explicit sign-off.
   (This complements — does not replace — the existing quant-skeptic + walk-forward IS/OOS gates.)
2. **Report PBO** when a wire is *selected out of a family* of ≥~8 variants (parking/lever/basket sweeps).
   PBO ≥ 0.5 = the selection is likely overfit → prefer the robust-median config over the IS-best.
3. Keep `bootstrap_nav.py` (circular block) as the sizing anchor; a stationary-bootstrap cross-check is
   cheap insurance for any leverage/sizing decision.

**Bottom line for V2.4:** core edge **clears deflation decisively (DSR≈1.0, no red flag)**; the config-family
selection carries a **moderate, disclosed** overfit risk (PBO≈0.20) that the robustness-first deploy choice
already mitigates; the drawdown-tail anchor (~−29%) is **method-robust**. No production change indicated.
Artifacts: `dsr_pbo_annex.py` (reproducible), this section.

## Wave1/H8 — 2 micro-audits data-gated (2026-07-05, Taylor, job Taylor_20260705_085949)
**Scope:** RESEARCH ONLY — reads/counts, NO production touched. New file `probe_lag_capacity_h8a.py` only.

### H8a — LAG capacity tiebreaker (d_NPR): does the ~12-name capacity actually BIND?
**Q (Mike):** Over 2014-2026, how often do LAG PEAD candidates (NP_R≥15 ∧ prior_n_good≥4 ∧ pa_HL3≥5, entry=Release_Date+5 sessions) exceed the LAG book's slot limit? Bind <10% → CLOSE (registry ~L628 allows d_NPR only as a *capacity tiebreaker*, not a hard filter). Bind ≥10% → propose d_NPR TIEBREAKER (un-coded).
**Slot-limit correction (the real answer to "look up the correct slot limit"):** `MAX_POS_V11=12` (pt_v23_audit_2014.py:477) is the **BAL/V11 momentum book** cap ("tier 10%/name, max 12", L11) — **NOT LAG**. The **LAG book is explicitly SLOT-EXEMPT** (`slot_exempt_tiers=set(tiers)`, L1117; header L15 & audit-meta L1960 "stop/slot-exempt", "sized on each book's free cash"). LAG names are sized LAG_HI 10% / LAG_LO 8% of book NAV (L1029) → **effective free-cash capacity ≈ 10-12 concurrent names** before cash exhausts. So there is no hard slot *count*; the binding resource is free cash (~12-name ceiling). The registry "capacity-constrained at 12 slots" language = that ~12 effective ceiling.
**Method (faithful to [4] Building LAGGED schedule):** rebuilt prior_n_good & pa_HL3 EXACTLY (LN2, HL=3.0; good=NP_R≥15 & post_ret notna) from `earnings_events_classified.csv`; gate NP_R≥15 ∧ prior_n_good≥4 ∧ pa_HL3≥5; entry=Release_Date+5 sessions on global calendar (`bq_cache/ticker/*.parquet`, 3364 sessions); hold=25 sessions (audit-meta L1959). Window 2014-01-01..2026-06-15. Compared concurrent demand vs 12-slot effective cap.
**Result — capacity binds ESSENTIALLY ALWAYS (≫10%):**
- Gated LAG entries in window: 5317. **Concurrent-holdings demand: median 74, mean 76, p90 147** (vs ~12 cap). **92.2% of entries** occur when >12 names are already concurrently held; **51.9% of all sessions** hold >12; peak 210.
- Literal reading (new candidates on a single entry-day >12): 22.0% of entry-days (max 132/day).
- **Robustness on count-scale:** current `earnings_events_classified.csv` was regenerated 2026-07-03 to a broader 1225-ticker universe (rows 2011:1477→2025:4417), so 5317 is ~2.3× the 2026-06-27 harness's 2345 FULL entries. **But even at the conservative harness scale, avg concurrent = 2345×25/3105 ≈ 18.9 > 12.** Direction invariant to CSV version. (Illiquid tail partially fills under LAG's 20%-ADV/5-day model → true tradeable oversubscription somewhat lower than 74, still far above 12.)
- **Current implicit tiebreaker when cash is scarce = SURPRISE** (TIER_PRIORITY LAG_HI 88 > LAG_LO 82, L1028) — higher-surprise names funded first. d_NPR would be an alternative/additional funding-priority key.
**VERDICT: bind ≫10% → do NOT close; PROPOSE d_NPR as a SOFT funding-priority TIEBREAKER (un-coded).** The ~12-name free-cash ceiling is oversubscribed by ~6× (median 74 want-to-hold for ~12), so a selection mechanism is *already materially engaged* — a real place for d_NPR (prefer d_NPR≥0 accelerating-growth names, event-study PASS +1.86pp OOS T+25, job …120256). **CAVEATS (why low-confidence):** (1) the d_NPR **HARD FILTER** form was already 50B-harness REJECTED (job …121416: −1.44pp FULL, destroys IS −2.87pp); a TIEBREAKER (reorder scarce-cash funding, do NOT drop events) is a DIFFERENT, untested form. (2) namecap weight-tilt partner study showed the signal "doesn't translate through the ~12-slot + sizing + dilution" → likely small. **Next step (NOT done here, per dispatch "chưa code"): faithful 50B V2.4 A/B of the TIEBREAKER form (reorder LAG funding priority by d_NPR within/above the surprise tier) vs baseline surprise-only ordering — wire only if OOS CAGR↑ ∧ Calmar↑ ∧ no IS damage.**

### H8b — Foreign-flow data audit (PIT foreign buy/sell net flow by ticker/day, 2014+)
**Method:** searched `bigquery_dictionary.json` + full `tav2_bq.INFORMATION_SCHEMA.COLUMNS` (40 tables) for foreign / nn_ / ngoai / khoi / forbuy / forsell / netflow / flow / buy / sell variants.
**Result: NO foreign-flow columns anywhere in tav2_bq.** Zero matches on foreign/investor-flow names. Only "invest/flow"-adjacent hits are `CF_Invest_*` (cash-flow-from-investing) and `LtInvest_P0` (long-term investments) = financial-statement items, NOT investor flow. `ticker`/`ticker_1m`/`ticker_prune` (174 cols each) carry only OHLCV + TA + fundamentals; no foreign-ownership/flow field.
**VERDICT: CLOSED — foreign-flow data is NOT available in tav2_bq. Backlog item if collection is desired (would need a new ingest source, e.g. HOSE/HNX foreign-trade feed); no build here.**

---

## Wave1/H8a-tiebreaker — LAG within-tier d_NPR fill-reorder (FULL-NAV A/B) — CONDITIONAL PASS, LUMPY (2026-07-05, job `Taylor_20260705_135028`)

**What:** the H8a TIEBREAKER proposal (not the rejected hard filter of line 659). Env `LAG_FUND_DNPR` in `pt_v23_audit_2014.py` (L471/780-806/1056-1058/1660): when a LAG entry-day has more same-tier candidates than free cash allows, **reorder within the tier by `_fund_tb` (d_NPR = accelerating net-profit YoY)** so accelerating names fill first. **Reorder-only inside a tier — never crosses tiers, never drops an event.** OFF-default → combine loop byte-identical baseline (verified). NaN (first event) treated neutral(0).

**Config (contemporaneous):** `LAG_FUND_DNPR=1 BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" AUDIT_END=2026-06-19 $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge`. threads=1 pinned. Logs `data/h8a_logs/{baseline,treatment}_h8a.log`; CSVs `..._etfliqcustompitg_wtnamecap.csv` (baseline) / `..._dnprREORDER.csv` (treatment). IS/OOS sliced from `combined_nav` daily (FULL reproduces script print exactly).

| Metric | Baseline (DNPR off) | Treatment (DNPR=1) | Δ |
|---|---|---|---|
| FULL CAGR / Sharpe / MaxDD / Calmar | 27.34% / 1.81 / −17.6% / 1.55 | 28.07% / 1.87 / −17.5% / 1.60 | +0.73pp / +0.06 / +0.1pp / +0.05 |
| IS (2014-19) CAGR / Sharpe / Calmar | 26.74% / 1.81 / 2.01 | 26.52% / 1.82 / 1.98 | **−0.22pp** / +0.01 / −0.03 |
| OOS (2020+) CAGR / Sharpe / Calmar | 27.89% / 1.80 / 1.58 | 29.50% / 1.90 / 1.68 | **+1.61pp** / +0.10 / **+0.10** |

- **Self-check 0 VND both** (BAL/LAG cash-flow identity + final-NAV identity = 0; borrow 0; max gross combined 1.000). Baseline FULL 27.34% == H3-family R3 baseline (byte-identical family confirmed). LAG book final 441.4B → 515.0B; LAG stock events 6692 → 6897 (reshuffle changes which names hold when cash exhausts → compounds over 12y).
- **WIRE-rule literally MET:** OOS CAGR↑ (+1.61pp) ∧ OOS Calmar↑ (+0.10) ∧ IS not materially hurt (−0.22pp CAGR, +0.01 Sharpe = within-noise flat).
- **BUT LUMPY — the trap:** per-year OOS delta = **2021 +12.24pp and 2023 +10.27pp CARRY EVERYTHING**; the other 5 OOS years are net-negative and **2024 gives back −4.68pp**. Drop either 2021 or 2023 (per-year LOO) → OOS edge flips negative. A within-tier fill-reorder firing only under cash scarcity is inherently **order-of-fill dependent** (threads=1 pinned) → a 2-year concentration reads as reshuffle-luck, not a durable signal edge. Same pattern the registry already flags (d_NPR hard-filter line 659; H3 single-year carry).

**VERDICT: CONDITIONAL PASS — do NOT auto-wire on the literal rule. Route to quant-skeptic + explicit per-year LOO (does edge survive dropping 2021 AND 2023?) before any production wiring.** Env kept OFF-default (baseline byte-identical). No production change this job. If it survives LOO+skeptic, deploy as a SOFT within-tier tiebreaker (matches earlier H8a proposal "TIEBREAKER not filter"), never a hard event-drop.

### Wave1/H8a-tiebreaker LOO (leave-one-out) — **CONFIRMED-LUMPY, DO-NOT-WIRE** (2026-07-05, job `Taylor_20260705_143219`)

**Method (ZERO re-run):** recomputed OOS (2020-01-02→2026-06-19) CAGR/Sharpe/Calmar from the two **frozen** DAILY `combined_nav` series (`loo_h8a_dnpr.py`, reads baseline + `_dnprREORDER` CSVs only). Metrics follow `calc_metrics` convention (Sharpe×√252, Calmar=CAGR/|MaxDD|); LOO annualizes by retained trading days ÷ OOS sessions/yr (spy=249.2, constant across subsets so the trt−base delta is method-invariant). No backtest re-run, env OFF-default, no production file touched.

| OOS subset | base CAGR / Calmar | trt CAGR / Calmar | Δ CAGR / Δ Calmar | trt vs base |
|---|---|---|---|---|
| Full (2020+) | 27.89% / 1.58 | 29.50% / 1.68 | **+1.61pp / +0.10** | WINS (reproduces prior) |
| drop 2021 | 17.46% / 0.99 | 17.93% / 1.02 | +0.47pp / +0.03 | marginal win (level collapses ⇒ 2021 dominates level) |
| drop 2023 | 28.97% / 1.64 | 28.96% / 1.65 | **−0.00pp / +0.01** | edge VANISHES (2023 carried the CAGR edge) |
| **drop 2021+2023 (CORE test c)** | **16.43% / 0.93** | **14.90% / 0.85** | **−1.53pp / −0.08** | **trt LOSES** |
| drop 2024 | 28.89% / 1.64 | 31.75% / 1.81 | +2.86pp / +0.17 | wins BIG (removing the giveback year inflates apparent edge — the overfit tell) |

- **CORE test (c) fails:** with both boom years removed, treatment is **strictly worse** than baseline on both CAGR (−1.53pp) and Calmar (−0.08). The entire OOS edge is reshuffle-luck concentrated in 2021+2023.
- **Mirror-image confirmation:** dropping the giveback year 2024 *inflates* the edge to +2.86pp — the classic sign of an unstable, year-dependent effect rather than a durable signal. Drop the good years → edge dies; drop the bad year → edge balloons.
- **MaxDD is inert** (−17.5% vs −17.6% in every subset): reorder-only changes *which* names hold when cash exhausts, not the risk path — the only lever is CAGR, and that lever is 2-year lumpy.

**VERDICT: CONFIRMED-LUMPY-DO-NOT-WIRE.** H8a-tiebreaker LAG_FUND_DNPR closed. The literal WIRE-rule (OOS CAGR↑ ∧ Calmar↑) was met on full OOS but is an artifact of 2021+2023; it does not survive leave-one-out. Env `LAG_FUND_DNPR` stays OFF-default permanently (baseline byte-identical). No production wiring. Matches the registry's standing pattern (d_NPR hard-filter line 659; H3 single-year carry) — a within-tier fill-reorder under cash scarcity is order-of-fill dependent and not a robust edge.

#### Full per-year LOO — year-sensitivity annex (2026-07-05, job `Taylor_20260705_144651`, completeness only)

Per quant-skeptic's optional suggestion at verify time (job `Taylor_20260705_143219`): leave-one-out for **every** individual OOS year, not just the 2021/2023/2024 hand-picked set. Same ZERO-re-run method / same frozen CSVs / same `spy=249.2` convention (`loo_h8a_dnpr_yearsens.py`, reads only the two audit series). **This does NOT change the verdict — it only documents year-sensitivity in full.** Full-OOS edge = **+1.61pp** CAGR; "edge vs full" = how the drop-one-year edge shifts relative to that (negative shift ⇒ dropped year *carried* the edge; positive shift ⇒ dropped year *dragged* the edge down).

| Drop year | base CAGR / Calmar | trt CAGR / Calmar | Δ CAGR / Δ Calmar | edge vs full (Δpp) | reads as |
|---|---|---|---|---|---|
| 2020 | 27.99% / 1.59 | 29.95% / 1.71 | +1.96pp / +0.12 | +0.36 | ≈ neutral |
| **2021** | 17.46% / 0.99 | 17.93% / 1.02 | +0.47pp / +0.03 | **−1.14** | **CARRIES edge (runner-up)** |
| 2022 | 35.04% / 1.99 | 37.38% / 2.13 | +2.33pp / +0.15 | +0.73 | drags edge down |
| **2023** | 28.97% / 1.64 | 28.96% / 1.65 | −0.00pp / +0.01 | **−1.61** | **CARRIES edge (primary — full edge collapses to ~0)** |
| 2024 | 28.89% / 1.64 | 31.75% / 1.81 | +2.86pp / +0.17 | **+1.25** | **biggest DRAGGER (giveback year — edge balloons when removed)** |
| 2025 | 26.41% / 1.72 | 28.59% / 1.95 | +2.18pp / +0.23 | +0.57 | drags edge down |
| 2026 (partial→06-19) | 30.86% / 1.75 | 32.46% / 1.85 | +1.60pp / +0.10 | −0.01 | ≈ neutral |

- **Concentration confirmed at full resolution:** the two edge-carrying years are exactly **2023 (primary, −1.61pp shift)** and **2021 (runner-up, −1.14pp shift)** — dropping either single-handedly guts the edge. Every other year *drags the edge down* or is neutral: **2024 is the biggest single dragger** (+1.25pp shift — remove the 2024 giveback and the apparent edge balloons to +2.86pp), with 2022 (+0.73) and 2025 (+0.57) also dilutive, and 2020/2026 ≈ neutral.
- **Single-year-drop caveat (why the CORE test is a 2-year drop):** dropping 2023 *alone* leaves the edge at −0.00pp (not negative) because 2021 still props up the level; it takes removing **both** 2021+2023 to push trt strictly below base (−1.53pp, core test c above). The two boom years jointly — not either individually — are the whole story.
- **Verdict UNCHANGED: CONFIRMED-LUMPY-DO-NOT-WIRE.** The full 7-year LOO adds resolution, not a reversal: the edge lives in 2 boom years and every non-carrier year is neutral-to-dilutive. No production wiring; env `LAG_FUND_DNPR` stays OFF-default.

---

## Sector #16 — Textile / Garment EXPORT (2026-07-05, job `Taylor_20260705_154537`)

**Framework:** `mike/agents/Taylor/textile_valuation_framework.md` · **Script:** `textile_screen.py` ·
**Artifacts:** `data/textile_{qualityvalue,basket}_monthly.csv`, `data/textile_verdict.json`.
First sector outside the 2026-06-30 15-sector sweep. Distinct economics: **USD revenue (export) / VND cost
(labor) + order-book-driven demand**. Universe (hand-curated, ICB lumps textile+apparel): liquid export core
TCM/TNG/MSH/GIL/VGT (ADV>5B); thin tail STK/EVE/ADS/HTG/GMC/VGG. Method: point-in-time monthly, ASOF ≤120d,
T+1, TC 0.1%, threads=1, hold cash when empty. **Self-check 0 VND: PASS** (qualityvalue 1e-6, basket 2e-6).

### FX-sensitivity test — hypothesis REFUTED (the headline)
Dispatch hypothesis: VND depreciation (USD/VND↑) lifts VND-translated export revenue → forward tailwind.
Tested causally (USD/VND 3M/6M momentum at *t* vs `profit_1M/2M/3M`, EVALUATION-ONLY), 17.8k name-days.
**Result is the OPPOSITE and significant:** Spearman(fx6m, profit_3M) = **−0.177** (textile) vs **−0.118**
(whole market). VND_weak regime (fx6m>+1%) → fwd-3M **−0.8%**; VND_strong → **+8.0%**. The "weak-VND-helps-
exporters" thesis is **dominated by the risk-off confound** — USD/VND spikes are a global-tightening proxy
that crushes all VN equity, and textile (high-beta cyclical exporter) gets hit *harder*. **FX depreciation is
NOT a tradeable long signal; it flags macro stress ("size down").** (Fertilizer-2021 pattern: the metric ≠ the
catalyst.) NB: `data/vcb_fx_rate.csv` live feed (Winston 2026-07-05) is forward-monitoring only, not backtestable.

### Backtest (net vs B&H VNINDEX)
| screen | window | net CAGR | Sharpe | MaxDD | Calmar | B&H CAGR | edge |
|---|---|---|---|---|---|---|---|
| **A quality-value** | FULL 14-26 | **−0.78%** | 0.09 | −59.1% | −0.01 | 10.23% | **−11.01pp** |
| A quality-value | IS 14-19 | 2.00% | 0.19 | −29.4% | 0.07 | 8.96% | −6.96pp |
| A quality-value | OOS 20-26 | −3.34% | 0.03 | −44.3% | −0.08 | 11.45% | −14.80pp |
| **B basket EW** | FULL 14-26 | 10.04% | 0.44 | −56.8% | 0.18 | 10.23% | −0.19pp |
| B basket EW | IS 14-19 | 4.32% | 0.28 | −32.5% | 0.13 | 8.96% | −4.64pp |
| B basket EW | OOS 20-26 | 15.76% | 0.56 | −56.6% | 0.28 | 11.45% | +4.30pp |

- **Screen A (quality-value) FAILS** — worse than B&H both IS (−6.96pp) and OOS (−14.80pp). Cash 90/140 months
  (margin-stable quality names rarely *also* cheap-vs-history) → concentrated 1-name whipsaws (2020 caught
  MSH/TCM but they lagged −8.4%; 2022 order-collapse −37.7%). **Not a book.**
- **Screen B (basket)** ≈ B&H CAGR but −57% MaxDD (vs −43%), lower Sharpe. OOS "+4.30pp" is **entirely** 2020
  (+124%) + 2021 (+75%) COVID reopening/PPE order-surge — un-repeatable (2022 −44.7%, 2025 +1.6% vs mkt +44%).
  **High-beta cyclical, not a durable book.**
- **Gate = alpha (as a lens):** GPM-CV(P0..P7)<0.15 + IntCov>1.5 + ROE5Y>0.15 correctly ranks MSH (elite) >
  TCM (margin-stable, ROE now faded <0.15) >> TNG (thin-CMT trap: NPM~0, Debt_Eq 2-4, IntCov<0); ejects GIL
  (CV 0.38), STK (losses), VGT (ROE 0.07), EVE (0.04). **Verify:** MSH CAUGHT 18mo (incl 2020 COVID), TCM
  CAUGHT 33mo (incl 2018-19 IntCov-turn window pre-2020-21 surge), TNG/STK/VGT REJECTED, GIL leaked 11mo
  2021-22 (transiently-stable margin pre-Amazon-loss, documented). Ortho 34% c30V / 2% 8L; median ADV 15.8B.

### Verdict: **LENS, not a BOOK** (sweep Rule 3 holds). Do NOT wire a textile sleeve.
Durable artifacts: (1) FX thesis refuted — don't size up on VND weakness. (2) GPM-CV+IntCov+ROE gate = a
single-name evaluation lens. (3) **MSH = the one genuine quality compounder** (ROE5Y 25-34%, IntCov 8-60),
buy-and-hold-on-weakness (like DHG pharma; timing destroys it) — and **cheap-vs-own-history right now**
(2026Q1: PE 6.5 < PE_MA1Y 7.6, PB 1.78, ROE5Y 24.9%). No HPG/DGC/MWG-style catchable compounding book exists.

---

## Sector #17 — Livestock / Animal-Feed (HOG CYCLE) (2026-07-05, job `Taylor_20260705_160724`)

**Framework:** `mike/agents/Taylor/livestock_valuation_framework.md` · **Script:** `livestock_screen.py` ·
**Artifacts:** `data/livestock_{troughbuy,basket}_monthly.csv`, `data/livestock_verdict.json`,
`data/livestock_prices.csv` (full-ticker panel — prune cache stale for BAF/HNG). Second sector outside the
2026-06-30 sweep. A genuine **protein/hog commodity cycle** (opposite of defensive F&B #10): margins swing on
hog price (supply, ASF disease) vs imported feed cost. **P/E goes NEGATIVE at the trough** (DBC 2023Q1 PE −19.8,
2023Q3 −87.1) → value on **P/B-trough + margin-turn**, not P/E. Universe (hand-curated): liquid core
DBC/BAF/HAG/HNG (ADV>5B); thin tail MML/VLC/VSN/APF/HKB/AGM (<3B). Aquaculture (VHC/ANV/MPC) deliberately
excluded (export-FX cycle = textile #16 story). Method: point-in-time monthly, ASOF ≤120d, T+1, TC 0.1%,
threads=1, hold cash when empty. **Self-check 0 VND: PASS** (troughbuy 0.0, basket 0.0).

### Hog-cycle signal test — SIGNAL CONFIRMED (the headline; contrast with textile's refuted FX)
No hog-price field in BQ → GPM as cycle proxy. Causal, 22.4k name-days. Mean forward return by regime:
`trough_up` (PB<MA1Y AND GPM turning up) = **+8.3% fwd-3M** vs `rich_down` +1.1% vs `mixed` +0.4%. BUT the
work is the **margin inflection**, not the cheap multiple: Spearman(GPM_turn, profit_3M) = **+0.117**, while
`pb_rel` alone = **+0.002 ≈ whole-market −0.003** → **P/B-trough alone is a value trap** (steel lesson).
**Rule: buy hog names only when margin is turning up off a trough (GPM_P0>GPM_P4) AND cheap-vs-history.**

### Backtest (net vs B&H VNINDEX)
| screen | window | net CAGR | Sharpe | MaxDD | Calmar | B&H CAGR | edge |
|---|---|---|---|---|---|---|---|
| **A trough-buy** | FULL 14-26 | **10.07%** | 0.46 | −27.0% | 0.37 | 10.27% | −0.19pp |
| A trough-buy | IS 14-19 | 10.41% | 0.53 | −7.2% | **1.45** | 8.96% | **+1.45pp** |
| A trough-buy | OOS 20-26 | 9.76% | 0.43 | −27.0% | 0.36 | 11.51% | −1.75pp |
| **B basket EW** | FULL 14-26 | **−1.30%** | 0.17 | **−82.9%** | −0.02 | 10.27% | −11.57pp |
| B basket EW | IS 14-19 | −20.61% | −0.37 | −80.9% | −0.25 | 8.96% | −29.57pp |
| B basket EW | OOS 20-26 | 20.99% | 0.63 | −54.3% | 0.39 | 11.51% | +9.48pp |

- **Screen A trough-buy ≈ B&H CAGR (−0.19pp) at HALF the DD (−27% vs −43%)**, IS +1.45pp / Calmar 1.45. But
  holds **cash 121/151 months** (margin-turn rarely fires; 30 mo in market, median **1 name**) → edge is
  **extremely lumpy** (DBC 2018 +98.7pp, 2020 ASF +50.8pp, 2023 +18.7pp; cash through 2016/17/21 bulls; 2026
  −22.6pp). **Valid single-name timing LENS, not a book** (OOS −1.75pp — Wave1/H8a boom-year-lumpiness lesson).
- **Screen B basket un-investable** — **−82.9% MaxDD**, FULL −1.30% CAGR (HAG near-default + HNG losses
  2015–19); OOS "+9.48pp" is entirely the 2020-21-23-24 hog up-cycles.
- **Verify:** DBC CAUGHT 14mo incl 2019Q4→2020 pre/into-ASF (PB 0.68<MA1Y 0.75) → the explosion · BAF leaked
  9mo 2023 (post-IPO multiple deflating PB 5.4→1.5 misread as cheap; later ejected by CF_OA_3Y<0 — honest
  documented leak, like GIL) · HAG 6mo/HNG 3mo. Ortho 33% c30V / 12% 8L; median selected ADV **56.9B**.

### Verdict: **LENS, not a BOOK** (sweep Rule 3 holds). Do NOT wire a livestock sleeve.
Durable artifacts: (1) **Hog-cycle entry signal is REAL** (vs textile FX refuted) — but the **GPM-turn
(IC +0.117), not the P/B-trough (IC +0.002 ≈ market), carries it**; buy on margin-inflection-off-trough only.
(2) **DBC = the one catchable name** (HPG-analog: integrated 3F, survives cycle, P/B-trough+GPM-turn entry
works) — but a **cyclical, NOT a secular compounder** (ROE5Y swings 0.11–0.19, IntCov negative 2012–17). It is
timed cyclical-trough-trading, not a hold. (3) **BAF = levered-growth bet** (never cheap on PE, thin margin,
CF_OA_3Y<0) a value screen correctly declines (TNG-analog). **Current read (2026Q1):** DBC cheap-vs-history
(PB 1.03<MA1Y 1.34, PE 6.3) but **GPM-turn NOT firing** (0.17=0.17 flat) + ROE5Y faded 0.11 → **WATCH; buy on
next confirmed GPM turn-up, not the cheap multiple alone.** No MWG/DGC/HPG-style compounding *hold* exists here.

## Hog price → GPM leading-indicator test (DBC/BAF) — 2026-07-06 (job Taylor_20260706_014930)
Follow-up to livestock #17: real weekly hog feed now exists (`data/hog_price_vn.csv`, Winston; North 2019+,
Central/South 2024+). Q: does the weekly hog price LEAD reported quarterly GPM (early-warning vs waiting for the
financial statement)? Script `mike/agents/Taylor/hog_gpm_leadlag.py`. North (Bắc) series (DBC is North-based),
quarterly mean, PIT (hog-quarter known ~30–45d before GPM `Release_Date`). Spearman, DBC 25–29q / BAF 17–19q.

**Verdict: YES — hog-price TURN is a genuine leading/coincident indicator for GPM (economically sound, not FX
noise), but ONE-SIDED (misses feed cost) → EARLY-WARNING overlay, NOT a standalone forecast or GPM-turn
replacement.**
- DBC `hog_yoy` vs `GPM_P0−GPM_P4`: **+0.45 (L0, ~45–90d mechanical early read), +0.55 (L1), +0.68 (L2 peak)**;
  hog level vs GPM level +0.50→+0.62. **Turn-sign agreement 76% (L0) / 71% (L1)** — hog rolls first, GPM follows.
- BAF (purer pure-play) tighter contemporaneous: hog-lvl vs GPM-lvl **+0.76**, hog_yoy vs GPM-turn +0.60/+0.62.
- **QoQ useless (sign 50%)** — quarter-avg too smooth QoQ; only the **YoY transform** carries signal.
- Cycle consistency: 2019–20 ASF (hog +65→96% ↔ GPM-turn +0.036→0.122), 2021 roll-over (hog neg 2021Q2 → GPM
  neg same q, ~5wk before 2021-08 filing), 2024 recovery. 2025→26: hog_yoy neg 2025Q3–Q4 → GPM rolled over
  2026Q1 (0.184→0.170), lead ~1–2q as predicted.
- **CAVEAT (2022):** hog recovered (+16→21%) but GPM-turn stayed −0.083→−0.112 (corn/soy feed spike) → hog =
  half the spread; necessary-not-sufficient. Small-sample, North-only history, no hard IS/OOS; exact lag (L1–2)
  = supportive-not-proven (YoY autocorr); the **76% L0 turn-sign match is the solid mechanically-guaranteed part.**
- **NOW (data ≤2026-06-27):** North hog 2026Q2 = 66,113 (**yoy −2.5%, qoq −5.9%**, faded from Q1 70,230) →
  indicator DOWN → DBC 2026Q2 GPM (files ~late-Jul) flat-to-soft, **no inflection imminent → WATCH holds** (now
  confirmed a quarter EARLY by hog, independent of the financial statement). No early buy-trigger.
- **Rule added (Part 7, overlay only):** Amber = `hog_yoy` turns positive/rising off trough → WATCH→ARMED
  (fires ~1q early); Green = reported `GPM_P0>GPM_P4` still required to act (feed-cost can veto, 2022); feed
  stale → no amber, fall back to pure GPM-turn. RESEARCH-only, no production change.

## Hog−FEED margin-spread proxy (completes the GPM signal) — 2026-07-06 (job Taylor_20260706_022555)
Follow-up to the hog leading-indicator test above: Winston built the feed side (job Winston_20260706_021459) —
`data/maize_monthly.csv` + `data/soybean_meal_monthly.csv` (World Bank Pink Sheet, USD/mt, monthly 2006-04+).
Q: does `spread = hog − feed_cost` explain GPM BETTER than hog alone, and does it FIX the 2022 false-positive
(hog recovered but GPM stayed deeply negative because corn/soy spiked)? Script `mike/agents/Taylor/hog_feed_spread.py`.
**Unit-safe:** feed (USD/mt) & hog (VND/kg) never mixed in levels — all YoY / rolling-z. Feed basket = physical-
tonnage-weighted $/mt of the pig-feed mix, base **corn:sbm 60:40** (sensitivity 50:50 & 70:30). `spread_yoy =
hog_yoy − feed_yoy`, tested at feed_lag 0 & 1q (imported-feed inventory pass-through). DBC 25q, BAF 17q. Self-check
n/a (correlation study, no NAV sim). 0 look-ahead (hog+feed of quarter Q known before GPM_Q `Release_Date`).

**Verdict: feed overlay is a REAL value-add — but ONLY for DBC (integrated 3F). BAF (pure farmer) REFUTED.**
- **DBC:** hog-alone corr(GPM-turn) +0.445 / sign-agree 76% → **spread_yoy feed_lag=1q +0.617 / 84%** (spread_z
  +0.637). Weight-robust: corr +0.512→+0.522, sign-agree 76→80% across 50:50 / 60:40 / 70:30.
- **THE 2022 TEST PASSED (the point):** hog-alone WRONGLY said margin-UP 2022Q3/Q4 (hog_yoy +15.7%/+20.5%);
  spread correctly said DOWN (feed_yoy +16.9%/+24.0% → spread −1.1%/−3.5%) matching actual GPM-turn −0.083/−0.112.
  Both quarters flip WRONG→OK. Feed clearly outran hog → margin clearly fell = arithmetic, not a fitted lag → the
  **non-overfit, mechanically-solid part of the finding.** (One new near-flat miss: 2023Q2 spread +13% vs turn
  −0.012.)
- **BAF: overlay HURTS** — sign-agree 76%→59%, corr +0.598→+0.407. Pure-play farmer margin maps directly to hog;
  world feed adds noise not signal (different sourcing). **→ feed overlay is DBC-only; BAF keeps hog-alone.**
- **Caveats:** small n (DBC 25q/BAF 17q); world feed ≠ DBC delivered input cost (FX/hedge/milling/inventory — the
  corr-max feed_lag=1q is itself a crude inventory-lag proxy); no hard IS/OOS. Exact +0.617 = supportive; the 2022
  fix = proven.
- **NOW (data ≤2026-06-27):** spread MORE cautious than hog-alone. 2026Q2 hog_yoy −2.5% AND feed_yoy turned back
  UP +10.1% (maize+sbm bottomed 2025Q3, recovering) → **spread_yoy −12.6%, most negative since 2023** → cost side
  now adding to the squeeze. **Reinforces WATCH a notch harder; no up-inflection; DBC WATCH holds.**
- **Rule upgrade (Part 8):** DBC Amber now = `spread_yoy` (hog_yoy−feed_yoy, feed lag1, 60:40) turns positive &
  rising off trough (won't arm on a hog rally a feed spike is eating — the 2022 trap). Green unchanged (reported
  `GPM_P0>GPM_P4` required to act). BAF keeps Part-7 hog-alone. Fail-safe: feed/hog stale → hog-alone → pure
  GPM-turn. RESEARCH-only, no production change.

## Construction contractors (civil/industrial EPC) — sector #18 — 2026-07-06 (job Taylor_20260706_033659)
Framework `mike/agents/Taylor/construction_valuation_framework.md`; screen `construction_screen.py` →
`data/construction_{arquality,basket,pbtrough}_monthly.csv` + `data/construction_verdict.json`. Universe (hand-
curated, liquid ADV-2024+>5B): CTD VCG HBC FCN LCG C4G HTN DPG VC3 DC4 G36. EXCLUDES BOT-toll asset-owners
CII/HHV/CTI/PC1 (→ rating_8l D&A_HEAVY) + telecom-infra CTR (ICB trap) + RE developers (sector #3). Monthly EW,
TC 0.1%, hold-cash-when-empty, ASOF financials (STALE≤120d), threads=1. **Self-check 0 VND PASS** (arquality 0.0,
basket 4e-6, pbtrough 3e-6). IS 2014-19 thin (liquid breadth only from ~2019: C4G/HTN'19, G36'20, DC4'21).

**VERDICT: LENS, NOT A BOOK (Rule 3). No watchlist buy candidate. Deliverable = a RISK/EXCLUSION framework.**

**PART 1 signal test** (Spearman IC vs fwd profit_1M/2M/3M, eval-only; 25,341 name-days):
- **`pb_rel`=PB/PB_MA1Y (trough proxy): IC(3M) −0.065 WRONG-SIGNED** — cheaper-vs-history → WORSE fwd return =
  the P/B-trough TRAP. **20× more negative than whole-market baseline (−0.003)** → sector-specific, sharper than
  steel. `dso_chg` −0.030 (correct sign, weak). `ar_rev` +0.002 (noise; AR level is structural). **`cfoa`=CF_OA_P0
  +0.052 = the ONLY reliably correct-signed factor** (cash-generative outperform), but weak.
- Regime mean fwd-T60: clean 5.5% / mixed 6.3% / stressed 3.8% (n 2754/7112/15475) → quality gate avoids the worst
  tercile, does NOT beat mixed → **edge is risk-reduction, not return.**

**PART 2 backtests** (Full 2014-2026 / OOS 2020-26 edge vs B&H VNINDEX):
| Screen | Full CAGR | Full MaxDD | Full Calmar | OOS edge | Months held | Read |
|---|---|---|---|---|---|---|
| A — AR-quality (cheap ∧ CF_OA>0 ∧ CF_OA_3Y>0 ∧ DSO_P0≤DSO_P4·1.15 ∧ IntCov>1.5 ∧ DE<2.5) | 3.1% | **−18.0%** | 0.17 | +0.2% CAGR (≈flat), −11.2pp | **25/148 (cash 84%)** | RISK FILTER not a book |
| B — sector basket (EW beta) | 15.0% | **−62.7%** | 0.24 | −3.1pp, Sharpe −0.20 | 147/148 | pure high-beta; Calmar=B&H |
| C — naive P/B-trough (no quality gate) | 1.3% | **−70.4%** | 0.02 | −9.8pp | 134/148 | the documented TRAP |

**Counterfactual (the point):** Screen A **REJECTED HBC through the entire 2022-24 crisis (0 months)**; Screen C
(naive value) **walked into HBC Oct-2022→Apr-2023 = INTO the −1.2T loss + equity wipeout**. Screen A distinct picks
ever = {VCG,LCG,FCN,DPG} (never HBC, never CTD). Ortho vs custom30V 4% / 8L-top25 16%; median sel ADV 32B.

**HBC crisis anatomy + early-warning (confirmed):** the tell fired ~3q before the 2022Q4 −1,202B loss = **CF_OA_P0
persistently NEGATIVE while P&L still showed profit (2022Q1-Q3), Debt_Eq already >3 & rising** (POC profit =
fictional receivables, Carillion-UK-2018 parallel). P/B a DOUBLE trap: cheap-P/B (0.84-1.03) led into the wipeout,
then P/B mechanically SPIKED to 5.5 mid-crisis as equity collapsed (DSO 139→386, Debt_Eq 3→162). **Read distress via
CF_OA + leverage trend + DSO *trend*, never P/E (POC noise: CTD PE swung −65.6→+140→+322) or P/B.**

**⚠️ LIVE 2026 finding — HTN (Hưng Thịnh Incons) = HBC-repeat in progress.** 2026Q1: DSO **2,425d** (was 1,485 yoy),
AR/Rev **49×**, PE −114, DE 3.66 — receivables collapse tied to a stressed captive developer. **P/B 0.46 is the trap,
not a value entry. AVOID.** HBC still stressed (DSO 473 rising, DE 7.14). No construction name is a catchable
compounder; best discretionary action = WATCH VCG/CTD for a cash-confirmed working-capital turn (tactical, DT5G-gated,
small), never a core sleeve. **Not wired; production untouched.**

## State-Owned-Enterprise (SOE) GOVERNANCE archetype — sector #19 — 2026-07-06 (job Taylor_20260706_040038)
Framework `mike/agents/Taylor/soe_governance_framework.md`; screen `soe_governance_screen.py` →
`data/soe_{broad,privpeer,cashcow}_monthly.csv` + `data/soe_governance_verdict.json`. **NOT a sector — a
cross-cutting GOVERNANCE NOTE** (like 5F moat): state-controlled names (state>50%/de-facto) scattered across
already-screened sectors (GAS/PLX energy#9, POW/NT2 power, VCB/CTG/BID banking, BVH insurance). No BQ ownership
field → state% hand-curated from public structure. Monthly EW, TC 0.1%, ADV≥10B gate, hold-cash-when-empty,
ASOF financials (STALE≤120d), threads=1. **Self-check 0 VND PASS** (broad 4e-6, privpeer 7e-6, cashcow 2e-6).

**VERDICT: GOVERNANCE LENS, NOT A BOOK and NOT a gate (Rule 3). State ownership = a mild return DRAG + a risk
lens; it does not select, does not discount-harvest. Do NOT wire.**

**PART 0 — FLOAT SIGNATURE (the one cleanly-measurable feature):** annual share turnover = ΣVolume/OShares (2024-25).
SOE median **0.181** vs private **0.443** (~2.4× thinner). **Spearman(state%, turnover) = −0.51** (monotone: more
state → thinner float). Most float-starved = the high-lock flagships **ACV 0.040 · VCB 0.105 · GAS 0.115 · VEA 0.117
· BID 0.124.** Liquid EXCEPTIONS (retail favorites, deep-enough public float): POW 0.691, NT2 0.650, VNM 0.428,
PLX 0.406 → "SOE=illiquid" is true for high-lock flagships, NOT universal.

**PART 1 — SIGNAL TEST (Spearman IC vs fwd profit_1M/2M/3M, eval-only; 63,679 name-days, 25 names):**
- **`state_pct` IC(3M) −0.034 (mildly NEGATIVE)** — governance is a small forward drag, not a factor. Mean fwd
  T+60 **SOE 3.16% vs PRIV 4.25%** (~1pp/quarter drag, consistent at T+20/40/60).
- `turnover` +0.019, `DY` +0.027 ≈ zero (liquidity/yield don't rescue). `PB` −0.174 = generic value factor, NOT
  SOE-specific. `pb_rel` −0.052 weak.

**PART 2 — VALUATION DISCOUNT REFUTED (SOE vs private, same sub-sector, 2014+ avg):** flagship trades PREMIUM,
not discount. power SOE/PRIV PB **1.02×**, banks **1.33×**, insurance **2.12×** (BVH). Index-heavyweight state
flagships (VCB/BVH/GAS/SAB PB5.8/VNM PB6.2) earn a scarcity/blue-chip premium that outweighs the governance+float
discount. **No "buy cheap SOE" edge** — a cheap-PB SOE is cheap for a policy/cyclical reason.

**PART 3 — BACKTESTS (Full 2014-2026 / OOS 2020-26 edge vs B&H VNINDEX):**
| Basket | Full CAGR | Sharpe | Full MaxDD | OOS edge | Read |
|---|---|---|---|---|---|
| A — SOE-controlled broad (GAS/PLX/POW/NT2/BSR/VCB/CTG/BID/BVH/VNM) | 9.45% | 0.48 | −48.1% | +0.06pp | lags B&H −0.78pp, worse Sharpe/DD |
| B — private-peer matched (REE/HDG/GEG/ACB/MBB/TCB/VPB/HDB/BMI/QNS) | **14.50%** | 0.69 | −49.4% | **+9.79pp** | control group CLOBBERS SOE, same sectors |
| C — SOE high-DY cash-cow (GAS/PLX/POW/NT2/BSR/PPC) | **4.53%** | 0.30 | **−58.2%** | +0.44pp | IS −11.67pp, Calmar 0.08 |

**INCOME-TRAP proof (C):** price-only CAGR 4.53% **+ ~4.5pp/yr gross div ≈ 9.0% total-return, STILL lags B&H
10.23%** with −58% DD → the "stable high dividend" does NOT compensate for price stagnation. **A-vs-B (9.45% vs
14.50%, same sectors) = state control is a ~5pp/yr realized drag** (directional — B carries more high-beta banks;
but A & C each lag B&H independently, no matching assumption needed).

**Policy case studies (qualitative event layer):** PLX 2022 (fuel price-ceiling losses in a record-oil year —
policy caps upside); POW/NT2 (EVN single-buyer administered PPA — margin policy-set); SAB 2017 (state divested
53.59% → ThaiBev at premium — event windfall); VCB/CTG/BID (SBV forced stock-div + retention for CAR — dividend
policy INVERTED vs cash-cow story); GAS/VEA (PVN/MoIT pull cash up — genuine budget-payout cash-cows); VNM (SCIC
~36% divestment overhang = structural seller). **5 governance rules → sector_watchlist_framework.md Section 2.
No buy watchlist add, no exclude-list add** (flagships handled by their own sector frameworks). Production untouched.

---

## Sector #20 — HOLDING COMPANY / CONGLOMERATE SOTP (Taylor_20260706_042831, 2026-07-06)
**LENS-NOT-BOOK — a VALUATION METHOD (SOTP), not a sector, not a gate.** Files: `holdco_sotp_screen.py`,
`mike/agents/Taylor/holdco_sotp_valuation_framework.md`, `data/holdco_{all,discount}_monthly.csv`,
`data/holdco_sotp_verdict.json`. Self-check 0 VND PASS (all 0e0 / discount 0e0), threads=1, walk-forward
IS(2016-19)/OOS(2020-26). Universe = 4 listed parents with BQ-measurable listed subs.

**coverage = ParentMarketCap / Σ(stake × listed-subsidiary MarketCap)**, MC = unadjusted Price × OShares(ASOF).
Stakes = public economic stakes held constant (documented limit; level sensitive, trend/signal-sign invariant).

**PART 0 — SNAPSHOT (2026-06-26): a clean PREMIUM/DISCOUNT split driven by what the UNLISTED part carries.**
| Parent | Parent MC | Listed-stake val | coverage | reading |
|---|---|---|---|---|
| VIC | 1,757tn | 432tn (VHM 64.9%) | **4.07×** | +307% PREMIUM (VinFast optionality) |
| GVR | 128tn | 8.7tn (PHR+DPR+TRC) | **14.8×** | +1376% PREMIUM (landbank; listed subs only ~7% of cap) |
| MSN | 104tn | 149tn (MCH 68%+TCB 15%) | **0.70×** | −30% DISCOUNT (holdco leverage 1.8-2.9 + complexity) |
| GEX | 27tn | 35tn (VGC 50%+GEE 79%) | **0.77×** | −23% DISCOUNT (classic holdco) |

**PART 1 — blended parent multiples are a lie:** VIC NPM went NEGATIVE 2022 (VinFast) vs VHM +0.30-0.50;
VIC Debt_Eq 3.0→6.7, PB 11.3 (option value) vs VHM PB 2.3. Cannot value VIC on any consolidated ratio.

**PART 2/4 — the discount does NOT mean-revert; deep discount is a TRAP (thesis REFUTED):**
- coverage is a TRENDING series: trend-vs-time MSN −0.68 / GEX −0.62 (secular de-rating), GVR +0.55
  (premium re-rating); AR(1) half-lives 51-259d. Emerging-market discount that never closes.
- pooled Spearman(own-history coverage-z, fwd profit_1M/2M/3M) = **+0.073/+0.054/+0.036** — WRONG-SIGNED for
  the thesis = premium-MOMENTUM not discount-reversion. Buying deep discount predicts WORSE returns.
- DISCOUNT-TILT basket (hold deepest-own-discount half) **LOSES**: Full CAGR 4.5% vs naive EW-all 14.0%,
  DD −57.6%, Full edge −8.1pp. Even naive EW-all "+1.4pp Full" is 100% OOS-luck (IS 2016-19 −19.1pp /
  OOS 2020-26 +16.2pp = VIC+GVR run-up), fails per-year-LOO.

**PART 3 — premium = optionality that deflates violently in CRISIS:** GVR coverage 14.7× (BULL) → 7.2×
(CRISIS). A premium holdco = a long unlisted call option, higher downside beta than its listed NAV; size as
optionality. Discount widening is name-specific (MSN coverage RISES in BEAR — defensive MCH), no universal law.

**VERDICT: valuation-DIAGNOSTIC LENS, not a book, not a gate — DO NOT WIRE** (N=4, discount is a trap, edge is
OOS-luck). Use SOTP to understand what you pay for (listed NAV vs unlisted burn/landbank) + size optionality/
leverage risk; never trade the discount. No buy-watchlist or exclude-list changes. Production untouched.
Added as cross-cutting overlay #20 to `sector_watchlist_framework.md` Section 2 (after SOE overlay #19).

---

## Technical-stabilization filter on WATCH universe (job Taylor_20260706_054234, 2026-07-06) — RESEARCH-ONLY, REFUTED as return filter

**Question (distinct from refuted momentum):** does a "downtrend has STOPPED/stabilized" technical
confirmation improve forward return / avoid deeper drawdown when added on top of the WATCH universe
(cheap-vs-history + quality gate), vs plain WATCH alone? Not "buy strength" (mom200 IC~0.002, already
refuted) — the opposite: filter OUT falling knives (cheap but still dropping).

**Setup** (`technical_stabilization_test.py`, threads=1, point-in-time, 2014-2026):
- WATCH base (proxy for rating<=3 / BUY-NOW): golden floor `ROE_Min3Y>=0 & CF_OA_5Y>0` + cheap
  `pb_z=(PB-PB_MA5Y)/PB_SD5Y<=-0.3` + liquid `Trading_Value_1M_P50>=3bn`. **118,395 daily events / 328 tickers.**
- Stabilization flags (all use current/past fields only): `rsi_bounce` (D_RSI>D_RSI_Min3M+0.05),
  `cmb_notbear` (D_CMB>=0), `price_off_low` (C_L1M>=1.05), `reclaim_ma50` (Close>=MA50),
  `combo_rsi_px`, `combo_ma_cmb`; neg-ref `near_1m_low` (C_L1M<=1.02 = still pinned at 1M low).
- Outcome profit_1M/2M/3M (eval only). Falling-knife = forward 40-sess min-drawdown <=-10% / -20%.
- Honest unit = monthly-cohort spread (daily WATCH rows autocorrelated); t over ~140 monthly obs; IS/OOS split.

**RESULT — stabilization HURTS return, only cuts the deep-DD tail (insurance, not alpha):**

*Return spread (flagged − not-flagged), monthly-cohort:*
| flag | profit_1M FULL (t) | IS / OOS 1M | median-robust 1M (t) |
|---|---|---|---|
| rsi_bounce | **-1.50% (t-4.3)** | -1.17 / -1.80 | -1.77% (t-5.4) |
| cmb_notbear | **-1.51% (t-3.9)** | -1.24 / -1.73 | -1.78% (t-4.7) |
| combo_ma_cmb | -0.86% (t-2.1) | -0.34 / -1.33 | -1.33% (t-3.5) |
| reclaim_ma50 | -0.79% (t-2.0) | -0.25 / -1.29 | — |
| price_off_low | -0.46% (t-1.5) noise | — | — |
| **near_1m_low (STILL falling)** | **+0.55% (t+1.7)** | +0.43 / +0.66 | **+0.94% (t+3.2), hitM 62%** |

- Every stabilization flag has NEGATIVE-to-zero forward-return spread, robust to outliers (median==mean)
  and NEGATIVE in BOTH IS and OOS for rsi_bounce/cmb_notbear (t=-3 to -5). Waiting for stabilization
  FORFEITS the mean-reversion premium that IS the cheap-universe edge.
- The negative reference (`near_1m_low` = the still-falling knife) has POSITIVE spread (+0.94%, t+3.2,
  62% of months) — within an already cheap+quality universe, the MORE beaten-down / still-falling names
  earn MORE forward return. Classic VN mean-reversion; "wait for it to stop falling" = buy higher, earn less.
- Per-year LOO (combo_ma_cmb, profit_2M): +6.1%(2017) but -7.7%(2022)/-4.7%(2026)/-2.7%(2020) — sign
  scattered, no durable edge = noise, not signal.

*Falling-knife (fwd 40-sess drawdown) — the ONE real effect:*
| flag | %dd<=-10 f/nf | %dd<=-20 f/nf | mean dd f/nf |
|---|---|---|---|
| rsi_bounce | 28.3 / 33.5 | 9.1 / 13.2 | -7.62 / -9.02 |
| cmb_notbear | 28.5 / 34.8 | 9.4 / 13.9 | -7.71 / -9.13 |
| combo_ma_cmb | 28.1 / 29.7 | 8.1 / 11.1 | -7.45 / -8.12 |

- Stabilization genuinely trims the DEEP-drawdown tail (dd<=-20%: ~13% → ~8-9%). But it trims the RIGHT
  tail too (net return negative). Textbook insurance: lower left tail + lower right tail + net cost.

**VERDICT:** (1) NO technical-stabilization filter improves walk-forward forward RETURN; rsi_bounce /
cmb_notbear are significantly NEGATIVE (t≈-3 to -5, IS+OOS), the rest noise. (2) DO NOT add as a WATCH→BUY
return filter — keep WATCH→BUY on fundamentals as-is. (3) The only real effect is deep-drawdown-tail
reduction = a RISK GATE (insurance, costs return), same profile as DT5G — NOT wired, not requested for
wiring; a risk observation only, un-vetted vs DSR/multiple-testing. Mirrors & extends the momentum-refuted
result: in VN, buying cheap-and-still-falling beats waiting for the bounce. Artifact:
`data/technical_stabilization_events.parquet`. sector_watchlist_framework.md intentionally NOT touched.

---

## sector_lens_monitor.py — Group-A watchlist 6-state monitor (job Taylor_20260706_062405, 2026-07-06)

RESEARCH/MONITOR tool (read-only), NOT a backtest and NOT a production selector. Builds Section 7
("Harvesting Workflow Proposal") of `mike/agents/Taylor/sector_watchlist_framework.md`, user-approved.
Reads BQ DuckDB cache (`data/bq_cache/`, threads=1) latest `ticker` row (PE/PB/EVEB/PE_MA5Y) + latest
`ticker_financial` row (fundamentals + PE_MA1Y/PB_MA1Y/GPM_P0..P7) + latest `vnindex_5state_dt5g_live`
state + on-disk hog/feed feeds (DBC overlay). Evaluates each name against its OWN `*_framework.md`
entry condition (formulas NOT re-invented) → one of 6 states: EXCLUDED / RICH_WAIT / WATCH / ARMED /
BUY(STRONG|ACCUMULATE) / STALE. Writes `data/sector_lens_status_<date>.csv` (history) + diffs vs prior
file → alerts ONLY on a state transition. Fail-safe: stale row/feed → HOLD last status (never fabricate).

**Baseline run 2026-07-06** (DT5G=BULL/3; hog-feed spread_yoy −0.126, hog↓/feed↑ not supportive) —
all 16 names reproduce the documented Section-0/1 statuses:
| State | Names |
|---|---|
| BUY·ACCUMULATE | FPT, MBB, ACB, HDB, TCB, CTR(9.9 mid-bucket), SSI, VCI, PVT, HAH, MSH, DHG |
| WATCH | DBC (value ✓, GPM-turn ✗, spread not supportive), VND (fails ROE inflection) |
| RICH_WAIT | VCB (PB 2.19 ≥ justPB 1.93, archetype-B) |
| EXCLUDED | HCM (PB 2.02 ≥ 1.8 euphoria cap) |

Self-checks PASS: (a) 16/16 match known states; (b) transition diff fires correctly on a synthetic
prior (FPT RICH_WAIT→BUY, DBC ARMED→WATCH); (c) STALE fail-safe holds prior status & is excluded from
the transition-alert list (data-outage ≠ state change). **CTR** is the only lens with a STRONG tier
(EVEB<9); it currently prints ACCUMULATE. **MSH** GPM-CV=0.178 > nominal 0.15 (rising-margin artifact) —
CV used as elite-ranking context per framework line 139, NOT a hard exclude (documented; flag for user if
a strict hard gate is ever wanted). No cron yet — run by hand; Mike to schedule after a few stable runs.
Production untouched (custom30V/BAL/LAG/rating_8l.py unchanged).

---

### STRONG-tier (screaming-buy) calibration — Group-A sector lenses (job Taylor_20260706_070219, 2026-07-06)

`sector_strong_threshold.py` — RESEARCH-ONLY. Defines a quantified STRONG tier (vs default ACCUMULATE)
for the Group-A sectors that previously had none (only CTR had EVEB<9). **Method** (same as CTR<9): pool
the ICB universe (single-name histories too thin), apply the live monitor gate, split the ACCUMULATE-
eligible population by DEPTH into quintiles, measure forward return (profit_1M/2M/3M, EVAL-ONLY), weekly-
sampled to cut overlap, walk-forward IS(2014-19)/OOS(2020-26). STRONG justified ONLY where a real step-up
survives OOS; smooth/no-break/sign-disagreement → NO STRONG (do not fabricate a line).

| Sector | STRONG line | Evidence (depth Q5 vs Q1-Q4) | Verdict |
|---|---|---|---|
| **Banking** (8355) | **discount ≥ 0.45** (PB≤0.55×justPB) | Q5 disc≥0.46: fwd-1M **+3.7%** / 3M **+11.8%** / hit **69%** vs ~+1.6%/+5%/54%. OOS confirms (+3.68%/1M, hit 69%) | ✅ **ADD** — clean OOS-surviving step |
| **Tech/FPT** (9537) | **PE < PE_MA1Y×0.75** (depth≥0.25) | Q5 best in BOTH IS (+3.5%/1M, hit 83%) & OOS (+7.3%/3M); framework's named 2018/2022-23 entries all sit at depth 0.25-0.29 | ✅ **ADD** — thin sample, corroborated-by-episode |
| **Securities** (8777) | **PB < 0.75** (already DT5G-gated) | ALL step Q3→Q4 at PB≈0.75 (2.1→4.5%/1M); Q4 holds both IS(+3.3%)&OOS(+3.5%); Q5/PB<0.42 huge OOS(+9.3%) but weak IS → robust line=0.75 not deeper | ✅ **ADD** — OOS-loaded, crisis-only trigger |
| **Textile/MSH** (3763) | — | IS best = MIDDLE bucket (+3.4%); Q5 weak IS (hit 36%) but best OOS → sign disagreement at extreme | ❌ **NO STRONG** — no break to trust; ACCUMULATE-only |
| **Pharma/DHG** (4577) | — | depth-return FLAT (Q1 ≈ Q5 both regimes; Q1 often best) | ❌ **NO STRONG BY DESIGN** — data confirms buy-and-hold anchor, timing adds nothing |
| **Logistics/PVT+HAH** (2777/2773) | — | deepest bucket UNDERPERFORMS IS (middle pays best); OOS non-clean | ❌ **NO STRONG BY DESIGN** — high-beta tactical, don't size up "cheaper still" |

**Live read 2026-07-06:** exactly ONE name hits a STRONG line — **FPT** (PE 12.4 < 0.75×PE_MA1Y 14.0),
a 2018/2022-class deep entry; flips ACCUMULATE→STRONG in the monitor. Banking tops at ACB 41%/MBB 40%
(<45%); securities all PB≥1.25 (≫0.75). Wired into `sector_lens_monitor.py` (eval_bank/eval_fpt/eval_sec)
+ the 6 `*_valuation_framework.md` docs + watchlist Section 5/table. STRONG here = a NECESSARY-NOT-
SUFFICIENT display conviction upgrade; still routes through Taylor-validate→DollarBill-plan→user→Mafee.
Production untouched (custom30V/BAL/LAG/rating_8l.py unchanged). Note: profit_* are forward-looking
EVAL-ONLY (never a live filter); PE_MA1Y self-rolled 252d from daily PE for the study (STRONG expressed
as a ratio → MA-source washes out).

#### Follow-up robustness (quant-skeptic CONFIRMED → job Taylor_20260706_074228, 2026-07-06)

Two add-ons requested by the verify pass (both display-only; NO threshold VALUE changed, production untouched).
`sector_strong_threshold.py` extended (`tech_universe_check` + `bootstrap_fpt_strong` + `sensitivity_sweep`).

**Việc 1 — Tech/FPT sample thinness.**
- *Universe cannot be widened.* ICB 9537 USABLE (tradeable ≥1bn VND/day AND ever passes ROIC5Y>0.12 &
  ROE5Y>0.15) = **[FPT] only**. ITD (1.12bn/day) & ICT (1.05bn/day) are liquid but quality-pass=0% (not
  compounders); VLA passes quality 8% but 0.01bn/day = untradeable. FPT is the sole liquid quality tech name.
- *Bootstrap CI (STRONG line depth≥0.25 = PE<0.75×PE_MA1Y).* The 26 STRONG weekly obs are only **~5 de-rating
  episodes** (2018, 2020, 2025, 2026), and **IS is literally ONE episode (2018)** → n_eff, not 13. Episode-cluster
  bootstrap (the honest resampler) vs i.i.d.-weekly (optimistic):

  | Seg (n_eff) | horizon | point | iid-weekly 90%CI | **episode 90%CI** | P(>0) episode |
  |---|---|---|---|---|---|
  | ALL (5) | 1M | +3.22% | [+1.3,+5.4] | [+0.6,+14.2] | 0.98 |
  | ALL (5) | 2M | +3.78% | [+0.4,+7.7] | **[−1.9,+14.4]** | 0.90 |
  | ALL (5) | 3M | +5.32% | [+1.7,+9.4] | [−0.1,+17.6] | 0.95 |
  | IS (1) | 1M | +3.68% | [+1.9,+5.4] | degenerate (1 cluster) | — |
  | OOS (4) | 1M | +2.75% | [−0.6,+6.9] | [−0.3,+19.5] | 0.93 |
  | OOS (4) | 2M | +3.01% | [−3.8,+11.7] | **[−3.0,+24.1]** | 0.62 |
  | OOS (4) | 3M | +6.88% | [−3.4,+17.7] | [−2.4,+24.6] | 0.85 |

  Direction is robust at **1M** (P(>0) ≈ 0.9–1.0) but the episode CIs are wide and **span 0 at 2M/3M**, and IS
  rests on a single 2018 event — the magnitudes (+3.5%/+7.3%) are NOT precisely estimable.
- **Verdict — KEEP the line (PE<0.75×PE_MA1Y), DOWNGRADE its confidence.** Loosening would dilute the depth step
  (Q1–Q4 ≈ +0.5–1%); a hard companion-signal gate would over-engineer a necessary-not-sufficient display flag
  (and the one candidate, technical-stabilization, was REFUTED as a return filter 2026-07-06). Fix = relabel
  STRONG(FPT) as **LOW-CONFIDENCE / "watch-close, confirm independently"** (edited `eval_fpt` tag in
  `sector_lens_monitor.py`), not a stat-standalone screaming buy.

**Việc 2 — Banking & Securities plateau sweep** (forward return/hit over the trigger set at each line, IS+OOS):
- *Banking* discount ∈ {0.40, 0.45, 0.50}: OOS p1M **3.08 / 3.39 / 4.72**, hit1M **0.65 / 0.67 / 0.74**, p3M
  **9.5 / 10.9 / 14.2** — **clean MONOTONE ramp** (deeper = better at every step), NOT a spike at 0.45. Line is a
  robust plateau; 0.45 sits mid-ramp with enough signals (OOS n=684) — 0.50 is even stronger but has zero IS
  triggers (banks rarely traded that deep pre-2020) → **KEEP 0.45**.
- *Securities* PB ∈ {0.70, 0.75, 0.80}: p1M ALL **4.40 / 4.48 / 4.14**, hit1M ALL **0.483 / 0.492 / 0.485**, OOS
  p1M **8.12 / 7.79 / 7.00** — **flat plateau** (results barely move across the ±step); 0.70 marginally best OOS
  but all three equivalent → **KEEP 0.75** (robust, not a single-point artifact).

**Net:** no threshold value changes. Banking/Securities lines CONFIRMED as plateaus (robust). Tech/FPT line kept
but relabeled LOW-CONFIDENCE (single-name, ~5 episodes, 1 IS). Still display/monitor only; routes through
Taylor-validate→DollarBill-plan→user→Mafee. Production (custom30V/BAL/LAG/rating_8l.py) untouched.

---

## sector_lens_monitor → daily 8L Telegram + 8L-rating cross-check (job Taylor_20260706_082923, 2026-07-06)

**What shipped** (research/monitor only — production custom30V/BAL/LAG/rating_8l.py UNTOUCHED):
- `pt_8l_daily.sh` step **[9]** `sector_lens_monitor.py --telegram` (runs AFTER step [1] rating_8l so the
  cross-check reads the same-day fresh `rating_8l.csv`; continue-on-error like every other step). User approved
  **DAILY** cadence (was proposed weekly) — transitions matter, the script is light so a daily read is cheap.
- `sector_lens_monitor.py` gains `--telegram`: sends to the **same 8L Telegram channel** (cfg chat_id via
  `telegram_recommend.load_config`/`send_telegram_text`, identical wiring to cheap_pb_floor.py). NOT the Discord
  Trading-report channel (that stays reserved for verified account numbers).
- Message order (dispatch req 3): (a) **TRANSITIONS first** (`FPT: BUY·ACCUMULATE → BUY·STRONG`) or
  "no transitions today"; (b) status table — BUY/ARMED always shown in full, WATCH/RICH_WAIT/EXCLUDED shown in
  full only on a transition day else collapsed to a count line (anti-spam); (c) **8L cross-check** inline.

**New logic worth pinning — DOUBLE-CONFIRM (two independent systems agree):**
- For each Group-A name, look up its 8L composite-v3 rating from the same-day `rating_8l.csv`. Mark
  **"✓✓ DOUBLE-CONFIRM"** iff `rating<=2` (golden/strong tier) AND sector-lens `status==BUY`. The sector-lens
  (per-name valuation/timing screen) and the 8L rating (cross-sectional fundamental-quality rank) are
  independent constructions, so simultaneous agreement is a genuine two-system consensus.
- Deliberately **no narrative on any other combination** (rating>2+BUY, or rating≤2+RICH/WATCH/EXCLUDED): the
  R# is shown next to every name for reference only — no derived interpretation from a single disagreeing data
  point (dispatch req 3c; same discipline as no-over-fit / necessary-not-sufficient).
- Live example 2026-07-06 (NEUTRAL/DT5G=3): ✓✓ on MBB/TCB/ACB (R2), HAH/DHG (R1), SSI/PVT/CTR (R2), FPT (R2,
  STRONG); NO ✓✓ on VCB (R1 but RICH_WAIT), HDB/VCI/MSH (R3 BUY). Real Telegram send confirmed (`ok:True`).

**Discovered (flagged, NOT fixed — out of scope, zero effect today):** `eval_sec` DT5G gate reads
`state not in (0,1)` but the `vnindex_5state_dt5g_live.state` column is **1-based** (CRISIS=1, BEAR=2, NEUTRAL=3
…). So the securities cash-gate closes only at CRISIS, staying **open in BEAR** (intended: cash in both). No
output change at today's NEUTRAL(3); needs its own fix + skeptic re-verify (STRONG-tier calibration was verified
against current behavior). Telegram label map was corrected to the 1-based convention in this job.

## FIX: eval_sec DT5G gate off-by-one (0-based → 1-based) (job Taylor_20260706_083933, 2026-07-06)

**Bug (flagged in job _082923 above, now fixed).** `sector_lens_monitor.py::eval_sec` closed the securities
cash-gate with `state["state"] not in (0, 1)` — 0-based labels — but the `vnindex_5state_dt5g_live.state` column
is **1-based** (1=CRISIS, 2=BEAR, 3=NEUTRAL, 4=BULL, 5=EX-BULL). Net effect: the gate closed only at CRISIS and
stayed **OPEN in BEAR**, whereas the securities lens is a euphoria/de-risk cap meant to hold cash in **both** high-
risk regimes.

**Design intent confirmed (not re-invented).** The source framework backtest `securities_screen.py` is explicit —
L37 "forced to CASH when DT5G state in {CRISIS,BEAR}", L72 "state in {1 CRISIS, 2 BEAR} = de-risk", L92
`derisk = gate_dt5g and st in (1, 2)`. So the correct condition is `not in (1, 2)` (close at CRISIS **and** BEAR),
matching the 1-based `state` column. `eval_sec` had merely copied the intent with 0-based labels.

**Fix.** `gate_open = state["state"] not in (1, 2)` (+ corrected inline comment). No other logic changed;
production custom30V/BAL/LAG/rating_8l.py untouched — this remains a research/monitor display tool.

**Gate test (injected states, fully-qualifying fundamentals so only the gate decides):**
| state | gate | result |
|---|---|---|
| CRISIS(1) | CLOSED | RICH_WAIT → cash |
| BEAR(2)   | CLOSED | RICH_WAIT → cash  ← was BUY before fix |
| NEUTRAL(3)| OPEN | BUY |
| BULL(4)   | OPEN | BUY |
| EX-BULL(5)| OPEN | BUY |

**Re-verify STRONG calibration — UNCHANGED (conclusion holds).** `sector_strong_threshold.py::gate_and_depth`
for Securities applies **only** the valuation gate (`pb>0 & pb<1.8`); it never applied the DT5G regime gate, so the
STRONG=PB<0.75 line is calibrated on the depth-quintile distribution across all regimes and is **logically
independent** of this fix. Re-ran `sector_strong_threshold.py`: output reproduces the pinned numbers exactly —
Securities OOS deepest-PB Q5 = +9.34%/1M, plateau sweep thr 0.70/0.75/0.80 → p1M 4.40/4.48/4.14, p3M
10.60/10.34/9.90, hit1M 0.483/0.492/0.485. PB<0.75 remains on a robust plateau. **STRONG-tier calibration
conclusion stands; no threshold change.**

---

## ConvergePort — double-confirm converge paper portfolio (job Taylor_20260706_093329, 2026-07-06)

**What.** A NEW paper portfolio at the intersection of AlphaLens (per-name sector-lens BUY) and
Golden/Strong (8L rating≤2) = the DOUBLE-CONFIRM set from `sector_lens_monitor.py`. 2-layer like
V2.4: active converge book (double-confirm names) + idle cash parked in custom30V. Script
`converge_portfolio_backtest.py`; NAV audit `data/converge_portfolio_backtest_nav.csv`; paper book
`data/converge_portfolio_paper.json`; framework `mike/agents/Taylor/converge_portfolio_framework.md`.
RESEARCH/PAPER ONLY — production custom30V/BAL/LAG/rating_8l.py untouched.

**Method (point-in-time, no look-ahead).** Sector-lens BUY decided by the EXACT `eval_*` functions
imported from `sector_lens_monitor` (no rewrite); price-current PE/PB/EVEB from `ticker` at t;
fundamentals as-of `ticker_financial.Release_Date≤t`; DT5G state as-of t (securities gate); 8L
rating as-of `rating_8l_history.csv.eff_date≤t`. Weight = min(0.20, share) of NAV, idle→custom30V
(published `custom30v_8l` basket, buy-and-hold drift). T+1 execution, threads=1. Self-check daily
weight-sum max|dev−1| = **2.2e-16** (0 VND leak). 2014-08-05→2026-06-26, 2970 sessions.

**Walk-forward (TC=0.1%):**
| Config | FULL CAGR | Sharpe | Calmar | MaxDD | IS CAGR | OOS CAGR |
|---|---|---|---|---|---|---|
| custom30V thuần (BASELINE) | 18.75% | 0.87 | 0.41 | −45.9% | 12.72% | 24.03% |
| ConvergePort equal-weight | **23.86%** | **1.11** | 0.52 | −46.1% | 14.22% | 32.54% |
| ConvergePort tilt 1.5×STRONG | 23.74% | 1.10 | 0.52 | −46.0% | 14.22% | 32.30% |
| AlphaLens-static (FPT/ACB/MBB/HDB) | 20.68% | 0.95 | 0.46 | −44.7% | 13.82% | 26.74% |

**Deltas vs baseline (FULL):** EW **+5.11pp CAGR / +0.24 Sharpe / +0.11 Calmar**, DD flat. Edge in
BOTH IS (+1.5pp) and OOS (+8.3pp). Dynamic double-confirm beats static 4-name AlphaLens by ~3pp.

**Robustness.** Turnover EW 4.14×/yr; TC sensitivity 23.74%@0.1→22.58%@0.3% (−1.16pp << 5pp edge →
turnover does NOT eat the edge). Leave-one-year-out full-period ΔCAGR ∈ [+3.42, +5.52]pp dropping
ANY single year (even dropping best year 2024 → +3.42pp) → broad-based, NOT 1–2-year carried;
positive yearly delta 9/13 years. DSR standalone EW **0.998** (n=3), **0.973** (n=16) → clears 0.95.
N trials = 3 (tilt/equal/static), minimal multiple-testing.

**Verdicts.** (1) Beats custom30V thuần: +5.0pp CAGR, yes clearly. (2) Turnover TC-robust, edge
intact to 0.3%. (3) STRONG 1.5× tilt NOT worth it — equal-weight marginally better + lower turnover
→ **launch equal-weight, drop tilt**. (4) → LAUNCH paper (9-name seed, entry 2026-07-06 @ 06-26
prices, review 2026-10-06, benchmark VNINDEX 1871.91), wired as §3 of `newdeals_daily_report.py`.

**Honest caveats.** Backtest parking = RAW ungated custom30V (DD −46%); production custom30V is
DT5G-gated (lower DD) — relative comparison clean (same basket both sides), absolute DD not a gated
book. Excess-over-baseline spread DSR=0.775 (<0.95): marginal edge over parking is statistically
softer than the robust standalone book — expected (shared equity beta). PAPER, not a production wire.

---
## Macro "confidence-loss" combined-regime study — job Taylor_20260706_100438 (2026-07-06, RESEARCH/DISPLAY-ONLY)
Follow-up to macro-corr job _094519. Tests user's SPECIFIC joint hypothesis (not pairwise corr):
"gold↑ AND USD/VND↑ AND (CPI high OR deposit rate rising) = confidence-loss regime → bad for
stocks: thin liquidity + broad decline." Scripts: `macro_confidence_regime.py`, `cpi_vn.py`,
`deposit_rate_vn.py`. Data: VNI+fwd (macro_features.csv 2011+), market turnover SUM(Trading_Value)
ticker_prune (BQ, 2011+), gold world (/tmp, 2016+), CPI YoY (**PROXY anchor** cpi_vn.py — no clean
GSO monthly fetchable: FRED err / WorldBank+TE blocked), deposit rate (**PROXY** deposit_rate_vn.py).

Results (fwd60 = 60-session fwd VNINDEX %, turn_rel = turnover/1y-median, baseline fwd60 +2.60% / turn 1.13x):
| regime (all 6m-momentum) | fwd60 T / F | diff | fwd60 +% T | turn_rel T | vol20 T | n days / episodes |
|---|---|---|---|---|---|---|
| REG_A (gold↑&usd↑&(CPIhot OR dep↑)) | 2.58 / 3.26 | -0.68pp | 61% | 1.15x | 15.3% | 827 / many (weak) |
| **REG_A_strict (gold↑&usd↑&CPI>4 AND dep↑)** | **-2.70 / 3.22** | **-5.92pp** | **35%** | **0.96x** | **23.4%** | **78 / 5** |
| REG_B (drop gold: usd↑&stress) | 3.04 / 2.22 | +0.82pp (REVERSES) | 65% | 1.08x | 15.7% | 1753 / — |
| REG_C (monetary stress alone) | 2.58 / 2.65 | -0.06pp (nil) | 61% | 1.12x | 15.6% | 2777 / — |

REG_A_strict 5 lifetime episodes: 2018-05/06 (fwd60 **-9.9%**), 2019-07 (1d), 2022-12→2023-02
(**+5.2%**, went UP), 2026-01 (fwd60 **-6.3%**), 2026-04/05 (pending). Outcomes MIXED, not uniformly bad.

**Verdict:** user hypothesis SUPPORTED only in strict all-4-binding form (rare days genuinely show
neg fwd return + thin liq <1x + high vol) — economically sensible. BUT thin & fragile: only ~5
episodes (gold→2016+), mixed outcomes, effect collapses/reverses if ANY condition relaxed (OR→AND,
drop gold, drop FX). Welch t=-11 is an OVERLAPPING-window artifact; true evidence = 5 episodes = too
few to call a tradeable regime. Extends prior finding (only SBV rate had stable single-var link);
conjunction beats single vars only in extreme form = flagging 2 known bad patches (2018-Q2, 2026-Q1),
not a repeatable edge. USD/VND is a managed crawl-peg (≈always "up") → weak discriminator. **NOT wired**;
largely redundant with DT5G (already de-risks 2018/2020/2022 via price+US/VIX). CPI/deposit = proxies —
refine if clean GSO/Big-4 series surfaces before any reconsideration.

---
## ConvergePort AS FULL ACTIVE-BOOK REPLACEMENT (2-book V2.4 → 1 ConvergePort book) — 2026-07-06 (job Taylor_20260706_095725, audited by Taylor_20260706_103815)
**Config:** `converge_fullharness_test.py` (production simulate() engine), `CONVERGE_BOOK=1 CONV_WPN=0.11`,
50B, DT5G-gated custom30V parking {3:0.7}, CAPIT ON, TC 0.15/0.15/0.1, borrow 10%, threads=1, T+1 Open fills.
Output: `data/v23_golive_audit_2014_now_CONVERGEPORT_wpn110.csv` (4,350 rows, self-check 0 VND both books).

**What it tests:** replace BOTH active books (BAL momentum SIGNAL_V11 + LAG PEAD) with ONE active book =
ConvergePort double-confirm (sector-lens BUY ∧ 8L rating≤2; 15-name watchlist; per-name fixed weight WPN=0.11).
Wiring: ConvergePort carried in the BAL slot @50B (`sig_f`/`RS` overwritten at code lines 708/709), LAG made
inert (1 VND, `sig_lag` zeroed line 1141), combine = static-sum (single active book). Everything else
byte-identical to R3.

**Result (FULL 2014-01-02→2026-06-19, 12.46y):** CAGR **12.05%** · Sharpe 0.85 · MaxDD **-38.4%** · Calmar 0.31.
IS 2014-19 CAGR 14.84%/Sharpe 1.27/DD -18.5%; OOS 2020-now CAGR 9.51%/Sharpe 0.61/DD -38.4%.
vs VNINDEX B&H CAGR 10.87%/Sharpe 0.66/DD -45.3%.

**VERDICT — DO NOT WIRE (strong REFUTE).** As a full replacement for both active books, ConvergePort is
FAR WORSE than production 2-book V2.4 R3 (CAGR 28.05% / Sharpe 1.86 / MaxDD -17.5% / Calmar 1.60, same
engine/parking/50B/TC): **-16pp CAGR, ~½ the Sharpe, ~2× the drawdown.** Root cause = thin breadth: the
double-confirm book is active on only ~83% of days, mean 3.9 names when active (17% of days 0 names →
100% parking/cash), nowhere near enough names to carry a 50B active allocation. The momentum+PEAD 2-book
engine is materially superior. ConvergePort's value (if any) is as a standalone paper sleeve / lens
(see 2026-07-06 09:47 equal-weight paper launch vs custom30V), NOT as the production active book.

**AUDIT NOTE (why this needed re-verification):** the run's printed labels were STALE and triggered a
false "only BAL ran alone" alarm — header said "25B BAL + 25B LAG", "[6] BOOK A — BAL 25B", "[7] BOOK B —
LAG 25B", and Book B logged "0 stock / final 0.0000B" while combined == BAL exactly. All EXPECTED artifacts
of the single-active-book design (LAG inert at 1 VND → rounds to 0.0000B; combined == BAL because LAG≈0).
Verified 3 independent ways the active book IS ConvergePort (not momentum): (a) code — sig_f/RS overwritten
with ConvergePort at 708/709, no re-overwrite before simulate(), line-1254 re-empty skipped since
IS_SINGLEBOOK=False in converge mode; (b) CSV play_types = only C_<ticker> (ConvergePort tiers) + CAPITB_* +
ETF_PARK, ZERO momentum tiers; (c) all 330 C_ stock trades in BAL book, LAG 0 stock trades, nav_bal_ref
50.0B→206.32B. The misleading labels were fixed (made CONVERGE_BOOK-conditional, lines 529/1257/1750) so
future runs don't misread — NO re-run needed, the 12.05% number is the true correctly-wired result.

## ConvergePort AS-ACTIVE-BOOK — DT5G STATE-GATE ON THE ACTIVE BOOK (does gating fix the deep MaxDD?) — 2026-07-06 (job Taylor_20260706_121242)
**Question (Mike follow-up to _103815):** the as-active-book run has a deep MaxDD. Does the double-confirm
**active** book throttle exposure by DT5G state, does CAPIT apply to it, and would adding a state-gate on
the active book fix the drawdown?

**Code-verified answers (converge_fullharness_test.py, not guessed):**
1. **Active book state-throttled? NO.** Entry/exit is purely double-confirm membership-driven;
   `tier_weights_by_state=None` (L1709), stops/hold/sector-caps disabled. The DT5G regime-size halving BAL
   uses is NOT applied to ConvergePort names → the active book does not scale down in CRISIS/BEAR.
2. **CAPIT applies? YES.** `add_capit_arm(sig_f,…)` (L1737) grafts the washout-buyer onto the SAME BAL-slot
   frame carrying ConvergePort — the `CAPIT=ON` washout events are part of this book, not a separate sleeve.
3. **`{3:0.7}` parking = ONLY total-exposure throttle? YES.** custom30V idle-cash parking follows DT5G
   `{1:0,2:0.2,3:0.7,4:1.0,5:1.0}` on *unused* cash only — it does nothing to money already in active
   positions, so a fully-invested book rides the drawdown in CRISIS/BEAR.

**MaxDD provenance:** dispatch's −46.1% = the STANDALONE paper sleeve (converge_portfolio_backtest.py, §3,
simpler sim). The full production harness as-active-book = **−38.4%** (both active-book-ungated). DD is
dominated by **universe concentration** (16 candidates, double-confirm breadth mean 4 / max 9, 17% zero-name
days), NOT the missing gate.

**State-gate test (added opt-in `CONV_STATE_GATE=1`, default-OFF, L1712-1732):** active book obeys DT5G
ceiling — `tier_weights_by_state` caps new entries; `state_exit_map={1:1.0,2:0.8,3:0.3}` trims held positions
to CRISIS-flush/BEAR-80%/NEUTRAL-30%. Caveat (disclosed): trim also flushes the CAPIT crisis-buyer in
CRISIS/BEAR (sells the bottom-fisher when it's meant to buy).

| Config (50B, CAPIT ON, same parking, threads=1) | CAGR | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|
| Ungated active book (baseline) | **12.05%** | 0.85 | **−38.4%** | 0.31 |
| State-gated (`CONV_STATE_GATE=1`) FULL | **5.74%** | 0.66 | **−19.4%** | 0.30 |
| — IS 2014-19 | 6.14% | 0.76 | −13.1% | 0.47 |
| — OOS 2020-now | 5.38% | 0.58 | −19.4% | 0.28 |
| *(ref)* 2-book V2.4 R3 | 28.05% | 1.86 | −17.5% | 1.60 |

**VERDICT — state-gate is NOT the fix (keep default-OFF, nothing wired).** The gate halves MaxDD
(−38.4%→−19.4%, to production's ~−17.5% neighborhood) but more-than-halves CAGR (12.05%→5.74%): ~1:1
return-for-DD → **Calmar flat (0.31→0.30), Sharpe WORSE (0.85→0.66)**. No risk-adjusted gain — it just
scales the (already-losing-to-R3) book down. Root cause of the give-up: forcing de-risk on a
value/mean-reversion + CAPIT book in CRISIS/BEAR sells into washouts and misses the recovery (same lesson as
hold-neutral-exit / vol-managed-BAL: throttling a mean-reverting book by regime kills its convexity). The
deep MaxDD is a small-concentrated-universe artifact, not a missing state-gate — and adding the gate proves
it. ConvergePort stays a capacity-limited paper sleeve on idle cash (~10-15B ex-DHG), NOT a 2-book
replacement. Output: `converge_fullharness_test.py` (+`CONV_STATE_GATE`), `/tmp/conv_stategate.log`,
framework §8.

## ConvergePort — CAPACITY-APPROPRIATE STANDALONE-SLEEVE SIZE — 2026-07-06 (job Taylor_20260706_105156)
**Question:** not "replace 2-book production" (already REFUTED at 50B, see above) — instead, what NAV can
ConvergePort absorb as an *independent* sleeve before liquidity (not signal) binds?
**Method:** `converge_capacity_sweep.py` reuses the EXACT capacity formula from
`converge_fullharness_test.py` L2298-2318 (no new logic): `days_build = WPN(0.11)×NAV / (0.20×ADV60)`,
ADV60 = recent-120d median of `Volume_3M_P50×Price` (tav2_bq.ticker, data END 2026-07-05); flag
OK≤1 / WATCH 1-3 / BREACH>3 build-days. Universe = 16 available names (`sector_lens_monitor.NAMES`).
Light (liqdf-only pull, no simulate() engine).

**Per-name ADV60 & onset-NAV (WATCH=0.20·ADV/WPN, BREACH=0.60·ADV/WPN):**
DHG ADV **1.21B/day** → WATCH@**2.2B**, BREACH@**6.6B** (thinnest, ~9× below next name).
MSH 10.57B → WATCH@19.2B, BREACH@57.7B. CTR 32.4B → WATCH@59B. HAH/DBC ~66-67B → WATCH@~120B.
PVT 159B → WATCH@290B. VND/VCI/HCM/ACB/TCB/HDB/MBB/VCB/SSI/FPT all ≥200B ADV → WATCH ≥365B.

**Sweep (days_build, thin names; all others <0.9 at ≤50B):** DHG 1B→0.46, 3B→1.37(WATCH),
5B→2.28, 10B→4.56(BREACH), 50B→22.81. MSH 20B→1.04(WATCH), 50B→2.60. CTR 50B→0.85.
Flag by NAV: 1B all-OK · 3-5B DHG-WATCH · ≥10B DHG-BREACH · ≥20B +MSH-WATCH (matches prior
50B/100B run job 095725: DHG BREACH+MSH WATCH @50B; MSH BREACH+CTR WATCH @100B).

**Answers:** (3) Full-16-name sweet-spot (all OK) = **~2.2B** (DHG binds — it barely trades).
(4) Exclude DHG (buy-and-hold pharma anchor, low turnover → build-rate rule overstates it) →
next binding = MSH: all-OK to **~19B**, or **~57B** tolerating MSH/CTR in WATCH (= the refuted
large-scale regime). (5) **+5.0pp CAGR is SCALE-INVARIANT** — verified `converge_portfolio_backtest.py`
`sim_nav()` is a pure fractional-weight return sim (iterates `r_active+r_park−turnover·TC` on weights
summing to 1.0), carries NO NAV/ADV/capacity term (only 0.20 per-name *weight* cap). Edge holds at any
NAV inside the sweet spot; capacity only *erodes* it above, never creates it.

**VERDICT — recommended standalone-sleeve size: ~10-15B VND with DHG hard-excluded from active
rebalancing** (kept as buy-and-hold anchor sized outside the sleeve — same `excluded_tickers` pattern as
ZaloPay/DGC). Rationale: excluding one thin low-turnover name lifts the deployable ceiling ~9× (2B→~19B);
10-15B sits comfortably below MSH's 19.2B WATCH onset with margin for thin-name ADV drift, so no name is
even at WATCH and every 15-name build completes <1 session; the +5.0pp edge is fully intact. Aggressive:
≤19B (zero MSH-drift margin); 50B only if accepting the refuted large-scale WATCH regime — not
recommended. RESEARCH/PAPER-ONLY, production untouched; current equal-weight paper book unaffected.
Framework: `mike/agents/Taylor/converge_portfolio_framework.md` §6.

---

## ConvergePort — UNION (OR) alternative vs double-confirm (AND) — 2026-07-06 (job Taylor_20260706_114506)
**RESEARCH-ONLY, production untouched (custom30V/BAL/LAG/rating_8l.py + double-confirm paper book unchanged).**
**Question (user via Mike):** double-confirm (AlphaLens Group-A BUY **AND** 8L golden) is thin — mean
3.95 names, **17.3% of days 0 names**. Does switching **AND → OR (UNION)** fix "too few deals" WITHOUT
hurting risk-adj performance? Should the launched paper book switch to UNION?

**UNION definition (no new conditions invented, per dispatch):** member(t) = [name∈sector_lens Group-A
∧ status==BUY] **OR** [name∈rating_8l.py BUY-NOW list]. BUY-NOW = rating_8l.py's OWN pre-defined golden
screen (rating≤3 ∧ liq_bn≥3.0 ∧ pb_z≤−0.3 ∧ NOT ROE_Min3Y<0). *Not* the refuted "rating≤2 anything"
composite-as-selector. Enter when a name appears in UNION, exit when it leaves BOTH arms.
**Engine:** `converge_union_test.py` — same fractional paper-sim as the §3/backtest frame (baseline /
double-confirm / UNION in one identical engine; custom30V parking; DT5G-as-of gate; T+1; threads=1;
min(CAP,1/n) equal-weight, weights sum 1.0 → **scale-invariant** return sim, so NAV=20B only feeds the
ADV overlay, not the return). Self-check 0 VND: max|Σw−1|=2.2e-16 (UNION), 1.1e-16 (double-confirm).

**Breadth — UNION DOES fix "too few deals" completely:**
| book | mean-when-active | max | empty days |
|---|---|---|---|
| double-confirm (AND) | 3.95 | 9 | 515/2970 (**17.3%**) |
| BUY-NOW golden arm alone | 33.1 | 104 | 0 (0.0%) |
| **UNION (OR)** | **36.1** | **107** | **0 (0.0%)** |
Live 2026-06-26: UNION = **65 names** (universe 297 ever) vs double-confirm 9.

**Performance (FULL 2014-08→2026-06, TC=0.1%):**
| book | CAGR | Sharpe | MaxDD | Calmar | turnover |
|---|---|---|---|---|---|
| custom30V thuần (baseline) | 18.75% | 0.87 | −45.9% | 0.41 | ~0 |
| double-confirm (AND) | **23.86%** | **1.11** | −46.1% | **0.52** | 4.14×/yr |
| **UNION (OR)** | **12.07%** | **0.64** | **−55.9%** | **0.22** | **12.89×/yr** |
**Δ UNION vs baseline: −6.68pp CAGR / −0.23 Sharpe / −0.19 Calmar / MaxDD −10pp WORSE**, and −11.8pp
vs double-confirm. Worse in BOTH IS (6.71% vs 12.72% baseline) and OOS (16.76% vs 24.03%). UNION loses
even to *pure parking*. TC sensitivity: 12.07%→9.22% @0.3% (12.9×/yr churn bites hard).

**Why UNION fails (mechanistic):** (1) golden BUY-NOW arm is a broad 8L deep-value list that heavily
overlaps custom30V itself → UNION ≈ a *worse-built* custom30V (equal-weight vs yieldcombo cap-weight) +
churn; (2) equal-weighting 30-100 pb_z≤−0.3 dislocated names = max exposure to the cheapest/most-
distressed right as they fall → falling-knife DD −55.9%; (3) 3× turnover; (4) the double-confirm edge
WAS the AND-selectivity (two lenses agreeing = high conviction) — OR destroys exactly that.

**Capacity @20B — NOT the constraint (but moot):** 65 names × ~1.5% = 0.31B/name → 64/65 OK, only
DHG at WATCH (1.27 build-days), 0 BREACH. Easier than double-confirm, but irrelevant given perf fails.

**VERDICT — DO NOT switch to UNION; keep double-confirm.** UNION "solves" empty-days, but that problem
was never real: an empty double-confirm day = 100% custom30V parking = **automatic safety, not a defect**
(exactly Mike's framing, confirmed). Trading AND-selectivity for OR-breadth turns a high-conviction
concentrated sleeve into a churning broad-value book that loses to plain parking. Launched paper book
(double-confirm equal-weight) stays as-is. Artifacts: `converge_union_test.py`,
`data/converge_union_test_nav.csv`, `data/converge_union_test_summary.json`. Framework §7.

---

### 2026-07-06 · Real NSO CPI YoY fetched (chart-embed) + confidence-loss study re-run — job Taylor_20260706_105930
**RESEARCH/DISPLAY-ONLY, production untouched.** Prior job Taylor_20260706_100438 used a PROXY CPI
anchor series (clean machine-readable GSO CPI could not be fetched then). This job fetched REAL
headline CPI YoY from the NSO/GSO Highcharts **chart-embed** endpoint — no NLP/prose parsing:
`https://www.nso.gov.vn/chart/cpi/embed/?show=chart` (slug "cpi", post id 24238) returns the raw
Highcharts `series.data` array of `["M/YYYY", yoy_pct]` pairs. Method verified, fast, robust.
(TLS cert verify skipped for nso.gov.vn ONLY, per user scope — `curl -k`.)

**Data obtained (REAL, authoritative):** headline CPI YoY, 13 months **2025-06 → 2026-06**:
3.57, 3.19, 3.24, 3.38, 3.25, 3.58, 3.48, **2.53** (Jan-26 dip), 3.35, **4.65, 5.46, 5.60**, 4.69.
Also grabbed NSO "inflation" chart (average/bình-quân YoY, slug "inflation" id 24239), same window.

**HARD LIMIT — history caps at ~13 months.** The NSO CPI chart is a SINGLE evergreen post with a
ROLLING 13-month window (slides monthly); there are NO per-article historical charts (article pages
are prose-only; probing older chart slugs/ids all 404). Real chart data reaches back only to
2025-06. Older history (2011→2025-05) stays on the Tier-2 proxy anchors as documented fallback.
**Gold/USD**: NSO articles are titled "…chỉ số giá vàng và …đô la Mỹ" but publish NO chart for them
(prose only) — NOT fetchable by this method. Kept vnstock gold / macro USD/VND as before (skipped
per job instruction to not stall on this).

**cpi_vn.py updated**: `NSO_CPI_YOY_REAL` dict overlays real values onto the proxy for months present
(`is_real_nso` flag added); proxy retained as fallback. Docstring rewritten with source/method/date/
coverage/limitation. `NSO_CPI_YOY_AVG_REAL` kept for reference.

**What the real data corrected vs proxy:** proxy modeled a smooth 2026 rise (Jan proxy 4.5); real print
**DIPPED to 2.53 in Jan** then spiked LATER & sharper (Mar 4.65 → May 5.60 → Jun 4.69). Jan-2026 was a
LOW, not a step-up. `cpi_yoy_chg3` now shows the true acceleration burst (+2.93 at Apr-26).

**Confidence-loss regime study re-run (macro_confidence_regime.py) — CONCLUSION UNCHANGED.**
The real CPI only touches the recent tail (macro_features ends 2026-05; fwd60 undefined there), so the
strict all-4-binding regime (gold↑ ∧ USD↑ ∧ CPI>4 ∧ deposit↑) still reads the same:
REG_A_strict n=62 (1.6% days), **fwd60 −2.44% vs baseline +2.60%**, fwd60+% 40%, turnover 0.84× (thin),
vol 25.4% (high). Still a genuine risk-off signature. Real CPI cleaned the episode count to **3 distinct
episodes** (2018-05, 2022-12→23-02, and the live/incomplete 2026-04→05) — proxy interpolation had padded
extra in-between days. **Still too rare / incomplete-live to be tradeable → NOT wired** (same verdict as
job _100438). The 2026 spike is REAL and DOES arm the strict regime now, but its fwd60 outcome is not yet
observable (data edge). Frame saved `/tmp/macro_confidence_regime_frame.csv`.

---
## Bottom-recovery regime (symmetric opposite of confidence-loss) — job Taylor_20260706_111335 (2026-07-06, RESEARCH/DISPLAY-ONLY)
Script: `bottom_recovery_regime.py`. Scope: production untouched (DT5G/custom30V/BAL/LAG/rating_8l.py unchanged). Does NOT propose re-enabling the easing floor.

**User hypothesis:** after a high-rate period, when (1) rates ease + (2) real estate cold + (3) gold falls + (4) equities cheap vs own history → VNINDEX bottom/turn-up drawing capital back. Question: does the 4-way combo fire EARLIER / with LESS NOISE than the single "rates falling" signal (which EASING_FLOOR_ENABLED=False deemed untrustworthy alone)?

**Data:** BQ ticker_prune 2007+ (RE sector = ICB 8633/8637 dev+services, 42+ names; VNINDEX_PE off stock rows), SBV refi (2006+), Big-4 deposit proxy, gold world (2016-07+ only — hard limit).

**Result — hypothesis NOT supported as an early/tradeable bottom signal:**
- **flag3** (rates-easing ∧ RE-cold ∧ cheap, no gold, 2008+): fwd60 +16.2% / fwd120 +22.0% / fwd250 +26.5% (hit 95–100%) vs baseline 1.7/3.5/7.4% — eye-popping BUT only **2 episodes ever**: 2012-09..12 and 2023-04..05.
- **Fires LATE, not early:** 2012 episode fires **+248d** after the true price trough (2012-01, price already +15% off low); 2023 episode fires **+163d** after trough (2022-11, price already +14% off low). Missed all 4 classic bottoms (2009 GFC, 2012-01, 2020-03 COVID, 2022-11). It CONFIRMS a recovery already underway — it does not lead it. Directly refutes "fires earlier than rates-only."
- **Single-episode carry:** LOO — drop 2012 → fwd120 collapses to 2.3% (≈baseline); the entire fwd120 edge is one episode. Not distinguishable from luck (same trap as Wave1/H8a & confidence-loss job).
- **flag4 (+gold) NEVER fires** across 2016+ — gold rose during both easing recoveries (2023 banking stress), so the gold condition zeroes all overlap → the 4-way combo is non-operational on the only window where gold data exists.
- **rates-only** baseline: 1112 sessions, fwd250 +18.2% (hit 88%) — noisier per-episode but far more episodes → the combo does NOT reduce noise, it just adds a multi-month LAG and shrinks to 2 lucky clusters.
- **Live 2026-07-06:** flag3=FALSE (PE pctile 0.45 = not cheap; refi flat since 2023-06 + deposit flat = rates_easing FALSE). RE cold + gold falling only.

**Verdict:** REFUTED as an early bottom indicator; NOT wired, NOT recommended for DT5G. Reinforces the standing decision — DT5G price-based re-risk would catch these recoveries EARLIER than this flag (which lags price 5–8 months). No case to re-enable easing floor. Same shape as confidence-loss study: strict combo looks great but too few episodes (2) + single-episode carry = untradeable.

---
## NEUTRAL idle-cash waterfall + SOFT-threshold glide — job Taylor_20260706_125540 (2026-07-06, RESEARCH-ONLY)
User (via Mike) proposed (1) a WATERFALL for NEUTRAL idle cash: BAL/LAG full FIRST → **DC book
(ConvergePort)** → custom30V residual; unwind reverse (sell custom30V first when BAL/LAG re-fill).
Core Q: should DC be ranked BELOW BAL/LAG? (2) NEUTRAL as a SOFT threshold: glide cash 10-30%
(park 0.90-0.70) by how NEUTRAL is "leaning" bear/bull, vs the approved fixed 70/30 (`trading_rules.json`
v2.1 `neutral_parking`). Production untouched (custom30V/BAL/LAG/rating_8l.py/trading_rules.json unchanged).

### PART 1 — Waterfall priority: DC book BELOW BAL/LAG is CONFIRMED CORRECT (decisive, from bracketing backtests)
The ordering is pinned by two already-run full-harness backtests that bracket it:
- **DC given TOP priority** (ConvergePort REPLACES BAL+LAG, job _095725): FULL CAGR **12.05%** / Sharpe
  0.85 / MaxDD −38.4% / Calmar 0.31.
- **BAL/LAG kept on top, R3** (DC absent): FULL CAGR **28.05%** / Sharpe 1.87 / MaxDD −18.8% / Calmar 1.50.
- **DC as PARKING vehicle** (below BAL/LAG, idle-only; job _093329): **+5.0pp CAGR** vs custom30V parking
  (23.86 vs 18.75), DSR standalone 0.998.
⇒ Giving DC priority OVER BAL/LAG costs ~16pp CAGR and doubles DD; DC as the top of the *parking*
waterfall (below BAL/LAG, above custom30V) adds +5pp on the parked sleeve. **User's waterfall ordering
BAL/LAG → DC → custom30V is CORRECT — DC must rank BELOW BAL/LAG. Answer = YES, decisive.**
- **Net effect on full V2.4:** parked sleeve = **19.0% of NAV mean full-history, 30.9% on NEUTRAL days,
  max 69.2%** (measured from R3 audit DAILY `bal_etf_ref`+`lag_etf_ref`/`combined_nav`). Upgrading that
  sleeve custom30V→DC-first ≈ +5.1pp × ~19% ≈ **+0.9-1.0pp/yr on total NAV full-history**; for **SpaceX-NOW
  (BAL/LAG empty since ~04/2026, parked ~70%) ≈ +3.5pp** — the motivating scenario, where it matters most.
- **Honest caveat (unchanged from _093329):** the DC-over-custom30V EXCESS has **DSR=0.775 (<0.95)** —
  softer than the standalone book (shared equity beta). Ordering confirmed & direction positive, but the
  parking-upgrade is insurance-grade, not high-confidence alpha → keep on PAPER (launched 07-06, review
  2026-10-06) before any wire. **Reverse-unwind rule (sell custom30V before DC when BAL/LAG re-fill) is a
  sound corollary** of the ordering (unwind lowest-conviction/most-liquid sleeve first) — no separate
  backtest needed; execution detail (avoid DC↔BAL/custom30V wash-churn) for Mafee/DollarBill.

### PART 2 — SOFT-threshold glide: REFUTED as a risk-adjusted improvement (4 indicators, neg-control clean)
Script `neutral_glide_backtest.py`; output `data/neutral_glide_backtest_output.txt`. Testbed = the NEUTRAL
parking SLEEVE in isolation (deploy park_frac into custom30V on NEUTRAL days, cash else; T+1; TC 0.1%;
2014-08→2026-06, 2969 sessions, 1820 NEUTRAL). Self-check sleeve NAV identity OK (0-VND leak). NB the
~8-10% sleeve CAGR is NOT a strategy return — the sleeve is in CASH on the 1149 non-NEUTRAL days by design;
only the RELATIVE (glide vs fixed) comparison is meaningful.

| config | avgPark | FULL CAGR | Sharpe | MaxDD | Calmar | IS | OOS |
|---|---|---|---|---|---|---|---|
| fixed_70 (APPROVED baseline) | 0.700 | 7.90% | **0.83** | −15.1% | 0.52 | 8.99% | 6.99% |
| fixed_80 | 0.800 | 8.99% | **0.83** | −17.1% | 0.53 | 10.25% | 7.96% |
| fixed_90 | 0.900 | 10.07% | **0.83** | −19.1% | 0.53 | 11.49% | 8.91% |
| GLIDE breadth(%>MA200) | 0.793 | 8.63% | 0.82 | −17.1% | 0.50 | 9.49% | 7.93% |
| GLIDE breadth (exp-pct) | 0.780 | 8.79% | 0.84 | −17.4% | 0.50 | 9.73% | 8.01% |
| GLIDE VNI mom60 | 0.791 | 8.56% | 0.80 | −18.8% | 0.46 | 10.03% | 7.36% |
| GLIDE VNI MA200-dist | 0.791 | 8.98% | 0.84 | −16.5% | 0.54 | 10.25% | 7.93% |
| GLIDE VNI RSI | 0.795 | 8.78% | 0.83 | −17.5% | 0.50 | 9.97% | 7.81% |
| INV-GLIDE breadth (neg ctrl) | 0.807 | 9.05% | 0.81 | −17.3% | 0.52 | — | — |

**The decisive fact: Sharpe is FLAT at 0.83 across the ENTIRE fixed ladder (70→80→90).** Deploying more
idle cash into custom30V in NEUTRAL trades raw CAGR against DD **1:1 (pure beta)** — no free lunch. So any
glide overlay must lift Sharpe ABOVE 0.83 to add value. **None does:** best is MA200-distance (Sharpe 0.84,
Calmar 0.54 — **+0.01 over the ladder = multiple-testing noise** from 4 indicators × mapping variants);
momentum is actively WORSE (0.80/0.46); breadth/RSI ≈ ladder. The breadth glide's +0.74pp CAGR vs fixed_70
is **purely "deploy more on average"** (avg park 0.79) — at the SAME avg deployment it is −0.35pp vs fixed_80,
and the **negative control (park more when breadth LOW) is NOT beaten** (9.05% / 0.81) → breadth carries no
within-NEUTRAL timing edge. **Economic reason: DT5G already does the regime timing; conditional on NEUTRAL,
residual breadth/momentum/trend variation has no forward edge on the defensive custom30V basket.**

**VERDICT Part 2:** the soft threshold is a **disguised risk-dial, not a signal** — it raises return only by
raising average deployment, which the 2026-07-03 decision already settled (fixed **0.70 = risk-adjusted
optimum**; higher park = proportionally worse DD, flat Sharpe/Calmar). **Do NOT wire a breadth/momentum/RSI
glide.** If the user wants more deployment in benign NEUTRAL, that is the existing **`risk_dial_override`**
governance lever (raise fixed park with explicit sign-off), NOT an indicator-driven auto-glide. Keep NEUTRAL
parking at the fixed 0.70.

---
## DC-book waterfall DEEP-DIVE — bảng số đầy đủ + 3 câu mở rộng — job Taylor_20260706_173317 (2026-07-06, RESEARCH-ONLY)
Scripts: `dc_waterfall_deepdive.py` + `dc_waterfall_panel_build.py`; output `data/dc_waterfall_deepdive_output.txt`.
Production + paper sleeve ĐANG CHẠY untouched. **N trials khai báo: 10** (3 state-policy × 4 mix × 3 timing, trừ trùng).

**Phương pháp**: overlay-recomposition trên R3 full-harness DAILY audit (`data/h3_baseline_R3.csv`,
pt_v23_audit v23a, AUDIT_END=2026-06-19, identity 0 VND): `r_new = r_base + w_park(t-1)·(r_wf − r_c30v)`,
với r_wf/r_c30v = vehicle returns cùng framework (job _093329, TC 0.1%, T+1). Self-check 3 tầng PASS:
(A) metrics recompute == METRIC rows trong audit; (B) overlay identity r_wf:=r_c30v → max|Δ|=0.00e+00;
(C) parked>0 CHỈ trên NEUTRAL days, max w_park=0.699 (đúng PARK {3:0.7}). Parked sleeve = 24.1% NAV mean,
39.2% trên NEUTRAL days, max 69.9%.
⚠️ Baseline note: R3 tại data-snapshot này = 27.35%/1.81/−17.6/1.55 (pinned cũ 28.05 @Jun-20 snapshot —
chênh = data-drift adjusted-price, so RATIOS not levels, đúng META caveat). Mọi so sánh dưới đây cùng 1 snapshot.
✅ OPS FLAG RESOLVED (2026-07-06, job Taylor_20260706_174921): file canonical `v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap.csv`
đã bị 1 run khác GHI ĐÈ 2026-07-06 17:20 (CAGR 17.5%, w_lag_tgt trống, V2.3C static combination — không phải R3).
ĐÃ regenerate bằng lệnh pinned R3 (interpreter `$DNA_PYEXE`=wc_venv) → CAGR 27.39% / Sh 1.81 / DD −17.6% / Calmar
1.55, self-check 0 VND, khớp R3-range. File giờ đúng chuẩn R3. Chi tiết + convention chống tái diễn: xem R3 block
(§ REGENERATED note) và coding_guidelines §8.

### CÂU 0 — Bảng chuẩn: FULL V2.4 NAV @50B, baseline R3 vs WATERFALL (đúng paper config: DC ex-DHG, equal-weight cap 0.20, daily signal-driven, NEUTRAL-only)
| config | window | CAGR | Sharpe | Sortino | MaxDD | Calmar |
|---|---|---|---|---|---|---|
| R3 baseline (custom30V parking) | FULL | 27.35% | 1.81 | 1.78 | −17.6% | 1.55 |
| | IS 2014-19 | 26.75% | 1.81 | 1.88 | −13.3% | 2.01 |
| | OOS 2020+ | 27.94% | 1.81 | 1.70 | −17.6% | 1.58 |
| **WATERFALL paper cfg (ex-DHG)** | FULL | **27.54%** | **1.83** | 1.84 | **−15.5%** | **1.77** |
| | IS 2014-19 | 26.55% | 1.82 | 1.90 | −13.1% | 2.03 |
| | OOS 2020+ | 28.48% | 1.84 | 1.79 | −15.5% | 1.83 |
| (biến thể DHG-included, cross-check) | FULL | 27.68% | 1.85 | 1.85 | −15.5% | 1.79 |

**Đọc**: giá trị chính của waterfall ở full-NAV = **giảm MaxDD −17.6→−15.5 (+2.1pp) và Calmar 1.55→1.77**,
CAGR chỉ +0.19pp (IS −0.20pp / OOS +0.54pp — CAGR-edge mỏng và nghiêng OOS; riêng DD/Calmar cải thiện Ở CẢ
IS VÀ OOS). **DSR của excess full-NAV (N=10) = 0.111 << 0.95** — khớp kết luận cũ (sleeve-level DSR 0.775):
đây là INSURANCE-GRADE, không phải alpha — **giữ PAPER, không wire**, đúng quyết định event-anchored review.

### CÂU 1 — State coverage: NEUTRAL-only vs +BULL vs +EXBULL → GIỮ NEUTRAL-ONLY
Idle cash trong BULL KHÔNG nhỏ (materiality có thật): 406 ngày BULL, cash mean 30.1% NAV, p90 58.3%.
Nhưng: (b) NEUTRAL+BULL FULL 28.42% (+0.88pp) Sharpe FLAT 1.85, IS ÂM (−0.09pp);
(c) +EXBULL: +0.01pp, Sharpe GIẢM 1.85→1.84 → EXBULL vô giá trị.
**Per-year LOO (quyết định)**: toàn bộ edge +BULL = 2020 (+6.91pp) + 2021 (+9.20pp); 2018 −0.62 / 2024 −0.40 /
2025 −0.75 — 3 năm bull gần nhất đều ÂM. Drop 2020+2021 → tổng delta ÂM. Cùng chữ ký lumpy khiến bull-park
custom30V bị loại (R2<R3) và cùng bẫy reshuffle-luck Wave1/H8a. **VERDICT: KHÔNG mở rộng, NEUTRAL-only đúng.**

### CÂU 2 — Tỷ lệ DC/custom30V trong sleeve: WATERFALL THUẦN THẮNG TUYỆT ĐỐI, không đáng phức tạp hoá
| sleeve split | FULL CAGR | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|
| waterfall thuần (DC ăn hết cap) | 27.68% | 1.85 | −15.5% | 1.79 |
| fixed 70/30 | 27.46% | 1.83 | −15.5% | 1.77 |
| fixed 50/50 | 27.44% | 1.83 | −16.0% | 1.72 |
| fixed 30/70 | 27.44% | 1.82 | −16.7% | 1.65 |
Đơn điệu: càng ít DC càng kém CẢ CAGR lẫn DD (double-confirm chọn lọc hơn custom30V trung bình).
Fixed ratio thêm turnover-phối trộn mà không thêm giá trị. **Giữ waterfall thuần như đã wire.**

### CÂU 3 — Timing rebalance: hiện tại = DAILY signal-driven (xác nhận từ code `dc_book_waterfall_paper.advance()` — recompute target mỗi close); QUARTERLY đáng cân nhắc khi review
| timing | turnover | TC drag (sleeve) | FULL | IS | OOS | MaxDD | Calmar |
|---|---|---|---|---|---|---|---|
| daily signal-driven (paper) | 3.18x/yr | 0.32pp/yr | 27.54% | 26.55% | 28.48% | −15.5% | 1.77 |
| quarterly q2m5-style | 0.76x/yr | 0.08pp/yr | 27.56% | 26.99% | 28.12% | −15.1% | 1.83 |
Event-driven ≡ daily trong frame target-weight (equal-weight không drift-model — không đo tách được ở đây).
Quarterly: turnover ÷4, TC drag −0.24pp/yr, metrics ngang-đến-tốt-hơn (IS +0.44pp, Calmar 1.83 vs 1.77), đổi lại
phản ứng chậm hơn khi 1 tên rớt double-confirm giữa quý. **KHÔNG đổi paper sleeve đang chạy** (per ràng buộc
dispatch); đề xuất đưa "quarterly refresh" vào agenda mốc review event-anchored làm refinement duy nhất đáng thử.

---

## DC-waterfall tinh chỉnh 3 nhánh — overlap cap / liquidity floor / lịch rebal theo thống kê BCTC (2026-07-07, job Taylor_20260707_042827)

**Scope**: RESEARCH-ONLY (paper sleeve + production untouched — input cho mốc review event-anchored).
**Method**: overlay recomposition trên R3 audit (`data/h3_baseline_R3.csv`, self-check 0 VND identity),
panel cache job _173317 (`dc_dbl_panel.csv` 00:42 2026-07-07). **N trials khai báo = 13** (5 timing + 4 overlap
+ 4 floor). threads=1. Scripts: `dc_release_date_stats.py`, `dc_rebal_timing_backtest.py`,
`dc_overlap_cap_backtest.py`, `dc_liquidity_floor_backtest.py`.
**Cache-consistency note (quan trọng cho mọi so sánh tương lai)**: file `converge_portfolio_backtest_nav.csv`
(build 16:41 06/07, TRƯỚC sync BQ 23:45) lệch với rebuild cùng công thức trên cache 07/07 ở 227 ngày (max 8.3e-03
daily — adjusted-Close revision toàn lịch sử). Mọi số dưới đây là SINGLE-CACHE (07/07): r_c30v, panel, vehicle
cùng snapshot. Máy per-name tái lập park_ret đúng 2.8e-17 (self-check A).

### NHÁNH C — Thống kê Release_Date thật (2014-2025, prune 508 tên, 20.575 báo cáo) → q2m5 GẦN TỐI ƯU
Phân phối lag nộp (ngày lịch sau quarter-end) CỰC DỒN quanh deadline pháp lý ~30d:
| mốc | Q1-Q3 đã nộp | Q4 đã nộp |
|---|---|---|
| lag 30d | 48.2% | 54.1% |
| lag 33d | 85.2% | 90.6% |
| **lag 36d (≈q2m5)** | **98.9%** | **96.2%** |
| lag 40d | 99.0% | 99.5% |
- p50/p80/p90/p95 = 31/33/34/34d (Q1-Q3); Q4 KHÔNG muộn hơn (30/33/33/34d) — `Release_Date` trong
  `ticker_financial` là báo cáo QUÝ (chưa audit), giả thuyết "Q4 audited muộn" không áp vào bảng này.
- Ổn định theo năm: p80 dao động 31-35d (2014-15 muộn nhất 34-35d, gần đây 31-32d) → mốc 36d robust mọi năm.
- **Bias nộp muộn = KHÔNG XẤU, hơi ngược**: nhóm nộp sau p80 có NP-YoY median +11.2% vs +6.6% nhóm sớm,
  %NP-giảm-YoY 39.8% vs 42.4%, %lỗ ngang nhau → không có adverse-selection penalty khi rebalance sớm.
- WL16/c30v members: ~10% báo cáo nộp sau 33d (2020-25) — không phải đuôi bỏ qua được.
**Backtest timing DC-refresh (full-NAV)**: daily 27.56%/Calmar 1.77; q2m5 27.60%/1.84; lag40 27.62%/1.85;
lag33 27.77%/1.84; lag30 27.73%/1.85. Cả dải 30-40d nằm trong ±0.2pp, per-year delta đổi dấu liên tục
(2019 +2.4→+3.5pp là sampling-luck 1 năm) → KHÔNG có edge "tươi sớm" thật giữa các mốc.
**VERDICT C**: mốc kinh nghiệm q2m5 của user ĐƯỢC THỐNG KÊ XÁC NHẬN gần tối ưu (98.9% coverage, chỉ 2-3 ngày
sau cụm deadline; sớm hơn không thêm gì, muộn hơn không cần). **Đề xuất: 1 LỊCH THỐNG NHẤT q2m5 cho CẢ DC book
VÀ custom30V** (mã trùng net-out cùng ngày, giảm wash-churn) — khớp đề xuất "quarterly refresh" CÂU 3 job trước.

### NHÁNH A — Mã trùng DC ∩ custom30V trong sleeve: CAP GỘP 0.15 = risk-control gần miễn phí
Control (hiện tại, cộng dồn tự do): max eff-name-weight sleeve 28.7% (p99 28.4%!), = **20.1% NAV khi sleeve
~70% NAV** — xuyên trần name_cap 10% NAV; 30.6% số ngày có tên >20% sleeve.
| variant (full-NAV overlay) | FULL | IS | OOS | MaxDD | Calmar | max name @70%NAV | extraTC sleeve |
|---|---|---|---|---|---|---|---|
| (iii) control cộng dồn tự do | 27.57% | 26.56% | 28.53% | −15.5% | 1.77 | 20.1% NAV | 0 |
| (ii) dedupe DC-loại-khỏi-c30V | 27.47% | 26.39% | 28.51% | −15.5% | 1.77 | 14.0% NAV | 0.04pp/yr |
| (i) cap gộp X=0.20 | 27.53% | 26.49% | 28.52% | −15.5% | 1.77 | 14.0% NAV | 0.04pp/yr |
| **(i) cap gộp X=0.15** | **27.46%** | 26.56% | 28.32% | **−15.3%** | **1.79** | **10.5% NAV** | 0.17pp/yr |
Chi phí kiểm soát rủi ro concentration: −0.04 đến −0.11pp CAGR FULL — trong noise; X=0.15 duy nhất đưa
exposure về đúng tinh thần trần 10% NAV (10.5%) và MaxDD/Calmar tốt nhất nhóm.
**VERDICT A**: đề xuất **cap gộp X=0.15** khi wire (nếu qua review); dedupe = phương án nhì (đơn giản hơn,
14% NAV). Control giữ nguyên cho paper đang chạy (per ràng buộc), nhưng con số 20.1% NAV/name là finding
phải xử lý trước bất kỳ wire live nào.

### NHÁNH B — Floor thanh khoản Trading_Value_1M_P50 ≥ 3B: KHÔNG phải no-op, là robustness CÓ LÃI nhẹ
Kỳ vọng ban đầu ("8 mã hiện tại không đổi, chỉ DHG rớt") SAI một nửa — floor cắt cả lịch sử:
- Floor 3B loại 15.0% name-days double-confirm: DHG 873/1075, **HAH 376/1296 (2016-19)**, **MSH 210/710
  (2020-23)**, VCI 2/12. Floor 5B loại 18.1% (thêm MSH 374/710, VCI 12/12, CTR 12/426) — cắt vào signal thật.
- Floor KHÔNG thay được hoàn toàn hard-exclude DHG: 3B vẫn cho DHG qua 202 ngày, 5B qua 78 ngày.
- Set hiện tại (2026-07-06, 9 tên double-confirm): floor 3B loại đúng DHG (TV 0.4B), giữ 8 tên live (19-447B).
| config (full-NAV) | FULL | IS | OOS | MaxDD | Calmar |
|---|---|---|---|---|---|
| paper (hard-exclude DHG, no floor) | 27.56% | 26.55% | 28.54% | −15.5% | 1.77 |
| **floor 3B (DHG cho lại vào)** | **27.68%** | 26.64% | **28.69%** | **−14.9%** | **1.86** |
| floor 5B | 27.54% | 26.89% | 28.17% | −15.0% | 1.84 |
| floor 3B + DHG vẫn hard-exclude (diag) | 27.67% | 26.59% | 28.70% | −15.0% | 1.85 |
Diagnostic chốt: gain của floor 3B đến từ LOẠI NGÀY KÉM THANH KHOẢN của HAH/MSH thời xưa, KHÔNG phải từ DHG
(3B-có-DHG ≈ 3B-không-DHG). Cải thiện Ở CẢ IS VÀ OOS, nhưng +0.12pp là nhỏ — frame là ROBUSTNESS (loại đúng
những name-day không trade nổi ở size thật), không phải alpha.
**VERDICT B**: đề xuất **floor 3B** vào membership DC khi wire; 5B quá chặt (cắt MSH nửa lịch sử). DHG: floor
3B đủ thay hard-exclude về mặt số (delta ≈0), chọn floor-only cho sạch cơ chế; hard-exclude giữ như double-safety
nếu muốn (không tốn gì).

**Tổng kết đề xuất cho mốc review event-anchored** (không đổi gì trước đó): (1) refresh q2m5 thống nhất
DC+custom30V; (2) cap gộp per-name 0.15 sleeve; (3) floor thanh khoản 3B. Cả 3 = risk-control/robustness với
chi phí CAGR ≈ 0 — nhất quán verdict DSR 0.775/0.111: sleeve là insurance, không phải alpha-engine.

## 2026-07-09 — NEUTRAL park sweep tại NAV nhỏ 20B vs 50B (premise check "NAV nhỏ → đẩy park 70→90 an toàn hơn") — job Taylor_20260709_012737 (kế thừa artifact Taylor_20260708_170202)
**Câu hỏi (user qua Mike):** NAV ~20B có nên đẩy NEUTRAL parking 70% → 90%?
**Cách chạy:** grid contemporaneous 8 run cùng ngày (tránh batch drift −1.2pp đã biết): {NAV_TOTAL_B=20,50} × PARK∈{0.70,0.80,0.90,0.94}, `$DNA_PYEXE pt_v23_audit_2014.py`, threads=1, self-check 0 VND **16/16 pass** (BAL+LAG × 8), borrow cost 0. Logs: `data/run_park_sweep_nav{20,50}_p{70,80,90,94}*.log`. CSVs: `..._nav20B.csv` (suffix mới NAV_TOTAL_B) + `park3-XX` tags; 50B p70 anchor: `data/park70_50B_anchor_20260709.csv`. Recompute độc lập từ CSV (extract-style, FULL/IS/OOS) khớp log ≤0.01. **N trials = 8** (1 họ sweep, quyết định = giữ nguyên status quo, không wire gì → không cần DSR mới).

| NAV | park | FULL CAGR | Sharpe | MaxDD | Calmar | IS CAGR/Sh | OOS CAGR/Sh |
|---|---|---|---|---|---|---|---|
| 20B | 0.70 | 28.93% | 1.84 | −17.9% | 1.62 | 29.38/1.94 | 28.44/1.76 |
| 20B | 0.80 | 29.56% | 1.81 | −19.0% | 1.55 | 29.75/1.85 | 29.32/1.77 |
| 20B | 0.90 | 29.49% | 1.73 | −19.9% | 1.48 | 30.19/1.76 | 28.77/1.69 |
| 20B | 0.94 | 30.03% | 1.73 | −20.4% | 1.47 | 30.18/1.72 | 29.82/1.73 |
| 50B | 0.70 | 26.75% | 1.76 | −17.7% | 1.51 | 26.74/1.80 | 26.70/1.71 |
| 50B | 0.80 | 27.10% | 1.70 | −18.9% | 1.43 | 26.05/1.66 | 28.04/1.73 |
| 50B | 0.90 | 28.01% | 1.67 | −19.6% | 1.43 | 26.35/1.58 | 29.52/1.75 |
| 50B | 0.94 | 28.89% | 1.69 | −19.6% | 1.48 | 27.86/1.61 | 29.80/1.77 |

**Slope risk-cost 70→90:** 20B = **+0.56pp CAGR / −0.12 Sharpe / −0.14 Calmar / −2.0pp DD**; 50B = +1.26pp / −0.09 / −0.08 / −1.9pp. OOS còn rõ hơn: 20B chỉ +0.33pp CAGR với Sharpe −0.07; 50B +2.82pp với Sharpe +0.04.
**Capacity phase-1:** ADV-cap 20%ADV enforce nhưng KHÔNG bind ở cả 2 NAV — 15/15 state-flip unwind xong trong 1 phiên. Kênh capacity không phân biệt 20B vs 50B.
**VERDICT: premise REFUTED (đảo ngược).** Ở NAV nhỏ, tăng park mua ÍT CAGR hơn và trả NHIỀU risk hơn so với 50B — vì 2 book lõi ở 20B đã chạy giàu hơn (28.9% vs 26.8% baseline), phần park thêm chỉ cộng DD. **GIỮ park=0.70 ở mọi NAV hiện hành. Không đổi production/paper.** Nhất quán reference 50B cũ (70→94→100: Sharpe 1.78→1.66→1.65, job _130720; batch này 1.76→1.69, drift ~0.02 đã biết).
**Ghi chú canonical (§8):** run anchor 50B p70 (đúng config pin R3, đúng $DNA_PYEXE) đã regenerate `..._etfliqcustompitg_wtnamecap.csv` as-of 2026-07-09 (drift −1.30pp vs pin 28.05% — đúng cỡ batch/as-of drift đã ghi nhận trong registry). Nội dung cũ (park94 từ job _130720) backup tại `data/park94_50B_job130720_backup.csv`.

## 2026-07-09 — Audit fill thật SpaceX+ZaloPay từ go-live vs fill-timing edge (user nghi "mua xong lỗ ngay trong phiên") — job Taylor_20260709_101602
**Nguồn:** broker raw `dnse_raw_2026-07-0*.jsonl` (final state per order-id, KHÔNG dùng journal-only vì 07-02 double-buy) × OHLC `data/bq_cache/ticker/2026.parquet`. 92 order khớp (59 BUY, 33 SELL); 58 BUY có OHLC (07-09 chưa sync), tổng mua 1.472B VND.
**BUY value-weighted:** vsOpen **+3.4bps** (cơ chế khớp sạch — mua sát giá arrival, chase thấp); vsClose **+41.7bps** (≈ −6.5M MTM cuối phiên); vsLow +110.5bps; range-position 68%. **Per-day vsClose: 07-01 −21.0 / 07-02 +76.7 / 07-07 −32.6 / 07-08 −6.7** → toàn bộ tổn thất = 1 ngày 07-02 (deploy 915.6M lúc 09:15, bank fade cả phiên, ≈ −7.0M); 3/4 ngày mua CÓ LÃI tại close. Day-level mean +4.1bps, sd 49.6, n=4, **t=0.17** = nhiễu thuần. Power: noise 110-220bps cần **~156-625 buy-days** cho t=2 → live/paper KHÔNG BAO GIỜ tự chứng minh edge 17.6bps trong vài tuần; edge đứng trên backtest lịch sử (t=12.0) như thiết kế gate 30-06 (mechanics-gate, không phải edge-gate).
**SELL (07-06 trim):** vsOpen −26.6bps VW, vsClose +105.4bps VW (bán sáng/13:00 trên ngày fade = tốt) — hướng khớp research SELL-at-open.
**Bug đo lường tìm thấy + đã sửa:** `execution_quality_review.py` đếm cả journal LIVE, mà live-gate ép mult=1.0 → nhãn `ft:in-window` VÔ NGHĨA trên mọi lệnh live 09:15 → "98% adherence/410 placements" là GIẢ. Sau filter paper-only (exec_main_*): **6 placements / 1 phiên / 0 fill trong cửa sổ sáng 10:45-11:15** — cơ chế delay-BUY-sáng CHƯA TỪNG chạy thật lần nào (6 lệnh paper 07-07 đặt 14:19 = nhánh chiều mult=1.0 by design; main 07-08/09 không có lệnh). Evidence-rate ≈ 0 → checkpoint cuối-07 sẽ rỗng nếu không sửa lịch paper main chạy phiên sáng có BUY.
**VERDICT:** cảm nhận user ĐÚNG về giá trị (−41.7bps VW) nhưng nguyên nhân = trôi thị trường 1 ngày 07-02, KHÔNG phải lỗi cơ chế khớp (vsOpen +3.4bps). KHÔNG đẩy nhanh flip toàn bộ (chi phí chờ hiện tại ~176k VND/100M mua, buy-volume đang nhỏ; ngày đắt thật là deploy lớn kế tiếp = LAG refill cuối 07 → checkpoint cuối-07 vẫn đúng thời điểm, flip TRƯỚC deploy đó nếu mechanics sạch). Điều kiện flip (mechanics): ≥5 phiên paper có BUY fill trong cửa sổ sáng + 0 reject + không lệnh treo bất thường → quant-skeptic → user sign-off. Option trung gian nếu user muốn sớm: pilot flip CHỈ ZaloPay (cash-only, lệnh nhỏ) trước SpaceX. Quyết định ở user.

## 2026-07-11 — F3 audit money-path: SIGNAL_V11 đọc bảng base thay vì dt5g_live trong pt_v4/pt_v22 — đo tác động, verdict C (cần user quyết) — job Taylor_20260711_051033
**Bối cảnh:** audit `Taylor_20260711_031821` phát hiện `signal_v11_sql.py` forward-fill `state5` từ `tav2_bq.vnindex_5state` (v3.4b BASE) — `golive_recommend_v23.py:77` (LIVE) đã patch `.replace(...)` sang `dt5g_live`, nhưng `pt_v4_dt5g.py`/`pt_v22_dt5g.py` (sổ tín hiệu production) VÀ `pt_v23_audit_2014.py` (baseline R3 pin 28.05%) dùng SIGNAL_V11 thô = base. Docstring golive nói "SAME logic as pt_v22" — không còn đúng.
**Đo (script `data/f3_exp/f3_signal_diff.py`, DuckDB cache, 2014-01-01→2026-07-10, 713.056 signal rows mỗi bên, merge 100% both):**
- State-diff base vs dt5g_live: 1.085/3.121 phiên (34,8%); bucket-diff (play_type-relevant {1,2}/{3}/{4,5}): **882 phiên (28,3%)**, 72 run, mean 12,2 phiên/run. Ma trận bucket: 12→3: 360d, 45→3: 212d, 3→12: 135d, 45←3: 79d, 12→45: 96d.
- play_type flips: 134.166 rows (18,8%) — đa số AVOID_bear↔PASS/WAIT (không actionable). **BUY-relevant: 13.068 rows = ~37% khối lượng BUY-signal** (base 34.776 vs dt5g 33.645 BUY rows, net −3,3%), trải 812/3.122 ngày, mọi năm 2014-2026 (đỉnh 2021: 3.547, 2025: 2.913). → play_type = CHÍNH entry gate BAL book, tác động MATERIAL, không phải phần phụ.
- **Live-era 06-11→nay: 131 BUY rows chỉ tồn tại dưới base, 0 chiều ngược** — toàn DEEP_VALUE_RECOVERY/MOMENTUM_A (tier BULL-only) từ cửa sổ BULL GIẢ 06-29→07-09 (bug EW-leg, base commit BULL(4), dt5g giữ NEUTRAL(3)). Sổ pt_v22 ĐÃ vào PVD/TVN/VCG/TLD/TPB/ASP theo tín hiệu giả; **TVN+TPB (DEEP_VALUE_RECOVERY, ~5,4B paper) đang là open positions**. Đã verify plan SpaceX 07-01→07-13: KHÔNG lệnh live nào từ nhóm này (plan hiện chỉ trade parking sleeve; DollarBill đọc golive recs dt5g-gated) → **lệnh live sạch, nhưng mệnh đề "live không bị ảnh hưởng bởi bug EW-leg" cần đính chính: sổ tín hiệu production đã hành động theo BULL giả 9 phiên**. pt_v22 chạm money-path gián tiếp: w_LAG band-trigger (golive đọc logs pt_v22), bối cảnh plan DollarBill, EOD paper report, V23Strategy mirror (chưa wire cron).
- Tự lành: tracker replay FULL từ START_DATE mỗi run (CSV = output thuần) → sau cron publish base-fix thứ Hai 07-13 18:30, fake entries tự biến mất khỏi sổ (cần verify sau publish). Fix F3 giải quyết lệch CẤU TRÚC 28,3% ngày, không chỉ episode này.
**VERDICT: C — không tự fix, cần user quyết.** Lý do: đây là lựa chọn "giữ nhất quán với AI": fix pt_v4/pt_v22→dt5g_live (1 dòng .replace như golive:77) = khớp LIVE nhưng lệch baseline R3 pin; giữ nguyên = khớp baseline nhưng sổ tín hiệu tiếp tục lệch live 28,3% ngày (đã có bằng chứng hại thật). **Khuyến nghị A cho tracker** + follow-up re-pin baseline (rerun pt_v23_audit 50B với dt5g swap, so 28.05%, quant-skeptic, user duyệt re-pin registry) — vì baseline hiện cũng KHÔNG mô tả config live (golive đã dt5g từ trước), lệch baseline-vs-live tồn tại sẵn, fix tracker không tạo lệch mới mà chỉ dời nó về đúng chỗ. Chưa làm NAV-level sandbox rerun (nguy cơ đè log production §8 + timeout); nếu user chọn A: copy tracker vào sandbox, redirect output, rerun 06-11→nay trước/sau, rồi mới sửa file thật.
**Artifacts:** `data/f3_exp/f3_signal_diff.py` + `.log` + `f3_playtype_flips.csv` (134k rows). Không đổi production/paper/registry-pin nào.

## 2026-07-11 — RE-PIN BASELINE R3 (DT5G swap trong SIGNAL_V11) — user duyệt, job Taylor_20260711_070437 (nối trace Taylor_20260711_064350)
**Việc:** hoàn tất chuỗi F3 — `pt_v23_audit_2014.py:524` (baseline R3) là consumer cuối cùng còn đọc play_type/state5 từ bảng base `tav2_bq.vnindex_5state` (v3.4b) qua SIGNAL_V11 thô. Apply đúng 1 dòng `.replace("tav2_bq.vnindex_5state AS s", STATE_TABLE + " AS s")` — mirror `golive_recommend_v23.py:77` và commit `0537514` (pt_v4/pt_v22). Baseline giờ mô tả ĐÚNG config live (golive đã dt5g từ trước).
**Lệnh regenerate (ĐÚNG lệnh pin, đúng `$DNA_PYEXE`):** `BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" AUDIT_END=2026-06-19 $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge` → CSV canonical `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap.csv` (log `data/run_r3_repin_dt5g_20260711.log`).

| R3 @50B NEUTRAL-only | CAGR | Sharpe | MaxDD | Calmar | Final NAV |
|---|---|---|---|---|---|
| Pin cũ (snapshot 06-19, re-pin 06-25, base-table play_type) | 28.05% | 1.86 | −17.5% | 1.60 | — |
| Base-table đương thời (probe cùng ngày 07-11, cùng cache) | 27.44% | 1.81 | −17.6% | 1.56 | 1.025,68B |
| **PIN MỚI (DT5G play_type, snapshot 07-11)** | **28.82%** | **1.90** | **−15.7%** | **1.83** | 1.172,70B |

**Phân rã +0.77pp (28.05→28.82):** data-drift as-of (06-25→07-11 cache) = **−0.61pp** (28.05→27.44, cùng cỡ drift −1.30pp đã ghi 07-09) + **hiệu ứng dt5g thuần = +1.38pp** (27.44→28.82, A/B cùng ngày cùng cache, chỉ khác 1 biến = bảng state trong SIGNAL_V11). Hiệu ứng dt5g cải thiện ĐỒNG LOẠT risk-adjusted: Sharpe +0.09, MaxDD +1.9pp nông hơn, Calmar +0.27. Driver lớn nhất: 2025 (base whipsaw EX-BULL → EXBULL-suppress chặn momentum; dt5g giữ BULL/NEUTRAL → +35.64%→+54.78%); đổi lại 2018 35.45→31.36, 2019 16.59→13.10 (dt5g de-risk chậm hơn vào bear) — net dương rõ.
**Verify (§8 đủ 3 bước):** (1) self-check **0 VND** BAL+LAG (cash-flow + final NAV identity), borrow 0, max gross 1.000; (2) recompute độc lập `$DNA_PYEXE extract_peryear.py <CSV>` → **FULL 28.82%** khớp chính xác print (IS 25.86% / OOS 31.59% — OOS > IS, cấu trúc walk-forward giữ nguyên); (3) probe đối chứng cũng self-check 0 VND (`data/f3_exp/pt_v23_basetable_probe_20260711.py` + log + CSV `data/f3_exp/v23_basetable_probe_20260711.csv` — §8 experiment name, không đụng canonical).
**DSR/PBO annex re-run trên pin mới (`dsr_pbo_annex.py`, log `data/run_dsr_pbo_annex_repin_20260711.log` — chạy lại lần 2 cùng ngày để verify, khớp chính xác):** DSR = **1.0000** @ mọi N (80 CSV/120/200), ann-SR (convention annex, daily combined_nav) 1.829; **PBO = 0.209** (~y hệt 0.20 cũ); bootstrap circular-block L=21: CAGR 5th-pct **20.1%** (cũ 18.6%), MaxDD 5th-pct **−26.1%** (anchor cũ ~−29%). Robustness KHÔNG suy giảm. N trials: +1 (swap này không phải tuning — là data-source correctness fix, không chọn từ họ config).
**Backup/revert:** CSV canonical cũ (nội dung 07-09 anchor) tại `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_pre_dt5g_repin_20260711_backup.csv`; revert code = bỏ 1 dòng `.replace` tại `pt_v23_audit_2014.py:524-527`.
**⭐ Số tham chiếu chính thức V2.4/R3 từ 2026-07-11: CAGR 28.82% / Sharpe 1.90 / MaxDD −15.7% / Calmar 1.83.** Mọi so sánh trước/sau ngày này phải nói rõ đang so với pin nào.

## 2026-07-11 — VALIDATE fa_ratings_8l MIGRATION (backtest song song, KHÔNG wire) — job Taylor_20260711_094714 — VERDICT: **KHÔNG MIGRATE as-is**
**Việc:** user duyệt hướng (B) — backtest song song trước khi quyết đổi nguồn `fa_tier` của SIGNAL_V11/pt_v22/pt_v23 từ `tav2_bq.fa_ratings` (STATIC, đóng băng 2026-05-10) sang `tav2_bq.fa_ratings_8l` (as-of PIT, refresh tay 06-20). Đo trước đó: chỉ 34% trùng tier / 80% lệch ≤1 bậc trên 659 mã chung → đây là ĐỔI SIGNAL. Kết quả đo: **đổi làm hệ KÉM ĐI toàn diện, đặc biệt OOS** → giữ nguyên `fa_ratings`.
**Setup (đúng §8, không đụng canonical):** probe copy `data/fa8l_exp/pt_v23_fatier8l_probe_20260711.py` = `pt_v23_audit_2014.py` + đúng 2 swap SQL (`fa_dated` trong SIGNAL_V11 + D1 CTE: `tav2_bq.fa_ratings` → `tav2_bq.fa_ratings_8l`) + AUDIT_PATH override ra `data/fa8l_exp/`. Lệnh = ĐÚNG lệnh pin R3 (`BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" AUDIT_END=2026-06-19 $DNA_PYEXE ... v23a none postbull 0 edge`). 2 mapping thử: **tier8l** = cột `tier` có sẵn của bảng 8l (panel A–E built-for-purpose: compounder = per-quarter percentile core_score, nhóm nhỏ = 1→A..5→E, rating 5 ép E, forensic override E — phân phối ~trùng legacy) và **rating8l** = map thô rating 1→A..5→E.
**Reproducibility:** control legacy chạy lại → **byte-identical CSV canonical** (28.82/1.90/−15.7/1.83); run tier8l được chạy ĐỘC LẬP 2 lần (2 process khác nhau cùng ngày) → **byte-identical nhau** (3.278.611 bytes). Self-check **0 VND** (BAL+LAG cash-flow + final-NAV identity) cả 4 run, borrow 0, max gross 1.000, threads=1.

| Config @50B (A/B đương thời, cùng cache 07-11) | FULL CAGR | Sh(252) | MaxDD | Calmar | IS 2014-19 CAGR | OOS 2020+ CAGR | OOS Calmar |
|---|---|---|---|---|---|---|---|
| **legacy control (= PIN R3)** | **28.82%** | 1.90 | **−15.7%** | **1.83** | 25.86% | **31.59%** | 2.01 |
| tier8l (đề xuất migrate chính) | 27.15% | 1.80 | −17.7% | 1.53 | 26.18% | 28.04% | 1.59 |
| rating8l (map thô) | 27.85% | 1.83 | −17.7% | 1.57 | 26.18% | 29.39% | 1.66 |

**Chữ ký xấu nhất — degradation DỒN VÀO OOS:** IS hai biến thể 8l đều NHỈNH hơn (+0.32pp) nhưng OOS tier8l **−3.55pp** (31.59→28.04), rating8l −2.20pp, MaxDD sâu thêm 2.0pp (đều rơi vào OOS). Per-year delta (tier8l vs control): 2020 **−12.1pp**, 2025 **−12.2pp**, 2026 −4.3pp; bù lại 2015 +3.9/2017 +5.4/2021 +5.0/2024 +3.7. **Per-year LOO (log `data/fa8l_exp/compare_out_20260711.log`): edge tier8l ÂM sau khi bỏ BẤT KỲ năm nào** (min −1.96pp, max −0.54pp) → suy giảm là BROAD, không phải 1-2 năm xui; rating8l chỉ dương (+0.06pp, ~0) khi bỏ đúng 2025. DSR cả 3 =1.0000 (không phân biệt được ở mức Sharpe này — KHÔNG dùng làm lý do); PBO family+2 trials = 0.238 (ổn); bootstrap L=21: 5th-pct CAGR 20.1%→18.3/18.8%, MaxDD 5th −26.1%→−28.2/−28.6%, P(DD<−30%) 1.5%→2.9/3.1% — **tail risk xấu đi rõ**.
**Đọc kết quả:** SIGNAL_V11 bucket logic (C/D momentum, A/B compounder, E avoid, banking ±10 theo tier) được tune trên phân phối/semantics của legacy `fa_ratings`; swap nguồn tier là đổi signal và số đo xác nhận drop-in thay thế làm hệ kém đi (~900 mã trước NULL nay có tier + 66% mã đổi bucket → hành vi BUY đổi material, và đổi theo hướng XẤU ở OOS).
**KHUYẾN NGHỊ (căn cứ số đo, chờ user + quant-skeptic):** (1) **KHÔNG migrate drop-in.** Giữ `fa_ratings` làm nguồn `fa_tier` production. (2) Deadline thật vẫn còn nguyên: `fa_ratings` đóng băng 2026-05-10, đủ phủ mùa Q1/2026, thành SAI DẦN khi BCTC Q2/2026 về (~cuối 07) — cần quyết hướng xử lý TRƯỚC đầu tháng 8 (lựa chọn: giữ static thêm 1 mùa chấp nhận tier cũ dần / hybrid NULL-fallback / re-tune bucket SIGNAL_V11 trên 8L như một dự án signal riêng có validation đầy đủ). (3) Nếu chọn re-tune: phải khai báo N trials + DSR/PBO như mọi thay đổi signal.
**Files:** toàn bộ trong `data/fa8l_exp/` (probe script, 4 CSV experiment, 4 log run, `fa8l_compare_20260711.py` + `compare_out_20260711.log`). Canonical KHÔNG bị ghi đè (verify mtime 14:15 + cmp byte-identical control copy).

## 2026-07-11 — PHASE 2 fa8l RE-TUNE: full-harness validation 3 finalist — job Taylor_20260711_133127 — VERDICT: **CP2 NO-GO CẢ 3 (F1/F6/F12)**
**Việc:** Phase 2 của dự án re-tune SIGNAL_V11 trên `fa_ratings_8l` (plan `mike/agents/Taylor/plan_fa8l_retune_20260711.md`, CP1 PASS 12/12 proxy). Full-harness `pt_v23_audit` 50B ĐÚNG lệnh pin R3 (`BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" AUDIT_END=2026-06-19 $DNA_PYEXE data/fa8l_exp/pt_v23_fa8l_phase2_20260711.py v23a none postbull 0 edge`, env `FA8L_CFG/FA8L_COV/FA8L_RUN`). 9 run (3 finalist × {full_r1, full_r2, legfoot_r1}): self-check **0 VND** cả 9, byte-repro r1==r2 cả 3 finalist, LAG book identical control (đổi đúng BAL). KHÔNG trial mới — N-ledger giữ 16.

| Config @50B (control = PIN R3) | FULL CAGR/Sh/DD/Cal | IS CAGR/Cal | OOS CAGR/Sh/DD/Cal | LOO min edge | ex-2021 edge | P(DD<−30%) |
|---|---|---|---|---|---|---|
| **control legacy** | **28.82%/1.83/−15.7/1.83** | 25.86/1.98 | **31.59%/1.94/−15.7/2.01** | — | — | 1.5% |
| F1_gate_lean full | 25.49/1.60/−18.0/1.41 | 25.84/2.13 | 25.13/1.55/−18.0/1.39 | −3.92pp | −2.99pp | 5.5% |
| F1 legfoot | 27.08/1.69/−16.9/1.60 | 25.79/2.08 | 28.25/1.73/−16.9/1.67 | — | — | — |
| F6_n_strict full | 26.72/1.68/−17.1/1.57 | 24.99/1.78 | 28.32/1.72/−17.1/1.66 | −2.69pp | −2.02pp | 4.2% |
| F6 legfoot | 27.41/1.71/−17.0/1.61 | 25.46/1.82 | 29.22/1.77/−17.0/1.72 | — | — | — |
| F12_dvr_23 full | 27.36/1.71/−16.9/1.62 | 25.90/2.05 | 28.69/1.76/−16.9/1.70 | −2.50pp | −2.50pp | 3.7% |
| F12 legfoot | 27.43/1.72/−16.9/1.62 | 25.74/2.05 | 28.99/1.79/−16.9/1.71 | — | — | — |

**CP2 (5 tiêu chí cứng khai báo trước): cả 3 NO-GO.** Fail #1 (OOS CAGR cần ≥31.09 & Calmar ≥2.01 — tốt nhất F12 28.69/1.70), fail #2 (LOO edge ÂM khi bỏ BẤT KỲ năm nào, cả ex-2021), fail #3 (tail: P(DD<−30%) 3.7–5.5% vs control 1.5%+0.5); pass #4 (PBO 0.199, CSCV 83 config registry+3 finalist) + #5 (edge âm NHẤT QUÁN dưới cả 2 universe-policy — không đảo dấu). DSR N=16 =1.0000 mọi biến thể (không phân biệt ở Sharpe này, không dùng làm căn cứ).
**Per-year signature chung cả 3:** thua đậm 2020 (−8..−10pp), 2022 (−3.5..−7.5), 2025 (−9..−21), 2026 (−4..−8); F12 2021 +20.95pp = outlier 1 năm làm đẹp số full (LOO ex-2021 −2.50 vs full-geo −1.43). Correlation per-year-delta F1↔F6 0.89, F1↔F12 0.41.
**Root cause gap proxy(+1.2..1.7pp OOS) vs harness(−2.9..−6.5pp OOS) — trace bằng TX attribution:** (1) **MOM_N là trục gãy chính**: control +44B OOS → F1 −35B / F12 −33B / F6 −25B (cả gate r≤3 KHÔNG cứu); lỗ dồn 2025–26 vào junk nhỏ (HHS/NNC/TV1/PVC) mà legacy footprint ngầm chặn (MOM_N legacy đòi tier C/D nên NULL-coverage bị loại) — nghiêm trọng nhất cho phối hợp với DT5G vì NEUTRAL là state phổ biến nhất → MOM_N = kênh entry chính; (2) DVR r=3 (F1) sập +193B→+50B OOS, r∈{2,3} (F12) hồi 1 phần +116B; (3) D1 ≤4 flood RE_BACKLOG entries (2020: 123 vs 80) gây displacement trong book 12-slot; (4) proxy signal-level không mô hình slot-displacement/idle-cash/2022 (đã khai caveat từ Phase 1). Đảo chiều đáng chú ý: dưới bucket redesign, **full-coverage 8L thành ÂM so legfoot** (F1 full 25.13 < legfoot 28.25 OOS) — kết quả 0b "coverage +0.88pp" KHÔNG chuyển giao sang bucket mới; footprint legacy tự nó là 1 quality filter.
**Kết luận nghiệp vụ:** hướng (c) re-tune bucket trên thang 8L gốc — như pre-registered — bị bác ở mức full-harness. Đề xuất fallback theo plan (user quyết): giữ `fa_ratings` static + xử staleness riêng / hybrid E-gate-only (CHƯA đo — cần family mới nếu muốn đo) / rebuild legacy builder. Caveat trung thực: backtest control dùng giá trị lịch sử fa_ratings lúc còn fresh — edge của control KHÔNG bảo chứng cho fa_ratings đóng băng sau mùa BCTC Q2/2026.
**Files:** `data/fa8l_exp/pt_v23_fa8l_phase2_20260711.py` (harness §8), 7 CSV `v23_fa8l_retune_phase2_*`, 9 log `run_phase2_*`, `phase2_compare_20260711.py` + `phase2_compare_out_20260711.log`. Canonical không đụng.

## 2026-07-12 — DVR-8L SIZING-TILT (nhánh (b) momentum-deals) — job Taylor_20260711_235305 (backtest) + Taylor_20260712_010527 (đóng) — VERDICT: **CP-DVR1 NO-GO CẢ 3 (R1/R2/R3)**
**Việc:** trial nhánh (b) sau CP1 NO-GO momentum-deals — khai thác insight "8L rating+route phân tách rõ ở kênh DVR" thành sizing-tilt entry-time (plan `mike/agents/Taylor/plan_dvr_8l_sizing_20260712.md`, user duyệt nguyên trạng, N=5 đóng sổ, không tune ngưỡng — rating≥4/route COMPOUNDER+POWER/size 10/5/2.5% đều pre-registered từ prior art). Harness `pt_v23_audit` integrated @50B threads=1 đúng lệnh pin R3, output `_exp_dvr8lbase/r1/r2/r3/r2h75` (không đè canonical). Self-check **0 VND cả 5 run**; base tái lập ĐÚNG R3 re-pinned 28.82/1.90/−15.7/1.83; PIT spot-check 20 signal-rows + 14 TX-entries = 0 FAIL (`data/dvr8l_exp/spotcheck_result_20260712.log`). Số verify độc lập từ CSV (recompute per-year + LOO re-chain), khớp 100% engine log.

| Config @50B | FULL | IS 14–19 | OOS 20+ | OOS Cal | MaxDD | Cal | Sh | LOO min (ex-yr) |
|---|---|---|---|---|---|---|---|---|
| **base (R3 pin)** | **28.82** | 25.86 | **31.59** | 2.012 | −15.70 | 1.835 | 1.90 | — |
| R1 route-tilt | 28.19 | 24.84 | 31.34 | 2.005 | −15.63 | 1.803 | 1.87 | âm CẢ 13 năm |
| R2 fragility-tilt | 29.72 | 25.69 | 33.56 | 2.136 | −15.71 | 1.892 | 1.95 | **+0.014pp (ex-2021)** |
| R3 combined | 27.97 | 25.70 | 30.08 | 1.915 | −15.71 | 1.781 | 1.86 | âm cả 13 năm |
| R2h75 (sens 7.5%) | 29.74 | 25.63 | 33.66 | 2.143 | −15.71 | 1.894 | 1.95 | **−0.077pp (ex-2021, ÂM)** |

**R1/R3 fail thẳng câu chữ** (OOS < base; R1 thêm IS −1.02pp > tolerance 0.3; LOO âm mọi năm) — trục route V=0.259 mạnh nhất ở signal-level KHÔNG dịch thành NAV edge (half-size COMPOUNDER phạt breadth đau hơn phần né được). **R2 pass câu chữ 4/5 gate đo được nhưng NO-GO theo tinh thần** (user quyết định trực tiếp, không cần DSR): per-year delta = 2018 −1.16 / 2020 **−3.91** / **2021 +17.89** / 2022 −0.32 / 2024 +1.88 / 2025 +2.51 / 2026 +1.10 → toàn bộ +0.90pp Full dồn đúng 1 năm 2021 (48% mẫu DVR labeled — caveat khai báo trước §8.2), ex-2021 edge +0.014pp ≈ 0; sensitivity 7.5% flip dấu ex-2021 thành ÂM → letter-pass của R2 là may mắn ranh giới. Đúng chữ ký F12/fa8l-CP2 (2021-outlier làm đẹp full) — chuẩn đã bác F12 thì bác R2. DSR KHÔNG chạy (quyết định user — moot khi NO-GO); N-ledger 5/5 ĐÓNG, không mở thêm.
**Kết luận nghiệp vụ:** toàn chuỗi momentum-deals ĐÓNG (Phase 1 CP1 NO-GO 0/13 feature + nhánh (b) CP-DVR1 NO-GO). Khuyến nghị Phase 1 giữ nguyên hiệu lực: đóng/thu hẹp MOM_N/MOM_S, tái phân bổ về DVR/RE_BACKLOG (chờ user quyết). Bài học lặp lại: signal-level separation (Cliff δ/Cramér V) ≠ NAV-level edge — proxy vs harness gap y hệt fa8l Phase 1→2. Production V2.4/R3 không đổi.
**Files:** 5 CSV `v23_golive_audit_..._exp_dvr8l*`, log+spotcheck `data/dvr8l_exp/`, plan doc section "CP-DVR1 KẾT QUẢ". `data/dvr8l_exp/dsr_dvr8l_20260712.py` tồn tại nhưng không chạy (theo quyết định user).

## 2026-07-12 — ĐO TÁC ĐỘNG ĐÓNG KÊNH MOM TRONG SIGNAL_V11 (production scoping) — job Taylor_20260712_012515 — VERDICT: **Scope A (−MOM_N,−MOM_S) = khuyến nghị đóng (governance); Scope B (−cả family) = BÁC**
**Việc:** đo tác động THẬT của việc đóng kênh MOM lên toàn book V2.4/R3 trước khi sửa code sống (user duyệt chủ trương sau CP1 NO-GO + CP-DVR1 NO-GO). Harness `pt_v23_audit_2014.py` + knob mới `BAL_DROP_TIERS` (env, unset = byte-identical, tag `_exp_drop*` — §8 an toàn, không thể đè canonical). 3 run contemporaneous cache-vintage đúng lệnh pin R3 @50B threads=1; **self-check 0 VND cả 3**; control tái lập pin CHÍNH XÁC 28.82/1.90/−15.7/1.83; engine print == recompute độc lập từ CSV.

| Run @50B | FULL | Sh | MaxDD | Cal | IS | OOS | OOS Cal |
|---|---|---|---|---|---|---|---|
| control (dropnone) | **28.82** | 1.90 | −15.7 | 1.83 | 25.86 | 31.59 | 2.01 |
| Scope A (−MOM_N,−MOM_S) | 27.84 | 1.84 | −18.2 | 1.53 | 23.15 | **32.30** | 1.77 |
| Scope B (−MEGA,−MOM,−MOM_N,−MOM_S) | 26.62 | 1.78 | −18.2 | 1.46 | 23.31 | 29.71 | 1.63 |

**Cửa sổ (delta vs control):** Scope A: OOS +0.74pp, OOS ex-2021 +0.11pp, 2022+ +1.03pp, 2024+ +0.65pp (gain KHÔNG phải 2021-carry — khác chữ ký R2/F12); chi phí dồn IS 2017 −8.5/2018 −7.7/2020 −4.3 (+2025 −3.8). Scope B: ÂM mọi cửa sổ (OOS −1.85, ex-2021 −1.25, 2024+ −1.79) → MOMENTUM/MEGA generic BULL-only vẫn đóng góp thật, CP1 không phủ chúng — **không đóng lây**. MaxDD cả 3 run cùng episode 2020-07-27; era gần DD không đổi (2024+: −12.3/−11.8/−12.5). LOO Scope A: full-delta −0.97pp âm ở cả 13 phép trung-hòa (broad-based, carrier lớn nhất 2017). DSR 1.0000 cả 2 (N=2 pre-registered, PBO n/a <8 → LOO thay). LAG book byte-identical 3 run (allocator không đụng); vốn giải phóng → DVR 710→780 + parking đúng thiết kế; path-dependence: MEGA fire 5× dưới Scope A (control 0×).
**Kết luận nghiệp vụ:** đóng MOM_N+MOM_S = quyết định risk-governance với giá đo được (FULL −0.97pp, DD kịch bản 2020 sâu thêm 2.5pp) nhưng regime hậu-2021 hoà-tới-dương; đóng cả family bị bác. Cơ chế implement đề xuất: bỏ tier khỏi TIER_BAL ở 3 consumer (golive_recommend_v23:47, pt_v22_dt5g:92, pt_v4_dt5g:61), KHÔNG sửa signal_v11_sql.py (label giữ làm diagnostics), rollback 1 dòng/file. Nếu duyệt: re-pin R3 → ≈27.84/1.84/−18.2/1.53 + cập nhật KB. **CHƯA sửa code sống — chờ user duyệt phạm vi + quant-skeptic.**
**Files:** plan `mike/agents/Taylor/plan_close_mom_20260712.md`; 3 CSV `v23_golive_audit_..._exp_dropnone/_exp_dropMOMN-MOMS/_exp_dropMEGA-MOM-MOMN-MOMS`; log + `analyze_momclose.py` + runner trong `data/momdeal_exp/`. Canonical không đụng.

## 2026-07-12 — RE-PIN BASELINE R3 (ĐÓNG KÊNH MOM_N/MOM_S — Scope A, user sign-off CUỐI CÙNG) — job Taylor_20260712_025715
**Việc:** thực thi production change đã duyệt trọn chuỗi quyết định: momdeal Phase 1 **CP1 NO-GO** (0/13 feature qua gate pre-registered, thành công MOM = dồn mẫu 2020-21) → nhánh (b) **CP-DVR1 NO-GO** → đo Scope A/B (job _012515) → tách MOM_N vs MOM_S (job _022816: Scope C backtest + Phase-1b regime-split) — mỗi bước quant-skeptic CONFIRMED — → **user duyệt CUỐI: Scope A** (đóng MOMENTUM_N + MOMENTUM_S, GIỮ MOMENTUM/MEGA generic).
**Code (rollback = revert 1 dòng/file):** bỏ `MOMENTUM_N`,`MOMENTUM_S` khỏi `TIER_BAL` ở 3 consumer production — `deploy_golive_dt5g_v4/golive_recommend_v23.py:47` (**money-path** SpaceX/ZaloPay), `pt_v22_dt5g.py:92` (sổ tín hiệu production), `pt_v4_dt5g.py:61` (paper mirror) — + default `TIER_BAL` của harness canonical `pt_v23_audit_2014.py:499` cùng commit (backtest == production, không lệch). KHÔNG sửa `signal_v11_sql.py` (label MOM giữ nguyên làm diagnostics, đúng plan §2). Safety xác nhận trước khi sửa: BAL/LAG live RỖNG (NEUTRAL parking từ ~04/2026) — không vị thế MOM nào bị ép thoát; PSI MOM_N_W trong sổ paper pt_v22 = case plan §2 đã dự liệu (tự thoát theo exit rule, đóng kênh chỉ chặn entry mới).
**Lệnh regenerate (ĐÚNG lệnh pin + BQ_LOCAL_CACHE bắt buộc):** `BQ_LOCAL_CACHE=1 BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" AUDIT_END=2026-06-19 $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge` → CSV canonical `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap.csv` (log `data/run_r3_repin_momclose_20260712_v2cache.log`).

| R3 @50B NEUTRAL-only | CAGR | Sharpe | MaxDD | Calmar | IS 14–19 | OOS 20+ |
|---|---|---|---|---|---|---|
| Pin cũ (2026-07-11, dt5g swap, TIER_BAL còn MOM_N/S) | 28.82% | 1.90 | −15.7% | 1.83 | 25.86% | 31.59% |
| **PIN MỚI (Scope A, 2026-07-12)** | **27.84%** | **1.84** | **−18.2%** | **1.53** | 23.15% | **32.30%** |

**Verify (đủ chuẩn §8):** (1) self-check **0 VND** BAL+LAG (cash-flow + final-NAV identity), borrow cost 0, max gross 1.000, threads=1; (2) CSV canonical mới **byte-identical** với `..._exp_dropMOMN-MOMS.csv` (run đo Scope A cùng cache-vintage đã quant-skeptic CONFIRMED) → DSR trên NAV daily carry nguyên **1.0000** (z=6.37; N-ledger 3 trial A/B/C pre-registered, PBO n/a <8 — thay bằng LOO 13 phép trung-hòa đã ghi plan §4.4); (3) recompute độc lập `extract_peryear.py`: FULL 27.84 / IS 23.15 / OOS 32.30 khớp chính xác engine print; recompute Sharpe/MaxDD/cửa sổ từ DAILY rows khớp (OOS 32.30 / 2022+ 21.30 / 2024+ 30.87 / OOS ex-2021 ~21.9).
**Sự cố trong lúc re-pin (bắt được nhờ kỷ luật khớp-chính-xác, không phải "gần đúng là được"):** run re-pin ĐẦU chạy thiếu `BQ_LOCAL_CACHE` (rơi về live BQ) → 28.28/1.89/−17.9/1.58 LỆCH số đã đo → DỪNG theo đúng chỉ đạo dispatch, root-cause, re-run với cache → khớp chính xác. Canonical CSV mang nội dung live-BQ sai trong ~15 phút (Chủ nhật ~10:06–10:21 ICT, không cron/consumer nào đọc trong khoảng đó); bản đúng đã đè. **Bài học ghi vào lệnh pin ở trên: `BQ_LOCAL_CACHE=1` giờ là PHẦN CỦA lệnh pin**, không phải env tùy chọn.
**Phát hiện phụ + đóng luôn trong job:** run Scope C sáng nay (job _022816, §6.2 plan) hoá ra CŨNG chạy live-BQ — TRÁI khai báo "cùng cache vintage" §6.1. Re-run Scope C sạch (cache-vintage, log `data/momdeal_exp/run_cache_dropMOMN_clean.log`, self-check 0 VND): **28.15/1.85/−18.1/1.56**; cửa sổ OOS 32.38 / OOS ex-2021 21.30 / 2022+ 20.48 / 2024+ 30.34 — so Scope A: 32.30 / **21.92** / **21.30** / **30.87**. **Kết luận GIỮ SCOPE A không đổi và VỮNG HƠN bản báo sáng**: dưới vintage sạch, C kém A ở CẢ 3 cửa sổ hậu-2021 (kể cả 2024+ — bản live-BQ từng cho C nhỉnh ở đó, đảo lại); phần hơn FULL của C (+0.31pp) là 2021-carry thuần (2021: C +112.65 vs A +106.81). Phần 2 regime-split (MOM_S tách riêng 0/13 FDR-pass) độc lập vintage (dataset Phase 0 đông cứng) — 2 chân bằng chứng vẫn đồng thuận.
**Backup/revert:** canonical cũ (nội dung pin 07-11) tại `..._pre_momclose_repin_20260712_backup.csv`; revert code = khôi phục 2 tier vào TIER_BAL ở 4 file.
**⭐ Số tham chiếu chính thức V2.4/R3 từ 2026-07-12: CAGR 27.84% / Sharpe 1.84 / MaxDD −18.2% / Calmar 1.53** (IS 23.15% / OOS 32.30% — OOS > IS giữ nguyên cấu trúc walk-forward). Đây là re-pin **GOVERNANCE** (đóng kênh có edge lịch sử đã bị bác là không lặp lại, chi phí dồn 2017–2020, hậu-2021 hoà-tới-dương) — KHÔNG phải return-enhancer. Mọi so sánh trước/sau phải nói rõ đang so pin nào.

## 2026-07-12 — V2.5 LEVERAGE VERIFICATION (LOO per-episode + DSR, re-pinned config) — job Taylor_20260712_054553 / _063143 — VERDICT: **NO-GO (giữ DISABLED)**
**Việc:** kiểm chứng go/no-go V2.5 (= V2.4 + lever MGE 1.5 CAPIT-only) trên nền config ĐÃ re-pin 2 lần (DT5G swap 07-11 + MOM closure 07-12) — số V2.5 pinned cũ 30.05 LỖI THỜI. Phần 1 (job _054553): xác nhận nhãn "Spyros-approved" trong trading_rules.json = ĐÚNG — bus event 2026-06-27T02:59Z `mge20-tail-review-REJECT-cap-at-1.5`: REJECT MGE 2.0 / APPROVE 1.5 **có điều kiện** ("ANY S4 fire @1.5x trong 6 tháng đầu → stop+review"); phân biệt với event 06-24 "BLOCK vĩnh viễn" = config CŨ margin_tiers full-book. Phần 2-3: 6 run `pt_v25_loo_tmp_20260712.py` (copy pt_v23_audit + env `LEVER_SKIP`/`EXP_TAG`, output non-canonical `_v25chk_*` — §8 an toàn), cache-vintage `BQ_LOCAL_CACHE=data/bq_cache` threads=1, **self-check 0 VND cả 6 run** (BAL+LAG), S4 margin-call ON 0 fires, max gross 1.485 < hard 1.65.

| Run @50B (V2.5-config: R3 + recovery-park CAPIT 1.7x state-blind PE≤0.20) | FULL | Sh(252) | MaxDD | Cal | IS 14–19 | OOS 20+ |
|---|---|---|---|---|---|---|
| LF (leverage-free control) | 29.41 | 1.82 | −20.9 | 1.41 | 23.15 | 35.45 |
| **LEV (prod-spec: MGE1.5 frac.50 cap100B borrow12.5%)** | **30.34** | **1.86** | **−20.6** | **1.47** | 25.03 | 35.40 |
| LOO2020 (skip 3 lever dates 2020) | 30.30 | 1.85 | −20.4 | 1.49 | 25.03 | 35.33 |
| LOO2022 (skip 2022-12-06) | 30.34 | 1.86 | −20.6 | 1.47 | 25.03 | 35.40 |
| LOO2023 (skip 2023-04-06/06-08) | 30.34 | 1.86 | −20.6 | 1.47 | 25.03 | 35.40 |
| LEVnocap (cap 100000B — proxy live NAV nhỏ) | 30.26 | 1.85 | −20.6 | 1.47 | 25.03 | 35.26 |

**Phân rã edge lever (LEV − LF = +0.92pp FULL): KHÔNG PHẢI edge cơ chế, không sống OOS.**
- **IS +1.88pp / OOS −0.04pp** → fail thẳng quy chuẩn "edge rớt OOS = loại". Nghịch lý: cả 6 bottom-dates lever đều nằm OOS (2020-03-12/03-19/04-21, 2022-12-06, 2023-04-06/06-08) nhưng edge dồn hết IS — vì path LEV tách khỏi LF từ **2014-05-09** (~6 năm TRƯỚC lever date đầu tiên): bật machinery margin (MGE=1.5) đổi hành vi từ đầu (borrow-days BAL 54/LAG 107 rải cả IS, tổng borrow cost chỉ 1.07B VND trên NAV 1357B) → excess per-year swing ±5–12pp đổi dấu liên tục (2014 +8.1, 2020 +5.4, 2021 −6.2, 2024 −2.8, 2025 +4.8 log-pts) = **path-divergence noise (butterfly), không phải financed-exposure alpha**.
- **LOO per-episode:** 2022 + 2023 = byte-identical LEV (borrow-audit + NAV trùng từng đồng) — 2 episode này BỊ NAV-cap 100B tự vô hiệu (NAV backtest vượt 100B trước 12/2022, lever auto-disable). Chỉ 2020 (COVID) từng thực sự lever; đóng góp ròng = **+0.04pp** full CAGR (gain trực tiếp 2020 +0.58 log-pts bị noise hậu-path nuốt: LOO2020 hơn LEV +0.85 ở 2021, +0.84 ở 2022). n hiệu dụng = **1 episode cluster**.
- **LEVnocap** (đại diện đúng cho live NAV ~1B, cap không bao giờ bind → mọi episode tương lai đều lever): +0.85pp FULL / **OOS −0.19pp** — 2 episode 2022/2023 khi được phép chạy là net ÂM.
- **DSR trên excess series (LEV−LF):** SR ann ~0.29, skew +1.48, kurt 34.3 → DSR = 0.564 (N=3) / 0.352 (N=7) / 0.184 (N=20, họ lever sweeps từng so) — **RED FLAG < 0.95 ở MỌI mức N**. OOS-only excess: SR ann −0.01, DSR 0.19. DSR trên NAV tuyệt đối LEV = 1.0000 (vô nghĩa cho câu hỏi này — do beta chiến lược gốc, không phải lever). **PBO: n/a** — family 2 config, CSCV không có nghĩa; nói thẳng thay vì báo số ảo. Giới hạn thống kê: 1 episode cluster hiệu dụng → mọi inference về "edge lever" là anecdote, không phải phân phối.
**Kết luận nghiệp vụ: NO-GO — giữ V2.5 DISABLED.** Edge +1.00pp từng đo trên pin cũ không tái lập có ý nghĩa trên config production hiện hành: phần attributable cho cơ chế lever ≈ +0.04pp, OOS ≈ 0, DSR RED FLAG. Điều kiện tái xét (cụ thể): (a) tích lũy episode capitulation MỚI ngoài mẫu — theo dõi S2 trigger fire trên paper trước, KHÔNG cần bật gì ở live; (b) nếu muốn đo lại: thiết kế episode-windowed sim cô lập cơ chế khỏi full-path butterfly (so sánh trong cửa sổ ±60d quanh từng episode, cùng path nền) thay vì diff 2 full-run; gate = DSR excess ≥0.95 + OOS-positive. Nhãn Spyros-approved MGE 1.5 vẫn hiệu lực (có điều kiện S4-6M) NẾU user tương lai muốn bật trên cơ sở risk-appetite — nhưng verdict quant hôm nay: kỳ vọng ≈ 0, chỉ thêm complexity máy móc tail. Số V2.5 tham chiếu mới (nếu cần quote): LF 29.41 / LEV 30.34 (bảng trên).
**Files:** 6 CSV `..._v25chk_{LF,LEV,LOO2020,LOO2022,LOO2023,LEVnocap}.csv`, log + runner + harvest tại `data/v25chk_logs/`; harness tạm `pt_v25_loo_tmp_20260712.py` archive vào `data/v25chk_logs/` (không để repo root — §8/§10). Canonical + trading_rules.json + production KHÔNG đụng.

## 2026-07-12 — FIX SPEC-DRIFT MONEY-PATH: edge-conditional w_LAG gate vào golive_recommend_v23.py — job Taylor_20260712_072039 (nối trace Taylor_20260712_070206)
**Việc:** user duyệt fix bug phát hiện ở plan_lag_weight_20260712.md §4/§9(1): `golive_recommend_v23.py:206` (money-path — DollarBill đọc recs lập plan thật) hardcode `w_tgt = STATE_LAG_WEIGHT.get(state_today, 0.5)` = 65% VÔ ĐIỀU KIỆN ở state 3/4/5, trong khi pinned R3 (argv `v23a none postbull 0 edge`) gate tilt 0.65 theo edge-health LAG (`pt_v23_audit_2014.py:1738-1751`): mean12 (trailing-12M mean post-return LAG, causal, `data/lag_edge_health.csv`, ffill as-of ngày signal) ≥ 4% → 0.65, else 0.50. BEAR=0/CRISIS=0.50 giữ nguyên. `pt_v22_dt5g.py:762-775` ĐÃ có gate đúng từ trước — chỉ recommender drift; chính lệch này tạo REBALANCE flag GIẢ trong output 07-11 (target 65% vs current 49% = breach band ±10pp; spec đúng: 50% vs 49% = trong band).
**Fix:** port hàm `w_lag_target(state, asof)` mirror đúng harness (KHÔNG viết lại khác đi): đọc cùng CSV, `drop_duplicates("entry")`, `Series.asof` (≡ reindex-ffill của harness tại 1 ngày), cùng ngưỡng EDGE_THR=4.0, cùng nhánh notna. CSV unreadable → fail-safe 0.50 (nhánh gate-fail, bảo thủ). 1 thay đổi surgical: docstring + hàm mới + 1 dòng thay ở section 5. KHÔNG đụng gì khác.
**Verify:**
- Mirror logic vs artifact pinned R3 (`..._edge_etfliqcustompitg_wtnamecap.csv`, cột `w_lag_tgt` DAILY): **0/3107 ngày lệch** (2014-01-02 → 2026-06-19; phân bố 0.65×1113 / 0.50×1774 / 0.00×220).
- Hàm production THẬT (extract từ source qua ast): **0/40 flip-days lệch + 0/200 ngày random lệch** vs pinned CSV.
- Chạy thử recommender (BQ_LOCAL_CACHE, signal date 2026-07-10): `[edge-alloc] mean12 = 0.5% < 4% -> w_LAG 0.50` — in đúng **50%**, current 50% → "trong band, không rebalance" (hết REBALANCE giả).
- Selfcheck mới `edge_wlag_gate_selfcheck.py` **13/13 PASS**: gate fail→0.50 (3/4/5), pass→0.65, boundary 4.0→0.65, BEAR→0/CRISIS→0.50 bất chấp mean12, CSV missing→0.50, pre-history NaN→0.50, không còn hardcode (`w_tgt = STATE_LAG_WEIGHT.get` phải vắng mặt trong source), equivalence 40 flip-days vs pinned CSV.
**Tác động thực tế NGAY (kiểm tra thật, không giả định):** BAL/LAG đang rỗng (NEUTRAL parking từ ~04/2026), run hôm nay 0 BAL picks / 0 LAG entries → plan T+1 kế tiếp **không đổi lệnh nào** (vẫn HOLD + park 70%). Thay đổi CÓ hiệu lực ngay ở guidance: status/md giờ báo target 50% (thay 65%) và bỏ flag REBALANCE giả — tránh DollarBill sinh action rebalance không được backtest bảo chứng. Hiệu lực sizing thật: khi LAG refill (dự kiến cuối 07), slot LAG được size trên book = 50% NAV (không phải 65%) chừng nào edge-health còn < 4%. Consumers downstream (`telegram_recommend.py`, `push_recommend_v23_to_bq.py` của Mafee) đọc từ status json → tự nhận giá trị đúng, không cần sửa.
**Caveat còn treo (đã flag ở plan §4, việc Winston):** `lag_edge_health.csv` entry cuối 2026-05-11 (file mtime 07-10) — cần xác nhận writer refresh định kỳ trước khi LAG refill; nếu file đông cứng thì gate sống trên dữ liệu cũ dần. KHÔNG chạy backtest family LAG-WEIGHT (user đã quyết không cần — đây là bug-fix align spec, không phải thay đổi chiến lược).
**Rollback:** revert 1 commit (hàm + 1 dòng). Chờ quant-skeptic verify (Mike dispatch) — thay đổi chạm money-path.

## 2026-07-12 — Q-SLEEVE (rổ nhỏ quality-concentrate thay custom30V parking + thử BULL-extension) — job Taylor_20260712_080114 / _090329 — VERDICT: **NO-GO CẢ 2 TRỤC (đóng nhánh)**
**Việc:** backtest family Q-sleeve N=5 pre-registered (`plan_quality_sleeve_20260712.md`, user duyệt 07-12): thay vehicle parking custom30V (top30, gate≤3, namecap 0.10) bằng rổ NHỎ chất lượng cao hơn — Q8-NEU (top8, gate≤2, ew, liq-floor 5B), Q12-NEU (top12, cùng gate), QF8-NEU (top8, KHÔNG rating-gate, thay bằng Đ2 fundamentals floor ROE_Min5Y≥0.10 ∧ CF_OA_3Y>0 ∧ FSCORE≥5), + trial 4 BULL-ext = winner mở park sang state 4/5 (PARK_STATES=3:0.7,4:0.7,5:0.7). Control = R3 đương thời cùng cache-vintage. Harness `pt_v23_audit_2014.py` + knobs mới env-default-OFF (`BASKET_GATE_RATING`/`BASKET_QFLOOR`/`BASKET_LIQ_FLOOR_B` tag filename theo §8, `EXP_TAG=qsleeve_*` — không đụng canonical). `BQ_LOCAL_CACHE=data/bq_cache` threads=1, **self-check 0 VND cả 5 run** (BAL+LAG), borrow cost 0 VND.
**Control tái lập pin CHÍNH XÁC: 27.84/1.84/−18.2/1.53** (IS 23.15 / OOS 32.30) — sanity đạt.

| Run @50B | FULL CAGR | Sh(252) | MaxDD | Cal | IS 14–19 | OOS 20+ (CAGR/Cal) |
|---|---|---|---|---|---|---|
| **ctrl (custom30V, pin R3)** | **27.84** | 1.84 | **−18.2** | **1.53** | **23.15** | 32.30 / 1.77 |
| Q8-NEU | 24.95 | 1.59 | −22.1 | 1.13 | 16.67 | 33.08 / 1.60 |
| Q12-NEU (winner-ít-tệ-nhất) | 24.91 | 1.63 | −22.1 | 1.13 | 16.39 | 33.29 / 1.78 |
| QF8-NEU (Đ2 floor) | 24.76 | 1.54 | −24.7 | 1.00 | 20.20 | 29.09 / 1.54 |
| Q12-BULLEXT (trial 4) | 25.88 | 1.57 | −22.1 | 1.17 | 16.87 | 34.78 / 1.87 |

**Gate CP-QS1 (§7): FAIL GẦN NHƯ TOÀN DIỆN cả 4 trial.**
- **Per-year LOO (gate quyết định): ÂM Ở MỌI NĂM BỎ-RA, cả 4 trial** (Q12-NEU: −1.5 tới −4.1pp mọi năm; ex-2020+2021 = **−4.46pp**). Phần OOS "cạnh tranh" (Q12-NEU 33.29 vs ctrl 32.30) là **carry thuần từ 2021**: per-year delta 2021 = +24.3pp (Q12) / +20.5 (Q8) / +31.2 (BULLEXT) — đúng chữ ký lỗi regime-2021 đã bác ở dự án MOM (CP1) và fa8l (F12). Bỏ 2021 là trial thua mọi cấu hình cửa sổ.
- **IS 2014-19: kém control 2.95–6.76pp** (gate cho phép tối đa −0.3pp) — rổ nhỏ ew không sống nổi giai đoạn thị trường mỏng.
- **Tail: MaxDD −22.1 tới −24.7% vs control −18.2%** — xấu hơn 3.9–6.5pp, fail.
- **Concentration diagnostic** (per-name attribution offline trên deployed capital, `diag_concentration.py`): tổng excess sleeve-vs-custom30V = **−99.84B (Q12-NEU) / −131.39B (BULLEXT)** — KHÔNG có edge dương để concentrate (test 40%-share moot); max single-name **13.24% NAV** (vượt namecap 10% của incumbent = thêm name-risk không được trả công); NEUTRAL fill-shortfall p95 = **100%** (có ngày không fill được đồng nào, mean 6.08%, 115/1912 ngày >5% — capacity KÉM HƠN control rõ); churn membership 39%/rebal (turnover cao hơn rổ 30).
- **DSR (N=5 khai báo, methodology `dsr_pbo_annex.py`; PBO n/a family<8 theo plan, LOO thay thế):** trên NAV tuyệt đối = 1.0000 (vô nghĩa — beta V2.4 gốc); trên **excess series vs control** (convention V2.5-verification): excess-SR ann **ÂM cả 4 trial** (−0.26 tới −0.48), DSR = **0.020–0.095 — RED FLAG cực nặng**, không có gì để deflate vì edge âm ngay mặt.
- **Trial 4 BULL-ext (gate riêng chặt hơn — tiền lệ 4 lần bác):** chết đúng chỗ tiền lệ chết — per-year delta **2025 = −19.53pp**, 2018 = −4.30pp (gate đòi không-âm ở 2018/2024/2025); ex-2020+2021 = −4.69pp (gate đòi ≥0). OOS 34.78 đẹp nhất bảng nhưng = 2020 +10.6pp và 2021 +31.2pp carry; đây là **tiền lệ bull-park bị bác lần thứ 5**, mạnh hơn các lần trước vì lần này có cả concentration diagnostic âm.
**Kết luận nghiệp vụ — NO-GO cả 2 trục, đóng nhánh:**
1. **Trục "rổ nhỏ chất lượng thay custom30V": NO-GO.** Cơ chế: custom30V thắng nhờ BREADTH (30 tên, namecap 10%, không ép rating quá gắt) — siết xuống 8-12 tên gate≤2/quality-floor làm mất diversification premium trong khi phần chọn lọc thêm không có alpha (attribution per-name: các tên "tốt" DPG/STB/DGC cộng +4-7B nhưng đuôi SSB/HAH/DTD/IDC trừ 9-15B mỗi tên). Đ2 fundamentals-floor (QF8) không cứu — còn tệ nhất tail (−24.7%).
2. **Trục "mở rộng park sang BULL/EXBULL": NO-GO lần 5.** Nhất quán với 4 tiền lệ (bull-park (30,0.15) overfit walk-forward-bác; hold-neutral exit −47B; …): mọi cấu hình đẩy thêm exposure vào BULL đều là bet một-chiều vào việc 2021 lặp lại. Không mở thêm trial BULL-extension nếu không có cơ chế mới thật sự khác biệt — 5 data-point cùng kết luận là đủ.
**N-ledger: 5/5 ĐÓNG** (4 chạy + trial 5 dự phòng không dùng — winner đã fail thì mọi biến thể sâu hơn vô nghĩa; không mở thêm). Kỳ vọng khai báo trước ở plan (+0.2-0.8pp nếu GO) — thực đo −2.9pp FULL: premise "chất lượng cô đặc > breadth" bị số liệu bác thẳng, đúng quy trình.
**Files:** 5 CSV `..._exp_qsleeve_{ctrl,q8neu,q12neu,qf8neu,q12bullext}.csv` (data/), log + runner + analyze/diag/dsr scripts tại `data/qsleeve_logs/`; harness knobs commit cùng ngày (env-default-OFF, control tái lập pin = bằng chứng byte-identical). Prior-attempt CSV (thiếu tag gate/liqf — chính là lỗ hổng §8 đã vá bằng `_qs_tag`) archive ở `data/qsleeve_logs/prior_attempt/`. Canonical + production + trading_rules.json KHÔNG đụng.

## 2026-07-12 — FIX R1 CRITICAL (audit Q2 roll-in): LIVE LAG candidate source point-in-time — job Taylor_20260712_124834 (trace cha Taylor_20260712_121642) — PRODUCTION FIX, backtest KHÔNG đổi
**Gap (R1, `audit_q2_rollin_signal_20260712.md`):** `golive_recommend_v23.py` (money-path 17:30 → DollarBill plan) lấy candidate LAG duy nhất từ `data/earnings_events_classified.csv`, nhưng writer (`refresh_lagged_caches.py`) chỉ ghi event khi đủ CẢ 4 mốc giá (kể cả release+30 phiên) → event mới công bố chỉ xuất hiện sau ~30 phiên, khi entry T+5 đã trôi ~25 phiên — **100% entry LAG mùa BCTC bị miss trong im lặng**. Bằng chứng sống: CSV max Release_Date 2026-05-04 vs pkl (fresh daily) đã có MBS 2026-07-08.
**Fix:** module mới **`lag_live_schedule.py`** — candidacy tính từ dữ liệu biết được NGAY tại ngày release: identity/NP_R/surprise_B_MA từ `earnings_surprise_data.pkl` (re-pull daily), prior_n_good/pa_HL3 từ classified CSV (prior luôn ≥1 quý tuổi → luôn đủ cửa sổ). Wire vào golive_recommend_v23 §4 CHỈ thay nguồn candidate (scheduling loop giữ nguyên); **CSV + writer + backtest semantics KHÔNG đụng** (pt_v23_audit_2014/pt_v22 full-replay giữ nguyên nguồn cũ). DC-book `n_lag_upcoming` (dc_book_waterfall_paper đọc `golive_v23_status.json`) tự nhận nguồn mới qua golive — không cần sửa riêng.
**Verify (chuẩn money-path):**
- **Selfcheck `lag_live_schedule_selfcheck.py` 23/23 PASS**: (A) parity old-vs-new trên toàn bộ 51.209 event lịch sử — **qualify khớp 100%** (0 mismatch, 5.387 qualifier), prior/pa_HL3/surprise/tier khớp tuyệt đối trừ đúng 2 case sibling-cùng-ngày (BOT 2026-01-28, CT6 2026-02-02 — code cũ đếm sibling làm prior bằng post_ret chưa tồn tại tại ngày release = look-ahead 30 phiên + phụ thuộc thứ tự dòng; bản mới strict `<` là định nghĩa point-in-time duy nhất khả thi, qualify 2 case này không đổi); (B) MBS 2026Q2 hiện diện NGAY với gate CHẤM ĐÚNG (NP_R=36.0 ✓, prior_n_good=23 ✓, pa_HL3=4.06<5 ✗ → không qualify — khớp audit R6, không mất trade nào); (C) synthetic event công bố HÔM NAY → qualify + schedule "T+5 phiên tới" ngay, old path mù; negative control 3 prior → reject; (D) wiring guard.
- **Backtest pin R3 re-run** (ĐÚNG lệnh pin `BQ_LOCAL_CACHE=data/bq_cache BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" AUDIT_END=2026-06-19 $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge` + `EXP_TAG=r1lagfix_verify` để không đè canonical): **27.84/1.84/−18.2/1.53 khớp pin, self-check 0 VND cả BAL+LAG, CSV md5 `4d736d9169c32f1055ea6c54ee5c6dac` BYTE-IDENTICAL với canonical** (`..._exp_r1lagfix_verify.csv`, log `data/run_r1lagfix_verify_20260712.log`). Lưu ý pin-command: dạng `BQ_LOCAL_CACHE=1` ghi ở L2798 là SAI-IM-LẶNG (manifest không tồn tại ở `workdir/1/` → rơi về BQ sống) — phải dùng `=data/bq_cache` + check dòng `[BQ_LOCAL_CACHE] ready`.
- **pt_v22_dt5g (paper) không re-run có chủ đích**: không import module mới, input files untouched (dependency-verified) — re-run ngoài lịch sẽ đẩy production paper log lệch cron 1 ngày. Semantics full-replay giữ nguyên.
- **Golive end-to-end** (BQ_LOCAL_CACHE, signal date 2026-07-10): `[lag-live] 1090 events in window, 137 qualify, release max 2026-07-08` — nguồn live nhìn thấy tới MBS 07-08 (cũ: 05-04). Hành vi HÔM NAY không đổi (0 upcoming/0 recent — event Q1 đã qua entry, MBS không qualify): fix chỉ kích hoạt khi release Q2 qualify bắt đầu về (~2 tuần tới), đúng mục tiêu "sửa trước khi bị dồn".
**Hạn chế biết trước:** golive_recommend.py (V4, paper benchmark — KHÔNG money-path) vẫn đọc CSV cũ → benchmark V4 vẫn mù event mới; chấp nhận (ngoài scope, không ảnh hưởng plan). **Rollback:** revert 1 commit. Chờ quant-skeptic/risk-auditor phản biện độc lập (Mike dispatch).

## 2026-07-13 — ĐIỀU TRA 2 NGHI VẤN USER (A: "mua cao hơn close"; B: "NAV giảm ~5%/2 tuần") — job Taylor_20260713_040055 — CHẨN ĐOÁN, KHÔNG đổi chiến lược
**Bug fix đi kèm (commit `f8cbb35`):** `execution_quality_review.py` báo "no completed fills" vì chỉ parse `payload.resp` (fillQuantity=0 lúc place), bỏ hẳn `payload.orders` poll records (nơi chứa trạng thái Filled). Fix: ingest cả 2, dedup last-state per (date, order id), fill-ts = poll đầu tiên có fill; thêm `--account LABEL` lọc theo `accountNo` trong order object (top-level `account_no` chỉ có từ file 07-06+, lọc theo nó sẽ mất sạch data go-live). Known limitation ghi trong docstring: lệnh khớp ATC SAU lần poll cuối giữ state cũ (case thật: VHC 600cp ZaloPay 07-10 order 502431 — positions xác nhận đã bán).
**CÂU A — VWAP mua vs close chính thức (Price không điều chỉnh, `tav2_bq.ticker_1m`; DCM/MBB có điều chỉnh giá hồi tố trong cửa sổ nên KHÔNG dùng Close adjusted):** 28 name-days (SpaceX 07-01/02, ZaloPay 07-07..10; 07-13 chưa có close). Mean +25.4bps, **VND-weighted +42.1bps**, median +39.6, 18/28 mua cao hơn close, t=1.63 (KHÔNG đạt significance, mẫu dồn 6 ngày). NHƯNG: vs OPEN chỉ +3.3bps (SpaceX weighted) / +11.0 (ZaloPay) — execution KHÔNG đuổi giá; per-day sign đảo (07-01 weighted **−21.0bps** dưới close, 07-02 +76.7). SELL mirror image: **+92.4bps weighted TRÊN close** (bán sớm trong ngày được giá tốt). Quy VND: buy "đắt hơn close" −6.42M trên 1.527M mua, sell "được hơn close" +7.78M trên 842M bán — net ≈ +1.4M. **Cơ chế: live gate mua ~09:15 (fill_timing_live_gate CHƯA flip → chưa dùng cửa sổ 10:45-11:15) + thị trường 2 tuần này drift XUỐNG trong phiên** → mua đầu ngày cao hơn close là beta trong-ngày, không phải lỗi chiến lược đặt lệnh. Fix đã có sẵn trong pipeline: flip fill-timing window (edge +17.6bps, t=12.0, job Taylor_20260702_031608) chờ đủ mẫu paper ~cuối 07.
**CÂU B — NAV live 11:08 ICT 07-13 (DNSE latest_trade G1, KHÔNG phải quote stale):** SpaceX **960.245.577đ = −3.98%** vs 1B go-live 07-01 (Mike đọc 971.7M lúc 10:57 là STALE — dùng BQ close 07-10; hôm nay VNINDEX đang −1.2% intraday). ZaloPay **964.998.035đ = −4.59%** vs go-live 1.011,47M (07-06) — **đây là con số "gần 5%"**. Đỉnh NAV SpaceX từng ghi: 994,73M (07-02, chưa bao giờ vượt 1B; gross 1.4B ngày 07-02 là exposure double-buy, không phải NAV). VNINDEX cùng kỳ: 1860.01 (06-30) → 1806.42 live = **−2.88%** (SpaceX window) / 1862.08 (07-03) → −2.99% (ZaloPay window).
**Attribution (self-check: giải thích khớp NAV thật residual 0.15M SpaceX / 0.3M ZaloPay):**
- SpaceX −39,8M = P&L cổ phiếu −38,87M (dàn trải: BID −7.4, VPB −4.4, MBB −4.0, TCB −4.0, VCB −3.8, CTG −3.7, VHM −3.1… không có blowup đơn lẻ; tệ nhất %: VIX −12.9% từ VWAP mua) + phí 1.59M + thuế bán 0.71M + lãi margin ~0.83M (409.86M×5d + 188.79M×2d @12.5%) − cổ tức chờ về +2.4M (MBB, chưa vào totalCash). Excess −1.1pp vs index do: (i) 141% gross exposure 07-02→07-06 (double-buy, đã fix) khi index −1.27%, (ii) chi phí giao dịch/margin ~0.31% NAV, (iii) rổ bank-heavy giảm sâu hơn index (riêng hôm nay stocks −1.71% vs index −1.2%).
- ZaloPay −46,5M = **legacy positions −41,3M** (DGC excluded −20.5M = 44% tổng giảm = −2.03pp NAV; VPB −11.6M; VIB −5.7M; VHC −2.9M…) + **V2.4 entry mới chỉ −4.2M trên ~155M deployed (−2.7%, ngang index −3.0%)** + phí/thuế 0.66M. Phần V2.4 thật sự vận hành ĐÚNG beta thị trường.
**KẾT LUẬN:** (A) KHÔNG có lỗi hệ thống trong chiến lược mua — chênh lệch vs close là intraday drift của thị trường giảm, execution vs open sạch (+3-11bps), cải tiến duy nhất (fill-timing window) đã trong pipeline chờ flip đúng quy trình. (B) KHÔNG cần review chiến lược — mức giảm −4.0/−4.6% trong khi index −2.9/−3.0% nằm hoàn toàn trong khung backtest (R3 MaxDD −18.2%, bootstrap 5th-pct −28.6%); phần lệch của ZaloPay chủ yếu là DGC/legacy ngoài chiến lược, của SpaceX chủ yếu là sự cố double-buy (đã fix từ 07-02) + chi phí một lần của đợt trim. Theo dõi tiếp: nếu drawdown vượt ~−10% từ go-live với index đi ngang → lúc đó mới đáng mở điều tra chiến lược thật.
**Files:** `mike/agents/Taylor/fills_dedup_20260713.csv`, `vwap_vs_close_20260713.csv`, `px_cache_20260713.csv`. Số liệu intraday 11:08 — close chính thức 07-13 sẽ lệch nhẹ, không đổi kết luận.

## 2026-07-13 — ECOLOGY DASHBOARD (AMH#4) WALK-FORWARD VALIDATION + P(NEUTRAL→BEAR/CRISIS) REFRESH — job Taylor_20260713_042317 — NGHIÊN CỨU, KHÔNG đổi production
**Câu hỏi user (qua Mike):** có dashboard đo xác suất thị trường nghiêng lên/xuống không? Validate `ecology_dashboard.py` (chưa từng có trong registry) + tính lại P(NEUTRAL→BEAR/CRISIS) với data mới nhất.
**Look-ahead audit `ecology_dashboard.py`:** features (opportunity/uniformity/mood/madness) đều CAUSAL (rolling z/pctile 504 phiên, min 120); `fwd20/fwd60` (shift âm) CHỈ dùng trong `validate()` để báo cáo, KHÔNG lọt vào live reading (`now_block`) — đạt quy tắc "forward-looking chỉ để validate". NHƯNG `validate()` gốc dùng `pd.qcut` full-sample (decile edges nhìn cả tương lai) → bài validate tự thân bị in-sample; đã làm lại đúng chuẩn walk-forward.
**Walk-forward (script `mike/agents/Taylor/ecology_wf_validation_20260713.py`, panel refresh BQ tới 2026-07-10, 3.122 phiên; decile edges chỉ từ IS 2014-19, áp nguyên trạng lên OOS 2020+; N trials = 1 signal pre-existing, không sweep):**
- **VERDICT: REFUTED làm công cụ xác suất/forecast.** Spread fwd60 (panic-decile0 − euphoria-decile9): IS **+1.44pp** (contrarian yếu) → OOS **−2.85pp** (procyclical) — **ĐẢO DẤU IS→OOS**. Spearman IC mood→fwd20: IS −0.111 → OOS +0.061 (đảo dấu); mood→fwd60: IS −0.009 → OOS +0.129. Non-overlap (mỗi 60 phiên): IC không significant cả 2 kỳ (p=0.46/0.65). Decile-profile stability IS-vs-OOS: ρ=+0.32, p=0.365 — KHÔNG ổn định.
- Đặc điểm sống sót duy nhất: hình chữ U — deep-panic decile 0 bounce (+4.5% IS/+4.95% OOS fwd60) và euphoria decile 9 persist (+3.1% IS/+7.8% OOS). Nghĩa là mood cực đoan KHÔNG cho biết HƯỚNG một cách nhất quán (panic sâu = bounce, panic vừa = decile TỆ NHẤT OOS −1.51%); claim AMH "uniformity precedes reversal" bị bác trên VN 2020+.
- Độ nhạy hiện tại: mood 07-10 = **−1.38**, chỉ cách edge decile0/1 (−1.312) đúng 0.07 điểm — lệch 1 sáng là "historical read" nhảy từ +5% (bounce) sang −1.5% (worst) → minh chứng không dùng làm số xác suất cho user quyết định.
**P(NEUTRAL→BEAR/CRISIS trong N phiên) — DT5G live refresh tới 2026-07-09 (49 transitions):** FULL 2014+: **11.8%/20p, 21.0%/40p, 30.9%/60p** (n=1.871/1.851/1.831 ngày-obs; số cũ job 113818: 12.3/21.6/31.1 — trôi nhẹ, cùng bức tranh). 2020+: **11.4%/15.8%/21.8%**. Điều kiện hoá mô tả (descriptive, KHÔNG pre-registered làm rule): NEUTRAL & breadth200≤0.35 (đúng hiện trạng 28.6%): 28.7%/36.9%/41.4% (n=150/130/116 ngày-obs, CỤM vào ít episode); NEUTRAL & run≥90 phiên (hiện tại run 97): 21.1%/38.6%/51.8% — nhưng effective n chỉ **9 run hoàn tất** (7/9 kết thúc xuống BEAR/CRISIS, tập trung 2014-19; 2020+ chỉ 2 run hoàn tất: 2023→CRISIS, 2024-25→BULL = 1/2). Các con số điều kiện là TẦN SUẤT LỊCH SỬ mẫu nhỏ, không phải xác suất dự báo có kiểm định.
**Khuyến nghị (câu 4 dispatch): KHÔNG đưa vào dna_report như "xác suất tham khảo".** Lý do: (1) ecology mood REFUTED walk-forward (đảo dấu IS→OOS — đúng quy chuẩn "rớt OOS = loại"); (2) P-hit-bear là BASE RATE lịch sử của chính DT5G, không phải forecast độc lập — trình bày như xác suất dự báo sẽ lặp bài học "insurance ≠ return-enhancer"; số có ý nghĩa quyết định đã nằm trong DT5G state (production gate). Nếu user vẫn muốn 1 dòng context: chỉ dòng base-rate unconditional (11.8%/20p full-sample) với nhãn rõ "tần suất lịch sử, không phải dự báo" — cần user duyệt riêng, không tự wire.
**Hiện trạng 2026-07-10 (descriptive, causal):** breadth 29% >MA200 / 29% >MA50 (n=192), opportunity pctile 20% (CROWDED/macro-driven), uniformity 61%, mood −1.38 (pctile 9.3% expanding = vùng panic nhưng CHƯA extreme-tail), divergence flag ON (index +60d nhưng breadth 29%). DT5G vẫn NEUTRAL, run 97 phiên.
**Phát hiện phụ:** `tav2_bq.vnindex_5state_dt5g_live` max(time)=**2026-07-09** — thiếu phiên 07-10, khớp chữ ký bug C1 (publish đọc qua BQ_LOCAL_CACHE=T-1) vì fix `4995262` commit 07-12 SAU lần chạy thứ Sáu; cron 18:30 ICT 07-13 với fix sẽ tự recompute (đúng checklist đang chờ) — cần xác nhận tối nay có cả dòng 07-10 VÀ 07-13.
**Files:** `mike/agents/Taylor/ecology_wf_validation_20260713.py` (script tái lập), `data/ecology_dashboard.csv`/`data/ecology_now.md` (refresh 07-10). Self-check: không có NAV sim (nghiên cứu thống kê, 0-VND không áp dụng); recompute độc lập mood từ panel CSV khớp dashboard. Production/paper/trading_rules KHÔNG đụng.

## 2026-07-13 — DEAL QUALITY SCORE 2-TRỤC (self-referential × cross-sectional) — job Taylor_20260713_092636 — NGHIÊN CỨU + 1 DISPLAY FIX, production/paper KHÔNG đụng
**Câu hỏi user (qua Mike):** STRONG của sector-lens chỉ đo "rẻ so với chính nó" — làm sao biết deal nào rẻ-so-với-thị-trường? Watchlist "20 chỉ báo rời rạc, không so sánh chéo được". Kiểm chứng: (1) cơ chế ✓✓ double-confirm hiện có đã giải quyết chưa; (2) composite 2-trục liên tục có dự báo tốt hơn 1 trục không (thực nghiệm).
**Việc 1 — XÁC NHẬN cơ chế ✓✓:** CTR 2026-07-13 = BUY·STRONG (EVEB 8.86<9) + 8L rating **2** → **CÓ ✓✓ thật** (không phải STRONG đơn thuần). FPT STRONG cũng R2 ✓✓. Cơ chế double-confirm (job Taylor_20260706_082923) ĐÚNG là giải pháp 2-trục user cần — nhưng display cũ để STRONG-không-✓✓ hiện trần (chỉ có tag "R4" không giải thích), user phải tự suy luận. **Đã fix display** (`sector_lens_monitor.py`): STRONG thiếu ✓✓ giờ in rõ "⚠️ rẻ vs chính nó, CHƯA xác nhận rẻ vs thị trường (8L rating 3-5)"; footer ghi số backtest. Self-check render PASS (telegram + discord `newdeals_daily_report._html_to_discord`, synthetic CTR-R4 mang warning, CTR thật R2 không mang).
**Việc 2+3 — BACKTEST composite (script `mike/agents/Taylor/deal_quality_score_backtest.py`, family pre-declared N=4 score × 2 horizon, KHÔNG sweep thêm):** trục A = 1 − percentile 3Y lịch sử riêng mã của metric lens (PB bank/sec, PE tech/textile/pharma, EVEB logistics/CTR; weekly, causal, min 52w). Trục B = percent-rank cross-sectional value composite (mean pctrank(1/PE), pctrank(1/PCF)) trong universe thanh khoản ≥1tỷ/ngày (PS không có trong daily cache — B = 2/3 trục value 8L, đã ghi chú). Population: pooled quality-gated 6 ICB + CTR, 84 mã, N=14.785 weekly obs 2014-2026, corr(A,B)=0.23 (2 trục gần trực giao — đo 2 thứ khác nhau thật). profit_1M/3M EVAL-ONLY.
- **Composite liên tục (MEAN/PROD): KHÔNG thắng rõ — FAIL tiêu chí pre-declared.** OOS per-date Spearman IC: B-alone 0.1024 (1M) / 0.1618 (3M) > MEAN 0.0797/0.1358 > PROD > A-alone 0.0272 (1M). Q5-Q1 OOS: 1M B 2.48pp > MEAN 1.95pp; 3M MEAN 6.02pp vs B 5.49pp (thắng đúng 1/4 cell — không đủ). Trục cross-sectional B là trục mạnh nhất đứng riêng (nhất quán "1/PE dominant, IC +0.125" của 8L) → KHÔNG wire điểm số DQS liên tục mới.
- **Binary BOTH-extreme (= chính cơ chế ✓✓): THẮNG RÕ ở đuôi phân phối.** OOS 2020-26 (A≥0.8 ∧ B≥0.8): fwd-1M **+5.63% hit 69%** vs A-only +2.61%/hit 60%, B-only +3.70%/hit 55%; fwd-3M **+16.67% hit 74%** vs +9.61%/+7.50%, neither +5.11%. n=276 weekly obs / **19 mã / 32 episode độc lập (gap>90d) / trải 5 năm OOS**; LOO bỏ từng năm: 3M vẫn +11.7…+20.4% (không carry bởi 1 năm; 2020 lớn nhất +40.7% nhưng ex-2020 vẫn +11.7%).
- **Caveat khai báo:** (i) IS 2014-19 bucket BOTH chỉ n=8 (điều kiện both-extreme gần như không tồn tại pre-2020 trong pool này) → edge OOS-loaded, đúng character đã biết của sector-lens, chấp nhận được cho watchlist display (không phải sổ tự động); (ii) trục A dùng proxy percentile-3Y, không phải đúng từng công thức STRONG per-lens; (iii) fwd-return weekly vẫn overlap (1M ~4x) → hit-rate không phải i.i.d., đọc là descriptive; (iv) BOTH bucket nghiêng Banking (192/276) theo cấu trúc pool.
**Việc 4 — VERDICT: KHÔNG wire composite liên tục** (thua B-alone trên IC giữa-phân-phối); **giữ ✓✓ nhị phân — giờ có backtest chứng minh trực tiếp** (trước đây ✓✓ chỉ là consensus 2 hệ chưa đo). Trả lời câu "deal hời nhất hôm nay xuyên sector": nhìn tầng ✓✓ trước (đã so-sánh-được xuyên sector vì rating 8L là rank toàn thị trường), trong tầng ✓✓ dùng 8L rating rồi mode STRONG làm tie-break — KHÔNG cần điểm số mới.
**Self-check:** không có NAV sim (0-VND n/a — nghiên cứu IC/quintile thuần); toàn bộ IC/quintile/LOO recompute độc lập từ obs CSV persisted (`dqs_backtest_obs.csv`) khớp print. **Files:** `mike/agents/Taylor/deal_quality_score_backtest.py`, `mike/agents/Taylor/dqs_backtest_obs.csv`, display fix `sector_lens_monitor.py` (repo thanhdt). Chờ quant-skeptic phản biện (Mike dispatch) — display fix vô hại production (watchlist tham khảo, không phải money-path).

## 2026-07-13 — ✓✓ DOUBLE-CONFIRM EXPLOITATION AUDIT (5 góc) + TRIGGER-GAP BACKTEST — job Taylor_20260713_100550 — RESEARCH-ONLY, production/paper KHÔNG đụng
**Câu hỏi (user qua Mike):** Waterfall DC-book đang paper đã khai thác HIỆU QUẢ cơ chế ✓✓ (vừa được backtest
xác nhận OOS fwd-3M +16.67%/hit 74%, job _092636) chưa? Còn không gian nào tận dụng tốt hơn?
**Bước 1 — trạng thái paper vs các tinh chỉnh đã nghiên cứu:** paper sleeve (`dc_book_waterfall_paper.py`,
chạy từ 2026-06-26) vẫn là BẢN GỐC: daily signal-driven, cap 0.20/tên, hard-exclude DHG, KHÔNG cap gộp 0.15,
KHÔNG floor 3B, KHÔNG q2m5 — đúng ràng buộc "không đổi giữa trial"; 3 tinh chỉnh (q2m5 thống nhất / cap gộp
0.15 / floor 3B, job _173317+_042827) vẫn là agenda-items cho mốc review event-anchored, chưa wire đâu cả.
**Bước 2 — 5 góc (descriptive từ R3 audit `h3_baseline_R3.csv` + panel `dc_dbl_panel.csv`, single-cache):**
1. **Sizing/depth-weight: KHÔNG còn không gian** — đã bị bác 2 lần độc lập (tilt STRONG 1.5× kém EW, job
   _093329 §4; DQS composite liên tục FAIL vs binary, job _092636). Không test lần 3 cùng giả thuyết.
2. **✓✓ làm tiebreaker/boost trong core BAL/LAG: KHÔNG có bề mặt** — đo thật: BAL 2047 entries chỉ 53 (2.6%)
   thuộc universe lens 16 tên, chỉ **8 (0.39%)** có ✓✓ ON tại entry; LAG 5360 entries → 9 (0.17%). Ràng buộc
   là COVERAGE lens (16 tên) chứ không phải priority; mở rộng lens = chương trình sector-sweep riêng (sweeps
   #1-9 đã kết luận lens = tilt, không standalone).
3. **CRISIS/BEAR coverage: có tín hiệu (618 ngày ✓✓, 16 block 2015-2024) nhưng KHÔNG test** — production cố ý
   giữ cash ở đó (insurance mandate); bài học state-gate §8.3-8.4 (mean-reversion book trong washout); CAPIT
   gated-overflow đã chiếm slot bear-washout mà chỉ có 18 event lịch sử → ✓✓-filter cho CAPIT không đủ power
   cho wire-decision. Để lại như observation, không mở trial.
4. **Sector-lens standalone cho core books: KHÔNG** — DQS đã trả lời: trục A (self-referential lens) IC 1M
   chỉ 0.027 đứng riêng; sức mạnh nằm ở AND-tail với 8L. Không test thêm.
5. **Chi phí cơ hội + TRIGGER GAP (phát hiện chính):** ✓✓ tồn tại 71.8% ngày NEUTRAL (1373/1912). Trigger
   binary của paper (`bal_lag_has_deal` → sleeve FLAT toàn phần) khác HẲN spec overlay đã backtest & pin
   (DC chạy liên tục trên phần tiền park): 57.8% ngày NEUTRAL-có-✓✓ có deal BAL/LAG mới (proxy TX-buy;
   n_lag_upcoming thực còn fire sớm hơn → số thực CAO hơn), tiền park những ngày đó vẫn ~38% NAV → paper
   bỏ **53.1% capital-days** so spec, kèm ~31 vòng whipsaw/năm.
**Bước 3 — backtest trigger-gap (N khai báo = 2: binary+TC, binary-noTC; script `dc_trigger_gap_backtest.py`,
output `data/dc_trigger_gap_output.txt`; self-check A identity 0 VND PASS, self-check C continuous tái lập
CÂU 0 chính xác 27.56/1.77; deal-day proxy lạc quan cho binary; flat modeled = park về custom30V — nếu flat
= cash thật như paper accounting thì binary còn tệ hơn):**
| config (full-NAV overlay R3 @50B, single-cache 07-07) | FULL | IS | OOS | MaxDD | Calmar | turn sleeve |
|---|---|---|---|---|---|---|
| R3 baseline (custom30V parking) | 27.35% | 26.75% | 27.94% | −17.6% | 1.55 | ~0 |
| **CONTINUOUS spec (đã pin, job _173317)** | **27.56%** | 26.55% | 28.54% | **−15.5%** | **1.77** | 3.18×/yr |
| **BINARY trigger (paper wire) +whipsawTC** | **27.26%** | 26.61% | 27.89% | **−17.8%** | **1.53** | **20.72×/yr** |
| BINARY noTC (diagnostic) | 28.00% | 26.93% | 29.03% | −17.5% | 1.60 | — |
**Đọc:** binary-với-TC THUA CẢ BASELINE mọi metric (edge-capture = **−43%**); riêng whipsaw TC ăn 0.74pp/yr.
Kể cả miễn phí giao dịch, binary vẫn mất sạch cải thiện DD/Calmar (−17.5/1.60 vs −15.5/1.77) — mà DD/Calmar
chính là value proposition đã pin của waterfall (CAGR chỉ +0.19pp, DSR 0.111 insurance-grade). Per-year:
continuous thắng binary 2023/2024/2025 (+1.5/+1.9/+3.2pp) — các năm deal-flow dày.
**Bước 4 — VERDICT: paper sleeve hiện tại KHÔNG khai thác hiệu quả cơ chế ✓✓ — không phải vì thiếu ý tưởng
tín hiệu mới, mà vì TRIGGER BINARY under-implement chính spec đã backtest.** Nếu wire live nguyên trạng
trigger này = net-ÂM vs parking thường. 4 góc "ý tưởng mới" còn lại đều KHÔNG có không gian thật (đã bác/
không bề mặt/không power). **Đề xuất cho mốc review event-anchored (~sau LAG refill + settle):** gói wire
ĐÚNG SPEC gồm (1) **trigger continuous-residual** (DC nhận phần idle-cash còn lại sau BAL/LAG lấy phần của
mình, không all-or-nothing) — đây là fix quan trọng nhất, (2) refresh q2m5 thống nhất (turnover 3.18→0.76×,
tự giảm luôn whipsaw), (3) cap gộp 0.15 + floor 3B (risk-control đã đo job _042827). Paper trial hiện tại
GIỮ NGUYÊN chạy tới review — chính cửa sổ LAG-refill sắp tới sẽ phô bày hành vi whipsaw của trigger binary
trên dữ liệu sống, đúng thứ mốc review event-anchored cần quan sát. KHÔNG wire gì bây giờ; DSR mechanism
không đổi (0.775 sleeve / 0.111 full-NAV — insurance, không phải alpha).
**Files:** `dc_trigger_gap_backtest.py`, `data/dc_trigger_gap_output.txt`. N-ledger job này: 2/2 đóng.

## 2026-07-13 — BETA-CAP custom30V (câu hỏi VIX của user): NO-GO cả 2 config, kể cả bản CÓ ĐIỀU KIỆN macro-phòng-thủ (job Taylor_20260713_114905)

**Câu hỏi user:** VIX (Chứng khoán VIX) nằm trong custom30V, beta cao/đầu cơ — khi vĩ mô nghiêng
phòng thủ (lãi suất huy động tăng, CPI tăng, thanh khoản giảm, dù DT5G vẫn NEUTRAL) có nên hạn
chế mã beta cao trong rổ không?

**Premise vĩ mô — CẢ 3 dấu hiệu user nêu ĐỀU CÓ THẬT (verify dữ liệu, không phải cảm nhận):**
- Deposit 12M Big-4 proxy (`deposit_rate_vn.DEPOSIT_EVENTS`): đáy 4.7% (04/2024) → 6.0% (01/2026)
  → **6.8% (06/2026)** — tăng +2.1pp từ đáy, ĐANG TIẾN GẦN floor 7.5% của deposit-gate RECOVERY_PARK
  (dormant từ 2013; nếu vượt 7.5% lần đầu tiên trong kỷ nguyên DT5G, gate tự vũ trang — đúng thiết kế).
  ⚠️ proxy best-estimate, không phải series chính thức.
- CPI YoY (NSO real, `cpi_vn.NSO_CPI_YOY_REAL`): 3.48% (12/2025) → đỉnh **5.60% (05/2026)** → 4.69%
  (06/2026) — tăng thật, tháng 6 hạ nhiệt nhẹ.
- Thanh khoản (ticker_prune, GTGD bình quân ngày): ~38-54T VND/ngày (07-08/2025) → **~16T (06-07/2026)**
  — giảm ~55-70% từ đỉnh.
- DT5G vẫn NEUTRAL(3) vì: Pillar A đọc REFI SBV (4.5% không đổi từ 06/2023 — SBV chưa nâng lãi điều
  hành, chỉ lãi huy động NHTM tăng); re-risk/de-risk theo GIÁ qua DT base. Không phải hệ "mù" — là
  thiết kế cap-only + price-based đã audit (DT5G = insurance).

**VIX beta — xác nhận:** realized beta 2Y = **1.50, #2/30 trong rổ** (sau SHS 1.61; MBS 1.46, VND
1.30 — cả 4 mã brokerage đều top-5 beta). `risk_rating` 2025Q4: Beta bin 5/5, Risk_Rating 4. VIX
nằm trong danh sách known-bad-IntCov của brokerage sweep (registry ~L1000) — đúng, không đổi, nhưng
đó là context screen brokerage (IntCov NULL-tolerant), không phải tiêu chí custom30V. Rổ mean beta
1.05 / median 0.99. custom30V **beta-blind by design** (`custom_basket.py` yieldcombo: liquidity
gate + rating≤3 + rank(1/PE)+rank(1/PCF), không có trục risk nào).

**Probe pre-registered N=2 (`probe_beta_cap_c30v.py`), cùng harness/PIT với H1/H6a (47 quý,
fwd profit_2M, top-30 yieldcombo từ pool top-60 liquid gate≤3, beta bin PRIOR-quarter causal):**
| config | mean2M% | vs base | IS(14-19) | OOS(20+) | win%q | avg_drop |
|---|---|---|---|---|---|---|
| base | 3.80 | — | 1.56 | 5.78 | — | 0 |
| EXCL-B5 vô điều kiện | 2.69 | **−1.11** | 0.92 | 4.26 | 28% | 15.1 |
| EXCL-B5 chỉ quý phòng-thủ* | 3.68 | **−0.12** | 1.35 | 5.74 | 85%† | 3.1 |

\* quý phòng-thủ = deposit 6m-momentum >+0.25pp (causal): 9/47 quý — 2017Q1-Q2, 2018Q1-Q2, 2022Q4,
2023Q1, 2025Q3-2026Q1 (bao gồm đúng giai đoạn hiện tại). † 85% là tie-inflated (38/47 quý identical);
trong 9 quý khác biệt: thua 6/9.
**FAIL cả 2 theo gate khai báo trước (≥base ở CẢ IS lẫn OOS).** Per-year của bản có-điều-kiện:
2017 −0.39 / 2018 −0.78 / **2022Q4 −0.67 (đúng bear lãi-tăng thật cũng THUA)** / 2023 +0.22 /
2025 +0.28 / 2026 −0.20. Cơ chế thua 2022Q4: lúc macro đã xấu rõ thì mã beta-5 ĐÃ rẻ sẵn — loại
chúng là bỏ lỡ rebound, đúng lời nguyền "de-risk theo macro chậm hơn giá". Cùng chữ ký fail với
H1 (FSCORE-excl) và H6a (MAX5 lottery-excl + soft-penalty): pool cô đặc, exclusion co pool →
substitute value kém hơn → dilute.

**Trả lời 3 câu:** (a) premise vĩ mô user ĐÚNG cả 3 dấu hiệu; (b) VIX/beta cao trong custom30V
KHÔNG phải vấn đề cần sửa ở tầng chọn mã — rủi ro beta đã được xử lý ở TẦNG SLEEVE: custom30V là
NEUTRAL-parking vehicle, DT5G chuyển BEAR/CRISIS → exposure về 20%/0% (cả rổ unwind); brokerage
sweep đã chứng minh DT5G gate chính là cơ chế đúng cho sector beta cao (17.74→27.74% CAGR); thêm
deposit-gate floor 7.5% đã wire sẵn làm bảo hiểm trục lãi suất, hiện 6.8% chưa chạm; (c) KHÔNG đề
xuất sửa gì — beta-cap cả vô điều kiện lẫn có điều kiện đều bị số đo bác. Đề xuất phụ DUY NHẤT
(không phải code): theo dõi deposit proxy tiến về 7.5% — nếu vượt, deposit-gate tự vũ trang lần
đầu kể từ 2013, và đó là tin ĐÁNG BÁO macro-view chứ không phải lý do override tay.

**N-ledger job này: 2/2 đóng.** Files: `probe_beta_cap_c30v.py` (repo root). KHÔNG đụng
production/paper. AUDIT date 2026-07-13, panel `value_panel_2014.csv` frozen, BQ_CACHE_THREADS=1,
beta PIT prior-quarter, không dùng profit_* làm filter.

---

## 2026-07-13 — DEPOSIT-RATE-GATE variant D0 (real-premium): **NO-GO** (đúng kỳ vọng pre-registered)
> Job `Taylor_20260713_141712` (tiếp `_131230`). Plan + kết quả đầy đủ: `mike/agents/Taylor/plan_deposit_rate_signal_20260713.md` §10 (family N=6 đóng sổ; D0 tiêu 1/6). quant-skeptic: PENDING (để bước sau theo dispatch).

- **Lệnh**: lệnh pin R3 nguyên văn (`BQ_LOCAL_CACHE=data/bq_cache BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" AUDIT_END=2026-06-19 $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge`) + state-view swap in-process (DuckDB) sang overlay `min(published_DT5G, commit(dep_cap,7))`, input `rp_chg6m = 6m-chg(deposit_Big4 − CPI_yoy shifted M+1)`, lag 5, ngưỡng mượn Pillar A {0.5/1.5/3.0}. `EXP_TAG=depgate_D0|control` — không đè canonical (§8).
- **Số** (self-check 0 VND cả 2 run; recompute `extract_peryear.py` + DAILY-rows khớp chính xác):

| Run | FULL | Sharpe | MaxDD | Calmar | IS | OOS |
|---|---|---|---|---|---|---|
| control same-vintage | 27.11% | 1.81 | −18.3% | 1.48 | 23.37% | 30.61% |
| D0 real-premium | 22.05% | 1.57 | −18.4% | 1.20 | 19.64% | 24.27% |
| **delta** | **−5.06pp** | −0.24 | −0.1 | −0.28 | −3.73pp | −6.34pp |

- **Event-audit**: 8 episode / 358 phiên deviate, **100% Pillar-A-im (incremental = phần sai)**; fwd T+60 sau de-risk trung bình **+3.3%** (de-risk vào lúc thị trường khỏe); cú đắt nhất 2020-08→2021-04 cap BEAR 169 phiên xuyên mega-rally = −30.2pp sleeve; **zero deviation trong 2022** (im đúng cửa sổ cần fire). Gate: **N2 auto-NO-GO** + G1 fail (−5.06pp) + G2 fail. Benign-identity PASS (NAV byte-identical 839 phiên tới đúng phiên deviate đầu 2017-05-24).
- **Caveat**: control ≠ pin R3 27.84 (−0.73pp) = mutation as-of (fa_ratings/fa_ratings_8l re-rank 07-12, custom30v_8l republish daily, DT5G re-publish sau EW-leg fix, cache full_only 07-13) — đúng lớp registry quy tắc #3; ablation same-vintage nên delta sạch, verdict bền.
- **Kết luận cơ chế**: trừ CPI khỏi deposit làm tín hiệu TỆ ĐI cả 2 đầu (thêm false-positive disinflation-bull 2017/2019/2020-21/2025, xóa true-positive 2022 khi CPI tăng cùng nhịp rate). Đóng dứt điểm hướng real-premium. Winner nếu có chọn trong {D1,D2,D3} (job song song).

## 2026-07-13 — DEPOSIT-RATE-GATE D1/D2/D3: **NO-GO CẢ 3 → family 0/4 GO, ĐÓNG HƯỚNG B (không shadow-monitor)**
- **Job**: `Taylor_20260713_145605` (family pre-registered `plan_deposit_rate_signal_20260713.md` §4, kết quả đầy đủ §11). Control same-vintage, KHÔNG đè canonical, self-check 0 VND mọi run.
- **⚠️ PHÁT HIỆN HARNESS (áp dụng mọi experiment view-swap `pt_v23_audit_2014.py` từ nay)**: sizing tie-break theo row-order query; DuckDB đổi row-order theo NỘI DUNG parquet swap → NAV lệch từ 2018 giữa 2 run state-identical-tới-2023 (~±0.5pp noise, MWG/PLX swap buy_amount). **Fix: stable-sort (time,ticker) trên BQLocalCache.query** (`run_depgate_variant_sorted.py`) + determinism-pair control (ctlSa≡ctlSb md5 `f4421a17...`). Delta <±0.5pp từ run view-swap KHÔNG sort = vô nghĩa. Pin canonical KHÔNG ảnh hưởng (không swap view); drift control-sorted vs pin chỉ −0.19pp (mutation as-of).
- **Số (sorted, chính thức)**: control 27.65/1.83/−18.3/1.51 (IS 23.37/OOS 31.70); D1 +0.17pp FULL, D2 +0.19pp, D3 −0.02pp; IS identical 23.37 cả 4 (dormant). Benign identity: D1/D2 trùng NAV 2.267 phiên tới đúng 2023-02-07, D3 3.012 phiên tới đúng 2026-01-28.
- **Verdict**: D1/D2 NO-GO ở **N1** (toàn bộ phần thắng = 2023-02→04 nơi Pillar A active/redundant 100%, nằm trong cửa sổ loại trừ; episode ngoài cửa sổ sleeve −1.29/−0.92pp) + G2/G3/G4 fail. D3 NO-GO ở **G2** (incremental thuần = 2 episode chu kỳ 2025-26, cả 2 tốn tiền −1.29pp, VNINDEX fwd60 DƯƠNG sau de-risk; ep 2026-06 truncated/đang diễn ra). **2017 false-positive KHÔNG bind** (fire 126 phiên nhưng DT5G published NEUTRAL cả năm → tier mild cap-NEUTRAL gần như vô hiệu lịch sử; dự đoán N2 pre-registered sai theo hướng informative). DSR non-informative (deviate 30-70 phiên) — khai báo trước, không ép số.
- **Treo**: G5 quant-skeptic verify CẢ CỤM D0-D3 một lần (artifacts `mike/agents/Taylor/exp_depgate/`).

## 2026-07-14 — DIVIDEND_MIN3Y (event-based, VCI ex-dates) → 8L value lens — job Taylor_20260714_033021 — GO opt-in (VALUE_VERSION=v3_div), DIAGNOSTIC-ONLY, production/paper KHÔNG đụng
**Câu hỏi user:** BQ có field cổ tức mới (event-based Dividend_Min3Y, phủ +~45%) — có giúp 8L đánh giá từng cổ phiếu tốt hơn không?
**Verdict: CÓ, tích hợp làm value-LENS opt-in (KHÔNG phải gate). Zero NAV impact (giống D&A_HEAVY).**

Artifacts: `dividend_upgrade_test.py` (repo root), panel `mike/agents/Taylor/exp_dividend/panel_monthly.csv`
(36,408 rows, ticker_prune 2014-01→2026-06, point-in-time monthly, Dividend_Min3Y as-of mỗi ngày), `ic_table.csv`.
Interpreter: `/home/trido/thanhdt/wc_venv/bin/python`. Forward cols profit_1M/2M/3M = TRAINING/eval-only (đúng phép dùng cho IC).

**1. Coverage (monthly panel):** DY_old>0 = **26.9%** → Dividend_Min3Y usable (payer+non-payer=0) = **98.2%** (div>0 60.9%, =0 36.7%, null 1.8%). Con số "+45%" của dispatch thực ra UNDERSTATE.
  - ⚠️ Đính chính quan trọng: so với legacy financial-estimate `Dividend_Min3Y_fin` (BQ), event-based khác biệt LEVEL ~0 (median rel-diff 0%, mean 0.4%), và _fin còn phủ nhỉnh hơn (1283 vs 1190 tên latest-Q). Cú nhảy 27→98% là do đổi sang DẠNG min-3Y dày (thay field DY điểm sparse), + độ chính xác point-in-time ex-date cho backtest — KHÔNG phải coverage/level thắng lớn so _fin.

**2. IC (cross-sectional Spearman, per-date avg, IS 2014-19 / OOS 2020-26):**
| signal (vs profit_3M) | IS_IC (t) | OOS_IC (t) | sign-stable? |
|---|---|---|---|
| real_dy = Dividend_Min3Y/Price | +0.033 (2.6) | +0.055 (2.8) | ✅ dương cả 2 |
| DY_old (field cũ, đã bị bác) | **−0.061 (−4.0)** | +0.029 (2.4) | ❌ SIGN-FLIP (lý do bị loại trước) |
  → Data mới BIẾN 1 tín hiệu sign-unstable (đã reject) THÀNH sign-stable dương. Đây là câu trả lời trực tiếp "data mới có giúp không": CÓ.

**3. Orthogonality vs 1/PE (earn_yield, factor value trội):** xsec rank-corr = **0.18** (gần orthogonal). Residual IC của real_dy sau khi neutralize earn_yield: **+0.031 IS (t2.4) / +0.030 OOS (t1.7)** vs profit_3M → thêm info thật, không redundant.

**4. Weight sweep (composite ey+w·div, IC vs profit_3M):** PARETO improvement — IS +0.0096→+0.016, OOS +0.1057→+0.110 (CẢ 2 tăng, no OOS dilution tới ~w0.35; w0.50 mới bắt đầu loãng OOS). Chọn **w=0.15** (an toàn giữa dải).

**5. Golden-floor GATE test = NEGATIVE (không nới rule 'DY chỉ bonus, không gate'):** golden & payer vs golden & NON-payer, mean fwd-3M gần bằng nhau (OOS 4.21 vs 4.35 — non-payer còn NHỈNH hơn); payer chỉ hơn nhẹ win-rate (53.4 vs 50.6%) + tail p10 (−18.0 vs −22.4). ⇒ đòi track-record cổ tức 3Y KHÔNG add cho ROE_Min3Y≥0 & CF_OA_3Y>0. Giữ là LENS, tuyệt đối KHÔNG làm hard gate.

**6. Bản chất = QUALITY/STABILITY proxy, không phải timing:** div_payer persistence m/m **99.1%**, real_dy autocorr **0.963** — đặc trưng chậm/bền, đúng giả thuyết dispatch. SOE caveat (VEA/QTP/SJD/TVD/IDC top-yield, cổ tức theo chính sách nhà nước) có thật nhưng IC tổng vẫn dương sign-stable + chỉ là lens 0.15 trên value axis (bị pha loãng), không đủ để bác.

**Implementation (rating_8l.py, opt-in):** `VALUE_VERSION=v3_div` = SUPERSET của v3_da (giữ nguyên D&A_HEAVY/POWER+EVEB) + lens div_yield (Dividend_Min3Y/Price, coverage-aware, non-payer→div_rank thấp nhất, truly-missing→NaN). Per-route weight 0.15 (CYCLICAL=0). Default GIỮ v3_da tới khi user duyệt.
**🐛 BUG BẮT ĐƯỢC + FIX (nhờ verify, không tin comment):** phiên trước để sót — dòng gán value_score gate ở `VALUE_VERSION in ("v3","v3_da")` BỎ SÓT "v3_div" → v3_div âm thầm fallback về value_score_v2 (60/61 tên v3-route), lens cổ tức bị VỨT. Fixed (thêm "v3_div"). Sau fix: value_score==value_score_v3 cho 61/61.
**Self-check (giống promotion D&A_HEAVY):** rating(1-5) v3_da vs v3_div **BYTE-IDENTICAL 0/107** → value-axis ONLY, production selectors (custom30V/BAL/LAG) đọc gate_rating≤3 off rating → **ZERO NAV impact**. Default v3_da vs backup trước-đổi: rating 0/785 khác. Div lens dịch value_score 46/107 (max|Δ|0.091), zone shift 22/107 — vừa phải, đúng lens 0.15.
**Không backtest CAGR/Sharpe** vì (như D&A_HEAVY) selector không đọc value_score — đây là trục rating/diagnostic. Muốn wire vào selector là quyết định KHÁC, cần N-budget + backtest riêng.

## 2026-07-14 — PROMOTE VALUE_VERSION=v3_div → DEFAULT (thay v3_da) — job Taylor_20260714_040245 — user-approved, DIAGNOSTIC-ONLY, ZERO NAV impact
**Bối cảnh:** tiếp nối verify job Taylor_20260714_033021 (v3_div = superset v3_da + lens Dividend_Min3Y event-based, IC dương sign-stable IS+OOS, orthogonal 1/PE). User duyệt promote thành default (giống quy trình promote v3_da 2026-07-04).
**Thay đổi code (`rating_8l.py`, commit — xem git):**
1. Default `os.environ.get("VALUE_VERSION", "v3_da")` → `"v3_div"`. v3_da/v3/v2 vẫn chạy được qua env var (rollback: `VALUE_VERSION=v3_da python rating_8l.py`).
2. Docstring cập nhật (v3_div là default từ 2026-07-14, lý do + rollback).

**🐛 BUG THỨ HAI BẮT ĐƯỢC KHI PROMOTE (cùng lớp với bug line-755 phiên trước, verify không tin comment):** golden-cell FLOOR ở `if VALUE_VERSION in ("v3","v3_da"):` **BỎ SÓT "v3_div"** → dưới v3_div golden floor **KHÔNG fire** (BUY-NOW rơi 46→32, 14 dislocation VCB/BID/SAB/ACV/VNM/FPT/CTR/VGC/REE/CMG/TV2/VSC/DGC/SZC mất floor). Nếu promote nguyên trạng = âm thầm ship regression. **Fixed:** thêm "v3_div" (v3_div là SUPERSET của v3_da nên PHẢI kế thừa golden floor). Sau fix: golden floor fire dưới v3_div = 15 tên (thêm LCG — value_score của LCG bị div-lens hạ nên rơi khỏi BUY-NOW rồi được floor lại; zone cuối vẫn BUY-NOW như v3_da, không phải diff thật).
  ⚠️ **Đính chính số phiên trước:** job 033021 báo "zone shift 22/107" — con số đó BỊ NHIỄM bởi golden-floor bug (14 tên mất floor lẫn vào). Sau khi fix line-783, **zone shift thật của div-lens = 7/107** (golden floor fire cả 2 phía, chỉ còn hiệu ứng lens thuần).

**Self-check (fresh live snapshot, 785 rated / 107 investable, interpreter `/home/trido/thanhdt/wc_venv/bin/python`):**
- **rating (1-5): 0/785 khác** ở CẢ 3 cặp: v3_da-vs-v3_div, default-vs-v3_div, default-vs-ORIG(old v3_da default) → **value-axis ONLY**. Production selectors (custom30V/BAL/LAG) đọc gate_rating≤3 off `tav2_bq.fa_ratings_8l.rating`, KHÔNG đọc value_score/zone → **ZERO NAV impact** (đường tiền không đổi 1 đồng).
- **flip xác nhận:** chạy no-env in `[VALUE_VERSION=v3_div]` + golden floor 15 (== explicit v3_div). rollback `VALUE_VERSION=v3_da` in `[VALUE_VERSION=v3_da]` + golden floor 14 (khớp trước-đổi). v3 (floor 14) / v2 (no floor) smoke exit 0.
- **phạm vi div-lens:** value_score re-weight 48/107 tên (max|Δ|0.091) — khớp ~46/107 job trước (chênh 2 = live-snapshot jitter, value_score là composite không do golden floor); zone shift **7/107** (đã sửa, sạch): CTI/VGT/MWG hạ (yield thấp), SHS/DCM/VEA/OIL firm-up (payer) — hợp lý, đúng lens 0.15 coverage-aware.
**Rollback:** `VALUE_VERSION=v3_da python rating_8l.py` (== hành vi cũ trước promote). **Không backtest CAGR/Sharpe** — selector không đọc value_score (trục rating/diagnostic), wire vào selector là quyết định KHÁC cần N-budget riêng.

## 2026-07-14 — DCF ABSOLUTE-VALUATION LENS (2-stage FCFE, VN non-financial) — jobs Taylor_20260714_042622 (build) → _051643 (finish) — RESEARCH TOOL, NOT wired to production
**What:** new absolute intrinsic-value lens complementing the 8L *relative* lenses (PE-vs-history, PB-vs-Gordon, EVEB). Files: `dcf_valuation.py` (model+CLI), `dcf_backtest.py` (2 studies), FV cache `mike/agents/Taylor/dcf_exp/fv_releases.parquet`, run log `dcf_exp/backtest_run.log`, framework `mike/agents/Taylor/dcf_valuation_framework.md`. **No production/trading_rules/allocator/rating_8l touched.**
**Model:** FCFE proxy = CF_OA+CF_Invest (base = norm 3y-avg (CF_OA_3Y+CF_Invest_3Y)/3). r = Big-4 12M deposit (deposit_rate_vn) + ERP 6.5% = 13.30% today. g_term = 5y-avg CPI (cpi_vn) = 3.40%. g_explicit = g_term + 0.50·(g_trailing−g_term), clamp [−2%,+20%]. Gates: exclude financials, CF_OA_3Y>0, norm-FCFE>0, OShares>0.

**STUDY A — recency-weight calibration (REJECTED full extrapolation).** Panel n=6,332 firm-years, 2009-2024, 892 non-fin tickers; predict next-year TTM-earnings growth. rankIC of trailing→next growth is NEGATIVE every window (mean-reversion): equal-1/3 = **−0.104 IS / −0.199 OOS / −0.151 ALL**; recency-tilt (60/25/15) strictly WORSE (−0.118/−0.221/−0.170). MAE: equal 0.641 ALL best. ⇒ use EQUAL weights + shrink-0.50 toward terminal (full extrapolation empirically unjustified). Growth direction is unforecastable; shrink just bounds the assumption.

**STUDY B — margin-of-safety forward-return IC (POSITIVE, stable).** Panel 51,529 rows · 144 months · 959 tickers, non-fin rating≤3, point-in-time FV as-of merged to monthly price panel, stale FV (>15mo) dropped. Cross-sectional Spearman IC of MoS vs forward return, monthly-averaged:
| window | 1M | 2M | 3M |
|---|---|---|---|
| ALL 2014-26 | +0.0444 (t7.3) | +0.0584 (t9.4) | +0.0690 (t11.6) |
| IS 2014-19 | +0.0410 (t4.5) | +0.0508 (t5.4) | +0.0690 (t7.5) |
| OOS 2020-26 | +0.0473 (t5.8) | +0.0646 (t7.9) | +0.0690 (t8.9) |
Quintile monotone (profit_2M, richest→cheapest): 1.70→2.24→2.68→3.24→4.94. **Positive, monotone, IS/OOS-stable, OOS≥IS (no overfit), strengthens with horizon.** Modest magnitude (~0.05-0.07) = real value signal, NOT stand-alone alpha. (authoritative run = `dcf_exp/backtest_run.log`; `/tmp/dcf_ic.log` shows a qcut `inf` edge-artifact in quintile 3, IC/t identical to ±0.001.)

**DEMO — 5 Group-A watchlist names (as-of 2026-07-13, r13.30/g_term3.40):**
| tk | DCF | FV/sh | price | MoS | sector_lens (relative) |
|---|---|---|---|---|---|
| MSH | no FCFE (capex>CFO) | — | 31,750 | — | BUY PE 5.70 cheap |
| PVT | no FCFE (tanker buildout) | — | 18,950 | — | BUY PB 0.83 trough |
| HAH | no FCFE (ship buildout) | — | 50,800 | — | BUY EVEB 4.21 cheap |
| CTR | RICH | 52,564 | 73,800 | −40.4% | BUY EVEB 9.74 accum |
| DHG | RICH | 51,614 | 92,500 | −79.2% | BUY PE 13.4<MA5Y 15.05 |
DCF disagrees with relative lens on all 5 — the point of an absolute lens: (1) 3/5 in DCF blind spot (capex-heavy, FCFE<0 → tool abstains; relative asset/EV lens is right tool = coverage boundary, not contradiction); (2) CTR/DHG compute RICH despite relative-cheap = value-trap flag (DHG archetype: cheap vs own 5Y PE but ~80% above intrinsic, driven by declining earnings g2 −10.2/g3 −16.6); (3) conservative level bias → use ranks/value-trap flags not an absolute buy line.

**SENSITIVITY (CTR/DHG):** ±1% r → FV ~±10%; ±2% g → ~±8%. Verdict ROBUST — even at most-favorable corner (r−1%) both stay RICH (CTR −26%, DHG −61%). Rule: distrust any MoS that flips sign inside the ±1%r/±2%g box.
**LIMITATIONS:** coverage (FCFE-positive gate excludes capex-heavy + all financials); growth unforecastable (Study A); parameter fragility (§sens); net-borrow≈0 simplification; modest IC = interpretive aid not a book; research BQ-cache prices (never for live sizing). **Status: interpretive/reference tool. Wiring into any selector = a separate decision needing its own N-budget + backtest.**

**ROBUSTNESS ADD-ON (job Taylor_20260714_055038, `dcf_rate_robustness.py`):** Spyros flagged that `deposit_rate_vn.py`'s 26 anchors are all calibrated on ONE date (2026-06-19) → discount-rate hindsight, esp. IS 2014-19. Deposit series DOES vary (annual means 6.65→4.78→6.13, spread 2.8pp/std 0.78). **Test: re-run Study B IC with a CONSTANT r=12.47% (window-mean deposit 5.97% + ERP 6.5%) applied to all dates** (removes all date-level rate info incl. hindsight). Result vs pinned: ALL Δ={1M −0.0003, 2M −0.0009, 3M −0.0010}; IS Δ≤−0.0025; OOS Δ≤+0.0003 (panel 51,367 rows/144 mo/952 tk; 4,525 pre-2014 degenerate g_term≥r releases skipped, all outside eval window). **VERDICT: IC NOT sensitive to deposit hindsight** — rate is date-only (same across tickers within a month), so within-month cross-sectional MoS rank differences out the common level. Same argument covers CPI-proxy (terminal g = 100% proxy pre-2025). Residual caveat: robust to rate LEVEL being wrong, does NOT make historical MoS *level* point-in-time-clean → use ranks not the line (§6.3). Also patched `dcf_valuation.py terminal_growth()` to return `frac_real` + CLI prints `terminal g = X% (Y% REAL NSO / Z% PROXY)` with soft WARN when frac_real<15% (Winston: 13/60=21.7% real at 2026-06). FV math unchanged (verified). Framework §7.1 + §8.

**ORTHOGONALITY / RESIDUAL-IC (Pha 1, job Taylor_20260714_061144, `dcf_orthogonality_test.py`) — the gate before ANY wire:** is MoS an independent axis or just 1/PE with more steps (the failure mode that killed composite-as-selector: 1/PE dominant factor absorbed everything)? Reuse Study B panel (51,529 rows/144 mo/959 tk, FV not recomputed) + point-in-time PE/PB/EVEB merged on same rows (98/98/96% cov). **t-stat on MONTHLY IC series n≈144 (time-series t), NOT 51k pooled rows — Spyros' method question, confirmed correct.** (1) Cross-sectional rank-corr rank(MoS) vs rank(1/PE)=**+0.285** ALL / 0.281 IS / 0.288 OOS; vs 1/PB=0.334; vs 1/EVEB=0.346 — all **modest 0.28–0.39, far from collinear** (>0.7 if same thing). (2) Residual IC (neutralize MoS in rank space, IC of residual vs fwd ret): **MoS⟂1/PE** keeps ~55–60% of raw IC, sig BOTH windows all horizons (3M: IS +0.0412 t4.4 / OOS +0.0373 t5.2); MoS⟂1/PB even higher (3M IS 0.0565/OOS 0.0508); MoS⟂1/EVEB sig both (3M IS 0.0425 t4.7 / OOS 0.0294 t3.8); **MoS⟂[1/PE,1/PB,1/EVEB] joint** (hardest) still +sig at 2M/3M both windows (3M IS +0.0261 t2.8 / OOS +0.0212 t3.2), only 1M/2M-IS lose sig (t1.5). **VERDICT: MoS IS an independent information axis → GO qualifies for Pha 2 consideration.** Not 1/PE relabeled; composite-selector failure does NOT repeat. **Honest caveat: residual ≈ half raw IC (meaningful share shared w/ relative lenses); modest incremental axis NOT large new alpha; edge concentrated at 2–3M horizon, weak at 1M once all 3 relatives removed** — bounds Pha 2 weighting. Framework §7.2. Research-only, 0 production touch.

## Pha 2 — DCF check tích hợp vào plan generation (DollarBill, 2026-07-14)

**File thay đổi:** `trading_bot/plan.py` (field mới) + `trading_bot/strategies.py` (hàm `_dcf_check_for_order` + call trong build_plan).

**Tích hợp:** mỗi BUY order trong plan JSON giờ có field `dcf_check` theo schema:
```json
{"status":"RICH"|"CHEAP"|"NOT_COMPUTED","margin_of_safety":<float|null>,"robust":<bool>,"as_of":"YYYY-MM-DD"}
```
+ field `dcf_override_reason` (bắt buộc ghi khi RICH+robust+BUY, nếu trống → WARN note trong plan).

**Nguồn dữ liệu:** `dcf_valuation.fair_value()` đọc từ `data/bq_cache/ticker_financial.parquet` (local, không gọi BQ live). Fail-safe: mọi lỗi → `NOT_COMPUTED` với reason=`dcf_error:...`, plan vẫn build bình thường.

**robust = True** khi MoS không đổi dấu qua sensitivity box (±1pp discount rate, ±2pp growth) — đúng ngưỡng thống nhất Spyros/họp round-table.

**Verified (2026-07-14):**
- CTR @73,800: RICH, MoS=−40.4%, robust=True ✓
- DHG @92,500: RICH, MoS=−79.2%, robust=True ✓
- E1VFVN30 (ETF): NOT_COMPUTED reason=insufficient_history ✓
- VIC: NOT_COMPUTED reason=fcfe_negative_buildout ✓
- Backward compat: old plans load với dcf_check=None ✓
- Save→load round-trip: JSON schema đúng ✓
- bot_prepare_plan.py --dry: KHÔNG crash, plan build bình thường ✓

**Giới hạn:** discretionary/informational only — KHÔNG block/tự động loại lệnh. Quyết định cuối = user khi duyệt plan.

## Pha 2 — DCF echo vào execution audit trail (Mafee, 2026-07-14)

**File thay đổi:** `trading_bot/plan.py` (+ `dcf_check: dict`, `dcf_override_reason: str` vào `PlannedOrder`) + `trading_bot/executor.py` (state parents + bus event trong `_sync_fills`).

**Logic:**
- `load_plan()` tự-preserve `dcf_check`/`dcf_override_reason` từ JSON (field đã trong known set, không cần thay đổi filter).
- `Executor._load_state()` ghi `dcf_check` vào `state["parents"][order_id]` → field tồn tại trong `exec_*_state.json` cho audit.
- `Executor._sync_fills()` khi delta fill > 0 cho BUY với `dcf_check.status=RICH AND robust=True`: publish bus event `finding/dcf-rich-fill` (chứa ticker, order_id, filled_delta, dcf_check, dcf_override_reason). KHÔNG chặn lệnh, KHÔNG thay đổi execution path.
- Backward-compat: plan không có `dcf_check` → `dcf_check=None`, không bus event, không lỗi.

**Selfcheck `dcf_check_selfcheck.py` — 8/8 PASS:**
1. PlannedOrder giữ dcf_check + dcf_override_reason ✓
2. Backward-compat (dcf_check=None) ✓
3. load_plan() giữ dcf_check từ JSON ✓
4. Executor state giữ dcf_check trong parents ✓
5. Executor state dcf_check=None khi order không có ✓
6. _sync_fills publish bus event cho RICH+robust BUY ✓
7. KHÔNG publish khi CHEAP/NOT_COMPUTED/None ✓
8. KHÔNG publish khi SELL side dù RICH ✓

## Pha 4 — DCF-as-gate PLACEBO test (Taylor, 2026-07-14, job Taylor_20260714_080414)

**Mục đích**: trả lời killer objection duy nhất mà quant-skeptic dùng để REFUTED Pha 3
(`mike/logs/verify_20260714_073843.log`): "~3 tên bị hoán đổi trong rổ PARKING 30 tên, chưa ai chứng
minh 1 hoán đổi NGẪU NHIÊN cùng cỡ không tạo ra spread tương đương".

**Control**: `BASKET_DCF_MODE=placebo_random` + `BASKET_DCF_PLACEBO_SEED` (custom_basket.py, mặc định
OFF). Mỗi ngày rebal d loại ĐÚNG n_d tên mà exclude_rich thật sự loại ở chính ngày d (đo từ cùng
`dcf_at`, không ước lượng) nhưng chọn NGẪU NHIÊN. Cùng số lượng / cùng pool / cùng bước / cùng
fail-safe → khác biệt DUY NHẤT vs biến thể A là CHỌN AI. RNG seed theo `(SEED, date.toordinal())`
→ mỗi ngày độc lập, cả path tái lập chính xác. 20 seed = phân phối null.

**Audit** (verified, không giả định): 20/20 run `self-check 0 VND` (cả BAL+LAG); mọi seed loại đúng
740 tên / 48 ngày (mean 15.42/ngày) = y hệt exclude_rich; **regression guard PASS** — chạy lại config
OFF dưới code đã vá cho ra NAV series **identical** với ctrl Pha 3 (`_exp_dcfctrlrerun20260714.csv`)
→ nhánh placebo KHÔNG động vào path selection dùng chung.

**KẾT QUẢ — objection KHÔNG đứng vững. varA là outlier rõ rệt vs null:**
| window | metric | null mean±SD | varA | z | #≥varA |
|---|---|---|---|---|---|
| FULL | ΔCAGR | −0.09 ± 0.43 | **+0.99** | +2.51 | **0/20** |
| FULL | ΔSharpe | +0.012 ± 0.021 | **+0.059** | +2.26 | **0/20** |
| OOS 2020+ | ΔCAGR | −0.14 ± 0.57 | **+1.50** | +2.85 | **0/20** |
| OOS 2020+ | ΔSharpe | −0.012 ± 0.030 | **+0.063** | +2.53 | **0/20** |
| IS 2014-19 | ΔCAGR | −0.03 ± 0.78 | +0.49 | +0.68 | 5/20 |

Hoán đổi ngẫu nhiên cùng cỡ đáng giá ≈ 0 trung bình (±0.43pp CAGR). varA nằm ~2.5 SD ngoài null,
0/20 seed random bằng hoặc hơn. Mạnh nhất Ở OOS (z=2.85) — ngược với dấu hiệu overfit thường gặp.

**KHÔNG PHẢI GO** (4 điều placebo KHÔNG chứng minh): (1) **objection 2017/2021 SỐNG NGUYÊN** — per-year
ΔCAGR 2017 +7.52pp / 2021 +8.71pp = ~100% tổng edge (+16.2pp); "không phải random" ≠ "lặp lại được".
(2) null random ≠ null multiple-testing — câu hỏi DSR/N-trials chưa đụng tới. (3) **DCF-hơn-random ≠
DCF-cụ-thể** — 1 rule hệ thống ĐƠN GIẢN hơn (vd loại các tên PE cao nhất) có thể bắt cùng spread;
**placebo theo value-proxy (thay vì random) là test tiếp theo cần làm, tôi CHƯA chạy** — đề xuất
quant-skeptic đòi test này trước mọi GO. (4) daily-return t=1.02/p=0.31 Pha 3 KHÔNG đổi.

**Trạng thái: REFUTED bị THÁCH THỨC đúng ở killer objection, CHƯA bị lật.** Research-only, 0 chạm
production (`BASKET_DCF_MODE` default OFF → production byte-identical). Route quant-skeptic.

**Artifacts**: `data/*_exp_dcfplacebo<1..20>.csv` (§8: seed trong filename), `dcf_placebo_test.py`,
`data/dcf_placebo_logs/` (runner.sh + 20 log + DONE_MARKS).
Reproduce: `SEEDS="1 2 3" bash data/dcf_placebo_logs/runner.sh` → `$DNA_PYEXE dcf_placebo_test.py`

---

## Sector-cap cho custom30V (yieldcombo basket) — **NO-GO cả 3 biến thể** (2026-07-14, job `Taylor_20260714_095953`)

**Câu hỏi:** basket custom30V dùng `BASKET_WT=namecap` (cap tên 10%, KHÔNG cap ngành). Tại rebal
2026-05-05 sector-8 (ICB/1000=8 = ngân hàng 8355 + BĐS 8633 + CK/DVTC 8773/8777) = **95.5%** rổ.
Cap ngành có cải thiện risk-adjusted không? (`weight_scheme="sectorcap"` có sẵn trong code từ
2026-06-15 nhưng **chưa từng backtest**.)

**Lệnh (§8: mỗi run 1 `EXP_TAG` riêng → CSV R3 pinned KHÔNG bị đụng; đã verify mtime R3 = Jul 12):**
```bash
# baseline / A / B / B×1.5 — chung: NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_SELECT=yieldcombo
# BQ_CACHE_THREADS=1 PARK_STATES="3:0.7" AUDIT_END=2026-06-19 $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge
EXP_TAG=seccap_base   BASKET_WT=namecap
EXP_TAG=seccap_Afix50 BASKET_WT=sectorcap                                 # A: fixed cap 0.50 (code có sẵn)
EXP_TAG=seccap_Bmkt   BASKET_WT=sectorcap BASKET_SECCAP_MODE=mktcap       # B: cap = mkt-cap w8 PIT
EXP_TAG=seccap_Bx15   BASKET_WT=sectorcap BASKET_SECCAP_MODE=mktx1.5      # B×1.5: value-tilt allowance
```

**Full harness (self-check 0 VND cả 4 run):**

| Biến thể | CAGR | Sharpe | MaxDD | Calmar | IS 14-19 | OOS 20-26 |
|---|---|---|---|---|---|---|
| baseline (namecap = production) | 27.09% | 1.81 | −18.3% | 1.48 | 23.37 | 30.58 |
| A fix50 | 26.88% | 1.81 | −18.1% | 1.48 | 23.30 | 30.23 |
| B mktcap | 26.93% | 1.82 | −18.1% | 1.49 | 23.22 | 30.40 |
| B×1.5 | 27.05% | 1.82 | −18.3% | 1.48 | 23.27 | 30.60 |

Δ vs baseline: A −0.21pp (IS −0.07 / OOS −0.35) · B −0.16pp (IS −0.15 / OOS −0.18) → **chữ ký
IS/OOS ÂM cả hai vế** = trượt chuẩn PASS. (baseline 27.09 ≠ 27.84 pinned = data-drift adj-price;
đã tự chạy baseline cùng snapshot để so cùng thước — đúng META caveat.)

**Vehicle thuần (custom30V level, không pha loãng bởi BAL/LAG) — số quyết định:**

| Biến thể | CAGR | Sharpe | **MaxDD** | Calmar |
|---|---|---|---|---|
| baseline | 29.86% | 1.24 | **−41.0%** | 0.73 |
| A fix50 | 28.71% | 1.22 | **−42.1%** | 0.68 |
| B mktcap | 28.59% | 1.22 | **−42.1%** | 0.68 |

→ **Cap ngành làm XẤU ĐI mọi chiều KỂ CẢ drawdown.** Trực giác "tập trung=rủi ro→cap sẽ giảm DD"
**bị số liệu bác**: đuôi phi-tài-chính của rổ là small-cap beta cao, sập mạnh hơn bank large-cap.
0.2pp DD "cải thiện" ở full harness = nhiễu pha loãng, không phải cơ chế. Turnover A/B 2.72×/năm
vs baseline 2.43× (+0.09pp phí/năm @TC 0.3%) mà harness **không hề charge** (`build_pit`:
`ret=Σ(W×r)`, không có phí nội bộ basket) → −0.21pp của A là **cận trên lạc quan**.

**Task 1 — tập trung ngành là DRIFT dài hạn, không phải cực đoan nhất thời** (48 rebal q2m5,
trọng số dựng lại khớp `custom30v_8l_publish.csv` tới 4 chữ số → LÀ số production):
w8 2014 0.25 → 2016 0.14 → 2018 0.57 → 2020 0.57 → 2022 0.74 → 2024 0.77 → **2026-05-05 0.955**.
**ĐÍNH CHÍNH tiền đề dispatch:** mkt-cap w8 thật của `ticker_prune` **KHÔNG** phải 25-35% —
mean **47.0%**, hiện tại **63.7%**. Thị trường VN thật sự nặng tài chính; basket vượt thị trường
36/48 rebal (tilt thật) nhưng phần lớn mức tập trung là **phản chiếu thị trường**.

**⚠️ Cảnh báo phương pháp:** cap bind 25-26/26 rebal OOS nhưng chỉ 6/22 (A) IS → cơ chế **ngủ đông
in-sample**, walk-forward IS/OOS **là công cụ SAI** ở đây (đúng bài học DT5G "IS = +0.00pp exactly").
Verdict dựa trên vehicle-level + dấu nhất quán mọi chiều, không dựa chữ ký IS/OOS.

**Verdict: NO-GO — không wire gì.** Không phải "edge nhỏ" mà **sai dấu mọi chiều đo**. Không cần
DSR/PBO (chỉ có nghĩa khi có ứng viên dương). Lý do bản chất: tập trung sector-8 là **hệ quả cơ học
của value axis** (1/PE+1/PCF; bank VN PE/PCF thấp cấu trúc) — đúng factor mạnh nhất của hệ (IC
+0.125, "Value dominates ALL regimes"). Cap ngành = cắt chính alpha đó, đổi lấy đuôi small-cap
kém-value + rủi ro hơn. Rủi ro tập trung là THẬT & đáng theo dõi, nhưng **sector-cap không phải
công cụ xử lý nó**.

**Task 3 — lệnh HPG→LPB:** sector-cap là cơ chế TRỌNG SỐ, không phải cơ chế CHỌN TÊN → 30 tên
**giống hệt** dưới mọi biến thể. LPB **là** thành viên dưới cả 3 (baseline 5.25% / A 2.75% /
B 3.50%); HPG **không** là thành viên dưới bất kỳ biến thể nào. → swap vẫn đúng hướng; sector-cap
không đưa ra tên khác thay LPB (chỉ đổi size ~½ + kéo theo rebalance rộng 13 tên đuôi).

**Production KHÔNG đổi gì**: `BASKET_SECCAP_MODE` default OFF = byte-identical (guard
`seccap_dyn_selfcheck.py` 9/9 PASS: OFF byte-identical · dyn bind thật · multiplier · raise khi
sai weight_scheme · đại số `_cap_sector`). `custom_basket.py` default, `BASKET_WT` production,
`trading_rules.json`, plan hiện tại: **không chạm**.

**Artifacts**: `mike/agents/Taylor/sector_cap_framework.md` (phương pháp mcap ngành + cách cap),
`sector_conc_audit.py` + `sector_conc_history.csv` (48 rebal), `seccap_vehicle_compare.py` + `.csv`,
`seccap_dyn_selfcheck.py`, `data/*_exp_seccap_{base,Afix50,Bmkt,Bx15}.csv`, log `mike/agents/Taylor/seccap_logs/`.

## Route-aware custom30V selector `BASKET_SELECT=v3route` — ~~CẦN VERIFY THÊM (lean GO)~~ → **NO-GO, KHÔNG WIRE** (2026-07-14, job `Taylor_20260714_112932` → fix quyết định `Taylor_20260714_121717`)

> ⚠️ **MỤC NÀY ĐÃ BỊ LẬT.** Số `+7.63pp` dưới đây **quy sai công** (so với `yieldcombo` = gộp 2 trục).
> Đóng góp THẬT của fix route = **−2.38pp** (âm cả IS lẫn OOS). Xem mục **`v3route` FIX QUYẾT ĐỊNH**
> ở cuối file. Giữ nguyên phần dưới làm dấu vết audit.

**Tiền đề (user)**: `yieldcombo` (production) xếp hạng bằng `rank(1/PE)+rank(1/PCF)` cho MỌI tên →
so ngân hàng với công ty sản xuất trên cùng thước `1/PCF`. PCF của bank = dòng tiền gửi/cho vay
(bảng cân đối), KHÔNG phải tiền do lõi kinh doanh tạo ra → **không so ngang hàng được**.

**v3route** = `v3latest` + đúng 1 đổi: BANK/INSURANCE/SECURITIES chấm bằng `rating_8l.value_score_v2`
verbatim (`0.65*ey_pct_WITHIN_route + 0.35*(0.5-pb_z/2) + cfo_confirm(±0.05/-0.08) + track_bonus`;
pb_z IC **+0.136** cho BANK, đã validate — không chế số mới). Mọi route khác **byte-identical
v3latest** → ablation sạch 1 trục. REALESTATE/POWER **cố ý giữ** đường v3latest (ablation riêng).

**Config**: NAV_TOTAL_B=50, PARK_STATES=3:0.7, DT5G, threads=1, AUDIT_END=2026-06-19, BASKET_WT=namecap.
**Self-check 0 VND cả 2 arm** (BAL+LAG). Cả 2 arm chạy CÙNG hôm nay/cùng vintage → delta hợp lệ.

| VEHICLE (custom30V standalone) | CAGR | Sharpe | MaxDD | Calmar | CAGR IS | CAGR OOS |
|---|---|---|---|---|---|---|
| yieldcombo | 29.83% | 1.24 | −40.98% | 0.73 | 23.53% | 35.89% |
| **v3route** | **37.47%** | **1.51** | **−36.39%** | **1.03** | **29.68%** | **45.12%** |
| Δ | **+7.63pp** | +0.27 | **+4.59pp tốt hơn** | +0.30 | **+6.15pp** | **+9.24pp** |

| HỆ 2-book V2.4 đầy đủ | CAGR | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|
| baseline yieldcombo | 27.09% | 1.81 | −18.3% | 1.48 |
| **v3route** | **27.96%** | **1.88** | **−18.6%** | **1.50** |
| Δ | **+0.87pp** | +0.07 | **−0.3pp xấu hơn** | +0.02 |

**Multiple-testing (KB §5)**: N trials = 10 selector mode. **DSR = 1.0000 PASS** mọi N (10/25/50/138)
— *nhưng tự hạ trọng số: DSR chấm NAV toàn hệ, Sharpe do V2.4 quyết định chứ không phải cú swap*.
**Per-year LOO: edge CAGR dương 13/13** (min +0.36pp @drop 2017, max +1.48pp @drop 2024); **Calmar
dương 12/13** (drop 2017 = −0.002 ≈ hoà) → **KHÔNG phải reshuffle-luck 1-2 năm** (khác DCF varA).
Recompute độc lập từ CSV: **+0.88pp** vs harness **+0.87pp** (lệch do calendar-time vs 252d) → khớp.

**⚠️ OBJECTION THẬT — 3 năm gần nhất ÂM ở cấp hệ**: 2024 **−5.57pp** / 2025 **−1.24pp** / 2026
**−2.37pp**. Thắng 8/13 năm (mean +0.92 / median +1.08pp); edge tập trung 2016-18 + 2022-23. LOO cho
thấy các năm gần đây **kéo edge xuống** (bỏ 2024 → edge tăng +1.48pp), không tạo ra nó. Edge vẫn
dương 13/13 nên chưa bị lật, nhưng **câu hỏi mở: noise 3 năm hay cơ chế đang xói mòn?** → đây là
killer objection phải giao quant-skeptic.

**Basket rebal 2026-05-05 (overlap 21/30)**: **FINANCIAL 18/30 → 10/30; BANK 13/30 → 6/30.**
OUT: BID·CTG·LPB·MBB·TCB·VCB[BANK], EVF[SEC], DCM[CYC]. IN: FPT·GAS·VNM·PNJ·DGW·GEE[COMPOUNDER],
DIG·HDG[RE], HPG[CYC]. → bỏ thước 1/PCF sai thì **một nửa ngân hàng rơi ra** (chúng vào rổ nhờ chỉ
số vô nghĩa với chúng). **HPG: yieldcombo OUT → v3route IN (liq_rank 29); LPB: IN → OUT** ⇒ **v3route
đảo ngược đúng 180° cả 2 lệnh plan 07-14 (bán HPG / mua LPB)** — user HOLD hôm nay là may; chốt
hướng selector TRƯỚC khi xử nốt basket-drift HPG.

**Selfcheck** `route_selector_selfcheck.py` **6/6 PASS**: OFF byte-identical (default `blend`) ·
bóp PCF của ACB → v3route **0.0000** vs v3latest 0.0353 (trục thật sự đổi) · bóp pb_z → 0.0431 ·
1010 tên phi-tài-chính **0 khác biệt**, 79/79 tài chính ĐỀU đổi · rank WITHIN route (shock PE thị
trường → 0 bank dịch) · thiếu pb_z → **abstain −1**, không bịa 0.5 · v2 tái lập rating_8l đúng 6 chữ
số (ACB 0.538235 vs 0.538235).

**⚠️ SỰ CỐ ĐÃ XỬ LÝ — canonical R3 CSV bị ghi đè**: baseline (`yieldcombo` → `_sel_tag` rỗng theo
thiết kế) ghi đè đúng file pinned `..._wtnamecap.csv` lúc 18:42 (đúng mẫu §8 2026-07-06). **Đã khôi
phục** từ `R3_pinned_backup_20260714.csv`, verify md5 `4d736d91…` khớp lại `_exp_dropMOMN-MOMS.csv`
(= R3 pinned thật). Rerun hôm nay giữ ở `_exp_selbaseline20260714.csv`. Bài học: tag rỗng bảo vệ
*tên file production*, KHÔNG bảo vệ *artifact pinned* khỏi một rerun hợp lệ.

**⚠️ PHÁT HIỆN PHỤ — R3 pinned KHÔNG tái lập được trên vintage hôm nay**: baseline production chạy
lại = **27.09%** vs registry pin **27.84%** (07-12) → **−0.75pp thuần data vintage** (fix cache 8L /
ticker_prune chunked 07-13). Mọi run hôm nay nhất quán với nhau (md5 khớp `_exp_dcfctrl20260714`) nên
A/B vẫn hợp lệ, **nhưng cần quyết định re-pin R3 riêng** — nền so sánh đang trôi.

**Rủi ro tồn dư (pre-existing)**: `build_value_panel.py` khai báo route bằng **port copy-paste** của
`rating_8l.route_of` (dòng 71), không import → 2 nguồn sự thật. Đối chiếu tay: **hiện khớp 100%**.
Đề xuất (ngoài phạm vi job): panel import trực tiếp từ `rating_8l`.

**Production KHÔNG đổi gì**: `BASKET_SELECT` default = `blend`; production set `yieldcombo` tường
minh → không bao giờ vào nhánh v3route. `custom_basket.py` default / `BASKET_WT` / `trading_rules.json`
/ plan hiện tại: **không chạm**. **BẮT BUỘC quant-skeptic CONFIRMED trước mọi cân nhắc wire.**

**Artifacts**: `mike/agents/Taylor/route_aware_selector_framework.md`, `route_selector_selfcheck.py`,
`mike/agents/Taylor/route_exp/` (logs/, vehicle_metrics.csv, members_{v3route,yieldcombo}.csv,
basket_compare.py, route_robustness.py, R3_pinned_backup_20260714.csv),
`data/*_exp_selv3route.csv` + `data/*_exp_selbaseline20260714.csv`.

---

## `v3route` FIX QUYẾT ĐỊNH — **NO-GO, edge KHÔNG TỒN TẠI khi tách bạch** (2026-07-14, job `Taylor_20260714_121717`)

Chạy theo đúng khuyến nghị quant-skeptic (REFUTED, verify 12:07:14) cho finding `Taylor_20260714_112932`.
**Fix đã làm đúng và đủ — edge không sống sót.** REFUTED **giữ nguyên**. Research-only, production **0 chạm**.

### Lỗi lớn hơn cả bug skeptic bắt: arm `v3latest` CHƯA TỪNG ĐƯỢC ĐO
Mọi số cũ quote vs `yieldcombo`, nhưng `v3route3` khác `yieldcombo` ở **2 chiều**: **(a)** trục định giá
→ composite 8L `v3latest` (áp cho MỌI route, **không liên quan route-aware**), **(b)** fix route tài chính
(**premise của user**). Không đo `v3latest` ⇒ (a)+(b) gộp làm một, toàn bộ công ghi cho (b).

### Cấp vehicle — 5 arm, cùng vintage/config (`route_v3latest_arm.py`, `route_fix_compare.py`)
| arm | CAGR | Sharpe | MaxDD | Calmar | IS | OOS | fin/30 |
|---|---|---|---|---|---|---|---|
| yieldcombo (production) | 29.83% | 1.24 | −40.98% | 0.73 | 23.53% | 35.89% | 9.27 |
| **`v3latest`** (trục (a) đơn thuần) | **38.38%** | **1.51** | **−34.96%** | **1.10** | **32.07%** | **44.51%** | 6.98 |
| `v3route` (REFUTED, lệch thang) | 37.47% | 1.51 | −36.39% | 1.03 | 29.68% | 45.12% | 5.08 |
| `v3route2` (pct-norm, quá đà) | 36.22% | 1.47 | −36.29% | 1.00 | 29.49% | 42.76% | 6.19 |
| **`v3route3`** (quantile-match, tham chiếu) | 36.01% | 1.46 | −36.41% | 0.99 | 29.52% | 42.30% | 6.54 |

`v3latest` **thắng mọi arm route ở mọi chiều** → thêm fix route lên trên chỉ làm xấu đi.

### Phân rã sạch của `+7.63pp` (cộng khớp chính xác)
```
 +8.55pp  (a) trục composite 8L    v3latest − yieldcombo   <- KHÔNG liên quan route
 −2.38pp  (b) fix route THẬT       v3route3 − v3latest     <- premise user, đã tách bạch
 +1.46pp  (c) artifact thang đo    v3route  − v3route3     <- đúng bug skeptic bắt
 ───────
 +7.63pp  = headline job 112932    ✓ (8.55 − 2.38 + 1.46 = 7.63)
```
**(b) ÂM CẢ HAI CỬA SỔ** (không phải hiện tượng 1 cửa sổ): IS **−2.56pp** · OOS **−2.20pp**.
*(so sánh: (a) IS +8.54 / OOS +8.62)*

### Đòn kết liễu 2: `v3latest` ĐÃ BỊ BÁC 2026-06-22 — và **cấp vehicle ĐẢO DẤU OOS**
Registry THREAD (b) (dòng ~145-154, drift-controlled, self-check 0 VND) đã đo `v3latest` **ở cấp hệ**:
IS **+1.40pp** / **OOS −0.78pp** → *IS-overfit, GIỮ yieldcombo, KHÔNG nhận v3 composite làm selector*.
Nhưng **cấp vehicle hôm nay nói OOS +8.62pp**. ⇒ **Proxy vehicle không chỉ suy giảm — nó ĐẢO DẤU**
(custom30V chỉ là sleeve park khi NEUTRAL; CAGR vehicle tính cả những đoạn sleeve không được dùng).
**Không bao giờ tuyên GO cho selector custom30V từ số cấp vehicle.**

### Các test phụ
- **§3 ABSTAIN — giả thuyết coverage-artifact BỊ BÁC** (sòng phẳng: điểm finding gốc đứng vững).
  `V3R_ABSTAIN_IMPUTE=1` (gán pb_z trung vị route thay vì loại): CAGR **36.46%** (+6.63pp, fin 7.46/30)
  **> `v3route3` 36.01%** ⇒ ABSTAIN **làm mất −0.45pp**, không tạo edge.
- **§4 SENSITIVITY — plateau THẬT nhưng quanh đóng góp ÂM.** 7 cell (`W_ABS` .55/.65/.75 × cfo off/×2 ×
  track off/×2): edge **+5.72 … +6.65pp**, sd 0.33, default không phải spike. Nhưng mọi cell mang sẵn
  +8.55pp của (a) ⇒ thực chất **−1.9 … −2.8pp so `v3latest`**: robust ở chỗ **hơi có hại**.
- **§2 PLACEBO — CONFOUND, verdict tự in của script SAI, KHÔNG ĐƯỢC TRÍCH.** 20 seed count-matched:
  placebo mean −2.13pp, real +6.18pp, z=+5.12; script in *"WHICH names are dropped carries real
  information"* — **sai**: placebo dựng trên ranking `yieldcombo` còn `v3route3` lấy phi-tài-chính từ
  `v3latest` ⇒ z đang đo **trục (a)**. Placebo đúng (nền `v3latest`) **không chạy**: thứ nó cần giải
  thích (edge dương của (b)) **không tồn tại** (b = −2.38pp).
- **§5 selfcheck `route_selector_selfcheck.py` — 7 nhóm ALL PASS.** Thêm **[7] cross-route scale**:
  gap fin−nonfin P90 mỗi quý → `v3route` **+0.107** (bug REFUTED, test PHẢI thấy) · `v3route2` **−0.064**
  (quá đà, cùng lớp lỗi ngược dấu) · `v3route3` **−0.001** ✅. Spearman trong-route 0.9993/0.9995
  (thứ tự bank-vs-bank không đổi, chỉ phép cắt dịch); 1010 tên phi-tài-chính byte-identical cả 3 arm.
  `basket_compare.py`: vá dòng chẩn đoán "85 names/237 with pb_z" (PANEL daily → lẫn rows-vs-names).

### Verdict + sòng phẳng với premise của user
**NO-GO. Không wire gì.** Kết quả **không** chứng minh "PCF bank = PCF nhà máy"; nó bác một điều hẹp hơn:
**cách hiện thực hoá này** (chấm bank bằng `pb_z` qua `value_score_v2` **trong phép cắt top-30 chéo ngành**)
**không tạo return edge** — mất 2.38pp. Sắc thái: `v3latest` (arm thắng vehicle) **cũng đã** xếp hạng
**TRONG route** ⇒ nguyên tắc "đừng so bank với nhà máy trên cùng thang" **hệ đã làm sẵn ở đó**; thứ gãy
là bước mạnh hơn (**thay 1/PCF bằng pb_z**). Và `v3latest` **cũng đã bị bác ở cấp hệ** ⇒ **không có gì để wire**.
**KHÔNG đảo ngược 2 lệnh HPG/LPB hoãn trong plan 07-14** (quyết định của user; nếu có thì kết quả này càng củng cố không hành động theo v3route).

### Bài học phương pháp (giá trị lâu dài nhất)
1. **Ablation phải neo vào arm LIỀN KỀ, không phải baseline production** — bug này có **trước** bug thang đo và **lớn hơn** (8.55 vs 1.46).
2. **Cấp vehicle custom30V là proxy ĐẢO DẤU cho cấp hệ.**
3. **Verdict tự in của script có thể sai khi thí nghiệm bị confound** — đọc thiết kế, đừng copy dòng kết luận.

### Việc riêng (không thuộc verdict này)
- **Re-pin R3**: vintage hôm nay **27.09%** vs pin **27.84%** = −0.75pp **data-drift, không phải bug** → **chờ Mike/user quyết**, job này KHÔNG tự re-pin.
- **`build_value_panel.py` import `rating_8l.route_of`: KHÔNG LÀM** — `route_of` là **hàm lồng** (`rating_8l.py:443`, closure trên `bank_set`/`power_set`) → cần **refactor production 8L**, sai phạm vi cho job research (guidelines §3). **Đã verify port TƯƠNG ĐƯƠNG hôm nay** (COMMODITY_MAP/SUGAR/CEMENT khớp từng ký tự, cùng lens CSV, cùng thứ tự nhánh) ⇒ **finding không bị nhiễm**; rủi ro trôi tương lai vẫn còn → task refactor riêng nếu muốn.

**Artifacts**: `mike/agents/Taylor/route_aware_selector_framework.md` §10 · `route_exp/`:
`route_v3latest_arm.py` (arm quyết định), `route_fix_compare.py`, `route_abstain_sens.py`, `route_placebo.py`,
`attribution_metrics.csv`, `abstain_sens_metrics.csv`, `placebo_v3route3.csv`, `vehicle_metrics_fix.csv`,
`vehicle_level_*.csv`, `members_*.csv`, `logs/*.log` · `route_selector_selfcheck.py` (7 nhóm ALL PASS).

## 🔬 CƠ CHẾ — vì sao thước đo "sai bản chất" (1/PCF cho bank) THẮNG thước đo "chuẩn hơn" (pb_z) + lời giải cho v3latest IS+1.40/OOS−0.78 (Taylor 2026-07-14, job `Taylor_20260714_132942`)
**NGHIÊN CỨU CƠ CHẾ — KHÔNG có ứng viên wire, KHÔNG chạm production, KHÔNG arm backtest mới.** Trả lời câu hỏi user sau NO-GO `v3route` (job 121717). Doc đầy đủ: `mike/agents/Taylor/route_aware_selector_framework.md` **§11**. Scripts: `route_exp/{mech_bank_pbz,mech_attribution,mech_scale_drift}.py`. Dữ liệu: panel PIT đông băng `data/value_panel_2014.csv` + `members_*.csv` (job 112932).

**TRẢ LỜI:** `1/PCF` **chưa bao giờ làm việc ĐỊNH GIÁ cho ngân hàng — nó làm việc PHÂN BỔ NGÀNH.** CFO ngân hàng = dòng huy động/cho vay (user đúng), nhưng sai **theo MỘT CHIỀU CÓ HỆ THỐNG** → `1/PCF` ngân hàng luôn cao → **bank ngồi percentile 0.711 TOÀN THỊ TRƯỜNG trên trục cfy vs 0.496 của phi-ngân-hàng** (coverage PCF>0: 0.742 vs 0.590). Phép cắt top-30 **CHÉO ngành** biến lệch đó thành **suất nhập rổ** ⇒ `yieldcombo` = **cỗ máy overweight bank đội lốt thước đo định giá**. Bank VN thắng **+1.29pp fwd2M** vs phần còn lại (IS +0.47 / OOS +1.39). ⇒ **thước đo sai đã MUA MỘT VỊ THẾ ĐÚNG; "sửa" phép đo = THANH LÝ vị thế.** Backtest chấm vị thế, không chấm phép đo. Hai mệnh đề cùng đúng, không mâu thuẫn: (1) `pb_z` đúng bản chất bank-vs-bank hơn; (2) thay `1/PCF`→`pb_z` làm hệ tệ (−2.38pp) — vì **leg `1/PCF` bị thay KHÔNG hề đang xếp hạng bank-vs-bank, nó đang giữ tỷ trọng ngành.**

**Bằng chứng A — tiền đề "pb_z dự báo tốt hơn" KHÔNG được dữ liệu ủng hộ** (IC rank cross-section TRONG route BANK, target `profit_2M` T+40, gộp (ticker,quarter)=last, 27 tên/50 quý/TB 19.2 tên/quý):
| lens | IC full | t | hit | IC IS | IC OOS |
|---|---|---|---|---|---|
| `pb_z` (cheap=high) | **+0.065** | **1.17** | 58% | +0.023 | +0.096 |
| `cfy=1/PCF` (thước đo "SAI") | **+0.086** | 1.65 | 49% | +0.140 | +0.033 |
| `ey=1/PE` | **+0.181** | **3.79** | 65% | +0.167 | +0.194 |
⇒ `pb_z` **t=1.17 không phân biệt được với 0**; thước đo "sai" xếp hạng bank **NHỈNH HƠN**; cả hai bị `1/PE` áp đảo — mà **cả 2 arm đều đã có `1/PE`**.
⚠️ **`+0.136` ở `rating_8l.py:649` KHÔNG TRUY VẾT ĐƯỢC** — grep toàn repo: chỉ tồn tại dưới dạng comment (`rating_8l.py:649`, `custom_basket.py:367`), **không artifact/script/dòng registry gốc**. Job 112932 trích nó như "đã validate" — **chưa từng validate ở đâu tìm được**. Đo lại: **+0.065**. → **số không truy vết được, không phải bằng chứng.** (Đề xuất dọn comment = task riêng có skeptic; KHÔNG sửa trong job research.)

**Bằng chứng B — H3 XÁC NHẬN: `pb_z` là cờ ĐUÔI, không phải trục XẾP HẠNG.** `rating_8l.py:646` **tự ghi**: *"pb_z is **LINEAR-DEAD** (golden-cell flag only) + TRAP guard"* / *"RETAIN pb_z (0.35) for its **NON-linear** value the IC can't see"*. `value_score_v2` lại dùng nó qua leg **TUYẾN TÍNH** `0.35·(0.5−pb_z/2)` = **category error**. Bucket trong BANK: `pb_z≤−1` (golden cell) fwd2M **+9.30%** vs `>+1` **+2.06%** — hiệu ứng đuôi THẬT **nhưng chỉ nổ 3.9% bank-quarter** (và **0.0% trong 2017/2018/2021**). Phân phối `pb_z` bank **lệch phải nặng** (median **+0.71**, 30% >+1, chỉ 3.9% <−1) vì **bank VN re-rate LÊN từ nền thấp** → PB gần như luôn TRÊN MA5Y của chính nó ⇒ với bank, `pb_z` **không đo "rẻ"**, nó đo **drift định giá vs quá khứ gần**.

**Bằng chứng C — H6 (mới) XÁC NHẬN: leg TUYỆT ĐỐI trong phép cắt CHÉO = cược thời điểm ngành ẩn.** Mọi leg khác (`ey/cfy/ps`, cả leg `ey` của v2) là **PERCENTILE chuẩn hoá lại mỗi quý**; leg `pb_z` là **TUYỆT ĐỐI**.
| | mean | **sd QUA CÁC QUÝ** | range |
|---|---|---|---|
| leg TUYỆT ĐỐI `(0.5−pb_z/2)` (đang dùng) | 0.343 | **0.235** | 0.000…0.863 |
| leg PERCENTILE của **cùng pb_z** (đối chứng) | 0.573 | **0.083** | 0.519…1.000 |
**38.7% phương sai `pb_z` bank = CÚ DỊCH CHUNG của cả ngành**; mean `pb_z` ngành swing **−0.78…+3.05 = 3.83 z-unit** → leg tuyệt đối dịch cả ngành **1.92 điểm** trong khi **range của leg chỉ 0..1** ⇒ leg bị cú dịch chung lấn át. Hệ quả: PB toàn ngành nhích lên → **MỌI bank cùng bị hạ điểm** → **bị đẩy khỏi top-30 hàng loạt**, không liên quan bank nào hấp dẫn hơn. Percentile miễn nhiễm (median bank luôn ~0.5 → chỉ nói "bank NÀO", không bao giờ nói "BAO NHIÊU bank"). Xác nhận trên rổ thật: Spearman(Δslot do route fix, median `pb_z` ngành) = **−0.153**; 2017Q4–2019Q3 (median +0.9…+2.8) cắt đều −1..−2 slot, 2021Q4 (median +2.33) cắt **−3**. **Và KHÔNG có kỹ năng timing**: Spearman(Δslot bank, bank−nonbank fwd2M quý đó) = **+0.127** (n=47; IS +0.084/OOS +0.145) ≈ 0.

**Bằng chứng D + LỜI GIẢI CHO v3latest IS+1.40/OOS−0.78 (registry L144-154, 2026-06-22).** Bank share THẬT của rổ 30 tên (48 quý, `members_*.csv`):
| arm | bank share FULL | IS 2014-19 | **OOS 2020+** | bank/quý |
|---|---|---|---|---|
| **`yieldcombo` (production)** | **24.1%** | 10.3% | **35.8%** | **7.23** |
| `v3latest` | 15.1% | 7.7% | 21.3% | 4.52 |
| `v3route3` | 13.0% | 4.9% | 19.9% | 3.90 |
Bank vs non-bank fwd2M: FULL **+4.06 vs +2.77 = +1.29pp** | IS **+2.10 vs +1.62 = +0.47pp** | **OOS +4.95 vs +3.56 = +1.39pp**. Ghép lại:
| cửa sổ | Δ bank share (v3latest−yieldcombo) | × (bank−nonbank) | = drag/2M | **≈ drag/năm (×6)** |
|---|---|---|---|---|
| IS 2014-19 | **−2.6pp** | +0.47pp | −0.012pp | **−0.07pp/yr ≈ 0** |
| **OOS 2020+** | **−14.5pp** | +1.39pp | −0.201pp | **−1.21pp/yr** |
⇒ **`v3latest` KHÔNG "hết thiêng" OOS — nó vẫn chọn tên tốt như thường, nhưng nó ĐANG SHORT ngành đã thắng, và OOS ngành đó thắng đậm hơn ×3.** Alpha chọn-tên gần như không đổi giữa 2 cửa sổ; **chi phí underweight bank nhân ba** → dấu lật `+`→`−`. **Không phải "overfit IS" theo nghĩa cổ điển** (fit nhiễu quá khứ) — là một **vị thế ngành ẩn** bị đổi mà không ai khai báo.
*⚠️ Giới hạn (ghi rõ):* ước lượng **equal-weight per-slot ×6**, KHÔNG phải NAV namecap theo ngày; fwd2M chồng lấn nên ×6 là thô. Khớp **CHIỀU + ĐỘ BẤT ĐỐI XỨNG IS/OOS** của số đã pin, **KHÔNG phải tái lập −0.78pp** — dùng làm bằng chứng cơ chế, **đừng quote như số hệ**. *Proxy THẤT BẠI đã ghi lại thay vì giấu:* Brinson equal-weight per-slot (`mech_attribution.py`) cho dR IS **+0.052 = SAI DẤU** vs cấp hệ (−2.56pp) → **không dùng để quy công** (đúng bài học §10.4: proxy equal-weight đảo dấu với đúng họ selector này).

**Phán quyết giả thuyết dispatch:** **H1 XÁC NHẬN** (mạnh hơn dự đoán — không "tình cờ mang tin" mà là **lệch có hệ thống 1 chiều → overweight ngành cơ học**) · **H2 BÁC** (bank `pb_z` thấp nhất mỗi quý fwd2M **+5.08%** vs toàn bank +4.06% = **TỐT HƠN**, không phải bẫy rủi ro; điểm này của finding gốc đứng vững) · **H3 XÁC NHẬN 2 tầng** (linear-dead + số +0.136 không truy vết) · **H4 KHÔNG ủng hộ** (IC `pb_z` theo năm nhảy 2 chiều cả trước/sau 2020 = nhiễu, **không có breakpoint**; cái ĐỔI quanh 2020 là **mức thắng của NGÀNH** +0.47→+1.39pp và **bank share yieldcombo tự chất lên** 10.3%→35.8%) · **H5 BÁC** (vấn đề ĐÚNG ở trục bank) · **H6 mới XÁC NHẬN**.

**⚠️ RỦI RO MỚI VỀ PRODUCTION — cần Mike/user quyết, Taylor KHÔNG tự đề xuất thay đổi:** custom30V production đang mang **vị thế OVERWEIGHT NGÂN HÀNG không ai chủ ý đặt và không ai quản** — **24.1% rổ toàn kỳ, 35.8% OOS 2020+, có quý 15/30 tên** (2025Q2-Q3). Nó **không đến từ quyết định** mà là **tác dụng phụ của lỗi đo lường** (`1/PCF` cho bank) — đúng thứ user chỉ ra. Hai mặt: (a) **đã trả tiền** (+1.29pp/2M, **LOO 13/13 năm dương**, min +0.755 khi bỏ 2017) ⇒ "sửa cho đúng lý thuyết" = phá giá trị thật (đã chứng minh 2 lần: −0.78pp, −2.38pp); (b) **bằng chứng thống kê MỎNG** — spread bank−nonbank theo quý **t=0.80, hit 46.9%** (IS t=0.25/OOS t=0.83) ⇒ **KHÔNG phải alpha đã validate**, là **cú đặt cược ngành dai dẳng sinh ra do tai nạn, đang thắng**. ⇒ **Không arm nào có alpha định giá đã validate ở tầng bank; cuộc so sánh được quyết bởi một cú cược ngành ngoài ý muốn, KHÔNG phải bởi độ chính xác thước đo.** Câu hỏi cho user/Mike: **24-36% rổ đỗ tiền nằm ở ngân hàng — có phải vị thế ta MUỐN giữ có chủ ý không?** CÓ → khai báo tường minh thành rule tỷ trọng ngành kiểm soát được, thay vì để phát sinh như tác dụng phụ của lỗi đã biết. KHÔNG → **cũng đừng "sửa" bằng đổi selector** (đã đo 2 lần, tệ hơn). Đây là câu hỏi **risk-concentration** — hợp lý hỏi thêm Spyros.

**Hướng route-aware duy nhất còn logic (GHI NHẬN, KHÔNG theo đuổi — cần user/Mike quyết mở dự án riêng):** nếu vẫn muốn "chấm bank bằng thước đo của bank" mà **không phá tỷ trọng ngành** → dạng đúng là **percentile TRONG route** (ghim ~0.5, chỉ đổi "bank nào" không đổi "bao nhiêu bank"). **Prior THẤP**: `pb_z` trong bank IC +0.065 (t=1.17) — gần như không có gì để thu hoạch, `1/PE` đã làm hết việc. **Taylor KHÔNG mở.**

---

## `v4final` — thiết kế tổng hợp selector custom30V (bỏ 1/PCF khỏi financial → 1 chỉ tiêu ey → cap 30%) + DY-floor — **KHÔNG WIRE** (2026-07-14, job `Taylor_20260714_140127`)

**Việc:** thiết kế tổng hợp cuối theo 4 ý user sau chuỗi 112932 → 121717 → 132942. Nhánh MỚI trong
`custom_basket.py` (`BASKET_SELECT=eyfin|eyonly`, `BASKET_WT=fincap` + `BASKET_FIN_CAP`), không sửa
nhánh cũ. Harness `pt_v23_audit_2014.py`, `EXP_TAG` mọi arm kể cả baseline (§8), threads=1,
`BQ_LOCAL_CACHE=data/bq_cache`, **self-check 0 VND (BAL+LAG) cả 4 arm**, borrow 0, max gross 1.000.

**⚠️ ĐÍNH CHÍNH QUAN TRỌNG — "bank 24.1% / 35.8% OOS / đỉnh 50%" là ĐẾM TÊN, KHÔNG phải TỶ TRỌNG.**
Đo trên vector tỷ trọng ngày thật của chính custom30V production (`reconcile_finweight.py`):
BANK-only **count-share** full 0.239 / IS 0.102 / OOS 0.354 / đỉnh quý 0.500 → tái lập **chính xác cả
3 con số** đã lưu hành cả ngày. **Weight-share thật gần GẤP ĐÔI: BANK-only 0.444 full / 0.603 OOS;
BANK+INS+SEC 0.474 full / 0.644 OOS / 2026Q2 = 0.827.** ⇒ lời khuyên "cap 30% hợp lý" của risk-auditor
được cho trên nền 24.1% (khi đó 30% = trần rộng, gần như không ràng buộc); trên tỷ trọng thật 47% nó là
can thiệp **cắt ~½ exposure**, ràng buộc 100% ngày từ 2017Q1. **Cần đưa lại số đúng cho risk-auditor/
Spyros trước khi coi "30%" là đã có tư vấn.**

**Chuỗi ablation NEO LIỀN KỀ** (mỗi arm khác arm ngay trước ĐÚNG 1 trục — không so end-state với baseline gộp):

| arm | thay đổi vs arm trước | FULL | IS | OOS | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|---|---|---|
| **A0** `yieldcombo`+namecap (= LIVE) | — | 27.09 | 23.37 | 30.58 | 1.81 | −18.3 | 1.48 |
| **A1** `eyfin` | financial bỏ chân 1/PCF (2×ey giữ range [0,2]) | 27.17 | 23.16 | 30.95 | 1.82 | −18.1 | 1.50 |
| **A2** `eyonly` | mọi route chỉ `rank_pct(1/PE)` pool-wide | 27.04 | 23.00 | 30.85 | 1.81 | −17.6 | 1.54 |
| **A3** `eyonly`+`fincap0.30` | cap BANK+INS+SEC 30% | **26.40** | 22.45 | 30.12 | **1.75** | −17.6 | 1.50 |

- **A1−A0 = +0.08pp FULL (IS −0.21 / OOS +0.37)** — trái dấu IS/OOS, biên độ 0.1-0.4pp/12.5y ⇒ **nhiễu**.
- **A2−A0 (bước 1+2) = −0.05pp FULL / −0.37 IS / +0.27 OOS**; DD −18.3→−17.6; Calmar 1.48→1.54 ⇒
  **return-neutral, rủi ro nhích tốt nhẹ (1 đường NAV)**. **KHÔNG có bằng chứng alpha.**
- **A3−A2 (cap 30%) = −0.64pp FULL / −0.55 IS / −0.73 OOS, Sharpe −0.06, DD ĐỨNG YÊN −17.6.**

**Cap 30% = NO-GO (test lại từ đầu trên pool ĐÃ SẠCH bias PCF, đúng yêu cầu dispatch — không suy diễn
từ sector-cap NO-GO sáng nay).** Cắt exposure tài chính 47%→26% mà **MaxDD không nhúc nhích** ⇒ tập
trung tài chính **không phải nguồn drawdown** của hệ 2014-2026; cap chỉ đổi tên cầm, không đổi rủi ro
đường giá. **Giới hạn phải nói rõ:** kết luận này chỉ phủ mẫu 12.5 năm, **không** bác rủi ro đuôi/kịch
bản (sốc hệ thống ngân hàng VN chưa từng có trong mẫu); điểm risk-auditor nêu về **độ trễ cam kết CRISIS
của DT5G (enC=25 phiên)** vẫn đứng và backtest **không trả lời được**. Muốn cap → cap vì quản trị rủi ro
đuôi có tuyên bố rõ, chấp nhận trả **0.64pp/năm**, KHÔNG phải vì backtest cho thấy an toàn hơn (số nói ngược).

**Ý 4 — DY làm NGƯỠNG CHẶN GIÁ, không phải return-predictor: CLAIM CỦA USER ĐƯỢC ỦNG HỘ (6M).**
`dy_floor_test.py`: 2,878 obs / 262 mã / 48 ngày q2m5 2014-2026; DY = `Dividend_Min3Y`/`Price` (PIT
as-of `Release_Date`); downside = `min(Close)/Close₀−1` trên Close **điều chỉnh** (cổ tức đã nằm trong
đường giá ⇒ không ăn gian được). Gate: (a) downside nông hơn có ý nghĩa **VÀ** (b) return KHÔNG hơn.

| cut | h | d_maxloss (HIGH−LOW) | t | hit/ngày | d_return | t | verdict |
|---|---|---|---|---|---|---|---|
| route×date | 6M | +2.07pp | 2.75 | 77% | +0.48pp | 0.31 | **FLOOR** |
| route×date×**ey-tertile** (khử confound rẻ) | 6M | **+2.34pp** | 2.37 | 68% | +0.35pp | 0.17 | **FLOOR** |
| marginal cohort (ey rank 20-45) | 6M | +2.40pp | 2.37 | 68% | +2.95pp | 1.39 | **FLOOR** |
| (mọi cut) | 3M | +0.80…+1.53pp | 1.40-1.94 | 58-67% | — | — | **không ủng hộ** |

Sống sót **double-sort trong ey-tertile** ⇒ không phải hiệu ứng "rẻ" mà selector đã chấm. **Giới hạn
trung thực:** t lạc quan (cửa sổ 6M chồng lấn + tên tương quan) — số đáng tin hơn là hit-rate theo ngày
68-77% trên 44-48 ngày (p≈0.01); cohort biên có d_return +2.95pp (t=1.39) **không có ý nghĩa nhưng
không nhỏ** — nếu N lớn hơn làm nó significant thì DY tụt về return-predictor và thuộc trục xếp hạng,
không phải rule chặn; DY>0 chỉ 70.4% obs ⇒ rule phải fail-open. **Đề xuất tích hợp (pre-registered,
CHƯA CHẠY): tie-break CHỈ trong dải biên ey rank ~20-45, thiếu DY = no-op** — là arm A4 riêng, cần
selfcheck + N-ledger + skeptic. **Job này KHÔNG chạy A4.**

**Selfcheck `v4final_selector_selfcheck.py` 12/12 PASS** (đo trên vector tỷ trọng thật, không tin code):
fincap@0.30 **max 0.3000 / mean 0.2995 / 1090 ngày / 0 vượt / 0 infeasible**, Σw=1 (err 4.4e-16); full
panel 0.0% ngày >30%. `eyonly` không đọc PCF (đảo toàn bộ PCF → 0 tên đổi); `eyfin` không đọc PCF cho
financial (255 pick, 0 khác) + **negative control**: cùng phép phá CÓ làm `yieldcombo` đổi 17/18 rebal;
OFF-path byte-identical vs `git show HEAD:custom_basket.py`.
**BUG THẬT bắt được nhờ đo:** `weight_scheme=sectorcap` **có sẵn KHÔNG giữ được cap** (`_cap_names`
chạy SAU `_cap_sector`, water-fill phần dư vào mọi tên chưa chạm trần **kể cả financial**) → cap danh
nghĩa 0.30 thực giao **mean 0.427 / max 0.542, vi phạm 1090/1090 ngày**. ⇒ dùng `_cap_group_jointly`
(ngân sách nhóm trước, name-cap water-fill TRONG nhóm) thay vì tái dùng `sectorcap` như dispatch gợi ý;
nếu tái dùng, A3 đã đo nhầm cap 0.43 rồi dán nhãn 0.30.

**Rổ @ rebal 2026-05-05** (`basket_20260505.md`): A0 (LIVE) financial **18/30**; A1 17/30 (giữ 29/30,
IN `HPG` / OUT `MBS`); A2 & A3 **cùng 16/30** (giữ 27/30, IN `HPG`,`PNJ`,`SAB` / OUT `MBS`,`VCB`,`VGC`).
A3 chọn **cùng 30 tên như A2** — cap là rule tỷ trọng, không đổi thành phần: thành phần đổi rất ít
(27/30) trong khi tỷ trọng đổi rất lớn (47%→26%). `HPG IN` trùng hướng plan 07-14/07-15 (bán HPG)
**nhưng KHÔNG phải căn cứ đảo lệnh** (chưa skeptic, delta trong nhiễu, không đề xuất wire).

**VERDICT: KHÔNG WIRE GÌ, production 0 chạm, không đảo lệnh plan.**
- Bước 1+2 (`eyonly`) = ứng viên hợp lệ **về NGUYÊN LÝ** (bỏ thước đo sai bản chất cho bank; 2→1 chỉ
  tiêu; triệt tiêu lớp lỗi thang-đo cross-route đã giết `v3route`) với bằng chứng **"không tốn gì"**
  + rủi ro nhích tốt. **KHÔNG có bằng chứng alpha** — wire (nếu có) phải vì tính đúng đắn mô hình,
  không vì kỳ vọng lãi hơn. **Bắt buộc quant-skeptic.**
- Bước 3 (cap 30%) = **NO-GO**. Ý 4 (DY floor) = **ỦNG HỘ 6M**, chờ quyết mở arm A4.

**Baseline note:** A0 = **27.09** khớp vintage hôm nay (registry mục `Taylor_20260714_121717` dòng
"vintage hôm nay 27.09% vs pin 27.84% = data-drift, không phải bug") ⇒ control tái lập sạch, delta
neo hợp lệ. **Re-pin R3 vẫn TREO** — job này không tự re-pin.

**Artifacts** (`mike/agents/Taylor/v4final_exp/`): `run_arms.sh`, `dy_floor_test.py`,
`basket_picture.py`, `reconcile_finweight.py`, `logs/*`, `dy_floor_{panel,results}.csv`,
`fin_weight_{by_quarter,summary}.csv`, `finweight_definitions.csv`, `basket_20260505.md`.
Code: `custom_basket.py` (nhánh mới `eyfin`/`eyonly`/`fincap`), `v4final_lib.py`,
`v4final_selector_selfcheck.py`. Chi tiết đầy đủ: `mike/agents/Taylor/route_aware_selector_framework.md` §12.
