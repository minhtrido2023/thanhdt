# TV1 (EVNPECC1) — DD redo VÒNG 3 · giá đóng cửa 06/11/2026 · job `Taylor_20261108_142024`

> Tài liệu nghiên cứu, giữ trung dung. Áp `TOP5_CORRECTIONS_20261108.md` §TV1 (user duyệt) sau khi **kiểm từng điểm bằng calc** + `STANDARD_r2.md`.
> - Số liệu: `calc/model_tv1_r3_out.txt|json`, chạy `$DNA_PYEXE -I calc/model_tv1_r3.py` (2 lần trùng byte: out.json, out.txt, LOCK).
> - SUMMARY: `calc/make_summary_r3.py` → `SUMMARY.json` (2 lần trùng byte); bản r2 backup `SUMMARY_r2.json`.
> - LOCK: `calc/LOCK_r3_md5.txt` (ddr2, wpct, ddg2, giá 06/11 + SQL, model r3, lõi `tv1_v2_core.py` — md5 không đổi so r2, CSV quý BQ, deposit/cctg + events) và `calc/LOCK_r3_summary_md5.txt`.
> - Lõi INTRINSIC_v2 02/11 không sửa. Bản r2 giữ nguyên: `REPORT_r2.md`.

## 0. Kết luận
| Sau CK 4,21% @5 tỷ | r3 | r2 |
|---|---|---|
| **Tâm** (kỳ vọng lưới) | **16.740** | 15.379 |
| P50 kết cục | 16.150 | 15.532 |
| Giá trị tại tham số trung tâm (520 · tư vấn 11% · Q187,5 · 2027 · VLĐ 49%) | 19.126 | 19.165 |
| **P10 / P90 kết cục** | **8.823 / 25.179** (min 3.012, max 43.218; n = 540) | 4.693 / 24.544 |
| Giá tham chiếu | **20.400** (đóng cửa 06/11) | 19.600 (04/11) |

- Giá cao hơn tâm **21,9%** (tâm thấp hơn giá 17,9%). **74,6% trọng số kết cục nằm dưới giá.** Nhãn **TRONG vùng**, không đổi so với r2. Định nghĩa vùng (P10–P90) cũng không đổi.
- Ngưỡng nhãn: **DƯỚI vùng** khi giá < 8.823; **TRÊN vùng** khi giá > 25.179.
- Tâm tăng +1.361 (+8,9%) so với r2. Toàn bộ mức tăng đến từ việc bỏ nhánh truy thu khỏi base (§1). Phần đổi dữ liệu giá chỉ làm tâm giảm 32.
- P10 tăng từ 4.693 lên 8.823. P10 của r2 là sản phẩm của các kết cục tự mâu thuẫn. P10 r3 do PPA 340 (55% trọng số quanh P10) và 440 (32%) quyết định, cùng biên tư vấn 5–8%. Không còn kết cục nào chạm sàn 0 (r2 có 5,5%, toàn bộ thuộc nhánh truy thu).
- Tâm (16.740) cao hơn P50 (16.150) vì đuôi phải: PPA 949/600 cộng tư vấn 14%. Tham số trung tâm 19.126 cao hơn tâm vì 520 > PPA kỳ vọng 509, và có 50% xác suất biên tư vấn ≤ 8%.
- **Giá ngụ ý:** để tâm bằng 20.400 cần giá PPA ròng phẳng từ 2027 khoảng **623 đ/kWh** (tư vấn ở mức kỳ vọng), hoặc **547** (tư vấn 11% vĩnh viễn), hoặc PPA 335 đi kèm tư vấn 14% vĩnh viễn. Mức duy nhất có văn bản là **340**. Dải 500–600 chỉ là lời lãnh đạo, chưa kiểm được bản gốc.

## 1. Kiểm từng đính chính (TOP5_CORRECTIONS §TV1)
| # | Đính chính | Kết quả kiểm | Bằng chứng |
|---|---|---|---|
| 1 | Nhánh truy thu nhân chéo độc lập với PPA ⇒ kết cục tự mâu thuẫn | **ĐÚNG** — áp | Truy thu chỉ xảy ra khi bậc 2018 ràng buộc, và khi đó PPA tương lai = 340. Calc tái lập số skeptic: S1k **16.571** / P10 8.414 (skeptic 16.570 / 8.420); S2k **15.702** / P10 3.515 (skeptic 15.734 / 3.522). Phần lệch nhỏ do CK mới 4,21% so với 4,02%. Câu r2 "P10 31% do truy thu" chỉ đúng trong cơ chế sai. |
| 2 | Truy thu không có văn bản ⇒ ra khỏi base | **ĐÚNG** — áp | Không có văn bản nào đòi truy thu. EVN trả khoảng 949 suốt 2022–25 (BCTC đã kiểm toán). Core v2 dòng [N1] đã ghi "KHÔNG vào tâm". r2 đưa vào mà không có thông tin mới. |
| 3 | "Đã ký" vs "dự thảo" HĐ 2018 | **ĐÚNG — r2 §1 viết "đã ký" là SAI** | `tv1_sb5_ppa_price_20261013/README.md` dòng 17–31: "Hợp đồng sửa đổi, bổ sung số 05" là **dự thảo**, được EVN chấp thuận (NQ 286/NQ-HĐTV 06/08/2018) và Cục ĐTĐL chấp thuận (1374/ĐTĐL-GP 24/08/2018). Chưa thấy bản ký. Phụ lục PPA hiện hành: KHÔNG TÌM THẤY. Thực tế giá không hạ năm 2022 ⇒ "phụ lục 05 hoặc không ký như dự thảo, hoặc mốc đã lùi". `LEGAL_PPA_20261102` dòng 6–7: "cần văn bản gốc". |
| 4 | Thiếu WARNING VnExpress "13 công ty" | **ĐÚNG** — thêm §6.2 | REPORT 02/11 §7 |
| 5a | KTPL 20% chỉ dựa trên 1 năm ⇒ độ nhạy 15/10% | **SAI hướng** — giữ 20% | BCTC đo 3 năm: FY2023 30,93/75,64 = **40,9%** · FY2024 17,24/87,50 = **19,7%** · FY2025 30,10/150,20 = **20,0%** (BCTC HN FY2025 TM17, TM18a, TM18c; H1/2026 TM22). Quỹ trích theo **1,5 tháng lương** (TM18c), không theo % lợi nhuận ⇒ khi LN giảm vì hạ PPA, tỷ lệ có xu hướng TĂNG. Không có cơ sở hạ xuống 10–15%. Độ nhạy vẫn báo đủ: 10% → 19.256 · 15% → 17.998 · 25% → 15.483. |
| 5b | Biên tư vấn lịch sử: Σ(DT quý × EBITM_P0 TTM) | **ĐÚNG** — core sai 2022–23 | EBITM_P0 là số TTM (dictionary 08/11). Cách đúng: TTM Q4 × DT năm. Kết quả: 2022 **−19%…−17% → +2%…+4%**; 2023 −2%…0% → **+4%…+7%**; 2024 (+4…+6%) và 2025 (+8…+10%) không đổi. Câu "biên âm 2022–23" trong core/r2 là SAI. Biên 5% là mức điển hình 2022–24, không phải đáy. Lưới không đổi: xác suất các kịch bản tư vấn [UL] lấy từ SKEPTIC_BLIND B3, không suy từ chuỗi này. |
| 6 | Dẫn chiếu §2 thay vì §2.5; giá ngụ ý; plan SELL | **ĐÚNG** — áp | TV1 là scandal cá nhân (nhóm a) ⇒ xét theo §2. Giá ngụ ý calc ra 547–623, skeptic ra 558–631. |

> ⚠️ **Cảnh báo KTPL (đính chính 5a, bổ sung sau skeptic):** (i) quỹ KTPL được trích theo ~1,5 tháng lương (gần như cố định theo VND, TM18c) nhưng mô hình dùng **20% × LN** ⇒ ở nhánh PPA thấp (LN giảm mạnh) mô hình **trừ KTPL thiếu**, tức **tâm có thể hơi cao** (chiều lệch chưa đo, không đổi con số headline). (ii) Số FY2023 **40,9%** là phép trừ 48,93 − 18,0 (TM18a) nên **có thể lẫn quỹ thưởng ban điều hành**; không dùng 40,9% làm cơ sở cho tỷ lệ chuẩn.

## 2. Bridge r2 → r3
| Bước | Tâm | P10 | P90 | Lý do |
|---|---|---|---|---|
| r2 (giá 19.600 @04/11, CK 4,02%) | 15.379 | 4.693 | 24.544 | — |
| Dữ liệu giá 06/11, giữ cơ chế r2 (CK 4,21%) | 15.347 | 4.684 | 24.494 | Cửa sổ thanh khoản mới. r không đổi (13,5%). |
| Bỏ truy thu khỏi base, dồn trọng số 0,10 về "đúng 2027" | **16.740** | **8.823** | **25.179** | Đính chính 1–3 |
| KTPL giữ 20% (không áp 15/10% vào base) | 16.740 | — | — | Đính chính 5a bị bác bằng dữ liệu |

Vì sao dồn trọng số về "đúng 2027" chứ không về "lùi": lãnh đạo nêu mốc 2027 và đây là kịch bản trung tâm. Chiều lùi giữ nguyên 0,15/0,05. Cơ sở của chiều lùi là dữ liệu quan sát được: mốc 2022 của dự thảo 2018 đã trôi ≥ 5 năm.

> ⚠️ **Cảnh báo cách chia trọng số (sau skeptic):** trọng số 0,10 của nhánh truy thu bị dồn **toàn bộ** vào nhánh "đúng 2027" (nhánh có giá trị thấp nhất), thay vì chuẩn hoá theo tỷ lệ 0,80/0,15/0,05. Chuẩn hoá theo tỷ lệ cho tâm cao hơn khoảng **46 đ** (S1k 16.571 so S1 16.525, cùng nguyên nhân) — tức headline 16.740 hơi thận trọng ở điểm này. Ngoài ra cơ sở "mốc 2027" chỉ là **lời lãnh đạo (KBSV 17/04/2026), chưa kiểm bản gốc** ⇒ trọng số 0,80 cho 2027 là [UL], không phải số có văn bản.

## 3. Biến thể song song (không phải headline)
| Biến thể | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn |
|---|---|---|---|---|---|---|
| **HEADLINE r3** | **16.740** | **8.823** | 16.150 | **25.179** | 74,6% | TRONG |
| S1 truy thu nhất quán: chỉ trong nhánh 340, P(truy thu \| 340) = 0,10 ⇒ P chung 0,02 | 16.525 | 8.388 | 16.119 | 25.176 | 74,6% | TRONG |
| S1k = S1, nhánh khác dùng timing r2 chuẩn hoá (đối chiếu số skeptic) | 16.571 | 8.414 | 16.158 | 25.238 | 74,4% | TRONG |
| S2 giữ P chung 0,10, dồn hết vào nhánh 340 (P \| 340 = 0,50) | 15.661 | 3.496 | 16.021 | 25.161 | 75,0% | TRONG |
| S2k (timing skeptic) | 15.702 | 3.515 | 16.026 | 25.225 | 74,8% | TRONG |
| S3 r2 cơ học trên dữ liệu 06/11 (đã bác) | 15.347 | 4.684 | 15.500 | 24.494 | 76,8% | TRONG |
| S0 không có trục thời điểm | 16.315 | 8.403 | 15.843 | 24.512 | 76,6% | TRONG |
| S4 có cấm thầu EVN 3 năm, DT tư vấn −50%, p 0,35 (vụ án ⇒ ngoài tâm) | 14.159 | 5.013 | 13.525 | 23.250 | 81,8% | TRONG |
| S5 độ nhạy KTPL 10% / 15% / 25% (headline 20%), `SUMMARY.json`: tâm 19.256 / 17.998 / 15.483 | 19.256 · 17.998 · 15.483 | — | — | — | — | không tính lại nhãn (10–15% không có cơ sở dữ liệu, đo ≥ 19,7%) |

- Ở S2, P10 do nhánh 340 quyết định (91%); timing quanh P10 gồm truy thu 48% và 2027 49%.
- **Nhãn TRONG ở mọi biến thể.** Tâm thấp hơn giá 18–31% ở mọi biến thể.
- *Đánh số:* báo cáo không có §4 (nhảy từ §3 sang §5); giữ nguyên số mục để không vỡ dẫn chiếu từ sổ/skeptic. S5 (KTPL) có trong `SUMMARY.json` nay đã ghi ở hàng trên (hàng S5 chỉ có tâm; P10/P50/P90 không xuất ra).
- **Độ nhạy chính (yếu tố gây chênh giá/tâm):** P(PPA ≤ 440) = 0,20 + 0,20 = **0,40** [UL]. Giá ngụ ý đòi PPA phẳng **547–623 đ/kWh** (623 với tư vấn kỳ vọng; 547 với tư vấn 11% vĩnh viễn), trong khi mức **duy nhất có văn bản là 340** (dự thảo HĐ sửa đổi 05/2018); dải 500–600 chỉ là lời lãnh đạo chưa kiểm bản gốc. Chênh giữa giá 20.400 và tâm 16.740 do đó phụ thuộc chủ yếu vào việc tin vào dải 500–600 hay vào 340/440.

## 5. Thanh khoản
| Cỡ | ADV trung vị | CK |
|---|---|---|
| **5 tỷ** | 120 phiên: 0,63 tỷ (Q/ADV 797%) | **4,21%** |
| 5 tỷ | 250 phiên: 0,82 tỷ | 3,73% |
| 5 tỷ | 60 phiên: 0,45 tỷ | 4,91% |
| **Sleeve 10 / 20 / 40 triệu** | 120 phiên | **0,49% / 0,56% / 0,66%** |

- ⚠️ Cỡ 5 tỷ **nằm ngoài vùng hiệu chỉnh của luật căn bậc hai**, nên CK thực tế có thể cao hơn nhiều. Cỡ hợp lý ≤ 1 tỷ.
- Ở cỡ sleeve 40 triệu: tâm = 17.477 × (1 − 0,66%) ≈ 17.362 (phép nhân từ tâm trước CK). Nhãn không đổi.

## 6. Pháp lý / quản trị — ⚠️ WARNING
Giữ toàn bộ WARNING của r2 §6 (vụ EVNNPT/PC1, Chủ tịch HĐQT và phó phòng TCKT bị khởi tố; công ty viết "chưa nhận được thông tin/kết luận chính thức" ≠ "chưa bị khởi tố"; kiểm toán FY2026 An Việt; cổ đông/cho vay cá nhân; tranh chấp 127,63 tỷ). Bổ sung và sửa:

1. **Mức thiệt hại theo kịch bản pháp lý:** S4 tâm 14.159 (−15% so với headline). Thiệt hại từng kịch bản (core, Ke 12,85%): cấm 3 năm ≈ −8.194 đ/cp; cấm 5 năm ≈ −12.983; nộp 20/50/100 tỷ ≈ −660 / −1.650 / −3.301.
2. **(MỚI r3) VnExpress 02/07/2026** ([link](https://vnexpress.net/47-nguoi-bi-khoi-to-trong-vu-an-tai-tong-cong-ty-truyen-tai-dien-quoc-gia-5092437.html), đã mở lại 02/11):
   - "**13 công ty bị xác định có liên quan**", trong đó có "các công ty CP tư vấn xây dựng điện 1, 2, 3, 4" (= TV1);
   - "**EVNNPT và nhà thầu đều có sai phạm** trong lập, phê duyệt dự toán…";
   - "Các nhà thầu khi thực hiện nhiều hạng mục cũng có vi phạm."
   - Bài không nói pháp nhân nào bị khởi tố. The Investor ghi "13 lãnh đạo và nhân viên" (13 NGƯỜI), mâu thuẫn với VnExpress; cả hai nguồn đều được nêu.
   - Đây là căn cứ đẩy P(cấm thầu) lên. Nguồn: REPORT 02/11 §7.
3. **Giá PPA SB5 (đã sửa):**
   - Bậc 243,66 + O&M ≈ 340 nằm trong **dự thảo** HĐ sửa đổi 05/2018, đã được EVN và Cục ĐTĐL chấp thuận. **Chưa thấy bản ký.** r2 §1 viết "đã ký" là sai.
   - 500–600 từ 2027 chỉ là lời lãnh đạo qua KBSV 17/04/2026, chưa kiểm bản gốc.
   - Truy thu 2022–26 nếu áp hồi tố đủ ≈ −17.397 đ/cp. Đây là kịch bản S1/S2, **không có văn bản đòi**.
4. **Tra tin:** chưa tra lại sau 05/11 trong job này. Mốc tra gần nhất: 05/11/2026 (WebSearch), không thấy khởi tố hay kết luận mới liên quan TV1. WebSearch không thay được CBTT sàn.
5. **Thiên lệch xác nhận:** TV1 đang nằm trong plan SELL. Định giá r3 **không neo vào quyết định bán**. Tâm r3 TĂNG so với r2, tức đi ngược chiều plan. Nhãn và kết luận "giá > tâm" không phụ thuộc biến thể nào được chọn.

## 7. Định giá
- **Phương pháp:** SOTP gồm:
  - PV FCFE thuỷ điện 2027–08/2059, sau KTPL 20%;
  - DCF mảng tư vấn;
  - tiền ròng điều chỉnh −2.412 đ/cp (nợ trên sổ Q3/2026 + KTPL đo được; LNST Q4 50 tỷ [UL]).
- **r = 13,5%:** 13,5% + 1,0 × (lãi huy động 12T hiệu dụng 06/11 = 7,40% − 7,40%) = 13,5%. Nguồn lãi: `deposit_rate_vn`, cctg_12m ngày 02/11.
- **Trục lưới:** xác suất là [UL] nếu không ghi khác.
  - PPA 949/600/520/440/340 @ 0,05/0,25/0,30/0,20/0,20;
  - biên tư vấn 5/8/11/14% @ 0,20/0,30/0,40/0,10;
  - sản lượng Q 175/187,5/200 GWh;
  - **thời điểm hạ bậc: 2027 0,80 / lùi 1 năm 0,15 / lùi 2 năm 0,05**;
  - VLĐ 45/49/53%.
- **Loại khỏi base:**
  - truy thu (r3, xem S1/S2);
  - vụ án (S4 + WARNING);
  - điện mặt trời nổi (NPV 0);
  - KTPL (đo được, 20%).
- **Gordon** (g 3%, trước CK, LNST 2025 sau KTPL): có lãi tiền gửi 36.723 · không lãi tiền gửi 37.198. Chỉ dùng để đối chiếu: LNST 2025 tính ở giá điện 949, mức sẽ bị hạ bậc.
- **Độ nhạy r** (tâm sau CK, β = 1):

| Lãi suất | −100bp | −50bp | 0 | +50bp | +100bp |
|---|---|---|---|---|---|
| Tâm | 18.398 (+9,9%) | 17.528 | 16.740 | 16.022 | 15.362 (−8,2%) |

## 8. Mốc đổi nhận định (hai chiều) + HARD ABANDON
| Mốc | LÊN nếu | XUỐNG nếu |
|---|---|---|
| Văn bản/phụ lục PPA SB5 | giá ròng ≥ 600, hoặc lùi hạ bậc ≥ 2 năm, hoặc xác nhận phụ lục 05 KHÔNG ký | ≤ 440 hoặc ~340; có văn bản đòi truy thu 2022–26 (⇒ S2, P10 ~3.500) |
| BCTC Q4/2026 + kiểm toán FY2026 (An Việt) | biên tư vấn ≥ 11%; chấp nhận toàn phần | ngoại trừ; trích lập cho vụ án |
| Vụ án | kết thúc, không cấm thầu/nộp tiền | quyết định cấm thầu EVN (≈ −8.200 trở lên) |
| Lãi huy động | −50bp ⇒ +4,7% | +50bp ⇒ −4,3% |

- **HARD ABANDON:** khởi tố pháp nhân, cấm thầu EVN, có văn bản truy thu, hoặc kiểm toán từ chối/ngoại trừ.
- **Không đủ điều kiện sleeve fear-buy** theo `calculated_fear_state_backstop.md` **§2** (sửa dẫn chiếu: r2 ghi §2.5; TV1 thuộc nhóm (a) scandal cá nhân). Lý do: giá cao hơn tâm và vụ án chưa kết luận. Nếu xét lại sau này: trần size 2–4% NAV và phải có trigger §3.
