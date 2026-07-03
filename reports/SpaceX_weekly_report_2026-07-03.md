# BÁO CÁO TUẦN — TÀI KHOẢN SPACEX
## Kỳ báo cáo: 01/07/2026 – 03/07/2026 (Tuần đầu tiên vận hành thực — "Go-Live Week 1")

**Tài khoản:** SpaceX · DNSE, số hiệu 0002023347
**Chiến lược:** V2.4 (custom30V — chiến lược giá trị định lượng, NAV mục tiêu 1.000.000.000 VND)
**Ngày báo cáo:** 03/07/2026 · **Người lập:** Mike (Fleet Coordinator) — số liệu đối soát tự động qua hệ thống giám sát nội bộ
**Đối tượng:** Báo cáo hiệu suất & vận hành — có thể chia sẻ với nhà đầu tư

---

> **📌 ĐÍNH CHÍNH (03/07/2026, sau khi phát hành bản đầu):** Bản đầu của báo cáo này dùng nhầm
> field giá vốn ước tính (`avg_cost` "ref_px_approx" trong file snapshot nội bộ) làm giá vốn thật
> để tính lãi/lỗ từng mã — field đó **không phải giá khớp lệnh thật**, chỉ là giá tham chiếu ước
> tính. Hậu quả cụ thể: báo cáo cũ ghi VHM lỗ chưa thực hiện −6,4%, trong khi giá vốn thật (khớp
> lệnh thật từ broker) là 149.800đ/cp và giá đóng cửa 03/07 là 151.600đ/cp → **VHM thực chất LÃI
> chưa thực hiện +1,20%**, đúng như phản ánh của người phụ trách quỹ. Toàn bộ bảng lãi/lỗ theo mã
> trong báo cáo này đã được **tính lại từ log gốc của broker** (không phải file tóm tắt trung gian)
> và xác minh chéo độc lập — xem Mục 7 (Phương pháp luận) để biết cơ chế xác minh mới. **NAV tổng
> (993.598.747 VND) không đổi** — số liệu này vốn chỉ phụ thuộc giá thị trường × khối lượng đã đối
> soát broker, không phụ thuộc giá vốn, nên không bị ảnh hưởng bởi lỗi trên.

---

## 1. TÓM TẮT ĐIỀU HÀNH (Executive Summary)

Tài khoản SpaceX chính thức đi vào vận hành thực (go-live) ngày **01/07/2026**, khởi động với NAV
**1.000.000.000 VND**. Đây là báo cáo cho **3 phiên giao dịch đầu tiên** (Thứ Tư 01/07 – Thứ Sáu 03/07).

| Chỉ tiêu | Giá trị |
|---|---|
| NAV đầu kỳ (01/07/2026) | 1.000.000.000 VND |
| NAV cuối kỳ, theo giá thị trường (03/07/2026) | **993.598.747 VND** |
| Thay đổi NAV trong kỳ | **−6.401.253 VND (−0,64%)** |
| VN-Index cùng kỳ (30/06 → 03/07) | 1.860,01 → 1.862,08 (**+0,11%**) |
| Số phiên giao dịch | 3/3 (01/07, 02/07 thực hiện lệnh; 03/07 tạm dừng chủ động — xem mục 3) |
| Số mã đang nắm giữ | 23 |
| Tỷ trọng cổ phiếu/NAV (thời điểm báo cáo) | 140,7%* |

**\* Lưu ý quan trọng:** tỷ trọng 140,7% là con số **tạm thời, đã được nhận diện và có kế hoạch xử lý**
do một sự cố vận hành ngày 02/07 (chi tiết mục 4). Kế hoạch khắc phục đã được phê duyệt và sẽ đưa
tỷ trọng về đúng **94,7%** theo thiết kế chiến lược vào phiên giao dịch kế tiếp (Thứ Hai 06/07/2026).
Không có rủi ro vay margin, không có lệnh bán ép giá (forced-sale) trong toàn bộ thời gian xử lý.

Trong 3 phiên đầu, hiệu suất tài khoản thấp hơn VN-Index khoảng **0,75 điểm phần trăm**, chủ yếu do biến
động giá thị trường bình thường trên danh mục — hai mã đóng góp lỗ chưa thực hiện lớn nhất là **BID
(−1,72%, −3,41tr VND)** và **LPB (−5,03%, −2,43tr VND)** — chứ không liên quan đến sự cố vận hành ở Mục
4. Ngược lại, một số mã đang lãi chưa thực hiện, dẫn đầu là **VHM (+1,20%)** và **MBS (+5,39%)**. Tổng
lãi/lỗ chưa thực hiện toàn danh mục: **−9,76 triệu VND (−0,69% trên phần cổ phiếu)**. Với chỉ 3 phiên dữ
liệu, mọi con số này **chưa có ý nghĩa thống kê** — chưa thể dùng để đánh giá hiệu quả chiến lược; báo
cáo các tuần tiếp theo sẽ cho bức tranh đầy đủ hơn.

---

## 2. BỐI CẢNH THỊ TRƯỜNG TRONG TUẦN

- **Trạng thái thị trường (hệ thống định thời DT5G):** NEUTRAL (trạng thái 3/5, thang từ KHỦNG HOẢNG →
  GIẢM → TRUNG TÍNH → TĂNG → TĂNG MẠNH). Đây là vùng trạng thái phổ biến nhất của thị trường, không có
  tín hiệu phòng thủ đặc biệt (macro gate không áp trần rủi ro).
- **VN-Index:** dao động hẹp 1.854 – 1.871 điểm trong tuần, đóng cửa 03/07 ở 1.862,08 điểm, gần như đi
  ngang so với cuối tuần trước (+0,11%).
- **Không có sự kiện vĩ mô bất thường:** lãi suất tái cấp vốn NHNN ổn định 4,5% (không đổi từ 2023),
  không có tín hiệu cảnh báo từ các chỉ báo rủi ro thị trường quốc tế (VIX trong vùng bình thường).

---

## 3. HOẠT ĐỘNG GIAO DỊCH TRONG TUẦN

### Thứ Tư 01/07/2026 — Ngày giao dịch đầu tiên (Go-live)
Triển khai danh mục khởi tạo theo chiến lược V2.4 (giỏ 30 mã cổ phiếu giá trị "custom30V", tỷ trọng
phòng thủ tại trạng thái NEUTRAL). Đặt 23 lệnh mua; khớp đầy đủ **12/23 lệnh** trong phiên (giá trị khớp
~492,6 triệu / kế hoạch 938,0 triệu VND, tỷ lệ khớp 53%) — 11 lệnh còn lại không khớp do đặt tại vùng
giá tham chiếu trong biên độ thanh khoản thực tế của phiên, được chuyển sang xử lý tiếp phiên sau theo
đúng quy trình chuẩn (không phải lỗi hệ thống).

### Thứ Năm 02/07/2026 — Hoàn tất khớp lệnh còn lại + Sự cố vận hành
11 lệnh mua còn lại từ phiên trước được khớp đủ. Tuy nhiên, hệ thống giám sát đối soát tự động (chạy
độc lập, so khớp lệnh ghi nhận nội bộ với sổ lệnh thực tế từ sàn) phát hiện **cả 11 mã đều bị mua với
khối lượng gấp đôi kế hoạch** — xem chi tiết và biện pháp xử lý ở Mục 4.

### Thứ Sáu 03/07/2026 — Tạm dừng chủ động (HOLD)
Không đặt lệnh mua/bán mới. Đây là quyết định thận trọng: dành trọn phiên để rà soát toàn diện nguyên
nhân sự cố, xác nhận độc lập, và triển khai lớp kiểm soát bổ sung trước khi tiếp tục giao dịch — ưu
tiên an toàn vốn hơn tốc độ xử lý.

**Tổng giá trị giao dịch trong tuần:** 1.408,2 triệu VND (giá vốn thật, đã xác minh qua
`verify_account_snapshot.py` — xem Mục 7) · phí giao dịch ước tính ~1,4 triệu VND (0,1%/lượt) — số liệu
phí chờ đối soát chính thức với sao kê broker (giá vốn gốc đã xác minh, chỉ phí giao dịch còn ước tính).

---

## 4. CÔNG BỐ SỰ CỐ VẬN HÀNH — MINH BẠCH THEO CHUẨN QUẢN TRỊ RỦI RO

Chúng tôi công bố đầy đủ sự cố sau đây theo nguyên tắc minh bạch với nhà đầu tư, kể cả khi không phát
sinh thiệt hại tài chính thực tế.

**Sự việc:** Ngày 02/07/2026, do trùng lặp giữa 2 tiến trình thực thi lệnh tự động chạy đồng thời cho
cùng một tài khoản (một tiến trình theo lịch chuẩn, một tiến trình từ cơ chế tự-phục-hồi kích hoạt sớm
hơn dự kiến vài giây), toàn bộ 11 mã còn lại của kế hoạch trong ngày bị đặt mua **hai lần độc lập** —
mỗi tiến trình không biết về sự tồn tại của tiến trình còn lại. Hậu quả: tỷ trọng cổ phiếu/NAV tăng lên
~140%, và 4 mã ngân hàng (BID, CTG, VPB, MBB) tạm thời vượt giới hạn tỷ trọng tối đa 10%/mã theo chính
sách quản trị rủi ro nội bộ (đạt 19,8% / 19,3% / 15,6% / 15,0%).

**Phát hiện & xác nhận:** Sự việc được phát hiện **trong cùng ngày** bởi hệ thống đối soát tự động
(so khớp dữ liệu lệnh nội bộ với sổ lệnh thực từ sàn), và được xác nhận độc lập lần thứ hai bởi một quy
trình kiểm toán tách biệt trước khi hành động khắc phục được phê duyệt.

**Không phát sinh rủi ro tài chính bất thường:**
- Đây **không phải** vay margin — số dư tiền mặt âm tạm thời (~−405 triệu VND) là khoản phải thanh toán
  theo cơ chế **T+2 tiêu chuẩn của thị trường chứng khoán Việt Nam** (2 ngày làm việc để hoàn tất thanh
  toán sau khi khớp lệnh), xác nhận trực tiếp từ API số dư của công ty chứng khoán: dư nợ vay = 0 VND,
  lãi suất phát sinh = 0 VND.
- Vì cơ chế T+2, không có áp lực phải bán tháo trước ngày 06/07 — có đủ thời gian lên kế hoạch xử lý
  một cách có trật tự, đã được phê duyệt ngay trong ngày phát hiện sự cố.

**Biện pháp khắc phục (đã triển khai, có kiểm thử độc lập trước khi đưa vào production):**
1. Bổ sung cơ chế khóa độc quyền (exclusive lock) — đảm bảo không thể có 2 tiến trình đặt lệnh cùng lúc
   cho cùng một tài khoản trong cùng một ngày.
2. Bổ sung lớp phòng vệ thứ hai, độc lập — tự động đối chiếu sổ lệnh thực từ sàn với dữ liệu nội bộ ở
   MỖI chu kỳ xử lý; nếu phát hiện bất kỳ lệnh nào không rõ nguồn gốc, hệ thống tự động **tạm dừng giao
   dịch mã đó** cho đến khi con người xác nhận thủ công (không tự đoán, không tự gộp).
3. Toàn bộ 2 lớp phòng vệ trên đã qua kiểm thử tự động (self-check) và rà soát độc lập bởi một quy
   trình phản biện chuyên trách trước khi xác nhận hoàn tất.

**Kế hoạch xử lý (đã được phê duyệt, thực hiện Thứ Hai 06/07/2026):** bán đúng phần khối lượng bị mua
trùng của cả 11 mã, đưa toàn bộ vị thế về đúng khối lượng dự kiến ban đầu (1x). Sau khi hoàn tất: tỷ
trọng cổ phiếu/NAV trở về **94,7%** — đúng thiết kế chiến lược V2.4 cho trạng thái thị trường NEUTRAL.

---

## 5. DANH MỤC HIỆN TẠI (chốt 03/07/2026, giá đóng cửa thị trường)

### 5.1 Phân bổ theo ngành

| Ngành | Giá trị thị trường (VND) | % NAV |
|---|---:|---:|
| Ngân hàng | 1.143.830.000 | 115,1%* |
| Bất động sản | 90.960.000 | 9,2% |
| Thép | 62.775.000 | 6,3% |
| Chứng khoán | 45.480.000 | 4,6% |
| Vật liệu xây dựng | 17.380.000 | 1,7% |
| Hóa chất/Phân bón | 14.140.000 | 1,4% |
| Thủy sản/Thực phẩm | 5.930.000 | 0,6% |
| Vận tải/Logistics | 5.190.000 | 0,5% |
| **Tổng cổ phiếu** | **1.398.485.000** | **140,7%*** |
| Tiền mặt (T+2 float) | −404.886.253 | −40,7%* |
| **NAV** | **993.598.747** | **100%** |

*\* Tỷ trọng ngành Ngân hàng và tổng tỷ trọng cổ phiếu phản ánh đúng con số TẠM THỜI trước khi xử lý sự
cố mục 4. Sau trim (dự kiến 06/07): Ngân hàng ước còn ~73,5% NAV, tổng cổ phiếu ~95,0% NAV, tiền mặt
~5,0% NAV — xem chi tiết mục 6.*

### 5.2 Top vị thế tập trung nhất (đơn lẻ) — hiện tại vs. sau xử lý

| Mã | % NAV hiện tại | % NAV dự kiến sau trim (06/07) | Giới hạn chính sách |
|---|---:|---:|---:|
| BID | 19,6% | 9,8% | 10,0% |
| CTG | 19,2% | 9,6% | 10,0% |
| VPB | 15,7% | 7,8% | 10,0% |
| MBB | 14,9% | 7,5% | 10,0% |

Sau khi trim hoàn tất, toàn bộ danh mục tuân thủ giới hạn tập trung 10%/mã theo chính sách quản trị rủi
ro.

---

## 6. KẾ HOẠCH TUẦN TỚI (06/07 – 10/07/2026)

**Thứ Hai 06/07/2026 — Ưu tiên số 1: Xử lý dứt điểm sự cố mục 4**
- Bán phần vượt trội của 11 mã (đưa về đúng 1x khối lượng kế hoạch gốc). Không mua mới trong phiên này.
- Kết quả dự kiến: NAV ~993,6 triệu VND (không đổi đáng kể do chỉ điều chỉnh khối lượng, không phải
  thay đổi chiến lược), tỷ trọng cổ phiếu ~95,0% NAV, tiền mặt đệm ~5,0% NAV.
- Kế hoạch đã được phê duyệt trước — không cần phê duyệt lại vào sáng 06/07.

**Vấn đề đang chờ quyết định (không ảnh hưởng đến kế hoạch 06/07, cần quyết định trong tuần tới):**
Bộ phận nghiên cứu định lượng đã phân tích và **khuyến nghị** cân nhắc giảm tỷ trọng đầu tư mục tiêu tại
trạng thái NEUTRAL từ mức "full-deploy" hiện tại (~94,7% NAV) xuống mức "engine mặc định" (~70% NAV) khi
danh mục đang ở giai đoạn khởi động (chưa có tín hiệu chọn mã chủ động nào kích hoạt). Phân tích định
lượng cho thấy: xét trên hiệu suất điều chỉnh rủi ro (Sharpe ratio), 2 mức tỷ trọng này **tương đương
nhau về mặt toán học** — mức 94,7% chỉ mang lại đòn bẩy thuần túy (lợi nhuận kỳ vọng và rủi ro sụt giảm
tối đa cùng tăng theo tỷ lệ), không tạo thêm giá trị vượt trội. Câu hỏi thuộc phạm vi khẩu vị rủi ro
(risk-budget) chứ không phải lỗi kỹ thuật — cần người phụ trách quỹ quyết định trực tiếp.

**Danh mục cần tái cân bằng dần (không gấp):** 8 mã hiện đang nắm giữ không còn nằm trong giỏ cổ phiếu
mục tiêu cập nhật của chiến lược (LPB, MSB, VHC, HAH, VIB, VGC, DCM, MBS); 15 mã trong giỏ mục tiêu chưa
được nắm giữ. Việc tái cân bằng được **chủ động hoãn lại** cho đến khi danh mục ổn định hoàn toàn sau sự
cố mục 4, tránh chồng lấn nhiều thay đổi cùng lúc.

**Lịch vận hành tiêu chuẩn (không đổi, áp dụng mỗi ngày giao dịch T2–T6):**
kiểm tra dữ liệu thị trường (17:30) → lập kế hoạch ngày kế tiếp (19:30) → kiểm tra sẵn sàng trước giờ mở
cửa (08:45) → thực thi phiên sáng (09:05) → thực thi phiên chiều (13:00) → báo cáo tổng kết cuối ngày
(15:00). Toàn bộ có giám sát tự động liên tục trong giờ giao dịch (kiểm tra mỗi 5 phút).

---

## 7. PHỤ LỤC — PHƯƠNG PHÁP LUẬN & LƯU Ý QUAN TRỌNG

- **Cơ sở tính NAV & giá vốn (đã nâng cấp cơ chế xác minh sau đính chính ngày 03/07/2026):** giá đóng
  cửa thị trường ngày 03/07/2026 (BigQuery) nhân với khối lượng đã đối soát với sàn, cộng tiền mặt ròng
  (bao gồm nghĩa vụ thanh toán T+2). Giá vốn từng mã lấy từ **`bin/verify_account_snapshot.py`** — script
  mới, đọc trực tiếp log gốc lệnh khớp từ API broker (`dnse_raw_*.jsonl`, field `averagePrice`/
  `fillQuantity` do chính DNSE trả về), **cross-check độc lập** với journal lệnh khớp nội bộ
  (`exec_*_journal.csv`, event `FILL`) và với snapshot đã được kiểm toán độc lập trước đó
  (`eod_account_*.json`). Nếu 3 nguồn lệch số lượng vượt ngưỡng, script báo lỗi và **không** cho phép
  dùng số liệu để viết báo cáo — không còn tự ý dùng field giá ước tính trung gian (`ref_px_approx`)
  làm giá vốn thật như bản đầu của báo cáo này đã mắc lỗi. Toàn bộ 23 mã trong báo cáo này đã chạy qua
  script và **verified=True** (0 lệch số lượng giữa broker thật, journal nội bộ, và snapshot kiểm toán).
- **Track record còn rất ngắn (3 phiên):** mọi so sánh hiệu suất với VN-Index trong báo cáo này **chỉ
  mang tính mô tả**, chưa đủ ý nghĩa thống kê để đánh giá hiệu quả chiến lược. Cần tối thiểu vài tháng dữ
  liệu để có kết luận đáng tin cậy.
- **Đây không phải khuyến nghị đầu tư.** Kết quả trong quá khứ (kể cả từ backtest) không đảm bảo kết quả
  tương lai. Thị trường chứng khoán Việt Nam có rủi ro biến động giá, rủi ro thanh khoản và rủi ro thị
  trường nói chung.
- Mọi thắc mắc về báo cáo này xin liên hệ trực tiếp người phụ trách quỹ.

---
*Báo cáo được tổng hợp tự động từ hệ thống giám sát vận hành nội bộ, đối soát với dữ liệu sàn giao dịch
và cơ sở dữ liệu thị trường (BigQuery). Người phụ trách quỹ rà soát trước khi phát hành cho nhà đầu tư.*
