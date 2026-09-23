#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""paper_corp_action.py — áp sự kiện quyền (corp-action) vào sổ PaperBroker.

VÌ SAO TỒN TẠI
--------------
`PaperBroker` (`trading_bot/brokers.py`) giữ vị thế là một con số thuần `{mã: KL}` và tiền là
một con số thuần. Nó khớp lệnh trên QUOTE THẬT — nghĩa là sáng ngày GDKHQ, giá nó nhìn thấy đã
rơi về hệ quy chiếu mới, trong khi KL nó đang giữ vẫn là KL hệ CŨ. Không ai bù phần chênh:
  · thưởng/cổ tức CP/tách: giá rơi, KL đứng im ⇒ sổ paper MẤT giá trị ảo mà NĐT thật không mất.
  · quyền mua: giá rơi, không có CP mới, không trừ tiền mua ⇒ paper KÉM NĐT thật một cách giả
    tạo đúng bằng phần giá trị của quyền.
  · cổ tức tiền: giá rơi, tiền không vào ⇒ mất đúng số cổ tức.
Sổ paper là NỀN BẰNG CHỨNG của các chương trình R&D; một cú lệch như vậy làm bẩn số đo mà không
ai nhìn sổ paper để phát hiện. Module này đóng đúng khe đó — nó là CÔNG CỤ ĐO, không chạm tiền
thật, không đi vào đường đặt lệnh.

KHÔNG VIẾT LẠI CÔNG THỨC: toàn bộ ngữ nghĩa sự kiện tái dùng hạ tầng đã có cho live —
`corp_action_lib` (taxonomy + reader BQ) và `trading_bot.price_frame.adjustment()` (hàm THUẦN,
CỘNG tỉ lệ chứ không NHÂN, fail-closed khi thiếu giá phát hành quyền mua).

⚠️ KHÔNG SAO CHÉP `cum_dividend_double_count` SANG ĐÂY — ĐÓ LÀ LỖI NẾU LÀM
--------------------------------------------------------------------------
`daily_nav_snapshot.cum_dividend_double_count` vá một HIỆN VẬT CỦA BROKER DNSE: DNSE ghi
`cashDividendReceiving` vào `totalCash` ngay TỐI NGÀY CUỐI CÒN HƯỞNG QUYỀN, trong khi giá đóng
cửa phiên đó vẫn là giá cum ⇒ NAV đếm 2 lần rồi tự triệt tiêu phiên sau.

PaperBroker KHÔNG có hiện vật đó: nó không có trường `cashDividendReceiving`, tiền chỉ đổi khi
có fill. Ở đây cổ tức tiền vào sổ ĐÚNG MỘT LẦN, tại ngày GDKHQ, CÙNG một thao tác với việc KL/giá
đổi hệ quy chiếu ⇒ không-đếm-2-lần là tính chất BẰNG CẤU TRÚC, không cần cổng dò. Bê logic trừ
của live sang đây sẽ TRỪ một khoản chưa bao giờ được cộng — tạo ra đúng cái sai nó định chống.

CHÍNH SÁCH (user chỉ đạo 2026-09-23, job Taylor_20260923_005911)
----------------------------------------------------------------
  · Quyền mua: MẶC ĐỊNH thực hiện 100% — không thực hiện là bỏ lỡ giá trị dương thật.
    Không tính phí: đăng ký mua quyền là giao dịch với tổ chức phát hành/VSD, không phải lệnh
    qua sàn ⇒ `PaperBroker.fee_rate` (phí môi giới) không áp dụng.
  · Cổ tức tiền: cộng tiền tại GDKHQ (xem khối cảnh báo trên).
  · Cổ tức CP / thưởng / tách: nhân KL theo `share_factor`, GIỮ NGUYÊN giá trị thị trường.

BẤT BIẾN ĐƯỢC CƯỠNG CHẾ (self-check 0 VND): với mỗi cụm sự kiện,
    KL_cũ × P_cum  ==  KL_mới × P_ref  +  Δtiền
đúng tới sai số làm tròn. Đây không phải lời hứa trong docstring — `verify_invariant()` tính lại
và bản ghi nào lệch quá `INVARIANT_TOL_VND` thì BỊ TỪ CHỐI, không ghi vào sổ.

LẺ CỔ PHIẾU: VN không giao dịch cổ phiếu lẻ. KL mới làm tròn XUỐNG; phần lẻ quy thành tiền theo
`P_ref` (giá tham chiếu ngày GDKHQ) và cộng vào tiền mặt. Đây là XẤP XỈ có chủ đích — thực tế tổ
chức phát hành có thể huỷ phần lẻ hoặc mua lại theo mệnh giá — nhưng nó là lựa chọn DUY NHẤT giữ
được bất biến 0 VND ở trên, và sai số bị chặn trên bởi giá 1 cổ phiếu. Ghi rõ trong từng bản ghi
(`frac_shares`, `frac_cash_vnd`) để hậu kiểm tách được phần xấp xỉ này ra.

KHÔNG HỒI TỐ: mặc định chỉ áp sự kiện có GDKHQ SAU `watermark`. Lần chạy đầu, watermark được đặt
= ngày chạy − 1 ⇒ không có sự kiện quá khứ nào bị áp ngược vào sổ, vì số liệu cũ đã là căn cứ cho
các verdict đã chốt. Muốn hồi tố phải nói rõ bằng `--backfill-since` (thao tác có chủ đích, in
cảnh báo, và KHÔNG tự chạy trong cron).

Usage:
  paper_corp_action.py [--label main] [--date YYYY-MM-DD] [--dry] [--backfill-since YYYY-MM-DD]
  paper_corp_action.py --selfcheck       # ủy quyền cho paper_corp_action_selfcheck.py
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import sys
from zoneinfo import ZoneInfo

WC_ROOT = "/home/trido/thanhdt/WorkingClaude"
if WC_ROOT not in sys.path:
    sys.path.insert(0, WC_ROOT)

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")

# Sai số cho phép của bất biến bảo toàn giá trị, tính trên TOÀN CỤM (không phải mỗi cổ phiếu).
# 1 VND là sai số làm tròn nhị phân thuần tuý: mọi số hạng đều là tích của số nguyên với giá
# VND, nên lệch thật sự chỉ có thể đến từ lỗi công thức, không từ dấu phẩy động.
INVARIANT_TOL_VND = 1.0


def now_ict() -> dt.datetime:
    return dt.datetime.now(_ICT)


def state_path(label: str) -> str:
    """Đường dẫn sổ paper theo label — PHẢI khớp `PaperBroker.__init__`, không đoán lại."""
    from trading_bot import brokers as brk
    if label == "main":
        return brk.PAPER_STATE_FILE
    return os.path.join(brk.DATA_DIR, f"bot_paper_{label}.json")


def load_state(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_state_atomic(path: str, state: dict) -> None:
    """Ghi nguyên tử (§5): kill giữa chừng không được để lại sổ paper viết dở."""
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def ledger(state: dict) -> dict:
    """Sổ con corp-action trong state (tạo nếu chưa có). Không ghi đĩa."""
    led = state.setdefault("corp_actions", {})
    led.setdefault("applied", [])
    led.setdefault("watermark", None)
    return led


def applied_keys(state: dict) -> set:
    return {r.get("key") for r in ledger(state).get("applied", [])}


def event_key(ticker: str, ex_date: str) -> str:
    return f"{str(ticker).strip().upper()}|{str(ex_date)[:10]}"


# ───────────────────────────────────────────────────────────────── lõi THUẦN (không IO)

def build_record(ticker, ex_date, events, qty0, cash_before, p_cum):
    """Một cụm sự kiện → (record | None, lý do). HÀM THUẦN — không đọc BQ, không đụng file.

    `p_cum` = giá THÔ phiên cum cuối (trước GDKHQ). Mọi nhánh không chắc chắn đều FAIL-CLOSED:
    trả `None` kèm lý do đọc được, KHÔNG áp một nửa và KHÔNG đoán số còn thiếu.
    """
    from trading_bot.price_frame import adjustment

    tk = str(ticker).strip().upper()
    if qty0 <= 0:
        return None, f"{tk}: KL = {qty0} — không giữ, bỏ qua"

    adj, info = adjustment(events)
    if adj is None:
        return None, f"{tk}@{ex_date}: {info.get('reason', 'adjustment() từ chối')}"

    try:
        p_cum = float(p_cum)
    except (TypeError, ValueError):
        p_cum = -1.0
    if not (p_cum > 0):
        return None, (f"{tk}@{ex_date}: thiếu giá phiên cum cuối (p_cum={p_cum!r}) — không dựng "
                      f"được P_ref nên không kiểm được bất biến 0 VND. FAIL-CLOSED")

    ratio = float(adj["ratio"])
    cash_ps = float(adj["cash"])              # cổ tức tiền, VND / 1 CP cũ
    rights_ps = float(adj["rights_value"])    # tiền PHẢI TRẢ mua quyền, VND / 1 CP cũ
    den = 1.0 + ratio
    num = p_cum - cash_ps + rights_ps
    if den <= 0 or num <= 0:
        return None, (f"{tk}@{ex_date}: công thức sở cho giá tham chiếu không hợp lệ "
                      f"(tử {num:,.0f}, mẫu {den})")
    p_ref = num / den

    raw_new = qty0 * den
    qty_new = int(math.floor(raw_new + 1e-9))
    frac = raw_new - qty_new
    frac_cash = frac * p_ref
    cash_div = qty0 * cash_ps
    rights_cost = qty0 * rights_ps
    cash_delta = cash_div - rights_cost + frac_cash

    if cash_before + cash_delta < 0:
        return None, (f"{tk}@{ex_date}: thực hiện 100% quyền mua cần {rights_cost:,.0f}đ nhưng sổ "
                      f"paper chỉ có {cash_before:,.0f}đ (Δ sau sự kiện = {cash_delta:,.0f}đ) ⇒ "
                      f"âm tiền. FAIL-CLOSED — chính sách 100% không tự hạ xuống mua một phần")

    rec = {
        "key": event_key(tk, ex_date), "ticker": tk, "ex_date": str(ex_date)[:10],
        "n_events": len(events or []), "reason": info.get("reason", ""),
        "ratio": ratio, "cash_per_share": cash_ps, "rights_value_per_share": rights_ps,
        "p_cum": p_cum, "p_ref": p_ref,
        "qty_before": int(qty0), "qty_after": qty_new,
        "frac_shares": frac, "frac_cash_vnd": frac_cash,
        "cash_dividend_vnd": cash_div, "rights_cost_vnd": rights_cost,
        "cash_delta_vnd": cash_delta,
        "mv_before_vnd": qty0 * p_cum, "mv_after_vnd": qty_new * p_ref,
    }
    ok, resid = verify_invariant(rec)
    rec["invariant_residual_vnd"] = resid
    if not ok:
        return None, (f"{tk}@{ex_date}: BẤT BIẾN 0 VND THẤT BẠI — lệch {resid:,.4f}đ "
                      f"(> {INVARIANT_TOL_VND}đ). Bản ghi bị TỪ CHỐI, sổ paper không đổi")
    return rec, info.get("reason", "")


def verify_invariant(rec) -> tuple:
    """KL_cũ×P_cum == KL_mới×P_ref + Δtiền → (đạt?, phần dư VND). Tính LẠI từ các trường thô."""
    lhs = rec["qty_before"] * rec["p_cum"]
    rhs = rec["qty_after"] * rec["p_ref"] + rec["cash_delta_vnd"]
    resid = lhs - rhs
    return abs(resid) <= INVARIANT_TOL_VND, resid


def apply_records(state: dict, records, asof: str) -> dict:
    """Áp danh sách bản ghi vào state (mutate). Bỏ qua key đã áp ⇒ chạy lại là idempotent."""
    led = ledger(state)
    done = applied_keys(state)
    summary = {"applied": [], "skipped_duplicate": [], "cash_delta_total": 0.0}
    for rec in records:
        if rec["key"] in done:
            summary["skipped_duplicate"].append(rec["key"])
            continue
        pos = state.setdefault("positions", {})
        cur = int(pos.get(rec["ticker"], 0))
        if cur != rec["qty_before"]:
            # Sổ đã đổi giữa lúc dựng bản ghi và lúc áp — không áp mù lên KL khác.
            summary.setdefault("rejected", []).append(
                f"{rec['key']}: KL sổ = {cur} ≠ qty_before {rec['qty_before']}")
            continue
        pos[rec["ticker"]] = rec["qty_after"]
        state["cash"] = float(state.get("cash", 0.0)) + rec["cash_delta_vnd"]
        rec = dict(rec, applied_at=now_ict().isoformat(timespec="seconds"), asof=asof)
        led["applied"].append(rec)
        done.add(rec["key"])
        summary["applied"].append(rec)
        summary["cash_delta_total"] += rec["cash_delta_vnd"]
    return summary


# ───────────────────────────────────────────────────────────────── đường production (có IO)

def collect(state, since, until, p_cum_fn=None, events_fn=None):
    """Tra sự kiện trong (since, until] cho các mã ĐANG GIỮ → (records, errors)."""
    from trading_bot.price_frame import events_by_ticker_date, p_cum_from_bq
    from trading_bot.price_frame import pricing_events as pf_pricing_events

    held = {t: int(q) for t, q in (state.get("positions") or {}).items() if int(q or 0) > 0}
    if not held:
        return [], []
    evs = (events_fn or pf_pricing_events)(sorted(held), since=since, until=until)
    by = events_by_ticker_date(evs)
    pcf = p_cum_fn or (lambda tk, d: p_cum_from_bq(tk, d))

    done = applied_keys(state)
    records, errors = [], []
    cash_run = float(state.get("cash", 0.0))
    for (tk, d), cluster in sorted(by.items()):
        if tk not in held or event_key(tk, d) in done:
            continue
        p_cum, pinfo = pcf(tk, d)
        if p_cum is None:
            errors.append(f"{tk}@{d}: {pinfo.get('reason', 'không lấy được p_cum')}")
            continue
        rec, why = build_record(tk, d, cluster, held[tk], cash_run, p_cum)
        if rec is None:
            errors.append(why)
            continue
        cash_run += rec["cash_delta_vnd"]
        records.append(rec)
    return records, errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--label", default="main")
    ap.add_argument("--date", default=None, help="ngày chạy (mặc định hôm nay ICT)")
    ap.add_argument("--dry", action="store_true", help="in ra, không ghi sổ")
    ap.add_argument("--backfill-since", default=None,
                    help="HỒI TỐ: quét từ ngày này (không dùng trong cron)")
    ap.add_argument("--selfcheck", action="store_true")
    args = ap.parse_args()

    if args.selfcheck:
        import subprocess
        return subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "paper_corp_action_selfcheck.py")]).returncode

    date = args.date or now_ict().date().isoformat()
    path = state_path(args.label)
    if not os.path.exists(path):
        print(f"[paper-ca] sổ paper [{args.label}] chưa tồn tại ({path}) — không có gì để áp")
        return 0
    state = load_state(path)
    led = ledger(state)

    if args.backfill_since:
        since = args.backfill_since
        print(f"[paper-ca] ⚠️ HỒI TỐ từ {since} — thao tác có chủ đích, sẽ ĐỔI số liệu lịch sử "
              f"của sổ paper. Mọi verdict đã chốt dựa trên số cũ cần được nêu lại thủ công.")
    elif led["watermark"]:
        since = led["watermark"]
    else:
        since = (dt.date.fromisoformat(date) - dt.timedelta(days=1)).isoformat()
        print(f"[paper-ca] lần chạy đầu trên sổ [{args.label}] — đặt watermark = {since}, "
              f"KHÔNG hồi tố sự kiện trước đó (số liệu cũ là căn cứ của verdict đã chốt).")

    records, errors = collect(state, since, date)
    for e in errors:
        print(f"[paper-ca] ❌ {e}")
    if not records:
        print(f"[paper-ca] [{args.label}] {since} → {date}: không có sự kiện nào cần áp"
              f"{' (có lỗi ở trên)' if errors else ''}")
    for r in records:
        print(f"[paper-ca] {r['ticker']}@{r['ex_date']}  KL {r['qty_before']:,} → "
              f"{r['qty_after']:,} · tiền {r['cash_delta_vnd']:+,.0f}đ "
              f"(cổ tức {r['cash_dividend_vnd']:+,.0f} − quyền mua {r['rights_cost_vnd']:,.0f} "
              f"+ lẻ {r['frac_cash_vnd']:+,.0f}) · P_cum {r['p_cum']:,.0f} → P_ref "
              f"{r['p_ref']:,.0f} · dư bất biến {r['invariant_residual_vnd']:+.4f}đ  [{r['reason']}]")

    if args.dry:
        print("[paper-ca] --dry: KHÔNG ghi sổ")
        return 1 if errors else 0

    summary = apply_records(state, records, asof=date)
    for r in summary.get("rejected", []):
        print(f"[paper-ca] ❌ TỪ CHỐI {r}")
    if not args.backfill_since:
        led["watermark"] = date
    if summary["applied"] or not args.backfill_since:
        save_state_atomic(path, state)
    print(f"[paper-ca] đã áp {len(summary['applied'])} sự kiện · tiền "
          f"{summary['cash_delta_total']:+,.0f}đ · watermark = {led['watermark']}")
    return 1 if (errors or summary.get("rejected")) else 0


if __name__ == "__main__":
    sys.exit(main())
