# DD NT2 (CTCP Điện lực Dầu khí Nhơn Trạch 2) — sleeve discretionary, chạy MÙ (job `Taylor_20261026_045653`, 2026-10-26)

> READ-ONLY, không phải khuyến nghị mua — user quyết. Giá tham chiếu **24.100 đ (đóng cửa 23/10/2026, BQ `ticker`)**.
> Nhãn nguồn: **[BQ]** · **[BCTC]** BCTC Q3/2026 bản gốc (CV 1394/CPNT2-TCKT 19/10/2026, ảnh scan đọc trực tiếp) ·
> **[BC]** báo chí · **[UL]** ước lượng (ghi công thức) · **[CB]** = `CYCLE_BLOCK.md` đã khoá. Script: `src_step2/calc_step2.py`.

```
BLIND_ATTESTATION (của cả job)
  buoc_1_viet_boi                  : subagent mới (general-purpose, opus, agentId a4b04738de607e17d), chỉ đọc TEMPLATE.md
  da_viet_truoc_khi_doc_BCTC_quy_Q : có (CYCLE_BLOCK mtime 12:04:35 ICT < file bước 2 đầu tiên; BCTC Q3 tải sau LOCK)
  da_doc_DD_cu_cua_ma_nay          : không (cả subagent lẫn Taylor, tới khi viết xong mục 0–H)
  da_biet_verdict_truoc            : subagent: không biết verdict fleet; THẤY tiêu đề khuyến nghị CTCK (ACBS "MUA" 26.700; "khả quan" 26.000) qua tóm tắt WebSearch
                                     Taylor (điều phối, viết bước 2): CÓ — README §4 của template ghi verdict cũ NT2 = NON
  quy_Q                            : 2026Q3, công bố 19–20/10/2026
  du_lieu_tai_chinh_dung_den_quy   : 2026Q2 (bước 1)
  cycle_block_md5                  : 4afe613f25b946a709ebc124120e4a79
  cycle_block_commit               : KHÔNG commit (theo dispatch) — thay bằng LOCK.txt + mtime
  thoi_diem_khoa (ICT)             : 2026-10-26T12:05:07+07:00
  blind                            : no  (xem lý do dưới)
```
**Vì sao `blind: no`:** dispatch quy định thấy *bất kỳ verdict nào của ai về mã này* ⇒ `blind: no`. Người viết khối chu kỳ
thấy 2 tiêu đề khuyến nghị CTCK (không mở). Mức lộ nhẹ hơn DDV/SAS (không lộ verdict fleet, không lộ số Q3), nhưng luật là luật.
Người viết bước 2 (tôi) biết verdict cũ NON qua README — không ảnh hưởng khối chu kỳ, nhưng có thể ảnh hưởng verdict bước 3.

## KHỐI CHU KỲ
Nguyên văn tại `CYCLE_BLOCK.md` (md5 `4afe613f…`, khoá 12:05 ICT). Tóm tắt: loại = annuity hợp đồng có thành phần chu kỳ (huy động/
thủy văn + giá khí neo dầu) · A: biên LNST TTM 14,3% phân vị 82 (BQ), loại hiệu ứng hết khấu hao ≈9,8% phân vị ≈44 · C: **KHÔNG XÁC
ĐỊNH** (chuỗi đầu ra thiếu), nghiêng GIỮA-LÊN về huy động, biên cao một phần là CẤU TRÚC · D: dòng tiền có thời hạn (khí hiện hữu cạn
~2030, HĐ khí ~2035, PPA sau 2020 chưa xác minh) · E: PE chuẩn hoá ex-cash 6,5x, PB 1,29x, DCF có thời hạn 21.600–29.500 đ ·
F: biên LNST TTM 2026Q1–Q4 ≥ 12,0%, p = 0,60, due 2027-01-31.

---

## 0. Verdict: **NON**

| Tiêu chí | Phán quyết | Bằng chứng chính | Dùng khối chu kỳ? |
|---|---|---|---|
| Có trigger sợ hãi (§0.5) | **KHÔNG** | Giá 24.100, +17% từ 20.600 (21/09); 52 tuần 20.250–28.900 [BQ]; LNST Q3 +95% yoy [BCTC] | — |
| §2 nhóm (a) | N/A | Không có scandal cá nhân lãnh đạo | — |
| §2.5 #1 chu kỳ, không cấu trúc | **FAIL / không áp dụng** | Không có khủng hoảng để phân loại. Rủi ro dài hạn là CẤU TRÚC: khí hiện hữu cạn ~2030, nhà máy 15 tuổi đã khấu hao 93% nguyên giá, NT3&4 1.624 MW cạnh tranh huy động | D |
| §2.5 #2 sống sót | PASS | Net cash 3.578 tỷ (tiền 11,8 + tiền gửi 5.362,3 − vay 1.795,8) [BCTC 30/09] | — |
| §2.5 #3 dẫn đầu chi phí | N/A | Giá bán cost-plus theo PPA (Qc×Pc), không cạnh tranh giá kiểu hàng hoá | A |
| §2.5 #4 sàn tài sản PB≲1 | **FAIL** | PB 1,28x (24.100/BVPS 18.832 [BQ 2026Q3]); tài sản cố định ròng chỉ 761,6 tỷ / VCSH 5.421 tỷ ⇒ "sàn" là tiền gửi, không phải nhà máy | E |
| Loại: "đáy chưa tới / không xác định" | Không áp dụng | Không có đáy để đợi — đang là pha LN tăng | C |

**Định giá:** PE chuẩn hoá ex-cash **6,3x** (LN chuẩn hoá 760 tỷ, mục 4), DCF có thời hạn ≈22.300–30.200 đ (ước lượng) quanh giá 24.100 ⇒ hợp lý,
không rẻ kiểu fear-buy. **Đổi verdict khi:** có trigger thật (giá −30% với lõi nguyên vẹn) VÀ PB ≤ 1,0 (≈ ≤ 18.800 đ) VÀ có HĐ khí sau 2030 rõ ràng.
**Pháp lý:** không có WARNING pháp lý; có 1 WARNING chất lượng số liệu (soát xét bán niên giảm LNST 94 tỷ — mục 7).

## 1. Giả thuyết và kiểm chứng
Không có giả thuyết fear-buy từ user cho NT2 trong dispatch; đây là phép thử phương pháp. Giả thuyết kiểm tra: "LN Q3 tăng là chu kỳ đỉnh hay
cấu trúc?" ⇒ **chủ yếu cấu trúc + khối lượng** (mục 2), khớp khối mù.

## 2. Phân rã LN Q3/2026 [BCTC tr.4, tr.5]
| Khoản (tỷ đ) | Q3/26 | Q3/25 | Δ | Bền? |
|---|---|---|---|---|
| Doanh thu | 2.807,2 | 1.928,2 | +879,0 (+45,6%) | Khối lượng: SL 1.160 tr kWh +47% [BC 24hmoney] — chu kỳ huy động (El Niño) |
| LN gộp | 489,9 (17,45%) | 204,6 (10,61%) | +285,2 | Xem dòng dưới |
| Khấu hao trong quý [UL: 9T − 6T] | 38,3 | 172,3 | −134,0 | **CẤU TRÚC** (máy móc hết khấu hao; 9T 114,8 vs 515,8 [BCTC LCTT mã 02]; H1 76,5/343,5 lấy từ [CB]) |
| Biên gộp TIỀN (GP + KH)/DT [UL] | **18,82%** | **19,55%** | **−0,7đ%** | Biên tiền mặt KHÔNG mở rộng — toàn bộ cải thiện biên kế toán đến từ hết khấu hao |
| DT tài chính (lãi tiền gửi) | 92,4 | 48,8 | +43,6 | Bền khi còn net cash; phần tiền gửi được tài trợ bởi phải trả PV GAS (mục 3) |
| Chi phí tài chính | 27,0 | 16,0 | +11,0 | Vay ngắn hạn tài trợ phải thu EVN |
| Chi phí QLDN | 28,6 | 0,9 | +27,6 | Q3/25 thấp bất thường (có thể hoàn nhập); 9T 89,0 vs 41,1 |
| LNTT / LNST | 524,1 / 418,6 | 239,2 / 214,2 | +95,4% LNST | Thuế 20,1% |

Phân bổ +285 tỷ LN gộp [UL]: ≈134 tỷ do khấu hao giảm (cấu trúc, lặp lại tới khi có đầu tư lớn), ≈151 tỷ do khối lượng (chu kỳ huy động).
LN lõi sau thuế ex-lãi tiền gửi Q3 ≈ 418,6 − (92,4 − 27,0)×0,8 ≈ **366 tỷ** [UL].

**9T/2026 [BCTC]:** DT 7.803,4 tỷ (+43,6%), LNST 906,4 tỷ (+57,0%), EPS 3.092 đ.
⚠️ 9T 906,4 − Q3 418,6 = **H1 487,7 tỷ** ≠ tổng Q1+Q2 tự lập 180,0 + 403,0 = 583,0 [BQ/BC] ⇒ chênh **−95 tỷ** = điều chỉnh soát xét bán niên
(−94 tỷ LNST, ghi nhận thêm giá vốn hợp đồng bảo trì sửa chữa dài hạn tổ máy, −119 tỷ LN gộp [BC stockbiz, tổng hợp WebSearch]).

## 3. Bảng cân đối, dòng tiền, cổ tức [BCTC tr.2–3, tr.5]
- Tiền 11,8 · đầu tư giữ đến đáo hạn ngắn hạn 5.362,3 (chủ yếu tiền gửi SHB [BC baophapluat]) · vay ngắn hạn 1.795,8 · **net cash 3.578,4 tỷ**
  (12.430 đ/cp). Trừ cổ tức phải trả 297,1 tỷ ⇒ 3.281,3 tỷ.
- Phải thu khách hàng (EVN) 4.252,0 (đầu năm 3.770,2) · **phải trả người bán 2.637,4 (đầu năm 1.234,3; ~2.618 là PV GAS [BC])** ⇒ net cash tăng
  một phần nhờ CHƯA TRẢ tiền khí. Nếu PV GAS thu về mức đầu năm, net cash giảm ≈1.400 tỷ [UL].
- CF_OA 9T **1.256,2 tỷ** vs LNST 906,4 ⇒ CF_OA/NP 1,39 — nhưng gồm +890,6 tăng phải trả và −520,1 tăng phải thu. Trước vốn lưu động 1.089,5.
- Capex 9T 2,5 tỷ ⇒ gần như không đầu tư duy trì lớn ghi nhận (bảo trì đi qua giá vốn/chi phí trả trước).
- Cổ tức tiền đã trả 9T chỉ 0,1 tỷ; phải trả cổ tức 297,1 tỷ (≈1.032 đ/cp [UL]) ⇒ cổ tức 2025 chưa chi hết. Kế hoạch 20–30% [CB WEB-1].
- Nợ vay dài hạn = 0; VCSH 5.421,4 tỷ; tổng tài sản 11.107,5 tỷ.

## 4. Định giá — trên LN chuẩn hoá
| | Khối mù (BS 30/06) | Cập nhật BS 30/09 |
|---|---|---|
| Vốn hoá (24.100 × 287,876 tr cp) | 6.938 | 6.938 |
| Net cash dùng tính | 3.066 [CB, trích ABS/Mirae] | 3.281 (sau trừ cổ tức phải trả) [BCTC] |
| Lãi tiền gửi sau thuế [UL: net cash × 6,8% × 0,8] | 167 | 178 |
| LN chuẩn hoá (trung vị LNST 2013–2025) | 760 | 760 (không đổi; soát xét chỉ chạm 2026) |
| **PE chuẩn hoá ex-cash** | 6,5x | **6,3x** = 3.657/582 |
| Biến thể "hết khấu hao" (LN 1.187, ước lượng) | 3,8x | 3,6x (ước lượng) |
| PE thô trailing (TTM Q3 BCTC 1.459 tỷ) | — | 4,75x |
| PB | 1,29x | 1,28x (vô hình 22,9 tỷ — PB hữu hình ≈1,28x) |
| DCF có thời hạn 9 năm, 12%, không giá trị cuối | 21.600–29.500 | ≈22.300–30.200 (ước lượng; chỉ cộng +215 tỷ net cash) |

Cảnh báo cho dòng biến thể "hết khấu hao": điều chỉnh soát xét cho thấy chi phí **bảo trì dài hạn (LTSA)** đang thay chỗ khấu hao — tài sản 15 tuổi
cần đại tu; một phần "tiết kiệm khấu hao" sẽ quay lại dưới dạng giá vốn bảo trì. ⇒ biến thể 3,6x là cận lạc quan.

## 5. Thanh khoản [BQ `ticker`, `src_step2/nt2_px.csv`]
ADV 20 phiên (đến 23/10): trung bình **31,2 tỷ**, trung vị **27,4 tỷ**. Size thực thi ở 10% trung vị ADV ≈ 2,7 tỷ/phiên [UL].

## 6. Điều kiện ĐỔI verdict
- Sang **AMBIGUOUS** khi: giá ≤ 18.800 đ (PB ≤ 1,0) **do** sự kiện không phá lõi (vd cắt huy động tạm thời, tranh chấp thanh toán EVN có thời hạn)
  VÀ net cash ≥ 2.500 tỷ sau khi trả PV GAS.
- Giữ **NON** bất kể giá nếu: không ký được HĐ khí bổ sung (PL13, Hải Thạch–Mộc Tinh) cho giai đoạn sau 2030, hoặc PPA hết hạn không gia hạn.

## 7. ⚠️ WARNING pháp lý/quản trị (chỉ cảnh báo; luật 2026-09-27)
- **WARNING chất lượng số tự lập:** BCTC bán niên 2026 soát xét giảm LNST 94 tỷ so số tự lập (ghi thiếu giá vốn bảo trì) [BC]. Số Q3/2026 cũng là
  tự lập, chưa soát xét ⇒ rủi ro điều chỉnh tương tự ở BCTC năm 2026.
- Không thấy CBTT pháp lý bất thường trong phạm vi job (KHÔNG quét chuyên sâu CBTT/legal-vn — chưa kiểm).
- Cổ đông chi phối PV Power (nhà nước) — không đánh giá thêm.

## 8. Lệch dữ liệu giữa các nguồn
| Mục | Nguồn A | Nguồn B | Xử lý |
|---|---|---|---|
| LNST Q2/2026 (*đính chính sau khi mở báo cáo cũ, xem I*) | BQ dòng 2026Q2 `NP_P0` 403,0 (tự lập, chưa restate) | BQ dòng 2026Q3 `NP_P1` **307,8** (đã restate) [`src_step2/nt2_np_lags.csv`]; BCTC 9T suy ra H1 487,7 = 180,0 + 307,8 ✓ | Điều chỉnh soát xét nằm ở **Q2**, không phải Q1 như bản đầu tôi viết. BQ có số đúng nhưng ở cột trễ `NP_P1` của dòng quý sau — dòng gốc không restate. Dùng 307,8 |
| Tiền | BQ `Cash_P0` 11,8 tỷ | BCTC: tiền 11,8 + tiền gửi đáo hạn 5.362,3 | Đúng bẫy template mục E — dùng BCTC |
| Biên gộp TTM | BQ `GPM_P0` 2026Q3 16,43% | BCTC quý: Q3 17,45%; 9T 13,65% | GPM_P0 là TTM và gồm số tự lập H1 — không dùng |
| DT 9T | Σ BQ 3 quý 7.803,9 | BCTC 7.803,4 | Khớp |

## H. Đối chiếu khối chu kỳ (KHÔNG sửa khối gốc)
| Mục | Khối mù nói | BCTC Q3 / thông tin sau khoá cho thấy | Khớp / lệch | Đổi verdict? |
|---|---|---|---|---|
| A biên | LNST TTM 14,3%, phân vị 82 (BQ) | TTM đến Q2 **sau soát xét** = 13,28% (phân vị 79); TTM đến Q3 [BCTC] = 14,13% (phân vị 81) [`calc_step2.py`, N=53 quý] | **Lệch mức ~1đ%, đúng hướng.** Nguồn lệch: dòng 2026Q2 của BQ không restate (số đúng 307,8 chỉ có ở `NP_P1` dòng 2026Q3, công bố sau khoá) — mà thông tin soát xét (08/2026) ĐÃ công khai trước khoá; khối mù bỏ sót vì tin BQ | Không |
| A cắt chuỗi "hết khấu hao" | Biên cao một phần là CẤU TRÚC; ex-KH ≈ 9,8% | Q3: KH 38,3 vs 172,3; biên gộp tiền 18,8% vs 19,6% cùng kỳ ⇒ biên tiền KHÔNG tăng; toàn bộ mở rộng biên kế toán = hết KH | **KHỚP mạnh** — đây là phát hiện có giá trị nhất của khối | Không (củng cố NON) |
| C pha | KHÔNG XÁC ĐỊNH, nghiêng GIỮA-LÊN về huy động; chống: Brent 116,8 ép giá khí | SL Q3 +47%; giá khí Q3 −3% qoq [BC 24hmoney] — áp lực dầu chưa vào giá khí quý này | Khớp phần ủng hộ; phần "chống" chưa hiện (có thể do độ trễ công thức giá khí) | Không |
| D | Khí cạn ~2030; tài sản già; PPA sau 2020 chưa xác minh | Soát xét lộ chi phí bảo trì dài hạn tổ máy — khớp "tài sản già" | Khớp (bổ sung bằng chứng) | Không |
| E PE chuẩn hoá | 6,5x; PB 1,29x | 6,3x; PB 1,28x | Khớp | Không |
| F dự báo | Biên LNST TTM 2026 ≥ 12,0% | 9T theo BCTC = 11,62% [UL 906,4/7.803,4]; cần LNST Q4 ≥ ≈330 tỷ nếu DT Q4 ≈2.500 tỷ (ước lượng) | Chưa tới hạn. ⚠️ **Rủi ro chấm**: `source` khai là Σ `NP_P0` BQ — BQ còn số Q1 tự lập (dòng 2026Q2 `NP_P0` 403,0 thay vì 307,8 đã restate: +95 tỷ ≈ +0,9đ%) ⇒ chấm theo BQ có thể ra HIT trong khi BCTC năm ra MISS. Đề xuất Mike chấm bằng BCTC năm 2026 kiểm toán, ghi cả hai | — |

- **Verdict có phụ thuộc khối chu kỳ không?** Không. Bỏ khối chu kỳ verdict vẫn NON (không có trigger, PB > 1). Khối chu kỳ làm verdict **vững hơn**
  ở 1 điểm: tách được "biên cao" thành cấu trúc (hết khấu hao) + khối lượng (El Niño), chứng minh không có "LN chu kỳ bị nén" để mua rẻ.
- **Bài học cho template:** thêm bẫy dữ liệu thứ 3 — *BQ `ticker_financial` giữ số TỰ LẬP, không cập nhật số soát xét/kiểm toán* (NT2 H1/2026: −95 tỷ).
  Số đúng có ở cột trễ `NP_P1` của dòng quý sau. Khối mù nên kiểm "có điều chỉnh soát xét bán niên/kiểm toán năm không" trước khi tính TTM.

## Sổ chấm
- Entry đề xuất gửi Mike (sổ chưa được duyệt tạo): `CYC-NT2-20261026`, `blind: no` (lý do: tiêu đề khuyến nghị CTCK lọt qua tóm tắt WebSearch), FORECAST nguyên văn
  `CYCLE_BLOCK.md` mục F, kèm ghi chú nguồn chấm (mục H dòng F). Không tính vào cổng đánh giá.

## Nguồn
- [BCTC] https://static2.vietstock.vn/data/HOSE/2026/BCTC/VN/QUY%203/NT2_Baocaotaichinh_Q3_2026.pdf (tải 26/10/2026; tr.1–3 văn bản giải trình; tr.6–9 BCĐKT/KQKD/LCTT đọc từ ảnh scan)
- [BC] https://24hmoney.vn/posts/-c55a2847410.html (20/10/2026: SL 1.160 tr kWh, giá khí −3% qoq) · https://doanhnhan.baophapluat.vn/dien-luc-dau-khi-nhon-trach-2-nt2-bao-lai-9-thang-tang-manh-57-vuot-xa-ke-hoach-nam.html (PV GAS 2.618, tiền gửi SHB, KH 2026 LNST 430 tỷ)
- [BC] soát xét bán niên −94 tỷ: tóm tắt WebSearch dẫn stockbiz.vn (https://stockbiz.vn/tin-tuc/mot-dai-gia-nganh-dien-boc-hoi-119-ty-dong-loi-nhuan-sau-soat-xet/41538060) — **không mở trang**; số khớp với suy ra độc lập từ BCTC Q3 (−95 tỷ)
- [BC] Q1/2026 tự lập 180 tỷ: tóm tắt WebSearch (DSC, stockbiz) — không mở trang
- [BQ] `tav2_bq.ticker_financial` NT2 2024Q3–2026Q3 (`src_step2/nt2_fin_q3.csv`), `tav2_bq.ticker` 21/09–23/10/2026 (`src_step2/nt2_px.csv`), 52 tuần MIN/MAX Close
- [CB] `CYCLE_BLOCK.md` và `src_step1/*`

## I. So với báo cáo cũ `dd_NT2_20261026/REPORT.md` (job `Taylor_20261026_011018`) — mở SAU khi mục 0–H đã ghi

| | Cũ | Mới (mù) |
|---|---|---|
| Verdict | **NON** (value/cổ tức, không phải fear-buy) | **NON** — **không đổi** |
| Lý do chính | Không trigger §0.5; §2.5 #1 FAIL (đang pha thuận, "gần đỉnh chu kỳ thủy văn"); #4 PB 1,28 > 1 | Không trigger; #1 không áp dụng + rủi ro dài hạn cấu trúc; #4 PB 1,28 > 1 |
| Định giá | SOTP net cash + DCF 10 năm; trọng số ≈25.400 đ (+5%); PE ex-cash base ≈5,0x | PE chuẩn hoá ex-cash 6,3x; DCF 9 năm ≈22.300–30.200 đ (ước lượng) |
| Đọc chu kỳ | "LN gần đỉnh chu kỳ thủy văn, Qc cao" | "KHÔNG XÁC ĐỊNH (thiếu chuỗi), nghiêng GIỮA-LÊN; biên cao chủ yếu do hết khấu hao" |

**Giống:** verdict, PB, net cash ≈3.578 tỷ, nhận diện khấu hao là phần tăng bền nhất, dòng tiền có thời hạn (~2035–36), bẫy `Cash_P0`, cảnh báo soát xét −94 tỷ.

**Khối mù bắt được mà báo cáo cũ không nói rõ:**
1. **Biên gộp TIỀN (GP + khấu hao) Q3 không tăng** (18,8% vs 19,6% cùng kỳ). Báo cáo cũ ghi "biên gộp 10,6% → 17,5%" và "giá khí không phải biến số
   chi phối" — đúng về kế toán, nhưng không tách được rằng toàn bộ mở rộng biên là khấu hao. Phát hiện này đến từ mục A ("cắt chuỗi tại điểm hết khấu hao").
2. **Phân vị biên trên ≥ 1 chu kỳ** (82, ex-KH ≈ 44): cho số cụ thể cho câu "LN gần đỉnh", và cho thấy phần CHU KỲ của biên đang ở giữa, không ở đỉnh —
   tinh chỉnh (không đảo) nhận định "gần đỉnh" của bản cũ.
3. Một dự báo bác bỏ được có ngày (F) — bản cũ không có.

**Báo cáo cũ bắt được mà khối mù bỏ sót/sai:**
1. **NT3&4 thuộc POW, không phải NT2** — khối mù ghi đúng là đối thủ huy động, nhưng không nêu đó là công ty mẹ ⇒ bỏ sót xung đột lợi ích POW (59,4%)
   cần tiền (NT5 ~9.000 tỷ, không chia cổ tức tiền mặt) — **WARNING quản trị quan trọng nhất** của mã này. Bản mới của tôi (mục 7) cũng bỏ sót.
2. **Q4/2025 553 tỷ có khoản một lần** và 9T/2025 có doanh thu bù Qc ⇒ TTM bị thổi phồng. Khối mù chỉ nghi ngờ (bù tỷ giá ~155 tỷ), không loại.
3. **Điều chỉnh soát xét nằm ở Q2** (BQ `NP_P1` dòng 2026Q3 = 307,8). Bản đầu của tôi gán nhầm vào Q1 — đã đính chính mục 8 sau khi đọc bản cũ.
   Khối mù (bước 1) dùng 403,0 chưa restate ⇒ TTM 14,3% thay vì 13,3%, dù tin soát xét đã công khai từ 08/2026.
4. PPA hết hạn ~10/2036, GSA 31/12/2036 (1 nguồn) — khối mù để "chưa xác minh".
5. Tập trung tiền gửi tại SHB; lịch sử đính chính BCTC 2022, phạt thuế 2020.

**Kết luận phép thử:** khối chu kỳ mù **không đổi verdict** (NT2 không có trigger nên đây là mẫu thử yếu — đúng như README §4 dự đoán). Giá trị gia tăng
là **chất lượng lập luận** (tách cấu trúc/chu kỳ trong biên), không phải quyết định. Chi phí: bỏ sót rủi ro quản trị nhóm công ty mẹ, vì mẫu A–F không có
câu hỏi về cổ đông chi phối/dùng tiền — đề xuất thêm vào mục D: "ai kiểm soát dòng tiền tự do và họ cần tiền cho việc gì, có ngày".
