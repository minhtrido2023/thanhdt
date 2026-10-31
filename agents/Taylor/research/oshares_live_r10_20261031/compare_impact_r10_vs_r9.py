"""So từng ô out_impact_r10_* với out_impact_r9_* (cột st/rb/mos/fv/osh, 5 chân), + cổng DCF_RICH
lag_dd_pack trên chân PD/PDM1: luật R9 (chỉ số live) vs luật R10 (live HOẶC số quý)."""
import glob, os, pandas as pd
H = os.path.dirname(os.path.abspath(__file__)); R9 = os.path.join(H, "..", "oshares_live_r9_20261031")
legs = ["FIN", "NOPD", "PD", "FINM1", "PDM1"]; cols = [f"{c}_{l}" for l in legs for c in ("st", "rb", "mos", "fv", "osh")]
tot = nd = 0
for f in sorted(glob.glob(os.path.join(H, "out_impact_r10_*.csv"))):
    a = f[-14:-4]; n = pd.read_csv(f).set_index("ticker"); o = pd.read_csv(os.path.join(R9, f"out_impact_r9_{a}.csv")).set_index("ticker")
    assert set(n.index) == set(o.index); o = o.loc[n.index]
    diffs = []
    for c in cols:
        for t in n.index:
            x, y = n.at[t, c], o.at[t, c]; tot += 1
            if not ((pd.isna(x) and pd.isna(y)) or x == y):
                nd += 1; diffs.append(f"{t}.{c}: {y} -> {x}")
    print(f"== {a}: {len(diffs)} ô khác"); [print("   ", d) for d in diffs]
    for l in ("PD", "PDM1"):
        fl = "FIN" if l == "PD" else "FINM1"
        ok = n[n[f"st_{l}"].isin(["CHEAP", "RICH"])]
        r9 = set(ok.index[(ok[f"st_{l}"] == "RICH") & ~(ok[f"mos_{l}"] >= -1.0)])
        # luật R10: thêm RICH sâu theo MoS số quý (= chân fin cùng giá) khi chân là live
        r10 = r9 | set(ok.index[ok[f"mos_{fl}"] < -1.0])
        r9_old = set(o.loc[ok.index][(o.loc[ok.index][f"st_{l}"] == "RICH") & ~(o.loc[ok.index][f"mos_{l}"] >= -1.0)].index)
        print(f"   DCF_RICH {l}: R9-luật-trên-R9-số {len(r9_old)} | R10 {len(r10)} | thêm so với R9 {sorted(r10 - r9_old)} | mất {sorted(r9_old - r10)}")
print(f"TỔNG: {nd} ô khác / {tot}")
