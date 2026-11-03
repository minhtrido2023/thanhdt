# DRI — rà soát luật "đầu tư dự án mới" (03/11/2026)

## 1. Tâm/vùng hiện hành + nguồn
- Sổ (dd_date 2026-10-30): tâm **10.500** (expected_weighted, 25/50/25), vùng cơ sở **9.100–11.100**; kịch bản hoãn tái canh 13.225–15.115.
- source_file: `agents/Taylor/research/dd_DRI_20261027/investor_report_v3/DRI_DD_investor_report_20261030_v3.md`; REPORT gốc `dd_DRI_20261027/REPORT.md`, `REPORT_Q3_UPDATE.md`.

## 2. Dự án mới / cam kết vốn
- **Chương trình tái canh 4.081,64 ha** (NQ 01/2025 HĐQT đã giao dự án): trồng 94,56 ha 2025, 37,77 ha kế hoạch 2026; thanh lý chờ liên doanh nhà máy gỗ (md:111). Thêm ~4.216 ha giai đoạn 2 chưa có kế hoạch. Capex mô hình 172,6 tr đ/ha (md:236). Dự án sầu riêng, cà phê liên kết (md:169, 322) nhỏ, không vào định giá.
- Không có dự toán và lịch theo năm của công ty (md:440 "capex/ha suy từ chi phí chăm sóc KTCB bình quân, không phải dự toán trồng mới").

## 3. Mô hình có trừ giá trị vì dự án không
- **CÓ, đây là trục quyết định của base.** md:249: "Tái canh làm giảm giá trị trong mô hình: biên mỗi ha cây mới (~18,5 tr đ/ha/năm) không trả nổi capex 172,6 tr đ/ha. Cả chương trình thanh lý + trồng lại làm giá trị giảm ~**4,0 nghìn đ/cp**"; giai đoạn 2 còn −1,3…−1,5 nghìn (md:250). Kịch bản cơ sở (50%) = "tái canh đúng kế hoạch" = 9.078–11.116 (md:286). Bảng md:256-261: không tái canh 13.096 / 15.172.
- **Cơ sở độc lập: KHÔNG.** Chính báo cáo ghi các giả định "chưa có nguồn": đời cạo, capex/ha, lịch thanh lý, năng suất cây mới, giá gỗ (md:265, 440, 443). Capex/ha là 7 năm × chi phí chăm sóc, không phải dự toán; năng suất cây mới 1,9 t/ha giả định. Ban lãnh đạo giao dự án tái canh => theo luật phải kỳ vọng IRR ≥ chi phí vốn. Chiết khấu thực 8,74% (≈12% danh nghĩa, md:236) là tham số tự chọn, không phải dữ liệu thị trường của dự án.
- Còn lại: yếu tố (−) cụ thể có thật (hợp đồng tô nhượng ràng buộc, "phải thanh lý sớm do không đảm bảo mật độ") là lý do để tái canh bắt buộc, nhưng không chứng minh NPV âm.
- Khoản cộng không cơ sở: không thấy; kịch bản "hoãn tái canh" chỉ là nhánh tích cực 25%.

## 4. Phân loại: **NGHIÊM_TRỌNG** (>15% tâm, ước lượng ~+30%)

## 5. Hiệu ứng khi tái canh = sổ sách/NPV 0
- Điểm cố định đo trong báo cáo: bỏ phần giảm 4,0 nghìn của chương trình => Cơ sở 9.078–11.116 -> **~13.100–15.200** (bảng md:259 cho "không tái canh" 13.096 / 15.172; khớp 9.078 + ~4.000). Kịch bản tích cực (đã là không tái canh) giữ 13.225–15.115. Kịch bản tiêu cực (tái canh nhanh, trừ nặng hơn: nhanh 7.903 vs trung bình 9.078 tại mid 1,97) -> ước lượng ~12.100–13.300 (6.920–8.058 + ~5.200).
- Tâm kỳ vọng: 0,25 × 14.170 + 0,50 × 14.134 + 0,25 × ~12.650 = **~13.800; khoảng 13.600–13.800 -> chênh ~+3.100…+3.300 đ/cp (~+30%) so với 10.500**. **Ước lượng**: tính tay từ các bảng trong báo cáo, mã định giá r4 không nằm trong thư mục (model.py / model_q3.py là bản trước/phụ), không chạy lại được. Không lẫn tăng giá cao su.
- Lưu ý: chưa rõ phần nào của chương trình là nghĩa vụ tô nhượng (nếu bắt buộc thì NPV âm có thể thật) — cần đọc hợp đồng 2004; hiện báo cáo không có văn bản.

## 6. Nhãn
- Giá 03/11 **13.400** (`close_20261103.md`) vs tâm gốc 10.500 (+27,6%, TRÊN vùng cơ sở; vùng hoãn tái canh 13,2–15,1k).
- Tâm điều chỉnh ~13.700: giá = ~0,98 × tâm (−2%); vùng cơ sở điều chỉnh ~13,1–15,2k => **TRONG vùng**, không còn "TRÊN vùng". Ngưỡng ứng viên (giá ≤ tâm × 0,85 = ~11.650): **không qua** (13.400 > 11.650) — nhãn thay đổi từ "TRÊN vùng/đắt" sang "ngang tâm", vẫn không phải ứng viên.
