# DRI — Rà lại DD theo luật B5 + E15/E16 (24/11/2026, job Taylor_20261124_095514)

Bản rà lại **REPORT_r3** (`agents/Taylor/research/dd_redo_20261105/DRI/REPORT_r3.md`; sổ ghi CONFIRMED theo `rule_backfill_20261122`, skeptic r3 08/11 CONFIRMED medium). **Không làm lại mô hình**: tái dùng nguyên `dri_redo_r3.py` v2 (md5 `89eb0871…`) + engine `dri_val_supply_adj_r4_20261027/model.py` (md5 `e0bba9b8…`) + `assumptions_r3.json` (md5 `e6a86891…`, không sửa). Chỉ chạy lại để đổi **r** (E15, dải Ke).

- **Đầu vào bị TRIM khỏi git** (dọn orphan 19/11): `assumptions_r3.json`, engine r3/r4, dữ liệu giá cao su/CPI/USDVND, `dri_peers_fin.csv`, bảng thanh khoản, output r3. Recheck khôi phục chúng từ lịch sử git vào `calc/mirror/`. md5 khớp từng dòng `calc/LOCK_r3_md5.txt` (assert trong code).
- **Calc:** `calc/calc_recheck.py` exec **nguyên văn** script r3. Chỉ có một thay đổi lúc chạy: `common.LIQ_CSV` trỏ bản trong mirror, vì đường dẫn tuyệt đối cũ không còn file.
- **CONTROL:** output r3 chạy lại trùng bản gốc (md5 `09e2c313…`) ở mọi trường số; khác duy nhất ở `files_read` (đường dẫn). Tâm 15.257, P10 12.908, P90 17.549 (assert). Bốn mức ±50/±100bp trùng bảng độ nhạy r3.
- Chạy 2 lần: `run1.txt` = `run2.txt`, md5 `116156ce…`. Output: `calc/calc_recheck_out.json`.
- Mù giá: phần định giá không dùng giá. Giá 13.100 (06/11/2026) kế thừa r3, chỉ dùng ở §0 để gắn nhãn.

## 0. Kết luận

**TÂM (base, r 13,5%, sau CK 2,00% @5 tỷ): 15.257 đ/cp — vùng 12.908–17.549 (trước CK 15.568). KHÔNG ĐỔI so với r3 (0%).**
Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): 15.713 đ/cp (+2,99% so với tâm base)
So với lịch sử 10 năm của chính mã (thước cơ học RI-ROE5Y, KHÔNG dùng tâm DD; chỉ hiển thị, không phải tín hiệu): **KHÔNG CHẮC (rẻ…trung tính)** — phân vị [fade 40, hold 11], 114 tháng, N hiệu dụng ≈ 3.9 ⚠ ĐỈNH LỢI NHUẬN? (ROE TTM/5Y=1.80)

- **Nhãn** (giá 13.100, ngày 06/11/2026): **TRONG vùng, sát cạnh dưới**. Giá cao hơn P10 1,5%. Luật 4 KHÔNG ĐẠT (ngưỡng 0,85 × 15.257 = 12.969). Nhãn không đổi so với r3.
- Ở cỡ sleeve thật (CK 0,09–0,18%), giá thấp hơn P10 0,4% ⇒ DƯỚI vùng. Điều này kế thừa r3, không đổi.
- Vị thế đã bán hết 02/11.
- Tâm đổi 0% và nhãn không đổi ⇒ phần luật mới chỉ cần **xác nhận cơ học**.

## 1. Thay đổi so với r3

| # | Luật | r3 | Recheck | Ảnh hưởng tâm |
|---|---|---|---|---|
| 1 | D4: dải Ke 12,3–13,4% | Chưa báo | Bổ sung: 15.713 / 15.294 | 0 |
| 2 | E15 | Chưa có | Dòng E15 ở §0 | 0 |
| 3 | E16 | Chưa có | Dòng E16 ở §0, chép nguyên văn `dd_history_label.py` (asof 2026-11-20) | 0 |
| 4 | V6: hai nền | Chưa có | V_ngắn 15.708, V_dài 6.831, D = 0,833 > ln2 ⇒ giải thích + vùng đọc (§3) | 0 (chỉ hiển thị) |
| 5 | V8: sizing | Không đề xuất (đã bán) | Nếu user xét mua lại: 2% NAV (§3) | 0 |

## 2. Độ nhạy r (V1 + D4 + E15) — cùng mô hình, chỉ đổi r

r tại neo 03/11/2026 là 13,5%, ứng với `deposit_rate_vn` 7,40% (cctg_12m 02/11). Đọc lại 24/11/2026: vẫn 7,40% ⇒ Δ = 0 ⇒ r = 13,5%. β = 1 (giả định).

| r | Tâm sau CK 5 tỷ | P10 | P90 | Δ tâm (đ/cp) | Δ (%) |
|---|---|---|---|---|---|
| 12,3% (E15, đầu dưới dải Ke) | 15.713 | 13.198 | 18.278 | +456 | +2,99% |
| 12,5% (−100bp) | 15.635 | 13.149 | 18.151 | +377 | +2,47% |
| 13,0% (−50bp) | 15.443 | 13.028 | 17.843 | +186 | +1,22% |
| 13,4% (đầu trên dải Ke) | 15.294 | 12.932 | 17.607 | +37 | +0,24% |
| **13,5% BASE** | **15.257** | **12.908** | **17.549** | 0 | 0 |
| 14,0% (+50bp) | 15.077 | 12.746 | 17.268 | −180 | −1,18% |
| 14,5% (+100bp) | 14.902 | 12.679 | 17.000 | −355 | −2,33% |

- Bốn mức ±50/±100bp trùng bảng `sens_mean_post` r3 ⇒ r3 đã có phần này (dạng Δ lãi huy động).
- Nhãn nhạy với r (chỉ báo kèm, không dùng cho nhãn): ở r ≤ 12,5%, P10 ≥ 13.149 > 13.100 ⇒ DƯỚI. Ở r ≥ 13,0% thì TRONG. Nhãn base nằm sát biên.

## 3. Soát luật B5 (D3/D4/V1–V8)

- **Bước 0 (tham số nền):**
  - **r:** không bị phủ (Δ = 0).
  - **CK holding:** không có tầng holding (công ty con Lào hợp nhất; rò rỉ chuyển tiền đã mô hình hoá bằng wht 8,16% + KTPL + quỹ dự phòng).
  - **RONIC:** nhánh NPV0, RONIC = Ke cho tái canh/dự án mới.
  - ⇒ Không bị phủ, chạy skeptic.
- **D4 terminal RONIC:** không có terminal vô hạn. Engine cho giá trị về 0 sau 2054 (hết tô nhượng; L0), tái canh = NPV0 (RONIC = Ke). Không lệch.
  - Lưu ý kế thừa (ADDENDUM_5F_r3 dòng 28): Cref 30,22 tr/t giữ tới 2054 ⇒ GPM mô hình khoảng 36% > peer 25%. Theo quy ước user 08/11 ("NARROW/NONE: không thưởng, KHÔNG TRỪ ở giai đoạn dự báo") thì đây không phải lệch D4. Bản "biên về ngành" là độ nhạy −20,6% (ADDENDUM).
- **D3 capex tuân thủ:** capex tái canh/KTCB đã tường minh trong engine r4 (`capex(s, m)`, m 4/7/10 năm chăm sóc), đó là capex tăng trưởng/duy trì. Chưa nhận diện chi bắt buộc không tạo doanh thu. **Cần kiểm chứng:** nghĩa vụ theo hợp đồng tô nhượng Lào (thuế đất, bảo vệ/trồng bù rừng trên phần đất thuộc quy hoạch rừng bảo tồn). Văn bản tô nhượng 01616/KĐ/DDT4 chưa công khai ⇒ không có số.
- **V1/D4 r:** đúng neo. Dải Ke nay đã báo (§2).
- **E15/E16:** đã thêm.
- **V3 thanh khoản:** đã đủ. CK 2,00% @5 tỷ + sleeve 10–40 tr (0,09–0,18%); nhãn theo sau CK.
- **V5 moat:** đã đủ. ADDENDUM_5F_r3 07/11/2026, chưa quá 12 tháng ⇒ tái dùng: NARROW / LOCATION-COST. Rủi ro số 1 là giá cao su (price-taker); rủi ro số 2 là đồng hồ đất (NQ15 + tô nhượng). Kiểm nhanh 24/11: không có dữ kiện mới.
- **V6 (chỉ HIỂN THỊ, không vào tâm/sổ)** — `calc/v6_display.py`, dữ liệu `calc/v6_bq.csv` (BQ `ticker_financial`, chỉ đối chiếu):
  - **V_ngắn** = trung vị LNST TTM (101,7 / 155,2 / 208,8 tỷ) = 155,2 / 13,5% = **15.708 đ/cp**.
  - **V_dài** = FCFE TTM Q3/26 67,5 tỷ / 13,5% = **6.831 đ/cp**. FCFE ở đây là CFO + CF đầu tư theo BQ, đơn giản hoá: chưa có g, chưa tách vay.
  - **D = 0,833 > ln2 (0,693) ⇒ cờ phân kỳ.** Nguồn chênh:
    - (i) CFO TTM chỉ khoảng 100 tỷ so với LNST 208,8, do vốn lưu động mùa vụ: CFO quý dao động −25…+110 tỷ.
    - (ii) Capex tái canh/KTCB.
    - (iii) LNST TTM ở đỉnh (cờ E16 ĐỈNH LỢI NHUẬN).
  - V_dài < giá và capex chủ yếu là tái canh ⇒ đọc là "FCFE thấp vì đầu tư (tái canh) + vốn lưu động", **không phải cảnh báo đắt**. Vùng đọc mở rộng theo hai nền: [6.831; 15.708], chỉ hiển thị.
  - D < ln3 ⇒ không phải phân kỳ mạnh.
- **V7:** không dùng.
- **V8 sizing:** đã bán hết 02/11. Nếu user xét mua lại: đề xuất **2% NAV**, đầu dưới chuẩn 2–4%, vì nhãn sát biên P10 và moat NARROW. Thực thi theo cỡ sleeve (CK ≤0,18%).

### Việc mở kế thừa
1. Giấy nhượng đất 2016 (mốc 2054) chưa xác minh. Phần đất thuộc quy hoạch rừng bảo tồn.
2. Khoản vay Dakruco gia hạn; tài sản đảm bảo là 6 triệu cp DRI (WARNING, không vào base).
3. Mật độ q của khối thanh lý là giả định [UL], đóng góp lớn nhất +635.
