#!/usr/bin/env python3
"""Cổng nhất quán plan LAG + cảnh báo ứng viên LAG hợp lệ bị hoãn đúng phiên chuẩn.

⚠️ CHỈ ĐỌC plan JSON (+ tuỳ chọn đối chiếu CSV khuyến nghị offline). KHÔNG sửa plan, KHÔNG đặt
   lệnh, KHÔNG unpark, KHÔNG gọi DNSE. Chỉ phát: (a) khối chữ cho report, (b) 1 tin Discord Trading
   Daily, (c) 1 bus event. Nguồn gốc: Taylor_20261021_102832 REPORT.md §A/§B/§5 (user duyệt
   2026-10-21) — 58% vốn LAG lỡ là WAIT_CASH, 7% là SSI 08-07 rơi im lặng.

HAI VIỆC trong một module (cùng đọc `lag_analysis.due_today[]` + `orders[]` + `deferred_orders[]`):

  CONSISTENCY_FAIL (việc 3) — mọi mã có `lag_analysis.due_today[].decision` bắt đầu bằng BUY phải
    xuất hiện trong `orders[]` (side=buy, qty>0) HOẶC `deferred_orders[]` (có `status`/lý do).
    Mã nguyên nhân: LAG_BUY_MISSING · LAG_BUY_DEFERRED_NO_REASON · LAG_BUY_ORDER_ZERO_QTY ·
    LAG_CANDIDATE_NOT_ANALYSED (đối chiếu offline `filter_lag_entry_window.filter_window`: mã phiên
    1 theo CSV mà `lag_analysis` không hề nhắc tới).
  FUNDING_ALERT (việc 2) — ứng viên BUY + entry_window_day==1 (phiên chuẩn) mà KHÔNG có lệnh mua
    thật (nằm trong deferred_orders / thiếu / qty 0) ⇒ cảnh báo ĐỎ + đề xuất cấp vốn + hạn chót.
  LAG_DD_GATE_VIOLATION (cổng DD trước plan, user duyệt 2026-10-21 22:10, job Taylor_20261021_151302)
    — lệnh MUA LAG trong orders[] (qty>0; book=="LAG", hoặc thiếu book mà mã có decision BUY trong
    lag_analysis.due_today) mà gói `data/lag_dd/<mã>_<release>.json` KHÔNG ở trạng thái CLEARED và
    KHÔNG có ack PROCEED decided_by=user khớp flags_hash (lag_dd_ack.dd_gate). Cause = `LAG_DD_<state>`
    (FLAG_NO_ACK, NO_PACK, ACK_DROP, ACK_RESEARCH, ACK_STALE, ACK_NOT_USER, PACK_UNREADABLE,
    ACK_UNREADABLE, GATE_UNAVAILABLE, NO_PLAN_DATE). Mã LAG trong lag_analysis chưa qua cổng mà
    KHÔNG có lệnh mua ⇒ dòng "⏳ chờ DD" (thông tin, không phải phát hiện). Vẫn CHỈ CẢNH BÁO như hai
    loại trên — chặn cứng là quyết định của user, chưa bật.

CHỌN WARN-và-bus, KHÔNG chặn gửi plan: send_plan_report.sh không có mẫu chặn-cứng cho kiểm tra
"nội dung" (chỉ chặn khi plan không đọc được/sai ngày/thiếu orders), và chặn 21:00 sẽ làm user
không thấy plan để duyệt — tệ hơn là gửi kèm cảnh báo đỏ ngay trong report.

§26: so khớp ticker/side/decision sau chuẩn hoá (strip/upper/lower, số từ chuỗi), KHÔNG suy từ sự
vắng mặt một kênh. §29: lý do trong cảnh báo là TRÍCH từ trường plan đã đọc, không hardcode.
Idempotent: state `mike/state/lag_plan_check/<account>_<plan_date>.json`, mỗi (loại|mã|nguyên nhân)
chỉ phát 1 lần; chỉ ghi "đã phát" SAU khi cả Discord lẫn bus trả rc=0.

Mã thoát: 0 sạch · 2 có phát hiện (KHÔNG phải lỗi script — cùng quy ước plan_position_drift_check)
· 1 lỗi đọc/ghi.

    python3 bin/lag_plan_consistency_check.py --account SpaceX --plan-file <plan.json> \
        [--report-block] [--json] [--dry-run] [--csv <recs.csv>]
"""
import argparse
import fcntl
import json
import math
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)

CHANNEL = "trading_daily"
AGENT = "Wags"
SUBPROC_TIMEOUT_S = 60
APPROVAL_DEADLINE = "08:45 ICT (preflight_check)"
# Cùng tập TAKE với lag_plan_calendar_check.py (hợp đồng kb/context_planning_mini.md: decision ∈ BUY/DEFER/SKIP):
# DEFER/WAIT_CASH/BUY_DEFERRED = ĐÚNG ca thiếu tiền ở phiên chuẩn (58% vốn lỡ) ⇒ vẫn phải có lệnh hoặc mục hoãn có lý do.
_RE_BUY = re.compile(r"^\s*(BUY_DEFERRED|BUY|DEFERRED|DEFER|WAIT_CASH|RESIDUAL|ORDER)\b", re.I)


def _env(name, default):
    return os.environ.get(name) or default


def _tk(x):
    return str(x or "").strip().upper()


def _num(x):
    """Số từ int/float/chuỗi ('1,234.5', '10.0'); không đọc được ⇒ None (KHÔNG đoán 0)."""
    if isinstance(x, bool):
        return None
    if isinstance(x, (int, float)):
        return float(x) if math.isfinite(x) else None
    try:
        v = float(str(x).strip().replace(",", ""))
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def _is_buy_decision(d):
    return bool(_RE_BUY.match(str(d or "")))


def _is_buy_side(o):
    return str(o.get("side") or "").strip().lower() == "buy"


def _window_day(c, plan_date):
    """entry_window_day chuẩn hoá; thiếu trường ⇒ suy từ entry_window_date == plan_date (schema
    08-07 không có entry_window_day). Không suy được ⇒ None (không coi là phiên chuẩn)."""
    n = _num(c.get("entry_window_day"))
    if n is not None:
        return int(n)
    if plan_date and str(c.get("entry_window_date") or "").strip() == str(plan_date):
        return 1
    return None


def _deferred_reason(d):
    return str(d.get("deferred_reason") or d.get("reason") or "").strip()


def _need_vnd(d, order=None):
    for src in (d, order or {}):
        for k in ("total_with_fee_vnd", "estimated_cost_vnd", "need_vnd"):
            v = _num(src.get(k))
            if v:
                return v
        q, p = _num(src.get("qty")), _num(src.get("limit_price_vnd") or src.get("ref_price"))
        if q and p:
            return q * p
    return None


def _walk_tickers(x):
    """Mọi giá trị khoá "ticker" ở bất kỳ độ sâu nào trong lag_analysis (schema do LLM viết, đổi
    giữa các mùa) — dùng để biết mã nào plan ĐÃ nhắc tới, không phụ thuộc tên khoá chứa danh sách."""
    if isinstance(x, dict):
        for k, v in x.items():
            if k == "ticker":
                yield _tk(v)
            else:
                yield from _walk_tickers(v)
    elif isinstance(x, list):
        for v in x:
            yield from _walk_tickers(v)


def _crosscheck_day1(plan, csv_path):
    """Mã phiên-1 theo CSV khuyến nghị (offline, không anchor) — (set|None, ghi chú)."""
    try:
        import filter_lag_entry_window as flw
        sig = plan.get("signal_date") or (plan.get("lag_analysis") or {}).get("signal_date")
        res = flw.filter_window(plan.get("plan_date"), signal_date=sig, csv_path=csv_path,
                                anchor_fetcher=None)
    except Exception as e:                       # fail-soft nhưng KHÔNG im lặng
        return None, f"đối chiếu CSV không chạy được: {type(e).__name__}: {str(e)[:160]}"
    if res.get("error") or not res.get("calendar_check", {}).get("ok"):
        why = res.get("error") or (res.get("calendar_check") or {}).get("reason")
        return None, f"đối chiếu CSV bỏ qua: {str(why)[:200]}"
    return {_tk(i["ticker"]) for i in res.get("due_today", []) if i.get("entry_window_day") == 1}, ""


def analyze(plan, csv_path=None, crosscheck=True, dd_gate=True, dd_dir=None):
    res = _analyze_lag(plan, csv_path=csv_path, crosscheck=crosscheck)
    if dd_gate:
        _dd_gate_check(plan, res, dd_dir)
    return res


def _dd_gate_check(plan, res, dd_dir=None):
    """Cổng DD: ghi LAG_DD_GATE_VIOLATION vào res["findings"], mã chờ DD vào res["dd_pending"].
    Chạy CẢ KHI lag_analysis thiếu/hỏng — lệnh mua LAG trong orders[] vẫn phải có gói DD."""
    plan_date = res["plan_date"]
    res["dd_pending"] = []
    la = plan.get("lag_analysis") if isinstance(plan.get("lag_analysis"), dict) else {}
    due = [c for c in (la.get("due_today") or []) if isinstance(c, dict)] \
        if isinstance(la.get("due_today"), list) else []
    upc = [c for c in (la.get("lag_upcoming_for_next_plans") or []) if isinstance(c, dict)] \
        if isinstance(la.get("lag_upcoming_for_next_plans"), list) else []
    buy_dec = {_tk(c.get("ticker")) for c in due if _is_buy_decision(c.get("decision"))}
    lag_buys = []
    for o in plan.get("orders") or []:
        if not isinstance(o, dict) or not _is_buy_side(o) or (_num(o.get("qty")) or 0) <= 0:
            continue
        book = _tk(o.get("book"))
        if book == "LAG" or (not book and _tk(o.get("ticker")) in buy_dec):
            lag_buys.append(_tk(o.get("ticker")))
    gate = None
    try:
        from lag_dd_ack import dd_gate as gate, BUY_OK
    except Exception as e:                       # fail-closed: không có cổng ⇒ mọi lệnh LAG đỏ
        err = f"không import được lag_dd_ack: {type(e).__name__}: {str(e)[:160]}"
    for t in sorted(set(lag_buys)):
        if not plan_date:
            cause, ev = "LAG_DD_NO_PLAN_DATE", "plan không có plan_date ⇒ không chọn được gói DD"
        elif gate is None:
            cause, ev = "LAG_DD_GATE_UNAVAILABLE", err
        else:
            g = gate(t, plan_date, directory=dd_dir)
            if g["state"] in BUY_OK:
                continue
            cause = f"LAG_DD_{g['state']}"
            ev = f"{g['evidence']}" + (f" ({os.path.basename(g['pack'])})" if g.get("pack") else "")
        res["findings"].append({"kind": "LAG_DD_GATE_VIOLATION", "cause": cause, "ticker": t,
                                "evidence": ev[:400]})
    if gate is None or not plan_date:
        return
    for src, items in (("due_today", due), ("upcoming", upc)):
        for c in items:
            t = _tk(c.get("ticker"))
            if not t or t in lag_buys or any(p["ticker"] == t for p in res["dd_pending"]):
                continue
            g = gate(t, plan_date, directory=dd_dir)
            if g["state"] not in BUY_OK:
                res["dd_pending"].append({"ticker": t, "source": src, "state": g["state"],
                                          "evidence": g["evidence"][:300]})


def _analyze_lag(plan, csv_path=None, crosscheck=True):
    plan_date = str(plan.get("plan_date") or plan.get("date") or "")
    res = {"account": plan.get("account"), "plan_date": plan_date, "findings": [], "notes": []}
    la = plan.get("lag_analysis")
    if not isinstance(la, dict):
        res["notes"].append("plan không có lag_analysis (dict) — không có gì để kiểm")
        return res
    due = la.get("due_today")
    if due is None:      # schema "ngày không có ứng viên" bỏ khoá due_today, chỉ ghi counts.due_today=0
        n = _num((la.get("counts") or {}).get("due_today") if isinstance(la.get("counts"), dict) else None)
        if n:
            res["findings"].append({
                "kind": "CONSISTENCY_FAIL", "cause": "LAG_ANALYSIS_MALFORMED", "ticker": None,
                "evidence": f"lag_analysis.counts.due_today={n:g} nhưng không có list due_today"})
            return res
        res["notes"].append("lag_analysis không có due_today (counts.due_today rỗng/0) — chỉ đối chiếu CSV")
        due = []
    elif not isinstance(due, list):
        res["findings"].append({
            "kind": "CONSISTENCY_FAIL", "cause": "LAG_ANALYSIS_MALFORMED", "ticker": None,
            "evidence": f"lag_analysis.due_today kiểu {type(due).__name__}, cần list"})
        return res

    orders = [o for o in (plan.get("orders") or []) if isinstance(o, dict)]
    deferred = [d for d in (plan.get("deferred_orders") or []) if isinstance(d, dict)]
    analysed = set(_walk_tickers(la))

    for c in due:
        if not isinstance(c, dict):
            continue
        t = _tk(c.get("ticker"))
        analysed.add(t)
        if not _is_buy_decision(c.get("decision")):
            continue
        day = _window_day(c, plan_date)
        buys = [o for o in orders if _tk(o.get("ticker")) == t and _is_buy_side(o)]
        live = [o for o in buys if (_num(o.get("qty")) or 0) > 0]
        defs = [d for d in deferred if _tk(d.get("ticker")) == t
                and str(d.get("side") or "buy").strip().lower() == "buy"]
        base = {"ticker": t, "day": day, "decision": str(c.get("decision"))[:40],
                "play_type": c.get("play_type") or c.get("tier")}
        if live:
            continue
        if buys:
            cause, ev = "LAG_BUY_ORDER_ZERO_QTY", f"orders[] có {t} nhưng qty={buys[0].get('qty')!r}"
            need = _need_vnd({}, buys[0])
        elif defs:
            d = defs[0]
            need = _need_vnd(d)
            reason = _deferred_reason(d)
            if not (reason or str(d.get("status") or "").strip()):
                cause, ev = "LAG_BUY_DEFERRED_NO_REASON", f"deferred_orders[] có {t} nhưng không status, không lý do"
            else:
                cause = "LAG_BUY_DEFERRED"
                ev = f"status={d.get('status')!r}; lý do: {reason[:300]}"
        else:
            cause, need = "LAG_BUY_MISSING", None
            ev = (f"{t} decision={c.get('decision')!r} nhưng không có trong orders[] "
                  f"({len(orders)} lệnh) lẫn deferred_orders[] ({len(deferred)} mục)")
        pt = plan.get("park_trim_proposal") or {}
        jit = plan.get("jit_unpark_proposal") or {}
        ctx = {"park_trim_decision": pt.get("decision"),
               "park_trim_blocked": [str(b)[:200] for b in (pt.get("blocked") or [])][:5],
               "jit_decision": jit.get("decision"), "jit_sell_total_vnd": jit.get("jit_sell_total_vnd"),
               "jit_sells_by_ticker": jit.get("sells_by_ticker"), "jit_blocked": jit.get("blocked"),
               "available_cash_vnd": _num((plan.get("cash_planning") or {}).get("available_cash_vnd"))}
        if cause != "LAG_BUY_DEFERRED":
            res["findings"].append(dict(base, kind="CONSISTENCY_FAIL", cause=cause, evidence=ev))
        if day == 1:
            res["findings"].append(dict(base, kind="FUNDING_ALERT", cause=cause, evidence=ev,
                                        need_vnd=need, context=ctx))

    if crosscheck:
        day1, note = _crosscheck_day1(plan, csv_path)
        if note:
            res["notes"].append(note)
        for t in sorted((day1 or set()) - analysed):
            res["findings"].append({
                "kind": "CONSISTENCY_FAIL", "cause": "LAG_CANDIDATE_NOT_ANALYSED", "ticker": t,
                "evidence": f"CSV khuyến nghị xếp {t} phiên chuẩn (entry_window_day=1) nhưng "
                            f"lag_analysis.due_today không có mục nào cho {t}"})
    return res


def _fmt_vnd(v):
    if v is None:
        return "không xác định (plan không có trường số tiền)"
    return f"{v / 1e6:,.1f}".replace(",", "_").replace(".", ",").replace("_", ".") + " triệu"


def _proposal(f, account, plan_date):
    c = f.get("context") or {}
    need, cash = f.get("need_vnd"), c.get("available_cash_vnd")
    short = max(0.0, need - cash) if need is not None and cash is not None else None
    lines = [f"  • Cần ≈ {_fmt_vnd(need)}; availableCash trong plan = {_fmt_vnd(cash)}; "
             f"thiếu ≈ {_fmt_vnd(short)} (chưa tính lệnh khác/JIT trong plan)."]
    if c.get("jit_sell_total_vnd"):
        lines.append(f"  • Plan đã có JIT {c.get('jit_decision')} {_fmt_vnd(_num(c['jit_sell_total_vnd']))} "
                     f"từ {sorted((c.get('jit_sells_by_ticker') or {}).keys())} mà mã này vẫn không có lệnh.")
    if c.get("park_trim_blocked") or str(c.get("park_trim_decision") or "").startswith("BLOCKED"):
        lines.append(f"  • park_trim: {c.get('park_trim_decision')} — {c.get('park_trim_blocked')}")
    amt = "mức thiếu" if short is None else f"≈ {math.ceil(short / 1e6)} triệu"
    lines.append(f"  • ĐỀ XUẤT (chưa thực hiện): unpark JIT {amt} từ sổ PARK — chạy "
                 f"`compute_jit_unpark.py --account {account} --plan <plan {plan_date}>` để lấy mã bán "
                 f"pro-rata, rồi merge + duyệt lại plan. HẠN CHÓT: {APPROVAL_DEADLINE} {plan_date} "
                 f"(bot đặt 09:05; sau đó chỉ còn phiên 2/3 với trần anchor).")
    return lines


def render(res, pending=True):
    acct, d = res["account"], res["plan_date"]
    out = []
    alerts = [f for f in res["findings"] if f["kind"] == "FUNDING_ALERT"]
    fails = [f for f in res["findings"] if f["kind"] == "CONSISTENCY_FAIL"]
    ddv = [f for f in res["findings"] if f["kind"] == "LAG_DD_GATE_VIOLATION"]
    if ddv:
        out.append(f"🔴 **LAG {acct} {d}: lệnh MUA LAG CHƯA QUA CỔNG DD** (cần gói CLEARED hoặc user "
                   f"trả lời PROCEED — data/lag_dd)")
        for f in ddv:
            out.append(f"- {f['ticker']} — {f['cause']}: {f['evidence']}")
    if alerts:
        out.append(f"🔴 **LAG {acct} {d}: ứng viên hợp lệ KHÔNG có lệnh ở PHIÊN CHUẨN**")
        for f in alerts:
            out.append(f"- **{f['ticker']}** ({f.get('play_type')}) — {f['cause']}: {f['evidence']}")
            out.extend(_proposal(f, acct, d))
    if fails:
        out.append(f"🔴 **Plan {acct} {d} KHÔNG nhất quán (LAG)**")
        for f in fails:
            out.append(f"- {f['cause']}: {f['ticker'] or '-'} — {f['evidence']}")
    if pending:
        out.extend(render_pending(res))
    return out


def render_pending(res):
    pend = res.get("dd_pending") or []
    if not pend:
        return []
    out = [f"⏳ **Chờ DD — đứng NGOÀI plan {res['plan_date']}** (user chưa trả lời / chưa có gói):"]
    for p in pend:
        out.append(f"- {p['ticker']} [{p['source']}] {p['state']}: {p['evidence']}")
    return out


# ── state + phát ─────────────────────────────────────────────────────────────────────────────
def _state_dir():
    return _env("MIKE_LAGCHK_STATE_DIR", os.path.join(ROOT, "state", "lag_plan_check"))


def _key(f):
    return f"{f['kind']}|{f['ticker']}|{f['cause']}"


def _run(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=SUBPROC_TIMEOUT_S)
        if r.returncode:
            print(f"  ❌ {os.path.basename(cmd[0])} rc={r.returncode}: "
                  f"{(r.stderr or r.stdout or '').strip()[:200]}", file=sys.stderr)
        return r.returncode
    except (OSError, subprocess.TimeoutExpired) as e:
        print(f"  ❌ {os.path.basename(cmd[0])}: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


def emit(res, trace_id=None):
    """Phát Discord + bus cho phát hiện MỚI (chưa có trong state). Trả số mục đã phát."""
    sd = _state_dir()
    os.makedirs(sd, exist_ok=True)
    path = os.path.join(sd, f"{res['account']}_{res['plan_date']}.json")
    with open(os.path.join(sd, f".lock-{res['account']}_{res['plan_date']}"), "a") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        try:
            with open(path, encoding="utf-8") as fh:
                sent = set(json.load(fh).get("sent", []))
        except (OSError, ValueError):
            sent = set()
        new = [f for f in res["findings"] if _key(f) not in sent]
        if not new:
            return 0
        sub = dict(res, findings=new)
        msg = "\n".join(render(sub, pending=False))   # "chờ DD" chỉ vào report, không vào tin cảnh báo
        notify = _env("MIKE_LAGCHK_NOTIFY", os.path.join(HERE, "notify_thread.sh"))
        bus = _env("MIKE_LAGCHK_APPEND_EVENT", os.path.join(HERE, "append_event.sh"))
        topic = f"lag-plan-check-{res['account']}-{res['plan_date']}"
        payload = json.dumps({"account": res["account"], "plan_date": res["plan_date"],
                              "findings": new, "report_lines": msg.splitlines(),
                              "mode": "CHỈ CẢNH BÁO — không đổi lệnh/không unpark"},
                             ensure_ascii=False, default=str)
        rc1 = _run([notify, msg, CHANNEL])
        rc2 = _run([bus, AGENT, "finding", topic, payload] + ([trace_id] if trace_id else []))
        if rc1 == 0 and rc2 == 0:
            fd, tmp = tempfile.mkstemp(dir=sd, suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump({"sent": sorted(sent | {_key(f) for f in new})}, fh)
            os.replace(tmp, path)
            return len(new)
        return -1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--account", required=True)
    ap.add_argument("--plan-file", required=True)
    ap.add_argument("--csv", default=None, help="CSV khuyến nghị cho đối chiếu (mặc định theo signal_date)")
    ap.add_argument("--no-crosscheck", action="store_true")
    ap.add_argument("--no-dd-gate", action="store_true", help="bỏ cổng DD (chỉ để chẩn đoán)")
    ap.add_argument("--dry-run", action="store_true", help="không Discord/bus/state")
    ap.add_argument("--report-block", action="store_true", help="in khối chữ cho report")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        with open(a.plan_file, encoding="utf-8") as fh:
            plan = json.load(fh)
    except (OSError, ValueError) as e:
        print(f"lỗi đọc plan {a.plan_file}: {e}", file=sys.stderr)
        return 1
    if not isinstance(plan, dict) or _tk(plan.get("account")) != _tk(a.account):
        print(f"plan.account={plan.get('account') if isinstance(plan, dict) else '?'!r} "
              f"≠ --account {a.account!r}", file=sys.stderr)
        return 1
    res = analyze(plan, csv_path=a.csv, crosscheck=not a.no_crosscheck, dd_gate=not a.no_dd_gate)
    for n in res["notes"]:
        print(f"  ℹ {n}", file=sys.stderr)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    if a.report_block:
        print("\n".join(render(res) if res["findings"] else
                        [f"✅ LAG nhất quán ({a.account}): mọi mã BUY đều có lệnh/lý do hoãn, lệnh LAG đều qua cổng DD."]
                        + render_pending(res)))
    if not res["findings"]:
        return 0
    if not a.dry_run:
        n = emit(res, trace_id=os.environ.get("MIKE_LAGCHK_TRACE_ID"))
        if n < 0:
            print("  ⚠ phát Discord/bus lỗi — sẽ thử lại lượt sau (chưa ghi state)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
