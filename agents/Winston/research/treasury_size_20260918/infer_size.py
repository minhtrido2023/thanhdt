"""Suy shares_delta cho su kien treasury_news buy_done/sell_done thieu co,
bang lech OShares giua 2 dong BCTC bao quanh ngay cong bo.

Do chinh xac bang CONTROL: chay cung thuat toan tren 131 su kien DA co co,
so voi gia tri that -> ty le dung do duoc, khong phai uoc doan.
"""
import pandas as pd, numpy as np, sys, os

D = os.path.dirname(os.path.abspath(__file__))
ev = pd.read_csv(f"{D}/events.csv", parse_dates=["public_date"])
fin = pd.read_csv(f"{D}/fin.csv", parse_dates=["time"])
ca = pd.read_csv(f"{D}/ca.csv", parse_dates=["effective_date", "record_date", "issue_date"])

fin = fin.dropna(subset=["OShares"])
fin = fin[fin.OShares > 0].sort_values(["ticker", "time"])

# CA lam doi so luong CP: ISS (phat hanh) + DIV tra bang CP -> co shares_delta
ca_sh = ca[ca.shares_delta.notna() & (ca.shares_delta != 0)].copy()
ca_sh["ca_date"] = ca_sh.effective_date.fillna(ca_sh.record_date).fillna(ca_sh.issue_date)
ca_sh = ca_sh.dropna(subset=["ca_date"])
ca_by_t = {t: g for t, g in ca_sh.groupby("ticker")}
fin_by_t = {t: g for t, g in fin.groupby("ticker")}
ev_by_t = {t: g for t, g in ev.groupby("ticker")}

SIGN = {"buy_done": -1, "sell_done": +1}   # tac dong len LUU HANH (OShares)


def infer(row):
    """Tra (delta_suy_luan, tang_tin_cay, ly_do)."""
    t, d, at = row.ticker, row.public_date, row.action_type
    g = fin_by_t.get(t)
    if g is None or len(g) < 2:
        return None, "NO_DATA", "khong co day BCTC"
    before = g[g.time < d]
    after = g[g.time >= d]
    if before.empty or after.empty:
        return None, "NO_DATA", "su kien ngoai pham vi BCTC"
    b, a = before.iloc[-1], after.iloc[0]
    lo, hi = b.time, a.time
    d_osh = a.OShares - b.OShares

    # co bao nhieu su kien treasury khac trong cung cua so?
    ge = ev_by_t[t]
    in_win = ge[(ge.public_date > lo) & (ge.public_date <= hi)]
    n_trsy = len(in_win)

    # CA lam doi so luong CP trong cung cua so?
    cg = ca_by_t.get(t)
    n_ca, ca_sum = 0, 0
    if cg is not None:
        cw = cg[(cg.ca_date > lo) & (cg.ca_date <= hi)]
        n_ca, ca_sum = len(cw), int(cw.shares_delta.sum())

    resid = d_osh - ca_sum          # tru phan giai thich duoc bang CA
    exp = SIGN[at]
    base = b.OShares

    if n_trsy > 1:
        return None, "MULTI_EVENT", f"{n_trsy} su kien treasury cung cua so {lo.date()}..{hi.date()}"
    if d_osh == 0 and ca_sum == 0:
        return None, "NO_MOVE", f"OShares khong doi qua cua so ({int(base):,})"
    if np.sign(resid) != exp or resid == 0:
        return None, "SIGN_MISMATCH", f"resid={int(resid):,} nguoc dau ky vong ({at})"
    pct = abs(resid) / base
    if pct > 0.25:
        return None, "IMPLAUSIBLE", f"|resid|={pct:.1%} OShares — qua lon cho 1 lo CP quy"

    tier = "HIGH" if n_ca == 0 else "MEDIUM"
    return int(abs(resid)) * exp, tier, f"dOSh={int(d_osh):,} ca={n_ca}/{ca_sum:,} resid={int(resid):,} ({pct:.2%})"


res = ev.apply(lambda r: pd.Series(infer(r), index=["inferred", "tier", "why"]), axis=1)
out = pd.concat([ev, res], axis=1)
out["is_unsized"] = out.shares_delta.isna()

# ---------- CONTROL: do do chinh xac tren 131 su kien DA biet co ----------
ctl = out[~out.is_unsized & out.inferred.notna()].copy()
# quy uoc dau treasury_news: buy_done duong (so CP mua vao quy) -> lat ve chieu LUU HANH
ctl["truth"] = ctl.shares_delta.abs() * ctl.action_type.map(SIGN)
ctl["err"] = (ctl.inferred - ctl.truth).abs() / ctl.truth.abs()

print("=" * 78)
print("CONTROL — thuat toan chay tren su kien DA BIET co (ground truth)")
print("=" * 78)
sized_total = int((~out.is_unsized).sum())
print(f"su kien co co: {sized_total} | suy luan ra so: {len(ctl)} "
      f"({len(ctl)/sized_total:.0%}) | im lang: {sized_total-len(ctl)}")
for tier in ["HIGH", "MEDIUM"]:
    c = ctl[ctl.tier == tier]
    if len(c) == 0:
        continue
    print(f"\n  [{tier}] n={len(c)}")
    for lab, thr in [("khop CHINX XAC", 0.0), ("sai <1%", 0.01), ("sai <5%", 0.05), ("sai <20%", 0.20)]:
        k = int((c.err <= thr).sum())
        print(f"    {lab:<16} {k:>3}/{len(c)}  ({k/len(c):5.1%})")
    print(f"    sai trung vi      {c.err.median():.2%}   sai TB {c.err.mean():.2%}")

print("\n  Truot nang nhat (control):")
for _, r in ctl.nlargest(6, "err").iterrows():
    print(f"    {r.ticker:<5} {r.public_date.date()} {r.action_type:<9} "
          f"that={int(r.truth):>12,} suy={int(r.inferred):>12,} sai={r.err:6.1%} [{r.tier}]")

# ly do im lang tren nhom co co
sil = out[~out.is_unsized & out.inferred.isna()]
print(f"\n  Ly do KHONG suy duoc (nhom co co, n={len(sil)}): "
      + ", ".join(f"{k}={v}" for k, v in sil.tier.value_counts().items()))

# ---------- KET QUA tren nhom THIEU co ----------
uns = out[out.is_unsized]
print("\n" + "=" * 78)
print(f"KET QUA — nhom THIEU co (n={len(uns)})")
print("=" * 78)
for k, v in uns.tier.value_counts().items():
    print(f"  {k:<15} {v:>4}  ({v/len(uns):5.1%})")

got = uns[uns.inferred.notna()]
print(f"\n  => suy duoc so: {len(got)}/{len(uns)} ({len(got)/len(uns):.0%})")
if len(got):
    p = (got.inferred.abs() / got.ticker.map(
        lambda t: fin_by_t[t].OShares.median())).describe(percentiles=[.5, .9])
    print(f"     quy mo (% OShares): p50={p['50%']:.2%} p90={p['90%']:.2%} max={p['max']:.2%}")

out.to_csv(f"{D}/inferred.csv", index=False)
uns[uns.inferred.isna()].to_csv(f"{D}/still_unsized.csv", index=False)
print(f"\nartifact: inferred.csv ({len(out)}), still_unsized.csv ({int(uns.inferred.isna().sum())})")
