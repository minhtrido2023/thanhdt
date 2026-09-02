# BÁO CÁO THÁNG — TÀI KHOẢN SPACEX & ZALOPAY
## Kỳ báo cáo: THÁNG 08/2026 (01/08 – 31/08/2026)
### *Tháng thứ hai vận hành — Signal HOLD toàn bộ từ 21/08 do VPI, capit_margin_lever LIVE từ 24/08*

**Tài khoản 1:** SpaceX · DNSE, số hiệu 0002023347 · V2.4 live (có margin) · vốn cơ sở theo R3 pin
**Tài khoản 2:** ZaloPay · DNSE, số hiệu 0001743768 · V2.4 live (cash-only) · DGC excluded
**Chiến lược:** V2.4 — BAL momentum + LAG hậu-công-bố-lợi-nhuận, parking custom30V NEUTRAL, rổ CAPIT khi bear-washout
**Ngày lập báo cáo:** 01/09/2026 · **Người lập:** Taylor (Quant, §2-3-6-8-11) · Mike (§1-7-9-10) · Bobby (§5) · Spyros (§4)
**Đối tượng:** Báo cáo hiệu suất & vận hành tháng — chuẩn mực quản lý tài sản

---

> **Ghi chú phiên bản:** Template này tạo ngày 25/08/2026 với §5 (Vĩ mô) đã điền đầy đủ bởi Bobby.
> Các mục hiệu suất (§1-4, §6-11) điền ngay sau khi đóng tháng (01/09/2026).

---

## MỤC LỤC — PHÂN CÔNG THEO PHẦN

| # | Mục | Người phụ trách | Nguồn dữ liệu |
|---|---|---|---|
| 1 | Tóm tắt điều hành | **Mike** | Tổng hợp toàn bộ |
| 2 | Hiệu suất MTD/QTD/YTD vs chỉ số | **Taylor** | nav_history + BQ + DNSE API |
| 3 | Phân rã nguồn lãi/lỗ (attribution) | **Taylor** | verify_account_snapshot.py + dividend_adjusted_return.py |
| 4 | Chỉ số rủi ro | **Spyros** (risk-auditor) | nav_history + positions |
| **5** | **Diễn biến vĩ mô tháng 8 & đánh giá rủi ro khủng hoảng** | **Bobby** (macro-strategist) | GSO/TCTK + SBV + Fed + nguồn công khai |
| 6 | Phí & chi phí | **Taylor** | execution logs + DNSE API |
| 7 | Nhật ký sự kiện tháng | **Mike** | bus events + KB |
| 8 | Danh mục cuối tháng | **Taylor** | positions DNSE 31/08 |
| 9 | Công bố sự cố & khoảng trống số liệu | **Mike** | bus incidents + kb/incidents/ |
| 10 | Triển vọng & việc cần làm | **Mike + DollarBill** | current_ops + plan pipeline |
| 11 | Phụ lục phương pháp | **Taylor** | pipeline spec + coding_guidelines |

---

## 1. TÓM TẮT ĐIỀU HÀNH
> **Người phụ trách: Mike** · Hoàn thành 02/09/2026

**Phiên chốt tháng: 28/08/2026, KHÔNG PHẢI 31/08.** HOSE nghỉ lễ Quốc khánh 31/08 → 02/09/2026
(31/08-01/09 cuối tuần, 02/09 nghỉ lễ chính thức); phiên giao dịch cuối cùng của tháng 8 là
**Thứ Sáu 28/08**. Mọi số liệu thị trường (giá, MTM, VNINDEX) dưới đây chốt tại 28/08; số dư tiền/
tài sản off-book (Trứng vàng) dùng bản đọc mới nhất 31/08 (không đổi so với 28/08 vì không có
giao dịch trong kỳ nghỉ).

| Chỉ tiêu | SpaceX | ZaloPay |
|---|---:|---:|
| NAV đầu kỳ (31/07, = NAV cuối T7) | 938.435.711đ | 888.828.498đ |
| NAV cuối tháng (28-31/08) | 985.617.905đ | 952.365.940đ |
| Lãi/lỗ trong kỳ (VND) | **+47.182.194đ** | **+63.537.442đ** |
| Tỷ suất MTD | **+5,03%** | **+7,15%** |
| VN-Index cùng khung (1.735,78→1.832,12) | +5,55% | +5,55% |
| Chênh so với chỉ số | −0,52pp | **+1,60pp** |
| Biến động năm hoá (annualized, mẫu ~16 ngày) | 12,37% | 25,58% |
| Sụt giảm tối đa trong tháng | −1,67% | −3,59% |
| Số lệnh khớp thật (event=FILL, không tính PLACE/CANCEL) | 80 | 42 |
| Tổng phí + thuế ước tính (0,075%/lượt + 0,1% thuế bán) | ~767.504đ | ~385.515đ |

**Cách tính lãi/lỗ & tỷ suất:** dùng trực tiếp **hiệu NAV đầu kỳ − cuối kỳ** từ snapshot NAV
broker-native (`nav_history_{account}.csv` = MTM cổ phiếu + tiền mặt − nợ margin + tài sản
off-book "egg", đọc thẳng từ `dnse_raw_*.jsonl`) — **KHÔNG** qua phân rã LHS (vốn+lãi/lỗ chưa
thực hiện−phí) vì `reconcile_equity.py` cho residual +23,7tr (+2,41% NAV, SpaceX) VƯỢT ngưỡng
dung sai: nguồn gốc residual đã xác định là **lãi/lỗ ĐÃ THỰC HIỆN từ các lượt bán/mua-lại trong
tháng** (HPG/LPB/MSB/VIB "về 0 rồi mua lại" — xem cảnh báo INFO trong `verify_account_snapshot.py`)
**chưa được cộng vào vế trái** của đẳng thức reconcile — công cụ này hiện chỉ tính lãi/lỗ CHƯA
THỰC HIỆN trên vị thế đang giữ. Hiệu NAV đầu-cuối không phụ thuộc cách phân rã này (chỉ cần 2 đầu
mút đúng), nên đây là con số MTD đáng tin cậy nhất hiện có; phân rã lãi/lỗ realized-vs-unrealized
đầy đủ ghi nhận là khoảng trống trong §11.2/§9.

**Số lệnh khớp** đếm dòng `event=FILL` thật trong `exec_{account}_2026-08-*_journal.csv`
(KHÔNG đếm `PLACE`/`CANCEL_STALE`/`WAIT_QUOTA` — SpaceX có 121 `PLACE` nhưng chỉ 80 `FILL` thật do
lệnh bị sửa/huỷ/đặt lại nhiều lần trong phiên trước khi khớp).

---

## 2. HIỆU SUẤT MTD / QTD / YTD SO VỚI CHỈ SỐ
> **Người phụ trách: Taylor** · Nguồn: nav_history_{SpaceX,ZaloPay}.csv + BQ ticker (VNINDEX, asof 28/08)

### 2.1 MTD tháng 8 (đã trình bày ở §1) và diễn biến theo tuần

| Tuần | SpaceX NAV | ZaloPay NAV | VNINDEX |
|---|---:|---:|---:|
| Đầu kỳ (31/07) | 938.435.711 | 888.828.498 | 1.735,78 |
| Tuần 1 (→07/08) | 961.311.265 (+2,44%) | 912.854.495 (+2,71%, snapshot gần nhất 05/08 — thiếu 06,07/08) | 1.768,06 (+1,86%) |
| Tuần 2 (→14/08) | 958.940.908 (+2,19%) | 939.887.091 (+5,74%) | 1.729,08 (−0,39%) |
| Tuần 3 (→21/08) | 977.129.844 (+4,13%) | 948.266.511 (+6,69%) | 1.768,12 (+1,86%) |
| Tuần 4 (→28/08) | 985.547.490 (+5,02%) | 952.338.703 (+7,14%) | 1.832,12 (+5,55%) |

*(% trong ngoặc = tích luỹ từ 31/07. Tuần 1 ZaloPay thiếu snapshot 07/08 — file `nav_history_ZaloPay.csv`
không có dòng cho ngày này, xem khoảng trống dữ liệu ở §9.)*

### 2.2 QTD (Q3/2026, từ 01/07)

Q3 chưa đóng (còn tháng 9) nên đây là QTD-so-far, gộp tháng 7+8:
- **SpaceX**: vốn khởi điểm quy ước 1.000.000.000đ (xác nhận qua `verify_account_snapshot.py`
  `starting_capital` field, go-live 01/07) → NAV 28/08 = 985.547.490đ ⇒ **QTD = −1,45%**
  (tháng 7 −6,16%, tháng 8 +5,03% — chưa bù hết mức lỗ tháng 7).
- **ZaloPay**: NAV go-live (07/07, bản ghi đầu tiên) = 986.585.454đ → NAV 28/08 = 952.338.703đ
  ⇒ **QTD (từ bản ghi đầu) = −3,47%** (tháng 7 −9,93%*, tháng 8 +7,14%). *Vốn khởi điểm chính xác
  01/07-06/07 (trước go-live 06/07) chưa re-verify độc lập lần này — dùng bản ghi NAV đầu tiên
  07/07 làm mốc, có thể không trùng khớp tuyệt đối vốn nạp ban đầu; đánh dấu GIẢ ĐỊNH.

### 2.3 YTD (từ ngày go-live, KHÔNG phải từ 01/01 — quy ước §2 gốc)

Trùng với QTD ở trên vì cả 2 tài khoản go-live trong Q3/2026 (chưa có lịch sử trước quý này).

**Diễn giải:** cả 2 tài khoản đang PHỤC HỒI từ mức lỗ tháng 7 (ghi nhận trong report tháng 7),
tháng 8 là tháng dương đầu tiên kể từ go-live. ZaloPay outperform VNINDEX +1,60pp MTD tháng 8 nhờ
tỷ trọng cao hơn ở PVT/SCL/CSV (nhóm dầu khí/vật liệu tăng mạnh); SpaceX underperform nhẹ −0,52pp
do tỷ trọng NCT/BID/CTG lớn hơn (nhóm chịu áp lực điều chỉnh cuối tháng).

Dùng `dividend_adjusted_return.py`/`report_return_gate.py::entitled_gross()` cho tỷ suất
per-position — xem §3.

---

## 3. PHÂN RÃ NGUỒN LÃI/LỖ (ATTRIBUTION)
> **Người phụ trách: Taylor** · Bắt buộc dùng `bin/dividend_adjusted_return.py` (§21 coding_guidelines)

### 3.1 SpaceX — phân rã theo cấu phần kế toán

| Cấu phần | VND | Ghi chú |
|---|---:|---|
| Lãi/lỗ CHƯA thực hiện (vị thế cuối kỳ, cộng cổ tức ròng −5% thuế) | +17.858.362đ | `report_return_gate.py::entitled_gross()`, 27/27 mã, tổng khớp `pl_net_total` |
| Phần còn lại (lãi/lỗ ĐÃ thực hiện từ bán/mua-lại trong tháng + phí, chưa phân rã chi tiết) | ≈ +29.323.832đ | = Lãi/lỗ NAV kỳ (§1, +47.182.194đ) − dòng trên. Gồm cả các lượt HPG/LPB/MSB/VIB "về 0 rồi mua lại" (§9.1) — CHƯA có công cụ tách riêng realized-vs-fee, xem việc cần làm §10.3#5 |
| **Tổng (= Lãi/lỗ NAV kỳ §1)** | **+47.182.194đ** | |

### 3.2 SpaceX — phân rã theo nhóm ngành (ICB, đã cộng cổ tức ròng sau thuế 5%)

| Nhóm | Mã | Tổng lãi/lỗ (VND) | % tỷ trọng cost |
|---|---|---:|---:|
| Dầu khí/Vật liệu | PVT, SCL, SIP, HPG, VND | +20.450.000đ | 23,9% |
| Ngân hàng | MBB, ACB, SHB, TCB, VCB, LPB, CTG, BID, TPB, VPB, HDB | −7.448.637đ | 36,3% |
| Bất động sản/Xây dựng | VHM, VRE, NCT | −3.125.000đ | 14,1% |
| Tiêu dùng/CK/Khác | DRI, VNM, SAB, TV1, VIB, EVF, MSB, VIX | +7.982.000đ | 25,7% |

*(% tỷ trọng theo `raw_cost` §3.1; tổng 4 nhóm khớp `pl_net_total` §3.1 tới 1đ.)*

### 3.3 SpaceX — 5 vị thế tốt nhất & 5 tệ nhất (đã cộng cổ tức, dividend-adjusted)

**Tốt nhất:**
| Mã | qty | % lãi | VND |
|---|---:|---:|---:|
| PVT | 3.500 | +18,13% | +10.850.000đ |
| SCL | 1.500 | +16,95% | +6.000.000đ |
| DRI | 3.700 | +6,32% | +3.100.000đ |
| VNM | 900 | +6,31% | +3.330.000đ |
| SIP | 1.700 | +5,08% | +4.065.000đ |

**Tệ nhất:**
| Mã | qty | % lỗ | VND |
|---|---:|---:|---:|
| TPB | 500 | −12,80% | −1.075.000đ |
| VIX | 420 | −8,82% | −573.000đ |
| BID | 1.175 | −6,88% | −3.197.554đ |
| VND | 300 | −6,46% | −345.000đ |
| CTG | 1.200 | −5,48% (đã cộng cổ tức 450đ/cp) | −2.253.786đ |

### 3.4 ZaloPay — phân rã theo nguồn

| Nguồn | VND | Ghi chú |
|---|---:|---|
| Lãi/lỗ CHƯA thực hiện, 27 mã ĐANG bot quản lý (loại DGC) | +17.779.415đ | = pl_net_total toàn bộ (−29.970.585đ) trừ dòng DGC (−47.750.000đ) |
| **DGC — vị thế legacy EXCLUDED, không do bot quản lý** | **−47.750.000đ** | qty=10.000, cost=47.775đ/cp, mkt=43.000đ/cp (28/08). HOSE hạn chế giao dịch + vụ án hình sự liên quan (xem kb, quyết định exclude trước go-live) — bot KHÔNG được phép bán/mua thêm; lỗ này KHÔNG phản ánh chất lượng chiến lược V2.4 |
| Phần còn lại (realized + phí, chưa phân rã chi tiết) | ≈ +45.758.027đ | = Lãi/lỗ NAV kỳ (§1, +63.537.442đ) − 2 dòng trên |
| **Tổng (= Lãi/lỗ NAV kỳ §1)** | **+63.537.442đ** | |

**Active_nav (loại DGC)**: MTD %(active) không tính riêng lần này (đòi hỏi tách NAV daily loại DGC
theo từng ngày, ngoài phạm vi dữ liệu hiện có) — nhưng hướng tác động RÕ: DGC kéo NAV toàn phần
XUỐNG, nghĩa là MTD +7,15% đã báo cáo ở §1 là **CẬN DƯỚI** hiệu suất phần bot chủ động quản lý.

### 3.5 ZaloPay — lãi/lỗ chưa thực hiện phần bot (đã xác minh, 27 mã loại DGC)

**Tốt nhất:** PVT +17,11% (+6.112.950đ) · SCL +17,00% (+4.010.000đ) · CSV +9,11% (+1.800.000đ)
· HDB +7,37% (+876.209đ) · DRI +6,31% (+1.590.000đ)

**Tệ nhất:** LPB −8,92% (−1.722.400đ) · NCT −3,39% (đã cộng cổ tức 8.000đ/cp, −1.193.600đ)
· BID −1,96% (−315.050đ) · VHM −1,77% (−395.000đ) · MSB −1,42% (−46.000đ)

VPB (legacy position, xem §9.3) nằm trong nhóm tốt +3,95% (+1.371.981đ) — dùng `costPrice`
broker-native trực tiếp vì không tái tạo được cost basis qua journal (chỉ 1 nguồn, không
cross-check 2 nguồn độc lập được như các mã khác).

---

## 4. CHỈ SỐ RỦI RO
> **Người phụ trách: Spyros** (risk-auditor) · Nguồn: nav_history ngày, positions DNSE
> ⚠️ Số liệu dưới đây do **Taylor** tính tạm thời (deadline giao báo cáo gấp, Spyros dispatch riêng
> chưa hoàn tất tính đến 02/09) — cùng phương pháp risk-auditor thường dùng nhưng CHƯA qua audit
> độc lập của Spyros. Cần Spyros xác nhận lại trước khi coi là số chính thức.

| Chỉ số | SpaceX | ZaloPay | VN-Index |
|---|---:|---:|---:|
| Độ lệch chuẩn lợi suất ngày (mẫu có gap) | 0,779% | 1,611% | 0,997% |
| Biến động năm hoá (×√252) | 12,37% | 25,58% | 15,83% |
| Sụt giảm tối đa trong tháng | −1,67% | −3,59% | −3,71% |
| Tỷ trọng cổ phiếu cuối tháng (MTM/NAV) | 89,0% (876,9tr/985,6tr) | 95,3% (907,6tr/952,4tr) | — |

**Cảnh báo phương pháp (quan trọng):** `nav_history_{account}.csv` có **4-5 ngày trống** trong
tháng 8 (SpaceX thiếu 06,10,25,27/08; ZaloPay thiếu thêm 07/08 — 5 ngày, xem §9). Lợi suất tính
trên mẫu này GỘP nhiều phiên liên tiếp vào 1 quan sát tại những chỗ có gap (vd bước nhảy 07→11/08
gộp 2 phiên thị trường thật) → **phóng đại độ lệch chuẩn ngày lẻ đó**, làm biến động năm hoá ước
tính CAO hơn con số thật nếu tính đủ 20 phiên. VNINDEX (nguồn BQ, đủ 20/20 phiên, không gap) dùng
làm đối chứng — chênh lệch vol SpaceX (12,4%) thấp hơn VNINDEX hợp lý (danh mục đa dạng hoá tốt
hơn 1 chỉ số), nhưng ZaloPay (25,6%) cao hơn hẳn VNINDEX một phần do đúng 2 trong 5 gap của nó rơi
ngay quanh giai đoạn biến động nhất (12-14/08, đỉnh rồi giảm mạnh) — số này CẦN Spyros đối chiếu
lại trên chuỗi đã vá gap trước khi dùng cho quyết định risk sizing.

Tỷ trọng cổ phiếu cuối tháng CHƯA trừ DGC (ZaloPay, excluded_tickers) — active_nav (loại DGC)
= (907.558.300 − 430.000.000)/(952.365.940 − 430.000.000) ≈ 91,3% cổ phiếu/active_nav, xem §8.2.

---

## 5. DIỄN BIẾN VĨ MÔ THÁNG 8/2026 & ĐÁNH GIÁ RỦI RO KHỦNG HOẢNG
> **Người phụ trách: Bobby** (macro-strategist) · Đọc BLIND với forward-return và backtest outcome
> Dữ liệu: GSO/Tổng cục Thống kê, SBV, Fed, NBS Trung Quốc, EIA · Chốt ngày: 25/08/2026

> **Lưu ý dữ liệu:** CPI tháng 8/2026 chưa được Tổng cục Thống kê công bố (lịch mới: ngày 6/9/2026).
> Mọi số liệu CPI dưới đây là tháng 7/2026 hoặc lũy kế 7 tháng — ghi rõ tường minh.

---

### 5.1 Số liệu kinh tế trong nước

**Tăng trưởng GDP:** Kinh tế Việt Nam tiếp tục đà tăng tốc mạnh. GDP Q2/2026 đạt **+8,39% YoY**
(Q1: +7,94%), nâng lũy kế H1/2026 lên **+8,18%** — thuộc nhóm cao nhất khu vực ASEAN. Chính phủ
đặt mục tiêu tăng trưởng cả năm 2026 ở mức 8% hoặc có thể hướng tới 2 con số.

**Lạm phát — CPI tháng 7/2026 (số liệu TCTK mới nhất):**
- MoM: **−0,12%** (giảm nhẹ theo mùa vụ)
- YoY: **+4,45%** (giảm nhẹ so với tháng 6: +4,69%)
- Lũy kế 7 tháng 2026: **+4,39% YoY** · Lạm phát cơ bản: **+4,19%**

CPI đang tiệm cận nhưng *chưa vượt* trần mục tiêu Quốc hội (~4,5%). Bloomberg survey dự báo bình
quân năm 2026 ở mức 4,8% — hàm ý CPI có thể nhích lên trong các tháng cuối năm.

**Sản xuất công nghiệp (tháng 7/2026):** IIP tăng **+14,5% YoY**; lũy kế 7 tháng **+11,4% YoY** —
mức cao nhất trong nhiều năm. Manufacturing đóng góp 33,07% tổng giá trị gia tăng toàn nền kinh tế Q2.

**Bán lẻ (tháng 7/2026):** Tổng mức bán lẻ đạt 669,1 nghìn tỷ VND, tăng **+14,5% YoY**
(7 tháng: +13,1% theo giá hiện hành, +7,5% loại trừ yếu tố giá). Cầu nội địa duy trì mạnh.

**Xuất nhập khẩu (tháng 7/2026 và lũy kế 7 tháng):**

| Chỉ tiêu | Tháng 7/2026 | Lũy kế 7T/2026 | So sánh 7T/2025 |
|---|---|---|---|
| Xuất khẩu | 53,08 tỷ USD (+25,0% YoY) | 319,53 tỷ USD (+21,7%) | — |
| Nhập khẩu | 56,67 tỷ USD (+41,4% YoY) | 340,05 tỷ USD (+34,8%) | — |
| Cán cân | −3,59 tỷ USD | **−20,52 tỷ USD** | Đảo chiều từ **+10,35 tỷ USD** |

Nhập khẩu tăng vọt do máy móc thiết bị FDI và đầu tư hạ tầng — phản ánh chu kỳ mở rộng đầu tư,
chưa phải mất cân đối tiêu dùng. Cần theo dõi dự trữ ngoại hối nếu thâm hụt kéo dài.

---

### 5.2 Chính sách tiền tệ

**Lãi suất điều hành NHNN:** Lãi suất tái cấp vốn giữ nguyên **4,5%** (từ tháng 8/2023 đến nay).
Chính sách tiền tệ tiếp tục nới lỏng hỗ trợ tăng trưởng.

**Tăng trưởng tín dụng:** Mục tiêu toàn năm 2026: **~15%**. Đến 31/7/2026: +8,98% YTD (~20,3 triệu tỷ VND),
bám sát kế hoạch. NHNN triển khai gói tín dụng ưu đãi 200.000 tỷ đồng (~8,4 tỷ USD) cho SME.
Chính phủ giao NHNN siết tín dụng vào lĩnh vực rủi ro (BĐS) và đẩy nhanh xử lý nợ xấu.

**Tỷ giá VND/USD:** Ổn định trong tháng 8, dao động **26.013–26.345** (bình quân ~26.224). Tỷ giá
trung tâm SBV ngày 24/8: 25.600; thị trường ~26.280. DXY dưới 99 điểm là yếu tố thuận lợi.

**Chất lượng ngân hàng:** NPL toàn hệ thống **2,01%** cuối Q2 (từ 1,99% Q1) — vẫn kiểm soát được.
Lãi suất huy động có áp lực tăng nhẹ (dự báo +0,5–1 điểm % cả năm) nhưng chưa đến mức đáng lo.

---

### 5.3 Bối cảnh quốc tế

**Fed:** Họp FOMC 29/7/2026 giữ nguyên **3,50–3,75%** với 3 thành viên bất đồng (muốn tăng).
Không có forward guidance cho tháng 9. Fed Chair Kevin Warsh (nhậm chức 5/2026) thận trọng.
Rủi ro tăng lãi suất thêm vẫn hiện hữu — đặc biệt nếu CPI Mỹ tiếp tục cứng.

**Trung Quốc:** PMI sản xuất NBS tháng 7: **49,2** (tháng 6: 50,3) — tháng thứ 5 dưới ngưỡng 50.
PMI phi sản xuất: 49,0. Trung Quốc là đối tác thương mại lớn nhất của VN; suy yếu kéo dài ảnh
hưởng chuỗi cung ứng nguyên vật liệu và cầu nhập khẩu hàng VN.

**Giá dầu Brent:** Biến động mạnh tháng 7–8: đáy 69 USD (đầu T7, sau MOU Mỹ-Iran) → đỉnh 105 USD
(23/7, căng thẳng Hormuz) → **~85 USD** (24/8/2026). J.P. Morgan dự báo bình quân Q3: 86 USD.
Biên độ ±35% trong 2 tháng phản ánh rủi ro địa chính trị cao, ảnh hưởng chi phí sản xuất và lạm phát nhập khẩu VN.

**VIX/Biến động toàn cầu:** Bất định Fed, địa chính trị Trung Đông, PMI Trung Quốc suy yếu — môi
trường rủi ro toàn cầu đang ở mức cao hơn bình thường trong tháng 8/2026.

---

### 5.4 Đánh giá rủi ro khủng hoảng

**Verdict: KHÔNG CÓ CRISIS SIGNAL**

Đối chiếu với framework Bobby (Loại 1 / Loại 2):

| Chỉ báo cảnh báo sớm | Ngưỡng nguy hiểm | Mức tháng 8/2026 | Kết quả |
|---|---|---|---|
| CPI YoY | ≥6% (PIT filter) / ≥8% (STRUCTURAL) | **4,45%** (T7) | ✅ Dưới ngưỡng |
| Lãi tiết kiệm 12M | ≥9% (PIT filter block) | ~6,5–7% (ước tính) | ✅ Dưới ngưỡng |
| Tăng trưởng tín dụng | ≥30% | **~15%/năm** (trong target) | ✅ Bình thường |
| NPL hệ thống ngân hàng | ≥5% | **2,01%** | ✅ Bình thường |
| Cán cân vãng lai | Xu hướng xấu nhiều quý | Đang xấu đi (FDI-driven) | ⚠️ WATCH |

**Kết luận:** Không có chỉ báo cốt lõi nào của Loại 1 (excess-credit/inflation structural) bị kích
hoạt. Macro VN đang trong **pha tăng trưởng lành mạnh** — GDP +8,18% H1, sản xuất +11,4%, tiêu dùng
+13%. Rủi ro chủ yếu đến từ bên ngoài (Fed/Trung Quốc/giá dầu), chưa yêu cầu hành động phòng thủ.

**Danh sách WATCH (theo dõi, chưa hành động):**
1. CPI tiệm cận trần 4,5%; Bloomberg dự báo 4,8% cuối năm — theo dõi xem có vượt 5%+ không
2. Thâm hụt thương mại đảo chiều lớn (-20,52 tỷ USD 7T) — theo dõi dự trữ ngoại hối
3. PMI Trung Quốc dưới 50 tháng thứ 5 liên tiếp — rủi ro chuỗi cung ứng
4. Fed bất định tháng 9 — nếu tăng lãi có thể tái áp lực tỷ giá như Q4/2022

*Ngưỡng kích hoạt PIT filter sản phẩm (tham chiếu): CPI≥6% OR lãi tiết kiệm≥9% → block capit_margin_lever. Cả hai đang còn đệm an toàn đáng kể tháng 8/2026.*

---

## 6. PHÍ & CHI PHÍ
> **Người phụ trách: Taylor** · Nguồn: `exec_{account}_2026-08-*_journal.csv` (event=FILL, đã lọc account_no theo tên file riêng từng account — §12)

| Khoản mục | SpaceX | ZaloPay |
|---|---:|---:|
| Giá trị mua trong tháng | 231.965.000đ | 130.945.000đ |
| Giá trị bán trong tháng | 339.160.000đ | 164.175.000đ |
| Tổng giá trị giao dịch | 571.125.000đ | 295.120.000đ |
| Phí giao dịch (0,075%/lượt, cả 2 chiều) | ~428.344đ | ~221.334đ |
| Thuế bán (0,1%, chỉ chiều bán) | ~339.160đ | ~164.175đ |
| **Tổng phí + thuế ước tính** | **~767.504đ** | **~385.509đ** |
| Lãi vay margin (`depositFeeAmount` API thật, 28/08) | 8.284đ | 0 (cash-only, `totalDebt`=6.842đ dư margin phái sinh không dùng) |
| Phí quản lý / hiệu suất | **0** | **0** |

Tổng phí+thuế/NAV trung bình tháng: SpaceX ~0,08%, ZaloPay ~0,04% — không đáng kể so với biến động
giá. `depositFeeAmount` là số phí ĐÃ POST thật từ DNSE (không phải ước tính) nhưng rất nhỏ
(8.284đ SpaceX) so với dư nợ margin thực tế còn tồn 7.763đ cuối kỳ — dư nợ này phát sinh từ khớp
lệnh cuối phiên/margin phái sinh kỹ thuật, KHÔNG phải vay chủ động (capit_margin_lever mới
ENABLED 22/08, chưa có gói vay margin lớn nào giải ngân trong tháng — xem §7.2).

---

## 7. NHẬT KÝ SỰ KIỆN THÁNG
> **Người phụ trách: Mike** · Nguồn: bus events (inbox/Taylor.jsonl + inbox/SpaceX.jsonl), KB, Discord topic Trading Daily

### 7.1 Signal HOLD toàn bộ từ 21/08 (VPI)
HOLD_ALL áp dụng cho cả 2 tài khoản đến 2026-09-16 (quyết định user 19/08).
Tín hiệu BAL mới phát sinh → escalate hỏi, không tự mua.

### 7.2 capit_margin_lever LIVE từ 24/08
`enabled=True`, `f=1.3`, `gate=dd52≤−20%`, `loan_package_id=1840 (RocketX)`.
Mỗi ngày có CAPIT margin phải chạy `approve_margin_day.py` trước bot.

### 7.3 capit_margin_lever ENABLED chính thức — 22/08
Mike xác nhận `enabled=true` trong `data/trading_rules.json` với authorization user qua Discord
thread 1521735922066919515 (2026-08-22, `decided_by: "user"`), selfcheck 188/180 PASS. Cấu hình
đầy đủ (`f=1.3`, `gate=dd52≤−20%`, `loan_package_id=1840`) LIVE từ 24/08 sau khi các bước wiring
phụ hoàn tất — human gate thứ 2 (`approve_margin_day.py`) vẫn bắt buộc mỗi ngày có lệnh dùng
gói vay này. Chưa có gói vay margin lớn nào giải ngân qua kênh này trong tháng 8 (dư nợ margin
cuối tháng chỉ 7.763đ SpaceX — kỹ thuật, không phải leverage chủ động, xem §6).

### 7.4 MBB quyền mua 10:1 — thực hiện 28/08, phát hiện reconcile lệch, xử lý cùng ngày
Sự kiện cổ tức cổ phiếu MBB 15% + quyền mua 10:1 (ex-date 11/08, đã CONFIRMED 3 nguồn độc lập
10/08-11/08). Quyền mua (mua thêm cổ phiếu, KHÔNG tự động như cổ tức CP) được user thực hiện và
xác nhận hoàn tất trên app DNSE tối 28/08 (SpaceX +110cp, ZaloPay +20cp, ~10.000đ/cp). DollarBill
phát hiện lệch reconcile 12:10 ICT cùng ngày (BLOCKED_RECONCILE ở L1 park_trim), điều tra ra đúng
nguyên nhân bằng đối chiếu giá vốn (khớp tuyệt đối tới đồng), bổ sung journal FILL 16:03 ICT sau
khi user xác nhận bằng 2 ảnh chụp app DNSE — đóng xong trong ngày, không ảnh hưởng plan (HOLD_ALL
đang hiệu lực, 0 lệnh cần trim). Giới hạn cấu trúc còn tồn: quyền mua thực hiện qua tính năng
riêng của DNSE KHÔNG sinh order/trade record trong `dnse_raw` ⇒ `verify_account_snapshot.py` sẽ
LUÔN báo WARN qty mismatch cho MBB kể từ đây — không phải lỗi tái diễn, xem §11.2.

### 7.5 MSB cổ phiếu thưởng 20% — ex-date đúng ngày chốt tháng, 28/08
Xác nhận CONFIRMED 27/08 (user authorization qua Discord thread 1542337717776556062, "Nếu có phải
fix gap ngay"), verify khớp BQ 02/09 (`bq_factor=1,2003` vs khai báo 1,2, MATCH). Ex-date trùng
đúng phiên chốt tháng — không tạo lệch số liệu vì broker đã cập nhật `openQuantity`/`costPrice`
trước khi snapshot 28/08 được ghi lại.

### 7.6 Host tắt ~18 tiếng 24/08 15:30 → 25/08 09:45 ICT — bỏ lỡ 1 loạt cron đêm
Không phải bug script (đã xác nhận qua `last -x`, log trống toàn bộ cửa sổ). Ảnh hưởng: cron
00:30 `daily_retro`, `daily_refresh`, `sync_bq_cache`, `paper_report` không fire — đây là nguyên
nhân trực tiếp của khoảng trống `nav_history` ngày 25/08 (xem §9). Đã recovery thủ công sáng 25/08
cho các pipeline chính.

### 7.7 Bot chết cả 2 account 14/08 — git stash conflict marker, 0 lệnh, không mất tiền
`git stash apply` bỏ dở để lại conflict marker `<<<<<<<` trong `trading_bot/config.py` +
`executor.py` → cả 2 bot thoát rc=1 ngay khi khởi động 09:05 ICT. 0 lệnh được đặt, không có lệnh
kẹt, không ảnh hưởng NAV (chỉ mất cơ hội đặt lệnh TV1 đã duyệt hôm đó).

---

## 8. DANH MỤC CUỐI THÁNG (31/08/2026)
> **Người phụ trách: Taylor** · Nguồn: DNSE API positions 31/08 (same-day = DNSE API, không dùng BQ §6 coding_guidelines)

### 8.1 SpaceX — 27 mã (nguồn: `dnse_raw_2026-08-31.jsonl`, positions record cuối, gộp multi-lot)

| Mã | qty | Giá vốn BQ | Giá TT (28/08) | Giá trị TT | % NAV |
|---|---:|---:|---:|---:|---:|
| PVT | 3.500 | 17.100 | 20.200 | 70.700.000 | 7,2% |
| MBB | 1.675 | 20.657 | 21.050 | 35.258.750 | 3,6% |
| SIP | 1.700 | 47.059 | 49.450 | 84.065.000 | 8,5% |
| VHM | 900 | 74.900 | 73.000 | 65.700.000 | 6,7% |
| BID | 1.175 | 39.571 | 36.850 | 43.298.750 | 4,4% |
| VNM | 900 | 58.600 | 62.300 | 56.070.000 | 5,7% |
| DRI | 3.700 | 13.262 | 14.100 | 52.170.000 | 5,3% |
| SAB | 1.100 | 44.368 | 45.600 | 50.160.000 | 5,1% |
| CTG | 1.200 | 33.806 | 31.950 | 38.340.000 | 3,9% |
| VCB | 700 | 61.464 | 60.100 | 42.070.000 | 4,3% |
| TV1 | 2.300 | 20.148 | 20.600 | 47.380.000 | 4,8% |
| NCT | 500 | 86.360 | 83.600 | 41.800.000 | 4,2% |
| VPB | 1.200 | 27.746 | 27.800 | 33.360.000 | 3,4% |
| TCB | 1.000 | 33.900 | 33.400 | 33.400.000 | 3,4% |
| SCL | 1.500 | 23.600 | 27.600 | 41.400.000 | 4,2% |
| ACB | 900 | 22.656 | 22.650 | 20.385.000 | 2,1% |
| HDB | 800 | 26.709 | 27.800 | 22.240.000 | 2,3% |
| HPG | 1.200 | 22.200 | 22.100 | 26.520.000 | 2,7% |
| VRE | 300 | 25.550 | 26.100 | 7.830.000 | 0,8% |
| SHB | 800 | 12.281 | 12.200 | 9.760.000 | 1,0% |
| LPB | 400 | 52.183 | 49.950 | 19.980.000 | 2,0% |
| TPB | 500 | 16.800 | 14.650 | 7.325.000 | 0,7% |
| MSB | 600 | 13.542 | 13.350 | 8.010.000 | 0,8% |
| VIX | 420 | 15.464 | 14.100 | 5.922.000 | 0,6% |
| VIB | 500 | 14.900 | 14.950 | 7.475.000 | 0,8% |
| VND | 300 | 17.800 | 16.650 | 4.995.000 | 0,5% |
| EVF | 100 | 12.550 | 12.400 | 1.240.000 | 0,1% |
| **Tổng cổ phiếu** | | | | **876.854.500** | **89,0%** |
| Tiền mặt | | | | 8.195.610 | 0,8% |
| Nợ margin | | | | −7.763 | 0,0% |
| Tài sản off-book (Trứng vàng) | | | | 100.505.558 | 10,2% |
| **NAV** | | | | **985.617.905** | **100%** |

### 8.2 ZaloPay — 27 mã bot quản lý + 1 mã legacy excluded (DGC) — 28 mã tổng

| Mã | qty | Giá vốn BQ | Giá TT | Giá trị TT | % NAV | % active_nav |
|---|---:|---:|---:|---:|---:|---:|
| **DGC (EXCLUDED, legacy)** | **10.000** | **47.775** | **43.000** | **430.000.000** | **45,2%** | **—** |
| PVT | 2.071 | 17.248 | 20.200 | 41.834.200 | 4,4% | 8,0% |
| SCL | 1.000 | 23.590 | 27.600 | 27.600.000 | 2,9% | 5,3% |
| VPB | 1.300 | 26.745 | 27.800 | 36.140.000 | 3,8% | 6,9% |
| SIP | 749 | 47.140 | 49.450 | 37.038.050 | 3,9% | 7,1% |
| VNM | 601 | 58.700 | 62.300 | 37.442.300 | 3,9% | 7,2% |
| SAB | 744 | 44.450 | 45.600 | 33.926.400 | 3,6% | 6,5% |
| MBB | 652 | 20.535 | 21.050 | 13.724.600 | 1,4% | 2,6% |
| CSV | 1.000 | 19.750 | 21.550 | 21.550.000 | 2,3% | 4,1% |
| NCT | 373 | 86.400 | 83.600 | 31.182.800 | 3,3% | 6,0% |
| TV1 | 1.200 | 20.400 | 20.600 | 24.720.000 | 2,6% | 4,7% |
| HDB | 459 | 25.891 | 27.800 | 12.760.200 | 1,3% | 2,4% |
| BID | 427 | 37.588 | 36.850 | 15.734.950 | 1,7% | 3,0% |
| DRI | 1.900 | 13.263 | 14.100 | 26.790.000 | 2,8% | 5,1% |
| LPB | 352 | 54.843 | 49.950 | 17.582.400 | 1,8% | 3,4% |
| TCB | 356 | 31.611 | 33.400 | 11.890.400 | 1,2% | 2,3% |
| CTG | 450 | 32.133 | 31.950 | 14.377.500 | 1,5% | 2,8% |
| VCB | 300 | 60.638 | 60.100 | 18.030.000 | 1,9% | 3,5% |
| VHM | 300 | 74.317 | 73.000 | 21.900.000 | 2,3% | 4,2% |
| HPG | 500 | 22.200 | 22.100 | 11.050.000 | 1,2% | 2,1% |
| ACB | 300 | 22.700 | 22.650 | 6.795.000 | 0,7% | 1,3% |
| MSB | 240 | 13.542 | 13.350 | 3.204.000 | 0,3% | 0,6% |
| TPB | 100 | 14.800 | 14.650 | 1.465.000 | 0,2% | 0,3% |
| VRE | 100 | 25.550 | 26.100 | 2.610.000 | 0,3% | 0,5% |
| VIB | 200 | 14.900 | 14.950 | 2.990.000 | 0,3% | 0,6% |
| VIX | 105 | 13.286 | 14.100 | 1.480.500 | 0,2% | 0,3% |
| SHB | 300 | 12.100 | 12.200 | 3.660.000 | 0,4% | 0,7% |
| **Tổng cổ phiếu (kể cả DGC)** | | | | **907.478.300** | **95,3%** | |
| Tổng cổ phiếu (loại DGC, active) | | | | 477.478.300 | | 91,4% |
| Tiền mặt | | | | 5.936.934 | 0,6% | |
| Nợ margin (kỹ thuật, cash-only) | | | | −6.842 | 0,0% | |
| Tài sản off-book (Trứng vàng) | | | | 38.877.548 | 4,1% | |
| **NAV** | | | | **952.365.940** | **100%** | |

### 8.3 Ghi chú rủi ro tập trung
> Số liệu tạm thời (Taylor), chưa qua audit Spyros — xem cảnh báo §4.

- **SpaceX**: không có mã nào vượt 10% NAV riêng lẻ (SIP cao nhất 8,5%). Tập trung ngành ngân
  hàng cao (36,3% cost, 11/27 mã) — đặc thù cấu trúc thị trường VN (ngân hàng chiếm tỷ trọng lớn
  VNINDEX), không phải lệch có chủ đích của chiến lược.
- **ZaloPay**: **DGC chiếm 45,2% NAV** — mức tập trung đơn lẻ RẤT CAO, nhưng đây là vị thế
  **legacy bị KHOÁ hoàn toàn** (không mua/bán được do hạn chế giao dịch HOSE + vụ án hình sự liên
  quan), không phải quyết định sizing của bot. Phần bot chủ động quản lý (active_nav, loại DGC)
  có cấu trúc phân tán hợp lý, mã cao nhất PVT 8,0% active_nav.
- Không có mã nào trong danh sách BANNED vĩnh viễn (PC1/VVS/KSF/NKG/HSG/HVN/VJC/NVL/GEG/SBA/
  DMC/IMP/TRA/TOS/VTP) xuất hiện ở cả 2 tài khoản.

---

## 9. CÔNG BỐ SỰ CỐ & KHOẢNG TRỐNG SỐ LIỆU
> **Người phụ trách: Mike** · Nguồn: kb/incidents/2026-08/, bus events, ops_health_check

**Nguyên tắc: công bố MỌI sự cố ảnh hưởng NAV/giao dịch/số liệu, kể cả đã tự khắc phục.**

### 9.1 Sự cố vận hành trong tháng (chi tiết ở §7)
1. **Báo cáo tháng 08 bị giao THIẾU NỘI DUNG 28/08, TRƯỚC KHI THÁNG ĐÓNG.** File này (template
   tạo 25/08 với 5/10 mục còn để trống chờ điền) đã bị `report_delivery_gate.py` coi là hoàn tất và giao thật
   qua Discord+email lúc 2026-08-28T03:33 UTC — 3 ngày trước khi kỳ báo cáo (01-31/08) kết thúc.
   Nguyên nhân gốc: `report_return_gate.py` không có phép kiểm nội dung nào (chỉ kiểm tỉ suất NẾU
   có bảng để kiểm — bảng TBD không có dòng nào nên PASS trong rỗng), và
   `check_report_cadence.sh` coi "có file đúng tên tháng" = đã xong, không kiểm trạng thái GIAO
   THẬT. **User chưa từng nhận được báo cáo tháng 8 thật trong suốt 5 ngày (28/08→02/09).** Đã
   vá cả 2 lỗ hổng cơ chế 02/09 (content-completeness gate + detector dùng delivered() thay vì
   sự tồn tại file) — xem commit 068c79c3, selfcheck 46/46 + 24/24 PASS.
2. **Bot chết cả 2 account 14/08** (git stash conflict marker) — 0 lệnh, không mất tiền (§7.7).
3. **Host tắt ~18 tiếng 24-25/08** — bỏ lỡ loạt cron đêm, gây khoảng trống dữ liệu 25/08 (§7.6, §9.2).
4. **MBB reconcile lệch 28/08** (quyền mua không sinh order record) — điều tra + xử lý cùng ngày,
   không ảnh hưởng plan (§7.4). Giới hạn cấu trúc CÒN TỒN TẠI VĨNH VIỄN (xem §11.2).

### 9.2 Khoảng trống dữ liệu `nav_history` tháng 8

| Tài khoản | Ngày thiếu | Nguyên nhân |
|---|---|---|
| SpaceX | 06, 10, 25, 27/08 | 25/08 = host downtime (§7.6, xác nhận). 06, 10, 27/08 = **chưa xác định nguyên nhân cụ thể**, không có incident log tương ứng — cần điều tra thêm, không suy đoán. |
| ZaloPay | 06, 07, 10, 25, 27/08 | Cùng danh sách + thêm 07/08. |

Ảnh hưởng: bảng diễn biến theo tuần §2.1 dùng giá trị gần nhất có sẵn thay thế (không nội suy);
chỉ số biến động §4 bị phóng đại nhẹ do gộp phiên tại các điểm gap — đã ghi caveat tại §4.

### 9.3 Hạng mục kế thừa từ tháng 7 (theo dõi tiếp)
- CAPIT episode 2026-07-20 (NCT/PVT/SAB/SIP/VNM): còn khoá đến ~60-phiên lock (~đầu 10/2026),
  chưa có sự kiện exit nào trong tháng 8.
- ZaloPay VPB: vị thế legacy (trước khi bot bắt đầu theo dõi tài khoản), `verify_account_snapshot.py`
  không tái tạo được cost basis qua journal fill reconstruction — số liệu P&L cho VPB trong §3.4
  dùng trực tiếp `costPrice` broker-native (đáng tin, chỉ không cross-check được qua 2 nguồn độc
  lập như các mã khác).

---

## 10. TRIỂN VỌNG & VIỆC CẦN LÀM
> **Người phụ trách: Mike + DollarBill** · Nguồn: current_ops.md + macro §5 + kết quả tháng

### 10.1 Bối cảnh hệ thống bước sang tháng 9
Signal HOLD_ALL vẫn hiệu lực cả 2 tài khoản đến 2026-09-16 (quyết định user 19/08, §7.1) — tháng
9 mở đầu KHÔNG có lệnh mới cho tới khi HOLD được gỡ hoặc có tín hiệu escalate riêng. Macro nền
(§5, Bobby) không có crisis signal — GDP +8,18% H1, CPI 4,45% dưới trần, tín dụng trong mục tiêu —
môi trường thuận lợi để tái mở vị thế khi HOLD hết hạn. capit_margin_lever đã ENABLED (§7.3) nhưng
chưa có gói vay lớn giải ngân — CAPIT episode 07-20 vẫn khoá đến ~đầu 10/2026 (§9.3) nên phạm vi
kích hoạt gate `dd52≤−20%` trong tháng 9 phụ thuộc diễn biến giá các mã trong rổ đó.

### 10.2 Rủi ro chính tháng 9
1. **CPI tháng 8 chưa công bố** (TCTK dự kiến 06/09) — nếu vượt đáng kể so với ước tính 4,45%
   tháng 7, có thể đổi verdict macro §5.4 từ "không crisis" sang cảnh giác hơn.
2. **Fed FOMC tháng 9** chưa có forward guidance rõ — rủi ro tỷ giá nếu Fed tăng lãi (§5.3).
3. **Khoảng trống dữ liệu `nav_history` chưa rõ nguyên nhân** (06,10,27/08, §9.2) — nếu tái diễn
   tháng 9 mà không xác định được nguyên nhân, cần điều tra kỹ hơn thay vì tiếp tục dùng giá trị
   gần nhất thay thế.
4. **Giới hạn cấu trúc reconcile_equity.py** (thiếu realized P&L, §1) — nếu tháng 9 có nhiều giao
   dịch xoay vòng hơn (bán rồi mua lại), residual sẽ càng lớn; nên ưu tiên bổ sung tracking
   realized P&L vào công cụ này trước báo cáo tháng 9.

### 10.3 Việc cần làm — có người phụ trách và hạn nghiệm thu

| # | Việc | Người phụ trách | Hạn |
|---|---|---|---|
| 1 | Cập nhật CPI thực tế tháng 8 vào §5 khi TCTK công bố (06/09) | **Bobby** | 07/09/2026 |
| 2 | Verify fill thật capit_margin_lever lần đầu (sau khi CAPIT signal kích hoạt) | **Spyros** | Khi có fill |
| 3 | Audit lại §4 chỉ số rủi ro (Taylor tính tạm, chưa qua Spyros) | **Spyros** | 05/09/2026 |
| 4 | Điều tra nguyên nhân khoảng trống `nav_history` 06,10,27/08 (chưa xác định) | **Winston** | 10/09/2026 |
| 5 | Bổ sung realized P&L vào `reconcile_equity.py` (residual +2,41% SpaceX hiện tại) | **Taylor** | trước báo cáo tháng 9 |

---

## 11. PHỤ LỤC — PHƯƠNG PHÁP & LƯU Ý
> **Người phụ trách: Taylor** · Cập nhật nếu có thay đổi pipeline so với tháng 7

### 11.1 Pipeline xác minh số liệu (bắt buộc, không có ngoại lệ)
Không đổi so với tháng 7: `verify_account_snapshot.py` (đối chiếu broker vs journal) →
`reconcile_equity.py` (đẳng thức vốn) → `dividend_adjusted_return.py`/`report_return_gate.py`
(tỷ suất per-position đã cộng cổ tức) — theo §6/§21 `coding_guidelines.md`. **Thay đổi tháng
này**: `reconcile_equity.py` không dùng được cho §1 (residual +2,41% do thiếu realized P&L —
xem §1) nên NAV MTD chuyển sang tính trực tiếp bằng hiệu 2 đầu mút `nav_history` broker-native;
`report_return_gate.py` được vá 2 lỗi mới phát hiện khi dựng báo cáo này (content-completeness
gate + gộp vị thế nhiều lô, xem §9.1/§11.2) — cả 2 đã selfcheck PASS và commit.

### 11.2 Cạm bẫy số liệu đặc thù tháng 8

1. **MBB — quyền mua không sinh order/trade record.** `verify_account_snapshot.py` sẽ **LUÔN**
   báo `WARN qty mismatch MBB` từ nay về sau cho MỌI kỳ báo cáo còn giữ MBB, vì cấu trúc dữ liệu
   (`dnse_fill_events` đọc từ order/trade history) không bao giờ thấy được giao dịch quyền mua
   (một tính năng riêng của DNSE, không qua sổ lệnh thường). Đây KHÔNG phải bug tái diễn cần điều
   tra lại — dùng trực tiếp `openQuantity`/`costPrice` từ `positions` broker-native (đã verify 2
   nguồn độc lập 28/08, xem §7.4).

2. **`report_return_gate.py::broker_positions()` từng ghi đè vị thế nhiều lô (đã vá 02/09).**
   Một mã cùng lúc nằm ở ≥2 `loanPackageId` (margin thường + gói CAPIT riêng) bị lấy CHỈ lô cuối
   cùng trong mảng JSON, làm mất hẳn lô đứng trước. Phát hiện thật khi dựng báo cáo này: ZaloPay
   28/08 có 3 mã multi-lot (BID 107+320cp, MBB 400+252cp, VCB 200+100cp) — nếu không sửa, bảng
   §3.4 sẽ báo thiếu ~1/3 số lượng 3 mã này. Đã sửa gộp qty + bình quân gia quyền cost, selfcheck
   thêm case 16b, commit df5d2e36.

3. **Phiên chốt tháng ≠ ngày cuối tháng dương lịch khi có nghỉ lễ dài.** Tháng 8/2026 chốt tại
   28/08 (Thứ Sáu) chứ không phải 31/08, vì HOSE nghỉ lễ Quốc khánh 31/08→02/09/2026 liền với cuối
   tuần. `report_return_gate.py::accounts_asof_from_name()` tự suy đúng ngày này cho filename dạng
   `..._2026-08.md` (chọn file `dnse_raw_YYYY-MM-DD.jsonl` MỚI NHẤT tồn tại trong tháng, không
   nhất thiết là ngày 31) — không hardcode "ngày cuối tháng dương lịch" ở bất kỳ chỗ nào khác khi
   viết công cụ mới đọc báo cáo tháng.

4. **`nav_history` có khoảng trống 4-5 ngày trong tháng** (khác biệt với tháng 7, vốn liên tục
   hơn) — xem §9.2. Bất kỳ phép tính biến động/lợi suất theo NGÀY nào trên chuỗi này phải nêu rõ
   caveat gộp-phiên-tại-gap, không trình bày như thể mẫu liên tục.

### 11.3 Quy ước
- Giá mark-to-market = giá đóng cửa phiên cuối kỳ
- Số liệu cùng ngày (định giá lệnh, sức mua) = DNSE API trực tiếp, KHÔNG dùng BQ
- Cổ tức tiền mặt = bắt buộc dùng `dividend_adjusted_return.py` (§21 coding_guidelines), hiển thị cả gộp lẫn ròng (−5% thuế TNCN)
- Phí: giao dịch 0,075%/lượt; thuế bán 0,1%; lãi margin ~12,5%/năm (chưa xác minh với DNSE)
- KHÔNG báo cáo Sharpe/Sortino/Calmar — cần tối thiểu 6 tháng NAV ngày (milestone: 01/01/2027)

### 11.4 Công bố tuân thủ
- Đây không phải khuyến nghị đầu tư. Kết quả quá khứ không đảm bảo kết quả tương lai.
- Mọi số liệu trace được về nguồn broker; số chưa trace được ghi rõ là thiếu/ước tính.

---

*Báo cáo tháng 08/2026 · Tổng hợp từ hệ thống giám sát vận hành nội bộ, đối soát với dữ liệu DNSE API và BigQuery.*
*Template tạo 25/08/2026; điền đầy đủ 02/09/2026 (Taylor).*
*Báo cáo tuần chi tiết: SpaceX_ZaloPay_weekly_report_2026-08-03_to_2026-08-07.md · ..._08-10_to_08-14.md · ..._08-17_to_08-21.md · ..._08-24_to_08-28.md*
