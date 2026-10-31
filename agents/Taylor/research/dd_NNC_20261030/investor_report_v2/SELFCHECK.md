# Tự kiểm v2 — NNC_DD_investor_report_20261031_v2 (job Taylor_20261031_030545, 31/10/2026)
md5 (md pdf html): 81e57a3195eb90082de0471d9fc697a9 0156c069506b1f6122339cfa252ab3ee 831100693d4379e71320dd1988d2ceb7  · PDF 17 trang (bản gốc 14) · bản gốc investor_report/ KHÔNG bị ghi đè.
Tái lập: `/home/trido/thanhdt/wc_venv/bin/python -I build_report.py pdf`; email dry-run: lệnh trong skill, subject từ EMAIL_SUBJECT.txt.

## Thêm mới (chỉ hình + chú thích + nguồn)
- fig_19_map_assets (mục 4, sau sơ đồ tài sản), fig_20_map_markets (mục 3), fig_21/22_products (mục 4 'Sản phẩm') + CSV từng hình; Phụ lục C và D cập nhật; banner dựng lại; tiêu đề: "vách" → “vách”; EMAIL_SUBJECT dùng “vách”, 0 nháy kép thẳng.
## Kiểm
- grep luật 4/12 trên md + subject + CSV hình mới: cả hai lệnh rỗng (đã chạy; không còn hit "giá vốn" ngoài mục COGS cũ — lệnh 1 đã loại "giá vốn").
- Diff số: diff md gốc↔v2 chỉ thêm dòng mới (toạ độ, tr. ảnh, 2008); không số cũ nào đổi (so tần suất token số).
- Nhìn bằng mắt: tr.1 (banner đúng dấu), tr.5–7 (khung ảnh, 2 bản đồ), tr.9; nhãn không chồng, ảnh không méo, bảng không tràn.
- Dry-run email: 24 ảnh, 11,1 MB, 24/24 thẻ <img> có alt đóng đúng; KHÔNG gửi thật.
## Giới hạn / chưa làm được
- Toạ độ xã Tân Lập không tra được ⇒ chấm ở trung tâm huyện Đồng Phú (ghi rõ trong chú thích). Mỏ Tam Lập 1 khu II, Tam Lập 2/3: không có nguồn vị trí ⇒ không vẽ; chỉ chấm khu vực huyện Phú Giáo (trung tâm huyện, nêu rõ không phải cơ sở NNC). Biên Hòa dùng làm đại diện Đồng Nai; Vành đai 4 không vẽ (chưa tra toạ độ).
- Ranh giới tỉnh bản 2008. Ảnh do công ty công bố (BCTN tr.6–9), không kiểm chứng độc lập; thiếu ảnh đá 0x4 Dmax 25 và 1x1 (đã nói trong chú thích). Ảnh BCTN tr.5 (cổng) không dùng vì không chắc là Mũi Tàu. nuinho.vn truy cập được qua http, có trang sản phẩm; chưa dùng ảnh từ đó.
- Chân chữ ảnh có câu "trang nêu trong CSV" (nhãn trong PNG) — nhỏ, chưa sửa.
