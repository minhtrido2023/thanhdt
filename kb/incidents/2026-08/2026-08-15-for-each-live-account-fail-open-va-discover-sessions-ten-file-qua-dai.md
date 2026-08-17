# 2026-08-15 — Weekly ops audit: 2 lỗi IM LẶNG (checker bỏ qua cả 2 account rc=0; discover_sessions chết cả lượt)

**Nguồn phát hiện:** weekly_ops_audit.sh (job `Mike_20260814_212442`), mục 1 — sweep
`bin/cron_health_check.py` + đọc log thật. Cả hai đều KHÔNG có ai báo, KHÔNG hiện ra ở bất kỳ
alert nào; đúng loại "log nói đã chạy, thực tế không làm gì" mà mandate rà soát tuần nhắm tới.

Cả hai đều nằm trong ranh giới tự sửa (script checker/tooling fleet — không chạm trade plan,
trading_rules.json, logic đặt lệnh, dòng cron thực thi, xoá dữ liệu, BOT_STOP).

---

## Bug A — `bin/for_each_live_account.sh` FAIL-OPEN: `trading_bot.config` hỏng ⇒ "không có account nào" ⇒ exit 0

**Hiện tượng (bằng chứng thật, `logs/ops_health.log:2802` + `logs/preflight.log:598`):**

```
appended status/ops-health-check-SpaceX-2026-08-13 for Mike
Traceback (most recent call last):
  File "/home/trido/thanhdt/WorkingClaude/trading_bot/config.py", line 121
    <<<<<<< Updated upstream
SyntaxError: invalid syntax
[for_each_live_account] KHÔNG có account nào enabled=true/mode=live/broker=dnse — không chạy gì.
```

**Root cause:** `LABELS="$(... python3 -c "from trading_bot.config import live_dnse_labels ...")"`
— exit code của command substitution không được kiểm (script dùng `set -uo pipefail`, KHÔNG có
`-e`). Python chết ⇒ `LABELS` rỗng ⇒ rơi vào đúng nhánh "cấu hình thật sự trống" ⇒ in 1 dòng ra
stderr rồi **`exit 0`**. Script lẫn lộn hai tình huống khác hẳn nhau: **"đọc không được danh
sách"** (lỗi) vs **"đọc được, danh sách rỗng"** (cấu hình hợp lệ).

**Ảnh hưởng đo được:** đây là điểm vào DUY NHẤT của **6 dòng cron** —
`send_plan_report.sh` (14:00 + 16:00 UTC), `ops_health_check.sh` (01:20 + 05:45),
`preflight_check.sh` (01:45), `eod_trading_report.sh` (12:10). Trong sự cố conflict-marker
2026-08-14 (`2026-08-14-git-stash-conflict-markers-giet-bot-ca-2-account.md`), ngoài việc 2 bot
chết, **toàn bộ 6 checker này cũng bị bỏ qua cho CẢ 2 account mà cron thấy rc=0** — nghĩa là
chính các lớp giám sát lẽ ra phải phát hiện sự cố cũng bị vô hiệu cùng lúc, im lặng. File sự cố
08-14 ghi phần bot chết, KHÔNG ghi kênh vô hiệu hoá này.

**Fix:** tách tường minh 2 nhánh — `if ! LABELS="$(...)"; then` in thông báo nêu rõ script nào bị
bỏ qua + cách kiểm tra 1 dòng, gọi `bin/notify.sh`, **`exit 1`** (để cron_health_check + cron mail
nhìn thấy). Nhánh "danh sách rỗng thật" giữ nguyên `exit 0` như cũ.

**Verify (chạy thật trên cây tạm có `config.py` chứa đúng conflict marker của 08-14):**

| Ca | Kỳ vọng | Thực tế |
|---|---|---|
| `config.py` hỏng (conflict marker) | rc≠0 + báo rõ | **rc=1**, in "BỎ QUA … cho MỌI account" |
| `config.py` OK, 2 account | rc=0, chạy 2 lần | **rc=0**, chạy SpaceX + ZaloPay |
| `config.py` OK, danh sách rỗng | rc=0, không chạy gì | **rc=0**, giữ nguyên hành vi cũ |

Cộng thêm chạy thật trên config PRODUCTION (`bin/for_each_live_account.sh /bin/echo`) → liệt kê
đúng ZaloPay + SpaceX, rc=0. `bash -n` + `shellcheck` sạch.

---

## Bug B — `bin/discover_sessions.py` chết CẢ LƯỢT vì tên session dài (OSError ENAMETOOLONG)

**Hiện tượng (`logs/discover.log:22620`, 2026-08-14):**

```
File "bin/discover_sessions.py", line 181, in main
    with open(tmp, "w", encoding="utf-8") as f:
OSError: [Errno 36] File name too long: '.../bus/registry/.Audit_ch_nh_th_c__read-only__commit_d5c1cc5e…VERDICT_JSON_.tmp'
```

**Root cause:** `safe()` (dòng 88) làm sạch KÝ TỰ nhưng không giới hạn ĐỘ DÀI. Một phiên headless
được đặt tên bằng cả prompt dispatch (456 ký tự sau khi sanitize) ⇒ tên file 461 byte > trần 255
byte của ext4. Vì `open()` nằm trong vòng lặp không bắt lỗi, **cả lượt quét chết** — mọi session
khác trong chu kỳ đó không được đăng ký (registry thiếu, `fleet_status` sai trong 10 phút).

**Fix:** hằng `LABEL_MAX = 180` + cắt trong `safe()`. Đặt trong `safe()` (chứ không tại chỗ ghi
file) là CỐ Ý: cả 2 call-site — `resolve()` (hook tra ngược id) và `main()` (đăng ký) — đều đi qua
đây nên đăng ký và tra cứu không bao giờ lệch nhau. Cơ chế de-dup `_<pid>` sẵn có xử lý trùng sau
khi cắt.

**Verify:** tái hiện đúng label 456 ký tự trong log → `safe()` trả 180 ký tự, `open()` tên file
185 byte **thành công**; `resolve()` và `main()` cho cùng kết quả; chạy thật
`bin/discover_sessions.py --exclude tri` → rc=0, đăng ký session bình thường.

---

**Bài học chung (cùng họ với `coding_guidelines.md` §28):** hai bug khác nhau về cơ chế nhưng cùng
một hình dạng — **một điều kiện LỖI bị nhào nặn thành một kết quả BÌNH THƯỜNG** ("không đọc được"
→ "không có gì để làm"; và một record hỏng → giết cả lượt thay vì bỏ qua 1 record). Khi viết
checker/script quét: phân biệt tường minh *không lấy được dữ liệu* với *dữ liệu rỗng*, và đừng để
một phần tử hỏng phá cả vòng lặp.
