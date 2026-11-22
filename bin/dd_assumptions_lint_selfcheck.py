#!/usr/bin/env python3
"""dd_assumptions_lint_selfcheck.py — fixture ĐÚNG phải 0 vi phạm; mỗi mutation phải bắn ĐÚNG mã luật.

Không mạng, không BQ, không đọc giờ hệ thống (lint không phụ thuộc TZ — chạy dưới `env -u TZ` và
`TZ=Pacific/Kiritimati` để chứng minh). Dùng: python3 bin/dd_assumptions_lint_selfcheck.py (rc 0 = PASS)
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dd_assumptions_lint as L  # noqa: E402

SRC = "src/BCTC_Q3_2026.pdf p2"


def good():
    return {
        "schema_version": "dd_assumptions_v1", "ticker": "ABC", "dd_date": "2026-11-23", "rev": 1,
        "loai_hinh": "san_xuat_khac", "method_version": "M20261122",
        "share_base": {"shares_m": 100.0, "source": SRC, "as_of_date": "2026-09-30",
                       "bonus_esop": {"status": "none", "source": "NQ ĐHĐCĐ 2026 p3"}},
        "projects": {"items": [
            {"name": "Nhà máy mới", "total_bn": 500, "spent_bn": 200, "remaining_bn": 300,
             "generates_revenue": True, "mandatory": False, "classification": "growth",
             "treatment": "NPV0_BOOK", "source": "NQ HĐQT 05/2026"},
            {"name": "Xử lý khí thải", "total_bn": 300, "spent_bn": 0, "remaining_bn": 300,
             "generates_revenue": False, "mandatory": True, "classification": "compliance",
             "treatment": "CASH_OUTFLOW", "source": "QĐ 917"}]},
        "welfare_fund": {"balance_deducted": 50.0, "annual_appropriation_pct_of_npat": 0.055,
                         "applied_to_cashflow": True, "source": "TM16"},
        "tax": {"rate_path": [{"from_year": 2027, "rate": 0.2}], "source": "TM27"},
        "working_capital": {"method": "normalized_pct_revenue", "nwc_bn": 80, "source": SRC},
        "scenarios": {"items": [{"name": "xau", "side": "down", "p": 0.25},
                                {"name": "co_so", "side": "base", "p": 0.5},
                                {"name": "tot", "side": "up", "p": 0.25}]},
        "discount_rate": {"r": 0.135, "deposit_rate_now": 0.074, "deposit_rate_date": "2026-11-20",
                          "deposit_rate_source": "deposit_rate_vn.effective_deposit_rate", "beta_passthrough": 1.0,
                          "sensitivity_bp": [-100, -50, 50, 100], "band_ends_reported": True},
        "terminal": {"moat_tier": "NARROW", "terminal_ronic": "EQUALS_KE", "g": 0.03},
        "liquidity_discount": {"basis": "computed_after_lock", "pct": None, "source": "bước riêng sau khoá"},
        "audit_opinion": {"status": "unqualified", "fy": 2025, "auditor": "UHY", "source": "src/fy2025_kt.pdf p4"},
        "related_parties": {"items": [{"desc": "bán hàng cho công ty mẹ", "amount_bn": 120, "source": "TM35"}]},
        "one_offs": {"items": [], "none_reason": "không có", "searched": ["TM KQKD 9T26"]},
        "capital_commitments_12m": {"items": [{"desc": "góp vốn dự án", "amount_bn": 300, "source": "NQ HĐQT 05/2026"}]},
        "sector": {},
    }


def bank():
    d = good()
    d.update(loai_hinh="bank", projects={"items": [], "none_reason": "ngân hàng"},
             working_capital={"method": "not_applicable_bank", "source": "không áp dụng cho ngân hàng"})
    kcb = {"value": "khong_cong_bo", "searched": ["BCTC Q3 TM", "BC thường niên 2025"]}
    d["sector"] = {"car": {"value": 0.115, "source": "báo chí 1 nguồn"}, "npl_group2_ratio": 0.0028,
                   "npl_coverage": 2.3, "ldr": 0.82, "casa": kcb}
    return d


def mut(fn):
    d = good()
    fn(d)
    return d


MUTATIONS = [
    ("thiếu khoá welfare_fund", lambda d: d.pop("welfare_fund"), "S:"),
    ("thiếu cam kết vốn", lambda d: d.pop("capital_commitments_12m"), "S:"),
    ("khong_cong_bo không kèm nguồn đã tìm", lambda d: d["welfare_fund"].update(
        annual_appropriation_pct_of_npat={"value": "khong_cong_bo", "searched": []}), "S:"),
    ("one_offs rỗng không lý do", lambda d: d.update(one_offs={"items": []}), "S:"),
    ("loai_hinh lạ", lambda d: d.update(loai_hinh="thep"), "S:"),
    ("audit enum lạ", lambda d: d["audit_opinion"].update(status="ok"), "S:"),
    ("ngoại trừ không nêu cơ sở", lambda d: d["audit_opinion"].update(status="qualified"), "S:"),
    ("WIDE thiếu cơ chế", lambda d: d["terminal"].update(moat_tier="WIDE", terminal_ronic="MOAT_WIDE_WITH_MECHANISM"), "S:"),
    ("tổng trọng số 0,95", lambda d: d["scenarios"]["items"][2].update(p=0.20), "L1:"),
    ("lệch 30/50/20 không lý do", lambda d: d["scenarios"]["items"][0].update(p=0.30) or
     d["scenarios"]["items"][2].update(p=0.20), "L2:"),
    ("r 13% không ghi đè", lambda d: d["discount_rate"].update(r=0.13), "L3:"),
    ("lãi huy động +50bp mà r giữ 13,5%", lambda d: d["discount_rate"].update(deposit_rate_now=0.079), "L3:"),
    ("thiếu độ nhạy ±100bp", lambda d: d["discount_rate"].update(sensitivity_bp=[-50, 50]), "L4:"),
    ("không báo hai đầu dải", lambda d: d["discount_rate"].update(band_ends_reported=False), "L5:"),
    ("NARROW mà RONIC>Ke", lambda d: d["terminal"].update(terminal_ronic="MOAT_WIDE_WITH_MECHANISM",
                                                         mechanism_reason="giấy phép độc quyền dài hạn"), "L6:"),
    ("capex tuân thủ ghi NPV0 (ca QTP)", lambda d: d["projects"]["items"][1].update(treatment="NPV0_BOOK"), "L7:"),
    ("bắt buộc không doanh thu, nhãn growth", lambda d: d["projects"]["items"][1].update(
        classification="growth", treatment="NPV0_BOOK"), "L7:"),
    ("growth âm không cơ sở (ca MVC r4)", lambda d: d["projects"]["items"][0].update(treatment="SCENARIO_ONLY"), "L7:"),
    ("method_version cũ", lambda d: d.update(method_version="M20261103B"), "L8:"),
    ("khoá adv_60d", lambda d: d["liquidity_discount"].update(adv_60d=175.0), "L9:"),
    ("khoá pe", lambda d: d.update(pe=6.2), "L9:"),
    ("chuỗi có ADV", lambda d: d["liquidity_discount"].update(source="ADV trung vị 3 năm = 175 tỷ"), "L9:"),
    ("chuỗi có P/E", lambda d: d["tax"].update(note="PE 6,2 lúc truy vấn"), "L9:"),
    ("BCTC kiểm toán cũ FY2024", lambda d: d["audit_opinion"].update(fy=2024), "L10:"),
]


def codes(viol):
    return {x.split(":", 1)[0] + ":" for x in viol}


def run_doc(doc):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False)
        p = f.name
    v, n, _ = L.lint(p)
    return v, n, p


def main():
    fails = 0
    ok_n = 0

    def check(cond, msg):
        nonlocal fails, ok_n
        if cond:
            ok_n += 1
            print(f"PASS {msg}")
        else:
            fails += 1
            print(f"FAIL {msg}")

    for name, doc in (("fixture đúng (sản xuất)", good()), ("fixture đúng (ngân hàng)", bank())):
        v, _, p = run_doc(doc)
        check(v == [], f"{name}: 0 vi phạm {v[:3]}")
        os.unlink(p)

    # biến thể ngành: bank thiếu CASA ⇒ S
    b = bank()
    b["sector"].pop("casa")
    v, _, p = run_doc(b)
    check("S:" in codes(v), f"bank thiếu casa ⇒ S {v[:2]}")
    os.unlink(p)
    for lh, key in (("mo_giay_phep", "license_expiry"), ("dien_ppa", "ppa_expiry"), ("bds_kcn", "land_bank")):
        d = good()
        d["loai_hinh"] = lh
        v, _, p = run_doc(d)
        check(any(key in x for x in v), f"{lh} thiếu {key} ⇒ S")
        os.unlink(p)
    d = good()
    d.update(loai_hinh="dien_ppa", sector={"ppa_expiry": {"value": "2047", "source": "TM20"},
                                           "ppa_price": {"value": "khong_cong_bo", "searched": ["HĐ mua bán điện"]}})
    v, _, p = run_doc(d)
    check(v == [], f"dien_ppa đủ (ppa_price khong_cong_bo có nguồn đã tìm) ⇒ 0 vi phạm {v[:2]}; ppa_price không bị L9")
    os.unlink(p)

    # override_reason hợp lệ tắt L3
    d = good()
    d["discount_rate"].update(r=0.13, override_reason="dòng tiền hợp đồng có thời hạn, lãi khớp kỳ hạn")
    v, _, p = run_doc(d)
    check("L3:" not in codes(v), "r lệch có override_reason ⇒ không L3")
    os.unlink(p)
    # asymmetry_reason tắt L2
    d = good()
    d["scenarios"]["items"][0]["p"] = 0.30
    d["scenarios"]["items"][2]["p"] = 0.20
    d["scenarios"]["asymmetry_reason"] = "P4 ở p90 chế độ 2023+, nguồn quặng ADMIN_GATED"
    v, _, p = run_doc(d)
    check(v == [], f"lệch có asymmetry_reason ⇒ 0 vi phạm {v[:2]}")
    os.unlink(p)
    # method_version cùng ngày nhiều mốc
    d = good()
    d.update(dd_date="2026-11-03", method_version="M20261103A")
    d["discount_rate"]["band_ends_reported"] = False
    v, _, p = run_doc(d)
    check("L8:" not in codes(v) and "L5:" not in codes(v), f"dd 03/11 + M20261103A hợp lệ, D4 chưa áp {v[:2]}")
    os.unlink(p)
    # audited_fy_missing ⇒ note, không vi phạm
    d = good()
    d["audit_opinion"] = {"status": "audited_fy_missing", "source": "chưa tải được BCTC 2025 KT"}
    v, n, p = run_doc(d)
    check(v == [] and any("Bậc 1" in x for x in n), f"audited_fy_missing ⇒ 0 vi phạm + ghi chú D5 {v[:2]}")
    os.unlink(p)

    for name, fn, code in MUTATIONS:
        v, _, p = run_doc(mut(fn))
        check(code in codes(v), f"mutation '{name}' ⇒ {code} (bắn: {sorted(codes(v))})")
        os.unlink(p)

    # rc: cảnh báo rc=0, --strict rc=1, ENFORCE_FROM đã qua ⇒ rc=1
    bad = mut(lambda d: d["discount_rate"].update(r=0.13))
    _, _, p = run_doc(bad)
    exe = [sys.executable, os.path.join(HERE, "dd_assumptions_lint.py"), p]
    r0 = subprocess.run(exe, capture_output=True, text=True).returncode
    r1 = subprocess.run(exe + ["--strict"], capture_output=True, text=True).returncode
    check(r0 == 0 and r1 == 1, f"rc cảnh báo={r0} (kỳ vọng 0), --strict={r1} (kỳ vọng 1)")
    saved = L.DD_ASSUMPTIONS_LINT_ENFORCE_FROM
    L.DD_ASSUMPTIONS_LINT_ENFORCE_FROM = "2026-01-01"
    r2 = L.main([p])
    L.DD_ASSUMPTIONS_LINT_ENFORCE_FROM = saved
    check(r2 == 1, f"dd_date ≥ ENFORCE_FROM ⇒ rc={r2} (kỳ vọng 1)")
    check(saved == "9999-12-31", f"hằng ENFORCE_FROM giao hàng = {saved}")
    os.unlink(p)
    good_p = run_doc(good())[2]
    r3 = subprocess.run(exe[:2] + [good_p, "--strict"], capture_output=True, text=True).returncode
    check(r3 == 0, f"fixture đúng --strict rc={r3}")
    os.unlink(good_p)

    print(f"\nTZ={os.environ.get('TZ', '<unset>')} · {ok_n} PASS / {fails} FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
