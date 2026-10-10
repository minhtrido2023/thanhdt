#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck: đối soát FILL-vs-STATE của eod_trading_report.sh lọc account FAIL-CLOSED (§12).

Chạy:  python3 mike/bin/eod_trading_report_account_filter_selfcheck.py
       cd /tmp && env -i PATH=/usr/bin:/bin python3 <repo>/mike/bin/eod_trading_report_account_filter_selfcheck.py

Bug gốc (code-quality 2026-09-13, vá ở c9edd4c6 mục c): không tra được account_id ⇒ `except: pass`
+ lọc có điều kiện ⇒ gộp order của MỌI account trong dnse_raw_{date}.jsonl (file chung
SpaceX+ZaloPay) ⇒ lệch giả / che lệch thật; record thiếu account_no lọt qua bộ lọc.

Test HÀNH VI: trích NGUYÊN đoạn python nhúng (heredoc REPORT=...PYEOF) từ .sh rồi chạy nó trên
một wc_root giả (mkdtemp): trading_bot.plan stub, secrets/dnse_raw/state giả, notify.sh STUB ghi
lại lời gọi (không có đường nào tới notify.sh thật: script gọi <wc_root>/mike/bin/notify.sh, và
PATH cũng chỉ trỏ vào thư mục stub). CHỨNG MINH NGƯỢC: cùng fixture trên bản trước vá
(4195911c = c9edd4c6~1) ⇒ (i)/(ii) phải ĐỎ.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
# EOD_SRC: chạy TOÀN BỘ ca lên một bản MUTANT thay vì bản thật (đối chứng mutation-kill, cùng
# quy ước RC_SRC của check_report_cadence_selfcheck.py).
SCRIPT = os.environ.get("EOD_SRC") or os.path.join(HERE, "eod_trading_report.sh")
PRE_FIX_REF = "4195911c"   # c9edd4c6~1
OPEN_MARK = "REPORT=\"$(python3 - \"$PLAN_FILE\" \"$STATE_FILE\" \"$ACCOUNT\" \"$PLAN_DATE\" \"$WC_ROOT\" << 'PYEOF'"
DATE = "2026-08-11"
ACCT_NO = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}
NEUTRAL = "Chưa đối chiếu được số liệu khớp lệnh hôm nay"

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  ✓ " if cond else "  ✗ ") + name + (f"   [{detail}]" if detail and not cond else ""))


def extract_py(sh_text):
    """Đoạn python giữa dòng mở REPORT=... << 'PYEOF' và dòng PYEOF kế tiếp. None nếu không thấy."""
    lines = sh_text.splitlines(keepends=True)
    starts = [i for i, ln in enumerate(lines) if ln.rstrip("\n") == OPEN_MARK]
    if len(starts) != 1:
        return None
    body = []
    for ln in lines[starts[0] + 1:]:
        if ln.rstrip("\n") == "PYEOF":
            return "".join(body)
        body.append(ln)
    return None


PLAN_STUB = '''import json, os, types
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load_plan(plan_date, account="main"):
    d = json.load(open(os.path.join(_ROOT, "plans", f"plan_{account}_{plan_date}.json")))
    return types.SimpleNamespace(orders=[types.SimpleNamespace(**o) for o in d["orders"]])
'''
# Leg 3 (statement DNSE qua email) không thuộc phạm vi test — stub "không có statement".
BROKER_STUB = '''import types
def load_broker_fills(plan_date, account, wc_root):
    return types.SimpleNamespace(available=False, by_key={}, qty=lambda *k: 0)
def reconcile_lines(bk, plan_by_key, state_by_key):
    return []
'''
NOTIFY_STUB = '#!/bin/sh\nprintf "%s\\n" "$*" >> "$(dirname "$0")/notify_calls.log"\n'


def build_root(secrets_accounts, raw_records):
    root = tempfile.mkdtemp(prefix="eod_acct_sc_")
    for d in ("trading_bot", "plans", "secrets", "data/execution_logs", "mike/bin", "state"):
        os.makedirs(os.path.join(root, d), exist_ok=True)
    open(os.path.join(root, "trading_bot", "__init__.py"), "w").close()
    with open(os.path.join(root, "trading_bot", "plan.py"), "w") as f:
        f.write(PLAN_STUB)
    with open(os.path.join(root, "mike", "bin", "broker_fill_confirm.py"), "w") as f:
        f.write(BROKER_STUB)
    notify = os.path.join(root, "mike", "bin", "notify.sh")
    with open(notify, "w") as f:
        f.write(NOTIFY_STUB)
    os.chmod(notify, 0o755)
    for acct in ACCT_NO:
        with open(os.path.join(root, "plans", f"plan_{acct}_{DATE}.json"), "w") as f:
            json.dump({"orders": [{"id": "B-FPT", "ticker": "FPT", "side": "buy", "qty": 1000,
                                   "ref_price": 72000}]}, f)
        with open(os.path.join(root, "state", f"state_{acct}.json"), "w") as f:
            json.dump({"parents": {"B-FPT": {"filled": 0, "children": []}}}, f)
    with open(os.path.join(root, "secrets", "trading_bot_accounts.json"), "w") as f:
        json.dump({"accounts": secrets_accounts}, f)
    with open(os.path.join(root, "data", "execution_logs", f"dnse_raw_{DATE}.jsonl"), "w") as f:
        for r in raw_records:
            f.write(json.dumps(r) + "\n")
    return root


def order_rec(account_no, oid, fill):
    rec = {"kind": "orders", "payload": {"orders": [
        {"id": oid, "symbol": "FPT", "fillQuantity": fill}]}}
    if account_no is not None:
        rec["account_no"] = account_no
    return rec


def run_report(py, root, account):
    state = os.path.join(root, "state", f"state_{account}.json")
    env = {"PATH": os.path.join(root, "mike", "bin") + ":/usr/bin:/bin", "HOME": root,
           "LANG": "C.UTF-8"}
    r = subprocess.run([sys.executable, "-", "plan.json", state, account, DATE, root],
                       input=py, capture_output=True, text=True, env=env, cwd=root, timeout=120)
    mm_path = os.path.join(root, "state", f"eod_mismatch_{account}_{DATE}.json")
    mm = json.load(open(mm_path)) if os.path.exists(mm_path) else None
    calls_path = os.path.join(root, "mike", "bin", "notify_calls.log")
    calls = open(calls_path).read() if os.path.exists(calls_path) else ""
    broker = {m["ticker"]: m["broker_filled"] for m in (mm or {}).get("mismatches", [])}
    return {"rc": r.returncode, "out": r.stdout, "err": r.stderr, "broker": broker, "notify": calls}


def scenarios(py):
    """Trả dict kết quả 3 ca trên đoạn python `py`."""
    res = {}
    both = [order_rec(ACCT_NO["SpaceX"], 1, 100), order_rec(ACCT_NO["ZaloPay"], 2, 300)]
    # (i) secrets KHÔNG có ZaloPay; dnse_raw có order của cả 2 account
    root = build_root([{"label": "SpaceX", "account_id": ACCT_NO["SpaceX"]}], both)
    try:
        res["i"] = run_report(py, root, "ZaloPay")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    # (ii) record thiếu account_no (fill 500) cạnh record đúng của SpaceX (fill 100)
    accts = [{"label": a, "account_id": n} for a, n in ACCT_NO.items()]
    root = build_root(accts, [order_rec(ACCT_NO["SpaceX"], 1, 100), order_rec(None, 9, 500)])
    try:
        res["ii"] = run_report(py, root, "SpaceX")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    # (iii) 2 account cùng file, secrets đủ
    root = build_root(accts, both)
    try:
        res["iii_S"] = run_report(py, root, "SpaceX")
        res["iii_Z"] = run_report(py, root, "ZaloPay")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    return res


def ok_i(r):
    return (r["rc"] == 0 and NEUTRAL in r["out"] and "🚨" not in r["out"] and "✅ Đối soát" not in r["out"]
            and not r["broker"] and "BỎ đối soát" in r["err"] and "BỎ đối soát" in r["notify"])


def ok_ii(r):
    return r["rc"] == 0 and r["broker"] == {"FPT": 100}


print("[0] harness còn sống")
cur_text = open(SCRIPT, encoding="utf-8").read()
cur_py = extract_py(cur_text)
check("trích được đúng 1 đoạn python REPORT=...PYEOF từ bản hiện tại", cur_py is not None)
check("đoạn trích là bản CÓ fail-closed (_target_account_err)", bool(cur_py) and "_target_account_err" in cur_py)
old = subprocess.run(["git", "-C", HERE, "show", f"{PRE_FIX_REF}:bin/eod_trading_report.sh"],
                     capture_output=True, text=True)
old_py = extract_py(old.stdout) if old.returncode == 0 else None
check(f"trích được đoạn python bản trước vá ({PRE_FIX_REF})", old_py is not None, old.stderr.strip())
check("bản trước vá KHÔNG có fail-closed (đúng là bản cũ)", bool(old_py) and "_target_account_err" not in old_py)
if cur_py is None:
    print("❌ không trích được đoạn python — dừng")
    sys.exit(1)

R = scenarios(cur_py)
print("\n[i] secrets thiếu account ⇒ BỎ đối soát, câu trung tính, không gộp order account khác")
r = R["i"]
check("rc=0 (báo cáo vẫn ra)", r["rc"] == 0, r["err"][-400:])
check("báo cáo có câu trung tính", NEUTRAL in r["out"], r["out"][:300])
check("báo cáo KHÔNG lộ path/exception (chi tiết chỉ ở kênh ops)",
      not any(x in r["out"] for x in ("trading_bot_accounts.json", "BỎ đối soát", "account_id",
                                      "Error", "lỗi")), r["out"][:400])
check("KHÔNG báo lệch 🚨 / KHÔNG báo khớp ✅ (không đối soát trên dữ liệu gộp)",
      "🚨" not in r["out"] and "✅ Đối soát" not in r["out"] and not r["broker"], r["broker"])
check("stderr + notify.sh STUB nhận lỗi thật", "BỎ đối soát" in r["err"] and "BỎ đối soát" in r["notify"],
      (r["err"][-200:], r["notify"]))

print("\n[ii] record thiếu account_no ⇒ bị loại")
check("SpaceX broker_filled = 100 (không cộng record thiếu account_no 500)", ok_ii(R["ii"]), R["ii"]["broker"])

print("\n[iii] 2 account cùng file ⇒ SpaceX ≠ ZaloPay, mỗi bên đúng của mình")
check("SpaceX = 100", R["iii_S"]["broker"] == {"FPT": 100}, R["iii_S"]["broker"])
check("ZaloPay = 300", R["iii_Z"]["broker"] == {"FPT": 300}, R["iii_Z"]["broker"])
check("SpaceX ≠ ZaloPay", R["iii_S"]["broker"] != R["iii_Z"]["broker"])

def extract_bash(begin, end, sh_text=None):
    """Trích phần THÂN bash giữa 2 marker comment (cùng quy ước với `extract()` của
    check_report_cadence_selfcheck.py — cắt tới HẾT DÒNG chứa marker)."""
    src = sh_text if sh_text is not None else cur_text
    m = re.search(re.escape(begin) + r"[^\n]*\n(.*?)[^\n]*" + re.escape(end), src, re.S)
    if not m:
        print(f"❌ FATAL: không trích được khối {begin}…{end} trong {SCRIPT} — "
              "khối đã bị đổi/di chuyển, selfcheck vô hiệu.")
        sys.exit(1)
    return m.group(1)


_MISMATCH_TAG = "VENDOR_MISMATCH_ALERT|SpaceX|ZZZ|2026-09-24|1000|1500|1"
_LOOKUP_TAG = "VENDOR_LOOKUP_FAILED|SpaceX|ZZZ|2026-09-24|1000|1|1"


def run_eod_vendor_reason(gate_out, vendor_rc=10):
    """Chạy khối EOD_VENDOR_REASON thật (why= rẽ theo TAG trong $gate_out) trên 1 fixture."""
    body = extract_bash("EOD_VENDOR_REASON_BEGIN", "EOD_VENDOR_REASON_END")
    script = ("#!/usr/bin/env bash\nset -uo pipefail\n"
              'gate_out="$1"\nvendor_rc="$2"\nwhy="__WHY_CỦA_KHỐI_TRƯỚC__"\n'
              + body + '\nprintf \'%s\' "$why"\n')
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "reason.sh")
        with open(p, "w", encoding="utf-8") as f:
            f.write(script)
        r = subprocess.run(["bash", p, gate_out, str(vendor_rc)], capture_output=True, text=True)
        if "syntax error" in r.stderr or "command not found" in r.stderr:
            return "__BLOCK_DID_NOT_RUN__: " + r.stderr
        return r.stdout


print("\n[vendor-reason] why= rẽ theo TAG THẬT trong $gate_out, không suy từ vendor_rc=10 "
      "(arch-review 2026-09-24 vòng 6, T1-c)")
why_mismatch = run_eod_vendor_reason(_MISMATCH_TAG)
check("mismatch-only ⇒ why nêu LỆCH NGUỒN VENDOR + Winston",
      "LỆCH NGUỒN VENDOR" in why_mismatch and "Winston" in why_mismatch, why_mismatch)
check("mismatch-only ⇒ KHÔNG lẫn câu lookup_failed",
      "KHÔNG TRA ĐƯỢC nguồn vendor" not in why_mismatch, why_mismatch)

why_lookup = run_eod_vendor_reason(_LOOKUP_TAG)
check("lookup_failed-only ⇒ why nêu lỗi hạ tầng BQ, KHÔNG giao Winston đối soát số",
      "KHÔNG TRA ĐƯỢC nguồn vendor" in why_lookup and "lỗi hạ tầng BQ" in why_lookup, why_lookup)
check("lookup_failed-only ⇒ KHÔNG lẫn câu LỆCH NGUỒN VENDOR (sai nguyên nhân/sai người, §29)",
      "LỆCH NGUỒN VENDOR" not in why_lookup, why_lookup)
assert ("KHÔNG TRA ĐƯỢC nguồn vendor" in why_lookup and "lỗi hạ tầng BQ" in why_lookup
        and why_lookup != "__BLOCK_DID_NOT_RUN__"), (
    "MUTATION-GUARD eod_vendor_reason_lookup_failed_branch: gate_out thuần lookup_failed mà "
    "why= không nêu đúng 'lỗi hạ tầng BQ' — nhánh elif VENDOR_LOOKUP_FAILED đã bị bỏ hoặc hỏng, "
    f"ca rơi về why= mặc định/sai nhánh mismatch. Đang là: {why_lookup!r}")

why_both = run_eod_vendor_reason(_MISMATCH_TAG + "\n" + _LOOKUP_TAG)
check("cả hai tag ⇒ ưu tiên nhánh mismatch (if đứng trước elif)",
      "LỆCH NGUỒN VENDOR" in why_both and "Winston" in why_both, why_both)

why_no10 = run_eod_vendor_reason("", vendor_rc=1)
check("vendor_rc≠10 ⇒ giữ nguyên why= của khối trước (không đổi khi không có tag vendor để so)",
      why_no10 == "__WHY_CỦA_KHỐI_TRƯỚC__", why_no10)


def run_eod_gate_reason(gate_out, gate_rc=1):
    """Chạy khối EOD_GATE_REASON thật (why= đọc từ CHÍNH output của cổng, §29) trên 1 fixture."""
    body = extract_bash("EOD_GATE_REASON_BEGIN", "EOD_GATE_REASON_END")
    script = ("#!/usr/bin/env bash\nset -uo pipefail\nf() {\n"
              'local gate_out="$1" gate_rc="$2"\n' + body + '\nprintf \'%s\' "$why"\n}\nf "$@"\n')
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "reason.sh")
        with open(p, "w", encoding="utf-8") as f:
            f.write(script)
        r = subprocess.run(["bash", p, gate_out, str(gate_rc)], capture_output=True, text=True)
        if r.returncode or "syntax error" in r.stderr or "command not found" in r.stderr:
            return f"__BLOCK_DID_NOT_RUN__ rc={r.returncode}: " + r.stderr
        return r.stdout


print("\n[gate-reason] why= mặc định đọc từ CHÍNH output của cổng, không gán sẵn một nguyên nhân (§29)")
_BLOCKED = ("CỔNG TỈ SUẤT — ZaloPay_daily_report_2026-10-02.md | chốt 2026-10-02\n\n"
            "❌ CHẶN — 2 vấn đề:\n"
            "   • DRI (dòng vị thế báo cáo ngày, dòng 32): báo cáo +28.00% vs kỳ vọng ZaloPay +29.31%\n"
            "   • SAB (dòng vị thế báo cáo ngày, dòng 29): báo cáo -2.60% vs kỳ vọng ZaloPay -4.53%\n"
            "report_delivery_gate: INCOMPLETE — Command '['python3', 'report_return_gate.py']' "
            "returned non-zero exit status 1.\n")
why_blk = run_eod_gate_reason(_BLOCKED)
check("cổng tỉ suất CHẶN ⇒ why nêu đúng số vấn đề + mục ĐẦU TIÊN của khối chặn (bản cũ: 'delivery "
      "chưa đủ kênh (Discord/email)' cho mọi rc≠0)",
      why_blk.startswith("cổng tỉ suất CHẶN — 2 vấn đề: DRI (dòng vị thế báo cáo ngày, dòng 32): "
                         "báo cáo +28.00% vs kỳ vọng ZaloPay +29.31%")
      and "SAB" not in why_blk and "delivery chưa đủ kênh" not in why_blk, why_blk)
why_ch = run_eod_gate_reason("report_delivery_gate: nav-flow PASS (x.md)\n\n"
                             "report_delivery_gate: INCOMPLETE — discord: HTTP 503\n", gate_rc=1)
check("không có khối chặn ⇒ why trích DÒNG CUỐI cổng in ra (lỗi kênh thật) + rc",
      why_ch == "report_delivery_gate rc=1 — dòng cuối cổng in ra: report_delivery_gate: INCOMPLETE "
                "— discord: HTTP 503", why_ch)
why_none = run_eod_gate_reason("", gate_rc=7)
check("cổng không in gì ⇒ nói đúng là không xác định được (kèm rc), không đoán",
      "rc=7" in why_none and "không xác định được nguyên nhân" in why_none
      and "Discord" not in why_none, why_none)
why_json = run_eod_gate_reason('Traceback\n  File "x.py"\nKeyError: "a\\b" \n   nhiều   khoảng trắng\n')
check("why= an toàn để ghép vào chuỗi JSON: không nháy kép, không gạch chéo ngược, một dòng",
      '"' not in why_json and "\\" not in why_json and "\n" not in why_json
      and why_json.endswith("nhiều khoảng trắng"), why_json)
assert why_blk.startswith("cổng tỉ suất CHẶN — 2 vấn đề: DRI"), (
    "MUTATION-GUARD eod_gate_reason: output có khối '❌ CHẶN' mà why= không trích nó — khối "
    f"EOD_GATE_REASON đã bị bỏ/hỏng và nguyên nhân lại bị gán cứng. Đang là: {why_blk!r}")

why_crash = run_eod_gate_reason(
    # (cố ý KHÔNG chép dòng mở đầu traceback của Python vào fixture: các bộ đột biến nhận diện
    #  "selfcheck SẬP" bằng chính chuỗi đó trong output của selfcheck)
    "  File \"report_return_gate.py\", line 1310, in run_gate\n    tot_pl += r[\"pl\"]\n"
    "KeyError: 'pl'\nreport_delivery_gate: INCOMPLETE — Command '['python3', "
    "'report_return_gate.py']' returned non-zero exit status 1.\n")
check("cổng tỉ suất SẬP (traceback, không khối chặn) ⇒ why là dòng lỗi THẬT, không phải dòng bọc "
      "'Command … returned non-zero exit status' (bản 53b48b76: dòng bọc)",
      why_crash == "report_delivery_gate rc=1 — dòng cuối cổng in ra: KeyError: 'pl' (cổng con thoát "
                   "lỗi, không in khối chặn)", why_crash)
why_wrap = run_eod_gate_reason("report_delivery_gate: INCOMPLETE — Command '['python3', 'x.py']' "
                               "returned non-zero exit status 1.\n")
check("chỉ có dòng bọc ⇒ giữ dòng bọc (không còn gì khác để trích)",
      why_wrap.endswith("returned non-zero exit status 1.") and "cổng con thoát lỗi" not in why_wrap,
      why_wrap)

# ── Vỏ bash quanh khối danh mục (K1 + arch-review 53b48b76 F5/F7): chạy NGUYÊN khối EOD_MEMO thật
#    rồi NGUYÊN đoạn python REPORT= trong cùng một tiến trình bash, trên wc_root giả có STUB
#    `mike/bin/portfolio_status.py`. Không có đường nào tới portfolio_status/BQ thật.
STUB_PS = r"""#!/usr/bin/env python3
import os, sys, time
mode = os.environ.get("STUB_PS_MODE", "ok")
d = os.environ.get("DAR_BQ_MEMO_DIR")
print("portfolio_status: QQ2 (SpaceX) không có tỉ suất §21: LÝ-DO-THẬT", file=sys.stderr)
print("/x/google/auth/_default.py:76: FutureWarning: ồn của thư viện", file=sys.stderr)
print("ℹ️  giá: dòng của công cụ tỉ suất", file=sys.stderr)
if mode == "fail":
    print("  File \"x.py\", line 1, in <module>\nValueError: chi tiết nội bộ BÍ-MẬT", file=sys.stderr)
    sys.exit(1)
if mode == "slow":
    time.sleep(6)
print(f"STUB_MEMO_DIR={d} ISDIR={bool(d) and os.path.isdir(d)} ARGS={' '.join(sys.argv[1:])}")
"""
NEUTRAL_PS = "Chưa có bảng tình trạng danh mục cho báo cáo hôm nay"


def run_shell(py, mode="ok", preset=False, account="SpaceX"):
    """{rc, out (báo cáo), err (log), memo (đường dẫn sổ nhớ stub thấy), tmp_after, preset}."""
    accts = [{"label": a, "account_id": n} for a, n in ACCT_NO.items()]
    root = build_root(accts, [order_rec(ACCT_NO[account], 1, 0)])
    tmp = tempfile.mkdtemp(prefix="eod_shell_sc_")
    try:
        with open(os.path.join(root, "mike", "bin", "portfolio_status.py"), "w", encoding="utf-8") as f:
            f.write(STUB_PS)
        two_days = __import__("time").time() - 2 * 86400
        for name, old_ in (("eod_bq_memo.OLD", True), ("eod_bq_memo.FRESH", False),
                           ("other_tool.OLD", True)):
            dpath = os.path.join(tmp, name)
            os.makedirs(dpath)
            open(os.path.join(dpath, "x.json"), "w").close()
            if old_:
                os.utime(dpath, (two_days, two_days))
        pre = os.path.join(tmp, "caller_memo")
        os.makedirs(pre)
        script = ("#!/usr/bin/env bash\nset -uo pipefail\n"
                  + extract_bash("EOD_MEMO_BEGIN", "EOD_MEMO_END", sh_text=SH_TEXT)
                  + f'\npython3 - plan.json "{root}/state/state_{account}.json" "{account}" "{DATE}" '
                    f'"{root}" << \'PYEOF\'\n' + py + "PYEOF\n")
        spath = os.path.join(root, "harness.sh")
        with open(spath, "w", encoding="utf-8") as f:
            f.write(script)
        env = {"PATH": os.path.join(root, "mike", "bin") + ":/usr/bin:/bin", "HOME": root,
               "LANG": "C.UTF-8", "TMPDIR": tmp, "STUB_PS_MODE": mode}
        if preset:
            env["DAR_BQ_MEMO_DIR"] = pre
        r = subprocess.run(["bash", spath], capture_output=True, text=True, env=env, cwd=root,
                           timeout=120)
        m = re.search(r"STUB_MEMO_DIR=(\S+) ISDIR=(\S+) ARGS=(.*)", r.stdout)
        return {"rc": r.returncode, "out": r.stdout, "err": r.stderr,
                "memo": m.group(1) if m else None, "isdir": m.group(2) if m else None,
                "args": m.group(3).strip() if m else None, "tmp": tmp,
                "memo_alive": bool(m) and os.path.isdir(m.group(1)),
                "after": sorted(os.listdir(tmp)), "pre": pre}
    finally:
        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(tmp, ignore_errors=True)


print("\n[vỏ bash] sổ nhớ BQ của lượt chạy + lời gọi portfolio_status (stub) — chạy khối thật")
SH_TEXT = cur_text
S = run_shell(cur_py)
check("biến `DAR_BQ_MEMO_DIR` TỚI tiến trình con portfolio_status (phải `export`): stub thấy một thư "
      "mục `eod_bq_memo.*` dưới TMPDIR đang TỒN TẠI lúc nó chạy; đúng tham số --account/--date",
      S["rc"] == 0 and bool(S["memo"]) and S["memo"].startswith(os.path.join(S["tmp"], "eod_bq_memo."))
      and S["isdir"] == "True" and S["args"] == f"--account SpaceX --date {DATE}",
      (S["rc"], S["memo"], S["isdir"], S["args"], S["err"][-300:]))
check("thư mục sổ nhớ của lượt bị XOÁ khi tiến trình bash thoát (trap EXIT)",
      S["memo"] is not None and not S["memo_alive"], S["after"])
check("dọn rác SIGKILL: `eod_bq_memo.*` cũ hơn 1 ngày bị xoá; cái MỚI (lượt tài khoản kia đang chạy) "
      "và thư mục tên khác thì không đụng",
      S["after"] == ["caller_memo", "eod_bq_memo.FRESH", "other_tool.OLD"], S["after"])
check("stderr của portfolio_status được CHUYỂN ra log: dòng `portfolio_status:` và dòng của công cụ "
      "tỉ suất có mặt, FutureWarning của thư viện thì không; không dòng nào lọt vào báo cáo",
      "portfolio_status: QQ2 (SpaceX) không có tỉ suất §21: LÝ-DO-THẬT" in S["err"]
      and "ℹ️  giá: dòng của công cụ tỉ suất" in S["err"] and "FutureWarning" not in S["err"]
      and "LÝ-DO-THẬT" not in S["out"], S["err"][-400:])
SP = run_shell(cur_py, preset=True)
check("caller ĐÃ đặt `DAR_BQ_MEMO_DIR` ⇒ dùng đúng thư mục đó, không tạo cái mới, không xoá của caller",
      SP["memo"] == SP["pre"] and "caller_memo" in SP["after"]
      and not [x for x in SP["after"] if x.startswith("eod_bq_memo.") and x != "eod_bq_memo.FRESH"],
      (SP["memo"], SP["after"]))
_to = re.findall(r'"portfolio_status\.py"\),.*?timeout=(\d+),', cur_py, re.S)
check("trần thời gian lời gọi portfolio_status ghim 600s (công cụ tỉ suất đo ~110-167s; 60s cũ là "
      "cắt ngang MỌI lượt có lệnh)", _to == ["600"], str(_to))
SF = run_shell(cur_py, mode="fail")
check("portfolio_status lỗi ⇒ báo cáo in MỘT câu trung tính — không tên script, không lệnh, không "
      "traceback/thông báo lỗi nội bộ (bản SpaceX gửi nhà đầu tư)",
      SF["rc"] == 0 and NEUTRAL_PS in SF["out"]
      and not any(x in SF["out"] for x in ("portfolio_status", "BÍ-MẬT", "x.py", "ValueError",
                                           "Command", "rc=")), SF["out"][:400])
check("… và lý do THẬT (dòng cuối stderr + rc) vào log",
      "portfolio_status: KHÔNG ra khối danh mục (SpaceX " + DATE + ") — ValueError: chi tiết nội bộ "
      "BÍ-MẬT [rc=1]" in SF["err"], SF["err"][-400:])
_fast = cur_py.replace("cwd=wc_root, timeout=600,", "cwd=wc_root, timeout=1,")
ST = run_shell(_fast, mode="slow") if _fast != cur_py else {"rc": -1, "out": "", "err": "không thay được timeout"}
check("portfolio_status QUÁ GIỜ (trần ép về 1s cho ca này) ⇒ vẫn câu trung tính; chuỗi 'Command … "
      "timed out' chỉ nằm trong log",
      ST["rc"] == 0 and NEUTRAL_PS in ST["out"]
      and not any(x in ST["out"] for x in ("timed out", "Command", "portfolio_status"))
      and "portfolio_status: KHÔNG gọi được (SpaceX " + DATE + ") — TimeoutExpired" in ST["err"],
      (ST["out"][:300], ST["err"][-300:]))
assert S["memo"] and S["isdir"] == "True" and not S["memo_alive"], (
    "MUTATION-GUARD eod_memo: khối EOD_MEMO không còn export sổ nhớ tới tiến trình con hoặc không "
    f"dọn khi thoát. Đang là: memo={S['memo']!r} isdir={S['isdir']!r} alive={S['memo_alive']!r}")

print(f"\n[RED] CHỨNG MINH NGƯỢC trên bản trước vá {PRE_FIX_REF}: (i)/(ii) phải ĐỎ")
if old_py is not None:
    O = scenarios(old_py)
    check("bản cũ (i) ĐỎ — gộp order account khác / không có câu trung tính",
          not ok_i(O["i"]), {"broker": O["i"]["broker"], "neutral": NEUTRAL in O["i"]["out"]})
    check("bản cũ (ii) ĐỎ — record thiếu account_no lọt vào", not ok_ii(O["ii"]), O["ii"]["broker"])

print(f"\n{'=' * 70}\nKẾT QUẢ: {len(PASS)} PASS / {len(FAIL)} FAIL")
if FAIL:
    print("FAIL:")
    for f in FAIL:
        print("  ·", f)
    sys.exit(1)
