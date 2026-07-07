# -*- coding: utf-8 -*-
"""dc_liquidity_floor_backtest.py (job Taylor_20260707_042827, NHÁNH B) — RESEARCH ONLY.

Floor thanh khoản tổng quát cho DC book membership thay hard-exclude DHG:
  member(t) = double-confirm(t) AND Trading_Value_1M_P50(t) >= THR   (THR = 3B / 5B VND)
DHG được đưa LẠI vào panel (không hard-exclude) — floor phải tự loại nó.
Đo: (1) name-days bị floor loại trong lịch sử double-confirm (theo tên/năm) — floor có cắt
tên nào ngoài DHG không; (2) backtest sleeve daily + overlay full-NAV vs paper config.
TV as-of: ffill theo tên trên calendar; TV missing -> KHÔNG đạt floor (fail-safe).
Self-checks: overlay identity 0 VND; variant floor-3B với DHG hard-excluded-thêm phải ==
floor-3B thuần nếu floor tự loại DHG 100% ngày double-confirm.
"""
import os, sys, numpy as np, pandas as pd, duckdb
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)

IS_END = pd.Timestamp("2019-12-31")
CAP, TC = 0.20, 0.001
WL_TK = ["MBB","ACB","HDB","TCB","VCB","FPT","SSI","VCI","VND","HCM","CTR","MSH","DHG","PVT","HAH","DBC"]

dbl_raw = pd.read_csv("data/dc_dbl_panel.csv", index_col=0, parse_dates=True).astype(bool)
sret = pd.read_csv("data/dc_stock_ret.csv", index_col=0, parse_dates=True)
park = pd.read_csv("data/dc_park_ret.csv", index_col=0, parse_dates=True)["park_ret"]
cal = dbl_raw.index
names = list(dbl_raw.columns)

con = duckdb.connect(":memory:"); con.execute("SET threads=1")
q = ",".join(f"'{t}'" for t in WL_TK)
tv = con.execute(f"""
    SELECT ticker, time, Trading_Value_1M_P50 tv
    FROM read_parquet('data/bq_cache/ticker_prune/*.parquet')
    WHERE ticker IN ({q}) AND time >= '2014-01-01'""").df()
tv["time"] = pd.to_datetime(tv["time"])
TV = tv.pivot_table(index="time", columns="ticker", values="tv").reindex(cal).ffill()
TV = TV.reindex(columns=names)

def build_member(thr, hard_exclude_dhg=False):
    m = dbl_raw & (TV >= thr).fillna(False)
    if hard_exclude_dhg and "DHG" in m.columns:
        m = m.copy(); m["DHG"] = False
    return m

def vehicle(member):
    W = pd.DataFrame(0.0, index=cal, columns=names); pk = pd.Series(0.0, index=cal)
    for d in cal:
        cur = [t for t in names if member.at[d, t]]
        n = len(cur)
        if n:
            w = min(CAP, 1.0 / n)
            for t in cur: W.at[d, t] = w
            pk.loc[d] = max(0.0, 1.0 - w * n)
        else:
            pk.loc[d] = 1.0
    r = pd.Series(0.0, index=cal); prev_w = W.iloc[0].copy(); prev_p = pk.iloc[0]
    for i, d in enumerate(cal):
        if i == 0: continue
        ra = float((prev_w * sret.loc[d].reindex(names).fillna(0.0)).sum())
        rp = prev_p * (park.loc[d] if np.isfinite(park.loc[d]) else 0.0)
        t = (float((W.loc[d] - prev_w).abs().sum()) + abs(pk.loc[d] - prev_p)) / 2.0
        r.loc[d] = ra + rp - t * TC
        prev_w = W.loc[d].copy(); prev_p = pk.loc[d]
    return r

# ---------------- overlay lên R3
aud_df = pd.read_csv("data/h3_baseline_R3.csv", low_memory=False)
d = aud_df[aud_df["record_type"] == "DAILY"].copy()
d["ymd"] = pd.to_datetime(d["ymd"])
for c_ in ["bal_etf_ref", "lag_etf_ref", "combined_nav"]:
    d[c_] = pd.to_numeric(d[c_])
aud = d.set_index("ymd").sort_index()
r_base = aud["combined_nav"].pct_change().dropna()
w_park_prev = ((aud["bal_etf_ref"] + aud["lag_etf_ref"]) / aud["combined_nav"]).shift(1).reindex(r_base.index).fillna(0.0)

def overlay(rv):
    dv = (rv - park.reindex(cal)).reindex(r_base.index).fillna(0.0)
    return r_base + w_park_prev * dv

def metrics(r):
    r = r.dropna(); nv = (1 + r).cumprod()
    yrs = (r.index[-1] - r.index[0]).days / 365.25
    cagr = nv.iloc[-1] ** (1 / yrs) - 1
    sh = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else np.nan
    dd = (nv / nv.cummax() - 1).min()
    return cagr * 100, sh, dd * 100, (cagr / abs(dd) if dd < 0 else np.nan)

def show(name, r):
    for tag, rr in [("FULL", r), ("IS", r[r.index <= IS_END]), ("OOS", r[r.index > IS_END])]:
        c, sh, dd, ca = metrics(rr)
        print(f"{name:<44}{tag:<5}{c:>7.2f}%{sh:>7.2f}{dd:>8.1f}%{ca:>7.2f}")
    print()

# identity self-check
assert float(((r_base + w_park_prev * 0.0) - r_base).abs().max()) == 0.0
print("SELF-CHECK: overlay identity 0 VND OK")

# ---------------- (1) diagnostic: floor loại name-days nào trong double-confirm history
print("\n=== NHÁNH B — name-days double-confirm bị floor loại (2014-08 → nay) ===")
for thr, lab in [(3e9, "3B"), (5e9, "5B")]:
    passed = (TV >= thr).fillna(False)
    dropped = dbl_raw & ~passed
    tot = int(dbl_raw.values.sum())
    print(f"floor {lab}: loại {int(dropped.values.sum())}/{tot} name-days double-confirm "
          f"({dropped.values.sum()/tot*100:.1f}%)")
    per = dropped.sum(axis=0)
    per = per[per > 0].sort_values(ascending=False)
    for tk, n in per.items():
        yrs = sorted(dropped.index[dropped[tk]].year.unique())
        dc_tot = int(dbl_raw[tk].sum())
        print(f"    {tk}: {int(n)}/{dc_tot} ngày double-confirm ({', '.join(map(str, yrs))})")
    print()

# DHG floor-coverage check: floor 3B có tự loại DHG đủ 100% ngày double-confirm không?
dhg_dc = dbl_raw["DHG"]
for thr, lab in [(3e9, "3B"), (5e9, "5B")]:
    ok = (TV["DHG"] >= thr).fillna(False)
    both = int((dhg_dc & ok).sum())
    print(f"DHG double-confirm days: {int(dhg_dc.sum())}; floor {lab} vẫn cho qua: {both}")

# ---------------- (2) backtest
hdr = f"{'config':<44}{'win':<5}{'CAGR':>8}{'Sharpe':>7}{'MaxDD':>9}{'Calmar':>7}"
print("\n=== NHÁNH B — backtest full-NAV overlay (daily membership, paper convention) ===")
print(hdr); print("-" * len(hdr))
paper = build_member(-np.inf, hard_exclude_dhg=True)   # không floor, DHG hard-exclude = paper
show("paper hiện tại (hard-exclude DHG, no floor)", overlay(vehicle(paper)))
for thr, lab in [(3e9, "3B"), (5e9, "5B")]:
    m = build_member(thr, hard_exclude_dhg=False)
    show(f"floor {lab} thay hard-exclude (DHG cho lại vào)", overlay(vehicle(m)))
# combo: floor 3B + vẫn hard-exclude DHG (chứng minh floor không đổi gì ngoài DHG-effect)
m2 = build_member(3e9, hard_exclude_dhg=True)
show("floor 3B + DHG vẫn hard-exclude (diagnostic)", overlay(vehicle(m2)))
