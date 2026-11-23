# DD SZL (Sonadezi Long Thành, HOSE) — REV5 (vòng 3) · 23/11/2026 · job `Taylor_20261123_100922`

Bản này xử lý skeptic DD_GENERAL r3 (`skeptic/r3.json`, REFUTED medium) chạy trên `REPORT_rev4b.md`. User duyệt vòng 3 lúc 23/11 17:03 ICT. `REPORT_rev4b.md`, `REPORT_rev4.md`, `REPORT_r3c.md` giữ nguyên, không sửa.

**Nguồn**
- BCTC Q3/2026 hợp nhất (`rev4/restored/src/Q3_2026_hopnhat.pdf`, md5 `6ef6a005…`) và soát xét H1/2026 (`rev4/restored/src/H1_2026_soatxet.pdf`, md5 `c36ddb57…`), khôi phục từ git `fc5bd02d9`. Ảnh trang ở `rev4/png/`.
- Mô hình `rev5/calc/model_rev5.py`, giả định khoá ở `rev5/calc/assumptions_rev5.json`.
- `rev5/calc/LOCK_rev5_prerun.txt` ghi **trước** lần chạy đầu (17:12:34 ICT). Hai lần chạy trùng byte, `model_rev5_out.txt` md5 `f9f1a8a2`.

**Mù giá.** Giá 27.700 (06/11) đã biết từ r3/r3c. Rev5 **không truy vấn giá mới**. File giá cũ chỉ dùng cho chiết khấu thanh khoản (CK) và gán nhãn. Không giả định nào được chọn theo giá.

## 0. Kết luận

| | rev4b (skeptic r3 REFUTED) | **rev5 base** |
|---|---|---|
| Tâm, cỡ 5 tỷ (CK 4,12%) | 25.852 | **26.183** |
| P10 / P50 / P90, cỡ 5 tỷ | 22.290 / 25.840 / 29.534 | **22.740 / 26.153 / 29.700** |
| Tâm, cỡ 40 tr (CK 0,37%) | 26.862 | **27.207** |
| P10 / P50 / P90, cỡ 40 tr | 23.162 / 26.850 / 30.688 | **23.629 / 27.175 / 30.861** |
| % trọng số kết cục dưới giá 27.700 (5 tỷ / 40 tr) | 74,9% / 60,8% | 70,9% / 57,6% |
| Nhãn (5 tỷ tham chiếu / 40 tr hành động) | TRONG / TRONG | **TRONG / TRONG**. Giá cao hơn tâm 5,8% (5 tỷ) / 1,8% (40 tr) |

**Cầu nối rev4b → rev5** (`model_rev5_out.txt`), tổng **+331**:

| Bước | Δ tâm 5 tỷ | Tâm |
|---|---|---|
| rev4b (control, tái lập) | | 25.852 |
| + bỏ khoản trừ NQ 76 (không qua P&L) | +708 | 26.559 |
| + tỷ lệ trích KTPL 2026 = 20,0% | −1.766 | 24.793 |
| + đất thuê trả trước KCN Tân Đức theo sổ sách 69,9 tỷ | +1.391 | **26.183** |

- **Control.** Đặt k = 11,215%, trừ NQ 76 và Tân Đức = 0 thì tái lập đúng tâm rev4b 25.852 (cỡ 40 tr: 26.862). P10/P90 lệch 4–6 đồng (22.296 / 29.530) do bỏ trục g làm đổi số điểm lưới khi nội suy phân vị.
- Hai bước đầu khớp con số skeptic r3 tính lại (26.559 và 24.793; cỡ 40 tr 25.762). Δ KTPL là −1.766, khác −1.688 của skeptic vì skeptic tính bước này trên nền rev4b còn trừ NQ 76.
- **Luật sổ (giá < tâm − 15%) KHÔNG đạt.** Không đủ điều kiện sleeve fear-buy §2.5.
- Trước CK, tâm cỡ 5 tỷ là 27.308.

## 1. Đính chính so với rev4b (từng hạng mục skeptic r3)

| # | Hạng mục skeptic r3 | Loại | Xử lý ở rev5 | Δ tâm 5 tỷ |
|---|---|---|---|---|
| r3-1 | **Killer.** KTPL 2026 trích 20%, mô hình vẫn dùng 11,215% | (a) | TM21e tr.26 (png q3_p30): trích quỹ KTPL 13.979.344.350 / LNST 69.896.721.750 = **20,0%**. Q3/2025 trên cùng bảng: 3.839 / 34.232 = 11,2%. Tỷ lệ 2026 là cơ sở độc lập mới nhất nên **base k = 20%**. Áp cả cho phần lãi holdco (như các rev trước). Tỷ lệ các năm sau chưa công bố ⇒ độ nhạy 11,215% (+1.766) và 25% (−1.005) | **−1.766** |
| r3-2 | NQ 76 5,846 tỷ/năm không đi qua P&L; khoản trừ −708 là điều chỉnh giảm không có cơ sở | (a) | Bảng biến động vốn chủ tr.25 (png q3_p29): dòng "Phân bổ lợi nhuận giữ lại để chia cổ tức năm 2026" 5.845.686.000 ghi thẳng vào LNST chưa phân phối. Thu nhập khác 9T chỉ 1,578 ⇒ khoản này không nằm trong N0. **Bỏ khoản trừ**, N0_9M = 131,08 (bằng r3c). Bỏ độ nhạy "NQ 76 không chịu thuế". Số dư 151,988 không bị tính là nợ trong mô hình (đúng: tiền đã thu, bản chất là LN giữ lại hoãn) | **+708** |
| r3-3 | Cơ sở 48,199 tr cp trình bày sai ("phát hành trong Q3") | (a) | TM21d tr.26: tại 30/09 có 29.114.840 cp đăng ký, **28.352.340 cp lưu hành** (762.500 cp quỹ). Bảng vốn chủ tr.25: "vốn khác của chủ sở hữu" 198.465.440.000 = **19.846.544 cp thưởng × 10.000**, tỷ lệ 70%, **chưa đăng ký tăng vốn** tại 30/09. Mẫu số định giá = **cơ sở sau thưởng 28,352340 + 19,846544 = 48,198884 tr** (đúng số rev4b; 19,8465 của skeptic là làm tròn). Ngày đăng ký cuối cùng **17/09/2026** (báo chí: [cafef](https://cafef.vn/mot-cong-ty-sap-tra-co-tuc-ty-le-70-188260812231045122.chn), [stockbiz](https://stockbiz.vn/tin-tuc/szl-mot-doanh-nghiep-sap-lan-chot-co-tuc-tong-ty-le-95/41625178)), khớp việc bút toán vốn khác đã ghi trước 30/09 ⇒ GDKHQ trước 06/11 ⇒ giá tham chiếu 27.700 cùng cơ sở sau thưởng. Ngày GDKHQ chính xác từ HOSE/VSD: **không kiểm chứng được** trong phiên; nếu sai (giá 06/11 là giá trước quyền) thì phải so với 27.700/1,70. Mẫu số EPS trong thuyết minh (27,985 tr) là bình quân trước thưởng, không dùng cho định giá | 0 |
| r3-4 | Trục g không có tác dụng (val() không dùng g), lưới lặp ba lần | (a) | **Bỏ trục g.** Lưới n = 1.080 (trước 3.240). Tâm không đổi, phân vị lệch ≤ 6 đồng | 0 |
| r3-5 | Chi phí trả trước thuê đất Châu Đức 147,3 + Tân Đức 69,9 tỷ chưa bàn | (a) Tân Đức / (a) Châu Đức | TM11 tr.20 (png q3_p24) và TM VI.1–2 tr.27 (png q3_p31). **Châu Đức** (dài hạn 147,306 + ngắn hạn 6,895): đang sinh doanh thu (cho thuê nhà xưởng KCN Châu Đức 4,544 tỷ Q3/2026) và được phân bổ vào giá vốn. Giá trị đã nằm trong N0 và trục BĐS ĐT mới ⇒ **không cộng riêng**, để tránh đếm hai lần. **Tân Đức** 69,900 (đầu năm 71,084, phân bổ −1,185 trong 9T): **không có dòng doanh thu hay giá vốn Tân Đức** ⇒ quỹ đất chưa khai thác ⇒ theo luật "dự án mới base = sổ sách / NPV 0", **cộng sổ sách 69,9**. Chi phí phân bổ khoảng 1,58 tỷ/năm vẫn nằm trong N0, không cộng lại (thận trọng). Độ nhạy Tân Đức = 0: −1.391 | **+1.391** |
| r3-6 | Ý kiến kiểm toán FY2025 vắng | (c) | **Không kiểm chứng được.** Đã tìm web 23/11: ĐHĐCĐ 2026 thông qua BCTC kiểm toán 2025 và dùng LNST chưa phân phối 31/12/2025 theo BCTC kiểm toán làm nguồn trả cổ tức (báo chí). Không có văn bản ý kiến kiểm toán trong src. Gần nhất: soát xét H1/2026 RSM số 16/2026/BCSX-RSMHCM ngày 10/08/2026, **chấp nhận toàn phần**. Đề xuất sổ đặt `audited_fy_missing = true`. Ảnh hưởng ước lượng: nếu FY2025 có ngoại trừ trọng yếu thì nằm ngoài lưới, chuyển sang mốc đổi nhận định | — |
| r3-7 | Tổng mức Long Phước 920 chỉ từ báo chí | (c) | **Không kiểm chứng được** (không có NQ HĐQT/ĐHĐCĐ trong src). Giữ NPV 0 và độ nhạy vượt vốn 20% phần còn lại: **−2.041** (nhãn 40 tr vẫn TRONG) | 0 |
| r3-8 | Capex duy trì = 1,0× KH chưa có bằng chứng; BQ CF đầu tư 140–314 tỷ/năm so với LN ~100 | (b) | `szl_cf_hist.csv` (BQ): CF đầu tư 2019–24 gồm cả mở rộng (nhà xưởng, Long Phước, BĐS ĐT), BCTC không tách duy trì/mở rộng ⇒ **không có cơ sở độc lập để đổi base**. Giữ trục ±45 tỷ/năm và ngưỡng nhãn (mục 2); đây vẫn là trục rộng nhất | 0 |

## 2. Độ nhạy (mỗi dòng đổi một trục so với base rev5)

| Biến thể | Tâm 5 tỷ | Δ | Nhãn 5 tỷ / 40 tr |
|---|---|---|---|
| **Base rev5** | **26.183** | 0 | TRONG / TRONG |
| KTPL 11,215% (tỷ lệ 2025) | 27.950 | +1.766 | TRONG / TRONG |
| KTPL 25% | 25.178 | −1.005 | TRONG / TRONG |
| Đất Tân Đức = 0 | 24.793 | −1.391 | TRONG / TRONG |
| NQ 76 trừ như rev4b (sai theo bảng vốn chủ) | 25.555 | −629 | TRONG / TRONG |
| N0 chỉ theo 9T | 27.571 | +1.388 | TRONG / TRONG |
| N0 chỉ theo biên chu kỳ | 24.796 | −1.388 | TRÊN / TRONG |
| BĐS ĐT mới = 0 | 24.476 | −1.707 | TRONG / TRONG |
| BĐS ĐT mới = đủ giá vốn | 27.796 | +1.612 | TRONG / TRONG |
| Ký quỹ dài hạn theo mệnh giá | 24.934 | −1.249 | TRONG / TRONG |
| Ký quỹ dài hạn theo PV@lãi huy động | 27.433 | +1.249 | TRONG / TRONG |
| Thuê đất +25% / +50% / ×2 | 25.788 / 25.392 / 24.600 | −396 / −792 / −1.583 | TRONG / TRONG |
| Thuê đất bỏ ×4/3 | 26.553 | +369 | TRONG / TRONG |
| Long Phước vượt vốn 20% | 24.142 | −2.041 | TRÊN / TRONG |
| Holdco 10% / 25% | 25.360 / 24.125 | −823 / −2.058 | TRONG, TRÊN / TRONG |
| Capex duy trì 0,5× KH (+45/năm) | 32.666 | +6.482 | DƯỚI / **DƯỚI** |
| Capex duy trì 1,5× KH (−45/năm) | 19.701 | −6.482 | TRÊN / **TRÊN** |
| Chỉ 27 năm / chỉ vĩnh viễn | 26.082 / 26.488 | −102 / +305 | TRONG / TRONG |

**Ngưỡng nhãn ở cỡ 40 tr (hành động):**
- **Sang TRÊN** khi có một trong các điều kiện: dòng tiền thêm < −21,2 tỷ/năm (≈ capex duy trì ≥ 1,24× KH 90/năm); holdco > 37,0%; KTPL > 33,9%.
- **Sang DƯỚI** khi dòng tiền thêm > +27,7 tỷ/năm (≈ capex duy trì ≤ 0,69× KH).

## 3. V1 / V2-D4 — chi phí vốn

- **r = 13,50%** = 13,5% + 1,0 × (7,40% − 7,40%); lãi huy động 12T hiệu dụng (`deposit_rate_vn`) tại 06/11 và tại neo 03/11 đều 7,40%.
- Độ nhạy lãi huy động (β = 1): −100bp ⇒ tâm **+3,3%**; +100bp ⇒ **−2,9%**.
- Để tâm cỡ 5 tỷ bằng giá 27.700 cần r ≈ **11,82%**.

## 4. V3 — thanh khoản

- CK = σ√(Q/ADV250), ADV trung vị 250 phiên đến 06/11 (như r3c/rev4b).
- Cỡ 5 tỷ: CK **4,12%** (Q/ADV250 ngoài vùng hiệu chỉnh, chỉ tham chiếu). Cỡ 40 tr: CK **0,37%**, chia ≥ 2 phiên.
- Tâm cỡ 5 tỷ trước CK 27.308; nhãn tính sau CK.
- V8 (2–4% NAV/mã) chỉ tham chiếu; DD này không đề xuất lệnh.

## 5. V5 — 5F

Tái dùng `ADDENDUM_5F.md` (lập 11/2026, chưa quá 12 tháng): **NARROW / LOCATION**. Rủi ro số 1: quỹ đất KCN Long Thành gần cạn và đồng hồ 2053. Quỹ đất thuê Tân Đức (chưa khai thác) là đường mở rộng; base chỉ tính theo sổ sách.

## 6. V6

**Không áp dụng.** Chuỗi DD SZL chưa dựng hai nền V_ngắn / V_dài.

## 7. Mốc đổi nhận định (hai chiều) và HARD ABANDON

| Mốc | Ngày | Lên (→ DƯỚI) | Xuống (→ TRÊN) |
|---|---|---|---|
| BCTC Q4/2026 | 31/01/2027 | GPM cả năm ≥ 38% ⇒ dồn N0 về mức 9T (+1.388) | GPM Q4 < 34% ⇒ dồn về biên chu kỳ (−1.388) |
| BCTC kiểm toán 2026 + LCTT | 31/03/2027 | Capex duy trì ≤ 0,69× KH, có số | Capex duy trì ≥ 1,24× KH; ý kiến kiểm toán ngoại trừ |
| NQ ĐHĐCĐ 2027 phân phối LN | 04/2027 | KTPL về ~11% (+1.766) | KTPL > 33,9% |
| Tân Đức | khi có | Hợp đồng cho thuê có giá | Trả lại đất / xoá sổ (−1.391) |
| Điều khoản ký quỹ khách thuê | khi có | Hoàn trả cuối hợp đồng/2053 ⇒ PV (+1.249) | Hoàn trả theo yêu cầu ⇒ mệnh giá (−1.249) |
| Long Phước | 30/06/2027 | Hợp đồng thuê có giá | Vượt vốn so với 920, có số |
| Lãi huy động 12T | hằng tháng | −100bp ⇒ +3,3% | +100bp ⇒ −2,9% |
| Thanh tra SNZ / thuế | — | — | Kết luận nêu tên SZL ⇒ nâng mức WARNING |

**Pháp lý — WARNING, không vào base:** vụ khởi tố Trưởng BKS thuộc SNZ (công ty mẹ); quyết định truy thu/phạt thuế SZL gần 14 tỷ (≈ 290 đ/cp, ước lượng), chưa kiểm chứng đã hạch toán hay chưa.

**HARD ABANDON** (giữ như rev4b): (a) thanh tra/khởi tố chạm tới pháp nhân SZL hoặc tài sản KCN; (b) cho bên liên quan vay hoặc trả trước không bảo đảm > 100 tỷ; (c) Long Phước bị thu hồi hoặc đình chỉ.

## 8. Còn mở (không kiểm chứng được trong phiên)

- Ý kiến kiểm toán FY2025 (`audited_fy_missing = true`).
- Ngày GDKHQ chính xác của cổ phiếu thưởng 70% (ĐKCC 17/09/2026 theo báo chí).
- Tổng mức đầu tư Long Phước 920.
- Tỷ lệ KTPL các năm sau 2026.
- Điều khoản hoàn trả ký quỹ; giấy phép đất 2053; đơn giá thuê đất mới; khoản truy thu thuế ~14 tỷ.
- Tách capex duy trì / mở rộng (trục rộng nhất ±6.482).
- DC 78,7 (phần LN BĐS ĐT mới đã nằm trong N0) là ước lượng.
- `bin/dd_assumptions_lint.py`: file giả định chưa theo schema `dd_assumptions_v1` (21 cảnh báo, rc=0, không strict) vì kế thừa khung r3/rev4b.

Không đặt lệnh, không sửa `kb/dd_price_zones.json`, không gửi email.

## Tái lập

```bash
cd SZL/rev5/calc
/home/trido/thanhdt/wc_venv/bin/python -I model_rev5.py > run1.txt; /home/trido/thanhdt/wc_venv/bin/python -I model_rev5.py > run2.txt; cmp run1.txt run2.txt   # = model_rev5_out.txt (md5 f9f1a8a2)
md5sum -c <(grep -v '^#' LOCK_rev5_prerun.txt)
```
