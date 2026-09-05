#!/usr/bin/env python3
"""tz_anchor_gate_selfcheck.py — selfcheck cho bin/tz_anchor_gate.py (coding_guidelines §16).

Kiểm CẢ HAI CHIỀU, đúng yêu cầu khi bật gate:
  - RED   : code dùng `datetime.now()` trần / `date.today()` PHẢI bị chặn.
  - CONTROL: code đã neo TZ (`datetime.now(_ICT)`, `datetime.now(ZoneInfo(...))`,
             `datetime.now(timezone.utc)` — bước 1 của ICT-anchor pattern) PHẢI qua.

Ca ĐẮT NHẤT không phải fixture bịa: lấy NGUYÊN VĂN 4 file tại `20bf2f20^` / `b26008a6^` (bản
ĐÚNG LÚC 5 finding §16 của code-quality-weekly 2026-08-30 còn sống) và bản đã vá. Gate phải bắt
đúng SỐ DÒNG mà commit message nêu, và im ở những dòng đó sau khi vá. Không có git (sandbox) →
SKIP có báo, KHÔNG âm thầm PASS.

§16 tự áp lên chính nó: `--all-tz` chạy lại toàn bộ suite dưới `env -u TZ` và một TZ lạ
(America/New_York), đòi output GIỐNG HỆT — gate là phân tích tĩnh, kết quả không được đổi theo
đồng hồ của người chạy. Đây là đúng phép thử đã bắt được lớp lỗi này ngay từ đầu.

Sandbox: mọi ca end-to-end chạy trong mkdtemp qua MIKE_TZ_GATE_ROOT + MIKE_TZ_GATE_BASELINE —
KHÔNG file production nào bị ghi. Có assertion sha256 chứng minh việc đó (không dựa vào
`finally`, thứ không sống qua SIGKILL).
"""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE_PROD = os.path.join(ROOT, "bin", "tz_anchor_gate.py")
PROD_BASELINE = os.path.join(ROOT, "kb", "tz_anchor_baseline.json")


def _resolve_target(env_target, mutation_flag, prod=None, varname="MIKE_TZ_GATE_TARGET"):
    """Từ chối override target nếu thiếu cờ mutation — nếu không 'ALL PASS' có thể là PASS GIẢ
    trên một bản sao, trong khi file production chưa hề được đọc."""
    prod = prod or GATE_PROD
    if not env_target or env_target == prod:
        return prod
    if not mutation_flag:
        raise SystemExit(
            f"❌ {varname} được đặt mà KHÔNG có MIKE_TZ_GATE_MUTATION=1 — selfcheck sẽ "
            f"kiểm {env_target} chứ KHÔNG phải {prod}. Bỏ biến này hoặc chạy qua --mutations."
        )
    return env_target


GATE_PATH = _resolve_target(
    os.environ.get("MIKE_TZ_GATE_TARGET"), os.environ.get("MIKE_TZ_GATE_MUTATION") == "1"
)

FAILED = []


TOTAL = []


def check(name, ok, detail=""):
    TOTAL.append(name)
    if ok:
        print(f"  ✓ {name}")
    else:
        FAILED.append(name)
        print(f"  ❌ {name}{('  — ' + detail) if detail else ''}")


def _load_gate():
    spec = importlib.util.spec_from_file_location("tz_gate", GATE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


# ── 1. Detector: RED — mọi cách viết KHÔNG neo TZ đang có thật trong 2 repo ────────────────
RED_CASES = [
    ("datetime.now() (from datetime import datetime)", "from datetime import datetime\nx = datetime.now()\n"),
    ("datetime.datetime.now() (import datetime)", "import datetime\nx = datetime.datetime.now()\n"),
    ("dt.datetime.now() (import datetime as dt)", "import datetime as dt\nx = dt.datetime.now()\n"),
    ("_dt.datetime.now() (alias _dt)", "import datetime as _dt\nx = _dt.datetime.now()\n"),
    ("date.today()", "from datetime import date\nx = date.today()\n"),
    ("datetime.date.today()", "import datetime\nx = datetime.date.today()\n"),
    ("_dt.date.today()", "import datetime as _dt\nx = _dt.date.today()\n"),
    ("datetime.today() (naive local, biến thể ít gặp)", "from datetime import datetime\nx = datetime.today()\n"),
    ("nằm trong f-string: f'{datetime.now():%H:%M}'", "from datetime import datetime\ns = f'{datetime.now():%H:%M}'\n"),
    # arch-review 2026-08-30 F8 — 4 dạng trước bản vá LỌT qua điều kiện (b)/(c).
    ("alias import: from datetime import datetime as dtm", "from datetime import datetime as dtm\nx = dtm.now()\n"),
    ("alias import: from datetime import date as d", "from datetime import date as d\nx = d.today()\n"),
    ("datetime.now(None) — có arg nhưng vô hiệu", "from datetime import datetime\nx = datetime.now(None)\n"),
    ("datetime.now(tz=None)", "from datetime import datetime\nx = datetime.now(tz=None)\n"),
]

# ── 2. Detector: CONTROL — đã neo TZ, hoặc ngoài phạm vi §16 ⇒ PHẢI im ────────────────────
CONTROL_CASES = [
    ("datetime.now(_ICT)", "from datetime import datetime\nx = datetime.now(_ICT)\n"),
    ('datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))',
     'from datetime import datetime\nfrom zoneinfo import ZoneInfo\nx = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))\n'),
    ("datetime.now(tz=ICT) (keyword)", "from datetime import datetime\nx = datetime.now(tz=ICT)\n"),
    ("datetime.now(timezone.utc) — bước 1 của ICT-anchor, PHẢI cho qua",
     "from datetime import datetime, timezone\nx = datetime.now(timezone.utc)\n"),
    ("ICT-anchor đầy đủ: (now(utc)+7h).date()",
     "from datetime import datetime, timezone, timedelta\nx = (datetime.now(timezone.utc) + timedelta(hours=7)).date()\n"),
    ("call xuống dòng: now(\\n timezone.utc\\n) — regex đếm sai, AST đúng",
     "import datetime\nx = datetime.datetime.now(\n    datetime.timezone.utc,\n)\n"),
    ("receiver khác: okf.today()", "x = okf.today()\n"),
    ("ngoài phạm vi user duyệt: pd.Timestamp.now()", "import pandas as pd\nx = pd.Timestamp.now()\n"),
    ("ngoài phạm vi: datetime.utcnow() (naive UTC, không phụ thuộc TZ host)",
     "from datetime import datetime\nx = datetime.utcnow()\n"),
]


# ── 2b. KNOWN GAP — gate KHÔNG bắt, và điều đó được GHI NHẬN, không phải "đúng" ────────────
# arch-review 2026-08-30 F8: trước đây `f = datetime.now` nằm trong CONTROL, tức selfcheck
# khẳng định "im ở đây là hành vi đúng". Sai — nó là lỗ hổng. Ghi ở mục này để bản sau ai bịt
# được thì biết phải chuyển sang RED, và để không ai đọc nhầm im lặng thành bảo đảm.
KNOWN_GAPS = [
    ("tham chiếu rồi gọi: n = datetime.now; n()", "from datetime import datetime\nn = datetime.now\nx = n()\n"),
    ("datetime.fromtimestamp(t) — naive host-local, chưa canh", "from datetime import datetime\nx = datetime.fromtimestamp(0)\n"),
    ("date.fromtimestamp(t)", "from datetime import date\nx = date.fromtimestamp(0)\n"),
    ("datetime.now(*args) — có arg nên qua (c)", "from datetime import datetime\nx = datetime.now(*a)\n"),
]


# ── 1b. Detector RULE 2 (2026-09-05): tdays() thiếu vn_holidays trong hàm bao quanh ────────
# RED — chính hình dạng sự cố thật (macro_healthcheck.py trước commit 96ebd124): gọi hàm tên
# chứa "tdays" mà hàm bao quanh không hề tham chiếu lễ VN ở đâu cả.
RED_CASES_TDAYS = [
    ("tdays() trần trong def, không marker",
     "def tdays(a, r=None):\n    return 1\ndef use(a):\n    return tdays(a)\n"),
    ("tdays() trần ở module top-level, không marker",
     "def tdays(a):\n    return 1\nx = tdays(1)\n"),
    ("TDAYS() hoa toàn bộ vẫn bắt — khớp tuyệt đối KHÔNG phân biệt hoa/thường",
     "def TDAYS(a):\n    return 1\ndef use(a):\n    return TDAYS(a)\n"),
    ("gọi qua attribute: obj.tdays(x)",
     "def use(obj, x):\n    return obj.tdays(x)\n"),
    ("scope LỒNG: is_holiday ở hàm NGOÀI không cứu hàm lồng bên trong (scope riêng)",
     "def outer(d):\n    def inner(a):\n        return tdays(a)\n"
     "    from trading_bot.vn_market import is_holiday\n    is_holiday(d)\n    return inner(d)\n"),
    # arch-review vòng 1 RULE-2 (F1, killer): ân xá theo SCOPE cho `vn_holidays=`/`is_holiday`
    # khiến MỘT lệnh gọi anchored che mất MỌI lệnh gọi tdays() TRẦN khác trong cùng hàm/module —
    # đúng hình dạng khiến gate mù với chính file gây sự cố (macro_healthcheck.py). 4 ca dưới
    # ghim đúng lỗ đã vá (per-call vn_holidays= + exact-match is_holiday), không phải suy diễn.
    ("F1: anchored + tdays() TRẦN khác trong CÙNG def — call anchored không được che call trần",
     "def f(a, kind):\n    y = tdays(a, vn_holidays=(kind == \"trading_vn\"))\n"
     "    z = tdays(a)\n    return y, z\n"),
    ("F1: anchored + tdays() TRẦN khác ở CÙNG module top-level",
     "def helper(a, kind):\n    return tdays(a, vn_holidays=(kind == \"trading_vn\"))\nz = tdays(1)\n"),
    ("F1: identifier chỉ CHỨA chuỗi con 'is_holiday' (vd `_vn_is_holiday`) KHÔNG còn là marker "
     "thật — khớp phải TUYỆT ĐỐI, không phải substring",
     "def f(d):\n    _vn_is_holiday = None\n    return tdays(d)\n"),
    ("scope LỒNG hướng NGƯỢC (M7b): marker is_holiday nằm TRONG def lồng TRỰC TIẾP ở top-level "
     "scope.body KHÔNG được phép cứu call tdays() trần ở scope NGOÀI nó — pin bộ lọc top-level "
     "(arch-review vòng 2 RULE-2 gốc)",
     "def outer(d):\n    z = tdays(d)\n"
     "    def inner():\n        from trading_bot.vn_market import is_holiday\n        return is_holiday(d)\n"
     "    return z, inner()\n"),
    ("scope LỒNG hướng NGƯỢC (M7): marker is_holiday nằm TRONG def lồng bên TRONG 1 compound "
     "statement (if), không phải statement top-level trực tiếp của scope.body, để pin RIÊNG bộ "
     "lọc bên trong walk() (arch-review vòng 3, B1: ca top-level chỉ pin được bộ lọc top-level — "
     "xoá RIÊNG bộ lọc trong walk() không lộ ra nếu chỉ có ca top-level, đã đo: 129/129 vẫn PASS)",
     "def outer(d):\n    if True:\n        z = tdays(d)\n"
     "    if True:\n        def inner():\n            from trading_bot.vn_market import is_holiday\n"
     "            return is_holiday(d)\n        inner()\n"),
    # arch-review vòng 3, B2: SCOPE_BOUNDARY_TYPES trước đây chỉ có FunctionDef/AsyncFunctionDef —
    # marker is_holiday trong lambda/comprehension/class LỒNG bên trong hàm rò ra ngoài, ân xá SAI
    # 1 call tdays() trần khác. 4 ca dưới đúng hình dạng thực tế "hols = [d for d in ds if
    # is_holiday(d)]" rồi "age = tdays(as_of)" trần ngay sau — bị lọt trước khi mở rộng bộ lọc.
    ("B2: is_holiday trong LAMBDA lồng bên trong hàm không được cứu call tdays() trần khác",
     "def f(d, ys):\n    cb = lambda x: is_holiday(x)\n    return tdays(d)\n"),
    ("B2: is_holiday trong LIST COMPREHENSION không được cứu call tdays() trần khác",
     "def f(d, ys):\n    xs = [is_holiday(y) for y in ys]\n    return tdays(d)\n"),
    ("B2: is_holiday trong GENERATOR EXPRESSION không được cứu call tdays() trần khác",
     "def f(d, ys):\n    xs = (is_holiday(y) for y in ys)\n    return tdays(d)\n"),
    ("B2: is_holiday trong method của 1 CLASS lồng bên trong hàm không được cứu call tdays() trần",
     "def f(d):\n    class C:\n        def m(self):\n            return is_holiday(d)\n    return tdays(d)\n"),
    ("B2: is_holiday trong method của 1 class Ở MODULE TOP-LEVEL không được cứu call tdays() "
     "trần khác cũng ở module top-level",
     "class C:\n    def m(self):\n        return is_holiday(1)\nz = tdays(1)\n"),
    ("B3: `is_holiday = None` (Store, không phải Load) KHÔNG được tính là marker thật",
     "def f(d):\n    is_holiday = None\n    return tdays(d)\n"),
    ("B3: `del is_holiday` (Del, không phải Load) KHÔNG được tính là marker thật",
     "def f(d):\n    is_holiday = 1\n    del is_holiday\n    return tdays(d)\n"),
]

# CONTROL — có dấu hiệu nhận-biết-lễ-VN trong CHÍNH hàm bao quanh ⇒ PHẢI im.
CONTROL_CASES_TDAYS = [
    ("vn_holidays=True ngay tại lệnh gọi",
     "def f(a):\n    return tdays(a, vn_holidays=True)\n"),
    ("vn_holidays=False ngay tại lệnh gọi — vẫn PASS, có tham chiếu là đủ (ca us_market cố ý Mon-Fri)",
     "def f(a):\n    return tdays(a, vn_holidays=False)\n"),
    ("vn_holidays=<biểu thức> — ca thật macro_healthcheck.py add_source() dòng 100",
     'def add_source(a, kind="trading"):\n    return tdays(a, vn_holidays=(kind == "trading_vn"))\n'),
    ("is_holiday tham chiếu Ở NƠI KHÁC trong CÙNG hàm (không phải trên chính lệnh gọi)",
     "def f(d):\n    from trading_bot.vn_market import is_holiday\n    if not is_holiday(d):\n        pass\n    return tdays(d)\n"),
    ("is_holiday dạng ATTRIBUTE (vn_market.is_holiday(d)), không phải import trực tiếp — pin "
     "riêng nhánh ast.Attribute (arch-review vòng 1 RULE-2, X4: bản trước chỉ CONTROL bằng "
     "Name nên xoá riêng nhánh Attribute vẫn PASS 122/122)",
     "import trading_bot.vn_market as vn_market\ndef f(d):\n    if not vn_market.is_holiday(d):\n        pass\n    return tdays(d)\n"),
    ("hàm bao quanh có tham số vn_holidays trong chữ ký, CHUYỂN TIẾP THẬT vào lệnh gọi "
     "(forward qua tham số vị trí) — khác ca KNOWN GAP bên dưới (khai báo rồi KHÔNG dùng)",
     "def f(d, vn_holidays=False):\n    return tdays(d, vn_holidays)\n"),
    ("np.busday_count trần — KHÔNG thuộc phạm vi rule 2 (chữ ký chỉ bắt tên KHỚP TUYỆT ĐỐI 'tdays')",
     "def f(a, b):\n    return np.busday_count(a, b)\n"),
    # Regression THẬT (2026-09-05): bản đầu dùng "chứa chuỗi con" tự bắt NHẦM chính hàm/test của
    # module này khi chạy --scan thật lần đầu trên 2 repo. Khớp tuyệt đối phải PASS 2 ca này.
    ("tên hàm chứa 'tdays' làm HẬU TỐ NGỮ NGHĨA KHÁC (tdays_violations) — KHÔNG phải call đếm ngày",
     "def tdays_violations(a):\n    return 1\ndef use(a):\n    return tdays_violations(a)\n"),
    ("tên hàm chứa 'tdays' dạng test_*_tdays — cùng lớp false-positive vừa đo được",
     "def test_historical_tdays(a):\n    return 1\ndef use(a):\n    return test_historical_tdays(a)\n"),
]

KNOWN_GAPS_TDAYS = [
    ("alias reimport: from x import tdays as t; t(a) — tên sau alias không còn khớp 'tdays'",
     "def f(a):\n    from x import tdays as t\n    return t(a)\n"),
    ("tham chiếu rồi gọi: f = tdays; f(a)", "def g(a):\n    f = tdays\n    return f(a)\n"),
    ("biến thể tên get_tdays/calc_tdays_age — khớp tuyệt đối cố ý KHÔNG bắt (đổi lấy loại bỏ "
     "false-positive tự-tham-chiếu tdays_violations/test_*_tdays, xem docstring đầu file)",
     "def get_tdays(a):\n    return 1\ndef use(a):\n    return get_tdays(a)\n"),
    ("_scope_has_vn_holidays_param CHỈ kiểm KHAI BÁO, KHÔNG kiểm CHUYỂN TIẾP thật (arch-review "
     "vòng 2 RULE-2, R2): tham số `vn_holidays` khai báo rồi KHÔNG dùng ở lệnh gọi vẫn PASS",
     "def f(a, vn_holidays=False):\n    return tdays(a)\n"),
]


def test_detector_tdays(gate, tmp):
    print("[1b] Detector RULE 2 (tdays/holiday) — RED (phải bị bắt)")
    for name, src in RED_CASES_TDAYS:
        p = _write(os.path.join(tmp, "det2", "f.py"), src)
        check(name, len(gate.tdays_violations(p)) >= 1, f"hits={gate.tdays_violations(p)}")
    print("[2b'] Detector RULE 2 — CONTROL (phải im)")
    for name, src in CONTROL_CASES_TDAYS:
        p = _write(os.path.join(tmp, "det2", "f.py"), src)
        check(name, gate.tdays_violations(p) == [], f"hits={gate.tdays_violations(p)}")
    print("[2c] KNOWN GAP RULE 2 — gate còn hở, ghi nhận chứ không tuyên bố là đúng")
    for name, src in KNOWN_GAPS_TDAYS:
        p = _write(os.path.join(tmp, "det2", "f.py"), src)
        state = "vẫn hở" if gate.tdays_violations(p) == [] else "ĐÃ BỊT — chuyển ca này sang RED_CASES_TDAYS"
        print(f"  · {name}: {state}")


def test_detector(gate, tmp):
    print("[1] Detector — RED (phải bị bắt)")
    for name, src in RED_CASES:
        p = _write(os.path.join(tmp, "det", "f.py"), src)
        check(name, len(gate.violations(p)) >= 1, f"violations={gate.violations(p)}")
    print("[2] Detector — CONTROL (phải im)")
    for name, src in CONTROL_CASES:
        p = _write(os.path.join(tmp, "det", "f.py"), src)
        check(name, gate.violations(p) == [], f"violations={gate.violations(p)}")
    print("[2b] KNOWN GAP — gate còn hở, ghi nhận chứ không tuyên bố là đúng")
    for name, src in KNOWN_GAPS:
        p = _write(os.path.join(tmp, "det", "f.py"), src)
        state = "vẫn hở" if gate.violations(p) == [] else "ĐÃ BỊT — chuyển ca này sang RED_CASES"
        print(f"  · {name}: {state}")


# ── 3. Ca THẬT: 5 finding §16 của code-quality-weekly 2026-08-30 ───────────────────────────
HIST = [
    # (repo_dir, commit, path_trong_commit, tên file tạm, các dòng commit message nêu)
    ("/home/trido/thanhdt", "20bf2f20", "WorkingClaude/deploy_golive_dt5g_v4/golive_recommend_v23.py",
     "golive_recommend_v23.py", [85, 1216]),
    ("/home/trido/thanhdt", "20bf2f20", "WorkingClaude/dna_report.py", "dna_report.py", [69]),
    (ROOT, "b26008a6", "agents/Taylor/anomaly_scan.py", "anomaly_scan.py", [379]),
    (ROOT, "b26008a6", "agents/Taylor/insider_flags.py", "insider_flags.py", [231]),
]


def _git_show(repo, rev, path, dest):
    r = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"],
                       capture_output=True, text=True, check=False)
    if r.returncode != 0:
        return None
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(r.stdout)
    return dest


def test_historical(gate, tmp):
    print("[3] Ca THẬT — 5 finding §16 ngày 2026-08-30 (bản TRƯỚC vá phải bị bắt, SAU vá phải im)")
    d = os.path.join(tmp, "hist")
    os.makedirs(d, exist_ok=True)
    for repo, commit, path, fname, lines in HIST:
        before = _git_show(repo, commit + "^", path, os.path.join(d, "before_" + fname))
        after = _git_show(repo, commit, path, os.path.join(d, "after_" + fname))
        if before is None or after is None:
            check(f"{fname} — git không truy được {commit}", False, "SKIP-KHÔNG-ÂM-THẦM-PASS")
            continue
        hit_before = {ln for ln, _ in gate.violations(before)}
        hit_after = {ln for ln, _ in gate.violations(after)}
        check(f"{fname}: bắt được dòng {lines} ở bản TRƯỚC vá",
              set(lines).issubset(hit_before), f"bắt được {sorted(hit_before)}")
        check(f"{fname}: im ở dòng {lines} sau khi vá",
              not (set(lines) & hit_after), f"còn bắt {sorted(hit_after & set(lines))}")


# Ca THẬT RULE 2: macro_healthcheck.py trước/sau commit 96ebd124 (sự cố macro_health=FAILED
# giả 2026-09-04, kb/incidents/2026-09/2026-09-04-macro-health-failed-holiday-tdays.md). Bản
# TRƯỚC vá có 2 call-site tdays() không holiday-aware (dòng 73 trong add_source(), dòng 233
# module top-level); bản SAU vá có 3 call-site ĐÃ holiday-aware (dòng 70 def, 100 add_source(),
# 265 module top-level) — 3 PASS/2 FLAG là ground-truth Mike giao khi duyệt rule này.
HIST_TDAYS = [
    ("/home/trido/thanhdt", "96ebd124", "WorkingClaude/macro_healthcheck.py",
     "macro_healthcheck.py", [73, 233]),
]


def test_historical_tdays(gate, tmp):
    print("[3b] Ca THẬT RULE 2 — macro_health=FAILED giả 2026-09-04 (commit 96ebd124)")
    d = os.path.join(tmp, "hist_tdays")
    os.makedirs(d, exist_ok=True)
    for repo, commit, path, fname, lines in HIST_TDAYS:
        before = _git_show(repo, commit + "^", path, os.path.join(d, "before_" + fname))
        after = _git_show(repo, commit, path, os.path.join(d, "after_" + fname))
        if before is None or after is None:
            check(f"{fname} — git không truy được {commit}", False, "SKIP-KHÔNG-ÂM-THẦM-PASS")
            continue
        hit_before = {ln for ln, _ in gate.tdays_violations(before)}
        hit_after = {ln for ln, _ in gate.tdays_violations(after)}
        check(f"{fname}: bắt được đúng dòng {lines} ở bản TRƯỚC vá (2 FLAG)",
              hit_before == set(lines), f"bắt được {sorted(hit_before)}")
        check(f"{fname}: im HOÀN TOÀN sau khi vá (3 PASS: def dòng 70 không phải call, "
              "call dòng 100+265 đều có vn_holidays)",
              hit_after == set(), f"còn bắt {sorted(hit_after)}")

        # F1 (arch-review vòng 1, killer): bản trước ân xá theo SCOPE khiến file THẬT này
        # no-op ngay cả khi dòng 100 bị REVERT về đúng bug SEV1 gốc (vì vn_holidays=/is_holiday
        # khác trong cùng scope vẫn sống). Regenerate bản AFTER với dòng 100 revert thủ công —
        # đây là bằng chứng trực tiếp trên FILE THẬT, không phải fixture tổng hợp.
        with open(after, encoding="utf-8") as fh:
            after_src = fh.read()
        reverted = after_src.replace(
            'age = tdays(as_of, vn_holidays=(kind == "trading_vn"))', "age = tdays(as_of)")
        check(f"{fname}: dòng 100 REVERT lại đúng bug SEV1 gốc — regenerate build đã đổi nội dung",
              reverted != after_src, "replace() không khớp — kiểm lại chuỗi nguồn dòng 100")
        reverted_path = os.path.join(d, "reverted_" + fname)
        with open(reverted_path, "w", encoding="utf-8") as fh:
            fh.write(reverted)
        hit_reverted = {ln for ln, _ in gate.tdays_violations(reverted_path)}
        check(f"{fname}: F1 — dòng 100 revert về bug SEV1 gốc PHẢI bị FLAG (không được ân xá "
              "theo scope bởi vn_holidays=/is_holiday khác còn sống trong cùng file)",
              100 in hit_reverted, f"bắt được {sorted(hit_reverted)} (mong đợi có 100)")


# ── 4. End-to-end: ratchet + escape hatch + exclude, chạy qua CLI trong sandbox ────────────
def _run(sandbox, baseline, files, env_extra=None, prefix=None):
    env = dict(os.environ)
    env["MIKE_TZ_GATE_SELFCHECK"] = "1"
    env["MIKE_TZ_GATE_ROOT"] = sandbox
    env["MIKE_TZ_GATE_BASELINE"] = baseline
    env.pop("MIKE_TZ_GATE", None)
    env.pop("MIKE_TZ_GATE_ROOTS", None)
    env.update(env_extra or {})
    r = subprocess.run([sys.executable, GATE_PATH] + (prefix or []) + files,
                       capture_output=True, text=True, env=env, cwd=sandbox, check=False)
    return r.returncode, r.stdout + r.stderr


BARE = "from datetime import datetime\nx = datetime.now()\n"
BARE2 = "from datetime import datetime, date\nx = datetime.now()\ny = date.today()\n"
ANCHORED = 'from datetime import datetime\nfrom zoneinfo import ZoneInfo\nx = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))\n'


def test_ratchet(tmp):
    print("[4] End-to-end — ratchet per-file + escape hatch + exclude")
    sb = os.path.join(tmp, "sandbox")
    bl = os.path.join(tmp, "sandbox_baseline.json")
    f = _write(os.path.join(sb, "app.py"), BARE)

    _write(bl, json.dumps({"files": {}}))
    rc, out = _run(sb, bl, [f])
    check("file MỚI có 1 vi phạm, baseline 0 → BLOCK (rc=1)", rc == 1, f"rc={rc} out={out[:200]}")
    check("thông điệp BLOCK có số dòng + biểu thức", "app.py:2" in out and "datetime.now()" in out, out[:200])
    check("thông điệp BLOCK nói baseline neo theo canonical + lối thoát SKIP (F6)",
          "CANONICAL" in out and "SKIP=tz-anchor-gate" in out, out[:400])

    _write(bl, json.dumps({"files": {"app.py": 1}}))
    rc, out = _run(sb, bl, [f])
    check("nợ CŨ đã trong baseline (1) → qua (rc=0)", rc == 0, f"rc={rc} out={out[:200]}")

    _write(os.path.join(sb, "app.py"), BARE2)
    rc, out = _run(sb, bl, [f])
    check("nợ TĂNG 1→2 → BLOCK", rc == 1, f"rc={rc}")

    _write(os.path.join(sb, "app.py"), ANCHORED)
    rc, out = _run(sb, bl, [f])
    check("đã vá (0 < baseline 1) → qua", rc == 0, f"rc={rc} out={out[:200]}")

    _write(os.path.join(sb, "app.py"), BARE)
    _write(bl, json.dumps({"files": {}}))
    rc, out = _run(sb, bl, [f], {"MIKE_TZ_GATE": "warn"})
    check("MIKE_TZ_GATE=warn → cảnh báo, không chặn", rc == 0 and "🔴" in out, f"rc={rc} out={out[:200]}")
    rc, out = _run(sb, bl, [f], {"MIKE_TZ_GATE": "off"})
    check("MIKE_TZ_GATE=off → im hoàn toàn", rc == 0 and out.strip() == "", f"rc={rc} out={out[:200]}")
    rc, out = _run(sb, bl, [], {"MIKE_TZ_GATE": "off"}, prefix=["--scan"])
    check("off + --scan (chạy TAY) → KHÔNG im: nói rõ là đã KHÔNG chạy",
          rc == 0 and "KHÔNG chạy --scan" in out, f"rc={rc} out={out[:200]}")

    for rel in ("test_thing.py", "probe_x/run.py", "agents/T/research/r.py", "archive/old.py"):
        p = _write(os.path.join(sb, rel), BARE)
        rc, out = _run(sb, bl, [p])
        check(f"loại trừ R&D/vendor: {rel} không bị gate", rc == 0 and out.strip() == "",
              f"rc={rc} out={out[:160]}")

    # Sandbox KHÔNG phải checkout mike ⇒ tuyệt đối không auto-update baseline ở đó.
    _write(os.path.join(sb, "app.py"), ANCHORED)
    _write(bl, json.dumps({"files": {"app.py": 5}}))
    _run(sb, bl, [f])
    check("commit ngoài repo mike → KHÔNG tự ghi baseline",
          json.load(open(bl))["files"]["app.py"] == 5, "baseline đã bị ghi đè")


TDAYS_BARE = "def tdays(a, r=None):\n    return 1\ndef use(a):\n    return tdays(a)\n"
TDAYS_BARE2 = ("def tdays(a, r=None):\n    return 1\ndef use(a):\n    return tdays(a)\n"
               "def use2(a):\n    return tdays(a)\n")
TDAYS_ANCHORED = ("def tdays(a, r=None, vn_holidays=False):\n    return 1\n"
                   "def use(a):\n    return tdays(a, vn_holidays=True)\n")


def test_ratchet_tdays(tmp):
    print("[4b] End-to-end RULE 2 — ratchet per-file trong namespace 'tdays_files' RIÊNG")
    sb = os.path.join(tmp, "sandbox2")
    bl = os.path.join(tmp, "sandbox2_baseline.json")
    f = _write(os.path.join(sb, "app.py"), TDAYS_BARE)

    _write(bl, json.dumps({"files": {}, "tdays_files": {}}))
    rc, out = _run(sb, bl, [f])
    check("file MỚI có 1 vi phạm tdays, baseline tdays_files 0 → BLOCK (rc=1)", rc == 1,
          f"rc={rc} out={out[:200]}")
    check("thông điệp BLOCK gắn nhãn RULE 2 + số dòng + biểu thức",
          "tdays" in out and "app.py:4" in out, out[:300])
    check("thông điệp BLOCK có hướng dẫn vn_holidays= riêng cho RULE 2",
          "vn_holidays=True" in out, out[:600])

    # Nợ CŨ trong đúng namespace tdays_files (KHÔNG phải "files") → qua.
    _write(bl, json.dumps({"files": {}, "tdays_files": {"app.py": 1}}))
    rc, out = _run(sb, bl, [f])
    check("nợ CŨ đã trong tdays_files (1) → qua (rc=0)", rc == 0, f"rc={rc} out={out[:200]}")

    _write(os.path.join(sb, "app.py"), TDAYS_BARE2)
    rc, out = _run(sb, bl, [f])
    check("nợ RULE 2 TĂNG 1→2 → BLOCK", rc == 1, f"rc={rc}")

    _write(os.path.join(sb, "app.py"), TDAYS_ANCHORED)
    rc, out = _run(sb, bl, [f])
    check("đã vá bằng vn_holidays=True (0 < baseline 1) → qua", rc == 0, f"rc={rc} out={out[:200]}")

    # 2 namespace ĐỘC LẬP: nợ rule 1 tăng không được rule 2 (đang sạch) che, và ngược lại.
    mixed = "from datetime import datetime\nx = datetime.now()\n" + TDAYS_ANCHORED
    _write(os.path.join(sb, "mix.py"), mixed)
    fm = os.path.join(sb, "mix.py")
    _write(bl, json.dumps({"files": {}, "tdays_files": {"mix.py": 0}}))
    rc, out = _run(sb, bl, [fm])
    check("rule 1 vi phạm (datetime.now trần) TĂNG dù rule 2 SẠCH → vẫn BLOCK, không bị che",
          rc == 1 and "datetime.now()" in out, f"rc={rc} out={out[:300]}")

    # Sandbox KHÔNG phải checkout mike ⇒ tuyệt đối không auto-update namespace tdays_files ở đó.
    _write(os.path.join(sb, "app.py"), TDAYS_ANCHORED)
    _write(bl, json.dumps({"files": {}, "tdays_files": {"app.py": 5}}))
    _run(sb, bl, [f])
    check("commit ngoài repo mike → KHÔNG tự ghi tdays_files",
          json.load(open(bl))["tdays_files"]["app.py"] == 5, "tdays_files đã bị ghi đè")


SHIM_PROD = "/home/trido/thanhdt/WorkingClaude/tz_anchor_gate_shim.sh"
# Cùng khuôn _resolve_target(): override chỉ hợp lệ khi ĐI KÈM cờ mutation, nếu không một biến
# sót lại làm suite kiểm một BẢN SAO và "ALL PASS" thành PASS GIẢ.
SHIM = _resolve_target(os.environ.get("MIKE_TZ_GATE_SHIM_TARGET"),
                       os.environ.get("MIKE_TZ_GATE_MUTATION") == "1", prod=SHIM_PROD,
                       varname="MIKE_TZ_GATE_SHIM_TARGET")


def test_shim_missing_nested_repo(tmp):
    """F1 (killer objection) — repo ngoài .gitignore chính WorkingClaude/mike/, nên trong mọi
    worktree/clone mới đường dẫn gate KHÔNG tồn tại. Thiếu repo lồng phải là KHÔNG-GATE-ĐƯỢC
    (cảnh báo + rc=0), tuyệt đối không phải CHẶN — phạm vi hook gồm bot_execute.py và
    trading_bot/*.py."""
    print("[6] F1 — shim khi repo lồng WorkingClaude/mike/ KHÔNG có mặt")
    if not os.path.isfile(SHIM):
        check("shim tồn tại", False, SHIM)
        return
    fake = os.path.join(tmp, "fake_wc")          # KHÔNG có thư mục mike/ bên trong
    victim = _write(os.path.join(fake, "bot_execute.py"), BARE)
    shutil.copy2(SHIM, os.path.join(fake, "tz_anchor_gate_shim.sh"))
    r = subprocess.run([os.path.join(fake, "tz_anchor_gate_shim.sh"), victim],
                       capture_output=True, text=True, check=False)
    check("thiếu repo lồng → rc=0 (không chặn commit)", r.returncode == 0, f"rc={r.returncode}")
    check("thiếu repo lồng → CÓ cảnh báo, không im lặng",
          "KHÔNG ĐƯỢC GATE" in r.stderr, f"stderr={r.stderr[:160]!r}")

    real = os.path.join(tmp, "real_wc")
    os.makedirs(os.path.join(real, "mike", "bin"), exist_ok=True)
    shutil.copy2(GATE_PATH, os.path.join(real, "mike", "bin", "tz_anchor_gate.py"))
    shutil.copy2(SHIM, os.path.join(real, "tz_anchor_gate_shim.sh"))
    v2 = _write(os.path.join(real, "app.py"), BARE)
    env = dict(os.environ)
    env["MIKE_TZ_GATE_SELFCHECK"] = "1"
    env["MIKE_TZ_GATE_ROOT"] = real
    env["MIKE_TZ_GATE_BASELINE"] = _write(os.path.join(tmp, "bl_shim.json"), '{"files": {}}')
    r2 = subprocess.run([os.path.join(real, "tz_anchor_gate_shim.sh"), v2],
                        capture_output=True, text=True, env=env, check=False)
    check("có repo lồng → shim ủy quyền cho gate thật và gate CHẶN",
          r2.returncode == 1 and "app.py:2" in r2.stdout, f"rc={r2.returncode} out={r2.stdout[:160]}")

    # R5-7: fallback `_shim_dir="."` khi BASH_SOURCE không chứa "/" (chạy `bash shim.sh` từ chính
    # thư mục của nó). Trước vòng 5 nhánh này không assertion nào chạm tới ⇒ guard trang trí.
    r2b = subprocess.run(["bash", "tz_anchor_gate_shim.sh", v2], capture_output=True, text=True,
                         env=env, cwd=real, check=False)
    check("gọi shim bằng TÊN TRẦN (không có '/') → vẫn tìm đúng gate và CHẶN",
          r2b.returncode == 1 and "app.py:2" in r2b.stdout,
          f"rc={r2b.returncode} out={r2b.stdout[:160]!r} err={r2b.stderr[:160]!r}")

    # arch-review vòng 4 (killer): bản trước `exec "${DNA_PYEXE:-python3}"` không kiểm interpreter
    # ⇒ DNA_PYEXE hỏng cho rc=127 = CHẶN commit SẠCH, và MIKE_TZ_GATE=off không gỡ được vì exec
    # chết trước khi python chạy. Đúng killer F1 đổi biến. Giờ shim không đọc DNA_PYEXE nữa.
    r3 = subprocess.run([os.path.join(real, "tz_anchor_gate_shim.sh"), v2],
                        capture_output=True, text=True,
                        env={**env, "DNA_PYEXE": "/nonexistent/python"}, check=False)
    check("DNA_PYEXE hỏng KHÔNG còn ảnh hưởng shim (vẫn gate bình thường)",
          r3.returncode == r2.returncode, f"rc={r3.returncode} (kỳ vọng {r2.returncode}) err={r3.stderr[:160]!r}")

    poor = os.path.join(tmp, "poorpath")
    os.makedirs(poor, exist_ok=True)
    if os.path.exists("/bin/bash"):
        os.symlink("/bin/bash", os.path.join(poor, "bash"))
        r4 = subprocess.run(["/bin/bash", os.path.join(real, "tz_anchor_gate_shim.sh"), v2],
                            capture_output=True, text=True, env={"PATH": poor}, check=False)
        check("KHÔNG có python3 trên PATH → cảnh báo + rc=0 (không chặn)",
              r4.returncode == 0 and "KHÔNG ĐƯỢC GATE" in r4.stderr,
              f"rc={r4.returncode} err={r4.stderr[:200]!r}")
    else:
        check("dựng được PATH nghèo để thử", False, "không có /bin/bash")


def test_key_none_is_loud(tmp):
    """F2 — 20 worktree của repo ngoài nằm ngoài WC_ROOT; trước bản vá gate trả rc=0 KHÔNG một
    chữ trong khi vi phạm còn sống nguyên ở đó."""
    print("[7] F2 — file ngoài WC_ROOT: phải KÊU, không im")
    sb = os.path.join(tmp, "sandbox")
    bl = _write(os.path.join(tmp, "bl_none.json"), '{"files": {}}')
    outside = _write(os.path.join(tmp, "outside_tree", "x.py"), BARE)
    rc, out = _run(sb, bl, [outside])
    check("không chặn (fail-open)", rc == 0, f"rc={rc}")
    check("nhưng CÓ cảnh báo nêu tên file + lý do",
          "KHÔNG ĐƯỢC GATE" in out and "x.py" in out, f"out={out[:200]!r}")


def test_warn_does_not_raise_baseline(tmp):
    """F3 — warn cho qua ĐÚNG lần này; nếu nó nâng baseline thì một lần lách = chấp nhận nợ
    vĩnh viễn (đúng cái code_quality_gate.sh làm và đã bị audit chỉ ra)."""
    print("[8] F3 — MIKE_TZ_GATE=warn KHÔNG được nâng baseline")
    sb = os.path.join(tmp, "sandbox_warn")
    bl = _write(os.path.join(tmp, "bl_warn.json"), '{"files": {}}')
    f = _write(os.path.join(sb, "app.py"), BARE2)
    rc, out = _run(sb, bl, [f], {"MIKE_TZ_GATE": "warn"})
    check("warn → rc=0", rc == 0, f"rc={rc}")
    check("warn → baseline VẪN rỗng", json.load(open(bl))["files"] == {},
          f"baseline={json.load(open(bl))['files']}")
    check("warn → nói rõ commit sau vẫn chặn", "commit sau vẫn chặn" in out, out[:200])
    rc2, _ = _run(sb, bl, [f])
    check("lần commit sau vẫn BLOCK", rc2 == 1, f"rc={rc2}")


def test_update_baseline_direction(tmp):
    """F4 — config repo ngoài quảng cáo --update-baseline là cách 'siết bằng tay'."""
    print("[9] F4 — --update-baseline mặc định chỉ SIẾT, nâng phải nói ra")
    sb = os.path.join(tmp, "sandbox_upd")
    bl = _write(os.path.join(tmp, "bl_upd.json"), '{"files": {}}')
    f = _write(os.path.join(sb, "app.py"), BARE2)
    rc, out = _run(sb, bl, [f], {}, prefix=["--update-baseline"])
    check("nâng 0→2 mà không có cờ → TỪ CHỐI (rc=1)", rc == 1, f"rc={rc} out={out[:160]}")
    check("baseline không đổi", json.load(open(bl))["files"] == {}, "baseline đã bị ghi")
    rc, out = _run(sb, bl, [f], {}, prefix=["--update-baseline", "--accept-new-debt"])
    check("có --accept-new-debt → nâng được", rc == 0 and json.load(open(bl))["files"].get("app.py") == 2,
          f"rc={rc} baseline={json.load(open(bl))['files']}")
    _write(os.path.join(sb, "app.py"), ANCHORED)
    rc, out = _run(sb, bl, [f], {}, prefix=["--update-baseline"])
    check("HẠ (siết) thì không cần cờ", rc == 0 and "app.py" not in json.load(open(bl))["files"],
          f"rc={rc} baseline={json.load(open(bl))['files']}")


def test_seed_refuses_partial(tmp):
    """F5 — một root không đọc được thì kiểm kê THIẾU; ghi đè bằng nó biến 72 key thành
    ngầm-định-0 ⇒ mọi commit sau chạm chúng đều hard-block."""
    print("[10] F5 — --seed-baseline từ chối ghi khi kiểm kê thiếu")
    bl = _write(os.path.join(tmp, "bl_seed.json"), '{"files": {"giu/nguyen.py": 9}}')
    before = open(bl).read()
    env = dict(os.environ)
    env["MIKE_TZ_GATE_SELFCHECK"] = "1"
    env["MIKE_TZ_GATE_BASELINE"] = bl
    env["MIKE_TZ_GATE_ROOTS"] = f"/nonexistent/repo|*.py:{ROOT}|*.py"
    r = subprocess.run([sys.executable, GATE_PATH, "--seed-baseline"],
                       capture_output=True, text=True, env=env, check=False)
    check("root hỏng → rc != 0", r.returncode != 0, f"rc={r.returncode}")
    check("root hỏng → baseline KHÔNG bị ghi đè", open(bl).read() == before, "baseline đã bị ghi")


def test_auto_update_in_repo(tmp):
    """F7 — nhánh auto-update + `git add` chỉ chạy khi commit TRONG repo chứa baseline. Trước
    bản này nhánh đó KHÔNG có test nào (mutation xoá guard dirty sống sót)."""
    print("[11] F7 — auto-update baseline trong repo thật + guard baseline bẩn")
    r = os.path.join(tmp, "fakerepo")
    os.makedirs(os.path.join(r, "bin"), exist_ok=True)
    os.makedirs(os.path.join(r, "kb"), exist_ok=True)
    for cmd in (["git", "init", "-q", r], ["git", "-C", r, "config", "user.email", "t@t"],
                ["git", "-C", r, "config", "user.name", "t"]):
        subprocess.run(cmd, capture_output=True, check=False)
    bl = os.path.join(r, "kb", "tz_anchor_baseline.json")
    _write(bl, json.dumps({"files": {"bin/app.py": 5}}))
    f = _write(os.path.join(r, "bin", "app.py"), ANCHORED)
    subprocess.run(["git", "-C", r, "add", "-A"], capture_output=True, check=False)
    subprocess.run(["git", "-C", r, "commit", "-qm", "init"], capture_output=True, check=False)

    env = dict(os.environ)
    env.update({"MIKE_TZ_GATE_SELFCHECK": "1", "MIKE_TZ_GATE_ROOT": r, "MIKE_TZ_GATE_BASELINE": bl})
    env.pop("MIKE_TZ_GATE", None)
    res = subprocess.run([sys.executable, GATE_PATH, f], capture_output=True, text=True,
                         env=env, cwd=r, check=False)
    check("trong repo + cây sạch → auto-update HẠ baseline",
          res.returncode == 0 and "bin/app.py" not in json.load(open(bl))["files"],
          f"rc={res.returncode} baseline={json.load(open(bl))['files']} out={res.stdout[:160]}")
    staged = subprocess.run(["git", "-C", r, "diff", "--cached", "--name-only"],
                            capture_output=True, text=True, check=False).stdout
    check("baseline được `git add` vào cùng commit", "kb/tz_anchor_baseline.json" in staged, staged)

    # F3 TRONG repo thật: đây là nơi DUY NHẤT nhánh ghi baseline chạy tới, nên warn phải được
    # kiểm ở đây chứ không phải trong sandbox không-git (ở đó in_mike_repo()=None nên không ghi
    # dù có lỗi hay không — assertion sẽ xanh giả).
    subprocess.run(["git", "-C", r, "reset", "-q", "--hard"], capture_output=True, check=False)
    _write(os.path.join(r, "bin", "app.py"), BARE2)
    _write(bl, json.dumps({"files": {}}))
    subprocess.run(["git", "-C", r, "add", "-A"], capture_output=True, check=False)
    subprocess.run(["git", "-C", r, "commit", "-qm", "warn-case"], capture_output=True, check=False)
    res = subprocess.run([sys.executable, GATE_PATH, f], capture_output=True, text=True,
                         env={**env, "MIKE_TZ_GATE": "warn"}, cwd=r, check=False)
    check("F3 trong repo thật: warn cho qua nhưng KHÔNG nâng baseline",
          res.returncode == 0 and json.load(open(bl))["files"] == {},
          f"rc={res.returncode} baseline={json.load(open(bl))['files']}")

    subprocess.run(["git", "-C", r, "reset", "-q", "--hard"], capture_output=True, check=False)
    _write(os.path.join(r, "bin", "app.py"), ANCHORED)
    _write(bl, json.dumps({"files": {"bin/app.py": 5, "dirty": 1}}))   # sửa CHƯA stage
    snapshot = open(bl).read()
    res = subprocess.run([sys.executable, GATE_PATH, f], capture_output=True, text=True,
                         env=env, cwd=r, check=False)
    check("baseline BẨN (chưa stage) → bỏ qua auto-update, không ghi đè",
          res.returncode == 0 and open(bl).read() == snapshot, f"rc={res.returncode}")


UNPARSABLE = "from datetime import datetime, date\nx = datetime.now()\ny = date.today()\nz = (\n"


def test_unparsable_is_loud(tmp):
    """R5-1 (arch-review vòng 5, KILLER) — 'không parse được' KHÔNG được coi là 'sạch'.

    Bản trước: violations() nuốt SyntaxError thành [] ⇒ (a) nợ §16 thật lọt im lặng, (b) nhánh
    auto-update thấy n==0 nên _set_count() XOÁ key baseline rồi `git add` vào chính commit đó,
    (c) commit SAU chạm file ấy bị HARD-BLOCK "N > baseline 0" trên code người commit không hề
    viết. Ca này phải chạy trong repo GIT THẬT: chỉ ở đó nhánh ghi baseline mới chạy tới.
    """
    print("[18] R5-1 — file KHÔNG parse được: phải KÊU, không gate, KHÔNG đụng baseline")
    r = os.path.join(tmp, "unparsable_repo")
    os.makedirs(os.path.join(r, "bin"), exist_ok=True)
    os.makedirs(os.path.join(r, "kb"), exist_ok=True)
    for cmd in (["git", "init", "-q", r], ["git", "-C", r, "config", "user.email", "t@t"],
                ["git", "-C", r, "config", "user.name", "t"]):
        subprocess.run(cmd, capture_output=True, check=False)
    bl = os.path.join(r, "kb", "tz_anchor_baseline.json")
    _write(bl, json.dumps({"files": {"bin/broken.py": 2}}))
    f = _write(os.path.join(r, "bin", "broken.py"), UNPARSABLE)
    subprocess.run(["git", "-C", r, "add", "-A"], capture_output=True, check=False)
    subprocess.run(["git", "-C", r, "commit", "-qm", "init"], capture_output=True, check=False)
    snapshot = open(bl).read()

    env = dict(os.environ)
    env.update({"MIKE_TZ_GATE_SELFCHECK": "1", "MIKE_TZ_GATE_ROOT": r, "MIKE_TZ_GATE_BASELINE": bl})
    env.pop("MIKE_TZ_GATE", None)
    res = subprocess.run([sys.executable, GATE_PATH, f], capture_output=True, text=True,
                         env=env, cwd=r, check=False)
    check("file không parse được → không chặn commit (rc=0)", res.returncode == 0, f"rc={res.returncode}")
    check("file không parse được → KÊU ra stderr, nêu tên file + nguyên văn exception",
          "bin/broken.py" in res.stderr and "KHÔNG parse được" in res.stderr
          and "SyntaxError" in res.stderr, f"stderr={res.stderr[:220]!r}")
    check("file không parse được → baseline KHÔNG bị đụng (key 2 còn nguyên)",
          open(bl).read() == snapshot, f"baseline={open(bl).read()[:160]!r}")
    staged = subprocess.run(["git", "-C", r, "diff", "--cached", "--name-only"],
                            capture_output=True, text=True, check=False).stdout
    check("file không parse được → baseline KHÔNG bị `git add`",
          "kb/tz_anchor_baseline.json" not in staged, f"staged={staged!r}")

    # --seed-baseline: kiểm kê phải tự khai là THIẾU ⇒ từ chối ghi (đúng luật F5).
    # MIKE_TZ_GATE_ROOTS BẮT BUỘC: không có nó, scan_tree() đi quét TRACKED_ROOTS = 2 checkout
    # THẬT chứ không phải sandbox — assertion sẽ nói về repo khác hẳn với repo nó vừa dựng.
    res = subprocess.run([sys.executable, GATE_PATH, "--seed-baseline"], capture_output=True,
                         text=True, env={**env, "MIKE_TZ_GATE_ROOTS": r}, cwd=r, check=False)
    check("--seed-baseline khi có file không parse được → TỪ CHỐI ghi (kiểm kê THIẾU)",
          res.returncode != 0 and open(bl).read() == snapshot,
          f"rc={res.returncode} out={(res.stdout + res.stderr)[:200]!r}")


def test_corrupt_baseline_fails_open(tmp):
    """R5-2 — baseline hỏng (mồi xung đột merge: file này auto-ghi + git add MỖI commit) không
    được ngầm thành {} rồi hard-block toàn bộ nợ cũ kèm chẩn đoán SAI 'baseline 0'."""
    print("[19] R5-2 — baseline HỎNG: fail-open + nói nguyên văn lỗi, không hard-block hàng loạt")
    sb = os.path.join(tmp, "corrupt")
    bl = os.path.join(tmp, "corrupt_baseline.json")
    f = _write(os.path.join(sb, "app.py"), BARE)
    _write(bl, '{"files": {\n<<<<<<< HEAD\n  "bin/a.py": 3\n=======\n  "bin/a.py": 4\n}}\n')
    rc, out = _run(sb, bl, [f])
    check("baseline hỏng → KHÔNG chặn (rc=0)", rc == 0, f"rc={rc} out={out[:200]}")
    check("baseline hỏng → nói rõ là không đọc được + nguyên văn lỗi",
          "KHÔNG đọc được" in out and ("JSONDecodeError" in out or "ValueError" in out),
          f"out={out[:250]!r}")
    check("baseline hỏng → KHÔNG khẳng định 'baseline 0' / HARD-BLOCK",
          "HARD-BLOCK" not in out, f"out={out[:250]!r}")
    # thiếu file baseline (chưa seed) VẪN phải là nợ 0 thật, không phải lỗi
    rc, out = _run(sb, os.path.join(tmp, "khong-ton-tai.json"), [f])
    check("baseline CHƯA seed (thiếu file) → vẫn gate bình thường (BLOCK nợ mới)",
          rc == 1 and "app.py:2" in out, f"rc={rc} out={out[:200]}")


def test_off_warns_flag_any_position(tmp):
    """R5-5 — logic parse cờ thật không phụ thuộc vị trí, cảnh báo `off` cũng không được."""
    print("[20] R5-5 — cảnh báo MIKE_TZ_GATE=off phải quét MỌI argv, không chỉ argv[0]")
    sb = os.path.join(tmp, "offpos")
    bl = os.path.join(tmp, "offpos_baseline.json")
    f = _write(os.path.join(sb, "app.py"), BARE)
    _write(bl, json.dumps({"files": {}}))
    for prefix, files, label in ((["--update-baseline"], [f], "cờ ĐỨNG TRƯỚC"),
                                 ([], [f, "--update-baseline"], "cờ ĐỨNG SAU file")):
        rc, out = _run(sb, bl, files, {"MIKE_TZ_GATE": "off"}, prefix=prefix)
        check(f"off + --update-baseline ({label}) → KHÔNG im lặng",
              rc == 0 and "KHÔNG chạy --update-baseline" in out, f"rc={rc} out={out[:200]!r}")


MIKE_CFG = os.path.join(ROOT, ".pre-commit-config.yaml")
OUTER_CFG = "/home/trido/thanhdt/.pre-commit-config.yaml"


def _git(repo, *a):
    return subprocess.run(["git", "-C", repo] + list(a), capture_output=True, text=True, check=False)


def test_outer_repo_never_writes_nested_baseline(tmp):
    """R1 (arch-review vòng 2, killer) — repo lồng nằm BÊN TRONG cây của repo ngoài, nên điều
    kiện 'BASELINE nằm dưới git-toplevel' ĐÚNG cho cả hai ⇒ commit từ repo NGOÀI ghi vào
    baseline của repo lồng. Ca này dựng ĐÚNG layout thật, không phải tmpdir không-git — đó là
    lý do assertion cũ ('commit ngoài repo mike → KHÔNG tự ghi baseline') xanh giả: nó chạy ở
    thư mục không phải git repo nên nhánh cần canh không bao giờ chạy tới."""
    print("[12] R1 — commit từ repo NGOÀI không được ghi baseline của repo LỒNG")
    outer = os.path.join(tmp, "outer")
    nested = os.path.join(outer, "WorkingClaude", "mike")
    os.makedirs(os.path.join(nested, "kb"), exist_ok=True)
    os.makedirs(os.path.join(nested, "bin"), exist_ok=True)
    _write(os.path.join(outer, ".gitignore"), "WorkingClaude/mike/\n")
    # Key PHẢI đúng cái baseline_key() sinh ra cho victim ("app.py", vì WC_ROOT của sandbox là
    # <outer>/WorkingClaude) — nếu lệch key thì counts không khớp entry nào, `changed` = False,
    # và ca này xanh kể cả khi guard bị tháo (bản đầu của tôi đúng như vậy: mutation R1 SỐNG SÓT
    # dù test "PASS"). Đây là lý do harness phải tự chứng minh bằng mutation.
    bl = _write(os.path.join(nested, "kb", "tz_anchor_baseline.json"),
                json.dumps({"files": {"app.py": 9, "khac.py": 3}}))
    _write(os.path.join(nested, "bin", "dispatch.sh"), "#!/bin/sh\n")
    victim = _write(os.path.join(outer, "WorkingClaude", "app.py"), ANCHORED)  # ĐÃ VÁ ⇒ hạ 9→0
    for cmd in (["init", "-q", outer], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git"] + cmd if cmd[0] == "init" else ["git", "-C", outer] + cmd,
                       capture_output=True, check=False)
    _git(outer, "add", "-A")
    _git(outer, "commit", "-qm", "init")
    before = open(bl).read()
    env = dict(os.environ)
    env.update({"MIKE_TZ_GATE_SELFCHECK": "1",
                "MIKE_TZ_GATE_ROOT": os.path.join(outer, "WorkingClaude"),
                "MIKE_TZ_GATE_BASELINE": bl})
    env.pop("MIKE_TZ_GATE", None)
    r = subprocess.run([sys.executable, GATE_PATH, victim], capture_output=True, text=True,
                       env=env, cwd=outer, check=False)
    check("chạy từ repo NGOÀI → rc=0", r.returncode == 0, f"rc={r.returncode} out={r.stdout[:200]}")
    check("baseline của repo LỒNG byte-identical (không bị ghi đè)", open(bl).read() == before,
          f"đã bị ghi: {open(bl).read()[:160]}")


def test_baseline_key_worktree(tmp):
    """R4 — nhánh chuẩn hoá key của worktree (mike/agents/wt-*/bin/x.py → mike/bin/x.py) là bản
    vá của một sự cố hard-block CÓ THẬT (arch-review Wags_20260823_071251) mà trước ca này
    KHÔNG có test nào: mọi sandbox đều ở /tmp nên chỉ nhánh key=None được chạy."""
    print("[13] R4 — baseline_key chuẩn hoá worktree về key canonical")
    r = os.path.join(tmp, "mike")
    os.makedirs(os.path.join(r, "bin"), exist_ok=True)
    os.makedirs(os.path.join(r, "kb"), exist_ok=True)
    _write(os.path.join(r, "bin", "dispatch.sh"), "#!/bin/sh\n")
    _write(os.path.join(r, "kb", "tz_anchor_baseline.json"), '{"files": {}}')
    _write(os.path.join(r, "bin", "x.py"), ANCHORED)
    subprocess.run(["git", "init", "-q", r], capture_output=True, check=False)
    _git(r, "config", "user.email", "t@t"); _git(r, "config", "user.name", "t")
    _git(r, "add", "-A"); _git(r, "commit", "-qm", "init")
    wt = os.path.join(r, "agents", "wt-test")
    res = _git(r, "worktree", "add", "-q", "-b", "wtbranch", wt)
    if res.returncode != 0:
        check("dựng được git worktree", False, res.stderr[:160])
        return
    env = dict(os.environ)
    env.update({"MIKE_TZ_GATE_SELFCHECK": "1", "MIKE_TZ_GATE_ROOT": tmp})
    code = ("import importlib.util,sys;"
            "spec=importlib.util.spec_from_file_location('g', sys.argv[1]);"
            "m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);"
            "print(m.baseline_key(sys.argv[2]))")
    k_canon = subprocess.run([sys.executable, "-c", code, GATE_PATH, os.path.join(r, "bin", "x.py")],
                             capture_output=True, text=True, env=env, check=False).stdout.strip()
    k_wt = subprocess.run([sys.executable, "-c", code, GATE_PATH, os.path.join(wt, "bin", "x.py")],
                          capture_output=True, text=True, env=env, check=False).stdout.strip()
    check("canonical → 'mike/bin/x.py'", k_canon == "mike/bin/x.py", f"got {k_canon!r}")
    check("worktree → CÙNG key (không phải mike/agents/wt-test/bin/x.py)", k_wt == k_canon,
          f"canon={k_canon!r} wt={k_wt!r}")


def _hook_block(lines, hook_id):
    """-> (dòng thuộc khối hook `- id: <hook_id>`, có thấy hook đó không).

    Kết thúc khối = BẤT KỲ mục list mới nào ("- " ở đầu sau khi bỏ thụt), KHÔNG phải riêng
    "- id: ": pre-commit không bắt `id` phải là khoá đầu tiên, nên một hook kế tiếp mở đầu bằng
    `- name:` sẽ bị nuốt vào khối này và `verbose: true` của NÓ làm assertion xanh giả.
    """
    block, ok = [], False
    for ln in lines:
        if ln.strip() == f"- id: {hook_id}":
            block, ok = [], True
            continue
        if ok:
            if ln.lstrip().startswith("- "):
                break
            block.append(ln)
    return block, ok


def test_hook_verbose(tmp):
    """R2 — pre_commit/commands/run.py:217 chỉ in output hook khi rc!=0 hoặc verbose. Gate này
    cố ý fail-open; không verbose thì mọi cảnh báo bị nuốt và fail-open thành FAIL-SILENT."""
    print("[14] R2 — hook phải có verbose:true, và verbose thật sự lộ stderr khi rc=0")
    # Fixture TỔNG HỢP, chạy TRƯỚC 2 config thật: trên chính 2 config đang có, bản cũ
    # (`startswith("- id: ")`) và bản mới cho kết quả Y HỆT ⇒ bản vá R4-3 sẽ không có assertion
    # nào canh, revert lúc nào cũng được mà suite vẫn xanh (arch-review vòng 5, R5-3). Chỉ ca
    # "hook KẾ TIẾP mở đầu bằng `- name:`" mới phân biệt được hai bản.
    synth = (
        "repos:\n  - repo: local\n    hooks:\n"
        "      - id: tz-anchor-gate\n        name: gate\n        entry: x\n"
        "      - name: hook-ke-tiep\n        id: khac\n        verbose: true\n"
    ).splitlines()
    sblock, sok = _hook_block(synth, "tz-anchor-gate")
    check("R5-3 fixture: hook kế tiếp mở đầu `- name:` KHÔNG bị nuốt vào khối tz-anchor-gate",
          sok and not any(l.strip() == "verbose: true" for l in sblock),
          f"block={sblock}")
    # KHÔNG `import yaml`: 2 runner selfcheck của fleet (bin/run_selfchecks.sh:19,
    # bin/selfcheck_weekly_baseline_check.sh:132) chạy bằng $DNA_PYEXE = wc_venv/bin/python, môi
    # trường đó KHÔNG có PyYAML ⇒ ca này đỏ giả và cả file bị đẩy vào known_red (arch-review
    # vòng 3, killer). Assertion chỉ cần "khối hook tz-anchor-gate có verbose: true" — quét văn
    # bản là đủ, và chạy được ở MỌI interpreter. Đây đúng là lớp lỗi §16 dạy: giả định của môi
    # trường tác giả không phải giả định của môi trường chạy thật.
    for cfg in (MIKE_CFG, OUTER_CFG):
        label = os.path.basename(os.path.dirname(cfg)) + "/.pre-commit-config.yaml"
        try:
            lines = open(cfg, encoding="utf-8").read().splitlines()
        except OSError as e:
            check(f"{label}: đọc được", False, str(e)[:120])
            continue
        block, ok = _hook_block(lines, "tz-anchor-gate")
        check(f"{label}: khối hook tz-anchor-gate tồn tại", ok, "không thấy `- id: tz-anchor-gate`")
        check(f"{label}: verbose: true trong khối đó",
              any(l.strip() == "verbose: true" for l in block), f"block={block[-6:]}")
    pc = shutil.which("pre-commit") or os.path.expanduser("~/.local/bin/pre-commit")
    if not os.path.exists(pc):
        check("có pre-commit để chứng minh hành vi verbose", False, "không tìm thấy pre-commit")
        return
    demo = os.path.join(tmp, "verbdemo")
    os.makedirs(demo, exist_ok=True)
    _write(os.path.join(demo, "warn.sh"), '#!/bin/sh\necho "CANH-BAO-RC0" >&2\nexit 0\n')
    os.chmod(os.path.join(demo, "warn.sh"), 0o755)
    _write(os.path.join(demo, "f.py"), "x = 1\n")
    for verbose, want in ((False, False), (True, True)):
        _write(os.path.join(demo, ".pre-commit-config.yaml"),
               "repos:\n  - repo: local\n    hooks:\n      - id: w\n        name: w\n"
               "        entry: ./warn.sh\n        language: system\n        files: '\\.py$'\n"
               + ("        verbose: true\n" if verbose else ""))
        subprocess.run(["git", "init", "-q", demo], capture_output=True, check=False)
        _git(demo, "add", "-A")
        out = subprocess.run([pc, "run", "w", "--files", os.path.join(demo, "f.py")],
                             capture_output=True, text=True, cwd=demo, check=False)
        seen = "CANH-BAO-RC0" in (out.stdout + out.stderr)
        check(f"pre-commit {'verbose' if verbose else 'mặc định'} + rc=0 → cảnh báo "
              f"{'HIỆN' if want else 'BỊ NUỐT'}", seen == want,
              f"seen={seen}, out={out.stdout[-200:]!r}")


def test_env_knobs_guarded(tmp):
    """R5 — một biến sót lại đổi được WC_ROOT là đủ biến gate thành no-op im lặng."""
    print("[15] R5 — env knob sandbox phải bị từ chối nếu thiếu MIKE_TZ_GATE_SELFCHECK=1")
    f = _write(os.path.join(tmp, "knob", "app.py"), BARE)
    for knob in ("MIKE_TZ_GATE_ROOT", "MIKE_TZ_GATE_BASELINE", "MIKE_TZ_GATE_ROOTS"):
        env = dict(os.environ)
        env.pop("MIKE_TZ_GATE_SELFCHECK", None)
        for k in ("MIKE_TZ_GATE_ROOT", "MIKE_TZ_GATE_BASELINE", "MIKE_TZ_GATE_ROOTS"):
            env.pop(k, None)
        env[knob] = "/nonexistent"
        r = subprocess.run([sys.executable, GATE_PATH, f], capture_output=True, text=True,
                           env=env, check=False)
        check(f"{knob} không có cờ → TỪ CHỐI chạy", r.returncode != 0 and "MIKE_TZ_GATE_SELFCHECK" in r.stderr,
              f"rc={r.returncode} err={r.stderr[:160]!r}")
        r_off = subprocess.run([sys.executable, GATE_PATH, f], capture_output=True, text=True,
                               env={**env, "MIKE_TZ_GATE": "off"}, check=False)
        check(f"{knob} + MIKE_TZ_GATE=off → off THẮNG (rc=0, im)",
              r_off.returncode == 0 and (r_off.stdout + r_off.stderr).strip() == "",
              f"rc={r_off.returncode} out={(r_off.stdout + r_off.stderr)[:160]!r}")


def test_git_add_failure_is_loud(tmp):
    """arch-review vòng 3 — nhánh 'baseline ĐÃ GHI nhưng git add THẤT BẠI' để lại dirt trong cây
    mike cho consolidate.sh `git add -A` quét (chính hiểm hoạ R1). Trước ca này nó không có
    assertion nào: mutation xoá dòng cảnh báo SỐNG SÓT."""
    print("[16] R3-residual — git add baseline thất bại phải KÊU")
    r = os.path.join(tmp, "addfail")
    os.makedirs(os.path.join(r, "bin"), exist_ok=True)
    os.makedirs(os.path.join(r, "kb"), exist_ok=True)
    _write(os.path.join(r, ".gitignore"), "kb/\n")           # baseline bị chính repo đó ignore
    bl = _write(os.path.join(r, "kb", "tz_anchor_baseline.json"), json.dumps({"files": {"bin/app.py": 7}}))
    f = _write(os.path.join(r, "bin", "app.py"), ANCHORED)     # 0 vi phạm ⇒ auto-update HẠ
    subprocess.run(["git", "init", "-q", r], capture_output=True, check=False)
    _git(r, "config", "user.email", "t@t"); _git(r, "config", "user.name", "t")
    _git(r, "add", "-A"); _git(r, "commit", "-qm", "init")
    env = dict(os.environ)
    env.update({"MIKE_TZ_GATE_SELFCHECK": "1", "MIKE_TZ_GATE_ROOT": r, "MIKE_TZ_GATE_BASELINE": bl})
    env.pop("MIKE_TZ_GATE", None)
    res = subprocess.run([sys.executable, GATE_PATH, f], capture_output=True, text=True,
                         env=env, cwd=r, check=False)
    check("git add thất bại → không chặn commit", res.returncode == 0, f"rc={res.returncode}")
    check("git add thất bại → CÓ cảnh báo 'CHƯA stage', không im",
          "CHƯA stage" in (res.stdout + res.stderr),
          f"out={(res.stdout + res.stderr)[:220]!r}")


def test_tracked_roots_resolve(gate):
    """arch-review vòng 3 — đổi đường dẫn canonical thành `mikeX` SỐNG SÓT cả suite: 2 hằng số
    quyết định kiểm kê baseline mà không assertion nào chạm tới."""
    print("[17] TRACKED_ROOTS phải trỏ vào 2 checkout git THẬT")
    for repo, _pattern in gate.TRACKED_ROOTS:
        top = subprocess.run(["git", "-C", repo, "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=False)
        check(f"{repo} là git checkout", top.returncode == 0 and top.stdout.strip() != "",
              f"rc={top.returncode} err={top.stderr[:120]!r}")


def test_prod_baseline_untouched(sha_before):
    print("[5] File production không bị selfcheck đụng")
    sha_after = hashlib.sha256(open(PROD_BASELINE, "rb").read()).hexdigest()
    check("kb/tz_anchor_baseline.json nguyên vẹn", sha_after == sha_before,
          f"{sha_before[:12]} → {sha_after[:12]}")


def main():
    print(f"tz_anchor_gate_selfcheck — gate={GATE_PATH}  TZ={os.environ.get('TZ', '(unset)')}")
    sha_before = hashlib.sha256(open(PROD_BASELINE, "rb").read()).hexdigest()
    gate = _load_gate()
    tmp = tempfile.mkdtemp(prefix="tz_anchor_selfcheck_")
    try:
        test_detector(gate, tmp)
        test_detector_tdays(gate, tmp)
        test_historical(gate, tmp)
        test_historical_tdays(gate, tmp)
        test_ratchet(tmp)
        test_ratchet_tdays(tmp)
        test_shim_missing_nested_repo(tmp)
        test_key_none_is_loud(tmp)
        test_warn_does_not_raise_baseline(tmp)
        test_update_baseline_direction(tmp)
        test_seed_refuses_partial(tmp)
        test_auto_update_in_repo(tmp)
        test_outer_repo_never_writes_nested_baseline(tmp)
        test_baseline_key_worktree(tmp)
        test_hook_verbose(tmp)
        test_env_knobs_guarded(tmp)
        test_git_add_failure_is_loud(tmp)
        test_unparsable_is_loud(tmp)
        test_corrupt_baseline_fails_open(tmp)
        test_off_warns_flag_any_position(tmp)
        test_tracked_roots_resolve(gate)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    test_prod_baseline_untouched(sha_before)
    print()
    if FAILED:
        print(f"❌ {len(FAILED)}/{len(TOTAL)} FAIL: {FAILED}")
        return 1
    print(f"✅ ALL PASS — {len(TOTAL)}/{len(TOTAL)} assertion")
    return 0


def run_all_tz():
    """§16 tự áp lên chính nó: cùng suite, 3 môi trường TZ, output phải GIỐNG HỆT."""
    variants = [("env -u TZ", ["env", "-u", "TZ"]),
                ("TZ=Asia/Ho_Chi_Minh", ["env", "TZ=Asia/Ho_Chi_Minh"]),
                ("TZ=America/New_York", ["env", "TZ=America/New_York"])]
    outs = {}
    rcs = {}
    for label, prefix in variants:
        r = subprocess.run(prefix + [sys.executable, os.path.abspath(__file__)],
                           capture_output=True, text=True, check=False)
        body = "\n".join(ln for ln in r.stdout.splitlines() if not ln.startswith("tz_anchor_gate_selfcheck"))
        outs[label] = body
        rcs[label] = r.returncode
        print(f"── {label}: rc={r.returncode}")
    ref = outs["env -u TZ"]
    bad = [k for k, v in outs.items() if v != ref] + [k for k, v in rcs.items() if v != 0]
    if bad:
        print(f"\n❌ khác nhau giữa các TZ hoặc FAIL: {sorted(set(bad))}")
        print(outs["TZ=America/New_York"])
        return 1
    print("\n✅ 3/3 môi trường TZ cho kết quả GIỐNG HỆT và đều PASS")
    return 0


# run_mutations() trước vòng 4 CHỈ mutate file .py — mọi guard trong shim (.sh) là guard chưa
# từng bị kiểm (arch-review vòng 4). Danh sách này bịt đúng chỗ đó.
SHIM_MUTATIONS = [
    ("shim quay lại `exec $DNA_PYEXE` (killer vòng 4) → biến kế thừa hỏng = chặn commit sạch",
     'PY="$(command -v python3 2>/dev/null || true)"\nif [ -z "$PY" ]; then',
     'PY="${DNA_PYEXE:-python3}"\nif [ -z "" ]; then'),
    # `/dev/null/never` (bản vòng 4) là mutation SAI HƯỚNG: `! -f` luôn ĐÚNG nên guard kích
    # hoạt VÔ ĐIỀU KIỆN — bị giết bởi assertion "ủy quyền cho gate thật", trong khi 2 assertion
    # fail-open F1 vẫn xanh. `if false; then` mới đúng nghĩa GỠ guard (arch-review vòng 5, R5-4).
    ("shim bỏ guard thiếu repo lồng (F1) → Executable not found, chặn commit sạch",
     'if [ ! -f "$GATE" ]; then', 'if false; then'),
    ("shim bỏ fallback _shim_dir → chạy bằng TÊN TRẦN (không có `/`) thì cd sai, gate câm",
     '[ "$_shim_dir" = "${BASH_SOURCE[0]}" ] && _shim_dir="."', ':'),
    ("shim bỏ guard thiếu python3 → PATH nghèo = rc!=0 = chặn commit sạch",
     'if [ -z "$PY" ]; then', 'if false; then'),
]

MUTATIONS = [
    ("bỏ điều kiện 'không có argument' (c) → datetime.now(_ICT) cũng bị bắt",
     "        if (node.args or node.keywords) and not _tz_arg_is_none(node):\n            continue\n", ""),
    ("nới receiver (b) sang mọi tên → okf.today()/pd.Timestamp.now() bị bắt",
     '        if recv.split(".")[-1] not in receivers:\n            continue\n', ""),
    ("bỏ 'today' khỏi (a) → date.today() lọt",
     'BAD_ATTRS = {"now", "today"}', 'BAD_ATTRS = {"now"}'),
    ("bỏ 'now' khỏi (a) → datetime.now() lọt",
     'BAD_ATTRS = {"now", "today"}', 'BAD_ATTRS = {"today"}'),
    ("ratchet luôn cho qua → nợ TĂNG không bị chặn",
     "            if n > old:\n                blocked.append((rule, key, old, n))\n", "            pass\n"),
    # Mutation ĐÚNG cho F3 là bỏ `return 0` để warn RƠI XUỐNG nhánh auto-update — không phải
    # xoá dòng print (bản đầu làm vậy và SURVIVED: dòng print thứ hai trong vòng lặp vẫn chứa
    # chuỗi mà assertion tìm, nên assertion không hề canh hành vi GHI).
    ("warn-mode rơi xuống auto-update (F3) → lách 1 lần = chấp nhận nợ vĩnh viễn",
     "        return 0\n\n    mike_top = in_mike_repo()", "        pass\n\n    mike_top = in_mike_repo()"),
    ("bỏ guard baseline BẨN (F7) → ghi đè sửa đổi chưa stage",
     "    if dirty:\n", "    if False:\n"),
    ("--seed-baseline ghi cả khi kiểm kê THIẾU (F5)",
     "        if not complete:\n", "        if False:\n"),
    ("bỏ alias-aware receiver (F8) → `from datetime import datetime as dtm` lọt",
     "    names = set(DATETIME_RECEIVERS)\n", "    return set(DATETIME_RECEIVERS)\n    names = set(DATETIME_RECEIVERS)\n"),
    ("bỏ nhận diện now(None) (F8)",
     "        if (node.args or node.keywords) and not _tz_arg_is_none(node):\n",
     "        if node.args or node.keywords:\n"),
    ("key=None quay lại IM LẶNG (F2)",
     "                f\"⚠️  tz_anchor_gate: {os.path.abspath(f)} nằm ngoài {WC_ROOT} và ngoài mọi \"\n                \"checkout mike — KHÔNG có baseline-key, file này KHÔNG ĐƯỢC GATE.\",",
     '                "",'),
    ("--update-baseline nâng được mà không cần cờ (F4)",
     "        if raises_by_rule and not accept_new_debt:\n", "        if False:\n"),
    ("in_mike_repo() nới về 'BASELINE nằm dưới top' (R1) → repo ngoài ghi baseline repo lồng",
     "        return top if os.path.isfile(cand) and os.path.samefile(cand, BASELINE) else None",
     "        return top"),
    ("baseline_key() mất nhánh chuẩn hoá worktree (R4) → hard-block oan như 2026-08-23",
     '    if top and os.path.isdir(os.path.join(top, "kb")) and os.path.isfile(os.path.join(top, "bin", "dispatch.sh")):\n        return "mike/" + os.path.relpath(abs_p, top)\n',
     ""),
    ("bỏ guard env knob (R5) → biến sót lại biến gate thành no-op im lặng",
     "    if _STRAY:\n", "    if False:\n"),
    # Needle phải nuốt TRỌN câu lệnh print. Bản đầu chỉ thay TIỀN TỐ chuỗi, phần đuôi
    # "…CHƯA stage." vẫn được in ⇒ assertion vẫn xanh ⇒ mutation SỐNG SÓT dù guard đã bị tháo.
    ("bỏ cảnh báo `git add` thất bại → baseline ghi rồi mà không ai biết chưa stage",
     '            print("⚠️  tz_anchor_gate: git add baseline thất bại — baseline đã ghi nhưng CHƯA stage.", file=sys.stderr)',
     '            pass'),
    ("TRACKED_ROOTS trỏ sai checkout (mike → mikeX)",
     '("/home/trido/thanhdt/WorkingClaude/mike", "*.py")',
     '("/home/trido/thanhdt/WorkingClaude/mikeX", "*.py")'),
    ("violations() quay lại coi 'không parse được' = 'sạch' (R5-1 killer) → nợ lọt im lặng + "
     "XOÁ key baseline",
     '    except (OSError, SyntaxError, ValueError, UnicodeDecodeError) as e:\n'
     '        _PARSE_ERR[os.path.abspath(path)] = f"{type(e).__name__}: {e}"\n'
     '        return None',
     '    except (OSError, SyntaxError, ValueError, UnicodeDecodeError):\n        return []'),
    ("load_baseline() nuốt baseline hỏng thành {} (R5-2) → hard-block toàn bộ nợ cũ + chẩn đoán sai",
     '    except (OSError, ValueError) as e:\n'
     '        return {"files": {}}, f"{type(e).__name__}: {e}"',
     '    except (OSError, ValueError):\n        return {"files": {}}, None'),
    ("load_baseline() mất nhánh FileNotFoundError → chưa seed bị coi là HỎNG rồi fail-open, "
     "gate thành no-op trên repo mới",
     '    except FileNotFoundError:\n'
     '        return {"files": {}}, None      # chưa seed = nợ 0, đúng nghĩa, không phải lỗi\n',
     ''),
    ("cảnh báo `off` quay lại chỉ nhìn argv[0] (R5-5) → cờ đứng sau file thì im lặng",
     "        manual = [a for a in argv if a in ", "        manual = [a for a in argv[:1] if a in "),
    # Hai mutation dưới đây CỐ Ý neo vào chuỗi NGẮN, không có comment: bản vòng 4 neo vào
    # nguyên văn cả khối `off` nên mỗi lần sửa một dòng comment trong khối là mutation tự hỏng
    # (HARNESS-HỎNG) — harness giòn thì mất luôn ý nghĩa canh gác.
    ("guard env knob chạy TRƯỚC `off` (R5 vòng 3) → off không còn tắt được gate",
     '    if mode == "off":', "    if False:"),
    ("bỏ cảnh báo `off` khi chạy TAY --scan/--seed/--update (vòng 4) → im lặng, người chạy "
     "tưởng đã quét/re-seed xong",
     "\n        if manual:", "\n        if False:"),
    # ── RULE 2 (tdays/holiday, 2026-09-05) — ghim đúng dòng vừa thêm, bắt bằng
    # test_detector_tdays/test_historical_tdays/test_ratchet_tdays (không phải suy diễn).
    ("RULE2 M1: đổi TDAYS_MARKER khỏi 'tdays' → mọi call-site thật sự lỗi lọt im lặng (rule "
     "2 trở thành no-op)",
     'TDAYS_MARKER = "tdays"', 'TDAYS_MARKER = "tdaysXXXNEVERMATCH"'),
    ("RULE2 M2: bỏ điều kiện marker (contains_holiday_marker/scope_has_vn_holidays_param) → "
     "MỌI call tdays() bị bắt vô điều kiện, kể cả ca đã khai vn_holidays= đúng",
     '        if _contains_holiday_marker(scope) or _scope_has_vn_holidays_param(scope):\n            continue\n',
     '        if False:\n            continue\n'),
    ("RULE2 M3: bỏ nhận diện PER-CALL keyword vn_holidays= → ca khai vn_holidays=True ngay "
     "tại lệnh gọi vẫn bị bắt oan (arch-review vòng 1 RULE-2: per-call thay cho scope-wide)",
     '        if any(kw.arg == "vn_holidays" for kw in node.keywords):\n            continue  # PER-CALL',
     '        if False:\n            continue  # PER-CALL'),
    ("RULE2 M4: bỏ nhận diện is_holiday dạng Attribute → ca tham chiếu vn_market.is_holiday() "
     "(dạng module.attribute, không phải Name import trực tiếp) vẫn bị bắt oan (X4, arch-review "
     "vòng 1 — bản trước xoá CẢ HAI nhánh cùng lúc nên không tách được lỗ này)",
     '        if isinstance(n, ast.Attribute) and n.attr == "is_holiday" and isinstance(n.ctx, ast.Load):\n            return True\n',
     '        if False:\n            return True\n'),
    ("RULE2 M4b: bỏ nhận diện is_holiday dạng Name (import trực tiếp) → ca `from … import "
     "is_holiday; is_holiday(d)` vẫn bị bắt oan",
     '        if isinstance(n, ast.Name) and n.id == "is_holiday" and isinstance(n.ctx, ast.Load):\n            return True\n',
     '        if False:\n            return True\n'),
    ("RULE2 M5: bỏ nhận diện tham số vn_holidays trong chữ ký hàm bao quanh → ca forward qua "
     "tham số vẫn bị bắt oan",
     '    return "vn_holidays" in names', '    return False'),
    ("RULE2 M6: enclosing_scope() không còn dừng ở def GẦN NHẤT (luôn rơi về module top-level) "
     "→ marker ở hàm bao quanh trực tiếp không còn được nhìn thấy",
     '            if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):\n                return cur\n',
     '            if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):\n                pass\n'),
    ("RULE2 M7 (X1, arch-review vòng 1): bỏ ranh giới scope TRONG walk() (đệ quy qua compound "
     "statement) → marker trong 1 def LỒNG bên trong 1 khối `if` lại ân xá được call ở scope "
     "NGOÀI nó (hướng NGƯỢC với ca 'scope LỒNG' đã có — ca đó test marker ngoài không cứu được "
     "lồng trong; mutation này test marker LỒNG TRONG không được phép cứu scope NGOÀI)",
     '            if isinstance(child, SCOPE_BOUNDARY_TYPES):\n                continue\n',
     '            if False:\n                continue\n'),
    ("RULE2 M7b (arch-review vòng 3, B1): bỏ ranh giới scope Ở TOP-LEVEL của scope.body (khác "
     "M7 — đây là bộ lọc RIÊNG cho statement top-level, không phải bộ lọc trong walk()) → def "
     "lồng TRỰC TIẾP ở top-level (không qua compound statement nào) ân xá được scope NGOÀI; đo "
     "được: xoá RIÊNG dòng này mà chỉ có ca 'if True' (M7) thì suite vẫn 129/129 PASS — cần ca "
     "top-level TRỰC TIẾP riêng để 2 mutation không dùng chung 1 điểm hỏng",
     '        if isinstance(stmt, SCOPE_BOUNDARY_TYPES):\n            continue\n',
     '        if False:\n            continue\n'),
    ("RULE2 M8 (arch-review vòng 3, B2): SCOPE_BOUNDARY_TYPES thu hẹp lại về CHỈ FunctionDef/"
     "AsyncFunctionDef (bỏ Lambda/ClassDef/comprehension) → marker is_holiday trong lambda/"
     "comprehension/class lồng bên trong hàm rò ra ngoài, ân xá SAI 1 call tdays() trần khác",
     "SCOPE_BOUNDARY_TYPES = (\n    ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef,\n"
     "    ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp,\n)",
     "SCOPE_BOUNDARY_TYPES = (ast.FunctionDef, ast.AsyncFunctionDef)"),
    ("RULE2 B3 (arch-review vòng 3): bỏ ràng buộc ctx=Load trên marker is_holiday → "
     "`is_holiday = None` (gán, không đọc) hoặc `del is_holiday` vẫn ân xá SAI call tdays() trần",
     '        if isinstance(n, ast.Attribute) and n.attr == "is_holiday" and isinstance(n.ctx, ast.Load):\n'
     '            return True\n'
     '        if isinstance(n, ast.Name) and n.id == "is_holiday" and isinstance(n.ctx, ast.Load):\n'
     '            return True\n',
     '        if isinstance(n, ast.Attribute) and n.attr == "is_holiday":\n            return True\n'
     '        if isinstance(n, ast.Name) and n.id == "is_holiday":\n            return True\n'),
]


def _run_mutation_set(target_prod, target_env, mutations, label):
    """Chạy 1 bộ mutation trên MỘT file production (bản sao trong mkdtemp) -> [mô tả sống sót]."""
    src = open(target_prod, encoding="utf-8").read()
    sha_before = hashlib.sha256(src.encode()).hexdigest()
    tmpdir = tempfile.mkdtemp(prefix="tz_anchor_mut_")
    survived = []
    print(f"── {label}")
    try:
        for desc, needle, repl in mutations:
            if needle not in src:
                survived.append(f"HARNESS-HỎNG: {desc}")
                print(f"  ❌ HARNESS  chuỗi cần thay KHÔNG có trong {label}: {desc}")
                continue
            mutant = os.path.join(tmpdir, "mutant" + os.path.splitext(target_prod)[1])
            with open(mutant, "w", encoding="utf-8") as fh:
                fh.write(src.replace(needle, repl, 1))
            os.chmod(mutant, 0o755)
            shutil.rmtree(os.path.join(tmpdir, "__pycache__"), ignore_errors=True)
            env = dict(os.environ)
            env[target_env] = mutant
            env["MIKE_TZ_GATE_MUTATION"] = "1"
            r = subprocess.run([sys.executable, os.path.abspath(__file__)],
                               capture_output=True, text=True, env=env, check=False)
            if r.returncode != 0:
                print(f"  KILLED    {desc}")
            else:
                survived.append(desc)
                print(f"  SURVIVED  {desc}  ← assertion tuyên bố canh nhánh này là GUARD GIẢ")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    sha_after = hashlib.sha256(open(target_prod, "rb").read()).hexdigest()
    if sha_after != sha_before:
        survived.append(f"PRODUCTION-FILE-MODIFIED:{target_prod}")
        print(f"  ❌ {label} production BỊ THAY ĐỔI: {sha_before[:12]} → {sha_after[:12]}")
    else:
        print(f"  OK        {label} production nguyên vẹn (sha256 {sha_before[:12]}…)")
    return survived


def run_mutations():
    survived = _run_mutation_set(GATE_PROD, "MIKE_TZ_GATE_TARGET", MUTATIONS, "tz_anchor_gate.py")
    survived += _run_mutation_set(SHIM_PROD, "MIKE_TZ_GATE_SHIM_TARGET", SHIM_MUTATIONS,
                                  "tz_anchor_gate_shim.sh")
    total = len(MUTATIONS) + len(SHIM_MUTATIONS)
    print()
    if survived:
        print(f"❌ {len(survived)} mutation sống sót: {survived}")
        return 1
    print(f"✅ {total}/{total} mutation bị giết")
    return 0


if __name__ == "__main__":
    if "--mutations" in sys.argv:
        sys.exit(run_mutations())
    if "--all-tz" in sys.argv:
        sys.exit(run_all_tz())
    sys.exit(main())
