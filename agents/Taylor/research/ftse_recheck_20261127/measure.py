"""FTSE upgrade (eff. 2026-09-21) structural-break RE-VALIDATION — measurement only, no parameter change.
Job Taylor_20261013_114456. NO forward/return-level statistics: only breadth, counts, turnover (VND),
foreign participation and return CORRELATION (dependence structure, not return level).

Design: every statistic = f(anchor) comparing POST = first NPOST sessions from anchor vs PRE = 60 sessions
before anchor. Actual anchor = 2026-09-21. "Normal range" = same f at placebo anchors:
  (a) non-overlapping anchors every NPOST sessions 2014-01 .. before event  -> p5/p50/p95 + percentile of actual
  (b) seasonal: first session >= Sep-21 of each prior year                   -> min/median/max
"""
import json, numpy as np, pandas as pd
import db_dtypes  # noqa: F401  (parquet written with BQ dbdate dtype)
EVENT = pd.Timestamp("2026-09-21"); NPRE = 60
FTSE27 = ("VCB VIC VHM BID HPG VPB FPT GEX HDB HCM MCH MSN NVL SHB STB SSB SSI TCX VNM VCI VJC MSB VRE VPL VIX VND VCK").split()
FTSE6 = "VCB VIC VHM BID HPG VPB".split()   # All-World (large+mid)

P = pd.read_parquet("panel_pit.parquet"); P["time"] = pd.to_datetime(P["time"])
P["ret"] = P["Close"] / P["Close_T1"] - 1
days = np.array(sorted(P["time"].unique())); didx = {d: i for i, d in enumerate(days)}
e = int(np.searchsorted(days, np.datetime64(EVENT))); NPOST = len(days) - e
T = P.pivot(index="time", columns="ticker", values="turn")          # NaN = not in universe that day
L = P.pivot(index="time", columns="ticker", values="liq3m")
R = P.pivot(index="time", columns="ticker", values="ret")
A200 = P[P.MA200.notna()].assign(a=lambda d: (d.Close > d.MA200).astype(float))
B = A200.groupby("time").agg(b200=("a", "mean"), univ=("a", "size")).reindex(days)
NU = P.groupby("time").size().reindex(days)                           # in_universe count
MK = pd.read_parquet("mkt_turn.parquet"); MK["time"] = pd.to_datetime(MK["time"]); MK = MK.set_index("time").mkt_turn.reindex(days)
F = pd.read_csv("foreign_vnindex_vndirect.csv", parse_dates=["tradingDate"]).set_index("tradingDate")
F = F[F.buyVal > 0]
FS = ((F.buyVal + F.sellVal) / 2).reindex(days) / MK                  # foreign participation share (incl. put-through; denom = all-exchange turnover)
FN = F.netVal.reindex(days) / 1e9
C30 = pd.read_csv("custom30v_members.csv").ticker.tolist()

def win(i):
    return slice(i - NPRE, i), slice(i, i + NPOST)

def mcorr(X):
    X = X.dropna(axis=1, thresh=int(len(X) * 0.9)).fillna(0.0)
    c = np.corrcoef(X.values.T); iu = np.triu_indices_from(c, 1)
    return float(np.nanmean(c[iu]))

def stats(i):
    pre, post = win(i); o = {}
    def pp(name, s, how="mean", kind="diff"):
        a = getattr(s.iloc[pre], how)(); b = getattr(s.iloc[post], how)()
        o[name] = (float(a), float(b), float(b - a) if kind == "diff" else float(b / a - 1))
    # ---- Tier 1: DT5G breadth guard
    pp("T1_b200_mean", B.b200); pp("T1_univ_ma200_mean", B.univ, kind="ratio")
    g = ((B.univ >= 100) & (B.b200 >= 0.50)).astype(float); pp("T1_guard_true_frac", g)
    top30 = T.iloc[pre].median().dropna().nlargest(30).index
    a, b = mcorr(R.iloc[pre][top30]), mcorr(R.iloc[post][top30]); o["T1_corr_top30"] = (a, b, b - a)
    if days[i - NPRE] >= np.datetime64("2018-09-01") and FS.iloc[pre].notna().sum() > 40:
        pp("T1_foreign_share_median", FS, "median"); pp("T1_foreign_net_bn_median", FN, "median")
    # ---- Tier 2: custom30V liquidity pool
    pp("T2_n_in_universe_mean", NU, kind="ratio")
    tp, tq = T.iloc[pre], T.iloc[post]
    mp, mq = tp.median(), tq.median()
    o["T2_n_adv_ge_10bn"] = (float((mp >= 10e9).sum()), float((mq >= 10e9).sum()), float((mq >= 10e9).sum() - (mp >= 10e9).sum()))
    o["T2_n_adv_ge_1bn"] = (float((mp >= 1e9).sum()), float((mq >= 1e9).sum()), float((mq >= 1e9).sum() - (mp >= 1e9).sum()))
    sp, sq = tp.sum(axis=1), tq.sum(axis=1)
    o["T2_univ_turnover_bn_day"] = (sp.mean() / 1e9, sq.mean() / 1e9, sq.mean() / sp.mean() - 1)
    pool_a = L.iloc[i - 1].dropna().nlargest(60).index
    j = min(i + NPOST - 1, len(days) - 1); pool_b = L.iloc[j].dropna().nlargest(60).index
    o["T2_top60_pool_names_changed"] = (60.0, float(len(set(pool_a) & set(pool_b))), float(60 - len(set(pool_a) & set(pool_b))))
    rr = (mq / mp).replace([np.inf, -np.inf], np.nan)
    o["T2_top60_adv_ratio_median"] = (float(mp[pool_a].median() / 1e9), float(mq[pool_a].median() / 1e9), float(rr[pool_a].median() - 1))
    top10p = (tp.sum().nlargest(10).sum() / tp.sum().sum()); top10q = (tq.sum().nlargest(10).sum() / tq.sum().sum())
    o["T2_top10_turnover_share"] = (float(top10p), float(top10q), float(top10q - top10p))
    f = [t for t in FTSE27 if t in T.columns]
    fp, fq = tp[f].sum().sum() / tp.sum().sum(), tq[f].sum().sum() / tq.sum().sum()
    o["T2_ftse27_turnover_share"] = (float(fp), float(fq), float(fq - fp))
    f6 = [t for t in FTSE6 if t in T.columns]
    fp, fq = tp[f6].sum().sum() / tp.sum().sum(), tq[f6].sum().sum() / tq.sum().sum()
    o["T2_ftse6_turnover_share"] = (float(fp), float(fq), float(fq - fp))
    return o

# ---- Tier 3: CAPIT %ADV cap = 0.10 * ADV20 * 2 ; ADV20 = median turnover of the 20 sessions BEFORE asof (prune source, as production)
C = pd.read_parquet("panel_capit_prune.parquet"); C["time"] = pd.to_datetime(C["time"])
CT = C.pivot(index="time", columns="ticker", values="turn")
cdays = np.array(sorted(C["time"].unique()))
Cq = C[(C.ROE_Min5Y >= 0.12) & (C.ROIC5Y >= 0.10) & (C.FSCORE >= 6)]
qset = Cq.groupby("time").ticker.apply(set)
npass = Cq[Cq.turn >= 2e9].groupby("time").size().reindex(cdays).fillna(0)

def capit(i, detail=False):
    """i = index in cdays of anchor. cap(asof=anchor) uses 20 sessions before anchor; cap(asof=anchor+NPOST) the 20 before that."""
    q = sorted(qset.get(cdays[i - 1], set()))
    a0 = CT.iloc[i - 20:i][q].median(); j = min(i + NPOST, len(cdays)); a1 = CT.iloc[j - 20:j][q].median()
    ok = (a0 > 0) & (a1 > 0); ch = (a1[ok] / a0[ok] - 1)
    o = {"T3_quality_set_n": (float(len(q)), float(len(qset.get(cdays[j - 1], set()))), 0.0),
         "T3_n_pass_2bn_floor_mean": (float(npass.iloc[i - NPRE:i].mean()), float(npass.iloc[i:j].mean()), float(npass.iloc[i:j].mean() - npass.iloc[i - NPRE:i].mean())),
         "T3_cap_change_median": (float(a0[ok].median() * 0.2 / 1e9), float(a1[ok].median() * 0.2 / 1e9), float(ch.median())),
         "T3_cap_change_abs_median": (np.nan, np.nan, float(ch.abs().median())),
         "T3_frac_names_cap_stale_gt30pct": (np.nan, np.nan, float((ch.abs() > 0.30).mean())),
         "T3_frac_names_cap_too_high_gt30pct": (np.nan, np.nan, float((ch < -0.30 / 1.30).mean()))}  # old cap > new cap by >30%
    if detail:
        d = pd.DataFrame({"adv20_pre_bn": a0 / 1e9, "adv20_now_bn": a1 / 1e9, "cap_pre_bn": 0.2 * a0 / 1e9, "cap_now_bn": 0.2 * a1 / 1e9,
                          "old_cap_vs_new_pct": (a0 / a1 - 1) * 100, "ftse27": [t in FTSE27 for t in a0.index]})
        d.round(3).to_csv("t3_capit_names.csv")
    return o

i0 = e; ce = int(np.searchsorted(cdays, np.datetime64(EVENT)))
assert len(cdays) - ce == NPOST, (len(cdays) - ce, NPOST)
act = {**stats(i0), **capit(ce, detail=True)}
start = int(np.searchsorted(days, np.datetime64("2014-01-02"))); cs_off = ce - e
anch = list(range(i0 - NPOST, max(start, NPRE + 5), -NPOST))            # non-overlapping POST windows, all strictly pre-event
plc = [{**stats(i), **capit(i + cs_off)} for i in anch]
seas_i = [int(np.searchsorted(days, np.datetime64(f"{y}-09-21"))) for y in range(2014, 2026)]
seas = [{**stats(i), **capit(i + cs_off)} for i in seas_i]

rows = []
for k, (a, b, d) in act.items():
    pv = np.array([p[k][2] for p in plc if k in p]); sv = np.array([s[k][2] for s in seas if k in s])
    pv = pv[~np.isnan(pv)]; sv = sv[~np.isnan(sv)]
    rows.append(dict(metric=k, pre60=a, post=b, change=d, n_placebo=len(pv),
                     plc_p5=np.percentile(pv, 5), plc_p50=np.percentile(pv, 50), plc_p95=np.percentile(pv, 95),
                     pctile_of_actual=float((pv < d).mean() * 100), outside_5_95=bool(d < np.percentile(pv, 5) or d > np.percentile(pv, 95)),
                     n_seasonal=len(sv), seas_min=sv.min() if len(sv) else np.nan, seas_med=np.median(sv) if len(sv) else np.nan,
                     seas_max=sv.max() if len(sv) else np.nan))
out = pd.DataFrame(rows); out.to_csv("results_table.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30); pd.set_option("display.float_format", lambda x: f"{x:,.4f}")
print(f"EVENT {EVENT.date()}  POST sessions N={NPOST} ({pd.Timestamp(days[e]).date()}..{pd.Timestamp(days[-1]).date()})  PRE={NPRE} ({pd.Timestamp(days[e-NPRE]).date()}..{pd.Timestamp(days[e-1]).date()})")
print(f"placebo anchors (non-overlapping, step {NPOST}): {len(anch)}  seasonal years: {len(seas)}")
print(out.to_string(index=False))

# ---- extras: levels & group split
print("\n== b200 / univ daily since event =="); print(B.iloc[e - 3:].assign(n_univ=NU.iloc[e - 3:]).round(4).to_string())
print("\nguard: b200 threshold 0.50, univ min 100. b200 pre60 min/max:", B.b200.iloc[e - 60:e].min().round(4), B.b200.iloc[e - 60:e].max().round(4),
      "| post min/max:", B.b200.iloc[e:].min().round(4), B.b200.iloc[e:].max().round(4))
S = pd.read_csv("dt5g_live.csv", parse_dates=["time"]).set_index("time").state
print("DT5G live state: pre60", sorted(S.reindex(days[e - 60:e]).dropna().unique()), "post", sorted(S.reindex(days[e:]).dropna().unique()),
      "| transitions since 2014:", int((S.diff().fillna(0) != 0).sum()))
tp, tq = T.iloc[e - NPRE:e], T.iloc[e:]; mp, mq = tp.median(), tq.median()
inu = T.iloc[e - 1].dropna().index
def grp(names, lab):
    n = [t for t in names if t in inu]
    r = (mq[n] / mp[n]).dropna()
    print(f"{lab:28s} n={len(n):3d} medianADV pre {mp[n].median()/1e9:8.1f} bn -> post {mq[n].median()/1e9:8.1f} bn | per-name ratio median {r.median()-1:+.1%} (p25 {r.quantile(.25)-1:+.1%}, p75 {r.quantile(.75)-1:+.1%}) | sum turnover/day pre {tp[n].sum(axis=1).mean()/1e9:8.0f} post {tq[n].sum(axis=1).mean()/1e9:8.0f} bn ({tq[n].sum(axis=1).mean()/tp[n].sum(axis=1).mean()-1:+.1%})")
    return r
print("\n== group split (turnover, VND bn; PIT universe members on 2026-09-18) ==")
print("FTSE27 not in universe_pit on 09-18:", [t for t in FTSE27 if t not in inu])
grp(FTSE6, "FTSE All-World 6"); grp([t for t in FTSE27 if t not in FTSE6], "FTSE small-cap 21"); grp(FTSE27, "FTSE27 all")
grp([t for t in inu if t not in FTSE27], "rest of universe"); 
pool = L.iloc[e - 1].dropna().nlargest(60).index
grp(pool, "top60 liq pool (09-18)"); grp([t for t in pool if t in FTSE27], "  top60 ∩ FTSE27"); grp([t for t in pool if t not in FTSE27], "  top60 \\ FTSE27")
grp(C30, "custom30V members (08-05)"); grp([t for t in C30 if t in FTSE27], "  c30V ∩ FTSE27"); grp([t for t in C30 if t not in FTSE27], "  c30V \\ FTSE27")
print("custom30V ∩ FTSE27:", sorted(set(C30) & set(FTSE27)))
poolb = L.iloc[-1].dropna().nlargest(60).index
print("top60 pool changes 09-18 -> last:", "out", sorted(set(pool) - set(poolb)), "in", sorted(set(poolb) - set(pool)))
print("custom30V members min ADV pre/post (bn):", (mp[C30].min() / 1e9).round(2), (mq[C30].min() / 1e9).round(2), "| names <10bn pre/post:", int((mp[C30] < 10e9).sum()), int((mq[C30] < 10e9).sum()))
d = pd.read_csv("t3_capit_names.csv", index_col=0)
print("\n== CAPIT quality set (prune, 2026-09-18) =="); print(d.sort_values("adv20_pre_bn", ascending=False).to_string())
print("\nforeign share daily post:"); print((FS.iloc[e:] * 100).round(1).to_string()); print("foreign net bn post:", FN.iloc[e:].round(0).tolist())
json.dump({"event": str(EVENT.date()), "npost": NPOST, "npre": NPRE, "n_placebo": len(anch), "n_seasonal": len(seas), "ftse27": FTSE27}, open("meta.json", "w"))
