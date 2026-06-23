# Experiment Protocol — 3 Tiers

## Overview

Three-tier ladder: explore cheaply with local snapshots → validate locally → audit once with fresh BQ.
Tier 1 and 2 are zero-BQ (use Winston's daily parquet snapshots). Tier 3 burns one BQ scan and is
required before any go-live or results_registry.md pinning.

---

## Tier 1: Explore (local snapshot, no self-check)

**Goal**: fast parameter sweep, leaderboard, discard losers.

```bash
# Run all built-in configs:
LOCAL_SNAPSHOT_DIR=data/snapshots SELFCHECK=0 python sweep_configs.py --mode v23a

# Or pass a custom config file:
python sweep_configs.py my_configs.json --snapshot data/snapshots --selfcheck 0

# Save leaderboard to JSON:
python sweep_configs.py --output /tmp/tier1_results.json
```

**Cost**: 0 BQ scans. Each run reads parquet snapshots from `data/snapshots/`.
**Speed**: seconds–minutes per config (no network round-trip).
**Verdict**: identify top-3 candidates by CAGR + Sharpe. Eliminate rest.

---

## Tier 2: Validate (local snapshot + self-check enabled)

**Goal**: confirm top-3 from Tier 1 pass the internal self-check reconciliation (selfcheck ≈ 0 VND).

```bash
# Run a single top-3 candidate with self-check on:
LOCAL_SNAPSHOT_DIR=data/snapshots python pt_v23_audit_2014.py v23a

# Or via sweep with SELFCHECK=1:
python sweep_configs.py top3_configs.json --selfcheck 1
```

**Cost**: 0 BQ scans.
**Acceptance gate**: `selfcheck` VND residual < 1 000 VND (rounding tolerance).
Reject any config that fails the self-check — it has a cash-flow inconsistency.

---

## Tier 3: Audit (fresh BigQuery pull, production gate)

**Goal**: full IS/OOS audit on live BQ data. Pin results before go-live.

```bash
# Unset LOCAL_SNAPSHOT_DIR to force real BQ:
unset LOCAL_SNAPSHOT_DIR
python pt_v23_audit_2014.py v23a

# Or explicitly:
LOCAL_SNAPSHOT_DIR="" python pt_v23_audit_2014.py v23a
```

**Cost**: 1 BQ full-history scan (~16 GB `ticker` table).
**Required before**: any go-live promotion, results_registry.md update, KB pinning.
**Checklist**:
- [ ] IS 2014–2019 metrics match prior pinned run (CAGR ± 0.05pp)
- [ ] OOS 2020–now Calmar ≥ IS Calmar (no overfit signal)
- [ ] Self-check residual < 1 000 VND
- [ ] MaxDD < -40% (risk bound)
- [ ] Output CSV committed to `data/v23_golive_audit_<date>.csv`

---

## Snapshot freshness

Winston's pipeline refreshes `data/snapshots/signal_YYYYMMDD.parquet` and
`data/snapshots/vni_YYYYMMDD.parquet` daily (cron). Before a Tier-2 run, verify:

```bash
ls -lt data/snapshots/*.parquet | head -5
cat data/snapshots/latest_date.txt
```

A snapshot older than 2 trading days should be treated as stale — run Tier 3 (real BQ) instead.
