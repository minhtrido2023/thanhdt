"""report_v2.data_sources — nạp số cho báo cáo tài khoản v2. CHỈ đọc nguồn/pipeline đã có.

| Số                                         | Nguồn (gọi thẳng hàm của pipeline, không chép công thức)          |
|--------------------------------------------|-------------------------------------------------------------------|
| NAV + cấu phần (cổ phiếu/tiền/Trứng/nợ)    | data/execution_logs/nav_history_<acct>.csv (daily_nav_snapshot.py) |
| Tỷ suất ngày/tuần/MTD/từ đầu + VN-Index    | nav_period_returns.compute_period_returns (§31) + _benchmark_fn   |
| Tỷ suất QTD/YTD/từng tháng                 | nav_period_returns._period/_period_result trên CÙNG sổ build_ledger |
| Bảng "Hiệu suất lũy kế" (cổng giao)        | period_table_32.run_cli + render (y hệt CLI)                      |
| Tỷ suất từng vị thế (đã cộng cổ tức)       | report_return_gate.position_returns (§21 — đúng hàm cổng dùng)    |
| KL vị thế đầu/cuối kỳ                      | portfolio_status.broker_positions_with_cost (dnse_raw positions)  |
| Lệnh khớp trong kỳ                         | dnse_raw_<ngày>.jsonl kind=order_history (bản ghi cuối ngày, có lệnh tay) |
| Phí/thuế                                   | dnse_khoplenh_broker_confirm_<dd-mm-yyyy>.csv; thiếu ⇒ biểu phí dnse_fee_rates (ghi rõ "ước tính") |
| Giá đóng cửa đầu/cuối kỳ cho đóng góp      | verify_account_snapshot.bq_close_prices (cùng hàm NAV dùng khi không có giá DNSE) |
| VN-Index đóng cửa / có cổ tức              | data/benchmark/vnindex_tr_daily.csv (vnindex_total_return.py)     |
| Khối thị trường (dữ kiện)                  | livermore_report_block.build_facts (số do script tính) + khối PASS nếu có |
| Trạng thái thị trường / định giá           | dna_report.build_dt_gate_line / build_value_radar_line (§6b)      |

§12: mọi đọc dnse_raw lọc account_no trước khi xử lý. §16: không đọc giờ hệ thống ở đây.
"""
import csv
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.dirname(HERE)
MIKE = os.path.dirname(BIN)
WC = os.path.dirname(MIKE) if os.path.basename(os.path.dirname(MIKE)) == "WorkingClaude" else "/home/trido/thanhdt/WorkingClaude"
EL = os.environ.get("REPORT_V2_EXEC_DIR", f"{WC}/data/execution_logs")
VNI_CSV = f"{WC}/data/benchmark/vnindex_tr_daily.csv"
LIVERMORE_DIR = f"{MIKE}/data/livermore"
for p in (BIN, WC):
    if p not in sys.path:
        sys.path.insert(0, p)

import nav_period_returns as npr  # noqa: E402

ACCOUNTS = ("SpaceX", "ZaloPay")


def D(s):
    return dt.date.fromisoformat(s) if isinstance(s, str) else s


class Unavailable(RuntimeError):
    """Nguồn không đọc được — mục tương ứng in "không có" kèm lý do thật, KHÔNG tự tính thay."""


# ───────────────────────── NAV / tỷ suất (§31) ─────────────────────────
def nav_rows(acct):
    with open(f"{EL}/nav_history_{acct}.csv", encoding="utf-8") as fh:
        return {r["date"]: r for r in csv.DictReader(fh)}


def nav_row_on_or_before(acct, d):
    rows = nav_rows(acct)
    keys = [k for k in rows if k <= D(d).isoformat()]
    if not keys:
        raise Unavailable(f"nav_history_{acct}.csv không có dòng <= {d}")
    return rows[max(keys)]


def periods(acct, report_date):
    """Đúng đầu ra CLI `nav_period_returns.py --account A --report-date D` (kèm benchmark)."""
    rows = npr.load_nav_history(acct)
    inc = npr.load_inception(acct)
    return npr.compute_period_returns(acct, D(report_date), rows, inc, benchmark=npr._benchmark_fn())


def _ledger(acct):
    rows = npr.load_nav_history(acct)
    inc = npr.load_inception(acct)
    flows = npr.load_flows(acct, require_file=True)
    frm, nav0 = npr._inception_baseline(rows, inc)
    ledger, _ = npr.build_ledger(rows, flows, frm, nav0)
    return ledger, inc


def ledger(acct):
    """[{date, unit_price, nav, flows}] — sổ giá đơn vị của nav_period_returns (dòng 0 = mốc gốc)."""
    return _ledger(acct)[0]


def extra_period(acct, start, report_date):
    """Kỳ [start, report_date] trên CÙNG sổ + cùng khối benchmark như `_assemble` (dùng cho QTD/YTD).
    start ≤ mốc gốc ⇒ lùi về dòng 0 (đúng hành vi `_period`) và mốc VN-Index = index_anchor_date."""
    led, inc = _ledger(acct)
    i1 = max(i for i, r in enumerate(led) if r["date"] <= D(report_date))
    p = npr._period(led, D(start), i1)
    bm_fn = npr._benchmark_fn()
    at_row0 = p["from_date"] == led[0]["date"].isoformat()
    bm = bm_fn(npr.index_anchor_date(acct, inc) if at_row0 else p["from_date"], p["to_date"])
    for k, col in (("excess_vs_price_pp", "vnindex_price_pct"), ("excess_vs_tr_pp", "vnindex_tr_pct")):
        bm[k] = round(p["return_pct"] - bm[col], 3) if bm.get(col) is not None else None
    p["benchmark"] = bm
    return p


def month_series(acct, report_date):
    """[(nhãn 'MM/YYYY', tỷ suất %, VN-Index giá %, VN-Index có cổ tức %)] từng tháng từ mốc gốc tới
    tháng của report_date — mỗi tháng là `_period` của sổ đơn vị (tháng đầu tính từ mốc gốc)."""
    out = []
    d = D(report_date)
    led, inc = _ledger(acct)
    m = led[0]["date"].replace(day=1)
    if led[0]["date"].day > 25:            # mốc gốc cuối tháng (SpaceX 30/06 → tháng 07 là tháng đầu)
        m = (m + dt.timedelta(days=32)).replace(day=1)
    while m <= d:
        nxt = (m + dt.timedelta(days=32)).replace(day=1)
        end = min(nxt - dt.timedelta(days=1), d)
        p = extra_period(acct, m, end)
        bm = p["benchmark"]
        out.append((f"{m:%m/%Y}", p["return_pct"], bm.get("vnindex_price_pct"), bm.get("vnindex_tr_pct")))
        m = nxt
    return out


def daily_window(acct, start_excl, end):
    """Dòng sổ trong (mốc kỳ, end] + dòng mốc: [(date, unit_price, nav)] — chart NAV theo ngày."""
    led = ledger(acct)
    base = max(i for i, r in enumerate(led) if r["date"] < D(start_excl)) if any(
        r["date"] < D(start_excl) for r in led) else 0
    rows = [r for r in led[base:] if r["date"] <= D(end)]
    return [(r["date"], r["unit_price"], r["nav"]) for r in rows]


def risk_stats(series):
    """series=[(date, value)] (giá đơn vị hoặc VN-Index) → độ biến động ngày, MDD + ngày, tỷ lệ phiên
    tăng. Thống kê mô tả trên sổ đơn vị, cùng phương pháp các bản mock đã đối chiếu (std mẫu)."""
    import statistics as st
    vals = [v for _, v in series]
    rets = [vals[i] / vals[i - 1] - 1 for i in range(1, len(vals))]
    pk, mdd, dday = vals[0], 0.0, series[0][0]
    for d, v in series:
        pk = max(pk, v)
        if v / pk - 1 < mdd:
            mdd, dday = v / pk - 1, d
    sd = st.stdev(rets) * 100 if len(rets) > 1 else None
    return {"n": len(rets), "sd": sd, "ann": sd * 252 ** 0.5 if sd is not None else None,
            "mdd": mdd * 100, "mdd_date": dday,
            "up_ratio": (sum(1 for r in rets if r > 0) / len(rets) * 100) if rets else None}


def vni_close():
    """{date: (vnindex, tr_net)} từ chuỗi benchmark chuẩn."""
    out = {}
    with open(VNI_CSV, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            out[D(r["date"])] = (float(r["vnindex"]), float(r["tr_net"]))
    return out


def vni_on_or_before(vnd, d):
    return vnd[max(k for k in vnd if k <= D(d))]


def excess_pp(period, vnd):
    """Chênh (điểm %) danh mục − VN-Index giá, từ số CHƯA làm tròn (unit_price_ratio + 2 mốc chỉ số
    nav_period_returns khai)."""
    bm = period["benchmark"]
    v0 = vnd[D(bm["index_anchor_date"] if "index_anchor_date" in bm else bm["anchor_date"])][0]
    v1 = vnd[D(bm["index_end_date"] if "index_end_date" in bm else bm["end_date"])][0]
    return (period["unit_price_ratio"] - 1) * 100 - (v1 / v0 - 1) * 100


def period_table_md(acct, report_date):
    """Bảng 'Hiệu suất lũy kế' = NGUYÊN đầu ra `period_table_32.py` (cổng benchmark-table đối chiếu)."""
    import subprocess
    cmd = [sys.executable, os.path.join(BIN, "period_table_32.py"), "--account", acct,
           "--report-date", D(report_date).isoformat()] + (["--with-sleeve"] if acct == "ZaloPay" else [])
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise Unavailable(f"period_table_32.py rc={p.returncode}: {p.stderr.strip()[-400:]}")
    return p.stdout.strip()


def sleeve_periods(acct, report_date):
    """Chuỗi 'phần bot quản lý' (chỉ ZaloPay) — None nếu chưa có số."""
    try:
        rows = npr.load_nav_history(acct)
        inc = npr.load_inception(acct)
        return npr.compute_sleeve_period_returns(acct, D(report_date), rows, inc, benchmark=npr._benchmark_fn())
    except Exception as exc:  # noqa: BLE001 — chuỗi phụ; lý do in vào báo cáo nội bộ
        return {"unavailable": f"{type(exc).__name__}: {exc}"}


# ───────────────────────── vị thế / lệnh / phí ─────────────────────────
def account_no(acct):
    import portfolio_status as ps
    return ps.account_no_for(acct)


def position_returns(acct, date):
    """§21: đúng hàm cổng tỉ suất dùng. stdout công cụ đẩy sang stderr."""
    import contextlib
    with contextlib.redirect_stdout(sys.stderr):
        import report_return_gate as rrg
        return rrg.position_returns(acct, D(date).isoformat())


def positions_qty(acct, date):
    """{mã: KL} từ bản ghi positions CUỐI của dnse_raw_<date> (lọc account_no, §12)."""
    import portfolio_status as ps
    pos = ps.broker_positions_with_cost(account_no(acct), D(date).isoformat())
    if pos is None:
        raise Unavailable(f"không có dnse_raw_{D(date)}.jsonl/positions cho {acct}")
    return {k: int(round(v["qty"])) for k, v in pos.items()}


def _confirm_rows(acct_no, d):
    path = f"{EL}/dnse_khoplenh_broker_confirm_{d:%d-%m-%Y}.csv"
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh) if r.get("tieu_khoan") == acct_no]


def fills(acct, start_excl, end):
    """Lệnh khớp (start_excl, end]: [{date, side B/S, ticker, qty, value, fee, tax, fee_src}].
    Nguồn KL/giá: order_history CUỐI NGÀY của dnse_raw (gồm lệnh tay). Phí/thuế: email xác nhận
    khớp lệnh của CTCK nếu có cho ngày đó (khớp đúng (mã, chiều)), còn lại ước theo biểu phí."""
    import dnse_fee_rates as fr
    acct_no = account_no(acct)
    out, d = [], D(start_excl) + dt.timedelta(days=1)
    missing_days = []
    while d <= D(end):
        path = f"{EL}/dnse_raw_{d}.jsonl"
        if os.path.exists(path):
            # Hợp theo `id` lệnh: trạng thái CUỐI của từng lệnh trong các bản ghi `orders` (bot, trong
            # phiên) ∪ `order_history` cuối ngày (có cả lệnh tay; không phải ngày nào cũng có).
            by_id, hist_by_id, has_hist = {}, {}, False
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    try:
                        rec = json.loads(line)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        continue
                    if rec.get("account_no") != acct_no:      # §12 — dòng đầu tiên là lọc account
                        continue
                    kind = rec.get("kind")
                    if kind == "orders":
                        lst = rec.get("payload", {}).get("orders") or []
                    elif kind == "order_history":
                        lst, has_hist = rec.get("payload", {}).get("data") or [], True
                    else:
                        continue
                    for o in lst:
                        if o.get("id") is not None:
                            (hist_by_id if kind == "order_history" else by_id)[o["id"]] = o
            day_fills = []
            # Ngày có order_history: chỉ dùng nó (đầy đủ, gồm lệnh tay) — `id` của bản ghi `orders`
            # trong phiên KHÔNG trùng hệ id của order_history (đo 29/10: MCH bị đếm 2 lần khi hợp).
            if has_hist:
                by_id = hist_by_id
            for o in by_id.values():
                q = int(o.get("fillQuantity") or 0)
                if q <= 0 or str(o.get("transDate") or d) != str(d):
                    continue
                side = "B" if o.get("side") == "NB" else "S"
                day_fills.append({"date": d, "side": side, "ticker": o["symbol"], "qty": q,
                                  "value": q * float(o.get("averagePrice") or 0)})
            if not has_hist and d.weekday() < 5:
                missing_days.append(d)
            conf = _confirm_rows(acct_no, d)
            agg = {}
            for f in day_fills:
                k = (f["ticker"], f["side"])
                a = agg.setdefault(k, {"date": d, "side": f["side"], "ticker": f["ticker"], "qty": 0, "value": 0.0})
                a["qty"] += f["qty"]; a["value"] += f["value"]
            for (tk, side), a in sorted(agg.items()):
                c = [r for r in (conf or []) if r["ma"] == tk and (r["loai_lenh"] == "MUA") == (side == "B")]
                if c and sum(int(r["khoi_luong"]) for r in c) == a["qty"]:
                    a["fee"] = sum(int(r["phi_tra_so"]) + int(r["phi_dnse"]) for r in c)
                    a["tax"] = sum(float(r["thue"]) for r in c)
                    a["fee_src"] = "xác nhận CTCK"
                else:
                    rate = fr.FEE_RATE_BUY_PCT if side == "B" else fr.FEE_RATE_SELL_PCT
                    a["fee"] = round(a["value"] * rate / 100)
                    a["tax"] = a["value"] * fr.SELL_TAX_RATE if side == "S" else 0.0
                    a["fee_src"] = "ước theo biểu phí"
                out.append(a)
        elif d.weekday() < 5:
            missing_days.append(d)
        d += dt.timedelta(days=1)
    return out, missing_days


def close_prices(tickers, date):
    """Giá đóng cửa CHƯA điều chỉnh (`Price`) của phiên mới nhất ≤ date, từng mã. KHÔNG dùng
    `Close`: cột đó điều chỉnh lùi theo cổ tức về sau ⇒ giá đầu kỳ bị hạ (đo 30/09 SpaceX: Σ KL×Close
    620,53 tr vs mtm_stock nav_history 630,67 tr). Cùng khuôn truy vấn verify_account_snapshot.bq_close_sql."""
    import subprocess
    import verify_account_snapshot as vas
    if not tickers:
        return {}
    tick_list = ",".join(f"'{t}'" for t in sorted(tickers))
    sql = (f"SELECT t.ticker, t.Price, CAST(t.time AS STRING) AS time FROM tav2_bq.ticker AS t "
           f"WHERE t.ticker IN ({tick_list}) AND t.time <= '{D(date).isoformat()}' AND t.time >= "
           f"DATE_SUB(DATE '{D(date).isoformat()}', INTERVAL 30 DAY) "
           f"QUALIFY ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time DESC) = 1")
    env = dict(os.environ)
    env["PATH"] = vas.BQ_PATH_PREFIX + ":" + env.get("PATH", "")
    out = subprocess.run(["bq", "query", "--use_legacy_sql=false", "--project_id=lithe-record-440915-m9",
                          "--format=json", "--max_rows=5000", sql], capture_output=True, text=True, env=env)
    if out.returncode != 0:
        raise Unavailable(f"BQ giá {date}: {(out.stderr.strip() or out.stdout.strip())[-300:]}")
    rows = json.loads(out.stdout)
    got = {r["ticker"]: float(r["Price"]) for r in rows}
    miss = set(tickers) - set(got)
    if miss:
        raise Unavailable(f"BQ không có giá {sorted(miss)} ≤ {date}")
    return got


def last_trading_on_or_before(acct, d):
    """Ngày của dòng nav_history gần nhất ≤ d (cuối tháng rơi vào thứ Bảy ⇒ thứ Sáu)."""
    return D(nav_row_on_or_before(acct, d)["date"])


def attribution(acct, start_row_date, end_row_date):
    """Đóng góp theo mã (VND) trong (start, end]: KL×giá cuối − KL×giá đầu − tiền mua + tiền bán.
    KL đầu/cuối từ sổ vị thế broker; lệnh từ order_history; giá đóng cửa bq_close_prices.
    Trả kèm đối soát: Σ KL đầu + mua − bán phải = KL cuối từng mã (lệch ⇒ mã đó gắn cờ, thường là
    cổ tức bằng cổ phiếu/quyền mua), và Σ KL×giá phải ≈ mtm_stock của nav_history (phần dư in ra)."""
    q0 = positions_qty(acct, start_row_date)
    q1 = positions_qty(acct, end_row_date)
    fl, missing = fills(acct, start_row_date, end_row_date)
    tks = set(q0) | set(q1) | {f["ticker"] for f in fl}
    p0 = close_prices(set(q0), start_row_date)
    p1 = close_prices(set(q1), end_row_date)
    rows, qty_flags = {}, []
    for t in sorted(tks):
        buy = sum(f["value"] for f in fl if f["ticker"] == t and f["side"] == "B")
        sell = sum(f["value"] for f in fl if f["ticker"] == t and f["side"] == "S")
        qb = sum(f["qty"] for f in fl if f["ticker"] == t and f["side"] == "B")
        qs = sum(f["qty"] for f in fl if f["ticker"] == t and f["side"] == "S")
        if q0.get(t, 0) + qb - qs != q1.get(t, 0):
            qty_flags.append((t, q0.get(t, 0), qb, qs, q1.get(t, 0)))
        rows[t] = q1.get(t, 0) * p1.get(t, 0.0) - q0.get(t, 0) * p0.get(t, 0.0) - buy + sell
    n0 = nav_row_on_or_before(acct, start_row_date)
    n1 = nav_row_on_or_before(acct, end_row_date)
    mtm0 = sum(q * p0.get(t, 0.0) for t, q in q0.items())
    mtm1 = sum(q * p1.get(t, 0.0) for t, q in q1.items())
    return {"by_ticker": rows, "fills": fl, "missing_days": missing, "qty_flags": qty_flags,
            "q0": q0, "q1": q1, "p0": p0, "p1": p1,
            "mtm_check": {"calc0": mtm0, "nav0_mtm": float(n0["mtm_stock"]),
                          "calc1": mtm1, "nav1_mtm": float(n1["mtm_stock"])}}


# ───────────────────────── thị trường ─────────────────────────
def market_facts(kind, period_end):
    """(meta, {nhãn: giá trị}) — dữ kiện script tính của khối kỹ thuật (không có diễn giải LLM)."""
    import livermore_report_block as L
    f = L.build_facts(kind, D(period_end))
    facts = f.get("facts")
    if isinstance(facts, str):
        facts = json.loads(facts.replace("'", '"'))
    return {k: v for k, v in f.items() if k != "facts"}, {k: v for k, v in facts}


def market_pass_block(kind, period_end):
    """Khối PASS của kỳ (nếu đã có): {md, sha256, forecast...} — để manifest bám sha (cổng giao)."""
    import livermore_report_block as L
    as_of = L.period_bounds(kind, D(period_end))[0]
    ok, meta = L.verify_pass(as_of, kind)
    if not ok:
        return None
    path = os.path.join(LIVERMORE_DIR, f"report_block_{as_of}_{kind}.json")
    try:
        with open(path, encoding="utf-8") as fh:
            j = json.load(fh)
    except OSError:
        j = dict(meta)
    import hashlib
    with open(meta["md"], encoding="utf-8") as fh:
        block = fh.read().strip()
    j["block_sha256"] = hashlib.sha256(block.encode("utf-8")).hexdigest()
    return j


def regime_lines():
    """(trạng thái DT gate, Value Radar) dạng chuỗi — §6b, không tự tính phân vị."""
    try:
        from dna_report import build_dt_gate_line, build_value_radar_line
        import contextlib
        import io
        with contextlib.redirect_stderr(io.StringIO()):
            return build_dt_gate_line(html=False), build_value_radar_line(html=False)
    except Exception as exc:  # noqa: BLE001
        raise Unavailable(f"dna_report: {type(exc).__name__}: {exc}")
