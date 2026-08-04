"""Duong cong CAPACITY theo NAV — thu thap + bang ket qua. Job Taylor_20260804_102015.

Moi moc NAV co 2 chan:
  real  = production (tran fill 20% ADV/phien, max_fill_days=5, min_fill_pct=0.30)
  ideal = LIQ_UNCAP=1 (go tran fill o tang vao lenh, moi thu khac giu nguyen)
Hieu so (ideal - real) CO LAP dung co che tran fill vao lenh.

Dinh nghia "%bo do" GIU NGUYEN cua job truoc (Taylor_20260804_085248, analyze.py) de so sanh
duoc: opened = so holding_id co dong buy; abandoned = so holding_id co dong ABANDONED_REFUND.
CANH BAO da biet: lenh KHONG khop noi 1 dong nao (filled_shares==0) KHONG sinh dong log nao
=> %bo do la CAN DUOI cua ty le that.
"""
import glob
import os
import re

import numpy as np
import pandas as pd

EXP = os.path.dirname(os.path.abspath(__file__))
DATA = "/home/trido/thanhdt/WorkingClaude/data"
NAVS = [1, 5, 10, 20, 30, 50, 75, 100]
IS_END = pd.Timestamp("2019-12-31")      # walk-forward IS 2014-19 / OOS 2020+


def tag_of(nav, leg):
    return f"cap{nav}b_{leg}"


def csv_for(tag):
    g = glob.glob(os.path.join(DATA, f"*_exp_{tag}_univpit*.csv"))
    return g[0] if g else None


def metrics(tag):
    p = os.path.join(EXP, tag + ".log")
    if not os.path.exists(p):
        return None
    txt = open(p, encoding="utf-8", errors="replace").read()
    m = re.search(r"Final NAV ([\d,\.]+)B\s+CAGR ([\d\.\-]+)%\s+Sharpe\(252\) ([\d\.\-]+)\s+"
                  r"MaxDD ([\d\.\-]+)%\s+Calmar ([\d\.\-]+)", txt)
    if m is None:
        return None
    d = dict(tag=tag, final_nav_b=float(m.group(1).replace(",", "")), cagr=float(m.group(2)),
             sharpe=float(m.group(3)), maxdd=float(m.group(4)), calmar=float(m.group(5)))
    d["annual"] = {int(y): float(v) for y, v in
                   re.findall(r"^\s{2}(\d{4}): ([\+\-][\d\.]+)%", txt, re.M)}
    # cong chong no-op: dong [CAPACITY] phai khop chan
    # `LIQ_PCT=` la truong THEM SAU (attempt-2) => de tuy chon, 16 log goc van parse duoc.
    g = re.search(r"\[CAPACITY\] LIQ_UNCAP=(\w+) \|(?: LIQ_PCT=\S+ \|)? BAL cap=(\S+) \| "
                  r"LAG cap=(\S+) \| NAV_TOTAL_B=(\S+)", txt)
    d["gate"] = g.groups() if g else None
    d["selfcheck0"] = txt.count("identity err = 0 VND") >= 2
    d["exit0"] = "EXIT=0" in txt
    return d


def nav_series(tag):
    p = csv_for(tag)
    if not p:
        return None
    d = pd.read_csv(p, low_memory=False)
    n = d[d["combined_nav"].notna()][["ymd", "combined_nav"]].copy()
    n["ymd"] = pd.to_datetime(n["ymd"])
    return n.set_index("ymd")["combined_nav"].astype(float).sort_index()


def cagr(s):
    if s is None or len(s) < 2:
        return np.nan
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    return (float(s.iloc[-1]) / float(s.iloc[0])) ** (1 / yrs) * 100 - 100


def is_oos(tag):
    s = nav_series(tag)
    if s is None:
        return (np.nan, np.nan)
    return (cagr(s[s.index <= IS_END]), cagr(s[s.index >= pd.Timestamp("2020-01-01")]))


SLEEVES = {
    "BAL": lambda d: (d["book"] == "BAL") & (~d["pt"].str.startswith("CAPIT")) & (d["pt"] != "ETF_PARK"),
    "LAG": lambda d: (d["book"] == "LAG") & (d["pt"].str.startswith("LAG_")),
    "CAPIT": lambda d: d["pt"].str.startswith("CAPIT"),
}


def exec_facts(tag):
    """Hien vat thi-hanh tach theo so. Tra ve dict {sleeve: {...}} + tong."""
    p = csv_for(tag)
    if not p:
        return {}
    d = pd.read_csv(p, low_memory=False)
    d = d[d["reason"].notna()].copy()
    d["pt"] = d["play_type"].astype(str)
    out = {}
    for name, pred in SLEEVES.items():
        s = d[pred(d)]
        buys = s[s["action"] == "buy"]
        ab = s[s["reason"] == "ABANDONED_REFUND"]
        opened = buys["holding_id"].nunique()
        nab = ab["holding_id"].nunique()
        out[name] = {
            "opened": int(opened), "abandoned": int(nab),
            "aband_pct": (100.0 * nab / opened) if opened else np.nan,
            "deployed_b": float(buys["buy_amount"].sum()) / 1e9,
            "stuck_b": float(ab["sell_amount"].sum()) / 1e9,
            "stuck_pct_of_deployed": (100.0 * float(ab["sell_amount"].sum()) /
                                      float(buys["buy_amount"].sum())) if len(buys) and buys["buy_amount"].sum() else np.nan,
        }
    tot_o = sum(v["opened"] for v in out.values())
    tot_a = sum(v["abandoned"] for v in out.values())
    out["TONG"] = {"opened": tot_o, "abandoned": tot_a,
                   "aband_pct": (100.0 * tot_a / tot_o) if tot_o else np.nan,
                   "deployed_b": sum(v["deployed_b"] for v in out.values()),
                   "stuck_b": sum(v["stuck_b"] for v in out.values()),
                   "stuck_pct_of_deployed": np.nan}
    return out


def main():
    rows = []
    for nav in NAVS:
        for leg in ("real", "ideal"):
            t = tag_of(nav, leg)
            m = metrics(t)
            if m is None:
                rows.append(dict(nav=nav, leg=leg, status="chua xong"))
                continue
            e = exec_facts(t)
            i, o = is_oos(t)
            r = dict(nav=nav, leg=leg, status="OK", cagr=m["cagr"], sharpe=m["sharpe"],
                     maxdd=m["maxdd"], calmar=m["calmar"], final_b=m["final_nav_b"],
                     is_cagr=i, oos_cagr=o, sc0=m["selfcheck0"], exit0=m["exit0"],
                     gate=m["gate"])
            for sl in ("BAL", "LAG", "CAPIT", "TONG"):
                if sl in e:
                    r[f"ab_{sl}"] = e[sl]["aband_pct"]
                    r[f"op_{sl}"] = e[sl]["opened"]
                    r[f"stuck_{sl}"] = e[sl]["stuck_b"]
            rows.append(r)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(EXP, "capacity_curve_raw.csv"), index=False)

    print("=" * 132)
    print("BANG 1 — DUONG CONG CAPACITY: CAGR THAT (real) vs LY TUONG (ideal, go tran fill vao lenh)")
    print("=" * 132)
    print(f"{'NAV_B':>6s} | {'CAGR that':>9s} {'CAGR ly tuong':>13s} {'do lech pp':>10s} | "
          f"{'Sharpe':>6s} {'MaxDD':>7s} {'Calmar':>6s} | {'IS that':>8s} {'OOS that':>8s} | "
          f"{'%bo do TONG':>11s} | {'sc0':>4s}")
    for nav in NAVS:
        r = df[(df.nav == nav) & (df.leg == "real")]
        v = df[(df.nav == nav) & (df.leg == "ideal")]
        if r.empty or r.iloc[0]["status"] != "OK":
            print(f"{nav:6d} | (chua xong)"); continue
        r = r.iloc[0]
        idl = v.iloc[0]["cagr"] if (not v.empty and v.iloc[0]["status"] == "OK") else np.nan
        gap = (idl - r["cagr"]) if not pd.isna(idl) else np.nan
        print(f"{nav:6d} | {r['cagr']:8.2f}% {idl if not pd.isna(idl) else float('nan'):12.2f}% "
              f"{gap:+10.2f} | {r['sharpe']:6.2f} {r['maxdd']:6.1f}% {r['calmar']:6.2f} | "
              f"{r['is_cagr']:7.2f}% {r['oos_cagr']:7.2f}% | {r.get('ab_TONG', np.nan):10.1f}% | "
              f"{'OK' if r['sc0'] else 'FAIL':>4s}")

    print("\n" + "=" * 132)
    print("BANG 2 — %VI THE BO DO (ABANDONED_REFUND) TACH THEO SO, chan THAT")
    print("=" * 132)
    print(f"{'NAV_B':>6s} | {'BAL mo':>7s} {'BAL %bo':>8s} | {'LAG mo':>7s} {'LAG %bo':>8s} | "
          f"{'CAPIT mo':>8s} {'CAPIT %bo':>9s} | {'von ket B (BAL/LAG/CAPIT)':>30s}")
    for nav in NAVS:
        r = df[(df.nav == nav) & (df.leg == "real")]
        if r.empty or r.iloc[0]["status"] != "OK":
            print(f"{nav:6d} | (chua xong)"); continue
        r = r.iloc[0]
        print(f"{nav:6d} | {r.get('op_BAL',0):7.0f} {r.get('ab_BAL',np.nan):7.1f}% | "
              f"{r.get('op_LAG',0):7.0f} {r.get('ab_LAG',np.nan):7.1f}% | "
              f"{r.get('op_CAPIT',0):8.0f} {r.get('ab_CAPIT',np.nan):8.1f}% | "
              f"{r.get('stuck_BAL',0):9.1f} {r.get('stuck_LAG',0):9.1f} {r.get('stuck_CAPIT',0):9.1f}")

    print("\n" + "=" * 132)
    print("BANG 3 — CONG CHONG NO-OP ([CAPACITY] tu chinh lan chay) + self-check")
    print("=" * 132)
    for _, r in df.iterrows():
        if r["status"] != "OK":
            print(f"  NAV={r['nav']:>3}B {r['leg']:>5s}: {r['status']}"); continue
        print(f"  NAV={r['nav']:>3}B {r['leg']:>5s}: gate={r['gate']} "
              f"selfcheck_0VND={'OK' if r['sc0'] else 'FAIL'} exit0={r['exit0']}")


if __name__ == "__main__":
    main()
