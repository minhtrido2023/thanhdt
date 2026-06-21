# -*- coding: utf-8 -*-
"""
build_comparison_v2_v34b.py
============================
So sánh toàn diện v2 (Ngũ Hành Tinh Tế) vs v3.4b (Tam Quan Định Tâm)
Output: vnindex_comparison_v2_vs_v34b.html
"""
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd

WORKDIR = os.environ.get("STATE_WORKDIR",
          r"/home/trido/thanhdt/WorkingClaude")

STATE_NAMES  = {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}
STATE_ALLOC  = {1:0.0, 2:0.20, 3:0.70, 4:1.00, 5:1.30}
STATE_COLOR  = {1:"#dc2626", 2:"#f97316", 3:"#9ca3af", 4:"#16a34a", 5:"#7c3aed"}
STATE_BG     = {1:"#2d0a0a", 2:"#2d1500", 3:"#1a1f2e", 4:"#0a2d1a", 5:"#1a0a2d"}

# ── Load data ──────────────────────────────────────────────────────────────────
vni = pd.read_csv(os.path.join(WORKDIR, "data/VNINDEX.csv"))
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
vni["ret"] = vni["Close"].pct_change()

v2 = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_history.csv"))
v2["time"] = pd.to_datetime(v2["time"])
v2 = v2.sort_values("time").reset_index(drop=True)

v34b = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_4b_full_history.csv"))
v34b["time"] = pd.to_datetime(v34b["time"])
v34b = v34b.sort_values("time").reset_index(drop=True)

# ── Backtest engine ────────────────────────────────────────────────────────────
def backtest(states_df, start="2000-01-01", end="2099-01-01", tc=0.001, deposit=0.06, borrow=0.10):
    df = vni.merge(states_df[["time", "state"]], on="time", how="inner")
    df = df[(df["time"] >= start) & (df["time"] <= end)].copy().reset_index(drop=True)
    if len(df) < 5:
        return None
    nav = 1.0; navs = []; w_prev = STATE_ALLOC[int(df["state"].iloc[0])]
    for i in range(len(df)):
        w   = STATE_ALLOC[int(df["state"].iloc[i])]
        ret = df["ret"].iloc[i] if not np.isnan(df["ret"].iloc[i]) else 0
        idle = max(0, 1 - w)
        lev  = max(0, w - 1)
        tc_cost = abs(w - w_prev) * tc
        sessions_yr = 252
        nav *= (1 + w * ret + idle * deposit/sessions_yr - lev * borrow/sessions_yr - tc_cost)
        navs.append(nav); w_prev = w
    navs = np.array(navs)
    dates = pd.to_datetime(df["time"].values)
    yr = max((dates[-1] - dates[0]).days / 365.25, 0.01)
    cagr = (navs[-1] ** (1/yr) - 1) * 100
    rets = np.diff(navs) / navs[:-1]
    sr   = rets.mean() / rets.std() * np.sqrt(252) if rets.std() > 0 else 0
    peak = np.maximum.accumulate(navs)
    dd   = navs / peak - 1
    maxdd  = dd.min() * 100
    calmar = cagr / abs(maxdd) if maxdd != 0 else 0
    # Sortino
    neg = rets[rets < 0]
    sortino = rets.mean() / neg.std() * np.sqrt(252) if len(neg) > 0 and neg.std() > 0 else 0
    # MAR / Ulcer
    ulcer = np.sqrt((dd**2).mean()) * 100
    wealth = navs[-1]
    n_trans = int((np.diff(df["state"].values) != 0).sum())
    seg_lens = []
    i = 0; sv = df["state"].values
    while i < len(sv):
        j = i + 1
        while j < len(sv) and sv[j] == sv[i]: j += 1
        seg_lens.append(j - i); i = j
    med_stay = float(np.median(seg_lens))
    # annual
    df2 = df.copy(); df2["nav"] = navs
    annual = {}
    for yr_ in sorted(df2["time"].dt.year.unique()):
        sub = df2[df2["time"].dt.year == yr_]
        if len(sub) < 2: continue
        n0 = sub["nav"].iloc[0]; n1 = sub["nav"].iloc[-1]
        # BH
        c0 = vni[vni["time"].dt.year == yr_]["Close"]
        if len(c0) >= 2:
            bh = (c0.iloc[-1] / c0.iloc[0] - 1) * 100
        else:
            bh = np.nan
        annual[int(yr_)] = {
            "sys": (n1/n0 - 1)*100,
            "bh":  bh
        }
    return {
        "cagr": cagr, "maxdd": maxdd, "sharpe": sr, "sortino": sortino,
        "calmar": calmar, "ulcer": ulcer, "wealth": wealth,
        "n_trans": n_trans, "med_stay": med_stay, "annual": annual,
        "navs": navs.tolist(), "dates": [str(d.date()) for d in dates]
    }

# ── Transitions extractor ──────────────────────────────────────────────────────
def get_transitions(states_df):
    sv = states_df["state"].values.astype(int)
    tv = states_df["time"].values
    rows = []
    i = 0
    while i < len(sv):
        j = i + 1
        while j < len(sv) and sv[j] == sv[i]: j += 1
        if i > 0:
            rows.append({
                "date": str(pd.Timestamp(tv[i]).date()),
                "from": int(sv[i-1]),
                "to":   int(sv[i]),
                "dur":  j - i,
            })
        i = j
    return rows

# ── State distribution ─────────────────────────────────────────────────────────
def state_pct(states_df, start=None):
    sv = states_df
    if start:
        sv = sv[sv["time"] >= start]
    total = len(sv)
    return {s: (sv["state"] == s).sum() / total * 100 for s in range(1, 6)}

# ── Compute everything ─────────────────────────────────────────────────────────
print("Computing backtests...")

bt_v2_full   = backtest(v2,   "2007-01-01")
bt_v2_2011   = backtest(v2,   "2011-01-01")
bt_v2_oos    = backtest(v2,   "2020-01-01")
bt_v2_24     = backtest(v2,   "2024-01-01")

bt_v34_full  = backtest(v34b, "2000-07-28")
bt_v34_2011  = backtest(v34b, "2011-01-01")
bt_v34_oos   = backtest(v34b, "2020-01-01")
bt_v34_24    = backtest(v34b, "2024-01-01")

# Comparable periods (both start 2007 and 2011)
bt_v2_cmp    = backtest(v2,   "2007-01-01")
bt_v34_cmp   = backtest(v34b, "2007-01-01")

tr_v2   = get_transitions(v2)
tr_v34b = get_transitions(v34b)

dist_v2   = state_pct(v2)
dist_v34b = state_pct(v34b)
dist_v2_11   = state_pct(v2,   "2011-01-01")
dist_v34b_11 = state_pct(v34b, "2011-01-01")

# Current state
cur_v2   = int(v2["state"].iloc[-1])
cur_v34b = int(v34b["state"].iloc[-1])
cur_date = str(v34b["time"].iloc[-1].date())
cur_vni  = float(vni["Close"].iloc[-1]) if not vni.empty else 0

print(f"v2   current: {STATE_NAMES[cur_v2]} | date={cur_date}")
print(f"v34b current: {STATE_NAMES[cur_v34b]} | date={cur_date}")

# ── Chart data ─────────────────────────────────────────────────────────────────
# NAV curves for chart (from 2007)
nav_v2   = bt_v2_full
nav_v34b = bt_v34_cmp   # from 2007 for comparable chart

# ── Helper functions ───────────────────────────────────────────────────────────
def delta_class(val, rev=False):
    """CSS class for positive/negative delta"""
    if rev:
        return "pos" if val < 0 else ("neg" if val > 0 else "neu")
    return "pos" if val > 0 else ("neg" if val < 0 else "neu")

def fmt_delta(val, fmt=".2f", unit="%", rev=False):
    sign = "+" if val > 0 else ""
    color = "#86efac" if (val > 0 and not rev) or (val < 0 and rev) else "#fca5a5" if (val < 0 and not rev) or (val > 0 and rev) else "#94a3b8"
    return f'<span style="color:{color}">{sign}{val:{fmt}}{unit}</span>'

def metric_row(label, v2_val, v34b_val, fmt=".2f", unit="%", rev=False, note=""):
    delta = v34b_val - v2_val
    note_html = f'<span style="color:#64748b;font-size:10px"> {note}</span>' if note else ""
    return f"""
    <tr>
      <td style="color:#94a3b8;font-size:12px">{label}{note_html}</td>
      <td style="text-align:center;font-size:14px;font-weight:700;color:#e2e8f0">{v2_val:{fmt}}{unit}</td>
      <td style="text-align:center;font-size:14px;font-weight:700;color:#e2e8f0">{v34b_val:{fmt}}{unit}</td>
      <td style="text-align:center;font-size:13px">{fmt_delta(delta, fmt, unit, rev)}</td>
    </tr>"""

# ── Annual comparison table ────────────────────────────────────────────────────
def annual_rows(bt_v2, bt_v34b):
    years = sorted(set(list(bt_v2["annual"].keys()) + list(bt_v34b["annual"].keys())))
    rows = []
    for yr in years:
        a2   = bt_v2.get("annual", {}).get(yr, {})
        a34b = bt_v34b.get("annual", {}).get(yr, {})
        sys2  = a2.get("sys", None)
        sys34 = a34b.get("sys", None)
        bh    = a2.get("bh", a34b.get("bh", None))
        def fmt_cell(v, bh_v):
            if v is None: return '<td style="text-align:right;color:#4a5568">—</td>'
            color = "#86efac" if v > 0 else "#fca5a5" if v < 0 else "#94a3b8"
            vs_bh = v - bh_v if bh_v is not None else 0
            arrow = "▲" if vs_bh > 0 else "▼"
            arr_c = "#86efac" if vs_bh > 0 else "#fca5a5"
            return f'<td style="text-align:right;color:{color};font-weight:700">{v:+.1f}% <small style="color:{arr_c}">{arrow}{abs(vs_bh):.1f}pp</small></td>'
        bh_html = f'<td style="text-align:right;color:#64748b">{bh:+.1f}%</td>' if bh is not None else '<td>—</td>'
        delta_html = ""
        if sys2 is not None and sys34 is not None:
            d = sys34 - sys2
            delta_c = "#86efac" if d > 0 else "#fca5a5"
            delta_html = f'<td style="text-align:right;color:{delta_c};font-weight:700">{d:+.1f}pp</td>'
        else:
            delta_html = '<td style="color:#4a5568">—</td>'
        rows.append(f'<tr><td style="color:#64748b">{yr}</td>{fmt_cell(sys2,bh)}{fmt_cell(sys34,bh)}{bh_html}{delta_html}</tr>')
    return "\n".join(rows)

# ── Transition rows ────────────────────────────────────────────────────────────
def trans_rows(trs):
    rows = []
    for i, t in enumerate(trs):
        f  = t["from"]; to = t["to"]
        fc = STATE_COLOR[f]; tc_ = STATE_COLOR[to]
        arrow = "▼" if to < f else "▲" if to > f else "="
        arrow_c = "#fca5a5" if to < f else "#86efac" if to > f else "#94a3b8"
        rows.append(f"""
        <tr>
          <td style="color:#64748b">{i+1}</td>
          <td style="color:#e2e8f0">{t['date']}</td>
          <td style="color:{fc};font-weight:700">{STATE_NAMES[f]}</td>
          <td style="color:{arrow_c};font-size:16px;text-align:center">{arrow}</td>
          <td style="color:{tc_};font-weight:700">{STATE_NAMES[to]}</td>
          <td style="color:#94a3b8;text-align:right">{t['dur']}d</td>
        </tr>""")
    return "\n".join(rows)

# ── JSON for charts ────────────────────────────────────────────────────────────
def series_json(bt, start="2007-01-01"):
    if bt is None: return "[]", "[]"
    d = bt["dates"]; n = bt["navs"]
    out_d, out_n = [], []
    for di, ni in zip(d, n):
        if di >= start:
            out_d.append(di); out_n.append(round(ni, 4))
    return json.dumps(out_d), json.dumps(out_n)

dates_v2_js,   navs_v2_js   = series_json(bt_v2_cmp,   "2007-01-01")
dates_v34b_js, navs_v34b_js = series_json(bt_v34_cmp,  "2007-01-01")

# BH NAV series
vni_c = vni[vni["time"] >= "2007-01-01"].copy()
bh_navs = (vni_c["Close"] / vni_c["Close"].iloc[0]).tolist()
bh_dates = [str(d.date()) for d in vni_c["time"]]
bh_dates_js = json.dumps(bh_dates)
bh_navs_js  = json.dumps([round(x,4) for x in bh_navs])

# ── Build HTML ─────────────────────────────────────────────────────────────────
print("Building HTML...")

def sc(color, text): return f'<span style="color:{color};font-weight:700">{text}</span>'

# State dist comparison
def dist_bar(dist, name):
    rows = []
    for s in [1,2,3,4,5]:
        pct = dist[s]
        rows.append(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
          <div style="width:72px;font-size:11px;color:{STATE_COLOR[s]};font-weight:700">{STATE_NAMES[s]}</div>
          <div style="flex:1;height:14px;background:#0f172a;border-radius:4px;overflow:hidden">
            <div style="width:{pct:.1f}%;height:100%;background:{STATE_COLOR[s]};opacity:0.8"></div>
          </div>
          <div style="width:44px;text-align:right;font-size:11px;color:#94a3b8">{pct:.1f}%</div>
        </div>""")
    return "\n".join(rows)

html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>So sánh v2 vs v3.4b · VNINDEX 5-State</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* {{ box-sizing:border-box;margin:0;padding:0 }}
body {{ background:#0a0f1e;color:#e2e8f0;font-family:'Segoe UI',sans-serif;padding:20px }}
h1 {{ font-size:20px;color:#f8fafc;margin-bottom:4px }}
h2 {{ font-size:15px;color:#94a3b8;margin:20px 0 10px }}
.subtitle {{ color:#64748b;font-size:13px;margin-bottom:16px }}
.grid2 {{ display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px }}
.card {{ background:#1e293b;border-radius:10px;padding:16px;border:1px solid #334155 }}
.card-head {{ font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px }}
.big-num {{ font-size:28px;font-weight:800 }}
.metric-table {{ width:100%;border-collapse:collapse }}
.metric-table th {{ background:#0f172a;color:#64748b;font-size:10px;font-weight:700;
                    text-transform:uppercase;letter-spacing:.5px;padding:7px 8px;
                    border-bottom:1px solid #334155 }}
.metric-table td {{ padding:7px 8px;border-bottom:1px solid #1a2035 }}
.metric-table tr:last-child td {{ border-bottom:none }}
.metric-table tr:hover td {{ background:rgba(96,165,250,0.06) }}
.trans-table {{ width:100%;border-collapse:collapse;font-size:12px }}
.trans-table th {{ background:#0f172a;color:#64748b;font-size:10px;font-weight:700;
                   text-transform:uppercase;letter-spacing:.5px;padding:6px 8px;
                   position:sticky;top:0;z-index:5;border-bottom:1px solid #334155 }}
.trans-table td {{ padding:5px 8px;border-bottom:1px solid #131a2a }}
.trans-table tr:hover td {{ background:rgba(96,165,250,0.06) }}
.badge {{ display:inline-block;padding:2px 10px;border-radius:6px;font-size:11px;font-weight:700 }}
.badge-live {{ background:#16a34a;color:#fff }}
.badge-next {{ background:#7c3aed;color:#fff }}
canvas {{ max-height:300px }}
.tab-wrap {{ display:flex;gap:6px;margin-bottom:14px }}
.tab {{ background:#1e293b;border:1px solid #334155;color:#94a3b8;
         padding:5px 14px;border-radius:6px;cursor:pointer;font-size:12px }}
.tab.active {{ border-color:#60a5fa;color:#60a5fa;background:#1e3a5f }}
.t-pane {{ display:none }}
.t-pane.active {{ display:block }}
.scroll-box {{ max-height:400px;overflow-y:auto;border-radius:8px;border:1px solid #334155 }}
.annual-table {{ width:100%;border-collapse:collapse;font-size:12px }}
.annual-table th {{ background:#0f172a;color:#64748b;font-size:10px;font-weight:700;
                    text-transform:uppercase;letter-spacing:.5px;padding:7px 8px;
                    border-bottom:1px solid #334155 }}
.annual-table td {{ padding:6px 8px;border-bottom:1px solid #131a2a }}
</style>
</head>
<body>

<h1>📊 So sánh: v2 Ngũ Hành Tinh Tế vs v3.4b Tam Quan Định Tâm</h1>
<p class="subtitle">VNINDEX 5-State Market Timing · Cập nhật: {cur_date} · Data: 2000–2026</p>

<!-- Current state banner -->
<div style="background:linear-gradient(90deg,#1e293b,#0f172a);border:1px solid #334155;border-radius:10px;
            padding:14px 20px;margin-bottom:20px;display:flex;align-items:center;gap:24px;flex-wrap:wrap">
  <div>
    <div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:.8px;margin-bottom:4px">
      v2 <span class="badge badge-live">LIVE BQ</span>
    </div>
    <div style="font-size:26px;font-weight:800;color:{STATE_COLOR[cur_v2]}">{STATE_NAMES[cur_v2]}</div>
    <div style="font-size:11px;color:#64748b;margin-top:2px">alloc = {STATE_ALLOC[cur_v2]*100:.0f}%</div>
  </div>
  <div style="border-left:1px solid #334155;padding-left:20px">
    <div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:.8px;margin-bottom:4px">
      v3.4b <span class="badge badge-next">STAGING</span>
    </div>
    <div style="font-size:26px;font-weight:800;color:{STATE_COLOR[cur_v34b]}">{STATE_NAMES[cur_v34b]}</div>
    <div style="font-size:11px;color:#64748b;margin-top:2px">alloc = {STATE_ALLOC[cur_v34b]*100:.0f}%</div>
  </div>
  <div style="border-left:1px solid #334155;padding-left:20px">
    <div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:.8px;margin-bottom:4px">VNINDEX</div>
    <div style="font-size:26px;font-weight:800;color:#e2e8f0">{cur_vni:,.1f}</div>
  </div>
  <div style="border-left:1px solid #334155;padding-left:20px">
    <div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:.8px;margin-bottom:4px">
      Đồng thuận
    </div>
    <div style="font-size:18px;font-weight:800;color:{'#86efac' if cur_v2==cur_v34b else '#fca5a5'}">
      {'✅ KHỚP' if cur_v2==cur_v34b else f'⚠️ KHÁC ({STATE_NAMES[cur_v2]} vs {STATE_NAMES[cur_v34b]})'}
    </div>
  </div>
</div>

<!-- NAV chart -->
<div class="card" style="margin-bottom:20px">
  <div class="card-head">NAV chart — từ 2007 (so sánh period chung · TC=0.1%/side)</div>
  <canvas id="navChart"></canvas>
</div>

<!-- Performance comparison: multiple periods -->
<h2>⚡ So sánh hiệu suất</h2>

<div class="tab-wrap">
  <button class="tab active" onclick="showTab('t-cmp')">So sánh từ 2007</button>
  <button class="tab" onclick="showTab('t-2011')">Từ 2011</button>
  <button class="tab" onclick="showTab('t-oos')">OOS 2020+</button>
  <button class="tab" onclick="showTab('t-2024')">2024+</button>
  <button class="tab" onclick="showTab('t-annual')">Theo năm</button>
</div>

<div id="t-cmp" class="t-pane active">
<div style="font-size:11px;color:#64748b;margin-bottom:8px">⚠️ v3.4b bắt đầu từ 2000, v2 từ 2007. Period chung = 2007–2026.</div>
<table class="metric-table">
  <thead><tr><th>Chỉ số</th><th style="text-align:center;color:#60a5fa">v2 (2007+)</th><th style="text-align:center;color:#a78bfa">v3.4b (2007+)</th><th style="text-align:center">Δ v3.4b−v2</th></tr></thead>
  <tbody>
    {metric_row("CAGR", bt_v2_cmp["cagr"], bt_v34_cmp["cagr"])}
    {metric_row("MaxDD", bt_v2_cmp["maxdd"], bt_v34_cmp["maxdd"], rev=True)}
    {metric_row("Sharpe", bt_v2_cmp["sharpe"], bt_v34_cmp["sharpe"], unit="")}
    {metric_row("Sortino", bt_v2_cmp["sortino"], bt_v34_cmp["sortino"], unit="")}
    {metric_row("Calmar", bt_v2_cmp["calmar"], bt_v34_cmp["calmar"], unit="")}
    {metric_row("Wealth", bt_v2_cmp["wealth"], bt_v34_cmp["wealth"], unit="x")}
    {metric_row("Ulcer Index", bt_v2_cmp["ulcer"], bt_v34_cmp["ulcer"], rev=True)}
    {metric_row("Transitions", bt_v2_cmp["n_trans"], bt_v34_cmp["n_trans"], fmt=".0f", unit="", note="(nhiều hơn = phức tạp hơn)")}
    {metric_row("Median Stay", bt_v2_cmp["med_stay"], bt_v34_cmp["med_stay"], fmt=".1f", unit="d")}
  </tbody>
</table>
</div>

<div id="t-2011" class="t-pane">
<div style="font-size:11px;color:#64748b;margin-bottom:8px">Canonical benchmark period: 2011–2026.</div>
<table class="metric-table">
  <thead><tr><th>Chỉ số</th><th style="text-align:center;color:#60a5fa">v2 (2011+)</th><th style="text-align:center;color:#a78bfa">v3.4b (2011+)</th><th style="text-align:center">Δ v3.4b−v2</th></tr></thead>
  <tbody>
    {metric_row("CAGR", bt_v2_2011["cagr"], bt_v34_2011["cagr"])}
    {metric_row("MaxDD", bt_v2_2011["maxdd"], bt_v34_2011["maxdd"], rev=True)}
    {metric_row("Sharpe", bt_v2_2011["sharpe"], bt_v34_2011["sharpe"], unit="")}
    {metric_row("Sortino", bt_v2_2011["sortino"], bt_v34_2011["sortino"], unit="")}
    {metric_row("Calmar", bt_v2_2011["calmar"], bt_v34_2011["calmar"], unit="")}
    {metric_row("Wealth", bt_v2_2011["wealth"], bt_v34_2011["wealth"], unit="x")}
    {metric_row("Ulcer Index", bt_v2_2011["ulcer"], bt_v34_2011["ulcer"], rev=True)}
    {metric_row("Transitions", bt_v2_2011["n_trans"], bt_v34_2011["n_trans"], fmt=".0f", unit="")}
    {metric_row("Median Stay", bt_v2_2011["med_stay"], bt_v34_2011["med_stay"], fmt=".1f", unit="d")}
  </tbody>
</table>
</div>

<div id="t-oos" class="t-pane">
<div style="font-size:11px;color:#64748b;margin-bottom:8px">OOS (Out-of-Sample): 2020–2026.</div>
<table class="metric-table">
  <thead><tr><th>Chỉ số</th><th style="text-align:center;color:#60a5fa">v2 OOS</th><th style="text-align:center;color:#a78bfa">v3.4b OOS</th><th style="text-align:center">Δ</th></tr></thead>
  <tbody>
    {metric_row("CAGR", bt_v2_oos["cagr"], bt_v34_oos["cagr"])}
    {metric_row("MaxDD", bt_v2_oos["maxdd"], bt_v34_oos["maxdd"], rev=True)}
    {metric_row("Sharpe", bt_v2_oos["sharpe"], bt_v34_oos["sharpe"], unit="")}
    {metric_row("Calmar", bt_v2_oos["calmar"], bt_v34_oos["calmar"], unit="")}
    {metric_row("Wealth", bt_v2_oos["wealth"], bt_v34_oos["wealth"], unit="x")}
    {metric_row("Transitions", bt_v2_oos["n_trans"], bt_v34_oos["n_trans"], fmt=".0f", unit="")}
  </tbody>
</table>
</div>

<div id="t-2024" class="t-pane">
<div style="font-size:11px;color:#64748b;margin-bottom:8px">2024–2026 (recent regime).</div>
<table class="metric-table">
  <thead><tr><th>Chỉ số</th><th style="text-align:center;color:#60a5fa">v2 2024+</th><th style="text-align:center;color:#a78bfa">v3.4b 2024+</th><th style="text-align:center">Δ</th></tr></thead>
  <tbody>
    {metric_row("CAGR", bt_v2_24["cagr"], bt_v34_24["cagr"])}
    {metric_row("MaxDD", bt_v2_24["maxdd"], bt_v34_24["maxdd"], rev=True)}
    {metric_row("Sharpe", bt_v2_24["sharpe"], bt_v34_24["sharpe"], unit="")}
    {metric_row("Calmar", bt_v2_24["calmar"], bt_v34_24["calmar"], unit="")}
    {metric_row("Wealth", bt_v2_24["wealth"], bt_v34_24["wealth"], unit="x")}
    {metric_row("Transitions", bt_v2_24["n_trans"], bt_v34_24["n_trans"], fmt=".0f", unit="")}
  </tbody>
</table>
</div>

<div id="t-annual" class="t-pane">
<div class="scroll-box">
<table class="annual-table">
  <thead><tr>
    <th>Năm</th>
    <th style="text-align:right">v2 sys</th>
    <th style="text-align:right">v3.4b sys</th>
    <th style="text-align:right">B&H VNI</th>
    <th style="text-align:right">Δ (v34b−v2)</th>
  </tr></thead>
  <tbody>
    {annual_rows(bt_v2_cmp, bt_v34_cmp)}
  </tbody>
</table>
</div>
</div>

<!-- State distribution -->
<h2>📊 Phân bổ trạng thái</h2>
<div class="grid2">
  <div class="card">
    <div class="card-head">v2 · Ngũ Hành Tinh Tế <span style="color:#64748b">(2007–2026 · {len(v2)} phiên)</span></div>
    {dist_bar(dist_v2, "v2")}
    <div style="margin-top:10px;font-size:10px;color:#64748b">Từ 2011:</div>
    {dist_bar(dist_v2_11, "v2_11")}
  </div>
  <div class="card">
    <div class="card-head">v3.4b · Tam Quan Định Tâm <span style="color:#64748b">(2000–2026 · {len(v34b)} phiên)</span></div>
    {dist_bar(dist_v34b, "v34b")}
    <div style="margin-top:10px;font-size:10px;color:#64748b">Từ 2011:</div>
    {dist_bar(dist_v34b_11, "v34b_11")}
  </div>
</div>

<!-- Transition tables side by side -->
<h2>🔄 Lịch sử chuyển đổi</h2>
<div class="grid2">
  <div>
    <div style="font-size:12px;color:#60a5fa;font-weight:700;margin-bottom:8px">
      v2 · {len(tr_v2)} lần chuyển đổi (2007–2026)
    </div>
    <div class="scroll-box">
    <table class="trans-table">
      <thead><tr><th>#</th><th>Ngày</th><th>Từ</th><th style="text-align:center"></th><th>Sang</th><th style="text-align:right">Durée</th></tr></thead>
      <tbody>{trans_rows(tr_v2)}</tbody>
    </table>
    </div>
  </div>
  <div>
    <div style="font-size:12px;color:#a78bfa;font-weight:700;margin-bottom:8px">
      v3.4b · {len(tr_v34b)} lần chuyển đổi (2000–2026)
    </div>
    <div class="scroll-box">
    <table class="trans-table">
      <thead><tr><th>#</th><th>Ngày</th><th>Từ</th><th style="text-align:center"></th><th>Sang</th><th style="text-align:right">Durée</th></tr></thead>
      <tbody>{trans_rows(tr_v34b)}</tbody>
    </table>
    </div>
  </div>
</div>

<!-- Architecture notes -->
<h2>🏛 Kiến trúc & Vai trò</h2>
<div class="grid2">
  <div class="card">
    <div style="font-size:13px;font-weight:700;color:#60a5fa;margin-bottom:10px">
      v2 · Ngũ Hành Tinh Tế <span class="badge badge-live">LIVE BQ</span>
    </div>
    <div style="font-size:12px;color:#94a3b8;line-height:1.8">
      <b style="color:#e2e8f0">Input:</b> 7 factors (P3M/P1M/MA200/RSI/MACD/CMF/Breadth)<br>
      <b style="color:#e2e8f0">Pipeline:</b> EMA(α=0.40) → mode(15) → min_stay(7)<br>
      <b style="color:#e2e8f0">Gate:</b> BearDvg RESET=True, dur=60, floor=CRISIS<br>
      <b style="color:#e2e8f0">Start:</b> 2007 (RANK_START bỏ bong bóng 2007)<br>
      <b style="color:#e2e8f0">BQ table:</b> <code style="background:#0f172a;color:#86efac;padding:1px 6px;border-radius:3px">tav2_bq.vnindex_5state</code><br>
      <b style="color:#e2e8f0">Feed:</b> V12+LIVE, backtest_holistic, paper-trade<br>
      <b style="color:#e2e8f0">Transitions:</b> {len(tr_v2)} (2007–2026) · median stay {bt_v2_cmp["med_stay"]:.1f}d
    </div>
  </div>
  <div class="card">
    <div style="font-size:13px;font-weight:700;color:#a78bfa;margin-bottom:10px">
      v3.4b · Tam Quan Định Tâm <span class="badge badge-next">STAGING</span>
    </div>
    <div style="font-size:12px;color:#94a3b8;line-height:1.8">
      <b style="color:#e2e8f0">Input:</b> v3.1 (US overlay) + BTC bull bypass + RSI gate<br>
      <b style="color:#e2e8f0">BTC:</b> ret_6m>15% AND VNI>MA200 → bypass US override<br>
      <b style="color:#e2e8f0">Conc filter:</b> concentration ≤ 0.55 (broad market only)<br>
      <b style="color:#e2e8f0">Start:</b> 2000 (full history + US data)<br>
      <b style="color:#e2e8f0">BQ table:</b> <code style="background:#0f172a;color:#a78bfa;padding:1px 6px;border-radius:3px">tav2_bq.vnindex_5state_tam_quan_v34b_clean</code><br>
      <b style="color:#e2e8f0">Feed:</b> V121_ENS, run_5systems_prodspec.py<br>
      <b style="color:#e2e8f0">Transitions:</b> {len(tr_v34b)} (2000–2026) · median stay {bt_v34_cmp["med_stay"]:.1f}d
    </div>
  </div>
</div>

<div style="background:#1e293b;border:1px solid #f59e0b;border-radius:8px;padding:12px 16px;margin-top:16px;font-size:12px;color:#fbbf24">
  ⚠️ <b>Lưu ý quan trọng:</b> v3.4b standalone 2011+ CAGR <b>thấp hơn</b> v2 ({bt_v34_2011["cagr"]:.2f}% vs {bt_v2_2011["cagr"]:.2f}%).
  Nhưng v3.4b được thiết kế để kết hợp với V11/V121 không phải chạy standalone — cần integrated backtest (run_5systems_prodspec.py)
  để đánh giá thực sự, giống như v2g standalone +1.28pp nhưng integrated -2.40pp.
</div>

<script>
// Charts
const labels = {dates_v2_js};
const navV2   = {navs_v2_js};
const navV34b = {navs_v34b_js};
const bhDates = {bh_dates_js};
const bhNavs  = {bh_navs_js};

const ctx = document.getElementById('navChart').getContext('2d');
new Chart(ctx, {{
  type: 'line',
  data: {{
    labels: labels,
    datasets: [
      {{
        label: 'v2 Ngũ Hành Tinh Tế',
        data: navV2,
        borderColor: '#60a5fa',
        backgroundColor: 'rgba(96,165,250,0.05)',
        borderWidth: 2, pointRadius: 0, fill: false, tension: 0.1
      }},
      {{
        label: 'v3.4b Tam Quan Định Tâm',
        data: navV34b,
        borderColor: '#a78bfa',
        backgroundColor: 'rgba(167,139,250,0.05)',
        borderWidth: 2, pointRadius: 0, fill: false, tension: 0.1
      }},
      {{
        label: 'VNINDEX B&H',
        data: bhNavs,
        borderColor: '#4a5568',
        backgroundColor: 'transparent',
        borderWidth: 1.5, borderDash: [4,3], pointRadius: 0, fill: false, tension: 0
      }}
    ]
  }},
  options: {{
    responsive: true,
    interaction: {{ mode:'index', intersect: false }},
    plugins: {{
      legend: {{ labels: {{ color:'#94a3b8', font:{{ size:12 }} }} }},
      tooltip: {{ backgroundColor:'#1e293b', titleColor:'#94a3b8', bodyColor:'#e2e8f0' }}
    }},
    scales: {{
      x: {{ grid:{{ color:'#1a2035' }}, ticks:{{ color:'#4a5568', maxTicksLimit:10, font:{{ size:10 }} }} }},
      y: {{ grid:{{ color:'#1a2035' }}, ticks:{{ color:'#4a5568', font:{{ size:10 }},
              callback: v => v.toFixed(2)+'x' }} }}
    }}
  }}
}});

// Tabs
function showTab(id) {{
  document.querySelectorAll('.t-pane').forEach(e => e.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(e => e.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  event.target.classList.add('active');
}}
</script>
</body>
</html>"""

out_path = os.path.join(WORKDIR, "vnindex_comparison_v2_vs_v34b.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"\nSaved: {out_path}")
print(f"File size: {os.path.getsize(out_path):,} bytes")
