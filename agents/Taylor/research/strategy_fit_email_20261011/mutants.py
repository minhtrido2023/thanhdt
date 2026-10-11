import subprocess, sys
M = [
 ("M1 bỏ chốt daily-only ở email", "bin/send_report_email.py", 'and "_daily_report_" not in fname', 'and False'),
 ("M2 cổng không chuyển tiếp --attach", "bin/report_delivery_gate.py", 'extra = [arg for path in attach for arg in ("--attach", str(path))]', 'extra = []'),
 ("M3 cổng không chuyển tiếp --attach-note", "bin/report_delivery_gate.py", 'extra += ["--attach-note", attach_note]', 'pass'),
 ("M4 EOD sinh cả cho ngày cũ", "bin/eod_trading_report.sh", '''&& [ "$PLAN_DATE" = "$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)" ]; then''', '; then'),
 ("M5 EOD luôn sinh lại (không dùng lại)", "bin/eod_trading_report.sh", 'if [ ! -s "$dash" ] && [', 'if true && ['),
 ("M6 EOD bỏ timeout", "bin/eod_trading_report.sh", 'out="$(timeout -k 5 "$tmo" "${DNA_PYEXE', 'out="$("${DNA_PYEXE'),
 ("M7 EOD lỗi sinh ⇒ trả rc≠0 (chặn email)", "bin/eod_trading_report.sh", '''sinh lỗi: $last")
      return 0''', '''sinh lỗi: $last")
      return 1'''),
 ("M8 EOD nuốt lỗi thật (ghi chú cố định)", "bin/eod_trading_report.sh", 'sinh lỗi: $last")', 'sinh lỗi")'),
 ("M9 sweep kèm cả weekly", "bin/check_report_cadence.sh", '=~ _daily_report_([0-9]{4}-[0-9]{2}-[0-9]{2})\\.md$', '=~ _report_.*([0-9]{4}-[0-9]{2}-[0-9]{2})\\.md$'),
 ("M10 sweep kèm cả file rỗng/không có", "bin/check_report_cadence.sh", '&& [ -s "$ROOT/reports/dashboard/strategy_fit_${BASH_REMATCH[1]}.html" ]; then', '; then'),
 ("M11 email chết khi file kèm thiếu", "bin/send_report_email.py", '''                continue
            extra = MIMEApplication''', '''                sys.exit(4)
            extra = MIMEApplication'''),
 ("M12 ghi chú chèn vào file .md kèm (đổi artifact)", "bin/send_report_email.py", 'html_body = render_html(body_md, title,', 'open(args.report_path, "w", encoding="utf-8").write(body_md); html_body = render_html(body_md, title,'),
 ("M13 dashboard tmp dùng chung", "bin/strategy_fit_dashboard.py", 'tmp = f"{path}.{os.getpid()}.tmp"', 'tmp = path + ".tmp"'),
 ("M14 EOD gộp stderr+stdout (lỗi thật bị dòng stdout che)", "bin/eod_trading_report.sh", '2>&1 >&3)"; rc=$?; } 3>&1', '2>&1)"; rc=$?; }'),
]
killed = 0
for name, f, a, b in M:
    s = open(f, encoding="utf-8").read()
    if s.count(a) != 1:
        print(f"NOAPPLY {name} (count={s.count(a)})"); continue
    open(f, "w", encoding="utf-8").write(s.replace(a, b))
    try:
        p = subprocess.run([sys.executable, "bin/strategy_fit_email_attach_selfcheck.py"], capture_output=True, text=True)
    finally:
        open(f, "w", encoding="utf-8").write(s)
    fails = [l[7:60] for l in p.stdout.splitlines() if l.startswith("[FAIL]")]
    dead = p.returncode != 0 and bool(fails)
    killed += dead
    print(f"{'CHẾT ' if dead else 'SỐNG '} {name} → {len(fails)} ca đỏ: {fails[:3]}")
print(f"mutants: {killed}/{len(M)} chết")
