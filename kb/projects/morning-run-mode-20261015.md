# Morning-run mode (`MIKE_MORNING_RUN=1`) — merged 2026-10-15
Sự cố gốc: 14/10 BQ về muộn (sau 19:45 ICT) ⇒ chuỗi 18:30/19:00 không lập plan 15/10; sáng 15/10 BQ đủ nhưng `daily_refresh_v34b_linux.sh`
và `bq_freshness_check.sh` khóa theo NGÀY LỊCH nên không có đường chạy hợp lệ. User chốt 08:43: bỏ plan 15/10, sửa cổng ngày.
- Opt-in qua env, cron KHÔNG đặt ⇒ 18:30/19:00 y nguyên. Phiên = phiên gần nhất có EOD (cutoff 17:00 ICT, `bin/expected_session.py`).
- Rào: plan đích = hôm nay mà ≥08:30 ICT ⇒ từ chối (exit 3); plan đích đã tồn tại ⇒ `[SKIP-MORNING]` (ép: `MIKE_MORNING_FORCE=1`).
- Chuỗi hạ nguồn (auto_exit_inject, send_plan_report, drift check...) KHÔNG theo mode ⇒ làm tay theo `kb/ops_runbook.md` § "Chạy TAY buổi sáng".
- Merge: mike `a19b77d62`, repo ngoài `3be6727a`. arch-review 2 vòng (NEEDS_CHANGES → NEEDS_CHANGES chỉ runbook → đã sửa), 19 mutation, 16 bị bắt.
- ⚠️ CHƯA chạy end-to-end (pipeline-2/3, DollarBill + MORNING_NOTE) lần nào — lần dùng thật đầu tiên phải theo dõi tay.
- Hạn chế NON-BLOCKING: rào 08:30 chỉ kiểm lúc khởi động; không lock; prompt/`CAL_TODAY` chưa có test; golive CSV đặt tên theo ngày lịch ≠ signal_date.
