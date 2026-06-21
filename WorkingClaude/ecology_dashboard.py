"""
Ecology Dashboard (AMH proposal #4)
===================================
AMH (Lo): crowds are WISE when diverse, MAD when uniform. Bubbles & crashes =
diversity of opinion collapsing to one side. This gauges the market ECOLOGY along
three axes and tests the core claim that crowd-uniformity extremes precede
reversals (mean-reversion of sentiment).

Axes (daily, liquid ticker_prune universe, causal):
  A. OPPORTUNITY  — cross-sectional return dispersion (wide = stock-picker's
                    market / rich edge set; narrow = macro-driven / crowded)
  B. UNIFORMITY   — breadth extremity |breadth-0.5|*2 (0 balanced/diverse,
                    1 everyone on one side) ; + low dispersion reinforces
  C. SENTIMENT    — directional mood (+euphoria / -panic) from breadth,
                    overbought-minus-oversold, and median PB_z (valuation greed)
  MADNESS = |mood| : distance from neutral, i.e. how far the crowd has herded.
  DIVERGENCE      — price up while breadth weak (late-cycle topping tell).

Validation: forward VNINDEX return by mood decile -> contrarian monotonicity
confirms "uniformity precedes reversal".

Inputs : data/ecology_panel.csv (breadth/disp/sentiment), data/dt5g_vnindex.csv (state+px)
Outputs: data/ecology_dashboard.csv, ecology_dashboard.png, data/ecology_now.md
Run: python ecology_dashboard.py
"""
import sys, os, subprocess
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
ECO = WORKDIR + r"/data/ecology_panel.csv"
STATEF = WORKDIR + r"/data/dt5g_vnindex.csv"

_PROJ = "lithe-record-440915-m9"
_ECO_SQL = '''WITH base AS (
  SELECT t.time, SAFE_DIVIDE(t.Close, NULLIF(t.Close_T1,0))-1 AS ret,
    IF(t.Close>t.MA200,1,0) AS a200, IF(t.Close>t.MA50,1,0) AS a50,
    SAFE_DIVIDE(t.PB-t.PB_MA5Y, NULLIF(t.PB_SD5Y,0)) AS pb_z, t.D_RSI
  FROM tav2_bq.ticker_prune AS t
  WHERE t.time>="2014-01-01" AND t.ticker!="VNINDEX"
    AND COALESCE(t.Price,t.Close)*t.Volume>=1e9 AND t.MA200 IS NOT NULL AND t.Close_T1 IS NOT NULL)
SELECT b.time, COUNT(*) AS n, ROUND(AVG(b.a200),4) AS breadth200, ROUND(AVG(b.a50),4) AS breadth50,
  ROUND(STDDEV(b.ret),5) AS disp, ROUND(APPROX_QUANTILES(b.pb_z,100)[OFFSET(50)],3) AS pbz_med,
  ROUND(AVG(IF(b.D_RSI<0.3,1.0,0)),4) AS pct_oversold, ROUND(AVG(IF(b.D_RSI>0.7,1.0,0)),4) AS pct_overbought
FROM base AS b GROUP BY b.time ORDER BY b.time'''
_DT5G_SQL = '''SELECT s.time, CAST(s.state AS INT64) AS state, v.Close AS vnindex
FROM tav2_bq.vnindex_5state_dt5g_live AS s
JOIN (SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker="VNINDEX") AS v ON s.time=v.time
ORDER BY s.time'''


def refresh_panels():
    for sql, out in [(_ECO_SQL, ECO), (_DT5G_SQL, STATEF)]:
        cmd = (f"bq query --use_legacy_sql=false --project_id={_PROJ} --format=csv "
               f"--max_rows=20000 '{sql}' > '{out.replace(chr(92), '/')}'")
        r = subprocess.run(["bash", "-lc", cmd], capture_output=True, text=True)
        if r.returncode != 0:
            print("[refresh] FAILED:", r.stderr[-800:]); sys.exit(1)
    print("[refresh] ecology_panel + dt5g_vnindex pulled from BQ.")
WIN = 504          # rolling normalization window (~2y), causal
STATE_LBL = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}


def rz(s, win=WIN):
    """Causal rolling z-score."""
    m = s.rolling(win, min_periods=120).mean()
    sd = s.rolling(win, min_periods=120).std()
    return (s - m) / sd


def rpct(s, win=WIN):
    """Causal rolling percentile rank (0-1)."""
    return s.rolling(win, min_periods=120).apply(
        lambda x: (x.iloc[-1] >= x).mean(), raw=False)


def load():
    e = pd.read_csv(ECO, parse_dates=["time"])
    st = pd.read_csv(STATEF, parse_dates=["time"])[["time", "state", "vnindex"]]
    df = e.merge(st, on="time", how="left").sort_values("time").reset_index(drop=True)
    df["state"] = df["state"].ffill()
    df["vnindex"] = df["vnindex"].ffill()
    df["disp_s"] = df["disp"].rolling(10).mean()
    # Axis A: opportunity = dispersion percentile
    df["opportunity"] = rpct(df["disp_s"])
    # Axis B: uniformity = breadth extremity (+ low-dispersion reinforcement)
    df["breadth_extremity"] = (df["breadth200"] - 0.5).abs() * 2
    df["uniformity"] = (df["breadth_extremity"] + (1 - df["opportunity"])) / 2
    # Axis C: directional mood (+euphoria / -panic)
    df["mood"] = (rz(df["breadth200"]) + rz(df["pct_overbought"] - df["pct_oversold"])
                  + rz(df["pbz_med"])) / 3.0
    df["madness"] = df["mood"].abs()
    # price-breadth divergence: index 60d up while breadth below median
    df["idx_ret60"] = df["vnindex"].pct_change(60)
    df["divergence"] = np.where((df["idx_ret60"] > 0) & (df["breadth200"] < 0.5),
                                (0.5 - df["breadth200"]) * np.sign(df["idx_ret60"]), 0.0)
    # forward VNINDEX returns for validation
    df["fwd20"] = df["vnindex"].shift(-20) / df["vnindex"] - 1
    df["fwd60"] = df["vnindex"].shift(-60) / df["vnindex"] - 1
    return df


def validate(df):
    print("\n=== VALIDATION: forward VNINDEX return by MOOD decile (contrarian => uniformity precedes reversal) ===")
    d = df.dropna(subset=["mood", "fwd60"]).copy()
    d["dec"] = pd.qcut(d["mood"], 10, labels=False)
    g = d.groupby("dec").agg(mood=("mood", "mean"),
                             fwd20=("fwd20", "mean"), fwd60=("fwd60", "mean"),
                             win60=("fwd60", lambda x: (x > 0).mean()), n=("fwd60", "size"))
    g["mood"] = g["mood"].round(2); g[["fwd20", "fwd60", "win60"]] = (g[["fwd20", "fwd60", "win60"]] * 100).round(1)
    print(g.to_string())
    lo, hi = g.loc[0], g.loc[9]
    print(f"\n  PANIC (decile 0, mood {lo['mood']:.2f}):    fwd60 = {lo['fwd60']:+.1f}%  win {lo['win60']:.0f}%")
    print(f"  EUPHORIA (decile 9, mood {hi['mood']:.2f}): fwd60 = {hi['fwd60']:+.1f}%  win {hi['win60']:.0f}%")
    spread = lo['fwd60'] - hi['fwd60']
    verdict = ("CONTRARIAN (fade the crowd)" if spread > 1 else
               "PROCYCLICAL (mood persists = momentum); only deep-tail panic bounces" if spread < -1 else
               "FLAT (no market-level edge)")
    print(f"  spread (panic - euphoria) fwd60 = {spread:+.1f}pp  =>  {verdict}")
    print(f"  NOTE: deepest-panic decile-0 ({lo['fwd60']:+.1f}%) > mild-panic deciles 1-3 "
          f"=> capitulation kick lives ONLY in the extreme tail (needs DT5G-CRISIS+washout, per #3)")


def now_block(df):
    r = df.iloc[-1]
    op_p = r["opportunity"]; mood = r["mood"]
    mood_p = (df["mood"].dropna() <= mood).mean()
    lines = []
    lines.append(f"🌊 *Ecology Dashboard* (AMH#4, {r['time'].date()}, DT5G={STATE_LBL.get(r['state'],'?')})")
    lines.append(f"Breadth: {r['breadth200']*100:.0f}% >MA200 | {r['breadth50']*100:.0f}% >MA50  "
                 f"(n={int(r['n'])})")
    lines.append(f"A Opportunity (dispersion pctile): {op_p*100:.0f}%  "
                 f"({'RICH stock-pickers' if op_p>0.6 else 'CROWDED/macro' if op_p<0.4 else 'normal'})")
    lines.append(f"B Uniformity: {r['uniformity']*100:.0f}%  (breadth-extremity {r['breadth_extremity']*100:.0f}%)")
    lines.append(f"C Mood: {mood:+.2f} (pctile {mood_p*100:.0f}%) -> "
                 f"{'EUPHORIA' if mood>0.7 else 'PANIC' if mood<-0.7 else 'neutral'}  | "
                 f"madness {r['madness']:.2f} | pb_z med {r['pbz_med']:+.2f}")
    div = r["divergence"]
    if div > 0.05:
        lines.append(f"⚠️ DIVERGENCE: index up 60d but breadth only {r['breadth200']*100:.0f}% "
                     f"(narrow leadership, late-cycle tell)")
    return "\n".join(lines)


def main():
    if "--refresh" in sys.argv:
        refresh_panels()
    df = load()
    print(f"Ecology panel: {df['time'].min().date()} -> {df['time'].max().date()} | {len(df)} sessions")
    validate(df)
    block = now_block(df)
    print("\n--- NOW (data/ecology_now.md) ---\n" + block)
    with open(WORKDIR + r"/data/ecology_now.md", "w", encoding="utf-8") as f:
        f.write(block)
    df.to_csv(WORKDIR + r"/data/ecology_dashboard.csv", index=False)

    # ---- plot ----
    fig, axes = plt.subplots(4, 1, figsize=(14, 12), sharex=True)
    ax = axes[0]
    ax.plot(df["time"], df["vnindex"], color="black", lw=1)
    ax.set_yscale("log"); ax.set_ylabel("VNINDEX"); ax.set_title("Ecology Dashboard (AMH #4)")
    ax.grid(alpha=0.3)
    ax = axes[1]
    ax.plot(df["time"], df["breadth200"], color="tab:blue", lw=1, label="breadth >MA200")
    ax.plot(df["time"], df["breadth50"], color="tab:cyan", lw=0.7, alpha=0.7, label="breadth >MA50")
    ax.axhline(0.5, color="gray", ls="--", lw=0.8); ax.set_ylabel("breadth"); ax.legend(fontsize=8); ax.grid(alpha=0.3)
    ax = axes[2]
    ax.plot(df["time"], df["opportunity"], color="tab:green", lw=1, label="A: opportunity (disp pctile)")
    ax.plot(df["time"], df["uniformity"], color="tab:red", lw=1, label="B: uniformity")
    ax.set_ylabel("A / B"); ax.legend(fontsize=8); ax.grid(alpha=0.3)
    ax = axes[3]
    ax.plot(df["time"], df["mood"], color="tab:purple", lw=1, label="C: mood (+euph/-panic)")
    ax.axhline(0, color="gray", lw=0.8)
    ax.fill_between(df["time"], 0, df["mood"], where=(df["mood"] > 0), color="tab:orange", alpha=0.2)
    ax.fill_between(df["time"], 0, df["mood"], where=(df["mood"] < 0), color="tab:blue", alpha=0.2)
    ax.set_ylabel("mood"); ax.legend(fontsize=8); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(WORKDIR + r"/ecology_dashboard.png", dpi=110)
    print("\nSaved: ecology_dashboard.png | data/ecology_dashboard.csv | data/ecology_now.md")


if __name__ == "__main__":
    main()
