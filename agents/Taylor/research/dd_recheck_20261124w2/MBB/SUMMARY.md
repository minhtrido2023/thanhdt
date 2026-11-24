# MBB — rà lại DD đợt 2 (24/11/2026, job Taylor_20261124_131354)

Nguồn: `REPORT_recheck_MBB.md` (md5 `fafa135d…`) · calc `calc/calc_recheck.py` (run1 = run2 md5 `51bfb06b…`; CONTROL: stdout `mbb_r3.py` trùng `run2.txt` r3 trừ dòng LOCK) · skeptic `skeptic/r1.json` · E17 `ADJ_CENTER.md` + `adj.json` · đề xuất sổ `LEDGER_PROPOSAL_MBB.json`.
⚠ `calc_r3/` gốc bị TRIM 19/11 (`14ad1c925`). Khôi phục: `git archive 14ad1c925^ agents/Taylor/research/dd_redo_20261105 agents/Taylor/research/dd_MBB_20261031 | tar -x -C /tmp/ddrestore_MBB`; 16/17 md5 khớp LOCK (lệch duy nhất `data/deposit_rate_vn_events.csv` — thêm sự kiện sau 08/11, lãi 12T hiệu dụng 03/11 = 06/11 = 24/11 = 7,40% ⇒ r không đổi).

**Bước 0:** KHÔNG có tham số nền bị phủ (không tầng holding; r Δ = 0; RONIC terminal = Ke từ r3 D1; độ nhạy r tính từ mô hình) ⇒ chạy skeptic.

## (a) Lệch theo luật mới
- **E15:** Tâm @ Ke 12,3%: **23.659 đ/cp (+12,30%)**. **E16:** nguyên văn **KHÔNG CHẮC (N hiệu dụng thấp, 1.93)** (asof 2026-11-20).
- **D4:** dải Ke bổ sung (23.659 / 21.266); terminal RONIC = Ke đúng; ±50/±100bp khớp r3 từng đồng. **D3:** không có capex tuân thủ (nhu cầu vốn quy định nằm ở ROE_T + payout).
- **V6:** chưa có (engine dd_blend không áp cho ngân hàng). **V3/V5:** đã đủ (NARROW, 5F 07/11). **V8 (mới):** 2% NAV.
- Đóng cờ 12 r3 bằng số BCTC HN-Q3: nhóm 2 HN 17.014 tỷ (1,32%), nhóm 2–5 2,99%, bao phủ 84,7% — chưa chạm mốc xấu (20.000 / 3,5% / 75%) nhưng đang tiến về phía đó.

## (b) Tâm / vùng / nhãn
| | r3 (sổ) | recheck | Δ |
|---|---|---|---|
| Tâm | 21.069 | 21.069 | 0% |
| Vùng | 14.729–27.577 | 14.729–27.577 | 0 |
| Nhãn @ 19.250 (06/11) | TRONG | TRONG | không đổi |
| skeptic_final | CONFIRMED (kiểu cũ, backfill) | **REFUTED_OPEN** | hạ nhãn |

## (c) Phản biện
`skeptic/r1.json`: **INCONCLUSIVE (medium)**, 1,02 USD, DD_GENERAL. Cơ học đúng (BVPS 15.594, Ke 12,3% +12,3% khớp, số CP đã gồm quyền mua). Đòn 8: rò LN sang quỹ KTPL ~8,9% LN 2025 (suy từ phần dư LNCPP; −6,5…−11,4%); chênh ROE_T−Ke vĩnh viễn (bỏ = −14,7%, là tham số luật); CAR 30/09/nhu cầu vốn; phát hành riêng lẻ 200 tr CP. Chiều lên: đường ROE 2027 18,5% < TTM 20,7% (+8,5% gồm T17). Tâm không đổi trong recheck (sửa = đổi mô hình) ⇒ không B2.

## (d) Tâm kỳ vọng điều chỉnh (E17)
**20.587 đ/cp (dải 19.245–21.061; −2,29%)**, 3 hạng mục: KTPL C+ (p 0,5 × −5,89%), đường ROE B-neg (p 0,35 × +2,75%), phát hành riêng lẻ B (p 0,5 × −0,51%); chạy lại mô hình tổ hợp. Điều kiện đổi số chính: tỷ lệ trích KTPL thật (NQ ĐHĐCĐ 2026, đọc được ngay) ⇒ tâm adj ≈19.023–21.218; BCTC Q4/26 (chất lượng tài sản, ROE) ±0,8–3,7%; lãi huy động ±50bp −4,5/+4,8%.

## (e) Rủi ro / việc mở
1. Đọc NQ ĐHĐCĐ 2026 MBB (phân phối LN 2025) ⇒ đóng hạng mục KTPL (rẻ nhất, tác động lớn nhất). 2. CAR/Tier1 30/09, phải thu MBV 30/09, pháp lý sau 05/11. 3. "3c chặt" chưa chạy lại trên r3 (thay bằng độ nhạy ROE_T = Ke 17.961).
4. `LEDGER_PROPOSAL_MBB.json` = rev4 `REFUTED_OPEN`, selfcheck `MIKE_SRC_ROOT=<worktree>` lỗi 0. E17 KHÔNG chép vào REPORT_recheck (giữ md5 khớp skeptic r1); dòng E17 nằm ở `ADJ_CENTER.md`.

## (f) Khuyến nghị lớp: **FULL** (rev5 khi có số KTPL thật)
Phần luật mới là MECH (0%); skeptic mở hạng mục KTPL có thể > 5%. Đọc NQ ĐHĐCĐ 2026 trước, rồi quyết rev5. Sizing đề xuất 2% NAV, chưa đạt luật 4 (ngưỡng 17.909).
