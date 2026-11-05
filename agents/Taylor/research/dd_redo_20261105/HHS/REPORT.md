# DD REDO — HHS (CTCP Đầu tư Dịch vụ Hoàng Huy) · mùa BCTC Q3/2026 · 05/11/2026 · job `Taylor_20261105_014125`

> NGHIÊN CỨU, trung dung. Không phải khuyến nghị.
> **Nguồn:** BCTC GỐC hợp nhất + riêng Q3/2026 (ký 29/10, **chưa soát xét**), 6T soát xét AASC, KT25 — đã có ở `dd_HHS_20261101/src/`, KHÔNG tải lại. Số BCTC + tham số NAV lấy từ DD v2 01/11 (`dd_HHS_20261101/REPORT.md`, `calc/valuation_v2.py`; phản biện REFUTED medium → 12 đính chính đã áp, số tự kiểm lại trên ảnh) và DD TCH v2 (cùng tài sản CRV).
> Sector read Bobby (mù): `sector_read_bds_nha_o_do_thi_phia_bac_20261031.md` + `sector_read_xe_tai_thuong_mai_vn_20261101.md`.
> **Tính lại:** `$DNA_PYEXE -I calc/hhs_redo.py > calc/hhs_redo_out.txt` (tất định, md5 trùng 2 lần). Mọi số §1, §6–§8 từ `calc/hhs_redo_out.txt` / `SUMMARY.json`.

## 1. Kết luận (số chuẩn hoá liên mã)

| Chỉ số | Giá trị |
|---|---|
| Giá 04/11/2026 [BQ] | **9.550** |
| r | **13,50%** (neo 13,5% @ 7,40% `cctg_12m(2026-11-02)`; 04/11 không đổi) |
| Tâm TRƯỚC / SAU CK thanh khoản | 10.766 / **10.611** (CK 1,44% @5 tỷ) |
| P10 / P50 / P90 SAU CK | **8.415 / 10.615 / 13.010** (trước: 8.538 / 10.771 / 13.201) |
| Giá vs tâm / P10 / P90 | **−10,0%** / +13,5% / −26,6% |
| **Nhãn** | **TRONG vùng** (nửa dưới) |

Một câu: lãi Q3 tăng thật nhờ CRV bàn giao NC-II, không vay, nhưng ~9.570 đ/cp sổ sách là thặng dư PPA chưa thực hiện; giá thấp hơn tâm 10%, và gần như toàn bộ chênh so với DD cũ là do **bỏ chiết khấu quản trị khỏi base** (luật pháp lý chỉ WARNING).

## 2. Giả thuyết kiểm chứng (BCTC gốc; không đổi vì chưa có BCTC mới)

| Giả thuyết | Số | Kết quả |
|---|---|---|
| "Lãi Q3 bật mạnh, bền" | DT BĐS Q3 1.746; LNST mẹ Q3 115,8 (Q3/25 17,2); biên BĐS ex-PPA Q3 52,2% ≈ biên NC-II ở TCH 51,9% | ĐÚNG về nguồn (NC-II), nhưng Q3 **chưa soát xét** (6T soát xét hạ LNST mẹ −34%) |
| "Sổ sách 21.188 đ/cp là giá trị đã có" | ~4.134 tỷ (≈9.570 đ/cp) là thặng dư PPA khi hợp nhất CRV 06/2025 | SAI |
| "Mảng xe gãy" | Q3 DT 156,4 (−36,6%, nền Q3/25 đột biến), 9T +1,4%; tồn kho ×1,9, biên −3–5 điểm %, bắt đầu chiết khấu thương mại | NỬA ĐÚNG |

## 3. Chất lượng LN · bảng cân đối · ghi nhận DT
- **Net cash THẬT 30/09 hợp nhất:** tiền + HTM 1.030,6 − vay 0 − kinh phí bảo trì giữ hộ 124,75 ≈ **906**, chưa trừ chi phí còn lại để giao các căn đã nhận tiền. Tiền **công ty mẹ chỉ 171**; phần còn lại ở CRV/Đại Lộc (thiểu số 48,85%). Cổ tức CRV về HHS 9T/26: **0**.
- **Ghi nhận DT:** bàn giao (không POC); người mua trả trước NC-II 3.099,2 = backlog đã thu tiền; ngoài phần bàn giao có ~1.670 thu mới (ước lượng).
- **CFO 9T −2.110** (nộp tiền đất I.14 ~1.066; HTK +1.909 gồm I.14 1.329, NC-II +336, ô tô +290).
- Chi tiết + trang: `dd_HHS_20261101/REPORT.md` §3–§4.

## 4. Cổ đông · room · thanh khoản
- TCH 58,31% (ông Đỗ Hữu Hạ + HH Finance 35,99% TCH); nhóm Đinh Quang Chiến 5,12% (19/10/2026); NN 0,59%, room 50% ⇒ **free float 36,6%**.
- **Thanh khoản [BQ 250 phiên tới 04/11]:** ADV trung vị **16,2 tỷ**; σ ngày 2,60%; Amihud 7,63e−04/tỷ (cao gấp ~35–50 lần MBB/FPT/HPG).
  Vị thế 5 tỷ thoát **3,1 / 2,1 / 1,5 phiên** ở tham gia 10/15/20%. **CK @5 tỷ = 1,44%** (Y 0,5 → 0,72%; Y 1,5 → 2,16%; 1 tỷ 0,65%; 10 tỷ 2,04%). Đây là mã duy nhất trong nhóm có CK thanh khoản đáng kể.

## 5. Pháp lý / quản trị — WARNING (trung bình, không loại)
- Kiểm toán 2025 + soát xét 6T AASC chấp nhận toàn phần; BCTC 2025 không có thuyết minh bảo lãnh/mua lại xe. **Q3 chưa soát xét.**
- **⚠ WARNING:** thương vụ HHS Capital (người bán không nêu tên, không định giá độc lập, TCH được biểu quyết); ký quỹ 28,4 tỷ cho cá nhân; **KL 08/KL-TTTP 26/02/2026** (Thanh tra TP Hải Phòng) với NƠXH Pruksa (HHS 90,17%): rà soát, điều chỉnh giá bán theo quyết toán; 2 kết luận thanh tra đang mở ở nhóm CRV/Pruksa. TCH (mẹ) có 2 QĐ xử phạt thật (UBCKNN 12/2024; thuế 20,21 tỷ 04/2026); HHS chưa thấy QĐ xử phạt 2023–26.
- **Theo luật (pháp lý/quản trị = WARNING, không bake vào base): bỏ "CK quản trị" 15/10/5% của DD cũ khỏi base.** Chỉ còn là độ nhạy:

| CK quản trị (chỉ độ nhạy) | 5% | 10% | 15% |
|---|---|---|---|
| Tâm trước CK thanh khoản | 10.228 (−538) | 9.689 (−1.077) | 9.151 (−1.615) |

## 6. Định giá
### 6.1 Mô hình (NAV holding)
CRV 100% = CRV giá gốc 7.735 (= CRV theo GTHL 15.818 − thặng dư PPA sau thuế 8.083) + NMTT NC-II 3.099,2/1,08 × biên ròng backlog × PV(1 năm) + (HTK CRV còn lại 7.338,8 − **I.14 1.329**) × thặng dư × PV(4 năm) + **I.14 × 0 (giá sổ, NPV 0 — luật dự án mới; dự án chưa mở bán, không có giá/hợp đồng đầu ra kiểm được)**.
HHS = [51,15% × CRV × (1 − CK holding) + phần khác 678 + ô tô LNST × P/E] / 431,99 triệu cp. **r = 13,50%** trong PV.
**Cơ sở dữ liệu cho khoản giảm trừ trong base — CK holding 25%:** CRV chưa trả cổ tức tiền về HHS 9T/2026 [Q3HN LCTT]; tiền NC-II chỉ lên HHS qua cổ tức CRV (2 tầng); tiền mẹ chỉ 171. Mức 25% là **(ước lượng)** — biến trọng yếu nên nằm trong lưới. Thặng dư dương trên HTK cũ có cơ sở: biên NC-II quan sát 51,9–52,2% (base dùng thặng dư 40% ⇔ biên gộp ~40%, có đệm).

| | TIÊU CỰC (w 0,30) | CƠ SỞ (w 0,50) | TÍCH CỰC (w 0,20) |
|---|---|---|---|
| Biên ròng backlog / thặng dư HTK cũ | 30% / 15% | 33,5% / 40% | 36% / 55% |
| Ô tô LNST × P/E | 25 × 5 | 35 × 6 | 50 × 8 |
| CK holding | 35% | 25% | 15% |
| **Giá trị** | **8.814** | **10.963** | **13.201** |

Kỳ vọng **10.766** trước CK ⇒ **10.611** sau CK. Độ nhạy I.14 (base NPV 0): thặng dư −15% → −105 đ/cp; +40% → +281. Thặng dư BĐSĐT CRV chưa vào tâm: tối đa +726 đ/cp (cận dưới chênh sổ; lợi suất cho thuê ~2,3%).

### 6.2 Lưới P10–P90
n = 45 = 3 kịch bản (w 0,30/0,50/0,20) × dịch thặng dư HTK CRV cũ **−15/−7,5/0/+7,5/+15 pp** × dịch CK holding **−5/0/+5 pp** (đều); r cố định 13,5%; không CK quản trị. File ô `calc/grid_hhs.csv`. (Hai biến trọng yếu nhất theo DD cũ: CK holding ±5đ% ≈ ∓555, thặng dư ±15đ% ≈ ±545.)

| | P10 | P25 | P50 | P75 | P90 |
|---|---|---|---|---|---|
| TRƯỚC CK | 8.538 | — | 10.771 | — | 13.201 |
| SAU CK | **8.415** | 9.214 | **10.615** | 11.644 | **13.010** |

### 6.3 Độ nhạy r theo lãi huy động 12T (trước CK)

| Δ lãi huy động | β = 0,5 | β = 1,0 |
|---|---|---|
| −100bp | 13,00% → 10.790 (+24; +0,2%) | 12,50% → 10.815 (+49; +0,5%) |
| −50bp | 13,25% → 10.778 (+12; +0,1%) | 13,00% → 10.790 (+24; +0,2%) |
| +50bp | 13,75% → 10.754 (−12; −0,1%) | 14,00% → 10.742 (−24; −0,2%) |
| +100bp | 14,00% → 10.742 (−24; −0,2%) | 14,50% → 10.719 (−47; −0,4%) |

NAV gần như không nhạy với r (PV chỉ trên backlog 1 năm và thặng dư 4 năm). Rủi ro lãi suất với HHS đi qua **cầu BĐS** (tốc độ bán, thặng dư), không qua chiết khấu — đã nằm ở trục thặng dư của lưới.

### 6.4 Đối chiếu (không vào tâm)
0,98 × BV giá gốc 11.617 (P/B VCSH mẹ của TCH) = 11.385; 0,72 × BV giá gốc (trung vị peer BQ, chưa truy nguyên) = 8.364; 51,15% × VCSH CRV riêng 31/03/26 = 8.974 (DD cũ). Cơ sở PPA của chính HHS (tham chiếu): ~11.700.

## 7. Mốc khoá trước + điều kiện đổi nhận định (HAI chiều)
Giữ M1–M7 (DD 01/11 §8):
- **M1 BCTC 2026 kiểm toán (03/2027)** — mốc quan trọng nhất vì Q3 chưa soát xét. Lên: LNST mẹ 9T không bị điều chỉnh >10%, kiểm toán sạch. Xuống: điều chỉnh >10% (như 6T −34%) hoặc ngoại trừ/nhấn mạnh về PPA/HTK ⇒ tâm −1.000 đến −1.500 đ (ước lượng) + nâng WARNING.
- **M3 cổ tức tiền CRV về HHS (31/12/2027):** ≥ 500 tỷ toàn CRV ⇒ CK holding −5đ% ⇒ +~555 đ; không có ⇒ giữ/nâng CK holding.
- **M2 mảng xe Q4/26:** DT ≥ 200 và HTK < 450 (lên) / DT < 150 và HTK > 600 hoặc trích DP giảm giá (xuống).
- **M4 danh tính người bán HHS Capital** và **M7 QĐ phạt/khởi tố mới, toàn văn KL 08:** chỉ đổi **mức WARNING** và độ nhạy CK quản trị (−538…−1.615), không đổi base.
- **I.14:** có giá mở bán/hợp đồng đầu ra kiểm được ⇒ chuyển phần thặng dư I.14 vào base (độ nhạy +281 ở 40%); trễ tiến độ có tín hiệu/giấy phép vướng ⇒ kịch bản tiêu cực riêng.
- Nhãn sang DƯỚI vùng nếu giá < 8.415; TRÊN vùng nếu > 13.010.

## 8. Phụ lục — ĐỔI gì so với DD cũ (01/11) và vì sao

| Mục | Cũ (01/11 v2) | Mới (05/11) | Lý do |
|---|---|---|---|
| Ke / r | 12,85% | **13,50%** | luật 03/11; tác động chỉ **−34** đ/cp |
| I.14 | thặng dư như HTK cũ (15/40/55%) | giá sổ, thặng dư 0 | luật dự án mới; **−236** |
| CK quản trị | 15/10/5% theo kịch bản trong base | **bỏ** (chỉ độ nhạy) | pháp lý/quản trị = WARNING; **+1.077** |
| CK thanh khoản | không có | 1,44% @5 tỷ (ADV 16,2 tỷ) | luật 03/11; **−155** |
| Tâm | ~9.950 (tái lập 9.959) | **10.611** | cầu nối: 9.959 → 9.925 → 9.689 → 10.766 → 10.611; **lệch +6,6% (< 10%)** |
| Vùng | ~7.600–13.000 (min–max kịch bản) | P10–P90 lưới n=45: 8.415–13.010 | định nghĩa chuẩn hoá liên mã |
| Nhãn | TRONG vùng, nửa dưới (giá 9.450, −5% vs tâm) | TRONG vùng, nửa dưới (giá 9.550, −10%) | |

## 9. Lỗ hổng mở
I.14 1.329 tỷ giả định nằm trong HTK CRV còn lại 7.338,8 (tham số DD TCH, chưa đối chiếu dòng); CK holding 25% là ước lượng; danh tính người bán HHS Capital (G4/G11); thặng dư BĐSĐT CRV chưa vào tâm; chưa quét tin 01–04/11/2026. Chưa qua fundamental-skeptic vòng này.
