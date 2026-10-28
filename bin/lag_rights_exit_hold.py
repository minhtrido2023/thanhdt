#!/usr/bin/env python3
"""HOLD lệnh thoát LAG khi mã có QUYỀN MUA chưa tới GDKHQ (X1) + sổ quyết định của USER cho sự kiện
chưa có ngày (`data/lag_rights/exit_ack.json`).

Luật user 2026-10-21 (kb/current_ops.md): mã LAG đang giữ có quyền mua trong kỳ giữ ⇒ KHÔNG bán
trước ngày GDKHQ; user tự thực hiện quyền. Duyệt áp patch 2026-10-22 09:27 ICT (job
Taylor_20261022_022942; audit agents/Taylor/research/lag_rights_audit_20261022 F4/B3.3).

Sự kiện quyền mua = `tav2_bq.corporate_action` dòng event_code ISS, issue_method_code "Rights",
exercise_ratio > 0, KHÔNG huỷ (issue_status_code ≠ N và event_status ≠ not_executed), đã công bố
tới `signal_date` (public_date ≤ signal_date). Với mỗi mã sắp bị auto-exit LAG:
  • có GDKHQ và plan_date < GDKHQ        ⇒ HOLD (blocked, lý do cố định ⇒ alert dedup 1 lần)
  • có GDKHQ và plan_date ≥ GDKHQ        ⇒ không ảnh hưởng (bán bình thường, giá đã điều chỉnh)
  • CHƯA có GDKHQ, công bố ≤ UNDATED_MAX_AGE_DAYS ngày:
        - chưa có ack user khớp hash     ⇒ HOLD, lý do mang ngày ⇒ alert MỖI NGÀY đòi user quyết
        - ack HOLD khớp hash             ⇒ HOLD, lý do cố định (user đã quyết, alert 1 lần)
        - ack SELL khớp hash             ⇒ RELEASE (bán bình thường, note ghi provenance ack)
    hash gồm exright_date ⇒ khi vendor điền ngày, ack cũ hết hiệu lực, chuyển sang luật có ngày.
  • CHƯA có GDKHQ, công bố > UNDATED_MAX_AGE_DAYS ngày ⇒ coi là bản ghi treo của vendor, bỏ qua
    (in ra stdout, KHÔNG chặn) — đo 2026-10-22: 25 dòng P không ngày từ 2022 vẫn nằm trong bảng.
Lỗi đọc BQ / sổ ack ⇒ fail-closed: HOLD mọi mã liên quan, lý do nêu lỗi thật (§29) + ngày.

Ack chỉ Mike ghi, CHỈ khi user trả lời thật (§20): decided_by=user, at có múi giờ, source khác
rỗng, event_hash phải khớp sự kiện HIỆN TẠI trên BQ (user đã xem đúng sự kiện đó).

    python3 bin/lag_rights_exit_hold.py --check SCL --plan-date 2026-11-03
    python3 bin/lag_rights_exit_hold.py --record --ticker SCL --event-id <id> --event-hash <h> \
        --decision HOLD --decided-by user --at 2026-10-25T18:30:00+07:00 --source "discord <link>"
    python3 bin/lag_rights_exit_hold.py --show

Đường cắm N1 sau này (lô quyền vào sổ lô): module này chỉ quyết định CÓ chèn SELL hay không theo
mã + ngày, không đọc/sửa sổ lô ⇒ lô quyền thêm vào sổ (book LAG) sẽ đi qua cùng cổng này.
"""
import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
import sys
import tempfile
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wc_paths  # noqa: E402
WC_ROOT = wc_paths.find_wc_root(__file__)
if WC_ROOT not in sys.path:
    sys.path.insert(0, WC_ROOT)

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")
UNDATED_MAX_AGE_DAYS = 365
DECISIONS = ("HOLD", "SELL")
_HASH_FIELDS = ("id", "ticker", "exright_date", "record_date", "exercise_ratio",
                "issue_status_code", "value_per_share", "total_value", "issue_volumn")


def rights_dir():
    return os.environ.get("MIKE_LAG_RIGHTS_DIR") or os.path.join(WC_ROOT, "data", "lag_rights")


def ack_path():
    return os.path.join(rights_dir(), "exit_ack.json")


def fetch_rights_rows(tickers):
    """Dòng Rights của `tickers` từ BQ (cùng truy vấn với rights_issue_alert). Raise khi lỗi."""
    from rights_issue_alert import fetch_rights
    return fetch_rights(tickers)


def event_hash(row):
    blob = json.dumps({k: (None if row.get(k) in (None, "") else str(row.get(k))) for k in _HASH_FIELDS},
                      sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:12]


def _is_live_rights(r):
    try:
        ratio = float(r.get("exercise_ratio") or 0)
    except (TypeError, ValueError):
        ratio = 0.0
    return (r.get("issue_method_code") == "Rights" and ratio > 0
            and r.get("issue_status_code") != "N" and r.get("event_status") != "not_executed")


def load_acks(path=None):
    """list ack. Không có file ⇒ []. File hỏng ⇒ raise (caller fail-closed)."""
    p = path or ack_path()
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as fh:
        d = json.load(fh)
    acks = d.get("acks") if isinstance(d, dict) else None
    if not isinstance(acks, list):
        raise ValueError(f"{p}: thiếu list 'acks'")
    return acks


def _latest_ack(acks, ticker, event_id):
    hit = [a for a in acks if isinstance(a, dict) and str(a.get("ticker")).upper() == ticker
           and str(a.get("event_id")) == str(event_id)]
    return hit[-1] if hit else None


def evaluate(ticker, plan_date, signal_date, rows, acks, ack_error=None):
    """Thuần. Trả None (không ảnh hưởng) hoặc {action: HOLD|RELEASE, reason, note}.
    `rows` = dòng BQ của MỌI mã (lọc theo ticker ở đây); `ack_error` = chuỗi lỗi đọc sổ ack."""
    sd = dt.date.fromisoformat(signal_date)
    holds, releases = [], []
    for r in rows:
        if str(r.get("ticker")) != ticker or not _is_live_rights(r):
            continue
        pub = str(r.get("public_date") or "")[:10]
        if pub and pub > signal_date:
            continue                                   # chưa công bố tại signal_date
        ratio = float(r["exercise_ratio"])
        eid, h = r.get("id"), event_hash(r)
        ex = str(r.get("exright_date") or "")[:10] or None
        if ex:
            try:
                dt.date.fromisoformat(ex)
            except ValueError:
                holds.append(f"[{signal_date}] HOLD: quyền mua {ratio:.2%} id={eid} có GDKHQ không đọc được "
                             f"({ex!r}) — fail-closed, kiểm dữ liệu corporate_action")
                continue
            if plan_date < ex:
                holds.append(f"HOLD tới GDKHQ quyền mua {ex} ({ratio:.2%}, id={eid}) — luật user 21/10: "
                             f"LAG không bán trước GDKHQ; tự bán lại từ plan ≥ {ex}")
            continue
        try:
            age = (sd - dt.date.fromisoformat(pub)).days if pub else None
        except ValueError:
            age = None
        if age is not None and age > UNDATED_MAX_AGE_DAYS:
            print(f"  [rights-hold] {ticker}: bỏ qua quyền mua chưa có ngày id={eid} công bố {pub} "
                  f"(> {UNDATED_MAX_AGE_DAYS} ngày — bản ghi treo của vendor)")
            continue
        ask = (f"[{signal_date}] HOLD quyền mua {ratio:.2%} CHƯA có GDKHQ (công bố {pub or '?'}) — "
               f"CẦN USER QUYẾT hold/sell: ack id={eid} h={h}")
        if ack_error:
            holds.append(f"{ask} | sổ ack không đọc được: {ack_error}")
            continue
        a = _latest_ack(acks, ticker, eid)
        if a is None:
            holds.append(f"{ask} | ghi: lag_rights_exit_hold.py --record --ticker {ticker} --event-id {eid} "
                         f"--event-hash {h} --decision HOLD|SELL --decided-by user --at <ISO> --source <link>")
        elif a.get("decided_by") != "user" or a.get("event_hash") != h or a.get("decision") not in DECISIONS:
            holds.append(f"{ask} | ack {a.get('at')} không dùng được (decided_by={a.get('decided_by')!r}, "
                         f"hash ack={a.get('event_hash')!r} ≠ {h} hoặc decision lạ) — sự kiện đã đổi, hỏi lại user")
        elif a["decision"] == "HOLD":
            holds.append(f"HOLD quyền mua {ratio:.2%} chưa có GDKHQ (id={eid}) — user chọn HOLD lúc "
                         f"{a.get('at')} ({a.get('source')})")
        else:
            releases.append(f"user chọn SELL dù quyền mua {ratio:.2%} chưa có GDKHQ (id={eid}, ack "
                            f"{a.get('at')}, {a.get('source')})")
    if holds:
        return {"action": "HOLD", "reason": " || ".join(holds), "note": None}
    if releases:
        return {"action": "RELEASE", "reason": None, "note": "; ".join(releases)}
    return None


def holds_for(tickers, plan_date, signal_date, fetch=None, ack_file=None):
    """{ticker: evaluate(...)} cho các mã có ảnh hưởng. KHÔNG raise: lỗi BQ ⇒ HOLD mọi mã (§29)."""
    tickers = sorted({str(t) for t in tickers})
    if not tickers:
        return {}
    try:
        rows = (fetch or fetch_rights_rows)(tickers)
    except Exception as e:  # noqa: BLE001 — mọi lỗi đọc nguồn đều phải fail-closed, nêu lỗi thật
        msg = f"{type(e).__name__}: {str(e).strip()[:200]}"
        return {t: {"action": "HOLD", "note": None,
                    "reason": f"[{signal_date}] HOLD: không đọc được tav2_bq.corporate_action ({msg}) — "
                              f"không biết mã có quyền mua hay không ⇒ KHÔNG bán LAG lượt này"}
                for t in tickers}
    try:
        acks, ack_error = load_acks(ack_file), None
    except (OSError, ValueError) as e:
        acks, ack_error = [], f"{type(e).__name__}: {str(e).strip()[:120]}"
    out = {}
    for t in tickers:
        res = evaluate(t, plan_date, signal_date, rows, acks, ack_error)
        if res:
            out[t] = res
    return out


def _write_atomic(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def record(ticker, event_id, event_hash_seen, decision, decided_by, at, source, note="",
           fetch=None, ack_file=None):
    """Validate + append 1 ack. Raise ValueError khi không hợp lệ. Sự kiện phải là quyền mua
    CHƯA có ngày, còn hiệu lực, và hash khớp bản HIỆN TẠI trên BQ."""
    t = str(ticker).strip().upper()
    if not str(source or "").strip():
        raise ValueError("--source bắt buộc (link/trích tin nhắn user trả lời — provenance, §20)")
    if decision not in DECISIONS:
        raise ValueError(f"decision phải ∈ {DECISIONS}, nhận {decision!r}")
    if decided_by != "user":
        raise ValueError("decided_by phải là 'user' — ack chỉ ghi khi USER đã trả lời thật (§20)")
    at_v = dt.datetime.fromisoformat(str(at))
    if at_v.tzinfo is None:
        raise ValueError("--at phải có múi giờ (vd 2026-10-25T18:30:00+07:00)")
    rows = [r for r in (fetch or fetch_rights_rows)([t]) if str(r.get("id")) == str(event_id)]
    if len(rows) != 1:
        raise ValueError(f"không thấy đúng 1 dòng quyền mua id={event_id} của {t} trên BQ (thấy {len(rows)})")
    r = rows[0]
    if not _is_live_rights(r):
        raise ValueError(f"id={event_id} không phải quyền mua còn hiệu lực (status={r.get('issue_status_code')})")
    if r.get("exright_date"):
        raise ValueError(f"id={event_id} ĐÃ có GDKHQ {r['exright_date']} — luật 21/10 áp thẳng, ack không áp dụng")
    h = event_hash(r)
    if str(event_hash_seen).strip() != h:
        raise ValueError(f"event_hash {event_hash_seen!r} ≠ hiện tại {h!r} — sự kiện đã đổi sau tin user đã xem; "
                         "hỏi lại user, KHÔNG ghi ack")
    entry = {"ticker": t, "event_id": str(event_id), "event_hash": h, "decision": decision,
             "decided_by": "user", "at": at_v.isoformat(), "source": source, "note": note,
             "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    ap = ack_file or ack_path()
    os.makedirs(os.path.dirname(ap), exist_ok=True)
    with open(ap + ".lock", "a") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        _write_atomic(ap, {"acks": load_acks(ap) + [entry]})
    return entry


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", metavar="TICKER")
    ap.add_argument("--plan-date")
    ap.add_argument("--signal-date", default=None)
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--ticker")
    ap.add_argument("--event-id")
    ap.add_argument("--event-hash")
    ap.add_argument("--decision", choices=DECISIONS)
    ap.add_argument("--decided-by")
    ap.add_argument("--at")
    ap.add_argument("--source", default="")
    ap.add_argument("--note", default="")
    a = ap.parse_args(argv)
    try:
        if a.show:
            print(json.dumps(load_acks(), ensure_ascii=False, indent=1))
            return 0
        if a.check:
            if not a.plan_date:
                ap.error("--check cần --plan-date")
            sd = a.signal_date or dt.datetime.now(_ICT).date().isoformat()
            print(json.dumps(holds_for([a.check.upper()], a.plan_date, sd), ensure_ascii=False, indent=1))
            return 0
        if a.record:
            missing = [k for k in ("ticker", "event_id", "event_hash", "decision", "decided_by", "at", "source")
                       if not getattr(a, k)]
            if missing:
                ap.error("thiếu " + ", ".join("--" + m.replace("_", "-") for m in missing))
            e = record(a.ticker, a.event_id, a.event_hash, a.decision, a.decided_by, a.at, a.source, a.note)
            print(json.dumps(e, ensure_ascii=False))
            return 0
        ap.error("cần --check / --record / --show")
    except (ValueError, OSError, RuntimeError) as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
