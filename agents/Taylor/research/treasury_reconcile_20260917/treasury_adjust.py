"""PROTOTYPE (research, KHÔNG wire) — điều chỉnh CP quỹ cho một con số OShares đã tính bởi oshares_live.

Sự thật ngữ nghĩa quyết định thiết kế (đo 2026-09-17, xem report.md §A2):
  * Mua CP quỹ KHÔNG đổi số NIÊM YẾT. `AIS.shares_total_after` = niêm yết (GỒM CP quỹ);
    `ticker_financial.OShares` = lưu hành (ĐÃ TRỪ CP quỹ). VRE: 2.328.818.410 − 2.272.318.410 = 56.500.000.
  * ⇒ KHÔNG hấp thụ kiểu ISS ("đến AIS kế tiếp thì hết"): AIS kế tiếp VẪN gồm CP quỹ, khoảng lệch
    tái xuất hiện. Phần trừ phải KÉO DÀI qua mọi neo AIS cho tới khi CP quỹ được bán/huỷ.
  * Neo dòng BCTC đã trừ sẵn ⇒ chỉ áp sự kiện treasury SAU ngày dòng quý (và chưa bị restate hấp thụ).

Hàm THUẦN, không đọc BQ: mọi input do caller truyền (hermetic selfcheck).
"""

CEILING_PCT = 15.0   # registry treasury_news Bẫy(3): > ~15% ⇒ nghi gắn nhầm nguyên nhân (ca MCH)
TOL = 1.0            # cổ phiếu


def _sign(ev):
    """buy_done ⇒ lưu hành GIẢM; sell_done ⇒ TĂNG. treasury_news.shares_delta luôn DƯƠNG cho buy_done."""
    return -1.0 if ev["action_type"] == "buy_done" else 1.0


def treasury_adjust(base, anchor_source, anchor_date, asof, fin_rows, listed_at, events, listed_cuts=()):
    """Trả (value, label, detail).

    base          — số oshares_live đã tính (neo + ISS lăn tiến), None ⇒ trả nguyên None.
    anchor_source — "corporate_action.AIS" (niêm yết) | "ticker_financial" (lưu hành).
    fin_rows      — [(time, OShares)] tăng dần, chỉ phần <= asof.
    listed_at     — callable(date) -> số niêm yết lăn tới ngày đó (None nếu không dựng được).
    events        — sự kiện treasury ĐÃ GỘP trùng, chỉ buy_done/sell_done, public_date <= asof:
                    {"public_date","action_type","abs_delta"(None nếu thiếu)}.
    listed_cuts   — ngày (<= asof) mà số niêm yết GIẢM (huỷ CP quỹ/giảm vốn).
    """
    if base is None:
        return None, "PASS_NONE", {}
    fin = [r for r in fin_rows if r[0] <= asof]
    if not fin:
        return base, "TREASURY_NO_FIN", {"note": "không có dòng BCTC để hiệu chuẩn — giữ nguyên, chưa kiểm"}
    f_time, f_val = fin[-1]
    after = [e for e in events if f_time < e["public_date"] <= asof]
    unsized = [e for e in after if not e.get("abs_delta")]
    if unsized:
        return base, "TREASURY_UNSIZED", {"events": unsized}
    fwd = sum(_sign(e) * float(e["abs_delta"]) for e in after)

    if anchor_source == "ticker_financial":
        # dòng quý có thể đã bị restate SỚM gồm luôn sự kiện (ca VRE 2019-10-29): hấp thụ ngược chiều
        prev = [r for r in fin if r[0] < f_time]
        if after and prev and abs((f_val - prev[-1][1]) - fwd) <= TOL:
            return base, "TREASURY_FIN_ABSORBED", {"fin_time": f_time, "delta_in_fin": f_val - prev[-1][1]}
        return _ceiling(base, base + fwd, "TREASURY_FIN_FWD", {"fwd": fwd, "fin_time": f_time})

    # neo AIS = niêm yết ⇒ trừ số CP quỹ đang tồn, hiệu chuẩn tại dòng BCTC gần nhất
    if any(f_time < d <= asof for d in listed_cuts):
        return None, "TREASURY_CANCEL_AMBIGUOUS", {"note": "niêm yết giảm sau dòng quý — phần hiệu chuẩn có thể đã bị huỷ"}
    l_at_fin = listed_at(f_time)
    if l_at_fin is None:
        return None, "TREASURY_NO_LISTED", {"fin_time": f_time}
    held = l_at_fin - f_val
    if held < -TOL:
        return base, "TREASURY_NEG_GAP", {"held": held, "note": "lưu hành > niêm yết: không phải CP quỹ, giữ nguyên"}
    held = max(held, 0.0)
    if held > TOL and not any(e["public_date"] <= f_time for e in events):
        return base, "TREASURY_GAP_UNCORROBORATED", {"held": held}
    return _ceiling(base, base - held + fwd, "TREASURY_AIS_ADJ", {"held_at_fin": held, "fwd": fwd, "fin_time": f_time})


def _ceiling(base, value, label, detail):
    if base and abs(value - base) / base * 100 > CEILING_PCT:
        return None, "TREASURY_CEILING", {**detail, "proposed": value}
    return value, label, detail
