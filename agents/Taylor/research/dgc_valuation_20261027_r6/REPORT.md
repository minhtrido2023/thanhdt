# DGC định giá VÒNG 6 — áp phản biện fundamental-skeptic vòng 5 (REFUTED, medium)

Job `Taylor_20261029_053128`. r1-r5/FORECAST/SCORE KHÔNG sửa; mọi đính chính r5 nằm ở ĐÂY. READ-ONLY, không phải khuyến nghị. Tỷ đồng, đ/cp. **[UL]** = ước lượng. Tái lập: `python3 model.py` (log `run_stdout.txt`; assert tái lập r4 = 33.766 và r5 = 40.302; md5 ở `LOCK.txt`). BCTC Q3 CHƯA soát xét. Giữ luật pháp lý 27/09: WARNING, không phải cổng chặn.
Giá tham chiếu 32.900 (28/10); TB 5 phiên 33.080.

## Kết luận (10 dòng)
1. **Phản biện ĐÚNG ở mọi điểm tôi tái lập được.** Chạy lại model: bỏ riêng uplift 34.786; gốc thuần r5+biên r4+w r4 = 36.468 (có uplift) / 31.589 (không); +quỹ KTPL 34.863 / 29.985; bỏ WC 300 → 40.122. Khớp từng chữ số skeptic (`out_skeptic_replication.csv`).
2. **Dải phân tầng r6: A 29.817 (−9,4% vs giá) · B 34.695 (+5,5%) · C 36.663 (+11,4%, chỉ độ nhạy) · D r5 40.302 (+22,5%).** Dải nên trình user: **~30.000 – ~35.000 (A→B)**; giá 32.900 nằm GIỮA dải ⇒ không có vùng định giá thấp rõ ràng theo mô hình sau khi gỡ phán đoán.
3. **40.000 là TRẦN CÓ ĐIỀU KIỆN, không phải kỳ vọng**: cần đồng thời (i) uplift khai trường 25/19B (+4.878), (ii) biên 2027-28 ≥ 18% (+1.968 trên B), (iii) trọng số lạc quan 0,25/0,5/0,25 (+1.739) — cả ba đều không có bằng chứng; (ii) và (iii) cùng xuất phát từ MỘT quý Q3.
4. **Cầu nối giá → giá vốn → biên KHÔNG dựng được đủ tin cậy từ nguồn công khai ⇒ dùng biên r4 (16,5/17,5%) làm nền**, biên cao chỉ ở độ nhạy (tầng C). Lý do ở §2. Thứ dựng được là RÀNG BUỘC cơ học (không phải hiệu chỉnh): giá vốn Q3 ×4 = 7.852; doanh thu 2027 của chính model = 9.261 (P4 4.150 $/t) ⇒ biên **15,2%** nếu giá vốn giữ như Q3; 17,5-19,5% chỉ khi giá vốn giảm 5% hoặc dự phòng 200 là một lần (§2). Biên 18% r5 **không có chỗ đứng** trong chính giả định giá P4 của model.
5. **Dự phòng 200 — phát hiện mới, là biến quyết định cách đọc biên**: +100 ở Q2, +100 ở Q3 (từ 0 ở 31/12/25). Note 26-28 liệt kê đủ chi phí tài chính / bán hàng / QLDN: **không dòng nào chứa khoản dự phòng và mọi dòng đều nhỏ hơn 100 ở mức quý** ⇒ nếu đã qua KQKD thì gần như chắc chắn nằm trong **GIÁ VỐN** (hoặc chi phí khác, nhưng Q3 chi khác chỉ 38,4). Giả sử ở giá vốn: biên Q2 18,9% → **23,0%**, Q3 20,5% → **24,6%**, Q1 23,0% (không dự phòng). Cách đọc R1 (lặp lại ~100/quý): biên nền 18,9-20,5% đúng, 2027 cơ sở 15,2%/16,5% ⇒ EV A **28.235** / B **33.113**. R2 (một lần): biên nền 23-24,6%, 2027-28 cơ sở **19,5/20,7%** ⇒ A **34.238** / B **39.117**. **Chưa biết là R1 hay R2 — hỏi DGC.** Đây là ước lượng suy từ phép loại trừ, không phải khẳng định.
6. **Trừ nhất quán dự phòng 200 VÀ quỹ KTPL 592,8 (cùng 100%)**: −1.605 đ/cp cho quỹ KTPL. Độ nhạy 0/50/100% cả hai ở §4: A từ 31.963 (không trừ gì) đến 29.817 (trừ cả hai). Quỹ KTPL được trích từ lợi nhuận (note 21 trừ 76,0 trong 9T khi tính EPS) và chi bằng tiền cho người lao động ⇒ coi như nợ chi tiền là cách đọc bảo thủ nhưng nhất quán với dự phòng.
7. **Bỏ 'thu hồi vốn lưu động 300' 2027** (tồn kho đã giảm 374 vào tiền): −168 (A 29.817; giữ 300 → 29.985). Không còn tồn kho dư để giải phóng chắc chắn: tồn kho 2.085,9 vs YE25 1.681,9 (còn +404 so cuối 2025 — là mức tối đa có thể giải phóng, [UL]).
8. **Đã thu 819/326 — rút lại câu của r5, thay bằng WARNING (§3)**: tiền ròng 8.370 theo bảng cân đối là ĐÚNG; điều chưa chứng minh là khoản 819 tất toán bằng TIỀN hay phi tiền. ~363 tỷ tiền gửi/dự thu giảm không qua tiền và ~224 tỷ tài sản tăng không qua tiền (số học ở §3). Giữ haircut pháp lý 3/9/29% nhưng lý do là rủi ro quản trị/pháp lý + nguồn tiền chưa đối chiếu được, KHÔNG phải "rủi ro bên vay ẩn đã biến mất".
9. **Thanh lý TSCĐ 332,3 — có lời giải số học mới**: note 10(a) nguyên giá thanh lý 350,31 − khấu hao lũy kế 66,25 = giá trị còn lại **284,06**; 332,29 − 284,06 = **48,23 = đúng số lệch LCTT** (khớp đến 0,001). Dòng tổng CFI 2.802,27 khớp tiền cuối kỳ 230,18 ⇒ **thu thật khả dĩ = 284,06 (bán đúng giá trị sổ), dòng 332,29 là in sai/gộp thêm 48,23**; cách đọc khác (thu 332,29, lãi 48,2, sai ở dòng khác) vẫn mở. Tài sản bán là **nhà cửa vật kiến trúc (NG −96,8) và máy móc thiết bị (NG −241,3)**, không có thuyết minh bên mua/mục đích. Độ nhạy sản lượng P4 54 kt: −5% / −10% / −20% ⇒ A **−765 / −1.530 / −3.059** đ/cp.
10. **P(LNST mẹ 2026 ≥ 1.600) với w r4**: mẹ 54% / hợp nhất 86% ⇒ 50/50 = **70%** (70/30 = 64%). Nghị quyết ĐHĐCĐ gốc vẫn chưa đọc. Q4 cơ sở 19% ít nhạy: Q4 biên 15% → 20,5% đổi EV A chỉ 29.714 → 29.855.

## 1. Dải phân tầng (`out_tiers.csv`; thuận / cơ sở / nghịch)
| Tầng | Gồm gì | EV | vs 32.900 | thuận / cơ sở / nghịch |
|---|---|---|---|---|
| **A** | BCTC Q3 thật (tiền ròng 8.370, VCSH mẹ 13.073,9, Q1-Q3 thực, MI 9%, Nghi Sơn còn lại 1.047) · **biên r4** 16,5/17,5% · **w r4 0,2/0,5/0,3** · **KHÔNG uplift** · trừ dự phòng 200 + quỹ KTPL 592,8 (100%) · bỏ WC 300 | **29.817** | −9,4% | 41.474 / 31.216 / 19.714 |
| **B** | A + uplift khai trường 25/19B (cơ sở +500 LN gộp 2028 nửa năm; thuận +500/+1.000; **không có mốc**) | **34.695** | +5,5% | 54.268 / 35.855 / 19.714 |
| **C** | B + biên cao r5 18,0/18,5% — **chỉ độ nhạy, KHÔNG có cầu nối** | 36.663 | +11,4% | 58.029 / 37.562 / 20.920 |
| **D** | r5 cũ (tái lập) | 40.302 | +22,5% | 59.873 / 39.406 / 22.524 |
Tầng A theo phương pháp (cơ sở): SOTP 32.769 · DCF 32.925 · P/B 32.890 · PE peer 26.238 · PE DGC 10y 24.734. Thuận B ≫ A do uplift thuận gấp đôi cơ sở (+1.000 từ 2028) — **kỳ vọng B bị kéo bởi đuôi thuận 54.268**; cơ sở B 35.855 phản ánh đúng hơn.
Hai cách đọc dự phòng chồng lên tầng: R1 → A 28.235 / B 33.113; R2 → A 34.238 / B 39.117.

## 2. Cầu nối giá → giá vốn → biên: vì sao KHÔNG dựng được
- **Dữ liệu quá ít để hiệu chỉnh**: biên thật chỉ 3 quý (23,0/18,9/20,5%); P4 SunSirs trong repo **bắt đầu 03/2026** (Q1 chỉ 3 điểm: 25.323; Q2 32.898; Q3 27.606; Q4 đến 23/10 28.093 RMB/t, `data/phosphorus_weekly.csv`); lưu huỳnh **5 điểm** (`sulfur_anchors.csv`: 295/256/315/620/500 $/t, điểm cuối 05/2026); DAP tháng có đủ (725→800 $/t Q2→Q3) nhưng DAP chỉ là một phần doanh thu. BCTC KHÔNG công bố sản lượng/đơn giá/giá vốn theo sản phẩm (note 23-24 chỉ có doanh thu thành phẩm 6.956 + khác 53 và giá vốn tổng). BQ biên gộp lệch BCTC 3-6pp (không dùng làm mức).
- **Dấu của quan hệ không ổn định**: cùng kỳ biên nghịch chiều giá P4 (Q1 giá thấp 25,3k biên 23,0%; Q2 giá cao 32,9k biên 18,9%) ⇒ giá bán chốt trễ và/hoặc chi phí đầu vào (lưu huỳnh đỉnh 03-05/2026) lấn át; trễ 1 quý có dấu đúng nhưng chỉ có 2 điểm. Hồi quy trên 3 điểm là vô nghĩa.
- **Không thể tách giá vs chi phí vs dự phòng** khi dự phòng 200 (≈ 4pp biên mỗi quý) có thể nằm trong giá vốn (kết luận 5).
- **Phần làm được — ràng buộc cơ học, không hiệu chỉnh** (`out_bridge.csv`, `out_price_shock_margin.csv`, `out_prov_readings_margin.csv`): với doanh thu 2027 của model, biên ngầm = 1 − giá vốn/doanh thu:
 | giá vốn so Q3×4 (7.852) | 0,95 | 1,00 | 1,05 | 1,10 |
 |---|---|---|---|---|
 | biên 2027 cơ sở | 19,5% | **15,2%** | 11,0% | 6,7% |
 | biên 2028 cơ sở | 20,7% | **16,5%** | 12,3% | 8,1% |
 Giá P4 xuất khẩu −5/−10/−16% (tỷ trọng ~65%, giá vốn phẳng như Q3, từ 20,5%) ⇒ biên 17,8 / 15,0 / 11,3%. Lưu huỳnh ~700 $/t 2027 (scenario cơ sở của chính model) so ~500 hiện nay là chiều **tăng** giá vốn, chưa định lượng được (không có tỷ trọng lưu huỳnh trong giá vốn; tỷ trọng 12% [UL] ⇒ +40% lưu huỳnh ≈ +5% giá vốn). ⇒ **r4 16,5/17,5% khớp ràng buộc (15,2/16,5% khi giá vốn phẳng); r5 18,0/18,5% không**, trừ khi dự phòng là một lần (R2) hoặc giá vốn giảm.
- Kết luận: dùng biên r4 làm nền; trình biên cao như độ nhạy: biên 2027-28 +1/+2/+3pp mọi kịch bản ⇒ A 31.238 / 32.652 / 34.070 (B 36.115 / 37.530 / 38.947) (`out_sens_margin.csv`).

## 3. WARNING thay cho câu "khoản 819 và lãi 326 đã thu, nằm trong tiền" (r5 kết luận 2 và dòng 8, 14)
Câu đó KHÔNG được lưu chuyển tiền chứng minh. Đã tái lập:
- **LCTT tự lệch 48,23**: tổng các dòng 21-27 = 2.850,50 vs dòng 30 in 2.802,27. Dòng 20+30+40 = dòng 50 và tiền cuối kỳ 230,18 KHỚP bảng cân đối ⇒ tổng CFI nhất quán với tiền; lệch nằm ở một dòng thành phần. Ứng viên số 1 là dòng 22 thanh lý (§kết luận 9: 332,29 − 48,23 = 284,06 = giá trị sổ tài sản bán).
- **Tiền gửi kỳ hạn ~363 giảm không qua tiền**: gốc giảm 12.065 → 9.437,8 = −2.627,2 vs net LCTT (thu hồi 14.309,5 − cho vay 11.822,7) = 2.486,8 ⇒ **140,4**; lãi kỳ vọng thu = lãi 527,5 + dự thu đầu 331 − dự thu cuối 93,2 = 765,3 vs LCTT thu lãi 542,9 ⇒ **222,4** [gốc 12.065 và dự thu 331 là số Mike chép từ extract, chưa tôi tự mở lại ảnh p24 YE25].
- **~224 tài sản tăng không qua tiền**: XDCB Q3 +131,9 và trả trước người bán +110,8 = 242,7 vs chi XDCB tiền Q3 ≈ 18,6 (511,6 − H1 493,0 "theo Mike", chưa kiểm); phải trả người bán chỉ +1,8 ⇒ ≈ 224,1. Note 11: XDCB 9T tăng 745,3; chi tiết Nghi Sơn **1.408,8** (r5 dùng 1.352,9; nếu dùng 1.408,8: A 29.980 / B 34.858, +163).
- **Dự phòng 200** và **thanh lý 332,3 không thuyết minh** (xem 5, 9).
Giữ: tiền ròng 8.370 theo BẢNG CÂN ĐỐI là đúng. Câu hỏi mở là khoản 819 (cho vay H1) và lãi 326 được tất toán bằng tiền hay phi tiền (bù trừ, chuyển đổi, đầu tư tài sản dài hạn?). Không đủ dữ kiện để loại trừ bên vay/đối tác liên quan; haircut 3/9/29% giữ nguyên với LÝ DO ĐÚNG như kết luận 8. **22.040 đ/cp là tiền ròng TRƯỚC haircut và trừ PAT-CĐKKS; sau PAT 274 và haircut 9% ≈ 19.400 đ/cp** (đã in ở run_stdout) — đính chính r5 kết luận 2.

## 4. Waterfall r5 → r6 (`out_waterfall.csv`; thứ tự phụ thuộc, nên kèm bảng bỏ-riêng)
| Bước | EV | Δ |
|---|---|---|
| r5 (tái lập) | 40.302 | |
| 1 biên 2027-28 về r4 (16,5/17,5) | 38.207 | −2.095 |
| 2 trọng số về r4 0,2/0,5/0,3 | 36.468 | −1.739 |
| 3 trừ quỹ KTPL 592,8 (100%) | 34.863 | −1.605 |
| 4 bỏ WC 300 2027 | 34.695 | −168 |
| 5 bỏ uplift khỏi nền = **tầng A** | **29.817** | −4.878 |
Bỏ RIÊNG từng thứ khỏi r5 (`out_waterfall_individual.csv`): nâng biên −2.095 · trọng số −1.867 · quỹ KTPL −1.604 · WC300 −180 · uplift −5.516. **Hơn một nửa mức chênh r5→A (10.485) là uplift + biên + trọng số (4.878 + 2.095 + 1.739 = 8.712 = 83%).**
Độ nhạy dự phòng 200 (hàng) × quỹ KTPL (cột), trừ 0/50/100% (`out_sens_prov_x_fund.csv`):
| A | fund 0% | 50% | 100% |
|---|---|---|---|
| prov 0% | 31.963 | 31.161 | 30.359 |
| 50% | 31.692 | 30.890 | 30.088 |
| 100% | 31.422 | 30.619 | **29.817** |
(B cộng ~4.880 ở mọi ô.) Uplift 0/250/500/750/1000 trên nền A: 29.817 / 31.036 / 32.256 / 33.476 / 34.695 (mỗi 250 ≈ +1.220). Tồn kho/WC: 0/100/200/300 → 29.817 / 29.873 / 29.929 / 29.985.

## 5. Cảnh báo / WARNING còn lại
- **HOSE hạn chế giao dịch DGC**: chỉ trích dẫn KB — `kb/current_ops.md` dòng 13 "DGC EXCLUDED (`excluded_tickers`, HOSE hạn chế giao dịch đến ~11-12/2026)"; điều kiện gỡ kép AND (BCTC + 6 tháng công bố thông tin sạch) theo `kb/memory/Wendy.md` dòng 16 (QĐ 22/2026, Điều 42 khoản 2). Data-ops đang kiểm trạng thái riêng; **tôi KHÔNG kết luận "không thấy tin" hay "đã gỡ"**. Giá trị tính cho tài khoản fleet = 0 vì DGC đang excluded.
- **Soát xét Q3**: H1 tự lập 797,4 → soát xét 788,9 (−1,05%); áp tương tự Q3 mẹ ≈ −5 (≈ −13 đ/cp). Chưa biết ngoại trừ.
- **Nghi Sơn GĐ1** (Q4/2026): XDCB Nghi Sơn 1.408,8/2.400 theo note 11 (còn ~991, không phải 1.047); trễ/vượt chi phí không mô hình riêng.
- **Khai trường 25/19B**: không có mốc; ±4.878 đ/cp trên B so A là biến nhạy nhất.
- Tiền "ngân hàng khác" 786,6 (8,3% tiền gửi) không nêu tên; phải thu khách hàng 467,1 (Mitsubishi 188,3).

## 6. Câu hỏi cho DGC (để vòng sau / nhà đầu tư)
1. **Dự phòng phải trả ngắn hạn 200 (mã 322)**: khoản gì (bảo hành, hợp đồng, vụ án, thuế, hoàn nhập quặng)? Ghi nhận vào chỉ tiêu nào của KQKD (giá vốn?) và có tiếp tục trích ~100/quý không? — quyết định biên R1 hay R2 (chênh EV ~6.000 đ/cp giữa A R1 28.235 và R2 34.238).
2. **Thanh lý TSCĐ**: bên mua? nhà cửa/máy móc nào (nguyên giá 350,3; giá trị còn lại 284,1)? giá bán 284,1 hay 332,3? ảnh hưởng sản lượng P4 54 kt?
3. **LCTT 9T**: dòng nào lệch 48,23 (mã 21-27)? Khoản cho vay 819 và lãi 326 được thu bằng tiền hay phi tiền; ~363 tiền gửi/dự thu giảm không qua tiền đi đâu; XDCB +131,9 Q3 vs chi tiền 18,6 (trả trước người bán +110,8)?
4. **Quỹ khen thưởng phúc lợi 592,8** (+191,8 trích, −79,0 sử dụng 9T): kế hoạch chi 2026-27?
5. **Khai trường 25/19B**: mốc mở lại, điều kiện pháp lý.
6. **Nghị quyết ĐHĐCĐ gốc**: mục tiêu LNST 1.600 là mẹ hay hợp nhất?
7. **BCTC soát xét Q3**; giá P4 chốt hợp đồng, độ trễ giá bán; cơ cấu chi phí (lưu huỳnh/quặng nhập/than cốc/điện) ⇒ dựng cầu nối được.
8. 786,6 tiền gửi "ngân hàng khác": ngân hàng nào.

## 7. Đính chính r5 (không sửa file r5)
- Kết luận 2 và dòng 14 r5: "khoản 819/326 đã thu, nằm trong tiền" ⇒ thay bằng §3.
- "22.040 đ/cp (= 67% vốn hoá)" là TRƯỚC haircut/PAT-CĐKKS; ~19.400 sau.
- "Hơn 2/3 mức tăng là cơ học từ tiền thật": đúng về số học bước 1-2 (+2.946) nhưng bước 3-6 (−224) chỉ bù nhẹ; phán đoán +3.814 và uplift +5.516 là phần quyết định kỳ vọng 40k.
- Nghi Sơn: XDCB 1.408,8 theo note 11 (r5 1.352,9, giả định [UL] — sai 56).
- Dự phòng tồn kho 0,29 tỷ (đã đính chính ở extract Q3) — không đổi.
