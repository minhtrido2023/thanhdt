#!/usr/bin/env python3
"""Cổng CƠ HỌC: mọi rail park-fraction phải BẰNG NHAU theo GIÁ TRỊ (§28 coding_guidelines).

VÌ SAO (bài học 2026-08-04, tái diễn 2026-09-27): mức park sống ở BA chỗ độc lập, không chỗ
nào đọc chỗ nào:
  R1 đường MUA      — deploy_golive_dt5g_v4/golive_recommend_v23.py  ETF_PARK = {3: x}
  R2 đường BÁN / L1 — mike/bin/compute_park_trim.py                  PARK_TARGET_F1 = x
  R3 cổng chính sách— data/trading_rules.json  neutral_parking.default_park_of_idle_pct = x
2026-08-04: R1 để 0,70 trong khi R2/R3 lên 0,80 → "mua tới 70% nhưng chỉ trim khi vượt 80%".
2026-09-27: user chốt 0,30, R1+R3 đổi, **R2 vẫn 0,80** (hardcode, KHÔNG đọc trading_rules.json)
→ hệ mua tới 30% nhưng chỉ trim khi vượt 80% ⇒ sổ PARK cũ ~80% KHÔNG BAO GIỜ bị đưa về 30%.
Cả hai lần đều IM LẶNG. Cổng này biến "im lặng" thành exit≠0.

ĐỌC GIÁ TRỊ, KHÔNG ĐỌC VĂN XUÔI: R1/R2 parse bằng `ast` — regex đếm sai khi hằng số viết
xuống dòng hoặc có comment cùng dòng (đúng bài học §16 `tz_anchor_gate.py`).

Dùng: python3 park_rail_consistency_selfcheck.py [--wc-root DIR] [--selftest]
exit 0 = ba rail khớp · 1 = LỆCH · 2 = không đọc được một rail (fail-CLOSED, không đoán).
"""
import argparse
import ast
import json
import os
import sys

TOL = 1e-9


def rail_golive(path):
    """ETF_PARK = {3: x} → x. None nếu không tìm thấy."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "ETF_PARK" for t in node.targets):
            if isinstance(node.value, ast.Dict):
                for k, v in zip(node.value.keys, node.value.values):
                    if isinstance(k, ast.Constant) and k.value == 3:
                        return float(ast.literal_eval(v))
    return None


def rail_named_const(path, name):
    tree = ast.parse(open(path, encoding="utf-8").read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == name for t in node.targets):
            try:
                return float(ast.literal_eval(node.value))
            except (ValueError, TypeError):
                return None
    return None


def rail_rules(path):
    d = json.load(open(path, encoding="utf-8"))
    v = d.get("neutral_parking", {}).get("default_park_of_idle_pct")
    return None if v is None else float(v)


def collect(wc):
    return {
        "R1 MUA  golive_recommend_v23.ETF_PARK[3]":
            rail_golive(os.path.join(wc, "deploy_golive_dt5g_v4", "golive_recommend_v23.py")),
        "R2 BÁN  compute_park_trim.PARK_TARGET_F1":
            rail_named_const(os.path.join(wc, "mike", "bin", "compute_park_trim.py"),
                             "PARK_TARGET_F1"),
        "R3 POLICY trading_rules.default_park_of_idle_pct":
            rail_rules(os.path.join(wc, "data", "trading_rules.json")),
    }


def check(wc, verbose=True):
    rails = collect(wc)
    missing = [k for k, v in rails.items() if v is None]
    if verbose:
        for k, v in rails.items():
            print(f"  {k:52s} = {v}")
    if missing:
        if verbose:
            print("❌ FAIL-CLOSED: không đọc được rail: " + "; ".join(missing))
        return 2
    vals = list(rails.values())
    if max(vals) - min(vals) > TOL:
        if verbose:
            print(f"❌ LỆCH RAIL: {min(vals)} … {max(vals)} — đường MUA và đường BÁN sẽ "
                  f"đánh nhau im lặng (bài học 2026-08-04 / 2026-09-27).")
        return 1
    if verbose:
        print(f"✅ ba rail khớp = {vals[0]}")
    return 0


def selftest(wc):
    """Mutation: cổng phải GIẾT được mỗi kiểu lệch, và phải PASS trên cây đã đồng bộ."""
    import shutil
    import tempfile
    fails = []
    with tempfile.TemporaryDirectory() as td:
        sand = os.path.join(td, "wc")
        for rel in ("deploy_golive_dt5g_v4/golive_recommend_v23.py",
                    "mike/bin/compute_park_trim.py", "data/trading_rules.json"):
            dst = os.path.join(sand, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(os.path.join(wc, rel), dst)

        def setrail(rel, old, new):
            p = os.path.join(sand, rel)
            s = open(p, encoding="utf-8").read()
            assert old in s, f"{rel}: không thấy {old!r}"
            open(p, "w", encoding="utf-8").write(s.replace(old, new, 1))

        # đưa cả 3 về 0.30 = cây ĐÃ đồng bộ ⇒ phải PASS (chứng minh không fail bừa)
        setrail("mike/bin/compute_park_trim.py", "PARK_TARGET_F1 = 0.80",
                "PARK_TARGET_F1 = 0.30")
        rc = check(sand, verbose=False)
        print(f"  M0 ba rail = 0.30          → rc={rc} (kỳ vọng 0)")
        fails += [] if rc == 0 else ["M0"]
        # M1: R2 lệch (ca THẬT 2026-09-27)
        setrail("mike/bin/compute_park_trim.py", "PARK_TARGET_F1 = 0.30",
                "PARK_TARGET_F1 = 0.80")
        rc = check(sand, verbose=False)
        print(f"  M1 R2 0.80 vs R1/R3 0.30   → rc={rc} (kỳ vọng 1)")
        fails += [] if rc == 1 else ["M1"]
        setrail("mike/bin/compute_park_trim.py", "PARK_TARGET_F1 = 0.80",
                "PARK_TARGET_F1 = 0.30")
        # M2: R1 lệch (ca THẬT 2026-08-04)
        setrail("deploy_golive_dt5g_v4/golive_recommend_v23.py", "ETF_PARK = {3: 0.30}",
                "ETF_PARK = {3: 0.7}")
        rc = check(sand, verbose=False)
        print(f"  M2 R1 0.7 vs R2/R3 0.30    → rc={rc} (kỳ vọng 1)")
        fails += [] if rc == 1 else ["M2"]
        setrail("deploy_golive_dt5g_v4/golive_recommend_v23.py", "ETF_PARK = {3: 0.7}",
                "ETF_PARK = {3: 0.30}")
        # M3: R3 lệch
        setrail("data/trading_rules.json", '"default_park_of_idle_pct": 0.3',
                '"default_park_of_idle_pct": 0.8')
        rc = check(sand, verbose=False)
        print(f"  M3 R3 0.8 vs R1/R2 0.30    → rc={rc} (kỳ vọng 1)")
        fails += [] if rc == 1 else ["M3"]
        setrail("data/trading_rules.json", '"default_park_of_idle_pct": 0.8',
                '"default_park_of_idle_pct": 0.3')
        # M4: hằng số viết xuống dòng + comment — regex sẽ trượt, ast thì không
        setrail("mike/bin/compute_park_trim.py", "PARK_TARGET_F1 = 0.30",
                "PARK_TARGET_F1 = (\n    0.80  # xuong dong + comment\n)")
        rc = check(sand, verbose=False)
        print(f"  M4 R2 0.80 viết xuống dòng → rc={rc} (kỳ vọng 1)")
        fails += [] if rc == 1 else ["M4"]
        # M5: rail biến mất ⇒ fail-CLOSED rc=2, KHÔNG âm thầm pass
        setrail("mike/bin/compute_park_trim.py",
                "PARK_TARGET_F1 = (\n    0.80  # xuong dong + comment\n)", "")
        rc = check(sand, verbose=False)
        print(f"  M5 R2 bị xoá               → rc={rc} (kỳ vọng 2)")
        fails += [] if rc == 2 else ["M5"]
    print(f"\n{'❌ SELFTEST FAIL: ' + ','.join(fails) if fails else '✅ SELFTEST: 6/6 mutation đúng kỳ vọng'}")
    return 1 if fails else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--wc-root", default="/home/trido/thanhdt/WorkingClaude")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest(a.wc_root))
    print("=== park rail consistency (§28: so GIÁ TRỊ, không so văn xuôi) ===")
    sys.exit(check(a.wc_root))
