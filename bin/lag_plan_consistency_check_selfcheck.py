#!/usr/bin/env python3
"""Self-check cho lag_plan_consistency_check.py (cổng nhất quán LAG + cảnh báo cấp vốn).

Không chạm DNSE/Discord/bus thật: notify/append_event là script giả ghi log, state ở thư mục tạm.
Có MUTATION: phá từng điểm logic trong bản sao module ⇒ bộ ca PHẢI đỏ (mutant không chết = test
yếu). Chạy lại dưới `env -u TZ` và TZ lạ (§16/§19) bằng subprocess.

Chạy: python3 mike/bin/lag_plan_consistency_check_selfcheck.py
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "lag_plan_consistency_check.py")
CHECKER = MOD
sys.path.insert(0, HERE)


def load(path, name="lagchk_under_test"):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def cand(t, decision="BUY", day=None, **kw):
    c = {"ticker": t, "decision": decision, "floor_fail": False, "play_type": "LAG_HI"}
    if day is not None:
        c["entry_window_day"] = day
    else:
        c["entry_window_date"] = "2026-10-26"
    c.update(kw)
    return c


def order(t, qty=100, side="buy", **kw):
    return dict({"id": f"{side}-{t}", "ticker": t, "side": side, "qty": qty, "book": "LAG",
                 "ref_price": 10000, "limit_price_vnd": 10000}, **kw)


def plan(due, orders=(), deferred=(), **kw):
    p = {"plan_date": "2026-10-26", "account": "SpaceX", "signal_date": "2026-10-23",
         "lag_analysis": {"due_today": list(due)}, "orders": list(orders),
         "deferred_orders": list(deferred), "cash_planning": {"available_cash_vnd": 5_000_000.0}}
    p.update(kw)
    return p


def kinds(res):
    return sorted((f["kind"], f["ticker"], f["cause"]) for f in res["findings"])


def write_exec(path, body):
    with open(path, "w") as fh:
        fh.write(body)
    os.chmod(path, 0o755)


def cases(m):
    """Trả danh sách (tên, ok, chi tiết). `m` = module cần test (gốc hoặc mutant)."""
    out = []

    def ck(name, cond, detail=""):
        out.append((name, bool(cond), detail))

    # dd_gate=False: file này kiểm logic NHẤT QUÁN; cổng DD có selfcheck riêng (lag_dd_gate_selfcheck.py)
    A = lambda p, **k: m.analyze(p, crosscheck=False, dd_gate=False, **k)       # noqa: E731

    # 1 ca bình thường
    r = A(plan([cand("ABC", day=1)], [order("ABC")]))
    ck("normal: BUY có lệnh ⇒ 0 phát hiện", r["findings"] == [], kinds(r))
    # 2 ca SSI 07/08: BUY, không orders, không deferred
    r = A(plan([cand("SSI"), cand("PGS", "SKIP — cờ đỏ")], [order("ACB")], []))
    ck("SSI: BUY rơi im lặng ⇒ LAG_BUY_MISSING + FUNDING_ALERT",
       ("CONSISTENCY_FAIL", "SSI", "LAG_BUY_MISSING") in kinds(r)
       and ("FUNDING_ALERT", "SSI", "LAG_BUY_MISSING") in kinds(r), kinds(r))
    ck("SSI: mã SKIP (PGS) không bị báo", all(f["ticker"] != "PGS" for f in r["findings"]))
    # 3 deferred hợp lệ, phiên chuẩn ⇒ alert đỏ, KHÔNG fail nhất quán
    d = {"ticker": "BSR", "side": "buy", "book": "LAG", "status": "WAIT_CASH", "qty": 2900,
         "ref_price": 25_000, "deferred_reason": "thiếu cash 5,8tr / cần 72,5tr"}
    r = A(plan([cand("BSR", day=1)], [], [d]))
    ck("deferred hợp lệ ngày 1 ⇒ chỉ FUNDING_ALERT", kinds(r) == [("FUNDING_ALERT", "BSR", "LAG_BUY_DEFERRED")], kinds(r))
    al = r["findings"][0]
    ck("alert: need = qty×ref_price từ plan (72,5tr)", abs((al["need_vnd"] or 0) - 72_500_000) < 1, al["need_vnd"])
    txt = "\n".join(m.render(r))
    ck("render nêu mã, account, thiếu ≈ 67,5 triệu, lý do trích, hạn chót",
       all(s in txt for s in ("BSR", "SpaceX", "67,5 triệu", "WAIT_CASH", "thiếu cash 5,8tr", "08:45")), txt)
    # 4 deferred nhưng phiên 2 ⇒ không alert, không fail
    r = A(plan([cand("BSR", day=2)], [], [d]))
    ck("deferred ngày 2 ⇒ im (chỉ phiên chuẩn mới báo đỏ)", r["findings"] == [], kinds(r))
    # 5 deferred không status, không lý do ⇒ FAIL
    r = A(plan([cand("BSR", day=2)], [], [{"ticker": "BSR", "side": "buy"}]))
    ck("deferred trống lý do ⇒ LAG_BUY_DEFERRED_NO_REASON",
       ("CONSISTENCY_FAIL", "BSR", "LAG_BUY_DEFERRED_NO_REASON") in kinds(r), kinds(r))
    # 6 qty 0 / '0' chuỗi
    for q in (0, "0"):
        r = A(plan([cand("ABC", day=1)], [order("ABC", qty=q)]))
        ck(f"order qty={q!r} ⇒ LAG_BUY_ORDER_ZERO_QTY", ("CONSISTENCY_FAIL", "ABC", "LAG_BUY_ORDER_ZERO_QTY") in kinds(r), kinds(r))
    r = A(plan([cand("ABC", day=1)], [order("abc", qty="1,500", side="BUY")]))
    ck("chuẩn hoá: ticker thường, side 'BUY', qty '1,500' ⇒ coi là có lệnh", r["findings"] == [], kinds(r))
    # 7 chuẩn hoá decision
    for dec, want in (("buy", True), (" BUY — DCF CHEAP", True), ("BUYING", False),
                      ("SKIP — KHÔNG PHẢI VÌ FLOOR_FAIL", False), (None, False)):
        r = A(plan([cand("XYZ", dec)], [], []))
        ck(f"decision {dec!r} ⇒ {'bắt' if want else 'bỏ qua'}", bool(r["findings"]) == want, kinds(r))
    # 7b decision DEFER/WAIT_CASH/BUY_DEFERRED (hợp đồng mini file) vẫn phải bị kiểm — ca 58% vốn lỡ
    for dec in ("DEFER", "WAIT_CASH", "BUY_DEFERRED", "deferred — thiếu tiền"):
        r = A(plan([cand("DEF", dec, day=1)], [], []))
        ck(f"decision {dec!r} thiếu cả lệnh lẫn mục hoãn ⇒ LAG_BUY_MISSING + FUNDING_ALERT",
           {("CONSISTENCY_FAIL", "DEF", "LAG_BUY_MISSING"), ("FUNDING_ALERT", "DEF", "LAG_BUY_MISSING")} <= set(kinds(r)), kinds(r))
        r = A(plan([cand("DEF", dec, day=1)], [], [{"ticker": "DEF", "side": "buy", "status": "WAIT_CASH",
                                                      "deferred_reason": "sức mua broker 142 cp < 1800"}]))
        ck(f"decision {dec!r} có mục hoãn kèm lý do ngày 1 ⇒ chỉ FUNDING_ALERT (không FAIL nhất quán)",
           [k for k in kinds(r) if k[0] == "CONSISTENCY_FAIL"] == [] and any(k[0] == "FUNDING_ALERT" for k in kinds(r)), kinds(r))
    r = A(plan([cand("DEF", "SKIP", day=1)], [], []))
    ck("decision SKIP thiếu lệnh ⇒ vẫn sạch (không bắt nhầm SKIP)", r["findings"] == [], kinds(r))
    # 8 lệnh BÁN cùng mã không tính
    r = A(plan([cand("ABC", day=1)], [order("ABC", side="sell")]))
    ck("lệnh bán cùng mã KHÔNG thoả BUY", ("FUNDING_ALERT", "ABC", "LAG_BUY_MISSING") in kinds(r), kinds(r))
    # 9 schema 08-07: không entry_window_day, dùng entry_window_date == plan_date
    c = cand("ABC")
    c["entry_window_date"] = "2026-10-26"
    r = A(plan([c], [], []))
    ck("schema entry_window_date==plan_date ⇒ tính là phiên chuẩn", ("FUNDING_ALERT", "ABC", "LAG_BUY_MISSING") in kinds(r), kinds(r))
    c["entry_window_date"] = "2026-10-27"
    ck("entry_window_date≠plan_date ⇒ không phải phiên chuẩn", not any(f["kind"] == "FUNDING_ALERT" for f in A(plan([c]))["findings"]))
    # 10 không lag_analysis / due_today hỏng
    ck("không lag_analysis ⇒ sạch", A({"plan_date": "x", "account": "A"})["findings"] == [])
    r = A({"plan_date": "x", "account": "A", "lag_analysis": {"counts": {"due_today": 0}, "result": "RỖNG"}})
    ck("schema ngày rỗng (counts.due_today=0, không list) ⇒ sạch, có ghi chú", r["findings"] == [] and r["notes"], r)
    r = A({"plan_date": "x", "account": "A", "lag_analysis": {"counts": {"due_today": 2}}})
    ck("counts.due_today=2 mà không có list ⇒ MALFORMED", r["findings"][0]["cause"] == "LAG_ANALYSIS_MALFORMED", r)
    ck("due_today không phải list ⇒ LAG_ANALYSIS_MALFORMED",
       A({"plan_date": "x", "account": "A", "lag_analysis": {"due_today": "oops"}})["findings"][0]["cause"] == "LAG_ANALYSIS_MALFORMED")
    # 11 bằng chứng JIT/park trích từ plan, không hardcode
    p = plan([cand("DRI", day=1)], [], [],
             park_trim_proposal={"decision": "BLOCKED_RECONCILE", "blocked": ["VHM lệch sổ 100cp"]},
             jit_unpark_proposal={"decision": "NO_JIT", "jit_sell_total_vnd": 0})
    txt = "\n".join(m.render(A(p)))
    ck("render trích park_trim BLOCKED_RECONCILE + lý do từ plan", "BLOCKED_RECONCILE" in txt and "VHM lệch sổ 100cp" in txt, txt)
    p = plan([cand("DRI", day=1)], [], [], jit_unpark_proposal={"decision": "JIT", "jit_sell_total_vnd": 137_200_000,
                                                                  "sells_by_ticker": {"ACB": 300}})
    txt = "\n".join(m.render(A(p)))
    ck("render trích JIT đã có (137,2 triệu từ ACB)", "137,2 triệu" in txt and "ACB" in txt, txt)
    # 12 đối chiếu CSV: mã phiên 1 theo CSV mà lag_analysis không nhắc
    td = tempfile.mkdtemp()
    try:
        csvp = os.path.join(td, "golive_v23_recommendations_2026-10-23.csv")
        with open(csvp, "w", encoding="utf-8") as fh:
            fh.write("book,ticker,play_type,status,weight_pct,weight_base,due_diligence\n"
                     "LAG,AAA,LAG_HI,UPCOMING T+1 phiên tới,10,x,ok\n"
                     "LAG,BBB,LAG_HI,UPCOMING T+1 phiên tới,10,x,ok\n"
                     "LAG,CCC,LAG_HI,UPCOMING T+3 phiên tới,10,x,ok\n")
        p = plan([cand("AAA", "SKIP — cờ đỏ", day=1)], [], [])
        r = m.analyze(p, csv_path=csvp, crosscheck=True)
        ck("crosscheck CSV: BBB (T+1) vắng trong lag_analysis ⇒ LAG_CANDIDATE_NOT_ANALYSED; AAA có; CCC (T+3) không",
           kinds(r) == [("CONSISTENCY_FAIL", "BBB", "LAG_CANDIDATE_NOT_ANALYSED")], (kinds(r), r["notes"]))
        p2 = plan([cand("AAA", "SKIP — cờ đỏ", day=1)], [], [])
        p2["lag_analysis"]["window_passed"] = [{"ticker": "bbb", "note": "đã xét ở khoá khác"}]
        ck("crosscheck: mã nhắc ở khoá khác trong lag_analysis (bbb) không bị báo vắng",
           m.analyze(p2, csv_path=csvp, crosscheck=True)["findings"] == [])
        r = m.analyze(p, csv_path=os.path.join(td, "khong_co.csv"), crosscheck=True)
        ck("crosscheck CSV thiếu ⇒ ghi chú rõ, không crash, không phát hiện giả", r["findings"] == [] and r["notes"], r["notes"])
    finally:
        shutil.rmtree(td, ignore_errors=True)
    # 13 phát + idempotent
    td = tempfile.mkdtemp()
    try:
        nlog, blog = os.path.join(td, "n.log"), os.path.join(td, "b.log")
        nf, bf = os.path.join(td, "notify.sh"), os.path.join(td, "bus.sh")
        write_exec(nf, f'#!/bin/bash\necho "$2|$1" >> {nlog}\nexit ${{FAKE_NOTIFY_RC:-0}}\n')
        write_exec(bf, f'#!/bin/bash\necho "$1|$2|$3" >> {blog}\nexit 0\n')
        os.environ.update(MIKE_LAGCHK_STATE_DIR=os.path.join(td, "st"), MIKE_LAGCHK_NOTIFY=nf, MIKE_LAGCHK_APPEND_EVENT=bf)
        res = A(plan([cand("SSI")], [], []))
        n1 = m.emit(res)
        n2 = m.emit(res)
        lines = lambda f: open(f).read().splitlines() if os.path.exists(f) else []   # noqa: E731
        ck("emit lần 1 phát 2 mục (FAIL+ALERT), lần 2 phát 0 (idempotent)", (n1, n2) == (2, 0), (n1, n2))
        msgs = lambda: [x for x in lines(nlog) if x.startswith("trading_daily|")]   # noqa: E731
        ck("đúng 1 tin Discord vào trading_daily + 1 bus finding", len(msgs()) == 1
           and len(lines(blog)) == 1 and "Wags|finding|lag-plan-check-SpaceX-2026-10-26" in lines(blog)[0], (lines(nlog), lines(blog)))
        res2 = A(plan([cand("SSI"), cand("DRI")], [], []))
        before = len(lines(nlog))
        n3 = m.emit(res2)
        tail = "\n".join(lines(nlog)[before:])
        ck("ca MỚI trong cùng plan_date chỉ phát phần mới (DRI), không lặp SSI",
           n3 == 2 and "DRI" in tail and not re.search(r"\bSSI\b", tail) and len(msgs()) == 2, n3)
        os.environ["FAKE_NOTIFY_RC"] = "7"
        res3 = A(plan([cand("NEW")], [], []))
        nb = m.emit(res3)
        os.environ.pop("FAKE_NOTIFY_RC")
        nr = m.emit(res3)
        ck("Discord lỗi ⇒ KHÔNG ghi state; lượt sau phát lại", nb == -1 and nr == 2, (nb, nr))
        ck("plan_date khác ⇒ state riêng, phát lại", m.emit(dict(res, plan_date="2026-10-27")) == 2)
    finally:
        for k in ("MIKE_LAGCHK_STATE_DIR", "MIKE_LAGCHK_NOTIFY", "MIKE_LAGCHK_APPEND_EVENT", "FAKE_NOTIFY_RC"):
            os.environ.pop(k, None)
        shutil.rmtree(td, ignore_errors=True)
    return out


MUTANTS = [
    ("bỏ nhận BUY (decision luôn False)", "return bool(_RE_BUY.match(str(d or \"\")))", "return False"),
    ("chỉ nhận BUY (bỏ DEFER/WAIT_CASH)", "_RE_BUY = re.compile(r\"^\\s*(BUY_DEFERRED|BUY|DEFERRED|DEFER|WAIT_CASH|RESIDUAL|ORDER)\\b\", re.I)", "_RE_BUY = re.compile(r\"^\\s*BUY\\b\", re.I)"),
    ("mã SKIP cũng bị bắt", "return bool(_RE_BUY.match(str(d or \"\")))", "return True"),
    ("qty 0 vẫn coi là có lệnh", "if (_num(o.get(\"qty\")) or 0) > 0]", "if True]"),
    ("lệnh bán cũng thoả BUY", "return str(o.get(\"side\") or \"\").strip().lower() == \"buy\"", "return True"),
    ("alert cả khi không phải phiên chuẩn", "if day == 1:", "if True:"),
    ("không còn nhận phiên chuẩn từ entry_window_date", "if plan_date and str(c.get(\"entry_window_date\") or \"\").strip() == str(plan_date):", "if False:"),
    ("bỏ idempotency (luôn coi là mới)", "new = [f for f in res[\"findings\"] if _key(f) not in sent]", "new = list(res[\"findings\"])"),
    ("ghi state dù Discord lỗi", "if rc1 == 0 and rc2 == 0:", "if True:"),
    ("không chuẩn hoá ticker (case)", "return str(x or \"\").strip().upper()", "return str(x or \"\")"),
    ("deferred trống lý do cũng được chấp nhận", "if not (reason or str(d.get(\"status\") or \"\").strip()):", "if False:"),
    ("bỏ walk ticker khoá khác", "analysed = set(_walk_tickers(la))", "analysed = set()"),
    ("counts.due_today>0 không list vẫn coi sạch", "        if n:\n", "        if False:\n"),
    ("bỏ đối chiếu CSV", "for t in sorted((day1 or set()) - analysed):", "for t in []:"),
    ("lý do hardcode thay vì trích plan", "ev = f\"status={d.get('status')!r}; lý do: {reason[:300]}\"", "ev = 'WAIT_CASH'"),
]


def run_inprocess():
    res = cases(load(MOD))
    npass = sum(1 for _, ok, _ in res if ok)
    for name, ok, det in res:
        print(f"  {'PASS' if ok else 'FAIL'} — {name}" + ("" if ok else f"  [{str(det)[:300]}]"))
    print(f"CASES: {npass} pass / {len(res) - npass} fail")
    if npass != len(res):
        return 1
    src = open(MOD, encoding="utf-8").read()
    dead = 0
    td = tempfile.mkdtemp()
    try:
        for i, (name, a, b) in enumerate(MUTANTS):
            if a not in src:
                print(f"  ❌ MUTANT không áp được (mẫu không còn trong nguồn): {name}")
                return 1
            mp = os.path.join(td, f"mut{i}.py")
            with open(mp, "w", encoding="utf-8") as fh:
                fh.write(src.replace(a, b, 1))
            try:
                mres = cases(load(mp, f"mut{i}"))
                killed = any(not ok for _, ok, _ in mres)
            except Exception:
                killed = True
            dead += killed
            print(f"  {'KILLED  ' if killed else 'SURVIVED'} — mutant: {name}")
    finally:
        shutil.rmtree(td, ignore_errors=True)
    print(f"MUTANTS: {dead}/{len(MUTANTS)} chết")
    return 0 if dead == len(MUTANTS) else 1


def run_cli():
    """CLI thật: exit code, --report-block, tài khoản lệch, --dry-run không phát gì."""
    td = tempfile.mkdtemp()
    ok_all = True
    try:
        p = plan([cand("SSI")], [], [])
        pf = os.path.join(td, "plan_SpaceX_2026-10-26.json")
        json.dump(p, open(pf, "w"))
        nlog = os.path.join(td, "n.log")
        write_exec(os.path.join(td, "n.sh"), f'#!/bin/bash\necho x >> {nlog}\n')
        write_exec(os.path.join(td, "b.sh"), "#!/bin/bash\nexit 0\n")
        env = dict(os.environ, MIKE_LAGCHK_STATE_DIR=os.path.join(td, "st"),
                   MIKE_LAGCHK_NOTIFY=os.path.join(td, "n.sh"), MIKE_LAGCHK_APPEND_EVENT=os.path.join(td, "b.sh"))
        base = [sys.executable, CHECKER, "--account", "SpaceX", "--plan-file", pf, "--no-crosscheck", "--no-dd-gate"]
        r = subprocess.run(base + ["--dry-run", "--report-block"], capture_output=True, text=True, env=env)
        c1 = r.returncode == 2 and "SSI" in r.stdout and not os.path.exists(nlog)
        r = subprocess.run(base + ["--report-block"], capture_output=True, text=True, env=env)
        r2 = subprocess.run(base, capture_output=True, text=True, env=env)
        c2 = r.returncode == 2 and r2.returncode == 2 and len(open(nlog).read().splitlines()) == 1
        r = subprocess.run([sys.executable, CHECKER, "--account", "ZaloPay", "--plan-file", pf], capture_output=True, text=True, env=env)
        c3 = r.returncode == 1
        json.dump(plan([cand("ABC", day=1)], [order("ABC")]), open(pf, "w"))
        r = subprocess.run(base + ["--report-block"], capture_output=True, text=True, env=env)
        c4 = r.returncode == 0 and "nhất quán" in r.stdout
        r = subprocess.run(base + ["--plan-file", os.path.join(td, "khong_co.json")], capture_output=True, text=True, env=env)
        c5 = r.returncode == 1
        for n, c in (("dry-run rc2, in khối, không phát", c1), ("phát 1 lần dù chạy 2 lần", c2),
                     ("account lệch ⇒ rc1", c3), ("plan sạch ⇒ rc0", c4), ("thiếu file ⇒ rc1", c5)):
            print(f"  {'PASS' if c else 'FAIL'} — CLI: {n}")
            ok_all &= bool(c)
    finally:
        shutil.rmtree(td, ignore_errors=True)
    return 0 if ok_all else 1


def run_real_replay():
    """Đo trên plan THẬT (read-only): không crash, ghi số liệu. Bỏ qua nếu không có thư mục plan."""
    try:
        import wc_paths
        d = os.path.join(wc_paths.find_wc_root(__file__), "data", "trade_plans")
    except Exception:
        d = "/home/trido/thanhdt/WorkingClaude/data/trade_plans"
    if not os.path.isdir(d):
        print("  SKIP replay: không có data/trade_plans")
        return 0
    m = load(MOD)
    n = err = nf = 0
    for fn in sorted(os.listdir(d)):
        if not (fn.startswith("plan_") and fn.endswith(".json")) or "_main_" in fn:
            continue
        try:
            p = json.load(open(os.path.join(d, fn)))
            if not isinstance(p, dict) or "account" not in p:
                continue
            r = m.analyze(p, crosscheck=False)
        except Exception as e:
            if isinstance(e, ValueError):
                continue
            err += 1
            print(f"  ❌ replay {fn}: {type(e).__name__}: {e}")
            continue
        n += 1
        nf += bool(r["findings"])
    print(f"  REPLAY: {n} plan thật, {nf} có phát hiện, {err} crash")
    return 1 if err else 0


def run_sender_hook():
    """send_plan_report.sh THẬT (sandbox + --dry-run): khối LAG xuất hiện trong report, lỗi checker
    không im lặng, và KHÔNG chặn gửi (vẫn ra báo cáo)."""
    import wc_paths
    wc = wc_paths.find_wc_root(__file__)
    real = os.path.join(wc, "data", "trade_plans", "plan_SpaceX_2026-08-07.json")
    if not os.path.exists(real):
        print("  SKIP hook: thiếu plan thật 08-07 làm nền")
        return 0
    base_plan = json.load(open(real))
    ok_all = True
    for label, cmd_body, want, notwant in (
            ("checker thật ⇒ khối đỏ SSI trong report", None, ("LAG SpaceX", "SSI", "LAG_BUY_MISSING"), ()),
            ("checker lỗi rc=3 ⇒ 'KHÔNG KIỂM ĐƯỢC' kèm stderr thật", "#!/bin/bash\necho boom-that >&2\nexit 3\n",
             ("KHÔNG KIỂM ĐƯỢC", "boom-that"), ()),
            ("không cấp SEND_PLAN_LAGCHK_CMD trong sandbox ⇒ không có khối", "SKIP", (), ("Cổng nhất quán LAG", "LAG_BUY_MISSING"))):
        td = tempfile.mkdtemp()
        try:
            for sub in ("data/trade_plans", "state"):
                os.makedirs(os.path.join(td, sub))
            os.symlink(os.path.join(wc, "trading_bot"), os.path.join(td, "trading_bot"))
            env = dict(os.environ, SEND_PLAN_WORKDIR_OVERRIDE=td, SEND_PLAN_MARKER_DIR=os.path.join(td, "state", "marker"),
                       MIKE_LAGCHK_STATE_DIR=os.path.join(td, "st"))
            env.pop("SEND_PLAN_LAGCHK_CMD", None)
            if cmd_body is None:
                env["SEND_PLAN_LAGCHK_CMD"] = CHECKER
            elif cmd_body != "SKIP":
                fk = os.path.join(td, "fake.py")
                write_exec(fk, cmd_body.replace("#!/bin/bash", "#!/bin/bash"))
                env["SEND_PLAN_LAGCHK_CMD"] = fk
            exp = subprocess.run([sys.executable, "-c",
                "import datetime as dt; from zoneinfo import ZoneInfo; from trading_bot.vn_market import next_trading_day; "
                "print(next_trading_day(dt.datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).date()))"],
                cwd=wc, capture_output=True, text=True, env=env).stdout.strip()
            pl = json.loads(json.dumps(base_plan))
            pl["plan_date"] = exp
            for c_ in pl["lag_analysis"]["due_today"]:     # ngày chuẩn của ca thật dời sang exp
                c_["entry_window_date"] = exp
            json.dump(pl, open(os.path.join(td, "data", "trade_plans", f"plan_SpaceX_{exp}.json"), "w"), ensure_ascii=False)
            r = subprocess.run(["bash", os.path.join(HERE, "send_plan_report.sh"), "--account", "SpaceX", "--dry-run"],
                               capture_output=True, text=True, env=env, timeout=600)
            out = r.stdout + r.stderr
            c = all(w in out for w in want) and not any(n in out for n in notwant) and "ESCALATE" not in out[:20]
        finally:
            shutil.rmtree(td, ignore_errors=True)
        print(f"  {'PASS' if c else 'FAIL'} — HOOK send_plan_report: {label}")
        if not c:
            print("     ...", [w for w in want if w not in out], [n for n in notwant if n in out], [l for l in out.splitlines() if "PHIÊN CHUẨN" in l or "SSI" in l][:3].__str__().replace("\n", " | "))
        ok_all &= c
    return 0 if ok_all else 1


def main():
    if "--inner" in sys.argv:
        rc = run_inprocess() | run_cli() | run_real_replay() | run_sender_hook()
        print("RESULT:", "PASS" if rc == 0 else "FAIL")
        return rc
    rc = 0
    for label, envmod in (("env -u TZ", lambda e: e.pop("TZ", None)),
                          ("TZ=Pacific/Kiritimati", lambda e: e.__setitem__("TZ", "Pacific/Kiritimati")),
                          ("TZ=America/New_York", lambda e: e.__setitem__("TZ", "America/New_York"))):
        env = dict(os.environ, MIKE_BOT_TEST_MODE="1")
        envmod(env)
        print(f"=== {label} ===")
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--inner"], env=env)
        rc |= r.returncode
    print("TỔNG:", "PASS" if rc == 0 else "FAIL")
    return rc


if __name__ == "__main__":
    sys.exit(main())
