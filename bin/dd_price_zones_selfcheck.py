#!/usr/bin/env python3
"""dd_price_zones_selfcheck.py — mỗi số trong kb/dd_price_zones.json phải khớp NGUYÊN VĂN file nguồn.

Kiểm (không mạng, không BQ/DNSE):
  1. Mỗi evidence.quote là chuỗi con NGUYÊN VĂN của evidence.file (đọc từ MIKE_SRC_ROOT — mặc định
     repo mike canonical, vì thư mục research/ của DD mới có thể chưa commit vào nhánh).
  2. Mỗi field số khai trong evidence.fields xuất hiện như một con số trong quote
     (chấp nhận '47.700', '55,0k', '19,4' (nghìn), '~20k').
  3. Mọi field số khác null (zone_low/center/zone_high/price_ref/center_range) đều được ÍT NHẤT một
     evidence phủ; field null phải có null_reason (trừ price_date).
  4. Bất biến: zone_low ≤ zone_high; center_range[0] == center; append-only key (ticker, dd_date, rev) duy nhất.
  5. center_kind ∈ enum; kind ≠ expected_weighted ⇒ phải có no_expected_reason (luật ưu tiên: giá trị kỳ vọng
     trọng số khi nguồn có); center_alt phải có center_alt_kind + evidence phủ.
  6. Đính chính append-only: rev>1 ⇒ supersedes "TICKER@dd_date#N" trỏ đúng entry rev=N đã có (N=rev−1),
     rev liên tục từ 1; rev≥2 bắt buộc correction_reason.
Dùng: python3 bin/dd_price_zones_selfcheck.py [--ledger PATH]   (rc 0 = PASS)
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_ROOT = os.environ.get("MIKE_SRC_ROOT", "/home/trido/thanhdt/WorkingClaude/mike")
NUM_FIELDS = ("zone_low", "center", "zone_high", "price_ref")
CENTER_KINDS = ("expected_weighted", "base_scenario", "blend", "median", "zone_midpoint", "point")
_TOK = re.compile(r"\d+(?:[.,]\d+)*")


def quote_numbers(q):
    """Tập giá trị (đồng) mà các token số trong quote có thể biểu diễn: 'a.bcd' = nghìn phân cách;
    'a,b' = thập phân. ×1000 (đơn vị k/nghìn) CHỈ cho token có giá trị < 1000 (19,4 / 55,0 / 20 → 19.400…);
    token ≥1000 (vd '9.950', '2026') không bị nhân thành số lớn vô nghĩa."""
    out = set()
    for t in _TOK.findall(q):
        if "." in t and all(len(g) == 3 for g in t.split(".")[1:]) and "," not in t:
            v = float(t.replace(".", ""))
        else:
            v = float(t.replace(".", "").replace(",", ".")) if t.count(",") == 1 else float(t.replace(",", ""))
        out.add(round(v, 3))
        if v < 1000:
            out.add(round(v * 1000, 3))
    return out


def check(ledger_path, src_root=SRC_ROOT):
    errs = []
    d = json.load(open(ledger_path, encoding="utf-8"))
    seen = set()
    cache = {}
    for i, e in enumerate(d["entries"]):
        tag = f"#{i} {e.get('ticker')} {e.get('dd_date')}"
        rev = int(e.get("rev", 1))
        key = (e["ticker"], e["dd_date"], rev)
        if key in seen:
            errs.append(f"{tag}: trùng khoá (ticker, dd_date, rev) — sổ append-only: DD mới khác ngày; đính chính = rev cao hơn")
        errs += _rev_errs(tag, e, rev, d["entries"][:i])
        seen.add(key)
        ck = e.get("center_kind")
        if e.get("center") is not None:
            if ck not in CENTER_KINDS:
                errs.append(f"{tag}: center_kind={ck!r} ngoài enum {CENTER_KINDS}")
            elif ck != "expected_weighted" and not e.get("no_expected_reason") and not any(
                    x.get("supersedes") == f"{e['ticker']}@{e['dd_date']}#{rev}" for x in d["entries"]):
                errs.append(f"{tag}: center_kind={ck} nhưng thiếu no_expected_reason (luật ưu tiên: kỳ vọng trọng số khi nguồn có)")
        elif ck is not None:
            errs.append(f"{tag}: center=null nhưng center_kind={ck!r}")
        if e.get("center_alt") is not None and e.get("center_alt_kind") not in CENTER_KINDS:
            errs.append(f"{tag}: center_alt thiếu/sai center_alt_kind")
        covered = set()
        for ev in e.get("evidence") or []:
            p = os.path.join(src_root, ev["file"])
            if p not in cache:
                try:
                    cache[p] = open(p, encoding="utf-8").read()
                except OSError as x:
                    cache[p] = None
                    errs.append(f"{tag}: không đọc được nguồn {ev['file']}: {x}")
            txt = cache[p]
            if txt is not None and ev["quote"] not in txt:
                errs.append(f"{tag}: trích dẫn KHÔNG có nguyên văn trong {ev['file']}: {ev['quote'][:80]!r}")
            nums = quote_numbers(ev["quote"])
            for fld in ev.get("fields", []):
                vals = e.get(fld)
                vals = vals if isinstance(vals, list) else [vals]
                for v in vals:
                    if v is None or round(float(v), 3) not in nums:
                        errs.append(f"{tag}: {fld}={v} KHÔNG có trong trích dẫn {ev['quote'][:80]!r}")
                covered.add(fld)
        for fld in NUM_FIELDS + ("center_range", "center_alt"):
            if e.get(fld) is not None and fld not in covered:
                errs.append(f"{tag}: {fld}={e[fld]} không có evidence nào phủ")
        for fld in NUM_FIELDS:
            if e.get(fld) is None and not e.get("null_reason"):
                errs.append(f"{tag}: {fld}=null nhưng thiếu null_reason")
        if e.get("zone_low") is not None and e.get("zone_high") is not None and e["zone_low"] > e["zone_high"]:
            errs.append(f"{tag}: zone_low > zone_high")
        cr = e.get("center_range")
        if cr is not None and (len(cr) != 2 or cr[0] != e.get("center") or cr[0] > cr[1]):
            errs.append(f"{tag}: center_range phải [center, hi] tăng dần")
        for fld in ("source_file",):
            if not os.path.exists(os.path.join(src_root, e[fld])):
                errs.append(f"{tag}: source_file không tồn tại {e[fld]}")
    return d, errs


def _rev_errs(tag, e, rev, prior):
    """Luật đính chính append-only (rev/supersedes)."""
    errs = []
    have = {int(x.get("rev", 1)) for x in prior if (x["ticker"], x["dd_date"]) == (e["ticker"], e["dd_date"])}
    if rev == 1:
        if e.get("supersedes"):
            errs.append(f"{tag}: rev=1 không được có supersedes")
        return errs
    want = f"{e['ticker']}@{e['dd_date']}#{rev - 1}"
    if e.get("supersedes") != want:
        errs.append(f"{tag}: rev={rev} cần supersedes={want!r}, có {e.get('supersedes')!r}")
    if (rev - 1) not in have:
        errs.append(f"{tag}: rev={rev} nhưng chưa có rev={rev - 1} đứng trước trong sổ (rev phải liên tục, ghi sau)")
    if not e.get("correction_reason"):
        errs.append(f"{tag}: rev={rev} thiếu correction_reason")
    return errs


def _self_tests():
    """Mutation nhỏ trên chính bộ so số: số sai 1 chữ số phải bị bắt."""
    r = []
    q = "nằm TRONG vùng ≈7.600–13.000 đ, tâm ≈9.950–10.250 đ; FV ≈ 19,4–21,2k; ~20k; **55,0–66,7k**"
    n = quote_numbers(q)
    r.append(("số chuẩn có mặt", all(x in n for x in (7600, 13000, 9950, 10250, 19400, 21200, 20000, 55000, 66700))))
    r.append(("số lệch bị bắt (7.700/9.960/19.500)", not any(x in n for x in (7700, 9960, 19500))))
    # rev / supersedes / enum — mutation nhỏ trên sổ giả
    base = {"ticker": "AAA", "dd_date": "2026-01-01"}
    r1 = dict(base, rev=1)
    r.append(("rev=2 hợp lệ", not _rev_errs("t", dict(base, rev=2, supersedes="AAA@2026-01-01#1", correction_reason="x"), 2, [r1])))
    r.append(("rev=2 thiếu supersedes bị bắt", bool(_rev_errs("t", dict(base, rev=2, correction_reason="x"), 2, [r1]))))
    r.append(("rev=2 supersedes sai bị bắt", bool(_rev_errs("t", dict(base, rev=2, supersedes="AAA@2026-01-01#2", correction_reason="x"), 2, [r1]))))
    r.append(("rev=3 nhảy cóc bị bắt", bool(_rev_errs("t", dict(base, rev=3, supersedes="AAA@2026-01-01#2", correction_reason="x"), 3, [r1]))))
    r.append(("rev=2 thiếu correction_reason bị bắt", bool(_rev_errs("t", dict(base, rev=2, supersedes="AAA@2026-01-01#1"), 2, [r1]))))
    r.append(("quote_numbers: token ≥1000 không bị ×1000", 9950000 not in quote_numbers("tâm 9.950") and 9950 in quote_numbers("tâm 9.950")))
    return r


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default=os.path.join(os.path.dirname(HERE), "kb", "dd_price_zones.json"))
    a = ap.parse_args()
    ok = True
    for name, res in _self_tests():
        print(("PASS " if res else "FAIL ") + name)
        ok &= res
    d, errs = check(a.ledger)
    for x in errs:
        print("FAIL " + x)
    n = len(d["entries"])
    print(f"-- sổ {n} entry / {len({e['ticker'] for e in d['entries']})} mã; lỗi {len(errs)}")
    sys.exit(0 if ok and not errs else 1)
