#!/usr/bin/env python3
"""Checker cơ học: lịch vào lệnh + quyết định DD của book LAG trong plan JSON phải khớp CODE.

⚠️ CHỈ ĐỌC. Không sửa plan, không đặt lệnh, không gọi DNSE/BQ. Không đổi ngưỡng/cổng DD nào.

VÌ SAO CÓ FILE NÀY (job Taylor_20261021_114050, user duyệt 21/10; bằng chứng:
`agents/Taylor/research/lag_entry_window_width_20261021/REPORT.md` §A):
  · Ca 24-27/07: plan SpaceX 07-24 ghi "T+2 entry 07-25" (THỨ BẢY); plan SpaceX 07-27 ghi "CỬA SỔ
    ĐÃ ĐÓNG" trong khi plan ZaloPay CÙNG NGÀY coi 07-27 là phiên chuẩn và mua VPB. SpaceX mất 4
    slot (AGR/BSI/FTS/HCM). LLM tự cộng T+n — `filter_lag_entry_window.py` đã có từ 08-04 nhưng
    không ai KIỂM plan có thật dùng đúng kết quả của nó.
  · Ca 28/07: ZaloPay loại EVF/PSI/VCI "FLOOR_FAIL — skip", SpaceX xếp VALID. Đo: DD chạy MỘT lần
    ở engine, cả 2 CSV (07-24, 07-27) in cùng "⚠ cờ chất lượng FLOOR_FAIL" + lăng kính CHEAP; lệch
    đến từ (a) plan ZaloPay 07-28 đọc CSV signal 07-24 (cũ 1 phiên) và (b) diễn giải FLOOR_FAIL
    thành cổng cứng, trái luật (context_planning_ext.md § "FLOOR_FAIL" + sector_valuation_lens.py).

NGUỒN SỰ THẬT (không có số nào do checker tự suy):
  · Lịch = `filter_lag_entry_window.filter_window()` chạy OFFLINE (anchor_fetcher=None) trên CSV
    của `signal_date` = phiên giao dịch NGAY TRƯỚC plan_date. Mã phiên 2/3 rơi vào
    `anchor_unavailable` khi offline vẫn là ứng viên đúng lịch ⇒ gộp vào tập tham chiếu.
  · FLOOR_FAIL = `sector_valuation_lens.lens_report(csv_path=..., floor_fail_only=True)` — chỉ đọc
    ô DD của CÙNG CSV, không tra live.
  · Ngày giao dịch = `trading_bot.vn_market` (T7/CN + `is_holiday`).

MÃ NGUYÊN NHÂN (mỗi phát hiện = 1 mã; FAIL nếu có ít nhất 1):
  Một plan:
    LAG_CAL_REF_UNAVAILABLE      không dựng được tham chiếu (thiếu CSV signal) ⇒ UNCHECKABLE (rc 3)
    LAG_CAL_PLAN_DATE_NONTRADING plan_date không phải phiên giao dịch
    LAG_CAL_ANALYSIS_MISSING     tham chiếu có ứng viên LAG nhưng plan không có `lag_analysis`
    LAG_CAL_SOURCE_MISSING       `lag_analysis.source_script` không ghi filter_lag_entry_window
    LAG_CAL_SIGNAL_MISMATCH      `lag_analysis.signal_date` ≠ phiên ngay trước plan_date
    LAG_CAL_DUE_MISSING          mã code nói hôm nay là PHIÊN CHUẨN (ngày 1) mà plan không liệt
                                 kê ở due_today (ngày 2/3 vắng không báo — xem chú thích code)
    LAG_CAL_DUE_EXTRA            plan liệt kê ở due_today mã code nói KHÔNG trong cửa sổ
    LAG_CAL_ORDER_NOT_DUE        lệnh book LAG cho mã không trong cửa sổ hôm nay
    LAG_CAL_FIELD_MISSING        thiếu entry_date / entry_window_day ở mục due_today
    LAG_CAL_ENTRY_DATE_MISMATCH  entry_date (hoặc entry_date_est của nhóm sắp tới) ≠ code
    LAG_CAL_WINDOW_DAY_MISMATCH  entry_window_day ≠ code
    LAG_CAL_UPCOMING_EXTRA       plan liệt kê "sắp tới" mã code không xếp vào nhóm đó
    LAG_CAL_NONTRADING_DATE      bất kỳ ngày vào lệnh nào plan ghi rơi vào ngày KHÔNG giao dịch
    LAG_DD_FLOOR_FAIL_NOT_GATE   SKIP lý do FLOOR_FAIL trong khi lăng kính ngành (cùng CSV) =
                                 KHONG_SKIP_VI_FLOOR_FAIL và lý do không nêu cổng nào khác
  Cặp 2 account cùng plan_date:
    LAG_X_SIGNAL_MISMATCH        2 plan dùng 2 signal_date khác nhau
    LAG_X_DUE_SET_MISMATCH       2 plan có tập due_today khác nhau
    LAG_X_ENTRY_DATE_MISMATCH    cùng mã, khác entry_date / entry_window_day / entry_date_est
    LAG_X_DD_DECISION_MISMATCH   cùng mã: 1 bên lấy (BUY/DEFER), bên kia SKIP mà KHÔNG khai
                                 `skip_reason_code` riêng-account (EXCLUDED_TICKER/ALREADY_HELD/
                                 CASH_ONLY) — khác biệt DD chỉ được đến từ khai báo tường minh
    LAG_X_EXCLUDED_UNVERIFIED    khai EXCLUDED_TICKER nhưng mã không có trong excluded_tickers
                                 của account (trading_bot/config) hoặc không đọc được config

Giới hạn ĐÃ BIẾT (nói thẳng, không giấu):
  · LAG_DD_FLOOR_FAIL_NOT_GATE đọc `decision_why` tự do bằng từ khoá — heuristic văn bản, không
    phải parse cấu trúc. Lý do nêu thêm cổng khác (RICH/cờ đỏ/rating/thanh khoản/banned/...) thì
    KHÔNG báo, kể cả khi cổng kia là bịa — checker không chấm lại DD.
  · ALREADY_HELD / CASH_ONLY được tin theo khai báo (không đọc vị thế DNSE ở đây).
  · Mã "sắp tới" dùng `entry_date_est` của filter — cùng nhãn "_est" (Tết ÂL chưa khai báo).

    python3 mike/bin/lag_plan_calendar_check.py --account SpaceX --plan-date 2026-10-26 [--json]
    python3 mike/bin/lag_plan_calendar_check.py --plan a.json [--plan b.json] [--recs-dir DIR]
        (1 --plan ⇒ tự ghép plan account kia cùng ngày trong cùng thư mục, trừ khi --no-pair)
    rc: 0 PASS · 1 FAIL · 3 UNCHECKABLE (không dựng được tham chiếu) · 4 lỗi đọc plan
"""
import argparse
import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wc_paths  # noqa: E402
WC_ROOT = wc_paths.find_wc_root(__file__)
sys.path.insert(0, WC_ROOT)

from trading_bot.vn_market import is_holiday  # noqa: E402

import filter_lag_entry_window as F            # noqa: E402
import sector_valuation_lens as L              # noqa: E402

PLANS_DIR = os.path.join(WC_ROOT, "data", "trade_plans")
ACCOUNTS = ("SpaceX", "ZaloPay")

TAKE = {"BUY", "DEFER", "DEFERRED", "BUY_DEFERRED", "WAIT_CASH", "RESIDUAL", "ORDER"}
SKIP = {"SKIP", "EXCLUDE", "EXCLUDED", "NO_BUY"}
ACCOUNT_SPECIFIC_SKIP = {"EXCLUDED_TICKER", "ALREADY_HELD", "CASH_ONLY"}
# Từ khoá cho thấy lý do SKIP viện dẫn một cổng KHÁC FLOOR_FAIL (xem "Giới hạn" ở docstring).
_OTHER_GATE = re.compile(
    r"RICH|cờ đỏ|co do|RED_FLAG|RATING|rating|8L|ADV|thanh khoản|thanh khoan|universe|BANNED|"
    r"banned|forensic|excluded_tickers|đã giữ|ALREADY_HELD|anchor|đuổi giá|duoi gia|no.?chase|chase", re.IGNORECASE)


def _d(x):
    return F._d(x)


def is_trading_day(d):
    d = _d(d)
    return d.weekday() < 5 and not is_holiday(d)


def prev_trading_day(d):
    d = _d(d) - dt.timedelta(days=1)
    while not is_trading_day(d):
        d -= dt.timedelta(days=1)
    return d


def _f(code, account, detail, ticker=None):
    return {"code": code, "account": account, "ticker": ticker, "detail": detail}


# ── tham chiếu do code tính ──────────────────────────────────────────────────
def reference(plan_date, recs_dir=None):
    """Lịch + FLOOR_FAIL-lens tham chiếu cho plan_date. Thuần offline."""
    plan_date = _d(plan_date)
    sig = prev_trading_day(plan_date)
    csv_path = os.path.join(recs_dir or F.RECS_DIR, f"golive_v23_recommendations_{sig}.csv")
    ref = {"plan_date": str(plan_date), "signal_date": str(sig), "csv": csv_path,
           "ok": False, "due": {}, "upcoming": {}, "lens": {}, "dd_red": {}, "error": None}
    if not os.path.exists(csv_path):
        ref["error"] = f"không thấy CSV signal {sig}: {csv_path}"
        return ref
    w = F.filter_window(plan_date, sig, csv_path, anchor_fetcher=None)
    if not (w.get("calendar_check") or {}).get("ok"):
        ref["error"] = f"cổng lịch của filter FAIL: {(w.get('calendar_check') or {}).get('reason')}"
        return ref
    for it in w["due_today"] + w["anchor_unavailable"]:
        ref["due"][it["ticker"]] = {"entry_date": it["entry_date"],
                                    "entry_window_day": it["entry_window_day"]}
        ref["dd_red"][it["ticker"]] = it.get("dd_red_flags") or []
    for it in w["upcoming_next_plans"]:
        ref["upcoming"][it["ticker"]] = it.get("entry_date_est") or it.get("entry_date")
    lr = L.lens_report(csv_path=csv_path, floor_fail_only=True)
    ref["lens"] = {r["ticker"]: r["decision"] for r in lr["results"]}
    ref["ok"] = True
    return ref


# ── trích phần LAG của plan ──────────────────────────────────────────────────
def _lag_orders(plan):
    out = []
    for key in ("orders", "deferred_orders"):
        for o in plan.get(key) or []:
            if not (isinstance(o, dict) and str(o.get("book") or "").upper() == "LAG"):
                continue
            # Lệnh BÁN của book LAG (thoát vị thế) không có lịch vào lệnh ⇒ không thuộc phạm vi.
            if str(o.get("side") or o.get("action") or "").strip().lower() == "sell":
                continue
            out.append(o)
    return out


def _entry_date(item):
    for k in ("entry_date", "entry_window_date", "entry_anchor_date"):
        if item.get(k):
            return str(item[k])[:10]
    return None


def _decision(item):
    d = str(item.get("decision") or "").strip().upper()
    if d in TAKE:
        return "TAKE"
    if d in SKIP:
        return "SKIP"
    return None


def _due_items(plan):
    la = plan.get("lag_analysis") or {}
    return {str(x.get("ticker")).strip(): x for x in (la.get("due_today") or [])
            if isinstance(x, dict) and x.get("ticker")}


def _upcoming_items(plan):
    la = plan.get("lag_analysis") or {}
    return {str(x.get("ticker")).strip(): x for x in (la.get("lag_upcoming_for_next_plans") or [])
            if isinstance(x, dict) and x.get("ticker")}


# ── kiểm 1 plan ──────────────────────────────────────────────────────────────
def check_plan(plan, ref):
    acct = plan.get("account")
    pdate = str(plan.get("plan_date") or plan.get("date") or "")[:10]
    out = []
    if not is_trading_day(pdate):
        # Kiểm TRƯỚC tham chiếu: plan_date ngày nghỉ thì filter cũng từ chối ⇒ nếu để sau, mã
        # nguyên nhân thật bị nuốt thành REF_UNAVAILABLE.
        out.append(_f("LAG_CAL_PLAN_DATE_NONTRADING", acct, f"{pdate} không phải phiên giao dịch"))
    if not ref.get("ok"):
        return out + [_f("LAG_CAL_REF_UNAVAILABLE", acct, ref.get("error"))]
    if pdate != ref["plan_date"]:
        return out + [_f("LAG_CAL_REF_UNAVAILABLE", acct,
                         f"plan_date {pdate} ≠ tham chiếu {ref['plan_date']}")]

    la = plan.get("lag_analysis")
    orders = _lag_orders(plan)
    if not la:
        if ref["due"] or ref["upcoming"] or orders:
            out.append(_f("LAG_CAL_ANALYSIS_MISSING", acct,
                          f"code có {len(ref['due'])} mã trong cửa sổ, {len(ref['upcoming'])} sắp "
                          f"tới; plan không có lag_analysis"))
        la = {}
    elif ref["due"] or ref["upcoming"] or orders or _due_items(plan) or _upcoming_items(plan):
        # Cả code lẫn plan đều rỗng LAG ⇒ không có lịch nào để sai; không đòi nguồn/signal.
        if "filter_lag_entry_window" not in str(la.get("source_script") or la.get("source") or ""):
            out.append(_f("LAG_CAL_SOURCE_MISSING", acct,
                          f"source_script={la.get('source_script')!r}"))
        if str(la.get("signal_date") or "")[:10] != ref["signal_date"]:
            out.append(_f("LAG_CAL_SIGNAL_MISMATCH", acct,
                          f"plan signal_date={la.get('signal_date')!r}, đúng phải là "
                          f"{ref['signal_date']} (phiên ngay trước {pdate})"))

    due = _due_items(plan)
    # Chỉ phiên CHUẨN (ngày 1) là bắt buộc có mặt: mã ngày 2/3 vắng có thể hợp lệ (filter thật
    # loại sang anchor_unavailable khi không tra được anchor, hoặc đã khớp đủ ở phiên trước).
    for tk in sorted(t for t in set(ref["due"]) - set(due) if ref["due"][t]["entry_window_day"] == 1):
        out.append(_f("LAG_CAL_DUE_MISSING", acct,
                      f"code: entry {ref['due'][tk]['entry_date']} ngày "
                      f"{ref['due'][tk]['entry_window_day']}/3 — plan không liệt kê", tk))
    for tk in sorted(set(due) - set(ref["due"])):
        out.append(_f("LAG_CAL_DUE_EXTRA", acct, "code: không trong cửa sổ hôm nay", tk))

    dates_seen = []
    for tk, it in due.items():
        r = ref["due"].get(tk)
        ed = _entry_date(it)
        if ed:
            dates_seen.append((tk, ed))
        if r is None:
            continue
        if ed is None:
            out.append(_f("LAG_CAL_FIELD_MISSING", acct, "thiếu entry_date", tk))
        elif ed != r["entry_date"]:
            out.append(_f("LAG_CAL_ENTRY_DATE_MISMATCH", acct,
                          f"plan {ed} ≠ code {r['entry_date']}", tk))
        if it.get("entry_window_day") is None:
            out.append(_f("LAG_CAL_FIELD_MISSING", acct, "thiếu entry_window_day", tk))
        elif int(it["entry_window_day"]) != int(r["entry_window_day"]):
            out.append(_f("LAG_CAL_WINDOW_DAY_MISMATCH", acct,
                          f"plan {it['entry_window_day']} ≠ code {r['entry_window_day']}", tk))
        if (_decision(it) == "SKIP" and ref["lens"].get(tk) == "KHONG_SKIP_VI_FLOOR_FAIL"
                and not ref["dd_red"].get(tk)):
            why = str(it.get("decision_why") or it.get("reason") or "")
            # Token verdict của lăng kính (KHONG_SKIP_VI_FLOOR_FAIL) chứa chữ FLOOR_FAIL nhưng là lý do NGƯỢC LẠI
            # ("không skip vì floor_fail"); DollarBill hay trích nguyên văn ⇒ gỡ trước khi dò (arch-review 21/10, SSI 08-11).
            why_core = why.upper().replace("KHONG_SKIP_VI_FLOOR_FAIL", "")
            if "FLOOR_FAIL" in why_core and not _OTHER_GATE.search(why):
                out.append(_f("LAG_DD_FLOOR_FAIL_NOT_GATE", acct,
                              f"SKIP vì FLOOR_FAIL nhưng sector_valuation_lens (cùng CSV) = "
                              f"KHONG_SKIP_VI_FLOOR_FAIL; why={why[:80]!r}", tk))

    for o in orders:
        tk = str(o.get("ticker") or "").strip()
        r = ref["due"].get(tk)
        ed = o.get("entry_anchor_date") or o.get("entry_date")
        if ed:
            dates_seen.append((tk, str(ed)[:10]))
        if r is None:
            out.append(_f("LAG_CAL_ORDER_NOT_DUE", acct, "lệnh LAG cho mã ngoài cửa sổ", tk))
            continue
        if ed and str(ed)[:10] != r["entry_date"]:
            out.append(_f("LAG_CAL_ENTRY_DATE_MISMATCH", acct,
                          f"lệnh: {str(ed)[:10]} ≠ code {r['entry_date']}", tk))
        if o.get("entry_window_day") is not None and \
                int(o["entry_window_day"]) != int(r["entry_window_day"]):
            out.append(_f("LAG_CAL_WINDOW_DAY_MISMATCH", acct,
                          f"lệnh: {o['entry_window_day']} ≠ code {r['entry_window_day']}", tk))

    for tk, it in _upcoming_items(plan).items():
        ed = _entry_date(it) or (str(it["entry_date_est"])[:10] if it.get("entry_date_est")
                                 else None)
        if ed:
            dates_seen.append((tk, ed))
        if tk not in ref["upcoming"]:
            out.append(_f("LAG_CAL_UPCOMING_EXTRA", acct, "code không xếp vào nhóm sắp tới", tk))
        elif ed != ref["upcoming"][tk]:
            out.append(_f("LAG_CAL_ENTRY_DATE_MISMATCH", acct,
                          f"sắp tới: plan {ed} ≠ code {ref['upcoming'][tk]}", tk))

    for tk, ed in sorted(set(dates_seen)):
        try:
            day = _d(ed)
        except ValueError:
            out.append(_f("LAG_CAL_NONTRADING_DATE", acct, f"{ed!r} không phải ngày hợp lệ", tk))
            continue
        if not is_trading_day(day):
            out.append(_f("LAG_CAL_NONTRADING_DATE", acct,
                          f"{ed} ({day.strftime('%A')}) không phải phiên giao dịch", tk))
    return out


# ── kiểm cặp 2 account ───────────────────────────────────────────────────────
def check_pair(pa, pb, excluded=None, has_lag=True):
    """excluded: {account: set(tickers)} từ config, hoặc None nếu không đọc được.
    has_lag=False (code + 2 plan đều rỗng LAG) ⇒ bỏ qua so signal_date: không có gì để lệch."""
    out = []
    a, b = pa.get("account"), pb.get("account")
    tag = f"{a}↔{b}"
    sa = str((pa.get("lag_analysis") or {}).get("signal_date") or "")[:10]
    sb = str((pb.get("lag_analysis") or {}).get("signal_date") or "")[:10]
    if has_lag and sa != sb:
        out.append(_f("LAG_X_SIGNAL_MISMATCH", tag, f"{a}={sa or None} {b}={sb or None}"))
    da, db = _due_items(pa), _due_items(pb)
    if set(da) != set(db):
        out.append(_f("LAG_X_DUE_SET_MISMATCH", tag,
                      f"chỉ {a}: {sorted(set(da) - set(db))}; chỉ {b}: {sorted(set(db) - set(da))}"))
    for tk in sorted(set(da) & set(db)):
        ia, ib = da[tk], db[tk]
        if _entry_date(ia) != _entry_date(ib) or \
                str(ia.get("entry_window_day")) != str(ib.get("entry_window_day")):
            out.append(_f("LAG_X_ENTRY_DATE_MISMATCH", tag,
                          f"{a}: {_entry_date(ia)}/ngày {ia.get('entry_window_day')} — "
                          f"{b}: {_entry_date(ib)}/ngày {ib.get('entry_window_day')}", tk))
        ca, cb = _decision(ia), _decision(ib)
        if ca and cb and ca != cb:
            acct, it = (a, ia) if ca == "SKIP" else (b, ib)
            code = str(it.get("skip_reason_code") or "").strip().upper()
            if code not in ACCOUNT_SPECIFIC_SKIP:
                out.append(_f("LAG_X_DD_DECISION_MISMATCH", tag,
                              f"{a}={ca} {b}={cb}; bên SKIP ({acct}) không khai skip_reason_code "
                              f"riêng-account (có: {code or None})", tk))
            elif code == "EXCLUDED_TICKER" and (excluded is None or
                                                tk not in (excluded.get(acct) or set())):
                out.append(_f("LAG_X_EXCLUDED_UNVERIFIED", tag,
                              f"{acct} khai EXCLUDED_TICKER nhưng excluded_tickers="
                              f"{None if excluded is None else sorted(excluded.get(acct) or [])}",
                              tk))
    ua, ub = _upcoming_items(pa), _upcoming_items(pb)
    for tk in sorted(set(ua) & set(ub)):
        ea = _entry_date(ua[tk]) or ua[tk].get("entry_date_est")
        eb = _entry_date(ub[tk]) or ub[tk].get("entry_date_est")
        if ea != eb:
            out.append(_f("LAG_X_ENTRY_DATE_MISMATCH", tag, f"sắp tới: {a}={ea} {b}={eb}", tk))
    return out


def load_excluded():
    try:
        from trading_bot.config import load_accounts, load_config
        return {p["label"]: set(p.get("excluded_tickers") or [])
                for p in load_accounts(load_config())}
    except Exception:                                        # noqa: BLE001
        return None


def run(plans, recs_dir=None, excluded=None):
    """plans: list[dict] (1 hoặc 2, cùng plan_date). → kết quả JSON-able."""
    pdate = str(plans[0].get("plan_date") or plans[0].get("date") or "")[:10]
    ref = reference(pdate, recs_dir)
    findings = []
    for p in plans:
        findings += check_plan(p, ref)
    if len(plans) == 2:
        has_lag = bool(ref.get("due") or ref.get("upcoming")) or any(
            _lag_orders(p) or _due_items(p) or _upcoming_items(p) for p in plans)
        findings += check_pair(plans[0], plans[1], excluded, has_lag)
    uncheckable = any(f["code"] == "LAG_CAL_REF_UNAVAILABLE" for f in findings)
    status = "UNCHECKABLE" if uncheckable else ("FAIL" if findings else "PASS")
    return {"script": "mike/bin/lag_plan_calendar_check.py", "plan_date": pdate,
            "accounts": [p.get("account") for p in plans], "status": status,
            "reference": {k: ref[k] for k in ("signal_date", "csv", "due", "upcoming", "error")},
            "findings": findings,
            "codes": sorted({f["code"] for f in findings})}


def report_block(res):
    acc = "/".join(str(a) for a in res["accounts"])
    if res["status"] == "PASS":
        return (f"✅ **Lịch LAG ({acc} {res['plan_date']})**: khớp filter_lag_entry_window "
                f"(signal {res['reference']['signal_date']}, {len(res['reference']['due'])} mã "
                f"trong cửa sổ).")
    head = ("⚠️ **Lịch LAG: KHÔNG KIỂM ĐƯỢC**" if res["status"] == "UNCHECKABLE"
            else "⛔ **Lịch/DD LAG lệch code — FAIL**")
    lines = [f"{head} ({acc} {res['plan_date']}): {', '.join(res['codes'])}"]
    for f in res["findings"][:12]:
        lines.append(f"- `{f['code']}` {f['account']}{' ' + f['ticker'] if f['ticker'] else ''}: "
                     f"{f['detail']}")
    if len(res["findings"]) > 12:
        lines.append(f"- … +{len(res['findings']) - 12} phát hiện (chạy lag_plan_calendar_check.py)")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--plan", action="append", default=[], help="file plan JSON (≤2)")
    ap.add_argument("--account", default=None)
    ap.add_argument("--plan-date", default=None)
    ap.add_argument("--no-pair", action="store_true",
                    help="KHÔNG tự kiểm chéo plan account kia cùng ngày (cùng thư mục)")
    ap.add_argument("--plans-dir", default=PLANS_DIR)
    ap.add_argument("--recs-dir", default=None, help="thư mục CSV khuyến nghị (mặc định engine)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--report-block", action="store_true")
    a = ap.parse_args()

    paths = list(a.plan)
    if not paths:
        if not (a.account and a.plan_date):
            ap.error("cần --plan hoặc (--account và --plan-date)")
        paths = [os.path.join(a.plans_dir, f"plan_{a.account}_{_d(a.plan_date)}.json")]
        if not a.no_pair:
            for other in ACCOUNTS:
                p = os.path.join(a.plans_dir, f"plan_{other}_{_d(a.plan_date)}.json")
                if other != a.account and os.path.exists(p):
                    paths.append(p)
    elif len(paths) == 1 and not a.no_pair:
        # 1 file plan ⇒ tự tìm plan account kia CÙNG NGÀY ở cùng thư mục (send_plan_report gọi kiểu này).
        try:
            p0 = json.load(open(paths[0], encoding="utf-8"))
            d0 = str(p0.get("plan_date") or p0.get("date") or "")[:10]
            for other in ACCOUNTS:
                q = os.path.join(os.path.dirname(os.path.abspath(paths[0])), f"plan_{other}_{d0}.json")
                if other != p0.get("account") and d0 and os.path.exists(q):
                    paths.append(q)
        except Exception:                                    # noqa: BLE001
            pass                                             # lỗi đọc sẽ báo rc 4 ngay dưới
    if len(paths) > 2:
        ap.error("tối đa 2 plan")
    try:
        plans = [json.load(open(p, encoding="utf-8")) for p in paths]
    except Exception as e:                                   # noqa: BLE001
        print(f"lag_plan_calendar_check: không đọc được plan: {e}", file=sys.stderr)
        return 4
    res = run(plans, a.recs_dir, load_excluded() if len(plans) == 2 else None)
    res["plans"] = paths
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif a.report_block:
        print(report_block(res))
    else:
        print(report_block(res))
        print(f"  tham chiếu: {res['reference']['csv']}")
    return {"PASS": 0, "FAIL": 1, "UNCHECKABLE": 3}[res["status"]]


if __name__ == "__main__":
    sys.exit(main())
