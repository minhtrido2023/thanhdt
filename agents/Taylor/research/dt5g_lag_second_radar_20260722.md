# DT5G có "chậm" trong đợt giảm 2026-05→07 không? Và "radar thứ 2" có báo sớm được không?
Job `Taylor_20260722_172427` · Taylor · 2026-07-23 (dữ liệu tới phiên 2026-07-22, BQ LIVE, không qua cache)

## 1. Sự thật thị trường hiện tại

| Mốc | Giá trị |
|---|---|
| Đỉnh gần nhất | **2026-05-18 = 1927.94** |
| Hiện tại | **2026-07-22 = 1668.53** |
| Sụt | **−13.45%**, 43 phiên |
| Giai đoạn cấp tính | 07-17 (1787.45) → 07-22 (1668.53) = **−6.65% / 3 phiên**; riêng 07-22 −3.58% |

**DT5G**: `NEUTRAL(3)` liên tục từ **2026-02-13** đến 07-22 = **106 phiên, KHÔNG có transition nào.**

**Base v3.4b** (`vnindex_5state_tam_quan_v34b_clean`): đã flip `3 → 2 (BEAR)` từ **2026-07-20**, tới 07-22 mới được 3 phiên.
DT 4-gate cần `default=10` phiên để commit ⇒ nếu base giữ BEAR, **DT5G sẽ commit BEAR khoảng 2026-07-31**,
tức trễ ~50 phiên so với đỉnh 05-18.

### Đây là hành vi THIẾT KẾ, không phải hỏng
Đo độ trễ DT5G ở mọi đợt sụt ≥15% từ 2014:

| Đỉnh | Đáy | Sụt | Ngày DT5G hạ state | Trễ (phiên) | VNI đã sụt bao nhiêu khi hạ |
|---|---|---|---|---|---|
| 2014-03-24 | 2014-05-13 | −15.4% | 2014-03-31 | 5 | −2.6% |
| 2014-09-03 | 2014-12-17 | −19.1% | **KHÔNG HẠ** | — | — |
| 2018-04-09 | 2020-03-24 | −45.3% | 2018-05-09 | 19 | −12.2% |
| 2026-01-13 | 2026-03-23 | −16.4% | **KHÔNG HẠ** | — | — |
| **2026-05-18** | **2026-07-22** | **−13.5%** | **chưa hạ** | — | — |

⇒ DT5G **thường xuyên** không hạ state ở các đợt sụt 13–19%. Nó chỉ phản ứng ở các đợt gãy lớn (2018→2020),
và ngay cả khi đó cũng chỉ hạ sau khi VNI đã mất ~12%. Đúng như KB đã pin: **DT5G là fail-safe risk gate
(bảo hiểm), KHÔNG phải return-enhancer / market timer.** Đợt hiện tại nằm trong phân phối hành vi bình
thường của nó, không phải regression.

## 2. Giả thuyết "index dominance" — ĐƯỢC DỮ LIỆU HỖ TRỢ

`concentration_history.csv` (đã tươi tới 07-22), percentile so với toàn bộ 2014+:

| Chỉ số | TB 63 phiên gần nhất | Percentile vs 2014+ |
|---|---|---|
| concentration_score | 0.650 | **85.5%** |
| **VIN_family share** | **0.1042** | **94.0%** |
| capEW_div_60d | 0.0969 | 77.8% |
| HHI_tv | 0.0224 | 69.6% |
| CR3 | 0.1617 | 61.0% |

VIN_family (VIC+VHM+VPL+VRE) share of trading value: 2025 TB **0.051** → 2026 TB **0.085** (gấp ~1,7 lần),
hiện ở percentile 94. concentration_score 2026 TB 0.582 vs 2014+ TB 0.393.

**Bằng chứng trực tiếp hơn về "chỉ số bị vài mã kéo"**: từ **2026-03-09** breadth (% mã `ticker_prune` trên
MA200) rơi xuống <30% và **không bao giờ hồi lại trên 36%**, trong khi VNINDEX vẫn tăng tiếp từ 1652.8 →
**1927.94 (+16.6%)** tới 05-18. M1 divergence (VNINDEX 6m − median stock 6m) chạm **+25pp** ngày 05-20 —
mức chỉ xuất hiện 3 lần trong 12,5 năm.

⇒ **Giả thuyết của user ĐÚNG về mặt mô tả**: đợt tăng cuối (03→05/2026) là megacap-led thật, chỉ số bị
một nhóm nhỏ kéo, đa số cổ phiếu đã yếu từ trước.

## 3. Nhưng "radar thứ 2" KHÔNG báo sớm được đợt này — và lịch sử false-fire rất nặng

### 3a. Trên chính đợt này, thời điểm ra sao?

| Tín hiệu | Ngày bật | So với đỉnh 05-18 |
|---|---|---|
| breadth < 30% | **2026-03-09** | sớm 47 phiên — **nhưng VNI còn tăng +16,6% sau đó** |
| M1 > 20pp | 2026-05-08 | sớm 6 phiên |
| M1 đỉnh +25pp | 2026-05-20 | **trễ 2 phiên** (đồng thời, không dẫn) |
| breadth < 25% | **2026-07-13** | **trễ 39 phiên**, VNI đã mất 6,6% |
| breadth < 20% | 2026-07-20 | trễ 44 phiên |
| Base v3.4b → BEAR | 2026-07-20 | trễ 44 phiên |

Không có ngưỡng nào cho ra một cảnh báo *dùng được*: hoặc bật quá sớm (03-09, bỏ lỡ +16,6%), hoặc bật sau
khi thị trường đã sụt xong phần lớn. **M1 hiện tại = +4,4pp — thậm chí dưới cả ngưỡng thấp nhất (5pp)** vì
megacap đã sụt cùng phần còn lại (capEW_div_60d rơi 0,091 → 0,017 trong 10 phiên).

### 3b. Kiểm tra false-fire lịch sử — cấp ĐỢT, không phải cấp ngày

Đếm theo ngày cho ảo giác thống kê (M1>25 "P(mdd60≤−10%)=53% vs baseline 21,7%" — nhưng 132 ngày đó chỉ là
**3 đợt**, pseudo-replication). Cấp đợt (gap ≥40 phiên):

**M1 > 25pp — 3 đợt / 12,5 năm:**
| Bật | VNI@bật | fwd60 | fwd120 | fwd250 |
|---|---|---|---|---|
| 2017-12-27 | 968.5 | **+20.5%** | +1.5% | −7.9% |
| 2025-08-21 | 1688.0 | −2.0% | **+6.4%** | — |
| 2026-05-19 | 1912.9 | (đang chạy) | | |

**M1 > 20pp — 3 đợt:** 2017-11-21 → fwd120 **+10.5%**; 2025-08-15 → fwd120 **+9.4%**; 2026-05-08 (đang chạy).

**breadth < 25% — 5 đợt:** 2018-07-03 → fwd60 **+11.4%**; 2020-03-12 → **+16.9%**; 2022-05-12 → −17.0% (đúng);
2025-04-08 → **+22.4%**; 2026-07-13 (đang chạy).

⇒ **2/2 đợt M1>25 đã hoàn tất đều là báo động giả** (thị trường tăng tiếp). **2/2 đợt M1>20 đã hoàn tất đều
tăng tiếp hai chữ số.** **3/4 đợt breadth<25 đã hoàn tất là ĐÁY, không phải đỉnh** — dùng nó làm trigger bán
sẽ bán đúng đáy 2020-03 và 2025-04. breadth<25 đúng 1/4 lần (2022).

Cụ thể với M1: nếu de-risk khi M1>20pp ngày **2025-08-15 @VNI 1630**, thị trường tăng tới 1927.94 (+18,3%)
trong 9 tháng tiếp theo trước khi quay đầu; hôm nay 1668.53 vẫn **cao hơn** điểm bật. Chín tháng ngồi ngoài
để rốt cuộc hoà.

## 4. Kết luận

1. **DT5G không "hỏng"**: nó chưa hạ state vì (a) base v3.4b mới flip BEAR được 3 phiên, (b) DT gate cố ý
   cần 10 phiên. Lịch sử 2014-2026, DT5G bỏ qua hoàn toàn nhiều đợt sụt 15–19%. Đây là chi phí đã biết và
   đã được chấp nhận khi chọn DT5G (audit: DT5G ≡ DT4 ở 98,4% phiên, chỉ lệch 49 phiên/4 đợt de-risk).
2. **Index-dominance CÓ thật** (VIN_family pct 94, concentration_score pct 85, breadth <30% suốt 2 tháng
   trong khi index +16,6%). Giả thuyết user đúng về chẩn đoán.
3. **Nhưng chẩn đoán đúng ≠ tín hiệu timing dùng được.** Cả M1 lẫn breadth đều KHÔNG báo sớm đợt này ở
   ngưỡng dùng được, và lịch sử cấp-đợt cho tỷ lệ báo động giả rất cao (M1: 0/2 đúng; breadth<25: 1/4 đúng,
   3/4 là đáy). n hiệu dụng = 3–5 đợt trong 12,5 năm ⇒ **không đủ để wire bất kỳ trigger nào.**

## 5. Đề xuất

**KHÔNG wire M1 hay breadth vào DT5G pipeline dưới dạng gate.** Lý do: (a) n cấp đợt = 3–5, (b) 2/2 và 3/4
đợt hoàn tất là false-fire, (c) trong chính đợt đang xét chúng không dẫn trước.

**Nên làm (rẻ, không chạm production gate):**
- Đưa `concentration_score` + `breadth %>MA200` + `M1` vào **EOD report / dna_report như chỉ báo BỐI CẢNH
  (mô tả, không quyết định)** — để đội biết "đợt tăng này hẹp" mà không tự động hoá hành động.
- Nếu user muốn một cơ chế *thật sự* phản ứng nhanh hơn DT5G, hướng đúng KHÔNG phải thêm radar mà là
  **hạ `default` commit của DT 4-gate** (10 → 7/5) — đây là tham số đã có, đo được, ablation được trên
  toàn bộ lịch sử, và đã biết nằm trên plateau robust. Nhưng phải backtest + quant-skeptic trước; và
  KB đã ghi rõ params DT5G là plateau robust, "không re-tune theo lịch sử".
- **Mọi thay đổi DT5G phải qua quant-skeptic + user duyệt.** Điều tra này KHÔNG sửa gì trong production.

## 6. Ghi chú chất lượng dữ liệu (cần Winston xác minh)
`tav2_bq.ticker.VNINDEX` giai đoạn **2026-04-01 → 2026-04-29** toàn số tròn (1700/1690/1680/1670/1680/1760/
1740/1750/1760/1780/1800/1820/1820/1840/1830/1860/1870/1850/1880/1850) — trông như dữ liệu điền tay/synthetic,
khác hẳn 2 chữ số thập phân của mọi giai đoạn khác. Không đổi kết luận ở trên (đỉnh 05-18 và đáy 07-22 đều
ngoài cửa sổ này), nhưng ảnh hưởng nhẹ tới MA200 / lợi suất 6 tháng trong ~4 tháng tới. Nên kiểm tra.
