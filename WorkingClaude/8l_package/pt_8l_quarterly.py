#!/usr/bin/env python3
"""pt_8l_quarterly.py — paper-trade tracker for the 8L top-20 recommendations, by quarter.
  snapshot : freeze current rank_8l top-N as this quarter's cohort (entry date/price) — run at quarter start.
  review   : pull current prices, compute return per pick vs VNINDEX since entry — run at quarter end.
Equal-weight, long-only, hold-to-review. Output: data/pt_8l/cohort_<Q>.csv + review_<Q>.md (+ optional Telegram).
Usage: python pt_8l_quarterly.py snapshot [--topn 20]
       python pt_8l_quarterly.py review [--cohort 2026Q2] [--telegram]
"""
import warnings; warnings.filterwarnings("ignore")
import sys, os, argparse, subprocess, tempfile, datetime, glob
from io import StringIO
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np
WORKDIR=os.environ.get("WORKDIR_8L", r"/home/trido/thanhdt/WorkingClaude")
PROJECT="lithe-record-440915-m9"; BQ=os.environ.get("BQ_BIN", (r"bq" if os.name=="nt" else "bq"))
PTDIR=os.path.join(WORKDIR,"data","pt_8l"); os.makedirs(PTDIR,exist_ok=True)
def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as f: f.write(sql); tmp=f.name
    try: r=subprocess.run(f'{"type" if os.name=="nt" else "cat"} "{tmp}" | "{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=100000',capture_output=True,text=True,timeout=300,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    return pd.read_csv(StringIO(r.stdout.strip()))
def qlabel(d=None):
    d=d or datetime.date.today(); return f"{d.year}Q{(d.month-1)//3+1}"
def prices(tickers):
    tks="','".join(tickers)
    p=bq(f"""WITH l AS (SELECT t.ticker,MAX(t.time) mx FROM tav2_bq.ticker t WHERE t.ticker IN ('{tks}') GROUP BY t.ticker)
    SELECT t.ticker, t.Close, t.time, t.VNINDEX FROM tav2_bq.ticker t JOIN l ON l.ticker=t.ticker AND l.mx=t.time""")
    return p

def snapshot(topn):
    r=pd.read_csv(os.path.join(WORKDIR,"data","rank_8l.csv")).sort_values("rank").head(topn)
    pr=prices(list(r["ticker"])).set_index("ticker")
    today=str(datetime.date.today()); q=qlabel()
    vni=float(pr["VNINDEX"].dropna().iloc[0]) if pr["VNINDEX"].notna().any() else np.nan
    rows=[]
    for _,x in r.iterrows():
        t=x["ticker"]; c=float(pr.loc[t,"Close"]) if t in pr.index else np.nan
        rows.append(dict(cohort=q,entry_date=today,ticker=t,rank=int(x["rank"]),score=x["score"],
            route=x["route"],verdict=x["verdict"],entry_close=round(c,0),vnindex_entry=round(vni,1)))
    out=pd.DataFrame(rows); fn=os.path.join(PTDIR,f"cohort_{q}.csv"); out.to_csv(fn,index=False)
    print(f"snapshot {q}: {len(out)} picks frozen @ {today} (VNINDEX {vni:.0f}) → {fn}")
    print(", ".join(out["ticker"]))

def review(cohort,telegram):
    fn=os.path.join(PTDIR,f"cohort_{cohort}.csv") if cohort else sorted(glob.glob(os.path.join(PTDIR,"cohort_*.csv")))[-1]
    c=pd.read_csv(fn); cohort=c["cohort"].iloc[0]
    pr=prices(list(c["ticker"])).set_index("ticker")
    vni_now=float(pr["VNINDEX"].dropna().iloc[0]) if pr["VNINDEX"].notna().any() else np.nan
    vni0=float(c["vnindex_entry"].iloc[0]); vni_ret=(vni_now/vni0-1)*100 if vni0 else np.nan
    c["now"]=c["ticker"].map(lambda t: float(pr.loc[t,"Close"]) if t in pr.index else np.nan)
    c["ret%"]=(c["now"]/c["entry_close"]-1)*100; c["exc%"]=c["ret%"]-vni_ret
    c=c.sort_values("ret%",ascending=False)
    avg=c["ret%"].mean(); med=c["ret%"].median(); win=(c["ret%"]>0).mean()*100; beat=(c["exc%"]>0).mean()*100
    L=[]; P=lambda s="":(print(s),L.append(s))
    P(f"# 8L paper-trade review — cohort {cohort}  (entry {c['entry_date'].iloc[0]} → {str(datetime.date.today())})")
    P(f"picks {len(c)} | avg {avg:+.1f}% · median {med:+.1f}% · win {win:.0f}% | VNINDEX {vni_ret:+.1f}% | beat-VNI {beat:.0f}% | excess(avg) {avg-vni_ret:+.1f}pp")
    P("")
    P(f"{'tkr':<6}{'route':<11}{'entry':>8}{'now':>8}{'ret%':>8}{'exc%':>8}")
    for _,x in c.iterrows():
        P(f"{x['ticker']:<6}{x['route']:<11}{x['entry_close']:>8.0f}{(x['now'] if pd.notna(x['now']) else 0):>8.0f}{x['ret%']:>+8.1f}{x['exc%']:>+8.1f}")
    P("")
    P(f"by route avg ret%: "+", ".join(f"{rt} {g['ret%'].mean():+.1f}%" for rt,g in c.groupby('route')))
    md="\n".join(L); open(os.path.join(PTDIR,f"review_{cohort}.md"),"w",encoding="utf-8").write(md)
    print("\nSaved",os.path.join(PTDIR,f"review_{cohort}.md"))
    if telegram:
        try:
            from telegram_recommend import send_telegram_text, load_config
            cfg=load_config()
            top3=c.head(3)[["ticker","ret%"]].apply(lambda r:f"{r['ticker']} {r['ret%']:+.0f}%",axis=1).tolist()
            bot3=c.tail(3)[["ticker","ret%"]].apply(lambda r:f"{r['ticker']} {r['ret%']:+.0f}%",axis=1).tolist()
            msg=(f"<b>📊 8L Paper-Trade Review — {cohort}</b>\n"
                 f"{len(c)} picks | avg <b>{avg:+.1f}%</b> · med {med:+.1f}% · win {win:.0f}%\n"
                 f"VNINDEX {vni_ret:+.1f}% → excess <b>{avg-vni_ret:+.1f}pp</b> (beat {beat:.0f}%)\n"
                 f"🏆 {' · '.join(top3)}\n🔻 {' · '.join(bot3)}")
            print(send_telegram_text(cfg["bot_token"],cfg["chat_id"],msg).get("ok"))
        except Exception as e: print("telegram skipped:",e)

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("mode",choices=["snapshot","review"])
    ap.add_argument("--topn",type=int,default=20); ap.add_argument("--cohort",default=None); ap.add_argument("--telegram",action="store_true")
    a=ap.parse_args()
    if a.mode=="snapshot": snapshot(a.topn)
    else: review(a.cohort,a.telegram)
