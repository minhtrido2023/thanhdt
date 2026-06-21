# -*- coding: utf-8 -*-
"""
analyze_v3_4b_success_by_year.py
================================
Yearly success-rate analysis for v3.4b transition predictions.

For each year:
  • Count transitions (total / up / down)
  • Compute mean forward T+5/T+20/T+60 return
  • Compute "raw win rate" (up: r>0; down: r<0)
  • Compare vs **per-year base rate** (% positive weeks in VNI that year)
  • Compute **edge** = (system win rate) − (base rate)

Edge > 0 → system predicts better than chance for that year
Edge < 0 → system is anti-predictive for that year

Then aggregate by era to see trend.

Output: console table + HTML chart `vnindex_v3_4b_yearly_success.html`
"""
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
ORDER = {"CRISIS":1,"BEAR":2,"NEUTRAL":3,"BULL":4,"EX-BULL":5}

# ── Load ───────────────────────────────────────────────────────────────
st = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_4b_full_history.csv"))
st["time"] = pd.to_datetime(st["time"]); st = st.sort_values("time").reset_index(drop=True)
dr = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_dual_v3_full.csv"))
dr["time"] = pd.to_datetime(dr["time"])
df = st.merge(dr[["time","Close"]], on="time", how="left").reset_index(drop=True)
n = len(df); close = df["Close"].values; state = df["state"].values.astype(int)
print(f"Loaded {n} rows | {df['time'].iloc[0].date()} → {df['time'].iloc[-1].date()}")

# ── Compute per-year VNI base rate (% positive T+H returns) ────────────
def fwd_ret(i, h):
    if i+h >= n: return None
    return close[i+h]/close[i] - 1

# For each day in each year, compute T+H fwd return. Get % positive that year.
df["year"] = df["time"].dt.year
base_rate = {}
for yr in sorted(df["year"].unique()):
    idxs = df[df["year"]==yr].index
    base_rate[yr] = {}
    for h in [5, 20, 60]:
        rets = []
        for i in idxs:
            r = fwd_ret(i, h)
            if r is not None: rets.append(r)
        if rets:
            base_rate[yr][h] = dict(
                n=len(rets), mean=np.mean(rets)*100,
                pos=(np.array(rets)>0).mean()*100,
            )

# ── Collect transitions and grade them ─────────────────────────────────
trans = []
prev = state[0]
for i in range(1, n):
    if state[i] != prev:
        f_n, t_n = STATE_NAMES[prev], STATE_NAMES[state[i]]
        step = ORDER[t_n] - ORDER[f_n]
        rec = dict(
            date=df["time"].iloc[i], year=df["year"].iloc[i],
            from_=f_n, to=t_n, step=step, abs_step=abs(step),
            dir="up" if step>0 else "down",
        )
        for h in [5,20,60]:
            rec[f"r{h}"] = fwd_ret(i, h)
        trans.append(rec)
        prev = state[i]

trans_full = [t for t in trans if t["r60"] is not None]
print(f"\n{len(trans_full)} transitions with full T+60 lookahead")

# ── Aggregate by year ──────────────────────────────────────────────────
print("\n" + "="*100)
print(f"YEARLY ANALYSIS: v3.4b transitions vs VNINDEX base rate")
print("="*100)
print(f"{'Year':<6}{'n_tr':>5}{'up':>4}{'dn':>4}  "
      f"{'UP T+20':<24}{'DOWN T+20':<24}{'NET edge':>10}")
print(f"{'':<6}{'':>5}{'':>4}{'':>4}  "
      f"{'win%(base) edge mean%':<24}{'win%(base) edge mean%':<24}")
print("-"*100)

yearly_stats = []
for yr in sorted({t["year"] for t in trans_full}):
    yr_trans = [t for t in trans_full if t["year"] == yr]
    if not yr_trans or yr not in base_rate or 20 not in base_rate[yr]: continue

    n_up = sum(1 for t in yr_trans if t["dir"]=="up")
    n_dn = sum(1 for t in yr_trans if t["dir"]=="down")

    base20_pos = base_rate[yr][20]["pos"]
    base20_neg = 100 - base20_pos
    base20_mean = base_rate[yr][20]["mean"]

    # UP: success if r20 > 0
    ups = [t for t in yr_trans if t["dir"]=="up"]
    if ups:
        up_rs = np.array([t["r20"] for t in ups])
        up_win = (up_rs>0).mean()*100
        up_mean = up_rs.mean()*100
        up_edge = up_win - base20_pos
        up_str = f"{up_win:>3.0f}%({base20_pos:>3.0f}) {up_edge:+5.0f}pp"
    else:
        up_win = up_mean = up_edge = None
        up_str = "—"

    # DOWN: success if r20 < 0
    dns = [t for t in yr_trans if t["dir"]=="down"]
    if dns:
        dn_rs = np.array([t["r20"] for t in dns])
        dn_win = (dn_rs<0).mean()*100  # win when market falls
        dn_mean = dn_rs.mean()*100
        dn_edge = dn_win - base20_neg  # vs base rate of negative weeks
        dn_str = f"{dn_win:>3.0f}%({base20_neg:>3.0f}) {dn_edge:+5.0f}pp"
    else:
        dn_win = dn_mean = dn_edge = None
        dn_str = "—"

    # Net edge: weighted avg of up_edge + dn_edge by count
    if up_edge is not None and dn_edge is not None:
        net = (up_edge*len(ups) + dn_edge*len(dns)) / (len(ups)+len(dns))
    elif up_edge is not None:
        net = up_edge
    elif dn_edge is not None:
        net = dn_edge
    else:
        net = 0

    yearly_stats.append(dict(
        year=yr, n=len(yr_trans), n_up=n_up, n_dn=n_dn,
        up_win=up_win, up_mean=up_mean, up_edge=up_edge,
        dn_win=dn_win, dn_mean=dn_mean, dn_edge=dn_edge,
        base20_pos=base20_pos, base20_neg=base20_neg, base20_mean=base20_mean,
        net_edge=net,
    ))

    print(f"{yr:<6}{len(yr_trans):>5}{n_up:>4}{n_dn:>4}  "
          f"{up_str:<24}{dn_str:<24}{net:>+8.1f}pp")

# ── Aggregate by era ───────────────────────────────────────────────────
print("\n" + "="*100)
print("ERA AGGREGATION")
print("="*100)
ERAS = [
    ("Pre-modern 2000-2007", 2000, 2007),
    ("Post-GFC 2008-2013",   2008, 2013),
    ("Modern 2014-2019",     2014, 2019),
    ("COVID+ 2020-2023",     2020, 2023),
    ("Recent 2024-2026",     2024, 2026),
]
print(f"{'Era':<24}{'n_tr':>6}{'UP win%':>10}{'UP edge':>10}{'DN win%':>10}{'DN edge':>10}{'NET edge':>10}")
print("-"*100)
era_data = []
for label, y0, y1 in ERAS:
    yr_in = [s for s in yearly_stats if y0 <= s["year"] <= y1]
    if not yr_in: print(f"{label:<24}  (no data)"); continue
    total_n = sum(s["n"] for s in yr_in)
    ups_n = sum(s["n_up"] for s in yr_in)
    dns_n = sum(s["n_dn"] for s in yr_in)
    # Weighted edges by counts
    up_win_w = sum((s["up_win"] or 0)*s["n_up"] for s in yr_in) / max(ups_n,1)
    up_edge_w = sum((s["up_edge"] or 0)*s["n_up"] for s in yr_in) / max(ups_n,1)
    dn_win_w = sum((s["dn_win"] or 0)*s["n_dn"] for s in yr_in) / max(dns_n,1)
    dn_edge_w = sum((s["dn_edge"] or 0)*s["n_dn"] for s in yr_in) / max(dns_n,1)
    net_w = (up_edge_w*ups_n + dn_edge_w*dns_n) / max(total_n,1)
    era_data.append(dict(label=label, n=total_n, n_up=ups_n, n_dn=dns_n,
                         up_win=up_win_w, up_edge=up_edge_w,
                         dn_win=dn_win_w, dn_edge=dn_edge_w, net=net_w))
    print(f"{label:<24}{total_n:>6}{up_win_w:>9.0f}%{up_edge_w:>+9.1f}pp"
          f"{dn_win_w:>9.0f}%{dn_edge_w:>+9.1f}pp{net_w:>+9.1f}pp")

# ── HTML output ────────────────────────────────────────────────────────
years     = [s["year"] for s in yearly_stats]
up_edges  = [s["up_edge"] if s["up_edge"] is not None else 0 for s in yearly_stats]
dn_edges  = [s["dn_edge"] if s["dn_edge"] is not None else 0 for s in yearly_stats]
net_edges = [s["net_edge"] for s in yearly_stats]
n_trans   = [s["n"] for s in yearly_stats]
up_means  = [s["up_mean"] or 0 for s in yearly_stats]
dn_means  = [s["dn_mean"] or 0 for s in yearly_stats]
base_means = [s["base20_mean"] for s in yearly_stats]

# Build year rows
year_rows = []
for s in yearly_stats:
    col_net = "#86efac" if s["net_edge"]>5 else ("#fbbf24" if s["net_edge"]>-5 else "#fca5a5")
    up_w = f"{s['up_win']:.0f}%" if s['up_win'] is not None else "—"
    dn_w = f"{s['dn_win']:.0f}%" if s['dn_win'] is not None else "—"
    up_e = f"{s['up_edge']:+.0f}pp" if s['up_edge'] is not None else "—"
    dn_e = f"{s['dn_edge']:+.0f}pp" if s['dn_edge'] is not None else "—"
    up_m = f"{s['up_mean']:+.1f}%" if s['up_mean'] is not None else "—"
    dn_m = f"{s['dn_mean']:+.1f}%" if s['dn_mean'] is not None else "—"
    year_rows.append(f'''<tr style="border-bottom:1px solid #334155">
      <td style="padding:6px 10px;color:#cbd5e1;font-weight:600">{s['year']}</td>
      <td style="padding:6px 10px;text-align:right;color:#94a3b8">{s['n']}</td>
      <td style="padding:6px 10px;text-align:right;color:#94a3b8">{s['n_up']}</td>
      <td style="padding:6px 10px;text-align:right;color:#94a3b8">{s['n_dn']}</td>
      <td style="padding:6px 10px;text-align:right;color:#e2e8f0;font-weight:600">{up_w}</td>
      <td style="padding:6px 10px;text-align:right;color:#94a3b8;font-size:11px">({s['base20_pos']:.0f}%)</td>
      <td style="padding:6px 10px;text-align:right;color:{'#86efac' if s['up_edge'] and s['up_edge']>0 else '#fca5a5'};font-weight:700">{up_e}</td>
      <td style="padding:6px 10px;text-align:right;color:#cbd5e1">{up_m}</td>
      <td style="padding:6px 10px;text-align:right;color:#e2e8f0;font-weight:600">{dn_w}</td>
      <td style="padding:6px 10px;text-align:right;color:#94a3b8;font-size:11px">({s['base20_neg']:.0f}%)</td>
      <td style="padding:6px 10px;text-align:right;color:{'#86efac' if s['dn_edge'] and s['dn_edge']>0 else '#fca5a5'};font-weight:700">{dn_e}</td>
      <td style="padding:6px 10px;text-align:right;color:#cbd5e1">{dn_m}</td>
      <td style="padding:6px 10px;text-align:right;background:{col_net};color:#0a0f1e;font-weight:800">{s['net_edge']:+.1f}pp</td>
    </tr>''')
year_tbody = "\n".join(year_rows)

# Era rows
era_rows = []
for e in era_data:
    col_net = "#86efac" if e["net"]>5 else ("#fbbf24" if e["net"]>-5 else "#fca5a5")
    era_rows.append(f'''<tr style="border-bottom:1px solid #334155;background:#1e293b">
      <td style="padding:8px 10px;color:#e2e8f0;font-weight:700">{e['label']}</td>
      <td style="padding:8px 10px;text-align:right;color:#cbd5e1;font-weight:600">{e['n']}</td>
      <td style="padding:8px 10px;text-align:right;color:#cbd5e1">{e['up_win']:.0f}%</td>
      <td style="padding:8px 10px;text-align:right;color:{'#86efac' if e['up_edge']>0 else '#fca5a5'};font-weight:700">{e['up_edge']:+.1f}pp</td>
      <td style="padding:8px 10px;text-align:right;color:#cbd5e1">{e['dn_win']:.0f}%</td>
      <td style="padding:8px 10px;text-align:right;color:{'#86efac' if e['dn_edge']>0 else '#fca5a5'};font-weight:700">{e['dn_edge']:+.1f}pp</td>
      <td style="padding:8px 10px;text-align:right;background:{col_net};color:#0a0f1e;font-weight:800">{e['net']:+.1f}pp</td>
    </tr>''')
era_tbody = "\n".join(era_rows)

chart_data = dict(
    years=[int(x) for x in years],
    up_edges=[float(x) for x in up_edges],
    dn_edges=[float(x) for x in dn_edges],
    net_edges=[float(x) for x in net_edges],
    n_trans=[int(x) for x in n_trans],
    up_means=[float(x) for x in up_means],
    dn_means=[float(x) for x in dn_means],
    base_means=[float(x) for x in base_means],
)

html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Tam Quan v3.4b — Success rate theo năm</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* {{ box-sizing:border-box;margin:0;padding:0 }}
body {{ background:#0a0f1e;color:#e2e8f0;font-family:'Segoe UI',sans-serif;padding:20px }}
h1 {{ font-size:20px;color:#f8fafc;margin-bottom:4px }}
h2 {{ font-size:15px;color:#cbd5e1;margin:20px 0 10px }}
.subtitle {{ color:#64748b;font-size:13px;margin-bottom:16px }}
.staging-tag {{ background:#7c3aed;color:#fff;padding:2px 10px;border-radius:6px;font-size:11px;font-weight:700;margin-left:8px }}
.panel {{ background:#0f172a;border:1px solid #334155;border-radius:8px;padding:14px;margin-bottom:16px }}
.panel .sub {{ font-size:11px;color:#64748b;margin-bottom:10px }}
table {{ width:100%;border-collapse:collapse;font-size:12px }}
thead th {{ background:#0f172a;color:#64748b;font-size:10px;font-weight:700;
            text-transform:uppercase;letter-spacing:.5px;padding:8px 6px;
            border-bottom:2px solid #334155;text-align:left }}
.table-wrap {{ overflow-x:auto;border-radius:8px;border:1px solid #334155;background:#0f172a }}
.legend {{ background:#1e293b;border:1px solid #334155;border-radius:8px;padding:10px 14px;
           margin-bottom:14px;font-size:12px;color:#94a3b8 }}
.legend b {{ color:#e2e8f0 }}
.legend code {{ background:#0f172a;color:#86efac;padding:1px 6px;border-radius:4px;font-size:11px }}
canvas {{ background:#0a0f1e;border-radius:6px }}
</style>
</head>
<body>
<h1>📈 Tam Quan v3.4b — Success rate theo năm/kỷ nguyên<span class="staging-tag">STAGING NEXT</span></h1>
<p class="subtitle">{len(trans_full)} transitions từ {trans_full[0]['date'].year} đến {trans_full[-1]['date'].year} · grading T+20 forward return vs base rate VNINDEX cùng năm</p>

<div class="legend">
  <b>Cách đọc</b>:<br>
  • <b>UP win%</b> = % upgrade-transitions có r20 &gt; 0 (system nói lên, market thật sự lên).<br>
  • <b>DOWN win%</b> = % downgrade-transitions có r20 &lt; 0 (system nói xuống, market thật sự xuống).<br>
  • Trong dấu ngoặc <code>(X%)</code> là <b>base rate</b> năm đó (% tuần dương / âm random của VNINDEX).<br>
  • <b>Edge</b> = system win% − base rate. Edge dương = system tốt hơn random. Edge âm = system tệ hơn random.<br>
  • <b>NET edge</b> = weighted avg edge (theo số transitions up vs down). Mục tiêu: edge dương ổn định.<br>
</div>

<h2>📊 Tổng hợp theo kỷ nguyên</h2>
<div class="table-wrap">
<table>
<thead><tr>
  <th>Era</th><th style="text-align:right">n trans</th>
  <th style="text-align:right">UP win%</th><th style="text-align:right">UP edge</th>
  <th style="text-align:right">DOWN win%</th><th style="text-align:right">DOWN edge</th>
  <th style="text-align:right">NET edge</th>
</tr></thead>
<tbody>{era_tbody}</tbody>
</table>
</div>

<h2>📈 Chart: NET edge theo năm</h2>
<div class="panel">
  <canvas id="chart_net" height="120"></canvas>
</div>

<h2>📉 Chart: UP edge vs DOWN edge theo năm</h2>
<div class="panel">
  <canvas id="chart_split" height="120"></canvas>
</div>

<h2>🔍 Chi tiết theo năm</h2>
<div class="table-wrap">
<table>
<thead><tr>
  <th>Năm</th><th style="text-align:right">n</th><th style="text-align:right">▲</th><th style="text-align:right">▼</th>
  <th style="text-align:right">UP win</th><th style="text-align:right">(base)</th><th style="text-align:right">UP edge</th><th style="text-align:right">UP mean r20</th>
  <th style="text-align:right">DN win</th><th style="text-align:right">(base)</th><th style="text-align:right">DN edge</th><th style="text-align:right">DN mean r20</th>
  <th style="text-align:right">NET edge</th>
</tr></thead>
<tbody>{year_tbody}</tbody>
</table>
</div>

<script>
const D = {json.dumps(chart_data)};
const baseOpt = {{
  responsive:true, maintainAspectRatio:false,
  plugins:{{ legend:{{ labels:{{ color:'#cbd5e1', font:{{size:11}} }} }} }},
  scales:{{
    x:{{ ticks:{{ color:'#64748b' }}, grid:{{color:'#1e293b'}} }},
    y:{{ ticks:{{ color:'#64748b', callback:v=>v+'pp' }}, grid:{{color:'#1e293b'}} }}
  }}
}};
new Chart(document.getElementById('chart_net'), {{
  type:'bar',
  data:{{ labels:D.years, datasets:[{{
    label:'NET edge', data:D.net_edges,
    backgroundColor: D.net_edges.map(v => v>5?'rgba(34,197,94,0.7)':(v>-5?'rgba(251,191,36,0.6)':'rgba(239,68,68,0.7)')),
    borderColor: '#0a0f1e', borderWidth:1
  }}]}},
  options: baseOpt
}});
new Chart(document.getElementById('chart_split'), {{
  type:'bar',
  data:{{ labels:D.years, datasets:[
    {{ label:'UP edge',   data:D.up_edges,
      backgroundColor:'rgba(34,197,94,0.65)', borderColor:'#16a34a', borderWidth:1 }},
    {{ label:'DOWN edge', data:D.dn_edges,
      backgroundColor:'rgba(239,68,68,0.65)', borderColor:'#dc2626', borderWidth:1 }}
  ]}},
  options: baseOpt
}});
</script>
</body>
</html>"""

out = os.path.join(WORKDIR, "vnindex_v3_4b_yearly_success.html")
with open(out, "w", encoding="utf-8") as f: f.write(html)
print(f"\n✓ Saved: {out}")
