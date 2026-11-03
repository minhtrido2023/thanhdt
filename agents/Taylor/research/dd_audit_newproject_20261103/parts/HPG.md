# HPG — rà soát luật "đầu tư dự án mới" (03/11/2026)

## 1. Tâm/vùng hiện hành
Sổ `kb/dd_price_zones.json` (dd_date 2026-10-31, entry blend): vùng 18.000–22.500, tâm 20.200 (2/3 RI 19.221 + 1/3 EV/EBITDA 5x 22.025).
Nguồn: agents/Taylor/research/dd_HPG_20261031/investor_report/HPG_DD_investor_report_20261031_v3.md; REPORT.md gốc cùng thư mục (dòng 298 tổng hợp tâm).

## 2. Dự án mới/cam kết vốn
- Dung Quất 2 (DQ2): đã lên công suất, hiệu suất HRC 9T quy năm ~81% (REPORT.md:96); KH + lãi vay DQ2 đã vào P&L, lãi vay vốn hoá 1.877 (2025) -> 162 (6T/26) (REPORT.md:98).
- XDCB dở dang 16.113,3 (DQ 11.146,0), cam kết vốn ~19.472 (30/6) (REPORT.md:142); capex 9T 14.607 (REPORT.md:146-147).
- Khác: 1.600 tỷ đặt cọc liên danh Đại lộ cảnh quan sông Hồng (REPORT.md:215-218) — tài sản phải thu dài hạn, không phải khoản trừ trong mô hình.

## 3. Mô hình có trừ giá trị vì dự án không
KHÔNG. `calc/hpg_valuation_v2.py` (dòng 15-28): RI trên BV0 VCSH mẹ 148.795,5 (đã gồm DQ2/XDCB ở giá sổ sách) + đường LNST theo kịch bản; không có dòng "trừ NPV dự án", không trừ capex còn lại/cam kết 19.472. Terminal ROE 11,8% (trung lập) ≈ Ke 11,83% => tăng trưởng trung tính giá trị = NPV 0 (REPORT.md:282). DQ2 xuất hiện chỉ như động lực KỊCH BẢN LN (hấp thụ chi phí cố định, REPORT.md:97; "DQ2 còn ~10pp hiệu suất" là rủi ro lên, REPORT.md:278) — có cơ sở sản lượng/công suất.
Không có khoản CỘNG vô cơ sở liên quan DQ2. Lưu ý không thuộc luật: thuế terminal 20% vs ETR ~12% (do ưu đãi DQ2 không công bố thời hạn, REPORT.md:108-109) là giả định thuế, có nêu nguồn CV 377/TCT-CS; Ke 11,83% (rf 6,75% + β 0,915 × ERP 5,55%) theo khung user, không phải Ke cao khiến NPV âm.

## 4. Phân loại
KHÔNG_VẤN_ĐỀ.

## 5. Hiệu ứng lên tâm khi đặt dự án ở sổ sách/NPV 0
0 đ/cp (0%). Ước lượng: không có khoản trừ dự án nào để gỡ (đọc code hpg_valuation_v2.py + REPORT.md:282); không chạy lại.

## 6. Giá 03/11 vs tâm
Giá 21.250 (close_20261103.md). Tâm gốc 20.200 (+5,2%); tâm điều chỉnh 20.200 (không đổi). Ngưỡng ứng viên 17.170 -> chưa qua, nhãn KHÔNG đổi. Vùng 18.000–22.500: trong vùng, nửa trên.
