# Tự kiểm — HPG_DD_investor_report_20261031 (job Taylor_20261031_102704, 31/10/2026, attempt 2)

Lần thử 1 hết lượt sau khi dựng xong .md/.pdf/hình; lần 2 kiểm tra trạng thái và hoàn tất phần còn thiếu (không viết lại từ đầu).

(i) Số khớp REPORT.md v2 — đối chiếu bằng grep từng chuỗi trên cả hai file: vùng 18.000–22.500, tâm ≈20.200; nợ ròng/EBITDA 1,54x /
1,62x / 1,35x (cận dưới); P/B 1,19 (đáy 2025) / 1,14 (đáy 2023); đỉnh 26.240 (26/02), −20%; Ke 11,83% (β Blume 0,90–0,93), thuế terminal 20%;
RI tốt/trung lập/xấu 28.147 / 19.563 / 9.612, trọng số 19.221; ROE ngầm định ≈12,4%; lõi Q3 +116–120% (lõi so lõi); CFO điều chỉnh 0,82x;
QĐ 1959/QĐ-BCT + rà soát QĐ 1902. Chuỗi đã đính chính không tái xuất hiện: "1917" 0 hit, "82,8" 0 hit, "nợ ròng thật" 0 hit.
Quy tắc đổi nhận định hai chiều (≈22.100 lên / ≈15.800 xuống, đuôi TLSH ≈590 đ/cp) lấy nguyên từ REPORT §9.

(ii) Luật 4: `grep -i -E "SpaceX|ZaloPay|\bNAV\b|Taylor|Bobby|Mike|skeptic|Wendy|Spyros|giá vốn"` trên .md = 0 hit; trên .html (bỏ base64) = 0.
(Hit "NAVY" chỉ là hằng màu trong figs_part.py, không xuất hiện ở sản phẩm.)
Luật 1: `grep -i -E "QUALIFY|AMBIGUOUS|\bNON\b|§2\.5|fear|sợ hãi|kiểm định|xung đột lợi ích|đang nắm giữ cổ phiếu|luật user"` trên .md = 0 hit.

(iii) Luật 16: thân (trước Phụ lục) 1.075 từ không tính bảng/hình (2.243 nếu tính cả chữ trong bảng); thân = trang 1–9, tổng 11 trang A4.

(iv) Luật 9/10/15: tiêu đề 1 câu, không có nháy kép thẳng; banner + hero có logo HPG (src/logo.png, nguồn hoaphat.com.vn, Phụ lục C), Be Vietnam Pro.
Bản đồ khu vực 3 khung (Bắc / Trung / Nam), toạ độ có nguồn (Phụ lục C), scripts/make_map.py chạy bằng wc_venv -I; khung 5 ảnh sản phẩm
(thép xây dựng, HRC, ống, tôn, nông nghiệp) từ hoaphat.com.vn, có nguồn.

(v) HTML: dựng bằng `send_dd_report_email.py --dry-run --html-out` (KHÔNG gửi); 15 `<img`, 0 alt vỡ.
Sửa trong lần 2: (a) .md cũ có dòng `![Banner]` + email chèn `--banner` ⇒ banner lặp 2 lần trong email → bỏ khỏi .md, build_report.py tự
chèn banner thay h1 trong PDF; (b) bản đồ ghép 1 hàng 3 khung quá dẹt (4089×1100) để một trang PDF gần trống, chữ không đọc được → ghép
2 hàng (Bắc trên cả hàng; Trung | Nam dưới, 3000×3111); (c) thêm 2 gạch "Nâng/Hạ nhận định" ở mục 10 (trước đó chỉ có bảng mốc).

(vi) Render PDF ra PNG, xem bằng mắt: trang 1 (banner, hero, Investment Summary — dấu tiếng Việt đúng, bảng không tràn), trang 3 (ngành +
doanh nghiệp + khung sản phẩm), trang 4 (bản đồ sau khi sửa — nhãn miền Bắc đọc được; nhãn Trung/Nam nhỏ nhưng rõ), trang 7 (định giá:
bảng kịch bản, heatmap độ nhạy ROE×Ke, bảng so sánh).

Giá: đóng cửa 30/10/2026 = 21.000 đ (thị trường nghỉ thứ Bảy 31/10; không cần DNSE latest_trade). Không gửi email (Mike gửi).

---

# Tự kiểm — PHIÊN BẢN 3 (job Taylor_20261031_125205, 31/10/2026, user duyệt phát hành 19:51)

File mới: `HPG_DD_investor_report_20261031_v3.{md,pdf,html}`; hình đổi ghi tên `*_v3` (`figs_v3.py`): fig_06_value_chain_v3 (thêm QĐ 1917),
fig_12_tlsh_v3 (ba lớp phơi nhiễm, dòng tiền theo GAPS2 §2–4), fig_13_risk_matrix_v3 (R5 TLSH/liên danh BT nâng xác suất Thấp→TB).
Bản v2 (`.md/.pdf/.html` 17:48, `fig_06/fig_12/fig_13` gốc) KHÔNG bị đè — kiểm mtime sau build. Lệnh: `wc_venv/bin/python -I build_report.py v3`
(figs3 + pdf3); HTML: `send_dd_report_email.py ... --dry-run --html-out` (KHÔNG gửi — Mike gửi). Nguồn số: `../GAPS2.md`, `../REPORT.md` v3.

(i) 8 sửa bắt buộc đối chiếu GAPS2: (1) QĐ 1959 = AD gốc; QĐ 1917 = chống lẩn tránh chính thức 27,83%, khổ >1.880–≤2.300 mm, hiệu lực 28/07/2026,
thay QĐ 612, ghi "theo báo chí, chưa đối chiếu văn bản gốc"; bỏ dòng "Số hiệu quyết định AD | Sai số hiệu" khỏi bảng phản biện Phụ lục E.
(2) bỏ "≈2.973 + ≈500 + 1.500"; đích chưa rõ ≈1,4–1,9 nghìn tỷ (ước lượng); 1.600 → dư hợp nhất 100 (giả thuyết, chưa xác nhận); ký quỹ +251;
mẹ 361,2 + 134,6. (3) 10.271 đ/cp = mệnh giá +2,7%; số học tự kiểm lại: 7.995.000.000.000 − 778.405.218×10.000 = 210.947.820.000 ✓;
7.995 tỷ/32.000 = 249,8 tr cp; 778,4 − 249,8 = 528,6 tr cp = 49,9% của 1.059,8 tr cp ✓; HĐQT đủ thẩm quyền (<35%); 0–~1.500 đ/cp chi phí cơ hội,
không trừ sổ. (4) KPMG 2024, ĐHĐCĐ 2025 uỷ quyền TGĐ chọn; hạ khỏi bảng WARNING thành dòng "ghi nhận"; Phụ lục D bỏ "tên hãng 2024 chưa đọc".
(5) thành viên liên danh (Đại Quang Minh đứng đầu, THACO) [báo]; thoả thuận 08/05/2026; thêm vào mục 6, R5, WARNING mục 9, mốc 15/04/2027 (H10).
(6) mẫu số HRC ~60% vs ~40% (VEOF 07/2026); XD theo vùng 2024 38% / Bắc 35 / Trung 51 / Nam 22 / XK 61. (7) 3,1% (31/12/25) / 2,8% (30/9/26)
— tự tính 7.995/257.899,2 = 3,10%, /283.449,8 = 2,82% ✓; thu nhập khác HN Q3 485,6, lõi 9T tối đa −211 tỷ (Phụ lục A).
(8) quỹ ngoại 1 dòng mục 2; β ngành 0,9–1,1 mục 7 + Phụ lục D. Đổi thêm: "≈9,5% vốn chủ" → "≈8,5%" (12.728,9 / 149.568,4 = 8,51%,
cổ phần TLSH + BĐS HP; v2 nhiều khả năng đã cộng 1.600 liên danh) — ghi trong bảng hiệu đính Phụ lục E.
Vùng 18.000–22.500 / tâm ≈20.200 và tiêu đề GIỮ (kết luận không đổi). Dưới tiêu đề: "Phiên bản 3 (hiệu đính 31/10/2026) — thay bản gửi trước."
Header PDF mọi trang thêm "· Phiên bản 3".

(ii) Luật 4 `grep -ciE "SpaceX|ZaloPay|\bNAV\b|Taylor|Bobby|Mike|skeptic|Wendy|Spyros|giá vốn"`: .md = 0; .html (bỏ base64) = 0.
Luật 1 `grep -ciE "QUALIFY|AMBIGUOUS|\bNON\b|§2\.5|fear|sợ hãi|kiểm định|xung đột lợi ích|đang nắm giữ cổ phiếu|luật user"`: .md = 0.
Phụ lục E: bảng hiệu đính ghi rõ "hiệu đính của chính nhóm nghiên cứu ..., không phải điểm của người phản biện".

(iii) "1917" trong .md v3: 4 hit — bảng ngành (chống lẩn tránh), Phụ lục C (chống lẩn tránh chính thức), Phụ lục D (văn bản gốc chưa đối chiếu),
Phụ lục E (phân biệt 1959 vs 1917) — cả 4 đúng nghĩa chống lẩn tránh; không còn câu "sai số hiệu".

(iv) Luật 16: thân (trước Phụ lục A) 1.478 từ không tính bảng/hình (v2: 1.064); 2.897 nếu tính chữ trong bảng. Thân = trang 1–9, tổng 11 trang A4.

(v) Render bằng mắt (75 dpi): trang 1 (banner, dòng Phiên bản 3 — lần build đầu `*…*` hiện nguyên dấu sao vì md_to_html không hỗ trợ in nghiêng
→ đổi sang in đậm, build lại), trang 3 (ngành: chuỗi giá trị v3 + bảng 2 dòng QĐ 1959/1917), trang 6–7 (TLSH: sơ đồ ba lớp — hình co nhẹ cho vừa
trang, chữ vẫn đọc được ở độ phân giải gốc; 7 gạch đầu dòng), trang 7 (định giá: bảng kịch bản, heatmap, so sánh + dòng β ngành).
HTML: 15 ảnh nhúng (dry-run in images=15).

Gợi ý cho người gửi: tiêu đề giữ nguyên; subject email có thể thêm "(phiên bản 3)" nếu muốn phân biệt với bản đã gửi.
