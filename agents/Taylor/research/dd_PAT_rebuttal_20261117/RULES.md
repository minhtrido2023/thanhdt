# Quy tắc chung — PAT phản biện 17/11/2026 (CTCP Phốt pho Apatit Việt Nam, mã PAT; "DGL" của user = DLC/Công ty mẹ hệ sinh thái DGC)
ROOT = /home/trido/thanhdt/WorkingClaude/mike. Thư mục làm việc: ROOT/agents/Taylor/research/dd_PAT_rebuttal_20261117/. KHÔNG commit git, KHÔNG sửa tệp ngoài thư mục này.

## Nhiệm vụ chung: KIỂM DỮ KIỆN, không định giá
User (nhà đầu tư) đưa phản biện vào một mô hình định giá. Bạn KIỂM từng khẳng định có đúng không, bằng bằng chứng. Phán quyết mỗi khẳng định ∈ {ĐÚNG, MỘT PHẦN, SAI, KHÔNG KIỂM ĐƯỢC}. BẮT BUỘC ghi ĐỒNG THỜI "bằng chứng ủng hộ" và "bằng chứng bác bỏ/mâu thuẫn" cho mỗi khẳng định (kể cả khi một bên rỗng: ghi "không tìm được, đã thử …"). KHÔNG thiên vị theo user, KHÔNG thiên vị theo mô hình cũ.

## MÙ GIÁ — tuyệt đối
KHÔNG thu thập/ghi/nhắc: giá cổ phiếu, P/E, P/B, vốn hoá, EV, mục tiêu giá, khuyến nghị, báo cáo CTCK có định giá, tin "cổ phiếu tăng/giảm". Gặp thì BỎ, ghi 1 dòng "ĐÃ BỎ: <loại, nguồn>" cuối tệp (không chép số). Cổ tức (đồng/cp, %) là số công bố của doanh nghiệp thì được lấy; yield tính trên giá thì CẤM.
Cấm đọc: kb/dd_price_zones.json, kb/projects/pat-dd-*, kb/memory/*, bus/*, agents/Taylor/research/dd_PAT_objective_20261114/{valuation,skeptic,investor_report}, dd_PAT_20261114/, blind_val_20261114/{REPORT_BLIND.md,assumptions_blind.md}. CẤM grep/rg lan rộng trong repo tìm "PAT".
Được đọc (đầu vào sạch): agents/Taylor/research/dd_PAT_objective_20261114/factpack/ (F1..F4 + data + raw — đây là fact đã thu 14/11, có thể SAI hoặc thiếu: đối chiếu lại nguồn khi dùng) và agents/Taylor/research/blind_val_20261114/inputs/ (ảnh BCTC trang src/png_*, facts_extracted.md [trích tay, có thể sai], sector_read, macro_snapshot).

## KỶ LUẬT BẰNG CHỨNG
- Mỗi fact = 1 bullet: nội dung (số + đơn vị + kỳ), NGUỒN (URL đầy đủ hoặc tệp+trang), NGÀY công bố/truy cập, phân loại [CÔNG BỐ DN]/[CƠ QUAN NHÀ NƯỚC]/[BÁO CHÍ — tên báo]/[TỰ TÍNH — công thức]. Không nguồn = không phải fact. Số báo chí phải truy về nguồn gốc nếu được; mâu thuẫn giữa nguồn → ghi CẢ HAI.
- Không tìm được = "KHÔNG TÌM ĐƯỢC (đã thử: …)". CẤM suy đoán, CẤM điền bằng "thông thường/có lẽ". Phần nhận định phải tách riêng, ghi rõ là nhận định + mức tin cậy.
- Web: ưu tiên nguồn gốc (site công ty/IR, CBTT HOSE/HNX/UBCK, công báo, cơ quan nhà nước, hải quan, Bộ Công Thương/Tài chính). Tải được PDF thì lưu vào thư mục con raw/ và dẫn tên tệp. Ngày hôm nay 17/11/2026.
- Cuối tệp: mục "ĐÃ BỎ", "KHÔNG TÌM ĐƯỢC", "ĐIỂM MÂU THUẪN". Trả lời cuối ≤12 dòng (phán quyết từng khẳng định + khoảng trống), không chép lại cả tệp.

## 4 khẳng định của user cần kiểm (nguyên văn; mỗi agent phụ trách phần được giao)
1. "2026 là năm biến động nhất của hệ sinh thái DGC. Bắt người giữa tháng 12/2025. Giữa tháng 03/2026 thì khởi tố. Ngưng khai thác mỏ ngay từ đầu năm 2026. Nếu kết quả tệ nhất, tôi đánh giá sẽ rơi vào năm nay, cụ thể quý 2, quý 3, sau đó kết quả kinh doanh sẽ tốt dần lên."
2. "Giá điện vừa giảm 2%, dù không bền. PAT sản xuất P4, bán lại chủ yếu cho mẹ DGL. Hệ sinh thái DGC xuất khẩu P4 là chính, chiếm vị thế thứ ba thế giới nên khả năng có power thương lượng giá cũng tốt hơn. Chi phí tăng lên có thể chuyển cho khách hàng, trừ khi có rủi ro thay thế P4."
3. "Việc nhập quặng và mua quặng ngoài đã thông suốt nên hoạt động sẽ ổn định. Chưa có cơ sở để nói lợi nhuận lõi năm sau sẽ thấp hơn 2026."
4. "Thuế xuất khẩu tăng lên 15% nhưng xuất qua Hàn Quốc, Đài Loan, Nhật lại không bị áp thuế này."
