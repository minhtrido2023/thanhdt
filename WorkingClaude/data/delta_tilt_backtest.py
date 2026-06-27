# -*- coding: utf-8 -*-
"""
delta_tilt_backtest.py — Test a delta_momentum WEIGHT TILT inside the custom30V parking basket.

Question (job Taylor_20260627_111639): does tilting custom30V intra-basket weights toward stocks
with improving fundamentals (ΔNP_R earnings acceleration + ΔFSCORE Piotroski improvement) BEAT the
plain cap-weighted (namecap) custom30V used in V2.4 NEUTRAL parking? WIRE only if OOS CAGR AND OOS
Calmar both improve (no DD trade-off), net of the extra intra-basket turnover the tilt induces.

Design (NO production code touched — Option B from dispatch):
  1. Call cb.build_pit() ONCE (yieldcombo / quality=none / gate_rating=3 / q2m5 / namecap) to get the
     baseline NAV (lvl_base), basket membership (memdf), and the raw daily panel (bx). Membership is
     UNCHANGED by the tilt — top-30-by-yieldcombo stays; only intra-basket weights move.
  2. Build a PIT delta_momentum table from ticker_financial, joined as-of Release_Date (no look-ahead):
       d_NPR    = (NP_P0/NP_P4 - 1) - (NP_P1/NP_P5 - 1)   [requires NP_P4>0 AND NP_P5>0]
       d_FSCORE = FSCORE - FSCORE_P1
  3. At each rebal_date: among the basket's own names, z-score d_NPR and d_FSCORE cross-sectionally,
       dm_score   = 0.6*z(d_NPR) + 0.4*z(d_FSCORE)   (weights from prior IC study Taylor_20260627_105942)
       tilt_factor= 1 + 0.15*clip(dm_score, -2, +2)   (=> per-name weight adj capped at ±30%)
     Missing delta -> tilt_factor = 1.0 (neutral).
  4. Reconstruct the chained namecap NAV myself for BOTH variants (tilt_factor=1 reproduces build_pit
     => SELF-CHECK), differing ONLY by the tilt multiplier on the pre-cap weight base.
  5. Overlay the SAME DT5G gate + cost model as custom30v_singlebook_faithful.py; the tilt variant pays
     EXTRA intra-basket turnover TC = 0.5*sum|w_tilt - w_capbase| * TC at each rebal.
  6. Walk-forward IS(2014-19)/OOS(2020+); report CAGR/Sharpe/MaxDD/Calmar + basket diff diagnostics.
"""
import os, sys, bisect, json, numpy as np, pandas as pd
WORKDIR = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude"); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import bq
import custom_basket as cb

START, END = "2014-01-01", "2026-06-19"
W_STATE = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.3}          # DT5G production 5-state allocation
TC = 0.003; REBAL_TURN = 0.35; BORROW = 0.10 / 252.0        # identical to custom30v_singlebook_faithful.py
NAME_CAP = 0.10
TILT_BETA = 0.15; W_DNPR = 0.6; W_DFSC = 0.4; CLIP = 2.0


def metrics(r):
    s = (1 + r).cumprod(); yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1; spd = len(r) / yrs
    sh = r.mean() / r.std() * np.sqrt(spd) if r.std() > 0 else 0; dd = (s / s.cummax() - 1).min()
    return cagr * 100, sh, dd * 100, (cagr * 100) / abs(dd * 100) if dd < 0 else 0


def _cap_names(w, cap):  # water-fill cap (copy of cb._cap_names so we stay self-contained)
    w = np.array(w, dtype=float); s = w.sum()
    if s <= 0: return w
    w = w / s
    for _ in range(100):
        over = w > cap + 1e-12
        if not over.any(): break
        excess = float((w[over] - cap).sum()); w[over] = cap
        under = ~over; us = float(w[under].sum())
        if us <= 1e-12: break
        w[under] = w[under] + excess * w[under] / us
    return w


# ----------------------------------------------------------------------------- 1. baseline build_pit
os.environ["BASKET_SELECT"] = "yieldcombo"
print("building baseline custom30V (build_pit, namecap) ...", flush=True)
lvl_base, _, memdf, bx = cb.build_pit(bq, START, END, quality="none", rebal="q2m5",
                                      gate_rating=3, weight_scheme="namecap")
lvl_base = pd.Series(lvl_base).sort_index(); lvl_base.index = pd.to_datetime(lvl_base.index)
memdf["rebal_date"] = pd.to_datetime(memdf["rebal_date"])

# daily mcap panel from the raw bx (same source build_pit weights off)
bx["time"] = pd.to_datetime(bx["time"])
mcap = bx.pivot_table(index="time", columns="ticker", values="mcap").sort_index()

# ----------------------------------------------------------------------------- 2. PIT delta_momentum
print("building PIT delta_momentum table ...", flush=True)
fin = bq("""SELECT ticker, Release_Date, NP_P0, NP_P1, NP_P4, NP_P5, FSCORE, FSCORE_P1
FROM tav2_bq.ticker_financial WHERE Release_Date IS NOT NULL""")
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
npr_cur = np.where(fin["NP_P4"] > 0, fin["NP_P0"] / fin["NP_P4"] - 1, np.nan)
npr_pri = np.where(fin["NP_P5"] > 0, fin["NP_P1"] / fin["NP_P5"] - 1, np.nan)
fin["d_NPR"] = npr_cur - npr_pri
fin["d_FSCORE"] = fin["FSCORE"] - fin["FSCORE_P1"]
fin = fin.dropna(subset=["d_NPR", "d_FSCORE"], how="all").sort_values("Release_Date")
# as-of lookup: per ticker, sorted (release_date -> (d_NPR, d_FSCORE))
dm_by_tk = {tk: (list(g["Release_Date"]), list(g["d_NPR"]), list(g["d_FSCORE"]))
            for tk, g in fin.groupby("ticker")}


def dm_asof(tk, d):
    e = dm_by_tk.get(tk)
    if not e: return (np.nan, np.nan)
    i = bisect.bisect_right(e[0], pd.Timestamp(d)) - 1
    return (e[1][i], e[2][i]) if i >= 0 else (np.nan, np.nan)


# ----------------------------------------------------------------------------- 3. per-rebal tilt map
def zscore(s):
    s = pd.Series(s, dtype=float); mu = s.mean(); sd = s.std(ddof=0)
    return (s - mu) / sd if (pd.notna(sd) and sd > 1e-12) else pd.Series(0.0, index=s.index)


members = {}  # rebal_date -> list[ticker]  (qmult is 1.0 since quality='none')
for d, g in memdf.groupby("rebal_date"):
    members[d] = list(g.sort_values("liq_rank")["ticker"])

tilt_map = {}      # rebal_date -> {ticker: tilt_factor}
rank_changes = []  # diagnostics: #names crossing the top-10/11-30 boundary vs cap order
wmae_list = []     # diagnostics: MAE between cap weights and tilt weights
extra_turn = {}    # rebal_date -> extra one-way intra-basket turnover induced by tilt
for d, tks in members.items():
    dn = pd.Series({t: dm_asof(t, d)[0] for t in tks})
    df = pd.Series({t: dm_asof(t, d)[1] for t in tks})
    z = W_DNPR * zscore(dn).fillna(0.0) + W_DFSC * zscore(df).fillna(0.0)
    tf = (1 + TILT_BETA * z.clip(-CLIP, CLIP))
    # missing BOTH deltas -> strictly neutral
    both_miss = dn.isna() & df.isna()
    tf[both_miss] = 1.0
    tilt_map[d] = tf.to_dict()

print(f"baseline rebal dates: {len(members)} | tilt map built", flush=True)


# ----------------------------------------------------------------------------- 4. reconstruct NAV
def recon_nav(apply_tilt):
    """Chained namecap NAV. apply_tilt=False reproduces build_pit (self-check)."""
    idx = mcap.index
    reb = sorted(members.keys())

    def active(dd):
        i = bisect.bisect_right(reb, dd) - 1
        return reb[i] if i >= 0 else None

    ret = pd.Series(0.0, index=idx); prev = None
    for dd in idx:
        aq = active(dd)
        if aq is None or prev is None:
            prev = dd; continue
        tks = [t for t in members[aq] if t in mcap.columns]
        today = mcap.loc[dd, tks].values.astype(float)
        yest = mcap.loc[prev, tks].values.astype(float)
        valid = ~np.isnan(today) & ~np.isnan(yest)
        if valid.sum() > 0:
            yv = yest[valid]
            base = yv.copy()
            if apply_tilt:
                tf = np.array([tilt_map[aq].get(t, 1.0) for t, ok in zip(tks, valid) if ok])
                base = base * tf
            W = _cap_names(base, NAME_CAP)
            r = today[valid] / yv - 1.0
            ret.loc[dd] = float(np.nansum(W * r))
        prev = dd
    return ret


# diagnostics: per-rebal weight deviation & rank shifts (cap base vs tilt base, on the rebal day panel)
def rebal_diag():
    reb = sorted(members.keys())
    for aq in reb:
        # use the first available panel day on/after rebal for yesterday-mcap basis
        days = mcap.index[mcap.index <= aq]
        if len(days) == 0: continue
        bday = days[-1]
        tks = [t for t in members[aq] if t in mcap.columns]
        yv = mcap.loc[bday, tks].values.astype(float)
        valid = ~np.isnan(yv)
        if valid.sum() < 2: continue
        yv = yv[valid]; tksv = [t for t, ok in zip(tks, valid) if ok]
        w_cap = _cap_names(yv.copy(), NAME_CAP)
        tf = np.array([tilt_map[aq].get(t, 1.0) for t in tksv])
        w_tilt = _cap_names(yv * tf, NAME_CAP)
        wmae_list.append(np.mean(np.abs(w_tilt - w_cap)))
        extra_turn[aq] = 0.5 * np.sum(np.abs(w_tilt - w_cap))
        # rank: top-10 by weight, count membership change of the top-10 set
        o_cap = set(pd.Series(w_cap, index=tksv).sort_values(ascending=False).index[:10])
        o_tlt = set(pd.Series(w_tilt, index=tksv).sort_values(ascending=False).index[:10])
        rank_changes.append(len(o_cap ^ o_tlt) // 2)


rebal_diag()

print("reconstructing NAVs (baseline self-check + tilt) ...", flush=True)
rb_base = recon_nav(apply_tilt=False)     # should match lvl_base
rb_tilt = recon_nav(apply_tilt=True)

# SELF-CHECK: reconstructed baseline vs build_pit level_dict
lvl_recon = (1 + rb_base).cumprod()
common = lvl_base.index.intersection(lvl_recon.index)
b_ret = lvl_base.loc[common].pct_change().dropna()
r_ret = lvl_recon.loc[common].pct_change().dropna()
ci = b_ret.index.intersection(r_ret.index)
maxdiff = float(np.max(np.abs((b_ret.loc[ci] - r_ret.loc[ci]).values))) if len(ci) else 9.9
print(f"SELF-CHECK recon-baseline vs build_pit: max daily-return abs diff = {maxdiff:.2e} "
      f"({'OK' if maxdiff < 1e-9 else 'MISMATCH — investigate'})", flush=True)


# ----------------------------------------------------------------------------- 5. DT5G overlay + cost
st = bq("SELECT s.time, s.state FROM tav2_bq.vnindex_5state_dt5g_live s")
st["time"] = pd.to_datetime(st["time"]); SD = dict(zip(st["time"], st["state"]))
rebd = set(members.keys())


def overlay(rb_gross, with_extra_turn):
    idx = rb_gross.index
    w = pd.Series([W_STATE.get(int(SD.get(d, np.nan)) if pd.notna(SD.get(d, np.nan)) else 3, 0.7)
                   for d in idx], index=idx).ffill().bfill()
    w_lag = w.shift(1).fillna(0.7)
    r = w_lag * rb_gross
    r = r - np.maximum(0.0, w_lag - 1.0) * BORROW
    r = r - (w_lag.diff().abs().fillna(0.0)) * TC
    # quarterly rebal TC (baseline assumed REBAL_TURN) + optional EXTRA intra-basket tilt turnover
    rebc = []
    for d in idx:
        c = REBAL_TURN * TC * w_lag[d] if d in rebd else 0.0
        if with_extra_turn and d in rebd:
            c += extra_turn.get(d, 0.0) * TC * w_lag[d]
        rebc.append(c)
    r = r - pd.Series(rebc, index=idx)
    return r


r_base = overlay(rb_base, with_extra_turn=False)
r_tilt = overlay(rb_tilt, with_extra_turn=True)

WINS = [("FULL 2014->now", None, None), ("IS 2014-2019", None, pd.Timestamp("2019-12-31")),
        ("OOS 2020->now", pd.Timestamp("2020-01-01"), None)]


def win(r, a, b):
    rr = r.copy()
    if a is not None: rr = rr[rr.index >= a]
    if b is not None: rr = rr[rr.index <= b]
    return metrics(rr)


print(f"\ncosts: TC={TC} (slippage incl), rebal_turn={REBAL_TURN}, borrow=10%/yr; DT5G W={W_STATE}")
print(f"tilt: dm=0.6*z(dNPR)+0.4*z(dFSCORE), factor=1+{TILT_BETA}*clip(dm,±{CLIP}); namecap={NAME_CAP}")
print(f"avg intra-basket weight MAE (tilt vs cap): {np.mean(wmae_list)*100:.3f}%  | "
      f"avg one-way extra turnover/rebal: {np.mean(list(extra_turn.values()))*100:.2f}%  | "
      f"avg top-10 set changes/rebal: {np.mean(rank_changes):.2f} names")

rows = {}
for tag, a, b in WINS:
    cb_, sb, db, calb = win(r_base, a, b)
    ct, st_, dt, calt = win(r_tilt, a, b)
    rows[tag] = (cb_, sb, db, calb, ct, st_, dt, calt)

print("\n| Window | Metric | Baseline | Delta_Tilt | Diff |")
print("|--------|--------|----------|------------|------|")
for tag, a, b in WINS:
    cb_, sb, db, calb, ct, st_, dt, calt = rows[tag]
    print(f"| {tag} | CAGR%  | {cb_:.2f} | {ct:.2f} | {ct-cb_:+.2f} |")
    print(f"| {tag} | Sharpe | {sb:.2f} | {st_:.2f} | {st_-sb:+.2f} |")
    print(f"| {tag} | MaxDD% | {db:.1f} | {dt:.1f} | {dt-db:+.1f} |")
    print(f"| {tag} | Calmar | {calb:.2f} | {calt:.2f} | {calt-calb:+.2f} |")

# ----------------------------------------------------------------------------- 6. verdict
oc_b, _, _, ocal_b = win(r_base, pd.Timestamp("2020-01-01"), None)
oc_t, _, _, ocal_t = win(r_tilt, pd.Timestamp("2020-01-01"), None)
wire = (oc_t > oc_b) and (ocal_t > ocal_b)
verdict = "WIRE" if wire else "REJECT"
print(f"\nVERDICT: {verdict}  (OOS CAGR {oc_b:.2f}->{oc_t:.2f} {oc_t-oc_b:+.2f}pp ; "
      f"OOS Calmar {ocal_b:.2f}->{ocal_t:.2f} {ocal_t-ocal_b:+.2f})")
print("rule: WIRE only if OOS CAGR AND OOS Calmar both improve.")

# emit machine-readable summary for the bus payload
summary = {"selfcheck_maxdiff": maxdiff, "verdict": verdict,
           "avg_w_mae_pct": round(float(np.mean(wmae_list))*100, 3),
           "avg_extra_turn_pct": round(float(np.mean(list(extra_turn.values())))*100, 2),
           "windows": {tag: {"base": [round(rows[tag][0],2), round(rows[tag][1],2), round(rows[tag][2],1), round(rows[tag][3],2)],
                             "tilt": [round(rows[tag][4],2), round(rows[tag][5],2), round(rows[tag][6],1), round(rows[tag][7],2)]}
                       for tag, _, _ in WINS}}
print("\nJSON " + json.dumps(summary))
