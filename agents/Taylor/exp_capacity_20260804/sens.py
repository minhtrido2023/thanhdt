"""Do NHAY cua duong cong capacity theo TRAN FILL (LIQ_PCT). Job Taylor_20260804_102015 (attempt 2).

LY DO: quant-skeptic CONFIRMED bao cao goc nhung neu killer_objection + recommended_reruns —
toan bo duong cong treo tren tran 20% ADV/phien, trong khi fill THAT cua DNSE moi xac nhan toi
~3,86%/phien va 90-96% phien-fill mo phong dang nam O TRAN. Chay lai chan THAT o LIQ_PCT=0.04
(neo theo fill that, trong khoang 0.04-0.06 quant-skeptic de xuat) tai 1B/10B/50B.

Chan LY TUONG (LIQ_UNCAP=1, cap=None) KHONG bi anh huong boi LIQ_PCT => dung lai 3 chan ideal
da co, khong can chay lai.

CANH BAO ke thua: knob LIQ_PCT ban dau duoc KHAI BAO nhung KHONG AP vao LIQ_FULL/LIQ_LAG (van
hardcode 0.20) => chan `_liqpct0p04` se trung byte voi chan 20% ma van mang ten khac. Da wire +
them assert o pt_v23_capacity.py; cong [CAPACITY] in ra `BAL cap=0.04 | LAG cap=0.04` xac nhan.
"""
import os

import numpy as np
import pandas as pd

from collect import exec_facts, is_oos, metrics

EXP = os.path.dirname(os.path.abspath(__file__))
PCT_TAG = "_liqpct0p04"
NAVS = [1, 5, 10, 20, 30, 50, 75, 100]


def row(tag, nav, label):
    m = metrics(tag)
    if m is None:
        return dict(nav=nav, leg=label, status="THIEU LOG")
    e = exec_facts(tag)
    i, o = is_oos(tag)
    r = dict(nav=nav, leg=label, status="OK", cagr=m["cagr"], sharpe=m["sharpe"],
             maxdd=m["maxdd"], calmar=m["calmar"], final_b=m["final_nav_b"],
             is_cagr=i, oos_cagr=o, sc0=m["selfcheck0"], exit0=m["exit0"], gate=m["gate"],
             annual=m["annual"])
    for sl in ("BAL", "LAG", "CAPIT", "TONG"):
        if sl in e:
            r[f"ab_{sl}"] = e[sl]["aband_pct"]
            r[f"op_{sl}"] = e[sl]["opened"]
    return r


def main():
    rows = []
    for nav in NAVS:
        rows.append(row(f"cap{nav}b_real", nav, "real@20%"))
        rows.append(row(f"cap{nav}b_real{PCT_TAG}", nav, "real@4%"))
        rows.append(row(f"cap{nav}b_ideal", nav, "ideal"))
    df = pd.DataFrame(rows)
    df.drop(columns=["annual"]).to_csv(os.path.join(EXP, "sens_liqpct_raw.csv"), index=False)

    def get(nav, leg, col):
        s = df[(df.nav == nav) & (df.leg == leg)]
        if s.empty or s.iloc[0]["status"] != "OK":
            return np.nan
        return s.iloc[0][col]

    print("=" * 118)
    print("BANG S1 — DO NHAY THEO TRAN FILL: chan THAT o 20% ADV/phien (chua neo) vs 4% (neo theo fill THAT DNSE ~3,86%)")
    print("=" * 118)
    print(f"{'NAV_B':>6s} | {'CAGR@20%':>9s} {'CAGR@4%':>9s} {'delta pp':>9s} | "
          f"{'Calmar@20%':>10s} {'Calmar@4%':>10s} | {'MaxDD@20%':>9s} {'MaxDD@4%':>9s} | {'sc0@4%':>7s}")
    for nav in NAVS:
        c20, c4 = get(nav, "real@20%", "cagr"), get(nav, "real@4%", "cagr")
        print(f"{nav:6d} | {c20:8.2f}% {c4:8.2f}% {c4 - c20:+9.2f} | "
              f"{get(nav,'real@20%','calmar'):10.2f} {get(nav,'real@4%','calmar'):10.2f} | "
              f"{get(nav,'real@20%','maxdd'):8.1f}% {get(nav,'real@4%','maxdd'):8.1f}% | "
              f"{'OK' if get(nav,'real@4%','sc0') else 'FAIL':>7s}")

    print("\n" + "=" * 118)
    print("BANG S2 — KET LUAN DINH TINH CO SONG SOT KHONG? do lech (ly tuong - that) o CA HAI tran")
    print("  (ket luan goc: chan LY TUONG THAP HON chan that o moi moc => tran fill = BO LOC CHON MA co loi)")
    print("=" * 118)
    print(f"{'NAV_B':>6s} | {'ideal':>8s} | {'that@20%':>9s} {'lech@20%':>9s} | "
          f"{'that@4%':>9s} {'lech@4%':>9s} | {'dau giu nguyen?':>16s}")
    for nav in NAVS:
        idl = get(nav, "ideal", "cagr")
        c20, c4 = get(nav, "real@20%", "cagr"), get(nav, "real@4%", "cagr")
        g20, g4 = idl - c20, idl - c4
        same = "CO" if (np.sign(g20) == np.sign(g4)) else "KHONG"
        print(f"{nav:6d} | {idl:7.2f}% | {c20:8.2f}% {g20:+9.2f} | {c4:8.2f}% {g4:+9.2f} | {same:>16s}")

    print("\n" + "=" * 118)
    print("BANG S3 — %VI THE BO DO tach theo so, chan THAT @4% ADV/phien (so voi @20% trong ngoac)")
    print("=" * 118)
    print(f"{'NAV_B':>6s} | {'BAL %bo':>16s} | {'LAG %bo':>16s} | {'CAPIT %bo':>16s} | {'TONG %bo':>16s}")
    for nav in NAVS:
        cells = []
        for sl in ("BAL", "LAG", "CAPIT", "TONG"):
            a4, a20 = get(nav, "real@4%", f"ab_{sl}"), get(nav, "real@20%", f"ab_{sl}")
            cells.append(f"{a4:5.1f}% ({a20:4.1f}%)")
        print(f"{nav:6d} | " + " | ".join(f"{c:>16s}" for c in cells))

    print("\n" + "=" * 118)
    print("BANG S4 — CONG CHONG NO-OP + self-check moi chan (gate PHAI in dung tran dang chay)")
    print("=" * 118)
    for _, r in df.iterrows():
        if r["status"] != "OK":
            print(f"  NAV={r['nav']:>3}B {r['leg']:>9s}: {r['status']}"); continue
        print(f"  NAV={r['nav']:>3}B {r['leg']:>9s}: gate={r['gate']} "
              f"selfcheck_0VND={'OK' if r['sc0'] else 'FAIL'} exit0={r['exit0']}")

    # Per-year: cai sut giam 10B->50B o tran 4% co ben khong, hay lai la reshuffle-luck?
    print("\n" + "=" * 118)
    print("BANG S5 — PER-YEAR: chenh lech nam (50B - 10B) o TUNG tran. Dem so nam cung dau.")
    print("=" * 118)
    for leg in ("real@20%", "real@4%", "ideal"):
        a10 = df[(df.nav == 10) & (df.leg == leg)]
        a50 = df[(df.nav == 50) & (df.leg == leg)]
        if a10.empty or a50.empty or a10.iloc[0]["status"] != "OK" or a50.iloc[0]["status"] != "OK":
            continue
        d10, d50 = a10.iloc[0]["annual"], a50.iloc[0]["annual"]
        yrs = sorted(set(d10) & set(d50))
        diffs = {y: d50[y] - d10[y] for y in yrs}
        neg = sum(1 for v in diffs.values() if v < 0)
        print(f"  {leg:>9s}: {neg}/{len(yrs)} nam GIAM khi 10B->50B | "
              + " ".join(f"{y}:{v:+.1f}" for y, v in diffs.items()))


if __name__ == "__main__":
    main()
