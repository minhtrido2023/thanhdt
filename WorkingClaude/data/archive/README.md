# Archive — deprecated 2026-05-25

These artifacts use the **OLD simplified 5-system spec** (max_positions=10, default
sizing, T-close exec, no RE_BACKLOG_BUY, no SV_TIGHT, no sector_cap_exempt).

**Replaced by:**

- `data/5sys_prodspec_201401_202605.csv` — canonical 12y, prod spec
- `data/5sys_prodspec_<start>_<end>.csv` — fresh-start variants (2018/2020/2022/2024)
- `data/papertrade_canonical_2026-05.md` — primary report
- `run_5systems_prodspec.py` — engine

Reasons for retirement:
1. Spec didn't match production paper-trade → V5 backtest understated by ~0.4-6pp CAGR per period
2. Did not show path-dependency (fresh-start variants) → quoted 12y CAGR was misleading
3. Largest discrepancy: 2026 YTD V5 was +7.06% in old spec vs +13.26% in prod spec (+6.20pp gap)

See `data/papertrade_canonical_2026-05.md` Section F for full caveats.

Files moved here:
- `full_5systems_2014_2026.csv` → daily NAV (old spec, 12y)
- `full_5systems_run.log` → run log of old script
- `papertrade_full_2014_2026.md` → old primary report
- `papertrade_full_2014_2026_metrics.csv` → old metrics
- `papertrade_full_2014_2026_curves.png` → old equity curves
- `papertrade_full_2014_2026_drawdown.png` → old drawdown curves
- `v5_prodspec_2014_2026.csv` → V5-only prod-spec test (superseded by full 5-system run)
- `v5_prodspec_run.log` → V5-only run log
