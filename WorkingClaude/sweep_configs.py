#!/usr/bin/env python3
"""sweep_configs.py — Tier-1 fast experiment runner (local snapshot, no BQ).

Usage:
  python sweep_configs.py [--snapshot data/snapshots] [--mode v23a] [config_file.json]

Config file JSON format (or uses hardcoded CONFIGS list when no file given):
  [
    {"label": "baseline",    "env": {}},
    {"label": "park095",     "env": {"RECOVERY_PARK": "1", "RECOVERY_WMAX": "0.95"}},
    {"label": "park095_fl7", "env": {"RECOVERY_PARK": "1", "RECOVERY_WMAX": "0.95", "DEPOSIT_FLOOR": "0.075"}},
    ...
  ]

Output: sorted leaderboard table (CAGR / Sharpe / MaxDD / Calmar / selfcheck)

Environment:
  LOCAL_SNAPSHOT_DIR — set automatically from --snapshot arg; can also be pre-set in env
  SELFCHECK          — set to "0" for Tier-1 speed (skips self-check reconciliation)
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from typing import Any

# ─── Default CONFIGS (used when no config file given) ────────────────────────
# Add / modify here for quick sweeps; override entirely by passing a JSON file.
CONFIGS: list[dict[str, Any]] = [
    {"label": "baseline",       "env": {}},
    {"label": "park095",        "env": {"RECOVERY_PARK": "1", "RECOVERY_WMAX": "0.95"}},
    {"label": "park095_fl7",    "env": {"RECOVERY_PARK": "1", "RECOVERY_WMAX": "0.95", "DEPOSIT_FLOOR": "0.075"}},
    {"label": "park080",        "env": {"RECOVERY_PARK": "1", "RECOVERY_WMAX": "0.80"}},
    {"label": "nopark",         "env": {"RECOVERY_PARK": "0"}},
]

# ─── Metric extraction patterns ───────────────────────────────────────────────
# These regexes match the summary output printed by pt_v23_audit_2014.py / simulate_holistic_nav.py
_METRIC_PATTERNS = {
    "CAGR":    re.compile(r"CAGR[=%\s]+([+-]?\d+\.?\d*)"),
    "Sharpe":  re.compile(r"Sharpe[=:\s]+([+-]?\d+\.?\d*)"),
    "MaxDD":   re.compile(r"MaxDD[=%\s]+([+-]?\d+\.?\d*)"),
    "Calmar":  re.compile(r"Calmar[=:\s]+([+-]?\d+\.?\d*)"),
    "selfcheck": re.compile(r"self.?check[=:\s]*([+-]?\d+\.?\d*)", re.IGNORECASE),
}


def _parse_metrics(stdout: str) -> dict[str, float | None]:
    """Extract key metrics from stdout of a simulation run."""
    metrics: dict[str, float | None] = {k: None for k in _METRIC_PATTERNS}
    for key, pat in _METRIC_PATTERNS.items():
        m = pat.search(stdout)
        if m:
            try:
                metrics[key] = float(m.group(1))
            except ValueError:
                metrics[key] = None
    return metrics


def run_one(config: dict[str, Any], base_env: dict[str, str], mode: str,
            timeout: int = 1800) -> dict[str, Any]:
    """Fork a subprocess for one config and capture stdout/stderr + metrics.

    Returns a result dict with label, env, metrics, elapsed_s, returncode, stdout_tail.
    """
    label = config["label"]
    extra_env = config.get("env", {})
    env = {**base_env, **extra_env}

    cmd = [sys.executable, "pt_v23_audit_2014.py", mode]
    print(f"[sweep] Starting '{label}' (mode={mode}) ...")
    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=os.path.dirname(os.path.abspath(__file__)) or ".",
            timeout=timeout,
        )
        elapsed = time.monotonic() - t0
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - t0
        print(f"  [sweep] '{label}' TIMEOUT after {elapsed:.0f}s")
        return {
            "label": label, "env": extra_env,
            "CAGR": None, "Sharpe": None, "MaxDD": None, "Calmar": None, "selfcheck": None,
            "elapsed_s": elapsed, "returncode": -1, "stdout_tail": "", "error": "TIMEOUT",
        }

    metrics = _parse_metrics(stdout)
    status = "OK" if rc == 0 else f"ERR(rc={rc})"
    stdout_tail = stdout[-2000:] if len(stdout) > 2000 else stdout
    print(f"  [sweep] '{label}' done in {elapsed:.1f}s — {status} | "
          f"CAGR={metrics['CAGR']} Sharpe={metrics['Sharpe']} "
          f"MaxDD={metrics['MaxDD']} Calmar={metrics['Calmar']} "
          f"selfcheck={metrics['selfcheck']}")
    if rc != 0:
        # Print last few lines of stderr to help diagnose failures
        err_tail = (stderr or "").strip().split("\n")[-10:]
        print("  [sweep] stderr tail:\n" + "\n".join(f"    {l}" for l in err_tail))

    return {
        "label": label,
        "env": extra_env,
        **metrics,
        "elapsed_s": elapsed,
        "returncode": rc,
        "stdout_tail": stdout_tail,
        "error": None if rc == 0 else f"rc={rc}",
    }


def print_leaderboard(results: list[dict[str, Any]]) -> None:
    """Print sorted leaderboard table to stdout."""
    # Sort: first by CAGR desc (None last), then by Sharpe desc
    def sort_key(r):
        cagr = r.get("CAGR")
        sharpe = r.get("Sharpe")
        return (-(cagr if cagr is not None else -9999),
                -(sharpe if sharpe is not None else -9999))

    ranked = sorted(results, key=sort_key)

    col_w = {"rank": 5, "label": 24, "CAGR": 8, "Sharpe": 8,
              "MaxDD": 8, "Calmar": 8, "selfcheck": 12, "elapsed_s": 9, "error": 12}

    def fmt_f(v, decimals=2):
        if v is None:
            return "N/A"
        return f"{v:.{decimals}f}"

    header = (f"{'#':>{col_w['rank']}}  {'label':<{col_w['label']}}  "
              f"{'CAGR%':>{col_w['CAGR']}}  {'Sharpe':>{col_w['Sharpe']}}  "
              f"{'MaxDD%':>{col_w['MaxDD']}}  {'Calmar':>{col_w['Calmar']}}  "
              f"{'selfcheck':>{col_w['selfcheck']}}  {'sec':>{col_w['elapsed_s']}}  "
              f"{'status':<{col_w['error']}}")
    sep = "─" * len(header)
    print("\n" + sep)
    print("  SWEEP LEADERBOARD  (sorted by CAGR desc)")
    print(sep)
    print(header)
    print(sep)
    for rank, r in enumerate(ranked, 1):
        err_str = r.get("error") or "OK"
        print(f"{rank:>{col_w['rank']}}  {r['label']:<{col_w['label']}}  "
              f"{fmt_f(r.get('CAGR')):>{col_w['CAGR']}}  "
              f"{fmt_f(r.get('Sharpe')):>{col_w['Sharpe']}}  "
              f"{fmt_f(r.get('MaxDD')):>{col_w['MaxDD']}}  "
              f"{fmt_f(r.get('Calmar')):>{col_w['Calmar']}}  "
              f"{fmt_f(r.get('selfcheck'), 0):>{col_w['selfcheck']}}  "
              f"{fmt_f(r.get('elapsed_s'), 1):>{col_w['elapsed_s']}}  "
              f"{err_str:<{col_w['error']}}")
    print(sep + "\n")


def main():
    parser = argparse.ArgumentParser(description="Sweep experiment configs against local parquet snapshots.")
    parser.add_argument("config_file", nargs="?", default=None,
                        help="JSON config file with list of {label, env} dicts (optional; uses builtin CONFIGS if omitted)")
    parser.add_argument("--snapshot", default=os.environ.get("LOCAL_SNAPSHOT_DIR", "data/snapshots"),
                        help="Path to local snapshot directory (default: data/snapshots)")
    parser.add_argument("--mode", default="v23a",
                        choices=["v23a", "v23c", "v22base", "singlebook"],
                        help="Simulation mode passed to pt_v23_audit_2014.py (default: v23a)")
    parser.add_argument("--selfcheck", default="0",
                        help="SELFCHECK env value (default: 0 = skip for speed)")
    parser.add_argument("--timeout", type=int, default=1800,
                        help="Per-experiment timeout in seconds (default: 1800)")
    parser.add_argument("--output", default=None,
                        help="Save leaderboard results to this JSON file")
    args = parser.parse_args()

    # Load configs
    if args.config_file:
        with open(args.config_file, encoding="utf-8") as f:
            configs = json.load(f)
        print(f"[sweep] Loaded {len(configs)} configs from {args.config_file}")
    else:
        configs = CONFIGS
        print(f"[sweep] Using {len(configs)} built-in configs")

    # Validate snapshot dir
    snap_dir = os.path.abspath(args.snapshot)
    if not os.path.isdir(snap_dir):
        print(f"[sweep] WARNING: snapshot dir does not exist: {snap_dir!r}")
        print("        Winston's pipeline must create snapshots before Tier-1 runs work.")
        print("        Continuing anyway — individual runs will fail with FileNotFoundError.")
    else:
        snap_files = [f for f in os.listdir(snap_dir) if f.endswith(".parquet")]
        if snap_files:
            print(f"[sweep] Snapshot dir: {snap_dir!r} ({len(snap_files)} parquet files found)")
        else:
            print(f"[sweep] WARNING: snapshot dir exists but has NO .parquet files: {snap_dir!r}")

    # Build base environment: inherit current env + LOCAL_SNAPSHOT_DIR + SELFCHECK
    base_env = {**os.environ, "LOCAL_SNAPSHOT_DIR": snap_dir, "SELFCHECK": args.selfcheck}

    print(f"[sweep] Mode={args.mode}, SELFCHECK={args.selfcheck}, timeout={args.timeout}s")
    print(f"[sweep] Running {len(configs)} experiments sequentially ...\n")

    t_start = time.monotonic()
    results = []
    for cfg in configs:
        r = run_one(cfg, base_env=base_env, mode=args.mode, timeout=args.timeout)
        results.append(r)

    elapsed_total = time.monotonic() - t_start
    print(f"\n[sweep] All {len(configs)} experiments done in {elapsed_total:.1f}s total.")

    print_leaderboard(results)

    # Optionally save to JSON
    if args.output:
        # Make serializable: convert None to null, floats stay floats
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"[sweep] Results saved to {args.output}")

    # Exit with non-zero if any experiment failed
    failed = [r["label"] for r in results if r.get("error")]
    if failed:
        print(f"[sweep] {len(failed)} experiment(s) failed: {failed}")
        sys.exit(1)


if __name__ == "__main__":
    main()
