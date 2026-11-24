# FPT — rà lại DD đợt 1 (24/11/2026, job Taylor_20261124_095517)

Nguồn: `REPORT_recheck_FPT.md` (md5 `78b26579…`) · calc `calc/calc_recheck.py` (run1 = run2 md5 `7a1b68e4…`; CONTROL: chạy lại `model_r3.py` ra stdout trùng byte `run1.txt` r3 `51b85a47…`) · skeptic `skeptic/r1.json` · đề xuất sổ `LEDGER_PROPOSAL_FPT.json`.
⚠ `calc_r3/` gốc (assumptions, out, px) đã bị TRIM khỏi git ngày 19/11 (`14ad1c925`). Khôi phục: `git archive 14ad1c925^ agents/Taylor/research/dd_redo_20261105 | tar -x -C /tmp/ddrestore_B`; md5 9 file khớp LOCK_r3.

**Bước 0:** KHÔNG có tham số nền bị phủ. CK FTEL base 0% cùng hướng với v5. r: Δ lãi huy động = 0. RONIC terminal = Ke đã có từ r3. Độ nhạy r đã tính từ mô hình ⇒ chạy skeptic.

## (a) Lệch theo luật mới
- **E15:** Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): **61.176 đ/cp (+6,74%)**.
- **E16:** nguyên văn **KHÔNG CHẮC (N hiệu dụng thấp, 2.46)** — asof 2026-11-20.
- **D4:** dải Ke bổ sung (61.176 / 57.606). Terminal RONIC = Ke đúng. ±50/±100bp khớp r3 đến từng đồng.
- **D3:** không nhận diện capex tuân thủ. Cam kết vốn data center/giáo dục = **cần kiểm chứng**.
- **V6:** bổ sung từ `dd_blend_20261111`: V_ngắn 73.501 / V_dài 69.472, D = 0,056 (không cờ). Caveat: tính ở r của engine, không phải 13,5%.
- **V3/V5:** đã đủ. **V8:** giữ ngoại lệ 5% NAV đã duyệt riêng.

## (b) Tâm / vùng / nhãn
| | r3 (sổ) | recheck | Δ |
|---|---|---|---|
| Tâm | 57.312 | 57.312 | 0% |
| Vùng | 45.270–68.466 | 45.270–68.466 | 0 |
| Nhãn @ 50.800 (06/11) | TRONG | TRONG | không đổi |

## (c) Phản biện
`skeptic/r1.json`: **INCONCLUSIVE (medium)**, 1,04 USD. Cơ học đúng: skeptic tự tính lại core_op 6.705 tỷ và NC 12.233 tỷ, khớp; tái chạy ra 57.312. Đòn 8 (thiếu hạng mục) chưa qua:
- cam kết capex DC/AI chưa đọc (FCF 9T26 −1.077 tỷ);
- quỹ KTPL 1.477 tỷ chưa trừ khỏi NC (−1,4%);
- trích quỹ hằng năm (~−3%, tỷ lệ chưa kiểm);
- ESOP (~−2,5%);
- conv CƠ SỞ 0,75 so với FY25 0,60 (−1,85%);
- tâm còn gồm cổ tức 1.000 đ chốt 30/11.

Chiều lên: g 9% < LFL 13,7% (+3,3%); r 13,5% ở trên dải Ke (theo luật V1, không phải lỗi). Skeptic ước hai chiều gần bù nhau.

## (d) Rủi ro / việc mở
1. Rev4 cần: đọc thuyết minh cam kết vốn Q3/2026 + NQ HĐQT 12 tháng; trừ quỹ KTPL khỏi NC (hoặc độ nhạy); lấy tỷ lệ trích quỹ + ESOP từ NQ ĐHĐCĐ 2026; xét conv CƠ SỞ.
2. Sau GDKHQ cổ tức 30/11: tâm −1.000 đ (cơ học).
3. Lãi LK Q4/25 600 tỷ chưa kiểm (G10). Pháp lý chưa quét sau 01/11.
4. `LEDGER_PROPOSAL_FPT.json` = rev4 `REFUTED_OPEN`. Selfcheck: `MIKE_SRC_ROOT=<worktree>` ⇒ lỗi 0. Tâm không đổi.

## (e) Khuyến nghị lớp: **FULL** (rev4)
Phần luật mới chỉ là MECH (0%), nhưng skeptic mở hạng mục mới. Cộng các khoản trừ thì ≈ −6–7% (ước lượng của skeptic, chưa đo), vượt ngưỡng 5%. Cần Mike quyết có làm rev4 không. Vị thế đang giữ: không đề xuất đổi sizing.
