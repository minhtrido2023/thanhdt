# DGC — rà lại DD đợt 1 (24/11/2026, job Taylor_20261124_095517)

Nguồn: `REPORT_recheck_DGC.md` (md5 `c6d0aeab…`) · calc `calc/calc_recheck.py` (run1 = run2 md5 `e2c7541c…`; CONTROL: center_pre = `model_r3b_out.json`, 4 số `r_sens_pre` tái lập) · skeptic `skeptic/r1.json` · đề xuất sổ `LEDGER_PROPOSAL_DGC.json`.
⚠ Output r3b + `dgc_valuation_20261029_r12` đã bị TRIM khỏi git. Khôi phục bằng `git archive 14ad1c925^` / `60fe58b82^` vào `/tmp/ddrestore_B`; md5 của 13 file khớp LOCK_r3b.

**Bước 0:** KHÔNG có tham số nền bị phủ. Không có tầng holding. r: Δ = 0. RONIC terminal = Ke đã áp. Độ nhạy r tính từ mô hình ⇒ chạy skeptic.

## (a) Lệch theo luật mới
- **E15:** Tâm @ Ke 12,3%: **43.657 đ/cp (+4,32%)**.
- **E16:** nguyên văn **KHÔNG CHẮC (proxy lệch DD, k=0.27–0.59)** ⚠ LỢI NHUẬN SỤT? (ROE TTM/5Y=0.38).
- **D4:** dải Ke 43.657 / 41.987. ±bp của r3b tính ở một điểm r, còn tâm có trục r ±50bp ⇒ báo thêm bản dịch cả trục. Lệch ≤ 16 đ/cp.
- **Nhãn nhạy với r** (chỉ báo kèm): ở r ≥ 14,0% thì P10 32.886 < 33.000 ⇒ TRONG.
- **D3:** dự phòng môi trường 100 tỷ/quý + quỹ KTPL đã trừ trong base. Capex môi trường bắt buộc mới sau vụ án = cần kiểm chứng.
- **V6:** V_ngắn 84.931 / V_dài 74.747, D = 0,128 (không cờ). Hai nền máy ≈ 1,8–2,0× tâm DD, do lớp phán đoán của DD.
- **V3/V5:** đã đủ (NARROW · COST/LOCATION). **V8:** EXCLUDED. Nếu gỡ: 2% NAV. Vị thế legacy vượt trần là việc của user.

## (b) Tâm / vùng / nhãn
| | r3b (sổ) | recheck | Δ |
|---|---|---|---|
| Tâm | 41.849 | 41.849 | 0% |
| Vùng | 33.272–50.227 | 33.272–50.227 | 0 |
| Nhãn @ 33.000 (06/11) | DƯỚI, mỏng | DƯỚI, mỏng | không đổi |

## (c) Phản biện
`skeptic/r1.json`: **INCONCLUSIVE (medium)**, 1,06 USD. Cơ học đúng: skeptic chạy lại ra đúng md5; tiền/vay/số CP/tồn kho khớp BQ. Còn hai điểm, ngược chiều nhau:
- **Lên:** nhánh mở lại khai trường không có biên sau 2028 (biến thể vĩnh viễn +14,1%). Thiếu thời hạn giấy phép và trữ lượng KT25/19B. ⚠ Bỏ biên vĩnh viễn là **cách B user đã duyệt 08/11** ⇒ không tự đảo; chỉ xét lại khi có dữ kiện về giấy phép/trữ lượng.
- **Xuống:** ngoại trừ kiểm toán tồn kho 950,9 tỷ chưa mô hình (chặn trên −5,8%); capex môi trường bắt buộc chưa có số; HTM 9.531 chưa đối chiếu PDF; nhà cung cấp quặng mua ngoài/bên liên quan chưa kiểm.

## (d) Rủi ro / việc mở
1. Rev mới cần dữ kiện: thời hạn GP + trữ lượng KT25/19B; cách xử lý ngoại trừ tồn kho (kịch bản có xác suất); capex môi trường bắt buộc (CBTT/quyết định cơ quan quản lý); HTM PDF gốc.
2. Nhãn DƯỚI mỏng ở cả trục r (lật ở +50bp) lẫn trục w mở lại (lật ở w ≤ 0,10).
3. `LEDGER_PROPOSAL_DGC.json` = rev3 `REFUTED_OPEN`. Selfcheck `MIKE_SRC_ROOT=<worktree>` ⇒ lỗi 0. Tâm không đổi.

## (e) Khuyến nghị lớp: **giữ + MECH** cho phần luật mới (0%). FULL chỉ khi có dữ kiện mới (GP/trữ lượng, xử lý ngoại trừ).
Lý do: mã EXCLUDED, không vào candidate. Hai đòn của skeptic ngược chiều nhau và đều thiếu dữ liệu; một đòn còn chạm quyết định user đã duyệt. Mike quyết.
