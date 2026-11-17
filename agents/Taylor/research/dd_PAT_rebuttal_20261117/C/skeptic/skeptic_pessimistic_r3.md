# PAT r3: phản biện BI QUAN (stateless, mù giá thị trường), 17/11/2026

Phạm vi: chỉ cố chứng minh tâm r3 (66.864 đ/cp) quá CAO. Đã đọc: RULES.md, C/VALUATION_r3.md, C/assumptions_objective_r3.md, C/calc_r3/*, A/A1, A/A2 (qua trích dẫn r3), A/A3, factpack F2/F3/F4, blind_val inputs (facts_extracted, sector_read, ảnh BCTC q326 p05/p06/p07/p29). Không đọc tệp bị cấm. Không thu thập hay nhắc giá cổ phiếu, P/E, vốn hoá hay mục tiêu giá.
Cách tính lại: chạy `calc_r3/model_r3.py` (import, không sửa tệp), chỉ thay tham số/hàm `ebit` trong bộ nhớ, chạy ngoài thư mục với `PYTHONDONTWRITEBYTECODE=1`. Đường tái lập r3 cho đúng **66.864**, khớp `model_out_r3.json`.

## VERDICT
- **r3: REFUTED (quá cao)**, độ tin cậy **trung bình**. Hướng lệch thì rõ. Độ lớn phụ thuộc vào 2 nút phán đoán (C4, C6).
- **Tâm bi quan hiệu chỉnh: ≈ 57.500 đ/cp** (khoảng tâm **54.300 – 59.500**), thấp hơn r3 khoảng 11–19%.
  - Chỉ tính các thay đổi có bằng chứng cứng (C1 dữ kiện BCTC, C2 nhất quán nội bộ, C3 bằng chứng F3/A1, C5 bằng chứng A1): **59.500**. Riêng phần này đã lệch −7.350, vượt mức "không thay đổi nào vượt ±5.000" mà r3 tự tuyên bố. Lý do: các thay đổi nhỏ cùng chiều cộng dồn lại.
  - Thêm C4 (P(A) 0,35): **57.500** (tâm đề xuất). Thêm C6 (trọng số nút T): **54.300** (cận dưới của khoảng tâm).
- Phân vị cây khi xếp chồng C1–C6 (q_B 0,25, λ giữ nguyên): P10 16.100 · P25 42.000 · P50 54.100 · P75 65.900 · P90 83.500. Tâm r3 66.864 nằm gần P75 của cây bi quan.
- Không thay đổi: TX 0,97, điện 0,985 × F5, tiền ròng 357,35, Q4/2026 FCFE, r/g. Đã kiểm, không thấy lạc quan sai đáng kể.

## Danh sách lỗi theo mức nghiêm trọng
| # | Mức | Lỗi | Tác động một-lần-một trên r3 (đ/cp) |
|---|---|---|---|
| E1 | CAO | (3b) +4.871 là thay đổi mô hình KHÔNG có bằng chứng mới. Cách sửa mâu thuẫn được chọn là phía làm giá trị TĂNG mạnh nhất. Hazard hằng ngoại suy từ một điểm duy nhất (F7) ngụ ý P(B giải trước cuối 2030) = 0,934. Sự kiện "3 nhà máy VAPC ≥80%" không phải là "PAT được tiếp cận quặng giá nội địa" | C3: −2.496 (q_B 0,25, λ hiệu chỉnh lại theo F7) … −4.112 (q_B 0,40) |
| E2 | CAO | Nhánh giữa nút P = 1,0 không nhất quán với độ co giãn mà chính hai nhánh đuôi ngụ ý (≈0,25). Trung vị Bobby F2 thấp hơn TB 9T/26 khoảng 10% mà ánh xạ ra 0 thay đổi | C2: −2.915 |
| E3 | TRUNG BÌNH (lỗi dữ kiện/hiệu chỉnh) | Tỷ lệ cước vận chuyển/DT xuất khẩu lấy theo FY2025 (3,85%). 9T/2026 là 4,69% (ảnh p29). Khung mô hình vì thế thổi EBIT nền quy năm 9T lên 281,6 so với thực tế 274,1 | C1: −1.382 |
| E4 | TRUNG BÌNH (phán đoán) | Nút T: 35% xác suất cho việc DLC (mua chi phối 51%) tự gánh bước thuế cho PAT, mà không có bằng chứng nào. Bằng chứng 2026 lại cho thấy PAT không hưởng phần giá tăng khi bán qua DLC | C6: −3.225 (0,80/0,15/0,05) |
| E5 | TRUNG BÌNH (phán đoán) | P(A) = 0,50 "trung tính" cho giấy phép KT25 hết hạn khoảng cuối 2026, đang bị điều tra tội khai thác trái phép, xin gia hạn chưa có kết quả | C4: −2.129 (0,35); −2.839 (0,30) |
| E6 | THẤP–TB | Khối lượng: nguồn Ai Cập chỉ tới hết Q1/2027, chưa có hợp đồng thay thế, UBND ghi nhận PAT thiếu nguyên liệu. Base vẫn giữ 100% | C5: −602 (−15% H2/2027) |
| E7 | THẤP–TB (không xếp chồng) | Nút D 0,5/0,5 đối xứng, trong khi tự khai thác từng chiếm ">80% nhu cầu" (SHS, F3 dòng 69) | D(A) 0,7: −1.745 |
| E8 | THẤP–TB (không xếp chồng) | Cốc 2028+ hồi về 1.825 (TB 2023+) là xác định, không có dự báo nào. Lịch sử cho thấy cốc đồng pha với P4/biên (F4: r +0,74), nhưng mô hình coi cốc và P độc lập | cốc giữ 2.108 mãi: −6.224; cốc 2.000: −3.849 |
| E9 | THẤP (trình bày) | VALUATION_r3 dòng 17 ghi "+4.871 (bước (3a)+(3b) gộp)". Thực ra số gỡ một-lần-một 61.994 → 66.864 chỉ là (3b). (3a)+(3b) = +4.317 | 0 |

## Đòn 1: Lỗi dữ kiện/số trong r3 (đối chiếu ảnh BCTC và factpack)
| Số r3 dùng | Nguồn kiểm | Kết quả |
|---|---|---|
| Tiền 1,246 | png_q326/p05, mã 110: 1.245.735.826 | KHỚP |
| HTM ngắn hạn 558,069 | p05, mã 123: 558.068.580.803 | KHỚP |
| Vay ngắn hạn 67,218 | p06, mã 321: 67.217.555.923 | KHỚP |
| Quỹ KT-PL 76,690 | p06, mã 323: 76.689.866.077 | KHỚP |
| Tiền ròng gốc 415,407; trừ cầm cố điện 45,11; trừ KT-PL 9T 12,94 ⇒ 357,35 | tự tính lại | KHỚP. Ghi chú: "phải trả ngắn hạn khác" 1,63 (p06 mã 320) không bị trừ, ≈ −65 đ/cp, không đáng kể |
| DT 9T 1.379,304; Q3 440,032; GP Q3 63,604; CPBH Q3 5,049; QLDN Q3 4,711; LNST 9T 215,713 | p07 | KHỚP. EBIT Q3 = 53,844 |
| EBIT H1/26 151,717 | F4 §2 (186,994 − 27,239 − 8,038) | KHỚP |
| GVHB thành phẩm 9T 1.116,065 | p29 TM22 | KHỚP (DT TP 1.366,52 lấy theo facts_extracted, chưa mở lại ảnh TM DT) |
| **Cước: 3,85% × s_exp × DT** | p29 TM25: vận chuyển 9T/26 = 22,844; DT nước ngoài 9T/26 = 487,508 ⇒ **4,69%**. 3,85% = FY2025 66,866/1.738,334 (F2 dòng 75). H1/26 18,182/428,111 = 4,25%; 9T/25 49,575/1.183,32 = 4,19% | **LỆCH**. Hằng số lấy từ năm cũ. Xu hướng 2025 → 2026 là tăng. Tại s_exp 9T (0,353), khung r3 cho EBIT quy năm 281,6 so với thực tế 274,1 (sai 7,5 tỷ/năm). Với 4,69%: 276,2 (sai 2,1) |
| Hoa hồng 6,3; QLDN 17; khác 5 | p29: hoa hồng 9T 6,297 (toàn bộ ở H1); FY25 6,438; QLDN 9T 12,75 ⇒ 17/năm; khác 9T 3,148 ⇒ 4,2/năm | KHỚP (mục "khác" hơi thận trọng, +0,8) |
| 63,7% DT bán DLC; 85,5% Q3 | facts_extracted (878,14/1.379,30; 376,29/440,03) | KHỚP số học (ảnh bên liên quan chưa mở lại) |
| Thuế XNK/DT nước ngoài 10,59% (9T/26); 5,10% (FY25) | 51,610/487,508; 88,627/1.738,334 | KHỚP số học |
| s_exp 35,3% (9T), 13,5% (Q3) | 487,508/1.379,304; 59,397/440,032 | KHỚP |
| GPM Q1 13,6% / Q2 25,0% / Q3 14,5% | F4: Q1 = 186,994 − 129,4 = 57,59 / 421,9; Q2 129,4 / 517,4 | KHỚP |
| NVL GĐ1 48,64% | F2/A3: NVL theo yếu tố H1/26 = 709,27 − 253,09 = 456,18 / 939,27 = 48,57% | KHỚP (xấp xỉ) |
| NVL GĐ2 55,20% | NVL yếu tố Q3 253,091/440,032 = 57,5%. Q3 sản xuất > tiêu thụ (TP +16,65) nên NVL trong GVHB nhỏ hơn | Hợp lý, không kiểm chính xác được (hệ số gốc nằm trong tệp r2 bị cấm đọc) |
| Cốc T11 2.108; cốc 9T ≈ 1.700 | sector_read dòng 35; F4 H1 1.541 / Q3 2.040 | KHỚP |
| P4 TB 9T ≈ 27.740 | F4: H1 27.835, Q3 27.606 ⇒ 27.760 | KHỚP (lệch 0,07%) |
| Bobby F2: trung vị 25.000; P(<23k) = 0,32; P(>32k) = 0,10 | sector_read dòng 136 | KHỚP |
| λ = 0,054874; P_B(13,5 tháng) = 0,523 | tự tính | KHỚP |
| KH LNST 2026 280 ⇒ Q4 ≈ 64,3; 2026E EBIT 259,4 | tự tính | KHỚP |
| Định mức cốc 1,37 t/t | sector_read: 1,4–1,6 [NỀN] | Thấp hơn nguồn ngành. Chiều tác động: làm NHỎ lợi ích hồi cốc 2028 ⇒ không phải lỗi lạc quan |
| Mức cắt điện 0,727 × bình quân | A3 §1.3 | Không kiểm lại nguồn gốc. Tác động nhỏ (±700) |

## Đòn 2: Lỗi logic cây kịch bản / xác suất
1. **(3b) +4.871 đảo nguyên tắc tự đặt của r3.** assumptions_r3 dòng 4 ghi: "quyết định nào KHÔNG có bằng chứng mới thì GIỮ". Chính dòng 32 thừa nhận về B: "không có tin sau 14/11 làm đổi". Vậy mà (3b) vẫn đổi cấu trúc và cho thay đổi lớn nhất của vòng (+4.871, lớn hơn tổng các thay đổi có bằng chứng −2.188). Mâu thuẫn r2 (hazard hằng để suy ra 0,55 nhưng lại cắt ở 2028) có ít nhất 3 cách sửa nhất quán:
   - (i) hazard hằng mãi mãi (r3 chọn): +4.871.
   - (ii) mô hình "khỏi bệnh" (cure) có khối vĩnh viễn q_B, với λ HIỆU CHỈNH LẠI để vẫn khớp F7 (P đến 31/05/2027 = 0,30): q = 0,25 ⇒ 64.369; q = 0,40 ⇒ 62.752.
   - (iii) hazard giảm dần theo thời gian (độ trễ hành chính/pháp lý điển hình): giá trị nằm giữa (i) và (ii).
   r3 chọn đúng đầu cao nhất. Lưu ý thêm: độ nhạy "q_B 0,25 → 64.000" của r3 giữ nguyên λ nên P(tới 31/05/2027) chỉ còn 0,225, không khớp F7. Bản hiệu chỉnh đúng ra 64.369, tức tác động −2.496 chứ không phải −2.865 (tôi dùng con số đúng, có lợi cho r3).
2. **Biến cố F7 khác biến cố mà mô hình cần.** F7 đo "3 nhà máy tuyển VAPC ≥80% công suất". Mô hình lại dùng nó cho "chi phí quặng của PAT về O2 khi D = B". Bằng chứng cho thấy hai việc này tách rời:
   - Lãnh đạo VAPC: nguồn theo giấy phép hiện hành "khó có thể đáp ứng đầy đủ nhu cầu của các đơn vị trong Tập đoàn đến năm 2030"; chất lượng quặng giảm hằng năm (F3 dòng 26, The Investor/Nhà Đầu Tư 19/03/2026).
   - Khoảng 50% doanh thu VAPC là các đơn vị phân bón Vinachem (cùng nguồn).
   - Báo 06/10 và 20/10 về gỡ khó cho VAPC không nhắc DGC/PAT là khách hàng. VAPC cũng thiếu quặng nên DGC "cạnh tranh cùng nguồn khan hiếm" (A1 dòng 74).
   - Mỏ Cóc 1 chỉ đủ đến hết 11/2026. 3,53 triệu tấn chưa có quyết định cho khai thác hay bán (A1 dòng 49–50).
   r3 bác bỏ bằng chứng này với lý do nó "nói về độ đủ, không phải 3 nhà máy có chạy lại". Nhưng với giá trị của PAT, độ đủ/quyền tiếp cận mới là biến số quyết định. Đây là lỗi lập luận. ⇒ Cần có khối vĩnh viễn q_B > 0.
3. **Ánh xạ nút P bậc thang không nhất quán.** Khớp lognormal với F2 (σ = 0,168; trung vị 25.000), so với TB 9T 27.740:
   - Đuôi dưới (<23k, p ≈ 0,31) có trung bình có điều kiện 20.730, tức 0,747 ⇒ r3 ánh xạ 0,937 ⇒ độ co giãn 0,249.
   - Đuôi trên (>32k) có trung bình 34.541, tức 1,245 ⇒ 1,063 ⇒ độ co giãn 0,257.
   - Nhánh giữa (23–32k) có trung bình 26.617, tức 0,9595. Với độ co giãn 0,25 thì phải ánh xạ ra **0,990**, không phải 1,0.
   Dùng "độ dính giá" cho riêng nhánh giữa mà không cho hai đuôi là tuỳ tiện. (Độ nhạy 0,977 của r3 dùng độ co giãn 0,33, tôi KHÔNG dùng con số đó vì nó quá bi quan so với chính các đuôi.) Tác động −2.915.
4. **Độc lập giữa cốc (xác định) và P (ngẫu nhiên).** F4 cho GPM ~ cốc r = +0,74, đồng pha chu kỳ. Hồi cốc về 1.825 trong thực tế thường đi cùng P4 hồi xuống. Phần lợi từ hồi cốc lẽ ra phải đi kèm một phần nhánh P thấp. C2 xử lý một phần. Không xếp chồng thêm để tránh đếm hai lần.
5. **Nút D đối xứng 0,5/0,5.** Theo SHS (F3 dòng 69), tự khai thác (A) từng chiếm ">80% nhu cầu". Nếu nguyên nhân quyết định chi phí nghiêng về A (0,7) ⇒ −1.745. Đây là số của CTCK, chưa có nguồn sơ cấp ⇒ chỉ đưa vào độ nhạy.
6. **Không thấy đếm hai lần** giữa TX/T (f chỉ áp khi TX15), hay giữa điện và DV. Tổng xác suất lá = 1. Tái lập tâm r3 ra 66.864.

## Đòn 3: Nút lạc quan thiếu bằng chứng
- **Giá DLC trả PAT (nút T + netback):**
  - Không có nguyên tắc giá (#N12, đã thử hơn 6 truy vấn).
  - Bằng chứng 2026 nghiêng bất lợi cho PAT, nhất quán với cách hiểu "bán DLC thấp hơn thị trường" (cách hiểu kia, chi phí tăng, cũng chưa loại được):
    - DT/DV mua ngoài (proxy đơn giá trên một đơn vị sản xuất): H1/26 −9,3% YoY, Q3/26 +0,2% YoY, trong khi P4 +18–22% (A3 §3.2(iv)).
    - Q1/26 DN nói "giá bán phốt pho vàng không có biến động nhiều" trong khi giá vốn +14% (A3 §3.2(iii)).
    - Khoảng cách YoY giữa DT và P4: Q1 −7,3pt, Q2 −24,1pt, Q3 −35,4pt.
  - Bên mua chi phối (DLC 51%) có động cơ tối đa hoá phần lợi 100% của mình. Cách hiểu "DLC tự chia khoản lợi FTA/thuế cho PAT" (T_b + T_c = 0,35) không có bằng chứng ủng hộ.
  - Đề xuất T_a 0,80 / T_b 0,15 / T_c 0,05 (−3.225). Không thêm nhánh "dưới netback" vào tâm vì không định lượng được. Độ nhạy −5% trên 65% DT ⇒ 50.700 (r3).
- **Truyền giá TQ → PAT:** đối xứng với ý trên. Nếu 2026 PAT không hưởng phần giá tăng, mô hình không có cơ sở giả định PAT được che chắn khi giá giảm. C2 chỉ sửa phần nhất quán nội bộ, không thêm nhánh xấu.
- **Mỏ DGC (A) P = 0,5:**
  - Giấy phép KT25 "chỉ được cấp phép đến hết năm 2026" (SHS/VietTimes; Vietnambiz ghi 6 năm từ 2021).
  - Tội danh liên quan khai thác tài nguyên. DGC xin gia hạn nhưng chưa có kết quả. 29/10 vẫn "chưa có thời điểm" (A1 dòng 39, 48).
  - Không bằng chứng nào nghiêng về phía được phép lại. "Trung tính 0,5" là lạc quan trong bối cảnh giấy phép hết hạn giữa lúc đang điều tra ⇒ 0,35 (phán đoán, tin cậy thấp–trung bình).
- **Tiền ròng:** không lạc quan.
  - VLĐ 30/09 (PT 15,8 + HTK 120,2 − PTNB 35,7 − KH trả trước 12,9) cao hơn 31/12/25, nên chuẩn hoá còn giải phóng tiền.
  - 70 tỷ cầm cố điện đã trừ PV 45,11.
  - Cầm cố chéo 40 tỷ + 100.000 USD cho "các công ty thành viên" (−42,6 ⇒ 65.100) vẫn là WARNING. Hợp lý, vì dư nợ của bên thứ ba không công bố.
- **Cốc dài hạn / "cốc TB 2023+" (r2 khoảng +7.000):**
  - 1.825 là TB nhiều năm (F4 quý 2023–2026: 1.341–2.492). Con số này CAO hơn TB 2026 (≈1.750), nên tự nó không lạc quan so với lịch sử.
  - Nó chỉ lạc quan so với spot T11 (2.108) và SMM 23/10 (2.200).
  - Không tìm được dự báo nào. Giữ 2.108 mãi thì −6.224.
  - Đây là nút lớn nhất CHƯA xếp chồng. Tôi không xếp chồng vì hồi về trung bình là giả định mặc định có thể bảo vệ được với hàng hoá, và vì E8/C2 chồng lấn.
- **Ai Cập hết Q1/2027:** C5 −15% sản lượng H2/2027 (−602). Mô hình chỉ cho vol27 ảnh hưởng nửa năm 2027. Nếu thiếu kéo dài sang 2028 thì không có trong cây. Không định lượng được vì không có tấn/hợp đồng ⇒ WARNING.
- **Phạt / truy thu / chuyển giá / ưu đãi thuế:**
  - Kiểm toán ngoại trừ BN26 vì "nghĩa vụ phải trả, dự phòng" (facts_extracted dòng 49).
  - 2025 có truy thu thuế 6,79.
  - Ưu đãi TNDN 5% đến 2030 gắn với dự án P4.
  - Hoàn nguyên đất thuê không trích lập.
  Theo luật user (vụ án chỉ WARNING, không bake vào base), tôi KHÔNG bake. Độ nhạy một lần −50 tỷ ⇒ −2.000 đ/cp (r3: 64.900). Nếu mất ưu đãi (thuế 20% từ 2027), giá trị giảm thêm đáng kể. Không tính vì không có căn cứ ngoài vụ án.

## Đòn 4: Tâm bi quan hiệu chỉnh: thay đổi cụ thể và cách tính lại
Phương pháp: import `calc_r3/model_r3.py`. Thay `ebit` (hệ số cước), `PP`, `PT`, `pA`, `q_perm` với λ hiệu chỉnh lại theo F7 (λ' = −ln(1 − 0,30/(1 − q))/6,5), và `vol27`. Cộng dồn theo thứ tự cố định:

| Bước | Thay đổi | Bằng chứng | Tâm | Δ |
|---|---|---|---|---|
| r3 | | | 66.864 | |
| C1 | cước 3,85% → 4,69% DT XK | p29 TM25 + p07 (9T/26) | 65.483 | −1.382 |
| C2 | nhánh giữa P 1,0 → 0,990 | độ co giãn mà chính đuôi r3 ngụ ý (0,25) + F2 | ≈62.570 | ≈ −2.900 |
| C3 | B: khối vĩnh viễn q_B 0,25, λ' = 0,0786 (khớp F7) | F3 dòng 26 (VAPC thiếu tới 2030), A1 dòng 49–50, 74 | — | ≈ −2.500 |
| C5 | sản lượng H2/2027 −15% | A1 §C2 (Ai Cập tới Q1/27), §C5 (UBND: thiếu NVL) | **59.516** | (C1+C2+C3+C5) |
| C4 | P(A) 0,5 → 0,35 | A1 dòng 39, 48 (giấy phép hết 2026, chưa gia hạn, đang điều tra) | **57.522** | −1.994 |
| C6 | T 0,65/0,25/0,10 → 0,80/0,15/0,05 | #N12 + A3 §3.2 (PAT không hưởng phần giá tăng 2026 khi bán qua DLC) | **54.305** | −3.217 |

Biến thể: q_B 0,40 (λ' 0,1066) ⇒ C1–C5 = 55.991; C1–C6 = 52.774. Thêm D(A) 0,7 ⇒ thêm khoảng −1.700. Cốc 2.108 mãi ⇒ thêm khoảng −6.000 (không đề xuất làm tâm).
**Tâm đề xuất 57.500; khoảng tâm 54.300 – 59.500.**

## Phần r3 ĐÚNG/vững (bằng chứng phía ngược lại, để công bằng)
- TX 0,97: A2 xác nhận dự thảo không có P4. Không có nhánh "tăng hơn 15%". Đúng.
- "LN lõi 2027 < 2026": cầu EBIT 283 → 109 có văn bản (thuế) và dữ liệu (cốc). Vững.
- Điện: đã sửa mức cắt bình quân sang mức cho nhóm sản xuất, theo chiều giảm giá trị. Đúng.
- Q4 FCFE, tiền ròng, KT-PL, r/g: không thấy lạc quan.
- r3 tự nêu đúng các điểm yếu chính (giá chuyển nhượng, ánh xạ P giữa). Lỗi của r3 là không đưa các điểm yếu đó vào tâm, trong khi lại đưa (3b) vào.

## ĐÃ BỎ
- Không gặp hay chép số giá cổ phiếu/định giá CTCK nào. Tiêu đề bài BVSC/SHS (A1) chỉ dùng phần dữ kiện sự kiện (hạn giấy phép), không dùng nhận định định giá.

## KHÔNG TÌM ĐƯỢC
- Nguyên tắc giá PAT–DLC (đã dựa vào A3 #N12).
- Sản lượng/đơn giá PAT.
- Dự báo cốc 2027–2028.
- Hợp đồng quặng sau Q1/2027.
- Dư nợ vay của các công ty thành viên được bảo đảm bằng tiền gửi PAT.
- Hệ số gốc NVL r2 (tệp r2 nằm trong vùng cấm đọc, nên mức GĐ2 55,20% chỉ kiểm được là hợp lý).

## ĐIỂM MÂU THUẪN
- Hạn giấy phép KT25: "hết 2026" (SHS/VietTimes) vs khoảng đầu 2027 (Vietnambiz).
- Tỷ lệ cước/DT XK: 3,85% (FY25) vs 4,69% (9T/26) vs 7,85% (Q3 riêng: 4,662/59,397 — có thể gồm cước nội địa).
- VALUATION_r3 dòng 17: nhãn "(3a)+(3b) gộp" sai so với `bridge_sens_out.json` (oat "gỡ O-nhất quán" = chỉ (3b)).
