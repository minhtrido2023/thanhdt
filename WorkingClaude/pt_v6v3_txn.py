"""
pt_v6v3_txn.py — REAL single-wallet TRANSACTION-LEVEL sim of V6-v3, 2022 -> now
==============================================================================
HONESTY NOTE: momentum here = engine TA-momentum (NOT V5-ensemble — V5 is a 3-book
recombination that can't be held as engine stocks). So this transaction-level DD
will be WORSE than the −16.8% return-combination (which used real V5). This is the
honest transaction sim; I do NOT tune it to hit −16.8%. Engine caps deployment at
100% cash (no margin-buy), so the capit "carve" here is SUBSTITUTION (≤100%), not
the additive 148% of the return-combination.

Sleeves (play_type) in ONE wallet via simulate():
  MOMENTUM = trending (Close>MA50>MA200 & RSI>0.5)        — good states
  VALUE    = cheapest PB+PE quintile                      — good states
  CAPIT    = golden basket (state CRISIS/BEAR & oversold & pb_z<−1 & quality) — crisis-buy
Outputs: data/v6v3_txn_transactions.csv (every buy/sell), data/v6v3_txn_nav.csv
(daily NAV + state + deployed + decision), console summary with honest MaxDD.
Run: python pt_v6v3_txn.py [--refresh]
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
PANEL = WORKDIR + r"\data\v6v3_txn_panel.csv"
PROJ = "lithe-record-440915-m9"
INIT = 1_000_000_000
START = "2022-01-01"

SQL = '''WITH p AS (
  SELECT t.time, t.ticker, t.Open, t.Close, t.MA50, t.MA200, t.D_RSI,
    t.PB, t.PE, t.PB_MA5Y, t.PB_SD5Y, t.ROE_Min5Y, t.FSCORE,
    t.Volume_3M_P50*COALESCE(t.Price,t.Close) AS liq_adv
  FROM tav2_bq.ticker_prune AS t
  WHERE t.time>="2021-09-01" AND t.ticker!="VNINDEX"
    AND t.Close IS NOT NULL AND t.Open IS NOT NULL AND t.MA200 IS NOT NULL
    AND t.PB IS NOT NULL AND t.PE>0
    AND COALESCE(t.Price,t.Close)*t.Volume>=5e9)
SELECT p.*, CAST(s.state AS INT64) AS state
FROM p JOIN tav2_bq.vnindex_5state_dt5g_live AS s ON s.time=p.time
ORDER BY p.time, p.ticker'''


def pull():
    cmd = (f"bq query --use_legacy_sql=false --project_id={PROJ} --format=csv "
           f"--max_rows=2000000 '{SQL}' > '{PANEL.replace(chr(92),'/')}'")
    print("[pull] richer panel 2021-09 -> now ...")
    r = subprocess.run(["bash", "-lc", cmd], capture_output=True, text=True)
    if r.returncode != 0:
        print("[pull] FAILED:", r.stderr[-1000:]); sys.exit(1)
    print("[pull] done.")


def main():
    if "--refresh" in sys.argv or not os.path.exists(PANEL):
        pull()
    df = pd.read_csv(PANEL, parse_dates=["time"])
    df["pb_z"] = (df["PB"] - df["PB_MA5Y"]) / df["PB_SD5Y"].replace(0, np.nan)
    df["mom_qual"] = (df["Close"] > df["MA200"]) & (df["Close"] > df["MA50"]) & (df["D_RSI"] > 0.50)
    df["golden"] = (df["state"].isin([1, 2]) & (df["D_RSI"] < 0.35) & (df["pb_z"] < -1.0)
                    & ((df["ROE_Min5Y"] >= 0.10) | (df["FSCORE"] >= 6)))
    parts = []
    for t, g in df.groupby("time"):
        g = g.copy()
        g["vscore"] = g["PB"].rank(pct=True) + g["PE"].rank(pct=True)
        cheap = g["vscore"] <= g["vscore"].quantile(0.20)
        g["play_type"] = np.where(g["golden"], "CAPIT",
                          np.where(g["mom_qual"], "MOMENTUM",
                          np.where(cheap, "VALUE", "PASS")))
        g["ta"] = np.where(g["play_type"] == "CAPIT", 300 - 100*g["pb_z"].clip(-5, 0),
                  np.where(g["play_type"] == "MOMENTUM", 100 + 100*(g["Close"]/g["MA200"]-1).clip(-0.5, 1.0),
                  np.where(g["play_type"] == "VALUE", 100 + 100*(1 - g["vscore"]/2), 0.0)))
        parts.append(g[["time", "ticker", "play_type", "ta", "Close", "Open", "liq_adv", "state"]])
    sig = pd.concat(parts, ignore_index=True)
    sig = sig[sig["play_type"].isin(["MOMENTUM", "VALUE", "CAPIT"])]
    print(f"Panel {df['time'].min().date()}->{df['time'].max().date()} | sig: "
          f"MOM {int((sig['play_type']=='MOMENTUM').sum()):,} VAL {int((sig['play_type']=='VALUE').sum()):,} "
          f"CAPIT {int((sig['play_type']=='CAPIT').sum()):,}")

    vni_dates = sorted(df["time"].unique())
    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in df.groupby("ticker")}
    opens = {tk: dict(zip(g["time"], g["Open"])) for tk, g in df.groupby("ticker")}
    liqlk = {(r.ticker, r.time): r.liq_adv for r in df.itertuples()}
    state_by_date = {t: int(s) for t, s in df.groupby("time")["state"].first().items()}

    # V6-v3 tier weights by DT5G state (engine caps gross at 100% — substitution-style capit)
    tw = {1: {"CAPIT": 0.80, "VALUE": 0.0,  "MOMENTUM": 0.0},   # CRISIS: golden carve
          2: {"CAPIT": 0.40, "VALUE": 0.35, "MOMENTUM": 0.0},   # BEAR
          3: {"CAPIT": 0.0,  "VALUE": 0.50, "MOMENTUM": 0.50},  # NEUTRAL
          4: {"CAPIT": 0.0,  "VALUE": 0.50, "MOMENTUM": 0.50},  # BULL
          5: {"CAPIT": 0.0,  "VALUE": 0.45, "MOMENTUM": 0.45}}  # EXBULL

    events, navlog = [], []
    nav_df, trades = simulate(
        sig, prices, vni_dates,
        allowed_tiers=["MOMENTUM", "VALUE", "CAPIT"], max_positions=16,
        tier_position_limit={"MOMENTUM": 7, "VALUE": 7, "CAPIT": 8},
        tier_weights_by_state=tw, state_by_date=state_by_date, state_exit_map={1: 0.0},
        hold_days=60, stop_loss=-0.15, min_hold=2,
        slippage=0.001, exit_slippage_tiered=True,
        liquidity_volume_pct=0.10, liquidity_lookup=liqlk, max_fill_days=2,
        open_prices=opens, t1_open_exec=True,
        borrow_annual=0.10, deposit_annual=0.03, init_nav=INIT,
        event_log=events, nav_log_extra=navlog, name="V6v3_txn")

    # restrict reporting to 2022+
    nav_df["time"] = pd.to_datetime(nav_df["time"])
    nd = nav_df[nav_df["time"] >= START].copy()
    nav = nd.set_index("time")["nav"]
    ret = nav.pct_change().dropna(); n = len(ret); yrs = n/252
    cagr = (nav.iloc[-1]/nav.iloc[0])**(1/yrs)-1
    dd = (nav/nav.cummax()-1); maxdd = dd.min()
    sh = ret.mean()/ret.std()*np.sqrt(252)
    so = ret.mean()/ret[ret<0].std()*np.sqrt(252)

    # save transactions + nav
    tx = pd.DataFrame(events)
    nbuy = nsell = 0
    if len(tx):
        tx["ymd"] = pd.to_datetime(tx["ymd"]); tx = tx[tx["ymd"] >= START]
        tx.to_csv(WORKDIR + r"\data\v6v3_txn_transactions.csv", index=False)
        nbuy = int((tx["action"] == "buy").sum()); nsell = int((tx["action"].isin(["sell"])).sum())
    nd.to_csv(WORKDIR + r"\data\v6v3_txn_nav.csv", index=False)

    print(f"\n=== V6-v3 TRANSACTION-LEVEL sim (real single-wallet, engine, {START} -> {nav.index[-1].date()}) ===")
    print(f"  CAGR {cagr*100:.1f}%  Sharpe {sh:.2f}  Sortino {so:.2f}  MaxDD {maxdd*100:.1f}%  "
          f"Calmar {cagr/abs(maxdd):.2f}")
    print(f"  transactions: {len(tx)} (buy {nbuy}, sell {nsell}) | MaxDD date {dd.idxmin().date()}")
    print(f"  NAV start {nav.iloc[0]/1e9:.2f}B -> end {nav.iloc[-1]/1e9:.2f}B")
    print(f"\n  HONEST NOTE: momentum=TA (not V5-ensemble) → DD worse than the −16.8% return-combo (which used real V5).")
    print(f"  Saved: data/v6v3_txn_transactions.csv, data/v6v3_txn_nav.csv")


if __name__ == "__main__":
    main()
