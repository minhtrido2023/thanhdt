# -*- coding: utf-8 -*-
"""sweep_basket_size_cap.py — C+D sweep: basket SIZE (top_n) x single-name CAP (name_cap).
Runs the BQ-auditable pt_v23_audit_2014.py once per (NAV, top_n, name_cap) cell with the
production deploy config (v23a none postbull 0.0 edge) + custompitg + namecap weighting.
Parses the printed CAGR/Sharpe/MaxDD/Calmar line and writes a tidy grid CSV.

Usage: python sweep_basket_size_cap.py <NAV_B> <topn_csv> <namecap_csv>
  e.g. python sweep_basket_size_cap.py 500 15,20,25,30,40 0.08,0.10,0.12,0.15
"""
import os, sys, re, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

NAV = sys.argv[1] if len(sys.argv) > 1 else "500"
TOPNS = [int(x) for x in (sys.argv[2] if len(sys.argv) > 2 else "15,20,25,30,40").split(",")]
CAPS = [float(x) for x in (sys.argv[3] if len(sys.argv) > 3 else "0.08,0.10,0.12,0.15").split(",")]
WORKERS = int(sys.argv[4]) if len(sys.argv) > 4 else 6
OUT = f"data/basket_size_cap_sweep_nav{NAV}B.csv"

METRIC_RE = re.compile(
    r"CAGR\s+([\d.\-]+)%\s+Sharpe\(252\)\s+([\d.\-]+)\s+MaxDD\s+([\d.\-]+)%\s+Calmar\s+([\d.\-]+)")
FINALNAV_RE = re.compile(r"Final NAV\s+([\d,\.]+)B")
CELLS = [(tn, cap) for tn in TOPNS for cap in CAPS]


def run_cell(tn, cap):
    env = dict(os.environ)
    env.update(ETF_LIQ="custompitg", BASKET_WT="namecap", NAV_TOTAL_B=NAV,
               BASKET_TOPN=str(tn), BASKET_NAMECAP=str(cap), PARK_STATES="3:0.7")
    t0 = time.time()
    p = subprocess.run([sys.executable, "pt_v23_audit_2014.py", "v23a", "none", "postbull", "0.0", "edge"],
                       env=env, capture_output=True, text=True)
    dt = time.time() - t0
    out = p.stdout + "\n" + p.stderr
    m = METRIC_RE.search(out); fn = FINALNAV_RE.search(out)
    if not m:
        print(f"[FAIL] topn={tn} cap={cap}: no metric line ({dt:.0f}s)\n{out[-1200:]}", flush=True)
        return dict(nav=NAV, top_n=tn, name_cap=cap, cagr=None, sharpe=None,
                    maxdd=None, calmar=None, final_nav_b=None, secs=round(dt))
    cagr, sh, dd, cal = (float(x) for x in m.groups())
    fnav = float(fn.group(1).replace(",", "")) if fn else None
    print(f"[OK] topn={tn:>2} cap={cap:.2f}: CAGR {cagr:6.2f}%  Sh {sh:.2f}  DD {dd:6.1f}%  "
          f"Cal {cal:.2f}  ({dt:.0f}s)", flush=True)
    return dict(nav=NAV, top_n=tn, name_cap=cap, cagr=cagr, sharpe=sh,
                maxdd=dd, calmar=cal, final_nav_b=fnav, secs=round(dt))


rows = []
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futs = {ex.submit(run_cell, tn, cap): (tn, cap) for tn, cap in CELLS}
    for f in as_completed(futs):
        rows.append(f.result())
        pd.DataFrame(rows).to_csv(OUT, index=False)

df = pd.DataFrame(rows).sort_values(["top_n", "name_cap"])
df.to_csv(OUT, index=False)
print("\n==== SWEEP RESULT (sorted by CAGR) NAV=" + NAV + "B ====")
print(df.to_string(index=False))
print("-> " + OUT)
