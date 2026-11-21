"""Muc 6 (MO TA, khong phai backtest wire): lenh LAG/BAL trong pin ladderA3-L3P (2026-11-13, pin0pct/pin1M)
tung mua 10 ma bank-nodata. Loi suat/holding = (sum sell - phi ban)/(sum buy + phi mua) - 1."""
import pandas as pd, glob
D = "/home/trido/thanhdt/WorkingClaude/data/pinned_ledgers/"
S5 = ["ABB", "KLB", "PCB", "VAB", "VBB"]; S10 = S5 + ["BAB", "BVB", "PGB", "NVB", "SGB"]
for tag in ("pin0pct", "pin1M"):
    f = glob.glob(D + f"2026-11-13__ladderA3-L3P-advsrcpit-{tag}__*.gz")[0]
    t = pd.read_csv(f, low_memory=False); t = t[(t.record_type == "TX") & t.ticker.isin(S10)].copy()
    t["ymd"] = pd.to_datetime(t.ymd)
    g = []
    for hid, x in t.groupby("holding_id"):
        b, s = x[x.action == "buy"], x[x.action == "sell"]
        cost = b.buy_amount.sum() + b.fee.sum(); proc = s.sell_amount.sum() - s.fee.sum()
        g.append(dict(holding=hid, ticker=x.ticker.iloc[0], book=x.book.iloc[0], entry=b.ymd.min().date(),
                      exit=s.ymd.max().date() if len(s) else None, reason=";".join(sorted(set(s.reason))),
                      cost_bn=round(cost / 1e9, 3), ret_pct=round((proc / cost - 1) * 100, 2) if len(s) else None))
    g = pd.DataFrame(g).sort_values("entry")
    print(f"===== {tag} ({f.split('/')[-1]}) =====")
    print(g.to_string(index=False))
    for lab, ss in (("5 ma doi hang (ABB/KLB/PCB/VAB/VBB)", S5), ("ca 10 ma nodata", S10)):
        h = g[g.ticker.isin(ss) & g.ret_pct.notna()]
        full = h[~h.reason.str.contains("ABANDONED")]
        w = (h.ret_pct * h.cost_bn).sum() / h.cost_bn.sum() if len(h) else float("nan")
        print(f"  {lab}: {len(h)} holding dong, {len(full)} khong-ABANDONED; TB theo von {w:.2f}%; "
              f"tong von {h.cost_bn.sum():.2f} ty; LAG {int((h.book=='LAG').sum())} / BAL {int((h.book=='BAL').sum())}")
