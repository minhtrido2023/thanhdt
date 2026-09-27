#!/usr/bin/env python3
"""Cổng CƠ HỌC: mọi rail park-fraction phải BẰNG NHAU theo GIÁ TRỊ (§28 coding_guidelines).

VÌ SAO (bài học 2026-08-04, tái diễn 2026-09-27): mức park sống ở nhiều chỗ độc lập, không chỗ
nào đọc chỗ nào:
  R1 đường MUA      — deploy_golive_dt5g_v4/golive_recommend_v23.py  ETF_PARK = {3: x}
  R2 đường BÁN / L1 — mike/bin/compute_park_trim.py                  (ĐỌC R3 từ 2026-09-27)
  R3 cổng chính sách— data/trading_rules.json  neutral_parking.default_park_of_idle_pct
2026-08-04: R1 để 0,70 trong khi R2/R3 lên 0,80 → "mua tới 70% nhưng chỉ trim khi vượt 80%".
2026-09-27: user chốt 0,30, R1+R3 đổi, **R2 vẫn 0,80** (hardcode, KHÔNG đọc trading_rules.json)
→ hệ mua tới 30% nhưng chỉ trim khi vượt 80% ⇒ sổ PARK cũ ~80% KHÔNG BAO GIỜ bị đưa về 30%.
Cả hai lần đều IM LẶNG. Cổng này biến "im lặng" thành exit≠0.

**ĐỔI 2026-09-27 — R2 đã được WIRE đọc R3, nên hằng số literal của R2 KHÔNG CÒN TỒN TẠI.** Cổng
không đọc literal đã biến mất được; nó đọc **GIÁ TRỊ R2 THỰC SỰ DÙNG** bằng cách trích chính
`park_target_from_rules()` (+ lớp exception của nó) ra khỏi file R2 bằng `ast` rồi **THỰC THI** nó
trên `trading_rules.json` của cây đang kiểm. Tức cổng chạy ĐÚNG đường code production, không phải
một bản sao logic (§28: so giá trị, không so văn xuôi — và cũng không so một bản chép lại).
Không `import compute_park_trim` vì module đó kéo theo `trading_bot`/`park_holdings`/DNSE; cổng
phải chạy được trên một sandbox chỉ có 3 file.

Cổng cũng CHẶN việc hardcode quay lại: một literal `PARK_TARGET_F1 = <số>` bằng đúng R3 hôm nay vẫn
là bản sao sẽ lệch ngày mai — đó chính là cơ chế đã cắn 2 lần ⇒ coi là LỆCH (rc=1), không phải PASS.

ĐỌC GIÁ TRỊ, KHÔNG ĐỌC VĂN XUÔI: R1 parse bằng `ast` — regex đếm sai khi hằng số viết xuống dòng
hoặc có comment cùng dòng (đúng bài học §16 `tz_anchor_gate.py`).

Dùng: python3 park_rail_consistency_selfcheck.py [--wc-root DIR] [--selftest]
exit 0 = các rail khớp · 1 = LỆCH (gồm cả hardcode quay lại) · 2 = không đọc/không chạy được một
rail (fail-CLOSED, không đoán).
"""
import argparse
import ast
import json
import os
import sys

TOL = 1e-9
R1_REL = os.path.join("deploy_golive_dt5g_v4", "golive_recommend_v23.py")
R2_REL = os.path.join("bin", "compute_park_trim.py")   # tương đối MIKE root (repo lồng riêng)
R3_REL = os.path.join("data", "trading_rules.json")
# Tên hàm/lớp của R2 mà cổng trích ra và chạy. Đổi tên ở R2 mà không đổi ở đây ⇒ rc=2 (fail-closed),
# KHÔNG phải pass im lặng.
R2_RESOLVER = "park_target_from_rules"
R2_EXC = "ParkTargetUnavailable"


class RailUnreadable(Exception):
    """Không đọc/không chạy được một rail. Mang theo BẰNG CHỨNG THẬT vừa đọc (§29)."""


def rail_golive(path):
    """R1: `ETF_PARK = {3: x}` → x."""
    try:
        src = open(path, encoding="utf-8").read()
    except OSError as e:
        raise RailUnreadable(f"R1 {path}: {type(e).__name__}: {e}") from e
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        raise RailUnreadable(f"R1 {path} không parse được: {e}") from e
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "ETF_PARK" for t in node.targets):
            if isinstance(node.value, ast.Dict):
                for k, v in zip(node.value.keys, node.value.values):
                    if isinstance(k, ast.Constant) and k.value == 3:
                        try:
                            return float(ast.literal_eval(v))
                        except (ValueError, TypeError, SyntaxError) as e:
                            raise RailUnreadable(
                                f"R1 {path}: ETF_PARK[3] không là hằng số đọc được — "
                                f"{ast.dump(v)[:120]} ({e})") from e
    raise RailUnreadable(f"R1 {path}: không tìm thấy phép gán `ETF_PARK = {{3: …}}`")


def rail_rules(path):
    """R3 đọc ĐỘC LẬP với R2 (cố ý trùng logic tối thiểu: đây là phía 'kỳ vọng' của phép so)."""
    try:
        d = json.load(open(path, encoding="utf-8"))
    except OSError as e:
        raise RailUnreadable(f"R3 {path}: {type(e).__name__}: {e}") from e
    except ValueError as e:
        raise RailUnreadable(f"R3 {path} không phải JSON hợp lệ — parser nói: {e}") from e
    try:
        v = d["neutral_parking"]["default_park_of_idle_pct"]
    except (KeyError, TypeError) as e:
        raise RailUnreadable(
            f"R3 {path}: thiếu neutral_parking.default_park_of_idle_pct ({type(e).__name__}: {e}); "
            f"khoá cấp 1 ĐỌC ĐƯỢC: {sorted(d) if isinstance(d, dict) else type(d).__name__}") from e
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise RailUnreadable(f"R3 {path}: giá trị {v!r} (type {type(v).__name__}) không phải số")
    return float(v)


def _extract(tree, names):
    """Lấy nguyên văn các def/class tên trong `names` ra khỏi AST đã parse."""
    out = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names:
            out[node.name] = node
    return out


def rail_trim_effective(r2_path, r3_path):
    """R2: GIÁ TRỊ THỰC SỰ DÙNG — chạy chính resolver của R2 trên `r3_path`.

    Trả (value, hardcode_literal_or_None). `hardcode_literal` ≠ None nghĩa là literal
    `PARK_TARGET_F1 = <số>` đã QUAY LẠI file R2 ⇒ caller coi là LỆCH.
    """
    try:
        src = open(r2_path, encoding="utf-8").read()
    except OSError as e:
        raise RailUnreadable(f"R2 {r2_path}: {type(e).__name__}: {e}") from e
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        raise RailUnreadable(f"R2 {r2_path} không parse được: {e}") from e

    hard = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "PARK_TARGET_F1" for t in node.targets):
            try:
                hard = float(ast.literal_eval(node.value))
            except (ValueError, TypeError, SyntaxError):
                hard = None   # gán từ biểu thức (vd gọi resolver) — không phải hardcode

    got = _extract(tree, {R2_RESOLVER, R2_EXC})
    missing = sorted({R2_RESOLVER, R2_EXC} - set(got))
    if missing:
        raise RailUnreadable(
            f"R2 {r2_path}: không trích được {missing} ở cấp module. Top-level def/class ĐỌC ĐƯỢC "
            f"THẬT: {[n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]}")

    mod = ast.Module(body=[got[R2_EXC], got[R2_RESOLVER]], type_ignores=[])
    ns = {"json": json, "os": os}
    try:
        exec(compile(ast.fix_missing_locations(mod), r2_path, "exec"), ns)   # noqa: S102
    except Exception as e:      # noqa: BLE001 — bất kỳ lý do nào cũng là fail-closed, có bằng chứng
        raise RailUnreadable(
            f"R2 {r2_path}: exec {R2_RESOLVER} thất bại — {type(e).__name__}: {e}. "
            f"(cổng chỉ cấp sẵn `json`,`os`; resolver cần thêm gì thì cổng phải được cập nhật)") from e
    try:
        v = ns[R2_RESOLVER](r3_path)
    except Exception as e:      # noqa: BLE001 — gồm ParkTargetUnavailable: R2 TỪ CHỐI ⇒ fail-closed
        raise RailUnreadable(
            f"R2 {r2_path}: {R2_RESOLVER}({r3_path}) raise {type(e).__name__}: {e}") from e
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise RailUnreadable(f"R2: {R2_RESOLVER} trả {v!r} (type {type(v).__name__}), không phải số")
    return float(v), hard


def check(wc, verbose=True, mike=None):
    """`mike` = gốc repo lồng `mike/` (mặc định `<wc>/mike`). Tách ra vì R2 nằm ở REPO KHÁC với
    R1/R3 ⇒ khi R2 đang ở một worktree của repo `mike` (kiểm TRƯỚC khi merge) phải trỏ được vào đó,
    không thì cổng chỉ kiểm được sau khi đã merge — tức quá muộn."""
    rails, errs, hard = {}, [], None
    mike = mike or os.path.join(wc, "mike")
    r3_path = os.path.join(wc, R3_REL)
    for label, fn in (
            ("R1 MUA    golive_recommend_v23.ETF_PARK[3]", lambda: rail_golive(os.path.join(wc, R1_REL))),
            ("R2 BÁN    compute_park_trim GIÁ TRỊ THỰC DÙNG", lambda: rail_trim_effective(os.path.join(mike, R2_REL), r3_path)),
            ("R3 POLICY trading_rules.default_park_of_idle_pct", lambda: rail_rules(r3_path))):
        try:
            v = fn()
            if isinstance(v, tuple):
                v, hard = v
            rails[label] = v
        except RailUnreadable as e:
            errs.append(str(e))
    if verbose:
        for k, v in rails.items():
            print(f"  {k:52s} = {v}")
    if errs:
        if verbose:
            print("❌ FAIL-CLOSED (rc=2) — không đọc được rail:")
            for e in errs:
                print(f"    · {e}")
        return 2
    if hard is not None:
        if verbose:
            print(f"❌ HARDCODE QUAY LẠI (rc=1): R2 lại có `PARK_TARGET_F1 = {hard}` ở cấp module. "
                  f"Bằng đúng R3 hôm nay vẫn là BẢN SAO sẽ lệch ngày mai — chính cơ chế đã cắn "
                  f"2026-08-04 và 2026-09-27. R2 phải ĐỌC R3, không giữ literal.")
        return 1
    vals = list(rails.values())
    if max(vals) - min(vals) > TOL:
        if verbose:
            print(f"❌ LỆCH RAIL (rc=1): {min(vals)} … {max(vals)} — đường MUA và đường BÁN sẽ "
                  f"đánh nhau im lặng (bài học 2026-08-04 / 2026-09-27).")
        return 1
    if verbose:
        print(f"✅ các rail khớp = {vals[0]}  (R2 lấy từ R3 bằng chính resolver của nó)")
    return 0


def selftest(wc, mike=None):
    """Mutation: cổng phải GIẾT được mỗi kiểu lệch, và phải PASS trên cây đã đồng bộ."""
    import shutil
    import tempfile
    fails = []
    with tempfile.TemporaryDirectory() as td:
        sand = os.path.join(td, "wc")
        mike = mike or os.path.join(wc, "mike")
        for rel, src_root in ((R1_REL, wc), (R3_REL, wc), (R2_REL, mike)):
            dst = os.path.join(sand, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(os.path.join(src_root, rel), dst)

        def put(rel, old, new, n=1):
            p = os.path.join(sand, rel)
            s = open(p, encoding="utf-8").read()
            assert old in s, f"{rel}: không thấy {old!r}"
            open(p, "w", encoding="utf-8").write(s.replace(old, new, n))

        def r3_set(val):
            p = os.path.join(sand, R3_REL)
            s = open(p, encoding="utf-8").read()
            import re as _re
            s2, n = _re.subn(r'"default_park_of_idle_pct":\s*[^,}\n]+', 
                             f'"default_park_of_idle_pct": {val}', s, count=1)
            assert n == 1, "không thấy khoá default_park_of_idle_pct trong R3 sandbox"
            open(p, "w", encoding="utf-8").write(s2)

        def r1_set(val):
            p = os.path.join(sand, R1_REL)
            s = open(p, encoding="utf-8").read()
            import re as _re
            s2, n = _re.subn(r"ETF_PARK = \{3:\s*[0-9.]+\}", f"ETF_PARK = {{3: {val}}}", s, count=1)
            assert n == 1, "không thấy ETF_PARK={3: …} trong R1 sandbox"
            open(p, "w", encoding="utf-8").write(s2)

        def run(label, rc_want):
            rc = check(sand, verbose=False, mike=sand)
            ok = "✅" if rc == rc_want else "❌"
            print(f"  {ok} {label:58s} → rc={rc} (kỳ vọng {rc_want})")
            if rc != rc_want:
                fails.append(label.split()[0])

        # M0 — cây thật, đã đồng bộ ⇒ PASS (chứng minh cổng không fail bừa)
        r3_set(0.30); r1_set(0.30)
        run("M0 cây đồng bộ @0.30", 0)
        # M1 — **mutation QUAN TRỌNG NHẤT**: đổi R3+R1 sang một mức KHÁC. Cổng cũ (đọc literal R2)
        #      sẽ báo LỆCH; cổng mới phải PASS vì R2 đã THỰC SỰ đi theo R3.
        r3_set(0.55); r1_set(0.55)
        run("M1 R3+R1 = 0.55 ⇒ R2 phải TỰ theo", 0)
        # M2 — R1 lệch (ca THẬT 2026-08-04)
        r1_set(0.70)
        run("M2 R1 0.70 vs R3 0.55", 1)
        r3_set(0.30); r1_set(0.30)
        # M3 — hardcode QUAY LẠI, bằng đúng R3 ⇒ vẫn phải bị chặn
        put(R2_REL, "PARK_TARGET_RULES = os.path.join",
            "PARK_TARGET_F1 = 0.30\nPARK_TARGET_RULES = os.path.join")
        run("M3 R2 hardcode quay lại (= R3)", 1)
        put(R2_REL, "PARK_TARGET_F1 = 0.30\nPARK_TARGET_RULES = os.path.join",
            "PARK_TARGET_RULES = os.path.join")
        run("M3b sau khi gỡ hardcode → lại PASS", 0)
        # M4 — resolver của R2 bị xoá tên ⇒ rc=2, KHÔNG âm thầm pass
        put(R2_REL, f"def {R2_RESOLVER}(path):", "def park_target_RENAMED(path):")
        run("M4 R2 resolver bị đổi tên", 2)
        put(R2_REL, "def park_target_RENAMED(path):", f"def {R2_RESOLVER}(path):")
        # M5 — R2 đọc SAI khoá (giả vờ wire nhưng trỏ chỗ khác) ⇒ resolver raise ⇒ rc=2
        put(R2_REL, '"default_park_of_idle_pct"', '"khoa_khong_ton_tai"', n=99)
        run("M5 R2 trỏ sang khoá không tồn tại", 2)
        put(R2_REL, '"khoa_khong_ton_tai"', '"default_park_of_idle_pct"', n=99)
        run("M5b sau khi trả lại khoá đúng → PASS", 0)
        # M6 — R3 mất khoá ⇒ rc=2 (cả R2 và R3 đều không đọc được)
        put(R3_REL, '"default_park_of_idle_pct"', '"default_park_of_idle_pct_DISABLED"')
        run("M6 R3 mất khoá", 2)
        put(R3_REL, '"default_park_of_idle_pct_DISABLED"', '"default_park_of_idle_pct"')
        # M7 — R3 ngoài [0,1] ⇒ rc=2 (R2 TỪ CHỐI)
        r3_set(1.4)
        run("M7 R3 = 1.4 ngoài [0,1]", 2)
        # M8 — R3 là bool ⇒ rc=2 (bool là subclass của int, phải bị loại)
        r3_set("true")
        run("M8 R3 = true (bool)", 2)
        # M9 — R3 là chuỗi ⇒ rc=2
        r3_set('"0.30"')
        run("M9 R3 = chuỗi \"0.30\"", 2)
        # M10 — R3 JSON hỏng ⇒ rc=2, thông điệp có câu của parser
        r3_set(0.30)
        put(R3_REL, "{", "{{", n=1)
        run("M10 R3 JSON hỏng", 2)
        put(R3_REL, "{{", "{", n=1)
        # M11 — R1 mất hằng số ⇒ rc=2
        put(R1_REL, "ETF_PARK = {3:", "ETF_PARK_DISABLED = {3:")
        run("M11 R1 mất ETF_PARK", 2)
        put(R1_REL, "ETF_PARK_DISABLED = {3:", "ETF_PARK = {3:")
        # M12 — R1 hằng số viết xuống dòng + comment: regex trượt, ast thì không
        import re as _re2
        _r1s = open(os.path.join(sand, R1_REL), encoding="utf-8").read()
        _m12 = _re2.search(r"ETF_PARK = \{3:\s*[0-9.]+\}", _r1s)
        assert _m12, "không đọc được literal ETF_PARK hiện tại trong sandbox"
        put(R1_REL, _m12.group(0),
            "ETF_PARK = {\n    3: 0.80,  # xuong dong + comment\n}")
        run("M12 R1 0.80 viết xuống dòng", 1)
        run_total = 15
    print(f"\n{'❌ SELFTEST FAIL: ' + ','.join(fails) if fails else f'✅ SELFTEST: {run_total}/{run_total} mutation đúng kỳ vọng'}")
    return 1 if fails else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--wc-root", default="/home/trido/thanhdt/WorkingClaude")
    ap.add_argument("--mike-root", default=None,
                    help="gốc repo lồng `mike/` chứa bin/compute_park_trim.py (mặc định <wc>/mike); "
                         "trỏ vào worktree để kiểm TRƯỚC khi merge")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest(a.wc_root, a.mike_root))
    print("=== park rail consistency (§28: so GIÁ TRỊ, không so văn xuôi) ===")
    sys.exit(check(a.wc_root, mike=a.mike_root))
