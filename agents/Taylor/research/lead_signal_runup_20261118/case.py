"""Case study TV1/VCP — chạy SAU kết quả toàn universe. Mô tả, không khuyến nghị."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
OUT = os.path.dirname(os.path.abspath(__file__))
P = pd.read_parquet(f"{OUT}/panel.parquet")
fin = pd.read_parquet(f"{ROOT}/data/bq_cache/ticker_financial.parquet", columns=["ticker", "quarter", "Release_Date"])
print(fin[fin.ticker.isin(["TV1", "VCP"])].sort_values("Release_Date").tail(4).to_string())
cases = {"TV1": "2026-10-29", "VCP": "2026-10-19"}
S = P[P.E & ~P.chase & P.OOS]
lines = []
for tk, t0 in cases.items():
    g = P[P.ticker == tk].reset_index(drop=True)
    i0 = int(np.flatnonzero(g.time == t0)[0])
    w = g.iloc[i0 - 10:i0 + 6]
    lines.append(f"\n### {tk} (T0 = {t0})\n| ngày | rel | Close | ret | TV tỷ | tín hiệu bật |\n|---|---|---|---|---|---|")
    for j, r in w.iterrows():
        on = [f"{s}" for s in SIGS if r[s]]
        lines.append(f"| {r.time.date()} | T0{j-i0:+d} | {r.Close:,.0f} | {r.ret:+.1%} | {r.TV/1e9:.2f} | {', '.join(on) or '—'} |")
    # precision thật của bộ tín hiệu (bất kỳ trong T0-5..T0) — khớp siêu tập trên OOS
    pre = [s for s in SIGS if g.loc[i0 - 5:i0, s].any()]
    lines.append(f"\nTín hiệu có mặt trong T0−5..T0: {', '.join(pre) or 'không'}")
    if pre:
        m = np.ones(len(S), bool)
        for s in pre:
            m &= (S[s] | S[f"pre5_{s}"]).to_numpy()
        D = S[m].sort_values(["ticker", "nhist"])
        st = D.groupby("ticker").nhist.diff().fillna(99) >= 10
        cs = D[st.to_numpy()]
        lines.append(f"Dòng OOS có ĐỦ bộ đó (trong 6 phiên): {len(D):,}; cụm độc lập {len(cs):,}; cụm có run-up≥20%: {int(cs.y20.sum())} "
                     f"(precision {cs.y20.mean():.1%}); cụm KHÔNG chạy: {int((~cs.y20).sum()):,}; base rate OOS {S.y20.mean():.1%}")
# climax mô tả: 6 phiên cuối
lines.append("\n### Cờ kết thúc đợt (K1–K4) 6 phiên cuối trong cache (tới 17/11)\n| mã | ngày | Close | C/MA20−1 | run20 | K bật |\n|---|---|---|---|---|---|")
for tk in cases:
    g = P[P.ticker == tk].tail(6)
    for _, r in g.iterrows():
        ma20 = P[(P.ticker == tk) & (P.time <= r.time)].Close.tail(20).mean()
        on = [k for k in KS if r[k]]
        lines.append(f"| {tk} | {r.time.date()} | {r.Close:,.0f} | {r.Close/ma20-1:+.0%} | {r.run20:+.0%} | {', '.join(on) or '—'} |")
open(f"{OUT}/case_study.md", "w").write("\n".join(lines)); print("\n".join(lines))
