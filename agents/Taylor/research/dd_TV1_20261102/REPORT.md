# DD — TV1 (CTCP Tư vấn Xây dựng Điện 1 / EVNPECC1, UPCOM) sau BCTC Q3/2026 · as-of 02/11/2026 · job `Taylor_20261102_035322` · VÒNG 2 (job `Taylor_20261102_042353`) · **VÒNG 3 (job `Taylor_20261102_075340`) — đã áp 4 BLOCKING + 10 NON-BLOCKING của phản biện vòng 2, xem Phụ lục E2**

> NGHIÊN CỨU READ-ONLY. Không khuyến nghị, không lệnh, không wire. User đang/đã giao dịch TV1 ngoài book V2.4 ⇒ "giữ/thêm/giảm" là quyết định của user; báo cáo chỉ đưa vùng giá + điều kiện đổi nhận định. Vòng 1 bị fundamental-skeptic phản biện REFUTED (mức văn bản/số liệu); vòng 2 áp 12 đính chính (Phụ lục E); vòng 2 bị phản biện REFUTED (medium) với 4 BLOCKING — bản này là vòng 3, đã áp toàn bộ (Phụ lục E2). **Đã qua 2 vòng phản biện; bản r3 CHƯA qua vòng 3.**
> **Nguồn:** [Q3 tr.X] = trang PDF `src/hn_q3_2026.pdf` (BCTC HN Q3/2026, ký 29/10/2026, **chưa soát xét**, bản scan) · [ME tr.X] `src/me_q3_2026.pdf` (BCTC tổng hợp/công ty mẹ) · [GT] `src/giaitrinh_hn_q3_2026.pdf` (CV 6603/TVĐ1-P3) · [H1 tr.X] = số trang **in** của `src/hn_h1_2026.pdf` (soát xét An Việt) · [Q2 tr.1] `src/hn_q2_2026.pdf` · [FY25 tr.X] = số trang in của `src/hn_fy2025_audited.pdf` (BCTC HN 2025 kiểm toán A&C) · [LV] `LEGAL_VN_20261102.md` (tra cứu pháp lý, tham khảo — cần luật sư xác nhận) · [IR] CBTT tải từ pecc1.com.vn vào `src/ir/` · [CB] `../dd_blind2_TV1_20261026/CYCLE_BLOCK.md` (khoá md5 4409305f…, 26/10) · [BQ] `tav2_bq` (lịch sử; chưa có dòng 2026Q3 của TV1 tại 02/11) · [DNSE] `calc/dnse_raw.json` (lấy 02/11/2026 ~10:50 ICT).
> Phép tính: `calc/valuation.py` → `calc/valuation_out.txt` (tái lập: `python3 -I calc/valuation.py`). Số tự đặt gắn **[UL]** (ước lượng). Ngành: `kb/data_registry/market-state/sector_read_power_consulting_20261028.md` (Bobby, đọc mù).

## 0. Kết luận

**Giá 19.800 đ (đóng cửa 30/10/2026 [DNSE], vốn hoá 528,5 tỷ) từ NGANG đến CAO HƠN giá trị kỳ vọng đã chiết khấu ~10%: vùng giá trị hợp lý 17.800–20.600 đ/cp** [UL; `valuation_out.txt` khối "r3"]. **Định nghĩa vùng:** PV hôm nay của giá trị kỳ vọng 3 kịch bản, lấy min–max trên hai bộ trọng số (25/50/25 và bộ **nhất quán 20/45/35**), kỳ hạn T = 1–2 năm, Ke 12,3–13,4%, cộng cổ tức 1.500 đ/năm, kịch bản Xấu trên VCSH Q3 hoặc VCSH soát xét. Hai đầu: **25/50/25 ⇒ PV 19.300–20.600 (giá −4%…+3%, ≈ngang)**; **20/45/35 ⇒ PV 18.200–19.400 (VCSH Q3) / 17.800–18.900 (VCSH soát xét) ⇒ giá cao hơn +2%…+11%**. Bộ 20/45/35 là bộ **nhất quán** với xác suất tiêu cực ~0,35 của M4/M5 và R1/R2 (lý do: §0 "Trọng số"); 25/50/25 giữ làm đầu lạc quan. **Không có biên an toàn định lượng.** Giá trị **tài sản** (SOTP: thuỷ điện Sông Bung 5 DCF có thời hạn + tư vấn − nợ) cao hơn nhiều — thấp 23.900 / giữa 44.200 đ/cp — nhưng cổ đông thiểu số **không tiếp cận được** giá trị đó trừ khi có bán tài sản hoặc nâng cổ tức (payout 2025 chỉ 27%, quỹ khen thưởng–phúc lợi 20% + quỹ đầu tư phát triển 36% giữ lại trong công ty [H1 tr.30]; SB5 từng đấu giá 5 lần không bán được) ⇒ dùng làm trần tham chiếu, KHÔNG làm neo kỳ vọng.

**Q3 đẹp trên bề mặt, nhưng 1/3 đến 3/4 lãi quý không lặp lại hoặc chưa giải thích:** LNST Q3 **66,9 tỷ (+150% YoY)** [Q3 tr.6; GT], trong đó **thu nhập khác 33,8 tỷ** ghi "các khoản khác", **không thuyết minh bản chất** [Q3 tr.32]. Bằng chứng phi tiền: LCTT dòng 03 "các khoản dự phòng" 9T −22,61 so H1 **soát xét** −1,15 ⇒ **−21,5 phi tiền trong Q3** [Q3 tr.7; H1 tr.8]; dự phòng bảng cân đối giảm 24,9 (phải thu mã 136: 19,2; HTK: 5,7). Hoàn nhập phải thu 19,2 đi vào dòng nào thì **chưa biết** — hai trường hợp **loại trừ nhau**, không trộn: **(A) vào QLDN** (VAS thông thường): lõi Q3 **16–45**, khi đó QLDN gộp trước hoàn nhập Q3 ≈ **40,7 tỷ = ~3,9× bình quân quý H1 (10,5)** và **cả 31,9** khác ròng không giải thích được; 9T lõi −17%…+15%. **(B) vào thu nhập khác:** lõi Q3 **31–45**, 9T lõi **0%…+15%**, còn **~16** tỷ khác ròng không xác định. Nghiêng A: H1 TM28 ghi trích dự phòng phải thu ròng 0,88 vào QLDN. Nghiêng B: TM VI.9c Q3 trống; QLDN gộp 40,7 khó tin. Phần không lặp lại/chưa giải thích của LNST Q3: **22–51 tỷ (33–76%)** ở A, **22–35 (33–53%)** ở B ⇒ "khoảng một nửa là một lần" chỉ đúng ở B; nói chung là **1/3 đến 3/4** [UL]. Không phải "+44%" lõi.

| | Tích cực (có chứng cứ) | Tiêu cực (có chứng cứ) |
|---|---|---|
| Lợi nhuận lõi | Biên gộp Q3 **38,9%** báo cáo; **35,5% nếu bỏ hoàn nhập dự phòng HTK 5,7** (Q3/25 34,4%) [Q3 tr.6; `valuation_out`] | QLDN Q3 **21,5 tỷ, gấp đôi** (10,6); 9T +54% [Q3 tr.6] — chưa thuyết minh; nếu hoàn nhập phải thu 19,2 đã làm giảm QLDN (trường hợp A) thì QLDN gộp ≈40,7 (~3,9× bình quân quý H1) và lõi thấp hơn |
| Tư vấn | DT tư vấn Q3 ~126,9 (+18%) [UL proxy] — khớp đọc ngành "upcycle khối lượng" | Biên gộp tư vấn Q3 ~34% theo báo cáo, **~29,9% nếu bỏ hoàn nhập HTK** [UL]; phụ thuộc proxy thuế tài nguyên; Q3 không có thuyết minh bộ phận |
| Thuỷ điện | Q3 ~41,2 tỷ DT ≈ cùng kỳ (~41,6) [UL proxy] | 9T ~122,4 (**−11,5%**); Q4 (47% DT năm 2025) đối mặt El Niño mạnh (ONI +2,16) [CB B] |
| Một lần | — | ⚠️ **CỜ:** dự phòng giảm **24,9 tỷ** trong Q3 (mã 136: 105,1 [H1 soát xét tr.5] → 85,9; HTK 59,3 → 53,6) — hoàn nhập mà bên soát xét còn giữ ở 30/6, đi vào quý **chưa soát xét**. Thu nhập khác 33,8 tỷ **không giải thích**; thuế hiệu dụng Q3 13,1% gợi ý một phần không chịu thuế — **coi là một lần** |
| Tiền | Tiền + HTM **198,5 tỷ** (đầu năm 93,0) [Q3 tr.1]; CFO 9T 116,8 = 0,94× LNST; Q3 CFO ≈ **69,8** (9T − H1 soát xét 47,0) [Q3 tr.7; H1 tr.8] | Vay 129,9 tỷ (118,8 từ "bên liên quan" — cá nhân) + lãi vay cá nhân phải trả 64,3 (30/6) + cổ tức 43,2 (đã trả 29/10) ⇒ net điều chỉnh **≈ −39 tỷ** |
| Phải thu | Phải thu KH gộp 387,5 **giảm** so đầu năm (408,2) [Q3 tr.12]; dự phòng phải thu KH **giảm** ~22 tỷ trong Q3 (90,8 tại 30/6 → 68,4) | Giảm dự phòng KH này là phần lớn của hoàn nhập Q3 (xem cờ ở trên) — phải thu gộp không giảm tương ứng ⇒ **không phải xoá sổ nợ**; còn ~15 tỷ chênh dự phòng mã 136 (85,9) vs thuyết minh KH+khác (70,5), chưa giải (tại 30/6 phần "trả trước người bán" 9,5 nằm trong mã 136 [H1 tr.21]) |
| Định giá | P/E TTM 2,8x (**lõi 3,2–3,8x** ở A, **3,2–3,45x** ở B; bỏ cả khoản khác 31,9 ⇒ 3,4x), P/B **0,92 (VCSH Q3 chưa soát xét, có khoản một lần); 1,04 theo VCSH soát xét 30/6 507,8**, cổ tức 1.500 đ = **7,6%** [IR; `valuation_out`] | Trung vị P/E 2025 (trước vụ án) 6,0x, P/B 1,53 [BQ] — chiết khấu hiện tại là **giá của rủi ro pháp lý**, không phải sai giá thuần |
| Kiểm toán | **Đã có kiểm toán FY2026: An Việt** (HĐ ký 18/08/2026) [IR CBTT 4958]; soát xét H1: kết luận chấp nhận, đoạn nhấn mạnh vụ án [H1 tr.4] | Big4 từ chối trước đó; An Việt là hãng nội địa nhỏ — chất lượng bảo đảm thấp hơn |
| Pháp lý | Theo BLHS hiện hành, pháp nhân thương mại **không** bị truy cứu hình sự về 5 tội danh của vụ án (Điều 76 không liệt kê Đ.221, 222, 353, 354, 364) [LV — tham khảo, cần luật sư xác nhận] | ⚠️ Chủ tịch HĐQT + phó phòng TCKT bị khởi tố, tạm giam 07/05/2026 (đấu thầu, **kế toán**, tham ô) [H1 tr.38]; VnExpress 02/07/2026: CTCP Tư vấn XD điện 1 thuộc "13 công ty bị xác định có liên quan", "EVNNPT và nhà thầu đều có sai phạm" (§7); kênh rủi ro thực tế: **cấm thầu 3–5 năm, buộc nộp lợi bất chính/bồi thường, đứt gãy quản trị** |

**3 kịch bản (giá trị/cp cho cổ đông thiểu số, tại ~2027–28, CHƯA chiết khấu; LNST bền dựng từ khối — `valuation_out.txt` [UL]):**

| Kịch bản | P | Giả định | Phép tính | Giá trị/cp |
|---|---|---|---|---|
| Tốt | 25% (nhất quán: 20%) | Vụ án khép lại không có cấm thầu/buộc nộp; FY2026 kiểm toán sạch; thuỷ điện về mức TB 2024–25 (DT 239 ⇒ LNST 117); thị trường trả lại P/E ~ 2025 | LNST bền = 117 + tư vấn 30–50 + TC 5 = **152–172** × P/E 5–6 | **28.500–38.700** (tâm ~33.400) |
| Cơ sở | 50% (nhất quán: 45%) | Overhang kéo dài 1–2 năm; thuỷ điện từ thiết kế (DT 171 ⇒ LNST 68) đến TB (DT 239 ⇒ 117), giữa DT 200 ⇒ 89; tư vấn 30–50 | LNST bền = thuỷ điện 68–117 + tư vấn 30–50 + TC 5 = **103–172** (giữa 134) × P/E 3,5–4,5 | **13.500–29.000** (tâm ~20.100) |
| Xấu | 25% (nhất quán: **35%**) | Ít nhất một sự kiện nặng: **cấm thầu EVN/EVNNPT 3–5 năm** (NĐ 214/2025 Đ.133) và/hoặc **kiểm toán FY2026 ngoại trừ trọng yếu** và/hoặc **buộc nộp lợi bất chính/bồi thường lớn**; El Niño cắt thuỷ điện làm nặng thêm | P/B 0,5–0,7 (P/B thấp nhất theo dữ liệu năm 2019–26 là 0,57 năm 2021; trung vị 2019–21 0,76–1,14 [BQ `calc/bq_pe_pb_yearly.csv`]) | **10.800–15.100** (tâm ~12.900) trên VCSH Q3 574,7; **9.500–13.300** (tâm ~11.400) trên VCSH soát xét 507,8 |

**Trọng số (r3 — sửa mâu thuẫn vòng 2):** bản r2 dùng P(Xấu)=25% trong khi chính báo cáo đặt P(tiêu cực) = 0,35 cho M4 (kiểm toán) và M5 (vụ án), là điều kiện của kịch bản Xấu — mâu thuẫn; câu "không có căn cứ dữ liệu để nghiêng" đã bỏ. Sửa: (1) theo tra cứu pháp lý [LV], "khởi tố pháp nhân" gần như không xảy ra theo luật hiện hành (Điều 76 BLHS không gồm 5 tội; dự thảo BLHS hiệu lực dự kiến 03/2027 không hồi tố) ⇒ M5/R1 viết lại thành **cấm thầu EVN 3–5 năm / buộc nộp lợi bất chính**, P(tiêu cực) **0,30** [UL]; M4 giữ 0,35 (gồm cả "đổi kiểm toán", mức nhẹ). (2) Xấu = **ít nhất một** sự kiện nặng; M4 và M5 cùng gốc (tội danh kế toán + đấu thầu, cùng kết luận điều tra) nên tương quan cao ⇒ hợp của hai ≈ **0,35** [UL] ⇒ bộ **nhất quán 20/45/35**. Giá trị kỳ vọng **chưa chiết khấu**: 25/50/25 ⇒ ~21.600; 20/45/35 ⇒ ~20.200 (VCSH soát xét ⇒ 19.700). **Mọi so sánh với giá dùng PV đã chiết khấu** (dưới) — bản r2 so 30/50/20 với số chưa chiết khấu (−12%) là sai: sau chiết khấu 30/50/20 ⇒ PV 20.100–21.500, giá −8%…−1%. Độ nhạy khác (PV): 15/50/35 ⇒ 17.300–18.800 (giá +5,5%…+14,5%); P/E ±15% (chưa chiết khấu, 25/50/25) ⇒ 18.900–24.400.

**Chiết khấu thời gian** (giá trị kịch bản là giá tại T năm tới; người giữ nhận cổ tức 1.500 đ/năm [UL, mức 2025, nhận tại t=1,2…≤T, **r3: cộng phần cổ tức tích luỹ của năm lẻ** nên T=1,5 không còn thấp giả]; Ke 12,3–13,4%): **25/50/25 ⇒ PV 19.300–20.600** (T=1: 20.400–20.600 · T=1,5: 19.800–20.100 · T=2: 19.300–19.700) ⇒ giá **−4%…+3%**; **20/45/35 ⇒ PV 18.200–19.400** (giá **+2%…+9%**); trên VCSH soát xét **17.800–18.900** (+5%…+11%). **Nguồn dải Ke 12,3–13,4%:** khung chi phí vốn nội địa của nhóm cho β≈1,1 (rf chuẩn hoá ~6,75% + ERP nội địa) — **β của TV1 chưa đo, chưa cộng phần bù thanh khoản** (trung vị 0,41 tỷ/phiên); độ nhạy Ke = r\* thị trường 15,1%: PV 25/50/25 = **18.750–20.080** (giá −1%…+6%), 20/45/35 = 17.700–18.900 (+5%…+12%).

**Thị trường đang định giá gì:** ở 19.800, P/E 4,0 ngầm định LNST bền ~132 tỷ — **trùng giữa vùng cơ sở (134)**; P/E 3,5 ⇒ ~151. Tức thị trường đã chấp nhận LN quanh mức 2025 nhưng áp bội số ~1/2 thời trước vụ án. Biến quyết định không phải LN quý mà là **kết luận vụ án + ý kiến kiểm toán FY2026**.

**Điều làm nhận định TÍCH CỰC hơn:** (1) Kiểm toán FY2026 (An Việt) chấp nhận toàn phần, không ngoại trừ (~03/2027); (2) kết luận điều tra/cáo trạng không có quyết định cấm thầu hay buộc TV1 nộp lợi bất chính; (3) Q4/2026 thuỷ điện ≥100 tỷ DT dù El Niño; (4) ĐHĐCĐ 2027 nâng cổ tức ≥2.000 đ (payout ≥35%) hoặc tái khởi động bán SB5 có giá ≥1.000 tỷ; (5) thuyết minh rõ khoản thu nhập khác 33,8 tỷ và hoàn nhập dự phòng 24,9 tỷ trong Q3 (BCTC soát xét/kiểm toán không đảo). **Điều làm TIÊU CỰC hơn:** (1) quyết định cấm dự thầu (EVN/EVNNPT hoặc rộng hơn) với pháp nhân TV1, hoặc buộc nộp lợi bất chính/bồi thường lớn; (2) kiểm toán FY2026 ngoại trừ/từ chối, hoặc đổi kiểm toán lần nữa; (3) khoản 33,8 tỷ bị đảo ngược ở BCTC kiểm toán; (4) Q4/2026 thuỷ điện <80 tỷ DT (El Niño); (5) phải thu KH gộp >430 tỷ hoặc dự phòng tăng mạnh; (6) phán quyết vụ Lê Phi Long bất lợi vượt sổ (gốc 64,4 + lãi 42,1 đã ghi).

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
- **Checklist (4) — giá điện 2027 / PPA SB5**: BCTC Q3 **không** có thông tin (không có thuyết minh bộ phận, không có thuyết minh hợp đồng). Không có dấu hiệu nào, theo cả hai chiều.

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

Rủi ro PPA (ngày hết hạn chưa xác định; giả định −20% DT từ 2034 [UL]): DT200 r12% ⇒ 876; DT171 r13% ⇒ 676. SOTP thấp = 676 + tư vấn 0 − 38,7 = **637 tỷ = 23.900 đ/cp** (r1: 24.300); giữa = 979 + tư vấn 40×6 − 38,7 = **1.180 tỷ = 44.200 đ/cp** (r1: 44.700). Đối chiếu: SB5 rao bán 2017–18 giá khởi điểm 1.688 → 1.390 tỷ (gồm nợ), **5 lần không bán được** [SOTP 23/07].

**Vì sao không dùng SOTP làm kỳ vọng:** cổ đông thiểu số nhận giá trị qua **cổ tức** (payout 27%) hoặc **bán tài sản** (tiền sử thất bại). Phép thử dòng cổ tức (g=0, Ke 12,3–13,4%): DPS 1.500 ⇒ 11.200–12.200; 2.000 ⇒ 14.900–16.300; 2.800 ⇒ 20.900–22.800 đ/cp (cao hơn giá). **Cổ tức cần có để biện minh giá 19.800 = 19.800 × Ke = 2.435–2.650 đ/năm** (65–71 tỷ ⇒ payout ~43% LNST 2025 150,2 … ~53% LNST bền cơ sở 134). Giá 19.800 ≈ thị trường kỳ vọng payout tăng lên ~43–53% hoặc giá trị giữ lại không bị rò rỉ.

### 8c. Chi phí vốn, DCF vô hạn
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

## 9. Thanh khoản [BQ, DNSE]
ADV20 đến 28/10: **0,72 tỷ/ngày** trung bình, **trung vị 0,41 tỷ** [BQ `calc/bq_px.csv`]; phiên 30/10 (sau công bố Q3 tối 29/10): 156.400 cp ≈ 3,1 tỷ, +4,8% [DNSE]. Biên độ UPCOM ±15%. Vị thế lớn hơn vài trăm triệu đồng/ngày sẽ là người tạo giá.

## 10. Mốc kiểm chứng (hai chiều, lập 02/11/2026; P = ước lượng)
| # | Mốc | Ngày chấm | Chiều tích cực | Chiều tiêu cực | P(tích cực) |
|---|---|---|---|---|---|
| M1 | LNST HN Q4/2026 (BCTC Q4) | ~30/01/2027 | ≥45 tỷ | <25 tỷ | 0,50 |
| M2 | DT thuỷ điện Q4/2026 (proxy thuế TN hoặc thuyết minh) | ~30/01/2027 | ≥100 tỷ | <80 tỷ | 0,45 |
| M3 | Thuyết minh khoản thu nhập khác 33,8 tỷ (BCTC kiểm toán 2026) | ~31/03/2027 | Thu hồi/xử lý nợ có căn cứ, giữ nguyên | Bị đảo/điều chỉnh giảm | 0,60 |
| M4 | Ý kiến kiểm toán FY2026 (An Việt) | ~31/03/2027 | Chấp nhận toàn phần (nhấn mạnh vụ án được phép) | Ngoại trừ/từ chối/đổi kiểm toán | 0,65 |
| M5 | Vụ EVNNPT/PC1 (TV1 có tên trong "13 công ty bị xác định có liên quan", VnExpress 02/07) | khi có kết luận điều tra/cáo trạng/quyết định cấm thầu | Không có cấm thầu, không buộc TV1 nộp lợi bất chính | **Cấm thầu EVN 3–5 năm** và/hoặc buộc nộp lợi bất chính/bồi thường lớn (khởi tố pháp nhân gần như không xảy ra theo luật hiện hành [LV]) | 0,70 [UL, căn cứ §7] |
| M6 | Cổ tức FY2026 (ĐHĐCĐ 2027) | ~04/2027 | ≥2.000 đ | ≤1.000 đ | 0,40 |
| M7 | Phải thu KH gộp (BCTC Q4) | ~30/01/2027 | ≤390 tỷ | >430 tỷ | 0,60 |
| M8 | Đọc ngành F8 (EVN tăng giá bán lẻ ≥1 lần đến 30/06/2027) | 30/06/2027 | YES | NO | 0,55 (của người đọc ngành) |

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
- Ngày hết hạn PPA SB5 chưa xác định ⇒ DCF thuỷ điện mang rủi ro giá sau ~2033 chưa đo.

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
