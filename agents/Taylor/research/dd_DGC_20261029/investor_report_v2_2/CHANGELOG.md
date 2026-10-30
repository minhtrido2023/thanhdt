# CHANGELOG — DGC DD bản 2.1 → 2.2 (30/10/2026)

Bản gốc: `../investor_report_v2/` (bản 2.1, đã gửi email). Bản này: `DGC_DD_investor_report_20261029_v2_2.{md,html,pdf}` (24 trang A4), dựng bằng `build_report.py`. Không gửi email.

| # | Cái gì | Vì sao | Nguồn |
|---|---|---|---|
| 1 | Chi phí vốn chủ: bỏ điểm Ke 14,9%, dùng KHOẢNG nội địa 12,5–13,5% (mốc đọc 13,0%), dải rộng 10,5–14,0%; 15,8% chỉ ghi là "góc nhìn nước ngoài" (USD, Damodaran) | Chuẩn mới user chốt 30/10 (skill due-diligence) | `../../erp_domestic_v2_20261030/REPORT.md`; tính lại ở `../../dgc_ke_domestic_20261030/` |
| 2 | Mọi số định giá tính lại: A7 33.118–33.951, B7 38.305–39.414 (13,0%: 33.514–38.832); kịch bản, ô thấp nhất lưới (26.739–27.293), biên ±2pp, khai trường, Nghi Sơn (ròng TB −254 ở 13%), cầu nối P/E↔DCF, dự phòng lặp (−6.511 ở 13%) | Hệ quả của #1; Ke vào DCF lõi, P/B hợp lý, chiết khấu giá trị Nghi Sơn | `out_ke_sens.csv`, `out_grid_ke.csv`, `out_margin_ke.csv`, `r10_at_ke13.0/`, `rerun/ke_13.0/` |
| 3 | Tiêu đề + tóm tắt: "sát cận dưới" → "ngang cận dưới … kể cả ở chi phí vốn nội địa"; giá thấp hơn A7 0,7–3,1% | A7 dịch lên 0,9–1,8 nghìn (+936…+1.769), B7 dịch lên 1,2–2,4 nghìn (+1.245…+2.354); nhận định không đổi; tiêu đề phải tóm ý chính (luật headline) | Như #2 |
| 4 | Mục 8b mới: bảng Ke 10,5→15,8, hình 15 (độ nhạy Ke); tỉ trọng terminal 59% giá trị hoạt động DCF ở 13% (61%/58% hai đầu), ~34% DCF/cp; g 3% ≤ GDP danh nghĩa; RONIC 12% < Ke, biến thể RONIC = Ke: A7 +74…+185 | Dispatch mục 2 yêu cầu nêu tỉ trọng terminal, g≤GDP, RONIC≥Ke | `out_ke_sens.csv` cột `tv_share_*`, biến thể RONIC |
| 5 | Khởi tố bổ sung 23/07: ba người + chức danh nêu đủ (Lưu Bách Đạt TV HĐQT/TGĐ; Phùng Trọng Tú PTGĐ; Nguyễn Quốc Trung TV HĐQT); điểm chưa thống nhất: chỉ Dân Trí ghi ngày QĐ 22/07, VnExpress có thể đọc là 2 người cấm đi khỏi nơi cư trú; sửa câu "số người chưa thống nhất" của 2.1 | Skeptic vòng 6 nêu còn mở | 5 bài gốc 23/07: Dân Trí, VnExpress, Tuổi Trẻ, Người Đưa Tin, Thuế & Hải quan (mở 30/10) |
| 6 | Ngày khởi tố 25/12/2025 và 14/03/2026: ghi rõ chỉ Đại biểu Nhân dân + Mekong Asean (17/03) nêu, không tách ngày nào gắn quyết định nào; Nhân Dân, Tuổi Trẻ không nêu; thêm Chủ tịch HĐQT trong 14 bị can | Đối chiếu nguồn gốc theo dispatch | daibieunhandan.vn, mekongasean.vn, Nhân Dân 17/03 |
| 7 | Dòng thời gian HOSE: QĐ 448 (20/05, hạn chế từ 26/05), QĐ 544 (23/06, cảnh báo), gỡ một lý do cảnh báo hiệu lực 24/08 (QĐ 567), 03/09 giữ cảnh báo do soát xét bán niên ngoại trừ; sau 06/10 không thấy thông báo gỡ, DNSE 30/10 mã trạng thái `RES` | Fleet records 24/08, 03/09 xác nhận được bằng báo gốc | Người Quan Sát 21/08, CafeF 04/09, Vietstock (đoạn trích), DNSE secdef 30/10 |
| 8 | Báo cáo thường niên 2025 (07/04/2026, scan) đọc trực tiếp: số 2025 tự lập (DT 11.262 tỷ, LNST 3.188,97 tỷ), không kiểm toán được vì hồ sơ bị niêm phong; Nghi Sơn dự kiến chạy thử đầu Q3/2026 → NQ 34 dời Q4/2026 (tiến độ đã lùi) | Dispatch mục 1 | ducgiangchem.vn, BCTN tr. 13, 15, 27 |
| 9 | Đóng cửa 30/10: 33.300 đ (DNSE); định giá vẫn neo đóng cửa 28/10 | Cập nhật trạng thái | DNSE |
| 10 | Phụ lục E thêm mục 11 (bản 2.2); Phụ lục nguồn thêm các bài gốc trên; giới hạn mới ở mục 10 | Minh bạch quy trình | — |

Không đổi: mô hình r12 (chỉ thay rf = Ke − 7,5%), trọng số kịch bản 0,2/0,5/0,3, lưới dự phòng, Phụ lục F (chỉ miễn trừ).
Giới hạn: chưa đọc trang thông báo gốc HOSE; chưa có thông cáo gốc Bộ Công an tách 2 ngày khởi tố; các sửa 2.2 chưa được rà lại.

## rev2 sau fundamental-skeptic 30/10 (verdict REFUTED mức nhẹ; số định giá tái lập đúng, 7 lỗi vòng 6 sửa thật)
Sửa tại chỗ thành 2.2 rev2 (md/html/pdf 25 trang, `build_report.py`, `figs/title_banner.png` dựng lại bằng `make_title_banner.py` của skill). Không gửi email.

| # | Sửa | Số/nguồn đo lại |
|---|---|---|
| 1 | CHẶN: chú thích hình hero bỏ câu "sau 6 vòng phản biện, Ke nội địa" (Ke nội địa chưa được rà); ghi đúng: số định giá đã tái lập (vòng 7), sửa 2.2 chưa phản biện đầy đủ | Phụ lục E mục 12 |
| 2 | CHẶN: chú thích + tiêu đề football-field khớp trạng thái (7 vòng, sửa sau vòng 7 chưa rà lại); tiêu đề rút gọn, không còn bị cắt | `figs/fig_08_football_field.png` |
| 3 | CHẶN: §8 "Cách đọc" và §1 "Trả lời" định lượng: biên gộp thấp hơn nền thấp từ ~0,7pp (Ke 12,5%) / ~0,15pp (13,5%), 1pp đủ cả hai đầu; dự phòng lặp = vĩnh viễn; dự phòng hữu hạn 4 quý KHÔNG đủ ở Ke 12,5% (33.194/33.389; hoặc 32.977/33.172 nếu giữ ~100 tỷ ngầm Q4) | `r10_at_ke12.5/13.5/out_r10_finite_N.csv`, `out_margin_ke.csv` |
| 4 | Khoảng cách giá–A7 tại 33.300: −1,9% (Ke 12,5%) / −0,6% (13,0%) / +0,6% (13,5%); thêm vào tóm tắt, bảng dữ liệu chính, §8, Phụ lục D | 33.300/33.951; /33.514; /33.118 |
| 5 | Phụ lục E 11a + CHANGELOG #3: A7 +936…+1.769 và B7 +1.245…+2.354 | `out_ke_sens.csv` vs bản 2.1 (32.182/37.060) |
| 6 | Tiêu đề: "dự kiến vận hành từ Q1/2027" (tiến độ lùi 2 lần, chưa có chạy thử tới 30/10); "kể cả ở chi phí vốn nội địa" → "dù đã dùng chi phí vốn nội địa"; hộp Nghi Sơn ở hero, bảng dữ liệu, §6 cũng ghi "dự kiến" | — |
| 7 | §8b: câu Ke >15% có nguồn: phép thử justify của nhóm, 78% mã phi ngân hàng PE cao hơn PE hàm ý ở Ke 15% (70% ở 13%), ghi rõ là phép thử của nhóm | `erp_domestic_20261030/out_justify_grid.csv` (g 5,5%, n 294) |
| 8 | §8b: "terminal ≈ 11%" ghi rõ chỉ tính terminal của DCF, chân P/B cũng là perpetuity, chưa tách | 0,34/3 = 0,113 |
| 9 | §6c: "khác nhau khoảng 3.250 (−228 → 3.019), bước lớn nhất +2.194" | 3.019 − (−228) = 3.247 |
| 10 | 263 = số thô (100 tỷ ÷ 379,78 tr cp), mô hình ở Ke 13% là 254; "754–971" = 754 so A7 / 971 so nền không trích thêm (777 sau lá chắn) | 33.514−32.760; 33.731−32.760; 33.731−32.954 |
| 11 | Pháp lý: "công bố 03/2026"; lý do cảnh báo ĐHĐCĐ có từ 09/07, gỡ hiệu lực 24/08; "hạn chế giao dịch" = chỉ giao dịch phiên chiều; phạt Đ.235 thêm quy tắc chuyển tiếp (hành vi trước 01/07/2025: 3–20 tỷ); Chủ tịch PAT = ông Lưu Bách Đạt | `../inputs/legal_and_news_scan_20261029.md` (Đ.235 bản 2017: 3–7/7–12/12–20); tên Chủ tịch PAT: `calculated_fear_state_backstop.md:1090` |
| 12 | Câu cụt §8 viết lại; biên độ biên gộp "≈ 4,8 nghìn" (+217…+5.034) tách khỏi nguồn quặng 5,3; thêm câu đối chiếu LNST 2025 tự lập 3.188,97 vs 3.025 trong cơ sở dữ liệu (chênh 164 tỷ, chưa đối chiếu) | `figs/fig_00_hero.csv`; BCTN tr. 15 |

Giới hạn còn lại: sửa rev2 chưa được người phản biện rà lại; Ke nội địa chưa phản biện độc lập đầy đủ.
