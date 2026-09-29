"""Concentration / capacity / overlap diagnostics for the two hypotheses that survived the
Phase 1 screen (H4, H6), plus the practical-significance bound recomputed on OOS DATA ONLY.

The screen's own criterion is only "IS and OOS same sign".  A hypothesis can pass that while the
OOS point estimate is a small fraction of the IS one, which is exactly the case worth surfacing:
Phase 2 would be sized off the OOS reality, not the IS number.
"""
import json
import numpy as np
import pandas as pd

exec(open("ccs_phase1_expectancy.py").read().split("# ---------------------------------------"
                                                    "------------------------------ main sweep")[0])

def arms(f, mfn, bk):
    g = scope(f, bk); mt, mc = mfn(g)
    return g, g[mt.fillna(False)], g[mc.fillna(False)]

CAND = [("H4", m_h4, "LAG"), ("H6", m_h6, "BOTH")]
res = {}
for hid, mfn, bk in CAND:
    g, t, c = arms(PRIMARY, mfn, bk)
    comp = g.drop(index=t.index)
    d_full = t.ret.mean() - c.ret.mean()

    # --- 1. ticker concentration: drop the single most-traded name, then the best name
    tk = t.ticker.value_counts()
    drops = {}
    for nm in list(tk.index[:3]):
        tt, cc = t[t.ticker != nm], c[c.ticker != nm]
        drops[f"drop_{nm}(n={int(tk[nm])})"] = float(tt.ret.mean() - cc.ret.mean())
    by_tk = t.groupby("ticker").ret.mean()
    best = by_tk.idxmax()
    tt, cc = t[t.ticker != best], c[c.ticker != best]
    drops[f"drop_best_ticker_{best}"] = float(tt.ret.mean() - cc.ret.mean())

    # --- 2. sector concentration
    sec = (t.groupby("sector").ret.agg(["size", "mean"]).sort_values("size", ascending=False))
    top_sec = sec.index[0]
    tt, cc = t[t.sector != top_sec], c[c.sector != top_sec]
    drops[f"drop_top_sector_{top_sec}(n={int(sec.iloc[0]['size'])})"] = float(
        tt.ret.mean() - cc.ret.mean())

    # --- 3. capacity: is the conviction group structurally thinner?
    cap = dict(t_pct_adv_med=float(t.pct_adv.median()), c_pct_adv_med=float(c.pct_adv.median()),
               t_pct_adv_p90=float(t.pct_adv.quantile(.9)), c_pct_adv_p90=float(c.pct_adv.quantile(.9)),
               t_adv_bn_med=float(t.adv_vnd.median() / 1e9), c_adv_bn_med=float(c.adv_vnd.median() / 1e9),
               t_over_10pct_adv=float((t.pct_adv > 0.10).mean()),
               c_over_10pct_adv=float((c.pct_adv > 0.10).mean()))

    # --- 4. duration: raw `ret` is not duration-normalised, so check the groups match
    dur = dict(t_hold_mean=float(t.holding_sessions.mean()), c_hold_mean=float(c.holding_sessions.mean()),
               t_hold_med=float(t.holding_sessions.median()), c_hold_med=float(c.holding_sessions.median()))

    # --- 5. practical significance recomputed on OOS ONLY
    t_o, c_o, comp_o = t[t.year > IS_END], c[c.year > IS_END], comp[comp.year > IS_END]
    feas_oos = feasibility_pp(t_o, comp_o) if len(t_o) and len(comp_o) else np.nan
    feas_is = feasibility_pp(t[t.year <= IS_END], comp[comp.year <= IS_END])

    res[hid] = dict(book=bk, n_t=len(t), n_c=len(c), diff_full=float(d_full),
                    n_tickers_t=int(t.ticker.nunique()),
                    top3_share=float(tk.head(3).sum() / len(t)),
                    robustness_drops=drops, sector_top=str(top_sec),
                    sector_profile={str(k): [int(v["size"]), float(v["mean"])]
                                    for k, v in sec.round(4).to_dict("index").items()},
                    capacity=cap, duration=dur,
                    feas_pp_full=float(feasibility_pp(t, comp)),
                    feas_pp_IS=float(feas_is), feas_pp_OOS=float(feas_oos))

# --- 6. do the two candidates overlap? (a joint Phase 2 must know)
_, t4, _ = arms(PRIMARY, m_h4, "LAG")
_, t6, _ = arms(PRIMARY, m_h6, "BOTH")
ov = len(set(t4.index) & set(t6.index))
res["overlap_H4_H6"] = dict(n_H4=len(t4), n_H6=len(t6), n_both=ov,
                            share_of_H4_inside_H6=ov / len(t4))

# --- 7. H6: BAL vs LAG, and the BOTTOM arm's own thinness
for bkk in ("BAL", "LAG"):
    g = PRIMARY[PRIMARY.book == bkk]
    t_, c_ = g[g.sig_rank_tercile == "TOP"], g[g.sig_rank_tercile == "BOTTOM"]
    res.setdefault("H6_book", {})[bkk] = dict(
        n_t=len(t_), n_c=len(c_), ep_t=int(ep_ids(t_).max() + 1), ep_c=int(ep_ids(c_).max() + 1),
        diff=float(t_.ret.mean() - c_.ret.mean()),
        IS=float(t_[t_.year <= IS_END].ret.mean() - c_[c_.year <= IS_END].ret.mean()),
        OOS=float(t_[t_.year > IS_END].ret.mean() - c_[c_.year > IS_END].ret.mean()))

json.dump(res, open("ccs_phase1_candidate_diag_exp.json", "w"), indent=2, default=float)
print(json.dumps(res, indent=2, default=float))
