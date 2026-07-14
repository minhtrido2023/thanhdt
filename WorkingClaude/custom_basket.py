# -*- coding: utf-8 -*-
"""custom_basket.py — deterministic, BQ-reconstructable CUSTOM VN30-style parking basket.
================================================================================================
§5 of SESSION_HANDOFF_2026-06-13: at large NAV the strict-E1VFVN30 parking cap strands idle cash.
This module builds a high-capacity, rule-based liquid VN-equity beta vehicle to replace the ETF as
the parking vehicle (own the underlyings -> no fund management fee, only rebalance friction).

The basket is a pure deterministic function of raw tav2_bq data, so an independent auditor can
rebuild it from scratch and verify every parking-row price. Shared by pt_v23_audit_2014.py /
pt_v22_dt5g.py (simulation) and data/v23_audit_spotcheck.py (verification): identical series.

UNIVERSE = RULES, NOT EXCEPTIONS: members come from ticker_prune ∩ ICB_Code IS NOT NULL (real
listed companies; indices/ETFs have NULL ICB -> auto-excluded). NO ticker is hardcoded out. VIC
competes like any name; it is admitted iff it passes the 8L quality gate (see build_pit gate_rating)
-> in practice gated out ~24/25 quarters because its 8L rating is 4-5, admitted when it earns <=3.

Construction (cap-weighted CHAINED index):
  members  = top-30 by AVG(Volume_3M_P50*Close); build()=static window, build_pit()=PIT-per-quarter.
  mcap_i,t = adjusted Close_i,t * OShares_i (OShares from ticker_financial, as-of/ffilled to daily).
  ret_t    = SUM_i(mcap_i,t) / SUM_i(mcap_i,t-1) - 1   over names valid on BOTH t-1 and t
             (chained -> listings/halts cause no composition jumps).
  level_t  = 1000 * cumprod(1 + ret_t).   (base 1000 arbitrary; only returns matter for parking.)
  adv_t    = 60-session rolling mean of SUM_i(COALESCE(Price,Close)_i,t * Volume_i,t)  [creation capacity].
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
# ticker_prune, i.e. ICB_Code IS NOT NULL. That single rule auto-excludes index pseudo-tickers
# (VN30/VNINDEX) AND ETFs (E1VFVN30) — all of which carry a NULL ICB_Code — without hardcoding any
# ticker. VIC is NOT special-cased: it competes on liquidity like any name and is admitted iff it
# passes the 8L quality gate (rating<=gate). Empirically VIC is rated 4-5 in ~24/25 quarters so the
# gate excludes it BY RULE, and admits it the rare quarter it earns rating<=3 (e.g. 2020Q4).
UNIVERSE_FILTER = "t.ICB_Code IS NOT NULL"
SEL_START, SEL_END = "2020-01-01", "2025-01-01"
N_MEMBERS = 30


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


def select_members(bq):
    """Return the 30 most-liquid listed-company members (deterministic, STATIC/hindsight window).
    Universe = ticker_prune ∩ UNIVERSE_FILTER (real companies). No per-ticker exclusions."""
    df = bq(f"""SELECT t.ticker FROM tav2_bq.ticker t
WHERE t.time BETWEEN DATE '{SEL_START}' AND DATE '{SEL_END}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)
  AND {UNIVERSE_FILTER}
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50*t.Close) DESC LIMIT {N_MEMBERS}""")
    return list(df["ticker"])


def build(bq, names, start_date, end_date):
    """Build the basket. Returns (level_dict{ts:level}, adv_dict{ts:adv_vnd}, raw_df).
    raw_df has columns time,ticker,Close,tv,OShares,mcap for full reconstruction transparency."""
    inlist = ",".join(f"'{x}'" for x in names)
    bx = bq(f"""WITH fin AS (
  SELECT f.ticker, f.time AS ftime, f.OShares,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS nft
  FROM tav2_bq.ticker_financial AS f WHERE f.OShares IS NOT NULL)
SELECT t.ticker, t.time, t.Close, COALESCE(t.Price,t.Close)*t.Volume AS tv, fin.OShares
FROM tav2_bq.ticker AS t
LEFT JOIN fin ON fin.ticker=t.ticker AND t.time>=fin.ftime AND (fin.nft IS NULL OR t.time<fin.nft)
WHERE t.ticker IN ({inlist})
  AND t.time >= DATE_SUB(DATE '{start_date}', INTERVAL 200 DAY) AND t.time <= DATE '{end_date}'""")
    bx["time"] = pd.to_datetime(bx["time"])
    bx = bx.sort_values(["ticker", "time"])
    bx["OShares"] = bx.groupby("ticker")["OShares"].ffill().bfill()
    bx["mcap"] = bx["Close"] * bx["OShares"]
    piv = bx.pivot_table(index="time", columns="ticker", values="mcap").sort_index()
    num = piv.where(piv.shift().notna())       # today's mcap where yesterday valid
    den = piv.shift().where(piv.notna())       # yesterday's mcap where today valid
    ret = (num.sum(axis=1) / den.sum(axis=1) - 1.0).fillna(0.0)
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
    assert weight_scheme in ("capwt", "ew", "namecap", "sectorcap")
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
    qliq = bq(f"""SELECT t.ticker, DATE_TRUNC(t.time, QUARTER) AS q,
  AVG(t.Volume_3M_P50*t.Close) AS liq, COUNT(*) AS nd
FROM tav2_bq.ticker t
WHERE t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)
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
    # BULL sleeve (custom30B) audit knobs (env, prod default OFF): absolute liquidity floor + 1/PE-led selectors.
    # LIQ_FLOOR_B = min prior-quarter avg secondary liq (VND bn/day) to ENTER (deploy more capital, ~10 = user).
    # SELECT_MODE 'petop' = pure rank(1/PE) (bull IC champion +0.161). 'pemom' = rank(1/PE)+MOM_W*rank(mom200).
    LIQ_FLOOR = float(os.environ.get("BASKET_LIQ_FLOOR_B", "0")) * 1e9
    MOM_W = float(os.environ.get("BASKET_MOM_W", "0.5"))
    RSI_W = float(os.environ.get("BASKET_RSI_W", "0"))   # custom30B: + RSI_W*rank(prior-q avg D_RSI) (best bull add)
    def _yield_piv(col):
        _y = bq(f"""SELECT t.ticker, DATE_TRUNC(t.time, QUARTER) AS q, AVG(SAFE_DIVIDE(1, t.{col})) AS y
FROM tav2_bq.ticker t WHERE t.{col} > 0 AND t.time BETWEEN DATE '{eff_start}' AND DATE '{end_date}'
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
    DCF_MODE = os.environ.get("BASKET_DCF_MODE", "").lower()
    DCF_W    = float(os.environ.get("BASKET_DCF_W", "0.25"))
    DCF_PLACEBO_SEED = int(os.environ.get("BASKET_DCF_PLACEBO_SEED", "0"))
    dcf_at = None
    if DCF_MODE:
        if SELECT_MODE != "yieldcombo":
            raise ValueError(f"BASKET_DCF_MODE={DCF_MODE} only defined for BASKET_SELECT=yieldcombo")
        if DCF_MODE not in ("exclude_rich", "tiebreak", "placebo_random"):
            raise ValueError(f"BASKET_DCF_MODE={DCF_MODE} unknown (exclude_rich|tiebreak|placebo_random)")
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
    _v3q = None
    if SELECT_MODE in ("v3comp", "ps3", "v3gated", "v3latest"):
        _p = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "value_panel_2014.csv"),
                         parse_dates=["time"])
        _p["qstart"] = _p["time"].dt.to_period("Q").dt.start_time
        _p = _p.sort_values("time").groupby(["ticker", "qstart"]).last().reset_index()   # last obs per quarter
        _cols=["qstart","ticker","PE","PCF","PS","pb_z","PB","route","ICB_Code","ROE_Min3Y",
               "CF_OA_P0","CF_OA_P1","CF_OA_P2","CF_OA_P3","CF_OA_3Y"]
        _v3q = _p[[c for c in _cols if c in _p.columns]]
    # v3comp = PS broad; v3gated = PS retail-only; v3latest = THIS-MORNING rating_8l v3 (CYCLICAL ps->0,
    # cfy=cfo_normy for non-cyclical, golden floor gated by CF_OA_3Y>0).
    VR_W_FULL   = {"COMPOUNDER": (.45,.30,.25), "CYCLICAL": (.35,.50,.15), "RETAIL": (.35,.20,.45)}
    VR_W_GATED  = {"RETAIL": (.35,.20,.45), "CYCLICAL": (.50,.50,.00), "_default": (.55,.45,.00)}
    VR_W_LATEST = {"COMPOUNDER": (.45,.30,.25), "CYCLICAL": (.40,.60,.00), "RETAIL": (.35,.20,.45)}
    VR_W = {"v3gated":VR_W_GATED,"v3latest":VR_W_LATEST}.get(SELECT_MODE, VR_W_FULL)
    _VRDEF = VR_W.get("_default", VR_W.get("COMPOUNDER"))
    def _score_v3(pool, src_q):
        toks = [t for t,_ in pool]
        d = _v3q[(_v3q.qstart == src_q) & (_v3q.ticker.isin(toks))].set_index("ticker")
        d = d.reindex(toks)                                   # align to pool order; missing -> NaN row
        ey  = np.where(d.PE  > 0, 1.0/d.PE,  np.nan)
        cfy = np.where(d.PCF > 0, 1.0/d.PCF, np.nan)
        ps  = np.where(d.PS  > 0, 1.0/d.PS,  np.nan)
        if SELECT_MODE == "v3latest" and "CF_OA_3Y" in d.columns:   # cfo_normy for non-cyclical, raw for cyclical
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
        if SELECT_MODE == "v3latest" and "CF_OA_3Y" in d.columns:   # golden floor also requires CF_OA_3Y>0 (CTF gate)
            bookok = bookok & (d.CF_OA_3Y.values > 0)
        sc = sc + 0.10*np.where(golden & pd.notna(d.pb_z.values), 1.0, 0.0)
        sc = np.where(d.PB.values < 0, 0.0, sc)
        sc = np.where(golden & bookok, np.maximum(np.nan_to_num(sc, nan=0.0), 1.0), sc)   # golden book-OK floor (=> selected first)
        return {t: (float(v) if pd.notna(v) else -1.0) for t, v in zip(toks, sc)}
    # ---- AUDIT-ONLY dynamic sector cap (job Taylor_20260714_095953, sector-cap research) ----
    # BASKET_SECCAP_MODE: "" (default, OFF -> byte-identical: sectorcap keeps the fixed `sector_cap`)
    #   | "mktcap"   (variant B: cap sector_code at its PIT market-cap weight in ticker_prune)
    #   | "mktx<f>"  (variant B': same x <f>, e.g. mktx1.5 = allow a 1.5x value tilt over market).
    # Only meaningful with weight_scheme='sectorcap'. The cap is recomputed at EACH rebal date from
    # ONLY that day's data (mcap = Close x as-of OShares, identical definition to the basket's own
    # mcap, so basket weight and market weight are on one scale) -> no look-ahead.
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
SELECT t.time, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS sec, SUM(t.Close*fin.OShares) AS mcap
FROM tav2_bq.ticker AS t
JOIN fin ON fin.ticker=t.ticker AND t.time>=fin.ftime AND (fin.nft IS NULL OR t.time<fin.nft)
WHERE t.time IN ({_rin}) AND t.ICB_Code IS NOT NULL AND t.Close IS NOT NULL
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)
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
    members = {}  # rebal_date -> list[(ticker, qmult)]
    mem_rows = []
    for d in rebal_dates:
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
            rt = rating_asof(tk, d)
            if gate_rating is not None and not (pd.notna(rt) and rt <= gate_rating): continue
            if quality == "filter" and not (pd.notna(rt) and rt <= 3): continue
            if QFLOOR and not qfloor_asof(tk, d): continue              # Đ2 fundamentals floor (see 2b)
            gated.append((tk, rt))
        if SELECT_MODE == "yieldcombo" and gated:
            # custom30V: liquidity = GATE only (top-POOL tradability floor); rank PURELY by combined
            # value-yield = rank(1/PE)+rank(1/PCF). For BULL parking funded mainly by LAG idle cash.
            pool = gated[:CFO_POOL]
            if dcf_at is not None and DCF_MODE in ("exclude_rich", "placebo_random"):
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
                        # seed = (SEED, date) so each rebal date draws INDEPENDENTLY, yet the whole
                        # 48-date path replays exactly from the same SEED. A single global RNG would
                        # make the draws path-dependent on rebal ordering and unreplayable per-date.
                        _rng = np.random.default_rng([DCF_PLACEBO_SEED, pd.Timestamp(d).toordinal()])
                        _drop = set(_rng.choice(len(pool), size=_n_d, replace=False).tolist())
                        pool = [p for _i, p in enumerate(pool) if _i not in _drop]
                        _placebo_log.append({"date": pd.Timestamp(d), "n_pool": len(pool) + _n_d,
                                             "n_dropped": _n_d})
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
        elif SELECT_MODE in ("v3comp", "ps3", "v3gated", "v3latest") and gated:
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
        picks = []
        for tk, rt in gated[:top_n]:
            qmult = (QT.get(int(rt), QTILT_MISSING) if (quality == "tilt" and pd.notna(rt)) else
                     (QTILT_MISSING if quality == "tilt" else 1.0))
            picks.append((tk, qmult, rt))
        members[d] = [(tk, qm) for tk, qm, _ in picks]
        for rnk, (tk, qm, rt) in enumerate(picks):
            mem_rows.append({"quarter": qd.date(), "rebal_date": d.date(), "ticker": tk,
                             "qmult": qm, "rating": rt, "liq_rank": rnk + 1})
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
SELECT t.ticker, t.time, t.Close, COALESCE(t.Price,t.Close)*t.Volume AS tv, fin.OShares
FROM tav2_bq.ticker AS t
LEFT JOIN fin ON fin.ticker=t.ticker AND t.time>=fin.ftime AND (fin.nft IS NULL OR t.time<fin.nft)
WHERE t.ticker IN ({inlist})
  AND t.time >= DATE_SUB(DATE '{eff_start}', INTERVAL 10 DAY) AND t.time <= DATE '{end_date}'""")
    bx["time"] = pd.to_datetime(bx["time"])
    bx = bx.sort_values(["ticker", "time"])
    bx["OShares"] = bx.groupby("ticker")["OShares"].ffill().bfill()
    bx["mcap"] = bx["Close"] * bx["OShares"]
    mcap = bx.pivot_table(index="time", columns="ticker", values="mcap").sort_index()
    tvv = bx.pivot_table(index="time", columns="ticker", values="tv").sort_index()
    # (6) chained quality/cap-weighted return using each day's active-quarter membership
    idx_dates = mcap.index
    reb = sorted(members.keys())
    def active_q(d):
        i = bisect.bisect_right(reb, d) - 1
        return reb[i] if i >= 0 else None
    ret = pd.Series(0.0, index=idx_dates); adv_tv = pd.Series(np.nan, index=idx_dates)
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
            valid = ~np.isnan(today) & ~np.isnan(yest)
            if valid.sum() > 0:
                if weight_scheme == "capwt":
                    # legacy path — kept byte-identical (mcap x qmult cap-weight)
                    num = np.nansum(today[valid] * w[valid]); den = np.nansum(yest[valid] * w[valid])
                    if den > 0: ret.loc[d] = num / den - 1.0
                else:
                    yv = yest[valid]
                    base = (np.ones(int(valid.sum())) if weight_scheme == "ew"
                            else yv * w[valid])              # cap-weight (x qmult) base
                    W = base / base.sum() if base.sum() > 0 else base
                    if weight_scheme == "sectorcap":
                        sv = np.array([sec_map.get(t, -1) for t, ok in zip(tks, valid) if ok])
                        # dynamic cap (audit-only): the cap set at THIS day's active rebal date `aq`;
                        # absent flag -> the fixed `sector_cap` (default path, byte-identical).
                        _scap = seccap_by_date.get(aq, sector_cap) if seccap_by_date else sector_cap
                        W = _cap_sector(W, sv, sector_code, _scap)
                        W = _cap_names(W, name_cap)
                    elif weight_scheme == "namecap":
                        W = _cap_names(W, name_cap)
                    r = today[valid] / yv - 1.0
                    ret.loc[d] = float(np.nansum(W * r))
            adv_tv.loc[d] = np.nansum(tvv.loc[d, tks].values.astype(float))
        prev = d
    if dcf_at is not None and DCF_MODE == "placebo_random" and _placebo_log:
        # audit trail: lets a reviewer verify the placebo dropped exactly n_d names per date, i.e.
        # that this really is a same-count control and not a differently-sized gate.
        _pl = pd.DataFrame(_placebo_log)
        _pl.to_csv(f"data/dcf_exp_logs/placebo_drops_seed{DCF_PLACEBO_SEED}.csv", index=False)
        print(f"  [DCF placebo] seed={DCF_PLACEBO_SEED}: dropped {int(_pl['n_dropped'].sum())} names "
              f"over {len(_pl)} rebal dates (mean {_pl['n_dropped'].mean():.2f}/date)")
    lvl = BASE_LEVEL * (1.0 + ret).cumprod()
    adv = adv_tv.rolling(60, min_periods=20).mean()
    level_dict = {t: float(v) for t, v in zip(lvl.index, lvl.values)}
    adv_dict = {t: float(v) for t, v in zip(adv.index, adv.values) if pd.notna(v)}
    return level_dict, adv_dict, members_df, bx
