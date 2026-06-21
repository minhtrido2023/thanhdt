# -*- coding: utf-8 -*-
"""
build_v3_1_horizon_diagnostic.py
================================
Step A1 + A2 diagnostic for Tam Quan v3.1:

  A1. Win rate at T+5 / T+20 / T+60 (state-system natural horizon)
  A2. Breakdown by |step| (1-step adjacent flips vs 2-3 step big moves)

Also computes the VN-Index unconditional base rate (% positive 5/20/60-day
windows + mean drift) so we can grade win rates against the right baseline.

Output: vnindex_v3_1_horizon_diagnostic.html
"""
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
ORDER = {"CRISIS":1,"BEAR":2,"NEUTRAL":3,"BULL":4,"EX-BULL":5}
HORIZONS = [5, 20, 60]   # trading days

# ── Load ───────────────────────────────────────────────────────────────
st = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_tam_quan_v3_1_full_history.csv"))
st["time"] = pd.to_datetime(st["time"]); st = st.sort_values("time").reset_index(drop=True)
dr = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_dual_v3_full.csv"))
dr["time"] = pd.to_datetime(dr["time"])
df = st.merge(dr[["time","Close"]], on="time", how="left").reset_index(drop=True)
n = len(df); close = df["Close"].values; state = df["state"].values.astype(int)
print(f"Loaded {n} rows | {df['time'].iloc[0].date()} → {df['time'].iloc[-1].date()}")

# ── Base rate: ALL forward windows ─────────────────────────────────────
print("\nComputing unconditional VN-Index base rate ...")
base = {}
for h in HORIZONS:
    r = np.array([close[i+h]/close[i]-1 for i in range(n-h)])
    base[h] = dict(
        n=len(r), mean=r.mean()*100, median=np.median(r)*100,
        pos=(r>0).mean()*100,
        pos_thr=( r >  (0.02 if h==5 else (0.04 if h==20 else 0.08))).mean()*100,
        neg_thr=( r < -(0.02 if h==5 else (0.04 if h==20 else 0.08))).mean()*100,
    )
    print(f"  T+{h:>2}: mean {r.mean()*100:+.2f}% | median {np.median(r)*100:+.2f}% | %pos {(r>0).mean()*100:.1f}%")

# ── Transitions with all horizons ─────────────────────────────────────
trans = []
prev = state[0]
for i in range(1, n):
    s = state[i]
    if s != prev:
        f_n, t_n = STATE_NAMES[prev], STATE_NAMES[s]
        step = ORDER[t_n] - ORDER[f_n]
        direction = "up" if step > 0 else "down"
        rec = dict(
            date=df["time"].iloc[i], from_=f_n, to=t_n, step=step,
            abs_step=abs(step), dir=direction, close=float(close[i]),
        )
        for h in HORIZONS:
            rec[f"r{h}"] = close[i+h]/close[i]-1 if i+h < n else None
        trans.append(rec)
        prev = s
trans = [t for t in trans if all(t[f"r{h}"] is not None for h in HORIZONS)]
print(f"\n{len(trans)} transitions with full T+60 lookahead")

# ── Per-horizon × direction × abs_step stats ─────────────────────────
def calc(rows, h):
    if not rows: return None
    rs = np.array([r[f"r{h}"] for r in rows])
    wins = [(r["dir"]=="up" and r[f"r{h}"]>0) or (r["dir"]=="down" and r[f"r{h}"]<0) for r in rows]
    thr = 0.02 if h==5 else (0.04 if h==20 else 0.08)
    wins_g = [(r["dir"]=="up" and r[f"r{h}"]> thr) or (r["dir"]=="down" and r[f"r{h}"]<-thr) for r in rows]
    return dict(
        n=len(rs), mean=rs.mean()*100, median=np.median(rs)*100,
        win=np.mean(wins)*100, win_g=np.mean(wins_g)*100,
    )

# Group rows
groups = {
    "ALL":   trans,
    "UP":    [t for t in trans if t["dir"]=="up"],
    "DOWN":  [t for t in trans if t["dir"]=="down"],
    "UP_1":  [t for t in trans if t["dir"]=="up"   and t["abs_step"]==1],
    "UP_2":  [t for t in trans if t["dir"]=="up"   and t["abs_step"]==2],
    "UP_3p": [t for t in trans if t["dir"]=="up"   and t["abs_step"]>=3],
    "DN_1":  [t for t in trans if t["dir"]=="down" and t["abs_step"]==1],
    "DN_2":  [t for t in trans if t["dir"]=="down" and t["abs_step"]==2],
    "DN_3p": [t for t in trans if t["dir"]=="down" and t["abs_step"]>=3],
}
group_labels = {
    "ALL":"Tất cả","UP":"▲ Upgrade","DOWN":"▼ Downgrade",
    "UP_1":"▲ 1-step","UP_2":"▲ 2-step","UP_3p":"▲ 3+ step",
    "DN_1":"▼ 1-step","DN_2":"▼ 2-step","DN_3p":"▼ 3+ step",
}

# Build summary table
print("\n" + "="*100)
print(f"{'Group':<12}{'n':>5}  {'T+5 win%/mean':>22}  {'T+20 win%/mean':>22}  {'T+60 win%/mean':>22}")
print("="*100)
table = []
for key, rows in groups.items():
    line = [key, len(rows)]
    cells = []
    for h in HORIZONS:
        s = calc(rows, h)
        if s is None: cells.append(("",0,0)); continue
        line.append(s)
        cells.append((f"{s['win']:.0f}% / {s['mean']:+.2f}%", s['win'], s['mean']))
    print(f"{group_labels[key]:<12}{len(rows):>5}  " +
          "  ".join(f"{c[0]:>22}" for c in cells))
    table.append((key, group_labels[key], len(rows), [calc(rows, h) for h in HORIZONS]))

# Edge vs base rate
print("\n--- EDGE vs unconditional base rate ---")
print(f"{'Group':<12}{'Horizon':>9}{'Win%':>8}{'BaseUp%':>10}{'Edge_pp':>10}{'Mean%':>9}{'BaseMean':>10}{'Edge_pp':>10}")
edge_table = []
for key, label, nrows, stats_list in table:
    if nrows == 0: continue
    for h, s in zip(HORIZONS, stats_list):
        if s is None: continue
        # for UP groups: win=%pos, base=base[h]['pos']
        # for DOWN groups: win=%neg, base=100-base[h]['pos']
        if key.startswith("DN") or key == "DOWN":
            base_win = 100 - base[h]['pos']
            edge_win = s['win'] - base_win
            edge_mean = s['mean'] - base[h]['mean']   # negative is good for down
        elif key.startswith("UP") or key == "UP":
            base_win = base[h]['pos']
            edge_win = s['win'] - base_win
            edge_mean = s['mean'] - base[h]['mean']
        else:  # ALL
            base_win = base[h]['pos']     # mixed, use neutral baseline
            edge_win = None
            edge_mean = s['mean'] - base[h]['mean']
        edge_table.append(dict(group=key, label=label, h=h, n=s['n'],
                               win=s['win'], base_win=base_win, edge_win=edge_win,
                               mean=s['mean'], base_mean=base[h]['mean'], edge_mean=edge_mean))
        ew_s = f"{edge_win:+.1f}pp" if edge_win is not None else "—"
        print(f"{label:<12}T+{h:<7}{s['win']:>6.1f}%{base_win:>9.1f}%{ew_s:>10}{s['mean']:>+8.2f}%{base[h]['mean']:>+9.2f}%{edge_mean:>+9.2f}pp")

# ── HTML ───────────────────────────────────────────────────────────────
def color_win(v, base):
    if v is None: return "#94a3b8"
    d = v - base
    if d >=  5: return "#16a34a"
    if d >=  2: return "#65a30d"
    if d >= -2: return "#9ca3af"
    if d >= -5: return "#ea580c"
    return "#dc2626"

def color_mean(v, base, is_down):
    # for UP/ALL we want mean > base; for DOWN we want mean < base
    if v is None: return "#94a3b8"
    d = (base - v) if is_down else (v - base)
    if d >= 0.5: return "#16a34a"
    if d >= 0.0: return "#65a30d"
    if d >= -0.5: return "#9ca3af"
    return "#dc2626"

STATE_BG = {
    "CRISIS":  ("#7f1d1d","#fca5a5"),
    "BEAR":    ("#7c2d12","#fdba74"),
    "NEUTRAL": ("#1e293b","#94a3b8"),
    "BULL":    ("#14532d","#86efac"),
    "EX-BULL": ("#3b0764","#c4b5fd"),
}

# Build main table HTML
rows_html = []
for key, label, nrows, stats_list in table:
    is_down = key.startswith("DN") or key == "DOWN"
    cells = [f'<td style="padding:8px 10px;color:#e2e8f0;font-weight:600">{label}</td>',
             f'<td style="padding:8px 10px;text-align:right;color:#94a3b8">{nrows}</td>']
    for h, s in zip(HORIZONS, stats_list):
        if s is None or nrows == 0:
            cells.append('<td colspan="2" style="padding:8px 10px;text-align:center;color:#475569">—</td>')
            continue
        bw = (100-base[h]['pos']) if is_down else base[h]['pos']
        wc = color_win(s['win'], bw) if key != "ALL" else "#94a3b8"
        mc = color_mean(s['mean'], base[h]['mean'], is_down)
        edge_w = "" if key == "ALL" else f"<div style='font-size:10px;color:#64748b'>edge {s['win']-bw:+.1f}pp</div>"
        edge_m_val = (base[h]['mean']-s['mean']) if is_down else (s['mean']-base[h]['mean'])
        edge_m = f"<div style='font-size:10px;color:#64748b'>edge {edge_m_val:+.2f}pp</div>"
        cells.append(f'<td style="padding:6px 10px;text-align:right;color:{wc};font-weight:700;border-left:1px solid #1e293b">'
                     f'{s["win"]:.0f}%{edge_w}</td>')
        cells.append(f'<td style="padding:6px 10px;text-align:right;color:{mc};font-variant-numeric:tabular-nums">'
                     f'{s["mean"]:+.2f}%{edge_m}</td>')
    rows_html.append(f'<tr style="border-bottom:1px solid #1e293b">{"".join(cells)}</tr>')
rows_html = "\n".join(rows_html)

# Base-rate row
base_cells = ['<td style="padding:8px 10px;color:#94a3b8;font-style:italic">Base rate (VN-Index)</td>',
              f'<td style="padding:8px 10px;text-align:right;color:#64748b">{base[5]["n"]:,}</td>']
for h in HORIZONS:
    base_cells.append(f'<td style="padding:6px 10px;text-align:right;color:#94a3b8;border-left:1px solid #1e293b">{base[h]["pos"]:.1f}%</td>')
    base_cells.append(f'<td style="padding:6px 10px;text-align:right;color:#94a3b8;font-variant-numeric:tabular-nums">{base[h]["mean"]:+.2f}%</td>')
base_row = f'<tr style="border-top:2px solid #475569;background:#0f172a">{"".join(base_cells)}</tr>'

# Per-pair × horizon table
pairs = {}
for t in trans:
    pairs.setdefault((t["from_"],t["to"]), []).append(t)

pair_html = []
for (f_n,t_n), rows in sorted(pairs.items(), key=lambda kv:(ORDER[kv[0][0]], ORDER[kv[0][1]])):
    step = ORDER[t_n]-ORDER[f_n]
    is_down = step < 0
    fbg,ffg = STATE_BG[f_n]; tbg,tfg = STATE_BG[t_n]
    cells = [
        f'<td style="padding:6px 8px"><span style="background:{fbg};color:{ffg};padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700">{f_n}</span></td>',
        f'<td style="padding:6px 6px;text-align:center;color:#64748b">{"▲"*step if step>0 else "▼"*(-step)}</td>',
        f'<td style="padding:6px 8px"><span style="background:{tbg};color:{tfg};padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700">{t_n}</span></td>',
        f'<td style="padding:6px 8px;text-align:right;color:#e2e8f0">{len(rows)}</td>',
    ]
    for h in HORIZONS:
        s = calc(rows, h)
        bw = (100-base[h]['pos']) if is_down else base[h]['pos']
        wc = color_win(s['win'], bw); mc = color_mean(s['mean'], base[h]['mean'], is_down)
        cells.append(f'<td style="padding:6px 8px;text-align:right;color:{wc};font-weight:700;border-left:1px solid #1e293b">{s["win"]:.0f}%</td>')
        cells.append(f'<td style="padding:6px 8px;text-align:right;color:{mc};font-variant-numeric:tabular-nums">{s["mean"]:+.2f}%</td>')
    pair_html.append(f'<tr style="border-bottom:1px solid #1e293b">{"".join(cells)}</tr>')
pair_html = "\n".join(pair_html)

# Headline summary
def hl(key, h):
    s = calc(groups[key], h)
    bw = (100-base[h]['pos']) if (key.startswith("DN") or key=="DOWN") else base[h]['pos']
    return s['win'], bw, s['win']-bw, s['mean'], base[h]['mean']

up_5  = hl("UP", 5);  up_20  = hl("UP", 20);  up_60  = hl("UP", 60)
dn_5  = hl("DOWN", 5); dn_20 = hl("DOWN", 20); dn_60 = hl("DOWN", 60)

html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Tam Quan v3.1 · Horizon Diagnostic (T+5/T+20/T+60)</title>
<style>
* {{ box-sizing:border-box;margin:0;padding:0 }}
body {{ background:#0a0f1e;color:#e2e8f0;font-family:'Segoe UI',sans-serif;padding:20px;max-width:1400px;margin:0 auto }}
h1 {{ font-size:20px;color:#f8fafc;margin-bottom:4px }}
h2 {{ font-size:15px;color:#cbd5e1;margin:24px 0 10px }}
.subtitle {{ color:#64748b;font-size:13px;margin-bottom:16px }}
.staging-tag {{ background:#7c3aed;color:#fff;padding:2px 10px;border-radius:6px;font-size:11px;font-weight:700;margin-left:8px }}
.verdict {{ background:linear-gradient(135deg,#0f172a,#1e293b);border:1px solid #334155;border-radius:10px;padding:16px;margin-bottom:18px }}
.verdict h3 {{ color:#86efac;font-size:14px;margin-bottom:8px }}
.verdict ul {{ margin-left:18px;color:#cbd5e1;font-size:13px;line-height:1.7 }}
.verdict code {{ background:#0a0f1e;color:#86efac;padding:1px 6px;border-radius:4px;font-size:11px }}
.summary {{ display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px }}
.hzn-card {{ background:#1e293b;border:1px solid #334155;border-radius:10px;padding:14px }}
.hzn-card h4 {{ color:#94a3b8;font-size:12px;margin-bottom:8px;letter-spacing:.5px;text-transform:uppercase }}
.hzn-row {{ display:flex;justify-content:space-between;padding:4px 0;font-size:12px }}
.hzn-row .lbl {{ color:#94a3b8 }}
.hzn-row .val {{ color:#e2e8f0;font-weight:700;font-variant-numeric:tabular-nums }}
.up-good {{ color:#86efac }}
.dn-good {{ color:#86efac }}
.bad {{ color:#fca5a5 }}
table {{ width:100%;border-collapse:collapse;font-size:12px;background:#0f172a;border-radius:8px;overflow:hidden }}
thead th {{ background:#1e293b;color:#64748b;font-size:10px;font-weight:700;
            text-transform:uppercase;letter-spacing:.5px;padding:10px 8px;
            border-bottom:2px solid #334155;text-align:left }}
thead th.right {{ text-align:right }}
thead th.center {{ text-align:center }}
.hzn-group {{ background:#0f172a;color:#cbd5e1;font-size:11px }}
.table-wrap {{ overflow-x:auto;border-radius:8px;border:1px solid #334155 }}
.note {{ background:#1e293b;border:1px solid #334155;border-radius:8px;padding:10px 14px;font-size:12px;color:#94a3b8;margin-bottom:14px }}
.note b {{ color:#e2e8f0 }}
</style>
</head>
<body>

<h1>📊 Tam Quan v3.1 · Horizon Diagnostic<span class="staging-tag">A1 + A2</span></h1>
<p class="subtitle">{len(trans)} transitions có đủ T+60 lookahead · {df['time'].iloc[0].year}–{df['time'].iloc[-1].year}
· Đánh giá ở 3 horizon: T+5 (1 tuần), T+20 (1 tháng), T+60 (3 tháng) — đo edge so với base rate VN-Index</p>

<div class="verdict">
  <h3>🎯 Headline — edge vs base rate</h3>
  <ul>
    <li><b>VN-Index base rate</b>: %pos T+5 = <code>{base[5]['pos']:.1f}%</code> · T+20 = <code>{base[20]['pos']:.1f}%</code> · T+60 = <code>{base[60]['pos']:.1f}%</code>
      (mean drift: <code>{base[5]['mean']:+.2f}%</code> / <code>{base[20]['mean']:+.2f}%</code> / <code>{base[60]['mean']:+.2f}%</code>)</li>
    <li><b>▲ Upgrade win vs base</b>: T+5 <code>{up_5[0]:.0f}% vs {up_5[1]:.0f}% ({up_5[2]:+.1f}pp)</code> ·
      T+20 <code>{up_20[0]:.0f}% vs {up_20[1]:.0f}% ({up_20[2]:+.1f}pp)</code> ·
      T+60 <code>{up_60[0]:.0f}% vs {up_60[1]:.0f}% ({up_60[2]:+.1f}pp)</code></li>
    <li><b>▼ Downgrade win vs base</b>: T+5 <code>{dn_5[0]:.0f}% vs {dn_5[1]:.0f}% ({dn_5[2]:+.1f}pp)</code> ·
      T+20 <code>{dn_20[0]:.0f}% vs {dn_20[1]:.0f}% ({dn_20[2]:+.1f}pp)</code> ·
      T+60 <code>{dn_60[0]:.0f}% vs {dn_60[1]:.0f}% ({dn_60[2]:+.1f}pp)</code></li>
  </ul>
</div>

<h2>📋 A1 — Win rate × horizon × direction × step size</h2>

<div class="note">
  <b>Cách đọc</b>: Win% là tỷ lệ transition đi đúng hướng (UP win = r&gt;0; DOWN win = r&lt;0).
  <code>edge</code> nhỏ bên dưới = chênh lệch so với base rate VN-Index trong cùng horizon — đây mới là metric quan trọng.
  Mean cũng có edge tương ứng. Group <code>ALL</code> trộn cả UP/DOWN nên edge_win không có ý nghĩa.
</div>

<div class="table-wrap">
<table>
<thead>
<tr>
  <th>Group</th>
  <th class="right">n</th>
  <th class="right" style="border-left:1px solid #334155">T+5 Win</th>
  <th class="right">T+5 Mean</th>
  <th class="right" style="border-left:1px solid #334155">T+20 Win</th>
  <th class="right">T+20 Mean</th>
  <th class="right" style="border-left:1px solid #334155">T+60 Win</th>
  <th class="right">T+60 Mean</th>
</tr>
</thead>
<tbody>
{rows_html}
{base_row}
</tbody>
</table>
</div>

<h2>🔬 A2 — Per-pair breakdown (xem cặp nào yếu nhất)</h2>

<div class="note">
Đây là chỗ confirm hypothesis: <b>1-step adjacent flips</b> (vd NEUTRAL↔BULL) thường có win rate thấp + mean nhỏ — đây là noise chính của hệ thống.
<b>Multi-step</b> (NEUTRAL→CRISIS, BEAR→BULL) ít hơn nhưng signal mạnh.
</div>

<div class="table-wrap">
<table>
<thead>
<tr>
  <th>Từ</th><th class="center">Step</th><th>Sang</th>
  <th class="right">n</th>
  <th class="right" style="border-left:1px solid #334155">T+5 Win</th>
  <th class="right">T+5 Mean</th>
  <th class="right" style="border-left:1px solid #334155">T+20 Win</th>
  <th class="right">T+20 Mean</th>
  <th class="right" style="border-left:1px solid #334155">T+60 Win</th>
  <th class="right">T+60 Mean</th>
</tr>
</thead>
<tbody>
{pair_html}
</tbody>
</table>
</div>

<div class="note" style="margin-top:18px">
  <b>Phương pháp tô màu</b>: Win cell — xanh đậm ≥+5pp edge, xanh nhạt +2..+5pp, xám ±2pp, cam −2..−5pp, đỏ &lt;−5pp.
  Mean cell — tương tự với mốc ±0.5pp.
  Base rate trong từng horizon (% positive tuần / tháng / quý) chính là benchmark để chấm điểm hệ thống.
</div>

</body>
</html>"""

out = os.path.join(WORKDIR, "vnindex_v3_1_horizon_diagnostic.html")
with open(out,"w",encoding="utf-8") as f: f.write(html)
print(f"\n✓ Saved: {out}")
