# DGC định giá VÒNG 9: xem lại cách xử lý dự phòng 200 tỷ

Job `Taylor_20261029_113514`. r1-r8 không sửa; mọi đính chính r8 ở §8. `model.py` giữ nguyên và tái lập r8: **A7 32.182 / B7 37.060 / A7_R1 30.598 / A7_R2 36.663** (assert trong `r9_calc.py`). Bảng mới: `r9_calc.py` → `run_stdout_r9.txt`, `out_r9_*.csv`. READ-ONLY, không phải khuyến nghị đặt lệnh. Đơn vị: tỷ đồng; đ/cp. **[UL]** = giả định; **[suy luận]** = rút ra bằng loại trừ hoặc theo chuẩn mực, không phải nguồn nói thẳng. BCTC Q3 CHƯA soát xét. Luật pháp lý 27/09: chỉ WARNING. Giá tham chiếu 32.900 (28/10). Nhãn **P1** (user đã chọn) giữ nguyên.

## Kết luận (≤12 dòng)
1. **Khoản 200 tỷ KHÔNG gây ra chênh 6.065 đ/cp giữa R1 và R2.** Cả R1 lẫn R2 đều đã trừ 200 như một khoản nợ (~541 đ/cp mỗi bên). Toàn bộ 6.065 đến từ giả định của R1 rằng **chi phí 100 tỷ/quý (400 tỷ/năm) tồn tại vĩnh viễn**. Giả định đó hạ biên gộp 4,3pp và được vốn hoá trong cả năm phương pháp: SOTP +1.880 · DCF +1.816 · PE DGC +794 · PE peer +818 · P/B +756 (`out_r9_decomp_R2_R1.csv`).
2. **Không tìm thấy tính đôi.** R1 trừ 200 đã trích (chi trong tương lai) và cộng 400/năm chi phí MỚI; R2 bỏ 400 khỏi biên và chỉ trừ 200. Có **một sai sót thật ở r8**: câu "mỗi 100 tỷ/quý = 263 đ/cp" là con số của một lần trừ 100 tỷ. Nếu 100 tỷ/quý lặp vĩnh viễn thì mất **1.516 đ/cp**, gấp 5,8 lần.
3. **Giả định "lặp vĩnh viễn" của R1 mâu thuẫn với cách DGC ghi sổ.** Khoản này là *dự phòng NGẮN HẠN* (mã 322). VAS 18 không cho trích dự phòng cho chi phí hoạt động tương lai [suy luận theo chuẩn mực]. Tại ĐHĐCĐ 13/08, DGC nói đã "chủ động trích lập dự phòng 100 tỷ đồng cho việc xử lý môi trường". Cả hai điểm nghiêng về một nghĩa vụ **hữu hạn**. Mức bằng chứng: vừa.
4. **"Chỉ một lần" thì CHƯA xác lập được.** Có bốn lý do:
   - Q3 trích thêm 100, tức ước tính đã tăng.
   - BCTC Q3 **không có thuyết minh dự phòng**, và văn bản giải trình Q3 không nhắc tới khoản này.
   - Note 36 (soát xét H1): HĐQT "chưa đủ cơ sở" để ước tính tác động tài chính của vụ án.
   - Note 35: chi phí hoàn trả mặt bằng đất thuê **chưa trích**.
5. **Mức trích thêm còn lại là câu hỏi cho DGC.** Đối chiếu trên nền R2 (`out_r9_finite_N.csv`, PV, chưa trừ lá chắn thuế):

   | Kịch bản trích thêm | Giảm |
   |---|---|
   | 100 tỷ × 4 quý | −960 |
   | 100 tỷ × 8 quý | −1.796 |
   | 200 tỷ × 8 quý | −3.592 |
   | Lặp vĩnh viễn | −6.065 |
6. **Biên gộp 2027-28 nặng ký hơn câu hỏi dự phòng.** Mỗi 1pp biên ≈ **1.420 đ/cp**. Biên nền r4 16,5/17,5% là **giả định [UL]** có từ r1, chỉ được "khớp" với ràng buộc cơ học giá vốn giữ phẳng. Các bằng chứng khác (BQ, Bobby) không cho ra một mức cụ thể. Dải 15,2-20,7% là dải giả định, không phải dải ước lượng.
7. **Dải A7 theo cách đọc biên (§5; không chọn base case):**

   | Cách đọc | A7 |
   |---|---|
   | Hữu hạn, nền r4 | **32.182 → 30.261** (thêm 200 × 4 quý) → 28.590 (thêm 200 × 8 quý) |
   | Hữu hạn, nền R2 | **36.663 → 33.071** |
   | Lặp vĩnh viễn (R1) | **30.598** |
8. **Nhận định của user, tách hai vế:** "liên quan xả thải" có căn cứ vừa về chủ đề và thời điểm; "chỉ một lần" chưa có căn cứ. P1 giữ. 8 trigger HARD ABANDON giữ nguyên chữ. T1 không đổi chữ; tuy vậy mẫu "trích mà không thuyết minh" **đã xảy ra một lần ở Q3** (§6).
9. **Đính chính r8 ở §8**, gồm: con số 263 đ/cp; cách gọi R1 là base case; chữ "thường xuyên" r8 tự thêm vào note 19; chi tiết 331 tỷ khắc phục là tiền của cá nhân, không phải của DGC.

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

**Kiểm tính đôi theo từng phương pháp:**

| | R1 | R2 | Tính đôi? |
|---|---|---|---|
| SOTP / DCF / PE / P/B | trừ 200 qua cash_adj (nợ đã ghi nhận, tiền sẽ chi) + biên đã gồm 400/năm chi phí **mới** | trừ 200; biên không gồm 400 | **Không.** 200 là chi phí Q2-Q3 đã hạch toán vào LN 2026 thực; LN 2026 không đi vào định giá, trừ q4_core. 400/năm của R1 là các lần trích **tương lai**. |
| P/B | 200 được cộng lại vào VCSH lõi (`extras_book`) để không bị trừ hai lần | như R1 | **Không** (đã xử lý đúng) |
| Cầu Q4/2026 (q4_core) | biên Q4 cơ sở 19,0% [UL], **không dịch** theo R1/R2 | như R1 | Không tính đôi. Có một điểm chưa nhất quán: Q4 không rõ có gồm dự phòng hay không. Ảnh hưởng nhỏ (một quý) và giống nhau ở hai cách đọc. |

**Ghi chú về chữ "R1 lặp ~100/quý":**
- Biên R1 15,2% thấp hơn **cả** biên Q3 thực tế 20,5% đã gồm dự phòng.
- Lý do: model hạ doanh thu 2027 xuống 9.261 (so với Q3 × 4 = 9.878, tức −6,2%; P4 4.150 $/t) nhưng giữ giá vốn phẳng.
- Như vậy 15,2% = dự phòng lặp **cộng** doanh thu giảm mà giá vốn không giảm. Chỉ phần đầu là câu hỏi dự phòng.
- Ở doanh thu Q3 × 4: R1 = 20,5%, R2 = 24,6%.

## 2. Độ nhạy theo số quý còn trích thêm N và mức trích mỗi quý
Đây là **bảng phụ thuộc, không có base case**. Nguồn: `out_r9_finite_N.csv`, `out_r9_perpetual.csv`.
- Nền: R2 (36.663). Ke = 14,9%. Quý j chi tại t = 0,17 + (j−0,5)/4 năm tính từ 29/10 [UL thời điểm chi].
- Không tính lá chắn thuế (bảo thủ). Khả năng khấu trừ thuế của dự phòng chưa xác minh.

| N quý trích thêm | 50/quý | 100/quý | 200/quý |
|---|---|---|---|
| 0 | 36.663 | 36.663 | 36.663 |
| 1 | 36.537 (−126) | 36.410 (−253) | 36.158 (−505) |
| 2 | 36.415 | 36.166 (−497) | 35.669 |
| 4 | 36.183 | 35.703 (−960) | 34.742 (−1.921) |
| 8 | 35.765 | 34.867 (−1.796) | 33.071 (−3.592) |
| **Lặp vĩnh viễn** (qua model: thuế lõi, MI, bội số) | 33.631 (−3.032) | **30.598 (−6.065) = R1** | 24.534 (−12.129) |

- Mức giảm cộng thẳng vào bất kỳ nền biên nào, vì là trừ tiền (xem §5). Nếu dự phòng được khấu trừ thuế 20%, mọi số ở hàng hữu hạn nhỏ đi 20% (bảng thứ hai trong CSV).
- **Mỗi 100 tỷ, đo theo cơ sở:**

  | Cơ sở | đ/cp |
  |---|---|
  | Trừ một lần | 263 (danh nghĩa) |
  | Trích thêm 1 quý (PV) | 253 |
  | 100/quý × 4 quý | 960 |
  | 100/quý lặp vĩnh viễn | **1.516** (= 6.065/4; model tuyến tính: 50 → 3.032, 200 → 12.129) |

  r8 viết "263 đ/cp mỗi 100 tỷ/quý" và dùng câu đó để gọi khoản này là "nhỏ". Câu đó **chỉ đúng cho lần trích một lần**.

## 3. Bằng chứng một lần hay lặp lại
Mỗi dòng ghi nguồn và hướng mà nó ủng hộ.

| # | Bằng chứng | Nguồn | Ủng hộ |
|---|---|---|---|
| i | Note 19 "Short-term provisions": *Provision for environmental restoration costs*. Đầu kỳ 0; **tăng 100.000.000.000**; **giảm "-"** (chưa chi đồng nào trong H1); cuối kỳ 100 tỷ. Chú thích (*): "best estimate of the future expected expenses in connection with environmental management and treatment arising from the Group's production and business activities. Actual expenses incurred may differ". | BCTC soát xét H1/2026, trang in 32 (ảnh `source_pages_h1/h1_p33.png`) | **Hữu hạn** [suy luận]. Là dự phòng *ngắn hạn* (chi trong 12 tháng) cho chi phí đã ước tính. Theo VAS 18 thì phải có nghĩa vụ hiện tại từ sự kiện đã xảy ra, không trích cho chi phí vận hành tương lai. Chữ "arising from production" **không** nói là thường xuyên. Câu "actual may differ" nghĩa là quy mô chưa chắc. |
| i' | Bảng cân đối H1, mã 322 = 100.000.000.000; đầu năm trống | BCTC soát xét H1, trang in 7 (`src_r9/h1_p8.png`) | Số dư 31/12/2025 = 0 |
| ii | **BCTC Q3 không có thuyết minh dự phòng.** Thuyết minh nhảy từ note 15 (thuế), 16 (phải trả khác), 17 (vay ngắn hạn) sang 18 (quỹ khen thưởng, phúc lợi). Chỉ có mã 322 = 200 trên bảng cân đối và dòng LCTT "dự phòng +199,95" của 9T. | BCTC Q3, trang in 32-34 (`../dgc_valuation_20261027_r6/source_pages/p33-p35.png`) | **Không phân định.** Nhưng là khoản +100 thứ hai **không được giải thích** |
| ii' | Văn bản giải trình Q3 (12/2026/CV-KT-DGC, 28/10) chỉ giải thích LN giảm bằng: doanh thu −12%; S, điện, than cốc, NH3 tăng; khai trường 25 dừng nên phải dùng quặng nhập/mua ngoài. **Không nhắc dự phòng.** | `/tmp/dgcpdf/20261028-DGC-Announcement-...pdf` trang 2-3 (`src_r9/q3expl_p2.png`) | Không phân định |
| iii | **Chỉ tiêu KQKD** [suy luận loại trừ]. 9T: chi phí khác = H1 13,95 + Q3 38,42 = 52,4 (<200). Note 28 QLDN 9T gồm nhân viên 83,4 · khấu hao 22,1 · dịch vụ mua ngoài 29,1 · khác 20,1, không dòng nào chứa được 100. Note 27 bán hàng 9T, dòng "khác" 52,2. Note 26 tài chính: lãi vay + chênh lệch tỷ giá. Note 24 giá vốn chỉ có **một dòng** 5.558,26. ⇒ 200 gần như chắc nằm trong **giá vốn**. | BCTC Q3 trang in 38-39 (`p39.png`, `p40.png`); KQKD H1 trang in 8 (`src_r9/h1_p9b.png`) | Không có nguồn nói thẳng; chia nhỏ ra nhiều dòng về số học là có thể nhưng không hợp lý |
| iv | Soát xét H1 (UHY, 995/2026/UHY-BCSX, 26/08): **cơ sở ngoại trừ** = vụ việc "natural resource exploitation, environment, and accounting" còn đang điều tra; không đủ bằng chứng để xác định có cần điều chỉnh khoản mục nào không. **Không nhắc khoản dự phòng.** | BCTC soát xét H1 trang in 5 (`src_r9/h1_p6.png`) | **Lặp/thêm khả dĩ**: kiểm toán viên không loại trừ được điều chỉnh liên quan môi trường |
| iv' | Note 36: HĐQT "has not had sufficient basis... to reliably assess the potential financial effects" của vụ án; "will... consider making additional recognition". Note 35: chi phí khôi phục đất thuê **không trích**, là nghĩa vụ tiềm tàng. | BCTC soát xét H1 trang in 44-45 (`src_r9/h1_p45.png`, `h1_p46.png`) | Theo chính DGC, **200 không phải ước tính tác động vụ án**. Tác động vụ án, nếu có, là phần **CỘNG THÊM** (T1) |
| v | Bộ Công an 17/03/2026: khởi tố theo Đ.221, 227, **235**, 14 bị can; "Đổ thải trái phép hàng triệu tấn chất thải, trên diện tích hàng chục hecta... tại KCN Tằng Loỏng". Đ.235 áp cho ông Đào Hữu Huyền và GĐ **Cty TNHH MTV Hóa chất Đức Giang – Lào Cai** (Nhân Dân, BNEWS 17/03). Tuổi Trẻ 23/07: TGĐ Lưu Bách Đạt và PTGĐ Phùng Trọng Tú bị khởi tố tội gây ô nhiễm môi trường. Báo Pháp luật 15/08: "chưa khởi tố pháp nhân". **Không tìm thấy** con số thiệt hại môi trường, mức phạt, bồi thường, hay quyết định buộc khắc phục có số tiền. Không tìm thấy kết luận điều tra hay cáo trạng (tới 10/2026). | bocongan.gov.vn 17/03; nhandan.vn 17/03; tuoitre.vn 23/07; doanhnhan.baophapluat.vn 15/08 (qua WebFetch, gần nguyên văn) | **Chủ đề khớp** (xả thải ↔ dự phòng môi trường; lần trích đầu ở H1, sau khởi tố 17/03). **Quy mô và tính một lần: không phân định.** "Hàng triệu tấn" không có đơn giá xử lý nên không biết 200 tỷ đủ hay thiếu (tôi không tính). |
| v' | 331,324 tỷ "khắc phục hậu quả" là tiền **bị can và gia đình tự nguyện nộp** (Kenh14 dẫn VKSND, 23/06). VnExpress 13/08: "Gia đình cựu chủ tịch... sử dụng tiền cá nhân". TV HĐQT Phạm Duy Tùng: "không phải là con số thiệt hại cuối cùng" (Viettimes 13/08). | kenh14.vn 23/06; vnexpress.net 13/08; viettimes.vn 13/08 | Thiệt hại cuối cùng **còn mở** ⇒ không ủng hộ "một lần đã đủ" |
| v'' | ĐHĐCĐ 13/08: "Công ty đã chủ động trích lập dự phòng 100 tỷ đồng cho việc xử lý môi trường"; bã xỉ phốt pho đã tiêu thụ hết; thạch cao có nhà máy xử lý, dự kiến mở rộng; "HĐQT chưa nhận được kết luận chính thức về sai phạm". Câu "xử lý toàn bộ lượng chất thải rắn còn tồn đọng" chỉ là **diễn ý từ snippet, chưa xác nhận nguyên văn**. | mekongasean.vn (ĐHĐCĐ 13/08); doanhnhan.baophapluat.vn 15/08 | **Nghiêng hữu hạn** (xử lý tồn đọng), mức vừa. Mở rộng xử lý thạch cao là chi phí/đầu tư **liên tục** nhưng không định lượng |
| vi | Lịch sử: số dư dự phòng 31/12/2025 = 0 (note 19 H1, đầu kỳ). Các năm trước: **chưa kiểm**. BCTN 2025 là PDF ảnh 58 trang, chưa đọc. | như i | Không phân định |
| vii | Tiền lệ cùng KCN Tằng Loỏng: DAP số 2 (Vinachem) bị phạt 2015-2018 nhiều lần (400 tr, 260 tr, 300 tr, 560 tr do vỡ đập hồ gyps, 150 tr) và bị buộc bồi thường dân (Thanh tra 01/06/2022). Formosa 2016 cam kết 500 tr USD **một lần** (Hanoi Times 01/07/2016). Không tìm thấy khoản dự phòng ở LAS; DPM/DCM/CSV/BFC chưa tra. | thanhtra.com.vn 01/06/2022; hanoitimes.vn 01/07/2016 | Lẫn lộn: sự cố gyps **lặp** (số nhỏ); bồi thường lớn thì **một lần**. Không suy được cho DGC |

**Kết luận bằng chứng.** Bằng chứng tách được ba điều:

| Điều | Đã xác lập chưa | Căn cứ / còn thiếu gì |
|---|---|---|
| (a) Chủ đề "môi trường, xử lý chất thải" | **Có** | note 19 + phát biểu ĐHĐCĐ |
| (b) Bản chất | Nghiêng **nghĩa vụ hữu hạn** hơn chi phí vận hành vĩnh viễn, mức **vừa** | phân loại dự phòng ngắn hạn + VAS 18 + "xử lý tồn đọng" |
| (c) Quy mô cuối cùng / "một lần đã đủ" | **CHƯA** | ước tính đã tăng một lần không giải thích; vụ án chưa kết luận; HĐQT tự nói chưa đủ cơ sở ước tính tác động vụ án |

Câu hỏi (c) chỉ DGC trả lời được (§7).

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

## 5. Dải cuối theo hai cách đọc dự phòng
Không chọn base case. Nguồn: `out_r9_final_grid.csv`. Trừ hữu hạn là PV, chưa tính lá chắn thuế.

| Cách đọc dự phòng | Mức bằng chứng | Nền biên r4 16,5/17,5 [UL] | Nền R2 19,5/20,7 [UL: giá vốn Q3 bỏ dự phòng, phẳng] |
|---|---|---|---|
| Hữu hạn, không trích thêm (N=0) | vừa (bản chất) / **chưa** (quy mô) | **32.182** (B7 37.060) | **36.663** (B7 41.539) |
| Hữu hạn, 100 × 4 quý | như trên | 31.222 | 35.703 |
| Hữu hạn, 200 × 4 quý | như trên | 30.261 | 34.742 |
| Hữu hạn, 200 × 8 quý | như trên | 28.590 (B7 33.468) | 33.071 |
| Lặp vĩnh viễn 100/quý (R1) | **thấp**: trái với phân loại dự phòng ngắn hạn và phát biểu ĐHĐCĐ | 30.598 (R1 trên nền giá vốn phẳng; B7 35.476) | |
| + nghĩa vụ vụ án pháp nhân 200 / 500 / 1.000 (T1) | chưa có số công bố; chưa khởi tố pháp nhân | 31.655 / 30.865 / **29.549** | 36.136 / 35.346 / 34.030 |

**Cận có điều kiện (A7):**

| Cận | Trị số | Điều kiện |
|---|---|---|
| Dưới, hữu hạn ≤8 quý × 200 | **28.590** | biên r4 |
| Dưới, lặp vĩnh viễn | 30.598 | — |
| Dưới, kể cả nghĩa vụ vụ án 1.000 | 29.549 | biên r4 |
| Trên | **36.663** | dự phòng không trích thêm **và** biên R2 |
| Ngoài cả hai | ±1.420/pp | biên tự thân |

Giá 32.900 nằm trong mọi dải.

## 6. P1 và HARD ABANDON
- **Nhãn P1** (user chọn): giữ. Không mua mới/không tăng; HARD ABANDON + time-stop 26/12/2026 và 26/03/2027 (r8 §6).
- **8 trigger T1-T8:** giữ nguyên chữ của r8 §6.
- **T1 không viết lại.** Ghi chú cập nhật bằng chứng: vế "Q4 trích thêm ≥100 mà không thuyết minh" có tiền lệ, vì Q3 đã trích +100 mà không có thuyết minh (§3 ii). Vế "xác nhận là nghĩa vụ/phạt pháp nhân": tới 10/2026 chưa khởi tố pháp nhân (Pháp luật 15/08), và HĐQT nói chưa đủ cơ sở ước tính (note 36).

## 7. Câu hỏi mở cho DGC, xếp theo tác động lên giá trị
1. **Bản chất và quy mô dự phòng môi trường.** Nghĩa vụ gì: khối lượng chất thải tồn đọng, địa điểm Tằng Loỏng? Tổng chi phí ước tính và lịch chi ra sao? Còn trích thêm không và tới quý nào? Có phải chi phí xử lý thường xuyên trong tương lai không? *Tác động: 0 tới −6.065 đ/cp (§2).*
2. **Chỉ tiêu KQKD.** 200 tỷ có nằm trong giá vốn không? Chi phí xử lý thạch cao/chất thải định kỳ sau 2026 (gồm phần mở rộng nhà máy thạch cao) là bao nhiêu mỗi năm, và hạch toán vào giá vốn hay capex? *Quyết định biên nền; mỗi 1pp = 1.420 đ/cp.*
3. **Mốc mở lại khai trường 25/19B bằng văn bản.** *B7 − A7 = 4.878 đ/cp.*
4. **Nghĩa vụ phát sinh từ vụ án cho pháp nhân/công ty con Lào Cai** (phạt, bồi thường, buộc khắc phục) và chi phí khôi phục đất thuê (note 35). *Mỗi 1.000 tỷ ≈ 2.633 đ/cp.*
5. **Thanh lý TSCĐ 332,3 tỷ:** bên mua là ai, có phải bên liên quan không? Đắk Nông 63,38 qua "giảm khác"; LCTT lệch 48,23. *Về số thì nhỏ (≤557 đ/cp), nhưng đây là cờ liêm chính.*
6. **Lộ trình gỡ ngoại trừ soát xét/kiểm toán** (phụ thuộc kết luận điều tra). *Không đo được bằng đ/cp; đây là cổng T5.*

## 8. Đính chính r8 (r8 không sửa)
- **r8 §1 "Mỗi 100 tỷ/quý = 263 đ/cp = 0,8% giá" → SAI.** 263 là trừ một lần 100 tỷ. Nếu lặp mỗi quý vĩnh viễn thì mất **1.516 đ/cp**; nếu lặp 4 quý thì mất 960. Câu "giá trị nhỏ" ở r8 §3B cũng sai theo, khi khoản này được đọc là lặp.
- **r8 KL1 và §1 gọi R1 là "base case nghiêm túc"; lý do "hai quý liên tiếp đúng 100, bản chất vận hành, không có dấu hiệu một lần" → bỏ.** Hai lần trích cho thấy ước tính đã tăng, không cho thấy chi phí vĩnh viễn. Khoản này được phân loại là dự phòng ngắn hạn (VAS 18) và DGC phát biểu "chủ động trích lập... cho việc xử lý môi trường" tại ĐHĐCĐ; cả hai trái với "vĩnh viễn". Nay **không có base case**; dùng bảng N (§2, §5).
- **r8 KL2 và §2 "BCTC mô tả nó là chi phí xử lý thường xuyên" → SAI chữ.** Note 19 viết "future expected expenses... arising from the Group's production and business activities", không có chữ "thường xuyên/recurring".
- **r8 §2 "Q3 +100 là cùng khoản (note Q3 chưa đọc lại)" → đã đọc.** BCTC Q3 **không có** thuyết minh dự phòng (p33-p35). Việc coi là cùng khoản chỉ suy từ cùng mã 322.
- **r8 §2, bảng mốc "Không trả lời → giữ R1" → đổi.** Nếu DGC không trả lời thì giữ **bảng N**, không mặc định R1. Ghi cờ "không minh bạch" như r8.
- **r8 §2 "Liên quan vụ án → A7 ≤30.071"** được tính trên R1. Trên nền r4, cộng nghĩa vụ 200/500/1.000: 31.655 / 30.865 / 29.549.
- **r8 §4 "Q1 −1.093 (RE-DO 23/07 đã coi là phần lớn một lần: 331 tỷ khắc phục…)" → căn cứ sai.** Theo VnExpress 13/08 và Kenh14 23/06, 331 tỷ là tiền **cá nhân** bị can và gia đình nộp, không phải tiền DGC. Giải thích CFO Q1 âm phải dựa vào vốn lưu động (tồn kho H1 −788,1). Kết luận "⚠ chưa đạt, 0,82×" của r8 không đổi, vì không dựa vào 331.
- **r8 KL1 "giá nằm TRÊN A7, không có biên an toàn ở cận dưới"** chỉ đúng dưới R1 và nền r4. Dải đúng ở §5.
- **Giữ nguyên:** A7/B7, PE lõi, tài khoản, CFO từng quý, ZaloPay, time-stop, T1-T8.
