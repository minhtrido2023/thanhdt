#!/usr/bin/env python3
"""Selfcheck X1 — HOLD lệnh thoát LAG khi có quyền mua (lag_rights_exit_hold.py + auto_exit_inject).

Fixture thuần (dòng BQ giả theo dòng SCL thật), sandbox mkdtemp, KHÔNG BQ, KHÔNG bus/Discord
(AUTO_EXIT_TEST_MODE=1 + recorder subprocess), KHÔNG ghi data/ thật. Chạy 3 TZ + mutant:
    python3 bin/lag_rights_exit_hold_selfcheck.py
"""
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile

os.environ["AUTO_EXIT_TEST_MODE"] = "1"
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append(bool(cond))
    print(f"  {'PASS' if cond else 'FAIL'} — {name}" + ("" if cond else f"  [{detail}]"))


def row(**kw):
    """Dòng quyền mua giả theo SCL 15,38% thật (id thật, public 2026-09-08, P, chưa ngày)."""
    r = {"id": "6a0516165b1fb4c98c3ab2a2", "ticker": "SCL", "issue_method_code": "Rights",
         "issue_status_code": "P", "event_status": "announced", "exright_date": None,
         "record_date": None, "public_date": "2026-09-08", "exercise_ratio": "0.15384615",
         "value_per_share": None, "total_value": "0.0", "issue_volumn": "0"}
    r.update(kw)
    return r


def run_unit(H):
    SD, PD = "2026-10-22", "2026-10-23"
    ev = H.evaluate
    r = ev("SCL", PD, SD, [row(exright_date="2026-11-09", issue_status_code="D", event_status="executed")], [])
    ck("U1 có GDKHQ sau plan_date ⇒ HOLD", r and r["action"] == "HOLD" and "2026-11-09" in r["reason"], r)
    ck("U1b lý do có ngày KHÔNG mang signal_date (alert dedup 1 lần)", r and SD not in r["reason"], r)
    ck("U2 plan_date == GDKHQ ⇒ bán bình thường", ev("SCL", "2026-11-09", SD, [row(exright_date="2026-11-09")], []) is None)
    ck("U3 GDKHQ đã qua ⇒ bán bình thường", ev("SCL", PD, SD, [row(exright_date="2026-10-01")], []) is None)
    r = ev("SCL", PD, SD, [row()], [])
    ck("U4 chưa có ngày, chưa ack ⇒ HOLD + đòi quyết + mang signal_date (alert mỗi ngày)",
       r and r["action"] == "HOLD" and "CẦN USER QUYẾT" in r["reason"] and r["reason"].startswith(f"[{SD}]"), r)
    h = H.event_hash(row())
    ck("U4b lý do nêu id + hash để ghi ack", r and f"id={row()['id']}" in r["reason"] and f"h={h}" in r["reason"], r)
    ack = {"ticker": "SCL", "event_id": row()["id"], "event_hash": h, "decided_by": "user",
           "at": "2026-10-21T18:00:00+07:00", "source": "discord x"}
    r = ev("SCL", PD, SD, [row()], [dict(ack, decision="HOLD")])
    ck("U5 ack HOLD khớp ⇒ HOLD, lý do cố định (không signal_date)", r and r["action"] == "HOLD"
       and SD not in r["reason"] and "user chọn HOLD" in r["reason"], r)
    r = ev("SCL", PD, SD, [row()], [dict(ack, decision="SELL")])
    ck("U6 ack SELL khớp ⇒ RELEASE + note provenance", r and r["action"] == "RELEASE" and "discord x" in r["note"], r)
    r = ev("SCL", PD, SD, [row()], [dict(ack, decision="SELL", event_hash="deadbeef0000")])
    ck("U7 ack lệch hash ⇒ vẫn HOLD", r and r["action"] == "HOLD" and "không dùng được" in r["reason"], r)
    r = ev("SCL", PD, SD, [row()], [dict(ack, decision="SELL", decided_by="agent")])
    ck("U8 ack decided_by=agent ⇒ vẫn HOLD", r and r["action"] == "HOLD", r)
    r = ev("SCL", PD, SD, [row()], [dict(ack, decision="SELL"), dict(ack, decision="HOLD")])
    ck("U8b ack MỚI NHẤT thắng", r and r["action"] == "HOLD", r)
    ck("U9 huỷ (N) ⇒ không ảnh hưởng", ev("SCL", PD, SD, [row(issue_status_code="N")], []) is None)
    ck("U9b not_executed ⇒ không ảnh hưởng", ev("SCL", PD, SD, [row(event_status="not_executed")], []) is None)
    ck("U9c tỉ lệ 0 ⇒ không ảnh hưởng", ev("SCL", PD, SD, [row(exercise_ratio="0.0")], []) is None)
    ck("U9d không phải Rights ⇒ không ảnh hưởng", ev("SCL", PD, SD, [row(issue_method_code="Bonus")], []) is None)
    ck("U10 công bố SAU signal_date ⇒ không nhìn trước", ev("SCL", PD, SD, [row(public_date="2026-10-23")], []) is None)
    ck("U11 chưa ngày, công bố > 365 ngày ⇒ bỏ qua (bản ghi treo)",
       ev("SCL", PD, SD, [row(public_date="2022-05-01")], []) is None)
    ck("U11b chưa ngày, công bố đúng 365 ngày ⇒ vẫn HOLD",
       (ev("SCL", PD, SD, [row(public_date="2025-10-22")], []) or {}).get("action") == "HOLD")
    ck("U12 dòng mã khác không ảnh hưởng", ev("HPG", PD, SD, [row()], []) is None)
    r = ev("SCL", PD, SD, [row(exright_date="2026-13-01")], [])
    ck("U13 GDKHQ hỏng ⇒ fail-closed HOLD", r and r["action"] == "HOLD" and "không đọc được" in r["reason"], r)
    ck("U14 hash đổi khi vendor điền ngày", H.event_hash(row()) != H.event_hash(row(exright_date="2026-11-09")))

    def boom(_t):
        raise RuntimeError("bq failed: Access Denied xyz")
    r = H.holds_for(["SCL", "HPG"], PD, SD, fetch=boom)
    ck("U15 lỗi BQ ⇒ HOLD MỌI mã + lỗi thật + ngày",
       set(r) == {"SCL", "HPG"} and all(v["action"] == "HOLD" and "Access Denied xyz" in v["reason"]
                                        and v["reason"].startswith(f"[{SD}]") for v in r.values()), r)
    td = tempfile.mkdtemp()
    try:
        bad = os.path.join(td, "exit_ack.json")
        open(bad, "w").write("{not json")
        rows = [row(), row(id="X2", ticker="VPB", exright_date="2026-11-30")]
        r = H.holds_for(["SCL", "VPB", "FPT"], PD, SD, fetch=lambda t: rows, ack_file=bad)
        ck("U16 sổ ack hỏng ⇒ mã chưa ngày HOLD nêu lỗi sổ; mã có ngày HOLD bình thường; mã không quyền ⇒ không có",
           "sổ ack không đọc được" in r.get("SCL", {}).get("reason", "") and r.get("VPB", {}).get("action") == "HOLD"
           and "FPT" not in r, r)
        ck("U17 không có mã ⇒ {} và KHÔNG gọi BQ", H.holds_for([], PD, SD, fetch=boom) == {})
        # record()
        ap = os.path.join(td, "ok", "exit_ack.json")
        f = lambda t: [row(), row(id="DATED", exright_date="2026-11-09")]  # noqa: E731
        base = dict(ticker="scl", event_id=row()["id"], event_hash_seen=h, decision="SELL", decided_by="user",
                    at="2026-10-22T18:00:00+07:00", source="discord link", fetch=f, ack_file=ap)

        def rej(label, **over):
            try:
                H.record(**dict(base, **over))
                ck(label, False, "không raise")
            except ValueError as e:
                ck(label, True, str(e))
        rej("R1 decided_by=agent bị từ chối", decided_by="agent")
        rej("R2 source rỗng bị từ chối", source=" ")
        rej("R3 at không múi giờ bị từ chối", at="2026-10-22T18:00:00")
        rej("R4 hash lệch bị từ chối", event_hash_seen="000000000000")
        rej("R5 sự kiện đã có ngày bị từ chối", event_id="DATED", event_hash_seen=H.event_hash(f(0)[1]))
        rej("R6 id không tồn tại bị từ chối", event_id="NOPE")
        rej("R7 decision lạ bị từ chối", decision="MAYBE")
        ck("R8 chưa ghi gì khi bị từ chối", not os.path.exists(ap))
        e = H.record(**base)
        ck("R9 ack hợp lệ ghi được (ticker chuẩn hoá, decided_by=user)", e["ticker"] == "SCL" and e["decided_by"] == "user"
           and H.load_acks(ap)[-1]["event_hash"] == h)
        r = H.holds_for(["SCL"], PD, SD, fetch=lambda t: [row()], ack_file=ap)
        ck("R10 sau ack SELL ⇒ RELEASE", r.get("SCL", {}).get("action") == "RELEASE", r)
        r = H.holds_for(["SCL"], PD, SD, fetch=lambda t: [row(exright_date="2026-11-09")], ack_file=ap)
        ck("R11 vendor điền ngày sau ack SELL ⇒ HOLD tới GDKHQ (ack hết hiệu lực)",
           r.get("SCL", {}).get("action") == "HOLD" and "2026-11-09" in r["SCL"]["reason"], r)
    finally:
        shutil.rmtree(td, ignore_errors=True)


def run_e2e(H):
    """process_account thật (book_lot_snapshot mock qua helper của auto_exit_inject_selfcheck)."""
    real_holds_for = H.holds_for
    import auto_exit_inject_selfcheck as S      # import này stub holds_for — khôi phục ngay
    import auto_exit_inject as aei
    aei.rights_hold.holds_for = real_holds_for
    from trading_bot.vn_market import next_trading_day
    base = next_trading_day(next_trading_day(dt.date(2024, 1, 2)))
    chain = [base]
    for _ in range(60):
        chain.append(next_trading_day(chain[-1]))
    sig = chain[-1]
    sd, pd = str(sig), str(next_trading_day(sig))
    lag_entry, bal_entry = str(chain[-1 - 25]), str(chain[-1 - 45])

    def run(rows, orders=None, ack_dir=None, fetch_raises=False):
        td, exec_dir, plan_dir, ledger = S.setup_sandbox()
        os.environ["MIKE_LAG_RIGHTS_DIR"] = ack_dir or os.path.join(td, "lag_rights")
        calls_fetch = []

        def fetch(t):
            calls_fetch.append(list(t))
            if fetch_raises:
                raise RuntimeError("bq failed: quota exceeded abc")
            return rows
        H.fetch_rights_rows = fetch
        sp_orig, calls = S.install_subprocess_recorder()
        orig = S.patch_all(exec_dir, plan_dir, ledger,
                           lag_lots={"SCL": {"qty": 14000, "entry_date": lag_entry},
                                     "HPG": {"qty": 1000, "entry_date": lag_entry}},
                           bal_lots={"FPT": {"qty": 500, "entry_date": bal_entry}})
        try:
            S.write_positions(exec_dir, sd, {"SCL": (14000, 22000), "HPG": (1000, 25000), "FPT": (500, 100000)})
            S.write_plan(plan_dir, S.ACCOUNT, pd, orders=orders)
            rc = aei.process_account(S.ACCOUNT, pd, sd, dry_run=False)
            plan = S.load_plan_raw(plan_dir, S.ACCOUNT, pd)
        finally:
            S.restore_all(orig)
            S.restore_subprocess_recorder(sp_orig)
            shutil.rmtree(td, ignore_errors=True)
        sells = {(o["ticker"], o["book"]): o for o in plan["orders"] if o["side"] == "sell"}
        blocked = [b for n in plan.get("auto_exit_inject_notes", []) for b in n.get("blocked", [])]
        return rc, sells, blocked, calls, calls_fetch

    rc, sells, blocked, calls, cf = run([])
    ck("E0 không quyền mua ⇒ SELL SCL+HPG LAG + FPT BAL như cũ (regression)",
       rc == 0 and {("SCL", "LAG"), ("HPG", "LAG"), ("FPT", "BAL")} <= set(sells) and not blocked, (sells, blocked))
    ck("E0b chỉ tra BQ cho candidate LAG", cf == [["HPG", "SCL"]], cf)
    pub = str(sig - dt.timedelta(days=30))
    dated = [row(exright_date=str(sig + dt.timedelta(days=30)), public_date=pub)]
    undated = [row(public_date=pub)]
    rc, sells, blocked, calls, _ = run(dated)
    ck("E1 GDKHQ sau plan_date ⇒ KHÔNG SELL SCL; HPG/FPT vẫn bán",
       ("SCL", "LAG") not in sells and ("HPG", "LAG") in sells and ("FPT", "BAL") in sells, sells)
    ck("E1b SCL vào blocked với lý do HOLD tới GDKHQ",
       any(b["ticker"] == "SCL" and b["book"] == "LAG" and "HOLD tới GDKHQ" in b["reason"] for b in blocked), blocked)
    ck("E1c test-mode ⇒ 0 subprocess thật (bus/Discord)", calls == [], calls)
    rc, sells, blocked, *_ = run([row(exright_date=pd, public_date=pub)])
    ck("E2 plan_date == GDKHQ ⇒ SELL SCL bình thường", ("SCL", "LAG") in sells and not blocked, (sells, blocked))
    rc, sells, blocked, *_ = run(undated)
    ck("E3 chưa ngày, chưa ack ⇒ KHÔNG SELL SCL, blocked đòi user quyết",
       ("SCL", "LAG") not in sells and any("CẦN USER QUYẾT" in b["reason"] for b in blocked), blocked)
    ackd = tempfile.mkdtemp()
    try:
        H.record("SCL", row()["id"], H.event_hash(undated[0]), "SELL", "user", "2026-10-22T18:00:00+07:00",
                 "discord y", fetch=lambda t: undated, ack_file=os.path.join(ackd, "exit_ack.json"))
        rc, sells, blocked, *_ = run(undated, ack_dir=ackd)
    finally:
        shutil.rmtree(ackd, ignore_errors=True)
    ck("E4 ack SELL của user ⇒ SELL SCL, note mang provenance",
       ("SCL", "LAG") in sells and "discord y" in sells[("SCL", "LAG")]["note"] and not blocked, (sells, blocked))
    rc, sells, blocked, *_ = run([], fetch_raises=True)
    ck("E5 lỗi BQ ⇒ KHÔNG SELL LAG nào, blocked nêu lỗi thật; BAL vẫn bán",
       ("SCL", "LAG") not in sells and ("HPG", "LAG") not in sells and ("FPT", "BAL") in sells
       and sum("quota exceeded abc" in b["reason"] for b in blocked) == 2, (sells, blocked))
    pre = S.existing_sell_order("SCL", 14000, "LAG", "SELL-SCL-DB")
    rc, sells, blocked, *_ = run(dated, orders=[pre])
    ck("E6 plan đã có SELL LAG do người khác + HOLD ⇒ cảnh báo người duyệt gỡ, không tự xoá",
       any("người duyệt phải gỡ" in b["reason"] and "SELL-SCL-DB" in b["reason"] for b in blocked)
       and sells.get(("SCL", "LAG"), {}).get("id") == "SELL-SCL-DB", (sells, blocked))

    # alert dedup: lý do có ngày ⇒ hôm sau KHÔNG báo lại; lý do chưa ngày (mang signal_date) ⇒ báo mỗi ngày
    td = tempfile.mkdtemp()
    orig_state = aei.BLOCK_ALERT_STATE_PATH
    aei.BLOCK_ALERT_STATE_PATH = os.path.join(td, "st.json")
    try:
        def day(sdate, rws):
            res = H.evaluate("SCL", "2026-10-23", sdate, rws, [])
            lines, st = aei._new_block_alert_lines("A", [{"ticker": "SCL", "book": "LAG", "reason": res["reason"]}],
                                                   [], sdate)
            aei._atomic_write_json(aei.BLOCK_ALERT_STATE_PATH, st)
            return lines
        d1 = day("2026-10-21", [row(exright_date="2026-11-09")])
        d2 = day("2026-10-22", [row(exright_date="2026-11-09")])
        ck("A1 có ngày: báo ngày đầu, hôm sau dedup", len(d1) == 1 and d2 == [], (d1, d2))
        u1 = day("2026-10-21", [row()])
        u2 = day("2026-10-22", [row()])
        ck("A2 chưa ngày: báo LẠI mỗi ngày (đòi user quyết)", len(u1) == 1 and len(u2) == 1, (u1, u2))
    finally:
        aei.BLOCK_ALERT_STATE_PATH = orig_state
        shutil.rmtree(td, ignore_errors=True)


def run_inner():
    sys.path.insert(0, HERE)
    import lag_rights_exit_hold as H
    import auto_exit_inject as aei
    mut = os.environ.get("LRH_MUT")
    if mut:
        fname, old, new = json.loads(mut)
        mod = H if fname == "lag_rights_exit_hold.py" else aei
        src = open(os.path.join(HERE, fname), encoding="utf-8").read()
        assert src.count(old) == 1, f"mutant gốc không khớp đúng 1 lần: {old!r}"
        exec(compile(src.replace(old, new), mod.__file__, "exec"), mod.__dict__)
        if mod is aei:
            aei.rights_hold = H
    run_unit(H)
    run_e2e(H)
    n, ok = len(RESULTS), sum(RESULTS)
    print(f"{ok}/{n} PASS")
    return 0 if ok == n else 1


MUTANTS = [
    ("lag_rights_exit_hold.py", "if plan_date < ex:", "if plan_date <= ex:"),
    ("lag_rights_exit_hold.py", "if plan_date < ex:", "if False:"),
    ("lag_rights_exit_hold.py", 'and r.get("issue_status_code") != "N"', ""),
    ("lag_rights_exit_hold.py", "if pub and pub > signal_date:", "if False:"),
    ("lag_rights_exit_hold.py", "if age is not None and age > UNDATED_MAX_AGE_DAYS:", "if False:"),
    ("lag_rights_exit_hold.py", 'elif a.get("decided_by") != "user" or', "elif"),
    ("lag_rights_exit_hold.py", 'a.get("event_hash") != h or ', ""),
    ("lag_rights_exit_hold.py", 'ask = (f"[{signal_date}] HOLD', 'ask = (f"HOLD'),
    ("lag_rights_exit_hold.py", 'return {t: {"action": "HOLD"', 'return {t: {"action": "RELEASE"'),
    ("lag_rights_exit_hold.py", "acks, ack_error = [], f\"", "acks, ack_error = [], None and f\""),
    ("lag_rights_exit_hold.py", "    if decided_by != \"user\":\n        raise", "    if False:\n        raise"),
    ("lag_rights_exit_hold.py", "    if str(event_hash_seen).strip() != h:\n        raise", "    if False:\n        raise"),
    ("lag_rights_exit_hold.py", "    if r.get(\"exright_date\"):\n        raise", "    if False:\n        raise"),
    ("auto_exit_inject.py", 'if rh and rh["action"] == "HOLD":', "if False:"),
    ("auto_exit_inject.py", "if lag_candidates else {})", "if False else {})"),
    ("auto_exit_inject.py", 'f"chèn): người duyệt phải gỡ" if existing else "")', '"")'),
    ("auto_exit_inject.py", "            note += f\" — {rh['note']}\"\n", ""),
]


def run_mutants():
    bad = 0
    for i, m in enumerate(MUTANTS, 1):
        env = dict(os.environ, LRH_MUT=json.dumps(m))
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--inner"], env=env,
                           capture_output=True, text=True, timeout=600)
        if "mutant gốc không khớp" in (r.stderr + r.stdout):
            print(f"  ❌ mutant {i}: chuỗi gốc không khớp đúng 1 lần — sửa MUTANTS")
            bad += 1
            continue
        killed = r.returncode != 0
        print(f"  {'KILLED' if killed else 'SURVIVED'} — mutant {i}: {m[0]} {m[1].strip()[:60]!r}")
        bad += 0 if killed else 1
    print(f"MUTANTS: {len(MUTANTS) - bad}/{len(MUTANTS)} killed")
    return bad


def main():
    if "--inner" in sys.argv:
        return run_inner()
    rc = 0
    for label, env in (("env -u TZ", {k: v for k, v in os.environ.items() if k != "TZ"}),
                       ("TZ=Pacific/Kiritimati", dict(os.environ, TZ="Pacific/Kiritimati")),
                       ("TZ=America/New_York", dict(os.environ, TZ="America/New_York"))):
        print(f"=== {label} ===")
        rc |= subprocess.run([sys.executable, os.path.abspath(__file__), "--inner"], env=env).returncode
    if "--no-mutants" not in sys.argv:
        print("=== mutants ===")
        if run_mutants():
            rc |= 1
    print("TỔNG:", "PASS" if rc == 0 else "FAIL")
    return rc


if __name__ == "__main__":
    sys.exit(main())
