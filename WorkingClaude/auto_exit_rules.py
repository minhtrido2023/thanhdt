# -*- coding: utf-8 -*-
"""auto_exit_rules.py — luật exit TỰ ĐỘNG cho sleeve LAG/BAL/CAPIT, THUẦN (không I/O).

Chỉ đạo: user qua Mike, 2026-09-30 (job Taylor_20260930_080814) — phát hiện lệch giữa backtest
đã pin và đường LIVE (không có dòng code nào tự bán LAG/BAL theo mốc phiên, và CAPIT hoàn toàn
không có exit tự động — `capit_episode.py` tự ghi rõ điều này từ 07-31).

Số hiệu, xác nhận bằng grep trực tiếp file:line — KHÔNG đoán:
  - LAG:   hold_days=25, hold_days_by_tier={t: 25 for t in _LAG_BASE_TIERS}
           (`pt_v23_audit_2014.py:2060,2062`; cùng số ở `lag_dnpr_harness.py:1640,1642`).
           stop_loss=-0.99 ⇒ MIỄN stop-loss theo drawdown cho LAG trong backtest pin.
  - BAL:   hold_days=45, stop_loss=-0.20 (`pt_v23_audit_2014.py:2008`; `lag_dnpr_harness.py:1588`).
  - CAPIT: CAPIT_HOLD = int(os.environ.get("CAPIT_HOLD", "60"))
           (`pt_v22_dt5g.py:123` hardcode 60; `pt_v23_audit_2014.py:752` / `lag_dnpr_harness.py:484`
           cùng default "60") — chỉ tồn tại ở nhánh BACKTEST/PAPER. Đường LIVE trước 2026-09-30
           KHÔNG có dòng code nào bán CAPIT theo mốc này (xem docstring `capit_episode.py`).

Ranh giới cố ý: module này KHÔNG đọc file, KHÔNG gọi broker/BQ — chỉ nhận `sessions_held` (số
phiên giao dịch đã trôi qua kể từ entry, tính bằng `count_trading_days` sẵn có trong
`mike/bin/portfolio_status.py`) và trả về quyết định. Nhờ vậy selfcheck test được toàn bộ
ngưỡng/biên mà không cần broker/DNSE/journal thật, và logic exit không lặp lại ở 2 nơi
(`portfolio_status.py` hiển thị cảnh báo, `auto_exit_inject.py` chèn lệnh bán — cả hai phải
dùng ĐÚNG MỘT hằng số, không phải 2 bản chép tay).

`stop_loss` KHÔNG được wire ở đây (ngoài phạm vi chỉ đạo 2026-09-30): LAG backtest MIỄN stop
(-0.99), BAL backtest có stop -0.20 nhưng auto-sell theo drawdown là quyết định khác (cần giá
live, không chỉ số phiên) — không suy diễn thêm nếu chưa có chỉ đạo riêng (§29 coding_guidelines).
"""

LAG_EXIT_SESSIONS = 25          # pt_v23_audit_2014.py:2060,2062 — mốc CỐ ĐỊNH, không phải khoảng
BAL_EXIT_SESSIONS = 45          # pt_v23_audit_2014.py:2008
CAPIT_EXIT_SESSIONS = 60        # pt_v22_dt5g.py:123 / pt_v23_audit_2014.py:752 (CAPIT_HOLD)
CAPIT_REMINDER_SESSIONS = 55    # user chốt: nhắc trước ~1 tuần (60 - 5)


def lag_should_exit(sessions_held):
    """True ⇔ vị thế LAG đã giữ ĐỦ 25 phiên giao dịch trở lên kể từ entry (fixed, không stop)."""
    return sessions_held is not None and sessions_held >= LAG_EXIT_SESSIONS


def bal_should_exit(sessions_held):
    """True ⇔ vị thế BAL đã giữ ĐỦ 45 phiên giao dịch trở lên kể từ entry."""
    return sessions_held is not None and sessions_held >= BAL_EXIT_SESSIONS


def capit_should_exit(sessions_held):
    """True ⇔ episode CAPIT đã giữ ĐỦ 60 phiên — tới hạn thoát TOÀN BỘ rổ."""
    return sessions_held is not None and sessions_held >= CAPIT_EXIT_SESSIONS


def capit_should_remind(sessions_held):
    """True ⇔ episode CAPIT đang trong cửa sổ nhắc trước (55 ≤ sessions_held < 60)."""
    return (sessions_held is not None
            and CAPIT_REMINDER_SESSIONS <= sessions_held < CAPIT_EXIT_SESSIONS)
