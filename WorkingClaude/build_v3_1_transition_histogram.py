# -*- coding: utf-8 -*-
"""
build_v3_1_transition_histogram.py
==================================
T+5 forward-return histogram for every Tam Quan v3.1 state transition.

"Success" rule:
  • UPGRADE   (BEAR→BULL etc.)  : success if return_5d > 0
  • DOWNGRADE (BULL→BEAR etc.)  : success if return_5d < 0
  • SAME-level transitions are ignored (none should occur)

Magnitude-weighted success (a 1-step move is graded against ±2% threshold,
a 2+ step move against ±4%) is reported alongside the strict-sign version.

Outputs:
  • vnindex_v3_1_transition_histogram.html  (interactive page with bins +
    a per-pair table + summary cards)
"""
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
ORDER = {"CRISIS":1,"BEAR":2,"NEUTRAL":3,"BULL":4,"EX-BULL":5}
FWD_DAYS = 5  # T+5 trading sessions

# ── Load ────────────────────────────────────────────────────────────────
print("Loading v3.1 state + close ...")
st = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_1_full_history.csv"))
st["time"] = pd.to_datetime(st["time"])
st = st.sort_values("time").reset_index(drop=True)

dr = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_dual_v3_full.csv"))
dr["time"] = pd.to_datetime(dr["time"])
df = st.merge(dr[["time","Close"]], on="time", how="left").reset_index(drop=True)

n = len(df); close = df["Close"].values; state = df["state"].values.astype(int)
print(f"  {n} rows | {df['time'].iloc[0].date()} → {df['time'].iloc[-1].date()}")

# ── Collect transitions with T+5 fwd return ─────────────────────────────
trans = []
prev = state[0]
for i in range(1, n):
    s = state[i]
    if s != prev:
        if i + FWD_DAYS < n:
            r5 = close[i+FWD_DAYS]/close[i] - 1
        else:
            r5 = None
        f_name, t_name = STATE_NAMES[prev], STATE_NAMES[s]
        step = ORDER[t_name] - ORDER[f_name]
        direction = "up" if step > 0 else ("down" if step < 0 else "same")
        trans.append({
            "date": df["time"].iloc[i],
            "from": f_name, "to": t_name, "step": step, "dir": direction,
            "close": float(close[i]), "r5": r5,
        })
        prev = s

trans = [t for t in trans if t["r5"] is not None]  # drop trailing
print(f"  {len(trans)} transitions with full T+5 lookahead")

# ── Strict-sign success: up→r5>0, down→r5<0 ─────────────────────────────
def strict_success(t):
    if t["dir"] == "up":   return t["r5"] > 0
    if t["dir"] == "down": return t["r5"] < 0
    return None

# Magnitude-weighted: 1-step ±2%, 2+step ±4%
def graded_success(t):
    thr = 0.02 if abs(t["step"]) == 1 else 0.04
    if t["dir"] == "up":   return t["r5"] >  thr
    if t["dir"] == "down": return t["r5"] < -thr
    return None

for t in trans:
    t["ok_strict"] = strict_success(t)
    t["ok_graded"] = graded_success(t)

# ── Overall stats ───────────────────────────────────────────────────────
def stats(rows):
    rs = np.array([t["r5"] for t in rows])
    if len(rs) == 0: return dict(n=0, mean=0, median=0, p25=0, p75=0, pos=0, win=0, win_g=0)
    return dict(
        n=len(rs), mean=rs.mean()*100, median=np.median(rs)*100,
        p25=np.percentile(rs,25)*100, p75=np.percentile(rs,75)*100,
        pos=(rs>0).mean()*100,
        win=np.mean([t["ok_strict"] for t in rows])*100,
        win_g=np.mean([t["ok_graded"] for t in rows])*100,
    )

all_s  = stats(trans)
up_s   = stats([t for t in trans if t["dir"]=="up"])
down_s = stats([t for t in trans if t["dir"]=="down"])

print(f"\nOverall (n={all_s['n']}): mean={all_s['mean']:+.2f}%, median={all_s['median']:+.2f}%, strict_win={all_s['win']:.1f}%, graded_win={all_s['win_g']:.1f}%")
print(f"Up   (n={up_s['n']}):  mean={up_s['mean']:+.2f}%, win={up_s['win']:.1f}%, graded={up_s['win_g']:.1f}%")
print(f"Down (n={down_s['n']}): mean={down_s['mean']:+.2f}%, win={down_s['win']:.1f}%, graded={down_s['win_g']:.1f}%")

# ── Per-pair stats ──────────────────────────────────────────────────────
pairs = {}
for t in trans:
    key = (t["from"], t["to"])
    pairs.setdefault(key, []).append(t)
pair_rows = []
for (f_n, t_n), rows in sorted(pairs.items(), key=lambda kv:(ORDER[kv[0][0]], ORDER[kv[0][1]])):
    rs = np.array([r["r5"] for r in rows])
    win_s = np.mean([r["ok_strict"] for r in rows])*100
    win_g = np.mean([r["ok_graded"] for r in rows])*100
    pair_rows.append(dict(
        f=f_n, t=t_n, step=ORDER[t_n]-ORDER[f_n],
        n=len(rs), mean=rs.mean()*100, median=np.median(rs)*100,
        win=win_s, win_g=win_g,
    ))

# ── Histogram bins ──────────────────────────────────────────────────────
# bins from -15% to +15% in 1% steps
BIN_EDGES = np.arange(-0.15, 0.151, 0.01)
BIN_LABELS = [f"{e*100:+.0f}%" for e in BIN_EDGES[:-1]]

def hist_for(rows):
    rs = np.array([t["r5"] for t in rows]) if rows else np.array([])
    counts, _ = np.histogram(np.clip(rs, BIN_EDGES[0], BIN_EDGES[-1]-1e-9), BIN_EDGES)
    return counts.tolist()

hist_all  = hist_for(trans)
hist_up   = hist_for([t for t in trans if t["dir"]=="up"])
hist_down = hist_for([t for t in trans if t["dir"]=="down"])

# Also: success-vs-fail per direction (strict)
hist_up_ok    = hist_for([t for t in trans if t["dir"]=="up"   and t["ok_strict"]])
hist_up_fail  = hist_for([t for t in trans if t["dir"]=="up"   and not t["ok_strict"]])
hist_down_ok  = hist_for([t for t in trans if t["dir"]=="down" and t["ok_strict"]])
hist_down_fail= hist_for([t for t in trans if t["dir"]=="down" and not t["ok_strict"]])

# ── HTML ────────────────────────────────────────────────────────────────
STATE_BG = {
    "CRISIS":  ("#7f1d1d","#fca5a5"),
    "BEAR":    ("#7c2d12","#fdba74"),
    "NEUTRAL": ("#1e293b","#94a3b8"),
    "BULL":    ("#14532d","#86efac"),
    "EX-BULL": ("#3b0764","#c4b5fd"),
}
def badge(s):
    bg,fg = STATE_BG.get(s,("#334155","#94a3b8"))
    return f'<span style="background:{bg};color:{fg};padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700;white-space:nowrap">{s}</span>'

# Pair table HTML
pair_tbody = []
for r in pair_rows:
    win_col = "#16a34a" if r["win"]>=60 else ("#eab308" if r["win"]>=45 else "#dc2626")
    wing_col= "#16a34a" if r["win_g"]>=50 else ("#eab308" if r["win_g"]>=30 else "#dc2626")
    mean_col= "#86efac" if r["mean"]>0 else "#fca5a5"
    med_col = "#86efac" if r["median"]>0 else "#fca5a5"
    step_arrow = "▲"*r["step"] if r["step"]>0 else "▼"*(-r["step"])
    pair_tbody.append(f'''<tr style="border-bottom:1px solid #334155">
      <td style="padding:6px 10px">{badge(r['f'])}</td>
      <td style="padding:6px 6px;text-align:center;color:#94a3b8">{step_arrow}</td>
      <td style="padding:6px 10px">{badge(r['t'])}</td>
      <td style="padding:6px 10px;text-align:right;color:#e2e8f0;font-weight:600">{r['n']}</td>
      <td style="padding:6px 10px;text-align:right;color:{mean_col};font-variant-numeric:tabular-nums">{r['mean']:+.2f}%</td>
      <td style="padding:6px 10px;text-align:right;color:{med_col};font-variant-numeric:tabular-nums">{r['median']:+.2f}%</td>
      <td style="padding:6px 10px;text-align:right;color:{win_col};font-weight:700">{r['win']:.0f}%</td>
      <td style="padding:6px 10px;text-align:right;color:{wing_col};font-weight:700">{r['win_g']:.0f}%</td>
    </tr>''')
pair_tbody = "\n".join(pair_tbody)

# Top winning + losing transitions (for verification)
def fmt_top(rows, n=12):
    rows = sorted(rows, key=lambda r: r["r5"], reverse=True)[:n]
    out = []
    for r in rows:
        col = "#86efac" if r["r5"]>0 else "#fca5a5"
        out.append(f'<tr><td style="padding:4px 8px;color:#94a3b8">{r["date"].strftime("%Y-%m-%d")}</td>'
                   f'<td style="padding:4px 8px">{badge(r["from"])}</td>'
                   f'<td style="padding:4px 8px">{badge(r["to"])}</td>'
                   f'<td style="padding:4px 8px;text-align:right;color:{col};font-weight:700;font-variant-numeric:tabular-nums">{r["r5"]*100:+.2f}%</td>'
                   f'<td style="padding:4px 8px;text-align:center">{"✓" if r["ok_strict"] else "✗"}</td></tr>')
    return "\n".join(out)

top_ups   = fmt_top([t for t in trans if t["dir"]=="up"],   12)
worst_ups = fmt_top(sorted([t for t in trans if t["dir"]=="up"],   key=lambda r:r["r5"])[:12], 12)
top_downs   = fmt_top(sorted([t for t in trans if t["dir"]=="down"], key=lambda r:r["r5"])[:12], 12)  # most-negative = best for down
worst_downs = fmt_top([t for t in trans if t["dir"]=="down"], 12)  # most-positive = bad for down

# JSON for charts
chart_data = dict(
    labels=BIN_LABELS,
    all=hist_all, up=hist_up, down=hist_down,
    up_ok=hist_up_ok, up_fail=hist_up_fail,
    down_ok=hist_down_ok, down_fail=hist_down_fail,
)

html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Tam Quan v3.1 · T+5 Transition Success Histogram</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* {{ box-sizing:border-box;margin:0;padding:0 }}
body {{ background:#0a0f1e;color:#e2e8f0;font-family:'Segoe UI',sans-serif;padding:20px }}
h1 {{ font-size:20px;color:#f8fafc;margin-bottom:4px }}
h2 {{ font-size:15px;color:#cbd5e1;margin:20px 0 10px }}
.subtitle {{ color:#64748b;font-size:13px;margin-bottom:16px }}
.staging-tag {{ background:#7c3aed;color:#fff;padding:2px 10px;border-radius:6px;font-size:11px;font-weight:700;margin-left:8px }}
.stats {{ display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px }}
.stat-card {{ background:#1e293b;border-radius:8px;padding:10px 16px;border:1px solid #334155;min-width:140px }}
.stat-card .num {{ font-size:22px;font-weight:800 }}
.stat-card .lbl {{ font-size:11px;color:#64748b }}
.grid {{ display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px }}
.panel {{ background:#0f172a;border:1px solid #334155;border-radius:8px;padding:14px }}
.panel h3 {{ font-size:13px;color:#cbd5e1;margin-bottom:8px }}
.panel .sub {{ font-size:11px;color:#64748b;margin-bottom:10px }}
.legend {{ background:#1e293b;border:1px solid #334155;border-radius:8px;padding:10px 14px;
           margin-bottom:14px;font-size:12px;color:#94a3b8 }}
.legend b {{ color:#e2e8f0 }}
.legend code {{ background:#0f172a;color:#86efac;padding:1px 6px;border-radius:4px;font-size:11px }}
table {{ width:100%;border-collapse:collapse;font-size:12px }}
thead th {{ background:#0f172a;color:#64748b;font-size:10px;font-weight:700;
            text-transform:uppercase;letter-spacing:.5px;padding:8px 6px;
            border-bottom:2px solid #334155;text-align:left }}
.table-wrap {{ overflow-x:auto;max-height:420px;overflow-y:auto;
               border-radius:8px;border:1px solid #334155;background:#0f172a }}
.small {{ font-size:11px;color:#64748b }}
canvas {{ background:#0a0f1e;border-radius:6px }}
</style>
</head>
<body>

<h1>📊 Tam Quan v3.1 · T+5 Transition Success Histogram<span class="staging-tag">STAGING</span></h1>
<p class="subtitle">{len(trans)} transitions có đủ {FWD_DAYS} phiên forward · {df['time'].iloc[0].year}–{df['time'].iloc[-1].year}
· Success = upgrade →&nbsp;r5&gt;0, downgrade →&nbsp;r5&lt;0</p>

<div class="stats">
  <div class="stat-card"><div class="num" style="color:#e2e8f0">{all_s['n']}</div><div class="lbl">Tổng transitions</div></div>
  <div class="stat-card"><div class="num" style="color:{'#86efac' if all_s['win']>=55 else '#fca5a5'}">{all_s['win']:.1f}%</div><div class="lbl">Strict win rate</div></div>
  <div class="stat-card"><div class="num" style="color:{'#86efac' if all_s['win_g']>=40 else '#fbbf24'}">{all_s['win_g']:.1f}%</div><div class="lbl">Graded win (±2/4%)</div></div>
  <div class="stat-card"><div class="num" style="color:{'#86efac' if all_s['mean']>0 else '#fca5a5'}">{all_s['mean']:+.2f}%</div><div class="lbl">Mean T+5 return</div></div>
  <div class="stat-card"><div class="num" style="color:{'#86efac' if all_s['median']>0 else '#fca5a5'}">{all_s['median']:+.2f}%</div><div class="lbl">Median T+5 return</div></div>
  <div class="stat-card"><div class="num" style="color:#16a34a">{up_s['n']}</div><div class="lbl">▲ Upgrade (win {up_s['win']:.0f}%)</div></div>
  <div class="stat-card"><div class="num" style="color:#dc2626">{down_s['n']}</div><div class="lbl">▼ Downgrade (win {down_s['win']:.0f}%)</div></div>
</div>

<div class="legend">
  <b>Đọc biểu đồ thế nào?</b>
  Mỗi histogram chia T+5 forward return của VNINDEX vào các bin 1% (từ −15% đến +15%).
  • <b>Strict win</b>: upgrade thắng nếu r5 &gt; 0; downgrade thắng nếu r5 &lt; 0 (bất kể độ lớn).
  • <b>Graded win</b>: yêu cầu độ lớn ≥ <code>2%</code> cho 1-step, <code>4%</code> cho 2+step — strict hơn, lọc nhiễu sát 0.
  • Cột <b>step</b> = số bậc state nhảy (▲▲ = +2 bậc như NEUTRAL→EX-BULL).
  Hệ thống "hợp lý" nếu UP có phân bố lệch phải (mean &gt; 0) và DOWN lệch trái (mean &lt; 0).
</div>

<h2>📈 Distribution by direction</h2>
<div class="grid">
  <div class="panel">
    <h3>Tất cả transitions <span class="small">(n={all_s['n']})</span></h3>
    <div class="sub">Mean {all_s['mean']:+.2f}% · Median {all_s['median']:+.2f}% · IQR [{all_s['p25']:+.2f}%, {all_s['p75']:+.2f}%]</div>
    <canvas id="chartAll" height="180"></canvas>
  </div>
  <div class="panel">
    <h3>▲ Upgrade vs ▼ Downgrade <span class="small">(stacked)</span></h3>
    <div class="sub">Upgrade mean {up_s['mean']:+.2f}% · Downgrade mean {down_s['mean']:+.2f}% — kỳ vọng đối nghịch nhau</div>
    <canvas id="chartUpDown" height="180"></canvas>
  </div>
  <div class="panel">
    <h3>▲ Upgrade: Win (xanh) vs Fail (đỏ)</h3>
    <div class="sub">Win = r5 &gt; 0 (n={sum(hist_up_ok)}) · Fail = r5 ≤ 0 (n={sum(hist_up_fail)})</div>
    <canvas id="chartUp" height="180"></canvas>
  </div>
  <div class="panel">
    <h3>▼ Downgrade: Win (xanh) vs Fail (đỏ)</h3>
    <div class="sub">Win = r5 &lt; 0 (n={sum(hist_down_ok)}) · Fail = r5 ≥ 0 (n={sum(hist_down_fail)})</div>
    <canvas id="chartDown" height="180"></canvas>
  </div>
</div>

<h2>🎯 Win rate theo từng cặp chuyển state</h2>
<div class="table-wrap">
<table>
<thead>
<tr>
  <th>Từ</th><th>Step</th><th>Sang</th>
  <th style="text-align:right">n</th>
  <th style="text-align:right">Mean r5</th>
  <th style="text-align:right">Median r5</th>
  <th style="text-align:right">Strict win</th>
  <th style="text-align:right">Graded win</th>
</tr>
</thead>
<tbody>
{pair_tbody}
</tbody>
</table>
</div>

<h2>🔍 Verification — best / worst transitions</h2>
<div class="grid">
  <div class="panel">
    <h3 style="color:#86efac">▲ Top 12 upgrade thành công nhất</h3>
    <table><thead><tr><th>Ngày</th><th>Từ</th><th>Sang</th><th style="text-align:right">r5</th><th style="text-align:center">OK</th></tr></thead>
    <tbody>{top_ups}</tbody></table>
  </div>
  <div class="panel">
    <h3 style="color:#fca5a5">▲ Top 12 upgrade thất bại tệ nhất</h3>
    <table><thead><tr><th>Ngày</th><th>Từ</th><th>Sang</th><th style="text-align:right">r5</th><th style="text-align:center">OK</th></tr></thead>
    <tbody>{worst_ups}</tbody></table>
  </div>
  <div class="panel">
    <h3 style="color:#86efac">▼ Top 12 downgrade thành công nhất</h3>
    <table><thead><tr><th>Ngày</th><th>Từ</th><th>Sang</th><th style="text-align:right">r5</th><th style="text-align:center">OK</th></tr></thead>
    <tbody>{top_downs}</tbody></table>
  </div>
  <div class="panel">
    <h3 style="color:#fca5a5">▼ Top 12 downgrade thất bại tệ nhất</h3>
    <table><thead><tr><th>Ngày</th><th>Từ</th><th>Sang</th><th style="text-align:right">r5</th><th style="text-align:center">OK</th></tr></thead>
    <tbody>{worst_downs}</tbody></table>
  </div>
</div>

<script>
const D = {json.dumps(chart_data)};
const baseOpt = {{
  responsive:true, maintainAspectRatio:false,
  plugins:{{ legend:{{ labels:{{ color:'#cbd5e1', font:{{size:11}} }} }} }},
  scales:{{
    x:{{ ticks:{{ color:'#64748b', font:{{size:9}}, autoSkip:true, maxTicksLimit:16 }}, grid:{{color:'#1e293b'}} }},
    y:{{ ticks:{{ color:'#64748b', font:{{size:10}} }}, grid:{{color:'#1e293b'}} }}
  }}
}};
function makeBar(id, datasets, stacked=false){{
  const opt = JSON.parse(JSON.stringify(baseOpt));
  if(stacked){{ opt.scales.x.stacked=true; opt.scales.y.stacked=true; }}
  new Chart(document.getElementById(id), {{
    type:'bar',
    data:{{ labels:D.labels, datasets:datasets }},
    options: opt
  }});
}}
makeBar('chartAll', [
  {{ label:'All transitions', data:D.all, backgroundColor:'#60a5fa', borderColor:'#3b82f6', borderWidth:1 }}
]);
makeBar('chartUpDown', [
  {{ label:'▲ Upgrade',   data:D.up,   backgroundColor:'rgba(34,197,94,0.65)',  borderColor:'#16a34a', borderWidth:1 }},
  {{ label:'▼ Downgrade', data:D.down, backgroundColor:'rgba(239,68,68,0.65)',  borderColor:'#dc2626', borderWidth:1 }}
], true);
makeBar('chartUp', [
  {{ label:'Win (r5>0)',  data:D.up_ok,   backgroundColor:'rgba(34,197,94,0.75)', borderColor:'#16a34a', borderWidth:1 }},
  {{ label:'Fail (r5≤0)', data:D.up_fail, backgroundColor:'rgba(239,68,68,0.75)', borderColor:'#dc2626', borderWidth:1 }}
], true);
makeBar('chartDown', [
  {{ label:'Win (r5<0)',  data:D.down_ok,   backgroundColor:'rgba(34,197,94,0.75)', borderColor:'#16a34a', borderWidth:1 }},
  {{ label:'Fail (r5≥0)', data:D.down_fail, backgroundColor:'rgba(239,68,68,0.75)', borderColor:'#dc2626', borderWidth:1 }}
], true);
</script>
</body>
</html>"""

out_path = os.path.join(WORKDIR, "vnindex_v3_1_transition_histogram.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"\n✓ Saved: {out_path}")
