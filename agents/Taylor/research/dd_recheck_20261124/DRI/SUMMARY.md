# DRI — rà lại DD đợt 1, nhóm A (24/11/2026, job Taylor_20261124_095514)

Nguồn: `REPORT_recheck_DRI.md` (md5 `07add5f0…`) · calc `calc/calc_recheck.py` (run1 = run2 md5 `116156ce…`; CONTROL: output r3 chạy lại trùng bản gốc, trừ đường dẫn `files_read`) · skeptic `skeptic/r1.json` · `LEDGER_PROPOSAL_DRI.json` (rev4, selfcheck bản tạm: lỗi 0).

⚠ **Hạ tầng:** engine r3/r4, `assumptions_r3.json`, dữ liệu giá cao su/CPI/USDVND, bảng thanh khoản và output r3 bị **xoá khỏi git** (TRIM 19/11). Recheck khôi phục chúng từ lịch sử vào `calc/mirror/`, md5 khớp LOCK. `assumptions_file` trong sổ đang trỏ tới file không còn.

## Bước 0
Không bị phủ:
- r: Δ = 0.
- Không có tầng CK holding (con Lào hợp nhất; rò rỉ đã mô hình bằng wht/KTPL/quỹ).
- RONIC = Ke ở nhánh NPV0.

⇒ Chạy skeptic.

## (a) Lệch theo luật mới
- **D4:**
  - Thiếu dải Ke ⇒ bổ sung 15.713 / 15.294.
  - ±50/±100bp r3 đúng.
  - Không có terminal vô hạn (giá trị về 0 sau 2054).
- **D3:** **lệch thật** (skeptic xác nhận). Nghĩa vụ tô nhượng Lào và trồng bù/bảo vệ phần đất rừng bảo tồn chưa có trong base. Văn bản 01616/KĐ/DDT4 chưa công khai ⇒ chưa định lượng được.
- **E15:** **15.713 đ/cp (+2,99%)**.
- **E16:** nguyên văn **KHÔNG CHẮC (rẻ…trung tính)** ⚠ ĐỈNH LỢI NHUẬN? (ROE TTM/5Y=1.80).
- **V6:** V_ngắn 15.708, V_dài 6.831, **D 0,833 > ln2**.
  - Giải thích: CFO TTM khoảng 100 vs LNST 208,8 tỷ (vốn lưu động mùa vụ), capex tái canh, LN đỉnh.
  - Vùng đọc mở rộng [6.831; 15.708]. Không phải cảnh báo đắt.
- **V3 / V5:** đã đủ.
- **V8:** nếu mua lại thì 2% NAV.

## (b) Tâm / vùng / nhãn
| | r3 (sổ) | recheck | Δ |
|---|---|---|---|
| Tâm (sau CK 5 tỷ) | 15.257 | 15.257 | 0% |
| Vùng | 12.908–17.549 | không đổi | 0 |
| Nhãn @ 13.100 (06/11) | TRONG (sát cạnh dưới) | TRONG (sát cạnh dưới) | không đổi |

Ở r ≤ 12,5% thì P10 > giá ⇒ DƯỚI. Đây chỉ là chỉ báo kèm.

## (c) Phản biện
`skeptic/r1.json`: **INCONCLUSIVE (medium)**, 1,13 USD, md5 khớp.
- Cơ học đúng: skeptic tự kiểm BQ, các số khớp. Biên 36% có cơ sở từ lịch sử chính DRI.
- Killer:
  - quyền đất tô nhượng chưa xác minh + nghĩa vụ rừng (D3), có thể >5%;
  - ý kiến kiểm toán FY2025 không nêu;
  - Dakruco 40 tỷ tính đủ mệnh giá (−1,8…−3,5%).
- ⇒ **Sổ hạ CONFIRMED (backfill) → REFUTED_OPEN (rev4)**.

## (d) Việc mở
1. Lấy điều khoản tô nhượng + nghĩa vụ rừng từ BCTC/BCTN gốc hoặc nhờ legal-vn; định lượng capex tuân thủ.
2. Ghi ý kiến kiểm toán FY2025.
3. Cân nhắc haircut Dakruco (TSĐB là cp DRI).
4. Báo song song q 0,7/1,0.
5. V_ngắn sau KTPL.
6. Khôi phục file bị trim (hạ tầng).

## (e) Khuyến nghị lớp: **FULL (rev5 có dữ liệu tô nhượng)**
- Phần luật mới đổi tâm 0%, nhưng D3 là lệch thật chưa định lượng được, nên MECH không đủ.
- Vị thế đã bán; không gấp trừ khi user xét mua lại.
