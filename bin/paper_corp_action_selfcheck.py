#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""paper_corp_action_selfcheck.py — kiểm `paper_corp_action.py` trên SỰ KIỆN THẬT.

HERMETIC: mọi sự kiện, `p_cum`, `Close` phiên cum và KL-tại-ngày-GDKHQ dưới đây là bản sao
NGUYÊN VĂN đã đọc từ `tav2_bq.corporate_action`, `tav2_bq.ticker` và băng `fills` của
`secrets/bot_paper_account.json` ngày 2026-09-23 (job Taylor_20260923_005911). Chạy offline,
không cần BQ/mạng, không lệ thuộc biến môi trường nào — kể cả TZ (§16: `env -u TZ` và một TZ lạ
phải cho cùng kết quả).

6 ca THẬT, mỗi ca bẻ một chỗ khác nhau:
  FPT 2026-09-21  thưởng 10%                     — ca nằm trong chính sổ paper main (KL 300)
  MBB 2026-07-09  cổ tức tiền 1.000đ             — chỉ-tiền, KL không đổi (KL 1.100)
  MBB 2026-08-11  quyền mua 10% + cổ tức CP 15%  — MẪU SỐ GIÁ 0,25 nhưng KL chỉ ×1,15 (KL 1.200)
  VHM 2026-08-06  cổ tức CP 100%                 — share_factor 2,0
  VIB 2026-09-10  thưởng 9,5%                    — sinh cổ phiếu LẺ
  DGC 2026-09-14  tiền 3.000đ + tiền 5.000đ      — GỘP 2 cổ tức tiền cùng ngày

⚠️ KL của 3 ca đầu là KL THẬT VÀO SÁNG NGÀY GDKHQ, dựng lại từ băng `fills` (300 / 1.100 /
1.200) — KHÔNG phải KL hôm nay (500 / 1.500). Sổ paper churn mỗi phiên nên hai con số khác nhau;
dùng KL hôm nay cho một sự kiện quá khứ là sai kinh tế, và vòng 1 đã mắc đúng lỗi đó.
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

# (tên, ticker, ex_date, [events], p_cum THẬT, KL THẬT sáng GDKHQ, Close phiên cum THẬT)
# `close_cum=None` ⇒ neo phải TỰ BỎ QUA vì mã còn sự kiện sau đó (chỉ ca MBB 07-09).
REAL = [
    ("FPT 2026-09-21 thưởng 10%", "FPT", "2026-09-21",
     [_iss("FPT", "2026-09-21", 0.1, BONUS)], 71700.0, 300, 65180.0),
    ("MBB 2026-07-09 tiền 1.000đ", "MBB", "2026-07-09",
     [_div("MBB", "2026-07-09", 1000.0)], 26000.0, 1100, None),
    ("MBB 2026-08-11 quyền mua 10% + cổ tức CP 15%", "MBB", "2026-08-11",
     [_iss("MBB", "2026-08-11", 0.1, RIGHTS), _iss("MBB", "2026-08-11", 0.15, STOCKDIV)],
     24250.0, 1200, 20200.0),
    ("VHM 2026-08-06 cổ tức CP 100%", "VHM", "2026-08-06",
     [_iss("VHM", "2026-08-06", 1.0, STOCKDIV)], 153000.0, 500, 76500.0),
    ("VIB 2026-09-10 thưởng 9,5%", "VIB", "2026-09-10",
     [_iss("VIB", "2026-09-10", 0.095, BONUS)], 15000.0, 1000, 13700.0),
    ("DGC 2026-09-14 tiền 3.000đ + 5.000đ", "DGC", "2026-09-14",
     [_div("DGC", "2026-09-14", 3000.0), _div("DGC", "2026-09-14", 5000.0)], 46750.0, 700, 38750.0),
]


def main() -> int:
    print("── A. 6 ca THẬT: đồng nhất thức bảo toàn giá trị ──")
    recs = {}
    for name, tk, d, evs, p_cum, qty, close_cum in REAL:
        rec, why = P.build_record(tk, d, evs, qty, p_cum, close_ref=close_cum)
        if rec is None:
            check(name, False, f"build_record TỪ CHỐI: {why}")
            continue
        recs[tk + d] = rec
        ok, resid = P.verify_invariant(rec)
        check(f"{name}: KL×P_cum = KL'×P_ref + Δtiền + quyền chờ", ok,
              f"dư {resid:+.6f}đ (≤{P.INVARIANT_TOL_VND}đ) · KL {rec['qty_before']:,}→"
              f"{rec['qty_after']:,} · tiền {rec['cash_delta_vnd']:+,.0f}đ · "
              f"P_ref {rec['p_ref']:,.2f}đ")

    print("\n── B. NEO NGOÀI (`ticker.Close` phiên cum) — phép kiểm DUY NHẤT ràng buộc kinh tế ──")
    for name, tk, d, _e, _p, _q, close_cum in REAL:
        r = recs.get(tk + d)
        if close_cum is None:
            continue
        check(f"{name}: P_ref khớp Close phiên cum trong 1 bước giá",
              r is not None and r["p_ref_anchor"] == "ok",
              f"P_ref {r['p_ref']:,.2f} vs Close {close_cum:,.2f} "
              f"(lệch {r['p_ref_anchor_diff']:+,.2f}đ)" if r else "")
    r = recs.get("MBB2026-07-09")
    check("MBB 07-09: không truyền Close ⇒ neo bỏ qua, KHÔNG báo lệch giả",
          r is not None and r["p_ref_anchor"] == "skipped-no-data",
          f"verdict = {r['p_ref_anchor']}" if r else "")

    print("\n── C. QUYỀN MUA KHÔNG LÀM TĂNG KL TẠI GDKHQ (bọ vòng 1) ──")
    r = recs.get("MBB2026-08-11")
    check("MBB 08-11: MẪU SỐ GIÁ = 0,25 (0,10 quyền mua + 0,15 cổ tức CP)",
          r is not None and abs(r["price_ratio"] - 0.25) < 1e-9,
          f"price_ratio = {r['price_ratio']}" if r else "")
    check("MBB 08-11: HỆ SỐ KL chỉ = 0,15 — LOẠI quyền mua",
          r is not None and abs(r["share_ratio"] - 0.15) < 1e-9,
          f"share_ratio = {r['share_ratio']}" if r else "")
    check("MBB 08-11: KL 1.200 → 1.380 (×1,15) — KHỚP broker thật 1.100→1.265 cùng hệ số; "
          "KHÔNG phải 1.500 (×1,25) như vòng 1",
          r is not None and r["qty_after"] == 1380, f"{r['qty_after']:,}" if r else "")
    check("MBB 08-11: tiền KHÔNG ra ở GDKHQ (quyền mua nộp tiền sau nhiều tuần)",
          r is not None and abs(r["cash_delta_vnd"]) < 1e-6,
          f"Δtiền {r['cash_delta_vnd']:+,.4f}đ" if r else "")
    check("MBB 08-11: quyền mua vào `pending_rights` 120cp @10.000đ, KHÔNG vào `positions`",
          r is not None and len(r["pending_rights"]) == 1
          and abs(r["pending_rights"][0]["shares"] - 120.0) < 1e-9
          and abs(r["pending_rights"][0]["issue_price"] - 10000.0) < 1e-9,
          str(r["pending_rights"]) [:120] if r else "")
    check("MBB 08-11: giá trị nội tại quyền = 120×(20.200−10.000) = 1.224.000đ",
          r is not None and abs(r["rights_intrinsic_vnd"] - 1_224_000.0) < 0.5,
          f"{r['rights_intrinsic_vnd']:,.0f}đ" if r else "")
    check("MBB 08-11: P_ref = 20.200đ — đúng giá tham chiếu app DNSE hiển thị thật",
          r is not None and abs(r["p_ref"] - 20200.0) < 0.5,
          f"{r['p_ref']:,.2f}đ" if r else "")

    print("\n── D. các con số khác phải đúng ──")
    v = recs.get("VHM2026-08-06")
    check("VHM 08-06: 500cp → 1.000cp (con số broker thật đã ghi)",
          v is not None and v["qty_after"] == 1000, f"{v['qty_after']:,}" if v else "")
    check("VHM 08-06: cổ tức CP thuần ⇒ Δtiền = 0", v is not None and abs(v["cash_delta_vnd"]) < 1e-6,
          f"{v['cash_delta_vnd']:+,.4f}đ" if v else "")
    m = recs.get("MBB2026-07-09")
    check("MBB 07-09: cổ tức TIỀN không đổi KL (1.100 → 1.100)",
          m is not None and m["qty_after"] == 1100, f"{m['qty_after']:,}" if m else "")
    check("MBB 07-09: tiền CỘNG đúng 1.100×1.000 = 1.100.000đ, MỘT LẦN",
          m is not None and abs(m["cash_delta_vnd"] - 1_100_000.0) < 0.5,
          f"{m['cash_delta_vnd']:+,.0f}đ" if m else "")
    check("MBB 07-09: P_ref = 26.000 − 1.000 = 25.000đ",
          m is not None and abs(m["p_ref"] - 25000.0) < 0.5, f"{m['p_ref']:,.2f}đ" if m else "")
    g = recs.get("DGC2026-09-14")
    check("DGC 09-14: 2 cổ tức tiền cùng ngày phải CỘNG = 8.000đ/CP ⇒ 700×8.000 = 5.600.000đ",
          g is not None and abs(g["cash_delta_vnd"] - 5_600_000.0) < 0.5,
          f"{g['cash_delta_vnd']:+,.0f}đ" if g else "")
    b = recs.get("VIB2026-09-10")
    check("VIB 09-10: 1.000 × 1,095 = 1.095 CP chẵn",
          b is not None and b["qty_after"] == 1095 and abs(b["frac_shares"]) < 1e-9,
          f"{b['qty_after']:,}" if b else "")
    f = recs.get("FPT2026-09-21")
    check("FPT 09-21: 300 × 1,1 = 330 CP", f is not None and f["qty_after"] == 330,
          f"{f['qty_after']:,}" if f else "")

    print("\n── E. LẺ cổ phiếu quy ra tiền theo P_ref ──")
    rec, why = P.build_record("VIB", "2026-09-10",
                              [_iss("VIB", "2026-09-10", 0.095, BONUS)], 111, 15000.0, 13700.0)
    check("VIB thưởng 9,5% trên 111cp → 121cp + lẻ 0,545cp",
          rec is not None and rec["qty_after"] == 121 and abs(rec["frac_shares"] - 0.545) < 1e-9,
          f"{rec['qty_after']} · lẻ {rec['frac_shares']:.6f}" if rec else why)
    ok, resid = P.verify_invariant(rec) if rec else (False, None)
    check("ca có lẻ: đồng nhất thức vẫn giữ", ok,
          f"dư {resid:+.6f}đ · tiền lẻ {rec['frac_cash_vnd']:,.2f}đ" if rec else "")

    print("\n── F. FAIL-CLOSED: không đoán, không áp một nửa ──")
    rec, why = P.build_record("XYZ", "2026-08-11",
                              [_iss("XYZ", "2026-08-11", 0.1, RIGHTS)], 1000, 20000.0)
    check("quyền mua KHÔNG có giá phát hành ⇒ TỪ CHỐI (không coi giá = 0)",
          rec is None and "quyền mua" in why.lower(), why[:100])
    rec, why = P.build_record("FPT", "2026-09-21",
                              [_iss("FPT", "2026-09-21", 0.1, BONUS)], 500, None)
    check("thiếu p_cum ⇒ TỪ CHỐI", rec is None and "p_cum" in why, why[:100])
    rec, why = P.build_record("ANY", "2026-08-11", [_iss("ANY", "2026-08-11", 0, BONUS)],
                              500, 20000.0)
    check("exercise_ratio rác (0) ⇒ TỪ CHỐI", rec is None, why[:100])
    rec, why = P.build_record("FPT", "2026-09-21",
                              [_iss("FPT", "2026-09-21", 0.1, BONUS)], 0, 71700.0)
    check("KL = 0 ⇒ không dựng bản ghi", rec is None, why[:80])

    print("\n── G. NEO LỆCH = CỐ VẤN, KHÔNG chặn (bỏ hẳn sự kiện mới là lỗi nặng hơn) ──")
    rec, why = P.build_record("MBB", "2026-08-11",
                              [_iss("MBB", "2026-08-11", 0.1, RIGHTS),
                               _iss("MBB", "2026-08-11", 0.15, STOCKDIV)],
                              1200, 24250.0, close_ref=19000.0)
    check("Close lệch xa ⇒ VẪN áp nhưng gắn cờ `mismatch` để người đối chiếu",
          rec is not None and rec["p_ref_anchor"] == "mismatch",
          f"verdict = {rec['p_ref_anchor']} · lệch {rec['p_ref_anchor_diff']:+,.2f}đ" if rec else why)

    print("\n── H. IDEMPOTENT + không áp mù (§5) ──")
    st = {"cash": 795_684_522.0, "positions": {"FPT": 300}}
    r1, _ = P.build_record("FPT", "2026-09-21",
                           [_iss("FPT", "2026-09-21", 0.1, BONUS)], 300, 71700.0, 65180.0)
    s1 = P.apply_records(st, [r1], asof="2026-09-21")
    check("lần 1: FPT 300 → 330", len(s1["applied"]) == 1 and st["positions"]["FPT"] == 330,
          f"FPT = {st['positions']['FPT']}")
    cash1, qty1 = st["cash"], st["positions"]["FPT"]
    s2 = P.apply_records(st, [r1], asof="2026-09-21")
    check("lần 2 cùng bản ghi: bỏ qua, KL và tiền KHÔNG đổi",
          len(s2["applied"]) == 0 and len(s2["skipped_duplicate"]) == 1
          and st["positions"]["FPT"] == qty1 and st["cash"] == cash1,
          f"FPT = {st['positions']['FPT']}")
    st_ext = {"cash": 1e9, "positions": {"FPT": 300}}
    s2b = P.apply_records(st_ext, [r1], asof="2026-09-21",
                          external=[{"key": "FPT|2026-09-21"}])
    check("khoá chỉ có ở SỔ CÁI NGOÀI (state bị PaperBroker ghi đè xoá mất) ⇒ vẫn KHÔNG áp lại",
          len(s2b["applied"]) == 0 and st_ext["positions"]["FPT"] == 300,
          f"FPT = {st_ext['positions']['FPT']}")
    st2 = {"cash": 1e9, "positions": {"FPT": 400}}
    s3 = P.apply_records(st2, [r1], asof="2026-09-21")
    check("KL sổ đã đổi giữa chừng ⇒ TỪ CHỐI áp mù",
          len(s3["applied"]) == 0 and len(s3["rejected"]) == 1 and st2["positions"]["FPT"] == 400,
          str(s3["rejected"]))

    print("\n── I. KL dựng lại từ băng `fills` cho đường HỒI TỐ ──")
    st4 = {"cash": 0.0, "positions": {"MBB": 1500}, "fills": [
        {"ts": "2026-07-01T09:00:00", "symbol": "MBB", "side": "buy", "qty": 1100},
        {"ts": "2026-07-20T09:00:00", "symbol": "MBB", "side": "buy", "qty": 100},
        {"ts": "2026-09-01T09:00:00", "symbol": "MBB", "side": "buy", "qty": 300},
        {"ts": "2026-08-20T09:00:00", "symbol": "FPT", "side": "buy", "qty": 999}]}
    check("KL MBB sáng 2026-07-09 = 1.100 (không phải 1.500 hôm nay)",
          P.qty_at(st4, "MBB", "2026-07-09") == 1100, str(P.qty_at(st4, "MBB", "2026-07-09")))
    check("KL MBB sáng 2026-08-11 = 1.200", P.qty_at(st4, "MBB", "2026-08-11") == 1200,
          str(P.qty_at(st4, "MBB", "2026-08-11")))
    check("fill của mã KHÁC không lọt vào", P.qty_at(st4, "MBB", "2026-09-23") == 1500,
          str(P.qty_at(st4, "MBB", "2026-09-23")))

    print("\n── J. tách tỉ lệ: `split_ratios` ──")
    pr, sr, rg, _ = P.split_ratios([_iss("MBB", "2026-08-11", 0.1, RIGHTS),
                                    _iss("MBB", "2026-08-11", 0.15, STOCKDIV)])
    check("split_ratios MBB 08-11 → price 0,25 · share 0,15 · 1 đợt quyền mua @10.000đ",
          abs(pr - 0.25) < 1e-9 and abs(sr - 0.15) < 1e-9 and len(rg) == 1
          and abs(rg[0][1] - 10000.0) < 1e-9, f"price={pr} share={sr} rights={rg}")
    pr, sr, rg, _ = P.split_ratios([_iss("VHM", "2026-08-06", 1.0, STOCKDIV)])
    check("không có quyền mua ⇒ price_ratio == share_ratio (2 vai trùng nhau, đúng)",
          abs(pr - sr) < 1e-9 and rg == [], f"price={pr} share={sr}")

    print("\n── K. collect() đầu-cuối: nối KL qua nhiều sự kiện + bỏ neo khi còn sự kiện sau ──")
    # MBB có 2 sự kiện đổi KL trong CÙNG cửa sổ. Vòng 1 đóng băng ảnh chụp KL đầu cửa sổ ⇒ sự
    # kiện thứ 2 mang qty_before SAI rồi bị TỪ CHỐI, để lại sổ ÁP DỞ DANG. Phải nối nhau.
    evs_all = ([_div("MBB", "2026-07-09", 1000.0)]
               + [_iss("MBB", "2026-08-11", 0.1, RIGHTS), _iss("MBB", "2026-08-11", 0.15, STOCKDIV)])
    pcum = {("MBB", "2026-07-09"): 26000.0, ("MBB", "2026-08-11"): 24250.0}
    closes = {("MBB", "2026-07-09"): 20820.0, ("MBB", "2026-08-11"): 20200.0}
    st5 = {"cash": 0.0, "positions": {"MBB": 1100}, "fills": [
        {"ts": "2026-07-01T09:00:00", "symbol": "MBB", "side": "buy", "qty": 1100},
        {"ts": "2026-07-20T09:00:00", "symbol": "MBB", "side": "buy", "qty": 100}]}
    recs2, errs2, edates = P.collect(
        st5, "2026-07-01", "2026-09-23",
        p_cum_fn=lambda tk, d: (pcum.get((tk, d)), {"reason": "fixture"}),
        events_fn=lambda tks, since, until: evs_all,
        close_fn=lambda tk, d: (closes.get((tk, d)), {"reason": "fixture"}))
    check("collect(): dựng đủ 2 bản ghi, không lỗi", len(recs2) == 2 and not errs2,
          f"{len(recs2)} bản ghi · errors={errs2}")
    check("collect(): sự kiện 2 NỐI từ KL sau sự kiện 1 (1.100 → 1.100 → ×1,15 = 1.265), "
          "KHÔNG phải cùng xuất phát 1.100 rồi bị từ chối",
          len(recs2) == 2 and recs2[1]["qty_before"] == 1100 and recs2[1]["qty_after"] == 1265,
          f"ev2: {recs2[1]['qty_before']} → {recs2[1]['qty_after']}" if len(recs2) == 2 else "")
    check("collect(): MBB@07-09 CÒN sự kiện 08-11 phía sau ⇒ neo = `skipped-later-events`",
          len(recs2) == 2 and recs2[0]["p_ref_anchor"] == "skipped-later-events",
          f"verdict = {recs2[0]['p_ref_anchor']}" if recs2 else "")
    check("collect(): MBB@08-11 KHÔNG còn sự kiện sau ⇒ neo chạy và khớp",
          len(recs2) == 2 and recs2[1]["p_ref_anchor"] == "ok",
          f"verdict = {recs2[1]['p_ref_anchor']}" if len(recs2) == 2 else "")
    s6 = P.apply_records(st5, recs2, asof="2026-09-23")
    check("collect()+apply(): áp ĐỦ CẢ 2, sổ không dở dang (MBB = 1.265)",
          len(s6["applied"]) == 2 and not s6["rejected"] and st5["positions"]["MBB"] == 1265,
          f"MBB = {st5['positions']['MBB']} · rejected={s6['rejected']}")

    # HỒI TỐ: KL phải dựng lại từ `fills` theo từng ngày GDKHQ, không dùng KL hiện tại.
    st7 = {"cash": 0.0, "positions": {"MBB": 1500}, "fills": [
        {"ts": "2026-07-01T09:00:00", "symbol": "MBB", "side": "buy", "qty": 1100},
        {"ts": "2026-07-20T09:00:00", "symbol": "MBB", "side": "buy", "qty": 100},
        {"ts": "2026-09-01T09:00:00", "symbol": "MBB", "side": "buy", "qty": 300}]}
    recs3, errs3, _ = P.collect(
        st7, "2026-07-01", "2026-09-23", backfill=True,
        p_cum_fn=lambda tk, d: (pcum.get((tk, d)), {"reason": "fixture"}),
        events_fn=lambda tks, since, until: evs_all,
        close_fn=lambda tk, d: (closes.get((tk, d)), {"reason": "fixture"}))
    check("collect(backfill=True): KL lấy theo NGÀY GDKHQ từ băng fills (1.100 và 1.200), "
          "KHÔNG phải 1.500 hôm nay",
          len(recs3) == 2 and recs3[0]["qty_before"] == 1100 and recs3[1]["qty_before"] == 1200,
          f"{[r['qty_before'] for r in recs3]}" if recs3 else f"errors={errs3}")

    # Chuỗi hai sự kiện ĐỀU ĐỔI KL. Ca trên (tiền → CP) không bẻ được lỗi đóng băng vì sự kiện
    # đầu giữ nguyên KL. Ở đây sự kiện 2 là THÊM một đợt thưởng 10% — dữ liệu TỔNG HỢP có chủ ý
    # (không có đợt thật nào của MBB sau 08-11); nó kiểm CƠ CHẾ nối KL, không kiểm kinh tế.
    evs_chain = [_iss("MBB", "2026-08-11", 0.1, RIGHTS),
                 _iss("MBB", "2026-08-11", 0.15, STOCKDIV),
                 _iss("MBB", "2026-09-15", 0.1, BONUS)]
    st9 = {"cash": 0.0, "positions": {"MBB": 1100}, "fills": [
        {"ts": "2026-07-01T09:00:00", "symbol": "MBB", "side": "buy", "qty": 1100}]}
    recs5, errs5, _ = P.collect(
        st9, "2026-08-01", "2026-09-23",
        p_cum_fn=lambda tk, d: ({"2026-08-11": 24250.0}.get(d, 22000.0), {"reason": "fixture"}),
        events_fn=lambda tks, since, until: evs_chain,
        close_fn=lambda tk, d: (None, {"reason": "fixture"}))
    check("hai sự kiện ĐỀU đổi KL: 1.100 →(×1,15) 1.265 →(×1,10) 1.391 — KL phải NỐI, "
          "không cùng xuất phát 1.100",
          len(recs5) == 2 and recs5[1]["qty_before"] == 1265 and recs5[1]["qty_after"] == 1391,
          f"ev2: {recs5[1]['qty_before']} → {recs5[1]['qty_after']}" if len(recs5) == 2
          else f"{len(recs5)} bản ghi · errors={errs5}")
    s10 = P.apply_records(st9, recs5, asof="2026-09-23")
    check("và áp được CẢ HAI — sổ về 1.391, không bị TỪ CHỐI dở dang ở sự kiện 2",
          len(s10["applied"]) == 2 and not s10["rejected"] and st9["positions"]["MBB"] == 1391,
          f"MBB = {st9['positions']['MBB']} · rejected={s10['rejected']}")

    st11 = {"cash": 0.0, "positions": {"MBB": 1391}, "fills": [
        {"ts": "2026-07-01T09:00:00", "symbol": "MBB", "side": "buy", "qty": 1100}]}
    recs6, errs6, _ = P.collect(
        st11, "2026-08-01", "2026-09-23", backfill=True,
        p_cum_fn=lambda tk, d: ({"2026-08-11": 24250.0}.get(d, 22000.0), {"reason": "fixture"}),
        events_fn=lambda tks, since, until: evs_chain,
        close_fn=lambda tk, d: (None, {"reason": "fixture"}))
    check("HỒI TỐ chuỗi 2 sự kiện: KL nền từ `fills` (1.100) rồi NHÂN tiếp hệ số sự kiện trước "
          "⇒ sự kiện 2 vào với 1.265, không phải 1.100",
          len(recs6) == 2 and recs6[1]["qty_before"] == 1265 and recs6[1]["qty_after"] == 1391,
          f"ev2: {recs6[1]['qty_before']} → {recs6[1]['qty_after']}" if len(recs6) == 2
          else f"errors={errs6}")

    print("\n── L. watermark KHÔNG vượt qua sự kiện còn treo ──")
    # Ca thật sẽ gặp: mọi đợt quyền mua tương lai đều fail-closed (RIGHTS_ISSUE_PRICE chỉ có 1
    # khoá quá khứ). Vòng 1 vẫn đẩy watermark ⇒ sự kiện rơi ra khỏi MỌI cửa sổ về sau, vĩnh viễn.
    st8 = {"cash": 0.0, "positions": {"ZZZ": 1000}, "fills": []}
    recs4, errs4, edates4 = P.collect(
        st8, "2026-09-01", "2026-09-23",
        p_cum_fn=lambda tk, d: (20000.0, {"reason": "fixture"}),
        events_fn=lambda tks, since, until: [_iss("ZZZ", "2026-09-15", 0.1, RIGHTS)],
        close_fn=lambda tk, d: (None, {"reason": "fixture"}))
    check("đợt quyền mua thiếu giá phát hành ⇒ 0 bản ghi + trả về NGÀY treo để chặn watermark",
          not recs4 and len(errs4) == 1 and edates4 == ["2026-09-15"],
          f"records={len(recs4)} errors={errs4} error_dates={edates4}")

    print(f"\n{'='*70}\n{NCHECK - len(FAILS)}/{NCHECK} PASS"
          + (f" · FAIL: {FAILS}" if FAILS else " · không có FAIL"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
