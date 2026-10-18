#!/usr/bin/env python3
"""Render the three locked Sprint 3 summary figures from results.json."""
import json, os
import matplotlib.pyplot as plt
import numpy as np

HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(HERE,"out3")
r=json.load(open(os.path.join(OUT,"results.json")))

def forest(keys,vals,title,name):
    mean=np.array([vals[k]["mean"]*100 for k in keys]); lo=np.array([vals[k]["lo"]*100 for k in keys]); hi=np.array([vals[k]["hi"]*100 for k in keys])
    fig,ax=plt.subplots(figsize=(7,3.8)); y=np.arange(len(keys))
    ax.errorbar(mean,y,xerr=[mean-lo,hi-mean],fmt="o",capsize=4,color="#315b7d")
    ax.axvline(0,color="black",lw=.8); ax.set_yticks(y,keys); ax.set_xlabel("Mean abnormal return (%)"); ax.set_title(title); ax.grid(axis="x",alpha=.2)
    fig.tight_layout(); fig.savefig(os.path.join(OUT,name),dpi=160); plt.close(fig)

forest(["EX_5","EX_10","EX_20","EX_60"],r["ex_horizons"],"Post-ex stock distributions","fig1_ex_horizons.png")
forest(["AIS_5","AIS_20","AIS_60"],r["ais_horizons"],"Around additional-listing date","fig2_ais_horizons.png")
keys=["IS","OOS","STOCK_DIVIDEND","BONUS"]
forest(keys,r["primary_splits"],"Ex-date T+20 stability","fig3_ex_stability.png")
