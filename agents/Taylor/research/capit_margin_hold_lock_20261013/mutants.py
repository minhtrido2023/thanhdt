#!/usr/bin/env python3
"""Mutation test cho khoá giữ CAPIT margin: mỗi mutant = 1 chỗ sửa hỏng có tên, chạy
`bin/capit_margin_hold_selfcheck.py` với CMH_OVERRIDE_DIR trỏ bản đã sửa hỏng. Bị BẮT = selfcheck
rc≠0 (ghi kèm ca nào bắt). Mutant SỐNG ở các nhóm nhắm tới được chạy lại với TOÀN BỘ selfcheck
trước khi ghi là sống.

    python3 agents/Taylor/research/capit_margin_hold_lock_20261013/mutants.py [tên…]
"""
import concurrent.futures as cf
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
BIN = os.path.join(WT, "bin")
BASE = os.environ.get("CMH_BASELINE_DIR", "")
H, A, P, S = ("capit_margin_hold.py", "approve_margin_day.py", "approve_plan_simple.sh",
              "send_plan_report.sh")

M = [  # (tên, file, nhóm selfcheck nhắm tới, old, new, mô tả)
 ("M01", H, "A", "    except FileNotFoundError:\n        return out\n    except OSError as ex:",
  "    except OSError:\n        return out\n    except OSError as ex:",
  "mọi OSError khi kiểm file (kể cả PermissionError) ⇒ không giữ"),
 ("M02", H, "A", "        os.lstat(path)",
  "        if not os.path.exists(path):\n            raise FileNotFoundError(path)",
  "os.path.exists thay lstat (symlink treo / thư mục cha khoá ⇒ không giữ)"),
 ("M03", H, "A C D E", "        out.update(corrupt=True, error=f\"{type(ex).__name__}: {ex}\")",
  "        out.update(held=False, corrupt=True, error=f\"{type(ex).__name__}: {ex}\")",
  "file hỏng ⇒ KHÔNG giữ (fail-open)"),
 ("M04", H, "A", "    out[\"held\"] = True\n    try:\n        with open(path",
  "    try:\n        with open(path", "bỏ gán held=True trước khi parse (file hỏng ⇒ không giữ; file tốt cũng mất held)"),
 ("M05", H, "A", "        if bad:\n", "        if False:\n", "bỏ kiểm field bắt buộc"),
 ("M06", H, "A", "        if not isinstance(rec, dict):\n", "        if False:\n",
  "bỏ kiểm 'phải là object' (dự đoán TƯƠNG ĐƯƠNG: rec.get ném AttributeError, vẫn bị bắt thành hỏng)"),
 ("M07", H, "A", "        dt.datetime.fromisoformat(rec[\"since\"])\n", "",
  "bỏ kiểm since là ISO"),
 ("M08", H, "A", "if not (isinstance(rec.get(k), str) and rec[k].strip())]",
  "if not rec.get(k)]", "field bắt buộc: chấp nhận số / chuỗi toàn dấu cách"),
 ("M09", H, "B D", "    return RC_NOT_HELD if not h[\"held\"] else (RC_HELD_CORRUPT if h[\"corrupt\"] else RC_HELD)",
  "    return RC_NOT_HELD", "status luôn rc 0 (shell tưởng không giữ)"),
 ("M10", H, "B", "    if who.lower() in APPROVAL_PLACEHOLDERS:\n        print(f\"❌ --by",
  "    if False:\n        print(f\"❌ --by", "off: bỏ kiểm placeholder"),
 ("M11", H, "B", "    if who.lower() in APPROVAL_PLACEHOLDERS:\n        print(f\"❌ --by",
  "    if who in APPROVAL_PLACEHOLDERS:\n        print(f\"❌ --by", "off: so placeholder phân biệt hoa/thường"),
 ("M12", H, "B", "    who = (args.by or \"\").strip()\n    if who.lower()", "    who = (args.by or \"\")\n    if who.lower()",
  "off: không strip --by (\"  \" / \" TBD \" lọt)"),
 ("M13", H, "B", "    os.remove(HOLD_PATH)\n", "    pass\n", "off: không xoá file giữ"),
 ("M14", H, "B", "    if h[\"held\"] and not h[\"corrupt\"]:\n        print(f\"⚠ đã giữ sẵn",
  "    if False:\n        print(f\"⚠ đã giữ sẵn", "on: ghi đè lệnh giữ đang có"),
 ("M15", H, "B", "        since = since.replace(tzinfo=ICT)\n", "        pass\n", "on: --since không neo ICT"),
 ("M16", H, "B", "        ok_b, ok_n = _bus(\"decision\", topic, payload), _notify(msg)",
  "        ok_b, ok_n = True, True", "bật/gỡ KHÔNG ghi bus, KHÔNG báo Discord mà vẫn rc 0"),
 ("M17", H, "B", "nguyên.\", file=sys.stderr)\n        return 2\n    who =",
  "nguyên.\", file=sys.stderr)\n        APPROVAL_PLACEHOLDERS = ()\n    who =",
  "off: không nạp được APPROVAL_PLACEHOLDERS ⇒ vẫn gỡ (fail-open)"),
 ("M18", H, "B", "        if d >= today and revoked in (False, None, \"\", 0, \"false\", \"False\", \"no\", \"0\"):",
  "        if d >= today:", "on: liệt kê cả bản duyệt ĐÃ thu hồi"),
 ("M19", H, "B", "        if d >= today and revoked in", "        if revoked in", "on: liệt kê cả bản duyệt quá khứ"),
 ("M20", H, "B", "    if args.dry_run:\n        print(f\"[dry-run] sẽ ghi {HOLD_PATH}", "    if False:\n        print(f\"[dry-run] sẽ ghi {HOLD_PATH}",
  "on --dry-run vẫn ghi file"),
 ("M21", H, "B", "{\"action\": \"on\", \"hold\": rec, \"decided_by\": args.decided_by,",
  "{\"action\": \"on\", \"hold\": rec, \"decided_by\": \"user\",", "on: bus luôn tự nhận decided_by=user"),
 ("M22", H, "B", "        if h[\"corrupt\"] and os.path.lexists(HOLD_PATH):", "        if False:",
  "on đè file hỏng mà không giữ bản hỏng"),
 ("M23", H, "B D E", "\"cờ vay và GIỮ NGUYÊN khối lượng plan", "\"cờ vay và hạ khối lượng về phần tiền mặt",
  "câu 09:05 nói SAI hành vi thật (hạ khối lượng)"),
 ("N01", A, "C", "    if hold[\"held\"]:\n        print(f\"🔒", "    if False:\n        print(f\"🔒", "approve_margin_day: bỏ cổng giữ"),
 ("N02", A, "C", "                      file=sys.stderr)\n                return 4\n", "                      file=sys.stderr)\n",
  "in lời từ chối nhưng vẫn ghi bản duyệt"),
 ("N03", A, "C", "            if not args.dry_run:\n                print(f\"❌ TỪ CHỐI", "            if True:\n                print(f\"❌ TỪ CHỐI",
  "--dry-run cũng bị từ chối khi đang giữ"),
 ("N04", A, "C", "            if override.lower() in PLACEHOLDER:", "            if False:", "--override-hold: bỏ kiểm placeholder"),
 ("N05", A, "C", "            override = args.override_hold.strip()", "            override = args.override_hold",
  "--override-hold: không strip (\"  \" lọt)"),
 ("N06", A, "C", "    if override is not None:\n        # Bản duyệt tự nói", "    if False:\n        # Bản duyệt tự nói",
  "vượt giữ nhưng bản duyệt KHÔNG ghi dấu vượt"),
 ("N07", A, "C", "    if override is not None:\n        msg = (f\"⚠️ **VƯỢT", "    if False:\n        msg = (f\"⚠️ **VƯỢT",
  "vượt giữ nhưng Discord KHÔNG ghi dấu vượt"),
 ("N08", A, "C", "**({\"overrode_capit_margin_hold\": True} if override is not None else {})", "",
  "vượt giữ nhưng bus thiếu cờ overrode_capit_margin_hold"),
 ("N09", A, "C", "    if hold[\"held\"]:\n        print(f\"🔒", "    if hold[\"held\"] and not hold[\"corrupt\"]:\n        print(f\"🔒",
  "file giữ hỏng ⇒ approve_margin_day coi như không giữ"),
 ("N10", A, "C", "    override = None\n    if hold[\"held\"]:", "    override = args.override_hold\n    if hold[\"held\"]:",
  "không giữ mà có --override-hold ⇒ vẫn gắn dấu vượt giữ"),
 ("N11", A, "C", "    if args.revoke:\n        if not os.path.exists(path):",
  "    if args.revoke and capit_margin_hold.read_hold()[\"held\"]:\n        return 4\n    if args.revoke:\n        if not os.path.exists(path):",
  "đang giữ thì --revoke cũng bị chặn"),
 ("N12", A, "C", "        rec[\"note\"] = \"VƯỢT LỆNH GIỮ CAPIT MARGIN (--override-hold). \" + rec[\"note\"]\n", "",
  "vượt giữ: note của bản duyệt không ghi VƯỢT"),
 ("P01", P, "D", "  if [[ \"$_HOLD_RC\" -eq 0 ]]; then", "  if true; then",
  "approve_plan_simple: bỏ kiểm giữ (vẫn gọi approve_margin_day.py — lớp 2 sẽ tự từ chối)"),
 ("P02", P, "D", "  if [[ \"$_HOLD_RC\" -eq 0 ]]; then", "  if [[ \"$_HOLD_RC\" -ne 3 && \"$_HOLD_RC\" -ne 4 ]]; then",
  "rc lạ của status (script hỏng/thiếu) ⇒ coi như KHÔNG giữ"),
 ("P03", P, "D", "    \"$MIKE_ROOT/bin/notify_thread.sh\" \"$_HOLD_MSG\" plan_approval \\", "    true \"$_HOLD_MSG\" plan_approval \\",
  "đang giữ: không báo Discord"),
 ("P04", P, "D", "    \"$MIKE_ROOT/bin/append_event.sh\" Mike status \"margin-day-approval-held-${ACCOUNT}-${PLAN_DATE}\" \\",
  "    true Mike status \"margin-day-approval-held-${ACCOUNT}-${PLAN_DATE}\" \\", "đang giữ: không ghi bus"),
 ("P05", P, "D", "capit_margin_hold.py\" status --consequence 2>&1)", "capit_margin_hold.py\" status 2>&1)",
  "đang giữ: không nói điều xảy ra lúc 09:05"),
 ("P06", P, "D", "if [[ \"${_LEVERAGED:-0}\" -gt 0 ]]; then\n  _HOLD_OUT", "if true; then\n  _HOLD_OUT",
  "plan KHÔNG có lệnh đòn bẩy cũng đi vào nhánh giữ"),
 ("P07", P, "D", "    if [[ \"$_HOLD_RC\" -ne 3 && \"$_HOLD_RC\" -ne 4 ]]; then\n      _HOLD_OUT=\"KHÔNG xác định",
  "    if false; then\n      _HOLD_OUT=\"KHÔNG xác định", "rc lạ: không nói 'KHÔNG xác định được' (đổ lỗi chung chung)"),
 ("S01", S, "E", "            _hold_line = _cmh.report_line(_hold) if _hold[\"held\"] else \"\"",
  "            _hold_line = \"\"", "send_plan_report: không bao giờ hiện dòng giữ"),
 ("S02", S, "E", "            _hold_line = _cmh.report_line(_hold) if _hold[\"held\"] else \"\"",
  "            _hold_line = _cmh.report_line(_hold)", "hiện dòng giữ cả khi KHÔNG giữ"),
 ("S03", S, "E", "            _hold_then = \"\"\n        if _rec is not None:", "            _hold_then = \"\"\n            _hold_line = \"\"\n        if _rec is not None:",
  "không đọc được trạng thái giữ ⇒ im lặng, vẫn hứa 'tự động' (fail-open)"),
 ("S04", S, "E", "        elif _hold_line:\n            margin_note.append(f\"   {_hold_line}\")", "        elif False:\n            margin_note.append(f\"   {_hold_line}\")",
  "đang giữ mà vẫn in 'Đồng ý plan = duyệt margin tự động'"),
 ("S05", S, "E", "            if _hold_then:\n", "            if False:\n", "đang giữ: bỏ câu điều xảy ra lúc 09:05"),
 ("S06", S, "E", "            if _hold_line:\n                margin_note.append(f\"   {_hold_line}\")\n                margin_note.append(\n                    \"   ⚠️ Bản duyệt",
  "            if False:\n                margin_note.append(f\"   {_hold_line}\")\n                margin_note.append(\n                    \"   ⚠️ Bản duyệt",
  "đang giữ + đã có bản duyệt: không cảnh báo bản duyệt vẫn hiệu lực"),
 ("S07", S, "E", "                       if _rec.get(\"hold_override\") else", "                       if False else",
  "bản duyệt vượt giữ: báo cáo không trích nguyên văn vượt"),
 ("S08", S, "E", "            _hold = _cmh.read_hold()\n", "            _hold = {\"held\": False}\n",
  "send_plan_report: không đọc file giữ"),
]


def run(mut, groups=None):
    name, fname, tgt, old, new, desc = mut
    src = open(os.path.join(BIN, fname), encoding="utf-8").read()
    if src.count(old) != 1:
        return name, "LỖI-MUTANT", f"mẫu xuất hiện {src.count(old)} lần (cần đúng 1)", desc
    d = tempfile.mkdtemp(prefix=f"cmh_mut_{name}_")
    p = os.path.join(d, fname)
    with open(p, "w", encoding="utf-8") as f:
        f.write(src.replace(old, new))
    os.chmod(p, 0o755)
    env = dict(os.environ, CMH_OVERRIDE_DIR=d)
    if BASE:
        env["CMH_BASELINE_DIR"] = BASE
    g = (groups if groups is not None else tgt.split())
    r = subprocess.run([sys.executable, os.path.join(BIN, "capit_margin_hold_selfcheck.py")] + g,
                       capture_output=True, text=True, env=env, timeout=3000)
    fails = re.findall(r"^\[FAIL\] (\S+)", r.stdout, re.M)
    tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:]
    if r.returncode != 0 and fails:
        return name, "BỊ BẮT", ",".join(sorted(set(fails)))[:90], desc
    if r.returncode != 0:
        return name, "LỖI-CHẠY", tail, desc
    return name, "SỐNG", tail, desc


def main():
    want = set(sys.argv[1:])
    muts = [m for m in M if not want or m[0] in want]
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        res = list(ex.map(run, muts))
    alive = [r[0] for r in res if r[1] == "SỐNG"]
    if alive:                                 # sống ở nhóm nhắm tới ⇒ xác nhận lại bằng TOÀN BỘ
        with cf.ThreadPoolExecutor(max_workers=4) as ex:
            full = dict((r[0], r) for r in ex.map(lambda m: run(m, []), [m for m in muts if m[0] in alive]))
        res = [full.get(r[0], r) for r in res]
    for name, verdict, how, desc in res:
        print(f"{name:4s} {verdict:10s} {desc}\n       ↳ {how}")
    n = len(res)
    k = sum(1 for r in res if r[1] == "BỊ BẮT")
    print(f"\n{k}/{n} mutant bị bắt · sống: {[r[0] for r in res if r[1] == 'SỐNG'] or 'không'} · "
          f"lỗi: {[r[0] for r in res if r[1].startswith('LỖI')] or 'không'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
