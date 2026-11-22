#!/usr/bin/env python3
"""dd_assumptions_lint.py — kiểm file khoá giả định DD theo kb/schemas/dd_assumptions_v1.json (B4, 22/11/2026).

CHẾ ĐỘ CẢNH BÁO (2 tuần đầu, theo dd-upgrade-final-action-20261122.md B4): mặc định rc=0 và in cảnh báo;
`--strict` ⇒ rc=1 nếu có vi phạm. Từ DD_ASSUMPTIONS_LINT_ENFORCE_FROM trở đi, file có dd_date ≥ mốc đó
bị coi như --strict (Mike đặt mốc sau 2 tuần). CHƯA nối vào dispatch/sổ/skill.

Kiểm:
  S  schema JSON (jsonschema Draft 2020-12).
  L1 tổng trọng số kịch bản = 1.
  L2 Σp(down) ≠ Σp(up) ⇒ bắt buộc scenarios.asymmetry_reason (không ép 25/50/25).
  L3 r khớp r_neo + β×(lãi huy động − lãi neo) (hằng đọc kb/config/dd_ke_bands.json), lệch > tolerance ⇒
     bắt buộc discount_rate.override_reason.
  L4 độ nhạy phải gồm ±50/±100bp lãi huy động.
  L5 từ mốc M20261122 (D4): band_ends_reported = true.
  L6 từ mốc M20261122 (D4): moat NARROW/NONE ⇒ terminal_ronic EQUALS_KE hoặc NOT_APPLICABLE_FINITE_LIFE.
  L7 dự án mandatory ∧ ¬generates_revenue, hoặc classification=compliance ⇒ treatment=CASH_OUTFLOW (D3).
     Dự án growth lệch NPV0_BOOK ⇒ bắt buộc independent_basis (luật 03/11 17:06).
  L8 method_version khớp bảng kb/config/dd_method_versions.json theo dd_date.
  L9 KHÔNG có dữ liệu thị trường trong file khoá mù giá: tên khoá (adv*, pe, pb, market_price, close,
     volume, ...) và chuỗi giá trị ("ADV", "P/E 6,2", "giá thị trường").
  L10 audit_opinion.fy < năm dd_date − 1 ⇒ phải ghi audited_fy_missing.
  N  (ghi chú, không tính vi phạm) audited_fy_missing ⇒ không vào Bậc 1, cổng LAG coi như chưa có DD (D5).

Dùng: python3 bin/dd_assumptions_lint.py <file.json> [--strict] [--json]
"""
import argparse
import json
import os
import re
import sys

DD_ASSUMPTIONS_LINT_ENFORCE_FROM = "9999-12-31"  # Mike đặt sau 2 tuần cảnh báo (bật chặn nếu báo giả ≤10%)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "kb", "schemas", "dd_assumptions_v1.json")
KE_BANDS = os.path.join(ROOT, "kb", "config", "dd_ke_bands.json")
METHODS = os.path.join(ROOT, "kb", "config", "dd_method_versions.json")
D4_MILESTONE = "M20261122"

MARKET_KEY_RE = re.compile(
    r"^(adv(_.*)?|.*_adv(_.*)?|pe|pb|ps|pcf|pe_ratio|pb_ratio|pe_ttm|market_price|price_ref|price_close|"
    r"close|close_price|market_cap|mcap|volume|volume_.*|trading_value.*|gia_thi_truong|thi_gia)$", re.I)
MARKET_TEXT_RE = re.compile(
    r"(\bADV\b|\bP/?E\s*[=:(]?\s*\d|\bP/?B\s*[=:(]?\s*\d|giá thị trường|gia thi truong|thị giá|thi gia|market price)",
    re.I)


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def schema_errors(doc, schema):
    try:
        import jsonschema
    except ImportError:
        return ["S: thiếu module jsonschema (chạy bằng /usr/bin/python3) — bỏ qua kiểm schema"]
    v = jsonschema.Draft202012Validator(schema)
    out = []
    for e in sorted(v.iter_errors(doc), key=lambda e: list(e.absolute_path)):
        path = "/".join(str(p) for p in e.absolute_path) or "(gốc)"
        out.append(f"S: {path}: {e.message[:220]}")
    return out


def expected_method_versions(dd_date, methods):
    ms = sorted(methods["milestones"], key=lambda m: (m["date"], m.get("time_ict") or ""))
    before = [m["id"] for m in ms if m["date"] < dd_date]
    same_day = [m["id"] for m in ms if m["date"] == dd_date]
    ok = set(same_day)
    if before:
        ok.add(before[-1])
    return ok


def _walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield path + "/" + str(k), k, v
            yield from _walk(v, path + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _walk(v, f"{path}[{i}]")


def _num(x):
    """num_or_kcb → float hoặc None (khong_cong_bo/thiếu)."""
    if isinstance(x, bool):
        return None
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, dict) and isinstance(x.get("value"), (int, float)):
        return float(x["value"])
    return None


def cross_rules(doc, bands, methods):
    v, notes = [], []
    dd_date = str(doc.get("dd_date", ""))

    sc = (doc.get("scenarios") or {}).get("items") or []
    if sc:
        tot = sum(float(s.get("p", 0) or 0) for s in sc)
        if abs(tot - 1.0) > 1e-6:
            v.append(f"L1: tổng trọng số kịch bản = {tot:.4f} ≠ 1")
        down = sum(float(s.get("p", 0) or 0) for s in sc if s.get("side") == "down")
        up = sum(float(s.get("p", 0) or 0) for s in sc if s.get("side") == "up")
        if abs(down - up) > 1e-6 and not (doc["scenarios"].get("asymmetry_reason") or "").strip():
            v.append(f"L2: trọng số lệch (down {down:.2f} ≠ up {up:.2f}) mà thiếu scenarios.asymmetry_reason")

    dr = doc.get("discount_rate") or {}
    anc = bands["anchor"]
    if all(isinstance(dr.get(k), (int, float)) for k in ("r", "deposit_rate_now")):
        beta = dr.get("beta_passthrough", bands["beta_passthrough_default"])
        r_exp = anc["r"] + beta * (dr["deposit_rate_now"] - anc["deposit_rate_12m_effective"])
        gap_bp = abs(dr["r"] - r_exp) * 1e4
        if gap_bp > bands["r_tolerance_bp"] and not (dr.get("override_reason") or "").strip():
            v.append(f"L3: r={dr['r']:.4f} lệch công thức neo {r_exp:.4f} "
                     f"({anc['r']}+{beta}×({dr['deposit_rate_now']}−{anc['deposit_rate_12m_effective']})) "
                     f"{gap_bp:.0f}bp > {bands['r_tolerance_bp']}bp mà thiếu override_reason")
    if dr:
        missing = [b for b in bands["required_sensitivity_bp"] if b not in (dr.get("sensitivity_bp") or [])]
        if missing:
            v.append(f"L4: thiếu độ nhạy lãi huy động {missing}bp")

    mv = doc.get("method_version")
    d4_on = isinstance(mv, str) and mv >= D4_MILESTONE
    if d4_on and dr and dr.get("band_ends_reported") is not True:
        v.append(f"L5: method_version {mv} ≥ {D4_MILESTONE} (D4) ⇒ phải báo hai đầu dải Ke "
                 f"{bands['ke_band_low']}–{bands['ke_band_high']} (band_ends_reported=true)")

    term = doc.get("terminal") or {}
    if d4_on and term.get("moat_tier") in ("NARROW", "NONE") and term.get("terminal_ronic") not in (
            "EQUALS_KE", "NOT_APPLICABLE_FINITE_LIFE", None):
        v.append(f"L6: moat {term['moat_tier']} ⇒ terminal_ronic phải EQUALS_KE (D4), đang {term.get('terminal_ronic')}")

    for i, p in enumerate((doc.get("projects") or {}).get("items") or []):
        name = p.get("name", f"#{i}")
        must_out = p.get("classification") == "compliance" or (
            p.get("mandatory") is True and p.get("generates_revenue") is False)
        if must_out and p.get("treatment") != "CASH_OUTFLOW":
            amt = _num(p.get("total_bn"))
            v.append(f"L7: dự án '{name}'{f' ({amt:,.0f} tỷ)' if amt else ''} là chi tuân thủ/bắt buộc không tạo "
                     f"doanh thu ⇒ treatment phải CASH_OUTFLOW (D3), đang {p.get('treatment')}")
        if (p.get("classification") == "growth" and p.get("treatment") not in ("NPV0_BOOK", None)
                and not (p.get("independent_basis") or "").strip()):
            v.append(f"L7: dự án growth '{name}' lệch NPV=0 ({p.get('treatment')}) mà thiếu independent_basis (luật 03/11 17:06)")

    if dd_date and mv:
        ok = expected_method_versions(dd_date, methods)
        if mv not in ok:
            v.append(f"L8: method_version {mv} không khớp bảng mốc cho dd_date {dd_date} (hợp lệ: {sorted(ok)})")

    for path, k, val in _walk(doc):
        if MARKET_KEY_RE.match(str(k)):
            v.append(f"L9: khoá dữ liệu thị trường trong file mù giá: {path}")
        elif isinstance(val, str) and MARKET_TEXT_RE.search(val):
            m = MARKET_TEXT_RE.search(val)
            v.append(f"L9: chuỗi chứa dữ liệu thị trường '{m.group(0)}' tại {path}: …{val[max(0, m.start()-30):m.end()+40]}…")

    ao = doc.get("audit_opinion") or {}
    if dd_date[:4].isdigit() and ao.get("status") != "audited_fy_missing" and isinstance(ao.get("fy"), int):
        if ao["fy"] < int(dd_date[:4]) - 1:
            v.append(f"L10: BCTC kiểm toán gần nhất FY{ao['fy']} < FY{int(dd_date[:4]) - 1} ⇒ ghi status audited_fy_missing (D5)")
    if ao.get("status") == "audited_fy_missing":
        notes.append("N: audited_fy_missing ⇒ không vào Bậc 1; cổng LAG coi như CHƯA có DD (D5)")
    return v, notes


def lint(path):
    doc = _load(path)
    if not isinstance(doc, dict):
        return ["S: gốc không phải object"], [], {}
    v = schema_errors(doc, _load(SCHEMA))
    cv, notes = cross_rules(doc, _load(KE_BANDS), _load(METHODS))
    return v + cv, notes, doc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file")
    ap.add_argument("--strict", action="store_true", help="rc=1 nếu có vi phạm")
    ap.add_argument("--json", action="store_true", help="in kết quả dạng JSON")
    a = ap.parse_args(argv)
    try:
        viol, notes, doc = lint(a.file)
    except (OSError, json.JSONDecodeError) as e:
        print(f"dd_assumptions_lint: không đọc được {a.file}: {e}", file=sys.stderr)
        return 2
    enforce = a.strict or str(doc.get("dd_date", "")) >= DD_ASSUMPTIONS_LINT_ENFORCE_FROM
    if a.json:
        print(json.dumps({"file": a.file, "violations": viol, "notes": notes,
                          "mode": "strict" if enforce else "warn"}, ensure_ascii=False, indent=1))
    else:
        tag = "LỖI" if enforce else "CẢNH BÁO"
        for x in viol:
            print(f"[{tag}] {x}")
        for x in notes:
            print(f"[GHI CHÚ] {x}")
        print(f"dd_assumptions_lint: {a.file}: {len(viol)} vi phạm · chế độ {'strict' if enforce else 'cảnh báo (rc=0)'}")
    return 1 if (enforce and viol) else 0


if __name__ == "__main__":
    sys.exit(main())
