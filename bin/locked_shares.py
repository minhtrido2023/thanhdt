#!/usr/bin/env python3
"""locked_shares.py — phân loại cổ phiếu ĐANG GIỮ nhưng CHƯA BÁN ĐƯỢC (openQuantity > tradeQuantity).

Dùng cho send_plan_report.sh: phần bị khoá là CP thưởng / cổ tức CP / quyền mua đang chờ niêm yết
bổ sung thì lệnh bán bị cắt về trần sellable là CHUYỆN ĐÃ BIẾT, tự hết khi niêm yết — không cần
người duyệt quyết gì ⇒ hiện 1 dòng ℹ️ gộp thay vì ⚠️ lặp lại mỗi tối (user duyệt 2026-10-07).

Một mã chỉ được xếp `pending` khi CÓ ĐỦ 2 bằng chứng đọc được (§29 — không đoán):
  1. KHÔNG có lệnh MUA khớp của mã đó (cùng account) trong `RECENT_FILES` file dnse_raw gần nhất
     ⇒ phần khoá không phải hàng mua chờ T+2;
  2. CÓ sự kiện phát hành cho cổ đông hiện hữu (ISS: CP thưởng / cổ tức CP / quyền mua) GDKHQ
     trong `LOOKBACK_DAYS` ngày — đọc `tav2_bq.corporate_action` (pricing_events, gồm announced),
     BQ lỗi thì rơi về registry `data/corp_actions.json` (chỉ bản ghi CONFIRMED).
Thiếu 1 trong 2 ⇒ `unexplained` ⇒ caller GIỮ cảnh báo ⚠️ như cũ.

Selfcheck: python3 bin/locked_shares.py --selfcheck
Chạy tay:  python3 bin/locked_shares.py --account-no 0001743768 --asof 2026-10-07
"""
import datetime as dt
import glob
import json
import os
import sys

RECENT_FILES = 4          # file dnse_raw gần nhất (≤ asof) quét lệnh mua — phủ T+2 + cuối tuần
LOOKBACK_DAYS = 150       # cửa sổ tìm sự kiện ISS: niêm yết bổ sung thường 3-8 tuần sau GDKHQ
_HOLDER_EXCLUDE = ("CBCNV", "ESOP", "riêng lẻ", "chuyển đổi")   # không phát cho cổ đông hiện hữu


def _raw_files(raw_dir, asof, n):
    fs = sorted(f for f in glob.glob(os.path.join(raw_dir, "dnse_raw_*.jsonl"))
                if os.path.basename(f)[9:19] <= asof)
    return fs[-n:]


def _records(path, account_no, kind):
    with open(path) as fh:
        for line in fh:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            # §12: file dùng chung mọi account — lọc account TRƯỚC mọi phép tính
            if str(r.get("account_no") or r.get("accountNo")) != str(account_no):
                continue
            if r.get("kind") == kind:
                yield r


def latest_positions(raw_dir, account_no, asof, max_back=5):
    """(ts, {ticker: (open, trade)}) từ bản ghi positions MỚI NHẤT ≤ asof; gộp TỔNG mọi lô."""
    for path in reversed(_raw_files(raw_dir, asof, max_back)):
        last = None
        for r in _records(path, account_no, "positions"):
            last = r
        if last is None:
            continue
        agg = {}
        for p in (last.get("payload") or {}).get("positions") or []:
            o, t = agg.get(p.get("symbol"), (0, 0))
            agg[p.get("symbol")] = (o + int(p.get("openQuantity") or 0),
                                    t + int(p.get("tradeQuantity") or 0))
        return last.get("ts"), agg
    return None, {}


def recent_buy_tickers(raw_dir, account_no, asof, n_files=RECENT_FILES):
    out = set()
    for path in _raw_files(raw_dir, asof, n_files):
        for r in _records(path, account_no, "orders"):
            for o in (r.get("payload") or {}).get("orders") or []:
                if (o.get("side") == "NB" and int(o.get("fillQuantity") or 0) > 0
                        and str(o.get("accountNo", account_no)) == str(account_no)):
                    out.add(o.get("symbol"))
    return out


def _bq_events(tickers, since, asof):
    import corp_action_lib
    rows = corp_action_lib.pricing_events(tickers, since=since, until=asof, codes=("ISS",))
    ev = {}
    for r in rows:
        meth = str(r.get("issue_method_name_vi") or "")
        if any(x.lower() in meth.lower() for x in _HOLDER_EXCLUDE):
            continue
        try:
            ratio = f"{float(r.get('exercise_ratio')) * 100:.4g}%"
        except (TypeError, ValueError):
            ratio = "?"
        ev.setdefault(r["ticker"], []).append(
            {"ex_date": r.get("exright_date"), "label": f"{meth or 'phát hành'} {ratio}"})
    return ev


def _registry_events(tickers, since, asof, registry_path):
    with open(registry_path) as fh:
        acts = json.load(fh).get("actions") or []
    ev = {}
    for a in acts:
        if (a.get("ticker") in tickers and str(a.get("_status", "")).startswith("CONFIRMED")
                and since < str(a.get("ex_date", "")) <= asof
                and float(a.get("qty_multiplier") or 1) > 1):
            ev.setdefault(a["ticker"], []).append(
                {"ex_date": a["ex_date"],
                 "label": f"{a.get('event_type')} ×{float(a['qty_multiplier']):g}"})
    return ev


def classify(account_no, asof, raw_dir, registry_path, bq_events=_bq_events):
    ts, pos = latest_positions(raw_dir, account_no, asof)
    locked = {tk: (o, o - t) for tk, (o, t) in pos.items() if o > t}
    res = {"positions_ts": ts, "pending": {}, "unexplained": {}, "event_source": None}
    if not locked:
        return res
    buys = recent_buy_tickers(raw_dir, account_no, asof)
    since = (dt.date.fromisoformat(asof) - dt.timedelta(days=LOOKBACK_DAYS)).isoformat()
    try:
        ev = bq_events(sorted(locked), since, asof)
        res["event_source"] = "tav2_bq.corporate_action"
    except Exception as e:                       # BQ lỗi ⇒ registry, vẫn phải có bằng chứng
        try:
            ev = _registry_events(set(locked), since, asof, registry_path)
            res["event_source"] = f"data/corp_actions.json (BQ lỗi: {type(e).__name__})"
        except Exception as e2:
            ev = {}
            res["event_source"] = f"KHÔNG đọc được (BQ {type(e).__name__}, registry {type(e2).__name__})"
    for tk, (o, lk) in sorted(locked.items()):
        item = {"open": o, "locked": lk, "events": sorted(ev.get(tk, []), key=lambda x: x["ex_date"] or "")}
        if tk in buys:
            item["why"] = f"có lệnh MUA khớp trong {RECENT_FILES} ngày gần nhất (có thể là hàng chờ T+2)"
            res["unexplained"][tk] = item
        elif not item["events"]:
            item["why"] = "không thấy sự kiện CP thưởng/cổ tức CP/quyền mua nào"
            res["unexplained"][tk] = item
        else:
            res["pending"][tk] = item
    return res


def _ddmm(d):
    try:
        return dt.date.fromisoformat(str(d)[:10]).strftime("%d/%m")
    except ValueError:
        return str(d)


def describe(tk, item):
    """'VPB 312cp (Trả Cổ tức bằng Cổ phiếu 26.04%, GDKHQ 24/09)' — nguồn = bằng chứng đã đọc."""
    by_ex = {}
    for e in item["events"]:
        by_ex.setdefault(e["ex_date"], []).append(e["label"])
    evs = "; ".join(f"{' + '.join(v)}, GDKHQ {_ddmm(k)}" for k, v in by_ex.items())
    return f"{tk} {item['locked']:,}cp ({evs})"


# ─────────────────────────────── selfcheck ───────────────────────────────
def _selfcheck():
    import tempfile
    fails = []

    def check(name, cond, detail=""):
        print(("PASS " if cond else "FAIL ") + name + ("" if cond else f" — {detail}"))
        if not cond:
            fails.append(name)

    acct, other = "0001743768", "0002023347"
    with tempfile.TemporaryDirectory() as d:
        def write(date, recs):
            with open(os.path.join(d, f"dnse_raw_{date}.jsonl"), "w") as fh:
                for r in recs:
                    fh.write(json.dumps(r) + "\n")

        def pos(acc, ts, rows):
            return {"ts": ts, "kind": "positions", "account_no": acc,
                    "payload": {"positions": [{"symbol": s, "openQuantity": o, "tradeQuantity": t}
                                              for s, o, t in rows]}}

        def orders(acc, rows):
            return {"ts": "x", "kind": "orders", "account_no": acc,
                    "payload": {"orders": [{"symbol": s, "side": sd, "fillQuantity": q, "accountNo": acc}
                                           for s, sd, q in rows]}}

        write("2026-10-05", [orders(acct, [("AAA", "NB", 100)])])          # mua cũ, ngoài 4 file? (xem dưới)
        write("2026-10-06", [orders(acct, [("BBB", "NB", 100), ("CCC", "NS", 50)]),
                             orders(other, [("VPB", "NB", 100)])])          # account khác — phải bị lọc
        write("2026-10-07", [pos(acct, "2026-10-07T20:00:00", [("VPB", 300, 0), ("VPB", 12, 0),
                                                                ("BBB", 100, 0), ("DDD", 50, 0),
                                                                ("EEE", 10, 10), ("FFF", 40, 0)]),
                             pos(acct, "2026-10-07T21:06:51", [("VPB", 300, 0), ("VPB", 12, 0),
                                                                ("BBB", 100, 0), ("DDD", 50, 0),
                                                                ("EEE", 10, 10), ("FFF", 40, 0)]),
                             pos(other, "2026-10-07T21:07:00", [("ZZZ", 999, 0)])])
        write("2026-10-08", [pos(acct, "2026-10-08T21:00:00", [("VPB", 1, 0)])])   # SAU asof — bỏ qua
        reg = os.path.join(d, "corp_actions.json")
        with open(reg, "w") as fh:
            json.dump({"actions": [
                {"ticker": "FFF", "event_type": "BONUS_ISSUE", "qty_multiplier": 1.2,
                 "ex_date": "2026-09-01", "_status": "CONFIRMED — test"},
                {"ticker": "DDD", "event_type": "BONUS_ISSUE", "qty_multiplier": 1.2,
                 "ex_date": "2026-09-01", "_status": "REVOKED — test"}]}, fh)

        def fake_bq(tickers, since, asof):
            assert asof == "2026-10-07" and since == "2026-05-10", (since, asof)
            return {"VPB": [{"ex_date": "2026-09-24", "label": "Trả Cổ tức bằng Cổ phiếu 26%"}],
                    "BBB": [{"ex_date": "2026-09-20", "label": "Cổ phiếu thưởng 10%"}]}

        def bad_bq(*_a):
            raise RuntimeError("bq down")

        r = classify(acct, "2026-10-07", d, reg, fake_bq)
        check("ts_latest_record_le_asof", r["positions_ts"] == "2026-10-07T21:06:51", r["positions_ts"])
        check("lots_summed", r["pending"].get("VPB", {}).get("locked") == 312, r["pending"].get("VPB"))
        check("other_account_filtered", "ZZZ" not in r["pending"] and "ZZZ" not in r["unexplained"])
        check("fully_tradeable_ignored", "EEE" not in r["pending"] and "EEE" not in r["unexplained"])
        check("recent_buy_not_pending", "BBB" in r["unexplained"] and "BBB" not in r["pending"], r)
        check("other_account_buy_not_counted", "VPB" in r["pending"])
        check("no_event_unexplained", "DDD" in r["unexplained"] and "FFF" in r["unexplained"], r)
        check("describe_text", describe("VPB", r["pending"]["VPB"])
              == "VPB 312cp (Trả Cổ tức bằng Cổ phiếu 26%, GDKHQ 24/09)", describe("VPB", r["pending"]["VPB"]))

        r2 = classify(acct, "2026-10-07", d, reg, bad_bq)
        check("bq_fail_registry_fallback", "FFF" in r2["pending"], r2)
        check("registry_revoked_ignored", "DDD" in r2["unexplained"], r2)
        check("bq_fail_source_named", "BQ lỗi: RuntimeError" in str(r2["event_source"]), r2["event_source"])
        check("bq_fail_vpb_unexplained", "VPB" in r2["unexplained"], r2)

        r3 = classify(acct, "2026-10-07", d, os.path.join(d, "missing.json"), bad_bq)
        check("both_sources_fail_all_unexplained", not r3["pending"] and "KHÔNG đọc được" in r3["event_source"], r3)

        r4 = classify("0009999999", "2026-10-07", d, reg, fake_bq)
        check("unknown_account_empty", r4 == {"positions_ts": None, "pending": {}, "unexplained": {},
                                             "event_source": None}, r4)
        # BUY 05/10 nằm trong 4 file gần nhất ⇒ AAA (nếu bị khoá) phải là unexplained
        check("buy_window_covers_4_files", "AAA" in recent_buy_tickers(d, acct, "2026-10-07"))
        check("buy_window_excludes_after_asof", recent_buy_tickers(d, acct, "2026-10-04") == set())

    print(f"\n{'OK' if not fails else 'FAIL'} — locked_shares selfcheck "
          f"{'PASS' if not fails else str(len(fails)) + ' FAIL'}")
    return 0 if not fails else 1


if __name__ == "__main__":
    if "--selfcheck" in sys.argv:
        sys.exit(_selfcheck())
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--account-no", required=True)
    ap.add_argument("--asof", required=True)
    ap.add_argument("--wc", default=os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude"))
    a = ap.parse_args()
    sys.path.insert(0, a.wc)
    print(json.dumps(classify(a.account_no, a.asof, os.path.join(a.wc, "data", "execution_logs"),
                              os.path.join(a.wc, "data", "corp_actions.json")),
                     ensure_ascii=False, indent=1))
