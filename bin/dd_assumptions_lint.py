#!/usr/bin/env python3
"""dd_assumptions_lint.py — kiểm file khoá giả định DD theo kb/schemas/dd_assumptions_v1.json (B4, 22/11/2026).

CHẾ ĐỘ CẢNH BÁO (2 tuần đầu, theo dd-upgrade-final-action-20261122.md B4): mặc định rc=0 và in cảnh báo;
`--strict` ⇒ rc=1 nếu có vi phạm. Từ DD_ASSUMPTIONS_LINT_ENFORCE_FROM trở đi, file có dd_date ≥ mốc đó
bị coi như --strict (Mike đặt mốc sau 2 tuần). CHƯA nối vào dispatch/sổ/skill.

Kiểm:
  S  schema JSON (jsonschema Draft 2020-12).
  L1 tổng trọng số kịch bản = 1.
  L2 Σp(down) ≠ Σp(up) ⇒ bắt buộc scenarios.asymmetry_reason (không ép 25/50/25).
  L3 (từ M20261103B) r khớp r_neo + β_MẶC_ĐỊNH×(lãi huy động − lãi neo) (hằng đọc kb/config/dd_ke_bands.json);
     lệch > tolerance (5bp — tham số TỰ ĐẶT của B4, KHÔNG có trong SKILL) hoặc β khác mặc định ⇒
     bắt buộc discount_rate.override_reason.
  L4 (từ M20261103B) độ nhạy phải gồm ±50/±100bp lãi huy động.
  L5 từ mốc M20261122 (D4): band_ends_reported = true.
  L6 từ mốc M20261122 (D4): moat NARROW/NONE ⇒ terminal_ronic EQUALS_KE hoặc NOT_APPLICABLE_FINITE_LIFE.
     (Schema đã chặn ca này; L6 giữ làm dự phòng khi thiếu jsonschema.)
  L7 (từ M20261122, D3) dự án mandatory ∧ ¬generates_revenue, hoặc classification=compliance ⇒ treatment=CASH_OUTFLOW (D3).
     classification=compliance ⇔ mandatory ∧ ¬generates_revenue (lệch ⇒ lỗi); growth ⇒ generates_revenue; cam kết
     vốn 12T có mà projects rỗng ⇒ lỗi (đối chiếu chéo).
     Dự án growth lệch NPV0_BOOK ⇒ bắt buộc independent_basis (luật 03/11 17:06).
  L8 method_version khớp bảng kb/config/dd_method_versions.json theo dd_date.
  L9 KHÔNG có dữ liệu thị trường trong file khoá mù giá: tên khoá (adv*, pe, pb, market_price, close,
     volume, ...) và chuỗi giá trị ("ADV", "P/E 6,2", "giá thị trường").
  L10 audit_opinion.fy < năm dd_date − 1 ⇒ phải ghi audited_fy_missing.
  L11 quá N trường khong_cong_bo (config max_khong_cong_bo) ⇒ cảnh báo file rỗng-ruột.
  L12 scenarios phải có đủ down/base/up (≥3 mục).
  L13 có tỉ lệ trích quỹ KT-PL > 0 ⇒ applied_to_cashflow=true.
  L14 deposit_rate_date phải nằm trong N ngày TRƯỚC dd_date (config deposit_rate_max_age_days).
  F  dd_date sai định dạng YYYY-MM-DD ⇒ cảnh báo, KHÔNG bao giờ tự lật sang chặn.
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
D3_MILESTONE = "M20261122"
D2_MILESTONE = "M20261103A"   # luật 03/11 17:06 (dự án: base NPV=0)
D_KE_MILESTONE = "M20261103B"  # luật 03/11 22:27 (r neo lãi huy động)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

MARKET_KEY_RE = re.compile(
    r"^(adv\d*(_.*)?|.*_adv\d*(_.*)?|pe(_.*)?|pb(_.*)?|ps|pcf|.*_pe|.*_pb|price|price_(ref|close|market|open|high|low).*|(market|close|stock|share|ref)_price|"
    r"market_?cap|mcap|close|close_price|volume|volume_.*|khoi_luong.*|trading_value.*|gia_thi_truong|thi_gia)$", re.I)
# chữ ADV/PE chỉ bắt khi đi kèm SỐ + đơn vị (mô tả phương pháp "ADV trung vị 60 phiên… sau khoá" KHÔNG bị bắt)
_UNIT = r"(tỷ|ty|triệu|tr\b|nghìn|cp\b|đ/cp|đồng|vnd)"
MARKET_TEXT_RE = re.compile(
    r"(\bADV\b\s*[=:]\s*\d|\bADV\b[^.;\n]{0,40}?\d[\d.,]*\s*" + _UNIT +
    r"|\bP/?E\s*[=:(]?\s*\d|\bP/?B\s*[=:(]?\s*\d|giá thị trường\s*[=:]?\s*\d|thị giá\s*[=:]?\s*\d)",
    re.I)


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def schema_errors(doc, schema):
    try:
        import jsonschema
    except ImportError:
        return ["S: MẤT KIỂM SCHEMA — thiếu module jsonschema (wc_venv không có; chạy bằng /usr/bin/python3). Kết quả lint KHÔNG đầy đủ"]
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
    # Ngày có mốc: CHỈ chấp nhận các mốc của chính ngày đó (không cho khai mốc trước đó để né luật mới trong ngày).
    if same_day:
        return set(same_day)
    return {before[-1]} if before else set()


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


def _days(a, b):
    """số ngày a − b (YYYY-MM-DD); None nếu sai định dạng. Không dùng giờ hệ thống."""
    from datetime import date
    try:
        return (date.fromisoformat(a) - date.fromisoformat(b)).days
    except (ValueError, TypeError):
        return None


def _is_kcb(x):
    return isinstance(x, dict) and x.get("value") == "khong_cong_bo"


def cross_rules(doc, bands, methods):
    v, notes = [], []
    dd_raw = doc.get("dd_date")
    dd_ok = isinstance(dd_raw, str) and bool(DATE_RE.match(dd_raw)) and _days(dd_raw, dd_raw) is not None
    dd_date = dd_raw if dd_ok else ""
    if not dd_ok:
        v.append(f"F: dd_date {dd_raw!r} sai định dạng YYYY-MM-DD (không so được mốc; không tự coi là ≥ mốc chặn)")
    mv = doc.get("method_version")
    mv_ok = isinstance(mv, str) and bool(re.match(r"^M\d{8}[A-Z]?$", mv))
    # method_version thiếu/sai định dạng ⇒ coi như mốc MỚI NHẤT (không né luật bằng cách bỏ trống); S/L8 vẫn báo riêng.
    ke_on = (not mv_ok) or mv >= D_KE_MILESTONE
    d2_on = (not mv_ok) or mv >= D2_MILESTONE
    d3_on = (not mv_ok) or mv >= D3_MILESTONE
    d4_on = (not mv_ok) or mv >= D4_MILESTONE

    sc_blk = doc.get("scenarios") or {}
    sc = sc_blk.get("items") or []
    if sc:
        tot = sum(float(s.get("p", 0) or 0) for s in sc)
        if abs(tot - 1.0) > 1e-6:
            v.append(f"L1: tổng trọng số kịch bản = {tot:.4f} ≠ 1")
        down = sum(float(s.get("p", 0) or 0) for s in sc if s.get("side") == "down")
        up = sum(float(s.get("p", 0) or 0) for s in sc if s.get("side") == "up")
        if abs(down - up) > 1e-6 and not (sc_blk.get("asymmetry_reason") or "").strip():
            v.append(f"L2: trọng số lệch (down {down:.2f} ≠ up {up:.2f}) mà thiếu scenarios.asymmetry_reason")
        sides = {s.get("side") for s in sc}
        if not {"down", "base", "up"} <= sides:
            v.append(f"L12: kịch bản phải đủ down/base/up (SKILL), đang {len(sc)} mục, phía {sorted(x for x in sides if x)}")

    dr = doc.get("discount_rate") or {}
    anc = bands["anchor"]
    if ke_on and all(isinstance(dr.get(k), (int, float)) for k in ("r", "deposit_rate_now")):
        beta_def = bands["beta_passthrough_default"]
        beta = dr.get("beta_passthrough", beta_def)
        r_exp = anc["r"] + beta_def * (dr["deposit_rate_now"] - anc["deposit_rate_12m_effective"])  # β MẶC ĐỊNH
        gap_bp = abs(dr["r"] - r_exp) * 1e4
        has_ov = bool((dr.get("override_reason") or "").strip())
        if gap_bp > bands["r_tolerance_bp"] and not has_ov:
            v.append(f"L3: r={dr['r']:.4f} lệch công thức neo {r_exp:.4f} "
                     f"({anc['r']}+{beta_def}×({dr['deposit_rate_now']}−{anc['deposit_rate_12m_effective']})) "
                     f"{gap_bp:.0f}bp > {bands['r_tolerance_bp']}bp (tham số tự đặt của B4) mà thiếu override_reason")
        if isinstance(beta, (int, float)) and abs(beta - beta_def) > 1e-9 and not has_ov:
            v.append(f"L3: beta_passthrough={beta} khác mặc định {beta_def} mà thiếu override_reason")
    if ke_on and dr:
        missing = [b for b in bands["required_sensitivity_bp"] if b not in (dr.get("sensitivity_bp") or [])]
        if missing:
            v.append(f"L4: thiếu độ nhạy lãi huy động {missing}bp")
    if dr and dd_ok and isinstance(dr.get("deposit_rate_date"), str):
        age = _days(dd_date, dr["deposit_rate_date"])
        mx = bands.get("deposit_rate_max_age_days", 14)
        if age is None:
            v.append(f"L14: deposit_rate_date {dr['deposit_rate_date']!r} sai định dạng")
        elif age < 0 or age > mx:
            v.append(f"L14: deposit_rate_date {dr['deposit_rate_date']} cách dd_date {dd_date} {age} ngày (phải 0–{mx} ngày trước)")

    if d4_on and dr and dr.get("band_ends_reported") is not True:
        v.append(f"L5: method_version {mv} ≥ {D4_MILESTONE} (D4) ⇒ phải báo hai đầu dải Ke "
                 f"{bands['ke_band_low']}–{bands['ke_band_high']} (band_ends_reported=true)")

    term = doc.get("terminal") or {}
    if d4_on and term.get("moat_tier") in ("NARROW", "NONE") and term.get("terminal_ronic") not in (
            "EQUALS_KE", "NOT_APPLICABLE_FINITE_LIFE", None):
        v.append(f"L6: moat {term['moat_tier']} ⇒ terminal_ronic phải EQUALS_KE (D4), đang {term.get('terminal_ronic')}")

    items = (doc.get("projects") or {}).get("items") or []
    for i, p in enumerate(items):
        name = p.get("name", f"#{i}")
        if d3_on:
            comp = p.get("classification") == "compliance"
            must_out = p.get("mandatory") is True and p.get("generates_revenue") is False
            if comp != must_out and p.get("classification") in ("compliance", "growth", "maintenance"):
                v.append(f"L7: dự án '{name}' không nhất quán: classification=compliance ⇔ mandatory ∧ ¬generates_revenue "
                         f"(đang classification={p.get('classification')}, mandatory={p.get('mandatory')}, "
                         f"generates_revenue={p.get('generates_revenue')})")
            if p.get("classification") == "growth" and p.get("generates_revenue") is False:
                v.append(f"L7: dự án growth '{name}' mà generates_revenue=false — growth phải tạo doanh thu")
            if (comp or must_out) and p.get("treatment") != "CASH_OUTFLOW":
                amt = _num(p.get("total_bn"))
                v.append(f"L7: dự án '{name}'{f' ({amt:,.0f} tỷ)' if amt else ''} là chi tuân thủ/bắt buộc không tạo "
                         f"doanh thu ⇒ treatment phải CASH_OUTFLOW (D3), đang {p.get('treatment')}")
        if (d2_on and p.get("classification") == "growth" and p.get("treatment") not in ("NPV0_BOOK", None)
                and not (p.get("independent_basis") or "").strip()):
            v.append(f"L7: dự án growth '{name}' lệch NPV=0 ({p.get('treatment')}) mà thiếu independent_basis (luật 03/11 17:06)")
    if d3_on and not items:
        cc = (doc.get("capital_commitments_12m") or {}).get("items") or []
        if cc:
            tot = sum(float(c.get("amount_bn") or 0) for c in cc)
            v.append(f"L7: capital_commitments_12m có {len(cc)} cam kết ({tot:,.0f} tỷ) mà projects.items rỗng "
                     f"(none_reason={((doc.get('projects') or {}).get('none_reason') or '')[:40]!r}) ⇒ đối chiếu chéo thất bại")

    if dd_ok and mv_ok:
        ok = expected_method_versions(dd_date, methods)
        if mv not in ok:
            v.append(f"L8: method_version {mv} không khớp bảng mốc cho dd_date {dd_date} (hợp lệ: {sorted(ok)})")

    n_kcb = 0
    for path, k, val in _walk(doc):
        if _is_kcb(val):
            n_kcb += 1
        if MARKET_KEY_RE.match(str(k)):
            v.append(f"L9: khoá dữ liệu thị trường trong file mù giá: {path}")
        elif isinstance(val, str) and MARKET_TEXT_RE.search(val):
            m = MARKET_TEXT_RE.search(val)
            v.append(f"L9: chuỗi chứa dữ liệu thị trường '{m.group(0)}' tại {path}: …{val[max(0, m.start()-30):m.end()+40]}…")
    mx_kcb = bands.get("max_khong_cong_bo", 3)
    if n_kcb > mx_kcb:
        v.append(f"L11: {n_kcb} trường khong_cong_bo > {mx_kcb} ⇒ file rỗng-ruột, phải tìm thêm nguồn hoặc giải trình")

    wf = doc.get("welfare_fund") or {}
    pct = _num(wf.get("annual_appropriation_pct_of_npat"))
    if pct and pct > 0 and wf.get("applied_to_cashflow") is not True:
        v.append(f"L13: có tỉ lệ trích quỹ KT-PL {pct:.3f} nhưng applied_to_cashflow≠true (phải trừ khỏi dòng tiền cổ đông)")

    ao = doc.get("audit_opinion") or {}
    if dd_ok and ao.get("status") != "audited_fy_missing" and isinstance(ao.get("fy"), int):
        yr = int(dd_date[:4])
        dl = bands.get("audited_fy_deadline_mmdd", "03-31")
        need = yr - 1 if dd_date[5:] > dl else yr - 2  # trước hạn công bố BCTC kiểm toán năm ⇒ chưa đòi FY vừa qua
        if ao["fy"] < need:
            v.append(f"L10: BCTC kiểm toán gần nhất FY{ao['fy']} < FY{need} (hạn công bố {dl}) ⇒ ghi status audited_fy_missing (D5)")
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


def _ensure_jsonschema():
    try:
        import jsonschema  # noqa: F401
    except ImportError:
        alt = "/usr/bin/python3"
        if os.path.exists(alt) and not os.environ.get("DD_LINT_REEXEC") and os.path.realpath(sys.executable) != os.path.realpath(alt):
            os.environ["DD_LINT_REEXEC"] = "1"
            os.execv(alt, [alt] + sys.argv)
        print("dd_assumptions_lint: CẢNH BÁO MẤT KIỂM SCHEMA (không có jsonschema) — chạy bằng /usr/bin/python3", file=sys.stderr)


def main(argv=None):
    _ensure_jsonschema()
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
    dd = doc.get("dd_date")
    # chặn theo mốc CHỈ khi dd_date đúng định dạng (chuỗi lạ như "TBD" so sánh chữ cái sẽ tự lật sang strict)
    enforce = a.strict or (isinstance(dd, str) and bool(DATE_RE.match(dd)) and dd >= DD_ASSUMPTIONS_LINT_ENFORCE_FROM)
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
