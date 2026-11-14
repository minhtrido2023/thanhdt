# PAT — DD làm lại KHÁCH QUAN, mù giá thật (brief gốc, user 14/11/2026 23:04 ICT)

## Chỉ đạo user (nguyên văn)
"Làm lại cho thật sự khách quan, không được bi quan khi không có bằng chứng. Phải chạy mù với giá thị trường. Đánh giá khách quan khả năng lợi nhuận của doanh nghiệp thực sự dựa trên phán đoán tình hình thực tế, không phải suy đoán do lười suy nghĩ."

## Vì sao 3 lượt trước chưa đạt (để KHÔNG lặp)
1. Lượt 1–2 (dd_PAT_20261114/REPORT.md, tâm 66.600): brief của Mike có giá + cột PE ⇒ KHÔNG mù; skeptic chỉ kéo MỘT CHIỀU (xuống) và sửa EBT 245→202,6 bằng run-rate Q3 — một quý yếu.
2. Lượt mù (blind_val_20261114, 78.300 sau CK): EBIT cơ sở 245 = TRUNG BÌNH ba con số khác chế độ (2024/TTM/Q3) — lười; skeptic sửa lại bằng nội suy 3 điểm P4–EBIT (Q1–Q3/26) — cũng suy đoán mỏng (N=3), và skeptic không mù giá nên "khuyến nghị 69–70k" sát giá 71.000.
3. Chưa ai trả lời câu hỏi cốt lõi bằng BẰNG CHỨNG VẬN HÀNH: sản lượng thật, đơn giá bán thật (nội địa/DLC vs xuất khẩu), vì sao biên Q3 sập, ban lãnh đạo tự dự báo gì, quặng Q4/2027 ra sao. Các giả thuyết "giá chuyển nhượng bất lợi", "thiếu quặng" được dùng như sự thật mà chưa có số.
4. Taylor có working memory chứa kết quả cũ ⇒ KHÔNG dùng Taylor/headless có memory cho lượt này; dùng agent stateless (Agent tool).

## LUẬT LƯỢT NÀY
- Mù giá thật: không tác nhân nào (kể cả skeptic) được thấy giá, PE, PB, vốn hoá, mục tiêu giá của PAT, REPORT cũ, sổ mức giá, tâm cũ. Mike chỉ so giá SAU khi khoá kết quả cuối.
- Không bi quan thiếu bằng chứng: MỌI khoản giảm trừ/rủi ro đưa vào base phải có "bằng chứng #n" dẫn tới fact pack (số, văn bản, ngày). Không có ⇒ mức trung tính hoặc chuyển thành độ nhạy/WARNING (luật 27/09 pháp lý; luật 03/11 dự án mới NPV=0; luật 08/11 moat không trừ). Đối xứng: mọi khoản cộng cũng cần bằng chứng.
- Cấm "trung bình các số cho tiện" và "nội suy ít điểm": cơ sở lợi nhuận phải xây bằng PHÁN ĐOÁN VẬN HÀNH có lập luận: sản lượng × đơn giá × chi phí đơn vị (build-up), rồi kiểm chéo với (a) kế hoạch SXKD của HĐQT, (b) run-rate nhiều quý (≥4–8) và (c) lịch sử 2022–2026; nếu ba cách lệch nhau phải giải thích vì sao chọn, không lấy trung bình.
- Skeptic HAI CHIỀU và MÙ GIÁ: (i) tố cáo lạc quan, (ii) tố cáo bi quan (gỡ mọi giảm trừ thiếu bằng chứng).

## QUY TRÌNH
A. FACT PACK (agent stateless, ≥3 agent song song theo nhóm câu hỏi; ĐƯỢC dùng web nhưng KHÔNG thu thập/ghi giá, PE, vốn hoá, mục tiêu giá, báo cáo phân tích CTCK có định giá; gặp thì bỏ + ghi dòng "đã bỏ"). Mỗi fact có nguồn (URL/tệp+trang, ngày). Đầu ra: `agents/Taylor/research/dd_PAT_objective_20261114/factpack/*.md`. Mike grep factpack tìm "đ/cp|giá cổ phiếu|P/E|vốn hoá|mục tiêu" trước khi đưa sang B.
  Câu hỏi bắt buộc:
  1. Kế hoạch SXKD 2026 (NQ ĐHCĐ 2026): sản lượng P4, doanh thu, LNST kế hoạch (báo chí nói 280 tỷ), cổ tức, đầu tư; tờ trình giải thích giả định (giá bán, quặng, thuế).
  2. Giải trình biến động LNST Q3/2026 (CBTT công ty): lý do chính thức LNST giảm ~46%; tương tự giải trình Q1/Q2 (Q1: "giá vốn +14% do NVL tăng").
  3. Sản lượng & đơn giá thật: BCTN 2025, thuyết minh doanh thu theo sản phẩm/thị trường; tính đơn giá P4 bình quân nội địa(DLC) vs xuất khẩu theo quý nếu có khối lượng; cơ cấu giá vốn (NVL, điện, nhân công, KH) và đơn giá NVL mua từ DLC (TM bên liên quan).
  4. Cung quặng apatit Lào Cai Q4/2026–2027: dây chuyền tuyển, quặng loại III, 3,53 triệu tấn tồn, quyết định chính sách/thủ tục (nguồn nhà nước/báo địa phương); ảnh hưởng tới DLC ⇒ PAT; mốc thời gian.
  5. Cơ chế giá giao dịch bên liên quan DLC–PAT: nghị quyết HĐQT/ĐHCĐ phê duyệt hợp đồng, nguyên tắc xác định giá (giá thị trường? cost-plus?), kiểm toán có nêu gì về giao dịch này.
  6. Thuế xuất khẩu P4: văn bản gốc NĐ 199/2025 phụ lục, có sửa đổi sau 07/2025 không; hiệu lực 15% từ 01/01/2027.
  7. Cổ tức 2025–2026: nghị quyết, tạm ứng, ngày chốt quyền; chính sách chi trả.
  8. Tình trạng vụ án hiện tại + tác động đã biết lên hoạt động PAT (WARNING-only, nêu nguồn); điều khoản ngoại trừ kiểm toán chi tiết.
  9. Lịch sử 2022–Q3/2026 từ BQ `ticker_financial` (CHỈ cột cơ bản: Revenue/NP/GPM/CFO/vốn chủ/số cp…; TUYỆT ĐỐI không cột giá/PE/PB/MarketCap/EV) + `commodity_prices` sunsirs P4/than cốc/(điện nếu có): dựng chuỗi ≥16 quý; thử quan hệ biên gộp ~ P4, than cốc, tỷ trọng bán DLC với kiểm định thống kê và nói thẳng nếu không xác định được.
  10. Đối thủ P4 trong nước (biên/giá bán hiện thực nếu có số công khai) và giá điện kế hoạch 2027.
B. VALUER MÙ (agent stateless Opus): nhận factpack + BCTC ảnh (blind_val_20261114/inputs/src được dùng lại) + sector_read_phot_pho_20261114.md + macro_snapshot. Làm theo khung skill `due-diligence` (r=13,5% @ lãi huy động 12T hiệu dụng, g có cơ sở, FCFE trừ trích quỹ KTPL, thuế ưu đãi TM27, thuế XK, hai nền V_ngắn/V_dài, moat 5F, độ nhạy, thanh khoản TRƯỚC chiết khấu + bảng 5/10/20%). Khoá assumptions + md5 + giờ TRƯỚC khi chạy mô hình. Bắt buộc có mục "Phán đoán khả năng sinh lời thực" (build-up + 3 kiểm chéo + vì sao chọn).
C. SKEPTIC HAI CHIỀU MÙ GIÁ (2 agent riêng, fundamental-skeptic: một tố cáo lạc quan, một tố cáo bi quan — dùng prompt riêng, đưa đường dẫn bản khoá, KHÔNG đưa giá/REPORT cũ). Áp đính chính MỘT vòng (bằng agent mới stateless nếu cần), khoá lần cuối.
D. SAU KHI KHOÁ: Mike mới so với giá đóng cửa (BQ `ticker`, kiểm đúng ngày — lần trước ANY_VALUE lấy nhầm ngày: dùng ORDER BY time DESC LIMIT 1). Dựng báo cáo NĐT PDF/HTML bằng skill `dd-investor-report` (dry-run, KHÔNG gửi email; email chỉ khi user báo). Sổ mức giá `kb/dd_price_zones.json` rev3 (supersedes PAT@2026-11-14#2, correction_reason: làm lại mù giá + khách quan theo chỉ đạo 14/11 23:04). Commit.
E. Báo user: kết luận 1 dòng, vùng giá, 3 kịch bản + xác suất CÓ CƠ SỞ, danh sách khoản giảm trừ đã GỠ vì thiếu bằng chứng, độ chênh so với 3 lượt trước và vì sao, mốc kiểm chứng.

## Tái sử dụng được (không mù không phải là vấn đề với BCTC ảnh)
- BCTC ảnh trang: agents/Taylor/research/blind_val_20261114/inputs/src/{png_q326,png_bn26,png_kt25} + PDF; số trích tay inputs/facts_extracted.md (kiểm vài số trọng yếu).
- Đọc ngành Bobby: kb/data_registry/market-state/sector_read_phot_pho_20261114.md (đọc ngành đã mù; dự báo khoá trước F1–F7).

## CẤM đưa cho tác nhân A–C
agents/Taylor/research/dd_PAT_20261114/REPORT.md và mọi tệp trong thư mục đó, investor_report/, kb/dd_price_zones.json, kb/projects/pat-dd-20261114.md, blind_val_20261114/REPORT_BLIND.md & assumptions_blind.md (chứa số/tâm cũ), kb/memory/*, bus/.
