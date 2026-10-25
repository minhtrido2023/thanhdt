# Thu thập bản tin "Mực nước hồ thủy điện" (Tạp chí Công Thương) — 2026-10-25

**Kết luận: KHÔNG có bản tin hằng ngày nào cho 01–25/10/2026. Phủ 0/25 ngày.** CSV `avc_sb4_daily.csv` ghi rõ 25 dòng "không tìm thấy", không nội suy.

## Bằng chứng
- Trang chuỗi `tapchicongthuong.vn/hashtag/muc-nuoc-ho-thuy-dien-4081.htm` (HTTP 200): bài mới nhất = 07/12/2023 ("ngày 6/12"); trang 2 lùi về 11/2023. Không bài nào sau 12/2023. Mẫu URL cũ: `/muc-nuoc-ho-thuy-dien-ngay-D-M--<slug>-<id>.htm` (id ~114k; bài 2026 id ~557k).
- Xác minh ngày đăng bằng meta `datePublished` (bản 22/11 → 2023-11-23).
- Web search (standard + extended, lọc tapchicongthuong/congthuong/moit) không trả bản tin nào 2024–2026. Kết quả "ngày 10/10, 13/10, 19/10" là 2023 (id 112xxx).
- Kết quả 2026 liên quan chỉ là bài rời, không phải bản tin ngày: A Vương 368,11 m ngày 03/05/2026 (MNDBT 380 m); EVN báo hồ miền Trung cao hơn kế hoạch đến 14/10/2026; bài xả/giảm lũ A Vương–SB4 (năm chưa xác minh, có thể 2025).
- `moit.gov.vn/tin-tuc/phat-trien-nang-luong` còn đăng tin 2026 (mới nhất thấy 30/09/2026) nhưng tôi không thấy bản "Tình hình hồ thủy điện ngày X" 2026 trong trang đầu; chưa dò sâu.
- Ngay cả bản tin 2023, bảng chi tiết A Vương/SB4 chỉ có khi nguồn Cục KTAT&MTCN báo; bản 29/11/2023 chỉ nêu A Vương/SB4 trong đoạn yêu cầu đón lũ của Quảng Nam, không có số Q xả. Không đảm bảo có số liệu từng ngày.

## Đề xuất thu thập tự động (CHƯA cài, chờ duyệt)
Bản tin Công Thương không còn là nguồn dùng được. Hướng khác, cần Mike/user chọn rồi Winston dò kỹ:
1. **EVNGENCO2 / thuỷ điện A Vương, SB4** và **Cục KTAT&MTCN (atmt.gov.vn / moit.gov.vn)** — tìm báo cáo hồ chứa hằng ngày.
2. **Cảnh báo/thông báo xả lũ** của Ban Chỉ huy PCTT Quảng Nam/Đà Nẵng (VOV, Báo Quảng Nam) — chỉ có khi xả, thiên lệch về mùa lũ.
3. **Dữ liệu thuỷ văn** (kttv, hydro.gov.vn / vndms.dmc.gov.vn) — lưu lượng sông Vu Gia/Bung theo trạm, thay thế gián tiếp.
Script mẫu: curl + parse, 1 lần/ngày sau 17:00 ICT, idempotent theo ngày. Rủi ro: đổi cấu trúc trang, chặn UA, nguồn dạng PDF/ảnh.

## Nhận xét giữ/xả (mục 4)
Không có số Q xả/Q về của 10/2026 → **không đưa ra được nhận xét**. Chỉ có tín hiệu mềm: quy trình A Vương từ 15/10 hạ mực nước về 372 m với xả nhỏ <10 m³/s để đón lũ (bài không ghi năm, chưa xác nhận là 2026) — không dùng làm chỉ báo.
