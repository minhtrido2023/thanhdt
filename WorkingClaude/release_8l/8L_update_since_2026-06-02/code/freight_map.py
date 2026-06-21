#!/usr/bin/env python3
"""
freight_map.py — 8L freight-rate lens (loader + tag + live regime)
==================================================================
Registry: data/freight_map.csv (segment · index · NP-sensitivity · play), hand-maintained.
Evidence: shipping_freight_sensitivity.py / data/shipping_freight_sensitivity.md.
Companion to oil_transmission.py (tankers appear in both: oil says "freight not oil",
freight gives the segment detail).

current_bdi() reads the REAL forward-accumulated feed (data/bdi_daily_real.csv, built by
fetch_bdi_daily.py) and falls back to the approx quarterly series.

    from freight_map import load_freight_map, freight_tag, current_bdi
    FMAP=load_freight_map(W); det+=freight_tag(FMAP,t)
"""
import os, pandas as pd

FREIGHT_TICKERS=["HAH","VOS","VNA","VSA","PVT","VIP","GSP","VTO","PVP","GMD","VSC","SGP"]

def load_freight_map(workdir):
    try: df=pd.read_csv(os.path.join(workdir,"data","freight_map.csv"))
    except Exception: return {}
    return {r["ticker"]:{"segment":r["segment"],"index":r["index"],
                         "sens":r["sens"],"play":r["play"]} for _,r in df.iterrows()}

def current_bdi(workdir):
    """(value, date, src) of latest BDI — prefer REAL feed, else approx quarterly. (None,..) if absent."""
    real=os.path.join(workdir,"data","bdi_daily_real.csv")
    if os.path.exists(real):
        try:
            d=pd.read_csv(real).sort_values("date")
            return (int(d["bdi"].iloc[-1]), str(d["date"].iloc[-1]), "real")
        except Exception: pass
    try:
        q=pd.read_csv(os.path.join(workdir,"data","freight_rates_quarterly.csv"),comment="#")
        return (int(q["bdi"].iloc[-1]), str(q["q"].iloc[-1]), "approx")
    except Exception: return (None,None,None)

def freight_tag(fmap, t, full=False):
    m=fmap.get(t)
    if not m: return ""
    base=f" | 🚢 FREIGHT[{m['segment']}·{m['index']}·NP~{m['sens']:+.2f}]"
    return base+f": {m['play']}" if full else base+f" {str(m['play'])[:64]}"
