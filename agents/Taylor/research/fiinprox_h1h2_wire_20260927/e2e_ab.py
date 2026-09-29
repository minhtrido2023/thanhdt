"""End-to-end A/B of rating_8l_history.py main(): HEAD (old, ROE-only + fail-open override) vs the
H1 wire (AQ-aware + fail-closed). Same cached BQ input for both; neither touches the canonical CSV
nor tav2_bq.fa_ratings_8l."""
import os, sys, importlib.util
import pandas as pd
SBX = "/tmp/h1h2_sbx"
WC  = "/home/trido/thanhdt/WorkingClaude"
WT  = "/home/trido/thanhdt/wt-fiinprox-h1h2-wire/WorkingClaude"
HIST = pd.read_csv(f"{SBX}/hist_fin.csv"); ICB = pd.read_csv(f"{SBX}/icb.csv")

def fake_bq(sql):
    return ICB.copy() if "ICB_Code" in sql and "GROUP BY" in sql else HIST.copy()

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m
    spec.loader.exec_module(m); return m

# ---- OLD (HEAD) ----
os.environ["WORKDIR_8L"] = f"{SBX}/oldwd"
old = load(f"{SBX}/r8l_hist_OLD.py", "r8l_old")
old.bq = fake_bq; old.refresh_bq_table = lambda p: print("  [old] bq refresh no-op")
old.main()
os.rename(f"{SBX}/oldwd/data/rating_8l_history.csv", f"{SBX}/ab_old.csv")

# ---- NEW (wire) ----
print("\n" + "="*78)
os.environ["WORKDIR_8L"] = WC          # needs real mike/data for the FiinPro file
os.environ["R8L_HIST_OUT"] = f"{SBX}/ab_new.csv"
os.environ["R8L_HIST_NO_BQ_REFRESH"] = "1"
new = load(f"{WT}/rating_8l_history.py", "r8l_new")
new.bq = fake_bq
new.main()

# ---- DIFF ----
print("\n" + "="*78)
A = pd.read_csv(f"{SBX}/ab_old.csv"); B = pd.read_csv(f"{SBX}/ab_new.csv")
key = ["ticker","eff_date","q_time"]
A["gate"] = (A.rating <= 3); B["gate"] = (B.rating <= 3)
m = A.merge(B, on=key, how="outer", suffixes=("_old","_new"), indicator=True)
print(f"rows old={len(A)}  new={len(B)}  merge={len(m)}  unmatched={(m._merge!='both').sum()}")
both = m[m._merge=="both"]
gd = both[both.gate_old != both.gate_new]
rd = both[both.rating_old != both.rating_new]
print(f"\nRATING changed : {len(rd)} rows ({', '.join(sorted(rd.route_old.dropna().unique()))})")
print(f"GATE   changed : {len(gd)} rows   <<< the GO invariant")
if len(gd):
    # is each gate change a LATEST row per bank (the intentional (c) fix) or a HISTORY row (a violation)?
    last = B.sort_values("eff_date").groupby(["ticker","route"]).tail(1)
    lastkey = set(zip(last.ticker, last.eff_date))
    gd = gd.copy(); gd["is_latest_row"] = [ (t,e) in lastkey for t,e in zip(gd.ticker, gd.eff_date) ]
    print(gd[["ticker","eff_date","route_old","rating_old","rating_new","is_latest_row"]].to_string(index=False))
    hist_viol = int((~gd.is_latest_row).sum())
    print(f"\n  HISTORY-row gate violations : {hist_viol}   (must be 0)")
    print(f"  LATEST-row gate changes     : {int(gd.is_latest_row.sum())}   (intentional: fail-closed fix (c))")
else:
    hist_viol = 0
# non-BANK routes must be untouched
nb = rd[rd.route_old != "BANK"]
print(f"\nnon-BANK rating changes : {len(nb)}  (must be 0 -- wire is BANK-route only)")
print("\nVERDICT: " + ("PASS" if hist_viol == 0 and len(nb) == 0 else "FAIL"))
