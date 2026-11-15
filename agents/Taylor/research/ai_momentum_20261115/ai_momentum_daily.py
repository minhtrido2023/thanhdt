#!/usr/bin/env python3
"""ai_momentum_daily.py — P1 BUILD (PREREG v3 + v3.1 + v3.2; khoa md5 = PREREG_v3_2.md5). Paper-only: KHONG lenh, KHONG plan, KHONG state_*.json.
Luong: su kien moi ngay T (PREREG s1) -> hang doi <=10/tuan -> goi PIT -> M1 (claude phien TRAN) -> M2 (adapter, fail-open) -> ghi JSONL
append-only (md5/dong, idempotent). Lich su cooldown + cap tuan TAT DINH tu BQ (T-200..T-1), KHONG phu thuoc luot chay nao thanh cong.
  python3 ai_momentum_daily.py --date 2026-11-16 [--mode live|retro] [--dry-run] [--ledger-dir DIR]
  python3 ai_momentum_daily.py --score [--ledger-dir DIR]
Exit: 0 ok | 3 khong phai ngay giao dich | 4 BQ chua ve/chua day | 5 loi ha tang M1 (KHONG ghi dong, chay lai duoc) | 6 co luot khac dang chay | 1 loi that.
PIT: moi SQL chi doc <= T (khong LEAD/profit_*; selfcheck bat). Cron: KHONG cai o P1."""
import os; os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, datetime as dt, fcntl, hashlib, json, re, signal, subprocess, sys, tempfile
from pathlib import Path
from zoneinfo import ZoneInfo
ICT = ZoneInfo("Asia/Ho_Chi_Minh")          # coding_guidelines §16: neo TZ tuong minh
HERE = Path(__file__).resolve().parent
WC = Path("/home/trido/thanhdt/WorkingClaude")
BQ_PROJECT = "lithe-record-440915-m9"
BANNED = "PC1 VVS KSF NKG HSG HVN VJC NVL GEG SBA DMC IMP TRA TOS VTP BAF".split()

class InfraError(RuntimeError): """Loi HA TANG (CLI/auth/usage/timeout/khong co binary): DUNG luot chay, KHONG ghi dong, chay lai duoc."""
class NotTradingDay(Exception): pass
class DataNotReady(Exception): pass
class Busy(Exception): pass

# ---- THAM SO GIAO THUC (hash vao khoa md5: doi bat ky cai nao = PREREG moi, khong chay) ----
M1_MODEL, M1_EFFORT, M1_TIMEOUT = "sonnet", "medium", 600          # alias 'sonnet' co the troi => ledger ghi model thuc te (usage.models) tung dong
M1_MAX_TURNS = {"live": 8, "retro": 2}; M1_MAX_BUDGET_USD = "0.60"
M2_MODEL = "opencode/deepseek-v4.1-flash-free"; M2_TIMEOUT = 240; M2_RETRIES = 1; M2_BACKOFF = 5
M2_OUTER = (M2_RETRIES + 1) * M2_TIMEOUT + M2_BACKOFF + 60            # tran ngoai subprocess = (retries+1)*timeout + backoff + bien
HIST_DAYS = 200; FRESH_RATIO = 0.95
NO_TOOL_LINE = "KHONG goi tool nao, tra loi truc tiep bang JSON (mot object JSON duy nhat, khong markdown)."   # thieu dong nay -> model goi glob roi TREO
FORMAT_HINT = {   # deepseek tu bia ten truong neu khong co khung (do that 16/11) => khung CHINH XAC theo schema_M2.json
    "blind": 'Dinh dang tra loi: DUNG MOT object JSON {"event_id": "<event_id>", "blind_driver": mot trong [EARNINGS, CORP_ACTION, SECTOR_MACRO, FLOW_INDEX, NARRATIVE_ONLY, UNKNOWN], '
             '"blind_view_20s": mot trong [CONT, REV, NO_VIEW], "blind_view_60s": mot trong [CONT, REV, NO_VIEW], "evidence": ["<chuoi: phan tu cua goi + ngay <= T>", ...]}. Khong them truong khac.',
    "challenge": 'Dinh dang tra loi: DUNG MOT object JSON {"event_id": "<event_id>", "missed": [{"item": "<yeu to M1 bo qua>", "source": "<phan tu cua goi>", "date": "YYYY-MM-DD", "verifiable": true|false}], '
                 '"disagree": [{"m1_field": "<ten truong cua M1>", "why": "<ly do>", "source": "<phan tu cua goi>", "verifiable": true|false}]}. Khong tim duoc => mang rong []. Khong them truong khac.'}

def m1_argv(mode, system=""):
    """Phien tran: cwd tmp rong (khong CLAUDE.md), --setting-sources "" (khong hook/settings/skill), khong MCP, khong memory.
    retro => --tools "" (khong web). live => chi WebSearch (--allowedTools de chay duoc o che do -p)."""
    live = mode == "live"
    cmd = ["claude", "-p", "--model", M1_MODEL, "--effort", M1_EFFORT, "--setting-sources", "", "--disable-slash-commands",
           "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}', "--system-prompt", system,
           "--tools", ("WebSearch" if live else ""), "--no-session-persistence", "--output-format", "json",
           "--max-turns", str(M1_MAX_TURNS[mode]), "--max-budget-usd", M1_MAX_BUDGET_USD]
    return cmd + (["--allowedTools", "WebSearch"] if live else [])

def protocol_consts():
    return {"m1_argv": {m: m1_argv(m) for m in ("live", "retro")}, "m1_timeout": M1_TIMEOUT, "m2_model": M2_MODEL, "m2_timeout": M2_TIMEOUT,
            "m2_retries": M2_RETRIES, "m2_outer": M2_OUTER, "hist_days": HIST_DAYS, "fresh_ratio": FRESH_RATIO, "no_tool_line": NO_TOOL_LINE, "format_hint": FORMAT_HINT}
def _consts_md5(): return hashlib.md5(json.dumps(protocol_consts(), sort_keys=True, ensure_ascii=False).encode()).hexdigest()

# ---- PREREG v3.2: MOT khoa md5 cho moi file giao thuc + hang so. Lech/thieu => khong chay (fail-closed, khong fallback).
LOCKED_FILES = ("PREREG_v3.md", "PREREG_v3_1.md", "PREREG_v3_2.md", "prereg_v3.json", "events_v3.csv", "prompt_M1_v2.md", "prompt_M1_rebuttal_v2.md",
                "schema_M1_v2.json", "prompt_M2_blind.md", "prompt_M2_challenge.md", "schema_M2.json")
def _md5b(b): return hashlib.md5(b).hexdigest()
def _md5f(p): return _md5b(Path(p).read_bytes())
def _load_locked():
    raw = (HERE / "PREREG_v3_2.md5").read_bytes()
    lock = {ln.split()[1]: ln.split()[0] for ln in raw.decode().splitlines() if ln.strip()}
    blobs = {}
    for f in LOCKED_FILES:
        b = (HERE / f).read_bytes()          # doc 1 lan: hash va noi dung la CUNG bytes
        if lock.get(f) != _md5b(b): raise SystemExit(f"PREREG v3.2 lech khoa md5: {f} (khong chay; sua giao thuc = PREREG moi)")
        blobs[f] = b
    if lock.get("CONST_PROTOCOL") != _consts_md5(): raise SystemExit("PREREG v3.2 lech khoa md5: CONST_PROTOCOL (hang so giao thuc doi: M1/M2 argv, model, timeout, FORMAT_HINT...)")
    return blobs, lock, _md5b(raw)
_BLOBS, _LOCK, PROTOCOL_MD5 = _load_locked()
PREREG_MD5 = _LOCK["PREREG_v3_2.md"]
V3 = json.loads(_BLOBS["prereg_v3.json"])
PREREG_VERSION = "v3.2"
CAP_WEEK = V3["cap_week"]
COOLDOWN_DAYS = V3["cooldown_days"]
PACKET_KEYS = {"event_id", "ticker", "T", "stats", "sector_context", "financials_released_le_T", "news_le_T"}
FORBIDDEN_KEYS = {"ex20", "ex60", "r20", "r60", "c1", "c21", "c61", "profit_2W", "profit_1M", "profit_2M", "profit_3M"}
M1_SYSTEM = _BLOBS["prompt_M1_v2.md"].decode("utf-8")
REBUT = _BLOBS["prompt_M1_rebuttal_v2.md"].decode("utf-8")
SCHEMA = json.loads(_BLOBS["schema_M1_v2.json"])
assert M1_SYSTEM.strip() and REBUT.strip() and SCHEMA, "prompt/schema M1 rong"

def _repo_root():
    """Repo root cua CHINH worktree nay (khong hardcode canonical): di len tu HERE toi thu muc co bin/second_opinion.sh."""
    for p in [HERE, *HERE.parents]:
        if (p / "bin" / "second_opinion.sh").is_file(): return p
    raise FileNotFoundError("bin/second_opinion.sh khong thay tu " + str(HERE))

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
      ON up.ticker=b.ticker AND up.time=b.time AND up.ruleset_version={V3["universe_ruleset"]}
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
SELECT * FROM s WHERE mom20>={V3["mom20"]} AND idio20>={V3["idio20"]} AND volr>={V3["volr"]} AND newhi AND liq_bn>={V3["liq_bn"]} AND rating IS NOT NULL AND rating<={V3["rating_max"]}
ORDER BY liq_bn DESC, ticker"""

def sql_freshness(T):
    """/* marker FRESHNESS */ MAX(time) + DO DAY (so dong T vs phien truoc do) cho ca ticker va universe_pit(in_universe)."""
    T = _date(T)
    return f"""/* FRESHNESS */
WITH tk AS (SELECT t.time, COUNT(*) n FROM tav2_bq.ticker AS t WHERE t.time BETWEEN DATE_SUB(DATE "{T}", INTERVAL 15 DAY) AND DATE "{T}" AND t.ticker != "VNINDEX" GROUP BY 1),
 up AS (SELECT u.time, COUNT(*) n FROM tav2_mike.universe_pit AS u WHERE u.time BETWEEN DATE_SUB(DATE "{T}", INTERVAL 15 DAY) AND DATE "{T}"
        AND u.ruleset_version={V3["universe_ruleset"]} AND u.in_universe GROUP BY 1)
SELECT (SELECT MAX(time) FROM tk) tk, (SELECT n FROM tk WHERE time=DATE "{T}") tk_n, (SELECT n FROM tk WHERE time=(SELECT MAX(time) FROM tk WHERE time<DATE "{T}")) tk_prev,
 (SELECT MAX(time) FROM up) up, (SELECT n FROM up WHERE time=DATE "{T}") up_n, (SELECT n FROM up WHERE time=(SELECT MAX(time) FROM up WHERE time<DATE "{T}")) up_prev"""

def freshness_problem(fr, T):
    """None neu du lieu da toi T VA du day; nguoc lai chuoi mo ta NOI SUY tu so doc duoc (coding_guidelines §29)."""
    for name, k in (("ticker", "tk"), ("universe_pit", "up")):
        mx, n, pv = fr.get(k), fr.get(k + "_n"), fr.get(k + "_prev")
        if not mx or str(mx)[:10] < T: return f"{name}: MAX(time)={mx} < T={T}"
        if n in (None, "") or pv in (None, ""): return f"{name}: thieu dem dong (n_T={n}, n_phien_truoc={pv})"
        if float(n) < FRESH_RATIO * float(pv): return f"{name}: so dong tai T={n} < {FRESH_RATIO:.0%} cua phien truoc ({pv})"
    return None

def sql_eligible_range(T):
    """-- ELIG_RANGE: cac (ticker, ngay) DU DIEU KIEN su kien (cung bo loc voi sql_candidates) trong [T-HIST_DAYS, T-1]. Chi doc <= T-1."""
    T = _date(T)
    return f"""/* ELIG_RANGE */
WITH base AS (
  SELECT t.ticker, t.time, t.Close, t.Price, t.Volume_1M, t.Volume_3M_P50, t.HI_3M_T1, t.VNINDEX,
    LAG(t.Close,20) OVER w c20, LAG(t.VNINDEX,20) OVER w v20
  FROM tav2_bq.ticker AS t
  WHERE t.time BETWEEN DATE_SUB(DATE "{T}", INTERVAL {HIST_DAYS + 60} DAY) AND DATE_SUB(DATE "{T}", INTERVAL 1 DAY) AND t.ticker != "VNINDEX"
  WINDOW w AS (PARTITION BY t.ticker ORDER BY t.time)),
u AS (SELECT b.* FROM base b JOIN tav2_mike.universe_pit AS up
      ON up.ticker=b.ticker AND up.time=b.time AND up.ruleset_version={V3["universe_ruleset"]}
      WHERE b.time >= DATE_SUB(DATE "{T}", INTERVAL {HIST_DAYS} DAY) AND up.in_universe),
rt AS (SELECT r.ticker, r.time rt_time, r.rating, LEAD(r.time) OVER (PARTITION BY r.ticker ORDER BY r.time) rt_next
       FROM tav2_bq.fa_ratings_8l AS r WHERE r.time <= DATE_SUB(DATE "{T}", INTERVAL 1 DAY)),
x AS (SELECT u.ticker, u.time, rt.rating, u.Close/u.c20-1 mom20, (u.Close/u.c20-1)-(u.VNINDEX/u.v20-1) idio20,
        u.Volume_1M/NULLIF(u.Volume_3M_P50,0) volr, u.Close>=u.HI_3M_T1 newhi, u.Price*u.Volume_1M/1e9 liq_bn
      FROM u JOIN rt ON rt.ticker=u.ticker AND rt.rt_time<=u.time AND (rt.rt_next IS NULL OR rt.rt_next>u.time))
SELECT x.ticker, CAST(x.time AS STRING) time, x.liq_bn FROM x
WHERE mom20>={V3["mom20"]} AND idio20>={V3["idio20"]} AND volr>={V3["volr"]} AND newhi AND liq_bn>={V3["liq_bn"]} AND rating IS NOT NULL AND rating<={V3["rating_max"]}
ORDER BY x.time, x.ticker"""

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
            rec = dict(rec)
            if (rec.setdefault("prereg_version", PREREG_VERSION) != PREREG_VERSION or rec.setdefault("prereg_md5", PREREG_MD5) != PREREG_MD5
                    or rec.setdefault("protocol_md5", PROTOCOL_MD5) != PROTOCOL_MD5):
                raise RuntimeError("dong ledger mang prereg/protocol khac hien hanh")
            rec["md5"] = line_md5(rec)
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(_canon(rec) + "\n"); f.flush(); os.fsync(f.fileno())   # §5: ghi NGAY sau khi xong 1 su kien
            return True

# ---------------------------------------------------------------- su kien: cooldown + hang doi
def quarter_of(d): return (d.year, (d.month - 1) // 3)

def cooldown_ok(tk, T, hist):
    prev = [d for d in hist.get(tk, []) if d < T]
    if not prev: return True
    last = max(prev)
    return (T - last).days > COOLDOWN_DAYS and quarter_of(T) != quarter_of(last)

def week_key(d): return d.isocalendar()[:2]

def replay_history(elig, T):
    """TAT DINH tu BQ, khong dung ledger: elig = [{ticker,time,liq_bn}] ngay du dk trong [T-HIST_DAYS, T-1].
    Greedy per-ma (cooldown tinh tu SU KIEN da phat, y het build_events.greedy) => (hist {ticker:[date]}, used = so su kien da XU LY trong tuan ISO cua T)."""
    rows = sorted(((dt.date.fromisoformat(str(r["time"])[:10]), r["ticker"], float(r["liq_bn"])) for r in elig), key=lambda x: (x[0], x[1]))
    hist, per_day = {}, {}
    for d, tk, liq in rows:
        if d >= T: continue                       # chi qua khu: khong bao gio doc T tro di
        h = hist.setdefault(tk, [])
        if not h or ((d - h[-1]).days > COOLDOWN_DAYS and quarter_of(d) != quarter_of(h[-1])):
            h.append(d); per_day.setdefault(d, []).append((-liq, tk))
    used = 0
    for d in sorted(per_day):
        if week_key(d) == week_key(T): used += min(max(0, CAP_WEEK - used), len(per_day[d]))
    return hist, used

def plan_day(T, cands, hist, used):
    """Tra (processed[], skipped[]) cho ngay T. Tat dinh: chi phu thuoc (cands, hist, used) tu BQ."""
    ok = sorted([c for c in cands if cooldown_ok(c["ticker"], T, hist)], key=lambda c: (-float(c["liq_bn"]), c["ticker"]))
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
    tmap = {"object": dict, "array": list, "string": str, "integer": int, "number": (int, float), "boolean": bool}
    if t and (not isinstance(obj, tmap[t]) or (isinstance(obj, bool) and t != "boolean")): return errs + [f"{path}: expected {t}"]
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
INFRA_RE = re.compile(r"auth|login|log in|credential|api key|usage limit|rate.?limit|quota|overloaded|credit|billing|\b401\b|\b429\b|\b529\b", re.I)
def run_claude_m1(system, user, mode):
    """Loi HA TANG (khong co binary, timeout, rc!=0, stdout khong phai JSON, is_error kieu auth/usage/rate limit) => InfraError.
    is_error khac (het max-turns/budget...) la loi NOI DUNG cua su kien -> RuntimeError (ghi m1_status=FAIL)."""
    try:
        with tempfile.TemporaryDirectory(prefix="am_m1_") as cwd:
            r = subprocess.run(m1_argv(mode, system), input=user, capture_output=True, text=True, cwd=cwd, timeout=M1_TIMEOUT,
                               env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": os.environ.get("HOME", "/home/trido"), "TZ": "Asia/Ho_Chi_Minh"})
    except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired, OSError) as e:
        raise InfraError(f"claude khong chay duoc: {type(e).__name__}: {str(e)[:200]}") from e
    if r.returncode: raise InfraError(f"claude rc={r.returncode}: {r.stderr[-400:]} {r.stdout[-200:]}")
    try: d = json.loads(r.stdout)
    except ValueError as e: raise InfraError(f"claude stdout khong phai JSON: {r.stdout[:200]!r}") from e
    if d.get("is_error"):
        msg = str(d.get("result"))[:300]
        if INFRA_RE.search(msg): raise InfraError(f"claude is_error (ha tang): {msg}")
        raise RuntimeError(f"claude is_error: {msg}")
    return d["result"], {"cost_usd": d.get("total_cost_usd"), "usage": {k: d["usage"].get(k) for k in
            ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")}, "models": list(d.get("modelUsage", {})),
            "num_turns": d.get("num_turns"), "web_search_requests": ((d.get("usage") or {}).get("server_tool_use") or {}).get("web_search_requests")}
M1_RUN = run_claude_m1

def _parse_json(txt):
    s = txt.strip()
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s)
    return json.loads(s)

def call_m1(packet, mode, schema_key="round1", extra=""):
    """Toi da 2 lan (lan 2 = nhac loi schema). Tra (obj|None, meta, err). InfraError KHONG bi nuot: noi len de dung luot chay."""
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
        except InfraError: raise
        except Exception as e:     # loi NOI DUNG (parse/schema): fail-open, ghi FAIL
            err = f"{type(e).__name__}: {str(e)[:200]}"
    return None, meta_all, err

# ---------------------------------------------------------------- M2: deepseek qua bin/second_opinion.sh --raw-prompt-file (Wags, 39d490f3e)
M2_PROMPT = {"blind": "prompt_M2_blind.md", "challenge": "prompt_M2_challenge.md"}
M2_SCHEMA = json.loads(_BLOBS["schema_M2.json"])["properties"]

def build_m2_prompt(stage, packet, m1=None):
    """Blind: prompt + no-tool + GOI (TUYET DOI khong M1). Challenge: prompt + no-tool + GOI + JSON M1."""
    parts = [_BLOBS[M2_PROMPT[stage]].decode("utf-8").strip(), NO_TOOL_LINE, FORMAT_HINT[stage],
             "Chi 1 su kien duoi day; tra MOT object JSON co event_id = " + packet["event_id"] + ".", "GOI:\n" + json.dumps(packet, ensure_ascii=False, indent=1)]
    if stage == "challenge": parts.append("JSON CUA M1:\n" + json.dumps(m1, ensure_ascii=False, indent=1))
    return "\n\n".join(parts) + "\n"

def run_second_opinion(prompt_file, out_jsonl, text_out, timeout=M2_TIMEOUT):
    """Tra (rc, stderr_tail). TMPDIR tro vao thu muc tam cua adapter => /tmp/so-raw.* bi don cung; bi qua tran ngoai => kill ca nhom tien trinh."""
    cmd = [str(_repo_root() / "bin" / "second_opinion.sh"), "--raw-prompt-file", str(prompt_file), "--out", str(out_jsonl), "--text-out", str(text_out),
           "--model", M2_MODEL, "--timeout", str(timeout), "--retries", str(M2_RETRIES)]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True,
                         env=dict(os.environ, TMPDIR=str(Path(out_jsonl).parent)))
    try: _, err = p.communicate(timeout=M2_OUTER)
    except subprocess.TimeoutExpired:
        try: os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError: pass
        p.communicate(); raise
    return p.returncode, (err or "")[-300:]
M2_RUN = run_second_opinion

def m2_dates_ok(stage, obj, T):
    """Giong M1: moi ngay M2 viet ra phai la YYYY-MM-DD va <= T (blind.evidence: moi chuoi co ngay; challenge.missed[].date: bat buoc dung dinh dang)."""
    if stage == "blind":
        return all(d <= T for e in obj.get("evidence", []) for d in re.findall(r"\d{4}-\d{2}-\d{2}", str(e)))
    return all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(x.get("date", ""))) and x["date"] <= T for x in obj.get("missed", []))

def m2_adapter(stage, packet, m1=None):
    """stage: 'blind' | 'challenge'. Tra {'status':'OK','data':..,'raw_text':..,'stderr_tail':..} hoac {'status':'FAIL','reason':..}.
    Fail-open: moi loi (exit 10/11/12/2, parse, schema, ngay>T, timeout) => FAIL (T1/T2 van cham, loai khoi T3). Khong WebSearch."""
    if os.environ.get("AI_MOMENTUM_M2", "on") == "off": return {"status": "FAIL", "reason": "adapter_disabled"}
    assert stage in ("blind", "challenge"); assert stage == "blind" or m1 is not None
    with tempfile.TemporaryDirectory(prefix="am_m2_") as d:
        d = Path(d); pf, rj, tx = d / "prompt.md", d / "raw.jsonl", d / "text.txt"
        pf.write_text(build_m2_prompt(stage, packet, m1), encoding="utf-8")
        try: rc, tail = M2_RUN(pf, rj, tx, M2_TIMEOUT)
        except subprocess.TimeoutExpired: return {"status": "FAIL", "reason": "timeout_subprocess"}
        if rc != 0: return {"status": "FAIL", "reason": f"second_opinion_exit_{rc}: {tail[-200:]}", "stderr_tail": tail}
        raw = rj.read_text(encoding="utf-8") if rj.exists() else ""
        txt = tx.read_text(encoding="utf-8") if tx.exists() else ""
        try:
            obj = _parse_json(txt)
            if isinstance(obj, list) and len(obj) == 1: obj = obj[0]
            if isinstance(obj, dict): obj.setdefault("event_id", packet["event_id"])
            errs = validate(obj, M2_SCHEMA[stage]) + ([] if isinstance(obj, dict) and obj.get("event_id") == packet["event_id"] else ["event_id mismatch"])
            if not errs and not m2_dates_ok(stage, obj, packet["T"]): errs = ["date > T"]
        except Exception as e: return {"status": "FAIL", "reason": f"parse_fail:{type(e).__name__}", "raw_text": txt[:20000], "stderr_tail": tail}
        if errs: return {"status": "FAIL", "reason": "schema:" + "; ".join(errs[:3]), "raw_text": txt[:20000], "stderr_tail": tail}
        return {"status": "OK", "data": obj, "raw_text": txt[:20000], "raw_jsonl_bytes": len(raw), "stderr_tail": tail}
M2 = m2_adapter

def run_m2(packet, m1):
    """Blind chay TRUOC va KHONG nhan m1. Raw text + duoi stderr wrapper luu vao ledger (m2_raw / m2_log), ca khi FAIL."""
    raw, log = {}, {}
    base = {"m2_model": M2_MODEL, "m2_raw": raw, "m2_log": log}
    try:
        b = M2("blind", packet); raw["blind"] = b.get("raw_text"); log["blind"] = b.get("stderr_tail")
        if b.get("status") != "OK": return {**base, "m2_status": "FAIL", "m2_reason": "blind:" + str(b.get("reason")), "blind": None, "challenge": None}
        c = M2("challenge", packet, m1); raw["challenge"] = c.get("raw_text"); log["challenge"] = c.get("stderr_tail")
        if c.get("status") != "OK": return {**base, "m2_status": "FAIL", "m2_reason": "challenge:" + str(c.get("reason")), "blind": b["data"], "challenge": None}
        return {**base, "m2_status": "OK", "m2_reason": None, "blind": b["data"], "challenge": c["data"]}
    except Exception as e:
        return {**base, "m2_status": "FAIL", "m2_reason": f"{type(e).__name__}: {str(e)[:150]}", "blind": None, "challenge": None}

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
def is_trading_day(d):
    """Thu 2-6 va khong phai ngay le (trading_bot.vn_market.is_holiday). Khong import duoc => loi that (fail-closed), KHONG doan."""
    if d.weekday() >= 5: return False
    sys.path.insert(0, str(WC))
    from trading_bot.vn_market import is_holiday
    return not is_holiday(d)
IS_TRADING_DAY = is_trading_day

class run_lock:
    """flock KHONG CHO tren <ledger_dir>/.run.lock cho CA luot chay: chay tay + cron cung luc khong goi M1 hai lan."""
    def __init__(self, ledger_dir): Path(ledger_dir).mkdir(parents=True, exist_ok=True); self.p = Path(ledger_dir) / ".run.lock"
    def __enter__(self):
        self.f = open(self.p, "w")
        try: fcntl.flock(self.f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: self.f.close(); raise Busy(f"co luot chay khac dang giu {self.p}")
        return self
    def __exit__(self, *a): self.f.close()

def m2_fail_streak(rows):
    """So dong processed (live) lien tiep o CUOI ledger co m2_status != OK (de wrapper canh bao khi >=3)."""
    n = 0
    for r in reversed([r for r in rows if r["status"] == "processed" and r.get("mode") == "live" and r.get("m1_status") == "OK"]):
        if r.get("m2_status") == "OK": break
        n += 1
    return n

def run_day(T, mode, ledger_dir, dry_run=False, elig=None, ff=None):
    Td = dt.date.fromisoformat(T); today = today_ict()
    if mode == "live" and Td != today: raise SystemExit(f"live chi cho T == hom nay ICT ({today}); T={T} -> dung --mode retro (khong gop vao N chinh)")
    if not IS_TRADING_DAY(Td): raise NotTradingDay(f"{T} khong phai ngay giao dich (T7/CN/le)")
    fr = BQ(sql_freshness(T))[0]
    prob = freshness_problem(fr, T)
    if prob: raise DataNotReady(f"BQ chua san sang cho T={T}: {prob}; KHONG ghi gi")
    if dry_run: return _run_day(Td, T, mode, ledger_dir, True, elig, ff)
    with run_lock(ledger_dir): return _run_day(Td, T, mode, ledger_dir, False, elig, ff)

def _run_day(Td, T, mode, ledger_dir, dry_run, elig, ff):
    led = Ledger(Path(ledger_dir) / ("ai_momentum_events.jsonl" if mode == "live" else "ai_momentum_retro.jsonl"))
    ff = ff if ff is not None else load_ff()
    elig = elig if elig is not None else BQ(sql_eligible_range(T))
    hist, used = replay_history(elig, Td)            # TAT DINH tu BQ: khong doc ledger de tinh cooldown/cap
    cands = BQ(sql_candidates(T))
    proc, skip = plan_day(Td, cands, hist, used)
    out = {"T": T, "mode": mode, "n_candidates": len(cands), "n_used_week_before": used, "processed": [c["ticker"] for c in proc],
           "skipped_capacity": [c["ticker"] for c in skip], "written": [], "m1_fail": 0, "m2_fail": 0, "infra_stop": None}
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
        try: rec = process_event(p, mode)
        except InfraError as e:        # ha tang hong: DUNG, khong ghi dong nao cho su kien nay => chay lai se lam lai dung su kien nay
            out["infra_stop"] = f"{p['event_id']}: {str(e)[:300]}"; break
        rec["stats"]["rating_read_at"] = now
        if led.append(rec):
            out["written"].append(rec["event_id"]); out["m1_fail"] += rec["m1_status"] != "OK"; out["m2_fail"] += rec.get("m2_status") == "FAIL"
    out["m2_fail_streak"] = m2_fail_streak(led.read())
    return out

# ---------------------------------------------------------------- scorer (khong peek giua cac moc look)
LOOKS = [("L1", 80), ("L2", 150)]; FINAL_N = 250
def gproc(rows):
    ok = [r for r in rows if r["status"] == "processed" and r.get("protocol_md5") == PROTOCOL_MD5 and r.get("mode") == "live"]
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

def _ticker_sens(d, nboot=10000, seed=20261115):
    """(a) bootstrap CUM THEO MA (resample ma, giu moi su kien cua ma) -> CI 95% cua chenh T1; (b) chenh T1 chi su kien DAU TIEN moi ma."""
    import numpy as np
    rng = np.random.default_rng(seed); g = d.assign(w=d.lab.astype(float)).groupby("ticker")
    S1 = g.apply(lambda x: (x.y * x.w).sum()).to_numpy(); N1 = g.w.sum().to_numpy()          # nhom CONT
    S0 = g.apply(lambda x: (x.y * (1 - x.w)).sum()).to_numpy(); N0 = g.size().to_numpy() - N1
    def diff(i):
        n1, n0 = N1[i].sum(), N0[i].sum()
        return S1[i].sum() / n1 - S0[i].sum() / n0 if n1 > 0 and n0 > 0 else np.nan
    k = len(S1); bs = np.array([diff(rng.integers(0, k, k)) for _ in range(nboot)])
    first = d.sort_values("T").groupby("ticker").head(1)
    fd = first.y[first.lab].mean() - first.y[~first.lab].mean() if first.lab.any() and (~first.lab).any() else float("nan")
    return {"n_tickers": int(k), "n_events": len(d), "diff_all": float(diff(np.arange(k))), "boot_ci95": [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))],
            "diff_first_per_ticker": float(fd), "n_first": len(first), "role": "descriptive_not_in_BH_family"}

def effects(df):
    """T1/T2/T3 (PREREG s4) tren df da cham. Chi goi o moc look."""
    import numpy as np, pandas as pd
    out = {}; df = df.copy(); df["ym"] = df["T"].str[:7]
    if df.ym.nunique() < 6: return {"note": "<6 thang co su kien: chua tinh p (PREREG s4)"}
    d1 = df.dropna(subset=["ex20"]); y = _winsor(d1.ex20).to_numpy(); lab = (d1.v20 == "CONT").to_numpy()
    if lab.sum() >= 3 and (~lab).sum() >= 3: out["T1"] = dict(zip(("diff", "p_raw"), _bperm_p(y, lab, d1.ym.to_numpy()))) | {"min_econ": 0.05}
    d2 = df.dropna(subset=["ex60"]); y = _winsor(d2.ex60).to_numpy(); lab = d2.driver.isin(["EARNINGS", "CORP_ACTION"]).to_numpy()
    if lab.sum() >= 3 and (~lab).sum() >= 3: out["T2"] = dict(zip(("diff", "p_raw"), _bperm_p(y, lab, d2.ym.to_numpy()))) | {"min_econ": 0.08}
    if "T1" in out and "ticker" in df:      # v3 s2: do nhay cum theo ma — MO TA, KHONG vao ho BH (PREREG_v3 s3)
        out["T1_ticker_sensitivity"] = _ticker_sens(d1.assign(y=_winsor(d1.ex20), lab=(d1.v20 == "CONT")))
    d3 = df.dropna(subset=["ex20"]); d3 = d3[d3.m2_ok.astype(bool) & ((d3.v20 != "NO_VIEW") | (d3.b1_v20 != "NO_VIEW"))]   # T3 so sanh co/khong M2 => chi su kien M2 OK
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
    ok = [r for r in rows if r["status"] == "processed" and r["m1_status"] == "OK" and r["mode"] == "live" and r.get("protocol_md5") == PROTOCOL_MD5]
    sc = []
    for r in sorted(ok, key=lambda r: (r["T"], r["ticker"])):
        o = outcomes.get(r["event_id"])
        if o and o.get("ex60") is not None:
            sc.append({"event_id": r["event_id"], "T": r["T"], "ticker": r["ticker"], "ex20": o["ex20"], "ex60": o["ex60"], "driver": r["final"]["driver_class"],
                       "v20": r["final"]["view_20s"], "b1_v20": r["b1"]["view_20s"], "m2_ok": r.get("m2_status") == "OK"})
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
   FROM tav2_bq.ticker AS t JOIN tav2_mike.universe_pit AS u ON u.ticker=t.ticker AND u.time=t.time AND u.ruleset_version={V3["universe_ruleset"]}
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
    ap.add_argument("--ledger-dir", default=str(_repo_root() / "data" / "ai_momentum")); a = ap.parse_args(argv)
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))      # de TemporaryDirectory/finally chay khi bi `timeout` giet
    today = today_ict().isoformat()
    try:
        if a.score:
            rows = Ledger(Path(a.ledger_dir) / "ai_momentum_events.jsonl").read()
            print(json.dumps(score_report(rows, fetch_outcomes(rows), today), ensure_ascii=False, indent=1, default=str)); return 0
        T = _date(a.date or today); mode = a.mode or ("live" if T == today else "retro")
        out = run_day(T, mode, a.ledger_dir, a.dry_run)
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return 5 if out.get("infra_stop") else 0
    except NotTradingDay as e: print(f"EXIT3 {e}", file=sys.stderr); return 3
    except DataNotReady as e: print(f"EXIT4 {e}", file=sys.stderr); return 4
    except Busy as e: print(f"EXIT6 {e}", file=sys.stderr); return 6
    except InfraError as e: print(f"EXIT5 {e}", file=sys.stderr); return 5
    except Exception:
        import traceback; traceback.print_exc(); return 1

if __name__ == "__main__":
    sys.exit(main())
