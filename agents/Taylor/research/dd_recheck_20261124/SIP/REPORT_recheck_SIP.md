# SIP — Rà lại DD theo luật B5 + E15/E16 (24/11/2026, job Taylor_20261124_095514)

Bản rà lại **REPORT_r3** (`agents/Taylor/research/dd_redo_20261105/SIP/REPORT_r3.md`; sổ ghi CONFIRMED theo `rule_backfill_20261122`, skeptic r3 09/11 CONFIRMED medium). **Không làm lại mô hình**: tái dùng nguyên `model_r3.py` (md5 `343f4b43…`) và `assumptions_r3.json` (md5 `627a563f…`, không sửa). Chỉ chạy lại để đổi **r** (E15, dải Ke).

- **Đầu vào bị TRIM khỏi git** (dọn orphan 19/11): `assumptions_r3.json`, `px_sip_r3_20261106.csv`, `px_g2r2_20261104.csv`, output r2/r3, `SUMMARY_r2.json`. Recheck khôi phục chúng từ lịch sử git vào `calc/mirror/`. md5 khớp từng dòng tính toán của `calc_r3/LOCK_md5.txt` (assert trong code). Ba file LOCK không khôi phục là tài liệu/SQL, model không đọc.
- **Calc:** `calc/calc_recheck.py` exec **nguyên văn** `model_r3.py`, sau đó gọi `run(AX, r, disc, PX)`.
- **CONTROL:** stdout trùng byte `model_r3_out.txt` (md5 `e11f6f4b…`), JSON trùng nội dung `model_r3_out.json` (md5 `c78d9b8a…`). Tâm 54.466, P10 43.257, P90 69.818 (assert). Bảng `sens_r` r3 (β 1 và 0,5) tái lập.
- Chạy 2 lần: `run1.txt` = `run2.txt`, md5 `354ddca1…`. Output: `calc/calc_recheck_out.json`.
- Mù giá: phần định giá không dùng giá. Giá 50.100 (06/11/2026) kế thừa r3, chỉ dùng ở §0 để gắn nhãn.

## 0. Kết luận

**TÂM (base, r 13,5%, sau CK 1,39% @5 tỷ): 54.466 đ/cp — vùng 43.257–69.818. KHÔNG ĐỔI so với r3 (0%).**
Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): 57.744 đ/cp (+6,02% so với tâm base)
So với lịch sử 10 năm của chính mã (thước cơ học RI-ROE5Y, KHÔNG dùng tâm DD; chỉ hiển thị, không phải tín hiệu): **KHÔNG CHẮC (N hiệu dụng thấp, 1.88)** — phân vị [fade 2, hold 13], 89 tháng, N hiệu dụng ≈ 1.9

- **Nhãn** (giá 50.100, ngày 06/11/2026): **TRONG vùng**, thấp hơn tâm 8,0%. Luật 4 KHÔNG ĐẠT (ngưỡng 0,85 × 54.466 = 46.296). Nhãn không đổi so với r3.
- Nhãn không nhạy với r trong dải 12,3–14,5% (P10 41.423…45.909 < giá < P90).
- Tâm đổi 0% và nhãn không đổi ⇒ phần luật mới chỉ cần **xác nhận cơ học**.

## 1. Thay đổi so với r3

| # | Luật | r3 | Recheck | Ảnh hưởng tâm |
|---|---|---|---|---|
| 1 | D4: dải Ke 12,3–13,4% | Chưa báo (chỉ có ±100bp) | Bổ sung: 57.744 / 54.720 | 0 |
| 2 | E15 | Chưa có | Dòng E15 ở §0 | 0 |
| 3 | E16 | Chưa có | Dòng E16 ở §0, chép nguyên văn `dd_history_label.py` (asof 2026-11-20) | 0 |
| 4 | V1: ±50bp | Chỉ có ±100bp trong REPORT (bảng `sens_r` có đủ) | Bổ sung đủ ±50/±100bp (§2) | 0 |
| 5 | V6: hai nền | Chưa có | V_ngắn 40.547, V_dài 36.437, D 0,107 (không cờ) | 0 (chỉ hiển thị) |
| 6 | V8: sizing | Không đề xuất | Nếu user xét: 2% NAV (§3) | 0 |

## 2. Độ nhạy r (V1 + D4 + E15) — cùng mô hình, chỉ đổi r

r tại neo 03/11/2026 là 13,5%, ứng với `deposit_rate_vn` 7,40% (cctg_12m 02/11). Đọc lại 24/11/2026: vẫn 7,40% ⇒ Δ = 0 ⇒ r = 13,5%. β = 1 (giả định).

| r | Tâm sau CK 5 tỷ | P10 | P90 | Δ tâm (đ/cp) | Δ (%) |
|---|---|---|---|---|---|
| 12,3% (E15, đầu dưới dải Ke) | 57.744 | 45.909 | 73.736 | +3.278 | +6,02% |
| 12,5% (−100bp) | 57.161 | 45.404 | 73.043 | +2.694 | +4,95% |
| 13,0% (−50bp) | 55.769 | 44.272 | 71.383 | +1.303 | +2,39% |
| 13,4% (đầu trên dải Ke) | 54.720 | 43.452 | 70.123 | +254 | +0,47% |
| **13,5% BASE** | **54.466** | **43.257** | **69.818** | 0 | 0 |
| 14,0% (+50bp) | 53.244 | 42.319 | 68.339 | −1.222 | −2,24% |
| 14,5% (+100bp) | 52.095 | 41.423 | 66.940 | −2.371 | −4,35% |

- Độ nhạy r lớn hơn các mã NAV vì mảng vận hành (KCN dịch vụ, điện nước) được định giá vô hạn với RONIC = Ke (P/E = 1/r).
- β = 0,5 (bảng `sens_r` r3): −100bp ⇒ 55.769; +100bp ⇒ 53.244.

## 3. Soát luật B5 (D3/D4/V1–V8)

- **Bước 0 (tham số nền):**
  - **r:** không bị phủ (Δ = 0).
  - **RONIC:** r3 đã sửa RONIC = Ke cho mảng vận hành (đính chính #1, −3.389).
  - **CK holding:** không có tầng CK holding trong base. Các công ty con hợp nhất, phần NCI là trục 8,5/20/31%. "Chiết khấu quản trị 10% [UL]" chỉ là độ nhạy (49.020). Dải user chốt 0…+20% đo trên holding niêm yết, không áp cho cấu trúc này.
  - ⇒ Không bị phủ, chạy skeptic.
- **D4 terminal RONIC:** RONIC = Ke ở base (`ronic_ke=True` ⇒ P/E = 1/r, `model_r3.py:53`). Quy ước r2 (RONIC = ROE5Y) chỉ còn là song song (57.855). Không lệch.
- **D3 capex tuân thủ:** base không có dòng chi bắt buộc không tạo doanh thu. Hai điểm **cần kiểm chứng**, không có số:
  - (i) hạ tầng môi trường KCN bắt buộc (xử lý nước thải tập trung, hạ tầng kỹ thuật theo quy hoạch) cho phần quỹ đất 937,1 ha chưa khai thác (72% ở Phước Đông B). Nếu nằm ngoài "chi phí đất" giá vốn thì là dòng tiền ra chưa có trong base.
  - (ii) tiền thuê đất trả Nhà nước (G16, việc mở r3). Đây là nghĩa vụ bắt buộc, không phải capex, cần đối chiếu đã nằm trong biên LN gộp vận hành chưa.
- **V1/D4 r:** đúng neo. Dải Ke + ±50bp nay đã báo (§2).
- **E15/E16:** đã thêm. E15 +6,02% chỉ là độ nhạy, **không đổi tâm** (luật B2 >5% áp cho dịch chuyển TÂM, không áp cho E15).
- **V3 thanh khoản:** đã đủ. CK 1,39% @5 tỷ (127% ADV120, ngoài vùng hiệu chỉnh) + sleeve 40 tr (0,31%: tâm 55.062); nhãn theo sau CK.
- **V5 moat:** đã đủ. ADDENDUM_5F (07–09/11/2026), chưa quá 12 tháng ⇒ tái dùng: NARROW / LOCATION-REGULATORY, không bền. Rủi ro số 1: tốc độ và giá thực thu 937 ha (2025 chỉ 28,6 ha); kênh điện nước phụ thuộc biểu giá EVN. Kiểm nhanh 24/11: không có dữ kiện mới.
- **V6 (chỉ HIỂN THỊ, không vào tâm/sổ)** — `calc/v6_display.py`, dữ liệu `calc/v6_bq.csv` (BQ `ticker_financial`, chỉ đối chiếu):
  - V_ngắn = trung vị LNST TTM (1.186,3 / 1.325,3 / 1.399,0 tỷ) = 1.325,3 / 13,5% = **40.547 đ/cp**.
  - V_dài = FCFE TTM Q3/26 1.191,0 tỷ / 13,5% = **36.437 đ/cp**.
  - **D = 0,107** < ln2 ⇒ không cờ.
  - Caveat: NP của BQ là LNST tổng, chưa tách NCI (trục NCI 8,5–31%) ⇒ cả hai nền có thể cao. Cả hai thấp hơn tâm 54.466 vì tâm DD gồm giá trị quỹ đất chưa khai thác + tài sản sổ sách, mà hai nền theo dòng LN/tiền hiện tại không chứa.
- **V7:** không dùng.
- **V8 sizing:** r3 không đề xuất (luật 4 không đạt). Nếu user xét mua: **2% NAV**, đầu dưới chuẩn 2–4%, vì có cờ quản trị/tín dụng phi ngân hàng 6.016 tỷ = 116% VCSH mẹ (WARNING). Thực thi theo cỡ sleeve (CK ≤0,31%).

### Việc mở kế thừa (r3)
G12 (số ha cho thuê 9T26; mỗi 50 ha −756) · thuyết minh VAT/DTL (+3.123 nếu theo sổ) · G14 NCI từng công ty con · G16 tiền thuê đất · G1/G2 danh tính bên vay · BCTC Q3 HN chưa soát xét · PDF scan chưa đối chiếu bằng text.
