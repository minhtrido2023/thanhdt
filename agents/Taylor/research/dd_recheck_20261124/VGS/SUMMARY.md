# VGS — rà lại DD đợt 1, nhóm A (24/11/2026, job Taylor_20261124_095514)

Nguồn: `REPORT_recheck_VGS.md` (md5 `e7390d6c…`) · calc `calc/calc_recheck.py` (run1 = run2 md5 `91c4080d…`; CONTROL tái lập r2 26.778 / 26.526 bằng assert) · skeptic `skeptic/r1.json` · đề xuất sổ `LEDGER_PROPOSAL_VGS.json` (selfcheck bản tạm: lỗi 0).

## Bước 0
Không bị phủ:
- r: Δ lãi huy động = 0 ⇒ 13,5%.
- RONIC = Ke, g = 0.
- Base không có tầng CK holding. Dải user chốt 0…+20% đo trên holding niêm yết; đầu 0% trùng base.

⇒ Chạy skeptic.

## (a) Lệch theo luật mới
- **D4:** chưa báo dải Ke ⇒ bổ sung: 28.294 / 26.661 (sau CK 1 tỷ). RONIC = Ke, không lệch. ±50/±100bp r2 tính đúng.
- **D3:** không nhận diện được capex tuân thủ. Môi trường (mạ kẽm/nước thải) = **cần kiểm chứng**.
- **E15:** Tâm @ Ke 12,3% = **28.294 đ/cp (+6,66%)**.
- **E16:** nguyên văn **KHÔNG CHẮC (rẻ…trung tính)** ⚠ ĐỈNH LỢI NHUẬN? (ROE TTM/5Y=1.50), asof 2026-11-20.
- **V6:** bổ sung V_ngắn 25.733 đ/cp (BQ, trung vị LNST TTM 3 mốc / 13,5%). V_dài **cần kiểm chứng**: BQ CFO Q3/26 = NULL.
- **V3 / V5:** đã đủ.
- **V8:** ngoại lệ 5% NAV đã duyệt riêng.

## (b) Tâm / vùng / nhãn
| | r2 (sổ) | recheck | Δ |
|---|---|---|---|
| Tâm (sau CK 1 tỷ) | 26.526 | 26.526 | 0% |
| Vùng | 19.393–34.722 | không đổi | 0 |
| Nhãn @ 19.300 (10/11) | DƯỚI (mong manh) | DƯỚI (mong manh) | không đổi |

## (c) Phản biện
`skeptic/r1.json`: **INCONCLUSIVE (medium)**, 0,80 USD, report_md5 khớp.
- Cơ học đúng.
- Killer (kế thừa r2, cộng 1 mục mới):
  - EPV lõi coi capex duy trì = khấu hao (khoảng 12 vs 45 tỷ/năm).
  - **Mới:** chưa trừ quỹ khen thưởng–phúc lợi.
  - Hai mục trên ⇒ tâm có thể −10…−20%.
  - Legend City theo giá gốc vs trần lợi nhuận NOXH.
- **Lỗi số của recheck:** độ nhạy CK +20% đúng là **24.288** (báo cáo ghi 24.103 do suy ngược từ số không trọng số). Chỉ là độ nhạy, không đụng tâm. Ghi tại đây và trong `notes` của proposal; không sửa báo cáo để giữ md5 khớp r1.

## (d) Việc mở
1. Đọc LCTT FY24/FY25/9T26 để tách capex duy trì/tăng trưởng. Việc này đóng killer và cho ra V_dài.
2. Tìm tỷ lệ trích quỹ khen thưởng–phúc lợi từ NQ ĐHĐCĐ.
3. Tìm mức trần lợi nhuận NOXH và vốn cam kết còn lại của Legend City.
4. Mike quyết có áp `LEDGER_PROPOSAL_VGS.json` không. Nó là rev3 `REFUTED_OPEN`: tâm không đổi, chỉ thêm E15/E16.

## (e) Khuyến nghị lớp: **FULL (rev3 có dữ liệu mới)**
- Phần luật mới là MECH: tâm 0%, nhãn không đổi.
- Base INCONCLUSIVE hai vòng liền (r2, r1-recheck) vì cùng một nhóm mục thiếu.
- Muốn đóng phải đọc LCTT/NQ, tức có nghiên cứu mới. MECH không đóng được.
