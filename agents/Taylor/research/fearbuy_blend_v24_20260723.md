# Fear-buy sleeve → BLEND vào production V2.4 (adaptive-threshold, blue-chip, concentrated)

> Taylor (Quant/Algo), job `Taylor_20260723_163630`, 2026-07-23. **RESEARCH-ONLY — KHÔNG wire.**
> Mandate user (blend ưu tiên cao): *"set điều kiện chặt tăng win-rate → blend vào production ở mức
> ưu tiên cao, mua nắm giữ ≥18 tháng, đặc biệt blue-chip… giúp production hiệu quả HẲN LÊN về CAGR,
> đánh đổi nhỏ MaxDD. Điều kiện mua ADAPTIVE theo thị trường (càng xấu càng phải rẻ mới mua)."*
> Nối tiếp: FEARBUY v1 (`fearbuy_systematic_screen_20260723.md`, N=237) + sizing scenario (N=2).
> Artefacts tái lập: `fearbuy_blend/` (panel.sql/csv, prices.sql/csv, phase_ab.py, phase_deals.py,
> blend.py, verify.py). Baseline = univpit R3 control (`..._exp_discC4_control_univpit.csv`).

---

## 0. TL;DR — kết luận thẳng (khác kỳ vọng user)

Tôi thiết kế đủ 5 điểm user yêu cầu (adaptive threshold liên tục, blue-chip filter, concentrated
sizing, blend đầy đủ vào V2.4, đề xuất phân bổ). Hai kết quả lớn:

1. **SCREEN chạy tốt** — adaptive threshold + blue-chip filter làm win-rate LÊN, không xuống:
   ADV≥20B → **win-rate 77%, median ex24 +41%, sign-test 5/5 crisis-year p=0.031**. Blue-chip lọc
   được value-trap (win-rate 64%→78% khi tăng sàn ADV). Thiết kế **đúng như user hình dung ở tầng
   chọn mã.**

2. **NHƯNG blend vào V2.4 KHÔNG "hiệu quả hẳn lên về CAGR" như kỳ vọng.** Đo thật trên NAV ngày:
   - **Bản swap (giữ reserve trong V2.4, rút ra lúc khủng hoảng — thực tế nhất): dCAGR chỉ +0.04…
     +0.09pp, MaxDD XẤU đi** ở w≥15% (−1.7 → −4.0pp). Gần như bằng 0.
   - **Bản cash-aware lạc quan nhất (rót từ tiền mặt phòng thủ ở đáy): dCAGR +1.7pp @w10% full**,
     nhưng **+2.96pp toàn bộ đến từ OOS 2020+** (COVID-V + 2022-23), IS 2014-19 chỉ +0.39pp;
     MaxDD vẫn xấu đi ở w≥15%.

**Root cause (điểm cốt lõi):** **V2.4 ĐÃ TỰ bắt hồi-phục-sau-khủng-hoảng** qua CAPIT (bear-washout)
+ LAG re-risk + parking. Trong đúng cửa sổ sleeve hoạt động, **sleeve annualized +26.9% < V2.4
+29.9%** — tức là **sleeve THUA chính V2.4** ở chỗ nó định thêm giá trị. Sleeve chỉ là một "long
high-beta cyclical/financial tập trung" — trùng lặp (redundant) với cỗ máy hồi-phục sẵn có của hệ,
Sharpe thấp hơn, và ở mức tập trung cao thì **làm sâu MaxDD** (mua cyclical high-beta ở đáy = rơi
tiếp trước khi bật).

**Verdict: KHÔNG đề xuất blend ưu tiên cao / reserve NAV riêng.** Giữ như **overlay cơ hội NHỎ
(≤5-10% NAV, chỉ rót từ tiền-mặt-đáy-khủng-hoảng)** — bảo hiểm/optionality, không phải core alpha.
Con số trung thực để kỳ vọng: **+0.5 … +1.5pp CAGR trong kịch bản rót-vốn thuận lợi, ~0 nếu swap,
kèm rủi ro MaxDD xấu đi nếu tập trung mạnh.** Xem §6 cho phân biệt QUAN TRỌNG market-wide (trùng lặp)
vs idiosyncratic-scandal (mới là chỗ fear-buy có giá trị riêng — chính là TV1/DGC/PNJ discretionary).

---

## 1. Điểm #4 — Hàm ngưỡng ADAPTIVE (thiết kế mới quan trọng nhất)

**Đặc trưng thị trường liên tục:** `s = −mkt_dd` = drawdown VNINDEX từ đỉnh 1 năm (0 = đỉnh, càng lớn
càng xấu). Point-in-time, causal, đã dùng trong FEARBUY v1. (Đã đọc job `Taylor_20260723_135623`:
kết luận ở đó là *đặc trưng liên tục KHÔNG thắng discrete DT5G gate cho LAG regime-sizing* — bài học
mang sang: đừng kỳ vọng continuous-feature tự động thắng; phải đo. Ở đây tôi CẦN liên tục vì user
yêu cầu ánh xạ mức-xấu→ngưỡng-định-giá, không phải on/off.)

**Hàm ngưỡng (đơn điệu giảm — thị trường càng xấu, PB yêu cầu càng THẤP = càng rẻ mới mua):**
```
PB_max(s) = clip( pb_hi − slope·(s − s0),  pb_lo,  pb_hi )
qualify   = (s ≥ s_min) ∧ (PB ≤ PB_max(s)) ∧ golden-floor ∧ core-cash
chọn:  s_min=0.20, s0=0.20, pb_hi=1.00, pb_lo=0.40, slope=2.0
```
Đọc bằng số: dd −20% → cho phép PB≤1.00; dd −35% → PB≤0.70; dd −50% → PB≤0.40 (sàn). golden-floor =
ROE_Min3Y≥0; core-cash = NP_P0>0 ∧ CF_OA_P0>0 (giữ nguyên v1).

**Calibrate ngược trên panel lịch sử (2508 episode, universe_pit PIT, dedup ticker-năm, col ex24):**

| Gate | N | median ex24 | mean | win-rate | sign-test crisis-yr |
|---|---|---|---|---|---|
| Binary v1 (dd<−30 & PB<0.7) | 330 | +23.8% | +58% | 64% | 5/6 p=0.11 |
| **Adaptive (trên)** | 819 | +18.0% | +43% | 61% | 7/9 p=0.09 |
| Adaptive tighter (s_min .25) | 386 | +21.9% | +59% | 63% | 7/9 p=0.09 |

→ Adaptive **KHÔNG vượt trội binary v1 về precision điểm**, nhưng (a) đúng ý thiết kế (liên tục, không
on/off — bắt cả pullback vừa với PB nới, đòi cực rẻ ở crash sâu), (b) **N gấp ~2.5× binary** ở
precision tương đương → phủ nhiều regime hơn (robustness cấp-crisis 7/9 vs 5/6). Giá trị adaptive =
**graded participation + robustness**, không phải nhảy vọt win-rate.

---

## 2. Điểm #2 — Blue-chip filter (ADV) — VÀ một cảnh báo trung thực

Sàn thanh khoản ADV (= Volume_1M × Price, VND thật tại entry). Blue-chip cải thiện **đơn điệu** độ
tin cậy:

| Rule = adaptive + ADV floor | N | median ex24 | win-rate | sign-test |
|---|---|---|---|---|
| ADV≥0 | 818 | +18% | 61% | 7/9 p=0.09 |
| ADV≥5B | 137 | +21% | 67% | 6/8 |
| **ADV≥10B** | 84 | +22% | 69% | **6/6 p=0.016** |
| **ADV≥20B** | 44 | +41% | **77%** | **5/5 p=0.031** |

Blue-chip **lọc value-trap** (micro-cap panic hay là bẫy cấu-trúc) → win-rate lên. **Đây là kết quả
tốt & phản trực giác dễ chịu: cổ phiếu thanh khoản lớn crash về gần/dưới book trong panic sâu hồi
phục ĐÁNG TIN hơn micro-cap.**

> ⚠️ **CẢNH BÁO trung thực — "blue-chip" ở đây KHÔNG phải compounder phòng thủ.** Danh sách ADV≥20B
> thực tế = **cyclical/financial/BĐS high-beta bị đánh sập**: SHB, KBC, HSG, HHV, LCG, TNG, PVS, PVD,
> STB, LPB, ASM, GEX, HPX, BCG… **Blue-chip chất-lượng-phòng-thủ thật (VNM/FPT/MWG/VCB/ACB) HIẾM KHI
> về PB<0.7** kể cả trong crash — chính vì chúng là quality. DGC 2020 (PB 0.73) là ngoại lệ và nó là
> **cyclical hoá chất**, không phải defensive. ⇒ "blue-chip fear-buy" về mặt vận hành = **"thanh khoản
> lớn + sàn chất lượng golden-floor"**, KHÔNG phải "mua Vinamilk lúc sợ hãi". User cần biết rõ điều
> này: pattern kiếm tiền là **deep-value high-beta mean-revert**, không phải "gom compounder giá rẻ".

Market-cap: ADV≥20B trong 2018-2023 đã ≈ lọc mid/large-cap; không thêm mcap floor riêng (ADV là ràng
buộc vận hành thật để giải ngân size). Ở NAV production hiện tại (~1,82 tỷ) thanh khoản KHÔNG binding
kể cả deal 10-15% NAV; sàn ADV chủ yếu là **proxy chất lượng + chuẩn bị scale** (backtest chạy @50B).

---

## 3. Điểm #1 & #3 — Concentrated sizing + BLEND đầy đủ vào V2.4

**Mô hình blend (portfolio-overlay, auditable, KHÔNG đụng canonical CSV — tránh bẫy §8):**
`r_comb(t) = (1−w(t))·r_V24(t) + w(t)·r_sleeve(t)`; w(t)=w_sleeve khi ≥1 tên đang giữ, =0 khi rỗng.
Sleeve = basket equal-weight các tên qualify, mỗi tên buy&hold 375 phiên (~18m). r_V24 = NAV ngày
baseline univpit R3. Test maxconc (số tên đồng thời) & w_sleeve.

**Baseline V2.4 (univpit control):** CAGR 27.16% / Sharpe 1.80 / MaxDD −18.1% / Calmar 1.50
(IS14-19 23.17% / OOS20+ 30.91%).

### 3a. Bản SWAP (reserve giữ trong V2.4, rút ra lúc khủng hoảng — thực tế nhất)
adaptive+ADV10B, maxconc=5:

| w_sleeve | CAGR | Sharpe | MaxDD | Calmar | dCAGR | dMaxDD |
|---|---|---|---|---|---|---|
| 0.05 | 27.21% | 1.79 | −18.6% | 1.47 | +0.05 | −0.5 |
| 0.10 | 27.23% | 1.76 | −19.0% | 1.43 | +0.07 | −0.9 |
| 0.15 | 27.24% | 1.73 | −19.5% | 1.40 | +0.08 | −1.4 |
| 0.20 | 27.24% | 1.68 | −21.2% | 1.28 | +0.08 | −3.1 |

→ **dCAGR ~0 (+0.05-0.08pp), MaxDD xấu dần, Calmar xấu dần.** IS 2014-19 thực ra là **−0.97pp (drag)**,
OOS +1.04pp. Tập trung hơn (maxconc nhỏ, w lớn) KHÔNG cứu CAGR mà **khuếch đại MaxDD**. DE≤2.5 ex-fin
làm TỆ hơn (−0.20pp) vì loại mất bank-winner SHB/LPB/STB.

### 3b. Bản CASH-AWARE (rót từ tiền-mặt-phòng-thủ ở đáy trước, chỉ chiếm book khi w>cash) — cận trên
Baseline **giữ tiền mặt lớn ở đáy khủng hoảng** (invested-fraction đáy ~0.53, tức ~47% cash). Rót
sleeve từ phần cash đó = ADDITIVE:

| w | CAGR | Sharpe | MaxDD | Calmar | dCAGR | dMaxDD |
|---|---|---|---|---|---|---|
| 0.05 | 28.11% | 1.80 | −17.8% | 1.58 | +0.95 | +0.3 |
| 0.10 | 28.85% | 1.77 | −18.6% | 1.55 | **+1.69** | −0.5 |
| 0.15 | 29.37% | 1.74 | −21.5% | 1.37 | +2.21 | −3.4 |
| 0.20 | 29.60% | 1.69 | −24.2% | 1.22 | +2.44 | −6.1 |

→ Cận-trên: **+1.7pp @w10%, Calmar 1.50→1.55 (chớm cải thiện)**; nhưng **w≥15% MaxDD sập −3.4→−6.1pp,
Calmar rơi dưới baseline**. IS 2014-19 chỉ **+0.39pp**, OOS 2020+ **+2.96pp** → **edge blend gần như
TOÀN BỘ đến từ OOS (COVID-V 2020 + 2022-23)**.

**Sự thật nằm GIỮA 3a và 3b** (đáy có cash → phần additive; nhưng V2.4 tái giải ngân cash đó trong
1-3 tháng → phần còn lại là swap). Ước lượng trung thực: **+0.5 … +1.5pp CAGR @w≈5-10%, Calmar
~neutral, MaxDD ~phẳng-đến-hơi-xấu.** KHÔNG phải "hiệu quả hẳn lên".

---

## 4. Vì sao blend không cộng thêm — REDUNDANCY test (bằng chứng quyết định)

Trong đúng cửa sổ sleeve hoạt động (60% thời gian 2018-2024):
- **Sleeve annualized +26.9%  <  V2.4 annualized +29.9%.** Sleeve THUA chính V2.4.
- corr(sleeve, V2.4) ngày = 0.54; sleeve thắng V2.4 chỉ **52% số ngày** (đồng xu).
- Baseline invested-fraction lúc sleeve active: mean 0.59 (không hề "toàn tiền mặt để mà additive").

→ **V2.4 đã kiếm tiền hồi-phục-khủng-hoảng qua CAPIT + LAG re-risk + parking.** Sleeve fear-buy
(market-adaptive) **kích hoạt ĐÚNG LÚC V2.4 cũng đang re-risk** → chỉ là đổi một xe bắt-hồi-phục này
lấy một xe khác, không cộng alpha. Excess-vs-VNINDEX +40% của sleeve **không** thành excess-vs-V2.4,
vì V2.4 tự nó đã thắng VNINDEX ở các cửa sổ đó.

**Per-crisis (sleeve standalone mean r24):** 2010 −29% · 2011 −57%(PVX) · 2012 +50% · 2018 +31% ·
2019 +134% · 2020 +255% · 2022 +55% · 2023 +54%. → Screen tốt & đa-regime (6/8 dương), NHƯNG lợi ích
BLEND dồn về 2019-2020. Theo đúng kỷ luật walk-forward của đội (edge chỉ hiện OOS, do 1-2 regime
gánh = reshuffle-luck, không bền) — **blend này FAIL chuẩn robust để wire như core-enhancer.**

---

## 5. Multiple-testing & caveat trung thực (bắt buộc)
- **N_eff ≈ 6-8 cụm khủng hoảng, KHÔNG phải 84/44 episode** (tương quan chéo trong cùng crisis).
- Đã grid nhiều tham số (adaptive params × ADV floor × maxconc × w) → **multiple testing**; config
  chọn **CHƯA** DSR-validated. Không tính DSR (episode returns cross-correlated → iid giả định thổi
  phồng, đúng lý do đã nêu ở FEARBUY v1). Thống kê trung thực = sign-test cấp-crisis (5/5 p=0.031).
- Cận-trên cash-aware **lạc quan** (giả định rót được từ idle cash; thực tế V2.4 tái giải ngân nhanh).
- Chưa mô hình chi phí impact/slippage khi gom size lớn ở đáy panic — số là lý thuyết mid-price.
- **Nếu user vẫn muốn overlay nhỏ → PHẢI qua `bin/verify_finding.sh` (quant-skeptic) trước.** Chưa
  làm trong job này (khuyến nghị chính là KHÔNG wire như core, nên skeptic-gate để dành cho quyết
  định overlay nhỏ nếu user chọn).

---

## 6. Phân biệt QUAN TRỌNG — market-wide (trùng lặp) vs idiosyncratic-scandal (giá trị riêng)

Điểm #4 (adaptive theo MARKET drawdown) kéo sleeve về đúng **case khủng-hoảng-toàn-thị-trường** — nơi
V2.4 ĐÃ hoạt động → trùng lặp → blend ~0. Nhưng fear-buy có **một chỗ giá trị riêng KHÔNG trùng V2.4**:

- **Market-wide fear-buy** (VNINDEX −30%, adaptive): **redundant với V2.4** → blend value thấp (nghiên
  cứu này).
- **Idiosyncratic-scandal fear-buy** (1 blue-chip sập vì bê bối lãnh đạo riêng lẻ TRONG KHI thị trường
  vẫn ổn — DGC 03/2026, TV1, PNJ 2015/2026): **V2.4 KHÔNG bắt** (không có tín hiệu market-crisis, CAPIT
  không fire, anomaly-gate còn chủ động LOẠI các tên này khỏi CAPIT). **Đây mới là chỗ sleeve
  discretionary cộng thêm thật** — và nó vốn đã là khung `calculated_fear_state_backstop.md` (cap
  ≤0.5-1.0% NAV, due-diligence từng tên, user duyệt).

⇒ **Khuyến nghị giữ nguyên hai khung tách biệt**, KHÔNG gộp systematic-market-fear thành book ưu tiên
cao. Systematic screen = **candidate-generator khi thị trường crash sâu** (bổ trợ CAPIT, không thay).

---

## 7. Điểm #5 — Đề xuất phân bổ vốn (chỉ đề xuất, user quyết)

1. **KHÔNG dựng thành book ngang hàng BAL/LAG, KHÔNG reserve NAV riêng cố định.** Reserve tiền-mặt chờ
   fear-buy = trả 27% CAGR cơ hội cho ~85% thời gian không khủng hoảng → lỗ ròng. Giữ trong V2.4 rồi
   rút lúc crisis = swap ~0 (bằng chứng §3a).
2. **Nếu user vẫn muốn overlay cơ hội:** trần **≤5-10% NAV**, **chỉ rót từ phần tiền-mặt phòng thủ khi
   DT5G ∈ {CRISIS,BEAR} VÀ adaptive-screen fire** (không rút từ book đang chạy alpha), maxconc ~3-5,
   giữ 18m. Kỳ vọng trung thực **+0.5…+1.5pp CAGR (kịch bản thuận)**, Calmar ~neutral. **KHÔNG vượt
   w=10%** (MaxDD sập). Coi là insurance/optionality, không core.
3. **Idiosyncratic discretionary (TV1/DGC/PNJ) giữ nguyên** khung backstop hiện có (≤1% NAV/tên,
   due-diligence + user duyệt). Đây mới là nhánh fear-buy cộng thêm thật.
4. **Systematic market-fear screen**: nâng `fearbuy_weekly_scan.sh` thành định lượng (adaptive+ADV≥10B),
   dùng làm **candidate-generator + bổ trợ CAPIT** khi VNINDEX crash sâu — KHÔNG auto-buy.

**Một câu cho user:** ý tưởng đúng ở tầng CHỌN MÃ (adaptive + blue-chip cho win-rate 77%), nhưng
blend vào V2.4 **không "hiệu quả hẳn lên"** vì V2.4 đã tự bắt hồi-phục-khủng-hoảng — sleeve trùng
lặp, thắng thêm chỉ khiêm tốn (+0.5-1.5pp kịch bản thuận) và **đánh đổi MaxDD BẤT LỢI nếu tập trung
mạnh** (ngược với kỳ vọng "concentrated big deals"). Giá trị fear-buy thật nằm ở case
**idiosyncratic-scandal** (thị trường ổn, 1 tên sập) — chỗ V2.4 không với tới — và chỗ đó vốn đã
được khung discretionary phục vụ.
