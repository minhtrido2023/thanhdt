# Tự kiểm — TV1_DD_investor_report_20261102 — r7 (job Taylor_20261102_112213, 02/11/2026; hiệu chuẩn peer; CHƯA gửi, CHƯA qua fundamental-skeptic)

## r7 — viết lại toàn bộ như bản độc lập (luật 18) + hiệu chuẩn P/E, lợi suất yêu cầu theo peer thuỷ điện
- Peer: `../calc/peer_study/` — SQL `q_panel_monthly.sql`, `q_fin.sql`, `q_div.sql`, `q_exch.sql` (bq CLI, stdin) → `bq_*.csv` → `/home/trido/thanhdt/wc_venv/bin/python -I peer_study.py` → `peer_study_out.txt` (md5 bb69207a…), `out_*.csv`, `peer_calib.json`.
- Định giá: `python3 -I calc/valuation.py > calc/valuation_out.txt` (md5 4fdfa088…) khối "r7" đọc `peer_calib.json`: P/E 6,80/7,42/8,01; Ke 11,1/10,4/9,5%; vùng 18.153–21.986 (18.200–22.000), tâm 20.667 (−4%); hoà vốn 540/514/480.
- Kiểm tay: P/E 8,55×0,868 = 7,42 ✓; 7,83×0,868 = 6,80 ✓; 9,22×0,868 = 8,00 ✓. LNST hoà vốn (205×0,540−71)×0,8+40 = 71,8 ✓ (fig_12). P/E ngầm giá trên LNST (b) 19.800/(81,6e9/26.691.319) = 6,5 ✓; (c) 8,1 ✓. Cổ tức cần 19.800×{0,0949; 0,1110} = 1.879–2.198 ✓. Bảng nhóm mục 7: P/E = trung vị mã-năm 2026 (peer_study_out "P/E theo SÀN"/"1d"), P/B/yield/ROE/payout = out_peer_universe.csv (tháng 10/2026) — nhãn "(2026, trung vị)".
- Hình mới: fig_14_peer_pe, fig_15_peer_yield (+CSV). Vẽ lại: fig_00_hero, fig_07_football, fig_12, fig_13, fig_08 (bỏ mã R0–R8 để qua grep `\br[0-9]\b`). Banner tạo lại theo tiêu đề mới.
- Grep luật 18 (md, HTML bỏ base64, figs/*.csv): `đính chính|thay bản|trước đây|đã sửa|vòng [0-9]|\br[0-9]\b|sai sót|bản r|REFUTED|phản biện lần|lỗi phương pháp` = **0 hit**. Grep nội bộ/fear (Taylor|Bobby|Mike|skeptic|SpaceX|ZaloPay|NAV|fear|QUALIFY|AMBIGUOUS|NON|§2.5|kiểm định|xung đột lợi ích|BANNED…) = **0 hit**.
- PDF 14 trang; HTML dry-run 17 ảnh, 4.6M; thân bài ≈1.630 từ (không tính bảng/hình/phụ lục). Xem bằng mắt trang 1, 8 (peer), 10 (định giá); sửa nhãn hero bị tràn và nhãn hoà vốn fig_12.
- Chưa kiểm được (ghi Giới hạn): KTPL của peer (giả định 7%); nhãn thuỷ/nhiệt tự gán theo tên DN; sàn 15 mã suy từ biên độ; KBSV 17/04/2026 bản gốc; nguyên nhân BSA KH 2026 −39%.
- Lưu ý dùng lại: `python3 -I` hệ thống không có numpy/pandas ⇒ peer_study + build_report chạy bằng wc_venv.

# Tự kiểm — TV1_DD_investor_report_20261102 — r6 (CHỐT; job Taylor_20261102_102919, 02/11/2026; thay bản gửi 15:25 và r4/r5; CHƯA gửi)

## r6 — sửa theo phản biện vòng 4 (`../SKEPTIC4_20261102.md`: B1, B2, N1–N5)
- **Chưa kiểm lại sau vòng 4 ngoài bước kiểm ngắn của Mike.** KHÔNG gửi email (dry-run only: images=15, 9,9 MB).
- Số: `../calc/valuation_out.txt` (`python3 -I calc/valuation.py`) khối "r5"+"r6". P/E ngang hàng: `../calc/hydro_peer_pe.sql` → `bq_hydro_peer_pe_r6.csv` (=`bq_hydro_peer_pe.csv`) → `hydro_peer_pe_stats.py` (20 mã, loại PPC/QTP/KHP/TV1): 2025 13,33 · 2026 YTD 9,81 (p25 8,90) · T10/2026 9,35 · TV1 4,01.
- Kết quả: P/E 5,9/6,15/6,4 ⇒ P/E mid 16.202; DDM27/40 13.936/14.500; vùng 13.936–16.768 (13.900–16.800), tâm 15.210 (+30%); hoà vốn PPA 634 (P/E) / 703 (tâm) / 817 (DDM40); chiết khấu ngầm so SOTP trộn 41%. Terminal DDM: P/E ngầm định phần hoạt động 1,2/2,1/2,6/4,4×; terminal P/E 6,15–6,75 ⇒ DDM 16.925–17.966, tâm 16.705–16.943.
- Hình vẽ lại (figs_part.py hằng số r6): fig_00_hero, fig_06 (nhãn dải), fig_07_football, fig_12 (đường hoà vốn 87,2 = (205×0,634−71)×0,8+40 — hyd_np 47,2 + tư vấn 40), fig_13 không đổi. Banner tạo lại.
- Quét: lộ nội bộ (md, figs/*.csv, HTML bỏ base64) = 0 hit; số cũ r5 (590, 6,75x, 15.900, 10,9x, 23 mã) chỉ còn ở độ nhạy/cột "Trước" Phụ lục E (cố ý). Xem bằng mắt PDF 14 trang: trang 1 (banner, hero, tear sheet) và 7.
- Lưu ý tự kiểm: tên ngành VPD/NED/DRL/HNA/ISH tra bằng tìm kiếm web (không đối chiếu BCTN); KBSV 17/04/2026 vẫn CHƯA kiểm.

# Tự kiểm — TV1_DD_investor_report_20261102 — BẢN ĐÍNH CHÍNH LẦN 2 / r5 (job Taylor_20261102_100630, 02/11/2026; thay bản 15:25 (r3, job Taylor_20261102_075340) đã gửi; bản r4 CHƯA từng gửi)

## r5 — sửa theo phản biện vòng 3 (`../SKEPTIC3_20261102.md`: B1–B3, N1–N11; N12 chỉ ở REPORT nội bộ)
- **CHƯA qua phản biện vòng 4** (Mike chạy sau). KHÔNG gửi email (dry-run only).
- Số: từ `../calc/valuation_out.txt` khối "r5" (`python3 -I calc/valuation.py`, md5 out 1e0d0a1d…). Quét tự động thân bài (trước Phụ lục E) vs REPORT + valuation_out + rate_lines + README 13/10: 291 chuỗi số, 3 không nguyên văn — đều có nguồn: 198,5 = tiền 30,7 + HTM 167,8; 20.000 (tham chiếu 02/11); 57,76 (Q1+Q2/26).
- Kiểm tay: LNST thuỷ điện Q205 (a) (199,9−71)×0,8 = 103,1; (b) 41,6; (c) 25,2; (d) −1,0 ⇒ +40 tư vấn = 143,1/81,6/65,2/39,0 ✓ khối r5. P/E LNST bền (b)/(c) = 528,5/81,6 = 6,5; /65,2 = 8,1 ✓. 65,2–81,6/150,2 = 43–54% ✓. Hoà vốn ≈591 đ/kWh ⇒ LNST HĐ (205×0,591−71)×0,8+40 = 80,1 ✓ (fig_12). Chiết khấu ngầm định 1−15.889/25.939 = 39% ✓.
- Hình vẽ lại: fig_00_hero (KPI + xlim 6–32k, tiêu đề rút gọn để không bị cắt), fig_07_football (thêm dòng SOTP×0,6–0,8), fig_12 (Q205, đường hoà vốn 80), fig_13 (cổ tức bền r5), fig_08 (+R8 truy thu, R5 0,50), fig_06 (nhãn dải lấy từ FAIR — trước còn chữ "17,8–20,6k" sót từ r3). Banner tiêu đề tạo lại (lệnh dưới). CSV kèm mỗi hình.
- Lộ nội bộ (md, figs/*.csv, HTML bỏ base64; mẫu thêm Taylor|skeptic|SpaceX|ZaloPay|Mike|job|state_TV1|[UL]) = 0 hit. PDF 14 trang; HTML dry-run 15 ảnh.
- Trung dung: tiêu đề nêu vế tốt (tư vấn tăng, cổ tức 7,6%) + vế rủi ro/giá + điều kiện đổi chiều (≥≈590 đ/kWh); bảng "điều làm nhận định đổi" hai chiều; nhạy hai chiều 12.600–22.700 bao quanh giá; SOTP trên giá được nêu rõ. Không fear-buy.
- Chưa kiểm được (ghi trong REPORT E4): bản gốc KBSV 17/04/2026 tr.4 (500–600 là giá tổng hay giá cố định); BCTN 2025 tr.38 (dùng trích 13/10). Đính chính: "1.351,7 tỷ 27/3/2026" thực là thông báo đấu giá lần 5 ngày 17/05/2021.


## r4 — dựng lại định giá theo giá PPA Sông Bung 5 (user phê bình phương pháp 02/11 16:42; ../REPORT.md Phụ lục E3)
- **CHƯA qua phản biện vòng 3** (Mike chạy sau). KHÔNG gửi email (dry-run only).
- Số: mọi số định giá mới từ `../calc/valuation_out.txt` khối "r4" (`python3 -I calc/valuation.py`, md5 out 9a1294b6…). Quét tự động thân bài (trước Phụ lục E) vs REPORT + valuation_out + rate_lines + `../../tv1_sb5_ppa_price_20261013/README.md`:
  169 chuỗi số, 10 không có nguyên văn — đều có nguồn: lưới P/E Phụ lục A (10.700/14.000/14.600/21.400/24.400/29.200 — nay in ở cuối valuation_out sau khi thêm khối lưới), 198,5 = tiền 30,7 + HTM 167,8, 20.000 (tham chiếu 02/11), 20.500 (vùng giá 12T), 57,76 (Q1+Q2/26).
- Kiểm tay: LNST thuỷ điện Q192,5: (a) (187,69−71)×0,8 = 93,4; (b) 35,6; (c) 20,2; (d) −4,4 ⇒ tổng có tư vấn 40: 133,4/75,6/60,2/35,6 ✓ khớp khối r4. P/E LNST bền (b)/(c): 528,5/75,6 = 7,0; /60,2 = 8,8 ✓. 60–76/150,2 = 40–51% ⇒ "khoảng 40–50%" ✓. Điện mặt trời 800/528,5 = 1,51× vốn hoá ✓.
- Fig mới: fig_12_np_by_ppa (LNST bền theo kịch bản giá PPA; đường 528,5/5,5 = 96), fig_13_dividend_gap (cần 2.435–2.650 vs thực trả 1.500, KH 1.000, bền 360–1.998). Vẽ lại: fig_00_hero, fig_07_football, fig_08_risk (+R0). CSV kèm mỗi hình.
- Nguồn mới (web 02/11): baodauthau.vn 30/04/2026 (ĐHĐCĐ 2026: KH LNST 104,2, DT 641,5, cổ tức KH 10%; điện mặt trời 46 MWp/~800 tỷ "chưa thể triển khai") và 27/06/2025 (~90 tỷ DT/năm). BCTN 2025 KHÔNG tải lại được (owa.hnx.vn lỗi chứng chỉ) — trích tr.38 lấy từ README 13/10. KBSV bản gốc không tìm lại được. BCTC 2025 kiểm toán tr.32–36 đọc ảnh: không có biểu giá PPA.
- Đã bỏ khỏi thân bài một câu chưa kiểm chứng ("tin 03/2026 rao bán 1.351,7 tỷ" — chỉ có qua tóm tắt tìm kiếm, không ngày).
- Lộ nội bộ/fear-buy (md, figs/*.csv, HTML bỏ base64) = 0 hit. HTML dry-run: 15 `<img`, 9,6 MB. PDF 13 trang (thân 1–10). Xem bằng mắt: montage 0,5x toàn bộ + 1,1x trang 1 và 8; đã sửa nhãn KPI bị cắt (hero).
- Quét số cũ r3 trong thân (17.800, 20.600, 13.500, 29.000, 103–172, 20/45/35, 25/50/25, 23.900, 44.200, "từ ngang") = 0 hit ngoài dòng "BẢN ĐÍNH CHÍNH LẦN 2" nêu kết luận cũ (cố ý).

## r3 (phản biện vòng 2: 4 BLOCKING + 10 NON-BLOCKING — đã áp hết; xem ../REPORT.md Phụ lục E2)
- Số: mọi số mới từ `../calc/valuation_out.txt` khối "r3" (python3 -I calc/valuation.py). Quét tự động thân bài (trước Phụ lục E) vs REPORT+valuation_out+rate_lines:
  8 chuỗi không có nguyên văn, đều có nguồn: 19.000–19.600 (EV 15/50/35: 19.042–19.568), 22.300–22.600 (EV 30/50/20: 22.338–22.639), 19.900 (PV 30/50/20 VCSH soát xét 19.860),
  20.000 / 20.500 / 26,69 / 57,76 như bản trước.
- Kết luận: vùng giá trị hợp lý 17.800–20.600 = min–max PV {25/50/25, 20/45/35} × T{1;1,5;2} × Ke{12,3;13,4%} × VCSH{574,7; 507,8}; 25/50/25 ⇒ 19.300–20.600 (−3,8…+2,6%);
  20/45/35 ⇒ 17.814–19.353 (+2,3…+11,1%). Giá tham chiếu 20.000: 20.000/20.600−1 = −2,9%; 20.000/17.800−1 = +12,4% ⇒ "−3% đến +12%".
- B3: đã render BCTC 2025 kiểm toán trang in 21 (`../img/fy25_p22.png`): dự phòng phải thu bên liên quan 16.751.114.343 + KH khác 73.179.659.301 = 89,93 ✓; fig_03 vẽ lại 89,9 → 90,8 → 68,4.
- B4: VnExpress 02/07/2026 mở lại 02/11 (WebFetch) — trích nguyên văn "13 công ty bị xác định có liên quan", "EVNNPT và nhà thầu đều có sai phạm trong lập, phê duyệt dự toán",
  "Các nhà thầu khi thực hiện nhiều hạng mục cũng có vi phạm."; bài không nói pháp nhân bị khởi tố; đếm tên ~12 (ghi trong REPORT §7).
- Quét số cũ (thân trước Phụ lục E): 19.200 / 17.200 / 20/50/30 / 15/45/40 / ≈2.800 / "thấp hơn ~10%" / "không có căn cứ" / doanhnghiephoinhap / "13 đơn vị" / "khởi tố pháp nhân" = 0 hit
  (63,2 chỉ còn ở dòng CỜ lệch 26,7; "một nửa" chỉ còn ở "một nửa bội số" P/E — đúng; 19200 trong fig_06_price.csv là giá đóng cửa ngày 24/08 và 12/10).
- Lộ nội bộ/fear-buy (md, figs/*.csv, HTML bỏ base64) = 0 hit. HTML dry-run: 13 `<img`, 13 alt không rỗng; 9,1 MB; KHÔNG gửi (Mike gửi).
- Xem bằng mắt: PDF 11 trang (thân 1–9, phụ lục 10–11), montage 0,5x toàn bộ + 1,1x trang 1, 3, 6, 7. Đã sửa trong r3: dấu ~ hiển thị thành "-" trong hình (đổi "khoảng");
  glyph mũi tên thiếu (fig_03); nhãn "giá 19,8k" đè thanh (fig_07); chú thích đè trục (fig_07, fig_03); ">" blockquote hiển thị thô; trang 2 trống nửa → bỏ ngắt trang trước
  "Ba điều"/"2.", thêm ngắt trước "7." để tiêu đề mục 7 không mồ côi.

## Bản trước (r2, giữ để đối chiếu)

Lệnh tái lập (chạy từ `investor_report/`): `bash scripts/make_maps.sh` → `/home/trido/thanhdt/wc_venv/bin/python -I build_report.py all`;
banner: `python3 ~/.claude/skills/dd-investor-report/scripts/make_title_banner.py --title "<dòng 1 .md bỏ '# '>" --ticker TV1 --kicker "Báo cáo due diligence · UPCOM: TV1" --sub "Nhóm nghiên cứu · 02/11/2026" --logo figs/logo.png --out figs/title_banner.png`;
HTML: `python3 -I .../send_dd_report_email.py <md> --pdf <pdf> --banner figs/title_banner.png --dry-run --html-out TV1_DD_investor_report_20261102.html` (KHÔNG gửi — Mike gửi).
Giá 12T: `scripts/tv1_px_bq.csv` (bq `tav2_bq.ticker` alias t, 27/10/2025–30/10/2026; đóng cửa 30/10 = 19.800 khớp DNSE `../calc/dnse_raw.json`).

(a) Lộ nội bộ / trung tính — grep trên .md: `SpaceX|ZaloPay|giá vốn|NAV|Taylor|Bobby|Mike|skeptic|Wendy|Spyros` = 0 hit;
    `QUALIFY|AMBIGUOUS|\bNON\b|§2\.5|fear|sợ hãi|kiểm định|xung đột lợi ích|đang nắm giữ cổ phiếu` = 0 hit. figs/*.csv = 0 hit. HTML (bỏ base64) = 0 hit.
(b) Độ dài: PDF 11 trang (thân 1–9, phụ lục 10–11). Số từ thân không tính bảng/hình = 1.214 (gồm bảng 2.433) ≤ ~1.800.
(c) Xem bằng mắt (render 1,4x): trang 1 (banner + hero + tear sheet), trang 7 (định giá: 2 bảng kịch bản/PV + bối cảnh lãi suất), trang 4 (bản đồ + ảnh) và toàn bộ 11 trang ở 0,6x:
    dấu tiếng Việt đúng, bảng không tràn. Đã sửa: tiêu đề hero bị cắt; nhãn chú thích đè cột (hình 01, 03); nhãn trục bị cắt (06, 08, 09); glyph mũi tên thiếu (03);
    ảnh hero mây che → đổi ảnh lưới điện; dấu * hiển thị thô; tiêu đề “Ba điều cần biết” mồ côi cuối trang 1 → sang trang 2.
    Còn: nhãn bản đồ ghép nhỏ khi in (đọc được khi phóng to); trang 9 (mục 10) chỉ đầy ≈1/3; trang 7 bảng kịch bản tách khỏi tiêu đề mục 7 (bảng giữ nguyên khối).
(d) Số khớp ../REPORT.md (vòng 2) + ../calc/valuation_out.txt + ../calc/rate_lines.txt: quét tự động 171 chuỗi số trong thân (trước Phụ lục E) — 4 không có nguyên văn trong nguồn,
    đều có nguồn khác: 20.000 (tham chiếu 02/11 = "20,0" trong REPORT §1), 46% và 18.000–20.500 (tính từ giá 12T: đỉnh 36.550 ngày 25/03/2026; min/max từ 15/07),
    57,76 (Q1+Q2/26 dữ liệu tổng hợp = 32,23 + 25,53, khớp H1 soát xét 57,759). "≈3/4 mức giảm trước khởi tố" = (36.550 − 24.400 đóng cửa 06/05) / (36.550 − 19.800) = 72,5%.
    Kiểm thủ công: PV 19.200–20.600, giá −4%…+3%; EV chưa CK 21.600; cơ sở 13.500–29.000 (tâm 20.100); tốt 28.500–38.700; xấu 10.800–15.100; SOTP 23.900/44.200;
    lõi Q3 16–45; CFO Q3 69,8; dự phòng −24,9 (KH 90,81→68,36); P/E 2,8 / 3,2–3,8; P/B 0,92 / 1,04; Ke 12,3–13,4%; r* 15,1% / TPCP 4,58% (+0,64).
    Ở giá tham chiếu 20.000: 20.000/20.600 − 1 = −2,9%, 20.000/19.200 − 1 = +4,2% ⇒ "−3%…+4%", kết luận không đổi.
(e) Số cũ bị đính chính (62,5; 27,5 dự phòng; "tăng 63,2→68,4"; 36–44; +7%; 3,24x; 125–155; 16.400–26.100; "thấp hơn ~10%"; 24.300/44.700) chỉ còn ở cột "Trước" Phụ lục E.
    Hai trùng hợp hợp lệ: 27,5 = QLDN 9T/25 (Phụ lục A); 16.400 = ô 125 tỷ × 3,5x trong lưới độ nhạy.
(f) HTML dry-run: 13 `<img`, 0 thiếu/vỡ alt; người nhận = địa chỉ trong secrets; 8,7 MB. Tiêu đề không có nháy kép thẳng (dùng “ ” trong thân).

Luật 15: bản đồ khu vực miền Trung (Quảng Nam cũ/Đà Nẵng) + Hà Nội, KHÔNG toàn quốc. Toạ độ: Sông Bung 5 = Global Energy Monitor wiki (15,8077; 107,7472; xã Mà Cooih–Thạnh Mỹ theo thông báo đấu giá — báo Đấu thầu);
  trụ sở 66 Lương Ngọc Quyến, phường Thanh Liệt (địa chỉ: footer pecc1.com.vn, WebFetch 02/11) → OSM Nominatim (20,9841; 105,7950); Đà Nẵng (MTV3, cấp thành phố) → OSM (16,0685; 108,2240).
  Ảnh: 3 banner trang chủ pecc1.com.vn (`../src/web/`, cắt phần không có khung chữ), ghi "minh hoạ lĩnh vực, không xác định công trình". BCTC đều là bản scan, không có ảnh sản phẩm trích được; chưa có BCTN 2025.
  Logo: pecc1.com.vn/images/logo.png → `../src/logo.png`, `figs/logo.png`.
Chưa làm (ngoài phạm vi dispatch): ghi `kb/dd_price_zones.json` — để Mike làm khi gửi email.
