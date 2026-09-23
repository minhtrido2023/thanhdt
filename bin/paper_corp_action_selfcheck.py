#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""paper_corp_action_selfcheck.py — kiểm `paper_corp_action.py` trên SỰ KIỆN THẬT.

HERMETIC: mọi sự kiện + `p_cum` dưới đây là bản sao NGUYÊN VĂN đã đọc từ
`tav2_bq.corporate_action` và `tav2_bq.ticker.Price` ngày 2026-09-23 (job
Taylor_20260923_005911), nên selfcheck chạy được offline, không cần BQ/mạng, và không lệ thuộc
biến môi trường nào — kể cả TZ (§16: chạy lại dưới `env -u TZ` và một TZ lạ phải cho cùng kết quả).

6 ca THẬT, chọn vì mỗi ca bẻ một chỗ khác nhau của công thức:
  FPT 2026-09-21  thưởng 10%                  — ca ĐANG NẰM TRONG sổ paper main
  MBB 2026-07-09  cổ tức tiền 1.000đ          — ca chỉ-tiền, KL không đổi
  MBB 2026-08-11  quyền mua 10% + cổ tức CP 15% — GỘP: phải CỘNG tỉ lệ (0,25) chứ không NHÂN
                  (1,10×1,15=1,265); P_ref thật app DNSE = 20.200đ là mốc đối chiếu ngoài
  VHM 2026-08-06  cổ tức CP 100%              — share_factor 2,0 (ca "500cp → 1.000cp" đã biết)
  VIB 2026-09-10  thưởng 9,5%                 — sinh CỔ PHIẾU LẺ, kiểm nhánh quy lẻ ra tiền
  DGC 2026-09-14  tiền 3.000đ + tiền 5.000đ   — GỘP 2 cổ tức tiền cùng ngày, phải CỘNG = 8.000đ
"""
from __future__ import annotations

import os
import sys

WC_ROOT = "/home/trido/thanhdt/WorkingClaude"
for p in (WC_ROOT, os.path.join(WC_ROOT, "mike", "bin")):
    if p not in sys.path:
        sys.path.insert(0, p)

import paper_corp_action as P  # noqa: E402

FAILS = []
NCHECK = 0


def check(name, cond, detail=""):
    global NCHECK
    NCHECK += 1
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
    if not cond:
        FAILS.append(name)


def _iss(tk, d, ratio, method, title=""):
    return {"ticker": tk, "event_code": "ISS", "exright_date": d, "event_status": "executed",
            "exercise_ratio": str(ratio), "issue_method_name_vi": method,
            "value_per_share": None, "event_title_vi": title}


def _div(tk, d, vps, title=""):
    return {"ticker": tk, "event_code": "DIV", "exright_date": d, "event_status": "executed",
            "exercise_ratio": str(vps / 10000.0), "issue_method_name_vi": None,
            "value_per_share": str(float(vps)), "event_title_vi": title}


BONUS = "Cổ phiếu thưởng"
STOCKDIV = "Trả Cổ tức bằng Cổ phiếu"
RIGHTS = "Quyền mua CP cho Cổ đông hiện hữu"

# (tên, ticker, ex_date, [events], p_cum THẬT, KL vào)
REAL = [
    ("FPT 2026-09-21 thưởng 10%", "FPT", "2026-09-21",
     [_iss("FPT", "2026-09-21", 0.1, BONUS)], 71700.0, 500),
    ("MBB 2026-07-09 tiền 1.000đ", "MBB", "2026-07-09",
     [_div("MBB", "2026-07-09", 1000.0)], 26000.0, 1500),
    ("MBB 2026-08-11 quyền mua 10% + cổ tức CP 15%", "MBB", "2026-08-11",
     [_iss("MBB", "2026-08-11", 0.1, RIGHTS), _iss("MBB", "2026-08-11", 0.15, STOCKDIV)],
     24250.0, 1500),
    ("VHM 2026-08-06 cổ tức CP 100%", "VHM", "2026-08-06",
     [_iss("VHM", "2026-08-06", 1.0, STOCKDIV)], 153000.0, 500),
    ("VIB 2026-09-10 thưởng 9,5%", "VIB", "2026-09-10",
     [_iss("VIB", "2026-09-10", 0.095, BONUS)], 15000.0, 1000),
    ("DGC 2026-09-14 tiền 3.000đ + 5.000đ", "DGC", "2026-09-14",
     [_div("DGC", "2026-09-14", 3000.0), _div("DGC", "2026-09-14", 5000.0)], 46750.0, 700),
]

CASH0 = 795_684_522.0   # tiền sổ paper main 2026-09-23 — đủ cho mọi ca quyền mua dưới đây


def main() -> int:
    print("── A. 6 ca THẬT: bất biến bảo toàn giá trị (self-check 0 VND) ──")
    recs = {}
    for name, tk, d, evs, p_cum, qty in REAL:
        rec, why = P.build_record(tk, d, evs, qty, CASH0, p_cum)
        if rec is None:
            check(name, False, f"build_record TỪ CHỐI: {why}")
            continue
        recs[tk + d] = rec
        ok, resid = P.verify_invariant(rec)
        check(f"{name}: bất biến KL×P_cum = KL'×P_ref + Δtiền", ok,
              f"dư {resid:+.6f}đ (≤{P.INVARIANT_TOL_VND}đ) · KL {rec['qty_before']:,}→"
              f"{rec['qty_after']:,} · tiền {rec['cash_delta_vnd']:+,.0f}đ · "
              f"P_ref {rec['p_ref']:,.2f}đ")

    print("\n── B. con số PHẢI đúng (mốc ngoài, không suy từ chính code) ──")
    r = recs.get("MBB2026-08-11")
    check("MBB 08-11: P_ref = 20.200đ đúng bằng giá tham chiếu app DNSE hiển thị thật",
          r is not None and abs(r["p_ref"] - 20200.0) < 0.5,
          f"tính được {r['p_ref']:,.2f}đ" if r else "không có bản ghi")
    check("MBB 08-11: tỉ lệ GỘP = 0,25 (CỘNG 0,10+0,15), KHÔNG phải nhân 1,10×1,15−1 = 0,265",
          r is not None and abs(r["ratio"] - 0.25) < 1e-9,
          f"ratio = {r['ratio']}" if r else "")
    check("MBB 08-11: KL 1.500 → 1.875 (= 1.500 × 1,25), không lẻ",
          r is not None and r["qty_after"] == 1875 and abs(r["frac_shares"]) < 1e-9,
          f"{r['qty_after']:,} · lẻ {r['frac_shares']}" if r else "")
    check("MBB 08-11: tiền GIẢM đúng 1.500×0,10×10.000 = 1.500.000đ (thực hiện 100% quyền mua)",
          r is not None and abs(r["cash_delta_vnd"] + 1_500_000.0) < 0.5,
          f"Δtiền {r['cash_delta_vnd']:+,.0f}đ" if r else "")

    v = recs.get("VHM2026-08-06")
    check("VHM 08-06: share_factor 2,0 — 500cp → 1.000cp (con số broker thật đã ghi)",
          v is not None and v["qty_after"] == 1000, f"{v['qty_after']:,}" if v else "")
    check("VHM 08-06: KHÔNG sinh/mất tiền (cổ tức CP thuần, Δtiền = 0)",
          v is not None and abs(v["cash_delta_vnd"]) < 1e-6,
          f"Δtiền {v['cash_delta_vnd']:+,.4f}đ" if v else "")

    m = recs.get("MBB2026-07-09")
    check("MBB 07-09: cổ tức TIỀN không đổi KL (1.500 → 1.500)",
          m is not None and m["qty_after"] == 1500, f"{m['qty_after']:,}" if m else "")
    check("MBB 07-09: tiền CỘNG đúng 1.500×1.000 = 1.500.000đ, MỘT LẦN",
          m is not None and abs(m["cash_delta_vnd"] - 1_500_000.0) < 0.5,
          f"Δtiền {m['cash_delta_vnd']:+,.0f}đ" if m else "")
    check("MBB 07-09: P_ref = 26.000 − 1.000 = 25.000đ (khớp giá tham chiếu thật đã đo)",
          m is not None and abs(m["p_ref"] - 25000.0) < 0.5,
          f"{m['p_ref']:,.2f}đ" if m else "")

    g = recs.get("DGC2026-09-14")
    check("DGC 09-14: 2 cổ tức tiền cùng ngày phải CỘNG = 8.000đ/CP ⇒ 700×8.000 = 5.600.000đ",
          g is not None and abs(g["cash_delta_vnd"] - 5_600_000.0) < 0.5,
          f"Δtiền {g['cash_delta_vnd']:+,.0f}đ" if g else "")

    b = recs.get("VIB2026-09-10")
    check("VIB 09-10: 1.000 × 1,095 = 1.095 CP chẵn, phần lẻ = 0",
          b is not None and b["qty_after"] == 1095 and abs(b["frac_shares"]) < 1e-9,
          f"{b['qty_after']:,} · lẻ {b['frac_shares']}" if b else "")

    print("\n── C. LẺ cổ phiếu: quy ra tiền theo P_ref, bất biến vẫn giữ ──")
    rec, why = P.build_record("VIB", "2026-09-10",
                              [_iss("VIB", "2026-09-10", 0.095, BONUS)], 111, CASH0, 15000.0)
    check("VIB thưởng 9,5% trên 111cp → 121cp + lẻ 0,545cp (111×1,095 = 121,545)",
          rec is not None and rec["qty_after"] == 121 and abs(rec["frac_shares"] - 0.545) < 1e-9,
          f"{rec['qty_after']} · lẻ {rec['frac_shares']:.6f}" if rec else why)
    ok, resid = P.verify_invariant(rec) if rec else (False, None)
    check("ca có lẻ: bất biến 0 VND vẫn giữ (lẻ quy tiền theo P_ref)", ok,
          f"dư {resid:+.6f}đ · tiền lẻ {rec['frac_cash_vnd']:,.2f}đ" if rec else "")

    print("\n── D. FAIL-CLOSED: không đoán, không áp một nửa ──")
    rec, why = P.build_record("XYZ", "2026-08-11",
                              [_iss("XYZ", "2026-08-11", 0.1, RIGHTS)], 1000, CASH0, 20000.0)
    check("quyền mua KHÔNG có giá phát hành trong RIGHTS_ISSUE_PRICE ⇒ TỪ CHỐI (không coi giá = 0)",
          rec is None and "quyền mua" in why.lower(), why[:110])
    rec, why = P.build_record("FPT", "2026-09-21",
                              [_iss("FPT", "2026-09-21", 0.1, BONUS)], 500, CASH0, None)
    check("thiếu p_cum ⇒ TỪ CHỐI (không dựng được P_ref thì không kiểm được bất biến)",
          rec is None and "p_cum" in why, why[:110])
    rec, why = P.build_record("MBB", "2026-08-11",
                              [_iss("MBB", "2026-08-11", 0.1, RIGHTS)], 1_000_000, 1000.0, 24250.0)
    check("không đủ tiền thực hiện 100% quyền mua ⇒ TỪ CHỐI (không tự hạ xuống mua một phần)",
          rec is None and "FAIL-CLOSED" in why, why[:110])
    rec, why = P.build_record("ANY", "2026-08-11",
                              [_iss("ANY", "2026-08-11", 0, BONUS)], 500, CASH0, 20000.0)
    check("exercise_ratio rác (0) ⇒ TỪ CHỐI", rec is None, why[:110])

    print("\n── E. IDEMPOTENT: chạy lại KHÔNG áp 2 lần (§5) ──")
    st = {"cash": CASH0, "positions": {"FPT": 500, "MBB": 1500}}
    r1, _ = P.build_record("FPT", "2026-09-21",
                           [_iss("FPT", "2026-09-21", 0.1, BONUS)], 500, CASH0, 71700.0)
    s1 = P.apply_records(st, [r1], asof="2026-09-21")
    check("lần 1: áp 1 sự kiện, FPT 500 → 550", len(s1["applied"]) == 1 and st["positions"]["FPT"] == 550,
          f"FPT = {st['positions']['FPT']}")
    cash_after_1, qty_after_1 = st["cash"], st["positions"]["FPT"]
    s2 = P.apply_records(st, [r1], asof="2026-09-21")
    check("lần 2 CÙNG bản ghi: bỏ qua, KL và tiền KHÔNG đổi",
          len(s2["applied"]) == 0 and len(s2["skipped_duplicate"]) == 1
          and st["positions"]["FPT"] == qty_after_1 and st["cash"] == cash_after_1,
          f"FPT = {st['positions']['FPT']} · tiền {st['cash']:,.0f}đ")

    st2 = {"cash": CASH0, "positions": {"FPT": 400}}   # KL sổ ≠ qty_before của bản ghi
    s3 = P.apply_records(st2, [r1], asof="2026-09-21")
    check("KL sổ đã đổi giữa chừng ⇒ TỪ CHỐI áp mù (không đè lên KL khác)",
          len(s3["applied"]) == 0 and len(s3.get("rejected", [])) == 1
          and st2["positions"]["FPT"] == 400, str(s3.get("rejected")))

    print("\n── F. KHÔNG hồi tố mặc định + không giữ vị thế thì không áp ──")
    rec, why = P.build_record("FPT", "2026-09-21",
                              [_iss("FPT", "2026-09-21", 0.1, BONUS)], 0, CASH0, 71700.0)
    check("KL = 0 ⇒ không dựng bản ghi", rec is None, why[:80])

    print(f"\n{'='*70}\n{NCHECK - len(FAILS)}/{NCHECK} PASS"
          + (f" · FAIL: {FAILS}" if FAILS else " · không có FAIL"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
