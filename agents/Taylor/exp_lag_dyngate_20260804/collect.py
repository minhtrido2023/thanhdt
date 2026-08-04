"""Gom ket qua moi chan: metric tu log + hien vat thi-hanh tu CSV audit.

Trong tam bao cao (dispatch job Taylor_20260804_085248): so vi the KET-KHONG-FILL-NOI
(ABANDONED_REFUND) giam bao nhieu — KHONG phai CAGR. Nhung van in day du CAGR/Sharpe/
MaxDD/Calmar/IS/OOS nhu thuong le.
"""
import glob
import json
import os
import re
import sys

import pandas as pd

EXP = os.path.dirname(os.path.abspath(__file__))
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
CSV_FMT = (WORKDIR + "/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_"
           "etfliqcustompitg_wtnamecap_advprice{lz}_exp_{tag}_univpit.csv")


def metrics_from_log(tag):
    p = os.path.join(EXP, tag + ".log")
    txt = open(p, encoding="utf-8", errors="replace").read()
    out = {"tag": tag}
    m = re.search(r"Final NAV ([\d,\.]+)B\s+CAGR ([\d\.\-]+)%\s+Sharpe\(252\) ([\d\.\-]+)\s+"
                  r"MaxDD ([\d\.\-]+)%\s+Calmar ([\d\.\-]+)", txt)
    if m:
        out.update(final_nav_b=float(m.group(1).replace(",", "")), cagr=float(m.group(2)),
                   sharpe=float(m.group(3)), maxdd=float(m.group(4)), calmar=float(m.group(5)))
    for lbl, pat in (("is_cagr", r"IS\s+2014-2019.*?CAGR\s+([\d\.\-]+)%"),
                     ("oos_cagr", r"OOS\s+2020-.*?CAGR\s+([\d\.\-]+)%")):
        mm = re.search(pat, txt)
        if mm:
            out[lbl] = float(mm.group(1))
    mm = re.search(r"\[DYNGATE\] K=([\d\.]+) dropped_entries=(\d+) distinct_tickers=(\d+)", txt)
    out["gate_drops"] = int(mm.group(2)) if mm else 0
    out["gate_drop_tickers"] = int(mm.group(3)) if mm else 0
    out["annual"] = {int(y): float(v) for y, v in
                     re.findall(r"^\s{2}(\d{4}): ([\+\-][\d\.]+)%", txt, re.M)}
    out["exit_ok"] = "EXIT=0" in txt
    out["selfcheck_ok"] = txt.count("= 0 VND") >= 2 or txt.count("0 VND") >= 2
    return out


def exec_facts(tag, lz):
    """Hien vat thi-hanh cua book LAG: bao nhieu vi the mo, bao nhieu bo do khong fill noi."""
    p = CSV_FMT.format(lz=("_liqzblag" if lz else ""), tag=tag)
    if not os.path.exists(p):
        return {"csv": None}
    d = pd.read_csv(p, low_memory=False)
    tx = d[d["record_type"] == "tx"] if "tx" in set(d["record_type"].astype(str)) else d
    lag = tx[(tx["book"] == "LAG") & (tx["play_type"].astype(str).str.startswith("LAG_"))]
    buys = lag[lag["action"] == "buy"]
    aband = lag[lag["reason"] == "ABANDONED_REFUND"]
    sells = lag[(lag["action"] == "sell") & (lag["reason"] != "ABANDONED_REFUND")]
    return {"csv": os.path.basename(p),
            "lag_positions_opened": int(buys["holding_id"].nunique()),
            "lag_abandoned": int(aband["holding_id"].nunique()),
            "lag_completed": int(sells["holding_id"].nunique()),
            "lag_buy_vnd": float(buys["buy_amount"].sum()),
            "lag_aband_vnd": float(aband["sell_amount"].sum()),
            "lag_tickers": int(buys["ticker"].nunique())}


if __name__ == "__main__":
    rows = []
    for spec in sys.argv[1:]:
        tag, lz = (spec.split(":") + ["0"])[:2]
        r = metrics_from_log(tag)
        r.update(exec_facts(tag, lz == "1"))
        rows.append(r)
    print(json.dumps(rows, ensure_ascii=False, indent=1, default=str))
