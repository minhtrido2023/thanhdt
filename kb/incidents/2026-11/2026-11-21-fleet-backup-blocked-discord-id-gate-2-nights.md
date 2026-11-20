# 2026-11-21 — `fleet_backup.sh`: commit mike-fleet bị discord-id-gate chặn 2 đêm (19+20/11), log vẫn có dòng "✅ Backup pushed"

status: fixed (mike commit `70eeb517d`, weekly ops audit job `Mike_20261120_222134`)

**Phát hiện:** weekly ops audit 21/11 — `cron_health_check.py` ERRORS_FOUND cho `fleet_backup.sh`
("FAIL fleet commit — hôm nay KHÔNG vào backup, push dưới đây chỉ đẩy HEAD CŨ"). Đuôi `logs/backup.log` lại kết thúc bằng
`✅ Backup pushed: 298cb506d` — dòng đó là push của repo NGOÀI (`main`), không phải mike-fleet. Đọc đuôi log là tưởng ổn.

**Nguyên nhân thật (đọc log):** `bin/mbb_rights_tradeable_watch.py` (file mới, staged `A`, cron 19:15 ICT) có
`THREAD = "1521470705563340910"` ở dòng 19 ⇒ pre-commit `discord-id-gate` HARD-BLOCK ⇒ commit backup của mike thất bại
toàn bộ (363 file staged, gồm research Taylor 19-20/11) 2 đêm liền. Script tự chạy được vì không ai commit nó qua gate.

**Sửa:** `THREAD = "trading_daily"` (notify_thread.sh tự resolve; `bin/discord_channel.sh trading_daily` ⇒ cùng ID cũ),
commit riêng qua gate (Passed). Pre-check: `pre-commit run` trên toàn bộ staged còn lại ⇒ 0 hook Failed ⇒ backup 17:00Z
21/11 sẽ qua. **Verify thật còn chờ:** dòng mike-fleet trong `logs/backup.log` của lượt 2026-11-21T17:00Z.

**Bài học:** "file mới không commit, chỉ staged" vẫn là code production (cron đã chạy nó) — gate chỉ cắn lúc backup, tức là
sau khi đã chạy thật. Đọc `backup.log` phải tách 2 repo; dòng ✅ cuối không nói gì về mike-fleet.

---

## Phụ: TRIM_DD 19/11 xoá file khoá giả định mà `kb/dd_price_zones.json` còn trỏ tới (đã sửa bởi Wags, ghi lại ở đây)

`weekly_orphan_review.py --apply` (TRIM_DD, user duyệt luật 19/11) xoá 28 file `calc/assumptions*.json`/`LOCK_*.txt` vì
`corpus()` không quét `kb/*.json` ⇒ `dd_price_zones_selfcheck` 29 lỗi + consolidator log `FAIL #65..#78 … không đọc được nguồn
khoá giả định`. Sửa trong `5e299519b` (Wags_20261120_093002): thêm `kb/*.json` vào corpus + restore byte-identical. Verify
21/11: `bin/dd_price_zones_selfcheck.py` ⇒ "sổ 91 entry / 34 mã; lỗi 0". Cùng đợt dọn research (`60fe58b82`) làm 5 selfcheck
research đỏ do mất input (dd_redo g2/g2r2, livermore_divergence, dd_PAT cwd-relative, oshares_r10 worktree) — không phải
production, chủ Taylor.
