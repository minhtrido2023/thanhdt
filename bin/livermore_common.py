#!/usr/bin/env python3
"""Lõi dùng chung của bộ Livermore "đọc sống" (livermore_trigger_check.py / livermore_run.sh /
livermore_score.py): lịch phiên HOSE, dữ liệu VNINDEX, parse RESULT, sổ registry append-only.

Đặc tả: user duyệt 2026-10-22. Registry: kb/data_registry/market-state/livermore_reads.md.
Luật: §5 (ghi atomic, idempotent), §16 (neo ICT, KHÔNG datetime.now() trần), §14 (freshness thật).

Hook kiểm thử (chỉ có tác dụng khi LIVERMORE_TEST=1 cho đồng hồ; còn lại là override đường dẫn):
  LIVERMORE_NOW=<iso ICT>   đồng hồ giả          LIVERMORE_BARS_CSV   bars thay cho BQ
  LIVERMORE_DT5G_CSV        state DT5G thay BQ   LIVERMORE_REGISTRY / _DATA_DIR / _STATE_DIR
"""
import csv
import datetime as dt
import fcntl
import io
import os
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))      # .../mike (hoặc worktree)
WC_ROOT = os.path.dirname(ROOT)                                          # .../WorkingClaude
PROJECT = "lithe-record-440915-m9"
REGISTRY = os.environ.get("LIVERMORE_REGISTRY") or os.path.join(
    ROOT, "kb", "data_registry", "market-state", "livermore_reads.md")
DATA_DIR = os.environ.get("LIVERMORE_DATA_DIR") or os.path.join(ROOT, "data", "livermore")
STATE_DIR = os.environ.get("LIVERMORE_STATE_DIR") or os.path.join(ROOT, "state")
HORIZON = 20            # phiên
PKG_BARS = 500          # số phiên OHLCV đưa cho Livermore
FREEZE_HOUR = 19        # DT5G publish ~19:01 ICT; trước giờ này phiên hôm nay chưa "đóng sổ"

# Ngày nghỉ HOSE mà trading_bot.vn_market chưa có (nó chỉ có lễ cố định + bù Quốc khánh 2026).
# CHƯA có thông báo chính thức của HOSE cho 2027 ⇒ các ngày dưới đây là ƯỚC LƯỢNG (calendar=ESTIMATE).
# Đáo hạn thật luôn được scorer xác nhận lại bằng bar thực (20 bar sau as_of), nên sai lệch lịch
# chỉ làm lệch ngày DỰ KIẾN, không làm sai điểm.
EXTRA_HOLIDAYS_ESTIMATE = (
    {dt.date(2027, 2, 1) + dt.timedelta(days=i) for i in range(0, 12)}   # Tết Đinh Mùi ~01-12/02/2027
    | {dt.date(2027, 4, 16)}                                              # Giỗ Tổ 10/3 ÂL
)
CONFIRMED_THROUGH = dt.date(2026, 12, 31)    # lịch vn_market coi là đủ đến hết 2026


def now_ict():
    if os.environ.get("LIVERMORE_TEST") == "1" and os.environ.get("LIVERMORE_NOW"):
        return dt.datetime.fromisoformat(os.environ["LIVERMORE_NOW"]).replace(tzinfo=ICT)
    return dt.datetime.now(ICT)


def today_ict():
    return now_ict().date()


# ───────────────────────── lịch phiên ─────────────────────────
_VM = None


def _vm():
    global _VM
    if _VM is None:
        if WC_ROOT not in sys.path:
            sys.path.insert(0, WC_ROOT)
        from trading_bot import vn_market          # fail loud nếu thiếu — không tự đoán lịch
        _VM = vn_market
    return _VM


def is_session(d):
    return d.weekday() < 5 and not _vm().is_holiday(d) and d not in EXTRA_HOLIDAYS_ESTIMATE


def next_session(d):
    d += dt.timedelta(days=1)
    while not is_session(d):
        d += dt.timedelta(days=1)
    return d


def prev_session(d):
    d -= dt.timedelta(days=1)
    while not is_session(d):
        d -= dt.timedelta(days=1)
    return d


def add_sessions(d, n):
    """→ (ngày đáo hạn, 'CONFIRMED'|'ESTIMATE'). ESTIMATE nếu khoảng đi qua hết 2026."""
    start = d
    for _ in range(n):
        d = next_session(d)
    return d, ("CONFIRMED" if d <= CONFIRMED_THROUGH and start <= CONFIRMED_THROUGH else "ESTIMATE")


def expected_last_session(now=None):
    """Phiên gần nhất mà dữ liệu NÊN đã có: hôm nay nếu là phiên và đã qua FREEZE_HOUR, ngược lại phiên trước."""
    now = now or now_ict()
    d = now.date()
    if is_session(d) and now.hour >= FREEZE_HOUR:
        return d
    return prev_session(d)


# ───────────────────────── dữ liệu ─────────────────────────
def _bq_env():
    env = dict(os.environ)
    env.setdefault("CLOUDSDK_CONFIG", "/home/trido/thanhdt/gcloud_dtienthanh")
    env["PATH"] = env.get("PATH", "") + ":/home/trido/google-cloud-sdk/bin"
    return env


def bq_rows(sql, max_rows=5000):
    r = subprocess.run(["bq", "query", "--use_legacy_sql=false", f"--project_id={PROJECT}",
                        "--format=csv", f"--max_rows={max_rows}", sql],
                       capture_output=True, text=True, timeout=120, env=_bq_env())
    if r.returncode != 0:
        raise RuntimeError(f"bq lỗi rc={r.returncode}: {r.stderr.strip()[:400]}")
    return list(csv.DictReader(io.StringIO(r.stdout)))


def _bar(row):
    return {"time": dt.date.fromisoformat(row["time"][:10]), "open": float(row["Open"]),
            "high": float(row["High"]), "low": float(row["Low"]), "close": float(row["Close"]),
            "volume": float(row["Volume"])}


def get_bars(start, end=None):
    """VNINDEX OHLCV [start, end], tăng dần theo ngày. Bảng `ticker` (không forward col)."""
    p = os.environ.get("LIVERMORE_BARS_CSV")
    if p:
        with open(p, encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
    else:
        cond = f"t.time >= DATE '{start}'" + (f" AND t.time <= DATE '{end}'" if end else "")
        rows = bq_rows("SELECT t.time, t.Open, t.High, t.Low, t.Close, t.Volume "
                       f"FROM tav2_bq.ticker AS t WHERE t.ticker = 'VNINDEX' AND {cond} ORDER BY t.time")
    bars = [_bar(r) for r in rows]
    bars = [b for b in bars if b["time"] >= start and (end is None or b["time"] <= end)]
    bars.sort(key=lambda b: b["time"])
    return bars


def get_dt5g_state(day):
    """State DT5G (1..5) tại `day` từ vnindex_5state_dt5g_live (KHÔNG phải bảng không hậu tố); None nếu thiếu."""
    p = os.environ.get("LIVERMORE_DT5G_CSV")
    if p:
        with open(p, encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
    else:
        rows = bq_rows("SELECT t.time, t.state FROM tav2_bq.vnindex_5state_dt5g_live AS t "
                       f"WHERE t.time = DATE '{day}'")
    for r in rows:
        if r["time"][:10] == str(day):
            return int(float(r["state"]))
    return None


# ───────────────────────── file ─────────────────────────
def atomic_write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def locked_append(path, text, guard=None):
    """Append-only an toàn: khoá flock, đọc, guard(content)->str|None (lý do từ chối), ghi atomic.
    Trả True nếu đã ghi, False nếu guard từ chối (idempotent)."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path + ".lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        cur = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        if guard and guard(cur):
            return False
        if cur and not cur.endswith("\n"):
            cur += "\n"
        atomic_write(path, cur + text)
        return True


# ───────────────────────── registry ─────────────────────────
_HDR = re.compile(r"^### LVR-(\d{4}-\d{2}-\d{2})\s*$", re.M)


def read_registry():
    return open(REGISTRY, encoding="utf-8").read() if os.path.exists(REGISTRY) else ""


def parse_entries(text):
    out = []
    ms = list(_HDR.finditer(text))
    for i, m in enumerate(ms):
        body = text[m.end(): ms[i + 1].start() if i + 1 < len(ms) else len(text)]
        body = re.split(r"^SCORE\|", body, maxsplit=1, flags=re.M)[0]

        def f(key):
            mm = re.search(rf"^- {key}:[ \t]*(.*)$", body, re.M)
            return mm.group(1).strip() if mm else ""
        res = re.search(r"^- result:\s*(RESULT\|\S+)\s*$", body, re.M)
        due = re.match(r"(\d{4}-\d{2}-\d{2})\s*\(calendar=(\w+)\)", f("due"))
        parts = res.group(1).split("|") if res else []
        if len(parts) != 5 or not due:
            continue            # entry hỏng — scorer không đoán
        out.append({"as_of": dt.date.fromisoformat(m.group(1)), "trigger": f("trigger"),
                    "close": float(f("close_asof")), "due": dt.date.fromisoformat(due.group(1)),
                    "calendar": due.group(2), "dir": parts[2], "p_up": float(parts[3]), "level": parts[4]})
    return out


def parse_scores(text):
    return {m.group(1): m.group(0) for m in re.finditer(r"^SCORE\|(\d{4}-\d{2}-\d{2})\|.*$", text, re.M)}


def has_entry(text, as_of):
    return f"### LVR-{as_of}" in text


class ResultError(ValueError):
    pass


def parse_forecast(report, as_of):
    """Đọc báo cáo của Livermore → dict. Fail LOUD (ResultError) với mọi lệch — không ghi entry nửa vời."""
    blocks = re.findall(r"<<<FORECAST\n(.*?)\nFORECAST>>>", report, re.S)
    if len(blocks) != 1:
        raise ResultError(f"cần đúng 1 khối <<<FORECAST...FORECAST>>>, thấy {len(blocks)}")
    block = blocks[0]
    for key in ("H20_DIR", "H20_P_UP", "LEVEL", "INVALIDATION"):
        if not re.search(rf"^\s*[-*]?\s*`?{key}`?\s*[:=]", block, re.M):
            raise ResultError(f"khối FORECAST thiếu trường {key}")
    lines = re.findall(r"^RESULT\|[^\n]*$", report, re.M)
    if len(lines) != 1:
        raise ResultError(f"cần đúng 1 dòng RESULT|..., thấy {len(lines)}")
    parts = lines[0].strip().split("|")
    if len(parts) != 5:
        raise ResultError(f"RESULT phải có 5 trường, thấy {len(parts)}: {lines[0]!r}")
    _, rid, d, p, lvl = parts
    if rid != str(as_of):
        raise ResultError(f"RESULT id={rid!r} ≠ as_of {as_of}")
    if d not in ("UP", "DOWN"):
        raise ResultError(f"RESULT dir={d!r} không phải UP/DOWN")
    if lvl not in ("HOLD", "BREAK"):
        raise ResultError(f"RESULT level={lvl!r} không phải HOLD/BREAK")
    try:
        pu = float(p)
    except ValueError:
        raise ResultError(f"RESULT P_UP={p!r} không phải số")
    if not (0.0 <= pu <= 1.0):
        raise ResultError(f"RESULT P_UP={pu} ngoài [0,1]")
    if (d == "UP" and pu < 0.5) or (d == "DOWN" and pu > 0.5):
        raise ResultError(f"RESULT tự mâu thuẫn: {d} với P_UP={pu}")
    m = re.search(r"H20_DIR\W+(UP|DOWN)\b", block)
    if not m or m.group(1) != d:
        raise ResultError(f"H20_DIR trong khối ({m.group(1) if m else None}) ≠ RESULT ({d})")
    m = re.search(r"H20_P_UP\W+([0-9.]+)", block)
    if not m or abs(float(m.group(1).rstrip('.')) - pu) > 0.005:
        raise ResultError(f"H20_P_UP trong khối ({m.group(1) if m else None}) ≠ RESULT ({pu})")
    return {"dir": d, "p_up": pu, "level": lvl, "block": block, "result": lines[0].strip()}


def format_entry(as_of, triggers, close, due, cal, report_rel, fc, created):
    ind = "\n".join("    " + ln for ln in fc["block"].splitlines())
    return (f"\n### LVR-{as_of}\n- as_of: {as_of}\n- created: {created}\n- trigger: {','.join(triggers)}\n"
            f"- close_asof: {close}\n- due: {due} (calendar={cal})\n- report: {report_rel}\n"
            f"- forecast:\n{ind}\n- result: {fc['result']}\n- outcome:\n")


# ───────────────────────── gói dữ liệu & prompt ─────────────────────────
def build_package(as_of, out_path):
    """CSV 500 phiên OHLCV VNINDEX đến as_of (gồm). Không DT5G, không bar sau as_of."""
    start = as_of - dt.timedelta(days=PKG_BARS * 2)
    bars = [b for b in get_bars(start, as_of) if b["time"] <= as_of]
    if not bars or bars[-1]["time"] != as_of:
        got = bars[-1]["time"] if bars else None
        raise RuntimeError(f"as-of lệch: không có bar đúng {as_of} (bar cuối={got})")
    bars = bars[-PKG_BARS:]
    if len(bars) < 260:
        raise RuntimeError(f"thiếu lịch sử: chỉ {len(bars)} bar (<260)")
    buf = ["time,open,high,low,close,volume"] + [
        f"{b['time']},{b['open']},{b['high']},{b['low']},{b['close']},{b['volume']:.0f}" for b in bars]
    atomic_write(out_path, "\n".join(buf) + "\n")
    return bars


def build_prompt(as_of, pkg_path):
    return f"""AS_OF = {as_of}. Dữ liệu duy nhất của bạn: file CSV {pkg_path} (500 phiên OHLCV VNINDEX, dòng cuối = as-of).
ĐỌC MÙ: chỉ Read file đó. KHÔNG đọc bất kỳ file nào khác, KHÔNG đọc vnindex_5state*, dt_gate, DT5G, registry,
KHÔNG tra tin tức/web, KHÔNG dùng dữ liệu sau {as_of}. Bỏ bước 5 (so DT5G) — bạn không được cho xem.
Viết báo cáo đúng cấu trúc bắt buộc của agent Livermore (mục 1-4: AS_OF, phân loại 3 thang, bảng vùng, FORECAST).
Cuối báo cáo, theo ĐÚNG khuôn máy đọc sau (không thêm gì sau dòng RESULT):

<<<FORECAST
- H20_DIR: UP|DOWN
- H20_P_UP: 0.00-1.00
- LEVEL: <một mức giá> HOLD|BREAK trong 20 phiên
- INVALIDATION: <giá/hành vi vô hiệu hoá>
FORECAST>>>
RESULT|{as_of}|<UP hoặc DOWN>|<P_UP>|<HOLD hoặc BREAK>

RESULT phải khớp H20_DIR / H20_P_UP / LEVEL ở trên (UP ⇒ P_UP ≥ 0.5, DOWN ⇒ P_UP ≤ 0.5)."""


# ───────────────────────── CLI cho livermore_run.sh ─────────────────────────
def _cli(argv):
    cmd = argv[1] if len(argv) > 1 else ""
    if cmd == "package":                      # package <as_of|-> <out_csv>  → in as_of dùng
        a = argv[2]
        if a == "-":
            a = str(expected_last_session())
        as_of = dt.date.fromisoformat(a)
        if as_of < expected_last_session() and os.environ.get("LIVERMORE_ALLOW_PAST") != "1":
            raise RuntimeError(f"as-of {as_of} cũ hơn phiên kỳ vọng {expected_last_session()} "
                               "(đặt LIVERMORE_ALLOW_PAST=1 nếu cố ý)")
        bars = build_package(as_of, argv[3])
        print(f"{as_of} {len(bars)} bars close={bars[-1]['close']}")
    elif cmd == "prompt":                     # prompt <as_of> <pkg_csv>
        print(build_prompt(dt.date.fromisoformat(argv[2]), argv[3]))
    elif cmd == "finalize":                   # finalize <as_of> <report_md> <triggers_csv>
        as_of = dt.date.fromisoformat(argv[2])
        report = open(argv[3], encoding="utf-8").read()
        fc = parse_forecast(report, as_of)    # ResultError ⇒ rc≠0, KHÔNG ghi gì
        bars = get_bars(as_of, as_of)
        if not bars:
            raise RuntimeError(f"không đọc lại được bar as-of {as_of}")
        due, cal = add_sessions(as_of, HORIZON)
        rep_path = os.path.join(DATA_DIR, f"{as_of}.md")
        rel = f"mike/data/livermore/{as_of}.md" if DATA_DIR == os.path.join(ROOT, "data", "livermore") else rep_path
        if has_entry(read_registry(), as_of):
            print(f"EXISTS LVR-{as_of}")
            return
        atomic_write(rep_path, report)          # báo cáo TRƯỚC, entry SAU: kill giữa chừng không để entry mồ côi
        entry = format_entry(as_of, [t for t in argv[4].split(",") if t] or ["MANUAL"], bars[0]["close"],
                             due, cal, rel, fc, now_ict().isoformat(timespec="seconds"))
        wrote = locked_append(REGISTRY, entry, guard=lambda c: has_entry(c, as_of))
        print(("WROTE" if wrote else "EXISTS") + f" LVR-{as_of} due={due} calendar={cal}")
    else:
        raise SystemExit(f"usage: {argv[0]} package|prompt|finalize ...")


if __name__ == "__main__":
    try:
        _cli(sys.argv)
    except (ResultError, RuntimeError) as e:
        print(f"LIVERMORE-FAIL: {e}", file=sys.stderr)
        sys.exit(1)
