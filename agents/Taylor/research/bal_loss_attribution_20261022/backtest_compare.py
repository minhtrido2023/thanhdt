"""Q3 + Q4 trên ledger pin R3 pin0% (md5 4707bcbe...). READ-ONLY, không chạy engine. Theo PREREG.md."""
import gzip, hashlib, json, os, math
import numpy as np, pandas as pd

W = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__))
LED = f"{W}/data/pinned_ledgers/2026-09-28__R3-anchor-pin0pct-sexies__4707bcbe.csv.gz"
raw = gzip.open(LED).read()
md5 = hashlib.md5(raw).hexdigest()
assert md5 == "4707bcbeb7e801d49a4a851ffd91d5e7", md5
import io
d = pd.read_csv(io.BytesIO(raw), low_memory=False)
out = {"ledger_md5": md5}

# ---- daily series + consistency check
D = d[d.record_type == "DAILY"].copy()
D["ymd"] = pd.to_datetime(D.ymd)
D = D.set_index("ymd").sort_index()
gap = (D.combined_nav - D.nav_bal_ref - D.nav_lag_ref).abs()
out["consistency_max_abs_gap_vnd"] = float(gap.max())
out["consistency_max_rel_gap"] = float((gap / D.combined_nav).max())

# ---- Q3(i) per-trade BAL stock holdings
T = d[(d.record_type == "TX") & (d.book == "BAL")].copy()
T = T[~T.play_type.isin(["ETF_PARK"]) & ~T.play_type.str.startswith("CAPITB")]
g = T.groupby("holding_id")
H = pd.DataFrame(dict(play=g.play_type.first(), buy=g.buy_amount.sum(), sell=g.sell_amount.sum(), fee=g.fee.sum(),
                      reason=g.apply(lambda x: ",".join(sorted(set(x[x.action == "sell"].reason.dropna())))),
                      entry=g.ymd.min(), exit=g.ymd.max()))
H = H[(H.sell > 0) & (~H.reason.str.contains("ABANDONED_REFUND")) & (~H.reason.str.contains("MTM_UNREALIZED"))]
H["ret"] = H.sell / (H.buy + H.fee) - 1
H.to_csv(f"{HERE}/bt_bal_holdings.csv")
live = json.load(open(f"{HERE}/live_attrib.json"))
vpi_ret = live["SpaceX"]["bal"]["ret_net_pct"] / 100
q = lambda s, p: float(np.quantile(s, p))
out["q3_trades"] = dict(n=len(H), median=q(H.ret, .5), p05=q(H.ret, .05), p10=q(H.ret, .10), p25=q(H.ret, .25),
                        mean=float(H.ret.mean()), win_rate=float((H.ret > 0).mean()),
                        vpi_ret=vpi_ret, vpi_percentile=float((H.ret <= vpi_ret).mean()),
                        n_stop=int(H.reason.str.contains("STOP").sum()),
                        stop_median=float(H[H.reason.str.contains("STOP")].ret.median()),
                        stop_min=float(H[H.reason.str.contains("STOP")].ret.min()),
                        frac_trades_le_minus20=float((H.ret <= -0.20).mean()),
                        n_by_play=H.play.value_counts().to_dict())

# ---- Q3(ii) combined DD
nav = D.combined_nav
out["q3_combined_maxdd"] = float((nav / nav.cummax() - 1).min())
bal = D.nav_bal_ref
out["q3_balbook_maxdd"] = float((bal / bal.cummax() - 1).min())

# ---- Q3(iii) BAL P&L / combined NAV over non-overlapping 21-session windows.
# NB: nav_bal_ref thay đổi cả do REBAL chuyển vốn BAL<->LAG; loại cửa sổ có REBAL.
reb = set(pd.to_datetime(d[d.record_type == "REBAL"].ymd))
idx = D.index
rows = []
for i in range(0, len(idx) - 21, 21):
    a, b = idx[i], idx[i + 21]
    if any(a < r <= b for r in reb):
        continue
    rows.append((a, (bal[b] - bal[a]) / nav[a]))
Wn = pd.DataFrame(rows, columns=["start", "bal_pnl_over_nav"])
Wn.to_csv(f"{HERE}/bt_bal_21d_windows.csv", index=False)
live_sx = live["SpaceX"]["bal"]["pnl_pct_nav"] / 100
live_zp = live["ZaloPay"]["bal"]["pnl_pct_nav"] / 100
s = Wn.bal_pnl_over_nav
out["q3_21d"] = dict(n=len(s), median=q(s, .5), p05=q(s, .05), p01=q(s, .01), min=float(s.min()),
                     spacex_live=live_sx, spacex_pct=float((s <= live_sx).mean()),
                     zalopay_live=live_zp, zalopay_pct=float((s <= live_zp).mean()),
                     n_rebal_windows_dropped=int(len(range(0, len(idx) - 21, 21)) - len(Wn)))

# ---- Q4 episodes
vni = D.vni_close
rv = vni.pct_change()
rb = bal.pct_change()
# REBAL-day returns of nav_bal_ref are polluted by capital transfers -> mask
rb[rb.index.isin(reb)] = np.nan
fwd = lambda r, t, k: float(np.prod(1 + r.iloc[t:t + k].values) - 1) if t + k <= len(r) else np.nan


def episodes(dd_thr, up_thr):
    eps, last = [], -10**9
    for t in range(61, len(vni)):
        if rv.iloc[t] >= up_thr and vni.iloc[t - 1] <= (1 - dd_thr) * vni.iloc[t - 61:t - 1].max() and t - last >= 20:
            eps.append(t); last = t
    return eps


def measure(ts):
    r = []
    for t in ts:
        b1, v1 = rb.iloc[t], rv.iloc[t]
        b5, v5 = fwd(rb, t, 5), fwd(rv, t, 5)
        r.append(dict(date=str(vni.index[t].date()), state=int(D.state.iloc[t]), vni_dd_prev=float(vni.iloc[t - 1] / vni.iloc[t - 61:t - 1].max() - 1),
                      bal_1d=b1, vni_1d=v1, ex_1d=b1 - v1, bal_5d=b5, vni_5d=v5, ex_5d=b5 - v5,
                      bal_stock_frac=float(D.bal_stocks_ref.iloc[t - 1] / D.nav_bal_ref.iloc[t - 1])))
    return pd.DataFrame(r)


allt = list(range(61, len(vni) - 5))
U = measure(allt).dropna(subset=["ex_1d", "ex_5d"])
rng = np.random.default_rng(20261022)
res4 = {}
for name, (ddt, upt) in {"main_-8_+2.0": (0.08, 0.02), "sens_-10_+2.5": (0.10, 0.025)}.items():
    E = measure(episodes(ddt, upt))
    E.to_csv(f"{HERE}/q4_episodes_{name}.csv", index=False)
    Ev = E.dropna(subset=["ex_1d", "ex_5d"])
    N = len(Ev)
    m5u = float(U.ex_5d.median()); m1u = float(U.ex_1d.median())
    k5 = int((Ev.ex_5d < m5u).sum()); k1 = int((Ev.ex_1d < m1u).sum())
    binom = lambda k, n: sum(math.comb(n, j) for j in range(k, n + 1)) / 2 ** n
    sims5 = np.array([np.median(rng.choice(U.ex_5d.values, N, replace=False)) for _ in range(10000)])
    sims1 = np.array([np.median(rng.choice(U.ex_1d.values, N, replace=False)) for _ in range(10000)])
    res4[name] = dict(N=N, N_dropped_rebal=int(len(E) - N), uncond_median_ex5=m5u, uncond_median_ex1=m1u,
                      ep_median_ex5=float(Ev.ex_5d.median()), ep_median_ex1=float(Ev.ex_1d.median()),
                      ep_median_bal5=float(Ev.bal_5d.median()), ep_median_vni5=float(Ev.vni_5d.median()),
                      k_below_ex5=k5, k_below_ex1=k1, binom_onesided_ex5=binom(k5, N), binom_onesided_ex1=binom(k1, N),
                      resample_pct_ex5=float((sims5 <= Ev.ex_5d.median()).mean()),
                      resample_pct_ex1=float((sims1 <= Ev.ex_1d.median()).mean()),
                      ep_median_stock_frac=float(Ev.bal_stock_frac.median()), uncond_median_stock_frac=float(U.bal_stock_frac.median()),
                      criterion_lag=bool(k5 >= math.ceil(2 * N / 3) and (sims5 <= Ev.ex_5d.median()).mean() <= 0.10))
out["q4"] = res4
json.dump(out, open(f"{HERE}/backtest_compare.json", "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
for name in res4:
    print("==", name); print(pd.read_csv(f"{HERE}/q4_episodes_{name}.csv").round(4).to_string())
