# -*- coding: utf-8 -*-
"""CCS Phase 2 — patch the job-local COPY of simulate_holistic_nav (shn_trim.py).
Three surgical edits, all no-ops when no signal row carries `_wmult` (default = control leg):
  E1  module-level CCS_TRIM_LOG list
  E2  carry `_wmult` from the signal row into the queued pending entry
  E3  scale target_value by `_wmult` at first fill + log the cut
Production simulate_holistic_nav.py is NOT touched (coding_guidelines §3/§8).
"""
import io, sys, os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shn_trim.py")
src = io.open(p, encoding="utf-8").read()
orig = src

# ---- E1: module-level trim log (declared next to WORKDIR) -------------------
A_OLD = 'WORKDIR = r"/home/trido/thanhdt/WorkingClaude"'
A_NEW = (A_OLD + "\n\n"
         "# CCS Phase 2 (trim-bottom overlay). Appended to at every first-fill whose entry carries\n"
         "# a `_wmult` != 1.0. Caller snapshots + clears it around each simulate() call.\n"
         "CCS_TRIM_LOG = []\n")
assert src.count(A_OLD) == 1, "E1 anchor"
src = src.replace(A_OLD, A_NEW)

# ---- E2: carry _wmult onto the queued entry --------------------------------
B_OLD = '''                        "seq_id": _entry_seq,
                        "_fund_tb": float(sig["_ftb"]) if "_ftb" in todays_sig.columns else 0.0,
                    })'''
B_NEW = '''                        "seq_id": _entry_seq,
                        "_fund_tb": float(sig["_ftb"]) if "_ftb" in todays_sig.columns else 0.0,
                        # CCS Phase 2: per-row target-weight multiplier (absent -> 1.0 = unchanged)
                        "_wmult": (float(sig["_wmult"])
                                   if ("_wmult" in todays_sig.columns and pd.notna(sig["_wmult"]))
                                   else 1.0),
                    })'''
assert src.count(B_OLD) == 1, "E2 anchor"
src = src.replace(B_OLD, B_NEW)

# ---- E3: scale target_value + log ------------------------------------------
C_OLD = '''                if effective_tw is not None and play_type in effective_tw:
                    target_value = cur_nav * effective_tw[play_type]
                else:
                    target_value = cur_nav / max_positions'''
C_NEW = '''                if effective_tw is not None and play_type in effective_tw:
                    target_value = cur_nav * effective_tw[play_type]
                else:
                    target_value = cur_nav / max_positions
                # CCS Phase 2 trim overlay: pure sizing scale, applied BEFORE the JIT-ETF-sell and
                # margin/cash clamps below so the trimmed target is what drives funding. _wm == 1.0
                # (every entry on the control leg) multiplies exactly, so the leg is bit-identical.
                _ccs_wm = float(entry.get("_wmult", 1.0))
                _ccs_tv_full = float(target_value)
                if _ccs_wm != 1.0:
                    target_value = target_value * _ccs_wm'''
assert src.count(C_OLD) == 1, "E3a anchor"
src = src.replace(C_OLD, C_NEW)

D_OLD = '''                if target_value < 1_000_000:
                    continue
                entry["target_value"] = target_value'''
D_NEW = '''                if target_value < 1_000_000:
                    continue
                entry["target_value"] = target_value
                if _ccs_wm != 1.0:
                    # holding_id as it WILL be minted if this session produces the first fill
                    # (first_fill_date is set to `today` a few lines below when buy_value >= 100k).
                    CCS_TRIM_LOG.append({
                        "ymd": today, "ticker": tk, "seq_id": entry.get("seq_id"),
                        "play_type": play_type, "wmult": _ccs_wm,
                        "cur_nav": float(cur_nav),
                        "target_full_vnd": _ccs_tv_full,
                        "target_trim_vnd": float(target_value),
                        "cut_vnd": float(_ccs_tv_full - target_value),
                        "cash_before": float(cash),
                        "holding_id": "%s_%s_%s" % (tk, today.strftime("%Y%m%d"), entry.get("seq_id", "?")),
                    })'''
assert src.count(D_OLD) == 1, "E3b anchor"
src = src.replace(D_OLD, D_NEW)

assert src != orig
io.open(p, "w", encoding="utf-8").write(src)
print("patched shn_trim.py: 4 anchors OK")
