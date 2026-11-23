# quant-skeptic — phần A (đo CK holding niêm yết VN) — 23/11/2026
VERDICT: **INCONCLUSIVE** (confidence medium). Tái lập bit-exact; headline 26,63% độc lập khớp. KHÔNG dùng 26,6% làm base HHS; chỉ làm dải độ nhạy.
Lỗi chính:
1. Trung vị cắt ngang trôi một chiều theo ngày đo: 11,8% (31/03) → 20,8% (30/06) → 29,6% (30/09) → 38,3% (20/11). 26,6% là điểm giữa của xu hướng; N hiệu dụng = 6 holding × 1 chế độ thị trường.
2. Giá con không giao dịch vẫn tính là giá thị trường: BBC (phiên cuối 15/01/2026, 34% giá trị niêm yết PAN), LGC (dữ liệu tới 18/06, ADV60=0, 84% giá trị niêm yết CII). Loại giá cũ >10 ngày/ADV60=0 ⇒ CII rớt, N=5, trung vị 28,35% (PAN sát ngưỡng 0,604; PAN rớt ⇒ ~35%).
3. Bẫy BVPS×OShares lệch nhịp quanh đợt phát hành (GEE/GEX 2026Q1, PAN 2026Q1, IPA 2026Q2); PAN 30/06 dùng số CP trước ex. Sửa xong headline vẫn 26,63% (không đổi), nhưng min…max §2 bị nhiễm; câu "tránh bẫy" ở §1 là sai.
4. VCSH mẹ xấp xỉ: thiên lệch hai chiều (E con dùng VCSH tổng gồm thiểu số làm CK lệch xuống), không một chiều như report nói.
5. 3/6 holding sát ngưỡng độ phủ 60%; ngưỡng 70% ⇒ N=3, 18,6%.
6. Mẫu hardcode 17 mã: bỏ im MSN/HAG (raw/kbs_subs có), khớp tên một tầng bỏ sót holding nhiều tầng; GEE (cấu trúc tầng chồng giống TCH→HHS→CRV) không được đo như holding mẹ ⇒ "N=0 tầng chồng" là do thiết kế mẫu.
Khuyến nghị: HHS giữ base 0% hoặc chỉ báo dải độ nhạy có nguồn (~12–42%); không chốt điểm 26,6%. Rerun: bỏ/cờ giá con cũ, sửa số CP/VCSH quý phát hành, thêm GEE+MSN, đo dày theo tháng 2025–2026.
