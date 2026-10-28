"""Q2 + Q3 trên ledger R3 (mặc định pin0% 4707bcbe). Theo PREREG.md. READ-ONLY.
Usage: python q2q3_ledger.py [ledger.csv.gz] [tag]"""
import gzip, hashlib, io, json, os, sys
import numpy as np, pandas as pd
from scipy.stats import fisher_exact

HERE = os.path.dirname(os.path.abspath(__file__))
W = "/home/trido/thanhdt/WorkingClaude"
LED = sys.argv[1] if len(sys.argv) > 1 else f"{W}/data/pinned_ledgers/2026-09-28__R3-anchor-pin0pct-sexies__4707bcbe.csv.gz"
TAG = sys.argv[2] if len(sys.argv) > 2 else "pin0"
raw = gzip.open(LED).read() if LED.endswith(".gz") else open(LED, "rb").read()
d = pd.read_csv(io.BytesIO(raw), low_memory=False)
out = {"ledger": os.path.basename(LED), "ledger_md5": hashlib.md5(raw).hexdigest()}

D = d[d.record_type == "DAILY"].copy(); D["ymd"] = pd.to_datetime(D.ymd); D = D.set_index("ymd").sort_index()
s = D.cap_bal / D.combined_nav
idx = D.index
BASE = {"MEGA", "MOMENTUM", "DEEP_VALUE_RECOVERY", "RE_BACKLOG_BUY"}
T = d[(d.record_type == "TX") & (d.book == "BAL")].copy(); T["ymd"] = pd.to_datetime(T.ymd)
T["base"] = T.play_type.str.replace("_W$", "", regex=True)
TS = T[T.play_type != "ETF_PARK"]                       # all BAL stock TX (incl CAPITB) for sleeve P&L identity
TB = T[T.base.isin(BASE)]                                # "lệnh BAL" per PREREG

# ---- holdings
g = TB.groupby("holding_id")
H = pd.DataFrame(dict(play=g.play_type.first(), ticker=g.ticker.first(), entry=g.ymd.min(), exit=g.ymd.max(),
                      buy=g.buy_amount.sum(), sell=g.sell_amount.sum(), fee=g.fee.sum(),
                      reason=g.apply(lambda x: ",".join(sorted(set(x[x.action == "sell"].reason.dropna()))))))
closed = (H.sell > 0) & ~H.reason.str.contains("MTM_UNREALIZED|ABANDONED_REFUND")
H["closed"] = closed
H["ret"] = H.sell / (H.buy + H.fee) - 1
H["stop"] = H.reason.str.contains("STOP")
# weight % combined NAV at entry
H["w_nav"] = [H.buy[h] / D.nav_bal_ref[H.entry[h]] * s[H.entry[h]] for h in H.index]
H["w_book"] = [H.buy[h] / D.nav_bal_ref[H.entry[h]] for h in H.index]

# ---- n_bal per day (open at close of day d: entry<=d<exit; sells on exit day close the position)
ent = H.entry.values
# every holding occupies the book entry..exit (ABANDONED_REFUND = partial fill held a few days; MTM_UNREALIZED = open at end)
ex = np.where(H.reason.str.contains("MTM_UNREALIZED"), np.datetime64("2100-01-01"), H.exit.values)
nb = pd.Series([int(((ent <= t) & (ex > t)).sum()) for t in idx.values], index=idx)
H["n_at_entry"] = [int(((ent <= e) & (ex > e)).sum()) for e in H.entry.values]   # includes itself
out["q2_nbal_daily"] = {"dist": {str(k): int(v) for k, v in nb.value_counts().sort_index().items()},
                        "frac_days_0": float((nb == 0).mean()), "frac_days_1_2": float(nb.between(1, 2).mean()),
                        "frac_days_ge3": float((nb >= 3).mean()), "median": float(nb.median()),
                        "median_when_ge1": float(nb[nb >= 1].median())}
def wstats(x):
    return dict(n=int(len(x)), median=float(x.median()), p10=float(x.quantile(.1)), p90=float(x.quantile(.9)),
                max=float(x.max())) if len(x) else dict(n=0)
grp = lambda n: "1" if n == 1 else ("2" if n == 2 else "3+")
H["grp_entry"] = H.n_at_entry.map(grp)
out["q2_weight_nav_by_n_at_entry"] = {k: wstats(v.w_nav) for k, v in H.groupby("grp_entry")}
out["q2_weight_nav_all"] = wstats(H.w_nav)
out["q2_weight_nav_excl_abandoned"] = wstats(H[~H.reason.str.contains("ABANDONED")].w_nav)
out["q2_weight_nav_by_n_excl_abandoned"] = {k: wstats(v.w_nav) for k, v in H[~H.reason.str.contains("ABANDONED")].groupby("grp_entry")}
out["q2_weight_book_all"] = wstats(H.w_book)
out["q2_share_bal_s"] = dict(median=float(s.median()), p10=float(s.quantile(.1)), p90=float(s.quantile(.9)),
                             by_state={str(int(k)): float(v) for k, v in s.groupby(D.state).median().items()})
for lab, live in (("SpaceX", 0.051), ("ZaloPay", 0.026)):
    out[f"q2_live_{lab}_pct_in_weight_dist"] = float((H.w_nav <= live).mean())
    out[f"q2_live_{lab}_pct_in_weight_dist_n1"] = float((H[H.n_at_entry == 1].w_nav <= live).mean()) if (H.n_at_entry == 1).any() else None
# live-like: distinct BAL entries per 77-session window (live 01/07-21/10 had 77 rec files, 3 distinct names)
starts = range(0, len(idx) - 77, 77)
dn = [H[(H.entry >= idx[i]) & (H.entry < idx[i + 77])].ticker.nunique() for i in starts]
out["q2_distinct_entries_per_77s"] = dict(n=len(dn), median=float(np.median(dn)), p05=float(np.quantile(dn, .05)),
                                          frac_le3=float(np.mean(np.array(dn) <= 3)), min=int(min(dn)))

# ---- Q3 windows (21 non-overlapping), stock-sleeve P&L via identity
rows = []
for i in range(0, len(idx) - 21, 21):
    a, b = idx[i], idx[i + 21]
    # sleeve P&L uses bal_stocks_ref (all BAL stocks incl CAPITB) => windows with CAPITB open are dropped below
    capit_open = bool(((T.play_type.str.startswith("CAPITB")) & (T.ymd <= b)).any() and
                      T[T.play_type.str.startswith("CAPITB")].groupby("holding_id").ymd.agg(["min", "max"])
                      .pipe(lambda m: ((m["min"] <= b) & (m["max"] > a)).any()))
    rows.append(dict(start=a, end=b, n_start=int(nb[a]), n_max=int(nb.loc[a:b].max()), capit=capit_open,
                     comb_ret=D.combined_nav[b] / D.combined_nav[a] - 1, state=int(D.state[a])))
Wn = pd.DataFrame(rows)
# pnl_book is in book VND; to system: book VND * (cap_bal/nav_bal_ref) / combined_nav
scale = (D.cap_bal / D.nav_bal_ref)
Wn["pnl_nav"] = [((D.bal_stocks_ref[r.end] - D.bal_stocks_ref[r.start]) +
                  TS[(TS.ymd > r.start) & (TS.ymd <= r.end)].eval("sell_amount - buy_amount - fee").sum())
                 * scale[r.start] / D.combined_nav[r.start] for r in Wn.itertuples()]
Wn.to_csv(f"{HERE}/q3_windows_{TAG}.csv", index=False)
main = Wn[~Wn.capit & (Wn.n_start >= 1)].copy()
main["grp"] = np.where(main.n_start <= 2, "1-2", "3+")
res = {}
for k, v in main.groupby("grp"):
    x = v.pnl_nav
    res[k] = dict(n=int(len(x)), median=float(x.median()), p05=float(x.quantile(.05)), min=float(x.min()),
                  n_le_070=int((x <= -0.0070).sum()), n_le_107=int((x <= -0.0107).sum()),
                  spacex_pct=float((x <= -0.0107).mean()), zalopay_pct=float((x <= -0.0055).mean()))
out["q3_windows_by_nstart"] = res
out["q3_n_windows_total"] = int(len(Wn)); out["q3_n_capit_dropped"] = int(Wn.capit.sum())
out["q3_n_nstart0_dropped"] = int((~Wn.capit & (Wn.n_start == 0)).sum())
if {"1-2", "3+"} <= set(res):
    for thr in ("070", "107"):
        a1 = res["1-2"][f"n_le_{thr}"]; n1 = res["1-2"]["n"]; a3 = res["3+"][f"n_le_{thr}"]; n3 = res["3+"]["n"]
        out[f"q3_fisher_le_{thr}"] = dict(table=[[a1, n1 - a1], [a3, n3 - a3]], p_two_sided=float(fisher_exact([[a1, n1 - a1], [a3, n3 - a3]])[1]))
# stop rate by n at entry
Hc = H[H.closed].copy(); Hc["g"] = np.where(Hc.n_at_entry <= 2, "1-2", "3+")
st = {k: dict(n=int(len(v)), n_stop=int(v.stop.sum()), rate=float(v.stop.mean()), median_ret=float(v.ret.median()))
      for k, v in Hc.groupby("g")}
out["q3_stop_by_n_entry"] = st
if {"1-2", "3+"} <= set(st):
    tb = [[st["1-2"]["n_stop"], st["1-2"]["n"] - st["1-2"]["n_stop"]], [st["3+"]["n_stop"], st["3+"]["n"] - st["3+"]["n_stop"]]]
    out["q3_stop_fisher"] = dict(table=tb, p_two_sided=float(fisher_exact(tb)[1]))
H.to_csv(f"{HERE}/q2_holdings_{TAG}.csv")
json.dump(out, open(f"{HERE}/q2q3_{TAG}.json", "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
