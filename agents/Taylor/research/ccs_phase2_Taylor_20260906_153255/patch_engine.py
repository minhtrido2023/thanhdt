# -*- coding: utf-8 -*-
"""CCS Phase 2 — patch the job-local engine copy (ccs_p2_engine.py).
Base = the Phase 0 probe engine, itself a verified copy of production pt_v23_audit_2014.py whose
output was byte-identical to the pinned R3 artifact. Edits here are all env-gated on
CCS_TRIM_FRAC (unset/1.0 => byte-identical control leg):
  F1  load the PATCHED job-local shn copy under the canonical module name + trim-log collector
  F2  BAL: PIT per-session signal-rank tercile -> `_wmult` column on sig_f
  F3  LAG: same on sig_lag (placed AFTER TIER_PRIORITY gets LAG_HI/LAG_LO, which is what
      orders the LAG panel — `ta` is a constant 400.0 there)
  F4  tag + drain the trim log around each of the 4 simulate() calls, dump to CSV at the end
"""
import io, os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ccs_p2_engine.py")
src = io.open(p, encoding="utf-8").read()
orig = src

# ---- F1 -------------------------------------------------------------------
A_OLD = """import simulate_holistic_nav as shn
from simulate_holistic_nav import simulate, bq, VNI_QUERY, TC_BUY, TC_SELL, CG_TAX"""
A_NEW = '''# ---- CCS Phase 2: bind the job-local PATCHED copy of simulate_holistic_nav under the CANONICAL
# module name, so every downstream import (regime_size_overlay, capit builders, add_capit_arm)
# resolves to the same patched object. Production simulate_holistic_nav.py is untouched.
import importlib.util as _ilu
_SHN_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shn_trim.py")
_spec = _ilu.spec_from_file_location("simulate_holistic_nav", _SHN_SRC)
_shn_mod = _ilu.module_from_spec(_spec)
sys.modules["simulate_holistic_nav"] = _shn_mod
_spec.loader.exec_module(_shn_mod)

import simulate_holistic_nav as shn
from simulate_holistic_nav import simulate, bq, VNI_QUERY, TC_BUY, TC_SELL, CG_TAX
assert shn.__file__ == _SHN_SRC, "patched shn not bound"
assert hasattr(shn, "CCS_TRIM_LOG"), "shn copy is not the patched one"

# CCS_TRIM_FRAC: target-weight multiplier applied to BOTTOM-tercile signal rows. 1.0 = OFF.
CCS_TRIM_FRAC = float(os.environ.get("CCS_TRIM_FRAC", "1"))
_CCS_TRIM_ROWS = []      # drained per simulate() call, tagged with (book, pass)
_CCS_TERCILE_ROWS = []   # the PIT tercile assignment itself, for audit

def _ccs_take(book, phase):
    """Drain shn.CCS_TRIM_LOG into _CCS_TRIM_ROWS, tagged. seq_id is per-simulate-call."""
    for r in shn.CCS_TRIM_LOG:
        r = dict(r); r["book"] = book; r["pass"] = phase
        _CCS_TRIM_ROWS.append(r)
    n = len(shn.CCS_TRIM_LOG)
    del shn.CCS_TRIM_LOG[:]
    print(f"  [CCS trim] {book}/{phase}: {n} first-fill targets trimmed")

def _ccs_wmult(df, allowed, book):
    """Per-session PIT signal-rank tercile, EXACTLY the Phase 0 ledger definition
    (`ccs_phase0_ledger.py::rank_panel`): rank within the pool simulate() ranks, ordered by
    (TIER_PRIORITY desc, ta desc) with a STABLE sort; rank_pct = (rank-1)/n_cands; cut at 1/3, 2/3.
    Returns a float Series aligned to df.index: CCS_TRIM_FRAC on BOTTOM, else 1.0.
    Uses ONLY same-session information -> no look-ahead."""
    w = pd.Series(1.0, index=df.index)
    if CCS_TRIM_FRAC == 1.0:
        return w
    sub = df[df["play_type"].isin(allowed)].copy()
    sub["time"] = pd.to_datetime(sub["time"])
    sub["_pri"] = sub["play_type"].map(shn.TIER_PRIORITY).fillna(0)
    sub = sub.sort_values(["time", "_pri", "ta"], ascending=[True, False, False], kind="mergesort")
    _rank = sub.groupby("time").cumcount() + 1
    _n = sub.groupby("time")["ta"].transform("size")
    sub["sig_rank"] = _rank
    sub["sig_n_cands"] = _n
    sub["sig_rank_pct"] = (_rank - 1) / _n.clip(lower=1)
    sub["tercile"] = pd.cut(sub["sig_rank_pct"], [-1e-9, 1/3, 2/3, 1.0 + 1e-9],
                            labels=["TOP", "MID", "BOTTOM"])
    w.loc[sub.index[sub["tercile"] == "BOTTOM"]] = CCS_TRIM_FRAC
    sub["book"] = book
    _CCS_TERCILE_ROWS.append(sub[["book", "time", "ticker", "play_type", "ta", "sig_rank",
                                  "sig_n_cands", "sig_rank_pct", "tercile"]])
    _vc = sub["tercile"].value_counts()
    print(f"  [CCS trim] {book}: pool={len(sub)} of {len(df)} rows; "
          f"TOP={int(_vc.get('TOP',0))} MID={int(_vc.get('MID',0))} BOTTOM={int(_vc.get('BOTTOM',0))}"
          f" -> wmult={CCS_TRIM_FRAC} on BOTTOM")
    return w'''
assert src.count(A_OLD) == 1, "F1 anchor"
src = src.replace(A_OLD, A_NEW)

# ---- F2 -------------------------------------------------------------------
B_OLD = '''    print(f"  [CCS] dumped sig_bal.parquet rows={len(sig_f)}")'''
B_NEW = B_OLD + '''

# ---- CCS Phase 2 trim overlay, BAL (env CCS_TRIM_FRAC; 1.0 = byte-identical) ----
sig_f["_wmult"] = _ccs_wmult(sig_f, RS["allowed_tiers"], "BAL")'''
assert src.count(B_OLD) == 1, "F2 anchor"
src = src.replace(B_OLD, B_NEW)

# ---- F3 -------------------------------------------------------------------
C_OLD = '''shn.TIER_PRIORITY.update({"LAG_TOP": 90, "LAG_HI": 88, "LAG_LO": 82})'''
C_NEW = C_OLD + '''

# ---- CCS Phase 2 trim overlay, LAG (after TIER_PRIORITY learns LAG_*: `ta` is a constant 400.0
# on this panel, so play-type priority is what actually orders it) ----
sig_lag["_wmult"] = _ccs_wmult(sig_lag, _LAG_BASE_TIERS, "LAG")'''
assert src.count(C_OLD) == 1, "F3 anchor"
src = src.replace(C_OLD, C_NEW)

# ---- F4: drain the trim log after each simulate() call ---------------------
for old, tag in [
    ('''    nav_bal0, _ = simulate(sig_f, prices, vni_dates, tier_weights=RS["tier_weights"],
                           name="v23audit_BAL_base", **BAL_KW, **LIQ_FULL)''', ('BAL', 'base')),
    ('''    nav_lag0, _ = simulate(sig_lag, prices_lag, vni_dates, tier_weights=LAG_TW,
                           tier_weights_by_state=_lag_disc_twbs(LAG_TW),
                           name="v23audit_LAG_base", **LAG_KW, **LIQ_LAG)''', ('LAG', 'base')),
]:
    assert src.count(old) == 1, f"F4 anchor {tag}"
    src = src.replace(old, old + f'\n    _ccs_take("{tag[0]}", "{tag[1]}")')

for old, tag in [
    ('''nav_bal, _ = simulate(sig_balC, prices, vni_dates, tier_weights=tw_balC,''', ('BAL', 'main')),
    ('''nav_lag, _ = simulate(sig_lagC, prices_lag, vni_dates, tier_weights=tw_lagC,''', ('LAG', 'main')),
]:
    assert src.count(old) == 1, f"F4 anchor {tag}"
    i = src.index(old)
    j = src.index('\n', src.index(')\n', i))       # end of the call statement
    src = src[:j + 1] + f'_ccs_take("{tag[0]}", "{tag[1]}")\n' + src[j + 1:]

# ---- F4b: dump the logs next to the audit CSV ------------------------------
D_OLD = '''print("\\nANNUAL (sys vs VNINDEX):")'''
D_NEW = '''# ---- CCS Phase 2 artifacts (never canonical: job dir + _exp suffix) ----
_ccs_out = os.path.dirname(os.path.abspath(__file__))
_ccs_leg = os.environ.get("CCS_LEG", "leg")
if _CCS_TRIM_ROWS:
    pd.DataFrame(_CCS_TRIM_ROWS).to_csv(
        os.path.join(_ccs_out, f"trimlog_{_ccs_leg}_exp.csv"), index=False)
if _CCS_TERCILE_ROWS:
    pd.concat(_CCS_TERCILE_ROWS, ignore_index=True).to_csv(
        os.path.join(_ccs_out, f"tercile_{_ccs_leg}_exp.csv"), index=False)
pd.DataFrame([{"record_type": "DAILY_CCS", **r} for r in []])
daily_df.to_csv(os.path.join(_ccs_out, f"daily_{_ccs_leg}_exp.csv"), index=False)
tx_df.to_csv(os.path.join(_ccs_out, f"tx_{_ccs_leg}_exp.csv"), index=False)
metric_df.to_csv(os.path.join(_ccs_out, f"metric_{_ccs_leg}_exp.csv"), index=False)
print(f"  [CCS] wrote leg artifacts ({_ccs_leg}) to {_ccs_out}")

print("\\nANNUAL (sys vs VNINDEX):")'''
assert src.count(D_OLD) == 1, "F4b anchor"
src = src.replace(D_OLD, D_NEW)

assert src != orig
io.open(p, "w", encoding="utf-8").write(src)
print("patched ccs_p2_engine.py OK")
