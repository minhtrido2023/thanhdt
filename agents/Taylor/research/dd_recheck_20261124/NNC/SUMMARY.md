# NNC — rà lại DD đợt 1 (24/11/2026, job Taylor_20261124_095517)

Nguồn: `REPORT_recheck_NNC.md` (md5 `53c3d244…`) · calc `calc/calc_recheck.py` (run1 = run2 md5 `a4c910d5…`; CONTROL: stdout r3 trùng byte `857c7adb…`) · skeptic `skeptic/r1.json` · đề xuất sổ `LEDGER_PROPOSAL_NNC.json`.
⚠ Output/assumptions r3 cùng engine dd_NNC/dd_MVC đã bị TRIM khỏi git (19/11). Khôi phục bằng `git archive 14ad1c925^` / `ef7472f56^` / `bffae9c42^` vào `/tmp/ddrestore_B`; md5 của 14 file đầu vào khớp LOCK_r3.

**Bước 0:** KHÔNG có tham số nền bị phủ. Holding chéo MVC base 0% cùng hướng với v5. r: Δ = 0. Terminal: không áp (mỏ hữu hạn tới 2043). Độ nhạy r: r3 thiếu, nay đã tính ⇒ chạy skeptic.

## (a) Lệch theo luật mới
- **V1 (thiếu ở r3):** chưa có ±50/±100bp tính bằng đ/cp ⇒ bổ sung từ mô hình: −1.847 / −944 / +988 / +2.024 đ/cp (−3,01…+3,30%).
- **E15:** Tâm @ Ke 12,3%: **63.725 đ/cp (+4,00%)**.
- **E16:** nguyên văn **KHÔNG CHẮC (N hiệu dụng thấp, 1.81)** ⚠ ĐỈNH LỢI NHUẬN? (ROE TTM/5Y=1.86).
- **D4:** dải Ke 63.725 / 61.467; terminal không áp.
- **D3:** PHMT 4,50 tỷ đã trừ (số dư). Chi PHMT/đóng mỏ phát sinh thêm và tiền cấp quyền = cần kiểm chứng. Skeptic: PHMT không trọng yếu (hệ số chiết khấu ≈ 0,12 tại 2043).
- **V6:** V_ngắn 68.074 / V_dài 68.527, D = 0,007 (không cờ). Lấy từ dd_blend, r engine.
- **V3/V5:** đã đủ (NARROW · LOCATION). **V8:** giữ ngoại lệ 5% NAV đã duyệt riêng.

## (b) Tâm / vùng / nhãn
| | r3 (sổ) | recheck | Δ |
|---|---|---|---|
| Tâm | 61.273 | 61.273 | 0% |
| Vùng | 30.375–95.341 | 30.375–95.341 | 0 |
| Nhãn @ 47.200 (06/11) | TRONG, luật 4 ĐẠT | TRONG, luật 4 ĐẠT | không đổi |

## (c) Phản biện
`skeptic/r1.json`: **INCONCLUSIVE (medium)**, 1,21 USD. Cơ học đúng: CONTROL trùng byte; skeptic tự query BQ Q3/26 (cash 25,47, nợ 5,00 + 69,89, OShares 21,92 tr, BVPS 29.915) và khớp. Đòn 8 chưa qua:
- trích quỹ KTPL hằng năm 2027–2043 chưa trừ: −3,6…−7,2% (ước lượng của skeptic với tỷ lệ 5–10%; tỷ lệ của NNC chưa có nguồn);
- "capex duy trì ≈ khấu hao" chưa có nguồn, trong khi capex thực 23–54 tỷ/năm (mua máy từ NHC);
- truy thu Núi Nhỏ ~42 tỷ có nằm trong dự phòng 22,37 không (≤1,5%).

## (d) Rủi ro / việc mở
1. Rev mới cần: tỷ lệ trích KTPL (NQ ĐHĐCĐ) → trừ trong DCF; đối chiếu capex với khấu hao 5 năm từ BCTC; làm rõ truy thu Núi Nhỏ.
2. MVC r6 còn lỗi trần chu kỳ chưa vá (ảnh hưởng chân MVC trong NNC — skeptic xếp vào chiều lên).
3. Errata r3: độ nhạy CHẶT-3C chưa chạy lại; chưa kiểm PDF 322,44/22,37/16,78. Pháp lý chưa quét sau 05/11.
4. `LEDGER_PROPOSAL_NNC.json` = rev6 `REFUTED_OPEN`. Selfcheck `MIKE_SRC_ROOT=<worktree>` ⇒ lỗi 0. Tâm không đổi.

## (e) Khuyến nghị lớp: **FULL** (rev mới)
Phần luật mới chỉ là MECH (0%). Nhưng hai hạng mục skeptic mở có thể kéo tâm > −5% (ước lượng, chưa đo). Ngay cả bản −7,2% (≈ 56.860, ước lượng) vẫn cho nhãn TRONG ở giá 47.200; luật 4 thì sát ngưỡng (0,85 × 56.860 ≈ 48.330, ước lượng). Vị thế đang giữ: không đề xuất đổi sizing. Mike quyết.
