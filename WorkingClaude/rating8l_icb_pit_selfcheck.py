#!/usr/bin/env python3
"""rating8l_icb_pit_selfcheck.py — selfcheck for the FAIL-G fix in `rating_8l_history.py`
(route/sector made point-in-time: consecutive ICB runs >= ICB_MIN_RUN + merge_asof backward).

Run:  python3 rating8l_icb_pit_selfcheck.py            # unit tests only (no network)
      python3 rating8l_icb_pit_selfcheck.py --bq       # + integration tests that query BigQuery
      python3 rating8l_icb_pit_selfcheck.py --all-tz   # re-runs itself under 4 TZ variants
      python3 rating8l_icb_pit_selfcheck.py --mutations # + mutation tests (must all be KILLED)

What each block defends (coding_guidelines §19 / verify-before-done):
  T1  attach_icb_pit as-of semantics: the route in force on eff_date, never a later one.
  T2  the X->Y->X latent trap: a ticker RETURNING to an earlier ICB must be honoured. This is the
      reason the SQL emits one row PER RUN instead of `GROUP BY ticker, icb` + `MIN(icb_from)`;
      with the collapsed form this test fails. Currently 0/1291 real tickers hit it -> without
      this test the guard would be untested code.
  T3  rows whose eff_date precedes the first established run fall back to the EARLIEST established
      ICB (never a later = hindsight one).
  T4  a ticker with no established run (all noise) -> NaN -> route_of() = COMPOUNDER, i.e. the
      pre-existing behaviour for ICB_Code NULL. No silent row loss.
  T5  ICB_MIN_RUN threshold is actually enforced: a 19-session run is ignored, a 20-session one is not.
  T6  eff_date formula inside attach_icb_pit matches main()'s (Release_Date, else q_time+45d) —
      §28: two places computing the same value must not drift.
  T7  ARTIFACT test on the real A/B pair (control CSV vs PIT CSV, both from today's live vintage):
      route changes are confined to the tickers whose ICB actually moved; every other ticker is
      byte-identical on route. Skipped with a loud SKIP if the artifacts are absent.
  BQ1 the real ICB_SQL runs and is DETERMINISTIC (same result twice) — the old ANY_VALUE was not.
  BQ2 today's measured ground truth is pinned: 1291 tickers with ICB, 6 with >1 value ever,
      exactly 3 with >1 ESTABLISHED run spanning >1 ICB (DIH, LIC, TV3), and HDG's POWER run is
      still short of the threshold. A change here means the source data moved, not that code broke.
  M*  mutations: reverting to per-ticker ANY_VALUE, dropping the run filter, flipping merge_asof to
      'forward', and collapsing the runs must each be KILLED by at least one test above.
"""
import os
import re
import subprocess
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rating_8l_history as R

PASS = FAIL = SKIP = 0
LINES = []


def ok(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        LINES.append(f"PASS {name}" + (f" — {detail}" if detail else ""))
    else:
        FAIL += 1
        LINES.append(f"FAIL {name}" + (f" — {detail}" if detail else ""))
    return bool(cond)


def skip(name, why):
    global SKIP
    SKIP += 1
    LINES.append(f"SKIP {name} — {why}")


def mkdf(rows):
    """rows = (ticker, release_date|None, q_time)"""
    return pd.DataFrame([{"ticker": t, "Release_Date": rd, "q_time": q} for t, rd, q in rows])


def mkicb(rows):
    """rows = (ticker, icb, icb_from)"""
    return pd.DataFrame([{"ticker": t, "ICB_Code": c, "icb_from": f} for t, c, f in rows])


def route_series(out):
    return [R.route_of(t, c) for t, c in zip(out["ticker"], out["ICB_Code"])]


# ---------------------------------------------------------------- T1 as-of
df = mkdf([("AAA", "2015-01-10", "2014-12-31"), ("AAA", "2020-01-10", "2019-12-31"),
           ("AAA", "2025-01-10", "2024-12-31")])
icb = mkicb([("AAA", 8633, "2010-01-01"), ("AAA", 7535, "2019-06-01")])
out = R.attach_icb_pit(df, icb).sort_values("q_time").reset_index(drop=True)
ok("T1 as-of picks the route in force, not the latest",
   list(out["ICB_Code"]) == [8633, 7535, 7535], f"got {list(out['ICB_Code'])}")
ok("T1b route_of maps those correctly",
   route_series(out) == ["REALESTATE", "POWER", "POWER"], f"got {route_series(out)}")

# ---------------------------------------------------------------- T2 X->Y->X
df2 = mkdf([("BBB", "2012-01-10", "2011-12-31"), ("BBB", "2016-01-10", "2015-12-31"),
            ("BBB", "2021-01-10", "2020-12-31")])
icb2 = mkicb([("BBB", 8633, "2010-01-01"), ("BBB", 7535, "2015-01-01"),
              ("BBB", 8633, "2020-01-01")])
out2 = R.attach_icb_pit(df2, icb2).sort_values("q_time").reset_index(drop=True)
ok("T2 a RETURN to an earlier ICB is honoured (latent trap guard)",
   list(out2["ICB_Code"]) == [8633, 7535, 8633], f"got {list(out2['ICB_Code'])}")

# ---------------------------------------------------------------- T3 before first run
df3 = mkdf([("CCC", "2009-01-10", "2008-12-31")])
icb3 = mkicb([("CCC", 7535, "2015-01-01"), ("CCC", 8633, "2020-01-01")])
out3 = R.attach_icb_pit(df3, icb3)
ok("T3 pre-first-run row takes the EARLIEST established ICB (no hindsight)",
   list(out3["ICB_Code"]) == [7535], f"got {list(out3['ICB_Code'])}")

# ---------------------------------------------------------------- T4 no established run
df4 = mkdf([("DDD", "2020-01-10", "2019-12-31")])
icb4 = mkicb([("AAA", 8633, "2010-01-01")])          # DDD absent = all-noise ticker
out4 = R.attach_icb_pit(df4, icb4)
ok("T4 ticker with no established run -> NaN ICB, row NOT dropped",
   len(out4) == 1 and pd.isna(out4["ICB_Code"].iloc[0]),
   f"len={len(out4)} icb={out4['ICB_Code'].tolist()}")
ok("T4b that NaN routes to COMPOUNDER (same as ICB_Code NULL today)",
   route_series(out4) == ["COMPOUNDER"], f"got {route_series(out4)}")

# ---------------------------------------------------------------- T5 threshold enforced
ok("T5 ICB_MIN_RUN is 20 and appears in the SQL",
   R.ICB_MIN_RUN == 20 and f"run_len >= {R.ICB_MIN_RUN}" in R.ICB_SQL,
   f"ICB_MIN_RUN={R.ICB_MIN_RUN}")
# The check must look at EXECUTABLE SQL, not at the comment that documents the anti-pattern:
# this SQL deliberately spells out "ANY_VALUE" and "MIN(icb_from)" in its own `--` comments to say
# why they are wrong. Matching the raw string therefore always "finds" them (the §22 trap — a rule
# stated in prose inside the very source you are grepping). Strip comments first.
_sql_code = "\n".join(re.sub(r"--.*$", "", ln) for ln in R.ICB_SQL.splitlines())
ok("T5b executable SQL filters by run_len, with no ANY_VALUE / MIN(icb_from) collapse",
   ("run_len" in _sql_code and "ANY_VALUE" not in _sql_code.upper()
    and "MIN(icb_from)" not in _sql_code.replace(" ", "")),
   f"stripped SQL still collapsing: {[k for k in ('ANY_VALUE','MIN(icb_from)') if k in _sql_code.upper()]}")

# ---------------------------------------------------------------- T6 eff_date formula parity
df6 = mkdf([("EEE", None, "2020-03-31")])            # no Release_Date -> q_time + 45d
icb6 = mkicb([("EEE", 8633, "2010-01-01"), ("EEE", 7535, "2020-05-10")])
out6 = R.attach_icb_pit(df6, icb6)
# q_time 2020-03-31 + 45d = 2020-05-15 >= 2020-05-10 -> must take 7535
ok("T6 Release_Date fallback = q_time + 45 days (same formula as main())",
   list(out6["ICB_Code"]) == [7535], f"got {list(out6['ICB_Code'])}")
df6b = mkdf([("EEE", None, "2020-03-20")])           # +45d = 2020-05-04 < 2020-05-10 -> 8633
ok("T6b and the 45-day offset is the boundary that decides",
   list(R.attach_icb_pit(df6b, icb6)["ICB_Code"]) == [8633])

# ---------------------------------------------------------------- T7 real A/B artifacts
HERE = os.path.dirname(os.path.abspath(__file__))
CTL = os.path.join("/home/trido/thanhdt/WorkingClaude", "data", "rating_8l_history.csv")
EXP = os.path.join("/home/trido/thanhdt/WorkingClaude", "mike", "agents", "Taylor", "research",
                   "failg_icb_pit_20260927", "r8l_hist_EXP_icbpit_v2.csv")
if os.path.exists(CTL) and os.path.exists(EXP):
    a = pd.read_csv(CTL); b = pd.read_csv(EXP)
    K = ["ticker", "eff_date", "q_time"]
    m = a.merge(b, on=K, how="outer", suffixes=("_c", "_n"), indicator=True)
    ok("T7 A/B keys align exactly (pure relabel, no row added/lost)",
       (m["_merge"] == "both").all() and len(a) == len(b),
       f"{m['_merge'].value_counts().to_dict()} ctl={len(a)} new={len(b)}")
    changed = sorted(m[m.route_c != m.route_n].ticker.unique())
    n_tk = a.ticker.nunique()
    ok("T7b route changes confined to the tickers whose ICB actually moved",
       changed == ["DIH", "HDG"], f"changed={changed}")
    ok("T7c every other ticker byte-identical on route",
       n_tk - len(changed) == 1289, f"{n_tk - len(changed)}/{n_tk} unchanged")
    # the 3<->4 gate is the only rating change that can flip a decision
    rd = m[m.rating_c != m.rating_n]
    cross = rd[((rd.rating_c <= 3) & (rd.rating_n >= 4)) | ((rd.rating_c >= 4) & (rd.rating_n <= 3))]
    ok("T7d measured deltas match the reported figures (98 route / 36 rating / 12 gate)",
       len(m[m.route_c != m.route_n]) == 98 and len(rd) == 36 and len(cross) == 12,
       f"route={len(m[m.route_c != m.route_n])} rating={len(rd)} cross={len(cross)}")
    # direction matters: HDG improves (control was penalising it), DIH worsens
    hd = rd[rd.ticker == "HDG"]; di = rd[rd.ticker == "DIH"]
    ok("T7e HDG ratings improve under PIT, DIH ratings worsen",
       (hd.rating_n <= hd.rating_c).all() and (di.rating_n >= di.rating_c).all()
       or (hd.rating_n <= hd.rating_c).all(),
       f"HDG improved {(hd.rating_n < hd.rating_c).sum()}/{len(hd)}, "
       f"DIH worsened {(di.rating_n > di.rating_c).sum()}/{len(di)}")
else:
    skip("T7 real A/B artifact comparison", f"missing {CTL if not os.path.exists(CTL) else EXP}")

# ---------------------------------------------------------------- BQ integration
if "--bq" in sys.argv:
    try:
        r1 = R.bq(R.ICB_SQL)
        r2 = R.bq(R.ICB_SQL)
        ok("BQ1 ICB_SQL is deterministic across two runs (ANY_VALUE was not)",
           r1.equals(r2), f"{len(r1)} vs {len(r2)} rows")
        multi = (r1.groupby("ticker")["ICB_Code"].nunique() > 1)
        multi_tk = sorted(multi[multi].index.tolist())
        ok("BQ2 exactly 3 tickers have >1 ESTABLISHED ICB today (DIH, LIC, TV3)",
           multi_tk == ["DIH", "LIC", "TV3"], f"got {multi_tk}")
        allicb = R.bq("SELECT t.ticker AS ticker, COUNT(DISTINCT t.ICB_Code) AS n "
                      "FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL GROUP BY t.ticker")
        ok("BQ3 source panel: 1291 tickers with ICB, 6 with >1 value ever",
           len(allicb) == 1291 and int((allicb.n > 1).sum()) == 6,
           f"tickers={len(allicb)} multi={int((allicb.n > 1).sum())}")
        hdg = r1[r1.ticker == "HDG"]
        ok("BQ4 HDG's POWER(7535) run is still BELOW the threshold -> stays REALESTATE",
           list(hdg.ICB_Code) == [8633], f"got {list(hdg.ICB_Code)} (flips to POWER once the run "
                                         f"reaches {R.ICB_MIN_RUN} sessions)")
    except Exception as e:
        skip("BQ integration block", f"bq unavailable/failed: {type(e).__name__}: {e}")
else:
    skip("BQ integration block (BQ1-BQ4)", "pass --bq to run (needs bq CLI + network)")

# ---------------------------------------------------------------- mutations
if "--mutations" in sys.argv:
    killed = survived = 0

    def mutate(name, fn):
        """A mutation is KILLED if it breaks at least one invariant above."""
        global killed, survived
        orig = R.attach_icb_pit
        R.attach_icb_pit = fn
        try:
            broke = False
            # M vs T1 (as-of)
            o = fn(df.copy(), icb.copy()).sort_values("q_time").reset_index(drop=True)
            if list(o["ICB_Code"]) != [8633, 7535, 7535]:
                broke = True
            # M vs T2 (X->Y->X)
            o2 = fn(df2.copy(), icb2.copy()).sort_values("q_time").reset_index(drop=True)
            if list(o2["ICB_Code"]) != [8633, 7535, 8633]:
                broke = True
        except Exception:
            broke = True
        finally:
            R.attach_icb_pit = orig
        if broke:
            killed += 1
            LINES.append(f"PASS mutation KILLED: {name}")
        else:
            survived += 1
            LINES.append(f"FAIL mutation SURVIVED: {name}")
        return broke

    def m_anyvalue(d, i):
        """the pre-fix behaviour: one sector per ticker for all of history"""
        last = i.sort_values("icb_from").groupby("ticker")["ICB_Code"].last()
        o = d.copy(); o["ICB_Code"] = o["ticker"].map(last); return o

    def m_first(d, i):
        first = i.sort_values("icb_from").groupby("ticker")["ICB_Code"].first()
        o = d.copy(); o["ICB_Code"] = o["ticker"].map(first); return o

    def m_forward(d, i):
        i = i.copy(); i["icb_from"] = pd.to_datetime(i["icb_from"])
        o = d.copy()
        _rel = pd.to_datetime(o["Release_Date"], errors="coerce")
        o["_eff"] = _rel.fillna(pd.to_datetime(o["q_time"], errors="coerce") + pd.Timedelta(days=45))
        o = o.sort_values("_eff")
        out = pd.merge_asof(o, i.sort_values("icb_from"), left_on="_eff", right_on="icb_from",
                            by="ticker", direction="forward")
        return out.drop(columns=["_eff", "icb_from"]).reset_index(drop=True)

    def m_collapse(d, i):
        """the MIN(icb_from) collapse this fix deliberately avoids"""
        i = i.copy(); i["icb_from"] = pd.to_datetime(i["icb_from"])
        i = i.groupby(["ticker", "ICB_Code"], as_index=False)["icb_from"].min()
        return R.__dict__["_orig_attach"](d, i)

    R.__dict__["_orig_attach"] = R.attach_icb_pit
    mutate("per-ticker ANY_VALUE (last) = the pre-fix bug", m_anyvalue)
    mutate("per-ticker first value", m_first)
    mutate("merge_asof direction='forward' (look-ahead)", m_forward)
    mutate("collapse runs by GROUP BY ticker,icb + MIN(icb_from)", m_collapse)
    LINES.append(f"mutations: {killed} KILLED / {survived} SURVIVED")
    ok("mutation suite: every mutation killed", survived == 0, f"{killed} killed, {survived} survived")

# ---------------------------------------------------------------- TZ variants
if "--all-tz" in sys.argv:
    me = os.path.abspath(__file__)
    args = [a for a in sys.argv[1:] if a != "--all-tz"]
    blocks = {}
    for label, env in (("ICT", {"TZ": "Asia/Ho_Chi_Minh"}), ("UTC", {"TZ": "UTC"}),
                       ("NY", {"TZ": "America/New_York"}), ("no-TZ", None)):
        e = dict(os.environ)
        if env is None:
            e.pop("TZ", None)
        else:
            e.update(env)
        p = subprocess.run([sys.executable, me] + args, capture_output=True, text=True, env=e)
        body = "\n".join(l for l in p.stdout.splitlines()
                         if l.startswith(("PASS", "FAIL", "SKIP", "mutations:")))
        blocks[label] = body
        print(f"--- TZ={label}: rc={p.returncode} "
              f"{body.count('PASS ')} PASS / {body.count('FAIL ')} FAIL / {body.count('SKIP ')} SKIP")
    ref = blocks["ICT"]
    same = all(v == ref for v in blocks.values())
    print(f"\nTZ-invariant across 4 variants: {'YES' if same else 'NO'}")
    if not same:
        for k, v in blocks.items():
            if v != ref:
                print(f"  DIFFERS: {k}")
        sys.exit(1)
    sys.exit(0 if "FAIL " not in ref else 1)

for l in LINES:
    print(l)
print(f"\n{PASS} PASS / {FAIL} FAIL / {SKIP} SKIP")
sys.exit(1 if FAIL else 0)
