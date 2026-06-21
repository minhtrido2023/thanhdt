"""Extended analysis of early-fire results across horizons + decision matrix."""
import os
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

def main():
    df = pd.read_csv(os.path.join(WORKDIR, "layer3_early_fire_events.csv"))
    print(f"Total events: {len(df)}")
    print(f"Signals: {df['signal'].value_counts().to_dict()}")

    horizons = [5, 20, 45]

    print("\n" + "="*100)
    print("STRATEGY MEAN RETURN BY HORIZON × SIGNAL × SEGMENT")
    print("="*100)
    for sname in ["S1_STRONG_COMBO","S2_OVERSOLD_REV","S3_VOL_BREAKOUT"]:
        print(f"\n--- {sname} ---")
        s = df[df["signal"]==sname]
        for seg in ["TOP30","MIDCAP","PENNY"]:
            sub = s[s["segment"]==seg]
            cat_TP = sub[(sub["fire_bar_idx"].notna()) & (sub["eod_signal"]==True)]
            cat_FP = sub[(sub["fire_bar_idx"].notna()) & (sub["eod_signal"]==False)]
            cat_E = pd.concat([cat_TP, cat_FP])
            cat_EOD = cat_TP
            print(f"\n  [{seg}] TP={len(cat_TP)} FP={len(cat_FP)} fire_rate={(len(cat_E)/max(1,len(sub)))*100:.1f}%")
            for h in horizons:
                col = f"Close_T{h}"
                if col not in sub.columns: continue
                r_eod = ((cat_EOD[col]/cat_EOD["eod_price"]-1)*100).dropna()
                r_early = ((cat_E[col]/cat_E["fire_price"]-1)*100).dropna()
                if len(r_eod)==0 or len(r_early)==0: continue
                lift = r_early.mean() - r_eod.mean()
                std_e = r_early.std() if len(r_early)>1 else 0
                sh_e = r_early.mean()/std_e if std_e>0 else 0
                std_w = r_eod.std() if len(r_eod)>1 else 0
                sh_w = r_eod.mean()/std_w if std_w>0 else 0
                print(f"    T+{h:>2}d  EARLY={r_early.mean():>7.3f}% (n={len(r_early):>4}, sh={sh_e:.3f})  "
                      f"WAIT_EOD={r_eod.mean():>7.3f}% (n={len(r_eod):>4}, sh={sh_w:.3f})  "
                      f"LIFT={lift:+.3f}pp")

    print("\n" + "="*100)
    print("FIRE-TIME ANALYSIS — does firing EARLIER give better entry?")
    print("="*100)
    s1 = df[(df["signal"]=="S1_STRONG_COMBO") & df["fire_bar_idx"].notna()].copy()
    # Convert HH:MM to ordinal
    s1["fire_minute"] = s1["fire_hhmm"].apply(lambda x: int(x[:2])*60 + int(x[3:]))
    s1["time_bucket"] = pd.cut(s1["fire_minute"], bins=[0, 9*60+45, 10*60+30, 11*60+30, 14*60, 24*60],
                                  labels=["09:15-09:45","09:45-10:30","10:30-11:30","13:00-14:00","14:00-ATC"])
    for seg in ["TOP30","MIDCAP","PENNY"]:
        sub = s1[s1["segment"]==seg]
        print(f"\n[{seg}]")
        g = sub.groupby("time_bucket", observed=True).agg(
            n=("fire_price","count"),
            ret_T5=("Close_T5", lambda s_: ((s_/sub.loc[s_.index, "fire_price"]-1)*100).mean()),
            ret_T20=("Close_T20", lambda s_: ((s_/sub.loc[s_.index, "fire_price"]-1)*100).mean()),
            ret_T45=("Close_T45", lambda s_: ((s_/sub.loc[s_.index, "fire_price"]-1)*100).mean()),
        )
        print(g.round(3).to_string())

    print("\n" + "="*100)
    print("NAV-LIKE NET STRATEGY COMPARISON")
    print("="*100)
    print("Assume equal-weight buy on each fire/EoD-confirmed event, hold to T+N, then sell at close.")
    print("Compute total cumulative pseudo-return (sum of trade returns) as a proxy for NAV impact.\n")
    for sname in ["S1_STRONG_COMBO","S2_OVERSOLD_REV"]:
        print(f"--- {sname} ---")
        s = df[df["signal"]==sname]
        rows = []
        for seg in ["TOP30","MIDCAP","PENNY","ALL"]:
            sub = s if seg=="ALL" else s[s["segment"]==seg]
            cat_TP = sub[(sub["fire_bar_idx"].notna()) & (sub["eod_signal"]==True)]
            cat_E = sub[sub["fire_bar_idx"].notna()]
            for h in [5,20,45]:
                col = f"Close_T{h}"
                r_eod = ((cat_TP[col]/cat_TP["eod_price"]-1)*100).dropna()
                r_early = ((cat_E[col]/cat_E["fire_price"]-1)*100).dropna()
                rows.append({"seg": seg, "horiz": h,
                              "EARLY_n": len(r_early), "EARLY_mean": round(r_early.mean(),3) if len(r_early) else None,
                              "EARLY_sum": round(r_early.sum(),1) if len(r_early) else None,
                              "EoD_n": len(r_eod), "EoD_mean": round(r_eod.mean(),3) if len(r_eod) else None,
                              "EoD_sum": round(r_eod.sum(),1) if len(r_eod) else None,
                              "lift_mean_pp": round(r_early.mean()-r_eod.mean(),3) if len(r_early) and len(r_eod) else None})
        print(pd.DataFrame(rows).to_string(index=False))
        print()

if __name__=="__main__":
    main()
