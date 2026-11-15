#!/usr/bin/env python3
"""ai_momentum_daily.py — P1 BUILD (PREREG v1 + PREREG_v2.md). Paper-only: KHONG lenh, KHONG plan, KHONG state_*.json.
Luong: su kien moi ngay T (PREREG s1) -> hang doi <=10/tuan -> goi PIT -> M1 (claude phien TRAN) -> M2 (adapter, hien
fail-open) -> ghi JSONL append-only (md5/dong, idempotent). `--score`: scorer chi in N + G-proc giua cac moc look.
  python3 ai_momentum_daily.py --date 2026-11-16 [--mode live|retro] [--dry-run] [--ledger-dir DIR]
  python3 ai_momentum_daily.py --score [--ledger-dir DIR]
PIT: moi SQL chi doc <= T (khong LEAD/profit_*; selfcheck bat). Cron: KHONG cai o P1."""
import os; os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, datetime as dt, fcntl, hashlib, json, re, subprocess, sys, tempfile
from pathlib import Path
from zoneinfo import ZoneInfo
ICT = ZoneInfo("Asia/Ho_Chi_Minh")          # coding_guidelines §16: neo TZ tuong minh
HERE = Path(__file__).resolve().parent
WC = Path("/home/trido/thanhdt/WorkingClaude")
BQ_PROJECT = "lithe-record-440915-m9"
BANNED = "PC1 VVS KSF NKG HSG HVN VJC NVL GEG SBA DMC IMP TRA TOS VTP BAF".split()
CAP_WEEK = 10
COOLDOWN_DAYS = 90
PACKET_KEYS = {"event_id", "ticker", "T", "stats", "sector_context", "financials_released_le_T", "news_le_T"}
FORBIDDEN_KEYS = {"ex20", "ex60", "r20", "r60", "c1", "c21", "c61", "profit_2W", "profit_1M", "profit_2M", "profit_3M"}
M1_SYSTEM = (HERE / "prompt_M1_v2.md").read_text(encoding="utf-8") if (HERE / "prompt_M1_v2.md").exists() else ""
REBUT = (HERE / "prompt_M1_rebuttal_v2.md").read_text(encoding="utf-8") if (HERE / "prompt_M1_rebuttal_v2.md").exists() else ""
SCHEMA = json.loads((HERE / "schema_M1_v2.json").read_text()) if (HERE / "schema_M1_v2.json").exists() else {}

# ---------------------------------------------------------------- BQ (injectable)
def bq(sql):
    """bq CLI qua env wc_env.sh. SQL qua env Q (khong qua argv shell)."""
    out = subprocess.run(["bash", "-c", f"source {WC}/wc_env.sh >/dev/null; bq query --use_legacy_sql=false "
        f"--project_id={BQ_PROJECT} --format=json --max_rows=100000 \"$Q\""],
        env={"Q": sql, "PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": "/home/trido"}, capture_output=True, text=True)
    if out.returncode:
        raise RuntimeError(f"bq failed rc={out.returncode}: {out.stderr[-800:]}")
    return json.loads(out.stdout or "[]")
BQ = bq

def today_ict(): return dt.datetime.now(ICT).date()

def _date(s):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(s)): raise ValueError(f"bad date {s!r}")
    return str(s)

def sql_candidates(T):
    T = _date(T)
    return f"""WITH base AS (
  SELECT t.ticker, t.time, t.Close, t.Price, t.Volume_1M, t.Volume_3M_P50, t.HI_3M_T1, t.VNINDEX, t.ICB_Code,
    LAG(t.Close,20) OVER w c20, LAG(t.VNINDEX,20) OVER w v20
  FROM tav2_bq.ticker AS t
  WHERE t.time BETWEEN DATE_SUB(DATE "{T}", INTERVAL 60 DAY) AND DATE "{T}" AND t.ticker != "VNINDEX"
  WINDOW w AS (PARTITION BY t.ticker ORDER BY t.time)),
u AS (SELECT b.* FROM base b JOIN tav2_mike.universe_pit AS up
      ON up.ticker=b.ticker AND up.time=b.time AND up.ruleset_version=1
      WHERE b.time = DATE "{T}" AND up.in_universe),
rt AS (SELECT r.ticker, r.time rt_time, r.route, r.rating FROM tav2_bq.fa_ratings_8l AS r
       WHERE r.time <= DATE "{T}" QUALIFY ROW_NUMBER() OVER (PARTITION BY r.ticker ORDER BY r.time DESC)=1),
x AS (SELECT u.ticker, u.time, CAST(u.ICB_Code AS STRING) icb, rt.route, rt.rating, rt.rt_time,
        u.Close/u.c20-1 mom20, (u.Close/u.c20-1)-(u.VNINDEX/u.v20-1) idio20, u.VNINDEX/u.v20-1 vn20,
        u.Volume_1M/NULLIF(u.Volume_3M_P50,0) volr, u.Close>=u.HI_3M_T1 newhi, u.Price*u.Volume_1M/1e9 liq_bn
      FROM u LEFT JOIN rt USING(ticker)),
s AS (SELECT x.*, PERCENTILE_CONT(mom20,0.5) OVER (PARTITION BY route) route_ret20_med,
        COUNT(*) OVER (PARTITION BY route) route_n, PERCENT_RANK() OVER (PARTITION BY route ORDER BY mom20) pct_in_route,
        PERCENTILE_CONT(mom20,0.5) OVER (PARTITION BY icb) icb_ret20_med, COUNT(*) OVER (PARTITION BY icb) icb_n FROM x)
SELECT * FROM s WHERE mom20>=0.20 AND idio20>=0.15 AND volr>=1.5 AND newhi AND liq_bn>=3 AND rating IS NOT NULL AND rating<=4
ORDER BY liq_bn DESC, ticker"""

def sql_freshness(T):
    return f"""SELECT (SELECT MAX(time) FROM tav2_bq.ticker AS t WHERE t.time>=DATE_SUB(DATE "{_date(T)}", INTERVAL 10 DAY)) tk,
 (SELECT MAX(time) FROM tav2_mike.universe_pit AS u WHERE u.time>=DATE_SUB(DATE "{T}", INTERVAL 10 DAY)) up"""

def sql_fin(T, tks):
    l = ",".join(f'"{t}"' for t in tks)
    return f"""SELECT f.ticker, f.quarter, f.Release_Date, f.NP_P0, f.NP_P4, f.Revenue_P0, f.Revenue_YoY_P0, f.GPM_P0, f.PE, f.PB, f.ROE_Trailing
  FROM tav2_bq.ticker_financial AS f WHERE f.ticker IN ({l}) AND f.Release_Date <= DATE "{_date(T)}"
  AND f.Release_Date >= DATE_SUB(DATE "{T}", INTERVAL 450 DAY)"""

def sql_news(T, tks):
    l = ",".join(f'"{t}"' for t in tks)   # LOC PIT THAT: ngay NAP (gio ICT) <= T, khong chi public_date
    return f"""SELECT n.ticker, n.public_date, n.public_datetime, n.title, n.matched_event_codes,
  DATE(n.ingested_at, "Asia/Ho_Chi_Minh") ingested_date
  FROM tav2_bq.stock_news AS n WHERE n.ticker IN ({l})
  AND n.public_date BETWEEN DATE_SUB(DATE "{_date(T)}", INTERVAL 120 DAY) AND DATE "{T}"
  AND DATE(n.ingested_at, "Asia/Ho_Chi_Minh") <= DATE "{T}"
  GROUP BY 1,2,3,4,5,6 ORDER BY 1,2"""

# ---------------------------------------------------------------- ledger (append-only, md5/dong, idempotent)
def _canon(rec): return json.dumps(rec, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
def line_md5(rec):
    return hashlib.md5(_canon({k: v for k, v in rec.items() if k != "md5"}).encode()).hexdigest()

class Ledger:
    def __init__(self, path): self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
    def read(self):
        if not self.path.exists(): return []
        rows = []
        for i, ln in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
            if not ln.strip(): continue
            r = json.loads(ln)
            if r.get("md5") != line_md5(r): raise RuntimeError(f"{self.path}:{i} md5 sai — ledger bi sua tay")
            rows.append(r)
        return rows
    def append(self, rec):
        """Them 1 dong neu event_id chua co. Khoa flock => 2 tien trinh song song khong nhan doi. Tra True neu ghi."""
        with open(str(self.path) + ".lock", "w") as lk:
            fcntl.flock(lk, fcntl.LOCK_EX)
            if any(r["event_id"] == rec["event_id"] for r in self.read()): return False
            rec = dict(rec); rec["md5"] = line_md5(rec)
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(_canon(rec) + "\n"); f.flush(); os.fsync(f.fileno())   # §5: ghi NGAY sau khi xong 1 su kien
            return True

# ---------------------------------------------------------------- su kien: cooldown + hang doi
def quarter_of(d): return (d.year, (d.month - 1) // 3)
def seed_history(path=HERE / "events.csv"):
    """Lich su cooldown tu events.csv (R4, PIT-greedy P0): {ticker: [date,...]}."""
    import csv
    h = {}
    if Path(path).exists():
        for r in csv.DictReader(open(path, encoding="utf-8")):
            if r["variant"] == "R4": h.setdefault(r["ticker"], []).append(dt.date.fromisoformat(r["time"][:10]))
    return h

def cooldown_ok(tk, T, hist):
    prev = [d for d in hist.get(tk, []) if d < T]
    if not prev: return True
    last = max(prev)
    return (T - last).days > COOLDOWN_DAYS and quarter_of(T) != quarter_of(last)

def week_key(d): return d.isocalendar()[:2]

def plan_day(T, cands, ledger_rows, seed):
    """Tra (processed[], skipped[]) cho ngay T. Tat dinh: cung dau vao => cung ket qua (idempotent khi chay lai)."""
    hist = {k: list(v) for k, v in seed.items()}
    for r in ledger_rows:
        hist.setdefault(r["ticker"], []).append(dt.date.fromisoformat(r["T"]))
    ok = sorted([c for c in cands if cooldown_ok(c["ticker"], T, hist)], key=lambda c: (-float(c["liq_bn"]), c["ticker"]))
    used = sum(1 for r in ledger_rows if r["status"] == "processed" and dt.date.fromisoformat(r["T"]) < T
               and week_key(dt.date.fromisoformat(r["T"])) == week_key(T))
    room = max(0, CAP_WEEK - used)
    return ok[:room], ok[room:]

# ---------------------------------------------------------------- goi PIT (whitelist; khong the lo outcome)
def _f(v):
    try: return None if v in (None, "") else float(v)
    except (TypeError, ValueError): return v
def build_packet(T, c, fin_rows, news_rows, dd_flag):
    Td = dt.date.fromisoformat(T)
    fin = sorted([r for r in fin_rows if r["ticker"] == c["ticker"] and str(r["Release_Date"])[:10] <= T],
                 key=lambda r: str(r["Release_Date"]))[-3:]
    news = [r for r in news_rows if r["ticker"] == c["ticker"] and str(r["public_date"])[:10] <= T
            and str(r["ingested_date"])[:10] <= T]
    p = {"event_id": f"{c['ticker']}_{T}", "ticker": c["ticker"], "T": T,
         "stats": {"mom20": _f(c["mom20"]), "idio20": _f(c["idio20"]), "volr": _f(c["volr"]), "newhi_3m": True,
                   "liq_bn": _f(c["liq_bn"]), "route_8l": c["route"], "rating_8l_asof": int(float(c["rating"])),
                   "rating_eff_date": str(c["rt_time"])[:10], "dd_flag": bool(dd_flag)},
         "sector_context": {"route_ret20_median": _f(c["route_ret20_med"]), "route_n": int(float(c["route_n"])),
                            "ticker_pct_in_route": _f(c["pct_in_route"]), "icb": c["icb"],
                            "icb_ret20_median": _f(c["icb_ret20_med"]), "icb_n": int(float(c["icb_n"])), "vnindex_ret20": _f(c["vn20"])},
         "financials_released_le_T": [{"quarter": r["quarter"], "Release_Date": str(r["Release_Date"])[:10],
              **{k: _f(r[k]) for k in ("NP_P0", "NP_P4", "Revenue_P0", "Revenue_YoY_P0", "GPM_P0", "PE", "PB", "ROE_Trailing")}} for r in fin],
         "news_le_T": [{"public_date": str(r["public_date"])[:10], "public_datetime": r["public_datetime"], "ingested_date": str(r["ingested_date"])[:10],
                        "title": r["title"], "codes": r["matched_event_codes"]} for r in news]}
    assert set(p) == PACKET_KEYS and not (FORBIDDEN_KEYS & _all_keys(p)), "goi co khoa cam (outcome)"
    return p
def _all_keys(o):
    if isinstance(o, dict): return set(o) | set().union(*[_all_keys(v) for v in o.values()]) if o else set()
    if isinstance(o, list): return set().union(*[_all_keys(v) for v in o]) if o else set()
    return set()

def dd_flag_of(tk, T, ff_rows):
    return tk in BANNED or any(r["ticker"] == tk and r["severity"] == "exclude" and r["date"] <= T for r in ff_rows)
def load_ff(path=WC / "data/forensic_flags.csv"):
    import csv
    return [{"ticker": r["ticker"], "severity": r["severity"], "date": r["date"][:10]} for r in csv.DictReader(open(path, encoding="utf-8"))] if Path(path).exists() else []

# ---------------------------------------------------------------- schema (validator toi gian, khong phu thuoc jsonschema)
def validate(obj, schema, path="$"):
    errs = []
    if "enum" in schema and obj not in schema["enum"]: errs.append(f"{path}: {obj!r} not in enum")
    t = schema.get("type")
    tmap = {"object": dict, "array": list, "string": str, "integer": int, "number": (int, float)}
    if t and (not isinstance(obj, tmap[t]) or isinstance(obj, bool)): return errs + [f"{path}: expected {t}"]
    if t == "number" or t == "integer":
        if "minimum" in schema and obj < schema["minimum"]: errs.append(f"{path}: < min")
        if "maximum" in schema and obj > schema["maximum"]: errs.append(f"{path}: > max")
    if t == "object":
        props = schema.get("properties", {})
        errs += [f"{path}.{k}: missing" for k in schema.get("required", []) if k not in obj]
        if schema.get("additionalProperties") is False: errs += [f"{path}.{k}: extra field" for k in obj if k not in props]
        for k, v in obj.items():
            if k in props: errs += validate(v, props[k], f"{path}.{k}")
    if t == "array":
        if "maxItems" in schema and len(obj) > schema["maxItems"]: errs.append(f"{path}: > maxItems")
        for i, v in enumerate(obj): errs += validate(v, schema.get("items", {}), f"{path}[{i}]")
    return errs

def evidence_dates_ok(m1, T):
    return all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", e["date"]) and e["date"] <= T for e in m1["evidence"])

# ---------------------------------------------------------------- M1: claude phien TRAN
def run_claude_m1(system, user, mode):
    """Phien tran: cwd tmp rong (khong CLAUDE.md), --setting-sources "" (khong hook/settings/skill), khong MCP, khong memory.
    retro => --tools "" (khong web). live => chi WebSearch. Do that: ~2,7k in + ~1,2k out/su kien, USD 0,023 (khong gom web)."""
    cmd = ["claude", "-p", "--model", "sonnet", "--effort", "medium", "--setting-sources", "", "--disable-slash-commands",
           "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}', "--system-prompt", system,
           "--tools", ("WebSearch" if mode == "live" else ""), "--no-session-persistence", "--output-format", "json"]
    with tempfile.TemporaryDirectory(prefix="am_m1_") as cwd:
        r = subprocess.run(cmd, input=user, capture_output=True, text=True, cwd=cwd, timeout=600,
                           env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": os.environ.get("HOME", "/home/trido"), "TZ": "Asia/Ho_Chi_Minh"})
    if r.returncode: raise RuntimeError(f"claude rc={r.returncode}: {r.stderr[-400:]}")
    d = json.loads(r.stdout)
    if d.get("is_error"): raise RuntimeError(f"claude error: {str(d.get('result'))[:300]}")
    return d["result"], {"cost_usd": d.get("total_cost_usd"), "usage": {k: d["usage"].get(k) for k in
            ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")}, "models": list(d.get("modelUsage", {}))}
M1_RUN = run_claude_m1

def _parse_json(txt):
    s = txt.strip()
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s)
    return json.loads(s)

def call_m1(packet, mode, schema_key="round1", extra=""):
    """Toi da 2 lan (lan 2 = nhac loi schema). Tra (obj|None, meta, err)."""
    user = ("CHE DO: " + mode + "\n" + extra + "\nGOI:\n" + json.dumps(packet, ensure_ascii=False)).strip()
    meta_all = []; err = None
    for attempt in range(2):
        try:
            txt, meta = M1_RUN(M1_SYSTEM + ("\n\n" + REBUT if schema_key == "final" else ""), user + (f"\nLOI LAN TRUOC (sua): {err}" if err else ""), mode); meta_all.append(meta)
            obj = _parse_json(txt)
            errs = validate(obj, SCHEMA[schema_key]) + ([] if obj.get("event_id", packet["event_id"]) == packet["event_id"] else ["event_id mismatch"])
            if isinstance(obj, dict): obj.setdefault("event_id", packet["event_id"])
            if not errs and not evidence_dates_ok(obj, packet["T"]): errs = ["evidence date > T"]
            if not errs: return obj, meta_all, None
            err = "; ".join(errs[:5])
        except Exception as e:     # fail-open: khong lam sap ca ngay
            err = f"{type(e).__name__}: {str(e)[:200]}"
    return None, meta_all, err

# ---------------------------------------------------------------- M2: adapter mong (doi che do khi Wags xong)
def m2_adapter(stage, packet, m1=None):
    """stage: 'blind' | 'challenge'. Tra {'status':'OK','data':{...}} hoac {'status':'FAIL','reason':...}.
    HIEN TAI fail-open (second_opinion.sh dang duoc Wags sua: che do prompt rieng + khong post bus; KHONG goi wrapper cu —
    no post bus 2 event/su kien). Khi Wags xong: thay than ham, giu nguyen hop dong tra ve + schema_M2.json."""
    mode = os.environ.get("AI_MOMENTUM_M2", "off")
    if mode == "off": return {"status": "FAIL", "reason": "adapter_not_enabled"}
    return {"status": "FAIL", "reason": f"unknown_mode:{mode}"}
M2 = m2_adapter

def run_m2(packet, m1):
    try:
        b = M2("blind", packet)
        if b.get("status") != "OK": return {"m2_status": "FAIL", "m2_reason": b.get("reason"), "blind": None, "challenge": None}
        c = M2("challenge", packet, m1)
        if c.get("status") != "OK": return {"m2_status": "FAIL", "m2_reason": c.get("reason"), "blind": b["data"], "challenge": None}
        return {"m2_status": "OK", "m2_reason": None, "blind": b["data"], "challenge": c["data"]}
    except Exception as e:
        return {"m2_status": "FAIL", "m2_reason": f"{type(e).__name__}: {str(e)[:150]}", "blind": None, "challenge": None}

def process_event(packet, mode):
    r1, meta1, err1 = call_m1(packet, mode, "round1")
    rec = {"event_id": packet["event_id"], "ticker": packet["ticker"], "T": packet["T"], "status": "processed", "mode": mode,
           "stats": packet["stats"], "m1_status": "OK" if r1 else "FAIL", "m1_error": err1, "m1_round1": r1,
           "packet_md5": hashlib.md5(_canon(packet).encode()).hexdigest(), "n_news": len(packet["news_le_T"]),
           "usage": meta1}
    if not r1:
        rec.update(m2_status="SKIPPED", final=None, b1=None); return rec
    rec["b1"] = {"view_20s": r1["view_20s"], "view_60s": r1["view_60s"], "driver_class": r1["driver_class"]}   # B1: truoc phan bien
    m2 = run_m2(packet, r1); rec.update(m2)
    final = r1
    ch = m2.get("challenge") or {}
    if m2["m2_status"] == "OK" and (ch.get("missed") or ch.get("disagree")):
        r2, meta2, err2 = call_m1(packet, mode, "final", "PHAN BIEN M2: " + json.dumps(ch, ensure_ascii=False) + "\nVONG 1 CUA BAN: " + json.dumps(r1, ensure_ascii=False))
        rec["usage"] = meta1 + meta2; rec["m1_rebuttal_error"] = err2
        if r2: final = r2
    rec["final"] = {k: final[k] for k in ("driver_class", "view_20s", "view_60s", "confidence", "dd_label") if k in final}
    rec["final"]["flipped_20s"] = final["view_20s"] != r1["view_20s"]
    rec["m1_final_full"] = final
    return rec

# ---------------------------------------------------------------- daily
def run_day(T, mode, ledger_dir, dry_run=False, seed=None, ff=None):
    Td = dt.date.fromisoformat(T); today = today_ict()
    if mode == "live" and Td != today: raise SystemExit(f"live chi cho T == hom nay ICT ({today}); T={T} -> dung --mode retro (khong gop vao N chinh)")
    fr = BQ(sql_freshness(T))[0]
    if not fr["tk"] or not fr["up"] or str(fr["tk"])[:10] < T or str(fr["up"])[:10] < T:
        raise SystemExit(f"du lieu BQ chua toi T={T} (ticker={fr['tk']}, universe_pit={fr['up']}) — doi sync 23:45 ICT; KHONG ghi gi")
    led = Ledger(Path(ledger_dir) / ("ai_momentum_events.jsonl" if mode == "live" else "ai_momentum_retro.jsonl"))
    rows = led.read(); seed = seed if seed is not None else seed_history(); ff = ff if ff is not None else load_ff()
    cands = BQ(sql_candidates(T))
    proc, skip = plan_day(Td, cands, rows, seed)
    out = {"T": T, "mode": mode, "n_candidates": len(cands), "processed": [c["ticker"] for c in proc], "skipped_capacity": [c["ticker"] for c in skip], "written": []}
    if dry_run or not (proc or skip): return out
    tks = [c["ticker"] for c in proc]
    fin = BQ(sql_fin(T, tks)) if tks else []; news = BQ(sql_news(T, tks)) if tks else []
    now = dt.datetime.now(ICT).isoformat(timespec="seconds")
    for c in skip:
        led.append({"event_id": f"{c['ticker']}_{T}", "ticker": c["ticker"], "T": T, "status": "skipped_capacity", "mode": mode,
                    "stats": {"liq_bn": _f(c["liq_bn"]), "route_8l": c["route"], "rating_8l_asof": int(float(c["rating"])),
                              "rating_eff_date": str(c["rt_time"])[:10], "rating_read_at": now}})
    for c in proc:
        if any(r["event_id"] == f"{c['ticker']}_{T}" for r in led.read()): continue     # idempotent: khong goi lai M1 (khong ton token)
        p = build_packet(T, c, fin, news, dd_flag_of(c["ticker"], T, ff))
        pdir = Path(ledger_dir) / ("packets" if mode == "live" else "packets_retro"); pdir.mkdir(parents=True, exist_ok=True)
        (pdir / f"{p['event_id']}.json").write_text(json.dumps(p, ensure_ascii=False, indent=1))
        rec = process_event(p, mode); rec["stats"]["rating_read_at"] = now
        if led.append(rec): out["written"].append(rec["event_id"])
    return out

# ---------------------------------------------------------------- scorer (khong peek giua cac moc look)
LOOKS = [("L1", 80), ("L2", 150)]; FINAL_N = 250
def gproc(rows):
    ok = [r for r in rows if r["status"] == "processed"]
    m1ok = [r for r in ok if r["m1_status"] == "OK"]
    n = len(ok)
    if not n: return {"n_processed": 0}
    ev_ok = sum(1 for r in m1ok if r["m1_round1"]["evidence"]) / n
    unk = sum(1 for r in m1ok if r["m1_round1"]["driver_class"] in ("UNKNOWN", "NARRATIVE_ONLY")) / n
    m2ok = [r for r in m1ok if r["m2_status"] == "OK"]
    dis = (sum(1 for r in m2ok if (r["challenge"] or {}).get("disagree") or (r["challenge"] or {}).get("missed")) / len(m2ok)) if m2ok else None
    flip = (sum(1 for r in m2ok if r["final"]["flipped_20s"]) / len(m2ok)) if m2ok else None
    cost = sum((m.get("cost_usd") or 0) for r in ok for m in r["usage"])
    return {"n_processed": n, "n_m1_fail": n - len(m1ok), "a_evidence_le_T": ev_ok, "b_unknown_or_narrative": unk, "m2_ok": len(m2ok),
            "c_disagree_rate": dis, "d_flip_rate": flip, "e_cost_usd_total": round(cost, 4)}

def _winsor(s): return s.clip(s.quantile(.01), s.quantile(.99))
def _bperm_p(y, lab, months, nperm=10000, seed=20261115):
    import numpy as np
    rng = np.random.default_rng(seed); y = np.asarray(y, float); lab = np.asarray(lab, bool)
    obs = y[lab].mean() - y[~lab].mean(); um = list(dict.fromkeys(months)); months = np.asarray(months)
    blocks = [lab[months == m] for m in um]; c = 0
    for _ in range(nperm):
        perm = np.concatenate([blocks[i] for i in rng.permutation(len(blocks))]); c += (y[perm].mean() - y[~perm].mean()) >= obs
    return obs, (c + 1) / (nperm + 1)

def effects(df):
    """T1/T2/T3 (PREREG s4) tren df da cham. Chi goi o moc look."""
    import numpy as np, pandas as pd
    out = {}; df = df.copy(); df["ym"] = df["T"].str[:7]
    if df.ym.nunique() < 6: return {"note": "<6 thang co su kien: chua tinh p (PREREG s4)"}
    d1 = df.dropna(subset=["ex20"]); y = _winsor(d1.ex20).to_numpy(); lab = (d1.v20 == "CONT").to_numpy()
    if lab.sum() >= 3 and (~lab).sum() >= 3: out["T1"] = dict(zip(("diff", "p_raw"), _bperm_p(y, lab, d1.ym.to_numpy()))) | {"min_econ": 0.05}
    d2 = df.dropna(subset=["ex60"]); y = _winsor(d2.ex60).to_numpy(); lab = d2.driver.isin(["EARNINGS", "CORP_ACTION"]).to_numpy()
    if lab.sum() >= 3 and (~lab).sum() >= 3: out["T2"] = dict(zip(("diff", "p_raw"), _bperm_p(y, lab, d2.ym.to_numpy()))) | {"min_econ": 0.08}
    d3 = df.dropna(subset=["ex20"]); d3 = d3[(d3.v20 != "NO_VIEW") | (d3.b1_v20 != "NO_VIEW")]
    hit = lambda v, e: ((v == "CONT") & (e > 0)) | ((v == "REV") & (e < 0))     # NO_VIEW = khong trung (v2 lam ro)
    if len(d3) >= 6:
        d = (hit(d3.v20, d3.ex20).astype(float) - hit(d3.b1_v20, d3.ex20).astype(float)).to_numpy()
        rng = np.random.default_rng(20261115); g = d3.ym.to_numpy(); um = list(dict.fromkeys(g)); obs = d.mean(); c = 0
        for _ in range(10000):
            sgn = {m: rng.choice([-1, 1]) for m in um}; c += np.mean([d[i] * sgn[g[i]] for i in range(len(d))]) >= obs
        out["T3"] = {"diff": float(obs), "p_raw": (c + 1) / 10001}
    return out

def score_report(rows, outcomes, now_date=None):
    """rows: ledger processed; outcomes: {event_id: {'ex20':..,'ex60':..}} chi cho su kien DU 61 phien.
    GIUA CAC MOC: chi tra N + G-proc (khong co khoa 'effects')."""
    import pandas as pd
    ok = [r for r in rows if r["status"] == "processed" and r["m1_status"] == "OK" and r["mode"] == "live"]
    sc = []
    for r in sorted(ok, key=lambda r: (r["T"], r["ticker"])):
        o = outcomes.get(r["event_id"])
        if o and o.get("ex60") is not None:
            sc.append({"event_id": r["event_id"], "T": r["T"], "ex20": o["ex20"], "ex60": o["ex60"], "driver": r["final"]["driver_class"],
                       "v20": r["final"]["view_20s"], "b1_v20": r["b1"]["view_20s"]})
    n_dir = [s for s in sc if s["v20"] in ("CONT", "REV")]
    rep = {"N_scored": len(sc), "N_dir_scored": len(n_dir), "G_proc": gproc(rows)}
    first = min((r["T"] for r in ok), default=None)
    months24 = bool(first and now_date and (dt.date.fromisoformat(now_date) - dt.date.fromisoformat(first)).days >= 730)
    look = None
    if len(sc) >= FINAL_N or months24: look = ("FINAL", sc)
    else:
        for name, nn in LOOKS:
            if len(n_dir) >= nn:                      # N look = su kien CO VIEW CO HUONG (PREREG v2 s2); mau dong bang = nn dau tien theo thoi gian
                look = (name, _first_n_dir(sc, nn))
    if look:
        rep["look"] = look[0]; rep["effects"] = effects(pd.DataFrame(look[1]))
    return rep

def _first_n_dir(sc, n):
    out, k = [], 0
    for s in sc:
        out.append(s); k += s["v20"] in ("CONT", "REV")
        if k >= n: break
    return out

def sql_outcomes(pairs):
    ds = sorted({t for _, t in pairs}); l = ",".join(f'"{tk}"' for tk, _ in pairs)
    lo, hi = ds[0], (dt.date.fromisoformat(ds[-1]) + dt.timedelta(days=130)).isoformat()
    return f"""WITH px AS (SELECT t.ticker, t.time, t.Close, LEAD(t.Close,1) OVER w c1, LEAD(t.Close,21) OVER w c21, LEAD(t.Close,61) OVER w c61
   FROM tav2_bq.ticker AS t JOIN tav2_mike.universe_pit AS u ON u.ticker=t.ticker AND u.time=t.time AND u.ruleset_version=1
   WHERE t.time BETWEEN DATE "{lo}" AND DATE "{hi}" AND t.ticker!="VNINDEX" AND u.in_universe
   WINDOW w AS (PARTITION BY t.ticker ORDER BY t.time)),
 rt AS (SELECT r.ticker, r.time rt_time, r.route, LEAD(r.time) OVER (PARTITION BY r.ticker ORDER BY r.time) rt_next FROM tav2_bq.fa_ratings_8l AS r),
 x AS (SELECT p.*, rt.route, p.c21/p.c1-1 r20, p.c61/p.c1-1 r60 FROM px p LEFT JOIN rt ON rt.ticker=p.ticker AND rt.rt_time<=p.time AND (rt.rt_next IS NULL OR rt.rt_next>p.time)),
 med AS (SELECT time, route, APPROX_QUANTILES(r20,2)[OFFSET(1)] m20, APPROX_QUANTILES(r60,2)[OFFSET(1)] m60 FROM x WHERE route IS NOT NULL GROUP BY 1,2)
 SELECT x.ticker, CAST(x.time AS STRING) T, x.r20-m.m20 ex20, x.r60-m.m60 ex60 FROM x JOIN med m ON m.time=x.time AND m.route=x.route
 WHERE x.ticker IN ({l}) AND x.time IN ({",".join(f'DATE "{d}"' for d in ds)})"""

def fetch_outcomes(rows):
    pairs = [(r["ticker"], r["T"]) for r in rows if r["status"] == "processed" and r["mode"] == "live"]
    if not pairs: return {}
    return {f"{o['ticker']}_{o['T']}": {"ex20": _f(o["ex20"]), "ex60": _f(o["ex60"])} for o in BQ(sql_outcomes(pairs))}

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--date"); ap.add_argument("--mode", choices=["live", "retro"])
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--score", action="store_true")
    ap.add_argument("--ledger-dir", default=str(WC / "mike/data/ai_momentum")); a = ap.parse_args(argv)
    today = today_ict().isoformat()
    if a.score:
        rows = Ledger(Path(a.ledger_dir) / "ai_momentum_events.jsonl").read()
        print(json.dumps(score_report(rows, fetch_outcomes(rows), today), ensure_ascii=False, indent=1, default=str)); return 0
    T = _date(a.date or today); mode = a.mode or ("live" if T == today else "retro")
    print(json.dumps(run_day(T, mode, a.ledger_dir, a.dry_run), ensure_ascii=False, indent=1)); return 0

if __name__ == "__main__":
    sys.exit(main())
