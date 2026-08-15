---
kind: group-index
group: price-volume
title: Giá / khối lượng cổ phiếu
---

# Giá / khối lượng cổ phiếu

| Nguồn (file) | Status |
|---|---|
| [`corp_action_pending.md`](corp_action_pending.md) — data/corp_action_pending.json + data/corp_action_backlog.json | VANHANH |
| [`corporate_action_bq.md`](corporate_action_bq.md) — tav2_bq.corporate_action (per-event corp action, mới tạo 2026-08-12) | TRAP |
| [`dnse_api_live.md`](dnse_api_live.md) — DNSE API live (dnse_api.py secdef/latest_trade/positions/balances) | CANONICAL |
| [`shares_outstanding_live.md`](shares_outstanding_live.md) — tav2_bq.shares_outstanding_live | CANONICAL |
| [`ticker_close_vs_price_dividend_adj.md`](ticker_close_vs_price_dividend_adj.md) — cặp cột Close (đã điều chỉnh) vs Price (thô) trong tav2_bq.ticker | TRAP |
| [`ticker_ohlcv_tables.md`](ticker_ohlcv_tables.md) — tav2_bq.ticker / ticker_1m / ticker_prune | CANONICAL |
| [`ticker_price_stale_on_exdate.md`](ticker_price_stale_on_exdate.md) — cột Price của tav2_bq.ticker/ticker_prune ĐÚNG NGÀY GDKHQ có thể kẹt ở hệ CUM (ca VHM 2026-08-06 sai +98,4%) | TRAP |
| [`ticker_prune.md`](ticker_prune.md) — tav2_bq.ticker_prune | TRAP |
| [`universe_pit.md`](universe_pit.md) — lithe-record-440915-m9.tav2_mike.universe_pit | CANONICAL |
| [`universe_pit_quality.md`](universe_pit_quality.md) — lithe-record-440915-m9.tav2_mike.universe_pit_quality | CANONICAL |
| [`vnindex_mirror_col.md`](vnindex_mirror_col.md) — cột mirror t.VNINDEX trên hàng CỔ PHIẾU (trong tav2_bq.ticker VÀ ticker_prune) | TRAP |
| [`vnindex_pe_mirror_col.md`](vnindex_pe_mirror_col.md) — cột mirror t.VNINDEX_PE trên hàng CỔ PHIẾU (trong tav2_bq.ticker VÀ ticker_prune) | TRAP (pending fix) |

↩ [Về index tổng](../index.md)
