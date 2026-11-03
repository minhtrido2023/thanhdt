# -*- coding: utf-8 -*-
"""Mutation runner cho dd_flag_order_gate_selfcheck.py: mỗi đột biến PHẢI làm selfcheck FAIL.

Chạy: $DNA_PYEXE dd_flag_order_gate_mutation.py   (offline, ~vài giây)
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MUT = [
    ("M1 không chặn mã FLAGGED", "trading_bot/plan.py",
     [('if st == "FLAGGED" and not disc:', 'if st == "FLAGGED" and False:')]),
    ("M2 chặn cả lệnh BÁN", "trading_bot/plan.py",
     [('buys = [o for o in plan.orders if (o.side or "").lower() == "buy" and not _exempt(o)]',
       'buys = [o for o in plan.orders if not _exempt(o)]'),
      ('if ((o.side or "").lower() == "buy" and not _exempt(o)) else None)',
       'if (not _exempt(o)) else None)')]),
    ("M3 bỏ quality_flag", "trading_bot/due_diligence.py",
     [("if qf and qf != DD_FLAG_QUALITY_OK:", "if False:")]),
    ("M4 universe n/a im lặng CLEAN", "trading_bot/due_diligence.py",
     [('if dd.get("in_universe") is None:', "if False:")]),
    ("M5 bỏ miễn DISCRETIONARY", "trading_bot/plan.py",
     [("disc = bk.startswith(DD_FLAG_EXEMPT_PREFIX)", "disc = False")]),
    ("M6 UNKNOWN không báo FAIL_OPEN", "trading_bot/plan.py",
     [('elif st == "UNKNOWN" and not disc:', "elif False:")]),
    ("M7 mọi red_flag đều là cờ", "trading_bot/due_diligence.py",
     [('codes = [c for c in (dd.get("red_flags") or []) if c in RED_FLAG_CODES]',
       'codes = list(dd.get("red_flags") or [])')]),
    ("M8 gỡ dây nối bot_execute", "bot_execute.py",
     [("plan, dd_blocked = filter_dd_flag_orders(plan)", "dd_blocked = []")]),
    ("M9 DD lỗi ⇒ chặn (fail-closed)", "trading_bot/due_diligence.py",
     [('return "UNKNOWN", [], f"DD n/a', 'return "FLAGGED", ["X"], f"DD n/a')]),
    ("M10 PROBE không miễn", "trading_bot/plan.py",
     [('DD_FLAG_EXEMPT_BOOKS = frozenset({"PROBE"})', "DD_FLAG_EXEMPT_BOOKS = frozenset()")]),
    ("M11 PROBE miễn mọi account", "trading_bot/plan.py",
     [('probe_ok = str(getattr(plan, "account", "") or "") in DD_FLAG_PROBE_ACCOUNTS',
       "probe_ok = True")]),
    ("M12 cổng chạy SAU netting (thứ tự vòng 1)", "bot_execute.py",
     [("        plan, dd_blocked = filter_dd_flag_orders(plan)\n", "        dd_blocked = []\n"),
      ("        plan, net_adj = net_offsetting_orders(plan)\n",
       "        plan, net_adj = net_offsetting_orders(plan)\n"
       "        plan, dd_blocked = filter_dd_flag_orders(plan)\n")]),
    ("M14 bỏ miễn PARK", "trading_bot/plan.py",
     [('DD_FLAG_EXEMPT_PARK_BOOKS = frozenset({"PARK", "CUSTOM30V_PARKING"})',
       'DD_FLAG_EXEMPT_PARK_BOOKS = frozenset()')]),
    ("M15 miễn nhầm CAPIT", "trading_bot/plan.py",
     [('DD_FLAG_EXEMPT_PARK_BOOKS = frozenset({"PARK", "CUSTOM30V_PARKING"})',
       'DD_FLAG_EXEMPT_PARK_BOOKS = frozenset({"PARK", "CUSTOM30V_PARKING", "CAPIT"})')]),
    ("M16 miễn PARK theo substring", "trading_bot/plan.py",
     [('return _bk(o) in DD_FLAG_EXEMPT_PARK_BOOKS or', 'return "PARK" in _bk(o) or')]),
    ("M17 chỉ nhận 1 nhãn park (bỏ custom30V_parking)", "trading_bot/plan.py",
     [('frozenset({"PARK", "CUSTOM30V_PARKING"})', 'frozenset({"PARK"})')]),
    ("M13 không gửi tin tóm tắt", "bot_execute.py",
     [("            _notify_dd_flag_summary(p[\"label\"], plan_date, _dd_lines)", "            pass")]),
]
killed = 0
for name, rel, reps in MUT:
    tmp = tempfile.mkdtemp(prefix="ddgate_mut_")
    try:
        shutil.copytree(os.path.join(HERE, "trading_bot"), os.path.join(tmp, "trading_bot"),
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy(os.path.join(HERE, "bot_execute.py"), tmp)
        p = os.path.join(tmp, rel)
        s = open(p, encoding="utf-8").read()
        for a, b in reps:
            assert s.count(a) == 1, f"{name}: anchor không duy nhất/không thấy: {a!r} ({s.count(a)})"
            s = s.replace(a, b)
        open(p, "w", encoding="utf-8").write(s)
        r = subprocess.run([sys.executable, os.path.join(HERE, "dd_flag_order_gate_selfcheck.py")],
                           env=dict(os.environ, DDGATE_CODE_ROOT=tmp), capture_output=True, text=True)
        ok = r.returncode != 0
        killed += ok
        nfail = r.stdout.count("  FAIL  ")
        print(f"  {'KILLED' if ok else 'SURVIVED'}  {name}  (selfcheck rc={r.returncode}, {nfail} FAIL)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
print(f"\n=== mutation: {killed}/{len(MUT)} killed ===")
sys.exit(0 if killed == len(MUT) else 1)
