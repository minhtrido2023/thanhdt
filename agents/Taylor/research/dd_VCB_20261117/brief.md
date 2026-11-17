# Brief DD VCB (Vietcombank) — mùa BCTC Q3/2026 (từ hàng đợi New deals: VCB VÀO double-confirm, 8L rating 1)
Mọi bước theo skill `~/.claude/skills/due-diligence/SKILL.md` BẢN MỚI NHẤT (11/11) — đọc hết trước khi làm. Thư mục làm việc: agents/Taylor/research/dd_VCB_20261117/ (src/ cho BCTC gốc).
## Đầu vào
- Sector read của Bobby (đọc ngành NH quốc doanh, MÙ): /home/trido/thanhdt/WorkingClaude/mike/kb/data_registry/market-state/sector_read_ngan_hang_quoc_doanh_20261117.md — đọc §7 "DD cần kiểm gì" (20 mục) và các forecast; lưu ý Bobby cảnh báo: nhóm 3 NH, mọi dải đều chứa NH mục tiêu.
- Snapshot vĩ mô (đưa SAU khi Bobby xong — đã xong): dd_VCB_20261117/macro_snapshot_20261117.md (DISPLAY-ONLY, quy tắc 3b).
- BCTC GỐC từ website công ty (vietcombank.com.vn → Quan hệ nhà đầu tư): BCTC hợp nhất quý 3/2026 + giải trình biến động LNST + BCTC kiểm toán/soát xét gần nhất (ý kiến ngoại trừ/nhấn mạnh), CBTT bất thường (tăng vốn, phát hành cổ phiếu, nhân sự, room ngoại). BQ chỉ để đối chiếu, không làm nguồn chính. PDF scan: xem hướng dẫn pymupdf trong skill.
## Bẫy đặc thù NH (từ Bobby + skill)
- P/PCF, FCFE, V_dài/C4/D2 KHÔNG áp dụng cho ngân hàng ⇒ ghi "không áp dụng" thay vì in số. Định giá theo P/B–ROE bền vững và Ke (khung Ke nội địa của skill, r gắn lãi huy động hiệu dụng — lấy từ deposit_rate_vn, ghi số+ngày; độ nhạy ±50/100bp), vùng giá, kịch bản xấu/cơ sở/tốt có trọng số.
- BVPS điều chỉnh: số cổ phiếu mới (phát hành/cổ tức cổ phiếu), thiếu hụt trích lập, lãi dự thu thừa; cổ tức bằng cổ phiếu KHÔNG phải thu nhập. ROE bền vững (không dùng ROE của năm trích lập thấp), và báo ROE ở mức CET1 mục tiêu.
- Chất lượng tài sản: NPL, nhóm 2, bao phủ nợ xấu, trích lập/tín dụng, nợ xấu tiềm ẩn BĐS; NIM và áp lực CV lãi suất cho vay; tiền gửi Kho bạc/LDR; TT14; CAR/Basel; room tín dụng.
- Luật user áp: 5F tầng (b) moat — tra data/moat_tags.csv + kb/projects/vcb-dd-* trước; <12 tháng thì tái dùng; NPV=0 cho đầu tư mới; chi phí vốn gắn lãi huy động + chiết khấu thanh khoản; pháp lý chỉ WARNING; định giá MÙ giá thị trường.
- Thanh khoản/sizing (ADV, room ngoại) và "điều thị trường chưa tính". Mốc khoá trước + điều kiện đổi nhận định hai chiều.
## Deliverable
REPORT.md (mẫu agents/Taylor/research/dd_DDV_20261026/REPORT.md) + file nguồn giả định (cho assumptions_md5). KHÔNG ghi dd_price_zones.json, KHÔNG dựng PDF, KHÔNG gửi email — Mike làm sau skeptic. Ghi bus finding khi xong. Dùng worktree nếu sửa code (không cần sửa code).
