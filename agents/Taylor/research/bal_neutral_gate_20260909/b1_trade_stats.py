"""VONG 3 truc B — thong ke MUC LENH cho tung chan (PREREG: moi luat phai bao CA 4 so:
dCAGR, d_median, d_hit, d_dong-gop-duoi-phai). So lenh dung lai tu chinh file audit CSV cua tung
chan (record_type=TX, book=BAL), gop theo holding_id nen ban mot phan (chan b2) van vao dung 1 lenh.
Loai ABANDONED_REFUND + cac arm CAPIT_* (dung quy uoc Phan 1 §6 / B0)."""
import numpy as np
import pandas as pd
from scipy import stats

B = ("/home/trido/thanhdt/WorkingClaude/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge"
     "_etfliqcustompitg_wtnamecap_advprice_univpit_exp_balgate%s.csv")
LEGS = ["ctrl", "a1", "a2", "a3", "a4", "b1", "b2", "b3"]


def ledger(tag):
    d = pd.read_csv(B % tag, low_memory=False)
    t = d[(d.record_type == "TX") & (d.book == "BAL")].copy()
    t["ymd"] = pd.to_datetime(t["ymd"])
    # drop the custom30V parking lots (play_type ETF_PARK) and the CAPIT arms: neither is a BAL
    # momentum stock trade. Verified on ctrl: 682 holding_ids - 177 ETF_PARK = 505 = exactly the
    # BAL count of the CCS Phase 0 ledger built from the same pinned CSV.
    t = t[~t.play_type.astype(str).str.startswith(("CAPIT", "ETF_PARK"))]
    g = t.groupby("holding_id")
    L = pd.DataFrame({
        "play_type": g.play_type.first(),
        "cost": g.buy_amount.sum(),
        "proceeds": g.sell_amount.sum(),
        "fee": g.fee.sum(),
        "entry": g.ymd.min(),
        "exit": g.ymd.max(),
        "reasons": g.reason.apply(lambda s: ",".join(sorted(set(s.dropna())))),
    })
    L = L[~L.reasons.str.contains("ABANDONED_REFUND")]
    L = L[(L.cost > 0) & (L.proceeds > 0)]
    L["ret"] = L.proceeds / L.cost - 1
    L["pnl"] = L.proceeds - L.cost
    L["yr"] = L.entry.dt.year
    return L


def stat(L):
    r = L.ret.values
    c = L.pnl.values
    pos = c[c > 0]
    k = max(1, int(round(len(c) * 0.1)))
    return dict(n=len(r), mean_pct=r.mean() * 100, median_pct=np.median(r) * 100,
                hit_pct=(r > 0).mean() * 100, skew=stats.skew(r),
                topdec_share_of_gain_pct=np.sort(c)[::-1][:k].sum() / pos.sum() * 100,
                gain_from_ret_gt20_pct=c[(r > 0.20) & (c > 0)].sum() / pos.sum() * 100,
                net_pnl_B=c.sum() / 1e9, stop_pct=L.reasons.str.contains("STOP").mean() * 100)


rows = {}
for t in LEGS:
    rows[t] = stat(ledger(t))
S = pd.DataFrame(rows).T
for k in S.columns:
    if k != "n":
        S["d_" + k] = S[k] - S.loc["ctrl", k]
pd.set_option("display.width", 260)
print("=== thong ke muc LENH sổ BAL (khong CAPIT, khong ABANDONED_REFUND) ===")
print(S.round(2).to_string())
S.to_csv("b1_trade_stats.csv")

print("\n=== rieng 2025 (entry year) ===")
r25 = {}
for t in LEGS:
    L = ledger(t)
    L = L[L.yr == 2025]
    r25[t] = stat(L) if len(L) else {}
S25 = pd.DataFrame(r25).T
for k in S25.columns:
    if k != "n":
        S25["d_" + k] = S25[k] - S25.loc["ctrl", k]
print(S25.round(2).to_string())
S25.to_csv("b1_trade_stats_2025.csv")
