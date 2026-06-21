#!/usr/bin/env python3
"""
universe_scan.py  (Phase 5b)
=============================
Load saved RF model -> query latest BQ data -> screen all ~1,272 tickers
Output: universe_scored.csv + universe_scan.png
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile, pickle
from io import StringIO
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT  = "lithe-record-440915-m9"
BQ_BIN   = r"bq"
MODEL_F  = "data/entry_quality_model.pkl"

DARK_BG="#0f1117"; PANEL_BG="#1a1d27"; GRID_CLR="#2a2d3a"; TEXT_CLR="#e0e0e0"
BLUE="#4fa3e0"; GREEN="#4ecb71"; RED="#e05c5c"; YELLOW="#f0c060"
ORANGE="#f0904a"; PURPLE="#b57bee"; TEAL="#4ecbbb"; CYAN="#4ecbee"
plt.rcParams.update({
    "figure.facecolor":DARK_BG,"axes.facecolor":PANEL_BG,"axes.edgecolor":GRID_CLR,
    "axes.labelcolor":TEXT_CLR,"xtick.color":TEXT_CLR,"ytick.color":TEXT_CLR,
    "text.color":TEXT_CLR,"grid.color":GRID_CLR,"grid.linestyle":"--","grid.alpha":0.4,
    "font.family":"DejaVu Sans",
})

# ── BQ HELPER ────────────────────────────────────────────────────────────────
def bq_query(sql, label=""):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8') as f:
        f.write(sql); tmppath = f.name
    try:
        cmd = (f'type "{tmppath}" | "{BQ_BIN}" query --use_legacy_sql=false '
               f'--project_id={PROJECT} --format=csv --max_rows=10000000')
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600, shell=True)
    finally:
        try: os.unlink(tmppath)
        except: pass
    if r.returncode != 0:
        print(f"  [BQ ERROR] {label}: {(r.stdout or r.stderr)[:400]}")
        return None
    txt = r.stdout.strip()
    if not txt: return pd.DataFrame()
    try: return pd.read_csv(StringIO(txt))
    except: return pd.DataFrame()

# ── LOAD MODEL ───────────────────────────────────────────────────────────────
print("Loading model ...")
with open(MODEL_F, "rb") as f:
    obj = pickle.load(f)
rf       = obj["model"]
FEATURES = obj["features"]
print(f"  {len(FEATURES)} features loaded")

# ── FETCH LATEST BQ DATA ─────────────────────────────────────────────────────
print("Fetching latest universe data from BQ ...")
sql = """
SELECT
    t.ticker, t.time,
    t.Close, t.Open,
    t.D_RSI, t.D_MACDdiff, t.D_CMF,
    t.MA10, t.MA50, t.MA200,
    t.PE, t.PB, t.PCF,
    t.ROE5Y, t.ROE_Min3Y, t.ROE_Min5Y,
    t.ROIC5Y, t.ROIC_Min3Y,
    t.FSCORE,
    t.NP_P0, t.NP_P1, t.NP_P4,
    t.CF_OA_5Y, t.OShares,
    t.Risk_Rating,
    t.HI_3M_T1, t.LO_3M_T1,
    t.D_RSI_Max3M, t.D_RSI_Max1W, t.D_RSI_T1W,
    t.Volume, t.Volume_1M, t.Volume_3M_P50,
    t.C_L1W, t.VAP1M, t.VAP3M,
    t.PE_MA5Y, t.PE_SD5Y, t.PB_MA5Y, t.PB_SD5Y,
    t.Sup_1Y, t.Res_1Y,
    t.ICB_Code
FROM tav2_bq.ticker_1m AS t
WHERE t.time >= DATE_SUB(
        (SELECT MAX(t2.time) FROM tav2_bq.ticker_1m AS t2),
        INTERVAL 7 DAY)
  AND t.time <= (SELECT MAX(t2.time) FROM tav2_bq.ticker_1m AS t2)
  AND t.D_RSI IS NOT NULL
ORDER BY t.ticker, t.time DESC
"""
df = bq_query(sql, "universe")
if df is None or df.empty:
    raise RuntimeError("No BQ data returned")

df["time"] = pd.to_datetime(df["time"])
df = df.sort_values("time").groupby("ticker").last().reset_index()
latest_date = df["time"].max().date()
print(f"  {len(df):,} tickers | latest date: {latest_date}")

# ── FEATURE ENGINEERING ───────────────────────────────────────────────────────
print("Engineering features ...")
df["pe_vs_hist"]    = df["PE"]  / df["PE_MA5Y"].clip(lower=0.5)
df["pb_vs_hist"]    = df["PB"]  / df["PB_MA5Y"].clip(lower=0.1)
df["pe_z_score"]    = (df["PE"] - df["PE_MA5Y"]) / df["PE_SD5Y"].clip(lower=0.1)
df["pb_z_score"]    = (df["PB"] - df["PB_MA5Y"]) / df["PB_SD5Y"].clip(lower=0.01)
df["np_growth_1q"]  = df["NP_P0"] / df["NP_P1"].replace(0, np.nan)
df["np_growth_1y"]  = df["NP_P0"] / df["NP_P4"].replace(0, np.nan)
df["cf_yield"]      = (df["CF_OA_5Y"] / df["OShares"].clip(lower=1)
                       / df["Close"].clip(lower=1)) * 100
df["price_vs_ma200"]= df["Close"] / df["MA200"].clip(lower=1)
df["price_vs_ma50"] = df["Close"] / df["MA50"].clip(lower=1)
df["ma10_vs_ma200"] = df["MA10"]  / df["MA200"].clip(lower=1)
df["vol_ratio"]     = df["Volume"] / df["Volume_1M"].clip(lower=1)
df["vol_vs_p50"]    = df["Volume"] / df["Volume_3M_P50"].clip(lower=1)
df["close_vs_lo"]   = df["Close"] / df["LO_3M_T1"].clip(lower=1)
df["close_vs_vap1m"]= df["Close"] / df["VAP1M"].clip(lower=1)
df["rsi_vs_max3m"]  = df["D_RSI"] / df["D_RSI_Max3M"].clip(lower=0.01)
df["rsi_vs_max1w"]  = df["D_RSI"] / df["D_RSI_Max1W"].clip(lower=0.01)
df["rsi_momentum"]  = df["D_RSI"] - df["D_RSI_T1W"]
df["macd_momentum"] = df["D_MACDdiff"]
df["volatility"]    = df["HI_3M_T1"] / df["LO_3M_T1"].clip(lower=1)
df["strat_tier"]    = 2  # neutral for universe scan

# ── SCORE ────────────────────────────────────────────────────────────────────
print("Scoring ...")
X = pd.DataFrame(index=df.index, columns=FEATURES, dtype=float)
for f in FEATURES:
    if f in df.columns:
        X[f] = df[f].values
    else:
        X[f] = np.nan
X = X.replace([np.inf, -np.inf], np.nan).fillna(0.0)
df["score"] = rf.predict_proba(X)[:, 1]
print(f"  Score range: {df['score'].min():.3f} - {df['score'].max():.3f}  |  "
      f"median: {df['score'].median():.3f}")

# ── SCREENS ──────────────────────────────────────────────────────────────────
# Screen A: High conviction — good fundamentals + positive momentum + RSI not overbought
screen_A = df[
    (df["score"] >= 0.55) &
    (df["D_RSI"] < 0.55) &
    (df["D_MACDdiff"] > 0) &
    (df["np_growth_1y"] > 1.10)
].sort_values("score", ascending=False)

# Screen B: Quality + positive technicals (slightly looser)
screen_B = df[
    (df["score"] >= 0.50) &
    (df["D_RSI"] < 0.62) &
    (df["D_MACDdiff"] > 0) &
    (df["FSCORE"] > 4) &
    (df["ROE_Min3Y"] > 0.06)
].sort_values("score", ascending=False)

# Screen C: Deep value — very cheap vs history + good quality floor
screen_C = df[
    (df["score"] >= 0.50) &
    (df["pe_vs_hist"] < 0.80) &
    (df["pb_vs_hist"] < 0.85) &
    (df["ROE_Min3Y"] > 0.08) &
    (df["FSCORE"] > 4)
].sort_values("score", ascending=False)

print(f"\n{'='*70}")
print(f"SCREEN A  Score>=0.55 + RSI<0.55 + MACDdiff>0 + NP_YoY>10%")
print(f"{'='*70}")
print(f"  {len(screen_A)} tickers matched\n")
cols_a = ["ticker","score","D_RSI","D_MACDdiff","D_CMF",
          "np_growth_1y","ROE_Min3Y","ROE5Y","ROIC5Y","FSCORE","PE","PB","ICB_Code"]
avail_a = [c for c in cols_a if c in screen_A.columns]
pd.set_option("display.float_format", "{:.3f}".format)
pd.set_option("display.max_columns", 20)
pd.set_option("display.width", 160)
print(screen_A[avail_a].head(30).to_string(index=False))

print(f"\n{'='*70}")
print(f"SCREEN B  Score>=0.50 + RSI<0.62 + MACDdiff>0 + FSCORE>4 + ROE_Min3Y>6%")
print(f"{'='*70}")
print(f"  {len(screen_B)} tickers matched\n")
cols_b = ["ticker","score","D_RSI","D_MACDdiff","D_CMF",
          "FSCORE","ROE_Min3Y","ROIC5Y","PE","PB","np_growth_1y","ICB_Code"]
avail_b = [c for c in cols_b if c in screen_B.columns]
print(screen_B[avail_b].head(30).to_string(index=False))

print(f"\n{'='*70}")
print(f"SCREEN C  Score>=0.50 + PE<80% hist + PB<85% hist + ROE_Min3Y>8% + FSCORE>4")
print(f"{'='*70}")
print(f"  {len(screen_C)} tickers matched\n")
cols_c = ["ticker","score","pe_vs_hist","pb_vs_hist","D_RSI","D_MACDdiff",
          "ROE_Min3Y","ROIC5Y","FSCORE","PE","PB","ICB_Code"]
avail_c = [c for c in cols_c if c in screen_C.columns]
print(screen_C[avail_c].head(30).to_string(index=False))

# Grade D holds to watch / consider exiting
print(f"\n{'='*70}")
print(f"ACTIVE HOLDS — Grade D (low quality, consider reviewing)")
print(f"{'='*70}")
hold = pd.read_csv("data/live_scored.csv")
grade_d = hold[hold["grade"]=="D"].sort_values("score")
print(f"  {len(grade_d)} positions:\n")
cols_d = ["filter","ticker","time","score","D_RSI","D_MACDdiff","ROE_Min3Y","pe_vs_hist","strat_tier"]
avail_d = [c for c in cols_d if c in grade_d.columns]
print(grade_d[avail_d].to_string(index=False))

# ── SAVE ─────────────────────────────────────────────────────────────────────
df.sort_values("score", ascending=False).to_csv("data/universe_scored.csv", index=False)
screen_A.to_csv("data/screen_A.csv", index=False)
screen_B.to_csv("data/screen_B.csv", index=False)
print(f"\nSaved: universe_scored.csv | screen_A.csv | screen_B.csv")

# ── CHART ────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(22, 14), facecolor=DARK_BG)
fig.suptitle(
    f"Universe Scan  |  {len(df):,} tickers  |  Latest: {latest_date}  |  "
    f"Screen A: {len(screen_A)}  |  Screen B: {len(screen_B)}  |  Screen C: {len(screen_C)}",
    color=TEXT_CLR, fontsize=13, fontweight="bold", y=0.995)

# P1: Score distribution
ax = axes[0,0]
bins_u = np.arange(0.1, 0.96, 0.03)
ax.hist(df["score"], bins=bins_u, color=PURPLE, alpha=0.55, label=f"All ({len(df)})")
if len(screen_A)>0: ax.hist(screen_A["score"], bins=bins_u, color=GREEN, alpha=0.85, label=f"Screen A ({len(screen_A)})")
if len(screen_B)>0: ax.hist(screen_B["score"], bins=bins_u, color=BLUE, alpha=0.65, label=f"Screen B ({len(screen_B)})")
ax.axvline(0.50, color=YELLOW, lw=1.5, ls="--"); ax.axvline(0.55, color=GREEN, lw=1.5, ls="--")
ax.set_xlabel("Score"); ax.set_ylabel("Count")
ax.set_title("Score Distribution — Full Universe", color=TEXT_CLR, fontweight="bold")
ax.legend(fontsize=9)

# P2: Top 20 Screen A
ax = axes[0,1]
top20a = screen_A.head(20).reset_index(drop=True)
if len(top20a)>0:
    col2 = [GREEN if s>=0.62 else (BLUE if s>=0.57 else TEAL) for s in top20a["score"]]
    ax.barh(range(len(top20a)), top20a["score"], color=col2, alpha=0.85)
    ax.set_yticks(range(len(top20a)))
    ax.set_yticklabels([f"{r['ticker']}  ICB:{r.get('ICB_Code','?')}" for _,r in top20a.iterrows()], fontsize=8)
    ax.axvline(0.55, color=GREEN, lw=1.2, ls="--")
    ax.axvline(0.60, color=YELLOW, lw=1.2, ls=":")
    for i,(_,r) in enumerate(top20a.iterrows()):
        ax.text(r["score"]+0.002, i, f"{r['score']:.3f}", va="center", fontsize=7.5, color=TEXT_CLR)
ax.set_xlabel("Score")
ax.set_title("Top 20 — Screen A\n(Score>=0.55 + RSI<0.55 + MACD>0 + NP_YoY>10%)", color=TEXT_CLR, fontweight="bold")

# P3: Top 20 Screen B
ax = axes[0,2]
top20b = screen_B.head(20).reset_index(drop=True)
if len(top20b)>0:
    col3 = [BLUE if s>=0.58 else (TEAL if s>=0.53 else CYAN) for s in top20b["score"]]
    ax.barh(range(len(top20b)), top20b["score"], color=col3, alpha=0.85)
    ax.set_yticks(range(len(top20b)))
    ax.set_yticklabels([f"{r['ticker']}  ICB:{r.get('ICB_Code','?')}" for _,r in top20b.iterrows()], fontsize=8)
    ax.axvline(0.50, color=YELLOW, lw=1.2, ls="--")
    for i,(_,r) in enumerate(top20b.iterrows()):
        ax.text(r["score"]+0.002, i, f"{r['score']:.3f}", va="center", fontsize=7.5, color=TEXT_CLR)
ax.set_xlabel("Score")
ax.set_title("Top 20 — Screen B\n(Score>=0.50 + MACD>0 + FSCORE>4 + ROE>6%)", color=TEXT_CLR, fontweight="bold")

# P4: RSI vs MACDdiff scatter for Screen A
ax = axes[1,0]
ax.scatter(df["D_RSI"], df["D_MACDdiff"], c=df["score"], cmap="RdYlGn",
           alpha=0.4, s=15, vmin=0.3, vmax=0.75)
if len(screen_A)>0:
    ax.scatter(screen_A["D_RSI"], screen_A["D_MACDdiff"],
               c="lime", s=50, zorder=5, label="Screen A", edgecolors="white", linewidths=0.5)
ax.axhline(0, color=TEXT_CLR, lw=0.8, ls="--")
ax.axvline(0.55, color=YELLOW, lw=0.8, ls="--")
ax.set_xlabel("D_RSI"); ax.set_ylabel("D_MACDdiff")
ax.set_xlim(0, 1); ax.set_ylim(-500, 500)
ax.set_title("RSI vs MACDdiff\n(color=score, green=Screen A)", color=TEXT_CLR, fontweight="bold")
ax.legend(fontsize=8)

# P5: ICB sector breakdown — Screen A
ax = axes[1,1]
if len(screen_A)>0 and "ICB_Code" in screen_A.columns:
    icb = screen_A["ICB_Code"].value_counts().head(10)
    col5 = [GREEN, BLUE, YELLOW, ORANGE, PURPLE, TEAL, RED, CYAN, GREEN, BLUE][:len(icb)]
    bars5 = ax.bar(range(len(icb)), icb.values, color=col5, alpha=0.85)
    ax.set_xticks(range(len(icb)))
    ax.set_xticklabels(icb.index, fontsize=9, rotation=25)
    ax.set_ylabel("Count")
    for bar, v in zip(bars5, icb.values):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.2, str(v),
                ha="center", fontsize=9, color=TEXT_CLR, fontweight="bold")
ax.set_title("Screen A by Sector (ICB_Code)", color=TEXT_CLR, fontweight="bold")

# P6: Score vs ROE_Min3Y scatter (fundamentals)
ax = axes[1,2]
valid = df[df["ROE_Min3Y"].notna() & df["ROE_Min3Y"].between(-0.1, 0.5)]
sc = ax.scatter(valid["ROE_Min3Y"]*100, valid["score"],
                c=valid["score"], cmap="RdYlGn",
                alpha=0.35, s=12, vmin=0.3, vmax=0.75)
if len(screen_A)>0:
    sa_v = screen_A[screen_A["ROE_Min3Y"].notna()]
    ax.scatter(sa_v["ROE_Min3Y"]*100, sa_v["score"],
               c="lime", s=50, zorder=5, label="Screen A",
               edgecolors="white", linewidths=0.5)
ax.axhline(0.55, color=GREEN, lw=1.2, ls="--", label="Score 0.55")
ax.axvline(6, color=YELLOW, lw=1.0, ls="--", label="ROE_Min3Y 6%")
ax.set_xlabel("ROE_Min3Y (%)"); ax.set_ylabel("Score")
ax.set_title("Score vs ROE_Min3Y\n(quality vs model confidence)", color=TEXT_CLR, fontweight="bold")
ax.legend(fontsize=8)
plt.colorbar(sc, ax=ax, label="Score")

plt.tight_layout()
plt.savefig("universe_scan.png", dpi=150, bbox_inches="tight", facecolor=DARK_BG)
print("Chart saved: universe_scan.png")
print("\nDone.")
