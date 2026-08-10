# -*- coding: utf-8 -*-
"""Nhom bi gate 2 ty chan co bao nhieu ca "giong SCL" = thanh khoan mong NHUNG chat luong tot?
Chat luong = 8L rating <= 3 (gate LAG live dang dung) + FSCORE cao, doc POINT-IN-TIME tai ngay
tin hieu. Nguon: bq_cache/fa_ratings_8l.parquet + bq_cache/ticker/<year>.parquet (FSCORE).
"""
import numpy as np
import pandas as pd

pos = pd.read_csv("mike/agents/Taylor/exp_advgate_quality_20260810/pos_lag_blocked_flag.csv",
                  parse_dates=["entry_d", "sd"])
pos["abandoned"] = pos["abandoned"].astype(bool)

r8 = pd.read_parquet("data/bq_cache/fa_ratings_8l.parquet")
r8.columns = [c.lower() for c in r8.columns]
print("fa_ratings_8l cols:", list(r8.columns), "| rows", len(r8), "| time", r8.time.min(), "->", r8.time.max())
r8["time"] = pd.to_datetime(r8["time"]).astype("datetime64[ns]")
r8 = r8.sort_values("time")

# FSCORE point-in-time tu bq_cache/ticker
fs = []
for y in range(2014, 2027):
    try:
        d = pd.read_parquet(f"data/bq_cache/ticker/{y}.parquet", columns=["ticker", "time", "FSCORE"])
        fs.append(d.dropna(subset=["FSCORE"]))
    except Exception:
        pass
fs = pd.concat(fs, ignore_index=True)
fs["time"] = pd.to_datetime(fs["time"]).astype("datetime64[ns]")
fs = fs.sort_values("time")

def asof_join(left, right, val, ldate="entry_d"):
    a = left.copy(); a[ldate] = a[ldate].astype("datetime64[ns]"); a = a.sort_values(ldate)
    out = pd.merge_asof(a, right.rename(columns={"time": ldate}), on=ldate, by="ticker",
                        direction="backward")
    return out

p = asof_join(pos, r8[["ticker", "time", "rating"]], "rating")
p = asof_join(p, fs[["ticker", "time", "FSCORE"]], "FSCORE")
print(f"\nphu song du lieu: rating {p.rating.notna().mean()*100:.1f}% | FSCORE {p.FSCORE.notna().mean()*100:.1f}%")

p["band"] = np.where(~p.blocked, "E. >=2 ty (giu lai)",
             np.where(p.adv_vnd <= 1e8, "A. <=0,1 ty (live DA chan)",
                      "D. 0,1-2 ty (gate 2 ty THEM vao)"))

print("\n=== HO SO CHAT LUONG THEO NHOM ===")
rows = []
for b, d in p.groupby("band"):
    n = len(d)
    rat_ok = (d.rating <= 3)
    fs_hi = (d.FSCORE >= 7)
    rows.append(dict(nhom=b, n=n,
                     rating_co=f"{d.rating.notna().mean()*100:.0f}%",
                     rating_tv=f"{d.rating.median():.1f}" if d.rating.notna().any() else "-",
                     pct_rating_le3=f"{rat_ok.sum()/max(d.rating.notna().sum(),1)*100:.1f}%",
                     n_rating_le3=int(rat_ok.sum()),
                     FSCORE_tv=f"{d.FSCORE.median():.1f}" if d.FSCORE.notna().any() else "-",
                     pct_FSCORE_ge7=f"{fs_hi.sum()/max(d.FSCORE.notna().sum(),1)*100:.1f}%",
                     n_giong_SCL=int((rat_ok & fs_hi).sum())))
print(pd.DataFrame(rows).to_string(index=False))

# ket cuc cua chinh nhom "giong SCL" trong vung 0,1-2 ty
scl = p[(p.band.str.startswith("D")) & (p.rating <= 3) & (p.FSCORE >= 7)]
print(f"\n=== NHOM 'GIONG SCL' (0,1-2 ty + rating<=3 + FSCORE>=7): n={len(scl)} vi the ===")
if len(scl):
    print(f"  bo do {scl.abandoned.mean()*100:.1f}% | von {scl.buy.sum()/1e9:.1f}B "
          f"({scl.buy.sum()/p.buy.sum()*100:.2f}% von toan so)")
    done = scl[~scl.abandoned]
    if len(done):
        r = ((done.sell - done.buy - done.fee) / done.buy).dropna()
        print(f"  deal hoan tat n={len(r)}: TB {r.mean()*100:+.2f}% | trung vi {r.median()*100:+.2f}% "
              f"| winrate {(r>0).mean()*100:.1f}%")
        print("  chi tiet:", ", ".join(f"{t}@{d:%Y-%m}={v*100:+.0f}%"
              for t, d, v in zip(done.ticker, done.entry_d, r)))
    else:
        print("  0 deal hoan tat — TAT CA deu bo do (khong fill noi)")
# doi chung: nhom giong SCL trong vung >=2 ty
ref = p[(p.band.str.startswith("E")) & (p.rating <= 3) & (p.FSCORE >= 7)]
d2 = ref[~ref.abandoned]
if len(d2):
    r2 = ((d2.sell - d2.buy - d2.fee) / d2.buy).dropna()
    print(f"\n  [doi chung] cung chat luong NHUNG ADV>=2 ty: n_deal={len(r2)} "
          f"TB {r2.mean()*100:+.2f}% | trung vi {r2.median()*100:+.2f}% | winrate {(r2>0).mean()*100:.1f}%")
p.to_csv("mike/agents/Taylor/exp_advgate_quality_20260810/pos_with_quality.csv", index=False)
