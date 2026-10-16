# Khoá cơ học "giữ CAPIT margin" — job Taylor_20261013_114453

Nhánh `feat/capit-margin-hold-lock-20261013` (repo mike, CHƯA merge). Luật + lý do giữ:
`kb/projects/capit-margin-hold-20261013.md`. Cách dùng: docstring `bin/capit_margin_hold.py`.

## Cái gì ở đâu
| File | Vai trò |
|---|---|
| `bin/capit_margin_hold.py` | đọc/bật/gỡ file giữ `<WC>/data/CAPIT_MARGIN_HOLD.json` |
| `bin/approve_margin_day.py` | đang giữ ⇒ từ chối (rc 4); lối vượt duy nhất `--override-hold` |
| `bin/approve_plan_simple.sh` | đang giữ ⇒ không gọi approve_margin_day.py, báo đúng điều xảy ra 09:05 |
| `bin/send_plan_report.sh` | đang giữ + plan có lệnh đòn bẩy ⇒ dòng 🔒 trong khối margin |
| `bin/capit_margin_hold_selfcheck.py` | 127 ca, chạy script thật trong cây giả /tmp |
| `mutants.py` (thư mục này) | 50 mutant có tên |

## PHÁT HIỆN CẦN USER/MIKE QUYẾT — "không cấp margin" KHÔNG phải "chỉ tắt vay"
Thiếu bản duyệt ngày, lúc 09:05 (đọc code `trading_bot` 2026-10-13, selfcheck nhóm H chạy lại):
1. `trading_bot/plan.py:1263-1271` (`_enforce_margin_day_approval`) gỡ `lever_f`/`loan_package_id`,
   KHÔNG đổi `qty` (docstring `apply_capit_lever` `plan.py:1336-1339`: "KHÔNG đụng tới sizing/qty").
2. Plan đã sizing ×1,3 (tầng sinh plan đọc `capit_slot_target_vnd_levered`) nên sau đó:
   - `trading_bot/plan_funding_gate.py:392` trả `BLOCK` khi Σ MUA > sức mua đo sống ⇒
     `bot_execute.py:697-701` `continue` trước khi tạo `Executor` ⇒ KHÔNG lệnh nào của account đi
     ra (kể cả lệnh không đòn bẩy, kể cả lệnh bán);
   - hoặc đủ sức mua ⇒ các lệnh CAPIT mua ĐỦ khối lượng ×1,3 bằng gói mặc định của account.
Tôi KHÔNG sửa `trading_bot`. Khoá vẫn đúng chiều (không bản duyệt margin nào được tạo), và cả ba
nơi báo đều nói thật hai hệ quả trên. Việc còn thiếu để lệnh giữ "sạch": tầng SIZING phải biết đang
giữ (vd `golive_recommend_v23.py` đặt `capit_lever.active=false` khi có file giữ ⇒ plan sizing 1,0×).
Hiện lever không active (dd52 −10,7% > −20%) nên chưa có plan nào rơi vào ca này.

## Việc phải làm CÙNG LÚC bật giữ (repo ngoài, tôi không sửa)
`capit_lever_selfcheck.py` nhóm L exec khối margin của `send_plan_report.sh` ⇒ đọc file giữ THẬT.
Bật giữ là L2 + L4 đỏ (`capit_lever_selfcheck_branch_bin_HOLD_ON_unpatched.txt`). Bản vá ghim trạng
thái giữ + thêm 2 ca: `capit_lever_selfcheck_pin_hold.patch` (`git apply --check` sạch trên repo
ngoài; đã chạy trong cây symlink: 211 PASS dù có hay không file giữ).

## Tái lập
```bash
B=/tmp/cmh_baseline_master; mkdir -p $B
for f in approve_margin_day.py approve_plan_simple.sh send_plan_report.sh; do git show "master:bin/$f" > "$B/$f"; done
CMH_BASELINE_DIR=$B python3 bin/capit_margin_hold_selfcheck.py            # + env -u TZ, TZ=America/New_York
CMH_BASELINE_DIR=$B python3 agents/Taylor/research/capit_margin_hold_lock_20261013/mutants.py
```
Nhóm F (cần `CMH_BASELINE_DIR`) so bản master ↔ bản nhánh: rc, stdout, stderr, bus, Discord, file ghi
ra giống hệt ở các ca "không giữ" và "plan không có lệnh đòn bẩy" — sau khi che dấu giờ
(`YYYY-MM-DDTHH:MM:SS`, `HH:MM ICT`) và đường dẫn cây giả `/tmp/cmh_sb_*`.

## Kết quả đã lưu
`selfcheck_tz_{ict,unset,newyork,kiritimati}.txt` · `mutants_run.txt` · `related_selfchecks.txt` ·
`capit_lever_selfcheck_*.txt`.
