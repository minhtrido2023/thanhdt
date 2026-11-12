"""Waterfall GĐ1 (job Taylor_20261112_104204). Đọc legs.json (leg_summary.py) + live từ GĐ0
(live_gap_phase0_20261112/vs_savings_table.csv = nav_period_returns.py). Ghi waterfall.csv + waterfall.png."""
import json, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/live_gap_phase1_20261112"
L = json.load(open(f"{R}/legs.json")); V = pd.read_csv(f"{R}/../live_gap_phase0_20261112/vs_savings_table.csv")
def live(acct, chuoi):
    r = V[(V.account == acct) & (V.series == chuoi) & (V["window"].astype(str).str.startswith("inception"))].iloc[0]
    return float(r["live_twr_pct"]), float(r["hurdle_flat74_pct"]), float(r["vnindex_price_pct"])
ret = lambda k: (L[k]["nav_last"] / L[k]["nav_first"] - 1) * 100
rows = []
for acct, pre, lives in [("SpaceX", "W", [("SpaceX", "account")]), ("ZaloPay", "Z", [("ZaloPay", "bot"), ("ZaloPay", "account")])]:
    steps = [("W0 pin park0 @50B", f"{pre}0_adj"), ("W1 vốn thật 1B", f"{pre}1_adj"), ("W2a +LIQ_ZERO_BLOCK=lag", f"{pre}2a_adj")]
    prev = None
    for name, k in steps:
        r = ret(k); rows.append(dict(account=acct, step=name, leg=k, md5=L[k]["md5"], window=f"{L[k]['first']}→{L[k]['last']}",
                                     ret_pct=round(r, 3), delta_pp=None if prev is None else round(r - prev, 3)))
        prev = r
    for name in ["W2b sàn ADV 2 tỷ / loại mã cờ / LAG DD-zone / excluded_tickers", "W3 lệnh tay thật", "W4 fill thật", "W5 tiền thật (egg)"]:
        rows.append(dict(account=acct, step=name, leg="CHƯA ĐO", md5="", window="", ret_pct=None, delta_pp=None))
    for a, ch in lives:
        lr, hur, vni = live(a, ch)
        rows.append(dict(account=acct, step=f"LIVE ({ch})", leg="nav_period_returns.py", md5="", window="", ret_pct=lr,
                         delta_pp=round(lr - prev, 3), hurdle_pct=hur, vni_pct=vni))
W = pd.DataFrame(rows); W.to_csv(f"{R}/waterfall.csv", index=False); print(W.to_string(index=False))
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
for ax, acct in zip(axes, ["SpaceX", "ZaloPay"]):
    d = W[(W.account == acct) & W.ret_pct.notna()]
    cols = ["#4a7bd0" if not s.startswith("LIVE") else "#d0634a" for s in d.step]
    ax.bar(range(len(d)), d.ret_pct, color=cols); ax.set_xticks(range(len(d)))
    ax.set_xticklabels([s.split(" ")[0] + ("\n" + s.split("(")[1].rstrip(")") if "(" in s else "") for s in d.step], fontsize=9)
    hur = d.hurdle_pct.dropna().iloc[0]; vni = d.vni_pct.dropna().iloc[0]
    ax.axhline(hur, ls="--", c="green", lw=1, label=f"tiết kiệm 7,4%/năm +{hur:.2f}%"); ax.axhline(vni, ls=":", c="gray", lw=1, label=f"VN-Index {vni:.2f}%")
    ax.axhline(0, c="k", lw=0.5); ax.set_title(f"{acct} — lợi suất kỳ (%)"); ax.legend(fontsize=8, loc="lower left")
    for i, v in enumerate(d.ret_pct): ax.text(i, v + (0.15 if v >= 0 else -0.45), f"{v:+.2f}", ha="center", fontsize=8)
fig.suptitle("GĐ1 waterfall 01/07→11/11/2026: engine pin (xanh) vs live (đỏ). W2b–W5 CHƯA ĐO"); fig.tight_layout(); fig.savefig(f"{R}/waterfall.png", dpi=110)
for k in ["W0_adj", "W1_adj"]:
    m = pd.Series(L[k]["month_end_nav"]); print(k, "month-end ret %", (m.pct_change() * 100).round(2).to_dict(), "first-month from start", round((m.iloc[0] / L[k]["nav_first"] - 1) * 100, 2))
