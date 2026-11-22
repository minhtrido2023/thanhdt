#!/usr/bin/env python3
"""dd_ledger_backfill_skeptic_final.py — backfill CHỈ-THÊM-TRƯỜNG vào kb/dd_price_zones.json (A2, 22/11/2026).

Thêm cho MỌI entry: skeptic_final (CONFIRMED|FIXED_UNVERIFIED|REFUTED_OPEN|NONE), skeptic_final_basis,
skeptic_verdict_path (đường dẫn file verdict thật hoặc null), audited_fy_missing (bool).
Không sửa trường cũ: chèn nguyên dòng ngay sau dòng "ticker" của mỗi entry ⇒ git diff chỉ là dòng thêm.
Idempotent: entry đã có skeptic_final thì bỏ qua. Luật đọc `skeptic_status` (xem classify()).
Ca mơ hồ ⇒ FIXED_UNVERIFIED + basis "ambiguous_backfill" (KHÔNG BAO GIỜ tự gán CONFIRMED).
Dùng: python3 bin/dd_ledger_backfill_skeptic_final.py [--ledger PATH] [--write]   (mặc định chỉ in báo cáo)
"""
import argparse
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_ROOT = os.environ.get("MIKE_SRC_ROOT", "/home/trido/thanhdt/WorkingClaude/mike")
BASIS_RULE = "rule_backfill_20261122"
BASIS_AMBIG = "ambiguous_backfill"
RE_REF = re.compile(r"REFUTED|INCONCLUSIVE")
RE_NONE = re.compile(r"CHƯA qua skeptic|CHƯA chạy fundamental-skeptic|CHƯA chạy skeptic")
RE_APPLIED = re.compile(r"đã áp|đã sửa|đính chính|Taylor áp|áp (?:đủ|toàn bộ|errata)|SKEPTIC\w*|đã xử|áp r\d|áp \d+ mục|từ skeptic|Taylor sửa")
RE_FINAL = re.compile(r"lần cuối CONFIRMED")
# thiếu BCTC năm GẦN NHẤT đã kiểm toán (tra trên skeptic_status/notes/correction_reason)
RE_FY_MISSING = re.compile(r"thiếu BCTC 20\d\d (?:kiểm toán|KT)", re.I)


def classify(e):
    """→ (skeptic_final, ambiguous: bool). Chỉ đọc skeptic_status (notes/correction_reason chỉ mô tả các
    vòng ĐÍNH CHÍNH trước verdict nên không dùng để suy nhãn)."""
    s = e.get("skeptic_status") or ""
    has_c = "CONFIRMED" in re.sub(r"(?:chưa|KHÔNG|không)\s+(?:\w+\s+){0,2}CONFIRMED", "", s)  # "chưa CONFIRMED" ≠ CONFIRMED
    has_r = bool(RE_REF.search(s))
    applied, none_m = bool(RE_APPLIED.search(s)), bool(RE_NONE.search(s))
    if RE_FINAL.search(s) and not has_r:
        return "CONFIRMED", False
    if not has_c and not has_r:
        if none_m and not applied:
            return "NONE", False
        if applied:  # có nhắc skeptic + đính chính nhưng không chữ verdict (vd SKEPTIC_R3 → r4, chưa chạy lại)
            return "FIXED_UNVERIFIED", "xác nhận" in s  # "skeptic cuối … xác nhận" không có chữ CONFIRMED ⇒ mơ hồ
        return "FIXED_UNVERIFIED", True  # không match luật nào
    if has_c and has_r:
        return "FIXED_UNVERIFIED", True  # verdict lẫn lộn (vòng sau CONFIRMED trên bản đã sửa? hay hai chiều?)
    if has_c:
        if none_m or applied:  # CONFIRMED nhưng kèm đính chính/chưa-chạy-lại ⇒ không chắc đính chính có chạm số/vùng
            return "FIXED_UNVERIFIED", True
        return "CONFIRMED", False
    # chỉ REFUTED/INCONCLUSIVE
    return ("FIXED_UNVERIFIED", False) if applied else ("REFUTED_OPEN", False)


def audited_fy_missing(e):
    return any(RE_FY_MISSING.search(e.get(k) or "") for k in ("skeptic_status", "notes", "correction_reason"))


def verdict_path(e, final, root=SRC_ROOT):
    """File SKEPTIC*/verdict thật trong thư mục nguồn của entry (dd_*/ hoặc dd_redo_*/<MÃ>/); null nếu NONE/không có.
    Nhiều ứng viên ⇒ chọn tên lớn nhất theo thứ tự tự nhiên (R4 > R3) và báo ra danh sách ứng viên."""
    if final == "NONE":
        return None, []
    parts = e["source_file"].split("/")
    if "research" not in parts:
        return None, []
    i = parts.index("research")
    sub = parts[i + 1:i + 3] if len(parts) - i - 1 >= 3 and parts[i + 1].startswith(("dd_redo_", "dd_lagcand_")) else parts[i + 1:i + 2]
    base = "/".join(parts[:i + 1] + sub)
    cands = []
    for dp, _dn, fn in os.walk(os.path.join(root, base)):
        for f in fn:
            low = f.lower()
            if low.endswith(".md") and ("skeptic" in low or "verdict" in low) and e["ticker"].lower() in os.path.join(dp, f).lower():
                cands.append(os.path.relpath(os.path.join(dp, f), root))
    nat = lambda p: [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", p)]  # noqa: E731
    cands.sort(key=nat)
    return (cands[-1] if cands else None), cands


def fields_for(e, root=SRC_ROOT):
    final, amb = classify(e)
    vp, cands = verdict_path(e, final, root)
    return {"skeptic_final": final, "skeptic_final_basis": BASIS_AMBIG if amb else BASIS_RULE,
            "skeptic_verdict_path": vp, "audited_fy_missing": audited_fy_missing(e)}, cands


def backfill_text(raw, d, root=SRC_ROOT):
    """Chèn trường mới sau dòng '"ticker": ...' của từng entry chưa có skeptic_final. Trả (text mới, info)."""
    lines, out, info, k = raw.split("\n"), [], [], 0
    in_entries = False
    for ln in lines:
        out.append(ln)
        if ln.startswith(' "entries"'):
            in_entries = True
        if in_entries and ln.startswith('   "ticker": '):
            e = d["entries"][k]
            k += 1
            if "skeptic_final" in e:
                continue
            f, cands = fields_for(e, root)
            for key, v in f.items():
                out.append(f'   "{key}": {json.dumps(v, ensure_ascii=False)},')
            info.append((e, f, cands))
    assert k == len(d["entries"]), f"đếm entry lệch {k} ≠ {len(d['entries'])}"
    return "\n".join(out), info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default=os.path.join(os.path.dirname(HERE), "kb", "dd_price_zones.json"))
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    raw = open(a.ledger, encoding="utf-8").read()
    d = json.loads(raw)
    new, info = backfill_text(raw, d)
    nd = json.loads(new)
    for o, n in zip(d["entries"], nd["entries"]):  # bất biến: trường cũ không đổi
        assert all(n[k] == v for k, v in o.items()), "trường cũ bị đổi"
    # xếp hạng: rev cuối mỗi mã theo (dd_date, rev) — luật sổ: bản cao nhất thắng
    last = {}
    for e in nd["entries"]:
        key = (e["dd_date"], int(e.get("rev", 1)))
        if e["ticker"] not in last or key > last[e["ticker"]][0]:
            last[e["ticker"]] = (key, e)
    from collections import Counter
    cnt = Counter(e["skeptic_final"] for _k, e in last.values())
    print(f"entry đã thêm trường: {len(info)} / {len(d['entries'])}")
    print("rev-cuối-mỗi-mã:", {k: cnt.get(k, 0) for k in ("CONFIRMED", "FIXED_UNVERIFIED", "REFUTED_OPEN", "NONE")}, "tổng", sum(cnt.values()))
    for i, e in enumerate(nd["entries"]):
        if e["skeptic_final_basis"] == BASIS_AMBIG:
            print(f"AMBIG #{i} {e['ticker']}@{e['dd_date']}#{e.get('rev', 1)} → {e['skeptic_final']}: {e['skeptic_status']}")
    if a.write and info:
        tmp = a.ledger + ".tmp"
        open(tmp, "w", encoding="utf-8").write(new)
        os.replace(tmp, a.ledger)
        print("ĐÃ GHI", a.ledger)


if __name__ == "__main__":
    main()
