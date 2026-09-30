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

Wire tiếp 2026-09-30 (chỉ đạo user qua Mike, job Taylor_20260930_111053): BAL stop-loss -20% trên
giá vốn (`pt_v23_audit_2014.py:2008`) — ĐỘC LẬP với mốc T+45, cần `pnl_pct` do caller tự tính từ
giá LIVE (broker-native `avg_cost`/`marketPrice`, coding_guidelines §6), module này KHÔNG đọc giá.
CỐ Ý CHƯA wire cho LAG (backtest MIỄN stop, -0.99) và CAPIT (backtest KHÔNG có tham số stop_loss,
chỉ có `CAPIT_HOLD` theo phiên) — không tự bịa số cho 2 sleeve đó nếu chưa có chỉ đạo riêng (§29).
"""

LAG_EXIT_SESSIONS = 25          # pt_v23_audit_2014.py:2060,2062 — mốc CỐ ĐỊNH, không phải khoảng
BAL_EXIT_SESSIONS = 45          # pt_v23_audit_2014.py:2008
BAL_STOP_LOSS_PCT = -0.20       # pt_v23_audit_2014.py:2008 — độc lập mốc phiên, theo giá live
BAL_STOP_LOSS_MIN_HOLD = 2      # pt_v23_audit_2014.py:2008 min_hold; simulate_holistic_nav.py:689
                                 # gate MỌI stop-loss check ở days_held<min_hold — pin chưa từng
                                 # kiểm chứng stop-loss bắn ở phiên 0/1, không suy diễn quá pin
                                 # (quant-skeptic 2026-09-30, job Taylor_20260930_111053)
CAPIT_EXIT_SESSIONS = 60        # pt_v22_dt5g.py:123 / pt_v23_audit_2014.py:752 (CAPIT_HOLD)
CAPIT_REMINDER_SESSIONS = 55    # user chốt: nhắc trước ~1 tuần (60 - 5)


def lag_should_exit(sessions_held):
    """True ⇔ vị thế LAG đã giữ ĐỦ 25 phiên giao dịch trở lên kể từ entry (fixed, không stop)."""
    return sessions_held is not None and sessions_held >= LAG_EXIT_SESSIONS


def bal_should_exit(sessions_held):
    """True ⇔ vị thế BAL đã giữ ĐỦ 45 phiên giao dịch trở lên kể từ entry."""
    return sessions_held is not None and sessions_held >= BAL_EXIT_SESSIONS


def bal_stop_loss_hit(pnl_pct, sessions_held):
    """True ⇔ vị thế BAL lỗ ≥20% trên giá vốn (pnl_pct = marketPrice/avg_cost − 1, âm khi lỗ)
    VÀ đã giữ ≥`BAL_STOP_LOSS_MIN_HOLD` phiên — mirror `min_hold` của pin, tránh bắn stop-loss ở
    phiên 0/1 mà backtest chưa từng kiểm chứng. Độc lập với `bal_should_exit` (mốc T+45) — trigger
    theo GIÁ, không theo số phiên tới hạn. Epsilon 1e-9 để tránh sai số float khiến đúng -20.0%
    (vd 80000/100000-1 = -0.19999999999999996) không trigger."""
    if pnl_pct is None or sessions_held is None:
        return False
    if sessions_held < BAL_STOP_LOSS_MIN_HOLD:
        return False
    return pnl_pct <= BAL_STOP_LOSS_PCT + 1e-9


def capit_should_exit(sessions_held):
    """True ⇔ episode CAPIT đã giữ ĐỦ 60 phiên — tới hạn thoát TOÀN BỘ rổ."""
    return sessions_held is not None and sessions_held >= CAPIT_EXIT_SESSIONS


def capit_should_remind(sessions_held):
    """True ⇔ episode CAPIT đang trong cửa sổ nhắc trước (55 ≤ sessions_held < 60)."""
    return (sessions_held is not None
            and CAPIT_REMINDER_SESSIONS <= sessions_held < CAPIT_EXIT_SESSIONS)
