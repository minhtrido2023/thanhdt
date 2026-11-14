"""Phân kỳ RSI cơ học — engine theo PREREG.md (md5 cd943e11). PAPER-ONLY.
Chạy: /home/trido/thanhdt/wc_venv/bin/python engine.py
Ghi: events.parquet (mọi sự kiện phân kỳ, trước lọc), control.parquet (mọi dòng U2 đủ điều kiện + fwd),
     u1_daily.parquet (VNINDEX mọi ngày + fwd), FREQ.md + freq.json (tần suất nền — TRƯỚC phân tích hiệu quả).
Tái dùng nguyên văn từ ta_model_5pct_20261106/engine.py: nạp cache, RSI Wilder (ewm adjust=False), MDV60 thực."""
import glob, json, os
import numpy as np, pandas as pd
from numpy.lib.stride_tricks import sliding_window_view as swv

ROOT = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.dirname(os.path.abspath(__file__))
START, OOS, FTSE = pd.Timestamp("2014-01-01"), pd.Timestamp("2020-01-01"), pd.Timestamp("2026-09-21")
HS, RSIS, K, GAP_MIN, GAP_MAX, COOL, BREAK = [10, 20, 40], [14, 9], 5, 10, 60, 20, 0.16
TYPES = ["RBEAR", "RBULL", "HBULL", "HBEAR"]
SIGN = {"RBEAR": -1, "RBULL": 1, "HBULL": 1, "HBEAR": -1}
L20 = 20e9

# ------------------------------------------------------------ load (như ta-model)
cols = ["time", "ticker", "Close", "Price", "Volume", "Inflation_7"]
raw = pd.concat([pd.read_parquet(f, columns=cols) for f in sorted(glob.glob(f"{ROOT}/data/bq_cache/ticker/20*.parquet"))])
raw["time"] = pd.to_datetime(raw["time"])
raw = raw.sort_values(["ticker", "time"]).drop_duplicates(["ticker", "time"]).reset_index(drop=True)
u = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "in_universe"]) for f in sorted(glob.glob(f"{ROOT}/data/bq_cache/universe_pit/*.parquet"))])
u["time"] = pd.to_datetime(u["time"]); u = u.drop_duplicates(["time", "ticker"])
vni_c = raw[raw.ticker == "VNINDEX"][["time", "Close"]]
pre = pd.read_csv(f"{OUT}/vnindex_pre2013.csv", parse_dates=["time"])
vni = pd.concat([pre[pre.time < vni_c.time.min()], vni_c]).sort_values("time").reset_index(drop=True)
seam = vni.index[vni.time == vni_c.time.min()][0]
print("VNINDEX seam ret", round(vni.Close[seam] / vni.Close[seam - 1] - 1, 4), "rows", len(vni), flush=True)
df = raw[raw.ticker != "VNINDEX"].merge(u, on=["time", "ticker"], how="left")
df["in_universe"] = df["in_universe"].fillna(False).astype(bool)
df = df.sort_values(["ticker", "time"]).reset_index(drop=True)
print("rows", len(df), "tickers", df.ticker.nunique(), "last", df.time.max().date(), flush=True)


def rsi_wilder(c, n):
    s = pd.Series(c); d = s.diff()
    au = d.clip(lower=0).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    ad = (-d).clip(lower=0).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    return (100 - 100 / (1 + au / ad.replace(0, np.nan))).to_numpy()


def pivots(c, kind):
    L = len(c); out = np.zeros(L, bool)
    if L < 2 * K + 1: return out
    w = swv(c, 2 * K + 1); ok = ~np.isnan(w).any(1)
    am = np.where(ok, (w.argmax(1) if kind == "hi" else w.argmin(1)), -1)
    out[K:L - K] = am == K
    return out


def fwd_arrays(c):
    L = len(c); F = {}
    for H in HS:
        f = np.full(L, np.nan)
        if L > H + 1: f[:L - 1 - H] = c[1 + H:] / c[1:L - H] - 1
        F[H] = f
    return F


def detect(c, rsi):
    """trả list (type, p1, p2, t) — chưa áp hồi chiêu/eligibility."""
    ev = []
    for kind, tps in [("hi", ("RBEAR", "HBEAR")), ("lo", ("RBULL", "HBULL"))]:
        P = np.flatnonzero(pivots(c, kind))
        for j in range(len(P)):
            p2 = P[j]; t = p2 + K
            if t >= len(c): continue
            p1 = None
            for q in range(j - 1, -1, -1):
                g = p2 - P[q]
                if g < GAP_MIN: continue
                if g <= GAP_MAX: p1 = P[q]
                break
            if p1 is None: continue
            c1, c2, r1, r2 = c[p1], c[p2], rsi[p1], rsi[p2]
            if np.isnan(r1) or np.isnan(r2): continue
            if kind == "hi":
                if c2 > c1 * 1.01 and r2 <= r1 - 3 and r1 >= 60: ev.append(("RBEAR", p1, p2, t))
                if c2 < c1 and r2 > r1 + 3: ev.append(("HBEAR", p1, p2, t))
            else:
                if c2 < c1 * 0.99 and r2 >= r1 + 3 and r1 <= 40: ev.append(("RBULL", p1, p2, t))
                if c2 > c1 and r2 < r1 - 3: ev.append(("HBULL", p1, p2, t))
    return ev


def cooldown(ev_list, ok):
    """ev_list sorted by t; giữ sự kiện nếu ok[t] và cách sự kiện đã giữ cùng loại ≥ COOL phiên."""
    keep, last = [], {}
    for e in sorted(ev_list, key=lambda x: x[3]):
        if not ok[e[3]]: continue
        if e[3] - last.get(e[0], -10**9) >= COOL:
            keep.append(e); last[e[0]] = e[3]
    return keep


def maxabs(ar, a, b):
    a = max(a, 1); b = min(b, len(ar) - 1)
    return np.nanmax(ar[a:b + 1]) if b >= a else np.nan


events, ctrl_parts = [], []
selfcheck_store = {}
# ---------------- U1 VNINDEX
cV = vni.Close.astype(float).to_numpy(); tV = vni.time.to_numpy()
arV = np.r_[np.nan, np.abs(cV[1:] / cV[:-1] - 1)]
FV = fwd_arrays(cV)
for n in RSIS:
    rs = rsi_wilder(cV, n)
    okV = tV >= np.datetime64(START)
    for (tp, p1, p2, t) in cooldown(detect(cV, rs), okV):
        rec = dict(U="U1", ticker="VNINDEX", rsi=n, type=tp, p1=p1, p2=p2, t=t, time=tV[t], c1=cV[p1], c2=cV[p2],
                   r1=rs[p1], r2=rs[p2], top250=bool(cV[p2] >= np.nanmax(cV[max(0, p2 - 249):p2 + 1])))
        for H in HS:
            rec[f"fwd{H}"] = FV[H][t]; rec[f"brk{H}"] = maxabs(arV, p1 - 20, t + 1 + H) > BREAK
            rec[f"end{H}"] = tV[t + 1 + H] if t + 1 + H < len(tV) else np.datetime64("NaT")
        events.append(rec)
u1 = pd.DataFrame({"time": tV, "close": cV, **{f"fwd{H}": FV[H] for H in HS},
                   **{f"end{H}": np.r_[tV[1 + H:], np.full(1 + H, np.datetime64("NaT"), dtype="datetime64[ns]")] for H in HS}})
u1["rsi14"] = rsi_wilder(cV, 14)

# ---------------- U2 stocks
n_elig_ctrl_leg = 0
for tk, g in df.groupby("ticker", sort=False):
    c = g.Close.astype(float).to_numpy(); tt = g.time.to_numpy(); L = len(c)
    tv_real = (g.Price.astype(float) * g.Volume.astype(float) / g.Inflation_7.astype(float))
    mdv60 = tv_real.rolling(60, min_periods=60).median().to_numpy()
    elig = g.in_universe.to_numpy() & (mdv60 >= L20) & (tt >= np.datetime64(START))
    n_elig_ctrl_leg += int((elig & (tt <= np.datetime64("2026-11-05"))).sum())
    if not elig.any(): continue
    ar = np.r_[np.nan, np.abs(c[1:] / c[:-1] - 1)]
    F = fwd_arrays(c)
    idx = np.flatnonzero(elig)
    cp = {"ticker": tk, "time": tt[idx], "pos": idx}
    for H in HS:
        cp[f"fwd{H}"] = F[H][idx]
        cp[f"brk{H}"] = np.array([maxabs(ar, i, i + 1 + H) > BREAK for i in idx])
        cp[f"end{H}"] = np.array([tt[i + 1 + H] if i + 1 + H < L else np.datetime64("NaT") for i in idx], dtype="datetime64[ns]")
    ctrl_parts.append(pd.DataFrame(cp))
    for n in RSIS:
        rs = rsi_wilder(c, n)
        for (tp, p1, p2, t) in cooldown(detect(c, rs), elig):
            rec = dict(U="U2", ticker=tk, rsi=n, type=tp, p1=p1, p2=p2, t=t, time=tt[t], c1=c[p1], c2=c[p2],
                       r1=rs[p1], r2=rs[p2], top250=bool(c[p2] >= np.nanmax(c[max(0, p2 - 249):p2 + 1])), mdv60=mdv60[t])
            for H in HS:
                rec[f"fwd{H}"] = F[H][t]; rec[f"brk{H}"] = maxabs(ar, p1 - 20, t + 1 + H) > BREAK
                rec[f"end{H}"] = tt[t + 1 + H] if t + 1 + H < L else np.datetime64("NaT")
            events.append(rec)

E = pd.DataFrame(events); E["time"] = pd.to_datetime(E["time"])
for H in HS: E[f"end{H}"] = pd.to_datetime(E[f"end{H}"])
E["sign"] = E.type.map(SIGN)
CT = pd.concat(ctrl_parts, ignore_index=True)
E.to_parquet(f"{OUT}/events.parquet"); CT.to_parquet(f"{OUT}/control.parquet"); u1.to_parquet(f"{OUT}/u1_daily.parquet")

# ---------------- FREQ (trước bước hiệu quả)
rows = []
for U in ["U1", "U2"]:
    for n in RSIS:
        for tp in TYPES:
            for H in HS:
                s = E[(E.U == U) & (E.rsi == n) & (E.type == tp)]
                v = s[s[f"fwd{H}"].notna()]; vb = v[~v[f"brk{H}"]]
                isd, ood = vb[vb.time < OOS], vb[vb.time >= OOS]
                nd_oos = ood.time.nunique()
                rows.append(dict(trial=f"{U}_{tp}_H{H}_RSI{n}", U=U, type=tp, H=H, rsi=n, n_raw=len(s), n_fwd=len(v),
                                 n_break_excl=int(v[f"brk{H}"].sum()), n_events=len(vb), n_dates=vb.time.nunique(),
                                 n_months=vb.time.dt.to_period("M").nunique(), n_dates_IS=isd.time.nunique(), n_dates_OOS=nd_oos,
                                 n_months_OOS=ood.time.dt.to_period("M").nunique(),
                                 n_FTSE=int((s.time >= FTSE).sum()),
                                 per_year=round(vb.time.nunique() / ((vb.time.max() - pd.Timestamp(START)).days / 365.25), 2) if len(vb) else 0,
                                 MDE_hit_OOS_pp=round(100 * 1.2435 / np.sqrt(nd_oos), 1) if nd_oos else None))
FR = pd.DataFrame(rows)
meta = {"prereg_md5": "cd943e11b9fbc923221d02812989d007", "rows_stock": len(df), "last": str(df.time.max().date()),
        "control_leg_n_elig_le_20261105": n_elig_ctrl_leg, "control_leg_pinned": 300437,
        "u2_control_rows": len(CT), "events_raw": len(E)}
json.dump({"meta": meta, "freq": rows}, open(f"{OUT}/freq.json", "w"), indent=1, default=str)
with open(f"{OUT}/FREQ.md", "w") as fh:
    fh.write("# Tần suất nền — đo TRƯỚC phân tích hiệu quả (PREREG §5)\n\n")
    fh.write(f"meta: `{json.dumps(meta)}`\n\n")
    T = FR.drop(columns=["U", "type", "H", "rsi"])
    fh.write("| " + " | ".join(T.columns) + " |\n|" + "---|" * len(T.columns) + "\n")
    for r in T.itertuples(index=False): fh.write("| " + " | ".join(str(x) for x in r) + " |\n")
print(json.dumps(meta, indent=1))
print(FR[["trial", "n_events", "n_dates", "n_dates_IS", "n_dates_OOS", "n_break_excl", "per_year", "MDE_hit_OOS_pp"]].to_string())
