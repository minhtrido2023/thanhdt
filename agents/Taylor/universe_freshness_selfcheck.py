#!/usr/bin/env python3
"""universe_freshness_selfcheck.py — cổng độ tươi watchlist của anomaly_scan (§14).

Job Taylor_20260814_041116 (Việc E1). Kiểm HERMETIC: mọi ca dựng file active_nav giả trong
tmpdir + bơm `now_ict` tường minh — KHÔNG đọc file production, KHÔNG phụ thuộc ngày chạy
(§23 hệ luận 1: selfcheck assert lên trạng thái SỐNG là selfcheck tự vô hiệu theo thời gian).

Chạy: python3 universe_freshness_selfcheck.py
Chạy đối kháng TZ (§16/§19): env -u TZ ... / TZ=America/New_York ... — kết quả phải Y HỆT.
"""
import datetime as dt
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anomaly_scan as A

PASS = FAIL = 0


def chk(name, cond, extra=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name} {extra}")


def _mkfiles(tmp, dates):
    """dates: {label: computed_at|None|'BROKEN'} → list path."""
    out = []
    for lbl, d in dates.items():
        p = os.path.join(tmp, f"active_nav_{lbl}.json")
        if d == "BROKEN":
            open(p, "w").write("{not json")
        else:
            body = {"account": lbl, "positions": [{"ticker": "ACB"}, {"ticker": "FPT"}]}
            if d is not None:
                body["computed_at"] = d
            json.dump(body, open(p, "w"))
        out.append(p)
    return out


# ---------------------------------------------------------------- A. expected_universe_asof
# Lịch neo: 2026-08-10 T2 … 2026-08-14 T6; 2026-08-15 T7; 2026-08-17 T2.
print("A. expected_universe_asof — producer chạy 20:15 ICT T2-T6, ngưỡng 'đáng lẽ xong' 21:00")
CASES = [
    # (now_ict,                              expected, vì sao)
    (dt.datetime(2026, 8, 17, 8, 20), "2026-08-14", "sáng T2 08:20 ⇒ bản của T6 tuần trước"),
    (dt.datetime(2026, 8, 11, 8, 20), "2026-08-10", "sáng T3 ⇒ bản của T2"),
    (dt.datetime(2026, 8, 11, 20, 30), "2026-08-10", "20:30 T3 — producer 20:15 CHƯA chắc xong (ngưỡng 21:00)"),
    (dt.datetime(2026, 8, 11, 21, 0), "2026-08-11", "21:00 T3 ⇒ đã phải có bản hôm nay"),
    (dt.datetime(2026, 8, 15, 10, 0), "2026-08-14", "T7 ⇒ bản của T6"),
    (dt.datetime(2026, 8, 16, 23, 0), "2026-08-14", "CN 23:00 ⇒ vẫn là T6, KHÔNG phải CN"),
    # 2026-09-02 Quốc khánh (T4) — ngày lễ phải bị bỏ qua, không được coi là phiên.
    (dt.datetime(2026, 9, 3, 8, 0), "2026-09-01", "sáng sau lễ Quốc khánh 02/09 ⇒ nhảy về 01/09"),
    (dt.datetime(2026, 9, 2, 22, 0), "2026-09-01", "22:00 ĐÚNG ngày lễ ⇒ không có bản của ngày lễ"),
]
for now, exp, why in CASES:
    got = str(A.expected_universe_asof(now))
    chk(f"{now:%Y-%m-%d %H:%M} → {exp} ({why})", got == exp, f"got={got}")

# ---------------------------------------------------------------- B. universe_freshness
print("B. universe_freshness — phân loại tươi/quá hạn")
NOW = dt.datetime(2026, 8, 17, 8, 20)   # sáng T2, kỳ vọng computed_at = 2026-08-14 (T6)
with tempfile.TemporaryDirectory() as tmp:
    f = _mkfiles(tmp, {"SpaceX": "2026-08-14", "ZaloPay": "2026-08-14"})
    r = A.universe_freshness(f, now_ict=NOW)
    chk("B1 cả 2 account đúng phiên T6 → KHÔNG stale", r["is_stale"] is False, r)
    chk("B1b lag_sessions = 0", r["lag_sessions"] == 0, r)

with tempfile.TemporaryDirectory() as tmp:
    f = _mkfiles(tmp, {"SpaceX": "2026-08-13", "ZaloPay": "2026-08-13"})
    r = A.universe_freshness(f, now_ict=NOW)
    chk("B2 trễ 1 phiên (T5 thay vì T6) → stale, lag=1", r["is_stale"] and r["lag_sessions"] == 1, r)

with tempfile.TemporaryDirectory() as tmp:
    # LỖ HỔNG THẬT được thiết kế để bắt: 1 account tươi, 1 account chết ⇒ vị thế của account
    # chết vô hình. Lấy min() chứ không phải max() — max() sẽ NUỐT đúng ca này.
    f = _mkfiles(tmp, {"SpaceX": "2026-08-14", "ZaloPay": "2026-08-11"})
    r = A.universe_freshness(f, now_ict=NOW)
    chk("B3 1 account tươi + 1 account trễ 3 phiên → stale (lấy CŨ NHẤT)",
        r["is_stale"] and r["asof"] == "2026-08-11" and r["lag_sessions"] == 3, r)

with tempfile.TemporaryDirectory() as tmp:
    f = _mkfiles(tmp, {"SpaceX": "2026-08-17", "ZaloPay": "2026-08-17"})
    r = A.universe_freshness(f, now_ict=NOW)
    chk("B4 file MỚI HƠN kỳ vọng (chạy tay giữa ngày) → KHÔNG stale", r["is_stale"] is False, r)

r = A.universe_freshness([], now_ict=NOW)
chk("B5 không có file nào → stale", r["is_stale"] and "không thấy file" in r["reason"], r)

with tempfile.TemporaryDirectory() as tmp:
    f = _mkfiles(tmp, {"SpaceX": "BROKEN"})
    r = A.universe_freshness(f, now_ict=NOW)
    chk("B6 JSON hỏng → stale (không im lặng coi là tươi)", r["is_stale"], r)

with tempfile.TemporaryDirectory() as tmp:
    f = _mkfiles(tmp, {"SpaceX": None})
    r = A.universe_freshness(f, now_ict=NOW)
    chk("B7 thiếu hẳn field computed_at → stale", r["is_stale"], r)

with tempfile.TemporaryDirectory() as tmp:
    f = _mkfiles(tmp, {"SpaceX": "hôm qua"})
    r = A.universe_freshness(f, now_ict=NOW)
    chk("B8 computed_at không parse được → stale", r["is_stale"], r)

# ---------------------------------------------------------------- C. chứng minh NGƯỢC
print("C. Ca chứng minh ngược — cổng có thật sự PHÂN BIỆT, không phải luôn trả 1 giá trị")
with tempfile.TemporaryDirectory() as tmp:
    fresh = A.universe_freshness(_mkfiles(tmp, {"A": "2026-08-14"}), now_ict=NOW)["is_stale"]
with tempfile.TemporaryDirectory() as tmp:
    stale = A.universe_freshness(_mkfiles(tmp, {"A": "2026-08-14"}),
                                 now_ict=dt.datetime(2026, 8, 18, 8, 20))["is_stale"]
chk("C1 CÙNG file: T2 sáng → tươi, T3 sáng → quá hạn", (fresh is False) and (stale is True),
    f"fresh={fresh} stale={stale}")

# ---------------------------------------------------------------- D. độc lập TZ (§16)
print("D. _ict_now() không phụ thuộc TZ của process (§16)")
_utc = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)
delta = abs((A._ict_now() - (_utc + dt.timedelta(hours=7))).total_seconds())
chk(f"D1 _ict_now() == UTC+7 (lệch {delta:.1f}s, TZ hiện tại={os.environ.get('TZ', '(unset)')})",
    delta < 5)

# ---------------------------------------------------------------- E. hợp đồng load_universe
print("E. Hợp đồng load_universe() — 3 giá trị, caller không thể vô tình bỏ meta")
import inspect
src = inspect.getsource(A.load_universe)
chk("E1 trả về 3 giá trị (hold, wl, meta)", "return hold, wl, meta" in src)
chk("E2 mọi caller trong file đã unpack 3 giá trị",
    A_src := open(A.__file__, encoding="utf-8").read(),
    "")
bad = [ln for ln in A_src.splitlines() if "= load_universe(" in ln and ln.count(",") < 2]
chk("E3 không còn caller nào unpack 2 giá trị", not bad, bad)

print(f"\n{PASS} pass / {FAIL} fail")
sys.exit(1 if FAIL else 0)
