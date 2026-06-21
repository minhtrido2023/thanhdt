#!/usr/bin/env python3
"""rank_8l_daily_alert.py — run EOD after unified_screener.py + rank_8l.py.
Compares today's top-30 ranking vs yesterday's; if a SURPRISE upward move is detected (a name climbing
fast / newly entering top-30 / a big score jump), sends a Telegram report. Then stores today as baseline.
Surprise = upward signal = something improving (price dislocation cheaper, metric/liquidity rising).
Usage: python rank_8l_daily_alert.py [--topn 30] [--no-telegram]
"""
import warnings; warnings.filterwarnings("ignore")
import sys, os, os, argparse, datetime
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np
WORKDIR=os.environ.get("WORKDIR_8L", r"/home/trido/thanhdt/WorkingClaude")
CUR=os.path.join(WORKDIR,"data","rank_8l.csv")
PREV=os.path.join(WORKDIR,"data","rank_8l_prev.csv")
# ---- surprise thresholds (tunable) ----
TOPN=30
RANK_JUMP=8       # improved >=8 positions AND now in top-N
SCORE_JUMP=6.0    # score rose >=6 pts
NEW_FROM=45       # entered top-N from outside top-45 (or brand new) = surge

def main(topn,telegram):
    today=str(datetime.date.today())
    cur=pd.read_csv(CUR).copy(); cur["rank"]=cur.index+1 if "rank" not in cur else cur["rank"]
    cur=cur.sort_values("rank")
    if not os.path.exists(PREV):
        cur.to_csv(PREV,index=False); print("no prior baseline — stored today as baseline, no alert."); return
    prev=pd.read_csv(PREV)
    pm={r["ticker"]:(int(r["rank"]),float(r["score"])) for _,r in prev.iterrows()}
    try: SDET=pd.read_csv(os.path.join(WORKDIR,"data","unified_screener.csv")).set_index("ticker")["detail"].to_dict()
    except Exception: SDET={}
    alerts=[]
    for _,r in cur[cur["rank"]<=topn].iterrows():
        t=r["ticker"]; rk=int(r["rank"]); sc=float(r["score"])
        prk,psc=pm.get(t,(None,None))
        if prk is None:
            # newcomer to top-N (was outside the prior file entirely, or beyond NEW_FROM)
            alerts.append((t,r,"NEW→top%d"%topn,None,None,sc))
        else:
            d_rank=prk-rk          # positive = improved (moved up)
            d_score=sc-psc
            if (d_rank>=RANK_JUMP) or (prk>NEW_FROM and rk<=topn) or (d_score>=SCORE_JUMP):
                alerts.append((t,r,f"↑{d_rank} ({prk}→{rk})",prk,d_score,sc))
    # save today as new baseline regardless
    cur.to_csv(PREV,index=False)
    if not alerts:
        print(f"{today}: no surprise rank jumps in top-{topn}."); return
    # build report
    lines=[f"<b>⚡ 8L Rank Alert — {today}</b>  (top-{topn} surprise moves)"]
    plines=[f"{today} ALERTS:"]
    for t,r,tag,prk,dsc,sc in alerts:
        det=str(SDET.get(t,"")).split("|")[0].strip()[:70]
        line=f"• <b>{t}</b> {tag} | {r['route']} | score {sc:.0f}{(' (%+.0f)'%dsc) if dsc is not None else ''} | {r['verdict']}"
        lines.append(line); lines.append(f"   <i>{det}</i>")
        plines.append(f"  {t} {tag} score {sc:.0f} [{r['route']}] {r['verdict']}")
    msg="\n".join(lines); print("\n".join(plines))
    if telegram:
        try:
            from telegram_recommend import send_telegram_text, load_config
            cfg=load_config(); print("telegram:",send_telegram_text(cfg["bot_token"],cfg["chat_id"],msg).get("ok"))
        except Exception as e: print("telegram skipped:",e)

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--topn",type=int,default=TOPN); ap.add_argument("--no-telegram",action="store_true")
    a=ap.parse_args(); main(a.topn, not a.no_telegram)
