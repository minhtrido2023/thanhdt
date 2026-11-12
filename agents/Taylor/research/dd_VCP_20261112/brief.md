# DD VCP (CTCP Xây dựng và Năng lượng VCP, UPCoM) — as-of 2026-11-12, giá đóng 11/11 = 31.700đ (chỉ dùng để so SAU khi định giá xong; định giá MÙ giá thị trường)

Làm theo skill `~/.claude/skills/due-diligence/SKILL.md` (đọc kỹ bước 3b/3c, khung nội dung DD, luật r gắn lãi huy động + thanh khoản, NPV=0 cho dự án mới, HAI NỀN V_ngắn/V_dài + C4 + D2 display-only, chống làm lại). Template: `agents/Taylor/research/dd_DDV_20261026/REPORT.md`. Ghi REPORT vào `agents/Taylor/research/dd_VCP_20261112/REPORT.md`.

## Nguồn (website công ty vcpholdings.com.vn) — thư mục `src/`
- bctc_hn_q3_2026.pdf (HN Q3/26, 16 trang), bctc_rieng_q3_2026.pdf, giaitrinh_hn_q3_2026.pdf (CV 110/2026 29/10), bctc_hn_h1_2026_reviewed.pdf (soát xét), bctc_hn_2025_audited.pdf (kiểm toán 2025), giaitrinh_hn_2025.pdf.
- Cần thêm: BCTC HN Q3/2025 (cùng kỳ), thuyết minh Q3/26 trang 9–16. Trang list: https://vcpholdings.com.vn/bao-cao-tai-chinh.htm (link PDF dạng /Pic/files/...). Trang chủ có mục "Quyết định xử phạt vi phạm hành chính về thuế của Cục Thuế TP Hà Nội" và "Thông báo ngày đăng ký cuối cùng quyền nhận cổ tức 2025 bằng tiền" — ĐỌC cả hai.
- ⚠️ PDF LÀ SCAN (0 ký tự text). Dùng `pymupdf` ở /tmp/pdflib (`sys.path.insert(0,'/tmp/pdflib'); import pymupdf`; chạy `python3 -I`), render trang cần ra PNG rồi Read. Mike đã render sẵn HN Q3/26 ra `img/hn_q3_pNN.png` (zoom 1.5).

## Số Mike đã đọc (Q3/26 HN) — Taylor KIỂM LẠI, đừng tin
- DT Q3 825,6 tỷ (+31,3% vs 629,0); GVHB 477,3; LN gộp 348,3 (biên 42,2%, vs 34,7% cùng kỳ); DT tài chính 56,8 (tăng nhờ lãi cho vay/tiền); CP tài chính 85,0 (lãi vay 82,8, +49,8%); QLDN 29,8 (x2); LNTT 288,1; thuế 24,1 (hiệu dụng 8,4% — kiểm: ưu đãi thuế hay điều chỉnh?); LNST 263,9 (+100%), cổ đông công ty mẹ 245,4 (vs 125,4).
- Giải trình CV110 nói DT tăng "do doanh thu khác (Doanh thu kinh doanh phế liệu) tăng" — nhưng công ty là thủy điện (Cửa Đạt 97MW + các thủy điện con: Bái Thượng, Nậm La, Xuân Minh, Cơ điện VCP, Thiết bị Phụ tùng Sài Gòn) ⇒ PHẢI tách doanh thu/GVHB/LN gộp theo mảng (điện vs phế liệu vs khác) từ thuyết minh VI.10/VI.11, và kiểm giải trình có khớp thuyết minh không. 9T: DT 2.264,5 (+41,1%), LNST 612,6, mẹ 563,3 (vs 303,9; +85%).
- Biến động BS (30/09/26 vs 31/12/25): tiền+tương đương 487,9 (vs 850,4); HTM ngắn 724,4 + dài 246,7; hàng tồn kho 763,5 (vs 341,7) trong đó "hàng hoá" 631,7 (vs 237,8) ⇒ phế liệu tồn? hay gì?; tài sản ngắn hạn khác 768,3 (vs 26,4; trong đó mục 155 = 696,5 tỷ — GIẢI THÍCH LÀ GÌ); phải thu dài hạn khác 538,0; XDCB dở dang 540,1 (vs 209,9); đầu tư vào liên kết 70,5 (mới); lợi thế thương mại 372,0 (vs 156,6 — thương vụ M&A mới? giá mua, đối tượng); tổng TS 8.111 (vs 6.315). Nợ phải trả 4.841,5 (vay ngắn 679,4 + dài 3.602,6 = 4.282, vs 3.487 đầu năm). VCSH 3.269,8, trong đó LI không kiểm soát 619,7 (vs 308,0), mẹ ≈ 2.650. 83,79 triệu cp (vốn 837,9 tỷ) ⇒ BVPS mẹ ~31,6k.
- LCTT 9T: CFO +1.004,4 (nhưng thu hồi phải thu +373,3 — một lần? kiểm), capex 351,8, đầu tư góp vốn vào đơn vị khác −1.545,7 tỷ (!), vay mới 1.453,2, trả nợ gốc 906,0, cổ tức trả 48,6. Tức 9T đã chi 1,55 nghìn tỷ mua/góp vốn — xác định đối tượng, tỷ lệ, định giá, đã hợp nhất chưa (goodwill + LICKS tăng) và nó nuôi LN 9T ra sao (DT/LN từ công ty mới mua tính từ tháng nào).
- Tăng trưởng LN không phải do thuỷ văn (Bobby: 2026 sản lượng thuỷ điện toàn quốc ~−16%): ĐIỀU TRA nguồn thật của biên gộp 42% & DT +41%.

## Việc ĐẶC BIỆT cần kiểm
1. Tách LN theo mảng + chất lượng LN (phế liệu: hợp đồng, khách, biên, có bền không; có giao dịch với bên liên quan?). DT tài chính tính trên số dư nào (cho vay 318,5 tỷ giải ngân/thu 328,6?).
2. Pháp lý: "Quyết định xử phạt hành chính về thuế" — số tiền, hành vi, năm; kiểm toán 2025 có ý kiến ngoại trừ/nhấn mạnh? Có yếu tố pháp lý ⇒ vẫn phân tích bình thường, chỉ WARNING; nêu rủi ro "scandal di cư".
3. Net cash THẬT: tiền + HTM − vay − phần cam kết; đòn bẩy (nợ vay/ EBITDA, ICR: lãi vay 9T 227,7 so LNTT+lãi), lịch đáo hạn nợ, tài sản đảm bảo, thế chấp quyền thu EVN?; cổ tức 2025 bằng tiền (tỷ lệ).
4. Thủy điện: sản lượng/giá bán/giờ vận hành 9T26 vs 9T25 theo từng nhà máy (nếu có), PPA/thị trường điện, thời hạn giấy phép/đất, phí môi trường rừng, tập trung khách (EVN), phải thu EVN. Đối chiếu danh sách "DD cần kiểm" 13 mục của Bobby.
5. Thanh khoản/room ngoại/sizing: UPCoM, ADV (BQ `tav2_bq.ticker` mã VCP; qua `universe_pit` nếu cần), free float, cổ đông lớn (ai nắm bao nhiêu).
6. Cổ phiếu: số cp lưu hành và pha loãng (kiểm có phát hành/ESOP/chuyển đổi 2026 không — vốn 837,9 tỷ không đổi đầu năm→cuối quý).
7. BQ `ticker_financial` VCP có Q3/2026 (Revenue_P0 825,6, NP_P0 245,4 = mẹ) — chỉ để đối chiếu; ⚠️ GPM/NPM/EBITM/EBITDA_P0 là TTM chứ không phải quý.

## Ngành & vĩ mô
- Bobby sector read MÙ: `kb/data_registry/market-state/sector_read_thuy_dien_20261112.md` (đọc kỹ: phân loại 12 tháng CYCLICAL/ADMIN_GATED, 12 forecast F1–F12, 13 mục "DD cần kiểm", quy định TT 29/2026 nhà máy >30MW vào thị trường trực tiếp, tái đàm phán PPA hết hạn).
- Snapshot vĩ mô (display-only): `agents/Taylor/research/dd_VCP_20261112/macro_snapshot_20261112.md` (file này Mike ghi trước khi dispatch Bobby nhưng Bobby báo không thấy; nếu không có, chạy lại `python3 mike/bin/macro_snapshot_asof.py --asof 2026-11-12`).
- Lưu ý: Bobby tự báo đã vô tình thấy kết quả Q3 của vài doanh nghiệp thủy điện khác khi tìm kiếm; đã ghi ở mục 0 của file; không ảnh hưởng.

## 5F tầng (b) + tham số moat (bước 3c)
- Tra `data/moat_tags.csv` mã VCP + REPORT/`kb/projects/vcp-dd-*.md` trước (nếu có <12 tháng thì tái dùng). Hào thủy điện: tài nguyên không tái tạo được/giấy phép/đất, giá PPA, NHƯNG có đồng hồ cắt hào (hết PPA/giấy phép, tái đàm phán giá, thuế phí nước). Phế liệu = thương mại, hào ≈ NONE. NARROW/NONE ⇒ không thưởng, không trừ (luật 08/11).

## Bắt buộc trong REPORT
- Verdict cuối: vùng giá [min, max] + tâm, nhãn, điều kiện đổi theo CẢ HAI chiều; r (13,5% + β×Δ lãi huy động 12T hiệu dụng từ `deposit_rate_vn`, độ nhạy ±50/100bp), giá trị TRƯỚC/SAU chiết khấu thanh khoản (ADV, số phiên thoát lệnh 10–20%); hai nền V_ngắn/V_dài + D + cờ capex + C4 + D2 (display-only); dự án đầu tư mới ghi NPV=0 trừ khi có cơ sở độc lập; mọi khoản giảm trừ có "cơ sở dữ liệu".
- Giả định cốt lõi khoá trong REPORT (nguồn BCTC, cơ sở TTM/quý, tham số moat, r); khi ghi `kb/dd_price_zones.json` khai `assumptions_md5` — NHƯNG chỉ ghi sổ SAU skeptic, Mike sẽ ghi, đừng ghi sổ.
- KHÔNG đặt lệnh, KHÔNG wire, KHÔNG gửi email.
- Heartbeat/bus finding khi xong (`append_event.sh Taylor finding "dd-vcp-20261112"` kèm `measured_by`).
