#!/usr/bin/env python3
"""Selfcheck: SỔ giao hàng báo cáo phải là MỘT, dù gate chạy từ cây nào.

Sự cố nền (kb/incidents/2026-09/2026-09-12-report-return-gate-worktree-root.md, mục "Còn treo"
#2): `report_delivery_gate.py` lấy `ROOT = parent.parent` của CÂY ĐANG CHẠY, mà `state/` bị
gitignore ⇒ mỗi worktree/clone giữ sổ riêng, còn `check_report_cadence.sh:44` chỉ đọc sổ
canonical ⇒ một lần giao hàng từ cây phụ là VÔ HÌNH ⇒ GỬI TRÙNG báo cáo cho nhà đầu tư. Đo
được trên đĩa: `mike_paseo` 32 entry + một worktree `WorkingClaude/wt-<thread>` 2 entry nằm
ngoài sổ canonical, và
monthly 2026-08 thực sự đã gửi hai lần (28/08 từ `mike_paseo`, 02/09 từ canonical).

Không monkey-patch: dựng SANDBOX tự chứa `<tmp>/WorkingClaude/{wc_env.sh,mike/...}` có worktree
giả ĐÚNG ĐỘ SÂU `mike/agents/wt-fake/bin/`, chạy gate thật như production nhưng với notify/email
/return-gate là STUB ⇒ không chạm Discord, email, BQ hay sổ thật. RED control lấy THẲNG TỪ GIT
(bản gần nhất còn `parent.parent`) — không có nó thì test xanh không chứng minh được gì.

    python3 mike/bin/report_delivery_ledger_selfcheck.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wc_paths  # noqa: E402

# Cây ĐANG TEST = cây chứa CHÍNH file này, tính không qua env. `dispatch.sh` export `WC_ROOT`
# vào mọi phiên agent; nếu để nó thắng thì selfcheck chạy từ worktree sẽ lặng lẽ đi test bản
# gate CANONICAL và báo PASS cho code mình vừa sửa nhưng KHÔNG chạy — đúng cơ chế đã làm lọt bug
# TZ 2026-07-31. `child_env()` đã pop cho tiến trình con; dòng này pop cho chính nó.
for _k in ("WC_ROOT", "MIKE_ROOT"):
    os.environ.pop(_k, None)
MIKE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REAL_BIN = os.path.join(MIKE, "bin")
GATE = "report_delivery_gate.py"
OLD_MARKER = "ROOT = Path(__file__).resolve().parent.parent"

_fails: list = []
_ran = 0


def check(name, got, want):
    global _ran
    _ran += 1
    ok = got == want
    print(("✅ " if ok else "❌ ") + name + ("" if ok else f"\n     got={got!r}\n     want={want!r}"))
    if not ok:
        _fails.append(name)
    return ok


def old_source() -> tuple:
    """(sha, nội dung) bản gần nhất còn `parent.parent` — đọc từ git, KHÔNG hardcode HEAD~."""
    revs = subprocess.run(["git", "-C", MIKE, "rev-list", "HEAD", "--", "bin/" + GATE],
                          capture_output=True, text=True, check=True).stdout.split()
    for sha in revs:
        blob = subprocess.run(["git", "-C", MIKE, "show", f"{sha}:bin/{GATE}"],
                              capture_output=True, text=True)
        if blob.returncode == 0 and OLD_MARKER in blob.stdout:
            return sha, blob.stdout
    raise SystemExit("❌ không tìm được bản cũ (parent.parent) trong lịch sử git — RED vô nghĩa")


def _write(path: str, text: str, mode: int = 0o644) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    os.chmod(path, mode)


def _stub_bin(bin_dir: str, tag: str, evidence: str, notify_log: str) -> None:
    """3 script con mà gate gọi ra ngoài — mỗi bản tự khai TÊN CÂY đã chạy nó."""
    shutil.copy2(os.path.join(REAL_BIN, "wc_paths.py"), os.path.join(bin_dir, "wc_paths.py"))
    _write(os.path.join(bin_dir, "report_return_gate.py"),
           "import sys\n"
           f"open({evidence!r}, 'a').write('gate:{tag}\\n')\n"
           "sys.exit(0)\n")
    _write(os.path.join(bin_dir, "notify_thread.sh"),
           "#!/usr/bin/env bash\n"
           f"echo \"ENTER {tag} $$\" >> {notify_log!r}\n"
           "sleep \"${SC_NOTIFY_SLEEP:-0}\"\n"
           f"echo \"EXIT {tag} $$\" >> {notify_log!r}\n", 0o755)
    _write(os.path.join(bin_dir, "send_report_email.py"),
           "import sys\n"
           f"open({evidence!r}, 'a').write('email:{tag}\\n')\n"
           "sys.exit(0)\n")


def build_sandbox(worktree_gate_src: str) -> dict:
    """`<tmp>/WorkingClaude/mike` (canonical) + `mike/agents/wt-fake` (worktree giả)."""
    sb = tempfile.mkdtemp(prefix="delivery-ledger-sc-")
    wc = os.path.join(sb, "WorkingClaude")
    mike = os.path.join(wc, "mike")
    wt = os.path.join(mike, "agents", "wt-fake")
    for d in (os.path.join(mike, "bin"), os.path.join(mike, "reports"),
              os.path.join(wt, "bin"), os.path.join(wt, "reports")):
        os.makedirs(d)
    _write(os.path.join(wc, "wc_env.sh"), "# marker\n")
    _write(os.path.join(mike, "MIKE.md"), "# fake canonical mike\n")
    _write(os.path.join(wt, "MIKE.md"), "# fake worktree\n")
    evidence = os.path.join(sb, "evidence.txt")
    notify_log = os.path.join(sb, "notify.log")
    _stub_bin(os.path.join(mike, "bin"), "canonical", evidence, notify_log)
    _stub_bin(os.path.join(wt, "bin"), "worktree", evidence, notify_log)
    with open(os.path.join(REAL_BIN, GATE), encoding="utf-8") as f:
        new_src = f.read()
    _write(os.path.join(mike, "bin", GATE), new_src)
    _write(os.path.join(wt, "bin", GATE), worktree_gate_src)
    return {"sb": sb, "wc": wc, "mike": mike, "wt": wt,
            "evidence": evidence, "notify_log": notify_log,
            "ledger": os.path.join(mike, "state", "report_delivery.json"),
            "stray": os.path.join(wt, "state", "report_delivery.json")}


def child_env(**extra) -> dict:
    """Env production TRỪ TZ, WC_ROOT, MIKE_ROOT — để nhánh tự tìm marker được chạy thật."""
    env = dict(os.environ)
    for k in ("TZ", "WC_ROOT", "MIKE_ROOT"):
        env.pop(k, None)
    env.update({k: str(v) for k, v in extra.items()})
    return env


def make_report(dir_: str, name: str) -> str:
    path = os.path.join(dir_, name)
    _write(path, f"# {name}\nnội dung báo cáo giả\n")
    return path


def run_gate(bin_dir: str, report: str, env: dict, wait: bool = True):
    cmd = [sys.executable, os.path.join(bin_dir, GATE), report, "--topic", "trading_report"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, env=env, cwd=bin_dir)
    if not wait:
        return p
    out, _ = p.communicate(timeout=180)
    return p.returncode, out


def ledger_keys(path: str) -> list:
    if not os.path.isfile(path):
        return []
    return sorted(json.loads(open(path, encoding="utf-8").read()).get("reports", {}))


def main() -> int:
    sha_old, src_old = old_source()
    print(f"cây ĐANG TEST (không qua env): {MIKE}")
    print(f"RED control = bản cũ {sha_old[:8]} (ROOT = parent.parent), lấy từ git\n")

    # --- 1. GREEN: gate MỚI chạy TỪ worktree giả ------------------------------------------
    s = build_sandbox(open(os.path.join(REAL_BIN, GATE), encoding="utf-8").read())
    try:
        rep = make_report(os.path.join(s["wt"], "reports"), "SpaceX_daily_report_2026-01-02.md")
        rc, out = run_gate(os.path.join(s["wt"], "bin"), rep, child_env())
        check("gate MỚI từ worktree: chạy xong sạch", (rc, "COMPLETE" in out), (0, True))
        check("… ghi vào sổ CANONICAL", ledger_keys(s["ledger"]),
              ["SpaceX_daily_report_2026-01-02.md"])
        check("… KHÔNG tạo sổ lạc trong worktree", os.path.exists(s["stray"]), False)
        check("… KHÔNG tạo cả thư mục state/ lạc", os.path.isdir(os.path.join(s["wt"], "state")),
              False)
        ev = open(s["evidence"], encoding="utf-8").read().split()
        check("… return gate + email chạy bản CANONICAL (không phải bản tiền-vá của worktree)",
              ev, ["gate:canonical", "email:canonical"])
        check("… Discord cũng đi qua bản canonical",
              [l.split()[1] for l in open(s["notify_log"], encoding="utf-8").read().splitlines()],
              ["canonical", "canonical"])
    finally:
        shutil.rmtree(s["sb"], ignore_errors=True)

    # --- 2. RED control: gate CŨ ở CÙNG đường dẫn phải phân mảnh sổ -------------------------
    s = build_sandbox(src_old)
    try:
        rep = make_report(os.path.join(s["wt"], "reports"), "SpaceX_daily_report_2026-01-02.md")
        rc, out = run_gate(os.path.join(s["wt"], "bin"), rep, child_env())
        check("RED · gate CŨ từ worktree: vẫn báo COMPLETE (lỗi IM LẶNG, không tự lộ)",
              (rc, "COMPLETE" in out), (0, True))
        check("RED · gate CŨ: sổ CANONICAL trống ⇒ cadence check mù ⇒ gửi trùng",
              ledger_keys(s["ledger"]), [])
        check("RED · gate CŨ: sổ LẠC mọc trong worktree", ledger_keys(s["stray"]),
              ["SpaceX_daily_report_2026-01-02.md"])
        check("RED · gate CŨ: chạy luôn bản tiền-vá trong worktree (đúng mục #1 incident)",
              open(s["evidence"], encoding="utf-8").read().split(),
              ["gate:worktree", "email:worktree"])
    finally:
        shutil.rmtree(s["sb"], ignore_errors=True)

    # --- 3. LOCK: hai cây khác nhau phải loại trừ nhau --------------------------------------
    s = build_sandbox(open(os.path.join(REAL_BIN, GATE), encoding="utf-8").read())
    try:
        r1 = make_report(os.path.join(s["mike"], "reports"), "SpaceX_daily_report_2026-01-03.md")
        r2 = make_report(os.path.join(s["wt"], "reports"), "ZaloPay_daily_report_2026-01-03.md")
        env = child_env(SC_NOTIFY_SLEEP="1.5")
        p1 = run_gate(os.path.join(s["mike"], "bin"), r1, env, wait=False)
        p2 = run_gate(os.path.join(s["wt"], "bin"), r2, env, wait=False)
        rc1 = p1.wait(timeout=180)
        rc2 = p2.wait(timeout=180)
        check("hai tiến trình (canonical + worktree) đều xong sạch", (rc1, rc2), (0, 0))
        seq = [l.split()[0] for l in open(s["notify_log"], encoding="utf-8").read().splitlines()]
        # Lock đúng ⇒ ENTER/EXIT luôn xen kẽ. Hỏng ⇒ có hai ENTER liền nhau (chồng lấn).
        check("… không chồng lấn: ENTER/EXIT xen kẽ đúng 2 lượt", seq,
              ["ENTER", "EXIT", "ENTER", "EXIT"])
        check("… và cả hai lượt giao hàng nằm chung MỘT sổ canonical", ledger_keys(s["ledger"]),
              ["SpaceX_daily_report_2026-01-03.md", "ZaloPay_daily_report_2026-01-03.md"])
    finally:
        shutil.rmtree(s["sb"], ignore_errors=True)

    # RED control cho CHÍNH phép đo trên: cùng kịch bản, cùng sleep, nhưng CẢ HAI cây chạy bản
    # CŨ (lock bám cây đang chạy). Không có bước này thì "ENTER/EXIT xen kẽ" có thể chỉ là do
    # hai tiến trình tình cờ không trùng giờ — tức một assertion trang trí.
    s = build_sandbox(src_old)
    try:
        shutil.copy2(os.path.join(s["wt"], "bin", GATE), os.path.join(s["mike"], "bin", GATE))
        r1 = make_report(os.path.join(s["mike"], "reports"), "SpaceX_daily_report_2026-01-03.md")
        r2 = make_report(os.path.join(s["wt"], "reports"), "ZaloPay_daily_report_2026-01-03.md")
        env = child_env(SC_NOTIFY_SLEEP="1.5")
        p1 = run_gate(os.path.join(s["mike"], "bin"), r1, env, wait=False)
        p2 = run_gate(os.path.join(s["wt"], "bin"), r2, env, wait=False)
        p1.wait(timeout=180)
        p2.wait(timeout=180)
        seq = [l.split()[0] for l in open(s["notify_log"], encoding="utf-8").read().splitlines()]
        check("RED · bản CŨ: hai cây KHÔNG loại trừ nhau (ENTER chồng ENTER) ⇒ phép đo có rằng",
              seq[:2], ["ENTER", "ENTER"])
    finally:
        shutil.rmtree(s["sb"], ignore_errors=True)

    # --- 4. wc_paths: canonical resolver + cảnh báo env lệch cây ----------------------------
    s = build_sandbox(open(os.path.join(REAL_BIN, GATE), encoding="utf-8").read())
    try:
        probe = ("import sys, os, json;"
                 f"sys.path.insert(0, {os.path.join(s['wt'], 'bin')!r});"
                 "import wc_paths as w;"
                 f"print(json.dumps(w.find_mike_canonical_root({os.path.join(s['wt'], 'bin', GATE)!r})))")
        p = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True,
                           env=child_env())
        check("find_mike_canonical_root từ worktree giả ⇒ cây canonical",
              json.loads(p.stdout.strip()), s["mike"])

        # env WC_ROOT HỢP LỆ nhưng trỏ cây KHÁC: hành vi giữ nguyên (env thắng) + CẢNH BÁO.
        probe2 = ("import sys, json;"
                  f"sys.path.insert(0, {REAL_BIN!r});"
                  "import wc_paths as w;"
                  f"print(json.dumps(w.find_wc_root({os.path.join(REAL_BIN, 'wc_paths.py')!r})))")
        p2 = subprocess.run([sys.executable, "-c", probe2], capture_output=True, text=True,
                            env=child_env(WC_ROOT=s["wc"]))
        check("env WC_ROOT hợp lệ-nhưng-khác-cây: vẫn được tôn trọng (không đổi hành vi)",
              json.loads(p2.stdout.strip()), s["wc"])
        check("… và có cảnh báo stderr", "khác cây chứa script" in p2.stderr, True)
        p3 = subprocess.run([sys.executable, "-c", probe2], capture_output=True, text=True,
                            env=child_env(WC_ROOT=wc_paths.find_wc_root(__file__)))
        check("… env trỏ ĐÚNG cây thì KHÔNG cảnh báo (không gây nhiễu cho đường chạy thật)",
              "khác cây chứa script" in p3.stderr, False)

        # env MIKE_ROOT: override MỚI trên đường client-facing ⇒ phải có lưới, không để 0%
        # coverage (mutation "tin MIKE_ROOT mù" từng sống sót toàn bộ selfcheck này).
        # Sổ dùng chung KHÔNG có override qua env — kể cả env trỏ một cây mike HỢP LỆ khác.
        other = os.path.join(s["sb"], "mike-khac")
        os.makedirs(other, exist_ok=True)
        _write(os.path.join(other, "MIKE.md"), "# cây mike hợp lệ nhưng KHÁC\n")
        for var in ("MIKE_ROOT", "WC_ROOT"):
            pe = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True,
                                env=child_env(**{var: other if var == "MIKE_ROOT" else s["sb"]}))
            check(f"env {var} trỏ cây khác KHÔNG lái được sổ canonical",
                  json.loads(pe.stdout.strip()), s["mike"])

        cli = subprocess.run([sys.executable, os.path.join(s["wt"], "bin", "wc_paths.py"),
                              "--mike-canonical"], capture_output=True, text=True,
                             env=child_env())
        check("CLI wc_paths --mike-canonical chạy TỪ worktree ⇒ in ra cây canonical",
              cli.stdout.strip(), s["mike"])
    finally:
        shutil.rmtree(s["sb"], ignore_errors=True)

    # --- 5. Hai script BASH quyết định có gửi hay không cũng phải neo canonical -------------
    # Chạy nguyên script trong selfcheck là dispatch + gửi thật, nên chỉ chạy ĐOẠN ĐẦU (tới hết
    # khối tính gốc cây) — vẫn là đo HÀNH VI, không phải so chuỗi. Cắt theo mẫu `^fi$` chứ không
    # theo số dòng, để một lần sửa phía trên không làm test lặng lẽ đo nhầm đoạn.
    # Cây `WorkingClaude` ANH EM hợp lệ (có marker + mike/MIKE.md) để thử env độc hại: đây là
    # hình dạng CÓ THẬT trên máy (`thanhdt/wt-oshares-*/WorkingClaude`), và `dispatch.sh` export
    # `WC_ROOT` của cây nó đang chạy vào MỌI phiên agent ⇒ đây là env của caller THẬT, không
    # phải giả định. Vì thế các lượt dưới đây CỐ Ý không dùng `child_env()` (hàm đó pop env).
    sib = tempfile.mkdtemp(prefix="sibling-wc-")
    os.makedirs(os.path.join(sib, "mike"))
    _write(os.path.join(sib, "wc_env.sh"), "# marker\n")
    _write(os.path.join(sib, "mike", "MIKE.md"), "# cây anh em\n")
    hostile = {"WC_ROOT": sib, "MIKE_ROOT": os.path.join(sib, "mike")}
    try:
        p = subprocess.run(
            [sys.executable, "-c",
             f"import sys; sys.path.insert(0, {REAL_BIN!r}); import wc_paths as w;"
             f"print(w.find_mike_canonical_root({os.path.join(REAL_BIN, 'wc_paths.py')!r}))"],
            capture_output=True, text=True, env=dict(os.environ, WC_ROOT=sib))
        check("env WC_ROOT trỏ cây anh em HỢP LỆ: KHÔNG được đổi sổ canonical "
              "(sổ là singleton của fleet, không phải 'cây của tôi')", p.stdout.strip(), MIKE)

        for script in ("check_report_cadence.sh", "paper_programs_daily_report.sh"):
            for mode in ("clean", "hostile-env", "red-no-wc-paths"):
                wt = tempfile.mkdtemp(prefix="wt-fake-cadence-", dir=os.path.join(MIKE, "agents"))
                try:
                    os.mkdir(os.path.join(wt, "bin"))
                    if mode != "red-no-wc-paths":
                        shutil.copy2(os.path.join(REAL_BIN, "wc_paths.py"),
                                     os.path.join(wt, "bin", "wc_paths.py"))
                    src = open(os.path.join(REAL_BIN, script), encoding="utf-8").read()
                    head, sep, _ = src.partition("\nfi\n")
                    frag_src = head + "\nfi\necho \"ROOT=$ROOT\"\n"
                    # Cắt theo mẫu là mong manh: chỉ cần một `fi  # chú thích` phía trên là mốc
                    # trượt xuống khối sau ⇒ selfcheck THỰC THI thân bài dispatch/notify THẬT.
                    # Hai assertion này biến mọi lần trượt thành ĐỎ thay vì side-effect im lặng.
                    body = "\n".join(ln for ln in frag_src.splitlines()
                                      if not ln.lstrip().startswith("#"))
                    danger = [c for c in ("dispatch.sh", "notify_thread.sh", "append_event.sh")
                              if c in body]
                    check(f"{script} · đoạn cắt KHÔNG chứa lệnh có side-effect", danger, [])
                    check(f"{script} · đoạn cắt CÓ chứa khối tính gốc cây (cắt đúng chỗ)",
                          'wc_paths.py" --mike-canonical' in frag_src, True)
                    if danger:
                        continue
                    frag = os.path.join(wt, "bin", "head_probe.sh")
                    _write(frag, frag_src)
                    env = child_env() if mode == "clean" else dict(os.environ, **hostile)
                    out = subprocess.run(["bash", frag], capture_output=True, text=True,
                                         env=env).stdout
                    got = [ln[5:] for ln in out.splitlines() if ln.startswith("ROOT=")]
                    if mode == "clean":
                        check(f"{script} chạy từ worktree ⇒ ROOT = cây canonical", got, [MIKE])
                    elif mode == "hostile-env":
                        check(f"{script} dưới env WC_ROOT/MIKE_ROOT trỏ cây anh em ⇒ VẪN là cây "
                              f"canonical", got, [MIKE])
                    else:
                        check(f"RED · {script} KHÔNG có wc_paths.py (worktree tiền-vá) ⇒ ROOT "
                              f"vẫn lệch về cây phụ", got, [wt])
                finally:
                    shutil.rmtree(wt, ignore_errors=True)
    finally:
        shutil.rmtree(sib, ignore_errors=True)

    print(f"\n{_ran - len(_fails)}/{_ran} check")
    if _fails:
        print(f"❌ SELFCHECK FAIL — {len(_fails)} test: " + "; ".join(_fails))
        return 1
    print("✅ SELFCHECK PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
