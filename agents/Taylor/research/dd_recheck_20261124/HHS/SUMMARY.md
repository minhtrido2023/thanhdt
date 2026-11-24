# HHS — pilot rà lại DD đợt 1 (24/11/2026, job Taylor_20261124_094353)

Nguồn: `REPORT_recheck_HHS.md` · calc `calc/calc_recheck.py` (run1 = run2 md5 `bd675399…`, CONTROL tái lập rev7 bằng assert) · skeptic `skeptic/r1.json` · đề xuất sổ `LEDGER_PROPOSAL_HHS.json`.

## (a) Lệch theo luật mới
- **V1 (lỗi thật của rev7):** rev7 ghi độ nhạy ±50/±100bp "≈ 0 đ/cp". Sai: mô hình có pv(y, Ke). Số đo: −167 / −85 / +86 / +174 đ/cp (−1,55…+1,61%). Đã sửa trong bản recheck.
- **D4 dải Ke:** rev7 chưa báo hai đầu 12,3–13,4% ⇒ bổ sung: 11.014 / 10.822. Terminal RONIC: không áp (NAV hữu hạn, NOT_APPLICABLE_FINITE_LIFE). P/E ô tô 6 < 1/Ke 7,4 ⇒ không ngầm thưởng.
- **D3:** không nhận diện được capex tuân thủ trong assumptions/BCTC đã đọc. Nghĩa vụ NƠXH/quỹ đất (NC-II, I.14) + KL 08/KL-TTTP = **cần kiểm chứng**, chưa có số.
- **E15:** Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): **11.014 đ/cp (+1,93%)**.
- **E16:** nguyên văn: **KHÔNG CHẮC (proxy lệch DD, k=0.23–0.26; N hiệu dụng thấp, 2.09)** ⚠ LỢI NHUẬN SỤT? (ROE TTM/5Y=0.05) — asof 2026-11-20.
- **V3/V5/V6/V8:** đã đủ (V6 thêm V_ngắn @12,3% = 4.903 đ/cp). V8 không áp (EXCLUDE); nếu gỡ, đề xuất 2% NAV.

## (b) Tâm / vùng / nhãn
| | rev7 (sổ) | recheck | Δ |
|---|---|---|---|
| Tâm CUM | 10.805 | 10.805 | 0% |
| Vùng | 9.634–12.012 | 9.634–12.012 | 0 |
| Nhãn @ 9.700 (BQ 20/11) | TRONG | TRONG (sát đáy) | không đổi |
Ghi kèm: nhãn lật sang DƯỚI khi r ≤ 13,0% (P10 9.723). Chỉ báo kèm, không dùng cho nhãn.

## (c) Phản biện
`skeptic/r1.json`: **REFUTED (medium)**, cost 0,79 USD. Cơ học đúng: skeptic tự tính Δr được +215 đ/cp, báo cáo ghi +209. Killer: base CK holding 26,63% (N=6) đã bị phép đo v5 (24/11) phủ lên. v5 cho trung vị N=12 là −3,24%, mốc hiện tại 19,7%, đề xuất base 0% ⇒ tâm +7,6…+29,3%. Ngoài ra, phần r5 (EX k=0,734 vs k_base=1; phạm vi CK) vẫn chưa sửa. **Không chạy thêm vòng**, vì bản sửa cần user chốt CK.

## (d) Rủi ro / việc mở
1. **User chốt CK holding** (v5 phương án A: base 0% / 19,7% / stress 37,7%). Đối chiếu cùng mô hình: CK 19,7% ⇒ tâm 11.628 (P10 10.353) DƯỚI; CK 0% ⇒ 13.969 DƯỚI.
2. Sửa EX k + thống nhất phạm vi CK (r5).
3. Định lượng NƠXH/quỹ đất + KL 08.
4. Kết quả lấy ý kiến cổ đông 14–25/12/2026 ⇒ làm lại bản pha loãng.
5. `LEDGER_PROPOSAL_HHS.json` = rev8 `REFUTED_OPEN` trỏ bản recheck. Selfcheck: `MIKE_SRC_ROOT=<worktree> python3 bin/dd_price_zones_selfcheck.py --ledger <bản tạm>` ⇒ lỗi 0. Chạy với root master thì báo 3 lỗi "file không tồn tại", vì file chỉ có trong worktree cho tới khi merge. Mike quyết có áp hay không: tâm không đổi, chỉ thêm E15/E16 + sửa độ nhạy r.

## (e) Khuyến nghị lớp: **FULL** (rev8)
Riêng phần luật mới thì chỉ cần MECH: tâm đổi 0%, nhãn không đổi. Nhưng base đang REFUTED_OPEN hai vòng liền (r5, r1-recheck), cùng một gốc là tham số CK, nên MECH không đóng được. Cần user chốt CK trước, rồi làm rev8 + phản biện đầy đủ.

**Bài học quy trình cho fan-out 7 mã còn lại:**
- Nên kiểm "tham số nền đã bị phép đo mới hơn phủ lên chưa" trước khi chạy skeptic. Bước này rẻ hơn một vòng skeptic.
- Selfcheck ledger trong worktree cần `MIKE_SRC_ROOT`.
