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
