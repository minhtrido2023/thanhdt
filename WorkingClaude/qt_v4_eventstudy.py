#!/usr/bin/env python3
"""
qt_v4_eventstudy.py — QT v4 (Buffett) as a STOCK FILTER, measured per-signal
============================================================================
Reframe (user): QT v4 picks GOOD companies for long-term holding. Measure the
QUALITY OF THE PICKS at the stock/event level — NOT portfolio NAV/Sharpe/Calmar
(which drag in capital constraints and obscure the filter's real signal).

Three questions:
  (1) WHEN TO BUY  — entry signals (VALUE / GARP paths), are the picks good?
  (2) LONG-TERM OUTCOME — forward return at 3M/6M/1Y/2Y/3Y, vs VNINDEX, win-rate
  (3) WHEN TO EXIT — do QT v4 exit rules beat just holding to a fixed horizon?

Method: event study. Each entry = first day the QT v4 entry signal fires for a
ticker after being off (distinct episode), equal-weight, unlimited capital.
Forward returns point-in-time from Close; exit rules applied per-position.
NO portfolio, NO cash, NO Sharpe. Just: what happens to the stocks it picks.

Reuses backtest_qt_v4.py's exact signal definitions + data (panel pkl, fa_ratings_lh,
fin cache). Output: data/qt_v4_eventstudy.md
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import os, subprocess, tempfile, pickle
from io import StringIO
import numpy as np, pandas as pd

WORKDIR=r"/home/trido/thanhdt/WorkingClaude"
PROJECT="lithe-record-440915-m9"
BQ_BIN=r"bq"
HOR=[(63,"3M"),(126,"6M"),(252,"1Y"),(504,"2Y"),(756,"3Y")]

def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as f:
        f.write(sql); tmp=f.name
    try:
        cmd=f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=200000'
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=600,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    return pd.read_csv(StringIO(r.stdout.strip()))

def main():
    lines=[]; P=lambda s="":(print(s),lines.append(s))

    # ── load data ─────────────────────────────────────────────────────────
    fa=pd.read_csv(os.path.join(WORKDIR,"fa_ratings_lh.csv"),parse_dates=["time","Release_Date"])
    fa=fa.sort_values(["ticker","quarter"]).reset_index(drop=True)
    fa["eff_release"]=fa["Release_Date"].fillna(fa["time"]+pd.Timedelta(days=60))
    # rolling pct_AB (>=12Q history) per ticker
    fa["is_ab"]=fa["tier"].isin(["A","B"]).astype(int)
    fa["cum_ab"]=fa.groupby("ticker")["is_ab"].cumcsum() if False else fa.groupby("ticker")["is_ab"].cumsum()
    fa["qnum"]=fa.groupby("ticker").cumcount()+1
    fa["pct_AB"]=fa["cum_ab"]/fa["qnum"]*100
    fa["valid_hist"]=fa["qnum"]>=12

    panel=pickle.load(open(os.path.join(WORKDIR,"qt_panel_2014_2026.pkl"),"rb"))
    panel["time"]=pd.to_datetime(panel["time"])
    panel=panel.sort_values(["ticker","time"]).reset_index(drop=True)
    panel["hi52"]=panel.groupby("ticker")["Close"].transform(lambda x:x.rolling(252,min_periods=60).max())
    panel["dd52"]=(panel["Close"]/panel["hi52"]-1)*100
    panel["pe_z"]=((panel["PE"]-panel["PE_MA5Y"])/panel["PE_SD5Y"].replace(0,np.nan)).clip(-10,10)
    panel["pb_z"]=((panel["PB"]-panel["PB_MA5Y"])/panel["PB_SD5Y"].replace(0,np.nan)).clip(-10,10)
    panel["vs200"]=(panel["Close"]/panel["MA200"]-1)*100
    panel["liqv"]=panel["Volume_3M_P50"]*panel["Close"]

    fin=pickle.load(open(os.path.join(WORKDIR,"qt_v4_fin.pkl"),"rb"))
    fin["eff_release"]=pd.to_datetime(fin["Release_Date"]).fillna(pd.to_datetime(fin["q_time"])+pd.Timedelta(days=60))
    fin=fin.sort_values(["ticker","eff_release"])
    fin["prev_NP_R"]=fin.groupby("ticker")["NP_R"].shift(1)
    fin["prev_Rev"]=fin.groupby("ticker")["Revenue_YoY_P0"].shift(1)

    # ── as-of merge FA tier/pct_AB/score + fin onto panel ─────────────────
    panel=panel.sort_values("time")
    fa_a=fa.sort_values("eff_release")
    panel=pd.merge_asof(panel,fa_a[["ticker","eff_release","tier","pct_AB","valid_hist","score"]]
                        .rename(columns={"eff_release":"time"}),on="time",by="ticker",direction="backward")
    fin_a=fin.sort_values("eff_release")[["ticker","eff_release","PEG","NP_R","Revenue_YoY_P0","prev_NP_R","prev_Rev"]]\
            .rename(columns={"eff_release":"time"})
    panel=pd.merge_asof(panel,fin_a,on="time",by="ticker",direction="backward")
    panel=panel.sort_values(["ticker","time"]).reset_index(drop=True)

    # ── QT v4 entry + exit flags (vectorized) ─────────────────────────────
    q_gate=(panel["pct_AB"]>=70)&(panel["valid_hist"])&(panel["tier"].isin(["A","B"]))&(panel["liqv"]>=5e9)
    v_under=((panel["pe_z"]<-1)|(panel["pb_z"]<-1)|(panel["dd52"]<-30))
    v_notknife=((panel["vs200"]>0)|(panel["dd52"]>-20))
    value_pass=v_under&v_notknife
    garp_pass=((panel["PEG"]>0)&(panel["PEG"]<=1.0)&(panel["NP_R"]>=0.20)&(panel["Revenue_YoY_P0"]>=0.20)
               &(panel["PE"]<25)&(panel["vs200"]>0))
    panel["entry"]=q_gate&(value_pass|garp_pass)
    panel["path"]=np.where(garp_pass&~value_pass,"GARP",np.where(value_pass&~garp_pass,"VALUE","BOTH"))
    # exit flags
    panel["x_fa"]=panel["tier"].isin(["C","D","E"])
    panel["x_ovr"]=(panel["pe_z"]>2.5)&(panel["pb_z"]>1.5)
    panel["x_growth"]=((panel["NP_R"]*100<-15)&(panel["Revenue_YoY_P0"]*100<-15)
                       &(panel["prev_NP_R"]*100<-15)&(panel["prev_Rev"]*100<-15))
    panel["any_exit"]=panel["x_fa"]|panel["x_ovr"]|panel["x_growth"]

    # ── VNINDEX for benchmarking ──────────────────────────────────────────
    vni=bq_query("SELECT t.time,t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time>='2014-01-01' AND t.Close>100 ORDER BY t.time")
    vni["time"]=pd.to_datetime(vni["time"]); vni_s=vni.set_index("time")["Close"]

    # ── build entry EVENTS (fresh trigger: entry True after False) ────────
    events=[]
    for tk,g in panel.groupby("ticker"):
        g=g.reset_index(drop=True)
        e=g["entry"].values
        cl=g["Close"].values; tm=g["time"].values; ax=g["any_exit"].values
        xfa=g["x_fa"].values; xovr=g["x_ovr"].values; xg=g["x_growth"].values
        for i in range(len(g)):
            if e[i] and (i==0 or not e[i-1]):  # fresh entry
                ep=cl[i]
                if not np.isfinite(ep) or ep<=0: continue
                ev={"ticker":tk,"date":pd.Timestamp(tm[i]),"path":g["path"].values[i],
                    "pe_z":g["pe_z"].values[i],"entry_px":ep}
                # forward fixed-horizon returns
                for H,nm in HOR:
                    j=i+H
                    ev[f"r_{nm}"]=(cl[j]/ep-1)*100 if j<len(g) and np.isfinite(cl[j]) and cl[j]>0 else np.nan
                # rule-based exit (first any_exit after entry)
                xi=None
                for j in range(i+1,len(g)):
                    if ax[j]: xi=j; break
                if xi is not None:
                    ev["exit_ret"]=(cl[xi]/ep-1)*100; ev["hold_d"]=(pd.Timestamp(tm[xi])-pd.Timestamp(tm[i])).days
                    ev["exit_reason"]=("FA_DEGRADE" if xfa[xi] else "OVERVALUED" if xovr[xi] else "GROWTH_BROKEN")
                else:
                    ev["exit_ret"]=(cl[-1]/ep-1)*100; ev["hold_d"]=(pd.Timestamp(tm[-1])-pd.Timestamp(tm[i])).days
                    ev["exit_reason"]="STILL_OPEN"
                events.append(ev)
    ev=pd.DataFrame(events)
    # excess vs VNI at each horizon
    vni_arr=vni_s.reindex(panel["time"].drop_duplicates().sort_values()).ffill()
    def vni_fwd(d,H):
        idx=vni_s.index.searchsorted(d)
        if idx>=len(vni_s): return np.nan
        j=idx+H
        if j>=len(vni_s): return np.nan
        return (vni_s.iloc[j]/vni_s.iloc[idx]-1)*100
    for H,nm in HOR:
        ev[f"vni_{nm}"]=ev["date"].apply(lambda d: vni_fwd(d,H))
        ev[f"exc_{nm}"]=ev[f"r_{nm}"]-ev[f"vni_{nm}"]

    P("# QT v4 (Buffett) as a FILTER — per-signal event study")
    P("")
    P(f"Entry events (fresh triggers) {len(ev):,} | tickers {ev['ticker'].nunique()} "
      f"| {ev['date'].min().date()}→{ev['date'].max().date()}")
    P(f"Path mix: "+", ".join(f"{p}={int((ev['path']==p).sum())}" for p in ev['path'].unique()))
    P("")

    # ── (1)+(2) forward outcome by horizon ────────────────────────────────
    P("## (1)(2) Forward outcome of picks — hold to fixed horizon")
    P(f"{'horizon':<8}{'N':>6}{'med':>8}{'mean':>8}{'win%':>7}{'vsVNI med':>10}{'beatVNI%':>9}")
    P("-"*56)
    for H,nm in HOR:
        r=ev[f"r_{nm}"].dropna(); exc=ev[f"exc_{nm}"].dropna()
        if len(r)<20: continue
        P(f"{nm:<8}{len(r):>6}{r.median():>+7.1f}%{r.mean():>+7.1f}%{(r>0).mean()*100:>6.0f}%"
          f"{exc.median():>+9.1f}%{(exc>0).mean()*100:>8.0f}%")
    P("")
    P("## By entry path (forward 1Y / 2Y median, beat-VNI%)")
    for p in ["VALUE","GARP","BOTH"]:
        g=ev[ev["path"]==p]
        if len(g)<15: continue
        P(f"  {p:<6} N={len(g):>4}  1Y med={g['r_1Y'].median():+6.1f}% (beat {100*(g['exc_1Y']>0).mean():.0f}%)"
          f"  2Y med={g['r_2Y'].median():+6.1f}% (beat {100*(g['exc_2Y']>0).mean():.0f}%)")
    P("")

    # ── (3) exit rules vs fixed-horizon holds ─────────────────────────────
    P("## (3) WHEN TO EXIT — QT v4 rule-based exit vs holding to fixed horizon")
    closed=ev[ev["exit_reason"]!="STILL_OPEN"]
    P(f"Rule-based exits: {len(closed)}/{len(ev)} closed; {len(ev)-len(closed)} STILL_OPEN at data end")
    P(f"  rule exit:  median ret {closed['exit_ret'].median():+.1f}%  mean {closed['exit_ret'].mean():+.1f}%  "
      f"median hold {closed['hold_d'].median():.0f}d  win {(closed['exit_ret']>0).mean()*100:.0f}%")
    for H,nm in HOR:
        r=ev[f"r_{nm}"].dropna()
        P(f"  hold {nm:<3}:  median ret {r.median():+.1f}%  mean {r.mean():+.1f}%  win {(r>0).mean()*100:.0f}%  (N={len(r)})")
    P("")
    P("Exit reason breakdown:")
    P(f"{'reason':<16}{'N':>5}{'med ret':>9}{'mean':>8}{'med hold':>10}{'win%':>7}")
    for rs,g in ev.groupby("exit_reason"):
        P(f"{rs:<16}{len(g):>5}{g['exit_ret'].median():>+8.1f}%{g['exit_ret'].mean():>+7.1f}%{g['hold_d'].median():>9.0f}d{(g['exit_ret']>0).mean()*100:>6.0f}%")
    P("")
    P("Read: if 'rule exit' mean/win ≈ or > best fixed-horizon hold, the exit rules add value.")
    P("If holding longer (2Y/3Y) beats rule exit, the rules exit too early (cut compounders).")
    P("")
    ev.to_csv(os.path.join(WORKDIR,"data","qt_v4_events.csv"),index=False)
    with open(os.path.join(WORKDIR,"data","qt_v4_eventstudy.md"),"w",encoding="utf-8") as f:
        f.write("\n".join(lines))
    P("Saved data/qt_v4_eventstudy.md + data/qt_v4_events.csv")

if __name__=="__main__":
    main()
