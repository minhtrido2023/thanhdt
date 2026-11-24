# TCH — Rà lại DD theo luật B5 + E15/E16 (24/11/2026, job Taylor_20261124_095514)

Bản rà lại **REPORT_r3b** (`agents/Taylor/research/dd_redo_20261105/TCH/REPORT_r3b.md`, md5 `1bf1cf07…`) theo HANDOFF `dd_recheck_20261124`. **Không làm lại mô hình**: tái dùng nguyên `tch_r3b.py` (md5 `bc9a874f…`) và `assumptions_r3b.json` (md5 `6a1f0e0d…`, không sửa). Chỉ chạy lại để đổi **r** (E15, dải Ke) và CK holding trên phần công ty con (Bước 0).

- **Đầu vào bị TRIM khỏi git** ở commit `14ad1c925` (dọn orphan 19/11): `assumptions_r3b.json`, `calc_r3/assumptions_r3.json`, `calc_r3/tch_r3_out.json`, `_shared/wpct.py`, `SUMMARY.json`. Recheck khôi phục chúng từ `fc5bd02d9` vào `calc/mirror/`. md5 khớp từng dòng `calc_r3b/LOCK_md5.txt`, có assert trong code.
- **Calc:** `calc/calc_recheck.py` exec bản sao model, chỉ với 3 thay thế văn bản, mỗi chuỗi assert đúng 1 lần:
  1. ghi đè R0;
  2. bỏ assert control r3 khi có ghi đè;
  3. nhân (1 − HOLD) vào phần công ty con, đúng cách `tch_r3.py:41` từng làm.
- **CONTROL:** ở r neo, HOLD = 0, tái lập đúng r3b: tâm trước CK 15.964, sau CK 5 tỷ 15.864, P10 14.563, P90 17.325 (assert). Bản song song "g kiểm toán 42,7%" tái lập 13.642.
- Chạy 2 lần: `run1.txt` = `run2.txt`, md5 `d2d3bb14…`. Output: `calc/calc_recheck_out.json`.
- Mù giá: calc không đọc giá. Giá so sánh 13.500 (06/11/2026) kế thừa r3b, chỉ dùng ở §0 để gắn nhãn.

## 0. Kết luận

**TÂM (base, r 13,5%, CK holding 0%, sau CK 5 tỷ 0,63%): 15.864 đ/cp — vùng 14.563–17.325. KHÔNG ĐỔI so với r3b (0%).**
Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): 16.270 đ/cp (+2,56% so với tâm base)
So với lịch sử 10 năm của chính mã (thước cơ học RI-ROE5Y, KHÔNG dùng tâm DD; chỉ hiển thị, không phải tín hiệu): **KHÔNG CHẮC (trung tính…đắt)** — phân vị [fade 47, hold 90], 120 tháng, N hiệu dụng ≈ 5.2

- **Nhãn** (giá 13.500, ngày 06/11/2026): **DƯỚI vùng — NHÃN KHÔNG CHẮC**. Giá thấp hơn P10 14.563 7,3%. Luật 4 KHÔNG ĐẠT ở 5 tỷ (ngưỡng 0,85 × 15.864 = 13.484). Nhãn không đổi so với r3b.
- **Bước 0 — CK holding:** base 0% trùng đầu "lạc quan" của dải user chốt 24/11 (0…+20%). Ở đầu +20%, cùng mô hình: tâm **14.294 (−9,9%)**, P10 13.155 ⇒ **TRONG vùng**. Nhãn base chỉ đứng ở một đầu của dải đã chốt (§3).
- `FLOOR_FAIL` (CF_OA_3Y −771,7 tỷ) ⇒ không vào candidate, bất kể nhãn. Sizing V8 không áp.
- Tâm base đổi 0% và nhãn không đổi ⇒ phần luật mới chỉ cần xác nhận cơ học. Điểm yếu quyết định của skeptic r2 (biên gộp 51,9% chưa soát xét vs 42,7% kiểm toán) vẫn mở: chờ báo cáo soát xét 6T FY26.

## 1. Thay đổi so với r3b

| # | Luật | r3b | Recheck | Ảnh hưởng tâm |
|---|---|---|---|---|
| 1 | V1: độ nhạy ±50/±100bp | Không có bảng riêng (r là trục ±dr trong lưới) | Bổ sung, xem §2 | 0 |
| 2 | D4: dải Ke 12,3–13,4% | Chưa báo | Bổ sung: 16.270 / 15.897 | 0 |
| 3 | E15 | Chưa có | Dòng E15 ở §0 | 0 |
| 4 | E16 | Chưa có | Dòng E16 ở §0, chép nguyên văn `dd_history_label.py` (asof 2026-11-20) | 0 |
| 5 | Bước 0: CK holding | Song song 27% (theo tham chiếu HHS cũ 26,63%), chạy trên mô hình **r3**, chưa chạy r3b | Thay bằng dải user chốt 0…+20%, chạy trên **r3b**: +20% ⇒ 14.294. Bản 27% trên r3b: 13.745 | 0 (song song) |
| 6 | V6: hai nền | Chưa có | V_ngắn 5.878. FCFE TTM ≤ 0 ⇒ chỉ V_ngắn (§3) | 0 (chỉ hiển thị) |

## 2. Độ nhạy r (V1 + D4 + E15) — cùng mô hình, chỉ đổi r (r là tâm của trục ±dr trong lưới)

r tại neo 03/11/2026 là 13,5%, ứng với `deposit_rate_vn` 7,40% (cctg_12m 02/11). Đọc lại 24/11/2026: vẫn 7,40% ⇒ Δ = 0 ⇒ r = 13,5%. β = 1 (giả định).

| r | Tâm sau CK 5 tỷ | P10 | P90 | Δ tâm (đ/cp) | Δ (%) | g kiểm toán 42,7% (song song) |
|---|---|---|---|---|---|---|
| 12,3% (E15, đầu dưới dải Ke) | 16.270 | 14.894 | 17.752 | +406 | +2,56% | 13.979 |
| 12,5% (−100bp) | 16.201 | 14.833 | 17.675 | +337 | +2,12% | 13.922 |
| 13,0% (−50bp) | 16.031 | 14.707 | 17.515 | +167 | +1,05% | 13.781 |
| 13,4% (đầu trên dải Ke) | 15.897 | 14.591 | 17.362 | +33 | +0,21% | 13.670 |
| **13,5% BASE** | **15.864** | **14.563** | **17.325** | 0 | 0 | 13.642 |
| 14,0% (+50bp) | 15.700 | 14.421 | 17.138 | −164 | −1,03% | 13.507 |
| 14,5% (+100bp) | 15.540 | 14.283 | 16.955 | −324 | −2,04% | 13.375 |

Độ nhạy r thấp: NAV quỹ đất, thặng dư thu trong 1–4 năm, không có terminal vô hạn. Nhãn không đổi trong toàn dải r (P10 ≥ 14.283 > 13.500).

## 3. Soát luật B5 (D3/D4/V1–V8)

- **Bước 0 (tham số nền):**
  - **r:** không bị phủ.
  - **CK holding:** có tầng holding (TCH hợp nhất CRV 68,02% qua NC-II và các công ty con khác).
    - r3b dùng base 0%. Mức này nằm trong dải user chốt 24/11 (`kb/projects/ck-hhs-reference-range-20261124.md`: 0% = "đầu lạc quan", +20% = mốc hiện tại, đo 15–23%) ⇒ base **không bị phủ**.
    - Độ nhạy song song cũ 27% thì **đã lạc hậu**: nó lấy tham chiếu HHS 26,63% (N=6), đã bị v5 phủ, và chạy trên mô hình r3.
    - Cùng mô hình r3b, CK áp lên phần công ty con: **+20% ⇒ 14.294** (P10 13.155, P90 15.587) ⇒ **TRONG**. Cộng r 12,3% ⇒ 14.641. Stress 27% ⇒ 13.745 (P10 12.662).
    - Dải 0…+20% được chốt cho HHS. Áp cho TCH là suy rộng: dải được đo và chốt cho HHS; TCH giữ CRV 68,02% (r3b §3). Quan hệ sở hữu HHS–TCH không kiểm trong recheck. Base vẫn giữ quy ước "CK holding 0% [UL]" mà user đã phán xử từ r3.
  - ⇒ Bước 0 không bảo dừng. Ghi rõ: **nhãn DƯỚI chỉ đứng ở đầu 0% của dải.**
- **D4 terminal RONIC:** không áp dụng. Mô hình là NAV quỹ đất hữu hạn; quỹ đất mới NPV0 (RONIC = Ke). Moat NONE (ADDENDUM_5F). Không lệch.
- **D3 capex tuân thủ:** r3b không có hạng mục chi bắt buộc không tạo doanh thu. Hai điểm **cần kiểm chứng**, không có số:
  - (i) nghĩa vụ quỹ đất NƠXH 20% / tiền SDĐ bổ sung theo quy định ở NC-II, GR, H2. TMĐT NC-II 15.076 "gồm tiền SDĐ" ⇒ phần SDĐ đã nằm trong k. Còn nghĩa vụ NƠXH thì chưa xác nhận.
  - (ii) Recheck không đọc lại BCTC/BCTN gốc để soát D3 ⇒ chưa có số để đưa vào base hay độ nhạy.
- **V1/D4 r:** đúng neo. Dải Ke và ±50/±100bp nay đã báo (§2).
- **E15/E16:** đã thêm.
- **V3 thanh khoản:** đã đủ. CK 0,63% @5 tỷ; sleeve 40 tr tâm 15.955; nhãn theo sau CK.
- **V5 moat:** đã đủ. ADDENDUM_5F 07/11/2026, chưa quá 12 tháng ⇒ tái dùng: NONE / LOCATION (quỹ đất giá vốn cũ, hữu hạn). Rủi ro số 1: biên quỹ đất mới (150 Tô Hiệu, I.14) mỏng hơn 51,9% lịch sử. Kiểm nhanh 24/11: không có dữ kiện mới.
- **V6 (chỉ HIỂN THỊ)** — `calc/v6_display.py`, dữ liệu `calc/v6_bq.csv` (BQ `ticker_financial`, chỉ đối chiếu):
  - V_ngắn = trung vị LNST TTM (942,8 / 572,3 / 796,1 tỷ) = 796,1 / 13,5% = **5.878 đ/cp**.
  - FCFE TTM Q3/26 = −2.858,6 tỷ ≤ 0 ⇒ **chỉ V_ngắn**.
  - Dòng tiền âm vì chi mua quỹ đất (150 Tô Hiệu, I.14) và vốn lưu động dự án (đúng như FLOOR_FAIL). V_ngắn thấp hơn xa tâm NAV vì giá trị nằm ở thặng dư quỹ đất chưa đi qua lợi nhuận (asset-play). Không phải tín hiệu đắt.
- **V7:** không dùng.
- **V8:** không áp (FLOOR_FAIL).

### Việc mở kế thừa
1. **Biên gộp:** chờ báo cáo soát xét 6T FY26 (AASC) cho biên 51,9%. Nếu biên thật ≈ 42,7% ⇒ tâm 13.642 và nhãn TRONG (skeptic r2).
2. **CK holding:** user xác nhận dải 0…+20% (chốt cho HHS) có áp cho TCH không, và base đặt ở đâu trong dải.
3. NƠXH/SDĐ bổ sung (D3) — cần kiểm chứng.
4. Danh tính "NH Sài Gòn Tài Lộc" (678,3 tỷ) chưa xác minh.
