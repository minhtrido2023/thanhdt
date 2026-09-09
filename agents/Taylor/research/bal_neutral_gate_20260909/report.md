# VÒNG 3 BAL — Trục A (nới cổng NEUTRAL) + Trục B (median lệnh âm)
job `Taylor_20260909_121342` · 2026-09-09 · **PAPER-ONLY** · **VERDICT: NO-GO cả 7 chân**

Tiền đăng ký: `PREREG.md`, viết **trước** khi chạy chân treatment nào (7 tiêu chí GO, N_trials=7,
mọi hằng số lấy từ production, không grid-search). Không có chân nào ngoài 7 chân đã khai.

---

## 0. Kết quả một dòng

| trục | chân | luật | ΔCAGR | MaxDD | Calmar | verdict |
|---|---|---|---|---|---|---|
| A | **a1** | mở `state5 IN (3,4,5)` cho MEGA/MOMENTUM/DVR | **−3,88pp** | **−33,59%** | 0,744 | NO-GO |
| A | **a2** | a1 + `pe_z < −0,5` cho nhánh NEUTRAL | **−2,72pp** | −27,64% | 0,946 | NO-GO |
| A | **a3** | a1 + nửa tỷ trọng (5%) cho lệnh NEUTRAL | **−1,56pp** | −25,81% | 1,058 | NO-GO |
| A | **a4** | a1 + chỉ mở khi breadth-tercile PIT = HIGH | **+0,31pp** | −18,79% | 1,553 | NO-GO |
| B | **b1** | stop −20% → **−10%** | **+0,32pp** | −18,70% | 1,560 | NO-GO |
| B | **b2** | chốt lời **50% khi +20%** (giữ hold-45 + stop −20%) | **−0,41pp** | −19,34% | 1,471 | NO-GO |
| B | **b3** | mọi lệnh BAL phải `pe_z < −0,5` | **−0,80pp** | −17,21% | 1,630 | NO-GO |
| — | ctrl | pin R3 | — | −17,785% | 1,6229 | — |

**Không chân nào qua C1** (ngưỡng nhiễu +0,385pp). Hai chân dương (a4 +0,31 / b1 +0,32) đều nằm
**dưới** sàn nhiễu, và cả hai còn trượt tiếp C2/C4/C5/C6. Đây là vòng NO-GO thứ **ba** liên tiếp
trên book BAL.

## 1. Chân control — harness sạch (C7)

CSV md5 **`7d053e6201c9d107685ff4d1dd9d2d2a`** = **TRÙNG BYTE** pin R3 2026-08-03.
CAGR 28,8627% · Final NAV 1.178,0099B · MaxDD −17,785% · Calmar 1,6229 — trùng pin từng chữ số.
`self-check 0 VND` (cash-flow identity **và** final-NAV identity, cả sổ BAL lẫn LAG) trên **cả 8
chân**. Bẫy `sys.path` của vòng 2 đã xử lý tường minh (`gate_engine.py` re-insert thư mục nghiên
cứu ngay sau dòng `sys.path.insert(0, WORKDIR)`); control chạy qua chính đường đó nên md5 trùng là
bằng chứng bản copy trung thực.

---

# TRỤC A — nới cổng vào BAL trong NEUTRAL

## 2. Cổng KHÔNG phải nút cổ chai lợi nhuận — nó là chốt rủi ro

Mở cổng làm đúng cái nó phải làm về mặt cơ học: **số lệnh hơn gấp đôi**, phần lớn là lệnh mới sinh
trong NEUTRAL.

| chân | tổng lệnh BAL | vào ở state 3 | vào ở state {4,5} | MaxDD | ngày đáy |
|---|---|---|---|---|---|
| ctrl | 452 | 118 (RE_BACKLOG_BUY) | 333 | −17,79% | 2018-07-05 |
| a1 | **976** | **709** | 262 | **−33,59%** | **2020-07-27** |
| a2 | 704 | 444 | 254 | −27,64% | 2020-07-27 |
| a3 | 865 | 620 | 242 | −25,81% | 2020-07-27 |
| a4 | 666 | 389 | 273 | −18,79% | 2020-07-27 |

Cả 4 chân A **đổi ngày đáy drawdown từ 2018-07 sang 2020-07**, và tháng tệ nhất của a1 so với
control là **2020-03: −13,22pp trong một tháng**. Cơ chế rõ: khi được phép mở lệnh trong NEUTRAL,
BAL đi vào cú sập COVID với sổ cổ phiếu momentum gần đầy thay vì rổ parking. Đây chính xác là kịch
bản mà gate `state5 IN (4,5)` tồn tại để chặn. Ba biến thể bù rủi ro (định giá / kích thước /
breadth) đều **giảm được mức thiệt hại nhưng không đảo được dấu**: −33,6% → −27,6% → −25,8% →
−18,8% MaxDD, ΔCAGR −3,88 → −2,72 → −1,56 → +0,31pp. Đơn điệu theo mức độ siết — nghĩa là siết
càng chặt càng tiến gần về **chính control**, không phải tiến tới một tối ưu mới.

## 3. Đối chứng bắt buộc: EXPOSURE hay SELECTION? (PREREG §6)

Đo trên **1.895 phiên NEUTRAL**, từ `bal_stocks_ref` / `bal_etf_ref` / `nav_bal_ref`:

| chân | w_stock % | w_park % | **w_equity %** | Δw_equity | lợi suất năm hoá của sổ BAL trong NEUTRAL |
|---|---|---|---|---|---|
| ctrl | 21,65 | 51,35 | **73,00** | — | 32,56% |
| a1 | 71,08 | 17,04 | **88,12** | **+15,12pp** | 31,09% |
| a2 | 52,01 | 30,46 | 82,46 | +9,47pp | 29,41% |
| a3 | 52,73 | 30,00 | 82,73 | +9,74pp | 32,78% |
| a4 | 44,10 | 35,69 | 79,79 | +6,79pp | 30,98% |
| b1/b2/b3 | ~20 | ~52,5 | ~72,5 | −0,4…−0,5pp | 31,4-32,5% |

**Giả thuyết "chỉ là hoán đổi rổ" BỊ BÁC.** Ngưỡng chốt trước là |Δw_equity| ≤ 2pp; thực đo
**+6,8 đến +15,1pp**. Lý do cơ học: parking chỉ nhận **70%** book (`PARK_STATES="3:0.7"`), 30% còn
lại nằm tiền mặt, trong khi sleeve momentum có thể chiếm >90% book. Nới cổng vì vậy **tăng thật**
rủi ro cổ phần trong NEUTRAL.

Và đây là điểm quan trọng nhất của trục A: **exposure tăng 6,8-15,1pp mà lợi suất sổ BAL trong
NEUTRAL vẫn GIẢM** (32,56% → 29,4-32,8%). Không cần tới quy tắc quy-delta-cho-beta của PREREG §6.3
— nó chỉ ràng buộc khi ΔCAGR > 0. Ở đây kết luận mạnh hơn: **rổ momentum mở trong NEUTRAL thua rổ
custom30V ngay cả khi được cấp thêm vốn.** custom30V parking (phần tin cậy nhất của V2.4, +7,4pp
Full) không phải chỗ trú tạm — nó là lựa chọn TỐT HƠN trong NEUTRAL.

## 4. Chất lượng lệnh sau khi nới cổng — xấu đi trên mọi chiều

Sổ lệnh dựng lại từ chính file audit của từng chân (`record_type=TX`, `book=BAL`, gộp theo
`holding_id`, loại `ETF_PARK`/`CAPIT_*`/`ABANDONED_REFUND` — kiểm chứng: control cho đúng **268**
lệnh, trùng số của sổ CCS Phase 0 dựng từ cùng file pin).

| chân | n | mean % | **median %** | hit % | topdec share of gain % | net P&L (B) |
|---|---|---|---|---|---|---|
| ctrl | 268 | 8,93 | **4,89** | 60,07 | 56,24 | 313,05 |
| a1 | 605 | 5,55 | **1,58** | 53,55 | 62,95 | 253,49 |
| a2 | 452 | 6,35 | **0,86** | 51,99 | 65,49 | 276,52 |
| a3 | 621 | 6,16 | **1,65** | 54,11 | 69,34 | 319,04 |
| a4 | 410 | 7,62 | **3,59** | 58,29 | 65,55 | 391,93 |

Mọi chân A đều làm **median lệnh giảm**, **hit giảm**, và **tập trung vào đuôi phải TĂNG**. Tức là
lệnh mới sinh trong NEUTRAL không chỉ ít lãi hơn — chúng còn làm cả sổ **phụ thuộc đuôi nhiều
hơn**, ngược hẳn mục tiêu của trục B.

## 5. Chấm 7 tiêu chí — trục A

| # | ngưỡng | a1 | a2 | a3 | **a4** (chân tốt nhất trục A) |
|---|---|---|---|---|---|
| C1 ΔCAGR | > +0,385pp | −3,88 ❌ | −2,72 ❌ | −1,56 ❌ | **+0,31 ❌** |
| C2 Calmar | ≥ 1,6229 | 0,744 ❌ | 0,946 ❌ | 1,058 ❌ | 1,553 ❌ |
| C3 IS & OOS cùng dương | — | +2,81 / **−9,94** ❌ | −1,24 / −4,18 ❌ | +1,51 / −4,39 ❌ | +1,44 / **−0,76** ❌ |
| C4a LOYO | < 50% | 0,44 ✅ | 0,35 ✅ | 0,73 ❌ | 4,38 ❌ |
| C4b LOWO | < 50% | 0,70 ❌ | 0,66 ❌ | 0,95 ❌ | 3,75 ❌ |
| C5a DSR vs SR_ctrl | > 0,95 | 0,128 ❌ | 0,208 ❌ | 0,322 ❌ | 0,463 ❌ |
| C5b PBO (CSCV S=16, 8 config) | < 0,5 | **0,519 ❌** (chung cho cả job) | | | |
| C6 bootstrap CI95 | loại trừ 0 | [−7,21;+0,55] ❌ | [−5,31;+0,58] ❌ | [−3,82;+1,18] ❌ | [−1,58;+2,03] ❌ |
| C7 self-check | 0 VND | ✅ | ✅ | ✅ | ✅ |

`C4a/C4b > 1` ở a4/b1 nghĩa là **một rổ đơn lẻ lớn hơn cả tổng delta** — các phần bù trừ nhau; đó
là chữ ký nhiễu quỹ đạo, không phải edge.

---

# TRỤC B — median lệnh BAL âm

## 6. B0 — ĐẶC TÍNH hay KHIẾM KHUYẾT? (phần bắt buộc, làm TRƯỚC mọi treatment)

Nguồn: sổ lệnh CCS Phase 0 dựng từ chính artifact pin. Lọc `book=BAL`, bỏ arm CAPIT, bỏ
`ABANDONED_REFUND` ⇒ **268 lệnh, 2015-2026** (2014 và 2022 không có lệnh BAL nào).

| năm | n | mean % | **median %** | hit % | skew | top-3 share of gain % | top-decile share % | ey median |
|---|---|---|---|---|---|---|---|---|
| 2015 | 5 | 19,95 | **−4,95** | 40,0 | 1,48 | 100,0 | 99,3 | 0,06 |
| 2016 | 6 | 8,07 | 3,67 | 83,3 | 0,29 | 90,7 | 82,2 | 0,08 |
| 2017 | 24 | 6,70 | 4,16 | 62,5 | 0,57 | 50,6 | 75,8 | 0,09 |
| 2018 | 23 | 1,77 | **−6,92** | 43,5 | 0,99 | 65,9 | 83,2 | 0,07 |
| 2019 | 11 | 2,43 | 0,19 | 54,5 | 1,62 | 97,0 | 88,6 | 0,08 |
| 2020 | 39 | 16,33 | 12,12 | 71,8 | 0,43 | 28,9 | 36,1 | 0,10 |
| 2021 | 71 | 10,33 | 6,45 | 59,2 | 1,19 | 31,1 | 54,6 | 0,08 |
| 2023 | 6 | 2,01 | 0,64 | 50,0 | −0,16 | 100,0 | 50,5 | 0,09 |
| 2024 | 27 | 10,44 | 9,22 | 77,8 | 0,65 | 33,8 | 33,8 | 0,05 |
| **2025** | **41** | **5,03** | **−0,96** | **48,8** | **1,05** | **42,5** | **50,3** | **0,08** |
| 2026 | 15 | −5,17 | **−9,38** | 26,7 | 0,48 | 99,5 | 71,7 | 0,06 |
| **ALL** | 268 | 8,10 | 4,15 | 58,2 | 1,31 | 14,5 | 57,2 | 0,08 |

**Trả lời: ĐẶC TÍNH, không phải khiếm khuyết — và 2025 KHÔNG bất thường.**

1. **`mean > median` ở 11/11 năm; skew > 0 ở 10/11 năm.** Lệch phải là hằng số của book này, không
   phải chuyện của riêng 2025.
2. **Median âm xảy ra ở 4/11 năm** (2015, 2018, 2025, 2026) — không phải chuẩn mực đa số, nhưng
   cũng không hiếm (36%). 2018 (−6,92%) và 2026 (−9,38%) đều âm **sâu hơn** 2025 (−0,96%).
3. 2025 nằm ở **phân vị 30%** của chính lịch sử BAL về median, hit và top-3 share; phân vị 70% về
   skew; phân vị 40% về mean. Không có chiều nào 2025 là ngoại lai.
4. **Điểm phản trực giác quan trọng: 2025 PHỤ THUỘC ĐUÔI ÍT HƠN mức thường của BAL.** top-3 share
   2025 = 42,5% trong khi trung vị các năm khác = **78,3%**; top-decile share 2025 = 50,3% vs trung
   vị 54,4%. Câu "2025 dương nhờ đuôi phải" đúng về sự kiện nhưng **sai về hàm ý bất thường** —
   BAL dương nhờ đuôi phải ở gần như mọi năm, và 2025 là một trong những năm ít phụ thuộc đuôi
   nhất. (Cảnh báo đọc số: top-3 share bị thổi lên ở năm ít lệnh — 2015 n=5 nên = 100% theo định
   nghĩa. Cột top-decile share là phiên bản so sánh được giữa các năm.)
5. Toàn kỳ: **top 3 lệnh (1,1% số lệnh) = 14,5% tổng lãi gộp; top 10 lệnh (3,7%) = 32,4%.**

**Hệ quả trực tiếp cho câu hỏi của user:** "vào 2025 theo BAL thì 50% khả năng đã lỗ" là mô tả
đúng — nhưng đó là mô tả **momentum nói chung**, không phải triệu chứng hỏng hóc năm 2025. Chiến
lược đuôi phải kiếm tiền bằng cách thua nhỏ nhiều lần và thắng lớn vài lần. Mọi luật nâng median
phải trả giá ở đuôi phải; §7 đo đúng cái giá đó.

⚠️ **Chênh nhỏ với Phần 1 §6** (báo median 2025 = −0,4%, hit 52%): quy ước lọc của Phần 1 không tái
lập được chính xác từ vật chứng của nó (thử 4 tổ hợp entry-year/exit-year × có/không arm CAPIT đều
không ra đúng cặp số đó; gần nhất là "gộp arm CAPIT" cho hit 52,3%). Quy ước dùng ở đây được khai
tường minh và tái lập được. Kết luận định tính không đổi: median 2025 âm, hit ≈ 50%.

## 7. B1 — ba luật, và cái giá của việc nâng median

Bốn số bắt buộc theo PREREG, đo trên cùng một sổ lệnh dựng lại:

| chân | ΔCAGR | **Δmedian lệnh** | **Δhit** | **Δ đóng góp đuôi (top-decile share)** | MaxDD | Calmar | tỉ lệ dính STOP |
|---|---|---|---|---|---|---|---|
| ctrl | — | 4,89% | 60,07% | 56,24% | −17,79% | 1,6229 | 12,3% |
| **b1** STOP10 | +0,32pp | **−3,79pp** | **−8,25pp** | +7,70pp | −18,70% | 1,560 | **35,9%** |
| **b2** PARTIAL20 | −0,41pp | **+2,06pp** | **+2,47pp** | **−5,13pp** | −19,34% | 1,471 | 11,2% |
| **b3** VALENTRY | −0,80pp | −0,71pp | +0,12pp | +4,29pp | −17,21% | 1,630 | 11,2% |

**b1 (cắt lỗ sớm hơn) làm median TỆ ĐI, không tốt lên.** Đây là kết quả phản trực giác nhất của
vòng này và trả lời thẳng gợi ý của user: hạ stop từ −20% xuống −10% nâng tỉ lệ dính stop từ 12,3%
lên **35,9%**, và vì rất nhiều vị thế chạm −10% rồi hồi, nó **cắt mất chính những lệnh trung vị**
(median 4,89% → 1,10%, hit −8,25pp). Toàn bộ ΔCAGR +0,32pp của b1 đến từ **một năm duy nhất là
2021** (+15,39pp trong khi tổng delta chỉ +0,32pp; C4a = 1,49) — 5 tháng tốt nhất và 3/5 tháng tệ
nhất của b1 đều nằm trong 2021.

**b2 (chốt lời 50% ở +20%) là chân DUY NHẤT nâng được median** (+2,06pp lên 6,95%) **và hit**
(+2,47pp) — và trả giá đúng chỗ PREREG dự báo: **đóng góp đuôi phải giảm 5,13pp**, ΔCAGR **−0,41pp**,
Calmar 1,623 → 1,471. Nói gọn: *nâng median được, nhưng phải mua bằng lợi nhuận.* Đây là bằng chứng
định lượng cho lý do không nên "sửa" median của một chiến lược lệch phải.

**b3 (lọc entry bằng `pe_z < −0,5`) cắt 23% số lệnh** (268 → 206), nâng **mean** (+1,17pp) nhưng
**không** nâng median, và ΔCAGR −0,80pp. Ăn khớp với vòng 1: `ey` có IC OOS thật nhưng BAL không có
đủ chỗ cho nó chạy; dùng nó làm cổng CẤM còn tệ hơn dùng làm khoá sắp xếp.

### Chấm 7 tiêu chí — trục B

| # | ngưỡng | b1 | b2 | b3 |
|---|---|---|---|---|
| C1 ΔCAGR | > +0,385pp | +0,32 ❌ | −0,41 ❌ | −0,80 ❌ |
| C2 Calmar | ≥ 1,6229 | 1,560 ❌ | 1,471 ❌ | 1,630 ✅ |
| C3 IS & OOS cùng dương | — | +0,26 / +0,37 ✅ | −1,07 / +0,25 ❌ | +0,02 / −1,58 ❌ |
| C4a LOYO | < 50% | 1,49 ❌ | 0,84 ❌ | 0,75 ❌ |
| C4b LOWO | < 50% | 2,14 ❌ | 1,39 ❌ | 0,81 ❌ |
| C5a DSR vs SR_ctrl | > 0,95 | 0,562 ❌ | 0,517 ❌ | 0,537 ❌ |
| C5b PBO | < 0,5 | 0,519 ❌ | | |
| C6 bootstrap CI95 | loại trừ 0 | [−0,86;+1,44] ❌ | [−1,37;+0,85] ❌ | [−2,62;+1,30] ❌ |
| C7 self-check | 0 VND | ✅ | ✅ | ✅ |

**b1 là chân duy nhất của cả job qua C3** (IS +0,26 / OOS +0,37 cùng dương) — nhưng ΔCAGR dưới sàn
nhiễu và C4a/C4b nói thẳng nó chỉ là một sự kiện 2021. NO-GO.

### Giới hạn N — nói rõ ở đúng chỗ

**2025 = 2 cửa sổ regime trong tổng 10** (`p1_bull_windows.csv`: 2025-03-07 và 2025-08-12). Mọi
phát biểu về "2025" trong báo cáo này là mô tả một mẫu **không độc lập**, không phải một quan sát
thống kê riêng. 41 lệnh của 2025 nằm trong 2 cược regime. Đây là lý do B0 được viết ở dạng **so
sánh 2025 với chính 11 năm của BAL** thay vì test giả thuyết trên riêng 2025.

---

## 8. Kết luận

1. **Trục A NO-GO.** Nới cổng NEUTRAL không phải là mở nút cổ chai — cổng `state5 IN (4,5)` đang
   làm việc chốt rủi ro thật: mở ra làm MaxDD từ −17,8% xuống **−33,6%** và ΔCAGR **−3,88pp**.
   Ba cách bù rủi ro (định giá / nửa size / breadth) chỉ **giảm thiệt hại đơn điệu về phía
   control**, không tạo được điểm tốt hơn control.
2. **Giả thuyết "chỉ đổi rổ" bị bác bằng số:** nới cổng **tăng thật** tỷ trọng cổ phần trong NEUTRAL
   +6,8…+15,1pp (parking chỉ nhận 70% book). Và dù được cấp thêm vốn, sleeve momentum trong NEUTRAL
   vẫn **thua rổ custom30V**. Không có phần delta nào để quy cho selection.
3. **Trục B: median lệnh âm là ĐẶC TÍNH của momentum, không phải khiếm khuyết của 2025.**
   mean > median 11/11 năm, skew > 0 10/11 năm, median âm 4/11 năm; 2025 ở phân vị 30% và **ít phụ
   thuộc đuôi hơn** mức thường của chính BAL (top-3 share 42,5% vs trung vị 78,3%).
4. **Cả 3 luật "cải thiện" đều NO-GO, và hai trong ba dạy một bài học ngược:** cắt lỗ sớm hơn
   (b1) làm median **tệ đi** vì cắt trúng lệnh sẽ hồi; chốt lời một phần (b2) là cách duy nhất nâng
   median (+2,06pp) nhưng đúng bằng cách **cắt đuôi phải** (−5,13pp) và **mất −0,41pp CAGR**.
5. **Khuyến nghị:** đóng cả hai trục. Không wire gì. `NGATE`/`BRULE` là env nghiên cứu, mặc định
   `off`; production `signal_v11_sql.py`, `pt_v23_audit_2014.py`, `simulate_holistic_nav.py`,
   `filter.json`, `macro_state_live.py` **không bị sửa**.
6. **Điều DUY NHẤT còn đáng theo dõi** (không phải đề xuất hành động): `ey` lúc BAL vào lệnh
   (`ey_median` trong bảng §6) đi 0,09 (2017) → 0,08 (2021) → 0,05 (2024) → 0,08 (2025) → 0,06
   (2026) — **không đơn điệu**, nên chưa xác nhận được xu hướng "mua ngày càng đắt" mà Phần 1 nêu.
   Cần thêm dữ liệu 2027, không hành động bây giờ.
7. **Ba vòng NO-GO độc lập** trên BAL (chọn mã → cơ chế thoát → cổng vào + luật lệnh) là một kết
   luận có nội dung, không phải chuỗi thất bại: nó nói V2.4 đang ở **điểm ổn định cục bộ**, và
   nguồn lợi nhuận trong NEUTRAL là **custom30V parking**, không phải momentum.

## 9. Vật chứng

`PREREG.md` · `gate_engine.py` · `simulate_holistic_nav.py` (copy + `partial_take_tiers`) ·
`run_leg.sh` · `run_{ctrl,a1,a2,a3,a4,b1,b2,b3}.log` · `analyze.py` + `analyze_out.txt` ·
`ab_metrics.csv` · `peryear.csv` · `perwindow.csv` · `exposure_decomp.csv` ·
`b0_peryear_dist.py` + `b0_peryear_dist.csv` + `b0_out.txt` ·
`b1_trade_stats.py` + `b1_trade_stats{,_2025}.csv` + `b1_out.txt` ·
`mech_gate.py` + `mech_gate.csv` + `mech_out.txt` · `breadth_pit_frozen.csv`.
NAV CSV: `data/v23_golive_audit_..._exp_balgate{ctrl,a1..a4,b1..b3}.csv` (`AUDIT_EXP_TAG` giữ mọi
output khỏi đường dẫn canonical — §8 coding_guidelines).
