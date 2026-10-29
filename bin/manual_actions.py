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


def _canon(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def exec_dir_for(path=None, wc_root=None):
    """Thư mục `execution_logs` đi cùng sổ (sổ ở `<data>/user_manual_actions.json`)."""
    return os.path.join(os.path.dirname(os.path.abspath(path or ledger_path(wc_root))),
                        "execution_logs")


def raw_log_path(exec_dir, date):
    return os.path.join(exec_dir, f"dnse_raw_{date}.jsonl")


def _raw_order_history(exec_dir, date, account_no):
    """Mọi lệnh trong bản ghi kind=order_history của ĐÚNG tiểu khoản (§12) trong dnse_raw_<date>.jsonl."""
    out, p = [], raw_log_path(exec_dir, date)
    if not os.path.exists(p):
        return out
    with open(p, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if _norm_acct(r.get("account_no", "")) != _norm_acct(account_no):   # §12 — dòng đầu tiên
                continue
            if r.get("kind") != "order_history":
                continue
            pl = r.get("payload")
            if isinstance(pl, dict) and isinstance(pl.get("data"), list):
                out.extend(o for o in pl["data"] if isinstance(o, dict))
    return out


def _filled(status):
    return str(status or "").lower().replace("_", "").replace(" ", "") in ("filled", "partiallyfilled")


def evidence_check(rec, account_no, exec_dir=None):
    """(ok, lý do). Dựng lại mọi bit TỪ bản ghi broker đã lưu — không tin trường tóm tắt — và đòi
    bản ghi đó có BẢN SAO KHỚP TỪNG BYTE trong artifact độc lập `dnse_raw_<ngày>.jsonl`
    (kind=order_history): sửa tay sổ khai không đủ để mở cổng, phải sửa luôn log thô."""
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
    if v.get("method") != "dnse_api.order_history":
        return False, f"method={v.get('method')!r} ≠ dnse_api.order_history"
    if not _filled(bo.get("orderStatus")):
        return False, f"lệnh broker ở trạng thái {bo.get('orderStatus')!r}, chưa khớp"
    if str(v.get("verified_at", ""))[:10] < str(bo.get("transDate", ""))[:10] or not v.get("verified_at"):
        return False, f"verified_at {v.get('verified_at')} sớm hơn ngày giao dịch {bo.get('transDate')}"
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
    ed = exec_dir or exec_dir_for()
    mine = [o for o in _raw_order_history(ed, rec["date"], rec["account_no"])
            if str(o.get("id")) == str(rec["broker_order_id"])]
    if not any(_canon(o) == _canon(bo) for o in mine):
        return False, (f"không có bản sao khớp từng byte của lệnh {rec['broker_order_id']} trong "
                       f"{os.path.basename(raw_log_path(ed, rec['date']))} (kind=order_history)")
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
    ed = exec_dir_for(path, wc_root)
    for rec in load_all(path or ledger_path(wc_root)):
        if rec["account"] != account_label or not (after_date < rec["date"] <= upto_date):
            continue
        ok, why = evidence_check(rec, account_no, ed)
        if not ok:
            if notes_out is not None:
                notes_out.append(f"{rec['date']} {rec['ticker']} {rec['side']} {rec['qty']:,}cp "
                                 f"lệnh tay KHAI nhưng KHÔNG tính ({why})")
            continue
        out.setdefault(rec["date"], []).append(
            {"ticker": rec["ticker"], "side": rec["side"], "qty": rec["qty"],
             "price": float(rec["price"]), "order_num": broker_order_num(rec["broker_order_id"]),
             "id": rec["id"], "time_ict": rec["time_ict"],
             "broker_order_id": str(rec["broker_order_id"])})
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


def _ops_notify(msg, day=None):
    """Đẩy MỘT cảnh báo sang kênh VẬN HÀNH (Trading Daily). KHÔNG BAO GIỜ in stdout/stderr: stderr của
    caller (daily_nav_snapshot…) bị eod_trading_report.sh gom vào NAV_SECTION của báo cáo SpaceX gửi nhà
    đầu tư — cảnh báo đối soát nội bộ không được lọt ra đó. Fail-safe: lỗi gửi không làm hỏng caller.
    Test: MIKE_MANUAL_WARN_SINK=<file> ghi nối thêm thay vì gửi; MIKE_BOT_TEST_MODE=1 ⇒ không gửi thật.
    Dedupe 1 lần/ngày/nội dung (state/manual_actions_warned.json) — NAV/park chạy nhiều lần mỗi ngày."""
    sink = os.environ.get("MIKE_MANUAL_WARN_SINK")
    if sink:
        with open(sink, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
        return True
    if os.environ.get("MIKE_BOT_TEST_MODE") == "1" or os.environ.get("PYTEST_CURRENT_TEST"):
        return False
    try:
        import hashlib
        import subprocess
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if os.path.basename(os.path.realpath(root)) != "mike" or os.path.basename(os.path.dirname(os.path.realpath(root))) != "WorkingClaude":
            return False          # worktree/sandbox copy (selfcheck) ⇒ KHÔNG gửi thật; chỉ cây production gửi
        st_path = os.path.join(root, "state", "manual_actions_warned.json")
        key = hashlib.sha1(f"{day}|{msg}".encode("utf-8")).hexdigest()[:16]
        try:
            with open(st_path, encoding="utf-8") as f:
                st = json.load(f)
        except (OSError, ValueError):
            st = {}
        if key in st:
            return False
        script = os.path.join(root, "bin", "notify_thread.sh")
        r = subprocess.run([script, msg, "trading_daily"], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=60)
        if r.returncode == 0:
            st[key] = day or ""
            os.makedirs(os.path.dirname(st_path), exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=os.path.dirname(st_path), suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(st, f)
            os.replace(tmp, st_path)
        return r.returncode == 0
    except Exception:                                            # noqa: BLE001 — fail-safe, cảnh báo không phá NAV
        return False


def emit_warnings(warns, day=None):
    """Cảnh báo statement_crosscheck phải TỚI người vận hành ở đường THÀNH CÔNG (rc=0) mà KHÔNG lọt vào
    báo cáo nhà đầu tư: gửi kênh Trading Daily (`_ops_notify`), không in stdout/stderr. Trả lại `warns`
    (caller vẫn đưa vào `notes` cho đường rc=5)."""
    for w in warns:
        _ops_notify(w, day)
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


ORDER_PAGE_SIZE, ORDER_MAX_PAGES = 100, 20


def _dnse_fetch(account_no, date):
    """order_history của `date`, đọc HẾT các trang (pageIndex bắt đầu từ 0 — ĐO THẬT 29/10: pageIndex=1 trả trang rỗng). Một trang đầy ⇒ đọc
    tiếp; trang ngắn ⇒ hết. Trang lặp y nguyên (API lờ phân trang) hoặc chạm trần ORDER_MAX_PAGES
    mà vẫn đầy ⇒ raise — không kết luận "không có lệnh" từ danh sách có thể cụt."""
    if WC_ROOT not in sys.path:
        sys.path.insert(0, WC_ROOT)
    from dnse_api import DNSEClient
    with contextlib.redirect_stdout(sys.stderr):
        c = DNSEClient.from_credentials_file()
        rows, seen, env0 = [], set(), None
        for page in range(0, ORDER_MAX_PAGES):
            env = c.order_history(account_no, from_date=date, to_date=date,
                                  page_size=ORDER_PAGE_SIZE, page_index=page)
            env0 = env0 if env0 is not None else env
            part = env.get("data") if isinstance(env, dict) else None
            if not isinstance(part, list):
                return env
            ids = [str(o.get("id")) for o in part if isinstance(o, dict)]
            if page > 0 and ids and set(ids) <= seen:
                raise RuntimeError(f"order_history trang {page + 1} lặp trang trước — API lờ pageIndex")
            seen.update(ids)
            rows.extend(part)
            if len(part) < ORDER_PAGE_SIZE:
                return dict(env0, data=rows, _pages=page + 1, _page_size=ORDER_PAGE_SIZE)
        raise RuntimeError(f"order_history còn đầy sau {ORDER_MAX_PAGES} trang × {ORDER_PAGE_SIZE} "
                           f"— không đọc hết được")


def _archive_raw(exec_dir, label, date, env):
    """Ghi NỐI-THÊM nguyên envelope order_history vào dnse_raw_<date>.jsonl (kind=order_history,
    account_no = tiểu khoản envelope trả về — §12). Đây là artifact độc lập evidence_check đòi."""
    rec = {"ts": _now_iso()[:19], "kind": "order_history", "account_no": str(env["accountNo"]),
           "account_label": label, "payload": env}
    os.makedirs(exec_dir, exist_ok=True)
    with open(raw_log_path(exec_dir, date), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def verify(date=None, account=None, path=None, fetch_fn=None, recheck=False):
    """Đối chiếu dòng khai với order-history DNSE đọc SỐNG; ghi kết quả vào sổ. Trả [(id, status, lý do)].
    `fetch_fn(account_no, date) -> envelope` — chỉ selfcheck truyền; production đọc DNSE thật."""
    p = path or ledger_path()
    fetch_fn = fetch_fn or _dnse_fetch
    results = []
    with _locked(p):
        actions = load_all(p)
        cache, archived, ed = {}, set(), exec_dir_for(p)
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
            pages = (env or {}).get("_pages", 1) if isinstance(env, dict) else 1
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
                               reason=f"order-history {rec['date']} (đã đọc {pages} trang, "
                                      f"{len(rows)} lệnh) có {len(hit)} lệnh id "
                                      f"{rec['broker_order_id']} (cần đúng 1)")
                else:
                    if (rec["account_no"], rec["date"]) not in archived:
                        _archive_raw(ed, rec["account"], rec["date"], env)
                        archived.add((rec["account_no"], rec["date"]))
                    ver["broker_order"] = hit[0]
                    ver["status"] = "VERIFIED"
                    ver["pages_read"] = pages
                    ok, why = evidence_check(dict(rec, verification=ver), rec["account_no"], ed)
                    if not ok:
                        ver.pop("broker_order")
                        ver.update(status="REJECTED", reason=why, broker_order_seen=hit[0])
            rec["verification"] = ver
            results.append((rec["id"], ver["status"], ver.get("reason", "")))
        _write_atomic(p, actions)
    return results


# ── hiển thị ─────────────────────────────────────────────────────────────────────────────────
def _fmt(rec, evidence_ok=None):
    """`evidence_ok`: kết quả evidence_check nếu caller đã có — "✅ broker xác nhận" chỉ in khi bằng
    chứng THỰC SỰ qua cổng, không chỉ vì status=VERIFIED trong file."""
    v = rec["verification"]
    st = v.get("status")
    good = (st == "VERIFIED") if evidence_ok is None else evidence_ok
    tag = "✅ broker xác nhận" if good else f"⛔ {st}: {v.get('reason', 'chưa verify')}"
    return (f"{rec['date']} {rec['time_ict'][:5]} {rec['account']} "
            f"{'MUA' if rec['side'] == 'buy' else 'BÁN'} {rec['ticker']} {rec['qty']:,}cp "
            f"@{rec['price']:,.0f} (lệnh {rec['broker_order_id']}) — {tag}")


def report_lines(account_label, account_no, date, path=None):
    """Dòng ℹ️ cho EOD report: lệnh tay đã khai của account trong `date`. Sổ rỗng ⇒ []."""
    recs = [r for r in load_all(path) if r["account"] == account_label and r["date"] == date]
    if not recs:
        return []
    ed = exec_dir_for(path)
    chk = [(r,) + evidence_check(r, account_no, ed) for r in recs]
    n_ok = sum(1 for _r, ok, _w in chk if ok)
    # Tiêu đề "(đã xác nhận broker)" chỉ khi có ÍT NHẤT 1 dòng qua cổng — toàn UNVERIFIED thì không
    # được nói "đã xác nhận" (báo cáo gửi nhà đầu tư).
    out = ["ℹ️ **Lệnh tay đã khai (đã xác nhận broker)** — user chủ động đặt ngoài plan, "
           "không phải sự cố:" if n_ok else
           "⚠️ **Lệnh tay đã khai nhưng CHƯA có dòng nào được broker xác nhận** — chưa được cổng KL chấp nhận:"]
    for r, ok, why in chk:
        out.append(f"  • {_fmt(r, True)}" if ok else
                   f"  • ⚠️ {_fmt(r, False)} — CHƯA được cổng KL chấp nhận ({why})")
    return out


def prompt_note(account_label, date, path=None, account_no=None):
    """Khối chèn prompt DollarBill: khai của `date` + phiên trước đó. Rỗng ⇒ ''."""
    if WC_ROOT not in sys.path:
        sys.path.insert(0, WC_ROOT)
    from trading_bot.vn_market import is_holiday
    d = dt.date.fromisoformat(date) - dt.timedelta(days=1)
    while d.weekday() >= 5 or is_holiday(d):
        d -= dt.timedelta(days=1)
    lo = d.isoformat()
    acct_no = account_no or account_no_for(account_label)
    ed = exec_dir_for(path)
    recs = [r for r in load_all(path) if r["account"] == account_label and lo <= r["date"] <= date]
    if not recs:
        return ""
    ok = [r for r in recs if evidence_check(r, acct_no, ed)[0]]
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
