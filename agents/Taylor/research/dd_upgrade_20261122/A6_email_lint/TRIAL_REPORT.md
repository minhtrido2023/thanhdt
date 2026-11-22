# A6 — TRIAL_REPORT (lint `send_dd_report_email.py`, 2026-11-22)

Đo bằng: `python3 /tmp/a6_trial.py top` (10 `*_DD_investor_report_*.md` mới nhất theo ngày trong tên file, trong
`agents/Taylor/research/dd_*/investor_report/`) → output thô `trial_top10_raw.txt`; ca thêm → `trial_extra_raw.txt`.
Độc lập: `grep -ciE` cùng danh sách cụm cho 10 bản = 0 hit (cũng khớp lint).

## 10 bản mới nhất
| Bản | Lint bắt | Đánh giá thủ công |
|---|---|---|
| PAT_20261114 (dd_PAT_20261114) | MD_LEDGER_MISMATCH vùng md 56.600–76.600 ≠ sổ PAT#2 41.000–74.900 | **ĐÁNG** — md là bản cũ, sổ đã rev2 |
| PAT_20261114 (dd_PAT_objective) | — (chỉ cảnh báo skeptic≠CONFIRMED) | đúng, sạch |
| PNJ_20261114 | — (cảnh báo skeptic) | đúng |
| QTP_20261117 | MD_LEDGER_MISMATCH tâm 13.140 ≠ sổ#3 7.701; vùng 10.390–16.490 ≠ 6.300–8.900 | **ĐÁNG** (2/2) — md = rev2, sổ rev3 sửa lớn (dự án khí thải) |
| DBC / LLM / POW_20261118, TTA_20261120, VCB_20261117 | — (cảnh báo skeptic) | đúng |
| VLB_20261122 | MD_LEDGER_MISMATCH vùng md 41.400–56.000 (tâm ±15%) ≠ sổ#2 33.336–65.385 (tâm 48.735 khớp) | **ĐÁNG, nhưng biên**: lệch ĐỊNH NGHĨA vùng md↔sổ (không phải số cũ). Nếu coi là báo giả thì 1/10 |

Tổng: 10 bản → 4 vi phạm ở 3 bản (+VLB=4 bản có cờ). **Báo giả: 0/10 (tối đa 1/10 nếu tính VLB)** — đạt mục tiêu ≤1/10.
L18 và tên nội bộ: 0 hit/10 bản (10 bản gần đây đã sạch — khớp grep độc lập).

## Ca NNC & bản bẩn cũ (kiểm tra độ nhạy, ngoài 10 bản)
| Bản | Lint bắt | Đánh giá |
|---|---|---|
| **NNC_20261031** | MD_LEDGER_MISMATCH vùng 59.000–79.000 ≠ sổ NNC#5 (11-03) 30.375–95.341 → **ca NNC BỊ BẮT**; L18 "đính chính" ×3 (dòng 331) | vùng: ĐÁNG. L18 dòng 331: **báo giả bối cảnh** ("đính chính" nói về đính chính nguồn dữ liệu công ty, không phải lỗi của báo cáo) |
| TV1 v1/v2/v3 sent | L18: 3 / 15 / 34 vi phạm (BẢN ĐÍNH CHÍNH, thay bản, vòng N, bản r6…) ; mismatch tâm/vùng vs sổ rev6 | ĐÁNG (đúng ca gốc của luật 18) |
| HPG_v3 | L18 "thay bản gửi trước", "đã sửa"; mismatch tâm/vùng vs sổ#4 | ĐÁNG |
| SCL | 20: nhãn NON/QUALIFY/AMBIGUOUS, `build_report.py`, "sai sót trình bày lặp lại" | NON/QUALIFY/AMBIGUOUS, `.py`: ĐÁNG (luật 1/12/4). "sai sót" ở dòng 242 là rủi ro kiểm toán, **báo giả bối cảnh** |
| DCM_20261104 | (đã sửa) trước chỉnh: "tâm md 1,316" = báo giả (số −1.316 đ/cp trong câu khác) | sau chỉnh: 0 vi phạm |

## Báo giả đã gặp khi dựng & đã chỉnh regex
1. VCP: "tâm" đầu tiên là dòng độ nhạy (38.058) thay vì dòng tiêu đề (40.273, cách >25 ký tự, có "1 tỷ" xen giữa) → cửa sổ 90 ký tự, lấy số ≥1000 đầu tiên.
2. NNC dòng 144: "tâm … 2026" (năm) → loại số 4 chữ 1990–2100 không đơn vị.
3. DCM dòng 125: "−1.316 đ/cp" sau "tâm" ở câu khác → cắt cửa sổ tại ". "/"; ", bỏ số có dấu −/+.

## Giới hạn còn lại (nêu thẳng)
- Chỉ so **tâm/vùng ĐẦU TIÊN** trong md với sổ (tiêu đề); số tâm/vùng thứ cấp không kiểm.
- Lệch định nghĩa vùng (VLB) cũng báo — Mike quyết định có chặn hay không (hiện gửi thật CHỈ cảnh báo vì `DD_LINT_BLOCK=False`).
- L18 `trước đây`, `đã sửa`, `sai sót`, `đính chính` bắt theo chuỗi — có thể báo giả khi ngữ cảnh khác nghĩa (2 ca trên). Không bịa thêm cụm ngoài luật 18 (chưa thêm "bản trước/phiên bản cũ/đã sửa lỗi": luật không liệt kê; "đã sửa" phủ "đã sửa lỗi").
- Tên nội bộ: thêm SpaceX/ZaloPay (luật 4) và job_id; "NON/QUALIFY/AMBIGUOUS/tên agent" chỉ khớp khi VIẾT HOA/đúng hoa-thường để tránh "non trẻ".
- Chưa kiểm tiêu đề thân email ngoài `--subject`.

## Nộp
- File skill (ngoài git) sửa; sao lưu `send_dd_report_email.py.bak_20261122`. Diff: `bin/send_dd_report_email.py.A6.diff` (worktree) .
- Selfcheck `bin/dd_email_lint_selfcheck.py`: 43 PASS / 0 FAIL ở `env -u TZ` và `TZ=Pacific/Kiritimati` (`selfcheck_*_raw.txt`).
- KHÔNG gửi email; chỉ `--dry-run`.
