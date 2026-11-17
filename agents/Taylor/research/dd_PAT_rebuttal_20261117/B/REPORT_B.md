# REPORT_B — cổ tức ổn định > lãi huy động: có bị giảm sâu không, và r* ngầm (17/11/2026)
Nguồn: hand-back agent Opus stateless B (PREREG md5 7510c9a3…, sửa trước khi xem kết quả md5 9fd85f56…). Code `code/`, output `out/`, chạy lại `/home/trido/thanhdt/wc_venv/bin/python` (fetch_exp.py → analyze_exp.py, ~15 phút). PAT bị loại khỏi mẫu ngay trong SQL. CHƯA qua quant-skeptic.

## Kết luận
1. Khẳng định "chưa có công ty cổ tức ổn định vượt lãi gửi mà bị giảm sâu" = **MỘT PHẦN**. Nghĩa đen sai: 23/176 mã-năm (106 mã) sụt tối đa ≥30% trong 12 tháng tiếp theo (đã tính cổ tức), rải 8/14 năm; 7 ca ≥50%. Nhưng nhóm này AN TOÀN hơn: tỷ lệ sụt sâu 13,1% [6,1; 21,1] so 25,2% ở mã trả cổ tức khác; chênh −12,2pp [−19,4; −4,2]; giữ ở 7/8 biến thể, IS 13,8% vs 22,8%, OOS 12,2% vs 28,6%.
2. ~17/23 phản ví dụ rơi vào năm cả thị trường sập (riêng nhóm chọn cuối 2021 → đợt sập 2022: 7 ca). "Ổn định" quá khứ không giữ: 10,8% mã-năm không trả tiền mặt năm sau; cổ tức 3 năm sau trung vị 0,74× mức cũ; 8/23 phản ví dụ bỏ hẳn cổ tức (11/153 ở nhóm không sụt). Thứ tự cắt cổ tức–giảm giá không kiểm chặt được (corporate_action ghi đè public_date); 9/15 ca chạm đáy sau ex-date kế tiếp.
3. Spread r mô hình (6,1pp) có quá cao cho nhóm này? = **KHÔNG PHÂN BIỆT ĐƯỢC**. Lợi suất thực nhận − lãi gửi: TB +14,0pp [+0,5; +29,3], trung vị +7,7; IS +14,0 [−2,6; +37,1], OOS +14,0 [−6,5; +35,4] — mọi khoảng chứa 6,1. Spread suy từ cổ tức phụ thuộc giả định tăng trưởng (0g: +3,1; g lịch sử ≤8%: +11,0; g cổ tức thực nhận: −9,9) ⇒ dữ liệu không xác định r* ngầm.
4. ~~Hàm ý 'lệch nằm ở dòng tiền, không ở r'~~ — GỠ theo quant-skeptic: dữ liệu không xác định được r* nên không thể quy khoảng lệch cho dòng tiền; chỉ còn là giả thuyết. Kết quả (3) là null THIẾU SỨC MẠNH (MDE ~20pp), không xác nhận 6,1pp; ước lượng điểm +14pp còn ngược hướng giả thuyết 'spread thấp hơn'.
5. Giới hạn: 14 lát năm (2–22 mã/năm), 2008–2010 không kiểm được (thiếu chuỗi lãi có nguồn ⇒ phản ví dụ có thể đếm thiếu), chuỗi lãi là mốc neo hồi tố, thiên lệch sống sót từ định nghĩa "ổn định", lợi suất dùng giá điều chỉnh (nghiêng về nhà đầu tư; giá thô: 14 ca ≤−30%).

## Bảng 1 — Nhóm P0 (cổ tức tiền liên tục 5 năm, không năm nào giảm >25%, yield 12T > lãi Big-4 12T; chọn cuối năm 2011–2024)
| Chỉ số | Ổn định | Trả cổ tức khác | Toàn universe |
|---|---:|---:|---:|
| Mã-năm (mã) | 176 (106) | 2.143 | 4.382 |
| Sụt ≥30% | 13,1% (23 ca/8 năm) | 25,2% | 30,4% |
| Sụt ≥40% | 5,7% (10/5 năm) | 15,1% | 19,9% |
| Sụt ≥50% | 4,0% (7/3 năm) | 9,3% | 13,6% |
8 biến thể: nhóm 12,4–19,8% vs 24,5–26,6%; 7/8 loại trừ 0 (V2 giảm tối đa 10%, 96 mã-năm: [−10,6; +1,1]). Ngành (ca/mã-năm): BĐS 6/19, tiêu dùng 6/35, công nghiệp 4/51, NVL 3/22; ngân hàng 0 mã lọt nhóm. Năm chọn: 2021 → 7 ca; 2019 → 3 (COVID); 2024 → 3 (sốc 04/2025).
## Bảng 2/3 — xem hand-back (spread theo nhóm; IS/OOS; bỏ-từng-năm: lợi suất vượt lãi 9,9–17,7pp; sụt≥30% 9,9–14,9%). Lãi gửi dùng: 2011 14,0 · 2012 9,0 · 2013 7,5 · 2014 6,3 · 2015–16 5,5 · 2017 6,5 · 2018 6,8 · 2019 7,0 · 2020 5,7 · 2021 5,5 · 2022 7,5 · 2023 5,0 · 2024 4,7 (%).
Kiểm chéo: yield tự tính khớp cột DY ±10% ở 97,7% dòng; 1 mã (NTP) kiểm tay khớp. DSR/PBO không áp dụng (không chọn cấu hình). Chưa làm: quant-skeptic, giá thô, cửa sổ 24 tháng, tách vốn hoá, chuỗi lãi 2008–10.

## ĐÍNH CHÍNH sau quant-skeptic (17/11, verdict CONFIRMED, tin cậy TB; tái lập 619/619 trường + tự dựng lại 176/176 mã-năm)
- Đo theo GIÁ THÔ quy đổi cp thưởng, không cộng cổ tức (đúng chữ 'giảm giá sâu'): nhóm ổn định sụt tối đa ≥30% = **18,2% (32 ca)** vs 28,0%; phân tầng theo năm chênh **−6,6pp [−14,4; +1,2] — CI chứa 0** (số Close/điều chỉnh: −9,3 [−16,1; −3,0]). 'Giá thô: 14 ca' ở trên là lợi suất cuối kỳ, KHÔNG phải sụt tối đa. Số Close có lợi cho nhóm yield cao (yield trung vị 9,2% vs 5,1%).
- **BĐS: nhóm ổn định KHÔNG an toàn hơn** (31,6% vs 31,2%; giá thô 36,8% vs 32,1%).
- Thiên lệch sống sót tầng dữ liệu: tav2_bq.ticker không có mã nào phiên cuối trước 2025; 494 mã vắng khỏi bảng giá (208 hủy niêm yết 2012–25); 108 mã/346 mã-năm đã chết đạt tiêu chí ổn định (17 hủy niêm yết trong 12T) ⇒ mọi tỷ lệ tuyệt đối là CẬN DƯỚI.
- '~17/23 ca ở năm thị trường sập' dựa ngưỡng đặt sau khi xem dữ liệu ⇒ khám phá.
- Cổ tức của nhóm quay đầu giảm sau thời điểm chọn (trung vị −13,9%/năm) — hệ quả chọn yield ở đỉnh.
- Phán quyết cuối cho #5: khẳng định của user ĐÚNG VỀ HƯỚNG (nhóm này ít bị sụt sâu hơn) nhưng SAI ở chữ 'chưa có công ty nào' và độ lớn co lại khi đo bằng giá thô; nghiên cứu KHÔNG đủ sức bác hay xác nhận spread 6,1pp.
