#!/usr/bin/env python
"""BUOC C (§2.1 ke hoach margin_kelly_full_cycle_plan_20260803.md) — tich hop TOAN SO.

Overlay phan VAY THEM len chuoi NAV ngay that cua chan L0 control (pin 28,86%, univ_pit).

QUAN TRONG (diem mo hinh hoa, ghi ro de kiem tra duoc): chuoi L0 control DA CHUA sleeve CAPIT
o muc 1x (CAPIT la co che production). Vi vay overlay chi duoc cong phan BIEN — tuc phan mua
THEM bang tien vay `(f-1) x sleeve_capital` — neu khong se DEM HAI LAN phan von tu co.
    A_tong(t) = NAV_L0(t) + (f-1)*S*(1+ret_t)      [tai san]
    L_tong(t) = (f-1)*S*(1 + c*d_t/365)            [no]
    NAV_tong(t) = A_tong(t) - L_tong(t)
Sleeve size S = NAV_book_LAG x capit_size (luat production user chot 07-20; `nav_lag_ref` doc
thang tu CSV L0, `capit_size` = capit_base(state, dd52, vn_cool) da tinh san o cot `size`).

GATE G-C (§5, dang ky TRUOC):
    DeltaCAGR > 0 o CA IS(2014-19) LAN OOS(2020+); DeltaMaxDD <= +1,0pp;
    LOO per-year: khong nam nao ganh >= 50% tong edge; 0 margin call toan-so tren path adversarial.

RESEARCH-ONLY.
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

# ---------------------------------------------------------------- chuoi NAV control
raw = pd.read_csv(L0, low_memory=False)
raw["time"] = pd.to_datetime(raw["ymd"], errors="coerce")
raw = raw[raw["time"].notna()]
nav0 = raw[raw["combined_nav"].notna()].groupby(
    raw["time"].dt.normalize())["combined_nav"].last().astype(float)
lagref = raw[raw["nav_lag_ref"].notna()].groupby(
    raw["time"].dt.normalize())["nav_lag_ref"].last().astype(float)
CAL = nav0.index.to_numpy()

# ---------------------------------------------------------------- su kien + size production
ev = pd.read_csv(HERE / "events_outcome_pit.csv", parse_dates=["event"])
ev = ev[(ev["skip"].fillna("") == "") & (ev["event"] >= "2014-01-01")].sort_values("event")
sz = pd.read_csv(EXP / "events_outcome.csv", parse_dates=["event"]).set_index("event")["size"]
ev["size"] = ev["event"].map(sz)          # capit_size chi phu thuoc state/dd52/vn_cool (muc thi
ev = ev.reset_index(drop=True)            # truong) => dong nhat giua 2 chan universe
paths = pd.read_csv(HERE / "event_paths_pit.csv", parse_dates=["event", "time"])


def metrics(s):
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1
    dd = (s / s.cummax() - 1).min()
    lr = np.diff(np.log(s.to_numpy()))
    shp = lr.mean() / lr.std() * np.sqrt(252) if lr.std() > 0 else np.nan
    return cagr, dd, shp


def overlay(f, c, maint, penalty, drop_year=None, drop_event=None):
    """Tra ve (chuoi NAV tong, so margin call toan-so, ngay call)."""
    add = pd.Series(0.0, index=nav0.index)     # P&L bien cong don (VND)
    assets_extra = pd.Series(0.0, index=nav0.index)
    debt = pd.Series(0.0, index=nav0.index)
    calls = []

    for _, e in ev.iterrows():
        if drop_year and e["event"].year == drop_year:
            continue
        if drop_event is not None and e["event"] == drop_event:
            continue
        S0 = float(lagref.asof(e["event"])) * float(e["size"])
        borrow = (f - 1.0) * S0
        if borrow <= 0:
            continue
        p = paths[paths["event"] == e["event"]].sort_values("t")
        tt = p["time"].to_numpy(); nv = p["nav"].to_numpy(float)
        d = (tt - tt[0]) / np.timedelta64(1, "D")
        A = borrow * (1 - TC) * nv                 # tai san mua bang tien vay
        L = borrow * (1 + c * d / 365.0)
        idx = nav0.index.get_indexer(pd.DatetimeIndex(tt))
        base = nav0.to_numpy()[idx]                # NAV control tai cung ngay
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = (base + A - L) / (base + A)    # equity/asset TOAN SO
        ratio[0] = np.inf
        hit = np.where(ratio < maint)[0]
        k = min(int(hit[0]) + 1, len(nv) - 1) if len(hit) else len(nv) - 1
        if len(hit):
            calls.append(f"{e['event'].date()}@{pd.Timestamp(tt[k]).date()}")
            pnl_end = A[k] * (1 - TC) * (1 - penalty) - L[k]
        else:
            pnl_end = A[k] * (1 - TC) - L[k]
        seg = nav0.index[idx[0]:idx[k] + 1]
        add.loc[seg] += (A[:k + 1] - L[:k + 1])
        assets_extra.loc[seg] += A[:k + 1]
        debt.loc[seg] += L[:k + 1]
        if idx[k] + 1 < len(nav0):
            add.iloc[idx[k] + 1:] += pnl_end       # tien mat con lai sau khi dong vi the
    return nav0 + add, len(calls), calls


def main():
    lines = []; P = lines.append
    P("=" * 96)
    P("BUOC C — tich hop TOAN SO (whole-book overlay) len chuoi NAV that cua L0 control")
    P("Ke hoach §2.1 | GATE G-C §5 | ro `universe_pit`, N=17 su kien 2014+")
    P("=" * 96)
    c0, d0, s0 = metrics(nav0)
    P(f"CONTROL L0: CAGR {c0:.2%} | MaxDD {d0:.2%} | Sharpe {s0:.2f} | "
      f"NAV cuoi {nav0.iloc[-1]/1e9:.2f}B | {nav0.index[0].date()} -> {nav0.index[-1].date()}")
    P(f"  (doi chieu pin R3 08-03: CAGR 28,86% / DD -17,8% — chan control tai lap)")
    P("")
    P("Sleeve size = NAV_book_LAG x capit_size (luat production 07-20):")
    for _, e in ev.iterrows():
        S0 = float(lagref.asof(e["event"])) * float(e["size"])
        P(f"  {e['event'].date()}  size={e['size']:.2f}  NAV_lag={lagref.asof(e['event'])/1e9:7.2f}B"
          f"  -> sleeve {S0/1e9:6.2f}B  ({S0/nav0.asof(e['event']):.1%} NAV tong)")
    P("")

    IS = (nav0.index >= "2014-01-01") & (nav0.index <= "2019-12-31")
    OOS = nav0.index >= "2020-01-01"

    for tag, c, mt, pen in [("BASE  c=12,5% maint=30% pen=1%", 0.125, 0.30, 0.01),
                            ("ADV   c=14%  maint=35% pen=2%", 0.140, 0.35, 0.02)]:
        P("-" * 96)
        P(f"KICH BAN: {tag}")
        P("-" * 96)
        P(f"{'f':>6}{'CAGR':>9}{'dCAGR':>9}{'MaxDD':>9}{'dMaxDD':>9}{'Sharpe':>8}"
          f"{'NAVcuoi':>10}{'dCAGR_IS':>10}{'dCAGR_OOS':>11}{'#call':>7}")
        for f in F_GRID:
            s, nc, cd = overlay(f, c, mt, pen)
            cg, dd, sh = metrics(s)
            ci, _, _ = metrics(s[IS]); c0i, _, _ = metrics(nav0[IS])
            co, _, _ = metrics(s[OOS]); c0o, _, _ = metrics(nav0[OOS])
            P(f"{f:>6.2f}{cg:>9.2%}{cg-c0:>+9.2%}{dd:>9.2%}{(dd-d0)*100:>+8.2f}pp"
              f"{sh:>8.2f}{s.iloc[-1]/1e9:>9.2f}B{ci-c0i:>+10.2%}{co-c0o:>+11.2%}{nc:>7d}")
            if cd:
                P(f"        margin call: {cd}")
        P("")

    # ---------------------------------------------------------------- GATE G-C
    P("=" * 96)
    P("GATE G-C (§5) — danh gia tren kich ban ADVERSARIAL (maint 35%, lai 14%, pen 2%)")
    P("=" * 96)
    res = {}
    for f in F_GRID[1:]:
        s, nc, cd = overlay(f, 0.140, 0.35, 0.02)
        cg, dd, sh = metrics(s)
        ci, _, _ = metrics(s[IS]); c0i, _, _ = metrics(nav0[IS])
        co, _, _ = metrics(s[OOS]); c0o, _, _ = metrics(nav0[OOS])
        d_is, d_oos = ci - c0i, co - c0o
        # dMaxDD tinh theo huong "XAU DI bao nhieu pp" (duong = te hon control), §5 nguong <= +1,0pp
        d_dd = (d0 - dd) * 100
        # LOO theo NAM (dung nhu gate dang ky §5)
        tot = cg - c0
        loo = {}
        for y in sorted(ev["event"].dt.year.unique()):
            sy, _, _ = overlay(f, 0.140, 0.35, 0.02, drop_year=int(y))
            cy, _, _ = metrics(sy)
            loo[int(y)] = tot - (cy - c0)          # phan edge nam y dong gop
        share = {y: (v / tot if tot else np.nan) for y, v in loo.items()}
        ymax = max(share, key=lambda k: share[k])
        # LOO theo SU KIEN — bai hoc p3 (bus 2026-08-03T09:03): LOO theo NAM tren chuoi
        # compounding la AO ANH (bo 1 nam som lam mat ca phan lai kep ve sau). Khong phai
        # gate dang ky, nhung la chan doan DUNG hon — bao cao kem.
        looe = {}
        for _, e2 in ev.iterrows():
            se, _, _ = overlay(f, 0.140, 0.35, 0.02, drop_event=e2["event"])
            ce, _, _ = metrics(se)
            looe[str(e2["event"].date())] = tot - (ce - c0)
        shr_e = {k: (v / tot if tot else np.nan) for k, v in looe.items()}
        emax = max(shr_e, key=lambda k: shr_e[k])
        ok = (d_is > 0 and d_oos > 0 and d_dd <= 1.0 and nc == 0
              and share[ymax] < 0.50)
        res[f] = ok
        P(f"  f={f:.2f}: dCAGR_IS {d_is:+.2%} ({'PASS' if d_is>0 else 'FAIL'}) | "
          f"dCAGR_OOS {d_oos:+.2%} ({'PASS' if d_oos>0 else 'FAIL'}) | "
          f"dMaxDD xau di {d_dd:+.2f}pp ({'PASS' if d_dd<=1.0 else 'FAIL'}) | "
          f"#call {nc} ({'PASS' if nc==0 else 'FAIL'})")
        P(f"         LOO nam gong nhat: {ymax} = {share[ymax]:.1%} tong edge "
          f"({'PASS' if share[ymax]<0.5 else 'FAIL'})  | dCAGR toan ky {tot:+.2%}")
        P(f"         LOO nam day du: " + ", ".join(f"{y}:{v:+.1%}" for y, v in share.items()))
        P(f"         LOO SU KIEN (chan doan dung hon, bai hoc p3) — gong nhat: "
          f"{emax} = {shr_e[emax]:.1%} tong edge")
        P(f"         LOO su kien day du: "
          + ", ".join(f"{k[5:]}:{v:+.0%}" for k, v in shr_e.items()))
        P(f"         --> f={f:.2f} {'PASS G-C' if ok else 'FAIL G-C'}")
        P("")

    surv = [f for f, o in res.items() if o]
    P(f"  f song sot qua G-C: {surv}")
    P(f"  >>> GATE G-C: {'PASS' if surv else 'FAIL -> NO-GO'}")
    P("")
    P("TRAN KY VONG §2.2 (guard #10): dCAGR toan-so > +2,1pp/nam => TU DONG NGHI VAN.")
    for f in F_GRID[1:]:
        s, _, _ = overlay(f, 0.140, 0.35, 0.02)
        cg, _, _ = metrics(s)
        flag = "VUOT TRAN - PHAI AUDIT" if (cg - c0) * 100 > 2.1 else "trong tran"
        P(f"  f={f:.2f}: dCAGR = {(cg-c0)*100:+.2f}pp/nam  -> {flag}")

    # ------------------------------------------------ guard #6 (§4): tuong quan sleeve vs ca so
    P("")
    P("-" * 96)
    P("CHAN DOAN guard #6 (§4) — trong 10 ngay MAE SAU NHAT cua sleeve, NAV_L0 doi bao nhieu?")
    P("(neu ca so cung sut manh cung luc => equity tong giam nhanh hon phep do sleeve-alone)")
    P("-" * 96)
    P(f"{'su kien':>12}{'sleeve MAE':>12}{'NAV_L0 cung ky':>16}{'NAV_L0 min/entry':>18}")
    rows = []
    for _, e in ev.iterrows():
        p = paths[paths["event"] == e["event"]].sort_values("t")
        nv = p["nav"].to_numpy(float); tt = p["time"].to_numpy()
        worst = np.argsort(nv)[:10]                        # 10 ngay sleeve te nhat
        idx = nav0.index.get_indexer(pd.DatetimeIndex(tt))
        b = nav0.to_numpy()[idx]
        rows.append((float(nv.min() - 1), float(b[worst].mean() / b[0] - 1),
                     float(b.min() / b[0] - 1)))
        P(f"{str(e['event'].date()):>12}{nv.min()-1:>+12.2%}"
          f"{b[worst].mean()/b[0]-1:>+16.2%}{b.min()/b[0]-1:>+18.2%}")
    a = np.array(rows)
    P(f"{'TRUNG BINH':>12}{a[:,0].mean():>+12.2%}{a[:,1].mean():>+16.2%}{a[:,2].mean():>+18.2%}")
    P(f"  tuong quan(sleeve MAE, NAV_L0 min) = {np.corrcoef(a[:,0], a[:,2])[0,1]:+.3f}")

    txt = "\n".join(lines)
    print(txt)
    (HERE / "step_c_wholebook.log").write_text(txt + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
