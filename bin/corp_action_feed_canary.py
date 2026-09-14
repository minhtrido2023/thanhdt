#!/usr/bin/env python3
"""corp_action_feed_canary.py — canary WARN-ONLY cho feed vendor `tav2_bq.corporate_action`.

VÌ SAO TỒN TẠI (job `Taylor_20260914_173213`, user duyệt 2026-09-15 00:31 ICT)
-------------------------------------------------------------------------------
Branch `test/oshares-freeze-live-selfchecks` đóng băng các selfcheck chạm BQ sống trong cổng
publish của `corp_action_daily`. arch-reviewer chỉ ra thứ bị mất: đổi CẤU TRÚC vẫn nổ to lúc
chạy thật (`bq()` raise → rc=5), nhưng **drift mức GIÁ TRỊ thì im lặng** — vendor đổi tên giá
trị `event_code`/`event_status` ⇒ mọi `WHERE event_status = "executed"` âm thầm trả ít dòng hơn,
`triggered_today` âm thầm bỏ cảnh báo, không bất biến nào bắt được "hôm nay không có sự kiện".

WARN-ONLY TUYỆT ĐỐI: script này KHÔNG import/đụng state, file publish hay `_FAILED` của
`corp_action_daily`. Nó chỉ ĐỌC BQ, in log, và post Discord topic `architecture` khi có WARN.

BỐN KIỂM TRA (mỗi mục ra PASS/WARN kèm số đọc được — §29, không hardcode nguyên nhân)
---------------------------------------------------------------------------------
(a) SCHEMA  — cột code THẬT SỰ đọc tồn tại đúng kiểu. Danh sách cột KHÔNG gõ tay: trích bằng
    `ast` từ đúng các hàm dựng SQL (`SQL_SOURCES`) mỗi lần chạy; chỉ KIỂU là pin
    (`EXPECTED_TYPES`, đo INFORMATION_SCHEMA 2026-09-15). Code đọc cột mới chưa pin ⇒ WARN để
    người cập nhật canary, không lặng lẽ bỏ qua.
(b) GIÁ TRỊ — tập `event_code`/`event_status` toàn bảng: giá trị chưa từng thấy ⇒ WARN; giá
    trị code lọc theo mà biến mất ⇒ WARN. Giá trị code cần = pin + trích từ code (regex trên
    chính SQL/so sánh Python) — hợp của hai.
    Cửa sổ gần đây (`public_date` ≥ hôm nay − 45 ngày) chỉ bắt buộc có DIV/ISS/AIS/executed.
    Căn cứ 45 ngày: min cuốn chiếu 2019-03→2026-09 (đo 2026-09-15 trên bảng hiện tại) —
    cửa sổ 30 ngày có AIS = 0 (2021-08-29); 45 ngày: DIV≥30, ISS≥15, AIS≥7, executed≥82.
    `announced`/`not_executed` KHÔNG bắt buộc trong cửa sổ: nhiều tháng liền = 0 (not_executed
    0 dòng mọi tháng 2026-06→09) — bắt buộc sẽ báo động giả; chúng chỉ phải còn trong toàn bảng.
    Lưu ý: bảng được vendor nạp lại TOÀN BỘ mỗi đêm (MAX=MIN `ingested_at` cùng một ngày), nên
    đổi tên giá trị kiểu rewrite sẽ hiện ra ở cả toàn bảng lẫn cửa sổ.
(c) HOẠT ĐỘNG — số dòng ISS(exright_date)/AIS(effective_date) `executed` trong
    `ACTIVITY_SESSIONS`=10 phiên VN liền trước hôm nay > 0. Căn cứ: đếm bằng ĐÚNG lịch canary
    dùng (T2-T6 trừ `trading_bot.vn_market.is_holiday`, Tết âm lịch KHÔNG khai báo ⇒ tính như
    phiên), mọi cửa sổ 2019-01→2026-09-14: N=5 → 7 cửa sổ rỗng (toàn quanh Tết), N=6 → 1
    (Tết 2022), N=8 → 0, N=10 → 0. Chọn 10 = mức sạch nhỏ nhất + 2 phiên đệm. Đổi lại: (c) phát
    hiện chậm ≤10 phiên — đổi tên giá trị thì (b) bắt ngay lượt sau.
(d) LỊCH SỬ  — 5 tổng `AIS.shares_total_after` đã chốt, không bao giờ nên đổi (kiểm lại trên BQ
    2026-09-15 trước khi pin, 1 dòng/khoá): đổi/biến mất/nhân đôi ⇒ WARN (vendor rewrite lịch sử).

Canary tự hỏng (BQ auth, không đọc được code...) ⇒ WARN "CANARY KHÔNG CHẠY ĐƯỢC" kèm stderr
thật, không đoán nguyên nhân.

Mã thoát: 0 = toàn PASS (1 dòng log, không post) · 1 = có WARN (đã post) · 2 = canary lỗi (đã
post) · 3 = post Discord thất bại (`NOTIFY_FAILED`). Không mã nào ảnh hưởng `corp_action_daily`.

Dùng:  python3 mike/bin/corp_action_feed_canary.py [--dry-run] [--asof YYYY-MM-DD]
Selfcheck: `corp_action_feed_canary_selfcheck.py` (hermetic, không BQ).
Registry: `mike/kb/data_registry/price-volume/corporate_action_bq.md`.
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import os
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from wc_paths import find_wc_root  # noqa: E402

WC_ROOT = find_wc_root(__file__)
if WC_ROOT not in sys.path:
    sys.path.insert(0, WC_ROOT)

# Cùng lý do `corp_action_daily.py:133`: canary phải nhìn BQ SỐNG, không cache T-1 của wc_env.sh.
os.environ.pop("BQ_LOCAL_CACHE", None)

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
TABLE = "lithe-record-440915-m9.tav2_bq.corporate_action"
DATASET = "lithe-record-440915-m9.tav2_bq"
NOTIFY_TOPIC = "architecture"

# Hàm dựng SQL đọc `corporate_action` trên đường production của corp_action_daily. Chỉ các mảnh
# chuỗi KHÔNG chứa `SKIP_MARKER` (truy vấn `ticker_financial` nằm chung `_fetch`).
SQL_SOURCES = (
    (os.path.join(WC_ROOT, "corp_action_lib.py"), "feed_freshness"),
    (os.path.join(WC_ROOT, "corp_action_lib.py"), "_events"),
    (os.path.join(WC_ROOT, "corp_action_lib.py"), "events"),
    (os.path.join(WC_ROOT, "corp_action_lib.py"), "pricing_events"),
    (os.path.join(WC_ROOT, "oshares_live.py"), "_fetch"),
    (os.path.join(HERE, "corp_action_daily.py"), "_events_on_sql"),
)
SKIP_MARKER = "{FIN_TABLE}"

# File quét so sánh giá trị phía Python (`r["event_code"] == "AIS"`, `.get("event_status") != …`).
VALUE_SCAN_FILES = (
    os.path.join(WC_ROOT, "corp_action_lib.py"),
    os.path.join(WC_ROOT, "oshares_live.py"),
    os.path.join(HERE, "corp_action_daily.py"),
)

# Kiểu cột, đo `INFORMATION_SCHEMA.COLUMNS` 2026-09-15 00:3x ICT. Chỉ các cột code đọc.
EXPECTED_TYPES = {
    "id": "STRING", "ticker": "STRING", "event_code": "STRING", "event_status": "STRING",
    "exright_date": "DATE", "effective_date": "DATE", "listing_date": "DATE",
    "public_date": "DATE", "ingested_at": "TIMESTAMP",
    "value_per_share": "FLOAT64", "exercise_ratio": "FLOAT64",
    "issue_method_name_vi": "STRING", "event_title_vi": "STRING",
    "issue_volumn": "INT64", "shares_delta": "INT64", "shares_total_after": "INT64",
}

# Tập giá trị toàn bảng đã thấy (GROUP BY đo 2026-09-15). Ngoài tập ⇒ WARN "giá trị mới".
KNOWN_CODES = {"DIV", "ISS", "AIS", "NLIS", "SUSP", "MOVE", "MA"}
KNOWN_STATUSES = {"announced", "executed", "not_executed"}
# Pin giá trị code cần (hợp với phần trích từ code lúc chạy):
#   DIV/ISS: `corp_action_lib.events` codes mặc định; ISS/AIS: `oshares_live._fetch` WHERE;
#   AIS: `corp_action_daily.triggered_today`/`upcoming_events`.
#   executed: `_fetch`, `events(executed_only)`; not_executed: `pricing_events`,
#   `_events_on_sql`; announced: `corp_action_daily` nhãn *(dự kiến)* (`!= "executed"`).
REQUIRED_CODES = {"DIV", "ISS", "AIS"}
REQUIRED_STATUSES = {"executed", "announced", "not_executed"}
RECENT_DAYS = 45
RECENT_REQUIRED = {("code", "DIV"), ("code", "ISS"), ("code", "AIS"), ("status", "executed")}

ACTIVITY_SESSIONS = 10

# (ticker, effective_date, shares_total_after) — AIS executed, kiểm lại BQ 2026-09-15, n=1/khoá.
# Sàn suy từ tiêu đề dòng: "Niêm yết bổ sung" (HOSE/HNX) vs "Đăng ký giao dịch bổ sung" (UPCOM).
AIS_PINS = (
    ("FPT", "2025-09-12", 1_703_507_121),   # HOSE
    ("VCB", "2025-05-09", 8_355_675_094),   # HOSE, ngân hàng
    ("SHS", "2025-06-13", 894_462_220),     # HNX
    ("MBS", "2024-10-31", 547_079_981),     # HNX
    ("ACV", "2025-09-29", 3_582_847_523),   # UPCOM ("Đăng ký giao dịch bổ sung")
)

_SQL_WORDS = {
    "select", "from", "where", "and", "or", "in", "is", "not", "null", "cast", "as", "string",
    "date", "max", "min", "count", "substr", "coalesce", "order", "by", "true", "false",
    "between", "limit", "desc", "asc", "group", "on", "join", "distinct", "countif",
}


# ── (0) đọc code ──────────────────────────────────────────────────────────────────────────
def _string_pieces(path, func):
    """Mọi hằng chuỗi / f-string trong thân hàm `func` (bỏ docstring), placeholder giữ `{expr}`."""
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), filename=path)
    fn = next((n for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == func), None)
    if fn is None:
        raise LookupError(f"không thấy hàm `{func}` trong {path}")
    body = fn.body
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None),
                                                               ast.Constant):
        body = body[1:]
    inner = set()
    pieces = []
    for stmt in body:
        for node in ast.walk(stmt):
            if isinstance(node, ast.JoinedStr):
                parts = []
                for v in node.values:
                    if isinstance(v, ast.Constant):
                        parts.append(str(v.value))
                        inner.add(id(v))
                    elif isinstance(v, ast.FormattedValue):
                        parts.append("{" + ast.unparse(v.value) + "}")
                        for sub in ast.walk(v):
                            inner.add(id(sub))
                pieces.append("".join(parts))
            elif isinstance(node, ast.Constant) and isinstance(node.value, str) \
                    and id(node) not in inner:
                pieces.append(node.value)
    return [p for p in pieces if SKIP_MARKER not in p]


def columns_in_sql(text):
    """Tên cột trong một mảnh SQL: bỏ placeholder/chuỗi/alias/từ khoá."""
    t = re.sub(r"\{[^{}]*\}", " ", text)
    t = re.sub(r'"[^"]*"|\'[^\']*\'|`[^`]*`', " ", t)
    t = re.sub(r"\bAS\s+[A-Za-z_]\w*", " ", t, flags=re.I)
    t = re.sub(r"\)\s*[A-Za-z_]\w*", ")", t)
    return {w for w in re.findall(r"\b[A-Za-z_]\w*\b", t)
            if w.lower() not in _SQL_WORDS and not w.isupper()}


def code_columns(sources=SQL_SOURCES):
    """{cột: [nguồn...]} — trích mỗi lần chạy, KHÔNG gõ tay."""
    out = {}
    for path, func in sources:
        for piece in _string_pieces(path, func):
            for c in columns_in_sql(piece):
                out.setdefault(c, []).append(f"{os.path.basename(path)}::{func}")
    return out


def code_values(sources=SQL_SOURCES, scan_files=VALUE_SCAN_FILES):
    """({code: nguồn}, {status: nguồn}) giá trị code so sánh/lọc — SQL + so sánh Python."""
    codes, statuses = {}, {}
    for path, func in sources:
        where = f"{os.path.basename(path)}::{func}"
        for piece in _string_pieces(path, func):
            for v in re.findall(r'event_status\s*!?=\s*"(\w+)"', piece):
                statuses.setdefault(v, where)
            for grp in re.findall(r'event_code\s+IN\s*\(([^)]*)\)', piece):
                for v in re.findall(r'"(\w+)"', grp):
                    codes.setdefault(v, where)
    for path in scan_files:
        name = os.path.basename(path)
        with open(path, encoding="utf-8") as fh:
            for ln, line in enumerate(fh, 1):
                for grp in re.findall(r'event_status"\)?\]?\s*[!=]=\s*"(\w+)"', line):
                    statuses.setdefault(grp, f"{name}:{ln}")
                for grp in re.findall(r'event_code"\)?\]?\s*(?:==\s*"(\w+)"|in\s*\(([^)]*)\))',
                                      line):
                    for v in [grp[0]] + re.findall(r'"(\w+)"', grp[1]):
                        if v:
                            codes.setdefault(v, f"{name}:{ln}")
    return codes, statuses


# ── SQL ───────────────────────────────────────────────────────────────────────────────────
def sql_schema():
    return (f"/* canary:schema */\nSELECT column_name, data_type FROM `{DATASET}`.INFORMATION_SCHEMA"
            f".COLUMNS WHERE table_name = 'corporate_action'")


def sql_values(today):
    lo = (today - dt.timedelta(days=RECENT_DAYS)).isoformat()
    parts = []
    for kind, col in (("code", "event_code"), ("status", "event_status")):
        parts.append(
            f"SELECT '{kind}' AS kind, IFNULL({col}, '<NULL>') AS v, COUNT(*) AS n_all, "
            f"COUNTIF(public_date >= DATE '{lo}') AS n_recent FROM `{TABLE}` GROUP BY v")
    return "/* canary:values */\n" + "\nUNION ALL\n".join(parts)


def sql_activity(lo, hi):
    return (f"/* canary:activity */\nSELECT "
            f"COUNTIF(event_code = 'ISS' AND exright_date BETWEEN DATE '{lo}' AND DATE '{hi}') "
            f"AS iss, "
            f"COUNTIF(event_code = 'AIS' AND effective_date BETWEEN DATE '{lo}' AND DATE '{hi}') "
            f"AS ais FROM `{TABLE}` WHERE event_status = 'executed'")


def sql_pins():
    cond = " OR ".join(f"(ticker = '{t}' AND effective_date = DATE '{d}')" for t, d, _ in AIS_PINS)
    return (f"/* canary:pins */\nSELECT ticker, CAST(effective_date AS STRING) AS eff, "
            f"shares_total_after FROM `{TABLE}` "
            f"WHERE event_code = 'AIS' AND event_status = 'executed' AND ({cond})")


# ── lịch ─────────────────────────────────────────────────────────────────────────────────
def prior_sessions(today, n):
    """n phiên VN liền TRƯỚC `today` (mới nhất trước) — T2-T6 trừ `vn_market.is_holiday`."""
    from trading_bot.vn_market import is_holiday
    out, d = [], today
    while len(out) < n:
        d -= dt.timedelta(days=1)
        if d.weekday() < 5 and not is_holiday(d):
            out.append(d)
    return out


# ── kiểm tra (thuần, nhận dữ liệu đã đọc) ─────────────────────────────────────────────────
def _res(name, ok, evidence):
    return {"check": name, "status": "PASS" if ok else "WARN", "evidence": evidence}


def check_schema(schema_rows, code_cols):
    live = {r["column_name"]: r["data_type"] for r in schema_rows}
    probs = []
    if not code_cols:
        probs.append("trích được 0 cột từ code — bộ trích hỏng hoặc SQL_SOURCES lệch code")
    for col in sorted(code_cols):
        src = ",".join(sorted(set(code_cols[col])))
        if col not in live:
            probs.append(f"`{col}` THIẾU trên bảng (code đọc ở {src})")
        elif col not in EXPECTED_TYPES:
            probs.append(f"`{col}` code đọc ({src}) nhưng canary chưa pin kiểu — live={live[col]}")
        elif live[col] != EXPECTED_TYPES[col]:
            probs.append(f"`{col}` kiểu {live[col]} ≠ pin {EXPECTED_TYPES[col]} ({src})")
    ev = (f"{len(code_cols)} cột code đọc / {len(live)} cột trên bảng"
          + ("" if not probs else ": " + "; ".join(probs)))
    return _res("a.schema", not probs, ev)


def check_values(value_rows, need_codes, need_statuses):
    seen = {("code" if r["kind"] == "code" else "status", r["v"]):
            (int(r["n_all"]), int(r["n_recent"])) for r in value_rows}
    probs = []
    for (kind, v), (n_all, _) in sorted(seen.items()):
        known = KNOWN_CODES if kind == "code" else KNOWN_STATUSES
        if v not in known:
            probs.append(f"giá trị MỚI {kind}=`{v}` ({n_all} dòng)")
    for kind, need in (("code", need_codes), ("status", need_statuses)):
        for v in sorted(need):
            n_all, n_recent = seen.get((kind, v), (0, 0))
            if n_all == 0:
                probs.append(f"{kind}=`{v}` code cần ({need[v]}) BIẾN MẤT khỏi toàn bảng")
            elif (kind, v) in RECENT_REQUIRED and n_recent == 0:
                probs.append(f"{kind}=`{v}` 0 dòng trong {RECENT_DAYS} ngày public_date gần nhất "
                             f"(toàn bảng {n_all})")
    summary = ", ".join(f"{k}={v}:{a}/{r}" for (k, v), (a, r) in sorted(seen.items()))
    ev = f"[toàn bảng/{RECENT_DAYS}d] {summary}" + ("" if not probs else " — " + "; ".join(probs))
    return _res("b.values", not probs, ev)


def check_activity(rows, lo, hi):
    r = rows[0] if rows else {}
    iss, ais = int(r.get("iss") or 0), int(r.get("ais") or 0)
    ev = (f"ISS+AIS executed {lo}→{hi} ({ACTIVITY_SESSIONS} phiên VN): ISS={iss} AIS={ais}"
          + ("" if iss + ais else " — 0 dòng; lịch sử 2019→nay chưa có cửa sổ 8+ phiên nào rỗng"))
    return _res("c.activity", iss + ais > 0, ev)


def check_pins(rows):
    got = {}
    for r in rows:
        got.setdefault((r["ticker"], r["eff"]), []).append(r["shares_total_after"])
    probs, oks = [], 0
    for t, d, want in AIS_PINS:
        vals = got.get((t, d), [])
        if len(vals) != 1:
            probs.append(f"{t} AIS {d}: {len(vals)} dòng executed (kỳ vọng 1) {vals}")
        elif int(vals[0]) != want:
            probs.append(f"{t} AIS {d}: {int(vals[0]):,} ≠ pin {want:,}")
        else:
            oks += 1
    return _res("d.ais_pins", not probs,
                f"{oks}/{len(AIS_PINS)} khớp" + ("" if not probs else ": " + "; ".join(probs)))


# ── chạy ─────────────────────────────────────────────────────────────────────────────────
def _guard(name, fn):
    try:
        return fn()
    except Exception as e:  # canary tự hỏng ⇒ WARN có bằng chứng, không đoán nguyên nhân
        return {"check": name, "status": "ERROR",
                "evidence": f"CANARY KHÔNG CHẠY ĐƯỢC mục này — {type(e).__name__}: "
                            f"{str(e).strip()[-600:]}"}


def run_checks(today, runner, sources=SQL_SOURCES, scan_files=VALUE_SCAN_FILES):
    out = []
    cols = {}

    def _a():
        nonlocal cols
        cols = code_columns(sources)
        return check_schema(runner(sql_schema()), cols)

    def _b():
        codes, statuses = code_values(sources, scan_files)
        need_c = {v: f"pin; {codes[v]}" if v in codes else "pin" for v in REQUIRED_CODES}
        need_c.update({v: s for v, s in codes.items() if v not in need_c})
        need_s = {v: f"pin; {statuses[v]}" if v in statuses else "pin" for v in REQUIRED_STATUSES}
        need_s.update({v: s for v, s in statuses.items() if v not in need_s})
        return check_values(runner(sql_values(today)), need_c, need_s)

    def _c():
        s = prior_sessions(today, ACTIVITY_SESSIONS)
        lo, hi = s[-1].isoformat(), s[0].isoformat()
        return check_activity(runner(sql_activity(lo, hi)), lo, hi)

    out.append(_guard("a.schema", _a))
    out.append(_guard("b.values", _b))
    out.append(_guard("c.activity", _c))
    out.append(_guard("d.ais_pins", lambda: check_pins(runner(sql_pins()))))
    return out


def render(today, results):
    bad = [r for r in results if r["status"] != "PASS"]
    head = (f"🐤 corp_action_feed_canary {today}: {len(bad)}/{len(results)} mục WARN — feed "
            f"`tav2_bq.corporate_action` (WARN-ONLY, corp_action_daily KHÔNG bị chặn)")
    lines = [head]
    for r in results:
        icon = {"PASS": "✅", "WARN": "⚠️", "ERROR": "🛠️"}[r["status"]]
        lines.append(f"{icon} {r['check']} {r['status']}: {r['evidence']}")
    return "\n".join(lines)


def default_runner(sql):
    from corp_action_lib import bq
    return bq(sql, timeout=180)


def default_notifier(msg):
    """(ok, detail). Topic theo TÊN qua registry `kb/discord_channels.json`."""
    try:
        p = subprocess.run([os.path.join(HERE, "notify_thread.sh"), msg, NOTIFY_TOPIC],
                           capture_output=True, text=True, timeout=90)
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"
    return p.returncode == 0, f"rc={p.returncode} stderr={p.stderr.strip()[-300:]}"


def main(argv=None, runner=default_runner, notifier=default_notifier, today=None,
         sources=SQL_SOURCES, scan_files=VALUE_SCAN_FILES):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="in message, không post Discord")
    ap.add_argument("--asof", help="YYYY-MM-DD thay cho hôm nay ICT (chạy lại/kiểm thử)")
    a = ap.parse_args(argv)
    today = today or (dt.date.fromisoformat(a.asof) if a.asof
                      else dt.datetime.now(ICT).date())
    results = run_checks(today, runner, sources, scan_files)
    if all(r["status"] == "PASS" for r in results):
        print(f"{dt.datetime.now(ICT):%Y-%m-%d %H:%M} corp_action_feed_canary {today}: PASS "
              f"{len(results)}/{len(results)} — " + " | ".join(r["evidence"][:90] for r in results))
        return 0
    msg = render(today, results)
    print(msg)
    rc = 2 if any(r["status"] == "ERROR" for r in results) else 1
    if a.dry_run:
        print("(dry-run: không post Discord)")
        return rc
    ok, detail = notifier(msg)
    if not ok:
        print(f"NOTIFY_FAILED topic={NOTIFY_TOPIC} {detail}")
        return 3
    return rc


if __name__ == "__main__":
    sys.exit(main())
