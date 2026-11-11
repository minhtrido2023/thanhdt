# -*- coding: utf-8 -*-
"""lag_rating_gate_snapshot_selfcheck.py — self-check cho snapshot AUDIT-only rating cổng 8L của LAG
(lag_rating_filter.lag_rating_gate_snapshot + append_lag_rating_gate_log, chỗ nối trong
deploy_golive_dt5g_v4/golive_recommend_v23.py). Job Taylor_20261111_015322.

Chạy:  env -u TZ $DNA_PYEXE lag_rating_gate_snapshot_selfcheck.py     (offline, bq giả lập)
Nhóm:  A hàm snapshot (PASS/RATING_FAIL/NO_RATING/lỗi nguồn/không đụng cand)
       B CSV: idempotent, atomic, lỗi ghi không raise, ICT neo tường minh
       C cổng 8L + khối LAG của golive KHÔNG ĐỔI so với bản gốc git (`LGS_BASE_REV`)
       D status.json có 3 khoá; thứ tự gọi (trước cổng, sau lọc thanh khoản)
       E mutation: sửa 1 dòng quan trọng ⇒ selfcheck con phải FAIL
Không dùng đồng hồ hệ thống để so kết quả (mọi ngày là hằng số); `logged_at_ict` chỉ kiểm định dạng.
`LGS_TARGET_DIR` = thư mục chứa bản cần kiểm (mặc định: thư mục file này) — dùng cho mutation.
"""
import contextlib
import io
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import types

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.abspath(os.environ.get("LGS_TARGET_DIR") or HERE)
BASE_REV = os.environ.get("LGS_BASE_REV") or "3f6ae5705"   # commit ngay trước thay đổi P1
GOLIVE_REL = os.path.join("deploy_golive_dt5g_v4", "golive_recommend_v23.py")
sys.path.insert(0, TARGET)
import lag_rating_filter as LRF  # noqa: E402

PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  PASS  {name}")
    else:
        FAIL += 1; print(f"  FAIL  {name}  {detail}")


def _read(rel):
    with open(os.path.join(TARGET, rel), encoding="utf-8") as f:
        return f.read()


def _git_base(rel, rev=None):
    """`git show <rev>:<path>` tính từ GỐC REPO (§8c) ⇒ ghép --show-prefix."""
    rev = rev or BASE_REV
    try:
        prefix = subprocess.run(["git", "-C", HERE, "rev-parse", "--show-prefix"],
                                capture_output=True, text=True, check=True).stdout.strip()
        r = subprocess.run(["git", "-C", HERE, "show", f"{rev}:{prefix}{rel.replace(os.sep, '/')}"],
                           capture_output=True, text=True, check=True)
        return r.stdout, None
    except Exception as ex:
        return None, f"{type(ex).__name__}: {(getattr(ex, 'stderr', '') or str(ex)).strip()[:200]}"


ASOF = pd.Timestamp("2026-11-10")


def cand_df(rows):
    return pd.DataFrame({"ticker": [r[0] for r in rows], "Release_Date": pd.to_datetime([r[1] for r in rows]),
                         "tier": ["LAG_HI"] * len(rows), "NP_R": [50.0] * len(rows)})


def fake_bq(table):
    def _bq(sql):
        m = re.search(r"f\.time <= DATE '(\d{4}-\d{2}-\d{2})'", sql)
        cut = pd.Timestamp(m.group(1)) if m else None
        recs = []
        for tk, hist in table.items():
            if f"'{tk}'" not in sql:
                continue
            ok = [(pd.Timestamp(t), r) for t, r in hist if cut is None or pd.Timestamp(t) <= cut]
            if ok:
                t, r = max(ok, key=lambda x: x[0]); recs.append({"ticker": tk, "rating": r, "time": t.date()})
        return pd.DataFrame(recs, columns=["ticker", "rating", "time"])
    return _bq


def _boom(sql):
    raise RuntimeError("BQ down")


def _norm(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True, default=str)


snap = LRF.lag_rating_gate_snapshot
# ═════════════════════════════════════════════════════════════════════════════════════════
print("=" * 78); print("  A. lag_rating_gate_snapshot"); print("=" * 78)
b = fake_bq({"P3": [("2026-11-05", 3)], "F4": [("2026-11-05", 4)], "NUL": [("2026-11-05", None)]})
c = cand_df([("P3", "2026-11-05"), ("F4", "2026-11-05"), ("NUL", "2026-11-05"), ("NOR", "2026-11-05")])
rows, err = snap(b, c, ASOF)
gm = {r["ticker"]: r for r in rows}
check("A1 rating=3 → PASS, đủ trường", err is None and gm["P3"] == {"ticker": "P3", "release_date": "2026-11-05",
      "rating": 3, "rating_time": "2026-11-05", "gate": "PASS"}, f"{gm.get('P3')} {err}")
check("A2 rating=4 → RATING_FAIL", gm["F4"]["gate"] == "RATING_FAIL" and gm["F4"]["rating"] == 4)
check("A3 rating NULL → NO_RATING, giữ rating_time", gm["NUL"]["gate"] == "NO_RATING" and gm["NUL"]["rating"] is None
      and gm["NUL"]["rating_time"] == "2026-11-05", f"{gm['NUL']}")
check("A4 không có dòng 8L → NO_RATING, rating/rating_time None",
      gm["NOR"]["gate"] == "NO_RATING" and gm["NOR"]["rating"] is None and gm["NOR"]["rating_time"] is None)
check("A5 đủ 4 dòng (kể cả mã không có rating), xếp theo (release, ticker)",
      [r["ticker"] for r in rows] == ["F4", "NOR", "NUL", "P3"], f"{[r['ticker'] for r in rows]}")
# rating cũ hơn BCTC (dòng Q3 trôi): ghi rating_time quý trước, gate theo rating đó
rows, _ = snap(fake_bq({"VGS": [("2026-07-30", 4), ("2026-11-12", 3)]}), cand_df([("VGS", "2026-11-05")]), ASOF)
check("A6 PIT: dòng sau asof không thấy; rating_time = quý trước, gate theo rating cũ",
      rows == [{"ticker": "VGS", "release_date": "2026-11-05", "rating": 4, "rating_time": "2026-07-30", "gate": "RATING_FAIL"}], f"{rows}")
# nhãn gate khớp quyết định cổng thật trên lưới ngẫu nhiên
rng = random.Random(7)
tbl = {f"T{i:02d}": [("2026-08-01", rng.choice([1, 2, 3, 4, 5, None]))] for i in range(40) if rng.random() < 0.85}
cc = cand_df([(f"T{i:02d}", "2026-11-05") for i in range(40)])
rows, _ = snap(fake_bq(tbl), cc, ASOF)
kept, drop, _ = LRF.lag_filter_low_rating(fake_bq(tbl), cc, ASOF)
check("A7 PASS == cổng giữ; RATING_FAIL+NO_RATING == cổng loại (40 mã ngẫu nhiên)",
      {r["ticker"] for r in rows if r["gate"] == "PASS"} == set(kept["ticker"])
      and {r["ticker"] for r in rows if r["gate"] != "PASS"} == {d["ticker"] for d in drop}, "nhãn lệch cổng")
rows, _ = snap(fake_bq({"D": [("2026-08-01", 3)]}), cand_df([("D", "2026-11-05"), ("D", "2026-11-05")]), ASOF)
check("A8 dòng trùng (ticker,release) không nhân đôi", len(rows) == 1)
rows, _ = snap(fake_bq({"D": [("2026-08-01", 3)]}), cand_df([("D", "2026-08-01"), ("D", "2026-11-05")]), ASOF)
check("A9 2 sự kiện cùng mã → 2 dòng", len(rows) == 2)
rows, err = snap(_boom, cand_df([("D", "2026-11-05")]), ASOF)
check("A10 BQ lỗi → ([], chuỗi lỗi), không raise", rows == [] and err and "BQ down" in err, f"{rows} {err}")
for nm, bad in (("None", lambda s: None), ("thiếu cột", lambda s: pd.DataFrame({"x": [1]})), ("chuỗi", lambda s: "oops")):
    try:
        r_, e_ = snap(bad, cand_df([("D", "2026-11-05")]), ASOF); ok = isinstance(r_, list)
    except Exception as ex:
        ok = False; print("     RAISED", ex)
    check(f"A10 bq trả {nm} → không raise", ok)
calls = []
r1 = snap(lambda s: calls.append(s), cand_df([]), ASOF); r2 = snap(lambda s: calls.append(s), None, ASOF)
check("A11 cand rỗng/None → ([], None), 0 truy vấn", r1 == ([], None) and r2 == ([], None) and not calls)
r3 = snap(fake_bq({}), pd.DataFrame({"ticker": ["A"]}), ASOF)
check("A12 cand thiếu Release_Date → lỗi tường minh", r3[0] == [] and r3[1])
src = cand_df([("F4", "2026-11-05"), ("P3", "2026-11-01")]); keep = src.copy(deep=True)
snap(b, src, ASOF)
check("A13 cand không bị đổi", src.equals(keep) and list(src.index) == list(keep.index))
rows, _ = snap(fake_bq({"J": [("2026-08-01", np.int64(3))]}), cand_df([("J", "2026-11-05")]), ASOF)
check("A14 JSON-hoá được, rating là int thuần", json.dumps(rows) and type(rows[0]["rating"]) is int)

# ═════════════════════════════════════════════════════════════════════════════════════════
print("=" * 78); print("  B. append_lag_rating_gate_log"); print("=" * 78)
tmpd = tempfile.mkdtemp(prefix="lgs_")
P = os.path.join(tmpd, "sub", "log.csv")
rows1 = [{"ticker": "AAA", "release_date": "2026-11-05", "rating": 3, "rating_time": "2026-11-05", "gate": "PASS"},
         {"ticker": "BBB", "release_date": "2026-11-05", "rating": None, "rating_time": None, "gate": "NO_RATING"}]
n, e = LRF.append_lag_rating_gate_log(rows1, ASOF, P)
d1 = pd.read_csv(P, dtype=str, keep_default_na=False)
check("B1 ghi 2 dòng, tạo cả thư mục", n == 2 and e is None and len(d1) == 2, f"{n} {e}")
check("B2 header đúng thứ tự cột", list(d1.columns) == ["logged_at_ict", "asof", "ticker", "release_date", "rating", "rating_time", "gate"])
check("B3 logged_at_ict dạng 'YYYY-MM-DD HH:MM:SS' + asof ISO", bool(re.fullmatch(r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d", d1.logged_at_ict[0]))
      and d1["asof"][0] == "2026-11-10")
check("B4 NULL ghi ô rỗng", d1.loc[d1.ticker == "BBB", "rating"].iloc[0] == "" and d1.loc[d1.ticker == "BBB", "rating_time"].iloc[0] == "")
raw1 = open(P, "rb").read()
n, e = LRF.append_lag_rating_gate_log(rows1, ASOF, P)
check("B5 idempotent: chạy lại cùng rows → 0 dòng mới, file không đổi byte", n == 0 and e is None and open(P, "rb").read() == raw1)
n, e = LRF.append_lag_rating_gate_log(rows1 + [dict(rows1[0], rating=4, gate="RATING_FAIL")], ASOF, P)
check("B6 rating đổi (khác khoá) → ghi thêm đúng 1 dòng, dòng cũ giữ nguyên", n == 1 and len(pd.read_csv(P)) == 3
      and open(P, "rb").read().startswith(raw1))
n, e = LRF.append_lag_rating_gate_log(rows1, pd.Timestamp("2026-11-11"), P)
check("B7 asof khác → coi là lượt mới (ghi 2 dòng)", n == 2 and len(pd.read_csv(P)) == 5)
check("B8 không để lại file .tmp", not [f for f in os.listdir(os.path.dirname(P)) if ".tmp" in f], f"{os.listdir(os.path.dirname(P))}")
# lỗi ghi: os.replace hỏng ⇒ không raise, file cũ còn nguyên, tmp bị dọn
raw_before = open(P, "rb").read(); real_replace = os.replace
os.replace = lambda *a, **k: (_ for _ in ()).throw(OSError("disk full"))
try:
    n, e = LRF.append_lag_rating_gate_log([dict(rows1[0], ticker="ZZZ")], ASOF, P)
finally:
    os.replace = real_replace
check("B9 os.replace lỗi → (0, lỗi), không raise, file cũ nguyên vẹn (atomic), tmp dọn sạch",
      n == 0 and e and "disk full" in e and open(P, "rb").read() == raw_before
      and not [f for f in os.listdir(os.path.dirname(P)) if ".tmp" in f], f"{n} {e}")
n, e = LRF.append_lag_rating_gate_log(rows1, ASOF, "/proc/nonexistent/x/log.csv")
check("B10 đường dẫn không ghi được → (0, lỗi), không raise", n == 0 and e)
check("B11 rows rỗng/rác → không raise", LRF.append_lag_rating_gate_log([], ASOF, P) == (0, None)
      and LRF.append_lag_rating_gate_log([{"x": 1}], ASOF, P)[0] == 0 and LRF.append_lag_rating_gate_log(None, ASOF, P) == (0, None))
check("B12 đường dẫn mặc định = data/lag_rating_gate_log.csv", LRF.GATE_LOG_PATH.endswith("/WorkingClaude/data/lag_rating_gate_log.csv"))
src_f = _read("lag_rating_filter.py")
check("B13 ICT neo tường minh (§16): ZoneInfo('Asia/Ho_Chi_Minh'), không datetime.now() trần",
      'ZoneInfo("Asia/Ho_Chi_Minh")' in src_f and "datetime.now()" not in src_f)
# tz-độc lập: logged_at_ict giống nhau (±2 phút) dưới TZ lạ
out = subprocess.run([sys.executable, "-c",
    "import sys;sys.path.insert(0,%r);import lag_rating_filter as L,pandas as pd,os,tempfile;"
    "p=os.path.join(tempfile.mkdtemp(),'a.csv');L.append_lag_rating_gate_log([{'ticker':'X','release_date':'2026-11-05','rating':3,'rating_time':'2026-11-05','gate':'PASS'}],pd.Timestamp('2026-11-10'),p);"
    "print(open(p).read().splitlines()[1].split(',')[0])" % TARGET],
    capture_output=True, text=True, env=dict(os.environ, TZ="Pacific/Kiritimati"))
import datetime as _dt
from zoneinfo import ZoneInfo
t_sub = _dt.datetime.strptime(out.stdout.strip(), "%Y-%m-%d %H:%M:%S") if out.stdout.strip() else None
now_ict = _dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)
check("B14 TZ=Pacific/Kiritimati vẫn ghi giờ ICT (lệch ≤120s so ICT thật)", t_sub is not None and abs((now_ict - t_sub).total_seconds()) < 120, out.stdout + out.stderr)
shutil.rmtree(tmpd, ignore_errors=True)

# ═════════════════════════════════════════════════════════════════════════════════════════
print("=" * 78); print(f"  C. cổng 8L + khối LAG golive KHÔNG ĐỔI (so với {BASE_REV})"); print("=" * 78)
lrf_base_src, e0 = _git_base("lag_rating_filter.py")
gl_base, e1 = _git_base(GOLIVE_REL)
gl_new = _read(GOLIVE_REL)
check("C0 đọc được bản gốc lag_rating_filter.py + golive từ git", lrf_base_src is not None and gl_base is not None, f"{e0} {e1}")
BASE_LRF = types.ModuleType("lrf_base"); exec(compile(lrf_base_src, "lrf@base", "exec"), BASE_LRF.__dict__)

import ast  # noqa: E402


def _fn_ast(src, name):
    for node in ast.parse(src).body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.dump(node)


check("C1 AST lag_filter_low_rating / lag_rating_stale_flags / annotate / format GIỐNG HỆT bản gốc",
      all(_fn_ast(lrf_base_src, f) and _fn_ast(lrf_base_src, f) == _fn_ast(src_f, f)
          for f in ("lag_filter_low_rating", "lag_rating_stale_flags", "annotate_stale_status", "format_lag_rating_stale_line")))

A_TD, A_BLK, A_END = "def td_offset(ref, off):", "lag_up, lag_recent, lag_source_error = [], [], None", "# ── 5. Allocator"
A_RECS, A_RECS_END = "for it in lag_up:\n    recs.append(", "for tk in basket:"


def _slice(src, a, b):
    i = src.index(a); j = src.index(b, i); return src[i:j]


def _run_block(src, lrf_mod, cand, bq_fn, live_raises=False, log_path=None, with_snapshot=True):
    td_src = _slice(src, A_TD, "# lag_source_error: None"); blk_src = _slice(src, A_BLK, A_END)
    recs_src = _slice(src, A_RECS, A_RECS_END)
    trade_dates = list(pd.bdate_range("2026-05-01", ASOF))

    def _liq(bq, c, asof):
        bad = [t for t in c["ticker"] if t.endswith("7")]
        return c[~c["ticker"].isin(bad)].copy(), [{"ticker": t, "reason": "ADV≤0"} for t in sorted(set(bad))], None

    def _forensic(c, asof, workdir=None):
        bad = [t for t in c["ticker"] if t.endswith("9")]
        return c[~c["ticker"].isin(bad)].copy(), [{"ticker": t, "kind": "BANNED"} for t in sorted(set(bad))], None

    def _live(start=None):
        if live_raises:
            raise RuntimeError("pkl hỏng")
        c = cand.copy(deep=True); c["qualify"] = [not t.endswith("5") for t in c["ticker"]]
        c["pa_HL3"] = 6.0; c["tier"] = ["LAG_HI" if i % 2 == 0 else "LAG_LO" for i in range(len(c))]
        return c

    fm = types.ModuleType("lag_live_schedule"); fm.live_lag_candidates = _live
    saved = sys.modules.get("lag_live_schedule"); sys.modules["lag_live_schedule"] = fm
    ns = {"pd": pd, "np": np, "bq": bq_fn, "START": "2026-06-15", "LATEST": ASOF, "WORKDIR": "/nonexistent",
          "trade_dates": trade_dates, "lag_filter_illiquid": _liq, "lag_filter_forensic_banned": _forensic,
          "lag_filter_low_rating": lrf_mod.lag_filter_low_rating, "recs": [],
          "LAG_TW": {"LAG_HI": 0.10, "LAG_LO": 0.08}, "sec_map": {}, "print": lambda *a, **k: None}
    for nm in ("lag_rating_stale_flags", "annotate_stale_status", "format_lag_rating_stale_line"):
        ns[nm] = getattr(lrf_mod, nm)
    if with_snapshot and hasattr(lrf_mod, "lag_rating_gate_snapshot"):
        ns["lag_rating_gate_snapshot"] = lrf_mod.lag_rating_gate_snapshot
        ns["append_lag_rating_gate_log"] = lambda rows, asof: lrf_mod.append_lag_rating_gate_log(rows, asof, log_path)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(td_src, "td", "exec"), ns); exec(compile(blk_src, "blk", "exec"), ns); exec(compile(recs_src, "recs", "exec"), ns)
    finally:
        if saved is None:
            sys.modules.pop("lag_live_schedule", None)
        else:
            sys.modules["lag_live_schedule"] = saved
    keys = ("lag_up", "lag_recent", "lag_source_error", "lag_liq_dropped", "lag_liq_error", "lag_rating_dropped",
            "lag_rating_error", "lag_forensic_dropped", "lag_forensic_error", "recs", "lag_rating_stale", "lag_rating_stale_error")
    return {k: ns[k] for k in keys}, ns


def _world(rng, n):
    tks = rng.sample([f"T{i:02d}" for i in range(30)], n); rows, table = [], {}
    for tk in tks:
        rel = ASOF - pd.Timedelta(days=rng.randint(0, 14)); rows.append((tk, str(rel.date())))
        mode = rng.choice(["none", "stale", "same", "null"])
        if mode == "stale":
            table[tk] = [(str((rel - pd.Timedelta(days=rng.randint(1, 95))).date()), rng.randint(1, 6))]
        elif mode == "null":
            table[tk] = [(str((rel - pd.Timedelta(days=30)).date()), None)]
        elif mode == "same":
            table[tk] = [(str(rel.date()), rng.randint(1, 6))]
    return cand_df(rows), table


tmpl = tempfile.mkdtemp(prefix="lgs_log_")
rng = random.Random(20261111)
n_cases, diff, n_orders, n_snap, n_fail, n_err, mism = 300, 0, 0, 0, 0, 0, 0
snap_cover_bad = 0
for i in range(n_cases):
    cand, table = _world(rng, rng.randint(0, 14))
    bqf = _boom if i % 30 == 29 else fake_bq(table); lr = (i % 37 == 36)
    LOGP = os.path.join(tmpl, f"c{i}.csv")
    d0, _ = _run_block(gl_base, BASE_LRF, cand, bqf, lr)
    d1, ns1 = _run_block(gl_new, LRF, cand, bqf, lr, LOGP)
    n_orders += len(d1["recs"])
    if _norm(d0) != _norm(d1):
        diff += 1
    rows_ = ns1.get("lag_rating_gate_snapshot_rows") or []
    n_snap += len(rows_); n_err += ns1.get("lag_rating_gate_snapshot_error") is not None
    if rows_:
        n_fail += sum(r["gate"] != "PASS" for r in rows_)
        if {r["ticker"] for r in rows_ if r["gate"] != "PASS"} != {d["ticker"] for d in d1["lag_rating_dropped"]}:
            mism += 1
        if not (os.path.exists(LOGP) and len(pd.read_csv(LOGP)) == len(rows_)):
            snap_cover_bad += 1
check(f"C2 {n_cases} thế giới: lag_up/lag_recent/dropped/recs/stale TRÙNG bản gốc ({n_orders} order LAG, {n_err} lượt lỗi snapshot-nguồn)",
      diff == 0, f"{diff} lệch")
check(f"C3 phép so có nội dung ({n_snap} dòng snapshot, {n_fail} không-PASS)", n_orders > 100 and n_snap > 100 and n_fail > 30 and n_err >= 5,
      f"orders={n_orders} snap={n_snap} fail={n_fail} err={n_err}")
check("C4 snapshot không-PASS == đúng tập mã mà cổng thật loại (mọi thế giới có snapshot)", mism == 0, f"{mism} lệch")
check("C5 mỗi lượt có snapshot đều ghi đủ dòng ra CSV", snap_cover_bad == 0, f"{snap_cover_bad}")
# snapshot hỏng/thiếu hàm: golive KHÔNG chết, quyết định không đổi
cand, table = _world(random.Random(5), 10)
d0, _ = _run_block(gl_base, BASE_LRF, cand, fake_bq(table))
d1, ns1 = _run_block(gl_new, LRF, cand, fake_bq(table), with_snapshot=False)   # tên không có trong ns ⇒ NameError nội bộ
check("C6 snapshot thiếu hàm (NameError) → quyết định không đổi, lỗi ghi vào snapshot_error", _norm(d0) == _norm(d1)
      and ns1["lag_rating_gate_snapshot_error"] and ns1["lag_rating_gate_snapshot_rows"] == [])
d1, ns1 = _run_block(gl_new, LRF, cand, fake_bq(table), log_path="/proc/nonexistent/x.csv")
check("C7 ghi CSV lỗi → quyết định không đổi, snapshot_error 'ghi CSV', rows vẫn có", _norm(d0) == _norm(d1)
      and (ns1["lag_rating_gate_snapshot_error"] or "").startswith("ghi CSV") and ns1["lag_rating_gate_snapshot_rows"])
shutil.rmtree(tmpl, ignore_errors=True)

# ═════════════════════════════════════════════════════════════════════════════════════════
print("=" * 78); print("  D. status.json + thứ tự gọi + diff golive"); print("=" * 78)
check("D1 status có đủ 3 khoá",
      all(k in gl_new for k in ('"lag_rating_gate_snapshot": lag_rating_gate_snapshot_rows,',
                                '"n_lag_rating_gate_snapshot": len(lag_rating_gate_snapshot_rows),',
                                '"lag_rating_gate_snapshot_error": lag_rating_gate_snapshot_error,')))
i_liq = gl_new.find("cand, lag_liq_dropped, lag_liq_error = lag_filter_illiquid(bq, cand, LATEST)")
i_st = gl_new.find("lag_rating_stale, lag_rating_stale_error = lag_rating_stale_flags(bq, cand, LATEST)")
i_sn = gl_new.find("lag_rating_gate_snapshot(bq, cand, LATEST)")
i_gate = gl_new.find("cand, lag_rating_dropped, lag_rating_error = lag_filter_low_rating(bq, cand, LATEST)")
check("D2 snapshot gọi SAU lọc thanh khoản, cạnh cờ stale, TRƯỚC cổng 8L, trên cùng `cand`", 0 < i_liq < i_st < i_sn < i_gate, f"{i_liq} {i_st} {i_sn} {i_gate}")
check("D3 khởi tạo biến snapshot NGOÀI try của khối LAG",
      0 < gl_new.find("lag_rating_gate_snapshot_rows, lag_rating_gate_snapshot_error = [], None") < gl_new.find("from lag_live_schedule import"))
check("D4 snapshot bọc try/except riêng (lỗi không làm golive chết)",
      re.search(r"try:.*?\n\s+lag_rating_gate_snapshot_rows, lag_rating_gate_snapshot_error = lag_rating_gate_snapshot\(bq, cand, LATEST\).*?except Exception", gl_new, re.S) is not None)
added = [l for l in gl_new.splitlines() if l not in set(gl_base.splitlines())]
removed = [l for l in gl_base.splitlines() if l.strip() and l not in set(gl_new.splitlines())]
check("D5 so với bản gốc golive KHÔNG mất dòng nào", removed == [], f"{removed}")
check("D6 mọi dòng THÊM đều thuộc snapshot (không đổi dòng nào khác của khối LAG)",
      all(("snapshot" in l or "_gl_" in l or l.strip().startswith("#") or "append_lag_rating_gate_log" in l
           or l.strip() in ("try:", "except Exception:   # pragma: no cover") or "lag_rating_gate_log.csv" in l) for l in added), f"{[l for l in added][:20]}")

# ═════════════════════════════════════════════════════════════════════════════════════════
if not os.environ.get("LGS_NO_MUTATION"):
    print("=" * 78); print("  E. mutation — sửa 1 dòng quan trọng ⇒ selfcheck con phải FAIL"); print("=" * 78)
    MUTS = [
        ("lag_rating_filter.py", 'float(rt) < rating_max_ok + 1 else "RATING_FAIL")})\n        rows.sort', 'float(rt) < rating_max_ok else "RATING_FAIL")})\n        rows.sort', "ngưỡng gate lệch biên 3/4"),
        ("lag_rating_filter.py", "            if _k(d) in have:\n                continue\n", "            if False:\n                continue\n", "bỏ idempotency"),
        ("lag_rating_filter.py", "            os.replace(tmp, path)", "            os.rename(tmp, path + 'x')", "đổi atomic replace"),
        ("lag_rating_filter.py", 'ZoneInfo("Asia/Ho_Chi_Minh")).strftime', 'ZoneInfo("UTC")).strftime', "mất neo ICT"),
        (GOLIVE_REL, "lag_rating_gate_snapshot(bq, cand, LATEST)\n        if lag_rating_gate_snapshot_rows", "lag_rating_gate_snapshot(bq, cand.iloc[:0], LATEST)\n        if lag_rating_gate_snapshot_rows", "snapshot nhận cand khác"),
        (GOLIVE_REL, '    "n_lag_rating_gate_snapshot": len(lag_rating_gate_snapshot_rows),\n', "", "mất khoá status"),
        (GOLIVE_REL, "    except Exception as _gl_ex:\n        lag_rating_gate_snapshot_rows, lag_rating_gate_snapshot_error = [], f\"{type(_gl_ex).__name__}: {_gl_ex}\"\n",
         "    except KeyboardInterrupt as _gl_ex:\n        pass\n", "bỏ bọc lỗi snapshot"),
        (GOLIVE_REL, "    cand, lag_rating_dropped, lag_rating_error = lag_filter_low_rating(bq, cand, LATEST)\n",
         "    cand, lag_rating_dropped, lag_rating_error = lag_filter_low_rating(bq, cand.head(1), LATEST)\n", "đổi quyết định cổng"),
    ]
    for rel, old, new, why in MUTS:
        md = tempfile.mkdtemp(prefix="lgs_mut_")
        try:
            for f in ("lag_rating_filter.py", GOLIVE_REL):
                os.makedirs(os.path.dirname(os.path.join(md, f)), exist_ok=True); shutil.copy(os.path.join(TARGET, f), os.path.join(md, f))
            p = os.path.join(md, rel); s = open(p, encoding="utf-8").read()
            if s.count(old) != 1:
                check(f"E mutant [{why}]: tìm thấy đúng 1 dòng để sửa", False, f"count={s.count(old)}"); continue
            open(p, "w", encoding="utf-8").write(s.replace(old, new, 1))
            r = subprocess.run([sys.executable, os.path.abspath(__file__)], capture_output=True, text=True,
                               env=dict(os.environ, LGS_TARGET_DIR=md, LGS_NO_MUTATION="1"))
            check(f"E mutant [{why}] → selfcheck con FAIL (rc={r.returncode})", r.returncode != 0)
        finally:
            shutil.rmtree(md, ignore_errors=True)

print("=" * 78)
print(f"  TỔNG: {PASS} PASS / {FAIL} FAIL   (target={TARGET}, base={BASE_REV})")
sys.exit(1 if FAIL else 0)
