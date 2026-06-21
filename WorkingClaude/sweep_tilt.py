# -*- coding: utf-8 -*-
"""sweep_tilt.py — dir B: 8L quality-TILT STRENGTH sweep under production weighting.
custompitgq (quality=tilt) + namecap, top_n=30, cap=0.10. Varies BASKET_QTILT preset.
'off' should ~= custompitg (no tilt) baseline (sanity anchor). BQ-auditable; parses metrics."""
import os, sys, re, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

NAV = sys.argv[1] if len(sys.argv) > 1 else "500"
TILTS = (sys.argv[2] if len(sys.argv) > 2 else "off,gentle,default,strong").split(",")
WORKERS = int(sys.argv[3]) if len(sys.argv) > 3 else 4
OUT = f"data/basket_tilt_sweep_nav{NAV}B.csv"
METRIC_RE = re.compile(r"CAGR\s+([\d.\-]+)%\s+Sharpe\(252\)\s+([\d.\-]+)\s+MaxDD\s+([\d.\-]+)%\s+Calmar\s+([\d.\-]+)")


def run_cell(tilt):
    env = dict(os.environ)
    env.update(ETF_LIQ="custompitgq", BASKET_WT="namecap", NAV_TOTAL_B=NAV,
               BASKET_TOPN="30", BASKET_NAMECAP="0.10", BASKET_QTILT=tilt, PARK_STATES="3:0.7")
    t0 = time.time()
    p = subprocess.run([sys.executable, "pt_v23_audit_2014.py", "v23a", "none", "postbull", "0.0", "edge"],
                       env=env, capture_output=True, text=True)
    dt = time.time() - t0
    m = METRIC_RE.search(p.stdout + "\n" + p.stderr)
    if not m:
        print(f"[FAIL] tilt={tilt} ({dt:.0f}s)\n{(p.stdout+p.stderr)[-1200:]}", flush=True)
        return dict(nav=NAV, tilt=tilt, cagr=None, sharpe=None, maxdd=None, calmar=None, secs=round(dt))
    cagr, sh, dd, cal = (float(x) for x in m.groups())
    print(f"[OK] tilt={tilt:<8}: CAGR {cagr:6.2f}%  Sh {sh:.2f}  DD {dd:6.1f}%  Cal {cal:.2f}  ({dt:.0f}s)", flush=True)
    return dict(nav=NAV, tilt=tilt, cagr=cagr, sharpe=sh, maxdd=dd, calmar=cal, secs=round(dt))


rows = []
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futs = {ex.submit(run_cell, t): t for t in TILTS}
    for f in as_completed(futs):
        rows.append(f.result()); pd.DataFrame(rows).to_csv(OUT, index=False)
df = pd.DataFrame(rows).set_index("tilt").reindex(TILTS).reset_index()
df.to_csv(OUT, index=False)
print("\n==== TILT SWEEP NAV=" + NAV + "B ===="); print(df.to_string(index=False)); print("-> " + OUT)
