#!/usr/bin/env python3
"""Cảnh báo TĂNG VỐN (quyền mua + MỌI phương thức phát hành) cho mã ĐANG GIỮ — CHỈ CẢNH BÁO, không chạm
lệnh/NAV/sizing/plan.

Mở rộng 29/10/2026 (user: "nên đưa warning khi có bất kỳ việc tăng vốn nào xuất hiện trong chu kỳ đầu tư";
REPORT agents/Taylor/research/capital_raise_warning_20261029/): ngoài Rights nay báo cả WARN (riêng lẻ,
công chúng, ESOP, chuyển đổi, sáp nhập) và INFO (cổ tức CP, thưởng) — phân loại ở bin/capital_raise_lib.py.
Mỗi tin có % pha loãng, giá phát hành so thị giá (giá trong active_nav), khoảng cách tới ngày chốt.
Khoá dedupe GIỮ NGUYÊN định dạng cũ (state cũ vẫn hợp lệ); REMIND chỉ cho Rights (cần user hành động).

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
LỌC THEO CHU KỲ NẮM GIỮ (user 29/10/2026 15:5x, `decided_by: user`): chỉ cảnh báo khi NGÀY CHỐT quyền (record_date,
thiếu thì GDKHQ) rơi vào CHU KỲ NẮM GIỮ của một lô thuộc book LAG (T+25 phiên) hoặc BAL (T+45 phiên) — tức
entry_date ≤ ngày chốt VÀ số phiên entry→ngày chốt ≤ hạn của book (hằng số `auto_exit_rules`). Tin nêu ĐÚNG book + lô
+ phiên thứ mấy của chu kỳ. Mã không thuộc LAG/BAL (park, CAPIT, custom30V, discretionary…) ⇒ im. Sự kiện CHƯA có ngày
chốt ⇒ chưa thể rơi vào chu kỳ ⇒ im (đếm ra stdout; có ngày sẽ báo qua giai đoạn DATED). Nguồn lô = sổ lô
`portfolio_status.book_lot_snapshot`. Không dựng được sổ lô (lỗi) hoặc mã bị sổ lô chặn (unverified) ⇒ FAIL-OPEN: vẫn cảnh
báo, nói rõ "không lọc được theo chu kỳ" (thà thừa một tin hơn lỡ một đợt tăng vốn). Dòng "nghi bỏ dở" (P cũ không ngày)
cũng im khi lọc hoạt động.
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

from capital_raise_lib import (METHOD_VI, STALE_P_DAYS, dilution, is_stale_p, is_zombie_p,  # noqa: E402,F401
                               issue_price, live_events, severity)

from auto_exit_rules import BAL_EXIT_SESSIONS, LAG_EXIT_SESSIONS  # noqa: E402

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
REMIND_SESSIONS = 3
CYCLE_BOOKS = (("LAG", LAG_EXIT_SESSIONS), ("BAL", BAL_EXIT_SESSIONS))   # (book, số phiên giữ cố định)
TRADING_DAILY_THREAD = "trading_daily"   # tên trong kb/discord_channels.json (notify_thread.sh nhận TÊN)
STATE_PATH = os.environ.get("MIKE_RIGHTS_ALERT_STATE") or os.path.join(MIKE, "state", "rights_issue_alert_state.json")
ACTIVE_NAV_GLOB = os.environ.get("MIKE_RIGHTS_ALERT_NAV_GLOB") or os.path.join(
    WC_ROOT, "data", "execution_logs", "active_nav_*.json")
NO_DEADLINE = ("hạn đăng ký/nộp tiền: tav2_bq.corporate_action KHÔNG có cột này — tra thông báo "
               "VSDC/công ty hoặc DNSE")
NO_PURPOSE = ("mục đích sử dụng vốn: nguồn KHÔNG có (event_description_vi rỗng ở 100% dòng ISS 2025-26) — "
              "đọc NQ ĐHCĐ/phương án phát hành")


def sessions_until(asof, ex, is_holiday):
    """Số phiên giao dịch từ sau `asof` tới hết ngày TRƯỚC GDKHQ (= số phiên còn mua/giữ cum)."""
    d, n = dt.date.fromisoformat(asof), 0
    end = dt.date.fromisoformat(ex)
    while d < end - dt.timedelta(days=1):
        d += dt.timedelta(days=1)
        if d.weekday() < 5 and not is_holiday(d):
            n += 1
    return n


def prev_session(asof, is_holiday):
    """Phiên giao dịch liền TRƯỚC `asof` (ISO) — mốc tươi tối thiểu của file vị thế."""
    d = dt.date.fromisoformat(asof)
    while True:
        d -= dt.timedelta(days=1)
        if d.weekday() < 5 and not is_holiday(d):
            return d.isoformat()


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


def sessions_to(asof, d, is_holiday):
    """Số phiên giao dịch trong (asof, d] — khoảng cách tới ngày chốt."""
    cur, n, end = dt.date.fromisoformat(asof), 0, dt.date.fromisoformat(d)
    while cur < end:
        cur += dt.timedelta(days=1)
        if cur.weekday() < 5 and not is_holiday(cur):
            n += 1
    return n


def _price_line(r, tk, prices):
    """Giá phát hành so thị giá (giá trong active_nav — DNSE G1 lúc tính NAV)."""
    px, mkt = issue_price(r), (prices or {}).get(tk)
    if not px:
        return "giá phát hành: CHƯA CÓ (BQ chưa điền)"
    if mkt:
        return f"giá phát hành: {px:,.0f}đ = {px / mkt:.0%} thị giá {mkt:,.0f}đ (giá active_nav)"
    return f"giá phát hành: {px:,.0f}đ (không có thị giá để so)"


def event_cycle_date(r):
    """Ngày chốt quyền dùng để xét chu kỳ: record_date, thiếu thì GDKHQ; None nếu chưa có ngày nào."""
    return (r.get("record_date") or r.get("exright_date") or None)


def cycle_hits(d, lots, is_holiday):
    """Các lô LAG/BAL mà ngày chốt `d` (YYYY-MM-DD) rơi vào chu kỳ nắm giữ. Thuần.

    lots = [{'book','entry','qty'}] (lô thật) hoặc [{'book','unknown': lý_do}] (sổ lô không xác nhận được ⇒ fail-open).
    Trả [(lô, số_phiên_entry→chốt | None, hạn_book)]. Rơi vào chu kỳ ⇔ entry ≤ d và phiên(entry→d) ≤ hạn."""
    hits, limits = [], dict(CYCLE_BOOKS)
    for l in lots:
        n = limits.get(l.get("book"))
        if n is None:
            continue
        if "unknown" in l:
            hits.append((l, None, n))
            continue
        if l["entry"] > d:
            continue
        k = sessions_to(l["entry"], d, is_holiday)
        if k <= n:
            hits.append((l, k, n))
    return hits


def build_alerts(asof, positions, rows, sent, is_holiday, meta=None, pos_notes=(), prices=None, oshares=None,
                 cycles=None, diag=None, cycle_err=None):
    """positions: {account: {ticker: qty}}; rows: dòng ISS (mọi phương thức); sent: set khoá đã gửi.

    meta: {account: {file, computed_at, stale}} · pos_notes: lý do vị thế có thể cũ (position_health) ·
    prices: {ticker: thị giá} · oshares: {ticker: CP lưu hành} (để tính % khi exercise_ratio = 0).
    cycles: {account: {ticker: [{'book','entry','qty'} | {'book','unknown'}]}} — sổ lô LAG/BAL; None ⇒ KHÔNG lọc
    theo chu kỳ (hành vi cũ / fail-open khi không dựng được sổ lô). diag: list nhận dòng chẩn đoán (sự kiện bị
    bỏ vì chưa có ngày chốt / ngoài chu kỳ). cycle_err: lý do không dựng được sổ lô (cycles=None) ⇒ tin ghi rõ không lọc.
    Trả list {keys, stage, text}. Thuần — selfcheck gọi thẳng.
    """
    out, stale_rows, meta = [], [], meta or {}
    held = {t for p in positions.values() for t, q in p.items() if q > 0}
    live, stale = live_events([r for r in rows if r.get("ticker") in held], asof)
    for r in stale:
        if cycles is None and f"{r['id']}|stale" not in sent:
            stale_rows.append(r)
        elif cycles is not None and diag is not None:
            diag.append(f"{r['ticker']}: dòng P nghi bỏ dở {r['id']} — im (lọc theo chu kỳ)")
    for r in live:
        tk, ex, meth = r["ticker"], (r.get("exright_date") or None), r.get("issue_method_code")
        rights, sev = meth == "Rights", severity(r)
        holders = [(lb, p[tk]) for lb, p in sorted(positions.items()) if p.get(tk, 0) > 0]
        hit_lines = {}
        if cycles is not None:
            d = event_cycle_date(r)
            if not d:
                if diag is not None:
                    diag.append(f"{tk}: {meth} {r['id']} CHƯA có ngày chốt/GDKHQ — chưa xét được chu kỳ (sẽ báo khi có ngày)")
                continue
            for lb, q in list(holders):
                hs = cycle_hits(d, (cycles.get(lb) or {}).get(tk) or [], is_holiday)
                if not hs:
                    holders.remove((lb, q))
                    continue
                hit_lines[lb] = [
                    (f"{l['book']}: KHÔNG xác định được chu kỳ — sổ lô không xác nhận ({l['unknown']})" if k is None else
                     f"{l['book']}: ngày chốt {d} rơi phiên thứ {k}/{n} của chu kỳ {l['book']} (lô {l['qty']:,} cp, entry {l['entry']})")
                    for l, k, n in hs]
            if not holders:
                if diag is not None:
                    diag.append(f"{tk}: {meth} {r['id']} ngày chốt {d} NGOÀI chu kỳ LAG/BAL của mọi lô — im")
                continue
        stages = [("ANNOUNCE", f"{r['id']}|announce")]
        if ex:
            stages.append(("DATED", f"{r['id']}|dated|{ex}"))
            left = sessions_until(asof, ex, is_holiday)
            if rights and left <= REMIND_SESSIONS:
                stages.append(("REMIND", f"{r['id']}|remind|{ex}|{asof}"))
        todo = [(s, k) for s, k in stages if k not in sent]
        if not todo:
            continue
        stage = todo[-1][0]                   # 1 tin/ sự kiện/ lượt: giai đoạn muộn nhất bao trùm
        ratio = float(r.get("exercise_ratio") or 0)
        dil = dilution(r, (oshares or {}).get(tk))
        dil_s = f"pha loãng {dil:.2%} số CP" if dil is not None else "pha loãng CHƯA RÕ (BQ chưa có tỉ lệ/khối lượng)"
        icon = "⏰" if stage == "REMIND" else ("📣" if sev == "WARN" else "ℹ️")
        kind = ("QUYỀN MUA" if rights else
                f"TĂNG VỐN {METHOD_VI.get(meth, meth)}" + (" — thu tiền/pha loãng" if sev == "WARN"
                                                           else " — KHÔNG thu tiền"))
        lines = [f"{icon} **{tk}** {kind} ({sev} · {stage}) — "
                 + (f"tỉ lệ {ratio:.2%} (CP mới / CP đang giữ), " if rights else "")
                 + f"{dil_s}, trạng thái `{r.get('issue_status_code') or '?'}`, "
                 f"công bố {(r.get('public_date') or '?')[:10]}"]
        rec = r.get("record_date")
        rec_s = f"{rec} (còn {sessions_to(asof, rec, is_holiday)} phiên)" if rec and rec > asof else (rec or "CHƯA CÓ")
        if ex:
            lines.append(f"  GDKHQ {ex} (còn {sessions_until(asof, ex, is_holiday)} phiên cum), ngày chốt {rec_s}")
        else:
            lines.append("  CHƯA CÓ ngày GDKHQ/chốt (vendor chưa điền) — sẽ báo lại khi có ngày")
        lines.append(f"  {_price_line(r, tk, prices)}" + (f"; {NO_DEADLINE}" if rights else ""))
        if sev == "WARN":
            lines.append(f"  {NO_PURPOSE}")
        for lb, q in holders:
            m = meta.get(lb) or {}
            src = f" [nguồn {m.get('file') or 'active_nav'} computed_at={m.get('computed_at') or '?'}" \
                  f"{' ⚠️ CŨ' if m.get('stale') else ''}]"
            if rights:
                n = math.floor(q * ratio + 1e-9)
                px = issue_price(r)
                cash = f"{n * px:,.0f}đ" if px else "chưa tính được (chưa có giá)"
                lines.append(f"  {lb}: giữ {q:,} cp ⇒ được mua {n:,} cp, tiền cần chuẩn bị {cash}{src}")
            else:
                lines.append(f"  {lb}: giữ {q:,} cp{src}")
            for hl in hit_lines.get(lb, []):
                lines.append(f"    ↳ {hl}")
        if cycles is None and cycle_err:
            lines.append(f"  ⚠️ KHÔNG lọc được theo chu kỳ LAG/BAL (fail-open, báo mọi mã đang giữ): {cycle_err}")
        if pos_notes:
            lines.append("  ⚠️ VỊ THẾ CÓ THỂ CŨ — tự kiểm trên DNSE (" + "; ".join(pos_notes) + ")")
        if rights:
            # X1 (lag_rights_exit_hold.py) đã merge 22/10: auto-exit TỰ giữ lệnh thoát LAG tới GDKHQ.
            lines.append("  Bot TỰ giữ lệnh thoát T+25 của mã LAG tới GDKHQ (nếu là mã LAG; mã non-LAG không bị giữ); "
                         "quyền mua CHƯA có ngày thì bot vẫn giữ và đòi anh quyết hold/sell "
                         "(lag_rights_exit_hold.py --record). Việc giữ này KHÔNG cấm thoái: user vẫn có thể "
                         "thoái bằng plan nếu muốn. User TỰ thực hiện quyền "
                         "đầy đủ (bot không mua/chuyển nhượng quyền). Sau khi nộp tiền NAV có thể chặn rc=5/6 — "
                         "xử lý theo tiền lệ MBB 08-28 (REPORT lag_rights_audit_20261022).")
        elif sev == "WARN":
            lines.append("  CHỈ CẢNH BÁO: bot KHÔNG tự bán/không sửa plan — user quyết giữ hay thoái (bằng plan).")
        else:
            lines.append("  Giá sẽ điều chỉnh tại GDKHQ qua luồng corp-action sẵn có; không cần hành động.")
        out.append({"keys": [k for _, k in todo], "stage": stage, "text": "\n".join(lines)})
    if stale_rows:
        items = "; ".join(f"{r['ticker']} {METHOD_VI.get(r.get('issue_method_code'), r.get('issue_method_code'))} "
                          f"(công bố {(r.get('public_date') or '?')[:10]}, tỉ lệ "
                          f"{float(r.get('exercise_ratio') or 0):.2%})" for r in stale_rows)
        out.append({"keys": [f"{r['id']}|stale" for r in stale_rows], "stage": "STALE",
                    "text": f"🔸 Tăng vốn nghi BỎ DỞ — dòng `P` không ngày, công bố > {STALE_P_DAYS} ngày, "
                            f"KHÔNG báo như sự kiện sống; kiểm VSDC/công ty nếu cần: {items}"})
    return out


def fetch_rights(tickers):
    """CHỈ dòng Rights — HỢP ĐỒNG với lag_rights_exit_hold.py / daily_nav_snapshot.py / rights_subscription.py
    (họ coi mọi dòng trả về là quyền mua). KHÔNG mở rộng hàm này; cảnh báo tăng vốn dùng fetch_issuance."""
    return [r for r in fetch_issuance(tickers) if r.get("issue_method_code") == "Rights"]


def fetch_issuance(tickers):
    """Mọi dòng phát hành CP (event_code ISS, mọi phương thức) của các mã — nguồn của cảnh báo tăng vốn."""
    from corp_action_lib import TABLE, bq
    tk = ",".join(f'"{t}"' for t in sorted(tickers))
    return bq(f"""
        SELECT c.id, c.ticker, c.issue_method_code, c.issue_status_code, c.event_status,
               CAST(c.exright_date AS STRING) exright_date, CAST(c.record_date AS STRING) record_date,
               CAST(c.public_date AS STRING) public_date, c.exercise_ratio, c.value_per_share,
               c.total_value, c.issue_volumn
        FROM `{TABLE}` AS c
        WHERE c.ticker IN ({tk}) AND c.event_code = "ISS"
        ORDER BY c.ticker, c.public_date""")


def fetch_oshares(tickers):
    """{ticker: OShares quý mới nhất} từ tav2_bq.ticker_financial (chỉ để tính % khi exercise_ratio = 0)."""
    from corp_action_lib import TABLE, bq
    tk = ",".join(f'"{t}"' for t in sorted(tickers))
    fin = TABLE.rsplit(".", 1)[0] + ".ticker_financial"
    rows = bq(f"""
        SELECT f.ticker, ARRAY_AGG(f.OShares ORDER BY f.time DESC LIMIT 1)[OFFSET(0)] oshares
        FROM `{fin}` AS f WHERE f.ticker IN ({tk}) AND f.OShares > 0 GROUP BY f.ticker""")
    return {r["ticker"]: float(r["oshares"]) for r in rows}


def read_positions(nav_glob=ACTIVE_NAV_GLOB, prices=None):
    """-> ({account: {ticker: qty}}, {account: {file, computed_at}}); `prices` (dict) nếu truyền ⇒ điền thị giá."""
    out, meta = {}, {}
    for path in sorted(glob.glob(nav_glob)):
        with open(path) as fh:
            d = json.load(fh)
        lb = d.get("account") or os.path.basename(path)
        out[lb] = {p["ticker"]: int(p.get("qty") or 0) for p in d.get("positions") or [] if p.get("ticker")}
        meta[lb] = {"file": os.path.basename(path), "computed_at": d.get("computed_at")}
        if prices is not None:
            prices.update({p["ticker"]: float(p["price"]) for p in d.get("positions") or []
                           if p.get("ticker") and (p.get("price") or 0) > 0})
    return out, meta


def fetch_cycles(accounts, snapshot=None):
    """-> ({account: {ticker: [{'book','entry','qty'} | {'book','unknown'}]}}, None) hoặc (None, lỗi).
    Sổ lô LAG/BAL từng account qua `portfolio_status.book_lot_snapshot`. Lỗi KẾT CẤU (ok=False/raise) ⇒ (None, lỗi thật)
    ⇒ caller FAIL-OPEN (không lọc). Mã bị sổ lô chặn (unverified/mồ côi) ⇒ lô 'unknown' ⇒ vẫn cảnh báo, nói rõ lý do."""
    if snapshot is None:
        from portfolio_status import book_lot_snapshot as snapshot
    out = {}
    for acc in sorted(accounts):
        for book, _n in CYCLE_BOOKS:
            try:
                lots, ok, reason, blocked = snapshot(acc, book)
            except Exception as e:                 # §29: lỗi thật, không đoán
                return None, f"{acc}/{book}: {type(e).__name__}: {str(e)[:160]}"
            if not ok:
                return None, f"{acc}/{book}: {str(reason)[:200]}"
            for tk, d in lots.items():
                for l in d.get("lots") or []:
                    out.setdefault(acc, {}).setdefault(tk, []).append(
                        {"book": book, "entry": l["entry_date"], "qty": int(l["qty"])})
            for tk, why in (blocked or {}).items():
                out.setdefault(acc, {}).setdefault(tk, []).append({"book": book, "unknown": str(why)[:160]})
    return out, None


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
    prices = {}
    pos, meta = read_positions(a.nav_glob, prices)
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
    rows = fetch_issuance(tickers)
    try:
        oshares = fetch_oshares(tickers)
    except Exception as e:                    # chỉ ảnh hưởng % pha loãng khi exercise_ratio = 0 — tin ghi "CHƯA RÕ"
        oshares = {}
        print(f"⚠️ không đọc được OShares (ticker_financial): {e!r} — % pha loãng chỉ từ exercise_ratio")
    sent = _load_sent(a.state) if a.send else set()
    cycles, cyc_err = fetch_cycles(sorted(pos))
    if cyc_err:
        print(f"⚠️ KHÔNG lọc được theo chu kỳ LAG/BAL (fail-open: cảnh báo mọi mã đang giữ): {cyc_err}")
    diag = []
    alerts = build_alerts(a.asof, pos, rows, sent, is_holiday, meta, notes, prices, oshares, cycles, diag, cyc_err)
    for line in diag:
        print(f"  [bỏ qua] {line}")
    if not alerts:
        print(f"[{a.asof}] không có sự kiện tăng vốn nào cần báo cho {len(tickers)} mã đang giữ")
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
