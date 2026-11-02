# DD — TV1 (CTCP Tư vấn Xây dựng Điện 1 / EVNPECC1, UPCOM) sau BCTC Q3/2026 · as-of 02/11/2026 · **VÒNG 5 (job `Taylor_20261102_100630`) — sửa theo phản biện vòng 3 (B1–B3, N1–N12), Phụ lục E4; thay vùng r4** · VÒNG 4 (job `Taylor_20261102_094407`) — DỰNG LẠI ĐỊNH GIÁ theo kịch bản giá PPA Sông Bung 5; kết luận r3 bị thay (Phụ lục E3)** · job gốc `Taylor_20261102_035322` · VÒNG 2 (job `Taylor_20261102_042353`) · **VÒNG 3 (job `Taylor_20261102_075340`) — đã áp 4 BLOCKING + 10 NON-BLOCKING của phản biện vòng 2, xem Phụ lục E2**

> NGHIÊN CỨU READ-ONLY. Không khuyến nghị, không lệnh, không wire. User đang/đã giao dịch TV1 ngoài book V2.4 ⇒ "giữ/thêm/giảm" là quyết định của user; báo cáo chỉ đưa vùng giá + điều kiện đổi nhận định. Vòng 1 bị fundamental-skeptic phản biện REFUTED (mức văn bản/số liệu); vòng 2 áp 12 đính chính (Phụ lục E); vòng 2 bị phản biện REFUTED (medium) với 4 BLOCKING — bản này là vòng 3, đã áp toàn bộ (Phụ lục E2). **Đã qua 2 vòng phản biện (r1, r2). r3 và r4 CHƯA qua vòng 3. r4 thay định giá r3 (lỗi phương pháp: bỏ quên nghiên cứu giá PPA 13/10).**
> **Nguồn:** [Q3 tr.X] = trang PDF `src/hn_q3_2026.pdf` (BCTC HN Q3/2026, ký 29/10/2026, **chưa soát xét**, bản scan) · [ME tr.X] `src/me_q3_2026.pdf` (BCTC tổng hợp/công ty mẹ) · [GT] `src/giaitrinh_hn_q3_2026.pdf` (CV 6603/TVĐ1-P3) · [H1 tr.X] = số trang **in** của `src/hn_h1_2026.pdf` (soát xét An Việt) · [Q2 tr.1] `src/hn_q2_2026.pdf` · [FY25 tr.X] = số trang in của `src/hn_fy2025_audited.pdf` (BCTC HN 2025 kiểm toán A&C) · [LV] `LEGAL_VN_20261102.md` (tra cứu pháp lý, tham khảo — cần luật sư xác nhận) · [IR] CBTT tải từ pecc1.com.vn vào `src/ir/` · [CB] `../dd_blind2_TV1_20261026/CYCLE_BLOCK.md` (khoá md5 4409305f…, 26/10) · [BQ] `tav2_bq` (lịch sử; chưa có dòng 2026Q3 của TV1 tại 02/11) · [DNSE] `calc/dnse_raw.json` (lấy 02/11/2026 ~10:50 ICT).
> Phép tính: `calc/valuation.py` → `calc/valuation_out.txt` (tái lập: `python3 -I calc/valuation.py`). Số tự đặt gắn **[UL]** (ước lượng). Ngành: `kb/data_registry/market-state/sector_read_power_consulting_20261028.md` (Bobby, đọc mù).

## 0. Kết luận (VÒNG 5 — sửa theo phản biện vòng 3; thay kết luận r4)

> **Bản r5 (job `Taylor_20261102_100630`) thay vùng r4 "8.700–10.600, tâm 9.900, giá +86…+129% (gấp đôi)".** Phản biện vòng 3 (`SKEPTIC3_20261102.md`, REFUTED medium) xác nhận HƯỚNG (giá > giá trị trừ khi PPA giữ giá) nhưng chỉ ra MỨC r4 là đầu bi quan: DDM không cho tiền tích luỹ sinh lãi và định giá tiền dưới mệnh giá (B1); P/E 5–6 lấy từ năm thị trường đã chiết khấu rủi ro PPA rồi áp lên LNST đã cắt ⇒ phạt kép (B2); câu "không tổ hợp nào đạt 19.800" bị chính SOTP bác (B3). r5 sửa hết trong một lần (Phụ lục E4). **Chưa qua phản biện vòng 4. Thay bản 02/11 15:25 (r3) đã gửi; chưa gửi bản r4 nào.**

**Giá 19.800 đ (30/10/2026) CAO HƠN vùng giá trị cân bằng 13.900–18.100 đ/cp, tâm ~15.900** [UL; `valuation_out.txt` khối "r5"] — giá cao hơn vùng **+9%…+42%, so tâm +25%**. Vùng = min–max của hai phương pháp đồng hạng, kỳ vọng trên 4 kịch bản giá PPA × 2 trạng thái pháp lý × mốc hạ bậc (đúng 2027 / lùi 2 năm): **(i) P/E 6,5–7 trên LNST hoạt động bền 2027+ cộng tiền ròng cuối 2027** ⇒ 17.000–18.100; **(ii) DDM cổ tức** (payout 27–40%; tiền giữ lại hưởng lãi 5% trước thuế, cộng theo mệnh giá ở năm 10; P/B ≤0,6 chỉ áp VCSH hoạt động) ⇒ 13.900–14.500. **Giá hiện tại ngang giá trị khi giá PPA ròng ≥~590 đ/kWh VÀ pháp lý ổn** (đầu trên dải lãnh đạo nêu 500–600).

**Trục chính = giá PPA Sông Bung 5 sau mốc hạ bậc** — thuỷ điện tạo 67% lãi gộp 2025 [FY25 tr.34: DT 261,6, KQ bộ phận 165,1]; giá ròng 2025 ≈949 đ/kWh (đã tách thuế TN + phí DVMTR ≈37,2 tỷ):

| Kịch bản giá ròng 2027+ | P [UL] | Căn cứ | LNST hoạt động bền (ổn / cấm thầu, mid Q205) | P/E 6,75 (ổn / cấm thầu) | DDM 27 / 40% (ổn) |
|---|---|---|---|---|---|
| (a) giữ ~975 | **0,10** | Chứng cứ NGƯỢC: BCTN 2025 tr.38 "giá điện… sụt giảm" (trích 13/10, chưa kiểm lại); lời lãnh đạo mốc 2027 (KBSV 17/04/2026, chưa đọc được bản gốc); vay dự án tất toán 31/3/2025. Thuận: mốc 2022 của dự thảo 2018 đã trôi; KH 2026 bán điện 187 tỷ | 143 / 118 | 35.100 / 28.000 | 21.700 / 22.800 |
| (b) 600 | **0,45** | Lời lãnh đạo 500–600 (qua KBSV) — trung tâm; tóm tắt tìm kiếm một báo cáo CTCK (nghi VCBS, chưa đọc được bản gốc): DT điện 2026–30 ~160 tỷ/năm ≈ giá ròng ~590 | 82 / 57 | 20.100 / 13.100 | 15.000 / 15.700 |
| (c) 500 | **0,35** | như (b) | 65 / 40 | 16.200 / 9.100 | 13.200 / 13.700 |
| (d) ~340 | **0,10** | Văn bản 2018 (PECC1 PA bán SB5 tr.13): bậc 243,66 + O&M ~95. Nhưng chưa bậc nào từng áp (giá ròng thực 2021–25 ≈870–950) và lời lãnh đạo 2026 mới hơn ⇒ hạ 0,20 → 0,10 | 39 / 14 | 9.800 / 2.700 | 10.400 / 10.700 |
| **Kỳ vọng** (P cấm thầu 0,30; P mốc lùi 0,15) | | | | **17.600** (6,5: 17.000 · 7: 18.100) | **13.900 / 14.500** |

Giả định chung [UL]: sản lượng giữa **205** tr kWh (bình quân các năm có số 2015–2025 = 207, thiếu 2018–20/2024; nhạy 175–210, 2013–23 công ty 175,3); O&M tiền mặt 25; khấu hao 38; chi phí chung phân bổ 8; thuế 20%; tư vấn LNST 30/40/50 nếu pháp lý ổn, **10/15/20 + khoản buộc nộp/bồi thường một lần 30 tỷ** nếu cấm thầu EVN (**cùng P/E** — PPA không phụ thuộc đấu thầu, không phạt hai lần); tiền ròng đầu 2027 = −38,7 (30/9) + LN Q4/2026 ở giá cũ 40 + KH−capex quý − cổ tức FY2026 − quỹ KTPL FY2026 ≈ **−63,5 tỷ**; lãi tiền 5%/năm trước thuế; cổ tức FY2026 **1.000/1.500/2.000** (KH 10%; nhưng tiền lệ KH FY2025 6% → thực trả 15%, KH LNST 2026 104,2 trong khi 9T đã 124,6); PV về 11/2026, Ke 12,3–13,4%.

**Vì sao chọn P/E 6,5–7 (B2):** LNST đã CẮT theo giá PPA mới ⇒ rủi ro hạ bậc đã nằm trong mẫu số, không chiết khấu thêm ở bội số. Trung vị P/E 23 mã thuỷ điện niêm yết [BQ `calc/bq_hydro_peer_pe.csv`]: 2024 14,2 · 2025 12,8 · 2026 YTD 10,9 (p25 9,1). 6,5–7 = chiết khấu ~35–40% so trung vị 2026 cho UPCOM thanh khoản thấp (ADV ~0,4–0,7 tỷ), quy mô nhỏ, mảng tư vấn chu kỳ. P/E TV1 2025 6,0 / 2026 YTD 5,1 là bội số trên LNST **chưa cắt** — thị trường đã chiết khấu PPA ở đó ⇒ không dùng lại. Nhạy: P/E 5,5 ⇒ 14.700; 6,0 ⇒ 15.900; 8 ⇒ 20.400; 9 ⇒ 22.700.

**Vì sao DDM thấp hơn P/E (viết lại, B1):** sau sửa, khoảng cách còn ~3.000–4.000 đ/cp và đến từ đúng một chỗ — **phần giá trị hoạt động ở năm 10** được tính theo P/B ≤0,6 trên VCSH hoạt động (thanh khoản thấp, thiểu số không quyết phân phối), còn P/E ngầm định giá trị đó theo bội số 6,5–7 lần lợi nhuận. Tiền giữ lại **không còn bị phạt**: ví dụ (c)/ổn/payout 27% = PV cổ tức 4.700 + terminal hoạt động 1.900 + tiền ròng năm 10 (586 tỷ, theo mệnh giá) 6.600 = 13.200 (r4: 9.200). Nhạy: lãi tiền 0% ⇒ DDM40 13.800; 3% ⇒ 14.200; 6,5% ⇒ 14.700; terminal P/B trần 1,0 ⇒ 15.700.

**Phép thử cổ tức (đồng hạng):** cổ tức cần có để biện minh 19.800 = **2.435–2.650 đ/năm** (Gordon g=0, Ke 12,3–13,4%). Cổ tức bền 2028+ ở payout 27%: (a) 1.460 · (b) 830 · (c) 660 · (d) 390 đ; payout cần: (a) 45% · (b) 80% · (c) 100% · (d) 170%. DDM vẫn cho thấy: với cổ đông thiểu số nhận tiền qua cổ tức, 19.800 chỉ đứng được nếu giá điện giữ hoặc tiền tích luỹ cuối cùng được trả ra/định giá đủ.

**Tổ hợp đạt 19.800 — chỉ trong P/E/DDM của cổ đông thiểu số (B3):** (a) giữ giá — mọi phương pháp (P/E 7 ổn 36.300; cấm thầu 29.000; DDM40 19.400–22.800); (b) 600 + pháp lý ổn ở P/E 7 (20.800); (b)/(c) + pháp lý ổn + mốc lùi 2 năm ở P/E 7 (23.800 / 20.500). Không tổ hợp nào ở (d) hoặc ở (b)/(c) + cấm thầu. Nếu 500–600 thực ra là **giá cố định chưa gồm O&M** (N2 — chưa kiểm được bản gốc KBSV) thì giá ròng ≈595–695 ⇒ P/E 22.100–23.900, DDM40 16.600–17.500 — tức giá hiện tại nằm trong vùng.

**SOTP (giá trị tài sản, không phải kỳ vọng của cổ đông thiểu số):** DCF thuỷ điện 2027–2059 (Q205) + tư vấn 40×6 + tiền ròng −38,7: (a) 45.100–51.100 · (b) 27.700–30.800 · (c) 23.000–25.400 · (d) 15.500–16.600 (r 13–11%); kỳ vọng r 12% **28.000** (trộn pháp lý 25.900). (b)/(c) đều **cao hơn** 19.800. Tâm 15.900 = SOTP trộn × 0,61 ⇒ **chiết khấu tiếp cận ngầm định ~39%** (43% so SOTP không trộn) — **ở mép trên** thông lệ holding/thiểu số 20–40% (thông lệ áp lên SOTP trộn ⇒ 15.600–20.800). Giá 19.800 = SOTP trộn × 0,76 (chiết khấu 24%, trong thông lệ). Đọc cân: theo giá trị tài sản, giá hiện tại không đắt; theo dòng tiền cổ đông thiểu số thực nhận, giá cao hơn kỳ vọng. Lịch sử bán SB5 cho thấy tài sản khó hiện thực hoá: **≥5 lần đấu giá không có người đăng ký, 01/2019 (1.688 tỷ) → 11/2020 lần 4 (1.390) → 05/2021 lần 5 (1.351,7 tỷ, chưa VAT/phí trả nợ trước hạn)** (baodauthau.vn; Công ty Đấu giá Hợp danh Quốc gia).

**Nhạy kết luận (mid, P/E 6,75 | DDM40):** trọng số giá r4 (10/35/35/20) + P xấu 0,35 ⇒ 16.200 | 13.800; P xấu 0 ⇒ 19.700 | 15.500; P mốc lùi 0 / 0,30 ⇒ 17.100 / 18.000 | 14.200 / 14.800; lạc quan (25/45/25/5, P xấu 0) ⇒ 22.700 | 17.000; bi quan (5/30/40/25, P xấu 0,40) ⇒ 14.400 | 13.000; Q giữa 175 / 236,6 ⇒ 14.100 / 21.200 | 12.800 / 16.300; Ke 15,1% ⇒ 17.100 | 12.600. Dải hai chiều 12.600–22.700 bao quanh giá; **kết luận "giá cao hơn tâm" đổi chiều khi PPA ≥~590 + pháp lý ổn, hoặc sản lượng bền ≥~230, hoặc P/E ≥~8.**

**N7 (tách rõ):** LN Q4/2026 ở giá cũ giữ lại ≈ +1.800 đ/cp; tiền ròng điều chỉnh hôm nay −38,7 tỷ ≈ −1.450 đ/cp; cổ tức FY2026 + quỹ KTPL ra ≈ −2.700 đ/cp (cổ tức về tay người giữ, cộng riêng).

**Ngoài giá điện, phần còn lại giữ nguyên:** Q3 LNST 66,9 tỷ có 1/3–3/4 không lặp lại/chưa giải thích (§3); rủi ro pháp lý §7; đuôi xấu mới (N9, không đưa vào kỳ vọng): nếu biểu giá 2018 bị áp hồi tố, chênh 2022/2023/2025 ≈415 tỷ trước thuế (~12.400 đ/cp sau thuế) — tiền lệ Sông Bung 4A (Thanh tra Chính phủ): ký lại giá 7/2022 về trần khung 1.110 đ/kWh và yêu cầu EVN "xác định tiền lãi" phần trả vượt; **chưa thấy xác nhận truy thu hồi tố** (vnbusiness.vn) ⇒ quy mô, không phải xác suất.

| | Tích cực (có chứng cứ) | Tiêu cực (có chứng cứ) |
|---|---|---|
| Giá PPA SB5 | Chưa có văn bản mức/mốc; lịch hạ bậc 2022 của dự thảo 2018 không xảy ra; KH 2026 bán điện 187 tỷ; 500–600 có thể là giá cố định chưa O&M (chưa kiểm) | Văn bản 2018 bậc 569,36 → 243,66; công ty thừa nhận "sụt giảm"; lãnh đạo: từ 2027 xuống 500–600 |
| Lợi nhuận | Tư vấn 9T +29% DT [UL]; công ty đặt KH thấp (KH LNST 2026 104,2 < 9T 124,6) | LNST hoạt động bền (b)/(c) ổn 65–82 tỷ vs 2025 150,2 |
| Cổ tức | FY2025 1.500 (KH chỉ 6%); tiền tích luỹ sinh lãi | KH FY2026 10%; payout 27% + 20% KTPL; cần ≥80% payout ở (b) để biện minh giá |
| Pháp lý, kế toán | Pháp nhân không bị truy cứu hình sự 5 tội danh [LV] | Chủ tịch + phó phòng TCKT bị khởi tố; TV1 trong 13 công ty liên quan; thu nhập khác Q3 chưa thuyết minh; đuôi truy thu biểu giá (N9) |
| Định giá | SOTP trộn 25.900 > giá (giá = chiết khấu 24%) | P/E/DDM kỳ vọng 13.900–18.100 < giá; P/E LNST bền (b)/(c) ổn 6,5–8,1x |

**Điều làm nhận định TÍCH CỰC hơn:** (1) **văn bản** xác nhận giá PPA ròng ≥~600 đ/kWh (hoặc 500–600 là giá cố định chưa O&M) hoặc mốc lùi ≥2 năm; (2) điện mặt trời lòng hồ có chủ trương + giá bán/hợp đồng, vốn không pha loãng; (3) cổ tức FY2026 ≥2.000 đ hoặc cam kết payout ≥50%; (4) bán SB5 ≥1.000 tỷ; (5) vụ án kết thúc không cấm thầu/buộc nộp + kiểm toán FY2026 chấp nhận toàn phần. **Điều làm TIÊU CỰC hơn:** (1) văn bản xác nhận ≤500 hoặc gần 340 đ/kWh; (2) quyết định cấm thầu EVN; (3) kiểm toán ngoại trừ; (4) đầu tư ~800 tỷ điện mặt trời bằng vay/phát hành khi chưa có giá bán; (5) cổ tức FY2026 thấp hơn mức thực trả FY2025 (<1.500 đ) — so với tiền lệ thực trả, không so KH; (6) văn bản truy thu phần giá trả vượt 2022–2026.

## 1. Kiểm lại số dùng lại (DD cũ, CYCLE_BLOCK, checklist)
| Số | Nguồn cũ | Kiểm | Kết quả |
|---|---|---|---|
| "Nợ dự án trả hết", net debt ~117 (SOTP 23/07) | BQ | Vay DH 0,41 tỷ [Q3 tr.4] ✅; nhưng vay NH 129,5 chủ yếu là **vay cá nhân/bên liên quan** (118,8) [Q3 tr.21], không phải "vốn lưu động tư vấn" | Nửa đúng — nay net cash thô +68,7, net điều chỉnh −38,7 |
| FCF thuỷ điện 110–140/năm (SOTP 23/07) | UL | Dựng lại từ hàm chi phí [CB B]: 101 (DT 171) / 122 (DT 200) / 150 (DT 239) | Cùng vùng; SOTP bảo thủ cũ 33.100 đ/cp **không tái lập** khi cắt PPA −20% từ 2034 + Ke 13%: 23.900 |
| Phải thu tư vấn "~295 tỷ" (checklist) | BQ 2026Q1 | Phải thu KH **gộp 387,5 / ròng 319,1** tại 30/9 [Q3 tr.12] | Số 295 là khái niệm khác (BQ); dùng BCTC |
| "Big4 từ chối FY2026" | SOTP 23/07 | Đã ký An Việt 18/08 [IR] | Rủi ro "không có kiểm toán viên" **đã đóng**; rủi ro chất lượng kiểm toán còn |
| Cổ tức 2025 ~1.500–1.600 [CB D] | UL | 1.500 đ, GDKHQ ~07/10, chốt 08/10, trả 29/10/2026 [IR CBTT 5744] | ✅ |
| 9T LNST − H1 soát xét = Q3 | | 124,636 − 57,759 = 66,877 ✅ | Khớp; mọi phép "Q3 = 9T − H1" trong r2 dựng trên H1 SOÁT XÉT |
| BQ 2026Q3 | | `ticker_financial` chưa có 2026Q3 tại 02/11 | Dùng BCTC |
| Giá 19.800 | dispatch | DNSE ohlc 30/10 đóng 19,8, KL 156.400 cp; tham chiếu 02/11 = 20,0 (UPCOM = bình quân phiên trước) [DNSE] | ✅ |

## 2. Doanh nghiệp và ngành
- **Hai mảng** [CB loại ngành; BCTC FY25 TM VII.3a]: (1) **Thuỷ điện Sông Bung 5** 57 MW, sở hữu 100%, bán cho Công ty Mua bán điện; 2025 DT 261,6 / LN gộp 165,1 (**67% LN gộp**); thuê đất đến **08/2059**; PPA — ngày hết hạn **không có** trong BCTC đã đọc. (2) **Tư vấn KS-TK điện**: 2025 DT 447,0 / LN gộp 80,8; khách hàng phần lớn là đơn vị EVN (bên liên quan).
- **Cấu trúc**: EVN 54,34%; Lê Minh Hà 9,84% (đồng thời là bên cho vay) [CB D]. Sáp nhập MTV3 (Tư vấn XD Điện 3 Đà Nẵng, 100% vốn) vào mẹ theo HĐ 08/10/2026 [IR 6177/TB] — không đổi số hợp nhất.
- **Ngành (đọc mù)**: `STRUCTURAL_UPCYCLE` về khối lượng tư vấn, `ADMIN_GATED` về nhịp; rủi ro chính "không ở biên mà ở nhịp ghi nhận và phải thu"; kịch bản xấu gồm **hình sự hoá/thanh tra làm cán bộ ngại ký** và trần tài chính EVN. Với TV1, đọc ngành ủng hộ mảng tư vấn (DT 9T +29% [UL]) nhưng **không** bù được rủi ro tư cách nhà thầu EVN nếu pháp nhân bị kết luận vi phạm.

## 3. Chất lượng lợi nhuận [Q3 tr.6, 30-32; `valuation_out.txt`]
| Tỷ đồng | Q3/26 | Q3/25 | 9T/26 | 9T/25 |
|---|---|---|---|---|
| DT thuần | 168,1 | 149,3 | 446,9 | 390,6 |
| Biên gộp | **38,9%** | 34,4% | 36,4% | 37,4% |
| QLDN | 21,5 | 10,6 | 42,4 | 27,5 |
| EBIT lõi | 44,0 | 40,8 | 120,1 | 118,6 |
| TC ròng | +1,1 | −2,4 | −1,3 | −7,5 |
| Khác ròng | **+31,9** | −4,4 | +31,7 | −4,6 |
| LNTT | 77,0 | 34,0 | 150,5 | 106,5 |
| Thuế hiệu dụng | 13,1% | 21,4% | 17,2% | 18,9% |
| LNST | **66,9** | 26,8 | 124,6 | 86,4 |
| LNST lõi [UL, thuế 20%, chỉ bỏ khoản khác] | ~36,0 | ~30,7 | ~95,0 | ~88,9 |
| **LNST lõi (A) hoàn nhập vào QLDN** [UL] | **16–45** | ~30,7 | **~74–103** | ~88,9 |
| **LNST lõi (B) hoàn nhập vào thu nhập khác** [UL] | **31–45** | ~30,7 | **~89–103** | ~88,9 |

- **Một lần — thu nhập khác 33,8 tỷ**: dòng "các khoản khác" 33.802.250.432 đ [Q3 tr.32], mẹ 33.715.114.112 [ME tr.24] ⇒ phát sinh ở công ty mẹ. BCTC Q3 **không** thuyết minh. Bằng chứng gián tiếp (dựng trên **H1 soát xét**, không dùng mốc Q2 chưa soát xét): LCTT dòng 03 "các khoản dự phòng" 9T −22,61 − H1 soát xét −1,15 [H1 tr.8] = **−21,5 phi tiền trong Q3**; dự phòng bảng cân đối giảm **24,9** (mã 136: 105,08 [H1 tr.5] → 85,91; HTK 59,29 → 53,57) [Q3 tr.1]. Phần khác ròng không xác định **phụ thuộc trường hợp**: (A) hoàn nhập vào QLDN ⇒ **cả 31,9** không giải thích; (B) hoàn nhập phải thu vào thu nhập khác ⇒ còn **~16** (31,9 − (21,5 − HTK 5,7)) (mã 16 không dùng được làm bằng chứng). **Giả thuyết B** (chưa xác nhận): hoàn nhập dự phòng/xoá nợ vào thu nhập khác. Không phải xoá lãi vay ông Lê Phi Long: phải trả khác 30/9 90,05 ≈ 30/6 88,79 [Q3 tr.24; H1 tr.27]. **Cờ chất lượng báo cáo:** hoàn nhập dự phòng mà bên soát xét còn giữ ở 30/6 lại đi vào quý chưa soát xét.
- **Thuế hiệu dụng Q3 13,1%** — gợi ý phần lớn khoản khác không chịu thuế (hoàn nhập dự phòng đã không được trừ khi trích là lời giải phổ biến) [UL].
- **QLDN gấp đôi** — chưa thuyết minh; 9T QLDN 42,4 so FY2025 ~45 [UL]. Soát xét H1 đã cộng thêm 6,25 tỷ QLDN [explanation_yoy_en]. **LNST lõi Q3 — hai trường hợp loại trừ nhau** (bản r2 trộn: cận dưới 16 coi hoàn nhập vào QLDN, trong khi cùng khoản 21,5 lại dùng để giải thích thu nhập khác): **(A) hoàn nhập phải thu 19,2 vào QLDN, HTK 5,7 vào giá vốn** ⇒ lõi **16–45** (cận dưới bỏ cả hai hoàn nhập; cận trên coi QLDN gấp đôi là một lần, về 10,6); QLDN gộp ≈ 40,7 = ~3,9× bình quân quý H1 10,5; cả 31,9 khác ròng không giải thích. **(B) hoàn nhập phải thu vào thu nhập khác** ⇒ QLDN báo cáo 21,5 là lõi, chỉ bỏ HTK 5,7 khỏi giá vốn ⇒ lõi **31–45**; 9T 0%…+15%; P/E lõi 3,2–3,45x. Bằng chứng nghiêng A: H1 TM28 trích dự phòng phải thu ròng 0,88 nằm trong QLDN. Nghiêng B: thuyết minh VI.9c Q3 trống; QLDN 40,7 khó tin. Chưa chọn; BCTC soát xét/kiểm toán sẽ cho biết. Điểm "như báo cáo, chỉ bỏ khoản khác" = 36,0.
- **Doanh thu tài chính** 9T 7,11 tỷ, trong đó lãi tiền gửi 5,66 [Q3 tr.31] trên số dư HTM tăng 60,9→167,8 + tiền 30,7 (lãi bình quân ~5–6%/năm trên số dư bình quân ~120 tỷ [UL]) — nhỏ, không phải nguồn LN chính (khác TV2).

## 4. Tách mảng Q3 (BCTC Q3 KHÔNG có báo cáo bộ phận) [UL]
- **Proxy**: thuế tài nguyên phải nộp 9T 13,227 [Q3 tr.23] vs H1 8,776 [H1 tr.27] ⇒ Q3 = 0,507× H1 ⇒ thuỷ điện Q3 ≈ **41,2 tỷ DT** (H1 81,20 [CB A]). Giả định thuế tài nguyên tỷ lệ thuận DT thuỷ điện trong năm. **Phép kiểm trên FY2025** (do fundamental-skeptic dựng, tỷ lệ thuế TN/DT thuỷ điện: 9T/25 10,954%; Q4/25 10,959%; H1/26 10,81%) — ổn định ~10,8–11,0% ⇒ proxy đứng vững; r2 chưa tự tái lập các tỷ lệ này, nhận từ phản biện.
- Hàm chi phí thuỷ điện [CB B]: 15,2 tỷ/quý cố định + 10% DT ⇒ LN gộp thuỷ điện Q3 ~21,9; **tư vấn Q3 DT ~126,9 (+18% so ~107,7), biên ~34% theo báo cáo / ~29,9% nếu bỏ hoàn nhập HTK 5,7** (nhạy: thuỷ điện 38–45 ⇒ biên tư vấn 32,6–35,7%).
- **Checklist (1) — đường đi 80 tỷ thuỷ điện**: LN gộp thuỷ điện 9T ~64,8 [UL] = 81% của 80. Nhưng **mốc 75% sau 9T không phải đường đi đúng**: 2025 Q4 chiếm ~47% DT thuỷ điện năm (123,3/261,6 [CB A]). Nếu "80 tỷ" là LN gộp thuỷ điện thì đã gần chắc vượt (Q4 chỉ cần ~15 tỷ); nếu là LNST thuỷ điện thì 9T ~[64,8 − ~6 phân bổ]×0,8 ≈ 47 = 59% [UL], cần Q4 ≥ ~33 tỷ LNST thuỷ điện ⇔ DT Q4 ≳ 75 tỷ (Q4/25 ~123) — khả thi trừ khi El Niño cắt >40%. **Ghi rõ: nghĩa của mốc "80 tỷ" trong checklist không được định nghĩa; số thuỷ điện là ước lượng proxy, không phải số thuyết minh.**
- **Checklist (4) — giá điện 2027 / PPA SB5 — ĐÍNH CHÍNH r4:** r1–r3 ghi "Không có dấu hiệu nào, theo cả hai chiều" — **SAI**. BCTC Q3 đúng là không có thông tin, nhưng DD đã **bỏ sót nghiên cứu giá PPA có sẵn của nhóm (13/10/2026, `../tv1_sb5_ppa_price_20261013/README.md`)**, trong đó có dấu hiệu rõ theo chiều **tiêu cực**: (i) văn bản gốc PECC1 "Báo cáo phương án bán toàn bộ tài sản NMTĐ Sông Bung 5" 8/2018 tr.13 — giá cố định hai bậc 569,36 → **243,66 đ/kWh** "từ 01/01/2022 đến hết đời sống kinh tế" (dự thảo HĐ sửa đổi 05; EVN NQ 286/NQ-HĐTV 06/08/2018) — thực tế chưa hạ (giá bình quân thực hiện 2021–25 gồm thuế+phí 1.000–1.150; ròng 2025 ≈949 [`valuation_out` r4]); (ii) **BCTN 2025 tr.38**, nguyên văn: "...đầu tư dự án điện mặt trời lòng hồ Sông Bung 5 góp phần đảm bảo và duy trì doanh thu cho Công ty khi giá điện của nhà máy TĐ Sông Bung 5 sụt giảm"; (iii) **KBSV 17/04/2026 tr.4** (lời lãnh đạo): hạ giá **từ 2027** xuống **500–600 đ/kWh** (chưa thuế TN/phí DVMTR). Mức/mốc **chưa có văn bản**; hai nguồn mâu thuẫn về mức (500–600 vs ~340).
  - **Tra lại 02/11/2026 (r4):** BCTC HN 2025 kiểm toán [FY25 tr.32–36]: có báo cáo bộ phận (thuỷ điện DT 261,60 / KQ bộ phận 165,05 / khấu hao 38,14; 2024: 215,94 / 130,11 / 37,54), mục sự kiện sau niên độ "không có sự kiện trọng yếu" — **không** có biểu giá, phụ lục PPA hay cam kết giá. Tài liệu ĐHĐCĐ 2026 qua báo chí (baodauthau.vn 30/04/2026, https://baodauthau.vn/dhcd-pecc1-manh-tay-chia-co-tuc-tham-gia-loat-du-an-thuy-dien-mo-rong-luoi-dien-dien-hat-nhan-post198014.html): KH 2026 DT **641,5**, LNST **104,2** tỷ, cổ tức KH 2026 **10%**, cổ tức FY2025 nâng lên 15%; điện mặt trời nổi 46 MWp + 5 MW BESS, ~800 tỷ, "chưa thể triển khai do những thay đổi về thủ tục pháp lý" — bài **không** nêu giá điện. Bài 27/06/2025 (https://baodauthau.vn/pecc1-dat-cuoc-tuong-lai-vao-du-an-dien-mat-troi-noi-post180887.html): kỳ vọng ~90 tỷ DT/năm từ điện mặt trời; tiền khả thi đã xong; vướng quy hoạch. **Không tìm được**: văn bản PPA mới, CBTT về giá SB5, báo cáo KBSV/VCBS bản gốc (WebSearch không trả về), BCTN 2025 bản gốc (owa.hnx.vn lỗi chứng chỉ 02/11 — dùng trích dẫn nguyên văn đã ghi 13/10). ⇒ **Giá PPA 2027+: KHÔNG XÁC ĐỊNH**; định giá r4 lấy nó làm trục chính (§0, §8e).

## 5. Bảng cân đối, net cash, dòng tiền [Q3 tr.1-5, 7-8, 21-24]
| Tỷ đồng | 30/09/2026 | 01/01/2026 |
|---|---|---|
| Tiền | 30,7 | 32,1 |
| Tiền gửi HTM ngắn hạn | 167,8 | 60,9 |
| Vay (NH + DH) | 129,9 (bên liên quan 118,8) | 134,2 |
| Cổ tức phải trả | 43,2 (trả 29/10/2026) | 3,3 |
| Lãi vay cá nhân phải trả (trong "phải trả khác") | 64,3 tại 30/6 [H1 tr.27] — Q3 không tách | 60,2 |
| Người mua trả trước | 138,7 | 104,4 |
| VCSH | 574,7 | 511,3 |

- **Net cash**: thô +68,7; trừ cổ tức đã công bố (chi 29/10) và lãi vay cá nhân đã ghi ⇒ **≈ −38,7 tỷ** [UL dùng lãi phải trả 30/6]. Khoản vay cá nhân gồm tranh chấp: ông Lê Phi Long (gốc 64,4 [CB D], lãi 42,1), bà Nguyễn Thị Ngãi (phúc thẩm 26/08/2026 giữ sơ thẩm: TV1 phải trả; công ty chờ bản án để xác định toàn bộ nghĩa vụ [H1 tr.29]).
- **CFO 9T 116,8** (9T/25 137,6) = 0,94× LNST; so với LNST trừ khoản khác ròng 31,9 (92,7) = **1,26×** — dòng tiền khớp lợi nhuận lõi. Q3 CFO ≈ **69,8** [UL: 9T − H1 **soát xét** 47,03, H1 tr.8 mã 20; bản cũ dùng 54,38 chưa soát xét ⇒ 62,5 là SAI]. Tiền dư dồn vào tiền gửi HTM (chi 218,6, thu 105,9 [Q3 tr.7-8]).
- **Checklist (2) — phải thu tư vấn**: phải thu KH gộp **408,2 → 378,7 (30/6) → 387,5 (30/9)**. **Dự phòng phải thu KH GIẢM ~22 tỷ trong Q3; H1 đi ngang**: 31/12/2025 **89,93** (bên liên quan 16,75 + KH khác 73,18 — BCTC 2025 **kiểm toán** A&C [FY25 tr.21 TM6]) → 30/6 soát xét **90,81** [H1 tr.21 TM10] → 30/9 **68,36** [Q3 tr.12-13]. ⚠️ **CỜ mới (r3):** thuyết minh Q3 ghi cột đầu năm dự phòng KH **63,23** — lệch **26,7 tỷ** so BCTC đã kiểm toán (bản r2 dùng nhầm 63,2 và mô tả "H1 tăng do trích 8,98" là SAI) — bản r1 đọc ngược thành "tăng 63,2→68,4". Phải thu bên liên quan 259,7 (dự phòng 9,6; đầu năm 267,7/1,9). Công ty Mua bán điện 34,0 (đầu năm 64,5). Kết luận: phải thu gộp **không tăng**, nhưng dự phòng bị hoàn nhập mạnh trong quý chưa soát xét ⇒ **cờ, không phải điểm cộng**. Tổng dự phòng mã 136 tại 30/9 (85,9) ≠ thuyết minh (68,4 KH + 2,1 khác = 70,5): chênh ~15,4, chủ yếu có thể là dự phòng trả trước người bán (tại 30/6: 9,49 trong tổng 105,08) — chưa xác nhận cho 30/9. BCTC chưa soát xét có thuyết minh không khớp bảng là **cờ chất lượng báo cáo**, không phải bằng chứng gian lận.
- Tồn kho (dở dang tư vấn) 148,8 gộp, dự phòng 53,6 (36%) [Q3 tr.15] — chi phí dở dang cũ đã trích lập lớn.
- Điều chỉnh VCSH trực tiếp **+8,90 tỷ** ở H1 ("bù trừ thiếu trên báo cáo từ các năm trước") [H1 tr.30]. **Có lời giải khớp số:** đúng bằng dòng "Giảm khác" 8.901.255.944 trong biến động dự phòng TM10 [H1 tr.21] — dự phòng ghi giảm thẳng vào vốn, không qua KQKD. Vẫn là **cờ** (số liệu năm trước bị sửa) và cần kiểm toán FY2026 xác nhận.

## 6. Ghi nhận doanh thu tư vấn, backlog, khách hàng
- BCTC Q3 phân loại DT 9T: "bán sản phẩm, hàng hoá" 413,9 + "cung cấp dịch vụ" 33,0 [Q3 tr.30]; **không** có dòng "DT hợp đồng xây dựng" ⇒ không đọc được phương pháp % hoàn thành từ Q3. Người mua trả trước 138,7 (+33%) — proxy backlog tăng [CB B]. Không có giá trị backlog công bố.
- Khách hàng (H1, bên liên quan): Mua bán điện 63,8; BQLDA điện miền Bắc (EVNNPT) **45,5** (H1/25 2,0); BQLDA Truyền tải điện (EVNNPT) 18,2 [H1 tr.36] ⇒ **khối EVNNPT là động lực tăng DT tư vấn 2026** — đúng khách hàng nơi xảy ra vụ án. Rủi ro đấu thầu: nếu pháp nhân TV1 bị kết luận vi phạm đấu thầu, mảng này chịu rủi ro "mất vị trí" (chưa xác định).

## 7. Pháp lý, quản trị — ⚠️ WARNING (mức cao; không chặn phân tích)
- ⚠️ **Vụ EVNNPT/PC1**: 07/05/2026 khởi tố, tạm giam **Chủ tịch HĐQT (ông Nguyễn Hữu Chỉnh — theo báo chí: tội tham ô tài sản) + phó phòng TCKT** TV1; vụ án gồm "vi phạm quy định về đấu thầu… vi phạm quy định về **kế toán**… tham ô… đưa/nhận hối lộ"; chưa kết luận; ban lãnh đạo khẳng định không cần trích lập [H1 tr.38 TM33]. **TM33 KHÔNG nói "pháp nhân TV1 chưa bị khởi tố"** — chỉ nói công ty "chưa nhận được thông tin hoặc kết luận chính thức" từ cơ quan nhà nước [H1 tr.4-5, đoạn nhấn mạnh]; "chưa có thông tin khởi tố pháp nhân" ở đây là **suy từ không thấy**. **Tra tin 02/11/2026:** (i) **VnExpress 02/07/2026 18:25**, https://vnexpress.net/47-nguoi-bi-khoi-to-trong-vu-an-tai-tong-cong-ty-truyen-tai-dien-quoc-gia-5092437.html (đã mở lại 02/11/2026) — nguyên văn: **"13 công ty bị xác định có liên quan"**, gồm "các công ty CP tư vấn xây dựng điện 1, 2, 3, 4" (**= TV1 có tên**); **"EVNNPT và nhà thầu đều có sai phạm trong lập, phê duyệt dự toán"**, xây dựng hồ sơ mời thầu…; **"Các nhà thầu khi thực hiện nhiều hạng mục cũng có vi phạm."** Bài nói "47 người bị khởi tố về 5 tội danh" và **không** nói pháp nhân nào bị khởi tố. Đếm tên liệt kê trong bài chỉ ra ~12 đơn vị (chưa khớp con số 13). **Mâu thuẫn nguồn:** The Investor ghi "ít nhất 13 lãnh đạo và nhân viên" (13 NGƯỜI) [LV] — nêu cả hai. (Bài doanhnghiephoinhap.vn mà r2 dẫn không mở lại được, đã bỏ.) (ii) thêm cựu Chủ tịch EVNNPT Đặng Phan Tường bị khởi tố 13/09/2026 (cùng vụ); tổng 47 bị can theo một nguồn (chưa đối chiếu); (iii) **không thấy tin khởi tố/kết luận mới liên quan TV1/PECC1 sau 28/10** — nhưng WebSearch không phải công cụ CBTT sàn, "không thấy" ≠ không có. Cùng vụ: cựu Chủ tịch + KTT TV2, bộ ba TV3 bị khởi tố. **Soát xét H1 có HAI đoạn nhấn mạnh** [H1 tr.3-4]: (a) tổng **127,63 tỷ** nợ vay + lãi phải trả ông Lê Phi Long và bà Nguyễn Thị Ngãi — đang kiện; vụ bà Ngãi đã có phúc thẩm 26/08/2026 [tr.3]; (b) việc bắt tạm giam hai cá nhân (Chủ tịch + phó phòng TCKT) [tr.4]; bản r1 chỉ nêu (b). **BCTC Q3 không có thuyết minh vụ án (mục 32 bỏ trống)** — chưa soát xét, đã đổi từ H1.
- **Khung pháp lý với pháp nhân** [LV — thông tin tham khảo, **cần luật sư hành nghề xác nhận**]: Điều 76 BLHS (33 tội pháp nhân thương mại có thể bị truy cứu; Luật 86/2025 không sửa Điều 76) **không** gồm Đ.221 (kế toán), 222 (đấu thầu), 353 (tham ô), 354/364 (hối lộ) ⇒ theo luật hiện hành chỉ cá nhân bị truy cứu; dự thảo BLHS sửa đổi (dự kiến hiệu lực 01/03/2027, đề xuất thêm tội đưa hối lộ cho pháp nhân, chưa xác nhận thông qua) **không hồi tố**. Kênh rủi ro thực tế: (a) **cấm thầu 06 tháng–05 năm** (Luật Đấu thầu 22/2023 Đ.16, Đ.87; NĐ 214/2025 Đ.133: 3–5 năm cho hối lộ/gian lận/thông thầu; quyết định trong hệ thống EVN là rủi ro doanh thu lớn nhất; Đ.133 không nói thẳng pháp nhân bị cấm vì hành vi nhân viên, nhưng legal-vn đánh giá khả năng cao chủ đầu tư coi pháp nhân nhà thầu là chủ thể vi phạm); (b) **buộc nộp lợi bất chính/bồi thường** (BLHS Đ.47-48; BLDS Đ.597), có thể gồm lợi nhuận gói thầu; (c) **quản trị**: người đang bị truy cứu TNHS không được quản lý doanh nghiệp (LDN 2020 Đ.17). **Căn cứ P(tiêu cực) M5/R1 = 0,30 [UL]:** VnExpress nêu nhà thầu "có sai phạm" (đẩy lên) nhưng chưa có kết luận/cáo trạng, chưa kê biên/rút phép/vô hiệu hợp đồng nào được công bố (giữ dưới 0,5); không có tần suất lịch sử cho cấm thầu nhà thầu tư vấn EVN sau vụ án ⇒ con số là phán đoán. **Chưa kích hoạt HARD ABANDON.**
- ⚠️ **"Scandal di cư"**: người bị khởi tố có **phó phòng TCKT** + nhóm tội **kế toán** ⇒ rủi ro không chỉ là pháp nhân/đấu thầu mà là **độ tin cậy số liệu quá khứ** (2023–25 — giai đoạn LN tăng mạnh). Bốn dấu hiệu nhỏ cùng chiều cần theo dõi (không chứng minh sai phạm): điều chỉnh VCSH trực tiếp +8,9 tỷ (H1); thu nhập khác 33,8 tỷ không thuyết minh (Q3); dự phòng mã 136 lệch thuyết minh 15,5 tỷ (Q3); **cột đầu năm dự phòng phải thu KH trong thuyết minh Q3 (63,2) lệch 26,7 tỷ so BCTC 2025 kiểm toán (89,9)**.
- **Kiểm toán**: FY2025 A&C chấp nhận toàn phần; soát xét H1/2026 **An Việt**: kết luận chấp nhận + đoạn nhấn mạnh vụ án [H1 tr.4]; HĐ kiểm toán FY2026 với **An Việt** ký 18/08/2026 [IR CBTT 4958]. **Checklist (3)**: đã bổ nhiệm kiểm toán mới; chưa có ý kiến ngoại trừ nào. Q3 chưa soát xét.
- Tranh chấp vốn huy động cá nhân (Ngãi, Long) — tồn đọng từ 2013–17.
- Room ngoại: có CBTT "tỷ lệ sở hữu nước ngoài tối đa" [IR] — **chưa đọc nội dung** (không suy ra con số).

## 8. Định giá — `calc/valuation_out.txt`

> ⚠️ **r5:** §8b (SOTP r3), §8c (P/E 6–8x), §8d (LNST bền 103–172) dựng trên **giá điện cũ** ⇒ BỊ THAY; §8e (r4) **cũng bị thay** về mức bởi **§8f (r5)**. Giữ lại để đối chiếu; KHÔNG dùng để kết luận — mọi số kết luận lấy ở §0/§8f.
### 8a. Bội số hôm nay (giá 19.800, 26.691.319 cp)
| | Giá trị |
|---|---|
| Vốn hoá / EV (net điều chỉnh −38,7) | 528,5 / 567,2 tỷ |
| P/E TTM (Q4/25 [BQ] 63,85 + 9T/26 124,6 = 188,5) | **2,80x**; bỏ cả khoản khác ròng Q3 31,9 (không trừ thuế — nhất quán: khoản này gần như không chịu thuế) ⇒ LNST TTM lõi 156,6 ⇒ **3,38x**; (A) Q3 lõi 16–45 ⇒ **3,2–3,8x**; (B) Q3 lõi 31–45 ⇒ **3,2–3,45x** |
| P/B (VCSH 574,7) | **0,92x** (VCSH Q3 chưa soát xét, gồm khoản một lần); **1,04x** theo VCSH soát xét 30/6 (507,8) |
| Cổ tức 2025 | 1.500 đ ⇒ 7,6%; payout 27% LNST 2025 |
| Lịch sử [BQ, trung vị năm] | P/E 2024 7,9 / 2025 6,0 / 2026 YTD 4,0; P/B 2024 1,60 / 2025 1,53 / 2026 1,12 (min 0,95) |

### 8b. SOTP giá trị tài sản (trần tham chiếu, không phải kỳ vọng)
DCF thuỷ điện có thời hạn (2027–2059, thuê đất đến 08/2059 [CB D]), FCF = (DT×0,9 − 60,8 − 8 chi phí chung)×0,8 + KH 38 − capex 5 [UL]; **r2: khấu hao 38 chỉ cộng 13 năm (2027–2039; TSCĐ ròng 506,3 [H1 tr.5] / 38), sau đó FCF thấp hơn 7,6/năm (EBIT +38, thuế +7,6)** — bản r1 cộng 38 suốt 33 năm, cao ~13 tỷ (~500 đ/cp). Lãi suất **10–13%** (khớp kỳ hạn ~33 năm, rủi ro thuỷ văn + PPA; đặt quanh dải Ke nội địa 12,3–13,4% vì cổ đông chịu toàn bộ rủi ro tài sản):

| DT thuỷ điện/năm \ r | 10% | 11% | 12% | 13% |
|---|---|---|---|---|
| 171 (thiết kế 187 GWh × ~912 đ/kWh [UL]) | 949 | 874 | 809 | 753 |
| 200 | 1.148 | 1.058 | 979 | 911 |
| 239 (TB 2024–25) | 1.417 | 1.305 | 1.208 | 1.123 |

Rủi ro PPA (ngày hết hạn chưa xác định; giả định −20% DT từ 2034 [UL]): DT200 r12% ⇒ 876; DT171 r13% ⇒ 676. SOTP thấp = 676 + tư vấn 0 − 38,7 = **637 tỷ = 23.900 đ/cp** (r1: 24.300); giữa = 979 + tư vấn 40×6 − 38,7 = **1.180 tỷ = 44.200 đ/cp** (r1: 44.700). Đối chiếu: SB5 rao bán 2017–18 giá khởi điểm 1.688 → 1.390 tỷ (gồm nợ), ~~5 lần không bán được [SOTP 23/07]~~ [r5 thống nhất: ≥5 lần đấu giá 01/2019 → 05/2021, khởi điểm 1.688 → 1.390 (11/2020) → 1.351,7 tỷ (05/2021), đều không có người đăng ký — baodauthau.vn; mốc "2017–18" là SAI].

**Vì sao không dùng SOTP làm kỳ vọng:** cổ đông thiểu số nhận giá trị qua **cổ tức** (payout 27%) hoặc **bán tài sản** (tiền sử thất bại). Phép thử dòng cổ tức (g=0, Ke 12,3–13,4%): DPS 1.500 ⇒ 11.200–12.200; 2.000 ⇒ 14.900–16.300; 2.800 ⇒ 20.900–22.800 đ/cp (cao hơn giá). **Cổ tức cần có để biện minh giá 19.800 = 19.800 × Ke = 2.435–2.650 đ/năm** (65–71 tỷ ⇒ payout ~43% LNST 2025 150,2 … ~53% LNST bền cơ sở 134). ~~Giá 19.800 ≈ thị trường kỳ vọng payout tăng lên ~43–53%…~~ [BỊ THAY r5: payout cần có theo LNST sau hạ bậc = (a) 45% · (b) 80% · (c) 100% — §8f].

### 8c. Chi phí vốn, DCF vô hạn — ⚠️ BỊ THAY (r5, B2): câu "P/E hợp lý ~6–8x nếu không rủi ro pháp lý / dải 3,5–6x là chiết khấu pháp lý" không còn dùng; bội số r5 = 6,5–7 cho mọi trạng thái pháp lý, rủi ro pháp lý đi qua LNST tư vấn + khoản một lần (§8f)
Không làm DCF vô hạn cho tư vấn: DT phụ thuộc tư cách nhà thầu EVN (chưa xác định sau vụ án) — terminal Gordon sẽ là giả định chồng giả định. Dùng P/E với Ke nội địa 12,3–13,4% (khung β≈1,1 của nhóm, β TV1 chưa đo, chưa phần bù thanh khoản — xem §0) làm phép thử: tư vấn g≈0, payout cao ⇒ P/E hợp lý ~6–8x **nếu không có rủi ro pháp lý**; dải 3,5–6x ở §0 là chiết khấu pháp lý tự đặt [UL].
Bối cảnh lãi suất (chỉ để tham khảo, không đổi giá trị hợp lý): r\* thị trường 15,1% (panel 30/10/2026, n=147 mã; r hằng mô hình 12,25%), percentile 75% lịch sử 2014→2026, đỉnh 2022 15,9%, đáy 2022–23 12,1% · TPCP 10Y 4,58% @30/10/2026, +0,64 điểm % trong 12 tháng (nguồn chưa đối chiếu độc lập) [`calc/rate_lines.txt`].

### 8d. Độ nhạy LNST bền × P/E (đ/cp)
| LNST \ P/E | 3 | 3,5 | 4 | 4,5 | 5 | 6 |
|---|---|---|---|---|---|---|
| 80 | 9.000 | 10.500 | 12.000 | 13.500 | 15.000 | 18.000 |
| 100 | 11.200 | 13.100 | 15.000 | 16.900 | 18.700 | 22.500 |
| 125 | 14.100 | 16.400 | 18.700 | 21.100 | 23.400 | 28.100 |
| 140 | 15.700 | 18.400 | 21.000 | 23.600 | 26.200 | 31.500 |
| 155 | 17.400 | 20.300 | 23.200 | 26.100 | 29.000 | 34.800 |
| 170 | 19.100 | 22.300 | 25.500 | 28.700 | 31.800 | 38.200 |

LNST bền cơ sở **103–172** (giữa 134) [UL] = thuỷ điện 68–117 (DT 171 → 239; công thức `(DT×0,9−68,8)×0,8`) + tư vấn 30–50 + TC 5 — bản r1 ghi "125–155 = 75–110 + 30–50 + 5" **không tái lập** từ khối của nó (bỏ nhánh thiết kế). Bảng trên là lưới LNST × P/E tham chiếu; ô cơ sở: 103×3,5 = 13.500 … 172×4,5 = 29.000. LNST 2023/24/25: 75,6 / 92,0 / 150,2 [CB E].

### 8e. r4 — Định giá dựng lại theo giá PPA [`valuation_out.txt` khối "r4"] — ⚠️ MỨC BỊ THAY bởi §8f (r5); giữ để đối chiếu
**Hiệu chuẩn** [FY25 tr.34]: thuỷ điện 2025 Q 236,6 tr kWh, DT 261,60 gồm thuế TN 28,66 + phí DVMTR ~8,5 [UL 36 đ/kWh] = 37,2 pass-through ⇒ giá ròng **949 đ/kWh**; chi phí tiền mặt bộ phận 21,2; khấu hao 38,1. Hàm LNST thuỷ điện 2027+ = (Q×p − O&M 25 − KH 38 − chung 8) × 0,8 [UL].

| LNST thuỷ điện (tỷ) | Q 175 | Q 210 |
|---|---|---|
| (a) 975 | 79,7 | 107,0 |
| (b) 600 | 27,2 | 44,0 |
| (c) 500 | 13,2 | 27,2 |
| (d) 340 | −9,2 | 0,3 |
| 2025 thực (949; Q 236,6) | 122,7 | |

| LNST bền cả công ty (lo/mid/hi) | Pháp lý ổn (tư vấn 30/40/50) | Cấm thầu (tư vấn 10/15/20) |
|---|---|---|
| (a) | 110 / 133 / 157 | 90 / 108 / 127 |
| (b) | 57 / 76 / 94 | 37 / 51 / 64 |
| (c) | 43 / 60 / 77 | 23 / 35 / 47 |
| (d) | 21 / 36 / 50 | 1 / 11 / 20 |

**(i) P/E** — giá trị tại ~01/2028 = P/E × LNST bền, PV T=1,25 + cổ tức FY2026 (t≈0,9). P/E ổn 5/5,5/6, cấm thầu 3/3,5/4 [UL]. Đ/cp (lo/mid/hi):

| | Pháp lý ổn | Cấm thầu |
|---|---|---|
| (a) | 18.500 / 24.700 / 31.900 | 9.500 / 13.300 / 17.800 |
| (b) | 10.000 / 14.500 / 19.600 | 4.500 / 6.800 / 9.600 |
| (c) | 7.800 / 11.800 / 16.400 | 3.100 / 5.100 / 7.500 |
| (d) | 4.200 / 7.400 / 11.100 | 1.000 / 2.300 / 4.000 |
| **Kỳ vọng** (P giá 10/35/35/20; P pháp lý xấu 0,35) | **7.100 / 10.600 / 14.700** | |

**(ii) DDM / cổ tức phân phối được** — DPS₁ = FY2026 1.000–1.500; DPS₂…₁₀ = payout × LNST bền; VCSH₊₁ = VCSH + LNST × (1 − payout − 0,20 KTPL); terminal năm 10 = min(0,6; ROE/Ke) × VCSH [UL bảo thủ — thanh khoản thấp, thiểu số không quyết phân phối]. Mid (Ke 12,85%, VCSH 541):

| | payout 27% | 40% | 60% | cấm thầu 27/40% |
|---|---|---|---|---|
| (a) | 15.400 | 17.300 | 20.300 | 13.400 / 15.000 |
| (b) | 10.800 | 11.900 | 13.600 | 7.900 / 9.100 |
| (c) | 9.200 | 10.400 | 11.800 | 5.900 / 6.700 |
| (d) | 5.900 | 6.700 | 8.000 | 2.500 / 2.800 |
| **Kỳ vọng** (lo / mid / hi) | 6.200 / **8.700** / 11.100 | 7.000 / **9.700** / 12.400 | 8.200 / 11.200 / 14.200 | |

Ví dụ (c)/ổn/27%: PV cổ tức 3.940 + terminal 5.300 (P/B terminal 0,57).

**Cổ tức cần có vs cổ tức bền:** cần 2.435–2.650 đ/năm. Bền 2028+ (ổn, mid) payout 27/40/60%: (a) 1.350/2.000/3.000 · (b) 770/1.130/1.700 · (c) 610/900/1.350 · (d) 360/530/800. Payout cần: (a) 49% · (b) 86% · (c) 108% · (d) 183%.

**Vùng giá trị hợp lý** = [min(P/E mid, DDM27 mid); max(P/E mid, DDM40 mid)] = **8.700–10.600**, tâm (trung bình hai phương pháp) **9.900**. Payout 60% chỉ dùng làm điều kiện đổi nhận định (KH FY2026 của công ty là 10%, đi ngược chiều). Nhạy: xem §0.

**SOTP trần** (EV thuỷ điện 2027–2059, Q 192,5, giá có phần O&M 95 đ trượt 2,5%, capex 5, + tư vấn 40×6, + nợ ròng điều chỉnh −38,7; r 11–13%): (a) 42.300–47.800 · (b) 25.900–28.800 · (c) 21.600–23.700 · (d) 14.300–15.200; kỳ vọng r 12% ~24.900. Đối chiếu 13/10 (nợ ròng −117, Q 210, không tư vấn): (b) 19.600–23.500, (c) 14.500–17.600 — cùng vùng sau khi chỉnh nợ/sản lượng.

### 8f. r5 — Sửa định giá theo phản biện vòng 3 (THAY vùng §8e) [`valuation_out.txt` khối "r5"]
**Thay đổi so r4:** (B1) DDM: tiền ròng tích luỹ hưởng lãi 5% trước thuế, cộng theo mệnh giá ở năm 10; P/B ≤0,6 chỉ áp VCSH hoạt động (= VCSH − tiền ròng; giảm 33/năm theo KH − capex). (B2) P/E 6,5/6,75/7 (lo/mid/hi) cho LNST hoạt động sau hạ bậc, căn cứ trung vị P/E thuỷ điện niêm yết 2026 YTD 10,9 [BQ `calc/bq_hydro_peer_pe.csv`] trừ ~35–40%; cùng bội số cho cả hai trạng thái pháp lý. (N4) cấm thầu = tư vấn 10/15/20 + một lần 30 tỷ [UL]. (N1) P giá 10/45/35/10. (N5) P cấm thầu 0,30 (= R1 = 1 − M5); P mốc lùi 2 năm 0,15 có điều kiện hạ bậc ⇒ P(hạ bậc đúng 2027) = 0,90 × 0,85 ≈ **0,77 (R0 0,75)**, P(M0 tích cực) = 0,10 + 0,135 ≈ **0,24**. (N6) Q 175/205/210. (N7) P/E cộng tiền ròng cuối 2027 (tiền ròng đầu 2027 ≈ −63,5 tỷ). (N3) cổ tức FY2026 1.000/1.500/2.000.

| Đ/cp (mid, đúng mốc) | P/E 6,75 ổn | P/E cấm thầu | DDM27 ổn | DDM40 ổn | DDM40 cấm thầu | DDM60 ổn |
|---|---|---|---|---|---|---|
| (a) 975 | 35.100 | 28.000 | 21.700 | 22.800 | 19.400 | 24.400 |
| (b) 600 | 20.100 | 13.100 | 15.000 | 15.700 | 12.300 | 16.600 |
| (c) 500 | 16.200 | 9.100 | 13.200 | 13.700 | 10.300 | 14.500 |
| (d) 340 | 9.800 | 2.700 | 10.400 | 10.700 | 6.600 | 11.100 |

| Kỳ vọng | lo | mid | hi |
|---|---|---|---|
| (i) P/E | 11.600 | **17.600** (6,5: 17.000 · 7: 18.100) | 21.000 |
| (ii) DDM 27% | 10.500 | **13.900** | 16.200 |
| (ii) DDM 40% | 10.900 | **14.500** | 16.800 |
| (ii) DDM 60% | 11.500 | 15.300 | 17.800 |

**Vùng giá trị cân bằng** = [min(P/E 6,5; DDM27); max(P/E 7; DDM40)] (mid) = **13.900–18.100, tâm 15.900**; giá 19.800 cao hơn +9%…+42% (tâm +25%). Giá PPA ròng hoà vốn (P/E 6,75, ổn, Q205) ≈ **591 đ/kWh**. Phân rã B1, nhạy, tổ hợp ≥19.800, SOTP và chiết khấu tiếp cận ngầm định: §0 (cùng số, `valuation_out.txt`).

## 9. Thanh khoản [BQ, DNSE]
ADV20 đến 28/10: **0,72 tỷ/ngày** trung bình, **trung vị 0,41 tỷ** [BQ `calc/bq_px.csv`]; phiên 30/10 (sau công bố Q3 tối 29/10): 156.400 cp ≈ 3,1 tỷ, +4,8% [DNSE]. Biên độ UPCOM ±15%. Vị thế lớn hơn vài trăm triệu đồng/ngày sẽ là người tạo giá.

## 10. Mốc kiểm chứng (hai chiều; r5 — thống nhất xác suất với mô hình; P = ước lượng)
| # | Mốc | Ngày chấm | Chiều tích cực | Chiều tiêu cực | P(tích cực) |
|---|---|---|---|---|---|
| **M0** | **Văn bản giá PPA SB5 2027+** (CBTT, BCTN 2026, tài liệu ĐHĐCĐ 2027, thuyết minh BCTC kiểm toán 2026, hoặc doanh thu thuỷ điện Q1/2027 chia sản lượng) | sớm nhất BCTC kiểm toán 2026 (~03/2027) / ĐHĐCĐ (~04/2027) / BCTC Q1/2027 (~04/2027) | giá ròng ≥~600 đ/kWh (hoà vốn P/E ≈591), hoặc 500–600 là giá cố định chưa O&M, hoặc mốc lùi ≥2 năm | <~590 (≤500: dưới trung tâm; ~340: kịch bản (d)) | **0,24** [UL; = P(a) 0,10 + 0,90 × P(mốc lùi) 0,15 — khớp mô hình §8f; chưa tính khả năng (b) ở mép ≥600] |
| M1 | LNST HN Q4/2026 | ~30/01/2027 | ≥45 tỷ | <25 tỷ | 0,50 (còn giá cũ — **không** đổi định giá 2027+) |
| M2 | DT thuỷ điện Q4/2026 | ~30/01/2027 | ≥100 tỷ | <80 tỷ | 0,45 (giá cũ; chỉ ảnh hưởng tiền mặt cuối 2026) |
| M3 | Thuyết minh thu nhập khác 33,8 tỷ (kiểm toán 2026) | ~31/03/2027 | có căn cứ, giữ | bị đảo | 0,60 |
| M4 | Ý kiến kiểm toán FY2026 (An Việt) | ~31/03/2027 | chấp nhận toàn phần | ngoại trừ/từ chối/đổi kiểm toán | 0,65 |
| M5 | Vụ EVNNPT/PC1 | khi có kết luận/cáo trạng/quyết định cấm thầu | không cấm thầu, không buộc nộp | cấm thầu EVN 3–5 năm / buộc nộp lớn | 0,70 [UL; = 1 − P cấm thầu 0,30 trong mô hình] |
| M6 | Cổ tức FY2026 (ĐHĐCĐ 2027) | ~04/2027 | ≥2.000 đ hoặc cam kết payout ≥50% | <1.500 đ (dưới mức thực trả FY2025) | **0,35** [UL] (r4 0,20 bị phản biện là chọn lọc: KH FY2025 6% → thực 15%; KH LNST 2026 104,2 < 9T 124,6 ⇒ công ty đặt KH thấp; 2.000 đ ≈ payout 32% LNST FY2026 ~165) |
| M7 | Phải thu KH gộp (BCTC Q4) | ~30/01/2027 | ≤390 tỷ | >430 tỷ | 0,60 |
| M8 | Điện mặt trời lòng hồ SB5 | khi có quyết định chủ trương / quy hoạch | có chủ trương + giá bán/hợp đồng + vốn không pha loãng | đầu tư ~800 tỷ bằng vay/phát hành khi chưa có giá bán | 0,30 [UL] |
| M9 | Đọc ngành F8 (EVN tăng giá bán lẻ ≥1 lần đến 30/06/2027) | 30/06/2027 | YES | NO | 0,55 (người đọc ngành) |

**Ma trận rủi ro (r5):** R0 **giá PPA hạ bậc ≤600 đ/kWh đúng mốc 2027** — P **0,75** [UL = 0,90 × 0,85 = 0,77, khớp M0 0,24], tác động: LNST hoạt động bền −45…−57% so 2025 ((b)/(c) ổn), giá trị P/E (b)/(c) 16.200–20.100; R1 cấm thầu/buộc nộp — P **0,30** (= mô hình; r4 0,35 bị thống nhất); R6 (mới, N9) truy thu phần giá trả vượt biểu giá 2018 — quy mô ≈415 tỷ trước thuế, P thấp [UL, không lượng hoá; tiền lệ SB4A chỉ ký lại giá + xác định tiền lãi]; R2 kiểm toán ngoại trừ — P 0,35 (giữ); R3 tiền giữ lại bị dùng cho dự án chưa có giá bán — P 0,30 [UL]; R4 El Niño Q4/2026 — chỉ ảnh hưởng 2026.

## 11. Chấm dự báo khoá trước (CYCLE_BLOCK 26/10, md5 4409305ff745a26984325a532afda8af — đã kiểm `md5sum` khớp LOCK.txt)
| Dự báo | Gọi | p | Thực tế Q3/2026 | Kết quả | Brier |
|---|---|---|---|---|---|
| **F (chính)** biên gộp HN Q3 < 33,0% | CÓ | 0,65 | **38,93%** (65,443/168,095) [Q3 tr.6] | **SAI** | 0,4225 |
| F2 LNST HN Q3 < 32,1 tỷ | CÓ | 0,75 | **66,88** (lõi ~36,0 [UL] — vẫn >32,1) | **SAI** | 0,5625 |
| F3 DT Mua bán điện 9T − 81,20 < 41,6 | CÓ | 0,70 | BCTC Q3 **không** thuyết minh DT theo bên liên quan [Q3 tr.30 mục b trống] | **VOID** (đúng điều kiện void_if); proxy thuế TN ~41,2 (không chấm) | — |
| Pha "GIỮA-XUỐNG" biên gộp HN | | | Biên Q3 tăng 4,5 điểm % YoY | Sai ở Q3 | — |

**Vì sao sai (trung thực):** phần thuỷ điện của lập luận gần đúng (Q3 ≈ cùng kỳ, 9T −11,5% [UL]), nhưng **mảng tư vấn** tăng biên lên ~34% (dự báo dùng 26%) — đúng là kịch bản phản bác đã ghi trong CB ("tư vấn ít tăng / biên tư vấn >30%"), chỉ là nửa sau xảy ra. Mục "Chống" của CB (cầu tư vấn pha lên, biên tư vấn H1 cao hơn) đã đúng hơn mục "Ủng hộ". F2 sai thêm vì khoản khác 33,8 tỷ — nhưng kể cả bỏ nó, LN lõi vẫn vượt ngưỡng. Bài học: biên mảng tư vấn dao động mạnh theo quý (Q4/25 ~2%, Q3/26 ~34% [UL]) ⇒ dự báo biên HN quý có độ tin thấp; p 0,65–0,75 là **quá tự tin**.

## 12. Lệch nguồn BQ ↔ BCTC
- `ticker_financial` TV1 chưa có 2026Q3 (02/11); `Cash_P0` thiếu tiền gửi HTM (bẫy đã biết). Phải thu "~295" trong checklist là số BQ, khác khái niệm với phải thu KH gộp 387,5 của BCTC.
- BQ `ticker` giá đến 28/10; giá 30/10 lấy từ DNSE.

## Giới hạn
- BCTC Q3 chưa soát xét, scan; thuyết minh Q3 mỏng (không bộ phận, không bên liên quan, thu nhập khác không chi tiết). Mọi số tách mảng Q3 là **ước lượng proxy**.
- Chưa đọc: BCTC Q3 mẹ đầy đủ (chỉ trang 6, 24), CBTT room ngoại, BCTN 2025. Tin pháp lý đã tra 02/11 bằng WebSearch/WebFetch (không phải CBTT sàn); khung pháp lý là tra cứu tham khảo, cần luật sư xác nhận. Đã qua 2 vòng phản biện; bản r3 chưa qua vòng 3. Trọng số kịch bản là phán đoán [UL]. Cổ tức giả định 1.500 đ/năm trong PV [UL].
- **r4:** Giá PPA SB5 2027+ (mức, mốc) **không xác định** bằng văn bản; trọng số 4 kịch bản giá là phán đoán [UL] neo vào chứng cứ ở §4. BCTN 2025 không tải lại được 02/11 (dùng trích dẫn 13/10); báo cáo KBSV không đọc lại bản gốc. Điện mặt trời lòng hồ không định giá (chưa có số công bố đủ). r4 chưa qua phản biện.

## Nguồn
`src/` (BCTC gốc pecc1.com.vn, do Mike tải) · `src/ir/` (CBTT kiểm toán FY2026 CV 4958 19/08/2026; cổ tức CV 5744 23/09/2026; sáp nhập MTV3 TB 6177 12/10/2026; room ngoại — chưa đọc) · `calc/` (valuation.py/out, dnse_px.py/raw, bq_px.csv, bq_fin.csv, bq_pe_pb_yearly.csv, rate_lines.txt) · `img/` (ảnh trang đã đọc, zoom 1.6).

## Phụ lục A — dòng tiền/biến động chính (đọc ảnh)
| Khoản | Số | Nguồn |
|---|---|---|
| LNTT 9T / KH / dự phòng | 150,45 / 29,63 / (22,61) | Q3 tr.7 |
| Biến động phải thu / HTK / phải trả | +32,73 / +3,74 / (26,60) | Q3 tr.7 |
| Thuế TNDN đã nộp / chi khác HĐKD | (29,17) / (21,38) | Q3 tr.7 |
| CFO 9T | 116,85 (9T/25 137,56) | Q3 tr.7 |
| Gửi HTM / thu hồi | (218,63) / 105,92 | Q3 tr.7-8 |
| Vay thu / trả | 4,48 / (8,74) | Q3 tr.8 |
| Thuế tài nguyên phải nộp H1 / 9T | 8,776 / 13,227 | H1 tr.27; Q3 tr.23 |
| Chi phí theo yếu tố 9T: nhân công | 145,6 (9T/25 104,4, +40%) | Q3 tr.32 |


## Phụ lục E — Đính chính từ phản biện (vòng 2, 02/11/2026)
Đã kiểm lại trực tiếp trên `src/hn_h1_2026.pdf` (trang in 3, 4, 5, 8, 21, 30; PDF trang +1). Đồng ý 12/12; không có điểm bác bỏ. Tất cả phép tính: `calc/valuation.py` → `valuation_out.txt`.
| # | Điểm | Số cũ → số mới | Nguồn trang / cách xử lý |
|---|---|---|---|
| 1a | LCTT dòng 03 "dự phòng" H1 | −5,94 (Q2 chưa soát xét) → **−1,149**; hoàn nhập phi tiền Q3 −16,7 → **−21,5** | [H1 tr.8] ✓ đọc ảnh |
| 1b | CFO H1 / Q3 | 54,38 → **47,03**; CFO Q3 62,5 → **69,8** | [H1 tr.8 mã 20] ✓ |
| 1c | Mã 136 tại 30/6; giảm dự phòng Q3 | 107,73 → **105,08**; 27,5 → **24,9** (mã136 19,2 + HTK 5,7) | [H1 tr.5] ✓ |
| 2 | Dự phòng phải thu KH | "tăng 63,2→68,4" → **giảm 90,81 (30/6) → 68,36 (~−22)**; chênh 15,5 chủ yếu liên quan dự phòng trả trước người bán (9,49 tại 30/6); dòng "dự phòng giảm" chuyển từ cột Tích cực sang **CỜ** | [H1 tr.21 TM10] ✓ (KH 90.813.554.507; khác 4.776.868.427; trả trước 9.490.958.667) |
| 3 | Điều chỉnh VCSH +8,90 | "chưa giải" → khớp "Giảm khác" 8.901.255.944 trong TM10 (dự phòng ghi giảm thẳng vào vốn); vẫn là cờ | [H1 tr.21, tr.30] ✓ |
| 4 | "Thu nhập khác không có tiền" (mã 16) | bỏ lập luận mã 16; bằng chứng mới = LCTT dòng 03 ≈ −21,5 phi tiền; ~10 tỷ còn lại không xác định | §0, §3 |
| 5 | LNST lõi Q3 | 36–44 → **16–45** hai chiều; biên gộp bỏ hoàn nhập HTK 38,9% → **35,5%**; biên tư vấn ~34% → **~29,9%**; 9T lõi +7% → **−17%…+15%** | `valuation_out` §1b (tự dựng; cận trên 44,7 so skeptic 44) |
| 6 | P/E lõi | 3,24x (trừ thuế khoản khác) → **3,38x** (loại cả 31,9; LNST TTM lõi 156,6); khoảng **3,2–3,8x**; P/B 0,92 + **1,04 (VCSH soát xét 30/6)** | §8a |
| 7 | Kịch bản cơ sở | LNST 125–155 → **103–172** (thuỷ điện 68–117 + tư vấn 30–50 + 5); 16.400–26.100 → **13.500–29.000**; tâm ~21.000 → ~20.100; "nửa dưới vùng cơ sở" bỏ (giá nằm gần tâm); Tốt dựng lại 152–172 (28.500–38.700) | §0, §8d; hydro_fcf cho 68/89/117 ✓ |
| 8 | Chiết khấu thời gian | "giá thấp hơn kỳ vọng ~10%" (21.963 chưa CK) → EV chưa CK **21.600**; **PV 19.200–20.600** ⇒ giá **−4%…+3%** (≈ngang); kết luận §0 viết lại | `valuation_out` §6b; phương pháp = skeptic (DPS 1.500, Ke 12,3–13,4%) |
| 9 | Pháp lý | "pháp nhân TV1 chưa bị khởi tố (TM33)" → "chưa có thông tin khởi tố pháp nhân (suy từ không thấy)"; thêm đoạn nhấn mạnh (a) 127,63 tỷ nợ vay + lãi đang kiện; **danh sách 13 đơn vị BCA 02/07/2026 CÓ TV1**; không có tin mới sau 28/10 (WebSearch); BCTC Q3 mục 32 bỏ trống | [H1 tr.3, tr.4] ✓; doanhnghiephoinhap.vn 02/07/2026 |
| 10 | Cơ cấu phân phối LNST 2025 | thêm: cổ tức 40,04 (27%) · khen thưởng phúc lợi 30,1 (20%) · đầu tư phát triển 54,15 (36%) · còn lại 25,9 (17%) | [H1 tr.30] ✓ |
| 11 | DCF thuỷ điện khấu hao | 38/năm × 33 năm → 38 × 13 năm (TSCĐ 506,3/38); SOTP 24.300/44.700 → **23.900/44.200** | `valuation.py` hydro_pv; [H1 tr.5] ✓ |
| 12 | Phép kiểm proxy thuế TN FY2025 | thêm vào §4 (10,95% ổn định) — nhận từ phản biện, chưa tự tái lập | §4 |

**Hệ quả đọc lại cho nhà đầu tư (r2, đã bị r3 thay — xem E2):** Q3 66,9 tỷ KHÔNG nên đọc như xu hướng.
## Phụ lục E2 — Đính chính vòng 3 (phản biện vòng 2 REFUTED medium, `SKEPTIC2_20261102.md`; pháp lý `LEGAL_VN_20261102.md`)
Đồng ý 4/4 BLOCKING + 10/10 NON-BLOCKING (N8 bản đồ: đã ghi gần đúng, giữ). Phép tính: `calc/valuation.py` (khối "r3") → `valuation_out.txt`.
| # | Điểm | r2 → r3 | Nguồn / cách xử lý |
|---|---|---|---|
| B1 | Trọng số mâu thuẫn M4/M5/R1/R2 (0,35) vs P(Xấu) 25% | Xấu định nghĩa lại = ít nhất một sự kiện nặng (cấm thầu EVN 3–5 năm / kiểm toán ngoại trừ trọng yếu / buộc nộp lớn); bộ nhất quán **20/45/35**; kết luận = **dải** 25/50/25 (PV 19.300–20.600) ↔ 20/45/35 (18.200–19.400; VCSH soát xét 17.800–18.900) ⇒ **giá từ ngang đến cao hơn ~10%**; bỏ "không có căn cứ dữ liệu để nghiêng" | §0; [LV]; M5 0,65 → 0,70 (tích cực), R1 0,35 → 0,30 |
| B2 | Lõi Q3 trộn hai cách hạch toán | (A) vào QLDN: 16–45, QLDN gộp 40,7 (~3,9×), cả 31,9 không giải thích; (B) vào thu nhập khác: **31–45**, 9T 0…+15%, P/E 3,2–3,45x, ~16 không xác định; "một nửa là một lần" → "1/3 đến 3/4" (chỉ B mới ≈ một nửa) | §0, §3, §8a |
| B3 | Dự phòng phải thu KH đầu năm | 63,2 → **89,93** (16,75 + 73,18) [FY25 tr.21 TM6, đã render `img/fy25_p22.png`]; H1 đi ngang 89,9 → 90,8, Q3 −22; **cờ mới**: thuyết minh Q3 lệch 26,7 tỷ | §5, §7; fig_03 |
| B4 | Nguồn "13 đơn vị" | URL + trích nguyên văn VnExpress 02/07/2026; thêm "nhà thầu có sai phạm"; mâu thuẫn 13 công ty (VnExpress) vs 13 người (The Investor); bỏ doanhnghiephoinhap; khung pháp lý Điều 76/NĐ 214 Đ.133 | §7 |
| N1 | Cổ tức cần có | ≈2.800 → **2.435–2.650** (payout ~43–53%) | §8b |
| N2 | 30/50/20 | −12% chưa chiết khấu → PV **20.100–21.500**, giá −8%…−1% | §0 |
| N3 | Xấu trên VCSH soát xét | thêm **9.500–13.300** (tâm 11.400) | §0 |
| N4 | "min P/B 0,50" | bỏ; thấp nhất trong csv 0,57 (2021) | §0 |
| N5 | Nguồn Ke | ghi khung β≈1,1, β TV1 chưa đo, chưa bù thanh khoản; nhạy r\* 15,1% ⇒ PV 18.750–20.080 | §0, §8c |
| N6 | PV T=1,5 | cộng cổ tức tích luỹ phần lẻ năm: 19.200–19.500 → 19.800–20.100 | `pv_scn` |
| N7 | Ảnh thuỷ điện | chú thích "không phải tài sản của công ty" | báo cáo NĐT fig_10 |
| N9 | "Vùng giá trị hợp lý" | định nghĩa = min–max PV trên 2 bộ trọng số × T 1–2 × Ke × 2 cơ sở VCSH = 17.800–20.600 | §0 |
| N10 | "Ba điều cần biết" lệch một chiều | thêm tiền ròng điều chỉnh −39 và 127,6 tỷ vay + lãi đang kiện | báo cáo NĐT |

## Phụ lục E3 — Vòng 4: dựng lại định giá (user phê bình phương pháp 02/11/2026 16:42; job `Taylor_20261102_094407`)
**Phê bình (nguyên văn):** "Nếu cổ tức 2.435-2.650 để biện minh giá hiện tại thì tôi nghĩ có vấn đề về định giá ở hiện tại. TV1 chủ yếu có vấn đề về giá điện phải tái ký lại, chưa xác định giá nên mảng thủy điện không rõ ràng lợi nhuận cao. Còn lại nếu giữ nguyên giá như 2026 thì không có giá này."

**Ghi nhận lỗi (không phải sửa số lẻ):**
1. **Bỏ quên nghiên cứu có sẵn.** Nghiên cứu giá PPA SB5 của chính nhóm ngày 13/10/2026 (`../tv1_sb5_ppa_price_20261013/`: văn bản PECC1 2018 bậc 569,36 → 243,66; BCTN 2025 tr.38 "giá điện… sụt giảm"; KBSV 17/04/2026 lời lãnh đạo 500–600 từ 2027; SOTP theo giá đã kết luận "biên an toàn không còn") **không được đọc** ở r1–r3. r1–r3 viết checklist (4) "không có dấu hiệu nào theo cả hai chiều" — sai (§4 đã đính chính).
2. **Giả định giá điện sai trục.** LNST bền 103–172 và SOTP 23.900/44.200 dựng trên DT thuỷ điện 171–239 tỷ ở giá ~912–950 đ/kWh, "chỉ −20% từ 2034" [UL] — mâu thuẫn trực tiếp với chứng cứ trên. Ở 500–600, LNST bền (pháp lý ổn) chỉ **60–76 tỷ**.
3. **Phép thử cổ tức bị để làm chú thích.** r3 tính "cổ tức cần có 2.435–2.650 (payout 43–53%)" so thực trả 1.500 (27%) nhưng kết luận vẫn theo P/E × LNST (giá cũ) ⇒ không nhất quán nội bộ. r4 đưa DDM thành phương pháp **đồng hạng** và vùng giá trị = hợp của hai phương pháp.
4. **TC ròng +5 tỷ/năm** trong LNST bền r3 là lạc quan (9T/26 −1,3) ⇒ r4 dùng 0.

**r3 → r4:**
| Mục | r3 | r4 |
|---|---|---|
| Vùng giá trị hợp lý | 17.800–20.600 (giá ngang…+11%) | **8.700–10.600, tâm 9.900 (giá +86%…+129%)** |
| Trục kịch bản | pháp lý Tốt/Cơ sở/Xấu, giá điện cũ | **giá PPA (a) 975 / (b) 600 / (c) 500 / (d) 340, P 10/35/35/20** × pháp lý ổn/cấm thầu (0,65/0,35) |
| LNST bền | 103–172 (giữa 134) | (b) 76, (c) 60 pháp lý ổn; kỳ vọng thấp hơn |
| Phương pháp | P/E (chính) + PV; cổ tức là chú thích | P/E và DDM đồng hạng; SOTP = trần |
| Checklist (4) | "không có dấu hiệu" | dấu hiệu tiêu cực rõ, mức/mốc chưa có văn bản |
| M6 P(cổ tức ≥2.000) | 0,40 | 0,20 (KH FY2026 10%) |
| Rủi ro mới | — | **M0/R0 giá PPA tái ký**, M8/R3 điện mặt trời lòng hồ |

**Nguồn mới tra 02/11/2026:** BCTC HN 2025 kiểm toán tr.32–36 (báo cáo bộ phận; không có biểu giá); baodauthau.vn 30/04/2026 (ĐHĐCĐ 2026: KH LNST 104,2, cổ tức KH 10%, điện mặt trời 46 MWp/~800 tỷ vướng thủ tục); baodauthau.vn 27/06/2025 (kỳ vọng ~90 tỷ DT/năm điện mặt trời). Không tìm được văn bản PPA mới, CBTT giá, KBSV/VCBS gốc; BCTN 2025 tải lỗi (lỗi chứng chỉ owa.hnx.vn) — dùng trích dẫn 13/10.

**Không điều chỉnh để ra kết quả:** các nhạy ở §0 (bỏ rủi ro pháp lý, trọng số giá rất lạc quan, P/E 7, hạ bậc trễ 2 năm) đều cho ≤16.400 đ; chỉ kịch bản (a) giữ giá mới đưa giá trị lên vùng giá hiện tại. Kết luận r3 nguyên văn: xem commit `465fedbc1` (REPORT.md §0).

## Phụ lục E4 — Vòng 5: áp phản biện vòng 3 (`SKEPTIC3_20261102.md`, REFUTED medium; job `Taylor_20261102_100630`)
Nguyên tắc: user phê bình PHƯƠNG PHÁP (02/11 16:42), không chỉ định kết quả; skeptic xác nhận HƯỚNG nhưng chỉ ra MỨC r4 dựng từ chồng giả định cùng nghiêng một phía. r5 sửa mọi điểm trong một lần, sửa CẢ hai chiều (vài sửa kéo giá trị lên — B1, B2, N1, N3, N4, N6, mốc lùi; vài sửa kéo xuống — N7 tiền ròng −38,7 + KTPL, khoản một lần 30 tỷ, N9 đuôi truy thu nêu riêng). Vùng r5 (13.900–18.100) nằm trong dải skeptic dựng lại (~11.800–15.000 cân; ~14.800–17.300 lạc quan) ở nửa trên, do r5 thêm mốc lùi (P 0,15), Q 205 và tiền Q4/2026 — mỗi thứ có nhạy riêng ở §0.

| # | Phản biện | Đã làm | Ở đâu |
|---|---|---|---|
| B1 | DDM định giá tiền tích luỹ < mệnh giá, tiền không sinh lãi | Tiền ròng hưởng lãi 5% trước thuế (nhạy 0/3/6,5%), cộng theo mệnh giá ở năm 10; P/B ≤0,6 chỉ áp VCSH hoạt động. (c)/ổn/27%: 9.200 → 13.200. Viết lại "Vì sao DDM thấp hơn P/E" | §0, §8f, `valuation.py` `ddm5()` |
| B2 | P/E 5–6 phạt kép rủi ro PPA | P/E 6,5–7 căn cứ trung vị thuỷ điện niêm yết 2026 YTD 10,9 [BQ] trừ 35–40%; nhạy 5,5–9; §8c đánh dấu bị thay | §0, §8c, §8f, `calc/bq_hydro_peer_pe.csv` |
| B3 | "Không tổ hợp nào đạt 19.800" bị SOTP bác | Giới hạn câu vào P/E/DDM thiểu số; liệt kê tổ hợp đạt (a; b ổn P/E 7; b/c ổn + mốc lùi); nêu chiết khấu tiếp cận ngầm định 39–43% vs thông lệ 20–40%; giá = SOTP trộn × 0,76; bỏ "gấp đôi" | §0 |
| N1 | P(d) 0,20 nặng | 0,10 (chuyển sang b: 0,45) | §0, §8f |
| N2 | 500–600 là giá TỔNG hay giá cố định? | **CHƯA KIỂM được**: KBSV 17/04/2026 chỉ thấy trong danh mục simplize.vn ("Báo cáo cơ hội đầu tư", MUA, 42.400), không tải được bản gốc; không tìm thấy SSI/BSC/MBS/VND nêu mức. Một tóm tắt tìm kiếm (file trên bsc.com.vn, liên kết về vcbs — nghi VCBS; CHỈ snippet) ghi DT điện 2026–30 ~160 tỷ/năm (−31%), LN gộp ~70 tỷ (−51%) ⇒ quy ra ≈590 đ/kWh ròng [UL]. Đã thêm nhạy: nếu là giá cố định ⇒ ròng 595–695 ⇒ P/E 22.100–23.900. BCTN 2025 tr.38 vẫn **chưa kiểm** lại (owa.hnx.vn lỗi chứng chỉ; không thấy bản trên pecc1/vietstock/cafef qua tìm kiếm) — trích dẫn dựa trên đọc ngày 13/10 | §0, Nguồn |
| N3 | M6 0,20 chọn lọc | M6 0,35; cổ tức FY2026 1.000/1.500/2.000; điều kiện tiêu cực (5) so với mức thực trả 1.500 | §0, §10 |
| N4 | Phạt pháp lý hai lần | Cùng P/E; cấm thầu = tư vấn 10/15/20 + một lần 30 tỷ [UL] | §0, §8f |
| N5 | Bất nhất xác suất | P cấm thầu 0,30 = R1 = 1 − M5; mốc lùi 0,15 ⇒ R0 0,75 / M0 0,24 khớp mô hình | §8f, §10 |
| N6 | Q 192,5 thấp | Q giữa 205 (bình quân năm có số 2015–2025 = 207,3); nhạy 175/190/236,6 | §0 |
| N7 | Bỏ sót LN 2026 và tiền ròng −38,7 | P/E cộng tiền ròng cuối 2027; tách +1.800 / −1.450 / −2.700 đ/cp | §0 |
| N8 | Tin 27/3/2026 giá 1.351,7 tỷ; lịch sử đấu giá lệch | Kiểm: **1.351,7 tỷ là lần 5, thông báo 17/05/2021** (đấu 14/6/2021), KHÔNG phải 2026 (ghi nhầm trong `peer_hydro_prices.md` 13/10 từ tóm tắt tìm kiếm). Thống nhất: 01/2019 1.688 → 11/2020 (lần 4) 1.390 → 05/2021 (lần 5) 1.351,7; đều không có người đăng ký (baodauthau.vn post106802). Không tìm thấy thông báo bán 2026 | §0, §8b |
| N9 | Rủi ro truy thu biểu giá 2018 | Quy mô ≈415 tỷ trước thuế (2022/23/25); tiền lệ SB4A (Thanh tra Chính phủ, ký lại 1.110 đ/kWh 7/2022, yêu cầu xác định tiền lãi; chưa xác nhận hồi tố — vnbusiness.vn); R6, điều kiện tiêu cực (6) | §0, §10 |
| N10 | Nhãn dòng nhạy "rất lạc quan" | Ghi rõ "lạc quan (25/45/25/5) + P xấu 0" là tổ hợp cả hai | §0 |
| N11 | Câu cũ còn sót | §8b câu payout 43–53% và "5 lần 2017–18" gạch + ghi bị thay; §8c đánh dấu; §8e đánh dấu mức bị thay; §0 r4 xoá hẳn | §8 |
| N12 | State file TV1 | Ghi ở mục nội bộ dưới — KHÔNG sửa file | dưới |

**r4 → r5:** vùng 8.700–10.600 (tâm 9.900, giá +86…+129%) → **13.900–18.100 (tâm 15.900, giá +9…+42%, tâm +25%)**. HƯỚNG giữ (giá > kỳ vọng P/E/DDM); MỨC giảm từ "gấp đôi" xuống "cao hơn ~1/4 so tâm".

## Nội bộ — việc USER quyết (N12; KHÔNG đưa vào báo cáo NĐT; KHÔNG sửa file)
`data/trade_plans/discretionary/state_TV1_{SpaceX,ZaloPay}.json` (đọc 02/11/2026, mtime 19/10): `status=paused` (từ 19/10); vẫn ghi `thesis_source = mike/agents/Taylor/research/tv1_pecc1_sotp_20260723.md` (SOTP 23/07 — luận điểm đã bị nghiên cứu 13/10 và DD này thay); `price_band.floor_note` "downside che bởi tài sản hydro" (không còn đúng: tài sản hydro chỉ che nếu bán được, ≥5 lần đấu giá thất bại); `target_pct_active_nav = 0.05` (vượt trần sleeve discretionary 2–4% theo phản biện); `hard_expiry.conditions` không có điều kiện M0 (văn bản giá PPA ròng ≤600 / dưới hoà vốn ~590). Nếu user mở lại chương trình: cập nhật thesis_source → REPORT này, bỏ floor_note, hạ target, thêm điều kiện dừng M0; `max_no_chase_ceiling` 25.000 cao hơn vùng r5 (trần 18.100). Việc của user; Taylor không đổi.
