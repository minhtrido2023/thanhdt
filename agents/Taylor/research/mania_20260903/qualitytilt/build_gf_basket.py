import pandas as pd, numpy as np, os
W = os.path.dirname(os.path.abspath(__file__))
gf = pd.read_csv(os.path.join(W, "golden_floor_snap.csv"), parse_dates=["time"])
gf["cf_ttm"] = gf[["CF_OA_P0","CF_OA_P1","CF_OA_P2","CF_OA_P3"]].sum(axis=1, min_count=1)
gf["golden_floor"] = (gf.ROE_Min3Y >= 0) & (gf.cf_ttm > 0)
gf["quarter"] = gf.time.dt.to_period("Q")

qdates = gf.groupby("quarter").time.min().sort_values().reset_index()
selections = {}
for _, row in qdates.iterrows():
    qd = row.time
    day = gf[(gf.time == qd) & gf.golden_floor]
    day = day[(day.PE.notna()) & (day.PE > 0)]
    if len(day) < 20:
        selections[row.quarter] = []
        continue
    thresh = day.PE.quantile(0.10)
    sel = day[day.PE <= thresh].ticker.tolist()
    selections[row.quarter] = sel

all_sel = sorted(set(t for v in selections.values() for t in v))
print(f"Golden-floor+ey basket: {len(all_sel)} unique tickers ever selected across {sum(1 for v in selections.values() if v)}/{len(qdates)} quarters")
with open(os.path.join(W, "gf_selected_tickers.txt"), "w") as f:
    f.write("\n".join(all_sel))

sizes = [len(v) for v in selections.values() if v]
print(f"Median basket size: {np.median(sizes):.0f}, min={min(sizes)}, max={max(sizes)}")
import json
with open(os.path.join(W, "gf_selections.json"), "w") as f:
    json.dump({str(k): v for k, v in selections.items()}, f)
