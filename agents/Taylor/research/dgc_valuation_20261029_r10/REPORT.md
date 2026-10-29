# DGC định giá VÒNG 10: áp sửa phản biện fundamental-skeptic lên r9

Job `Taylor_20261029_115813`. r1-r9 không sửa; `model.py` giữ nguyên và tái lập: **A7 32.182 / B7 37.060 / R1 30.598 / R2 36.663** (assert trong `r10_calc.py`; 6 file `out_r9_*` khớp r9). Bảng mới: `python3 r10_calc.py` → `run_stdout_r10.txt`, `out_r10_*.csv`. READ-ONLY, không phải khuyến nghị đặt lệnh. Đơn vị: tỷ đồng; đ/cp. **[UL]** = giả định; **[suy luận]** = rút ra bằng loại trừ/theo chuẩn mực, không phải nguồn nói thẳng; **[chưa chứng minh]**. BCTC Q3 CHƯA soát xét. Luật pháp lý 27/09: chỉ WARNING. Giá tham chiếu 32.900 (28/10). Nhãn **P1** (user đã chọn) giữ nguyên; **không chọn base case thay user**.

## Kết luận (≤12 dòng)
1. **Khoản 200 tỷ không gây ra chênh 6.065 đ/cp giữa R1 và R2**; chênh đến từ giả định R1 "100 tỷ/QUÝ lặp vĩnh viễn" (400 tỷ/năm, hạ biên 4,3pp). Cả R1 lẫn R2 đã trừ 200 như nợ (~541 đ/cp/bên). Không thấy tính đôi giữa hai phần đó.
2. **Sửa sai r9 (số):** "100 tỷ/quý lặp vĩnh viễn = 1.516 đ/cp" SAI. Đúng: **100 tỷ/quý vĩnh viễn = −6.065 (= R1)**; 1.516 là mức cho 100 tỷ/NĂM (25/quý). So với 263 đ/cp (trừ một lần 100 tỷ) là **~23 lần**, không phải 5,8.
3. **Sửa sai r9 (tính đôi nhỏ):** biên Q4/2026 19% (nội suy từ Q2 18,9% / Q3 20,5% đã gồm dự phòng) ngầm chứa ~100 tỷ trích Q4 = **217 đ/cp** (đo: `out_r10_q4_split.csv`). Tách Q4 ex-dự phòng: **R2 N=0 = 36.880 (không phải 36.663), r4 N=0 = 32.399**; mọi hàng N≥1 của r9 trừ quý đầu hai lần. Đã chạy lại bảng.
4. **Cùng cơ sở thuế:** bảng N nay có hai cột (trước thuế / sau lá chắn 20% [UL]); hàng vĩnh viễn thô 100/quý = −7.406 (trước thuế) / −5.925 (sau lá chắn) vs −6.065 của model. Khấu trừ thuế của chi phí/dự phòng môi trường **chưa xác minh** (giao legal-vn) nên hiển thị cả hai.
5. **Hữu hạn vs lặp: chưa loại trừ.** Lập luận "VAS 18 + dự phòng ngắn hạn ⇒ hữu hạn" của r9 **bị bỏ** (không phân biệt được). Bằng chứng phân biệt được (§3): nhãn "restoration" nghiêng hữu hạn nhẹ; chữ "arising from production and business activities" nghiêng vận hành/lặp; Q3 trích thêm 100 nghiêng lặp/tăng. Mức: **R1 chưa loại trừ; bằng chứng nghiêng nhẹ-vừa về hữu hạn, không phải "thấp"; "một lần" chưa xác lập.**
6. **r8→r9 lật chiều theo hướng user nghi** — phần có căn cứ mới chỉ là: sửa chữ "thường xuyên" r8, số 263, đọc lại thuyết minh Q3; không phải toàn bộ chiều lật.
7. **Dải A7 đối xứng hai nền biên (Q4 ex-dự phòng, trước thuế → sau lá chắn 20%):**
   - nền r4: N=0 **32.399**; 200×8 quý **28.807 → 29.525**
   - nền R2: N=0 **36.880**; 200×8 quý **33.288 → 34.006**
   - R1 (100/quý vĩnh viễn, model): **30.598**
   Nền r4 chồng hai giả định bi quan: ngầm ~**281 tỷ/năm** chi phí so với run-rate Q3 bỏ dự phòng [UL] **cộng** 200×8 quý (§5).
8. Biên gộp 2027-28 vẫn nặng ký: ~1.420 đ/cp mỗi 1pp. P1 và 8 trigger HARD ABANDON **giữ nguyên chữ**; ghi chú thêm ở §6.
9. Đính chính r9: §9. Câu hỏi mở thêm: T7 gồm công ty con không; khấu trừ thuế; 332,29 vs 332,33 (§7).

## 1. Phân rã chênh R2 → R1 (6.065 đ/cp)
Nguồn: `out_r9_methods_R1_R2.csv`, `out_r9_decomp_R2_R1.csv`. Trị số mỗi phương pháp là trung bình theo trọng số kịch bản 0,2/0,5/0,3. EV = TB(SOTP, DCF, TB(3 bội số)), nên SOTP và DCF mỗi cái chiếm trọng số 1/3, mỗi bội số chiếm 1/9.

| Phương pháp | R1 | R2 | R2−R1 | Trọng số | Đóng góp vào EV |
|---|---|---|---|---|---|
| SOTP | 30.016 | 35.657 | 5.641 | 1/3 | **1.880** |
| DCF | 30.047 | 35.496 | 5.449 | 1/3 | **1.816** |
| PE DGC 10y (lõi) | 32.460 | 39.602 | 7.142 | 1/9 | 794 |
| PE peer (lõi) | 33.145 | 40.511 | 7.366 | 1/9 | 818 |
| P/B chính đáng | 29.592 | 36.398 | 6.806 | 1/9 | 756 |
| **EV A7** | **30.598** | **36.663** | **6.065** | | 6.064 (làm tròn) |

**(a) Phần trừ MỘT LẦN 200 tỷ.** Phần này **giống nhau ở cả R1 và R2**, nên đóng góp vào chênh R2−R1 bằng **0**.
- Bỏ khoản trừ 200: R1 tăng +542, R2 tăng +541.
- 527 đ/cp đi thẳng qua cash_adj. Khoảng ~15 còn lại đi qua P/B, vì khoản nợ được tách khỏi VCSH lõi.
- Hai khoản trừ này là cùng một khoản 200 tỷ, nên chênh giữa chúng triệt tiêu nhau.

**(b) Giả định biên.** Phần này chiếm **100% chênh lệch**.
- R1 lấy giá vốn Q3 × 4 = 7.852 (gồm 100 dự phòng) và giữ phẳng. R2 lấy 7.852 − 400.
- Chênh 400/năm trên doanh thu lõi 2027 = 9.261 cho ra **4,32pp biên**. Mức dịch này áp đồng loạt cho cả ba kịch bản và cả hai năm 2027-28.
- Mọi phương pháp đều vốn hoá chênh lệch này vô hạn:
  - SOTP: LNST lõi chuẩn hoá × PE lõi 6-8.
  - DCF: EBIT 2028 tăng trưởng 3% rồi đi vào terminal.
  - PE: LNST 2027-28 × PE.
  - P/B: chênh lệch đi qua ROE.
- Vì vậy 400 tỷ/năm trước thuế, ở Ke 14,9%, ≈ 6.000 đ/cp. Con số này không phải lỗi mô hình; nó là hệ quả trực tiếp của giả định "vĩnh viễn".


**Kiểm tính đôi theo từng phương pháp (SỬA ở dòng Q4):**

| | R1 | R2 | Tính đôi? |
|---|---|---|---|
| SOTP / DCF / PE / P/B | trừ 200 qua cash_adj (nợ đã ghi nhận, tiền sẽ chi) + biên đã gồm 400/năm chi phí **mới** | trừ 200; biên không gồm 400 | **Không** giữa 200 và 400/năm: 200 là chi phí Q2-Q3 đã hạch toán vào LN 2026 thực (không đi vào định giá, trừ q4_core); 400/năm của R1 là các lần trích **tương lai**. |
| P/B | 200 cộng lại vào VCSH lõi (`extras_book`) để không trừ hai lần | như R1 | **Không** (đã xử lý đúng) |
| Cầu Q4/2026 (q4_core) | biên Q4 cơ sở 19,0% [UL] (nội suy Q2 18,9% / Q3 20,5%, **đã gồm dự phòng**) ngầm chứa khoản trích Q4 ~100 tỷ | như R1 | **CÓ, ở R2 và ở mọi hàng N≥1 hữu hạn của r9**: Q4 đã trừ ~100 trong biên, rồi bảng N trừ lại quý đầu. Đo: cộng 100 tỷ vào LN gộp Q4 mỗi kịch bản → A7 **+217** (cả nền r4 lẫn R2; `out_r10_q4_split.csv`). R1 nhất quán (Q4 trích 100 + 400/năm từ 2027); R2 N=0 r9 thấp 217. **Tách đúng ở §2.** |

R1 − R2 (Q4 ex-dự phòng) = **−6.282** = −6.065 (400/năm từ 2027) − 217 (Q4).

**Ghi chú về chữ "R1 lặp ~100/quý":**
- Biên R1 15,2% thấp hơn **cả** biên Q3 thực tế 20,5% đã gồm dự phòng.
- Lý do: model hạ doanh thu 2027 xuống 9.261 (so với Q3 × 4 = 9.878, tức −6,2%; P4 4.150 $/t) nhưng giữ giá vốn phẳng.
- Như vậy 15,2% = dự phòng lặp **cộng** doanh thu giảm mà giá vốn không giảm. Chỉ phần đầu là câu hỏi dự phòng.
- Ở doanh thu Q3 × 4: R1 = 20,5%, R2 = 24,6%.

## 2. Độ nhạy theo N quý trích thêm và mức trích mỗi quý (SỬA: Q4 tách đúng, hai cơ sở thuế)
**Bảng phụ thuộc, không có base case.** Nguồn: `out_r10_finite_N.csv`, `out_r10_perpetual.csv`. Ke = 14,9%; quý j chi tại t = 0,17 + (j−0,5)/4 năm từ 29/10 [UL thời điểm chi]. Nền: **R2 Q4 ex-dự phòng = 36.880** (N=0 = không trích thêm kể cả Q4). Mức giảm (đ/cp) cộng thẳng vào bất kỳ nền biên nào.

**Mức giảm, trích 100 tỷ/quý, hai cơ sở:**

| N quý | Trước thuế (PV) | Sau lá chắn 20% [UL] | A7 nền R2 (trước thuế / sau lá chắn) | A7 nền r4 (trước / sau) |
|---|---|---|---|---|
| 0 | 0 | 0 | 36.880 | 32.399 |
| 1 | −253 | −202 | 36.627 / 36.678 | 32.146 / 32.197 |
| 2 | −497 | −397 | 36.383 / 36.483 | 31.902 / 32.002 |
| 4 | −960 | −768 | 35.920 / 36.112 | 31.439 / 31.631 |
| 8 | −1.796 | −1.437 | 35.084 / 35.443 | 30.603 / 30.962 |
| **vĩnh viễn, thô (cùng timing)** | **−7.406** | **−5.925** | | |
| vĩnh viễn qua model (R1; thuế lõi + MI + bội số, nền Q4-ngầm r9) | −6.065 | | 30.598 | |

- Cùng cơ sở: vĩnh viễn thô sau lá chắn 20% (−5.925) ≈ −6.065 của model, nên hàng model có thể đọc như "đã gồm thuế" và so được với cột "sau lá chắn". Trước thuế thì so với −7.406.
- **Khả năng khấu trừ thuế của chi phí/dự phòng môi trường: CHƯA xác minh** (đã giao legal-vn) ⇒ hiển thị cả hai cơ sở, không chọn.
- Mức trích 50 và 200/quý: xem CSV (200 × 8 quý: −3.592 / −2.874; vĩnh viễn 50/quý −3.032 và 200/quý −12.129 qua model, tuyến tính).

**Mỗi 100 tỷ, đo theo cơ sở (trước thuế):**

| Cơ sở | đ/cp | Gấp so với trừ một lần |
|---|---|---|
| Trừ một lần 100 tỷ | 263 | 1× |
| Trích thêm 1 quý (PV) | 253 | 1× |
| 100 tỷ/quý × 4 quý | 960 | 3,6× |
| 100 tỷ/quý × 8 quý | 1.796 | 6,8× |
| **100 tỷ/quý lặp vĩnh viễn (R1)** | **6.065** (qua model; thô 7.406 trước thuế) | **~23×** |
| 100 tỷ/NĂM (25/quý) lặp vĩnh viễn | ~1.512 (`out_r10_perpetual.csv`, 25/quý) | ~5,8× |

r9 (L7/L96/L186) nhầm hai dòng cuối: gán 1.516 cho "100 tỷ/quý". r8 viết "263 đ/cp mỗi 100 tỷ/quý" và gọi khoản này nhỏ; câu đó chỉ đúng cho một lần trích.

## 3. Bằng chứng một lần hay lặp lại (VIẾT LẠI)
**Bỏ lập luận r9 "VAS 18 + dự phòng ngắn hạn ⇒ hữu hạn".** Lý do: VAS 18 vẫn cho trích định kỳ cho nghĩa vụ phát sinh mỗi kỳ, và khoản chi trong 12 tháng cũng là ngắn hạn, nên hai điểm đó **không phân biệt** được hữu hạn với lặp. Phần dưới chỉ giữ các bằng chứng có chiều phân biệt, mỗi cái ghi nguồn + chiều.

| # | Bằng chứng | Nguồn | Chiều |
|---|---|---|---|
| a | Nhãn khoản mục: *Provision for environmental **restoration** costs* (khôi phục) | note 19 BCTC soát xét H1/2026, trang in 32 (`source_pages_h1/h1_p33.png`) | **Hữu hạn nhẹ** [suy luận từ chữ "restoration"] |
| b | 0 đồng sử dụng sau 6 tháng: H1 cột giảm "-"; LCTT 9T mã 03 +199,95 ⇒ chưa chi đồng nào trong 200 tới 30/09 | note 19 H1; LCTT Q3 | **Không phân định**: nghiêng dự án khắc phục đang chờ (hữu hạn) HOẶC chưa đến hạn chi |
| c | Phát biểu ĐHĐCĐ 13/08 đặt trong đoạn nói về vụ án (diễn ý báo chí, §3 v'') | doanhnhan.baophapluat.vn 15/08 | Nghiêng **liên quan vụ án** (≈ hữu hạn nếu là nghĩa vụ vụ án); không nói gì về lặp |
| d | Chú thích (*) note 19: "best estimate of the future expected expenses in connection with environmental management and treatment **arising from the Group's production and business activities**. Actual expenses incurred may differ" | note 19 H1 | Nghiêng **vận hành/lặp** (chữ "production and business activities"); r8 viết "thường xuyên" là SAI chữ, nhưng chữ thật vẫn nghiêng hướng này |
| e | Q3 trích thêm +100 (mã 322: 100 → 200); không thuyết minh | BCTC Q3 | Ước tính đã **tăng**; nghiêng lặp/tăng, không phân biệt hữu hạn với lặp |

**Mức R1 (100/quý vĩnh viễn): chưa loại trừ; bằng chứng nghiêng nhẹ-vừa về hữu hạn** (a, c nghiêng hữu hạn; d, e nghiêng lặp/tăng; b không phân định). KHÔNG phải "thấp". **"Một lần" chưa xác lập.**

**Ghi nhận trung thực:** r8→r9 lật chiều theo hướng nghi ngờ của user. Phần có căn cứ mới là: sửa chữ "thường xuyên" r8, số 263, đọc lại thuyết minh Q3 (không có). Lập luận VAS 18 của r9 là phần không có căn cứ phân biệt, nay đã bỏ.

**Các dòng bằng chứng khác (mỗi dòng ghi nguồn + chiều):**

| # | Bằng chứng | Nguồn | Ủng hộ |
|---|---|---|---|
| i' | Bảng cân đối H1, mã 322 = 100.000.000.000; đầu năm trống | BCTC soát xét H1, trang in 7 (`src_r9/h1_p8.png`) | Số dư 31/12/2025 = 0 |
| ii | BCTC Q3 **không có thuyết minh dự phòng**: thuyết minh nhảy từ note 15, 16, 17 sang 18. Chỉ có mã 322 = 200 trên bảng cân đối và dòng LCTT "dự phòng +199,95" 9T. **Hạ trọng số:** theo phản biện fundamental-skeptic (tôi chưa tự đối chiếu ở r10), BCTC quý DGC cũng không thuyết minh mã 315 (162,5 tỷ) và 316, nên đây là **cách trình bày báo cáo quý nói chung, không riêng khoản này**. | BCTC Q3, trang in 32-34 (`../dgc_valuation_20261027_r6/source_pages/p33-p35.png`) | **Không phân định** (không còn là lý do chính để nói "chưa xác lập một lần") |
| ii' | Văn bản giải trình Q3 (12/2026/CV-KT-DGC, 28/10) chỉ giải thích LN giảm bằng: doanh thu −12%; S, điện, than cốc, NH3 tăng; khai trường 25 dừng nên phải dùng quặng nhập/mua ngoài. **Không nhắc dự phòng.** | `/tmp/dgcpdf/20261028-DGC-Announcement-...pdf` trang 2-3 (`src_r9/q3expl_p2.png`) | Không phân định |
| iii | **Chỉ tiêu KQKD** [suy luận loại trừ]. 9T: chi phí khác = H1 13,95 + Q3 38,42 = 52,4 (<200). Note 28 QLDN 9T gồm nhân viên 83,4 · khấu hao 22,1 · dịch vụ mua ngoài 29,1 · khác 20,1, không dòng nào chứa được 100. Note 27 bán hàng 9T, dòng "khác" 52,2. Note 26 tài chính: lãi vay + chênh lệch tỷ giá. Note 24 giá vốn chỉ có **một dòng** 5.558,26. ⇒ 200 gần như chắc nằm trong **giá vốn**. | BCTC Q3 trang in 38-39 (`p39.png`, `p40.png`); KQKD H1 trang in 8 (`src_r9/h1_p9b.png`) | Không có nguồn nói thẳng; chia nhỏ ra nhiều dòng về số học là có thể nhưng không hợp lý |
| iv | Soát xét H1 (UHY, 995/2026/UHY-BCSX, 26/08): **cơ sở ngoại trừ** = vụ việc "natural resource exploitation, environment, and accounting" còn đang điều tra; không đủ bằng chứng để xác định có cần điều chỉnh khoản mục nào không. **Không nhắc khoản dự phòng.** | BCTC soát xét H1 trang in 5 (`src_r9/h1_p6.png`) | **Lặp/thêm khả dĩ**: kiểm toán viên không loại trừ được điều chỉnh liên quan môi trường |
| iv' | Note 36: HĐQT "has not had sufficient basis... to reliably assess the potential financial effects" của vụ án; "will... consider making additional recognition". Note 35: chi phí khôi phục đất thuê **không trích**, là nghĩa vụ tiềm tàng. | BCTC soát xét H1 trang in 44-45 (`src_r9/h1_p45.png`, `h1_p46.png`) | Theo chính DGC, **200 không phải ước tính tác động vụ án**. Tác động vụ án, nếu có, là phần **CỘNG THÊM** (T1) |
| v | Bộ Công an 17/03/2026: khởi tố theo Đ.221, 227, **235**, 14 bị can; "Đổ thải trái phép hàng triệu tấn chất thải, trên diện tích hàng chục hecta... tại KCN Tằng Loỏng". Đ.235 áp cho ông Đào Hữu Huyền và GĐ **Cty TNHH MTV Hóa chất Đức Giang – Lào Cai** (Nhân Dân, BNEWS 17/03). Tuổi Trẻ 23/07: TGĐ Lưu Bách Đạt và PTGĐ Phùng Trọng Tú bị khởi tố tội gây ô nhiễm môi trường. **Tính đến 15/08/2026, theo Báo Pháp luật 15/08: "chưa khởi tố pháp nhân".** **Tin tháng 10 CHƯA quét lại** (đang giao data-ops quét riêng). **Không tìm thấy** (tới các nguồn trên) con số thiệt hại môi trường, mức phạt, bồi thường, hay quyết định buộc khắc phục có số tiền; không tìm thấy kết luận điều tra/cáo trạng. | bocongan.gov.vn 17/03; nhandan.vn 17/03; tuoitre.vn 23/07; doanhnhan.baophapluat.vn 15/08 (qua WebFetch, gần nguyên văn) | **Chủ đề khớp** (xả thải ↔ dự phòng môi trường; lần trích đầu ở H1, sau khởi tố 17/03). **Quy mô và tính một lần: không phân định.** "Hàng triệu tấn" không có đơn giá xử lý nên không biết 200 tỷ đủ hay thiếu (tôi không tính). |
| v' | 331,324 tỷ "khắc phục hậu quả" là tiền **bị can và gia đình tự nguyện nộp** (Kenh14 dẫn VKSND, 23/06). VnExpress 13/08: "Gia đình cựu chủ tịch... sử dụng tiền cá nhân". TV HĐQT Phạm Duy Tùng: "không phải là con số thiệt hại cuối cùng" (Viettimes 13/08). | kenh14.vn 23/06; vnexpress.net 13/08; viettimes.vn 13/08 | Thiệt hại cuối cùng **còn mở** ⇒ không ủng hộ "một lần đã đủ" |
| v'' | ĐHĐCĐ 13/08: **diễn ý của báo** (doanhnhan.baophapluat.vn, không phải lời nguyên văn DGC): đánh giá rủi ro môi trường là vấn đề trọng điểm; doanh nghiệp đã chủ động trích lập dự phòng 100 tỷ đồng để triển khai các biện pháp xử lý. Các ý khác (bã xỉ phốt pho tiêu thụ hết; thạch cao có nhà máy xử lý, dự kiến mở rộng; "HĐQT chưa nhận được kết luận chính thức về sai phạm") dẫn từ mekongasean.vn: **chưa xác minh**. | doanhnhan.baophapluat.vn 15/08; mekongasean.vn (chưa xác minh) | Gắn với vụ án (c ở trên). Mở rộng xử lý thạch cao là chi phí/đầu tư **liên tục** nhưng không định lượng |
| vi | Lịch sử: số dư dự phòng 31/12/2025 = 0 (note 19 H1, đầu kỳ). Các năm trước: **chưa kiểm**. BCTN 2025 là PDF ảnh 58 trang, chưa đọc. | như i | Không phân định |
| vii | Tiền lệ cùng KCN Tằng Loỏng: DAP số 2 (Vinachem) bị phạt 2015-2018 nhiều lần (400 tr, 260 tr, 300 tr, 560 tr do vỡ đập hồ gyps, 150 tr) và bị buộc bồi thường dân (Thanh tra 01/06/2022). Formosa 2016 cam kết 500 tr USD **một lần** (Hanoi Times 01/07/2016). Không tìm thấy khoản dự phòng ở LAS; DPM/DCM/CSV/BFC chưa tra. | thanhtra.com.vn 01/06/2022; hanoitimes.vn 01/07/2016 | Lẫn lộn: sự cố gyps **lặp** (số nhỏ); bồi thường lớn thì **một lần**. Không suy được cho DGC |

**Kết luận bằng chứng.**

| Điều | Đã xác lập chưa | Căn cứ / còn thiếu gì |
|---|---|---|
| (a) Chủ đề "môi trường, xử lý chất thải" | **Có** | note 19 + phát biểu ĐHĐCĐ (diễn ý báo) |
| (b) Bản chất hữu hạn vs lặp | **CHƯA phân định**; nghiêng nhẹ-vừa hữu hạn | nhãn "restoration", phát biểu gắn vụ án vs chữ "production and business activities" và Q3 +100 |
| (c) Quy mô cuối cùng / "một lần đã đủ" | **CHƯA** | ước tính đã tăng một lần không giải thích; vụ án chưa kết luận; HĐQT tự nói chưa đủ cơ sở ước tính tác động vụ án |

Câu hỏi (b), (c) chỉ DGC trả lời được (§7).

## 4. Biên nền 2027-28: căn cứ tới đâu
- **r4 16,5/17,5%** có nguồn gốc là "giả định" ở r1/r2 (r2 REPORT bảng biên: "giả định"). r6 chỉ cho thấy nó **khớp** với ràng buộc cơ học giá vốn Q3 × 4 giữ phẳng (15,2/16,5%). Ràng buộc đó chính là R1, nên nó đã ngầm chứa dự phòng lặp. Theo cách nhìn giá vốn phẳng, nền r4 tương đương giá vốn 2027 thấp hơn Q3 × 4 (gồm dự phòng) khoảng **119 tỷ/năm** (`run_stdout_r9.txt`).
- **Quan sát có căn cứ (BCTC):**

  | Quý | Biên gộp | Ghi chú |
  |---|---|---|
  | Q1/26 | 23,0% | không dự phòng |
  | Q2/26 | 18,9% | ngoài dự phòng 23,0% [suy luận: dự phòng ở giá vốn] |
  | Q3/26 | 20,5% | ngoài dự phòng 24,6% |

  Cả ba quý đều đã gánh quặng nhập 100% (giải trình Q3) và S/NH3 cao.
- **Model:** biên 2027-28 giảm so với các quý thực vì giả định doanh thu 2027 = 9.261 (−6,2% so Q3 × 4) với giá vốn không giảm. Đây là hai giả định [UL] chồng nhau: giá P4 và giá vốn phẳng.
- **Bobby 28/10** (`kb/data_registry/market-state/sector_read_fertilizer_dap_20261028.md`):
  - Chi phí S về HƯỚNG giảm (trung vị TE ~4.900 CNY/t 01/2027, ~4.400 04/2027), nhưng MỨC giảm ít hơn.
  - NH3/khí tăng (TTF +63%) có thể bù lại.
  - Giá vốn BCTC trễ 1-2 quý.
  - Bobby không cho tỷ trọng S hay NH3 trong giá vốn DGC, nên **không dựng được cầu nối định lượng tới biên**.
- **BQ `ticker_financial.GPM_P0`** (`out_r9_gpm_hist_bq.csv`): 2019-20 khoảng 20-22%, 2024-25 khoảng 33-35%. Nhưng BQ ghi 2026Q1 = 28,7% và Q2 = 24,8%, **lệch** so với BCTC (23,0 / 18,9). Định nghĩa cột khác BCTC, nên **không dùng để định mức**.
- **Kết luận thẳng:** biên 2027-28 là **giả định, dải rộng**. Mỗi 1pp ≈ 1.420 đ/cp (A7: −2pp 29.345 … +2pp 35.017; `out_r9_margin_pp.csv`). Khoảng 15,2-20,7% đều có lý lẽ, không có số neo đáng tin. Câu hỏi dự phòng chỉ là **một trong ba** động lực biên cùng cỡ: dự phòng ±4,3pp, giá P4, và chi phí S/NH3/quặng.
- **Ghi chú r10:** r4 16,5% khi dự phòng hữu hạn tương đương giá vốn 2027 = 9.261 × (1 − 16,5%) = **7.733** vs run-rate Q3 bỏ dự phòng (nền R2) **7.452** ⇒ ngầm **~281 tỷ/năm** chi phí [UL] (đo: `run_stdout_r10.txt`; r9 ghi 119 là so với giá vốn Q3×4 gồm dự phòng, 7.852). Nền r4 vì vậy KHÔNG trung tính với câu hỏi dự phòng: nó đã chứa một khoản chi phí ngầm.

## 5. Dải cuối đối xứng theo hai nền biên (SỬA)
Không chọn base case. Nguồn: `out_r10_final_grid.csv`. Q4 ex-dự phòng (tách đúng). Hai cơ sở thuế hiển thị cùng lúc: **trước thuế / sau lá chắn 20% [UL, chưa xác minh khấu trừ]**.

| Cách đọc dự phòng | Nền biên r4 16,5/17,5 [UL] (ngầm ~281 tỷ/năm so với R2) | Nền biên R2 19,5/20,7 [UL: giá vốn Q3 bỏ dự phòng, phẳng] |
|---|---|---|
| N=0, không trích thêm (kể cả Q4) | **32.399** (B7 37.277) | **36.880** (B7 41.757) |
| 100 × 1 quý | 32.146 / 32.197 | 36.627 / 36.678 |
| 100 × 4 quý | 31.439 / 31.631 | 35.920 / 36.112 |
| 200 × 4 quý | 30.478 / 30.862 | 34.959 / 35.343 |
| 100 × 8 quý | 30.603 / 30.962 | 35.084 / 35.443 |
| 200 × 8 quý | **28.807 / 29.525** (B7 33.685 / 34.403) | **33.288 / 34.006** (B7 38.165 / 38.883) |
| Vĩnh viễn 100/quý (R1, model, nền Q4-ngầm r9) | 30.598 (B7 35.476) | |
| + nghĩa vụ vụ án pháp nhân 200 / 500 / 1.000 (T1; trừ thẳng 527 / 1.317 / 2.633, số học từ r9) | 31.872 / 31.082 / 29.766 | 36.353 / 35.563 / 34.247 |
| (tham chiếu r9, Q4 gồm ~100 ngầm) N=0 | 32.182 | 36.663 |

Mức bằng chứng cho mọi hàng: bản chất hữu hạn/lặp **chưa phân định** (§3), quy mô **chưa xác lập**. Hàng 200 × N chỉ là kịch bản, không có số nào công bố ủng hộ mức 200/quý.

**Cận có điều kiện (A7):**

| Cận | Trị số | Điều kiện |
|---|---|---|
| Dưới trong bảng | **28.807** (trước thuế) / 29.525 (sau lá chắn) | nền r4 **và** 200 × 8 quý: chồng hai giả định bi quan (ngầm 281 tỷ/năm [UL] + 8 quý × 200 [UL]) |
| Dưới, lặp vĩnh viễn | 30.598 | R1 |
| Dưới, kể cả nghĩa vụ vụ án 1.000 | 29.766 | nền r4, N=0 |
| Trên | **36.880** | không trích thêm **và** nền R2 |
| Ngoài cả hai | ±1.420/pp | biên tự thân |

Giá 32.900 nằm trong mọi dải trên. Không hàng nào được chọn làm base case ở đây.

## 6. P1 và HARD ABANDON
- **Nhãn P1** (user chọn): giữ. Không mua mới/không tăng; HARD ABANDON + time-stop 26/12/2026 và 26/03/2027 (r8 §6).
- **8 trigger T1-T8:** giữ nguyên chữ của r8 §6 (không đổi; chỉ ghi chú thêm).
- **Ghi chú T1 (không viết lại chữ):** vế "Q4 trích thêm ≥100 mà không thuyết minh" đã có tiền lệ ở Q3 (§3 ii), **nhưng** BCTC quý DGC nói chung không thuyết minh dự phòng (theo skeptic; mã 315, 316 cũng không thuyết minh), nên tiền lệ này **trọng số thấp**. **Cần nêu cho user biết:** mệnh đề "mà không thuyết minh" thực tế gần như luôn đúng nếu Q4 có trích, nên T1 gần bằng "Q4 trích thêm ≥100". Vế "xác nhận là nghĩa vụ/phạt pháp nhân": theo Pháp luật 15/08 chưa khởi tố pháp nhân (tính đến 15/08; tin tháng 10 chưa quét lại) và HĐQT nói chưa đủ cơ sở ước tính (note 36).

## 7. Câu hỏi mở
**Cho DGC, xếp theo tác động lên giá trị:**

1. **Bản chất và quy mô dự phòng môi trường.** Nghĩa vụ gì: khối lượng chất thải tồn đọng, địa điểm Tằng Loỏng? Tổng chi phí ước tính và lịch chi ra sao? Còn trích thêm không và tới quý nào? Có phải chi phí xử lý thường xuyên trong tương lai không? *Tác động: 0 tới −6.065 đ/cp (§2).*
2. **Chỉ tiêu KQKD.** 200 tỷ có nằm trong giá vốn không? Chi phí xử lý thạch cao/chất thải định kỳ sau 2026 (gồm phần mở rộng nhà máy thạch cao) là bao nhiêu mỗi năm, và hạch toán vào giá vốn hay capex? *Quyết định biên nền; mỗi 1pp = 1.420 đ/cp.*
3. **Mốc mở lại khai trường 25/19B bằng văn bản.** *B7 − A7 = 4.878 đ/cp.*
4. **Nghĩa vụ phát sinh từ vụ án cho pháp nhân/công ty con Lào Cai** (phạt, bồi thường, buộc khắc phục) và chi phí khôi phục đất thuê (note 35). *Mỗi 1.000 tỷ ≈ 2.633 đ/cp.*
5. **Thanh lý TSCĐ 332,3 tỷ:** bên mua là ai, có phải bên liên quan không? Đắk Nông 63,38 qua "giảm khác"; LCTT lệch 48,23. *Về số thì nhỏ (≤557 đ/cp), nhưng đây là cờ liêm chính.*
6. **Lộ trình gỡ ngoại trừ soát xét/kiểm toán** (phụ thuộc kết luận điều tra). *Không đo được bằng đ/cp; đây là cổng T5.*

**Cho user quyết / chưa giải quyết (mới ở r10):**
- **(i) T7 "Pháp nhân DGC bị khởi tố":** bị can Đ.235 là GĐ Cty TNHH MTV Hóa chất Đức Giang – Lào Cai (công ty con 100%). **Câu hỏi:** có cần ghi rõ T7 gồm công ty con không? User quyết; đang giao legal-vn xác nhận Đ.76 BLHS. Tôi **không đổi chữ** T7.
- **(ii) Khấu trừ thuế** của chi phí/dự phòng môi trường: legal-vn đang xác minh; §2/§5 hiển thị cả hai cơ sở.
- **(iii) 332,29 (LCTT mã 22 thanh lý TSCĐ 9T) vs 332,33 (phải thu ngắn hạn khác cuối 2025 trước phân loại lại)** — đã mở ảnh note 38 H1 (`/tmp/r10img/p46.png`, trang in 45 của `20260826-DGC-2026-Reviewed-interim...pdf`): note 38 "Comparative figures" ghi mã 136 *Other short-term receivables* trước điều chỉnh **332.334.512.496**, điều chỉnh **−330.919.324.902** sang mã 123 *Short-term held-to-maturity investments* (12.065.290.261.748 → 12.396.209.586.650), còn lại mã 135 = **1.415.187.594**. Kết quả: 332,33 là một số dư **có thật**, nhưng nó đã được **phân loại lại gần hết (330,92) sang đầu tư nắm giữ đến ngày đáo hạn** theo TT 99/2025 và 43/2026; chênh 332,29 vs 332,33 = ~0,04 tỷ. Điều này **không** chứng minh là cùng khoản với dòng thanh lý TSCĐ, cũng **không** loại trừ. **Chưa phân định.** Kết luận: chưa đủ cơ sở hỏi DGC "bên mua là ai" dựa trên sự trùng số này; câu hỏi 5 ở trên giữ như cũ (thanh lý TSCĐ không nêu bên mua), không bổ sung giả thuyết trùng. Việc đối chiếu mã 22 Q3 với số liệu gốc tôi lấy từ `MIKE_EXTRACT_BCTC_Q3_2026.md` (332,3, đánh dấu "?"), chưa mở lại ảnh LCTT Q3 ở r10.

## 8. Đính chính r8 (từ r9, vẫn đúng trừ chỗ r9 sai bên dưới)
Xem `../dgc_valuation_20261029_r9/REPORT.md` §8. Hai điều chỉnh của r10 lên §8 đó: (1) câu "100 tỷ/quý lặp vĩnh viễn = 1.516" → 6.065; (2) lập luận "VAS 18 ⇒ hữu hạn" dùng trong đính chính r8 KL1 bị bỏ (§9).

## 9. Đính chính r9 (r9 không sửa)
| # | r9 viết | Đính chính r10 |
|---|---|---|
| 1 | L7/L96/L186: "100 tỷ/quý lặp vĩnh viễn = 1.516 đ/cp; gấp 5,8 lần" | **SAI.** 100 tỷ/quý vĩnh viễn = **−6.065** (R1; `out_r9_perpetual.csv` x=100). 1.516 là mức 100 tỷ/NĂM. Gấp **~23×** 263, không 5,8× (§2). Bảng cạnh nhau: 1 quý 253 · 4 quý 960 · 8 quý 1.796 · vĩnh viễn 6.065 |
| 2 | L14-21, L79-86: bảng N trộn PV trước thuế với hàng vĩnh viễn đã qua model (có thuế) | Thêm cột sau lá chắn 20% [UL]; so cùng cơ sở: thô vĩnh viễn −7.406 trước thuế / −5.925 sau lá chắn vs model −6.065. Khấu trừ thuế chưa xác minh (§2) |
| 3 | L64-66: "không tính đôi, Q4 giống nhau ở hai cách đọc" | **SAI.** Q4 19% gồm ~100 ngầm = 217 đ/cp. R2 N=0 = 36.880 (r9: 36.663); r4 N=0 = 32.399; mọi hàng N≥1 của r9 trừ quý đầu hai lần. Tính lại (§2, §5; `out_r10_q4_split.csv`) |
| 4 | L8, L114: câu ĐHĐCĐ 13/08 trong ngoặc kép | Là **diễn ý của báo** (doanhnhan.baophapluat.vn), không phải lời DGC; bỏ ngoặc kép. Câu mekongasean: chưa xác minh |
| 5 | L114, L123: "xử lý tồn đọng" trong cột căn cứ | Bỏ (r9 đã ghi chưa xác nhận nguyên văn) |
| 6 | L112, L175: "tới 10/2026 chưa khởi tố pháp nhân" | Chỉ dựa nguồn ngày 15/08: "tính đến 15/08/2026, theo Báo Pháp luật"; tin tháng 10 chưa quét lại (data-ops đang quét) |
| 7 | L11/L30/L107/L175: "BCTC Q3 không thuyết minh dự phòng" như lý do (4) | Hạ trọng số: BCTC quý DGC nói chung không thuyết minh dự phòng (mã 315 162,5 tỷ, 316 cũng không; theo skeptic). T1 "mà không thuyết minh" gần bằng "Q4 trích thêm ≥100" — nêu cho user, không đổi chữ |
| 8 | L8, L105, L123, L157, L187: "VAS 18 + dự phòng ngắn hạn ⇒ hữu hạn"; R1 mức "thấp" | **Bỏ** lập luận (không phân biệt được). Thay bằng a-e §3. R1 "chưa loại trừ; nghiêng nhẹ-vừa hữu hạn". "Một lần" chưa xác lập. Ghi nhận r8→r9 lật chiều theo hướng nghi của user |
| 9 | L27, L153-167, L194: dải "Hữu hạn, nền r4" + "giữ nguyên A7" | Nền r4 ngầm ~281 tỷ/năm [UL] so với R2; cận dưới 28.590 = khoản này + 200×8 quý chồng nhau. Nay hiển thị đối xứng hai nền (§5); cận dưới mới 28.807/29.525. "Giữ nguyên A7" chỉ có nghĩa số mô hình không đổi, không phải chọn base case |
| 10 | Kết luận đầu r9 | Viết lại ≤12 dòng ở đầu file này |

**Giữ nguyên:** A7/B7 mô hình (32.182 / 37.060), R1 30.598, R2 36.663 (nay có thêm biến thể Q4 ex-dự phòng), phân rã 6.065 theo phương pháp (§1), CFO từng quý, ZaloPay, time-stop, T1-T8, nhãn P1.
