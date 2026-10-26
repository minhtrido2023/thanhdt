# DGC — Dự báo BCTC hợp nhất Q3/2026 KHOÁ TRƯỚC (job Taylor_20261026_064029)

Lập 2026-10-26 ~13:45 ICT bởi Taylor. READ-ONLY, không phải khuyến nghị mua bán.
⚠️ **WARNING pháp lý:** DGC đang trong vụ án hình sự (lãnh đạo bị khởi tố), cổ phiếu ở diện hạn chế giao dịch
HOSE. BCTC 2025 (UHY) có 2 ý kiến ngoại trừ (tồn kho ~951 tỷ chưa chứng kiến kiểm kê; tác động của điều tra
chưa đánh giá được). Phân tích bình thường theo luật 2026-09-27.

## 0. Trạng thái công bố tại lúc khoá
- BQ `tav2_bq.ticker_financial`: DGC có tới 2026Q2 (Release 2026-07-22), **CHƯA có 2026Q3** (query 26/10 ~13:40 ICT).
- Báo chí đến 26/10: chỉ thấy PAT (công ty con) công bố Q3; DGC chỉ có **dự báo** (MBS ~350 tỷ LNST mẹ, nguoiquansat.vn 29/09/2026).
  Bài nguoiquansat "Cập nhật KQKD Q3 ngày 26/10" (đăng 25/10 21:48) không có số DGC.
- Lịch sử Release_Date Q3 của DGC (BQ): 2021-10-19, 2022-10-19, 2023-10-23, 2024-10-22, 2025-10-24 ⇒ năm nay **đã trễ** so với lệ
  thường (Q1/2026 cũng trễ: 2026-04-29). Hạn luật cho BCTC hợp nhất quý của công ty mẹ: 30 hoặc 45 ngày (ước lượng ngày công bố: 27/10–14/11).

## 1. Quan hệ DGC–PAT
- DGC sở hữu **gián tiếp 51%** PAT qua Công ty TNHH MTV Hóa chất Đức Giang Lào Cai (100% DGC) ⇒ **hợp nhất toàn bộ**, lợi ích CĐKKS 49%
  (nguồn: báo chí tổng hợp từ BCTN/CBTT, nhadautu.vn, baodautu.vn; ĐHĐCĐ 2024 có ý định sáp nhập PAT, chưa thấy hoàn tất).
  Đào Hữu Duy Anh 9,03%, Đào Hữu Huyền 7,69% nắm trực tiếp PAT.
- Kiểm tra chéo bằng số: Q2/2026 LNST hợp nhất 440 − LNST mẹ 389 = CĐKKS ~51 tỷ; 49% × LNST PAT Q2 (109,8 tỷ, BQ) = 53,8 ⇒ khớp, PAT ≈ gần toàn bộ CĐKKS.
- Tỷ trọng: doanh thu PAT Q2 517 tỷ ≈ 21% doanh thu hợp nhất DGC Q2 (2.415) **trước loại trừ nội bộ**; LNST PAT ≈ 25% LNST hợp nhất Q2.
  PAT là cơ sở phốt pho vàng (P4) ở Lào Cai; mức bán P4 cho DGC (nội bộ) vs xuất khẩu trực tiếp: **chưa xác minh được** từ nguồn công khai
  — đây là điểm mù chính (nếu PAT bán phần lớn cho DGC thì biên PAT phản ánh giá chuyển nhượng nội bộ, không phải biên cụm P4).

## 2. PAT Q3/2026 (đã công bố) và điều nó cho biết
Nguồn: tinnhanhchungkhoan.vn 24/10/2026 08:08 (post400112); cafef 25/10/2026. BCTC gốc chưa đọc trực tiếp.

| tỷ đồng | Q3/2025 | Q2/2026 (BQ) | Q3/2026 |
|---|---|---|---|
| Doanh thu | ~507 | 517,4 | **440,0** (−13,2% YoY, −15% QoQ) |
| Biên gộp | 25,7% | 21,2% | **14,5%** |
| Thu nhập TC | ~13,8 | — | 11,4 |
| CP BH+QLDN | ~24,7 | — | 9,8 |
| LNST | ~110 | 109,8 | **59,3** (−46,1%) |

Giải thích của PAT: doanh thu giảm do **sản lượng phốt pho vàng giảm**; giá vốn tăng do nguyên vật liệu đầu vào đều tăng. 9T/2026 LNST 215,7 tỷ (77% KH 280 tỷ).
Hàm ý (không suy tuyến tính):
- Cụm P4: biên gộp −6,7pp QoQ; LNST PAT chỉ giảm ~46% nhờ CP BH+QLDN giảm mạnh (khoản này không lặp lại cho DGC).
- Giá P4 TQ (SunSirs, `data/phosphorus_weekly.csv`, nguồn CHƯA có trong `kb/data_registry/`): TB T4–T6/2026 ≈ 31.600 RMB/t → TB T7–T9 ≈ 27.600 (**−13% QoQ**); T10 ~28.100 (đi ngang).
  Kết hợp sản lượng giảm ⇒ doanh thu P4 của DGC giảm QoQ là kịch bản cơ sở.
- PAT KHÁC DGC: PAT là lò điện P4 (quặng + than cốc + điện), **không dùng lưu huỳnh**; DGC còn axit photphoric trích ly ướt (H2SO4 từ lưu huỳnh), DAP/MAP, phụ gia thức ăn, xút/clo,
  và thu nhập tài chính lớn (~194 tỷ/quý). Do đó PAT chỉ là đại diện cho mảng P4, không cho chi phí lưu huỳnh.

## 3. Dữ liệu đầu vào khác
- DGC Q1/2026: DT 2.125, LN gộp 488,7 (biên 23,0%), LNST mẹ ~409 (BQ) / ~430 LNST (ACBS).
- DGC Q2/2026 (Vietcap flash 22/07/2026): DT 2.415 (xuất khẩu 2.097, nội địa 318 −69,5% YoY), LN gộp 456 (**18,9%**), BH −71, QLDN −54, EBIT 330,
  TNTC 194, CPTC −16, LNTT 507, LNST 440, **LNST mẹ 389**. ⚠️ BQ ghi NP_P0 2026Q2 = 380,1 và GPM_P0 = 24,8% — LỆCH báo chí (biên lệch 5,9pp; Q1 BQ 28,7% vs 23,0%):
  không dùng GPM_P0 của BQ cho 2026; **nguồn chấm là BCTC gốc**.
- Bảng CĐKT 30/6: tiền+tiền gửi 10.921 tỷ, vay 1.870, tồn kho tăng 46% (Vietcap 2,5 nghìn tỷ), CFO H1 −10 tỷ; cổ tức 2025 còn 5.000 đ/cp chưa trả (ngày trả chưa xác minh).
- Lưu huỳnh (KSP Kuwait FOB, Argus/SMM/fertilizerdaily): T4 570, T5 765, T6 805 ⇒ TB Q2 ~713 $/t; T7 950, T8 865, T9 ~860–890 (spot Argus ME, thứ cấp, ước lượng) ⇒ TB Q3 ~895 (**+26% QoQ**, ước lượng);
  MBS: ~4× cùng kỳ. Có độ trễ tồn kho ⇒ Q3 gánh giá T5–T8.
- DAP (WB CMO `data/dap_monthly.csv`): TB Q2 759,5 → Q3 798,5 $/t (+5%). Urê Q2 693 → Q3 399. Brent T9 116,8.
- Xút: `data/caustic_soda_monthly.csv` chỉ tới 2026-05 (680 $/t, đi xuống) — không cập nhật được Q3.
- Khai trường 25 / 19B: tạm dừng từ cuối 2025, đến báo cáo TCBS 29/07/2026 chưa có thời điểm khôi phục; không tìm thấy tin khôi phục T9–T10 ⇒ giả định **100% quặng mua ngoài cả Q3**.
- Nghi Sơn: Vietcap kỳ vọng vận hành Q4/2026 ⇒ **không đóng góp Q3** (có thể có chi phí chạy thử, chưa đo).

## 4. Mô hình Q3/2026 (tất cả là ƯỚC LƯỢNG)
Cầu: DT × biên gộp − BH&QLDN (125, = Q2) + TNTC − CPTC (18) ⇒ LNTT; thuế hiệu dụng 13% (Q2: 1 − 440/507); trừ CĐKKS ≈ 49% × LNST PAT (+ nhỏ).

| Kịch bản | XS | DT | Biên gộp | LN gộp | TNTC | LNTT | LNST | CĐKKS | **LNST mẹ** |
|---|---|---|---|---|---|---|---|---|---|
| Thuận | 0,20 | 2.450 | 19,0% | 466 | 195 | 518 | 450 | 30 | **420** |
| Cơ sở | 0,50 | 2.250 | 16,0% | 360 | 185 | 402 | 350 | 29 | **321** |
| Nghịch | 0,30 | 2.050 | 12,5% | 256 | 170 | 283 | 246 | 27 | **219** |

Lý do theo mảng (ước lượng định tính, không có công bố cơ cấu doanh thu theo mảng):
- P4 và dẫn xuất (TPA…): giá −13% QoQ, sản lượng PAT giảm ⇒ doanh thu mảng giảm, biên bị ép (PAT −6,7pp).
- Axit photphoric / DAP-MAP / phụ gia: giá lưu huỳnh +26% QoQ (ước lượng) và quặng nhập ⇒ biên giảm tiếp; giá DAP +5% bù được một phần.
- Xút/clo: nhỏ, giá đi xuống tới T5; giả định đi ngang.
- Thu nhập tài chính: số dư tiền gửi ~10,9 nghìn tỷ cuối Q2; nếu đã trả 5.000 đ/cp (ước lượng ~1,9 nghìn tỷ) trong Q3 thì TNTC giảm ⇒ cơ sở 185, khoảng 165–205.
- Rủi ro đuôi xấu KHÔNG mô hình hoá: trích lập/điều chỉnh tồn kho (giá P4 giảm, tồn kho +46%), dự phòng liên quan điều tra (thuế/tài nguyên mỏ). Đuôi tốt: hoàn nhập, chênh lệch tỷ giá.

## 5. DỰ BÁO KHOÁ (BCTC hợp nhất Q3/2026, riêng quý)
| Chỉ tiêu | Điểm | Khoảng 50% | Khoảng 80% |
|---|---|---|---|
| **(a) LNST cổ đông công ty mẹ** | **320 tỷ** | **[270 ; 370]** | **[215 ; 425]** |
| (b) Doanh thu thuần | 2.250 tỷ | [2.130 ; 2.380] | [1.980 ; 2.520] |
| (c) Biên gộp (LN gộp / DT thuần) | 16,0% | [14,3% ; 17,8%] | [12,3% ; 19,8%] |
| (d) Doanh thu hoạt động tài chính | 185 tỷ | [175 ; 196] | [160 ; 210] |

Hàm ý: LNST mẹ Q3 ≈ −57% YoY (Q3/2025 = 751,6 tỷ BQ) và ≈ −18% QoQ (Q2 = 389). Xác suất LNST mẹ < Q2 (389): ~0,80 (ước lượng chủ quan).
So với đồng thuận báo chí: MBS ~350 ⇒ dự báo này thấp hơn ~30 tỷ, chủ yếu do tín hiệu PAT.

## 6. Biến số quyết định (xếp theo độ nhạy)
1. Biên gộp: ±1pp ≈ ±22 tỷ LN gộp ≈ ±19 tỷ LNST mẹ. Phụ thuộc giá lưu huỳnh qua tồn kho + giá P4 xuất khẩu + có điều chỉnh tồn kho không.
2. Sản lượng/doanh thu xuất khẩu P4 (PAT báo sản lượng giảm).
3. TNTC (thời điểm trả cổ tức 5.000 đ/cp).
4. Khoản bất thường (dự phòng điều tra, tồn kho bị ngoại trừ kiểm toán).

## 7. Vai trò PAT
- Bỏ PAT (chỉ dùng giá P4 TQ −13%, lưu huỳnh +26%, DAP +5%): dự báo cơ sở sẽ là biên ~17,5%, DT ~2.330, LNST mẹ ~350 (ước lượng, ≈ MBS).
- PAT kéo dự báo xuống ~30 tỷ qua 2 kênh: (i) xác nhận sản lượng P4 giảm, (ii) biên cụm P4 bị ép mạnh hơn tác động giá P4 đơn thuần.
  Có kênh bù ngược: LNST PAT giảm làm CĐKKS giảm ~22 tỷ QoQ (51 → ~29) — đã tính vào bảng.
- Nếu PAT chủ yếu bán nội bộ cho DGC, tín hiệu (ii) yếu đi (biên PAT = giá chuyển nhượng) ⇒ nghiêng về kịch bản thuận.

## 8. Ngưỡng chấm (nguồn chấm = BCTC hợp nhất Q3/2026 gốc của DGC, KQKD riêng quý 3, dòng "LN sau thuế của cổ đông công ty mẹ")
- **TRÚNG (chính):** LNST mẹ Q3/2026 ∈ **[270 ; 370] tỷ**. Trúng nới: ∈ [215 ; 425].
- **Trúng hướng:** LNST mẹ Q3 < 389 tỷ (dưới Q2) và < 751,6 tỷ×0,5 = 376 tỷ (giảm >50% YoY).
- Phụ: DT thuần ∈ [2.130 ; 2.380]; biên gộp ∈ [14,3% ; 17,8%]; DT tài chính ∈ [175 ; 196] (khoảng 50%). Mỗi chỉ tiêu cũng chấm theo khoảng 80%.
- Chấm thêm điểm log/Brier theo 3 kịch bản: kịch bản trúng = kịch bản có LNST mẹ gần nhất (biên giữa: 270 và 370).
- Hạn chấm: khi DGC công bố (ước lượng 27/10–14/11/2026). Nếu BCTC có khoản bất thường >100 tỷ, vẫn chấm trên số báo cáo, ghi chú riêng.

## Nguồn
- BQ `tav2_bq.ticker_financial` (DGC, PAT, 2018–2026Q2), query 26/10/2026.
- PAT Q3: https://www.tinnhanhchungkhoan.vn/apatit-viet-nam-pat-lai-rong-quy-iii2026-giam-461-ve-5932-ty-dong-post400112.html ; https://cafef.vn/cong-ty-con-cua-hoa-chat-duc-giang-dgc-bao-lai-quy-3-2026-giam-46-so-voi-cung-ky-188261025132626838.chn
- DGC Q2: https://www.vietcap.com.vn/en/research-center/dgc-h1-2026-npat-mi-falls-52-yoy-on-weaker-volumes-cost-pressure-2026-agm-guidance-implies-downside-risk-earnings-flash-agm-documents-note ; https://elibook.vn/2026/09/08/dgc-loi-nhuan-quy-2-roi-hon-nua-kiem-toan-ngoai-tru-va-ghe-chu-tich-doi-nguoi-nhung-khong-doi-ho/ ; https://www.tcbs.com.vn/fc/kqkd_dgc_q2_26
- MBS dự báo: https://nguoiquansat.vn/hoa-chat-duc-giang-dgc-chua-het-kho-khan-loi-nhuan-quy-iii-2026-co-the-boc-hoi-50-319073.html
- Sở hữu PAT: https://nhadautu.vn/mot-cong-ty-con-cua-dgc-sap-len-san-upcom-d66869.html ; https://doanhnhan.baophapluat.vn/apatit-viet-nam-pat-sap-chi-72-5-ty-dong-co-tuc.html
- Lưu huỳnh: https://www.argusmedia.com/en/news-and-insights/latest-market-news/2822615-kuwait-s-kpc-raises-may-sulphur-price-by-195-t ; https://www.fertilizerdaily.com/20260709-kuwait-kpc-sulphur-price-record/ ; https://news.metal.com/newscontent/103939358 ; https://api.argusmedia.com/articles/2860769 (tra 26/10/2026)
- Khai trường: https://www.tcbs.com.vn/fc/kqkd_dgc_q2_26 ; https://acbs.com.vn/acbsmedia/2026/05/DGC_Cap-nhat-nhanh-11.05.2026-1.pdf
- Giá P4 TQ: `data/phosphorus_weekly.csv` (SunSirs, tới 2026-10-23); DAP/urê/Brent: `data/*_monthly.csv` (WB CMO, tới 2026-09).
