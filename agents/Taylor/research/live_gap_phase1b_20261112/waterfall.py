"""GĐ1 vòng 2 — waterfall tách cold / warm-live-scale, MỘT hurdle PIT (job Taylor_20261112_112708).
Số engine đọc thẳng từ ledger (md5 in ra). Live TWR + hurdle PIT từ GĐ0 vs_savings_table.csv (hurdle_pit_pct).
Usage: $DNA_PYEXE waterfall.py  -> waterfall.csv, waterfall.png"""
import glob, hashlib
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/live_gap_phase1b_20261112"
P1 = R.replace("phase1b", "phase1")
VS = R.replace("live_gap_phase1b_20261112", "live_gap_phase0_20261112") + "/vs_savings_table.csv"
END = "2026-11-11"


def leg(pat, start, cold):
    f = glob.glob(pat); assert len(f) == 1, (pat, f); f = f[0]
    X = pd.read_csv(f, low_memory=False); D = X[X.record_type == "DAILY"].copy()
    D["d"] = pd.to_datetime(D.ymd.astype(str).str[:10]); n = D.set_index("d")["combined_nav"].astype(float)
    n0 = float(n.iloc[0]) if cold else float(n[n.index <= start].iloc[-1])
    n1 = float(n[n.index <= END].iloc[-1])
    return 100 * (n1 / n0 - 1), n0, hashlib.md5(open(f, "rb").read()).hexdigest()


vs = pd.read_csv(VS)
def live(acct, series):
    q = vs[(vs.account == acct) & (vs.series == series) & (vs.window == "inception->11/11")].iloc[0]
    return float(q.live_twr_pct), float(q.hurdle_pit_pct)


SPEC = [  # account, series, start, [(regime, step, pattern, cold)]
    ("SpaceX", "account", "2026-06-30", [
        ("cold", "W0 pin park0 @50B (tiền mặt 01/07)", f"{P1}/ledgers/*_exp_gap_W0_adj_univpit_from20260701.csv", True),
        ("cold", "W1 quy mô live 1B", f"{P1}/ledgers/*_exp_gap_W1_adj_univpit_nav1B_from20260701.csv", True),
        ("cold", "W2a +LIQ_ZERO_BLOCK=lag", f"{P1}/ledgers/*_exp_gap_W2a_adj_univpit_nav1B_from20260701.csv", True),
        ("warm", "W0 warm @50B gốc 2014", f"{P1}/ledgers/*_exp_gap_W0warm_adj_univpit.csv", False),
        ("warm-D5", "W0 warm @50B LAG canonical (sandbox_ctrl)", f"{R}/ledgers/*_exp_gap_W0warm_ctrl_univpit.csv", False),
        ("warm-D5", "W0 warm @50B LAG vintage 10-29 (pin-era)", f"{R}/ledgers/*_exp_gap_W0warm_unadj1029_univpit.csv", False),
        ("warm", "W1 warm quy mô live (NAV_TOTAL_B=0,079958)", f"{R}/ledgers/*_exp_gap_WL2warm_SX_adj_univpit_nav0B.csv", False),
    ]),
    ("ZaloPay", "bot", "2026-07-06", [
        ("cold", "W0 pin park0 @50B (tiền mặt 06/07)", f"{P1}/ledgers/*_exp_gap_Z0_adj_univpit_from20260706.csv", True),
        ("cold", "W1 quy mô live 0,525B", f"{R}/ledgers/*_exp_gap_Z1cold_live_adj_univpit_nav0B_from20260706.csv", True),
        ("warm", "W0 warm @50B gốc 2014", f"{P1}/ledgers/*_exp_gap_W0warm_adj_univpit.csv", False),
        ("warm-D5", "W0 warm @50B LAG canonical (sandbox_ctrl)", f"{R}/ledgers/*_exp_gap_W0warm_ctrl_univpit.csv", False),
        ("warm-D5", "W0 warm @50B LAG vintage 10-29 (pin-era)", f"{R}/ledgers/*_exp_gap_W0warm_unadj1029_univpit.csv", False),
        ("warm", "W1 warm quy mô live (NAV_TOTAL_B=0,046052)", f"{R}/ledgers/*_exp_gap_WL2warm_Z_adj_univpit_nav0B.csv", False),
    ]),
]

rows = []
for acct, series, start, legs in SPEC:
    rL, hur = live(acct, series)
    for reg, step, pat, cold in legs:
        r, n0, md5 = leg(pat, start, cold)
        rows.append(dict(account=acct, regime=reg, step=step, ret_pct=r, nav_entry=n0, vs_hurdle_pp=r - hur,
                         live_minus_engine_pp=rL - r, ledger_md5=md5))
    rows.append(dict(account=acct, regime="live", step=f"LIVE {series}", ret_pct=rL, vs_hurdle_pp=rL - hur,
                     ledger_md5="GĐ0 vs_savings_table.csv"))
    rows.append(dict(account=acct, regime="ref", step="hurdle PIT (tiết kiệm)", ret_pct=hur))
W = pd.DataFrame(rows)
W.to_csv(f"{R}/waterfall.csv", index=False, float_format="%.3f")
print(W.to_string())

fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
for ax, acct in zip(axes, ["SpaceX", "ZaloPay"]):
    g = W[W.account == acct]
    col = {"warm-D5": "#b9a0d0", "cold": "#7aa6c2", "warm": "#2f6690", "live": "#c0504d", "ref": "#9bbb59"}
    ax.barh(range(len(g)), g.ret_pct, color=[col[x] for x in g.regime])
    ax.set_yticks(range(len(g))); ax.set_yticklabels([f"[{a}] {b}" for a, b in zip(g.regime, g.step)], fontsize=8)
    for i, v in enumerate(g.ret_pct): ax.text(v, i, f" {v:+.2f}%", va="center", fontsize=8)
    ax.axvline(0, color="k", lw=0.6); ax.invert_yaxis()
    ax.set_title(f"{acct} {'01/07' if acct == 'SpaceX' else '06/07'}→11/11 — lợi suất kỳ (%)", fontsize=10)
fig.suptitle("GĐ1 vòng 2: engine cold vs warm-live-scale vs LIVE, hurdle PIT (1 cửa sổ, N=1)", fontsize=10)
fig.tight_layout(); fig.savefig(f"{R}/waterfall.png", dpi=110)
