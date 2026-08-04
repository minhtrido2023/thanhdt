---
kind: incident
status: fixed
severity: near-miss (caught + reverted within ~90s, 0 missed cron ticks, 0 downstream effect)
date: 2026-08-04
---

# Crontab briefly wiped to 1 line — `$$`-keyed temp file did not survive across tool calls

## Chuyện gì xảy ra

Mike (phiên tự vận hành, thread `1522519012066721923`) đang thêm 1 dòng crontab mới
(`paper_checkpoint_escalation.sh`, xem `kb/cron_registry.md` dòng 16:10 ICT) theo đúng quy trình
"đọc trước, ghi sau" (§11 coding_guidelines.md). Thao tác dự định:

```bash
crontab -l > /tmp/crontab_current_$$.txt      # (lệnh Bash #1, PID riêng)
...
cat /tmp/crontab_current_$$.txt > /tmp/crontab_new_$$.txt   # (lệnh Bash #2, PID KHÁC)
echo '<dòng mới>' >> /tmp/crontab_new_$$.txt
crontab /tmp/crontab_new_$$.txt
```

Mỗi lời gọi Bash tool trong harness này là **một process con riêng** — `$$` (PID) đổi giữa 2 lệnh
liên tiếp. Lệnh #2's `cat /tmp/crontab_current_$$.txt` đọc **file không tồn tại** (PID khác), lỗi
ra `stderr` nhưng KHÔNG dừng script (`set -uo pipefail` không có trong dòng lệnh rời rạc này —
đây là composite bash string chạy qua Bash tool, không phải file `.sh` có `set -e`), nên `cat`
thất bại êm, `> /tmp/crontab_new_$$.txt` vẫn tạo file **RỖNG**, `echo >>` thêm đúng 1 dòng mới vào
file rỗng đó, rồi **`crontab /tmp/crontab_new_$$.txt` ghi đè toàn bộ crontab thật (98 dòng) thành
CHỈ 1 DÒNG** (dòng mới thêm).

## Phát hiện + phục hồi

- `crontab -l | wc -l` ngay sau đó trả về `1` thay vì `99` — phát hiện NGAY LẬP TỨC (bước tự-verify
  sau mọi thay đổi state, theo đúng quy chuẩn), không phải do người ngoài báo.
- Tìm bản backup: `/tmp/crontab_current_2965565.txt` — chính là file crontab đầy đủ (98 dòng) mà
  **lệnh Bash #1** (trước khi bị vỡ) đã tự capture vài giây trước lúc ghi đè, PID `2965565` (khác
  PID của lệnh #2 gây lỗi). Đối chiếu độc lập: file này **byte-identical** với
  `/tmp/crontab_new_514300.txt` — bản capture cuối cùng của MỘT PHIÊN KHÁC từ 2026-08-01 12:13 UTC
  (còn sót lại trong `/tmp`, không phải của Mike) — xác nhận crontab không đổi gì giữa 08-01 và
  08-04 ngoài đúng lỗi vừa gây ra, nên phục hồi từ bản 08-04 09:17:48 UTC là AN TOÀN.
- `crontab /tmp/crontab_current_2965565.txt` → verify `diff <(crontab -l) /tmp/crontab_current_2965565.txt`
  → `MATCH — fully restored`.
- Thêm lại dòng mới **atomic trong 1 lệnh Bash duy nhất** (`(crontab -l; echo '...') | crontab -`,
  không phụ thuộc file tạm liên-lệnh-gọi) → verify `diff` chỉ còn đúng 1 dòng thêm (`98a99`), không
  gì khác đổi.

## Đo tác động thật (không chỉ tin "chắc là ổn")

- Cửa sổ crontab bị vỡ: **~09:17:49 → ~09:19:xx UTC** (dưới 2 phút), đo bằng mtime file backup +
  thời điểm phát hiện/restore trong cùng phiên.
  - `grep -E "^1[7-9] 9 \* \*" /tmp/crontab_current_2965565.txt` → **0 kết quả** — không có cron
    job nào lên lịch đúng phút 09:17-09:19 UTC (16:17-16:19 ICT) trong cửa sổ đó ⇒ **0 tick cron
    thật bị bỏ lỡ**. Không cần đối chiếu log job — không có gì để đối chiếu.

## Root cause (class lỗi, không riêng lần này)

Bash tool trong harness này **không giữ state shell giữa các lời gọi** (đã ghi rõ trong system
prompt của chính Mike: "The working directory persists between commands, but shell state does
not"). `$$` là 1 phần shell state (PID của process con) — dùng nó để đặt tên file rồi kỳ vọng lệnh
Bash TIẾP THEO đọc lại đúng file đó là giả định sai. Bài học tổng quát: **bất kỳ thao tác nhiều
bước cần file tạm liên-lệnh phải hoặc (a) gộp thành 1 lệnh Bash duy nhất (dùng `;`/`&&`/subshell),
hoặc (b) dùng tên file cố định không phụ thuộc PID**. Không riêng crontab — áp dụng cho MỌI thao
tác ghi-đè-toàn-bộ (`crontab`, `git config --replace-all`, ghi đè file cấu hình dùng chung) chạy
qua nhiều lời gọi Bash tool.

## Vì sao không tệ hơn

- Tự-verify NGAY sau mỗi thay đổi state (thói quen đã có, không phải thêm mới cho vụ này) bắt được
  trong <10 giây kể từ lúc ghi đè.
- Backup tình cờ tồn tại (chính lệnh Bash #1 tự capture trước khi lệnh #2 phá) — may mắn, KHÔNG
  phải cơ chế phòng thủ chủ động. Nếu lệnh #1 không capture kịp (vd network/IO chậm), sẽ KHÔNG có
  backup nào để phục hồi → phải dựa vào `git log`/tài liệu `kb/cron_registry.md` để tái tạo tay,
  chậm hơn nhiều và rủi ro tái tạo thiếu dòng.

## Fix / phòng ngừa

- **Ngay lập tức**: đổi cách thêm dòng crontab thành 1 lệnh Bash nguyên khối, không qua file tạm
  liên-lệnh (`(crontab -l; echo '<dòng mới>') | crontab -`) — đã áp dụng cho lần thêm dòng thứ 2
  trong chính sự cố này, verify sạch.
- **Khuyến nghị lâu dài (chưa làm, cần cân nhắc)**: một wrapper `bin/crontab_add_line.sh` bọc đúng
  pattern an toàn này (đọc-sửa-ghi atomic trong 1 process, verify diff trước khi coi là xong) để
  không ai (kể cả Mike ở phiên khác) lặp lại đúng bẫy `$$` liên-lệnh này với `crontab` — nhưng
  KHÔNG tự làm ngay trong sự cố này (giữ phạm vi sửa đúng bằng lỗi vừa gây ra, tránh mở rộng surface
  thay đổi không cần thiết — coding_guidelines.md §3 Surgical Changes).

## Tham chiếu

- `kb/cron_registry.md` dòng `paper_checkpoint_escalation.sh` (thay đổi crontab đang làm dở lúc xảy ra sự cố).
- `mike/bin/paper_checkpoint_escalation.sh` (script mới, không liên quan tới root cause của sự cố này).
