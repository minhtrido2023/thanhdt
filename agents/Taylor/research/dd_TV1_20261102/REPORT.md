# DD — TV1 (CTCP Tư vấn Xây dựng Điện 1 / EVNPECC1, UPCOM) sau BCTC Q3/2026 · as-of 02/11/2026 · job `Taylor_20261102_035322`

> NGHIÊN CỨU READ-ONLY. Không khuyến nghị, không lệnh, không wire. User đang/đã giao dịch TV1 ngoài book V2.4 ⇒ "giữ/thêm/giảm" là quyết định của user; báo cáo chỉ đưa vùng giá + điều kiện đổi nhận định. Chưa qua người phản biện (Mike chạy sau).
> **Nguồn:** [Q3 tr.X] = trang PDF `src/hn_q3_2026.pdf` (BCTC HN Q3/2026, ký 29/10/2026, **chưa soát xét**, bản scan) · [ME tr.X] `src/me_q3_2026.pdf` (BCTC tổng hợp/công ty mẹ) · [GT] `src/giaitrinh_hn_q3_2026.pdf` (CV 6603/TVĐ1-P3) · [H1 tr.X] = số trang **in** của `src/hn_h1_2026.pdf` (soát xét An Việt) · [Q2 tr.1] `src/hn_q2_2026.pdf` · [IR] CBTT tải từ pecc1.com.vn vào `src/ir/` · [CB] `../dd_blind2_TV1_20261026/CYCLE_BLOCK.md` (khoá md5 4409305f…, 26/10) · [BQ] `tav2_bq` (lịch sử; chưa có dòng 2026Q3 của TV1 tại 02/11) · [DNSE] `calc/dnse_raw.json` (lấy 02/11/2026 ~10:50 ICT).
> Phép tính: `calc/valuation.py` → `calc/valuation_out.txt` (tái lập: `python3 -I calc/valuation.py`). Số tự đặt gắn **[UL]** (ước lượng). Ngành: `kb/data_registry/market-state/sector_read_power_consulting_20261028.md` (Bobby, đọc mù).

## 0. Kết luận

**Giá 19.800 đ (đóng cửa 30/10/2026 [DNSE], vốn hoá 528,5 tỷ) thấp hơn giá trị kỳ vọng có trọng số ~22.000 đ khoảng 10%, và nằm ở nửa dưới vùng cơ sở 16.400–26.100 đ** [UL; `valuation_out.txt`]. Biên an toàn **mỏng** so với rủi ro đuôi pháp lý: chỉ cần trọng số dịch sang 15/45/40 (xấu nặng hơn) là kỳ vọng ~19.600 ≈ giá. Giá trị **tài sản** (SOTP: thuỷ điện Sông Bung 5 DCF có thời hạn + tư vấn − nợ) cao hơn nhiều — thấp 24.300 / giữa 44.700 đ/cp — nhưng cổ đông thiểu số **không tiếp cận được** giá trị đó trừ khi có bán tài sản hoặc nâng cổ tức (payout 2025 chỉ 27%; SB5 từng đấu giá 5 lần không bán được) ⇒ dùng làm trần tham chiếu, KHÔNG làm neo kỳ vọng.

**Q3 đẹp trên bề mặt, nhưng một nửa là một lần:** LNST Q3 **66,9 tỷ (+150% YoY)** [Q3 tr.6; GT], trong đó **thu nhập khác 33,8 tỷ** ghi "các khoản khác", **không thuyết minh bản chất** [Q3 tr.32] và **không có tiền tương ứng** (LCTT "tiền thu khác từ HĐKD" 9T chỉ 1,45 tỷ [Q3 tr.7]). LNST **lõi** Q3 ~36,0 tỷ (+17% YoY), 9T lõi ~95,0 tỷ (**+7%**, không phải +44%) [UL: (LN gộp − QLDN + TC ròng)×0,8].

| | Tích cực (có chứng cứ) | Tiêu cực (có chứng cứ) |
|---|---|---|
| Lợi nhuận lõi | Biên gộp Q3 **38,9%** (Q3/25 34,4%); EBIT lõi Q3 44,0 (40,8) [Q3 tr.6] | QLDN Q3 **21,5 tỷ, gấp đôi** (10,6); 9T +54% [Q3 tr.6] — chưa thuyết minh lý do |
| Tư vấn | DT tư vấn Q3 ~126,9 (+18%), biên gộp ~34% [UL proxy] — khớp đọc ngành "upcycle khối lượng" | Ước lượng phụ thuộc proxy thuế tài nguyên; Q3 không có thuyết minh bộ phận |
| Thuỷ điện | Q3 ~41,2 tỷ DT ≈ cùng kỳ (~41,6) [UL proxy] | 9T ~122,4 (**−11,5%**); Q4 (47% DT năm 2025) đối mặt El Niño mạnh (ONI +2,16) [CB B] |
| Một lần | Dự phòng giảm 27,5 tỷ trong Q3 (phải thu 107,7→85,9; HTK 59,3→53,6) [Q3 tr.1; Q2 tr.1] | Thu nhập khác 33,8 tỷ **không giải thích**; thuế hiệu dụng Q3 13,1% (≠20%) gợi ý một phần không chịu thuế — **phải coi là một lần** |
| Tiền | Tiền + HTM **198,5 tỷ** (đầu năm 93,0) [Q3 tr.1]; CFO 9T 116,8 = 0,94× LNST [Q3 tr.7] | Vay 129,9 tỷ (118,8 từ "bên liên quan" — cá nhân) + lãi vay cá nhân phải trả 64,3 (30/6) + cổ tức 43,2 (đã trả 29/10) ⇒ net điều chỉnh **≈ −39 tỷ** |
| Phải thu | Phải thu KH gộp 387,5 **giảm** so đầu năm (408,2) [Q3 tr.12] | Dự phòng phải thu KH **tăng** 63,2→68,4; tổng dự phòng mã 136 (85,9) **không khớp** tổng thuyết minh (68,4+2,1) — lệch 15,5 tỷ chưa giải |
| Định giá | P/E TTM 2,8x (lõi 3,2x), P/B **0,92**, cổ tức 1.500 đ = **7,6%** [IR; `valuation_out`] | Trung vị P/E 2025 (trước vụ án) 6,0x, P/B 1,53 [BQ] — chiết khấu hiện tại là **giá của rủi ro pháp lý**, không phải sai giá thuần |
| Kiểm toán | **Đã có kiểm toán FY2026: An Việt** (HĐ ký 18/08/2026) [IR CBTT 4958]; soát xét H1: kết luận chấp nhận, đoạn nhấn mạnh vụ án [H1 tr.4] | Big4 từ chối trước đó; An Việt là hãng nội địa nhỏ — chất lượng bảo đảm thấp hơn |
| Pháp lý | Pháp nhân TV1 chưa bị khởi tố (theo BCTC H1 TM33) | ⚠️ Chủ tịch HĐQT + phó phòng TCKT bị khởi tố, tạm giam 07/05/2026 (vụ EVNNPT/PC1: đấu thầu, **kế toán**, tham ô) [H1 tr.38]; chưa kết luận |

**3 kịch bản (giá trị/cp cho cổ đông thiểu số, 2027–28; [UL]):**

| Kịch bản | P | Giả định | Phép tính | Giá trị/cp |
|---|---|---|---|---|
| Tốt | 25% | Vụ án khép lại không chạm pháp nhân; FY2026 kiểm toán sạch; thị trường trả lại P/E ~ 2025 (trung vị 6,0) | LNST bền 150–170 × P/E 5–6 | **28.100–38.200** (tâm ~33.000) |
| Cơ sở | 50% | Overhang kéo dài 1–2 năm; thuỷ điện về mức thiết kế–trung bình; tư vấn LNST 30–50 | LNST 125–155 × P/E 3,5–4,5 | **16.400–26.100** (tâm ~21.000) |
| Xấu | 25% | Pháp nhân bị khởi tố/cấm thầu EVN, kiểm toán ngoại trừ, El Niño cắt thuỷ điện | P/B 0,5–0,7 (min lịch sử 0,50; vùng đáy 2019–21 0,57–0,94) | **10.800–15.100** (tâm ~12.900) |

Trọng số 25/50/25 **không có căn cứ dữ liệu để nghiêng**. Độ nhạy: 20/50/30 ⇒ 21.000 (giá −6%); 15/45/40 ⇒ 19.600 (giá +1%); 30/50/20 ⇒ 23.000 (−14%); P/E ±15% ⇒ 19.200–24.800.

**Thị trường đang định giá gì:** ở 19.800, P/E 4,0 ngầm định LNST bền ~132 tỷ; P/E 3,5 ⇒ ~151 — tức thị trường **đã chấp nhận LN quanh mức 2025** nhưng áp bội số ~1/2 thời trước vụ án. Biến quyết định không phải LN quý mà là **kết luận vụ án + ý kiến kiểm toán FY2026**.

**Điều làm nhận định TÍCH CỰC hơn:** (1) Kiểm toán FY2026 (An Việt) chấp nhận toàn phần, không ngoại trừ (~03/2027); (2) kết luận điều tra không nêu pháp nhân TV1 / không truy thu; (3) Q4/2026 thuỷ điện ≥100 tỷ DT dù El Niño; (4) ĐHĐCĐ 2027 nâng cổ tức ≥2.000 đ (payout ≥35%) hoặc tái khởi động bán SB5 có giá ≥1.000 tỷ; (5) thuyết minh rõ khoản thu nhập khác 33,8 tỷ là thu hồi nợ thật (có tiền). **Điều làm TIÊU CỰC hơn:** (1) khởi tố pháp nhân TV1 hoặc cấm dự thầu EVN/EVNNPT; (2) kiểm toán FY2026 ngoại trừ/từ chối, hoặc đổi kiểm toán lần nữa; (3) khoản 33,8 tỷ bị đảo ngược ở BCTC kiểm toán; (4) Q4/2026 thuỷ điện <80 tỷ DT (El Niño); (5) phải thu KH gộp >430 tỷ hoặc dự phòng tăng mạnh; (6) phán quyết vụ Lê Phi Long bất lợi vượt sổ (gốc 64,4 + lãi 42,1 đã ghi).

## 1. Kiểm lại số dùng lại (DD cũ, CYCLE_BLOCK, checklist)
| Số | Nguồn cũ | Kiểm | Kết quả |
|---|---|---|---|
| "Nợ dự án trả hết", net debt ~117 (SOTP 23/07) | BQ | Vay DH 0,41 tỷ [Q3 tr.4] ✅; nhưng vay NH 129,5 chủ yếu là **vay cá nhân/bên liên quan** (118,8) [Q3 tr.21], không phải "vốn lưu động tư vấn" | Nửa đúng — nay net cash thô +68,7, net điều chỉnh −38,7 |
| FCF thuỷ điện 110–140/năm (SOTP 23/07) | UL | Dựng lại từ hàm chi phí [CB B]: 101 (DT 171) / 122 (DT 200) / 150 (DT 239) | Cùng vùng; SOTP bảo thủ cũ 33.100 đ/cp **không tái lập** khi cắt PPA −20% từ 2034 + Ke 13%: 24.300 |
| Phải thu tư vấn "~295 tỷ" (checklist) | BQ 2026Q1 | Phải thu KH **gộp 387,5 / ròng 319,1** tại 30/9 [Q3 tr.12] | Số 295 là khái niệm khác (BQ); dùng BCTC |
| "Big4 từ chối FY2026" | SOTP 23/07 | Đã ký An Việt 18/08 [IR] | Rủi ro "không có kiểm toán viên" **đã đóng**; rủi ro chất lượng kiểm toán còn |
| Cổ tức 2025 ~1.500–1.600 [CB D] | UL | 1.500 đ, GDKHQ ~07/10, chốt 08/10, trả 29/10/2026 [IR CBTT 5744] | ✅ |
| 9T LNST − H1 soát xét = Q3 | | 124,636 − 57,759 = 66,877 ✅ | Khớp |
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
| LNST lõi [UL, thuế 20%] | ~36,0 | ~30,7 | ~95,0 | ~88,9 |

- **Một lần — thu nhập khác 33,8 tỷ**: dòng "các khoản khác" 33.802.250.432 đ [Q3 tr.32], mẹ 33.715.114.112 [ME tr.24] ⇒ phát sinh ở công ty mẹ. BCTC Q3 **không** thuyết minh. Bằng chứng gián tiếp: dự phòng (phải thu + HTK) giảm **27,5 tỷ** trong Q3 [Q3 tr.1 vs Q2 tr.1]; LCTT "các khoản dự phòng" 9T −22,61 vs H1 (Q2 chưa soát xét) −5,94 ⇒ Q3 ~−16,7 [Q3 tr.7; Q2 tr.7]. **Giả thuyết** (chưa xác nhận): một phần là hoàn nhập dự phòng/xoá sổ nợ phải trả ghi vào thu nhập khác. Không phải tiền: "tiền thu khác từ HĐKD" 9T 1,45 tỷ. Không phải xoá lãi vay ông Lê Phi Long: phải trả khác 30/9 90,05 ≈ 30/6 88,79 [Q3 tr.24; H1 tr.27].
- **Thuế hiệu dụng Q3 13,1%** — gợi ý phần lớn khoản khác không chịu thuế (hoàn nhập dự phòng đã không được trừ khi trích là lời giải phổ biến) [UL].
- **QLDN gấp đôi** — chưa thuyết minh; 9T QLDN 42,4 so FY2025 ~45 [UL]. Soát xét H1 đã cộng thêm 6,25 tỷ QLDN [explanation_yoy_en]. Có thể gồm chi phí pháp lý/dự phòng; nếu là trích lập thì phần "lõi" ở trên **bị đánh thấp** — tức LNST lõi thật nằm trong khoảng 36–44 tỷ/quý (ước lượng không đủ cơ sở để chọn điểm).
- **Doanh thu tài chính** 9T 7,11 tỷ, trong đó lãi tiền gửi 5,66 [Q3 tr.31] trên số dư HTM tăng 60,9→167,8 + tiền 30,7 (lãi bình quân ~5–6%/năm trên số dư bình quân ~120 tỷ [UL]) — nhỏ, không phải nguồn LN chính (khác TV2).

## 4. Tách mảng Q3 (BCTC Q3 KHÔNG có báo cáo bộ phận) [UL]
- **Proxy**: thuế tài nguyên phải nộp 9T 13,227 [Q3 tr.23] vs H1 8,776 [H1 tr.27] ⇒ Q3 = 0,507× H1 ⇒ thuỷ điện Q3 ≈ **41,2 tỷ DT** (H1 81,20 [CB A]). Giả định thuế tài nguyên tỷ lệ thuận DT thuỷ điện trong năm.
- Hàm chi phí thuỷ điện [CB B]: 15,2 tỷ/quý cố định + 10% DT ⇒ LN gộp thuỷ điện Q3 ~21,9; **tư vấn Q3 DT ~126,9 (+18% so ~107,7), biên ~34%** (nhạy: thuỷ điện 38–45 ⇒ biên tư vấn 32,6–35,7%).
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
- **CFO 9T 116,8** (9T/25 137,6) = 0,94× LNST; trừ khoản khác không tiền 31,9 ⇒ CFO ≈ 1,2× LNST lõi — **chất lượng dòng tiền tốt**. Q3 CFO ≈ 62,5 [UL: 9T − H1 chưa soát xét 54,4]. Tiền dư dồn vào tiền gửi HTM (chi 218,6, thu 105,9 [Q3 tr.7-8]).
- **Checklist (2) — phải thu tư vấn**: phải thu KH gộp **408,2 → 378,7 (30/6) → 387,5 (30/9)**; dự phòng phải thu KH 63,2 → 68,4 (+5,1) [Q3 tr.12-13]. Phải thu bên liên quan 259,7 (dự phòng 9,6; đầu năm 267,7/1,9) — dự phòng bên liên quan **tăng 7,7**. Công ty Mua bán điện 34,0 (đầu năm 64,5). Kết luận: **không tăng, có trích lập thêm nhỏ**; ⚠️ tổng dự phòng mã 136 (85,9) ≠ tổng thuyết minh (68,4 KH + 2,1 khác = 70,5) — lệch 15,5 tỷ chưa giải (đầu năm lệch 47,8: 113,1 vs 65,3). Một BCTC chưa soát xét có thuyết minh không khớp bảng cân đối là **cờ chất lượng báo cáo**, không phải bằng chứng gian lận.
- Tồn kho (dở dang tư vấn) 148,8 gộp, dự phòng 53,6 (36%) [Q3 tr.15] — chi phí dở dang cũ đã trích lập lớn.
- Điều chỉnh VCSH trực tiếp **+8,90 tỷ** ở H1 ("bù trừ thiếu trên báo cáo từ các năm trước") [H1 tr.30] — ghi thẳng vốn, không qua KQKD; cần kiểm toán FY2026 xác nhận.

## 6. Ghi nhận doanh thu tư vấn, backlog, khách hàng
- BCTC Q3 phân loại DT 9T: "bán sản phẩm, hàng hoá" 413,9 + "cung cấp dịch vụ" 33,0 [Q3 tr.30]; **không** có dòng "DT hợp đồng xây dựng" ⇒ không đọc được phương pháp % hoàn thành từ Q3. Người mua trả trước 138,7 (+33%) — proxy backlog tăng [CB B]. Không có giá trị backlog công bố.
- Khách hàng (H1, bên liên quan): Mua bán điện 63,8; BQLDA điện miền Bắc (EVNNPT) **45,5** (H1/25 2,0); BQLDA Truyền tải điện (EVNNPT) 18,2 [H1 tr.36] ⇒ **khối EVNNPT là động lực tăng DT tư vấn 2026** — đúng khách hàng nơi xảy ra vụ án. Rủi ro đấu thầu: nếu pháp nhân TV1 bị kết luận vi phạm đấu thầu, mảng này chịu rủi ro "mất vị trí" (chưa xác định).

## 7. Pháp lý, quản trị — ⚠️ WARNING (mức cao; không chặn phân tích)
- ⚠️ **Vụ EVNNPT/PC1**: 07/05/2026 khởi tố, tạm giam **Chủ tịch HĐQT + phó phòng TCKT** TV1; vụ án gồm "vi phạm quy định về đấu thầu… vi phạm quy định về **kế toán**… tham ô… đưa/nhận hối lộ"; chưa kết luận; ban lãnh đạo khẳng định không cần trích lập [H1 tr.38 TM33]. Cùng vụ: cựu Chủ tịch + KTT TV2 bị khởi tố tham ô (Đ.353); Bộ Công an 02/07/2026 nêu 13 pháp nhân, gồm "các công ty tư vấn xây dựng điện", không nêu tên (theo DD TV2 01/11, chưa tự kiểm lại). **Không tra tin mới sau 28/10 trong lượt này.**
- ⚠️ **"Scandal di cư"**: người bị khởi tố có **phó phòng TCKT** + nhóm tội **kế toán** ⇒ rủi ro không chỉ là pháp nhân/đấu thầu mà là **độ tin cậy số liệu quá khứ** (2023–25 — giai đoạn LN tăng mạnh). Ba dấu hiệu nhỏ cùng chiều cần theo dõi (không chứng minh sai phạm): điều chỉnh VCSH trực tiếp +8,9 tỷ (H1); thu nhập khác 33,8 tỷ không thuyết minh (Q3); dự phòng mã 136 lệch thuyết minh 15,5 tỷ (Q3).
- **Kiểm toán**: FY2025 A&C chấp nhận toàn phần; soát xét H1/2026 **An Việt**: kết luận chấp nhận + đoạn nhấn mạnh vụ án [H1 tr.4]; HĐ kiểm toán FY2026 với **An Việt** ký 18/08/2026 [IR CBTT 4958]. **Checklist (3)**: đã bổ nhiệm kiểm toán mới; chưa có ý kiến ngoại trừ nào. Q3 chưa soát xét.
- Tranh chấp vốn huy động cá nhân (Ngãi, Long) — tồn đọng từ 2013–17.
- Room ngoại: có CBTT "tỷ lệ sở hữu nước ngoài tối đa" [IR] — **chưa đọc nội dung** (không suy ra con số).

## 8. Định giá — `calc/valuation_out.txt`
### 8a. Bội số hôm nay (giá 19.800, 26.691.319 cp)
| | Giá trị |
|---|---|
| Vốn hoá / EV (net điều chỉnh −38,7) | 528,5 / 567,2 tỷ |
| P/E TTM (Q4/25 [BQ] 63,85 + 9T/26 124,6 = 188,5) | **2,80x**; bỏ khoản khác Q3 ⇒ 3,24x |
| P/B (VCSH 574,7) | **0,92x** |
| Cổ tức 2025 | 1.500 đ ⇒ 7,6%; payout 27% LNST 2025 |
| Lịch sử [BQ, trung vị năm] | P/E 2024 7,9 / 2025 6,0 / 2026 YTD 4,0; P/B 2024 1,60 / 2025 1,53 / 2026 1,12 (min 0,95) |

### 8b. SOTP giá trị tài sản (trần tham chiếu, không phải kỳ vọng)
DCF thuỷ điện có thời hạn (2027–2059, thuê đất đến 08/2059 [CB D]), FCF = (DT×0,9 − 60,8 − 8 chi phí chung)×0,8 + KH 38 − capex 5 [UL]. Lãi suất **10–13%** (khớp kỳ hạn ~33 năm, rủi ro thuỷ văn + PPA; đặt quanh dải Ke nội địa 12,3–13,4% vì cổ đông chịu toàn bộ rủi ro tài sản):

| DT thuỷ điện/năm \ r | 10% | 11% | 12% | 13% |
|---|---|---|---|---|
| 171 (thiết kế 187 GWh × ~912 đ/kWh [UL]) | 967 | 890 | 822 | 764 |
| 200 | 1.167 | 1.073 | 992 | 922 |
| 239 (TB 2024–25) | 1.436 | 1.320 | 1.221 | 1.134 |

Rủi ro PPA (ngày hết hạn chưa xác định; giả định −20% DT từ 2034 [UL]): DT200 r12% ⇒ 889; DT171 r13% ⇒ 687. SOTP thấp = 687 + tư vấn 0 − 38,7 = **648 tỷ = 24.300 đ/cp**; giữa = 992 + tư vấn 40×6 − 38,7 = **1.193 tỷ = 44.700 đ/cp**. Đối chiếu: SB5 rao bán 2017–18 giá khởi điểm 1.688 → 1.390 tỷ (gồm nợ), **5 lần không bán được** [SOTP 23/07].

**Vì sao không dùng SOTP làm kỳ vọng:** cổ đông thiểu số nhận giá trị qua **cổ tức** (payout 27%) hoặc **bán tài sản** (tiền sử thất bại). Phép thử dòng cổ tức (g=0, Ke 12,3–13,4%): DPS 1.500 ⇒ 11.200–12.200; 2.000 ⇒ 14.900–16.300; 2.800 (payout ~50%) ⇒ 20.900–22.800 đ/cp. Giá 19.800 ≈ thị trường kỳ vọng payout tăng lên ~45–50% hoặc giá trị giữ lại không bị rò rỉ.

### 8c. Chi phí vốn, DCF vô hạn
Không làm DCF vô hạn cho tư vấn: DT phụ thuộc tư cách nhà thầu EVN (chưa xác định sau vụ án) — terminal Gordon sẽ là giả định chồng giả định. Dùng P/E với Ke nội địa 12,3–13,4% làm phép thử: tư vấn g≈0, payout cao ⇒ P/E hợp lý ~6–8x **nếu không có rủi ro pháp lý**; dải 3,5–6x ở §0 là chiết khấu pháp lý tự đặt [UL].
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

LNST bền cơ sở 125–155 [UL] = thuỷ điện 75–110 (thiết kế → TB) + tư vấn 30–50 + TC ~5 − phần không phân bổ. LNST 2023/24/25: 75,6 / 92,0 / 150,2 [CB E].

## 9. Thanh khoản [BQ, DNSE]
ADV20 đến 28/10: **0,72 tỷ/ngày** trung bình, **trung vị 0,41 tỷ** [BQ `calc/bq_px.csv`]; phiên 30/10 (sau công bố Q3 tối 29/10): 156.400 cp ≈ 3,1 tỷ, +4,8% [DNSE]. Biên độ UPCOM ±15%. Vị thế lớn hơn vài trăm triệu đồng/ngày sẽ là người tạo giá.

## 10. Mốc kiểm chứng (hai chiều, lập 02/11/2026; P = ước lượng)
| # | Mốc | Ngày chấm | Chiều tích cực | Chiều tiêu cực | P(tích cực) |
|---|---|---|---|---|---|
| M1 | LNST HN Q4/2026 (BCTC Q4) | ~30/01/2027 | ≥45 tỷ | <25 tỷ | 0,50 |
| M2 | DT thuỷ điện Q4/2026 (proxy thuế TN hoặc thuyết minh) | ~30/01/2027 | ≥100 tỷ | <80 tỷ | 0,45 |
| M3 | Thuyết minh khoản thu nhập khác 33,8 tỷ (BCTC kiểm toán 2026) | ~31/03/2027 | Thu hồi/xử lý nợ có căn cứ, giữ nguyên | Bị đảo/điều chỉnh giảm | 0,60 |
| M4 | Ý kiến kiểm toán FY2026 (An Việt) | ~31/03/2027 | Chấp nhận toàn phần (nhấn mạnh vụ án được phép) | Ngoại trừ/từ chối/đổi kiểm toán | 0,65 |
| M5 | Vụ EVNNPT/PC1 | khi có kết luận điều tra | Không nêu pháp nhân TV1 | Khởi tố pháp nhân/cấm thầu | 0,70 |
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
- Chưa đọc: BCTC Q3 mẹ đầy đủ (chỉ trang 6, 24), CBTT room ngoại, BCTN 2025, tin pháp lý sau 28/10. Chưa có người phản biện.
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
