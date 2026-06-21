"""Data-driven calibration of the 8L composite value axis (user questions 2026-06-16):
  Q1: optimal REL vs ABS weight (pb_z vs sector-neutral 1/PE) — find the robust plateau, not the single max.
  Q2/Q3: 3Y vs 5Y CFO normalization — coverage (new listings lack 5Y) AND effectiveness; if 3Y ~ 5Y, prefer 3Y.
  Q4: HAG-type trap exclusion check.
Forward target = profit_2M (T+40). IC = per-month cross-sectional Spearman.
"""
import numpy as np, pandas as pd

def spear(a, b):
    ra, rb = pd.Series(np.asarray(a, float)).rank(), pd.Series(np.asarray(b, float)).rank()
    if ra.nunique() < 2 or rb.nunique() < 2: return np.nan
    return float(np.corrcoef(ra, rb)[0, 1])

WD = "/home/trido/thanhdt/WorkingClaude"
df = pd.read_csv(f"{WD}/data/calib_panel.csv", parse_dates=["time"])
df["ym"] = df.time.values.astype("datetime64[M]"); df["year"] = df.time.dt.year
df["pb_z"] = (df.PB - df.PB_MA5Y) / df.PB_SD5Y.replace(0, np.nan)
df["earn_yield"] = np.where(df.PE > 0, 1.0/df.PE, np.nan)
df["sec"] = (df.ICB_Code // 1000).fillna(-1)

# merge_asof CF_OA_3Y (from financial, PIT)
fin = pd.read_csv(f"{WD}/data/cfoa3y_fin.csv", parse_dates=["fin_time"]).sort_values("fin_time")
df = df.sort_values("time")
df = pd.merge_asof(df, fin, by="ticker", left_on="time", right_on="fin_time", direction="backward")

LIQ = 5e9
d = df[df.turnover >= LIQ].copy()

# ---- axes ----
d["rel"] = (0.5 - d.pb_z/2.0).clip(0, 1)
# sector-neutral abs (rank earn_yield within ICB sector per month; fallback global if sector<5)
def _sn(g):
    out = g.copy()
    for sec, idx in g.groupby("sec").groups.items():
        sub = g.loc[idx, "earn_yield"]
        out.loc[idx, "abs_sn"] = sub.rank(pct=True) if sub.notna().sum() >= 5 else np.nan
    out["abs_sn"] = out["abs_sn"].fillna(g["earn_yield"].rank(pct=True))
    return out["abs_sn"]
d["abs_sn"] = d.groupby("ym", group_keys=False).apply(_sn)
d["abs_pool"] = d.groupby("ym")["earn_yield"].transform(lambda s: s.rank(pct=True))

def ic_by(fac, fwd="profit_2M"):
    rows = []
    for ym, g in d.groupby("ym"):
        s = g[[fac, fwd]].dropna()
        if len(s) >= 8 and s[fac].nunique() > 2:
            ic = spear(s[fac], s[fwd])
            if np.isfinite(ic): rows.append((ym.year, ic))
    r = pd.DataFrame(rows, columns=["yr","ic"])
    m = r.ic.mean(); ir = m/r.ic.std()*np.sqrt(len(r)) if r.ic.std() > 0 else np.nan
    yrs = r.groupby("yr").ic.mean(); yp = f"{(yrs>0).sum()}/{len(yrs)}"
    return m, ir, yp

# ---- Q1: REL vs ABS weight sweep (sector-neutral abs) ----
print("=== Q1: composite IC by REL/ABS weight (w = ABS weight; sector-neutral abs, profit_2M) ===")
print(f"{'w_abs':>6} {'IC':>8} {'IR(t)':>6} {'yrs+':>6}   (w=0 pure pb_z, w=1 pure 1/PE)")
for w in [0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]:
    d["comp"] = (1-w)*d["rel"] + w*d["abs_sn"]
    m, ir, yp = ic_by("comp")
    bar = "#"*int(m*200) if m>0 else ""
    print(f"{w:>6.1f} {m:>+8.4f} {ir:>6.1f} {yp:>6}  {bar}")
print("  [pooled-abs sanity] ", end="")
d["comp_p"] = 0.5*d["rel"] + 0.5*d["abs_pool"]; m,ir,yp = ic_by("comp_p")
print(f"w=0.5 pooled-abs IC={m:+.4f} (vs sector-neutral below) -> sector-neutral keeps signal if ~equal")

# ---- Q2/Q3: 3Y vs 5Y CFO normalization ----
print("\n=== Q2/Q3: cycle-normalized CFO yield — 3Y vs 5Y (coverage + IC) ===")
ttm = d[["CF_OA_P0","CF_OA_P1","CF_OA_P2","CF_OA_P3"]].sum(axis=1, min_count=1)
d["ncfy_5y"] = np.where((d.PCF>0)&(ttm>0)&(d.CF_OA_5Y/5>0), (1/d.PCF)*np.clip((d.CF_OA_5Y/5)/ttm,0.3,3), np.nan)
d["ncfy_3y"] = np.where((d.PCF>0)&(ttm>0)&(d.CF_OA_3Y/3>0), (1/d.PCF)*np.clip((d.CF_OA_3Y/3)/ttm,0.3,3), np.nan)
n = len(d.dropna(subset=["profit_2M"]))
for nm in ["ncfy_5y","ncfy_3y"]:
    pop = d[nm].notna().sum()/len(d)*100
    m, ir, yp = ic_by(nm)
    print(f"  {nm}: coverage {pop:>4.0f}%   IC {m:>+.4f}  IR {ir:>5.1f}  yrs+ {yp}")
# coverage gain specifically among NEWER names (proxy: names with null CF_OA_5Y)
new = d[d.CF_OA_5Y.isna() | (d.CF_OA_5Y<=0)]
print(f"  among rows lacking valid 5Y CFO ({len(new)} rows): 3Y available for {new.ncfy_3y.notna().sum()} "
      f"({new.ncfy_3y.notna().sum()/max(len(new),1)*100:.0f}%) -> coverage rescued by 3Y")

# ---- Q4: HAG-type trap check ----
print("\n=== Q4: HAG + capital-destroyer trap check (latest snapshot per ticker) ===")
latest = df.sort_values("time").groupby("ticker").tail(1)
for tk in ["HAG","HNG","HVN","JVC","FLC"]:
    r = latest[latest.ticker==tk]
    if len(r):
        r=r.iloc[0]
        ey = (1/r.PE) if (pd.notna(r.PE) and r.PE>0) else np.nan
        print(f"  {tk}: pb_z {r.pb_z:+.2f}  earn_yield {ey if pd.isna(ey) else round(ey,3)}  "
              f"ROE_Min5Y {r.ROE_Min5Y:+.0%}  -> {'TRAP(ROE_Min5Y<0 guard fires)' if (pd.notna(r.ROE_Min5Y) and r.ROE_Min5Y<0) else 'not auto-trapped'}")
# how many capital-destroyers (ROE_Min5Y<0) would the guard catch among optically-cheap names
inv = latest[(latest.turnover>=LIQ)]
cheap_look = inv[(inv.pb_z<=-0.3) | (np.where(inv.PE>0,1/inv.PE,0) > inv[inv.PE>0].pipe(lambda x:(1/x.PE)).median())]
destroyers = cheap_look[cheap_look.ROE_Min5Y<0]
print(f"  optically-cheap capital-destroyers caught by TRAP guard now: {len(destroyers)} "
      f"({sorted(destroyers.ticker.tolist())[:12]})")
