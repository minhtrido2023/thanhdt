#!/usr/bin/env python3
"""Selfcheck cho `worktree_stale_check.py` — chạy trên SANDBOX tự chứa, không chạm cây thật.

Hai thứ dễ sai nhất ở một checker, và là lý do selfcheck này tồn tại:
  1. Nó có IM khi không có gì để nói không? Checker kêu mỗi lượt cron là WARN-rác — đúng cái
     `ops_health_check.sh` (header §7) ghi là đã lặp ~20 lần/5 ngày mà không ai hành động.
  2. Nó có kêu ĐÚNG lúc có chuyện không? (cây tiền-vá đang được dùng; sổ lạc có báo cáo đã gửi
     mà sổ canonical không biết.)

    python3 mike/bin/worktree_stale_check_selfcheck.py
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

for _k in ("WC_ROOT", "MIKE_ROOT"):                  # tự bảo vệ như ledger selfcheck
    os.environ.pop(_k, None)
REAL_BIN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin")
CHECKER = "worktree_stale_check.py"

_fails: list = []
_ran = 0


def check(name, got, want):
    global _ran
    _ran += 1
    ok = got == want
    print(("✅ " if ok else "❌ ") + name + ("" if ok else f"\n     got={got!r}\n     want={want!r}"))
    if not ok:
        _fails.append(name)


def write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def age(path: str, days: int) -> None:
    """Đẩy mtime của cả cây về quá khứ — 'nằm im' phải mô phỏng bằng mtime thật, không mock."""
    old = time.time() - days * 86400
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files + dirs:
            os.utime(os.path.join(root, name), (old, old))
    os.utime(path, (old, old))


def build(tmp: str) -> dict:
    mike = os.path.join(tmp, "WorkingClaude", "mike")
    write(os.path.join(tmp, "WorkingClaude", "wc_env.sh"), "# marker\n")
    write(os.path.join(mike, "MIKE.md"), "# canonical\n")
    os.makedirs(os.path.join(mike, "bin"), exist_ok=True)
    for name in ("wc_paths.py", CHECKER):
        shutil.copy2(os.path.join(REAL_BIN, name), os.path.join(mike, "bin", name))
    for name in ("report_return_gate.py", "report_delivery_gate.py"):
        write(os.path.join(mike, "bin", name), "# bản canonical\n")

    report = "SpaceX_daily_report_2026-01-05.md"
    body = "# báo cáo thật\n"
    write(os.path.join(mike, "reports", report), body)
    sha = hashlib.sha256(body.encode()).hexdigest()
    write(os.path.join(mike, "state", "report_delivery.json"),
          json.dumps({"version": 1, "reports": {}}))

    def tree(path: str, drift: bool, ledger: dict | None = None):
        os.makedirs(os.path.join(path, "bin"), exist_ok=True)
        for name in ("wc_paths.py", "report_delivery_gate.py"):
            shutil.copy2(os.path.join(mike, "bin", name), os.path.join(path, "bin", name))
        write(os.path.join(path, "bin", "report_return_gate.py"),
              "# bản TIỀN-VÁ\n" if drift else "# bản canonical\n")
        if ledger is not None:
            write(os.path.join(path, "state", "report_delivery.json"), json.dumps(ledger))

    delivered = {"version": 1, "reports": {report: {
        "sha256": sha, "path": os.path.join(mike, "reports", report),
        "discord": {"status": "delivered", "delivered_at": "x", "sha256": sha},
        "email": {"status": "delivered", "delivered_at": "x", "sha256": sha}}}}
    tree(os.path.join(mike, "agents", "wt-active"), drift=True)
    tree(os.path.join(mike, "agents", "wt-dormant"), drift=True)
    tree(os.path.join(tmp, "WorkingClaude", "wt-ledger"), drift=False, ledger=delivered)
    age(os.path.join(mike, "agents", "wt-dormant"), 60)
    return {"mike": mike, "report": report, "sha": sha, "delivered": delivered}


def run(mike: str, *args) -> dict:
    out = subprocess.run([sys.executable, os.path.join(mike, "bin", CHECKER), "--json", *args],
                         capture_output=True, text=True, env=dict(os.environ))
    return json.loads(out.stdout)


def text(mike: str) -> str:
    return subprocess.run([sys.executable, os.path.join(mike, "bin", CHECKER)],
                          capture_output=True, text=True, env=dict(os.environ)).stdout


def main() -> int:
    tmp = tempfile.mkdtemp(prefix="wt-stale-sc-")
    try:
        s = build(tmp)
        mike = s["mike"]
        res = run(mike)
        check("cây tiền-vá ĐANG DÙNG ⇒ báo", [os.path.basename(t["tree"]) for t in
                                              res["stale_trees"]], ["wt-active"])
        check("cây tiền-vá NẰM IM (mtime 60 ngày) ⇒ không báo, chỉ đếm",
              res["stale_dormant_count"], 1)
        check("sổ lạc có báo cáo ĐÃ GỬI mà canonical không biết ⇒ báo",
              [len(x["delivered"]) for x in res["stray_ledgers"]], [1])
        out = text(mike)
        check("… và nói ra nguy cơ gửi TRÙNG bằng chữ", "gửi TRÙNG" in out, True)

        # Sau khi sổ canonical ĐÃ có entry đó: checker phải IM (không lặp lại việc đã xong).
        write(os.path.join(mike, "state", "report_delivery.json"), json.dumps(s["delivered"]))
        check("sổ canonical đã có entry ⇒ IM (không WARN-rác)", run(mike)["stray_ledgers"], [])

        # Artifact khác hash (cùng tên) KHÔNG được coi là "đã gửi" — cùng khoá hash với merge tool.
        write(os.path.join(mike, "state", "report_delivery.json"),
              json.dumps({"version": 1, "reports": {}}))
        write(os.path.join(mike, "reports", s["report"]), "# NỘI DUNG KHÁC\n")
        check("cùng tên nhưng khác hash ⇒ KHÔNG báo là đã gửi (khoá theo hash, không theo tên)",
              run(mike)["stray_ledgers"], [])

        # Mọi cây được vá ⇒ im hoàn toàn (điều kiện 'sạch' phải đạt được thật, không phải lý thuyết)
        for t in ("agents/wt-active", "agents/wt-dormant"):
            write(os.path.join(mike, t, "bin", "report_return_gate.py"), "# bản canonical\n")
        check("mọi cây đã vá + không sổ lạc ⇒ checker KHÔNG in gì", text(mike).strip(), "")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{_ran - len(_fails)}/{_ran} check")
    if _fails:
        print("❌ SELFCHECK FAIL — " + "; ".join(_fails))
        return 1
    print("✅ SELFCHECK PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
