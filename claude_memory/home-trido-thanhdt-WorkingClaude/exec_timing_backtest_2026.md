---
name: exec-timing-backtest-2026
description: "Backtest execution timing cho trading_bot (2023-09→2026-06, 16 mã, bar 1m) — dip-cross thắng blind-cross ~3.5bps/side, OR-pacing thêm ít nhưng tail xấu ngày crash"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7e8fc85f-a649-4195-a4d7-aa9bfdea1ed9
---

# Execution-timing backtest ([REDACTED]12)

**Câu hỏi**: executor bot (mirror V2.3) cross spread mù từ 9:15 — chọn thời điểm trong phiên theo research intraday có tốt hơn?

**Setup**: `workspace/backtest_exec_timing.py` + fetcher `workspace/fetch_intraday_1m.py` (cache `data/intraday_1m/{16 mã}.csv`, bar 1m vnstock VCI từ 2023-09-11). Parent order 1B VND buy & sell mỗi (mã, ngày); fill model giống executor.py: child 200M/8phút, 1 child sống, participation 10%/bar, spread ước 1 tick (như nhau mọi strategy), 14:25 force-cross. Metric = implementation shortfall vs arrival 9:15, penalty phần không khớp mark close. 13,538 obs, t-stat cluster theo ngày. Kết quả: `data/exec_timing_results.csv` (chạy `--report` để in lại).

**Kết quả** (delta vs S0 blind-cross 13.3bps, âm = tiết kiệm):
- **S2 DIP-CROSS** (mean-reversion 15': giá vừa chạy cùng hướng lệnh → passive tại bid; ngược hướng → cross): **−3.48bps, t=−31, win 74%/ngày**, đều cả buy/sell, LIQUID/SMALL, dương mọi năm nhưng DECAY 2023 −5.0 → 2026 −2.2bps. Tail lành (P99 +42bps). Cơ chế = spread capture có timing; KHÔNG cần data ngoài (chỉ close 15' của chính mã).
- **S1 OR-PACING** (OR30 VN30F 9:00-9:30, front-load khi drift bất lợi / back-load khi thuận): −1.06bps tổng (chỉ tác dụng trên ~40% ngày |OR|≥0.2%: −2.6/−2.8bps), sell-side không significant (t=−1.8).
- **S3 COMBO**: −4.13bps tốt nhất trung bình NHƯNG **tail xấu**: ngày crash/trend mạnh (2025-04 tariff: STB +383bps, VIX +263bps tệ hơn S0) vì back-load lỡ tàu rồi force fill giá tệ. P99 +69bps.

**Verdict trader**: wire **S2 only** vào executor (sửa `buy_cross_spread` → điều kiện r15: cross khi giá vừa đi ngược hướng mình, passive khi vừa chạy cùng hướng; giữ nguyên chase-cap/ATC). BỎ OR-pacing (edge nhỏ + tail risk + thêm dependency futures feed realtime). Ước tiết kiệm ~0.3–0.6pp NAV/năm tùy turnover (one-side ~8-15× NAV), lấy đầu thấp vì decay.

**Caveat**: spread model 1 tick + fill khi low<limit là proxy (không có queue position) → con số thật phải xác nhận bằng A/B paper-trade. Small-cap ngày <5B GTGD bị loại khỏi mẫu (D2D/DHA/NNC gần như không đóng góp).

**WIRED [REDACTED]12** (user duyệt): executor.py có `cross_mode` ("dip" mặc định / "[REDACTED]"), `px_hist` lấy mẫu giá 60s trong state (resume được), `_r15`/`_decide_cross` (no-hist/stale → cross fail-safe; urgency=high luôn cross; sell passive = nằm ở ask). **A/B paper**: account `[REDACTED]` (control, override [REDACTED]) vs `[REDACTED]` (treatment) trong trading_bot_accounts.json — cùng plan V2.3 scale 1B, đọc `bot_ab_report.py` (so vwap theo date×ticker×side, dương=dip tốt hơn, lịch sử data/exec_ab_history.csv; kết luận sau ~3-4 tuần, kỳ vọng +2-3.5bps t>2). Account live `[REDACTED]` PIN cross_mode=[REDACTED] tới khi A/B xác nhận. Lưu ý [REDACTED]12 book V2.3 paper mới go-live 100% cash + recs rỗng → plan 0 lệnh là đúng; A/B có data khi V2.3 bắt đầu vào lệnh.

Liên quan: [[vn30f_intraday_orb_2026]] (nguồn 2 finding gốc), [[trading_bot_phs_2026]].
