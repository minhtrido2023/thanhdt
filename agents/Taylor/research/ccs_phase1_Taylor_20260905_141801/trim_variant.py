"""Descriptive follow-up, NOT a nominated hypothesis.

The H6 tercile response turned out non-monotone (MID >= TOP in IS and in BAL), so the sizing move
the hypothesis implies -- "upsize TOP, funded from the rest" -- is not what the data supports.
The only monotone piece is the BOTTOM arm being worse than everything above it.  This file prices
that mirror-image move (TRIM the bottom tercile, redistribute pro-rata upward) so the report can
state a number instead of a hunch.  It is a POST-HOC derived bucket: advancing it would be an
8th trial and needs its own pre-registration.
"""
import json
import numpy as np
import pandas as pd

exec(open("ccs_phase1_expectancy.py").read().split("# ---------------------------------------"
                                                   "------------------------------ main sweep")[0])

out = {}
for tag, f in (("PRIMARY", PRIMARY), ("+ABANDONED", SENS)):
    g = f[f.sig_rank_tercile.notna()]
    bot, rest = g[g.sig_rank_tercile == "BOTTOM"], g[g.sig_rank_tercile != "BOTTOM"]
    bd = boot_diff(rest, bot, "ret", None, B, SEED + 21)
    row = dict(n_bot=len(bot), ep_bot=int(ep_ids(bot).max() + 1),
               n_rest=len(rest), ep_rest=int(ep_ids(rest).max() + 1),
               exp_bot=float(bot.ret.mean()), exp_rest=float(rest.ret.mean()),
               win_bot=float((bot.ret > 0).mean()), win_rest=float((rest.ret > 0).mean()),
               **{f"rest_minus_bot_{k}": v for k, v in bd.items()})
    for lab, lo, hi in (("IS", 2014, IS_END), ("OOS", IS_END + 1, 2100)):
        b_, r_ = bot[bot.year.between(lo, hi)], rest[rest.year.between(lo, hi)]
        row[f"{lab}_diff"] = float(r_.ret.mean() - b_.ret.mean())
        row[f"{lab}_n_bot"] = len(b_)
    yrs = sorted(set(g.year))
    loo = {int(y): float(rest[rest.year != y].ret.mean() - bot[bot.year != y].ret.mean())
           for y in yrs}
    full = row["rest_minus_bot_diff"]
    row["loo_same_sign"] = all(np.sign(v) == np.sign(full) for v in loo.values())
    row["loo_range"] = [min(loo.values()), max(loo.values())]
    row["per_year"] = loo

    # price the trim: move x of BOTTOM's deployed capital up into the rest
    for x in (0.5, 1.0):
        per_year = []
        for y in sorted(set(g.year)):
            if y not in navy.index:
                continue
            nr, tot = navy.loc[y], 0.0
            for bk, navc, wc in (("BAL", "nav_bal", "w_bal"), ("LAG", "nav_lag", "w_lag")):
                cb = bot[(bot.year == y) & (bot.book == bk)]
                rr = rest[(rest.year == y) & (rest.book == bk)]
                if len(cb) == 0 or len(rr) == 0 or nr[navc] <= 0:
                    continue
                de = np.average(rr.ret, weights=rr.cost_vnd) - np.average(cb.ret, weights=cb.cost_vnd)
                tot += nr[wc] * (x * cb.cost_vnd.sum()) * de / nr[navc]
            per_year.append(tot)
        row[f"trim_x{x}_pp_full"] = float(np.mean(per_year) * 100)
    for lab, sel in (("IS", lambda z: z.year <= IS_END), ("OOS", lambda z: z.year > IS_END)):
        per_year = []
        for y in sorted(set(g[sel(g)].year)):
            if y not in navy.index:
                continue
            nr, tot = navy.loc[y], 0.0
            for bk, navc, wc in (("BAL", "nav_bal", "w_bal"), ("LAG", "nav_lag", "w_lag")):
                cb = bot[(bot.year == y) & (bot.book == bk)]
                rr = rest[(rest.year == y) & (rest.book == bk)]
                if len(cb) == 0 or len(rr) == 0 or nr[navc] <= 0:
                    continue
                de = np.average(rr.ret, weights=rr.cost_vnd) - np.average(cb.ret, weights=cb.cost_vnd)
                tot += nr[wc] * (1.0 * cb.cost_vnd.sum()) * de / nr[navc]
            per_year.append(tot)
        row[f"trim_x1.0_pp_{lab}"] = float(np.mean(per_year) * 100) if per_year else np.nan
    out[tag] = row

json.dump(out, open("ccs_phase1_trim_variant_exp.json", "w"), indent=2, default=float)
for k, v in out.items():
    print(f"\n=== BOTTOM-tercile trim, {k} branch ===")
    print(f"  bottom n={v['n_bot']} ep={v['ep_bot']} exp={v['exp_bot']:+.4f} win={v['win_bot']:.3f}")
    print(f"  rest   n={v['n_rest']} ep={v['ep_rest']} exp={v['exp_rest']:+.4f} win={v['win_rest']:.3f}")
    print(f"  rest-bottom = {v['rest_minus_bot_diff']:+.4f} "
          f"95%CI[{v['rest_minus_bot_lo']:+.4f},{v['rest_minus_bot_hi']:+.4f}] "
          f"p={v['rest_minus_bot_p_boot']:.4f}")
    print(f"  IS {v['IS_diff']:+.4f} (n_bot={v['IS_n_bot']}) | OOS {v['OOS_diff']:+.4f} "
          f"(n_bot={v['OOS_n_bot']}) | LOO same sign={v['loo_same_sign']} "
          f"range[{v['loo_range'][0]:+.4f},{v['loo_range'][1]:+.4f}]")
    print(f"  dCAGR bound: trim 50% {v['trim_x0.5_pp_full']:+.3f}pp | trim 100% "
          f"{v['trim_x1.0_pp_full']:+.3f}pp  (IS {v['trim_x1.0_pp_IS']:+.3f} / OOS "
          f"{v['trim_x1.0_pp_OOS']:+.3f})   [floor {NOISE_FLOOR_PP}pp]")
