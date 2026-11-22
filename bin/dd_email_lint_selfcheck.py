#!/usr/bin/env python3
"""Selfcheck lint của ~/.claude/skills/dd-investor-report/scripts/send_dd_report_email.py (A6).
Import bằng importlib theo đường dẫn tuyệt đối. Không gửi email, không đọc credential.
Chạy: env -u TZ python3 bin/dd_email_lint_selfcheck.py ; TZ=Pacific/Kiritimati python3 bin/dd_email_lint_selfcheck.py"""
import importlib.util, json, os, subprocess, sys, tempfile

SK = os.path.expanduser("~/.claude/skills/dd-investor-report/scripts/send_dd_report_email.py")
sp = importlib.util.spec_from_file_location("sdr", SK)
m = importlib.util.module_from_spec(sp)
sp.loader.exec_module(m)

fails = []
def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  [{extra}]" if (extra and not cond) else ""))
    if not cond:
        fails.append(name)

d = tempfile.mkdtemp()
ledger = os.path.join(d, "ledger.json")
def entry(t, rev, low, c, high, sf="CONFIRMED", dd="2026-11-20", **kw):
    e = {"ticker": t, "dd_date": dd, "rev": rev, "zone_low": low, "center": c, "zone_high": high, "skeptic_final": sf,
         "center_alt": None, "center_range": None}
    e.update(kw); return e
json.dump({"entries": [entry("AAA", 1, 40000, 50000, 60000), entry("AAA", 2, 41000, 52000, 63000),
                       entry("BBB", 1, 8000, 10000, 12000, sf="FIXED_UNVERIFIED")]}, open(ledger, "w"))

def run(name, text, subject=None):
    p = os.path.join(d, name); open(p, "w", encoding="utf-8").write(text)
    return m.lint_report(p, text, subject, ledger_path=ledger)

CLEAN = "# AAA — báo cáo\n\n| Vùng giá trị hợp lý | **41.000 – 63.000 đ** | Tâm | **≈52.000 đ** |\n\nNội dung trung dung. R3 = rating. Tâm +2,2% khi lãi đổi.\n"
v, w = run("AAA_DD_investor_report_20261120.md", CLEAN)
check("sạch: 0 vi phạm", v == [], v)
check("sạch: không cảnh báo", w == [], w)

# luật 18: từng cụm
for phrase in ["BẢN ĐÍNH CHÍNH", "thay bản gửi trước", "trước đây", "đã sửa", "sai sót", "vòng 2", "bản r4", "kết luận đổi từ A sang B", "lỗi phương pháp"]:
    v, _ = run("AAA_DD_investor_report_20261120.md", CLEAN + f"\nCâu {phrase} ở đây.\n")
    check(f"L18 bắt '{phrase}'", any("LUAT18_NHAC_LOI" in x for x in v), v)
v, _ = run("AAA_DD_investor_report_20261120.md", CLEAN + "\nRating R3 và đường rn3 không phải vòng.\n")
check("L18 không bắt 'R3' hoa/'rn3'", not any("LUAT18" in x for x in v), v)
v, _ = run("AAA_DD_investor_report_20261120.md", CLEAN, subject="[ĐÍNH CHÍNH 2] AAA")
check("L18 bắt subject", any(x.startswith("subject:") and "LUAT18" in x for x in v), v)

# tên nội bộ
for phrase in ["Taylor", "Bobby", "Mike", "Livermore", "skeptic", "agents/Taylor", "kb/x.json", "build_report.py", "Taylor_20261122_124816", "QUALIFY", "NON", "fear-buy", "discretionary sleeve", "SpaceX"]:
    v, _ = run("AAA_DD_investor_report_20261120.md", CLEAN + f"\nGhi chú {phrase} ở đây.\n")
    check(f"NỘI BỘ bắt '{phrase}'", any("TEN_NOI_BO" in x for x in v), v)
v, _ = run("AAA_DD_investor_report_20261120.md", CLEAN + "\nCông ty non trẻ, nonstop, mike nhỏ.\n")
check("NỘI BỘ không bắt 'non'/'mike' thường", not any("TEN_NOI_BO" in x for x in v), v)

# đối chiếu sổ
v, _ = run("AAA_DD_investor_report_20261120.md", CLEAN.replace("52.000", "50.000"))
check("MD↔sổ: tâm cũ (rev1 50.000) bị bắt vì sổ rev cao nhất = 52.000", any("MD_LEDGER_MISMATCH" in x and "tâm" in x for x in v), v)
v, _ = run("AAA_DD_investor_report_20261120.md", CLEAN.replace("41.000 – 63.000", "40.000 – 60.000"))
check("MD↔sổ: vùng cũ bị bắt", any("MD_LEDGER_MISMATCH" in x and "vùng" in x for x in v), v)
v, _ = run("AAA_DD_investor_report_20261120.md", CLEAN.replace("**41.000 – 63.000 đ**", "**41,0–63,0k**").replace("≈52.000 đ", "≈52,0k"))
check("MD↔sổ: định dạng 'k' khớp, không báo giả", v == [], v)
v, _ = run("AAA_DD_investor_report_20261120.md", CLEAN.replace("52.000 đ", "52.700 đ"))
check("MD↔sổ: lệch 1,3% (<3%) không báo", v == [], v)
v, w = run("AAA_DD_investor_report_20261120.md", "# AAA\nTâm khoảng 2026 và +1.316 đ/cp\n")
check("MD↔sổ: năm/số có dấu không bị coi là tâm", not any("MISMATCH" in x for x in v), v)
v, w = run("ZZZ_DD_investor_report_20261120.md", CLEAN)
check("mã không có trong sổ: cảnh báo, không lỗi", v == [] and any("LEDGER_MISSING" in x for x in w), (v, w))
v, w = run("BBB_DD_investor_report_20261120.md", "# BBB\n| Vùng | 8.000 – 12.000 đ | Tâm | 10.000 đ |\n")
check("skeptic_final≠CONFIRMED: chỉ cảnh báo", v == [] and any("SKEPTIC_NOT_CONFIRMED" in x for x in w), (v, w))
v, w = run("AAA_DD_investor_report_20261120.md", CLEAN)
check("skeptic CONFIRMED: không cảnh báo skeptic", not any("SKEPTIC" in x for x in w), w)

# rc / chế độ
p = os.path.join(d, "AAA_DD_investor_report_20261120.md")
bad = CLEAN + "\nBản đính chính.\n"
open(p, "w", encoding="utf-8").write(bad)
m.LEDGER_PATH = ledger
orig = m.lint_report
m.lint_report = lambda *a, **k: orig(a[0], a[1], a[2], ledger_path=ledger)
check("rc dry-run có vi phạm = 3", m.run_lint(p, bad, None, True) == 3)
check("rc gửi thật + DD_LINT_BLOCK=False = 0 (chỉ cảnh báo)", m.run_lint(p, bad, None, False) == 0)
m.DD_LINT_BLOCK = True
check("rc gửi thật + DD_LINT_BLOCK=True = 3", m.run_lint(p, bad, None, False) == 3)
m.DD_LINT_BLOCK = False
check("rc sạch = 0", m.run_lint(p, CLEAN, None, True) == 0)
check("hằng DD_LINT_BLOCK mặc định False", importlib.util.module_from_spec(sp) is not None and "DD_LINT_BLOCK = False" in open(SK).read())

# CLI --dry-run thật (không gửi): cần PNG? dùng md không ảnh. Chỉ kiểm rc + 'DRY-RUN'
open(p, "w", encoding="utf-8").write(bad)
env = {k: v for k, v in os.environ.items()}
r = subprocess.run([sys.executable, SK, p, "--dry-run"], capture_output=True, text=True, env=env)
check("CLI --dry-run có vi phạm: rc=3, in LINT, không gửi", r.returncode == 3 and "LINT " in r.stdout and "ĐÃ GỬI" not in r.stdout, (r.returncode, r.stdout[-300:], r.stderr[-300:]))
r = subprocess.run([sys.executable, SK, p, "--dry-run", "--skip-lint"], capture_output=True, text=True, env=env)
check("CLI --skip-lint ghi cảnh báo, rc=0", r.returncode == 0 and "--skip-lint" in r.stdout, (r.returncode, r.stdout[-300:], r.stderr[-300:]))

print("\nKẾT QUẢ:", "OK" if not fails else f"{len(fails)} FAIL: {fails}")
sys.exit(1 if fails else 0)
