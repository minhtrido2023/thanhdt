"""
pt_v6v2.py — REAL single-wallet NAV engine for the balanced core (objective test)
=================================================================================
Honesty goal: the V6-v2 backtest (CAGR 32%) is a RETURN-COMBINATION of idealized
streams. This runs a TRUE single-cash-account NAV sim where MOMENTUM and VALUE
sleeves COMPETE for one wallet with REAL frictions (T+1 Open fills, slippage, 0.3%
round-trip TC+tax, liquidity-cap fills, margin borrow on gross>100%), gated by DT5G
+ leverage ≤150% — via the production `simulate_holistic_nav.simulate()` engine.

SCOPE (labelled honestly): momentum = simple TA-momentum tier (NOT V5's BA+VN30
ensemble); value = cheapest PB+PE quintile; capit/grind NOT included (v2). So this
is the objective real-cash test of the BALANCED-CORE concept + its friction drag,
not a byte-faithful V6-v2. Compare its CAGR/Sharpe to the idealized 32% to size
how much was construction inflation.

Run: python pt_v6v2.py   (pulls ~daily prune panel from BQ; heavy → background)
"""
import sys, os, subprocess
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np
import pandas as pd
from simulate_holistic_nav import simulate, metrics

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
PANEL = WORKDIR + r"\data\v6v2_engine_panel.csv"
PROJ = "lithe-record-440915-m9"
INIT = 1_000_000_000

SQL = '''WITH p AS (
  SELECT t.time, t.ticker, t.Open, t.Close, t.MA50, t.MA200, t.D_RSI,
    t.PB, t.PE, COALESCE(t.Price,t.Close)*t.Volume AS liq_day,
    t.Volume_3M_P50*COALESCE(t.Price,t.Close) AS liq_adv
  FROM tav2_bq.ticker_prune AS t
  WHERE t.time>="2014-01-01" AND t.ticker!="VNINDEX"
    AND t.Close IS NOT NULL AND t.Open IS NOT NULL AND t.MA200 IS NOT NULL
    AND t.PB IS NOT NULL AND t.PE>0
    AND COALESCE(t.Price,t.Close)*t.Volume>=5e9)
SELECT p.*, CAST(s.state AS INT64) AS state
FROM p JOIN tav2_bq.vnindex_5state_dt5g_live AS s ON s.time=p.time
ORDER BY p.time, p.ticker'''


def pull():
    cmd = (f"bq query --use_legacy_sql=false --project_id={PROJ} --format=csv "
           f"--max_rows=2000000 '{SQL}' > '{PANEL.replace(chr(92),'/')}'")
    print("[pull] loading engine panel from BQ (heavy)...")
    r = subprocess.run(["bash", "-lc", cmd], capture_output=True, text=True)
    if r.returncode != 0:
        print("[pull] FAILED:", r.stderr[-1000:]); sys.exit(1)
    print("[pull] done.")


def main():
    if "--refresh" in sys.argv or not os.path.exists(PANEL):
        pull()
    df = pd.read_csv(PANEL, parse_dates=["time"])
    print(f"Panel: {len(df):,} rows | {df['ticker'].nunique()} tickers | "
          f"{df['time'].min().date()}→{df['time'].max().date()}")

    # --- per-day sleeve tagging ---
    df["mom_qual"] = (df["Close"] > df["MA200"]) & (df["Close"] > df["MA50"]) & (df["D_RSI"] > 0.50)
    df["mom_strength"] = df["Close"] / df["MA200"] - 1
    parts = []
    for t, g in df.groupby("time"):
        g = g.copy()
        g["vscore"] = g["PB"].rank(pct=True) + g["PE"].rank(pct=True)        # low = cheap
        cheap_cut = g["vscore"].quantile(0.20)
        is_val = g["vscore"] <= cheap_cut
        is_mom = g["mom_qual"]
        # assign play_type: MOMENTUM priority if trending; else VALUE if cheap; else PASS
        g["play_type"] = np.where(is_mom, "MOMENTUM", np.where(is_val, "VALUE", "PASS"))
        # ta = ranking score within tier (engine picks top max_pos by ta)
        g["ta"] = np.where(g["play_type"] == "MOMENTUM", 100 + 100*g["mom_strength"].clip(-0.5, 1.0),
                  np.where(g["play_type"] == "VALUE", 100 + 100*(1 - g["vscore"]/2.0), 0.0))
        parts.append(g[["time", "ticker", "play_type", "ta", "Close", "Open", "liq_adv", "state"]])
    sig = pd.concat(parts, ignore_index=True)
    sig = sig[sig["play_type"].isin(["MOMENTUM", "VALUE"])].copy()
    print(f"signal rows: MOMENTUM {int((sig['play_type']=='MOMENTUM').sum()):,} | "
          f"VALUE {int((sig['play_type']=='VALUE').sum()):,}")

    vni_dates = sorted(df["time"].unique())
    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in df.groupby("ticker")}
    opens = {tk: dict(zip(g["time"], g["Open"])) for tk, g in df.groupby("ticker")}
    liqlk = {(r.ticker, r.time): r.liq_adv for r in df.itertuples()}
    state_by_date = {t: int(s) for t, s in df.groupby("time")["state"].first().items()}

    # --- V6-v2 balanced-core tier weights by DT5G state (gross ≤150% via leverage) ---
    # 1 CRISIS 2 BEAR 3 NEUTRAL 4 BULL 5 EXBULL
    if "--valueonly" in sys.argv:   # REAL DT5G-gated value book alone (no momentum), no leverage
        tw = {1: {"MOMENTUM": 0.0, "VALUE": 0.0}, 2: {"MOMENTUM": 0.0, "VALUE": 0.20},
              3: {"MOMENTUM": 0.0, "VALUE": 0.70}, 4: {"MOMENTUM": 0.0, "VALUE": 1.00},
              5: {"MOMENTUM": 0.0, "VALUE": 1.00}}
    elif "--nolev" in sys.argv:   # gross capped at 1.0 (isolate leverage's contribution to DD)
        tw = {1: {"MOMENTUM": 0.0, "VALUE": 0.0}, 2: {"MOMENTUM": 0.0, "VALUE": 0.40},
              3: {"MOMENTUM": 0.50, "VALUE": 0.50}, 4: {"MOMENTUM": 0.50, "VALUE": 0.50},
              5: {"MOMENTUM": 0.45, "VALUE": 0.45}}
    else:
        tw = {1: {"MOMENTUM": 0.0,  "VALUE": 0.0},
              2: {"MOMENTUM": 0.0,  "VALUE": 0.40},
              3: {"MOMENTUM": 0.50, "VALUE": 0.50},
              4: {"MOMENTUM": 0.675,"VALUE": 0.675},   # gross 1.35
              5: {"MOMENTUM": 0.45, "VALUE": 0.45}}

    nav_df, trades = simulate(
        sig, prices, vni_dates,
        allowed_tiers=["MOMENTUM", "VALUE"], max_positions=16,
        tier_position_limit={"MOMENTUM": 8, "VALUE": 8},
        tier_weights_by_state=tw,
        state_by_date=state_by_date, state_exit_map={1: 1.0, 2: 0.5},
        hold_days=60, stop_loss=-0.15, min_hold=2,
        slippage=0.001, exit_slippage_tiered=True,
        liquidity_volume_pct=0.10, liquidity_lookup=liqlk, max_fill_days=2,
        open_prices=opens, t1_open_exec=True,
        borrow_annual=0.10, deposit_annual=0.03, init_nav=INIT,
        name="V6v2_realcash")

    m = metrics(nav_df, trades, "V6v2_realcash")
    print("\n=== V6-v2 REAL single-wallet (momentum+value compete, real frictions, DT5G, lev≤150%) ===")
    print(f"  CAGR {m['cagr_pct']:.1f}%  Sharpe {m['sharpe']:.2f}  MaxDD {m['max_dd_pct']:.1f}%  "
          f"Calmar {m['calmar']:.2f}  trades {m['n_trades']}  win {m.get('win_rate_pct',0):.0f}%")
    print(f"\n  vs idealized return-combination V6-v2: CAGR ~32% / Sharpe 1.45 / Calmar 1.99")
    print(f"  → friction+construction drag = the difference (this is the OBJECTIVE real-cash number)")
    nav_df.to_csv(WORKDIR + r"\data\pt_v6v2_nav.csv", index=False)
    print("  Saved: data/pt_v6v2_nav.csv")


if __name__ == "__main__":
    main()
