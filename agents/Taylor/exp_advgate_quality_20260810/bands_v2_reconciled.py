# -*- coding: utf-8 -*-
"""v2 — MOT dinh nghia bang DUY NHAT cho ca §3/§4/BANG2 (sua loi quant-skeptic bat 2026-08-10).

LOI v1: `np.where(adv <= 1e8, "A", "D")` — so sanh voi NaN luon False nen moi vi the co
adv_vnd=NaN bi dun am tham vao bang D ("0,1-2 ty"), trong khi ADV cua chung KHONG DO DUOC.
=> tach hang rieng "U. ADV khong do duoc" va KHONG bao gio gop vao D.
"""
import glob
import numpy as np
import pandas as pd

p = pd.read_csv("mike/agents/Taylor/exp_advgate_quality_20260810/pos_with_quality.csv",
                parse_dates=["entry_d"])
p["abandoned"] = p["abandoned"].astype(bool)
p["yr"] = p.entry_d.dt.year

def band(d):
    return np.select(
        [~d.blocked, d.adv_vnd.isna(), d.adv_vnd <= 1e8, d.adv_vnd < 2e9],
        ["E. >=2 ty (giu lai)", "U. ADV KHONG DO DUOC", "A. <=0,1 ty (live DA chan)",
         "D. 0,1-2 ty (gate 2 ty THEM vao)"], default="?? loi phan bang")
p["band"] = band(p)
assert not (p.band == "?? loi phan bang").any()
print("phan bo vi the theo bang:"); print(p.band.value_counts().to_string())
print(f"\nkiem NaN: {int(p.adv_vnd.isna().sum())} vi the bi chan co adv_vnd = NaN")

# recommended_rerun #3 cua skeptic: NaN co that su la Volume_3M_P50 <= 0 / thieu du lieu khong?
nan_pos = p[p.adv_vnd.isna() & p.blocked]
chk, need = [], set(zip(nan_pos.ticker, nan_pos.entry_d.dt.year))
for y in sorted({y for _, y in need}):
    try:
        t = pd.read_parquet(f"data/bq_cache/ticker/{y}.parquet",
                            columns=["ticker", "time", "Volume_3M_P50", "Price", "Close"])
    except Exception:
        continue
    t["time"] = pd.to_datetime(t["time"])
    for _, r in nan_pos[nan_pos.yr == y].iterrows():
        d = t[(t.ticker == r.ticker) & (t.time <= r.entry_d)].sort_values("time")
        if d.empty:
            chk.append((r.ticker, r.entry_d.date(), "khong co dong nao", None)); continue
        last = d.iloc[-1]
        v = last["Volume_3M_P50"]
        chk.append((r.ticker, r.entry_d.date(),
                    "Volume_3M_P50 NaN" if pd.isna(v) else ("Volume_3M_P50 <= 0" if v <= 0 else "CO du lieu"),
                    None if pd.isna(v) else float(v)))
c = pd.DataFrame(chk, columns=["ticker", "entry_d", "chan_doan", "v50"])
print("\n=== kiem chung goc cua NaN (skeptic rerun #3) ===")
print(c.chan_doan.value_counts().to_string())
print(c.to_string(index=False))

d = p[~p.abandoned].copy()
d["r"] = (d.sell - d.buy - d.fee) / d.buy
assert np.isfinite(d.r).all() and (d.buy > 0).all()

ORDER = ["A. <=0,1 ty (live DA chan)", "U. ADV KHONG DO DUOC",
         "D. 0,1-2 ty (gate 2 ty THEM vao)", "E. >=2 ty (giu lai)"]
print("\n=== BANG 1 (v2): thang lieu theo bang ADV ===")
rows = []
for b in ORDER:
    x, r = p[p.band == b], d[d.band == b].r
    rows.append(dict(bang=b, n=len(x), bo_do=f"{x.abandoned.mean()*100:.1f}%",
                     von_B=round(x.buy.sum()/1e9, 1), pct_von=f"{x.buy.sum()/p.buy.sum()*100:.1f}%",
                     PnL_B=round((x.sell-x.buy-x.fee).sum()/1e9, 2), n_deal=len(r),
                     TB=f"{r.mean()*100:+.2f}%" if len(r) else "-",
                     trung_vi=f"{r.median()*100:+.2f}%" if len(r) else "-",
                     winrate=f"{(r>0).mean()*100:.1f}%" if len(r) else "-",
                     lo_gt20=f"{(r<-.2).mean()*100:.1f}%" if len(r) else "-"))
print(pd.DataFrame(rows).to_string(index=False))

rng = np.random.default_rng(20260810)
print("\n=== BANG 2 (v2): D vs E theo cua so thoi gian ===")
for lab, m in [("TOAN KY 2014-2026", d.yr > 0), ("IS 2014-19", d.yr <= 2019),
               ("OOS 2020+", d.yr >= 2020), ("2019+", d.yr >= 2019)]:
    x = d[m]
    a = x.loc[x.band.str.startswith("D"), "r"].values
    e = x.loc[x.band.str.startswith("E"), "r"].values
    if len(a) < 3:
        print(f"{lab:<18} n_D={len(a)} — qua mong, KHONG bootstrap"); continue
    bs = np.array([rng.choice(a, len(a), True).mean() - rng.choice(e, len(e), True).mean()
                   for _ in range(10000)])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    print(f"{lab:<18} n_D={len(a):>3} TB_D {a.mean()*100:+7.2f}% tv {np.median(a)*100:+6.2f}% "
          f"wr {(a>0).mean()*100:4.1f}% | n_E={len(e):>3} TB_E {e.mean()*100:+6.2f}% | "
          f"D-E {(a.mean()-e.mean())*100:+7.2f}pp CI95 [{lo*100:+.2f};{hi*100:+.2f}] "
          f"{'KHAC 0' if (lo>0)==(hi>0) else 'CHUA 0'}")

print("\n=== BANG 3 (v2): ho so chat luong + nhom 'giong SCL' ===")
rows = []
for b in ORDER:
    x = p[p.band == b]
    rat, fs = (x.rating <= 3), (x.FSCORE >= 7)
    rows.append(dict(bang=b, n=len(x),
                     rating_tv=f"{x.rating.median():.1f}", FSCORE_tv=f"{x.FSCORE.median():.1f}",
                     pct_rating_le3=f"{rat.sum()/max(x.rating.notna().sum(),1)*100:.1f}%",
                     pct_FSCORE_ge7=f"{fs.sum()/max(x.FSCORE.notna().sum(),1)*100:.1f}%",
                     n_giong_SCL=int((rat & fs).sum())))
print(pd.DataFrame(rows).to_string(index=False))

for b in ("D. 0,1-2 ty (gate 2 ty THEM vao)", "U. ADV KHONG DO DUOC", "E. >=2 ty (giu lai)"):
    s = p[(p.band == b) & (p.rating <= 3) & (p.FSCORE >= 7)]
    done = s[~s.abandoned]
    r = ((done.sell - done.buy - done.fee) / done.buy) if len(done) else pd.Series(dtype=float)
    print(f"\n[giong SCL] {b}: n={len(s)} vi the, bo do {s.abandoned.mean()*100:.1f}%, "
          f"n_deal={len(r)}" + (f", TB {r.mean()*100:+.2f}%, trung vi {r.median()*100:+.2f}%, "
          f"winrate {(r>0).mean()*100:.1f}%" if len(r) else ""))
    if len(r) and b.startswith(("D", "U")):
        print("   ", ", ".join(f"{t}@{x:%Y-%m}={v*100:+.0f}%"
                               for t, x, v in zip(done.ticker, done.entry_d, r)))
p.to_csv("mike/agents/Taylor/exp_advgate_quality_20260810/pos_bands_v2.csv", index=False)
