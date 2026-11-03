# DDV — rà soát luật "đầu tư dự án mới" (03/11/2026)

## 1. Tâm/vùng hiện hành + nguồn
- Sổ `kb/dd_price_zones.json` (dd_date 2026-10-28): tâm **14.500** (expected_weighted), vùng **12.300–17.300**, stress net cash ~12.900 (10.700–15.700).
- source_file: `agents/Taylor/research/dd_DDV_reweight_20261028/REPORT.md` (tái trọng số Bobby). DD gốc: `dd_DDV_20261026/REPORT.md` (tâm ~18.000, đã bị thay).

## 2. Dự án mới / cam kết vốn
- **Có, 1 dự án: MAP 60k t/năm**, capex 9T/26 = 186,4 tỷ, dự kiến xong cuối 2026 (`dd_DDV_20261026/REPORT.md:94`; theo dõi tiến độ dòng 127). Không có dự toán tổng, vốn còn phải chi, IRR/NPV hay WACC nào trong báo cáo (grep không ra).
- Capex 80 tỷ/năm trong DCF (dòng 114) là chi duy trì giả định, không gắn dự án.
- Không có M&A hay mở rộng khác (chỉ Liven Nutrients là khoản phải thu, không phải dự án).

## 3. Mô hình có trừ giá trị vì dự án không
- **KHÔNG trừ.** `dd_DDV_reweight_20261028/model.py`: giá trị = net cash + LN hoạt động × bội số (Bear: net cash − lỗ + 0,72 × book vận hành). Không có dòng NPV/capex dự án nào. Vốn đã chi 186,4 tỷ nằm ngoài net cash (đã ra khỏi tiền) và **không được cộng lại như tài sản** trong Base/Bull (LN 2027 dựng từ DT 5.500 tỷ giả định chạy theo run-rate, không có sản lượng MAP riêng) -> thiên về thận trọng nhẹ, không phải khoản trừ.
- Các khoản giảm ở base (độ dốc biên theo giá lưu huỳnh, trọng số Bear 45%) không liên quan dự án mới; có cơ sở độc lập là chuỗi giá Bobby (`sector_read_fertilizer_dap_20261028.md`) — thuộc luật chu kỳ giá, không thuộc luật này.
- Khoản CỘNG không cơ sở: không thấy khoản cộng nào cho dự án.

## 4. Phân loại: **KHÔNG_VẤN_ĐỀ** (không có khoản trừ do dự án; còn thiếu "cộng tài sản theo giá vốn" cho MAP, thiên thận trọng)

## 5. Hiệu ứng lên tâm khi đặt dự án ở sổ sách
- Không có khoản trừ để gỡ => **0 đ/cp (0%)** theo đúng luật.
- Cận trên nếu cộng MAP theo giá vốn 186,4 tỷ vào mọi kịch bản: 186,4e9 / 146,11e6 cp = **+1.276 đ/cp (+8,8% tâm 14.500)** — **ước lượng**, tính tay; có nguy cơ cộng trùng vì LN 2027 giả định đã dựa trên run-rate toàn công ty. Không chạy lại model.

## 6. Nhãn
- Giá 03/11 15.000 (`close_20261103.md`) vs tâm gốc 14.500 (+3,4%, TRONG vùng) vs tâm điều chỉnh: 14.500 (không đổi); cận trên ước lượng 15.776 -> giá = 0,95 × tâm cận trên. Ngưỡng ứng viên (≤ tâm × 0,85 = 12.325): **không đổi nhãn** ở cả hai.
