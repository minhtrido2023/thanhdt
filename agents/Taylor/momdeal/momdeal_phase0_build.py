#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""momdeal Phase 0 step 2 — build episode/deal dataset with PIT joins + labels.

Job Taylor_20260711_165407 (plan_momentum_deals_20260711.md §6 CP0).
Outputs (data/momdeal_exp/, per guidelines §8 — never canonical filenames):
  momdeal_episodes_phase0.csv  — L2 unit: signal episodes (gap>7d), 13 features + forward labels
  momdeal_deals_phase0.csv     — L1 unit: book round-trips from canonical R3 CSV, features at T-1
  phase0_report.txt            — N reconciliation, 8L coverage, distribution checks

PIT rules enforced here:
  - technical features: ticker row at episode entry day (signal info set) / deals: last row <= entry-1
  - fa_ratings_8l: ASOF time <= feature_date
  - ticker_financial: ASOF Release_Date <= feature_date (NOT quarter time — release-anchored)
  - forward labels profit_2M/3M: pulled ONLY into label columns, never features
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd, duckdb

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
OUT = "data/momdeal_exp"
os.makedirs(OUT, exist_ok=True)

PKL_NEW = "data/ba_v11_unified_12y_sig.pkl"                    # dt5g, rebuilt 07-11
PKL_OLD = "data/ba_v11_unified_12y_sig.pkl.bak_predt5g_20260711"  # base, frozen 06-16
CSV_R3  = "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap.csv"

FAMILY   = ["MOMENTUM_N", "MOMENTUM_S", "MOMENTUM", "MEGA"]
COHORT   = ["DEEP_VALUE_RECOVERY"]
DIAG     = ["MOMENTUM_S_N"]          # state-3 twin of MOMENTUM_S — surfaces under DT5G; flagged, not in family
EP_TYPES = FAMILY + COHORT + DIAG
GAP_DAYS = 7

rep = []
def R(s=""):
    print(s); rep.append(s)

# ---------------------------------------------------------------- episodes
def episodes_from(pkl_path, types):
    sig = pickle.load(open(pkl_path, "rb"))
    sig["time"] = pd.to_datetime(sig["time"])
    s = sig[sig["play_type"].isin(types)][
        ["ticker", "time", "play_type", "ta", "liq", "sec", "days_since_release", "state5", "Close"]
    ].sort_values(["ticker", "play_type", "time"])
    g = s.groupby(["ticker", "play_type"])
    new_ep = (s["time"] - g["time"].shift()).dt.days.gt(GAP_DAYS) | g.cumcount().eq(0)
    s["ep_id"] = new_ep.cumsum()
    ep = s.groupby("ep_id").agg(
        ticker=("ticker", "first"), play_type=("play_type", "first"),
        entry_date=("time", "first"), last_fire=("time", "last"), n_fires=("time", "size"),
        ta=("ta", "first"), liq=("liq", "first"), sec=("sec", "first"),
        days_since_release=("days_since_release", "first"), state5=("state5", "first"),
        close_entry=("Close", "first"),
    ).reset_index(drop=True)
    return ep

R("=" * 90)
R("PHASE 0 DATASET BUILD — momentum-deals (job Taylor_20260711_165407)")
R("=" * 90)

ep_new = episodes_from(PKL_NEW, EP_TYPES)
ep_old = episodes_from(PKL_OLD, EP_TYPES)

R("\n[A] Episode counts — survey reconciliation")
R(f"    {'play_type':<22} {'survey(§2b)':>12} {'base pkl 06-16':>15} {'dt5g pkl 07-10':>15}")
survey = {"MOMENTUM_N": 87, "MOMENTUM_S": 513, "MOMENTUM": 129, "MEGA": 10, "DEEP_VALUE_RECOVERY": 1077}
oc = ep_old["play_type"].value_counts(); nc = ep_new["play_type"].value_counts()
recon_fail = []
for t in EP_TYPES:
    sv = survey.get(t, None)
    o, n = int(oc.get(t, 0)), int(nc.get(t, 0))
    flag = ""
    if sv is not None:
        dev = abs(o - sv) / sv
        flag = "OK(±10%)" if dev <= 0.10 else f"DEV {dev*100:.0f}%"
        if dev > 0.10: recon_fail.append(t)
    R(f"    {t:<22} {str(sv) if sv else '—':>12} {o:>15,} {n:>15,}   {flag}")
R(f"    (survey was measured on the frozen base-state pkl; base-pkl column is the like-for-like check.")
R(f"     dt5g column = dataset actually used downstream — shift is the F3 state-source change + 1 extra month.)")

ep = ep_new.copy()
ep["in_family"] = ep["play_type"].isin(FAMILY)
ep["cohort"] = np.where(ep["play_type"].isin(FAMILY), "MOM_FAMILY",
               np.where(ep["play_type"].isin(COHORT), "DVR_CONTROL", "DIAG_S_N"))

# ---------------------------------------------------------------- deals (L1)
R("\n[B] Deals (L1) — canonical R3 ledger round-trips")
tx = pd.read_csv(CSV_R3, low_memory=False)
tx = tx[tx["record_type"] == "TX"].copy()
tx["ymd"] = pd.to_datetime(tx["ymd"])
for c in ["shares", "buy_amount", "sell_amount", "fee"]:
    tx[c] = pd.to_numeric(tx[c], errors="coerce").fillna(0.0)

def agg_holding(h):
    b, s = h[h["action"] == "buy"], h[h["action"] == "sell"]
    return pd.Series({
        "book": h["book"].iloc[0], "ticker": h["ticker"].iloc[0], "play_type": h["play_type"].iloc[0],
        "entry_date": b["ymd"].min() if len(b) else pd.NaT, "exit_date": s["ymd"].max() if len(s) else pd.NaT,
        "n_buys": len(b), "n_sells": len(s),
        "buy_amt": b["buy_amount"].sum(), "sell_amt": s["sell_amount"].sum(),
        "fee_buy": b["fee"].sum(), "fee_sell": s["fee"].sum(),
        "sh_buy": b["shares"].sum(), "sh_sell": s["shares"].sum(),
        "exit_reason": s["reason"].iloc[-1] if len(s) else None,
    })

deals = tx.groupby("holding_id").apply(agg_holding).reset_index()
deals["closed"] = (deals["n_sells"] > 0) & (np.abs(deals["sh_buy"] - deals["sh_sell"]) < 1.0)
deals["net_ret"] = (deals["sell_amt"] - deals["fee_sell"]) / (deals["buy_amt"] + deals["fee_buy"]) - 1
closed = deals[deals["closed"]].copy()
R(f"    holdings total={len(deals):,}  closed={len(closed):,}  (survey: 2,258 closed)")

deal_survey = {"MOMENTUM_N": 77, "MOMENTUM_S": 46, "RE_BACKLOG_BUY": 136, "DEEP_VALUE_RECOVERY": 247}
closed["pt_base"] = closed["play_type"].str.replace("_W$", "", regex=True)
R(f"    {'play_type(+_W)':<24} {'survey':>8} {'measured':>9} {'win%':>6} {'avg%':>7} {'med%':>7}")
deal_recon_fail = []
for t, sv in deal_survey.items():
    d = closed[closed["pt_base"] == t]
    n = len(d)
    dev = abs(n - sv) / sv
    if dev > 0.10: deal_recon_fail.append(t)
    R(f"    {t:<24} {sv:>8} {n:>9} {(d['net_ret']>0).mean()*100:>5.1f} {d['net_ret'].mean()*100:>+6.1f} {d['net_ret'].median()*100:>+6.1f}"
      f"   {'OK(±10%)' if dev<=0.10 else f'DEV {dev*100:.0f}%'}")

BAL_PT = ["MOMENTUM_N", "MOMENTUM_S", "MOMENTUM", "MEGA", "DEEP_VALUE_RECOVERY", "RE_BACKLOG_BUY"]
dl = closed[closed["pt_base"].isin(BAL_PT)].copy().reset_index(drop=True)
dl["feature_date"] = dl["entry_date"] - pd.Timedelta(days=1)   # T-1 info set (ASOF <= handles weekends)
R(f"    L1 dataset rows (BAL family+controls, closed): {len(dl):,}")

# ---------------------------------------------------------------- duckdb PIT joins
con = duckdb.connect()
con.execute("SET threads TO 1")
TK  = "read_parquet('data/bq_cache/ticker/*.parquet')"
TKP = "read_parquet('data/bq_cache/ticker_prune/*.parquet')"

fa8 = pd.read_parquet("data/bq_cache/fa_ratings_8l.parquet")
fa8["time"] = pd.to_datetime(fa8["time"])
fa8 = fa8.sort_values(["ticker", "time"]).rename(columns={"time": "eff_date"})

fin = pd.read_parquet("data/bq_cache/ticker_financial.parquet",
                      columns=["ticker", "time", "Release_Date", "ROIC_Trailing", "CF_OA_P0", "Revenue_YoY_P0"])
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
fin = fin.dropna(subset=["Release_Date"]).sort_values(["ticker", "Release_Date"])
# same release date can carry restatements — keep the latest quarter (max time) per release
fin = fin.sort_values(["ticker", "Release_Date", "time"]).drop_duplicates(["ticker", "Release_Date"], keep="last")

def join_all(df, fdate_col):
    """Attach technical (ticker row ASOF fdate), prune liq col, 8L ASOF, financial ASOF Release_Date."""
    con.register("base_df", df)
    con.register("fa8_df", fa8)
    con.register("fin_df", fin)
    q = f"""
    WITH tk AS (
      SELECT ticker, CAST(time AS DATE) AS time, D_RSI, Volume, Volume_3M_P50, C_L1M, Close, Res_1Y,
             profit_2M, profit_3M
      FROM {TK}
    ),
    tkp AS (
      SELECT ticker, CAST(time AS DATE) AS time, Trading_Value_1M_P50 FROM {TKP}
    )
    SELECT b.*,
           t.time  AS tech_date, t.D_RSI, t.Volume, t.Volume_3M_P50, t.C_L1M,
           t.Close AS close_tech, t.Res_1Y, t.profit_2M, t.profit_3M,
           p.time  AS prune_date, p.Trading_Value_1M_P50,
           f.eff_date AS fa8_eff_date, f.route, f.rating, f.tier,
           fi.Release_Date AS fin_release_date, fi.ROIC_Trailing, fi.CF_OA_P0, fi.Revenue_YoY_P0
    FROM base_df b
    ASOF LEFT JOIN tk  t  ON b.ticker = t.ticker  AND t.time  <= CAST(b.{fdate_col} AS DATE)
    ASOF LEFT JOIN tkp p  ON b.ticker = p.ticker  AND p.time  <= CAST(b.{fdate_col} AS DATE)
    ASOF LEFT JOIN fa8_df f  ON b.ticker = f.ticker AND f.eff_date <= CAST(b.{fdate_col} AS DATE)
    ASOF LEFT JOIN fin_df fi ON b.ticker = fi.ticker AND fi.Release_Date <= CAST(b.{fdate_col} AS DATE)
    """
    out = con.execute(q).df()
    con.unregister("base_df"); con.unregister("fa8_df"); con.unregister("fin_df")
    return out

R("\n[C] PIT joins (duckdb ASOF, threads=1)")
ep_j = join_all(ep.assign(feature_date=ep["entry_date"]), "feature_date")
dl_j = join_all(dl, "feature_date")

for df, fcol, tag in [(ep_j, "entry_date", "episodes"), (dl_j, "feature_date", "deals")]:
    stale = (pd.to_datetime(df[fcol]).dt.normalize() - pd.to_datetime(df["tech_date"])).dt.days
    R(f"    {tag}: tech row found {(df['tech_date'].notna()).mean()*100:.1f}% | tech row >5d older than feature date: {(stale>5).mean()*100:.2f}%")

# derived features (pre-registered §4)
for df in (ep_j, dl_j):
    df["T3_vol_ratio"]  = df["Volume"] / df["Volume_3M_P50"].replace(0, np.nan)
    df["T5_close_res"]  = df["close_tech"] / df["Res_1Y"].replace(0, np.nan)
    df["C1_log_tv"]     = np.log10(df["Trading_Value_1M_P50"].where(df["Trading_Value_1M_P50"] > 0))
    df["F4_cfoa_pos"]   = (df["CF_OA_P0"] > 0).astype("float").where(df["CF_OA_P0"].notna())

# L2 labels: forward returns at entry (labels ONLY)
ep_j["L2_success"] = np.where(ep_j["profit_2M"] >= 0.10, 1, np.where(ep_j["profit_2M"] <= 0.0, 0, np.nan))
ep_j["label_available"] = ep_j["profit_2M"].notna()
dl_j["L1_success"] = np.where(dl_j["net_ret"] >= 0.10, 1, np.where(dl_j["net_ret"] <= 0.0, 0, np.nan))

# ---------------------------------------------------------------- coverage (CP0 gate)
R("\n[D] 8L coverage at entry (CP0 hard gate: >=80% episodes)")
def cov_block(df, tag, datecol):
    d = pd.to_datetime(df[datecol])
    cov_all = df["rating"].notna().mean() * 100
    R(f"    {tag}: overall coverage = {cov_all:.1f}%  (n={len(df):,})")
    for lo, hi in [("2014", "2019"), ("2020", "2026")]:
        m = (d.dt.year >= int(lo)) & (d.dt.year <= int(hi))
        if m.sum():
            R(f"      {lo}-{hi}: {df.loc[m,'rating'].notna().mean()*100:.1f}%  (n={int(m.sum()):,})")
    per_yr = df.assign(y=d.dt.year).groupby("y")["rating"].apply(lambda s: s.notna().mean() * 100)
    R("      per-year: " + "  ".join(f"{y}:{v:.0f}%" for y, v in per_yr.items()))
    return cov_all

cov_fam = cov_block(ep_j[ep_j["in_family"]], "episodes MOM_FAMILY", "entry_date")
cov_all_ep = cov_block(ep_j, "episodes ALL (family+DVR+diag)", "entry_date")
cov_dl = cov_block(dl_j, "deals L1", "entry_date")

R("\n[E] Label availability")
R(f"    episodes with profit_2M label: {ep_j['label_available'].mean()*100:.1f}%  "
  f"(missing = tail entries after ~2026-05 without T+40 yet + data gaps)")
lbl = ep_j[ep_j["in_family"] & ep_j["label_available"]]
R(f"    MOM_FAMILY labeled episodes: {len(lbl):,} | L2 SUCCESS {int((lbl['L2_success']==1).sum())} / FAIL {int((lbl['L2_success']==0).sum())} / neutral-band {int(lbl['L2_success'].isna().sum())}")

# ---------------------------------------------------------------- write outputs
ep_cols = ["ticker", "play_type", "cohort", "in_family", "entry_date", "last_fire", "n_fires",
           "ta", "liq", "sec", "days_since_release", "state5",
           "rating", "route", "tier", "fa8_eff_date",
           "ROIC_Trailing", "CF_OA_P0", "F4_cfoa_pos", "Revenue_YoY_P0", "fin_release_date",
           "D_RSI", "T3_vol_ratio", "C_L1M", "T5_close_res", "C1_log_tv",
           "tech_date", "profit_2M", "profit_3M", "L2_success", "label_available"]
dl_cols = ["holding_id", "book", "ticker", "play_type", "pt_base", "entry_date", "exit_date", "feature_date",
           "n_buys", "n_sells", "buy_amt", "sell_amt", "net_ret", "L1_success", "exit_reason",
           "ta", "liq", "sec", "days_since_release", "state5",
           "rating", "route", "tier", "fa8_eff_date",
           "ROIC_Trailing", "CF_OA_P0", "F4_cfoa_pos", "Revenue_YoY_P0", "fin_release_date",
           "D_RSI", "T3_vol_ratio", "C_L1M", "T5_close_res", "C1_log_tv", "tech_date"]
# deals need pkl-context cols (ta/state5/...) — attach from pkl ASOF <= feature_date
sig_new = pickle.load(open(PKL_NEW, "rb")); sig_new["time"] = pd.to_datetime(sig_new["time"])
sigc = sig_new[["ticker", "time", "play_type", "ta", "liq", "sec", "days_since_release", "state5"]] \
         .sort_values(["ticker", "time"]).rename(columns={"play_type": "sig_play_type"})
con.register("dlj", dl_j.drop(columns=[c for c in ["ta","liq","sec","days_since_release","state5"] if c in dl_j.columns]))
con.register("sigc", sigc)
dl_j = con.execute("""
  SELECT d.*, s.time AS sig_date, s.sig_play_type, s.ta, s.liq, s.sec, s.days_since_release, s.state5
  FROM dlj d
  ASOF LEFT JOIN sigc s ON d.ticker = s.ticker AND s.time <= CAST(d.feature_date AS DATE)
""").df()
dl_j["sig_matches_deal"] = dl_j["sig_play_type"] == dl_j["pt_base"]
sigmatch = dl_j.groupby("pt_base")["sig_matches_deal"].mean() * 100
R("\n[F] deal↔signal linkage (pkl play_type at T-1 == book play_type): " +
  "  ".join(f"{k}:{v:.0f}%" for k, v in sigmatch.items()))
R("    (<100% expected: book applies extra gates/washout variants + dt5g-rebuilt pkl vs base-era book decisions)")

ep_out = ep_j[[c for c in ep_cols if c in ep_j.columns]]
dl_out = dl_j[[c for c in dl_cols + ["sig_date", "sig_play_type", "sig_matches_deal"] if c in dl_j.columns]]
ep_out.to_csv(f"{OUT}/momdeal_episodes_phase0.csv", index=False)
dl_out.to_csv(f"{OUT}/momdeal_deals_phase0.csv", index=False)
R(f"\n[write] {OUT}/momdeal_episodes_phase0.csv  ({len(ep_out):,} rows)")
R(f"[write] {OUT}/momdeal_deals_phase0.csv      ({len(dl_out):,} rows)")

# ---------------------------------------------------------------- verdict summary
R("\n[G] CP0 checklist snapshot")
R(f"    episode recon vs survey (base pkl, ±10%): {'PASS' if not recon_fail else 'FAIL: ' + ','.join(recon_fail)}")
R(f"    deal recon vs survey (±10%):              {'PASS' if not deal_recon_fail else 'FAIL: ' + ','.join(deal_recon_fail)}")
R(f"    8L coverage MOM_FAMILY episodes:          {cov_fam:.1f}%  ({'PASS >=80%' if cov_fam >= 80 else 'BELOW 80% — escalate'})")
R(f"    8L coverage ALL episodes:                 {cov_all_ep:.1f}%")
R(f"    8L coverage deals:                        {cov_dl:.1f}%")

open(f"{OUT}/phase0_report.txt", "w").write("\n".join(rep) + "\n")
print(f"\nreport -> {OUT}/phase0_report.txt")
