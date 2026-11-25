# HPG — rà lại DD đợt 3 (25/11/2026, job Taylor_20261125_032443 → resume Taylor_20261125_053002)

Nguồn: `REPORT_recheck_HPG.md` (md5 `12090efc…`, GIỮ NGUYÊN để khớp skeptic) + `ERRATA_recheck_HPG.md` · calc `calc/calc_recheck.py` (run1 = run2 md5 `dacbd3bc…`; CONTROL hpg_r3 = `calc/ref_hpg_r3_out.txt`) · skeptic `skeptic/r1.json` · E17 `ADJ_CENTER.md` + `adj.json` (`calc/calc_adj.py`, adj_run1 = adj_run2) · đề xuất sổ `LEDGER_PROPOSAL_HPG.json` (rev5).
Calc r3 bị TRIM 19/11, khôi phục `git archive 14ad1c925^`; md5 khớp LOCK (`dd_redo_20261105/HPG/calc_r3/LOCK_md5.txt`).

**Bước 0:** KHÔNG bị phủ (không tầng holding; lãi huy động 7,40% = neo ⇒ r 13,5%; RONIC/g_RI = 0 theo r3; độ nhạy r tính từ mô hình).

## (a) Lệch theo luật mới
- **E15:** Tâm @ Ke 12,3%: **23.625 (+10,72%)**; dải Ke 23.625 / 21.513.
- **E16:** nguyên văn **KHÔNG CHẮC (rẻ…trung tính)** — phân vị [fade 21, hold 60], 120 tháng, N hiệu dụng ≈ 5.4 (thước cơ học, chỉ hiển thị).
- **D3:** capex tuân thủ môi trường chưa có số ⇒ C (cận trên −4,1%). **D4:** văn bản sai (ghi "vốn tăng thêm = Ke"; code: vốn vượt cam kết sinh lời 5,92%) ⇒ ERRATA; áp Ke cho phần vượt ⇒ 22.971 (+7,7%), tham số luật, không vào Σ.
- **V6:** FCFE chuẩn hoá ≤ 0 (DQ2) ⇒ chỉ V_ngắn 12.577; chỉ hiển thị. **V3/V5:** đủ (CK 0,15%; moat NARROW). **V8:** 0% mua mới ở giá tham chiếu; ≤3% NAV nếu dưới luật 4.

## (b) Tâm / vùng / nhãn
| | rev4 (sổ) | recheck rev5 | Δ |
|---|---|---|---|
| Tâm | 21.338 | 21.338 | 0% |
| Vùng | 13.316–28.993 | 13.316–28.993 | 0 |
| Nhãn @ 21.200 (06/11) | TRONG | TRONG | không đổi |

## (c) Phản biện
`skeptic/r1.json`: **CONFIRMED (medium)**, 1,03 USD. Cơ học đúng (BV0/SH khớp BCTC). `missing_items` fail dưới ngưỡng: KTPL (−1,8…−4,4%), capex môi trường (cận trên −4,1%). Không đổi tâm/nhãn ⇒ không chạy vòng 2. Sổ: skeptic_final FIXED_UNVERIFIED (bước 1 §E14.8), bước 2 = `dd_ledger_append_confirmed.py --ticker HPG --verdict …/HPG/skeptic/r1.json`.

## (d) Tâm kỳ vọng điều chỉnh (E17 — vì hạng mục thiếu chưa đóng)
**20.203 đ/cp (dải 19.823–20.956; −5,32% tổ hợp)**, 4 hạng mục (1 A + 3 B): trích KTPL + thù lao 2,60% LNST (A, −2,05pp) · đếm trùng cam kết vốn 30/06 với XDCB (B, −0,76) · ETR thép thực 6,55% (B, −1,07) · nhánh TỐT đếm trùng lợi ích capex (B, −1,56). Bảng điều kiện đổi số: ADJ_CENTER.md §3 — quan trọng nhất: capex môi trường trong cam kết (đến −4,1%), tỷ lệ KTPL/thù lao 2026 (NQ ĐHĐCĐ 2027), ETR thép cả năm 2026, phân loại thuế DQ2 (±3–4%).

## (e) Rủi ro / việc mở · khuyến nghị lớp
Cổ tức 2026 15% chưa rõ hình thức (cơ học khi GDKHQ). WARNING quản trị TLSH (chỉ cảnh báo). Selfcheck sổ tạm (`/tmp/ledger_hpg_w3a.json`, 157 entry): **lỗi 0**; dry-run `dd_ledger_append_center_adj` OK (rev6 center_adj 20.203 [19.823–20.956]). **Khuyến nghị: MECH** (tâm base 0%) + ghi tâm điều chỉnh; FULL khi có TM cam kết vốn 31/12/2026 hoặc dữ kiện capex môi trường.
