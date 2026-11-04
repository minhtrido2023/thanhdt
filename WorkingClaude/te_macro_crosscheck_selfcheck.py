#!/usr/bin/env python3
"""Selfcheck te_macro_crosscheck.py — chạy: env -u TZ $DNA_PYEXE te_macro_crosscheck_selfcheck.py
Hermetic: fixture thay BQ, data dir tạm, notify tắt. Có ca LỆCH GIẢ LẬP ⇒ phải cảnh báo."""
import contextlib, io, json, os, sys, tempfile

tmp = tempfile.mkdtemp()
os.environ.update(TE_XCHECK_SELFCHECK="1", TE_XCHECK_DATA_DIR=tmp, TE_XCHECK_FIXTURE=os.path.join(tmp, "fx.json"),
                  TE_XCHECK_FAKE_NOW="2026-11-05T01:00:00+00:00")
csv = os.path.join(tmp, "fiin.csv")
os.environ["FIINPRO_CPI_CSV"] = csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import te_macro_crosscheck as T
from cpi_vn import NSO_CPI_YOY_REAL
from sbv_macro_overlay import SBV_REFI_EVENTS as EV

FAIL = []
def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: FAIL.append(m)

def eom(ym):
    import calendar
    y, m = map(int, ym.split("-")); return f"{ym}-{calendar.monthrange(y, m)[1]:02d}"

# fiin: 2014-01..2026-08, TE = fiin (khớp) trừ NSO tháng dùng giá trị NSO cho cả hai
months = [f"{y}-{m:02d}" for y in range(2014, 2027) for m in range(1, 13) if f"{y}-{m:02d}" <= "2026-08"]
nso = {k[:7]: v for k, v in NSO_CPI_YOY_REAL.items()}
fiin = {m: nso.get(m, 3.0) for m in months}
open(csv, "w").write("month,cpi_yoy_pct\n" + "".join(f"{m},{v}\n" for m, v in fiin.items()))
cpi_te = {eom(m): v for m, v in fiin.items()}; cpi_te[eom("2026-09")] = 5.1
pol_te = {}
for ym in [f"{y}-{m:02d}" for y in range(2014, 2027) for m in range(1, 13) if f"{y}-{m:02d}" <= "2026-10"]:
    pol_te[eom(ym)] = T._expected(EV, eom(ym))
pol_te["2020-09-30"] = 4.0      # sự kiện 2020-10-01 bị TE gán nhãn cuối tháng trước ⇒ biên, KHÔNG phải lệch
FRESH = "2026-11-04T15:00:00+00:00"

def run(pol=pol_te, cpi=cpi_te, pf=FRESH, cf=FRESH, perr=None, cerr=None):
    fx = {"vn_policy_rate": {"rows": pol, "fetched_at": pf, **({"error": perr} if perr else {})},
          "vn_cpi_yoy": {"rows": cpi, "fetched_at": cf, **({"error": cerr} if cerr else {})}}
    json.dump(fx, open(os.environ["TE_XCHECK_FIXTURE"], "w"))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = T.run()
    return r, buf.getvalue()

sbv_log = os.path.join(T.HERE, "data", "sbv_verify_log.json")
before = os.stat(sbv_log).st_mtime_ns if os.path.exists(sbv_log) else None

r, out = run()
ok(r["status"] == "ok" and r["n_alerts"] == 0, f"1. khớp hoàn toàn ⇒ ok, không cảnh báo (status={r['status']}, alerts={r['n_alerts']})")
ok(r["policy"]["alerts"] == [], "2. lệch biên tháng (2020-09-30) KHÔNG bị coi là lệch")
ok(r["cpi"]["tier_assessment"]["can_replace_interpolation"] is True
   and "2026-09" in r["cpi"]["tier_assessment"]["te_months_beyond_fiin"], "3. TE phủ tháng sau fiinprox, đủ tư cách làm tầng")

p2 = dict(pol_te); p2["2026-10-31"] = 4.0
r, out = run(pol=p2)
ok(r["status"] == "alert" and not r["policy"]["current"]["match"] and "[no-notify]" in out and "HIỆN TẠI" in out,
   "4. GIẢ LẬP TE hạ lãi điều hành 4,0 vs 4,5 ⇒ cảnh báo lãi hiện tại")

p3 = dict(pol_te); p3["2019-05-31"] = 9.9
r, out = run(pol=p3)
ok(r["status"] == "alert" and any(a["month_end"] == "2019-05-31" for a in r["policy"]["alerts"]), "5. lệch lịch sử ≥2014 ⇒ cảnh báo")

p4 = dict(pol_te); p4["2008-05-31"] = 13.0
r, out = run(pol=p4)
ok(r["status"] == "ok" and r["policy"]["info_pre2014"], "6. lệch pre-2014 chỉ là thông tin (bảng sự kiện CONTEXTUAL)")

c2 = dict(cpi_te); c2[eom("2026-03")] = 4.0     # NSO 4,65
r, out = run(cpi=c2)
ok(r["status"] == "alert" and any(a["vs"] == "NSO" and a["month"] == "2026-03" for a in r["cpi"]["alerts"]), "7. GIẢ LẬP CPI lệch NSO 0,65pp ⇒ cảnh báo")

c3 = dict(cpi_te); c3[eom("2018-07")] = 3.5      # fiin 3,0 ⇒ +0,5
r, out = run(cpi=c3)
ok(r["status"] == "alert" and any(a["vs"] == "fiinprox" for a in r["cpi"]["alerts"])
   and r["cpi"]["tier_assessment"]["can_replace_interpolation"] is False, "8. CPI lệch fiinprox 0,5pp ⇒ cảnh báo + KHÔNG đề xuất làm tầng")

r, out = run(pf="2026-10-20T15:00:00+00:00")
ok(r["status"] == "unavailable" and "policy" not in r and "KHÔNG dùng số cũ" in out, "9. series stale >7 ngày ⇒ unavailable, không điền số cũ")

r, out = run(cerr="403 quota")
ok(r["status"] == "unavailable" and "403 quota" in r["unavailable"], "10. BQ lỗi ⇒ unavailable, trích lỗi thật (§29)")

after = os.stat(sbv_log).st_mtime_ns if os.path.exists(sbv_log) else None
ok(before == after, "11. data/sbv_verify_log.json KHÔNG bị đụng")
lg = json.load(open(T.LOG_PATH))
ok(lg["last"]["status"] == "unavailable" and len(lg["history"]) == 8 and os.path.dirname(T.LOG_PATH) == tmp,
   "12. log riêng ghi đúng, history tăng, ghi vào data dir tạm")
print("\nTZ env =", os.environ.get("TZ"))
print("TẤT CẢ PASS" if not FAIL else f"FAIL {len(FAIL)}: {FAIL}")
sys.exit(1 if FAIL else 0)
