#!/usr/bin/env python3
"""Sổ KHAI BÁO của USER: số cổ phiếu QUYỀN MUA thực sự đã mua, RIÊNG TỪNG ACCOUNT (N1 + N4).

Luật user (chốt 22/10/2026 09:40 ICT, phương án A — kb/projects/lag-rights-lot-rule-20261022.md):
  • user TỰ thực hiện quyền mua bằng LỆNH TAY, có thể không mua đủ ở một account ⇒ số CP quyền
    KHÔNG suy ra được từ tỉ lệ, phải do user khai cho từng account;
  • lô CP quyền KẾ THỪA entry_date GỐC của lô được hưởng quyền (chụp tại GDKHQ, không phụ thuộc lô
    gốc còn hay đã bán) ⇒ thoát cùng hạn T+25 với vị thế gốc, bán ở phiên ĐẦU TIÊN được phép bán;
  • N4 (legal-vn 22/10, mức tin cậy TB-cao): CP quyền đã nộp tiền nhưng CHỜ VSDC ghi nhận KHÔNG
    vào cơ sở hưởng quyền của đợt cổ tức CP/tiền/quyền khác có ĐKCC rơi vào khoảng chờ.

File: `data/lag_rights/subscriptions.json` (`MIKE_LAG_RIGHTS_DIR` đổi thư mục — selfcheck).
Append-only; bản ghi MỚI NHẤT của (account, event_id) có hiệu lực (khai lại để sửa / bổ sung ngày
ghi nhận; `subscribed_qty=0` = huỷ khai báo). Ghi atomic (tmp + os.replace) dưới flock.
AGENT KHÔNG TỰ GHI: chỉ Mike ghi bằng `--record` khi USER đã trả lời thật (§20) — decided_by=user,
`at` có múi giờ, `source` (link/trích tin nhắn), `event_hash` khớp dòng quyền mua HIỆN TẠI trên BQ.

Consumer (cùng đọc MỘT sổ — không còn dòng journal tay / known_position_discrepancies kiểu MBB):
  park_holdings (lô mới, entry kế thừa, N4 không nhân lô chờ) · portfolio_status/auto_exit_inject
  (lô khoá chờ niêm yết) · daily_nav_snapshot/exdate_frame (KL kỳ vọng) · verify_account_snapshot
  (giá vốn bình quân gồm lô quyền) · reconcile_equity (realized/giá vốn) · cash_identity (phí 0).
File hỏng / bản ghi sai ⇒ `RightsSubscriptionError` — consumer fail-closed (như corp_actions CONFIRMED).

    python3 bin/rights_subscription.py --show [--account SpaceX]
    python3 bin/rights_subscription.py --record --account SpaceX --ticker SCL --event-id <id> \
        --event-hash <h> --subscribed-qty 5000 --issue-price 12500 --payment-date 2026-11-03 \
        --decided-by user --at 2026-11-03T10:15:00+07:00 --source "discord <link>"
        [--credit-date D] [--registered-date D] [--listing-date D] [--note ...]
"""
import argparse
import datetime as dt
import fcntl
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wc_paths  # noqa: E402
WC_ROOT = wc_paths.find_wc_root(__file__)
if WC_ROOT not in sys.path:
    sys.path.insert(0, WC_ROOT)

KIND = "rights_subscription"
KEY_PREFIX = KIND + "|"
CREDIT_TS_SUFFIX = "T23:59:59"          # cùng quy ước fill broker xác nhận ở reconcile_equity
ISSUE_PRICE_TOL_VND = 0.5
_REQ = ("account", "account_no", "ticker", "event_id", "event_hash", "exright_date", "exercise_ratio",
        "issue_price_vnd", "subscribed_qty", "payment_date", "credit_date", "decided_by", "at", "source")
_OPT_DATES = ("registered_date", "listing_date")


class RightsSubscriptionError(ValueError):
    pass


def rights_dir():
    return os.environ.get("MIKE_LAG_RIGHTS_DIR") or os.path.join(WC_ROOT, "data", "lag_rights")


def subscriptions_path():
    return os.path.join(rights_dir(), "subscriptions.json")


def _date(v, field, where):
    try:
        if len(str(v)) == 10:
            return dt.date.fromisoformat(str(v)).isoformat()
    except ValueError:
        pass
    raise RightsSubscriptionError(f"{where}: `{field}`={v!r} không phải ngày YYYY-MM-DD")


def validate(rec, where="record"):
    """Kiểm MỘT bản ghi; trả bản chuẩn hoá. Sai ⇒ RightsSubscriptionError (nêu field + giá trị)."""
    if not isinstance(rec, dict):
        raise RightsSubscriptionError(f"{where}: phải là object")
    miss = [k for k in _REQ if rec.get(k) in (None, "")]
    if miss:
        raise RightsSubscriptionError(f"{where}: thiếu {', '.join(miss)}")
    if rec["decided_by"] != "user":
        raise RightsSubscriptionError(f"{where}: decided_by={rec['decided_by']!r} — chỉ USER khai (§20)")
    try:
        at = dt.datetime.fromisoformat(str(rec["at"]))
    except ValueError:
        raise RightsSubscriptionError(f"{where}: `at`={rec['at']!r} không phải ISO datetime")
    if at.tzinfo is None:
        raise RightsSubscriptionError(f"{where}: `at` phải có múi giờ")
    out = dict(rec)
    for k in ("exright_date", "payment_date", "credit_date"):
        out[k] = _date(rec[k], k, where)
    for k in _OPT_DATES:
        out[k] = _date(rec[k], k, where) if rec.get(k) not in (None, "") else None
    try:
        qty, px, ratio = rec["subscribed_qty"], float(rec["issue_price_vnd"]), float(rec["exercise_ratio"])
    except (TypeError, ValueError):
        raise RightsSubscriptionError(f"{where}: issue_price_vnd/exercise_ratio không phải số")
    if not isinstance(qty, int) or isinstance(qty, bool) or qty < 0:
        raise RightsSubscriptionError(f"{where}: subscribed_qty={qty!r} phải là số nguyên ≥ 0")
    if px <= 0 or ratio <= 0:
        raise RightsSubscriptionError(f"{where}: issue_price_vnd={px} / exercise_ratio={ratio} phải > 0")
    if out["payment_date"] < out["exright_date"]:
        raise RightsSubscriptionError(f"{where}: payment_date {out['payment_date']} < GDKHQ {out['exright_date']}")
    if out["credit_date"] < out["payment_date"]:
        raise RightsSubscriptionError(f"{where}: credit_date {out['credit_date']} < payment_date")
    for k in _OPT_DATES:
        if out[k] and out[k] < out["credit_date"]:
            raise RightsSubscriptionError(f"{where}: {k} {out[k]} < credit_date {out['credit_date']}")
    out.update(ticker=str(rec["ticker"]).strip().upper(), account_no=str(rec["account_no"]),
               event_id=str(rec["event_id"]), issue_price_vnd=px, exercise_ratio=ratio)
    return out


def load_all(path=None):
    """Mọi bản ghi (đã validate, thứ tự file). Thiếu file ⇒ []. Hỏng ⇒ raise."""
    p = path or subscriptions_path()
    if not os.path.exists(p):
        return []
    try:
        with open(p, encoding="utf-8") as fh:
            d = json.load(fh)
    except (OSError, json.JSONDecodeError) as e:
        raise RightsSubscriptionError(f"{p}: không đọc được ({type(e).__name__}: {e})")
    recs = d.get("subscriptions") if isinstance(d, dict) else None
    if not isinstance(recs, list):
        raise RightsSubscriptionError(f"{p}: thiếu list 'subscriptions'")
    return [validate(r, f"{os.path.basename(p)}[{i}]") for i, r in enumerate(recs)]


def load_subscriptions(account, path=None, account_no=None):
    """Khai báo ĐANG HIỆU LỰC của `account` (label): bản mới nhất mỗi event_id, qty > 0.
    §12: lọc theo account; truyền `account_no` thì bản ghi lệch số tài khoản ⇒ raise (không đoán)."""
    latest = {}
    for r in load_all(path):
        if r["account"] != account:
            continue
        if account_no is not None and r["account_no"] != str(account_no):
            raise RightsSubscriptionError(f"khai báo {account}/{r['ticker']} id={r['event_id']} mang "
                                          f"account_no {r['account_no']} ≠ {account_no}")
        latest[r["event_id"]] = r
    return [r for r in latest.values() if r["subscribed_qty"] > 0]


def pending_end(sub):
    """Ngày VSDC ghi nhận (registered_date) nếu user khai, else ngày niêm yết; None = còn chờ."""
    return sub.get("registered_date") or sub.get("listing_date")


def pending_at(sub, date_iso):
    """N4: lô quyền ĐANG CHỜ ghi nhận tại `date_iso` (GDKHQ của sự kiện khác) ⇒ KHÔNG hưởng quyền.
    Chờ = đã credit trên broker (credit_date ≤ d) và chưa có ngày ghi nhận ≤ d."""
    d = str(date_iso)[:10]
    end = pending_end(sub)
    return sub["credit_date"] <= d and (end is None or d < end)


def event_key(sub):
    """Khoá fill tổng hợp mang cửa sổ chờ ⇒ consumer quyết N4 thuần từ khoá (`exempt_from`)."""
    return f"{KEY_PREFIX}{sub['event_id']}|{sub['credit_date']}|{pending_end(sub) or ''}"


def exempt_from(key, ex_date):
    """True ⇔ `key` là fill quyền mua và lô đó ĐANG CHỜ tại `ex_date` ⇒ KHÔNG nhân hệ số sự kiện."""
    if not str(key).startswith(KEY_PREFIX):
        return False
    _eid, credit, end = str(key)[len(KEY_PREFIX):].split("|")
    d = str(ex_date)[:10]
    return credit <= d and (not end or d < end)


def fill_events(account, upto=None, path=None, account_no=None):
    """{date: [(ts, key, ticker, 'buy', qty, price)]} — cùng dạng tuple của verify_account_snapshot,
    ngày = credit_date (ngày CP về openQuantity broker), giá = giá phát hành, phí 0."""
    out = {}
    for s in load_subscriptions(account, path, account_no):
        if upto and s["credit_date"] > upto:
            continue
        out.setdefault(s["credit_date"], []).append(
            (s["credit_date"] + CREDIT_TS_SUFFIX, event_key(s), s["ticker"], "buy",
             float(s["subscribed_qty"]), s["issue_price_vnd"]))
    return out


def pending_qty(account, ticker, ex_date, credited_upto, path=None, account_no=None, subs=None):
    """Σ CP quyền của `ticker` đã nằm trong KL broker tới `credited_upto` và đang chờ tại `ex_date`."""
    subs = load_subscriptions(account, path, account_no) if subs is None else subs
    return float(sum(s["subscribed_qty"] for s in subs
                     if s["ticker"] == ticker and s["credit_date"] <= str(credited_upto)[:10]
                     and pending_at(s, ex_date)))


def _write_atomic(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def _account_no(account):
    from park_holdings import account_profile
    try:
        return str(account_profile(account)["account_id"])
    except SystemExit as e:
        raise RightsSubscriptionError(str(e))


def record(account, ticker, event_id, event_hash_seen, subscribed_qty, issue_price, payment_date,
           decided_by, at, source, credit_date=None, registered_date=None, listing_date=None, note="",
           fetch=None, path=None, account_no=None):
    """Validate với dòng quyền mua HIỆN TẠI trên BQ rồi append. Raise RightsSubscriptionError."""
    import lag_rights_exit_hold as rh
    t = str(ticker).strip().upper()
    if not str(source or "").strip():
        raise RightsSubscriptionError("--source bắt buộc (link/trích tin nhắn user — provenance, §20)")
    rows = [r for r in (fetch or rh.fetch_rights_rows)([t]) if str(r.get("id")) == str(event_id)]
    if len(rows) != 1:
        raise RightsSubscriptionError(f"không thấy đúng 1 dòng quyền mua id={event_id} của {t} trên BQ "
                                      f"(thấy {len(rows)})")
    r = rows[0]
    if not rh._is_live_rights(r):
        raise RightsSubscriptionError(f"id={event_id} không phải quyền mua còn hiệu lực")
    h = rh.event_hash(r)
    if str(event_hash_seen).strip() != h:
        raise RightsSubscriptionError(f"event_hash {event_hash_seen!r} ≠ hiện tại {h!r} — sự kiện đã đổi "
                                      "sau tin user đã xem; hỏi lại user, KHÔNG ghi")
    ex = str(r.get("exright_date") or "")[:10]
    if not ex:
        raise RightsSubscriptionError(f"id={event_id} CHƯA có GDKHQ trên BQ — chưa khai được lô quyền")
    from rights_issue_alert import issue_price as _bq_px
    bq_px = _bq_px(r)
    if bq_px and abs(bq_px - float(issue_price)) > ISSUE_PRICE_TOL_VND:
        raise RightsSubscriptionError(f"giá phát hành khai {float(issue_price):,.0f} ≠ BQ {bq_px:,.0f}")
    acc_no = str(account_no) if account_no is not None else _account_no(account)
    rec = {"account": account, "account_no": acc_no, "ticker": t, "event_id": str(event_id),
           "event_hash": h, "exright_date": ex, "exercise_ratio": float(r["exercise_ratio"]),
           "issue_price_vnd": float(issue_price),
           "issue_price_source": "bq+user" if bq_px else "user (BQ chưa có giá)",
           "subscribed_qty": int(subscribed_qty), "payment_date": payment_date,
           "credit_date": credit_date or payment_date, "registered_date": registered_date,
           "listing_date": listing_date, "decided_by": decided_by, "at": at, "source": source,
           "note": note, "kind": KIND,
           "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    rec = validate(rec, "khai báo mới")
    p = path or subscriptions_path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p + ".lock", "a") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        load_all(p)                                  # file hiện có phải hợp lệ trước khi nối thêm
        raw = []
        if os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                raw = json.load(fh)["subscriptions"]
        _write_atomic(p, {"subscriptions": raw + [rec]})
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--record", action="store_true")
    for k in ("account", "ticker", "event-id", "event-hash", "payment-date", "credit-date",
              "registered-date", "listing-date", "decided-by", "at", "source"):
        ap.add_argument("--" + k)
    ap.add_argument("--subscribed-qty", type=int)
    ap.add_argument("--issue-price", type=float)
    ap.add_argument("--note", default="")
    a = ap.parse_args(argv)
    try:
        if a.show:
            recs = load_subscriptions(a.account) if a.account else load_all()
            print(json.dumps(recs, ensure_ascii=False, indent=1))
            return 0
        if a.record:
            need = ("account", "ticker", "event_id", "event_hash", "subscribed_qty", "issue_price",
                    "payment_date", "decided_by", "at", "source")
            missing = [k for k in need if getattr(a, k) in (None, "")]
            if missing:
                ap.error("thiếu " + ", ".join("--" + m.replace("_", "-") for m in missing))
            rec = record(a.account, a.ticker, a.event_id, a.event_hash, a.subscribed_qty, a.issue_price,
                         a.payment_date, a.decided_by, a.at, a.source, a.credit_date,
                         a.registered_date, a.listing_date, a.note)
            print(json.dumps(rec, ensure_ascii=False))
            return 0
        ap.error("cần --show / --record")
    except (RightsSubscriptionError, OSError, RuntimeError) as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
