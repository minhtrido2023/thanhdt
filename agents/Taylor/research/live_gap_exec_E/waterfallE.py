"""Luồng E — waterfall đóng: LIVE = ENGINE(park mục tiêu) + fidelity park + W2b + W3 + W4 + W5 + dư.
ENGINE(park mục tiêu) = chân base (lịch park base chuẩn + LZB, JIT bật); fidelity = fidT − base; W2b = w2b_flag − fidT
(adv/ddzone inert = md5 trùng fidT; excluded_tickers/CAPIT-lever inert, xem REPORT); W3/W4/W5 từ e5_accounting.csv.
Lợi suất engine = legs.csv (gốc = NAV đóng cửa trước cửa sổ, như decompose3); live = TWR GĐ0 (vs_savings_table, kỳ inception→11/11).
Cộng gộp số học (bậc 1) — không có tương tác; phần dư gom tương tác + những gì chưa mô hình."""
import os, sys
import pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../live_gap_phase1c_20261112")))
import decompose3 as D3
R = os.path.dirname(os.path.abspath(__file__))
L = pd.read_csv(f"{R}/legs.csv").set_index("tag").r_ky_pct; E5 = pd.read_csv(f"{R}/e5_accounting.csv").set_index("TK")
vs = pd.read_csv(D3.VS)
rows = []
for acct, k, ser in (("SpaceX", "SX", "account"), ("ZaloPay", "Z", "bot")):
    live = float(vs[(vs.account == acct) & (vs.series == ser) & (vs.window == "inception->11/11")].live_twr_pct.iloc[0])
    for reg in ("cold", "warm"):
        need = [f"gapE_{k}{reg}_{x}" for x in ("base", "fidT", "w2b_flag")]
        if not all(n in L for n in need): continue
        base, fidT, w2b = (float(L[n]) for n in need)
        e = E5.loc[acct]; w5 = float(e.W5_pp_sleeve)
        comp = [("ENGINE park mục tiêu", base), ("fidelity park (buy-only tới 06/08, trim 07-06)", fidT - base),
                ("W2b mã cờ 11-03 (adv/ddzone/excl/lever inert)", w2b - fidT), ("W3 lệnh tay DISC (sổ, từ 04/08)", float(e.W3_lots_pp)),
                ("W4 fill thật vs Open (non-DISC)", float(e.W4_nonDISC_pp)), ("W5 lãi egg", w5)]
        s = sum(v for _, v in comp); comp.append(("dư chưa giải thích", live - s)); comp.append(("LIVE", live))
        for i, (n, v) in enumerate(comp): rows.append(dict(TK=acct, regime=reg, step=i, thanh_phan=n, pp=round(v, 3)))
T = pd.DataFrame(rows); T.to_csv(f"{R}/waterfall.csv", index=False)
print(T.pivot_table(index=["step", "thanh_phan"], columns=["TK", "regime"], values="pp").to_string())
g = [(a, r) for a, r in T[["TK", "regime"]].drop_duplicates().itertuples(index=False)]
fig, axs = plt.subplots(1, len(g), figsize=(6 * len(g), 5), squeeze=False)
for ax, (a, r) in zip(axs[0], g):
    t = T[(T.TK == a) & (T.regime == r)].sort_values("step"); cum = 0.0
    for i, x in enumerate(t.itertuples()):
        if x.step == 0 or x.thanh_phan == "LIVE":
            ax.bar(i, x.pp, color="#4a6fa5" if x.step == 0 else "#2a9d8f"); cum = x.pp if x.step == 0 else cum
        else:
            ax.bar(i, x.pp, bottom=cum, color="#e76f51" if x.pp < 0 else "#8ab17d"); cum += x.pp
        ax.text(i, (x.pp if x.step == 0 or x.thanh_phan == "LIVE" else cum) + 0.1, f"{x.pp:+.2f}", ha="center", fontsize=8)
    ax.set_xticks(range(len(t))); ax.set_xticklabels([s.split(" (")[0] for s in t.thanh_phan], rotation=40, ha="right", fontsize=7)
    ax.axhline(0, color="k", lw=0.5); ax.set_title(f"{a} — {r} (pp, kỳ inception→11/11)", fontsize=9)
plt.tight_layout(); plt.savefig(f"{R}/waterfall.png", dpi=110)
