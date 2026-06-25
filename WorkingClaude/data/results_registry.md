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
