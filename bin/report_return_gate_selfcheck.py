#!/usr/bin/env python3
"""Selfcheck: `report_return_gate.py` phải tìm ĐÚNG gốc cây kể cả khi chạy từ WORKTREE.

Sự cố 2026-09-12 (bus question `report-return-gate-worktree-root-chan-bao-cao-nha-dau-tu`):
`ROOT = dirname×3(__file__)` đúng cho bản gốc `mike/bin/`, nhưng mọi bản sao trong
`mike/agents/wt-*/bin/` cho ROOT = `WorkingClaude/mike/agents` ⇒ `EXEC_DIR` trỏ thư mục KHÔNG
TỒN TẠI ⇒ cổng fail-closed ⇒ **báo cáo nhà đầu tư không gửi được** (5 ca thật: 2026-07-03,
07-24, 07-31, 08-07 + 1 lần Errno 2). 3/3 worktree kiểm tra đều lệch.

Selfcheck này KHÔNG mô phỏng bằng monkey-patch: nó dựng một worktree GIẢ THẬT trong
`mike/agents/wt-fake-*` (mkdtemp, cùng độ sâu thư mục với worktree thật), đặt bản sao script
vào `bin/` của nó rồi chạy như production. Có RED control: bản TRƯỚC bản vá — lấy thẳng từ
lịch sử git, không chép tay — đặt ở CÙNG đường dẫn giả phải FAIL. RED control là phần quan
trọng nhất: không có nó, 4 test xanh không chứng minh được test có khả năng bắt lỗi.

    python3 mike/bin/report_return_gate_selfcheck.py            # đủ bộ (~8-10 phút, chạm BQ)
    python3 mike/bin/report_return_gate_selfcheck.py --root-only  # bỏ 2 test chạm BQ (vài giây)

Ngoài 7 test ROOT/worktree, nó còn chạy bộ assertion NHÚNG của chính `report_return_gate.py`
(`--selfcheck`) — xem `run_embedded_selfcheck()`, được gọi ở luồng chính (:163). Đây LÀ runner của
bộ đó: `report_return_gate.py --selfcheck` không có điểm vào nào khác, nên bỏ file này khỏi
`run_selfchecks.sh` là bộ assertion nhúng ngừng chạy mà không ai báo.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wc_paths  # noqa: E402

WC = wc_paths.find_wc_root(__file__)
MIKE = os.path.join(WC, "mike")
REAL_BIN = os.path.join(MIKE, "bin")
AGENTS_DIR = os.path.join(MIKE, "agents")
SCRIPT = "report_return_gate.py"
OLD_MARKER = "ROOT = os.path.dirname(os.path.dirname(os.path.dirname("
# báo cáo THẬT đã gửi nhà đầu tư (state/report_delivery.json) — GREEN phải PASS trên đúng nó
DEFAULT_REPORT = os.path.join(MIKE, "reports", "SpaceX_weekly_report_2026-08-31_to_2026-09-04.md")

_fails: list = []


def check(name, got, want):
    ok = got == want
    print(("✅ " if ok else "❌ ") + name + ("" if ok else f"\n     got={got!r}\n     want={want!r}"))
    if not ok:
        _fails.append(name)
    return ok


def child_env() -> dict:
    """Env của production MINUS hai biến che khuất lỗi.

    - `TZ`: theo yêu cầu — cổng không được phụ thuộc TZ của người chạy.
    - `WC_ROOT`: fleet ĐANG export biến này (wc_env.sh), nên nếu để nguyên thì nhánh override
      luôn thắng và nhánh đi-lên-tìm-marker — thứ thật sự vá lỗi — không bao giờ được chạy.
    """
    env = dict(os.environ)
    env.pop("TZ", None)
    env.pop("WC_ROOT", None)
    return env


def make_fake_worktree(source_text: str) -> str:
    """`mike/agents/wt-fake-XXXX/bin/` — ĐÚNG độ sâu của worktree thật (nơi bug cắn).

    Các file bin khác được COPY (không symlink) — worktree git thật cũng là file thật. Symlink
    hôm nay vô hại (không module nào trong đường này dùng `.resolve()`), nhưng
    `report_delivery_gate.py:22` CÓ dùng — mai mở selfcheck sang đó thì symlink sẽ cho XANH GIẢ.
    """
    root = tempfile.mkdtemp(prefix="wt-fake-", dir=AGENTS_DIR)
    fake_bin = os.path.join(root, "bin")
    os.mkdir(fake_bin)
    for name in os.listdir(REAL_BIN):
        src = os.path.join(REAL_BIN, name)
        if not os.path.isfile(src):
            continue
        if name == SCRIPT:
            continue
        shutil.copy2(src, os.path.join(fake_bin, name))
    with open(os.path.join(fake_bin, SCRIPT), "w", encoding="utf-8") as f:
        f.write(source_text)
    return root


def old_source() -> tuple:
    """(sha, nội dung) của bản GẦN NHẤT còn dùng dirname×3 — đọc từ git, không chép tay.

    Không hardcode `HEAD~`: chỉ cần một commit khác chen vào là RED control lặng lẽ biến thành
    bản ĐÃ VÁ và test xanh giả.
    """
    revs = subprocess.run(["git", "-C", MIKE, "rev-list", "HEAD", "--", "bin/" + SCRIPT],
                          capture_output=True, text=True, check=True).stdout.split()
    for sha in revs:
        blob = subprocess.run(["git", "-C", MIKE, "show", f"{sha}:bin/{SCRIPT}"],
                              capture_output=True, text=True)
        if blob.returncode == 0 and OLD_MARKER in blob.stdout:
            return sha, blob.stdout
    raise SystemExit("❌ không tìm được bản cũ (dirname×3) trong lịch sử git — RED control vô nghĩa")


def probe_root(worktree: str, extra_env: dict = None) -> tuple:
    """(ROOT, EXEC_DIR, EXEC_DIR có tồn tại) mà bản sao trong worktree giả tự tính ra."""
    code = ("import sys, os, json;"
            f"sys.path.insert(0, {os.path.join(worktree, 'bin')!r});"
            "import report_return_gate as g;"
            "print(json.dumps([g.ROOT, g.EXEC_DIR, os.path.isdir(g.EXEC_DIR)]))")
    env = child_env()
    env.update(extra_env or {})
    p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                       env=env, cwd=worktree)
    if p.returncode != 0:
        return ("<crash>", p.stderr.strip().splitlines()[-1] if p.stderr else "", False)
    import json
    return tuple(json.loads(p.stdout.strip().splitlines()[-1]))


def run_embedded_selfcheck() -> tuple:
    """(rc, output) của `report_return_gate.py --selfcheck` — bộ assertion NHÚNG trong file gốc.

    Bộ đó sống trong CHÍNH `report_return_gate.py` sau cờ `--selfcheck`, mà không runner nào của
    fleet gọi cờ đó: `run_selfchecks.sh` chạy file NÀY với `--root-only`, còn file này trước
    2026-09-24 chỉ gọi `--report`. ⇒ toàn bộ assertion nhúng (gồm 6 ca cổng LỆCH NGUỒN VENDOR và
    2 MUTATION-GUARD của `entitled_gross`) TÀNG HÌNH với cả hai runner — đúng lớp vấn đề mà
    `dividend_adjusted_return_selfcheck.py` (8989d80e) vừa vá cho file anh em. Offline, không
    chạm BQ/broker nên chạy ở CẢ `--root-only`.

    Chạy bản NẰM CẠNH file này (`dirname(__file__)`), KHÔNG phải `REAL_BIN` như phần còn lại:
    các test ROOT cố ý kiểm bản CANONICAL (chúng hỏi "bản canonical có chạy được từ worktree
    không"), còn bộ nhúng hỏi "logic trong CÂY NÀY có đúng không" — chạy nó trên canonical thì
    thay đổi đang phát triển trong worktree sẽ không bao giờ được kiểm. Cùng khuôn
    `dividend_adjusted_return_selfcheck.py`.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    p = subprocess.run([sys.executable, os.path.join(here, SCRIPT), "--selfcheck"],
                       capture_output=True, text=True, env=child_env(),
                       cwd=os.path.dirname(here))
    return p.returncode, (p.stdout + p.stderr)


def run_gate(worktree: str, report: str) -> tuple:
    p = subprocess.run([sys.executable, os.path.join(worktree, "bin", SCRIPT), "--report", report],
                       capture_output=True, text=True, env=child_env(), cwd=worktree)
    return p.returncode, (p.stdout + p.stderr)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default=DEFAULT_REPORT)
    ap.add_argument("--root-only", action="store_true", help="bỏ 2 test chạy cổng thật (chạm BQ)")
    args = ap.parse_args()

    sha_old, src_old = old_source()
    with open(os.path.join(REAL_BIN, SCRIPT), encoding="utf-8") as f:
        src_new = f.read()
    print(f"gốc cây (marker wc_env.sh): {WC}")
    print(f"RED control = bản cũ {sha_old[:8]} (dirname×3), lấy từ git\n")

    rc_emb, out_emb = run_embedded_selfcheck()
    check("bộ assertion NHÚNG `report_return_gate.py --selfcheck` PASS", rc_emb, 0)
    # rc=0 CHƯA đủ: thay lời gọi bằng một hằng số giả cũng cho rc=0 (mutation sống). Đòi thêm
    # dòng đếm THẬT với số ca > 0 — "chạy 0 ca rồi báo xanh" không lọt được.
    _count = [l for l in out_emb.strip().splitlines() if l.startswith("SELFCHECK:")]
    _m = re.search(r"\((\d+)/(\d+) ca\)", _count[-1]) if _count else None
    _ran = int(_m.group(2)) if _m else 0
    _passed = int(_m.group(1)) if _m else -1
    check("… và nó THỰC SỰ chạy: dòng đếm có thật, số ca > 0, không ca nào FAIL",
          (_ran > 0, _passed == _ran), (True, True))
    print("     " + (_count[-1] if _count
                     else "\n     ".join(out_emb.strip().splitlines()[-8:])))

    wt_new = make_fake_worktree(src_new)
    wt_old = make_fake_worktree(src_old)
    try:
        # 1 GREEN: bản mới trong worktree giả phải ra đúng gốc cây + EXEC_DIR có thật
        root, exec_dir, exists = probe_root(wt_new)
        check("worktree giả · bản MỚI: ROOT = gốc WorkingClaude", root, WC)
        check("worktree giả · bản MỚI: EXEC_DIR trỏ thư mục CÓ THẬT",
              (exec_dir, exists), (os.path.join(WC, "data", "execution_logs"), True))

        # 2 RED: bản cũ ở CÙNG đường dẫn giả phải lệch đúng như sự cố đã đo
        root_o, exec_o, exists_o = probe_root(wt_old)
        check("RED control · bản CŨ: ROOT lệch về mike/agents (tái hiện sự cố)",
              root_o, os.path.join(WC, "mike", "agents"))
        check("RED control · bản CŨ: EXEC_DIR KHÔNG tồn tại ⇒ cổng fail-closed", exists_o, False)

        # 3 env `WC_ROOT` ĐỘC HẠI — nhánh ưu tiên CAO NHẤT, arch-reviewer vòng 1 bắt được:
        # `bin/dispatch.sh` tự tính WC_ROOT bằng ĐÚNG phép đếm cấp đang bị vá rồi export xuống
        # phiên agent. Bản sao dispatch.sh trong worktree export `WC_ROOT=.../mike/agents`; nếu
        # find_wc_root tin env mù thì bản ĐÃ VÁ tái hiện sự cố 1:1. Test này (chứ không phải
        # test marker) mới là test của đường chạy THẬT trong fleet.
        poisoned = os.path.join(WC, "mike", "agents")
        root_p, exec_p, exists_p = probe_root(wt_new, {"WC_ROOT": poisoned})
        check("env WC_ROOT độc hại (=mike/agents, y hệt dispatch.sh trong worktree): bị BỎ QUA",
              root_p, WC)
        check("env WC_ROOT độc hại: EXEC_DIR vẫn trỏ thư mục CÓ THẬT", exists_p, True)
        root_v, _, _ = probe_root(wt_new, {"WC_ROOT": WC})
        check("env WC_ROOT HỢP LỆ vẫn được tôn trọng (không vô hiệu hoá override)", root_v, WC)

        if args.root_only:
            print("\n(--root-only: bỏ qua 2 test chạy cổng thật)")
        else:
            rc_new, out_new = run_gate(wt_new, args.report)
            check(f"worktree giả · bản MỚI: cổng PASS trên báo cáo THẬT đã gửi "
                  f"({os.path.basename(args.report)})", rc_new, 0)
            if rc_new == 0:
                check("… và PASS đó là PASS thật (in đúng dòng kết luận)",
                      "✅ PASS" in out_new, True)
            else:
                print("     " + "\n     ".join(out_new.strip().splitlines()[-6:]))

            rc_old, out_old = run_gate(wt_old, args.report)
            check("RED control · bản CŨ: cổng KHÔNG PASS trên cùng báo cáo đó", rc_old != 0, True)
            check("RED control · bản CŨ: fail đúng vì trỏ execution_logs vào mike/agents "
                  "(đúng chữ ký sự cố, không phải lỗi khác)",
                  os.path.join(WC, "mike", "agents", "data", "execution_logs") in out_old, True)
    finally:
        shutil.rmtree(wt_new, ignore_errors=True)
        shutil.rmtree(wt_old, ignore_errors=True)

    print()
    if _fails:
        print(f"❌ SELFCHECK FAIL — {len(_fails)} test: " + "; ".join(_fails))
        return 1
    print("✅ SELFCHECK PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
