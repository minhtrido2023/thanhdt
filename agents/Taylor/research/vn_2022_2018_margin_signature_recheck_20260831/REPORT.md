# Áp lại Framework B (margin-forced vs fundamentals) vào 2022 và 2018

> Job `Taylor_20260831_050908` · 2026-08-31 · RESEARCH-ONLY, không wire production, không đổi
> DT5G/CAPIT. Tiếp nối job `Taylor_20260831_042737` (Phần 2+3, framework B gốc) và
> `Taylor_20260831_040228` (2022 đã phân tích như 1 episode CONTAINABLE tổng thể, lag chính sách —
> job này hỏi câu KHÁC: bản chất/cơ chế của chính đợt giảm giá).

## Tóm tắt 1 dòng

**Cả 2 giả thuyết ban đầu của user đều chỉ ĐÚNG MỘT PHẦN.** 2022 không phải "thuần margin-forced" —
4 sub-episode margin-cascade có thật (mechanics mạnh hơn cả 07/2026) nhưng **LỒNG BÊN TRONG** một
khủng hoảng niềm tin/tín dụng rộng hơn (SCB bank-run + bear market Mỹ) — `external_flag` FAIL cả 4
lần. 2018 không phải "thuần gradual" — có 1 leg cấp tính đầu tiên (04-06/2018, 2 sub-episode) khớp
**TOÀN BỘ 3 flag** giống hệt 07/2026, thậm chí độ biến động ngày-qua-ngày còn MẠNH HƠN — nhưng sau
đó KHÔNG V-recover mà tiếp tục grind xuống thêm ~9,6% trong 91 phiên (0 cluster) rồi đi ngang hơn 1
năm. Điểm phân biệt mấu chốt hoá ra KHÔNG PHẢI "có cluster margin-cascade hay không" (cả 3 case đều
CÓ) mà là **điều gì xảy ra SAU cluster đó** — V-recover nhanh (07/2026) vs tiếp tục suy yếu/lặp lại
(2018/2022).

---

## Case A — 2022: margin-cascade lồng bên trong khủng hoảng niềm tin/tín dụng

### Bước 1 — Quét speed_flag (price component) toàn bộ 2022-01-06 → 2022-11-15

Đỉnh **2022-01-06** (1.528,57) → đáy **2022-11-15** (911,90), tổng **-40,34%** trong 213 phiên
(~42,6 tuần). Quét `≥2 phiên giảm ≥2%/phiên trong cửa sổ 5 phiên` trên TOÀN BỘ giai đoạn: **25
cửa sổ TRUE**, gom vào **4 cụm rời rạc**:

| Cụm | Ngày | Đỉnh giảm 1 phiên | Ghi chú thời sự |
|---|---|---|---|
| 1 | 2022-05-09 → 05-18 | -4,82% (05-12), -4,53% (05-13) | Bond-market crackdown (Tân Hoàng Minh 04/2022) + Fed 50bp hike toàn cầu |
| 2 | 2022-10-06 → 10-13 | -3,59% (10-07) | **Trùng khít SCB bank-run/Vạn Thịnh Phát** (bắt Trương Mỹ Lan 07/10/2022) |
| 3 | 2022-10-24 → 10-27 | -3,30% (10-24) | Tiếp diễn khủng hoảng thanh khoản, SBV tăng lãi suất cuối 10/2022 |
| 4 | 2022-11-07 → 11-16 | -3,89% (11-10), -3,10% (11-15, đáy) | Call-margin hàng loạt lan rộng, đáy tuyệt đối |

### Bước 2 — Breadth confirmation (universe_pit D_RSI<0,30, BQ)

Cả **4/4 cụm** đều có breadth_oversold nhảy **>10pp trong cửa sổ 5 phiên** — vượt xa ngưỡng framework
và vượt xa cả baseline 07/2026 (~14pp):

| Cụm | Max 5-phiên breadth jump | Đỉnh %oversold đạt được |
|---|---|---|
| 1 (05/2022) | **+37,4pp** | 56,5% |
| 2 (SCB, đầu 10/2022) | **+35,0pp** | 62,9% |
| 3 (cuối 10/2022) | **+39,5pp** | 56,2% |
| 4 (11/2022) | **+33,1pp** | 73,3% (cao nhất toàn giai đoạn) |

→ **`speed_flag` (đầy đủ price+breadth) = TRUE cho cả 4/4 cụm.** Mechanics margin-cascade ở 2022
mạnh HƠN 07/2026 về biên độ breadth (33-40pp vs ~14pp), không hề yếu hơn.

### Bước 3 — earnings_flag

Q3/2022 phát hành đúng trùng cụm 3 (24-27/10, đỉnh phát hành 18-31/10). Median NP_R (YoY) Q3/2022 =
**-7,70%**, so với trailing 4 quý trước đó (Q3'21 -18,9%, Q4'21 -8,4%, Q1'22 +3,2%, Q2'22 -3,7%,
trung bình **-6,95%**) — **xấp xỉ, không rõ ràng xấu hơn** (earnings_flag borderline TRUE tại thời
điểm đó). Nhưng **Q4/2022 (phát hành 01-02/2023, SAU đáy) sụt -39,26% YoY** — mức tệ nhất trong toàn
bộ chuỗi quý kiểm tra (2017Q4→2023Q1) — xác nhận khủng hoảng tín dụng/thanh khoản THẬT đang hình
thành, chỉ chưa lộ ra hết trong số liệu công bố tại lúc giá đang giảm.

### Bước 4 — external_flag

**FAIL cả 4/4 cụm** — khác hẳn 07/2026 (US pillar hoàn toàn sạch):

| Cụm | VIX range | SPX dd_1y range |
|---|---|---|
| 1 (05/2022) | 26,1-34,8 | -18,7% đến -13,5% |
| 2 (SCB) | 28,5-33,6 | **-25,4%** đến -21,0% |
| 3 | 25,8-29,9 | -20,8% đến -18,7% |
| 4 | 22,5-26,1 | -21,8% đến -16,8% |

Toàn bộ 2022, VIX ≥22,5 và SPX dd_1y vượt hẳn ngưỡng "sạch" -15% (chạm tới -25,4%) — đây là **bear
market Mỹ thật** (chu kỳ Fed hiking 2022), không phải VN đơn độc.

### Kết luận Case A

2022 **KHÔNG PHẢI** thuần margin-forced tách biệt (như 07/2026) và **CŨNG KHÔNG PHẢI** thuần
fundamentals-selloff phẳng lặng — nó là **cả hai cùng lúc, xếp lồng nhau**: mechanics margin-cascade
xuất hiện lặp lại 4 lần với cường độ MẠNH (breadth jump 33-40pp, mạnh hơn baseline 07/2026), nhưng
mỗi lần đều xảy ra trong bối cảnh **external KHÔNG sạch** (bear market Mỹ) và ít nhất 1 lần trùng
khít với **1 cú sốc niềm tin nội địa cụ thể** (SCB bank-run 06-08/10, sau đó là Q4 earnings crash
xác nhận tín dụng thật sự xấu đi). Đúng như user đặt giả thuyết ban đầu: **2022 = margin-cascade
LỒNG BÊN TRONG một khủng hoảng niềm tin/fundamentals rộng hơn**, không phải thuần cơ chế nào riêng lẻ.

---

## Case B — 2018: front-loaded acute leg rồi grind, KHÔNG hoàn toàn "gradual"

### Bước 1 — Quét toàn bộ giai đoạn từ đỉnh đến ổn định

Đỉnh **2018-04-09** (1.204,33) → đáy riêng của 2018 **2018-10-30** (888,69, **-26,21%**, 142 phiên,
~28,4 tuần) → sau đó **cả năm 2019** (436 phiên) đi ngang trong biên 878,22-1.024,91 (không phá đáy
mới, không hồi phục về đỉnh cũ) — đúng là giai đoạn "ổn định lại" theo nghĩa không còn xu hướng rõ,
trước khi COVID (2020-03) tạo một cuộc khủng hoảng HOÀN TOÀN KHÁC xen vào.

Quét `speed_flag` (price-only) trên TOÀN BỘ 2018-04-09 → 2019-12-31 (436 phiên): **20 cửa sổ TRUE**,
nhưng **TẤT CẢ đều nằm gọn trong 2018-04-23 → 2018-06-22** — **ZERO** cửa sổ TRUE trong suốt 2018-06-23
→ 2019-12-31 (≈300 phiên liên tục, hơn 1 năm).

### Bước 2 — Breadth confirmation cho 3 cụm price-flagged trong 2018

| Cụm | Ngày | Max 5-phiên breadth jump | Kết luận |
|---|---|---|---|
| 1 | 2018-04-23 → 05-04 | **+15,6pp** | TRUE (vượt ngưỡng 10pp) |
| 2 | 2018-05-21 → 05-31 | **+26,4pp** | TRUE (mạnh, gần bằng 2022) |
| 3 | 2018-06-19 → 06-22 | +4,6pp | **FALSE** — chỉ là nhiễu giá, không phải breadth-cascade thật |

→ **2/3 cụm khớp FULL speed_flag** (price+breadth), không phải zero như giả thuyết ban đầu.

### Bước 3 — earnings_flag & external_flag cho 2 cụm khớp

- **Cụm 1** (23/04-04/05): trùng khít mùa BCTC Q1/2018 (đỉnh phát hành 23/04 và 02/05). Median NP_R
  Q1/2018 = **-1,86%**, TỐT HƠN trailing avg 3 quý trước (2017Q2 -10,4%, Q3 -5,1%, Q4 -13,6%, TB
  -9,7%) → **earnings_flag TRUE** (loại trừ rõ ràng "bán vì KQKD xấu" — KQKD thực ra đang cải thiện).
  VIX 13,2-18,0 / SPX dd_1y -5,2% đến -8,5% → **external_flag TRUE** (Mỹ hoàn toàn sạch).
- **Cụm 2** (21-31/05): không trùng đợt phát hành lớn (N/A cho earnings_flag). VIX 12,4-17,0 / SPX
  dd_1y -4,3% đến -6,4% → **external_flag TRUE**.

→ **Cụm 1 khớp ĐỦ 3/3 flag** — signature **giống hệt cơ chế 07/2026** (margin/technical, không phải
KQKD, không phải ngoại sinh). Cụm 2 khớp 2/3 (thiếu dữ liệu earnings để test, không phải FALSE).

### Bước 4 — Profile hình dạng: so sánh tốc độ giảm 3 case

| Giai đoạn | Phiên | Tuần | Tổng giảm | Tốc độ (%/tuần) | Std ngày | Ngày tệ nhất | %ngày giảm≥2% |
|---|---|---|---|---|---|---|---|
| **07/2026 FULL** (đỉnh→đáy, baseline margin-forced) | 45 | 9,0 | -13,46% | **-1,50%** | 0,99% | -3,58% | 6,4% |
| **2018 PHASE 1** (09/04→22/06, acute) | 51 | 10,2 | -18,36% | -1,80% | **1,83%** | -3,86% | **25,5%** |
| **2018 PHASE 2** (22/06→30/10, grind) | 91 | 18,2 | -9,61% | -0,53% | 1,17% | -4,84% | 2,2% |
| **2018 FULL** (09/04→30/10) | 142 | 28,4 | -26,21% | -0,92% | 1,44% | -4,84% | 10,6% |
| **2022 FULL** (06/01→15/11) | 213 | 42,6 | -40,34% | -0,95% | 1,50% | -4,95% | 10,8% |

**Phát hiện bất ngờ:** PHASE 1 của 2018 (11/04-22/06) có độ biến động ngày-qua-ngày (std 1,83%) và tỷ
lệ ngày giảm mạnh (25,5% số phiên) **CAO HƠN** cả baseline 07/2026 (0,99%/6,4%) — nghĩa là leg đầu của
2018 về mặt THUẦN TÚY tốc độ/biến động **dữ dội hơn**, không phải "nhẹ nhàng hơn", 07/2026. Cái làm
2018 khác 07/2026 không phải là cường độ cú sập, mà là **KHÔNG CÓ V-recovery sau đó** — 07/2026 hồi
63,1% khoảng cách giảm trong 5,5 tuần sau đáy; 2018 sau Phase1 (kết thúc 22/06 ở 983,17) tiếp tục grind
xuống thêm 9,6% trong 18,2 tuần nữa (0 cluster margin-cascade nào trong suốt Phase2), rồi đi ngang
hơn 1 năm.

### Kết luận Case B

Giả thuyết user ("2018 = điều chỉnh kéo dài, không phải sập nhanh") **ĐÚNG cho phần đa số thời gian
(Phase 2 + cả 2019, ~330/436 phiên, ~76% thời lượng, KHÔNG có margin-cascade signature nào)** nhưng
**SAI cho leg mở đầu (Phase 1, 51 phiên đầu, ~70% tổng biên độ giảm điểm)** — leg đó khớp cơ chế
margin-forced gần như y hệt 07/2026 (đủ 3 flag ở cụm 1, biến động còn mạnh hơn). 2018 là case **hai
pha rõ rệt**: mở đầu bằng 1 cú sập cấp tính kiểu margin-cascade (correcting đòn bẩy tích luỹ sau bull
run 2017 +48%), sau đó KHÔNG hồi phục mà chuyển sang chế độ suy yếu chậm/đi ngang kéo dài — khác 2022
(margin-cascade LẶP LẠI nhiều lần suốt cả giai đoạn) và khác 07/2026 (chỉ 1 cluster, V-recover ngay).

---

## Tổng hợp — cập nhật Framework B: 3 hình dạng, không phải 2

Framework B gốc (job 042737) chỉ hỏi "3 flag TRUE hay không" tại MỘT thời điểm cắt lát. Bằng chứng
mới cho thấy cần thêm **chiều thứ 4 — điều gì xảy ra SAU cluster** để phân biệt đủ 3 archetype quan
sát được:

| Archetype | Case | Cluster margin-cascade (speed+breadth) | External sạch | Điều xảy ra SAU cluster |
|---|---|---|---|---|
| **(1) Pure margin-forced, contained** | 07/2026 | 1 cụm duy nhất | Sạch (VIX 15-21, SPX dd≤-3,9%) | V-recover nhanh (63% trong 5,5 tuần), breadth lành trong ~1 tuần |
| **(2) Front-loaded acute → grind** | 2018 | 2 cụm (đầu Phase1), rồi **0 cụm** suốt ~300 phiên | Sạch cả 2 cụm | KHÔNG V-recover — tiếp tục grind -9,6% thêm 91 phiên, rồi sideways >1 năm |
| **(3) Cascade nested-in-crisis** | 2022 | 4 cụm, LẶP LẠI xuyên suốt cả giai đoạn | **KHÔNG sạch** (VIX 22,5-35, SPX dd tới -25,4%) cả 4 lần | Mỗi cụm hồi ngắn rồi sập cụm tiếp — không ổn định cho tới đáy tuyệt đối tháng 11 |

**Hệ luỵ cho việc dùng speed_flag/breadth-jump làm tín hiệu độc lập:** bản thân "cluster margin-cascade
xuất hiện" (đủ price+breadth) **KHÔNG phân biệt được** case containable (07/2026, Phase1-2018) với
case đang nằm trong khủng hoảng sâu hơn (2022) — cả 3 đều có mechanics gần như giống hệt nhau lúc
xảy ra, thậm chí 2022 và 2018-Phase1 có breadth jump MẠNH HƠN 07/2026. **Phải kết hợp external_flag
tại THỜI ĐIỂM cluster** (2022 fail rõ, 07/2026 và 2018-Phase1 đều sạch) **VÀ THEO DÕI SAU cluster
kết thúc** (V-recover hay tiếp tục suy yếu/lặp lại) mới phân loại đúng — một lát cắt tại chỗ (snapshot)
là không đủ.

## Giới hạn phải mang theo

1. **N vẫn rất nhỏ** — 3 case tổng cộng (07/2026, 2018, 2022), trong đó 2018 tách được 2 cụm và
   2022 tách được 4 cụm nội bộ — không đủ để hiệu chỉnh (calibrate) ngưỡng số nào, chỉ đủ để tinh
   chỉnh KHUNG PHÂN LOẠI định tính.
2. **earnings_flag cho 2022 borderline** (Q3'22 -7,7% vs trailing -6,95%, chênh lệch nhỏ, không rõ
   ràng "xấu hơn hẳn" theo đúng câu chữ framework) — chỉ có Q4'22 (sau đáy) mới xấu rõ rệt. Đây là
   giới hạn thật của flag này khi khủng hoảng tín dụng chưa kịp lộ ra hết trong BCTC ngay lúc giá sập.
3. **RESEARCH-ONLY** — không đề xuất wire vào DT5G/CAPIT/production. Không override quyết định đã
   chốt (VD LAG rating gate §feedback-lag-rating-gate-locked, margin-lever NO-GO).
4. Chưa mở rộng thêm case margin-cascade lịch sử khác ngoài 3 case đã có (2007, 2009-10, COVID 2020
   chưa được áp lại framework B đầy đủ theo cùng phương pháp) — nằm ngoài phạm vi job này.

## Artifact

- `breadth_oversold_2022.csv`, `breadth_oversold_2018.csv` — breadth oversold (universe_pit JOIN
  ticker.D_RSI<0,30) theo ngày, 2022-04-15→12-15 và 2018-04-01→11-15.
- `vnindex_jul2026_close.csv` — giá VNINDEX 07/2026 (BQ, vì `data/VNINDEX.csv` local chỉ tới
  2026-05-26, KHÔNG cập nhật tới 07/2026 — dùng BQ trực tiếp cho case này).
- Bus: `vn-2022-margin-cascade-nested-in-crisis-20260831`, `vn-2018-frontloaded-acute-then-grind-20260831`.
