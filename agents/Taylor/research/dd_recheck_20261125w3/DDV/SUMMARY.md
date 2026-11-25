# DDV — rà lại DD đợt 3 (25/11/2026, job Taylor_20261125_032443)

Nguồn: `REPORT_recheck_DDV.md` (md5 `1da93334…`) · calc `calc/calc_recheck.py` (run1 = run2 md5 `1b0e4835…`; CONTROL model_r3 stdout trùng byte run1 r3 `eeee072d…`) · skeptic `skeptic/r1.json` · E17 `ADJ_CENTER.md` + `adj.json` (`calc/calc_adj.py`, run1 = run2 `0c30b312…`) · đề xuất sổ `LEDGER_PROPOSAL_DDV.json` (rev3).
⚠ calc_r3 + BCTC src bị TRIM 19/11. Khôi phục: `git archive 14ad1c925^ agents/Taylor/research/dd_redo_20261105 | tar -x -C /tmp/ddrestore_w3a/mike` và `git archive ae0ff5446^ agents/Taylor/research/dd_DDV_20261026 | tar -x …`; md5 khớp LOCK.

**Bước 0:** KHÔNG có tham số nền bị phủ (không holding; lãi huy động 7,40% = neo ⇒ r 13,5%; RONIC = Ke từ r3; độ nhạy r tính từ mô hình). "r 14,58%" trong HANDOFF là r ngụ ý bởi giá, không phải r của tâm.

## (a) Lệch theo luật mới
- **E15:** Tâm @ Ke 12,3%: **16.854 (+5,93%)**. Dải Ke 16.854 / 15.983. ±50/±100bp khớp r3 từng đồng.
- **E16:** nguyên văn **RẺ** — phân vị [fade 6, hold 0], 60 tháng, N hiệu dụng ≈ 2.9 (thước cơ học, không phải nhãn DD).
- **D3:** bãi thạch cao Đình Vũ = capex tuân thủ chưa có số ⇒ C (độ nhạy −674 đ/100 tỷ). **D4:** đúng.
- **V6:** V_ngắn 29.229 / V_dài 68.749, D 0,855 > ln2 — do LN chuẩn hoá đỉnh 393,5 tỷ + g 12,75% của engine; chỉ hiển thị.
- **V3/V5:** đã đủ (CK 1,47%; moat NONE). **V8:** 0% mua mới ở giá tham chiếu; ≤2% NAV nếu xuống dưới luật 4.

## (b) Tâm / vùng / nhãn
| | rev2 (sổ) | recheck rev3 | Δ |
|---|---|---|---|
| Tâm | 15.911 | 15.911 | 0% |
| Vùng | 13.315–18.573 | 13.315–18.573 | 0 |
| Nhãn @ 15.200 (06/11) | TRONG | TRONG | không đổi |

## (c) Phản biện
`skeptic/r1.json`: **INCONCLUSIVE (medium)**, 0,79 USD. Cơ học đúng (tâm độc lập 15.905). Đòn 8: thiếu trích quỹ KTPL; capex bãi thạch cao chưa có số; hai chiều (DT FY2025 đỉnh −21,7% vs khoản trừ lãi gửi +7,4%) chưa đủ bằng chứng để đổi base. Không sửa base (không có dữ kiện mới đổi mô hình) ⇒ không chạy vòng 2. Nhãn sổ **REFUTED_OPEN**.

## (d) Tâm kỳ vọng điều chỉnh (E17)
**15.050 đ/cp (dải 14.401–16.264; −5,41%)**, căn cứ 3 hạng mục (2 A + 1 B): trích KTPL 10,19% LNST (A, −6,07pp) · tồn quỹ KTPL 80,22 tỷ (A, −3,06pp) · khoản trừ lãi gửi về trung điểm proxy (B, +3,72pp). Tính bằng tổ hợp trong mô hình (|Σ| > 5%). Bảng điều kiện đổi số: ADJ_CENTER.md §3 — quan trọng nhất: cam kết vốn bãi thạch cao (mỗi 100 tỷ −4,2%), tỷ lệ KTPL 2026 (NQ ĐHĐCĐ 2027), thu nhập TC kiểm toán 2015–22.

## (e) Rủi ro / việc mở · khuyến nghị lớp
Rủi ro lớn nhất vẫn là mức LN giữa chu kỳ (DT FY2025 đỉnh: 12.452 nếu TB 2021–25) — C hai chiều, không vào tâm. Selfcheck sổ tạm: lỗi 0; dry-run `dd_ledger_append_center_adj` OK (rev4 center_adj 15.050). **Khuyến nghị: MECH** cho tâm base (0%) + ghi tâm điều chỉnh; FULL chỉ khi có dữ kiện bãi thạch cao / KTPL 2026.
