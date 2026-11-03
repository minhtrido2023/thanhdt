#!/usr/bin/env python3
"""A/B CAPIT flag gate — job Taylor_20261103_024121. Reads leg logs + ledgers; writes ab_results_exp_.json.
Reuses paired_w2.metrics/boot (L=21 B=4000 seed=12345, one shared block-index stream for all legs)."""
import hashlib, io, json, os, re, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); LOGS = os.path.join(HERE, "logs")
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/c30v_w2_q2_20260927")
from paired_w2 import metrics, boot, L, B, SEED, load_nav
PIN = "537e349b5589408c994f8aceafeb9a39"
LEGS = [l for l in sys.argv[1:]] or ["ctrlmain_exp", "ctrloff_exp", "g_all_exp", "g_floor_exp", "g_rating_exp", "g_strict_exp"]
BASE = "ctrloff_exp"

def leg_path(tag):
    txt = io.open(os.path.join(LOGS, f"{tag}.log"), encoding="utf-8", errors="replace").read()
    assert f"EXIT=0 ({tag}" in txt, f"{tag} not EXIT=0"
    hits = [l.split("->", 1)[1].split("(")[0].strip() for l in txt.splitlines()
            if l.strip().startswith("-> ") and l.strip().endswith("rows)")]
    assert len(hits) == 1, hits
    sc = [l for l in txt.splitlines() if "self-check" in l.lower()]
    return hits[0], txt, sc

def md5(p):
    h = hashlib.md5(); h.update(open(p, "rb").read()); return h.hexdigest()

def mets(nav):
    r = np.log(nav).diff().dropna().values
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25; ann = len(r) / yrs
    c, s, d, k = metrics(r[:, None], ann); return dict(CAGR=float(c[0]), Sharpe=float(s[0]), MaxDD=float(d[0]), Calmar=float(k[0]))

def capit_events(path):
    df = pd.read_csv(path, low_memory=False)
    tx = df[(df.record_type == "TX") & df.play_type.astype(str).str.contains("CAPIT")].copy()
    tx["ev"] = tx.play_type.str.extract(r"_E(\d+)")[0].astype(int)
    g = tx.groupby("ev").agg(buy=("buy_amount", "sum"), sell=("sell_amount", "sum"), fee=("fee", "sum"),
                             names=("ticker", lambda s: ",".join(sorted(set(s)))), d0=("ymd", "min"))
    g["pnl"] = g.sell - g.buy - g.fee; g["ret"] = g.pnl / g.buy
    return g

res = {"job": "Taylor_20261103_024121", "boot": dict(L=L, B=B, seed=SEED), "legs": {}}
navs, evs = {}, {}
for t in LEGS:
    p, txt, sc = leg_path(t)
    navs[t] = load_nav(p); evs[t] = capit_events(p)
    nav = navs[t]
    m = {"ledger": os.path.basename(p), "md5": md5(p), "selfcheck_lines": sc[:6], "full": mets(nav),
         "IS": mets(nav[nav.index <= "2019-12-31"]), "OOS": mets(nav[nav.index >= "2019-12-31"]),
         "final_nav_B": float(nav.iloc[-1] / 1e9)}
    m["control_byte_identical_pin"] = (m["md5"] == PIN)
    m["drops"] = re.findall(r"\[capflag:\w+\] (\S+) pool (\d+) -> (\d+) dropped=(\S*)", txt)
    m["events"] = evs[t].reset_index().to_dict("records")
    res["legs"][t] = m
# pool composition from base log
_, btxt, _ = leg_path(BASE)
pools = {}
for d, body in re.findall(r"\[capflag-pool\] (\S+) (\S*)", btxt):
    pools.setdefault(d, [tuple(x.split(":")) for x in body.split(",") if x])
res["pools"] = pools
# paired bootstrap vs BASE
idx = navs[BASE].index
for t in LEGS:
    if t == BASE: continue
    assert navs[t].index.equals(idx)
R = np.column_stack([np.log(navs[t]).diff().dropna().values for t in LEGS])
yrs = (idx[-1] - idx[0]).days / 365.25; ann = R.shape[0] / yrs
C, S, D, K = boot(R, ann, R.shape[0]); bi = LEGS.index(BASE)
res["paired"] = {}
for j, t in enumerate(LEGS):
    if t in (BASE, "ctrlmain_exp"): continue
    dc = C[:, j] - C[:, bi]; dd = D[:, j] - D[:, bi]; dk = K[:, j] - K[:, bi]
    res["paired"][t] = {"dCAGR_pp_mean": float(dc.mean() * 100), "dCAGR_pp_90": [float(np.percentile(dc, 5) * 100), float(np.percentile(dc, 95) * 100)],
                        "P_CAGR_better": float((dc > 0).mean()), "P_MaxDD_better": float((dd > 0).mean()), "P_Calmar_better": float((dk > 0).mean())}
json.dump(res, open(os.path.join(HERE, "ab_results_exp_.json"), "w"), indent=1, default=str, ensure_ascii=False)
for t in LEGS:
    m = res["legs"][t]; f = m["full"]
    print(f"{t:14s} md5={m['md5'][:8]} pin={m['control_byte_identical_pin']} CAGR={f['CAGR']*100:.2f} Sh={f['Sharpe']:.2f} DD={f['MaxDD']*100:.1f} Cal={f['Calmar']:.2f} IS={m['IS']['CAGR']*100:.2f} OOS={m['OOS']['CAGR']*100:.2f} nav={m['final_nav_B']:.2f}")
print(json.dumps(res["paired"], indent=1))
