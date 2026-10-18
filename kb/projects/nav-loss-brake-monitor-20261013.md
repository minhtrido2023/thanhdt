# Monitor phanh lỗ cấp NAV — CHỈ CẢNH BÁO, LIVE từ 2026-10-13

> Nguồn: user chốt 2026-10-12 18:11 + 21:31 ICT (`decided_by: user`); nhánh
> `feat/nav-loss-brake-monitor-20261012`, merge master `69397f67b`; arch-reviewer APPROVED 3 vòng.

## Trạng thái
- `bin/nav_loss_brake_monitor.py`, cron 22:05 + 00:20 ICT T2-T6 (`5 15 * * 1-5`, `20 17 * * 1-5` UTC);
  trạng thái `data/loss_brake/`; runbook: `kb/ops_runbook.md` mục "Phanh lỗ NAV".
- Ba phanh đo trên **NAV toàn tài khoản** (không tách DGC — user 21:31: DGC thuộc discretionary sleeve,
  hệ thống quản lý cả tài khoản): lỗ một ngày ≤ −5% theo giá chốt · lỗ từ đỉnh ≥ 25% · lỗ ≤ −15% từ
  điểm vào đợt đòn bẩy CAPIT (khoá số `episode_drawdown_limit_pct` trong `trading_rules.json`).
- **KHÔNG tự tạo `data/BOT_STOP`.** Chạm ngưỡng ⇒ tin đỏ ở Trading Daily kèm sẵn lệnh, user quyết.
- Luật giảm tin (user duyệt): NAV ước tính mà số tạm tính cách ngưỡng > 2,0 điểm % ⇒ không đẩy tin
  tối, chỉ hiện ở dòng kiểm sáng.
- `agents/Spyros/risk_monitor.py` vẫn KHÔNG chạy và không phải cổng. Phanh −5% đo trong phiên: CHƯA có.

## Còn mở (2026-10-13)
- Commit nối `bin/ops_health_check.sh` (`3e0a9f7a7`) ĐÃ MERGE 2026-10-16 (arch-review APPROVED, 7 đêm cron rc=0). Việc nhỏ còn lại: lỗi cấp fleet rc=2/3 bị route 2 lần/lượt (mỗi account), stderr nhiều dòng chỉ route dòng đầu.
- Ba mục nhỏ reviewer nêu, chờ user duyệt cho Mike tự sửa: F1 khoá chống trùng nuốt tin "tạm tính sát
  ngưỡng" khi dòng ước tính về sau 22:05 (`:1049`); F2 dòng ước tính của ngày có `nav_gate_block` vẫn
  được giảm tin (`:664-708`); F4 gửi lỗi (rc=3) che phanh chạm (rc=5) ở dòng sáng (`:1085-1091`).
- F5: nhiều phiên NAV ước tính liên tiếp thì không có tin tối (lịch sử dài nhất 2 phiên).
- `data/loss_brake/` chưa nằm trong `fleet_backup.sh` — phải xong trước đợt đòn bẩy đầu tiên.
- Nạp tiền không khai trong `data/account_cash_flows.json` sẽ che lỗ — nhánh
  `feat/fund-cashflow-detect-20261012` là chỗ đóng.
- Đường mở "đợt đòn bẩy" chưa từng chạy trên dữ liệu thật (chưa có lệnh vay gói 1840 nào).
- **Mốc xem lại 2026-11-09**: sau ~4 tuần không báo giả ⇒ trình user quyết tự tạo BOT_STOP hay giữ cảnh báo.
