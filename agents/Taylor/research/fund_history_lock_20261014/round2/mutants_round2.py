#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutant vòng 2 (job Taylor_20261014_033336): bộ mutant của arch-reviewer (REVIEW.md, trừ Sa–Sh
vì khối giá thay đã bị GỠ khỏi daily_nav_snapshot.py) + mutant MỚI nhắm code B2/B4/B6/B7/B12/
B13/B14/G19.

Mỗi mutant: chép bin/ của worktree sang /tmp, thay ĐÚNG MỘT chỗ (chuỗi phải xuất hiện đúng 1 lần),
chạy selfcheck liên quan với WC_ROOT = sandbox RỖNG (chỉ wc_env.sh + symlink trading_bot), gỡ TZ.
"chết" = ít nhất một selfcheck rc != 0. Chạy song song.

Dùng: python3 mutants_round2.py [--only N2,B2a] [--tz Pacific/Kiritimati] [--jobs 12]
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

WT = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-fundlock-1014"
EMPTY = "/tmp/fl2/empty"
REVIEWER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reviewer_mutants.json")
L, F = "nav_unit_ledger.py", "fund_restatement.py"
V, R, U = "nav_ledger_vault_selfcheck.py", "fund_restatement_selfcheck.py", "nav_unit_ledger_selfcheck.py"

NEW = [
    # ---------------- B2: thư mục dữ liệu thật
    ("B2a", L, "return real in (os.path.realpath(CANONICAL_REAL_DIR), os.path.realpath(NAV_HISTORY_DIR))",
     "return real in (os.path.realpath(NAV_HISTORY_DIR),)", "bỏ cây cố định (chỉ còn WC_ROOT)", (R, V)),
    ("B2b", L, "return real in (os.path.realpath(CANONICAL_REAL_DIR), os.path.realpath(NAV_HISTORY_DIR))",
     "return real in (os.path.realpath(CANONICAL_REAL_DIR),)", "bỏ NAV_HISTORY_DIR", (R, V)),
    ("B2c", L, 'return any(n.startswith("dnse_raw_") and n.endswith(".jsonl") for n in names)',
     "return False", "bỏ luật (b) dnse_raw", (R, V)),
    ("B2d", L, 'return any(n.startswith("dnse_raw_") and n.endswith(".jsonl") for n in names)',
     'return any(n.startswith("dnse_raw_") for n in names)', "luật (b) lỏng: mọi file dnse_raw_*", (R, V)),
    ("B2e", F, "if nul.is_real_data_dir(args.nav_dir) and not args.real_data:",
     "if nul.is_canonical_dir(args.nav_dir) and not args.real_data:", "apply: chỉ chặn cây canonical", (R, V)),
    ("B2f", L, "    return is_real_data_dir(os.path.dirname(os.path.abspath(path)))",
     "    return is_canonical_dir(os.path.dirname(os.path.abspath(path)))", "seal/restate: chỉ chặn canonical", (V,)),
    ("B2g", L, 'CANONICAL_REAL_DIR = "/home/trido/thanhdt/WorkingClaude/data/execution_logs"',
     'CANONICAL_REAL_DIR = "/home/trido/thanhdt/WorkingClaude/data/execution_log"', "sai đường dẫn cố định", (R, V)),
    # ---------------- B4: khung giờ + md5 đọc lại
    ("B4a", F, "APPLY_WINDOW_ICT = (datetime.time(9, 0), datetime.time(18, 30))",
     "APPLY_WINDOW_ICT = (datetime.time(8, 0), datetime.time(18, 30))", "khung mở sớm 08:00", (R, V)),
    ("B4b", F, "APPLY_WINDOW_ICT = (datetime.time(9, 0), datetime.time(18, 30))",
     "APPLY_WINDOW_ICT = (datetime.time(9, 0), datetime.time(19, 30))", "khung đóng muộn 19:30", (R, V)),
    ("B4c", F, "    if not lo <= now.time().replace(tzinfo=None) <= hi:", "    if False:", "bỏ khung giờ", (R, V)),
    ("B4d", F, "        return _clock().astimezone(ICT)", "        return _clock()", "đồng hồ không quy về ICT", (R, V)),
    ("B4e", F, "    if nul.is_canonical_dir(nav_dir):\n        raise RestatementError(\n            f\"biến môi trường",
     "    if False:\n        raise RestatementError(\n            f\"biến môi trường", "giờ giả được nhận ở thư mục thật", (R, V)),
    ("B4f", F, "        if seen != bound[2]:", "        if False:", "bỏ đọc lại md5 trước os.replace", (R, V)),
    ("B4g", F, '                       and last.get("status") != "aborted")', "                       )",
     "bản ghi 'aborted' bị coi là lần áp dở", (R, V)),
    ("B4h", F, "    return fake.replace(tzinfo=ICT) if fake.tzinfo is None else fake.astimezone(ICT)",
     "    return fake.replace(tzinfo=ICT)", "giờ giả có múi giờ bị đọc như ICT", (R, V)),
    ("B4i", F, '            _append_log(log, {k: record[k] for k in key} | {',
     '            (lambda *a: None)(log, {k: record[k] for k in key} | {', "huỷ mà không ghi 'aborted'", (R, V)),
    # ---------------- B6: lời nhận gắn với dòng
    ("B6a", L, "            elif isinstance(old, dict) and {k: old.get(k) for k in ident} == ident:",
     "            elif isinstance(old, dict):", "mang lời nhận cũ không kiểm danh tính", (V,)),
    ("B6b", L, "            elif isinstance(old, dict) and {k: old.get(k) for k in ident} == ident:",
     '            elif isinstance(old, dict) and old.get("nav") == ident["nav"]:', "chỉ kiểm NAV, bỏ giờ chụp", (V,)),
    ("B6c", L, "            elif isinstance(old, dict) and {k: old.get(k) for k in ident} == ident:",
     '            elif isinstance(old, dict) and old.get("balance_ts") == ident["balance_ts"]:', "chỉ kiểm giờ, bỏ NAV", (V,)),
    ("B6d", L, "                accepted[key] = dict(ident, reason=accept_preclose[key])",
     "                accepted[key] = accept_preclose[key]", "lời nhận mới không lưu danh tính", (V,)),
    ("B6e", L, "                                           carried=_accepted_so_far(manifest))",
     "                                           carried={})", "restate không mang lời nhận cũ", (V,)),
    ("B6f", L, "            elif isinstance(old, dict) and {k: old.get(k) for k in ident} == ident:",
     "            elif old is not None:", "lời nhận kiểu chuỗi cũ vẫn được mang", (V,)),
    # ---------------- B7: impact
    ("B7a", F, '"monthly": ("mtd", "qtd", "ytd", "inception")}', '"monthly": ("mtd", "ytd", "inception")}',
     "báo cáo tháng thiếu QTD", (R, V)),
    ("B7b", F, '"monthly": ("mtd", "qtd", "ytd", "inception")}', '"monthly": ("mtd", "qtd", "inception")}',
     "báo cáo tháng thiếu YTD", (R, V)),
    ("B7c", F, "quarter = datetime.date(asof.year, 3 * ((asof.month - 1) // 3) + 1, 1)",
     "quarter = datetime.date(asof.year, asof.month, 1)", "QTD tính như MTD", (R, V)),
    ("B7d", F, '        if not (name.endswith(".md") or ".md.bak_sent_" in name):',
     '        if not name.endswith(".md"):', "bỏ qua bản .bak_sent (bản đã gửi)", (R, V)),
    ("B7e", F, "        if start <= d <= end and nav_new == nav_old and money:", "        if False:",
     "đổi cột tiền giữ NAV ⇒ 'không ảnh hưởng'", (R, V)),
    ("B7f", F, "        if start <= d <= end and nav_new == nav_old and money:",
     "        if d <= end and nav_new == nav_old and money:", "đổi cột tiền kéo cả báo cáo ngoài kỳ", (R, V)),
    ("B7g", F, '        or bool(out["component_changes"]))', "        )", "đổi cột tiền không vào hàng đợi", (R, V)),
    ("B7h", F, 'MONEY_COLUMNS = ("mtm_stock", "cash", "margin_debt", "offbook_assets", "egg_assets",',
     'MONEY_COLUMNS = ("mtm_stock", "margin_debt", "offbook_assets", "egg_assets",', "bỏ cột cash", (R, V)),
    ("B7i", F, "            if hits:\n                out[\"literal_hits_new\"]",
     "            if False:\n                out[\"literal_hits_new\"]", "không tìm NAV mới của dòng chèn", (R, V)),
    ("B7j", F, "        if hits and nav_new != nav_old:", "        if hits:", "trích NAV không đổi vẫn tính lệch", (R, V)),
    # ---------------- B14: sao lưu
    ("B14a", F, "                and _read_bytes(os.path.join(folder, name)) == data):", "                and False):",
     "không dùng lại bản sao lưu ⇒ chép bản hai", (R, V)),
    ("B14b", F, '        with open(path, "xb") as f:', '        with open(path, "wb") as f:', "ghi đè bản sao lưu", (R, V)),
    ("B14c", F, '"backup": os.path.relpath(backup, args.nav_dir),', '"backup": None,', "nhật ký mất đường sao lưu", (R, V)),
    ("B14d", F, "    backup = _backup_nav_history(args.nav_dir, args.account, cur_bytes, now)",
     "    backup = _backup_nav_history(args.nav_dir, args.account, new_bytes, now)", "sao lưu byte SAU khi sửa", (R, V)),
    # ---------------- B12 / B13
    ("B12a", L, "        if not os.path.exists(lock_path):", "        if True:", "đối chiếu chỉ-đọc không chờ khoá", (V,)),
    ("B13a", L, "            if args.seal or args.restate:", "            if True:", "SEAL_MD5 in cả khi chỉ đối chiếu", (V,)),
    ("B13b", L, 'print(f"SEAL_MD5 {args.account} {_file_md5(path)} {_file_md5(manifest_path(path))}")',
     'print(f"SEAL_MD5 {args.account} {_file_md5(manifest_path(path))} {_file_md5(path)}")', "đảo thứ tự md5", (V,)),
    # ---------------- G19 tầng áp
    ("G19b", F, "        if not isinstance(item.get(\"expect\"), dict):\n            raise RestatementError(f\"{where}: thiếu expect",
     "        if False:\n            raise RestatementError(f\"{where}: thiếu expect", "apply_corrections: KeyError trần", (R, V)),
    # ---------------- 7 mutant vòng 1 (mutants.py) không dựng được trên code vòng 2 — port cùng ý đồ
    ("L25p", L, "            problems, accepted = seal_gate(ledger, rows[0][\"date\"], rows, accept_preclose or {},\n"
     "                                           carried=_accepted_so_far(manifest))",
     "            problems, accepted = [], {}", "restate bỏ qua cổng chốt", (V,)),
    ("L28p", L, "        diffs = diff_against_sealed(ledger, sealed)\n        if diffs:\n            raise LedgerDriftError(path, diffs)\n        return sealed, []",
     "        diffs = []\n        if diffs:\n            raise LedgerDriftError(path, diffs)\n        return sealed, []",
     "đối chiếu chỉ-đọc kho bất biến không báo lệch dòng", (V,)),
    ("L36p", L, "                                           carried=_accepted_so_far(manifest))",
     "                                           carried=None)", "restate quên lời nhận của các lần chốt trước", (V,)),
    ("F12p", F, '        or (bool(structural) and out["tier_headline"] < 2)\n', "        or False\n",
     "kỳ có dòng thêm/bỏ không gọi người xem", (R,)),
    ("F17p", F, "    if nul.is_real_data_dir(args.nav_dir) and not args.real_data:",
     "    if nul.is_real_data_dir(args.nav_dir) and False:", "apply vào thư mục thật không cần --real-data", (R,)),
    ("F20p", F, "    if not pending:\n        _append_log(log, record)", "    if True:\n        _append_log(log, record)",
     "chạy lại sau khi chết ghi bản ghi nhật ký thứ hai", (R,)),
    ("F31p", F, "        if ra != rb:", "        if (ra or {}).get('nav') != (rb or {}).get('nav'):",
     "changed_dates chỉ so cột nav", (R,)),
]


def load_reviewer():
    out = []
    for mid, fn, old, new, desc, scs in json.load(open(REVIEWER, encoding="utf-8")):
        if mid == "G26":            # dòng code đổi ở vòng 2 (thêm điều kiện 'aborted'); cùng ý đồ
            old = "            pending = (all(last.get(k) == record[k] for k in key)"
            new = "            pending = (all(last.get(k) == record[k] for k in key[:1])"
        if mid == "G14":            # ghi nhật ký tách thành _append_log ở vòng 2; cùng ý đồ
            old = "    if not pending:\n        _append_log(log, record)"
            new = "    if False:\n        _append_log(log, record)"
        if mid == "N10":            # bộ lọc lời nhận cũ đã thay bằng kiểm danh tính (B6) ⇒ ý đồ = B6e/B6a
            continue
        if mid == "N14":            # _is_real_dir viết lại (B2); ý đồ "bỏ realpath" giữ nguyên
            old = "    real = os.path.realpath(os.path.abspath(directory))\n    return real in"
            new = "    real = directory\n    return real in"
        out.append((mid, fn, old, new, desc, tuple(scs)))
    return out


def run_one(m, tz):
    mid, fn, old, new, desc, scs = m
    d = tempfile.mkdtemp(prefix=f"mut_{mid}_", dir="/tmp/fl2/mut")
    try:
        shutil.copytree(os.path.join(WT, "bin"), d + "/bin")
        p = d + "/bin/" + fn
        s = open(p, encoding="utf-8").read()
        n = s.count(old)
        if n != 1:
            return (mid, f"LỖI-DỰNG({n})", fn, desc, "")
        open(p, "w", encoding="utf-8").write(s.replace(old, new))
        for sc in scs:
            env = dict(os.environ, WC_ROOT=EMPTY)
            env.pop("TZ", None)
            if tz:
                env["TZ"] = tz
            r = subprocess.run([sys.executable, d + "/bin/" + sc], cwd="/tmp", env=env,
                               capture_output=True, text=True, timeout=600)
            if r.returncode != 0:
                fl = [x for x in (r.stdout + r.stderr).splitlines() if "FAIL" in x or "Error" in x]
                return (mid, "chết", fn, desc, f"{sc} rc={r.returncode}: {fl[0] if fl else ''}"[:200])
        return (mid, "SỐNG", fn, desc, "")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--tz")
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("--set", choices=("all", "new", "reviewer"), default="all")
    a = ap.parse_args()
    ms = (load_reviewer() if a.set in ("all", "reviewer") else []) + (NEW if a.set in ("all", "new") else [])
    if a.only:
        keep = set(a.only.split(","))
        ms = [m for m in ms if m[0] in keep]
    with ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(lambda m: run_one(m, a.tz), ms))
    for r in res:
        print(r, flush=True)
    print(f"\nTỔNG {len(res)} chết {sum(r[1] == 'chết' for r in res)} SỐNG {sum(r[1] == 'SỐNG' for r in res)} "
          f"lỗi {sum(r[1].startswith('LỖI') for r in res)}  (tz={a.tz or 'gỡ TZ'})")
    for r in res:
        if r[1] != "chết":
            print("  ", r[0], r[1], r[2], r[3])


if __name__ == "__main__":
    main()
