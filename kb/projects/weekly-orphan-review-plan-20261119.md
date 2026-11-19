# Kế hoạch rà + dọn MỒ CÔI hằng tuần (user chỉ đạo 2026-11-19 22:08 ICT, `decided_by: user`)
Luật user: thứ gì để quá lâu, không tham chiếu, không định hướng ⇒ dọn; đưa vào lịch hàng tuần để khỏi tích mồ côi (bài học: 63 gitlink worktree mồ côi, 1,4G pkl research đã đóng, ~7G/worktree do `agents/Taylor` được track).
## Cơ chế — `bin/weekly_orphan_review.py` (cron Chủ nhật 10:30 ICT = `30 3 * * 0` UTC; log `logs/orphan_review.log`, báo cáo `logs/orphan_review/<ngày>.md`, digest 1 tin qua `bin/notify.sh`)
| Nhóm | Điều kiện | Hành động |
|---|---|---|
| research (không `dd_*`, không trong `kb/cleanup_keep.txt`) | im >3 ngày, **không** code/cron/registry nhắc tên, nặng ≥1MB | **TRIM**: xoá file không-`.md` (tracked: `git rm` + commit theo pathspec, khôi phục được; untracked: chỉ xoá nếu md5 không khớp code/registry/PINS) |
| research mồ côi hẳn | như trên + không `.md` + KB không nhắc + im >14 ngày | **REMOVE_DIR** |
| `/tmp` top-level của user | im >7 ngày, không tiến trình nào nhắc | `rm -rf` ngay (không grace) |
| **GRACE** | research phải xuất hiện ≥7 ngày ở báo cáo trước (state `state/orphan_review_state.json`) mới xoá | cho người kịp ghi vào `kb/cleanup_keep.txt` |
| CHỈ BÁO (không bao giờ tự xoá) | `dd_*`, `data/bq_cache_asof*`, `data/pinned_ledgers`, worktree chưa merge >7 ngày sạch, 12 file lớn cũ trong `data/` | liệt kê để người quyết |
Giữ nguyên các cron có sẵn: `worktree_cleanup_daily.sh` (worktree/nhánh ĐÃ merge, 03:00 ICT), `disk_guard_daily.sh` (cache regen + cảnh báo ≥85%).
## Quy tắc đi kèm (từ giờ)
1. Nghiên cứu mới PHẢI để lại `.md` kết luận (REPORT/README) — đó là "định hướng"; thư mục không có thì bị coi mồ côi sau 14 ngày.
2. Muốn giữ artifact nặng: ghi `kb/cleanup_keep.txt` (kèm lý do) hoặc để code/cron tham chiếu thật.
3. Worktree mới của mike dùng **sparse-checkout** (`git worktree add --no-checkout` + `sparse-checkout set`), vì `agents/Taylor` track ~5G (PDF DD, csv, png) ⇒ worktree đầy đủ ~7G.
## Việc còn để người quyết (không tự động)
`dd_*` (PDF/png nguồn ~3G+) — giữ theo chỉ đạo "chỉ cập nhật tiếp"; cân nhắc đẩy nguồn PDF DD ra ngoài git (LFS/ngoài repo) để giảm ~3G/worktree và `.git` 5,6G.
Selfcheck: `bin/weekly_orphan_review_selfcheck.py` (repo giả, 2 TZ).
