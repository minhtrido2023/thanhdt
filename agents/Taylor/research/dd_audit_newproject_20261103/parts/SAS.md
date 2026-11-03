# SAS — rà soát luật "đầu tư dự án mới" (03/11/2026)

## 1. Tâm/vùng hiện hành + nguồn
- Sổ (dd_date 2026-10-26): tâm **32.600** (expected_weighted), vùng null.
- source_file: `agents/Taylor/research/dd_SAS_20261026/REPORT.md` (calc `src/val.py`, `src/val_out.txt`).

## 2. Dự án mới / cam kết vốn
- **Không có dự án đầu tư/capex/M&A do SASCO cam kết.** grep (dự án, đầu tư, capex, mở rộng, nhà máy, M&A, NPV, IRR, WACC): chỉ ra Long Thành (REPORT.md:18-20, 69-80) = sự kiện **chuyển chuyến bay quốc tế TSN->Long Thành 2027–2028** (rủi ro ngoại sinh, quyết định Cục HK) và **đấu thầu suất kinh doanh** ở Long Thành, SASCO "đã chuẩn bị hồ sơ", chưa có gói thầu chính thức (dòng 75-76). "Đầu tư" còn lại là cổ tức từ khoản đầu tư tài chính (dòng 91).
- Không có vốn dự án nào để đặt ở sổ sách.

## 3. Mô hình có trừ giá trị vì dự án không
- Không có khoản trừ vì dự án. Có **giảm LN từ 2028 theo kịch bản** (`src/val.py`): Base −25% (45%), Bear −50% (30%), Bull +5% (25%), r=14%, + 3.500 đ/cp tiền thừa. Cơ sở: lịch chuyển chuyến bay của Cục HK (dòng 70-73) và lời SASCO tự nhận thị phần thấp hơn ở TSN (dòng 76) — có nguồn cho CHIỀU, **không có nguồn cho độ lớn** −25%/−50% (tự đặt, ghi "xác suất chủ quan"). Là kịch bản có xác suất, đúng cách luật cho phép (rủi ro (−) cụ thể quan sát được), không phải NPV âm mặc định của dự án.
- Khoản cộng không cơ sở: 3.500 đ/cp "~50% của 945 tỷ" là ước lượng tự gán, không phải dự án.

## 4. Phân loại: **KHÔNG_VẤN_ĐỀ** (không áp dụng luật dự án mới). Lưu ý riêng: độ lớn haircut Long Thành chưa có dữ liệu độc lập.

## 5. Hiệu ứng
- Dự án ở sổ sách: **0 đ/cp (0%)** — không có khoản dự án để gỡ.
- Tham khảo (không phải theo luật): chạy `val` với Base không haircut (LN 650 giữ nguyên) cho Base 41.569 và tâm ~36.425 (+11,8%) — **đã chạy lại bằng bản sao công thức `src/val.py`** (python3 tại /tmp), chỉ là độ nhạy cho thấy tâm phụ thuộc haircut tự đặt; KHÔNG dùng để sửa tâm vì có cơ sở (Cục HK, lời SASCO).

## 6. Nhãn
- Giá 03/11 **34.900** vs tâm 32.600 (+7,1%; vùng null). Tâm không đổi => nhãn không đổi; ngưỡng ứng viên ≤ 27.710: không qua. (Độ nhạy 36.425: giá = 0,96 × tâm, vẫn không qua.) Cờ sổ: free float ≈4,4%, ADV 1,58 tỷ.
