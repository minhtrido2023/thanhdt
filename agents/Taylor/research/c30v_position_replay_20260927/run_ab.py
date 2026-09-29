#!/usr/bin/env python3
"""A/B R3 with the PARK leg swapped for the position-replay level — ONE variable, engine untouched.

`pt_v23_audit_2014.py` takes the parking vehicle's level series straight from
`custom_basket.build_pit()`. Wrapping that one function is therefore the minimal intervention: the
membership, the ADV cap, the weights, every allocator rule and the whole NAV machinery stay
byte-identical, and the only thing that changes is WHICH return series the parked cash earns.

Why a wrapper and not an edit: `pt_v23_audit_2014.py:42` does `sys.path.insert(0, WORKDIR)` with
WORKDIR hardcoded to the canonical checkout, so running a copy of the engine from elsewhere would
silently re-import the CANONICAL custom_basket — the no-op-in-silence class of §29. Loading the
patch into `sys.modules` first makes every `import custom_basket` at any depth resolve to it.

argv: run_ab.py <REPLAY_A|REPLAY_B|ENGINE_FLAT> <engine args...>
"""
import os
import runpy
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WC)

LEG = sys.argv[1]
lv = pd.read_parquet(f"{HERE}/levels_base.parquet")[LEG]

import custom_basket as cb

_orig = cb.build_pit


def build_pit_patched(*a, **k):
    lvl, adv, mem, bx = _orig(*a, **k)
    if LEG == "ENGINE_FLAT":
        # control leg: prove the wrapper itself is a no-op before trusting the treated leg.
        ref = pd.Series(lvl).sort_index()
        j = lv.reindex(ref.index)
        err = float((j / ref - 1).abs().max())
        print(f"  [AB-wrapper] CONTROL {LEG}: max |Δ| vs build_pit = {err:.3e}", flush=True)
        assert err < 1e-9, "control leg lệch -> wrapper KHÔNG phải no-op, không đọc số treated"
    s = lv.reindex(pd.Series(lvl).sort_index().index)
    assert s.notna().all(), f"level {LEG} thiếu ngày so với build_pit"
    out = {t: float(v) for t, v in zip(s.index, s.values)}
    print(f"  [AB-wrapper] park leg = {LEG}  ({len(out)} ngày, "
          f"{s.iloc[0]:.1f} -> {s.iloc[-1]:.1f})", flush=True)
    return out, adv, mem, bx


cb.build_pit = build_pit_patched
sys.argv = [f"{WC}/pt_v23_audit_2014.py"] + sys.argv[2:]
runpy.run_path(f"{WC}/pt_v23_audit_2014.py", run_name="__main__")
