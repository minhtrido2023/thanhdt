#!/usr/bin/env python3
"""
fetch_bdi_daily.py — forward-accumulating REAL Baltic Dry Index daily scraper
=============================================================================
Source: handybulk.com/baltic-dry-index (publishes the LATEST trading-day BDI in prose;
local network reaches it fine; investing.com API is 403, stooq is JS-gated).
Each run grabs the most recent (date, BDI) [+ BCI/BPI/BSI/BHSI if present] and appends
to data/bdi_daily_real.csv, deduped by date. Schedule daily → a genuine BDI feed builds up.

Run:  python fetch_bdi_daily.py
CSV:  data/bdi_daily_real.csv  (columns: date,bdi,bci,bpi,bsi,bhsi,src,fetched)
"""
import os, re, ssl, sys, urllib.request
import pandas as pd
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
WORKDIR=os.environ.get("WORKDIR_8L", os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(WORKDIR,"data","bdi_daily_real.csv")
URL="https://www.handybulk.com/baltic-dry-index/"
MONTHS={m:i+1 for i,m in enumerate(["January","February","March","April","May","June",
    "July","August","September","October","November","December"])}

def fetch_html():
    ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
    hdr={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"}
    return urllib.request.urlopen(urllib.request.Request(URL,headers=hdr),timeout=30,context=ctx).read().decode("utf-8","ignore")

def parse(html):
    # lead date like "4-June-2026"
    md=re.search(r'(\d{1,2})-([A-Za-z]+)-(20\d\d)', html)
    if not md: raise RuntimeError("no date found")
    d,mon,y=md.groups()
    if mon not in MONTHS: raise RuntimeError(f"bad month {mon}")
    date=f"{int(y):04d}-{MONTHS[mon]:02d}-{int(d):02d}"
    def grab(label):
        # data sentence reads e.g. "... decreased by 87 points to reach 3,037 points." The LEVEL follows
        # 'to reach' / 'to' / 'at' (the first number is the delta). Require that connector to skip the
        # intro definition sentence. Fallback: last '<num> points' in a 160-char window after the label.
        m=re.search(label+r'[^.]{0,140}?(?:to reach|to|stood at|at|of)\s+([\d,]{3,7})\s*points', html)
        if m: return int(m.group(1).replace(",",""))
        m2=re.search(label+r'([^.]{0,160})', html)
        if m2:
            vals=re.findall(r'([\d,]{3,7})\s*points', m2.group(1))
            if vals: return int(vals[-1].replace(",",""))
        return None
    row={"date":date,
         "bdi":grab(r'Baltic Dry Index \(BDI\)'),
         "bci":grab(r'Baltic Capesize Index \(BCI\)'),
         "bpi":grab(r'Baltic Panamax Index \(BPI\)'),
         "bsi":grab(r'Baltic Supramax Index \(BSI\)'),
         "bhsi":grab(r'Baltic Handysize Index \(BHSI\)')}
    if row["bdi"] is None: raise RuntimeError("BDI value not parsed")
    return row

def main():
    html=fetch_html(); row=parse(html); row["src"]="handybulk"
    # fetched timestamp from the data date itself (no Date.now needed); keep simple
    row["fetched"]=row["date"]
    new=pd.DataFrame([row])
    if os.path.exists(OUT):
        old=pd.read_csv(OUT)
        comb=pd.concat([old,new],ignore_index=True).drop_duplicates(subset=["date"],keep="last")
    else:
        comb=new
    comb=comb.sort_values("date").reset_index(drop=True)
    comb.to_csv(OUT,index=False)
    print(f"BDI {row['date']} = {row['bdi']} (BCI {row['bci']} BPI {row['bpi']} BSI {row['bsi']} BHSI {row['bhsi']})")
    print(f"-> {OUT} now {len(comb)} rows ({comb['date'].iloc[0]} .. {comb['date'].iloc[-1]})")

if __name__=="__main__": main()
