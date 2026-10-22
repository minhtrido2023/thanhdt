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
    python3 bin/rights_issue_alert.py --send                # gửi Trading Daily + ghi state

Sự kiện P/NULL "xác sống" (arch-review 2026-10-22 B1; BQ thật: 103 dòng Rights `P` chưa ngày, 40 dòng
cũ hơn 12 tháng): vendor hiếm khi dọn dòng P sau khi sự kiện đã thực hiện. Hai lớp lọc, đều thuần:
  · BỎ dòng P/NULL nếu CÙNG mã có dòng D cùng exercise_ratio, GDKHQ ≤ asof và SAU public_date của dòng P
    (ca DSC: D GDKHQ 2025-10-03 tỉ lệ 0,1725 còn 2 dòng P ⇒ trước đây phát 2 tin ANNOUNCE sai);
  · dòng P/NULL có public_date cũ hơn STALE_P_DAYS (=183 ngày ≈ 6 tháng — quá một quý, một đợt phát hành
    thật luôn có ngày GDKHQ trong khoảng đó) ⇒ KHÔNG báo như sự kiện sống, gộp 1 tin "nghi bỏ dở — kiểm
    VSDC" (mỗi dòng 1 lần). Ca SCL 2026 (D 2025 tỉ lệ 35,7% + P 08/09/2026 tỉ lệ 15,38%) KHÁC tỉ lệ và
    còn mới ⇒ vẫn ANNOUNCE.
Độ tươi vị thế (B2): tin in `computed_at` của active_nav_*.json; file cũ hơn phiên giao dịch TRƯỚC asof
hoặc thiếu account live (trading_bot.config.live_dnse_labels) ⇒ tin ghi "VỊ THẾ CÓ THỂ CŨ" và rc=3.
Mã thoát: 0 ổn · 1 gửi thất bại (state giữ nguyên) · 2 không có file vị thế nào · 3 đã chạy nhưng vị thế
có thể cũ. Env test: MIKE_RIGHTS_ALERT_NOTIFY (lệnh gửi, mặc định bin/notify_thread.sh),
MIKE_RIGHTS_ALERT_STATE, MIKE_RIGHTS_ALERT_NAV_GLOB.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import math
import os
import shlex
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
STALE_P_DAYS = 183                       # dòng P/NULL cũ hơn ngần này ngày ⇒ "nghi bỏ dở" (B1)
TRADING_DAILY_THREAD = "trading_daily"   # tên trong kb/discord_channels.json (notify_thread.sh nhận TÊN)
STATE_PATH = os.environ.get("MIKE_RIGHTS_ALERT_STATE") or os.path.join(MIKE, "state", "rights_issue_alert_state.json")
ACTIVE_NAV_GLOB = os.environ.get("MIKE_RIGHTS_ALERT_NAV_GLOB") or os.path.join(
    WC_ROOT, "data", "execution_logs", "active_nav_*.json")
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


def prev_session(asof, is_holiday):
    """Phiên giao dịch liền TRƯỚC `asof` (ISO) — mốc tươi tối thiểu của file vị thế."""
    d = dt.date.fromisoformat(asof)
    while True:
        d -= dt.timedelta(days=1)
        if d.weekday() < 5 and not is_holiday(d):
            return d.isoformat()


def _same_ratio(a, b):
    try:
        return abs(float(a.get("exercise_ratio") or 0) - float(b.get("exercise_ratio") or 0)) < 1e-6
    except (TypeError, ValueError):
        return False


def is_zombie_p(r, rows, asof):
    """Dòng P/NULL đã được dòng D cùng mã + cùng tỉ lệ (GDKHQ ≤ asof, sau public_date của P) thay thế."""
    if r.get("issue_status_code") != "P" or r.get("exright_date"):
        return False
    pub = (r.get("public_date") or "")[:10]
    for o in rows:
        ex = o.get("exright_date")
        if o is not r and o.get("ticker") == r["ticker"] and o.get("issue_status_code") == "D" \
                and ex and ex <= asof and ex > pub and _same_ratio(o, r):
            return True
    return False


def is_stale_p(r, asof):
    """Dòng P/NULL công bố cũ hơn STALE_P_DAYS ⇒ nghi bỏ dở, không phải sự kiện sống."""
    pub = (r.get("public_date") or "")[:10]
    if r.get("issue_status_code") != "P" or r.get("exright_date") or not pub:
        return False
    return (dt.date.fromisoformat(asof) - dt.date.fromisoformat(pub)).days > STALE_P_DAYS


def position_health(asof, meta, labels, is_holiday):
    """Ghi meta[lb]['stale']; trả list lý do vị thế có thể cũ (rỗng = ổn). labels None = không đọc được."""
    cutoff, notes = prev_session(asof, is_holiday), []
    for lb, m in sorted(meta.items()):
        m["stale"] = (m.get("computed_at") or "")[:10] < cutoff
        if m["stale"]:
            notes.append(f"{lb}: computed_at={m.get('computed_at') or '?'} cũ hơn phiên trước {cutoff}")
    if labels is None:
        notes.append("không đối chiếu được danh sách account live (trading_bot.config.live_dnse_labels lỗi)")
    elif [lb for lb in labels if lb not in meta]:
        notes.append("thiếu file vị thế account live: " + ", ".join(lb for lb in labels if lb not in meta))
    return notes


def build_alerts(asof, positions, rows, sent, is_holiday, meta=None, pos_notes=()):
    """positions: {account: {ticker: qty}}; rows: dòng Rights; sent: set khoá đã gửi.

    meta: {account: {file, computed_at, stale}} · pos_notes: lý do vị thế có thể cũ (position_health).
    Trả list {keys, stage, text}. Thuần — selfcheck gọi thẳng.
    """
    out, stale_rows, meta = [], [], meta or {}
    for r in rows:
        if r.get("issue_method_code") != "Rights" or r.get("issue_status_code") == "N" \
                or r.get("event_status") == "not_executed":
            continue
        tk, ex = r["ticker"], (r.get("exright_date") or None)
        if (r.get("public_date") or "")[:10] > asof:
            continue                          # chưa công bố tại asof (chạy hồi cứu) — không nhìn trước
        if ex and ex <= asof:
            continue                          # đã GDKHQ — hết thời điểm hành động
        if is_zombie_p(r, rows, asof):
            continue                          # sự kiện đã thực hiện (dòng D), dòng P là xác sống (B1)
        holders = [(lb, p[tk]) for lb, p in sorted(positions.items()) if p.get(tk, 0) > 0]
        if not holders:
            continue
        if is_stale_p(r, asof):
            if f"{r['id']}|stale" not in sent:
                stale_rows.append(r)
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
                 f"{ratio:.2%} (CP mới / CP đang giữ), trạng thái `{r.get('issue_status_code') or '?'}`, "
                 f"công bố {(r.get('public_date') or '?')[:10]}"]
        if ex:
            lines.append(f"  GDKHQ {ex} (còn {sessions_until(asof, ex, is_holiday)} phiên cum), "
                         f"ngày chốt {r.get('record_date') or 'CHƯA CÓ'}")
        else:
            lines.append("  CHƯA CÓ ngày GDKHQ/chốt (vendor chưa điền) — sẽ báo lại khi có ngày")
        lines.append(f"  giá phát hành: {f'{px:,.0f}đ' if px else 'CHƯA CÓ (BQ chưa điền)'}; {NO_DEADLINE}")
        for lb, q in holders:
            n = math.floor(q * ratio + 1e-9)
            cash = f"{n * px:,.0f}đ" if px else "chưa tính được (chưa có giá)"
            m = meta.get(lb) or {}
            src = f" [nguồn {m.get('file') or 'active_nav'} computed_at={m.get('computed_at') or '?'}" \
                  f"{' ⚠️ CŨ' if m.get('stale') else ''}]"
            lines.append(f"  {lb}: giữ {q:,} cp ⇒ được mua {n:,} cp, tiền cần chuẩn bị {cash}{src}")
        if pos_notes:
            lines.append("  ⚠️ VỊ THẾ CÓ THỂ CŨ — tự kiểm trên DNSE (" + "; ".join(pos_notes) + ")")
        # TODO(X1, job Taylor_20261022_022942): khi auto_exit_inject giữ lệnh thoát tới GDKHQ được merge,
        # đổi câu dưới thành "Bot tự giữ lệnh thoát tới GDKHQ".
        lines.append("  Bot CHƯA tự giữ lệnh thoát tới GDKHQ — nếu là mã LAG và ngày thoát T+25 rơi TRƯỚC "
                     "GDKHQ thì phải HOLD TAY lệnh thoát. User TỰ thực hiện quyền đầy đủ (bot không "
                     "mua/chuyển nhượng quyền). Sau khi nộp tiền NAV có thể chặn rc=5/6 — xử lý theo tiền "
                     "lệ MBB 08-28 (REPORT lag_rights_audit_20261022).")
        out.append({"keys": [k for _, k in todo], "stage": stage, "text": "\n".join(lines)})
    if stale_rows:
        items = "; ".join(f"{r['ticker']} (công bố {(r.get('public_date') or '?')[:10]}, tỉ lệ "
                          f"{float(r.get('exercise_ratio') or 0):.2%})" for r in stale_rows)
        out.append({"keys": [f"{r['id']}|stale" for r in stale_rows], "stage": "STALE",
                    "text": f"🔸 Quyền mua nghi BỎ DỞ — dòng `P` không ngày, công bố > {STALE_P_DAYS} ngày, "
                            f"KHÔNG báo như sự kiện sống; kiểm VSDC/công ty nếu cần: {items}"})
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
    """-> ({account: {ticker: qty}}, {account: {file, computed_at}})."""
    out, meta = {}, {}
    for path in sorted(glob.glob(nav_glob)):
        with open(path) as fh:
            d = json.load(fh)
        lb = d.get("account") or os.path.basename(path)
        out[lb] = {p["ticker"]: int(p.get("qty") or 0) for p in d.get("positions") or [] if p.get("ticker")}
        meta[lb] = {"file": os.path.basename(path), "computed_at": d.get("computed_at")}
    return out, meta


def live_labels():
    from trading_bot.config import live_dnse_labels
    return live_dnse_labels()


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
    ap.add_argument("--nav-glob", default=ACTIVE_NAV_GLOB)
    a = ap.parse_args()
    from trading_bot.vn_market import is_holiday
    pos, meta = read_positions(a.nav_glob)
    if not pos:
        print(f"❌ không tìm thấy file vị thế nào khớp {a.nav_glob} — không kết luận được 'không giữ mã nào'")
        return 2
    try:
        labels = live_labels()
    except Exception as e:                    # §29: in bằng chứng thật, không đoán nguyên nhân
        labels = None
        print(f"⚠️ không đọc được danh sách account live: {e!r}")
    notes = position_health(a.asof, meta, labels, is_holiday)
    if notes:
        print("⚠️ VỊ THẾ CÓ THỂ CŨ — " + "; ".join(notes))
    stale_rc = 3 if notes else 0
    tickers = {t for p in pos.values() for t, q in p.items() if q > 0}
    if not tickers:
        print("không có vị thế nào trong active_nav_*.json")
        return stale_rc
    rows = fetch_rights(tickers)
    sent = _load_sent(a.state) if a.send else set()
    alerts = build_alerts(a.asof, pos, rows, sent, is_holiday, meta, notes)
    if not alerts:
        print(f"[{a.asof}] không có quyền mua nào cần báo cho {len(tickers)} mã đang giữ")
    notify = shlex.split(os.environ.get("MIKE_RIGHTS_ALERT_NOTIFY") or os.path.join(MIKE, "bin", "notify_thread.sh"))
    for al in alerts:
        print(al["text"])
        if not a.send:
            continue
        r = subprocess.run(notify + [al["text"], TRADING_DAILY_THREAD], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"❌ gửi thất bại rc={r.returncode}: {(r.stderr or r.stdout).strip()[:300]} — CHƯA ghi state")
            return 1
        sent |= set(al["keys"])
        _save_sent(a.state, sent)              # ghi NGAY sau mỗi lần gửi (§5)
    return stale_rc


if __name__ == "__main__":
    sys.exit(main())
