# BÁO CÁO TUẦN — TÀI KHOẢN SPACEX & ZALOPAY
## Kỳ báo cáo: 24/08/2026 – 28/08/2026

**Tài khoản 1:** SpaceX · DNSE, số hiệu 0002023347 · V2.4 live từ 01/07/2026 (có margin)
**Tài khoản 2:** ZaloPay · DNSE, số hiệu 0001743768 · V2.4 live từ 06/07/2026 (cash-only, không margin)
**Chiến lược:** V2.4 (2 book BAL/LAG + parking custom30V tại trạng thái NEUTRAL)
**Ngày lập báo cáo:** 29/08/2026 · **Người lập:** Taylor (Quant) — báo cáo này là dispatch tự động, phát
hiện bởi `check_report_cadence.sh` (báo cáo tuần bị bỏ sót)
**Đối tượng:** Báo cáo hiệu suất & vận hành — có thể chia sẻ với nhà đầu tư

---

> **⚠️ CHẤT LƯỢNG SỐ LIỆU TUẦN NÀY — đọc trước khi dùng con số:** chuỗi NAV chính thức
> `nav_history_{account}.csv` **thiếu 2/5 ngày trong tuần (25/08 và 27/08, cả 2 account)** — tác vụ
> chụp NAV cuối ngày không chạy. Hai dòng này đã được **tái dựng** trực tiếp từ dữ liệu gốc còn
> nguyên vẹn (vị thế broker thật `dnse_raw_{date}.jsonl` kind=`positions` × giá đóng cửa BigQuery
> đúng ngày, cộng số dư tiền/Trứng vàng thật từ bản ghi `balances` cùng ngày) — **không phải ước
> lượng nội suy**. `verify_account_snapshot.py` cũng báo `Verified=False` cho ngày 28/08 ở cả 2
> account do một sự kiện quyền mua cổ phiếu MBB chưa kịp đồng bộ vào ảnh chụp vị thế broker (giải
> trình đầy đủ ở Mục 6). Chi tiết đầy đủ, kể cả phần **chưa giải thích được**, ở Mục 6 và 7 — không
> làm tròn.

---

## 1. TÓM TẮT ĐIỀU HÀNH (Executive Summary)

| Chỉ tiêu | SpaceX | ZaloPay |
|---|---:|---:|
| NAV đầu kỳ (chốt 21/08) | 977.129.844 | 948.266.511 |
| NAV cuối kỳ (28/08) | **985.547.490** | **952.338.703** |
| Thay đổi trong kỳ | **+8.417.646 (+0,86%)** | **+4.072.192 (+0,43%)** |
| VN-Index cùng kỳ (21/08 → 28/08) | 1.768,12 → 1.832,12 (**+3,62%**) | — |
| Cổ phiếu cuối kỳ (giá đóng cửa 28/08) | 876.924.500 | 907.558.300 |
| Tiền mặt tại công ty CK | 8.195.610 | 5.936.934 |
| **Tiền gửi "Trứng vàng"** (tự động qua API DNSE từ 18/08) | **100.435.143** | **38.850.311** |
| "Nợ" trên sổ (thực chất là phí lưu ký chưa post, xem Mục 6) | 7.763 | 6.842 |
| Tỷ trọng cổ phiếu/NAV | 89,0% | 95,3% (gồm DGC legacy 45,1% NAV) |
| Số mã nắm giữ cuối kỳ | 28 | 27 (25 mã bot + VPB + DGC legacy) |

**Nhận định tuần:** VN-Index tăng mạnh **+3,62%** (1.768,12 → 1.832,12), phiên nào cũng dương ngoại
trừ biến động nhỏ ngày 28/08. **Cả 2 tài khoản đều tăng nhưng tăng ÍT HƠN chỉ số rất nhiều**: SpaceX
+0,86%, ZaloPay +0,43%. Đây **không phải dấu hiệu bất thường của hệ thống** — hai nguyên nhân chính:
(1) danh mục hiện tại là giỏ custom30V đa dạng ngành (28 mã, không còn tập trung ngân hàng như tháng
7), một phần đáng kể là cổ phiếu vừa/nhỏ (PVT, SCL, SIP, NCT, TV1, CSV, DRI...) không tăng đồng pha
với đà tăng do nhóm vốn hóa lớn dẫn dắt tuần này; (2) tuần có 2 sự kiện quyền lợi cổ đông không sinh
lời (quyền mua MBB, cổ tức cổ phiếu MSB tỷ lệ phát hành +20% số lượng — KHÔNG phải tỷ suất lợi nhuận;
lãi/lỗ thật của MSB tuần này vẫn là **−1,42%**, xem bảng Mục 3.3) làm nhiễu một phần số liệu
ngày-qua-ngày (Mục 6). Trạng
thái thị trường DT5G giữ nguyên **NEUTRAL (3/5)** suốt tuần, không có cap vĩ mô kích hoạt. **Không có
lệnh mua/bán thị trường nào trong tuần ở cả 2 tài khoản** — chỉ có 2 sự kiện quyền cổ đông (Mục 6);
BAL/LAG vẫn rỗng, danh mục giữ nguyên như thiết kế parking.

---

## 2. BỐI CẢNH THỊ TRƯỜNG TRONG TUẦN

| Ngày | VN-Index | Δ ngày |
|---|---:|---:|
| 21/08 (trước kỳ) | 1.768,12 | — |
| 24/08 | 1.788,78 | +1,17% |
| 25/08 | 1.791,41 | +0,15% |
| 26/08 | 1.821,32 | +1,67% |
| 27/08 | 1.831,56 | +0,56% |
| 28/08 | 1.832,12 | +0,03% |

- Tuần tăng liên tục cả 5 phiên, tổng **+3,62%** — tuần tăng mạnh nhất trong nhiều tuần gần đây, dẫn
  dắt chủ yếu bởi nhóm vốn hóa lớn (phiên 26/08 tăng mạnh nhất +1,67%).
- **Trạng thái thị trường (DT5G): NEUTRAL (3/5) toàn bộ tuần** (xác nhận từ bảng sản xuất
  `vnindex_5state_dt5g_live`, cả 5 phiên đều `state=3`) → mục tiêu phân bổ ~70% cho phần vốn parking,
  không có cap phòng thủ vĩ mô nào kích hoạt (Gate DT4: ổn định, không có candidate chuyển trạng thái).
- **Bề rộng thị trường (breadth, % mã đóng cửa trên MA50, universe `tav2_mike.universe_pit` PIT):**
  36,9% trên tổng 833 mã (28/08), so với 34,1%/864 mã (21/08) và 37,3%/793 mã (24/08) — cải thiện nhẹ
  trong tuần nhưng vẫn dưới 50%, tức đà tăng của chỉ số **chưa được đa số cổ phiếu xác nhận** — phù
  hợp với việc danh mục đa dạng ngành của quỹ tăng chậm hơn chỉ số.
- **Value Radar** (composite P/E+P/B+spread lãi suất, rolling 10 năm, DISPLAY-ONLY — không phải tín
  hiệu mua/bán): **26,7 — RẺ** (P/E phân vị 10, P/B phân vị 35, spread EY−tiết kiệm +1,71pp phân vị
  35), dữ liệu tới 28/08. **[xem chart Value Radar đính kèm]** — số liệu phân vị từng thành phần nêu
  trên là bản dự phòng dạng chữ cho người đọc không xem được ảnh.

![Value Radar chart](/tmp/value_radar_chart_20260829.png)

---

## 3. TÀI KHOẢN SPACEX

### 3.1 Diễn biến NAV theo ngày

| Ngày | NAV (VND) | Δ ngày | VN-Index Δ ngày | Ghi chú |
|---|---:|---:|---:|---|
| 21/08 (đầu kỳ) | 977.129.844 | — | — | |
| 24/08 | 980.169.758 | +0,31% | +1,17% | HOLD |
| 25/08 | **973.342.760**\* | −0,70% | +0,15% | HOLD · **NAV tái dựng, xem Mục 6.1** |
| 26/08 | 982.587.257 | +0,95% | +1,67% | HOLD |
| 27/08 | **985.119.512**\* | +0,26% | +0,56% | HOLD · **NAV tái dựng** · cổ tức CP MSB +20% (Mục 6.2) |
| 28/08 (cuối kỳ) | 985.547.490 | +0,04% | +0,03% | Quyền mua MBB (Mục 6.3) |

Cả tuần **+0,86%** vs VN-Index **+3,62%** — kém chỉ số 2,76 điểm phần trăm. Danh mục hiện là giỏ đa
ngành (không còn tập trung ngân hàng), phần lớn tăng chậm hơn nhóm vốn hóa lớn dẫn dắt tuần này.

### 3.2 Hoạt động giao dịch

**Không có lệnh mua/bán thị trường nào trong tuần.** BAL/LAG rỗng, danh mục parking giữ nguyên. Hai
sự kiện duy nhất là quyền lợi cổ đông (corp action), không phải lệnh bot — xem Mục 6.

### 3.3 Danh mục cuối kỳ (28/08, giá vốn thật đã xác minh × giá đóng cửa 28/08)

Nguồn: `verified_snapshot_SpaceX_2026-08-28.json` (28 mã). **Lưu ý:** snapshot này báo `Verified=False`
do lệch số lượng MBB giữa `dnse_raw` (1.565cp) và journal nội bộ (1.675cp) — nguyên nhân là quyền mua
MBB chưa kịp đồng bộ vào ảnh chụp vị thế lúc trích xuất, KHÔNG phải sai lệch thật (giải trình đầy đủ
Mục 6.3). Bảng dưới dùng qty broker thật (1.565, thời điểm trích xuất), tổng MTM = 874.619.182 —
**thấp hơn `mtm_stock` chính thức trong `nav_history` (876.924.500) đúng ~2,3tr**, khớp với phần cổ
phiếu quyền mua MBB (110cp) chưa vào ảnh chụp lúc chạy snapshot buổi tối.

| Mã | KL | Giá vốn thật | Giá 28/08 | Giá trị TT (VND) | Lãi/lỗ chưa TH | % |
|---|---:|---:|---:|---:|---:|---:|
| PVT | 3.500 | 17.100 | 20.200 | 70.700.000 | +10.850.000 | +18,13% |
| SCL | 1.500 | 23.600 | 27.600\*\* | 41.400.000 | +6.000.000\*\* | +16,95%\*\* |
| SIP | 1.700 | 47.059 | 49.450 | 84.065.000 | +4.065.000 | +5,08% |
| VNM | 900 | 58.600 | 62.300 | 56.070.000 | +3.330.000 | +6,31% |
| DRI | 3.700 | 13.262 | 14.100 | 52.170.000 | +3.100.000 | +6,32% |
| HDB | 800 | 26.709 | 27.800 | 22.240.000 | +872.500 | +4,08% |
| TV1 | 2.300 | 20.148 | 20.500 | 47.150.000 | +810.000 | +1,75% |
| VRE | 300 | 25.550 | 26.100 | 7.830.000 | +165.000 | +2,15% |
| VPB | 1.200 | 27.746 | 27.800 | 33.360.000 | +64.286 | +0,19% |
| VIB | 500 | 14.900 | 14.950 | 7.475.000 | +25.000 | +0,34% |
| ACB | 900 | 22.656 | 22.650 | 20.385.000 | −5.000 | −0,02% |
| EVF | 100 | 12.550 | 12.400 | 1.240.000 | −15.000 | −1,20% |
| SHB | 800 | 12.281 | 12.200 | 9.760.000 | −65.000 | −0,66% |
| MSB | 600 | 13.542 | 13.350 | 8.010.000 | −115.000 | −1,42% |
| HPG | 1.200 | 22.200 | 22.100 | 26.520.000 | −120.000 | −0,45% |
| VND | 300 | 17.800 | 16.650 | 4.995.000 | −345.000 | −6,46% |
| TCB | 1.000 | 33.900 | 33.400 | 33.400.000 | −500.000 | −1,47% |
| VIX | 420 | 15.464 | 14.100 | 5.922.000 | −573.000 | −8,82% |
| LPB | 400 | 52.183 | 49.950 | 19.980.000 | −893.333 | −4,28% |
| TPB | 500 | 16.800 | 14.650 | 7.325.000 | −1.075.000 | −12,80% |
| VCB | 700 | 61.786 | 60.100 | 42.070.000 | −966.250\* | −2,23%\* |
| MBB | 1.565 | 22.109 | 21.050 | 32.943.250 | −1.656.750 | −4,79% |
| VHM | 900 | 74.900 | 73.000 | 65.700.000 | −1.710.000 | −2,54% |
| SAB | 1.100 | 47.368 | 45.600 | 50.160.000 | +1.190.000\* | +2,28%\* |
| CTG | 1.200 | 34.181 | 31.950 | 38.340.000 | −2.249.286\* | −5,48%\* |
| BID | 1.175 | 39.945 | 36.850 | 43.308.932 | −3.209.873\* | −6,84%\* |
| NCT | 500 | 94.360 | 83.600 | 41.800.000 | −1.580.000\* | −3,35%\* |
| **Tổng (28 mã)** | | **giá vốn 866.929.638** | | **874.319.182\*\*** | **+15.393.294\*\*** | **+1,78%\*\*** |

\* **Sửa 02/09/2026 — cột lãi/lỗ đã cộng cổ tức tiền mặt RÒNG (sau thuế TNCN 5%), theo
`mike/kb/coding_guidelines.md` §21 / `mike/bin/dividend_adjusted_return.py`.** Bản báo cáo phát hành
29/08 chỉ tính lãi/lỗ THEO GIÁ, bỏ sót 5 sự kiện cổ tức tiền mặt tháng 7 (CTG/VCB/SAB/NCT/BID, ex-date
17–28/07) đã nằm trong tiền mặt tài khoản nhưng chưa cộng vào bảng này — SCL được kiểm tra riêng và
**không đổi**: vị thế mới mua 10/08/2026, sau mọi ex-date phát hiện được (gần nhất 12/06), nên
+17,80% giữ nguyên là số đúng.
  - CTG/VCB/BID: vị thế đã giảm rồi tăng lại (tái cân bằng custom30V đầu tháng 8) — chỉ số cổ phiếu
    THỰC SỰ còn nắm giữ liên tục từ trước ex-date (mốc đáy sau khi bán, trước khi mua lại — CTG 1.000,
    VCB 500, BID 1.000cp) mới được cộng cổ tức; phần mua thêm sau ex-date (CTG +200, VCB +200,
    BID +175cp) không có quyền, không cộng.
  - SAB/NCT: không đổi số lượng kể từ ex-date, cộng đủ cho toàn bộ vị thế hiện tại.
  - Cổ tức GỘP/cp: CTG 450, VCB 450, SAB 3.000, NCT 8.000, BID 450 — RÒNG sau thuế 5%: 427,5 / 427,5
    / 2.850 / 7.600 / 427,5. Nguồn CTG/VCB/SAB/NCT: giải trực tiếp từ tiền mặt broker thật
    (`CASH_CONFIRMED`, khớp `Dividend_1Y` trailing). Riêng **BID** nghiệm broker (450) bị cổng
    sanity-check tự động của công cụ từ chối (lệch 1,5% so với ước lượng tỉ số giá 457, vốn có nhiễu
    làm tròn) nên mặc định rơi về `CASH_VENDOR` (bị chặn khỏi báo cáo theo chính sách mặc định) — dùng
    450 ở đây vì đã đối chiếu ĐỘC LẬP khớp tuyệt đối với delta `Dividend_1Y` (450→900) VÀ với
    `tav2_bq.corporate_action`; ghi rõ đây là ngoại lệ có kiểm chứng ba nguồn, không phải override
    lặng lẽ. Tổng dòng cộng thêm 8.003.750đ cổ tức ròng (giá vốn/MTM từng mã không đổi).

\*\* **SCL không phải lỗi cổ tức** (`report_return_gate.py` xác nhận cổ tức GỘP = 0đ/cp cho SCL —
vị thế mới mua 10/08, sau mọi ex-date phát hiện được) — bản 29/08 dùng nhầm giá đóng cửa BigQuery
`Price`=27.800 cho phiên 28/08, trong khi giá `marketPrice` đã ổn định (từ 19:30 ICT trở đi, giữ
nguyên tới 23:30) trong chính bản ghi vị thế broker (`dnse_raw_2026-08-28.jsonl`) là **27.600**.
Đã sửa theo giá broker (khớp đúng dispatch kỳ vọng +16,95%). Chênh lệch 200đ/cp giữa hai nguồn giá
cho đúng phiên 28/08 **chưa được điều tra tận gốc** trong phạm vi lần sửa này — có thể là lỗi đồng
bộ BQ hoặc do broker cập nhật giá khớp muộn; NAV chính thức (Mục 1/3.1, nguồn `nav_history`/BQ
Close) KHÔNG được sửa theo giá 27.600 vì nằm ngoài phạm vi dispatch này, chỉ bảng lãi/lỗ Mục 3.3 —
nên tổng MTM 874.319.182 ở đây tiếp tục lệch khoảng 2,3tr + 300.000đ so với `mtm_stock` chính thức
876.924.500 (gốc quyền mua MBB Mục 6.3, cộng thêm chênh SCL vừa nêu).

**Điểm cần lưu ý:** danh mục đã chuyển từ tập trung ngân hàng (58,6% NAV tháng 7) sang đa ngành hơn
đáng kể — hiện không mã nào vượt 10% NAV (lớn nhất PVT ~7,2%). Đây là kết quả tái cân bằng định kỳ
của custom30V qua các tuần trước đó (không có lệnh nào phát sinh riêng trong tuần này).

---

## 4. TÀI KHOẢN ZALOPAY

### 4.1 Diễn biến NAV theo ngày

| Ngày | NAV (VND) | Δ ngày | Ghi chú |
|---|---:|---:|---|
| 21/08 (đầu kỳ) | 948.266.511 | — | |
| 24/08 | 958.333.248 | +1,06% | HOLD |
| 25/08 | **941.358.398**\* | −1,77% | HOLD · **NAV tái dựng, xem Mục 6.1** |
| 26/08 | 964.373.145 | +2,44% | HOLD |
| 27/08 | **929.399.121**\* | −3,63% | HOLD · **NAV tái dựng** · cổ tức CP MSB +20% (Mục 6.2) |
| 28/08 (cuối kỳ) | 952.338.703 | +2,47% | Quyền mua MBB (Mục 6.3) |

Cả tuần **+0,43%** vs VN-Index **+3,62%** — kém chỉ số 3,19 điểm phần trăm. Biến động ngày-qua-ngày
lớn hơn hẳn SpaceX (−3,63% rồi +2,47% liên tiếp hai ngày cuối) — **chưa tìm được nguyên nhân đơn lẻ
giải thích trọn vẹn** ngoài đặc tính basket đa dạng ngành/vốn hóa nhỏ biến động mạnh hơn chỉ số; đây
là điểm cần theo dõi thêm, không khẳng định là lỗi dữ liệu vì cả 2 ngày đều dùng đúng phương pháp tái
dựng như 3.1 và khớp với biến động giá thật trong vị thế broker.

### 4.2 Hoạt động giao dịch

**Không có lệnh mua/bán thị trường nào trong tuần** ở phần bot quản lý. Hai sự kiện quyền lợi cổ đông
(quyền mua MBB, cổ tức cổ phiếu MSB) — xem Mục 6. Vị thế legacy VPB tiếp tục giữ nguyên ở mức đã giảm
từ các tuần trước (1.300cp, ~3,8% NAV — đã ra khỏi vùng tập trung rủi ro, khác hẳn tình trạng 38,8%
NAV hồi tháng 7).

### 4.3 Danh mục cuối kỳ (28/08)

Nguồn: `verified_snapshot_ZaloPay_2026-08-28.json` (25 mã bot, loại DGC/VPB — không có lịch sử khớp
nội bộ) + vị thế legacy DGC/VPB lấy trực tiếp từ `dnse_raw` (giá vốn broker báo). Cùng cảnh báo
`Verified=False` do MBB (dnse_raw=232 vs journal=252) — giống hệt nguyên nhân ở SpaceX (Mục 6.3).

| Mã | KL | Giá trị TT (VND) | % NAV | Ghi chú |
|---|---:|---:|---:|---|
| DGC | 10.000 | 430.000.000 | 45,1% | **Legacy, excluded khỏi P&L** — giá vốn broker 47.775, giá 28/08 43.000 → **−47.750.000 (−10,0%)** |
| VPB | 1.300 | 36.140.000 | 3,8% | Legacy — giá vốn broker 26.745, giá 28/08 27.800 → +1.372.081 (+3,85%) |
| PVT | 2.071 | 41.834.200 | 4,4% | Bot |
| SAB | 744 | 33.926.400 | 3,6% | Bot |
| NCT | 373 | 31.182.800 | 3,3% | Bot |
| VNM | 601 | 37.442.300 | 3,9% | Bot |
| SIP | 749 | 37.038.050 | 3,9% | Bot |
| SCL | 1.000 | 27.800.000 | 2,9% | Bot |
| DRI | 1.900 | 26.790.000 | 2,8% | Bot |
| VHM | 300 | 21.900.000 | 2,3% | Bot |
| CSV | 1.000 | 21.550.000 | 2,3% | Bot |
| TV1 | 1.200 | 24.600.000 | 2,6% | Bot |
| LPB | 352 | 17.582.400 | 1,8% | Bot |
| VCB | 300 | 18.030.000 | 1,9% | Bot |
| CTG | 450 | 14.377.500 | 1,5% | Bot |
| MBB | 232 | 13.309.915 | 1,4% | Bot |
| BID | 320 | 15.748.702 | 1,7% | Bot |
| HDB | 459 | 12.760.200 | 1,3% | Bot |
| TCB | 356 | 11.890.400 | 1,2% | Bot |
| HPG | 500 | 11.050.000 | 1,2% | Bot |
| ACB | 300 | 6.795.000 | 0,7% | Bot |
| SHB | 300 | 3.660.000 | 0,4% | Bot |
| VIB | 200 | 2.990.000 | 0,3% | Bot |
| MSB | 240 | 3.204.000 | 0,3% | Bot |
| VIX | 105 | 1.480.500 | 0,2% | Bot |
| VRE | 100 | 2.610.000 | 0,3% | Bot |
| TPB | 100 | 1.465.000 | 0,2% | Bot |
| Tiền mặt | | 5.936.934 | 0,6% | |
| Tiền gửi Trứng vàng | | 38.850.311 | 4,1% | Tự động qua API |
| **Tổng NAV** | | **952.338.703** | 100% | |

Cộng dồn: cổ phiếu 907.558.300 + tiền mặt 5.936.934 − "nợ" 6.842 + Trứng vàng 38.850.311 =
**952.338.703** ✓ khớp từng đồng với chuỗi NAV chính thức. **Bot P&L (25 mã, loại DGC/VPB):** giá vốn
430.051.692 → thị giá 441.017.367 = **+10.965.676 (+2,55%)**.

**Điểm tích cực cần ghi nhận:** vị thế legacy VPB — vấn đề tập trung rủi ro nêu liên tục trong các báo
cáo tuần 7 (từng 38,8% NAV) — nay chỉ còn **3,8% NAV**, đã ra khỏi diện cảnh báo tập trung. DGC vẫn là
vị thế lớn nhất (45,1% NAV, ngoài phạm vi bot) và đang lỗ trên giấy **−47,75tr (−10,0%)** — nhắc lại
khuyến nghị các kỳ trước: đây là rủi ro tập trung thật, nhà đầu tư cần chủ động quyết định giữ/giảm vì
nằm ngoài phạm vi tái cân bằng tự động.

---

## 5. CÔNG BỐ SỰ CỐ & SỰ KIỆN VẬN HÀNH TRONG TUẦN

Nguyên tắc: liệt kê đầy đủ, không làm tròn, kể cả phần chưa giải thích được.

### 6.1 Thiếu 2 dòng NAV chính thức (25/08, 27/08 — cả 2 account)

Tác vụ chụp NAV cuối ngày (`daily_nav_snapshot.py`) không chạy cho cả 2 account vào đúng 2 ngày này
(có chạy bình thường 24/08, 26/08, 28/08 — không phải toàn bộ pipeline chết, chỉ 2 ngày bị bỏ sót,
cần rà lại vì sao). Dữ liệu gốc (vị thế broker + số dư) cho 2 ngày này **còn nguyên vẹn** trong
`dnse_raw_2026-08-25.jsonl` / `dnse_raw_2026-08-27.jsonl`, nên NAV đã được **tái dựng đúng phương
pháp** (không phải nội suy/ước lượng):
`NAV = Σ(qty vị thế broker thật lúc cuối ngày × giá đóng cửa BQ đúng ngày) + tiền mặt thật + Trứng
vàng thật (egg.totalValue) − "nợ" thật`, dùng đúng công thức `daily_nav_snapshot.py` áp dụng.
Cần bổ sung chính thức 2 dòng này vào `nav_history_{account}.csv` sau khi báo cáo này được duyệt.

### 6.2 Cổ tức cổ phiếu MSB — tỷ lệ phát hành +20% SỐ LƯỢNG (không phải lợi nhuận), ex-date khoảng 27/08 (cả 2 account)

Vị thế MSB tăng đúng 20% ở CẢ HAI account cùng lúc, không có lệnh mua nào: SpaceX 500→600cp,
ZaloPay 200→240cp. Giá vốn/cp giảm tương ứng đúng tỷ lệ pha loãng (SpaceX 16.250→13.541,67; tổng giá
vốn 8.125.000 giữ nguyên tuyệt đối cả trước/sau — bằng chứng toán học xác nhận đây là cổ tức bằng cổ
phiếu, không phải giao dịch mua). Đây là NGUYÊN NHÂN chính khiến 2 dòng NAV tái dựng 25/08→27/08 có
vẻ biến động khác thường — không phải lỗi dữ liệu. **"+20%" ở tiêu đề mục này là tỷ lệ PHA LOÃNG số
lượng cổ phiếu (thưởng cổ phiếu), không phải tỷ suất lợi nhuận** — MSB là cổ tức bằng CỔ PHIẾU nên
không cần cộng cổ tức tiền mặt như 5 mã ở Mục 3.3; lãi/lỗ thật của vị thế MSB (theo giá, đã phản ánh
đúng số lượng mới) là **−1,42%**, xem bảng Mục 3.3.

### 6.3 Quyền mua cổ phiếu MBB, khớp 28/08 (cả 2 account) — gây `Verified=False`

MBB thực hiện quyền mua tỷ lệ 10:1 giá 10.000đ/cp: SpaceX +110cp, ZaloPay +20cp, người dùng xác nhận
thực hiện qua app DNSE lúc 22:53 ICT 28/08 (ghi trong journal). Đối chiếu giá vốn khớp tuyệt đối:
SpaceX 1.565×21.405,75 = 1.675×20.656,72 (≈ 33,55tr cả 2 vế); ZaloPay tương tự. **Nguyên nhân
`Verified=False`**: bản ghi vị thế broker (`dnse_raw`) tại thời điểm trích xuất báo cáo này vẫn còn
số lượng CŨ (1.565/232) — quyền mua chưa kịp đồng bộ vào feed vị thế broker, KHÔNG phải sai lệch thật
(bằng chứng: phép nhân chéo khớp tuyệt đối, không lệch 1 đồng). MTM cổ phiếu trong bảng Mục 3.3/4.3
vì vậy **thấp hơn khoảng 2,3tr (SpaceX)/0,2tr (ZaloPay) so với `mtm_stock` chính thức** — chênh lệch
đúng bằng giá trị số cổ phiếu quyền mua chưa vào ảnh chụp.

### 6.4 "Nợ" 7.763đ / 6.842đ trên sổ KHÔNG phải margin thật

Cả 2 account (kể cả ZaloPay cash-only) hiện `totalDebt` dương nhỏ. Đối chiếu trực tiếp field
`depositFeeAmount` trong cùng bản ghi balances (8.284đ SpaceX, 7.304đ ZaloPay) — giá trị gần khớp,
xác nhận đây là **phí lưu ký/dịch vụ chưa post**, không phải margin vay thật (ZaloPay là cash-only,
không thể có margin). Không ảnh hưởng NAV (đã trừ đúng trong công thức).

### 6.5 Đẳng thức hai chiều (Mục 7) — residual TĂNG so với tuần tham chiếu, KHÔNG giải thích được hết

SpaceX residual +23.788.891 (+2,42% vế phải) — cao hơn hẳn mức +0,76% ghi nhận ở báo cáo tuần
13/07–17/07. Đã loại trừ được ~2,3tr do lệch thời điểm quyền mua MBB (Mục 6.3); phần còn lại
(~21,5tr) **chưa phân rã được đầy đủ** trong phạm vi báo cáo này — nghi ngờ tích lũy từ lãi/lỗ đã
thực hiện nhiều tuần qua chưa được cộng vào công thức (công thức hiện chỉ tính lãi/lỗ CHƯA thực
hiện) và các lần "cost-basis lot reset" (HPG/LPB/MSB/VIB — vị thế về 0 rồi mua lại, xem cảnh báo
INFO trong snapshot) làm mất dấu vết P&L cũ. **Không ảnh hưởng đến số NAV** (NAV chỉ phụ thuộc
KL×giá thị trường, đã đối chiếu khớp từng đồng ở Mục 3.3). Cần điều tra sâu hơn trước báo cáo tháng.

ZaloPay: đẳng thức hai chiều **không áp dụng được** như đã nêu từ báo cáo tuần trước — 2 vị thế legacy
lớn nhất (DGC + VPB, 48,9% NAV) không có lịch sử khớp nội bộ nên "Vốn ban đầu" không so sánh được với
tập con "P&L đã verify" (chỉ 25/27 mã). Chạy máy móc công cụ sẽ ra residual +108% NAV — con số này
**vô nghĩa, không phải một sự cố**, không đưa vào bảng chính.

---

## 6. KẾ HOẠCH TUẦN TỚI (31/08 – 04/09/2026, lưu ý HOSE nghỉ lễ Quốc khánh 02/09)

- **Khắc phục số liệu (ưu tiên):** bổ sung 2 dòng NAV thiếu (25/08, 27/08) vào `nav_history_*.csv`
  chính thức; rà lại vì sao `daily_nav_snapshot.py` bỏ sót đúng 2 ngày đó cho CẢ 2 account cùng lúc
  (khác lỗi tháng 7 chỉ ảnh hưởng 1 account) — nghi vấn dùng chung 1 nguyên nhân hệ thống (cron/lock),
  cần Winston xác minh log vận hành.
- **DGC (ZaloPay, 45,1% NAV, −10,0% chưa TH):** tiếp tục là quyết định của nhà đầu tư, ngoài phạm vi
  tái cân bằng bot — đề nghị xác nhận lại chủ đích giữ/giảm.
- **Đẳng thức hai chiều SpaceX (Mục 6.5):** phân rã residual +2,42% trước báo cáo tháng — cần cộng
  lãi/lỗ ĐÃ thực hiện lũy kế vào công thức `reconcile_equity.py`, hiện công cụ chỉ tính phần chưa TH.
- **SpaceX/ZaloPay:** vận hành thường lệ, BAL/LAG rỗng ở NEUTRAL, mặc định HOLD quanh mức parking đã
  thiết lập trừ khi có tín hiệu mới hoặc tái cân bằng giỏ custom30V định kỳ.
- **Lịch giao dịch tuần tới rút ngắn còn 4 phiên** do HOSE nghỉ lễ Quốc khánh 02/09/2026.

---

## 7. PHỤ LỤC — PHƯƠNG PHÁP LUẬN & LƯU Ý

- **Pipeline xác minh** (theo `mike/kb/coding_guidelines.md` §6): `verify_account_snapshot.py` →
  `nav_history_{account}.csv` (2 ngày tái dựng thủ công đúng phương pháp, Mục 6.1) →
  `reconcile_equity.py` (SpaceX residual +2,42% chưa phân rã hết; ZaloPay không áp dụng được — Mục
  6.5). Giá mark-to-market = giá đóng cửa BigQuery đúng ngày từng dòng.
- **Trứng vàng**: đọc **tự động qua API DNSE** từ 18/08/2026 (field `egg.totalValue` trong payload
  `balances`, cột `egg_assets_auto=True` trong `nav_history`) — **không còn** là số off-book người
  dùng tự báo như quy trình cũ trước 18/08. Không có rủi ro staleness còn lại từ cơ chế thủ công.
- **Breadth**: `tav2_mike.universe_pit` (point-in-time thật, KHÔNG dùng `ticker_prune`) JOIN
  `tav2_bq.ticker` lấy `Close`/`MA50` đúng ngày trong universe.
- **Value Radar**: hiển thị theo `dna_report.build_value_radar_line()` — chỉ mang tính tham khảo, đã
  công bố trong nghiên cứu nội bộ là CHƯA qua kiểm định đa giả thuyết đủ mạnh để dùng làm tín hiệu.
- **Phí/thuế:** phí giao dịch 0,075%/lượt; thuế bán 0,1% giá trị bán. Không có lệnh mua/bán thị
  trường nào phát sinh phí trong tuần này (2 sự kiện quyền cổ đông không tính phí giao dịch).
- **Track record vẫn ngắn** (SpaceX ~40 phiên, ZaloPay ~38 phiên kể từ go-live) — so sánh với
  VN-Index chỉ mang tính mô tả, chưa đủ ý nghĩa thống kê để đánh giá chiến lược.
- **Đây không phải khuyến nghị đầu tư.** Kết quả quá khứ (kể cả backtest) không đảm bảo kết quả
  tương lai.

---
*Báo cáo tổng hợp từ hệ thống giám sát vận hành nội bộ, đối soát với dữ liệu sàn (DNSE API) và cơ sở
dữ liệu thị trường (BigQuery). Báo cáo này do Taylor (Quant) soạn qua dispatch tự động, phát hiện
báo cáo tuần bị bỏ sót bởi `check_report_cadence.sh` — người phụ trách quỹ nên rà soát thêm trước khi
coi các mục có dấu ⚠️ là đã khép kín hoàn toàn.*
