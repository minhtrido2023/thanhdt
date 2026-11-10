# DD — VGS (CTCP Ống thép Việt-Đức VG PIPE, HNX) · 10/11/2026 · job `Taylor_20261110_125453`

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị mua, không lệnh, không wire. User quyết.
> Nguồn: **[Q3HN]** BCTC hợp nhất Q3/2026 (lập 27/10/2026, `src/BCTC-Q3-HN.pdf`, md5 `e30e74ce…`); **[Q3R]** BCTC riêng Q3/2026;
> **[FY25]** BCTC hợp nhất 2025 kiểm toán AASC; **[H1]** BCTC hợp nhất bán niên 2026 soát xét AASC; **[CBTT]** website vgpipe.com.vn /
> thepvietduc.com.vn; **[BQ]** `tav2_bq` (chỉ đối chiếu); **[Bobby]** `kb/data_registry/market-state/sector_read_thep_20261031.md` (đọc MÙ).
> Tất cả PDF là scan, đọc bằng render pymupdf. Đơn vị: tỷ đồng trừ khi ghi khác. Số tự đặt gắn **(ước lượng)**.
> Định giá làm MÙ giá: `calc/assumptions.json` + `calc/model.py` khoá md5 ở `calc/LOCK_prerun.txt` TRƯỚC khi lấy giá (`calc/px_vgs.csv`).
> **VÒNG 2 (10/11/2026, job `Taylor_20261110_131720`):** áp 9 đính chính của fundamental-skeptic (Phụ lục E). Headline mới chạy từ `calc/assumptions_r2.json` + `calc/model_r2.py`, khoá ở `calc/LOCK_r2_prerun.txt` trước khi chạy lại; bản vòng 1 giữ ở `REPORT_r1.md` / `SUMMARY_r1.json`. Trang dẫn = số trang IN trên BCTC (PNG = trang in + 1).

## 0. Kết luận

**Giá trị nội tại (SOTP, kỳ vọng có trọng số), r2: tâm 26.778 đ/cp trước chiết khấu thanh khoản; sau CK ở cỡ thực thi ≤1 tỷ là 26.526 (P10 19.393 · P90 34.722).**
Giá 19.300 (10/11/2026) **DƯỚI vùng ở cỡ ≤1 tỷ, nhưng chỉ thấp hơn P10 0,5% ⇒ NHÃN MONG MANH** (chỉ cần P10 nhích 0,5% là thành TRONG). Ở cỡ 5 tỷ, vốn quá lớn so với thanh khoản và không thực thi được, nhãn là TRONG (tâm 26.215, P10 19.165). Nhãn ghi sổ theo cỡ thực thi: **DƯỚI (mong manh)**.
Giá thấp hơn tâm sau CK 27,2% (cỡ ≤1 tỷ), luật 4 (giá ≤ 0,85 × tâm, ngưỡng 22.547) **đạt**, và vẫn đạt ở mọi độ nhạy dưới đây.

**Độ rẻ phụ thuộc cách định giá liên kết 28,6% (không công bố số).** Vòng 2 đã thêm kịch bản xấu 0,7 × sổ sách (cơ sở: lãi 2024 chỉ 10,9 tỷ trên sổ khoảng 113 ⇒ lợi suất khoảng 9% < Ke, tức giá trị dưới sổ; ước lượng). Độ nhạy (trước CK; sau CK ≤1 tỷ trong ngoặc):
- liên kết cơ sở = sổ sách (ROE = Ke giữa chu kỳ): **25.430** (−5,0%) (25.191);
- liên kết cơ sở = 0,75 × sổ (P/B peer): **24.911** (−7,0%) (24.676);
- cả ba kịch bản liên kết = 0,75 × sổ: **23.379** (−12,7%) (23.159; giá thấp hơn 16,7%, luật 4 vẫn đạt sát: ngưỡng 19.685).

Nhưng độ rẻ này **gần như toàn bộ đến từ hai tài sản không phải ống thép**, và cả hai đều có điểm yếu. Tâm cơ sở chia ra như sau:

| Khối (cơ sở, r 13,5%) | đ/cp | Ghi chú |
|---|---|---|
| Lõi ống + tôn cán nguội (EPV, g = 0) | 15.575 | LN lõi chuẩn hoá 129,4 tỷ (ước lượng) |
| Liên kết 28,6% CTCP Tập đoàn SX Thép Việt Đức | 6.853 | EPV của phần lãi bình quân 2024/2025/TTM |
| Dự án KĐT Việt Đức Legend City, phần vốn ròng | 6.524 | theo giá gốc (luật NPV = 0) |
| Nợ ròng (tiền + HTM − vay) | −542 | |

- **Lõi cộng nợ ròng chỉ đáng 15.033 < giá.** Giá 19.300 đang trả khoảng 4.270 đ/cp cho liên kết + Legend City, tức khoảng 32% giá trị cơ sở của hai khối này.
- Nếu áp chiết khấu holding 30% lên hai khối (chỉ là độ nhạy, không có cơ sở dữ liệu nên không vào tâm), tâm còn **22.765** (trước CK), vẫn cao hơn giá 18%.
- r ngầm định để tâm cơ sở bằng giá là **22,7%**, cao hơn nhiều so với 13,5%.

**Điểm yếu của luận điểm (nói thẳng):**
1. Gần một nửa giá trị là **liên kết không kiểm soát và không công bố số**. Nó đang ở **đỉnh chu kỳ**: phần lãi Q3 là 45,6 tỷ, cả năm 2024 chỉ 10,9 tỷ. Thêm vào đó là một **dự án BĐS hai chiều**: giai đoạn 1A (214.481 m², khoảng 78% giai đoạn 1) đã bàn giao đất trên thực địa và có giấy phép xây dựng, nhưng phần còn lại giai đoạn 1 vẫn đang giải phóng mặt bằng sau 16 năm kể từ QĐ 2010, và mục tiêu dự án chủ yếu là nhà ở thu nhập thấp/công nhân (lợi nhuận có thể bị trần, IRR có thể < Ke; §4).
2. Lợi nhuận Q3 tăng +51% YoY, nhưng **77% phần tăng PBT đến từ liên kết**. EBIT lõi chỉ +10%.
3. Có cờ kế toán và quản trị (§9): cổ tức từ liên kết năm 2025 nghi bị đếm hai lần; phải thu tập trung vào 2 khách; một đối tác vừa là khách vừa là nhà cung cấp; cả Ban kiểm soát từ nhiệm 09/2025.
4. Thanh khoản đang co: ADV60 2,23 tỷ so với ADV250 6,17 tỷ.

**Moat: NONE**, căn cứ vào **biên gộp 10 năm chỉ 2,3–4,9% và đầu vào HRC mua từ Hòa Phát (đối thủ tích hợp)**. ROIC5Y 8,7% (ROIC_Min5Y 5,7%) thấp hơn Ke 13,5% nhưng bị pha loãng bởi vốn nhàn rỗi (Legend City 900 tỷ XDCB, liên kết 256 tỷ); lõi ống đứng một mình khoảng 16% trên khoảng 780 tỷ vốn (129,4 / (1.433,3 − 255,7 − 401,4 = 776,2) = 16,7%; ước lượng, chưa cộng nợ ròng), tức **trên** Ke, nên ROIC không dùng làm căn cứ NONE. Mô hình không thưởng moat và cũng không trừ.

## 1. Kiểm chứng câu hỏi trọng tâm (brief Mike)
| Câu | Kết luận | Bằng chứng |
|---|---|---|
| Doanh thu Q3 BQ khoảng 2.152 tỷ là số QUÝ? | **ĐÚNG**: 2.151,6 là doanh thu gộp quý; thuần 2.138,7 | [Q3HN] KQKD mã 01/10; [BQ] `Revenue_P0` 2026Q3 = 2.152 |
| NP_P0 BQ | **khớp**: 96,2 = LNST công ty mẹ Q3 | [Q3HN] mã 61 |
| GPM_P0 BQ (TTM) | **khớp**: 4,32% ≈ GP TTM 338,7 / DT thuần TTM 7.849,6 = 4,31% | `calc/model_out.json` ttm |
| CF_OA_P0 BQ 2026Q3 | **trống** ở BQ; CFO 9T [Q3HN] = 40,3 tỷ | lệch nguồn: BQ chưa nạp CFO quý |

## 2. Chất lượng lợi nhuận [Q3HN, Q3R, FY25]
| | Q3/26 | Q3/25 | YoY | 9T/26 | 9T/25 | YoY | TTM |
|---|---|---|---|---|---|---|---|
| DT thuần | 2.138,7 | 1.767,2 | +21,0% | 6.205,3 | 5.674,3 | +9,4% | 7.849,6 |
| LN gộp | 98,4 | 76,7 | +28,2% | 252,4 | 199,3 | +26,6% | 338,7 |
| Biên gộp | 4,60% | 4,34% | | 4,07% | 3,51% | | 4,31% |
| BH + QLDN | 37,1 | 20,9 | +77% | 102,5 | 69,0 | +49% | 127,5 |
| **EBIT lõi** | **61,3** | **55,8** | **+9,8%** | **149,8** | **130,4** | **+14,9%** | 211,2 |
| DT tài chính | 20,4 | 2,9 | | 32,1 | 31,8 (gồm 26,6 cổ tức liên kết) | | 35,6 |
| Chi phí lãi vay | 18,2 | 3,5 | | 42,8 | 13,6 | | 47,2 |
| **Lãi liên kết** | **45,6** | **19,3** | **+136%** | **87,6** | **14,9** | ×5,9 | 116,3 |
| PBT | 108,9 | 75,0 | +45% | 227,3 | 164,4 | +38% | 317,0 |
| LNST cty mẹ | 96,2 | 63,8 | +50,9% | 199,3 | 139,6 | +42,8% | 276,7 (EPS 4.498) |

- **Phần tăng PBT Q3 là +33,9 tỷ.** Liên kết đóng góp +26,2 (77%), EBIT lõi +5,5, tài chính ròng +2,8.
  - Liên kết chiếm **42% PBT Q3** và **39% PBT 9T**. Phần lãi này không chịu thuế ở VGS và không phải tiền mặt cho tới khi được chia cổ tức.
- **Theo mảng [Q3HN TM23/25]:**
  - Sản phẩm tự sản xuất 9T: DT 5.383,8, GP 284,5 (5,29%), biên y hệt 9T/25 (5,29%).
  - Hàng hoá thương mại 9T: DT 852,6, GP 6,3 (0,74%); 9T/25 là 1.304,4 / 11,3. Đây là doanh thu đi qua, gần như không có biên.
  - Biên gộp tổng tăng chủ yếu nhờ **chiết khấu thương mại giảm** (37,3 so với 44,3) và **tỷ trọng thương mại giảm**, không nhờ biên sản phẩm.
- **Theo pháp nhân [Q3R]:** công ty mẹ (ống) 9T có DT thuần 3.741,7, GP 200,8 (5,37%; 9T/25 4,75%). Con là CTCP Thép Việt Đức, sở hữu 99,94%, làm tôn cán nguội. GP của con ước khoảng 51,6 tỷ trên khoảng 2.460 tỷ DT, biên khoảng 2% (ước lượng, chưa trừ giao dịch nội bộ).
- **Chi phí bán hàng 9T +59%** (80,1 so với 50,3). Phần lớn là dịch vụ mua ngoài (53,3 so với 29,5), như vận chuyển và hoa hồng. Biên ròng lõi vì thế không theo kịp biên gộp.
- **Lãi tồn kho do giá HRC:** không tách được từ BCTC, vì không có dự phòng giảm giá HTK và không công bố sản lượng.
  - Bobby (§3b) cho thấy giá HRC nội địa 2026 đi ngang (H1 548,9 → 10/2026 556 USD/t), nên lãi/lỗ tồn kho không phải động lực chính (suy luận, chưa đo).
  - Hàng mua đang đi đường tăng 16,2 → 155,5 tỷ (nhập HRC). Nếu giá HRC giảm thì đây là rủi ro tồn kho cho Q4.
- **Tài chính ròng:**
  - Vay ngắn hạn tăng 572 → 1.202 tỷ trong khi tiền gửi HTM tăng 275 → 1.097 tỷ. HTM gồm 476,6 tỷ ở mẹ (lãi 8,0–9,3%) và 620 tỷ ở con (7,4–8,5%).
  - Chi phí vay 9T khoảng 6,4%/năm (ước lượng = 42,8 × 4/3 chia dư nợ bình quân 887). Như vậy đang có chênh lãi dương nhẹ.
  - Đã kiểm thì chưa thấy tiền gửi bị cầm cố cho khoản vay. TM20 chỉ ghi chung "thế chấp/cầm cố/bảo lãnh", nên **cần kiểm chứng**.
- **Một lần và bền:**
  - Lãi khác ≈ 0. Hoàn nhập dự phòng 21,1 tỷ trong LCTT 9T là dự phòng phải trả (sửa chữa lớn): 31,4 → 10,0.
  - Năm 2025 có 26,6 tỷ cổ tức liên kết ghi vào DT tài chính (§9 W2). Khoản này nằm ngoài TTM, vì Q4/25 DT tài chính chỉ 3,5.

## 3. Bảng cân đối và dòng tiền (30/09/2026, [Q3HN])
| Khoản | 30/09/26 | 01/01/26 |
|---|---|---|
| Tiền + HTM | 1.168,3 | 355,3 |
| Vay NH (BIDV 655 · VietinBank 473 · VCB 71 · cá nhân 2,4 lãi 9%) | 1.201,6 | 571,9 |
| **Nợ ròng (tiền + HTM − vay)** | **−33,3** | −216,6 |
| Phải thu KH (2 khách 481,2) | 651,1 | 262,6 |
| Tồn kho (đi đường 155,5) | 676,2 | 531,4 |
| Phải trả NCC (Hòa Phát 181,7 · Điện Xanh Châu Á 198,5) | 625,7 | 128,8 |
| XDCB dở dang: Legend City 891,5 + CC4 Vân Canh 8,6 | 900,1 | 809,2 |
| Phải trả dài hạn khác: Vinaconex góp BCC | 498,7 | 204,4 |
| Đầu tư liên kết (28,6%) | 255,7 | 168,1 |
| VCSH cty mẹ (BVPS 23.297) | 1.433,3 | 1.295,6 |

- Nợ ròng xấp xỉ 0 trên nền VCSH 1.433 và không có nợ dài hạn ngân hàng. **Nhưng không thể nói "không có rủi ro thanh khoản":** khoảng 294,3 tỷ trong HTM có vẻ là tiền BCC của Vinaconex (phải trả Vinaconex 204,4 → 498,7 = +294,3; LCTT tr.5: tiền gửi đặt 1.096,6 / thu hồi 569,3, số dư HTM 275 → 1.096,6). Nợ ròng **tự do** của VGS ≈ −33,3 − 294,3 = **−327,6 tỷ** (vay ngắn hạn 1.201,6 lớn hơn tiền tự do), phụ thuộc tái tục vay NH. SOTP không đổi: HTM đã tính đủ trong nợ ròng và khoản phải trả BCC đã trừ trong vốn ròng Legend City (§4). Nợ phải trả/VCSH = 1,71, nhưng 499 tỷ trong đó là vốn góp BCC của Vinaconex.
- **Vốn lưu động phình:** ngày phải thu khoảng 28 ngày so với khoảng 14 ngày ngày 01/01 (ước lượng theo DT quý quy năm). Phải trả NCC tăng tương ứng, nên vốn lưu động ròng tăng ít. Riêng phải thu thì tăng 370 tỷ.
- **CFO:**
  - 9T/26 chỉ **40,3** so với LNST 199,3, vì phải thu −370, tồn kho −145, phải trả +481.
  - 2025: CFO 440,7 so với LNST 217,0. 2024: 93,6 so với 109,9.
  - Theo [BQ], CFO đã âm các năm 2016, 2017, 2019. Ống thép là ngành ăn vốn lưu động: CFO lệch mạnh theo năm nhưng cộng dồn nhiều năm vẫn dương (BQ 2015–2025 tổng khoảng 1.165 tỷ).
- Cổ tức tiền 2025 là 1.000 đ/cp, đã chi 61,5 tỷ (TM21c).

## 4. Legend City (luật NPV = 0)
- **Dự án [Q3HN TM10, TM18]:**
  - KĐT 62,17 ha; giai đoạn 1 là 27,5 ha (Thủ tướng đồng ý chuyển mục đích 23,6 ha năm 2015). Chấp thuận đầu tư QĐ 2204/QĐ-UBND ngày 10/08/2010.
  - Có giấy phép xây dựng hạ tầng (04/2024, 07/2024) và NOXH cao tầng giai đoạn 1 (24/01/2025). Vẫn đang "tiếp tục giải phóng mặt bằng phần còn lại giai đoạn 1".
- **BCC 3168/2025 với Vinaconex (VCG), 50:50 giai đoạn 1A (214.481 m²):**
  - Phần VGS đã chi được tính là 852,1 tỷ. Vinaconex góp tiền tương ứng 426,0 tỷ (cọc 204,4 + 221,6 đến 31/03/2026), cộng 9,6 tỷ cho giai đoạn 2.
  - Số dư phải trả Vinaconex là 498,7 tỷ.
  - **Mốc tham chiếu, KHÔNG phải mốc độc lập sạch (r2):** Vinaconex mua 50% bằng giá vốn, nhưng (i) TM6 tr.17: VGS đang ứng trước cho Vinaconex 38,02 tỷ (01/01/2026 = 0); (ii) Vinaconex còn là nhà thầu của dự án (theo skeptic, chưa tự kiểm hợp đồng thầu); (iii) tiền BCC có vẻ nằm trong HTM của VGS (§3). Đây là đối tác hai chiều, nên "đúng giá vốn" là giá thoả thuận có liên quan, không phải giá thị trường độc lập (§9 W7). Vẫn dùng giá gốc làm base (NPV = 0) vì chưa có mốc nào tốt hơn, nhưng không coi là xác nhận.
- **Định giá:**
  - Phần vốn ròng VGS = 891,5 + 8,6 − 498,7 = **401,4 tỷ = 6.524 đ/cp** (base, trọng số 0,7).
  - Kịch bản xấu ×0,7 (trọng số 0,3). Cơ sở là **cả hai chiều bất lợi**, không chỉ độ trễ: (a) phần còn lại giai đoạn 1 vẫn đang giải phóng mặt bằng, cộng chi phí giữ vốn; (b) TM10 tr.19 mô tả mục tiêu là nhà ở cho người thu nhập thấp, cán bộ công nhân viên, nên lợi nhuận có thể bị trần theo quy định NOXH (mức trần cụ thể chưa tra) và IRR có thể thấp hơn Ke. Không có số vượt dự toán.
  - **Chiều thuận, nói rõ để không nói quá:** TM18 tr.25 ghi toàn bộ 214.481,4 m² giai đoạn 1A "đã được bàn giao đất trên thực địa" và có giấy phép xây dựng hạ tầng/NOXH 2024–25. Câu "16 năm chưa xong giải phóng mặt bằng" ở bản đầu là nói quá: chỉ phần còn lại của giai đoạn 1 chưa xong.
  - **Không có kịch bản thưởng:** chưa có giá bán hay hợp đồng đầu ra kiểm được.
- Phần còn phải chi: chưa có tổng mức đầu tư trong tài liệu đã tải (tờ trình 05/2026 không kèm trong biên bản ĐHĐCĐ). Theo luật, phần này được bù bằng giá trị tương đương.

## 5. Vị thế & lợi thế cạnh tranh (5F tầng b) — LÀM MỚI (moat_tags.csv chưa có VGS; không có DD VGS trước)
**Loại hình DN:** chế biến hạ nguồn. VGS mua HRC/cuộn để làm ống hàn, ống mạ và tôn cán nguội (qua con), bán nội địa qua nhà phân phối. Số dư USD chỉ 1.718 USD, nên **gần như không xuất khẩu** ⇒ không bị phòng vệ thương mại nước ngoài (Bobby §2c) đánh trực tiếp.

| Lực | Đánh giá | Bằng chứng |
|---|---|---|
| Nhà cung cấp | **MẠNH (bất lợi)** | HRC mua của Hòa Phát (phải trả 181,7 tỷ), đối thủ trực tiếp cũng làm ống. Thuế AD HRC Trung Quốc 23–28% (Bobby §2c, ĐÍNH CHÍNH) nâng giá đầu vào nội địa |
| Người mua | Trung bình–mạnh | 2 khách = 481 tỷ / 74% phải thu KH; chiết khấu thương mại 37,3 tỷ 9T |
| Đối thủ | Mạnh | Hòa Phát, Hoa Sen, Nam Kim, SeAH… Ống hàn toàn ngành H1 bán 1,41 tr t (+5,2%, Bobby §1a) |
| Thay thế | Thấp | ống thép trong xây dựng/kết cấu |
| Gia nhập | Trung bình | vốn dây chuyền ống không lớn; rào cản là kênh phân phối |
| Lực 6 (chính sách) | Hai mặt | AD HRC giữ giá nội địa: tốt cho liên kết làm thép XD, xấu cho chi phí đầu vào ống |

**Định lượng [BQ `calc/bq_vgs_hist.csv` + peer]:**
- ROIC5Y 8,7%, ROIC_Min5Y 5,7%, ROE_Min3Y 6,1%, đều < Ke 13,5% (nhưng ROIC5Y bị pha vốn nhàn rỗi; lõi một mình khoảng 16%, xem §0 và kết luận 5F).
- Biên gộp TTM cuối năm 2016–2025 nằm trong 2,3–4,9%, trung vị 3,6%; TTM Q3/26 là 4,32%.
- Peer biên gộp TTM: HPG 17,2%, HSG 12,6%, NKG 6,8%, HMC 2,6%, SMC 1,7%.
- Điểm mạnh tương đối: ROIC_Min5Y của VGS (5,7%) cao hơn HSG (−6,3%), NKG (0,9%), SMC (−17,9%). Nghĩa là "không lỗ qua đáy chu kỳ", nhưng chưa phải lợi nhuận siêu ngạch.
- **Thị phần ống hàn của VGS: cần kiểm chứng.** BCTC không có sản lượng. Profile công ty ghi công suất 700 nghìn t/năm cho nhà máy ống và 1,3 tr t/năm cho cả tập đoàn. Con số 5,0% thị phần VSA ở Bobby §2b là thép XD, thuộc **liên kết**, không phải VGS.

**Kết luận 5F:** **moat_tier NONE**, moat_type "SCALE/DISTRIBUTION (không bền)". Rủi ro số 1: **biên chế biến mỏng 2–5%, đầu vào HRC từ đối thủ tích hợp (Hòa Phát), thêm vốn lưu động lớn**. Hai điều kiện (i) và (ii) của moat bền đều không qua ⇒ **không thêm tham số moat** (RONIC = Ke, g = 0). Cũng không trừ. Độ nhạy moat: NONE / NARROW / WIDE đều không đổi headline, vì không có cơ sở thưởng.

**Đề xuất dòng `data/moat_tags.csv` (human-curated, KHÔNG tự sửa):**
`VGS,NONE,SCALE/DISTRIBUTION,M,"Downstream pipe/CRC processor buying HRC from integrated rival (HPG); GPM 2.3-4.9% 10Y, ROIC_Min5Y 5.7% < Ke; ~half of value sits in 28.6% unlisted long-steel associate (peak cycle) + Legend City real-estate project",2026-11-10,taylor_dd_VGS_20261110,N`

## 6. Định giá (MÙ giá; khoá `calc/LOCK_prerun.txt`)
**r:**
- r = 13,5% + 1,0 × (dep12T − 7,40%). dep12T hiện là `effective_deposit_rate('2026-11-10')` = cctg_12m(2026-11-02) **7,40%** (Big-4 online 6,8%). Vậy **r = 13,50%**, đúng điểm neo.
- Độ nhạy tâm (trước CK) theo lãi huy động:

| Δ lãi huy động | β = 1 | β = 0,5 |
|---|---|---|
| −100bp | 28.242 (+5,5%) | 27.482 |
| −50bp | 27.482 (+2,6%) | 27.123 |
| +50bp | 26.125 (−2,4%) | 26.446 |
| +100bp | 25.517 (−4,7%) | 26.125 |

**Lưới 18 kết cục** = LN lõi × liên kết × Legend City, trọng số nhân (`calc/model.py`):

| Khối | Xấu (w) | Cơ sở (w) | Tốt (w) |
|---|---|---|---|
| LN lõi = DT × (GPM − SG&A 1,5%) × 0,8 (ước lượng) | DT 7.000, GPM 2,5% (đáy 2022–23) → **56,0 tỷ / 6.742 đ** (0,25) | DT 7.700, GPM 3,6% (trung vị 10 năm) → **129,4 / 15.575** (0,5) | DT 8.000, GPM 4,3% (TTM) → **179,2 / 21.575** (0,25) |
| Liên kết 28,6% | 0,7 × sổ sách = 179,0 → **2.910** (0,25) (r2; vòng 1 là 1,0 × sổ = 4.156) | EPV lãi bình quân (10,9 + 43,6 + 116,3)/3 = 56,9 → 421 tỷ → **6.853** (0,5) | TTM 116,3 × 5 → **9.451** (0,25) |
| Legend City | ×0,7 → **4.567** (0,3) | giá gốc → **6.524** (0,7) | — |
| Nợ ròng | −542 | | |

- **Tâm 26.778 · P10 19.577 · P50 28.410 · P90 35.052** (trước CK; vòng 1: 27.090). Min 13.677, max 37.009. Base liên kết giữ EPV; **TTM 116,3 chồng FY25 một quý** (Q4/25 = 28,7 nằm trong cả hai), nên trung bình 3 mốc đếm Q4/25 hai lần (ghi nhận, không chỉnh; độ nhạy ở dưới).
- Đối chiếu:
  - Tâm / BVPS = 1,15x.
  - Tâm / EPS chuẩn hoá (186,3 tỷ → 3.028 đ) = 8,8x.
  - Tâm / EPS TTM 4.498 = 6,0x.
  - EV/EBITDA lõi tại tâm khoảng 3,9x TTM và 5,0x trên EBIT chuẩn hoá (ước lượng; EV lõi = vốn hoá tâm − liên kết cơ sở − Legend City + nợ ròng).
- **LN lõi cơ sở 129,4 thấp hơn LN lõi TTM khoảng 160,5** (PBT ngoài liên kết × (1 − thuế)). Kịch bản tốt 179 cao hơn TTM vì giả định tài chính ròng = 0, trong khi TTM là −11,6.
- **Comp (chất lượng thấp, chỉ tham khảo):**
  - P/B [BQ 10/11]: HPG 1,20 · HSG 0,73 · NKG 0,77 · HMC 0,68 · SMC 0,99 · TLH 0,29; trung vị khoảng 0,75.
  - PE của BQ cho peer bất thường (HPG PE_MA5Y 22,3, SHI 59,5), nên không dùng.
  - VGS tâm 1,15x book, cao hơn trung vị peer. Lý do là ROE TTM khoảng 20% so với ROE5Y peer 10–17%. Nhưng phần ROE cao đến từ liên kết đỉnh chu kỳ.
- **Thanh khoản [`calc/liq_vgs.csv`]:** σ ngày 2,34%; ADV250 trung vị 6,17 tỷ; ADV60 2,23 tỷ (đang co).

| Cỡ | CK (ADV250) | CK (ADV60) | Tâm sau CK | P10 | P90 | Phiên thoát @10% ADV250 / ADV60 | Nhãn @19.300 |
|---|---|---|---|---|---|---|---|
| 5 tỷ (không thực thi) | 2,11% | 3,50% | 26.215 | 19.165 | 34.314 | 8,1 / 22,4 | TRONG (sát P10) |
| **1 tỷ (cỡ ghi sổ)** | 0,94% | 1,57% | **26.526** | 19.393 | 34.722 | 1,6 / 4,5 | **DƯỚI (mong manh, 0,5% dưới P10)** |
| 40 tr | 0,19% | 0,31% | 26.728 | 19.540 | 34.986 | 0,1 / 0,2 | DƯỚI |

Luật 4 (giá ≤ 0,85 × tâm sau CK): ngưỡng 22.282 / 22.547 / 22.719, **đạt** cả ba cỡ. Ở cỡ 5 tỷ thì Q/ADV250 = 81%, nằm ngoài vùng hiệu chỉnh của luật căn bậc hai, nên số CK chỉ là chỉ dấu. Cỡ thực thi được là **≤1 tỷ/lần** (khoảng 16% ADV250, 45% ADV60). Với ADV60 hiện tại thì nên ≤0,5 tỷ/phiên.

**Độ nhạy định giá liên kết (r2, tâm trước CK; so với 26.778):**

| Cách định giá liên kết | Tâm | Δ | Sau CK 1 tỷ |
|---|---|---|---|
| Lưới r2 (0,7×sổ / EPV TB3 / TTM×5) | 26.778 | | 26.526 |
| Cơ sở = sổ sách (ROE = Ke) | 25.430 | −5,0% | 25.191 |
| Cơ sở = 0,75 × sổ (P/B peer) | 24.911 | −7,0% | 24.676 |
| Cả 3 kịch bản = 0,75 × sổ | 23.379 | −12,7% | 23.159 |
| W2 cách đọc (b): LN liên kết 2025 = 70,2 (avg3 = 66,0) | 27.313 | +535 đ | 27.056 |
| M1 trung gian: trọng số liên kết 0,45/0,45/0,10 | 25.600 | −4,4% | 25.359 |

(Skeptic đưa ~23.847 cho P/B peer 0,75; tôi không tái lập đúng số đó. Hai cách tính của tôi là 24.911 khi chỉ đổi cơ sở và 23.379 khi đổi cả ba kịch bản. Số liệu: `calc/model_out_r2.json`.)

**Phản ứng giá quanh sự kiện [BQ `calc/px_events.csv`, đọc SAU khoá]:** BCTC Q3 công bố 27/10, giá 18.800 → 18.700 (28/10) → 19.300 (30/10). Mức +51% LN không được thị trường định giá lại.

## 7. Điều thị trường chưa tính (và vì sao có thể đúng khi chưa tính)
1. **Phần lãi liên kết 116 tỷ TTM**, khoảng 1.890 đ/cp/năm. Không xuất hiện trong doanh thu, và VGS không công bố BCTC liên kết. Thị trường có lý do để chiết khấu: liên kết đang ở đỉnh chu kỳ thép XD. Bobby F2 (P 0,65) dự báo bán thép XD Q1/2027 tăng < +12%, tức giảm tốc.
2. **Legend City được Vinaconex "định giá" bằng giá vốn** qua BCC (đối tác hai chiều, §9 W7; không phải mốc độc lập sạch). Thị trường có thể đang coi 900 tỷ XDCB là vốn chết.
3. **Vĩ mô (DISPLAY-ONLY, snapshot 10/11):** IIP +15,0% YoY, FDI luỹ kế +13,05% YoY, GDP Q3 +9,95%. Kênh xây dựng và nhà xưởng thuận cho khối lượng ống và thép XD. GDP xây dựng không có Δ. CPI 5,09% và LNH 3M 6,60% (Δ12T +0,40pp) đẩy chi phí vốn lưu động lên. Không chỉnh giá trị theo các chỉ báo này.

## 8. Mốc khoá trước + điều kiện đổi nhận định (CẢ HAI chiều)
| # | Mốc (nguồn chấm) | Hạn | Nếu tốt hơn | Nếu xấu hơn |
|---|---|---|---|---|
| M1 | Lãi liên kết Q4/2026 [BCTC Q4 HN] | 31/01/2027 | ≥ 35 tỷ ⇒ trọng số liên kết TỐT 0,25→0,40 (tâm +390 đ) | **Ngưỡng trung gian:** < 25 tỷ hai quý liền (Q4/26 và Q1/27) hoặc giảm > 50% so Q3/26 (45,6, tức < 22,8) ⇒ chuyển trọng số liên kết sang xấu 0,45/0,45/0,10 (tâm −1.178 đ). **Ngưỡng nặng:** < 10 tỷ ⇒ liên kết cơ sở về sổ sách (tâm −1.348 đ). Các ngưỡng là ước lượng |
| M2 | Biên gộp hợp nhất Q4/2026 | 31/01/2027 | ≥ 4,5% hai quý liền ⇒ lõi cơ sở GPM 4,0% (tâm +1.483 đ) | < 3,0% hai quý liền ⇒ lõi cơ sở GPM 3,0% (tâm −2.225 đ) |
| M3 | Phải thu KH 31/12/2026 [BCTC năm] | 31/03/2027 | ≤ 400 tỷ, không trích dự phòng ⇒ xoá cờ W3 | > 800 tỷ hoặc trích dự phòng 2 khách lớn ⇒ hạ nhãn, xem lại doanh thu |
| M4 | Legend City: CBTT mở bán / ghi nhận doanh thu NOXH giai đoạn 1 | 31/12/2027 | có giá bán kiểm được ⇒ mở kịch bản IRR > Ke | XDCB tăng tiếp, không bán, không xong GPMB ⇒ base ×0,85 (ước lượng; tâm −685 đ) |
| M5 | Ý kiến kiểm toán BCTC 2026 + giải trình cổ tức liên kết 2025 | 31/03/2027 | chấp nhận toàn phần + thuyết minh rõ ⇒ đóng W2 | ngoại trừ / điều chỉnh hồi tố ⇒ đổi nhận định |
| M6 | Lãi huy động 12T (`effective_deposit_rate`) | liên tục | −50bp ⇒ +704 đ | +50bp ⇒ −653 đ |
| M7 | Thuế AD HRC TQ còn hiệu lực (Bobby F8, P 0,90) | 31/03/2027 | — | bị huỷ ⇒ liên kết (thép XD) mất ô bảo hộ, kịch bản xấu nặng hơn |

## 9. Pháp lý / quản trị — chỉ WARNING (không đưa vào tâm)
- **W1:** Cả 3 thành viên Ban kiểm soát nhiệm kỳ 2022–2026 nộp đơn từ nhiệm cùng ngày 15/09/2025, bầu bổ sung 07/11/2025 [CBTT NQ ĐHĐCĐ bất thường 11/2025]. Không rõ lý do. Đã bầu Chủ tịch HĐQT và Trưởng BKS nhiệm kỳ 2026–2031 (04/2026).
- **W2:** FY25 ghi **cổ tức từ liên kết 26,6 tỷ vào DT tài chính** [nguồn đúng: Q3HN TM26 tr.33 (cột 9T/25: cổ tức 26.598.798.283, đã đọc lại); TM33 tr.34 và LCTT FY25 mã 27 (33,3 tiền nhận) là theo skeptic, chưa tự kiểm lại; bản đầu trích "FY25 TM25" sai], trong khi giá trị liên kết 124,5 → 168,1 = +43,6, đúng bằng phần lãi trong năm, tức không trừ cổ tức.
  - Theo VAS 07, cổ tức nhận từ liên kết phải giảm giá trị khoản đầu tư. Nếu đây là đếm hai lần thì **LN 2025 bị thổi khoảng 26,6 tỷ (khoảng 12% LNST)**.
  - Cách đọc (b): "phần lãi" đã trình bày ròng sau cổ tức, tức LN liên kết 2025 = 43,6 + 26,6 = 70,2. Hệ quả định giá nếu (b) đúng: avg3 = 66,0, tâm cơ sở **+535 đ** (27.313). Không truy hết được: cần BCTC liên kết (không công bố), nên **ghi là không truy**. Kiểm toán AASC chấp nhận toàn phần.
  - TTM và tâm định giá **không** chứa khoản này.
- **W3:** Phải thu tập trung:
  - Cty TNHH Kinh doanh Thiết bị Vật tư Xây dựng 284,5 tỷ (01/01/2026: 8,0) và Cty TNHH Điện Xanh Châu Á 196,7 tỷ (01/01/2026: 69,1) [Q3HN TM5 tr.17, đã đọc lại].
  - **Nền 01/01/2025** [FY25 TM5, theo skeptic, chưa tự kiểm]: phải thu KH 569,9; HPM 182,2; Kinh doanh Thiết bị VTXD 116,7. Tức phải thu tập trung **có tính mùa vụ/chu kỳ**, và so riêng với 01/01/2026 (đáy 262,6) làm cờ này trông nặng hơn thực tế. Đọc cờ trên cả hai nền.
  - **Điện Xanh Châu Á đồng thời là nhà cung cấp, phải trả 198,5 tỷ** (hai chiều cả ở 01/01/2026: phải thu 69,1 / phải trả 69,7 [phải trả: theo skeptic]). Có thể là bù trừ/hàng đổi hàng, cần kiểm chứng bản chất.
  - Có nợ xấu cũ 28,1 tỷ (4 khách, dự phòng 26,5).
- **W4:** Thuyết minh bên liên quan (TM33) **không kê giao dịch mua/bán với liên kết** "Tập đoàn SX Thép Việt Đức", dù cùng thương hiệu và hệ sinh thái. Cổ đông lớn: bà Nguyễn Thị Thanh Thủy 25,67%, bà Lê Khánh Huyền 8,24%, ông Lê Quốc Khánh 5,15% [TM21b]. Quan hệ sở hữu chéo với liên kết: cần kiểm chứng.
- **W5:** Vay cá nhân 2,4 tỷ tín chấp lãi 9%. Nhỏ, nhưng là dấu hiệu.
- **W7 (mới, r2):** **Vinaconex là đối tác hai chiều** (kiểu W3): vừa đối tác BCC 50:50 mua phần dự án bằng giá vốn, vừa được VGS ứng trước 38,02 tỷ (TM6 tr.17; 01/01 = 0), vừa là nhà thầu dự án (theo skeptic, chưa tự kiểm). Tiền BCC có vẻ nằm trong HTM (§3). Không dùng giá BCC làm bằng chứng giá thị trường độc lập.
- **W6:** NQ 17 (05/10/2026) lấy ý kiến cổ đông bằng văn bản (ĐKCC 27/10, thực hiện 23/11/2026) chỉ để **sửa ngành nghề kinh doanh**, không phát hành, không pha loãng [CBTT]. Số CP 61.524.155 không đổi trong 2026.
- Kiểm toán AASC: FY25 chấp nhận toàn phần (24/03/2026), soát xét bán niên 2026 không ngoại trừ (24/08/2026) [FY25 tr.4–5; H1 tr.5].
- Room ngoại: chưa đo (BQ không có cột; không tìm thấy CBTT). Biên bản ĐHĐCĐ 2026 cho thấy 55% số CP dự họp.
- Rủi ro "scandal di cư": luồng hàng hoá thương mại biên 0,7% + 2 khách lớn + đối tác hai chiều + liên kết không công bố là **chỗ lợi nhuận/tiền có thể chạy ngang**. Chưa có bằng chứng sai phạm.

## 10. Giả định tự đặt (đầy đủ trong `calc/assumptions_r2.json`, md5 `c13014360aa523a102e31b5699c44db9`; vòng 1: `191bb785…`)
| Giả định | Giá trị | Cơ sở |
|---|---|---|
| DT chuẩn hoá xấu / cơ sở / tốt | 7.000 / 7.700 / 8.000 (ước lượng) | DT 2021–25 6.695–8.491; TTM 7.850 |
| GPM xấu / cơ sở / tốt | 2,5 / 3,6 / 4,3% (ước lượng) | BQ TTM Q4: đáy 2022–23, trung vị 2016–25, TTM Q3/26 |
| SG&A/DT | 1,5% (ước lượng) | TTM 1,62%, FY25 1,28% |
| Thuế | 20% | thuế hiệu dụng TTM ngoài liên kết 40,2/200,7 = 20,0% |
| Tài chính ròng chuẩn hoá | 0 (ước lượng) | nợ ròng ≈ 0; TTM −11,6 |
| Liên kết | **0,7 × sổ** / EPV TB3 / TTM × 5 (ước lượng) | phần lãi 2024 10,9, 2025 43,6, TTM 116,3 (TTM chồng FY25 Q4/25 28,7); 0,7 vì lợi suất 2024 khoảng 9% < Ke |
| Legend City | ×0,7 / ×1,0 (ước lượng) | giá vốn theo BCC với VCG (đối tác hai chiều, không độc lập sạch); xấu = GPMB còn lại + trần NOXH |
| Trọng số | 0,25/0,5/0,25; LGC 0,3/0,7 (ước lượng) | đối xứng; LGC chỉ có phía xấu có cơ sở |
| Cỡ ghi nhãn headline | ≤1 tỷ (ước lượng) | cỡ thực thi theo ADV; 5 tỷ chỉ để tham khảo |
| g, RONIC | 0; = Ke | moat NONE |

## Phụ lục nguồn
| File (`src/`) | Nội dung | Trang đã đọc |
|---|---|---|
| `BCTC-Q3-HN.pdf` (md5 `e30e74cecf7bc93ba8804050edd534a7`) | BCTC hợp nhất Q3/2026 | 1–8, 16–36 |
| `BCTC-Q3-trang.pdf` | BCTC riêng Q3/2026 | 4 (KQKD riêng) |
| `bctc-2025-hop-nhat-TV.pdf` | BCTC hợp nhất 2025 kiểm toán AASC | 5–6 (ý kiến), 9–10 (KQKD, LCTT), 21 (TM4) |
| `27.8-BCTC-giua-nien-do-trang.pdf` | BCTC hợp nhất bán niên 2026 soát xét | 6 (kết luận soát xét) |
| `BCTC-giua-nien-do-tv.pdf`, `BCTC-Q3HN-TA-1.pdf` | riêng bán niên; bản EN Q3 | tải, chưa đọc |
| `NQ_DHDCD_2026.pdf` | NQ + biên bản ĐHĐCĐ thường niên 17/04/2026 | 1–2, lướt 5–28 |
| `BB_2025-11.pdf` | NQ ĐHĐCĐ bất thường 07/11/2025 | 1–3 |
| `cbtt_NQ-SO17…pdf`, `cbtt_Thong-bao…pdf`, `cbtt_TB-ngay-DKCC…pdf` | NQ 17 + thông báo VSDC 3994 | 1 |
| `VGS_Company_profile.txt` | text trích từ profile (PDF 396 MB đã xoá sau trích) | công suất |
| BQ | `calc/bq_vgs_hist.csv`, `calc/liq_vgs.csv`, `calc/px_vgs.csv`, `calc/px_events.csv`; peer trong §5–6 | — |
| Ảnh render | `png/` | — |

**Chưa lấy được:** giải trình biến động LNST Q3 (không thấy trên trang CBTT công ty; LN tăng > 10% nên HNX có thể có, **chưa kiểm**); kế hoạch kinh doanh 2026 bằng số; BCTC liên kết; sản lượng/thị phần ống; room ngoại.

## Phụ lục E — Đính chính sau skeptic (vòng 2, 10/11/2026)
fundamental-skeptic: REFUTED mức văn bản (medium); hướng đúng (giá < tâm, luật 4 đạt mọi biến thể) nhưng độ rẻ và nhãn vùng lạc quan. Đã áp 9 điểm (trang dẫn đã đọc lại khi ghi "đã đọc lại"):
1. **[MEDIUM] Liên kết lạc quan:** thêm kịch bản xấu 0,7 × sổ (trước: 1,0 × sổ). Tâm 27.090 → **26.778**; sau CK ≤1 tỷ 26.526 (P10 19.393, P90 34.722). Nhãn @≤1 tỷ vẫn DƯỚI nhưng chỉ 0,5% dưới P10 ⇒ ghi **nhãn mong manh** (§0). Độ nhạy base = sổ 25.430, P/B 0,75 → 24.911 / 23.379 (không tái lập đúng 23.847 của skeptic). TTM chồng FY25 một quý đã ghi (§6). Luật 4 vẫn đạt.
2. **[MEDIUM] Vinaconex không độc lập sạch:** TM6 tr.17 (38,02 tỷ ứng trước, đã đọc lại); LCTT tr.5 (đặt 1.096,6 / thu 569,3, đã đọc lại; chênh 294,3 = mức Vinaconex góp thêm 204,4 → 498,7). Làm mềm chữ "độc lập" (§4); thêm W7 (§9). "Nhà thầu dự án": theo skeptic, chưa tự kiểm.
3. **[LOW-MED] Legend City hai chiều:** TM18 tr.25 (214.481,4 m² GĐ1A đã bàn giao đất, đã đọc lại) và TM10 tr.19 (mục tiêu NOXH/nhà ở thu nhập thấp, đã đọc lại). Viết cả hai (§0, §4). Mức trần NOXH cụ thể chưa tra.
4. **[LOW-MED] W3:** thêm nền 01/01/2025 và tính hai chiều của Điện Xanh Châu Á (§9). Số 01/01/2025 và 69,7 là theo skeptic, chưa tự kiểm.
5. **[LOW] W2 trích sai nguồn:** sửa thành Q3HN TM26 tr.33 (đã đọc lại), TM33 tr.34 và LCTT FY25 mã 27 (theo skeptic). Nêu cách đọc (b) và hệ quả +535 đ (đã đo, `model_out_r2.json`). Không truy hết (cần BCTC liên kết).
6. **[LOW] Nợ ròng / thanh khoản:** ~294,3 tỷ HTM có vẻ là tiền BCC; nợ ròng tự do ≈ −327,6 tỷ. Sửa câu "không có rủi ro thanh khoản" (§3). SOTP không đổi.
7. **[LOW] Moat:** giữ NONE nhưng đổi căn cứ sang biên gộp 2,3–4,9% + mua HRC từ Hòa Phát; ROIC5Y thấp do pha vốn nhàn rỗi, lõi khoảng 16% (§0, §5).
8. **[LOW] Nhãn headline:** dùng cỡ thực thi ≤1 tỷ trong §0 và `SUMMARY.json` (`headline_size_bn = 1.0`), không dùng cỡ 5 tỷ.
9. **[LOW] M1:** thêm ngưỡng trung gian (< 25 tỷ hai quý liền hoặc giảm > 50% so Q3 ⇒ trọng số 0,45/0,45/0,10, tâm −1.178 đ) (§8).

Quy trình: `assumptions_r2.json` (md5 `c13014360aa523a102e31b5699c44db9`) + `model_r2.py` khoá ở `calc/LOCK_r2_prerun.txt` trước khi chạy; giá 19.300 chỉ dùng ở `post_r2.py`, sau khoá. Không thêm nghiên cứu ngoài danh sách.
