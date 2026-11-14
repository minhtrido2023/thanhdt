# Quy tắc chung cho mọi tác nhân fact-pack PAT (CTCP Phốt pho Apatit Việt Nam, mã PAT)

Mục tiêu: thu BẰNG CHỨNG VẬN HÀNH thật để người định giá (không biết giá thị trường) phán đoán khả năng sinh lời của doanh nghiệp. Bạn chỉ THU THẬP + ĐỐI CHIẾU SỰ KIỆN, KHÔNG định giá, KHÔNG khuyến nghị mua/bán.

## MÙ GIÁ — tuyệt đối
- KHÔNG thu thập, KHÔNG ghi, KHÔNG nhắc: giá cổ phiếu, P/E, P/B, vốn hoá, EV, mục tiêu giá, khuyến nghị, báo cáo phân tích CTCK có định giá, tin "cổ phiếu PAT tăng/giảm". Gặp thì BỎ và ghi 1 dòng "ĐÃ BỎ: <loại nội dung, nguồn>" ở cuối file (không chép số).
- Nếu cần EPS/cổ tức/mệnh giá/số cổ phần thì CHỈ lấy số liệu doanh nghiệp công bố (không lấy giá thị trường).
- Cấm đọc: bất kỳ thư mục `agents/Taylor/research/dd_PAT_20261114/`, `investor_report/`, `kb/dd_price_zones.json`, `kb/projects/pat-dd-*`, `blind_val_20261114/REPORT_BLIND.md`, `blind_val_20261114/assumptions_blind.md`, `kb/memory/*`, `bus/*`. CẤM chạy grep/rg lan rộng trong repo để tìm "PAT" (repo chứa kết luận cũ). Chỉ đọc các tệp được liệt kê trong nhiệm vụ.
- Được đọc (đầu vào sạch): `agents/Taylor/research/blind_val_20261114/inputs/` (ảnh BCTC trang `src/png_q326`, `png_bn26`, `png_kt25`, PDF; `facts_extracted.md` = trích tay, CÓ THỂ SAI → khi dùng phải đối chiếu lại ảnh gốc; `sector_read_phot_pho_20261114.md`; `macro_snapshot_20261114.md`). Đường dẫn tuyệt đối gốc: /home/trido/thanhdt/wt-1571194491489091644/agents/Taylor/research/blind_val_20261114/inputs/

## KỶ LUẬT BẰNG CHỨNG
- Mỗi fact = 1 dòng/bullet có: nội dung (số + đơn vị + kỳ), NGUỒN (URL đầy đủ HOẶC tệp+trang), NGÀY công bố/truy cập. Số chép từ ảnh BCTC phải ghi trang. Không nguồn = không phải fact.
- Phân loại mỗi fact: [CÔNG BỐ DN] / [CƠ QUAN NHÀ NƯỚC] / [BÁO CHÍ — ghi tên báo] / [TỰ TÍNH — ghi công thức]. Số báo chí phải đối chiếu nguồn gốc nếu được; mâu thuẫn giữa nguồn thì ghi CẢ HAI, không tự chọn.
- Không biết/không tìm được = ghi "KHÔNG TÌM ĐƯỢC (đã thử: …)". CẤM suy đoán, CẤM điền bằng "thông thường/có lẽ". CẤM thêm giả thuyết hoặc nhận định thiên lệch (bi quan hay lạc quan); chỉ chép sự kiện + ngày + nguồn. Giữa hai cách hiểu có thể có, trình bày CẢ HAI cùng bằng chứng nào phân biệt được.
- Web: ưu tiên nguồn gốc (site công ty/IR, HOSE/HNX/UBCK CBTT, cafef/vietstock chỉ để tìm văn bản gốc, công báo, báo cơ quan nhà nước). Tải được PDF thì lưu vào thư mục `factpack/raw/` (tạo nếu chưa có) và dẫn tên tệp.
- Ghi đầu ra ở: /home/trido/thanhdt/wt-1571194491489091644/agents/Taylor/research/dd_PAT_objective_20261114/factpack/<tên tệp được giao>. Cuối tệp: mục "ĐÃ BỎ", mục "KHÔNG TÌM ĐƯỢC", và mục "ĐIỂM MÂU THUẪN" nếu có. Trả lời cuối: ≤12 dòng tóm tắt danh mục fact + khoảng trống, không chép lại cả tệp.
- Không sửa tệp nào ngoài `factpack/`. Không commit git.
