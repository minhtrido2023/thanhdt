"""Chan doan — PBO episode-anchored = 0,073 la TIN HIEU THAT hay HIEN VAT cua mau?

Gia thuyet can bac: mau 15 su kien KHONG chua mot washout that bai sau nao (objection goc cua
reviewer, lo te nhat quan sat -4,7%). Neu MOI su kien deu thuan loi thi leg phoi nhiem lon nhat
thang o MOI cach chia -> IS-best == OOS-best mot cach tam thuong -> PBO ~ 0 MA KHONG he chung minh
xep hang do dang tin cho tuong lai.

Kiem 3 dieu:
  1. Dau loi nhuan cua tung su kien (bao nhieu su kien am?).
  2. Tuong quan giua PHOI NHIEM (%NAV trien khai) va Sharpe cua su kien -> co don dieu khong?
  3. PBO tinh lai khi LOAI cac su kien thang dam nhat (leave-worst-out) — neu PBO van ~0 thi ben.
"""
import glob
import itertools
import os
from collections import Counter

import numpy as np
import pandas as pd

D = "/home/trido/thanhdt/WorkingClaude/data"
LEGS = [
    ("capsz_ctrl", "cash"), ("capsz_idle", "idle"), ("capsz_booknav", "booknav"),
    ("capsz_nav10", "nav:0.10"), ("capsz_nav20", "nav:0.20"),
    ("capsz_idlecap30", "idlecap:0.30"), ("capsz_park25", "park:0.25"),
    ("capsz_park50", "park:0.50"), ("capsz_navsize15", "navsize:0.15"),
    ("capsz_navsize25", "navsize:0.25"), ("capsz_navsize30", "navsize:0.30"),
    ("capsz_navsize35", "navsize:0.35"), ("capsz_navsize40", "navsize:0.40"),
]

navs, ref_csv = {}, None
for tag, base in LEGS:
    f = glob.glob(os.path.join(D, f"v23_golive_audit_2014_now_*_exp_{tag}_univpit.csv"))
    if not f:
        continue
    if base == "navsize:0.25":
        ref_csv = f[0]
    df = pd.read_csv(f[0], low_memory=False)
    d = df[df.record_type == "DAILY"][["ymd", "combined_nav"]].copy()
    d["combined_nav"] = pd.to_numeric(d.combined_nav)
    navs[base] = d.sort_values("ymd").set_index("ymd")["combined_nav"]

idx = None
for s in navs.values():
    idx = s.index if idx is None else idx.intersection(s.index)
R = pd.DataFrame({k: navs[k].reindex(idx).pct_change() for k in navs}).dropna()
R.index = pd.to_datetime(R.index)
N = R.shape[1]

ref = pd.read_csv(ref_csv, low_memory=False)
ev = ref[ref.record_type == "EVENT_CAPIT"][["ymd", "value"]].copy()
ev["ymd"] = pd.to_datetime(ev.ymd)
ev["size"] = pd.to_numeric(ev.value)
ev = ev.sort_values("ymd").reset_index(drop=True)
tx = ref[(ref.record_type == "TX") & ref.play_type.astype(str).str.startswith("CAPIT")].copy()
tx["ymd"] = pd.to_datetime(tx.ymd)
tx["eid"] = tx.play_type.str.extract(r"_E(\d+)$")[0].astype(int)

windows = []
for eid in range(len(ev)):
    g = tx[tx.eid == eid]
    if g.empty:
        continue
    d0, d1 = ev.loc[eid, "ymd"], g.ymd.max()
    m = (R.index >= d0) & (R.index <= d1)
    if m.sum() >= 5:
        windows.append((eid, d0, m))
blocks = [R.loc[m] for _, _, m in windows]
NE = len(blocks)

# ---------- 1. dau loi nhuan / Sharpe tung su kien ----------
print("=" * 78)
print("1. DAU KET QUA CUA TUNG SU KIEN (loi suat tich luy trong cua so, %)")
print("=" * 78)
key = ["cash", "idle", "booknav", "navsize:0.25", "navsize:0.40"]
print(f"{'E':>4} {'ngay':>12} {'size':>5} " + " ".join(f"{k:>13}" for k in key)
      + f" {'CHENH idle-0.25':>16}")
neg = 0
rows = []
for (eid, d0, m), b in zip(windows, blocks):
    cum = (1 + b).prod() - 1
    rows.append(cum)
    if cum["idle"] < cum["cash"]:
        pass
    excess = cum["idle"] - cum["cash"]        # phan do arm CAPIT to hon dong gop
    if excess < 0:
        neg += 1
    print(f"E{eid:>3} {str(d0.date()):>12} {ev.loc[eid,'size']:>5.3f} "
          + " ".join(f"{100*cum[k]:>12.2f}%" for k in key)
          + f" {100*(cum['idle']-cum['navsize:0.25']):>15.2f}%")
cum_df = pd.DataFrame(rows)
print(f"\nSo su kien ma leg phoi nhiem LON NHAT (`idle`) THUA baseline `cash`: {neg}/{NE}")
print("  -> neu ~0 thi mau KHONG chua truong hop phoi nhiem lon bi phat")

# ---------- 2. phoi nhiem vs Sharpe: co don dieu khong ----------
print("\n" + "=" * 78)
print("2. XEP HANG SHARPE (cua so su kien) vs PHOI NHIEM trung binh")
print("=" * 78)
Rev = pd.concat(blocks)
sr_ev = Rev.mean() / Rev.std(ddof=1) * np.sqrt(252)
# proxy phoi nhiem: do lech chuan cua chenh lech so voi `cash` (leg cang to cang lech)
expo = (Rev.sub(Rev["cash"], axis=0)).std() * np.sqrt(252)
t = pd.DataFrame({"SR_event": sr_ev, "expo_proxy": expo}).sort_values("SR_event", ascending=False)
t["rank_SR"] = t.SR_event.rank(ascending=False)
t["rank_expo"] = t.expo_proxy.rank(ascending=False)
print(t.round(4).to_string())
rho = t.SR_event.corr(t.expo_proxy, method="spearman")
print(f"\nSpearman(SR su kien, phoi nhiem) = {rho:+.3f}")
print("  -> gan +1 nghia la 'cang phoi nhiem cang thang' tren CHINH mau nay")

# ---------- 3. leave-worst-out: bo cac su kien thang dam nhat ----------
print("\n" + "=" * 78)
print("3. PBO khi LOAI k su kien co dong gop CAPIT duong LON NHAT (leave-best-out)")
print("=" * 78)


def pbo_of(bl):
    S = len(bl)
    k = S // 2
    logits = []
    wins = Counter()
    for c in itertools.combinations(range(S), k):
        cs = set(c)
        Ris = pd.concat([bl[i] for i in c])
        Ros = pd.concat([bl[i] for i in range(S) if i not in cs])
        best = (Ris.mean() / Ris.std(ddof=1)).idxmax()
        wins[best] += 1
        rk = (Ros.mean() / Ros.std(ddof=1)).rank().loc[best]
        w = rk / (N + 1.0)
        logits.append(np.log(w / (1 - w)))
    logits = np.array(logits)
    return float((logits <= 0).mean()), wins.most_common(1)[0]


contrib = cum_df["idle"] - cum_df["cash"]
order = np.argsort(-contrib.values)      # su kien dong gop duong lon nhat truoc
print(f"{'k bo':>5} {'PBO':>8}  {'leg thang IS nhieu nhat':>28}  su kien con lai")
for k in range(0, 6):
    keep = [i for i in range(NE) if i not in set(order[:k])]
    if len(keep) < 6:
        break
    p, top = pbo_of([blocks[i] for i in keep])
    print(f"{k:>5} {p:>8.4f}  {top[0]:>20s} {100*top[1]/max(1,len(list(itertools.combinations(range(len(keep)), len(keep)//2)))):5.1f}%"
          f"  n={len(keep)}")

print("\nKET LUAN CHAN DOAN se ghi trong bao cao.")
