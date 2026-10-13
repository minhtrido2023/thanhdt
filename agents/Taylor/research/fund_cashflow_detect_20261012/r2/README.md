# Quỹ mở bước 2 — vòng 2 (sửa theo arch-review `ea9d6969a`)

Job `Taylor_20261012_162001` (resume của `Taylor_20261012_141756`). Nhánh
`feat/fund-cashflow-detect-20261012`, worktree `agents/Taylor/wt-fundcf-1012`. Không merge, không
push, không tạo `data/cash_identity_acks.json` thật.

## File ở đây
| File | Là gì |
|---|---|
| `repro_r2.py` / `.txt` | 13 ca tái hiện của reviewer (R1–R13) chạy trên code mới, kèm nhãn từng ca |
| `mutants_r2.py`, `run_r2.py` | 4 bộ mutant chuyển sang code vòng 2: `rev` (71, của reviewer), `new` (66, viết cho code mới), `step2` (86) + `ar3` (71 áp được) = bộ 157 của vòng 1 |
| `out_{rev,new,step2,ar3}_final.txt`, `results_*.json` | lượt mutant CUỐI, trên code đã commit |
| `out_*_pass1.txt`, `out_*_pass2.txt` | hai lượt trước khi thêm test giết mutant sống (giữ để thấy quá trình) |
| `acceptance/1_numbers_unchanged.txt` | nghiệm thu 1 — tỉ suất 4 mốc, đọc `data/` thật (chỉ đọc) |
| `acceptance/4_acks_on_copy.py` / `.txt` | nghiệm thu 4 — áp `../proposed_acks.json` trên bản sao dữ liệu, so với master mọi ngày báo cáo |
| `acceptance/56_demo.py` / `.txt` | nghiệm thu 5 + 6 — nguyên văn đầu ra của cổng và của đẳng thức trên dữ liệu giả |
| `acceptance/7_selfcheck_3tz.txt` | 10 selfcheck liên quan × 3 môi trường TZ (`env -u TZ`, New York, Kiritimati) |
| `broad_scan_r2/` | quét rộng §23 trong sandbox (27 selfcheck, bỏ `nav_scripts_2account_selfcheck.py`) |
| `explore_real.py`, `explore_gaps.py` | thăm dò dữ liệu thật trước khi sửa C1 (chỉ đọc) |

## Chạy lại
```bash
W=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-fundcf-1012
python3 repro_r2.py
python3 run_r2.py rev            # hoặc new | step2 | ar3; thêm --dry để chỉ kiểm chuỗi còn áp được
python3 acceptance/56_demo.py $W/bin
python3 acceptance/4_acks_on_copy.py $W/bin /home/trido/thanhdt/WorkingClaude ../proposed_acks.json
```
Bộ mutant cần dữ liệu giả của reviewer ở `/tmp/archrev_fcf/SEED` (thư mục tạm — mất thì dựng lại
bằng `../arch_review_ea9d6969a/run.py`).

## Điều cần biết khi đọc số
- Bộ `ar3` có 76 định nghĩa, 5 cái (B01, B02, B03, B08, B09) không áp được từ vòng 1 vì đoạn code
  chúng nhắm tới đã bị viết lại ở bước 1 — không phải mutant sống.
- Mutant còn sống: N01, N16, N34, G06 (reviewer đã xếp "tương đương/biên") và X10 (mutant đối
  chứng cố ý không đổi hành vi, để kiểm bộ chạy không báo "chết" bừa).
- ZaloPay có thêm MỘT cửa sổ mở (08-27 → 08-28, +20 MBB ngoài lệnh) mà vòng 1 không báo: hệ quả
  trực tiếp của sửa C1. Bản đề xuất xác nhận có sẵn bản ghi cho nó.
