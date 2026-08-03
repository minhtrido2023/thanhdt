#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DNSE portfolio dashboard — read-only (no trading-token/OTP ever requested).

Fetches balances/positions/order-history from DNSE OpenAPI v2 via the existing
`dnse_api.DNSEClient`, appends today's NAV to a local CSV history, and renders a
single self-contained HTML file (no server, no CDN — open it directly in a
browser). Data-provenance rules followed:
  - 3 cash fields kept distinct (availableCash vs totalCash vs NAV), never
    conflated (see tbot/kb/concepts/dnse-openapi-v2-calling-guideline/).
  - Quotes read the G1 (round-lot) board explicitly, never rows[0] blindly.
  - Fields not confirmed present (e.g. margin debt, cost basis) render as "—"
    instead of a fabricated 0/guess.

Usage:
    python3 build_dashboard.py [--creds PATH] [--label NAME] [--days N] [--out PATH]
    python3 build_dashboard.py --demo   # render with synthetic data, no API calls
"""
import argparse
import csv
import json
import os
import sys
from datetime import date, datetime, timedelta

WORKDIR = os.path.dirname(os.path.abspath(__file__))
TBOT_ROOT = os.path.normpath(os.path.join(WORKDIR, "..", ".."))          # tbot/
REPO_ROOT = os.path.dirname(TBOT_ROOT)                                    # WorkingClaude/ (dnse_api.py lives here)
sys.path.insert(0, REPO_ROOT)

DATA_DIR = os.path.join(WORKDIR, "data")
OUTPUT_DIR = os.path.join(TBOT_ROOT, "html", "dashboards", "dnse_portfolio")


# --------------------------------------------------------------- defensive parsing

def _get(d, *names):
    """Case-insensitive, multi-spelling field lookup (DNSE JSON isn't uniform)."""
    if not isinstance(d, dict):
        return None
    lower_map = {k.lower(): v for k, v in d.items()}
    for n in names:
        if n in d:
            return d[n]
        if n.lower() in lower_map:
            return lower_map[n.lower()]
    return None


def _num(v, default=0.0):
    if v is None or v == "":
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _unwrap_balances(bal):
    """balances can be a bare object, a 1-element list, or nested under 'stock'."""
    row = bal[0] if isinstance(bal, list) and bal else bal
    if isinstance(row, dict) and isinstance(row.get("stock"), dict):
        row = row["stock"]
    return row if isinstance(row, dict) else {}


def _as_rows(resp, *list_keys):
    """Unwrap a {"<key>": [...]} or bare-list response into a list of dict rows."""
    if isinstance(resp, list):
        return resp
    if isinstance(resp, dict):
        for k in list_keys:
            v = _get(resp, k)
            if isinstance(v, list):
                return v
    return []


def _pick_g1(resp):
    """Market-data endpoints return per-board arrays — always pick G1 (round lot)."""
    rows = resp if isinstance(resp, list) else None
    if rows is None:
        return resp if isinstance(resp, dict) else {}
    for row in rows:
        board = _get(row, "boardId", "board")
        if board == "G1":
            return row
    return rows[0] if rows else {}


# ------------------------------------------------------------------- data fetch

def fetch_portfolio(creds_path, account_no, days):
    from dnse_api import DNSEClient  # local import: only needed for live mode

    client = DNSEClient.from_credentials_file(creds_path) if creds_path \
        else DNSEClient.from_credentials_file()

    accounts_resp = client.accounts()
    accounts = _as_rows(accounts_resp, "accounts")
    if account_no is None:
        if not accounts:
            raise SystemExit("GET /accounts trả rỗng — kiểm tra api_key/api_secret.")
        account_no = _get(accounts[0], "id", "accountNo", "accountNumber")

    bal_raw = client.balances(account_no)
    brow = _unwrap_balances(bal_raw)
    available_cash = _num(_get(brow, "availableCash"))
    total_cash = _num(_get(brow, "totalCash"))
    margin_debt_raw = _get(brow, "marginDebt", "totalDebt", "loanAmount", "debt")
    margin_debt = _num(margin_debt_raw) if margin_debt_raw is not None else None

    pos_raw = client.positions(account_no)
    pos_rows = _as_rows(pos_raw, "positions", "data")

    positions = []
    market_value_sum = 0.0
    for row in pos_rows:
        symbol = _get(row, "symbol")
        if not symbol:
            continue
        total_qty = _num(_get(row, "quantity", "total", "totalQuantity"))
        sellable_qty = _get(row, "sellableQuantity", "tradeQuantity", "availableQuantity")
        avg_price = _get(row, "avgPrice", "costPrice", "averageCostPrice", "averagePrice")
        try:
            trade_raw = client.latest_trade(symbol)
            match_price = _num(_get(_pick_g1(trade_raw), "matchPrice"))
        except Exception:
            match_price = 0.0
        mv = total_qty * match_price
        market_value_sum += mv
        positions.append({
            "symbol": symbol,
            "quantity": total_qty,
            "sellable": _num(sellable_qty) if sellable_qty is not None else None,
            "avg_price": _num(avg_price) if avg_price is not None else None,
            "last_price": match_price,
            "market_value": mv,
        })

    nav = total_cash + market_value_sum - (margin_debt or 0.0)

    to_date = date.today()
    from_date = to_date - timedelta(days=days)
    hist_raw = client.order_history(account_no, from_date=from_date.isoformat(),
                                     to_date=to_date.isoformat())
    hist_rows = _as_rows(hist_raw, "orders", "data")
    transactions = []
    for row in hist_rows:
        side_raw = _get(row, "side")
        side = {"NB": "Mua", "NS": "Bán"}.get(side_raw, side_raw)
        transactions.append({
            "date": _get(row, "transactionDate", "date", "createdDate", "matchedDate"),
            "symbol": _get(row, "symbol"),
            "side": side,
            "quantity": _num(_get(row, "quantity", "matchedQuantity", "fillQuantity")),
            "price": _num(_get(row, "price", "matchedPrice", "averagePrice")),
            "status": _get(row, "orderStatus", "status"),
        })
    transactions.sort(key=lambda t: t["date"] or "", reverse=True)

    return {
        "account_no": str(account_no),
        "available_cash": available_cash,
        "total_cash": total_cash,
        "margin_debt": margin_debt,
        "nav": nav,
        "positions": positions,
        "transactions": transactions,
    }


def demo_portfolio():
    """Synthetic data — lets the HTML be built/inspected with no API access."""
    return {
        "account_no": "0000000000 (demo)",
        "available_cash": 42_150_000.0,
        "total_cash": 58_400_000.0,
        "margin_debt": 0.0,
        "nav": 1_178_010_000.0,
        "positions": [
            {"symbol": "VNM", "quantity": 3000, "sellable": 3000, "avg_price": 62500,
             "last_price": 64800, "market_value": 3000 * 64800},
            {"symbol": "FPT", "quantity": 5000, "sellable": 4500, "avg_price": 118000,
             "last_price": 121500, "market_value": 5000 * 121500},
            {"symbol": "MBB", "quantity": 10000, "sellable": 10000, "avg_price": 22300,
             "last_price": 21800, "market_value": 10000 * 21800},
        ],
        "transactions": [
            {"date": "2026-08-03", "symbol": "FPT", "side": "Mua", "quantity": 500,
             "price": 121500, "status": "Filled"},
            {"date": "2026-08-01", "symbol": "MBB", "side": "Mua", "quantity": 2000,
             "price": 21900, "status": "Filled"},
            {"date": "2026-07-29", "symbol": "VNM", "side": "Bán", "quantity": 500,
             "price": 63200, "status": "Filled"},
        ],
    }


# --------------------------------------------------------------------- NAV history

def update_nav_history(history_path, snapshot):
    today = date.today().isoformat()
    rows = {}
    if os.path.exists(history_path):
        with open(history_path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                rows[r["date"]] = r
    rows[today] = {
        "date": today,
        "nav": f"{snapshot['nav']:.2f}",
        "total_cash": f"{snapshot['total_cash']:.2f}",
        "available_cash": f"{snapshot['available_cash']:.2f}",
        "margin_debt": f"{(snapshot['margin_debt'] or 0.0):.2f}",
    }
    tmp_path = history_path + ".tmp"
    os.makedirs(os.path.dirname(history_path), exist_ok=True)
    with open(tmp_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "nav", "total_cash",
                                          "available_cash", "margin_debt"])
        w.writeheader()
        for d in sorted(rows):
            w.writerow(rows[d])
    os.replace(tmp_path, history_path)

    return [{"date": d, "nav": float(rows[d]["nav"])} for d in sorted(rows)]


# -------------------------------------------------------------------------- render

HTML_TEMPLATE = """<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DNSE Portfolio Dashboard</title>
<style>
  .viz-root {
    color-scheme: light;
    --surface-1:      #fcfcfb;
    --page-plane:     #f9f9f7;
    --text-primary:   #0b0b0b;
    --text-secondary: #52514e;
    --text-muted:     #898781;
    --gridline:       #e1e0d9;
    --baseline:       #c3c2b7;
    --series-1:       #2a78d6;
    --series-1-wash:  rgba(42,120,214,0.10);
    --good:           #006300;
    --critical:       #d03b3b;
    --border:         rgba(11,11,11,0.10);
  }
  @media (prefers-color-scheme: dark) {
    .viz-root {
      color-scheme: dark;
      --surface-1:      #1a1a19;
      --page-plane:     #0d0d0d;
      --text-primary:   #ffffff;
      --text-secondary: #c3c2b7;
      --text-muted:     #898781;
      --gridline:       #2c2c2a;
      --baseline:       #383835;
      --series-1:       #3987e5;
      --series-1-wash:  rgba(57,135,229,0.12);
      --good:           #0ca30c;
      --critical:       #e66767;
      --border:         rgba(255,255,255,0.10);
    }
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 24px;
    background: var(--page-plane);
    color: var(--text-primary);
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  }
  .wrap { max-width: 960px; margin: 0 auto; }
  h1 { font-size: 18px; font-weight: 600; margin: 0 0 4px; }
  .asof { color: var(--text-muted); font-size: 12px; margin-bottom: 20px; }
  .card {
    background: var(--surface-1);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
  }
  .card h2 { font-size: 13px; font-weight: 600; color: var(--text-secondary);
             text-transform: uppercase; letter-spacing: 0.04em; margin: 0 0 14px; }
  .hero-row { display: flex; gap: 32px; flex-wrap: wrap; align-items: baseline; }
  .hero-value { font-size: 32px; font-weight: 600; }
  .hero-delta { font-size: 14px; font-weight: 600; }
  .stat-line { font-size: 13px; color: var(--text-secondary); margin-top: 10px; }
  .stat-line b { color: var(--text-primary); font-variant-numeric: tabular-nums; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th, td { text-align: right; padding: 7px 8px; border-bottom: 1px solid var(--gridline); }
  th:first-child, td:first-child { text-align: left; }
  th { color: var(--text-muted); font-weight: 600; font-size: 11px;
       text-transform: uppercase; letter-spacing: 0.03em; }
  td { font-variant-numeric: tabular-nums; }
  .pos { color: var(--good); }
  .neg { color: var(--critical); }
  .muted { color: var(--text-muted); }
  #navChart { width: 100%; height: 220px; display: block; }
  .tooltip {
    position: absolute; pointer-events: none; background: var(--surface-1);
    border: 1px solid var(--border); border-radius: 6px; padding: 6px 10px;
    font-size: 12px; color: var(--text-primary); box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    display: none; white-space: nowrap;
  }
  .chart-wrap { position: relative; }
  .no-data { color: var(--text-muted); font-size: 13px; }
</style>
</head>
<body class="viz-root">
<div class="wrap">
  <h1>DNSE Portfolio Dashboard — __ACCOUNT_LABEL__</h1>
  <div class="asof">Số liệu tính đến __GENERATED_AT__ · account __ACCOUNT_NO__</div>

  <div class="card">
    <h2>Daily NAV</h2>
    <div class="hero-row">
      <div class="hero-value">__NAV_FMT__</div>
      <div class="hero-delta" id="heroDelta"></div>
    </div>
    <div class="stat-line">Tiền mặt đã settle (availableCash): <b>__AVAIL_CASH_FMT__</b>
      &nbsp;·&nbsp; Tổng tiền dùng cho NAV (totalCash): <b>__TOTAL_CASH_FMT__</b></div>
    <div class="chart-wrap">
      <svg id="navChart" viewBox="0 0 900 220" preserveAspectRatio="none"></svg>
      <div class="tooltip" id="navTooltip"></div>
    </div>
  </div>

  <div class="card">
    <h2>Current Portfolio</h2>
    <div id="portfolioTable"></div>
  </div>

  <div class="card">
    <h2>Transaction History</h2>
    <div id="txTable"></div>
  </div>
</div>

<script>
const DATA = __DATA_JSON__;

function fmtVND(n) {
  if (n === null || n === undefined || isNaN(n)) return "—";
  return Math.round(n).toLocaleString("vi-VN");
}
function fmtPct(n) {
  if (n === null || n === undefined || isNaN(n)) return "—";
  const s = (n >= 0 ? "+" : "") + n.toFixed(2) + "%";
  return s;
}

function renderPortfolioTable() {
  const el = document.getElementById("portfolioTable");
  const rows = DATA.positions || [];
  if (!rows.length) { el.innerHTML = '<div class="no-data">Không có vị thế nào.</div>'; return; }
  const navTotal = rows.reduce((s, r) => s + (r.market_value || 0), 0);
  let html = "<table><thead><tr>" +
    "<th>Mã</th><th>KL đang giữ</th><th>KL bán được</th>" +
    "<th>Giá vốn</th><th>Giá hiện tại</th><th>Giá trị thị trường</th>" +
    "<th>Lãi/lỗ</th><th>Tỷ trọng</th></tr></thead><tbody>";
  rows.forEach(r => {
    const hasCost = r.avg_price !== null && r.avg_price !== undefined && r.avg_price > 0;
    const pnlPct = hasCost ? (r.last_price - r.avg_price) / r.avg_price * 100 : null;
    const pnlCls = pnlPct === null ? "muted" : (pnlPct >= 0 ? "pos" : "neg");
    const weight = navTotal > 0 ? (r.market_value / navTotal * 100) : 0;
    html += "<tr>" +
      "<td>" + r.symbol + "</td>" +
      "<td>" + fmtVND(r.quantity) + "</td>" +
      "<td>" + (r.sellable === null || r.sellable === undefined ? "—" : fmtVND(r.sellable)) + "</td>" +
      "<td>" + (hasCost ? fmtVND(r.avg_price) : "—") + "</td>" +
      "<td>" + fmtVND(r.last_price) + "</td>" +
      "<td>" + fmtVND(r.market_value) + "</td>" +
      "<td class=\\"" + pnlCls + "\\">" + fmtPct(pnlPct) + "</td>" +
      "<td>" + weight.toFixed(1) + "%</td>" +
      "</tr>";
  });
  html += "</tbody></table>";
  el.innerHTML = html;
}

function renderTxTable() {
  const el = document.getElementById("txTable");
  const rows = DATA.transactions || [];
  if (!rows.length) { el.innerHTML = '<div class="no-data">Không có giao dịch nào trong khoảng thời gian này.</div>'; return; }
  let html = "<table><thead><tr>" +
    "<th>Ngày</th><th>Mã</th><th>Lệnh</th><th>KL</th><th>Giá</th><th>Trạng thái</th></tr></thead><tbody>";
  rows.forEach(t => {
    html += "<tr>" +
      "<td>" + (t.date || "—") + "</td>" +
      "<td>" + (t.symbol || "—") + "</td>" +
      "<td>" + (t.side || "—") + "</td>" +
      "<td>" + fmtVND(t.quantity) + "</td>" +
      "<td>" + fmtVND(t.price) + "</td>" +
      "<td>" + (t.status || "—") + "</td>" +
      "</tr>";
  });
  html += "</tbody></table>";
  el.innerHTML = html;
}

function renderHeroDelta() {
  const hist = DATA.nav_history || [];
  const el = document.getElementById("heroDelta");
  if (hist.length < 2) { el.textContent = ""; return; }
  const prev = hist[hist.length - 2].nav;
  const cur = hist[hist.length - 1].nav;
  const delta = cur - prev;
  const pct = prev !== 0 ? delta / prev * 100 : 0;
  el.className = "hero-delta " + (delta >= 0 ? "pos" : "neg");
  el.textContent = (delta >= 0 ? "+" : "") + fmtVND(delta) + " (" + fmtPct(pct) + " so với phiên trước)";
}

function renderNavChart() {
  const hist = DATA.nav_history || [];
  const svg = document.getElementById("navChart");
  const tooltip = document.getElementById("navTooltip");
  if (hist.length < 2) {
    svg.outerHTML = '<div class="no-data">Chưa đủ dữ liệu NAV (cần ≥2 ngày) — chạy script này lại vào ngày mai để thấy đường NAV.</div>';
    return;
  }
  const W = 900, H = 220, padL = 60, padR = 16, padT = 12, padB = 24;
  const navs = hist.map(d => d.nav);
  const minNav = Math.min.apply(null, navs);
  const maxNav = Math.max.apply(null, navs);
  const span = (maxNav - minNav) || 1;
  const x = i => padL + (i / (hist.length - 1)) * (W - padL - padR);
  const y = v => padT + (1 - (v - minNav) / span) * (H - padT - padB);

  const ns = "http://www.w3.org/2000/svg";
  function el(tag, attrs) {
    const e = document.createElementNS(ns, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    return e;
  }

  const gridSteps = 4;
  for (let i = 0; i <= gridSteps; i++) {
    const v = minNav + span * i / gridSteps;
    const gy = y(v);
    svg.appendChild(el("line", {x1: padL, x2: W - padR, y1: gy, y2: gy,
      stroke: "var(--gridline)", "stroke-width": 1}));
    const label = el("text", {x: 4, y: gy + 4, fill: "var(--text-muted)", "font-size": 11});
    label.textContent = Math.round(v).toLocaleString("vi-VN");
    svg.appendChild(label);
  }

  let areaPath = "M " + x(0) + " " + y(navs[0]);
  let linePath = "M " + x(0) + " " + y(navs[0]);
  for (let i = 1; i < hist.length; i++) {
    areaPath += " L " + x(i) + " " + y(navs[i]);
    linePath += " L " + x(i) + " " + y(navs[i]);
  }
  areaPath += " L " + x(hist.length - 1) + " " + (H - padB) + " L " + x(0) + " " + (H - padB) + " Z";

  svg.appendChild(el("path", {d: areaPath, fill: "var(--series-1-wash)", stroke: "none"}));
  svg.appendChild(el("path", {d: linePath, fill: "none", stroke: "var(--series-1)",
    "stroke-width": 2, "stroke-linecap": "round", "stroke-linejoin": "round"}));

  const lastX = x(hist.length - 1), lastY = y(navs[navs.length - 1]);
  svg.appendChild(el("circle", {cx: lastX, cy: lastY, r: 5, fill: "var(--series-1)",
    stroke: "var(--surface-1)", "stroke-width": 2}));

  const crosshair = el("line", {x1: 0, x2: 0, y1: padT, y2: H - padB,
    stroke: "var(--baseline)", "stroke-width": 1, style: "display:none"});
  svg.appendChild(crosshair);
  const hoverDot = el("circle", {r: 5, fill: "var(--series-1)", stroke: "var(--surface-1)",
    "stroke-width": 2, style: "display:none"});
  svg.appendChild(hoverDot);

  const overlay = el("rect", {x: padL, y: padT, width: W - padL - padR, height: H - padT - padB,
    fill: "transparent"});
  svg.appendChild(overlay);

  overlay.addEventListener("mousemove", function(evt) {
    const rect = svg.getBoundingClientRect();
    const relX = (evt.clientX - rect.left) / rect.width * W;
    let idx = Math.round((relX - padL) / (W - padL - padR) * (hist.length - 1));
    idx = Math.max(0, Math.min(hist.length - 1, idx));
    const px = x(idx), py = y(navs[idx]);
    crosshair.setAttribute("x1", px); crosshair.setAttribute("x2", px);
    crosshair.style.display = "block";
    hoverDot.setAttribute("cx", px); hoverDot.setAttribute("cy", py);
    hoverDot.style.display = "block";
    tooltip.style.display = "block";
    tooltip.style.left = (rect.left + px * rect.width / W + 12) + "px";
    tooltip.style.top = (rect.top + py * rect.height / H - 10 + window.scrollY) + "px";
    tooltip.innerHTML = hist[idx].date + "<br><b>" + fmtVND(hist[idx].nav) + "</b>";
  });
  overlay.addEventListener("mouseleave", function() {
    crosshair.style.display = "none";
    hoverDot.style.display = "none";
    tooltip.style.display = "none";
  });
}

renderHeroDelta();
renderNavChart();
renderPortfolioTable();
renderTxTable();
</script>
</body>
</html>
"""


def render_html(account_label, snapshot, nav_history, out_path):
    payload = dict(snapshot)
    payload["nav_history"] = nav_history
    html = (HTML_TEMPLATE
            .replace("__ACCOUNT_LABEL__", account_label)
            .replace("__ACCOUNT_NO__", snapshot["account_no"])
            .replace("__GENERATED_AT__", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            .replace("__NAV_FMT__", f"{snapshot['nav']:,.0f}".replace(",", "."))
            .replace("__AVAIL_CASH_FMT__", f"{snapshot['available_cash']:,.0f}".replace(",", "."))
            .replace("__TOTAL_CASH_FMT__", f"{snapshot['total_cash']:,.0f}".replace(",", "."))
            .replace("__DATA_JSON__", json.dumps(payload, ensure_ascii=False)))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--creds", default=None, help="path to DNSE credentials JSON "
                     "(default: secrets/dnse_credentials.json)")
    ap.add_argument("--account", default=None, help="accountNo override "
                     "(default: first account from GET /accounts)")
    ap.add_argument("--label", default="dnse", help="display name / filename tag")
    ap.add_argument("--days", type=int, default=90, help="order history lookback")
    ap.add_argument("--out", default=None, help="output HTML path")
    ap.add_argument("--demo", action="store_true", help="use synthetic data, no API calls")
    args = ap.parse_args()

    snapshot = demo_portfolio() if args.demo else \
        fetch_portfolio(args.creds, args.account, args.days)

    history_path = os.path.join(DATA_DIR, f"nav_history_{args.label}.csv")
    if args.demo:
        # demo mode: synthesize a short history so the chart has something to draw
        today = date.today()
        nav_history = [{"date": (today - timedelta(days=n)).isoformat(),
                        "nav": snapshot["nav"] * (1 + 0.004 * (5 - n))}
                       for n in range(5, -1, -1)]
    else:
        nav_history = update_nav_history(history_path, snapshot)

    out_path = args.out or os.path.join(OUTPUT_DIR, f"dashboard_{args.label}.html")
    render_html(args.label, snapshot, nav_history, out_path)
    print(f"Dashboard written to {out_path}")


if __name__ == "__main__":
    main()
