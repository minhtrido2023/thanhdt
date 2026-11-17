# DD — VCB (Ngân hàng TMCP Ngoại thương Việt Nam) · mùa BCTC Q3/2026 · 2026-11-17 · job `Taylor_20261117_110239`

> NGHIÊN CỨU READ-ONLY, chưa qua fundamental-skeptic. Không phải khuyến nghị mua; user quyết. Không ghi `dd_price_zones.json`,
> không PDF, không email (Mike làm sau skeptic).
> Nguồn: **[BCTC]** = BCTC hợp nhất Q3/2026 + giải trình biến động LNST + Phụ lục II điều chỉnh hồi tố 2025 theo KTNN, CV
> 22146/VCB-CSTCKT ký 30/10/2026 (`src/VCB_BCTC_Q3_2026_HN.pdf`, 66 trang scan, tôi đọc trực tiếp từng trang). Site
> vietcombank.com.vn tải danh mục bằng AJAX (trang BCTC trả 404) ⇒ lấy bản PDF CBTT y nguyên từ `static2.vietstock.vn`
> (trang 1 có chữ ký số VCB 30/10/2026 16:03). `src/VCB_BCTC_2025_KT_HN.pdf` = BCTC kiểm toán 2025 (đã tải; **chưa đọc được** — môi trường không có công cụ đọc PDF, xem §10).
> **[BQ]** = `tav2_bq.ticker_financial` / `tav2_bq.ticker` · **[Bobby]** = `kb/data_registry/market-state/sector_read_ngan_hang_quoc_doanh_20261117.md`
> (đọc mù) · **[Báo]** = báo chí, ghi rõ cạnh số. Mọi phép tính: `calc.py` trên `assumptions_VCB_20261117.json`
> (md5 `55731df5d9c0c9292b5695cc5d6c4cce`). Số tự đặt gắn **(ước lượng)**.

## 0. Kết luận

**Ngân hàng tốt nhất hệ thống về chất lượng tài sản và chi phí vốn. Ở mức r 13,5% của fleet, giá trị cơ sở (tâm ROE 14,6%) là 35.500 đ/cp (có trọng số
39.100; ba mốc ROE 13,2% / 14,6% / 16% ⇒ 29.000 / 35.500 / 42.000), dưới giá 52.100 (17/11/2026).** Toàn bộ chênh lệch nằm ở **chi phí vốn**, không nằm ở lợi nhuận. Giá hiện tại hàm ý hoặc
ROE bền **18,2%** (ở Ke 13,5%), hoặc Ke **11,4%** (ở ROE 14,6%). Ke 11,4% nằm trong dải CAPM cho ra với β thật của VCB (0,76 thô,
0,84 sau hiệu chỉnh Blume), không phải β 1,1 mặc định.

| Mục | Số | Nguồn |
|---|---|---|
| Giá trị sổ sách / cổ phiếu (BVPS, 30/09) | **30.359 đ** (VCSH công ty mẹ 253.669 tỷ / 8.355,7 triệu cp) | [BCTC] |
| Lợi nhuận 9T, headline vs lõi | +24,4% headline; **+12,5% lõi** sau khi bỏ lãi đánh giá lại khi hợp nhất, không chịu thuế (ước lượng) | [BCTC], §2 |
| Q3/2026 | Lợi nhuận trước dự phòng (PPOP) **+44,8% YoY**, nhưng LNTT **−0,2%** vì dự phòng 6.184 tỷ (Q3/25: 776 tỷ) | [BCTC] |
| Nợ xấu / bao phủ | NPL **0,71%** (từ 0,58%); bao phủ **243%**; nhóm 2 **+85% YTD** trong khi cho vay +8,5% | [BCTC] |
| Tâm định giá ở r 13,5% (ROE 14,6%) | **35.500** (P/B 1,169); có trọng số **39.100**; vùng Ke ±100bp **30.800–42.000**; mốc ROE 13,2% / 16% ⇒ **29.000 / 42.000** | `calc.py` |
| Ở Ke theo β thật 12% (ROE 14,6%) | **46.100** (dưới giá 52.100) | `calc.py` |
| Thanh khoản | ADV trung vị 3 năm **175 tỷ/phiên** (Price×Volume, BQ; 153 nếu Close×Volume; trung vị 1 năm 281) ⇒ chiết khấu thanh khoản 0 (giá trị trước = sau) | [BQ] |
| Moat (5F tầng b) | **NARROW**: hào chi phí vốn + chất lượng tài sản; không thưởng và không trừ vào mô hình | §6 |
| Pháp lý | WARNING nhẹ: KTNN điều chỉnh hồi tố 2025 (nhỏ); thanh tra cấp chi nhánh; không có vụ án | §8 |

**Đọc nhanh:** đây là ca **"tốt nhưng không rẻ ở r của fleet"**. Quyết định chủ yếu là chọn Ke. Báo cáo này giữ tâm ở r 13,5% đúng luật
user 03/11, và in mốc β thật cạnh đó, không lấy mốc β thật làm tâm. Rủi ro thật cho lợi nhuận 2027 là áp lực NIM do chỉ đạo và tầng
nợ sớm (nhóm 2) tăng nhanh. Rủi ro này đã một phần lộ ra ở Q3: dự phòng tăng gấp 8 lần.

---

## 1. Kiểm chứng giả thuyết hàng đợi (New deals: "VCB VÀO double-confirm, 8L rating 1")

| Giả thuyết | Kiểm chứng bằng BCTC | Kết quả |
|---|---|---|
| Chất lượng hàng đầu (rating 1) | NPL 0,71%, bao phủ 243%, **không xoá nợ nào trong 9T/2026** (TM6: "xử lý nợ xấu bằng dự phòng" = 0; năm 2025 xoá 7.288 tỷ) | **Đúng** |
| Lợi nhuận tăng mạnh | 9T LNST công ty mẹ 33.032 tỷ, **+24,4%**. Có khoản một lần: lãi thuần HĐ khác +3.171 tỷ do "đánh giá lại giá trị khoản đầu tư theo giá trị hợp lý khi hợp nhất kinh doanh" (giải trình mục 2), tức Bonday-Bến Thành chuyển từ liên doanh 52% thành công ty con (TM8, GCN 03/06/2026). LNST quý theo BQ: Q2/26 14.542 tỷ vs Q1 9.457 / Q3 9.033 | **Nửa đúng**: lõi **+12,5%** (ước lượng, coi toàn bộ phần tăng thêm là một lần; **không chịu thuế**: ETR thực 9T/25 19,82% × LNTT 37.269 = 7.388 so với thuế thực 7.386, tr.20 BCTC ⇒ lãi đánh giá lại không phát sinh thuế; LN lõi 29.861 tỷ) |
| Q3 tốt | PPOP +44,8%, NII +39,1% YoY; LNTT Q3 **đi ngang** (11.218 vs 11.239 tỷ) | Mạnh ở dòng trên, bị dự phòng ăn hết |

**Lệch nguồn ghi lại (không chọn im lặng):**
- Báo chí [24hmoney, Báo] ghi LNTT 9T **43.789 tỷ, +32%**; BCTC hợp nhất ghi **40.440 tỷ, +22,05%**; riêng lẻ 36.431 tỷ. Báo cáo này dùng BCTC.
- [Bobby] §2b ghi NPL 3 NH quốc doanh trong khoảng **1,20–1,85%**. VCB theo BCTC là **0,71%**, nằm ngoài khoảng đó. Khoảng bao phủ 73–243% thì khớp ở đầu trên. Bobby tự khai số lấy từ snippet; nhiều khả năng khác định nghĩa hoặc khác mẫu. Không dùng khoảng NPL của Bobby cho VCB.
- BQ `ROE_Trailing` 2026Q3 = 17,31% có gồm khoản một lần ở Q2; ROE lõi tự tính là 16,65% (§5).

## 2. Chất lượng lợi nhuận (9T/2026 vs 9T/2025, hợp nhất, tỷ đồng) [BCTC]

| Dòng | 9T/26 | 9T/25 | Δ |
|---|---|---|---|
| Thu nhập lãi thuần | 57.179 | 42.505 | **+34,5%** (cho vay chỉ +8,5% YTD ⇒ phần lớn do NIM/đòn bẩy tài sản sinh lãi) |
| Dịch vụ thuần | 2.707 | 2.605 | +3,9% (yếu) |
| Ngoại hối | 6.408 | 4.939 | +29,7% |
| HĐ khác thuần | 5.919 | 2.748 | +115% (**một lần** ~3.171) |
| Chi phí HĐ | (23.363) | (17.715) | +31,9%; CIR 32,0% |
| PPOP | 49.620 | 35.470 | +39,9% (lõi +30,9%) |
| Dự phòng rủi ro tín dụng — cho vay | (6.190) | n/a | gồm dự phòng chung 1.003 + cụ thể 5.187 (TM6 tr.40) |
| Dự phòng — TPDN chưa niêm yết giữ đến đáo hạn | (2.997) | n/a | TM7 tr.41: dự phòng cụ thể 3.307→6.304, gốc còn 6.501, **đã trích 97%** |
| Tổng dự phòng (cho vay + TPDN) | (9.180) | (2.338) | ×3,9 |
| LNTT | 40.440 | 33.133 | +22,1% |

- **NIM:** BCTC quý không công bố NIM. Báo chí ghi NIM Q2/2026 3,03%, "cao nhất 8 quý" [Báo, elibook/ACBS — chưa đối chiếu]. Tức PPOP 2026 đang ở **đỉnh NIM**. [Bobby] §2a đọc NIM nhóm quốc doanh Q4/26–Q1/27 là "đi ngang đến giảm" (CV 9608/9736 ép giảm lãi cho vay 1,5–2pp, KBNN rút, CCTG/cấp 2 đắt).
- **Lãi dự thu** 11.811 tỷ, +18,0% YTD so với cho vay +8,5%. Mức ≈ 0,65% dư nợ, không bất thường về quy mô. Nhưng tốc độ tăng gấp 2 tín dụng, cùng hướng với ngành (+40% YoY) ⇒ WARNING nhẹ, không điều chỉnh BVPS.
- **Chi phí thuế** 18,3% LNTT, bình thường.

## 3. Chất lượng tài sản [BCTC TM5–6]

| Chỉ tiêu | 30/09/2026 | 31/12/2025 (trình bày lại) |
|---|---|---|
| Nợ nhóm 2 | 4.995 (0,28%) | 2.702 (0,16%) |
| Nợ nhóm 3 / 4 / 5 | 2.571 / 1.657 / 8.589 | 761 / 302 / 8.651 |
| NPL (3–5) | **12.817 = 0,71%** | 9.714 = 0,58% |
| Dự phòng cho vay (chung + cụ thể) | 31.168 (13.425 + 17.743) | 24.980 |
| Bao phủ NPL | **243%** | 257% |
| Xoá nợ bằng dự phòng 9T | **0** | 7.288 (cả năm 2025) |
| Hình thành NPL 9T (Δ NPL + xoá) | **3.104** ≈ 0,18% dư nợ BQ (≈ 0,24% năm hoá) | — |
| Chi phí tín dụng CHO VAY 9T năm hoá | **0,47%** dư nợ BQ (6.190 ÷ dư nợ BQ × 12/9; tổng gồm TPDN 0,70%) | — |

**Đọc:** cờ của Bobby (§7.12, "nhóm 2 tăng > 2 lần tốc độ cho vay") **CHẠM**: nhóm 2 +85% so với cho vay +8,5%. Nợ chuyển xuống
**nhóm 3–4** (tăng từ 1.063 lên 4.229 tỷ), chưa xuống nhóm 5. Đây là pha sớm. Nhưng quy mô tuyệt đối vẫn nhỏ so với đệm: dự phòng
31,2 nghìn tỷ ≈ 2,4× NPL. Kể cả khi toàn bộ nhóm 2–4 thành mất trắng (9.223 tỷ), dự phòng hiện có vẫn đủ. Câu hỏi của Q7 (Bobby,
dự phòng 2026 > 2025) với riêng VCB gần như chắc chắn **CÓ**: 9T đã 9.180 tỷ, trong khi 9T/25 chỉ 2.338 tỷ.
**Cơ cấu 9.180:** cho vay 6.190 + TPDN chưa niêm yết 2.997. Nguồn kéo LN này **gần cạn**: dự phòng TPDN đã trích 97% gốc còn lại (6.304/6.501) ⇒ chiều tốt cho dự phòng 2027 nếu không có mã mới. Chưa thấy chênh lệch dự phòng so với chuẩn bao phủ 100% ⇒ **không điều chỉnh trừ BVPS**.

Chưa kiểm trong lượt này: top-10 khách hàng / VCSH, dư nợ BĐS, ý kiến kiểm toán 2025 — **cần kiểm** ở BCTC kiểm toán 2025 (đã tải nhưng chưa đọc được, §10) hoặc Pillar 3.
Ngoại bảng (BCTC Q3 tr.18): bảo lãnh khác **+38% YTD**, cam kết khác **+88% YTD** ⇒ WARNING nhẹ, chưa định lượng rủi ro; không điều chỉnh BVPS.

## 4. Nguồn vốn, thanh khoản, vốn

| Chỉ tiêu | 30/09/2026 | 31/12/2025 | Ghi chú |
|---|---|---|---|
| Tiền gửi khách hàng | 1.781.703 (+6,5% YTD) | 1.672.535 | [BCTC TM11] |
| CASA (không kỳ hạn / TG KH) | **31,8%** | 33,7% | Ngành 19,4% Q3 [Báo 24hmoney]; xu hướng giảm |
| Tiền gửi KBNN (TM9) | **171.617** (có kỳ hạn VND 170.175) + repo TPCP với KBNN 10.479 | 136.001 | **8,8%** (TG KH + KBNN), từ 7,5% ⇒ **chạm cờ Bobby §7.7 (>8%)** |
| Giấy tờ có giá phát hành | 47.392 (CCTG 31.937, trái phiếu dài hạn 11.455) | 27.101 | +20,3 nghìn tỷ, chủ yếu CCTG ngắn hạn ⇒ chi phí biên đắt hơn (đúng cơ chế Bobby §1b) |
| Vay NHNN | 282 | 24.127 | Đã trả hết vay cầm cố GTCG |
| LDR thô (cho vay / (TG KH + GTCG)) | 99,3% | — | **Không phải** định nghĩa TT22/TT50; LDR theo quy định **chưa có số** |
| CAR | Basel III ~11,1–11,6% (30/06/2026) | — | [Báo, 1 nguồn — chưa đối chiếu Pillar 3]; CET1 chưa có số |

**Độ nhạy KBNN (ước lượng):** nếu KBNN rút về mức cuối 2025 (−35,6 nghìn tỷ) và được thay bằng CCTG đắt hơn khoảng 2pp, NII giảm
khoảng 0,7 nghìn tỷ/năm ≈ 1% NII năm hoá. Tác động nhỏ với VCB. Cờ vẫn chạm, nhưng không phải biến số lớn.

**Cổ đông và cổ phiếu [BCTC TM1(b), TM14]:** Nhà nước **74,80%**, Mizuho **15,00%**, khác **10,20%** ⇒ free float thật khoảng
10%. 8.355.675.094 cp, **không đổi trong 9T/2026**. Hành động vốn chờ thực hiện [Báo: ĐHĐCĐ 24/04/2026, **chưa đối chiếu nghị
quyết gốc**]:
(a) phát hành từ nguồn vốn chủ khoảng 10.687 tỷ (≈ **+12,8%** số cp, ước lượng);
(b) cổ tức từ LN 2025 là 20.331 tỷ, **chưa rõ** tiền hay cổ phiếu, đang trình cơ quan nhà nước (nếu bằng cổ phiếu ≈ +24,3% số cp);
(c) phát hành riêng lẻ **tối đa 6,5%** (~543 triệu cp, ≤55 nhà đầu tư), Chủ tịch nói "cố gắng trong 2026".
⇒ (a) và (b) **không đổi giá trị**, chỉ chia nhỏ cổ phiếu. Mọi giá trị/cp trong báo cáo này là **trên số cp hiện hành**, so được
trực tiếp với giá 52.100 (chưa qua ngày giao dịch không hưởng quyền). Sau khi (a) và (b) thực hiện, chia cho (1 + tỷ lệ).
(c) chỉ tăng BVPS nếu giá phát hành > BVPS; hướng có lợi, nhưng chưa đưa vào base.

**Nghĩa vụ chính sách (Bobby §7.15):** công ty con 100% "**Ngân hàng TNHH MTV Ngoại thương Công nghệ số**" (giấy phép 15/GP-NHNN
27/03/2026, TM1(d)). Đây là ngân hàng nhận chuyển giao bắt buộc **[NỀN — chưa đối chiếu tên cũ trong BCTC]**. Theo skeptic R2 (chưa tự đối chiếu văn bản gốc),
ngân hàng này **được miễn hợp nhất và bị loại khỏi tính CAR** ⇒ lỗ của nó **không chảy qua LN hợp nhất/BVPS hay CAR** của VCB; rủi ro còn lại là
quyết định hỗ trợ vốn/thanh khoản và khả năng bỏ miễn trừ. BCTC Q3 không có thuyết minh riêng về quy mô, lỗ luỹ kế hay hỗ trợ ⇒ **WARNING: chưa định lượng được**. 

## 5. Định giá — P/B = (ROE bền − g)/(Ke − g); MÙ giá thị trường

**Không áp dụng** cho ngân hàng (Bobby §7.1, luật DD): P/PCF, EV/EBITDA, FCFE, V_ngắn/V_dài, dòng C4, dòng D2. CFO của NH chứa
biến động tiền gửi/cho vay. Không in số.

**Chi phí vốn:** r = **13,5%**, đúng điểm neo 03/11. Lãi huy động 12T hiệu dụng `deposit_rate_vn.effective_deposit_rate()` =
**7,40%** (CCTG 12M 02/11/2026) tại cả 03/11 và 17/11 ⇒ không điều chỉnh (β pass-through = 1). β thật VCB so với VNINDEX (tuần,
06/2021–11/2026, n=282): **0,763**, tương quan 0,60 ⇒ Blume **0,84** < 1,1 mặc định. Ke nội địa với β 0,84 ≈ 10,9–11,9%; làm tròn
**12%** làm MỐC ĐỌC, không làm tâm.

**ROE bền (không dùng ROE năm có khoản một lần / năm giảm dự phòng):**
- Lịch sử [BQ ROE_Trailing]: 2019 23,5% → 2022 23,6% → 2024 18,3% → 2025 16,3%; `ROE_Min5Y` 16,7%. ROE 2025 tự tính 16,7% (VCSH đầu kỳ ước từ BQ, ước lượng). Xu hướng giảm vì vốn tích luỹ nhanh hơn lợi nhuận.
- ROE lõi 9T/26 năm hoá: **16,65%** (LN lõi 29.861 tỷ, lãi đánh giá lại không chịu thuế). Theo chi phí tín dụng chuẩn hoá trên PPOP lõi: CC 0,4% → 18,4% · 0,6% → 17,2% · 0,8% → **16,0%** · 1,0% → 14,9%.
- **Ba mốc ROE bền (minh bạch, cùng g 7%, Ke 13,5%):**
  - **13,2%** = ROE 2025 chuẩn hoá chi phí tín dụng 0,8% (sức sinh lời năm nền, trước đợt tăng NIM 2026) ⇒ **29.000**.
  - **16,0%** = PPOP lõi 9T/26 năm hoá với CC 0,8% (≈ 1,7× CC cho vay hiện tại 0,47%) ⇒ **42.000**. **KHÔNG phải mốc thận trọng**: nó dùng PPOP ở đỉnh NIM, đúng mức mà §9 và §7 cảnh báo chịu áp lực chỉ đạo giảm lãi.
  - **14,6%** = trung điểm hai mốc trên ⇒ **35.500**. **Chọn làm TÂM** vì (i) 13,2% bỏ qua tăng trưởng PPOP có thật của 2026, (ii) 16,0% giả định đỉnh NIM tồn tại vĩnh viễn; trung điểm không tựa vào một trong hai giả định cực. Lựa chọn tâm là phán đoán (ước lượng), không suy ra từ dữ liệu; bảng 3 mốc để người đọc tự chọn.
- **ROE ở CET1 mục tiêu:** CAR ~11,35% (giữa khoảng báo chí) so với mục tiêu ~12% (10,5% + D-SIB giả định 1–2%) ⇒ ROE 14,6% × 11,35/12 = **13,8%** ⇒ giá trị **31.800**. Chỉ là thông tin rủi ro (D-SIB chưa ban hành; Bobby Q11 P=0,25), không đổi headline.
- **g = 7%** (ước lượng; ≤ GDP danh nghĩa dài hạn; ≪ ROE × (1 − tỷ lệ cổ tức tiền ~10%)).

**Kịch bản (tâm theo luật = base):**

| Kịch bản | P | Giả định | P/B | Giá trị/cp |
|---|---|---|---|---|
| Xấu | 0,25 | ROE 13,5% = Ke (NIM −30bp theo chỉ đạo + CC 1,0% + gánh nặng NH chuyển giao) | 1,00 | **30.400** |
| Cơ sở | 0,50 | ROE 14,6% (tâm, xem ba mốc), g 7% | 1,169 | **35.500** |
| Tốt | 0,25 | ROE 18% (NIM giữ, CC 0,4–0,6%), g 8% | 1,82 | **55.200** |
| **Có trọng số** | | | | **39.100** |

**Độ nhạy theo lãi huy động** (ROE 14,6%, g 7%; β pass-through 1 / 0,5):

| Δ lãi huy động 12T | −100bp | −50bp | 0 | +50bp | +100bp |
|---|---|---|---|---|---|
| Giá trị/cp (β=1) | 42.000 (+18%) | 38.500 (+8%) | 35.500 | 33.000 (−7%) | 30.800 (−13%) |
| Giá trị/cp (β=0,5) | 38.500 | — | 35.500 | — | 33.000 |

g 6% / 8% ⇒ 34.800 / 36.400. Chiết khấu thanh khoản: **0%** (ADV trung vị 3 năm 175 tỷ/phiên, Price×Volume BQ [153 nếu Close×Volume; 281 trung vị 1 năm]; tham gia 5% ≈ **8,75 tỷ/phiên**, vị thế ≤10 tỷ thoát trong ≤2 phiên) ⇒ giá trị trước = sau. Free float 10% là giới hạn cho quỹ lớn, không phải cho quy mô fleet.

**Vùng đọc:** rẻ ≤ **30.200** (0,85 × tâm) · hợp lý **30.800–42.000** (Ke ±100bp) · trên **42.000** = đắt theo r 13,5% (**độ nhạy theo r/Ke**: giá 52.100 chỉ đạt khi Ke ≈ 11,4% hoặc ROE ≈ 18,2%; xem hai giai đoạn bên dưới).
Đối chiếu sau khi định giá xong (không dùng để suy ngược): giá 52.100 = P/B 1,72 ⇒ hàm ý ROE 18,2% ở Ke 13,5%, hoặc Ke 11,4% ở ROE 14,6%.

**Độ nhạy mô hình hai giai đoạn (HIỂN THỊ, không đổi tâm):** 5 năm BV tăng g1, ROE 14,6%, chia = (ROE − g1) × BV đầu kỳ, sau đó P/B Gordon g 7%
(`calc.py`, khối `two_stage`). Gordon một giai đoạn ngầm chia cổ tức 56% lợi nhuận, trong khi VCB chia tiền thực tế ~10%.

| Ke | g1 13% | g1 10% |
|---|---|---|
| 13,5% (tâm theo luật) | **36.800** | 36.100 |
| 12,5% (−100bp) | **45.100** | 43.400 |

Tâm headline vẫn **35.500** (một giai đoạn, r 13,5%) theo luật; hai giai đoạn chỉ nâng giá trị thêm khoảng +4% ở g1 13% (tương ứng 36.800), không đủ để chạm 52.100.

**P/B lịch sử 5 năm — HIỂN THỊ SAU định giá, không dùng để suy ngược** (BQ `tav2_bq.ticker` cột `PB`, PIT theo ngày, 2021-11-17 → 2026-11-17, n=1.246 phiên/mã; truy vấn 17/11/2026):

| Mã | P/B hiện tại | P10 | Trung vị | P90 | Đáy 5 năm | Phân vị hiện tại |
|---|---|---|---|---|---|---|
| **VCB** | **1,72** | 2,16 | 2,83 | 3,33 | 1,72 | 0,1% (= đáy) |
| BID | 1,19 | 1,57 | 1,97 | 2,28 | 1,19 | 0,1% (= đáy) |
| CTG | 1,16 | 1,18 | 1,36 | 1,66 | 0,93 | 6,9% |
| ACB | 1,14 | 1,26 | 1,40 | 1,74 | 1,13 | 0,5% |
| TCB | 1,14 | 0,87 | 1,21 | 1,79 | 0,66 | 33,4% |
| MBB | 1,16 | 1,03 | 1,26 | 1,71 | 0,85 | 27,5% |
| VPB | 1,08 | 1,03 | 1,20 | 1,67 | 0,86 | 26,1% |
| HDB | 1,55 | 1,16 | 1,46 | 1,88 | 0,95 | 68,4% |
| STB | 2,12 | 1,14 | 1,33 | 2,06 | 0,77 | 92,0% |

Đọc: VCB đang ở đáy 5 năm của chính nó nhưng vẫn là P/B cao nhất nhóm NH lớn (trừ STB); cả nhóm quốc doanh/ACB nằm gần đáy 5 năm ⇒ phần nén P/B là chung ngành, không riêng VCB. Đây là mô tả, **không** thành cơ sở nâng tâm.

## 6. Vị thế & lợi thế cạnh tranh (5F tầng b) — làm đầy đủ lần đầu

`data/moat_tags.csv`: **không có dòng VCB**; không có `kb/projects/vcb-dd-*` ⇒ làm đầy đủ (lần kế tiếp ≥ 11/2027).
Loại hình: NHTM Nhà nước chi phối, bán buôn + bán lẻ, đầu mối thanh toán quốc tế / ngoại hối.

| Lực | Đọc | Bằng chứng định lượng |
|---|---|---|
| Nguồn vốn (nhà cung cấp) | **Lợi thế** chi phí vốn bình quân | CASA 31,8% so với ngành 19,4% [BCTC; Báo]; KBNN 171,6 nghìn tỷ (đặc quyền hành chính, Bobby §3) |
| Khách vay (người mua) | Trung tính–yếu: bán buôn, biên mỏng, bị chỉ đạo giá | Tỷ trọng SXKD nhóm 51–66% [Bobby]; CV 9608 ép −1,5–2pp |
| Cạnh tranh nội ngành | Lợi thế chất lượng tài sản | NPL 0,71% so với ngành 2,09% (SSI 13 NH) [Bobby §2b]; bao phủ 243% so với ngành 77% |
| Thay thế (fintech, ví) | Thấp–trung bình; dịch vụ thuần chỉ +3,9% | [BCTC] |
| Gia nhập mới | Rào cản giấy phép cao | — |
| **Lực thứ 6 (chính sách)** | **Hai chiều**: bảo lãnh ngầm của Nhà nước (hút tiền gửi khi có sự cố) ↔ nghĩa vụ phi thương mại (NH chuyển giao bắt buộc, giảm lãi theo chỉ đạo, room tín dụng); quy chế KBNN (sửa NĐ 24, dự kiến 01/2027) | TM1(d); Bobby §2d, Q9 |

**Kiểm 3 điều kiện moat bền:** (i) ROE − Ke > 0 nhiều chu kỳ: **có** (ROE_Min5Y 16,7% > 13,5%), nhưng chênh chỉ khoảng 3pp và
đang thu hẹp (23,5% năm 2019 → 16,3% năm 2025). (ii) Cơ chế gọi tên được: nền tiền gửi được Nhà nước bảo chứng (CASA) + kỷ luật
tín dụng (NPL thấp nhất). (iii) Đồng hồ cắt hào: CASA đang giảm (33,7% → 31,8% trong 9T), KBNN là đặc quyền có thể đổi, Basel
III/D-SIB pha loãng ROE.
⇒ **moat_tier = NARROW** (không phải WIDE: chênh ROE so với Ke nhỏ và đang co; hai trụ hào có công tắc hành chính).
**Tham số moat trong mô hình: KHÔNG có** (không thưởng, không trừ — luật 08/11). Tâm ROE 14,6% < ROE_Min5Y (16,7%), không ngầm thưởng.

**Độ nhạy theo moat:** WIDE (ROE 18%) **51.400** · NARROW (base) **35.500** · NONE (ROE → Ke) **30.400**.

**Đề xuất dòng `data/moat_tags.csv`** (human-curated; KHÔNG tự ghi):
`VCB,NARROW,cost_of_funds+asset_quality (state-backed deposit franchise),DD 2026-11-17,"policy burden: directed lending-rate cuts / KBNN rule / compulsory-transfer subsidiary",2026-11-17,agents/Taylor/research/dd_VCB_20261117/REPORT.md,`

## 7. Bối cảnh vĩ mô (DISPLAY-ONLY, chỉ dòng cờ `ok` — `macro_snapshot_20261117.md`) và "điều thị trường chưa tính"

- Tái cấp vốn 4,50% (Δ12T 0) · liên NH 3M 6,33% (Δ3T −1,19pp) · spread 3M − điều hành +1,83pp (giả thuyết D2, chỉ mô tả) · TPCP 10Y **Δ12T +0,57pp** (lỗ đánh giá nhẹ danh mục AFS 153,8 nghìn tỷ; dự phòng rủi ro tín dụng **TPDN chưa niêm yết** đã tăng 3,36 → 6,35 nghìn tỷ [BCTC TM7] — KHÔNG phải lỗ AFS/TPCP 10Y) · USD/VND 25.764 (Δ12T −2,24%). Không chỉnh giá trị nội tại theo các dòng này.
- **Thị trường có thể chưa tính (chiều tốt):** (1) dự phòng 243% và chưa xoá nợ năm 2026 ⇒ có đệm để LN 2027 không phải trích bù mạnh, nếu nhóm 2 không chuyển tiếp xuống; (2) NQ 79 giữ lại lợi nhuận ⇒ BVPS tăng nhanh hơn trong khi tăng trưởng tín dụng được nới; (3) riêng lẻ 6,5% trên BVPS có lợi cho BVPS.
- **Chiều xấu:** (1) PPOP 2026 ở đỉnh NIM, đúng lúc chỉ đạo giảm lãi vay đè lên nhóm quốc doanh; (2) nhóm 2 +85% và nợ chuyển xuống nhóm 3–4 ×4; (3) ngân hàng con nhận chuyển giao chưa được định lượng; (4) cung cổ phiếu NH lớn 2026–27 (~128 nghìn tỷ toàn ngành [Bobby §2c]) đè lên kênh định giá.

## 8. Pháp lý / quản trị — chỉ WARNING (luật 27/09)

- ⚠️ **KTNN điều chỉnh hồi tố số liệu 2025** (dự phòng, TSCĐ, phải thu, lãi phải thu, chi phí, thuế), trình bày lại từ BCTC Q3/2026. Quy mô nhỏ: VCSH riêng lẻ +29 tỷ; LN trước dự phòng 2025 hợp nhất +46,9 tỷ [BCTC Phụ lục II]. Ý kiến kiểm toán BCTC 2025: chưa đọc trong lượt này (file đã tải) — **cần kiểm**.
- ⚠️ Kết luận thanh tra NHNN cấp chi nhánh 2026 (Đà Nẵng 228/KL-TTNH, "chưa đến mức xử lý hành chính"; Bình Phước 78/KL-TTRA.BP 12/08) [Báo/DNSE]. Không tìm thấy vụ khởi tố cán bộ VCB năm 2026 (tìm kiếm báo chí, chưa tra UBCKNN/HOSE).
- ⚠️ Nghĩa vụ chính sách: ngân hàng con nhận chuyển giao (§4); chỉ thị giảm lãi suất cho vay; quyết định tăng vốn và hình thức cổ tức cần cơ quan chủ sở hữu duyệt (biến hành chính, Bobby §2c).
- ⚠️ BCTC Q3 **không** soát xét; CV CBTT đánh dấu "Signature Not Verified" trên bản tải (do trình đọc PDF, không phải dấu hiệu giả mạo).

## 9. Mốc khoá trước & điều kiện đổi nhận định (hai chiều)

**Hướng tích cực (tâm ↑ / chuyển sang "hợp lý-rẻ"):** BCTC Q4/2026 (≈ cuối 01/2027) có **nhóm 2 giảm QoQ** và bao phủ ≥ 200% mà
chi phí tín dụng cả năm ≤ 0,8%; **hoặc** lãi huy động 12T hiệu dụng giảm ≥ 50bp (tâm +8%); **hoặc** phát hành riêng lẻ ≥ 1,5× BVPS;
**hoặc** giá ≤ 30.200.
**Hướng tiêu cực (tâm ↓):** NPL > 1,0% **hoặc** nhóm 2 + nhóm 3–4 > 1,0% dư nợ tại Q4/26; bao phủ < 180%; lãi huy động hiệu dụng
+50bp (tâm −7%); quy định D-SIB ≥ 1,5% (Bobby Q11); VCB công bố khoản hỗ trợ vốn/thanh khoản cho ngân hàng chuyển giao > 5% LNST năm, **hoặc** miễn trừ hợp nhất/loại khỏi CAR bị bỏ (lỗ của nó vào LN hợp nhất và CAR).
**Theo dõi:** BCTC Q4 (KBNN, nhóm 2, NIM tự tính — Bobby Q1/Q4/Q5); ngày chốt quyền phát hành thưởng và cổ tức; CBTT riêng lẻ; Pillar 3 / CAR.

## 10. Việc chưa làm (cho skeptic / Mike)
- **Chưa đọc được BCTC kiểm toán 2025** (`src/VCB_BCTC_2025_KT_HN.pdf`; môi trường không có poppler/PyMuPDF, cài đặt bị chặn): ý kiến kiểm toán, VCSH đầu kỳ 2025 (hiện là **196.112,9** (nguồn skeptic R2, chưa tự đối chiếu) trong `calc.py`:48, chỉ ảnh hưởng ROE 2025 tự tính 16,7%, không ảnh hưởng tâm), top khách hàng, BĐS. Cần ai đó có công cụ đọc PDF. Chưa có CET1/LDR theo TT22, chưa có CASA theo cá nhân/DN.
- Số cổ phiếu sau phát hành và hình thức cổ tức: báo chí mâu thuẫn, **chưa đối chiếu nghị quyết ĐHĐCĐ gốc**.
- Khoản một lần 3.171 tỷ: dùng phần chênh của HĐ khác làm proxy; thuyết minh hợp nhất kinh doanh chi tiết không có trong BCTC quý.

## Nguồn
- BCTC Q3/2026 hợp nhất (CBTT 30/10/2026): https://static2.vietstock.vn/data/HOSE/2026/BCTC/VN/QUY%203/VCB_Baocaotaichinh_Q3_2026_Hopnhat.pdf
- BCTC kiểm toán 2025 hợp nhất: https://static2.vietstock.vn/data/HOSE/2025/BCTC/VN/NAM/VCB_Baocaotaichinh_2025_Kiemtoan_Hopnhat.pdf
- ĐHĐCĐ 2026: https://baodautu.vn/dhdcd-vietcombank-dang-tim-nha-dau-tu-de-chao-ban-65-von-du-chi--20331-ty-dong-tra-co-tuc-d576464.html · https://nhadautu.vn/chu-tich-vietcombankngan-hang-co-gang-hoan-thanh-phat-hanh-co-phieu-rieng-le-trong-nam-2026-d104560.html · https://doanhnhan.baophapluat.vn/dhdcd-vietcombank-vcb-2026-kiem-soat-chat-tin-dung-bat-dong-san-dau-co-don-luc-tang-von-len-gan-94-000-ty-dong.html
- LNTT 9T theo báo chí / CASA ngành: https://24hmoney.vn/news/buc-tranh-loi-nhuan-ngan-hang-quy-3-2026-c30a2854597.html · https://vnbusiness.vn/cuoc-phan-hoa-nghin-ty-tai-nhom-ngan-hang-quy-iii2026.html
- NIM Q2, CAR 30/06 (chưa đối chiếu): https://elibook.vn/?p=121700 · https://acbs.com.vn/acbsmedia/2026/08/VCB_cap-nhat_ACBS_07.08.2026-VN.pdf
- Thanh tra chi nhánh: https://www.dnse.com.vn/senses/tin-tuc/mot-chi-nhanh-ngan-hang-o-da-nang-chua-thuc-hien-day-du-cong-tac-tham-dinh-kiem-tra-giam-sat-von-vay-35262386 · https://www.dnse.com.vn/senses/tin-tuc/vietcombank-chi-nhanh-binh-phuoc-chua-thuc-hien-nghiem-tuc-quy-dinh-cua-nhnn-35270234
- BQ: `tav2_bq.ticker_financial` (VCB 2015Q4–2026Q3), `tav2_bq.ticker` (giá/ADV tới 2026-11-17, β tuần 2021-06 → 2026-11).
