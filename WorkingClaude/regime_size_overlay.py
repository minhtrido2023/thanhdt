# -*- coding: utf-8 -*-
"""regime_size_overlay.py — VALIDATED 8L-rating integration for the V11/V12x books.

Research (memory: fa_rating_8l_pergroup_2026): replacing the flat fa_tier with the 8L per-group rating
LOSES at full-NAV (OOS -4.22pp). The integration that WINS is regime-conditional SIZE modulation:
keep weak names at full weight in good regimes, HALVE them only in BEAR/CRISIS (state<=2). Prior art
+0.73 Full / +0.84 OOS, Sharpe & DD better, across all systems. The weak flag must be the ABSOLUTE 8L
rating>=4 (genuine fragility: low ROIC / high real-leverage / weak FSCORE), NOT the per-group percentile
tier D/E (relative — that LOST, OOS -0.45: fragility is absolute, not relative-to-peers).

Dormant in NEUTRAL/BULL/EX-BULL (state>=3) -> adding it to a live paper-trade changes NOTHING until a
stress regime hits, then it provides the validated protection. Safe to deploy as default.

Usage in a pt_* script (after SV_TIGHT/P3, before simulate):
    from regime_size_overlay import apply_regime_size
    sig_f, RS = apply_regime_size(sig_f, START_DATE, END_DATE, bq, base_tiers=TIER_BAL)
    # then in EACH simulate() call:
    #   allowed_tiers          = RS["allowed_tiers"]
    #   tier_weights           = RS["tier_weights"]
    #   tier_weights_by_state  = RS["tier_weights_by_state"]
    #   sector_cap_exempt_tiers= RS["sector_cap_exempt"]   # BAL book only (keeps RE_BACKLOG_BUY exempt)
"""
import pandas as pd

FULL_SIZE = 0.10
WEAK_SIZE = 0.05          # halved weight for rating>=4 names in BEAR/CRISIS
STRESS_STATES = (1, 2)    # CRISIS, BEAR
WEAK_RATING_MIN = 4       # absolute 8L rating >= 4 = fragile (NOT the per-group percentile tier)

# default book buy tiers that carry position weight (BAL leg)
DEFAULT_BASE_TIERS = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
DEFAULT_BUY_TIERS  = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                      "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}


def load_rating8l(start, end, bq):
    """Point-in-time ABSOLUTE 8L rating (1-5) per (ticker, eff_date) from tav2_bq.fa_ratings_8l.
    Returns a DataFrame [ticker, time, rating8l] sorted by time (ready for merge_asof)."""
    df = bq(f"""SELECT f.ticker, f.time, f.rating AS rating8l
    FROM tav2_bq.fa_ratings_8l AS f
    WHERE f.time <= DATE '{end}'""")
    df["time"] = pd.to_datetime(df["time"])
    return df.sort_values("time")[["ticker","time","rating8l"]]


def build_capit_suppress_windows(comovement_csv="data/daily_comovement_dt5g.csv",
                                 hold=60, oversold=0.40, min_gap=30, scope="all"):
    """Build the set of dates where regime_size should be SUPPRESSED because a capitulation event is active.
    A washout event = first day of a cluster with breadth pct_oversold >= `oversold` (clusters split by
    >= `min_gap` calendar days); regime_size is suppressed for `hold` trading days from each event.
    scope: "all" (every washout, matches the EXTENDED-GRINDHALF overlay) or "crisis" (only state==1 events).
    Returns a set of pd.Timestamp. VALIDATED (RS-off-in-capitulation): V5 +cap+grind 34.73 -> 35.37 (+0.64pp
    vs RS-always, +0.22 vs RS-never), Sharpe back to 1.64. Deploy this TOGETHER with the capitulation overlay.
    """
    import os
    p = comovement_csv if os.path.isabs(comovement_csv) else os.path.join(
        os.environ.get("WORKDIR_8L", os.getcwd()), comovement_csv)
    D = pd.read_csv(p, parse_dates=["time"]).sort_values("time").reset_index(drop=True)
    days = list(D["time"])
    ws = D[D["pct_oversold"] >= oversold].copy()
    ws["g"] = ws["time"].diff().dt.days.fillna(999); ws["c"] = (ws["g"] >= min_gap).cumsum()
    st_by = D.set_index("time")["state"] if "state" in D.columns else None
    sup = set()
    for _, g in ws.groupby("c"):
        ev = g.iloc[0]["time"]
        if scope == "crisis" and st_by is not None and int(st_by.get(ev, 3)) != 1:
            continue
        i0 = days.index(ev)
        for d in days[i0:i0 + hold + 1]:
            sup.add(pd.Timestamp(d))
    return sup


def apply_regime_size(sig, start, end, bq, base_tiers=None, buy_tiers=None,
                      full_size=FULL_SIZE, weak_size=WEAK_SIZE, rating_df=None, capit_windows=None):
    """Attach point-in-time 8L rating, split weak (rating>=4) buy rows into '<tier>_W', and return the
    simulate() config that halves the _W tiers ONLY in stress states (1,2). Non-stress states keep full
    size, so the overlay is dormant outside BEAR/CRISIS.

    capit_windows: optional set of pd.Timestamp (from build_capit_suppress_windows) on which the weak-halving
      is SUPPRESSED (regime_size yields to the capitulation overlay there). None = always-on (current default,
      since capitulation is not yet deployed). Plumbed to simulate() via RS["regime_suppress_dates"].

    Returns (sig_out, RS) where RS has allowed_tiers / tier_weights / tier_weights_by_state / sector_cap_exempt
    / regime_suppress_dates.
    """
    base_tiers = list(base_tiers) if base_tiers is not None else list(DEFAULT_BASE_TIERS)
    buy_tiers  = set(buy_tiers) if buy_tiers is not None else set(DEFAULT_BUY_TIERS)
    s = sig.copy()
    s["time"] = pd.to_datetime(s["time"])

    rd = rating_df if rating_df is not None else load_rating8l(start, end, bq)
    s = s.sort_values("time")
    s = pd.merge_asof(s, rd, on="time", by="ticker", direction="backward")

    weak_mask = (s["rating8l"] >= WEAK_RATING_MIN) & s["play_type"].isin(set(base_tiers))
    n_weak = int(weak_mask.sum())
    s.loc[weak_mask, "play_type"] = s.loc[weak_mask, "play_type"].astype(str) + "_W"

    weak_tiers = [t + "_W" for t in base_tiers]
    allowed = base_tiers + weak_tiers
    twbs = {st: {**{t: full_size for t in base_tiers}, **{t: weak_size for t in weak_tiers}}
            for st in STRESS_STATES}
    exempt = {"RE_BACKLOG_BUY", "RE_BACKLOG_BUY_W"}
    cov = s["rating8l"].notna().mean()
    print(f"  [regime_size] rating coverage {cov:.1%}; weak buy-rows flagged (rating>={WEAK_RATING_MIN}): "
          f"{n_weak:,} -> halved to {weak_size:.0%} ONLY in BEAR/CRISIS (state<=2), full {full_size:.0%} elsewhere")
    if capit_windows:
        print(f"  [regime_size] RS-off-in-capitulation: suppressed on {len(capit_windows)} dates "
              f"(weak names keep full size during capitulation windows)")
    RS = dict(allowed_tiers=allowed,
              tier_weights={t: full_size for t in allowed},
              tier_weights_by_state=twbs,
              sector_cap_exempt=exempt,
              regime_suppress_dates=capit_windows)
    return s, RS
