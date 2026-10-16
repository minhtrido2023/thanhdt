"""Snapshot effective_deposit_rate()/macro_killswitch_a_status()/effective_deposit_events_df() for a given repo root."""
import sys, json, os
root = sys.argv[1]; sys.path.insert(0, root); os.chdir(root)
import pandas as pd
import deposit_rate_vn as d
out = {}
for asof in ["2026-06-01", "2026-09-29", "2026-09-30", "2026-10-05", "2026-10-14", "2026-11-14", "2026-11-25", "2027-03-01", None]:
    k = str(asof)
    e = d.effective_deposit_rate(pd.Timestamp(asof) if asof else None)
    m = d.macro_killswitch_a_status(pd.Timestamp(asof) if asof else None)
    out[k] = {"eff": e, "ks": m}
ev = d.effective_deposit_events_df()
out["events_df"] = ev.astype(str).to_dict(orient="records")
print(json.dumps(out, default=str, indent=1, sort_keys=True))
