#!/usr/bin/env python3
"""
backtest_qt_v4.py — "Buffett Quality Compounder"
=================================================
Sửa hai weakness của QT v1:
  (i)  Entry chậm  → thêm GARP path (PEG ≤ 1 + growth ≥ 20%) song song với VALUE
  (ii) Hold ngắn   → bỏ TIME EXIT, bỏ TRAIL STOP, chấp nhận DD lớn miễn FA còn tốt

Entry (OR):
  Path VALUE   : (PE_z<-1 OR PB_z<-1 OR DD52w<-30) AND (Close>MA200 OR DD52w>-20)
  Path GARP    : PEG∈(0,1] AND NP_YoY≥20% AND Rev_YoY≥20% AND PE<25 AND Close>MA200
Universe: ≥70% A+B (≥12Q lịch sử), latest A/B, liq ≥5B/day

Exit (chỉ 3):
  FA_DEGRADE        : tier xuống C/D/E ở quý kế
  OVERVALUED_EXIT   : PE_z>+2.5 AND PB_z>+1.5
  GROWTH_BROKEN     : NP_YoY<-15% AND Rev_YoY<-15% trong 2 quý liên tiếp
  (KHÔNG trail-stop / hard-stop / time-exit / MA200 break / RSI)

Position sizing:
  Max 8 vị thế, initial 10% NAV/pos
  Average-down: lỗ ≤-20% từ entry AND FA vẫn A/B AND PE_z giảm thêm → +5% NAV
                Tối đa 2 lần averaging → cap 20% NAV/pos
Blacklist 90 ngày sau FA_DEGRADE/GROWTH_BROKEN; 30 ngày sau OVERVALUED_EXIT
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile, sys, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import pandas as pd, numpy as np

PROJECT = "lithe-record-440915-m9"
BQ = r"bq"
INIT_NAV = 50e9

def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = f'type "{tmp}" | "{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=10000000'
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode != 0: raise RuntimeError(r.stderr[:500])
    return pd.read_csv(StringIO(r.stdout.strip()))

# ─── 1. Quality universe (giữ v1) ────────────────────────────────────────
print("[1] Building quality universe from FA history ...", flush=True)
fa = pd.read_csv("data/fa_ratings_lh.csv", parse_dates=["time","Release_Date"])
fa = fa.sort_values(["ticker","quarter"]).reset_index(drop=True)

quality_at_q = {}
for tk, g in fa.groupby("ticker"):
    g = g.sort_values("quarter").reset_index(drop=True)
    for i, row in g.iterrows():
        if i < 12: continue
        history = g.iloc[:i+1]
        pct_ab = (history["tier"].isin(["A","B"])).sum() / len(history) * 100
        quality_at_q[(tk, row["quarter"])] = {
            "pct_AB": pct_ab,
            "latest_tier": row["tier"],
            "score": row["score"],
            "sub": row["sub"],
        }
print(f"  Quality lookup built: {len(quality_at_q):,} entries")

print("\n[2] Loading TA panel cache ...", flush=True)
with open("data/qt_panel_2014_2026.pkl","rb") as f:
    panel = pickle.load(f)
panel["time"] = pd.to_datetime(panel["time"])
print(f"  Panel: {len(panel):,} rows")

# Compute derived features
panel = panel.sort_values(["ticker","time"]).reset_index(drop=True)
panel["hi_52w"] = panel.groupby("ticker")["Close"].transform(lambda x: x.rolling(252, min_periods=60).max())
panel["dd_52w_pct"] = (panel["Close"]/panel["hi_52w"] - 1) * 100
panel["pe_z"] = ((panel["PE"]-panel["PE_MA5Y"])/panel["PE_SD5Y"].replace(0,np.nan)).clip(-10,10)
panel["pb_z"] = ((panel["PB"]-panel["PB_MA5Y"])/panel["PB_SD5Y"].replace(0,np.nan)).clip(-10,10)
panel["vs_MA200_pct"] = (panel["Close"]/panel["MA200"] - 1) * 100

# ─── 3. Pull quarterly financial (PEG/NP_R/Revenue_YoY) ──────────────────
fin_cache = "data/qt_v4_fin.pkl"
if os.path.exists(fin_cache):
    with open(fin_cache,"rb") as f: fin = pickle.load(f)
    print(f"  Loaded financial cache: {len(fin):,} rows")
else:
    print("\n[3] Pulling quarterly financial fields ...", flush=True)
    fin = bq_query("""
    SELECT f.ticker, f.quarter, f.time AS q_time, f.Release_Date,
           f.PEG, f.NP_R, f.Revenue_YoY_P0, f.PE
    FROM tav2_bq.ticker_financial AS f
    WHERE f.time >= '2010-01-01'
    """)
    fin["q_time"] = pd.to_datetime(fin["q_time"])
    fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
    fin["eff_release"] = fin["Release_Date"].fillna(fin["q_time"] + pd.Timedelta(days=60))
    with open(fin_cache,"wb") as f: pickle.dump(fin, f)
    print(f"  Pulled + cached: {len(fin):,} rows")

# Per-ticker financial timeline sorted by eff_release
fin_map = {}
for tk, g in fin.groupby("ticker"):
    fin_map[tk] = g.sort_values("eff_release").reset_index(drop=True)

# FA release timeline (for tier lookup)
fa_release_map = {}
for tk, g in fa.groupby("ticker"):
    g = g.sort_values("time").reset_index(drop=True)
    g["eff_release"] = g["Release_Date"].fillna(g["time"] + pd.Timedelta(days=60))
    fa_release_map[tk] = g[["eff_release","quarter","tier","score","sub"]].copy()

def get_fa_at(tk, dt):
    if tk not in fa_release_map: return None
    g = fa_release_map[tk]
    av = g[g["eff_release"] <= dt]
    if len(av) == 0: return None
    last = av.iloc[-1]
    q = last["quarter"]
    qi = quality_at_q.get((tk, q))
    return qi  # contains pct_AB, latest_tier, sub

def get_fin_at(tk, dt):
    """Returns dict with PEG, NP_R, Revenue_YoY_P0, prev_NP_R, prev_Rev_YoY."""
    if tk not in fin_map: return None
    g = fin_map[tk]
    av = g[g["eff_release"] <= dt]
    if len(av) == 0: return None
    last = av.iloc[-1]
    prev = av.iloc[-2] if len(av) >= 2 else None
    return {
        "PEG": last["PEG"],
        "NP_R": last["NP_R"],
        "Rev_YoY": last["Revenue_YoY_P0"],
        "PE": last["PE"],
        "prev_NP_R": prev["NP_R"] if prev is not None else np.nan,
        "prev_Rev_YoY": prev["Revenue_YoY_P0"] if prev is not None else np.nan,
    }

# ─── 4. Pivots for daily lookup ──────────────────────────────────────────
print("\n[4] Setting up pivots ...", flush=True)
px_close = panel.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill()
px_open  = panel.pivot_table(index="time", columns="ticker", values="Open",  aggfunc="first").sort_index().ffill()
ma200    = panel.pivot_table(index="time", columns="ticker", values="MA200", aggfunc="first").sort_index().ffill()
pe_z     = panel.pivot_table(index="time", columns="ticker", values="pe_z",  aggfunc="first").sort_index().ffill()
pb_z     = panel.pivot_table(index="time", columns="ticker", values="pb_z",  aggfunc="first").sort_index().ffill()
dd_52w   = panel.pivot_table(index="time", columns="ticker", values="dd_52w_pct", aggfunc="first").sort_index().ffill()
vs_ma200 = panel.pivot_table(index="time", columns="ticker", values="vs_MA200_pct", aggfunc="first").sort_index().ffill()
pe_daily = panel.pivot_table(index="time", columns="ticker", values="PE", aggfunc="first").sort_index().ffill()
liq      = panel.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().ffill()

trading_days = sorted(panel["time"].unique())

# ─── 5. Backtest ─────────────────────────────────────────────────────────
print("\n[5] Running QT v4 (Buffett spec) backtest ...", flush=True)

MAX_POSITIONS    = 8
INIT_PCT         = 0.10
AVG_DOWN_PCT     = 0.05
MAX_POS_PCT      = 0.20
AVG_DOWN_TRIGGER = -20.0   # %
MAX_AVG_DOWN     = 2
LIQ_CAP_PCT      = 0.20
MAX_FILL_DAYS    = 5
SLIP_IN          = 0.001
SLIP_OUT         = 0.0015
TAX_SALE         = 0.001
DEPOSIT_RATE     = 0.01
BL_DAYS_FA       = 90
BL_DAYS_OVR      = 30
PE_Z_OVR         = 2.5
PB_Z_OVR         = 1.5
GROWTH_BAD_THR   = -15.0  # %

start_dt = pd.Timestamp("2014-04-01")
end_dt   = pd.Timestamp("2026-05-13")
sim_days = [d for d in trading_days if start_dt <= d <= end_dt]

cash = INIT_NAV
positions = {}      # tk → {entry_dt, entry_px, shares, entry_pe_z, n_avg_down, total_cost}
blacklist = {}
nav_history = []
trades = []
daily_rate = (1+DEPOSIT_RATE)**(1/365.25) - 1

pending_buys  = []  # {ticker, type: NEW|AVGDN, signal_dt}
pending_sells = []

vni = bq_query("""SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time >= '2014-01-01' AND t.Close > 100 ORDER BY t.time""")
vni["time"] = pd.to_datetime(vni["time"])
vni_px = vni.set_index("time")["Close"]

print(f"  Sim window: {start_dt.date()} → {end_dt.date()} ({len(sim_days)} days)", flush=True)

for i, dt in enumerate(sim_days):
    if i % 500 == 0:
        mtm = sum(p["shares"] * px_close.at[dt, tk] for tk,p in positions.items()
                  if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav = cash + mtm
        print(f"  Day {i}/{len(sim_days)} ({dt.date()}): NAV={nav/1e9:.2f}B pos={len(positions)} cash={cash/1e9:.1f}B", flush=True)
    cash *= (1 + daily_rate)

    # T+1 Sells
    nps = []
    for s in pending_sells:
        tk = s["ticker"]
        if tk not in positions: continue
        if tk not in px_open.columns: continue
        fpx = px_open.at[dt, tk]
        if pd.isna(fpx) or fpx <= 0: nps.append(s); continue
        pos = positions[tk]
        gross = pos["shares"] * fpx * (1 - SLIP_OUT)
        net = gross * (1 - TAX_SALE)
        cash += net
        avg_entry = pos["total_cost"]/pos["shares"] if pos["shares"]>0 else pos["entry_px"]
        trades.append({"dt":dt,"ticker":tk,"side":s["reason"],"shares":pos["shares"],
                       "px":fpx,"net":net,"entry_dt":pos["entry_dt"],"entry_px":avg_entry,
                       "ret_pct":(fpx/avg_entry-1)*100,"hold_days":(dt-pos["entry_dt"]).days,
                       "n_avg_down":pos["n_avg_down"]})
        bl_days = BL_DAYS_OVR if s["reason"]=="OVERVALUED" else BL_DAYS_FA
        blacklist[tk] = dt + pd.Timedelta(days=bl_days)
        del positions[tk]
    pending_sells = nps

    # T+1 Buys (new + avg down)
    npb = []
    for b in pending_buys:
        tk = b["ticker"]; btype = b["type"]
        if tk not in px_open.columns: continue
        fpx = px_open.at[dt, tk]
        if pd.isna(fpx) or fpx <= 0: npb.append(b); continue

        mtm = sum(p["shares"]*px_close.at[dt,t_] for t_,p in positions.items()
                  if t_ in px_close.columns and pd.notna(px_close.at[dt,t_]))
        nav_now = cash + mtm

        if btype == "NEW":
            if tk in positions: continue
            if len(positions) >= MAX_POSITIONS: continue
            if tk in blacklist and blacklist[tk] > dt: continue
            target = nav_now * INIT_PCT
        else:  # AVGDN
            if tk not in positions: continue
            pos = positions[tk]
            if pos["n_avg_down"] >= MAX_AVG_DOWN: continue
            cur_value = pos["shares"] * px_close.at[dt, tk] if pd.notna(px_close.at[dt, tk]) else 0
            if cur_value/nav_now >= MAX_POS_PCT: continue
            target = nav_now * AVG_DOWN_PCT
            target = min(target, nav_now*MAX_POS_PCT - cur_value)
            if target <= 0: continue

        adv = liq.at[dt, tk] if tk in liq.columns else 0
        if pd.isna(adv) or adv <= 0: adv = 1e6
        cap = LIQ_CAP_PCT * adv * MAX_FILL_DAYS * fpx
        alloc = min(target, cap)
        if alloc < 1e6: continue

        eff_px = fpx * (1 + SLIP_IN)
        shares = alloc / eff_px
        cost = shares * eff_px
        if cost > cash: continue
        cash -= cost

        if btype == "NEW":
            positions[tk] = {"entry_dt":dt, "entry_px":fpx, "shares":shares,
                              "entry_pe_z": pe_z.at[dt,tk] if tk in pe_z.columns else np.nan,
                              "n_avg_down":0, "total_cost":cost}
            trades.append({"dt":dt,"ticker":tk,"side":"BUY","shares":shares,"px":fpx,
                            "net":-cost,"entry_dt":dt,"entry_px":fpx,"ret_pct":0,
                            "hold_days":0,"n_avg_down":0})
        else:
            pos = positions[tk]
            pos["shares"] += shares
            pos["total_cost"] += cost
            pos["n_avg_down"] += 1
            trades.append({"dt":dt,"ticker":tk,"side":f"AVGDN_{pos['n_avg_down']}",
                            "shares":shares,"px":fpx,"net":-cost,
                            "entry_dt":pos["entry_dt"],"entry_px":pos["total_cost"]/pos["shares"],
                            "ret_pct":0,"hold_days":(dt-pos["entry_dt"]).days,
                            "n_avg_down":pos["n_avg_down"]})
    pending_buys = []

    # Check exits + avg-down triggers
    for tk, pos in list(positions.items()):
        if tk not in px_close.columns: continue
        p_today = px_close.at[dt, tk]
        if pd.isna(p_today): continue

        exit_reason = None
        fa_info  = get_fa_at(tk, dt)
        fin_info = get_fin_at(tk, dt)

        # FA degrade
        if fa_info is not None and fa_info["latest_tier"] in ("C","D","E"):
            exit_reason = "FA_DEGRADE"
        # Overvalued
        if exit_reason is None:
            pez = pe_z.at[dt, tk] if tk in pe_z.columns else np.nan
            pbz = pb_z.at[dt, tk] if tk in pb_z.columns else np.nan
            if pd.notna(pez) and pd.notna(pbz) and pez > PE_Z_OVR and pbz > PB_Z_OVR:
                exit_reason = "OVERVALUED"
        # Growth broken (2 quý liên tiếp âm sâu)
        if exit_reason is None and fin_info is not None:
            if (pd.notna(fin_info["NP_R"]) and pd.notna(fin_info["Rev_YoY"])
                and pd.notna(fin_info["prev_NP_R"]) and pd.notna(fin_info["prev_Rev_YoY"])
                and fin_info["NP_R"]*100 < GROWTH_BAD_THR and fin_info["Rev_YoY"]*100 < GROWTH_BAD_THR
                and fin_info["prev_NP_R"]*100 < GROWTH_BAD_THR and fin_info["prev_Rev_YoY"]*100 < GROWTH_BAD_THR):
                exit_reason = "GROWTH_BROKEN"

        if exit_reason:
            pending_sells.append({"ticker":tk,"reason":exit_reason})
            continue

        # Avg-down trigger
        if pos["n_avg_down"] < MAX_AVG_DOWN:
            avg_entry = pos["total_cost"]/pos["shares"]
            ret_pct = (p_today/avg_entry - 1)*100
            if ret_pct <= AVG_DOWN_TRIGGER:
                pez_now = pe_z.at[dt, tk] if tk in pe_z.columns else np.nan
                if (fa_info is not None and fa_info["latest_tier"] in ("A","B")
                    and pd.notna(pez_now) and pd.notna(pos["entry_pe_z"])
                    and pez_now < pos["entry_pe_z"] - 0.3):  # giảm ≥ 0.3 std
                    # đẩy pending avg-down (chỉ 1 lần/ngày)
                    if not any(b["ticker"]==tk for b in pending_buys):
                        pending_buys.append({"ticker":tk,"type":"AVGDN","signal_dt":dt})

    # Scan for NEW entries (only if room)
    if len(positions) + sum(1 for b in pending_buys if b["type"]=="NEW") < MAX_POSITIONS:
        slots_left = MAX_POSITIONS - len(positions) - sum(1 for b in pending_buys if b["type"]=="NEW")
        # Score candidates per day and take top N
        candidates = []
        for tk in px_close.columns:
            if tk in positions: continue
            if tk in blacklist and blacklist[tk] > dt: continue
            if any(b["ticker"]==tk for b in pending_buys): continue

            fa_info = get_fa_at(tk, dt)
            if fa_info is None: continue
            if fa_info["pct_AB"] < 70: continue
            if fa_info["latest_tier"] not in ("A","B"): continue

            adv_vnd = liq.at[dt, tk] if tk in liq.columns else 0
            p = px_close.at[dt, tk]
            if pd.isna(p) or pd.isna(adv_vnd) or adv_vnd*p < 5e9: continue

            pez = pe_z.at[dt, tk] if tk in pe_z.columns else np.nan
            pbz = pb_z.at[dt, tk] if tk in pb_z.columns else np.nan
            ddv = dd_52w.at[dt, tk] if tk in dd_52w.columns else np.nan
            vs200 = vs_ma200.at[dt, tk] if tk in vs_ma200.columns else np.nan
            pe_now = pe_daily.at[dt, tk] if tk in pe_daily.columns else np.nan

            # Path VALUE
            v_under = ((pd.notna(pez) and pez < -1.0)
                       or (pd.notna(pbz) and pbz < -1.0)
                       or (pd.notna(ddv) and ddv < -30))
            v_not_falling_knife = (pd.notna(vs200) and vs200 > 0) or (pd.notna(ddv) and ddv > -20)
            value_pass = v_under and v_not_falling_knife

            # Path GARP
            fin_info = get_fin_at(tk, dt)
            garp_pass = False
            if fin_info is not None:
                peg = fin_info["PEG"]; npyoy = fin_info["NP_R"]; revyoy = fin_info["Rev_YoY"]
                if (pd.notna(peg) and 0 < peg <= 1.0
                    and pd.notna(npyoy) and npyoy >= 0.20
                    and pd.notna(revyoy) and revyoy >= 0.20
                    and pd.notna(pe_now) and pe_now < 25
                    and pd.notna(vs200) and vs200 > 0):
                    garp_pass = True

            if not (value_pass or garp_pass): continue

            # Score: prefer lower PE_z + higher fa score
            score = -(pez if pd.notna(pez) else 0) * 2 + fa_info["score"]/10
            if garp_pass: score += 2
            candidates.append((tk, score, "VALUE" if value_pass else "GARP"))

        candidates.sort(key=lambda x: x[1], reverse=True)
        for tk, sc, path in candidates[:slots_left]:
            pending_buys.append({"ticker":tk,"type":"NEW","signal_dt":dt,"path":path})

    # NAV
    mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items()
              if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
    nav = cash + mtm
    nav_history.append({"date":dt,"nav":nav,"cash":cash,"equity":mtm,"n_pos":len(positions)})

nav_df = pd.DataFrame(nav_history).set_index("date")
trades_df = pd.DataFrame(trades)
print(f"\n  Sim complete: {len(trades_df)} trades, final NAV={nav_df['nav'].iloc[-1]/1e9:.2f}B")

# ─── 6. Metrics ──────────────────────────────────────────────────────────
def metrics(nav, start, end):
    s = nav[(nav.index>=start) & (nav.index<=end)]
    if len(s) < 30: return None
    yrs = (s.index[-1]-s.index[0]).days/365.25
    cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs) - 1
    rets = s.pct_change().dropna()
    spy = len(rets)/yrs
    sh = rets.mean()/rets.std()*np.sqrt(spy) if rets.std()>0 else 0
    dd = (s - s.cummax())/s.cummax()
    mdd = dd.min()
    calmar = cagr/abs(mdd) if mdd<0 else 0
    return {"CAGR":cagr*100,"Sharpe":sh,"MaxDD":mdd*100,"Calmar":calmar}

vni_aligned = vni_px.reindex(nav_df.index).ffill()
periods = [
    ("FULL_12y",  pd.Timestamp("2014-04-01"), pd.Timestamp("2026-05-13")),
    ("PRE_2024",  pd.Timestamp("2014-04-01"), pd.Timestamp("2023-12-31")),
    ("OOS_2024+", pd.Timestamp("2024-01-01"), pd.Timestamp("2026-05-13")),
    ("Y2022",     pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Q1_2026",   pd.Timestamp("2025-12-30"), pd.Timestamp("2026-03-30")),
]
print("\n" + "="*100)
print(f"  {'Period':<14}{'CAGR':>10}{'Sharpe':>10}{'MaxDD':>10}{'Calmar':>10}{'VNI':>10}{'alpha':>10}")
for nm, ps, pe in periods:
    m = metrics(nav_df["nav"], ps, pe); vm = metrics(vni_aligned, ps, pe)
    if m is None or vm is None: continue
    a = m["CAGR"] - vm["CAGR"]
    print(f"  {nm:<14}{m['CAGR']:>+9.2f}%{m['Sharpe']:>+10.2f}{m['MaxDD']:>+9.2f}%{m['Calmar']:>+10.2f}{vm['CAGR']:>+9.2f}%{a:>+9.2f}pp")

if len(trades_df) > 0:
    exits = trades_df[~trades_df["side"].isin(["BUY","AVGDN_1","AVGDN_2"])]
    print(f"\n  --- Trade summary ---")
    print(f"  Total events: {len(trades_df)}  | Buys: {(trades_df['side']=='BUY').sum()}  | Avg-downs: {(trades_df['side'].str.startswith('AVGDN')).sum()}  | Exits: {len(exits)}")
    if len(exits) > 0:
        for rs, g in exits.groupby("side"):
            print(f"    {rs:<14}: N={len(g):3d}, avg_ret={g['ret_pct'].mean():+6.1f}%, median_hold={g['hold_days'].median():.0f}d, WR={(g['ret_pct']>0).mean()*100:.1f}%")
        print(f"  Avg hold (exits): {exits['hold_days'].mean():.0f}d | Avg return: {exits['ret_pct'].mean():+.2f}%")
        print(f"  Win rate: {(exits['ret_pct']>0).mean()*100:.1f}%")
        if len(exits) > 0:
            print(f"  Best: {exits['ret_pct'].max():+.1f}% ({exits.loc[exits['ret_pct'].idxmax(),'ticker']})")
            print(f"  Worst: {exits['ret_pct'].min():+.1f}% ({exits.loc[exits['ret_pct'].idxmin(),'ticker']})")
        per_tk = exits.groupby("ticker").agg(n=("ticker","size"),avg_ret=("ret_pct","mean"),
                                              total_ret=("ret_pct","sum"),avg_hold=("hold_days","mean"))
        per_tk = per_tk.sort_values("total_ret", ascending=False)
        print(f"\n  Top 15 by cum return:")
        for tk, r in per_tk.head(15).iterrows():
            print(f"    {tk:<7} N={int(r['n']):2d}  avg={r['avg_ret']:+6.1f}%  cum={r['total_ret']:+7.1f}%  hold={r['avg_hold']:.0f}d")

nav_df.to_csv("data/qt_v4_nav.csv")
trades_df.to_csv("data/qt_v4_trades.csv", index=False)
print("\nSaved: qt_v4_nav.csv, qt_v4_trades.csv")
