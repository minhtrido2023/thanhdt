# Trứng vàng DNSE — bản chất pháp lý (legal-vn 2026-09-27)
> Chuyển nguyên văn từ `kb/current_ops.md` (trim context_pack 2026-10-08). Trạng thái quyết định
> (user chốt 2026-10-05: Trứng vàng = tương đương tiền) vẫn ở `kb/current_ops.md`.

## Chuyển từ kb/current_ops.md L17-30 (trim 2026-10-08, Wags_20261008_133659) — Trứng vàng — dòng trạng thái đầy đủ + đính chính bản chất 2026-09-27
- **Trứng vàng** (`egg.totalValue`): SpaceX ~100,9tr / ZaloPay ~102,2tr (đo 09-27), đã cộng NAV tự động — KHÔNG phải `availableCash`. ⚠️ **RÚT VỀ TRONG NGÀY, KHÔNG phải T+1** (đính chính 2026-09-27, Mafee job `Mafee_20260927_091828`: SpaceX 17/09 egg 100,9tr→51,0tr VÀ `availableCash` +49,8tr trong CÙNG snapshot 11:00:11 phiên sáng ⇒ tiền dùng mua được ngay phiên đó). ⚠️ **KHÔNG phải tiền gửi ngân hàng** — DNSE mô tả là "Sinh Lời Theo Ngày" qua giao dịch TRÁI PHIẾU niêm yết ⇒ không có bảo hiểm tiền gửi, phụ thuộc tổ chức phát hành; lãi đo thật **8,543%/năm** và DNSE **tự khấu trừ TNCN trước khi trả** nên số đó đã là net. Không thấy trần số dư (ZaloPay vượt 102tr vẫn cộng lãi phẳng); "Tài khoản Không Ngủ" là SẢN PHẨM KHÁC (trần 30 tỷ), đừng lẫn. `manual_offbook_assets_vnd` ĐÃ ĐÓNG vĩnh viễn 07-23.
  ⚠️ **ĐÍNH CHÍNH BẢN CHẤT 2026-09-27 (legal-vn, bus `dnse-trung-vang-legal-review-20260927`) — KHÔNG phải repo.**
  Mô tả "bond repo" trước đó của Mike là SAI. Bằng chứng từ chính FAQ DNSE + 3 dấu hiệu gián tiếp
  (phí lưu ký 0,3đ/trái phiếu/tháng, coupon về THẲNG TK khách, khách chịu thuế chuyển nhượng 0,1%):
  khách **SỞ HỮU THẬT** trái phiếu niêm yết, **lưu ký tại VSDC**; cấu trúc = 2 giao dịch mua bán
  dứt điểm + cam kết hợp đồng DNSE mua lại. ⇒ phần ĐANG GIỮ **không phải** claim không bảo đảm vào
  DNSE. Ba rủi ro THẬT, khác nhau: (a) TCPH vỡ nợ ⇒ chủ nợ không bảo đảm (Luật Phá sản 2014 Đ54);
  (b) cam kết mua lại của DNSE vô giá trị ⇒ **mắc kẹt tới đáo hạn / bán giá thị trường**, không mất
  trắng; (c) tiền đang trên đường lúc DNSE vỡ nợ — **không tra được** điều luật nào tường minh loại
  tiền khách khỏi khối tài sản phá sản (Đ89 LCK 2019 + TT121 Đ17-18 là nghĩa vụ HÀNH CHÍNH).
  **Việt Nam KHÔNG CÓ Quỹ bảo vệ nhà đầu tư** (đề xuất 2014, không vào Luật CK 2019) — đây là kết
  luận xác định, không phải "chưa tra được". Thuế: coupon **5%** + chuyển nhượng **0,1%** (TT111/2013;
  TT92/2015 bỏ phương án 20%; 0,1% giữ sau 01/7/2026 theo L109/2025 + NĐ253/2026 + TT87/2026), khấu
  trừ tại nguồn, **không quyết toán**. CTCK được phép làm việc này: TT121/2020 Đ28.3.

## Chuyển từ kb/current_ops.md L34-35 (trim 2026-10-08, Wags_20261008_133659) — Trần đề xuất (chưa user chốt) — đã bị user chốt 2026-10-05 thay thế (dòng ✅ ở current_ops)
  Trần đề xuất (chưa user chốt): ~2% NAV/một TCPH (haircut 50% ⇒ max loss ≤1% NAV), sleeve ≤10% NAV
  — mức hiện tại ~100,9tr / ~102,2tr **đã ở hoặc vượt nhẹ trần tổng**.

