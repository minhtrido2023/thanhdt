#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cổng cơ học: CẤM annualize theo SỐ PHIÊN (`yrs = N/252`, `sqrt(252)`) — CLAUDE.md §Backtest
bắt buộc THỜI GIAN LỊCH (`(t_last−t_first).days/365.25`, đúng `simulate_holistic_nav.metrics` —
nguồn của mọi con số trong `data/results_registry.md`).

Vì sao là CƠ HỌC chứ không phải một đoạn văn xuôi nữa (coding_guidelines § "Enforcement policy"):
luật lịch-không-phiên có trong CLAUDE.md từ lâu, mà audit measurement-integrity 2026-09-27 vẫn tìm
ra 2 vi phạm đang SỐNG trong đúng 2 script sinh số pin KB (`bootstrap_nav.py:51`,
`dsr_pbo_annex.py:142`) — hệ quả: cột CAGR của chúng cao giả ~+0,3pp so với cột CAGR của registry
nằm ngay bên cạnh, tức 2 con số cạnh nhau KHÔNG so sánh được. Đo thật trên R3: 3.106 return / 4.551
ngày lịch ⇒ 12,460y lịch vs 12,325y theo phiên.

Phát hiện bằng AST (không phải regex): `yrs = N / 252` và `yrs = N / ANN` (ANN là hằng ~252 trong
cùng module) chỉ khác nhau ở chỗ toán hạng phải là Name hay Num, mà cả hai đều viết xuống dòng được.

RATCHET per-file so với `kb/annualization_basis_baseline.json` (cùng cơ chế `tz_anchor_gate.py`):
nợ cũ không bắt sửa ngay, chỉ KHÔNG ĐƯỢC TĂNG.

Dùng:
  python3 mike/bin/annualization_basis_selfcheck.py --scan                # gate (rc=1 nếu vượt baseline)
  python3 mike/bin/annualization_basis_selfcheck.py --scan --root <dir>   # phạm vi khác
  python3 mike/bin/annualization_basis_selfcheck.py <file.py> ...         # chỉ liệt kê, rc=0
  python3 mike/bin/annualization_basis_selfcheck.py --selfcheck           # fixture + mutation
  python3 mike/bin/annualization_basis_selfcheck.py --seed-baseline       # kiểm kê lần đầu
  python3 mike/bin/annualization_basis_selfcheck.py --update-baseline [--accept-new-debt]
"""
import argparse
import ast
import json
import os
import sys

BIN_DIR = os.path.dirname(os.path.abspath(__file__))
MIKE_ROOT = os.path.dirname(BIN_DIR)
WC_ROOT = os.path.dirname(MIKE_ROOT)
BASELINE_PATH = os.path.join(MIKE_ROOT, "kb", "annualization_basis_baseline.json")

# Mẫu số "số phiên/năm" — khoảng hẹp quanh 252 có chủ đích: 240..260 phủ mọi biến thể thật gặp
# (250/252/253/256) mà không chạm các hằng số khác (365/365.25 là ĐÚNG, 12/52/4 là tần suất khác).
SESSION_DENOM_LO, SESSION_DENOM_HI = 240, 260
# Tên biến bị soi: chỉ những cái NGHĨA LÀ "số năm". Không soi mù mọi phép chia cho 252 (một số chỗ
# chia 252 hợp lệ: đổi vol ngày→năm trên chuỗi ĐÃ biết là phiên, đếm block...).
YEAR_NAME_HINTS = ("yrs", "years", "nyears", "n_yr", "yr_", "_yr")
SQRT_FUNCS = ("sqrt",)
SKIP_DIR_PARTS = (".git", "__pycache__", ".claude", "node_modules", "wc_venv", "site-packages")


def _is_session_number(node):
    return (isinstance(node, ast.Constant) and isinstance(node.value, (int, float))
            and not isinstance(node.value, bool)
            and SESSION_DENOM_LO <= float(node.value) <= SESSION_DENOM_HI)


def _module_session_consts(tree):
    """Tên hằng cấp module gán một số trong khoảng phiên (ANN = 252.0, TRADING_DAYS = 252)."""
    out = set()
    for node in tree.body:
        if isinstance(node, ast.Assign) and _is_session_number(node.value):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    out.add(tgt.id)
    return out


def _denom_is_session(node, consts):
    if _is_session_number(node):
        return True
    return isinstance(node, ast.Name) and node.id in consts


def _year_target(node):
    lowered = None
    if isinstance(node, ast.Name):
        lowered = node.id.lower()
    elif isinstance(node, ast.Attribute):
        lowered = node.attr.lower()
    if lowered is None:
        return False
    return any(h in lowered for h in YEAR_NAME_HINTS)


def _mentions_cagr(scope):
    """Scope này có tính CAGR/lợi nhuận hoá-năm hay không.

    RULE 2 CỐ Ý chỉ bắt `sqrt(252)` trong scope ĐÃ tính CAGR. Lý do đo được, không phải khẩu vị:
    quét toàn repo 2026-09-27 cho 600 hit nếu bắt mù, mà phần lớn là annualize ĐỘ BIẾN ĐỘNG
    (`rv = ret.rolling(20).std()*sqrt(252)`) — hợp lệ và không liên quan. Bất biến thật hẹp hơn:
    *trong cùng một khối metric của backtest, Sharpe phải cùng hệ quy chiếu với CAGR* — nếu CAGR
    theo lịch mà Sharpe theo phiên thì 2 con số cạnh nhau không nhất quán.
    """
    for node in ast.walk(scope):
        if isinstance(node, ast.Name) and "cagr" in node.id.lower():
            return True
        if isinstance(node, ast.Attribute) and "cagr" in node.attr.lower():
            return True
        if isinstance(node, ast.Constant) and isinstance(node.value, str) \
                and "cagr" in node.value.lower():
            return True
        # `nav[-1] ** (1 / yrs)` — hoá-năm không cần chữ "cagr" nào
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow) \
                and isinstance(node.right, ast.BinOp) and isinstance(node.right.op, ast.Div) \
                and _year_target(node.right.right):
            return True
    return False


def violations_in_source(src, path="<src>"):
    """[(lineno, rule, snippet)] — rule ∈ {"yrs-per-session", "sqrt-session-const"}."""
    tree = ast.parse(src)
    consts = _module_session_consts(tree)
    lines = src.splitlines()
    out = []

    def snip(node):
        i = node.lineno - 1
        return lines[i].strip()[:120] if 0 <= i < len(lines) else ""

    for node in ast.walk(tree):
        # RULE 1 — `<...yrs...> = <bất kỳ> / <hằng phiên>`
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        if targets and isinstance(getattr(node, "value", None), ast.BinOp) \
                and isinstance(node.value.op, ast.Div) \
                and _denom_is_session(node.value.right, consts) \
                and any(_year_target(t) for t in targets):
            out.append((node.lineno, "yrs-per-session", snip(node)))

    # RULE 2 — `sqrt(<hằng phiên>)`, CHỈ trong scope có tính CAGR (xem `_mentions_cagr`).
    scopes = [tree] + [n for n in ast.walk(tree)
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    flagged = set()
    for scope in scopes:
        if not _mentions_cagr(scope):
            continue
        for node in ast.walk(scope):
            if not (isinstance(node, ast.Call) and len(node.args) == 1 and not node.keywords):
                continue
            fname = node.func.attr if isinstance(node.func, ast.Attribute) else (
                node.func.id if isinstance(node.func, ast.Name) else None)
            if fname in SQRT_FUNCS and _denom_is_session(node.args[0], consts) \
                    and node.lineno not in flagged:
                flagged.add(node.lineno)
                out.append((node.lineno, "sqrt-session-const", snip(node)))
    out.sort()
    return out


def scan_paths(paths):
    """(per_file_counts, details, unparsable). Không parse được ⇒ KÊU, KHÔNG gate, KHÔNG đụng
    baseline (bài học tz_anchor_gate vòng 5: trả 0 im lặng rồi xoá key baseline)."""
    counts, details, unparsable = {}, {}, []
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8") as f:
                src = f.read()
            v = violations_in_source(src, p)
        except (SyntaxError, ValueError, UnicodeDecodeError) as exc:
            unparsable.append((p, f"{type(exc).__name__}: {exc}"))
            continue
        except OSError as exc:
            unparsable.append((p, f"OSError: {exc}"))
            continue
        rel = os.path.relpath(p, WC_ROOT)
        counts[rel] = len(v)
        if v:
            details[rel] = v
    return counts, details, unparsable


def walk_roots(roots):
    out = []
    for root in roots:
        if os.path.isfile(root):
            out.append(os.path.abspath(root))
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_PARTS
                            and not d.startswith("wt-")]
            if any(part in SKIP_DIR_PARTS for part in dirpath.split(os.sep)):
                continue
            for fn in filenames:
                if fn.endswith(".py"):
                    out.append(os.path.join(dirpath, fn))
    return sorted(set(out))


def load_baseline():
    if not os.path.exists(BASELINE_PATH):
        return {}
    with open(BASELINE_PATH, "r", encoding="utf-8") as f:
        return json.load(f).get("files", {})


def save_baseline(counts):
    tmp = BASELINE_PATH + ".tmp"
    payload = {"_doc": "Ratchet baseline cho annualization_basis_selfcheck.py (§Backtest: annualize "
                        "theo LỊCH 365.25, không theo phiên). Nợ cũ chỉ được GIẢM, không được tăng.",
               "files": {k: v for k, v in sorted(counts.items()) if v}}
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, BASELINE_PATH)


def cmd_scan(roots, update=False, accept_new_debt=False, seed=False):
    files = walk_roots(roots)
    counts, details, unparsable = scan_paths(files)
    for p, err in unparsable:
        print(f"annualization_basis: KHÔNG PARSE ĐƯỢC {p} ({err}) — không gate file này",
              file=sys.stderr)
    total = sum(counts.values())
    for rel in sorted(details):
        for lineno, rule, snippet in details[rel]:
            print(f"{rel}:{lineno}: {rule}: {snippet}")
    print(f"annualization_basis: {total} vi phạm / {len([1 for v in counts.values() if v])} file "
          f"(quét {len(files)} file .py)")
    if seed or update:
        base = load_baseline()
        if not seed:
            rising = {k: (base.get(k, 0), v) for k, v in counts.items() if v > base.get(k, 0)}
            if rising and not accept_new_debt:
                for k, (o, n) in sorted(rising.items()):
                    print(f"  TỪ CHỐI nâng baseline {k}: {o} → {n}", file=sys.stderr)
                print("annualization_basis: baseline chỉ được HẠ; thêm --accept-new-debt nếu cố ý.",
                      file=sys.stderr)
                return 1
        save_baseline(counts)
        print(f"annualization_basis: đã ghi baseline {BASELINE_PATH}")
        return 0
    base = load_baseline()
    over = {k: (base.get(k, 0), v) for k, v in counts.items() if v > base.get(k, 0)}
    if over:
        for k, (o, n) in sorted(over.items()):
            print(f"annualization_basis: CHẶN {k}: {n} vi phạm > baseline {o} — annualize theo "
                  f"LỊCH ((t_last−t_first).days/365.25), không theo số phiên", file=sys.stderr)
        return 1
    print("annualization_basis: PASS (không file nào vượt baseline)")
    return 0


FIX_OK = '''
import pandas as pd
def f(s):
    idx = pd.DatetimeIndex(s.index)
    yrs = (idx[-1] - idx[0]).days / 365.25
    ann = (len(s) - 1) / yrs
    return yrs, ann
'''
BAD_LITERAL = '''
import numpy as np
def boot(s):
    r = np.diff(np.log(s)); N = len(r); yrs = N / 252.0
    nav = np.exp(np.cumsum(r))
    return nav[-1] ** (1 / yrs) - 1, r.mean() / r.std() * np.sqrt(252)
'''
BAD_CONST = '''
import math
ANN = 252.0
def m(logp, nav):
    yrs = len(logp)/ANN
    cagr = nav[-1]**(1/yrs) - 1
    return cagr, logp.mean()/logp.std()*math.sqrt(ANN)
'''
BAD_MULTILINE = '''
TRADING_DAYS = 253
def g(n):
    n_yrs = (
        n
        / TRADING_DAYS
    )
    return n_yrs
'''
NOT_A_VIOLATION = '''
import numpy as np
BLOCK = 252
def realized_vol(r):
    return r.rolling(20).std() * np.sqrt(252)   # annualize ĐỘ BIẾN ĐỘNG — hợp lệ, không phải CAGR
def h(r):
    n_blocks = len(r) / BLOCK          # đếm block, không phải số năm
    vol_ann = r.std() * np.sqrt(250.0 / 1)  # biểu thức, không phải hằng đơn
    days_per_month = 252 / 12
    return n_blocks, vol_ann, days_per_month
'''


def cmd_selfcheck():
    n = 0

    def chk(cond, msg):
        nonlocal n
        if not cond:
            raise AssertionError(msg)
        n += 1

    v = violations_in_source(FIX_OK)
    chk(v == [], f"bản ĐÚNG (lịch 365.25) phải sạch, được {v}")

    v = violations_in_source(BAD_LITERAL)
    chk([r for _, r, _ in v] == ["yrs-per-session", "sqrt-session-const"],
        f"N/252.0 + sqrt(252) phải ra đúng 2 vi phạm, được {v}")

    v = violations_in_source(BAD_CONST)
    chk(len(v) == 2 and {r for _, r, _ in v} == {"yrs-per-session", "sqrt-session-const"},
        f"chia cho hằng ANN=252.0 + sqrt(ANN) phải bị bắt, được {v}")

    v = violations_in_source(BAD_MULTILINE)
    chk([r for _, r, _ in v] == ["yrs-per-session"],
        f"phép chia viết XUỐNG DÒNG phải bị bắt (regex sẽ trượt), được {v}")

    v = violations_in_source(NOT_A_VIOLATION)
    chk(v == [], f"3 ca chia-252 hợp lệ KHÔNG được báo (false-positive), được {v}")

    # đổi 252 -> 365.25 ở mọi fixture xấu ⇒ phải sạch (chứng minh cổng soi ĐÚNG mẫu số)
    for name, src in (("BAD_LITERAL", BAD_LITERAL), ("BAD_CONST", BAD_CONST),
                      ("BAD_MULTILINE", BAD_MULTILINE)):
        fixed = src.replace("252.0", "365.25").replace("252", "365.25").replace("253", "365.25")
        chk(violations_in_source(fixed) == [],
            f"{name} sau khi đổi mẫu số sang 365.25 phải sạch, được {violations_in_source(fixed)}")

    # ca thật: 2 dòng audit chỉ ra, đọc từ CHÍNH file trên đĩa nếu còn ở dạng cũ
    for rel, want_rule in (("bootstrap_nav.py", "yrs-per-session"),
                            ("dsr_pbo_annex.py", "yrs-per-session")):
        path = os.path.join(WC_ROOT, rel)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            found = violations_in_source(f.read(), path)
        rules = {r for _, r, _ in found}
        state = "CÒN VI PHẠM" if want_rule in rules else "đã sửa sang lịch"
        print(f"  ca thật {rel}: {state} ({len(found)} hit: "
              f"{[(l, r) for l, r, _ in found]})")
        n += 1

    print(f"OK — {n} assertion PASS (annualization_basis_selfcheck.py)")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--root", action="append", default=[])
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--seed-baseline", action="store_true")
    ap.add_argument("--update-baseline", action="store_true")
    ap.add_argument("--accept-new-debt", action="store_true")
    args = ap.parse_args()

    if args.selfcheck:
        return cmd_selfcheck()
    if args.files and not args.scan:
        _, details, unparsable = scan_paths([os.path.abspath(f) for f in args.files])
        for p, err in unparsable:
            print(f"annualization_basis: KHÔNG PARSE ĐƯỢC {p} ({err})", file=sys.stderr)
        for rel in sorted(details):
            for lineno, rule, snippet in details[rel]:
                print(f"{rel}:{lineno}: {rule}: {snippet}")
        if not details:
            print("annualization_basis: 0 vi phạm")
        return 0
    roots = args.root or args.files or [WC_ROOT, os.path.join(MIKE_ROOT, "bin")]
    return cmd_scan(roots, update=args.update_baseline,
                    accept_new_debt=args.accept_new_debt, seed=args.seed_baseline)


if __name__ == "__main__":
    raise SystemExit(main())
