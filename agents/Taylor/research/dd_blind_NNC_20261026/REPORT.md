# DD NNC (CTCP Đá Núi Nhỏ) — sleeve discretionary, chạy MÙ theo mẫu v1 (job `Taylor_20261026_045700`, 2026-10-26)

> READ-ONLY, không phải khuyến nghị mua — user quyết. Giá tham chiếu **47.600 đ (đóng cửa 23/10/2026, BQ `ticker`)**.
> Nhãn nguồn: **[BQ]** · **[BCTC]** BCTC giữa niên độ Q3/2026 bản gốc, ký 19/10/2026 (scan, đọc từ ảnh trang:
> `static2.vietstock.vn/data/HOSE/2026/BCTC/VN/QUY 3/NNC_Baocaotaichinh_Q3_2026.pdf`, tải 26/10/2026) · **[CTCK]**
> FPTS 07/01/2026 · **[WEB]** · **[UL]** ước lượng của tôi.

```
BLIND_ATTESTATION
  da_viet_truoc_khi_doc_BCTC_quy_Q : có (BCTC Q3 tải và đọc SAU khi khoá, 12:01 ICT)
  da_doc_DD_cu_cua_ma_nay          : không (trước khi ghi verdict mục 0)
  da_biet_verdict_truoc            : CÓ — working memory Taylor bơm đầu phiên dòng "dd-NNC 10-26 … NON (không fear-state,
                                     đỉnh chu kỳ, PB1,59); weighted 62,8k vs 47,6k"; README template (file được giao đọc)
                                     có biên gộp Q3 57,9%, "đá +50% so 2023–24", "giấy phép 2043", "PE 4,88x", phụ lục "khẳng định NON"
  quy_Q (mới nhất đã công bố)      : 2026Q3       ngày công bố: 2026-10-20 (BQ Release_Date; BCTC ký 19/10/2026)
  du_lieu_tai_chinh_dung_den_quy   : 2026Q2
  cycle_block_md5                  : 07b687cd6a3702acb96a4f8aa43534df
  cycle_block_commit               : KHÔNG commit (dispatch yêu cầu) — thay bằng LOCK.txt + mtime 2026-10-26 12:00:51 +07:00
  thoi_diem_khoa (ICT)             : 2026-10-26T12:01:00+07:00
  => blind: NO
```

## KHỐI CHU KỲ
Xem `CYCLE_BLOCK.md` (đã khoá, md5 trên; không chép lại để không lệch bản khoá). Tóm tắt: loại = chu kỳ cầu đầu tư;
A biên LNST TTM 38,8% phân vị 100; B giá bán Mũi Tàu cao nhất chuỗi 2020–9T25; **C = ĐỈNH**; D giấy phép Mũi Tàu hết
2043 + cung Tam Lập 2/3; E PE chuẩn hoá ex-cash 16,7x (E1) / 8,7x (E2), PB 1,70x; F biên LNST TTM 2027Q1 ≤ 40,0%.

---

## 0. Verdict: **NON** (không có trạng thái sợ hãi để mua; đang ở đỉnh biên, PB 1,59)

| Tiêu chí §2.5 (nhóm b) | Phán quyết | Bằng chứng chính | Dùng khối chu kỳ? |
|---|---|---|---|
| Có trigger khủng hoảng chu kỳ/tạm thời | **KHÔNG CÓ** trigger | Doanh thu Q3 +49,1% YoY, LNST +62,8% YoY [BCTC]; giá +22% từ 08/10 (39.000) tới 23/10 (47.600) [BQ] | C (ĐỈNH) — củng cố, không quyết định |
| #1 Chu kỳ, không cấu trúc | N/A (không có khủng hoảng); rủi ro tương lai = chu kỳ (cầu 2028) + cấu trúc nhẹ (giấy phép 2043) | FPTS: cầu cụm 4,9 → 3,0 tr m³ (2027F→2028F) | C, D |
| #2 Sống sót | PASS mạnh | Tiền + HTM 347,9 tỷ vs vay 74,9 tỷ ⇒ net cash **273,0 tỷ** [BCTC] | Không |
| #3 Dẫn đầu chi phí | PASS một phần | Mũi Tàu: công suất cấp phép lớn nhất cụm (1 tr m³) [CTCK]; biên gộp đá thành phẩm Q3 59,9% [BCTC TM bộ phận] | Không |
| #4 Sàn tài sản PB ≲ 1 | **FAIL** | PB 1,59x (47.600 / BVPS 29.915) [BCTC] | E |
| Loại "đáy chưa tới" | **FAIL nặng hơn: đang ở ĐỈNH, không phải đáy** | Biên LNST TTM 40,3%, cao nhất lịch sử | A, C |

Định giá (dòng tiền có thời hạn tới 2043, mục 4): trọng số **~43.200 đ (ước lượng)** vs giá 47.600 ⇒ không có biên an
toàn. Đổi verdict: chỉ khi có cú sốc giá đá/cầu làm biên giảm về ≤ 25% VÀ giá ≤ 30.000 (PB ≲ 1,0) — mục 6.
Pháp lý: WARNING nhẹ — khoản truy thu tiền cấp quyền khai thác mỏ Núi Nhỏ (20,4 tỷ) đã tất toán trong 9T2026.

## 1. Giả thuyết và kiểm chứng
- Giả thuyết kiểm: "PE TTM ~4–5x = rẻ". Sai bản chất: PE thấp vì LN đang ở đỉnh chu kỳ biên, dòng tiền lõi có thời hạn
  17 năm, và một phần giá trị là tiền mặt. Bẫy "PE thấp ở đỉnh" (backstop §8, HPG chiều ngược).

## 2. Phân rã LN Q3/2026 [BCTC tr.4, tr.29]
| Khoản | Q3/26 | Q3/25 | 9T26 | 9T25 |
|---|---|---|---|---|
| Doanh thu thuần | 149,49 | 100,27 | 402,20 | 261,89 |
| LN gộp (biên) | 86,54 (**57,9%**) | 50,67 (50,5%) | 218,52 (54,3%) | 128,34 (49,0%) |
| DT tài chính | 6,07 | 7,60 | 15,60 | 13,48 |
| CP bán hàng + QLDN | 5,14 | 4,00 | 12,87 | 14,02 |
| Thu nhập − chi phí khác | −0,0003 | −1,88 | −19,29 | −4,18 |
| LNTT | 86,61 | 52,04 | 200,14 | 116,28 |
| LNST | **69,29** | 42,56 | **160,08** | 93,95 |
- Lõi bền (có điều kiện chu kỳ): mỏ Tân Lập/Mũi Tàu — DT 143,28 tỷ, LN gộp 84,16 tỷ (58,7%); đá thành phẩm 139,97 tỷ
  DT, giá vốn 56,07 ⇒ biên 59,9% [BCTC TM bộ phận tr.29].
- Một lần / không lõi: chi phí khác 9T 22,0 tỷ (gần hết ở 1H26; trùng thời điểm tất toán tiền cấp quyền Núi Nhỏ 20,4 tỷ
  — số dư đầu năm 20.426.182.763 → 0 [BCTC V16]; liên hệ nhân quả **chưa xác minh**). DT tài chính ~6 tỷ/quý = lãi tiền gửi.
- LNST TTM tại Q3 = 213,96 tỷ / DT TTM 531,26 tỷ ⇒ **biên LNST TTM 40,3%** [BQ NP_P0/Revenue_P0 2025Q4–2026Q3, khớp BCTC Q3].

## 3. Bảng cân đối, dòng tiền, cổ tức [BCTC 30/09/2026]
- Tiền 25,47 tỷ + **HTM ngắn hạn 322,44 tỷ** = 347,91 tỷ. Vay ngắn hạn 5,00 + dài hạn **69,89** (từ 22,22 đầu năm; vay mới
  51,0 tỷ trong 9T) = 74,89 tỷ. Net cash **273,0 tỷ** = 12.455 đ/cp.
- VCSH 655,73 tỷ; BVPS 29.915 đ; TSCĐ vô hình 5,14 tỷ (PB hữu hình ≈ PB).
- **XDCB dở dang 108,00 tỷ (đầu năm 0)** [BCTC V10a]: đền bù chuyển nhượng QSDĐ **dự án mỏ đá Tam Lập 1 khu II** 79,48 tỷ;
  đặt trước tiền cấp quyền khai thác dự án này 4,03 tỷ; máy nghiền 350T/giờ (Cty NHC) 21,29 tỷ; lắp đặt 3,21 tỷ.
  ⇒ NNC đang mở mỏ thứ hai trong chính cụm Tam Lập — đổi bài toán thời hạn/công suất (mục H).
- Dòng tiền 9T: CF_OA 109,27 tỷ vs LNST 160,08 ⇒ **0,68x**; capex 131,06 tỷ; cổ tức trả 21,41 tỷ (1.000 đ/cp, lợi suất
  2,1%). Q3 riêng: CF_OA 63,13 tỷ vs LNST 69,29 (0,91x) [BQ CF_OA_P0]. CF_OA thấp ở 1H do nộp thuế 45,9 tỷ 9T và tất toán
  tiền cấp quyền (ước đoán, chưa tách được từ LCTT trực tiếp).

## 4. Định giá — dòng tiền có thời hạn (giấy phép Mũi Tàu tới 2043, ~17 năm) [UL]
Vốn hoá 1.043 tỷ (47.600 × 21,92 tr cp). Lãi tiền gửi sau thuế ≈ 15,6 tỷ × 4/3 × 0,8 = 16,6 tỷ/năm, tách khỏi LN lõi.
Hệ số niên kim 17 năm @12% = 7,12; 3 năm = 2,40.

| Kịch bản | LN lõi/năm (ex lãi tiền gửi) | Giá trị lõi | + net cash 273 | /cp | Trọng số |
|---|---|---|---|---|---|
| Bear (E1: trung vị 2023–25 = 62,6 → lõi 46) | 46 × 7,12 = 327 | 600 | **27.400** | 25% |
| Base (E2: biên 30% × DT 2025 = 117 → lõi 100) | 100 × 7,12 = 712 | 985 | **44.900** | 50% |
| Bull (giữ TTM lõi 197 thêm 3 năm rồi về base) | 197×2,40 + 100×4,72 = 945 | 1.218 | **55.600** | 25% |
| **Trọng số** | | | **~43.200 (ước lượng)** | |
- Không định giá quyền chọn mỏ Tam Lập 1 khu II (chưa biết trữ lượng/công suất/thời hạn; mới chi 83,5 tỷ) — đây là
  upside chưa lượng hoá, và cũng là capex tiếp theo.
- PE chuẩn hoá ex-cash: E1 (1.043−273)/(62,6−16,6) = **16,7x**; E2 770/(117−16,6) = **7,7x**; TTM 770/(214,0−16,6) = 3,9x.

## 5. Thanh khoản
ADV 20 phiên **1,21 tỷ/phiên** (trung vị 0,93 tỷ; KL TB 27.795 cp) [BQ `ticker` Price×Volume]. Ở 10% ADV ⇒ ~0,1 tỷ/phiên,
~2 tỷ/tháng (ước lượng). Size thực thi được rất nhỏ so với NAV các book.

## 6. Điều kiện ĐỔI verdict
- Sang AMBIGUOUS/QUALIFY chỉ khi đồng thời: (i) biên LNST TTM ≤ 25% (về trung vị 5 năm) do giá đá/cầu cụm giảm — tức
  cú sốc chu kỳ thật; (ii) giá ≤ 30.000 đ (PB ≲ 1,0 với BVPS ~30k); (iii) net cash còn ≥ 200 tỷ sau capex Tam Lập 1.
- Theo dõi: thông tin trữ lượng/giấy phép Tam Lập 1 khu II (công suất, thời hạn) — nếu kéo dài đời mỏ > 2043 thì định
  giá base tăng, nhưng không đổi verdict khi PB > 1 và không có trigger.

## 7. ⚠️ WARNING pháp lý/quản trị (chỉ cảnh báo)
- Truy thu tiền cấp quyền khai thác mỏ Núi Nhỏ (QĐ 1581/QĐ-UBND Bình Dương, theo FPTS) — 20,43 tỷ phải trả đầu năm, đã
  về 0 ở 30/09/2026 [BCTC V16]. Rủi ro còn lại: truy thu tương tự với mỏ đã đóng khác (chưa thấy).
- Dự án mỏ Tam Lập 1 khu II: đã chi đền bù QSDĐ 79,5 tỷ trước khi có giấy phép khai thác (chỉ "đặt trước tiền cấp quyền")
  ⇒ rủi ro thủ tục cấp phép/đền bù. Không thấy tranh chấp.

## 8. Lệch dữ liệu giữa các nguồn
| Chỉ tiêu | Nguồn A | Nguồn B | Xử lý |
|---|---|---|---|
| Tiền 30/09/26 | BQ `Cash_P0` 25,47 tỷ | BCTC tiền 25,47 + **HTM 322,44** | Dùng BCTC; BQ thiếu HTM (bẫy đã ghi ở mẫu, nay xác nhận thêm NNC) |
| Tiền 30/06/26 (bước 1) | BQ 72,05 tỷ | BCTC Q2 chưa đọc; HTM đầu năm 241,73 tỷ [BCTC Q3 cột đầu kỳ] | Net cash bước 1 (46,5) **thấp hơn thực tế ~200+ tỷ** |
| Vay dài hạn | BQ `LtDebt_P0` 69,89 | BCTC 69,89 | Khớp |
| `LtInvest_P0` | BQ 119,32 | BCTC: góp vốn 103,0 − DP 5,35 + LDLK 21,67 = 119,32 | Khớp; là góp vốn, KHÔNG phải tiền gửi (bước 1 xử lý đúng khi không cộng) |
| Biên gộp | BQ `GPM_P0` 2026Q3 = 0,533 | BCTC Q3 quý 57,9%; 9T 54,3% | `GPM_P0` KHÔNG phải biên quý; nhiều khả năng TTM (chưa tính lại GP TTM từ 4 BCTC quý) |

## H. Đối chiếu khối chu kỳ với BCTC Q3/2026 (KHÔNG sửa khối gốc)
| Mục | Khối mù nói | BCTC Q3 cho thấy | Khớp / lệch | Đổi gì trong verdict? |
|---|---|---|---|---|
| A biên | LNST TTM 38,8%, phân vị 100 | TTM 40,3% (Q3 quý 46,4%); biên gộp quý 57,9% | Khớp hướng (vẫn cao nhất lịch sử) | Không |
| C pha | ĐỈNH; bằng chứng chống "cầu còn tăng, đỉnh kéo dài 4–6 quý" | Biên còn MỞ RỘNG +1,5pp TTM trong 1 quý; DT +49% YoY | **Lệch một phần**: nhãn ĐỈNH theo phân vị đúng, nhưng chưa có dấu hiệu gãy — bằng chứng chống đang thắng ở chân trời 1 quý; đúng hơn "đỉnh chưa gãy / giữa-lên muộn" | Không (NON không phụ thuộc ĐỈNH vs GIỮA-LÊN) |
| D neo | GP Mũi Tàu hết 2043; Tam Lập là CUNG ĐỐI THỦ | NNC chi 83,5 tỷ cho **mỏ Tam Lập 1 khu II** của chính mình | **LỆCH lớn — bỏ sót**: rủi ro "dòng tiền có thời hạn" có thể bị kéo dài, và NNC tự thành một phần làn sóng cung Tam Lập | Không đổi verdict; đổi định giá (upside chưa lượng hoá) |
| E PE chuẩn hoá | Net cash 46,5 tỷ (BQ) ⇒ E1 16,7x / E2 8,7x | Net cash 273,0 tỷ ⇒ E1 16,7x / E2 7,7x; PB 1,59 | **Lệch đầu vào** (bẫy `Cash_P0`/HTM — mẫu đã cảnh báo, bước 1 tự nhận "không biết" nhưng chọn hướng thận trọng sai chỗ: không có HTM ở BQ) | Không đổi verdict; giá trị/cp +~10.000 đ so với dùng net cash BQ |
| F dự báo | biên LNST TTM 2027Q1 ≤ 40,0%, p 0,55 | TTM Q3 đã 40,3% — vượt ngưỡng ngay quý đầu | Chưa chấm (due 2027-05-01); xác suất trúng giảm rõ | — |
- **Verdict có phụ thuộc khối chu kỳ không?** Không. Bỏ khối chu kỳ, NON giữ nguyên vì (i) không có trigger sợ hãi,
  (ii) PB 1,59 > 1. Khối chu kỳ chỉ đổi lý do phụ (vì sao PE TTM thấp) và lộ ra 2 điểm bước 1 không bắt được do giới
  hạn dữ liệu ≤ Q−1: mỏ Tam Lập 1 khu II (chi đầu tiên xuất hiện trong 9T2026 — có thể đã thấy ở BCTC Q2 nếu bước 1 đọc
  BCTC Q2 gốc thay vì chỉ BQ) và HTM.
- Bài học cho mẫu: mục E nên BẮT BUỘC đọc bảng cân đối BCTC Q−1 gốc (không chỉ BQ) — cả 2 lệch lớn đều nằm ở đó.

## Sổ chấm
- Entry đề xuất: `CYC-NNC-20261026`, **blind: no** (nhiễm verdict cũ qua working memory + README) ⇒ không tính vào cổng.

## I. So với báo cáo cũ (`dd_NNC_20261026/REPORT.md`, đọc SAU khi verdict trên đã ghi)
| | Cũ (`Taylor_20261026_012529`) | Mới (job này) |
|---|---|---|
| Verdict | **NON** | **NON** — **không đổi** |
| Lý do chính | Không có khủng hoảng; PB 1,59; dính "mua ở đỉnh chu kỳ" | Như cũ (cùng 3 lý do) |
| Giá trị trọng số | **62.800 đ (+32%)** — r 14%, base 169 tỷ LN (giá −12% từ TTM) trọng số 40% | **~43.200 đ (−9%)** — r 12%, base 100 tỷ lõi (biên 30% × DT 2025) trọng số 50% |
| Net cash | 273,0 tỷ (đã bắt HTM 322,4) | 273,0 tỷ (bước 2); bước 1 mù sai còn 46,5 (BQ) |
| Cổ phần MVC/NHC | Cộng MVC theo giá thị trường 147,3 + NHC 14,1 = 161,4 tỷ (7.360 đ/cp) | **Bỏ sót** — coi 103 tỷ góp vốn là tài sản không định giá |
| Tam Lập 1 khu II | Có, kèm số AWM (11 tr m³, 1 tr m³/năm, từ 2028), upside thô ~15.000 đ/cp | Có (từ BCTC), không lượng hoá |
| Pháp lý | 3 WARNING: sở hữu chéo NNC↔MVC; có thể vượt trần công suất; đóng mỏ | 2 WARNING: truy thu tiền cấp quyền (đã tất toán); thủ tục mỏ mới |

**Giống:** verdict, cả 3 trụ (không trigger / PB > 1 / đỉnh chu kỳ), net cash, thời hạn 2043, Tam Lập 1 khu II.
**Khác:** chỉ ở định giá. Hai nguồn lệch chính, đo được: (1) LN chuẩn hoá — cũ đặt base gần TTM (169 tỷ, 79% TTM), mới đặt
base ở biên giữa chu kỳ (100 tỷ lõi, 47% TTM). Điểm này giải thích phần chênh còn lại ~12.200 đ/cp (62.800 − 43.200 − 7.360; r 12% của mới lại nâng giá trị ngược chiều); (2) mới bỏ sót cổ phần MVC/NHC
(−7.360 đ/cp). Cộng lại MVC/NHC thì giá trị mới ≈ 50.600 đ (ước lượng), vẫn quanh giá thị trường.

**Khối chu kỳ mù có bắt được gì báo cáo cũ bỏ sót không?**
- Có một điểm: mục A/C buộc neo LN chuẩn hoá vào **lịch sử biên của chính mã** (trung vị TTM 27,8%, 5 năm 25,9%), trong khi kịch bản
  cũ dùng biên gộp 35–56% và đặt 55% xác suất vào base/bull ≥ 50%. README phụ lục đã dự đoán đúng: "nếu C kết luận ĐỈNH, trọng số
  nghiêng về deep/bear, giá trị trọng số giảm". Nhận định phụ cũ "rẻ +32%, hợp value screen" **yếu đi** — ở base biên giữa chu
  kỳ thì giá hiện tại xấp xỉ giá trị hợp lý, không rẻ.
- Ngược lại, báo cáo cũ bắt được 3 thứ khối mù bỏ sót hoặc sai: HTM 322 tỷ (bước 1 dùng BQ), mỏ Tam Lập 1 khu II (bước 1 coi Tam Lập
  là cung ĐỐI THỦ), cổ phần MVC. Cả ba đều nằm trong **bảng cân đối BCTC gốc**, không nằm trong câu chuyện chu kỳ ⇒ khuyến nghị
  sửa mẫu: bước 1 phải đọc CĐKT + thuyết minh XDCB/đầu tư tài chính của BCTC **Q−1 gốc**, không chỉ BQ.
- **Hạn chế của phép so sánh:** blind = no. Tôi biết verdict NON, "PB 1,59" và "62,8k vs 47,6k" trước khi viết khối chu kỳ, nên
  việc chọn base thận trọng hơn có thể là phản ứng với con số cũ (thiên lệch hồi tưởng), không phải bằng chứng khối chu kỳ thêm
  thông tin. Kết quả này KHÔNG tính vào cổng đánh giá.

## Nguồn
- BQ `tav2_bq.ticker_financial` (NNC, 2010Q1–2026Q3), `tav2_bq.ticker` (giá, KL).
- BCTC giữa niên độ Q3/2026 NNC (ký 19/10/2026), tr.1–5 (CĐKT, KQKD, LCTT), tr.18 (V10a), tr.20 (V16), tr.29 (bộ phận).
- FPTS, "Báo cáo định giá lần đầu NNC", 07/01/2026 — `static1.vietstock.vn/edocs/18527/DuyNHKBao_cao_dinh_gia_lan_dau_NNC_c0067741.pdf`.
- nhadautu.vn 20/08/2026 "Giá cát, đá tăng mạnh…"; thesaigontimes.vn 16/07/2026 "Đồng Nai tìm thêm đá xây dựng…".
