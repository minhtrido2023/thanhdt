# DD — TV2 (CTCP Tư vấn Xây dựng Điện 2 / PECC2, HOSE) · **v3 (sau phản biện)** · as-of 01/11/2026 · job `Taylor_20261101_043110` (v2 giữ nguyên ở `REPORT_v2.md`)

> NGHIÊN CỨU READ-ONLY (v3 = v2 + toàn bộ đính chính của người phản biện `SKEPTIC_20261101.md`, xem Phụ lục cuối). Không khuyến nghị, không lệnh, không wire.
> Khung: skill `dd-investor-report` luật 12 — tích cực và tiêu cực cùng chuẩn chứng cứ; **không** dùng nhãn nội bộ; kết luận = vị trí giá so với vùng giá trị hợp lý + 3 kịch bản có xác suất.
> **Nguồn:** [Q3 tr.X] BCTC hợp nhất Q3/2026 (chưa soát xét, ký 28/10/2026) · [H1 tr.X] BCTC HN bán niên 2026 soát xét UHY · [RIENG TMx] BCTC riêng Q3/2026 · [GT] giải trình 4270/PECC2-TCKT · [BCTN25], [NQ26], [BB26], [BCQT6T], [FOL], [NQ-NCLQ]: xem `GAPS.md` · [BQ] `tav2_bq` (lịch sử; KHÔNG dùng cho giá hôm nay) · [DNSE] `calc/dnse_raw.json` (secdef/latest_trade/ohlc, lấy 01/11/2026 11:1x ICT).
> Phép tính: `calc/valuation.py` (v3) → `calc/valuation_out.txt`; v2 lưu `calc/valuation_v2.py`/`_out.txt`; P/E theo pha `calc/pe_by_phase.py` → `calc/pe_by_phase_out.txt`; lịch sử `calc/hist_out.txt` (script sinh file này không được lưu ở v2 — số trung vị nay tái lập bằng `pe_by_phase.py`, khớp: TV2 2014+ 8,75, 2019+ 10,99); giá `calc/dnse_px_out.txt`; DD 28/10 `../dd_TV2_20261028/calc.py` → `out.txt`. Số tự đặt gắn **(ước lượng)**.
> Ngành: đọc độc lập `kb/data_registry/market-state/sector_read_power_consulting_20261028.md` (đọc mù, không biết mã/giá).

## 0. Kết luận

**Giá 27.000 đ (đóng cửa 30/10/2026, HOSE [DNSE secdef `marketId=STO`, latest_trade 14:45:07]) cao hơn giá trị kỳ vọng có trọng số ~20.700 đ khoảng 31%, và cao hơn đỉnh vùng cơ sở 17.100–25.300 đ khoảng 7%** (ước lượng; `calc/valuation_out.txt`). Neo P/E dùng **pha LN đỉnh 2017–21 của chính TV2 (trung vị 7,45x)**, không dùng P/E thời LN đáy. Độ nhạy: kỳ vọng 19.600–22.400 khi dải P/E đổi 6,5–8,5x … 7,5–10x; 19.700–21.600 khi trọng số đổi 30/50/20 … 20/50/30 ⇒ giá **cao hơn kỳ vọng 21–38%** trong mọi biến thể có căn cứ. Chỉ khi dùng P/E 9–11x (trung vị 2019+ 11,0 lẫn pha LN đáy) khoảng cách mới thu về +7%.

**Cách dựng vùng cơ sở (khai rõ):** góc-tới-góc LN 165×7x … LN 190×9x = 17.100–25.300; một chiều P/E 7–9x tại LN tâm 177,5 = 18.400–23.700; một chiều LN 165–190 tại 8x = 19.500–22.500; tâm 21.000. Giá 27.000 chỉ "trong vùng" nếu **đồng thời** LN ≥203 tỷ (trên đỉnh LN cơ sở) và P/E 9x (đỉnh dải).

**Thị trường đang định giá gì:** ở 27.000 (vốn hoá 1.823 tỷ), P/E 7,45x (trung vị pha đỉnh) ngầm định LNST bền vững **~245 tỷ/năm**; 9x ⇒ ~203 tỷ — tức coi LN 2026 (ước 217–242 tỷ, gồm lãi trên tiền ứng) là **bền vững 2027–28 ở mức đỉnh chu kỳ trước**. Giữ xác suất tiêu cực 25%, kỳ vọng tối đa đạt được (75% tích cực, 0% cơ sở) là ~25.000 < 27.000; bỏ hẳn tiêu cực thì cần P(tích cực) ~70%.

| | Tích cực (có chứng cứ) | Tiêu cực (có chứng cứ) |
|---|---|---|
| Tăng trưởng | Backlog **4 HĐ EPC** đã ký: Ô Môn IV (PVN 1.155 MW, cùng Doosan, COD 12/2028), eREX Yên Bái 1 + Tuyên Quang (50 MW mỗi nhà máy), Tân Thuận GĐ3 (25 MW); DT phân bổ chủ yếu 2026–28 [BB26]. EPC **nguồn** (khí PVN, sinh khối Nhật, gió) nằm ngoài trần tài chính EVN | EPC biên mỏng: biên gộp mẹ 9T **9,7%** [RIENG TM21-22]; EBIT lõi/DT 9T 6,4% [Q3 tr.6] |
| Kế hoạch | LNST 9T đạt **163% kế hoạch cả năm HN** (~100 tỷ, ban lãnh đạo nêu tại ĐHĐCĐ) ⇒ kế hoạch thận trọng; biên LNST 9T thực tế 13,6% [Q3 tr.6; BB26] | Cổ đông tại ĐHĐCĐ chỉ ra kế hoạch HN (DT 2.500, LN ~100) ngụ ý biên LNST ~4% [BB26 ý kiến 4] |
| Tiền | Tiền + HTM **2.104 tỷ**, vay chỉ 152,8 [Q3 tr.3-4]; tiền lãi và cổ tức đã thu 109,2 (LCTT dòng 27, gồm ~5 tỷ cổ tức) [Q3 tr.7] | Gần như toàn bộ tiền là **tiền ứng của khách** (2.418,6) — tiền ròng "của cổ đông" ≈ −55 tỷ nếu coi float là nợ (ước lượng) |
| Lịch sử | Đã có 5 năm LNST **214–272 tỷ** (2017–21) khi chu kỳ EPC lên [BQ] | Sau đó **sập ~70%** (2022: 77 tỷ) khi hết HĐ [BQ]; ở pha đỉnh thị trường chỉ trả **~7,45x** |
| Vị thế | Oligopoly tư vấn điện gốc EVN: gói 500kV 1–2 nhà thầu, giảm giá 1–5% (đọc ngành); ~50 kỹ sư hạt nhân [BB26]; O&M 48 nhà máy | Mảng lưới EVN co lại 2026 (khách EVN ~8% DT 9T, ước lượng); lưới bị trần tài chính EVN (đọc ngành) |
| Bên liên quan | CMC tái cơ cấu nợ 2025, bắt đầu có lãi; GĐ3 COD Q4/2026 [BB26; QĐ 2230 Cà Mau] | Phải thu CMC **657–666 tỷ** + đầu tư 188,6 = **~64% VCSH mẹ**, không dự phòng, gần như chưa thu tiền Q3 |
| Quản trị | Cổ tức tiền mặt 10%/năm đều; FY2026 ≥10% [NQ26]. **Đã ký HĐ kiểm toán + soát xét BCTC 2026 với UHY ngày 15/07/2026** [CBTT 2604/PECC2-TC&PC] — giảm rủi ro đuôi "không có kiểm toán viên" | ⚠️ cựu Chủ tịch + KTT bị khởi tố **tham ô (Đ.353)**; Q3 chưa soát xét; room ngoại **0%** từ 14/09; họp báo Bộ Công an 02/07 nêu 13 pháp nhân vi phạm gồm "các công ty tư vấn xây dựng điện" (không nêu tên) |
| Bảng cân đối | Không vay đáng kể; không rủi ro thanh khoản 12 tháng | P/B 1,37 > P/B hợp lý theo ROE 12,7% (~0,9–1,1) |

**3 kịch bản (LNST bình quân 2027–28, ước lượng; P/E neo pha LN đỉnh):**

| Kịch bản | P | Giả định | LNST | P/E | Giá trị/cp |
|---|---|---|---|---|---|
| Tích cực | 25% | Lặp lại chu kỳ 2019–21: HĐ mới (BOP khí/LNG, Philippines, tư vấn hạt nhân), CMC thu đủ | 230–270 | 7–9 | **23.800–36.000** (tâm ~29.600; ở 10x ~37.000) |
| Cơ sở | 50% | 4 HĐ EPC đúng tiến độ; tư vấn + O&M ổn định; TC ròng giảm còn 50–70 khi giải ngân thiết bị; LK ~30 | 165–190 | 7–9 | **17.100–25.300** (tâm ~21.000) |
| Tiêu cực | 25% | Vượt chi phí EPC/trễ tiến độ, lãi float giảm nhanh, CMC trích lập ~100 tỷ trước thuế (−80 sau thuế, một lần) | 100–120 | 7–8 | **9.200–13.000** (tâm ~11.000) |

Trọng số 25/50/25 giữ như v2 nhưng **không phải căn cứ dữ liệu mới**; DD 28/10 dùng 30/50/20 ⇒ kỳ vọng ~19.700 (độ nhạy đầy đủ §8d). Cân bằng phía dưới: tâm tiêu cực 11.000 ứng P/B ~0,56 — thấp hơn mọi tháng của TV2 từ 2014 (thấp nhất 0,92; từ 2017 thấp nhất 1,04); nếu định tiêu cực theo P/B sàn 0,8–1,0 của nhóm PECC hiện tại thì kỳ vọng ~22.100 (giá vẫn cao hơn ~22%). Đuôi nặng hơn tiêu cực: mất 50% phơi nhiễm CMC ⇒ −5.100 đ/cp (ước lượng).

**Điều làm nhận định TÍCH CỰC hơn:** (1) Q4/2026 hoặc BCTC kiểm toán 2026 cho thấy **phải thu CMC giảm ≥30%** sau COD Tân Thuận GĐ3; (2) CFO năm 2026 trừ biến động float ròng ≥ 0; (3) công bố HĐ EPC/tổng thầu mới có giá trị (gói BOP LNG, Philippines) hoặc tư vấn NT1 có HĐ ký — tức bằng chứng LN ~230 tỷ+ kéo dài sau 2028, thứ có thể biện minh P/E cao hơn pha đỉnh 2017–21; (4) kiểm toán FY2026 chấp nhận toàn phần, không đoạn ngoại trừ; (5) ĐHĐCĐ 2027 sửa ngành nghề, nâng room ngoại. **Điều làm TIÊU CỰC hơn:** (1) phải thu CMC >700 tỷ hoặc trích lập; (2) Tân Thuận GĐ3 trượt COD sang 2027; (3) pháp nhân TV2 bị khởi tố/cấm thầu, hoặc kết luận điều tra quy trách nhiệm kế toán tại TV2; (4) biên gộp Q4 <8% hoặc ghi nhận lỗ HĐ (vượt chi phí thiết bị nhập, tỷ giá INR/USD); (5) lãi TC ròng giảm >50% YoY mà EBIT lõi không bù.

## 1. Kiểm lại số dùng lại từ DD 28/10 (không làm lại phần đã kiểm đúng)
DD 28/10 §13: skeptic tự kiểm 20 số then chốt trên ảnh, 0 sai. Vòng này kiểm thêm trên ảnh/tài liệu:
| Số | Kiểm | Kết quả |
|---|---|---|
| Phải thu CMC TM3 / TM32 | [Q3 tr.25] 657.327.141.975 / [Q3 tr.43] 666.374.010.268 | ✅ cả hai đúng như đọc; **lệch nội bộ BCTC** (xem §6) |
| DT CMC 9T 478,7 và dòng −58,1 | [Q3 tr.43] 478.727.859.941 / (58.123.047.367) | ✅ |
| EVN 51,33% | [RIENG TM20.1] 346,59 tỷ / 675,26 tỷ; [BCTN25 tr.38]; [NQ-NCLQ] | ✅ 3 nguồn — **đóng điểm mở của DD 28/10** |
| DT TC mẹ, cổ tức nhận | [RIENG TM23] 107,93; cổ tức 13,32; lãi gửi 86,52 | ✅ mới đọc |
| BQ 2026Q3 | `ticker_financial` nay **đã có 2026Q3**: DT 517,06, NP 60,77 (BCTC LNST 61,04 gồm NCI) | ✅ khớp (lệch 0,27 = phần NCI, suy luận) |
| Giá | [DNSE] đóng cửa 30/10 = 27.000; tham chiếu 02/11 = 27,0; trần 28,85 / sàn 25,15 | ✅ |

## 2. Doanh nghiệp và ngành (tóm tắt, chi tiết ngành ở file đọc ngành)
- **Hoạt động**: tư vấn khảo sát–thiết kế–QLDA điện (truyền thống, nguồn + lưới), **tổng thầu EPC** (mảng tăng trưởng 2025–28), **O&M** qua công ty con PESE (48 nhà máy; Lào), đầu tư điện tái tạo (7 dự án, 58,7 MW thuần; liên kết CMC 25%, Sơn Mỹ 25%, Thác Bà 2 45%) [EVN 31/01/2026; BCQT6T]. 1.432 lao động [Q3 tr.9].
- **Backlog (định tính, không có giá trị HĐ công bố)**: 4 EPC — Ô Môn IV (PVN, liên danh Doosan–PECC2, COD 12/2028), eREX Yên Bái 1 (ký 07/11/2025, COD đầu 2028) + Tuyên Quang, Tân Thuận GĐ3 (COD Q4/2026). Tiền ứng phản ánh quy mô: eREX 1.843,5 + PVN 467,1 tỷ [Q3 tr.31]. Pipeline tư vấn: liên danh gói 5 Krông Buk–Tây Ninh 1 (158,84 tỷ cả liên danh 3 PECC), FS Bản Chát, BOP khí, tư vấn hạt nhân NT1/NT2 (MoU, chưa HĐ) [đọc ngành §3; BB26].
- **Ngành (đọc độc lập)**: `STRUCTURAL_UPCYCLE` về nhu cầu tư vấn (thiếu điện 4,3 GW 2027 → 14 GW 2030; 45% công suất PDP8 chưa có chủ trương = còn ở pha tư vấn), nhưng **ADMIN_GATED** về nhịp (capex EVN 2026 đi ngang ~123k tỷ; 500kV khởi công 2/28 KH 9T). Rủi ro: phần "upcycle" lớn nhất (LNG/ĐGNK/hạt nhân) có thể vào tay tư vấn/EPC ngoại. Với TV2, động lực 2026–28 **không phải lưới EVN** mà là EPC nguồn (khí PVN, sinh khối Nhật, gió CMC) — nằm ngoài trần tài chính EVN, đây là điểm tích cực ít được nhắc.

## 3. Chất lượng lợi nhuận [Q3 tr.6, 37-39; RIENG TM21-23; out.txt DD 28/10]
| Tỷ đồng | Q3/26 | Q3/25 | 9T/26 | 9T/25 |
|---|---|---|---|---|
| DT thuần | 517,1 | 253,8 | 1.199,2 | 769,5 |
| Biên gộp HN | 17,5% | 16,0% | 15,7% | 15,5% |
| EBIT lõi | 47,5 | 5,9 | 76,3 | 23,2 |
| TC ròng | 27,3 | 3,4 | 85,6 | 5,7 |
| Lãi liên kết | 0,7 | 4,5 | 31,3 | 23,9 |
| LNTT | 76,4 | 14,8 | 195,4 | 52,3 |
| Tỷ trọng lõi/TC/LK | 62/36/1% | | **39/44/16%** | 44/11/46% |

- **Kế hoạch so thực tế (đính chính TB-2):** câu "LNST/DT ~4%" là ý kiến **cổ đông** tại ĐHĐCĐ về **kế hoạch** HN (DT 2.500, LN ~100) [BB26 ý kiến 4], không phải ban lãnh đạo tự nhận. Thực tế 9T: biên LNST 13,6%, EBIT lõi/DT 6,4%; LNST 9T đạt **163% kế hoạch HN cả năm** ⇒ kế hoạch thận trọng.
- **Tích cực (thật):** EBIT lõi Q3 47,5 tỷ gấp ~8 lần Q3/25 (5,9); biên gộp HN **giữ được 15–17%** dù DT gấp đôi (không phải "tăng DT bằng bán lỗ"); Q3 phần lõi đã chiếm 62% LNTT, tức xu hướng chuyển dần từ lãi tiền gửi sang lõi. Lãi tiền gửi phần lớn là **tiền thật** (LCTT dòng 27 "tiền thu lãi cho vay, cổ tức và LN được chia" 109,2 tỷ 9T, gồm ~5 tỷ cổ tức). Chi phí phải trả 248,2 tỷ là trích trước chi phí công trình — chiều thận trọng [Q3 tr.33].
- **Tiêu cực (thật):** 9T 44% LNTT là TC; ở mẹ TC ròng ~110,8 tỷ, **80% là lãi tiền gửi**, cổ tức nhận chỉ 13,3 [RIENG TM23]. Biên gộp **mẹ** 9,7% (thấp hơn HN 15,7% ⇒ con O&M/khảo sát biên cao hơn; EPC ở mẹ biên thấp). Lãi tiền gửi sẽ co khi tiền ứng được giải ngân cho thiết bị (Isgec, Triveni, Toshiba… đã ứng 293 tỷ [Q3 tr.26]).
- **CMC chiếm phần lớn tăng trưởng DT**: 9T 478,7 tỷ gộp, ròng sau loại trừ HN 420,6 (−58,1 chỉ có ở HN) ⇒ ~35% DT 9T [Q3 tr.43]. Doanh thu ghi theo khối lượng **khách xác nhận** (VAS 15) [Q3 tr.15] — khách là liên kết của chính TV2.
- **2026E (ước lượng)**: 9T LNST mẹ 162,2 + Q4 55–80 ⇒ **217–242 tỷ**, EPS 3.200–3.600 đ; P/E @27.000 7,5–8,4x. Q4 mùa vụ (2025: 52% LN năm) và ban lãnh đạo nói nghiệm thu EPC dồn Q3–Q4 [BB26].
- **Base rate 2 chiều** [BQ, `hist_out.txt`]: EPS (số cp hiện tại) 2017–21: 3.180–4.030 đ; 2022–25: 790–1.400 đ. LN 2026 đang **ở đỉnh chu kỳ trước**, không vượt.

## 4. Ghi nhận doanh thu và tiền ứng
- Tiền người mua trả trước 2.418,6 (đầu năm 984+2,2): eREX Yên Bái 929,4 + Tuyên Quang 914,1 + PVN 467,1 + khác 105,8 [Q3 tr.31]. Tỷ lệ ứng/giá trị HĐ: không tính được (giá trị HĐ không công bố) — DD 28/10 ước 37–46% là **ước lượng không nguồn, bỏ**.
- Ý nghĩa 2 chiều: (+) tiền ứng = bằng chứng HĐ có thật và khách có vốn (eREX: ADB/JCM; PVN); (−) đây là nghĩa vụ giao hàng, TV2 gánh rủi ro giá cố định EPC (thiết bị nhập Ấn Độ/Nhật/TQ; thầu phụ thiết kế TQ 87 tỷ [Q3 tr.31]).

## 5. Bảng cân đối, net cash, dòng tiền
- **Không vay đáng kể**: vay NH 152,8 tỷ (ở công ty con, thế chấp 200 tỷ tài sản) [Q3 tr.4; H1 TM43]; tiền + HTM 2.104,2 [Q3 tr.3]; TTS 4.822,9; NPT 3.488 [Q3 tr.3-5].
- **Net cash — trình bày dải, không một điểm** (ước lượng): thô 1.951 tỷ; trừ float ròng (ứng 2.418,6 − trả trước NCC 293,0 − dở dang 119,5 = 2.006,2) ⇒ **≈ −55 tỷ** nếu coi toàn bộ float là nợ; nếu tính phần lãi gộp EPC sẽ hưởng trên khối lượng còn lại (chưa đo được do thiếu giá trị HĐ) thì cao hơn, có thể +100–300 tỷ (ước lượng thô, chưa có cơ sở số). Cách đọc trung lập: **TV2 không có rủi ro thanh khoản 12 tháng, nhưng cũng không có "tiền dư của cổ đông" đáng kể để cộng vào định giá.** Định giá ở §8 dùng P/E trên LN đã gồm lãi tiền gửi ⇒ KHÔNG cộng thêm tiền.
- **CFO**: 9T **+858,6** nhưng nhờ tăng tiền ứng. Trình bày dải (ước lượng): trừ **gộp** tăng tiền ứng +1.432,4 ⇒ **−573,8**; trừ tăng **float ròng** (định nghĩa nhất quán với net cash ở trên: ứng − trả trước NCC − dở dang) +1.083,4 (người phản biện tính; số đầu kỳ chưa tự đọc lại) ⇒ **−224,8**. Nguyên nhân chính là phải thu CMC +458 (theo TM32: 208,1 → 666,4); bỏ CMC thì ~+230. Theo quý (báo cáo): **Q2 −62,7, Q3 −125,3** [Q3 tr.7; H1 tr.10; DD 28/10 §13]. Đây là đặc điểm pha đầu EPC (mua sắm, ứng NCC) cộng CMC không trả; cần quan sát Q4 khi nghiệm thu dồn.
- **Cổ tức**: 1.000 đ/cp/năm (3,7% @27.000); FY2025 67,53 tỷ chưa chi tại 30/9, ngày GDKHQ chưa công bố (tiền lệ FY2024: chốt 12/2025); nguồn gồm 49,9 tỷ LN năm trước ⇒ cổ tức 2025 vượt LN mẹ để lại [NQ26 Điều 5]. FY2026 ≥10%.

## 6. Phải thu và CMC [Q3 tr.25, 43; BCQT6T; BB26]
- Phải thu KH 1.386,2 (đầu năm 919,9); bên liên quan 992,4. **CMC**: TM32 208,1 → 367,1 (30/6) → **666,4** (30/9); TM3 236,8 → **657,3**. Q3 tăng 299,2 tỷ (theo TM32) > DT Q3 từ CMC (+VAT) ⇒ thu tiền Q3 từ CMC ≈ 0 (ước lượng). Lãi trả chậm tính trên CMC 9T 5,50 tỷ [Q3 tr.43] (dồn tích).
- **Cờ dữ liệu chưa giải**: TM3 và TM32 lệch **cả cuối kỳ (+9,05 TM32) lẫn đầu năm (+28,7 TM3)**; DT CMC 6T BCTC H1 244,4 vs BCQT 220,8 chưa VAT. Hậu Giang: cờ "đảo DT" của DD 28/10 **đã giải** — BCQT 6T ghi 1,335 tỷ = BCTC 9T, số H1 14,06 mới là số lệch [GAPS (h)].
- **Phía tích cực có chứng cứ**: CMC tái cơ cấu nợ 2025 và "bắt đầu có lãi"; GĐ3 dùng chung hạ tầng GĐ1-2 (75 MW, vận hành 2022); COD GĐ3 mục tiêu Q4/2026 [BB26; baophapluat 21/06/2026]. Sau COD + PPA, CMC có dòng tiền bán điện để trả. **Phía tiêu cực**: dự án GĐ1-2 vay USD lỗ luỹ kế (phần TV2 −40,2 tỷ [Q3 tr.23]); chưa có BCTC CMC; nhà thầu cũng là cổ đông 25% ⇒ động cơ giãn nợ.
- Khác: nợ quá hạn 120,4 tỷ, dự phòng 71,0 (+20 YTD); quá hạn >3 năm 37,2; Vĩnh Tân 54,05 tỷ không đổi; Hậu Giang 63,6–73,6 không giảm [Q3 tr.25, 27].

## 7. Cổ đông, quản trị, pháp lý — ⚠️ WARNING (mức trung bình-cao; không chặn phân tích)
- **Cổ đông**: EVN **51,33%** (duy nhất ≥5%); 4.341 cổ đông khác; khối ngoại cuối 2025 **7,28%** [BCTN25 tr.38].
- ⚠️ **Room ngoại 0% từ 14/09/2026** [FOL]: hiệu lực thực tế = khối ngoại không mua thêm được; công ty dự định sửa ngành nghề ở ĐHĐCĐ gần nhất để nâng room. Hệ quả cho cổ phiếu: thu hẹp tập người mua tiềm năng (tác động định giá không đo được).
- ⚠️ **Vụ án EVNNPT/PC1** (500kV mạch 3): cựu Chủ tịch Nguyễn Chơn Hùng + KTT Bùi Thị Ngọc Lý bị khởi tố tội **tham ô tài sản (Đ.353 BLHS)**, VKSND tối cao phê chuẩn (05/2026); vụ án 48 bị can, nhóm tội có **vi phạm quy định kế toán**; TV1/TV3 cùng bị nêu; chưa kết luận điều tra; **pháp nhân TV2 chưa bị khởi tố**; không có tin mới sau 28/10 trong phạm vi tra [GAPS (d)]. Họp báo Bộ Công an **02/07/2026** nêu **13 pháp nhân** vi phạm, gồm "các công ty tư vấn xây dựng điện" — **không nêu tên; chưa xác định TV2 có trong danh sách** (nguoiquansat 02/07/2026; DD 28/10 §13.9). Bài báo không nêu tài sản bị tham ô của ai — nếu là tài sản của TV2 thì đó là rủi ro kiểm soát nội bộ kế toán (chưa xác định).
- ⚠️ Kiểm toán đổi EY (FY2025, chấp nhận toàn phần) → UHY (soát xét H1 2026: chấp nhận + đoạn nhấn mạnh vụ khởi tố) [H1 tr.5-6]; Q3 chưa soát xét; phụ trách kế toán mới từ 17/07/2026. **Tích cực:** HĐ kiểm toán + soát xét BCTC 2026 với UHY đã ký **15/07/2026** [CBTT 2604/PECC2-TC&PC, `src/gaps/pdf/05_…`] ⇒ loại rủi ro đuôi "không thuê được kiểm toán" kiểu TV1.
- HĐQT mới 4 thành viên, Chủ tịch Phạm Liên Hải (từ 30/06/2026) [NQ26 Điều 15]. NQ HĐQT 29/10/2026 phê duyệt khung giao dịch bên liên quan; **HĐ tổng thầu với bên liên quan được HĐQT/TGĐ tự duyệt** (loại khỏi ngưỡng 35% phải trình ĐHĐCĐ) [NQ-NCLQ]. Tính phù hợp với Đ.167 Luật Doanh nghiệp 2020 **chưa được thẩm định pháp lý** (bỏ chữ "đúng luật" của v2); là điểm cần theo dõi khi giao dịch CMC lớn.
- ĐHĐCĐ 2026: 48,26 triệu cp biểu quyết = **71,5% vốn** [NQ26 Điều 17]; trừ EVN 34,66 triệu, cổ đông ngoài EVN dự **13,6 / 32,87 triệu cp ≈ 41%** (ước tính từ 67,53 triệu cp).
- Giả thuyết (không khẳng định liên hệ): NQ26 Điều 11 (30/06) bổ sung ngành nghề; 08/09 nộp hồ sơ room, CV UBCK đưa room về 0% viện dẫn NĐ 245/2025 [FOL].

## 8. Định giá — `calc/valuation_out.txt`
### 8a. Bội số và các neo (trình bày CẢ neo thấp lẫn neo lịch sử)
| Neo | Giá trị | Áp lên LNST cơ sở 178 tỷ ⇒ đ/cp |
|---|---|---|
| TV1 P/E hiện tại 3,6 (UPCOM, có thuỷ điện, cùng vụ án, ADV 0,8 tỷ) | thấp | 9.500 |
| TV4 5,5 / TV3 7,2 (HNX, ADV 0,04–0,05 tỷ — gần như không giao dịch) | thấp | 14.500 / 19.000 |
| P/E hợp lý từ Ke (khung domestic_v2 Ke 12,5–13,5%; ROE 11–12,7%, payout 40%) — giả định g 6,6–7,6% vĩnh viễn, **không hợp base rate LN sập ~70%** khi hết HĐ | 6,2–8,8x | 16.300–23.200 |
| Trung vị P/E lịch sử nhóm PECC (BQ, tháng, 2014+; TV1 lọc pe<100 = 8,6, không lọc 9,35): TV3 9,5 / TV4 8,9 — gộp mọi pha | 8,6–9,5x | 22.700–25.000 |
| **P/E TV2 pha LN ĐỈNH 2017–21** (LNST 214–272): trung vị **7,45** (IQR 6,1–8,9, n=60); 2019–21: 7,95 | 7–9x | 18.500–23.700 |
| P/E TV2 pha LN ĐÁY 2022–25: trung vị ~33 — **không dùng** (P/E trên LN đáy, thị trường định theo sổ sách) | — | — |
| Trung vị gộp 2014+ 8,75 / 2019+ 11,0 — lẫn pha, chỉ tham khảo | — | — |
| P/B: hiện 1,37 vs trung vị TV2 1,81 (2014+) / 1,77 (2019+); P/B hợp lý ROE 12,7%, Ke 12,5–13,5% = 0,93–1,12 | | 18.300–22.100 (trên BVPS 19.708) |

Đọc trung lập: comp hiện tại đều **thấp** nhưng thanh khoản quá mỏng (TV3/TV4) hoặc khác cấu trúc (TV1 có SB5, cùng vụ án). Neo trực tiếp nhất là chính TV2 **khi LN ở đỉnh** (7,45x; IQR 6,1–8,9). Ke-P/E cho 6,2–8,8x — cùng vùng. ⇒ dải P/E cơ sở và tích cực **7–9x**. Câu v2 "dải 7,5–10x bao cả hai neo" là **sai** (không bao comp 3,6/5,5/7,2 lẫn 7,45). Một P/E >9x cần căn cứ khác lịch sử (vd bằng chứng backlog kéo LN ~230 tỷ+ sau 2028); hiện chưa có.

### 8b. Chi phí vốn
Khung domestic_v2: **Ke 12,5–13,5%** (thống nhất với khung; v2 ghi 12,3–13,4% là lệch). Không làm DCF vô hạn: dòng tiền EPC theo dự án, lệch pha, không có giá trị HĐ ⇒ DCF sẽ là giả định chồng giả định. Dùng P/E hợp lý từ Ke + ROE làm phép thử: ROE 11% ⇒ 6,2–7,2x; 12,7% ⇒ 7,3–8,8x.

### 8c. Độ nhạy giá trị/cp (nghìn đồng) — LNST bền vững × P/E
| LNST \ P/E | 6 | 7 | 7,45 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|
| 100 | 8,9 | 10,4 | 11,0 | 11,8 | 13,3 | 14,8 |
| 130 | 11,6 | 13,5 | 14,3 | 15,4 | 17,3 | 19,3 |
| 160 | 14,2 | 16,6 | 17,7 | 19,0 | 21,3 | 23,7 |
| 178 | 15,8 | 18,5 | 19,6 | 21,1 | 23,7 | 26,4 |
| 190 | 16,9 | 19,7 | 21,0 | 22,5 | 25,3 | 28,1 |
| 220 | 19,5 | 22,8 | 24,3 | 26,1 | 29,3 | 32,6 |
| 250 | 22,2 | 25,9 | **27,6** | 29,6 | 33,3 | 37,0 |

Giá 27.000 ≈ (LNST 245, P/E 7,45) hoặc (203, 9x). Phơi nhiễm CMC: tổn thất 15/30/50% (sau thuế 20%) ⇒ −1.500 / −3.000 / −5.100 đ/cp (ước lượng).

### 8d. Vùng, kỳ vọng, độ nhạy — `calc/valuation_out.txt`
| Biến thể | Giá trị kỳ vọng | Giá 27.000 so kỳ vọng |
|---|---|---|
| **v3: 25/50/25, P/E 7–9** | **20.700** | **+31%** |
| Trọng số 30/50/20 (DD 28/10) | 19.700 | +37% |
| Trọng số 20/50/30 | 21.600 | +25% |
| P/E 6,5–8,5 | 19.600 | +38% |
| P/E 7,5–10 (dải v2) | 22.400 | +21% |
| P/E 9–11 (trung vị lẫn pha, chỉ tham khảo) | 25.200 | +7% |
| Tiêu cực định theo P/B sàn 0,8–1,0 | 22.100 | +22% |

Vùng cơ sở 17.100–25.300 (góc-tới-góc, khai rõ ở §0); tâm 21.000.

## 9. Thanh khoản [DNSE]
ADV20 trung bình **5,66 tỷ/ngày** (213k cp), **trung vị 3,05 tỷ** (119k cp) — trung bình bị kéo bởi phiên 28/10 (1,01 triệu cp); cao nhất nhóm (TV1 0,82; TV3 0,04; TV4 0,05). YTD −21,6% (34.450 → 27.000); vùng 12 tháng 23.000–44.200. Phiên 28/10 (ngày ký BCTC Q3): +6,9%, KL 1,01 triệu cp — quan sát.

## 10. Mốc kiểm chứng (hai chiều, lập 01/11/2026; P = ước lượng)
| # | Mốc | Ngày | Chiều tích cực | Chiều tiêu cực | P(tích cực) |
|---|---|---|---|---|---|
| M1 | COD Tân Thuận GĐ3 | ≤31/12/2026 | COD + PPA | Trượt sang 2027 | 0,55 |
| M2 | Phải thu CMC trên BCTC Q4/2026 hoặc kiểm toán 2026 | ~01–03/2027 | ≤470 tỷ (−30%) | >700 tỷ hoặc có trích lập | 0,35 |
| M3 | LNST HN 2026 (BCTC Q4) | ~30/01/2027 | ≥230 tỷ | <200 tỷ | 0,50 |
| M4 | CFO 2026 trừ biến động **float ròng** (ứng − trả trước NCC − dở dang) | kiểm toán 2026 | ≥0 | < −300 tỷ | 0,30 |
| M5 | Ý kiến kiểm toán FY2026 | ~03/2027 | Chấp nhận toàn phần | Ngoại trừ/từ chối | 0,70 |
| M6 | Vụ án EVNNPT/PC1 | — | Kết luận điều tra không nêu pháp nhân TV2 | Khởi tố pháp nhân/cấm thầu | 0,75 |
| M7 | HĐ EPC/tư vấn mới ký có giá trị công bố | ≤30/06/2027 | ≥1 HĐ | Không có | 0,45 |
| M8 | ĐHĐCĐ 2027 sửa ngành nghề, room ngoại >0% | ~06/2027 | Có | Không | 0,60 |
| M9 | Đọc ngành F1 (capex EVN 2026 ≥123k tỷ) | 31/01/2027 | YES | NO | 0,55 (của người đọc ngành) |

## 11. Lệch nguồn BQ ↔ BCTC
- BQ `ticker_financial` nay có 2026Q3 (NP 60,77 = phần mẹ; BCTC 61,04 gồm NCI). `Cash_P0` BQ 2026Q3 1.059,7 = chỉ tiền + tương đương; **thiếu HTM 1.044,5** ⇒ không dùng BQ cho net cash.
- `ticker.PE` BQ 30/10 = 8,64 (TTM BQ) vs tính tay 2026E 7,5–8,4 (forward, ước lượng) — khác cơ sở, không mâu thuẫn.
- Lịch sử 2014–2016 BQ có OShares 4,4 triệu (trước nhiều đợt tăng vốn) ⇒ chỉ dùng LNST tuyệt đối, EPS quy về số cp hiện tại.

## Giới hạn
1. Không có giá trị HĐ EPC, backlog theo giá trị, cơ cấu DT theo mảng (công ty không công bố) ⇒ kịch bản dựa trên LN, không dựng được từ DT×biên theo dự án.
2. BCTC Q3 chưa soát xét; hai thuyết minh lệch nhau về phải thu CMC; không có BCTC CMC.
3. Tỷ trọng EVN ~8% DT 9T là cộng tay từ ảnh (DD 28/10), có thể sót.
4. Trọng số 25/50/25 và dải P/E là phán đoán (độ nhạy §8d); neo P/E pha đỉnh dựa vào **một** chu kỳ 2017–21 (N=1); P/E BQ là TTM có độ trễ công bố.
5. "O&M ~700 tỷ 2025" và mục tiêu 3.000–5.000 tỷ là lời ban lãnh đạo tại ĐHĐCĐ, chưa đối chiếu BCTC.
6. Ngày GDKHQ cổ tức FY2025 và lý do room ngoại 0% chưa công bố.

## Thay đổi so với DD 28/10
| # | DD 28/10 | v2 | Lý do |
|---|---|---|---|
| 1 | Khung nhãn nội bộ, giá trị kỳ vọng ~22.900 (base 9x) / ~20.400 (base 7x) | Vùng hợp lý 18.300–28.100, kỳ vọng ~22.600; giá **trong vùng, nửa trên** | Luật 12: trung lập, dải P/E 7,5–10 bao cả comp thấp và lịch sử |
| 2 | Bear 30 / Base 50 / Bull 20 | 25 / 50 / 25 | Không có căn cứ đo được để nghiêng |
| 3 | "Dòng DT CMC có thể gần hết sau Q4/2026"; CMC = Tân Thuận GĐ3 là suy luận | CMC = Tân Thuận GĐ3 **xác nhận**; backlog **4 HĐ** đến 2028 (Ô Môn IV, 2 eREX, GĐ3) | EVN 31/01/2026, RIENG TM19, BB26 |
| 4 | PVN 467 tỷ "chưa xác định dự án" | Gần như chắc Ô Môn IV (suy luận có căn cứ) | theinvestor 06/2025 |
| 5 | EVN 51% chưa đối chiếu | 51,33% xác nhận 3 nguồn | RIENG TM20.1, BCTN25 |
| 6 | Room ngoại 14/09 chưa đọc | **0%**, khối ngoại 7,28% chỉ còn chiều bán | FOL |
| 7 | KH 2026 LNST 100 (không rõ HN/mẹ) | Mẹ: DT 2.080 / LNST 83,2; HN ~2.500 / ~100 (nói miệng) | NQ26, BB26 |
| 8 | TC mẹ "có thể gồm cổ tức con" | Cổ tức 13,3 / TC 110,8; 80% là lãi tiền gửi | RIENG TM23 |
| 9 | Cờ Hậu Giang "nghi đảo" | Đã giải: số H1 14,06 là số lệch | BCQT6T |
| 10 | Tỷ lệ ứng 37–46% (ước lượng không nguồn) | Bỏ | Không có giá trị HĐ |
| 11 | Thiếu base rate tích cực | Thêm 2017–21 LNST 214–272 tỷ (BQ) cạnh cú sập 2022 | Cân bằng chứng cứ |
| 12 | Pháp lý: "khởi tố" | Tội danh tham ô (Đ.353), vụ án 48 bị can, có nhóm tội kế toán | nhandan, Bộ Công an 01/10 |

## Nguồn
Xem `GAPS.md` § Nguồn web và `../dd_TV2_20261028/REPORT.md` §12. Thêm: DNSE API (secdef/latest_trade/ohlc, read-only, `calc/dnse_raw.json`, `calc/dnse_fetch_time.txt`); BQ `tav2_bq.ticker_financial` (TV2 2014Q1–2026Q3) và `tav2_bq.ticker` (PE/PB tháng TV1–4 2014–10/2026) → `calc/bq_tv2_fin.csv`, `calc/bq_pe_pb_monthly.csv`.

## Phụ lục: đính chính của người phản biện (01/11/2026, `SKEPTIC_20261101.md`, VERDICT REFUTED high) — đã áp
| Mục | v2 | v3 |
|---|---|---|
| CAO-1 Neo P/E | Trung vị 2019+ 11,0 / 2014+ 8,7; dải 7,5–10x "bao cả hai neo" | Tách pha: đỉnh 2017–21 **7,45** (dùng), đáy 2022–25 ~33 (không dùng); dải 7–9x; script `calc/pe_by_phase.py` |
| CAO-1 Kịch bản | Cơ sở 18.300–28.100, tích cực tâm 33.300, kỳ vọng 22.600 | Cơ sở 17.100–25.300, tích cực tâm 29.600, kỳ vọng **20.700** |
| CAO-2 Câu dẫn | "TRONG vùng, nửa trên" (vùng góc-tới-góc không khai) | Dẫn bằng khoảng cách tới kỳ vọng (+31%); khai cách dựng vùng; "trong vùng" chỉ khi LN ≥203 và 9x đồng thời |
| TB-1 CFO | −573 (gộp) | Dải −574 (gộp) … −225 (float ròng); CMC +458 là nguyên nhân chính; M4 định nghĩa lại |
| TB-2 "LNST/DT ~4%" | Gán ban lãnh đạo | Là cổ đông nói về kế hoạch; thực tế 13,6%, đạt 163% KH |
| TB-3 Bộ Công an 02/07 | Rơi mất | Thêm lại (13 pháp nhân, "tư vấn xây dựng điện", chưa xác định TV2) |
| TB-4 "Đúng luật" | Khẳng định | Bỏ; chưa thẩm định Đ.167 LDN |
| TB-5 UHY FY2026 | Bỏ sót | Thêm như điểm tích cực |
| TB-6 Trọng số | 25/50/25 không căn cứ mới | Giữ 25/50/25, nói rõ không phải dữ liệu mới, độ nhạy 30/50/20 ⇒ 19.700 |
| THẤP | +15% "so tâm"; nhãn 109,2; "chỉ" 71,5%; script hist; Ke 12,3–13,4; Đ.11/NĐ245; ADV | Sửa toàn bộ: bỏ câu so mốc 26.050; nhãn LCTT dòng 27; cổ đông ngoài EVN ~41%; script lưu; Ke 12,5–13,5; nêu như giả thuyết; ADV kèm trung vị 3,05 tỷ |

Bổ sung cân bằng ngoài yêu cầu: tâm tiêu cực ứng P/B 0,56 (thấp hơn mọi tháng từ 2014); biến thể P/B sàn cho kỳ vọng 22.100 — đã ghi §0/§8d.
