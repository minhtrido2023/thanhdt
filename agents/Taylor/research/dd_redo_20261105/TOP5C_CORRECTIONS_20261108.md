# Đính chính từ fundamental-skeptic 08/11/2026 (cụm 3) — DGC, MBB, NNC, PVP, SZL (áp trong vòng 3). Kiểm từng điểm bằng calc, đừng chép mù. Giá tham chiếu = đóng cửa 06/11/2026 (BQ tav2_bq.ticker): DGC 33.000, MBB 19.250, NNC 47.200, PVP 18.000, SZL 27.700.
Quy tắc chung: khoản lệch khỏi sổ sách/NPV0 trong BASE phải có dòng 'cơ sở dữ liệu' + nguồn; chỉ nhận định ⇒ ra độ nhạy/kịch bản có xác suất. Moat chỉ cộng khi bền, không trừ (user 08/11) ⇒ moat NARROW/NONE: RONIC = Ke. P10/P50/P90 ở MỨC KẾT CỤC bằng _shared/wpct.py. CK ở cỡ 5 tỷ và cỡ sleeve thật. Headline = mô hình cơ sở hiện hành sau đính chính. Chốt giả định vào LOCK_md5 trước khi đọc kết quả so giá. Cả 5 mã: REFUTED hẹp (medium), số r2 tái lập trùng byte, nhãn không đảo trừ ghi chú.

## DGC (tâm r2 44.767 → skeptic điểm 45.132, khoảng 38.870–48.152; P10/P50/P90 33.936/45.118/56.104; 7,4% dưới 33.000)
1. BLOCKING model_r2.py:17 + model.py:31: nhánh dự phòng 'vĩnh viễn' 400 tỷ/năm cộng chồng lên nền biên r4 đã ngầm chứa giá vốn cao hơn 281 tỷ/năm (run_stdout_r10.txt:39; r9_calc.py:83 tự ghi 'tính đôi') ⇒ bỏ đếm đôi: +1.612.
2. BLOCKING model.py:31-34: trọng số 0,3/0,5/0,2 chỉ là 'giữ thứ tự r12', biên độ xấu/tốt gần đối xứng (−337/+367) ⇒ 0,25/0,5/0,25: +653.
3. BLOCKING model.py:28: RONIC 20% > Ke trong khi ADDENDUM_5F_r2.md:28 moat_durable=false ⇒ RONIC=Ke: −1.760.
4. Trọng số mở lại khai trường 0,5 [UL] (model.py:37; thêm ở vòng 1 không có thông tin mới, REPORT.md:76, +6.854) ⇒ đưa lên HEADLINE thành dòng độ nhạy w=0/0,1/0,5 (w=0: 38.870 TRONG; w≥~0,1: DƯỚI). Nhãn phụ thuộc gần hoàn toàn vào đây — nói thẳng.
5. Nền biên r4 thiếu dòng cơ sở dữ liệu; nền R2 (19,5%) gần trung vị 4 peer 19,47%, Q3 chạy hoàn toàn quặng mua ngoài ⇒ R2 làm độ nhạy (+3.041) hoặc base nếu có dòng cơ sở.
6. model_r2.py:19: lá chắn thuế dự phòng = 0 trong khi TT48 cho trừ khi chi thật ⇒ độ nhạy +378.
7. REPORT_r2.md:53 gọi LN 9T là 'đáy' nhưng EBIT 2027 cơ sở 1.008 < EBIT 9T năm hoá (1.405 gồm dự phòng; 1.672 bỏ dự phòng) ⇒ sửa chữ/nhất quán.
8. Giá 33.000 (06/11): r2 ở giá mới 11,1% dưới giá. HTM 9.531 chỉ truy về bản trích (note 4 p24) — đối chiếu PDF hoặc ghi 'chưa kiểm'.
9. Kỷ luật exit/WARNING: ZaloPay giữ 10.000 cp, giá vốn 39.775 ≈ 330 triệu = 35,3% NAV (934,6 tr) so với trần sleeve 2–4% NAV — ghi rõ cho user. Chạy §2.5 (P/B mẹ ≈0,96 đạt; trụ #2 DN tư nhân trượt ⇒ NON đứng). Pháp lý sau 05/11 chưa quét ⇒ quét lại (chỉ WARNING).
Giá ngụ ý 33.000: không bao giờ mở lại khai trường + chi môi trường 400 tỷ/năm chắc chắn trên nền r4 (đếm đôi), hoặc EBIT lõi ~0,68× cơ sở mãi.

## MBB (tâm r2 23.804 → skeptic điểm 21.069, khoảng 20.400–21.100; P10/P50/P90 14.775/20.943/27.488; 38,6% dưới 19.250)
1. BLOCKING mbb_r2.py:43: 'vốn mới NPV 0' chỉ áp khi ROE_T<Ke; khi ROE_T 14/16/18% > Ke thì RI terminal vẫn tăng theo g 6–8% ⇒ RONIC>Ke vĩnh viễn = thưởng moat ngầm, trong khi ADDENDUM_5F.md:5,44 xếp NARROW không bền; tiền lệ HPG#3, DDV#3. g_RI=0 mọi ô: −3.638 (tâm 20.183). Sửa headline ADDENDUM_5F.md:1. Trục Δg mất tác dụng — ghi rõ.
2. BLOCKING mbb_r2.py:30-32: trọng số 0,35/0,45/0,20 ánh xạ sai từ Bobby (nhánh TỐT mượn xác suất 0,20 của STRUCTURAL) + STRUCTURAL đã vào ROE_T (mbb_calc.py:133) ⇒ đếm hai lần. Đối xứng 0,275/0,45/0,275: +1.204 riêng, +650 sau điểm 1.
3. Trục MBV (mbb_r2.py:64) [UL] lệch xuống; điểm 15.688 không có văn bản nghĩa vụ ⇒ đối xứng ±3.500 (+278), giữ điểm làm cờ HARD ABANDON.
4. Phải thu bán nợ 11.248 tỷ từ MBV có ở độ nhạy r1, mất khỏi lưới r2 và không có trong axes_excluded ⇒ đưa vào lưới hoặc ghi axes_excluded + lý do.
5. Độ nhạy ROE_T ±2pp (23.395 / 18.742): ROE_T 16% thấp hơn ROE 10 năm của MBB (19,8%) nhưng cao hơn trung vị ngành (13,0%).
6. REPORT_r2.md:64 LNTT Q4/25 '≈10.950' → số thật 11.129 (mbb_calc.py:106).
7. Giá 19.250 (06/11, không đổi so 04/11), ghi price_date. NPL/nhóm 2/bao phủ chưa tự kiểm (BQ không có cột) — đọc từ ảnh BCTC HN-Q3 hoặc ghi 'chưa kiểm'.
Giá ngụ ý: Ke ≈14,5% hoặc ROE_T ≈14,4% (sau đính chính). Nếu user cho phép RONIC>Ke thì 25.317.

## NNC (tâm r2 57.589 → skeptic điểm 60.114, khoảng 58,7k–61,8k; P10/P50/P90 30.379/57.157/95.353; 29,6% dưới 47.200; r2 ở giá mới 38,0%)
1. BLOCKING dd_MVC_20261103/r6/calc/model_r6.py:43-47 × model_r5.py:49,124: trần chu kỳ P_CYC tính bằng tiền 2026 (thực) nhưng nhân hệ số đường giá g2031 ⇒ ở ADMIN/CYCLICAL, đường g2031 (50%) biên gộp kẹt 26,0% từ 2030 so TB chu kỳ 34,3% = đếm hai lần (SKEPTIC_R4:3 đã nêu, r2 chỉ ghi chú). Cho trần tăng theo lạm phát 3%/năm: +2.525.
2. Trục trần chỉ mở chiều giảm (SL 1,40 = 236,1k < giá 2024 ≈260k quy về 2026) ⇒ thêm mức SL 1,05 = 260,8k đối xứng: +1.167 sau điểm 1.
3. Trục thuê Núi Nhỏ [UL] đều (nnc_redo_r2.py:60-68): báo song song bản 'chỉ tới 2043' = 61.822.
4. min() (model_r6.py:46) chỉ cắt chiều lên; bản co giãn đối xứng 64.022 nhưng P10 28,2k ⇒ chỉ độ nhạy.
5. Kịch bản xấu (SL 0,8 × giá 250k suốt 2028–43, FPTS 'không nêu lý do') cần dòng cơ sở dữ liệu; chồng đáy lên TB chu kỳ đã gồm đáy = đếm đôi một phần.
6. Giá 47.200. Tiền gửi 322,44, dự phòng 22,37, quỹ KTPL 16,78 chỉ truy về REPORT_v2:89 (PDF scan) ⇒ kiểm hoặc ghi 'chưa kiểm'; trừ khoản người mua trả trước 5,03 tỷ (≈−230 đ/cp). Sửa đường dẫn calc/summary_r2.py trong LOCK.
Giá ngụ ý: ROE bền 19,6% (Gordon) vs ROE chuẩn hoá 14,7–17,2%; ngay 100% CYCLICAL (51,1k) vẫn cao hơn giá 8%.

## PVP (tâm r2 22.366 → skeptic điểm 23.199, khoảng 22.746–24.195; P10/P50/P90 13.886/24.085/30.431; 20,5% dưới 18.000)
1. BLOCKING model.py:25: trọng số cước 0,40/0,45/0,15 [UL] 'Bobby blind' — chu kỳ bị tính ba lần cùng chiều (mức trung tâm 400 < 561 năm hoá, trọng số lệch xuống, −30% NPV tàu gắn nhánh xấu) ⇒ 0,275/0,45/0,275: +1.694 (tâm 24.060 nếu giữ ±30%).
2. BLOCKING model_r2.py:16: +30% NPV tàu nhánh tốt không có dữ liệu (luật chỉ cộng khi IRR kiểm được) ⇒ cắt: −861. −30% có cơ sở IRR 7,67% < hurdle 11% [AGM p44] nhưng không phụ thuộc chu kỳ nên gắn vào trọng số cước cũng chỉ là [UL].
3. model.py:22: chiết khấu FSO 10% (= huy động + 2,6pp [UL]) không có dữ liệu; bên thuê là công ty mẹ đã từng cắt giá cước (03/06/2025) ⇒ r=13,5%: −453 (hoặc dẫn nguồn spread).
4. Vốn lưu động ròng ngoài tiền +37,0 tỷ (583,9−546,9; BCTC Q3 tr.1–2) bị bỏ, mô hình chỉ trừ cổ tức 109,5 + dự phòng 232,9 ⇒ +349.
5. Trục FSO 177 tỷ ăn tiền/mất 0,5/0,5 [UL] có cơ sở là phần chênh chưa hoà giải; nếu ghi sổ: +646 (P50 25.173). Con số 25.173 là một ô lưới, KHÔNG phải kỳ vọng — đừng dùng làm tâm.
6. Độ nhạy hai chiều: giá trị phế liệu đội tàu cũ (hiện 0) vs chi phí lên đà sau TT99 chưa nằm trong EBITDA.
7. WARNING thiếu: bán niên tr.31 — phụ lục gia hạn FSO đến 2036 CHƯA KÝ (hợp đồng cũ hết 17/05/2026), đối tác là công ty mẹ; REPORT_r2 §5 không nhắc ⇒ thêm WARNING + mốc hai chiều.
8. Giá 18.000 (06/11); ở giá mới r2 có 29,8% dưới giá. HTM 1.015,87 không có trong BQ.
Giá ngụ ý: EBITDA đội tàu ~174 tỷ/năm (31% mức 561), hoặc mua hai tàu với NPV −25%.

## SZL (tâm r2 32.391 → skeptic điểm 29.510, khoảng 28.640–29.900; P10/P50/P90 26.469/29.306/32.787; 23,2% dưới 27.700; nhãn DƯỚI → TRONG vùng)
1. BLOCKING calc/model_r2.py:39-41: vốn hoá toàn bộ LN lõi cho cổ đông, bỏ quỹ khen thưởng phúc lợi: TM18 (BCTC tr.23) trích 15,778 tỷ trên LNST 2025 140,687 = 11,2%; số dư quỹ 23,96 tỷ (mã 323) chưa vào nợ. Phần trích hằng năm −2.383, số dư −477 ⇒ tâm 29.510. Tiền lệ SAS #2, #6. Tỷ lệ 11,2% mới một năm ⇒ ghi độ nhạy (KTPL 5% vẫn DƯỚI, 8% đã TRONG) và dẫn NQ ĐHĐCĐ 2026 nếu tra được.
2. Trọng số thời hạn 3/4–1/4 [UL] (model_r2.py:57): NQ 76/2020 mốc 2053 chỉ cho phần đất KCN Long Thành cho thuê lại 2004–08, mô hình áp cả xưởng Châu Đức/Tân Đức (TM11) ⇒ tách đồng hồ; 1/2–1/2: +385 (độ nhạy).
3. Vùng P10–P90 hẹp do ~1/3 giá trị cố định không biến động (cổ phần SZC/SZB theo giá một ngày ~9,2k, XDCB 8.445, nợ); trục chiết khấu holdco bị loại 'không dữ liệu' dù SNZ là comp holdco niêm yết ⇒ tra SNZ, cho vào độ nhạy (KTPL + holdco 25% ⇒ 28.052 ≈ giá). Ghi rõ vùng hẹp là do cấu trúc mô hình.
4. Trục LN phi tiền mặt một chiều; bỏ qua khấu hao ~91 tỷ/năm (TM9–10); BQ CF_OA 2019–9T/26 1.371 vs CF_Invest 1.704 (FCF −333 tỷ trong khi LNST cộng dồn 887) ⇒ đọc LCTT, tách capex duy trì/mở rộng, độ nhạy hai chiều.
5. Độ nhạy chiều lên (không vào base): BĐS đầu tư +166,2 tỷ trong 9T; LN lõi Q3×4 = 138,5 (+1.070). Ký quỹ dài hạn 147 tỷ theo PV đến 2053: +2,8k (độ nhạy).
6. Mốc N0 131,1 KHÔNG cherry-pick (giữa 115,3 năm hoá 2025 và 138,5 Q3×4).
7. Giá 27.700 (06/11). Cỡ sleeve 40 tr: P10 27.514 TRONG; kèm điểm 2 thì P10 27.745 ⇒ DƯỚI sát ranh — nhãn mong manh, ghi thẳng. Kiểm số cổ phiếu quỹ (~0,76 tr). Pháp lý SNZ/Đồng Nai sau 05/11 chưa tra lại.
Giá ngụ ý: LN lõi trước KTPL ≈115 tỷ/năm (= 2025) hoặc KTPL + holdco 25%.
