# DRI r5 — đăng ký trước (viết 03/11/2026, TRƯỚC khi chạy mô hình r5; job Taylor_20261103_160959)

Mù giá: không truy vấn giá DRI khi dựng; khoá md5 (r5/calc/LOCK_md5_r5.txt) TRƯỚC bước thanh khoản + so giá.
Trung thực: các vòng trước đã biết giá (13.400 @03/11); skeptic R4 đã công bố trung bình thực của vài cửa sổ
(2014-01..2026-09 = 2,221; 10 năm trượt = 2,201) TRƯỚC khi đăng ký này được viết ⇒ khoá chỉ chứng minh thứ tự chạy.

## 1. Cửa sổ mức giữa chu kỳ RSS3 (USD 2025/kg, CPI-U) — CHỌN: 2014-01..2026-09
Lý do (nêu trước khi chạy):
- Bắt đầu ở năm trọn đầu tiên SAU đợt siêu chu kỳ cầu 2010–11 và phần đuôi thoái lui 2012–13 (2013 thực ~3,87 vẫn
  thuộc đuôi siêu chu kỳ; bản đọc ngành độc lập nói mẫu hình hiện tại giống đỉnh thời tiết 2016–17/Q4-2024 HƠN siêu
  chu kỳ 2010–11 ⇒ loại cả hai đầu siêu chu kỳ khỏi mức giữa).
- Dùng TOÀN BỘ dữ liệu hậu siêu chu kỳ (153 tháng), gồm ≥2 chu kỳ trọn (đáy 2015–16, 2019–20, 2023; đỉnh 2017, 2021,
  2024) ⇒ không cắt tuỳ ý.
- 10 năm trượt (2016-10..2026-09) bị loại làm tâm vì điểm đầu rơi giữa chu kỳ (sau đáy 2016) và bỏ nhịp giảm
  2014–15 ⇒ ít chu kỳ trọn hơn; báo làm ĐỘ NHẠY, không chọn lại sau khi thấy số.
- Đầu cuối 2026 là đỉnh chu kỳ (Q3 phân vị cao) — giữ vì không có đáy đối xứng sau nó; độ nhạy "năm trọn 2014–2025"
  được báo.

## 2. Lưới (27 ô, trọng số tích) — đối xứng
- mid {P25 thực .25, TB thực .5, P75 thực .25} cùng cửa sổ 2014-01..2026-09 (BỎ "TB 2006–26" — chứa siêu chu kỳ).
- L_tập (đời cạo vườn hiện hữu) {22 .25, 27 .5, 32 .25} — **GIẢ ĐỊNH** (không có định mức nguồn công bố; BCTN thanh
  lý theo chất lượng vườn/mật độ ⇒ đời hiệu dụng có thể ngắn hơn: báo độ nhạy L22/L24).
- r {11,5 .25; 13,5 .5; 15,5 .25}%, neo lãi huy động 12T 7,40%, β=1, độ nhạy ±50/100bp (giữ nguyên r4).
- Thang P10/P25/P50/P75/P90 có trọng số. Tâm = ô (TB, L27, r13,5).

## 3. Base và diễn giải tái canh (luật 20)
- Base = vườn hiện hữu cạo tới hết đời L_tập, KHÔNG thanh lý sớm, tái canh/giai đoạn 2/sầu riêng/liên doanh gỗ = NPV 0,
  phần đã chi (XDCB 72,71 tỷ) cộng giá vốn.
- DIỄN GIẢI (không phải hệ quả cơ học): kế hoạch thanh lý ~3.949 ha "kém hiệu quả" 2029–36 được coi là một phần CỦA
  chương trình tái canh (dự án mới ⇒ NPV 0). Cách đọc khác: thanh lý là quyết định về tài sản HIỆN HỮU (mất sản lượng
  vườn cũ), chỉ phần vốn mới tính giá vốn ⇒ "C-thanh lý" = thanh lý khối, không trồng lại, + XDCB. Báo song song, KHÔNG
  vào base, KHÔNG vào trọng số.
- Kịch bản "tái canh bị buộc, kinh tế cũ" = T1 cũ + XDCB 72,71 tỷ (sửa r4: thiếu XDCB). Xác suất 20% = NHẬN ĐỊNH chủ
  quan, không có cơ sở định lượng ⇒ báo độ nhạy p ∈ {0; 10; 20; 30}%.

## 4. Thanh khoản + nhãn
- Công thức r4 giữ nguyên (luật căn bậc hai, Y 0,5/1/1,5; ADV trung vị 250 phiên tới 02/11/2026 snapshot BQ).
- Báo bảng 1/5/10 tỷ; THAM CHIẾU NHÃN = 5 tỷ (quy ước fleet).
- Ngưỡng trên thang SAU CK 5 tỷ: RẺ ≤ P10; RẺ CÓ ĐIỀU KIỆN P10–P25; HỢP LÝ P25–P75; NGHIÊNG ĐẮT P75–P90; ĐẮT ≥ P90.
- Kiểm thêm luật sổ mức giá (giá đóng cửa < tâm −15%) với tâm sau CK 5 tỷ; ghi đạt/không đạt.
- Giá so sánh: đóng cửa 03/11/2026 (đọc SAU khoá).

## 5. Dữ liệu khoá
Snapshot (md5 trong LOCK): rubber_monthly (bản engine đọc), macro_usdvnd, CPI-U, peers fin; engine r3/r4 đọc file qua
chuyển hướng sang snapshot (không đọc file sống).
