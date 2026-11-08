# Đính chính từ fundamental-skeptic 08/11/2026 — TV2, DCM, HPG, SCL, TV1 (áp trong vòng 3). Kiểm từng điểm bằng calc, đừng chép mù. Giá tham chiếu = đóng cửa 06/11/2026 (BQ tav2_bq.ticker; 07/11 thứ Bảy).
Quy tắc chung: khoản lệch khỏi sổ sách/NPV0 trong BASE phải có dòng 'cơ sở dữ liệu' + nguồn; chỉ nhận định (kể cả Bobby) ⇒ ra khỏi base sang độ nhạy/kịch bản có xác suất. Moat chỉ cộng khi bền, không trừ (user 08/11). P10/P50/P90 ở MỨC KẾT CỤC bằng _shared/wpct.py. Báo CK ở cả cỡ tham chiếu 5 tỷ và cỡ sleeve thật. Headline = mô hình cơ sở hiện hành sau đính chính; phiên bản thay thế chỉ là độ nhạy song song.

## TV2 (giá 27.400; tâm r2 15.832 → skeptic 16.463–17.483)
1. BLOCKING: bỏ sàn P/E=0 khi ROE<g (model_tv2_r2.py dòng 29 max(...,0.0)). Cơ sở: cổ tức 1.000đ/cp/năm (67,5 tỷ) 2023–25 khi LNST TTM 53–65 tỷ ⇒ trả ≥100% LN. Khi ROE<r dùng chia hết (P/E=1/r). P10 2.726 (P/B 0,14) là artifact; giá thấp nhất từ 2022 = 18.300, đáy 2023–25 P/B 1,6–1,9.
2. Nhánh 'sập 70%' áp lên 110 tỷ ⇒ 33 tỷ, dưới đáy quan sát (LNST TTM min 53 tỷ). Neo nhánh sập ở MỨC đáy quan sát ~53–72 tỷ (skeptic dùng 64 tỷ), không phải tỷ lệ áp lên mọi kịch bản.
3. Nhánh cao P/E 8,3–8,8x > P/E thị trường thực trả ở đỉnh LN 2017–21 (7,45x = SKEPTIC CAO-1) ⇒ cap hoặc báo song song. Biến thể skeptic: A tâm 17.268/P10 6.319/P90 30.675; B (A+sập neo 64 tỷ) 17.483/7.677/30.675; C (B + P/E 1/r mọi nhánh) 16.463/7.677/26.733 (C ⇒ P90 < giá ⇒ nhãn TRÊN vùng). Chọn headline có lý giải; báo A/B/C song song.
4. Tâm trượt 21.000→18.784→15.832 qua 3 vòng mà không có thông tin mới — ghi bridge nguyên nhân từng bước.
5. Số CMC 666,4/188,6 tỷ chỉ trong PDF scan (txt rỗng): đọc bằng pymupdf (fitz) render trang, hoặc ghi 'chưa kiểm được'. WARNING '13 pháp nhân' giữ nguyên.
6. Giá ngụ ý (nêu trong báo cáo): LNST ~235–250 tỷ vĩnh viễn gồm ~44% lãi float trên tiền ứng, g 4%, ROE 17–19%, CMC không mất đồng nào.

## DCM (giá 32.100; tâm r5 24.326 → skeptic 24.700–26.800, điểm 25.723)
Tài liệu: agents/Taylor/research/dd_DCM_20261104/ (REPORT_r5.md, calc/model_r5.py...). Viết vòng 3 thành r6 trong thư mục đó (không đè r5) + SUMMARY.json chuẩn như các mã khác.
1. BLOCKING: P10/P90 hiện là phân vị kỳ vọng từng ô (0,8 CYC + 0,2 STRUCT). Tính lại ở mức kết cục: sym3 P10 19.817/P90 29.210, 100% trọng số dưới giá 33.000 (nay 32.100); sym5 P90 ~32.059. Đưa trục khí (V1/V2, Nam Du 30–60,5%, I_C 20/25) VÀO lưới hoặc báo bản song song (STANDARD_r2 điều 2).
2. Con số '297 USD/t ngoài dải bền' là sản phẩm của nhánh STRUCT 125 giữ 20% VĨNH VIỄN. Nhãn STRUCT do Bobby đặt cho 2–4 quý (model_r2 chú thích 'KHÔNG phải trọng số vĩnh viễn'), không có dòng cơ sở dữ liệu. Chỉ nhánh CYC: giá hàm ý biên ~253; thêm sửa hồi quy: 237–249 — trong dải bền 180–260 của Bobby, sát biên thực 2025 (257). Sửa câu dẫn đầu.
3. Hồi quy n=5 bị 2022 kéo: ở biên thấp phần dư 2023–24 TB +138 tỷ. 3 cách cho LNST@biên179: fit 2016–25 = 1.367; bỏ 2022 = 1.388; so với r5 1.265 (cao hơn 100–140 tỷ ⇒ tâm +1,0–1,4k đ/cp). Báo cả 3 biến thể hoặc fit lại có lý giải.
4. P(thuế XK 0%)=0,55 của Bobby trong base (+1.034) chỉ là nhận định ⇒ ra khỏi base sang độ nhạy. STRUCT vĩnh viễn (−996) cũng ra khỏi base (nếu không có cơ sở). Áp luật 03/11 cho cả hai nhánh rồi sửa hồi quy ⇒ skeptic ra 25.723.
5. Rủi ro giảm CHƯA vào base — báo ở độ nhạy: hụt khí 2028–29, capex thay nhà máy, thuế hiệu dụng 2021–24, đồng hồ khí 2035+ (−7,6k).
6. Thiếu: câu 'không đủ điều kiện §2.5' (GPM thấp hơn DPM 8/10 năm, PB 1,47) + HARD ABANDON (STANDARD_r2 điều 8); cỡ sleeve thật (điều 6); LOCK_md5 thiếu CSV đầu vào (điều 9). SĐBS 12 mới là DỰ THẢO; hợp đồng khí là giao dịch bên liên quan khép kín (WARNING).

## HPG (giá 21.200; tâm r2 16.286 → skeptic 18.558–19.529)
1. BLOCKING: kịch bản TRUNG LẬP giữ 80% LN (VCSH 148,8 → ~217,6 nghìn tỷ, +68,8 nghìn tỷ) nhưng vốn giữ lại sinh lời 0% ⇒ ROE terminal 11,8% < r 13,5% ⇒ RI terminal âm vĩnh viễn; ROE 2027 17,5% mà P/B trung lập 0,95. Trái luật 20 (XDCB 16,1 nghìn tỷ + cam kết ~19,5 nghìn tỷ bị phạt ngầm) và REPORT §3d/§3e. Sửa: vốn giữ lại sinh lời tối thiểu bằng lãi tiền gửi sau thuế 6,0% (sàn) hoặc phần capex sinh lời = r (NPV0) + phần còn lại lãi tiền gửi. Skeptic: tâm 18.558 (sàn 6%) / 19.529 (13,5% cho capex); % dưới giá 66,6% / 59,2% (so 82,3%).
2. Thuế terminal 20% từ 2030 chưa có nguồn mốc hết ưu đãi (−1.855 so giữ ~12%) ⇒ chuyển sang độ nhạy hoặc dẫn nguồn.
3. Nhánh TỐT g_RI=g (+270) = thưởng moat ngầm, trái quy ước 08/11 (NARROW không bền thì không cộng) ⇒ bỏ.
4. Trọng số trục TLSH lệch xuống không có dữ liệu [UL] (−193) ⇒ độ nhạy.
5. Quét tin pháp lý 31/10–06/11 (TLSH, bên mua 2 công ty BĐS); mở bản gốc QĐ 1917 (mới thấy trên báo). Giá ngụ ý: vốn giữ lại sinh lời ~11,6% sau thuế ~ ROE terminal trung lập ~15,5% sau thuế 20% (ROE5Y 16,9%, TB 2022–25 9,6%).

## SCL (giá cum-quyền 29.400, TERP 27.139; tâm r2 22.769 → skeptic 20.600–23.700, headline lõi sửa GPM 21.813)
1. BLOCKING: REPORT_r2/SUMMARY vẫn headline 22.769 dù đã biết lỗi GPM_P0=TTM (đúng 21.813, P90 26.672; bigquery_dictionary.json xác nhận). Đổi headline sang lõi đã sửa ở REPORT/SUMMARY/ADDENDUM.
2. Quy ước một chiều có công bố nhưng không cơ sở dữ liệu: (a) bội số áp lên LN năm hiện tại E0 thay vì năm tới E1 (~−880 đ/cp; SKEPTIC_R2 đã nêu chưa sửa) ⇒ báo bản E1 song song và chọn headline có lý giải; (b) CK 4,5% @5 tỷ (219% ADV, ngoài vùng căn bậc hai) vs cỡ sleeve 0,85% (~+840 đ/cp) ⇒ báo cả hai, nhãn nêu cỡ; (c) trục lỗ phải thu xác suất [UL] trong base (~−90) ⇒ độ nhạy. Gộp 3 khoản ⇒ P90 ~28.800 (giá chỉ còn cao hơn ~2%); thêm IRR Phả Lại ~29.350. Biến thể đối xứng có nhánh TROUGH + khung nợ theo mệnh giá kéo tâm xuống ~1.100–1.200.
3. Sửa câu 5F §5 'không sát ranh giới' (chỉ đúng ở CK 5 tỷ và E0).
4. So sánh cùng cơ sở: giá còn quyền (cum) vs tâm trước quyền, hoặc TERP vs tâm sau quyền (hồ sơ chỉ có quyền mua 100:15,4453 giá 12.500; không thấy cổ phiếu thưởng cùng ĐKCC 10/11; ESOP 0,92 triệu cp đã nằm trong pha loãng). Xác nhận lịch chuyển nhượng quyền qua CBTT sàn.
5. Bảng cân đối (vốn chủ, nợ, XDCB, phải thu 58,5% tập trung một tập đoàn BĐS) chỉ truy về PDF scan ⇒ đọc bằng pymupdf (fitz) hoặc ghi 'chưa kiểm'. Giá ngụ ý: LN ~140,6 tỷ/năm không quay về TB, g 4%, ROE 17,5%, hoặc r ~11,1% (lãi huy động ~5,0%); CFO 9T 9,9 tỷ vs LN 94,4 tỷ là phản chứng.

## TV1 (giá 20.400; tâm r2 15.379 → skeptic 15.700–16.600)
1. BLOCKING: nhánh truy thu (p=0,10) nhân chéo ĐỘC LẬP với giá PPA (949/600/520/440) — truy thu chỉ xảy ra nếu bậc giá 2018 ràng buộc ⇒ khi đó PPA tương lai = 340. Làm nhất quán (truy thu chỉ trong nhánh 340): tâm 16.570, P10 8.420; nếu giữ xác suất chung 0,10 dồn hết vào nhánh 340: tâm 15.734, P10 3.522. Tính lại P10 và ngưỡng nhãn 'DƯỚI vùng' (REPORT_r2.md:104; câu 'P10 31% do truy thu' sai).
2. Truy thu 'đủ' 2022–26 (−17.397 đ/cp) không có văn bản đòi; EVN trả 949 suốt 5 năm đã kiểm toán; blind và core v2 trước đó xếp 'KHÔNG vào tâm'; r2 đưa vào tâm không có thông tin mới ⇒ ra khỏi base sang kịch bản/độ nhạy, trừ khi có cơ sở dữ liệu.
3. Mâu thuẫn nguồn: core ghi 'Dự thảo HĐ sửa đổi 05/2018', REPORT_r2 §1 'bậc giá 2018 đã ký' ⇒ kiểm văn bản gốc (agents/Taylor/research/dd_TV1_20261102/LEGAL_PPA_20261102.md, phụ lục 05).
4. WARNING §6 thiếu: VnExpress 02/07 — TV1 trong '13 công ty liên quan', 'nhà thầu đều có sai phạm' (có ở REPORT 02/11 §159).
5. KTPL 20% vĩnh viễn từ 1 năm (FY2025): kiểm FY2023/24; độ nhạy 15% ⇒ 16.595, 10% ⇒ 17.818. Biên lịch sử core §B dùng Σ(Rev quý × EBITM_P0 TTM) — kiểm lại (ảnh hưởng nhỏ).
6. Sửa dẫn chiếu: TV1 thuộc nhóm (a) scandal cá nhân ⇒ §2 chứ không phải §2.5 (kết luận không đủ điều kiện vẫn đúng). 500–600 chỉ là lời lãnh đạo qua KBSV, chưa kiểm bản gốc. Giá ngụ ý: PPA ~558–631 (biên 9,2–11%); mức duy nhất có văn bản là 340. Lưu ý: TV1 đang trong plan SELL — định giá không được neo vào quyết định bán (ghi rõ thiếu thiên lệch xác nhận).
