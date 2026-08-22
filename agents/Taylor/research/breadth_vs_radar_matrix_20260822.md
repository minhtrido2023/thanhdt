# B2 — Breadth (%>MA200) thay Value Radar làm trục 2 (PAPER-ONLY, KHÔNG wire)

**Job** `Taylor_20260822_141143` · **Ngày** 2026-08-22 · **Tác giả** Taylor

**Kết luận một câu:** breadth **thắng radar rõ ràng về mặt CẤU TRÚC thống kê** (hết confound kỷ
nguyên, n_effective gấp đôi) — nhưng **vẫn 0/27 ô qua BH FDR 10%**, và cái tưởng là tín hiệu
(excess đơn điệu theo tercile) **tan biến khi trễ nhãn 1 phiên** và **đảo thứ tự khi khử beta**.
Trục tốt hơn để MÔ TẢ, không phải trục để wire.

---

## 1. Nguồn & self-check

| Nguồn | Trạng thái | Ghi chú |
|---|---|---|
| `tav2_mike.universe_pit` (`in_universe=TRUE`) JOIN `tav2_bq.ticker` (`Close`, `MA200`) | **CANONICAL** | đã tra `data_registry/price-volume/index.md`; `ticker_prune` là **TRAP cho code mới** (cutover 2026-07-22) → không dùng |
| `panel_daily.csv` (part 1, job `_101400`) | pin R3, self-check 0 VND | `r_bal/r_lag/r_comb/r_vni` + `state` DT5G + `zone` radar |

- Breadth = `COUNTIF(Close > MA200) / COUNT(*)` trên universe PIT từng ngày. 3.652 phiên
  2012-01-03 → 2026-08-21; `n_univ` median 276 (min 88, max 578).
- **Tercile PIT**: phân vị của breadth hôm nay trong **252 phiên TRƯỚC ĐÓ** (không gồm hôm nay).
  Warm-up 252 phiên bị loại. Phân bố trên panel: LOW 1.232 / MID 897 / HIGH 978 phiên.
- Self-check: 0/3.107 phiên thiếu breadth, 0 thiếu nhãn tercile.
- ⚠️ **Self-check no-look-ahead ra +0,109, KHÔNG ra 0** — `corr(pct252_t, r_vni_t) = +0,1088`. Đây
  không phải bug cửa sổ: `breadth_t` dùng `Close` của **chính phiên t**, nên nhãn tercile của hôm nay
  có chứa thông tin hôm nay. Hệ quả được xử lý tường minh ở §5.

---

## 2. Confound kỷ nguyên — breadth thắng dứt khoát

Đây là lý do sinh ra B2. A1/A2 kết luận radar zone ≈ kỷ nguyên (ĐẮT = 2017-19 + 2021, RẺ = 2015-16
+ 2022-25, không chồng lấn) ⇒ mọi phân tích conditional theo zone đều dính confound.

Số phiên theo năm × tercile breadth:

| năm | LOW | MID | HIGH | | năm | LOW | MID | HIGH |
|---|---:|---:|---:|---|---|---:|---:|---:|
| 2014 | 67 | 95 | 85 | | 2021 | 43 | 106 | 101 |
| 2015 | 177 | 33 | 38 | | 2022 | 209 | 39 | 1 |
| 2016 | 91 | 55 | 105 | | 2023 | 9 | 88 | 152 |
| 2017 | 57 | 80 | 113 | | 2024 | 112 | 133 | 5 |
| 2018 | 175 | 64 | 11 | | 2025 | 68 | 93 | 88 |
| 2019 | 43 | 66 | 141 | | 2026 | 90 | 19 | 3 |
| 2020 | 91 | 26 | 135 | | | | | |

| Trục | % số năm bị MỘT nhãn chiếm ≥90% phiên | share nhãn trội trung bình |
|---|---:|---:|
| **Breadth** | **0%** | **57%** |
| Radar zone | 54% | 84% |

**Breadth biến thiên TRONG từng năm; radar zone thì không.** Đúng như giả thuyết đặt ra.

**n_effective** (đoạn liên tục = episode xấp xỉ độc lập):

| Trục | số ô | episode median | min | max | **tổng episode** | số năm/ô (median) |
|---|---:|---:|---:|---:|---:|---:|
| **Breadth** | 13 | 11 | 2 | 74 | **262** | **6** |
| Radar | 14 | 9 | 1 | 25 | 131 | 5 |

Gấp **2,0×** tổng episode. Ô NEUTRAL — nơi hệ sống 61% thời gian — có 41/74/42 episode trải 11-12
năm, thay vì vài chu kỳ dính kỷ nguyên.

---

## 3. Ma trận DT5G × breadth-tercile

CAGR annualised trong ô (gross backtest, chưa trừ −1,5% quy đổi thực tế):

| regime | tile | phiên | ep | năm | breadth TB | VNI | BAL | LAG | COMB | BALex | LAGex | COMBex |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CRISIS | LOW | 266 | 20 | 7 | 37,6% | −21,8 | −6,4 | −5,3 | −6,0 | +15,5 | +16,6 | +15,8 |
| CRISIS | MID | 171 | 23 | 8 | 66,3% | +16,0 | +3,0 | +41,1 | +21,2 | −13,0 | +25,1 | +5,2 |
| CRISIS | HIGH | 52 | 5 | 4 | 70,6% | −4,3 | +25,6 | +16,0 | +20,7 | +29,9 | +20,3 | +24,9 |
| BEAR | LOW | 151 | 7 | 5 | 19,8% | −43,2 | −8,9 | −2,8 | −10,1 | +34,3 | +40,5 | +33,1 |
| BEAR | MID | 42 | 11 | 4 | 29,2% | −18,3 | +20,3 | +17,8 | +20,7 | +38,6 | +36,1 | +39,0 |
| BEAR | HIGH | 48 | 9 | 4 | 34,2% | +113,7 | +17,1 | −2,5 | +17,1 | −96,7 | −116,3 | −96,7 |
| **NEUTRAL** | **LOW** | **698** | **41** | **12** | 44,7% | −7,5 | +13,2 | +18,8 | +17,7 | +20,7 | +26,3 | **+25,2** |
| **NEUTRAL** | **MID** | **516** | **74** | **12** | 58,0% | +20,9 | +34,1 | +31,2 | +34,7 | +13,2 | +10,4 | **+13,8** |
| **NEUTRAL** | **HIGH** | **681** | **42** | **11** | 67,6% | +43,8 | +53,2 | +54,0 | +53,6 | +9,4 | +10,2 | **+9,8** |
| BULL | LOW | 117 | 8 | 6 | 47,7% | −38,3 | −20,9 | +40,3 | +12,0 | +17,4 | +78,6 | +50,3 |
| BULL | MID | 168 | 12 | 6 | 70,7% | +52,1 | +82,9 | +26,8 | +48,6 | +30,8 | −25,3 | −3,6 |
| BULL | HIGH | 137 | 8 | 4 | 87,1% | +88,0 | +144,4 | +55,7 | +86,6 | +56,4 | −32,3 | −1,4 |
| EXBULL | HIGH | 60 | 2 | 3 | 83,8% | +63,0 | +67,9 | +96,0 | +85,6 | +4,8 | +33,0 | +22,6 |

(EXBULL không có phiên nào ở LOW/MID — EXBULL theo định nghĩa đi kèm breadth cao.)

**BH(FDR 10%) trên 27 test hợp lệ (15 ô × 3 chiến lược, bỏ 18 ô thiếu mẫu): 0 PASS. Bonferroni: 0 PASS.**
Ứng viên gần nhất: NEUTRAL+LOW COMB `p=0,027`, BULL+LOW LAG `p=0,030`, NEUTRAL+LOW LAG `p=0,044`.
Ngưỡng BH cho hạng 1 với m=27 là `0,10×1/27 = 0,0037` — còn cách xa **7×**.
So sánh: ma trận radar `_101400` là 24 test, **0 PASS**. ⇒ **về mặt "có ô nào thật không", HAI TRỤC HÒA — cùng 0.**

---

## 4. Marginal theo tercile — chỗ breadth thật sự khác radar

| tercile | phiên | ep | VNI | COMB | COMB excess | IS 14-19 excess | OOS 20+ excess |
|---|---:|---:|---:|---:|---:|---:|---:|
| LOW | 1.232 | 54 | −19,2% | +8,0% | **+27,1pp** | +26,9pp | +28,2pp |
| MID | 897 | 107 | +22,9% | +33,8% | **+10,8pp** | +7,9pp | +8,5pp |
| HIGH | 978 | 54 | +50,2% | +55,6% | **+5,4pp** | −0,3pp | +6,9pp |

Đơn điệu, và **IS/OOS gần như trùng nhau** — thứ radar zone chưa bao giờ làm được. LOO theo năm
(bỏ từng năm, tính lại): LOW dao động +23,4…+31,9%, MID +3,3…+11,1%, HIGH +0,4…+5,5% — **không lần
nào đảo dấu**, 13/13 năm.

Nhìn đến đây thì rất giống một phát hiện. Hai kiểm tra sau đây phá nó.

---

## 5. Hai kiểm tra phá kết luận §4

### 5a. Trễ nhãn 1 phiên — bắt buộc nếu muốn wire

`breadth_t` dùng `Close` phiên t (§1). Bất kỳ ý định dùng làm cổng sizing nào cũng phải dùng nhãn
**trễ 1 phiên**. Làm vậy:

| tercile | VNI (nhãn trễ) | COMB | excess | IS excess | OOS excess |
|---|---:|---:|---:|---:|---:|
| LOW | **+1,9%** (so với −19,2% khi không trễ) | +26,8% | +24,9pp | +22,5pp | +18,7pp |
| MID | +18,0% | +26,4% | +8,4pp | +7,3pp | +5,9pp |
| HIGH | +16,4% | +33,9% | **+17,4pp** | +5,6pp | **+21,8pp** |

**Tính đơn điệu biến mất** (LOW +24,9 > HIGH +17,4 > MID +8,4). Và VNI trong ô LOW nhảy từ **−19,2%
lên +1,9%** chỉ vì trễ MỘT phiên — tức phần lớn "VNI rơi khi breadth thấp" là **cùng phiên, cơ học**,
không phải trạng thái kéo dài.

### 5b. Khử beta — thứ tự ĐẢO NGƯỢC

Sổ chạy beta thấp (không bao giờ full-invested):

| tercile | tỷ trọng đầu tư BAL | LAG | beta(COMB,VNI) | COMB | VNI | excess thô | **alpha sau khi khử beta** |
|---|---:|---:|---:|---:|---:|---:|---:|
| LOW | 57,4% | 68,4% | 0,43 | +8,0% | −19,2% | +27,1pp | **+16,3pp** |
| MID | 62,7% | 65,5% | 0,59 | +33,8% | +22,9% | +10,8pp | **+20,2pp** |
| HIGH | 69,8% | 65,9% | 0,55 | +55,6% | +50,2% | +5,4pp | **+28,1pp** |

**Thứ tự đảo hoàn toàn**: excess thô giảm dần LOW→HIGH, alpha sau khử beta **tăng** dần LOW→HIGH.
Nói cách khác, "breadth thấp thì hệ vượt VNI nhiều" chủ yếu là **beta 0,43 trong thị trường rơi
−19,2%** — đúng nghĩa "không lỗ nhiều bằng", không phải kỹ năng chọn/định thời.

---

## 6. Trả lời trực tiếp 3 câu hỏi của B2

1. **n_effective có cao hơn radar không?** — **CÓ, gấp 2,0×** (262 vs 131 episode; median 6 vs 5 năm/ô;
   0% vs 54% số năm bị một nhãn chiếm ≥90%). Đây là kết quả vững, đo được, và là lý do chính đáng để
   dùng breadth thay radar **trong mọi phân tích conditional sau này**.
2. **Có ô nào qua BH FDR 10% không?** — **KHÔNG. 0/27**, y như radar 0/24. Tăng n_effective gấp đôi
   vẫn chưa đủ để một ô nào nổi lên trên nhiễu.
3. **Breadth có phải trục tốt hơn không?** — **Tốt hơn để MÔ TẢ, không phải để wire.** Ưu điểm là cấu
   trúc mẫu; nhược điểm là hai điểm ở §5 — hiệu ứng bề mặt phần lớn là cùng-phiên + beta.

---

## 7. Khuyến nghị

- **KHÔNG wire.** Không đề xuất thay `capit_base()` hay bất kỳ cổng sizing nào theo breadth-tercile
  dựa trên báo cáo này.
- **CÓ đề xuất một thay đổi quy trình, chi phí bằng 0:** mọi phân tích conditional (ma trận, phân rã,
  bảng regime) từ nay dùng **breadth-tercile PIT** thay `Value Radar zone` làm trục 2 mặc định. Radar
  giữ nguyên vai trò **DISPLAY-ONLY trong báo cáo** như §6b coding_guidelines đã chốt — chỉ là đừng
  dùng nó làm trục phân tích nữa, vì nó là kỷ nguyên trá hình.
- **Nếu ai muốn theo tiếp**: bài toán đúng không phải "ô nào có excess cao" mà là "**alpha sau khử
  beta** có phụ thuộc breadth không" (§5b gợi ý HIGH > MID > LOW — ngược hẳn trực giác ban đầu, và
  chưa hề được kiểm định). Đó là một prereg MỚI, không phải phần mở rộng của báo cáo này.

**Artifacts**: `strategy_regime_matrix_20260822/b2_breadth.csv`, `b2_cells.csv`, `b2_bh_tests.csv`,
`b2_neff_breadth.csv`, `b2_neff_radar.csv` · script `strategy_regime_matrix_20260822_b2.py`.
