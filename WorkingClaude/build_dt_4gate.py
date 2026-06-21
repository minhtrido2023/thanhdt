# -*- coding: utf-8 -*-
"""
build_dt_4gate.py
=================
Production builder for the DT 4-gate market-state series.

Upgrades DT_10_25_25 (which keyed confirmation only on the PENDING state) to a
4-gate directional asymmetric causal commitment filter, where ENTERING vs
EXITING the extreme states use independent thresholds:

    default     = 10   normal transitions among BEAR/NEUTRAL/BULL
    enter_crisis= 25    slow to commit DOWN into CRISIS  (avoid panic on noise)
    enter_exbull= 25    slow to commit UP into EX-BULL   (avoid chasing euphoria)
    exit_crisis = 10    recovery out of CRISIS
    exit_exbull = 10    derisk out of EX-BULL            (exit-EXBULL empirically inert)

These all-canonical params (10/25/10/25/10) are behaviorally identical to
DT_10_25_25 but expressed in the cleaner 4-gate parameterization.

Note: exit_crisis=7 (faster V-recovery capture) looked marginally better on
the pure-VNINDEX fixed-allocation sim, but FAILED the integrated Kelly test
(V5): +0.07pp return (noise) at the cost of MaxDD -27.0% vs -24.5% and Calmar
0.82 vs 0.90 — faster CRISIS exit = earlier risk re-entry = whipsaw under
leverage. exit_crisis=10 is the validated production value.
Deployment scope: MODERN ERA (2014+) per DT pre-2014 V-recovery caveat.

Base series: v3.4b (`vnindex_5state_tam_quan_v3_4b_full_history.csv`), same base
DT_10_25_25 was built from. Filter is causal (no look-ahead).
"""
import os, sys, io
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
BASE_CSV = os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_4b_full_history.csv")
OUT_CSV  = os.path.join(WORKDIR, "data/vnindex_5state_dt_4gate.csv")

PARAMS = dict(default=10, enter_crisis=25, exit_crisis=10, enter_exbull=25, exit_exbull=10)
CRISIS, EXBULL = 1, 5


def asym_dir_commit(states, default, enter_crisis, exit_crisis, enter_exbull, exit_exbull):
    """Causal 4-gate commitment. need(committed, pending):
       entering an extreme (pending in {CRISIS,EXBULL}) -> enter_* (slow);
       exiting an extreme (committed in {CRISIS,EXBULL}) -> exit_* (own param);
       else -> default. A pending state must persist `need` consecutive
       sessions before it is committed; otherwise the prior state holds."""
    states = np.asarray(states, dtype=int)
    out = states.copy()
    committed = states[0]
    pending_state, pending_run = states[0], 1
    for t in range(1, len(states)):
        s = states[t]
        if s == pending_state:
            pending_run += 1
        else:
            pending_state, pending_run = s, 1
        if pending_state == committed:
            out[t] = committed
            continue
        if pending_state == CRISIS:     need = enter_crisis
        elif pending_state == EXBULL:   need = enter_exbull
        elif committed == CRISIS:       need = exit_crisis
        elif committed == EXBULL:       need = exit_exbull
        else:                           need = default
        if pending_run >= need:
            committed = pending_state
        out[t] = committed
    return out


def main():
    base = pd.read_csv(BASE_CSV)
    base["time"] = pd.to_datetime(base["time"])
    base = base.sort_values("time").reset_index(drop=True)

    state_in  = base["state"].values.astype(int)
    state_raw = base["state_raw"].values.astype(int) if "state_raw" in base.columns else state_in.copy()

    state_out = asym_dir_commit(state_in, **PARAMS)

    out = pd.DataFrame({
        "time":      base["time"].dt.strftime("%Y-%m-%d"),
        "state":     state_out.astype(int),
        "state_raw": state_raw.astype(int),
    })
    out.to_csv(OUT_CSV, index=False)

    n_tr  = int((state_out[1:] != state_out[:-1]).sum())
    dist  = pd.Series(state_out).value_counts(normalize=True).sort_index()
    dist  = {int(k): round(v*100, 1) for k, v in dist.items()}
    print(f"Wrote {OUT_CSV}  ({len(out)} rows, {out['time'].iloc[0]} -> {out['time'].iloc[-1]})")
    print(f"Params: {PARAMS}")
    print(f"Transitions (full): {n_tr}   |   State dist %: {dist}")
    print(f"Latest state: {out['time'].iloc[-1]} = {int(state_out[-1])}")


if __name__ == "__main__":
    main()
