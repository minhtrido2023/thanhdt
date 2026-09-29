"""CCS Phase 0 gate #3 — count INDEPENDENT EPISODES per pre-registered hypothesis bucket.

Job Taylor_20260905_135003. Counting only: no expectancy, win-rate, or return statistic is
computed or printed here — that is Phase 1, and printing it now would make the pre-registration
in §5 of the proposal worthless.

Episode = a cluster of entries in the same bucket separated by <= GAP trading sessions. Trades
inside one cluster share the same market window and are NOT independent draws. GAP=10 sessions is
the headline; 5 and 21 are printed beside it so no conclusion can rest on that choice.
For market-level buckets (H3, H5) the calendar-block count is also reported (convention of
b2_neff, 2026-08-22): maximal contiguous runs of the condition over trading sessions.
"""
import json
import os

import numpy as np
import pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.join(WC, "mike/agents/Taylor/research/ccs_phase0_Taylor_20260905_135003")
MIN_EP = 30                                    # dispatch gate: below this -> descriptive only

d = pd.read_csv(os.path.join(OUT, "trade_ledger_bal_lag_exp.csv"),
                parse_dates=["entry_fill_date", "signal_date", "exit_date"])
cal = pd.read_csv(os.path.join(OUT, "breadth_pit_frozen_exp.csv"), parse_dates=["time"])
sessions = pd.DatetimeIndex(sorted(cal.time.unique()))
sidx = {t: i for i, t in enumerate(sessions)}
d["sess_i"] = d.signal_date.map(sidx)


def n_episodes(sub, gap=10):
    """Clusters of entry sessions separated by more than `gap` trading sessions."""
    s = sorted(sub.sess_i.dropna().unique())
    if not s:
        return 0
    return 1 + sum(1 for a, b in zip(s, s[1:]) if (b - a) > gap)


def summarise(name, sub, extra=None):
    row = dict(bucket=name, n_trades=int(len(sub)),
               n_entry_days=int(sub.signal_date.nunique()),
               n_tickers=int(sub.ticker.nunique()),
               n_years=int(sub.signal_date.dt.year.nunique()),
               ep_gap5=n_episodes(sub, 5), ep_gap10=n_episodes(sub, 10),
               ep_gap21=n_episodes(sub, 21))
    row["verdict"] = "OK" if row["ep_gap10"] >= MIN_EP else "THIN — descriptive only"
    if extra:
        row.update(extra)
    return row


def blocks(mask_by_session):
    m = np.asarray(mask_by_session, dtype=bool)
    return int(np.sum(m & ~np.r_[False, m[:-1]]))


# ---- derived bucket columns (must exist before the per-book views are taken)
d["recovery_dt"] = d.sessions_since_dt5g_upgrade <= 10
br = cal.sort_values("time").reset_index(drop=True)
br["turn_up"] = br.breadth > br.breadth.shift(5)          # breadth higher than 5 sessions earlier
turn = dict(zip(br.time, br.turn_up.fillna(False)))
# breadth is attached at t-1, so "turning up" is also read at t-1
d["breadth_low_turning"] = d.breadth_tercile_tm1.eq("LOW") & d.signal_date.map(
    lambda t: bool(turn.get(t - pd.Timedelta(days=0), False)) if pd.notna(t) else False)

out = []
BOOKS = [("BAL", d[d.book == "BAL"]), ("LAG", d[d.book == "LAG"]), ("BOTH", d)]

# ---- H1: dd52 <= -20% at entry (per-stock washout)
for bk, sub in BOOKS:
    for lab, m in (("dd52<=-20%", sub.dd52 <= -0.20), ("dd52>-20%", sub.dd52 > -0.20),
                   ("dd52 missing", sub.dd52.isna())):
        out.append(summarise(f"H1 {bk} {lab}", sub[m], {"hypothesis": "H1", "book": bk}))

# ---- H2: 1/PE tercile x recovery.  recovery = DT5G upgraded within the last 10 sessions
for bk, sub in BOOKS:
    for t in ("CHEAP", "MID", "EXPENSIVE"):
        for rec in (True, False):
            m = (sub.ey_tercile == t) & (sub.recovery_dt == rec)
            out.append(summarise(f"H2 {bk} ey={t} recovery={rec}", sub[m],
                                 {"hypothesis": "H2", "book": bk}))

# ---- H3: breadth tercile (t-1), plus "LOW and turning up"
for bk, sub in BOOKS:
    for t in ("LOW", "MID", "HIGH"):
        out.append(summarise(f"H3 {bk} breadth_tm1={t}", sub[sub.breadth_tercile_tm1 == t],
                             {"hypothesis": "H3", "book": bk}))
    out.append(summarise(f"H3 {bk} breadth LOW & turning up", sub[sub.breadth_low_turning],
                         {"hypothesis": "H3", "book": bk}))
# calendar-block N for the market-level condition itself (independent of how many trades fired)
bt = br.set_index("time")
for t in ("LOW", "MID", "HIGH"):
    out.append(dict(bucket=f"H3 CALENDAR breadth={t}", hypothesis="H3", book="market",
                    n_trades=int((bt.btile == t).sum()), n_entry_days=int((bt.btile == t).sum()),
                    n_tickers=0, n_years=int(bt[bt.btile == t].index.year.nunique()),
                    ep_gap5=blocks(bt.btile == t), ep_gap10=blocks(bt.btile == t),
                    ep_gap21=blocks(bt.btile == t),
                    verdict="OK" if blocks(bt.btile == t) >= MIN_EP else "THIN — descriptive only"))

# ---- H4: LAG only — surprise tercile x 1/PE tercile
lag = d[d.book == "LAG"]
for st in ("HIGH", "MID", "LOW"):
    for et in ("CHEAP", "MID", "EXPENSIVE"):
        m = (lag.lag_surprise_tercile == st) & (lag.ey_tercile == et)
        out.append(summarise(f"H4 LAG surprise={st} ey={et}", lag[m],
                             {"hypothesis": "H4", "book": "LAG"}))

# ---- H5: DT5G upgraded <= 10 sessions ago
for bk, sub in BOOKS:
    for lab, m in (("<=10 sessions since upgrade", sub.sessions_since_dt5g_upgrade <= 10),
                   (">10 sessions since upgrade", sub.sessions_since_dt5g_upgrade > 10)):
        out.append(summarise(f"H5 {bk} {lab}", sub[m], {"hypothesis": "H5", "book": bk}))
dtser = d[["signal_date", "sessions_since_dt5g_upgrade"]].drop_duplicates("signal_date") \
         .set_index("signal_date").reindex(sessions)
mk = (dtser.sessions_since_dt5g_upgrade <= 10).fillna(False)
out.append(dict(bucket="H5 CALENDAR <=10 sessions since upgrade", hypothesis="H5", book="market",
                n_trades=int(mk.sum()), n_entry_days=int(mk.sum()), n_tickers=0,
                n_years=int(sessions[mk.to_numpy()].year.nunique()),
                ep_gap5=blocks(mk), ep_gap10=blocks(mk), ep_gap21=blocks(mk),
                verdict="OK" if blocks(mk) >= MIN_EP else "THIN — descriptive only"))

# ---- H6: in-book signal rank tercile
for bk, sub in BOOKS:
    for t in ("TOP", "MID", "BOTTOM"):
        out.append(summarise(f"H6 {bk} rank={t}", sub[sub.sig_rank_tercile == t],
                             {"hypothesis": "H6", "book": bk}))
    out.append(summarise(f"H6 {bk} rank=n/a (CAPIT arm)", sub[sub.sig_rank_tercile.isna()],
                         {"hypothesis": "H6", "book": bk}))

E = pd.DataFrame(out)[["hypothesis", "book", "bucket", "n_trades", "n_entry_days", "n_tickers",
                       "n_years", "ep_gap5", "ep_gap10", "ep_gap21", "verdict"]]
E.to_csv(os.path.join(OUT, "n_episode_by_bucket_exp.csv"), index=False)
print(E.to_string(index=False))
thin = E[E.verdict.str.startswith("THIN")]
print(f"\n[gate] buckets total={len(E)} | THIN (<{MIN_EP} episodes @gap10) = {len(thin)}")
with open(os.path.join(OUT, "n_episode_summary_exp.json"), "w") as fh:
    json.dump({"min_episodes_gate": MIN_EP, "n_buckets": len(E), "n_thin": int(len(thin)),
               "thin_buckets": thin.bucket.tolist()}, fh, indent=2)
