---
kind: research-report
title: Ma trận chiến lược DT5G × Value Radar (5 regime × 3 zone)
author: Taylor (Quant/Algo)
job: Taylor_20260822_101400
date: 2026-08-22
status: DESCRIPTIVE MAP — KHÔNG phải tín hiệu sizing (0/24 ô qua BH FDR 10%; DSR < 0,95)
artifacts: mike/agents/Taylor/research/strategy_regime_matrix_20260822/
---

# Ma trận chiến lược DT5G × Value Radar

**Câu hỏi:** dưới điều kiện thị trường nào thì BAL / LAG / Alpha Lens phát huy tối đa?

## ⚠️ ĐỌC TRƯỚC — kết luận thống kê đứng trên mọi con số bên dưới

Tôi chạy **24 kiểm định hợp lệ** (15 ô × 3 chiến lược, loại các ô n<100 phiên) trên giả thuyết
H₀ = "excess return so với VNINDEX trong ô này = 0", block-bootstrap L=20 phiên, 20.000 lần lấy mẫu.

| Chỉ tiêu | Kết quả |
|---|---|
| N_trials khai báo | **24** |
| Số ô qua **BH (FDR 10%)** | **0 / 24** |
| Số ô qua **Bonferroni** | **0 / 24** |
| p nhỏ nhất | 0,0149 (NEUTRAL+RẺ, LAG) — ngưỡng BH hạng 1 = 0,10 × 1/24 = **0,0042** |
| **DSR** ô mạnh nhất (NEUTRAL+RẺ, BAL, SR_excess +2,15) | **0,830** → **RED FLAG** (<0,95) |
| DSR NEUTRAL+RẺ LAG (SR +1,56 vs SR*_max kỳ vọng N=24 = +1,49) | **0,535** → RED FLAG |

⇒ **Ma trận này là BẢN ĐỒ MÔ TẢ để đọc bối cảnh, KHÔNG phải bộ luật sizing.** Không một ô nào
đủ mạnh để wire vào allocator, và tôi **không đề xuất** thay đổi allocator hay `trading_rules.json`
từ báo cáo này. Điều này khớp tiền lệ đã có: Phụ lục C `market_regime_probability_20260729.md`
cũng cho **0/17 lăng kính** qua BH — Value Radar đã được đóng dấu **DISPLAY-ONLY** vì đúng lý do này.

### Hai confound cấu trúc phải mang theo khi đọc mọi con số

**Confound 1 — Value Radar zone ≈ THỜI KỲ, không phải một biến độc lập với thời gian.**
Đếm phiên theo năm × zone (2014-01→2026-06, 3.107 phiên):

| Năm | RẺ | TRUNG TÍNH | ĐẮT |
|---|---:|---:|---:|
| 2014 | 3 | 244 | 0 |
| 2015 | 68 | 180 | 0 |
| 2016 | 28 | 192 | 31 |
| 2017 | 0 | 0 | **250** |
| 2018 | 0 | 0 | **250** |
| 2019 | 0 | 24 | **226** |
| 2020 | 37 | 199 | 16 |
| 2021 | 0 | 7 | **243** |
| 2022 | **155** | 76 | 18 |
| 2023 | **249** | 0 | 0 |
| 2024 | **172** | 78 | 0 |
| 2025 | **125** | 124 | 0 |
| 2026 | 1 | 108 | 3 |

Zone **ĐẮT ≡ 2017-2019 + 2021**; zone **RẺ ≡ 2015-16 + 2022-2025**. Gần như không chồng lấn.
Nên "BAL trong ô ĐẮT" thực chất đọc là "**BAL trong giai đoạn 2017-19/2021**" — mọi khác biệt
giữa 2 zone có thể là khác biệt CHẾ ĐỘ THỊ TRƯỜNG của 2 kỷ nguyên, không phải hiệu ứng định giá.
Đây là lý do vật lý khiến không ô nào qua được đa kiểm định: **n hiệu dụng ≈ số kỷ nguyên (2-3),
không phải số phiên (hàng trăm).**

**Confound 2 — DT5G state là HÀM CỦA GIÁ, nên "return theo state" một phần là cơ học.**
VNINDEX annualised trong từng state: CRISIS −8,3% · BEAR −21,2% · NEUTRAL +16,6% · BULL +26,9% ·
EX-BULL +63,0%. Đó là **định nghĩa** của state, không phải edge. ⇒ Chỉ đọc cột **excess vs VNI**
trong ô, đừng đọc cột CAGR tuyệt đối như thành tích.

**Confound 3 — EX-BULL và BEAR+ĐẮT không có mẫu.** EX-BULL chỉ có 60 phiên / 2 đoạn
(31 TRUNG TÍNH + 29 ĐẮT); BEAR+ĐẮT có 11 phiên / 1 đoạn. Số CAGR annualised của các ô này
(vd EX-BULL+ĐẮT BAL **+334,8%**) là **phép ngoại suy 29 phiên ra 1 năm — KHÔNG được trích dẫn.**

---

## 1. Nguồn dữ liệu & self-check

| Trục / chuỗi | Nguồn | Status registry |
|---|---|---|
| DT5G 5-state | cột `state` trong DAILY rows của **pin R3 2026-08-03** (engine `pt_v23_audit_2014.py`, chính là chuỗi DT5G production đã dùng để chạy backtest) | CANONICAL |
| Xác nhận state hôm nay | `tav2_bq.vnindex_5state_dt5g_live` — `state=3` (NEUTRAL) liên tục 08-14→08-21 | CANONICAL |
| BAL / LAG NAV theo phiên | `nav_bal_ref` / `nav_lag_ref` — sổ cái tham chiếu 25B độc lập của từng book | pin R3, self-check 0 VND |
| NAV hệ thống | `combined_nav = cap_bal + cap_lag` (allocator band ±10pp) | " |
| Value Radar | `value_radar.load_series()` trên `data/value_radar_series.csv` | CANONICAL, **DISPLAY-ONLY** |
| Alpha Lens | `tav2_bq.ticker.Close` cho FPT/ACB/MBB/HDB | CANONICAL |

**Self-check đã chạy (part1.log):**
- `max |combined_nav − (cap_bal + cap_lag)| = 0,000366 VND`
- `nav_identity BAL = 0,000183 VND · LAG = 0,000183 VND` (NAV book = cash + stocks + etf)
- 3.107 phiên, radar score NaN = 0/3.107
- **Chú ý phương pháp:** dùng `nav_*_ref` (sổ cái độc lập) chứ KHÔNG dùng `cap_*` cho return
  từng book — 37 lần allocator rebalance làm `cap_*` nhảy vì **chuyển vốn**, không phải lãi/lỗ.
  `nav_*_ref` không bị ảnh hưởng ⇒ không cần mask ngày nào.
- Radar dùng `_roll_pct` — đã đọc code, **nhân quả** (`h[:-1] < v[i]`, cửa sổ lùi 2500 phiên).
  Vẫn còn bias đã biết: 26 mốc lãi suất neo hồi tố 1 lần 2026-06-19 ⇒ **thành phần spread mang
  bias "biết trước"** ở phần lịch sử (bẫy #3 registry). Đây là 1/3 của composite.

---

## 2. MA TRẬN 5 × 3

Ký hiệu: `CAGR` = annualised trong các phiên thuộc ô (gross backtest, đã trừ TC 0,1%/chiều của
engine). `ex` = excess vs VNINDEX cùng phiên. `ep` = số đoạn liên tục (≈ số sự kiện độc lập).
🔴 = mẫu quá nhỏ, không đọc.

| Regime | Zone | phiên | ep | radar TB | w_LAG | VNI | **BAL** | **LAG** | COMB | **AL4** | BALex | LAGex | ALex |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CRISIS | RẺ | 132 | 12 | 17,0 | 0,50 | −16,1% | +4,7% | +2,1% | +2,6% | −17,8% | +20,8 | +18,2 | −1,6 |
| CRISIS | TRUNG TÍNH | 246 | 16 | 52,2 | 0,50 | −3,2% | +10,8% | **+25,4%** | +18,6% | +2,6% | +14,0 | +28,7 | +5,8 |
| CRISIS | ĐẮT | 111 | 10 | 78,6 | 0,50 | −9,5% | **−24,8%** | −5,5% | −16,0% | +11,1% | **−15,3** | +4,0 | +20,6 |
| BEAR | RẺ | 170 | 6 | 17,0 | 0,00 | −25,6% | +0,8% | (+11,4%)* | +0,4% | −10,1% | +26,4 | (+36,9)* | +15,5 |
| BEAR | TRUNG TÍNH | 60 | 4 | 52,7 | 0,00 | −23,2% | −5,2% | (−15,8%)* | −8,8% | −12,4% | +18,0 | (+7,4)* | +10,8 |
| BEAR | ĐẮT | 🔴 11 | 1 | 79,3 | 0,00 | — | — | — | — | — | — | — | — |
| **NEUTRAL** | **RẺ** ⬅ **HIỆN TẠI** | 440 | 18 | 22,4 | 0,56 | −6,0% | +10,7% | +14,5% | +13,9% | +11,5% | **+16,7** | **+20,5** | **+17,5** |
| NEUTRAL | TRUNG TÍNH | 802 | 25 | 47,9 | 0,57 | +27,8% | +37,0% | +39,2% | +41,6% | +32,3% | +9,2 | +11,5 | +4,6 |
| NEUTRAL | ĐẮT | 653 | 11 | 81,7 | 0,54 | +20,5% | +42,5% | +42,1% | +40,9% | +32,6% | +22,0 | +21,6 | +12,1 |
| BULL | RẺ | 96 | 6 | 20,9 | 0,64 | −5,9% | −5,5% | **+35,9%** | +18,3% | +0,6% | +0,4 | +41,9 | +6,5 |
| BULL | TRUNG TÍNH | 93 | 10 | 51,7 | 0,60 | +40,7% | **+90,2%** | +25,8% | +46,9% | +47,5% | +49,5 | −14,8 | +6,8 |
| BULL | ĐẮT | 233 | 8 | 81,5 | 0,60 | +37,7% | +84,0% | +46,8% | +62,6% | +77,9% | +46,3 | +9,0 | +40,2 |
| EX-BULL | TRUNG TÍNH | 🔴 31 | 2 | 51,7 | 0,65 | +15,6% | −31,1% | +47,1% | +11,0% | +55,2% | −46,7 | +31,5 | +39,6 |
| EX-BULL | ĐẮT | 🔴 29 | 2 | 75,8 | 0,65 | +135% | +335% | +166% | +222% | +214% | — | — | — |
| EX-BULL | RẺ | **0** | 0 | — | — | — | — | — | — | — | — | — | — |

\* **BEAR: `w_LAG = 0`** ⇒ sổ LAG **không nhận vốn** trong BEAR. Con số LAG trong 2 ô BEAR là return
của **sổ cái tham chiếu** (giả định nếu có vốn), **KHÔNG** vào NAV hệ thống. Xem §5 edge-signal #4.

### Tổng hợp theo regime (gộp mọi zone)

| Regime | phiên | VNI | BAL | LAG | COMB | AL4 | BAL Sharpe | LAG Sharpe |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CRISIS | 489 | −8,3% | −0,1% | +11,3% | +5,5% | −1,6% | 0,03 | 0,70 |
| BEAR | 241 | −21,2% | +0,5% | (+0,6%) | −0,2% | −6,7% | 0,11 | — |
| NEUTRAL | 1.895 | +16,6% | +32,2% | +34,0% | **+34,4%** | +27,2% | 1,90 | 1,82 |
| BULL | 422 | +26,9% | +59,3% | +39,4% | +47,9% | +49,9% | 1,96 | 2,74 |
| EX-BULL | 🔴 60 | +63,0% | +67,9% | +96,0% | +85,6% | +118,2% | 1,64 | 4,17 |

### Tổng hợp theo zone (gộp mọi regime)

| Zone | phiên | ep | VNI | BAL (ex) | LAG (ex) | COMB (ex) | AL4 (ex) |
|---|---:|---:|---:|---:|---:|---:|---:|
| RẺ | 838 | 26 | −11,9% | +5,7% (+17,7) | +14,0% (+26,0) | +9,7% (+21,6) | +0,5% (+12,5) |
| TRUNG TÍNH | 1.232 | 42 | +18,5% | +29,9% (+11,4) | +32,2% (+13,7) | +33,3% (+14,9) | +24,8% (+6,3) |
| ĐẮT | 1.037 | 15 | +23,5% | +45,3% (+21,9) | +38,1% (+14,6) | +41,0% (+17,5) | +43,2% (+19,8) |

**Giả thuyết trong đề bài BỊ BÁC:** đề bài đoán "RẺ+BULL/NEUTRAL có edge tốt nhất cho BAL; ĐẮT+EX-BULL
kém nhất". Dữ liệu nói ngược: **excess của BAL trong zone ĐẮT (+21,9pp) CAO HƠN trong zone RẺ
(+17,7pp)**, và ô BAL tuyệt vời nhất là **BULL+ĐẮT (+46,3pp)** chứ không phải BULL+RẺ (+0,4pp).
Lý giải cơ học chứ không phải "momentum thích bubble": zone ĐẮT ≡ 2017-19/2021 = **thị trường
xu hướng mượt**, đúng môi trường momentum SIGNAL_V11 sống; zone RẺ ≡ 2022-25 = **thị trường
sideway/whipsaw**, môi trường momentum kém nhất. Lại là confound-1 nói chuyện.

### Walk-forward zone (IS 2014-19 / OOS 2020+) — excess vs VNI

| Zone | IS BAL | OOS BAL | IS LAG | OOS LAG | IS AL4 | OOS AL4 |
|---|---:|---:|---:|---:|---:|---:|
| RẺ (n_IS=99!) | +35,5 | +14,6 | +20,3 | +25,6 | +33,5 | +11,4 |
| TRUNG TÍNH | +3,7 | +14,3 | **+22,8** | **−2,3** | −1,6 | +14,0 |
| ĐẮT | +8,0 | +40,8 | +6,2 | +24,0 | +14,6 | +21,2 |

**Chỉ dấu hiệu duy nhất giữ được DẤU ở cả IS và OOS cho cả 3 chiến lược: zone ĐẮT và zone RẺ.**
Zone TRUNG TÍNH thì LAG **đổi dấu** (+22,8 → −2,3). Nhưng RẺ có n_IS chỉ 99 phiên ⇒ chân IS gần như
rỗng. ⇒ Không có kết luận zone nào đứng vững walk-forward.

---

## 3. Đọc từng ô — môi trường, kỳ vọng, tổ hợp, rủi ro

> Cột "kỳ vọng edge" dưới đây là **đọc dữ liệu mô tả + cơ chế chiến lược**, đã bị chấm FAIL bởi đa
> kiểm định. Đọc như "giả thuyết làm việc có số đi kèm", không phải như tham số.

### CRISIS × RẺ (132 phiên / 12 đoạn — 2022 Q4, 2020 Q1, 2015)
- **Môi trường:** hoảng loạn giá + định giá đã sập. VNI −16,1% ann. DT5G cap 0% ⇒ hệ thống gần như
  toàn tiền/parking.
- **BAL:** ~neutral tuyệt đối (+4,7%) nhưng **excess +20,8pp**, Sharpe 1,51 — edge đến từ **KHÔNG
  MẤT TIỀN**, không từ kiếm tiền. Đúng thiết kế: SB_GATE = 0 exposure.
- **LAG:** +2,1% (ex +18,2), Sharpe 0,21. `w_LAG=0,50` ⇒ CAPIT có thể chạy trên tiền LAG rảnh.
- **Alpha Lens:** **−17,8% ann, excess −1,6pp — ô tệ nhất của Tier-1.** Buy-and-hold Tier-1 không
  bảo vệ trong crisis+rẻ; ngân hàng bị đánh nặng nhất (MBB −36,6%, ACB −25,2%; FPT +3,7%).
- **Tổ hợp:** giữ nguyên gate (0% risk). Vốn nằm ở custom30V recovery-park + CAPIT washout.
- **Rủi ro chính:** **"rẻ nên phải mua"**. Phụ lục C đã đo: **đầu RẺ KHÔNG đơn điệu** — dải radar
  0-20 tệ hơn dải 20-33. Ô này radar TB 17,0 = đúng dải nguy hiểm đó.

### CRISIS × TRUNG TÍNH (246 phiên / 16 đoạn)
- **Môi trường:** giá sập nhanh trước khi định giá kịp rẻ — sốc, không phải suy thoái định giá.
- **BAL** +10,8% (ex +14,0, Sharpe 1,60) · **LAG +25,4% (ex +28,7, Sharpe 1,89)** — Sharpe cao bất thường cho một ô CRISIS.
  Cơ chế hợp lý: PEAD sống bằng **sự kiện KQKD từng mã**, ít phụ thuộc hướng index; sốc giá làm
  earnings-drift bị định giá sai nhiều hơn.
- **Alpha Lens:** +2,6% (ex +5,8) — mờ nhạt.
- **Tổ hợp:** **LAG-heavy trong khuôn khổ w_LAG=0,50 hiện hành.** Đây là ô ủng hộ mạnh nhất việc
  allocator KHÔNG cắt LAG về 0 trong CRISIS (khác BEAR).
- **Rủi ro:** thanh khoản. LAG hay chạm mã ADV mỏng; trong sốc, spread nở, lỗi fidelity `liq<=0`
  (VẪN MỞ trong pin R3) làm số backtest **lạc quan** đúng ở loại phiên này.

### CRISIS × ĐẮT (111 phiên / 10 đoạn) — 🚨 **Ô NGUY HIỂM NHẤT CHO BAL**
- **Môi trường:** giá bắt đầu sập nhưng định giá vẫn cao — đỉnh bong bóng đang vỡ.
- **BAL: −24,8%, excess −15,3pp, Sharpe −1,74.** Đây là ô **duy nhất** BAL vừa âm tuyệt đối vừa
  âm tương đối rõ. Cơ chế: momentum bị whipsaw ở đỉnh; SIGNAL_V11 vẫn thấy tín hiệu mạnh ngay
  trước khi trend gãy.
- **LAG:** −5,5% (ex +4,0) — chịu đựng tốt hơn nhiều.
- **Alpha Lens: +11,1%, excess +20,6pp** — Tier-1 là nơi trú ẩn TỐT NHẤT trong ô này (ACB +39,6%,
  MBB +14,8%; FPT −15,8%, HDB −31,6% ⇒ phân tán rất lớn, không đồng nhất).
- **Tổ hợp:** hạ BAL tối đa trong khuôn khổ gate; LAG + Tier-1 chống đỡ.
- **Rủi ro:** n=111 phiên/10 đoạn, p=0,52 — **số −15,3pp này KHÔNG có ý nghĩa thống kê.**

### BEAR × RẺ (170 phiên / 6 đoạn — 2022 Q3-Q4, 2018 cuối)
- **Môi trường:** giảm kéo dài, định giá đã rẻ. **w_LAG = 0 ⇒ toàn bộ vốn về BAL/park.**
- **BAL:** +0,8% (ex **+26,4pp**) — gate BEAR (exposure 0,2) làm đúng việc bảo hiểm.
- **LAG (sổ tham chiếu, KHÔNG có vốn): +11,4%, ex +36,9pp** — một trong hai số excess cao nhất bảng cho LAG (cùng BULL+RẺ +41,9). Xem §5 #4.
- **Alpha Lens: −10,1%** nhưng **ex +15,5pp** — Tier-1 giảm ít hơn thị trường (ACB +4,4%, HDB −0,7%,
  FPT −18,4%, MBB −23,8%).
- **Tổ hợp:** đúng như production đang làm — BAL gate thấp + park, LAG tắt.
- **Rủi ro:** **6 đoạn** = 6 sự kiện thật. Mọi con số ở đây là mô tả 6 lần xảy ra, không phải phân phối.

### BEAR × TRUNG TÍNH (60 phiên / 4 đoạn) — mẫu mỏng
- BAL −5,2% (ex +18,0) · LAG-ref −15,8% · AL4 −12,4% (ex +10,8). Ô duy nhất LAG-ref âm mạnh trong BEAR
  ⇒ ủng hộ `w_LAG=0` ở BEAR khi định giá CHƯA rẻ. Mẫu 60 phiên ⇒ **không kiểm định** (bị loại khỏi 24 test).

### BEAR × ĐẮT (11 phiên) — 🔴 KHÔNG CÓ DỮ LIỆU. Về mặt cấu trúc rất hiếm: DT5G cần 25 phiên để
vào BEAR, đủ lâu để radar kịp rời zone ĐẮT.

### ⭐ NEUTRAL × RẺ (440 phiên / 18 đoạn) — **Ô CHÚNG TA ĐANG ĐỨNG**
- **Môi trường:** không xu hướng rõ, định giá rẻ. VNI **−6,0% ann** — nghĩa là ô này lịch sử là
  **thị trường đi ngang/xuống nhẹ**, không phải nền tăng. Xảy ra ở 2015-16, 2020 (ngắn), 2022-2026.
- **BAL:** +10,7% (**ex +16,3pp, p=0,020, CI[+3,1;+30,8]**), Sharpe 0,76.
- **LAG:** +14,5% (**ex +19,9pp, p=0,015, CI[+3,5;+35,7]** — p nhỏ nhất toàn ma trận), Sharpe 0,89.
- **Alpha Lens:** +11,5% (**ex +17,2pp, p=0,021**). MBB +19,4%, FPT +14,5%, HDB +7,2%, ACB +4,8%.
- **⚠️ Cả 3 đều p ∈ [0,015; 0,021] — và cả 3 đều FAIL BH** (ngưỡng hạng 1 = 0,0042). Chúng cũng
  **không độc lập với nhau** (cùng thị trường, cùng phiên).
- **Tổ hợp tối ưu:** BAL-LAG chênh nhau **−3,7pp/năm với CI[−19,6;+14,4]** ⇒ **KHÔNG phân biệt được.**
  Kết luận đúng là: **giữ w_LAG mặc định 0,65 (band ±10pp)** — dữ liệu không cho lý do nghiêng bên nào.
- **Rủi ro chính:** (a) VNI âm trong ô này ⇒ toàn bộ "thắng" là **tương đối, không tuyệt đối**;
  (b) đây là ô sideway → momentum BAL dễ bị whipsaw phí; (c) 18 đoạn nhưng dồn vào 2023-2025.

**Forward 60 phiên tính từ ngày VÀO ô (18 lần, `neutral_re_entries.csv`):**

| | COMB | BAL | LAG | AL4 | VNI |
|---|---:|---:|---:|---:|---:|
| median f60 | **+6,9%** | +3,3% | +7,6% | +3,7% | +5,0% |
| tỉ lệ > VNI | **83%** | 78% | 56% | 67% | — |

Tệ nhất: 2022-08-17 (COMB −9,8% khi VNI −25,7% ⇒ vẫn +15,9pp). Tốt nhất: 2025-05-19 (+26,5%).
**COMB thắng VNI 15/18 lần — nhưng 18 lần này không độc lập** (nhiều lần cách nhau vài phiên,
vd 2024-10-14/10-18, 2024-12-31/2025-01-03).

### NEUTRAL × TRUNG TÍNH (802 phiên / 25 đoạn) — ô "cày tiền" của hệ
- VNI +27,8%; BAL +37,0% (ex +9,2, Sharpe **2,17**); LAG +39,2% (ex +11,5, Sharpe 2,01);
  COMB **+41,6%**. AL4 +32,3% (ex +4,6 — Tier-1 THUA hệ thống ở ô này).
- **Tổ hợp:** cân bằng, đúng w_LAG=0,65. Đây là ô đóng góp nhiều NAV nhất (802 phiên, 26% mẫu).
- **Rủi ro:** ex của BAL/LAG chỉ +9 đến +11pp với p≈0,44 ⇒ phần lớn return là **beta**, không phải alpha.

### NEUTRAL × ĐẮT (653 phiên / 11 đoạn — 2017-2019, 2021)
- VNI +20,5%; BAL +42,5% (**ex +22,0**, Sharpe 2,32); LAG +42,1% (ex +21,6); AL4 +32,6% (ex +12,1).
- **Ô có Sharpe cao nhất cho BAL trong nhóm có mẫu đủ.** Nhưng chỉ **11 đoạn** và ≡ kỷ nguyên 2017-21.
- **Tổ hợp:** BAL và LAG ngang nhau (BAL−LAG = +0,2pp, CI[−14,9;+13,8]).
- **Rủi ro:** đây chính là confound-1 ở dạng thuần khiết. Đừng đọc "đắt thì tốt".

### BULL × RẺ (96 phiên / 6 đoạn) — nghịch lý đáng chú ý
- VNI −5,9% (!) — DT5G nói BULL nhưng index đi ngang/xuống trong các phiên đó.
- **BAL −5,5% (ex +0,4pp — vô dụng)** vs **LAG +35,9% (ex +41,9pp, Sharpe 2,11)**.
- **Tổ hợp:** ô ủng hộ LAG-heavy rõ nhất. Nhưng n=96/6 đoạn, p=0,42 ⇒ **không kết luận được.**
- **Rủi ro:** BULL+RẺ thường là **BULL sắp gãy** (DT5G cần 10 phiên để RA, nên nó còn treo nhãn BULL
  trong lúc thị trường đã quay đầu). Momentum chết đúng lúc đó.

### BULL × TRUNG TÍNH (93 phiên / 10 đoạn)
- **BAL +90,2% (ex +49,5pp, Sharpe 3,74 — ô mạnh nhất của BAL)** vs LAG +25,8% (**ex −14,8pp**).
- **Tổ hợp:** BAL-heavy. Đây là ô duy nhất LAG có excess ÂM đáng kể.
- **Rủi ro:** 93 phiên, p=0,13. Và BAL+90% ann là đọc 93 phiên ra 1 năm.

### BULL × ĐẮT (233 phiên / 8 đoạn — 2017-18, 2021)
- VNI +37,7%; BAL +84,0% (ex +46,3); LAG +46,8% (ex +9,0); **AL4 +77,9% (ex +40,2, p=0,068 — số
  tốt nhì toàn ma trận cho Alpha Lens)**. ACB +77,3%, MBB +85,0%, HDB +80,9%, FPT +48,0%.
- **Tổ hợp:** BAL-heavy + Tier-1 (ngân hàng) chạy tốt cùng lúc.
- **Rủi ro:** 8 đoạn / 1 kỷ nguyên. Và ô này đứng ngay trước CRISIS×ĐẮT (ô tệ nhất cho BAL) —
  chuyển tiếp có thể rất nhanh.

### EX-BULL × TRUNG TÍNH / ĐẮT (31 và 29 phiên) — 🔴 KHÔNG ĐỌC
Số annualised ở đây (BAL +334,8%, AL4 +214,2%) là **ngoại suy 29 phiên**. Điều DUY NHẤT đọc được:
trong 31 phiên EX-BULL+TRUNG TÍNH, **BAL âm trong khi LAG và AL4 dương** — nhất quán với luật
`EXBULL-suppress` đã có trong SIGNAL_V11. Không có ô EX-BULL × RẺ (0 phiên) — cấu trúc: định giá
rẻ và hưng phấn cực độ không đồng thời tồn tại.

---

## 4. Alpha Lens — phân tích Tier-1

### 4.1 Tier-1 LEAD hay LAG thị trường?
Cumulative return quanh 51 lần đổi state DT5G (T0 = phiên đổi):

| Nhóm | chuỗi | T−20 | T−10 | T0 | T+10 | T+20 |
|---|---|---:|---:|---:|---:|---:|
| **XUỐNG state** (n=24) | AL4 | +0,05% | −2,69% | −2,74% | −3,99% | −4,76% |
| | VNI | −0,30% | −3,02% | −3,07% | −4,16% | −4,97% |
| | BAL | −0,19% | −2,56% | −1,35% | **+0,50%** | −0,76% |
| | LAG | −0,23% | −0,16% | **+0,58%** | +0,78% | +0,81% |
| **LÊN state** (n=27) | AL4 | +0,48% | +4,31% | **+5,52%** | +6,90% | +7,94% |
| | VNI | +0,36% | +4,16% | +4,70% | +4,85% | +5,32% |
| | BAL | +0,18% | +2,95% | +5,05% | +6,48% | **+8,22%** |
| | LAG | +0,33% | +3,85% | +5,76% | +5,11% | +6,45% |

**Kết luận: Tier-1 KHÔNG lead — nó đi gần như trùng VNINDEX** (chênh <0,6pp ở mọi mốc khi xuống;
+0,8 đến +2,6pp khi lên). Điều này hợp lý vì FPT/ACB/MBB/HDB **chính là** thành phần vốn hoá lớn
của VNINDEX. ⇒ **Alpha Lens không có giá trị làm tín hiệu sớm cho DT5G.**
Ngược lại **LAG là chuỗi duy nhất KHÔNG âm quanh transition xuống** (+0,58% tại T0, +0,81% tại T+20)
— PEAD ít nhạy với đổi regime, đúng bản chất event-driven.

### 4.2 Ngân hàng vs chế độ lãi suất (ACB/MBB/HDB trung bình vs FPT)

| Lãi suất huy động | phiên | BANK | FPT | VNI | BANK excess | FPT excess |
|---|---:|---:|---:|---:|---:|---:|
| < 5,5% | 1.516 | +23,5% | +22,9% | +10,4% | +13,1pp | +12,6pp |
| 5,5–6,5% | 795 | **+43,8%** | +24,8% | +22,5% | **+21,3pp** | +2,3pp |
| **6,5–8%** ⬅ **HIỆN TẠI (6,8%)** | 796 | **+2,2%** | +21,5% | +1,2% | **+1,0pp** | **+20,3pp** |

🚩 **Đây là phát hiện có giá trị vận hành nhất về Alpha Lens.** Ở mức lãi suất huy động hiện tại
(**6,8%**), lịch sử cho thấy **ngân hàng gần như không có excess (+1,0pp)** trong khi **FPT có
+20,3pp**. Rổ Alpha Lens đang **3/4 là ngân hàng** ⇒ cơ cấu này nằm ở đúng bucket lãi suất bất lợi
nhất cho nó.

**Ngân hàng theo zone:** RẺ −1,2% · TRUNG TÍNH +22,8% · ĐẮT +44,7% (FPT: +5,7% / +22,8% / +39,4%).
⇒ "P/E ngân hàng thấp" trong zone RẺ **KHÔNG** là tín hiệu mua: ô RẺ là ô ngân hàng chạy tệ nhất
(−1,2% ann). Nhất quán với memory `finance-domain-grounding-not-pure-statistics`: P/E thấp ở ngân
hàng thường phản ánh **rủi ro chất lượng tài sản đang bị định giá**, không phải chiết khấu vô cớ.

**Chú ý dữ liệu:** HDB chỉ có 2.107/3.128 phiên (niêm yết 2018) ⇒ mọi số HDB trước 2018 vắng mặt,
và số AL4 giai đoạn 2014-17 thực chất là rổ 3 mã.

### 4.3 Trong ô hiện tại NEUTRAL+RẺ
AL4 +11,5% ann, ex +17,2pp (p=0,021, FAIL BH) — **không phân biệt được với BAL (+16,3) hay LAG (+19,9)**.
Alpha Lens không tệ, nhưng cũng **không cho thấy ưu thế nào so với hệ thống production**. Kết hợp với
tiền lệ **Q-sleeve NO-GO** (rổ nhỏ 8-12 mã thua custom30V 2,9-6,8pp IS vì mất breadth), luận điểm
"cô đặc Tier-1" vẫn chưa có bằng chứng mới.

---

## 5. Năm "edge signal" nên WATCH (không phải để wire)

| # | Tín hiệu | Số liệu | Trạng thái thống kê |
|---|---|---|---|
| **1** | **CRISIS × ĐẮT là ô độc cho BAL** — momentum bị whipsaw ở đỉnh đang vỡ | BAL −24,8% ann, ex −15,3pp, Sharpe −1,74; LAG chỉ −5,5%; AL4 **+11,1%** | p=0,52, n=111/10 đoạn — **rất yếu**, nhưng là ô DUY NHẤT BAL âm 2 chiều ⇒ đáng canh |
| **2** | **LAG chống chịu transition tốt hơn BAL/VNI** | Quanh 24 lần XUỐNG state: LAG +0,58% tại T0, +0,81% tại T+20; VNI −3,07%/−4,97% | Nhất quán với cơ chế PEAD (event-driven, không directional). Đây là tín hiệu có **cơ chế**, không chỉ có số |
| **3** | **Alpha Lens không lead DT5G** — bỏ ý định dùng Tier-1 làm tín hiệu sớm | AL4 lệch VNI <0,6pp ở mọi mốc quanh transition xuống | Kết luận NEGATIVE, độ tin cậy cao (đây là kết luận "không có gì", ít bị p-hacking) |
| **4** | **BEAR × RẺ: sổ LAG tham chiếu +11,4% (ex +36,9pp) trong khi allocator để w_LAG=0** | 170 phiên / **6 đoạn**; p=0,14; BEAR TRUNG TÍNH thì ngược lại (LAG-ref −15,8%) | ⚠️ **KHÔNG đề xuất đổi allocator.** 6 đoạn, p không qua, và dấu ĐẢO NGƯỢC ngay ở ô BEAR kế bên ⇒ đúng chữ ký overfit. Ghi lại để nếu sau này có thêm 2-3 đợt BEAR thì kiểm định lại |
| **5** | **Lãi suất 6,5-8% = bucket xấu nhất cho ngân hàng, tốt nhất cho FPT** | BANKex +1,0pp vs FPTex +20,3pp trên 796 phiên; hiện tại lãi suất = **6,8%** | Cơ chế kinh tế rõ (NIM bị ép + chi phí vốn tăng). 796 phiên nhưng ≈3-4 chu kỳ lãi suất ⇒ n hiệu dụng nhỏ. **Áp dụng cho AUDIT Alpha Lens 2026-09-30, không phải để đổi rổ giữa chừng** |

---

## 6. Vị trí hiện tại: NEUTRAL + RẺ

**Xác nhận trạng thái (không lấy từ prompt, đọc lại nguồn):**
- DT5G `tav2_bq.vnindex_5state_dt5g_live`: `state=3` NEUTRAL, liên tục 2026-08-14 → **2026-08-21**.
- Value Radar (`value_radar_now`, asof **2026-08-21**, cửa sổ rolling-10Y): **24,53 = RẺ**;
  P/E 11,58 (p8,6) · P/B 1,96 (p33,2) · spread EY−tiết kiệm +1,83pp (p31,8) · deposit_rate 6,8%.
  Lệch nhẹ so với context dispatch (24,5 / p9 / p33 / p32) — cùng số, làm tròn khác.
- ⚠️ Radar 24,5 nằm trong dải **0-33 "RẺ"**, và cụ thể ở **dải 20-33**. Phụ lục C: dải **0-20 tệ hơn**
  dải 20-33 ⇒ "rẻ thêm nữa" không tự động tốt hơn.
- ⚠️ **Radar chỉ ~1,5-2 chiều thông tin, không phải 3.** corr(P/E,P/B)=0,913. Và p_pe=8,6 vs
  p_pb=33,2 lệch rất xa nhau — nghĩa là "rẻ" hiện nay chủ yếu do **P/E**, không phải P/B.

### Nhận định

1. **Ô này lịch sử KHÔNG phải nền tăng.** VNI trong NEUTRAL+RẺ = **−6,0% ann** trên 440 phiên.
   Mọi lợi thế đo được đều là **tương đối**. Đừng lập kế hoạch dựa trên kỳ vọng index tăng.
2. **Cả 3 chiến lược đều dương tương đối và KHÔNG phân biệt được với nhau.** BAL ex +16,3 · LAG
   ex +19,9 · AL4 ex +17,2, ba p-value nằm trong 0,015-0,021, và BAL−LAG = −3,7pp/năm với
   CI[−19,6; +14,4] chứa 0 rất rộng.
   ⇒ **Khuyến nghị: KHÔNG nghiêng. Giữ w_LAG mặc định 0,65, band ±10pp.** Không có căn cứ để lệch.
3. **COMB−VNI trong ô này = +19,1pp/năm, CI[+6,0; +31,1] không chứa 0** — đây là con số bền nhất
   trong toàn báo cáo (ô có mẫu lớn nhất trong zone RẺ). Nó nói: **hệ thống 2-book có giá trị ở ô
   hiện tại**, dù không nói được book nào.
4. **Forward 60 phiên từ 18 lần vào ô: median COMB +6,9%, thắng VNI 15/18 lần.** Nhưng 18 lần
   không độc lập và trải trên chỉ 5 giai đoạn thật (2014-16, 2020, 2022-23, 2024-25, 2026).
5. **Đối với Alpha Lens:** rổ đang 3/4 ngân hàng, ở đúng bucket lãi suất (6,8%) mà lịch sử cho
   ngân hàng excess ≈ 0. Đây là **rủi ro cấu trúc của rổ**, cần nêu trong audit 2026-09-30.

---

## 7. Khuyến nghị theo kịch bản chuyển tiếp

Bảng dưới **mô tả hệ thống production SẼ TỰ LÀM GÌ** (allocator + DT5G gate đã encode) và điều
cần CANH, chứ không đề xuất thay đổi tham số.

### Forward 60 phiên sau mỗi lần đổi state (mẫu thật, n nhỏ)

| Transition | n | COMB | BAL | LAG | AL4 | VNI |
|---|---:|---:|---:|---:|---:|---:|
| NEUTRAL → BULL | 9 | +10,0% | **+13,7%** | +7,9% | +7,6% | +6,7% |
| NEUTRAL → BEAR | 7 | +2,8% | +5,0% | −0,4% | +2,8% | −1,4% |
| NEUTRAL → CRISIS | 4 | +5,0% | +3,8% | +5,8% | +2,2% | +1,1% |
| CRISIS → NEUTRAL | 7 | +9,7% | +7,2% | **+11,2%** | +9,7% | +4,8% |
| BULL → NEUTRAL | 6 | +13,1% | **+20,3%** | +8,8% | +1,4% | +6,8% |
| BEAR → NEUTRAL | 7 | +4,4% | +6,2% | +2,7% | +0,1% | −2,6% |

### Kịch bản A — NEUTRAL → BEAR (radar ở lại RẺ)
- **Hệ tự làm:** `w_LAG` 0,65 → **0**, toàn bộ vốn về BAL; SB_GATE hạ exposure BAL về 0,2;
  custom30V recovery-park nhận tiền rảnh. DT-gate cần **25 phiên** để commit vào BEAR.
- **Lịch sử ô BEAR+RẺ:** BAL ex +26,4pp, COMB gần như phẳng (+0,4% ann) khi VNI −25,6%.
  Forward-60 sau NEUTRAL→BEAR: COMB +2,8% (7 lần).
- **Canh:** (i) `get_dt_gate_clock()` — candidate BEAR đang tích luỹ mấy/25 phiên, đây mới là cảnh
  báo sớm, không phải state đã commit; (ii) trong 25 phiên đó hệ vẫn chạy NEUTRAL sizing — đó là
  **cửa sổ rủi ro có chủ đích** của thiết kế chậm-hoảng-loạn; (iii) edge-signal #4 (LAG-ref dương
  trong BEAR+RẺ) — **quan sát, ghi lại, KHÔNG hành động.**

### Kịch bản B — NEUTRAL → BULL (radar ở lại RẺ ⇒ ô BULL+RẺ)
- **Hệ tự làm:** w_LAG → 0,65; SB_GATE exposure 1,0.
- **Lịch sử ô BULL+RẺ (96 phiên/6 đoạn):** đây là ô **BAL vô dụng** (ex +0,4pp) trong khi **LAG
  ex +41,9pp**. Nhưng forward-60 sau NEUTRAL→BULL lại cho **BAL +13,7% > LAG +7,9%** (9 lần).
  **Hai lát cắt mâu thuẫn nhau ⇒ không có kết luận.** Giữ mặc định.
- **Canh:** BULL+RẺ hay là "BULL sắp gãy" (DT5G ra khỏi BULL chỉ cần 10 phiên). Nếu radar bắt đầu
  bò lên TRUNG TÍNH trong lúc vẫn BULL → đó là đường vào ô BULL+TRUNG TÍNH/ĐẮT (ô BAL mạnh nhất),
  chứ không phải ô hiện tại.

### Kịch bản C — NEUTRAL giữ nguyên, radar RẺ → TRUNG TÍNH (giá tăng)
- **Hệ tự làm:** không gì cả (radar DISPLAY-ONLY, không nối vào sizing) — **đúng thiết kế**.
- **Lịch sử:** NEUTRAL+TRUNG TÍNH là ô cày tiền nhất (COMB +41,6% ann, Sharpe BAL 2,17, 802 phiên).
  Đây là **hướng dịch chuyển tốt nhất** từ vị trí hiện tại.
- **Canh:** tăng do giá lên (tốt) hay do E giảm (P/E tăng vì lợi nhuận sụt — xấu)? Phải nhìn
  `pe_cap10` vs earnings, radar không phân biệt được.

### Kịch bản D — NEUTRAL → CRISIS
- **Hệ tự làm:** w_LAG → 0,50 (KHÔNG về 0 như BEAR); exposure 0; CAPIT washout gate mở với size
  1,0; MATURITY rule scale theo độ sâu `dd52w`.
- **Lịch sử:** nếu vào CRISIS trong lúc radar còn RẺ → ô CRISIS+RẺ, LAG chỉ +2,1%, Sharpe 0,21.
  Nếu radar kịp lên TRUNG TÍNH → ô CRISIS+TRUNG TÍNH, LAG +25,4%, Sharpe 1,89. **Chênh lệch rất
  lớn giữa 2 ô kề nhau, trên mẫu nhỏ ⇒ đọc như phương sai, không như quy luật.**
- **Canh:** dải radar 0-20 (ô CRISIS+RẺ có radar TB 17,0) là dải mà Phụ lục C đo được **không đơn
  điệu** — "càng rẻ càng nên mua" sai ở chính chỗ này.

### Điều KHÔNG được rút ra từ báo cáo này
- ❌ Đổi `STATE_LAG_WEIGHT` (allocator) — ngoài phạm vi dispatch và không có ô nào qua BH.
- ❌ Dùng Value Radar zone để sizing — DISPLAY-ONLY, và confound-1 cho thấy zone ≈ kỷ nguyên.
- ❌ Trích bất kỳ số EX-BULL nào (60 phiên / 2 đoạn).
- ❌ Kết luận "momentum thích thị trường đắt" — đó là phát biểu về 2017-2021, không phải về định giá.

---

## 8. Tái lập

```bash
cd /home/trido/thanhdt/WorkingClaude
/home/trido/thanhdt/wc_venv/bin/python mike/agents/Taylor/research/strategy_regime_matrix_20260822.py
/home/trido/thanhdt/wc_venv/bin/python mike/agents/Taylor/research/strategy_regime_matrix_20260822_part2.py
```

**Artifacts** (`mike/agents/Taylor/research/strategy_regime_matrix_20260822/`):
`panel_daily.csv` (3.107 phiên × mọi chuỗi) · `cells.csv` (19 ô + tổng hợp) ·
`bh_tests.csv` (45 dòng, 24 kiểm định hợp lệ + cờ BH/Bonferroni) ·
`neutral_re_entries.csv` (18 lần vào ô hiện tại) · `alphalens_px.csv` (giá thô BQ) ·
`part1.log` / `part2.log` (stdout đầy đủ kèm self-check).

**N-ledger:** job này mở **24 trial** (kiểm định excess theo ô × chiến lược). **0 trial nào cho
kết quả được đề xuất wire** ⇒ không tiêu ngân sách đa kiểm định của bất kỳ dự án production nào.
