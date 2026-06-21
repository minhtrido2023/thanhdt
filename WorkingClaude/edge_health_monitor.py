"""
Edge Health Monitor (AMH proposal #1)  -- refined
=================================================
Tracks rolling cross-sectional Information Coefficient (IC) of each 8L lens /
signal over time AND per super-sector, to detect whether an edge is in the
*efficiency* (dead) or *inefficiency* (alive) phase of the Adaptive-Markets
cycle -- alive, fading, dead, or sign-flipped (crowded out / regime-inverted).

IC = Spearman rank-corr between signal[T] (cross-section, liquid ticker_prune)
and forward 3-month return (clean LEAD(Close), NOT corrupted profit_*).

Refinements vs v1:
  * per-sector IC (super-sector mapped from ICB_Code first digit, 8L-aligned)
  * alert thresholds -> RED (flipped) / ORANGE (decayed) actionable list
  * daily-cadence artifacts: data/edge_health_status.json + edge_health_block.md
    (compact block for the 18:00 Telegram / daily report to surface)
  * --refresh re-pulls the monthly panel from BQ (idempotent, daily-safe;
    forward-3M IC only changes when a new month realizes -> cheap recompute)

Run:  python edge_health_monitor.py            # recompute from cached panel
      python edge_health_monitor.py --refresh  # re-pull panel from BQ first
"""
import os, sys, json, subprocess
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
PANEL = WORKDIR + r"/data/edge_panel.csv"
SQLFILE = WORKDIR + r"/data/edge_panel.sql"
PRIMARY_FWD = "fwd_3m"
MIN_NAMES = 25          # min cross-section for ALL-universe monthly IC
MIN_NAMES_SEC = 18      # min cross-section for a per-sector monthly IC
ROLL = 12               # rolling window (months)
RECENT = 12             # "recent" window for decay verdict (months)
T_SIG = 2.0             # |t| threshold for "robust" edge
MAG_MIN = 0.015         # min |recent IC| magnitude to call a flip meaningful

# signal -> (a-priori expected sign, label, drop-exact-zero[bank placeholder], quality-only)
SIGNALS = {
    "pb_z":      (-1, "Val: PB_z (cheap vs own 5Y)", False, False),
    "PB":        (-1, "Val: PB",                     False, False),
    "PE":        (-1, "Val: PE",                     False, False),
    "ROIC5Y":    (+1, "Qual: ROIC 5Y",              True,  True),
    "FSCORE":    (+1, "Qual: F-Score",              False, True),
    "ROE_Min5Y": (+1, "Qual: ROE floor 5Y",         True,  True),
    "mom_200":   ( 0, "Mom: Close/MA200",           False, False),
    "D_RSI":     ( 0, "Mom: daily RSI",             False, False),
    "D_CMF":     (+1, "Flow: CMF",                  False, False),
    "C_L1M":     ( 0, "Pos: Close/Low-1M",          False, False),
}

PANEL_SQL = '''
WITH daily AS (
  SELECT
    t.time, t.ticker, t.ICB_Code AS icb,
    SAFE_DIVIDE(LEAD(t.Close, 60) OVER w, t.Close) - 1 AS fwd_3m,
    SAFE_DIVIDE(LEAD(t.Close, 20) OVER w, t.Close) - 1 AS fwd_1m,
    COALESCE(t.Price, t.Close) * t.Volume AS liq,
    t.PB, t.PE,
    SAFE_DIVIDE(t.PB - t.PB_MA5Y, NULLIF(t.PB_SD5Y, 0)) AS pb_z,
    t.ROIC5Y, t.FSCORE, t.ROE_Min5Y, t.D_RSI, t.D_CMF,
    SAFE_DIVIDE(t.Close, NULLIF(t.MA200, 0)) - 1 AS mom_200,
    t.C_L1M,
    ROW_NUMBER() OVER (PARTITION BY t.ticker, EXTRACT(YEAR FROM t.time),
                       EXTRACT(MONTH FROM t.time) ORDER BY t.time) AS rn_month
  FROM tav2_bq.ticker_prune AS t
  WINDOW w AS (PARTITION BY t.ticker ORDER BY t.time)
)
SELECT d.time, d.ticker, d.icb, d.fwd_3m, d.fwd_1m, d.liq, d.pb_z, d.PB, d.PE,
       d.ROIC5Y, d.FSCORE, d.ROE_Min5Y, d.D_RSI, d.D_CMF, d.mom_200, d.C_L1M
FROM daily AS d
WHERE d.rn_month = 1 AND d.time >= "2014-01-01" AND d.fwd_3m IS NOT NULL
  AND d.ticker != "VNINDEX" AND d.liq >= 1e9
ORDER BY d.time, d.ticker
'''


CAPF = WORKDIR + r"/data/bt_capitulation_STRONG.csv"
CARVE_BY_HEALTH = {"HEALTHY": 0.70, "FADING": 0.45, "NEGATIVE": 0.20}  # max capit carve (V6 levered)


def spearman(a, b):
    ra = pd.Series(a).rank(); rb = pd.Series(b).rank()
    return ra.corr(rb)


def capit_edge_health(k_recent=4):
    """Monitor the capitulation sleeve's edge (V6 Tứ Trụ leans on it harder when levered).
    Compares last-k STRONG-event basket returns vs full history -> verdict + a recommended
    MAX capit carve. The allocator should not raise capit carve above this until edge confirms."""
    try:
        ev = pd.read_csv(CAPF)
    except Exception:
        return None
    r = ev["FIX60_ret"].astype(float)
    full_mean = r.mean(); full_hit = (r > 0).mean()
    rec = r.tail(k_recent); rec_mean = rec.mean(); rec_hit = (rec > 0).mean()
    last = r.iloc[-1]
    # verdict: needs recent positive mean + majority hit, and last event not a deep miss
    if rec_mean >= 0.5 * full_mean and rec_hit >= 0.5 and last > -5:
        verdict = "HEALTHY"
    elif rec_mean > 0 and rec_hit >= 0.5:
        verdict = "FADING"
    else:
        verdict = "NEGATIVE"
    return dict(n=len(r), full_mean=round(full_mean, 1), full_hit=round(full_hit, 2),
                rec_mean=round(rec_mean, 1), rec_hit=round(rec_hit, 2), last=round(last, 1),
                verdict=verdict, max_carve=CARVE_BY_HEALTH[verdict])


def lag_edge_health():
    """LAG/PEAD edge health (half of the V2.3 book; w_LAG=.65 live in V2.3A).
    Rebuilds the e3 cohort exactly as the LAG book does (NP_R>=15, prior_n_good>=4,
    pa_HL3>=5), entry T+5 after release, measures the book's actual hold horizon
    (25 sessions), then trailing-12M mean/win at the latest COMPLETE event.
    Sources are the daily-refreshed caches (refresh_lagged_caches.py step [0/6]),
    so this line stays live without extra BQ cost. Series inherently lags ~5 weeks
    (events complete 25 sessions after entry).
    Pre-committed thresholds (research 2026-06-10, lag edge-cycle: trough=3rd pctile,
    recovery = 12M-mean > +4-5%; 5/5 troughs recovered >= +3.9% within 6M):
      mean12 >= +4%        HEALTHY  -> w_LAG .65 OK
      +1..+4%              NEUTRAL  -> giu w_LAG, khong tang
      0..+1%               TROUGH   -> khong tang w_LAG; von moi paper-trade
      < 0%                 NEGATIVE -> ha w_LAG .65->.50; <0 keo dai 3 thang -> treo entry LAG moi
    Writes the rolling series to data/lag_edge_health.csv (auto-updated)."""
    import pickle
    try:
        with open(WORKDIR + r"/data/earnings_px.pkl", "rb") as f: px = pickle.load(f)
        px["time"] = pd.to_datetime(px["time"])
        pxc = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
        ev = pd.read_csv(WORKDIR + r"/data/earnings_events_classified.csv", parse_dates=["Release_Date"])
    except Exception as e:
        print(f"[lag-edge] skipped: {e}")
        return None
    ev = ev.sort_values(["ticker", "Release_Date"]).reset_index(drop=True)
    LN2 = np.log(2); HL = 3.0
    ev["prior_n_good"] = 0; ev["pa_HL3"] = np.nan
    for tk, g in ev.groupby("ticker"):
        hist = []
        for ri in g.index.tolist():
            row = ev.loc[ri]; cur = row["Release_Date"]
            ev.at[ri, "prior_n_good"] = len(hist)
            if hist:
                da = pd.to_datetime([d for d, _ in hist]); pa = np.array([p for _, p in hist])
                wts = np.exp(-LN2 * ((cur - da).days.values / 365.25) / HL)
                ev.at[ri, "pa_HL3"] = (pa * wts).sum() / wts.sum() if wts.sum() > 0 else np.nan
            if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]):
                hist.append((cur, row["post_ret"]))
    e3 = ev[(ev["NP_R"] >= 15) & (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5)]
    idx = pxc.index
    rows = []
    for _, r in e3.iterrows():
        tk = r["ticker"]
        if tk not in pxc.columns: continue
        pos = idx.searchsorted(r["Release_Date"], side="right") - 1 + 5   # entry T+5
        if pos < 0 or pos + 25 >= len(idx): continue                      # need complete 25-session hold
        p0, p1 = pxc.iloc[pos][tk], pxc.iloc[pos + 25][tk]
        if pd.isna(p0) or pd.isna(p1) or p0 <= 0: continue
        rows.append({"entry": idx[pos], "ret": (p1 / p0 - 1) * 100})
    if len(rows) < 20:
        print("[lag-edge] too few complete events"); return None
    d = pd.DataFrame(rows).sort_values("entry").reset_index(drop=True)
    d["mean12"] = np.nan; d["win12"] = np.nan; d["n12"] = np.nan
    for i in range(len(d)):
        w = d[(d["entry"] > d.at[i, "entry"] - pd.Timedelta(days=365)) & (d["entry"] <= d.at[i, "entry"])]["ret"]
        d.at[i, "mean12"], d.at[i, "win12"], d.at[i, "n12"] = w.mean(), (w > 0).mean() * 100, len(w)
    d.to_csv(WORKDIR + r"/data/lag_edge_health.csv", index=False)
    m12, w12, n12 = d["mean12"].iloc[-1], d["win12"].iloc[-1], int(d["n12"].iloc[-1])
    pctl = (d["mean12"] <= m12).mean() * 100
    # months-below-zero streak (calendar months whose last reading < 0)
    mo = d.set_index("entry")["mean12"].resample("ME").last().dropna()
    neg_streak = 0
    for v in mo.values[::-1]:
        if v < 0: neg_streak += 1
        else: break
    if n12 < 8:        verdict, act = "THIN", "mau qua mong, khong ket luan"
    elif m12 >= 4.0:   verdict, act = "HEALTHY", "w_LAG .65 OK"
    elif m12 >= 1.0:   verdict, act = "NEUTRAL", "giu w_LAG, khong tang"
    elif m12 >= 0.0:   verdict, act = "TROUGH", "khong tang w_LAG; von moi paper-trade"
    else:
        verdict = "NEGATIVE"
        act = ("HA w_LAG .65->.50 + treo entry LAG moi (am %d thang lien tiep)" % neg_streak
               if neg_streak >= 3 else "canh bao: ha w_LAG .65->.50 neu keo dai 3 thang")
    return dict(mean12=round(float(m12), 2), win12=round(float(w12), 1), n12=n12,
                pctl=round(float(pctl), 0), asof=str(d["entry"].iloc[-1].date()),
                neg_streak=neg_streak, verdict=verdict, act=act)


def refresh_panel():
    """Re-pull the monthly panel from BQ via bash (uses .bashrc-configured bq)."""
    with open(SQLFILE, "w") as f:
        f.write(PANEL_SQL)
    cmd = ("bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 "
           "--format=csv --max_rows=200000 \"$(cat '%s')\" > '%s'"
           % (SQLFILE.replace('\\', '/'), PANEL.replace('\\', '/')))
    print("[refresh] pulling panel from BQ ...")
    r = subprocess.run(["bash", "-lc", cmd], capture_output=True, text=True)
    if r.returncode != 0:
        print("[refresh] FAILED:\n", r.stderr[-1500:]); sys.exit(1)
    print("[refresh] done.")


def map_sector(icb):
    try:
        c = int(float(icb))
    except (ValueError, TypeError):
        return "OTHER"
    d = c // 1000
    if d == 8:
        if 8350 <= c <= 8359:   return "BANK"
        if 8630 <= c <= 8639:   return "REALEST"
        return "FINSVC"
    if d in (1, 2):  return "CYCLICAL"     # materials + industrials
    if d in (3, 5):  return "CONSUMER"     # consumer goods + services
    if d == 7:       return "UTILITY"
    if d == 4:       return "HEALTH"
    if d == 6:       return "TELECOM"
    if d == 9:       return "TECH"
    return "OTHER"


def load_panel():
    df = pd.read_csv(PANEL, parse_dates=["time"])
    df = df[df[PRIMARY_FWD].notna()].copy()
    lo, hi = df[PRIMARY_FWD].quantile([0.005, 0.995])
    df[PRIMARY_FWD] = df[PRIMARY_FWD].clip(lo, hi)
    df["sector"] = df["icb"].map(map_sector)
    df["ym"] = df["time"].dt.to_period("M")
    return df


def monthly_ic(df, col, drop_zero, min_names):
    out = {}
    for ym, g in df.groupby("ym"):
        s = g[[col, PRIMARY_FWD]].dropna()
        if drop_zero:
            s = s[s[col] != 0.0]
        if len(s) < min_names or s[col].nunique() < 5:
            continue
        ic = spearman(s[col].values, s[PRIMARY_FWD].values)
        if ic is not None and np.isfinite(ic):
            out[ym.to_timestamp()] = ic
    return pd.Series(out).sort_index()


def classify(full, recent, tstat):
    if not np.isfinite(tstat) or abs(tstat) < T_SIG:
        return "WEAK"
    if np.sign(recent) != np.sign(full) and abs(recent) >= MAG_MIN:
        return "FLIPPED"
    ratio = abs(recent) / abs(full) if full else 0.0
    if ratio < 0.33:   return "DECAYED"
    if ratio < 0.66:   return "FADING"
    if ratio > 1.30:   return "STRENGTH"
    return "HEALTHY"


def edge_row(ic):
    full = ic.mean(); n = len(ic)
    sd = ic.std(ddof=1)
    tstat = full / (sd / np.sqrt(n)) if sd and sd > 0 else 0.0
    recent = ic.tail(RECENT).mean()
    return dict(n=n, full=full, recent=recent, tstat=tstat,
                verdict=classify(full, recent, tstat))


def main():
    if "--refresh" in sys.argv or not os.path.exists(PANEL):
        refresh_panel()
    df = load_panel()
    last_month = df["ym"].max()
    secs = ["ALL"] + [s for s in ["CYCLICAL", "CONSUMER", "REALEST", "FINSVC",
                                  "BANK", "UTILITY"]
                      if (df["sector"] == s).sum() > 0]
    print(f"Panel: {len(df):,} obs | {df['ym'].nunique()} months | "
          f"-> {last_month} | {df['ticker'].nunique()} tickers")
    sec_counts = df.groupby("sector")["ticker"].nunique().sort_values(ascending=False)
    print("Sector universe (distinct tickers):", dict(sec_counts))

    # ---- compute IC: ALL + per sector ----
    all_ic = {}            # for plotting (ALL scope)
    matrix = []            # (signal, scope) rows
    for col, (prior, label, dz, qonly) in SIGNALS.items():
        for sc in secs:
            sub = df if sc == "ALL" else df[df["sector"] == sc]
            # skip quality signals for financial sectors (meaningless)
            if qonly and sc in ("BANK", "FINSVC"):
                continue
            mn = MIN_NAMES if sc == "ALL" else MIN_NAMES_SEC
            ic = monthly_ic(sub, col, dz, mn)
            if len(ic) < 18:   # not enough months for a verdict
                continue
            if sc == "ALL":
                all_ic[col] = ic
            r = edge_row(ic)
            matrix.append(dict(signal=col, label=label, scope=sc, prior=prior, **r))

    mdf = pd.DataFrame(matrix)
    mdf["full"] = mdf["full"].round(4); mdf["recent"] = mdf["recent"].round(4)
    mdf["tstat"] = mdf["tstat"].round(2)

    # ---- alerts ----
    robust = mdf[mdf["tstat"].abs() >= T_SIG]
    reds = robust[robust["verdict"] == "FLIPPED"]
    oranges = robust[robust["verdict"] == "DECAYED"]
    greens = robust[robust["verdict"] == "STRENGTH"]

    # ---- console output ----
    pd.set_option("display.width", 220, "display.max_columns", 30)
    print("\n=== ALL-UNIVERSE edge health (fwd-3M IC) ===")
    a = mdf[mdf["scope"] == "ALL"].sort_values("tstat", key=lambda s: s.abs(), ascending=False)
    print(a[["signal", "label", "n", "full", "recent", "tstat", "verdict"]].to_string(index=False))

    print("\n=== PER-SECTOR IC matrix: recent-12M IC (verdict) ===")
    piv_r = mdf.pivot_table(index="signal", columns="scope", values="recent", aggfunc="first")
    piv_v = mdf.pivot_table(index="signal", columns="scope", values="verdict", aggfunc="first")
    order = [c for c in ["ALL", "CYCLICAL", "CONSUMER", "REALEST", "FINSVC", "BANK", "UTILITY"] if c in piv_r.columns]
    print(piv_r[order].round(3).to_string())

    print("\n=== 🔴 RED (FLIPPED — crowded out / regime-inverted) ===")
    print(reds[["signal", "scope", "full", "recent", "tstat"]].to_string(index=False) if len(reds) else "  (none)")
    print("\n=== 🟠 ORANGE (DECAYED — edge faded to <33%) ===")
    print(oranges[["signal", "scope", "full", "recent", "tstat"]].to_string(index=False) if len(oranges) else "  (none)")
    print("\n=== 🟢 STRENGTHENING ===")
    print(greens[["signal", "scope", "full", "recent", "tstat"]].to_string(index=False) if len(greens) else "  (none)")

    # ---- write artifacts ----
    mdf.to_csv(WORKDIR + r"/data/edge_health_matrix.csv", index=False)
    pd.DataFrame(all_ic).sort_index().to_csv(WORKDIR + r"/data/edge_health_ic.csv")

    status = {
        "as_of_month": str(last_month),
        "n_obs": int(len(df)), "n_months": int(df["ym"].nunique()),
        "reds": reds[["signal", "scope", "full", "recent"]].to_dict("records"),
        "oranges": oranges[["signal", "scope", "full", "recent"]].to_dict("records"),
        "strengthening": greens[["signal", "scope", "full", "recent"]].to_dict("records"),
    }
    with open(WORKDIR + r"/data/edge_health_status.json", "w") as f:
        json.dump(status, f, indent=2)

    # ---- compact markdown block for daily report ----
    def fmt(rs):
        return ", ".join(f"{r['signal']}·{r['scope']}({r['full']:+.3f}→{r['recent']:+.3f})" for r in rs) or "—"
    block = []
    block.append(f"🧭 *Edge Health* (AMH#1, fwd-3M IC, as of {last_month})")
    block.append(f"🔴 FLIPPED: {fmt(status['reds'])}")
    block.append(f"🟠 DECAYED: {fmt(status['oranges'])}")
    block.append(f"🟢 STRENGTH: {fmt(status['strengthening'])}")
    # one-line snapshot of the headline families (ALL scope)
    al = mdf[mdf["scope"] == "ALL"].set_index("signal")
    def cell(sig):
        if sig in al.index:
            return f"{sig} {al.loc[sig, 'recent']:+.3f}[{al.loc[sig, 'verdict']}]"
        return f"{sig} n/a"
    block.append("Snapshot: " + " | ".join(cell(s) for s in ["PE", "PB", "mom_200", "ROE_Min5Y", "FSCORE"]))
    # capit-edge health (gates the V6 Tứ Trụ levered capit carve)
    ce = capit_edge_health()
    if ce:
        block.append(f"⚔️ Capit edge: {ce['verdict']} (recent{4} {ce['rec_mean']:+.1f}%/hit{ce['rec_hit']:.0%} "
                     f"vs full {ce['full_mean']:+.1f}%/{ce['full_hit']:.0%}, last {ce['last']:+.1f}%) "
                     f"→ max capit carve {ce['max_carve']:.0%}")
        print(f"\n=== CAPIT-EDGE HEALTH (gates V6 levered capit carve) ===\n{ce}")
    # LAG/PEAD-edge health (half the V2.3 book; thresholds pre-committed 2026-06-10)
    le = lag_edge_health()
    if le:
        block.append(f"📮 LAG edge: {le['verdict']} (12M {le['mean12']:+.2f}%/win {le['win12']:.0f}%, "
                     f"n={le['n12']}, pctile {le['pctl']:.0f}, asof {le['asof']}) → {le['act']}")
        print(f"\n=== LAG-EDGE HEALTH (gates w_LAG in V2.3A) ===\n{le}")
    # momentum action hint: half the BAL book — pre-committed response when IC flips
    try:
        mom_v = al.loc["mom_200", "verdict"] if "mom_200" in al.index else None
        if mom_v == "FLIPPED":
            block.append("📉 Momentum FLIPPED → không nới slot/size momentum; "
                         "dormant fix sẵn: EXBULL-suppression (validated +0.3pp FULL, 2025+ +1.6pp, chưa live)")
    except Exception:
        pass
    md = "\n".join(block)
    with open(WORKDIR + r"/data/edge_health_block.md", "w", encoding="utf-8") as f:
        f.write(md)
    print("\n--- daily-report block (data/edge_health_block.md) ---\n" + md)

    # ---- plot ALL-scope rolling IC grid ----
    cols = list(all_ic.keys())
    ncol = 2; nrow = int(np.ceil(len(cols) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(15, 2.9 * nrow), sharex=True)
    axes = axes.flatten()
    for i, col in enumerate(cols):
        ax = axes[i]; s = all_ic[col]; roll = s.rolling(ROLL).mean()
        ax.axhline(0, color="black", lw=0.8)
        ax.axhline(s.mean(), color="tab:green", ls="--", lw=1, label=f"full={s.mean():+.3f}")
        ax.plot(s.index, s.values, color="lightgray", lw=0.7, alpha=0.7)
        ax.plot(roll.index, roll.values, color="tab:blue", lw=1.8, label=f"roll-{ROLL}m")
        ax.fill_between(roll.index, 0, roll.values, where=(roll.values >= 0), color="tab:green", alpha=0.15)
        ax.fill_between(roll.index, 0, roll.values, where=(roll.values < 0), color="tab:red", alpha=0.15)
        ax.set_title(SIGNALS[col][1], fontsize=9); ax.legend(fontsize=7, loc="upper left"); ax.tick_params(labelsize=7)
    for j in range(len(cols), len(axes)):
        axes[j].axis("off")
    fig.suptitle("Edge Health Monitor — rolling 12M cross-sectional IC vs fwd-3M (ALL universe)", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    fig.savefig(WORKDIR + r"/edge_health_ic.png", dpi=110)
    print("\nSaved: edge_health_ic.png | data/{edge_health_matrix,edge_health_ic,edge_health_status}.* | edge_health_block.md")


if __name__ == "__main__":
    main()
