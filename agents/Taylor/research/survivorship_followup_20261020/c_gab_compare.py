"""C: đối chiếu khối lượng GAB — VNDirect (Winston) vs SSI iBoard (ngày) vs Simplize (tháng). Job Taylor_20261020_113646."""
import json, sys, pandas as pd
R = sys.argv[1]
s = json.load(open(f"{R}/ssi_GAB.json"))["data"]
ssi = pd.DataFrame({k: s[k] for k in ["t", "o", "h", "l", "c", "v"]})
ssi["date"] = (pd.to_datetime(ssi.t, unit="s") + pd.Timedelta(hours=7)).dt.normalize()
K = "/home/trido/thanhdt/WorkingClaude/mike/kb/projects/delisted-tickers-survivorship-20261020.d/prices/GAB.csv"
v = pd.read_csv(K); v["date"] = pd.to_datetime(v.date)
m = ssi.merge(v, on="date", how="inner")
m["rv"] = m.v / m.nmVolume.where(m.nmVolume > 0); m["rc"] = m.c.astype(float) / (m.close * 1000)
print("SSI rows", len(ssi), "merged", len(m), ssi.date.min().date(), ssi.date.max().date())
print(m[["date", "c", "close", "adClose", "v", "nmVolume", "ptVolume", "nmValue", "rv", "rc"]].iloc[::25].to_string())
print("vol ratio SSI/VND:", m.rv.describe().round(3).to_dict())
print("exact vol match share:", float((m.v == m.nmVolume)[m.nmVolume > 0].mean()))
sz = pd.DataFrame(json.load(open(f"{R}/simplize_GAB.json"))["data"], columns="ts o h l c v".split())
sz["mon"] = (pd.to_datetime(sz.ts, unit="s") + pd.Timedelta(hours=7)).dt.to_period("M")
v["mon"] = v.date.dt.to_period("M"); ssi["mon"] = ssi.date.dt.to_period("M")
mm = sz.set_index("mon")[["c", "v"]].rename(columns={"c": "sz_c", "v": "sz_v"}).join(v.groupby("mon").nmVolume.sum().rename("vnd_v")) \
    .join(v.groupby("mon").ptVolume.sum().rename("vnd_pt")).join(ssi.groupby("mon").v.sum().rename("ssi_v"))
mm["sz/vnd"] = mm.sz_v / mm.vnd_v; mm["ssi/vnd"] = mm.ssi_v / mm.vnd_v; mm["sz/ssi"] = mm.sz_v / mm.ssi_v
print(mm.to_string())
mm["sz-(nm+pt)"] = mm.sz_v - mm.vnd_v - mm.vnd_pt; mm["sz/(nm+pt)"] = mm.sz_v / (mm.vnd_v + mm.vnd_pt)
print(mm[["sz_v", "vnd_v", "vnd_pt", "sz-(nm+pt)", "sz/(nm+pt)"]].dropna().round(3).to_string())
tot = mm.dropna(); print("TOTAL sz/nm", tot.sz_v.sum() / tot.vnd_v.sum(), "sz/(nm+pt)", tot.sz_v.sum() / (tot.vnd_v + tot.vnd_pt).sum())
print("pt nonzero days VND:", int((v.ptVolume > 0).sum()), "first", v.date[v.ptVolume > 0].min())
