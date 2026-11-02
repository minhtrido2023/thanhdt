# DRI — DD khủng hoảng NGÀY 1 (tóm tắt nhanh) · 02/11/2026 ~11:05 ICT · Taylor (job Taylor_20261102_040003)

## 1. Chuyện gì xảy ra
- Cổng giá bắn 11:00: DRI 13.400 (tham chiếu 14.200, −5,6%), VNINDEX −0,8%. Lúc 11:0x DNSE: **13.500 (−4,9%)**. Sàn 12.100, chưa chạm sàn.
- Diễn biến trong phiên (DNSE bars 1 phút): mở 14.000, trượt dần 13.900 → 13.700 → 13.500, không có gap sàn. Khối lớn nhất: 151.000 cp lúc 09:51 @13.500. **KL tới 11:00 = 848.400 cp**, so với KL TB 1 tháng 1,67 triệu (BQ `ticker.Volume_1M`, 30/10) ⇒ **không phải KL hoảng loạn**.
- Đây là chặng tiếp nối đà giảm đã có: đóng cửa 16.200 (20/10) → 15.300 (21/10) → 14.700 (26/10) → 14.400 (27/10) → 14.000 (30/10) (BQ `tav2_bq.ticker`). Từ 20/10 tới giá hiện tại ≈ −17%. (Lưu ý: tham chiếu UPCoM 14.200 = giá bình quân phiên trước, khác giá đóng 14.000.)
- **Cả nhóm cao su cùng giảm phiên sáng** (DNSE, lúc ~11:02): TRC −4,8% (21.050/22.100), PHR −3,2% (30.000/31.000), DPR −1,4%, DRC −1,2%, GVR −1,0%, DRG 0%. ⇒ phần "idio −4,8%" so với VNINDEX phần lớn là **yếu tố NGÀNH**, không phải tin riêng DRI. Chưa tìm thấy tin giá cao su thế giới ngày 02/11 (bài gần nhất 28/10: TOCOM RSS3 −1%, SHFE +0,7%).

## 2. Pháp lý (legal-vn / Wendy, 7 ngày 26/10–02/11)
- **Chưa thấy tin pháp lý** dính DRI: không khởi tố/điều tra, thanh tra, xử phạt UBCKNN, cảnh báo/kiểm soát/đình chỉ giao dịch UPCoM, bắt/miễn nhiệm lãnh đạo, tranh chấp đất Lào/Đắk Lắk. Không có tin mới về DRG/Dakruco hay GVR.
- Tin cũ, ngoài cửa sổ: 22/09/2025 Cục Thuế Đắk Lắk phạt + truy thu ~144 triệu (khai sai GTGT/TNDN 2024) — nhiễu ([baophapluat](https://doanhnhan.baophapluat.vn/vuong-sai-pham-cong-ty-dau-tu-cao-su-dak-lak-dri-bi-phat-va-truy-thu-thue-gan-144-trieu-dong-86872.html)).
- Giới hạn: không đọc trực tiếp được danh sách cảnh báo HNX và trang xử phạt ssc.gov.vn; mục tin Vietstock bị chặn quyền.

## 3. Tin doanh nghiệp
- CBTT gần nhất tìm được: BCTC Q3/2026 hợp nhất + mẹ đăng ~29/10 ([cafef](https://cafef.vn/du-lieu/dri-3009667/dri-bao-cao-tai-chinh-quy-32026.chn)) — đã phân tích trong hồ sơ (LNST mẹ Q3 25,98 tỷ, −33% YoY; 9T 167,75 tỷ, +44%; thành phẩm tồn 64,99 → 138,81 tỷ; CFO 9T/LNST 0,75×). Xem `mike/kb/projects/dri-dd-summary-20261030.md`.
- **Chưa thấy tin** giao dịch nội bộ / cổ đông lớn / bán giải chấp / thoái vốn mới trong 7 ngày. Lịch sử: Dakruco giảm sở hữu về ~45% (03/2025) ([tinnhanhchungkhoan](https://www.tinnhanhchungkhoan.vn/cao-su-dak-lak-thoai-von-dri-tag217898.html)).
- Chuyển sàn HOSE: SXKD 9T (20/10) nói "phấn đấu hoàn thành trong Q4/2026"; **chưa thấy CBTT** HOSE chấp thuận.
- Khuyến nghị bên ngoài: Mirae MUA 05/10/2026, mục tiêu 20.100 ([24hmoney](https://24hmoney.vn/stock/dri)) — cao hơn nhiều so với FV nội bộ r4 (8,0–12,5 nghìn).

## 4. Đánh giá: có dính pháp nhân / tài sản lõi không?
- **KHÔNG thấy** sự kiện chạm pháp nhân hay tài sản lõi (vườn Lào, Dakruco, Quỹ TDND). Không trigger nào trong `dri-triggers-20261027.md` chạm hôm nay (THOÁT: Lào/Dakruco/TROUGH — không; GIẢM NỐT: SXKD T10 chưa ra).
- Giải thích hợp lý nhất (suy luận, chưa có tin xác nhận): **bán ngành cao su + tiếp nối phản ứng với Q3 kém** (miss sản lượng bán, tồn kho tăng). Giá 13.500 vẫn trên vùng FV cơ sở r4 9,1–11,1 nghìn; giá vốn bình quân 2 tài khoản ~12.263 (còn lãi ~+10%).
- Cờ rủi ro: **KHÔNG đặt** (không có tin pháp lý, không có thay đổi chính sách ngành). Mặc định **GIỮ** theo quyết định user 01/11.

## 5. Câu hỏi mở — theo dõi các ngày tới
1. Giá cao su thế giới (TOCOM/SHFE/SGX TSR20) phiên 30/10–02/11: có đợt giảm mạnh không? (Giải thích nhóm cao su cùng giảm.)
2. **SXKD tháng 10 (~10/11)**: tấn bán < 1.000 t HOẶC LNTT lũy kế 10T < 208,21 tỷ ⇒ trình user GIẢM NỐT (trigger đã duyệt).
3. BCTC Q3 chi tiết: tiền gửi Quỹ TDND Cao su ĐL có vượt 70 tỷ (mốc 30/09) không; Dakruco vay thêm/gia hạn không.
4. CBTT HNX/UPCoM: giao dịch cổ đông lớn/nội bộ, kết quả lấy ý kiến cổ đông, hồ sơ chuyển HOSE.
5. Khối lượng: nếu các phiên tới KL > 2× TB 1 tháng cùng giảm sàn mà không có tin ⇒ coi là tín hiệu thông tin chưa công bố, nâng mức.

Nguồn giá/KL: DNSE ReadOnly (`intraday_price_watch.py` quote/bars), BQ `tav2_bq.ticker` (đóng cửa 20–30/10).
