# DD REDO VÒNG 3b — SZL (Sonadezi Long Thành, HOSE) · job `Taylor_20261108_175123` · 09/11/2026

Đầu vào: `REPORT_r3.md` + `calc_r3/` (giữ nguyên mọi đính chính r3), cộng 2 đề nghị cuối của fundamental-skeptic **user đã duyệt**: (A) RONIC = Ke ở base; (B) trừ quỹ KTPL cả trên thu nhập từ cổ phần SZC/SZB. Số trong file này lấy từ `calc_r3b/model_r3b_out.txt` (chạy 2 lần trùng byte, md5 `47373344`). LOCK ghi **trước** lần chạy đầu, file riêng có timestamp: `calc_r3b/LOCK_r3b_prerun.txt` (2026-11-09T00:53:59+07:00, chỉ-đọc; model không ghi LOCK). Minh bạch: giá 27.700 đã biết từ r3; file giá giữ nguyên của r3, không truy vấn lại.

## 0. Kết luận

| | r3 | **r3b** |
|---|---|---|
| Tâm, cỡ 5 tỷ (CK 4,12%) | 29.257 | **24.529** (−16,2%) |
| P10 / P50 / P90, 5 tỷ | 26.209 / 28.963 / 32.706 | **22.301 / 24.372 / 27.074** |
| Nhãn 5 tỷ (tham chiếu) | TRONG | **TRÊN vùng** (giá cao hơn P90 2,3%; 95,3% trọng số dưới giá) |
| Tâm, cỡ sleeve 40 tr (CK 0,37%) | 30.401 | **25.488** |
| P10 / P50 / P90, 40 tr | 27.234 / 30.095 / 33.984 | **23.173 / 25.325 / 28.133** |
| **Nhãn 40 tr (có thể hành động)** | TRONG | **TRONG, sát cạnh trên** (giá thấp hơn P90 1,5%; 87,2% dưới giá) |
| Giá | 27.700 (06/11, BQ) | 27.700 |

- Nhãn hành động = cỡ sleeve 40 tr (Q/ADV250 8,7%, trong vùng hiệu chỉnh). Cỡ 5 tỷ là 1.084% ADV250 — **ngoài vùng hiệu chỉnh** của CK √(Q/ADV), chỉ để tham chiếu.
- Giá 27.700 cao hơn tâm 12,9% (5 tỷ) / 8,7% (40 tr). Thị trường đang trả cho tăng trưởng mà base r3b cho là không tạo giá trị.
- **Số skeptic khớp.** A: −3.733 (đúng). B: skeptic ước −624…−1.248, calc −995 trên SZC/SZB. Lý do lệch: con số "~559 tỷ" của skeptic = cổ phần SZC/SZB ròng 446,1 + chưa niêm yết 113,25. Áp B lên cả hai ⇒ tâm **24.276**, P90 5 tỷ **26.822**, P90 40 tr **27.870** — trùng từng số với skeptic. Nhãn không đổi giữa hai cách.

## 1. Cầu nối r3 → A → A+B (tâm sau CK 5 tỷ)

| Bước | Tâm 5 tỷ | Δ | P10–P90 5 tỷ | Nhãn 5 tỷ | Tâm 40 tr | P10–P90 40 tr | Nhãn 40 tr |
|---|---|---|---|---|---|---|---|
| r3 (control, tái lập khớp) | 29.257 | — | 26.209–32.706 | TRONG | 30.401 | 27.234–33.984 | TRONG |
| + A: RONIC = Ke | 25.524 | −3.733 | 23.296–28.070 | TRONG | 26.522 | 24.207–29.167 | TRONG |
| + B: KTPL 11,2% trên cổ phần SZC/SZB | **24.529** | −995 | 22.301–27.074 | **TRÊN** | **25.488** | 23.173–28.133 | **TRONG** |

**A.** Vĩnh viễn: cf/r. Nhánh 27 năm: annuity không tăng trưởng cf·(1−(1+r)^−27)/r (công thức đã sửa ở ADDENDUM_5F r3, không nhân (1−g/r)). Trục g không còn tác dụng; giữ trọng số để lưới vẫn n=270. Cơ sở: moat NARROW/LOCATION không bền; FCF cộng dồn 2019–9T/26 −333 tỷ; capex 9T 309,4 vs khấu hao 67,5 ⇒ tăng trưởng đang được mua bằng tái đầu tư.

**B.** Cổ phần SZC/SZB theo thị giá 06/11: 486,4 tỷ, trừ thuế lãi vốn 40,3 ⇒ ròng 446,1 tỷ (9.255 đ/cp). Tỷ lệ 11,2% (15,778 / LNST 2025 140,687) tính trên LNST đã gồm cổ tức SZC/SZB ⇒ dòng thu nhập từ cổ phần cũng bị trích: 446,1 × 11,2% = 50,0 tỷ = 1.038 đ/cp trước CK (−995 sau CK).

## 2. Độ nhạy (mỗi dòng đổi 1 trục so với r3b)

| Biến thể | Tâm 5 tỷ | Δ | P10–P90 5 tỷ | 5 tỷ | P10–P90 40 tr | 40 tr |
|---|---|---|---|---|---|---|
| **HEADLINE r3b (A+B)** | **24.529** | 0 | 22.301–27.074 | TRÊN | 23.173–28.133 | TRONG |
| Chỉ A (B tắt) | 25.524 | +995 | 23.296–28.070 | TRONG | 24.207–29.167 | TRONG |
| Chỉ B (A tắt) | 28.262 | +3.733 | 25.214–31.711 | TRONG | 26.200–32.950 | TRONG |
| B ở 50% | 25.027 | +498 | 22.799–27.572 | TRÊN | 23.690–28.650 | TRONG |
| B cả cổ phần chưa niêm yết (= skeptic) | 24.276 | −253 | 22.048–26.822 | TRÊN | 22.910–27.870 | TRONG |
| KTPL 5% (lõi + cổ phần) | 26.254 | +1.725 | 23.995–29.000 | TRONG | 24.933–30.134 | TRONG |
| KTPL 8% (lõi + cổ phần) | 25.421 | +892 | 23.178–28.071 | TRONG | 24.083–29.168 | TRONG |
| N0 = Q3×4 (138,5) | 25.371 | +842 | 23.017–28.060 | TRONG | 23.917–29.157 | TRONG |
| N0 = 2025 năm hoá (115,3) | 22.738 | −1.791 | 20.778–24.977 | TRÊN | 21.591–25.953 | TRÊN |
| Chỉ nhánh vĩnh viễn | 24.913 | +384 | 22.442–27.443 | TRÊN | 23.319–28.516 | TRONG |
| Chỉ 27 năm | 24.401 | −128 | 22.113–26.929 | TRÊN | 22.977–27.981 | TRONG |
| Thời hạn 1/2–1/2 | 24.657 | +128 | 22.329–27.074 | TRÊN | 23.202–28.133 | TRONG |
| Holdco 10% (SZC/SZB) | 23.741 | −788 | 21.513–26.286 | TRÊN | 22.354–27.314 | TRÊN |
| Holdco 25% (SZC/SZB) | 22.559 | −1.970 | 20.331–25.105 | TRÊN | 21.126–26.086 | TRÊN |
| Holdco ngụ ý P/B SNZ/SZC 45% (cận trên thô) | 20.970 | −3.559 | 18.742–23.515 | TRÊN | 19.474–24.434 | TRÊN |
| Capex duy trì 0,5× KH (+45/năm) | 31.011 | +6.482 | 28.619–33.650 | DƯỚI | 29.738–34.965 | DƯỚI |
| Capex duy trì 1,5× KH (−45/năm) | 18.047 | −6.482 | 15.823–20.411 | TRÊN | 16.442–21.208 | TRÊN |
| + BĐS đầu tư mới 166,9 theo giá vốn | 27.849 | +3.320 | 25.621–30.394 | TRONG | 26.622–31.582 | TRONG |
| Ký quỹ DH theo PV đến 2053 | 27.356 | +2.827 | 25.110–29.903 | TRONG | 26.092–31.071 | TRONG |

- Ở cỡ 40 tr, nhãn TRONG giữ qua mọi biến thể về A/B, KTPL, thời hạn và N0 = Q3×4. Đổi sang TRÊN khi: holdco ≥ 10%, N0 = mức 2025, capex duy trì 1,5× KH. Đổi sang DƯỚI chỉ khi capex duy trì 0,5× KH.
- Trục rộng nhất vẫn là capex duy trì (±6.482), nằm ngoài lưới vì BCTC không tách capex duy trì/mở rộng.
- Vùng P10–P90 hẹp hơn r3 (≈19% tâm) vì RONIC = Ke làm trục g vô hiệu; ~1/3 giá trị vẫn cố định (cổ phần theo giá 1 ngày, XDCB, nợ). Đừng đọc là "ít bất định".

**Holdco SNZ (mục 5 dispatch).** BQ 06/11: SNZ P/B 0,658 vs SZC 1,200 / SZB 1,780 / SZL 1,703. Ngụ ý thô 1 − 0,658/1,200 = 45% là **cận trên** (SNZ còn giữ tài sản khác, không thuần là holdco các công ty niêm yết). Không có dữ liệu NAV cổ phần SNZ để tính discount thật ⇒ chỉ độ nhạy; mọi mức holdco ≥ 10% đều cho TRÊN ở cả 2 cỡ.

## 3. Giá ngụ ý (tâm 5 tỷ = 27.700)

Chỉ cần **một** điều sau đúng:
- N0 = 159,0 tỷ (KTPL 11,2%), tức 131,5 khi KTPL 0%. Mốc tham chiếu: base 131,1; Q3×4 138,5; 2025 115,3.
- KTPL ≈ 0% (−0,2%).
- r = 10,89% (base 13,50%).
- Thêm +22,0 tỷ/năm dòng tiền (vd. capex duy trì thấp hơn khấu hao ~0,75×).

Ngưỡng nhãn: P90 bằng giá khi N0 = 135,8 (cỡ 5 tỷ) / 127,9 (cỡ 40 tr). Base 131,1 nằm giữa ⇒ nhãn 40 tr đổi sang TRÊN nếu LN lõi chạy thấp hơn base 2,4%.

Độ nhạy lãi huy động (β = 1): −100bp ⇒ tâm +4,4%; +100bp ⇒ −3,9%.

## 4. Đối chiếu REPORT_r3.md:28 — skeptic 28.052 vs r3 28.507 (chênh 455)

Tái lập được trong `model_r3b.py` §4, trên cấu hình r3 (RONIC ngầm vô hạn, KTPL 5%, holdco 25%):

| Cấu hình | Tâm | vs 28.052 |
|---|---|---|
| r3: KTPL 5% trên N0 + holdco 25% chỉ SZC/SZB | 28.507 | +455 |
| + holdco 25% cả cổ phần chưa niêm yết 113,25 | 27.943 | −109 |
| + KTPL trên N0×(1−nc) (quy ước skeptic) | 28.625 | +573 |
| **cả hai** | **28.062** | **+10** |

Giả thuyết trong dispatch đúng một phần: −564 do skeptic áp holdco lên cả phần chưa niêm yết, bù lại +118 do skeptic tính KTPL trên N0×(1−nc) thay vì N0. Đây là khác quy ước, không phải lỗi số. Cùng cách này tái lập điểm 29.510 của skeptic: 29.522 (+12).

## 5. Đồng bộ văn bản

- `ADDENDUM_5F.md:1,5` và `SUMMARY_5F.json:32` vẫn ghi 32.391 / "Headline = chặt-3c". **Không sửa**: hai file này có md5 trong LOCK của DDV/PVT/NT2/PVP (`*/calc_r3/LOCK_md5.txt`). Thay bằng ghi chú cạnh: `ADDENDUM_5F_SYNC_r3b.md`, `SUMMARY_5F_SYNC_r3b.json`.
- `REPORT_r3.md` cũng có md5 trong LOCK nhiều mã ⇒ không sửa; giải thích dòng 28 ở §4 trên.
- Pháp lý SNZ/Đồng Nai: chỉ **WARNING**, không vào base, chưa tra lại sau 05/11.
- Không đặt lệnh, không sửa `kb/dd_price_zones.json`, không email, không PDF.

## 6. Tái lập

```bash
cd SZL/calc_r3b
$DNA_PYEXE -I model_r3b.py > model_r3b_out.txt     # 2 lần, cmp trùng byte (md5 47373344)
$DNA_PYEXE -I make_summary_r3b.py                  # SUMMARY.json (backup r3: SUMMARY_r3.json)
md5sum -c <(grep -v '^#' LOCK_r3b_prerun.txt | sed 's#  SZL/#  ../#; s#  _shared/#  ../../_shared/#; s#  TOP5C#  ../../TOP5C#; s#  STANDARD#  ../../STANDARD#')   # upstream chưa đổi (trừ SUMMARY.json, được thay có chủ đích)
```
