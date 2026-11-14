"""Phân tích hiệu quả 48 trial theo PREREG.md (md5 cd943e11) §6-§8. Đọc events/control/u1_daily từ engine.py.
Ghi: results.csv (48 dòng), byyear.csv, dt5g_lead.json, summary.json."""
import json, os, itertools, math
import numpy as np, pandas as pd
from scipy.stats import norm, skew, kurtosis

OUT = os.path.dirname(os.path.abspath(__file__))
OOS, FTSE, START = pd.Timestamp("2020-01-01"), pd.Timestamp("2026-09-21"), pd.Timestamp("2014-01-01")
HS, RSIS, TYPES = [10, 20, 40], [14, 9], ["RBEAR", "RBULL", "HBULL", "HBEAR"]
FEE, SLIP = 0.00097, 0.002
NB, NP = 5000, 1000
rng = np.random.default_rng(20261114)
E = pd.read_parquet(f"{OUT}/events.parquet"); CT = pd.read_parquet(f"{OUT}/control.parquet"); U1 = pd.read_parquet(f"{OUT}/u1_daily.parquet")
for d in (E, CT, U1): d["time"] = pd.to_datetime(d["time"])
CAL = U1[U1.time >= START].time.reset_index(drop=True)
calm = CAL.dt.to_period("M")
cal_by_m = {m: g.tolist() for m, g in CAL.groupby(calm)}
ordinal = {t: i for m, g in CAL.groupby(calm) for i, t in enumerate(g)}


def monthly_clim(times, ends, fwd, months):
    """c_m, r̄_m từ các dòng có end < ngày đầu tháng m (PIT)."""
    d = pd.DataFrame({"end": ends, "up": (fwd > 0).astype(float), "f": fwd}).dropna(subset=["end", "f"]).sort_values("end")
    ce, cu, cf = d.end.to_numpy(), np.cumsum(d.up.to_numpy()), np.cumsum(d.f.to_numpy())
    res = {}
    for m in months:
        k = np.searchsorted(ce, m.start_time.to_datetime64(), side="left")
        res[m] = (cu[k - 1] / k, cf[k - 1] / k) if k > 0 else (0.5, 0.0)
    return res


months_all = pd.period_range("2014-01", CAL.max().to_period("M"), freq="M")
CLIM = {}
for H in HS:
    u = U1[U1.time >= "2007-01-01"]
    CLIM[("U1", H)] = monthly_clim(u.time, u[f"end{H}"], u[f"fwd{H}"].to_numpy(), months_all)
    c = CT[CT[f"fwd{H}"].notna() & ~CT[f"brk{H}"]]
    CLIM[("U2", H)] = monthly_clim(c.time, c[f"end{H}"], c[f"fwd{H}"].to_numpy(), months_all)
CTRL = {H: CT[CT[f"fwd{H}"].notna() & ~CT[f"brk{H}"]].groupby("time")[f"fwd{H}"].mean() for H in HS}
LOOK = {}
for H in HS:
    c = CT[CT[f"fwd{H}"].notna() & ~CT[f"brk{H}"]].copy()
    c["x"] = c[f"fwd{H}"] - c.time.map(CTRL[H])
    LOOK[H] = c.set_index(["ticker", "time"])["x"]
U1x = {H: U1.set_index("time")[f"fwd{H}"] for H in HS}


def month_boot(D, nb=NB):
    """bootstrap khối THÁNG: resample tháng có hoàn lại trên tổng theo tháng. Trả (BSS[], meanx[])."""
    A = D.groupby("month").agg(bf=("bs_f", "sum"), bc=("bs_c", "sum"), xs=("x", "sum"), n=("x", "size")).to_numpy()
    idx = rng.integers(0, len(A), (nb, len(A))); S = A[idx].sum(1)
    return 1 - S[:, 0] / S[:, 1], S[:, 2] / S[:, 3]


def trial(U, tp, H, n):
    s = E[(E.U == U) & (E.type == tp) & (E.rsi == n) & E[f"fwd{H}"].notna() & ~E[f"brk{H}"]].copy().sort_values("time")
    name = f"{U}_{tp}_H{H}_RSI{n}"
    r = dict(trial=name, U=U, type=tp, H=H, rsi=n, n_events=len(s))
    if len(s) == 0:
        r.update(p_bss=1.0); return r, None
    sg = s["sign"].to_numpy(); f = s[f"fwd{H}"].to_numpy()
    s["month"] = s.time.dt.to_period("M"); s["up"] = (f > 0).astype(float); s["hit"] = (sg * f > 0).astype(float)
    cl = CLIM[(U, H)]
    s["c"] = s.month.map(lambda m: cl[m][0]); s["rbar"] = s.month.map(lambda m: cl[m][1])
    # dự báo PIT: sự kiện cùng trial có end < t
    ends = s[f"end{H}"].to_numpy(); ups = s.up.to_numpy(); order = np.argsort(ends); se, su = ends[order], np.cumsum(ups[order])
    k = np.searchsorted(se, s.time.to_numpy(), side="left")
    kup = np.where(k > 0, su[np.maximum(k - 1, 0)], 0)
    s["p"] = (kup + 2 * s.c) / (k + 2)
    s["bs_f"] = (s.p - s.up) ** 2; s["bs_c"] = (s.c - s.up) ** 2
    s["x"] = sg * (f - (s.time.map(CTRL[H]).to_numpy() if U == "U2" else s.rbar.to_numpy()))
    D = s.groupby("time").agg(month=("month", "first"), bs_f=("bs_f", "mean"), bs_c=("bs_c", "mean"), x=("x", "mean"),
                              hit=("hit", "mean"), fwd_s=("x", "size")).reset_index()
    D["year"] = D.time.dt.year
    Do = D[D.time >= OOS]; Di = D[D.time < OOS]
    so = s[s.time >= OOS]
    r.update(n_dates=len(D), n_dates_IS=len(Di), n_dates_OOS=len(Do), n_months_OOS=Do.month.nunique(),
             hit_IS=round(s[s.time < OOS].hit.mean(), 4) if len(Di) else np.nan, hit_OOS=round(so.hit.mean(), 4) if len(Do) else np.nan,
             exR_IS=Di.x.mean() if len(Di) else np.nan)
    bss = lambda d: 1 - d.bs_f.sum() / d.bs_c.sum() if d.bs_c.sum() > 0 else 0.0
    if len(Do) >= 2:
        r["BSS_OOS"] = bss(Do); bb, be = month_boot(Do)
        r["BSS_lo"], r["BSS_hi"] = np.percentile(bb, [2.5, 97.5]); r["p_bss"] = float((bb <= 0).mean())
        r["exR_OOS"] = Do.x.mean()
        r["exR_lo"], r["exR_hi"] = np.percentile(be, [2.5, 97.5]); r["p_exR"] = float((be <= 0).mean())
        for sl in (0.001, 0.002, 0.003):
            r[f"exR_net_s{int(sl*1000)}"] = r["exR_OOS"] - 2 * (FEE + sl)
        x = Do.x.to_numpy(); r["SR"] = x.mean() / x.std(ddof=1) if x.std(ddof=1) > 0 else np.nan
        r["skew"], r["kurt"] = skew(x), kurtosis(x, fisher=False)
        # placebo khối tháng trong vùng OOS
        moos = [m for m in months_all if m >= pd.Period("2020-01", "M") and m in cal_by_m]
        lastf = U1.time[U1[f"fwd{H}"].notna()].max(); moos = [m for m in moos if cal_by_m[m][0] <= lastf]
        ev = so[["ticker", "time", "sign", "month"]].copy(); ev["ord"] = ev.time.map(ordinal)
        ev = ev[ev.ord.notna()]
        actual = Do.x.mean(); cnt = 0; pv = []
        for _ in range(NP):
            perm = dict(zip(moos, rng.permutation(moos)))
            tgt = [cal_by_m[perm.get(m, m)][min(int(o), len(cal_by_m[perm.get(m, m)]) - 1)] for m, o in zip(ev.month, ev.ord)]
            tgt = pd.to_datetime(tgt)
            if U == "U2":
                v = LOOK[H].reindex(pd.MultiIndex.from_arrays([ev.ticker.to_numpy(), tgt])).to_numpy()
            else:
                mm = tgt.to_period("M"); v = U1x[H].reindex(tgt).to_numpy() - np.array([cl.get(m, (0.5, 0.0))[1] for m in mm])
            v = ev.sign.to_numpy() * v; ok = ~np.isnan(v)
            if ok.sum() == 0: continue
            val = pd.Series(v[ok]).groupby(np.asarray(tgt)[ok]).mean().mean(); pv.append(val); cnt += val >= actual
        r["p_placebo"] = cnt / max(len(pv), 1); r["placebo_n"] = len(pv)
    else:
        r.update(p_bss=1.0)
    # LOYO trên toàn kỳ
    full = D.x.mean(); flips = 0
    for y in range(2014, 2027):
        d = D[D.year != y]
        if len(d) and np.sign(d.x.mean()) != np.sign(full): flips += 1
    r["exR_full"] = full; r["loyo_flips"] = flips
    by = D.groupby("year").x.mean(); r["years_neg_sign"] = int((np.sign(by) != np.sign(full)).sum()); r["years_with_data"] = len(by)
    ft = s[s.time >= FTSE]; r["n_FTSE"] = len(ft); r["hit_FTSE"] = ft.hit.mean() if len(ft) else np.nan
    return r, D.assign(trial=name)


rows, dates = [], []
for U in ["U1", "U2"]:
    for n in RSIS:
        for tp in TYPES:
            for H in HS:
                r, D = trial(U, tp, H, n); rows.append(r)
                if D is not None: dates.append(D)
                print(r["trial"], r.get("n_dates_OOS"), r.get("BSS_OOS"), r.get("exR_OOS"), flush=True)
R = pd.DataFrame(rows)
# BH-FDR q=0.10 trên p_bss
p = R.p_bss.fillna(1.0).to_numpy(); m = len(p); o = np.argsort(p); thr = 0.10 * np.arange(1, m + 1) / m
passed = np.zeros(m, bool); kk = np.where(p[o] <= thr)[0]
if len(kk): passed[o[:kk.max() + 1]] = True
R["BH_pass"] = passed
# DSR trên 48
srs = R.SR.dropna(); V = srs.var(ddof=1); g = 0.5772156649; N = 48
SR0 = math.sqrt(V) * ((1 - g) * norm.ppf(1 - 1 / N) + g * norm.ppf(1 - 1 / (N * math.e)))
def dsr(r):
    if pd.isna(r.SR) or r.n_dates_OOS < 3: return np.nan
    den = 1 - r["skew"] * r.SR + (r["kurt"] - 1) / 4 * r.SR ** 2
    return norm.cdf((r.SR - SR0) * math.sqrt(r.n_dates_OOS - 1) / math.sqrt(max(den, 1e-12)))
R["DSR"] = R.apply(dsr, axis=1)
# PBO CSCV S=16 trên exR theo khối thời gian toàn kỳ
AD = pd.concat(dates); edges = pd.date_range(START, CAL.max() + pd.Timedelta(days=1), periods=17)
AD["blk"] = np.searchsorted(edges.to_numpy(), AD.time.to_numpy(), side="right") - 1
M = AD.groupby(["blk", "trial"]).x.mean().unstack().reindex(index=range(16), columns=R.trial).fillna(0.0).to_numpy()
lam = []
for IS in itertools.combinations(range(16), 8):
    oos = [b for b in range(16) if b not in IS]
    best = M[list(IS)].mean(0).argmax(); perf = M[oos].mean(0)
    rk = (perf < perf[best]).sum() + 0.5 * ((perf == perf[best]).sum() - 1)
    w = (rk + 1) / (M.shape[1] + 1); lam.append(math.log(w / (1 - w)))
PBO = float((np.array(lam) <= 0).mean())
# tiêu chí §7
R["crit_a"] = (R.BSS_OOS > 0) & (R.BSS_lo > 0)
R["crit_b"] = R.BH_pass
R["crit_c"] = R.loyo_flips <= 2
R["crit_d"] = np.where(R.U == "U2", R.exR_net_s2 > 0, True)
R["PASS"] = R.crit_a & R.crit_b & R.crit_c & R.crit_d
R.to_csv(f"{OUT}/results.csv", index=False)
AD.groupby(["trial", "year"]).agg(n=("x", "size"), exR=("x", "mean"), hit=("hit", "mean")).reset_index().to_csv(f"{OUT}/byyear.csv", index=False)

# §8 DT5G lead (mô tả)
ep = pd.read_csv(f"{OUT}/B_episodes.csv", parse_dates=["start", "end"])
down_from_hi = ep[(ep.outcome == "commit") & ep.committed_from.isin([4, 5]) & (ep.cand < ep.committed_from)]
down_any = ep[(ep.outcome == "commit") & ep.committed_from.isin([3, 4, 5]) & (ep.cand < ep.committed_from)]
cpos = {t: i for i, t in enumerate(U1.time)}
rb = E[(E.U == "U1") & (E.type == "RBEAR") & (E.rsi == 14)].sort_values("time")
lead = []
for _, e in rb.iterrows():
    nxt = down_from_hi[down_from_hi.end > e.time].end.min()
    nd = down_any[(down_any.end > e.time)].end.min()
    s_next = cpos.get(nd, None)
    lead.append(dict(time=str(e.time.date()), top250=bool(e.top250), fwd20=e.fwd20,
                     sessions_to_next_commit_leaving_BULL=(cpos[nxt] - cpos[e.time]) if pd.notna(nxt) else None,
                     false_alarm_40=bool(pd.isna(nd) or (cpos[nd] - cpos[e.time]) > 40)))
cover = []
for _, c in down_from_hi.iterrows():
    prior = rb[(rb.time < c.end) & (rb.time >= c.end - pd.Timedelta(days=90))]
    cover.append(dict(commit=str(c.end.date()), rbear_within_90d_before=len(prior)))
DT = dict(n_RBEAR14_U1=len(rb), n_top250=int(rb.top250.sum()), false_alarm_40=int(sum(x["false_alarm_40"] for x in lead)),
          events=lead, commits_leaving_BULL=cover, commits_covered=int(sum(c["rbear_within_90d_before"] > 0 for c in cover)))
json.dump(DT, open(f"{OUT}/dt5g_lead.json", "w"), indent=1, default=str)
summ = dict(prereg_md5="cd943e11b9fbc923221d02812989d007", n_trials=len(R), n_pass=int(R.PASS.sum()),
            n_crit_a=int(R.crit_a.sum()), n_BH=int(R.BH_pass.sum()), PBO=PBO, SR0_DSR=SR0, max_DSR=float(R.DSR.max()),
            U2_exR_OOS_gt0_CI_excl0=int(((R.U == "U2") & (R.exR_lo > 0)).sum() + ((R.U == "U2") & (R.exR_hi < 0)).sum()),
            U2_exR_pos_CI_excl0=int(((R.U == "U2") & (R.exR_lo > 0)).sum()),
            U2_net_pos=int(((R.U == "U2") & (R.exR_net_s2 > 0)).sum()),
            DT=dict(n=DT["n_RBEAR14_U1"], false_alarm_40=DT["false_alarm_40"], commits_covered=DT["commits_covered"]))
json.dump(summ, open(f"{OUT}/summary.json", "w"), indent=1, default=float)
print(json.dumps(summ, indent=1, default=float))
pd.set_option("display.width", 250)
print(R[["trial", "n_dates_OOS", "hit_OOS", "BSS_OOS", "BSS_lo", "BSS_hi", "p_bss", "exR_OOS", "exR_lo", "exR_hi", "exR_net_s2", "p_placebo", "loyo_flips", "DSR", "PASS"]].round(4).to_string())
