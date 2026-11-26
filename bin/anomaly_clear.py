#!/usr/bin/env python3
"""anomaly_clear.py — ghi 1 dòng gỡ cờ bất thường SAU KHI user duyệt (data/anomaly_clearances.json).

  anomaly_clear.py TICKER FLAG_DATE VERDICT --evidence "..." --approval-ref "<link tin nhắn duyệt>" \
      --decided-by user [--dry-run]

Chỉ nhận cờ đang tồn tại đúng ngày; BAD_COMPANY bị từ chối; NONE_FOUND phải đủ 7 ngày."""
import argparse, datetime, json, os, sys

WC = "/home/trido/thanhdt/WorkingClaude"
VERDICTS = ("SECTOR_OR_MARKET", "TECHNICAL", "NONE_FOUND")
NONE_FOUND_MIN_DAYS = 7


def main(argv=None, wc=WC):
    ap = argparse.ArgumentParser()
    ap.add_argument("ticker"), ap.add_argument("flag_date"), ap.add_argument("verdict", choices=VERDICTS)
    ap.add_argument("--evidence", required=True), ap.add_argument("--approval-ref", required=True)
    ap.add_argument("--decided-by", required=True, choices=["user"])
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if os.environ.get("JOB_ID"):
        sys.exit("TỪ CHỐI: đang chạy trong job headless (JOB_ID) — chỉ phiên tương tác với user mới được "
                 "ghi gỡ cờ. Agent chỉ đề xuất qua bus question.")
    today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).date()
    with open(os.path.join(wc, "data", "anomaly_flags.json"), encoding="utf-8") as fh:
        flag = json.load(fh).get(a.ticker) or {}
    if flag.get("last_alert") != a.flag_date:
        sys.exit(f"không có cờ {a.ticker} ngày {a.flag_date} (cờ hiện tại: {flag.get('last_alert')})")
    if not a.evidence.strip() or not a.approval_ref.strip():
        sys.exit("evidence / approval-ref rỗng")
    age = (today - datetime.date.fromisoformat(a.flag_date)).days
    if a.verdict == "NONE_FOUND" and age < NONE_FOUND_MIN_DAYS:
        sys.exit(f"NONE_FOUND cần cờ cũ >= {NONE_FOUND_MIN_DAYS} ngày (mới {age})")
    path = os.path.join(wc, "data", "anomaly_clearances.json")
    doc = {"clearances": []}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)          # hỏng ⇒ raise, KHÔNG ghi đè
    row = {"ticker": a.ticker, "flag_date": a.flag_date, "verdict": a.verdict, "decided_by": a.decided_by,
           "decided_on": str(today), "evidence": a.evidence, "approval_ref": a.approval_ref}
    print(json.dumps(row, ensure_ascii=False, indent=1))
    if a.dry_run:
        return row
    doc["clearances"] = [c for c in doc["clearances"]
                         if (c.get("ticker"), c.get("flag_date")) != (a.ticker, a.flag_date)] + [row]
    with open(path + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    os.replace(path + ".tmp", path)
    print(f"✅ đã ghi {path}")
    return row


if __name__ == "__main__":
    main()
