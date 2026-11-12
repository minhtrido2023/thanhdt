"""Bổ sung decompose3 (job Taylor_20261112_122855): (1) engine: α_park = Σ e_park,t−1·(r_rổ,t − r_VNI,t) với r_rổ = chỉ số
CUSTOM_VN30EXVIC_PITG trong chính ledger (xe park của engine); α_sig+chi phí = α − α_park. (2) rổ vs VNI theo tháng.
(3) live: e TB theo từng book (sổ park_holdings từ 04/08; trước đó xấp xỉ bootstrap). Usage: alpha_split.py out.md"""
import sys, glob, json, os
import pandas as pd
R = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, R); import decompose3 as D3
VNI = D3.engine("exp_gap_c3_SXwarm_p0")["vni"]
lines = []
def bkt(tag):
    X = pd.read_csv(D3.one(f"{R}/ledgers/*_exp_{tag}_univpit*.csv"), low_memory=False)
    C = X[X.record_type == "CUSTOM_BASKET"]; s = pd.Series(C["value"].astype(float).values, index=pd.to_datetime(C["ymd"].astype(str).str[:10]))
    return s.sort_index()
B = bkt("exp_gap_c3_SXcold_ps").reindex(VNI.index)
lines.append("| kỳ | VNI % | rổ park engine % | rổ − VNI pp |\n|---|---|---|---|")
for lab, a, b in D3.MONTHS["SpaceX"] + [("ky SX", *D3.WIN["SpaceX"])]:
    rv = VNI[:b].iloc[-1] / VNI[:a].iloc[-1] - 1; rb = B[:b].iloc[-1] / B[:a].iloc[-1] - 1
    lines.append(f"| {lab} | {100*rv:+.2f} | {100*rb:+.2f} | {100*(rb-rv):+.2f} |")
lines.append("\n| TK | engine | r eng | β park | β sig | α park (rổ−VNI) | α sig+chi phí |\n|---|---|---|---|---|---|---|")
rv, rb = VNI.pct_change(), B.pct_change()
for (acct, lab), tag in D3.LEGS.items():
    E = D3.engine("exp_gap_" + tag).reindex(VNI.index); E["nav"] = E["nav"].bfill(); E = E.fillna(0.0)
    a, b = D3.WIN[acct]; m = (VNI.index > pd.Timestamp(a)) & (VNI.index <= pd.Timestamp(b))
    n0 = E["nav"][:a].iloc[-1] if len(E["nav"][:a]) else E["nav"].iloc[0]; r = E["nav"][:b].iloc[-1] / n0 - 1
    bp = (E["park"].shift(1)[m] * rv[m]).sum(); bs = (E["sig"].shift(1)[m] * rv[m]).sum()
    ap = (E["park"].shift(1)[m] * (rb[m] - rv[m])).sum()
    lines.append(f"| {acct} | {lab} | {100*r:+.2f} | {100*bp:+.2f} | {100*bs:+.2f} | {100*ap:+.2f} | {100*(r-bp-bs-ap):+.2f} |")
lines.append("\nLive — tỷ trọng TB /NAV theo book (01/07|06/07 → 11/11):\n")
for acct in ["SpaceX", "ZaloPay"]:
    acc = {}; n = 0
    for f in sorted(glob.glob(f"{R}/live_books/{acct}_2026-*.json")):
        if os.path.getsize(f) == 0: continue
        H = json.load(open(f)); n += 1
        for k, v in H["by_book"].items(): acc[k] = acc.get(k, 0.0) + v["mv_vnd"]
    lines.append(f"- {acct} (sổ từ 04/08, {n} phiên): Σmv TB theo book (triệu VND) " + ", ".join(f"{k} {v/n/1e6:,.0f}" for k, v in sorted(acc.items())))
open(sys.argv[1], "w").write("\n".join(lines) + "\n"); print("\n".join(lines))
