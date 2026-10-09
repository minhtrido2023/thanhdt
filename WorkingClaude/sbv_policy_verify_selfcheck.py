#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck sbv_policy_verify.py — chạy hoàn toàn trong sandbox (SBV_POLICY_SELFCHECK=1: data dir
tạm, HTML giả, không mạng, không notify). Luật trọng tâm: MỌI kết cục không-verified chỉ đẩy
attempted_at, KHÔNG BAO GIỜ đẩy verified_at. Chạy thêm dưới `env -u TZ` và TZ lạ (§16/§19)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "sbv_policy_verify.py")
TODAY = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()
_n = 0


def ok(cond, msg):
    global _n
    _n += 1
    if not cond:
        print(f"FAIL #{_n}: {msg}")
        sys.exit(1)


def page(refi="4,500", red="3,000"):
    return ("<html><head><title>Lãi suất - NHNN</title></head><body><table>"
            f"<tr><td>Lãi suất tái chiết khấu</td><td>{red}%</td><td>1123/QĐ-NHNN ngày 16/06/2023</td>"
            "<td>19/03/2023</td></tr>"
            f"<tr><td>Lãi suất tái cấp vốn</td><td>{refi}%</td><td>1123/QĐ-NHNN ngày 16/06/2023</td>"
            "<td>19/03/2023</td></tr></table><script>var x='Lãi suất tái cấp vốn 9,000%';</script>"
            "</body></html>")


PAGE_404 = "<html><head><title>404 - Ngân hàng Nhà nước Việt Nam</title></head><body>x</body></html>"


def src(url, refi=4.5, red=3.0, days_ago=3, **kw):
    return dict(publisher="p", url=url, date=(TODAY - timedelta(days=days_ago)).isoformat(),
                refi=refi, rediscount=red, **kw)


class Box:
    def __init__(self):
        self.d = tempfile.mkdtemp(prefix="sbvpol_")
        self.html = os.path.join(self.d, "page.html")
        self.set_page(page())

    def set_page(self, text):
        open(self.html, "w", encoding="utf-8").write(text)

    def run(self, *args, extra_env=None):
        env = dict(os.environ, SBV_POLICY_SELFCHECK="1", SBV_POLICY_DATA_DIR=self.d,
                   SBV_POLICY_FAKE_HTML=self.html, **(extra_env or {}))
        r = subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True,
                           env=env, cwd=HERE, timeout=120)
        return r.returncode, r.stdout + r.stderr

    def verify(self, sources):
        return self.run("verify", "--sources", json.dumps(sources))

    def log(self):
        p = os.path.join(self.d, "sbv_verify_log.json")
        return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}

    def close(self):
        shutil.rmtree(self.d, ignore_errors=True)


LEGACY = {"last_verified": "2026-10-09", "rate_confirmed": 4.5, "fetch_status": "fetch_failed",
          "note": "fetch_failed_assumed_unchanged",
          "history": [{"date": "2026-06-27", "rate_confirmed": 4.5, "fetch_status": "skipped",
                       "note": "initial seed — user confirmed 4.5% stable since 2023-06-19"},
                      {"date": "2026-10-09", "rate_confirmed": 4.5, "fetch_status": "fetch_failed",
                       "note": "fetch_failed_assumed_unchanged"}]}


def t_fetch_parse():
    b = Box()
    rc, out = b.run("fetch")
    ok(rc == 0, f"fetch rc={rc}: {out}")
    j = json.loads(out.strip().splitlines()[-1])
    ok(j["refi_pct"] == 4.5 and j["rediscount_pct"] == 3.0, f"parse sai: {j}")
    ok(j["refi_decision"] == "1123/QĐ-NHNN ngày 16/06/2023", f"decision sai: {j}")
    b.set_page(PAGE_404)
    rc, out = b.run("fetch")
    ok(rc == 2 and "official_parse_failed" in out and "404" in out,
       f"trang 404 phải REFUSE kèm title thật (§29): rc={rc} {out}")
    ok(not os.path.exists(os.path.join(b.d, "sbv_verify_log.json")), "fetch không được ghi log")
    b.close()


def t_legacy_migration_and_success():
    b = Box()
    json.dump(LEGACY, open(os.path.join(b.d, "sbv_verify_log.json"), "w"))
    # thất bại đầu tiên sau di trú: verified_at = seed thật 06-27, KHÔNG phải 10-09 giả
    b.set_page(PAGE_404)
    rc, out = b.verify([src("https://vietstock.vn/a")])
    lg = b.log()
    ok(rc == 2, f"404 phải rc=2: {out}")
    ok(lg["verified_at"].startswith("2026-06-27") and lg["last_verified"] == "2026-06-27",
       f"di trú phải bỏ last_verified giả 10-09: {lg.get('verified_at')} / {lg.get('last_verified')}")
    ok(lg["attempted_at"] and lg["last_attempt"]["outcome"] == "official_parse_failed",
       f"attempt chưa ghi: {lg.get('last_attempt')}")
    ok(lg["legacy_history"][-1]["note"] == "fetch_failed_assumed_unchanged", "mất legacy_history")
    # thành công
    b.set_page(page())
    rc, out = b.verify([src("https://vietstock.vn/a", omo=4.0), src("https://vnexpress.net/b", omo=4.0)])
    lg = b.log()
    ok(rc == 0 and "VERIFIED" in out, f"verify hợp lệ phải rc=0: {out}")
    ok(lg["last_verified"] == TODAY.isoformat(), f"last_verified phải = hôm nay: {lg['last_verified']}")
    ok(lg["verified_at"] == lg["attempted_at"], "verified ⇒ verified_at == attempted_at")
    v = lg["verified"]
    ok(v["refi_pct"] == 4.5 and v["rediscount_pct"] == 3.0, f"số verified sai: {v}")
    ok(v["omo_pct"] == 4.0 and v["omo_status"] == "cross_checked", f"OMO 2 chủ khớp phải ghi: {v}")
    ok(os.path.exists(os.path.join(b.d, "sbv_policy_last_auto_sources.json")), "thiếu sidecar URL")
    good_va = lg["verified_at"]
    # URL dùng lại ⇒ từ chối, verified_at giữ nguyên
    rc, out = b.verify([src("https://www.vietstock.vn/a/")])
    lg = b.log()
    ok(rc == 2 and lg["last_attempt"]["outcome"] == "url_reused", f"URL dùng lại phải chặn: {out}")
    ok(lg["verified_at"] == good_va, "url_reused đã đẩy verified_at")
    b.close()


def t_refusals_never_advance_verified():
    cases = [
        ("source_mismatch", page(), [src("https://vietstock.vn/x", refi=4.25)]),
        ("source_mismatch", page(), [src("https://vietstock.vn/x", red=2.5)]),
        ("not_independent", page(), [src("https://dttktt.sbv.gov.vn/x")]),
        ("stale_source", page(), [src("https://vietstock.vn/x", days_ago=60)]),
        ("stale_source", page(), [src("https://vietstock.vn/x", days_ago=-2)]),
        ("bad_sources", page(), [{"publisher": "p", "url": "https://vietstock.vn/x",
                                  "date": TODAY.isoformat(), "refi": 4.5}]),
        ("bad_sources", page(), []),
        ("rate_change_detected", page(refi="5,000"), [src("https://vietstock.vn/x", refi=5.0)]),
        ("official_parse_failed", page().replace("4,500", "4,500%</td></tr><tr><td>Lãi suất "
                                                  "tái cấp vốn</td><td>4,750"), [src("https://vietstock.vn/x")]),
    ]
    for outcome, html_text, sources in cases:
        b = Box()
        seed = dict(json.loads(json.dumps(LEGACY)))
        json.dump(seed, open(os.path.join(b.d, "sbv_verify_log.json"), "w"))
        b.set_page(html_text)
        rc, out = b.verify(sources)
        lg = b.log()
        ok(rc == 2, f"{outcome}: phải rc=2, được {rc}: {out}")
        ok(lg["last_attempt"]["outcome"] == outcome,
           f"{outcome}: outcome thực = {lg['last_attempt']['outcome']}: {out}")
        ok(lg["verified_at"].startswith("2026-06-27") and lg["last_verified"] == "2026-06-27",
           f"{outcome}: đã đẩy verified_at {lg['verified_at']}")
        ok(lg.get("verified", {}).get("method") == "legacy_check_sbv_weekly",
           f"{outcome}: đã ghi số verified mới dù bị từ chối")
        if outcome == "rate_change_detected":
            ok("🔴" in out and "KHÔNG tự sửa" in out, f"đổi lãi phải cảnh báo 🔴: {out}")
        b.close()


def t_finalize():
    b = Box()
    json.dump(LEGACY, open(os.path.join(b.d, "sbv_verify_log.json"), "w"))
    start = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rc, out = b.run("finalize", "--run-start", start, "--dispatch-rc", "0")
    lg = b.log()
    ok(rc == 0, f"finalize rc={rc}: {out}")
    ok(lg["last_attempt"]["outcome"] == "no_verify_call", f"không gọi verify phải ghi attempt: {lg}")
    ok(lg["verified_at"].startswith("2026-06-27"), "finalize đẩy verified_at")
    ok("[no-notify] ⚠️" in out and "STALE" in out, f"verified_at cũ phải nhắc STALE 1 dòng: {out}")
    ok(out.count("[no-notify]") == 1, f"chỉ 1 dòng nhắc: {out}")
    # verify thành công trong lượt ⇒ finalize im lặng, không ghi đè attempt
    rc, _ = b.verify([src("https://vietstock.vn/z")])
    ok(rc == 0, "verify lượt 2 phải OK")
    rc, out = b.run("finalize", "--run-start", start)
    ok(rc == 0 and "[no-notify]" not in out, f"đã verified + tươi ⇒ không nhắc: {out}")
    ok(b.log()["last_attempt"]["outcome"] == "verified", "finalize ghi đè attempt verified")
    b.close()


def t_env_override_needs_selfcheck_flag():
    env = {k: v for k, v in os.environ.items() if k != "SBV_POLICY_SELFCHECK"}
    env["SBV_POLICY_DATA_DIR"] = "/tmp/should_be_ignored"
    r = subprocess.run([sys.executable, "-c", "import sbv_policy_verify as m; print(m.LOG_PATH)"],
                       capture_output=True, text=True, env=env, cwd=HERE)
    ok(r.stdout.strip() == os.path.join(HERE, "data", "sbv_verify_log.json"),
       f"SBV_POLICY_DATA_DIR không có cờ selfcheck phải bị bỏ qua: {r.stdout}{r.stderr}")


if __name__ == "__main__":
    for t in (t_fetch_parse, t_legacy_migration_and_success, t_refusals_never_advance_verified,
              t_finalize, t_env_override_needs_selfcheck_flag):
        t()
    print(f"PASS {_n} assertions (TZ={os.environ.get('TZ', '<unset>')})")
