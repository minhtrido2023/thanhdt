#!/usr/bin/env python3
"""thesis_card_watch.py — nhắc mốc theo THẺ LUẬN ĐIỂM discretionary (B3, 22/11/2026). CHỈ ĐỌC + in/POST.

KHÔNG ghi plan/sổ/lệnh, không đụng luật thoát. Ba nhóm nhắc:
  (a) milestone `pending` đến hạn ≤3 ngày hoặc QUÁ HẠN chưa chấm;
  (b) vị thế lỗ ≥15% so giá vốn ⇒ "mở rà 48h theo thẻ" (KHÔNG phải lệnh bán/stop). Giá + giá vốn lấy từ bản ghi
      `positions` mới nhất của dnse_raw_*.jsonl (DNSE), nêu nguồn + thời điểm;
  (c) thẻ `last_review_at` > 30 ngày.
Dùng: thesis_card_watch.py [--dry-run] [--asof YYYY-MM-DD] [--notify]
  --notify: gọi bin/notify_thread.sh tới topic `discretionary_stocks` (tên trong kb/discord_channels.json).
rc: 0 = chạy được · 1 = không dựng được (sổ lỗi/thiếu dữ liệu giá không phải lỗi — nói rõ trong khối).
"""
import argparse
import datetime as dt
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import thesis_cards as T  # noqa: E402

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")
DUE_DAYS = 3
LOSS_PCT = 15
STALE_REVIEW_DAYS = 30
PRICE_STALE_DAYS = 4        # bản ghi positions cũ hơn thế (so asof) ⇒ cảnh báo giá cũ
NOTIFY_CHANNEL = "discretionary_stocks"


def _vn(x, nd, sign=False):
    """Số kiểu VN: '.' hàng nghìn, ',' thập phân (chỉ định dạng SỐ, không đụng chuỗi khác)."""
    s = f"{x:{'+' if sign else ''},.{nd}f}"
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def _d(s):
    return dt.date.fromisoformat(s)


def build(doc, asof, pos, ts, fname, notes=None):
    """→ (lines, n_alerts). Pure — selfcheck bơm dữ liệu."""
    cards = {t: c for t, c in T.latest_cards(doc).items() if c.get("status") == "active"}
    out, n = [], 0
    out.append(f"THẺ LUẬN ĐIỂM — nhắc mốc {asof:%d/%m/%Y} (CHỈ HIỂN THỊ; không phải lệnh bán/stop)")
    # (a)
    a = []
    for t, c in sorted(cards.items()):
        for m in c.get("milestones", []):
            if m.get("status") != "pending":
                continue
            days = (_d(m["date"]) - asof).days
            if days <= DUE_DAYS:
                tag = f"QUÁ HẠN {-days} ngày" if days < 0 else ("HÔM NAY" if days == 0 else f"còn {days} ngày")
                a.append(f"- {t} {m['id']} [{tag}] {m['date']} ({m.get('date_basis', '')}): {m['metric']} — "
                         f"ngưỡng: {m['threshold']} — nguồn: {m['source']}")
    out.append(f"(a) Mốc đến hạn ≤{DUE_DAYS} ngày / quá hạn chưa chấm: {len(a) or 'không có'}")
    out += a
    n += len(a)
    # (b)
    b = []
    if not pos:
        b.append("⚠️ KHÔNG đọc được giá vị thế: không có bản ghi `positions` trong dnse_raw_*.jsonl "
                 f"(thư mục {T.EXEC_DIR}) — không đánh giá được ngưỡng −{LOSS_PCT}%")
    for acc in T.ACCOUNTS:
        if acc not in pos:
            if pos:
                b.append(f"⚠️ {acc}: không có bản ghi positions trong {fname} — bỏ qua account này (không đoán)")
            continue
        age = None
        if ts.get(acc):
            age = (asof - _d(ts[acc][:10])).days
        for t, c in sorted(cards.items()):
            if acc not in c.get("accounts", []):
                continue
            p = pos[acc].get(t)
            if not p:
                b.append(f"⚠️ {acc} {t}: thẻ active nhưng KHÔNG có vị thế trong {fname} — thẻ lỗi thời? (kiểm sổ lô)")
                continue
            cost, mkt = p.get("cost"), p.get("market")
            if not cost or not mkt:
                b.append(f"⚠️ {acc} {t}: thiếu costPrice/marketPrice trong bản ghi — không tính được")
                continue
            pnl = (mkt / cost - 1) * 100
            line = (f"{acc} {t}: giá {_vn(mkt, 0)} vs vốn {_vn(cost, 1)} = {_vn(pnl, 1, True)}% "
                    f"(DNSE positions {ts.get(acc)}, file {fname})")
            if pnl <= -LOSS_PCT:
                b.append(f"- 🔔 {line} ⇒ MỞ RÀ 48 GIỜ THEO THẺ (không phải lệnh bán). Thẻ: kb/thesis_cards.json "
                         f"{t} rev{c['rev']}, mốc/abandon_triggers cần chấm lại.")
                n += 1
            else:
                b.append(f"- {line} — chưa chạm −{LOSS_PCT}%")
            if age is not None and age > PRICE_STALE_DAYS:
                b.append(f"  ⚠️ giá cũ {age} ngày so với {asof:%d/%m} — không phải đóng cửa gần nhất")
    out.append(f"(b) Vị thế vs giá vốn (ngưỡng rà −{LOSS_PCT}%):")
    out += b
    # (c)
    c_ = []
    for t, c in sorted(cards.items()):
        d = (asof - _d(c["last_review_at"])).days
        if d > STALE_REVIEW_DAYS:
            c_.append(f"- {t}: last_review_at {c['last_review_at']} ({d} ngày) — rà lại thẻ")
    out.append(f"(c) Thẻ quá {STALE_REVIEW_DAYS} ngày chưa rà: {len(c_) or 'không có'}")
    out += c_
    n += len(c_)
    drafts = [t for t, c in sorted(cards.items()) if c.get("draft_pending_user_review")]
    if drafts:
        out.append(f"ℹ️ Thẻ còn nháp chờ user duyệt: {', '.join(drafts)}")
    for x in notes or []:
        out.append(f"ℹ️ {x}")
    return out, n


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="chỉ in, không POST (mặc định cũng chỉ in)")
    ap.add_argument("--asof", help="YYYY-MM-DD (mặc định: hôm nay ICT)")
    ap.add_argument("--notify", action="store_true", help="POST khối qua notify_thread.sh tới topic discretionary")
    a = ap.parse_args(argv)
    asof = _d(a.asof) if a.asof else dt.datetime.now(_ICT).date()
    try:
        doc = T.read_json(T.CARDS)
        errs = T.validate(doc, T.read_json(T.LEDGER)["entries"], None)
    except Exception as e:  # noqa: BLE001
        print(f"LỖI: không đọc được sổ thẻ/sổ giá: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    notes = []
    if errs:
        notes.append(f"sổ thẻ có {len(errs)} lỗi invariant (chạy bin/thesis_cards_selfcheck.py): {errs[0]}")
    pos, ts, fname = T.raw_positions()
    lines, n = build(doc, asof, pos, ts, fname, notes)
    text = "\n".join(lines)
    print(text)
    print(f"\n[nguồn: kb/thesis_cards.json; giá: {fname}; asof {asof}; alerts={n}; notify={'ON' if a.notify and not a.dry_run else 'off'}]")
    if a.notify and not a.dry_run:
        cmd = os.environ.get("TCW_NOTIFY_CMD") or os.path.join(T.MIKE, "bin", "notify_thread.sh")
        r = subprocess.run([cmd, text, NOTIFY_CHANNEL], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"LỖI notify rc={r.returncode}: {r.stderr.strip() or r.stdout.strip()}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
