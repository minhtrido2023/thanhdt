# State vintage reference

Point-in-time snapshots of the 5-state series (`vnindex_5state`) so backtests are reproducible (state machine restates history via non-causal min_stay_filter).

**Use**: a backtest 'as of date D' should load the latest `VINTAGE_<=D` file.
```python
from state_vintage_loader import load_vintage
state_df = load_vintage('2026-05-28')  # or asof=None for latest
```

Daily accumulation: `python snapshot_state_vintage.py` (wire into papertrade_daily.bat).
Seeded 2026-05-28 with 2 historical points (May20 pkl.bak, May28 rebuild) + full BQ snapshot.
