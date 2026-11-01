# -*- coding: utf-8 -*-
"""Độ bền: (1) beta-MoS có phải chỉ là hiệu ứng low-beta? (2) loại ticker-date OShares đổi >10% (PREREG §1).
(3) tác động live 2026-10-30."""
import os
import numpy as np
import pandas as pd
from common import DATA, OUT, month_close, add_fwd, ic_by_date, ic_summary

P = print
pd.set_option("display.width", 250)
f = pd.read_parquet(os.path.join(DATA, "fv_variants.parquet"))
mc, me = month_close()
f = add_fwd(f, mc, me)
V0, VS0, VB, VSB = ("V0 hiện tại (s.5 N5 gT5.5 r hằng)", "G s=0", "B beta tương đối (β/median) kẹp 0.6-1.6",
                    "S s=0 + beta tương đối 0.6-1.6")
for k in (V0, VS0, VB, VSB):
    f["mos_" + k] = (f[k] - f.Price) / f[k]
f["neg_beta"] = -f.beta_b1


def summ(df, col, h=12):
    s = ic_summary(ic_by_date(df, col, f"fwd{h}"), h)
    return {k: round(v, 4) if isinstance(v, float) else v for k, v in s.items() if k in ("ic", "ic_is", "ic_oos", "t_nw", "ci_lo", "ci_hi")}


P("=== (1) low-beta: IC của −beta MỘT MÌNH (cùng tập có MoS)")
q = f.dropna(subset=["beta_b1", "mos_" + V0])
for h in (3, 12):
    P(f" h={h}: -beta", summ(q, "neg_beta", h), "| MoS V0", summ(q, "mos_" + V0, h), "| MoS beta", summ(q, "mos_" + VB, h))
# MoS beta sau khi trung hoà beta (phần dư rank trong ngày)
def resid(df, y, x):
    out = pd.Series(np.nan, index=df.index)
    for t, g in df.groupby("t"):
        g = g[[y, x]].dropna()
        if len(g) < 30:
            continue
        ry, rx = g[y].rank(pct=True), g[x].rank(pct=True)
        b = np.polyfit(rx, ry, 1)
        out[g.index] = ry - (b[0] * rx + b[1])
    return out


q = q.copy()
q["mosB_perp_beta"] = resid(q, "mos_" + VB, "beta_b1")
q["mosV0_perp_beta"] = resid(q, "mos_" + V0, "beta_b1")
q["mosB_perp_V0"] = resid(q, "mos_" + VB, "mos_" + V0)
for h in (3, 12):
    P(f" h={h}: MoS_beta ⟂ beta", summ(q, "mosB_perp_beta", h), "| MoS_V0 ⟂ beta", summ(q, "mosV0_perp_beta", h),
      "| MoS_beta ⟂ MoS_V0", summ(q, "mosB_perp_V0", h))
# combo đơn giản: rank MoS V0 + rank(−beta) (không qua DCF) — nếu bằng beta-MoS thì DCF-beta chỉ là trộn yếu tố
q["combo"] = q.groupby("t")["mos_" + V0].rank(pct=True) + 0.5 * q.groupby("t").neg_beta.rank(pct=True)
P(" combo rank(MoS V0)+0.5·rank(−β), h=12:", summ(q, "combo", 12))

P("=== (2) loại ticker-date có OShares đổi >10% trong ±4 quý (bẫy restate)")
ri = pd.read_parquet(os.path.join(DATA, "row_inputs.parquet")).sort_values(["ticker", "time"])
ri["osh_max"] = ri.groupby("ticker").OShares.transform(lambda s: s.rolling(9, center=True, min_periods=1).max())
ri["osh_min"] = ri.groupby("ticker").OShares.transform(lambda s: s.rolling(9, center=True, min_periods=1).min())
ri["unstable"] = ri.osh_max / ri.osh_min > 1.10
g = pd.merge_asof(f.sort_values("t"), ri[["ticker", "time", "unstable"]].sort_values("time"), left_on="t", right_on="time",
                  by="ticker", direction="backward")
P(" tỷ lệ ticker-date bị loại:", round(g.unstable.mean(), 3))
gs = g[~g.unstable.fillna(False).astype(bool)]
for k in (V0, VS0, VB, VSB):
    P(f"  {k}: IC12", summ(gs, "mos_" + k, 12), " IC3", summ(gs, "mos_" + k, 3))

P("=== (3) tác động live t=2026-10-30 (giá Price BQ 30/10, beta ngày 1Y tới 2026-09-30)")
L = f[f.t == f.t.max()].copy()
for k in (V0, VS0, VB, VSB):
    ok = np.isfinite(L[k]) & (L[k] > 0)
    P(f"  {k}: n={ok.sum()} FV median/V0 = {np.median(L[k][ok] / L[V0][ok]) - 1:+.3f}  %RẺ = {(L['mos_' + k][ok] > 0).mean():.3f}"
      f"  RICH sâu (MoS<-100%) = {(L['mos_' + k][ok] < -1).sum()}  beta_b1 non-NaN = {L.beta_b1[ok].notna().mean():.2f}")
P("  beta Blume1Y ngày phân phối 2026-09-30 p5/p50/p95:", L.beta_b1.quantile([.05, .5, .95]).round(3).tolist(),
  " beta tương đối p5/p50/p95:", L.beta_rel.quantile([.05, .5, .95]).round(3).tolist())

P("=== (4) pha loãng: tăng trưởng OShares/năm (dòng Q4, phi tài chính, 2014+) — FCFE/CP tăng chậm hơn FCFE tổng")
ri4 = ri[ri.quarter.str.endswith("Q4")].copy()
ri4["fy"] = ri4.quarter.str[:4].astype(int)
ri4 = ri4.drop_duplicates(["ticker", "fy"], keep="last").sort_values(["ticker", "fy"])
ri4["osg"] = ri4.groupby("ticker").OShares.pct_change()
ri4 = ri4[(ri4.fy >= 2014) & ri4.osg.between(-0.5, 3)]
P(f"  median {ri4.osg.median():.4f}  mean {ri4.osg.mean():.4f}  mean(cắt 1-99%) {ri4.osg.clip(*ri4.osg.quantile([.01,.99])).mean():.4f}"
  f"  share năm có tăng >1%: {(ri4.osg > 0.01).mean():.3f}  (lưu ý OShares restate — TRAP)")
P("=== (5) tuổi BCTC tại các ngày cuối tháng: phân phối")
pan = pd.read_parquet(os.path.join(DATA, "panel_monthly.parquet"))
a = pan.age_days.dropna()
P(f"  p50 {a.median():.0f} p90 {a.quantile(.9):.0f} p95 {a.quantile(.95):.0f} p99 {a.quantile(.99):.0f}; >100 ngày {(a>100).mean():.3f}; >125 ngày {(a>125).mean():.3f}; >185 ngày {(a>185).mean():.3f}")
