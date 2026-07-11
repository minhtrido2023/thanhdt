#!/usr/bin/env python3
"""
refresh_fa_ratings.py — append-only weekly refresh of `tav2_bq.fa_ratings`.

Continuation of feasibility job Taylor_20260711_145129 (quant-skeptic CONFIRMED):
the original builder `fundamental_rating.py` was never lost (lineage 100% — 12,367/12,367
rows of the frozen table match data/fundamental_rating_all.csv), and a full rebuild today
reproduces 82.3% exact tier / 99.9% within ±1 tier. The 18% drift is retroactive
dividend-adjusted Close → liquidity cohort membership → percentile boundary flips near
tier edges — NOT a formula error (user confirmed the cause and accepted statistical-match
verification for old quarters; byte-equality is NOT required).

Append-only design (protects every pinned backtest that as-of joins this table):
- FROZEN quarters = everything already published EXCEPT the 2 most recent published
  quarters. Never re-ranked, never rewritten — the publish step is DELETE(open) +
  INSERT(new) inside one BigQuery transaction, so frozen rows are physically untouched.
- OPEN quarters = the 2 most recent published quarters. BCTC arrives over weeks; late
  filers change the per-quarter percentile cohort → re-ranked wholesale every run.
- NEW quarters append only once their cohort reaches MIN_COHORT rows. A tiny cohort makes
  per-quarter percentiles meaningless (a 1-row cohort gets score_pct=1.0 → spurious tier
  A straight into SIGNAL_V11's fa_tier gate). Until the gate opens, as-of consumers keep
  extending the previous quarter's tier — exactly what the frozen table already does.

Safety gates, in order, before any BQ write:
1. Fresh build sanity — row floor, every published open quarter still present at ≥80%
   of its published row count (guards against upstream data loss).
2. Statistical frozen-quarter match — rebuild vs published on frozen quarters:
   exact-tier ≥ FLOOR_EXACT (70%), ±1-tier ≥ FLOOR_WITHIN1 (99%). Measured baseline
   2026-07-11: 82.27% / 99.91%. Falling far below that is NOT natural price drift —
   ABORT, publish nothing, exit non-zero so the cron wrapper alerts.
3. Publish = staging-table load (explicit schema copied from the live table) +
   one multi-statement transaction (DELETE open quarters; INSERT staging).
4. Post-publish verify — re-count from BQ: frozen rows unchanged, open/new quarter
   counts match what we staged.

Only after a successful publish are the three local canonical CSVs
(data/fundamental_rating{,_all,_latest}.csv) rewritten to mirror the table (the 05-10
originals are backed up once as *_pre_refresh_backup_20260510.csv — they are the lineage
evidence for the frozen table).

Usage:
  python3 refresh_fa_ratings.py --dry-run   # full build + all verifications, no BQ write
  python3 refresh_fa_ratings.py             # real refresh (cron path)
"""
import warnings; warnings.filterwarnings("ignore")
import json, os, shutil, subprocess, sys, tempfile
from io import StringIO

import numpy as np, pandas as pd

ROOT       = os.path.dirname(os.path.abspath(__file__))
PROJECT    = "lithe-record-440915-m9"
TABLE      = "tav2_bq.fa_ratings"
STAGING_TB = "tav2_bq.fa_ratings_refresh_staging"
STAGE_DIR  = os.path.join(ROOT, "data", "fa_ratings_refresh")

MIN_COHORT    = int(os.environ.get("FA_MIN_COHORT", "30"))    # rows before a NEW quarter is appended
FLOOR_EXACT   = float(os.environ.get("FA_FLOOR_EXACT", "0.70"))    # frozen-quarter exact-tier floor
FLOOR_WITHIN1 = float(os.environ.get("FA_FLOOR_WITHIN1", "0.99"))  # frozen-quarter ±1-tier floor
MIN_BUILD_ROWS = 11000    # frozen table is 12,367 and history only grows
OPEN_SHRINK_FLOOR = 0.80  # an open quarter losing >20% of its published rows = upstream data loss

TIER_ORD = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}

CANON = {  # local canonical CSVs (mirrors of the table, rewritten post-publish only)
    "all":    os.path.join(ROOT, "data", "fundamental_rating_all.csv"),
    "q4":     os.path.join(ROOT, "data", "fundamental_rating.csv"),
    "latest": os.path.join(ROOT, "data", "fundamental_rating_latest.csv"),
}

def log(msg): print(msg, flush=True)

def die(msg):
    log(f"ABORT: {msg}")
    sys.exit(1)

# ─── BQ helpers (bq CLI, same convention as the builder) ─────────────────────
def bq_query_df(sql, label=""):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        r = subprocess.run(
            f'cat "{tmp}" | bq query --use_legacy_sql=false --project_id={PROJECT} '
            f'--format=csv --max_rows=10000000',
            capture_output=True, text=True, timeout=900, shell=True)
    finally:
        try: os.unlink(tmp)
        except OSError: pass
    if r.returncode != 0:
        raise RuntimeError(f"[BQ ERROR] {label}: {(r.stdout or r.stderr)[:600]}")
    txt = r.stdout.strip()
    return pd.read_csv(StringIO(txt)) if txt else pd.DataFrame()

def bq_run(args, label, timeout=600):
    r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"[BQ ERROR] {label}: {(r.stderr or r.stdout)[:800]}")
    return r.stdout

def table_schema():
    out = bq_run(["bq", "show", "--schema", "--format=prettyjson", f"{PROJECT}:{TABLE}"],
                 "show schema")
    return json.loads(out)

# ─── Step 1: fresh full build via the original builder, into the staging dir ─
def run_builder():
    os.makedirs(STAGE_DIR, exist_ok=True)
    env = dict(os.environ,
               FA_OUT_CSV=os.path.join(STAGE_DIR, "stage_q4.csv"),
               FA_OUT_ALL=os.path.join(STAGE_DIR, "stage_all.csv"),
               FA_OUT_LATEST=os.path.join(STAGE_DIR, "stage_latest.csv"))
    log("=== [1/6] Running fundamental_rating.py (full rebuild → staging) ===")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "fundamental_rating.py")],
                       cwd=ROOT, env=env, capture_output=True, text=True, timeout=1800)
    tail = "\n".join((r.stdout or "").splitlines()[-15:])
    log(tail)
    if r.returncode != 0:
        die(f"builder exit={r.returncode}: {(r.stderr or r.stdout)[-800:]}")
    fresh = pd.read_csv(env["FA_OUT_ALL"])
    if len(fresh) < MIN_BUILD_ROWS:
        die(f"fresh build only {len(fresh)} rows (< {MIN_BUILD_ROWS}) — upstream data problem")
    return fresh

# ─── Step 2/3: download published table, classify quarters, verify ───────────
def verify_and_split(fresh):
    log("=== [2/6] Downloading published table ===")
    pub = bq_query_df(f"SELECT * FROM `{PROJECT}.{TABLE}`", "download published")
    log(f"  published: {len(pub):,} rows, {pub.quarter.nunique()} quarters, "
        f"max quarter {pub.quarter.max()}")

    pub_quarters  = sorted(pub.quarter.unique())
    open_quarters = pub_quarters[-2:]
    frozen_q      = set(pub_quarters[:-2])
    log(f"  open (re-rank): {open_quarters} | frozen: {len(frozen_q)} quarters")

    # open quarters must still exist in the fresh build at sane size
    for q in open_quarters:
        n_new, n_pub = (fresh.quarter == q).sum(), (pub.quarter == q).sum()
        if n_new < OPEN_SHRINK_FLOOR * n_pub:
            die(f"open quarter {q}: fresh build {n_new} rows < {OPEN_SHRINK_FLOOR:.0%} of "
                f"published {n_pub} — upstream data loss?")

    log("=== [3/6] Statistical match on FROZEN quarters (rebuild vs published) ===")
    fz_pub   = pub[pub.quarter.isin(frozen_q)][["ticker", "quarter", "tier", "score_pct"]]
    fz_fresh = fresh[fresh.quarter.isin(frozen_q)][["ticker", "quarter", "tier", "score_pct"]]
    m = fz_pub.merge(fz_fresh, on=["ticker", "quarter"], suffixes=("_pub", "_new"))
    if len(m) < 0.85 * len(fz_pub):
        die(f"frozen overlap only {len(m)}/{len(fz_pub)} keys (<85%) — universe collapsed?")
    d = (m.tier_pub.map(TIER_ORD) - m.tier_new.map(TIER_ORD)).abs()
    exact, within1 = (d == 0).mean(), (d <= 1).mean()
    log(f"  overlap {len(m):,}/{len(fz_pub):,} | exact tier {exact:.2%} | ±1 tier {within1:.2%} "
        f"| mean |Δscore_pct| {(m.score_pct_pub - m.score_pct_new).abs().mean():.4f}")
    log(f"  (baseline 2026-07-11: 82.27% / 99.91% — floors {FLOOR_EXACT:.0%} / {FLOOR_WITHIN1:.0%})")
    if exact < FLOOR_EXACT or within1 < FLOOR_WITHIN1:
        die(f"frozen-quarter match {exact:.2%}/{within1:.2%} below floors "
            f"{FLOOR_EXACT:.0%}/{FLOOR_WITHIN1:.0%} — NOT normal price drift, investigate "
            f"before publishing (per user directive 2026-07-11)")

    # rows to publish: re-ranked open quarters + new quarters past the cohort gate
    new_quarters = sorted(q for q in fresh.quarter.unique() if q > pub_quarters[-1])
    publish_q, skipped = list(open_quarters), []
    for q in new_quarters:
        n = (fresh.quarter == q).sum()
        (publish_q if n >= MIN_COHORT else skipped).append(q)
        if n < MIN_COHORT:
            log(f"  NEW quarter {q}: cohort {n} < {MIN_COHORT} — NOT appended yet "
                f"(as-of consumers keep extending the previous tier)")
    out = fresh[fresh.quarter.isin(publish_q)].copy()
    # table stores ICB_Code as FLOAT; builder writes "UNK" for missing — coerce to NULL
    out["ICB_Code"] = pd.to_numeric(out["ICB_Code"], errors="coerce")
    log(f"  publishing quarters {publish_q}: {len(out):,} rows "
        f"(published had {pub.quarter.isin(open_quarters).sum():,} in open quarters)")
    return pub, out, open_quarters, frozen_q, skipped

# ─── Step 4/5: stage + transactional publish ─────────────────────────────────
def publish(out_rows, open_quarters, pub, frozen_q, dry_run):
    schema = table_schema()
    cols = [f["name"] for f in schema]
    missing = [c for c in cols if c not in out_rows.columns]
    if missing:
        die(f"fresh build missing table columns: {missing}")
    stage = out_rows[cols].copy()
    stage_csv = os.path.join(STAGE_DIR, "stage_publish.csv")
    stage.to_csv(stage_csv, index=False)

    q_list = ", ".join(f"'{q}'" for q in sorted(set(stage.quarter)))
    dml = (f"BEGIN TRANSACTION;\n"
           f"DELETE FROM `{PROJECT}.{TABLE}` WHERE quarter IN ({q_list});\n"
           f"INSERT INTO `{PROJECT}.{TABLE}` SELECT * FROM `{PROJECT}.{STAGING_TB}`;\n"
           f"COMMIT TRANSACTION;")
    if dry_run:
        log("=== [4/6] DRY-RUN — staged CSV written, BQ untouched ===")
        log(f"  staging csv: {stage_csv} ({len(stage):,} rows)")
        log("  would run:\n    bq load --replace (schema of live table) "
            f"{STAGING_TB} {os.path.basename(stage_csv)}\n" +
            "\n".join("    " + l for l in dml.splitlines()))
        return
    log("=== [4/6] Loading staging table ===")
    schema_file = os.path.join(STAGE_DIR, "stage_schema.json")
    with open(schema_file, "w") as f:
        json.dump(schema, f)
    bq_run(["bq", "load", "--replace", "--source_format=CSV", "--skip_leading_rows=1",
            f"--schema={schema_file}", f"--project_id={PROJECT}", STAGING_TB, stage_csv],
           "load staging", timeout=600)
    n_stage = int(bq_query_df(
        f"SELECT COUNT(*) AS n FROM `{PROJECT}.{STAGING_TB}`", "count staging").n.iloc[0])
    if n_stage != len(stage):
        die(f"staging table has {n_stage} rows, expected {len(stage)}")

    log("=== [5/6] Transactional publish (DELETE open + INSERT staging) ===")
    bq_query_df(dml, "publish transaction")

    chk = bq_query_df(
        f"SELECT quarter, COUNT(*) AS n FROM `{PROJECT}.{TABLE}` GROUP BY quarter",
        "post-publish counts").set_index("quarter").n
    n_frozen_now = int(chk[chk.index.isin(frozen_q)].sum())
    n_frozen_was = int(pub.quarter.isin(frozen_q).sum())
    if n_frozen_now != n_frozen_was:
        die(f"POST-PUBLISH CHECK FAILED: frozen rows {n_frozen_was} → {n_frozen_now} — "
            f"frozen history was touched, investigate immediately")
    for q, n in stage.quarter.value_counts().items():
        if int(chk.get(q, 0)) != int(n):
            die(f"POST-PUBLISH CHECK FAILED: quarter {q} has {chk.get(q, 0)} rows, staged {n}")
    log(f"  OK — frozen rows unchanged ({n_frozen_now:,}), "
        f"published quarters match staging, total {int(chk.sum()):,} rows")

# ─── Step 6: mirror the table into the local canonical CSVs ──────────────────
def update_local_csvs(pub, out_rows, open_quarters):
    log("=== [6/6] Updating local canonical CSVs (post-publish mirror) ===")
    for path in CANON.values():
        bak = path.replace(".csv", "_pre_refresh_backup_20260510.csv")
        if os.path.exists(path) and not os.path.exists(bak):
            shutil.copy2(path, bak)
            log(f"  backup: {os.path.basename(bak)}")
    frozen_rows = pub[~pub.quarter.isin(set(out_rows.quarter) | set(open_quarters))]
    merged = pd.concat([frozen_rows, out_rows[frozen_rows.columns]], ignore_index=True)
    merged = merged.sort_values(["time", "tier", "ticker"], ascending=[False, True, True])
    merged.to_csv(CANON["all"], index=False)
    q4 = merged[merged.quarter.str.endswith("Q4")]
    q4.to_csv(CANON["q4"], index=False)
    latest = (q4.sort_values("time").groupby("ticker", as_index=False).tail(1)
                .sort_values(["tier", "total_score"], ascending=[True, False]))
    drop = [c for c in ("profit_3M", "DY_sust") if c in latest.columns]
    latest.drop(columns=drop).to_csv(CANON["latest"], index=False)
    log(f"  {CANON['all']} ({len(merged):,}) | q4 ({len(q4):,}) | latest ({len(latest):,})")

def main():
    dry_run = "--dry-run" in sys.argv
    fresh = run_builder()
    pub, out_rows, open_quarters, frozen_q, skipped = verify_and_split(fresh)
    publish(out_rows, open_quarters, pub, frozen_q, dry_run)
    if not dry_run:
        update_local_csvs(pub, out_rows, open_quarters)
    log(f"DONE{' (dry-run)' if dry_run else ''}"
        + (f" — skipped small new quarters: {skipped}" if skipped else ""))

if __name__ == "__main__":
    main()
