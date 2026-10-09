#!/usr/bin/env python3
"""analyze_v2.py — chấm replay v2 theo PREREG.md. Tái dùng công thức chấm của analyze.py v1 (score_exec:
phí 0,097%×2 + impact 0,5·σ20·√(KL/ADV20); P_k = Price(D)·Close_adj(D+k)/Close_adj(D); không dùng profit_*).
Thêm: ADV20 (trung vị Price×Volume 20 phiên TRƯỚC D), cờ dữ liệu lỗi (P1==TC, Vol(D)/Vol(D+1)=0, quote cũ
>60' tại T0), lọc t0 theo khối của shard, bảng chính sách (B_k trên mọi ca kích hoạt, ca không bán = 0)."""
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(os.path.dirname(HERE), "intraday_cutloss_replay_20261009")
sys.path.insert(0, V1)
import analyze as A1  # noqa: E402

D = A1.DAILY.copy()
D["val"] = D.Price * D.Volume
D = D.sort_values(["ticker", "d"])
D["adv20"] = D.groupby("ticker").val.transform(lambda s: s.rolling(20, min_periods=10).median().shift(1))
ADV = {(t, d): v for t, d, v in zip(D.ticker, D.d, D.adv20)}
VOL = {(t, d): v for t, d, v in zip(D.ticker, D.d, D.Volume)}
TD = A1.TD


def nxt(d, k=1):
    i = TD.index(d) + k if d in TD else None
    return TD[i] if i is not None and i < len(TD) else None


def load_cfg(pattern):
    """→ (exec df, trigger-event rows, market-wide rows, relabel rows, cases dict) gộp mọi shard."""
    ex_all, trig, mw, rel, cases_all = [], [], [], [], {}
    for run in sorted(glob.glob(os.path.join(HERE, "runs", pattern))):
        bf = os.path.join(run, "block.txt")
        if not os.path.exists(bf):
            print("CHƯA XONG", run)
            continue
        block = {x.strip() for x in open(bf) if x.strip()}
        ev, cases = A1.read_run(run)
        cases = {k: v for k, v in cases.items() if k[0][:10] in block}
        cases_all.update(cases)
        for r in ev:
            if r["ts"][:10] not in block:
                continue
            if r["kind"] == "TRIGGER":
                q = r["quote"]
                trig.append({"t0": r["ts"], "day": r["ts"][:10], "ticker": r["ticker"], "held": bool(r.get("holdings")),
                             "bar_t": q.get("bar_t"), "ref": q.get("ref"), "last": q.get("last"),
                             "exchange": q.get("exchange"), **{k: r["trigger"].get(k) for k in
                                                               ("ret", "idio", "vni_ret", "at_floor")}})
            elif r["kind"] == "MARKET_WIDE":
                for tk in r["new"]:
                    mw.append({"ts": r["ts"], "day": r["ts"][:10], "ticker": tk, "reason": r["reason"],
                               "not_individual": (r.get("not_individual") or {}).get(tk)})
            elif r["kind"] == "MARKET_WIDE_RELABEL":
                for tk, v in r["cases"].items():
                    rel.append({"ts": r["ts"], "day": r["ts"][:10], "ticker": tk, "t0": v["t0"],
                                "reason": r["reason"], "note": "; ".join(v["note"])})
        sc = A1.score_exec(cases, None)
        if len(sc):
            sc["run"] = os.path.basename(run)
            ex_all.append(sc)
    ex = pd.concat(ex_all, ignore_index=True) if ex_all else pd.DataFrame()
    return ex, pd.DataFrame(trig), pd.DataFrame(mw), pd.DataFrame(rel), cases_all


def flags(df, trig=None):
    """Thêm adv20, bucket, giá<5k, cờ lỗi dữ liệu vào bảng có cột t0/day/ticker/ref/P1."""
    if df.empty:
        return df
    df = df.copy()
    d = pd.to_datetime(df.day).dt.date
    df["adv20"] = [ADV.get((t, x), np.nan) for t, x in zip(df.ticker, d)]
    df["adv_bucket"] = pd.cut(df.adv20, [-1, 1e9, 1e10, np.inf], labels=["<1 tỷ", "1-10 tỷ", ">=10 tỷ"], right=False)
    df["px_lt5k"] = df.ref < 5000
    df["g_p1_eq_ref"] = (df.P1 / df.ref - 1).abs() < 1e-6 if "P1" in df else False
    df["g_vol0"] = [(VOL.get((t, x), 0) or 0) == 0 or (VOL.get((t, nxt(x)), 0) or 0) == 0 for t, x in zip(df.ticker, d)]
    if trig is not None and len(trig):
        bt = {(r.t0, r.ticker): r.bar_t for r in trig.itertuples()}
        df["bar_t"] = [bt.get((a, b)) for a, b in zip(df.t0, df.ticker)]
        df["g_stale"] = [bool(b) and (pd.Timestamp(a) - pd.Timestamp(b)).total_seconds() > 3600 for a, b in
                         zip(df.t0, df.bar_t)]
    else:
        df["g_stale"] = False
    df["glitch"] = df.g_p1_eq_ref | df.g_vol0 | df.g_stale
    df["half"] = np.where(df.day < "2025-01-01", "2023-09..2024-12", "2025-01..2026-10")
    return df


def summ(sc, prefix="E", by=None):
    if sc.empty:
        return pd.DataFrame()
    if by is None:
        return A1.summarize(sc, prefix)
    out = []
    for k, g in sc.groupby(by, observed=True):
        s = A1.summarize(g, prefix)
        s.insert(0, by if isinstance(by, str) else "grp", str(k))
        out.append(s)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


def verdict(sc5):
    """Luật quyết định PREREG trên dòng h=5."""
    if sc5 is None or not len(sc5):
        return "INCONCLUSIVE (không có ca)"
    r = sc5.iloc[0]
    if r.n_days < 30:
        return f"INCONCLUSIVE (N ngày {r.n_days} < 30)"
    if r["ci_hi%"] < 0:
        return "REFUTED"
    if r["mean%"] < 0:
        return "NOT SUPPORTED"
    if r["ci_lo%"] > 0:
        return "SUPPORTED-STRONG"
    if r["ci_lo%"] > -1.0:
        return "SUPPORTED"
    return "INCONCLUSIVE (CI quá rộng)"


if __name__ == "__main__":
    pat = sys.argv[1]
    ex, tr, mw, rel, _ = load_cfg(pat)
    ex = flags(ex, tr)
    print(len(ex), "exec rows;", len(tr), "triggers;", len(mw), "mw;", len(rel), "relabel")
    print(summ(ex[~ex.glitch], by="adv_bucket").round(2).to_string(index=False))
