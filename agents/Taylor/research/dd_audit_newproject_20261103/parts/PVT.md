# PVT — rà soát luật "đầu tư dự án mới" (03/11/2026)

## 1. Tâm/vùng hiện hành
Sổ (dd_date 2026-10-29): vùng 19.400–21.200, tâm 20.000 (point, ~ước lượng sau đính chính skeptic). Nguồn: kb/projects/pvt-dd-20261029.md; agents/Taylor/research/dd_PVT_20261029/REPORT.md (§7 dòng 154-158, §14 dòng 242-250).

## 2. Dự án mới/cam kết vốn
- 9T/26 mua phương tiện vận tải +979,6 tỷ; capex 9T 947,0; XDCB dở dang chỉ 62,4 tỷ (REPORT.md:69,106,110). Phải trả PVN tiền mua tàu 232,7 (REPORT.md:104).
- Mở rộng đội tàu/phát hành cổ phần xin phê duyệt 05/10 (nguồn calculated_fear_state_backstop.md, ghi ở §14 mục 6 dòng 250; quy mô không có). Bobby: dồn mua tàu trước hết miễn VAT NK 31/12/2026 — "chưa thấy trong 9T", Q4 theo dõi (REPORT.md:110,178,221).

## 3. Mô hình có trừ giá trị vì dự án không
KHÔNG. Định giá = PE × LNST mẹ 2027 theo 3 kịch bản (calc.py:134-144; REPORT.md:154-158); không có dòng NPV/capex mới, vì kế hoạch mở rộng chưa lượng hoá nên không vào mô hình. "KH tàu mua 2025–26 đè lên" (kịch bản xấu) là khấu hao tàu ĐÃ mua, hiệu ứng LN thật, không phải trừ NPV. Không có khoản cộng vô cơ sở liên quan dự án. Tâm 20.000 là ước lượng sau skeptic (REPORT.md:247). Lệch nhẹ ngoài luật: capex thay thế ≈ KH chỉ là ghi chú FCF, không vào FV.

## 4. Phân loại
KHÔNG_VẤN_ĐỀ (lưu ý lỗ hổng: kế hoạch phát hành mở rộng đội tàu 05/10 chưa lượng hoá; theo luật, nếu có thì base = sổ sách/NPV 0, pha loãng là kịch bản).

## 5. Hiệu ứng khi đặt dự án ở sổ sách/NPV 0
0 đ/cp (0%). Ước lượng: không có khoản trừ dự án trong FV (đọc calc.py + REPORT.md §7/§14). Không chạy lại.

## 6. Giá 03/11 vs tâm
Giá 20.800. Tâm gốc 20.000 (+4,0%); tâm điều chỉnh 20.000. Ngưỡng ứng viên 17.000 -> chưa qua, nhãn KHÔNG đổi. Vùng 19.400–21.200: trong vùng, nửa trên.
