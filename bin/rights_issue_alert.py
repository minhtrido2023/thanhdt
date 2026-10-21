#!/usr/bin/env python3
"""Cảnh báo QUYỀN MUA (rights issue) cho mã ĐANG GIỮ — CHỈ CẢNH BÁO, không chạm lệnh/NAV/sizing.

Vì sao có file này (audit 2026-10-22, agents/Taylor/research/lag_rights_audit_20261022/REPORT.md):
`corp_action_daily.upcoming_events` chỉ thấy sự kiện khi vendor đã điền `exright_date` và nằm
trong 10 ngày tới (thực tế ~2 phiên trước GDKHQ); dòng trạng thái `P` ngày NULL bị bỏ qua im lặng;
không cảnh báo nào có số CP được mua / giá / số tiền. Luật user 2026-10-21: mã LAG có quyền mua
trong thời gian giữ ⇒ KHÔNG bán trước GDKHQ, user TỰ mua đủ quyền ⇒ user cần biết SỚM và đủ số.

Ba giai đoạn, mỗi giai đoạn dedupe theo khoá riêng (state chỉ ghi SAU khi gửi thành công):
  ANNOUNCE  lần đầu thấy sự kiện (kể cả trạng thái P, chưa có ngày/giá)      khoá id|announce
  DATED     lần đầu thấy một exright_date (đổi ngày ⇒ báo lại)               khoá id|dated|<ex>
  REMIND    còn ≤ REMIND_SESSIONS phiên tới GDKHQ — mỗi phiên một lần         khoá id|remind|<ex>|<asof>

    python3 bin/rights_issue_alert.py                       # dry-run: in ra, không gửi, không ghi state
    python3 bin/rights_issue_alert.py --asof 2025-10-14     # hồi cứu
    python3 bin/rights_issue_alert.py --send                # gửi Trading Daily + ghi state (CHƯA wire cron)
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import math
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

WC_ROOT = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
MIKE = os.path.join(WC_ROOT, "mike")
HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (WC_ROOT, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
REMIND_SESSIONS = 3
TRADING_DAILY_THREAD = "trading_daily"   # tên trong kb/discord_channels.json (notify_thread.sh nhận TÊN)
STATE_PATH = os.path.join(MIKE, "state", "rights_issue_alert_state.json")
ACTIVE_NAV_GLOB = os.path.join(WC_ROOT, "data", "execution_logs", "active_nav_*.json")
NO_DEADLINE = ("hạn đăng ký/nộp tiền: tav2_bq.corporate_action KHÔNG có cột này — tra thông báo "
               "VSDC/công ty hoặc DNSE")


def sessions_until(asof, ex, is_holiday):
    """Số phiên giao dịch từ sau `asof` tới hết ngày TRƯỚC GDKHQ (= số phiên còn mua/giữ cum)."""
    d, n = dt.date.fromisoformat(asof), 0
    end = dt.date.fromisoformat(ex)
    while d < end - dt.timedelta(days=1):
        d += dt.timedelta(days=1)
        if d.weekday() < 5 and not is_holiday(d):
            n += 1
    return n


def issue_price(r):
    """Giá phát hành: value_per_share nếu vendor điền, else total_value/issue_volumn; không có ⇒ None."""
    try:
        v = float(r.get("value_per_share") or 0)
        if v > 0:
            return v
        tv, vol = float(r.get("total_value") or 0), float(r.get("issue_volumn") or 0)
        return tv / vol if tv > 0 and vol > 0 else None
    except (TypeError, ValueError):
        return None


def build_alerts(asof, positions, rows, sent, is_holiday):
    """positions: {account: {ticker: qty}}; rows: dòng Rights; sent: set khoá đã gửi.

    Trả list {key, stage, text}. Thuần — selfcheck gọi thẳng.
    """
    out = []
    for r in rows:
        if r.get("issue_method_code") != "Rights" or r.get("issue_status_code") == "N" \
                or r.get("event_status") == "not_executed":
            continue
        tk, ex = r["ticker"], (r.get("exright_date") or None)
        if (r.get("public_date") or "")[:10] > asof:
            continue                          # chưa công bố tại asof (chạy hồi cứu) — không nhìn trước
        if ex and ex <= asof:
            continue                          # đã GDKHQ — hết thời điểm hành động
        holders = [(lb, p[tk]) for lb, p in sorted(positions.items()) if p.get(tk, 0) > 0]
        if not holders:
            continue
        stages = [("ANNOUNCE", f"{r['id']}|announce")]
        if ex:
            stages.append(("DATED", f"{r['id']}|dated|{ex}"))
            left = sessions_until(asof, ex, is_holiday)
            if left <= REMIND_SESSIONS:
                stages.append(("REMIND", f"{r['id']}|remind|{ex}|{asof}"))
        todo = [(s, k) for s, k in stages if k not in sent]
        if not todo:
            continue
        stage = todo[-1][0]                   # 1 tin/ sự kiện/ lượt: giai đoạn muộn nhất bao trùm
        ratio = float(r.get("exercise_ratio") or 0)
        px = issue_price(r)
        lines = [f"{'⏰' if stage == 'REMIND' else '📣'} **{tk}** QUYỀN MUA ({stage}) — tỉ lệ "
                 f"{ratio:.2%} (CP mới / CP đang giữ), trạng thái `{r.get('issue_status_code') or '?'}`"]
        if ex:
            lines.append(f"  GDKHQ {ex} (còn {sessions_until(asof, ex, is_holiday)} phiên cum), "
                         f"ngày chốt {r.get('record_date') or 'CHƯA CÓ'}")
        else:
            lines.append("  CHƯA CÓ ngày GDKHQ/chốt (vendor chưa điền) — sẽ báo lại khi có ngày")
        lines.append(f"  giá phát hành: {f'{px:,.0f}đ' if px else 'CHƯA CÓ (BQ chưa điền)'}; {NO_DEADLINE}")
        for lb, q in holders:
            n = math.floor(q * ratio + 1e-9)
            cash = f"{n * px:,.0f}đ" if px else "chưa tính được (chưa có giá)"
            lines.append(f"  {lb}: giữ {q:,} cp ⇒ được mua {n:,} cp, tiền cần chuẩn bị {cash}")
        lines.append("  Luật 21/10: mã LAG — KHÔNG bán trước GDKHQ; user TỰ thực hiện quyền đầy đủ "
                     "(bot không mua/chuyển nhượng quyền). Sau khi nộp tiền NAV có thể chặn rc=5/6 — "
                     "xử lý theo tiền lệ MBB 08-28 (REPORT lag_rights_audit_20261022).")
        out.append({"keys": [k for _, k in todo], "stage": stage, "text": "\n".join(lines)})
    return out


def fetch_rights(tickers):
    from corp_action_lib import TABLE, bq
    tk = ",".join(f'"{t}"' for t in sorted(tickers))
    return bq(f"""
        SELECT c.id, c.ticker, c.issue_method_code, c.issue_status_code, c.event_status,
               CAST(c.exright_date AS STRING) exright_date, CAST(c.record_date AS STRING) record_date,
               CAST(c.public_date AS STRING) public_date, c.exercise_ratio, c.value_per_share,
               c.total_value, c.issue_volumn
        FROM `{TABLE}` AS c
        WHERE c.ticker IN ({tk}) AND c.event_code = "ISS" AND c.issue_method_code = "Rights"
        ORDER BY c.ticker, c.public_date""")


def read_positions(nav_glob=ACTIVE_NAV_GLOB):
    out = {}
    for path in sorted(glob.glob(nav_glob)):
        with open(path) as fh:
            d = json.load(fh)
        out[d.get("account") or os.path.basename(path)] = {
            p["ticker"]: int(p.get("qty") or 0) for p in d.get("positions") or [] if p.get("ticker")}
    return out


def _load_sent(path):
    try:
        with open(path) as fh:
            return set(json.load(fh).get("sent") or [])
    except FileNotFoundError:
        return set()


def _save_sent(path, sent):
    tmp = f"{path}.tmp"
    with open(tmp, "w") as fh:
        json.dump({"sent": sorted(sent)}, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asof", default=dt.datetime.now(ICT).date().isoformat())
    ap.add_argument("--send", action="store_true")
    ap.add_argument("--state", default=STATE_PATH)
    a = ap.parse_args()
    from trading_bot.vn_market import is_holiday
    pos = read_positions()
    if not pos:
        print(f"❌ không tìm thấy file vị thế nào khớp {ACTIVE_NAV_GLOB} — không kết luận được 'không giữ mã nào'")
        return 2
    tickers = {t for p in pos.values() for t, q in p.items() if q > 0}
    if not tickers:
        print("không có vị thế nào trong active_nav_*.json")
        return 0
    rows = fetch_rights(tickers)
    sent = _load_sent(a.state) if a.send else set()
    alerts = build_alerts(a.asof, pos, rows, sent, is_holiday)
    if not alerts:
        print(f"[{a.asof}] không có quyền mua nào cần báo cho {len(tickers)} mã đang giữ")
    for al in alerts:
        print(al["text"])
        if not a.send:
            continue
        r = subprocess.run([os.path.join(MIKE, "bin", "notify_thread.sh"), al["text"], TRADING_DAILY_THREAD],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"❌ gửi thất bại rc={r.returncode}: {(r.stderr or r.stdout).strip()[:300]} — CHƯA ghi state")
            return 1
        sent |= set(al["keys"])
        _save_sent(a.state, sent)              # ghi NGAY sau mỗi lần gửi (§5)
    return 0


if __name__ == "__main__":
    sys.exit(main())
