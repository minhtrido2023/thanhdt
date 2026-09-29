# -*- coding: utf-8 -*-
"""Mo rong backtest config DANG DEPLOY (orb_pt.py) ve 2022-02-17 bang tape FiinProX.

Nguon:
  - 2022-02-17..2023-09-08 : FiinX MCP (fiinx_daily_gap.csv, per-day record)  <-- MOI
  - 2023-09-11..2026-09-25 : tape vnstock da dung tu truoc (orb_core.load_bars)

Bay vendor da do (xem bus finding): FiinX thu gon bar 14:30 ve MOT gia (o=h=l=c=gia dau),
trong khi vnstock giu OHLC day du => exit tai 14:30 KHAC nhau tren 69/76 ngay trung.
Nen BAO CAO CHINH dung exit 14:29 cho CA HAI doan (dong quy uoc), va in them bien the
14:30 tren doan vnstock de do do lon cua quy uoc nay.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/orb_deployed_config_validation_20260925")
import orb_core

TICK, SLIP, FEE = orb_core.TICK, orb_core.SLIP_TICKS, orb_core.FEE


def days_from_local():
    df = orb_core.load_bars()
    out = []
    for d, g in df.groupby("date"):
        g = g.sort_values("time")
        g = g[(g["hm"] >= "09:00") & (g["hm"] <= "14:45")]
        if len(g) == 0:
            continue
        op = g[g["hm"] <= "09:30"]
        s29 = g[(g["hm"] > "09:30") & (g["hm"] <= "14:29")]
        s30 = g[(g["hm"] > "09:30") & (g["hm"] <= "14:30")]
        if len(op) < 10 or len(s29) == 0 or g["hm"].iloc[-1] < "14:25":
            continue
        out.append(dict(date=str(d), src="vnstock", c_first=float(g["close"].iloc[0]),
                        entry=float(op["close"].iloc[-1]),
                        exit29=float(s29["close"].iloc[-1]),
                        exit30=float(s30["close"].iloc[-1]) if len(s30) else np.nan,
                        minlow29=float(s29["low"].min()), maxhigh29=float(s29["high"].max())))
    return pd.DataFrame(out)


def days_from_fiinx():
    f = pd.read_csv("fiinx_daily_gap.csv")
    f = f[(f["nop"] >= 10) & (f["nseg29"] > 0) & (f["hmL"] >= "14:25")].copy()
    f["src"] = "fiinx"
    return f[["date", "src", "c_first", "entry", "exit29", "exit30", "minlow29", "maxhigh29"]]


def sim(d, exit_col="exit29", stop=None, min_or=0.0):
    r = d.copy()
    r["or_ret"] = r["entry"] / r["c_first"] - 1
    r["sig"] = np.sign(r["or_ret"]).astype(int)
    r = r[(r["sig"] != 0) & (r["or_ret"].abs() >= min_or)].copy()
    px = r[exit_col].astype(float).values
    if stop is not None:
        lo, hi, e, s = r["minlow29"].values, r["maxhigh29"].values, r["entry"].values, r["sig"].values
        hit_l = (s > 0) & (lo <= e * (1 - stop))
        hit_s = (s < 0) & (hi >= e * (1 + stop))
        px = np.where(hit_l, e * (1 - stop), np.where(hit_s, e * (1 + stop), px))
    ef = r["entry"].values + r["sig"].values * SLIP * TICK
    xf = px - r["sig"].values * SLIP * TICK
    r["net"] = r["sig"].values * (xf / ef - 1) - FEE
    return r


def stats(r, label):
    x = r["net"].values
    n = len(x); mu = x.mean(); sd = x.std(ddof=1)
    sh = mu / sd * np.sqrt(252)
    nav = np.cumprod(1 + x)
    mdd = float((nav / np.maximum.accumulate(nav) - 1).min())
    t = mu / (sd / np.sqrt(n))
    print("  %-34s n=%4d  WR=%5.1f%%  mean=%+7.2fbps  Sharpe=%+6.2f  cum=%+8.2f%%  MaxDD=%+6.2f%%  t=%+5.2f"
          % (label, n, (x > 0).mean() * 100, mu * 1e4, sh, (nav[-1] - 1) * 100, mdd * 100, t))
    return dict(n=n, mean=mu, sd=sd, sharpe=float(sh), t=float(t), mdd=mdd, cum=float(nav[-1] - 1))


L = days_from_local(); F = days_from_fiinx()
both = set(L["date"]) & set(F["date"])
print("Local(vnstock) days=%d  %s..%s" % (len(L), L["date"].min(), L["date"].max()))
print("FiinX gap  days=%d  %s..%s  | trung voi local: %d ngay" % (len(F), F["date"].min(), F["date"].max(), len(both)))
ALL = pd.concat([F, L], ignore_index=True).sort_values("date").reset_index(drop=True)
assert ALL["date"].duplicated().sum() == 0, "TRUNG NGAY"
print("Ghep: %d ngay %s..%s\n" % (len(ALL), ALL["date"].min(), ALL["date"].max()))

print("=== Config DANG DEPLOY (khong stop, khong loc |OR|), exit 14:29 ===")
sF = stats(sim(F), "MOI: FiinX 2022-02..2023-09")
sL = stats(sim(L), "CU : vnstock 2023-09..2026-09")
sA = stats(sim(ALL), "GOP: 2022-02..2026-09")

print("\n=== Do lon cua quy uoc exit (chi doan vnstock, co ca 2 cot) ===")
stats(sim(L, "exit29"), "vnstock exit 14:29")
stats(sim(L, "exit30"), "vnstock exit 14:30 (= deployed)")

print("\n=== Theo nam (exit 14:29, tape ghep) ===")
a = sim(ALL); a["yr"] = a["date"].str[:4]
for yr, g in a.groupby("yr"):
    x = g["net"].values
    print("  %s  n=%3d  mean=%+7.2fbps  Sharpe=%+6.2f  cum=%+7.2f%%  src=%s"
          % (yr, len(x), x.mean() * 1e4, x.mean() / x.std(ddof=1) * np.sqrt(252),
             (np.prod(1 + x) - 1) * 100, "/".join(sorted(g["src"].unique()))))

print("\n=== Kiem dinh doan MOI la OOS that (khong dung de chon tham so) ===")
xF = sim(F)["net"].values; xL = sim(L)["net"].values
from scipy import stats as st
tt = st.ttest_ind(xF, xL, equal_var=False)
print("  Welch t-test mean(FiinX 2022-23) vs mean(vnstock 2023-26): t=%.3f p=%.4f" % (tt.statistic, tt.pvalue))
print("  mean moi=%+.2fbps  mean cu=%+.2fbps" % (xF.mean() * 1e4, xL.mean() * 1e4))

a.to_csv("orb_trades_extended_20220217_20260925.csv", index=False)
print("\nGhi: orb_trades_extended_20220217_20260925.csv (%d trade)" % len(a))
