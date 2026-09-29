#!/usr/bin/env python3
"""B3 — trích số hiệu suất vào KB thì phải mang PROVENANCE.

LUẬT: một **khối văn bản MỚI** thêm vào `kb/canonical.md` / `kb/KNOWLEDGE.md`
mà công bố một con số hiệu suất (CAGR/Sharpe/Calmar/MaxDD kèm số) thì trong
CHÍNH khối đó phải có ít nhất một trong:
    · md5 ledger      — `4707bcbe…` hoặc 32 hex đầy đủ
    · tham chiếu pin  — `registry` / `results_registry` / tên mục `(sexies)`…
    · `no_pin: <lý do>` — khai tường minh là số này không có ledger

VÌ SAO KHỐI CHỨ KHÔNG PHẢI DÒNG: một đoạn KB thật hay tách thành nhiều dòng —
số ở dòng này, nguồn ở dòng kia. Bắt theo DÒNG sẽ oan gần như toàn bộ. Khối =
đoạn giữa hai dòng trống, đúng đơn vị mà người đọc thực sự đọc.

ĐÃ ĐO TRƯỚC KHI BẬT (mandate coding_guidelines: "luôn test luật mới trên file
thật"): xem `--measure` — chạy luật ngược lên toàn bộ lịch sử commit của 2 file
này và đếm xem nó sẽ chặn bao nhiêu khối đã từng được commit.

Ratchet: chỉ xét khối MỚI so với HEAD. Nội dung cũ KHÔNG bị đụng.
Lối thoát: `MIKE_PROV_GATE=warn` (qua 1 lần, không ghi nhớ) · `=off`.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from wc_paths import find_wc_root  # noqa: E402

WATCHED = ("mike/kb/canonical.md", "mike/kb/KNOWLEDGE.md")

# Từ neo: chỉ 4 chỉ tiêu hiệu suất, cố ý KHÔNG bắt mọi con số có `%`.
RE_ANCHOR = re.compile(r"\b(CAGR|Sharpe|Calmar|MaxDD)\b", re.I)
# Số kiểu VN (23,37) hoặc kiểu Anh (23.37) — phải có phần thập phân để loại
# những câu nhắc tên chỉ tiêu mà không công bố giá trị.
RE_NUMBER = re.compile(r"\d+[.,]\d+")
RE_PROV = re.compile(
    r"(`[0-9a-f]{8}…`|\b[0-9a-f]{32}\b|results_registry|registry|ledger_md5"
    r"|\((?:bis|ter|quater|quinquies|sexies|septies|octies)\))",
    re.I,
)
RE_OPTOUT = re.compile(r"^\s*no_pin:\s*(\S.*)$", re.M)


def _git(args, cwd, allow_fail=True):
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0 and not allow_fail:
        raise SystemExit(f"git {' '.join(args)} rc={r.returncode}: {r.stderr.strip()}")
    return r.stdout


def blocks(text: str) -> list:
    """Cắt văn bản thành khối theo dòng trống. Giữ nguyên nội dung khối."""
    out, cur = [], []
    for line in text.splitlines():
        if line.strip():
            cur.append(line)
        elif cur:
            out.append("\n".join(cur))
            cur = []
    if cur:
        out.append("\n".join(cur))
    return out


# Khối do CONSOLIDATOR tự sinh — miễn trừ, có bằng chứng chứ không phải nhân nhượng.
# Đo trên 116 commit thật của 2 file: 8/20 khối bị chặn là `## Consolidation <ts>`
# do cron `bin/consolidate.sh` ghi (nó chép nguyên văn payload bus vào KB). Chặn
# nhóm này = KẸT PIPELINE KB mỗi lần có một bus event mang số — tức gate tự bắn
# vào chân đường vận hành, và sẽ bị tắt hẳn trong một ngày.
# Provenance của nhóm này nằm ở CHỖ KHÁC: bus event gốc + trace_id.
RE_AUTOGEN = re.compile(r"^##\s+Consolidation\s+\d{4}-\d{2}-\d{2}T", re.M)


def is_autogen(block: str) -> bool:
    return bool(RE_AUTOGEN.match(block.lstrip("\n")))


def claims_number(block: str) -> bool:
    if is_autogen(block):
        return False
    return bool(RE_ANCHOR.search(block) and RE_NUMBER.search(block))


def has_provenance(block: str) -> bool:
    return bool(RE_PROV.search(block) or RE_OPTOUT.search(block))


def check_file(new_text: str, old_text: str) -> list:
    old_blocks = set(blocks(old_text))
    bad = []
    for b in blocks(new_text):
        if b in old_blocks:
            continue
        if claims_number(b) and not has_provenance(b):
            first = b.strip().splitlines()[0]
            bad.append(first if len(first) <= 100 else first[:97] + "…")
    return bad


def cmd_measure(wc_root: str, limit: int) -> int:
    """Chạy luật NGƯỢC lên lịch sử: nó sẽ chặn bao nhiêu khối đã từng commit?"""
    total_new = 0
    total_bad = 0
    per_file = {}
    # `mike/` là repo RIÊNG (nested) ⇒ trong repo đó đường dẫn là `kb/...`,
    # không phải `mike/kb/...`. Dùng đúng một cách tính với main(), đừng đoán.
    prefix = _git(["rev-parse", "--show-prefix"], wc_root).strip()
    for rel in WATCHED:
        path = (prefix + rel.split("mike/", 1)[-1]).replace(os.sep, "/")
        revs = _git(["log", f"-{limit}", "--format=%H", "--", path], wc_root).split()
        f_new = f_bad = 0
        for i, rev in enumerate(revs):
            new = _git(["show", f"{rev}:{path}"], wc_root)
            old = _git(["show", f"{rev}~1:{path}"], wc_root)
            if not new:
                continue
            nb = [b for b in blocks(new) if b not in set(blocks(old))]
            f_new += len(nb)
            f_bad += len([b for b in nb if claims_number(b) and not has_provenance(b)])
        per_file[path] = (f_new, f_bad, len(revs))
        total_new += f_new
        total_bad += f_bad
    print("ĐO LUẬT B3 NGƯỢC LÊN LỊCH SỬ (khối MỚI mỗi commit):")
    for p, (nn, bb, nr) in per_file.items():
        pct = (100.0 * bb / nn) if nn else 0.0
        print(f"  {p}: {nr} commit · {nn} khối mới · {bb} sẽ bị chặn ({pct:.1f}%)")
    pct = (100.0 * total_bad / total_new) if total_new else 0.0
    print(f"  TỔNG: {total_new} khối mới · {total_bad} bị chặn ({pct:.1f}%)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--rev", default="HEAD")
    ap.add_argument("--measure", type=int, default=0,
                    help="đo luật ngược lên N commit gần nhất của 2 file, KHÔNG gate")
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--mutations", action="store_true")
    args = ap.parse_args(argv)

    if args.selfcheck:
        return _run_selfcheck(args.mutations)

    wc_root = os.environ.get("PIN_STORE_WC_ROOT") or find_wc_root(__file__)
    mike_root = os.path.join(wc_root, "mike")
    if args.measure:
        return cmd_measure(mike_root, args.measure)

    mode = os.environ.get("MIKE_PROV_GATE", "").strip().lower()
    if mode == "off":
        print("number_provenance_gate: TẮT qua MIKE_PROV_GATE=off")
        return 0

    prefix = _git(["rev-parse", "--show-prefix"], mike_root).strip()
    violations = {}
    for rel in WATCHED:
        sub = rel.split("mike/", 1)[-1]
        if args.files and not any(f.replace("\\", "/").endswith(sub) for f in args.files):
            continue
        repo_path = (prefix + sub).replace(os.sep, "/")
        new = _git(["show", f":{repo_path}"], mike_root)
        if not new:
            abs_p = os.path.join(mike_root, sub)
            new = open(abs_p, encoding="utf-8").read() if os.path.exists(abs_p) else ""
        old = _git(["show", f"{args.rev}:{repo_path}"], mike_root)
        if not new:
            continue
        if not old.strip():
            # Cùng lớp bẫy đã cắn ở pin_artifact_gate: không đọc được bản cũ thì
            # MỌI khối trông như mới. Nói thẳng là không kiểm được (§29).
            print(f"⚠️ number_provenance_gate: không đọc được bản {args.rev} của `{repo_path}` "
                  f"⇒ KHÔNG GATE file này (không kiểm được ≠ sạch).")
            continue
        bad = check_file(new, old)
        if bad:
            violations[sub] = bad

    if not violations:
        return 0
    print("\n🔴 number_provenance_gate — KHỐI MỚI CÔNG BỐ SỐ MÀ KHÔNG KHAI NGUỒN (B3):")
    for f, items in violations.items():
        for it in items:
            print(f"   · {f}: {it}")
    print(
        "\n   Khối công bố CAGR/Sharpe/Calmar/MaxDD phải có trong CÙNG khối một trong:\n"
        "     · md5 ledger  `4707bcbe…`  (hoặc 32 hex đầy đủ)\n"
        "     · tham chiếu registry / tên mục pin  (sexies), (septies)…\n"
        "     · no_pin: <lý do>   — số này không đến từ một ledger đã pin\n"
        "   Bỏ qua 1 lần (KHÔNG ghi nhớ): MIKE_PROV_GATE=warn git commit …"
    )
    if mode == "warn":
        print("\n   ⚠️ MIKE_PROV_GATE=warn ⇒ CHO QUA lần này. Lần sau vẫn chặn.")
        return 0
    return 1


def _run_selfcheck(mutations: bool) -> int:
    n = 0
    fails = []

    def check(name, cond):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name)

    OLD = "# KB\n\nĐoạn cũ không có số.\n"

    check("khong_doi_thi_sach", check_file(OLD, OLD) == [])
    check("khoi_moi_khong_co_so_thi_qua",
          check_file(OLD + "\nMột ghi chú bình thường.\n", OLD) == [])
    check("cong_bo_CAGR_khong_nguon_bi_chan",
          len(check_file(OLD + "\nR3 CAGR 23,37% rất tốt.\n", OLD)) == 1)
    check("co_md5_rut_gon_thi_qua",
          check_file(OLD + "\nR3 CAGR 23,37% (md5 `4707bcbe…`).\n", OLD) == [])
    check("co_md5_32hex_thi_qua",
          check_file(OLD + "\nCAGR 23,37% 4707bcbeb7e801d49a4a851ffd91d5e7\n", OLD) == [])
    check("co_tham_chieu_registry_thi_qua",
          check_file(OLD + "\nCAGR 23,37%; xem results_registry mục sexies.\n", OLD) == [])
    check("co_ten_muc_pin_thi_qua",
          check_file(OLD + "\nCAGR 23,37% (sexies)\n", OLD) == [])
    check("no_pin_thi_qua",
          check_file(OLD + "\nCAGR ước lượng 20,0%\nno_pin: số tham khảo từ báo cáo ngoài\n",
                     OLD) == [])
    check("nguon_o_DONG_KHAC_cung_khoi_van_qua",
          check_file(OLD + "\nR3 đạt CAGR 23,37%\nSharpe 1,88 — nguồn: registry.\n", OLD) == [])
    check("nguon_o_KHOI_KHAC_thi_KHONG_tinh",
          len(check_file(OLD + "\nR3 đạt CAGR 23,37%\n\nnguồn: registry\n", OLD)) == 1)
    check("nhac_ten_chi_tieu_khong_co_so_thi_qua",
          check_file(OLD + "\nSharpe là một chỉ tiêu rủi ro.\n", OLD) == [])
    check("so_nguyen_khong_thap_phan_thi_qua",
          check_file(OLD + "\nCó 12 vị thế Sharpe tối đa.\n", OLD) == [])
    check("so_kieu_Anh_cung_bi_bat",
          len(check_file(OLD + "\nCAGR 23.37% no source\n", OLD)) == 1)
    check("khoi_cu_giu_nguyen_khong_bi_bat",
          check_file("CAGR 23,37% không nguồn\n", "CAGR 23,37% không nguồn\n") == [])
    check("khoi_Consolidation_tu_sinh_duoc_mien_tru",
          check_file(OLD + "\n## Consolidation 2026-09-28T01:02:03Z\nCAGR 23,37% khong nguon\n",
                     OLD) == [])
    check("mien_tru_KHONG_lan_sang_khoi_thuong",
          len(check_file(OLD + "\n## Consolidation ghi chu tay\nCAGR 23,37%\n", OLD)) == 1)
    check("no_pin_rong_khong_duoc_tinh",
          len(check_file(OLD + "\nCAGR 23,37%\nno_pin:\n", OLD)) == 1)

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

        mut("M1_that_su_chan_khoi_thieu_nguon",
            lambda: len(check_file(OLD + "\nCAGR 99,9%\n", OLD)) == 1)
        mut("M2_ratchet_that_su_bo_qua_khoi_cu",
            lambda: check_file("CAGR 9,9%\n", "CAGR 9,9%\n") == [])
        mut("M3_md5_7_ky_tu_khong_duoc_tinh_la_nguon",
            lambda: len(check_file(OLD + "\nCAGR 23,37% `4707bcb…`\n", OLD)) == 1)
        mut("M4_anchor_phai_la_tu_rieng",
            lambda: check_file(OLD + "\nSharpener 23,37 mm\n", OLD) == [])
        print(f"mutation: {killed}/{total} bị giết")
        n += total

    if fails:
        print(f"❌ FAIL {len(fails)}/{n}")
        for f in fails:
            print("   -", f)
        return 1
    print(f"✅ number_provenance_gate selfcheck: {n} assertion PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
