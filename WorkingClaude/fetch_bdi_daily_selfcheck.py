#!/usr/bin/env python3
"""Selfcheck fetch_bdi_daily.py: stale-copy guard, normal append, fetched tz, raw HTML retention.
Network-free (fetch_html monkeypatched). Run under any TZ — result must be identical."""
import contextlib, io, os, sys, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_bdi_daily as F
import pandas as pd

def page(date, bdi, bci, bpi, bsi, bhsi):
    d,m,y=date.split("-")[::-1]; mon=["January","February","March","April","May","June","July","August","September","October","November","December"][int(m)-1]
    return (f"{int(d)}-{mon}-{y} Baltic Dry Index (BDI) rose to reach {bdi:,} points. Baltic Capesize Index (BCI) rose to reach {bci:,} points. "
            f"Baltic Panamax Index (BPI) rose to reach {bpi:,} points. Baltic Supramax Index (BSI) rose to reach {bsi:,} points. "
            f"Baltic Handysize Index (BHSI) rose to reach {bhsi:,} points.")

def run(csv_text, html):
    with tempfile.TemporaryDirectory() as w:
        os.makedirs(os.path.join(w,"data"))
        out=os.path.join(w,"data","bdi_daily_real.csv")
        if csv_text is not None: open(out,"w").write(csv_text)
        F.WORKDIR=w; F.OUT=out; F.fetch_html=lambda: html
        err=io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            F.main()                      # must not raise / sys.exit non-zero
        df=pd.read_csv(out) if os.path.exists(out) else None
        raws=os.listdir(os.path.join(w,"data","raw")) if os.path.isdir(os.path.join(w,"data","raw")) else []
        return df, err.getvalue(), raws

HDR="date,bdi,bci,bpi,bsi,bhsi,src,fetched\n"
BASE=HDR+"2026-07-02,2650,3921,2195,1675,944,handybulk,2026-07-02\n2026-07-03,2717,4100,2203,1673,942,handybulk,2026-07-03\n"
fails=[]
def check(name, ok):
    print(("PASS " if ok else "FAIL ")+name); 
    if not ok: fails.append(name)

# 1 stale copy -> no row, warning, raw still saved
df,err,raws=run(BASE, page("2026-07-06",2717,4100,2203,1673,942))
check("stale copy: no new row", len(df)==2 and "2026-07-06" not in set(df.date))
check("stale copy: WARN on stderr", "WARN" in err and "identical" in err)
check("stale copy: raw html saved", len(raws)==1)
# 2 normal -> appended, fetched ISO with +07:00
df,err,raws=run(BASE, page("2026-07-06",2797,4200,2210,1680,945))
check("normal: row appended", len(df)==3 and df.date.iloc[-1]=="2026-07-06" and df.bdi.iloc[-1]==2797)
check("normal: no warning", err=="")
f=str(df.fetched.iloc[-1]); check(f"normal: fetched ICT ISO ({f})", f.endswith("+07:00") and "T" in f)
# 3 same BDI but different sub-index -> NOT stale
df,_,_=run(BASE, page("2026-07-06",2717,4101,2203,1673,942))
check("only BDI-equal: still appended", len(df)==3)
# 4 no csv -> created
df,_,_=run(None, page("2026-07-06",2797,4200,2210,1680,945))
check("no csv: created", df is not None and len(df)==1)
# 5 raw retention: 31d-old removed, 1d-old kept
with tempfile.TemporaryDirectory() as w:
    F.WORKDIR=w; d=os.path.join(w,"data","raw"); os.makedirs(d)
    old=os.path.join(d,"bdi_handybulk_2026-01-01_2005.html"); new=os.path.join(d,"bdi_handybulk_2026-02-01_2005.html")
    for p,age in ((old,31),(new,1)):
        open(p,"w").write("x"); t=time.time()-age*86400; os.utime(p,(t,t))
    F.save_raw("<html/>", F.datetime.now(F.ICT))
    left=sorted(os.listdir(d))
    check("retention: >30d deleted, recent kept", os.path.basename(old) not in left and os.path.basename(new) in left and len(left)==2)
print("ALL PASS" if not fails else f"FAILED: {fails}"); sys.exit(1 if fails else 0)
