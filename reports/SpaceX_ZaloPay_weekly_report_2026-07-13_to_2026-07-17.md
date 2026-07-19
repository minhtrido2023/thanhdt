# BÁO CÁO TUẦN — TÀI KHOẢN SPACEX & ZALOPAY
## Kỳ báo cáo: 13/07/2026 – 17/07/2026

**Tài khoản 1:** SpaceX · DNSE, số hiệu 0002023347 · V2.4 live từ 01/07/2026 (có margin)
**Tài khoản 2:** ZaloPay · DNSE, số hiệu 0001743768 · V2.4 live từ 06/07/2026 (cash-only, không margin)
**Chiến lược:** V2.4 (2 book BAL/LAG + parking custom30V tại trạng thái NEUTRAL)
**Ngày lập báo cáo:** 19/07/2026 · **Người lập:** Taylor (Quant) — số liệu đối soát qua pipeline xác minh chuẩn (xem Mục 7)
**Đối tượng:** Báo cáo hiệu suất & vận hành — có thể chia sẻ với nhà đầu tư

---

> **✅ Nguồn số liệu:** toàn bộ NAV/giá vốn/lãi-lỗ chạy qua pipeline xác minh bắt buộc:
> `verify_account_snapshot.py` — **cả 2 account Verified = True, 0 lệch khối lượng** giữa 2 nguồn độc
> lập (log thô API broker vs journal khớp lệnh nội bộ); chuỗi NAV ngày từ `nav_history_{account}.csv`;
> giá mark-to-market = giá đóng cửa 17/07 (BigQuery). Đối chiếu độc lập: giá trị cổ phiếu tính lại từ
> sổ vị thế broker khớp **từng đồng** với chuỗi NAV ở cả 2 account. Con số nào không trace được qua
> pipeline đều được ghi rõ là ước tính/thiếu — không tự suy đoán.

---

## 1. TÓM TẮT ĐIỀU HÀNH (Executive Summary)

| Chỉ tiêu | SpaceX | ZaloPay |
|---|---:|---:|
| NAV đầu kỳ (chốt 10/07) | 971.690.659 | 978.346.744 |
| NAV cuối kỳ (17/07) | **951.448.674** | **949.864.227** |
| Thay đổi trong kỳ | **−20.241.985 (−2,08%)** | **−28.482.517 (−2,91%)** |
| VN-Index cùng kỳ (10/07 → 17/07) | 1.828,34 → 1.787,45 (**−2,24%**) | — |
| Cổ phiếu cuối kỳ (giá đóng cửa 17/07) | 646.180.000 | 779.925.000 |
| Tiền mặt tại công ty CK | 3.160.463 | 22.465.980 |
| **Tiền gửi "Trứng vàng" (off-book)** | **302.108.211** | **147.473.247** |
| Nợ margin cuối kỳ | 0 | 0 (cash-only) |
| Tỷ trọng cổ phiếu/NAV | 67,9% (đúng mục tiêu ~70% NEUTRAL) | 82,1% (gồm DGC excluded 47,2%) |
| Số mã nắm giữ cuối kỳ | 15 | 8 (6 mã bot + VPB legacy + DGC excluded) |

**Nhận định tuần:** thị trường tiếp tục giảm sang tuần thứ hai liên tiếp (VN-Index −2,24%, mất mốc
1.800 và đóng tuần ở 1.787,45). **SpaceX −2,08%, giảm nhẹ hơn chỉ số** nhờ cấu hình phòng thủ NEUTRAL
(~68% cổ phiếu, phần còn lại là tiền). **ZaloPay −2,91%, giảm sâu hơn chỉ số** — nguyên nhân chính là
tỷ trọng cổ phiếu cao hơn nhiều (82,1%) do vị thế DGC 47,2% NAV nằm ngoài phạm vi tái cân bằng của bot;
riêng DGC tuần này giảm 46.200 → 44.800 (−3,0%), đóng góp khoảng −14tr vào mức giảm NAV. Trạng thái
thị trường theo hệ thống DT5G giữ nguyên **NEUTRAL (3/5)** suốt tuần; không có cap phòng thủ vĩ mô nào
kích hoạt. Hai book tín hiệu chủ động (BAL/LAG) vẫn rỗng — phần cổ phiếu là parking custom30V theo
đúng thiết kế.

---

## 2. ⚠️ GIẢI TRÌNH QUAN TRỌNG — KHOẢN TIỀN GỬI "TRỨNG VÀNG" (KHÔNG PHẢI RÚT VỐN, KHÔNG PHẢI LỖ)

Tối **16/07/2026**, nhà đầu tư chủ động chuyển phần tiền mặt nhàn rỗi trong 2 tài khoản sang sản phẩm
**tiền gửi "Trứng vàng" của DNSE** để hưởng lãi suất thay vì để tiền không sinh lời:

| Tài khoản | Số tiền chuyển | Thời điểm | Ảnh hưởng NAV |
|---|---:|---|---|
| SpaceX | 302.108.211 | 19:10 ngày 16/07 | **0 (bằng không)** |
| ZaloPay | 147.473.247 | ghi nhận từ 17/07 | **0 (bằng không)** |

**Vì sao số dư tiền mặt trong báo cáo giảm mạnh nhưng NAV không đổi:** tiền mặt tại công ty chứng
khoán của SpaceX giảm từ 305.388.637 xuống 3.160.463 (đúng bằng 305.388.637 − 302.108.211 = 3.280.426
trước biến động nhỏ trong ngày). Đây **không phải rút vốn khỏi tài khoản và cũng không phải khoản lỗ**
— tiền vẫn thuộc sở hữu nhà đầu tư, chỉ chuyển từ dạng "tiền mặt chờ trong tài khoản chứng khoán" sang
dạng "tiền gửi có lãi", và đang **sinh lãi thay vì nằm không**.

**Cách xử lý trong báo cáo:** sản phẩm Trứng vàng nằm **ngoài phạm vi API của DNSE** (đã kiểm tra cạn
19 nhóm endpoint và bộ SDK chính thức — không có cách đọc tự động). Vì vậy hệ thống đã được bổ sung
một cột riêng `offbook_assets` trong chuỗi NAV (áp dụng từ 17/07, đã qua kiểm định độc lập của bộ phận
phản biện định lượng): **NAV = Cổ phiếu + Tiền mặt − Nợ vay + Tiền gửi off-book**. Kiểm tra đối chiếu:

- SpaceX: 646.180.000 + 3.160.463 − 0 + 302.108.211 = **951.448.674** ✓ khớp từng đồng
- ZaloPay: 779.925.000 + 22.465.980 − 0 + 147.473.247 = **949.864.227** ✓ khớp từng đồng

**Hạn chế cần biết:** vì không có API, số dư Trứng vàng là **số do nhà đầu tư tự báo** (đã đối chiếu
ảnh chụp ứng dụng EntradeX ngày 16/07). Khi nhà đầu tư nạp thêm hoặc rút ra, **phải báo lại để cập
nhật** — nếu không, NAV sẽ bị tính trùng hoặc thiếu. Hệ thống tự cảnh báo khi số này quá 21 ngày chưa
cập nhật. Phần lãi tiền gửi phát sinh cũng chưa được ghi nhận vào NAV (sẽ cộng khi có số dư cập nhật),
tức NAV hiện đang **hơi thận trọng**, không thổi phồng.

---

## 3. BỐI CẢNH THỊ TRƯỜNG TRONG TUẦN

| Ngày | VN-Index | Δ ngày |
|---|---:|---:|
| 10/07 (đầu kỳ) | 1.828,34 | — |
| 13/07 | 1.800,54 | −1,52% |
| 14/07 | 1.806,63 | +0,34% |
| 15/07 | 1.782,12 | −1,36% |
| 16/07 | 1.804,24 | +1,24% |
| 17/07 | 1.787,45 | −0,93% |

- Tuần giảm thứ hai liên tiếp, **−2,24%**; chỉ số mất mốc tâm lý 1.800 ngày 13/07, hồi lại ngày 16/07
  rồi lại đánh mất ngày 17/07. Áp lực giảm tập trung ở nhóm ngân hàng — nhóm chiếm tỷ trọng lớn nhất
  trong danh mục cả 2 tài khoản.
- **Trạng thái thị trường (DT5G): NEUTRAL (3/5) toàn bộ tuần** (xác nhận từ bảng trạng thái sản xuất
  `vnindex_5state_dt5g_live`, cả 5 phiên đều = 3) → mục tiêu phân bổ ~70% cho phần vốn parking. Không
  có cap phòng thủ vĩ mô (lãi suất SBV ổn định, VIX/SPX bình thường, breadth chưa suy yếu tới ngưỡng).
- Đánh giá vĩ mô: mức giảm hiện tại vẫn nằm trong biên độ dao động bình thường của trạng thái NEUTRAL,
  **chưa có tín hiệu nào đòi hỏi hạ tỷ trọng phòng thủ**. Hệ thống được thiết kế để chỉ phản ứng khi
  giá xác nhận (chậm, có chủ đích) chứ không đoán đáy/đỉnh.

---

## 4. TÀI KHOẢN SPACEX

### 4.1 Diễn biến NAV theo ngày (chuỗi đã xác minh, `nav_history_SpaceX.csv`)

| Ngày | NAV (VND) | Δ ngày | VN-Index Δ ngày | Ghi chú |
|---|---:|---:|---:|---|
| 10/07 (đầu kỳ) | 971.690.659 | — | — | |
| 13/07 | 957.955.577 | −1,41% | −1,52% | HOLD |
| 14/07 | 959.332.216 | +0,14% | +0,34% | HOLD |
| 15/07 | 948.270.867 | −1,15% | −1,36% | **Bán HPG, mua LPB** (xem 4.2) |
| 16/07 | 957.558.637 | +0,98% | +1,24% | HOLD · tối: chuyển Trứng vàng 302,1tr |
| 17/07 (cuối kỳ) | 951.448.674 | −0,64% | −0,93% | HOLD · NAV đã gồm off-book |

Cả tuần **−2,08%** vs VN-Index **−2,24%** — nhích hơn chỉ số 0,16 điểm phần trăm. Đáng chú ý: danh mục
**giảm ít hơn chỉ số ở cả 3 phiên giảm** (13/07, 15/07, 17/07) nhưng cũng **tăng ít hơn ở 2 phiên
tăng** — đúng đặc tính của cấu hình phòng thủ giữ ~32% tài sản ngoài cổ phiếu. Track record vẫn quá
ngắn (13 phiên) để coi là bằng chứng thống kê.

### 4.2 Hoạt động giao dịch

**Thứ Tư 15/07 — 2 lệnh, khớp 100%** (nguồn: `exec_SpaceX_2026-07-15_report.md`):

| Lệnh | Mã | KL kế hoạch | KL khớp | Giá tham chiếu | Giá khớp bình quân |
|---|---|---:|---:|---:|---:|
| Bán | HPG | 2.200 | 2.200 (100%) | 22.500 | 22.473 |
| Mua | LPB | 900 | 900 (100%) | 51.500 | 51.467 |

Giá trị kế hoạch 96tr, thực hiện 96tr (100%). Đây là giao dịch tái cân bằng giỏ parking custom30V:
loại HPG (thép) khỏi giỏ mục tiêu, thay bằng LPB (ngân hàng) theo xếp hạng định lượng mới.

**Lãi/lỗ thực hiện:** HPG bán 2.200cp giá bình quân 22.473 so với giá vốn thật đã xác minh 23.500 →
**−2.259.400 (−4,4%)**. Cộng thuế bán 0,1% (49.441đ) và phí bán 0,075% (37.080đ) → tác động ròng
**≈ −2.345.900**. Phí mua LPB ≈ 34.740đ.

**13/07, 14/07, 16/07, 17/07 — HOLD (không lệnh nào):** BAL/LAG rỗng, danh mục parking đã đúng target,
không phát sinh nhu cầu tái cân bằng. Đây là hành vi đúng thiết kế, không phải hệ thống ngừng hoạt động.

### 4.3 Danh mục cuối kỳ (17/07, giá vốn THẬT đã xác minh × giá đóng cửa 17/07)

| Mã | KL | Giá vốn thật | Giá 17/07 | Giá trị TT (VND) | Lãi/lỗ chưa TH | % |
|---|---:|---:|---:|---:|---:|---:|
| VCB | 1.300 | 62.300 | 58.500 | 76.050.000 | −4.940.000 | −6,10% |
| BID | 1.900 | 42.991 | 38.800 | 73.720.000 | −7.963.478 | −9,75% |
| CTG | 2.300 | 34.477 | 32.000 | 73.600.000 | −5.696.607 | −7,18% |
| VHM | 500 | 149.800 | 140.500 | 70.250.000 | −4.650.000 | −6,21% |
| TCB | 2.000 | 33.900 | 31.450 | 62.900.000 | −4.900.000 | −7,23% |
| VPB | 2.300 | 27.914 | 25.850 | 59.455.000 | −4.747.857 | −7,40% |
| MBB | 2.400 | 25.850 | 23.750 | 57.000.000 | −5.040.000 | −8,12% |
| LPB | 900 | 52.583 | 52.900 | 47.610.000 | +285.000 | +0,60% |
| HDB | 1.500 | 26.675 | 27.250 | 40.875.000 | +862.500 | +2,16% |
| ACB | 1.500 | 22.650 | 23.550 | 35.325.000 | +1.350.000 | +3,97% |
| SHB | 1.500 | 13.550 | 12.650 | 18.975.000 | −1.350.000 | −6,64% |
| TPB | 800 | 16.800 | 15.200 | 12.160.000 | −1.280.000 | −9,52% |
| VIX | 700 | 17.000 | 13.750 | 9.625.000 | −2.275.000 | −19,12% |
| VND | 300 | 17.800 | 17.850 | 5.355.000 | +15.000 | +0,28% |
| SHS | 200 | 18.900 | 16.400 | 3.280.000 | −500.000 | −13,23% |
| **Tổng** | | **giá vốn 687.010.443** | | **646.180.000** | **−40.830.443** | **−5,94%** |

**Phân bổ ngành:** Ngân hàng 557,7tr (58,6% NAV) · Bất động sản 70,3tr (7,4%) · Chứng khoán 18,3tr
(1,9%) · Tiền mặt + tiền gửi Trứng vàng 305,3tr (32,1%). **Toàn bộ 15 mã đều dưới trần tập trung
10%/mã** (lớn nhất: VCB 8,0% NAV) — tuân thủ đầy đủ chính sách rủi ro.

**Điểm cần lưu ý:** danh mục đang tập trung rất cao vào **ngành ngân hàng (58,6% NAV, 86% phần cổ
phiếu)**. Đây là kết quả của bộ chọn định lượng custom30V ở giai đoạn hiện tại (nhóm ngân hàng đang
rẻ nhất theo các thước đo giá trị) và **được chấp nhận có chủ đích** — chính sách của quỹ không đặt
trần theo ngành, vì chất lượng doanh nghiệp niêm yết Việt Nam vốn tập trung theo ngành; kiểm soát rủi
ro được thực hiện qua trần 10%/mã và trạng thái thị trường DT5G. Tuy vậy, đây là **nguồn rủi ro tập
trung thật** cần theo dõi: 3 phiên giảm trong tuần đều do nhóm ngân hàng dẫn dắt, và toàn bộ 11 mã
ngân hàng cùng chịu chung yếu tố rủi ro ngành.

---

## 5. TÀI KHOẢN ZALOPAY

### 5.1 Diễn biến NAV theo ngày

| Ngày | NAV (VND) | Δ ngày | Ghi chú |
|---|---:|---:|---|
| 10/07 (đầu kỳ) | 978.346.744 | — | |
| 13/07 | 962.178.035 | −1,65% | **Bán hết VIB, mua BID** (ngày 5/5 chuyển tiếp) |
| 14/07 | 963.865.542* | +0,18% | HOLD — *số tái dựng, xem ghi chú* |
| 15/07 | 950.227.003 | −1,41% | **Bán VPB, mua CTG** |
| 16/07 | 953.593.885 | +0,35% | **Bán VPB, mua CTG** |
| 17/07 (cuối kỳ) | 949.864.227 | −0,39% | **Bán VPB, mua TCB** · NAV đã gồm off-book |

\* **Ghi chú minh bạch — thiếu bản ghi NAV ngày 14/07:** tác vụ chụp NAV cuối ngày không chạy cho
ZaloPay ngày 14/07 (SpaceX vẫn chạy bình thường), nên chuỗi `nav_history_ZaloPay.csv` bị khuyết một
dòng. Số 963.865.542 ở trên được **tái dựng từ đúng nguồn gốc mà tác vụ đó vẫn dùng** — sổ vị thế
broker trong log thô `dnse_raw_2026-07-14.jsonl` (6 mã: DGC 10.000, VPB 7.500, VCB 800, VHM 300,
MBB 1.000, BID 900) nhân giá đóng cửa 14/07 từ BigQuery, cộng số dư tiền mặt thật 160.740.542. Đây
**không phải ước lượng**, mà là tính lại đúng phương pháp trên dữ liệu gốc còn nguyên vẹn. Sự cố này
được ghi nhận ở Mục 6 và dòng thiếu cần được bổ sung chính thức vào file chuỗi NAV.

Cả tuần **−2,91%** vs VN-Index **−2,24%** — kém chỉ số 0,67 điểm phần trăm, do tỷ trọng cổ phiếu cao
(82,1%) và DGC (47,2% NAV, ngoài phạm vi bot) giảm −3,0% trong tuần.

### 5.2 Hoạt động giao dịch — hoàn tất chuyển tiếp & khởi động giảm tập trung VPB

Tất cả 8 lệnh trong tuần đều **khớp 100%** (nguồn: execution report chính thức từng ngày):

| Ngày | Lệnh | Mã | KL | Giá tham chiếu | Giá khớp BQ | Giá trị (VND) |
|---|---|---|---:|---:|---:|---:|
| 13/07 | Bán | VIB | 9.200 | 15.950 | 15.830 | 145.635.000 |
| 13/07 | Mua | BID | 900 | 41.000 | 40.767 | 36.690.300 |
| 15/07 | Bán | VPB | 800 | 26.500 | 26.238 | 20.990.400 |
| 15/07 | Mua | CTG | 850 | 32.600 | 32.685 | 27.782.250 |
| 16/07 | Bán | VPB | 800 | 25.800 | 25.738 | 20.590.400 |
| 16/07 | Mua | CTG | 200 | 32.150 | 32.150 | 6.430.000 |
| 17/07 | Bán | VPB | 800 | 26.000 | 25.869 | 20.695.200 |
| 17/07 | Mua | TCB | 600 | 31.900 | 31.850 | 19.110.000 |

**Hai việc quan trọng đã hoàn tất/khởi động trong tuần:**

1. **Kết thúc kế hoạch chuyển tiếp 5 ngày (07/07 → 13/07):** lệnh cuối là bán hết VIB 9.200cp và mua
   BID 900cp (bù lệnh không khớp ngày 10/07). Từ 13/07 ZaloPay vận hành thường lệ như SpaceX.
2. **Bắt đầu xử lý tập trung VPB — vấn đề đã nêu ở báo cáo tuần trước:** VPB là vị thế legacy chiếm
   **38,8% active NAV**, vượt xa trần chính sách 10%/mã. Bot bắt đầu giảm dần **800cp/phiên** từ
   15/07, đưa vị thế từ 7.500cp xuống **5.100cp** cuối tuần. Tỷ trọng VPB/active NAV giảm từ 38,8%
   xuống **26,3%** — tiến triển thật nhưng **vẫn còn vượt trần**, việc giảm dần sẽ tiếp tục sang
   tuần tới.

**Lãi/lỗ thực hiện trong tuần** (giá vốn legacy = số broker DNSE báo, xem Mục 7):

| Mã | KL bán | Giá vốn broker | Giá bán BQ | Lãi/lỗ thực hiện |
|---|---:|---:|---:|---:|
| VIB | 9.200 | 15.251 | 15.830 | **+5.325.000 (+3,8%)** |
| VPB | 2.400 (3×800) | 27.887 | 25.948 (bq) | **−4.652.000 (−7,0%)** |
| | | | **Tổng** | **+673.000** |

Trừ thuế bán 0,1% (207.911đ) và phí bán 0,075% (155.933đ) → **lãi thực hiện ròng ≈ +309.000đ**. Phí
mua trong tuần ≈ 67.509đ.

### 5.3 Danh mục cuối kỳ (17/07, giá đóng cửa 17/07)

| Mã | KL | Giá trị TT (VND) | % tổng NAV | % active NAV | Ghi chú |
|---|---:|---:|---:|---:|---|
| DGC | 10.000 | 448.000.000 | 47,2% | — | **Excluded** — ngoài phạm vi bot |
| VPB | 5.100 | 131.835.000 | 13,9% | **26,3%** | Legacy — đang giảm dần 800cp/phiên |
| VCB | 800 | 46.800.000 | 4,9% | 9,3% | Bot |
| VHM | 300 | 42.150.000 | 4,4% | 8,4% | Bot |
| BID | 900 | 34.920.000 | 3,7% | 7,0% | Bot |
| CTG | 1.050 | 33.600.000 | 3,5% | 6,7% | Bot |
| MBB | 1.000 | 23.750.000 | 2,5% | 4,7% | Bot |
| TCB | 600 | 18.870.000 | 2,0% | 3,8% | Bot |
| Tiền mặt | | 22.465.980 | 2,4% | | |
| Tiền gửi Trứng vàng | | 147.473.247 | 15,5% | | Off-book |
| **Tổng NAV** | | **949.864.227** | 100% | | Active NAV (loại DGC): **501.864.227** |

Cộng dồn kiểm tra: 779.925.000 + 22.465.980 + 147.473.247 = **949.864.227** ✓ khớp từng đồng với chuỗi
NAV đã xác minh.

**Lãi/lỗ chưa thực hiện phần bot mua** (6 mã, giá vốn thật đã xác minh): cost 208.392.500 → thị giá
200.090.000 = **−8.302.500 (−3,98%)**. Lãi/lỗ của DGC và VPB không đưa vào con số này (vị thế legacy,
không có lịch sử khớp nội bộ — xem Mục 7).

---

## 6. CÔNG BỐ SỰ CỐ VẬN HÀNH TRONG TUẦN

Nguyên tắc: chỉ liệt kê sự cố ảnh hưởng thật đến NAV/giao dịch/số liệu công bố.

**Tin tốt: tuần này KHÔNG có sự cố nào chạm đến tiền thật hoặc làm sai lệch giao dịch.** Toàn bộ 10
lệnh (2 SpaceX + 8 ZaloPay) đều khớp 100% đúng kế hoạch đã duyệt; không có lệnh sai, lệnh trùng, hay
lệnh bị bỏ sót. Hai lớp bảo vệ mới có hiệu lực từ 14/07 (gửi lại duyệt tự động 23:00 + chốt chặn
"plan chưa duyệt thì bot từ chối chạy") hoạt động đúng, không chặn nhầm phiên nào.

Ba vấn đề **về chất lượng số liệu báo cáo** (không chạm tiền) được phát hiện trong quá trình lập báo
cáo này và cần khắc phục:

1. **Thiếu bản ghi NAV ngày 14/07 của ZaloPay** (SpaceX không bị) — tác vụ chụp NAV cuối ngày không
   chạy cho tài khoản này. Dữ liệu gốc còn nguyên vẹn nên số đã được tái dựng đúng phương pháp (Mục
   5.1), nhưng **chuỗi NAV chính thức vẫn đang khuyết một dòng** và cần bổ sung. Cần rà lại vì sao
   tác vụ bỏ sót đúng 1 trong 2 tài khoản.
2. **Lỗi công cụ đối soát khi có nhiều tài khoản (`reconcile_equity.py`):** công cụ đọc số dư tiền
   mặt từ file log dùng chung nhưng **không lọc theo tài khoản** — nó lấy bản ghi cuối cùng trong
   file, nên khi đối soát ZaloPay lại lấy nhầm tiền mặt của SpaceX (3.160.463 thay vì 22.465.980).
   Đây đúng là loại lỗi đã từng gây sự cố NAV nhiễm chéo ngày 06/07: khi đó đã sửa ở công cụ chụp NAV
   hằng ngày nhưng **chưa sửa ở công cụ đối soát này**. Số trong báo cáo này **không dùng đầu ra sai
   đó** — phần đối soát ZaloPay đã tính lại thủ công từ bản ghi số dư đúng tài khoản. Cần vá công cụ
   trước kỳ báo cáo sau.
3. **Công cụ xác minh giá vốn mặc định KHÔNG lọc theo tài khoản** (`verify_account_snapshot.py`): nếu
   người chạy quên truyền tham số `--account-no`, công cụ trộn lệnh khớp của cả 2 tài khoản và cho ra
   kết quả sai (lần chạy đầu của báo cáo này đã bị đúng như vậy — báo VPB/CTG của SpaceX sai số lượng).
   **Cơ chế fail-safe đã hoạt động đúng như thiết kế**: công cụ tự phát hiện lệch giữa 2 nguồn độc lập
   và in cảnh báo "❌ KHÔNG dùng số liệu này để viết báo cáo", nên sai sót bị chặn lại ngay chứ không
   lọt vào báo cáo. Số cuối cùng dùng trong báo cáo này đã chạy lại đúng tham số và đối chiếu khớp với
   sổ vị thế broker. Đề xuất: bắt buộc tham số này thay vì để mặc định không lọc.

---

## 7. ĐỐI SOÁT ĐẲNG THỨC HAI CHIỀU

**SpaceX** (`reconcile_equity.py`, vốn ban đầu 1.000.000.000, ngày 17/07):

| Vế trái (Vốn + Lãi/lỗ − Phí) | VND | | Vế phải (Tài sản − Nợ) | VND |
|---|---:|---|---|---:|
| Vốn ban đầu | 1.000.000.000 | | Cổ phiếu (MTM) | 646.180.000 |
| + Lãi/lỗ chưa thực hiện | −40.830.443 | | + Tiền mặt | 3.160.463 |
| − Phí giao dịch (0,075%) | −515.258 | | − Nợ margin | 0 |
| − Phí/lãi đã post (API thật) | −3.468 | | + Tiền gửi off-book | 302.108.211 |
| **= Vế trái** | **958.650.832** | | **= Vế phải** | **951.448.674** |

**Chênh lệch +7.202.158 (+0,76% NAV) — vượt ngưỡng dung sai, chưa khép kín hoàn toàn.** Phân rã các
thành phần đã nhận diện được:

- **Lãi/lỗ đã thực hiện chưa được đưa vào công thức (~−1,8tr):** công cụ hiện chỉ hạch toán lãi/lỗ
  *chưa* thực hiện. Tính từ sổ vị thế broker, lãi/lỗ đã thực hiện lũy kế (đợt trim 06/07 + bán HPG
  15/07) ≈ −774.000, cộng thuế/phí bán ≈ −1.047.000 → tổng ≈ −1,82tr.
- **Khác biệt quy ước giá vốn (~3,3tr):** giá vốn "thật" của hệ thống tính bình quân từ các lệnh khớp
  của bot, còn broker dùng bình quân động có điều chỉnh sau mỗi lần bán một phần. Chênh rõ nhất ở MBB
  (25.850 vs 24.850 → 2,4tr) và BID (42.991 vs 42.541 → 0,86tr). Đây là khác biệt **định nghĩa**, không
  phải mất mát tài sản.
- **Lãi vay margin phát sinh chưa post (~1tr ước tính):** dư nợ 409,86tr tồn tại 02/07–09/07, lãi suất
  ~12,5%/năm (số nhà đầu tư cung cấp, **chưa xác minh với DNSE**) → ≈ 982.000đ. Số phí đã post trên API
  hiện mới 3.468đ, cho thấy lãi được ghi nhận theo chu kỳ chứ không hằng ngày.
- **Phần còn lại (~1tr) chưa giải thích được** — ghi nhận thẳng thắn là còn thiếu, sẽ đối soát với sao
  kê chính thức DNSE trong báo cáo tháng.

**Điều này KHÔNG ảnh hưởng đến con số NAV.** NAV chỉ phụ thuộc khối lượng cổ phiếu × giá thị trường,
cộng tiền mặt, trừ nợ — cả 3 đều đọc trực tiếp từ broker và đã đối chiếu khớp từng đồng. Chênh lệch
trên nằm ở bài toán *quy kết lãi/lỗ*, không phải ở *giá trị tài sản*.

**ZaloPay: đẳng thức hai chiều chưa lập được** — 2 vị thế legacy lớn nhất (DGC 448tr và VPB 131,8tr,
tổng 61% NAV) hình thành trước khi bot quản lý, không có lịch sử khớp nội bộ nên không có giá vốn đã
xác minh để đưa vào vế trái. Đây là hạn chế đã biết (nêu từ báo cáo tuần trước), **không thay bằng số
ước lượng**. Vế phải vẫn được xác minh đầy đủ (Mục 5.3 khớp từng đồng). Cần bổ sung khả năng hạch toán
giá vốn vị thế legacy trước khi có thể so sánh *tỷ suất sinh lời* của ZaloPay với SpaceX.

---

## 8. KẾ HOẠCH TUẦN TỚI (20/07 – 24/07/2026)

- **ZaloPay — tiếp tục giảm tập trung VPB:** duy trì nhịp bán ~800cp/phiên cho tới khi VPB về dưới
  trần 10% active NAV (từ 5.100cp hiện tại, dự kiến còn ~4–5 phiên nữa nếu điều kiện thanh khoản cho
  phép); tiền thu về giải ngân vào giỏ custom30V.
- **SpaceX:** vận hành thường lệ. BAL/LAG vẫn rỗng ở NEUTRAL nên mặc định HOLD quanh mức parking ~68–70%,
  trừ khi có tín hiệu mới hoặc tái cân bằng giỏ định kỳ.
- **Cần quyết định của nhà đầu tư — tiền gửi Trứng vàng:** hiện 449,6tr (cả 2 tài khoản) đang nằm ở
  tiền gửi. Nếu hệ thống phát tín hiệu mua mới, phần tiền này **không tự động khả dụng** — cần nhà đầu
  tư rút về tài khoản chứng khoán trước. Đề nghị nhà đầu tư báo lại mỗi lần nạp/rút để cập nhật NAV.
- **Việc cần khắc phục về số liệu (Mục 6):** bổ sung dòng NAV 14/07 của ZaloPay; vá lỗi lọc tài khoản
  ở công cụ đối soát; bắt buộc tham số tài khoản ở công cụ xác minh giá vốn. Cả 3 đều thuộc nhóm chất
  lượng báo cáo, không chạm logic đặt lệnh.
- **Các chương trình paper-trading đang chạy** (không bật gì ở live khi chưa có sign-off): EXTREME-regime
  gate (dự kiến kết thúc ~28/07) · chase-cap vol-scale (đã quá mốc ~14/07, **cần review**) · fill-timing
  khung giờ (review ~cuối tháng 7) · DC-book idle-cash waterfall (review theo sự kiện, kèm 4 hạng mục
  sửa đã lên danh sách).
- **Mùa báo cáo tài chính Q2/2026 bắt đầu ~cuối tháng 7** — book LAG (đón sóng sau công bố lợi nhuận)
  có thể phát tín hiệu trở lại sau nhiều tuần rỗng; công tác rà soát sẵn sàng dữ liệu đã hoàn tất.

**Lịch vận hành tiêu chuẩn không đổi** (T2–T6): kiểm tra dữ liệu (17:30) → lập kế hoạch T+1 (19:30,
thêm vòng gửi duyệt lại 23:00) → kiểm tra sẵn sàng (08:20 & 08:45) → phiên sáng (09:05) → kiểm tra giữa
phiên (12:45) → phiên chiều (13:00) → báo cáo cuối ngày (15:00), giám sát tự động mỗi 5 phút trong giờ
giao dịch.

---

## 9. PHỤ LỤC — PHƯƠNG PHÁP LUẬN & LƯU Ý

- **Pipeline xác minh bắt buộc** (không đổi):
  1. `verify_account_snapshot.py` — giá vốn/khối lượng thật từ log gốc API broker (`dnse_raw_*.jsonl`,
     field `averagePrice`/`fillQuantity` do DNSE trả về), cross-check độc lập với journal khớp lệnh nội
     bộ. Tuần này: **SpaceX Verified = True** (15 mã, ngày khớp 01–02/07, 06/07, 15/07) và **ZaloPay
     Verified = True** (6 mã bot, ngày khớp 07–17/07), **0 lệch khối lượng** ở cả 2.
  2. `daily_nav_snapshot.py` → `nav_history_{account}.csv` — chuỗi NAV ngày từ số dư/vị thế API thật
     (thiếu 1 dòng ZaloPay 14/07, đã tái dựng và ghi rõ — Mục 5.1 & 6.1).
  3. `reconcile_equity.py` — đẳng thức hai chiều (Mục 7); SpaceX chưa khép kín (+0,76%), ZaloPay chưa
     lập được. Cả hai đều được công bố nguyên trạng thay vì làm tròn cho đẹp.
  - **Đối chiếu độc lập bổ sung:** giá trị cổ phiếu tính lại từ sổ vị thế broker ngày 17/07 khớp **từng
    đồng** với `mtm_stock` trong chuỗi NAV ở cả 2 account (SpaceX 646.180.000; ZaloPay 779.925.000).
- **Giá mark-to-market** = giá đóng cửa 17/07 từ BigQuery. Riêng số liệu cùng ngày (định giá lệnh, sức
  mua) luôn lấy từ API DNSE trực tiếp, không lấy từ BigQuery (dữ liệu BQ chỉ đồng bộ qua đêm).
- **Giá vốn vị thế legacy ZaloPay** (DGC/VPB, và VIB đã bán): hệ thống không có lịch sử khớp nội bộ nên
  dùng **giá vốn do broker DNSE báo** (`costPrice`) — nguồn broker-native nhưng là số broker tự tính,
  chưa đối soát được với chứng từ gốc của các giao dịch cũ. Lãi/lỗ chưa thực hiện của DGC/VPB vì vậy
  không đưa vào P&L hợp nhất; **NAV không bị ảnh hưởng** (chỉ phụ thuộc khối lượng × giá thị trường).
- **Tiền gửi "Trứng vàng"**: số do nhà đầu tư tự báo (đối chiếu ảnh chụp ứng dụng EntradeX 16/07, khớp
  4/5 trường số dư còn lại từng đồng qua API). **Không có API để tự động cập nhật.** Lãi tiền gửi phát
  sinh chưa ghi nhận vào NAV.
- **Phí/thuế:** phí giao dịch 0,075%/lượt (đã xác nhận với biểu phí tài khoản); thuế bán 0,1% giá trị
  bán theo quy định. Lãi margin ~12,5%/năm là **số nhà đầu tư cung cấp, chưa xác minh với DNSE**. Các
  con số phí/thuế/lãi trong báo cáo là **ước tính từ biểu phí**, chưa đối soát sao kê chính thức — sẽ
  đối soát trong báo cáo tháng.
- **Track record vẫn rất ngắn** (SpaceX 13 phiên, ZaloPay 9 phiên): mọi so sánh với VN-Index chỉ mang
  tính mô tả, **chưa đủ ý nghĩa thống kê** để đánh giá chiến lược. Việc danh mục giảm ít/nhiều hơn chỉ
  số trong 1 tuần không nói lên điều gì về chất lượng hệ thống.
- **Đây không phải khuyến nghị đầu tư.** Kết quả quá khứ (kể cả backtest) không đảm bảo kết quả tương lai.

---
*Báo cáo tổng hợp từ hệ thống giám sát vận hành nội bộ, đối soát với dữ liệu sàn (DNSE API) và cơ sở
dữ liệu thị trường (BigQuery). Người phụ trách quỹ rà soát trước khi phát hành cho nhà đầu tư.*
