#!/usr/bin/env python3
"""Clearing giữa các sổ (PARK → LAG/BAL) — GIAI ĐOẠN 1: chế độ SHADOW (chỉ báo cáo).

Thiết kế: `kb/projects/book-clearing-plan-20261029.md`. Broker không có "sổ"; PARK/LAG/BAL chỉ là
NHÃN trong sổ lô (`park_holdings.LotBook`). Khi plan T+1 vừa BÁN PARK mã X vừa MUA LAG/BAL mã X,
phần chồng có thể CHUYỂN NHÃN (`BOOK_TRANSFER`) thay vì mua + bán thật ⇒ tiết kiệm phí 2 chiều +
thuế bán + spread.

SHADOW = script này KHÔNG sửa plan, KHÔNG ghi journal, KHÔNG gọi API broker (đọc
`dnse_raw_{asof}.jsonl` qua `read_broker_snapshot(source="jsonl")`). Đầu ra DUY NHẤT:
`mike/state/clear_books_shadow/<acct>_<plan_date>.json` + 1 dòng người đọc ra stdout.

Ba loại ghi nhận mỗi mã:
  (a) `opportunities` — lệnh MUA book LAG/BAL + lệnh BÁN book PARK cùng mã trong plan.orders:
      m_raw = min(Σ mua, Σ bán PARK, PARK bán được T+2 ∩ broker sellable); m = m_raw hạ xuống để
      phần lệnh còn lại (mua − m, bán − m) vẫn là bội lô 100 (số nhãn chuyển được phép lẻ, lệnh
      thật thì không). Tiết kiệm = m × ref × (phí mua + phí bán + thuế bán) — hằng số từ
      `dnse_fee_rates.py`, không hardcode.
  (b) `roll_candidates` — lệnh BÁN book A + MUA book B cùng mã ngoài cặp (a) (vd LAG exit + LAG
      re-entry). CHỈ BÁO, KHÔNG tính tiết kiệm (lệch spec pinned R3 ⇒ giai đoạn 2 + quant-skeptic).
  (c) `missed` — plan đang BÁN PARK mã X nhưng LAG/BAL đã MUA X trong `--missed-lookback-sessions`
      phiên gần đây (lúc PARK đang giữ X) ⇒ cơ hội đã MẤT, tiết kiệm 0, chỉ ghi phần "lẽ ra".

Chặn từng mã (vào `blocked`, có lý do — §29): excluded_tickers của account, UNVERIFIED của sổ lô
(gồm lệch đối soát broker), BANNED (`lag_forensic_filter.BANNED` + trading_rules hard_ban), sổ PARK
của mã có lô CP quyền mua, không còn PARK bán được T+2.

FAIL-CLOSED (rc=2, lý do thật ra stderr + JSON `status=ERROR`): thiếu/hỏng plan, thiếu bootstrap,
thiếu dnse_raw jsonl hoặc bản ghi positions không cùng ngày asof, không nạp được danh sách BANNED.
KHÔNG BAO GIỜ báo "không có cơ hội" khi chưa đọc được dữ liệu.

    python3 mike/bin/clear_books.py --plan-date 2026-10-29 [--account SpaceX ...] [--asof 2026-10-28]
"""
import argparse
import datetime as dt
import hashlib
import json
import math
import os
import sys
import traceback
from zoneinfo import ZoneInfo

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import dnse_fee_rates as fees  # noqa: E402
import park_holdings as ph  # noqa: E402
import wc_paths  # noqa: E402

ICT = ZoneInfo("Asia/Ho_Chi_Minh")   # §16
WC_ROOT = wc_paths.find_wc_root(__file__)
PLAN_DIR = os.path.join(WC_ROOT, "data", "trade_plans")
OUT_DIR = os.path.join(WC_ROOT, "mike", "state", "clear_books_shadow")
LOT = 100
TO_BOOKS = ("LAG", "BAL")
FROM_BOOK = "PARK"
STATUS = "SHADOW"


class DataError(Exception):
    """Không đọc được dữ liệu cần thiết ⇒ rc≠0, KHÔNG được kết luận 'không có cơ hội'."""


def rates():
    return {"buy_fee": fees.FEE_RATE_BUY_PCT / 100.0, "sell_fee": fees.FEE_RATE_SELL_PCT / 100.0,
            "sell_tax": fees.SELL_TAX_RATE}


def saving_vnd(m, px_buy, px_sell, r):
    """Chi phí tránh được khi KHÔNG mua m cp và KHÔNG bán m cp."""
    return m * px_buy * r["buy_fee"] + m * px_sell * (r["sell_fee"] + r["sell_tax"])


def lot_feasible(m_raw, buy_qty, sell_qty):
    """m lớn nhất ≤ m_raw sao cho phần lệnh còn lại (mua − m, bán − m) đều là bội lô 100."""
    for m in range(int(m_raw), -1, -1):
        if (buy_qty - m) % LOT == 0 and (sell_qty - m) % LOT == 0:
            return m
    return 0


def load_banned():
    """BANNED toàn hệ — dùng lại hằng số của `lag_forensic_filter` (một nguồn) + hard_ban của
    trading_rules.json. Không nạp được ⇒ DataError (không đoán danh sách rỗng)."""
    sys.path.insert(0, WC_ROOT)
    try:
        from lag_forensic_filter import BANNED
    except Exception as e:
        raise DataError(f"không nạp được lag_forensic_filter.BANNED: {type(e).__name__}: {e}")
    path = os.path.join(WC_ROOT, "data", "trading_rules.json")
    try:
        hard = (json.load(open(path, encoding="utf-8")).get("exclusions", {})
                .get("hard_ban", {}).get("tickers", []))
    except Exception as e:
        raise DataError(f"không đọc được {path}: {type(e).__name__}: {e}")
    return set(BANNED) | set(hard or [])


def _sessions(start_iso, end_iso, count_fn):
    n = count_fn(dt.date.fromisoformat(start_iso), dt.date.fromisoformat(end_iso))
    if n is None:
        raise DataError("không đếm được phiên giao dịch (trading_bot.vn_market import lỗi)")
    return n


def analyze(plan, holdings, plan_date, banned, count_fn, missed_lookback=5, r=None):
    """Lõi THUẦN (không I/O) — selfcheck gọi thẳng. `holdings` = output `park_holdings()`.
    Trả dict báo cáo (chưa có meta file)."""
    r = r or rates()
    orders = plan.get("orders")
    if not isinstance(orders, list):
        raise DataError("plan thiếu `orders` dạng list")
    lots = holdings.get("lots")
    if not isinstance(lots, list):
        raise DataError("sổ lô thiếu `lots`")
    positions = holdings.get("broker_positions") or {}
    excluded = set(holdings.get("excluded_tickers") or [])
    unverified = set(holdings.get("unverified_tickers") or [])

    buys, sells = {}, {}       # ticker → {book: [order,...]}
    for o in orders:
        tk, side = o.get("ticker"), (o.get("side") or "").lower()
        bk = ph.norm_book(o.get("book"))
        try:
            q = int(o.get("qty") or 0)
        except (TypeError, ValueError):
            raise DataError(f"lệnh {o.get('id')} qty lạ {o.get('qty')!r}")
        if not tk or q <= 0 or side not in ("buy", "sell"):
            continue
        (buys if side == "buy" else sells).setdefault(tk, {}).setdefault(bk, []).append(o)

    opps, blocked, rolls, missed = [], [], [], []
    for tk in sorted(set(buys) | set(sells)):
        b_by, s_by = buys.get(tk, {}), sells.get(tk, {})
        park_sells = s_by.get(FROM_BOOK, [])
        to_bk = [bk for bk in TO_BOOKS if bk in b_by]
        park_lots = [l for l in lots if l["ticker"] == tk and l["book"] == FROM_BOOK]

        # (b) roll — mọi cặp bán A / mua B cùng mã TRỪ cặp PARK→LAG/BAL của (a). Chỉ báo.
        for a_bk, a_os in sorted(s_by.items()):
            for b_bk, b_os in sorted(b_by.items()):
                if a_bk == FROM_BOOK and b_bk in TO_BOOKS:
                    continue
                rolls.append({"ticker": tk, "sell_book": a_bk, "buy_book": b_bk,
                              "sell_qty": sum(int(o["qty"]) for o in a_os),
                              "buy_qty": sum(int(o["qty"]) for o in b_os),
                              "sell_order_ids": [o.get("id") for o in a_os],
                              "buy_order_ids": [o.get("id") for o in b_os],
                              "saving_est_vnd": 0,
                              "note": "CHỈ BÁO — roll/chéo sổ ngoài PARK→LAG/BAL là giai đoạn 2"})

        if not park_sells:
            continue
        park_sell_qty = sum(int(o["qty"]) for o in park_sells)
        px_sell = float(park_sells[0].get("ref_price") or 0)
        if not math.isfinite(px_sell) or px_sell <= 0:
            blocked.append({"ticker": tk, "reason": "thiếu/sai ref_price lệnh bán PARK — không tính được chân bán"})
            continue

        # (c) missed — LAG/BAL đã MUA gần đây trong lúc PARK đang giữ mã này.
        recent = [l for l in lots if l["ticker"] == tk and l["book"] in TO_BOOKS
                  and not l.get("book_transfer")
                  and _sessions(l["entry_date"], plan_date, count_fn) <= missed_lookback]
        if recent:
            first_buy = min(l["entry_date"] for l in recent)
            park_before = sum(l["qty"] for l in park_lots if ph._held_since(l) < first_buy)
            m_missed = min(sum(l["qty"] for l in recent), park_before)
            if m_missed > 0:
                px = px_sell or float(recent[0].get("price") or 0)
                missed.append({
                    "ticker": tk, "to_book": sorted({l["book"] for l in recent}),
                    "recent_buy_lots": [{"entry_date": l["entry_date"], "qty": l["qty"],
                                         "book": l["book"]} for l in recent],
                    "park_qty_held_before_buy": park_before, "park_sell_qty_in_plan": park_sell_qty,
                    "would_have_transferred_qty": m_missed,
                    "forgone_saving_est_vnd": round(saving_vnd(m_missed, px, px, r)),
                    "saving_est_vnd": 0,
                    "note": (f"MISSED — {FROM_BOOK} đã giữ {park_before}cp khi "
                             f"{'/'.join(sorted({l['book'] for l in recent}))} mua "
                             f"{sum(l['qty'] for l in recent)}cp từ {first_buy}; lệnh mua đã khớp "
                             f"⇒ không còn chuyển nhãn được, plan vẫn bán {park_sell_qty}cp {FROM_BOOK}")})

        if not to_bk:
            continue
        # (a) cơ hội — qua các cổng chặn từng mã
        why = None
        if tk in excluded:
            why = "excluded_tickers của account"
        elif tk in banned:
            why = "BANNED"
        elif tk in unverified:
            why = "UNVERIFIED trong sổ lô (lệch đối soát/bán không tag/corp-action...)"
        elif any(l.get("rights_subscription") for l in park_lots):
            why = f"sổ {FROM_BOOK} có lô CP quyền mua (khoá/hạn riêng)"
        if why:
            blocked.append({"ticker": tk, "reason": why})
            continue
        # PARK bán được T+2: PREFIX lô PARK (thứ tự trừ của LotBook.sell/transfer) đã đủ 2 phiên
        settled = 0
        for l in park_lots:
            if _sessions(l["entry_date"], plan_date, count_fn) < 2:
                break
            settled += l["qty"]
        pos = positions.get(tk) or {}
        broker_sellable = pos.get("sellable")
        if broker_sellable is None:
            blocked.append({"ticker": tk, "reason": "broker không có `sellable` cho mã (positions)"})
            continue
        avail = min(settled, int(broker_sellable))
        rem_buy = park_sell_qty
        for bk in to_bk:
            b_os = b_by[bk]
            buy_qty = sum(int(o["qty"]) for o in b_os)
            px_buy = float(b_os[0].get("ref_price") or 0)
            m_raw = max(0, min(buy_qty, rem_buy, avail))
            m = lot_feasible(m_raw, buy_qty, rem_buy)
            if m_raw <= 0 or px_buy <= 0:
                blocked.append({"ticker": tk, "to_book": bk,
                                "reason": (f"không còn {FROM_BOOK} bán được T+2 (lô đủ 2 phiên "
                                           f"{settled}cp, broker sellable {broker_sellable}cp)")
                                if m_raw <= 0 else "thiếu ref_price lệnh mua"})
                continue
            opps.append({
                "ticker": tk, "from_book": FROM_BOOK, "to_book": bk,
                "buy_order_ids": [o.get("id") for o in b_os], "buy_qty": buy_qty,
                "park_sell_order_ids": [o.get("id") for o in park_sells],
                "park_sell_qty": rem_buy, "park_settled_qty": settled,
                "broker_sellable": int(broker_sellable), "m_raw": m_raw,
                "transfer_qty": m, "buy_qty_after": buy_qty - m, "park_sell_qty_after": rem_buy - m,
                "ref_price_buy": px_buy, "ref_price_sell": px_sell,
                "saving_est_vnd": round(saving_vnd(m, px_buy, px_sell, r)),
                "transfer_id_proposed": f"XFER-{holdings.get('account_label')}-{plan_date}-{tk}-{FROM_BOOK}-{bk}",
                "note": ("" if m == m_raw else
                         f"m hạ {m_raw}→{m} để lệnh còn lại giữ bội lô {LOT}")})
            rem_buy -= m
            avail -= m

    return {"opportunities": opps, "blocked": blocked, "roll_candidates": rolls, "missed": missed,
            "total_saving_est_vnd": sum(o["saving_est_vnd"] for o in opps),
            "total_forgone_saving_est_vnd": sum(x["forgone_saving_est_vnd"] for x in missed)}


def summary_line(acct, plan_date, rep):
    if rep.get("status") == "ERROR":
        return f"[{STATUS}] clear_books {acct} {plan_date}: LỖI DỮ LIỆU — {rep['error']} (KHÔNG kết luận)"
    parts = [f"{o['transfer_qty']}cp {o['ticker']} {o['from_book']}→{o['to_book']} "
             f"(~{o['saving_est_vnd']:,}đ)" for o in rep["opportunities"]]
    s = (f"[{STATUS}] clear_books {acct} {plan_date}: "
         + (f"lẽ ra chuyển {'; '.join(parts)}, tiết kiệm ~{rep['total_saving_est_vnd']:,}đ"
            if parts else "không có cơ hội chuyển nhãn"))
    if rep["missed"]:
        s += " | missed: " + "; ".join(
            f"{x['ticker']} {x['would_have_transferred_qty']}cp (mất ~{x['forgone_saving_est_vnd']:,}đ)"
            for x in rep["missed"])
    if rep["roll_candidates"]:
        s += f" | roll (chỉ báo): {', '.join(sorted({x['ticker'] for x in rep['roll_candidates']}))}"
    if rep["blocked"]:
        s += f" | chặn: {', '.join(x['ticker'] + '(' + x['reason'][:40] + ')' for x in rep['blocked'])}"
    return s


def _atomic_write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, default=str)
    os.replace(tmp, path)


def run_account(acct, plan_date, asof, plan_dir, out_dir, missed_lookback, count_fn=None,
                holdings_fn=None):
    """I/O wrapper. Trả (rc, report). rc=2 ⇒ lỗi dữ liệu (report có status=ERROR + error)."""
    plan_path = os.path.join(plan_dir, f"plan_{acct}_{plan_date}.json")
    rep = {"status": STATUS, "account": acct, "plan_date": plan_date, "plan_file": plan_path,
           "generated_at": dt.datetime.now(ICT).isoformat(timespec="seconds"),
           "fee_rates": rates(), "mode_note": "SHADOW: không sửa plan, không ghi journal, không gọi API"}
    try:
        if not os.path.exists(plan_path):
            raise DataError(f"thiếu plan {plan_path}")
        raw = open(plan_path, "rb").read()
        rep["plan_md5"] = hashlib.md5(raw).hexdigest()
        try:
            plan = json.loads(raw)
        except ValueError as e:
            raise DataError(f"plan không parse được: {e}")
        plan_asof = (plan.get("park_trim_proposal") or {}).get("asof")
        if asof is None:
            asof = plan_asof
            if not asof:
                raise DataError("không suy được asof (plan thiếu park_trim_proposal.asof) — truyền --asof")
        elif plan_asof and asof != plan_asof:
            raise DataError(f"--asof={asof} ≠ park_trim_proposal.asof={plan_asof} của plan — "
                            "sổ lô/broker khác ngày với vị thế plan đã dựa vào")
        if asof >= plan_date:
            raise DataError(f"asof={asof} phải TRƯỚC plan_date={plan_date}")
        rep["asof"] = asof
        if count_fn is None:
            from portfolio_status import count_trading_days as count_fn
        gap = _sessions(asof, plan_date, count_fn)
        if gap != 1:
            raise DataError(f"asof={asof} cách plan_date={plan_date} {gap} phiên — phải là phiên "
                            "liền trước (sổ cũ ⇒ 'không có cơ hội' sẽ là âm tính giả)")
        banned = load_banned()
        if holdings_fn is None:
            prof = ph.account_profile(acct)
            broker = ph.read_broker_snapshot(acct, prof.get("account_id"), asof,
                                             need_price=False, source="jsonl")
            ts_pos = (broker[2] or {}).get("ts_positions") or ""
            if ts_pos[:10] != asof:
                raise DataError(f"bản ghi positions trong dnse_raw_{asof}.jsonl có ts={ts_pos!r} ≠ asof")
            rep["broker_source"] = {k: broker[2].get(k) for k in ("source", "ts_positions")}
            holdings = ph.park_holdings(acct, asof=asof, broker=broker, need_price=False)
        else:
            holdings = holdings_fn(acct, asof)
        rep["ledger"] = {"reconcile_ok": holdings["reconcile"]["ok"],
                         "unverified_tickers": holdings.get("unverified_tickers"),
                         "bootstrap": holdings.get("bootstrap")}
        rep.update(analyze(plan, holdings, plan_date, banned, count_fn, missed_lookback))
        rc = 0
    except (DataError, SystemExit) as e:
        rep["status"] = "ERROR"
        rep["error"] = str(e) if str(e) else type(e).__name__
        rc = 2
    except Exception as e:   # lỗi lạ: vẫn fail-closed, in nguyên traceback (§29)
        rep["status"] = "ERROR"
        rep["error"] = f"{type(e).__name__}: {e}"
        rep["traceback"] = traceback.format_exc()
        rc = 2
    rep["summary_line"] = summary_line(acct, plan_date, rep)
    _atomic_write_json(os.path.join(out_dir, f"{acct}_{plan_date}.json"), rep)
    return rc, rep


def live_accounts():
    path = os.path.join(WC_ROOT, "secrets", "trading_bot_accounts.json")
    return [a["label"] for a in json.load(open(path, encoding="utf-8")).get("accounts", [])
            if a.get("enabled") and a.get("mode") == "live" and a.get("broker") == "dnse"]


def main():
    ap = argparse.ArgumentParser(description="Clearing PARK→LAG/BAL — SHADOW (chỉ báo cáo)")
    ap.add_argument("--plan-date", required=True)
    ap.add_argument("--account", action="append", help="mặc định: mọi account live enabled")
    ap.add_argument("--asof", default=None, help="ngày sổ lô/broker (mặc định park_trim_proposal.asof)")
    ap.add_argument("--plan-dir", default=PLAN_DIR)
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--missed-lookback-sessions", type=int, default=5)
    a = ap.parse_args()
    rc_all = 0
    for acct in a.account or live_accounts():
        rc, rep = run_account(acct, a.plan_date, a.asof, a.plan_dir, a.out_dir,
                              a.missed_lookback_sessions)
        print(rep["summary_line"])
        if rc:
            print(f"[clear_books] {acct}: {rep['error']}", file=sys.stderr)
        rc_all = max(rc_all, rc)
    return rc_all


if __name__ == "__main__":
    sys.exit(main())
