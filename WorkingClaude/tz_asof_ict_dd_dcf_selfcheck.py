#!/usr/bin/env python3
"""Selfcheck: "today by default" must mean TODAY in ICT (Asia/Ho_Chi_Minh), not the host process
TZ (coding_guidelines §16) -- 4 call sites, job Taylor_20261012_040502:
  dd_order : trading_bot/due_diligence.py::dd_check_for_order   (asof=None)
  dd_run   : trading_bot/due_diligence.py::run_due_diligence    (context without "asof")
  dcf_cli  : dcf_valuation.py  __main__ block                   (no --asof)
  gate     : dcf_refresh_gate.py::_now_ict_date / run_gate      (asof=None)

Method (same family as cctg_deposit_asof_ict_selfcheck.py): a child process pins the clock at the
two instants straddling ICT midnight to the minute (2026-10-11 16:59Z -> want 10-11; 17:00Z ->
want 10-12). The pinned clock is honest about the process TZ: a bare date.today() /
datetime.now() / pd.Timestamp.today() answers in the CHILD's local TZ, a tz-aware now(tz) answers
in tz. The parent runs the child under 5 process TZs itself (unset, UTC, Etc/GMT+12,
Pacific/Kiritimati, Asia/Ho_Chi_Minh), so the verdict does not depend on the TZ or the
wall-clock time this file is started with. Any fixed zone with offset != +7:00 (UTC, Asia/Tokyo,
Asia/Yangon +6:30) and any process-TZ read fails at one of the two instants; Asia/Bangkok (+7,
no DST) is behaviourally identical and passes -- correct, not a gap.

Hermetic: no BigQuery / network / broker / execution dir. due_diligence is cut right below the
date derivation (run_due_diligence / _latest_row stubbed), the dcf_valuation CLI block is
exec'd with fair_value / latest_price / _print_report stubbed, the gate writes to a tmp dir.
Also asserts an EXPLICIT asof passes through untouched at all 4 sites.

Run: $DNA_PYEXE tz_asof_ict_dd_dcf_selfcheck.py   (also runs under system python3)
     ... --dump <TZ|unset>     print the child's raw JSON for one process TZ (main-vs-branch diff)
"""
import json
import os
import subprocess
import sys

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")     # §5b: before anything imports trading_bot

HERE = os.path.dirname(os.path.abspath(__file__))
INSTANTS = (("2026-10-11T16:59:00+00:00", "2026-10-11"), ("2026-10-11T17:00:00+00:00", "2026-10-12"))
EXPLICIT = ("2026-07-21", "2026-10-11", "2026-10-12")
TZS = (None, "UTC", "Etc/GMT+12", "Pacific/Kiritimati", "Asia/Ho_Chi_Minh")
SITES = ("dd_order", "dd_run", "dcf_cli", "gate", "gate_run", "gate_state", "gate_log")

CHILD = r'''
import os
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
import ast, datetime as real_dt, importlib.util, json, sys, tempfile, types
HERE = %(here)r
sys.path.insert(0, HERE)
import pandas as pd
import trading_bot.due_diligence as DD          # first: before any module re-points sys.path


def _load(name):                                 # root modules insert the canonical WORKDIR
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


DV = _load("dcf_valuation")
GATE = _load("dcf_refresh_gate")
for m in (DD, DV, GATE):
    assert os.path.abspath(m.__file__).startswith(HERE + os.sep), m.__file__

EPOCH = [0.0]


class FDate(real_dt.date):
    @classmethod
    def today(cls):
        return real_dt.datetime.fromtimestamp(EPOCH[0]).date()          # process-local, like the real one


class FDateTime(real_dt.datetime):
    @classmethod
    def now(cls, tz=None):
        return real_dt.datetime.fromtimestamp(EPOCH[0], tz)             # tz=None -> process-local naive

    @classmethod
    def today(cls):
        return real_dt.datetime.fromtimestamp(EPOCH[0])

    @classmethod
    def utcnow(cls):
        return real_dt.datetime.fromtimestamp(EPOCH[0], real_dt.timezone.utc).replace(tzinfo=None)


def _ts_now(tz=None):
    if tz is None:
        return pd.Timestamp(real_dt.datetime.fromtimestamp(EPOCH[0]))
    return pd.Timestamp(EPOCH[0], unit="s", tz="UTC").tz_convert(tz)


pd.Timestamp.now = staticmethod(_ts_now)
pd.Timestamp.today = staticmethod(lambda tz=None: _ts_now(tz))

fake_dt = types.ModuleType("datetime")
fake_dt.__dict__.update({k: v for k, v in vars(real_dt).items() if not k.startswith("__")})
fake_dt.date, fake_dt.datetime = FDate, FDateTime
DD.dt = fake_dt
GATE.datetime = FDateTime

cap = {}


def _stub_run(ticker, book=None, context=None, as_dict=False):
    cap["dd_order"] = (context or {}).get("asof")
    return {"has_red_flag": False, "red_flags": []}


def _stub_latest_row(ticker, asof):
    cap["dd_run"] = asof
    return None                                   # -> run_due_diligence returns its no-data dict


def _stub_fair_value(ticker, asof, **kw):
    cap["dcf_cli"] = asof
    return {}


_real_run = DD.run_due_diligence
DD._latest_row = _stub_latest_row
GATE._dep = types.SimpleNamespace(consumer_deposit_rate=lambda asof=None: 6.8)

_tree = ast.parse(open(DV.__file__, encoding="utf-8").read())
_main = [n for n in _tree.body if isinstance(n, ast.If) and "__main__" in ast.unparse(n.test)]
assert len(_main) == 1, "dcf_valuation.py: expected exactly one __main__ block"
_cli = compile(ast.Module(body=_main[0].body, type_ignores=[]), DV.__file__, "exec")


def _desc(v):
    """(type name, 10-char date, exact repr) -- enough to prove value AND kind are unchanged."""
    return [type(v).__name__, str(v)[:10], repr(v)]


def probe(asof):
    """asof=None -> the 4 default paths; else the explicit path. Returns {site: desc}."""
    cap.clear()
    out = {}
    DD.run_due_diligence = _stub_run
    DD.dd_check_for_order("XXX", "BAL", asof)
    out["dd_order"] = _desc(cap["dd_order"])
    DD.run_due_diligence = _real_run
    d = DD.run_due_diligence("XXX", "BAL", {} if asof is None else {"asof": asof}, as_dict=True)
    assert cap["dd_run"] == d["as_of"], (cap["dd_run"], d["as_of"])
    out["dd_run"] = _desc(cap["dd_run"])
    ns = dict(vars(DV))
    ns.update(fair_value=_stub_fair_value, latest_price=lambda *a, **k: 1.0,
              _print_report=lambda r: None, __name__="__main__")
    sys.argv = ["dcf_valuation.py", "XXX"] + ([] if asof is None else ["--asof", asof])
    exec(_cli, ns)
    v = cap["dcf_cli"]
    out["dcf_cli"] = _desc(v) + [str(getattr(v, "tz", None))]
    out["gate"] = _desc(GATE._now_ict_date(asof))
    with tempfile.TemporaryDirectory() as td:
        sp, lp = os.path.join(td, "state.json"), os.path.join(td, "gate.log")
        out["gate_run"] = _desc(GATE.run_gate(asof=asof, state_path=sp, log_path=lp)["date"])
        st = json.load(open(sp))
        out["gate_state"] = _desc(st["last_check_date"]) + [st["last_used_date"]]
        out["gate_log"] = _desc(json.loads(open(lp).read().splitlines()[-1])["date"])
    return out


res = {"pinned": {}, "explicit": {}}
for iso, _want in %(instants)r:
    EPOCH[0] = real_dt.datetime.fromisoformat(iso).timestamp()
    res["pinned"][iso] = probe(None)
for a in %(explicit)r:
    res["explicit"][a] = probe(a)
print(json.dumps(res, sort_keys=True))
''' % {"here": HERE, "instants": INSTANTS, "explicit": EXPLICIT}

N = 0
FAILS = []


def check(label, cond):
    global N
    N += 1
    if not cond:
        FAILS.append(label)
    print(f"  {'ok' if cond else 'FAIL'}: {label}")


def run(tz):
    env = dict(os.environ)
    env["MIKE_BOT_TEST_MODE"] = "1"
    if tz is None:
        env.pop("TZ", None)
    else:
        env["TZ"] = tz
    p = subprocess.run([sys.executable, "-c", CHILD], env=env, capture_output=True, text=True,
                       cwd=HERE)
    assert p.returncode == 0, f"child rc={p.returncode} (TZ={tz})\n{p.stderr[-3000:]}"
    return json.loads(p.stdout.strip().splitlines()[-1])


if len(sys.argv) == 3 and sys.argv[1] == "--dump":
    print(json.dumps(run(None if sys.argv[2] == "unset" else sys.argv[2]), sort_keys=True, indent=1))
    sys.exit(0)

print(f"=== default 'today' anchors to ICT at 4 sites ({sys.executable}) ===")
for tz in TZS:
    o = run(tz)
    tag = tz or "unset"
    for iso, want in INSTANTS:
        for site in SITES:
            check(f"[TZ={tag}] {iso[:16]}Z {site} -> ICT date {want}", o["pinned"][iso][site][1] == want)
        check(f"[TZ={tag}] {iso[:16]}Z gate_state.last_used_date -> ICT date {want}", o["pinned"][iso]["gate_state"][3] == want)
    # kind of the default value is what the callers always got
    p = o["pinned"][INSTANTS[0][0]]
    check(f"[TZ={tag}] dd_order default is a datetime.date", p["dd_order"][0] == "date")
    check(f"[TZ={tag}] dd_run default is a 10-char str", p["dd_run"][0] == "str" and len(p["dd_run"][2]) == 12)
    check(f"[TZ={tag}] dcf_cli default is a tz-naive midnight Timestamp",
          p["dcf_cli"][0] == "Timestamp" and p["dcf_cli"][3] == "None"
          and p["dcf_cli"][2] == "Timestamp('2026-10-11 00:00:00')")
    check(f"[TZ={tag}] gate default is a 10-char str", p["gate"][0] == "str" and len(p["gate"][2]) == 12)
    for a in EXPLICIT:
        e = o["explicit"][a]
        check(f"[TZ={tag}] explicit asof {a} passes through untouched at all sites",
              all(e[s][0] == "str" and e[s][1] == a for s in SITES)
              and e["dd_order"][2] == repr(a) and e["dcf_cli"][2] == repr(a)
              and e["gate_state"][3] == a)

print(f"\n{N - len(FAILS)}/{N} PASS")
if FAILS:
    print("FAILED:")
    for f in FAILS:
        print("  -", f)
    sys.exit(1)
print("ALL PASS")
