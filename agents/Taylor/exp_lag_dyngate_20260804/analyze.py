"""Bang ket qua day du cho gate kha-thi-thi-hanh LAG — job Taylor_20260804_085248.

Trong tam (theo dispatch): HIEN VAT THI-HANH (vi the ket khong fill noi = ABANDONED_REFUND)
va MaxDD/Calmar; CAGR/Sharpe in day du nhung KHONG phai luan diem.
"""
import glob
import json
import os
import re

import numpy as np
import pandas as pd

EXP = os.path.dirname(os.path.abspath(__file__))
DATA = "/home/trido/thanhdt/WorkingClaude/data"


def csv_for(tag):
    g = glob.glob(os.path.join(DATA, f"*_exp_{tag}_univpit*.csv"))
    return g[0] if g else None


def metrics(tag):
    txt = open(os.path.join(EXP, tag + ".log"), encoding="utf-8", errors="replace").read()
    m = re.search(r"Final NAV ([\d,\.]+)B\s+CAGR ([\d\.\-]+)%\s+Sharpe\(252\) ([\d\.\-]+)\s+"
                  r"MaxDD ([\d\.\-]+)%\s+Calmar ([\d\.\-]+)", txt)
    if m is None:
        return None
    d = dict(tag=tag, final_nav_b=float(m.group(1).replace(",", "")), cagr=float(m.group(2)),
             sharpe=float(m.group(3)), maxdd=float(m.group(4)), calmar=float(m.group(5)))
    d["annual"] = {int(y): float(v) for y, v in
                   re.findall(r"^\s{2}(\d{4}): ([\+\-][\d\.]+)%", txt, re.M)}
    mm = re.search(r"\[DYNGATE\] K=([\d\.]+) dropped_entries=(\d+) distinct_tickers=(\d+)", txt)
    d["gate_drops_raw"] = int(mm.group(2)) if mm else 0
    d["selfcheck0"] = txt.count("identity err = 0 VND") >= 2
    d["exit0"] = "EXIT=0" in txt
    return d


def exec_facts(tag):
    p = csv_for(tag)
    if not p:
        return {}
    d = pd.read_csv(p, low_memory=False)
    lag = d[(d["book"] == "LAG") & (d["play_type"].astype(str).str.startswith("LAG_"))]
    buys = lag[lag["action"] == "buy"]
    ab = lag[lag["reason"] == "ABANDONED_REFUND"]
    ok = lag[(lag["action"] == "sell") & (lag["reason"] != "ABANDONED_REFUND")]
    opened = buys["holding_id"].nunique()
    nab = ab["holding_id"].nunique()
    return {"opened": int(opened), "abandoned": int(nab),
            "aband_pct": round(100.0 * nab / opened, 1) if opened else np.nan,
            "completed": int(ok["holding_id"].nunique()),
            "tickers": int(buys["ticker"].nunique()),
            "capital_deployed_b": round(float(buys["buy_amount"].sum()) / 1e9, 1),
            "capital_stuck_b": round(float(ab["sell_amount"].sum()) / 1e9, 1)}


def nav_series(tag):
    p = csv_for(tag)
    d = pd.read_csv(p, low_memory=False)
    n = d[d["combined_nav"].notna()][["ymd", "combined_nav"]].copy()
    n["ymd"] = pd.to_datetime(n["ymd"])
    return n.set_index("ymd")["combined_nav"].astype(float).sort_index()


LEGS_50 = [("ctrl (production, pin R3)", "n50_ctrl"), ("L1 (LIQ_ZERO_BLOCK=lag)", "n50_L1ctrl"),
           ("K=1,00  f=20%/N=5", "n50_K1_00"), ("K=2,59  f=3,86%/N=10", "n50_K2_59"),
           ("K=5,18  f=3,86%/N=5", "n50_K5_18"), ("K=12,95 f=3,86%/N=2", "n50_K12_95"),
           ("K=44,4  f=0,45%/N=5", "n50_K44_4")]
LEGS_1 = [("ctrl (production)", "n1_ctrl"), ("L1 (LIQ_ZERO_BLOCK=lag)", "n1_L1ctrl"),
          ("K=1,00", "n1_K1_00"), ("K=5,18", "n1_K5_18"), ("K=44,4", "n1_K44_4")]


def table(legs, title):
    print(f"\n{'='*118}\n{title}\n{'='*118}")
    hdr = (f"{'chan':28s} {'CAGR':>7s} {'Sharpe':>7s} {'MaxDD':>7s} {'Calmar':>7s} "
           f"{'NAV_B':>9s} | {'mo':>5s} {'bo do':>6s} {'%bo':>6s} {'xong':>5s} {'ma':>4s} "
           f"{'vonB':>8s} {'ketB':>7s} | {'sc0':>4s}")
    print(hdr)
    rows = []
    for lbl, tag in legs:
        if not os.path.exists(os.path.join(EXP, tag + ".log")):
            print(f"{lbl:28s}  (chua co)")
            continue
        m = metrics(tag)
        if m is None:
            print(f"{lbl:28s}  (dang chay)"); continue
        e = exec_facts(tag)
        rows.append((lbl, m, e))
        print(f"{lbl:28s} {m['cagr']:6.2f}% {m['sharpe']:7.2f} {m['maxdd']:6.1f}% "
              f"{m['calmar']:7.2f} {m['final_nav_b']:9.2f} | {e.get('opened',0):5d} "
              f"{e.get('abandoned',0):6d} {e.get('aband_pct',0):5.1f}% {e.get('completed',0):5d} "
              f"{e.get('tickers',0):4d} {e.get('capital_deployed_b',0):8.1f} "
              f"{e.get('capital_stuck_b',0):7.1f} | {'OK' if m['selfcheck0'] else 'FAIL':>4s}")
    return rows


def per_year(legs, base_tag):
    print(f"\n--- Δpp theo nam vs {base_tag} (LOO / doi dau) ---")
    b = metrics(base_tag)["annual"]
    print(f"{'nam':6s}" + "".join(f"{t[1][4:]:>12s}" for t in legs if t[1] != base_tag))
    for y in sorted(b):
        line = f"{y:6d}"
        for _, tag in legs:
            if tag == base_tag or not os.path.exists(os.path.join(EXP, tag + ".log")):
                continue
            _mt = metrics(tag)
            a = _mt["annual"].get(y) if _mt else None
            line += f"{(a - b[y]):+12.2f}" if a is not None else f"{'—':>12s}"
        print(line)


if __name__ == "__main__":
    table(LEGS_50, "THANG NAV = 50 ty (so sanh apple-to-apple voi job truoc Taylor_20260804_080547)")
    table(LEGS_1, "THANG NAV = 1 ty (~ active_nav THAT dang chay live: SpaceX ~950tr, ZaloPay tuong tu)")
    per_year(LEGS_50, "n50_ctrl")
    per_year(LEGS_1, "n1_ctrl")

    # required_ADV theo nam — bang chung gate ti-le-NAV that chat dan theo compounding
    print("\n--- required_ADV trung vi theo nam (chan n50_K5_18) vs (chan n1_K5_18), ty VND ---")
    for tag in ("n50_K5_18", "n1_K5_18"):
        p = os.path.join(EXP, f"drops_{tag}.json")
        if not os.path.exists(p):
            continue
        dd = pd.DataFrame(json.load(open(p)))
        dd["year"] = pd.to_datetime(dd["date"]).dt.year
        g = dd.groupby("year")[["required_adv_vnd", "slot_vnd", "adv_vnd"]].median() / 1e9
        print(f"\n[{tag}]")
        print(g.round(2).to_string())
