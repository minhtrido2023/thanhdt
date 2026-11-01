# DD — TV2 (CTCP Tư vấn Xây dựng Điện 2 / PECC2, HOSE) · **v2 khách quan** · as-of 01/11/2026 · job `Taylor_20261101_040936`

> NGHIÊN CỨU READ-ONLY (bước 1/3: sau đây là phản biện số liệu/nguồn, rồi báo cáo nhà đầu tư). Không khuyến nghị, không lệnh, không wire.
> Khung: skill `dd-investor-report` luật 12 — tích cực và tiêu cực cùng chuẩn chứng cứ; **không** dùng nhãn nội bộ; kết luận = vị trí giá so với vùng giá trị hợp lý + 3 kịch bản có xác suất.
> **Nguồn:** [Q3 tr.X] BCTC hợp nhất Q3/2026 (chưa soát xét, ký 28/10/2026) · [H1 tr.X] BCTC HN bán niên 2026 soát xét UHY · [RIENG TMx] BCTC riêng Q3/2026 · [GT] giải trình 4270/PECC2-TCKT · [BCTN25], [NQ26], [BB26], [BCQT6T], [FOL], [NQ-NCLQ]: xem `GAPS.md` · [BQ] `tav2_bq` (lịch sử; KHÔNG dùng cho giá hôm nay) · [DNSE] `calc/dnse_raw.json` (secdef/latest_trade/ohlc, lấy 01/11/2026 11:1x ICT).
> Phép tính: `calc/valuation.py` → `calc/valuation_out.txt`; lịch sử `calc/hist_out.txt`; giá `calc/dnse_px_out.txt`; DD 28/10 `../dd_TV2_20261028/calc.py` → `out.txt`. Số tự đặt gắn **(ước lượng)**.
> Ngành: đọc độc lập `kb/data_registry/market-state/sector_read_power_consulting_20261028.md` (đọc mù, không biết mã/giá).

## 0. Kết luận

**Giá 27.000 đ (đóng cửa 30/10/2026, HOSE [DNSE secdef `marketId=STO`, latest_trade 14:45:07]) nằm TRONG vùng giá trị hợp lý 18.300–28.100 đ, ở nửa trên (≈88% bề rộng vùng), cao hơn tâm ~23.000 khoảng 17%.** Giá trị kỳ vọng có trọng số **~22.600** (dải 18.300–27.300) (ước lượng). Ở mốc 26.050 (27/10) kết luận không đổi (vẫn trong vùng, +15% so tâm).

**Thị trường đang định giá gì:** ở 27.000 (vốn hoá 1.823 tỷ), P/E 9x ngầm định LNST bền vững **~203 tỷ/năm**, 8x ⇒ ~228 tỷ — tức là coi mức LN 2026 (ước ~217–242 tỷ, gồm lãi trên tiền ứng) là **gần bền vững cho 2027–28**. Đó là kịch bản "4 hợp đồng EPC chạy đúng tiến độ và CMC trả được tiền", nghiêng lên hơn là cơ sở trung tính.

| | Tích cực (có chứng cứ) | Tiêu cực (có chứng cứ) |
|---|---|---|
| Tăng trưởng | Backlog **4 HĐ EPC** đã ký: Ô Môn IV (PVN 1.155 MW, cùng Doosan, COD 12/2028), eREX Yên Bái 1 + Tuyên Quang (50 MW mỗi nhà máy), Tân Thuận GĐ3 (25 MW); DT phân bổ chủ yếu 2026–28 [BB26] | EPC biên mỏng: biên gộp mẹ 9T **9,7%** [RIENG TM21-22]; ban lãnh đạo tự nhận LNST/DT ~4% [BB26] |
| Tiền | Tiền + HTM **2.104 tỷ**, vay chỉ 152,8 [Q3 tr.3-4]; lãi tiền gửi thu bằng tiền 109,2 [Q3 tr.7] | Gần như toàn bộ tiền là **tiền ứng của khách** (2.418,6) — tiền ròng "của cổ đông" ≈ −55 tỷ nếu coi float là nợ (ước lượng) |
| Lịch sử | Đã có 5 năm LNST **214–272 tỷ** (2017–21) khi chu kỳ EPC lên [BQ] | Sau đó **sập ~70%** (2022: 77 tỷ) khi hết HĐ [BQ] |
| Vị thế | Oligopoly tư vấn điện gốc EVN: gói 500kV 1–2 nhà thầu, giảm giá 1–5% (đọc ngành) ; ~50 kỹ sư hạt nhân [BB26]; O&M 48 nhà máy | Mảng lưới EVN co lại 2026 (khách EVN ~8% DT 9T, ước lượng) ; lưới bị trần tài chính EVN (đọc ngành) |
| Bên liên quan | CMC tái cơ cấu nợ 2025, bắt đầu có lãi; GĐ3 COD Q4/2026 [BB26; QĐ 2230 Cà Mau] | Phải thu CMC **657–666 tỷ** + đầu tư 188,6 = **~64% VCSH mẹ**, không dự phòng, gần như chưa thu tiền Q3 |
| Quản trị | Cổ tức tiền mặt 10%/năm đều; FY2026 ≥10% [NQ26] | ⚠️ cựu Chủ tịch + KTT bị khởi tố **tham ô (Đ.353)**; Q3 chưa soát xét; room ngoại **0%** từ 14/09 |

**3 kịch bản (LNST bình quân 2027–28, ước lượng):**

| Kịch bản | P | Giả định | LNST | P/E | Giá trị/cp |
|---|---|---|---|---|---|
| Tích cực | 25% | Lặp lại chu kỳ 2019–21: HĐ mới (BOP khí/LNG, Philippines, tư vấn hạt nhân), CMC thu đủ | 230–270 | 8–10 | **27.200–40.000** (tâm ~33.300) |
| Cơ sở | 50% | 4 HĐ EPC đúng tiến độ; tư vấn + O&M ổn định; TC ròng giảm còn 50–70 khi giải ngân thiết bị; LK ~30 | 165–190 | 7,5–10 | **18.300–28.100** (tâm ~23.000) |
| Tiêu cực | 25% | Vượt chi phí EPC/trễ tiến độ, lãi float giảm nhanh, CMC trích lập ~100 tỷ trước thuế (−80 sau thuế, một lần) | 100–120 | 7–8 | **9.200–13.000** (tâm ~11.000) |

Trọng số 25/50/25 là đối xứng có chủ đích (không có căn cứ đo được để lệch). Đuôi nặng hơn tiêu cực: mất 50% phơi nhiễm CMC ⇒ −5.100 đ/cp (ước lượng).

**Điều làm nhận định TÍCH CỰC hơn:** (1) Q4/2026 hoặc BCTC kiểm toán 2026 cho thấy **phải thu CMC giảm ≥30%** sau COD Tân Thuận GĐ3; (2) CFO năm 2026 trừ biến động tiền ứng ≥ 0; (3) công bố HĐ EPC/tổng thầu mới có giá trị (gói BOP LNG, Philippines) hoặc tư vấn NT1 có HĐ ký; (4) kiểm toán FY2026 chấp nhận toàn phần, không đoạn ngoại trừ; (5) ĐHĐCĐ 2027 sửa ngành nghề, nâng room ngoại. **Điều làm TIÊU CỰC hơn:** (1) phải thu CMC >700 tỷ hoặc trích lập; (2) Tân Thuận GĐ3 trượt COD sang 2027; (3) pháp nhân TV2 bị khởi tố/cấm thầu, hoặc kết luận điều tra quy trách nhiệm kế toán tại TV2; (4) biên gộp Q4 <8% hoặc ghi nhận lỗ HĐ (vượt chi phí thiết bị nhập, tỷ giá INR/USD); (5) lãi TC ròng giảm >50% YoY mà EBIT lõi không bù.

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

- **Tích cực (thật):** EBIT lõi Q3 47,5 tỷ gấp ~8 lần Q3/25 (5,9); biên gộp HN **giữ được 15–17%** dù DT gấp đôi (không phải "tăng DT bằng bán lỗ"); Q3 phần lõi đã chiếm 62% LNTT, tức xu hướng chuyển dần từ lãi tiền gửi sang lõi. Lãi tiền gửi là **tiền thật** (thu bằng tiền 109,2 tỷ 9T). Chi phí phải trả 248,2 tỷ là trích trước chi phí công trình — chiều thận trọng [Q3 tr.33].
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
- **CFO**: 9T **+858,6** nhưng nhờ tăng tiền ứng +1.432; trừ đi ⇒ **−573** (ước lượng); **Q2 −62,7, Q3 −125,3** [Q3 tr.7; H1 tr.10; DD 28/10 §13]. Đây là đặc điểm pha đầu EPC (mua sắm, ứng NCC) cộng CMC không trả; cần quan sát Q4 khi nghiệm thu dồn.
- **Cổ tức**: 1.000 đ/cp/năm (3,7% @27.000); FY2025 67,53 tỷ chưa chi tại 30/9, ngày GDKHQ chưa công bố (tiền lệ FY2024: chốt 12/2025); nguồn gồm 49,9 tỷ LN năm trước ⇒ cổ tức 2025 vượt LN mẹ để lại [NQ26 Điều 5]. FY2026 ≥10%.

## 6. Phải thu và CMC [Q3 tr.25, 43; BCQT6T; BB26]
- Phải thu KH 1.386,2 (đầu năm 919,9); bên liên quan 992,4. **CMC**: TM32 208,1 → 367,1 (30/6) → **666,4** (30/9); TM3 236,8 → **657,3**. Q3 tăng 299,2 tỷ (theo TM32) > DT Q3 từ CMC (+VAT) ⇒ thu tiền Q3 từ CMC ≈ 0 (ước lượng). Lãi trả chậm tính trên CMC 9T 5,50 tỷ [Q3 tr.43] (dồn tích).
- **Cờ dữ liệu chưa giải**: TM3 và TM32 lệch **cả cuối kỳ (+9,05 TM32) lẫn đầu năm (+28,7 TM3)**; DT CMC 6T BCTC H1 244,4 vs BCQT 220,8 chưa VAT. Hậu Giang: cờ "đảo DT" của DD 28/10 **đã giải** — BCQT 6T ghi 1,335 tỷ = BCTC 9T, số H1 14,06 mới là số lệch [GAPS (h)].
- **Phía tích cực có chứng cứ**: CMC tái cơ cấu nợ 2025 và "bắt đầu có lãi"; GĐ3 dùng chung hạ tầng GĐ1-2 (75 MW, vận hành 2022); COD GĐ3 mục tiêu Q4/2026 [BB26; baophapluat 21/06/2026]. Sau COD + PPA, CMC có dòng tiền bán điện để trả. **Phía tiêu cực**: dự án GĐ1-2 vay USD lỗ luỹ kế (phần TV2 −40,2 tỷ [Q3 tr.23]); chưa có BCTC CMC; nhà thầu cũng là cổ đông 25% ⇒ động cơ giãn nợ.
- Khác: nợ quá hạn 120,4 tỷ, dự phòng 71,0 (+20 YTD); quá hạn >3 năm 37,2; Vĩnh Tân 54,05 tỷ không đổi; Hậu Giang 63,6–73,6 không giảm [Q3 tr.25, 27].

## 7. Cổ đông, quản trị, pháp lý — ⚠️ WARNING (mức trung bình-cao; không chặn phân tích)
- **Cổ đông**: EVN **51,33%** (duy nhất ≥5%); 4.341 cổ đông khác; khối ngoại cuối 2025 **7,28%** [BCTN25 tr.38].
- ⚠️ **Room ngoại 0% từ 14/09/2026** [FOL]: hiệu lực thực tế = khối ngoại không mua thêm được; công ty dự định sửa ngành nghề ở ĐHĐCĐ gần nhất để nâng room. Hệ quả cho cổ phiếu: thu hẹp tập người mua tiềm năng (tác động định giá không đo được).
- ⚠️ **Vụ án EVNNPT/PC1** (500kV mạch 3): cựu Chủ tịch Nguyễn Chơn Hùng + KTT Bùi Thị Ngọc Lý bị khởi tố tội **tham ô tài sản (Đ.353 BLHS)**, VKSND tối cao phê chuẩn (05/2026); vụ án 48 bị can, nhóm tội có **vi phạm quy định kế toán**; TV1/TV3 cùng bị nêu; chưa kết luận điều tra; **pháp nhân TV2 chưa bị khởi tố**; không có tin mới sau 28/10 trong phạm vi tra [GAPS (d)]. Bài báo không nêu tài sản bị tham ô của ai — nếu là tài sản của TV2 thì đó là rủi ro kiểm soát nội bộ kế toán (chưa xác định).
- ⚠️ Kiểm toán đổi EY (FY2025, chấp nhận toàn phần) → UHY (soát xét H1 2026: chấp nhận + đoạn nhấn mạnh vụ khởi tố) [H1 tr.5-6]; Q3 chưa soát xét; phụ trách kế toán mới từ 17/07/2026.
- HĐQT mới 4 thành viên, Chủ tịch Phạm Liên Hải (từ 30/06/2026) [NQ26 Điều 15]. NQ HĐQT 29/10/2026 phê duyệt khung giao dịch bên liên quan; **HĐ tổng thầu với bên liên quan được HĐQT/TGĐ tự duyệt** (loại khỏi ngưỡng 35% phải trình ĐHĐCĐ) [NQ-NCLQ]. Đúng luật, nhưng là điểm cần theo dõi khi giao dịch CMC lớn.
- ĐHĐCĐ 2026: chỉ 48,26 triệu cp biểu quyết = **71,5% vốn** (EVN 34,66 triệu là phần lớn) [NQ26 Điều 17; ước tính tỷ lệ từ 67,53 triệu cp].

## 8. Định giá — `calc/valuation_out.txt`
### 8a. Bội số và các neo (trình bày CẢ neo thấp lẫn neo lịch sử)
| Neo | Giá trị | Áp lên LNST cơ sở 178 tỷ ⇒ đ/cp |
|---|---|---|
| TV1 P/E hiện tại 3,6 (UPCOM, có thuỷ điện, cùng vụ án, ADV 0,8 tỷ) | thấp | 9.500 |
| TV4 5,5 / TV3 7,2 (HNX, ADV 0,04–0,05 tỷ — gần như không giao dịch) | thấp | 14.500 / 19.000 |
| P/E hợp lý từ Ke (Ke nội địa 12,3–13,4%, ROE bền 12,7%, payout 40%) | 7,4–9,2x | 19.500–24.200 |
| Trung vị P/E lịch sử nhóm PECC (BQ, tháng, 2014+): TV1 8,6 / TV3 9,5 / TV4 8,9 | 8,6–9,5x | 22.700–25.000 |
| Trung vị P/E lịch sử TV2: 2014+ **8,7**; 2019+ **11,0** | 8,7–11x | 22.900–29.000 |
| P/B: hiện 1,37 vs trung vị TV2 1,81 (2014+) / 1,77 (2019+); P/B hợp lý ROE 12,7% = 0,95–1,17 | | 18.700–23.100 (trên BVPS 19.708) |

Đọc trung lập: comp hiện tại đều **thấp** nhưng thanh khoản quá mỏng (TV3/TV4) hoặc khác cấu trúc (TV1 có SB5, cùng vụ án) để làm neo chính; bội số lịch sử cao hơn nhưng gồm giai đoạn 2019–21 khi LN đỉnh. Hai neo hợp lý cùng tồn tại ⇒ dải P/E cơ sở **7,5–10x** bao cả hai.

### 8b. Chi phí vốn
Khung skill: rf chuẩn hoá ~6,75%, ERP nội địa 5,0–6,1%, β ~1,1 ⇒ **Ke 12,3–13,4%** (dải rộng 10,5–14,0). Không làm DCF vô hạn: dòng tiền EPC theo dự án, lệch pha, không có giá trị HĐ ⇒ DCF sẽ là giả định chồng giả định. Dùng P/E hợp lý từ Ke + ROE làm phép thử: ROE 11% ⇒ 6,3–7,5x; 12,7% ⇒ 7,4–9,2x; 15% ⇒ 9,9–13,2x.

### 8c. Độ nhạy giá trị/cp (nghìn đồng) — LNST bền vững × P/E
| LNST \ P/E | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|
| 100 | 8,9 | 10,4 | 11,8 | 13,3 | 14,8 | 16,3 |
| 130 | 11,6 | 13,5 | 15,4 | 17,3 | 19,3 | 21,2 |
| 160 | 14,2 | 16,6 | 19,0 | 21,3 | 23,7 | 26,1 |
| 190 | 16,9 | 19,7 | 22,5 | 25,3 | 28,1 | 31,0 |
| 220 | 19,5 | 22,8 | 26,1 | **29,3** | 32,6 | 35,8 |
| 250 | 22,2 | 25,9 | 29,6 | 33,3 | 37,0 | 40,7 |

Giá 27.000 ≈ (LNST 190, P/E ~9,6) hoặc (220, ~8,3). Phơi nhiễm CMC: tổn thất 15/30/50% (sau thuế 20%) ⇒ −1.500 / −3.000 / −5.100 đ/cp (ước lượng).

### 8d. Vùng giá trị và kịch bản — xem §0. Vùng hợp lý = dải kịch bản cơ sở **18.300–28.100**; kỳ vọng có trọng số ~22.600.

## 9. Thanh khoản [DNSE]
ADV20 **5,66 tỷ/ngày** (213k cp) — cao nhất nhóm (TV1 0,82; TV3 0,04; TV4 0,05). YTD −21,6% (34.450 → 27.000); vùng 12 tháng 23.000–44.200. Phiên 28/10 (ngày ký BCTC Q3): +6,9%, KL 1,01 triệu cp — quan sát.

## 10. Mốc kiểm chứng (hai chiều, lập 01/11/2026; P = ước lượng)
| # | Mốc | Ngày | Chiều tích cực | Chiều tiêu cực | P(tích cực) |
|---|---|---|---|---|---|
| M1 | COD Tân Thuận GĐ3 | ≤31/12/2026 | COD + PPA | Trượt sang 2027 | 0,55 |
| M2 | Phải thu CMC trên BCTC Q4/2026 hoặc kiểm toán 2026 | ~01–03/2027 | ≤470 tỷ (−30%) | >700 tỷ hoặc có trích lập | 0,35 |
| M3 | LNST HN 2026 (BCTC Q4) | ~30/01/2027 | ≥230 tỷ | <200 tỷ | 0,50 |
| M4 | CFO 2026 trừ biến động tiền ứng | kiểm toán 2026 | ≥0 | < −300 tỷ | 0,25 |
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
4. Trọng số 25/50/25 và dải P/E là phán đoán; kịch bản tích cực dựa vào base rate 2019–21 (một chu kỳ, N=1).
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
