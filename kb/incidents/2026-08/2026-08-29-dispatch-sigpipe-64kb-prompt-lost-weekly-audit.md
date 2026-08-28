# 2026-08-29 — `dispatch.sh` chết rc=141 (SIGPIPE) với prompt > 64KB ⇒ mất trọn 1 tuần weekly ops audit

**Status**: fixed
**Phát hiện bởi**: weekly ops audit 2026-08-29 (mục 1, đọc `logs/weekly_ops_audit.log` + `logs/resume_pending.log`)
**Ảnh hưởng**: weekly ops audit 2026-08-22 KHÔNG bao giờ chạy. Không có báo động — chỉ còn 1 dòng
WARNING trong log của lần chạy tuần kế tiếp ("không tìm thấy decision 'weekly-ops-audit' nào trong
9 ngày qua").

## Chuỗi sự kiện
1. `2026-08-22T04:33` job `Mike_20260821_213356` (weekly ops audit) hết turn budget 80 →
   `status=maxturns_pending`, ghi `bus/pending_resumes/` đúng thiết kế (MIKE.md §6b).
2. `resume_pending.py` gọi lại `dispatch.sh` 3 lần (21:50, 22:20, 22:50 UTC). **Cả 3 lần rc=141.**
3. Sau lần 3: `GIVE-UP Mike (orig_job=Mike_20260821_213356): dispatch fail 3 lần — BỎ record`.
   Việc mất hẳn, không ai được báo.

## Root cause
`bin/dispatch.sh` chạy dưới `set -euo pipefail` (dòng 106). Dòng 1225:

```sh
_psum="$(printf '%s' "$prompt" | head -c 160 | tr '\n\t' '  ')"
```

`head -c 160` đọc đủ 160 byte rồi THOÁT. Nếu prompt lớn hơn buffer pipe của kernel (**64KiB**),
`printf` còn đang ghi → nhận **SIGPIPE** → pipeline trả **141** → `pipefail` truyền 141 lên phép
gán → `set -e` giết dispatch.sh **trước khi job kịp khởi động**. Prompt nhỏ hơn 64KiB thì lọt hết
vào buffer, `printf` xong trước khi `head` thoát ⇒ không bao giờ lỗi. Đó là lý do lỗi chỉ cắn đúng
weekly ops audit: prompt của nó nối thêm `tail -200` output selfcheck thật.

Đo ngưỡng (bash, cùng cấu trúc lệnh):

| kích thước prompt | rc |
|---|---|
| 60.000 | 0 |
| 64.000 | 0 |
| 65.000 | 0 |
| **70.000** | **141** |
| 100.000 | 141 |

Dòng 1600 (`_dp="$(printf '%s' "$prompt" | head -c 120 …)"`) cùng lớp lỗi, chưa cắn nhưng cùng
điều kiện kích hoạt.

## Fix
`|| true` ở cả 2 site (chỉ nuốt exit-code của SIGPIPE; giá trị cắt vẫn được gán đúng vì command
substitution đã thu đủ 160/120 byte đầu). `head -c` đọc THẲNG FILE (dòng 890, 1403) không thuộc
lớp lỗi này — không có producer để nhận SIGPIPE, không sửa.

## Verify (chạy thật, không đọc lại code)
- Tái hiện lỗi cũ bằng bash isolate: rc=141 tại n=70.000 (bảng trên).
- Sau fix: `DISPATCH_FROM=user bin/dispatch.sh Mike "<70.000 ký tự>" --bg` → **rc=0**, job
  `Mike_20260828_205730` khởi động thật (đã `jobs.sh cancel` ngay, 9 process verified dead).
- `bash -n bin/dispatch.sh` OK.

## Bài học
Đúng lớp lỗi mà `shellcheck_gate.sh` (§15) sinh ra để chặn nhưng ShellCheck KHÔNG bắt: đây không
phải lỗi quoting, mà là tương tác `pipefail` × SIGPIPE × kích thước dữ liệu. Chỉ lộ ra khi input
vượt một ngưỡng của kernel — không test nào ở kích thước "bình thường" chạm tới.

Cùng ngày, cùng tinh thần §29: thông điệp lỗi mà `resume_pending.py` ghi (`rc=141` + argv) là thứ
DUY NHẤT cho phép truy ra nguyên nhân — nếu nó nuốt rc như bản trước 2026-08-03 thì tuần audit này
cũng sẽ không tìm ra.
