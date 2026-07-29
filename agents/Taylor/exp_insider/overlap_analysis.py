"""Vong 3 — job Taylor_20260729_032713.
Do phan GIA TANG that cua co insider-sell (§3.4) so voi anomaly_scan/forensic_flags dang co.
Khong sweep them tham so: co insider DA PIN o §3.4, co anomaly copy nguyen van tu anomaly_scan.py.
"""
import numpy as np, pandas as pd

D = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_insider"
WC = "/home/trido/thanhdt/WorkingClaude"

df = pd.read_csv(f"{D}/panel2.csv", parse_dates=["time"])
an = pd.read_csv(f"{D}/anom_replay.csv", parse_dates=["time"])
for c in ["anom_w", "anom_h", "anom_w_down"]:
    an[c] = an[c].astype(str).str.lower().eq("true")

df = df.merge(an, on=["time", "ticker"], how="left")
for c in ["anom_w", "anom_h", "anom_w_down"]:
    # BAT BUOC astype(bool): left-join sinh NaN -> cot thanh dtype=object, khi do `~col`
    # lam BITWISE-NOT tren Python bool (~True = -2, truthy) chu khong phai phu dinh logic.
    df[c] = df[c].fillna(False).astype(bool)

df["ey"] = np.where(df.PE > 0, 1.0 / df.PE, np.nan)
df["ey_rk"] = df.groupby("time").ey.rank(pct=True)
df["sell_pct"] = np.where(df.oshares > 0, df.sell_sh_90 / df.oshares, np.nan)
# CO INSIDER — copy nguyen van dinh nghia da pin o §3.4 (gate_analysis.py dong cuoi)
df["INS"] = ((df.sell_pct >= 0.01) & (df.nsell_90 > df.nbuy_90)).fillna(False)
df["bad"] = df.fwd60 < -0.20

x = df.dropna(subset=["fwd60"]).copy()
cand = x[(x.rating8l <= 3) & (x.ey_rk >= 2 / 3)].copy()

print(f"Panel: {len(df)} obs, {df.time.nunique()} thang, {df.time.min().date()} -> {df.time.max().date()}")
print(f"Co fwd60: {len(x)} obs | ro ung vien mua (rating<=3 & ey top-tercile): {len(cand)} obs")
print(f"Ty le bat: INS={x.INS.mean():.4f} | anom_w={x.anom_w.mean():.4f} | anom_h={x.anom_h.mean():.4f} "
      f"| anom_w_down={x.anom_w_down.mean():.4f}")
# SELF-CHECK: tai lap dung con so da PIN o §3.4 (INS bat 5,4% universe, P(sap)=19,68%, nen 11,28%)
_p_ins, _p_base = x[x.INS].bad.mean(), x[~x.INS].bad.mean()
print(f"SELF-CHECK vs §3.4 pin: INS bat {x.INS.mean()*100:.1f}% (pin 5,4%) | "
      f"P(sap|INS)={_p_ins*100:.2f}% (pin 19,68%) | nen={_p_base*100:.2f}% (pin 11,28%) | "
      f"lift={_p_ins/_p_base:.3f}x (pin 1,745x)")
assert abs(len(x) - (x.INS & x.anom_w).sum() - (x.INS & ~x.anom_w).sum()
           - (~x.INS & x.anom_w).sum() - (~x.INS & ~x.anom_w).sum()) == 0, "2x2 khong khep tong"


def two_by_two(s, A, lab):
    n = len(s)
    a = s[s.INS & s[A]]; b = s[s.INS & ~s[A]]
    c = s[~s.INS & s[A]]; d = s[~s.INS & ~s[A]]
    print(f"\n--- 2x2: INS (insider-sell >=1% CP luu hanh/90d) x {lab} | mau {lab_name} ---")
    print(f"{'':22s} {A}=T {'':6s} {A}=F")
    print(f"  INS=T{'':16s} {len(a):6d}       {len(b):6d}      (tong INS {len(a)+len(b):6d})")
    print(f"  INS=F{'':16s} {len(c):6d}       {len(d):6d}      (tong {len(c)+len(d):6d})")
    if len(a) + len(b) > 0:
        print(f"  => TRONG SO MA BI INS: {len(a)/(len(a)+len(b))*100:.1f}% DA co {A} (trung lap) | "
              f"{len(b)/(len(a)+len(b))*100:.1f}% KHONG co {A} (tin hieu MOI)")
    if len(a) + len(c) > 0:
        print(f"  => chieu nguoc: trong so ma bi {A}, {len(a)/(len(a)+len(c))*100:.1f}% cung bi INS")
    # phi / odds-ratio
    A_, B_, C_, D_ = len(a), len(b), len(c), len(d)
    orr = (A_ * D_) / (B_ * C_) if B_ * C_ > 0 else np.nan
    phi = (A_ * D_ - B_ * C_) / np.sqrt((A_ + B_) * (C_ + D_) * (A_ + C_) * (B_ + D_))
    print(f"  odds-ratio={orr:.2f}  phi={phi:.4f}  (phi~0 => hai co gan nhu DOC LAP)")
    return a, b, c, d


def tail(sub, lab, base_p, base_n):
    if len(sub) < 30:
        print(f"  {lab:38s} n={len(sub):5d}  (qua nho, bo qua)")
        return
    p = sub.bad.mean()
    pool = (sub.bad.sum() + base_p * base_n) / (len(sub) + base_n)
    z = (p - base_p) / np.sqrt(pool * (1 - pool) * (1 / len(sub) + 1 / base_n))
    print(f"  {lab:38s} n={len(sub):5d}  P(fwd60<-20%)={p:.4f}  lift={p/base_p:.3f}x  z={z:.2f}")


for lab_name, s in [("TOAN UNIVERSE", x), ("RO UNG VIEN MUA", cand)]:
    print("\n" + "=" * 78)
    print(f"### {lab_name} ###")
    for A, labA in [("anom_w", "anomaly tier-W (thuc te cho ung vien mua)"),
                    ("anom_h", "anomaly tier-H (nguong LONG = bien tren do phu)")]:
        a, b, c, d = two_by_two(s, A, labA)
        print(f"\n  P(fwd60 < -20%) theo tung o ({A}):")
        base_p, base_n = d.bad.mean(), len(d)
        print(f"  {'NEN: khong co ca 2 co':38s} n={base_n:5d}  P={base_p:.4f}")
        tail(a, "INS & " + A + " (trung ca 2)", base_p, base_n)
        tail(b, "INS RIENG (khong co " + A + ")", base_p, base_n)
        tail(c, A + " RIENG (khong co INS)", base_p, base_n)
        # recall increment
        tot_bad = s.bad.sum()
        print(f"  Recall: {A} bat {c.bad.sum()+a.bad.sum():4d}/{tot_bad} ca sap ({(c.bad.sum()+a.bad.sum())/tot_bad*100:.1f}%) "
              f"| INS THEM {b.bad.sum():3d} ca ({b.bad.sum()/tot_bad*100:.1f}pp) "
              f"voi chi phi {len(b)} co moi")

print("\n" + "=" * 78)
print("### ON DINH IS/OOS cua phan INS-RIENG (khong co anomaly tier-W) ###")
for lab_name, s in [("toan universe", x), ("ro ung vien", cand)]:
    for per, m in [("IS 2015-19", s.time < "2020-01-01"), ("OOS 2020+", s.time >= "2020-01-01")]:
        ss = s[m]
        b = ss[ss.INS & ~ss.anom_w]; d = ss[~ss.INS & ~ss.anom_w]
        if len(b) < 30:
            print(f"  {lab_name:14s} {per:11s}: n={len(b)} qua nho"); continue
        pb, pd_ = b.bad.mean(), d.bad.mean()
        pool = (b.bad.sum() + d.bad.sum()) / (len(b) + len(d))
        z = (pb - pd_) / np.sqrt(pool * (1 - pool) * (1 / len(b) + 1 / len(d)))
        print(f"  {lab_name:14s} {per:11s}: n_INS_rieng={len(b):5d} P={pb:.4f} vs nen {pd_:.4f} "
              f"lift={pb/pd_:.3f}x z={z:.2f}")

print("\n" + "=" * 78)
print("### FORENSIC_FLAGS — do phu point-in-time ###")
ff = pd.read_csv(f"{WC}/data/forensic_flags.csv", parse_dates=["date"])
print(ff[["ticker", "flag_type", "severity", "date"]].to_string(index=False))
print(f"\nTat ca {len(ff)} co deu co date = {sorted(ff.date.dt.date.unique())}")
fmap = dict(zip(ff.ticker, ff.date))
x["FOR_pit"] = x.apply(lambda r: r.ticker in fmap and fmap[r.ticker] <= r.time, axis=1)
print(f"PIT: so quan sat co forensic flag hieu luc trong panel 2015-06..2026-06 = {x.FOR_pit.sum()} "
      f"({x.FOR_pit.mean()*100:.4f}% panel)")
print(f"  -> nam o cac thang: {sorted(x[x.FOR_pit].time.dt.date.unique())}")
print(f"  trong so do, bao nhieu cung bi INS: {x[x.FOR_pit].INS.sum()}/{x.FOR_pit.sum()}")
print(f"  trong ro ung vien mua (rating<=3): {cand.ticker.isin(ff.ticker).sum()} quan sat "
      f"(forensic cap rating->5 tu ngay flag => cau truc KHONG the nam trong ro sau 2026-06-20)")
print("\nKiem tra TINH (KHONG point-in-time, chi tham khao): 11 ma forensic co tung bi INS bat khong?")
seen = df[df.ticker.isin(ff.ticker)]
for t in ff.ticker:
    sub = seen[seen.ticker == t]
    if len(sub) == 0:
        print(f"  {t}: khong co trong universe_pit ky nay"); continue
    print(f"  {t}: {len(sub):3d} quan sat trong universe, INS bat {sub.INS.sum():3d} lan "
          f"({'CO trung' if sub.INS.sum() else 'KHONG trung'})")

print("\n" + "=" * 78)
print("### BIEN THE THUC TE: anomaly_scan chi QUET hold ∪ watchlist(rating<=2) ###")
print("(replay o tren ap quy tac gia cho TOAN universe => da UU AI anomaly toi da.")
print(" Thuc te ma rating 3 khong nam trong universe quet => anomaly KHONG BAO GIO bat duoc.)")
for lab_name, s in [("toan universe", x), ("ro ung vien mua", cand)]:
    s = s.copy()
    s["anom_real"] = s.anom_w & (s.rating8l <= 2)   # bo qua nhanh 'hold' (khong tai lap duoc lich su)
    a = s[s.INS & s.anom_real]; b = s[s.INS & ~s.anom_real]; d = s[~s.INS & ~s.anom_real]
    ov = len(a) / (len(a) + len(b)) * 100
    pb, pd_ = b.bad.mean(), d.bad.mean()
    pool = (b.bad.sum() + d.bad.sum()) / (len(b) + len(d))
    z = (pb - pd_) / np.sqrt(pool * (1 - pool) * (1 / len(b) + 1 / len(d)))
    print(f"  {lab_name:16s}: overlap chi {ov:.1f}% | INS-rieng n={len(b):5d} P={pb:.4f} vs nen {pd_:.4f} "
          f"lift={pb/pd_:.3f}x z={z:.2f}")
print(f"\n  Ty trong ro ung vien mua co rating 3 (ngoai tam quet anomaly): "
      f"{(cand.rating8l == 3).mean()*100:.1f}%")
