"""
pt_v6v3_faithful.py — FAITHFUL transaction-level V6-v3 (REAL BA-v11 momentum signal)
====================================================================================
Replaces the crude TA-momentum with the REAL prod-spec BA-v11 stock signal
(ba_v11_unified_12y_sig.pkl — the actual V5 momentum selection: MEGA/MOMENTUM/
COMPOUNDER_BUY/DEEP_VALUE_RECOVERY tiers + ta), merged with VALUE (cheapest PB+PE
quintile) + CAPIT (golden basket) into ONE simulate() wallet, DT5G-gated tier
weights, real T+1/slippage/0.3%TC/liquidity-cap fills, 2022 -> now. This is the
honest transaction-level V6-v3 — momentum is now V5's real selection, not crude TA.
(Engine caps deployment at 100% cash → capit/leverage = substitution, no margin-buy.)

Run: python pt_v6v3_faithful.py
"""
import sys, os, pickle
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np
import pandas as pd
from simulate_holistic_nav import simulate

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
PKL = WORKDIR + r"\ba_v11_unified_12y_sig.pkl"
PANEL = WORKDIR + r"\data\v6v3_txn_panel.csv"
INIT = 1_000_000_000
START = "2022-01-01"
MOM_TIERS = ["MEGA", "S_PRO", "MOMENTUM", "MOMENTUM_QUALITY", "MOMENTUM_N",
             "MOMENTUM_S", "MOMENTUM_A", "MOMENTUM_S_N", "COMPOUNDER_BUY", "DEEP_VALUE_RECOVERY"]


def main():
    sig_b = pickle.load(open(PKL, "rb"))
    sig_b["time"] = pd.to_datetime(sig_b["time"])
    mom = sig_b[sig_b["play_type"].isin(MOM_TIERS)][["ticker", "time", "ta"]].copy()
    mom["is_mom"] = True

    df = pd.read_csv(PANEL, parse_dates=["time"])
    df["pb_z"] = (df["PB"] - df["PB_MA5Y"]) / df["PB_SD5Y"].replace(0, np.nan)
    df = df.merge(mom, on=["ticker", "time"], how="left")
    df["is_mom"] = df["is_mom"].fillna(False)
    df["golden"] = (df["state"].isin([1, 2]) & (df["D_RSI"] < 0.35) & (df["pb_z"] < -1.0)
                    & ((df["ROE_Min5Y"] >= 0.10) | (df["FSCORE"] >= 6)))

    parts = []
    for t, g in df.groupby("time"):
        g = g.copy()
        g["vscore"] = g["PB"].rank(pct=True) + g["PE"].rank(pct=True)
        cheap = g["vscore"] <= g["vscore"].quantile(0.20)
        # priority: MOMENTUM (real BA-v11 pick) > CAPIT (golden) > VALUE (cheap)
        g["play_type"] = np.where(g["is_mom"], "MOMENTUM",
                          np.where(g["golden"], "CAPIT",
                          np.where(cheap, "VALUE", "PASS")))
        g["ta2"] = np.where(g["play_type"] == "MOMENTUM", g["ta"].fillna(120),
                   np.where(g["play_type"] == "CAPIT", 300 - 100*g["pb_z"].clip(-5, 0),
                   np.where(g["play_type"] == "VALUE", 100 + 100*(1 - g["vscore"]/2), 0.0)))
        parts.append(g[["time", "ticker", "play_type", "ta2", "Close", "Open", "liq_adv", "state"]])
    sig = pd.concat(parts, ignore_index=True).rename(columns={"ta2": "ta"})
    sig = sig[sig["play_type"].isin(["MOMENTUM", "VALUE", "CAPIT"])]
    print(f"Faithful signal: MOM {int((sig['play_type']=='MOMENTUM').sum()):,} (real BA-v11) "
          f"VAL {int((sig['play_type']=='VALUE').sum()):,} CAPIT {int((sig['play_type']=='CAPIT').sum()):,}")

    # E1VFVN30 ETF prices for idle-cash parking (V5's real machinery)
    ETFF = WORKDIR + r"\data\e1vfvn30_daily.csv"
    if not os.path.exists(ETFF):
        import subprocess
        sql = ('SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker="E1VFVN30" '
               'AND t.time>="2021-09-01" ORDER BY t.time')
        cmd = (f'bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv '
               f'--max_rows=5000 \'{sql}\' > \'{ETFF.replace(chr(92),"/")}\'')
        subprocess.run(["bash", "-lc", cmd], check=True)
    etf = pd.read_csv(ETFF, parse_dates=["time"])
    vn30_und = pd.Series(etf["Close"].values, index=etf["time"])

    vni_dates = sorted(df["time"].unique())
    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in df.groupby("ticker")}
    opens = {tk: dict(zip(g["time"], g["Open"])) for tk, g in df.groupby("ticker")}
    liqlk = {(r.ticker, r.time): r.liq_adv for r in df.itertuples()}
    state_by_date = {t: int(s) for t, s in df.groupby("time")["state"].first().items()}

    CORE = "--core" in sys.argv   # CORE: momentum+value with crisis EXITS (like V5 actually behaves), no capit-hold
    if CORE:
        tiers = ["MOMENTUM", "VALUE"]; tpl = {"MOMENTUM": 8, "VALUE": 6}   # cap value concentration
        tw = {1: {"VALUE": 0.0,  "MOMENTUM": 0.0}, 2: {"VALUE": 0.20, "MOMENTUM": 0.0},
              3: {"VALUE": 0.35, "MOMENTUM": 0.50}, 4: {"VALUE": 0.35, "MOMENTUM": 0.50},
              5: {"VALUE": 0.30, "MOMENTUM": 0.45}}   # value down → idle cash parks ETF (VN30 balance)
        sexit = {1: 1.0, 2: 0.5}      # EXIT in crisis/bear (V5's real protective behavior)
    else:
        tiers = ["MOMENTUM", "VALUE", "CAPIT"]; tpl = {"MOMENTUM": 8, "VALUE": 6, "CAPIT": 8}
        tw = {1: {"CAPIT": 0.80, "VALUE": 0.0,  "MOMENTUM": 0.0},
              2: {"CAPIT": 0.40, "VALUE": 0.35, "MOMENTUM": 0.0},
              3: {"CAPIT": 0.0,  "VALUE": 0.50, "MOMENTUM": 0.50},
              4: {"CAPIT": 0.0,  "VALUE": 0.50, "MOMENTUM": 0.50},
              5: {"CAPIT": 0.0,  "VALUE": 0.45, "MOMENTUM": 0.45}}
        sexit = {1: 0.0}      # capit wants to HOLD crisis buys -> no force-close (the conflict)

    events = []
    nav_df, _ = simulate(
        sig, prices, vni_dates,
        allowed_tiers=tiers, max_positions=16,
        tier_position_limit=tpl,
        tier_weights_by_state=tw, state_by_date=state_by_date, state_exit_map=sexit,
        hold_days=60, stop_loss=-0.15, min_hold=2,
        slippage=0.001, exit_slippage_tiered=True,
        liquidity_volume_pct=0.10, liquidity_lookup=liqlk, max_fill_days=2,
        open_prices=opens, t1_open_exec=True, borrow_annual=0.10, deposit_annual=0.03,
        init_nav=INIT, event_log=events,
        # ETF-parking idle cash in good states (V5 machinery) — keeps exposure when momentum sparse
        cash_etf_states={1: 0.0, 2: 0.0, 3: 0.8, 4: 1.0, 5: 0.8} if CORE else None,
        vn30_underlying=vn30_und if CORE else None,
        etf_mgmt_fee_annual=0.0065, etf_tracking_drag_annual=0.003, etf_rebalance_friction=0.0015,
        name="V6v3_faithful")

    nav_df["time"] = pd.to_datetime(nav_df["time"])
    nd = nav_df[nav_df["time"] >= START].copy(); nav = nd.set_index("time")["nav"]
    ret = nav.pct_change().dropna(); n = len(ret); cagr = (nav.iloc[-1]/nav.iloc[0])**(252/n)-1
    dd = (nav/nav.cummax()-1); sh = ret.mean()/ret.std()*np.sqrt(252)
    so = ret.mean()/ret[ret < 0].std()*np.sqrt(252)
    tx = pd.DataFrame(events)
    if len(tx):
        tx["ymd"] = pd.to_datetime(tx["ymd"]); tx = tx[tx["ymd"] >= START]
        tx.to_csv(WORKDIR + r"\data\v6v3_faithful_transactions.csv", index=False)
    nd.to_csv(WORKDIR + r"\data\v6v3_faithful_nav.csv", index=False)
    print(f"\n=== V6-v3 FAITHFUL (real BA-v11 momentum + value + capit, one wallet, {START}->{nav.index[-1].date()}) ===")
    print(f"  CAGR {cagr*100:.1f}%  Sharpe {sh:.2f}  Sortino {so:.2f}  MaxDD {dd.min()*100:.1f}%  "
          f"Calmar {cagr/abs(dd.min()):.2f}  (MaxDD {dd.idxmin().date()})")
    print(f"  transactions {len(tx)} | NAV {nav.iloc[0]/1e9:.2f}B -> {nav.iloc[-1]/1e9:.2f}B")
    if len(tx):
        print(f"  by play_type: {tx['play_type'].value_counts().to_dict()}")
    print("  Saved: data/v6v3_faithful_transactions.csv, data/v6v3_faithful_nav.csv")


if __name__ == "__main__":
    main()
