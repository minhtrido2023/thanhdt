#!/usr/bin/env python3
"""thesis_cards_sync_ddref — đồng bộ `dd_ref` của thẻ luận điểm với sổ giá DD khi sổ chỉ thêm rev mà SỐ không đổi.

Sổ giá `kb/dd_price_zones.json` thêm rev mới (đính chính, recheck, thêm tâm adj E17…) làm `thesis_cards_selfcheck` FAIL vì
`dd_ref.rev` tụt. Tool này thêm thẻ rev+1 (append-only) chỉ đổi `dd_ref` — KHÔNG đụng luận điểm/exit/mốc.

  python3 bin/thesis_cards_sync_ddref.py [--ticker FPT ...] [--write]

Quy tắc an toàn:
  · chỉ đồng bộ thẻ ACTIVE, không có `dd_ref.stale_reason`, chỉ lệch ở `rev`; (dd_date, center, zone_low, zone_high) phải GIỐNG HỆT.
  · số khác (center/vùng/dd_date) ⇒ luận điểm user đã duyệt dựa trên số cũ ⇒ KHÔNG tự đồng bộ, in "CẦN NGƯỜI XEM" (rc=4).
  · mặc định dry-run; --write: dựng bản tạm → T.validate FAIL thì KHÔNG ghi (rc=3) → os.replace nguyên tử. Chạy lại = no-op.
rc: 0 ok/không có gì để làm · 2 lỗi đầu vào · 3 validate bản tạm FAIL · 4 có mã cần người xem (các mã còn lại vẫn đồng bộ được).
"""
import argparse
import copy
import datetime as dt
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import thesis_cards as T  # noqa: E402

ICT = dt.timezone(dt.timedelta(hours=7))
NUM_KEYS = ("dd_date", "center", "zone_low", "zone_high")


def plan(doc, ledger, tickers=None):
    """→ (sync: [(ticker, old_rev, led_entry)], review: [(ticker, lý do)])."""
    lg, sync, review = T.latest_ledger(ledger), [], []
    for t, c in sorted(T.latest_cards(doc).items()):
        if tickers and t not in tickers:
            continue
        d, e = c.get("dd_ref") or {}, lg.get(t)
        if c.get("status") != "active" or d.get("stale_reason") or e is None:
            continue
        if d.get("rev") == e.get("rev", 1) and all(d.get(k) == e.get(k) for k in NUM_KEYS):
            continue
        diff = [k for k in NUM_KEYS if d.get(k) != e.get(k)]
        if diff:
            review.append((t, "số trong sổ giá ĐỔI (%s: thẻ %s → sổ %s) — luận điểm đã duyệt dựa số cũ" % (
                ", ".join(diff), [d.get(k) for k in diff], [e.get(k) for k in diff])))
        else:
            sync.append((t, d.get("rev"), e))
    return sync, review


def apply(doc, sync, now):
    new = copy.deepcopy(doc)
    for t, old, e in sync:
        c = copy.deepcopy(T.latest_cards(new)[t])
        c["rev"] += 1
        c["dd_ref"].update(dd_date=e["dd_date"], rev=e.get("rev", 1), center=e["center"], zone_low=e["zone_low"], zone_high=e["zone_high"],
                           source="kb/dd_price_zones.json (đồng bộ tự động %s; rev %s→%s, center/vùng không đổi)" % (now.strftime("%d/%m/%Y"), old, e.get("rev", 1)))
        c["recorded_at"] = now.isoformat(timespec="seconds")
        c["supersedes_note"] = "rev%d: chỉ đồng bộ dd_ref theo sổ giá rev %s (không đổi luận điểm/exit/mốc; thesis_cards_sync_ddref.py)" % (c["rev"], e.get("rev", 1))
        new["cards"].append(c)
    return new


def run(cards_path, ledger_path, write, tickers=None, now=None, out=sys.stdout, err=sys.stderr):
    now = now or dt.datetime.now(ICT)
    try:
        raw = open(cards_path, encoding="utf-8").read()
        doc = json.loads(raw)
        ledger = T.read_json(ledger_path)["entries"]
    except (OSError, ValueError, KeyError) as x:
        print("TỪ CHỐI: không đọc được đầu vào: %s" % x, file=err)
        return 2
    if json.dumps(doc, ensure_ascii=False, indent=2) + "\n" != raw:
        print("TỪ CHỐI: định dạng thesis_cards.json lệch json.dumps(indent=2) — sửa tay rồi chạy lại", file=err)
        return 2
    sync, review = plan(doc, ledger, set(tickers) if tickers else None)
    for t, why in review:
        print("CẦN NGƯỜI XEM %s: %s" % (t, why), file=out)
    rc_review = 4 if review else 0
    if not sync:
        print("không có thẻ nào cần đồng bộ rev." if not review else "không có thẻ nào đồng bộ được tự động.", file=out)
        return rc_review
    new = apply(doc, sync, now)
    # lệch dd_ref của mã KHÔNG đồng bộ lượt này (CẦN NGƯỜI XEM / ngoài --ticker) có sẵn từ trước, không phải do tool ⇒ không chặn mã đồng bộ được
    mine = {t for t, _, _ in sync}
    skip = tuple("%s: dd_ref" % t for t in {c["ticker"] for c in new["cards"]} - mine)
    errs = [x for x in T.validate(new, ledger, None) if not x.startswith(skip)]
    if errs:
        for x in errs[:10]:
            print("validate bản tạm FAIL: " + x, file=err)
        print("TỪ CHỐI: validate bản tạm có %d lỗi — KHÔNG ghi" % len(errs), file=err)
        return 3
    for t, old, e in sync:
        print("đồng bộ %s: dd_ref.rev %s → %s (thẻ rev→%d)" % (t, old, e.get("rev", 1), T.latest_cards(new)[t]["rev"]), file=out)
    if not write:
        print("[dry-run] không ghi; thêm --write để ghi.", file=out)
        return rc_review
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(cards_path)), prefix=".tmp_thesis_cards_", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps(new, ensure_ascii=False, indent=2) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, cards_path)
        tmp = None
        print("ĐÃ GHI %s (%d thẻ)" % (cards_path, len(sync)), file=out)
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)
    return rc_review


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ticker", action="append")
    ap.add_argument("--cards", default=T.CARDS)
    ap.add_argument("--ledger", default=T.LEDGER)
    ap.add_argument("--write", action="store_true")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    return run(a.cards, a.ledger, a.write, [x.upper() for x in a.ticker] if a.ticker else None)


if __name__ == "__main__":
    sys.exit(main())
