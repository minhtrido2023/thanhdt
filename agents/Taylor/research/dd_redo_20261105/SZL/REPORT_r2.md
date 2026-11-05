# DD REDO VÒNG 2 — SZL (Sonadezi Long Thành, HOSE) · job `Taylor_20261105_020021` · 05/11/2026

> Chỉ NGHIÊN CỨU, không khuyến nghị. Áp `../STANDARD_r2.md`. Số: `calc/model_r2.py` → `calc/model_r2_out.txt/json`, `SUMMARY.json` (r1: `SUMMARY_r1.json`), `calc/LOCK_r2_md5.txt`; chạy 2 lần trùng byte.
> BCTC Q3/2026 gốc `src/Q3_2026_hopnhat.pdf` (B01a-DN, scan). **Vòng 2 đọc thêm thuyết minh** (ảnh trang PDF 22–27 = in tr.18–24): TM8 XDCB, TM11 chi phí trả trước, TM13 phải trả NB, TM16 chi phí phải trả, TM17 phải trả khác, TM19 DT chưa thực hiện, TM20 vay. Giá **27.650 đ** (04/11/2026); SZC/SZB theo BQ 04/11. Đơn vị tỷ đồng.

## 0. Kết luận (mức KẾT CỤC, sau CK thanh khoản 5 tỷ)

| | đ/cp |
|---|---|
| **Tâm** = kỳ vọng lưới (trước / sau CK) | 33.796 / **32.391** |
| **P50** kết cục (sau CK) | 32.162 |
| Giá trị tại tham số trung tâm (N0, g 3%, r 13,5%, phi tiền mặt 10%; sau CK) | 31.858 (27 năm) / 33.481 (vĩnh viễn) |
| **P10 / P90** kết cục (sau CK) | **28.966 / 36.075** |
| n kết cục · % trọng số dưới giá · thấp nhất | 270 · **3,4%** · 25.175 |
| Giá 27.650 so tâm | **−14,6% ⇒ DƯỚI vùng (<P10)** |

**NHÃN ĐỔI so vòng 1 (TRONG → DƯỚI) — do SỬA LỖI MÔ HÌNH, KHÔNG do đổi định nghĩa vùng** (vẫn P10–P90):
1. **XDCB 407,0 cộng theo giá vốn (+8.445 đ/cp)**. Vòng 1 viết "Long Phước NPV 0, không cộng không trừ" nhưng thực tế KHÔNG cộng tài sản trong khi nợ vay tài trợ dự án đã nằm trong nợ ròng ⇒ NPV ngầm định = −407 (vi phạm điều 3). TM8: CCN Long Phước 344,7 + nhà xưởng cho thuê 39,2 + TĐC Tam An 14,2 + Châu Đức 6,1 + khác; phải trả người bán chỉ 16,7 ⇒ không có nợ xây dựng lớn đối ứng.
2. **Trừ nợ theo sổ vòng 1 bỏ sót (−4.183 đ/cp)**: ký quỹ khách thuê 157,4 (TM17: NH 10,4 + DH 147,0) + trích bổ sung tiền thuê đất KCN Long Thành 44,3 (TM16, không đổi từ 01/01).
3. **Trục thời hạn mới**: dòng tiền lõi đến 2053 (27 năm) / vĩnh viễn, trọng số 3/4–1/4 — TM17 cho cơ sở dữ liệu mốc 2053 (NQ ĐHĐCĐ 76/2020 phân bổ LN giữ lại 5,85 tỷ/năm 2019–2053); vòng 1 dùng Gordon vĩnh viễn dù tự nêu thời hạn thuê ~27 năm (trục chỉ lệch xuống bị bỏ — điều 2).
Tâm vòng 1 29.900 ⇒ vòng 2 **+8,3%** (vùng cũ 26/10: 27.200 ⇒ +19,1%).
**Độ bền nhãn** (song song, §1): chiết khấu holdco 25% lên SZC/SZB ⇒ TRONG vùng (tâm 30.168, giá −8,3%); holdco 10% ⇒ vẫn DƯỚI. Bỏ XDCB như vòng 1 ⇒ TRONG (tâm 24.297, giá +13,8%). **Nhãn DƯỚI phụ thuộc hoàn toàn vào việc ghi XDCB theo giá vốn** — đó là luật 03/11, nhưng là điểm phản biện nên tấn công trước tiên.
Ba con số: tâm 32.391 ≈ P50 32.162; giá trị tại tham số trung tâm 31.858/33.481 theo nhánh thời hạn. Nhánh vĩnh viễn (trọng số 0,25) kéo P90; P10 không do nhánh trọng số nhỏ.

## 1. Lưới (điều 1–2)
5 trục, 270 ô, mỗi ô 1 kết cục tất định; phân vị `_shared/wpct.py`.
- **Có**: LN lõi N0 {−12; −6; 0; +6; +12}% quanh 131,1 (0,1/0,2/0,4/0,2/0,1) [UL] · g {2; 3; 4}% · r {12,5; 13,5; 14,5}% · LN phi tiền mặt {20; 10; 0}% [UL; cận trên 17% = DT chưa thực hiện 762,2/27 năm × 0,8] (mỗi trục 1/4–1/2–1/4) · thời hạn {27 năm; vĩnh viễn} (3/4–1/4) [UL trọng số].
- **Loại + song song (sau CK)**:

| Trục/khoản | Lý do loại | Bản song song |
|---|---|---|
| CK holdco trên SZC/SZB | không có dữ liệu (SZC thanh khoản ~7,8 tỷ/phiên) | 10%: tâm 31.502, P10 28.077 (DƯỚI) · 25%: tâm 30.168, P10 26.743 (TRONG) |
| Thanh tra SNZ lan sang SZL | chưa có quyết định nêu tên SZL | WARNING |
| Long Phước NPV ≠ 0 | luật 03/11 | — |
| (đối chiếu) bỏ XDCB = cách r1 | — | tâm 24.297, P10/P90 20.872/27.981 |
| (đối chiếu) bỏ nợ khác | — | tâm 36.401 |
| (đối chiếu) chỉ vĩnh viễn | — | tâm 33.691 |
| (đối chiếu) tái lập r1 | — | tâm 29.607 |

## 2. Khoản lệch sổ sách/NPV 0 trong BASE (điều 3)
| Khoản | đ/cp | Cơ sở dữ liệu | Nguồn |
|---|---|---|---|
| XDCB 407,0 theo giá vốn — **MỚI** | +8.445 | TM8a; luật dự án mới 03/11 | BCTC in tr.18 |
| Ký quỹ 157,4 + trích thuê đất 44,3 — **MỚI** | −4.183 | TM16–17 | BCTC in tr.23 |
| Thuế TNDN 20% lãi vốn chưa thực hiện SZC/SZB | −843 | giá sổ (mã 260 + cơ cấu ABS 30/03/2026) + thuế suất | BCTC + ABS |
| Cổ tức phải trả 70,4 vào nợ | −1.460 | mã 313, chi 07/10/2026 | BCTC |
| LN phi tiền mặt tâm 10% N0 | trục | DT chưa thực hiện 762,2 ÷ 27 năm (cận trên 17%); 10% = [UL] | TM19 |
Không cộng (tài sản vận hành, đã phân bổ vào chi phí trong N0): chi phí trả trước DH 280,9 (tiền thuê đất Châu Đức 147,3, Tân Đức 69,9…). Phải trả DH khác 152,0 = LN giữ lại phân bổ dần (phi tiền mặt, nằm trong trục phi tiền mặt).
Tham số tự đặt [UL]: mức/trọng số N0, phi tiền mặt, trọng số thời hạn 3/4–1/4, β=1.

## 3. Cross-check Gordon/ROE (điều 10; g 3%, phi tiền mặt 10%, vĩnh viễn)
- Vốn hoá LNST gồm cổ tức SZC/SZB (không cộng cổ phần riêng): **31.437** · ROE 22,5%.
- LN lõi + cổ phần theo thị giá: **34.935** · ROE lõi (trừ đầu tư, XDCB) 33,9%.
Cả hai > giá 27.650.

## 4. Thanh khoản (điều 6)
| Cỡ | ADV250 0,46 tỷ (σ 1,26%; 5 phiên KL=0) | ADV60 0,61 tỷ (σ 1,23%) |
|---|---|---|
| 10 / 20 / 40 tr (sleeve) | 0,19% / 0,26% / **0,37%** (40 tr = 8,7% ADV, trong vùng) | 0,16% / 0,22% / 0,31% |
| **5 tỷ (tham chiếu nhãn)** | **4,2%** — Q/ADV 1.084%, **NGOÀI xa vùng hiệu chỉnh**, 54–108 phiên | 3,5% (821%) |
Nhãn ở cỡ 5 tỷ = DƯỚI; ở cỡ sleeve 40 tr cũng DƯỚI (tâm 33.670, giá −17,9%). 40 tr ≈ 9% ADV ⇒ chia ≥2 phiên.

## 5. Độ nhạy r (tâm trước CK): β=1: −100bp +5,8% · −50bp +2,8% · +50bp −2,6% · +100bp −5,0%; β=0,5: +2,8/+1,4/−1,3/−2,6%.

## 6. ⚠️ WARNING pháp lý/quản trị (mang đủ cờ)
1. **SNZ (mẹ 52,7%)**: Trưởng BKS bị khởi tố, tạm giam (CBTT ~27–28/05/2026; nhadautu, vneconomy) — cá nhân ở công ty mẹ, chưa chạm pháp nhân/tài sản SZL.
2. Luân chuyển tiền trong hệ sinh thái Sonadezi (ABS); sở hữu chéo (SZL nắm SZC/SZB; SNZ nắm SZL); trả trước người bán NH 14,2 → 72,6; trả trước DH dự án Sonadezi Bình Thuận. **Mới đọc**: vay từ bên liên quan còn 23,9 (TM20, giảm từ 44,7); ký quỹ nhận từ BLQ 0,23 (TM17).
3. Đồng Nai: sai phạm quản lý xăng dầu/đất đai (báo chí 2026) — SZL có mảng xăng dầu, chưa bị nêu tên.
4. Trích bổ sung tiền thuê đất KCN Long Thành 44,3 treo từ đầu năm (TM16) — nghĩa vụ đất đai chưa quyết toán (đã trừ ở base).
5. Free float < 25%, ADV 0,46 tỷ.
6. "Chưa thấy khởi tố/xử phạt chạm pháp nhân SZL": nguồn = DD 26/10/2026 (nhadautu, vneconomy, doanhnghiephoinhap) + web search 05/11/2026 (baophapluat, diendandoanhnghiep) — không có kết quả mới; không thấy NQ HĐQT/ĐHĐCĐ mới. CCN Long Phước dự kiến hoạt động cuối 2026 [baophapluat].

## 8. Mốc đổi nhận định (hai chiều) + HARD ABANDON
| Mốc | Ngày chấm | Lên | Xuống |
|---|---|---|---|
| BCTC Q4/2026 | 31/01/2027 | LN lõi Q4 ≥36 + DT chưa thực hiện tăng | LN lõi <30 / QLDN +30% |
| Long Phước cho thuê | 30/06/2027 | hợp đồng thuê/đặt cọc có giá ⇒ NPV dương có cơ sở | đội vốn >920 có số / chậm sau 2027 / D/E vay >0,8 ⇒ kịch bản tiêu cực có xác suất (tấn công trực tiếp +8.445 đ) |
| Quyết toán tiền thuê đất KCN Long Thành | khi có | hoàn nhập 44,3 | truy thu > 44,3 |
| Cổ tức SZC/SZB 2026 | 2027 | giữ/tăng | cắt ⇒ cổ phần niêm yết (447 tỷ sau thuế) giảm |
| Thanh tra SNZ | — | — | kết luận nêu tên SZL ⇒ nâng WARNING |
**HARD ABANDON**: (a) kết luận thanh tra/khởi tố chạm pháp nhân SZL hoặc tài sản KCN; (b) SZL cho bên liên quan vay/trả trước không bảo đảm > 100 tỷ; (c) Long Phước bị thu hồi/đình chỉ. Sleeve 10–40 tr ⇒ không tranche (chia ≥2 phiên vì 9% ADV).
**Sleeve fear-buy §2.5: KHÔNG đủ điều kiện** — không có khủng hoảng ở doanh nghiệp; "dưới vùng" đến từ sửa sổ sách + thanh khoản kém, không từ sự kiện sợ hãi.

## 9. Mở
Mốc 2053 chưa đối chiếu giấy phép thuê đất · tiến độ/tổng mức Long Phước · đối tượng trả trước 72,6 · LCTT chưa đọc · bẫy BQ OShares/BVPS restate. Chưa qua fundamental-skeptic.

## Phụ lục — đổi so với vòng 1
| Mục | Vòng 1 | Vòng 2 | Lý do |
|---|---|---|---|
| XDCB 407 | "NPV 0" nhưng không cộng | cộng giá vốn (+8.445 đ) | điều 3 |
| Ký quỹ + trích thuê đất 201,7 | bỏ sót | trừ (−4.183 đ) | điều 3 (đọc TM16–17) |
| Thời hạn | vĩnh viễn | 27 năm / vĩnh viễn 3/4–1/4 | điều 2; cơ sở TM17 |
| Tâm | 3 kịch bản | kỳ vọng lưới 270 ô | điều 4 |
| Nhãn | TRONG (nửa dưới) | **DƯỚI** | sửa lỗi mô hình, không đổi định nghĩa vùng |
