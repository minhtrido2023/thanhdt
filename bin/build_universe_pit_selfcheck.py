#!/usr/bin/env python3
"""
build_universe_pit_selfcheck.py — selfcheck cho `bin/build_universe_pit.py` (G1).

Bao gồm:
  A. B8 integrity gate (thuần, không I/O) — 3 case dispatch yêu cầu + negative controls
  B. Atomic write — kill giữa chừng không để lại file dở dang
  C. Membership SHA — ổn định, không phụ thuộc thứ tự
  D. (chỉ khi --live) idempotent thật trên BQ: chạy 2 lần cùng ngày → lần 2 REFUSED,
     số dòng trong bảng KHÔNG đổi.

Chạy:  python3 build_universe_pit_selfcheck.py          # A-C, không chạm BQ
       python3 build_universe_pit_selfcheck.py --live   # thêm D
"""
import os, sys, json, tempfile, importlib.util

os.environ.pop("BQ_LOCAL_CACHE", None)
_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("bup", os.path.join(_HERE, "build_universe_pit.py"))
bup = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bup)

PASS, FAIL = [], []


def ck(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}{(' — ' + detail) if detail else ''}")


# ── A. B8 gate ───────────────────────────────────────────────────────────────
print("[A] B8 integrity gate")
base_in = [300] * 20          # trung vị 300
base_raw = [1200] * 20        # trung vị 1200

# A1 — bình thường: pass
v = bup.check_b8(305, base_in, 1195, base_raw, 0)
ck("A1 ngay binh thuong -> pass", v == [], str(v))

# A2 — case dispatch #1: lệch > +15% số mã
v = bup.check_b8(346, base_in, 1200, base_raw, 0)   # +15,3%
ck("A2 n_in +15,3% -> B8_COUNT_DEV", any("B8_COUNT_DEV" in x for x in v), str(v))
v = bup.check_b8(254, base_in, 1200, base_raw, 0)   # -15,3%
ck("A2b n_in -15,3% -> B8_COUNT_DEV", any("B8_COUNT_DEV" in x for x in v), str(v))
# biên: đúng 15% phải PASS (không chặn nhầm ngày hợp lệ)
v = bup.check_b8(345, base_in, 1200, base_raw, 0)   # +15,0%
ck("A2c bien +15,0% -> pass (khong chan nham)", v == [], str(v))

# A3 — case dispatch #2: dòng thô `ticker` < 90% trung vị
v = bup.check_b8(300, base_in, 1079, base_raw, 0)   # 89,9%
ck("A3 raw 89,9% -> B8_RAW_DEPTH", any("B8_RAW_DEPTH" in x for x in v), str(v))
v = bup.check_b8(300, base_in, 1080, base_raw, 0)   # đúng 90%
ck("A3b bien 90,0% -> pass", v == [], str(v))

# A4 — case dispatch #3: đã có dòng cho ngày đó (double-run)
v = bup.check_b8(300, base_in, 1200, base_raw, 7)
ck("A4 existing_rows=7 -> B8_DUPLICATE", any("B8_DUPLICATE" in x for x in v), str(v))

# A5 — duplicate chặn KỂ CẢ khi tắt gate lệch (backfill) — dispatch: không được ghi đè
v = bup.check_b8(9999, base_in, 1, base_raw, 3, enforce_deviation=False)
ck("A5 backfill van chan duplicate", v == ["".join(v[:1])] and "B8_DUPLICATE" in v[0], str(v))

# A6 — chưa đủ mẫu tham chiếu (<5 ngày): không chặn theo lệch (ngày đầu backfill)
v = bup.check_b8(9999, [300, 300], 1, [1200, 1200], 0)
ck("A6 <5 ngay tham chieu -> khong chan theo lech", v == [], str(v))

# A7 — nhiều vi phạm cùng lúc thì báo hết
v = bup.check_b8(500, base_in, 100, base_raw, 5)
ck("A7 bao du 3 vi pham", len(v) == 3, str(v))

# ── B. atomic write ──────────────────────────────────────────────────────────
print("[B] atomic write")
with tempfile.TemporaryDirectory() as td:
    p = os.path.join(td, "sub", "art.json")
    bup.atomic_write_json(p, {"a": 1})
    ck("B1 ghi duoc + tao thu muc", json.load(open(p))["a"] == 1)

    # ghi đè: nội dung cũ còn nguyên vẹn nếu quá trình chết trước os.replace
    orig = json.dumps({"a": 1})
    real_replace = os.replace
    try:
        os.replace = lambda *a, **k: (_ for _ in ()).throw(KeyboardInterrupt("kill giua chung"))
        try:
            bup.atomic_write_json(p, {"a": 2})
        except KeyboardInterrupt:
            pass
    finally:
        os.replace = real_replace
    ck("B2 kill truoc replace -> file dich con nguyen ban cu",
       json.dumps(json.load(open(p))) == orig)
    ck("B3 khong doc nham file .tmp (dich van la 1 file duy nhat)",
       len([f for f in os.listdir(os.path.dirname(p)) if f == "art.json"]) == 1)

# ── C. membership sha ────────────────────────────────────────────────────────
print("[C] membership sha")
ck("C1 doc lap thu tu", bup.membership_sha(["B", "A"]) == bup.membership_sha(["A", "B"]))
ck("C2 doi tap -> doi sha", bup.membership_sha(["A", "B"]) != bup.membership_sha(["A", "C"]))

# ── D. idempotent thật trên BQ ───────────────────────────────────────────────
if "--live" in sys.argv:
    print("[D] idempotent tren BQ (live)")
    client = bup.get_client()
    ref = bup.ensure_table(client)
    day = bup._q(client, f"SELECT MAX(time) AS d FROM `{ref}`")[0]["d"]
    if day is None:
        print("  SKIP — bang rong, chay backfill truoc")
    else:
        n0 = bup._q(client, f"SELECT COUNT(*) AS n FROM `{ref}` WHERE time = DATE'{day}'")[0]["n"]
        res = bup.build_day(client, ref, day, day)
        n1 = bup._q(client, f"SELECT COUNT(*) AS n FROM `{ref}` WHERE time = DATE'{day}'")[0]["n"]
        ck("D1 chay lai ngay da co -> REFUSED", res.get("status") == "REFUSED", str(res))
        ck("D2 so dong KHONG doi", n0 == n1, f"{n0} -> {n1}")
        dup = bup._q(client, f"SELECT COUNT(*) AS n FROM (SELECT time, ticker FROM `{ref}` "
                             f"GROUP BY time, ticker HAVING COUNT(*) > 1)")[0]["n"]
        ck("D3 khong co (time,ticker) trung trong toan bang", dup == 0, f"dup={dup}")

print(f"\n=== {len(PASS)} PASS / {len(FAIL)} FAIL ===")
if FAIL:
    print("FAILED:", FAIL)
sys.exit(1 if FAIL else 0)
