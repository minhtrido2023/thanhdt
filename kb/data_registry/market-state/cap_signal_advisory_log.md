---
kind: script-output
status: CANONICAL (advisory-only, không có consumer quyết định tự động)
source: kb/data_registry/market-state/cap_signal_advisory_log.csv
group: market-state
writer: mike/agents/Taylor/cap_signal_advisory_check.py — chạy tay/cron tuỳ chọn, KHÔNG phải cron mặc định
role: sổ tích luỹ CỤM MACRO ĐỘC LẬP cho CAP_SIGNAL composite, phục vụ ngưỡng nâng cấp N_clusters>=10
---

# `kb/data_registry/market-state/cap_signal_advisory_log.csv`

**Status: CANONICAL cho advisory CAP_SIGNAL** — user duyệt 2026-08-30 21:10 ICT (decided_by=user,
job Taylor_20260830_141109). Nguồn gốc + verify đầy đủ:
`agents/Taylor/research/diverge_indicator_strategy_backtest_round2_20260830.md` (quant-skeptic
CONFIRMED medium confidence). Xem thêm quyết định gốc:
`kb/projects/cap-signal-advisory-20260830.md`.

## Là gì
Mỗi dòng = 1 lần CAP_SIGNAL fire mới (chưa từng ghi ngày đó). Composite =
DIVERGE (EM_dd60<=-8% AND VNI_dd60>=-3%) AND xác nhận (DXY_mom60>=5% OR TNX>=3.0) — ngưỡng
PRE-REGISTERED, khớp `production_mechanism_2009_2018_20260830.md` §B.2 +
`cap_signal_grid_test_round2.py`, KHÔNG re-tune.

Cột: `fire_date`, `cluster_id` (int, gộp các fire cách nhau <=60 ngày lịch vào 1 cụm macro),
`EM_dd60`, `VNI_dd60`, `DXY_mom60`, `TNX` (giá trị chỉ báo tại ngày fire), `checked_at_ict`.

## Ai ghi / cadence
`mike/agents/Taylor/cap_signal_advisory_check.py` — KHÔNG có cron mặc định (chạy tay hoặc
nhúng vào report cadence sẵn có theo đề xuất trong project doc). Script tự dedupe theo
`fire_date` — chạy nhiều lần/ngày không tạo dòng trùng.

## Nguồn dữ liệu SỐNG dùng để tính (KHÔNG dùng `data/tier2_macro_panel.csv`)
- VNI (VNINDEX Close) — `tav2_bq.ticker` (sync nightly 23:45 ICT, đọc same-day có độ trễ theo
  §CLAUDE.md "same-day: DNSE API, KHÔNG BQ" — advisory này KHÔNG phải same-day live nên BQ OK).
- EEM / DXY (`DX-Y.NYB`) / TNX (`^TNX`) — `yfinance`, verify sống 2026-08-30. Dòng cuối có thể
  NaN nếu phiên Mỹ chưa đóng cửa tại giờ VN fetch — script tự `dropna` trước khi tính rolling,
  KHÔNG dùng dòng chưa hoàn tất.

## Bẫy
- `data/tier2_macro_panel.csv` (nguồn của backtest gốc) **đóng băng 2026-05-15, KHÔNG refresh**
  — chỉ dùng cho backtest lịch sử, KHÔNG dùng cho advisory sống. Script này build lại pipeline
  tương đương từ nguồn SỐNG, không đọc file đó.
- Đơn vị N cho ngưỡng nâng cấp là **CỤM ĐỘC LẬP** (`cluster_id.nunique()`), không phải số dòng —
  khớp đúng cách đếm N=6 trong nghiên cứu round2 (leave-one-out theo cụm, không theo lần fire).
- Ngưỡng nâng cấp N_clusters>=10 chỉ TỰ BẮN 1 bus `question` đề xuất xem xét — KHÔNG tự wire.
  Wire production vẫn cần qua quant-skeptic + user duyệt như mọi thay đổi production khác.
