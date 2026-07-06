#!/usr/bin/env python3
"""
Hog - Feed margin-SPREAD proxy vs reported GPM (DBC, BAF).  job Taylor_20260706_022555

Follow-up to hog_gpm_leadlag.py (job Taylor_20260706_014930). That work proved the
weekly hog price LEADS/co-moves with quarterly GPM, but flagged the one-sided flaw:
GPM = f(hog_price - FEED_COST). In 2022 hog RECOVERED (hog_yoy +16..+21%) yet DBC GPM
went DEEPLY negative because corn/soybean-meal feed cost spiked (Ukraine war). A hog-
price-alone signal FALSE-POSITIVES there.

Now feed data exists (Winston, job Winston_20260706_021459):
  data/maize_monthly.csv          -- corn, World Bank Pink Sheet, USD/mt, monthly 2006-04+
  data/soybean_meal_monthly.csv   -- soybean meal, same source, USD/mt, monthly 2006-04+
  data/hog_price_vn.csv           -- North (Bac) VND/kg, weekly, 2019-01-04+

Build a margin-spread proxy = hog - feed_cost, and test: does it correlate with GPM
BETTER than hog alone, and does it FIX the 2022 false-positive?

UNIT DISCIPLINE (critical): feed = world USD/mt, hog = VN domestic VND/kg. Absolute
levels are NOT comparable (scale + FX + pass-through). So everything is done in
% change (YoY) or z-score of level -- never mixing raw USD/mt with VND/kg. The feed
"basket" is a real $/mt cost of the pig-feed mix (physical tonnage weights), then YoY.

Strictly evaluation-only, no look-ahead, RESEARCH -- touches no production file.
"""
import pandas as pd, numpy as np

def spearmanr(a, b):
    a = pd.Series(np.asarray(a, float)); b = pd.Series(np.asarray(b, float))
    n = len(a); r = a.rank().corr(b.rank())
    if n > 2 and abs(r) < 1:
        from math import erfc, sqrt
        t = r * np.sqrt((n - 2) / (1 - r * r)); p = erfc(abs(t) / sqrt(2))
    else:
        p = float("nan")
    return r, p

ROOT = "/home/trido/thanhdt/WorkingClaude"

# ---------- 1. FEED basket -> quarterly, YoY ----------
# VN pig-feed ("cam heo") formula: corn/maize = main energy (~55-65% by weight),
# soybean meal = main protein (~15-25%). Cost basket weights below are the PHYSICAL
# TONNAGE proportions of the two dominant imported inputs, RENORMALISED to sum 1
# (the rest -- rice bran, additives, vitamins -- is not in the world series and is
# assumed to move with these two). Base case corn:sbm = 60:40; sensitivity 70:30 &
# 50:50 reported below. A weighted USD/mt sum IS a legitimate $/mt feed-mix cost.
maize = pd.read_csv(f"{ROOT}/data/maize_monthly.csv")
sbm   = pd.read_csv(f"{ROOT}/data/soybean_meal_monthly.csv")
for df in (maize, sbm):
    df["month"] = pd.PeriodIndex(df["month"], freq="M")
feed = maize.rename(columns={"price": "maize"}).merge(
    sbm.rename(columns={"price": "sbm"}), on="month", how="inner").set_index("month")

def feed_quarterly(w_maize):
    w_sbm = 1.0 - w_maize
    basket = w_maize * feed["maize"] + w_sbm * feed["sbm"]      # USD/mt feed-mix cost
    q = basket.groupby(basket.index.asfreq("Q")).mean().rename("feed")
    out = q.to_frame()
    out["feed_yoy"] = out["feed"].pct_change(4)
    out["feed_z"] = (out["feed"] - out["feed"].rolling(20, min_periods=8).mean()) \
                    / out["feed"].rolling(20, min_periods=8).std()
    return out

FEED = {w: feed_quarterly(w) for w in (0.60, 0.70, 0.50)}
print("=== Feed basket (60:40 corn:sbm) quarterly USD/mt, YoY ===")
print(FEED[0.60].loc["2020Q1":].round(3).to_string())

# ---------- 2. HOG -> quarterly, YoY, z ----------
hog = pd.read_csv(f"{ROOT}/data/hog_price_vn.csv")
hog = hog[hog["region"] == "Bắc"].copy()
hog["date"] = pd.to_datetime(hog["date"], errors="coerce")
hog = hog.dropna(subset=["date"]).sort_values("date")
hq = hog.groupby(hog["date"].dt.to_period("Q"))["price_vnd_kg"].mean().rename("hog").to_frame()
hq["hog_yoy"] = hq["hog"].pct_change(4)
hq["hog_z"] = (hq["hog"] - hq["hog"].rolling(20, min_periods=8).mean()) \
              / hq["hog"].rolling(20, min_periods=8).std()

# ---------- 3. GPM per ticker ----------
gpm = pd.read_csv("/tmp/gpm_dbc_baf.csv")
gpm["q"] = pd.PeriodIndex(gpm["quarter"], freq="Q")
gpm["Release_Date"] = pd.to_datetime(gpm["Release_Date"])

def build(tk, w_maize=0.60, feed_lag=0):
    """Align hog, feed, GPM at the same GPM-quarter. feed_lag>0 lags feed cost into
    COGS (imported feed inventories before hitting the P&L)."""
    d = gpm[gpm["ticker"] == tk].sort_values("q").set_index("q")
    d = d[["GPM_P0", "GPM_P4", "Release_Date"]].copy()
    d["gpm_turn"] = d["GPM_P0"] - d["GPM_P4"]              # YoY margin turn (framework signal)
    fq = FEED[w_maize]
    m = d.join(hq[["hog", "hog_yoy", "hog_z"]], how="left")
    # feed at Q-feed_lag aligned to GPM at Q
    m["feed_yoy"] = fq["feed_yoy"].reindex(m.index - feed_lag).values
    m["feed_z"]   = fq["feed_z"].reindex(m.index - feed_lag).values
    # SPREAD proxies (unit-free):
    m["spread_yoy"] = m["hog_yoy"] - m["feed_yoy"]        # YoY: hog rise minus feed rise
    m["spread_z"]   = m["hog_z"]   - m["feed_z"]          # z-level: hog high minus feed high
    return m

# ---------- 4. HEADLINE: spread vs hog-alone, corr with GPM turn ----------
print("\n\n" + "=" * 78)
print("HEADLINE — does SPREAD beat hog-alone at explaining the GPM YoY-turn?")
print("=" * 78)
for tk in ("DBC", "BAF"):
    print(f"\n########## {tk} ##########")
    best = None
    for fl in (0, 1):
        m = build(tk, 0.60, feed_lag=fl)
        rows = []
        for sig in ("hog_yoy", "feed_yoy", "spread_yoy", "spread_z"):
            sub = m[[sig, "gpm_turn"]].dropna()
            if len(sub) >= 6:
                r, p = spearmanr(sub[sig], sub["gpm_turn"])
                rows.append((sig, r, p, len(sub)))
        print(f"  -- feed_lag={fl}q (feed at GPM-quarter minus {fl}) --")
        for sig, r, p, n in rows:
            tag = "  <-- FEED OVERLAY" if sig.startswith("spread") else ""
            print(f"     {sig:12s} vs gpm_turn : {r:+.3f} (n={n}, p={p:.2f}){tag}")

# ---------- 5. THE 2022 TEST (the whole point) ----------
print("\n\n" + "=" * 78)
print("2022 CASE — hog RECOVERED but GPM went DEEPLY negative (feed spike).")
print("Does the spread proxy correctly say 'margin DOWN' where hog-alone says 'UP'?")
print("=" * 78)
m = build("DBC", 0.60, feed_lag=0)
seg = m.loc[pd.Period("2021Q3", "Q"):pd.Period("2023Q2", "Q")]
print("\n DBC 2021Q3..2023Q2:")
print(f"  {'quarter':8s} {'hog_yoy':>8s} {'feed_yoy':>9s} {'SPREAD':>8s} {'gpm_turn':>9s} {'GPM':>6s}  verdict")
for q, r in seg.iterrows():
    hog_says = "UP" if r["hog_yoy"] > 0 else "DN"
    spr_says = "UP" if r["spread_yoy"] > 0 else "DN"
    gpm_real = "UP" if r["gpm_turn"] > 0 else "DN"
    hog_ok = "OK" if hog_says == gpm_real else "WRONG"
    spr_ok = "OK" if spr_says == gpm_real else "WRONG"
    print(f"  {str(q):8s} {r['hog_yoy']:+8.2%} {r['feed_yoy']:+9.2%} {r['spread_yoy']:+8.2%}"
          f" {r['gpm_turn']:+9.3f} {r['GPM_P0']:6.3f}  hog={hog_says}({hog_ok}) spread={spr_says}({spr_ok})")

# ---------- 6. TURN-SIGN agreement: spread vs hog-alone (all history) ----------
print("\n\n" + "=" * 78)
print("TURN-SIGN AGREEMENT across full overlap — does the SPREAD sign match the GPM-turn")
print("sign more often than the hog-alone sign?  (higher = better early-warning)")
print("=" * 78)
for tk in ("DBC", "BAF"):
    for fl in (0, 1):
        m = build(tk, 0.60, feed_lag=fl)
        sub = m[["hog_yoy", "spread_yoy", "gpm_turn"]].dropna()
        if len(sub) < 6:
            print(f"  {tk} feed_lag={fl}: n={len(sub)} short"); continue
        hog_agree = (np.sign(sub["hog_yoy"]) == np.sign(sub["gpm_turn"])).mean()
        spr_agree = (np.sign(sub["spread_yoy"]) == np.sign(sub["gpm_turn"])).mean()
        print(f"  {tk} feed_lag={fl}q (n={len(sub):2d}): hog-alone {hog_agree:.0%}"
              f"   spread {spr_agree:.0%}   delta {spr_agree-hog_agree:+.0%}")

# ---------- 7. WEIGHT SENSITIVITY (is the result an artifact of 60:40?) ----------
print("\n\n" + "=" * 78)
print("WEIGHT SENSITIVITY (DBC, feed_lag=0) — corr(spread_yoy, gpm_turn) by corn:sbm mix")
print("=" * 78)
for w in (0.70, 0.60, 0.50):
    m = build("DBC", w, feed_lag=0)
    sub = m[["spread_yoy", "gpm_turn"]].dropna()
    r, p = spearmanr(sub["spread_yoy"], sub["gpm_turn"])
    agree = (np.sign(sub["spread_yoy"]) == np.sign(sub["gpm_turn"])).mean()
    print(f"  corn:sbm = {w:.0%}:{1-w:.0%}  corr={r:+.3f} (n={len(sub)}, p={p:.2f})  sign-agree={agree:.0%}")

# ---------- 8. NOW read — spread today ----------
print("\n\n" + "=" * 78)
print("NOW READ — what does the hog-FEED spread say for DBC right now?")
print("=" * 78)
m = build("DBC", 0.60, feed_lag=0)
print("\n hog & feed quarterly (latest):")
tail = m[["hog", "hog_yoy", "feed_yoy", "spread_yoy", "GPM_P0", "gpm_turn"]].dropna(
    subset=["hog_yoy", "feed_yoy"]).tail(6)
print(tail.round(3).to_string())
# also raw latest feed & hog (may lead the last GPM quarter)
print("\n latest feed basket (60:40) & hog quarters (may post-date last GPM filing):")
fj = FEED[0.60][["feed", "feed_yoy"]].join(hq[["hog", "hog_yoy"]], how="outer")
fj["spread_yoy"] = fj["hog_yoy"] - fj["feed_yoy"]
print(fj.loc["2025Q1":].round(3).to_string())
