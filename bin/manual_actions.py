#!/usr/bin/env python3
"""Sổ LỆNH TAY ĐÃ KHAI của user (ngoài plan) — khai MỘT lần, mọi consumer biết.

Vì sao (ca thật 29/10/2026, kb/projects/manual-deviation-process-20261029.md): user bán tay SCL
14:26 (SpaceX 800cp, ZaloPay 500cp @29.600). Statement DNSE (email ~16:30) chưa về ⇒
`daily_nav_snapshot` chặn rc=5 cả 2 TK (`qty_unexplained` SCL −800/−500) ⇒ NAV 29/10 null, dòng
tiền kẹt `pending_flows`, EOD report 🚨, plan-drift/DollarBill "KHÔNG KIỂM ĐƯỢC" — cho đúng việc
user đã chủ động làm. Tiền lệ DRI 21/10 chỉ gỡ được khi statement về.

NGUYÊN TẮC: khai ≠ bằng chứng; khai chỉ là CHỈ MỤC tới bằng chứng. Một dòng khai chỉ được cổng KL
dùng khi `verify` đã đọc SỐNG order-history DNSE (`dnse_api.order_history`, lọc ĐÚNG tiểu khoản
§12 qua `accountNo` của envelope) và lưu NGUYÊN bản ghi lệnh broker vào `verification.broker_order`.
Lúc dùng, `gate_fills` dựng lại mã/chiều/KL/ngày/tiểu khoản TỪ bản ghi broker đó (không tin trường
tóm tắt) — lệch bất kỳ bit nào ⇒ dòng đó KHÔNG được tính (fail-closed), phần dư vẫn chặn rc=5.

File: `<WC_ROOT>/data/user_manual_actions.json` (`MIKE_MANUAL_ACTIONS_FILE` đổi đường dẫn — selfcheck/
sandbox). Không có file / sổ rỗng ⇒ mọi hàm trả rỗng ⇒ consumer y hệt bản cũ (INERT). File hỏng /
schema sai ⇒ `ManualActionsError` — consumer fail-closed (cùng hợp đồng `rights_subscription`).
Ghi atomic (tmp + os.replace) dưới flock (§5).

Consumer: exdate_frame.net_fills_journal_and_broker (⇒ daily_nav_snapshot, compute_active_nav) ·
park_holdings.statement_extra_sells · broker_fill_confirm.reconcile_lines / eod_trading_report.sh ·
plan_position_drift_check · bq_freshness_check.sh (prompt DollarBill, lệnh `note`).
Dòng tiền ngoài plan (rút/nạp Trứng vàng) KHÔNG nằm ở đây — vẫn là `data/account_cash_flows.json`.

    python3 bin/manual_actions.py add --date 2026-10-29 --time 14:26:56 --account SpaceX \
        --ticker SCL --side sell --qty 800 --price 29600 --order-id 20261029_344271 \
        --source "user Discord 29/10 14:30 + DNSE order_history" [--verify]
    python3 bin/manual_actions.py verify [--date D] [--account A]   # đọc SỐNG DNSE, ghi kết quả
    python3 bin/manual_actions.py list [--date D] [--account A] [--json]
    python3 bin/manual_actions.py note --account A --date D          # khối prompt DollarBill
"""
import argparse
import contextlib
import datetime as dt
import fcntl
import json
import os
import sys
import tempfile
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wc_paths  # noqa: E402
WC_ROOT = wc_paths.find_wc_root(__file__)

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
SCHEMA_VERSION = 1
_SIDE_BROKER = {"NB": "buy", "NS": "sell"}
_REQ = ("id", "date", "time_ict", "account", "account_no", "ticker", "side", "qty", "price",
        "broker_order_id", "source", "declared_at", "verification")
_STATUSES = ("UNVERIFIED", "VERIFIED", "REJECTED")


class ManualActionsError(ValueError):
    pass


def ledger_path(wc_root=None):
    return (os.environ.get("MIKE_MANUAL_ACTIONS_FILE")
            or os.path.join(wc_root or WC_ROOT, "data", "user_manual_actions.json"))


def _norm_acct(x):
    s = str(x).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s.lstrip("0") or "0"


def _validate(rec, where):
    if not isinstance(rec, dict):
        raise ManualActionsError(f"{where}: không phải object")
    miss = [k for k in _REQ if k not in rec]
    if miss:
        raise ManualActionsError(f"{where}: thiếu trường {miss}")
    try:
        dt.date.fromisoformat(rec["date"])
        dt.time.fromisoformat(rec["time_ict"])
    except (TypeError, ValueError) as e:
        raise ManualActionsError(f"{where}: date/time_ict sai dạng ({e})")
    if rec["side"] not in ("buy", "sell"):
        raise ManualActionsError(f"{where}: side={rec['side']!r} (chỉ buy/sell)")
    if not isinstance(rec["qty"], int) or isinstance(rec["qty"], bool) or rec["qty"] <= 0:
        raise ManualActionsError(f"{where}: qty={rec['qty']!r} phải là số nguyên > 0")
    if not isinstance(rec["price"], (int, float)) or rec["price"] <= 0:
        raise ManualActionsError(f"{where}: price={rec['price']!r} phải > 0")
    if not str(rec["ticker"]).isupper() or not str(rec["broker_order_id"]).strip():
        raise ManualActionsError(f"{where}: ticker phải VIẾT HOA, broker_order_id không rỗng")
    v = rec["verification"]
    if not isinstance(v, dict) or v.get("status") not in _STATUSES:
        raise ManualActionsError(f"{where}: verification.status phải thuộc {_STATUSES}")


def load_all(path=None):
    """Toàn bộ dòng khai (đã validate). Không có file ⇒ []. Hỏng ⇒ ManualActionsError."""
    p = path or ledger_path()
    if not os.path.exists(p):
        return []
    try:
        with open(p, encoding="utf-8") as f:
            obj = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise ManualActionsError(f"{p}: không đọc được ({type(e).__name__}: {e})")
    if not isinstance(obj, dict) or obj.get("schema_version") != SCHEMA_VERSION \
            or not isinstance(obj.get("actions"), list):
        raise ManualActionsError(f"{p}: cần {{schema_version: {SCHEMA_VERSION}, actions: [...]}}")
    seen_id, seen_oid = set(), set()
    for i, rec in enumerate(obj["actions"]):
        _validate(rec, f"{p} actions[{i}]")
        oid = (_norm_acct(rec["account_no"]), str(rec["broker_order_id"]))
        if rec["id"] in seen_id or oid in seen_oid:
            # Hai dòng cùng một lệnh broker = đếm đôi KL — không chọn hộ, chặn.
            raise ManualActionsError(f"{p} actions[{i}]: trùng id/broker_order_id {rec['id']}")
        seen_id.add(rec["id"])
        seen_oid.add(oid)
    return obj["actions"]


def evidence_check(rec, account_no):
    """(ok, lý do). Dựng lại mọi bit TỪ bản ghi broker đã lưu — không tin trường tóm tắt."""
    v = rec.get("verification") or {}
    if v.get("status") != "VERIFIED":
        return False, f"chưa xác nhận broker (status={v.get('status')})"
    bo = v.get("broker_order")
    if not isinstance(bo, dict):
        return False, "thiếu bản ghi lệnh broker"
    if not account_no or _norm_acct(account_no) != _norm_acct(rec["account_no"]):
        return False, f"tiểu khoản khai {rec['account_no']} ≠ tiểu khoản đang xét {account_no}"
    if _norm_acct(v.get("envelope_account_no", "")) != _norm_acct(rec["account_no"]):
        return False, f"order-history thuộc tiểu khoản {v.get('envelope_account_no')} (§12)"
    checks = (
        (str(bo.get("id")) == str(rec["broker_order_id"]), "mã lệnh"),
        (str(bo.get("symbol", "")).upper() == rec["ticker"], "mã CK"),
        (_SIDE_BROKER.get(str(bo.get("side", "")).upper()) == rec["side"], "chiều"),
        (str(bo.get("transDate", ""))[:10] == rec["date"], "ngày giao dịch"),
        (_int(bo.get("fillQuantity")) == rec["qty"], "KL khớp"),
    )
    bad = [name for ok, name in checks if not ok]
    if bad:
        return False, f"bản ghi broker lệch khai ở: {', '.join(bad)}"
    return True, ""


def _int(x):
    try:
        f = float(x)
    except (TypeError, ValueError):
        return None
    return int(f) if f == int(f) else None


def broker_order_num(oid):
    """'20261029_344271' → '344271' (dạng child_oid trong journal bot)."""
    return str(oid).rsplit("_", 1)[-1]


def gate_fills(account_label, account_no, after_date, upto_date, path=None, notes_out=None,
               wc_root=None):
    """{ngày: [{ticker, side, qty, price, order_num, id, time_ict}]} — CHỈ dòng VERIFIED hợp lệ
    của ĐÚNG account (label + account_no, §12), ngày ∈ (after_date, upto_date].
    Dòng khai của account này mà KHÔNG hợp lệ ⇒ ghi lý do vào `notes_out`, không tính."""
    out = {}
    for rec in load_all(path or ledger_path(wc_root)):
        if rec["account"] != account_label or not (after_date < rec["date"] <= upto_date):
            continue
        ok, why = evidence_check(rec, account_no)
        if not ok:
            if notes_out is not None:
                notes_out.append(f"{rec['date']} {rec['ticker']} {rec['side']} {rec['qty']:,}cp "
                                 f"lệnh tay KHAI nhưng KHÔNG tính ({why})")
            continue
        out.setdefault(rec["date"], []).append(
            {"ticker": rec["ticker"], "side": rec["side"], "qty": rec["qty"],
             "price": float(rec["price"]), "order_num": broker_order_num(rec["broker_order_id"]),
             "id": rec["id"], "time_ict": rec["time_ict"]})
    return out


def by_key(fills):
    """[fill] → {(ticker, side): qty}."""
    agg = {}
    for f in fills:
        agg[(f["ticker"], f["side"])] = agg.get((f["ticker"], f["side"]), 0) + f["qty"]
    return agg


def statement_crosscheck(day, manual, statement_qty, journal_qty):
    """Statement đã về ⇒ statement − journal phải = KL lệnh tay đã khai cho từng (mã, chiều).
    Trả list cảnh báo (rỗng = khớp). `statement_qty`/`journal_qty`: {(ticker, side): qty}."""
    warns = []
    for k, m in sorted(by_key(manual).items()):
        extra = statement_qty.get(k, 0) - journal_qty.get(k, 0)
        if extra != m:
            warns.append(f"⚠️ {day} {k[0]} {k[1]}: lệnh tay đã khai {m:,}cp ≠ statement−journal "
                         f"{extra:,}cp — hai nguồn lệch, cần kiểm")
    return warns


# ── ghi ──────────────────────────────────────────────────────────────────────────────────────
@contextlib.contextmanager
def _locked(path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path + ".lock", "w") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        yield


def _write_atomic(path, actions):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(path)), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump({"schema_version": SCHEMA_VERSION, "actions": actions}, f,
                  ensure_ascii=False, indent=2)
        f.write("\n")
    os.chmod(tmp, 0o644)
    os.replace(tmp, path)


def _now_iso():
    return dt.datetime.now(ICT).isoformat(timespec="seconds")


def account_no_for(label, wc_root=None):
    from broker_fill_confirm import account_no_for as _a
    return _a(wc_root or WC_ROOT, label)


def add(date, time_ict, account, ticker, side, qty, price, order_id, source, note="",
        account_no=None, path=None):
    p = path or ledger_path()
    account_no = account_no or account_no_for(account)
    if not account_no:
        raise ManualActionsError(f"không tra được số tiểu khoản cho {account}")
    rec = {"id": f"MA-{date.replace('-', '')}-{account}-{ticker.upper()}-{side.upper()}-"
                 f"{broker_order_num(order_id)}",
           "date": date, "time_ict": time_ict, "account": account, "account_no": str(account_no),
           "ticker": ticker.upper(), "side": side, "qty": int(qty), "price": float(price),
           "broker_order_id": str(order_id), "source": source, "note": note,
           "declared_at": _now_iso(), "verification": {"status": "UNVERIFIED"}}
    _validate(rec, "dòng mới")
    with _locked(p):
        actions = load_all(p)
        actions.append(rec)
        tmp_check = {(_norm_acct(a["account_no"]), a["broker_order_id"]) for a in actions[:-1]}
        if (_norm_acct(rec["account_no"]), rec["broker_order_id"]) in tmp_check:
            raise ManualActionsError(f"lệnh {order_id} của {account} đã có trong sổ")
        _write_atomic(p, actions)
    return rec


def _dnse_fetch(account_no, date):
    if WC_ROOT not in sys.path:
        sys.path.insert(0, WC_ROOT)
    from dnse_api import DNSEClient
    with contextlib.redirect_stdout(sys.stderr):
        c = DNSEClient.from_credentials_file()
        return c.order_history(account_no, from_date=date, to_date=date)


def verify(date=None, account=None, path=None, fetch_fn=None, recheck=False):
    """Đối chiếu dòng khai với order-history DNSE đọc SỐNG; ghi kết quả vào sổ. Trả [(id, status, lý do)].
    `fetch_fn(account_no, date) -> envelope` — chỉ selfcheck truyền; production đọc DNSE thật."""
    p = path or ledger_path()
    fetch_fn = fetch_fn or _dnse_fetch
    results = []
    with _locked(p):
        actions = load_all(p)
        cache = {}
        for rec in actions:
            if (date and rec["date"] != date) or (account and rec["account"] != account):
                continue
            if rec["verification"].get("status") == "VERIFIED" and not recheck:
                results.append((rec["id"], "VERIFIED", "đã xác nhận trước đó"))
                continue
            key = (rec["account_no"], rec["date"])
            try:
                if key not in cache:
                    cache[key] = fetch_fn(*key)
                env = cache[key]
            except Exception as e:
                # Không đọc được broker ⇒ KHÔNG đổi trạng thái (đã VERIFIED thì giữ, chưa thì vẫn chưa).
                results.append((rec["id"], rec["verification"].get("status"),
                                f"đọc DNSE lỗi {type(e).__name__}: {e}"))
                continue
            env_acct = (env or {}).get("accountNo") if isinstance(env, dict) else None
            rows = (env or {}).get("data") if isinstance(env, dict) else None
            ver = {"verified_at": _now_iso(), "method": "dnse_api.order_history",
                   "envelope_account_no": str(env_acct) if env_acct is not None else None}
            if env_acct is None or _norm_acct(env_acct) != _norm_acct(rec["account_no"]):
                ver.update(status="REJECTED",
                           reason=f"order-history trả tiểu khoản {env_acct} ≠ {rec['account_no']} (§12)")
            elif not isinstance(rows, list):
                ver.update(status="REJECTED", reason="order-history không có mảng data")
            else:
                hit = [o for o in rows if isinstance(o, dict)
                       and str(o.get("id")) == str(rec["broker_order_id"])]
                if len(hit) != 1:
                    ver.update(status="REJECTED",
                               reason=f"order-history {rec['date']} có {len(hit)} lệnh id "
                                      f"{rec['broker_order_id']} (cần đúng 1)")
                else:
                    ver["broker_order"] = hit[0]
                    ver["status"] = "VERIFIED"
                    ok, why = evidence_check(dict(rec, verification=ver), rec["account_no"])
                    if not ok:
                        ver.pop("broker_order")
                        ver.update(status="REJECTED", reason=why, broker_order_seen=hit[0])
            rec["verification"] = ver
            results.append((rec["id"], ver["status"], ver.get("reason", "")))
        _write_atomic(p, actions)
    return results


# ── hiển thị ─────────────────────────────────────────────────────────────────────────────────
def _fmt(rec):
    v = rec["verification"]
    st = v.get("status")
    tag = "✅ broker xác nhận" if st == "VERIFIED" else f"⛔ {st}: {v.get('reason', 'chưa verify')}"
    return (f"{rec['date']} {rec['time_ict'][:5]} {rec['account']} "
            f"{'MUA' if rec['side'] == 'buy' else 'BÁN'} {rec['ticker']} {rec['qty']:,}cp "
            f"@{rec['price']:,.0f} (lệnh {rec['broker_order_id']}) — {tag}")


def report_lines(account_label, account_no, date, path=None):
    """Dòng ℹ️ cho EOD report: lệnh tay đã khai của account trong `date`. Sổ rỗng ⇒ []."""
    recs = [r for r in load_all(path) if r["account"] == account_label and r["date"] == date]
    if not recs:
        return []
    out = ["ℹ️ **Lệnh tay đã khai (đã xác nhận broker)** — user chủ động đặt ngoài plan, "
           "không phải sự cố:"]
    for r in recs:
        ok, why = evidence_check(r, account_no)
        out.append(f"  • {_fmt(r)}" if ok else
                   f"  • ⚠️ {_fmt(r)} — CHƯA được cổng KL chấp nhận ({why})")
    return out


def prompt_note(account_label, date, path=None):
    """Khối chèn prompt DollarBill: khai của `date` + phiên trước đó. Rỗng ⇒ ''."""
    if WC_ROOT not in sys.path:
        sys.path.insert(0, WC_ROOT)
    from trading_bot.vn_market import is_holiday
    d = dt.date.fromisoformat(date) - dt.timedelta(days=1)
    while d.weekday() >= 5 or is_holiday(d):
        d -= dt.timedelta(days=1)
    lo = d.isoformat()
    acct_no = account_no_for(account_label)
    recs = [r for r in load_all(path) if r["account"] == account_label and lo <= r["date"] <= date]
    if not recs:
        return ""
    ok = [r for r in recs if evidence_check(r, acct_no)[0]]
    bad = [r for r in recs if r not in ok]
    s = " LỆNH TAY ĐÃ KHAI HÔM NAY/PHIÊN GẦN NHẤT (data/user_manual_actions.json): "
    if ok:
        s += ("đã xác nhận broker — "
              + "; ".join(f"{r['date']} {'MUA' if r['side'] == 'buy' else 'BÁN'} {r['ticker']} "
                          f"{r['qty']}cp @{r['price']:,.0f}" for r in ok)
              + ". Đây là lệnh user CHỦ ĐỘNG đặt ngoài plan: dùng KL broker THẬT hiện tại làm cơ sở, "
                "KHÔNG coi là drift/bất thường, KHÔNG tự sinh lệnh để 'bù' lại.")
    if bad:
        s += (" CHƯA xác nhận broker (coi như CHƯA được giải thích, nêu trong plan note): "
              + "; ".join(f"{r['date']} {r['ticker']} {r['side']} {r['qty']}cp" for r in bad) + ".")
    return s


def main(argv=None):
    ap = argparse.ArgumentParser(description="Sổ lệnh tay đã khai của user (ngoài plan).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    for k in ("date", "time", "account", "ticker", "side", "order-id", "source"):
        a.add_argument(f"--{k}", required=True)
    a.add_argument("--qty", type=int, required=True)
    a.add_argument("--price", type=float, required=True)
    a.add_argument("--note", default="")
    a.add_argument("--verify", action="store_true", help="đọc DNSE xác nhận ngay sau khi ghi")
    v = sub.add_parser("verify")
    v.add_argument("--date")
    v.add_argument("--account")
    v.add_argument("--recheck", action="store_true", help="đọc lại cả dòng đã VERIFIED")
    lp = sub.add_parser("list")
    lp.add_argument("--date")
    lp.add_argument("--account")
    lp.add_argument("--json", action="store_true")
    n = sub.add_parser("note")
    n.add_argument("--account", required=True)
    n.add_argument("--date", required=True)
    args = ap.parse_args(argv)
    try:
        if args.cmd == "add":
            rec = add(args.date, args.time, args.account, args.ticker, args.side, args.qty,
                      args.price, args.order_id, args.source, args.note)
            print(f"đã ghi {rec['id']} (UNVERIFIED)")
            if args.verify:
                for rid, st, why in verify(args.date, args.account):
                    if rid == rec["id"]:
                        print(f"verify {rid}: {st} {why}")
            return 0
        if args.cmd == "verify":
            res = verify(args.date, args.account, recheck=args.recheck)
            for rid, st, why in res:
                print(f"{rid}: {st}" + (f" — {why}" if why else ""))
            return 0 if res and all(st == "VERIFIED" for _, st, _ in res) else 1
        if args.cmd == "list":
            recs = [r for r in load_all() if (not args.date or r["date"] == args.date)
                    and (not args.account or r["account"] == args.account)]
            if args.json:
                print(json.dumps(recs, ensure_ascii=False, indent=2))
            else:
                for r in recs:
                    print(_fmt(r))
            return 0
        if args.cmd == "note":
            s = prompt_note(args.account, args.date)
            if s:
                print(s)
            return 0
    except ManualActionsError as e:
        print(f"❌ sổ lệnh tay: {e}", file=sys.stderr)
        return 2
    return 3


if __name__ == "__main__":
    sys.exit(main())
