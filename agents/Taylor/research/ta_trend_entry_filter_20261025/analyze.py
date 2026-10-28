"""Cờ xu hướng A2/F3/F2 làm bộ lọc lệnh vào LAG/BAL — theo PREREG.md (không tune).
Chạy: $DNA_PYEXE analyze.py   → positions.csv, results.csv, results_sens.csv, selfcheck.txt"""
import glob, os
import numpy as np, pandas as pd

ROOT = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.environ.get("LEDGER", f"{ROOT}/data/pinned_ledgers/2026-10-08__R3-park0-pin0pct-SAN__537e349b.csv.gz")
TAG = os.environ.get("OUT_TAG", "")
PX = f"{ROOT}/data/bq_cache_asof20260729_postrestate/ticker"
IS_END, B, SEED, NMIN = 2019, 5000, 20261025, 100
FLAGS, BOOKS = ["A2", "F3", "F2"], ["LAG", "BAL"]

# ---------------------------------------------------------------- ledger → positions
L = pd.read_csv(LEDGER, low_memory=False)
tx = L[(L.record_type == "TX") & L.book.isin(BOOKS)].copy()
tx["ymd"] = pd.to_datetime(tx.ymd)
for k in ["buy_amount", "sell_amount", "fee"]:
    tx[k] = tx[k].astype(float)
tx["is_buy"] = tx.action == "buy"
# vá: engine đôi khi ghi holding_id lệnh bán là "<TK>_<YYYYMMDD>_?" (thiếu seq) → nối về holding mua duy nhất cùng tiền tố
_q = tx.holding_id.str.endswith("_?")
_buy_ids = tx.loc[tx.is_buy, "holding_id"].unique()
for i in tx.index[_q]:
    pre = tx.at[i, "holding_id"][:-1]
    cand = [h for h in _buy_ids if h.startswith(pre)]
    assert len(cand) == 1, (tx.at[i, "holding_id"], cand)
    tx.at[i, "holding_id"] = cand[0]
N_QFIX = int(_q.sum())
tx["cost"] = np.where(tx.is_buy, tx.buy_amount + tx.fee, 0.0)
tx["proc"] = np.where(~tx.is_buy, tx.sell_amount - tx.fee, 0.0)
g = tx.groupby("holding_id")
pos = pd.DataFrame({
    "book": g.book.first(), "ticker": g.ticker.first(), "play_type": g.play_type.first(),
    "entry_date": g.apply(lambda x: x.loc[x.is_buy, "ymd"].min(), include_groups=False),
    "exit_date": g.apply(lambda x: x.loc[~x.is_buy, "ymd"].max(), include_groups=False),
    "n_buy": g.is_buy.sum(), "n_sell": g.is_buy.apply(lambda s: int((~s).sum())),
    "cost": g.cost.sum(), "proc": g.proc.sum(),
    "abandoned": g.reason.apply(lambda s: (s == "ABANDONED_REFUND").any()),
    "mtm": g.reason.apply(lambda s: (s == "MTM_UNREALIZED").any()),
}).reset_index()
pos["pnl"] = pos.proc - pos.cost
pos["ret"] = pos.proc / pos.cost - 1

D = L[L.record_type == "DAILY"].copy()
D["ymd"] = pd.to_datetime(D.ymd)
D = D.set_index("ymd")
cal = D.index.sort_values()
navref = {"LAG": D.nav_lag_ref.astype(float), "BAL": D.nav_bal_ref.astype(float)}
pos["book_nav"] = [navref[b].get(d, np.nan) for b, d in zip(pos.book, pos.entry_date)]
pos["contrib_bp"] = pos.pnl / pos.book_nav * 1e4
ix = cal.searchsorted(pos.entry_date)
pos["signal_date"] = [cal[i - 1] if i > 0 else pd.NaT for i in ix]

# ---------------------------------------------------------------- flags (công thức engine.py job trước)
tks = set(pos.ticker)
raw = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "Open", "High", "Low", "Close", "Volume"]) for f in sorted(glob.glob(f"{PX}/*.parquet"))])
raw = raw[raw.ticker.isin(tks)]
raw["time"] = pd.to_datetime(raw.time)
raw = raw.sort_values(["ticker", "time"]).drop_duplicates(["ticker", "time"])


def flags(gp):
    gp = gp.reset_index(drop=True)
    h, l, c, v = (gp[k].astype(float) for k in ["High", "Low", "Close", "Volume"])
    ten = (h.rolling(9).max() + l.rolling(9).min()) / 2
    kij = (h.rolling(26).max() + l.rolling(26).min()) / 2
    ssa = ((ten + kij) / 2).shift(26)
    ssb = ((h.rolling(52).max() + l.rolling(52).min()) / 2).shift(26)
    top = np.maximum(ssa, ssb)
    MA50 = c.rolling(50).mean()
    vr = v / v.shift(1).rolling(20).mean()
    f3ev = ((c > c.shift(1).rolling(252).max()) & (vr > 1.5)).fillna(False).astype(int)
    return pd.DataFrame({
        "time": gp.time, "ticker": gp.ticker,
        "A2": ((ten > kij) & (c > top)).fillna(False),
        "F3": f3ev.rolling(20, min_periods=1).max() > 0,
        "F2": ((c > MA50) & (MA50 > MA50.shift(10))).fillna(False),
        "hist_ok": top.notna() & c.shift(1).rolling(252).max().notna() & MA50.shift(10).notna(),
    })


F = pd.concat([flags(gp) for _, gp in raw.groupby("ticker", sort=False)], ignore_index=True)
F = F.sort_values("time")
pos["signal_date"] = pos.signal_date.astype("datetime64[ns]"); F["time"] = F.time.astype("datetime64[ns]")
pos = pos.sort_values("signal_date")
pos = pd.merge_asof(pos, F.rename(columns={"time": "flag_date"}), left_on="signal_date", right_on="flag_date", by="ticker", direction="backward")
for k in FLAGS + ["hist_ok"]:
    pos[k] = pos[k].fillna(False).astype(bool)
pos["year"] = pos.entry_date.dt.year
pos["ym"] = pos.entry_date.dt.to_period("M").astype(str)
pos = pos.sort_values(["book", "entry_date", "holding_id"]).reset_index(drop=True)
pos.to_csv(f"{OUT}/positions{TAG}.csv", index=False, float_format="%.10g")


# ---------------------------------------------------------------- stats
def boot(df, col, flag):
    rng = np.random.default_rng(SEED)
    months = df.ym.unique()
    grp = {m: df[df.ym == m] for m in months}
    s = {m: (x.loc[x[flag], col].sum(), x[flag].sum(), x.loc[~x[flag], col].sum(), (~x[flag]).sum()) for m, x in grp.items()}
    arr = np.array([s[m] for m in months])
    ds = np.empty(B)
    for b in range(B):
        a = arr[rng.integers(0, len(months), len(months))].sum(0)
        ds[b] = a[0] / a[1] - a[2] / a[3] if a[1] > 0 and a[3] > 0 else np.nan
    ds = ds[~np.isnan(ds)]
    p = 2 * min((ds <= 0).mean(), (ds >= 0).mean())
    return max(p, 1 / B), np.percentile(ds, [2.5, 97.5])


def bh(p):
    p = np.asarray(p, float); n = len(p); o = np.argsort(p)
    q = np.empty(n); q[o] = np.minimum.accumulate((p[o] * n / np.arange(1, n + 1))[::-1])[::-1]
    return np.minimum(q, 1)


def table(sub):
    rows = []
    for bk in BOOKS:
        x = sub[sub.book == bk]
        for fl in FLAGS:
            on, off = x[x[fl]], x[~x[fl]]
            r = {"book": bk, "flag": fl, "N_on": len(on), "N_off": len(off),
                 "Nm_on": on.ym.nunique(), "Nm_off": off.ym.nunique(),
                 "ret_on": on.ret.mean(), "ret_off": off.ret.mean(), "d": on.ret.mean() - off.ret.mean(),
                 "med_on": on.ret.median(), "med_off": off.ret.median(),
                 "pct_excluded": len(off) / len(x)}
            for nm, m in [("IS", x.year <= IS_END), ("OOS", x.year > IS_END)]:
                xi = x[m]
                r[f"d_{nm}"] = xi.loc[xi[fl], "ret"].mean() - xi.loc[~xi[fl], "ret"].mean()
                r[f"N_on_{nm}"], r[f"N_off_{nm}"] = int(xi[fl].sum()), int((~xi[fl]).sum())
            r["p"], ci = boot(x, "ret", fl)
            r["ci_lo"], r["ci_hi"] = ci
            r["c_on_bp"], r["c_off_bp"] = on.contrib_bp.mean(), off.contrib_bp.mean()
            r["p_contrib"] = boot(x, "contrib_bp", fl)[0]
            r["sum_contrib_off_bp"] = off.contrib_bp.sum()
            rows.append(r)
    R = pd.DataFrame(rows)
    R["q"] = bh(R.p)
    R["thieu_mau"] = (R.N_on < NMIN) | (R.N_off < NMIN)
    return R


main = pos[~pos.abandoned & ~pos.mtm & (pos.n_sell > 0)]
sens = pos[~pos.mtm & (pos.n_sell > 0)]
R, S = table(main), table(sens)
R["sens_d"] = S.d.values
R["pass"] = ((R.d_IS > 0) & (R.d_OOS > 0) & (R.q < 0.10) & (R.d >= 0.01) & (R.pct_excluded <= 0.40)
             & (np.sign(R.sens_d) == np.sign(R.d)) & ~R.thieu_mau)
R.to_csv(f"{OUT}/results{TAG}.csv", index=False, float_format="%.6g")
S.to_csv(f"{OUT}/results_sens{TAG}.csv", index=False, float_format="%.6g")

# ---------------------------------------------------------------- selfcheck
lines = []
for bk in BOOKS:
    t = tx[tx.book == bk]
    lines.append(f"{bk}: sum pnl positions={pos[pos.book == bk].pnl.sum():.4f} ; sum(proc)-sum(cost) from TX={t.proc.sum() - t.cost.sum():.4f}")
_m = pos[(pos.n_buy > 1) & (pos.holding_id == "AAM_20160722_504")]
a = (_m if len(_m) else pos[pos.n_buy > 1]).iloc[0]
lines.append(f"{a.holding_id}: n_buy={a.n_buy} n_sell={a.n_sell} entry={a.entry_date.date()} signal={a.signal_date.date()} ret={a.ret:.6f} abandoned={a.abandoned}")
lines.append(f"holding_id '_?' vá={N_QFIX}")
lines.append(f"positions total={len(pos)} main={len(main)} abandoned={int(pos.abandoned.sum())} mtm/open={int((pos.mtm | (pos.n_sell == 0)).sum())}")
lines.append(f"hist_ok False (cờ có thể TẮT do thiếu lịch sử) main={int((~main.hist_ok).sum())} ; no flag row={int(main.flag_date.isna().sum())}")
lines.append(f"signal lag (signal_date - flag_date) >0 days count main={int((main.signal_date > main.flag_date).sum())}")
open(f"{OUT}/selfcheck{TAG}.txt", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
pd.set_option("display.width", 250)
print(R[["book", "flag", "N_on", "N_off", "Nm_on", "Nm_off", "ret_on", "ret_off", "d", "d_IS", "d_OOS", "p", "q", "pct_excluded", "sens_d", "c_on_bp", "c_off_bp", "pass"]].to_string())
