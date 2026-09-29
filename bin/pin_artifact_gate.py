#!/usr/bin/env python3
"""Cổng cơ học: mục MỚI trong `results_registry.md` phải trỏ tới một ledger ĐÃ PIN.

VÌ SAO (mandate 2026-08-01 của user: "đẩy bài học cũ ra công cụ/linter thay vì văn
xuôi"): registry rule 2 — *"CSV LÀ ARTIFACT ĐÔNG CỨNG"* — có từ 2026-06-19 và
**chưa bao giờ có cơ chế cưỡng chế**. Hệ quả đo thật 2026-09-28: trong 31 tham
chiếu md5 của registry, 2 mất dấu hoàn toàn, 5 chỉ còn sống trong một worktree
TẠM; và chính file audit user giữ từ 06-11 đã bị một file KHÁC ghi đè lên đúng
cái tên đó. Luật văn xuôi không chặn được lớp lỗi này.

LUẬT (cố ý CHỌN MỘT TÍN HIỆU CƠ HỌC DUY NHẤT, không đoán ngữ nghĩa — §29):
  Mỗi **mục `## ` MỚI** thêm vào `data/results_registry.md` phải chứa ĐÚNG MỘT
  trong hai dòng:
      ledger_md5: <32 ký tự hex>     → phải resolve được trong PINS.jsonl
                                        VÀ bản lưu verify sạch
                                        VÀ manifest ghi selfcheck_0vnd=true
      no_ledger: <lý do KHÔNG rỗng>  → mục không công bố số từ một ledger
                                        (vd: quyết định quy trình, ghi chú, đính chính)
  Thiếu cả hai ⇒ rc=1, CHẶN COMMIT.

CỐ Ý KHÔNG LÀM: không đoán "mục này có phải số pin không" bằng cách dò chữ
`CAGR`/`%`. Một cổng đoán ngữ nghĩa sẽ vừa bắt oan vừa bỏ lọt, và khi nó nói sai
thì người đọc bị dẫn sai ngay dòng đầu (§29). Thà bắt tác giả khai 1 dòng tường
minh — `no_ledger:` rẻ, và nó để lại dấu vết ai đã tuyên bố mục này không có số.

RATCHET: chỉ xét mục MỚI (so với HEAD). 135 mục lịch sử KHÔNG bị đụng — nợ cũ
không phải trả ngay, chỉ không được tăng.

LỐI THOÁT: `MIKE_PIN_GATE=warn` (qua 1 lần, KHÔNG ghi nhớ, lần sau vẫn chặn) ·
`MIKE_PIN_GATE=off`. Cố ý KHÔNG có cờ "thêm vào danh sách bỏ qua".
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pin_ledger  # noqa: E402
from wc_paths import find_wc_root  # noqa: E402

REGISTRY_REL = os.path.join("data", "results_registry.md")
RE_SECTION = re.compile(r"^##\s+(.+?)\s*$")
RE_LEDGER = re.compile(r"^\s*ledger_md5:\s*`?([0-9a-fA-F]{32})`?\s*$", re.M)
RE_NOLEDGER = re.compile(r"^\s*no_ledger:\s*(\S.*?)\s*$", re.M)


def _git(args, cwd, allow_fail=False):
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0 and not allow_fail:
        raise SystemExit(
            f"git {' '.join(args)} thất bại (rc={r.returncode}).\n"
            f"  Lỗi thật: {r.stderr.strip() or '(stderr rỗng)'}"
        )
    return r.stdout


def repo_rel_registry(wc_root: str) -> str:
    """Đường dẫn registry TÍNH TỪ GỐC REPO, không phải từ wc_root.

    BẮT ĐƯỢC KHI TEST THẬT 2026-09-28: `git show HEAD:<path>` giải path theo GỐC
    REPO chứ không theo cwd. Repo ngoài là `/home/trido/thanhdt`, còn registry ở
    `WorkingClaude/data/results_registry.md` ⇒ truyền `data/results_registry.md`
    thì git trả RỖNG, `old_text=""`, và gate coi **cả 135 mục lịch sử là MỚI** —
    tức ratchet biến mất đúng lúc cần nó nhất. Phải hỏi git tiền tố thật.
    """
    prefix = _git(["rev-parse", "--show-prefix"], wc_root, allow_fail=True).strip()
    return (prefix + REGISTRY_REL).replace(os.sep, "/")


def split_sections(text: str) -> dict:
    """{tiêu đề mục -> thân mục}. Trùng tiêu đề ⇒ nối thân lại (hiếm, nhưng có)."""
    out = {}
    cur = None
    buf = []
    for line in text.splitlines():
        m = RE_SECTION.match(line)
        if m:
            if cur is not None:
                out[cur] = out.get(cur, "") + "\n".join(buf) + "\n"
            cur = m.group(1)
            buf = []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        out[cur] = out.get(cur, "") + "\n".join(buf) + "\n"
    return out


def check_text(new_text: str, old_text: str, wc_root: str) -> tuple:
    """Trả (danh sách vi phạm, danh sách mục mới đã OK)."""
    new_sec = split_sections(new_text)
    old_sec = split_sections(old_text)
    added = [k for k in new_sec if k not in old_sec]

    man = pin_ledger.read_manifest(wc_root)
    by_md5 = {r["md5"]: r for r in man if r.get("record") != "annotation" and "md5" in r}

    violations = []
    ok = []
    for title in added:
        body = new_sec[title]
        md5s = RE_LEDGER.findall(body)
        nol = RE_NOLEDGER.findall(body)
        short = title if len(title) <= 70 else title[:67] + "…"

        if md5s and nol:
            violations.append(
                f"[{short}] khai CẢ `ledger_md5:` LẪN `no_ledger:` — chọn đúng một."
            )
            continue
        if not md5s and not nol:
            violations.append(
                f"[{short}] THIẾU cả `ledger_md5: <32 hex>` lẫn `no_ledger: <lý do>`."
            )
            continue
        if nol:
            ok.append(f"{short}  → no_ledger: {nol[0][:50]}")
            continue

        for digest in {d.lower() for d in md5s}:
            rec = by_md5.get(digest)
            if rec is None:
                violations.append(
                    f"[{short}] ledger_md5 {digest[:12]}… KHÔNG có trong "
                    f"data/pinned_ledgers/PINS.jsonl.\n"
                    f"      Pin trước đã: bin/pin_ledger.py add <ledger.csv> --label … "
                    f"--command … --audit-end …"
                )
                continue
            # Kiểm selfcheck_0vnd TRƯỚC khi đụng đĩa: đây là metadata, đúng/sai
            # không phụ thuộc file còn hay mất, và một ledger không cân sổ thì
            # không đủ điều kiện làm số pin dù file còn nguyên (registry rule 5).
            if not rec.get("selfcheck_0vnd"):
                violations.append(
                    f"[{short}] ledger {digest[:12]}… có trong kho nhưng "
                    f"selfcheck_0vnd=false ⇒ không đủ điều kiện làm số pin "
                    f"(registry rule 5)."
                )
                continue
            stored = os.path.join(wc_root, rec["stored"])
            if not os.path.exists(stored):
                violations.append(
                    f"[{short}] manifest có {digest[:12]}… nhưng file MẤT: {rec['stored']}"
                )
                continue
            got = pin_ledger.md5_of_gz_member(stored)
            if got != digest:
                violations.append(
                    f"[{short}] bản lưu của {digest[:12]}… giải nén ra {got[:12]}… — "
                    f"KHÔNG khớp."
                )
                continue
            want_gz = rec.get("md5_gz")
            if want_gz and pin_ledger.md5_of_file(stored) != want_gz:
                violations.append(
                    f"[{short}] file .gz của {digest[:12]}… đã bị SỬA "
                    f"(md5_gz không khớp manifest)."
                )
                continue
            ok.append(f"{short}  → {digest[:12]}… {rec.get('label','')}")
    return violations, ok


STORE_REL = os.path.join("data", "pinned_ledgers")
MANIFEST_NAME = pin_ledger.MANIFEST_NAME


def check_store_immutability(wc_root: str, rev: str) -> list:
    """B6 — kho đã pin là CHỈ-THÊM: cấm xoá, cấm sửa, PINS.jsonl append-only.

    VÌ SAO: retention không phải lời hứa, nó phải là một thứ git từ chối làm.
    Một ledger đã pin mất đi = một con số neo kỳ vọng vĩnh viễn không tái lập
    được — đúng 2 ca đã xảy ra (`a953d4bb…`, `f30a5bea…`). Thiếu dung lượng thì
    nén thêm, KHÔNG xoá.
    """
    prefix = _git(["rev-parse", "--show-prefix"], wc_root, allow_fail=True).strip()
    store = (prefix + STORE_REL).replace(os.sep, "/")
    # ⚠️ HAI QUY ƯỚC ĐƯỜNG DẪN KHÁC NHAU CỦA GIT — đã cắn 2 lần trong CHÍNH file này:
    #   `git show <rev>:<path>`      → <path> tính từ GỐC REPO
    #   `git diff … -- <pathspec>`   → <pathspec> tính từ CWD
    # Chạy từ `WorkingClaude/` mà truyền "WorkingClaude/data/..." thì git đi tìm
    # "WorkingClaude/WorkingClaude/data/..." ⇒ diff RỖNG ⇒ gate im lặng cho qua
    # đúng lúc có người xoá artifact đã pin. `:(top)` ép pathspec về gốc repo.
    out = _git(["diff", "--cached", "--name-status", "-M", rev, "--", f":(top){store}"],
               wc_root, allow_fail=True)
    v = []
    manifest_rel = f"{store}/{MANIFEST_NAME}"
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        st, path = parts[0], parts[-1]
        if st.startswith("D"):
            v.append(f"XOÁ artifact đã pin: {path} — kho là CHỈ-THÊM (B6). "
                     f"Thiếu dung lượng thì nén, KHÔNG xoá.")
        elif st.startswith("R"):
            v.append(f"ĐỔI TÊN artifact đã pin: {line} — tên mang md5, đổi tên là "
                     f"phá đường dò.")
        elif st.startswith("M") and path != manifest_rel:
            v.append(f"SỬA artifact đã pin: {path} — bản lưu bất biến, muốn số mới "
                     f"thì pin ledger MỚI (md5 mới).")

    # PINS.jsonl: append-only — N dòng đầu của bản mới phải TRÙNG bản cũ
    old = _git(["show", f"{rev}:{manifest_rel}"], wc_root, allow_fail=True)
    new = _git(["show", f":{manifest_rel}"], wc_root, allow_fail=True)
    if old and new:
        o, nl = old.splitlines(), new.splitlines()
        if len(nl) < len(o):
            v.append(f"{MANIFEST_NAME}: mất {len(o) - len(nl)} dòng — manifest là APPEND-ONLY.")
        else:
            for i, (a, b) in enumerate(zip(o, nl), 1):
                if a != b:
                    v.append(f"{MANIFEST_NAME} dòng {i} BỊ SỬA — manifest là APPEND-ONLY; "
                             f"muốn bổ sung thông tin thì `pin_ledger.py annotate`.")
                    break
    return v


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="*", help="pre-commit truyền vào; bỏ qua file khác")
    ap.add_argument("--rev", default=None, help="so với rev này thay vì HEAD (dùng để test)")
    ap.add_argument("--worktree", action="store_true",
                    help="đọc bản trên ĐĨA thay vì bản trong index")
    ap.add_argument("--store-immutability", action="store_true",
                    help="B6: kiểm kho pinned_ledgers chỉ-thêm (không xoá/sửa/đổi tên)")
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--mutations", action="store_true")
    args = ap.parse_args(argv)

    if args.selfcheck:
        return _run_selfcheck(args.mutations)

    mode = os.environ.get("MIKE_PIN_GATE", "").strip().lower()
    if mode == "off":
        print("pin_artifact_gate: TẮT qua MIKE_PIN_GATE=off")
        return 0

    wc_root = os.environ.get("PIN_STORE_WC_ROOT") or find_wc_root(__file__)

    if args.store_immutability:
        v = check_store_immutability(wc_root, args.rev or "HEAD")
        if not v:
            return 0
        print("\n🔴 pin-store BẤT BIẾN — commit này đang PHÁ kho đã pin (B6):")
        for x in v:
            print(f"   · {x}")
        print("\n   Kho `data/pinned_ledgers/` CHỈ ĐƯỢC THÊM. Bỏ qua 1 lần: "
              "MIKE_PIN_GATE=warn git commit …")
        if mode == "warn":
            print("\n   ⚠️ MIKE_PIN_GATE=warn ⇒ CHO QUA lần này. Lần sau vẫn chặn.")
            return 0
        return 1

    reg_abs = os.path.join(wc_root, REGISTRY_REL)

    if args.files:
        touched = any(os.path.abspath(f) == os.path.abspath(reg_abs)
                      or f.replace("\\", "/").endswith("data/results_registry.md")
                      for f in args.files)
        if not touched:
            return 0

    rev = args.rev or "HEAD"
    rel = repo_rel_registry(wc_root)
    if args.worktree:
        if not os.path.exists(reg_abs):
            print(f"Không thấy {reg_abs}")
            return 2
        new_text = open(reg_abs, encoding="utf-8").read()
    else:
        new_text = _git(["show", f":{rel}"], wc_root, allow_fail=True)
        if not new_text:
            new_text = open(reg_abs, encoding="utf-8").read() if os.path.exists(reg_abs) else ""
    old_text = _git(["show", f"{rev}:{rel}"], wc_root, allow_fail=True)

    if not new_text:
        print("pin_artifact_gate: không đọc được nội dung registry mới — KHÔNG gate.")
        return 0

    # FAIL-CLOSED có chủ đích: đọc được bản MỚI mà bản CŨ rỗng nghĩa là ratchet
    # KHÔNG hoạt động — mọi mục lịch sử sẽ bị coi là mới. Thà nói thẳng là không
    # gate được còn hơn phun 135 vi phạm giả rồi bị người ta tắt hẳn hook (§29).
    if not old_text.strip():
        print(
            f"⚠️ pin_artifact_gate: KHÔNG đọc được bản {rev} của `{rel}` "
            f"(git show trả rỗng) ⇒ không xác định được mục nào là MỚI.\n"
            f"   KHÔNG GATE lần này — đây là 'không kiểm được', KHÔNG phải 'sạch'."
        )
        return 0

    violations, ok = check_text(new_text, old_text, wc_root)

    for line in ok:
        print(f"  ✅ mục mới có ledger: {line}")
    if not violations:
        if ok:
            print(f"pin_artifact_gate: {len(ok)} mục mới, tất cả đều khai nguồn ledger. OK")
        return 0

    print("\n🔴 pin_artifact_gate — MỤC MỚI KHÔNG KHAI NGUỒN LEDGER:")
    for v in violations:
        print(f"   · {v}")
    print(
        "\n   Mỗi mục `## ` mới trong data/results_registry.md phải có ĐÚNG MỘT dòng:\n"
        "     ledger_md5: <32 ký tự hex>   (số lấy từ một ledger đã pin trong kho)\n"
        "     no_ledger: <lý do>           (mục không công bố số từ ledger)\n"
        "   Pin ledger: bin/pin_ledger.py add <csv> --label … --command … --audit-end …\n"
        "   Bỏ qua 1 lần (KHÔNG ghi nhớ): MIKE_PIN_GATE=warn git commit …"
    )
    if mode == "warn":
        print("\n   ⚠️ MIKE_PIN_GATE=warn ⇒ CHO QUA lần này. Lần sau vẫn chặn.")
        return 0
    return 1


# ----------------------------------------------------------------- selfcheck
def _run_selfcheck(mutations: bool) -> int:
    import json
    import shutil
    import tempfile

    n = 0
    fails = []

    def check(name, cond):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name)

    sandbox = tempfile.mkdtemp(prefix="pingate_sc_")
    try:
        wc = os.path.join(sandbox, "WorkingClaude")
        os.makedirs(os.path.join(wc, "data", "pinned_ledgers"), exist_ok=True)
        open(os.path.join(wc, "wc_env.sh"), "w").close()

        good = "a" * 32
        bad_selfcheck = "b" * 32
        # bản lưu THẬT cho `good`
        led = os.path.join(sandbox, "g.csv")
        with open(led, "w", encoding="utf-8") as fh:
            fh.write(pin_ledger._SAMPLE)
        real = pin_ledger.md5_of_file(led)

        class A:
            pass
        a = A()
        a.ledger, a.label, a.command = led, "sc", "CMD"
        a.audit_end, a.note, a.decided_by, a.pin_date = "2026-06-19", "", "agent", "2026-09-28"
        a.control_md5, a.control_byte_identical = None, False
        a.no_control = "sandbox selfcheck"
        pin_ledger.cmd_add(a, wc)

        # thêm 1 bản GIẢ có selfcheck_0vnd=false
        pin_ledger._atomic_append_line(
            pin_ledger.manifest_path(wc),
            json.dumps({"md5": bad_selfcheck, "label": "fake", "stored": "data/pinned_ledgers/x.gz",
                        "selfcheck_0vnd": False}))

        OLD = "# R\n\n## Mục cũ\nnội dung\n"

        def run(new):
            return check_text(new, OLD, wc)

        v, ok = run(OLD)
        check("khong_muc_moi_thi_khong_vi_pham", v == [] and ok == [])

        v, ok = run(OLD + "\n## Mục mới không khai gì\nCAGR 23,37%\n")
        check("muc_moi_thieu_khai_bi_chan", len(v) == 1 and "THIẾU" in v[0])

        v, ok = run(OLD + f"\n## Mục mới có ledger\nledger_md5: {real}\n")
        check("muc_moi_co_ledger_hop_le_qua", v == [] and len(ok) == 1)

        v, ok = run(OLD + "\n## Mục quy trình\nno_ledger: quyết định quy trình, không có số\n")
        check("no_ledger_co_ly_do_qua", v == [] and len(ok) == 1)

        v, ok = run(OLD + "\n## Mục rỗng lý do\nno_ledger:\n")
        check("no_ledger_rong_ly_do_bi_chan", len(v) == 1 and "THIẾU" in v[0])

        v, ok = run(OLD + f"\n## Khai cả hai\nledger_md5: {real}\nno_ledger: abc\n")
        check("khai_ca_hai_bi_chan", len(v) == 1 and "CẢ" in v[0])

        v, ok = run(OLD + f"\n## md5 la lo\nledger_md5: {good}\n")
        check("md5_khong_co_trong_kho_bi_chan", len(v) == 1 and "KHÔNG có trong" in v[0])

        v, ok = run(OLD + f"\n## selfcheck false\nledger_md5: {bad_selfcheck}\n")
        check("selfcheck_false_bi_chan", len(v) == 1 and "selfcheck_0vnd=false" in v[0])

        v, ok = run(OLD + f"\n## Có backtick\nledger_md5: `{real}`\n")
        check("chap_nhan_md5_trong_backtick", v == [] and len(ok) == 1)

        # SỬA mục cũ (không thêm mục mới) ⇒ không gate
        v, ok = run("# R\n\n## Mục cũ\nnội dung ĐÃ SỬA rất nhiều\nCAGR 99%\n")
        check("sua_muc_cu_khong_bi_gate", v == [] and ok == [])

        # 2 mục mới, 1 sai ⇒ đúng 1 vi phạm
        v, ok = run(OLD + f"\n## A\nledger_md5: {real}\n\n## B\nkhông khai\n")
        check("hai_muc_moi_bat_dung_1", len(v) == 1 and len(ok) == 1)

        # md5 có trong manifest nhưng FILE MẤT
        rec = [r for r in pin_ledger.read_manifest(wc) if r.get("md5") == real][0]
        stored_abs = os.path.join(wc, rec["stored"])
        os.rename(stored_abs, stored_abs + ".moved")
        v, ok = run(OLD + f"\n## File mat\nledger_md5: {real}\n")
        check("file_mat_bi_chan", len(v) == 1 and "MẤT" in v[0])
        os.rename(stored_abs + ".moved", stored_abs)

        # file .gz bị nối thêm rác ⇒ md5_gz lệch ⇒ chặn
        with open(stored_abs, "ab") as fh:
            fh.write(b"\x00")
        v, ok = run(OLD + f"\n## Gz bi sua\nledger_md5: {real}\n")
        check("gz_bi_noi_rac_bi_chan", len(v) == 1 and "bị SỬA" in v[0])

        # ---- B6: kho CHỈ-THÊM, test trên một repo git THẬT trong sandbox
        import subprocess as _sp

        def g(*a, cwd):
            return _sp.run(["git"] + list(a), cwd=cwd, capture_output=True, text=True)

        grepo = os.path.join(sandbox, "grepo")
        gwc = os.path.join(grepo, "WorkingClaude")
        os.makedirs(os.path.join(gwc, "data", "pinned_ledgers"), exist_ok=True)
        open(os.path.join(gwc, "wc_env.sh"), "w").close()
        g("init", "-q", cwd=grepo)
        g("config", "user.email", "t@t", cwd=grepo)
        g("config", "user.name", "t", cwd=grepo)
        st = os.path.join(gwc, "data", "pinned_ledgers")
        open(os.path.join(st, "PINS.jsonl"), "w").write('{"md5":"aa","label":"x"}\n')
        open(os.path.join(st, "a__aa.csv.gz"), "wb").write(b"one")
        g("add", "-A", cwd=grepo)
        g("commit", "-qm", "seed", cwd=grepo)
        check("B6_kho_khong_doi_thi_sach", check_store_immutability(gwc, "HEAD") == [])

        # THÊM bản mới + append manifest ⇒ hợp lệ
        open(os.path.join(st, "b__bb.csv.gz"), "wb").write(b"two")
        with open(os.path.join(st, "PINS.jsonl"), "a") as fh:
            fh.write('{"md5":"bb","label":"y"}\n')
        g("add", "-A", cwd=grepo)
        check("B6_them_moi_va_append_thi_qua", check_store_immutability(gwc, "HEAD") == [])
        g("commit", "-qm", "add", cwd=grepo)

        # XOÁ ⇒ chặn
        os.unlink(os.path.join(st, "a__aa.csv.gz"))
        g("add", "-A", cwd=grepo)
        r = check_store_immutability(gwc, "HEAD")
        check("B6_xoa_bi_chan", len(r) == 1 and "XOÁ" in r[0])
        g("reset", "-q", "--hard", "HEAD", cwd=grepo)

        # SỬA bản .gz ⇒ chặn
        open(os.path.join(st, "a__aa.csv.gz"), "wb").write(b"ONE-CHANGED")
        g("add", "-A", cwd=grepo)
        r = check_store_immutability(gwc, "HEAD")
        check("B6_sua_ban_luu_bi_chan", len(r) == 1 and "SỬA" in r[0])
        g("reset", "-q", "--hard", "HEAD", cwd=grepo)

        # SỬA dòng cũ của PINS.jsonl ⇒ chặn (append-only)
        open(os.path.join(st, "PINS.jsonl"), "w").write(
            '{"md5":"aa","label":"BI-SUA"}\n{"md5":"bb","label":"y"}\n')
        g("add", "-A", cwd=grepo)
        r = check_store_immutability(gwc, "HEAD")
        check("B6_sua_dong_cu_manifest_bi_chan",
              len(r) == 1 and "dòng 1 BỊ SỬA" in r[0])
        g("reset", "-q", "--hard", "HEAD", cwd=grepo)

        # XOÁ dòng manifest ⇒ chặn
        open(os.path.join(st, "PINS.jsonl"), "w").write('{"md5":"aa","label":"x"}\n')
        g("add", "-A", cwd=grepo)
        r = check_store_immutability(gwc, "HEAD")
        check("B6_xoa_dong_manifest_bi_chan", len(r) == 1 and "mất 1 dòng" in r[0])
        g("reset", "-q", "--hard", "HEAD", cwd=grepo)

        if mutations:
            killed = 0
            total = 0

            def mut(name, fn):
                nonlocal killed, total
                total += 1
                if fn():
                    killed += 1
                else:
                    fails.append(f"MUTATION SỐNG SÓT: {name}")

            # M1: nếu ratchet hỏng (xét cả mục cũ) thì "sửa mục cũ" đã bị bắt
            mut("M1_ratchet_chi_xet_muc_moi",
                lambda: check_text("# R\n\n## Mục cũ\nCAGR 99%\n", OLD, wc)[0] == [])
            # M2: regex md5 phải đúng 32 hex — 31 ký tự KHÔNG được coi là khai
            mut("M2_md5_31_ky_tu_khong_duoc_chap_nhan",
                lambda: "THIẾU" in check_text(OLD + f"\n## X\nledger_md5: {'a'*31}\n", OLD, wc)[0][0])
            # M3: md5 33 hex cũng không khớp (neo ^...$)
            mut("M3_md5_33_ky_tu_khong_duoc_chap_nhan",
                lambda: "THIẾU" in check_text(OLD + f"\n## X\nledger_md5: {'a'*33}\n", OLD, wc)[0][0])
            # M4: `ledger_md5` nằm giữa câu (không phải đầu dòng) KHÔNG tính là khai
            mut("M4_ledger_md5_giua_cau_khong_tinh",
                lambda: "THIẾU" in check_text(
                    OLD + f"\n## X\nxem ledger_md5: {real} ở trên\n", OLD, wc)[0][0])
            # M5: verify nội dung thật — md5 đúng format, có trong kho, nhưng bản lưu đã hỏng
            def m5():
                shutil.copy(stored_abs, stored_abs + ".bk")
                import gzip as _g
                with _g.GzipFile(stored_abs, "wb", mtime=0) as g:
                    g.write(b"khac han")
                r = check_text(OLD + f"\n## X\nledger_md5: {real}\n", OLD, wc)[0]
                shutil.move(stored_abs + ".bk", stored_abs)
                return len(r) == 1 and "KHÔNG khớp" in r[0]
            mut("M5_bat_duoc_noi_dung_ban_luu_doi", m5)

            # M6: B6 phai bat XOA (khong duoc am tham cho qua)
            def m6():
                os.unlink(os.path.join(st, "b__bb.csv.gz"))
                g("add", "-A", cwd=grepo)
                rr = check_store_immutability(gwc, "HEAD")
                g("reset", "-q", "--hard", "HEAD", cwd=grepo)
                return bool(rr)
            mut("M6_B6_that_su_chan_xoa", m6)

            print(f"mutation: {killed}/{total} bị giết")
            n += total
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)

    if fails:
        print(f"❌ FAIL {len(fails)}/{n}")
        for f in fails:
            print("   -", f)
        return 1
    print(f"✅ pin_artifact_gate selfcheck: {n} assertion PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
