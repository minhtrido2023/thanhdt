# Kế hoạch rà + dọn MỒ CÔI hằng tuần (user chỉ đạo 2026-11-19 22:08 ICT, `decided_by: user`)
Luật user: thứ gì để quá lâu, không tham chiếu, không định hướng ⇒ dọn; đưa vào lịch hàng tuần để khỏi tích mồ côi (bài học: 63 gitlink worktree mồ côi, 1,4G pkl research đã đóng, ~7G/worktree do `agents/Taylor` được track).
## Cơ chế — `bin/weekly_orphan_review.py` (cron Chủ nhật 10:30 ICT = `30 3 * * 0` UTC; log `logs/orphan_review.log`, báo cáo `logs/orphan_review/<ngày>.md`, digest 1 tin qua `bin/notify.sh`)
| Nhóm | Điều kiện | Hành động |
|---|---|---|
| research (không trong `kb/cleanup_keep.txt`; `dd_*` xem dòng DD dưới) | im >3 ngày, **không** code/cron/registry nhắc tên, nặng ≥1MB | **TRIM**: xoá file không-`.md` (tracked: `git rm` + commit theo pathspec, khôi phục được; untracked: chỉ xoá nếu md5 không khớp code/registry/PINS) |
| research mồ côi hẳn | như trên + không `.md` + KB không nhắc + im >14 ngày | **REMOVE_DIR** |
| `/tmp` top-level của user | im >7 ngày, không tiến trình nào nhắc | `rm -rf` ngay (không grace) |
| **GRACE** | research phải xuất hiện ≥7 ngày ở báo cáo trước (state `state/orphan_review_state.json`) mới xoá | cho người kịp ghi vào `kb/cleanup_keep.txt` |
| **DD (`dd_*`) — user duyệt 2026-11-19 22:18 ICT** | im >3 ngày, không code/cron nhắc | **TRIM_DD**: giữ `.md` (nguồn dùng lại khi cập nhật) + `.py`/`.sh`; xoá file tạm (src BCTC tải về, png/figs, pdf/html báo cáo, csv/json/xlsx trung gian). DD mới sửa <3 ngày (đang làm) không bị đụng. |
| CHỈ BÁO (không bao giờ tự xoá) | `data/bq_cache_asof*`, `data/pinned_ledgers`, worktree chưa merge >7 ngày sạch, 12 file lớn cũ trong `data/` | liệt kê để người quyết |
Giữ nguyên các cron có sẵn: `worktree_cleanup_daily.sh` (worktree/nhánh ĐÃ merge, 03:00 ICT), `disk_guard_daily.sh` (cache regen + cảnh báo ≥85%).
## Quy tắc đi kèm (từ giờ)
1. Nghiên cứu mới PHẢI để lại `.md` kết luận (REPORT/README) — đó là "định hướng"; thư mục không có thì bị coi mồ côi sau 14 ngày.
2. Muốn giữ artifact nặng: ghi `kb/cleanup_keep.txt` (kèm lý do) hoặc để code/cron tham chiếu thật.
3. Worktree mới của mike dùng **sparse-checkout** (`git worktree add --no-checkout` + `sparse-checkout set`), vì `agents/Taylor` track ~5G (PDF DD, csv, png) ⇒ worktree đầy đủ ~7G.
## Đã quyết (user 2026-11-19 22:18 ICT)
DD xong ⇒ về sau dùng lại nguồn `.md`, không giữ file tạm. Áp dụng ngay 1 lần với grace 0 (`--grace-days 0 --only R:dd_`), sau đó theo lịch tuần (grace 7 ngày). Nguồn BCTC cần lại ⇒ tải lại từ website công ty (skill `due-diligence` bước 1) hoặc `git checkout <commit> -- <đường dẫn>`. `.git` vẫn giữ lịch sử (5,6G) — không viết lại lịch sử.
Selfcheck: `bin/weekly_orphan_review_selfcheck.py` (repo giả, 2 TZ).
