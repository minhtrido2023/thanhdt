# -*- coding: utf-8 -*-
"""custom_basket.py — deterministic, BQ-reconstructable CUSTOM VN30-style parking basket.
================================================================================================
§5 of SESSION_HANDOFF_2026-06-13: at large NAV the strict-E1VFVN30 parking cap strands idle cash.
This module builds a high-capacity, rule-based liquid VN-equity beta vehicle to replace the ETF as
the parking vehicle (own the underlyings -> no fund management fee, only rebalance friction).

The basket is a pure deterministic function of raw tav2_bq data, so an independent auditor can
rebuild it from scratch and verify every parking-row price. Shared by pt_v23_audit_2014.py /
pt_v22_dt5g.py (simulation) and data/v23_audit_spotcheck.py (verification): identical series.

UNIVERSE = RULES, NOT EXCEPTIONS: members come from UNIVERSE_SOURCE ∩ ICB_Code IS NOT NULL (real
listed companies; indices/ETFs have NULL ICB -> auto-excluded). NO ticker is hardcoded out. VIC
competes like any name; it is admitted iff it passes the 8L quality gate (see build_pit gate_rating)
-> in practice gated out ~24/25 quarters because its 8L rating is 4-5, admitted when it earns <=3.

Construction (cap-weighted CHAINED index):
  members  = top-30 by AVG(Volume_3M_P50*COALESCE(Price,Close)); build()=static, build_pit()=PIT/quarter.
  mcap_i,t  = adjusted Close_i,t * OShares_i  -> RETURN leg only (see PRICE BASIS below).
  mcapw_i,t = raw COALESCE(Price,Close)_i,t * OShares_i  -> WEIGHT leg only.
  r_i,t    = mcap_i,t / mcap_i,t-1 - 1   (adjusted -> an ex-dividend date is NOT a loss)
  ret_t    = SUM_i(mcapw_i,t-1 * qmult_i * r_i,t) / SUM_i(mcapw_i,t-1 * qmult_i)  over names valid
             on BOTH t-1 and t (chained -> listings/halts cause no composition jumps).
  level_t  = 1000 * cumprod(1 + ret_t).   (base 1000 arbitrary; only returns matter for parking.)
  adv_t    = 60-session rolling mean of SUM_i(COALESCE(Price,Close)_i,t * Volume_i,t)  [creation capacity].

PRICE BASIS — SPLIT BY ROLE (fix 2026-08-02, job Taylor_20260802_141725; same bug family as the
`ps` lens fix `6ea466f` and the refuted PE rescale `beec96c`):
  `Close` is RETROACTIVELY adjusted for dividends/splits/bonuses; `Price` is the raw point-in-time
  quote. The adjustment factor Close/Price depends on corporate actions that happen AFTER date t
  and differs per name (median 0.219 in 2007 -> 1.000 by 2026), so pairing `Close` with a raw PIT
  quantity (`Volume`, `OShares`) injects look-ahead into any CROSS-SECTIONAL comparison.
    - SELECTION / WEIGHTING at one point in time -> raw `COALESCE(Price,Close)`. Evidence:
      `Trading_Value == Volume * Price` reproduces 100.0% of rows every year 2010-2026 (n~850k);
      `Volume * Close` only 1.1-69.8%.  (audit job Taylor_20260802_083624 §2f)
    - RETURN / momentum chains (mcap_t / mcap_t-1) -> keep adjusted `Close`. Using raw `Price` here
      would book every ex-dividend date as a price crash. This is why the fix is a ROLE SPLIT and
      NOT a file-wide Close->Price replace.
  Report: mike/agents/Taylor/research/pe_pb_basis_broad_audit_20260802.md §3
  Registry: mike/kb/data_registry/price-volume/ticker_close_vs_price_dividend_adj.md
"""
import bisect
import os
import numpy as np
import pandas as pd

BASE_LEVEL = 1000.0
# 8L quality tilt multipliers by rating (1=best..5=worst); gentle ±, cap-weight stays dominant.
QTILT = {1: 1.50, 2: 1.25, 3: 1.00, 4: 0.70, 5: 0.40}
QTILT_MISSING = 1.00
# UNIVERSE RULE (no per-name exceptions): the basket universe = real listed companies in
# UNIVERSE_SOURCE (see below), i.e. ICB_Code IS NOT NULL. That single rule auto-excludes index pseudo-tickers
# (VN30/VNINDEX) AND ETFs (E1VFVN30) — all of which carry a NULL ICB_Code — without hardcoding any
# ticker. VIC is NOT special-cased: it competes on liquidity like any name and is admitted iff it
# passes the 8L quality gate (rating<=gate). Empirically VIC is rated 4-5 in ~24/25 quarters so the
# gate excludes it BY RULE, and admits it the rare quarter it earns rating<=3 (e.g. 2020Q4).
UNIVERSE_FILTER = "t.ICB_Code IS NOT NULL"
SEL_START, SEL_END = "2020-01-01", "2025-01-01"
N_MEMBERS = 30

# ── UNIVERSE SOURCE — P2 cutover 2026-07-22 (§4.2/§4.3 ticker_prune_replacement_plan.md) ────────
# "pit"   = `tav2_mike.universe_pit_q`, membership PER DAY (branch B of the §4.3b A/B) — the team-
#           owned, append-only, point-in-time universe. Per-day EXISTS also removes the look-ahead
#           the old predicate carried (`DISTINCT ticker`-ever admits a name years before it listed).
# "prune" = legacy `tav2_bq.ticker_prune` DISTINCT-ever. Kept as the ONE-WORD ROLLBACK.
# Module-level constant on purpose, NOT an env var (env inherited through a process is exactly the
# mechanism behind incident C1 07-12 — coding_guidelines §11).
# Measured before flipping (§4.3b, job Taylor_20260722_062405): the 30-name basket is IDENTICAL at
# the LIVE rebal 2026-05-05 and at every rebal since 2018-08; diffs exist only in 2014-2015 where
# `ticker_prune` was thin.
UNIVERSE_SOURCE = "pit"
UNIVERSE_PIT_TABLE = "lithe-record-440915-m9.tav2_mike.universe_pit_q"


def pxw_sql(alias="t"):
    """SQL for the RAW point-in-time price used by the SELECTION and WEIGHT legs (see the module
    header's PRICE BASIS block). The RETURN leg never calls this — it always uses adjusted Close.

    env BASKET_PRICE_BASIS:
      "split"  (default = PRODUCTION since 2026-08-02, job Taylor_20260802_141725) — raw
               COALESCE(Price,Close). Correct: `Volume`/`OShares` are raw PIT quantities.
      "legacy" — pre-fix behaviour (adjusted `Close` for selection/weight too). Kept ONLY as the
               A/B control leg and as a one-word rollback, same role as UNIVERSE_SOURCE="prune".
               NEVER for production: it lets post-t corporate actions reorder the cross-section.
    The ADV/`tv` column is deliberately NOT routed through here — it was already on the raw basis
    before the fix, so the legacy leg must leave it alone to stay a clean single-variable control.
    """
    if os.environ.get("BASKET_PRICE_BASIS", "split").lower() == "legacy":
        return f"{alias}.Close"
    return f"COALESCE({alias}.Price,{alias}.Close)"


def universe_pred(alias="t"):
    """SQL predicate restricting `alias` (a tav2_bq.ticker row) to the universe.

    Fail-safe (§4.3): there is deliberately NO branch that silently falls back to `ticker_prune` —
    a silent fallback would re-import the very drift this migration exists to escape.
    """
    if UNIVERSE_SOURCE == "prune":
        return f"{alias}.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)"
    if UNIVERSE_SOURCE != "pit":
        raise ValueError(f"UNIVERSE_SOURCE={UNIVERSE_SOURCE!r} unknown (pit|prune)")
    return (f"EXISTS(SELECT 1 FROM `{UNIVERSE_PIT_TABLE}` u2 "
            f"WHERE u2.ticker={alias}.ticker AND u2.time={alias}.time AND u2.in_universe)")


def assert_universe_covers(bq, start_date, end_date):
    """Fail-safe (§4.3): STOP WITH AN ERROR if `universe_pit` does not cover every trading day in
    [start_date, end_date]. Without this the missing days would silently look like "no name was in
    the universe that day" — an empty basket instead of a loud failure."""
    if UNIVERSE_SOURCE != "pit":
        return
    df = bq(f"""SELECT
  (SELECT COUNT(DISTINCT t.time) FROM tav2_bq.ticker t
     WHERE t.time BETWEEN DATE '{start_date}' AND DATE '{end_date}') AS n_ticker,
  (SELECT COUNT(DISTINCT u.time) FROM `{UNIVERSE_PIT_TABLE}` u
     WHERE u.time BETWEEN DATE '{start_date}' AND DATE '{end_date}') AS n_universe""")
    n_tk, n_un = int(df["n_ticker"].iloc[0]), int(df["n_universe"].iloc[0])
    if n_un < n_tk:
        raise RuntimeError(
            f"universe_pit thieu ngay trong [{start_date},{end_date}]: co {n_un} phien / "
            f"tav2_bq.ticker co {n_tk} phien. DUNG — khong tu fallback ve ticker_prune (§4.3). "
            f"Chay lai mike/bin/build_universe_pit.py cho khoang thieu.")


def _cap_names(w, cap):
    """Iterative water-fill: cap each name's weight at `cap`, redistribute excess pro-rata to uncapped."""
    w = np.array(w, dtype=float)
    s = w.sum()
    if s <= 0: return w
    w = w / s
    for _ in range(100):
        over = w > cap + 1e-12
        if not over.any(): break
        excess = float((w[over] - cap).sum()); w[over] = cap
        under = ~over; us = float(w[under].sum())
        if us <= 1e-12: break
        w[under] = w[under] + excess * w[under] / us
    return w


def _cap_sector(w, sec, code, scap):
    """Scale the `code`-sector total weight down to `scap`; scale the rest up pro-rata."""
    w = np.array(w, dtype=float)
    s = w.sum()
    if s <= 0: return w
    w = w / s
    grp = (sec == code); g = float(w[grp].sum()); other = float(w[~grp].sum())
    if g > scap + 1e-12 and grp.any() and (~grp).any() and other > 1e-12:
        w[grp] = w[grp] * (scap / g); w[~grp] = w[~grp] * ((1.0 - scap) / other)
    return w


def _cap_group_jointly(w, grp, gcap, ncap):
    """Cap the `grp`-True group's TOTAL weight at `gcap` AND every name at `ncap`, jointly.

    Why this is not just `_cap_sector` then `_cap_names` (the pre-existing `sectorcap` path):
    `_cap_names` water-fills each over-cap name's excess pro-rata across ALL uncapped names —
    the just-capped group included — so it silently re-inflates the group above `gcap`. MEASURED
    on the real custom30V weight vector (v4final_selector_selfcheck [5], job Taylor_20260714_140127):
    a nominal 0.30 financial cap actually delivered mean 0.427 / max 0.542, breaching on 1090/1090
    days; a nominal 0.50 delivered mean 0.558. The cap never held at its stated level.

    Here each group gets a fixed BUDGET first, and the name cap is water-filled WITHIN each group,
    so neither cap can undo the other.

    FEASIBILITY: the non-group side must be able to absorb `1-gcap` under `ncap`, i.e. it needs at
    least `(1-gcap)/ncap` names. With 30 names @ ncap=0.10, holding a group at 0.30 needs >=7
    non-group names. When there are fewer, `gcap` is MATHEMATICALLY unreachable — we then raise the
    group budget to the tightest feasible value and return it, rather than silently returning a
    vector that violates one of the two caps. -> (weights, effective_group_cap).
    """
    w = np.array(w, dtype=float)
    s = w.sum()
    if s <= 0: return w, gcap
    w = w / s
    g = np.asarray(grp, dtype=bool)
    if not g.any() or not (~g).any(): return _cap_names(w, ncap), gcap
    n_out = int((~g).sum())
    gcap_eff = max(gcap, 1.0 - n_out * ncap)           # tightest budget the name cap permits
    b_in = min(float(w[g].sum()), gcap_eff)            # only ever cap DOWN, never top a group up
    out = np.zeros_like(w)
    for m, b in ((g, b_in), (~g, 1.0 - b_in)):
        if b <= 0 or w[m].sum() <= 0:
            continue
        out[m] = _cap_names(w[m], ncap / b) * b        # water-fill inside the group's own budget
    return out, gcap_eff


def select_members(bq):
    """Return the 30 most-liquid listed-company members (deterministic, STATIC/hindsight window).
    Universe = UNIVERSE_SOURCE ∩ UNIVERSE_FILTER (real companies). No per-ticker exclusions."""
    assert_universe_covers(bq, SEL_START, SEL_END)
    df = bq(f"""SELECT t.ticker FROM tav2_bq.ticker t
WHERE t.time BETWEEN DATE '{SEL_START}' AND DATE '{SEL_END}'
  AND {universe_pred()}
  AND {UNIVERSE_FILTER}
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50*{pxw_sql()}) DESC LIMIT {N_MEMBERS}""")
    return list(df["ticker"])


def build(bq, names, start_date, end_date):
    """Build the basket. Returns (level_dict{ts:level}, adv_dict{ts:adv_vnd}, raw_df).
    raw_df has columns time,ticker,Close,pxw,tv,OShares,mcap,mcapw for reconstruction transparency
    (`mcap` = RETURN leg / adjusted Close; `mcapw` = WEIGHT leg / raw price — module header)."""
    inlist = ",".join(f"'{x}'" for x in names)
    bx = bq(f"""WITH fin AS (
  SELECT f.ticker, f.time AS ftime, f.OShares,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS nft
  FROM tav2_bq.ticker_financial AS f WHERE f.OShares IS NOT NULL)
SELECT t.ticker, t.time, t.Close, {pxw_sql()} AS pxw,
       COALESCE(t.Price,t.Close)*t.Volume AS tv, fin.OShares
FROM tav2_bq.ticker AS t
LEFT JOIN fin ON fin.ticker=t.ticker AND t.time>=fin.ftime AND (fin.nft IS NULL OR t.time<fin.nft)
WHERE t.ticker IN ({inlist})
  AND t.time >= DATE_SUB(DATE '{start_date}', INTERVAL 200 DAY) AND t.time <= DATE '{end_date}'""")
    bx["time"] = pd.to_datetime(bx["time"])
    bx = bx.sort_values(["ticker", "time"])
    bx["OShares"] = bx.groupby("ticker")["OShares"].ffill().bfill()
    bx["mcap"] = bx["Close"] * bx["OShares"]          # RETURN leg (adjusted; ex-div is not a loss)
    bx["mcapw"] = bx["pxw"] * bx["OShares"]           # WEIGHT leg (raw PIT; see PRICE BASIS header)
    piv = bx.pivot_table(index="time", columns="ticker", values="mcap").sort_index()
    pivw = (bx.pivot_table(index="time", columns="ticker", values="mcapw")
              .reindex(index=piv.index, columns=piv.columns))
    valid = piv.notna() & piv.shift().notna()  # name priced on BOTH t-1 and t
    r = (piv / piv.shift() - 1.0).where(valid)                 # adjusted-Close return
    wprev = pivw.shift().where(valid).fillna(piv.shift().where(valid))  # raw-Price weight as of t-1
    # Identity: with wprev == piv.shift() this is exactly the legacy SUM(mcap_t)/SUM(mcap_t-1)-1.
    ret = (wprev.mul(r).sum(axis=1) / wprev.sum(axis=1)).fillna(0.0)
    lvl = BASE_LEVEL * (1.0 + ret).cumprod()
    adv_src = bx.groupby("time", as_index=False)["tv"].sum().sort_values("time")
    adv_src["adv"] = adv_src["tv"].rolling(60, min_periods=20).mean()
    level_dict = {t: float(v) for t, v in zip(lvl.index, lvl.values)}
    adv_dict = {t: float(v) for t, v in zip(adv_src["time"], adv_src["adv"]) if pd.notna(v)}
    return level_dict, adv_dict, bx


def build_pit(bq, start_date, end_date, top_n=N_MEMBERS, quality="none",
              rebal="qstart", gate_rating=None,
              weight_scheme="capwt", name_cap=0.10, sector_cap=0.50, sector_code=8,
              qtilt=None):
    """POINT-IN-TIME basket — removes the hindsight membership bias of build().
    Membership is re-chosen each period from ONLY past data (prior-completed-quarter average
    liquidity), ex-VIC/ex-index.

    rebal: 'qstart'  = first trading day of each calendar quarter (legacy).
           'q2m5'    = first trading day on/after the 5th of the 2nd month of each quarter
                       (Feb 5 / May 5 / Aug 5 / Nov 5). Chosen so the just-ended quarter's
                       FINANCIALS are already public -> the quality gate/rating see fresh data.
    gate_rating: None = no gate. int k = HARD SAFETY GATE — only names whose as-of 8L rating is
                 <= k (and NOT missing) may enter. k=3 = investment-grade floor; excludes the
                 manipulation/distress names (rating 4-5: PVX, OGC, HNG, SCR-in-distress, ...)
                 that pure-liquidity selection would otherwise pull in (FLC/ROS already out of
                 ticker_prune; this stops the rest). Capital-preservation guard for parked cash.
    quality: 'none' = pure cap-weight; 'tilt' = cap-weight x QTILT[as-of rating] (soft lean);
             'filter' = legacy soft filter rating<=3 (superseded by gate_rating).

    Returns (level_dict, adv_dict, members_df, raw_df). members_df: quarter,ticker,qmult,liq_rank.
    Index is a chained cap(-or-quality)-weighted return using each period's ACTIVE membership,
    so an auditor rebuilds it deterministically from raw BQ (prices, OShares, fa_ratings_8l)."""
    assert quality in ("none", "tilt", "filter")
    assert rebal in ("qstart", "q2m5")
    # qtilt: optional override of the rating->multiplier map (C+D-style sweep of TILT STRENGTH,
    # dir B 2026-06-16). None = module default QTILT. Only used when quality=='tilt'.
    QT = qtilt if qtilt else QTILT
    # WEIGHT SCHEME (de-concentration review 2026-06-15). 'capwt' = byte-identical legacy cap-weight
    # (mcap x qmult); others transform the daily cap-weight vector to bound group/single-name risk:
    #   'ew'        = equal-weight (1/n active) — kills mega-cap & sector dominance, ignores mcap/qmult.
    #   'namecap'   = cap-weight then water-fill each name to <= name_cap (limits VHM/VCB single-name).
    #   'sectorcap' = cap the sector_code (default 8 = Financials+RealEstate) group to <= sector_cap,
    #                 then also apply name_cap. Keeps it market-like but bounds the bank/RE cluster.
    #   'fincap'    = like sectorcap but the capped GROUP is the three FINANCIAL ROUTES
    #                 (BANK/INSURANCE/SECURITIES, PIT route from value_panel_2014.csv) rather than
    #                 1-digit ICB 8 — ICB-8 also sweeps in REALESTATE (8633) and brokers' parent
    #                 sector, which is NOT the cluster under discussion (job Taylor_20260714_140127).
    #                 Cap level = env BASKET_FIN_CAP (default 0.30), then name_cap as usual.
    assert weight_scheme in ("capwt", "ew", "namecap", "sectorcap", "fincap")
    # EFFECTIVE start: always work back >=~1.5y before `end` even if the caller asks for a tiny window
    # (e.g. the LIVE forward script runs a 2-day window). This guarantees recent quarterly rebalances
    # AND a full 60-session ADV history exist, so the returned levels/ADV are valid over [start,end].
    # For full-history backtests (start=2014) this is a no-op (2014 < end-600d). Returned dicts span
    # the extended range; the caller just looks up the dates it needs.
    eff_start = min(str(start_date), (pd.Timestamp(end_date) - pd.Timedelta(days=600)).strftime("%Y-%m-%d"))
    # (1) per-ticker per-quarter average secondary liquidity. Universe = listed companies only
    # (UNIVERSE_FILTER); NO per-ticker exclusions — VIC/indices/ETFs handled BY RULE (see header):
    # indices+ETFs have NULL ICB_Code so the filter drops them; VIC competes and is removed only
    # when it fails the 8L gate below.
    assert_universe_covers(bq, (pd.Timestamp(eff_start) - pd.Timedelta(days=380)).strftime("%Y-%m-%d"),
                           str(end_date))
    # PRICE BASIS (see module header): liquidity in VND = raw share count x RAW price. `Volume` is a
    # raw PIT share count, so `Volume_3M_P50*Close` mixed bases and let post-t corporate actions
    # reorder the cross-section (measured: 8.5/30 names differed pre-2014, 5.0/30 2014+).
    qliq = bq(f"""SELECT t.ticker, DATE_TRUNC(t.time, QUARTER) AS q,
  AVG(t.Volume_3M_P50*{pxw_sql()}) AS liq, COUNT(*) AS nd
FROM tav2_bq.ticker t
WHERE {universe_pred()}
  AND {UNIVERSE_FILTER}
  AND t.time >= DATE_SUB(DATE '{eff_start}', INTERVAL 380 DAY) AND t.time <= DATE '{end_date}'
GROUP BY t.ticker, q HAVING nd >= 20""")
    qliq["q"] = pd.to_datetime(qliq["q"])
    # (2) 8L ratings, as-of map per ticker (sorted time->rating)
    rat = bq(f"""SELECT r.ticker, r.time, r.rating FROM tav2_bq.fa_ratings_8l r
WHERE r.time <= DATE '{end_date}' ORDER BY r.ticker, r.time""")
    rat["time"] = pd.to_datetime(rat["time"])
    rat_by_tk = {tk: (list(g["time"]), list(g["rating"])) for tk, g in rat.groupby("ticker")}
    # FORENSIC EXCLUDE (2026-06-20, date-aware, NO hindsight): a human-flagged 'exclude' name (related-party/
    # manipulation, data/forensic_flags.csv) is forced rating 5 (fails gate<=3) ONLY from its flag date
    # forward -> dropped from custom30/V2.3 going forward; historical rebals keep its real rating (PIT-honest).
    _FORX = {}
    try:
        _ff = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "forensic_flags.csv"))
        _FORX = {r["ticker"]: pd.Timestamp(r["date"]) for _, r in _ff.iterrows() if str(r["severity"]).strip() == "exclude"}
        if _FORX: print(f"  [forensic exclude] custom30 universe drops from flag date: { {k: str(v.date()) for k,v in _FORX.items()} }")
    except Exception as e:
        print(f"  [forensic exclude] none ({e})")
    def rating_asof(tk, d):
        fd = _FORX.get(tk)
        if fd is not None and pd.Timestamp(d) >= fd: return 5.0   # forensic exclude, flag date onward
        e = rat_by_tk.get(tk)
        if not e: return np.nan
        i = bisect.bisect_right(e[0], d) - 1
        return float(e[1][i]) if i >= 0 else np.nan
    # (2b) Đ2 QUALITY-FLOOR (env BASKET_QFLOOR=1, plan_quality_sleeve_20260712.md trial QF8-NEU).
    # Fundamentals floor in PLACE OF the rating gate: ROE_Min5Y>=0.10 AND CF_OA_3Y>0 AND FSCORE>=5,
    # missing = fail (hard gate semantics, same as gate_rating). As-of Release_Date, fallback
    # time+45d when Release_Date is missing — PIT-honest, independent of fa_ratings* tables.
    # Default OFF = byte-identical.
    QFLOOR = os.environ.get("BASKET_QFLOOR", "") == "1"
    qf_by_tk = {}
    if QFLOOR:
        qf = bq(f"""SELECT f.ticker, f.time, f.Release_Date, f.ROE_Min5Y, f.CF_OA_3Y, f.FSCORE
FROM tav2_bq.ticker_financial f WHERE f.time <= DATE '{end_date}'""")
        qf["time"] = pd.to_datetime(qf["time"])
        qf["eff"] = pd.to_datetime(qf["Release_Date"]).fillna(qf["time"] + pd.Timedelta(days=45))
        qf["ok"] = (qf["ROE_Min5Y"] >= 0.10) & (qf["CF_OA_3Y"] > 0) & (qf["FSCORE"] >= 5)
        qf = qf.sort_values(["ticker", "eff"])
        qf_by_tk = {tk: (list(g["eff"]), list(g["ok"])) for tk, g in qf.groupby("ticker")}
        print(f"  [qfloor Đ2] ROE_Min5Y>=0.10 & CF_OA_3Y>0 & FSCORE>=5 as-of Release_Date "
              f"({len(qf_by_tk)} tickers, pass-rate latest {qf.groupby('ticker')['ok'].last().mean():.0%})")
    def qfloor_asof(tk, d):
        e = qf_by_tk.get(tk)
        if not e: return False
        i = bisect.bisect_right(e[0], d) - 1
        return bool(e[1][i]) if i >= 0 else False
    # (3) rebalance dates within [start,end]
    cal = bq(f"""SELECT DISTINCT t.time FROM tav2_bq.ticker t WHERE t.ticker='VNINDEX'
  AND t.time BETWEEN DATE '{eff_start}' AND DATE '{end_date}' ORDER BY t.time""")
    cal["time"] = pd.to_datetime(cal["time"])
    days = list(cal["time"])
    if rebal == "q2m5":
        days_arr = np.array(days, dtype="datetime64[ns]")
        sd, ed = pd.Timestamp(eff_start), pd.Timestamp(end_date)
        rebal_dates = []
        for Y in range(sd.year, ed.year + 1):
            for mo in (2, 5, 8, 11):  # 2nd month of each quarter
                i = int(np.searchsorted(days_arr, np.datetime64(pd.Timestamp(Y, mo, 5)), side="left"))
                if i < len(days_arr):
                    a = pd.Timestamp(days_arr[i])
                    if sd <= a <= ed: rebal_dates.append(a)
        rebal_dates = sorted(set(rebal_dates))
    else:  # qstart
        q_of = pd.Series(days, index=days).groupby(pd.Grouper(freq="QS")).min().dropna()
        rebal_dates = [pd.Timestamp(d) for d in sorted(q_of.values.astype("datetime64[ns]"))]
    # (4) per-quarter membership from PRIOR-quarter liquidity (PIT)
    liq_piv = qliq.pivot_table(index="q", columns="ticker", values="liq")
    # CFO-yield SELECTION BLEND (env BASKET_CFO_BLEND; default 0 = byte-identical pure-liquidity selection).
    # When >0: among the top-BASKET_CFO_POOL liquid gated names (tradability floor), pick top_n by
    # rank_pct(liq)+lam*rank_pct(cfo_yield) instead of pure liquidity. Tests custom30 as a quality-value
    # core (validated standalone 2026-06-16: +0.66pp/-1.7pp DD at lam=0.5). cfo_yield = prior-quarter 1/PCF.
    CFO_BLEND = float(os.environ.get("BASKET_CFO_BLEND", "0"))
    CFO_POOL  = int(os.environ.get("BASKET_CFO_POOL", "60"))
    _YM = os.environ.get("BASKET_YIELD_METRIC", "pcf").lower()   # "pe" = stable earnings yield (preferred)
    SELECT_MODE = os.environ.get("BASKET_SELECT", "blend").lower()  # "blend" (liq+lam*yield) | "yieldcombo" (custom30V)
    # AUDIT-ONLY hard exclude (env BASKET_EXCLUDE="HVN,VJC,..."; prod default empty = byte-identical).
    # Tests whether a Permanent Exclude List (sector-sweep flagged structural value-traps) helps the basket.
    EXCLUDE = {x.strip().upper() for x in os.environ.get("BASKET_EXCLUDE", "").split(",") if x.strip()}
    # RESEARCH FORK (adaptive_exclusion_20260904, NOT production): PIT dynamic quality/leverage
    # gate loaded from a precomputed (ticker, start, end) episode CSV — env BASKET_DYNAMIC_GATE_CSV.
    # Default empty = byte-identical to upstream custom_basket.py.
    _DYN_CSV = os.environ.get("BASKET_DYNAMIC_GATE_CSV", "")
    _DYN_EVENTS = {}
    if _DYN_CSV:
        _dyn_df = pd.read_csv(_DYN_CSV, parse_dates=["start", "end"])
        for _tk, _g in _dyn_df.groupby("ticker"):
            _DYN_EVENTS[_tk] = list(zip(_g["start"], _g["end"]))

    def dyn_excluded_asof(tk, d):
        for s, e in _DYN_EVENTS.get(tk, []):
            if s <= d <= e:
                return True
        return False
    # BULL sleeve (custom30B) audit knobs (env, prod default OFF): absolute liquidity floor + 1/PE-led selectors.
    # LIQ_FLOOR_B = min prior-quarter avg secondary liq (VND bn/day) to ENTER (deploy more capital, ~10 = user).
    # SELECT_MODE 'petop' = pure rank(1/PE) (bull IC champion +0.161). 'pemom' = rank(1/PE)+MOM_W*rank(mom200).
    LIQ_FLOOR = float(os.environ.get("BASKET_LIQ_FLOOR_B", "0")) * 1e9
    MOM_W = float(os.environ.get("BASKET_MOM_W", "0.5"))
    RSI_W = float(os.environ.get("BASKET_RSI_W", "0"))   # custom30B: + RSI_W*rank(prior-q avg D_RSI) (best bull add)
    # AUDIT-ONLY knob BASKET_PEADJ=1 (default OFF -> byte-identical): multiply PE/PCF by the price
    # ratio Price/Close before inverting, i.e. yield = 1/(col * Price/Close) instead of 1/col.
    # ⚠️ THIS IS THE *BIASED* LEG, KEPT ONLY TO MEASURE THE COST OF A MISTAKE — never turn it on in
    # production. Job Taylor_20260802_042110 claimed tav2_bq.ticker.PE was stored on an ADJUSTED-close
    # basis and that this multiplication removes a look-ahead. Job Taylor_20260802_054825 REFUTED that
    # at universe scale (2014-2021, 1,419,351 rows / 23,067 ticker x report-period): PE/Price is exactly
    # constant within a report period in 93.1% of periods vs 11.0% for PE/Close (PB 94.6/12.6, PCF
    # 86.9/20.3); hand-check VNM & FPT 2015-06-30 reproduce NP_ttm/OShares from the RAW Price only.
    # => PE/PB/PCF are already raw-Price point-in-time correct; multiplying by Price/Close INJECTS
    # look-ahead (the ratio depends on dividend/bonus events AFTER date t). See the data_registry entry
    # mike/kb/data_registry/fundamentals/valuation_pe_pb_pcf_ps.md "Bay (4)".
    PEADJ = os.environ.get("BASKET_PEADJ", "") == "1"
    def _yield_piv(col):
        _expr = (f"SAFE_DIVIDE(1, t.{col} * SAFE_DIVIDE(t.Price, t.Close))" if PEADJ
                 else f"SAFE_DIVIDE(1, t.{col})")
        _extra = " AND t.Price > 0 AND t.Close > 0" if PEADJ else ""
        _y = bq(f"""SELECT t.ticker, DATE_TRUNC(t.time, QUARTER) AS q, AVG({_expr}) AS y
FROM tav2_bq.ticker t WHERE t.{col} > 0{_extra} AND t.time BETWEEN DATE '{eff_start}' AND DATE '{end_date}'
GROUP BY t.ticker, q""")
        _y["q"] = pd.to_datetime(_y["q"])
        return _y.pivot_table(index="q", columns="ticker", values="y")
    def _mom_piv():
        _m = bq(f"""SELECT t.ticker, DATE_TRUNC(t.time, QUARTER) AS q,
  AVG(SAFE_DIVIDE(t.Close, NULLIF(t.MA200,0)) - 1) AS m
FROM tav2_bq.ticker t WHERE t.MA200 > 0 AND t.time BETWEEN DATE '{eff_start}' AND DATE '{end_date}'
GROUP BY t.ticker, q""")
        _m["q"] = pd.to_datetime(_m["q"])
        return _m.pivot_table(index="q", columns="ticker", values="m")
    def _rsi_piv():
        _r = bq(f"""SELECT t.ticker, DATE_TRUNC(t.time, QUARTER) AS q, AVG(t.D_RSI) AS r
FROM tav2_bq.ticker t WHERE t.D_RSI IS NOT NULL AND t.time BETWEEN DATE '{eff_start}' AND DATE '{end_date}'
GROUP BY t.ticker, q""")
        _r["q"] = pd.to_datetime(_r["q"])
        return _r.pivot_table(index="q", columns="ticker", values="r")
    # ---- AUDIT-ONLY DCF overlay on the custom30V (yieldcombo) selector (Pha 3, Taylor 2026-07-14) ----
    # BASKET_DCF_MODE: "" (default, OFF -> byte-identical) | "exclude_rich" (variant A: drop
    #   status==RICH AND robust==True from the pool BEFORE ranking) | "tiebreak" (variant B: add
    #   BASKET_DCF_W * rank_pct(MoS) to the yieldcombo score, no hard exclude).
    # NOT_COMPUTED is a NEUTRAL pass-through in BOTH variants: never dropped (A), and given the
    # same 0.5 mid-rank the production selector already uses for a missing yield (B) — i.e. neither
    # auto-cheap nor auto-rich. Verified explicitly by dcf_selector_selfcheck.py.
    # status/robust replicate trading_bot/strategies.py::_dcf_check_for_order exactly (Pha 2 rule):
    #   status = CHEAP iff MoS>0 else RICH; robust = MoS keeps its sign across the whole ±1pp-r /
    #   ±2pp-g sensitivity box. PIT: fair_value(asof=d) itself picks the last release <= d; price =
    #   Price at d (the backtest analogue of production's live order ref price).
    # We call fair_value(asof=d) LIVE (memoised per (ticker, rebal date)) rather than reading a
    # per-release FV cache: fair_value resolves the discount rate and terminal g AT `asof`, so a
    # cache keyed by release date prices them at rel_time instead of d and does NOT reproduce
    # production (measured: 14/40 samples off, incl. a CHEAP/RICH flip on a knife-edge MoS≈0 name).
    # Both are look-ahead-free, but only asof=d matches the gate we are actually testing. Cost is
    # ~5ms/call * ~pool*rebal_dates ≈ 30s per run — not worth an approximation on a level call.
    # "placebo_random" (Pha 4, job Taylor_20260714_080414): the null-distribution control for variant
    # A. At each rebal date it drops the SAME NUMBER of names exclude_rich would have dropped that
    # day, but picks the victims at RANDOM instead of by DCF. Same count, same pool, same stage,
    # same fail-safe -> the ONLY difference vs variant A is *which* names go. If A's edge survives
    # only because "3 names got swapped in a 30-name basket", the placebo reproduces it.
    # "placebo_pe" (Pha 5, job Taylor_20260715_041608): the value-proxy control for variant A —
    # the SECOND killer objection ("is DCF just 1/PE in disguise?"). Same frame as placebo_random
    # (same n_d per date measured off the same dcf_at calls, same pool, same stage, same fail-safe),
    # but the victims are the n_d names with the HIGHEST PE (lowest 1/PE from the selector's own
    # pe_piv at src_q — the simplest available value proxy) instead of random/DCF. Names with no PE
    # are a neutral pass-through (never dropped), mirroring exclude_rich's NOT_COMPUTED convention.
    # If variant A's edge is reproduced here, DCF adds nothing over a trivial PE rule.
    DCF_MODE = os.environ.get("BASKET_DCF_MODE", "").lower()
    DCF_W    = float(os.environ.get("BASKET_DCF_W", "0.25"))
    DCF_PLACEBO_SEED = int(os.environ.get("BASKET_DCF_PLACEBO_SEED", "0"))
    dcf_at = None
    if DCF_MODE:
        if SELECT_MODE != "yieldcombo":
            raise ValueError(f"BASKET_DCF_MODE={DCF_MODE} only defined for BASKET_SELECT=yieldcombo")
        if DCF_MODE not in ("exclude_rich", "tiebreak", "placebo_random", "placebo_pe"):
            raise ValueError(f"BASKET_DCF_MODE={DCF_MODE} unknown "
                             "(exclude_rich|tiebreak|placebo_random|placebo_pe)")
        import dcf_valuation as _dcfv
        _fin = _dcfv._load_financials()
        _rebal_in = ",".join(f"DATE '{pd.Timestamp(x).date()}'" for x in rebal_dates)
        _px = bq(f"""SELECT t.ticker, t.time, t.Price FROM tav2_bq.ticker t
WHERE t.time IN ({_rebal_in}) AND t.Price IS NOT NULL""")
        _px["time"] = pd.to_datetime(_px["time"])
        _px_map = {(r.ticker, r.time): float(r.Price) for r in _px.itertuples()}
        _dcf_memo = {}
        _dcf_stat = {"CHEAP": 0, "RICH": 0, "NOT_COMPUTED": 0}
        _placebo_log = []   # placebo_random: per-date (n_pool, n_dropped) — audit trail proving the
                            # placebo dropped exactly as many names as exclude_rich would have.
        def dcf_at(tk, d):
            """-> (status, mos, robust). status='NOT_COMPUTED' when FV or price unavailable.
            Mirrors trading_bot/strategies.py::_dcf_check_for_order, incl. its fail-safe: any
            error -> NOT_COMPUTED (neutral), never raise."""
            key = (tk, pd.Timestamp(d))
            if key in _dcf_memo:
                return _dcf_memo[key]
            px = _px_map.get(key)
            out = ("NOT_COMPUTED", np.nan, False)
            if px and px > 0:
                try:
                    res = _dcfv.fair_value(tk, pd.Timestamp(d), price=px, fin=_fin)
                    if res.get("ok"):
                        mos = res.get("margin_of_safety")
                        if mos is not None and pd.notna(mos):
                            # the 4 box keys ONLY — `sensitivity` also carries a bare `base_fv_ps`
                            # float; folding it in would add a 5th point production never counts.
                            _sens = res.get("sensitivity") or {}
                            signs = []
                            for _k in ("r-1%", "r+1%", "g-2%", "g+2%"):
                                _f = (_sens.get(_k) or {}).get("fv")
                                if _f and _f > 0:
                                    signs.append(((_f - px) / _f) > 0)
                            robust = bool(signs) and all(s == (mos > 0) for s in signs)
                            out = (("CHEAP" if mos > 0 else "RICH"), float(mos), robust)
                except Exception:
                    out = ("NOT_COMPUTED", np.nan, False)
            _dcf_memo[key] = out
            _dcf_stat[out[0]] += 1
            return out
        print(f"  [DCF overlay] mode={DCF_MODE}"
              + (f" w={DCF_W}" if DCF_MODE == "tiebreak" else "")
              + (f" seed={DCF_PLACEBO_SEED}" if DCF_MODE == "placebo_random" else "")
              + "; fair_value(asof=rebal date) live; NOT_COMPUTED = neutral pass-through")
    cfo_piv = None; pe_piv = None; pcf_piv = None; mom_piv = None; rsi_piv = None; pb_piv = None
    if SELECT_MODE == "yieldcombo":
        # custom30V: liquidity is GATE only; rank PURELY by combined value-yield rank(1/PE)+rank(1/PCF)
        pe_piv = _yield_piv("PE"); pcf_piv = _yield_piv("PCF")
    elif SELECT_MODE == "eyfin":
        # STEP 1 of the v4final chain (job Taylor_20260714_140127): yieldcombo, except the three
        # FINANCIAL routes drop the 1/PCF leg entirely — a bank's "cash flow" is deposit/loan
        # balance-sheet flow, not a product of core operations, so 1/PCF is not the same economic
        # quantity there (the user's premise, established 2026-07-14).
        # SCALE, deliberately: a financial's score is 2*rank(1/PE), NOT a bare rank(1/PE). The cut is
        # CROSS-route, so a 1-leg score on [0,1] against a 2-leg score on [0,2] would not "remove a
        # wrong metric" — it would silently near-eliminate financials from the top-30, and the delta
        # would measure a sector underweight, not the metric fix. That is EXACTLY the class of bug
        # (absolute-vs-percentile scale mismatch across a cross-route cut) that killed v3route this
        # morning; doubling the ey leg keeps the range identical and changes ONLY which metric is read.
        pe_piv = _yield_piv("PE"); pcf_piv = _yield_piv("PCF")
    elif SELECT_MODE == "eyonly":
        # STEP 2 (v4final): ONE metric for every name, pool-wide — score = rank_pct(1/PE).
        # Percentiles are normalised by construction, so there is no cross-group distribution to
        # match and the whole scale-mismatch failure class cannot arise. 1/PE is the system's
        # strongest, route-neutral factor (KB: IC +0.125, "Value dominates ALL regimes"; BANK route
        # IC +0.181 t=3.79 — stronger than pb_z or 1/PCF inside the bank route itself).
        pe_piv = _yield_piv("PE")
    elif SELECT_MODE == "eyrisk":
        # RISK-ADJUSTED earnings yield (job Taylor_20260715_025346): the "middle ground" the user
        # asked for between raw pool-wide 1/PE (structurally favours banks whose PE is low because
        # future NPL risk is not yet in E) and full sector-neutral ranking (REFUTED: strips the
        # low-PE-sector tilt that earns return — composite-v2 selector −7..−15pp, v3route3 −2.38pp).
        # Instead of neutralising the SECTOR, discount the EARNINGS by a continuous quality floor:
        #   ey_adj = (1/PE) × m,  m = clip(0.5 + 5·ROE_Min5Y, 0.5, 1.0)
        # i.e. a name whose worst-5Y ROE is ≤0 gets HALF credit for its earnings, full credit from
        # ROE_Min5Y ≥ 0.10, linear between. Missing ROE_Min5Y → m = 1.0 (fail-open: absence of a
        # track record is not evidence of risk; penalising absence is a different, unmeasured rule).
        # PRE-REGISTERED, NO GRID: the (0.5, 0.10) knobs are fixed a priori and will NOT be swept —
        # if neither scope shows an effect outside noise vs the A2 anchor, the verdict is NO-GO.
        # BASKET_RISK_SCOPE: "all" (default) = penalty on every name; "fin" = penalty only on
        # BANK/INSURANCE/SECURITIES (the user's NPL thesis is financial-specific).
        pe_piv = _yield_piv("PE")
    elif SELECT_MODE == "pbcombo":
        # BOTTOM-DEPLOY vehicle (#18, Taylor 2026-06-27): 1/PB dominates at deep-cheap bottoms (crisis-IC
        # +0.222 vs −0.019 full-period) → weight 0.67*rank(1/PB)+0.23*rank(1/PCF)+0.10*rank(1/PE).
        pb_piv = _yield_piv("PB"); pcf_piv = _yield_piv("PCF"); pe_piv = _yield_piv("PE")
    elif SELECT_MODE == "petop":
        pe_piv = _yield_piv("PE")
    elif SELECT_MODE == "pemom":
        pe_piv = _yield_piv("PE"); mom_piv = _mom_piv()
    if RSI_W > 0 and SELECT_MODE in ("petop", "pemom"): rsi_piv = _rsi_piv()
    elif CFO_BLEND > 0:
        cfo_piv = _yield_piv("PE" if _YM == "pe" else "PCF")
    # ---- AUDIT-ONLY selection modes (env BASKET_SELECT=v3comp|ps3; prod never sets these) ----
    # v3comp = the live 8L valuation-v3 axis as the basket ranker (route-neutral sector-weighted
    #   coverage-aware ey+cfy+ps + golden-cell floor). ps3 = simple equal rank(1/PE)+rank(1/PCF)+rank(1/PS)
    #   (isolates the +1/PS contribution vs yieldcombo). Reuses data/value_panel_2014.csv for PIT inputs.
    # v3route (job Taylor_20260714_112932) = v3latest + the FINANCIAL value axis rating_8l actually uses.
    #   Motivation (user, 2026-07-14): yieldcombo ranks a bank and a manufacturer on the SAME 1/PCF. A
    #   bank's PCF reflects deposit/loan flows, not cash generated by core operations -> not comparable.
    #   rating_8l already solved this: BANK/INSURANCE/SECURITIES (and REALESTATE) KEEP value_score_v2
    #   (= 0.65*earnings-yield-percentile-WITHIN-route + 0.35*pb_z-relative + cfo confirm + track bonus),
    #   which carries NO cfy/PCF main lens and preserves BANK's real pb_z +0.136 signal. v3latest gave
    #   financials the COMPOUNDER composite (cfy=1/PCF weighted .30) -> ranked within-route, but on the
    #   wrong metric. v3route reuses the v2 formula verbatim for those routes; every other route is
    #   BYTE-IDENTICAL to v3latest, so this is a clean single-axis ablation.
    # v3route2 / v3route3 (job Taylor_20260714_121717) = v3route + the SCALE fix quant-skeptic's
    #   REFUTED verdict demanded. v3route's flaw: value_score_v2 mixes an ABSOLUTE pb_z term
    #   (0.35*(0.5-pb_z/2), which only reaches 1.0 at pb_z<=-1) into a score that is then cut against
    #   non-financial scores built from PURE WITHIN-ROUTE PERCENTILES (where some name always reaches
    #   1.0). rating_8l only ever compares v2 scores bank-vs-bank, so the absolute scale never
    #   mattered there; a cross-route top-30 cut makes it decisive.
    #   v3route2 = rank-percentile v2 WITHIN each financial route before the cross-route cut. This is
    #     the fix as specified, but MEASURED (selfcheck [7]) it over-corrects the other way: a single
    #     percentile is UNIFORM (P90 ~ .96) while the non-financial score is a weighted mean of three
    #     percentiles and therefore BELL-shaped (P90 ~ .87). Financials go from -0.107 too low to
    #     +0.064 too high. Same class of bug, opposite sign.
    #   v3route3 = quantile-MATCH: map each financial's within-route percentile through the
    #     non-financial score distribution of the same quarter, so a financial at within-route rank q
    #     scores exactly what a non-financial at rank q scores. This is the only one of the three that
    #     is actually scale-comparable, and it is the reference arm.
    #   All three share identical financial ORDERING (monotone transforms of one v2 score) and leave
    #   non-financials byte-identical to v3latest -> the 3-arm spread isolates PURELY how much
    #   financial weight the cut grants, which is exactly the thing under suspicion.
    _V3_MODES    = ("v3comp", "ps3", "v3gated", "v3latest", "v3route", "v3route2", "v3route3")
    _V3L_MODES   = ("v3latest", "v3route", "v3route2", "v3route3")   # "latest rating_8l v3" cfo/golden
    _ROUTE_MODES = ("v3route", "v3route2", "v3route3")               # financial routes -> value_score_v2
    _v3q = None
    if SELECT_MODE in _V3_MODES:
        _p = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "value_panel_2014.csv"),
                         parse_dates=["time"])
        _p["qstart"] = _p["time"].dt.to_period("Q").dt.start_time
        _p = _p.sort_values("time").groupby(["ticker", "qstart"]).last().reset_index()   # last obs per quarter
        _cols=["qstart","ticker","PE","PCF","PS","pb_z","PB","route","ICB_Code","ROE_Min3Y",
               "CF_OA_P0","CF_OA_P1","CF_OA_P2","CF_OA_P3","CF_OA_3Y",
               "ROE_Min5Y","CF_OA_5Y"]   # v3route* only: v2 track-record bonus inputs (proven5y, ROE floor)
        _v3q = _p[[c for c in _cols if c in _p.columns]]
    # v3comp = PS broad; v3gated = PS retail-only; v3latest = THIS-MORNING rating_8l v3 (CYCLICAL ps->0,
    # cfy=cfo_normy for non-cyclical, golden floor gated by CF_OA_3Y>0).
    VR_W_FULL   = {"COMPOUNDER": (.45,.30,.25), "CYCLICAL": (.35,.50,.15), "RETAIL": (.35,.20,.45)}
    VR_W_GATED  = {"RETAIL": (.35,.20,.45), "CYCLICAL": (.50,.50,.00), "_default": (.55,.45,.00)}
    VR_W_LATEST = {"COMPOUNDER": (.45,.30,.25), "CYCLICAL": (.40,.60,.00), "RETAIL": (.35,.20,.45)}
    VR_W = {"v3gated":VR_W_GATED,"v3latest":VR_W_LATEST,"v3route":VR_W_LATEST,
            "v3route2":VR_W_LATEST,"v3route3":VR_W_LATEST}.get(SELECT_MODE, VR_W_FULL)
    _VRDEF = VR_W.get("_default", VR_W.get("COMPOUNDER"))
    # routes rating_8l KEEPS on value_score_v2 (never the ey/cfy/ps composite). rating_8l's rule is
    # "financials/RE/POWER KEEP v2"; v3route deliberately moves ONLY the three FINANCIAL routes, so the
    # v3latest->v3route delta isolates exactly the metric the user challenged (bank ranked on 1/PCF).
    # REALESTATE/POWER stay on the v3latest path (unchanged) -> separate ablation if ever wanted.
    _V2_ROUTES = {"BANK", "INSURANCE", "SECURITIES"}
    # rating_8l value_score_v2 knobs. Defaults ARE rating_8l's live values -> unset env == verbatim.
    # AUDIT-ONLY overrides (job Taylor_20260714_121717) exist because these were tuned inside
    # rating_8l's WITHIN-route problem; nothing says they survive a CROSS-route cut. Sweep = §5
    # sensitivity-plateau evidence, not a tuning opportunity.
    W_ABS_V2  = float(os.environ.get("V3R_W_ABS", 0.65))   # abs (ey-within-route) weight; 1-w -> pb_z
    CFO_UP    = float(os.environ.get("V3R_CFO_UP", 0.05))  # cfo-confirm nudge (pool pct >= .5)
    CFO_DN    = float(os.environ.get("V3R_CFO_DN", -0.08)) # cfo-contradict nudge (pool pct < .2)
    TRK_CF    = float(os.environ.get("V3R_TRK_CF", 0.03))  # track bonus: CF_OA_5Y > 0
    TRK_ROE   = float(os.environ.get("V3R_TRK_ROE", 0.03)) # track bonus: ROE_Min5Y > 0.10
    # ABSTAIN isolation: v3route* drops a financial with NO pb_z entirely (rating_8l's own rule).
    # In 2014-19 that is ~20% of financial exclusions -> a DATA-COVERAGE effect masquerading as a
    # valuation judgement. =1 imputes the route-median pb_z instead, so the name stays and is judged
    # on its real ey. The v3route3-vs-this delta IS the abstain contribution.
    ABST_IMP  = os.environ.get("V3R_ABSTAIN_IMPUTE", "") == "1"
    def _score_v3(pool, src_q):
        toks = [t for t,_ in pool]
        d = _v3q[(_v3q.qstart == src_q) & (_v3q.ticker.isin(toks))].set_index("ticker")
        d = d.reindex(toks)                                   # align to pool order; missing -> NaN row
        ey  = np.where(d.PE  > 0, 1.0/d.PE,  np.nan)
        cfy = np.where(d.PCF > 0, 1.0/d.PCF, np.nan)
        ps  = np.where(d.PS  > 0, 1.0/d.PS,  np.nan)
        if SELECT_MODE in _V3L_MODES and "CF_OA_3Y" in d.columns:   # cfo_normy non-cyclical, raw cyclical
            _ttm = d[["CF_OA_P0","CF_OA_P1","CF_OA_P2","CF_OA_P3"]].sum(axis=1, min_count=1)
            _n3 = d["CF_OA_3Y"]/3.0
            _cfynorm = np.where((d.PCF>0)&(_ttm>0)&(_n3>0), (1.0/d.PCF)*np.clip(_n3/_ttm,0.3,3.0), np.nan)
            cfy = np.where((d.route=="CYCLICAL").values, cfy, _cfynorm)
        F = pd.DataFrame({"ey":ey,"cfy":cfy,"ps":ps}, index=toks)
        if SELECT_MODE == "ps3":                               # equal 3-yield, pool-wide percentile
            s = sum(F[c].rank(pct=True).fillna(0.5) for c in ["ey","cfy","ps"])
            return {t: float(s[t]) for t in toks}
        # v3comp: route-neutral percentile (fallback pool-wide), sector weights, coverage-aware, golden floor
        icb = d.ICB_Code
        vr = np.where((d.route == "COMPOUNDER") & icb.apply(lambda c: pd.notna(c) and ((3500<=c<3800) or (5300<=c<5400))),
                      "RETAIL", d.route.fillna("COMPOUNDER"))
        vr = pd.Series(vr, index=toks)
        pct = {}
        for c in ["ey","cfy","ps"]:
            rr = F[c].groupby(vr).transform(lambda g: g.rank(pct=True) if g.notna().sum()>=5 else pd.Series(np.nan,index=g.index))
            gg = F[c].rank(pct=True); m = rr.isna() & F[c].notna(); rr = rr.copy(); rr[m] = gg[m]
            pct[c] = rr
        Wm = np.array([VR_W.get(v, _VRDEF) for v in vr])     # n x 3
        P = np.vstack([pct["ey"].values, pct["cfy"].values, pct["ps"].values]).T   # n x 3
        pres = ~np.isnan(P); num = np.nansum(np.where(pres,P*Wm,0),1); den = np.nansum(np.where(pres,Wm,0),1)
        sc = np.where(den>0, num/den, np.nan)
        golden = (d.pb_z.values <= -1); bookok = ~(d.ROE_Min3Y.values < 0)
        if SELECT_MODE in _V3L_MODES and "CF_OA_3Y" in d.columns:   # golden floor also needs CF_OA_3Y>0
            bookok = bookok & (d.CF_OA_3Y.values > 0)
        if SELECT_MODE in _ROUTE_MODES:
            # FINANCIAL routes -> rating_8l value_score_v2, verbatim (rating_8l.py "value_score_v2"):
            #   0.65*ey-percentile-WITHIN-route + 0.35*(0.5 - pb_z/2) + cfo confirm/contradict + track bonus.
            # NO cfy/PCF main lens: 1/PCF enters only as the same small ±0.05/-0.08 confirm nudge rating_8l
            # applies, ranked POOL-WIDE (not per-route) exactly as rating_8l does it.
            _fin = vr.isin(_V2_ROUTES).values
            if _fin.any():
                _pbz = d.pb_z.values
                if ABST_IMP:      # impute route-median pb_z so a no-pb_z financial competes, not abstains
                    _pbs = pd.Series(np.where(_fin, _pbz, np.nan), index=toks)
                    _med = _pbs.groupby(vr).transform("median")
                    _pbz = np.where(np.isnan(_pbz) & _fin & _med.notna().values, _med.values, _pbz)
                _rel = np.clip(0.5 - _pbz / 2.0, 0, 1)                             # pb_z=-1 -> 1, 0 -> .5, +1 -> 0
                _cfo_pct = pd.Series(cfy, index=toks).rank(pct=True)               # pool-wide, as rating_8l
                _adj = np.where(_cfo_pct.notna() & (_cfo_pct >= 0.5), CFO_UP,
                        np.where(_cfo_pct.notna() & (_cfo_pct < 0.2), CFO_DN, 0.0))
                _track = (np.where(pd.Series(d.get("CF_OA_5Y", np.nan), index=toks).fillna(-9).values > 0, TRK_CF, 0.0)
                          + np.where(pd.Series(d.get("ROE_Min5Y", np.nan), index=toks).fillna(-9).values > 0.10, TRK_ROE, 0.0))
                _ey_route = pct["ey"].values                                       # already within-route (v2's design)
                _v2 = np.clip((1 - W_ABS_V2) * _rel + W_ABS_V2 * np.nan_to_num(_ey_route, nan=0.5)
                              + _adj + _track, 0, 1)
                _v2 = np.where(np.isnan(_pbz), np.nan, _v2)                        # no pb_z -> abstain, not a fake 0.5
                if SELECT_MODE in ("v3route2", "v3route3"):
                    # SCALE FIX step 1 (both arms): v2 -> within-route percentile, so financials are
                    # ranked on the same *kind* of quantity the non-financial score is built from.
                    # Same convention as the ey/cfy/ps pct block above: rank WITHIN route when the
                    # route has >=5 scored names, else fall back to the whole financial pool.
                    _s2 = pd.Series(np.where(_fin, _v2, np.nan), index=toks)
                    _rk = _s2.groupby(vr).transform(
                        lambda g: g.rank(pct=True) if g.notna().sum() >= 5 else pd.Series(np.nan, index=g.index))
                    _pool_rk = _s2.rank(pct=True)                                   # financial-pool-wide fallback
                    _m = _rk.isna() & _s2.notna(); _rk = _rk.copy(); _rk[_m] = _pool_rk[_m]
                    _v2 = _rk.values                                                # NaN (abstain) stays NaN
                if SELECT_MODE == "v3route3":
                    # step 2 (v3route3 only): a bare percentile is UNIFORM; the non-financial score is
                    # a weighted mean of three percentiles and is BELL-shaped. Equal percentiles are
                    # therefore still NOT equal scores. Push each financial's percentile through the
                    # quarter's own non-financial score distribution -> a financial at within-route
                    # rank q gets exactly the score a non-financial at rank q has. Order-preserving.
                    _nf_sc = sc[(~_fin) & ~np.isnan(sc)]
                    if _nf_sc.size >= 5:
                        _v2 = np.where(np.isnan(_v2), np.nan,
                                       np.quantile(_nf_sc, np.clip(np.nan_to_num(_v2, nan=0.5), 0, 1)))
                sc = np.where(_fin, _v2, sc)
        sc = sc + 0.10*np.where(golden & pd.notna(d.pb_z.values), 1.0, 0.0)
        sc = np.where(d.PB.values < 0, 0.0, sc)
        sc = np.where(golden & bookok, np.maximum(np.nan_to_num(sc, nan=0.0), 1.0), sc)   # golden book-OK floor (=> selected first)
        return {t: (float(v) if pd.notna(v) else -1.0) for t, v in zip(toks, sc)}
    # ---- AUDIT-ONLY count-matched PLACEBO (job Taylor_20260714_121717) ----
    # BASKET_PLACEBO_FIN = "<seed>:<counts_csv>" (default "" = OFF, byte-identical).
    # The v3route* family's only measurable effect on the cut is that it holds FEWER financial names
    # (9.27/30 -> ~5-6.5/30). This asks the obvious question: does WHICH financials it keeps matter at
    # all, or would ANY equally-sized financial underweight score the same? Keeps the baseline
    # selector's ranking, but forces exactly the SAME NUMBER of financial names the real arm chose
    # that quarter, picking WHICH ones at RANDOM from the eligible pool; non-financial slots are
    # filled by the baseline's own top names. Same pattern as the DCF Pha-4 placebo.
    PLACEBO = os.environ.get("BASKET_PLACEBO_FIN", "")
    _pl_n, _pl_route, _pl_seed = {}, {}, 0
    if PLACEBO:
        _pl_seed_s, _pl_csv = PLACEBO.split(":", 1)
        _pl_seed = int(_pl_seed_s)
        _pc = pd.read_csv(_pl_csv, parse_dates=["rebal_date"])
        _pl_n = {pd.Timestamp(r.rebal_date): int(r.n_fin) for r in _pc.itertuples()}
        _pp = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data",
                                       "value_panel_2014.csv"), parse_dates=["time"])
        _pp["qstart"] = _pp["time"].dt.to_period("Q").dt.start_time
        _pp = _pp.sort_values("time").groupby(["ticker", "qstart"]).last().reset_index()
        _pl_route = {(r.ticker, pd.Timestamp(r.qstart)): r.route for r in _pp.itertuples()}   # PIT route
        print(f"  [placebo] seed={_pl_seed}, count-matched to {len(_pl_n)} rebals from {os.path.basename(_pl_csv)}")
    _PL_FIN = {"BANK", "INSURANCE", "SECURITIES"}

    def _placebo_reorder(gated, d, src_q, top_n):
        """Force exactly n_fin(d) financial names into the top-n, chosen at RANDOM."""
        tgt = _pl_n.get(pd.Timestamp(d))
        if tgt is None: return gated
        fin = [x for x in gated if _pl_route.get((x[0], pd.Timestamp(src_q))) in _PL_FIN]
        non = [x for x in gated if _pl_route.get((x[0], pd.Timestamp(src_q))) not in _PL_FIN]
        k = min(tgt, len(fin))
        rng = np.random.default_rng(abs(hash((_pl_seed, pd.Timestamp(d).value))) % (2**32))
        keep = [fin[i] for i in sorted(rng.choice(len(fin), size=k, replace=False))] if k > 0 else []
        head = keep + non[: max(0, top_n - len(keep))]
        rest = [x for x in gated if x not in head]
        return head + rest

    # ---- AUDIT-ONLY dynamic sector cap (job Taylor_20260714_095953, sector-cap research) ----
    # BASKET_SECCAP_MODE: "" (default, OFF -> byte-identical: sectorcap keeps the fixed `sector_cap`)
    #   | "mktcap"   (variant B: cap sector_code at its PIT market-cap weight in ticker_prune)
    #   | "mktx<f>"  (variant B': same x <f>, e.g. mktx1.5 = allow a 1.5x value tilt over market).
    # Only meaningful with weight_scheme='sectorcap'. The cap is recomputed at EACH rebal date from
    # ONLY that day's data (mcap = raw COALESCE(Price,Close) x as-of OShares — identical definition
    # to the basket's own WEIGHT leg `mcapw`, so basket weight and market weight stay on one scale;
    # price basis split by role 2026-08-02, see module header) -> no look-ahead.
    SECCAP_MODE = os.environ.get("BASKET_SECCAP_MODE", "").lower()
    seccap_by_date = {}
    if SECCAP_MODE:
        if weight_scheme != "sectorcap":
            raise ValueError(f"BASKET_SECCAP_MODE={SECCAP_MODE} only defined for weight_scheme=sectorcap")
        if SECCAP_MODE == "mktcap":
            _mult = 1.0
        elif SECCAP_MODE.startswith("mktx"):
            _mult = float(SECCAP_MODE[4:])
        else:
            raise ValueError(f"BASKET_SECCAP_MODE={SECCAP_MODE} unknown (mktcap|mktx<f>)")
        _rin = ",".join(f"DATE '{pd.Timestamp(x).date()}'" for x in rebal_dates)
        _mk = bq(f"""WITH fin AS (
  SELECT f.ticker, f.time AS ftime, f.OShares,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS nft
  FROM tav2_bq.ticker_financial AS f WHERE f.OShares IS NOT NULL)
SELECT t.time, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS sec,
       SUM({pxw_sql()}*fin.OShares) AS mcap
FROM tav2_bq.ticker AS t
JOIN fin ON fin.ticker=t.ticker AND t.time>=fin.ftime AND (fin.nft IS NULL OR t.time<fin.nft)
WHERE t.time IN ({_rin}) AND t.ICB_Code IS NOT NULL AND t.Close IS NOT NULL
  AND {universe_pred()}
GROUP BY t.time, sec""")
        _mk["time"] = pd.to_datetime(_mk["time"])
        for _d, _g in _mk.groupby("time"):
            _tot = float(_g["mcap"].sum())
            if _tot <= 0: continue
            _w = float(_g.loc[_g["sec"] == sector_code, "mcap"].sum()) / _tot
            seccap_by_date[pd.Timestamp(_d)] = min(1.0, _w * _mult)
        if seccap_by_date:
            _vv = pd.Series(seccap_by_date)
            print(f"  [sector-cap dyn] mode={SECCAP_MODE} sec={sector_code}: PIT market weight x{_mult} "
                  f"-> cap over {len(_vv)} rebals: min {_vv.min():.3f} / med {_vv.median():.3f} / max {_vv.max():.3f}")
    # ---- PIT route map for the v4final family (job Taylor_20260714_140127) ----
    # Needed by SELECT_MODE='eyfin' (which routes get the PCF leg dropped) and weight_scheme='fincap'
    # (which names count toward the financial cap). Source = data/value_panel_2014.csv `route`, the
    # same column rating_8l's router produces — reused rather than re-derived so the route definition
    # cannot drift between the rating engine and the basket.
    # PIT: route is looked up at the SELECTION quarter (src_q), never "latest" — a name reclassified
    # later must not retro-change an old rebal. Fallback = the name's LAST route at//before src_q,
    # then its earliest known route; unknown -> non-financial (fail-open on the CAP = the cap can
    # only ever bind on names we positively know are financial; a missing route never fabricates one).
    FIN_CAP = float(os.environ.get("BASKET_FIN_CAP", "0.30"))
    _FIN_ROUTES = {"BANK", "INSURANCE", "SECURITIES"}
    route_by_tq, route_hist = {}, {}
    roe_by_tq, roe_hist = {}, {}
    RISK_SCOPE = os.environ.get("BASKET_RISK_SCOPE", "all").lower()   # eyrisk only: "all" | "fin"
    if SELECT_MODE in ("eyfin", "eyrisk") or weight_scheme == "fincap":
        _rp0 = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data",
                                        "value_panel_2014.csv"), parse_dates=["time"],
                           usecols=["ticker", "time", "route", "ROE_Min5Y"])
        _rp0["qstart"] = _rp0["time"].dt.to_period("Q").dt.start_time
        if SELECT_MODE == "eyrisk":
            if RISK_SCOPE not in ("all", "fin"):
                raise ValueError(f"BASKET_RISK_SCOPE={RISK_SCOPE} invalid (want 'all' or 'fin')")
            # PIT ROE_Min5Y map, same (ticker, qstart)->last convention as the route map below so
            # the two lookups cannot drift. Unlike route_asof there is NO earliest-known fallback:
            # a floor first published AFTER the selection quarter must not leak backward — absent
            # history at src_q simply means m=1.0 (fail-open).
            _rr = _rp0.dropna(subset=["ROE_Min5Y"]).sort_values("time")
            _rr = _rr.groupby(["ticker", "qstart"])["ROE_Min5Y"].last().reset_index()
            roe_by_tq = {(r.ticker, pd.Timestamp(r.qstart)): float(r.ROE_Min5Y) for r in _rr.itertuples()}
            roe_hist = {tk: (list(g["qstart"]), list(g["ROE_Min5Y"])) for tk, g in _rr.groupby("ticker")}
            print(f"  [eyrisk] scope={RISK_SCOPE}: ey × clip(0.5 + 5·ROE_Min5Y, 0.5, 1.0), "
                  f"missing→1.0 ({len(roe_hist)} tickers with a PIT ROE_Min5Y history)")
        _rp = _rp0.dropna(subset=["route"]).sort_values("time")
        _rl = _rp.groupby(["ticker", "qstart"])["route"].last().reset_index()
        route_by_tq = {(r.ticker, pd.Timestamp(r.qstart)): r.route for r in _rl.itertuples()}
        route_hist = {tk: (list(g["qstart"]), list(g["route"])) for tk, g in _rl.groupby("ticker")}
        if weight_scheme == "fincap":
            print(f"  [fincap] cap BANK+INSURANCE+SECURITIES total weight at {FIN_CAP:.2f}, then name_cap "
                  f"{name_cap:.2f} ({len(route_hist)} tickers routed, PIT as-of selection quarter)")

    # ---- AUDIT-ONLY DY marginal-band tie-break, arm A4 (job Taylor_20260714_152605) ----
    # BASKET_DY_TIEBREAK: "" (default, OFF -> byte-identical) | "<lo>:<hi>" (1-indexed, inclusive)
    #   e.g. "20:45" = the pre-registered marginal band (§12.4).
    # Role, deliberately narrow: DY is a DOWNSIDE FLOOR, not a ranking axis (§12.4 measured a 6M
    # downside effect of +2.34pp t=2.37 that SURVIVES de-confounding for cheapness, with NO return
    # edge, t=0.17). A floor belongs where it can break a tie, not in a linear score — folding
    # rank(DY) into `score` would make it a return-predictor by construction, which is the exact
    # claim the data does NOT support. So: inside the band only, DY-bearing names permute among the
    # slots THEY ALREADY OCCUPY; ranks outside the band are untouched.
    # FAIL-OPEN (DY>0 covers only ~70.4% of obs): a name without a positive DY does not move AT ALL
    # — it keeps its exact ey slot. Sorting the whole band by DY would push those names to the back,
    # i.e. PENALISE absent data; that is a different (and unmeasured) rule.
    # PIT: Dividend_Min3Y as-of Release_Date (never `time`, which is the quarter it describes, not
    # the day it became public); denominator = UNADJUSTED Price at d, the price a real yield is
    # quoted against. Identical definition to dy_floor_test.py, reused so the rule cannot drift from
    # the evidence that justified it.
    DY_BAND = os.environ.get("BASKET_DY_TIEBREAK", "")
    dy_at = None
    if DY_BAND:
        if SELECT_MODE != "eyonly":
            raise ValueError(f"BASKET_DY_TIEBREAK={DY_BAND} only defined for BASKET_SELECT=eyonly "
                             f"(arm A4 is pre-registered on the A2 base; got {SELECT_MODE})")
        try:
            _dy_lo, _dy_hi = (int(x) for x in DY_BAND.split(":"))
        except ValueError:
            raise ValueError(f"BASKET_DY_TIEBREAK={DY_BAND} malformed (want '<lo>:<hi>', e.g. '20:45')")
        if not (1 <= _dy_lo < _dy_hi):
            raise ValueError(f"BASKET_DY_TIEBREAK={DY_BAND}: need 1 <= lo < hi")
        _dv = bq(f"""SELECT f.ticker, f.time, f.Release_Date, f.Dividend_Min3Y
FROM tav2_bq.ticker_financial f WHERE f.time <= DATE '{end_date}' AND f.Dividend_Min3Y IS NOT NULL""")
        # Release_Date NULL -> time+45d: the same conservative public-availability fallback
        # dy_floor_test.py used. It can only ever DELAY a fact, never leak one early.
        _dv["eff"] = (pd.to_datetime(_dv["Release_Date"])
                      .fillna(pd.to_datetime(_dv["time"]) + pd.Timedelta(days=45)))
        _dv = _dv.sort_values("eff")
        _dv_hist = {tk: (list(g["eff"]), list(g["Dividend_Min3Y"])) for tk, g in _dv.groupby("ticker")}
        _dy_rebal_in = ",".join(f"DATE '{pd.Timestamp(x).date()}'" for x in rebal_dates)
        _dy_px = bq(f"""SELECT t.ticker, t.time, t.Price FROM tav2_bq.ticker t
WHERE t.time IN ({_dy_rebal_in}) AND t.Price IS NOT NULL""")
        _dy_px["time"] = pd.to_datetime(_dy_px["time"])
        _dy_px_map = {(r.ticker, r.time): float(r.Price) for r in _dy_px.itertuples()}
        _dy_memo = {}
        _dy_stat = {"have": 0, "absent": 0}

        def dy_at(tk, d):
            """-> float DY>0, or None when DY is absent/zero (caller must then NOT move the name)."""
            key = (tk, pd.Timestamp(d))
            if key in _dy_memo:
                return _dy_memo[key]
            out = None
            e = _dv_hist.get(tk)
            px = _dy_px_map.get(key)
            if e and px and px > 0:
                i = bisect.bisect_right(e[0], pd.Timestamp(d)) - 1
                if i >= 0:
                    _d3 = float(e[1][i])
                    if _d3 > 0:
                        out = _d3 / px
            _dy_memo[key] = out
            _dy_stat["have" if out is not None else "absent"] += 1
            return out

        print(f"  [DY tie-break] band = ey ranks {_dy_lo}-{_dy_hi} (1-indexed, inclusive); "
              f"DY = Dividend_Min3Y(as-of Release_Date)/Price(d); fail-open: no DY -> name does not "
              f"move; ranks outside the band untouched; NOT added to the score")

    def _dy_reorder(gated, d, lo, hi):
        """Permute the DY-bearing names inside gated[lo-1:hi] by DY desc, into the slots those names
        already occupy. Names without a positive DY keep their exact ey slot (fail-open). Returns a
        new list; ranks outside [lo-1:hi] are copied through untouched."""
        band = gated[lo - 1:hi]
        if len(band) < 2:
            return gated
        slots = [i for i, (tk, _) in enumerate(band) if dy_at(tk, d) is not None]
        if len(slots) < 2:            # 0 or 1 DY-bearing name -> nothing to re-order
            return gated
        ranked = sorted((band[i] for i in slots), key=lambda tr: dy_at(tr[0], d), reverse=True)
        out = list(band)
        for _slot, _item in zip(slots, ranked):
            out[_slot] = _item
        return gated[:lo - 1] + out + gated[hi:]

    def route_asof(tk, q):
        """PIT route of `tk` as of selection quarter `q`; None when never routed."""
        r = route_by_tq.get((tk, pd.Timestamp(q)))
        if r is not None: return r
        e = route_hist.get(tk)
        if not e: return None
        i = bisect.bisect_right(e[0], pd.Timestamp(q)) - 1
        return e[1][i] if i >= 0 else e[1][0]

    def is_fin(tk, q):
        return route_asof(tk, q) in _FIN_ROUTES

    def roemin_asof(tk, q):
        """PIT ROE_Min5Y of `tk` as of selection quarter `q`; None when no history at//before q."""
        r = roe_by_tq.get((tk, pd.Timestamp(q)))
        if r is not None: return r
        e = roe_hist.get(tk)
        if not e: return None
        i = bisect.bisect_right(e[0], pd.Timestamp(q)) - 1
        return e[1][i] if i >= 0 else None   # deliberately NO earliest-known fallback (look-ahead)

    def eyrisk_mult(tk, q):
        if RISK_SCOPE == "fin" and not is_fin(tk, q):
            return 1.0
        r = roemin_asof(tk, q)
        return 1.0 if r is None else float(np.clip(0.5 + 5.0 * r, 0.5, 1.0))

    members = {}  # rebal_date -> list[(ticker, qmult)]
    mem_rows = []
    fin_src_q = {}   # rebal_date -> selection quarter, so the daily weighting can route names PIT
    for d in rebal_dates:
        score = None   # selector score of the picked names, recorded into members_df for audit
        qd = pd.Timestamp(d).to_period("Q").start_time
        prior_qs = [qq for qq in liq_piv.index if qq < qd]
        src_q = max(prior_qs) if prior_qs else (qd if qd in liq_piv.index else None)  # 1st quarter: self-seed
        if src_q is None: continue
        liq_row = liq_piv.loc[src_q].dropna().sort_values(ascending=False)
        if LIQ_FLOOR > 0: liq_row = liq_row[liq_row >= LIQ_FLOOR]   # absolute tradability floor (custom30B)
        ranked = list(liq_row.index)
        # gated candidates in liquidity order (HARD SAFETY GATE: investment-grade as-of 8L rating)
        gated = []
        for tk in ranked:
            if tk in EXCLUDE: continue                                  # audit-only permanent exclude
            if _DYN_EVENTS and dyn_excluded_asof(tk, d): continue       # research fork: PIT dynamic gate
            rt = rating_asof(tk, d)
            if gate_rating is not None and not (pd.notna(rt) and rt <= gate_rating): continue
            if quality == "filter" and not (pd.notna(rt) and rt <= 3): continue
            if QFLOOR and not qfloor_asof(tk, d): continue              # Đ2 fundamentals floor (see 2b)
            gated.append((tk, rt))
        if SELECT_MODE == "yieldcombo" and gated:
            # custom30V: liquidity = GATE only (top-POOL tradability floor); rank PURELY by combined
            # value-yield = rank(1/PE)+rank(1/PCF). For BULL parking funded mainly by LAG idle cash.
            pool = gated[:CFO_POOL]
            if dcf_at is not None and DCF_MODE in ("exclude_rich", "placebo_random", "placebo_pe"):
                # variant A: drop only names the DCF calls RICH *and* robust (sign survives the
                # whole sensitivity box). CHEAP / non-robust-RICH / NOT_COMPUTED all stay.
                _keep = [(t, rt) for t, rt in pool
                         if not (lambda s: s[0] == "RICH" and s[2])(dcf_at(t, d))]
                if DCF_MODE == "exclude_rich":
                    if _keep: pool = _keep  # never empty the pool (fail-safe -> no-op that quarter)
                else:
                    # placebo: n_d = what exclude_rich ACTUALLY dropped at THIS date d (measured off
                    # the same dcf_at calls, not estimated). `_keep` empty means variant A no-ops via
                    # the fail-safe above -> effective drop 0 -> the placebo must also drop 0, else
                    # it would be a strictly harsher gate than the thing it is a control for.
                    _n_d = len(pool) - len(_keep)
                    if _keep and _n_d > 0:
                        if DCF_MODE == "placebo_random":
                            # seed = (SEED, date) so each rebal date draws INDEPENDENTLY, yet the
                            # whole 48-date path replays exactly from the same SEED. A single global
                            # RNG would make the draws path-dependent on rebal ordering and
                            # unreplayable per-date.
                            _rng = np.random.default_rng([DCF_PLACEBO_SEED,
                                                          pd.Timestamp(d).toordinal()])
                            _drop = set(_rng.choice(len(pool), size=_n_d, replace=False).tolist())
                            pool = [p for _i, p in enumerate(pool) if _i not in _drop]
                            _placebo_log.append({"date": pd.Timestamp(d), "n_pool": len(pool) + _n_d,
                                                 "n_dropped": _n_d})
                        else:  # placebo_pe — drop the n_d HIGHEST-PE names (lowest 1/PE at src_q,
                            # the very series the selector ranks on 20 lines below). NaN 1/PE =
                            # neutral pass-through, mirroring exclude_rich's NOT_COMPUTED rule; ties
                            # break on ticker so the whole path is deterministic (no seed needed).
                            _pe_row = (pe_piv.loc[src_q]
                                       if (pe_piv is not None and src_q in pe_piv.index) else None)
                            _cand = sorted(
                                [(t, float(_pe_row[t])) for t, _rt in pool
                                 if _pe_row is not None and pd.notna(_pe_row.get(t, np.nan))],
                                key=lambda ty: (ty[1], ty[0]))
                            _dropset = {t for t, _y in _cand[:_n_d]}
                            _keepset = {t for t, _rt in _keep}
                            _placebo_log.append({
                                "date": pd.Timestamp(d), "n_pool": len(pool),
                                "n_target": _n_d, "n_dropped": len(_dropset),
                                # audit trail for the overlap question this test exists to answer:
                                # who does DCF drop vs who does the naive PE rule drop, same date.
                                "dcf_drops": "|".join(sorted(t for t, _rt in pool
                                                             if t not in _keepset)),
                                "pe_drops": "|".join(sorted(_dropset))})
                            pool = [p for p in pool if p[0] not in _dropset]
            pe_s  = pe_piv.loc[src_q]  if (pe_piv  is not None and src_q in pe_piv.index)  else None
            pcf_s = pcf_piv.loc[src_q] if (pcf_piv is not None and src_q in pcf_piv.index) else None
            pe_r  = pd.Series({t:(pe_s.get(t,np.nan)  if pe_s  is not None else np.nan) for t,_ in pool}).rank(pct=True).fillna(0.5)
            pcf_r = pd.Series({t:(pcf_s.get(t,np.nan) if pcf_s is not None else np.nan) for t,_ in pool}).rank(pct=True).fillna(0.5)
            score = {t: pe_r[t] + pcf_r[t] for t,_ in pool}
            if dcf_at is not None and DCF_MODE == "tiebreak":
                # variant B: soft blend. rank_pct over the names that HAVE a MoS; NOT_COMPUTED gets
                # 0.5 (same neutral mid-rank convention as a missing 1/PE above) -> never favoured
                # nor penalised, it just keeps its yieldcombo standing.
                mos_r = pd.Series({t: dcf_at(t, d)[1] for t, _ in pool}).rank(pct=True).fillna(0.5)
                for t, _ in pool: score[t] += DCF_W * mos_r[t]
            gated = sorted(pool, key=lambda tr: score[tr[0]], reverse=True)
        elif SELECT_MODE in ("eyfin", "eyonly") and gated:
            pool = gated[:CFO_POOL]
            pe_s = pe_piv.loc[src_q] if (pe_piv is not None and src_q in pe_piv.index) else None
            pe_r = pd.Series({t: (pe_s.get(t, np.nan) if pe_s is not None else np.nan)
                              for t, _ in pool}).rank(pct=True).fillna(0.5)
            if SELECT_MODE == "eyonly":
                score = {t: pe_r[t] for t, _ in pool}
            else:
                pcf_s = pcf_piv.loc[src_q] if (pcf_piv is not None and src_q in pcf_piv.index) else None
                pcf_r = pd.Series({t: (pcf_s.get(t, np.nan) if pcf_s is not None else np.nan)
                                   for t, _ in pool}).rank(pct=True).fillna(0.5)
                # financial -> 2*ey (PCF leg dropped, range preserved); everyone else -> ey + cfy.
                score = {t: (2.0 * pe_r[t] if is_fin(t, src_q) else pe_r[t] + pcf_r[t]) for t, _ in pool}
            gated = sorted(pool, key=lambda tr: score[tr[0]], reverse=True)
            if dy_at is not None:
                # arm A4: DY breaks ties ONLY in the marginal band, and only among names it can
                # actually speak about. Applied AFTER the ey sort and BEFORE the top_n cut — the
                # band straddles the cut line, which is the only place a tie-break changes a pick.
                gated = _dy_reorder(gated, d, _dy_lo, _dy_hi)
        elif SELECT_MODE == "eyrisk" and gated:
            # risk-adjusted ey: multiply the RAW yield by the continuous quality-floor multiplier
            # BEFORE the pool rank — the penalty reorders names only where the floor actually
            # differs, so the rank stays pool-wide (no sector neutralisation anywhere).
            pool = gated[:CFO_POOL]
            pe_s = pe_piv.loc[src_q] if (pe_piv is not None and src_q in pe_piv.index) else None
            ey_adj = pd.Series({t: (pe_s.get(t, np.nan) if pe_s is not None else np.nan)
                                * eyrisk_mult(t, src_q) for t, _ in pool})
            pe_r = ey_adj.rank(pct=True).fillna(0.5)   # NaN ey stays NaN (×m keeps NaN) -> same 0.5 convention as eyonly
            score = {t: pe_r[t] for t, _ in pool}
            gated = sorted(pool, key=lambda tr: score[tr[0]], reverse=True)
        elif SELECT_MODE == "pbcombo" and gated:
            # bottom-deploy: 1/PB-heavy crisis-IC weights (0.67/0.23/0.10) within the liquid+gated pool.
            pool = gated[:CFO_POOL]
            pb_s  = pb_piv.loc[src_q]  if (pb_piv  is not None and src_q in pb_piv.index)  else None
            pcf_s = pcf_piv.loc[src_q] if (pcf_piv is not None and src_q in pcf_piv.index) else None
            pe_s  = pe_piv.loc[src_q]  if (pe_piv  is not None and src_q in pe_piv.index)  else None
            pb_r  = pd.Series({t:(pb_s.get(t,np.nan)  if pb_s  is not None else np.nan) for t,_ in pool}).rank(pct=True).fillna(0.5)
            pcf_r = pd.Series({t:(pcf_s.get(t,np.nan) if pcf_s is not None else np.nan) for t,_ in pool}).rank(pct=True).fillna(0.5)
            pe_r  = pd.Series({t:(pe_s.get(t,np.nan)  if pe_s  is not None else np.nan) for t,_ in pool}).rank(pct=True).fillna(0.5)
            score = {t: 0.67*pb_r[t] + 0.23*pcf_r[t] + 0.10*pe_r[t] for t,_ in pool}
            gated = sorted(pool, key=lambda tr: score[tr[0]], reverse=True)
        elif SELECT_MODE in ("petop", "pemom") and gated:
            # custom30B bull sleeve: liquidity = floor/GATE only; rank by 1/PE (bull IC champion),
            # optionally + MOM_W*rank(mom200). Pool = top-CFO_POOL liquid gated names.
            pool = gated[:CFO_POOL]
            pe_s  = pe_piv.loc[src_q]  if (pe_piv  is not None and src_q in pe_piv.index)  else None
            pe_r  = pd.Series({t:(pe_s.get(t,np.nan) if pe_s is not None else np.nan) for t,_ in pool}).rank(pct=True).fillna(0.5)
            score = {t: pe_r[t] for t,_ in pool}
            if SELECT_MODE == "pemom":
                mom_s = mom_piv.loc[src_q] if (mom_piv is not None and src_q in mom_piv.index) else None
                mom_r = pd.Series({t:(mom_s.get(t,np.nan) if mom_s is not None else np.nan) for t,_ in pool}).rank(pct=True).fillna(0.5)
                for t,_ in pool: score[t] += MOM_W*mom_r[t]
            if RSI_W > 0 and rsi_piv is not None:
                rsi_s = rsi_piv.loc[src_q] if src_q in rsi_piv.index else None
                rsi_r = pd.Series({t:(rsi_s.get(t,np.nan) if rsi_s is not None else np.nan) for t,_ in pool}).rank(pct=True).fillna(0.5)
                for t,_ in pool: score[t] += RSI_W*rsi_r[t]
            gated = sorted(pool, key=lambda tr: score[tr[0]], reverse=True)
        elif SELECT_MODE in _V3_MODES and gated:
            pool = gated[:CFO_POOL]
            score = _score_v3(pool, src_q)
            gated = sorted(pool, key=lambda tr: score[tr[0]], reverse=True)
        elif CFO_BLEND > 0 and gated:
            # liquidity floor (top-POOL), then re-rank by liq x cfo-yield blend
            pool = gated[:CFO_POOL]
            src_cfo = cfo_piv.loc[src_q] if (cfo_piv is not None and src_q in cfo_piv.index) else None
            liq_r = pd.Series({t: liq_row.get(t, np.nan) for t, _ in pool}).rank(pct=True)
            cfo_r = pd.Series({t: (src_cfo.get(t, np.nan) if src_cfo is not None else np.nan)
                               for t, _ in pool}).rank(pct=True).fillna(0.5)
            score = {t: liq_r[t] + CFO_BLEND * cfo_r[t] for t, _ in pool}
            gated = sorted(pool, key=lambda tr: score[tr[0]], reverse=True)
        if PLACEBO and gated:
            gated = _placebo_reorder(gated, d, src_q, top_n)
        picks = []
        for tk, rt in gated[:top_n]:
            qmult = (QT.get(int(rt), QTILT_MISSING) if (quality == "tilt" and pd.notna(rt)) else
                     (QTILT_MISSING if quality == "tilt" else 1.0))
            picks.append((tk, qmult, rt))
        members[d] = [(tk, qm) for tk, qm, _ in picks]
        fin_src_q[d] = src_q
        for rnk, (tk, qm, rt) in enumerate(picks):
            mem_rows.append({"quarter": qd.date(), "rebal_date": d.date(), "ticker": tk,
                             "qmult": qm, "rating": rt, "liq_rank": rnk + 1,
                             # audit column (job Taylor_20260714_140127): the selector score this
                             # name was picked on. Lets a guard assert WHICH INPUTS reach a score
                             # (e.g. "no PCF for financials") directly, instead of inferring it from
                             # membership — membership also moves through the shared rank denominator,
                             # so it cannot isolate one leg. Levels/membership are unaffected.
                             "score": (float(score[tk]) if (score is not None and tk in score) else np.nan)})
    members_df = pd.DataFrame(mem_rows)
    union = sorted(members_df["ticker"].unique())
    # (5) daily panel for the union of all members ever selected
    inlist = ",".join(f"'{x}'" for x in union)
    # sector map (1-digit ICB) for sector-cap weighting — latest row per ticker
    sec_map = {}
    if weight_scheme == "sectorcap":
        secq = bq(f"""SELECT x.ticker, x.sec FROM (
  SELECT t.ticker AS ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS sec,
    ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time DESC) AS rn
  FROM tav2_bq.ticker AS t WHERE t.ticker IN ({inlist}) AND t.ICB_Code IS NOT NULL) AS x
WHERE x.rn=1""")
        sec_map = {tk: int(s) for tk, s in zip(secq["ticker"], secq["sec"])}
    bx = bq(f"""WITH fin AS (
  SELECT f.ticker, f.time AS ftime, f.OShares,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS nft
  FROM tav2_bq.ticker_financial AS f WHERE f.OShares IS NOT NULL)
SELECT t.ticker, t.time, t.Close, {pxw_sql()} AS pxw,
       COALESCE(t.Price,t.Close)*t.Volume AS tv, fin.OShares
FROM tav2_bq.ticker AS t
LEFT JOIN fin ON fin.ticker=t.ticker AND t.time>=fin.ftime AND (fin.nft IS NULL OR t.time<fin.nft)
WHERE t.ticker IN ({inlist})
  AND t.time >= DATE_SUB(DATE '{eff_start}', INTERVAL 10 DAY) AND t.time <= DATE '{end_date}'""")
    bx["time"] = pd.to_datetime(bx["time"])
    bx = bx.sort_values(["ticker", "time"])
    bx["OShares"] = bx.groupby("ticker")["OShares"].ffill().bfill()
    bx["mcap"] = bx["Close"] * bx["OShares"]          # RETURN leg (adjusted; ex-div is not a loss)
    bx["mcapw"] = bx["pxw"] * bx["OShares"]           # WEIGHT leg (raw PIT; see PRICE BASIS header)
    mcap = bx.pivot_table(index="time", columns="ticker", values="mcap").sort_index()
    mcapw = (bx.pivot_table(index="time", columns="ticker", values="mcapw")
               .reindex(index=mcap.index, columns=mcap.columns))
    tvv = bx.pivot_table(index="time", columns="ticker", values="tv").sort_index()
    # (6) chained quality/cap-weighted return using each day's active-quarter membership
    idx_dates = mcap.index
    reb = sorted(members.keys())
    def active_q(d):
        i = bisect.bisect_right(reb, d) - 1
        return reb[i] if i >= 0 else None
    ret = pd.Series(0.0, index=idx_dates); adv_tv = pd.Series(np.nan, index=idx_dates)
    fincap_infeasible = []   # days where too few non-financial names exist to honour FIN_CAP
    prev = None
    for d in idx_dates:
        aq = active_q(d)
        if aq is None or prev is None:
            prev = d; continue
        mem = members.get(aq, [])
        if mem:
            tks = [t for t, _ in mem if t in mcap.columns]
            w = np.array([qm for t, qm in mem if t in mcap.columns])
            today = mcap.loc[d, tks].values.astype(float)
            yest = mcap.loc[prev, tks].values.astype(float)
            yestw = mcapw.loc[prev, tks].values.astype(float)
            valid = ~np.isnan(today) & ~np.isnan(yest)
            if valid.sum() > 0:
                yv = yest[valid]
                # SPLIT BY ROLE (see module header PRICE BASIS): the RETURN uses adjusted Close, the
                # WEIGHT uses the raw PIT price. COALESCE(Price,Close) is non-NULL wherever Close is,
                # so this fills only on a genuine data hole -> fail-safe back to the legacy basis.
                yvw = np.where(np.isnan(yestw[valid]), yv, yestw[valid])
                r = today[valid] / yv - 1.0                   # adjusted-Close return, ex-div safe
                if weight_scheme == "capwt":
                    base = yvw * w[valid]                     # cap-weight (x qmult) base
                    if base.sum() > 0:
                        ret.loc[d] = float(np.nansum(base / base.sum() * r))
                else:
                    base = (np.ones(int(valid.sum())) if weight_scheme == "ew"
                            else yvw * w[valid])             # cap-weight (x qmult) base
                    W = base / base.sum() if base.sum() > 0 else base
                    if weight_scheme == "sectorcap":
                        sv = np.array([sec_map.get(t, -1) for t, ok in zip(tks, valid) if ok])
                        # dynamic cap (audit-only): the cap set at THIS day's active rebal date `aq`;
                        # absent flag -> the fixed `sector_cap` (default path, byte-identical).
                        _scap = seccap_by_date.get(aq, sector_cap) if seccap_by_date else sector_cap
                        W = _cap_sector(W, sv, sector_code, _scap)
                        W = _cap_names(W, name_cap)
                    elif weight_scheme == "fincap":
                        # financial ROUTES capped as one group (routed PIT at this day's active
                        # rebal's selection quarter) JOINTLY with the single-name cap.
                        _sq = fin_src_q.get(aq)
                        fv = np.array([is_fin(t, _sq) for t, ok in zip(tks, valid) if ok])
                        W, _ce = _cap_group_jointly(W, fv, FIN_CAP, name_cap)
                        if _ce > FIN_CAP + 1e-9: fincap_infeasible.append((d, _ce, int((~fv).sum())))
                    elif weight_scheme == "namecap":
                        W = _cap_names(W, name_cap)
                    ret.loc[d] = float(np.nansum(W * r))
            adv_tv.loc[d] = np.nansum(tvv.loc[d, tks].values.astype(float))
        prev = d
    if dcf_at is not None and DCF_MODE in ("placebo_random", "placebo_pe") and _placebo_log:
        # audit trail: lets a reviewer verify the placebo dropped exactly n_d names per date, i.e.
        # that this really is a same-count control and not a differently-sized gate.
        _pl = pd.DataFrame(_placebo_log)
        _plname = (f"placebo_drops_seed{DCF_PLACEBO_SEED}.csv" if DCF_MODE == "placebo_random"
                   else "placebo_pe_drops.csv")
        _pl.to_csv(f"data/dcf_exp_logs/{_plname}", index=False)
        print(f"  [DCF placebo] {DCF_MODE}: dropped {int(_pl['n_dropped'].sum())} names "
              f"over {len(_pl)} rebal dates (mean {_pl['n_dropped'].mean():.2f}/date)"
              + (f" [target {int(_pl['n_target'].sum())}]" if "n_target" in _pl else ""))
    if weight_scheme == "fincap":
        if fincap_infeasible:
            _wc = pd.DataFrame(fincap_infeasible, columns=["date", "cap_eff", "n_nonfin"])
            print(f"  [fincap] ⚠ cap {FIN_CAP:.2f} INFEASIBLE on {len(_wc)}/{len(idx_dates)} days "
                  f"(too few non-financial names to absorb 1-cap under name_cap={name_cap:.2f}): "
                  f"effective cap med {_wc.cap_eff.median():.3f} / max {_wc.cap_eff.max():.3f}, "
                  f"n_nonfin med {int(_wc.n_nonfin.median())}")
        else:
            print(f"  [fincap] cap {FIN_CAP:.2f} feasible on all {len(idx_dates)} days")
    lvl = BASE_LEVEL * (1.0 + ret).cumprod()
    adv = adv_tv.rolling(60, min_periods=20).mean()
    level_dict = {t: float(v) for t, v in zip(lvl.index, lvl.values)}
    adv_dict = {t: float(v) for t, v in zip(adv.index, adv.values) if pd.notna(v)}
    return level_dict, adv_dict, members_df, bx
