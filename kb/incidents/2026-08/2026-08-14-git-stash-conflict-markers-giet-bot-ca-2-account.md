# 2026-08-14 — `git stash apply` bỏ dở để lại conflict marker trong `trading_bot/config.py` + `executor.py` → bot CHẾT NGAY khi khởi động, CẢ 2 account

**Hiện tượng:** cron 09:05 ICT khởi động `run_bot.sh` cho SpaceX và ZaloPay; cả hai thoát rc=1
sau ~0 phút với:

```
File "/home/trido/thanhdt/WorkingClaude/trading_bot/config.py", line 121
    <<<<<<< Updated upstream
SyntaxError: invalid syntax
```

Không có process `bot_execute.py` nào sống, **không có journal**
`exec_*_2026-08-14_journal.csv` ⇒ **0 lệnh được đặt**, không có lệnh kẹt, không mất tiền.
Plan hôm nay: 1 lệnh BUY TV1 mỗi account, đã `approved_by = "user (John) - Discord real-time
2026-08-13"`.

**Root cause (bằng chứng, không suy đoán):** `git status` cho `UU trading_bot/config.py` và
`UU trading_bot/executor.py` — working tree đang ở trạng thái **unmerged của một `git stash
apply/pop` bỏ dở**. Không có `MERGE_HEAD`/`REBASE_HEAD` ⇒ không phải merge/rebase. Stash còn
nguyên: `stash@{0}: On session/1520374161971875940-rubber: hybrid+refresh_skip_fix WIP
20260810` (config.py +31 dòng, executor.py +283/−22). mtime cả 2 file = **07:56:21 ICT
2026-08-14**, tức ~1h09 trước giờ bot chạy.

**Ai gây ra:** KHÔNG phải cron/script của fleet — `grep -rln stash mike/bin/*.sh bin/*.sh`
không có kết quả, và không có cron job nào chạy quanh 00:56 UTC. ⇒ một phiên tương tác
(người hoặc session Claude interactive) đã `git stash apply` lúc 07:56 rồi bỏ đi khi đang
conflict. **Chưa xác định được phiên nào** — dispatch log qua đêm không nhắc `stash`.

**Xử lý (Winston, job `Winston_20260814_020503`):**
`git checkout HEAD -- ./trading_bot/config.py ./trading_bot/executor.py`. An toàn tuyệt đối
vì đã kiểm chứng trước: phía "ours" (stage 2, tức working tree TRƯỚC khi apply stash) **giống
HEAD từng byte** ở cả 2 file ⇒ không có công việc chưa commit nào bị mất. `stash@{0}` giữ
nguyên cho người muốn apply hoàn tất. Verify: `python3 -m py_compile` PASS, 0 conflict marker,
`git status` sạch.

**VIỆC CÒN MỞ (không thuộc quyền Winston):** stash chứa 2 thay đổi thật —
`fill_timing_hybrid_enabled: True` (paper) và một "refresh_skip_fix" trong `executor.py`
(+283 dòng). Ai đó ĐANG muốn đưa 2 thứ này vào. Resolve đúng cách = việc của Taylor +
quant-skeptic (chạm logic đặt lệnh), không phải khôi phục vội trong giờ giao dịch.

**Bài học:**
1. Một `git stash apply` bỏ dở **giết toàn bộ fleet giao dịch** ở lần cron kế tiếp — file
   Python vỡ cú pháp không có fallback nào cả. Đụng `trading_bot/*` bằng thao tác git có thể
   để lại conflict thì phải **resolve xong trong cùng phiên**, hoặc `git stash` lại/`git
   checkout HEAD --` trước khi rời máy.
2. `bot_heartbeat.sh` autoheal restart cũng vô dụng với lỗi loại này — nó restart vào đúng
   cái file vỡ. Autoheal chỉ chữa được chết-lúc-chạy, không chữa được repo hỏng.
3. Checker phát hiện đúng và nhanh (ops_autofix dispatch trong vòng vài giây sau 09:05), nhưng
   chuỗi này chỉ chạy khi cron bot chạy — nếu ai đó để conflict marker vào chiều thứ Sáu thì
   phải tới sáng thứ Hai mới lộ.
