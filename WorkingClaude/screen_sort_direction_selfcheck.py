#!/usr/bin/env python3
"""Selfcheck chiều sort/rank trong mọi `*_screen.py` (job Taylor_20260927_103434).

Vì sao cần: `fa_ratings_8l.rating` là thang 1–5 kiểu hãng xếp hạng tín nhiệm — **1 = AAA =
TỐT NHẤT** (`rating_8l.py` dòng 2/346; cổng production là `rating<=3`). 16 file sàng lọc viết
`sort_values(["rating","tv"], ascending=False).head(25)` rồi gọi kết quả là "8L top-25", tức
lấy đúng 25 mã **XẤU NHẤT**. Lỗi này KHÔNG có cách nào bắt bằng đọc code tuần tự — nó chỉ lộ ra
khi so chiều sort với NGỮ NGHĨA cột. Selfcheck này làm đúng việc đó, bằng AST trên file THẬT.

Chạy:
  $DNA_PYEXE screen_sort_direction_selfcheck.py              # scan + test hành vi, 4 môi trường TZ
  $DNA_PYEXE screen_sort_direction_selfcheck.py --mutations  # + mutation trên file thật
"""
import ast
import glob
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- BẢNG NGỮ NGHĨA CỘT: mỗi dòng phải trích được nguồn, không suy từ tên ------------------
# LOWER_BETTER: giá trị NHỎ hơn = tốt hơn ⇒ xếp TĂNG dần khi chọn top-N.
LOWER_BETTER = {
    # rating_8l.py:2 "8L Quality Rating 1-5 (credit-agency-style)"; :346 `rating = 2 if s>=6
    # else 3 if s>=4 else 4` (điểm CAO -> số rating THẤP); cổng production `rating<=3`.
    "rating",
}
# HIGHER_BETTER: giá trị LỚN hơn = tốt hơn ⇒ xếp GIẢM dần khi chọn top-N.
HIGHER_BETTER = {
    # `score` trong MỌI file là tổng z-score với cấu phần định giá ĐÃ ĐẢO DẤU (`negz`/`-zc(s)`)
    # và cấu phần chất lượng để dương ⇒ score cao = rẻ + tốt. Đã kiểm 23/23 chỗ gán score.
    "score",
    "tv",            # Trading_Value_1M_P50 — thanh khoản, dùng làm tie-break: nhiều hơn = tốt hơn
    "susp",          # forensic_screen.py:47 in rõ "susp score 0-5; higher = stronger signature"
    "roic5y", "med_ttm", "machine",   # cash_machine_screen.py: ROIC, TTM CFO/NP, cờ bool
    "ar_rev",        # forensic: AR/revenue càng cao càng đáng ngờ (đây là màn hình TÌM nghi vấn)
}
# NEUTRAL: cột định danh/thời gian — chiều là quy ước trình bày hoặc yêu cầu thuật toán
# (merge_asof cần time TĂNG; groupby().tail(1) cần time TĂNG để lấy bản ghi MỚI NHẤT).
NEUTRAL = {
    "time", "d", "dd", "Release_Date", "ticker", "quarter", "ym",
    "type", "engine", "route",
}
# DISPLAY_ONLY: có phải metric số thật, CÓ chiều "tốt/xấu", nhưng chỗ dùng duy nhất trong repo là
# in bảng cho người đọc, KHÔNG cắt top-N, KHÔNG vào quyết định chọn mã. Liệt kê TƯỜNG MINH ở đây
# thay vì nhét vào NEUTRAL để người đọc sau thấy được đây là phán xét, không phải sự thật về cột:
#   `turnover`, `state_pct` — soe_governance_screen.py:128 `flt.sort_values(["type","turnover"])`,
#   một vòng `for _, r in ....iterrows(): print(...)`. Nếu về sau có ai cắt top-N trên 2 cột này
#   thì phải chuyển chúng sang HIGHER_BETTER/LOWER_BETTER và chạy lại selfcheck.
DISPLAY_ONLY = {"turnover", "state_pct"}
NEUTRAL |= DISPLAY_ONLY

SELECTIVE_ATTRS = {"head", "tail"}   # sort rồi cắt top-N = quyết định CHỌN, không phải trình bày


def _const_list(node):
    """['a','b'] hoặc 'a' -> list[str]; không phải literal -> None."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, (ast.List, ast.Tuple)):
        out = []
        for e in node.elts:
            if isinstance(e, ast.Constant) and isinstance(e.value, str):
                out.append(e.value)
            else:
                return None
        return out
    return None


def _ascending(node, ncols):
    """kw ascending -> list[bool] dài ncols; None nếu không đọc được literal."""
    if node is None:
        return [True] * ncols          # pandas default
    if isinstance(node, ast.Constant) and isinstance(node.value, bool):
        return [node.value] * ncols
    if isinstance(node, (ast.List, ast.Tuple)):
        out = []
        for e in node.elts:
            if isinstance(e, ast.Constant) and isinstance(e.value, bool):
                out.append(e.value)
            else:
                return None
        return out if len(out) == ncols else None
    return None


def scan_file(path):
    """-> (violations, ambiguous, checked_count)"""
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src, filename=path)
    # cha của mỗi node, để biết kết quả sort có bị .head()/.tail() cắt ngay không
    parent = {}
    for n in ast.walk(tree):
        for c in ast.iter_child_nodes(n):
            parent[c] = n

    def is_selective(call):
        p = parent.get(call)
        # sort_values(...).head(25)  =>  call là .value của Attribute 'head', Attribute là .func
        if isinstance(p, ast.Attribute) and p.attr in SELECTIVE_ATTRS:
            return True
        return False

    viol, amb, n = [], [], 0
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        attr = node.func.attr
        kws = {k.arg: k.value for k in node.keywords if k.arg}

        if attr == "sort_values":
            by = None
            if node.args:
                by = _const_list(node.args[0])
            elif "by" in kws:
                by = _const_list(kws["by"])
            if by is None:
                amb.append((node.lineno, attr, "cột `by` không phải literal — không kết luận"))
                continue
            asc = _ascending(kws.get("ascending"), len(by))
            if asc is None:
                amb.append((node.lineno, attr, f"`ascending` không đọc được literal cho {by}"))
                continue
            n += 1
            sel = is_selective(node)
            for col, a in zip(by, asc):
                if col in LOWER_BETTER and a is not True:
                    viol.append((node.lineno, attr, col,
                                 f"`{col}` NHỎ hơn = tốt hơn nhưng đang xếp GIẢM dần "
                                 f"(ascending=False) ⇒ lấy đúng phần XẤU NHẤT"))
                elif col in HIGHER_BETTER and a is not False and sel:
                    viol.append((node.lineno, attr, col,
                                 f"`{col}` LỚN hơn = tốt hơn, sort này bị .head()/.tail() cắt "
                                 f"top-N nhưng đang xếp TĂNG dần"))
                elif col not in LOWER_BETTER and col not in HIGHER_BETTER and col not in NEUTRAL:
                    amb.append((node.lineno, attr, f"cột `{col}` chưa khai ngữ nghĩa"))

        elif attr in ("nlargest", "nsmallest"):
            col = None
            if len(node.args) >= 2:
                col = _const_list(node.args[1])
            elif "columns" in kws:
                col = _const_list(kws["columns"])
            if col is None:
                amb.append((node.lineno, attr, "cột không phải literal — không kết luận"))
                continue
            n += 1
            for c in col:
                if attr == "nlargest" and c in LOWER_BETTER:
                    viol.append((node.lineno, attr, c,
                                 f"nlargest trên `{c}` (NHỎ hơn = tốt hơn) ⇒ lấy phần XẤU NHẤT"))
                if attr == "nsmallest" and c in HIGHER_BETTER:
                    viol.append((node.lineno, attr, c,
                                 f"nsmallest trên `{c}` (LỚN hơn = tốt hơn) ⇒ lấy phần XẤU NHẤT"))
                if c not in LOWER_BETTER and c not in HIGHER_BETTER and c not in NEUTRAL:
                    amb.append((node.lineno, attr, f"cột `{c}` chưa khai ngữ nghĩa"))
    return viol, amb, n


def behaviour_test():
    """Test HÀNH VI (không phải scan text): biểu thức đã sửa phải chọn rating THẤP,
    và `tv` phải là tie-break GIẢM dần trong cùng mức rating."""
    import pandas as pd
    fails = []
    m = pd.DataFrame({
        "ticker": ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF"],
        "rating": [1, 1, 3, 5, 5, 2],
        "tv":     [1e9, 9e9, 5e9, 8e9, 2e9, 7e9],
    })
    fixed = m.sort_values(["rating", "tv"], ascending=[True, False]).head(3).ticker.tolist()
    if fixed != ["BBB", "AAA", "FFF"]:
        fails.append(f"biểu thức SỬA chọn sai: {fixed} (kỳ vọng ['BBB','AAA','FFF'] — "
                     f"rating tăng dần, tv giảm dần trong cùng rating)")
    buggy = m.sort_values(["rating", "tv"], ascending=False).head(3).ticker.tolist()
    if buggy != ["DDD", "EEE", "CCC"]:
        fails.append(f"biểu thức CŨ không tái hiện được lỗi: {buggy} "
                     f"(kỳ vọng ['DDD','EEE','CCC'] = 3 mã rating xấu nhất)")
    if set(fixed) & set(buggy):
        fails.append(f"2 rổ phải RỜI NHAU trên dữ liệu này: {set(fixed) & set(buggy)}")
    # tie-break: nếu tv cũng tăng dần thì thứ tự trong cùng rating phải đổi
    alt = m.sort_values(["rating", "tv"], ascending=[True, True]).head(3).ticker.tolist()
    if alt == fixed:
        fails.append("tie-break `tv` không có tác dụng — case test vô nghĩa")
    return fails


def run_scan(files, verbose=True):
    total_v, total_a, total_n = [], [], 0
    for p in files:
        v, a, n = scan_file(p)
        total_n += n
        for x in v:
            total_v.append((p, *x))
        for x in a:
            total_a.append((p, *x))
    if verbose:
        for p, ln, attr, col, why in total_v:
            print(f"  VIOLATION {os.path.basename(p)}:{ln} {attr}({col}) — {why}")
    return total_v, total_a, total_n


MUTATIONS = [
    ("revert-fix-rating-desc",
     lambda t: t.replace('sort_values(["rating","tv"], ascending=[True, False])',
                         'sort_values(["rating","tv"], ascending=False)')),
    ("revert-fix-rating-desc-spaced",
     lambda t: t.replace('sort_values(["rating", "tv"], ascending=[True, False])',
                         'sort_values(["rating", "tv"], ascending=False)')),
    ("nlargest-on-rating",
     lambda t: t.replace('.nlargest(KA, "score")', '.nlargest(KA, "rating")')),
    ("nlargest-on-rating-K",
     lambda t: t.replace('.nlargest(K, "score")', '.nlargest(K, "rating")')),
    ("score-ascending-in-topN",
     lambda t: t.replace('sort_values("score", ascending=False).ticker.tolist()',
                         'sort_values("score", ascending=False).head(99).ticker.tolist()')
     .replace('sort_values("score", ascending=False).head(99)',
              'sort_values("score", ascending=True).head(99)')),
    ("nsmallest-on-score",
     lambda t: t.replace('.nlargest(KA, "score")', '.nsmallest(KA, "score")')),
    ("rating-ascending-explicit-False",
     lambda t: t.replace('ascending=[True, False])', 'ascending=[False, False])')),
]


def run_mutations(files, tmpdir):
    import shutil
    killed, survived = 0, []
    for mname, mfn in MUTATIONS:
        applied = []
        for p in files:
            s = open(p, encoding="utf-8").read()
            m = mfn(s)
            if m != s:
                dst = os.path.join(tmpdir, os.path.basename(p))
                open(dst, "w", encoding="utf-8").write(m)
                applied.append(dst)
        if not applied:
            survived.append(f"{mname} (KHÔNG áp được — pattern không khớp code hiện tại)")
            continue
        v, _, _ = run_scan(applied, verbose=False)
        if v:
            killed += 1
            print(f"  killed   {mname}  ({len(v)} violation trên {len(applied)} file)")
        else:
            survived.append(mname)
            print(f"  SURVIVED {mname}  (áp lên {len(applied)} file mà scan vẫn sạch)")
        for d in applied:
            os.remove(d)
    return killed, survived


def main():
    args = sys.argv[1:]
    if os.environ.get("_SSD_CHILD") == "1":
        # chạy thật trong 1 môi trường TZ
        files = sorted(glob.glob(os.path.join(HERE, "*_screen.py")))
        v, a, n = run_scan(files)
        bf = behaviour_test()
        for f in bf:
            print(f"  BEHAVIOUR FAIL {f}")
        print(f"__RESULT__ files={len(files)} sorts_checked={n} violations={len(v)} "
              f"ambiguous={len(a)} behaviour_fails={len(bf)}")
        if a:
            for p, ln, attr, why in a:
                print(f"  AMBIGUOUS {os.path.basename(p)}:{ln} {attr} — {why}")
        return 1 if (v or bf) else 0

    tzs = [("ICT", "Asia/Ho_Chi_Minh"), ("UTC", "UTC"),
           ("NY", "America/New_York"), ("no-TZ", None)]
    print(f"scan dir: {HERE}")
    print(f"môi trường TZ: {[t[0] for t in tzs]}")
    rc = 0
    results = {}
    for tzname, tz in tzs:
        env = dict(os.environ, _SSD_CHILD="1")
        env.pop("TZ", None)
        if tz:
            env["TZ"] = tz
        out = subprocess.run([sys.executable, os.path.abspath(__file__)],
                             capture_output=True, text=True, env=env, timeout=300)
        line = [l for l in out.stdout.splitlines() if l.startswith("__RESULT__")]
        print(f"\n--- TZ={tzname} rc={out.returncode}")
        for l in out.stdout.splitlines():
            if not l.startswith("__RESULT__"):
                print("  " + l if not l.startswith("  ") else l)
        if not line:
            print(f"  FATAL: không đọc được __RESULT__ — stderr={out.stderr[:400]}")
            rc = 1
            continue
        print("  " + line[0])
        results[tzname] = line[0]
        if out.returncode != 0:
            rc = 1
    if len(set(results.values())) > 1:
        print("\nFAIL: kết quả KHÁC nhau giữa các múi giờ (phải bất biến theo TZ):")
        for k, v in results.items():
            print(f"  {k}: {v}")
        rc = 1
    elif results:
        print(f"\nBẤT BIẾN theo TZ: cả {len(results)} môi trường cho cùng kết quả ✓")

    if "--mutations" in args or "--all" in args:
        import tempfile
        files = sorted(glob.glob(os.path.join(HERE, "*_screen.py")))
        print(f"\nMUTATION ({len(MUTATIONS)} đột biến, áp lên bản copy của file THẬT):")
        with tempfile.TemporaryDirectory() as td:
            killed, survived = run_mutations(files, td)
        print(f"\nMUTATION: {killed}/{len(MUTATIONS)} bị giết")
        if survived:
            print("  sống sót: " + "; ".join(survived))
            rc = 1

    print("\n" + ("PASS" if rc == 0 else "FAIL"))
    return rc


if __name__ == "__main__":
    sys.exit(main())
