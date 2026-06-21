#!/usr/bin/env python3
"""
oil_transmission.py — 8L oil-transmission lens (loader + tag formatter)
======================================================================
Registry: data/oil_transmission_map.csv (hand-maintained, like moat_tags.csv).
Encodes HOW Brent crude transmits into each oil&gas name: chain position,
signal type (DIRECTION/LEVEL/INVERSE_MARGIN/CO_CYCLICAL/FREIGHT_NOT_OIL),
profit lag (quarters), and the practical play. Evidence: oil_8l_framework.md
(oil_sector_sensitivity.py / oil_bsr_pvd_deepdive.py / oil_pvd_anticip_gas.py).

Use:
    from oil_transmission import load_oil_map, oil_tag
    OILMAP = load_oil_map(WORKDIR)          # {ticker: {chain,signal,lag_q,play}}
    det += oil_tag(OILMAP, t)               # appends " | ⛽ OIL: ..." or "" if absent
"""
import os, pandas as pd

OIL_TICKERS = ["PVD","PVS","PVC","PVB","BSR","OIL","PLX","GAS","PGS","CNG",
               "PGD","PGC","PVG","DPM","DCM","PVT","VTO","VIP","GSP","PVP"]

def load_oil_map(workdir):
    try:
        df = pd.read_csv(os.path.join(workdir,"data","oil_transmission_map.csv"))
    except Exception:
        return {}
    out={}
    for _,r in df.iterrows():
        out[r["ticker"]]={"chain":r["chain"],"signal":r["signal"],
                          "lag_q":r["lag_q"],"play":r["play"]}
    return out

def oil_tag(oilmap, t, full=False):
    """Inline overlay tag for the screener/dna-card detail line. '' if not an oil name."""
    m=oilmap.get(t)
    if not m: return ""
    lag = "" if str(m["lag_q"])=="99" else f" lag{int(m['lag_q'])}Q"
    base=f" | ⛽ OIL[{m['chain']}·{m['signal']}{lag}]"
    return base+f": {m['play']}" if full else base+f" {str(m['play'])[:70]}"
