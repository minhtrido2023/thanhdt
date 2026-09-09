"""DT 4-gate CANDIDATE CLOCK as a per-date PIT series (job Taylor_20260909_112201, PAPER-ONLY).

Emits, for every session of the v3.4b BASE series, the state the gate is CURRENTLY committed to
plus whichever candidate it is accumulating toward and how long (k) — the exact quantity
`dna_report.get_dt_gate_clock()` prints live ("candidate BEAR 6/10"), but as a full history so a
backtest can consume it.

Causal by construction: the walk is the same forward loop as macro_state_live._dt_4gate /
dt_gate_hazard_research.extract_episodes — session t only ever reads raw[0..t]. Verified by the
truncation test in main() (clock computed on a truncated series must equal the full-series clock
on the overlapping prefix).

Source = the PINNED snapshot's own copy of tav2_bq.vnindex_5state_tam_quan_v34b_clean, so there is
no vintage gap vs the pinned R3 run.
"""
import os
import sys

import pandas as pd

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor")
from dt_gate_hazard_research import dt_4gate, need_for  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dt_candidate_clock_exp.csv")


def clock_series(times, raw, default=10, enC=25, exC=10, enX=25, exX=10):
    """Per-session (committed, cand, k, need). Same loop as _dt_4gate; nothing read ahead of t."""
    rows = [dict(time=times[0], committed=int(raw[0]), cand=int(raw[0]), k=1, need=0)]
    committed = raw[0]
    ps, pr = raw[0], 1
    for t in range(1, len(raw)):
        s = raw[t]
        if s == ps:
            pr += 1
        else:
            ps, pr = s, 1
        if ps != committed:
            need = need_for(ps, committed, default, enC, exC, enX, exX)
            if pr >= need:
                committed = ps
        else:
            need = 0
        rows.append(dict(time=times[t], committed=int(committed), cand=int(ps), k=int(pr),
                         need=int(need_for(ps, committed, default, enC, exC, enX, exX))
                         if ps != committed else 0))
    return pd.DataFrame(rows)


def main():
    from simulate_holistic_nav import bq
    b = bq("SELECT t.time, t.state FROM tav2_bq.vnindex_5state_tam_quan_v34b_clean AS t "
           "WHERE t.time >= DATE '2014-01-01' ORDER BY t.time")
    b["time"] = pd.to_datetime(b["time"])
    b = b.sort_values("time").reset_index(drop=True)
    times = list(b["time"])
    raw = b["state"].astype(int).values
    print(f"[clock] base v3.4b rows={len(b)} {times[0].date()} -> {times[-1].date()}")

    ck = clock_series(times, raw)

    # self-check 1: committed column must equal the production gate output exactly
    gate = dt_4gate(raw.copy())
    n_diff = int((ck["committed"].values != gate).sum())
    print(f"[selfcheck committed==dt_4gate] mismatches = {n_diff}")
    assert n_diff == 0, "clock committed series diverges from the production DT 4-gate"

    # self-check 2: PIT / no look-ahead — truncate at several points, clock on the prefix must be
    # identical to the full-series clock over that prefix.
    bad = 0
    for cut in (500, 1200, 2000, len(raw) - 5):
        sub = clock_series(times[:cut], raw[:cut].copy())
        merged = sub.merge(ck.head(cut), on="time", suffixes=("_cut", "_full"))
        d = int(((merged["committed_cut"] != merged["committed_full"])
                 | (merged["cand_cut"] != merged["cand_full"])
                 | (merged["k_cut"] != merged["k_full"])).sum())
        print(f"[selfcheck PIT cut={cut}] rows={len(merged)} diffs={d}")
        bad += d
    assert bad == 0, "clock is NOT point-in-time"

    ck.to_csv(OUT, index=False)
    print(f"[clock] wrote {OUT} rows={len(ck)}")

    # Descriptive: how often does a candidate leave {4,5} and reach k>=10 (the chan-C trigger)?
    trig = ck[(ck["committed"].isin([4, 5])) & (~ck["cand"].isin([4, 5])) & (ck["k"] >= 10)]
    print(f"[chan-C trigger] sessions where committed in 4/5, candidate outside, k>=10: {len(trig)}")
    if len(trig):
        print(trig.groupby(trig["time"].dt.year).size().to_string())


if __name__ == "__main__":
    main()
