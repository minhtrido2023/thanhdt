# ĐÃ ÁP DỤNG 2026-08-04 — thư mục này là LỊCH SỬ, không phải việc đang chờ

Patch `flip_live.patch` **đã được áp ngay trong ngày 2026-08-04**, commit `d4f667b2`
("chase-cap patch#3: flip chase_cap_vol_scale_enabled -> LIVE"). README.md bên cạnh viết ở
thời điểm patch CHƯA áp và chưa bao giờ được cập nhật — đọc nó một mình sẽ hiểu ngược.

Bằng chứng kiểm lại 2026-09-23 (job Taylor_20260923_005911):
- `trading_bot/config.py:192` → `"chase_cap_vol_scale_enabled": True,   # LIVE 2026-08-04`
- `git log -L 192,192:trading_bot/config.py` → d4f667b2, 2026-08-04
- `git apply --check flip_live.patch` → **FAIL cả 4 file**, vì thay đổi đã nằm sẵn trong cây
- 3 selfcheck chạy thật: `stress_vol_scale_chase_cap.py` RESULT: PASS (LIVE paper+live+global) ·
  `chase_cap_selfcheck.py` ALL PASS · `dc_book_waterfall_selfcheck.py` 78 passed / 0 failed

Vì sao thư mục còn sót 7 tuần: sau khi áp patch không ai xoá thư mục pending, và registry để
`end: None` nên `paper_checkpoint_escalation.sh` không bao giờ rà tới. Hai kênh cùng im lặng ⇒
người đọc sau kết luận "việc còn treo". Đúng §28: **không suy diễn từ sự vắng mặt trên một
kênh — xác nhận bằng ARTIFACT** (ở đây artifact là `config.py` + `git log`, tra mất 2 phút).

Registry đã cập nhật cùng lượt: `status: graduated-live 2026-08-04`, `end: 2026-08-04`.
