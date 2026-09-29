"""Implementation shortfall cho A vs B — phần Mike KHÔNG đo: fill cao hơn có ĐÁNG giá không.

IS = fill×(px_tra − px_quyết_định) + (1−fill)×(px_bù_sau − px_quyết_định)
  px_quyết_định = close phiên TRƯỚC campaign (lúc lập plan)
  px_bù_sau     = close 5 phiên SAU khi campaign kết thúc (phải mua bù ở đâu đó)
Đơn vị bps của px_quyết_định. Âm = tốt (mua rẻ hơn giá lúc quyết định).
"""
import os
import glob
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
B1 = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/thin_exec_20260812/data/bars1m"
B2 = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/thin_exec_20260812/data/bars1m_liquid"
LAG_CATCHUP = 5

rows = []
for f in sorted(glob.glob(os.path.join(B1, "*.csv"))) + sorted(glob.glob(os.path.join(B2, "*.csv"))):
    tk = os.path.basename(f)[:-4]
    d = pd.read_csv(f, parse_dates=["time"])
    d = d[d.volume > 0]
    g = d.groupby(d.time.dt.normalize())["close"].last()
    for i, (dt, c) in enumerate(g.items()):
        rows.append({"ticker": tk, "date": dt.date(), "i": i, "close": c})
daily = pd.DataFrame(rows)
daily["dec_px"] = daily.groupby("ticker")["close"].shift(1)          # close phiên trước campaign
daily["catchup_px"] = daily.groupby("ticker")["close"].shift(-(5 - 1 + LAG_CATCHUP))
daily["date"] = daily["date"].astype(str)

df = pd.read_csv(os.path.join(HERE, "out", "campaigns_main.csv"))
df = df.merge(daily[["ticker", "date", "dec_px", "catchup_px"]],
              left_on=["ticker", "start"], right_on=["ticker", "date"], how="left")
df = df.dropna(subset=["dec_px", "catchup_px"])
df["px_paid"] = df.avg_px.fillna(df.catchup_px)
df["is_bps"] = 1e4 * (
    df.fill_frac * (df.px_paid - df.dec_px) + (1 - df.fill_frac) * (df.catchup_px - df.dec_px)
) / df.dec_px

out = []
for sp in sorted(df.size_pct.unique()):
    for k in sorted(df.kappa.unique()):
        s = df[(df.size_pct == sp) & (df.kappa == k)]
        p = s.pivot_table(index=["ticker", "start"], columns="rule",
                          values=["is_bps", "fill_frac"]).dropna()
        d = p[("is_bps", "A")] - p[("is_bps", "B")]
        from scipy import stats
        t = float(stats.ttest_1samp(d, 0).statistic)
        out.append({"size_pct": sp, "kappa": k, "n": len(p),
                    "IS_A_bps": p[("is_bps", "A")].mean(),
                    "IS_B_bps": p[("is_bps", "B")].mean(),
                    "dIS_bps": d.mean(), "t": t,
                    "A_better_pct": 100.0 * (d < 0).mean()})
res = pd.DataFrame(out)
res.to_csv(os.path.join(HERE, "out", "shortfall.csv"), index=False)
print(res.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
