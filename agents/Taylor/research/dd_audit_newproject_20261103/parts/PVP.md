# PVP — rà soát luật "đầu tư dự án mới" (03/11/2026)

## 1. Tâm/vùng hiện hành
Sổ (dd_date 2026-10-29): vùng 15.500–22.400, KHÔNG có tâm (dải nối P/B trung vị lịch sử 15.545 -> SOTP kỳ vọng PP-B 22.387). Nguồn: agents/Taylor/research/dd_PVP_20261029/investor_report/PVP_DD_investor_report_20261029.md; REPORT.md gốc (dòng 169-190).

## 2. Dự án mới/cam kết vốn
ĐHĐCĐ 23/06/2026 duyệt mua 2 dự án tàu: Aframax #2 56,5 tr USD (VCSH 17,08/vay 39,42) và Aframax #3 hoặc 2 tàu MR1/MR2 59,5 tr USD; tổng 116 tr USD ≈ 3.021 tỷ = 1,55x vốn hoá, VCSH 916 tỷ, vay 2.104 (REPORT.md:42,102). Chưa ký; ĐHĐCĐ bất thường ≤30/11. Báo cáo khả thi công ty cho #2: NPV dự án +43.719 USD (≈0), IRR 7,67% < IRRmin 11%, NPV vốn CSH +2,24 tr USD (REPORT.md:103-106). Dự báo TC 1 năm 43,8k (2027)/39,4k (2028) > giả định dự án 30.240 USD/ngày.

## 3. Mô hình có trừ giá trị vì dự án không
CÓ, và không có cơ sở độc lập. calc.py:~148-153 (`loss = {xau 0,30; co so 0,10; tot 0}`, "thiệt hại mua ở đỉnh giá tàu cũ (ước lượng)"): NPV mua đắt = -30%/-10%/0 × giá tàu kỳ vọng 2.025 tỷ => -608/-203/0 tỷ, đưa vào PP-B ("ships_new") và PP-A (REPORT.md:163-169). Chính báo cáo ghi "mua đắt -10%... thận trọng hơn mô hình công ty (nhận định của nhóm)" (REPORT.md:107) => giả định tự đặt, đúng loại luật cấm; công ty tự tính NPV ≈ 0, chi phí vốn đã nằm trong khả thi. Cùng nhóm: "sàn sau capex" coi 916 tỷ VCSH bỏ vào = 0 (REPORT.md:185) — là sàn stress, không phải tâm, nhưng vẫn là cách xử lý "vừa chi vừa mất". Không có khoản cộng vô cơ sở. Phần hợp lệ giữ nguyên: rủi ro giá tàu như kịch bản có xác suất / điều kiện đổi nhận định (REPORT.md:241), không nhét vào base.

## 4. Phân loại
ĐÁNG_KỂ: +14,4% trên cận trên dải (PP-B 22.387); +8,5% trên điểm giữa dải (không có tâm chính thức).

## 5. Hiệu ứng khi đặt dự án ở NPV 0
Đã chạy lại bản copy: calc/PVP/calc_npv0.py (loss=0 mọi kịch bản; kết quả calc/PVP/out_npv0.txt, PYTHONHASHSEED=0, python3 -I, rc=0).
- PP-B kỳ vọng 22.387 -> 25.610 (+3.223 đ/cp, +14,4%); kịch bản xấu/cơ sở/tốt 15.701/24.428/34.095 -> 21.559/26.381/34.095.
- PP-A 8.115 -> 11.337 (không dùng làm cận dải).
- Cận dưới P/B 15.545 không đổi => dải điều chỉnh 15.500–25.600; điểm giữa 18.966 -> 20.578.
- Sàn sau capex 4,7–6,1k không tính lại (ước lượng: với tàu ở sổ sách sàn ≈ sàn trước capex 13,6–14,9k, vì cash chuyển thành tàu ở giá vốn).

## 6. Giá 03/11 vs tâm
Giá 17.800. Không có tâm; vị trí trong dải: gốc 33% (nửa dưới), điều chỉnh 22%. Nếu lấy điểm giữa dải làm tâm: ngưỡng 0,85 = 16.121 (gốc) -> 17.491 (điều chỉnh); giá 17.800 vẫn cao hơn 1,8% => nhãn KHÔNG đổi qua ngưỡng ứng viên. (Nếu lấy PP-B làm tâm thì giá đã dưới ngưỡng ở cả hai bản: 19.029 và 21.769 — nhưng sổ không đặt tâm.) PVP vẫn NON ngoài §2.5.
