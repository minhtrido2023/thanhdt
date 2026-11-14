# DD — PNJ (CTCP Vàng bạc Đá quý Phú Nhuận) · review trigger BCTC Q3/2026 · 2026-11-14 · job `Taylor_20261114_014836`

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị. **Không sửa `excluded_tickers`, không khôi phục PNJ** — user quyết.
> Quy trình: skill `due-diligence` (Bobby đọc ngành MÙ trước: `kb/data_registry/market-state/sector_read_ban_le_trang_suc_vang_20261114.md`).
> Nguồn: **[HN]** = BCTC hợp nhất Q3/2026 (ký 29/10/2026) · **[SX]** = BCTC hợp nhất bán niên 2026 soát xét PwC (03/09/2026) ·
> **[GT]** = CV giải trình LNST 674/2026 (29/10) · **[IR]** = báo cáo KQKD Q3/2026 + bản "Tình hình hoạt động & tài chính Q3.2026" trình
> ĐHĐCĐ bất thường 21/10 + báo cáo T7–T8 (FAQ, 25/09) · **[ĐHĐCĐ]** = tờ trình phát hành riêng lẻ 622/2026/TTr-HĐQT (29/09) + TM27 [HN] ·
> **[CBTT]** = công bố 21/08, 06/11, 13/11. Tất cả tải từ pnj.com.vn → `src/`. **[BQ]** = `tav2_bq.ticker_financial` / `ticker`.
> Đơn vị: tỷ đồng, đ/cp. Số tự đặt gắn **(ước lượng)**. Giả định khoá: `calc/assumptions.json` (r1) + `calc/assumptions_r2.json` (r2) — md5 ở §10.
> **R2 (14/11, job `Taylor_20261114_021336`)**: sửa theo phản biện fundamental-skeptic (verdict CONFIRMED cho GIỮ LOẠI/NON; khối định giá
> KHÔNG được xác nhận). Verdict NON giữ nguyên. Danh sách đính chính: **Phụ lục E**. Đối chiếu tiêu chí playbook: file nội bộ riêng
> `INTERNAL_criteria_check.md` (không thuộc bản nhà đầu tư).

## 0. Kết luận

**Đề xuất: GIỮ LOẠI (NON) — chưa đủ cơ sở cho PNJ trở lại candidate custom30V.** Cờ đổi bản chất: rủi ro **pháp lý đã GIẢM**
(công an xác nhận hồ sơ nhập khẩu kim cương của PNJ đầy đủ; bị can là cựu GĐ công ty con P-Lab), nhưng **scandal đã DI CƯ trọn vẹn sang
kinh tế doanh nghiệp**: khách ồ ạt thu đổi hàng theo chính sách mua lại trọn đời ⇒ nghĩa vụ **21.058 tỷ** giá trị thu đổi còn lại (= 1,60×
vốn chủ), dự phòng kế hoạch **7.071 tỷ** ⇒ LNST 2026 kế hoạch **−6.270 tỷ**, vốn chủ ước còn ~6.440 tỷ (ước lượng), phải phát hành riêng lẻ
tới **550 triệu cp (+107% số cp)** để huy động 8.000 tỷ.

| Câu hỏi trọng tâm | Trả lời bằng số |
|---|---|
| LN gộp/chuẩn hoá suy giảm cấu trúc? | **Có, ít nhất 2026–2028 — nhưng bằng chứng là KH của DN, không phải biên Q3.** Biên gộp Q3 báo cáo **8,7%** vs 19,8% cùng kỳ, song Q3 chứa dự phòng: cộng lại dự phòng ⇒ biên **trước dự phòng ~13,3–20,3%** (§2) — không tách được cấu trúc khỏi một lần. Bằng chứng cấu trúc thật = **KH chính DN**: LNST 2027 **0,1k**, 2028 1,2k, 2029 **1,6k** (vs 2025 2,8k); biên LN ròng KH 2028–29 **2,4–2,8%** vs 9T/2025 6,4%; trên số cp gấp ~2,07 ⇒ EPS 2029 KH ~1.507 vs 2025 ~5.527 (**−73%**) |
| Scandal di cư sang kinh doanh? | **Có** — sang khách hàng (thu đổi), ngân hàng (vay NH **−606 tỷ, −14%** trong 9T: ACB rút hẳn 500, HSBC 12, VCB giảm 802; VietinBank **tăng** 707), cơ cấu vốn (phát hành 107%), nhân sự (GĐCC Tài chính — người ký BCTC — từ nhiệm 06/11). **Chưa** sang: ý kiến kiểm toán (PwC chấp nhận toàn phần + nhấn mạnh), pháp nhân PNJ (không bị khởi tố), giấy phép |
| Giá hiện tại vs vùng DD | Giá 14.950 (13/11) **trên** cả vùng cơ sở 6.370–7.640 (KH DN, g 5%/0%) và kịch bản tốt 14.370 (n=550). ⚠️ Định giá này **CHƯA MÙ giá** (§6) ⇒ không dùng làm neo luật 4 |
| Bỏ cờ AMBIGUOUS→NON? | **Không.** Cổng xem lại sớm nhất: BCTC kiểm toán 2026 + kết quả phát hành (≈ Q1–Q2/2027); xem §8 |

Thêm một lý do CƠ HỌC (§7): rổ custom30V 05/11 **vẫn chọn PNJ** (w=0,30%, 8L=3) vì BQ còn TTM dương (PE 4,72) chưa chứa lỗ Q4 kế hoạch
−6.742 tỷ. Hiện **không có kênh mua live** (park 0%, CAPIT chưa kích hoạt — §7, đính chính r2); nhưng nếu park bật lại thì `excluded_tickers`
là rào duy nhất ⇒ bỏ loại trừ lúc này = sẵn sàng mua theo EPS cũ đã biết sai. Sau khi Q4/2026 vào BQ (~cuối T1/2027) TTM âm ⇒ bộ chọn tự loại.

## 1. Đối chiếu tiền đề của lần đánh giá trước (18/07 AMBIGUOUS → 28/09 NON)

| Tiền đề | Kiểm chứng [nguồn] | Kết quả |
|---|---|---|
| "Lãnh đạo bị bắt buôn lậu kim cương" (KB current_ops) | Bị can là **Đặng Ngọc Thảo, nguyên GĐ P-Lab** (con 100%) — khởi tố 02/07/2026 [SX TM39]. CA Thanh Hoá 21/08: PNJ "có đầy đủ hồ sơ nhập khẩu… tuân thủ đầy đủ" [CBTT 21/08] | **Sai một nửa** — không phải lãnh đạo PNJ; pháp lý pháp nhân sạch hơn đánh giá cũ. ⚠️ **WARNING quản trị (bổ sung r2)**: 14/07 thêm **1 nhân viên P-Lab bị khởi tố, được báo chí nêu là EM TRAI một thành viên HĐQT PNJ** (`calculated_fear_state_backstop.md` §7, dòng 423–427; nguồn báo chí, chưa đối chiếu CBTT) — liên kết quản trị, thu hẹp khoảng cách "cá nhân bên ngoài"; cáo buộc vẫn nhắm cá nhân |
| Lõi vàng/trang sức không bị chạm | Q3: bán lẻ −20,1%, 24K −41,4%, sỉ +69% [IR]; biên gộp 8,7% [GT]; "Từ 21/7 áp dụng chính sách chậm thanh toán do khó khăn thanh khoản" [IR] | **Sai** — lõi bị chạm qua kênh thu đổi |
| Dự phòng 7.071 tỷ (công bố 25–27/09) | Đã được ĐHĐCĐ 21/10 thông qua (giả định 80% khách thu đổi) [HN TM27]. Q3 mới ghi: dự phòng thu đổi tăng 2.236,8, dùng 1.415,4, dư 821,4; dự phòng giảm giá tồn kho 2.229,0 [HN TM7, TM17]. ⚠️ **Mâu thuẫn trong chính TM17** (r2): lời thuyết minh viết "ghi nhận khoản dự phòng tổn thất ước tính dự kiến là **6.104.276.353.481 đồng** vào BCTC hợp nhất quý 3/2026 (luỹ kế từ đầu năm 2026: **6.783.265.883.683** đồng)", trong khi bảng cùng TM cho số dư **821,4** và KQKD Q3 chỉ LNST **−256,9** — xem §9 | Theo số bảng/KQKD: phần còn lại vào Q4 ⇒ Q4 ngầm định **−6.742 tỷ** (KH −6.270 − 9T +471,7). Nếu lời TM17 đúng thì Q3 đã sai ⇒ câu hỏi cho cổng kiểm toán FY2026 |

## 2. Chất lượng lợi nhuận

| | Q3/2025 | Q3/2026 | 9T/2025 | 9T/2026 |
|---|---|---|---|---|
| DT thuần [HN] | 8.135,5 | 6.994,7 (−14,0%) | 25.353,1 | 32.703,9 (+29,0%) |
| LN gộp | 1.607,2 | 609,1 | 5.284,5 | 3.383,1 |
| Biên gộp (báo cáo) | 19,8% | **8,7%** | 20,8% | 10,3% |
| Biên gộp **trước dự phòng** (r2) | — | **13,3–20,3%** | — | — |
| CP bán hàng + QLDN | 997,9 | 869,2 | 3.256,2 | 2.708,3 |
| CP lãi vay | 24,1 | 80,4 | 85,6 | 187,8 |
| LNST cổ đông mẹ | 495,7 | **−256,9** | 1.610,4 | 471,7 |
| CFO | — | ≈ **−2.874** (9T −883,0 − H1 +1.991,1) | 1.713,9 | **−883,0** |

- **Biên trước dự phòng (r2)**: cộng lại vào LN gộp Q3 (609,1) phần dự phòng của quý, đo bằng hai cách ⇒ một **khoảng**, không phải một số:
  (i) LCTT mã 03 "các khoản dự phòng" 9T 2.987,9 [HN] − H1 2.667,2 [SX] = **320,7** (ròng, đã trừ phần sử dụng dự phòng thu đổi) ⇒ biên **13,3%**;
  (ii) dự phòng giảm giá tồn kho 30/6 **1.416,8** [SX TM8] → 30/9 **2.229,0** [HN TM7] = **+812,1** (giả định toàn bộ đi qua giá vốn) ⇒ biên **20,3%**.
  So 19,8% Q3/2025: biên gộp Q3 **không chứng minh được** suy giảm cấu trúc — cận trên ngang cùng kỳ. Bằng chứng cấu trúc chính là KH của DN (biên LN ròng 2028–29 2,4–2,8%; **biên gộp KH 2027/28/29 = 3,8/43,4 = 8,8% · 5,5/50,6 = 10,9% · 6,3/57,7 = 10,9%** vs thực hiện 2024 17,5% · 2025 21,8% [IR ĐHĐCĐ p9, đọc lại r2]).
  Kiểm chéo: FAQ 25/09 — biên gộp T7–T8 "khoảng 10%" vs ~18,5% cùng kỳ [IR T7–8 p7] (2 tháng, chưa rõ đã gồm bao nhiêu dự phòng).
- **Cơ cấu** [IR]: Q3 bán lẻ 60,4% (−20,1%), sỉ 21,4% (+69%), 24K 17,2% (−41,4%). DN đẩy bán sỉ để giữ doanh thu — kênh biên thấp (Bobby §3b **[NỀN, PHẢI KIỂM]** — đọc ngành mù, không phải số của PNJ, không dùng làm bằng chứng: sỉ "1 chữ số–thấp 2 chữ số").
  BCTC không công bố biên theo mảng ⇒ **không tách được** biên bán lẻ thật; chỉ biết biên hợp nhất sập kèm dự phòng tồn kho (DN tự nhận 2 nguyên nhân: cơ cấu + dự phòng [IR p7]).
- **Q2 bị soát xét cắt**: LNST H1 soát xét **728,5** [SX] vs Q1 1.467,4 + Q2 tự lập −282,9 = 1.184,5 ⇒ Q2 thật ≈ **−738,9** (soát xét cắt ~456 tỷ). Khủng hoảng bắt đầu từ Q2, không phải Q3.
- **Tồn kho** [HN TM7]: giá gốc 15.881 → **18.855** (+2.974 trong 9T, gần hết ở Q3); kim cương & kim cương rời **5.159,8** (dự phòng 1.684,8 = 32,7%); trang sức mua lại 1.310,6 (dự phòng 473,5). Tỷ trọng tồn kho nhóm kim cương **41% → 52%** (30/6→30/9) [IR ĐHĐCĐ]. Tiền chuyển thành hàng thu đổi kém thanh khoản.
- **Một lần vs bền**: dự phòng là một lần về kế toán, nhưng phần **mất niềm tin** thì không: số cửa hàng 432 (31/08) → **403** (30/09), 9T mở 10 đóng 38; nhân sự 8.164 → **7.123** (−12,7%) [IR, HN].
- Thu nhập khác/tài chính không che gì: lãi tiền gửi Q3 chỉ 4,5 tỷ [HN TM19.2].
- Thuế: Q3 thuế TNDN hiện hành **−220,5** (lỗ tính thuế 1.102,5); tài sản thuế hoãn lại **773,3** (31/12/25: 327,5) — thu hồi phụ thuộc lãi tương lai [HN TM23, BS 272].

## 3. Bảng cân đối & nghĩa vụ thu đổi [HN 30/09/2026]

- Tiền 1.242,2 + HTM 82,6 − vay ngắn hạn **4.320,6** = **nợ ròng ~2.996 tỷ** (31/12/25: nợ ròng ~1.637 = 4.223,4 − 522,3 − 1.966,0 − 97,9 CK KD).
- Vay NH [HN TM16]: tổng **4.223,4 → 3.616,9 (−606,5; −14,4%)**. Rút thật: **ACB 499,9 → 0**, HSBC 12,1 → 0; **VCB 1.799,2 → 997,7 (−801,5)**. Shinhan, Kasikorn, Siam Commercial **đầu năm đã 0** (vay rồi trả trong kỳ — không phải "rút về 0"). **VietinBank 571,3 → 1.278,2 (+706,9)**; Woori 161, KEB Hana 180, BIDV 1.000 giữ nguyên. TS đảm bảo: hàng tồn kho (5.111 tỷ tồn kho thế chấp). *(r1 viết "5 ngân hàng rút về 0" — sai, xem Phụ lục E.)* **Vay cá nhân Chủ tịch Cao Thị Ngọc Dung 700 tỷ, lãi 10%/năm, tín chấp**, đáo hạn 25/09/2027 [HN TM16].
- Vốn chủ 13.198,7 (mẹ 13.182,3), BVPS 30/9 ~25.760. Sau Q4 theo KH: vốn chủ ~6.440, BVPS ~12.590 (ước lượng từ KH −6.270).
- **Nghĩa vụ ngoài bảng thực chất**: giá trị thu đổi còn lại **21.057,9** (10.920,7 hàng bán 2020–26 + 10.137,2 trước 2020) [HN TM17]; KH giả định 80% khách thực hiện ⇒ ~16.500 cần tất toán, dự phòng 7.100 [IR ĐHĐCĐ p7]. Nếu 100% thực hiện thay vì 80% ⇒ lỗ thêm ~1.768 (ước lượng tuyến tính).
- **Nhu cầu vốn** [IR ĐHĐCĐ p4, p7]: nợ NH 3.000, tài trợ hoạt động 150/tháng; huy động **8.000 tỷ năm 2027** (60% xử lý thu đổi, 20% vốn lưu động, 20% trả vay).
- **Phát hành riêng lẻ** [ĐHĐCĐ tờ trình 622]: tối đa **550.000.000 cp** (≈107% số cp lưu hành 511,72tr), từ Q4/2026; giá ≥ max(TB đóng cửa 30 phiên, BVPS BCTC kiểm toán/soát xét gần nhất); hạn chế chuyển nhượng 1 năm; nhà đầu tư chứng khoán chuyên nghiệp. ĐHĐCĐ 21/10 đã thông qua [HN TM27].
  **Sàn giá ràng buộc (r2)**: BVPS soát xét gần nhất (30/6) = (13.456,5 − 17,4 NCI)/511,72tr ≈ **26.263** [SX BS; mẫu số theo BQ OShares] > giá 14.950
  ⇒ sàn = BVPS ⇒ không NĐT nào trả 26,3k cho cp giao dịch 15k ⇒ **thực tế không phát hành trước BCTC kiểm toán 2026** (~cuối 03/2027),
  khi BVPS mới ~**12.590** (ước lượng từ KH −6.270). Ở sàn đó 550tr cp chỉ huy động **~6.923 tỷ < 8.000**; muốn đủ 8.000 với 550tr cp cần giá ≥ **14.545**.
  ⇒ Thứ tự sớm nhất: kiểm toán FY2026 → hồ sơ UBCKNN → phát hành ≈ Q2–Q3/2027 (ước lượng). Hoàn nhập quỹ ĐTPT 4.602,8 vào LNST chưa phân phối (Q4/26–2027) — bù kế toán, không phải tiền.
- **Hoạt động liên tục** [SX TM2.1]: Ban điều hành nhận định đủ khả năng đáp ứng nghĩa vụ 12 tháng, dựa trên (i) giãn thời hạn thanh toán thu đổi + với nhà cung cấp, (ii) chuyển hàng mua lại thành nguyên liệu, (iii) đàm phán ngân hàng giữ hạn mức, (iv) phát hành cổ phiếu "khi phù hợp". Cơ sở là tỷ lệ mua lại "giảm dần từ tuần đầu T8".

## 4. Pháp lý / quản trị — WARNING (luật user 27/09) + rủi ro scandal di cư

| Kênh di cư | Trạng thái | Nguồn |
|---|---|---|
| Pháp nhân PNJ bị khởi tố | **Không.** Bị can = cựu GĐ P-Lab; CA Thanh Hoá xác nhận hồ sơ nhập khẩu PNJ đầy đủ | SX TM39, CBTT 21/08 |
| Kiểm toán | PwC soát xét H1: **kết luận chấp nhận toàn phần + "Vấn đề cần nhấn mạnh" TM39** (không ngoại trừ). BCTC năm 2026 chưa có | SX p3–4 |
| Khách hàng | **Có** — "giá trị thu đổi T7 gần bằng nguyên năm 2025"; chậm thanh toán từ 21/07; 15/09 HĐQT giảm thời gian thanh toán mua lại | IR, CBTT 15/09 |
| Ngân hàng | **Có, mức vừa** — vay NH −606 (−14%): ACB rút 500, HSBC 12, VCB giảm 802; VietinBank tăng 707; vay Chủ tịch 700 tỷ | HN TM16 |
| Nhân sự | TGĐ đổi 03/04 (trước vụ án); GĐCC Vận hành chuyển vai 09–10/10; TV HĐQT Đào Trung Kiên, Đặng Hải Anh rời; **GĐCC Tài chính Nguyễn Minh Hải từ nhiệm 06/11** (người được uỷ quyền ký BCTC Q3) | HN p1, CBTT 06/11 |
| Thuế | Thanh tra Chính phủ kết luận 08/08 (2777/TB-TTCP): khai sai VAT; phạt **2,0 tỷ** + truy nộp 10,0 + chậm nộp 0,97 (12/11) — nhỏ; 13/02 đã có 1 QĐ xử phạt thuế khác | CBTT 13/11, 13/02 |
| Thoái vốn | 06/11 chủ trương thoái toàn bộ CTCP Giải pháp Tài sản An Tín (PNJ 65%, lập 03/2026) | CBTT 06/11 |
| Giấy phép vàng miếng | GP 293/GP-NHNN (28/12/2012, theo NĐ 24). Hiệu lực dưới NĐ 232/2025 + NĐ 390/2026: **chưa kiểm** | src |
| Ngành (Bobby F14) | P(≥1 vụ khởi tố mới về buôn lậu/hợp thức hoá kim cương đến 30/06/2027) = 0,45 | sector read §5 |

⚠️ WARNING tổng: rủi ro pháp lý pháp nhân thấp; rủi ro **thương mại + tài chính** cao. Quản trị: dựa vào khoản vay của chính Chủ tịch là dấu hiệu cam kết nhưng cũng là tập trung rủi ro bên liên quan (tín chấp, lãi 10%).

## 5. Vị thế & lợi thế cạnh tranh (5F tầng b)

`data/moat_tags.csv` **chưa có PNJ**; không có DD/5F nào <12 tháng ⇒ làm lần đầu, gọn.
- **Loại hình**: chuỗi bán lẻ trang sức có thương hiệu + sản xuất (PNJP) + bán sỉ + 24K.
- **Bằng chứng tiền khủng hoảng** [BQ]: ROIC5Y 19,6–19,8%, ROE5Y 21,5%, ROE_Min3Y 20,1% (đến Q3/26) > Ke 13,5% nhiều năm ⇒ điều kiện (i) **đạt**. GPM TTM 17–22% 2016–2025. Peer niêm yết cùng mô hình để so biên: **cần kiểm chứng** (không có số trong lượt này).
- **Cơ chế (ii)**: niềm tin thương hiệu + chính sách thu đổi trọn đời (switching cost) + mạng lưới 31/34 tỉnh + kiểm định nội bộ (P-Lab). **Chính cơ chế này đã đảo dấu**: cam kết thu đổi thành nghĩa vụ 21.058 tỷ; kiểm định nội bộ là mắt xích bị khai thác.
- **Đồng hồ cắt hào (iii)**: **đang chạy** — mất niềm tin (cửa hàng −29 trong T9), LGD làm giảm giá kim cương tự nhiên (Bobby §3c: LGD −30,1%, thô −25% 2025) trên tồn kho kim cương 5.160 tỷ.
- **Kết luận**: `moat_tier = NARROW` (đang suy giảm), `moat_type = BRAND/SCALE`, rủi ro số 1 = niềm tin khách hàng (chính sách thu đổi). **Không thưởng moat trong mô hình** (fail (iii)); cũng không trừ: dùng nguyên KH của DN làm base.
- Dòng đề xuất cho `data/moat_tags.csv` (KHÔNG tự sửa; người curate quyết):
  `PNJ,NARROW,BRAND/SCALE,M,"Trust collapse after 07/2026 P-Lab diamond case turned lifetime trade-in policy into 21,058bn VND exchange liability (1.6x equity); 7,071bn provision; up to 550m-share private placement; LGD deflates natural-diamond inventory",2026-11-14,dd_PNJ_20261114,N`
- Ngành (Bobby, mù): 12T CYCLICAL 0,40 / ADMIN 0,40 / STRUCTURAL 0,20; 36T STRUCTURAL 0,45 (chính thức hoá có lợi chuỗi **tuân thủ, sạch**). Khủng hoảng PNJ là **riêng doanh nghiệp**, không phải ngành: Bobby đọc cầu trang sức "gần đáy chu kỳ" — thuận cho phục hồi nếu niềm tin hồi.

## 6. Định giá — ⚠️ **CHƯA MÙ giá thị trường** (đính chính r2)

> **Ghi trung thực quy trình r1**: lượt r1 đã **truy vấn Price/PE/PB của PNJ lúc ~01:51Z, TRƯỚC khi khoá kịch bản/`assumptions.json`
> lúc ~01:55Z** (mốc theo phản biện skeptic; r2 đo được: `calc/assumptions.json` mtime **01:59:54Z** — vẫn sau truy vấn giá). Nhãn "MÙ giá thị trường" của r1 vì vậy **sai** và đã gỡ. Hệ quả:
> **tâm 6.440 và ngưỡng "rẻ" 5.470 KHÔNG được dùng làm neo cho luật 4** (giá < tâm 15% ⇒ xét candidate discretionary) cho tới khi
> dựng lại ở **một lượt mù giá thật**: phiên mới, không truy vấn Price/PE/PB/giá, khoá `assumptions.json` + md5 TRƯỚC khi so giá.
> **R2 KHÔNG làm được lượt mù**: phiên r2 đã đọc REPORT r1 chứa giá 14.950 và chuỗi giá sự kiện ⇒ mọi tham số đặt trong phiên này đều
> nhiễm giá. Trạng thái: **"chưa mù"**. Số dưới đây là định giá tham khảo, không phải neo hành động.
> Lưu ý thêm: **trọng số kịch bản r1 (0,20/0,50/0,30) được thêm SAU thông báo "khoá"** ⇒ r2 không dùng tâm có trọng số.

**Khung**: giá trị vốn chủ SAU tái cấp vốn F = LNST chuẩn hoá 2029 × (1+g)(1 − g/ROE)/(r − g), chiết khấu 3 năm về cuối 2026; chia cho
(511,72 + n_mới) triệu cp. Tiền huy động mới bị nghĩa vụ thu đổi tiêu hết (60/20/20) nên không cộng thêm. r = **13,5%** @ lãi huy động 12T hiệu
dụng **7,40%** (CCTG 12M 02/11; `effective_deposit_rate` 14/11 = 7,40% = điểm neo 03/11 ⇒ r giữ nguyên). g = 5% (ước lượng). Tái đầu tư chặn [0; 0,8].
Không có dự án mới cần NPV=0 (capex 9T 57,4 tỷ, XDCB 31,7). Chiết khấu thanh khoản **0%**: ADV trung vị 20 phiên **141,3 tỷ**, 60 phiên 156,5 tỷ [BQ] — vị thế 1% NAV live (~10–20 triệu đ) không đáng kể.

**Bảng r2** (`calc/model_r2.py` → `model_r2_out.json`; r2 **bỏ trọng số** và **bỏ kịch bản xấu 800/6% của r1** vì không có cơ sở dữ liệu):

| Kịch bản | LNST 2029 | ROE | đ/cp n=550tr, g=5% | g=0 | n=400tr, g=5% |
|---|---|---|---|---|---|
| Tốt — thương hiệu hồi về kinh tế 2023–25 | 2.500 (ước lượng) | 18% | **14.368** | 11.929 | 16.731 |
| **Cơ sở — đúng KH của DN** | 1.600 [IR ĐHĐCĐ p9] | 10% (=1,6k/~15,8k VCSH, ước lượng) | **6.366** | **7.635** | 7.413 |
| Xấu (r2) — KH trễ 1 năm: 2029 chỉ đạt mức KH 2028 | 1.200 [IR ĐHĐCĐ p9] | 7,6% (=1,2k/15,8k, ước lượng) | **3.267** | 5.726 | 3.804 |
| ~~Xấu r1 — 800 / 6%~~ (đã bỏ: không có cơ sở) | ~~800~~ | ~~6%~~ | ~~1.273~~ | ~~3.817~~ | ~~1.483~~ |

- **Vùng tham khảo r2 = kịch bản cơ sở 6.370–7.640** (g 5% → 0%). Với ROE < Ke, tăng trưởng **huỷ** giá trị ⇒ g=0 cho số CAO hơn g=5%; g=5% của r1 là phía bi quan.
- **Độ nhạy theo MỨC lợi nhuận 2029** (ROE = N/15,8k VCSH, ước lượng; n=550):
  N=1.200 (KH 2028) → 3.263 (g5) / 5.726 (g0) · **N=1.600 (KH 2029) → 6.446 / 7.635** · N=2.113 (trung vị 2023–25) → 10.527 / 10.082 · N=2.828 (2025) → 16.221 / 13.497.
  ⇒ giá trị nhạy mạnh theo MỨC lợi nhuận (×5 từ 1.200 → 2.828), mạnh hơn nhiều so với tỷ lệ giữ lại.
- ⚠️ **Thiên bi quan cấu trúc của khung**: khung vốn hoá **vĩnh viễn** năm 2029 của DN, khi NPM KH 2029 mới **2,8%** (2028: 2,4%) vs 9T/2025 **6,4%** — 2029 là năm còn đang phục hồi theo chính KH DN (doanh thu KH +16,6% 2028, +14,0% 2029), không phải trạng thái ổn định. Nếu NPM về mức 9T/2025 (6,4%) trên doanh thu KH 2029 57,7k thì N ≈ 3,7k (ước lượng; NPM năm 2025 = 2,8/35,4 = 7,9% ⇒ ~4,6k) — ngoài lưới trên. Phía lạc quan này **không** được định lượng có trọng số vì không có dữ liệu xác nhận niềm tin hồi.
- ~~Trọng số 0,20/0,50/0,30 ⇒ 6.438~~ (r1): trọng số chủ quan, **được thêm vào sau thông báo "khoá"** ⇒ gỡ khỏi tâm.
- **Độ nhạy ROE (cơ sở, n=550)**: 10% → 6.366 · 13,5% (=Ke) → 8.016 · 20% (tiền khủng hoảng) → 9.549. Đây cũng là độ nhạy moat NONE/NARROW/WIDE-cũ.
- **Độ nhạy lãi huy động (cơ sở, β=1)**: −100bp 7.409 (+16,4%) · −50bp 6.854 (+7,7%) · +50bp 5.934 (−6,8%) · +100bp 5.548 (−12,8%). β=0,5: 6.854 / 6.602 / 6.143 / 5.934.
- **Hai nền (chỉ hiển thị)**: V_dài (FCFE) **không tính** — CFO TTM âm (Q3/26 −2.579,5; TB 3 TTM **−340**), trượt cổng CFO. **V_ngắn** (LNST chuẩn hoá = trung vị năm 2023–25 = 2.112,9; ROE 21,5%) = **37.280 đ/cp trước pha loãng/nghĩa vụ**; sau pha loãng 550tr = **17.968**. Nền này giả định lợi nhuận tiền khủng hoảng quay lại ngay — chính điều đang bị nghi ngờ ⇒ không dùng làm tâm; nó là trần trên lý thuyết. D không tính (thiếu V_dài). **C4/D2**: CFO3 âm ⇒ không có nghĩa (dòng tiền nằm trong tồn kho vàng/kim cương).
- Kiểm chéo sổ sách: BVPS sau Q4 + 8.000 tỷ mới ≈ (6.440 + 8.000)/1.061,7 ≈ **13.600** (ước lượng); với ROE 10% < Ke, P/B hợp lý < 1 ⇒ giá trị < 13.600 — khớp chiều với bảng.

**Phản ứng giá quanh sự kiện** [BQ, Price]: 01/07 62.700 → 09/07 50.000 (khởi tố P-Lab) → 22/07 35.500 (chậm thanh toán thu đổi) → 21/08 37.300 → 25/08 42.650 (CA xác nhận hồ sơ, 22,4tr cp) → 28/09 30.700 (công bố dự phòng 7.071) → 01/10 24.750 → 30/10 15.500 (BCTC Q3) → 13/11 **14.950** (−77% từ 23/06 65.200).

## 7. Hệ quả cơ học với custom30V (lý do giữ loại tới khi Q4 vào BQ) — viết lại r2

- **Hiện KHÔNG có kênh mua live nào cho PNJ qua custom30V**: park = **0%** (`data/trading_rules.json:49` `neutral_parking.default_park_of_idle_pct = 0.0`, từ 01/10, chỉ đổi khi user quyết) và CAPIT **chưa kích hoạt** (`data/golive_v23_status.json` `n_capit_basket = 0`). r1 viết "thứ duy nhất chặn mua là `excluded_tickers`" — **sai về hiện trạng**.
- `tav2_bq.custom30v_8l` rebal **2026-11-05**: PNJ **còn trong rổ** w=0,30%, rating_8l=3, liq_rank 14 (08/05: 0,71%, 8L=2). **NẾU park được bật lại**, `excluded_tickers` của 2 account sẽ là **rào duy nhất** — vì PARK được **miễn cổng cờ** (anomaly/fear flag) theo quyết định 03/11 (theo dispatch Mike/skeptic; r2 chưa tự đọc lại văn bản quyết định).
- Lý do: BQ TTM NP Q4/25–Q3/26 = 1.218,1 + 1.467,4 − 282,9 − 256,9 = **2.145,7** ⇒ PE 4,72 (ngày release), PB 0,6. Không chứa Q4/26 kế hoạch −6.742 và Q2 chưa cập nhật số soát xét (−738,9).
- Khi BCTC Q4/2026 vào BQ (~cuối T1/2027): TTM ≈ 1.467,4 − 738,9 − 256,9 − 6.741,7 ≈ **−6.270** (ước lượng) ⇒ PE âm, LNST năm âm ⇒ 8L nhiều khả năng ≥4 ⇒ gate ≤3 tự loại ở rebal 02/2027. **Bỏ loại trừ trước mốc đó = giữ PNJ ~3 tháng trên EPS cũ đã biết sai.**

## 8. Vùng giá & điều kiện đổi nhận định (HAI chiều)

- **R2 — CHƯA MÙ (§6)**: vùng tham khảo cơ sở **6.370–7.640** (KH DN, g 5%/0%) · lưới mức lợi nhuận [3.260; 16.220] (n=550) · tốt 14.370.
  ~~Tâm 6.440 / "rẻ" ≤ 5.470~~ (r1) **bị đình chỉ làm neo luật 4** cho tới lượt mù giá thật.
- Giá 14.950 ⇒ **trên kịch bản tốt** (n=550) ⇒ nhãn ĐẮT so mô hình (kết luận chiều này bền với cả g=0 và bỏ trọng số). Lưu ý vòng phản hồi: giá thị trường quyết định giá phát hành ⇒ quyết định n_mới; giá cao hơn ⇒ ít cp mới hơn ⇒ giá trị/cp cũ cao hơn (n=400tr, cơ sở: 7.413–8.891).

| Mốc (khoá trước) | LÊN (xét lại candidate) nếu | XUỐNG (NON cứng) nếu |
|---|---|---|
| BCTC Q4/2026 (~30/01/2027) | Dự phòng thu đổi lũy kế ≤ 7.071; **CFO Q4/2026 tốt hơn cùng kỳ Q4/2025 (−1.695,0** [BQ CF_OA_P0]; Q4 âm theo mùa Tết, Q4/2024 −1.573,3); **biên gộp TRƯỚC dự phòng** quý ≥ 15% (quý ghi nốt dự phòng ⇒ không dùng biên báo cáo) | Dự phòng > 7.071 (thu đổi > 80%) hoặc thêm dự phòng giảm giá kim cương lớn; CFO Q4 xấu hơn −1.695 |
| Phát hành riêng lẻ (sớm nhất sau BCTC kiểm toán 2026, ≈ Q2–Q3/2027 — sàn giá = BVPS soát xét/kiểm toán, §3) | Hoàn tất ≥ 6.000 tỷ với NĐT tổ chức có tên | **Chưa hoàn tất trước 31/12/2027** (hết năm KH huy động 8.000), hoặc < 4.000 tỷ, hoặc chủ yếu bên liên quan, hoặc DN xin hạ sàn giá dưới BVPS |
| BCTC kiểm toán 2026 (~03/2027) | PwC chấp nhận toàn phần, không nghi ngờ hoạt động liên tục | Ngoại trừ / "nghi ngờ đáng kể về hoạt động liên tục" |
| Q1/2027 (Tết + Thần Tài ~giữa T2/2027) | Bán lẻ YoY ≥ −10%, biên gộp (trước dự phòng nếu có) ≥ 15%, cửa hàng ổn định | Bán lẻ tiếp −20%, đóng thêm >30 cửa hàng |
| Ngân hàng / bên liên quan | Hạn mức được nối lại (≥1 ngân hàng nước ngoài quay lại) | Thêm vay bên liên quan; vi phạm điều khoản vay |
| Pháp lý | — | Khởi tố mới chạm pháp nhân PNJ hoặc P-Lab đang hoạt động |
| BCTC kiểm toán 2026 — mâu thuẫn TM17 (§9) | Kiểm toán làm rõ con số 6.104/6.783 và khớp với số dư dự phòng + KQKD | Điều chỉnh hồi tố Q3 / ý kiến về dự phòng thu đổi |
| Giá | ~~≤ 5.470~~ — **đình chỉ** tới khi có lượt định giá mù giá thật (§6) | — |

Điều kiện mở lại candidate custom30V = (1) Q4/2026 đã vào BQ và 8L ≤ 3 tính trên TTM mới **và** (2) phát hành xong **và** (3) kiểm toán 2026 không ngoại trừ/không nghi ngờ hoạt động liên tục. Sizing nếu mở lại: theo bộ chọn (custom30V), không cộng tay.

## 9. Lệch nguồn BQ vs BCTC (ghi, không im lặng chọn)

- `NP_P0` 2026Q2 = **−282,9** (Q2 tự lập) — soát xét H1 ngầm định Q2 **−738,9**; BQ chưa cập nhật (lệch −456).
- `Revenue_P0` 2026Q3 = 7.076,8 = **doanh thu GỘP** (mã 01), không phải thuần 6.994,7.
- `GPM_P0` 2026Q3 = 0,1366 = **TTM**, không phải biên quý 8,7%.
- `Cash_P0` 1.242,2 = tiền & tương đương, thiếu HTM 82,6.
- `PE` 4,72 / `PB` 0,6: dựa TTM cũ và BVPS 25.793 trước dự phòng Q4 — gây ảo giác "rẻ".
- `NP_P0` 2026Q3 −256,9 khớp BCTC (mẹ −256,87). `OShares` 511,72tr khớp VĐL trừ cp quỹ.
- **Lệch NỘI BỘ BCTC Q3 — TM17 (r2, không chọn im lặng)**: lời thuyết minh (*) viết Ban Điều hành "ghi nhận khoản dự phòng tổn thất ước
  tính dự kiến là **6.104.276.353.481 đồng** vào Báo cáo tài chính hợp nhất quý 3/2026 (luỹ kế từ đầu năm 2026: **6.783.265.883.683** đồng)".
  Nhưng cùng TM17: dự phòng thu đổi tăng 2.236,8 / dùng 1.415,4 / **số dư 821,4**, bảng "giá trị tổn thất tương ứng" tổng 821,4; KQKD Q3
  LNST mẹ **−256,9**; LCTT mã 03 Q3 chỉ +320,7. Hai cách đọc: (a) câu chữ là ước tính **dự kiến** (gần khớp phần lớn KH 7.071) bị ghi
  nhầm "vào BCTC Q3" ⇒ số bảng đúng, Q4 gánh ~6.742; (b) câu chữ đúng ⇒ BCTC Q3 thiếu dự phòng ~5.300 (ước lượng) ⇒ sai trọng yếu.
  r2 dùng (a) cho mọi số trong báo cáo (khớp KQKD/BS/LCTT), **nhưng đây là câu hỏi bắt buộc cho cổng kiểm toán FY2026** (§8).

## 10. Nguồn & khoá giả định

- `src/3b_-_20261030_-_PNJ_-_BCTC_quy_3_nam_2026__Hop_nhat_.pdf` (BS p2–3, KQKD p4, LCTT p5, TM7 p19, TM16 p24–25, TM17 p26, TM18 p27, TM19–23 p28–29, TM27 p32), `3a_…Rieng_.pdf` (chưa đọc chi tiết — riêng: DT 7.842,8, LNST −393,2 theo [GT]), `3c_…giai_trinh…pdf`, `79c_…soat_xet_ban_nien…Hop_nhat_.pdf` (p3–4 PwC, p8–9, TM2.1 p11–12, TM39 p51), `Cap-nhat-tinh-hinh-hoat-dong-tinh-hinh-tai-chinh-Q3-2026.pdf`, `2026.07.30_PNJ-Q3.2026_Report-VN_8.pdf` (tên file DN đặt nhầm ngày, nội dung Q3), `2026.09.25_…T07.08…pdf`, `EGM_proposal_private_placement_EN.pdf`, `EGM_resolution_20261021.pdf` (chưa đọc tỷ lệ biểu quyết), `20260821_…CAP_NHAT…pdf`, `20261106_*`, `20261113_CBTT_QD_xu_phat…pdf`, `21_-_Giay_phep…pdf`, `FY2025_audited_HN.pdf` (chưa đọc).
- BQ: `ticker_financial` (PNJ 2015Q4–2026Q3), `ticker` (giá/ADV tới 2026-11-13), `custom30v_8l` (rebal 2026-11-05). Lãi suất: `deposit_rate_vn.effective_deposit_rate('2026-11-14')`.
- Ngành: `kb/data_registry/market-state/sector_read_ban_le_trang_suc_vang_20261114.md` (Bobby, blind: YES). Vĩ mô: `macro_snapshot_20261114.md` (chỉ bối cảnh; bán lẻ +14,7% YoY T10, CPI 5,09%, ô tô −28,4% — không đổi giá trị nội tại).
- Khoá r1 (giữ nguyên, không sửa): `calc/assumptions.json` md5 **4e3fce77fa22d0b2cd8a8d4d7f8be463**; `calc/model.py` md5 7996ffb6dd545d46f6f11fd07b10a0d3; output `calc/model_out.json`. ⚠️ r1 **không mù giá** (§6).
- Khoá r2: `calc/assumptions_r2.json` md5 **0efafe3c1c3d31282ece9af7c0d1653d** (kế thừa r1 + khối `r2` có nguồn từng trường); `calc/model_r2.py` md5 62df005900703347a056838b0bbb82e6; output `calc/model_r2_out.json` md5 bd9fa7f7d34cd49ce03781f0313a5398. REPORT md5 r2: `calc/LOCK_r2_md5.txt`. ⚠️ r2 cũng **không mù giá**.
- Nguồn r2 đọc thêm (render ảnh trang, PDF scan): HN Q3 LCTT p5 in, TM7 p19, TM16 p24–25, TM17 p26; SX BS p7, LCTT p9, TM8 p29; `Cap-nhat…Q3-2026.pdf` p9 (KH 2027–29); `2026.09.25_…T07.08` p7 (FAQ biên T7–8). BQ: `ticker_financial` CF_OA_P0 2024Q4/2025Q4.
- Chưa làm (để skeptic biết): BCTC riêng chi tiết; BCTC kiểm toán 2025 (ý kiến); biên bản ĐHĐCĐ 21/10 (tỷ lệ thông qua); trạng thái giấy phép vàng miếng dưới NĐ 232/390; peer so biên; **lượt định giá mù giá thật** (r2); văn bản quyết định 03/11 miễn cổng cờ cho PARK (r2 dẫn theo dispatch); đối chiếu CBTT cho liên kết "em trai thành viên HĐQT".

## Phụ lục E — Đính chính của fundamental-skeptic (r2, 14/11/2026)

Verdict skeptic: **CONFIRMED** cho GIỮ LOẠI/NON; **khối định giá KHÔNG được xác nhận**. Verdict NON **không đổi**. Mỗi số skeptic nêu đã được r2
**đọc lại từ trang nguồn** trước khi áp (trừ chỗ ghi khác).

| # | Đính chính | Đã áp? | Ở đâu / ghi chú |
|---|---|---|---|
| 1 | Nhãn "MÙ giá thị trường" sai — giá/PE/PB đã truy vấn trước khi khoá kịch bản | **Áp một phần** | Gỡ nhãn, ghi trung thực (§6); tâm 6.440 / "rẻ" 5.470 **đình chỉ** làm neo luật 4 (§0, §8). **Lượt mù giá thật KHÔNG làm được** trong r2 (phiên đã nhiễm giá) ⇒ trạng thái "chưa mù" |
| 2 | Biên gộp Q3 8,7% chứa dự phòng; bằng chứng cấu trúc là KH DN | Áp | §0, §2: biên trước dự phòng **13,3–20,3%** (LCTT 03: 320,7 / Δ dự phòng tồn kho +812,1); biên gộp KH 2027–29 **8,8/10,9/10,9%** đọc lại p9 |
| 3 | "5 ngân hàng rút về 0" sai | Áp | §0, §3, §4: tổng −606,5 (−14,4%); ACB −499,9, HSBC −12,1 rút thật; Shinhan/Kasikorn/SCB đầu năm đã 0; VietinBank +706,9. **Bổ sung skeptic bỏ sót: VCB −801,5** (1.799,2 → 997,7) |
| 4 | Mâu thuẫn TM17 (6.104 / 6.783 vs số dư 821,4, LNST Q3 −257) | Áp | §1, §9, §8 (cổng kiểm toán FY2026) |
| 5 | Sàn giá phát hành = max(TB30, BVPS) | Áp | §3: BVPS soát xét 30/6 ≈ **26.263** (đo từ SX BS) > giá ⇒ không phát hành trước kiểm toán 2026; ở BVPS ~12.590 (ước lượng) 550tr cp ⇒ ~6.923 < 8.000; §8: mốc + điều kiện XUỐNG đổi sang "chưa hoàn tất trước 31/12/2027" |
| 6 | §7 sai hiện trạng: park=0, CAPIT chưa kích hoạt | Áp | §7 viết lại (trading_rules.json:49 = 0.0; n_capit_basket = 0 đã đọc). Miễn cổng cờ PARK 03/11: dẫn theo dispatch, chưa đọc văn bản |
| 7 | Điều kiện LÊN Q4: CFO so cùng kỳ; biên trước dự phòng | Áp | §8: CFO Q4/2026 vs Q4/2025 **−1.695,0** (BQ đã kiểm); biên gộp TRƯỚC dự phòng |
| 8 | Kịch bản xấu 800/6%/0,30 không có cơ sở; thêm g=0, độ nhạy mức LN; trọng số thêm sau khoá; thiên bi quan 2029 | Áp | §6: bỏ bear r1, thay "KH trễ 1 năm" (N=1.200 = KH 2028 của DN); g=0 cơ sở **7.635**; lưới mức N 1.200→2.828; bỏ trọng số khỏi tâm; nêu NPM 2029 KH 2,8% vs 9T/2025 6,4% |
| 9 | WARNING quản trị (em trai TV HĐQT); Bobby §3b chỉ là nền | Áp | §1 (WARNING, nguồn báo chí qua backstop §7 dòng 423–427); §2 nhãn **[NỀN, PHẢI KIỂM]** |
| 10 | Bảng đối chiếu §2 #1–#5 + danh sách KHÔNG ĐỦ — tách nội bộ | Áp | File riêng `INTERNAL_criteria_check.md` (**không** thuộc bản nhà đầu tư) |
