# -*- coding: utf-8 -*-
"""lag_rating_stale_selfcheck.py — self-check cho cờ CẢNH BÁO-only `lag_rating_stale`
(lag_rating_filter.lag_rating_stale_flags + annotate_stale_status + format_lag_rating_stale_line,
và chỗ nối vào deploy_golive_dt5g_v4/golive_recommend_v23.py + telegram_recommend.py).

Chạy:  $DNA_PYEXE lag_rating_stale_selfcheck.py            (offline, bq giả lập)
       $DNA_PYEXE lag_rating_stale_selfcheck.py --live     (thêm 1 truy vấn BQ thật, chỉ đọc)

Sáu nhóm:
  A  hàm cờ: cũ / đúng ngày / mới hơn / không có rating / lỗi nguồn / không đụng cand
  B  CỔNG 8L KHÔNG ĐỔI: `lag_filter_low_rating` giống hệt bản gốc (AST + hành vi trên lưới ngẫu nhiên)
  C  ĐƯỜNG GOLIVE KHÔNG ĐỔI: khối LAG của golive bản gốc vs bản mới, cùng input → cùng
     lag_up / lag_recent / các danh sách bị loại / dòng `recs` LAG (= danh sách order LAG)
  D  gắn status + dòng cảnh báo (markdown + HTML)
  E  chỗ nối: golive (thứ tự gọi, 3 khoá status, dòng trong .md) và telegram (dòng HTML)
  F  --live: truy vấn thật không lỗi (chỉ đọc)

Bản gốc để so (nhóm B, C) lấy từ git: `LRS_BASE_REV` (mặc định = commit ngay trước thay đổi).
Không đọc được bản gốc ⇒ FAIL, không lặng lẽ bỏ qua. `LRS_TARGET_DIR` = thư mục chứa bản cần kiểm
(mặc định: thư mục của chính file này) — dùng cho mutation test.

Không dùng đồng hồ hệ thống ở bất kỳ đâu (mọi ngày đều là hằng số) ⇒ kết quả không phụ thuộc TZ;
vẫn nên chạy dưới `env -u TZ` và 1 TZ lạ (§16/§19).
"""
import ast
import contextlib
import io
import json
import os
import random
import re
import subprocess
import sys
import types

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.abspath(os.environ.get("LRS_TARGET_DIR") or HERE)
BASE_REV = os.environ.get("LRS_BASE_REV") or "3dc35467"
GOLIVE_REL = os.path.join("deploy_golive_dt5g_v4", "golive_recommend_v23.py")

sys.path.insert(0, TARGET)
import lag_rating_filter as LRF  # noqa: E402

PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")


def _read(rel):
    with open(os.path.join(TARGET, rel), encoding="utf-8") as f:
        return f.read()


def _git_base(rel):
    """Nội dung file ở BASE_REV. `git show <rev>:<path>` tính từ GỐC REPO (§8c) ⇒ ghép prefix."""
    try:
        prefix = subprocess.run(["git", "-C", HERE, "rev-parse", "--show-prefix"],
                                capture_output=True, text=True, check=True).stdout.strip()
        r = subprocess.run(["git", "-C", HERE, "show", f"{BASE_REV}:{prefix}{rel.replace(os.sep, '/')}"],
                           capture_output=True, text=True, check=True)
        return r.stdout, None
    except Exception as ex:
        err = getattr(ex, "stderr", "") or str(ex)
        return None, f"{type(ex).__name__}: {err.strip()[:200]}"


ASOF = pd.Timestamp("2026-10-13")


def cand_df(rows):
    """rows: [(ticker, release 'YYYY-MM-DD'|None)]"""
    return pd.DataFrame({"ticker": [r[0] for r in rows],
                         "Release_Date": pd.to_datetime([r[1] for r in rows]),
                         "tier": ["LAG_HI"] * len(rows), "NP_R": [50.0] * len(rows)})


def fake_bq(table):
    """table: {ticker: [(time 'YYYY-MM-DD', rating|None), ...]}. Hàm THUẦN theo chuỗi SQL: trả dòng
    mới nhất có time ≤ ngày trong mệnh đề `f.time <= DATE '…'` (không có mệnh đề ⇒ mới nhất toàn bộ),
    chỉ cho các mã có trong `IN (…)`."""
    def _bq(sql):
        m = re.search(r"f\.time <= DATE '(\d{4}-\d{2}-\d{2})'", sql)
        cut = pd.Timestamp(m.group(1)) if m else None
        recs = []
        for tk, hist in table.items():
            if f"'{tk}'" not in sql:
                continue
            ok = [(pd.Timestamp(t), r) for t, r in hist if cut is None or pd.Timestamp(t) <= cut]
            if not ok:
                continue
            t, r = max(ok, key=lambda x: x[0])
            recs.append({"ticker": tk, "rating": r, "time": t.date()})
        return pd.DataFrame(recs, columns=["ticker", "rating", "time"])
    return _bq


def _boom(sql):
    raise RuntimeError("BQ down")


# ══════════════════════════════════════════════════════════════════════════════════════════
print("=" * 78); print("  A. lag_rating_stale_flags (bq giả lập)"); print("=" * 78)
flags_fn = LRF.lag_rating_stale_flags

# A1 — rating cũ hơn BCTC ⇒ gắn cờ, đủ trường, đúng ngày
b = fake_bq({"TVN": [("2026-04-28", 3)]})
fl, err = flags_fn(b, cand_df([("TVN", "2026-07-30")]), pd.Timestamp("2026-08-05"))
check("A1 rating 04-28 < BCTC 07-30 → CÓ cờ", len(fl) == 1 and err is None, f"{fl} {err}")
check("A1 … đúng ticker/rating/ngày rating/ngày BCTC/gate",
      fl and fl[0] == {"ticker": "TVN", "rating": 3, "rating_date": "2026-04-28",
                       "release_date": "2026-07-30", "gate": "PASS"}, f"{fl}")

# A2 — rating ĐÚNG ngày BCTC ⇒ không cờ (biên)
b = fake_bq({"KBC": [("2026-07-20", 2), ("2026-10-12", 2)]})
fl, err = flags_fn(b, cand_df([("KBC", "2026-10-12")]), ASOF)
check("A2 rating_date == release → KHÔNG cờ", fl == [] and err is None, f"{fl} {err}")

# A3 — rating SAU ngày BCTC ⇒ không cờ
b = fake_bq({"KBC": [("2026-10-13", 2)]})
fl, err = flags_fn(b, cand_df([("KBC", "2026-10-12")]), ASOF)
check("A3 rating_date > release → KHÔNG cờ", fl == [] and err is None, f"{fl} {err}")

# A4 — sai MỘT ngày ⇒ có cờ (biên phía kia)
b = fake_bq({"KBC": [("2026-10-11", 2)]})
fl, err = flags_fn(b, cand_df([("KBC", "2026-10-12")]), ASOF)
check("A4 rating_date = release − 1 ngày → CÓ cờ", len(fl) == 1 and fl[0]["rating_date"] == "2026-10-11", f"{fl}")

# A5 — mã KHÔNG có dòng rating ⇒ không cờ, KHÔNG lỗi (cổng đã loại fail-closed, lý do riêng)
b = fake_bq({"POW": [("2026-10-12", 3)]})
fl, err = flags_fn(b, cand_df([("NORATE", "2026-10-12"), ("POW", "2026-10-12")]), ASOF)
check("A5 mã không có rating → không cờ, err=None", fl == [] and err is None, f"{fl} {err}")
fl, err = flags_fn(fake_bq({}), cand_df([("NORATE", "2026-10-12")]), ASOF)
check("A5b bảng rỗng hoàn toàn → không cờ, err=None", fl == [] and err is None, f"{fl} {err}")

# A6 — dòng rating có rating=None nhưng cũ ⇒ cờ, rating None, gate RATING_FAIL (đúng phía cổng)
b = fake_bq({"NUL": [("2026-07-01", None)]})
fl, err = flags_fn(b, cand_df([("NUL", "2026-10-12")]), ASOF)
check("A6 rating NULL + cũ → cờ, rating=None, gate=RATING_FAIL",
      len(fl) == 1 and fl[0]["rating"] is None and fl[0]["gate"] == "RATING_FAIL", f"{fl}")

# A7 — nhãn gate ở biên 3/4 phải trùng phía của cổng thật
b = fake_bq({"R3": [("2026-07-01", LRF.RATING_MAX_OK)], "R4": [("2026-07-01", LRF.RATING_MAX_OK + 1)]})
c7 = cand_df([("R3", "2026-10-12"), ("R4", "2026-10-12")])
fl, _ = flags_fn(b, c7, ASOF)
gm = {f["ticker"]: f["gate"] for f in fl}
kept7, drop7, _ = LRF.lag_filter_low_rating(b, c7, ASOF)
check("A7 rating=3 → PASS, rating=4 → RATING_FAIL", gm == {"R3": "PASS", "R4": "RATING_FAIL"}, f"{gm}")
check("A7 … nhãn gate KHỚP quyết định của cổng thật",
      set(kept7["ticker"]) == {t for t, g in gm.items() if g == "PASS"}
      and {d["ticker"] for d in drop7} == {t for t, g in gm.items() if g == "RATING_FAIL"}, f"{gm}")

# A8 — point-in-time: dòng rating mới (sau asof) KHÔNG được nhìn thấy
b = fake_bq({"PIT": [("2026-07-01", 3), ("2026-10-14", 2)]})
fl, err = flags_fn(b, cand_df([("PIT", "2026-10-12")]), ASOF)
check("A8 dòng rating SAU asof không che cờ (PIT)", len(fl) == 1 and fl[0]["rating_date"] == "2026-07-01", f"{fl}")

# A9 — so theo NGÀY, không theo giờ: release 15:00 cùng ngày rating ⇒ không cờ
c9 = cand_df([("HR", "2026-10-12")]); c9["Release_Date"] = pd.to_datetime(["2026-10-12 15:00:00"])
fl, err = flags_fn(fake_bq({"HR": [("2026-10-12", 2)]}), c9, ASOF)
check("A9 release có giờ, cùng ngày rating → KHÔNG cờ", fl == [] and err is None, f"{fl} {err}")

# A10 — 2 sự kiện cùng mã (quý cũ + quý mới): chỉ sự kiện mới bị cờ; dòng trùng không nhân đôi
b = fake_bq({"TWO": [("2026-07-25", 3)]})
fl, err = flags_fn(b, cand_df([("TWO", "2026-07-25"), ("TWO", "2026-10-10"), ("TWO", "2026-10-10")]), ASOF)
check("A10 2 sự kiện 1 mã → chỉ sự kiện mới, không nhân đôi",
      [(f["ticker"], f["release_date"]) for f in fl] == [("TWO", "2026-10-10")], f"{fl}")

# A11 — Release_Date thiếu (NaT) ⇒ bỏ qua dòng đó, không lỗi
c11 = cand_df([("NAT", None), ("OLD", "2026-10-12")])
fl, err = flags_fn(fake_bq({"NAT": [("2026-07-01", 3)], "OLD": [("2026-07-01", 3)]}), c11, ASOF)
check("A11 Release_Date NaT → bỏ qua, mã khác vẫn cờ", [f["ticker"] for f in fl] == ["OLD"] and err is None, f"{fl} {err}")

# A12 — LỖI NGUỒN: không raise, trả ([], chuỗi lỗi) — phân biệt được với "không có mã nào cũ"
fl, err = flags_fn(_boom, cand_df([("TVN", "2026-10-12")]), ASOF)
check("A12 BQ lỗi → [] + chuỗi lỗi, KHÔNG raise", fl == [] and err is not None and "BQ down" in err, f"{fl} {err}")
for nm, bad in (("None", lambda s: None), ("thiếu cột", lambda s: pd.DataFrame({"x": [1]})),
                ("chuỗi", lambda s: "oops"), ("time rác", lambda s: pd.DataFrame(
                    {"ticker": ["TVN"], "rating": ["abc"], "time": ["không-phải-ngày"]}))):
    try:
        fl, err = flags_fn(bad, cand_df([("TVN", "2026-10-12")]), ASOF)
        ok = isinstance(fl, list) and (fl == [] or err is None)
    except Exception as ex:  # hàm cờ raise = có thể làm sập cả khối LAG của golive
        ok, fl, err = False, None, f"RAISED {type(ex).__name__}: {ex}"
    check(f"A12 bq trả {nm} → không raise", ok, f"{fl} {err}")

# A13 — thiếu cột Release_Date ⇒ báo lỗi (không im lặng trả "không có gì")
fl, err = flags_fn(fake_bq({"A": [("2026-07-01", 3)]}), pd.DataFrame({"ticker": ["A"]}), ASOF)
check("A13 cand thiếu Release_Date → [] + lỗi", fl == [] and err is not None, f"{fl} {err}")

# A14 — rổ rỗng / None ⇒ no-op, KHÔNG gọi BQ
calls = []
def _count(sql):
    calls.append(sql); return pd.DataFrame(columns=["ticker", "rating", "time"])
fl1, e1 = flags_fn(_count, cand_df([]), ASOF); fl2, e2 = flags_fn(_count, None, ASOF)
check("A14 rổ rỗng/None → no-op, 0 truy vấn", fl1 == [] and fl2 == [] and e1 is None and e2 is None and not calls)

# A15 — KHÔNG đụng cand (giá trị, cột, thứ tự, index)
b = fake_bq({"A": [("2026-07-01", 2)], "B": [("2026-07-01", 4)], "C": [("2026-10-12", 3)]})
src = cand_df([("B", "2026-10-12"), ("A", "2026-10-10"), ("C", "2026-10-12")]); snap = src.copy(deep=True)
fl, _ = flags_fn(b, src, ASOF)
check("A15 cand không bị sửa", src.equals(snap) and list(src.columns) == list(snap.columns)
      and list(src.index) == list(snap.index), "cand đã bị đổi")
check("A15 … cờ xếp theo (release, ticker)", [f["ticker"] for f in fl] == ["A", "B"], f"{fl}")

# A16 — kiểu dữ liệu `time` của BQ: date / Timestamp / chuỗi đều cho cùng kết quả
for nm, conv in (("Timestamp", pd.Timestamp), ("str", str)):
    def _bq_t(sql, conv=conv):
        return pd.DataFrame({"ticker": ["TY"], "rating": [3], "time": [conv(pd.Timestamp("2026-07-01").date())]})
    fl, err = flags_fn(_bq_t, cand_df([("TY", "2026-10-12")]), ASOF)
    check(f"A16 time kiểu {nm} → cờ đúng ngày", len(fl) == 1 and fl[0]["rating_date"] == "2026-07-01", f"{fl} {err}")

# A17 — kết quả JSON-hoá được (đi thẳng vào golive_v23_status.json)
b = fake_bq({"J": [("2026-07-01", np.int64(3))]})
fl, _ = flags_fn(b, cand_df([("J", "2026-10-12")]), ASOF)
try:
    json.dumps(fl); ok = True
except Exception as ex:
    ok = False; print("     ", ex)
check("A17 cờ JSON-hoá được (rating numpy → int)", ok and type(fl[0]["rating"]) is int, f"{fl}")
# cột rating có NULL ⇒ pandas đổi cả cột sang float: rating phải vẫn ra int 3, không phải 3.0
b = fake_bq({"FL": [("2026-07-01", 3)], "NU": [("2026-07-01", None)]})
fl, _ = flags_fn(b, cand_df([("FL", "2026-10-12"), ("NU", "2026-10-12")]), ASOF)
fm = {f["ticker"]: f["rating"] for f in fl}
check("A17b cột rating lẫn NULL (float) → rating vẫn là int 3 / None", fm == {"FL": 3, "NU": None}
      and type(fm.get("FL")) is int, f"{fl}")

# A18 — MỘT dòng rating có time rác không được làm mất cờ của mã khác
def _bq_mixed(sql):
    return pd.DataFrame({"ticker": ["BAD", "GOOD"], "rating": [3, 3], "time": ["không-phải-ngày", "2026-07-01"]})
fl, err = flags_fn(_bq_mixed, cand_df([("BAD", "2026-10-12"), ("GOOD", "2026-10-12")]), ASOF)
check("A18 time rác ở 1 mã → bỏ qua mã đó, mã còn lại VẪN có cờ, err=None",
      [f["ticker"] for f in fl] == ["GOOD"] and err is None, f"{fl} {err}")

# ══════════════════════════════════════════════════════════════════════════════════════════
print("=" * 78); print(f"  B. cổng 8L lag_filter_low_rating KHÔNG ĐỔI (so với {BASE_REV})"); print("=" * 78)
base_src, base_err = _git_base("lag_rating_filter.py")
new_src = _read("lag_rating_filter.py")
check("B0 đọc được bản gốc lag_rating_filter.py từ git", base_src is not None, f"{base_err}")


def _fn_ast(src, name):
    for node in ast.parse(src).body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.dump(node)
    return None


def _consts(src, names):
    out = {}
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and getattr(node.targets[0], "id", None) in names:
            out[node.targets[0].id] = ast.dump(node.value)
    return out


BASE_LRF = None
if base_src is not None:
    check("B1 AST của lag_filter_low_rating giống hệt bản gốc",
          _fn_ast(base_src, "lag_filter_low_rating") == _fn_ast(new_src, "lag_filter_low_rating")
          and _fn_ast(new_src, "lag_filter_low_rating") is not None)
    check("B2 hằng số RATING_MAX_OK / POLICY_TAG không đổi",
          _consts(base_src, {"RATING_MAX_OK", "POLICY_TAG"}) == _consts(new_src, {"RATING_MAX_OK", "POLICY_TAG"})
          and len(_consts(new_src, {"RATING_MAX_OK", "POLICY_TAG"})) == 2)
    BASE_LRF = types.ModuleType("lag_rating_filter_base")
    exec(compile(base_src, "lag_rating_filter@base", "exec"), BASE_LRF.__dict__)


def _rand_world(rng, n=None, max_age=40):
    """Một 'thế giới' ngẫu nhiên: cand + bảng rating. Trả (cand, table)."""
    n = rng.randint(0, 12) if n is None else n
    tks = rng.sample([f"T{i:02d}" for i in range(30)], n)
    rows, table = [], {}
    for tk in tks:
        rel = pd.Timestamp("2026-10-13") - pd.Timedelta(days=rng.randint(0, max_age))
        rows.append((tk, str(rel.date())))
        mode = rng.choice(["none", "stale", "same", "after", "future_only", "null"])
        if mode == "none":
            continue
        hist = []
        if mode in ("stale", "null"):
            hist.append((str((rel - pd.Timedelta(days=rng.randint(1, 95))).date()), None if mode == "null" else rng.randint(1, 6)))
        if mode == "same":
            hist.append((str((rel - pd.Timedelta(days=90)).date()), rng.randint(1, 6)))
            hist.append((str(rel.date()), rng.randint(1, 6)))
        if mode == "after":
            hist.append((str((rel + pd.Timedelta(days=rng.randint(0, 3))).date()), rng.randint(1, 6)))
        if mode == "future_only":
            hist.append(("2026-12-01", rng.randint(1, 6)))
        table[tk] = hist
    cand = cand_df(rows)
    if n and rng.random() < 0.3:   # thêm sự kiện thứ hai cho 1 mã
        extra = cand.iloc[[0]].copy(); extra["Release_Date"] = extra["Release_Date"] - pd.Timedelta(days=80)
        cand = pd.concat([cand, extra], ignore_index=True)
    return cand, table


def _norm(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str)


if BASE_LRF is not None:
    rng = random.Random(20261013)
    diff = 0; n_cases = 400; n_drop = 0
    for i in range(n_cases):
        cand, table = _rand_world(rng)
        bqf = _boom if i % 25 == 24 else fake_bq(table)
        with contextlib.redirect_stdout(io.StringIO()):   # nuốt dòng WARNING fail-open của cổng
            k0, d0, e0 = BASE_LRF.lag_filter_low_rating(bqf, cand.copy(deep=True), ASOF)
            k1, d1, e1 = LRF.lag_filter_low_rating(bqf, cand.copy(deep=True), ASOF)
        n_drop += len(d1)
        if not (k0.equals(k1) and _norm(d0) == _norm(d1) and e0 == e1):
            diff += 1
    check(f"B3 hành vi cổng trùng bản gốc trên {n_cases} thế giới ngẫu nhiên (có {n_drop} lượt loại)",
          diff == 0 and n_drop > 100, f"{diff} thế giới lệch")

# ══════════════════════════════════════════════════════════════════════════════════════════
print("=" * 78); print(f"  C. khối LAG của golive: bản gốc ({BASE_REV}) vs bản mới — cùng input → cùng order LAG"); print("=" * 78)
gl_base, gl_err = _git_base(GOLIVE_REL)
gl_new = _read(GOLIVE_REL)
check("C0 đọc được bản gốc golive_recommend_v23.py từ git", gl_base is not None, f"{gl_err}")

A_TD, A_BLK, A_END = "def td_offset(ref, off):", "lag_up, lag_recent, lag_source_error = [], [], None", "# ── 5. Allocator"
A_RECS, A_RECS_END = "for it in lag_up:\n    recs.append(", "for tk in basket:"


def _slice(src, a, b):
    i = src.index(a); j = src.index(b, i)
    return src[i:j]


def _run_lag_block(src, lrf_mod, cand, table, bq_fn, live_raises=False):
    """exec khối LAG (td_offset + try-block + dựng recs LAG) trích từ `src`, với mọi phụ thuộc giả lập."""
    td_src = _slice(src, A_TD, "# lag_source_error: None")
    blk_src = _slice(src, A_BLK, A_END)
    recs_src = _slice(src, A_RECS, A_RECS_END)
    latest = ASOF
    trade_dates = list(pd.bdate_range("2026-05-01", latest))

    def _liq(bq, c, asof):       # lọc thanh khoản giả: loại mã kết thúc bằng '7'
        bad = [t for t in c["ticker"] if t.endswith("7")]
        return c[~c["ticker"].isin(bad)].copy(), [{"ticker": t, "reason": "ADV≤0"} for t in sorted(set(bad))], None

    def _forensic(c, asof, workdir=None):   # gate quản trị giả: loại mã kết thúc bằng '9'
        bad = [t for t in c["ticker"] if t.endswith("9")]
        return c[~c["ticker"].isin(bad)].copy(), [{"ticker": t, "kind": "BANNED"} for t in sorted(set(bad))], None

    def _live(start=None):
        if live_raises:
            raise RuntimeError("pkl hỏng")
        c = cand.copy(deep=True)
        c["qualify"] = [not t.endswith("5") for t in c["ticker"]]
        c["pa_HL3"] = 6.0
        c["tier"] = ["LAG_HI" if i % 2 == 0 else "LAG_LO" for i in range(len(c))]
        return c

    fake_mod = types.ModuleType("lag_live_schedule"); fake_mod.live_lag_candidates = _live
    saved = sys.modules.get("lag_live_schedule")
    sys.modules["lag_live_schedule"] = fake_mod
    ns = {"pd": pd, "np": np, "bq": bq_fn, "START": "2026-06-15", "LATEST": latest, "WORKDIR": "/nonexistent",
          "trade_dates": trade_dates, "lag_filter_illiquid": _liq, "lag_filter_forensic_banned": _forensic,
          "lag_filter_low_rating": lrf_mod.lag_filter_low_rating,
          "recs": [], "LAG_TW": {"LAG_HI": 0.10, "LAG_LO": 0.08}, "sec_map": {},
          "print": lambda *a, **k: None}
    for nm in ("lag_rating_stale_flags", "annotate_stale_status", "format_lag_rating_stale_line"):
        if hasattr(lrf_mod, nm):
            ns[nm] = getattr(lrf_mod, nm)
    try:
        with contextlib.redirect_stdout(io.StringIO()):   # cổng thật in WARNING khi fail-open
            exec(compile(td_src, "golive:td_offset", "exec"), ns)
            exec(compile(blk_src, "golive:lag_block", "exec"), ns)
            exec(compile(recs_src, "golive:lag_recs", "exec"), ns)
    finally:
        if saved is None:
            sys.modules.pop("lag_live_schedule", None)
        else:
            sys.modules["lag_live_schedule"] = saved
    decision = {k: ns[k] for k in ("lag_up", "lag_recent", "lag_source_error", "lag_liq_dropped", "lag_liq_error",
                                   "lag_rating_dropped", "lag_rating_error", "lag_forensic_dropped",
                                   "lag_forensic_error", "recs")}
    return decision, ns


if gl_base is not None and BASE_LRF is not None:
    rng = random.Random(1013)
    n_cases, diff, n_orders, n_stale_pass, n_stale_fail, n_src_err = 300, 0, 0, 0, 0, 0
    first_diff = ""
    for i in range(n_cases):
        cand, table = _rand_world(rng, n=rng.randint(0, 14), max_age=14)
        bqf = _boom if i % 30 == 29 else fake_bq(table)
        live_raises = (i % 37 == 36)
        d0, _ = _run_lag_block(gl_base, BASE_LRF, cand, table, bqf, live_raises)
        d1, ns1 = _run_lag_block(gl_new, LRF, cand, table, bqf, live_raises)
        n_orders += len(d1["recs"]); n_src_err += d1["lag_source_error"] is not None
        st = ns1.get("lag_rating_stale") or []
        n_stale_pass += sum(f["gate"] == "PASS" for f in st); n_stale_fail += sum(f["gate"] == "RATING_FAIL" for f in st)
        if _norm(d0) != _norm(d1):
            diff += 1
            first_diff = first_diff or f"case {i}: gốc={_norm(d0)[:300]} mới={_norm(d1)[:300]}"
    check(f"C1 {n_cases} thế giới: lag_up/lag_recent/dropped/recs LAG TRÙNG bản gốc "
          f"({n_orders} dòng order LAG, {n_src_err} lượt nguồn hỏng)", diff == 0, f"{diff} lệch — {first_diff}")
    check("C2 phép so có nội dung thật (có order, có cờ PASS, có cờ RATING_FAIL, có lượt nguồn hỏng)",
          n_orders > 200 and n_stale_pass > 50 and n_stale_fail > 50 and n_src_err >= 5,
          f"orders={n_orders} stale_pass={n_stale_pass} stale_fail={n_stale_fail} src_err={n_src_err}")

    # C3 — ca cố định kiểu TVN: rating cũ =3 (PASS) vẫn VÀO danh sách order; cũ =5 vẫn bị loại; cả hai có cờ
    cand = cand_df([("TVN", "2026-10-08"), ("L40", "2026-10-08"), ("POW", "2026-10-08")])
    table = {"TVN": [("2026-07-30", 3)], "L40": [("2026-07-30", 5)], "POW": [("2026-10-08", 2)]}
    d0, _ = _run_lag_block(gl_base, BASE_LRF, cand, table, fake_bq(table))
    d1, ns1 = _run_lag_block(gl_new, LRF, cand, table, fake_bq(table))
    tk_orders = sorted(r["ticker"] for r in d1["recs"])
    st = {f["ticker"]: f for f in ns1["lag_rating_stale"]}
    check("C3 TVN (rating cũ=3) VẪN là order; L40 (cũ=5) vẫn bị loại; POW (tươi) là order",
          tk_orders == ["POW", "TVN"] and [d["ticker"] for d in d1["lag_rating_dropped"]] == ["L40"]
          and _norm(d0) == _norm(d1), f"{tk_orders} {d1['lag_rating_dropped']}")
    check("C3 … cờ: TVN gate=PASS có status, L40 gate=RATING_FAIL status=None, POW không cờ",
          set(st) == {"TVN", "L40"} and st["TVN"]["gate"] == "PASS" and st["L40"]["gate"] == "RATING_FAIL"
          and st["L40"].get("status") is None, f"{st}")
    rec_status = {r["ticker"]: r["status"] for r in d1["recs"]}
    check("C3 … status của cờ TVN TRÙNG status dòng order TVN trong recs (UPCOMING T+2 phiên tới)",
          st.get("TVN", {}).get("status") == rec_status.get("TVN") == "UPCOMING T+2 phiên tới", f"{st.get('TVN')} vs {rec_status}")
    # ca WINDOW_PASSED: release 10-02 → entry T+5 = 10-09 ≤ LATEST 10-13
    cand_w = cand_df([("OLDW", "2026-10-02")]); table_w = {"OLDW": [("2026-07-30", 2)]}
    d1w, ns1w = _run_lag_block(gl_new, LRF, cand_w, table_w, fake_bq(table_w))
    stw = ns1w["lag_rating_stale"]
    check("C3 … ca cửa sổ đã qua: status cờ = status recs = 'WINDOW_PASSED 2026-10-09'",
          len(stw) == 1 and stw[0].get("status") == d1w["recs"][0]["status"] == "WINDOW_PASSED 2026-10-09", f"{stw} {d1w['recs']}")
    check("C3 … dòng cảnh báo được dựng trong khối golive", "TVN" in (ns1.get("_lag_stale_line") or "")
          and "L40" in (ns1.get("_lag_stale_line") or ""), f"{ns1.get('_lag_stale_line')}")

    # C4 — nguồn rating hỏng: cổng fail-open như cũ, cờ báo lỗi riêng, order không đổi
    d0, _ = _run_lag_block(gl_base, BASE_LRF, cand, table, _boom)
    d1, ns1 = _run_lag_block(gl_new, LRF, cand, table, _boom)
    check("C4 BQ rating hỏng → order trùng bản gốc + lag_rating_stale_error != None",
          _norm(d0) == _norm(d1) and ns1["lag_rating_stale_error"] is not None and ns1["lag_rating_stale"] == []
          and d1["lag_rating_error"] is not None, f"{ns1.get('lag_rating_stale_error')}")

    # C5 — nguồn LAG hỏng trước khi tới cờ: cờ rỗng, không lỗi giả
    d1, ns1 = _run_lag_block(gl_new, LRF, cand, table, fake_bq(table), live_raises=True)
    check("C5 nguồn LAG hỏng → cờ rỗng, stale_error None, lag_source_error set",
          ns1["lag_rating_stale"] == [] and ns1["lag_rating_stale_error"] is None and d1["lag_source_error"] is not None)

# ══════════════════════════════════════════════════════════════════════════════════════════
print("=" * 78); print("  D. annotate_stale_status + format_lag_rating_stale_line"); print("=" * 78)
import datetime as _dt  # noqa: E402

fl = [{"ticker": "AAA", "rating": 3, "rating_date": "2026-07-20", "release_date": "2026-10-08", "gate": "PASS"},
      {"ticker": "BBB", "rating": 2, "rating_date": "2026-07-21", "release_date": "2026-10-02", "gate": "PASS"},
      {"ticker": "CCC", "rating": 5, "rating_date": "2026-07-22", "release_date": "2026-10-09", "gate": "RATING_FAIL"},
      {"ticker": "DDD", "rating": 1, "rating_date": "2026-07-23", "release_date": "2026-09-01", "gate": "PASS"}]
up = [{"ticker": "AAA", "release": _dt.date(2026, 10, 8), "entry": "2026-10-15"}]
rc = [{"ticker": "BBB", "release": _dt.date(2026, 10, 2), "entry": "2026-10-09"},
      {"ticker": "DDD", "release": _dt.date(2026, 6, 1), "entry": "2026-06-08"}]   # DDD: sự kiện KHÁC (release khác)
up_snap, rc_snap = json.dumps(up, default=str), json.dumps(rc, default=str)
LRF.annotate_stale_status(fl, up, rc)
sm = {f["ticker"]: f["status"] for f in fl}
check("D1 status: AAA=UPCOMING, BBB=WINDOW_PASSED, CCC=None, DDD=None (khớp theo CẢ release)",
      sm == {"AAA": "UPCOMING 2026-10-15", "BBB": "WINDOW_PASSED 2026-10-09", "CCC": None, "DDD": None}, f"{sm}")
check("D1 … lag_up/lag_recent không bị sửa", json.dumps(up, default=str) == up_snap and json.dumps(rc, default=str) == rc_snap)

line = LRF.format_lag_rating_stale_line(fl)
check("D2 markdown: 1 dòng, có tên cờ + 'CHỈ CẢNH BÁO'", "\n" not in line and "**lag_rating_stale**" in line and "CHỈ CẢNH BÁO" in line, line)
check("D2 … AAA/BBB ở nhóm CHO QUA kèm status + ngày", "AAA (8L=3 chấm 2026-07-20, trước BCTC 2026-10-08, UPCOMING 2026-10-15)" in line
      and "BBB (8L=2 chấm 2026-07-21, trước BCTC 2026-10-02, WINDOW_PASSED 2026-10-09)" in line, line)
i_pass, i_fail = line.find("CHO QUA"), line.find("cổng LOẠI")
check("D2 … CCC ở nhóm LOẠI, đúng thứ tự nhóm", 0 < i_pass < i_fail < line.find("CCC (8L=5"), line)
check("D2 … DDD (PASS, ngoài cửa sổ) chỉ được ĐẾM, không nêu tên", "DDD" not in line and "+1 sự kiện ngoài cửa sổ entry" in line, line)

check("D3 không có cờ, không lỗi → chuỗi rỗng", LRF.format_lag_rating_stale_line([]) == ""
      and LRF.format_lag_rating_stale_line(None) == "" and LRF.format_lag_rating_stale_line([], None, html=True) == "")
el = LRF.format_lag_rating_stale_line([], "RuntimeError: BQ down")
check("D4 có lỗi → dòng 'KHÔNG kiểm được' kèm nguyên văn lỗi", "KHÔNG kiểm được" in el and "BQ down" in el and "\n" not in el, el)

hl = LRF.format_lag_rating_stale_line(
    [{"ticker": "A<b>", "rating": 3, "rating_date": "2026-07-20", "release_date": "2026-10-08", "gate": "PASS",
      "status": "UPCOMING T+2 phiên tới"}], html=True)
check("D5 HTML: <b> cho tên cờ, dữ liệu được escape, không còn '**'",
      "<b>lag_rating_stale</b>" in hl and "A&lt;b&gt;" in hl and "**" not in hl, hl)
check("D5 HTML: ngoài cặp <b></b> không còn dấu '<' '>' trần (Telegram parse_mode=HTML sẽ từ chối)",
      "<" not in hl.replace("<b>", "").replace("</b>", "") and ">" not in hl.replace("<b>", "").replace("</b>", ""), hl)
he = LRF.format_lag_rating_stale_line([], "Err <x> & y", html=True)
check("D5 HTML: chuỗi lỗi được escape", "&lt;x&gt; &amp; y" in he, he)

many = [{"ticker": f"M{i:02d}", "rating": 3, "rating_date": "2026-07-20", "release_date": "2026-10-08",
         "gate": "PASS", "status": "UPCOMING 2026-10-15"} for i in range(LRF.STALE_LIST_MAX + 5)]
ml = LRF.format_lag_rating_stale_line(many)
check(f"D6 cắt ở {LRF.STALE_LIST_MAX} mã + '(+5)'", f"M{LRF.STALE_LIST_MAX - 1:02d}" in ml
      and f"M{LRF.STALE_LIST_MAX:02d}" not in ml and "(+5)" in ml, ml[-120:])

ok = True
for garbage in ([{"ticker": "X"}], [None], "abc", 5, [{"gate": "PASS", "status": "U"}]):
    try:
        r = LRF.format_lag_rating_stale_line(garbage)
        ok = ok and isinstance(r, str)
        LRF.annotate_stale_status(garbage if isinstance(garbage, list) else [], None, None)
    except Exception as ex:
        ok = False; print("      raise:", garbage, ex)
check("D7 rác → formatter/annotate không raise, luôn trả str", ok)
check("D7 … cờ rác (thiếu khoá) vẫn ra dòng cảnh báo, không im lặng",
      LRF.format_lag_rating_stale_line([{"ticker": "X"}]) != "")

# ══════════════════════════════════════════════════════════════════════════════════════════
print("=" * 78); print("  E. chỗ nối: golive + telegram"); print("=" * 78)
i_flag = gl_new.find("lag_rating_stale, lag_rating_stale_error = lag_rating_stale_flags(bq, cand, LATEST)")
i_gate = gl_new.find("cand, lag_rating_dropped, lag_rating_error = lag_filter_low_rating(bq, cand, LATEST)")
i_liq = gl_new.find("cand, lag_liq_dropped, lag_liq_error = lag_filter_illiquid(bq, cand, LATEST)")
check("E1 golive: cờ đo SAU lọc thanh khoản và TRƯỚC cổng 8L, cùng (bq, cand, LATEST)", 0 < i_liq < i_flag < i_gate,
      f"liq={i_liq} flag={i_flag} gate={i_gate}")
check("E2 golive: cổng 8L vẫn được gọi đúng 1 lần, kết quả gán lại cand",
      gl_new.count("lag_filter_low_rating(bq, cand, LATEST)") == 1)
check("E3 golive: 3 khoá status",
      all(k in gl_new for k in ('"lag_rating_stale": lag_rating_stale,', '"n_lag_rating_stale": len(lag_rating_stale),',
                                '"lag_rating_stale_error": lag_rating_stale_error,')))
i_md = gl_new.find('L.append("\\n" + _lag_stale_line)')
check("E4 golive: dòng cảnh báo được đưa vào .md sau khối 'Cửa sổ entry đã qua'",
      i_md > gl_new.find("Cửa sổ entry đã qua trong các phiên gần nhất") > 0, f"{i_md}")
check("E5 golive: biến cờ được khởi tạo NGOÀI try (nguồn LAG hỏng không gây NameError)",
      0 < gl_new.find("lag_rating_stale, lag_rating_stale_error = [], None") < gl_new.find("from lag_live_schedule import"))
# các gate khác không bị chạm: mọi dòng bị XOÁ so với bản gốc phải nằm trong danh sách cho phép
if gl_base is not None:
    # bỏ dòng CHỈ-comment: commit sau được duyệt có quyền sửa chú thích (ea82525f0 đổi nhãn CCTG
    # 6M→12M trong comment) — E6 canh dòng CODE của gate khác, không canh chữ trong comment
    removed = [ln for ln in gl_base.splitlines()
               if ln.strip() and not ln.strip().startswith("#") and ln not in set(gl_new.splitlines())]
    check("E6 golive: so với bản gốc chỉ MẤT đúng 1 dòng code (dòng import được viết lại)",
          removed == ["from lag_rating_filter import lag_filter_low_rating"], f"{removed}")

try:
    sys.path.insert(0, TARGET)
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location("telegram_recommend_under_test", os.path.join(TARGET, "telegram_recommend.py"))
    TR = _ilu.module_from_spec(_spec); _spec.loader.exec_module(TR)
    sys.path.insert(0, TARGET)   # telegram_recommend chèn WORKDIR canonical lên đầu — trả TARGET về trước
    empty = pd.DataFrame()
    lag_df = pd.DataFrame([{"ticker": "AAA", "play_type": "LAG_HI", "weight_pct": 10.0, "status": "WINDOW_PASSED 2026-10-09"}])
    base_st = {"w_lag_target": 0.5, "w_lag_current": 0.5, "capit_episode_open": False, "breadth_oversold": 0.1}
    os.environ.pop("EXTRA_WARN_HEADER", None)

    def _msg(extra):
        return TR.build_message("2026-10-13", 3, "NEUTRAL", empty, lag_df, empty, {}, 0,
                                include_universe=False, v23_status=dict(base_st, **extra))
    m_none = _msg({})
    m_flag = _msg({"lag_rating_stale": [fl[0]], "lag_rating_stale_error": None})
    m_err = _msg({"lag_rating_stale": [], "lag_rating_stale_error": "RuntimeError: BQ down"})
    check("E7 telegram: status không có cờ → KHÔNG có dòng cảnh báo", "lag_rating_stale" not in m_none)
    check("E8 telegram: có cờ → dòng HTML ngay sau BOOK B, nêu mã + status",
          "<b>lag_rating_stale</b>" in m_flag and "AAA (8L=3" in m_flag
          and m_flag.find("BOOK B") < m_flag.find("<b>lag_rating_stale</b>") < m_flag.find("🧯"), m_flag[:200])
    check("E9 telegram: lỗi kiểm → dòng 'KHÔNG kiểm được'", "KHÔNG kiểm được" in m_err)
    check("E10 telegram: phần còn lại của tin nhắn KHÔNG đổi khi thêm cờ",
          m_flag.replace("\n" + LRF.format_lag_rating_stale_line([fl[0]], None, html=True), "", 1)
          .split("Sent:")[0] == m_none.split("Sent:")[0]
          and [l for l in m_none.splitlines() if "Sent:" not in l]
          == [l for l in m_flag.splitlines() if "Sent:" not in l and "lag_rating_stale" not in l])
except Exception as ex:
    check("E7-E10 telegram build_message chạy được", False, f"{type(ex).__name__}: {ex}")

# ══════════════════════════════════════════════════════════════════════════════════════════
if "--live" in sys.argv:
    print("=" * 78); print("  F. LIVE (BQ thật, chỉ đọc)"); print("=" * 78)
    os.environ.pop("BQ_LOCAL_CACHE", None)
    sys.path.insert(0, HERE)
    from simulate_holistic_nav import bq  # noqa: E402
    live_c = cand_df([("KBC", "2026-10-12"), ("POW", "2026-07-20"), ("TVN", "2026-07-30")])
    fl, err = LRF.lag_rating_stale_flags(bq, live_c, pd.Timestamp("2026-10-13"))
    print(f"  cờ live @2026-10-13: {fl}  err={err}")
    check("F1 live: truy vấn không lỗi", err is None, f"{err}")
    check("F2 live: POW/TVN (BCTC Q2 đã re-rate từ lâu) KHÔNG bị cờ", not {f["ticker"] for f in fl} & {"POW", "TVN"}, f"{fl}")
    k, d, e = LRF.lag_filter_low_rating(bq, live_c, pd.Timestamp("2026-10-13"))
    gm = {f["ticker"]: f["gate"] for f in fl}
    check("F3 live: nhãn gate của cờ khớp quyết định cổng thật",
          e is None and all((g == "PASS") == (t in set(k["ticker"])) for t, g in gm.items()), f"{gm} kept={list(k['ticker'])}")

print("=" * 78)
print(f"  TỔNG: {PASS} PASS / {FAIL} FAIL   (target={TARGET}, base={BASE_REV})")
sys.exit(1 if FAIL else 0)
