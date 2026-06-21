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
    cfo_piv = None; pe_piv = None; pcf_piv = None; mom_piv = None; rsi_piv = None
    if SELECT_MODE == "yieldcombo":
        # custom30V: liquidity is GATE only; rank PURELY by combined value-yield rank(1/PE)+rank(1/PCF)
        pe_piv = _yield_piv("PE"); pcf_piv = _yield_piv("PCF")
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
            rt = rating_asof(tk, d)
            if gate_rating is not None and not (pd.notna(rt) and rt <= gate_rating): continue
            if quality == "filter" and not (pd.notna(rt) and rt <= 3): continue
            gated.append((tk, rt))
        if SELECT_MODE == "yieldcombo" and gated:
            # custom30V: liquidity = GATE only (top-POOL tradability floor); rank PURELY by combined
            # value-yield = rank(1/PE)+rank(1/PCF). For BULL parking funded mainly by LAG idle cash.
            pool = gated[:CFO_POOL]
            pe_s  = pe_piv.loc[src_q]  if (pe_piv  is not None and src_q in pe_piv.index)  else None
            pcf_s = pcf_piv.loc[src_q] if (pcf_piv is not None and src_q in pcf_piv.index) else None
            pe_r  = pd.Series({t:(pe_s.get(t,np.nan)  if pe_s  is not None else np.nan) for t,_ in pool}).rank(pct=True).fillna(0.5)
            pcf_r = pd.Series({t:(pcf_s.get(t,np.nan) if pcf_s is not None else np.nan) for t,_ in pool}).rank(pct=True).fillna(0.5)
            score = {t: pe_r[t] + pcf_r[t] for t,_ in pool}
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
                        W = _cap_sector(W, sv, sector_code, sector_cap)
                        W = _cap_names(W, name_cap)
                    elif weight_scheme == "namecap":
                        W = _cap_names(W, name_cap)
                    r = today[valid] / yv - 1.0
                    ret.loc[d] = float(np.nansum(W * r))
            adv_tv.loc[d] = np.nansum(tvv.loc[d, tks].values.astype(float))
        prev = d
    lvl = BASE_LEVEL * (1.0 + ret).cumprod()
    adv = adv_tv.rolling(60, min_periods=20).mean()
    level_dict = {t: float(v) for t, v in zip(lvl.index, lvl.values)}
    adv_dict = {t: float(v) for t, v in zip(adv.index, adv.values) if pd.notna(v)}
    return level_dict, adv_dict, members_df, bx
