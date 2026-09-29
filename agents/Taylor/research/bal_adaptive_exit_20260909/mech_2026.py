"""Mechanism check: did the adaptive exit actually change what happened in 2026 (the window the
rule was designed for)? Reads the TX section of each leg's audit CSV. Diagnostic only."""
import pandas as pd
B = ("/home/trido/thanhdt/WorkingClaude/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge"
     "_etfliqcustompitg_wtnamecap_advprice_univpit_exp_baladapt%s.csv")
for leg in ["ctrl", "a", "b", "c", "d"]:
    df = pd.read_csv(B % leg, low_memory=False)
    tx = df[df.record_type == "TX"].copy()
    tx["ymd"] = pd.to_datetime(tx["ymd"])
    bal = tx[(tx.book == "BAL") & (tx.action == "sell")]
    mom = bal[~bal.play_type.astype(str).str.startswith("CAPIT")]
    y26 = mom[mom.ymd.dt.year == 2026]
    print(f"--- {leg}: BAL momentum SELLs total={len(mom)}  2026={len(y26)}")
    print("    reasons all-period:", mom.reason.value_counts().head(6).to_dict())
    if len(y26):
        print("    2026 sell dates:", sorted(set(y26.ymd.dt.date.astype(str)))[:12])
        print("    2026 reasons:", y26.reason.value_counts().to_dict())
    buys = tx[(tx.book == "BAL") & (tx.action == "buy")]
    bm = buys[~buys.play_type.astype(str).str.startswith("CAPIT")]
    print(f"    BAL momentum BUYs total={len(bm)}  2026={int((bm.ymd.dt.year==2026).sum())}")
