"""Nạp số liệu cho báo cáo tài khoản v2 — CHỈ đọc nguồn/pipeline đã có, không tự tính tỷ suất.

| Số                                   | Nguồn (gọi trực tiếp, không sao chép công thức)                       |
|--------------------------------------|-----------------------------------------------------------------------|
| NAV, cấu phần (cổ phiếu/tiền/Trứng)  | data/execution_logs/nav_history_<acct>.csv (daily_nav_snapshot.py ghi) |
| Tỷ suất kỳ (ngày/tuần/MTD/từ đầu)    | bin/nav_period_returns.py → compute_period_returns (§31)              |
| Chuỗi giá đơn vị đã loại dòng tiền   | bin/nav_period_returns.py → build_ledger (cùng sổ với dòng trên)      |
| VN-Index đóng cửa (+ bản có cổ tức)  | data/benchmark/vnindex_tr_daily.csv (vnindex_total_return.py)         |
| OHLCV + MA20/50/200 + độ rộng %>MA50 | bin/livermore_report_block.py loaders (cùng nguồn khối Livermore)     |
| Khối kỹ thuật (dữ kiện + dự báo mở)  | data/livermore/report_block_<date>_weekly.json                        |
| Attribution / lệnh / vị thế tuần     | artifact của job báo cáo gốc (calc.json, tables.json) — tái hiển thị  |

Chạy bằng python3 hệ thống (cần BQ env cho loader Livermore: source wc_env.sh).
"""
import csv
import datetime as dt
import json
import os
import sys

WC = "/home/trido/thanhdt/WorkingClaude"
MIKE = f"{WC}/mike"
BIN = f"{MIKE}/bin"
EL = f"{WC}/data/execution_logs"
VNI_CSV = f"{WC}/data/benchmark/vnindex_tr_daily.csv"
if BIN not in sys.path:
    sys.path.insert(0, BIN)

import nav_period_returns as npr  # noqa: E402


def D(s):
    return dt.date.fromisoformat(s) if isinstance(s, str) else s


def nav_history(acct):
    with open(f"{EL}/nav_history_{acct}.csv", encoding="utf-8") as fh:
        return {r["date"]: r for r in csv.DictReader(fh)}


def periods(acct, report_date):
    """Đúng đầu ra CLI `nav_period_returns.py --account A --report-date D` (kèm benchmark)."""
    rows = npr.load_nav_history(acct)
    inc = npr.load_inception(acct)
    return npr.compute_period_returns(acct, D(report_date), rows, inc, benchmark=npr._benchmark_fn())


def unit_ledger(acct):
    """[(date, unit_price, nav)] — sổ giá đơn vị của nav_period_returns (dòng tiền đã loại theo
    timing bod/eod khai trong cash_flows). Dòng đầu = mốc khởi điểm (account_inception.json)."""
    rows = npr.load_nav_history(acct)
    inc = npr.load_inception(acct)
    flows = npr.load_flows(acct, require_file=True)
    frm, nav0 = npr._inception_baseline(rows, inc)
    ledger, _ = npr.build_ledger(rows, flows, frm, nav0)
    return [(r["date"], r["unit_price"], r["nav"]) for r in ledger]


def vni_close():
    """{date: (vnindex, tr_net)} từ chuỗi benchmark chuẩn."""
    out = {}
    with open(VNI_CSV, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            out[D(r["date"])] = (float(r["vnindex"]), float(r["tr_net"]))
    return out


def tape(start, end):
    """OHLCV + chỉ báo + độ rộng, cùng loader khối Livermore (BQ)."""
    import livermore_report_block as L
    bars = [b for b in L.C.get_bars(D(start), D(end)) if D(start) <= b["time"] <= D(end)]
    ind = L.get_indicators(D(start), D(end))
    br = L.get_breadth(D(start), D(end))
    return bars, ind, br


def livermore_block(date="2026-10-30"):
    with open(f"{MIKE}/data/livermore/report_block_{date}_weekly.json", encoding="utf-8") as fh:
        return json.load(fh)


def weekly_artifacts(job_dir=f"{MIKE}/agents/Taylor/research/weekly_20261026_20261030"):
    """calc.json (attribution, lệnh) + tables.json (vị thế, rủi ro) mà báo cáo tuần gốc đã in."""
    with open(f"{job_dir}/calc.json", encoding="utf-8") as fh:
        calc = json.load(fh)
    with open(f"{job_dir}/tables.json", encoding="utf-8") as fh:
        tables = json.load(fh)
    return calc, tables


def vni_on_or_before(vnd, d):
    """VN-Index phiên gần nhất ≤ d (nav_history có dòng ngày nghỉ HOSE, vd 31/08/2026)."""
    return vnd[max(k for k in vnd if k <= d)]


def excess_pp(period, vnd):
    """Chênh (điểm %) danh mục − VN-Index giá, từ số CHƯA làm tròn: unit_price_ratio của
    nav_period_returns và hai mốc VN-Index mà chính nó khai (index_anchor_date → index_end_date).
    Trừ hai số đã làm tròn 3 chữ số có thể lệch 0,01 khi in (ca 2,675 → 2,68 vs 2,6748 → 2,67)."""
    bm = period["benchmark"]
    v0 = vnd[D(bm["index_anchor_date"])][0]
    v1 = vnd[D(bm["index_end_date"])][0]
    return (period["unit_price_ratio"] - 1) * 100 - (v1 / v0 - 1) * 100
