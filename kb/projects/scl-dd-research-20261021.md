# SCL (CTCP Sông Đà Cao Cường) — nghiên cứu thêm sau cờ DD `EQ_PHAI_THU_TANG` (21/10/2026)

> Yêu cầu: user duyệt "nghiên cứu thêm SCL" 21/10 23:28 ICT. Gói DD: `data/lag_dd/SCL_2026-10-19.json` (FLAG, hash `827ba0a2a6ce832e`),
> ack `RESEARCH` đã ghi. Tác giả: agent nghiên cứu đọc BCTC hợp nhất Q3/2026 (ký 15/10/2026) + công văn giải trình 1295/GT-SCL
> tại songdacaocuong.vn; số BQ `tav2_bq.ticker_financial`/`ticker`. Nguồn phụ: cafef 16/10, doanhnhan.baophapluat 16/10,
> nguoiquansat 16/10, chuyendongthitruong 20/10. **CHƯA qua phản biện độc lập** khi ghi file này (xem mục "Phản biện" cuối file).
> Trạng thái: SCL vẫn NGOÀI plan cho tới khi user ack PROCEED.

## Kết luận một dòng
Cờ "phải thu +159%" chủ yếu là **nền yếu (Q3/2025 thấp bất thường) + khoản TRẢ TRƯỚC cho người bán** (thiết bị dự án Phả Lại), không phải
nợ khách hàng phình to. Rủi ro THẬT là **dòng tiền, đòn bẩy và pha loãng**, không phải phải thu. Xếp **CHỜ có điều kiện**, không PROCEED mù.

## Đính chính tiền đề
- SCL **không phải xi măng/clinker**: gạch AAC, tấm ALC, vữa khô, keo dán gạch, phụ gia bê tông (nguyên liệu tro xỉ nhiệt điện, thạch cao).
- Phụ thuộc chính là **hệ sinh thái Vingroup/VinCons (~25% doanh thu theo lời Chủ tịch) + BĐS tư nhân + hạ tầng giao thông**; không thấy bằng chứng
  "ăn theo đầu tư công" như giả định ban đầu. Thuế xuất khẩu clinker và thừa cung xi măng gần như không liên quan trực tiếp.

## Phải thu (thuyết minh V.3–V.6, đã đọc trực tiếp)
| Khoản mục (tỷ đồng) | 30/9/2026 | 1/1/2026 |
|---|---|---|
| Tổng phải thu ngắn hạn (= số vendor 203,5) | 203,5 | 134,4 |
| Phải thu khách hàng | 116,0 | 88,5 |
| Trả trước cho người bán | 86,6 | 46,4 |
| Phải thu khác | 5,1 | 3,7 |
| Dự phòng | −4,1 | −4,2 |
- Nợ khách hàng chỉ +31% so với đầu năm. VinCons nợ 67,9 tỷ = 59% phải thu khách hàng (từ 48,2); không dự phòng riêng; **không có bảng tuổi nợ**.
- Trả trước 86,6 tỷ: LS XNK 19,3; Điện Kym 16,0; Long Thành Hải 12,8; Geetech 4,6; khác 33,9 (từ 6,5). Thuyết minh không nêu mục đích;
  "thiết bị Phả Lại (hợp đồng BIDV 184 tỷ để mở LC)" là **GIẢ THUYẾT có bằng chứng gián tiếp**.
- Nền yếu: phải thu vendor Q3/2025 chỉ 78,5 tỷ (các quý khác 134–199). Tỷ lệ phải thu/doanh thu quý: 0,73 (Q3/26) vs 0,53 (Q3/25), 0,57 (Q2/26), 1,08 (Q1/26).
- Mâu thuẫn DSO: DSO vendor 40,7 ngày khớp với phải thu KHÁCH HÀNG (116/263×90); DSO thô 65 ngày tính cả trả trước ⇒ khác định nghĩa, không phải dữ liệu hỏng.
- ⚠️ Gói DD tính AR = TỔNG phải thu ngắn hạn (gồm trả trước người bán) — định nghĩa cờ cần tách "phải thu khách hàng" khỏi "trả trước" (ghi nhận cho cổng DD).

## Dòng tiền / đòn bẩy / pha loãng (rủi ro thật)
- 9T/2026: CFO chỉ 9,9 tỷ vs LNTT 118 tỷ; capex 198 tỷ; tiền mặt 188 → 95 tỷ; vay ròng +86 tỷ. Gói DD dùng CFO 4 quý 93,7 tỷ (Q4/25 chiếm 83,8 tỷ; Q1/26 −96,2 tỷ) ⇒ tỷ lệ 0,80 che mất CFO ~0 của 9 tháng.
- Vay 416,5 tỷ: ngắn hạn 259,7 (BIDV 252,9, cao hơn hạn mức 230 tỷ ghi ở thuyết minh — chưa rõ vì sao), dài hạn 156,7 (gồm 26 tỷ vay cổ đông, lãi 10%). Lãi vay ~5,2 tỷ/quý, nhẹ so với EBIT ~54 tỷ.
- Phả Lại (AAC/panel/vữa/keo): vốn 262,9 tỷ, đã ghi 178 tỷ, dự kiến vận hành ~T11/2026.
- **Pha loãng**: cổ phiếu 22,4tr (9/2025) → 38,8tr (+73%). Q3 lợi nhuận +136% nhưng EPS chỉ 995 vs 721 (+38%). HĐQT có nghị quyết phát hành cho cổ đông hiện hữu 4/9 và 22/9/2026 (số 1191/1192) — **KHÔNG lấy được giá/tỷ lệ/ngày chốt**.

## Chất lượng lợi nhuận
- Biên gộp 41% (cùng kỳ 36%) do công suất, tự động hóa, giá nguyên liệu ổn định; không có thu nhập khác đáng kể (0,07 tỷ). Là sản lượng/vận hành, không phải khoản một lần.
- BCTC hợp nhất quý này lập LẦN ĐẦU (công ty con chưa rõ). Chi phí bán hàng tăng >2 lần cùng kỳ (40 tỷ).
- Doanh thu Q3: 277,9 tỷ gộp, 263,4 tỷ sau chiết khấu 14,6 tỷ; số 281,6 trong gói DD (suy từ NPM) không khớp cả hai.

## Định giá / thanh khoản
Giá 31.000 (21/10); PE 10,2; PB 2,26; giá +10% từ 15/10, ~gấp đôi 1 năm trước (16.540). ADV 3,8 tỷ/phiên (65 phiên). Lịch sử 25 phiên từ 2023: phân vị 5% −10,8%, tệ nhất −32%.
Kịch bản xấu: về 23.300 (giá 20/7) = −25%; lịch sử tệ nhất −32%; thêm rủi ro đợt phát hành chưa rõ giá/ngày chốt có thể rơi vào cửa sổ giữ lệnh.

## Phán quyết của agent nghiên cứu
CHỜ có điều kiện: cần (1) giá/ngày chốt đợt phát hành 2026; (2) tuổi nợ VinCons + mục đích trả trước. Không rõ trước 26/10 ⇒ giảm quy mô thay vì PROCEED đủ.
Ba câu hỏi IR: (1) giá/tỷ lệ/ngày chốt phát hành 2026 + vay BIDV vượt hạn mức; (2) tuổi nợ VinCons, điều khoản, mục đích 86,6 tỷ trả trước; (3) vốn còn cần cho Phả Lại/Lâm Đồng, lịch trả nợ BIDV, khi nào CFO dương.
Không tra được: nghị quyết phát hành 2026, tuổi nợ, kế hoạch 2026, số liệu đối thủ, bán nội bộ, vĩ mô ngành.

## Hệ quả cho hệ thống (Mike ghi, chờ user duyệt xử lý)
- Tín hiệu LAG dựa NP_R (tăng trưởng lợi nhuận ròng); với SCL EPS chỉ +38% do cổ phiếu +73% ⇒ "độ bất ngờ trên mỗi cổ phiếu" yếu hơn nhiều so với NP_R 136%. Chưa có kiểm nghiệm hệ thống về lớp lỗi này (pha loãng làm phồng NP_R).
- Định nghĩa cờ `EQ_PHAI_THU_TANG` nên tách phải thu khách hàng / trả trước người bán (cờ này bắt đúng một biến động nhưng hiểu sai bản chất).

## Phản biện — fundamental-skeptic 21/10 23:4x ICT: **REFUTED (độ tin cậy trung bình) phán quyết "CHỜ" ở trên**
Số liệu nguồn của writeup ĐÚNG (skeptic đối chiếu lại BCTC hợp nhất Q3/2026 + BQ: phải thu, trả trước, VinCons 67,9, CFO 9T 9,9, capex 198, vay 416,5, cổ phiếu 22,39→38,84tr), nhưng diễn giải nghiêng bi quan:
- **Dòng tiền**: CFO Q2+Q3 = 106 tỷ = 1,39× lợi nhuận (76,5); lỗ hổng 9T nằm hết ở Q1 (−96 tỷ); ~40 tỷ trả trước mang tính capex bị tính vào CFO. Nợ vay/vốn chủ (`STLTDebt_Eq`) GIẢM 1,03→0,78 so với cùng kỳ; nợ ròng/EBITDA ~1,4×; EBIT ~10× lãi vay.
- **Pha loãng bị nói quá**: EPS 721 của quý so sánh CHƯA điều chỉnh hồi tố cho cổ tức cổ phiếu (9% + 17%); ~46% cổ phiếu tăng thêm là cổ tức cổ phiếu (không có ý nghĩa kinh tế). Pha loãng thật: quyền mua 8tr cổ phiếu (35,7%, ~12.500đ, thực hiện đầu 2026) + ESOP 0,92tr. EPS tính lại tăng +76..97%, không phải +38%.
- **Bằng chứng có lợi writeup bỏ sót**: 1/1/2026 trả trước 30 tỷ cho Anhui Keda (nhà sản xuất thiết bị TQ) về 0 đến 30/9 ⇒ củng cố giả thuyết trả trước là thiết bị.
- **Tín hiệu LAG**: `lag_live_schedule.py:79-82,116` dùng NP_R/surprise theo LỢI NHUẬN RÒNG, không điều chỉnh số cổ phiếu; tính theo cổ phiếu surprise ~0,32–0,46 < ngưỡng 0,5 ⇒ hạng LAG_LO (8%) thay vì LAG_HI (10%); vẫn qualify (NP_R/cp ≥ 15%).
- **Rủi ro thật DUY NHẤT**: đợt QUYỀN MUA 15,38% cho cổ đông hiện hữu — Mike ĐÃ TỰ XÁC MINH trong `tav2_bq.corporate_action`: công bố 08/09/2026, trạng thái `P` (chờ), `exercise_ratio` 0,1538, CHƯA có giá phát hành, ngày giao dịch không hưởng quyền, ngày chốt (writeup nói "không lấy được tỷ lệ" — sai). Ví dụ: giá phát hành 15.000 ⇒ giá điều chỉnh lý thuyết ~28.900 (−6,9% ngày không hưởng quyền); 12.500 ⇒ ~28.500 (−8,0%, Mike tính). Bot không thực hiện/chuyển nhượng quyền ⇒ lỗ thật; backtest dùng giá điều chỉnh nên KHÔNG mô hình hoá rủi ro này.
- Phải thu: đứng được (mức 203 tỷ ngang 2024 — 206/188; Q3/2025 78,5 tỷ mới là bất thường). VinCons chậm hơn mặt bằng (~90 vs ~40 ngày) nhưng kể cả mất 30% ≈ 20 tỷ ≈ 4% vốn chủ và không lộ ra trong 25 phiên.
- Thanh khoản: đạt — 2 tài khoản tổng ~95 triệu ≈ 2,5% ADV (3,86 tỷ), trần `cap_lag_orders` 20%.
- Lịch sử 20 sự kiện LAG của chính SCL: trung bình +7,8%, trung vị +9,7%, 65% lãi, tệ nhất −25,9%.
- **Khuyến nghị skeptic: PROCEED có điều kiện** thay vì CHỜ (CHỜ quá 26/10 = DROP không đủ lý do; tuổi nợ VinCons không về kịp và không ảnh hưởng 25 phiên): (1) quy mô theo LAG_LO 8% của book LAG (~4% NAV ≈ 39tr SpaceX, 37tr ZaloPay); (2) luật thoát: nếu ngày chốt quyền mua 15,4% rơi trong thời gian giữ ⇒ bán TRƯỚC ngày giao dịch không hưởng quyền (hoặc user tự đăng ký mua quyền), ghi vào plan; (3) HỦY vào lệnh nếu trước 26/10 có tin VinCons chậm trả hoặc công bố giá phát hành thấp kèm ngày chốt sát.
- Việc nên làm ngoài mã (chưa làm, cần user duyệt): (i) cờ `EQ_PHAI_THU_TANG` tách phải thu KH khỏi trả trước người bán; (ii) R&D riêng: surprise LAG theo mỗi cổ phiếu có điều chỉnh cổ tức cổ phiếu + mô hình hoá rủi ro ngày không hưởng quyền của quyền mua (kèm quant-skeptic); (iii) xác nhận hệ thống cảnh báo ex-date (`nav_exdate_forecast`, `corp_action_daily`) có bắt ĐÚNG sự kiện quyền mua của mã đang giữ.
