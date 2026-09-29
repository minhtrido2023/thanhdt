#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""portfolio_status.py --account SpaceX --date YYYY-MM-DD

In ra (stdout) một khối markdown "TÌNH TRẠNG DANH MỤC" cho EOD trading report — góc nhìn
portfolio-manager: cơ cấu theo sleeve (BAL/PARK/LAG/CAPIT/DISCRETIONARY/Trứng vàng/Cash),
lãi/lỗ chưa hiện thực từng sleeve, và corp-action sắp tới trên mã đang giữ.

Nguồn dữ liệu (đọc, KHÔNG ghi gì):
  - `data/golive_v23_status.json` — regime DT5G, park roster size, CAPIT basket.
  - `data/execution_logs/dnse_raw_{date}.jsonl` — vị thế + costPrice broker-native (kind=positions,
    lọc accountNo — §12).
  - `data/execution_logs/nav_history_{account}.csv` — NAV/mtm_stock/cash/margin_debt/egg_assets,
    qua `nav_period_returns.load_nav_history()` (không tự tính lại).
  - `data/execution_logs/exec_{account}_*_journal.csv` cột `book` (BAL/PARK/LAG/DISCRETIONARY_SPECIAL)
    trên dòng FILL — nguồn sleeve-attribution CHÍNH, vì đây là nhãn engine tự gắn lúc đặt lệnh.
  - `data/custom30v_8l_publish_CAND_*.csv` — fallback sleeve PARK cho mã KHÔNG có journal (ví dụ
    journal cũ đã bị dọn/rotate) — dùng batch `rebal_date` MỚI NHẤT.
  - `nav_exdate_forecast.build_report()` — corp-action ≤7 phiên tới trên mã đang giữ.

Sleeve còn lại KHÔNG xác định được (không có journal FILL, không trong PARK roster hiện hành)
mặc định về BAL (momentum/yieldcombo — sleeve nền của V2.4) — không suy diễn LAG/CAPIT/DISCRETIONARY
nếu không có bằng chứng trực tiếp.

⚠️ Lãi/lỗ per-position dùng `costPrice` DNSE báo cáo trực tiếp (bình quân gia quyền broker-native,
KHÔNG tự tính lại từ fill log) — đây là con số DASHBOARD nội bộ cho PM theo dõi hướng, KHÔNG đi qua
`dividend_adjusted_return.py` (§21) nên KHÔNG được dùng làm số công bố chính thức investor-facing.
"""
import argparse
import csv
import datetime as _dt
import glob
import json
import os
import sys
from collections import Counter, defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import wc_paths  # noqa: E402

WC_ROOT = wc_paths.find_wc_root(__file__)
EXEC_DIR = os.path.join(WC_ROOT, "data", "execution_logs")

ACCOUNT_NO_BY_LABEL = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}

SLEEVE_ORDER = ["BAL", "PARK", "LAG", "CAPIT", "DISCRETIONARY_SPECIAL"]
SLEEVE_LABEL = {
    "BAL": "BAL",
    "PARK": "PARK custom30V",
    "LAG": "LAG",
    "CAPIT": "CAPIT",
    "DISCRETIONARY_SPECIAL": "Discretionary",
}
SLEEVE_NOTE = {
    "BAL": "Momentum V11 + yieldcombo",
    "PARK": None,  # gắn động (rebal date) ở build_output()
    "LAG": "PEAD/earnings drift",
    "CAPIT": "Bear-washout overflow",
    "DISCRETIONARY_SPECIAL": "Fear-buy/special situation",
}

RECS_DIR = os.path.join(WC_ROOT, "deploy_golive_dt5g_v4", "out")

# Cửa sổ thoát LAG (PEAD/earnings-drift): T+14 tới T+20 phiên sau ngày entry.
LAG_EXIT_MIN_SESSIONS = 14
LAG_EXIT_MAX_SESSIONS = 20

# Ngưỡng stop-loss xử lý theo sleeve (không có nghĩa là "ngưỡng cứng đã lập trình ở nơi khác" —
# đây là số kỷ luật V2.4 tham chiếu, dùng để cảnh báo GẦN ngưỡng). PARK cố tình KHÔNG có trong
# bảng này: rebalance định kỳ là cơ chế rủi ro của PARK, không phải stop-loss theo drawdown.
STOP_LOSS_PCT_BY_SLEEVE = {
    "BAL": 20.0,
    "LAG": 15.0,
    "CAPIT": 20.0,
    "DISCRETIONARY_SPECIAL": 20.0,
}
RISK_WARN_DISPLAY_FLOOR_PCT = 15.0  # bắt đầu in cảnh báo từ mức lỗ này
RISK_WARN_RED_ZONE_PCT = 18.0  # đưa vào "Cờ theo dõi" từ mức lỗ này


def _read_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def account_no_for(account):
    """account_no broker cho `account` — tra `trading_bot.config.load_accounts()` trước
    (nguồn thật), fallback map tĩnh nếu config không load được (đọc-chỉ-đọc, không phải
    con đường ghi tiền nên fallback tĩnh chấp nhận được cho dashboard này)."""
    try:
        sys.path.insert(0, WC_ROOT)
        from trading_bot.config import load_accounts, load_config
        match = next((p for p in load_accounts(load_config()) if p["label"] == account), None)
        if match and match.get("account_id"):
            return match["account_id"]
    except Exception:
        pass
    return ACCOUNT_NO_BY_LABEL.get(account)


def broker_positions_with_cost(account_no, asof):
    """{ticker: {qty, marketPrice, avg_cost}} từ bản ghi `positions` CUỐI CÙNG trong
    dnse_raw_{asof}.jsonl — gộp nhiều loan-package cùng mã (qty cộng dồn, costPrice bình
    quân gia quyền theo qty, marketPrice giữ giá trị của lô cuối cùng khác-None gặp trong
    file, cùng quy ước `verify_account_snapshot.broker_positions_from_raw`)."""
    path = os.path.join(EXEC_DIR, f"dnse_raw_{asof}.jsonl")
    if not os.path.exists(path):
        return None
    latest = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if rec.get("kind") != "positions":
                continue
            if rec.get("account_no") != account_no:  # §12: file dùng chung nhiều account
                continue
            latest = rec.get("payload", {}).get("positions") or []
    if latest is None:
        return None
    out = {}
    for p in latest:
        qty = float(p.get("openQuantity") or 0)
        if qty <= 0:
            continue
        tk = p.get("symbol")
        row = out.setdefault(tk, {"qty": 0.0, "marketPrice": None, "_cost_wsum": 0.0})
        row["qty"] += qty
        cp = p.get("costPrice")
        if cp is not None:
            row["_cost_wsum"] += qty * float(cp)
        mp = p.get("marketPrice")
        if mp is not None:
            row["marketPrice"] = mp
    for tk, row in out.items():
        row["avg_cost"] = row["_cost_wsum"] / row["qty"] if row["qty"] else None
        del row["_cost_wsum"]
    return out


def sleeve_map_from_journal(account):
    """{ticker: book} — nhãn book PHỔ BIẾN NHẤT trên các dòng FILL trong TOÀN BỘ journal
    `exec_{account}_*_journal.csv` còn trên đĩa. Rỗng nếu không đọc được file nào (không phải
    lỗi — journal cũ có thể đã bị dọn/rotate, caller fallback qua PARK roster)."""
    votes = defaultdict(Counter)
    for fn in sorted(glob.glob(os.path.join(EXEC_DIR, f"exec_{account}_*_journal.csv"))):
        try:
            with open(fn, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    if row.get("event") != "FILL":
                        continue
                    tk, bk = row.get("ticker"), row.get("book")
                    if tk and bk:
                        votes[tk][bk] += 1
        except (OSError, csv.Error):
            continue
    return {tk: c.most_common(1)[0][0] for tk, c in votes.items()}


def current_park_basket():
    """(set(ticker), rebal_date str|None) — batch rebal MỚI NHẤT trong
    `custom30v_8l_publish_CAND_*.csv` (glob, giữ file mtime mới nhất nếu có nhiều bản)."""
    cands = sorted(glob.glob(os.path.join(WC_ROOT, "data", "custom30v_8l_publish_CAND_*.csv")),
                    key=os.path.getmtime, reverse=True)
    if not cands:
        return set(), None
    path = cands[0]
    rows_by_rebal = defaultdict(list)
    latest_rebal = None
    try:
        with open(path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rd = row.get("rebal_date")
                if not rd:
                    continue
                rows_by_rebal[rd].append(row["ticker"])
                if latest_rebal is None or rd > latest_rebal:
                    latest_rebal = rd
    except (OSError, csv.Error):
        return set(), None
    if latest_rebal is None:
        return set(), None
    return set(rows_by_rebal[latest_rebal]), latest_rebal


def _next_trading_day_fn():
    """`trading_bot.vn_market.next_trading_day` hoặc None nếu import lỗi (fail-soft — caller
    bỏ qua phần tính phiên thay vì crash cả report)."""
    try:
        sys.path.insert(0, WC_ROOT)
        from trading_bot.vn_market import next_trading_day
        return next_trading_day
    except Exception:
        return None


def count_trading_days(start, asof):
    """Số phiên giao dịch TỪ SAU `start` ĐẾN `asof` (cả hai `datetime.date`), dùng
    `next_trading_day` (đã trừ T7/CN + `is_holiday` — §16 RULE 2, không tự đếm lịch tay).
    None nếu không import được `trading_bot.vn_market`."""
    next_trading_day = _next_trading_day_fn()
    if next_trading_day is None:
        return None
    if asof <= start:
        return 0
    d, n = start, 0
    while d < asof:
        d = next_trading_day(d)
        n += 1
    return n


def _first_fill_dates(account, book_label):
    """{ticker: 'YYYY-MM-DD'} ngày FILL mua ĐẦU TIÊN gắn nhãn book=`book_label`."""
    first = {}
    for fn in sorted(glob.glob(os.path.join(EXEC_DIR, f"exec_{account}_*_journal.csv"))):
        try:
            with open(fn, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    if row.get("event") != "FILL" or row.get("book") != book_label:
                        continue
                    if (row.get("side") or "").lower() != "buy":
                        continue
                    tk, ts = row.get("ticker"), row.get("ts")
                    if not tk or not ts:
                        continue
                    d = ts[:10]
                    if tk not in first or d < first[tk]:
                        first[tk] = d
        except (OSError, csv.Error):
            continue
    return first


def lag_entry_dates(account):
    """{ticker: 'YYYY-MM-DD'} ngày FILL mua ĐẦU TIÊN gắn nhãn book=LAG."""
    return _first_fill_dates(account, "LAG")


def disc_entry_dates(account):
    """{ticker: 'YYYY-MM-DD'} ngày FILL mua ĐẦU TIÊN gắn nhãn book=DISCRETIONARY_SPECIAL."""
    return _first_fill_dates(account, "DISCRETIONARY_SPECIAL")


def lag_exit_hint(ticker, entry_dates, asof_date):
    """Text cửa sổ thoát LAG cho `ticker`, hoặc None nếu không có entry date / không tính
    được phiên (fail-soft)."""
    entry_str = entry_dates.get(ticker)
    if not entry_str:
        return None
    try:
        entry = _dt.date.fromisoformat(entry_str)
        asof = _dt.date.fromisoformat(asof_date)
    except ValueError:
        return None
    sessions = count_trading_days(entry, asof)
    if sessions is None:
        return None
    if sessions < LAG_EXIT_MIN_SESSIONS:
        return (f"vào {entry_str}, còn {LAG_EXIT_MIN_SESSIONS - sessions} phiên tới cửa "
                f"T+{LAG_EXIT_MIN_SESSIONS}")
    if sessions <= LAG_EXIT_MAX_SESSIONS:
        remaining = LAG_EXIT_MAX_SESSIONS - sessions
        return (f"còn ~{remaining} phiên (cửa T+{LAG_EXIT_MIN_SESSIONS}/T+{LAG_EXIT_MAX_SESSIONS}, "
                f"vào {entry_str})")
    return f"ĐÃ QUA cửa T+{LAG_EXIT_MAX_SESSIONS} ({sessions} phiên từ {entry_str}) — cân nhắc thoát"


def latest_recs_csv():
    """(date_str, path) file `golive_v23_recommendations_YYYY-MM-DD.csv` MỚI NHẤT theo TÊN
    FILE (không phải mtime — tên file mang ngày signal thật, mtime có thể trễ nếu regenerate).
    (None, None) nếu thư mục rỗng/không tồn tại."""
    dated = []
    for p in glob.glob(os.path.join(RECS_DIR, "golive_v23_recommendations_*.csv")):
        base = os.path.basename(p)
        stem = base[len("golive_v23_recommendations_"):-len(".csv")]
        if len(stem) == 10:
            dated.append((stem, p))
    if not dated:
        return None, None
    dated.sort()
    return dated[-1]


def load_recs(path):
    """book -> {ticker: status} từ 1 file recommendations (cột thật: book/ticker/status —
    KHÔNG có cột 'signal_FULL_SIZE'; status BAL = 'FULL'/'HALF_SIZE')."""
    out = defaultdict(dict)
    try:
        with open(path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                bk, tk = row.get("book"), row.get("ticker")
                if bk and tk:
                    out[bk][tk] = row.get("status")
    except (OSError, csv.Error):
        return {}
    return out


def bal_exit_hint(ticker, bal_recs):
    """Ghi chú tín hiệu BAL cho `ticker` từ file recommendations MỚI NHẤT.
    ⚠️ File này là danh sách CANDIDATE MỚI mỗi ngày (top momentum re-rank, không phải "roster
    đang mở"), nên KHÔNG suy ra "tín hiệu đã kết thúc" chỉ vì vắng mặt 1 ngày — chỉ báo sự kiện
    quan sát được (§29: không đoán nguyên nhân chưa có bằng chứng)."""
    if not bal_recs:
        return None
    st = bal_recs.get(ticker)
    if st:
        return f"tín hiệu hôm nay: {st}"
    return "không có tín hiệu mới hôm nay"


def park_next_rebal_estimate(asof_date_str):
    """Ước tính ngày rebal PARK kế tiếp: đầu tuần (né T7/CN) của tháng đầu quý VN (3/6/9/12)
    kế tiếp SAU `asof_date_str`. Chỉ tham khảo, KHÔNG phải lịch chính thức."""
    try:
        asof = _dt.date.fromisoformat(asof_date_str)
    except ValueError:
        return None
    quarters = (3, 6, 9, 12)
    year = asof.year
    next_q_month = next((q for q in quarters if q > asof.month), None)
    if next_q_month is None:
        next_q_month, year = 3, year + 1
    d = _dt.date(year, next_q_month, 1)
    while d.weekday() >= 5:
        d += _dt.timedelta(days=1)
    return d.isoformat(), next_q_month // 3


def classify_sleeve(ticker, journal_sleeve, park_tickers, capit_tickers):
    if ticker in journal_sleeve:
        bk = journal_sleeve[ticker]
        if bk in SLEEVE_LABEL:
            return bk
        if bk == "CORP_ACTION":  # nhãn kỹ thuật của lệnh phái sinh từ corp-action, không phải sleeve riêng
            pass
        else:
            return "BAL"
    if ticker in capit_tickers:
        return "CAPIT"
    if ticker in park_tickers:
        return "PARK"
    return "BAL"


def risk_warning(sleeve, pnl_pct):
    """(emoji, text)|None — cảnh báo gần ngưỡng xử lý cho 1 position, hoặc None nếu sleeve
    không có ngưỡng (PARK) / lỗ chưa tới RISK_WARN_DISPLAY_FLOOR_PCT."""
    threshold = STOP_LOSS_PCT_BY_SLEEVE.get(sleeve)
    if threshold is None or pnl_pct is None or pnl_pct > -RISK_WARN_DISPLAY_FLOOR_PCT:
        return None
    dd = abs(pnl_pct)
    remaining = max(threshold - dd, 0.0)
    emoji = "🔴" if dd >= RISK_WARN_RED_ZONE_PCT else "⚠️"
    return emoji, f"{emoji} còn {remaining:.1f}pp đến ngưỡng xử lý (−{threshold:.0f}%)"


def load_nav_row(account, date):
    """Dòng nav_history {account} đúng `date` (hoặc gần nhất TRƯỚC nếu hôm nay chưa có),
    và dòng NGAY TRƯỚC nó — đọc trực tiếp `nav_history_{account}.csv` vì cần cột
    `cash`/`egg_assets` mà `nav_period_returns.load_nav_history()` không expose (nó chỉ
    trả (date, nav) cho tính TWR)."""
    path = os.path.join(EXEC_DIR, f"nav_history_{account}.csv")
    if not os.path.exists(path):
        return None, None
    rows = []
    with open(path, encoding="utf-8") as f:
        for rec in csv.DictReader(f):
            if not rec.get("date") or not rec.get("nav"):
                continue
            row = dict(rec)
            row["date"] = _dt.date.fromisoformat(rec["date"])
            row["nav"] = float(rec["nav"])
            for k in ("cash", "egg_assets"):
                row[k] = float(rec[k]) if rec.get(k) not in (None, "") else 0.0
            rows.append(row)
    rows.sort(key=lambda r: r["date"])
    if not rows:
        return None, None
    d = _dt.date.fromisoformat(date)
    on_or_before = [r for r in rows if r["date"] <= d]
    if not on_or_before:
        return None, None
    today_row = on_or_before[-1]
    prior_row = on_or_before[-2] if len(on_or_before) >= 2 else None
    return today_row, prior_row


def build_output(account, date):
    lines = []
    status = _read_json(os.path.join(WC_ROOT, "data", "golive_v23_status.json"), {}) or {}
    state_name = status.get("state_name", "?")

    today_row, prior_row = load_nav_row(account, date)
    if today_row is None:
        return None  # không có NAV — caller in cảnh báo, không crash

    nav = today_row["nav"]
    day_chg_pct = None
    if prior_row and prior_row["nav"]:
        day_chg_pct = (nav / prior_row["nav"] - 1) * 100

    inception_pct = None
    try:
        from nav_period_returns import load_inception, load_nav_history, compute_period_returns
        result = compute_period_returns(account, _dt.date.fromisoformat(date),
                                         load_nav_history(account), load_inception(account))
        inception_pct = result.get("inception", {}).get("return_pct")
    except Exception:
        pass

    account_no = account_no_for(account)
    positions = broker_positions_with_cost(account_no, date) if account_no else None
    if positions is None:
        positions = {}

    journal_sleeve = sleeve_map_from_journal(account)
    park_tickers, park_rebal_date = current_park_basket()
    capit_tickers = set(status.get("capit_episode_basket") or [])

    sleeves = defaultdict(list)  # sleeve -> [(ticker, qty, mkt_value, pnl_pct)]
    for tk, p in positions.items():
        mkt_value = (p["qty"] * p["marketPrice"]) if p.get("marketPrice") else None
        pnl_pct = None
        if p.get("avg_cost") and p.get("marketPrice"):
            pnl_pct = (p["marketPrice"] - p["avg_cost"]) / p["avg_cost"] * 100
        sleeve = classify_sleeve(tk, journal_sleeve, park_tickers, capit_tickers)
        sleeves[sleeve].append((tk, p["qty"], mkt_value, pnl_pct))

    cash = today_row.get("cash") or 0
    egg = today_row.get("egg_assets") or 0
    held = set(positions.keys())

    recs_date, recs_path = latest_recs_csv()
    recs_by_book = load_recs(recs_path) if recs_path else {}
    bal_recs = recs_by_book.get("BAL", {})
    lag_entries = lag_entry_dates(account)
    disc_entries = disc_entry_dates(account)

    dt_gate_line = value_radar_line = None
    try:
        sys.path.insert(0, WC_ROOT)
        from dna_report import build_dt_gate_line, build_value_radar_line
        dt_gate_line = build_dt_gate_line(html=False)
        value_radar_line = build_value_radar_line(html=False)
    except Exception:
        pass

    # ---------------- header ----------------
    hdr_day = f"{day_chg_pct:+.2f}%" if day_chg_pct is not None else "?"
    hdr_incep = f"{inception_pct:+.2f}%" if inception_pct is not None else "?"
    lines.append("─────────────────────────────────────────────────")
    lines.append(f"📋 **TÌNH TRẠNG DANH MỤC — {account} ({date})**")
    lines.append(f"Chiến lược: **V2.4** | Regime: **{state_name}** (DT5G) | "
                 f"Park target: **{status.get('etf_park_frac', 0) * 100:.0f}%** idle cash")
    lines.append(f"NAV: **{nav / 1e6:,.1f}M** | Hôm nay: **{hdr_day}** | "
                 f"Từ khi bắt đầu hoạt động: **{hdr_incep}**")
    if dt_gate_line:
        lines.append(dt_gate_line)
    if value_radar_line:
        lines.append(value_radar_line.splitlines()[0])  # chỉ dòng chính, bỏ dòng chú thích phụ
    lines.append("─────────────────────────────────────────────────")
    lines.append("")

    # ---------------- sleeve table ----------------
    lines.append("**Cơ cấu danh mục**")
    lines.append("")
    lines.append("| Sleeve | Giá trị | % NAV | Lãi/Lỗ CK | Ghi chú |")
    lines.append("|--------|--------:|------:|----------:|---------|")
    for sleeve in SLEEVE_ORDER:
        rows = sleeves.get(sleeve) or []
        if not rows:
            continue
        tot_value = sum(v for _, _, v, _ in rows if v is not None)
        num = 0.0
        den = 0.0
        for tk, qty, v, pp in rows:
            if v is None or pp is None:
                continue
            cost_v = v / (1 + pp / 100)
            num += v - cost_v
            den += cost_v
        pnl_txt = f"{(num / den * 100):+.1f}%" if den else "—"
        pct_nav = f"{tot_value / nav * 100:.1f}%" if nav else "—"
        note = SLEEVE_NOTE.get(sleeve) or ""
        if sleeve == "PARK":
            if park_rebal_date:
                next_est = park_next_rebal_estimate(date)
                note = f"Rebal gần nhất: {park_rebal_date}"
                if next_est:
                    next_date, q = next_est
                    note += f" | kế tiếp: ~{next_date} (ước tính Q{q})"
            else:
                note = "custom30V"
        lines.append(f"| {SLEEVE_LABEL[sleeve]} ({len(rows)} mã) | {tot_value / 1e6:,.1f}M | "
                     f"{pct_nav} | {pnl_txt} | {note} |")
    egg_pct = f"{egg / nav * 100:.1f}%" if nav else "—"
    lines.append(f"| Trứng vàng | {egg / 1e6:,.1f}M | {egg_pct} | — | DNSE bond-like (off-book) |")
    cash_pct = f"{cash / nav * 100:.1f}%" if nav else "—"
    lines.append(f"| Cash | {cash / 1e6:,.1f}M | {cash_pct} | 0% | Idle |")
    lines.append("")

    # ---------------- per-sleeve detail ----------------
    red_zone = []  # [(sleeve, ticker, pnl_pct, remaining_pp)]
    for sleeve in SLEEVE_ORDER:
        rows = sleeves.get(sleeve) or []
        if not rows:
            continue
        rows_sorted = sorted(rows, key=lambda r: -(r[2] or 0))
        lines.append(f"**Chi tiết {SLEEVE_LABEL[sleeve]} ({len(rows)} mã)**")
        bits = []
        for tk, qty, v, pp in rows_sorted:
            v_txt = f"{v / 1e6:,.1f}M" if v is not None else "?"
            pp_txt = f", {pp:+.1f}%" if pp is not None else ""
            extra = []
            if sleeve == "LAG":
                h = lag_exit_hint(tk, lag_entries, date)
                if h:
                    extra.append(h)
            elif sleeve == "BAL":
                h = bal_exit_hint(tk, bal_recs)
                if h:
                    extra.append(h)
            elif sleeve == "CAPIT":
                extra.append("không fixed exit, thoát theo tín hiệu đảo")
            elif sleeve == "DISCRETIONARY_SPECIAL":
                entry_str = disc_entries.get(tk)
                if entry_str:
                    sessions = count_trading_days(_dt.date.fromisoformat(entry_str),
                                                   _dt.date.fromisoformat(date))
                    sess_txt = f"{sessions} phiên từ {entry_str}" if sessions is not None else f"từ {entry_str}"
                else:
                    sess_txt = "ngày vào không rõ"
                extra.append(f"⚠️ {sess_txt} — chờ ý kiến PM về exit")
            rw = risk_warning(sleeve, pp)
            if rw:
                emoji, rw_txt = rw
                extra.append(rw_txt)
                if emoji == "🔴":
                    threshold = STOP_LOSS_PCT_BY_SLEEVE[sleeve]
                    red_zone.append((sleeve, tk, pp, max(threshold - abs(pp), 0.0)))
            bit = f"{tk} {v_txt}{pp_txt}"
            if extra:
                bit += " — " + "; ".join(extra)
            bits.append(bit)
        lines.append("  " + " · ".join(bits))
        lines.append("")
        if sleeve == "BAL" and bal_recs:
            candidates = [tk for tk, st in sorted(bal_recs.items())
                          if st == "FULL" and tk not in held][:5]
            if candidates:
                lines.append(f"  Ứng viên BAL chờ vào: {', '.join(candidates)} "
                             f"(xem recommendations {recs_date})")
                lines.append("")

    # ---------------- corp action ----------------
    lines.append("**Corp Action — 7 ngày tới** (mã đang giữ)")
    events = []
    try:
        sys.path.insert(0, _HERE)
        from nav_exdate_forecast import build_report, classify
        _lines, _snap, events = build_report(asof=date, days_ahead_max=7)
    except Exception:
        events = []
    mine = [e for e in events if e.get("ticker") in held]
    if mine:
        lines.append("| Mã | Sự kiện | Ngày | Tác động dự kiến |")
        lines.append("|----|---------|------|-------------------|")
        for e in sorted(mine, key=lambda x: x["date"]):
            kind = classify(e)
            if kind == "CASH_DIV":
                vps = e.get("value_per_share")
                impact = f"{vps:,.0f}đ/cp cổ tức tiền mặt" if vps is not None else "cổ tức tiền mặt (chưa rõ mức)"
            elif kind == "SHARE_EVENT":
                ratio = e.get("exercise_ratio")
                impact = f"{e.get('event_code')}, tỉ lệ {float(ratio) * 100:.2f}%" if ratio else e.get("event_code", "?")
            else:
                impact = e.get("title") or e.get("event_code", "—")
            lines.append(f"| {e['ticker']} | {e.get('event_code', '?')} | {e['date']} | {impact} |")
    else:
        lines.append("Không có corp action trong 7 ngày tới trên mã đang giữ.")
    lines.append("")

    # ---------------- flags ----------------
    flags = []
    if park_rebal_date:
        park_next = park_next_rebal_estimate(date)
        next_txt = f", kế tiếp ~{park_next[0]} (ước tính)" if park_next else ", rebal kế tiếp chưa xác định"
        flags.append(f"PARK: rổ hiện hành chốt {park_rebal_date} (chu kỳ ~quý{next_txt}).")
    if sleeves.get("LAG"):
        flags.append(f"LAG: đang giữ {len(sleeves['LAG'])} mã PEAD/earnings-drift, theo dõi cửa sổ thoát.")
    if sleeves.get("DISCRETIONARY_SPECIAL"):
        disc_bits = []
        for tk, *_ in sleeves["DISCRETIONARY_SPECIAL"]:
            entry_str = disc_entries.get(tk)
            if entry_str:
                sessions = count_trading_days(_dt.date.fromisoformat(entry_str),
                                               _dt.date.fromisoformat(date))
                disc_bits.append(f"{tk} ({sessions}p)" if sessions is not None else f"{tk} (từ {entry_str})")
            else:
                disc_bits.append(tk)
        flags.append(f"⚠️ Discretionary: {', '.join(sorted(disc_bits))} — chờ ý kiến PM về exit")
    if sleeves.get("CAPIT"):
        flags.append(f"CAPIT: {len(sleeves['CAPIT'])} mã đang trong episode overflow. "
                     "Không có fixed exit — thoát theo tín hiệu đảo.")
    n_lag_upcoming = status.get("n_lag_upcoming") or 0
    if n_lag_upcoming:
        flags.append(f"LAG: {n_lag_upcoming} candidate đang trong cửa sổ upcoming (chưa vào lệnh).")
    for sleeve, tk, pp, remaining in red_zone:
        flags.append(f"🔴 {tk} {pp:+.1f}% ({SLEEVE_LABEL[sleeve]}): còn {remaining:.1f}pp → "
                     "ngưỡng, cân nhắc xử lý sớm")
    if flags:
        lines.append("**Cờ theo dõi**")
        for f in flags:
            lines.append(f"- {f}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", required=True, choices=["SpaceX", "ZaloPay"])
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--selfcheck", action="store_true")
    args = ap.parse_args()

    if args.selfcheck:
        import portfolio_status_selfcheck
        return portfolio_status_selfcheck.run()

    out = build_output(args.account, args.date)
    if out is None:
        print(f"⚠️ portfolio_status: không có NAV cho {args.account} {args.date}", file=sys.stderr)
        return 1
    sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
