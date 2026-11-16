#!/usr/bin/env python3
"""Selfcheck ai_momentum_daily.py — fake BQ + fake M1/M2 (khong goi mang, khong ton token) + MUTATION test tren chinh source.
Chay duoi 3 TZ:  env -u TZ python3 selfcheck_ai_momentum.py ; TZ=UTC ... ; TZ=America/New_York ...   (coding_guidelines §16/§23)"""
import os, sys, json, time, tempfile, types, datetime, shutil, atexit, subprocess, multiprocessing as mp, importlib.util
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import ai_momentum_daily as REAL
SRC = (HERE / "ai_momentum_daily.py").read_text()
_TMPS = []
def mk(prefix="am_sc_"): d = tempfile.mkdtemp(prefix=prefix); _TMPS.append(d); return d      # selfcheck chi don thu muc CUA MINH
atexit.register(lambda: [shutil.rmtree(d, ignore_errors=True) for d in _TMPS])
T = "2026-11-13"; WK = ["2026-11-09", "2026-11-10", "2026-11-11", "2026-11-12", "2026-11-13"]   # cung tuan ISO

class HarnessError(Exception): pass
def mutant(old, new, name="mut"):
    src = SRC
    for o, n in (zip(old, new) if isinstance(old, list) else [(old, new)]):
        if o not in src: raise HarnessError(f"mutation target khong ton tai: {o[:60]!r}")      # KHONG duoc tinh la 'killed'
        src = src.replace(o, n, 1)
    mod = types.ModuleType(name); mod.__file__ = str(HERE / "ai_momentum_daily.py")
    sys.modules[name] = mod; exec(compile(src, mod.__file__, "exec"), mod.__dict__); return mod

def cand(tk, liq=10.0, **kw):
    d = dict(ticker=tk, mom20=0.3, idio20=0.2, volr=2.0, liq_bn=liq, route="COMPOUNDER", rating=3, rt_time="2026-10-01", route_ret20_med=0.05,
             route_n=100, pct_in_route=0.95, icb="8000", icb_ret20_med=0.04, icb_n=50, vn20=0.01); d.update(kw); return d
def valid_m1(tk, T_, view="CONT", drv="EARNINGS", ev_date=None):
    return {"driver_class": drv, "evidence": [{"claim": "x", "source": "stats", "date": ev_date or T_}], "what_market_prices_in": "a",
            "invalidation": "b", "view_20s": view, "view_60s": "NO_VIEW", "confidence": 0.4}

class Env:
    """Dung fake cho 1 module m. cands_by_date: {T: [cand,...]}; elig_extra: dong lich su BQ them. BQ gia lap: cac ngay co trong cands_by_date
    < T tu dong thanh (ticker,ngay) du dieu kien trong [T-200,T-1] (y nhu sql_eligible_range). m1_fn(tk,T)->dict|str; m2_fn(stage,packet,m1)->dict."""
    def __init__(self, m, cands_by_date, m1_fn=None, m2_fn=None, news=None, elig_extra=None, fresh=None):
        self.m, self.cd, self.calls, self.news, self.extra, self.fresh = m, cands_by_date, [], news or [], elig_extra or [], fresh
        self.tmp = mk(); self.bq_calls = []; self.cur_T = None
        def bq(sql):
            self.bq_calls.append(sql[:20])
            if sql.startswith("/* FRESHNESS */"):
                return [self.fresh if self.fresh is not None else {"tk": self.cur_T, "up": self.cur_T, "up_n": "340", "pv_n": "340", "pv_cov": "340"}]
            if sql.startswith("/* ELIG_RANGE */"):
                return self.extra + [{"ticker": c["ticker"], "time": d, "liq_bn": c["liq_bn"]} for d, cs in self.cd.items() if d < self.cur_T for c in cs]
            if "PERCENTILE_CONT" in sql: return self.cd.get(self.cur_T, [])
            if "ticker_financial" in sql: return [{"ticker": c["ticker"], "quarter": "2026Q3", "Release_Date": "2026-10-20", "NP_P0": "1", "NP_P4": "1",
                    "Revenue_P0": "1", "Revenue_YoY_P0": "0.1", "GPM_P0": "0.2", "PE": "10", "PB": "1", "ROE_Trailing": "0.1"} for cs in self.cd.values() for c in cs]
            if "stock_news" in sql: return self.news
            raise AssertionError("SQL la: " + sql[:60])
        def m1_run(system, user, mode):
            pk = json.JSONDecoder().raw_decode(user.split("GOI:\n", 1)[1])[0]; tk, Tn = pk["ticker"], pk["T"]; self.calls.append(("m1", tk))
            r = (m1_fn or (lambda tk_, T_: valid_m1(tk_, T_)))(tk, Tn)
            return (r if isinstance(r, str) else json.dumps(r)), {"cost_usd": 0.01, "usage": {"input_tokens": 1, "output_tokens": 1, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}, "models": ["fake"]}
        m.BQ = bq; m.M1_RUN = m1_run; m.M2 = m2_fn or (lambda st, p, m1=None: {"status": "FAIL", "reason": "off"}); m.IS_TRADING_DAY = lambda d: d.weekday() < 5
    def day(self, d, mode="retro", dry=False):
        self.cur_T = d
        return self.m.run_day(d, mode, self.tmp, dry, ff=[])
    def rows(self): return self.m.Ledger(Path(self.tmp) / "ai_momentum_retro.jsonl").read()
    def ids(self): return [r["event_id"] for r in self.rows()]

# ---------------- tests (m -> bool; True = hanh vi dung) ----------------
def t_no_double_append(m):
    e = Env(m, {T: [cand("AAA"), cand("BBB", 5)]}); e.day(T); n1 = len(e.rows()); c1 = len(e.calls); e.day(T)
    return n1 == 2 and len(e.rows()) == 2 and len(e.calls) == c1 == 2
def _w(path): m_ = REAL; led = m_.Ledger(path); led.append({"event_id": "X_1", "ticker": "X", "T": "2026-11-13", "status": "processed", "mode": "retro"})
def t_ledger_append_twice(m):
    led = m.Ledger(Path(mk()) / "l.jsonl"); r = {"event_id": "E", "ticker": "X", "T": T, "status": "processed", "mode": "retro"}
    return led.append(r) is True and led.append(dict(r)) is False and len(led.read()) == 1
def t_parallel_append(m):
    p = Path(mk()) / "l.jsonl"; led = m.Ledger(p)
    ps = [mp.Process(target=led.append, args=({"event_id": "E", "ticker": "X", "T": T, "status": "processed", "mode": "retro"},)) for _ in range(6)]
    [x.start() for x in ps]; [x.join() for x in ps]; return len(led.read()) == 1
def t_md5_tamper(m):
    p = Path(mk()) / "l.jsonl"; led = m.Ledger(p); led.append({"event_id": "E", "ticker": "X", "T": T, "status": "processed", "mode": "retro"})
    p.write_text(p.read_text().replace('"X"', '"Y"'))
    try: led.read(); return False
    except RuntimeError: return True
def t_no_outcome_in_packet(m):
    c = cand("AAA", ex20=0.99, ex60=0.88, r20=0.77, profit_1M=0.66, c21=123456.0)
    p = m.build_packet(T, c, [], [], False); s = json.dumps(p)
    ks = m._all_keys(p)
    return set(p) == m.PACKET_KEYS and not (m.FORBIDDEN_KEYS & ks) and all(x not in s for x in ("0.99", "0.88", "0.77", "0.66", "123456"))
def t_sql_pit(m):
    sqls = [m.sql_candidates(T), m.sql_fin(T, ["AAA"]), m.sql_news(T, ["AAA"]), m.sql_freshness(T)]
    rg = m.sql_eligible_range(T)       # co LEAD(r.time) chi de tim rating ke tiep (khong phai gia tuong lai); khong LEAD tren Close
    return all("LEAD(" not in s and "profit_" not in s and "ticker_prune" not in s for s in sqls) and "universe_pit" in sqls[0] \
        and 'DATE(n.ingested_at, "Asia/Ho_Chi_Minh") <= DATE' in sqls[2] and "universe_pit" in rg and "ticker_prune" not in rg and "profit_" not in rg \
        and "LEAD(t." not in rg and 'DATE_SUB(DATE "2026-11-13", INTERVAL 1 DAY)' in rg and rg.count("INTERVAL 1 DAY") == 2 \
        and all(x.lstrip().startswith("/*") for x in (sqls[3], rg))        # `bq query` coi '-- ...' dau cau la co => comment kieu /* */
def t_news_pit(m):
    rows = [{"ticker": "AAA", "public_date": "2026-11-10", "public_datetime": "x", "title": "ok", "matched_event_codes": "DIV", "ingested_date": "2026-11-12"},
            {"ticker": "AAA", "public_date": "2026-11-10", "public_datetime": "x", "title": "LATE_INGEST", "matched_event_codes": "DIV", "ingested_date": "2026-11-14"},
            {"ticker": "AAA", "public_date": "2026-11-14", "public_datetime": "x", "title": "FUTURE_PUB", "matched_event_codes": "DIV", "ingested_date": "2026-11-12"}]
    p = m.build_packet(T, cand("AAA"), [], rows, False); ts = [n["title"] for n in p["news_le_T"]]
    return ts == ["ok"] and "ingested_date" in p["news_le_T"][0] and "public_date" in p["news_le_T"][0]
def t_fin_pit(m):
    rows = [{"ticker": "AAA", "quarter": "q", "Release_Date": d, **{k: "1" for k in ("NP_P0", "NP_P4", "Revenue_P0", "Revenue_YoY_P0", "GPM_P0", "PE", "PB", "ROE_Trailing")}} for d in ("2026-10-20", "2026-11-14")]
    return [f["Release_Date"] for f in m.build_packet(T, cand("AAA"), rows, [], False)["financials_released_le_T"]] == ["2026-10-20"]
def t_m2_exception_failopen(m):
    def boom(st, p, m1=None): raise ValueError("deepseek 500")
    e = Env(m, {T: [cand("AAA")]}, m2_fn=boom); e.day(T); r = e.rows()[0]
    return r["m2_status"] == "FAIL" and "ValueError" in r["m2_reason"] and r["m1_status"] == "OK" and r["final"]["view_20s"] == "CONT"
def t_m2_fail_status(m):
    e = Env(m, {T: [cand("AAA")]}); e.day(T); r = e.rows()[0]
    return r["m2_status"] == "FAIL" and r["final"]["view_20s"] == r["b1"]["view_20s"] and r["final"]["flipped_20s"] is False
def t_m2_ok_rebuttal(m):
    def m2(st, p, m1=None): return {"status": "OK", "data": {"x": 1} if st == "blind" else {"missed": [{"item": "i"}], "disagree": []}}
    def m1f(tk, T_):
        o = valid_m1(tk, T_); 
        if not hasattr(m1f, "n"): m1f.n = 0
        m1f.n += 1
        if m1f.n >= 2: o.update(view_20s="REV", rebuttal_accepted=1, rebuttal_rejected=0)
        return o
    e = Env(m, {T: [cand("AAA")]}, m1_fn=m1f, m2_fn=m2); e.day(T); r = e.rows()[0]
    return r["m2_status"] == "OK" and r["b1"]["view_20s"] == "CONT" and r["final"]["view_20s"] == "REV" and r["final"]["flipped_20s"] is True
def t_schema_strict(m):
    bad_keys = {"driver_class": "UNKNOWN", "evidence": [{"ref": "stats", "note": "x", "date": T}], "what_market_prices_in": "a", "invalidation": "b", "view_20s": "NO_VIEW", "view_60s": "NO_VIEW", "confidence": .1}
    extra = valid_m1("A", T); extra["caveats"] = "x"
    late = valid_m1("A", T, ev_date="2026-11-14")
    s = m.SCHEMA["round1"]
    return bool(m.validate(bad_keys, s)) and bool(m.validate(extra, s)) and not m.validate(valid_m1("A", T), s) and m.evidence_dates_ok(late, T) is False
def t_m1_fail_recorded(m):
    e = Env(m, {T: [cand("AAA")]}, m1_fn=lambda tk, T_: "khong phai json"); e.day(T); r = e.rows()[0]
    badk = {"driver_class": "UNKNOWN", "evidence": [{"ref": "stats", "note": "x", "date": T}], "what_market_prices_in": "a", "invalidation": "b",
            "view_20s": "NO_VIEW", "view_60s": "NO_VIEW", "confidence": .1}      # JSON hop le nhung SAI ten khoa (loi that cua P0)
    e2 = Env(m, {T: [cand("AAA")]}, m1_fn=lambda tk, T_: badk); e2.day(T); r2 = e2.rows()[0]
    return r["m1_status"] == "FAIL" and r["m1_error"] and r["m2_status"] == "SKIPPED" and len(e.calls) == 2 and r2["m1_status"] == "FAIL" and "missing" in r2["m1_error"]
def t_capacity(m):
    cs = [cand(f"T{i:02d}", liq=100 - i) for i in range(12)]
    e = Env(m, {WK[0]: cs, WK[1]: [cand("ZZZ", 999)]}); o = e.day(WK[0]); o2 = e.day(WK[1]); rows = e.rows()
    sk = [r["ticker"] for r in rows if r["status"] == "skipped_capacity"]
    return len(o["processed"]) == 10 and sorted(o["skipped_capacity"]) == ["T10", "T11"] and o2["processed"] == [] and "ZZZ" in sk \
        and sum(r["status"] == "processed" for r in rows) == 10
def t_capacity_resets_next_week(m):
    cs = [cand(f"T{i:02d}", liq=100 - i) for i in range(10)]
    e = Env(m, {WK[0]: cs, "2026-11-16": [cand("NEXT")]}); e.day(WK[0])
    o = e.day("2026-11-16"); return o["processed"] == ["NEXT"]
def t_cooldown(m):
    seed = {"CLOSE": [datetime.date(2026, 9, 20)], "OLD": [datetime.date(2026, 6, 1)], "SAMEQ": [datetime.date(2026, 10, 2)], "FAR": [datetime.date(2026, 5, 1)], "Q": [datetime.date(2026, 8, 10)]}
    ex = [{"ticker": k, "time": str(v[0]), "liq_bn": 1.0} for k, v in seed.items()]
    e = Env(m, {T: [cand("OLD"), cand("SAMEQ"), cand("FAR"), cand("Q"), cand("NEW"), cand("CLOSE")]}, elig_extra=ex); o = e.day(T)
    # OLD: 165 ngay & khac quy (Q2 vs Q4) -> OK ; SAMEQ: 42 ngay -> loai ; FAR OK ; Q: 95 ngay, khac quy (Q3 vs Q4) -> OK ; NEW OK
    return sorted(o["processed"]) == ["FAR", "NEW", "OLD", "Q"]
def t_cooldown_same_quarter(m):   # >90 ngay nhung cung quy duong lich (vd 2026-10-01 vs ...): dung ngay 2026-01-01 vs 2026-04-... khong cung quy; test truc tiep
    h = {"A": [datetime.date(2026, 7, 1)]}   # 2026-07-01 -> 09-30 = 91 ngay (>90) nhung CUNG quy => loai; 10-01 khac quy => duoc
    return m.cooldown_ok("A", datetime.date(2026, 9, 30), h) is False and m.cooldown_ok("A", datetime.date(2026, 10, 1), h) is True
def t_live_guard(m):
    e = Env(m, {T: [cand("A")]})
    e.cur_T = T
    try: m.run_day(T, "live", e.tmp, True, ff=[]); return False
    except SystemExit: return True
def t_dry_run_no_write(m):
    e = Env(m, {T: [cand("A")]}); o = e.day(T, dry=True)
    return o["processed"] == ["A"] and e.calls == [] and not list(Path(e.tmp).glob("*.jsonl")) and not (Path(e.tmp) / "packets_retro").exists()
def t_dd_flag(m):
    return m.dd_flag_of("NKG", T, []) and m.dd_flag_of("ZZZ", T, [{"ticker": "ZZZ", "severity": "exclude", "date": "2026-01-01"}]) \
        and not m.dd_flag_of("ZZZ", T, [{"ticker": "ZZZ", "severity": "exclude", "date": "2026-12-01"}])
def _rows_for_score(m, n_dir, n_nv=0):
    rows, out = [], {}
    for i in range(n_dir + n_nv):
        d = datetime.date(2026, 1, 1) + datetime.timedelta(days=i * 4); eid = f"S{i}_{d}"; v = ("CONT" if i % 2 else "REV") if i < n_dir else "NO_VIEW"
        rows.append({"event_id": eid, "ticker": f"S{i}", "T": str(d), "status": "processed", "mode": "live", "m1_status": "OK", "m2_status": "FAIL", "protocol_md5": m.PROTOCOL_MD5,
                     "m1_round1": {"evidence": [{}], "driver_class": "EARNINGS" if i % 3 else "UNKNOWN"}, "b1": {"view_20s": v}, "final": {"driver_class": "EARNINGS", "view_20s": v, "flipped_20s": False},
                     "usage": [{"cost_usd": 0.01}], "challenge": None})
        out[eid] = {"ex20": 0.01 * ((i % 7) - 3), "ex60": 0.02 * ((i % 5) - 2)}
    return rows, out
def t_scorer_no_peek(m):
    rows, out = _rows_for_score(m, 79, 40); r = m.score_report(rows, out, "2026-12-31")
    return "effects" not in r and r["N_dir_scored"] == 79 and r["N_scored"] == 119 and r["G_proc"]["n_processed"] == 119
def t_scorer_look(m):
    rows, out = _rows_for_score(m, 80, 10); r = m.score_report(rows, out, "2026-12-31")
    return r.get("look") == "L1" and "effects" in r and r["N_dir_scored"] == 80
def t_scorer_ignores_unscored(m):
    rows, out = _rows_for_score(m, 85); out = {k: v for i, (k, v) in enumerate(out.items()) if i < 70}
    r = m.score_report(rows, out, "2026-12-31"); return r["N_scored"] == 70 and "effects" not in r
def t_prereg_params(m):
    s = m.sql_candidates(T)
    return (m.V3["mom20"], m.V3["idio20"], m.V3["volr"], m.V3["liq_bn"], m.V3["rating_max"], m.V3["cap_week"], m.V3["cooldown_days"]) == (0.15, 0.1, 1.2, 1.0, 4, 10, 90) \
        and all(x in s for x in ("mom20>=0.15", "idio20>=0.1 ", "volr>=1.2", "liq_bn>=1.0", "rating<=4")) \
        and not any(x in s for x in ("mom20>=0.2", "idio20>=0.15", "volr>=1.5", "liq_bn>=3")) and m.CAP_WEEK == 10 and m.COOLDOWN_DAYS == 90
def t_prereg_stamp(m):
    cs = [cand(f"T{i:02d}", liq=100 - i) for i in range(12)]
    e = Env(m, {T: cs}); e.day(T); rows = e.rows()
    return len(rows) == 12 and {r["status"] for r in rows} == {"processed", "skipped_capacity"} \
        and all(r.get("prereg_version") == "v3.2" and r.get("prereg_md5") == m.PREREG_MD5 and r.get("protocol_md5") == m.PROTOCOL_MD5 and len(r["protocol_md5"]) == 32 for r in rows) \
        and m.PREREG_MD5 == m._md5f(HERE / "PREREG_v3_2.md") and m.PROTOCOL_MD5 == m._md5f(HERE / "PREREG_v3_2.md5")
def _lock_dir(tamper=None, drop=None, tamper_const=False):
    d = Path(mk()); old = m_ = None
    for f in (*REAL.LOCKED_FILES, "PREREG_v3_2.md5"): shutil.copy(HERE / f, d / f)
    if tamper: (d / tamper).write_text((d / tamper).read_text() + " ")
    if drop: (d / drop).unlink()
    if tamper_const: (d / "PREREG_v3_2.md5").write_text((d / "PREREG_v3_2.md5").read_text().replace("CONST_PROTOCOL", "CONST_PROTOCOLX"))
    return d
def _loads(m, d):
    old = m.HERE; m.HERE = d
    try:
        _, lock, _ = m._load_locked(); m._check_const(lock); return "ok"
    except SystemExit: return "exit"
    except Exception as e: return type(e).__name__          # file thieu => loi, KHONG fallback ''/{}
    finally: m.HERE = old
def t_prereg_lock(m):
    res = [_loads(m, _lock_dir())] + [_loads(m, _lock_dir(tamper=f)) for f in REAL.LOCKED_FILES] + [_loads(m, _lock_dir(tamper_const=True))]
    miss = [_loads(m, _lock_dir(drop=f)) for f in ("prompt_M1_v2.md", "schema_M2.json", "prompt_M2_blind.md")]
    return res[0] == "ok" and all(x == "exit" for x in res[1:]) and all(x != "ok" for x in miss)
def t_protocol_nonempty(m): return len(m.M1_SYSTEM) > 200 and len(m.REBUT) > 20 and bool(m.SCHEMA) and bool(m.M2_SCHEMA) and set(m.M2_PROMPT) == {"blind", "challenge"}
def t_ticker_sens(m):
    rows, out = _rows_for_score(m, 80, 10); r = m.score_report(rows, out, "2026-12-31"); ef = r.get("effects", {}); ts = ef.get("T1_ticker_sensitivity")
    return bool(ts) and ts["role"] == "descriptive_not_in_BH_family" and ts["n_tickers"] == 80 and ts["n_first"] == 80 and len(ts["boot_ci95"]) == 2 \
        and ts["boot_ci95"][0] <= ts["boot_ci95"][1] and set(k for k in ef if k.startswith("T")) <= {"T1", "T2", "T3", "T1_ticker_sensitivity"}
def t_scorer_ignores_other_prereg(m):
    rows, out = _rows_for_score(m, 80, 10)
    for r in rows[:30]: r["protocol_md5"] = "0" * 32
    r = m.score_report(rows, out, "2026-12-31"); return r["N_scored"] == 60 and r["G_proc"]["n_processed"] == 60
def t_today_ict(m):
    real_dt = m.dt
    class F(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            b = datetime.datetime(2026, 11, 15, 18, 0, tzinfo=datetime.timezone.utc)   # 01:00 ICT ngay 16
            return b.astimezone(tz) if tz else b.astimezone().replace(tzinfo=None)
    m.dt = types.SimpleNamespace(datetime=F, date=datetime.date, timedelta=datetime.timedelta)
    try: return m.today_ict() == datetime.date(2026, 11, 16)
    finally: m.dt = real_dt


# ---------------- M2 adapter (second_opinion.sh raw) ----------------
SENT = "SENTINEL_M1_KET_LUAN_XYZ"
def _pk(): return {"event_id": "AAA_" + T, "ticker": "AAA", "T": T, "stats": {}, "sector_context": {}, "financials_released_le_T": [], "news_le_T": []}
def _blind_ok(): return {"event_id": "AAA_" + T, "blind_driver": "UNKNOWN", "blind_view_20s": "NO_VIEW", "blind_view_60s": "NO_VIEW", "evidence": []}
def _chal_ok(): return {"event_id": "AAA_" + T, "missed": [], "disagree": []}
def _fake_run(m, rc=0, text=None, log=None, exc=None):
    def run(pf, rj, tx, timeout=None):
        if log is not None: log.append({"prompt": Path(pf).read_text(), "timeout": timeout})
        if exc: raise exc
        Path(rj).write_text('{"ev":1}\n')
        if text is not None: Path(tx).write_text(text if isinstance(text, str) else json.dumps(text))
        return rc, "second_opinion(raw): model=X attempts=1 rc=%d" % rc
    return run
def t_m2a_ok_and_prompt(m):
    log = []; m.M2_RUN = _fake_run(m, 0, _blind_ok(), log); os.environ.pop("AI_MOMENTUM_M2", None)
    r = m.m2_adapter("blind", _pk())
    pr = log[0]["prompt"]
    log2 = []; m.M2_RUN = _fake_run(m, 0, _chal_ok(), log2); m.m2_adapter("challenge", _pk(), {"driver_class": "UNKNOWN"})
    hint_ok = '"blind_driver"' in pr and "NARRATIVE_ONLY" in pr and '"m1_field"' in log2[0]["prompt"] and '"item"' in log2[0]["prompt"]
    return hint_ok and r["status"] == "OK" and m.NO_TOOL_LINE in pr and "KHONG goi tool nao" in pr and log[0]["timeout"] >= 200 and "AAA_" + T in pr and r["raw_text"]
def t_m2a_fail_modes(m):
    os.environ.pop("AI_MOMENTUM_M2", None); ok = True
    for rc in (10, 11, 12, 2):
        m.M2_RUN = _fake_run(m, rc, ""); r = m.m2_adapter("blind", _pk()); ok &= (r["status"] == "FAIL" and f"exit_{rc}" in r["reason"])
    m.M2_RUN = _fake_run(m, 0, "khong phai json {"); r = m.m2_adapter("blind", _pk()); ok &= (r["status"] == "FAIL" and r["reason"].startswith("parse_fail") and bool(r["raw_text"]))
    m.M2_RUN = _fake_run(m, 0, dict(_blind_ok(), blind_view_20s="MOON")); r = m.m2_adapter("blind", _pk()); ok &= (r["status"] == "FAIL" and r["reason"].startswith("schema"))
    m.M2_RUN = _fake_run(m, 0, dict(_blind_ok(), event_id="ZZZ_x")); r = m.m2_adapter("blind", _pk()); ok &= (r["status"] == "FAIL")
    m.M2_RUN = _fake_run(m, exc=m.subprocess.TimeoutExpired("x", 1)); r = m.m2_adapter("blind", _pk()); ok &= (r["status"] == "FAIL" and "timeout" in r["reason"])
    return bool(ok)
def t_m2a_blind_before_and_no_m1(m):
    log = []; os.environ.pop("AI_MOMENTUM_M2", None)
    def run(pf, rj, tx, timeout=None):
        pr = Path(pf).read_text(); log.append(pr)
        Path(rj).write_text("{}\n"); Path(tx).write_text(json.dumps(_blind_ok() if len(log) == 1 else _chal_ok())); return 0, ""
    m.M2_RUN = run; m.M2 = m.m2_adapter
    r = m.run_m2(_pk(), {"driver_class": SENT})
    return r["m2_status"] == "OK" and len(log) == 2 and SENT not in log[0] and SENT in log[1] and "PHAN BIEN" in log[1].upper() + "PHAN BIEN" and "MÙ" in log[0] and r["m2_raw"]["blind"] and r["m2_raw"]["challenge"]
def t_m2a_e2e_failopen(m):
    os.environ.pop("AI_MOMENTUM_M2", None)
    for rc in (10, 11, 12):
        m.M2_RUN = _fake_run(m, rc, ""); e = Env(m, {T: [cand("AAA")]}); m.M2 = m.m2_adapter; e.day(T); r = e.rows()[0]
        if not (r["m2_status"] == "FAIL" and r["m1_status"] == "OK" and f"exit_{rc}" in r["m2_reason"] and r["final"]["flipped_20s"] is False and "m2_raw" in r): return False
    return True
def t_m2a_schema_boolean(m):
    os.environ.pop("AI_MOMENTUM_M2", None)
    good = dict(_chal_ok(), missed=[{"item": "i", "source": "s", "date": "2026-11-13", "verifiable": True}], disagree=[{"m1_field": "f", "why": "w", "source": "s", "verifiable": False}])
    m.M2_RUN = _fake_run(m, 0, good); a = m.m2_adapter("challenge", _pk(), {"x": 1})
    bad = dict(good, missed=[{"item": "i", "source": "s", "date": "d", "verifiable": "yes"}]); m.M2_RUN = _fake_run(m, 0, bad); b = m.m2_adapter("challenge", _pk(), {"x": 1})
    inv = dict(good, missed=[{"claim": "i", "source": "s", "date": "d", "verifiable": True}]); m.M2_RUN = _fake_run(m, 0, inv); c = m.m2_adapter("challenge", _pk(), {"x": 1})   # ten truong bia (ca that 16/11)
    return a["status"] == "OK" and b["status"] == "FAIL" and c["status"] == "FAIL"
def t_m2a_off_switch(m):
    os.environ["AI_MOMENTUM_M2"] = "off"
    try: return m.m2_adapter("blind", _pk())["reason"] == "adapter_disabled"
    finally: os.environ.pop("AI_MOMENTUM_M2", None)
def t_m2a_bin_in_own_worktree(m):
    return (m._repo_root() / "bin" / "second_opinion.sh").is_file() and Path(m._repo_root()).resolve() == HERE.parents[3]


# ---------------- v3.2 (arch-review vong 2) ----------------
def _cp(stdout="", rc=0, stderr=""): return subprocess.CompletedProcess(["claude"], rc, stdout, stderr)
class _FakeSub:
    """Thay m.subprocess: run() lan luot tra/nem cac phan tu cua `script`; ghi lai cmd."""
    def __init__(self, script): self.script, self.cmds = list(script), []; self.TimeoutExpired = subprocess.TimeoutExpired
    def run(self, cmd, **kw):
        self.cmds.append((cmd, kw)); x = self.script.pop(0) if len(self.script) > 1 else self.script[0]
        if isinstance(x, Exception): raise x
        return x
def _claude_ok(result):
    return _cp(json.dumps({"is_error": False, "result": result, "total_cost_usd": 0.01, "usage": {"input_tokens": 1, "output_tokens": 1}, "modelUsage": {"claude-sonnet": {}}}))
def t_infra_stop_no_write_and_resume(m):
    """B1: loi ha tang o su kien thu 2 => su kien 1 ghi, su kien 2 KHONG ghi dong nao, run_day bao infra_stop; chay lai sau khi 'sua' => ghi du, khong goi lai su kien 1."""
    st = {"down": True}
    def m1f(tk, T_):
        if tk == "BBB" and st["down"]: raise m.InfraError("claude khong chay duoc: FileNotFoundError")
        return valid_m1(tk, T_)
    e = Env(m, {T: [cand("AAA", 10), cand("BBB", 5), cand("CCC", 1)]}, m1_fn=m1f); o = e.day(T)
    r1 = e.ids(); c1 = len(e.calls)
    st["down"] = False; o2 = e.day(T)
    return r1 == ["AAA_" + T] and o["infra_stop"] and "BBB" in o["infra_stop"] and o2["infra_stop"] is None and e.ids() == ["AAA_" + T, "BBB_" + T, "CCC_" + T] \
        and [c[1] for c in e.calls[c1:]] == ["BBB", "CCC"] and all(r["m1_status"] == "OK" for r in e.rows())
def t_infra_real_claude_errors(m):
    """run_claude_m1 that (subprocess gia): FileNotFoundError/Timeout/rc!=0/stdout rac/is_error auth|usage|rate => InfraError; max-turns => RuntimeError (noi dung)."""
    real = m.subprocess; out = []
    try:
        for x, want in [(FileNotFoundError("claude"), m.InfraError), (subprocess.TimeoutExpired("claude", 1), m.InfraError), (_cp("", 2, "boom"), m.InfraError), (_cp("khong json"), m.InfraError),
                        (_cp(json.dumps({"is_error": True, "result": "Claude AI usage limit reached"})), m.InfraError), (_cp(json.dumps({"is_error": True, "result": "Not logged in - please login"})), m.InfraError),
                        (_cp(json.dumps({"is_error": True, "result": "Error: Reached max turns (8)"})), RuntimeError),
                        # R3-B: rc!=0 + JSON hop le subtype max-turns/budget => noi dung (RuntimeError), KHONG ha tang
                        (_cp(json.dumps({"is_error": True, "subtype": "error_max_turns", "num_turns": 9}), 1), RuntimeError),
                        (_cp(json.dumps({"is_error": True, "subtype": "error_max_budget_usd", "total_cost_usd": 0.5}), 1), RuntimeError),
                        (_cp(json.dumps({"is_error": True, "subtype": "error_max_turns", "result": "usage limit reached"}), 1), m.InfraError),
                        (_cp(json.dumps({"is_error": False, "subtype": "success"}), 1), m.InfraError)]:
            m.subprocess = _FakeSub([x])
            try: m.run_claude_m1("S", "U", "retro"); out.append(False)
            except m.InfraError as ex: out.append(want is m.InfraError)
            except RuntimeError as ex: out.append(want is RuntimeError)
            except Exception: out.append(False)
        m.subprocess = _FakeSub([_claude_ok("{}")]); txt, meta = m.run_claude_m1("SYS", "USR", "live"); fs = m.subprocess
        out.append(txt == "{}" and fs.cmds[0][0] == m.m1_argv("live", "SYS") and fs.cmds[0][1]["input"] == "USR")
    finally: m.subprocess = real
    return all(out) and len(out) == 12
def t_infra_cli_recovers_same_day(m):
    """B1 mutant: FileNotFoundError that chay qua run_claude_m1 -> run_day; sau khi 'cai lai CLI' chay lai ghi duoc su kien."""
    real = m.subprocess
    try:
        e = Env(m, {T: [cand("AAA")]}); m.M1_RUN = m.run_claude_m1
        m.subprocess = _FakeSub([FileNotFoundError("claude")]); o = e.day(T); none_written = e.rows() == [] and bool(o["infra_stop"])
        m.subprocess = _FakeSub([_claude_ok(json.dumps(valid_m1("AAA", T)))]); o2 = e.day(T)
        return none_written and e.ids() == ["AAA_" + T] and e.rows()[0]["m1_status"] == "OK" and o2["infra_stop"] is None
    finally: m.subprocess = real
def t_exit_codes(m):
    """B5: main() map ngoai le -> exit code rieng; infra_stop => 5."""
    real = m.run_day; got = {}
    try:
        for name, exc, want in [("nt", m.NotTradingDay("x"), 3), ("dn", m.DataNotReady("x"), 4), ("busy", m.Busy("x"), 6), ("infra", m.InfraError("x"), 5), ("other", ValueError("x"), 1)]:
            def boom(*a, _e=exc, **k): raise _e
            m.run_day = boom
            import io, contextlib
            with contextlib.redirect_stderr(io.StringIO()): got[name] = m.main(["--date", T, "--mode", "retro", "--ledger-dir", mk()])
            ok = got[name] == want
            if not ok: return False
        m.run_day = lambda *a, **k: {"infra_stop": "AAA: x"}
        import io, contextlib
        with contextlib.redirect_stdout(io.StringIO()): r5 = m.main(["--date", T, "--mode", "retro", "--ledger-dir", mk()])
        m.run_day = lambda *a, **k: {"infra_stop": None}
        with contextlib.redirect_stdout(io.StringIO()): r0 = m.main(["--date", T, "--mode", "retro", "--ledger-dir", mk()])
        return r5 == 5 and r0 == 0
    finally: m.run_day = real
def t_not_trading_day(m):
    """B5: exit 3 TRUOC khi cham BQ; ham that: T7/CN/le (2026-09-02) khong phai, thu 2 binh thuong la ngay giao dich."""
    e = Env(m, {"2026-11-14": [cand("A")]}); m.IS_TRADING_DAY = lambda d: False; e.cur_T = "2026-11-14"
    try: m.run_day("2026-11-14", "retro", e.tmp, False, ff=[]); return False
    except m.NotTradingDay: pass
    real = m.is_trading_day
    return e.bq_calls == [] and not real(datetime.date(2026, 11, 14)) and not real(datetime.date(2026, 11, 15)) and not real(datetime.date(2026, 9, 2)) and real(datetime.date(2026, 11, 16))
def t_freshness_depth(m):
    """B6/R3: MAX(time) dung nhung ti le ma in_universe phien truoc co dong ticker tai T thap => DataNotReady, KHONG ghi, KHONG goi M1.
    Thu Hai (ticker tang dan trong tuan roi tut) khong con bi tu choi vi so dong tho."""
    full = {"tk": T, "up": T, "up_n": "340", "pv_n": "340", "pv_cov": "340"}
    bad = [dict(full, pv_cov="40"), dict(full, up_n="0"), dict(full, tk="2026-11-12"), dict(full, up=None), dict(full, pv_cov=None), dict(full, pv_n="")]
    ok = True
    for fr in bad:
        e = Env(m, {T: [cand("AAA")]}, fresh=fr)
        try: e.day(T); ok = False
        except m.DataNotReady as ex: ok &= (str(ex).count("T=") >= 1 and "23:45" not in str(ex))
        ok &= (e.rows() == [] and e.calls == [] and not list(Path(e.tmp).glob("*.jsonl")))
    f = m.freshness_problem
    ok &= f(full, T) is None and f(dict(full, pv_cov="323", pv_n="340"), T) is None and f(dict(full, pv_cov="949", pv_n="1000"), T) is not None and f(dict(full, pv_cov="950", pv_n="1000"), T) is None
    # R3: sql dung in_universe phien truoc + join ticker tai T (mutant: bo in_universe / <=T)
    q = m.sql_freshness(T)
    ok &= (q.count("u.in_universe") >= 2 and "u.time < DATE" in q and "JOIN tkT" in q and "t.time = DATE" in q)
    return ok
def t_hist_deterministic_vs_ledger(m):
    """B2: cooldown/cap khong phu thuoc ledger. Cung BQ, ledger co dong la/khong co => cung ke hoach; ledger rong sau kill => van dung cap tuan."""
    cs = [cand(f"T{i:02d}", liq=100 - i) for i in range(12)]
    e1 = Env(m, {WK[0]: cs[:6], WK[1]: cs[6:]}); e1.day(WK[0]); o1 = e1.day(WK[1])       # BQ-elig gia lap: 6 su kien thu 2 => used=6 => con room 4
    e2 = Env(m, {WK[0]: cs[:6], WK[1]: cs[6:]}); e2.cur_T = WK[1]                        # ledger RONG + dong la (nhu chua tung chay WK[0])
    e2.m.Ledger(Path(e2.tmp) / "ai_momentum_retro.jsonl").append({"event_id": "ZZZ_old", "ticker": "ZZZ", "T": WK[0], "status": "processed", "mode": "retro"})
    o2 = e2.day(WK[1])
    return o1["processed"] == o2["processed"] == [f"T{i:02d}" for i in range(6, 10)] and o1["n_used_week_before"] == o2["n_used_week_before"] == 6
def t_replay_greedy(m):
    h, u = m.replay_history([{"ticker": "X", "time": "2026-07-01", "liq_bn": 1}, {"ticker": "X", "time": "2026-09-30", "liq_bn": 1}, {"ticker": "X", "time": "2026-10-01", "liq_bn": 1},
                             {"ticker": "X", "time": "2026-10-05", "liq_bn": 1}, {"ticker": "Y", "time": "2026-11-12", "liq_bn": 1}], datetime.date(2026, 11, 13))
    return h["X"] == [datetime.date(2026, 7, 1), datetime.date(2026, 10, 1)] and h["Y"] == [datetime.date(2026, 11, 12)] and u == 1
def t_replay_ignores_T_and_future(m):
    """Dong o ngay T (hoac sau) khong duoc vao lich su/cap: 10 ung vien ngay T phai du 10 cho."""
    ex = [{"ticker": "Q", "time": T, "liq_bn": 99}, {"ticker": "R", "time": "2026-11-14", "liq_bn": 99}]
    e = Env(m, {T: [cand(f"T{i:02d}", liq=100 - i) for i in range(10)]}, elig_extra=ex); o = e.day(T)
    h, u = m.replay_history(ex, datetime.date(2026, 11, 13))
    return len(o["processed"]) == 10 and h == {} and u == 0
def t_cooldown_from_prev_day(m):
    """Su kien hom truoc (BQ) chan cung ma hom sau (cung quy, <90 ngay) du ledger chua tung ghi gi."""
    e = Env(m, {WK[0]: [cand("PREV")], WK[1]: [cand("PREV"), cand("OTHER", 1)]}); e.cur_T = WK[1]; o = e.day(WK[1])
    return o["processed"] == ["OTHER"]
def t_rating_fin_news_pit(m):
    Td = "2026-11-13"
    return f'r.time <= DATE "{Td}"' in m.sql_candidates(Td) and f'f.Release_Date <= DATE "{Td}"' in m.sql_fin(Td, ["AAA"]) \
        and f'AND DATE "{Td}"' in m.sql_news(Td, ["AAA"]) and "2099" not in m.sql_candidates(Td) + m.sql_fin(Td, ["AAA"]) + m.sql_news(Td, ["AAA"]) \
        and f'r.time <= DATE_SUB(DATE "{Td}", INTERVAL 1 DAY)' in m.sql_eligible_range(Td)
def t_m1_content_checks(m):
    """evidence date > T va event_id lech di qua call_m1 => m1_status FAIL (ghi dong, khong phai infra)."""
    e = Env(m, {T: [cand("AAA")]}, m1_fn=lambda tk, T_: valid_m1(tk, T_, ev_date="2026-11-14")); e.day(T); r1 = e.rows()[0]
    e2 = Env(m, {T: [cand("AAA")]}, m1_fn=lambda tk, T_: dict(valid_m1(tk, T_), event_id="ZZZ_" + T)); e2.day(T); r2 = e2.rows()[0]
    return r1["m1_status"] == "FAIL" and "date > T" in r1["m1_error"] and r2["m1_status"] == "FAIL" and "event_id" in r2["m1_error"]
def t_m1_argv(m):
    rt, lv = m.m1_argv("retro", "SYS"), m.m1_argv("live", "SYS")
    def nxt(c, k): return c[c.index(k) + 1]
    return nxt(rt, "--tools") == "" and "WebSearch" not in rt and "--allowedTools" not in rt and nxt(rt, "--setting-sources") == "" and nxt(rt, "--system-prompt") == "SYS" \
        and nxt(lv, "--tools") == "WebSearch" and nxt(lv, "--allowedTools") == "WebSearch" and nxt(lv, "--setting-sources") == "" \
        and all(k in c for c in (rt, lv) for k in ("--max-turns", "--max-budget-usd", "--strict-mcp-config", "--no-session-persistence")) and nxt(lv, "--max-turns") == "8"
def t_m2_dates(m):
    os.environ.pop("AI_MOMENTUM_M2", None)
    chk = lambda st, obj: (setattr(m, "M2_RUN", _fake_run(m, 0, obj)), m.m2_adapter(st, _pk(), {"x": 1} if st == "challenge" else None)["status"])[1]
    return chk("blind", dict(_blind_ok(), evidence=["news 2026-11-12"])) == "OK" and chk("blind", dict(_blind_ok(), evidence=["news 2026-11-14"])) == "FAIL" \
        and chk("challenge", dict(_chal_ok(), missed=[{"item": "i", "source": "s", "date": T, "verifiable": True}])) == "OK" \
        and chk("challenge", dict(_chal_ok(), missed=[{"item": "i", "source": "s", "date": "2026-11-14", "verifiable": True}])) == "FAIL" \
        and chk("challenge", dict(_chal_ok(), missed=[{"item": "i", "source": "s", "date": "gan day", "verifiable": True}])) == "FAIL"
def t_m2_record_and_cmd(m):
    """c: model M2 tuong minh + retries + tran ngoai >= (retries+1)*timeout; ledger ghi m2_model + duoi stderr; Popen qua tran => killpg + TimeoutExpired; TMPDIR trong thu muc tam."""
    os.environ.pop("AI_MOMENTUM_M2", None)
    cap = {}
    class P:
        def __init__(s, cmd, **kw): cap["cmd"], cap["kw"] = cmd, kw; s.pid = 4242; s.returncode = 0
        def communicate(s, timeout=None):
            cap["timeout"] = timeout
            if cap.get("hang"): cap["hang"] = False; raise subprocess.TimeoutExpired("x", timeout)
            return "", "second_opinion(raw): model=M attempts=1 rc=0"
    real_sub, real_kp = m.subprocess, m.os.killpg; killed = []
    m.subprocess = types.SimpleNamespace(Popen=P, PIPE=-1, TimeoutExpired=subprocess.TimeoutExpired); m.os.killpg = lambda pid, sig: killed.append(pid)
    try:
        d = Path(mk()); rc, tail = m.run_second_opinion(d / "p.md", d / "r.jsonl", d / "t.txt")
        cmd = cap["cmd"]; flag = lambda k: cmd[cmd.index(k) + 1]
        ok = rc == 0 and "attempts=1" in tail and flag("--model") == m.M2_MODEL and flag("--retries") == str(m.M2_RETRIES) and flag("--timeout") == str(m.M2_TIMEOUT) \
            and cap["timeout"] == m.M2_OUTER >= (m.M2_RETRIES + 1) * m.M2_TIMEOUT + 5 and cap["kw"]["env"]["TMPDIR"] == str(d) and cap["kw"]["start_new_session"] is True
        cap["hang"] = True
        try: m.run_second_opinion(d / "p.md", d / "r.jsonl", d / "t.txt"); ok = False
        except subprocess.TimeoutExpired: ok &= killed == [4242]
    finally: m.subprocess, m.os.killpg = real_sub, real_kp
    m.M2_RUN = _fake_run(m, 0, _blind_ok()); m.M2 = m.m2_adapter
    r = m.run_m2(_pk(), {"driver_class": "UNKNOWN"})      # challenge se loi schema (blind_ok) => FAIL, nhung ledger van phai co model + log
    return ok and r["m2_model"] == m.M2_MODEL and "blind" in r["m2_log"] and "exit" not in str(r["m2_reason"]) and r["m2_raw"]["blind"]
def t_m2_fail_reason_has_stderr(m):
    os.environ.pop("AI_MOMENTUM_M2", None); m.M2_RUN = _fake_run(m, 10, ""); r = m.m2_adapter("blind", _pk())
    return r["status"] == "FAIL" and "exit_10" in r["reason"] and "model=X attempts=1" in r["reason"] and "model=X" in r["stderr_tail"]
def t_t3_only_m2_ok(m):
    import pandas as pd
    rows = [{"T": f"2026-{(i % 8) + 1:02d}-{(i % 20) + 1:02d}", "ticker": f"S{i}", "ex20": 0.01 * ((i % 7) - 3), "ex60": 0.02 * ((i % 5) - 2), "v20": "CONT" if i % 2 else "REV",
             "driver": "EARNINGS", "b1_v20": "REV" if i % 2 else "CONT"} for i in range(80)]
    none = m.effects(pd.DataFrame([dict(r, m2_ok=False) for r in rows])); some = m.effects(pd.DataFrame([dict(r, m2_ok=(i < 30)) for i, r in enumerate(rows)]))
    return "T3" not in none and "T3" in some and "T1" in none
def t_run_lock_busy(m):
    e = Env(m, {T: [cand("AAA")]}); e.cur_T = T
    with m.run_lock(e.tmp):
        try: e.day(T); return False
        except m.Busy: pass
    o = e.day(T); return e.calls == [("m1", "AAA")] and o["written"] == ["AAA_" + T]
def t_m2_fail_streak(m):
    mk_ = lambda s_: {"status": "processed", "mode": "live", "m1_status": "OK", "m2_status": s_}
    return m.m2_fail_streak([mk_("OK"), mk_("FAIL"), mk_("FAIL")]) == 2 and m.m2_fail_streak([mk_("FAIL"), mk_("OK")]) == 0 and m.m2_fail_streak([]) == 0 \
        and m.m2_fail_streak([mk_("FAIL"), {"status": "processed", "mode": "live", "m1_status": "FAIL", "m2_status": "SKIPPED"}]) == 1
def t_default_ledger_dir(m):
    real = m.run_day; got = {}
    def spy(T_, mode, ld, *a, **k): got["ld"] = ld; return {"infra_stop": None}
    m.run_day = spy
    try:
        import io, contextlib
        with contextlib.redirect_stdout(io.StringIO()): m.main(["--date", T, "--mode", "retro"])
    finally: m.run_day = real
    return got["ld"] == str(m._repo_root() / "data" / "ai_momentum") and str(m._repo_root()) == str(HERE.parents[3])
def t_outcomes_ruleset(m):
    old = m.V3; m.V3 = dict(old, universe_ruleset=7)
    try: return "ruleset_version=7" in m.sql_outcomes([("AAA", T)]) and "ruleset_version=1" not in m.sql_outcomes([("AAA", T)])
    finally: m.V3 = old
def t_kill_resume_midday(m):
    """Giet giua ngay (InfraError sau 3 su kien) roi chay lai: du 10 processed, khong trung, cap tuan khong bi dem hai lan."""
    cs = [cand(f"T{i:02d}", liq=100 - i) for i in range(12)]; st = {"n": 0}
    def m1f(tk, T_):
        st["n"] += 1
        if st["n"] == 4: raise m.InfraError("kill")
        return valid_m1(tk, T_)
    e = Env(m, {WK[0]: cs}, m1_fn=m1f); o = e.day(WK[0]); o2 = e.day(WK[0]); rows = e.rows()
    ids = e.ids()
    return o["infra_stop"] and len(ids) == len(set(ids)) and sum(r["status"] == "processed" for r in rows) == 10 and sum(r["status"] == "skipped_capacity" for r in rows) == 2 and len(e.calls) == 11 and o2["infra_stop"] is None

# ---------------- R3 (D-a/c/d): test cho mutant song ----------------
def t_r3_rebuttal_infra_not_swallowed(m):
    """Phan bien M1 (vong 2) gap InfraError => dung luot, KHONG ghi dong, khong nuot."""
    def m2(st, p, m1=None): return {"status": "OK", "data": {"x": 1} if st == "blind" else {"missed": [{"item": "i"}], "disagree": []}}
    n = {"k": 0}
    def m1f(tk, T_):
        n["k"] += 1
        if n["k"] >= 2: raise m.InfraError("claude overloaded 529")
        return valid_m1(tk, T_)
    e = Env(m, {T: [cand("AAA")]}, m1_fn=m1f, m2_fn=m2); o = e.day(T)
    return bool(o["infra_stop"]) and e.rows() == []
def t_r3_scorer_m2_ok_real(m):
    """score_report: m2_ok phai phan anh m2_status that. Toan FAIL => khong co T3; co M2 OK => co T3."""
    rows, out = _rows_for_score(m, 80, 10)
    none = m.score_report(rows, out, "2026-12-31").get("effects", {})
    for r in rows[:40]: r["m2_status"] = "OK"; r["m2_raw"] = {}
    some = m.score_report(rows, out, "2026-12-31").get("effects", {})
    return "T1" in none and "T3" not in none and "T3" in some
def t_r3_cooldown_boundary(m):
    """Dung 90 ngay + khac quy: CHUA du (> khong phai >=); 91 ngay moi du. Ca cooldown_ok lan replay_history."""
    h = {"A": [datetime.date(2026, 6, 30)]}   # Q2; +90 = 2026-09-28 (Q3)
    a = m.cooldown_ok("A", datetime.date(2026, 9, 28), h) is False and m.cooldown_ok("A", datetime.date(2026, 9, 29), h) is True
    hh, _ = m.replay_history([{"ticker": "X", "time": "2026-06-30", "liq_bn": 1}, {"ticker": "X", "time": "2026-09-28", "liq_bn": 1}], datetime.date(2026, 11, 13))
    hh2, _ = m.replay_history([{"ticker": "X", "time": "2026-06-30", "liq_bn": 1}, {"ticker": "X", "time": "2026-09-29", "liq_bn": 1}], datetime.date(2026, 11, 13))
    return a and hh["X"] == [datetime.date(2026, 6, 30)] and hh2["X"] == [datetime.date(2026, 6, 30), datetime.date(2026, 9, 29)]
def t_r3_run_lock_held_through_run(m):
    """Khoa phai giu SUOT luot (luc goi M1), khong chi luc vao."""
    import fcntl
    st = {"locked": None}
    def m1f(tk, T_):
        f = open(Path(e.tmp) / ".run.lock", "w")
        try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB); st["locked"] = False
        except BlockingIOError: st["locked"] = True
        finally: f.close()
        return valid_m1(tk, T_)
    e = Env(m, {T: [cand("AAA")]}, m1_fn=m1f); e.day(T)
    return st["locked"] is True
def t_r3_m2_blind_packet_clean(m):
    """Blind nhan DUNG goi goc (khong them khoa nao, khong mang ket luan M1)."""
    seen = []
    def m2(st, p, m1=None): seen.append((st, json.dumps(p, sort_keys=True))); return {"status": "FAIL", "reason": "x"}
    m.M2 = m2; pk = _pk(); m.run_m2(pk, {"driver_class": SENT, "view_20s": "CONT"})
    return len(seen) == 1 and seen[0][0] == "blind" and SENT not in seen[0][1] and json.loads(seen[0][1]) == pk
def t_r3_streak_live_only(m):
    base = {"status": "processed", "m1_status": "OK"}
    rows = [dict(base, mode="live", m2_status="OK"), dict(base, mode="retro", m2_status="FAIL"), dict(base, mode="retro", m2_status="FAIL"), dict(base, mode="retro", m2_status="FAIL")]
    rows2 = [dict(base, mode="live", m2_status="OK")] + [dict(base, mode="live", m2_status="FAIL")] * 2 + [dict(base, mode="retro", m2_status="OK")]
    return m.m2_fail_streak(rows) == 0 and m.m2_fail_streak(rows2) == 2
def t_r3_infra_overloaded_529(m):
    real = m.subprocess; out = []
    try:
        for msg in ("Overloaded", "API Error: 529 something", "overloaded_error"):
            m.subprocess = _FakeSub([_cp(json.dumps({"is_error": True, "result": msg}))])
            try: m.run_claude_m1("S", "U", "retro"); out.append(False)
            except m.InfraError: out.append(True)
            except Exception: out.append(False)
    finally: m.subprocess = real
    return all(out) and len(out) == 3
def t_r3_skip_rows_full(m):
    cs = [cand(f"T{i:02d}", liq=100 - i) for i in range(m.CAP_WEEK + 3)]
    e = Env(m, {WK[0]: cs}); o = e.day(WK[0]); rows = e.rows()
    sk = [r for r in rows if r["status"] == "skipped_capacity"]
    return len(o["skipped_capacity"]) == 3 and len(sk) == 3 and len(rows) == len(cs) \
        and all(r["stats"].get("rating_8l_asof") == 3 and r["stats"].get("route_8l") == "COMPOUNDER" and r["stats"].get("liq_bn") and r["stats"].get("rating_eff_date") == "2026-10-01" and r["stats"].get("rating_read_at") for r in sk)
def t_r3_sigterm_kills_m2_group(m):
    """(c) SIGTERM handler kill nhom second_opinion dang chay; run_second_opinion dang ky/huy dang ky nhom."""
    import signal as sg
    p = subprocess.Popen(["sleep", "60"], start_new_session=True); m._M2_PGIDS.add(p.pid)
    try:
        try: m._sigterm(); ok1 = False
        except SystemExit as ex: ok1 = ex.code == 143
        try: p.wait(timeout=5); ok2 = p.returncode == -9
        except subprocess.TimeoutExpired: ok2 = False
    finally:
        m._M2_PGIDS.discard(p.pid)
        try: os.killpg(p.pid, sg.SIGKILL)
        except (ProcessLookupError, PermissionError): pass
    seen = {}
    class P:
        pid = 424242; returncode = 0
        def __init__(self, *a, **k): pass
        def communicate(self, timeout=None): seen["in"] = 424242 in m._M2_PGIDS; return "", ""
    real = m.subprocess
    m.subprocess = types.SimpleNamespace(Popen=P, PIPE=subprocess.PIPE, TimeoutExpired=subprocess.TimeoutExpired)
    try: m.run_second_opinion(Path("/x"), Path("/y"), Path("/z"))
    finally: m.subprocess = real
    return ok1 and ok2 and seen.get("in") is True and 424242 not in m._M2_PGIDS
def t_r3_event_sql_in_protocol_hash(m):
    """(d) van ban SQL dinh nghia su kien nam trong CONST_PROTOCOL; doi SQL => hash doi."""
    c = m.protocol_consts()["event_sql_md5"]
    return set(c) == {"candidates", "eligible_range"} and all(len(v) == 32 for v in c.values()) and c["candidates"] != c["eligible_range"] \
        and m.hashlib.md5(m.sql_candidates("2000-01-03").encode()).hexdigest() == c["candidates"]
def t_r3_elig_rating_window(m):
    q = m.sql_eligible_range(T)
    return "rt.rt_time<=u.time" in q and "rt.rt_next IS NULL OR rt.rt_next>u.time" in q and "LEAD(r.time) OVER (PARTITION BY r.ticker ORDER BY r.time) rt_next" in q

TESTS = [t_r3_rebuttal_infra_not_swallowed, t_r3_scorer_m2_ok_real, t_r3_cooldown_boundary, t_r3_run_lock_held_through_run, t_r3_m2_blind_packet_clean, t_r3_streak_live_only, t_r3_infra_overloaded_529, t_r3_skip_rows_full, t_r3_sigterm_kills_m2_group, t_r3_event_sql_in_protocol_hash, t_r3_elig_rating_window, t_no_double_append, t_ledger_append_twice, t_parallel_append, t_md5_tamper, t_no_outcome_in_packet, t_sql_pit, t_news_pit, t_fin_pit, t_m2_exception_failopen,
         t_m2_fail_status, t_m2_ok_rebuttal, t_schema_strict, t_m1_fail_recorded, t_capacity, t_capacity_resets_next_week, t_cooldown, t_cooldown_same_quarter,
         t_live_guard, t_dry_run_no_write, t_dd_flag, t_scorer_no_peek, t_scorer_look, t_scorer_ignores_unscored, t_today_ict,
         t_prereg_params, t_prereg_stamp, t_prereg_lock, t_ticker_sens, t_scorer_ignores_other_prereg,
         t_m2a_ok_and_prompt, t_m2a_fail_modes, t_m2a_blind_before_and_no_m1, t_m2a_e2e_failopen, t_m2a_off_switch, t_m2a_bin_in_own_worktree, t_m2a_schema_boolean,
         t_protocol_nonempty, t_infra_stop_no_write_and_resume, t_infra_real_claude_errors, t_infra_cli_recovers_same_day, t_exit_codes, t_not_trading_day, t_freshness_depth,
         t_hist_deterministic_vs_ledger, t_replay_greedy, t_replay_ignores_T_and_future, t_cooldown_from_prev_day, t_rating_fin_news_pit, t_m1_content_checks, t_m1_argv, t_m2_dates,
         t_m2_record_and_cmd, t_m2_fail_reason_has_stderr, t_t3_only_m2_ok, t_run_lock_busy, t_m2_fail_streak, t_default_ledger_dir, t_outcomes_ruleset, t_kill_resume_midday]
MUTANTS = [  # (ten, old, new, test phai BAT duoc)
    # ---- R3 (D-a): 12 mutant song ----
    ("R3 rebuttal M1 nuot InfraError", '        r2, meta2, err2 = call_m1(packet, mode, "final", "PHAN BIEN M2: " + json.dumps(ch, ensure_ascii=False) + "\\nVONG 1 CUA BAN: " + json.dumps(r1, ensure_ascii=False))\n',
        '        try: r2, meta2, err2 = call_m1(packet, mode, "final", "PHAN BIEN M2: " + json.dumps(ch, ensure_ascii=False) + "\\nVONG 1 CUA BAN: " + json.dumps(r1, ensure_ascii=False))\n        except InfraError as _e: r2, meta2, err2 = None, [], str(_e)\n', "t_r3_rebuttal_infra_not_swallowed"),
    ("R3 score_report m2_ok luon True", '"m2_ok": r.get("m2_status") == "OK"})', '"m2_ok": True})', "t_r3_scorer_m2_ok_real"),
    ("R3 cooldown_ok '>' thanh '>='", "return (T - last).days > COOLDOWN_DAYS", "return (T - last).days >= COOLDOWN_DAYS", "t_r3_cooldown_boundary"),
    ("R3 replay_history '>' thanh '>='", "((d - h[-1]).days > COOLDOWN_DAYS", "((d - h[-1]).days >= COOLDOWN_DAYS", "t_r3_cooldown_boundary"),
    ("R3 run_lock chi giu luc vao", "    with run_lock(ledger_dir): return _run_day(Td, T, mode, ledger_dir, False, elig, ff)", "    with run_lock(ledger_dir): pass\n    return _run_day(Td, T, mode, ledger_dir, False, elig, ff)", "t_r3_run_lock_held_through_run"),
    ("R3 M2 blind nhan M1 qua packet", 'b = M2("blind", packet);', 'b = M2("blind", dict(packet, m1_view=m1));', "t_r3_m2_blind_packet_clean"),
    ("R3 m2_fail_streak dem ca retro", 'r.get("mode") == "live" and r.get("m1_status") == "OK"])', 'r.get("m1_status") == "OK"])', "t_r3_streak_live_only"),
    ("R3 INFRA_RE bo overloaded", "quota|overloaded|credit", "quota|credit", "t_r3_infra_overloaded_529"),
    ("R3 INFRA_RE bo 529", r"|\b429\b|\b529\b", r"|\b429\b", "t_r3_infra_overloaded_529"),
    ("R3 SQL elig bo cua so hieu luc rating", "AND (rt.rt_next IS NULL OR rt.rt_next>u.time))\nSELECT x.ticker", ")\nSELECT x.ticker", "t_r3_elig_rating_window"),
    ("R3 for c in skip khong ghi", "    for c in skip:\n        led.append(", "    for c in []:\n        led.append(", "t_r3_skip_rows_full"),
    ("R3 skip ghi dong rong (stats mat rating)", '"status": "skipped_capacity", "mode": mode,\n                    "stats": {"liq_bn": _f(c["liq_bn"]), "route_8l": c["route"], "rating_8l_asof": int(float(c["rating"])),', '"status": "skipped_capacity", "mode": mode,\n                    "stats": {"liq_bn": _f(c["liq_bn"]), "route_8l": c["route"], "rating_8l_asof": None,', "t_r3_skip_rows_full"),
    ("R3 SIGTERM khong kill nhom M2", "    for g in list(_M2_PGIDS):", "    for g in []:", "t_r3_sigterm_kills_m2_group"),
    ("R3 run_second_opinion khong dang ky nhom", "    _M2_PGIDS.add(p.pid)\n", "    pass\n", "t_r3_sigterm_kills_m2_group"),
    ("R3 SQL su kien khong vao hash", '"event_sql_md5": {"candidates": hashlib.md5(sql_candidates("2000-01-03").encode()).hexdigest(), "eligible_range"', '"event_sql_md5": {"candidates": "0", "eligible_range_": "0", "eligible_range"', "t_r3_event_sql_in_protocol_hash"),
    ("ledger append khong idempotent", 'if any(r["event_id"] == rec["event_id"] for r in self.read()): return False', "pass", "t_ledger_append_twice"),
    ("run_day bo guard idempotent (+ledger)", 'if any(r["event_id"] == f"{c[\'ticker\']}_{T}" for r in led.read()): continue', "pass", "t_no_double_append"),
    ("append khong khoa flock (mo rong cua so race)", ["fcntl.flock(lk, fcntl.LOCK_EX)", 'rec["md5"] = line_md5(rec)'], ["pass", '__import__("time").sleep(0.4); rec["md5"] = line_md5(rec)'], "t_parallel_append"),
    ("cooldown bo luat khac-quy", " and quarter_of(T) != quarter_of(last)", "", "t_cooldown_same_quarter"),
    ("bo kiem md5 khi doc", 'if r.get("md5") != line_md5(r): raise', 'if False: raise', "t_md5_tamper"),
    ("SQL dung LEAD (lo tuong lai)", "LAG(t.Close,20) OVER w c20", "LEAD(t.Close,20) OVER w c20", "t_sql_pit"),
    ("SQL doc ticker_prune", "tav2_mike.universe_pit AS up", "tav2_bq.ticker_prune AS up", "t_sql_pit"),
    ("bo loc ingested_at (code)", ' and str(r["ingested_date"])[:10] <= T]', "]", "t_news_pit"),
    ("bo loc ingested_at (SQL)", 'AND DATE(n.ingested_at, "Asia/Ho_Chi_Minh") <= DATE "{T}"', "", "t_sql_pit"),
    ("goi lot truong outcome", '"stats": {"mom20": _f(c["mom20"])', '"ex20": _f(c.get("ex20")), "stats": {"mom20": _f(c["mom20"])', "t_no_outcome_in_packet"),
    ("bo loc Release_Date<=T", ' and str(r["Release_Date"])[:10] <= T],', "],", "t_fin_pit"),
    ("M2 loi khong fail-open", "    except Exception as e:\n        return {**base, \"m2_status\": \"FAIL\"", "    except KeyboardInterrupt as e:\n        return {**base, \"m2_status\": \"FAIL\"", "t_m2_exception_failopen"),
    ("M1 bo kiem schema", "errs = validate(obj, SCHEMA[schema_key]) + (", "errs = [] + (", "t_m1_fail_recorded"),
    ("schema cho phep truong thua", '"additionalProperties") is False', '"additionalProperties") is True', "t_schema_strict"),
    ("tran hang doi 10->100", 'CAP_WEEK = V3["cap_week"]', "CAP_WEEK = 100", "t_capacity"),
    ("hang doi khong reset tuan", "if week_key(d) == week_key(T): used +=", "if True: used +=", "t_capacity_resets_next_week"),
    ("cooldown 90->0", 'COOLDOWN_DAYS = V3["cooldown_days"]', "COOLDOWN_DAYS = 0", "t_cooldown"),
    ("live cho T != hom nay", 'if mode == "live" and Td != today:', 'if False:', "t_live_guard"),
    ("dry-run van ghi", "if dry_run or not (proc or skip): return out", "if not (proc or skip): return out", "t_dry_run_no_write"),
    ("scorer lo effects giua look", "    if look:\n        rep[\"look\"]", "    look = look or ('PEEK', _first_n_dir(sc, 10**9))\n    if look:\n        rep[\"look\"]", "t_scorer_no_peek"),
    ("scorer dem N khong huong", 'n_dir = [s for s in sc if s["v20"] in ("CONT", "REV")]', "n_dir = list(sc)", "t_scorer_no_peek"),
    ("nguong mom20 sai (cu v2)", "mom20>={V3[\"mom20\"]}", "mom20>=0.20", "t_prereg_params"),
    ("nguong volr sai (cu v2)", "volr>={V3[\"volr\"]}", "volr>=1.5", "t_prereg_params"),
    ("nguong liq sai (cu v2)", "liq_bn>={V3[\"liq_bn\"]} AND rating", "liq_bn>=3 AND rating", "t_prereg_params"),
    ("nguong idio sai (cu v2)", "idio20>={V3[\"idio20\"]}", "idio20>=0.15", "t_prereg_params"),
    ("JSON v3 doi nguong (khong dong bo)", 'CAP_WEEK = V3["cap_week"]', "CAP_WEEK = 7", "t_prereg_params"),
    ("mat prereg_version/md5 tren dong", 'rec.setdefault("prereg_version", PREREG_VERSION) != PREREG_VERSION or rec.setdefault("prereg_md5", PREREG_MD5) != PREREG_MD5\n                    or rec.setdefault("protocol_md5", PROTOCOL_MD5) != PROTOCOL_MD5', "False", "t_prereg_stamp"),
    ("bo khoa md5 PREREG", 'if lock.get(f) != _md5b(b): raise SystemExit(', 'if False: raise SystemExit(', "t_prereg_lock"),
    ("bo khoa hang so giao thuc", '    if lock.get("CONST_PROTOCOL") != _consts_md5(): raise SystemExit(', '    if False: raise SystemExit(', "t_prereg_lock"),
    ("scorer dem dong protocol khac", ' and r.get("protocol_md5") == PROTOCOL_MD5]', "]", "t_scorer_ignores_other_prereg"),
    ("G-proc khong loc protocol", ' and r.get("protocol_md5") == PROTOCOL_MD5 and r.get("mode") == "live"]', ' and r.get("mode") == "live"]', "t_scorer_ignores_other_prereg"),
    ("bo do nhay cum theo ma", 'if "T1" in out and "ticker" in df:', "if False:", "t_ticker_sens"),
    ("sensitivity lot vao ho BH (khoa T1 sai)", '"role": "descriptive_not_in_BH_family"', '"role": "bh"', "t_ticker_sens"),
    ("sc khong mang ticker", '"T": r["T"], "ticker": r["ticker"],', '"T": r["T"],', "t_ticker_sens"),
    ("M2 blind nhan M1 (ro ri)", ['b = M2("blind", packet)', 'if stage == "challenge": parts.append'], ['b = M2("blind", packet, m1)', 'if m1 is not None: parts.append'], "t_m2a_blind_before_and_no_m1"),
    ("M2 mat khung dinh dang", "NO_TOOL_LINE, FORMAT_HINT[stage],", "NO_TOOL_LINE,", "t_m2a_ok_and_prompt"),
    ("validate khong biet boolean", ', "boolean": bool}', "}", "t_m2a_schema_boolean"),
    ("M2 prompt mat dong no-tool", 'parts = [_BLOBS[M2_PROMPT[stage]].decode("utf-8").strip(), NO_TOOL_LINE,', 'parts = [_BLOBS[M2_PROMPT[stage]].decode("utf-8").strip(),', "t_m2a_ok_and_prompt"),
    ("M2 timeout 240->100 (bi KHOA md5 bat)", "M2_TIMEOUT = 240", "M2_TIMEOUT = 100", "t_m2a_ok_and_prompt"),
    ("M2 bo qua exit code", "if rc != 0: return", "if False: return", "t_m2a_fail_modes"),
    ("M2 bo bat timeout", "except subprocess.TimeoutExpired: return", "except KeyError: return", "t_m2a_fail_modes"),
    ("M2 bo kiem schema", "errs = validate(obj, M2_SCHEMA[stage]) +", "errs = [] +", "t_m2a_fail_modes"),
    ("M2 bo kiem event_id", 'obj.get("event_id") == packet["event_id"]', 'True', "t_m2a_fail_modes"),
    ("M2 mat raw ledger", 'base = {"m2_model": M2_MODEL, "m2_raw": raw, "m2_log": log}', 'base = {"m2_model": M2_MODEL, "m2_log": log}', "t_m2a_e2e_failopen"),
    ("M2 hardcode bin canonical", 'return p\n    raise FileNotFoundError', 'return Path("/home/trido/thanhdt/WorkingClaude/mike")\n    raise FileNotFoundError', "t_m2a_bin_in_own_worktree"),
    ("today bo neo ICT", "dt.datetime.now(ICT).date()", "dt.datetime.now().date()", "t_today_ict"),
    # ---- v3.2 ----
    ("B1 loi ha tang bi nuot o call_m1", "        except InfraError: raise\n", "        except KeyError: raise\n", "t_infra_stop_no_write_and_resume"),
    ("B1 FileNotFoundError khong thanh InfraError", "except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired, OSError) as e:", "except KeyError as e:", "t_infra_cli_recovers_same_day"),
    ("B1 rc!=0 khong JSON khong phai ha tang", 'if r.returncode: raise InfraError(f"claude rc={r.returncode}: {r.stderr[-400:]}', 'if r.returncode: raise RuntimeError(f"claude rc={r.returncode}: {r.stderr[-400:]}', "t_infra_real_claude_errors"),
    ("R3-B xet rc truoc JSON (max-turns thanh ha tang)", "    if not isinstance(d, dict):   # khong co JSON", "    if r.returncode: raise InfraError('rc')\n    if not isinstance(d, dict):   # khong co JSON", "t_infra_real_claude_errors"),
    ("R3-B max-turns rc!=0 thanh ha tang", 'if sub in ("error_max_turns", "error_max_budget_usd") or d.get("is_error"):\n            raise RuntimeError', 'if sub in ("error_max_turns", "error_max_budget_usd") or d.get("is_error"):\n            raise InfraError', "t_infra_real_claude_errors"),
    ("B1 is_error usage/auth khong phai ha tang", 'if INFRA_RE.search(msg) or INFRA_RE.search(', 'if False and INFRA_RE.search(msg) or INFRA_RE.search(', "t_infra_real_claude_errors"),
    ("B1 run_day ghi dong khi ha tang hong", 'out["infra_stop"] = f"{p[\'event_id\']}: {str(e)[:300]}"; break', 'out["infra_stop"] = f"{p[\'event_id\']}: {str(e)[:300]}"; rec = dict(event_id=p["event_id"], ticker=p["ticker"], T=T, status="processed", mode=mode, stats={}, m1_status="FAIL", m1_error="infra", m2_status="SKIPPED", usage=[]); led.append(rec); break', "t_infra_stop_no_write_and_resume"),
    ("B2 cooldown replay bo luat khac-quy", " and quarter_of(d) != quarter_of(h[-1])", "", "t_replay_greedy"),
    ("B2 replay doc ca ngay T", "        if d >= T: continue                       # chi qua khu: khong bao gio doc T tro di\n", "", "t_replay_ignores_T_and_future"),
    ("B2 cap tuan khong tru su kien truoc", "if week_key(d) == week_key(T): used +=", "if False: used +=", "t_hist_deterministic_vs_ledger"),
    ("B2 cooldown khong dung lich su BQ", "hist, used = replay_history(elig, Td)", "hist, used = {}, 0", "t_cooldown_from_prev_day"),
    ("B2 SQL range doc den T (khong T-1)", 'AND DATE_SUB(DATE "{T}", INTERVAL 1 DAY) AND t.ticker', 'AND DATE "{T}" AND t.ticker', "t_sql_pit"),
    ("B5 khong phan biet exit 4", 'except DataNotReady as e: print(f"EXIT4 {e}", file=sys.stderr); return 4', 'except DataNotReady as e: print(f"EXIT4 {e}", file=sys.stderr); return 1', "t_exit_codes"),
    ("B5 infra_stop khong ra exit 5", 'return 5 if out.get("infra_stop") else 0', "return 0", "t_exit_codes"),
    ("B5 bo kiem ngay giao dich", "if not IS_TRADING_DAY(Td): raise NotTradingDay", "if False: raise NotTradingDay", "t_not_trading_day"),
    ("B5 ngay le khong tinh", "    if d.weekday() >= 5: return False\n", "    if d.weekday() >= 9: return False\n", "t_not_trading_day"),
    ("B5 bo run_lock", "fcntl.flock(self.f, fcntl.LOCK_EX | fcntl.LOCK_NB)", "pass", "t_run_lock_busy"),
    ("B6 cong freshness chi MAX(time)", "    if float(cov) < FRESH_RATIO * float(pv_n):", "    if False:", "t_freshness_depth"),
    ("R3 SQL freshness bo in_universe", "AND u.in_universe),\n tkT", "),\n tkT", "t_freshness_depth"),
    ("R3 SQL freshness phien truoc thanh <=T", 'u.time < DATE "{T}" AND u.time >=', 'u.time <= DATE "{T}" AND u.time >=', "t_freshness_depth"),
    ("B6 thieu dem dong van cho qua", '    if pv_n in (None, "") or cov in (None, "") or float(pv_n) <= 0: return', '    if False: return', "t_freshness_depth"),
    ("B6 bo kiem MAX(time)<T", 'if not mx or str(mx)[:10] < T: return', 'if not mx: return', "t_freshness_depth"),
    ("R3 up_n=0 van cho qua", 'if up_n in (None, "") or float(up_n) <= 0: return', 'if False: return', "t_freshness_depth"),
    ("B6 freshness khong raise (ghi tiep)", 'if prob: raise DataNotReady', 'if False: raise DataNotReady', "t_freshness_depth"),
    ("rating khong gioi han <=T", 'WHERE r.time <= DATE "{T}" QUALIFY', 'WHERE r.time <= DATE "2099-01-01" QUALIFY', "t_rating_fin_news_pit"),
    ("fin khong gioi han <=T", 'f.Release_Date <= DATE "{_date(T)}"', 'f.Release_Date <= DATE "2099-01-01"', "t_rating_fin_news_pit"),
    ("news khong gioi han <=T", 'INTERVAL 120 DAY) AND DATE "{T}"', 'INTERVAL 120 DAY) AND DATE "2099-01-01"', "t_rating_fin_news_pit"),
    ("M1 bo kiem evidence date<=T", 'if not errs and not evidence_dates_ok(obj, packet["T"]): errs = ["evidence date > T"]', "pass", "t_m1_content_checks"),
    ("M1 bo kiem event_id", 'else ["event_id mismatch"])', 'else [])', "t_m1_content_checks"),
    ("M1 argv retro co WebSearch (bi KHOA md5 bat)", '"--tools", ("WebSearch" if live else "")', '"--tools", "WebSearch"', "t_m1_argv"),
    ("M1 live thieu allowedTools (bi KHOA md5 bat)", ' + (["--allowedTools", "WebSearch"] if live else [])', "", "t_m1_argv"),
    ("M2 bo kiem ngay<=T", 'if not errs and not m2_dates_ok(stage, obj, packet["T"]): errs = ["date > T"]', "pass", "t_m2_dates"),
    ("M2 khong truyen --model", '"--model", M2_MODEL, "--timeout"', '"--timeout"', "t_m2_record_and_cmd"),
    ("M2 khong kill nhom khi qua tran", "            try: os.killpg(p.pid, signal.SIGKILL)\n            except ProcessLookupError: pass\n", "            pass\n", "t_m2_record_and_cmd"),
    ("M2 khong don tmpdir wrapper (TMPDIR)", "env=dict(os.environ, TMPDIR=str(Path(out_jsonl).parent))", "env=dict(os.environ)", "t_m2_record_and_cmd"),
    ("M2 reason mat duoi stderr", 'f"second_opinion_exit_{rc}: {tail[-200:]}"', 'f"second_opinion_exit_{rc}"', "t_m2_fail_reason_has_stderr"),
    ("T3 gom ca su kien M2 FAIL", "d3 = d3[d3.m2_ok.astype(bool) & (", "d3 = d3[d3.m2_ok.astype(bool) | (", "t_t3_only_m2_ok"),
    ("ledger mac dinh tro ve canonical", 'default=str(_repo_root() / "data" / "ai_momentum")', 'default=str(WC / "mike/data/ai_momentum")', "t_default_ledger_dir"),
    ("sql_outcomes hardcode ruleset 1", 'AND u.ruleset_version={V3["universe_ruleset"]}\n   WHERE t.time BETWEEN', 'AND u.ruleset_version=1\n   WHERE t.time BETWEEN', "t_outcomes_ruleset"),
    ("harness: dich khong ton tai (PHAI lam harness FAIL)", "CHUOI_KHONG_TON_TAI_XYZ", "x", "t_protocol_nonempty"),
]
def main():
    bad = 0; print(f"TZ env={os.environ.get('TZ')!r}  local={time.tzname}")
    for t in TESTS:
        try: ok = bool(t(REAL))
        except Exception as e: ok = False; print("   exc:", type(e).__name__, e)
        bad += (not ok); print(("PASS " if ok else "FAIL ") + t.__name__)
    tm = {t.__name__: t for t in TESTS}; killed = by_lock = 0
    for i, (name, old, new, tn) in enumerate(MUTANTS):
        if "KHONG_TON_TAI" in old:        # tu-kiem harness: mutant co chuoi dich khong ton tai PHAI lam harness FAIL, khong duoc tinh KILLED
            try: mutant(old, new, f"mut{i}"); bad += 1; print(f"HARNESS-BUG khong phat hien dich mutant mat: {name}")
            except HarnessError: print(f"HARNESS-OK  mutant[{name}] <- dich khong ton tai => harness FAIL dung")
            continue
        try: mod = mutant(old, new, f"mut{i}")
        except HarnessError as e: bad += 1; print(f"HARNESS-FAIL mutant[{name}]: {e}"); continue
        except SystemExit as e: killed += 1; by_lock += 1; print(f"KILLED(lock) mutant[{name}] <- khoa md5 giao thuc ({str(e)[:50]})"); continue
        try: det = not tm[tn](mod)
        except Exception as e: det = True; print(f"   (mutant lam test nem {type(e).__name__})")      # mutant lam sap hanh vi = bi bat, nhung CHI sau khi dich da ap dung that
        killed += det; bad += (not det); print(("KILLED " if det else "SURVIVED ") + f"mutant[{name}] <- {tn}")
    print(f"== {len(TESTS)} tests, {len(MUTANTS)} mutants ({killed} killed, {by_lock} boi khoa md5) -> {'ALL PASS' if not bad else str(bad) + ' LOI'}"); return 1 if bad else 0
if __name__ == "__main__": sys.exit(main())
