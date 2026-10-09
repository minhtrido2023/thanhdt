#!/usr/bin/env python3
"""analyze.py — chấm kết quả replay (đọc runs/<SCENARIO>_d<depth>/ state_*.json + shadow_*.jsonl).

Không dùng cột profit_*. Giá tương lai lấy từ BQ daily: P_k = Price(D) × Close_adj(D+k)/Close_adj(D)
(D = ngày T0; giá thô ngày D, điều chỉnh corp-action theo Close_adj). Lợi ích cutloss so với GIỮ:
  exit_net = giá bán TB mô phỏng × (1 − 0,097% bán − 0,097% tái phân bổ/mua lại − impact)
  impact   = 0,5 × σ20 × √(KL bán / ADV20)   (σ20 = độ lệch chuẩn lợi suất ngày 20 phiên trước D)
  B_k (% giá trị vị thế theo TC) = (sold/qty) × (exit_net − P_k)/TC
  "bán oan" tại k = P_k > giá bán TB (gross) — bán rồi giá hồi lên trên giá đã bán.
N độc lập = số NGÀY có sự kiện (các ca cùng ngày tương quan) — CI bootstrap theo cụm ngày.
"""
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
C = os.path.join(HERE, "cache")
FEE = 0.00097
HOR = (0, 1, 5, 20)

DAILY = pd.read_parquet(os.path.join(C, "daily.parquet"))
DAILY["d"] = DAILY.time.dt.date
PX = {t: g.set_index("d").sort_index() for t, g in DAILY.groupby("ticker")}
VNI = PX["VNINDEX"]
TD = list(VNI.index)


def fut(tk, d, k):
    """Giá thô quy về ngày d của phiên D+k (k=0: đóng cửa D)."""
    p = PX.get(tk)
    if p is None or d not in p.index or d not in TD:
        return np.nan
    i = TD.index(d) + k
    if i >= len(TD):
        return np.nan
    dk = TD[i]
    if dk not in p.index:
        return np.nan
    return float(p.loc[d, "Price"] * p.loc[dk, "Close"] / p.loc[d, "Close"])


def vni_fut(d, k):
    i = TD.index(d) + k
    return float(VNI.loc[TD[i], "Close"] / VNI.loc[d, "Close"] - 1) if i < len(TD) else np.nan


def risk(tk, d):
    p = PX.get(tk)
    if p is None or d not in p.index:
        return np.nan, np.nan
    h = p[p.index < d].tail(21)
    r = h.Close.pct_change().dropna()
    return float(r.std()) if len(r) > 5 else np.nan, float(h.Volume.tail(20).mean()) if len(h) else np.nan


def read_run(run):
    ev = []
    for f in sorted(glob.glob(os.path.join(run, "shadow_*.jsonl"))):
        for line in open(f):
            ev.append(json.loads(line))
    cases = {}
    for f in sorted(glob.glob(os.path.join(run, "state_*.json"))):
        st = json.load(open(f))
        for tk, c in (st.get("cases") or {}).items():
            cases[(c["t0"], tk)] = c            # bản muộn nhất (carryover ghi đè)
    return ev, cases


def triggers(ev):
    rows = []
    scan_vni = {}
    for r in ev:
        if r["kind"] == "SCAN":
            scan_vni[r["ts"]] = r.get("vni")
    for r in ev:
        if r["kind"] != "TRIGGER":
            continue
        tr = r["trigger"]
        for lab, h in (r.get("holdings") or {}).items():
            rows.append({"t0": r["ts"], "day": r["ts"][:10], "ticker": r["ticker"], "account": lab,
                         "book": h.get("book"), "qty": h.get("qty"), "no_auto_sell": h.get("no_auto_sell"),
                         "last": r["quote"].get("last"), "ref": r["quote"].get("ref"),
                         "floor": r["quote"].get("floor"), "exchange": r["quote"].get("exchange"),
                         "ret": tr["ret"], "idio": tr["idio"], "vni_ret": tr["vni_ret"], "at_floor": tr["at_floor"],
                         "late": r.get("late"), "reason": tr["reason"]})
        if not r.get("holdings"):
            rows.append({"t0": r["ts"], "day": r["ts"][:10], "ticker": r["ticker"], "account": None,
                         "book": "WATCH", "qty": 0, "last": r["quote"].get("last"), "ref": r["quote"].get("ref"),
                         "floor": r["quote"].get("floor"), "exchange": r["quote"].get("exchange"),
                         "ret": tr["ret"], "idio": tr["idio"], "vni_ret": tr["vni_ret"],
                         "at_floor": tr["at_floor"], "late": r.get("late"), "reason": tr["reason"]})
    return pd.DataFrame(rows)


def market_wide(ev):
    scans = {r["ts"]: r for r in ev if r["kind"] == "SCAN"}
    rows = []
    for r in ev:
        if r["kind"] == "MARKET_WIDE":
            v = (scans.get(r["ts"]) or {}).get("vni") or [None, None]
            rows.append({"ts": r["ts"], "day": r["ts"][:10], "reason": r["reason"], "n": len(r["tickers"]),
                         "tickers": ",".join(r["tickers"]), "new": ",".join(r["new"]),
                         "vni_ret": (v[0] / v[1] - 1) if v[0] and v[1] else None})
    return pd.DataFrame(rows)


def alt(ev):
    rows = []
    for r in ev:
        if r["kind"] == "ALT_THRESHOLD":
            for a in r["rows"]:
                rows.append({"ts": r["ts"], "day": r["ts"][:10], **a})
    return pd.DataFrame(rows)


def score_exec(cases, trig):
    rows = []
    for (t0, tk), c in cases.items():
        d = pd.Timestamp(t0[:10]).date()
        for lab, ex in (c.get("execution") or {}).items():
            h = c["holdings"][lab]
            sold, val = ex.get("sold", 0), ex.get("value", 0.0)
            ref = (c.get("t0_quote") or {}).get("ref")
            avg = val / sold if sold else np.nan
            sig, adv = risk(tk, d)
            imp = 0.5 * sig * np.sqrt(sold / adv) if sold and adv and sig == sig else 0.0
            net = avg * (1 - 2 * FEE - imp) if sold else np.nan
            row = {"t0": t0, "day": t0[:10], "ticker": tk, "account": lab, "book": h["book"], "qty": h["qty"],
                   "target": ex["target"], "sold": sold, "fill": sold / ex["target"] if ex["target"] else np.nan,
                   "avg": avg, "impact": imp, "exit_net": net, "ref": ref,
                   "t0_last": (c.get("t0_quote") or {}).get("last"), "status": ex.get("status"),
                   "modes": "/".join(str(m[1]) for m in ex.get("mode_history") or []),
                   "max_mode": max([m[1] for m in ex.get("mode_history") or []], default=0),
                   "started": ex.get("started_at"), "verdict": (c.get("verdict") or {}).get("label"),
                   "deferred": c.get("reply_deferred"), "compressed": c.get("compressed"),
                   "idio": c["trigger"]["idio"], "ret": c["trigger"]["ret"], "at_floor": c["trigger"]["at_floor"],
                   "vni_ret_t0": c["trigger"]["vni_ret"]}
            for k in HOR:
                pk = fut(tk, d, k)
                row[f"P{k}"] = pk
                row[f"B{k}"] = (sold / h["qty"]) * (net - pk) / ref if sold and ref else 0.0
                row[f"E{k}"] = net / pk - 1 if sold and pk == pk else np.nan
                row[f"oan{k}"] = bool(pk > avg) if sold and pk == pk else np.nan
                # tham chiếu: bán NGAY tại giá T0 (không có 20'+30' điều tra/chờ) — tách chi phí trễ quy trình
                t0p = row["t0_last"]
                row[f"Eideal{k}"] = t0p * (1 - 2 * FEE - imp) / pk - 1 if t0p and pk == pk else np.nan
            rows.append(row)
    return pd.DataFrame(rows)


def boot_ci(df, col, by="day", n=2000, seed=7):
    x = df[[by, col]].dropna()
    if x.empty:
        return (np.nan, np.nan)
    g = [v[col].values for _, v in x.groupby(by)]
    rng = np.random.default_rng(seed)
    m = []
    for _ in range(n):
        pick = rng.integers(0, len(g), len(g))
        m.append(np.mean(np.concatenate([g[i] for i in pick])))
    return tuple(np.percentile(m, [2.5, 97.5]))


def summarize(sc, col_prefix="E"):
    out = []
    for k in HOR:
        c = f"{col_prefix}{k}"
        x = sc[c].dropna()
        if x.empty:
            continue
        lo, hi = boot_ci(sc, c)
        out.append({"h": k, "n_cases": len(x), "n_days": sc.loc[x.index, "day"].nunique(),
                    "mean%": x.mean() * 100, "median%": x.median() * 100, "ci_lo%": lo * 100, "ci_hi%": hi * 100,
                    "win%": (x > 0).mean() * 100,
                    "ban_oan%": sc.loc[x.index, f"oan{k}"].mean() * 100 if f"oan{k}" in sc else np.nan})
    return pd.DataFrame(out)


def main():
    runs = sys.argv[1:] or sorted(glob.glob(os.path.join(HERE, "runs", "*_d*")))
    outd = os.path.join(HERE, "out")
    os.makedirs(outd, exist_ok=True)
    for run in runs:
        name = os.path.basename(run.rstrip("/"))
        ev, cases = read_run(run)
        tr = triggers(ev)
        tr.to_csv(os.path.join(outd, f"{name}_triggers.csv"), index=False)
        mw = market_wide(ev)
        mw.to_csv(os.path.join(outd, f"{name}_market_wide.csv"), index=False)
        al = alt(ev)
        al.to_csv(os.path.join(outd, f"{name}_alt.csv"), index=False)
        sc = score_exec(cases, tr)
        sc.to_csv(os.path.join(outd, f"{name}_exec.csv"), index=False)
        print(f"\n===== {name}: {len(tr)} trigger-rows ({tr.day.nunique() if len(tr) else 0} ngày), "
              f"{len(mw)} market-wide scans ({mw.day.nunique() if len(mw) else 0} ngày), exec rows {len(sc)}")
        if len(sc):
            s = summarize(sc)
            s.to_csv(os.path.join(outd, f"{name}_summary.csv"), index=False)
            print(s.round(2).to_string(index=False))
            print("ideal (bán ngay tại T0):")
            print(summarize(sc, "Eideal").round(2).to_string(index=False))


if __name__ == "__main__":
    main()
