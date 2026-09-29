"""Dựng fixture ĐÓNG BĂNG cửa sổ tối thiểu từ BQ đã ghi (base_*_live.json) và CHỨNG MINH tương đương
bằng REPLAY từng lời gọi tầng ngoài (cùng trạng thái global đã vá) — full-dict output phải trùng khít.
Usage: OSH_WT=... python freeze.py  -> windows.json, fixture_rows.json, replay_report.json
"""
import json, os, re, sys
WT = os.environ["OSH_WT"]; sys.path.insert(0, WT)
import oshares_live as L, oshares_pit as P
assert L.__file__.startswith(WT) and P.__file__.startswith(WT)
REAL_V, REAL_FWD = L._ais_verdicts, L._forward_absorption_test
CAPS = [json.load(open(f)) for f in ("base_live_live.json", "base_pit_live.json")]

def key_c(r):  # khoá ngày của dòng corp — đúng ORDER BY của _fetch
    return r["exright_date"] or r["effective_date"] or ""

# 1) gom dòng thô theo mã, kiểm nhất quán giữa các lần hỏi trong CÙNG phiên
Q, C, QUNTIL, DUP = {}, {}, {}, []
for cap in CAPS:
    for b in cap["bq"]:
        s = " ".join(b["sql"].split()); tk = re.search(r"ticker IN \(([^)]*)\)", s)
        if not tk or "rows" not in b: continue
        tks = [t.strip('"') for t in tk.group(1).split(",")]
        if "ticker_financial" in s:
            until = re.search(r'time <= DATE "([^"]+)"', s).group(1)
            for t in tks:
                rows = [r for r in b["rows"] if r["ticker"] == t]
                if t in Q:
                    lo, hi = sorted([(QUNTIL[t], Q[t]), (until, rows)], key=lambda x: x[0])
                    if [r for r in hi[1] if r["time"] <= lo[0]] != lo[1]: DUP.append(("Q", t, until))
                    if until > QUNTIL[t]: Q[t], QUNTIL[t] = rows, until
                else:
                    Q[t], QUNTIL[t] = rows, until
        elif 'event_code IN ("ISS", "AIS")' in s:
            for t in tks:
                rows = [r for r in b["rows"] if r["ticker"] == t]
                if t in C and sorted(map(json.dumps, C[t])) != sorted(map(json.dumps, rows)):
                    DUP.append(("C", t))
                C.setdefault(t, rows)
REAL = set(Q) | set(C)
print("mã thật:", sorted(REAL), "| lệch nội phiên:", DUP)

# 2) danh sách lời gọi để replay
CALLS = []
for cap in CAPS:
    for c in cap["calls"]:
        a = c["args"]
        tks = [a["ticker"]] if c["fn"] == "_ais_verdicts" else a["tickers"]
        # KHP/ASM/MCH: oshares_at của khối K dùng fixture DỰNG TAY (inline) — không phải feed BQ.
        # Riêng `_ais_verdicts` KHP của bất biến 10b thì đọc feed BQ thật (n_corp = cả feed KHP).
        inline = set(tks) & {"KHP", "ASM", "MCH"} and not (
            c["fn"] == "_ais_verdicts" and a["ticker"] == "KHP" and a["n_corp"] == len(C["KHP"]))
        if tks and all(t in REAL for t in tks) and not inline:
            CALLS.append((cap["which"], c, tks))
print("lời gọi replay:", len(CALLS))

def boom(*_a, **_k): raise RuntimeError("cổng chứng nhận sập giả lập")

def norm(x): return json.loads(json.dumps(x, default=str, sort_keys=True))

def cache_for(tks, fq, fc):
    s = sorted(set(tks))
    return ([r for t in s for r in fq[t]], [r for t in s for r in fc[t]])

def replay(c, tks, fq, fc):
    s, a = c["state"], c["args"]
    L._SERVE_AIS_VERDICTS = tuple(s["serve"]); L.FIN_FALLBACK_MAX_AIS_AGE_DAYS = s["age"]
    L._ais_verdicts = boom if s["verdicts_fn"] == "_boom_verdicts" else REAL_V
    L._forward_absorption_test = REAL_FWD
    try:
        cache = cache_for(tks, fq, fc)
        if c["fn"] == "oshares_at":
            r = L.oshares_at(a["tickers"], a["asof"], _cache=cache, live=a["live"])
        elif c["fn"] == "_ais_verdicts":
            r = REAL_V(cache[1], a["ticker"], a["asof"])
        else:
            fb = {k: (float("nan") if v == "NaN" else v) for k, v in a["fb"].items()}
            r = getattr(P, c["fn"])(a["tickers"], a["asof"], fb, cache=cache)
        return norm(r), None
    except Exception as e:  # noqa
        return None, f"{type(e).__name__}: {e}"
    finally:
        L._SERVE_AIS_VERDICTS = ("OK", "NO_PRIOR"); L.FIN_FALLBACK_MAX_AIS_AGE_DAYS = 90
        L._ais_verdicts = REAL_V

def slice_out(c, out, t):
    if c["fn"] == "_ais_verdicts" or out is None: return out
    return out.get(t)

def eq_for(t, fq, fc, calls=None):
    bad = []
    for which, c, tks in (calls or CALLS):
        if t is not None and t not in tks: continue
        out, err = replay(c, tks, fq, fc)
        want = c["out"]
        ts = [t] if t is not None else ([None] if c["fn"] == "_ais_verdicts" else tks)
        for tt in ts:
            if (err is None) != (c["err"] is None) or slice_out(c, out, tt) != slice_out(c, want, tt):
                bad.append((which, c["fn"], c["args"].get("tickers") or c["args"].get("ticker"),
                            c["args"]["asof"], tt)); break
    return bad

# 3) replay với dòng ĐẦY ĐỦ phải tái lập 100% (độ trung thực của chính bộ replay)
full_bad = eq_for(None, Q, C)
print("replay FULL lệch:", full_bad)
assert not full_bad, "replay không trung thực — dừng"
assert L._SERVE_AIS_VERDICTS == ("OK", "NO_PRIOR"), L._SERVE_AIS_VERDICTS

# 4) tìm cửa sổ LIỀN NGÀY nhỏ nhất cho từng mã (không cắt tỉa lẻ từng dòng):
#    trần = asof lớn nhất mã đó được hỏi; sàn corp rồi sàn quý = ngày MUỘN NHẤT còn tái lập khít.
def ok(t, fq, fc): return not eq_for(t, fq, fc)
WIN, FQ, FC = {}, dict(Q), dict(C)
for t in sorted(REAL):
    asofs = [c["args"]["asof"] for _, c, tks in CALLS if t in tks]
    if not asofs: continue
    hi = max(asofs)
    tq = dict(FQ, **{t: [r for r in Q[t] if r["time"] <= hi]})
    tc = dict(FC, **{t: [r for r in C[t] if key_c(r) <= hi]})
    if ok(t, tq, tc): FQ, FC = tq, tc
    else: hi = None
    clo = None
    for d in sorted({key_c(r) for r in FC[t]}, reverse=True):
        tc = dict(FC, **{t: [r for r in FC[t] if key_c(r) >= d]})
        if ok(t, FQ, tc): clo, FC = d, tc; break
    qlo = None
    for d in sorted({r["time"] for r in FQ[t]}, reverse=True):
        tq = dict(FQ, **{t: [r for r in FQ[t] if r["time"] >= d]})
        if ok(t, tq, FC): qlo, FQ = d, tq; break
    if qlo is None:   # có thể không cần dòng quý nào
        tq = dict(FQ, **{t: []})
        if ok(t, tq, FC): qlo, FQ = "(none)", tq
    assert ok(t, FQ, FC), t
    WIN[t] = {"hi": hi, "corp_from": clo, "q_from": qlo, "n_q": len(FQ[t]), "n_c": len(FC[t]),
              "n_q_full": len(Q[t]), "n_c_full": len(C[t]), "n_calls": len(asofs)}
    print(t, WIN[t], flush=True)

final_bad = eq_for(None, FQ, FC)
print("replay FIXTURE (mọi mã cùng lúc) lệch:", final_bad)
json.dump(WIN, open("windows.json", "w"), indent=1)
json.dump({"Q": FQ, "C": FC}, open("fixture_rows.json", "w"), ensure_ascii=False)
json.dump({"full_replay_mismatch": full_bad, "fixture_replay_mismatch": final_bad,
           "n_calls": len(CALLS), "intra_run_feed_diffs": DUP, "windows": WIN},
          open("replay_report.json", "w"), indent=1, ensure_ascii=False)
