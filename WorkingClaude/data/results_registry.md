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
