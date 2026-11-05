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
ok(r["status"] == "partial" and "policy" not in r and "cpi" in r and "KHÔNG dùng số cũ" in r["policy_unavailable"]
   and "nhánh policy KHÔNG kiểm được" in out, "9. policy stale >7 ngày, CPI sạch ⇒ partial, vẫn chạy nhánh CPI, không điền số cũ")

r, out = run(cerr="403 quota")
ok(r["status"] == "partial" and "403 quota" in r["cpi_unavailable"] and "policy" in r, "10. CPI BQ lỗi, policy sạch ⇒ partial, trích lỗi thật (§29)")

r, out = run(pf="2026-10-20T15:00:00+00:00", cerr="403 quota")
ok(r["status"] == "unavailable" and "403 quota" in r["unavailable"] and "KHÔNG dùng số cũ" in r["unavailable"],
   "10b. cả hai nhánh hỏng ⇒ unavailable, liệt kê cả hai lý do")

r, out = run(pol=p2, cerr="403 quota")
ok(r["status"] == "alert" and "HIỆN TẠI" in out and "Nhánh cpi KHÔNG kiểm được" in out and "403 quota" in out
   and out.count("[no-notify]") == 1, "13. policy-alert + CPI unavailable ⇒ MỘT tin gộp có cả cảnh báo lẫn nhánh unavailable")

r, out = run(cpi=c2, pf="2026-10-20T15:00:00+00:00")
ok(r["status"] == "alert" and any(a["vs"] == "NSO" for a in r["cpi"]["alerts"]) and "Nhánh policy KHÔNG kiểm được" in out
   and out.count("[no-notify]") == 1, "14. CPI-alert + policy stale ⇒ MỘT tin gộp có cả cảnh báo CPI lẫn nhánh policy unavailable")

# policy-alert + CPI-stale (ca đối xứng yêu cầu: CPI stale)
r, out = run(pol=p2, cf="2026-10-20T15:00:00+00:00")
ok(r["status"] == "alert" and "HIỆN TẠI" in out and "Nhánh cpi KHÔNG kiểm được" in out, "15. policy-alert + CPI-stale ⇒ tin gộp")

# notify hỏng ⇒ main() non-zero, vẫn save_log
import subprocess as _sp
orig_notify, orig_argv = T._notify, sys.argv
T._notify = lambda m: False
json.dump({"vn_policy_rate": {"rows": p2, "fetched_at": FRESH}, "vn_cpi_yoy": {"rows": cpi_te, "fetched_at": FRESH}},
          open(os.environ["TE_XCHECK_FIXTURE"], "w"))
n_hist = len(json.load(open(T.LOG_PATH))["history"])
sys.argv = ["x"]
with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    rc = T.main()
ok(rc != 0 and len(json.load(open(T.LOG_PATH))["history"]) == n_hist + 1, "16. có tin cần gửi mà notified=False ⇒ main() non-zero, log vẫn lưu")
T._notify = orig_notify
# _notify thật: FileNotFoundError không được nổ ra ngoài
T._SELFCHECK = False
os.environ.pop("TE_XCHECK_NO_NOTIFY", None)
orig_path = T.NOTIFY
T.NOTIFY = os.path.join(tmp, "khong_ton_tai.sh")
with contextlib.redirect_stderr(io.StringIO()):
    got = T._notify("x")
T.NOTIFY, T._SELFCHECK = orig_path, True
ok(got is False, "17. notify_thread.sh không tồn tại (FileNotFoundError) ⇒ _notify trả False, không nổ")
# không có tin ⇒ main 0
json.dump({"vn_policy_rate": {"rows": pol_te, "fetched_at": FRESH}, "vn_cpi_yoy": {"rows": cpi_te, "fetched_at": FRESH}},
          open(os.environ["TE_XCHECK_FIXTURE"], "w"))
with contextlib.redirect_stdout(io.StringIO()):
    rc = T.main()
sys.argv = orig_argv
ok(rc == 0, "18. không có tin cần gửi ⇒ main() == 0")
# 19. ghi snapshot CPI hỏng ⇒ status partial, tin notify nêu lỗi, main() != 0
_orig_w = T.write_cpi_snapshot
def _boom(*a, **k): raise OSError("disk full (giả lập)")
T.write_cpi_snapshot = _boom
sent = []
T._notify = lambda m: (sent.append(m), True)[1]
json.dump({"vn_policy_rate": {"rows": pol_te, "fetched_at": FRESH}, "vn_cpi_yoy": {"rows": cpi_te, "fetched_at": FRESH}},
          open(os.environ["TE_XCHECK_FIXTURE"], "w"))
sys.argv = ["x"]
with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    rc = T.main()
sys.argv = orig_argv
lg = json.load(open(T.LOG_PATH))
ok(rc != 0 and lg["last"]["status"] == "partial" and sent and "disk full" in sent[0] and lg["history"][-1]["status"] == "partial",
   f"19. snapshot ghi lỗi ⇒ status partial + tin nêu lỗi + main() != 0 (rc={rc})")
T.write_cpi_snapshot = _orig_w; T._notify = orig_notify
# đưa trạng thái log cuối về unavailable cho ca 12
run(pf="2026-10-20T15:00:00+00:00", cerr="403 quota")

after = os.stat(sbv_log).st_mtime_ns if os.path.exists(sbv_log) else None
ok(before == after, "11. data/sbv_verify_log.json KHÔNG bị đụng")
lg = json.load(open(T.LOG_PATH))
ok(lg["last"]["status"] == "unavailable" and len(lg["history"]) >= 8 and os.path.dirname(T.LOG_PATH) == tmp,
   "12. log riêng ghi đúng, history tăng, ghi vào data dir tạm")
print("\nTZ env =", os.environ.get("TZ"))
print("TẤT CẢ PASS" if not FAIL else f"FAIL {len(FAIL)}: {FAIL}")
sys.exit(1 if FAIL else 0)
