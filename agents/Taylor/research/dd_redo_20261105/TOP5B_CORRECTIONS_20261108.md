# Đính chính từ fundamental-skeptic 08/11/2026 (cụm 2) — PVT, DDV, SAS, NT2, DRI (áp trong vòng 3). Kiểm từng điểm bằng calc, đừng chép mù. Giá tham chiếu = đóng cửa 06/11/2026 (BQ tav2_bq.ticker; 07/11 thứ Bảy).
Quy tắc chung: khoản lệch khỏi sổ sách/NPV0 trong BASE phải có dòng 'cơ sở dữ liệu' + nguồn; chỉ nhận định (kể cả Bobby) ⇒ ra khỏi base sang độ nhạy/kịch bản có xác suất. Moat chỉ cộng khi bền, không trừ (user 08/11). P10/P50/P90 ở MỨC KẾT CỤC bằng _shared/wpct.py. Báo CK ở cả cỡ tham chiếu 5 tỷ và cỡ sleeve thật. Headline = mô hình cơ sở hiện hành sau đính chính; phiên bản thay thế chỉ là độ nhạy song song. Chốt giả định thay đổi vào LOCK_md5 trước khi đọc kết quả so giá.
Cả 5 mã: verdict skeptic = REFUTED hẹp (confidence medium); số r2 tái lập trùng byte; nhãn TRONG vùng không đảo.

## PVT (giá 20.550; tâm r2 17.675 → skeptic 18.050–18.774, điểm 18.506)
1. BLOCKING: calc/model.py:20 — trọng số kịch bản 0,35/0,45/0,20 và hệ số ROE 0,85/1,0/1,1 gắn [UL] 'Bobby blind' lệch xuống (ROE kỳ vọng ×0,9675), chồng lên trung vị chu kỳ đầy đủ 13,15% (đã gồm đáy 2015–17) và trục MULTS 0,8–1,2 đối xứng ⇒ chu kỳ bị đếm hai lần, chỉ là nhận định. Chuyển sang độ nhạy. Skeptic: chỉ đối xứng trọng số 0,275/0,45/0,275 → 18.212; chỉ đối xứng hệ số 0,9/1/1,1 → 18.050; cả hai → 18.506 (P10/P50/P90 13.591/18.493/23.852; 67,1% dưới giá). Khi đối xứng, NPV tàu kỳ vọng ±30% (model_r2.py:16) tự về 0 (−86 đ/cp biến mất).
2. LN 2027 cơ sở 1.250 (model.py:20) mâu thuẫn lý do 'biên ~20% như Q3' (Q3 năm hoá ≈1.500). Skeptic 29/10 đã nêu (dd_PVT_20261029/REPORT.md:246), r1/r2 giữ nguyên ⇒ thiên lệch xác nhận. Đổi 1.200/1.450/1.700 + đối xứng → 18.774.
3. Bản song song 'ROE bỏ lãi tiền gửi' (model_r2.py:20; REPORT_r2.md:16,32,48) chỉ trừ lãi gửi (251 tỷ/9T) mà giữ chi phí lãi vay trên nợ gộp ~6,3 nghìn tỷ ⇒ kiểm chéo một chiều: tính lại theo lãi ròng (~0) hoặc bỏ khỏi §0.
4. WARNING thiếu: PVT Logistics xin chào bán thêm cổ phần mở rộng đội tàu 05/10, rủi ro pha loãng (REPORT.md:250; calculated_fear_state_backstop.md:3408) trong khi REPORT_r2.md:35 viết 'chưa có đợt cụ thể'. Ý kiến kiểm toán 2025 treo qua 2 vòng (:54), đóng lại.
5. Giá tham chiếu 20.550 (06/11), không phải 21.000 (04/11): % trọng số dưới giá của r2 là 72,2% (không phải 78,3%).
6. Provenance: 9.855,6 (VCSH mẹ) và 251,0 (lãi gửi) chỉ truy về REPORT 29/10 (text bảng vỡ; PDF 11,8MB không tải được). Đọc bằng pymupdf (fitz) hoặc ghi 'chưa kiểm'.
Giá ngụ ý: 20.550 ≈ ROE giữa chu kỳ ~14,4% vĩnh viễn (= trung vị 2018–25 14,5%) hoặc r ~12,4% (lãi huy động ~6,3%).

## DDV (giá 15.200; tâm r2 13.109 → skeptic 13.840–14.740, điểm 14.388: P10 12.213 / P50 14.355 / P90 16.430, 69,1% dưới giá)
1. BLOCKING: chuẩn hoá vốn lưu động −1.635 đ/cp (model.py:11-12; REPORT_r2.md:36) chọn mốc 30/06 là 'bình thường' = ĐỈNH vốn lưu động (tồn kho 905,8, phải trả 120,0), chỉ lấy chân phải trả/phải thu, bỏ chân tồn kho (Q3 giảm 69,2). VLĐ ròng 30/09 = 581,8 nặng hơn mốc kiểm toán 01/01 (463,9). Lấy 01/01 làm mốc: trừ 52,6 tỷ (−360 đ/cp), tâm +1.257; bỏ chuẩn hoá: +1.612. Lịch sử: 'stress 5.950' của DD 28/10 sang r1 thành base mà không có thông tin mới.
2. BLOCKING: hệ số giữa chu kỳ 0,8/1,0/1,1 theo trọng số Bobby 0,45/0,40/0,15 (model.py:28-30; model_r2.py:20) cắt vĩnh viễn 7,5% LN terminal; mức LN đã là TB 2015–25 gồm năm 2016 lỗ −470 tỷ ⇒ nhận định, ra độ nhạy: tâm +603.
3. RONIC 20% > Ke cho mã moat NONE (model.py:26; ADDENDUM_5F.md:33,48) = thưởng moat ngầm, trái quy ước 08/11 (tiền lệ HPG #3): tâm −675. (Phần peer LAS/NFC đã sửa tận gốc.)
4. Xác suất mất phải thu Liven 0,10 [UL] (model_r2.py:13) không có văn bản nợ quá hạn ⇒ độ nhạy: tâm +147.
5. Khoản trừ lãi tiền gửi 55,6 tỷ/năm (model.py:27) lấy lãi HIỆN TẠI (1,01% DT) trừ khỏi biên LN TRUNG BÌNH lịch sử (2015–20 tiền mặt ít hơn nhiều) ⇒ có thể trừ quá tay; cần thu nhập tài chính kiểm toán 2015–25 (BQ không có cột này). Ước của skeptic +0,5–1,0k, CHƯA kiểm — kiểm hoặc ghi 'chưa kiểm được'.
6. REV_NORM 5.500 [UL] (model.py:25) không có dòng cơ sở; DT TB 2021–25 = 3.710, 2025 = 5.652 ⇒ độ nhạy hai chiều.
7. Trục Q4 lệch xuống −60/+40 quanh −4,4 (model_r2.py:12; −19 đ/cp). VCSH xấp xỉ 2.214 (REPORT_r2.md:47) vs BCTC 3.349,9 − 1.141,7 = 2.208,2. Bảng nhạy theo 2027 dùng trọng số đối xứng 1/3: thêm +425.
8. Kỳ hạn nhận định (REPORT_r2.md:15) đổi sang 06/11 (giá không đổi 15.200). WARNING: chưa tra trực tiếp UBCKNN/HNX.
Giá ngụ ý: LNST giữa chu kỳ không tính lãi gửi ~189 tỷ/năm (NPM ~4,44% vs 167 tỷ base), hoặc giữ RONIC 20% sau khi sửa 1, 2, 4 (tâm 15.115).

## SAS (giá 34.200; tâm r2 31.066 → skeptic 30.700–33.400, điểm 31.731; P10/P90 24.970/38.159)
1. BLOCKING: calc/model_r2.py:22 `FIN_AT_9M=(DT TC−CP TC)×0,80` đánh thuế 20% lên cả 195 tỷ thu nhập tài chính, mà cổ tức được miễn thuế. KQKD tr.5: LNTT 638,03, thuế TNDN hiện hành 98,13 ⇒ phần miễn thuế ≈147,4; DD 26/10 dòng 47/91: cổ tức 9T = 88+47,8 = 135,8. N0 thật 479–482 tỷ (không phải 518,4). Tâm 29.325 (−1.741 đ/cp), P10/P90 22.564/35.753, 84,4% dưới giá. Sửa: tách cổ tức miễn thuế khỏi lãi tiền gửi (KQKD tr.5, thuyết minh V.27).
2. Vốn lưu động một chiều (:21): trừ phải trả NLĐ 141,2 + thuế phải nộp 50,2 khỏi tiền, bỏ thuế GTGT được khấu trừ 240,6 (mã 162), phải thu 165,8, HTK 204,3 (REPORT.md:48 tự ghi VLĐ ngoài tiền dương +130,3). Chỉ trừ quỹ KTPL 99,7: +1.348; gộp đủ VLĐ ròng: +2.968. Làm nhất quán.
3. Luật 20: XDCB dở dang 118,0 (mã 252) + BĐS đầu tư 32,2 (mã 240) đang định giá bằng 0 ⇒ ghi theo sổ: +1.058.
4. Trục chiều lên bị loại: bản song song chiều xuống ('bỏ phải thu DH') có, chiều lên không. Cổ tức đầu tư ~136–147 tỷ/9T vs giá sổ khoản đầu tư 253,8; vốn hoá 140 tỷ/năm ⇒ tâm 37.253 (giá thấp hơn tâm 8,2%). Báo độ nhạy, KHÔNG vào base (chưa biết bên trả cổ tức, mức đều đặn; đọc thuyết minh V.2c/V.27).
5. Giá 34.200 (06/11) thay 34.700: r2 ở giá mới: giá > tâm 10,1%, 73,3% dưới giá; bản đính chính: giá > tâm 7,8%. Cỡ sleeve 40tr: tâm 33.578, giá > tâm 1,9%.
6. WARNING còn thiếu: 20 lô đất >7,2 triệu m² (Bộ Tài chính 2019); phải thu IPP Group Pte 194 tỷ (bên liên quan, đã thu); bên trả cổ tức chưa xác định; kỳ giữa niên độ không trích quỹ KTPL trên LN 9T (~63 tỷ, −473 đ/cp nếu trích như 2025).
7. Ghi chú: tâm Δ −25% Long Thành và 57% DT khách quốc tế là [UL] hai chiều (nguồn bất định lớn nhất); Gordon không trừ tái đầu tư giữ theo quy ước 08/11 (bản chặt 22.002 chỉ độ nhạy). Thanh khoản: ADV250 0,59 tỷ; 5 tỷ = 847% ADV (CK 6,0%, ngoài vùng); 40tr = 6,8% ADV (CK 0,54%); free float ~4,4%.
Giá ngụ ý: tâm Δ Long Thành ≈ −16% (thay −25%), hoặc r ≈ 12,4%, hoặc ≈71 tỷ/năm cổ tức đầu tư vốn hoá.

## NT2 (giá 22.200; tâm r2 23.617 → skeptic 23.400–24.300, điểm 24.111; P10/P50/P90 18.598/24.155/29.276, 32,5% dưới giá)
1. BLOCKING: trục thời hạn chỉ mở phía TĂNG (bản 15 năm, REPORT_r2.md:27), thiếu nút GIẢM có nguồn: khí mỏ hiện hữu cạn ~2030, PPA gốc 2011–2020, sau 2020 chưa xác minh (dd_blind_NT2_20261026/CYCLE_BLOCK.md:72,75) — vi phạm điều 2 STANDARD_r2. Lưới 5/8/10/12/15 năm (0,1/0,2/0,4/0,2/0,1): tâm 23.475 (−142), P10 18.088; nút 4 năm trọng số 0,2: tâm 22.780, P10 17.546. Hai nguồn mâu thuẫn về hạn PPA (2036 substack vs 2011–2020 báo cáo MBS 2016) ⇒ ghi WARNING.
2. BLOCKING: vốn lưu động khoá 837 tỷ (mức đỉnh theo DT năm hoá 2026 ~10.400) suốt 10 năm (model_r2.py:30) trong khi dòng LN chuẩn hoá theo DT 7.137. Chuẩn hoá: giữ 574, giải phóng 263 tỷ ⇒ +646 đ/cp (tâm 24.263). Gộp với #1: tâm 24.111.
3. Giá 22.200 (06/11) thay 22.650: giá/tâm −6,0% (không phải −4,1%); % dưới giá 32,5% (không phải 37,5%).
4. FCF = LNST thiếu cơ sở (REPORT_r2.md:38 'khấu hao 153 ≈ capex duy trì'): capex thực 2,5 tỷ (9T/26), 4,8 tỷ (9T/25); đại tu đi qua chi phí trả trước 262,9 tỷ (mã 271). ±150 tỷ/năm = ±2.746 đ/cp, lớn hơn mọi đính chính khác ⇒ đưa vào lưới hoặc độ nhạy hai chiều với lịch sử capex+trả trước 2015–25.
5. LNST tâm 800 chỉ neo dự báo CTCK (BSC/VDSC; REPORT.md:66): thêm dòng cơ sở dữ liệu — biên LNST TB/trung vị 2015–25 = 10,4%/10,2% × DT 7.137 = 729–742; biên 9T/26 11,6% ⇒ 829. 800 đứng được. Lập luận ADDENDUM_5F.md:35 (biên EBITDA 20,1% vs mô hình 13,2%) KHÔNG đủ nâng tâm (khấu hao 516→115 nhưng biên LNST chỉ 10,6%→11,6% = PPA cost-plus).
6. WARNING thiếu (REPORT_r2.md:56-62): số Q3 tự lập chưa soát xét; tiền lệ bán niên bị soát xét giảm 94 tỷ do chi phí bảo trì định kỳ ghi thiếu.
Giá ngụ ý: tiền ròng 11.398 đ/cp (51% giá); thị trường tính LNST ~720 tỷ/năm cố định 10 năm hoặc 800 tỷ/năm ~8 năm.

## DRI (giá 13.100; tâm r2 14.092 → skeptic 14.290–15.300, điểm ≈14.900; DRI đã bán hết 02/11 — định giá KHÔNG được neo vào quyết định bán, ghi rõ thiên lệch xác nhận)
1. BLOCKING: trọng số 0,20 nhánh NQ15-KINH TẾ chỉ là nhận định [UL] (calc/dri_redo_r2.py:90; REPORT_r2.md:28), thực chất phạt tái canh NPV âm trái luật 20 + STANDARD_r2 điều 3 ⇒ chuyển sang độ nhạy: tâm 14.288 (+196), 25,0% dưới giá.
2. BLOCKING: khối 1.975 ha thanh lý được coi năng suất bằng trung bình vườn (q=1; dri_redo_r2.py:56) — nguồn khoản −2.120 (REPORT_r2.md:19). BCTN 2025 tr.44: 'thanh lý sớm do không đảm bảo mật độ khai thác' (dri_val_supply_adj_r4_20261027/REPORT.md:194). Trục mật độ q bị bỏ ngầm, không có trong axes_excluded (trái điều 2). Skeptic: nhánh NPV0 sau CK: q 0,85 → 14.902; q 0,7 → 15.519; q 0,5 → 16.348. Đưa trục q {0,7/0,85/1} trọng số .25/.5/.25 vào lưới ⇒ tâm ≈14.900, ~15% dưới giá (ghép với L22 đã trong lưới).
3. Thuế khấu trừ tại nguồn wht 10% (r3/model.py:59) cao hơn mức quan sát 7,0% và 8,3% (r3/model.py:29); SUMMARY tự ghi 'CHƯA dẫn nguồn luật thuế Lào' ⇒ dẫn nguồn hoặc dùng mức quan sát: +300.
4. Trọng số đường giá PEAK 0,6/0,4 [UL] lệch xuống: 0,5/0,5 cho +74.
5. Giá 13.100 (06/11) thay 13.500: tâm r2 14.092 (giá thấp hơn 7,0%), % dưới giá 27,5% (không phải 35,2%). SUMMARY price_date đang null. Tỷ giá LAK 1,1404 từ E_CORRECTIONS cần dẫn nguồn FX.
6. WARNING thiếu: tiền lệ DRI gia hạn khoản vay 40 tỷ cho Dakruco (Thời báo Tài chính, daily_day4_taylor.md:42) mâu thuẫn 'đang trả đúng hạn' (REPORT_r2.md:56); giấy nhượng đất 2016 chưa xác minh (SKEPTIC_R4 mục 4).
7. Thiên lệch xác nhận: thông tin mới duy nhất (NQ15) chỉ áp theo chiều giảm trong khi bằng chứng mật độ có sẵn lại bị bỏ qua ⇒ ghi rõ. Luật 4 sổ cần giá ≤12.665, nên không đạt; §2.5 vẫn KHÔNG đủ điều kiện.
Giá ngụ ý: tái canh phá giá trị 100% (nhánh KINH TẾ 13.307), hoặc FCF/LN lõi ~80% (13.219) + khối thanh lý năng suất trung bình.
