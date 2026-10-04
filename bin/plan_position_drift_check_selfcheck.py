#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho plan_position_drift_check.py (+ khối nhúng trong send_plan_report.sh).

Mọi ghi đều vào thư mục tạm (MIKE_DRIFT_SELFCHECK=1 + override; script TỪ CHỐI nếu state/
append_event trỏ production). Replay đọc dnse_raw THẬT ở chế độ chỉ-đọc (--no-state/--no-bus).

  python3 bin/plan_position_drift_check_selfcheck.py              # chạy hết
  python3 bin/plan_position_drift_check_selfcheck.py --mutations  # + đột biến: mỗi đột biến phải
        # bị giết bởi ÍT NHẤT 1 assertion CÓ TÊN (in tên assertion giết nó)
Chạy dưới python3 và $DNA_PYEXE × TZ {Asia/Ho_Chi_Minh, unset, America/New_York}.
"""
import datetime as dt
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TARGET = os.environ.get("DRIFT_SC_TARGET") or os.path.join(HERE, "plan_position_drift_check.py")
SEND_PLAN = os.environ.get("DRIFT_SC_SENDPLAN") or os.path.join(HERE, "send_plan_report.sh")
SP, ZP = "0002023347", "0001743768"
D = "2026-10-05"            # thứ Hai, ngày giao dịch
FAILS, PASSED = [], []


def check(name, cond, detail=""):
    (PASSED if cond else FAILS).append(name)
    if not cond:
        print(f"  ✗ {name} {detail}")


# ── sandbox ─────────────────────────────────────────────────────────────────────────────────
SB = tempfile.mkdtemp(prefix="driftsc_")
EXEC = os.path.join(SB, "exec")
PLANS = os.path.join(SB, "plans")
STATE = os.path.join(SB, "state")
BUSLOG = os.path.join(SB, "bus.jsonl")
FAKE_BUS = os.path.join(SB, "append_event.sh")
for d_ in (EXEC, PLANS, STATE):
    os.makedirs(d_)
with open(FAKE_BUS, "w") as f:
    f.write('#!/usr/bin/env bash\n'
            '[ -f "$(dirname "$0")/bus_fail" ] && { echo "bus down" >&2; exit 1; }\n'
            'python3 -c \'import json,sys; print(json.dumps(sys.argv[1:]))\' "$@" >> "' + BUSLOG + '"\n')
os.chmod(FAKE_BUS, 0o755)
os.environ.update({"MIKE_DRIFT_SELFCHECK": "1", "MIKE_DRIFT_EXEC_DIR": EXEC,
                   "MIKE_DRIFT_PLAN_DIR": PLANS, "MIKE_DRIFT_STATE_DIR": STATE,
                   "MIKE_DRIFT_APPEND_EVENT": FAKE_BUS})

spec = importlib.util.spec_from_file_location("drift_mod", TARGET)
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


def z(ict_hms, day=D):
    """giờ ICT → modifiedDate UTC 'Z' như DNSE trả (kèm phần lẻ 9 chữ số như thật)."""
    t = dt.datetime.fromisoformat(f"{day}T{ict_hms}") - dt.timedelta(hours=7)
    return t.strftime("%Y-%m-%dT%H:%M:%S") + ".123456789Z"


def row(sym, qty, mp, mod, pkg=1841, status="OPEN"):
    return {"symbol": sym, "openQuantity": qty, "marketPrice": mp, "modifiedDate": mod,
            "loanPackageId": pkg, "status": status, "tradeQuantity": qty}


def rec(ts, acct_no, label, kind, payload):
    return {"ts": f"{D}T{ts}", "kind": kind, "account_no": acct_no, "account_label": label,
            "payload": payload}


def write_raw(recs, day=D):
    with open(os.path.join(EXEC, f"dnse_raw_{day}.jsonl"), "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")


def reset():
    for d_ in (EXEC, STATE):
        shutil.rmtree(d_)
        os.makedirs(d_)
    for p in (BUSLOG, os.path.join(SB, "bus_fail")):
        if os.path.exists(p):
            os.remove(p)
    for f in os.listdir(PLANS):
        os.remove(os.path.join(PLANS, f))


def bus_calls():
    if not os.path.exists(BUSLOG):
        return []
    return [json.loads(x) for x in open(BUSLOG)]


FRESH = z("18:55:00")       # sau batch cuối ngày hôm nay
STALE = z("11:40:00", "2026-10-02")   # batch phiên trước


def live(rows, orders=None, raise_=None):
    def _f(acct_no, label):
        if raise_:
            raise raise_
        return {"positions": rows}, orders
    return _f


def run(acct="SpaceX", acct_no=SP, sim_at=None, now=None):
    return M.run_check(acct, acct_no, D, M.paths(), sim_at=sim_at,
                       now=now or dt.datetime(2026, 10, 5, 20, 50, 0))


def items(res):
    return {i["ticker"]: i for i in res["items"]}


# ── 1. chỉ KL đổi (ISS kiểu VPB/TPB), sau lần đọc đầu của plan ─────────────────────────────
def t_qty_only():
    reset()
    write_raw([rec("19:03:01", SP, "SpaceX", "positions",
                   {"positions": [row("VPB", 1100, 22100, FRESH), row("HPG", 500, 21700, FRESH)]})])
    M.live_read = live([row("VPB", 1386, 22100, z("20:15:00")), row("HPG", 500, 21700, FRESH)], [])
    r = run()
    it = items(r)
    check("qty_only.status_DRIFT", r["status"] == "DRIFT", r)
    check("qty_only.only_VPB", set(it) == {"VPB"}, list(it))
    v = it.get("VPB", {})
    check("qty_only.counts", (v.get("qty_before"), v.get("qty_after")) == (1100, 1386), v)
    check("qty_only.ratio", v.get("ratio") == 1.26, v.get("ratio"))
    check("qty_only.kind_SAU_PLAN", v.get("kind") == "SAU_PLAN", v.get("kind"))
    check("qty_only.px_not_flagged", v.get("px_flag") is False, v)
    txt = "\n".join(M.render(r))
    check("qty_only.render_header", "VỊ THẾ ĐỔI SAU KHI LẬP PLAN" in txt, txt)
    check("qty_only.render_counts", "1.100→1.386" in txt and "0002023347" in txt, txt)


# ── 2. chỉ giá đổi (cả 2 bản đã qua batch) ──────────────────────────────────────────────────
def t_price_only():
    reset()
    write_raw([rec("19:05:00", SP, "SpaceX", "positions",
                   {"positions": [row("HPG", 1000, 21700, FRESH), row("FPT", 300, 100000, FRESH)]})])
    M.live_read = live([row("HPG", 1000, 19000, z("20:15:00")),
                        row("FPT", 300, 100300, FRESH)], [])          # 0,3% < 1% ⇒ không cờ
    r = run()
    it = items(r)
    check("price_only.status_DRIFT", r["status"] == "DRIFT", r)
    check("price_only.only_HPG", set(it) == {"HPG"}, list(it))
    h = it.get("HPG", {})
    check("price_only.px_flag", h.get("px_flag") is True and h.get("qty_flag") is False, h)
    check("price_only.render_px", "21.700→19.000" in "\n".join(M.render(r)))


# ── 3. không đổi ⇒ ĐÚNG 1 dòng ✅ ────────────────────────────────────────────────────────────
def t_no_change():
    reset()
    rows = [row("VPB", 1100, 22100, FRESH)]
    write_raw([rec("19:03:00", SP, "SpaceX", "positions", {"positions": rows})])
    M.live_read = live(rows, [])
    r = run()
    lines = M.render(r)
    check("no_change.status", r["status"] == "NO_DRIFT", r)
    check("no_change.one_line", len(lines) == 1 and lines[0].startswith("✅ Vị thế không đổi sau plan"),
          lines)
    check("no_change.cites_baseline_time", "mốc 19:03" in lines[0], lines)


# ── 4. DNSE lỗi ⇒ KHÔNG KIỂM ĐƯỢC, kèm lỗi thật ─────────────────────────────────────────────
def t_dnse_error():
    reset()
    write_raw([rec("19:03:00", SP, "SpaceX", "positions", {"positions": [row("A", 1, 1, FRESH)]})])
    M.live_read = live(None, raise_=ConnectionError("HTTP 503 gateway"))
    r = run()
    txt = "\n".join(M.render(r))
    check("dnse_err.status", r["status"] == "CANNOT_CHECK", r)
    check("dnse_err.render_loud", "KHÔNG KIỂM ĐƯỢC" in txt and "HTTP 503 gateway" in txt, txt)
    check("dnse_err.no_green", "✅" not in txt, txt)
    # payload sai dạng / danh mục rỗng khi cơ sở có mã
    M.live_read = lambda a, b: ("oops", [])
    check("dnse_err.bad_shape", run()["status"] == "CANNOT_CHECK")
    write_raw([rec("19:03:00", SP, "SpaceX", "positions", {"positions": []})])   # account trống
    M.live_read = lambda a, b: ("oops", [])
    r3 = run()
    check("dnse_err.bad_shape_empty_base_not_green", r3["status"] == "CANNOT_CHECK", r3)
    write_raw([rec("19:03:00", SP, "SpaceX", "positions", {"positions": [row("A", 1, 1, FRESH)]})])
    M.live_read = live([], [])
    r2 = run()
    check("dnse_err.empty_vs_base", r2["status"] == "CANNOT_CHECK" and "RỖNG" in r2["reason"], r2)


# ── 5. không có cơ sở ───────────────────────────────────────────────────────────────────────
def t_no_baseline():
    reset()
    M.live_read = live([row("A", 1, 1, FRESH)], [])
    r = run()
    check("no_base.file_missing", r["status"] == "CANNOT_CHECK" and "dnse_raw" in r["reason"], r)
    write_raw([rec("19:45:00", SP, "SpaceX", "positions", {"positions": [row("A", 1, 1, FRESH)]}),
               rec("19:01:00", ZP, "ZaloPay", "positions", {"positions": [row("A", 1, 1, FRESH)]})])
    r = run()
    check("no_base.no_record_before_1930", r["status"] == "CANNOT_CHECK" and "cơ sở" in r["reason"], r)
    check("no_base.render_loud", "KHÔNG KIỂM ĐƯỢC" in "\n".join(M.render(r)))
    # fallback: chỉ có bản trong phiên ⇒ dùng, ghi rõ FALLBACK
    write_raw([rec("16:00:00", SP, "SpaceX", "positions", {"positions": [row("A", 5, 10, FRESH)]})])
    M.live_read = live([row("A", 5, 10, FRESH)], [])
    r = run()
    check("no_base.fallback_labeled", "FALLBACK" in r.get("baseline_source", ""), r)
    check("no_base.fallback_render", "mốc FALLBACK 16:00" in M.render(r)[0], M.render(r))


# ── 6. hai account khác nhau ⇒ hai kết quả KHÁC nhau; lọc account_no (§12) ─────────────────
def t_two_accounts():
    reset()
    write_raw([
        rec("19:02:00", ZP, "ZaloPay", "positions", {"positions": [row("BID", 400, 38850, STALE)]}),
        rec("19:03:00", SP, "SpaceX", "positions", {"positions": [row("BID", 1100, 38850, STALE)]}),
        rec("19:04:00", ZP, "ZaloPay", "positions", {"positions": [row("BID", 400, 38850, STALE)]}),
    ])
    lives = {SP: [row("BID", 1175, 35800, z("19:09:00"))],
             ZP: [row("BID", 400, 38850, z("19:09:00"))]}
    M.live_read = lambda acct_no, label: ({"positions": lives[acct_no]}, [])
    rs, rz = run("SpaceX", SP), run("ZaloPay", ZP)
    check("two_acct.spacex_drift", rs["status"] == "DRIFT" and
          items(rs).get("BID", {}).get("qty_before") == 1100, rs)
    check("two_acct.zalopay_clean", rz["status"] == "NO_DRIFT", rz)
    check("two_acct.differ", M.render(rs) != M.render(rz))
    check("two_acct.render_names_account", "SpaceX 0002023347" in M.render(rs)[0])


# ── 7. batch DNSE chưa chạy lúc kiểm ⇒ KHÔNG được ra ✅ ─────────────────────────────────────
def t_stale_now():
    reset()
    rows = [row("VPB", 1100, 28000, STALE)]
    write_raw([rec("19:03:00", SP, "SpaceX", "positions", {"positions": rows})])
    M.live_read = live(rows, [])
    r = run()
    check("stale_now.cannot", r["status"] == "CANNOT_CHECK" and "chưa chạy xong" in r["reason"], r)


# ── 8. mốc trước batch: giá đổi theo phiên (≤ biên độ) KHÔNG cờ; KL đổi vẫn cờ ─────────────
def t_stale_base_daily_move():
    reset()
    write_raw([rec("19:03:00", SP, "SpaceX", "positions",
                   {"positions": [row("VHM", 900, 71800, STALE), row("BID", 1100, 38850, STALE)]})])
    M.live_read = live([row("VHM", 900, 68200, FRESH), row("BID", 1175, 35800, FRESH)], [])
    r = run()
    it = items(r)
    check("stale_base.daily_move_not_flagged", "VHM" not in it, list(it))
    check("stale_base.qty_flagged", "BID" in it, list(it))


# ── 9. đọc lẫn 2 hệ giá giữa các lô lúc kiểm ⇒ cờ ───────────────────────────────────────────
def t_mixed_frame():
    reset()
    write_raw([rec("19:03:00", ZP, "ZaloPay", "positions",
                   {"positions": [row("BID", 107, 35800, FRESH, 1826),
                                  row("BID", 300, 35800, FRESH, 1258)]})])
    M.live_read = live([row("BID", 107, 35800, FRESH, 1826), row("BID", 300, 38850, FRESH, 1258)], [])
    r = run("ZaloPay", ZP)
    b = items(r).get("BID", {})
    check("mixed.flagged", b.get("mixed_frame_now") is True, r)
    check("mixed.render", "lẫn 2 hệ giá" in "\n".join(M.render(r)))


# ── 10. khớp lệnh trong phiên giải thích KL; thiếu sổ lệnh ⇒ vẫn cờ + ghi chú ──────────────
def t_fills():
    reset()
    base_rows = [row("SSI", 1000, 30000, z("10:00:00")), row("VPB", 1100, 28000, STALE)]
    write_raw([
        rec("11:00:00", SP, "SpaceX", "positions", {"positions": base_rows}),
        rec("11:00:05", SP, "SpaceX", "orders", {"orders": []}),
        rec("19:03:00", SP, "SpaceX", "positions",
            {"positions": [row("SSI", 1500, 30500, FRESH), row("VPB", 1100, 28000, STALE)]}),
    ])
    orders = [{"id": 9, "symbol": "SSI", "side": "NB", "fillQuantity": 500,
               "createdDate": z("13:00:00"), "transDate": D}]
    M.live_read = live([row("SSI", 1500, 30500, FRESH), row("VPB", 1386, 22100, FRESH)], orders)
    r = run()
    it = items(r)
    check("fills.buy_explained_not_flagged", "SSI" not in it, it.get("SSI"))
    check("fills.credit_flagged_sau_phien", it.get("VPB", {}).get("kind") == "SAU_PLAN", it.get("VPB"))
    # không có sổ lệnh nào ⇒ SSI vẫn cờ (SAU_PHIEN), có ghi chú, không nuốt
    write_raw([rec("11:00:00", SP, "SpaceX", "positions", {"positions": base_rows}),
               rec("19:03:00", SP, "SpaceX", "positions",
                   {"positions": [row("SSI", 1500, 30500, FRESH), row("VPB", 1100, 28000, STALE)]})])
    M.live_read = live([row("SSI", 1500, 30500, FRESH), row("VPB", 1100, 28000, FRESH)], None)
    r = run()
    s = items(r).get("SSI", {})
    check("fills.no_orders_still_flagged", s.get("kind") == "SAU_PHIEN" and s.get("fills_unsure"), r)
    check("fills.no_orders_render_caveat", "chưa loại trừ được khớp lệnh" in "\n".join(M.render(r)))
    # lệnh tạo TRƯỚC mốc, không có ảnh chụp sổ lệnh tại mốc ⇒ không biết khớp trước/sau mốc ⇒
    # KL lệch phải gắn "chưa loại trừ được khớp lệnh" (không khẳng định chắc)
    early = [{"id": 7, "symbol": "SSI", "side": "NB", "fillQuantity": 500,
              "createdDate": z("10:00:00"), "transDate": D}]
    write_raw([rec("11:00:00", SP, "SpaceX", "positions",
                   {"positions": [row("SSI", 1500, 30000, z("10:30:00"))]}),
               rec("19:03:00", SP, "SpaceX", "positions", {"positions": [row("SSI", 1500, 30500, FRESH)]})])
    M.live_read = live([row("SSI", 1500, 30500, FRESH)], early)
    r = run()
    s_ = items(r).get("SSI", {})
    check("fills.created_before_base_unsure", s_.get("fills_unsure") is True, r)
    # sổ lệnh sống RỖNG ⇒ lùi về orders cuối trong dnse_raw (có ghi chú)
    write_raw([rec("11:00:00", SP, "SpaceX", "positions", {"positions": base_rows}),
               rec("11:00:05", SP, "SpaceX", "orders", {"orders": []}),
               rec("14:45:10", SP, "SpaceX", "orders", {"orders": orders}),
               rec("19:03:00", SP, "SpaceX", "positions",
                   {"positions": [row("SSI", 1500, 30500, FRESH), row("VPB", 1100, 28000, STALE)]})])
    M.live_read = live([row("SSI", 1500, 30500, FRESH), row("VPB", 1100, 28000, FRESH)], [])
    r = run()
    check("fills.empty_live_orders_fallback", "SSI" not in items(r) and any(
        "sổ lệnh DNSE lúc kiểm rỗng" in n for n in r["notes"]), r)


def t_sim_guard():
    reset()
    write_raw([rec("04:49:59", SP, "SpaceX", "positions", {"positions": [row("A", 1, 1, STALE)]})])
    r = run(sim_at="20:50:59")
    check("sim.no_record_after_base_cannot", r["status"] == "CANNOT_CHECK" and "mô phỏng" in r["reason"], r)


# ── 11. ngày nghỉ ⇒ SKIP, vẫn in 1 dòng (không rỗng) ───────────────────────────────────────
def t_weekend():
    r = M.run_check("SpaceX", SP, "2026-10-04", M.paths())
    check("weekend.skip", r["status"] == "SKIP")
    check("weekend.render_nonempty", len(M.render(r)) == 1 and M.render(r)[0])


# ── 12. main(): state + bus 1 lần / nội dung; bus lỗi ⇒ lần sau gửi lại ─────────────────────
def _main(*args):
    return M.main(["--account", "SpaceX", "--account-no", SP, "--date", D] + list(args))


def t_main_bus_state():
    reset()
    M.now_ict = lambda: dt.datetime(2026, 10, 5, 20, 50, 0)
    write_raw([rec("19:03:00", SP, "SpaceX", "positions", {"positions": [row("BID", 1100, 38850, STALE)]})])
    M.live_read = live([row("BID", 1175, 35800, FRESH)], [])
    rc1 = _main()
    rc2 = _main()
    calls = bus_calls()
    check("main.rc_drift_0", rc1 == 0 and rc2 == 0, (rc1, rc2))
    check("main.bus_once", len(calls) == 1, calls)
    check("main.bus_topic", bool(calls) and calls[0][1:3] == ["finding", f"plan-position-drift-SpaceX-{D}"],
          calls)
    st = json.load(open(os.path.join(STATE, f"SpaceX_{D}.json")))
    check("main.state_written", st["result"]["status"] == "DRIFT" and st.get("bus_posted_hash"), st)
    M.live_read = live([row("BID", 1200, 35800, FRESH)], [])     # nội dung đổi ⇒ gửi lại
    _main()
    check("main.bus_resend_on_change", len(bus_calls()) == 2)
    open(os.path.join(SB, "bus_fail"), "w").close()
    M.live_read = live(None, raise_=TimeoutError("read timed out"))
    rc = _main()
    check("main.cannot_rc2", rc == 2, rc)
    st = json.load(open(os.path.join(STATE, f"SpaceX_{D}.json")))
    check("main.bus_fail_not_marked", st["result"]["status"] == "CANNOT_CHECK" and
          st["bus_posted_hash"] != M.content_hash(st["result"]), st)
    os.remove(os.path.join(SB, "bus_fail"))
    _main()
    calls = bus_calls()
    check("main.bus_retry_after_fail", calls and calls[-1][1:3] ==
          ["error", f"plan-position-drift-cannot-check-SpaceX-{D}"], calls[-1:])


# ── 13. --report-block: lần này hỏng, lần trước kiểm được ⇒ in CẢ HAI ───────────────────────
def t_report_block_fallback(capsys_out):
    reset()
    M.now_ict = lambda: dt.datetime(2026, 10, 5, 20, 50, 0)
    write_raw([rec("19:03:00", SP, "SpaceX", "positions", {"positions": [row("BID", 1100, 38850, STALE)]})])
    M.live_read = live([row("BID", 1175, 35800, FRESH)], [])
    _main("--no-bus")
    M.live_read = live(None, raise_=ConnectionError("dnse down"))
    out = capsys_out(lambda: _main("--report-block", "--no-bus"))
    check("report_block.cannot_shown", "KHÔNG KIỂM ĐƯỢC" in out and "dnse down" in out, out)
    check("report_block.prev_drift_shown", "kết quả lần kiểm trước" in out and "1.100→1.175" in out, out)


def capture(fn):
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn()
    return buf.getvalue()


# ── 14. cổng môi trường ─────────────────────────────────────────────────────────────────────
def t_env_guard():
    saved = dict(os.environ)
    try:
        os.environ["MIKE_DRIFT_SELFCHECK"] = "0"
        try:
            M.paths()
            ok = False
        except M.EnvError:
            ok = True
        check("env.override_without_selfcheck_refused", ok)
        os.environ["MIKE_DRIFT_SELFCHECK"] = "1"
        os.environ["MIKE_DRIFT_STATE_DIR"] = M._PROD_STATE
        try:
            M.paths()
            ok = False
        except M.EnvError:
            ok = True
        check("env.selfcheck_prod_state_refused", ok)
    finally:
        os.environ.clear()
        os.environ.update(saved)


# ── 15. TZ: chuyển modifiedDate UTC→ICT không phụ thuộc TZ host ─────────────────────────────
def t_tz():
    check("tz.utc_to_ict", M._utc_z_to_ict("2026-08-14T12:09:09.401943562Z") == "2026-08-14T19:09:09",
          M._utc_z_to_ict("2026-08-14T12:09:09.401943562Z"))
    n = dt.datetime.now(dt.timezone.utc).astimezone(M.ICT).replace(tzinfo=None)
    check("tz.now_ict_anchored", abs((_orig_now() - n).total_seconds()) < 5, (_orig_now(), n))


# ── 16. replay dnse_raw THẬT ────────────────────────────────────────────────────────────────
REPLAY = [("2026-08-14", "SpaceX", SP, {"BID": (1100, 1175)}),
          ("2026-08-14", "ZaloPay", ZP, {"BID": (400, 427)}),
          ("2026-09-23", "SpaceX", SP, {"VPB": (1100, 1386)}),
          ("2026-09-23", "ZaloPay", ZP, {"VPB": (1200, 1512)}),
          ("2026-10-01", "SpaceX", SP, {"TPB": (200, 230)}),
          ("2026-10-01", "ZaloPay", ZP, {})]


def t_replay():
    prod_exec = M._PROD_EXEC
    saved = os.environ["MIKE_DRIFT_EXEC_DIR"], os.environ["MIKE_DRIFT_PLAN_DIR"]
    os.environ["MIKE_DRIFT_EXEC_DIR"], os.environ["MIKE_DRIFT_PLAN_DIR"] = prod_exec, M._PROD_PLAN
    try:
        for day, acct, no, want in REPLAY:
            if not os.path.exists(os.path.join(prod_exec, f"dnse_raw_{day}.jsonl")):
                check(f"replay.{day}.{acct}.file_present", False, "thiếu dnse_raw thật")
                continue
            r = M.run_check(acct, no, day, M.paths(), sim_at="20:50:59")
            got = {k: (v["qty_before"], v["qty_after"]) for k, v in items(r).items()}
            check(f"replay.{day}.{acct}.exact", got == want, got)
            check(f"replay.{day}.{acct}.sim_labeled", "MÔ PHỎNG" in r.get("now_source", ""), r)
    finally:
        os.environ["MIKE_DRIFT_EXEC_DIR"], os.environ["MIKE_DRIFT_PLAN_DIR"] = saved


# ── 17. tích hợp send_plan_report.sh (sandbox, --dry-run, lệnh drift GIẢ) ───────────────────
def t_send_plan():
    if os.environ.get("DRIFT_SC_SKIP_SENDPLAN") == "1":
        return
    sb = tempfile.mkdtemp(prefix="driftsc_sendplan_")
    try:
        plans = os.path.join(sb, "data", "trade_plans")
        os.makedirs(plans)
        json.dump({"plan_date": "2026-10-06", "account": "SpaceX", "state_name": "NEUTRAL",
                   "orders": [], "requires_user_approval": False},
                  open(os.path.join(plans, "plan_SpaceX_2026-10-06.json"), "w"))
        fakes = {
            "drift": "print('⚠️ **VỊ THẾ ĐỔI SAU KHI LẬP PLAN** FAKEBID 1.100→1.175')",
            "ok": "print('✅ Vị thế không đổi sau plan (kiểm 21:00, mốc 19:03)')",
            "crash": "import sys; sys.stderr.write('boom-fake-err\\n'); sys.exit(1)",
            "silent": "pass",
            "cannot": "print('⚠️ **Vị thế sau plan (SpaceX): KHÔNG KIỂM ĐƯỢC** — x'); raise SystemExit(2)",
        }
        outs = {}
        for k, code in fakes.items():
            fp = os.path.join(sb, f"fake_{k}.py")
            open(fp, "w").write(code + "\n")
            env = dict(os.environ, SEND_PLAN_WORKDIR_OVERRIDE=sb,
                       SEND_PLAN_MARKER_DIR=os.path.join(sb, "markers"), SEND_PLAN_DRIFT_CMD=fp)
            p = subprocess.run(["bash", SEND_PLAN, "--account", "SpaceX", "--dry-run"],
                               capture_output=True, text=True, env=env, timeout=180)
            outs[k] = p.stdout + p.stderr
        check("sendplan.drift_block_embedded", "FAKEBID 1.100→1.175" in outs["drift"], outs["drift"][-600:])
        check("sendplan.ok_one_line", outs["ok"].count("Vị thế không đổi sau plan") == 1)
        check("sendplan.crash_failsoft_loud", "KHÔNG KIỂM ĐƯỢC" in outs["crash"] and
              "boom-fake-err" in outs["crash"] and "Kế hoạch giao dịch" in outs["crash"],
              outs["crash"][-800:])
        check("sendplan.silent_not_allclear", "KHÔNG KIỂM ĐƯỢC" in outs["silent"] and
              "Vị thế không đổi" not in outs["silent"], outs["silent"][-600:])
        check("sendplan.cannot_rc2_passthrough", outs["cannot"].count("KHÔNG KIỂM ĐƯỢC") == 1 and
              "rc=2" not in outs["cannot"], outs["cannot"][-600:])
        env = dict(os.environ, SEND_PLAN_WORKDIR_OVERRIDE=sb,
                   SEND_PLAN_MARKER_DIR=os.path.join(sb, "markers"))
        env.pop("SEND_PLAN_DRIFT_CMD", None)
        p = subprocess.run(["bash", SEND_PLAN, "--account", "SpaceX", "--dry-run"],
                           capture_output=True, text=True, env=env, timeout=180)
        check("sendplan.sandbox_no_live_call", "sau plan" not in p.stdout.lower() and "Kế hoạch giao dịch" in p.stdout,
              p.stdout[-400:])
    finally:
        shutil.rmtree(sb, ignore_errors=True)


_orig_now = M.now_ict
_orig_live = M.live_read


def main_tests():
    for fn in (t_qty_only, t_price_only, t_no_change, t_dnse_error, t_no_baseline, t_two_accounts,
               t_stale_now, t_stale_base_daily_move, t_mixed_frame, t_fills, t_sim_guard, t_weekend, t_tz,
               t_env_guard, t_main_bus_state, lambda: t_report_block_fallback(capture), t_replay,
               t_send_plan):
        try:
            fn()
        except Exception as e:
            check(f"{getattr(fn, '__name__', 'lambda')}.no_exception", False, f"{type(e).__name__}: {e}")
        finally:
            M.now_ict, M.live_read = _orig_now, _orig_live


# ── đột biến ────────────────────────────────────────────────────────────────────────────────
MUTANTS = [
    ("filter_account_removed", 'if str(rec.get("account_no")) != str(account_no):', 'if False:'),
    ("baseline_last_not_first", "return in_win[0], session", "return in_win[-1], session"),
    ("window_end_widened", 'PLAN_WIN_END = "19:30:00"', 'PLAN_WIN_END = "23:59:59"'),
    ("no_session_compare", '("SAU_PHIEN", sess_base)', '("SAU_PHIEN", None)'),
    ("qty_flag_off", "qty_flag = unexpl != 0", "qty_flag = False"),
    ("px_flag_off", "px_flag = dev is not None and dev > px_thr", "px_flag = False"),
    ("px_thr_always_stale", 'px_thr = PX_THR_FRESH if (b.get("fresh") and n.get("fresh")) else PX_THR_STALE',
     "px_thr = PX_THR_STALE"),
    ("px_thr_always_fresh", 'px_thr = PX_THR_FRESH if (b.get("fresh") and n.get("fresh")) else PX_THR_STALE',
     "px_thr = PX_THR_FRESH"),
    ("mixed_off", "mixed = len(n[\"px\"]) > 1 and", "mixed = False and"),
    ("stale_now_silent", 'return cannot(why + ", chưa kết luận được")', "pass"),
    ("fills_ignored", "exp, unsure = explained_fills(base[0], ords, final_orders)",
     "exp, unsure = {}, set()"),
    ("fills_sign_flipped", 'sign = 1 if str(o.get("side", "")).upper() in ("NB", "B", "BUY") else -1',
     "sign = -1"),
    ("unsure_dropped", "unsure.add(sym)", "pass"),
    ("no_orders_not_unsure", 'return {}, {"*"}', "return {}, set()"),
    ("empty_live_orders_trusted", "if not final_orders:\n            final_orders = ords[-1][1] if ords else None",
     "if False:\n            final_orders = ords[-1][1] if ords else None"),
    ("dnse_error_swallowed", 'return cannot(f"đọc DNSE lỗi', 'return res or cannot(f"đọc DNSE lỗi'),
    ("empty_now_trusted", "if base_agg and not now_agg:", "if False:"),
    ("bad_shape_trusted", "if not isinstance(rows, list):", "if False:"),
    ("no_base_allclear", 'return cannot("không có cơ sở', 'res["status"]="NO_DRIFT"; return res\n        return cannot("x'),
    ("bus_every_time", "and st[\"bus_posted_hash\"] != h:", ":"),
    ("bus_marked_on_fail", "if post_bus(P, res, lines) == 0:", "if post_bus(P, res, lines) or True:"),
    ("report_block_prev_dropped", 'lines = lines + [f"   · kết quả lần kiểm trước', 'lines = lines or [f"x'),
    ("env_guard_off", "if set_ and not sc:", "if False:"),
    ("prod_state_guard_off", 'if os.path.realpath(out[k]) == os.path.realpath(_OVERRIDES[k]):', "if False:"),
    ("tz_utc_offset_lost", ".replace(tzinfo=dt.timezone.utc)\n    except ValueError:\n        return None\n    return t.astimezone(ICT)",
     "\n    except ValueError:\n        return None\n    return t.astimezone(ICT)"),
    ("render_no_drift_extra_line", 'f"{_hms(str(res.get(\'baseline_ts\', \'\')))[:5]}{sim})"]',
     'f"{_hms(str(res.get(\'baseline_ts\', \'\')))[:5]}{sim})", "extra"]'),
    ("render_cannot_green", 'return [f"⚠️ **Vị thế sau plan ({acct}): KHÔNG KIỂM ĐƯỢC** (kiểm {hm})',
     'return [f"✅ Vị thế sau plan ({acct}): KHÔNG KIỂM ĐƯỢC** (kiểm {hm})'),
    ("skip_weekend_off", "if d.weekday() >= 5 or is_holiday(d):", "if False:"),
    ("sim_guard_off", "if sim_at and now_ts <= plan_base[0]:", "if False:"),
]


SHELL_MUTANTS = [
    ("sh_empty_output_trusted", '} || [ -z "$DRIFT_BLOCK" ]; then', "}; then"),
    ("sh_rc2_wrapped", '[ "$DRIFT_RC" -ne 0 ] && [ "$DRIFT_RC" -ne 2 ]', '[ "$DRIFT_RC" -ne 0 ]'),
    ("sh_block_not_rendered", 'for _dl in os.environ.get("DRIFT_BLOCK", "").splitlines():',
     'for _dl in []:'),
    ("sh_sandbox_calls_real", 'elif [ -z "${SEND_PLAN_WORKDIR_OVERRIDE:-}" ]; then', "else"),
    ("sh_stderr_dropped", '_derr="$(tail -n 2 "$DRIFT_ERR"', '_derr="$(true'),
]


def run_mutations():
    src = open(TARGET).read()
    killed, alive = [], []
    sh_src = open(SEND_PLAN).read()
    for name, old, new in SHELL_MUTANTS:
        if sh_src.count(old) != 1:
            alive.append((name, f"mẫu không khớp đúng 1 lần ({sh_src.count(old)})"))
            continue
        mp = os.path.join(HERE, f".send_plan_report_mut_{name}.sh")   # trong bin/ để $ROOT đúng
        try:
            open(mp, "w").write(sh_src.replace(old, new))
            p = subprocess.run([sys.executable, os.path.abspath(__file__)], capture_output=True,
                               text=True, env=dict(os.environ, DRIFT_SC_SENDPLAN=mp), timeout=600)
        finally:
            os.remove(mp)
        killers = [ln.strip()[2:].split(" ")[0] for ln in p.stdout.splitlines()
                   if ln.strip().startswith("✗")]
        (killed.append((name, killers[0])) if p.returncode != 0 and killers
         else alive.append((name, f"rc={p.returncode}")))
    for name, old, new in MUTANTS:
        if src.count(old) != 1:
            alive.append((name, f"mẫu không khớp đúng 1 lần ({src.count(old)})"))
            continue
        tdir = tempfile.mkdtemp(prefix="driftmut_")
        shutil.copy(os.path.join(HERE, "wc_paths.py"), tdir)
        tp = os.path.join(tdir, "plan_position_drift_check.py")
        open(tp, "w").write(src.replace(old, new))
        env = dict(os.environ, DRIFT_SC_TARGET=tp, DRIFT_SC_SKIP_SENDPLAN="1",
                   WC_ROOT=M.WC_ROOT)
        p = subprocess.run([sys.executable, os.path.abspath(__file__)], capture_output=True,
                           text=True, env=env, timeout=600)
        shutil.rmtree(tdir, ignore_errors=True)
        killers = [ln.strip()[2:].split(" ")[0] for ln in p.stdout.splitlines()
                   if ln.strip().startswith("✗")]
        if p.returncode != 0 and killers:
            killed.append((name, killers[0]))
        else:
            alive.append((name, f"rc={p.returncode}"))
    for n, k in killed:
        print(f"  ☠ {n:30s} ← {k}")
    for n, why in alive:
        print(f"  ☺ SỐNG {n:26s} {why}")
    print(f"MUTATION: {len(killed)}/{len(MUTANTS) + len(SHELL_MUTANTS)} bị giết")
    return not alive


if __name__ == "__main__":
    try:
        main_tests()
        print("checks:", " ".join(sorted({x.split(".")[0] for x in PASSED})))
        print(f"PASS {len(PASSED)} / FAIL {len(FAILS)}  (python {sys.version.split()[0]}, "
              f"TZ={os.environ.get('TZ', '<unset>')})")
        ok = not FAILS
        if ok and "--mutations" in sys.argv:
            ok = run_mutations()
    finally:
        shutil.rmtree(SB, ignore_errors=True)
    sys.exit(0 if ok else 1)
