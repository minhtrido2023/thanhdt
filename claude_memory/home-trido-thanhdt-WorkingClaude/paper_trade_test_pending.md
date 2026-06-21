---
name: Paper-trade test cho Layer 3 timing rules (pending review)
description: ACTIVE paper-trade simulation đang chạy daily 14:55 từ 2026-05-12. Weekly Telegram report Fri 15:30. Review hẹn [REDACTED]12. Trigger khi user nói "check paper trade" hoặc "kiểm tra paper trade".
type: project
originSessionId: 90878235-541c-4207-a725-44398117b136
---
**TRIGGER PHRASES:** "check paper trade" / "kiểm tra paper trade" / "review paper trade" / "kết quả paper trade"

**Khi user nói các phrase trên:**

1. Chạy `python paper_trade_daily.py --report` để xem summary
2. Đọc `paper_trade_entries.csv` và `paper_trade_exits.csv`
3. Compare với backtest baseline (memory `layer3_rules_backtest.md`):
   - Backtest miss rate: TOP30 0.03%, MIDCAP 0.4%, PENNY 1.6%
   - Backtest per-trade lift: TOP30 +0.90pp, MIDCAP +1.18pp, PENNY +1.73pp
   - Expected annual CAGR alpha: +0.8 đến +1.5pp
4. Đánh giá:
   - Live miss rate có gần backtest không?
   - Fill saving median có dương không?
   - Có ticker/play_type bị adversely selected (limit không fill khi cần)?
   - Sample đủ lớn để inference chưa? (cần ~50+ entries)
5. Round-trips đầu (~entries ngày 2026-05-12 đủ 45d ngày [REDACTED]25) — nếu đã có exits, đánh giá lift thực tế.
6. Nếu kết quả tốt: đề xuất implement vào `recommend_holistic.py` dưới flag để A/B test live
7. Nếu xấu/inconsistent: phân tích nguyên nhân (signal leakage? market regime?) và đề xuất stop hoặc adjust

**Setup hiện có (đã chạy):**
- `paper_trade_daily.py` — script chính (idempotent)
- `paper_trade_run.bat` — wrapper cho Task Scheduler
- Windows Task `PaperTradeBA` — chạy daily 14:55
- Windows Task `PaperTradeReminder` — pop-up message [REDACTED]12 09:00
- `paper_trade_weekly_report.py` + `paper_trade_weekly_run.bat` — weekly Telegram report (reuse `telegram_recommend.py` send helpers + `telegram_config.json`)
- Windows Task `PaperTradeWeeklyReport` — chạy thứ 6 hàng tuần 15:30; gửi summary + đính kèm entries/exits CSV qua Telegram chat [REDACTED]
- Rule map (PLAY_RULE dict trong script):
  - MOMENTUM_* / COMPOUNDER_BUY / S_PRO / MEGA → E1_T1115_LIM (limit @ 11:15)
  - DEEP_VALUE_RECOVERY → E_S2_ANTICIPATE (S2 intraday trigger w/ ATC fallback)
  - COMPOUNDER_HOLD / WAIT / PASS / AVOID_faE → SKIP

**Caveats user đã được thông báo:**
- Máy phải ON lúc 14:55 mỗi ngày trading
- recommend_holistic.py cần chạy định kỳ để có fresh holistic_*.csv (latest hiện tại: 2026-05-11)
- Sau 1 tháng chỉ có entry-side metrics, P&L cần thêm ~2 tuần nữa
