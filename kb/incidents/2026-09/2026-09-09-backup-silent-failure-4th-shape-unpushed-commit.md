# 2026-09-09 — Backup silent-failure shape thứ 4: `backup.sh` báo "already up to date" trong khi remote thiếu hẳn 1 commit; và 3/3 lần hỏng trước KHÔNG có alert nào

**Status**: fixed
**Phát hiện bởi**: Wags, job `Wags_20260909_012007` (wags_autofix coord-2026-09-09, triage bus question `Mike/retro-2026-09-08-backup-silent-failure-recurring-3rd`)
**Ảnh hưởng**: workspace chính `/home/trido/thanhdt` — commit `3ff20579` ("BQ cache: self-heal year chunks…", 2026-09-08T17:48Z) nằm local **chưa push suốt 8h**, `origin/main` dừng ở `057254e0` (17:12Z). Không mất dữ liệu (đĩa còn nguyên), nhưng đúng chế độ hỏng mà backup sinh ra để chặn: một sự cố ổ đĩa trong cửa sổ đó = mất commit. Quan trọng hơn: **tự nó sẽ không bao giờ tự lành** — mọi lần chạy sau đều rơi vào cùng nhánh và tiếp tục báo thành công.

## Root cause

`backup.sh:29-33` (bản cũ):

```bash
git add -A
if git diff --cached --quiet; then
  echo "Nothing changed — already up to date."
  exit 0            # ← thoát TRƯỚC khi tới lệnh push ở dưới
fi
```

"Không có gì để **COMMIT**" bị coi là "không có gì để **PUSH**". Một commit sinh ra ngoài `backup.sh` (người/phiên khác `git commit` tay) làm working tree sạch ⇒ nhánh này thoát 0, **không bao giờ chạm tới `git push` ở cuối script**, và mọi caller (`fleet_backup.sh`, `kb_nightly.sh`) in ra thành công.

> **Đính chính (arch-review Wags_20260909_012007, verdict NEEDS_CHANGES — grep bác bỏ dẫn chứng gốc):**
> câu cũ ở đây khẳng định "Log đêm 09-08 ghi đúng nguyên văn `Nothing changed — already up to date.`"
> — SAI. Chuỗi đó lần cuối xuất hiện trong `logs/backup.log` ngày **2026-07-19**, không có ở run
> 09-08. Run `fleet_backup 2026-09-08T17:00:01Z` thật ra chết ở bước `git add -A`/`git status
> --porcelain=2` vì gitlink treo `mike_paseo/agents/wt-1521113190405247057/.git` (worktree đã bị
> gỡ khỏi `mike/.git/worktrees/` nhưng thư mục checkout vẫn còn, trỏ về admin dir không tồn tại).
> Shape 4 (đoạn dưới) là bug LATENT phát hiện được bằng đọc code, **không phải nguyên nhân của
> lần miss 09-08** — hai chuyện độc lập bị gộp nhầm khi viết incident lần đầu.
>
> **Sự cố ĐANG MỞ lúc đó, giờ đã tự khép**: cùng lỗi gitlink làm `fleet_backup` FAIL **11 đêm
> liên tiếp 2026-08-29 → 2026-09-08** (`grep -c "FAIL main backup" logs/backup.log` = khớp đúng
> chuỗi 11 lần liền trong khoảng này), tất cả cùng 2 dòng `fatal:` y hệt. Không cần Wags can
> thiệp: chính user đã tự sửa cùng ngày 09-08, commit `057254e0` "manual verify after gitlink
> fix 2026-09-09" (17:12:39Z, TRƯỚC cả commit `3ff20579` 17:48Z) thêm `WorkingClaude/mike_paseo/`
> vào `.gitignore` — từ đó `mike_paseo` không còn tham gia `git add -A`/`git status` của repo
> `/home/trido/thanhdt` nữa. Run `fleet_backup 2026-09-09T17:00:01Z` ngay sau đó đã PASS sạch
> (`✅ Backup pushed: c1721329`), và mọi run từ 09-09 tới nay đều sạch. Thư mục worktree treo vẫn
> còn trên đĩa (`mike_paseo/agents/wt-1521113190405247057/`) nhưng vô hại vì đã bị `.gitignore`
> — không cần dọn để backup chạy đúng; dọn hay không là quyết định vệ sinh, không phải rủi ro.

Đây là **shape thứ 4** của cùng một họ sự cố trong 5 tuần — mỗi lần một nguyên nhân kỹ thuật khác nhau, cùng một hậu quả (backup không lên mà không ai biết):

| Ngày | Nguyên nhân kỹ thuật | Ai phát hiện |
| --- | --- | --- |
| 2026-08-01 | `kb_nightly.sh` trỏ sai đường dẫn `backup.sh` | cron_health_check audit |
| 2026-08-12 | `\|\| true` nuốt exit thật của `backup.sh` | người đọc chủ động |
| 2026-09-08 | gitlink worktree treo + submodule `mike_paseo` ⇒ `git status` fatal | retro 09-08 |
| 2026-09-09 | "nothing to commit" thoát 0, không push commit tồn | Wags coord-2026-09-09 |

Bốn nguyên nhân độc lập ⇒ **vá theo nguyên nhân không hội tụ**. Khiếm khuyết chung không nằm ở nguyên nhân nào cả mà ở chỗ: **chưa từng có ai kiểm tra KẾT QUẢ** (bản trên GitHub có tươi không), chỉ kiểm tra exit code của chính script hay đọc một dòng warning chìm trong digest KB-nightly.

## Fix (3 phần — option C của bus question, Wags thực hiện theo mandate ops 2026-07-07)

1. **`/home/trido/thanhdt/backup.sh`** — nhánh "nothing to commit" nay so `git ls-remote origin main` với HEAD; nếu remote là tổ tiên thật của HEAD (không phân nhánh) thì push các commit đã có rồi mới thoát. Trạng thái phân nhánh cố tình KHÔNG tự push (sẽ do checker báo, không tự sửa).
2. **`mike/bin/kb_nightly.sh`** (option A) — `BACKUP_WARN` chuyển từ đuôi dòng digest chung sang **dòng RIÊNG đứng đầu** message (`🚨 …`), không còn nằm sau OVERSIZE/PRUNE_WARN.
3. **`mike/bin/backup_freshness_check.sh`** (option B, MỚI) + cron 08:35 ICT hằng ngày — kiểm tra ĐỘC LẬP trên remote ref thật, 2 bất biến: HEAD remote ≤ 30h tuổi; không có commit local >30h chưa push và local/remote không phân nhánh. Vì nó đọc kết quả chứ không đọc nguyên nhân, nó bắt được cả shape thứ 5 chưa từng gặp. Báo Architecture + bus event `error`; sạch thì quiet-heartbeat Telegram.

## Verify

- `backup.sh`: test sandbox (repo bare local + clone) — (a) commit chưa push, tree sạch → bản vá PUSH, remote khớp local; (b) **negative control** chạy code CŨ trên đúng state đó → remote vẫn tụt lại (bug tái hiện được); (c) local/remote đã khớp → in "Nothing changed", không push, rc=0; (d) state phân nhánh → không crash, không push.
- `backup_freshness_check.sh`: chạy thật `BACKUP_FRESHNESS_QUIET=1` → sạch (remote 8h tuổi, 2 nhánh). Negative control `BACKUP_MAX_AGE_H=1` → bắt đúng cả 3 vi phạm, **gồm chính commit `3ff20579` chưa push** ("remote thiếu 1 commit") — tức nếu script này đã tồn tại, nó đã bắt được sự cố hôm nay.
- `bash -n` sạch cả 3 script; render test dòng `BACKUP_WARN` đứng đầu message.
- ~~Chưa chạy `backup.sh` thật để đẩy `3ff20579` lên...~~ — MOOT: run `fleet_backup 09-09T17:00:01Z` đã tự push `c1721329` (xem đính chính trên), toàn bộ dây chuyền từ 09-09 tới nay xanh liên tục.

**Cập nhật coord-2026-09-10 (round 2 của arch-review, cùng trace):**
- `backup.sh`: thêm chẩn đoán rõ khi remote không tới được (`git ls-remote` rc≠0 → in lỗi + `exit 1`, thay vì chết im lặng dưới `set -euo pipefail` như review phát hiện) và cảnh báo rõ khi local/remote phân nhánh (không còn lặng lẽ in "Nothing changed").
- `cron_health_check.py`: thêm `fatal:`, `^\s*FAIL ` (IGNORECASE, scoped bằng `(?i:...)` để không nới các pattern khác) và `NOTIFY_FAILED` vào `ERROR_PATTERNS` — verify bằng cách chạy đúng 3 dòng lỗi thật của run 09-08 qua `ERROR_RE`, cả 3 khớp; dòng `✅ Backup pushed` không khớp (không có false positive).
- `backup_freshness_check.sh`: thêm bất biến #3 (tuổi commit `auto-backup <ts>` / `fleet backup <ts>` gần nhất trên remote — bắt được ca "HEAD remote tươi nhờ push tay, pipeline tự động đã chết phía sau"); bỏ toàn bộ `2>/dev/null || true` quanh notify, thay bằng `NOTIFY_FAILED: ...` in ra stderr khi notify/append_event thất bại.
- Selfcheck mới: `bin/backup_push_selfcheck.sh` (6/6 PASS, extract-and-test trực tiếp từ `backup.sh`, gồm 1 negative control tái hiện shape-4 bằng code cũ) và `bin/backup_freshness_check_selfcheck.py` (6/6 PASS, gồm 1 negative control chứng minh check_repo() bản CŨ — trước bất biến #3 — im lặng đúng ở ca "HEAD tươi nhưng pipeline chết"). Cả hai chạy sạch dưới `env -u TZ` và `TZ=Pacific/Kiritimati`.
- Chạy thật `BACKUP_FRESHNESS_QUIET=1 bin/backup_freshness_check.sh` trên trạng thái hiện tại (2026-09-10) → sạch, không báo động giả từ bất biến #3 mới.

## Bài học

Vá nguyên nhân thứ N của một họ sự cố lặp lại là dấu hiệu thiếu **một phép đo kết quả**. Ba lần đầu đều "đã fix" đúng nguyên nhân của nó và đều không ngăn được lần sau. Câu hỏi phải hỏi không phải "vì sao lần này hỏng" mà "cái gì trả lời được câu *backup có lên không* mà không cần biết nguyên nhân".
