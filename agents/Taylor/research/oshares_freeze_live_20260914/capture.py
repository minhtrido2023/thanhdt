"""Chạy selfcheck oshares_live / oshares_pit NẠP TỪ WORKTREE, ghi lại:
  - mọi truy vấn bq (sql -> rows)  [mode=live]  hoặc CHẶN bq (ném lỗi) [mode=blocked]
  - mọi lời gọi TẦNG NGOÀI của oshares_at / _ais_verdicts / oshares_pit / oshares_reconciled
    (args + trạng thái các global bị selfcheck vá + output JSON đầy đủ)
Usage: OSH_WT=<wt>/WorkingClaude python capture.py <live|pit> <live|blocked> <out.json>
"""
import contextlib, io, json, os, subprocess, sys
WT = os.environ["OSH_WT"]
sys.path.insert(0, WT)
which, mode, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
import corp_action_lib as C
assert C.__file__.startswith(WT), C.__file__
BQ_LOG = []
_real_bq = C.bq
_real_run = subprocess.run

def rec_bq(sql, timeout=300):
    if mode == "blocked":
        BQ_LOG.append({"sql": sql, "blocked": True})
        raise RuntimeError("BQ BLOCKED by capture.py (hermetic proof)")
    rows = _real_bq(sql, timeout)
    BQ_LOG.append({"sql": sql, "rows": rows})
    return rows
C.bq = rec_bq
if mode == "blocked":   # chặn cả đường vòng: ai gọi thẳng CLI `bq` cũng nổ
    def guarded_run(cmd, *a, **k):
        if isinstance(cmd, (list, tuple)) and cmd and os.path.basename(str(cmd[0])) == "bq":
            BQ_LOG.append({"cli": list(map(str, cmd))[:4], "blocked": True})
            raise RuntimeError("bq CLI BLOCKED by capture.py")
        return _real_run(cmd, *a, **k)
    subprocess.run = guarded_run

import oshares_live as L
assert L.__file__.startswith(WT)
assert L.bq is rec_bq
CALLS, depth = [], [0]

def state():
    return {"serve": list(L._SERVE_AIS_VERDICTS), "age": L.FIN_FALLBACK_MAX_AIS_AGE_DAYS,
            "verdicts_fn": getattr(L._ais_verdicts, "__name__", "?"),
            "fwd_fn": getattr(L._forward_absorption_test, "__name__", "?")}

def wrap(name, fn, argfmt):
    def w(*a, **k):
        top = depth[0] == 0
        depth[0] += 1
        try:
            r = fn(*a, **k); err = None
        except Exception as e:                       # noqa: BLE001
            r, err = None, f"{type(e).__name__}: {e}"
        finally:
            depth[0] -= 1
        if top:
            CALLS.append({"fn": name, "args": argfmt(a, k), "state": state(),
                          "out": json.loads(json.dumps(r, default=str, sort_keys=True)), "err": err})
        if err:
            raise RuntimeError(err)
        return r
    w.__name__ = fn.__name__
    return w

fmt_at = lambda a, k: {"tickers": a[0], "asof": a[1], "live": k.get("live", False),
                       "cached": bool(k.get("_cache") or (len(a) > 2 and a[2]))}
fmt_v = lambda a, k: {"ticker": a[1], "asof": a[2], "n_corp": len(a[0])}
L.oshares_at = wrap("oshares_at", L.oshares_at, fmt_at)
L._ais_verdicts = wrap("_ais_verdicts", L._ais_verdicts, fmt_v)
if which == "pit":
    import oshares_pit as P
    assert P.__file__.startswith(WT)
    P.oshares_at = L.oshares_at
    P._ais_verdicts = L._ais_verdicts
    fmt_p = lambda a, k: {"tickers": a[0], "asof": a[1], "fb": a[2],
                          "cached": (k.get("cache") if "cache" in k else (a[3] if len(a) > 3 else None)) is not None}
    P.oshares_pit = wrap("oshares_pit", P.oshares_pit, fmt_p)
    P.oshares_reconciled = wrap("oshares_reconciled", P.oshares_reconciled, fmt_p)
    target = P
else:
    target = L
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    try:
        rc = target._selfcheck()
    except Exception as e:                           # noqa: BLE001
        print(f"SELFCHECK CRASH {type(e).__name__}: {e}"); rc = 98
text = buf.getvalue()
json.dump({"which": which, "mode": mode, "rc": rc, "stdout": text, "bq": BQ_LOG, "calls": CALLS},
          open(out_path, "w"), ensure_ascii=False, default=str)
print(text[-3000:])
print(f"[capture] which={which} mode={mode} rc={rc} bq_calls={len(BQ_LOG)} calls={len(CALLS)} "
      f"blocked={sum(1 for b in BQ_LOG if b.get('blocked'))}")
