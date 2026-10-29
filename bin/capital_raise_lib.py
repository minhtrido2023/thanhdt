#!/usr/bin/env python3
"""Sự kiện TĂNG VỐN (phát hành CP) từ tav2_bq.corporate_action — phân loại + lọc sự kiện SỐNG. Hàm thuần.

Dùng chung cho 2 lớp cảnh báo (user chốt 29/10/2026: "nên đưa warning khi có bất kỳ việc tăng vốn nào
xuất hiện trong chu kỳ đầu tư của chúng ta"; thiết kế + số đo:
agents/Taylor/research/capital_raise_warning_20261029/REPORT.md):
  (A) lag_dd_pack.py     — cờ CAPITAL_RAISE_PENDING / CAPITAL_RAISE_12M TRƯỚC khi vào lệnh LAG
  (B) rights_issue_alert — cảnh báo mã ĐANG GIỮ khi có sự kiện tăng vốn (mọi phương thức, không chỉ quyền mua)
CHỈ CẢNH BÁO — không module nào ở đây chạm lệnh/plan/sizing.

Phân hạng theo `issue_method_code` (đếm thật trên BQ 2025-26 trong REPORT §2):
  WARN = tăng vốn THU TIỀN / pha loãng giá trị: Rights, PP (riêng lẻ), PUBL (ra công chúng), EMPL (ESOP),
         TRANS (chuyển đổi trái phiếu), MERGER (phát hành để sáp nhập), ICRE (cho trái chủ), BBOD
  INFO = tăng vốn điều lệ KHÔNG thu tiền: DIV (cổ tức bằng CP), Bonus (thưởng) — đã có luồng chỉnh giá
Mã lạ (vendor thêm mã mới) ⇒ WARN (fail-closed: thà báo thừa còn hơn im).
"""
from __future__ import annotations

import datetime as dt

WARN_METHODS = {"Rights", "PP", "PUBL", "EMPL", "TRANS", "MERGER", "ICRE", "BBOD"}
INFO_METHODS = {"DIV", "Bonus"}
METHOD_VI = {"Rights": "QUYỀN MUA", "PP": "PHÁT HÀNH RIÊNG LẺ", "PUBL": "PHÁT HÀNH RA CÔNG CHÚNG",
             "EMPL": "ESOP", "TRANS": "CHUYỂN ĐỔI TRÁI PHIẾU", "MERGER": "PHÁT HÀNH ĐỂ SÁP NHẬP",
             "ICRE": "PHÁT HÀNH CHO TRÁI CHỦ", "BBOD": "PHÁT HÀNH (BBOD)",
             "DIV": "CỔ TỨC BẰNG CP", "Bonus": "CP THƯỞNG"}
STALE_P_DAYS = 183        # dòng P/NULL cũ hơn ⇒ "nghi bỏ dở" (arch-review 2026-10-22 B1)
RAISE_12M_X = 0.10        # pha loãng THU TIỀN đã thực hiện 12 tháng > 10% ⇒ cờ (REPORT §3: ESOP thuần max 5,0%)
WINDOW_12M_DAYS = 365


def severity(r):
    m = r.get("issue_method_code")
    return "INFO" if m in INFO_METHODS else "WARN"


def is_dead(r):
    return r.get("issue_status_code") == "N" or r.get("event_status") == "not_executed"


def _f(x):
    try:
        return float(x or 0)
    except (TypeError, ValueError):
        return 0.0


def _same_ratio(a, b):
    return abs(_f(a.get("exercise_ratio")) - _f(b.get("exercise_ratio"))) < 1e-6


def is_zombie_p(r, rows, asof):
    """Dòng P/NULL đã được dòng D cùng mã + cùng phương thức + cùng tỉ lệ (GDKHQ ≤ asof, sau public_date của P)
    thay thế."""
    if r.get("issue_status_code") != "P" or r.get("exright_date"):
        return False
    pub = (r.get("public_date") or "")[:10]
    for o in rows:
        ex = o.get("exright_date")
        if o is not r and o.get("ticker") == r["ticker"] and o.get("issue_status_code") == "D" \
                and o.get("issue_method_code") == r.get("issue_method_code") \
                and ex and ex <= asof and ex > pub and _same_ratio(o, r):
            return True
    return False


def is_stale_p(r, asof):
    """Dòng P/NULL công bố cũ hơn STALE_P_DAYS ⇒ nghi bỏ dở, không phải sự kiện sống."""
    pub = (r.get("public_date") or "")[:10]
    if r.get("issue_status_code") != "P" or r.get("exright_date") or not pub:
        return False
    return (dt.date.fromisoformat(asof) - dt.date.fromisoformat(pub)).days > STALE_P_DAYS


def issue_price(r):
    """Giá phát hành: value_per_share nếu vendor điền, else total_value/issue_volumn; không có ⇒ None."""
    v = _f(r.get("value_per_share"))
    if v > 0:
        return v
    tv, vol = _f(r.get("total_value")), _f(r.get("issue_volumn"))
    return tv / vol if tv > 0 and vol > 0 else None


def dilution(r, oshares=None):
    """Số CP mới / CP hiện hữu: exercise_ratio nếu > 0, else issue_volumn/oshares; không tính được ⇒ None."""
    ratio = _f(r.get("exercise_ratio"))
    if ratio > 0:
        return ratio
    vol, os_ = _f(r.get("issue_volumn")), _f(oshares)
    return vol / os_ if vol > 0 and os_ > 0 else None


def live_events(rows, asof):
    """-> (sống, nghi_bỏ_dở). Sống = chưa huỷ, đã công bố ≤ asof, GDKHQ chưa tới (hoặc chưa có), không phải
    dòng P xác sống. Dòng P/NULL cũ > STALE_P_DAYS tách riêng (không báo như sự kiện sống)."""
    live, stale = [], []
    for r in rows:
        if is_dead(r):
            continue
        if (r.get("public_date") or "")[:10] > asof:
            continue                          # chưa công bố tại asof (hồi cứu) — không nhìn trước
        ex = r.get("exright_date") or None
        if ex and ex <= asof:
            continue                          # đã GDKHQ
        if is_zombie_p(r, rows, asof):
            continue
        (stale if is_stale_p(r, asof) else live).append(r)
    return live, stale


def cash_dilution_12m(rows, asof, oshares=None):
    """Pha loãng THU TIỀN (WARN) đã GDKHQ trong (asof−365, asof]: (Π(1+d)−1, [dòng]). Dòng không tính được
    tỉ lệ bị bỏ khỏi tích nhưng vẫn trả trong danh sách (để in 'không rõ tỉ lệ')."""
    lo = (dt.date.fromisoformat(asof) - dt.timedelta(days=WINDOW_12M_DAYS)).isoformat()
    hit, prod = [], 1.0
    for r in rows:
        ex = r.get("exright_date") or ""
        if is_dead(r) or severity(r) != "WARN" or r.get("issue_status_code") != "D" or not (lo < ex <= asof):
            continue
        hit.append(r)
        d = dilution(r, oshares)
        prod *= 1 + (d or 0)
    return prod - 1, hit


def describe(r, oshares=None):
    """1 dòng mô tả ngắn cho bằng chứng/tin."""
    d = dilution(r, oshares)
    px = issue_price(r)
    return (f"{METHOD_VI.get(r.get('issue_method_code'), r.get('issue_method_code'))} "
            f"{'pha loãng ' + format(d, '.2%') if d is not None else 'tỉ lệ CHƯA RÕ'}"
            f", trạng thái {r.get('issue_status_code') or '?'}, công bố {(r.get('public_date') or '?')[:10]}"
            f", GDKHQ {r.get('exright_date') or 'CHƯA CÓ'}"
            f"{', giá phát hành ' + format(px, ',.0f') + 'đ' if px else ''}")


def pre_entry_flags(rows, asof, oshares=None, oshares_g12=None):
    """Lớp A — trả (flags, warnings), mỗi phần tử (code, evidence). rows = mọi dòng ISS của 1 mã.

    CAPITAL_RAISE_PENDING: có sự kiện WARN SỐNG (đã công bố, chưa GDKHQ) — như SCL quyền mua 15,38% trạng thái P.
    CAPITAL_RAISE_12M: pha loãng THU TIỀN đã thực hiện 12 tháng > RAISE_12M_X.
    INFO sống (cổ tức CP/thưởng) và dòng nghi bỏ dở ⇒ chỉ warnings (không đổi status gói DD)."""
    flags, warns = [], []
    live, stale = live_events(rows, asof)
    w = [r for r in live if severity(r) == "WARN"]
    if w:
        flags.append(("CAPITAL_RAISE_PENDING", "; ".join(describe(r, oshares) for r in w)))
    g, hit = cash_dilution_12m(rows, asof, oshares)
    if g > RAISE_12M_X + 1e-9:                # 1,10−1 = 0,1000…09 trong float — đúng 10% KHÔNG cờ
        flags.append(("CAPITAL_RAISE_12M", f"pha loãng thu tiền 12 tháng {g:+.1%} > {RAISE_12M_X:.0%}: "
                      + "; ".join(describe(r, oshares) for r in hit)))
    info = [r for r in live if severity(r) == "INFO"]
    if info:
        warns.append(("CAPITAL_RAISE_INFO", "; ".join(describe(r, oshares) for r in info)))
    if stale:
        warns.append(("CAPITAL_RAISE_NGHI_BO_DO", "; ".join(describe(r, oshares) for r in stale)))
    if flags and oshares_g12 is not None:
        flags = [(c, e + f" | số CP lưu hành 4 quý {oshares_g12:+.1%} (ticker_financial.OShares, gồm cả CP thưởng/cổ tức)")
                 for c, e in flags]
    return flags, warns
