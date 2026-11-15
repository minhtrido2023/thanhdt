#!/usr/bin/env python3
"""Selfcheck ai_momentum_daily.py — fake BQ + fake M1/M2 (khong goi mang, khong ton token) + MUTATION test tren chinh source.
Chay duoi 3 TZ:  env -u TZ python3 selfcheck_ai_momentum.py ; TZ=UTC ... ; TZ=America/New_York ...   (coding_guidelines §16/§23)"""
import os, sys, json, time, tempfile, types, datetime, multiprocessing as mp, importlib.util
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import ai_momentum_daily as REAL
SRC = (HERE / "ai_momentum_daily.py").read_text()
T = "2026-11-13"; WK = ["2026-11-09", "2026-11-10", "2026-11-11", "2026-11-12", "2026-11-13"]   # cung tuan ISO

def mutant(old, new, name="mut"):
    src = SRC
    for o, n in (zip(old, new) if isinstance(old, list) else [(old, new)]):
        assert o in src, f"mutation target khong ton tai: {o[:50]}"; src = src.replace(o, n, 1)
    mod = types.ModuleType(name); mod.__file__ = str(HERE / "ai_momentum_daily.py")
    sys.modules[name] = mod; exec(compile(src, mod.__file__, "exec"), mod.__dict__); return mod

def cand(tk, liq=10.0, **kw):
    d = dict(ticker=tk, mom20=0.3, idio20=0.2, volr=2.0, liq_bn=liq, route="COMPOUNDER", rating=3, rt_time="2026-10-01", route_ret20_med=0.05,
             route_n=100, pct_in_route=0.95, icb="8000", icb_ret20_med=0.04, icb_n=50, vn20=0.01); d.update(kw); return d
def valid_m1(tk, T_, view="CONT", drv="EARNINGS", ev_date=None):
    return {"driver_class": drv, "evidence": [{"claim": "x", "source": "stats", "date": ev_date or T_}], "what_market_prices_in": "a",
            "invalidation": "b", "view_20s": view, "view_60s": "NO_VIEW", "confidence": 0.4}

class Env:
    """Dung fake cho 1 module m. cands_by_date: {T: [cand,...]}; m1_fn(tk,T)->dict|str; m2_fn(stage,packet,m1)->dict."""
    def __init__(self, m, cands_by_date, m1_fn=None, m2_fn=None, news=None):
        self.m, self.cd, self.calls, self.news = m, cands_by_date, [], news or []
        self.tmp = tempfile.mkdtemp(prefix="am_sc_")
        def bq(sql):
            if "SELECT (SELECT MAX(time)" in sql: return [{"tk": "2026-11-13", "up": "2026-11-13"}]
            if "PERCENTILE_CONT" in sql: return self.cd.get(sql.split('DATE "')[1][:10] if False else self.cur_T, [])
            if "ticker_financial" in sql: return [{"ticker": c["ticker"], "quarter": "2026Q3", "Release_Date": "2026-10-20", "NP_P0": "1", "NP_P4": "1",
                    "Revenue_P0": "1", "Revenue_YoY_P0": "0.1", "GPM_P0": "0.2", "PE": "10", "PB": "1", "ROE_Trailing": "0.1"} for cs in self.cd.values() for c in cs]
            if "stock_news" in sql: return self.news
            raise AssertionError("SQL la: " + sql[:60])
        def m1_run(system, user, mode):
            pk = json.JSONDecoder().raw_decode(user.split("GOI:\n", 1)[1])[0]; tk, Tn = pk["ticker"], pk["T"]; self.calls.append(("m1", tk))
            r = (m1_fn or (lambda tk_, T_: valid_m1(tk_, T_)))(tk, Tn)
            return (r if isinstance(r, str) else json.dumps(r)), {"cost_usd": 0.01, "usage": {"input_tokens": 1, "output_tokens": 1, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}, "models": ["fake"]}
        m.BQ = bq; m.M1_RUN = m1_run; m.M2 = m2_fn or (lambda st, p, m1=None: {"status": "FAIL", "reason": "off"})
    def day(self, d, mode="retro", dry=False, seed=None):
        self.cur_T = d
        return self.m.run_day(d, mode, self.tmp, dry, seed={} if seed is None else seed, ff=[])
    def rows(self): return self.m.Ledger(Path(self.tmp) / "ai_momentum_retro.jsonl").read()

# ---------------- tests (m -> bool; True = hanh vi dung) ----------------
def t_no_double_append(m):
    e = Env(m, {T: [cand("AAA"), cand("BBB", 5)]}); e.day(T); n1 = len(e.rows()); c1 = len(e.calls); e.day(T)
    return n1 == 2 and len(e.rows()) == 2 and len(e.calls) == c1 == 2
def _w(path): m_ = REAL; led = m_.Ledger(path); led.append({"event_id": "X_1", "ticker": "X", "T": "2026-11-13", "status": "processed", "mode": "retro"})
def t_ledger_append_twice(m):
    led = m.Ledger(Path(tempfile.mkdtemp()) / "l.jsonl"); r = {"event_id": "E", "ticker": "X", "T": T, "status": "processed", "mode": "retro"}
    return led.append(r) is True and led.append(dict(r)) is False and len(led.read()) == 1
def t_parallel_append(m):
    p = Path(tempfile.mkdtemp()) / "l.jsonl"; led = m.Ledger(p)
    ps = [mp.Process(target=led.append, args=({"event_id": "E", "ticker": "X", "T": T, "status": "processed", "mode": "retro"},)) for _ in range(6)]
    [x.start() for x in ps]; [x.join() for x in ps]; return len(led.read()) == 1
def t_md5_tamper(m):
    p = Path(tempfile.mkdtemp()) / "l.jsonl"; led = m.Ledger(p); led.append({"event_id": "E", "ticker": "X", "T": T, "status": "processed", "mode": "retro"})
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
    return all("LEAD(" not in s and "profit_" not in s and "ticker_prune" not in s for s in sqls) and "universe_pit" in sqls[0] \
        and 'DATE(n.ingested_at, "Asia/Ho_Chi_Minh") <= DATE' in sqls[2]
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
    e.m.run_day  # tuan sau: freshness fake chap nhan moi ngay
    e.cd["2026-11-16"] = [cand("NEXT")]
    m_bq = m.BQ; m.BQ = lambda sql: [{"tk": "2026-11-16", "up": "2026-11-16"}] if "SELECT (SELECT MAX(time)" in sql else m_bq(sql)
    o = e.day("2026-11-16"); return o["processed"] == ["NEXT"]
def t_cooldown(m):
    seed = {"CLOSE": [datetime.date(2026, 9, 20)], "OLD": [datetime.date(2026, 6, 1)], "SAMEQ": [datetime.date(2026, 10, 2)], "FAR": [datetime.date(2026, 5, 1)], "Q": [datetime.date(2026, 8, 10)]}
    e = Env(m, {T: [cand("OLD"), cand("SAMEQ"), cand("FAR"), cand("Q"), cand("NEW"), cand("CLOSE")]}); o = e.day(T, seed=seed)
    # OLD: 165 ngay & khac quy (Q2 vs Q4) -> OK ; SAMEQ: 42 ngay -> loai ; FAR OK ; Q: 95 ngay, khac quy (Q3 vs Q4) -> OK ; NEW OK
    return sorted(o["processed"]) == ["FAR", "NEW", "OLD", "Q"]
def t_cooldown_same_quarter(m):   # >90 ngay nhung cung quy duong lich (vd 2026-10-01 vs ...): dung ngay 2026-01-01 vs 2026-04-... khong cung quy; test truc tiep
    h = {"A": [datetime.date(2026, 7, 1)]}   # 2026-07-01 -> 09-30 = 91 ngay (>90) nhung CUNG quy => loai; 10-01 khac quy => duoc
    return m.cooldown_ok("A", datetime.date(2026, 9, 30), h) is False and m.cooldown_ok("A", datetime.date(2026, 10, 1), h) is True
def t_live_guard(m):
    e = Env(m, {T: [cand("A")]})
    try: m.run_day(T, "live", e.tmp, True, seed={}, ff=[]); return False
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
        rows.append({"event_id": eid, "ticker": f"S{i}", "T": str(d), "status": "processed", "mode": "live", "m1_status": "OK", "m2_status": "FAIL", "prereg_md5": m.PREREG_MD5,
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
        and all(r.get("prereg_version") == "v3" and r.get("prereg_md5") == m.PREREG_MD5 and len(r["prereg_md5"]) == 32 for r in rows) \
        and m.PREREG_MD5 == m._md5f(HERE / "PREREG_v3.md")
def t_prereg_lock(m):
    import shutil; ok_dir = Path(tempfile.mkdtemp()); bad_dir = Path(tempfile.mkdtemp()); old = m.HERE
    for d in (ok_dir, bad_dir):
        for f in ("PREREG_v3.md", "PREREG_v3.md5", "prereg_v3.json", "events_v3.csv"): shutil.copy(HERE / f, d / f)
    (bad_dir / "prereg_v3.json").write_text((HERE / "prereg_v3.json").read_text().replace('"mom20": 0.15', '"mom20": 0.2'))
    try:
        m.HERE = ok_dir; good = m._load_prereg()[0]["mom20"] == 0.15
        m.HERE = bad_dir
        try: m._load_prereg(); return False
        except SystemExit: return good
    finally: m.HERE = old
def t_ticker_sens(m):
    rows, out = _rows_for_score(m, 80, 10); r = m.score_report(rows, out, "2026-12-31"); ef = r.get("effects", {}); ts = ef.get("T1_ticker_sensitivity")
    return bool(ts) and ts["role"] == "descriptive_not_in_BH_family" and ts["n_tickers"] == 80 and ts["n_first"] == 80 and len(ts["boot_ci95"]) == 2 \
        and ts["boot_ci95"][0] <= ts["boot_ci95"][1] and set(k for k in ef if k.startswith("T")) <= {"T1", "T2", "T3", "T1_ticker_sensitivity"}
def t_scorer_ignores_other_prereg(m):
    rows, out = _rows_for_score(m, 80, 10)
    for r in rows[:30]: r["prereg_md5"] = "0" * 32
    r = m.score_report(rows, out, "2026-12-31"); return r["N_scored"] == 60
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

TESTS = [t_no_double_append, t_ledger_append_twice, t_parallel_append, t_md5_tamper, t_no_outcome_in_packet, t_sql_pit, t_news_pit, t_fin_pit, t_m2_exception_failopen,
         t_m2_fail_status, t_m2_ok_rebuttal, t_schema_strict, t_m1_fail_recorded, t_capacity, t_capacity_resets_next_week, t_cooldown, t_cooldown_same_quarter,
         t_live_guard, t_dry_run_no_write, t_dd_flag, t_scorer_no_peek, t_scorer_look, t_scorer_ignores_unscored, t_today_ict,
         t_prereg_params, t_prereg_stamp, t_prereg_lock, t_ticker_sens, t_scorer_ignores_other_prereg]
MUTANTS = [  # (ten, old, new, test phai BAT duoc)
    ("ledger append khong idempotent", 'if any(r["event_id"] == rec["event_id"] for r in self.read()): return False', "pass", "t_ledger_append_twice"),
    ("run_day bo guard idempotent (+ledger)", 'if any(r["event_id"] == f"{c[\'ticker\']}_{T}" for r in led.read()): continue', "pass", "t_no_double_append"),
    ("append khong khoa flock (mo rong cua so race)", ["fcntl.flock(lk, fcntl.LOCK_EX)", 'rec = dict(rec); rec["md5"] = line_md5(rec)'], ["pass", 'rec = dict(rec); __import__("time").sleep(0.4); rec["md5"] = line_md5(rec)'], "t_parallel_append"),
    ("cooldown bo luat khac-quy", " and quarter_of(T) != quarter_of(last)", "", "t_cooldown_same_quarter"),
    ("bo kiem md5 khi doc", 'if r.get("md5") != line_md5(r): raise', 'if False: raise', "t_md5_tamper"),
    ("SQL dung LEAD (lo tuong lai)", "LAG(t.Close,20) OVER w c20", "LEAD(t.Close,20) OVER w c20", "t_sql_pit"),
    ("SQL doc ticker_prune", "tav2_mike.universe_pit AS up", "tav2_bq.ticker_prune AS up", "t_sql_pit"),
    ("bo loc ingested_at (code)", ' and str(r["ingested_date"])[:10] <= T]', "]", "t_news_pit"),
    ("bo loc ingested_at (SQL)", 'AND DATE(n.ingested_at, "Asia/Ho_Chi_Minh") <= DATE "{T}"', "", "t_sql_pit"),
    ("goi lot truong outcome", '"stats": {"mom20": _f(c["mom20"])', '"ex20": _f(c.get("ex20")), "stats": {"mom20": _f(c["mom20"])', "t_no_outcome_in_packet"),
    ("bo loc Release_Date<=T", ' and str(r["Release_Date"])[:10] <= T],', "],", "t_fin_pit"),
    ("M2 loi khong fail-open", "    except Exception as e:\n        return {\"m2_status\": \"FAIL\"", "    except KeyboardInterrupt as e:\n        return {\"m2_status\": \"FAIL\"", "t_m2_exception_failopen"),
    ("M1 bo kiem schema", "errs = validate(obj, SCHEMA[schema_key]) + (", "errs = [] + (", "t_m1_fail_recorded"),
    ("schema cho phep truong thua", '"additionalProperties") is False', '"additionalProperties") is True', "t_schema_strict"),
    ("tran hang doi 10->100", 'CAP_WEEK = V3["cap_week"]', "CAP_WEEK = 100", "t_capacity"),
    ("hang doi khong reset tuan", "and week_key(dt.date.fromisoformat(r[\"T\"])) == week_key(T))", ")", "t_capacity_resets_next_week"),
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
    ("mat prereg_version/md5 tren dong", 'rec.setdefault("prereg_version", PREREG_VERSION) != PREREG_VERSION or rec.setdefault("prereg_md5", PREREG_MD5) != PREREG_MD5', "False", "t_prereg_stamp"),
    ("bo khoa md5 PREREG", 'if lock.get(f) != _md5f(HERE / f): raise SystemExit(', 'if False: raise SystemExit(', "t_prereg_lock"),
    ("scorer dem dong prereg khac", ' and r.get("prereg_md5") == PREREG_MD5]', "]", "t_scorer_ignores_other_prereg"),
    ("bo do nhay cum theo ma", 'if "T1" in out and "ticker" in df:', "if False:", "t_ticker_sens"),
    ("sensitivity lot vao ho BH (khoa T1 sai)", '"role": "descriptive_not_in_BH_family"', '"role": "bh"', "t_ticker_sens"),
    ("sc khong mang ticker", '"T": r["T"], "ticker": r["ticker"],', '"T": r["T"],', "t_ticker_sens"),
    ("today bo neo ICT", "dt.datetime.now(ICT).date()", "dt.datetime.now().date()", "t_today_ict"),
]
def main():
    bad = 0; print(f"TZ env={os.environ.get('TZ')!r}  local={time.tzname}")
    for t in TESTS:
        try: ok = bool(t(REAL))
        except Exception as e: ok = False; print("   exc:", type(e).__name__, e)
        bad += (not ok); print(("PASS " if ok else "FAIL ") + t.__name__)
    tm = {t.__name__: t for t in TESTS}; killed = 0
    for i, (name, old, new, tn) in enumerate(MUTANTS):
        try: mod = mutant(old, new, f"mut{i}"); det = not tm[tn](mod)
        except Exception: det = True                                   # mutant lam sap/ nem loi = bi bat
        killed += det; bad += (not det); print(("KILLED " if det else "SURVIVED ") + f"mutant[{name}] <- {tn}")
    print(f"== {len(TESTS)} tests, {len(MUTANTS)} mutants ({killed} killed) -> {'ALL PASS' if not bad else str(bad) + ' LOI'}"); return 1 if bad else 0
if __name__ == "__main__": sys.exit(main())
