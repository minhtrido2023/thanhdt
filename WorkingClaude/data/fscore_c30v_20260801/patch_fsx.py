# -*- coding: utf-8 -*-
"""patch_fsx.py — job Taylor_20260801_131833.

Generates data/fscore_c30v_20260801/custom_basket_fsx.py from the PRODUCTION custom_basket.py
by inserting an AUDIT-ONLY FSCORE-enhancer block for the custom30V (BASKET_SELECT=yieldcombo)
selector. Production custom_basket.py is NEVER edited (quant-research skill §13).

The enhancer is env-gated and DEFAULT OFF -> with BASKET_FS_MODE unset the generated module is
behaviourally byte-identical to production (proved by the ctrl leg reproducing the pinned R3
number 27,60% / 1,84 / -17,5% / 1,58 exactly).

Modes (BASKET_FS_MODE):
  ""         OFF (default) — byte-identical
  "blend"    score[t] += BASKET_FS_W * rank_pct(FSCORE)   (membership CAN change)
  "tiebreak" permute FSCORE-bearing names inside the band straddling the top_n cut
             (membership CAN change, but ONLY at the margin; mirrors _dy_reorder exactly)
  "wtilt"    membership UNCHANGED; qmult *= 1 + BASKET_FS_T*2*(rank_pct(FSCORE)-0.5)

FSCORE source: tav2_bq.ticker_financial (CANONICAL per mike/kb/data_registry/fundamentals/
ticker_financial.md), joined POINT-IN-TIME on Release_Date (fallback time+45d) — the identical
convention the existing BASKET_QFLOOR block in this same file already uses.
Missing FSCORE = NEUTRAL everywhere (0.5 mid-rank for blend/wtilt, "does not move" for tiebreak),
matching the file's existing convention for a missing 1/PE and for DCF NOT_COMPUTED.
"""
import os

SRC = "/home/trido/thanhdt/WorkingClaude/custom_basket.py"
DST = "/home/trido/thanhdt/WorkingClaude/data/fscore_c30v_20260801/custom_basket_fsx.py"

src = open(SRC, encoding="utf-8").read()

# ---------------------------------------------------------------- (A) loader + as-of accessor
A_ANCHOR = '''    def qfloor_asof(tk, d):
        e = qf_by_tk.get(tk)
        if not e: return False
        i = bisect.bisect_right(e[0], d) - 1
        return bool(e[1][i]) if i >= 0 else False
'''
A_ADD = A_ANCHOR + '''
    # ---- AUDIT-ONLY FSCORE ENHANCER on the custom30V (yieldcombo) selector -------------------
    # job Taylor_20260801_131833. Tests the open lead from IC PANEL 8L (results_registry muc 6):
    # "FSCORE robustly adds marginal signal INSIDE the gate (+0.031 pooled)" — never tested inside
    # custom30V, which is RATING-BLIND and FSCORE-blind by construction.
    # PIT: as-of Release_Date, fallback time+45d (SAME convention as BASKET_QFLOOR above).
    FS_MODE = os.environ.get("BASKET_FS_MODE", "").lower()
    FS_W    = float(os.environ.get("BASKET_FS_W", "0.2"))     # blend: additive weight on a [0,2] base
    FS_BAND = int(os.environ.get("BASKET_FS_BAND", "10"))     # tiebreak: half-width around the cut
    FS_T    = float(os.environ.get("BASKET_FS_T", "0.3"))     # wtilt: +/- tilt strength on qmult
    FS_SEED = int(os.environ.get("BASKET_FS_SEED", "0"))      # placebo_tieb: RNG seed
    fs_by_tk = {}
    if FS_MODE:
        if FS_MODE not in ("blend", "tiebreak", "wtilt", "placebo_tieb"):
            raise ValueError(f"BASKET_FS_MODE={FS_MODE} unknown (blend|tiebreak|wtilt|placebo_tieb)")
        if SELECT_MODE_PEEK != "yieldcombo":
            raise ValueError(f"BASKET_FS_MODE only defined for BASKET_SELECT=yieldcombo")
        _fs = bq(f"""SELECT f.ticker, f.time, f.Release_Date, f.FSCORE
FROM tav2_bq.ticker_financial f WHERE f.time <= DATE '{end_date}' AND f.FSCORE IS NOT NULL""")
        _fs["time"] = pd.to_datetime(_fs["time"])
        _fs["eff"] = pd.to_datetime(_fs["Release_Date"]).fillna(_fs["time"] + pd.Timedelta(days=45))
        _fs = _fs.sort_values(["ticker", "eff"])
        fs_by_tk = {tk: (list(g["eff"]), list(g["FSCORE"])) for tk, g in _fs.groupby("ticker")}
        _fslo = max(1, top_n - FS_BAND + 1); _fshi = top_n + FS_BAND
        print(f"  [FSCORE enhancer] mode={FS_MODE}"
              + (f" w={FS_W}" if FS_MODE == "blend" else "")
              + (f" band=ranks {_fslo}-{_fshi} (1-indexed, incl.)" if FS_MODE == "tiebreak" else "")
              + (f" tilt=+/-{FS_T:.0%}" if FS_MODE == "wtilt" else "")
              + f"; {len(fs_by_tk)} tickers, PIT as-of Release_Date (fallback time+45d); "
                "missing FSCORE = NEUTRAL")
    def fscore_asof(tk, d):
        """PIT FSCORE of `tk` as of date `d`; np.nan when nothing released yet (NEUTRAL)."""
        e = fs_by_tk.get(tk)
        if not e: return np.nan
        i = bisect.bisect_right(e[0], pd.Timestamp(d)) - 1
        return float(e[1][i]) if i >= 0 else np.nan
    def _fs_reorder(gated, d, lo, hi):
        """Permute the FSCORE-bearing names inside gated[lo-1:hi] by FSCORE desc, into the slots
        those names already occupy. Names with no PIT FSCORE keep their exact yieldcombo slot
        (fail-open). Ranks outside the band are copied through untouched.
        Deliberately a VERBATIM mirror of _dy_reorder (arm A4) — same fail-open semantics, same
        band-straddles-the-cut placement; only the ordering key differs. Ties on FSCORE (an
        integer 0-9, so ties are COMMON) break on the name's existing yieldcombo standing, i.e.
        a tie changes nothing — the enhancer can only act where FSCORE actually discriminates."""
        band = gated[lo - 1:hi]
        if len(band) < 2:
            return gated
        slots = [i for i, (tk, _) in enumerate(band) if pd.notna(fscore_asof(tk, d))]
        if len(slots) < 2:
            return gated
        if FS_MODE == "placebo_tieb":
            # NULL-DISTRIBUTION CONTROL for "tiebreak". Same band, same slots, same number of
            # names moved — the ONLY difference is that the permutation is RANDOM instead of by
            # FSCORE. If the tiebreak's effect is reproduced here, it is reshuffle luck at the
            # cut line, not information in FSCORE. Seeded per (SEED, date) so every rebal date
            # draws independently yet the whole 48-date path replays exactly (same convention as
            # the file's existing BASKET_DCF_MODE=placebo_random).
            _rng = np.random.default_rng([FS_SEED, pd.Timestamp(d).toordinal()])
            _perm = _rng.permutation(len(slots))
            ranked = [(slots[j], band[slots[j]]) for j in _perm]
        else:
            ranked = sorted(((i, band[i]) for i in slots),
                            key=lambda it: (-fscore_asof(it[1][0], d), it[0]))
        out = list(band)
        for _slot, (_oi, _item) in zip(slots, ranked):
            out[_slot] = _item
        return gated[:lo - 1] + out + gated[hi:]
'''
assert src.count(A_ANCHOR) == 1, "anchor A not unique"
src = src.replace(A_ANCHOR, A_ADD)

# SELECT_MODE is parsed AFTER this point in the file, so peek at the env directly for the guard.
src = src.replace(
    '    FS_MODE = os.environ.get("BASKET_FS_MODE", "").lower()',
    '    SELECT_MODE_PEEK = os.environ.get("BASKET_SELECT", "blend").lower()\n'
    '    FS_MODE = os.environ.get("BASKET_FS_MODE", "").lower()')

# ---------------------------------------------------------------- (B) blend + tiebreak hooks
B_ANCHOR = '''                mos_r = pd.Series({t: dcf_at(t, d)[1] for t, _ in pool}).rank(pct=True).fillna(0.5)
                for t, _ in pool: score[t] += DCF_W * mos_r[t]
            gated = sorted(pool, key=lambda tr: score[tr[0]], reverse=True)
'''
B_ADD = '''                mos_r = pd.Series({t: dcf_at(t, d)[1] for t, _ in pool}).rank(pct=True).fillna(0.5)
                for t, _ in pool: score[t] += DCF_W * mos_r[t]
            if FS_MODE == "blend":
                # additive on the SAME [0,2] scale the yieldcombo score lives on (pe_r + pcf_r), so
                # FS_W is directly readable as "FSCORE share = FS_W/(2+FS_W)". Missing FSCORE -> 0.5
                # mid-rank, identical to the file's existing missing-yield convention 8 lines above.
                fs_r = pd.Series({t: fscore_asof(t, d) for t, _ in pool}).rank(pct=True).fillna(0.5)
                for t, _ in pool: score[t] += FS_W * fs_r[t]
            gated = sorted(pool, key=lambda tr: score[tr[0]], reverse=True)
            if FS_MODE in ("tiebreak", "placebo_tieb"):
                # AFTER the yieldcombo sort, BEFORE the top_n cut — the band straddles the cut line,
                # the only place a tie-break can change a pick.
                gated = _fs_reorder(gated, d, max(1, top_n - FS_BAND + 1), top_n + FS_BAND)
'''
assert src.count(B_ANCHOR) == 1, "anchor B not unique"
src = src.replace(B_ANCHOR, B_ADD)

# ---------------------------------------------------------------- (C) wtilt hook (weights only)
C_ANCHOR = '''        picks = []
        for tk, rt in gated[:top_n]:
            qmult = (QT.get(int(rt), QTILT_MISSING) if (quality == "tilt" and pd.notna(rt)) else
                     (QTILT_MISSING if quality == "tilt" else 1.0))
            picks.append((tk, qmult, rt))
'''
C_ADD = '''        picks = []
        _fs_wt = {}
        if FS_MODE == "wtilt" and gated:
            # MEMBERSHIP UNCHANGED (variant c): the top_n cut is pure yieldcombo. Only the weight
            # each member carries is tilted, via qmult -> the cap-weight base (yest*qmult) that the
            # namecap water-fill then bounds at name_cap. rank_pct is taken WITHIN THE BASKET (the
            # 30 picked names), because the question is "reweight inside the rổ", not "vs the pool".
            _sel = [tk for tk, _rt in gated[:top_n]]
            _fsr = pd.Series({t: fscore_asof(t, d) for t in _sel}).rank(pct=True).fillna(0.5)
            _fs_wt = {t: float(1.0 + FS_T * 2.0 * (_fsr[t] - 0.5)) for t in _sel}
        for tk, rt in gated[:top_n]:
            qmult = (QT.get(int(rt), QTILT_MISSING) if (quality == "tilt" and pd.notna(rt)) else
                     (QTILT_MISSING if quality == "tilt" else 1.0))
            if _fs_wt: qmult = qmult * _fs_wt[tk]
            picks.append((tk, qmult, rt))
'''
assert src.count(C_ANCHOR) == 1, "anchor C not unique"
src = src.replace(C_ANCHOR, C_ADD)

open(DST, "w", encoding="utf-8").write(src)
print(f"wrote {DST} ({len(src.splitlines())} lines)")
