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
        ("stale_source", page(), [src("https://vietstock.vn/x", days_ago=130)]),
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


# ───────── official_unchanged (user duyệt 2026-10-12) — đồng hồ GHIM, không phụ thuộc ngày chạy ─────────
PIN = datetime(2026, 10, 12, 0, 30, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))  # sát nửa đêm ICT (§16)
PIN_ENV = {"SBV_POLICY_FAKE_NOW": PIN.isoformat()}
PIN_START = (PIN - timedelta(minutes=1)).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
V_OK = {"refi_pct": 4.5, "rediscount_pct": 3.0, "refi_decision": "1123/QĐ-NHNN ngày 16/06/2023",
        "independent_owners": ["eastasiaforum.org"], "note": "giữ nguyên từng byte"}
FROZEN = ("verified_at", "last_verified", "verified")


def _seed(b, age_days=30, verified=V_OK, outcome=None, va="auto", notified=None):
    """Log v2 với verified_at = PIN - age_days. outcome=None ⇒ chưa ai gọi verify trong lượt
    (finalize tự ghi no_verify_call/dispatch_queued); khác None ⇒ attempt của lượt này."""
    vat = PIN - timedelta(days=age_days)
    d = {"schema": "sbv_policy_verify_v2",
         "verified_at": vat.isoformat(timespec="seconds") if va == "auto" else va,
         "attempted_at": None, "last_verified": vat.date().isoformat(), "verified": verified,
         "last_attempt": None, "history": []}
    if outcome:
        at = PIN.isoformat(timespec="seconds")
        d["attempted_at"] = at
        d["last_attempt"] = {"at": at, "outcome": outcome, "detail": f"seed {outcome}", "notified": notified}
        d["history"] = [{"at": at, "outcome": outcome, "detail": f"seed {outcome}"}]
    json.dump(d, open(os.path.join(b.d, "sbv_verify_log.json"), "w", encoding="utf-8"), ensure_ascii=False)
    return json.dumps({k: d[k] for k in FROZEN}, ensure_ascii=False)


def _fin(b, rc_arg="0"):
    rc, out = b.run("finalize", "--run-start", PIN_START, "--dispatch-rc", rc_arg, extra_env=PIN_ENV)
    lg = b.log()
    return rc, out, lg, json.dumps({k: lg.get(k) for k in FROZEN}, ensure_ascii=False)


def _must_nag(tag, b, frozen, want_outcome, needle, tu_doc=True):
    rc, out, lg, after = _fin(b)
    ok(rc == 0 and out.count("[no-notify] ⚠️") == 1, f"{tag}: phải nhắc đúng 1 dòng: rc={rc} {out}")
    ok(lg["last_attempt"]["outcome"] == want_outcome, f"{tag}: outcome phải giữ {want_outcome}: {lg['last_attempt']}")
    ok("official_reconfirmed_at" not in lg, f"{tag}: không được ghi official_reconfirmed_at")
    ok(after == frozen, f"{tag}: verified_at/last_verified/verified bị đổi")
    ok(("tự đọc trang NHNN" in out) is tu_doc, f"{tag}: 'tự đọc trang NHNN' phải {tu_doc}: {out}")
    ok(needle in lg["last_attempt"]["detail"] and (not tu_doc or needle in out),
       f"{tag}: detail/dòng nhắc thiếu lý do thật {needle!r}: {lg['last_attempt']['detail']} // {out}")
    ok("🔴" not in out, f"{tag}: finalize không được tự phát 🔴: {out}")
    return lg


def t_official_unchanged():
    # 1) cả ba outcome trong lớp ⇒ im, ghi official_unchanged; tuổi 30 > STALE_DAYS vẫn im (mục 2)
    for outcome in (None, "url_reused", "stale_source"):
        b = Box()
        frozen = _seed(b, age_days=30, outcome=outcome)
        rc, out, lg, after = _fin(b)
        tag = f"official_unchanged[{outcome or 'no_verify_call'}]"
        ok(rc == 0 and "[no-notify]" not in out, f"{tag}: phải KHÔNG nhắc: rc={rc} {out}")
        la = lg["last_attempt"]
        ok(la["outcome"] == "official_unchanged", f"{tag}: outcome={la['outcome']}")
        ok("refi=4.5%" in la["detail"] and "rediscount=3.0%" in la["detail"] and "30/120" in la["detail"]
           and (outcome or "no_verify_call") in la["detail"], f"{tag}: detail thiếu số/tuổi/outcome gốc: {la['detail']}")
        ok(lg.get("official_reconfirmed_at") == lg["attempted_at"] == PIN.isoformat(timespec="seconds"),
           f"{tag}: official_reconfirmed_at sai: {lg.get('official_reconfirmed_at')} vs {lg['attempted_at']}")
        ok(after == frozen, f"{tag}: verified_at/last_verified/verified KHÔNG byte-identical")
        ok([h["outcome"] for h in lg["history"]] == [outcome or "no_verify_call", "official_unchanged"],
           f"{tag}: history sai: {lg['history']}")
        # finalize chạy lại cùng lượt: vẫn im, không ghi thêm
        rc, out, lg2, after = _fin(b)
        ok(rc == 0 and "[no-notify]" not in out and len(lg2["history"]) == 2 and after == frozen,
           f"{tag}: chạy lại phải im + không ghi thêm: {out} {lg2['history']}")
        b.close()
    # 2) (a) sai — tuổi 3 ngày (không STALE) ⇒ dòng nhắc chỉ có thể đến từ điều kiện (a)
    for tag, v, needle in (
            ("a:refi", dict(V_OK, refi_pct=4.25), "≠ verified refi=4.25%"),
            ("a:rediscount", dict(V_OK, rediscount_pct=3.5), "≠ verified refi=4.5% rediscount=3.5%"),
            ("a:thiếu rediscount", {"refi_pct": 4.5, "method": "legacy_check_sbv_weekly"}, "rediscount_pct=None"),
            ("a:verified None", None, "refi_pct=None")):
        b = Box()
        frozen = _seed(b, age_days=3, verified=v)
        lg = _must_nag(tag, b, frozen, "no_verify_call", needle)
        ok("NHNN refi=4.5% rediscount=3.0%" in lg["last_attempt"]["detail"], f"{tag}: thiếu số NHNN đọc được")
        b.close()
    # 3) (b) sai — NHNN + verified{} cùng 5,0% nhưng SBV_REFI_EVENTS 4,5%: nhắc kèm số, KHÔNG tự phát 🔴
    b = Box()
    b.set_page(page(refi="5,000"))
    frozen = _seed(b, age_days=3, verified=dict(V_OK, refi_pct=5.0), outcome="url_reused")
    _must_nag("b:SBV_REFI_EVENTS", b, frozen, "url_reused", "refi=5.0% rediscount=3.0% ≠ SBV_REFI_EVENTS 4.5%")
    b.close()
    # 4) (c) biên tuổi: đúng 120 ⇒ im; 121 ⇒ nhắc; verified_at thiếu / ở tương lai ⇒ nhắc
    b = Box()
    frozen = _seed(b, age_days=120)
    rc, out, lg, after = _fin(b)
    ok(rc == 0 and "[no-notify]" not in out and lg["last_attempt"]["outcome"] == "official_unchanged"
       and "120/120" in lg["last_attempt"]["detail"] and after == frozen, f"c:120 phải im: {out} {lg['last_attempt']}")
    b.close()
    for tag, kw, needle in (("c:121", dict(age_days=121), "tuổi 121 ngày ngoài 0..120"),
                            ("c:tương lai", dict(age_days=-2), "tuổi -2 ngày ngoài 0..120"),
                            ("c:verified_at None", dict(va=None), "tuổi None ngày")):
        b = Box()
        frozen = _seed(b, **kw)
        _must_nag(tag, b, frozen, "no_verify_call", needle)
        b.close()
    # 5) fetch/parse lỗi ⇒ nhắc như cũ, trích lỗi thật (§29)
    b = Box()
    frozen = _seed(b, age_days=3, outcome="stale_source")
    b.set_page(PAGE_404)
    _must_nag("parse 404", b, frozen, "stale_source", "official_parse_failed")
    ok("404" in b.log()["last_attempt"]["detail"], "parse 404: thiếu title thật")
    b.close()
    b = Box()
    frozen = _seed(b, age_days=3)
    os.remove(b.html)
    lg = _must_nag("fetch lỗi", b, frozen, "no_verify_call", "FileNotFoundError")
    # chạy lại: lý do GHI ĐÈ phần đuôi, không nối dài; vẫn đúng 1 dòng nhắc; trang về lại ⇒ im
    _must_nag("fetch lỗi (lần 2)", b, frozen, "no_verify_call", "FileNotFoundError")
    lg = b.log()
    ok(lg["last_attempt"]["detail"].count("NHNN tự đọc") == 1 and len(lg["history"]) == 1
       and lg["history"][-1]["detail"] == lg["last_attempt"]["detail"][:300], f"chạy lại nối dài detail: {lg}")
    b.set_page(page())
    rc, out, lg, after = _fin(b)
    ok("[no-notify]" not in out and lg["last_attempt"]["outcome"] == "official_unchanged" and after == frozen,
       f"trang đọc lại được ⇒ official_unchanged: {out}")
    b.close()
    # 6) outcome NGOÀI lớp ⇒ hành vi cũ, không tự đọc NHNN (trang + verified{} + tuổi đều đạt)
    for outcome in ("source_mismatch", "bad_sources", "not_independent", "official_fetch_failed",
                    "official_parse_failed", "recorded_refi_unreadable", "internal_error"):
        b = Box()
        frozen = _seed(b, age_days=3, outcome=outcome)
        _must_nag(f"ngoài lớp[{outcome}]", b, frozen, outcome, f"seed {outcome}", tu_doc=False)
        ok(b.log()["last_attempt"]["detail"] == f"seed {outcome}", f"{outcome}: detail bị sửa")
        b.close()
    b = Box()  # rate_change_detected CHƯA notified ⇒ gửi lại 🔴 như cũ
    frozen = _seed(b, age_days=3, outcome="rate_change_detected", notified=False)
    rc, out, lg, after = _fin(b)
    ok(rc == 0 and "[no-notify] seed rate_change_detected" in out and "⚠️" not in out
       and lg["last_attempt"]["outcome"] == "rate_change_detected" and after == frozen
       and "official_reconfirmed_at" not in lg, f"rate_change chưa notified phải gửi lại nguyên văn: {out}")
    b.close()
    # dispatch_queued / verified: ngưỡng STALE_DAYS=21 GIỮ NGUYÊN (30 ngày ⇒ nhắc STALE, 3 ngày ⇒ im)
    for age, nag in ((30, True), (3, False)):
        for outcome, rc_arg in (("dispatch_queued", "5"), ("verified", "0")):
            b = Box()
            frozen = _seed(b, age_days=age, outcome=None if outcome == "dispatch_queued" else outcome)
            rc, out, lg, after = b.run("finalize", "--run-start", PIN_START, "--dispatch-rc", rc_arg,
                                       extra_env=PIN_ENV) + (None, None)
            lg = b.log()
            ok(rc == 0 and lg["last_attempt"]["outcome"] == outcome and "official_reconfirmed_at" not in lg
               and (("QUÁ 21 ngày — STALE" in out) is nag) and (out.count("[no-notify]") == int(nag)),
               f"{outcome} tuổi {age}: nhắc STALE phải = {nag}: {out}")
            b.close()


def _patch(b, fn):
    path = os.path.join(b.d, "sbv_verify_log.json")
    d = json.load(open(path, encoding="utf-8"))
    fn(d)
    json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False)


def _hist(outcomes, at_override=None):
    """fn cho _patch: history = các attempt của lượt (cách PIN vài phút), last_attempt = mục cuối."""
    def fn(d):
        hs = []
        for i, o in enumerate(outcomes):
            at = at_override or (PIN - timedelta(seconds=10 - i)).isoformat(timespec="seconds")
            hs.append({"at": at, "outcome": o, "detail": f"seed {o} #{i}"})
        d["history"] = hs
        d["last_attempt"] = dict(hs[-1], notified=None)
        d["attempted_at"] = hs[-1]["at"]
    return fn


def src_pin(url, days_ago=3, **kw):  # ngày theo đồng hồ GHIM, không theo ngày chạy
    return dict(publisher="p", url=url, date=(PIN.date() - timedelta(days=days_ago)).isoformat(),
                **{**dict(refi=4.5, rediscount=3.0), **kw})


def t_round2():
    # B1: attempt cùng lượt phải tới người đứng TRƯỚC attempt cuối vô hại
    for veto in ("source_mismatch", "internal_error", "rate_change_detected"):
        for last in ("stale_source", "url_reused"):
            b = Box()
            frozen = _seed(b, age_days=3)
            _patch(b, _hist([veto, last]))
            rc, out, lg, after = _fin(b)
            ok(rc == 0 and out.count("[no-notify] ⚠️") == 1 and f"({veto}: seed {veto}" in out,
               f"B1[{veto}→{last}]: phải nhắc đúng 1 dòng, trích detail CỦA {veto}: rc={rc} {out}")
            ok("official_reconfirmed_at" not in lg and lg["last_attempt"]["outcome"] == last
               and after == frozen and [h["outcome"] for h in lg["history"]] == [veto, last],
               f"B1[{veto}→{last}]: không được ghi official_unchanged/đổi log: {lg['history']}")
            b.close()
    # không veto: bad_sources/not_independent (agent trượt quoting rồi gọi lại) và attempt TUẦN TRƯỚC
    for tag, fn in (("bad_sources", _hist(["bad_sources", "stale_source"])),
                    ("not_independent", _hist(["not_independent", "url_reused"])),
                    ("mismatch tuần trước", _hist(["source_mismatch", "stale_source"],
                                                  at_override=(PIN - timedelta(days=7)).isoformat(timespec="seconds")))):
        b = Box()
        frozen = _seed(b, age_days=3)
        _patch(b, fn)
        rc, out, lg, after = _fin(b)
        ok(rc == 0 and "[no-notify]" not in out and lg["last_attempt"]["outcome"] == "official_unchanged"
           and after == frozen, f"B1 không-veto[{tag}] phải im + official_unchanged: {out} {lg['last_attempt']}")
        b.close()
    # B1 + B1b đầu-cuối qua lệnh verify thật (đồng hồ ghim): mismatch rồi stale ⇒ finalize PHẢI nhắc
    b = Box()
    frozen = _seed(b, age_days=3)
    rc, _ = b.run("verify", "--sources", json.dumps([src_pin("https://vietstock.vn/m", refi=4.25)]), extra_env=PIN_ENV)
    rc2, _ = b.run("verify", "--sources", json.dumps([src_pin("https://vnexpress.net/o", days_ago=130)]), extra_env=PIN_ENV)
    ok(rc == 2 and rc2 == 2 and [h["outcome"] for h in b.log()["history"]] == ["source_mismatch", "stale_source"],
       f"B1 e2e: history sai {b.log()['history']}")
    rc, out, lg, after = _fin(b)
    ok(out.count("[no-notify] ⚠️") == 1 and "(source_mismatch:" in out and "official_reconfirmed_at" not in lg
       and after == frozen, f"B1 e2e: phải nhắc source_mismatch: {out}")
    b.close()
    # B1b: nguồn quá hạn KHÔNG che nguồn còn hạn lệch số — cả 2 thứ tự; không lệch ⇒ stale_source
    stale = src_pin("https://vnexpress.net/old", days_ago=200)
    bad = src_pin("https://vietstock.vn/new", refi=4.25)
    good = src_pin("https://cafef.vn/new")
    for tag, lst, want in (("stale→bad", [stale, bad], "source_mismatch"), ("bad→stale", [bad, stale], "source_mismatch"),
                           ("stale→good", [stale, good], "stale_source"), ("good→stale", [good, stale], "stale_source")):
        b = Box()
        _seed(b, age_days=3)
        rc, out = b.run("verify", "--sources", json.dumps(lst), extra_env=PIN_ENV)
        lg = b.log()
        ok(rc == 2 and lg["last_attempt"]["outcome"] == want, f"B1b[{tag}]: phải {want}: {out}")
        ok(lg["verified_at"] == (PIN - timedelta(days=3)).isoformat(timespec="seconds"), f"B1b[{tag}] đẩy verified_at")
        b.close()
    # B2(i): official_unchanged của TUẦN TRƯỚC (at < run-start) không được che lượt này
    wk = (PIN - timedelta(days=7)).isoformat(timespec="seconds")
    b = Box()
    frozen = _seed(b, age_days=3, verified=dict(V_OK, refi_pct=4.25))  # trang đổi so với verified{}
    _patch(b, _hist(["official_unchanged"], at_override=wk))
    lg = _must_nag("leftover:trang đổi", b, frozen, "no_verify_call", "≠ verified refi=4.25%")
    b.close()
    b = Box()
    frozen = _seed(b, age_days=3)
    _patch(b, _hist(["official_unchanged"], at_override=wk))
    rc, out, lg, after = _fin(b)
    ok([h["outcome"] for h in lg["history"]] == ["official_unchanged", "no_verify_call", "official_unchanged"]
       and "[no-notify]" not in out and lg["official_reconfirmed_at"] == PIN.isoformat(timespec="seconds")
       and after == frozen, f"leftover:trang y nguyên: phải có no_verify_call + official_unchanged MỚI: {lg['history']} {out}")
    b.close()
    # B2(ii): NaN trong verified{} ⇒ nhắc (phép so `>` sẽ cho qua)
    nan = float("nan")
    b = Box()
    frozen = _seed(b, age_days=3, verified=dict(V_OK, refi_pct=nan, rediscount_pct=nan))
    _must_nag("NaN verified", b, frozen, "no_verify_call", "≠ verified refi=nan%")
    b.close()
    # N9: verified{} không phải object ⇒ nhắc kèm lý do thật, không AttributeError
    for tag, v in (("list", [1, 2]), ("str", "4.5")):
        b = Box()
        frozen = _seed(b, age_days=3, verified=v)
        _must_nag(f"verified={tag}", b, frozen, "no_verify_call", "không phải object")
        b.close()
    # B2(iv): verified_at tuổi đúng 0 ngày ⇒ im (biên dưới của 0..120)
    b = Box()
    frozen = _seed(b, age_days=0)
    rc, out, lg, after = _fin(b)
    ok(rc == 0 and "[no-notify]" not in out and lg["last_attempt"]["outcome"] == "official_unchanged"
       and "0/120" in lg["last_attempt"]["detail"] and after == frozen, f"tuổi 0 phải im: {out} {lg['last_attempt']}")
    b.close()
    # N1: verify thành công chen giữa lúc finalize đọc mạng ⇒ verified_at KHÔNG lùi
    b = Box()
    _seed(b, age_days=30, outcome="stale_source")
    new_va = PIN.isoformat(timespec="seconds")
    raced = {"schema": "sbv_policy_verify_v2", "verified_at": new_va, "attempted_at": new_va,
             "last_verified": PIN.date().isoformat(), "verified": dict(V_OK, note="verify chen giữa"),
             "last_attempt": {"at": new_va, "outcome": "verified", "detail": "raced", "notified": None},
             "history": [{"at": new_va, "outcome": "verified", "detail": "raced"}]}
    rp = os.path.join(b.d, "raced.json")
    json.dump(raced, open(rp, "w", encoding="utf-8"), ensure_ascii=False)
    rc, out = b.run("finalize", "--run-start", PIN_START, "--dispatch-rc", "0",
                    extra_env=dict(PIN_ENV, SBV_POLICY_SIM_RACE_LOG=rp))
    lg = b.log()
    ok(rc == 0 and lg["verified_at"] == new_va and lg["verified"]["note"] == "verify chen giữa"
       and lg["last_attempt"]["outcome"] == "verified" and "[no-notify]" not in out
       and "official_reconfirmed_at" not in lg, f"N1: verified_at bị lùi/ghi đè: {lg} // {out}")
    b.close()


def t_fake_now_needs_selfcheck():
    env = {k: v for k, v in os.environ.items() if not k.startswith("SBV_POLICY_")}
    env.update(SBV_POLICY_SELFCHECK="1", SBV_POLICY_FAKE_NOW="2001-01-01T00:00:00+07:00")
    r = subprocess.run([sys.executable, "-c", "import sbv_policy_verify as m; print(m._now().year)"],
                       capture_output=True, text=True, env=env, cwd=HERE)
    ok(r.stdout.strip() != "2001", f"FAKE_NOW không kèm data dir tạm phải bị bỏ qua: {r.stdout}{r.stderr}")


def t_env_override_needs_selfcheck_flag():
    env = {k: v for k, v in os.environ.items() if k != "SBV_POLICY_SELFCHECK"}
    env["SBV_POLICY_DATA_DIR"] = "/tmp/should_be_ignored"
    r = subprocess.run([sys.executable, "-c", "import sbv_policy_verify as m; print(m.LOG_PATH)"],
                       capture_output=True, text=True, env=env, cwd=HERE)
    ok(r.stdout.strip() == os.path.join(HERE, "data", "sbv_verify_log.json"),
       f"SBV_POLICY_DATA_DIR không có cờ selfcheck phải bị bỏ qua: {r.stdout}{r.stderr}")


def t_review_r1():
    """Các lỗ arch-review r1 bắt được: NaN/inf, báo NHNN chủ quản, 🔴 không tới người, rc=5, log hỏng."""
    bad = [("bad_sources", '[{"publisher":"p","url":"https://vietstock.vn/n1","date":"%s","refi":NaN,"rediscount":3.0}]'),
           ("bad_sources", '[{"publisher":"p","url":"https://vietstock.vn/n1","date":"%s","refi":4.5,"rediscount":"nan"}]'),
           ("bad_sources", '[{"publisher":"p","url":"https://vietstock.vn/n1","date":"%s","refi":"inf","rediscount":3.0}]'),
           ("not_independent", json.dumps([src("https://thoibaonganhang.vn/x")]).replace(TODAY.isoformat(), "%s")),
           ("not_independent", json.dumps([src("https://tapchinganhang.gov.vn/x")]).replace(TODAY.isoformat(), "%s"))]
    for outcome, raw in bad:
        b = Box()
        json.dump(LEGACY, open(os.path.join(b.d, "sbv_verify_log.json"), "w"))
        raw = raw.replace("%s", (TODAY - timedelta(days=3)).isoformat()) if "%s" in raw else raw
        rc, out = b.run("verify", "--sources", raw)
        lg = b.log()
        ok(rc == 2 and lg["last_attempt"]["outcome"] == outcome, f"{outcome}: rc={rc} {out}")
        ok(lg["verified_at"].startswith("2026-06-27"), f"{outcome}: đẩy verified_at")
        b.close()
    # 🔴 không tới người ⇒ finalize gửi lại; tới rồi ⇒ finalize im
    for fail, expect_resend in ((True, True), (False, False)):
        b = Box()
        b.set_page(page(refi="5,000"))
        env = {"SBV_POLICY_SIM_NOTIFY_FAIL": "1"} if fail else {}
        start = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        b.run("verify", "--sources", json.dumps([src("https://vietstock.vn/r", refi=5.0)]), extra_env=env)
        ok(b.log()["last_attempt"]["notified"] is (not fail), f"notified phải = {not fail}")
        rc, out = b.run("finalize", "--run-start", start)
        ok(("🔴" in out) is expect_resend, f"resend={expect_resend} sai: {out}")
        b.close()
    # dispatch rc=5 (xếp hàng usage-limit) với verified còn tươi ⇒ ghi attempt, KHÔNG nhắc
    b = Box()
    b.verify([src("https://vietstock.vn/q")])
    import time; time.sleep(1.1)
    start = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rc, out = b.run("finalize", "--run-start", start, "--dispatch-rc", "5")
    ok(rc == 0 and "[no-notify]" not in out and b.log()["last_attempt"]["outcome"] == "dispatch_queued",
       f"rc=5 phải ghi dispatch_queued, không nhắc: {out}")
    b.close()
    # log hỏng ⇒ rc≠0, KHÔNG ghi đè (giữ bằng chứng), không coi là rỗng
    b = Box()
    lp = os.path.join(b.d, "sbv_verify_log.json")
    open(lp, "w").write("{not json")
    for args in (("verify", "--sources", json.dumps([src("https://vietstock.vn/c")])),
                 ("finalize", "--run-start", "2026-01-01T00:00:00Z")):
        rc, out = b.run(*args)
        ok(rc not in (0, 2) and open(lp).read() == "{not json", f"log hỏng {args[0]}: rc={rc} {out[-200:]}")
    b.close()


def t_flag_alone_does_not_enable_fakes():
    for extra in ({}, {"SBV_POLICY_DATA_DIR": os.path.join(HERE, "data")}):
        env = {k: v for k, v in os.environ.items() if not k.startswith("SBV_POLICY_")}
        env.update(SBV_POLICY_SELFCHECK="1", SBV_POLICY_FAKE_HTML="/nonexistent", **extra)
        r = subprocess.run([sys.executable, "-c", "import sbv_policy_verify as m; print(m._SELFCHECK, m.LOG_PATH)"],
                           capture_output=True, text=True, env=env, cwd=HERE)
        ok(r.stdout.split()[0] == "False" and r.stdout.split()[1] == os.path.join(HERE, "data", "sbv_verify_log.json"),
           f"cờ selfcheck không kèm data dir tạm phải KHÔNG bật fake: {extra} -> {r.stdout}{r.stderr}")


def t_wrapper_block():
    """Khối finalize cuối refresh_deposit_cctg_weekly.sh: đúng lệnh, dry-run chỉ fetch, notify khi
    SBV_RC≠0 (không ở dry-run), exit code gộp TREND_RC+SBV_RC."""
    text = open(os.path.join(HERE, "refresh_deposit_cctg_weekly.sh"), encoding="utf-8").read()
    i = text.index("# --- SBV policy rates: finalize ALWAYS runs")
    block = text[i:]
    for dry, sbv_rc, trend_rc, want_exit, want_notify in (
            (0, 0, 0, 0, False), (0, 1, 0, 1, True), (0, 0, 1, 1, False), (1, 0, 0, 0, False), (1, 2, 0, 1, False)):
        d = tempfile.mkdtemp(prefix="sbvwrap_")
        os.makedirs(os.path.join(d, "mike", "bin"))
        fakepy = os.path.join(d, "fakepy")
        open(fakepy, "w").write(f'#!/bin/bash\necho "ARGS $*" >> {d}/calls\nexit {sbv_rc}\n')
        nt = os.path.join(d, "mike", "bin", "notify_thread.sh")
        open(nt, "w").write(f'#!/bin/bash\necho "NOTIFY $2" >> {d}/calls\n')
        os.chmod(fakepy, 0o755); os.chmod(nt, 0o755)
        pre = (f'DRY_RUN={dry}; PY={fakepy}; LOG={d}/log; RUN_START_UTC=2026-10-12T01:05:00Z; '
               f'DISPATCH_RC=0; TREND_RC={trend_rc}; WORKDIR_8L={d}; TODAY=2026-10-12; CONFIRMED=yes\n')
        r = subprocess.run(["bash", "-c", pre + block], capture_output=True, text=True, cwd=d)
        calls = open(os.path.join(d, "calls")).read() if os.path.exists(os.path.join(d, "calls")) else ""
        tag = f"dry={dry} sbv={sbv_rc} trend={trend_rc}"
        ok(r.returncode == want_exit, f"wrapper {tag}: exit {r.returncode} != {want_exit} {r.stderr}")
        want_args = "ARGS sbv_policy_verify.py fetch" if dry else \
            "ARGS sbv_policy_verify.py finalize --run-start 2026-10-12T01:05:00Z --dispatch-rc 0"
        ok(want_args in calls, f"wrapper {tag}: lệnh sai: {calls}")
        ok(("NOTIFY trading_daily" in calls) is want_notify, f"wrapper {tag}: notify sai: {calls}")
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    for t in (t_fetch_parse, t_legacy_migration_and_success, t_refusals_never_advance_verified,
              t_finalize, t_env_override_needs_selfcheck_flag, t_review_r1,
              t_flag_alone_does_not_enable_fakes, t_wrapper_block, t_official_unchanged,
              t_round2, t_fake_now_needs_selfcheck):
        t()
    print(f"PASS {_n} assertions (TZ={os.environ.get('TZ', '<unset>')})")
