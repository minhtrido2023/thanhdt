#!/usr/bin/env python
"""BUOC C — bien the ROBUSTNESS: overlay CO TAI DAU TU (compounding).

Ly do ton tai (tu phe binh, §6 ke hoach): overlay cong-them o step_c_wholebook.py de lai P&L bien
duoi dang TIEN MAT nam im den cuoi chuoi => KHONG duoc tai dau tu theo nhip cua so => phep do do
LAM NHE loi ich cua don bay. Neu ket luan NO-GO chi ton tai nho gia dinh bat loi nay thi no khong
dang tin. O day dung bien the CO LOI NHAT co the bien minh duoc cho phe "margin tot":
sleeve size scale theo NAV TONG da phinh ra, va moi P&L bien duoc tai dau tu theo suat sinh loi
NGAY cua chinh chuong trinh (r_L0), tuc lai kep day du.

Neu NO-GO van dung o day => ket luan ben, khong phai san pham cua 1 lua chon ke toan.
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

r_l0 = nav0.pct_change().fillna(0.0).to_numpy()      # suat sinh loi ngay cua chuong trinh
IDX = {d: i for i, d in enumerate(nav0.index)}


def metrics(s):
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1
    dd = (s / s.cummax() - 1).min()
    lr = np.diff(np.log(s.to_numpy()))
    return cagr, dd, (lr.mean() / lr.std() * np.sqrt(252) if lr.std() > 0 else np.nan)


def overlay_comp(f, c, maint, penalty):
    """NAV tong mo phong tien tien: moi ngay chay lai kep tren CA phan P&L bien da tich luy."""
    n = len(nav0)
    nav = np.empty(n); nav[0] = nav0.iloc[0]
    # tai san/no cua phan VAY THEM dang mo, theo ngay
    extraA = np.zeros(n); extraL = np.zeros(n)
    calls = []

    segs = []
    for _, e in ev.iterrows():
        if e["size"] <= 0:
            continue
        p = paths[paths["event"] == e["event"]].sort_values("t")
        tt = p["time"].to_numpy(); nv = p["nav"].to_numpy(float)
        i0 = IDX.get(pd.Timestamp(tt[0]))
        if i0 is None:
            continue
        segs.append((i0, e, nv, (tt - tt[0]) / np.timedelta64(1, "D")))

    for t in range(1, n):
        # so co ban chay lai kep theo suat sinh loi cua chuong trinh
        nav[t] = nav[t - 1] * (1 + r_l0[t])
        for i0, e, nv, dd_ in segs:
            k = t - i0
            if k < 0 or k >= len(nv):
                continue
            if k == 0:
                continue
            # sleeve size scale theo do phinh cua NAV tong (bien the CO LOI cho margin)
            scale = nav[i0] / nav0.iloc[i0]
            S0 = float(lagref.asof(e["event"])) * float(e["size"]) * scale
            borrow = (f - 1.0) * S0
            A = borrow * (1 - TC) * nv[k]
            L = borrow * (1 + c * dd_[k] / 365.0)
            Ap = borrow * (1 - TC) * nv[k - 1]
            Lp = borrow * (1 + c * dd_[k - 1] / 365.0)
            nav[t] += (A - L) - (Ap - Lp)          # bien dong equity cua phan vay them
            if (A - L) / (A + nav[t]) < maint:
                calls.append(f"{e['event'].date()}")
    return pd.Series(nav, index=nav0.index), len(set(calls)), sorted(set(calls))


def main():
    lines = []; P = lines.append
    c0, d0, s0 = metrics(nav0)
    IS = (nav0.index >= "2014-01-01") & (nav0.index <= "2019-12-31")
    OOS = nav0.index >= "2020-01-01"
    c0i, _, _ = metrics(nav0[IS]); c0o, _, _ = metrics(nav0[OOS])

    P("=" * 92)
    P("BUOC C-bis — overlay CO TAI DAU TU (bien the CO LOI NHAT cho phe 'margin tot')")
    P("=" * 92)
    P(f"CONTROL: CAGR {c0:.2%} | MaxDD {d0:.2%} | IS {c0i:.2%} | OOS {c0o:.2%}")
    P("")
    P(f"{'f':>6}{'CAGR':>9}{'dCAGR':>9}{'MaxDD':>9}{'dMaxDD xau':>12}"
      f"{'dCAGR_IS':>10}{'dCAGR_OOS':>11}{'#call':>7}")
    for f in F_GRID:
        s, nc, cd = overlay_comp(f, 0.140, 0.35, 0.02)
        cg, dd, sh = metrics(s)
        ci, _, _ = metrics(s[IS]); co, _, _ = metrics(s[OOS])
        P(f"{f:>6.2f}{cg:>9.2%}{cg-c0:>+9.2%}{dd:>9.2%}{(d0-dd)*100:>+11.2f}pp"
          f"{ci-c0i:>+10.2%}{co-c0o:>+11.2%}{nc:>7d}")
    P("")
    P("DOC: neu dCAGR_OOS VAN am o bien the co tai dau tu nay thi ket luan NO-GO cua G-C")
    P("KHONG phai san pham cua gia dinh ke toan 'tien mat nam im' o step_c_wholebook.py.")
    txt = "\n".join(lines)
    print(txt)
    (HERE / "step_c2_compounded.log").write_text(txt + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
