#!/usr/bin/env python
"""BUOC C — AUDIT bat buoc (guard #10 §4 + meta-gate §5).

HAI van de phat hien o C va C-bis, phai giai quyet TRUOC khi bao cao bat cu con so nao:

(1) C (cong-them, tien mat nam im) va C-bis (tai dau tu) cho ket luan NGUOC NHAU ve dCAGR_OOS
    (am vs duong). Meta-gate §5 bat xu ly "ket luan phu thuoc lua chon" nhu NO-GO — nhung truoc
    khi ket luan FRAGILE phai kiem xem 1 trong 2 co phai AO ANH DO LUONG khong.
(2) C-bis cho f=1,5 => dCAGR +3,07pp/nam, VUOT tran ky vong §2.2 (+2,1pp). Guard #10: tu dong
    nghi van, dung lai audit.

CHAN DOAN cho (1): trong ban cong-them, lai cua giai doan IS nam duoi dang TIEN MAT 0%/nam suot
ca giai doan OOS => keo TUT toc do tang truong do trong cua so OOS. dCAGR_OOS am co the hoan
toan la DO LUONG BAN, khong phai "don bay mat tac dung sau 2020". Phep do sach: chay overlay
CHI voi su kien trong tung cua so, do CAGR trong DUNG cua so do, khong mang lai IS sang OOS.

CHAN DOAN cho (2): tach tran ky vong theo so lieu THUC DO (sleeve % NAV thuc, so su kien thuc)
thay vi tham so xap xi cua §2.2.
"""
import numpy as np
import pandas as pd
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
WC = Path("/home/trido/thanhdt/WorkingClaude")
L0 = (WC / "data" / "v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_"
      "wtnamecap_advprice_exp_s4p2_L0_control_univpit.csv")
TC = 0.00075
F_GRID = [1.0, 1.1, 1.2, 1.3, 1.5]

raw = pd.read_csv(L0, low_memory=False)
raw["time"] = pd.to_datetime(raw["ymd"], errors="coerce")
raw = raw[raw["time"].notna()]
nav0 = raw[raw["combined_nav"].notna()].groupby(
    raw["time"].dt.normalize())["combined_nav"].last().astype(float)
lagref = raw[raw["nav_lag_ref"].notna()].groupby(
    raw["time"].dt.normalize())["nav_lag_ref"].last().astype(float)

ev = pd.read_csv(HERE / "events_outcome_pit.csv", parse_dates=["event"])
ev = ev[(ev["skip"].fillna("") == "") & (ev["event"] >= "2014-01-01")].sort_values("event")
sz = pd.read_csv(EXP / "events_outcome.csv", parse_dates=["event"]).set_index("event")["size"]
ev["size"] = ev["event"].map(sz)
ev = ev.reset_index(drop=True)
paths = pd.read_csv(HERE / "event_paths_pit.csv", parse_dates=["event", "time"])
IDX = {d: i for i, d in enumerate(nav0.index)}


def cagr(s):
    return (s.iloc[-1] / s.iloc[0]) ** (365.25 / (s.index[-1] - s.index[0]).days) - 1


def maxdd(s):
    return (s / s.cummax() - 1).min()


def run(f, c, maint, penalty, lo, hi, compound):
    """Overlay CHI voi su kien trong [lo,hi]; tra ve chuoi NAV cat dung cua so do."""
    m = (nav0.index >= lo) & (nav0.index <= hi)
    base = nav0[m]
    n = len(base)
    sub = {d: i for i, d in enumerate(base.index)}
    r_l0 = base.pct_change().fillna(0.0).to_numpy()

    segs = []
    for _, e in ev.iterrows():
        if e["size"] <= 0 or not (pd.Timestamp(lo) <= e["event"] <= pd.Timestamp(hi)):
            continue
        p = paths[paths["event"] == e["event"]].sort_values("t")
        tt = p["time"].to_numpy(); nv = p["nav"].to_numpy(float)
        i0 = sub.get(pd.Timestamp(tt[0]))
        if i0 is None or i0 + len(nv) > n:
            continue
        segs.append((i0, e, nv, (tt - tt[0]) / np.timedelta64(1, "D")))

    nav = np.empty(n); nav[0] = base.iloc[0]
    calls = set()
    for t in range(1, n):
        nav[t] = nav[t - 1] * (1 + r_l0[t])
        for i0, e, nv, dd_ in segs:
            k = t - i0
            if k <= 0 or k >= len(nv):
                continue
            scale = (nav[i0] / base.iloc[i0]) if compound else 1.0
            borrow = (f - 1.0) * float(lagref.asof(e["event"])) * float(e["size"]) * scale
            if borrow <= 0:
                continue                      # f=1,0 => khong vay => KHONG the co margin call
            A = borrow * (1 - TC) * nv[k]
            L = borrow * (1 + c * dd_[k] / 365.0)
            Ap = borrow * (1 - TC) * nv[k - 1]
            Lp = borrow * (1 + c * dd_[k - 1] / 365.0)
            nav[t] += (A - L) - (Ap - Lp)
            if (nav[t] + A - L) / (nav[t] + A) < maint:
                calls.add(str(e["event"].date()))
    return pd.Series(nav, index=base.index), sorted(calls)


def main():
    lines = []; P = lines.append
    P("=" * 96)
    P("AUDIT BUOC C (guard #10 §4 + meta-gate §5) — phep do SACH tung cua so")
    P("=" * 96)
    P("Van de: ban cong-them de lai IS cua giai doan truoc duoi dang tien mat 0%/nam trong")
    P("suot OOS => dCAGR_OOS am co the la AO ANH DO LUONG. Phep do sach: overlay CHI su kien")
    P("cua tung cua so, do CAGR trong DUNG cua so do (khong mang von tu ky truoc sang).")
    P("")

    wins = [("IS  2014-2019", "2014-01-01", "2019-12-31"),
            ("OOS 2020-nay ", "2020-01-01", "2026-12-31"),
            ("FULL 2014-nay", "2014-01-01", "2026-12-31")]

    for mode, tag in [(False, "CONG-THEM (tien mat nam im)"), (True, "TAI DAU TU (compounding)")]:
        P("-" * 96)
        P(f"BAN: {tag}   [adversarial c=14%, maint 35%, pen 2%]")
        P("-" * 96)
        P(f"{'cua so':<16}{'f':>6}{'CAGR':>9}{'dCAGR':>9}{'MaxDD':>9}"
          f"{'dMaxDD xau':>12}{'#call':>7}")
        for wname, lo, hi in wins:
            b, _ = run(1.0, 0.140, 0.35, 0.02, lo, hi, mode)
            cb, db = cagr(b), maxdd(b)
            for f in F_GRID[1:]:
                s, cl = run(f, 0.140, 0.35, 0.02, lo, hi, mode)
                P(f"{wname if f==F_GRID[1] else '':<16}{f:>6.2f}{cagr(s):>9.2%}"
                  f"{cagr(s)-cb:>+9.2%}{maxdd(s):>9.2%}{(db-maxdd(s))*100:>+11.2f}pp"
                  f"{len(cl):>7d}")
            P("")

    # ---------------------------------------------------------- audit tran ky vong (guard #10)
    P("=" * 96)
    P("AUDIT TRAN KY VONG (guard #10) — tinh lai tran bang SO LIEU THUC DO, khong dung xap xi §2.2")
    P("=" * 96)
    shares, yrs = [], (nav0.index[-1] - nav0.index[0]).days / 365.25
    for _, e in ev.iterrows():
        S0 = float(lagref.asof(e["event"])) * float(e["size"])
        shares.append(S0 / float(nav0.asof(e["event"])))
    sh = float(np.mean(shares))
    edge = float((ev["r"] - (0.14 * ev["cal_days"] / 365 + 0.0015)).mean())
    n_yr = len(ev) / yrs
    P(f"  sleeve TB thuc do        = {sh:.1%} NAV  (§2.2 gia dinh 31%)")
    P(f"  edge sau lai vay 14%     = {edge:+.2%}/su kien  (§2.2 dung +9,75%)")
    P(f"  tan suat su kien thuc do = {n_yr:.2f}/nam  (§2.2 dung 1,4)")
    for f in F_GRID[1:]:
        P(f"  tran tinh lai f={f:.2f}: {(f-1)*sh*edge*n_yr*100:+.2f}pp/nam")
    P("")
    P("  => Tran §2.2 (+2,1pp) tinh cho sleeve 31%; sleeve THUC lon hon nen tran that cao hon.")
    P("     Nhung phan VUOT tran cua ban tai-dau-tu con den tu viec sleeve duoc scale theo NAV")
    P("     da phinh (lai kep chong lai kep) — day la ban DOC NHIEU NHAT co the, khong phai so")
    P("     trung tam. Bao cao phai neo vao ban cong-them (than trong) lam so chinh.")

    txt = "\n".join(lines)
    print(txt)
    (HERE / "step_c3_clean_isoos.log").write_text(txt + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
