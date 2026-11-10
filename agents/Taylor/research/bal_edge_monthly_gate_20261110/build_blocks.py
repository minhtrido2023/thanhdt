"""Build monthly-gate block schedules from the BLIND (pin0%, park0) control ledger — job Taylor_20261110_053025.

Signal = calendar-month return of the BLIND BAL book (`nav_bal_ref`, pure book ledger, no allocator
flows), taken from the pin0% blind ledger (carry-neutral trading metric) and used for BOTH carry
conventions so the block schedule is identical across carries (one axis at a time).
Causality: month M's return is known at the close of M's last session; the state it implies governs
first fills on every session of month M+1+LAG (orders queued on M's last session execute T+1 = first
session of M+1, so lag 0 is already causal; LAG=1,2 emulate a slower live series).
"No sample": month with mean stock exposure < MIN_EXPO of BAL NAV, or return exactly 0 -> hold state.

Usage: build_blocks.py <ledger.csv> <outdir>   -> writes <outdir>/<variant>.txt (+ states.csv)
"""
import sys, json
import numpy as np, pandas as pd

LEDGER, OUT = sys.argv[1], sys.argv[2]
BOOK = sys.argv[3] if len(sys.argv) > 3 else "bal"   # "lag" = LAG comparison leg (measurement only)
MIN_EXPO = 0.05

d = pd.read_csv(LEDGER, low_memory=False)
d = d[d.record_type == "DAILY"].copy()
d["ymd"] = pd.to_datetime(d["ymd"])
d = d.sort_values("ymd").set_index("ymd")
d["expo"] = d[f"{BOOK}_stocks_ref"] / d[f"nav_{BOOK}_ref"]
d["ym"] = d.index.to_period("M")
m = d.groupby("ym").agg(nav=(f"nav_{BOOK}_ref", "last"), expo=("expo", "mean"),
                        n_sess=("nav_bal_ref", "size"))
prev = m["nav"].shift(1)
prev.iloc[0] = d[f"nav_{BOOK}_ref"].iloc[0]          # first month vs starting capital
m["ret"] = m["nav"] / prev - 1
m["sample_ok"] = (m["expo"] >= MIN_EXPO) & (m["ret"] != 0)
# 3-month trailing (compounded) return, "no sample" if none of the 3 months had sample
m["ret3"] = (1 + m["ret"]).rolling(3).apply(np.prod, raw=True) - 1
m["ok3"] = m["sample_ok"].rolling(3).sum() >= 1


def run(sig_ok, lock_fn, unlock_fn):
    """Return Series ym -> locked(bool) DECIDED at end of month ym (applies to later months)."""
    locked, out, hist = False, {}, []
    for ym in m.index:
        ok = bool(sig_ok.loc[ym]) if pd.notna(sig_ok.loc[ym]) else False
        hist.append((ok, ym))
        if ok:
            if not locked and lock_fn(ym):
                locked = True
            elif locked and unlock_fn(ym):
                locked = False
        out[ym] = locked
    return pd.Series(out)


r, r3, ok, ok3 = m["ret"], m["ret3"], m["sample_ok"], m["ok3"]
okidx = list(m.index)


def last_ok(ym, k, series=r, okser=ok):
    """last k sample-ok monthly values up to and including ym (in calendar order)."""
    vals = [series.loc[x] for x in okidx[:okidx.index(ym) + 1] if okser.loc[x]]
    return vals[-k:] if len(vals) >= k else None


def min_holdings_ok():
    tx = pd.read_csv(LEDGER, low_memory=False)
    tx = tx[(tx.record_type == "TX") & (tx.book == BOOK.upper()) & (tx.action == "buy")]
    tx["ym"] = pd.to_datetime(tx["ymd"]).dt.to_period("M")
    return tx.groupby("ym")["holding_id"].nunique().reindex(m.index).fillna(0)


VAR = {}
VAR["G1"] = run(ok, lambda y: r[y] < 0, lambda y: r[y] > 0)                         # base rule
VAR["G2_3m"] = run(ok3, lambda y: r3[y] < 0, lambda y: r3[y] > 0)                 # 3M trailing
VAR["G3_x2"] = run(ok, lambda y: r[y] < -0.02, lambda y: r[y] > 0)                # lock only if < -2%
VAR["G4_hu2"] = run(ok, lambda y: r[y] < 0,                                        # unlock needs 2 pos
                    lambda y: (v := last_ok(y, 2)) is not None and all(x > 0 for x in v))
VAR["G5_hl2"] = run(ok, lambda y: (v := last_ok(y, 2)) is not None and all(x < 0 for x in v),  # lock needs 2 neg
                    lambda y: r[y] > 0)
nh = min_holdings_ok()
ok_n3 = ok & ((nh >= 3) | (m["expo"] >= 0.30))                                     # n_min: >=3 names bought or >=30% expo
VAR["G6_n3"] = run(ok_n3, lambda y: r[y] < 0, lambda y: r[y] > 0)

sess = pd.Series(d.index, index=d.index)
rows = []
for name, st in VAR.items():
    for lag in ([0, 1, 2] if name == "G1" else [0]):
        appl = st.shift(1 + lag).reindex(m.index).fillna(False).astype(bool)   # state applying DURING month
        tag = f"{name}_L{lag}"
        blk = d.index[d["ym"].map(appl).astype(bool)]
        with open(f"{OUT}/{tag}.txt", "w") as f:
            f.write("\n".join(x.strftime("%Y-%m-%d") for x in blk) + ("\n" if len(blk) else ""))
        n_tr = int((appl.astype(int).diff().abs() == 1).sum())
        rows.append(dict(variant=tag, months_locked=int(appl.sum()), frac_locked=float(appl.mean()),
                         transitions=n_tr, lock_episodes=int(((appl.astype(int).diff() == 1)).sum() + int(appl.iloc[0])),
                         sessions_blocked=len(blk)))
        m[f"lk_{tag}"] = appl
m.to_csv(f"{OUT}/states.csv")
s = pd.DataFrame(rows)
s.to_csv(f"{OUT}/summary.csv", index=False)
print(s.to_string(index=False))
print(f"months={len(m)} sample_ok={int(ok.sum())} neg={int((ok & (r < 0)).sum())} pos={int((ok & (r > 0)).sum())}")
