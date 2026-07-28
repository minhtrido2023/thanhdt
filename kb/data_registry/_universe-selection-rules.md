---
kind: rule
status: CANONICAL
group: _rules
title: Quy tắc chọn universe (ticker vs universe_pit vs ticker_prune vs ticker_1m)
---

# Quy tắc chọn universe (ticker vs universe_pit vs ticker_prune vs ticker_1m)

- **Backtest/ML/breadth/chọn rổ — code MỚI** → JOIN `tav2_mike.universe_pit`/`universe_pit_quality` per-day
  vào `tav2_bq.ticker`, **KHÔNG dùng `ticker_prune`** (xem [`price-volume/ticker_prune.md`](price-volume/ticker_prune.md) — TRAP, đang trôi dần
  khỏi universe_pit, không có tín hiệu tự động báo lệch).
- **`ticker_prune`** — chỉ còn hợp lệ cho: (a) 2 consumer live đã ghi rõ điều kiện gỡ (CAPIT pool/ADV,
  `trading_bot/executor.py` R&D flags), (b) research/backtest có TỪ TRƯỚC dự án migrate 2026-07-22 (không
  bắt buộc sửa ngay, nhưng đừng coi là "đúng" khi đối chiếu với số mới trên `universe_pit`), (c) freshness
  monitoring của chính bảng này (`preflight_check.sh`) chừng nào (a) còn tồn tại. Breadth chỉ có nghĩa từ ~2008.
- **Live screening/daily eval** → `ticker_1m` (có Trading_Value, pattern stats, outcome cols).
- **`ticker` full** → chỉ khi cần phủ toàn bộ mã (15.2M rows, có đuôi illiquid có thể trễ ingest
  — freshness triage chỉ tính `ticker_prune`+VNINDEX, xem memory `dataops-completeness-universe`).
- Cột `profit_*` (forward-looking) ở mọi bảng: CHỈ để train, cấm dùng filter live.
