# -*- coding: utf-8 -*-
"""
deposit_fallback_direction_selfcheck.py — selfcheck for the 2026-10-13 fallback-DIRECTION fix in
deposit_rate_vn.effective_deposit_rate() (job Taylor_20261013_163831, user-approved).

Before: a stale (>45d) or unreadable CCTG made the 5 consumers drop to Big-4-only — r goes DOWN,
fair value goes UP, on a feed lapse. After: the last known CCTG value is HELD (+WARNING, label
`cctg_held(...)`); the number never falls below a level already observed.

What this file proves (the consumer call paths themselves — dcf_valuation.discount_rate,
dcf_refresh_gate, custom30_yield_labels._label_one, due_diligence._deposit_rate_pct — are covered
by cctg_deposit_wiring_selfcheck.py §7/§8, updated in the same commit):
  S*  scenario behaviour of the central function (stale hold, 13 kinds of read error, knob, way out)
  H*  HISTORY IS BYTE-IDENTICAL to the pre-change code (PIN_REV) for every asof <= HIST_END, on the
      frozen fixtures AND on a copy of the live CSVs; macro_killswitch_a_status() identical on a
      grid that extends PAST HIST_END (it must not have been touched at all)
  M*  14 source-level mutants, each must turn at least one check red (reversed fallback
      direction on the stale branch = M1, on the error branch = M2)

Both code versions are loaded from SOURCE TEXT into private temp dirs (never via sys.path), so
each has its own isolated `data/` CSV location and nothing here reads or writes the live files.

Run: $DNA_PYEXE deposit_fallback_direction_selfcheck.py [--full-daily]
     and again under `env -u TZ`, `TZ=America/New_York`, `TZ=Pacific/Kiritimati` (§16/§19).
"""
import ast
import hashlib
import importlib.util
import inspect
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PIN_REV = "cce3699d"            # last commit BEFORE the fallback-direction change
HIST_END = "2026-10-13"         # the day the change was written; history = every asof <= this
LIVE_DATA = "/home/trido/thanhdt/WorkingClaude/data"
FULL_DAILY = "--full-daily" in sys.argv

fails = []


def check(name, cond, sink=None):
    if sink is not None:            # mutant run: collect, do not print/record
        if not cond:
            sink.append(name)
        return
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        fails.append(name)


class Pair:
    """One (deposit_rate_vn, cctg_rate_vn) code version, loaded from source text into its own
    temp dir. `with pair:` makes it the pair that `from cctg_rate_vn import ...` resolves to."""

    def __init__(self, dep_src, cctg_src, tag):
        self.dir = tempfile.mkdtemp(prefix=f"fbdir_{tag}_")
        os.makedirs(os.path.join(self.dir, "data"))
        self.mods = {}
        for name, src in (("cctg_rate_vn", cctg_src), ("deposit_rate_vn", dep_src)):
            fp = os.path.join(self.dir, f"{name}.py")
            with open(fp, "w", encoding="utf-8") as fh:
                fh.write(src)
            spec = importlib.util.spec_from_file_location(name, fp)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self.mods[name] = mod
        self.dep, self.cctg = self.mods["deposit_rate_vn"], self.mods["cctg_rate_vn"]

    def __enter__(self):
        self._saved = {n: sys.modules.get(n) for n in self.mods}
        sys.modules.update(self.mods)
        return self

    def __exit__(self, *exc):
        for n, m in self._saved.items():
            if m is None:
                sys.modules.pop(n, None)
            else:
                sys.modules[n] = m

    def set_csv(self, dep_text=None, cctg_text=None):
        for mod, text in ((self.dep, dep_text), (self.cctg, cctg_text)):
            fp = mod._EVENTS_CSV
            if os.path.isdir(fp):
                shutil.rmtree(fp)
            elif os.path.exists(fp):
                os.remove(fp)
            if text is not None:
                with open(fp, "w", encoding="utf-8") as fh:
                    fh.write(text)

    def close(self):
        shutil.rmtree(self.dir, ignore_errors=True)


def with_knob(flag, fn):
    old = os.environ.get("DEPOSIT_RATE_CCTG_OVERLAY")
    if flag is None:
        os.environ.pop("DEPOSIT_RATE_CCTG_OVERLAY", None)
    else:
        os.environ["DEPOSIT_RATE_CCTG_OVERLAY"] = flag
    try:
        return fn()
    finally:
        if old is None:
            os.environ.pop("DEPOSIT_RATE_CCTG_OVERLAY", None)
        else:
            os.environ["DEPOSIT_RATE_CCTG_OVERLAY"] = old


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


CCTG_HDR = "effective_date,cctg_rate,collected_date,source,note\n"
CCTG_GOOD = CCTG_HDR + "2026-10-05,7.4,2026-10-05,t,rebase\n2026-10-12,7.4,2026-10-12,t,same\n"
ERR_ASOF = "2026-10-20"


def scenario_checks(pair, sink=None):
    """All behaviour checks of the central function. sink=None -> print + record; sink=list ->
    collect failed names silently (mutant runs)."""
    dep, cctg = pair.dep, pair.cctg
    cap = _Capture()
    lg = logging.getLogger("deposit_rate_vn")
    lg.addHandler(cap)
    old_level = lg.level
    lg.setLevel(logging.WARNING)

    def det(asof):
        return with_knob("1", lambda: dep.consumer_deposit_rate_detail(asof))

    try:
        with pair:
            # ---- S1/S2: stale hold + the exact boundary (frozen fixtures: CCTG 7.5 @ 2026-09-30)
            pair.set_csv()
            cap.messages.clear()
            s1 = det("2026-11-15")                              # age 46 > 45 -> stale
            check("S1 stale CCTG is HELD at last known 7.5 (not Big-4 6.8)",
                  abs(s1["rate_pct"] - 7.5) < 1e-9, sink)
            check("S1 held value is labelled cctg_held(2026-09-30; cctg_stale: 46d)",
                  s1["rate_source"] == "cctg_held(2026-09-30; cctg_stale: 46d)", sink)
            check("S1 a WARNING saying HOLDING was logged",
                  any("CCTG stale" in m and "HOLDING" in m for m in cap.messages), sink)
            s2 = det("2026-11-14")                              # age 45 -> still fresh
            check("S2 age==45d is still fresh: 7.5, labelled cctg_6m(2026-09-30) (pre-rebase 6M anchor)",
                  abs(s2["rate_pct"] - 7.5) < 1e-9 and s2["rate_source"] == "cctg_6m(2026-09-30)", sink)

            # ---- S3: never below the level already observed, however long the feed stays dark
            days = pd.date_range("2026-09-30", "2028-12-31", freq="7D")
            lo = min(det(str(d.date()))["rate_pct"] for d in days)
            check("S3 with no new data the rate never drops below 7.5 through 2028", lo >= 7.5 - 1e-9, sink)

            # ---- S4: the way out is a newer CONFIRMED row -- which may be lower
            pair.set_csv(cctg_text=CCTG_HDR + "2027-01-10,7.0,2027-01-10,t,down\n")
            s4 = det("2027-01-10")
            check("S4 a newer confirmed CCTG row ends the hold (7.0, fresh 12M label)",
                  abs(s4["rate_pct"] - 7.0) < 1e-9 and s4["rate_source"] == "cctg_12m(2027-01-10)", sink)
            pair.set_csv(cctg_text=CCTG_HDR + "2027-01-10,6.5,2027-01-10,t,below big4\n")
            s4b = det("2027-06-30")                             # stale AND below Big-4
            check("S4 a confirmed CCTG below Big-4 -> plain Big-4 6.8 (no hold, no label)",
                  abs(s4b["rate_pct"] - 6.8) < 1e-9 and s4b["rate_source"] == "big4_12m", sink)

            # ---- S5: read ERRORS hold the last known GOOD row (2026-10-12, 7.4)
            bad_rows = {
                "a out-of-range value (74)": CCTG_GOOD + "2026-10-19,74,2026-10-19,t,typo\n",
                "b unparseable rate (7.4%)": CCTG_GOOD + "2026-10-19,7.4%,2026-10-19,t,typo\n",
                "c unparseable date": CCTG_GOOD + "19/10/2O26,7.9,2026-10-19,t,typo\n",
                "e malformed row (extra fields)": CCTG_GOOD + "2026-10-19,7.9,a,b,c,d,e,f\n",
                "f year-typo row (<= anchor)": CCTG_GOOD + "2025-10-19,9.9,2026-10-19,t,typo\n",
            }
            for label, text in bad_rows.items():
                pair.set_csv(cctg_text=text)
                err = cctg.current_cctg_rate_checked(ERR_ASOF)[2]
                cap.messages.clear()
                r = det(ERR_ASOF)
                check(f"S5{label}: strict loader really errors (fixture is live)", err is not None, sink)
                check(f"S5{label}: HELD at last good row 7.4 (not Big-4 6.8, not the bad row)",
                      abs(r["rate_pct"] - 7.4) < 1e-9, sink)
                check(f"S5{label}: labelled cctg_held(2026-10-12; cctg_unavailable: ...)",
                      r["rate_source"].startswith("cctg_held(2026-10-12; cctg_unavailable: "), sink)
                check(f"S5{label}: a WARNING saying HOLDING was logged",
                      any("CCTG unavailable" in m and "HOLDING" in m for m in cap.messages), sink)

            pair.set_csv(cctg_text="date,rate\n2026-10-05,7.4\n2026-10-12,7.4\n")
            r = det(ERR_ASOF)
            check("S5d wrong header: no CSV row is trustworthy -> held at frozen anchor 7.5",
                  abs(r["rate_pct"] - 7.5) < 1e-9
                  and r["rate_source"].startswith("cctg_held(2026-09-30; cctg_unavailable: "), sink)

            pair.set_csv()
            os.makedirs(cctg._EVENTS_CSV)                       # a directory where the file should be
            r = det(ERR_ASOF)
            check("S5g unreadable file (OSError): held at frozen anchor 7.5",
                  abs(r["rate_pct"] - 7.5) < 1e-9 and r["rate_source"].startswith("cctg_held(2026-09-30; "), sink)

            pair.set_csv(cctg_text=CCTG_GOOD)
            orig = cctg.current_cctg_rate_checked
            cctg.current_cctg_rate_checked = lambda asof=None: (_ for _ in ()).throw(RuntimeError("boom"))
            try:
                r = det(ERR_ASOF)
            finally:
                cctg.current_cctg_rate_checked = orig
            check("S5h the checked reader itself raising: held at 7.4, cause named",
                  abs(r["rate_pct"] - 7.4) < 1e-9 and "boom" in r["rate_source"], sink)

            pair.set_csv(cctg_text=CCTG_GOOD + "2026-12-01,9.0,2026-12-01,t,future\n2026-10-19,74,x,t,typo\n")
            r = det(ERR_ASOF)
            check("S5j a FUTURE-dated good row is not used for a past asof (7.4, not 9.0)",
                  abs(r["rate_pct"] - 7.4) < 1e-9, sink)

            pair.set_csv(cctg_text=CCTG_GOOD + "2026-10-19,74,2026-10-19,t,typo\n")
            orig_lkg = getattr(cctg, "last_known_good_cctg", None)
            cctg.last_known_good_cctg = lambda asof=None: (_ for _ in ()).throw(RuntimeError("lkg down"))
            try:
                r = det(ERR_ASOF)
            finally:
                cctg.last_known_good_cctg = orig_lkg
            check("S5i the last-known lookup itself failing -> frozen in-code anchor 7.5 is HELD (not Big-4), cause named",
                  abs(r["rate_pct"] - 7.5) < 1e-9
                  and r["rate_source"].startswith("cctg_held(2026-09-30; cctg_unavailable: ")
                  and "lkg down" in r["rate_source"], sink)

            # S5k: tz-aware / 'Z' date row must not make the salvage raise (arch-review B1)
            for lbl, bad in (("Z", "2026-10-19T00:00:00Z"), ("+07:00", "2026-10-19T00:00:00+07:00")):
                pair.set_csv(cctg_text=CCTG_GOOD + f"{bad},7.9,2026-10-19,t,tz\n")
                r = det(ERR_ASOF)
                check(f"S5k tz-aware date row ({lbl}) is skipped: HELD at 7.4, not Big-4 6.8",
                      abs(r["rate_pct"] - 7.4) < 1e-9 and r["rate_source"].startswith("cctg_held("), sink)
            # S5l: day-first date is never guessed (12/10/2026 must not become Dec 10 = 8.0)
            pair.set_csv(cctg_text=CCTG_GOOD + "12/10/2026,8.0,2026-10-12,t,dayfirst\n")
            r = det("2026-12-15")
            check("S5l day-first date row is skipped, not guessed (7.4 held, not 8.0)",
                  abs(r["rate_pct"] - 7.4) < 1e-9, sink)
            # S5m (kills X1): error + last good CCTG BELOW Big-4 -> Big-4 6.8, never below it
            pair.set_csv(cctg_text=CCTG_HDR + "2026-10-12,6.5,2026-10-12,t,low\n2026-10-19,74,2026-10-19,t,typo\n")
            r = det(ERR_ASOF)
            check("S5m error + last good CCTG 6.5 < Big-4 6.8 -> 6.8 big4_12m(cctg_unavailable...)",
                  abs(r["rate_pct"] - 6.8) < 1e-9 and r["rate_source"].startswith("big4_12m(cctg_unavailable: "), sink)
            # S5n (kills X2): a row on the frozen-anchor date must not displace the anchor
            pair.set_csv(cctg_text=CCTG_HDR + "2026-09-30,6.9,2026-09-30,t,same-day\n2026-10-19,74,2026-10-19,t,typo\n")
            r = det(ERR_ASOF)
            check("S5n a row dated on the frozen anchor day (6.9) does not displace 7.5",
                  abs(r["rate_pct"] - 7.5) < 1e-9, sink)

            # ---- S6: read error BEFORE anything is known on the CCTG side -> Big-4 (as before)
            pair.set_csv(cctg_text=CCTG_GOOD + "2026-10-19,74,2026-10-19,t,typo\n")
            r = det("2026-09-29")
            check("S6 error + nothing known at/before asof (2026-09-29) -> Big-4 6.8",
                  abs(r["rate_pct"] - 6.8) < 1e-9 and r["rate_source"].startswith("big4_12m(cctg_unavailable: "), sink)

            # ---- S7: rollback knob untouched -- 0 is Big-4-only even while a hold is active
            pair.set_csv()
            k0 = with_knob("0", lambda: dep.consumer_deposit_rate_detail("2026-11-15"))
            check("S7 DEPOSIT_RATE_CCTG_OVERLAY=0 -> Big-4-only 6.8 at a stale date",
                  abs(k0["rate_pct"] - 6.8) < 1e-9 and k0["rate_source"] == "big4_12m(cctg_overlay_disabled)", sink)
            check("S7 knob unset == knob 1 (default on)",
                  with_knob(None, lambda: dep.consumer_deposit_rate("2026-11-15"))
                  == with_knob("1", lambda: dep.consumer_deposit_rate("2026-11-15")), sink)

            # ---- S8: Big-4 above a stale CCTG -> Big-4 drives, no hold involved
            pair.set_csv(dep_text="effective_date,deposit_rate\n2026-10-20,8.0\n")
            r = det("2026-12-30")
            check("S8 Big-4 8.0 > stale CCTG 7.5 -> 8.0, plain big4_12m",
                  abs(r["rate_pct"] - 8.0) < 1e-9 and r["rate_source"] == "big4_12m", sink)

            # ---- S9: kill-switch A stays fail-closed on a stale CCTG (NOT part of this change)
            pair.set_csv(dep_text="effective_date,deposit_rate\n2026-11-10,6.8\n")
            ks = dep.macro_killswitch_a_status("2026-11-15", check_freshness=True)
            check("S9 macro_killswitch_a_status: stale CCTG still ARMED + stale, rate = Big-4 6.8",
                  ks["armed"] is True and ks["stale"] is True and abs(ks["rate"] - 0.068) < 1e-12, sink)

            # ---- S10: asof=None is ICT-today, not host-TZ today (run under 3 TZ)
            pair.set_csv()
            ict_today = str(pd.Timestamp.now(tz="Asia/Ho_Chi_Minh").date())
            check(f"S10 asof=None == asof=ICT today ({ict_today}), whatever the host TZ",
                  det(None) == det(ict_today), sink)
    finally:
        lg.removeHandler(cap)
        lg.setLevel(old_level)
        pair.set_csv()


def _grid(end, start=None):
    if start is not None:
        return [str(d.date()) for d in pd.date_range(start, end, freq="D")]
    if FULL_DAILY:
        return [str(d.date()) for d in pd.date_range("2011-01-01", end, freq="D")]
    g = set(pd.date_range("2011-01-01", "2025-12-31", freq="SMS"))      # 1st + 15th
    g |= set(pd.date_range("2026-01-01", end, freq="D"))
    return [str(d.date()) for d in sorted(d for d in g if d <= pd.Timestamp(end))]


# 2026-10-14 (job Taylor_20261014_135258, user-approved LABEL-only change): a fresh CCTG anchor
# dated >= 2026-10-05 is now labelled "cctg_12m(<date>)" instead of "cctg_6m(<date>)" (series
# rebased to 12M that day). The H-section below must still prove NUMBERS byte-identical to PIN_REV,
# so it folds exactly that rename back before hashing/comparing -- nothing else is normalised.
def _label_norm(text):
    return text.replace("cctg_12m(", "cctg_6m(")


def _code_norm(src):
    """Function source minus its docstring, with the one-line label rename folded back."""
    src = src.replace("cctg_source_label(cctg_date)", 'f"cctg_6m({cctg_date.date()})"')
    fn = ast.parse(textwrap.dedent(src)).body[0]
    if fn.body and isinstance(fn.body[0], ast.Expr) and isinstance(getattr(fn.body[0], "value", None), ast.Constant) \
            and isinstance(fn.body[0].value.value, str):
        fn.body = fn.body[1:]
    return ast.unparse(fn)


def history_fingerprint(pair, end=HIST_END, start=None):
    """Every consumer-path output for every asof <= end, both knob states -> one sha256."""
    dep = pair.dep
    h = hashlib.sha256()
    lg = logging.getLogger("deposit_rate_vn")
    old_level = lg.level
    lg.setLevel(logging.CRITICAL)
    try:
        with pair:
            for a in _grid(end, start):
                row = (a,
                       with_knob("1", lambda: dep.consumer_deposit_rate_detail(a)),
                       with_knob("0", lambda: dep.consumer_deposit_rate_detail(a)),
                       dep.effective_deposit_rate(a, check_freshness=True),
                       dep.effective_deposit_rate(a, check_freshness=False),
                       dep.current_deposit_rate(a))
                h.update(_label_norm(repr(row)).encode("utf-8"))
    finally:
        lg.setLevel(old_level)
    return h.hexdigest()


BIG4_KEPT_FRESH = "effective_date,deposit_rate\n" + "".join(
    f"{d.date()},6.8\n" for d in pd.date_range("2026-07-01", "2027-06-01", freq="MS"))


def killswitch_fingerprint(pair, dep_text=None, cctg_text=None):
    """macro_killswitch_a_status on a grid running PAST HIST_END into stale territory, on the
    given fixtures AND with Big-4 kept fresh by monthly rows -- on the plain fixtures Big-4 and
    CCTG go stale together and `big4_stale` alone forces ARMED, which hides any change on the
    CCTG side of the gate (mutant M10 survived the first version of this check for that reason)."""
    dep = pair.dep
    dates = [str(d.date()) for d in pd.date_range("2011-01-01", "2026-06-01", freq="MS")]
    dates += [str(d.date()) for d in pd.date_range("2026-06-01", "2027-06-30", freq="D")]
    h = hashlib.sha256()
    with pair:
        for dt in (dep_text, BIG4_KEPT_FRESH):
            pair.set_csv(dep_text=dt, cctg_text=cctg_text)
            for a in dates:
                for cf in (True, False):
                    h.update(_label_norm(repr((a, cf, dep.macro_killswitch_a_status(a, check_freshness=cf))))
                             .encode("utf-8"))
    pair.set_csv()
    return h.hexdigest()


def read_here(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return fh.read()


def read_pinned(name):
    """Source text at PIN_REV. `git show <rev>:<path>` resolves from the REPO ROOT (§8c), so the
    prefix of HERE inside the repo is asked from git, not assumed."""
    prefix = subprocess.run(["git", "-C", HERE, "rev-parse", "--show-prefix"],
                            capture_output=True, text=True)
    if prefix.returncode != 0:
        raise RuntimeError(f"git rev-parse failed: {prefix.stderr.strip()}")
    out = subprocess.run(["git", "-C", HERE, "show", f"{PIN_REV}:{prefix.stdout.strip()}{name}"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"git show {PIN_REV}:{name} failed: {out.stderr.strip()}")
    return out.stdout


def live_csv(name):
    fp = os.path.join(LIVE_DATA, name)
    if not os.path.exists(fp):
        return None
    with open(fp, encoding="utf-8") as fh:
        return fh.read()


# ============================================================================== main
NEW_DEP, NEW_CCTG = read_here("deposit_rate_vn.py"), read_here("cctg_rate_vn.py")
new = Pair(NEW_DEP, NEW_CCTG, "new")

print(f"host TZ={os.environ.get('TZ', '<unset>')}  grid={'FULL DAILY' if FULL_DAILY else '1st+15th <2026 + daily 2026'}")
print("\nS — behaviour of the central function (this checkout):")
scenario_checks(new)

print(f"\nH — history byte-identical to {PIN_REV} for every asof <= {HIST_END}:")
try:
    old = Pair(read_pinned("deposit_rate_vn.py"), read_pinned("cctg_rate_vn.py"), "old")
except RuntimeError as exc:
    old = None
    check(f"H0 pinned pre-change source readable ({exc}) -- unreadable is NOT 'clean'", False)
if old is not None:
    check("H0 pinned source really is the pre-change code (no cctg_held in it)",
          "cctg_held" not in inspect.getsource(old.dep) and not hasattr(old.cctg, "last_known_good_cctg"))
    for p in (old, new):
        p.set_csv()
    fo, fn = history_fingerprint(old), history_fingerprint(new)
    print(f"      frozen fixtures  old={fo[:16]}  new={fn[:16]}  ({len(_grid(HIST_END))} asof x 5 outputs)")
    M9_START = "2026-09-01"
    base_hist = history_fingerprint(old, start=M9_START)
    check("H1 frozen fixtures: identical fingerprint", fo == fn)

    dep_live, cctg_live = live_csv("deposit_rate_vn_events.csv"), live_csv("cctg_rate_vn_events.csv")
    if dep_live is None or cctg_live is None:
        print(f"  [SKIP] H2 live-CSV copy: {LIVE_DATA}/*_events.csv not present on this host — NOT verified here")
    else:
        for p in (old, new):
            p.set_csv(dep_text=dep_live, cctg_text=cctg_live)
        fo, fn = history_fingerprint(old), history_fingerprint(new)
        print(f"      live-CSV copy    old={fo[:16]}  new={fn[:16]}")
        check("H2 copy of the LIVE CSVs: identical fingerprint", fo == fn)
        ko, kn = (killswitch_fingerprint(p, dep_live, cctg_live) for p in (old, new))
        check("H3b kill-switch A on live-CSV copy, grid to 2027-06-30: identical", ko == kn)

    for p in (old, new):
        p.set_csv()
    ko, kn = killswitch_fingerprint(old), killswitch_fingerprint(new)
    base_ks = ko
    print(f"      kill-switch A    old={ko[:16]}  new={kn[:16]}  (grid runs to 2027-06-30; frozen + Big-4-kept-fresh)")
    check("H3 macro_killswitch_a_status identical incl. the stale future (frozen fixtures)", ko == kn)

    same_src = [("deposit_rate_vn", n) for n in ("macro_killswitch_a_status", "deposit_events_df", "merge_deposit",
                                                 "current_deposit_rate", "consumer_deposit_rate",
                                                 "effective_deposit_events_df")]
    same_src += [("cctg_rate_vn", n) for n in ("cctg_events_df", "current_cctg_rate", "current_cctg_rate_checked")]
    for modname, fn_name in same_src:
        check(f"H4 {modname}.{fn_name}: source unchanged vs {PIN_REV}",
              _code_norm(inspect.getsource(getattr(old.mods[modname], fn_name)))
              == _code_norm(inspect.getsource(getattr(new.mods[modname], fn_name))))
    check("H4 frozen anchors unchanged (DEPOSIT_EVENTS, CCTG_EVENTS)",
          old.dep.DEPOSIT_EVENTS == new.dep.DEPOSIT_EVENTS and old.cctg.CCTG_EVENTS == new.cctg.CCTG_EVENTS)

    with old:
        o = with_knob("1", lambda: old.dep.consumer_deposit_rate("2026-11-15"))
    with new:
        n = with_knob("1", lambda: new.dep.consumer_deposit_rate("2026-11-15"))
    check(f"H5 the change is real AFTER history ends: 2026-11-15 old={o} -> new={n}", o == 6.8 and n == 7.5)

# ------------------------------------------------------------------------------ mutants
print("\nM — source-level mutants (each must be CAUGHT; a mutant that does not apply is a FAIL):")
MUTANTS = [
    ("M1 REVERSED DIRECTION, stale branch (drop to Big-4 again)", "dep",
     "        rate_pct = cctg_pct\n        if not cctg_stale:\n            rate_source = cctg_source_label(cctg_date)",
     "        if not cctg_stale:\n            rate_pct = cctg_pct\n            rate_source = cctg_source_label(cctg_date)", "S"),
    ("M2 REVERSED DIRECTION, error branch (drop to Big-4 again)", "dep",
     "            rate_pct = held_pct\n", "            rate_pct = big4_pct\n", "S"),
    ("M3 silent hold (stale WARNING removed)", "dep",
     "            _log.warning(\"effective_deposit_rate(asof=%s): CCTG stale (%dd > %dd, last %s) -> \"\n                         \"HOLDING",
     "            _log.debug(\"effective_deposit_rate(asof=%s): CCTG stale (%dd > %dd, last %s) -> \"\n                         \"HOLDING", "S"),
    ("M4 held value mislabelled as fresh", "dep",
     "rate_source = f\"cctg_held({cctg_date.date()}; cctg_stale: {cctg_age}d)\"",
     "rate_source = cctg_source_label(cctg_date)", "S"),
    ("M5 rollback knob ignored", "dep",
     "if os.environ.get(\"DEPOSIT_RATE_CCTG_OVERLAY\", \"1\") == \"0\":",
     "if os.environ.get(\"DEPOSIT_RATE_CCTG_OVERLAY\", \"1\") == \"never\":", "S"),
    ("M6 salvage accepts an out-of-range row", "cctg",
     "if pd.isna(d) or not (RATE_MIN_PCT <= r <= RATE_MAX_PCT) or d <= frozen_max:",
     "if pd.isna(d) or d <= frozen_max:", "S"),
    ("M7 salvage ignores asof (uses a future row)", "cctg",
     "    known = [(d, r) for d, r in known if d <= asof_ts]\n", "", "S"),
    ("M8 salvage returns the OLDEST known row, not the latest", "cctg",
     "d, r = max(enumerate(known), key=lambda t: (t[1][0], t[0]))[1]",
     "d, r = min(enumerate(known), key=lambda t: (t[1][0], t[0]))[1]", "S"),
    ("M9 hold reaches back into history (stale threshold 5d)", "dep",
     "        cctg_stale = check_freshness and cctg_age > stale_days_limit\n        rate_pct = cctg_pct\n",
     "        cctg_stale = check_freshness and cctg_age > 5\n        rate_pct = cctg_pct\n", "H"),
    ("M10 kill-switch A weakened (stale CCTG no longer forces ARMED)", "dep",
     "                if cctg_stale:\n                    cctg_force_armed = True",
     "                if cctg_stale:\n                    cctg_force_armed = False", "K"),
    ("M12 error branch holds a value BELOW Big-4 (comparison dropped)", "dep",
     "        if held_pct is not None and held_pct > big4_pct:\n            rate_pct = held_pct\n            rate_source = f\"cctg_held({held_date.date()}; cctg_unavailable",
     "        if held_pct is not None:\n            rate_pct = held_pct\n            rate_source = f\"cctg_held({held_date.date()}; cctg_unavailable", "S"),
    ("M13 salvage lets a row on/before the frozen anchor date through", "cctg",
     " or d <= frozen_max:\n                        continue", ":\n                        continue", "S"),
    ("M14 salvage reverts to the old loose parse (no strict ISO, compare outside the row guard)", "cctg",
     "                try:\n                    # strict ISO like the loader",
     "                try:\n                    d = pd.to_datetime(row[\"effective_date\"])\n                    r = float(row[\"cctg_rate\"])\n                except (KeyError, TypeError, ValueError):\n                    continue\n                if pd.isna(d) or not (RATE_MIN_PCT <= r <= RATE_MAX_PCT) or d <= frozen_max:\n                    continue\n                known.append((d, r))\n                continue\n                try:\n                    # strict ISO like the loader", "S"),
    ("M11 a CCTG BELOW Big-4 is allowed to drive (rate can fall under Big-4)", "dep",
     "    elif cctg_pct is not None and cctg_pct > big4_pct:\n        cctg_age",
     "    elif cctg_pct is not None and cctg_pct > 0:\n        cctg_age", "S"),
]
for name, which, a, b, kind in MUTANTS:
    src = NEW_DEP if which == "dep" else NEW_CCTG
    if src.count(a) != 1:
        check(f"{name}: mutation applies exactly once (found {src.count(a)})", False)
        continue
    msrc = src.replace(a, b)
    try:
        m = Pair(msrc if which == "dep" else NEW_DEP, msrc if which == "cctg" else NEW_CCTG, "mut")
    except Exception as exc:
        check(f"{name}: mutant source loads ({exc!r})", False)
        continue
    try:
        if kind == "S":
            red = []
            try:
                scenario_checks(m, sink=red)
            except Exception as exc:        # a mutant that crashes the checks is caught too
                red.append(f"exception {exc!r}")
            check(f"{name}: caught by {len(red)} check(s), e.g. {red[0] if red else '-'}", bool(red))
        elif old is None:
            check(f"{name}: needs the pinned source (H0 failed)", False)
        elif kind == "H":
            m.set_csv()
            check(f"{name}: caught by H1 history fingerprint",
                  history_fingerprint(m, start=M9_START) != base_hist)
        else:
            m.set_csv()
            check(f"{name}: caught by H3 kill-switch fingerprint", killswitch_fingerprint(m) != base_ks)
    finally:
        m.close()

new.close()
if old is not None:
    old.close()
print(f"\n{'ALL PASS' if not fails else f'{len(fails)} FAIL'}")
for f in fails:
    print(f"  FAIL: {f}")
sys.exit(1 if fails else 0)
