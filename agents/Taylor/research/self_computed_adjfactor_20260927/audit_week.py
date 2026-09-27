#!/usr/bin/env python3
"""Cohort audit: every ticker whose price-adjusting ex-date falls in [--ex0,--ex1].

The question this answers, which the single-ticker FPT view cannot: is the incomplete
back-adjustment specific to one ticker/vendor hiccup, or does it hit the whole cohort of events in
a date window? Run it on the suspect week AND on an earlier week as a negative control -- a method
that flags 100% of every week it is pointed at is measuring itself, not the data.
"""
import argparse
import sys

exec(open(__file__.replace("audit_week.py", "selfcomp_adjfactor.py")).read().split("if __name__")[0])

ap = argparse.ArgumentParser()
ap.add_argument("--ex0", required=True)
ap.add_argument("--ex1", required=True)
ap.add_argument("--since", default="2026-06-01")
ap.add_argument("--end", default="2026-09-25")
ap.add_argument("--tol", type=float, default=0.003)
a = ap.parse_args()

tks = [r["tk"] for r in cal.bq(f'''
  SELECT DISTINCT c.ticker AS tk FROM `{BQ}.tav2_bq.corporate_action` AS c
  WHERE c.exright_date BETWEEN DATE "{a.ex0}" AND DATE "{a.ex1}"
    AND c.event_status = "executed"
    AND (c.event_code = "DIV" OR (c.event_code = "ISS"
         AND c.issue_method_name_vi IN ("Trả Cổ tức bằng Cổ phiếu","Cổ phiếu thưởng",
                                        "Quyền mua CP cho Cổ đông hiện hữu")))''')]
print(f"cohort ex-date in [{a.ex0},{a.ex1}] : {len(tks)} tickers")
series, by_tk = load_window(tks, a.since, a.end)
print(f"{'tk':<7}{'ex':<12}{'r_obs oldest':>13}{'r_pred':>10}{'dev':>10}"
      f"{'n_bad':>7}{'n_good':>8}  verdict")
summ = {"BROKEN": [], "OK": [], "UNCOMPUTABLE": [], "NODATA": []}
for tk in sorted(series):
    curve, used, _n, unknown = build_factor_curve(tk, series[tk], by_tk.get(tk, []))
    if unknown:
        summ["UNCOMPUTABLE"].append(tk)
        print(f"{tk:<7}{str(unknown[:1]):<12}{'':>13}{'':>10}{'':>10}{'':>7}{'':>8}  UNCOMPUTABLE")
        continue
    s = [b for b in series[tk] if b["d"] >= a.since]
    if not used or not s:
        summ["NODATA"].append(tk)
        continue
    ex0 = min(d for d, _f in used)
    pre = [b for b in s if b["d"] < ex0]
    if not pre:
        summ["NODATA"].append(tk)
        continue
    dev0 = (pre[0]["price"] / pre[0]["close"]) / curve[pre[0]["d"]] - 1.0
    bad = [b for b in pre if abs((b["price"] / b["close"]) / curve[b["d"]] - 1.0) > a.tol]
    vd = "BROKEN" if len(bad) >= 3 else "OK"
    summ[vd].append(tk)
    print(f"{tk:<7}{ex0:<12}{pre[0]['price'] / pre[0]['close']:>13.6f}"
          f"{curve[pre[0]['d']]:>10.6f}{dev0:>+10.4%}{len(bad):>7}{len(pre) - len(bad):>8}  {vd}")
print()
for k, v in summ.items():
    print(f"{k:<14}{len(v):>4}  {sorted(v)}")
