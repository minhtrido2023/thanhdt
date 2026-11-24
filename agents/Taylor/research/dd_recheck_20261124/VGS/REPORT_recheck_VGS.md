# VGS — Rà lại DD theo luật B5 + E15/E16 (24/11/2026, job Taylor_20261124_095514)

Bản rà lại **REPORT.md r2** (`agents/Taylor/research/dd_VGS_20261110/REPORT.md`, md5 `aa88380c…`) theo HANDOFF `dd_recheck_20261124`. **Không làm lại mô hình**: tái dùng nguyên `model_r2.py` (md5 `05e02527…`) và `assumptions_r2.json` (md5 `c13014360aa523a102e31b5699c44db9`, không sửa). Chỉ chạy lại để đổi **r** (E15, dải Ke).

- **Calc:** `calc/calc_recheck.py`. Nó assert md5 model và assumptions, rồi exec model gốc với output ghi vào thư mục recheck (không ghi đè `model_out_r2.json` cũ). **Chân CONTROL:** ở r = 13,5%, script tái lập đúng tâm trước CK 26.778 và tâm sau CK 1 tỷ 26.526 (có assert trong code).
- Chạy 2 lần: `run1.txt` = `run2.txt`, md5 `91c4080d…`. Output: `calc/calc_recheck_out.json`.
- Mù giá: calc không đọc giá. Giá so sánh 19.300 (10/11/2026) kế thừa từ r2, chỉ dùng ở §0 để gắn nhãn.

## 0. Kết luận

**TÂM (base, r 13,5%, sau CK cỡ thực thi ≤1 tỷ): 26.526 đ/cp — vùng 19.393–34.722 (trước CK: 26.778). KHÔNG ĐỔI so với r2 (0%).**
Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): 28.294 đ/cp (+6,66% so với tâm base)
So với lịch sử 10 năm của chính mã (thước cơ học RI-ROE5Y, KHÔNG dùng tâm DD; chỉ hiển thị, không phải tín hiệu): **KHÔNG CHẮC (rẻ…trung tính)** — phân vị [fade 45, hold 27], 120 tháng, N hiệu dụng ≈ 7.0 ⚠ ĐỈNH LỢI NHUẬN? (ROE TTM/5Y=1.50)

- **Nhãn** (giá 19.300, ngày 10/11/2026): **DƯỚI vùng (MONG MANH)**. Giá chỉ thấp hơn P10 0,5%. Luật 4 ĐẠT (ngưỡng 0,85 × 26.526 = 22.547). Nhãn không đổi so với r2.
- Tâm đổi 0% (<5%) và lớp nhãn không đổi ⇒ phần luật mới chỉ cần **xác nhận cơ học**. Vòng skeptic gần nhất (r2, 24/11) ra INCONCLUSIVE. Các điểm mở của vòng đó vẫn còn (§3), vì recheck không có dữ kiện mới để đóng chúng.

## 1. Thay đổi so với r2

| # | Luật | r2 | Recheck | Ảnh hưởng tâm |
|---|---|---|---|---|
| 1 | D4: hai đầu dải Ke 12,3–13,4% | Chưa báo | Bổ sung, xem §2 | 0 |
| 2 | E15 | Chưa có | Dòng E15 ở §0 | 0 |
| 3 | E16 | Chưa có | Dòng E16 ở §0, chép nguyên văn từ `dd_history_label.py` (asof 2026-11-20; `calc/dd_history_label_VGS_2026-11-20.*`) | 0 |
| 4 | V6: hai nền | Chưa có | Bổ sung V_ngắn. V_dài: cần kiểm chứng (§3) | 0 (chỉ hiển thị) |
| 5 | V8: sizing | Không ghi trong REPORT | Ngoại lệ 5% NAV đã được user duyệt riêng (SKILL V8). Recheck không đề xuất mức mới | 0 |
| 6 | Bước 0: độ nhạy CK holding | Chỉ có 30%, "không có cơ sở dữ liệu" | Nay có dải tham chiếu user chốt 0…+20% (đo trên holding niêm yết, ca HHS). Base 0% của VGS trùng đầu dải. Thêm độ nhạy +20% | 0 |

## 2. Độ nhạy r (V1 + D4 + E15) — cùng mô hình, chỉ đổi r

r tại neo 03/11/2026 là 13,5%, ứng với lãi huy động 12T hiệu dụng `deposit_rate_vn` = 7,40% (cctg_12m 02/11). Đọc lại 24/11/2026: vẫn 7,40% (last_update 16/11) ⇒ Δ = 0 ⇒ r = 13,5%. β = 1 (giả định).

| r | Tâm trước CK | Tâm sau CK 1 tỷ | P10 / P90 sau CK 1 tỷ | Δ tâm (đ/cp) | Δ (%) |
|---|---|---|---|---|---|
| 12,3% (E15, đầu dưới dải Ke) | 28.563 | 28.294 | 20.680 / 36.834 | +1.768 | +6,66% |
| 12,5% (−100bp) | 28.242 | 27.976 | 20.470 / 36.431 | +1.450 | +5,47% |
| 13,0% (−50bp) | 27.482 | 27.223 | 19.911 / 35.544 | +697 | +2,63% |
| 13,4% (đầu trên dải Ke) | 26.915 | 26.661 | 19.493 / 34.881 | +135 | +0,51% |
| **13,5% BASE** | **26.778** | **26.526** | **19.393 / 34.722** | 0 | 0 |
| 14,0% (+50bp) | 26.125 | 25.879 | 18.912 / 33.958 | −647 | −2,44% |
| 14,5% (+100bp) | 25.517 | 25.276 | 18.464 / 33.248 | −1.250 | −4,71% |

- Các mức ±50/±100bp khớp bảng độ nhạy của r2 §6 (28.242 / 27.482 / 26.125 / 25.517 trước CK) ⇒ r2 đã báo đúng phần này.
- Độ nhạy r lớn hơn HHS vì lõi ống và liên kết đều được định giá bằng EPV vô hạn (NI/r).
- Nhãn không nhạy với r theo chiều xấu: ở mọi r ≤ 13,5%, P10 sau CK ≥ 19.393 > 19.300 ⇒ vẫn DƯỚI. Ở r 14,0%, P10 18.912 < giá ⇒ nhãn chuyển TRONG. Đây là chỉ báo kèm, không dùng cho nhãn.

## 3. Soát luật B5 (D3/D4/V1–V8)

- **Bước 0 (tham số nền đã bị phủ chưa):**
  - **r:** không bị phủ (Δ lãi huy động = 0).
  - **RONIC:** r2 dùng g = 0, RONIC = Ke (moat NONE), đúng D4.
  - **CK holding:** base không có tầng CK holding. r2 chỉ ghi độ nhạy 30% và nói rõ "không có cơ sở dữ liệu". Dải user chốt 24/11 (0…+20%, `kb/projects/ck-hhs-reference-range-20261124.md`) được đo trên holding niêm yết. Nó không áp thẳng cho liên kết chưa niêm yết và dự án của VGS. Đầu 0% trùng base ⇒ base **không bị phủ**.
  - Độ nhạy +20% lên hai khối liên kết + Legend City (phần đóng góp có trọng số là 13.377 đ/cp, suy từ r2: 26.778 − 22.765 = 4.013 = 30% × 13.377): tâm trước CK 26.778 − 0,2 × 13.377 = **24.103** (−10,0%). Đây là phép tính số học trên số của r2, chỉ là độ nhạy, không vào tâm.
  - ⇒ Bước 0 không bảo dừng, nên chạy skeptic.
- **D4 terminal RONIC:** RONIC = Ke ở base, g = 0. Không lệch.
- **D3 capex tuân thủ:** `assumptions_r2.json` không có hạng mục chi bắt buộc nào không tạo doanh thu. Recheck không nhận diện được capex tuân thủ, nhưng chưa đọc lại BCTC để soát môi trường (dây chuyền mạ kẽm/xử lý nước thải) ⇒ **cần kiểm chứng**, không có số. Điểm liên quan nhưng **không phải** capex tuân thủ, do skeptic r2 nêu: capex duy trì khoảng 45 tỷ/năm (ước lượng của skeptic) so với khấu hao khoảng 12 tỷ/năm. Nếu đúng, EPV lõi có thể cao 7–15%. Đây là việc mở kế thừa, chưa có số kiểm được.
- **V1/D4 r:** r 13,5% đúng neo + β×Δ (Δ = 0). Độ nhạy ±50/±100bp r2 đúng. Dải Ke nay đã báo (§2).
- **E15/E16:** đã thêm (§0).
- **V3 thanh khoản:** đã đủ ở r2 §6: tâm trước CK 26.778 và sau CK theo 3 cỡ; nhãn theo giá trị sau CK ở cỡ thực thi ≤1 tỷ; có số phiên thoát lệnh @10% ADV.
- **V5 moat:** đã đủ. 5F đầy đủ làm ngày 10/11/2026 (r2 §5), chưa quá 12 tháng ⇒ tái dùng: NONE / SCALE-DISTRIBUTION (không bền). Rủi ro số 1 là biên chế biến mỏng và đầu vào HRC mua từ đối thủ tích hợp. Kiểm nhanh 24/11: không có dữ kiện mới.
- **V6 (chỉ HIỂN THỊ, không vào tâm/sổ)** — script `calc/v6_display.py`, dữ liệu `calc/v6_bq.csv` (BQ `ticker_financial`, chỉ đối chiếu):
  - **V_ngắn** = trung vị LNST TTM 3 mốc (Q3/24 61,4; Q3/25 213,7; Q3/26 276,7 tỷ) = 213,7 tỷ / 13,5% = **25.733 đ/cp**.
    - RONIC = Ke ⇒ g không đổi giá trị; tỷ lệ tái đầu tư không bị chặn.
    - Cờ ĐỈNH LỢI NHUẬN: TTM Q3/26 chứa phần lãi liên kết ở đỉnh chu kỳ (r2 §0).
  - **V_dài: cần kiểm chứng.** BQ `CF_OA_P0` / `CF_Invest_P0` quý Q3/26 = NULL, và LCTT gốc chưa được đọc lại trong recheck. Chưa tính D, chưa có cờ.
- **V7:** chỉ hiển thị, không đổi.
- **V8:** VGS có ngoại lệ **5% NAV** đã duyệt riêng (SKILL V8). Recheck không đề xuất mức mới.

### Việc mở kế thừa (skeptic r2 INCONCLUSIVE, 24/11)
1. Tách capex duy trì / tăng trưởng của lõi ống (EPV coi capex duy trì = khấu hao).
2. Legend City NPV = 0 vs trần lợi nhuận NOXH. Cần mức trần theo quy định và phần cam kết vốn còn lại.
3. Biến động dự phòng 21,1 tỷ: nếu là một lần thì "EBIT lõi +14,9%" có thể ≈ phẳng.
4. Chiều lên: khoản ứng trước Vinaconex 38 tỷ bị bỏ sót; biên sản phẩm tự sản xuất 5,29% gợi ý GPM base 3,6% có thể thấp.
5. V_dài (V6) cần LCTT gốc 9T/2026.
