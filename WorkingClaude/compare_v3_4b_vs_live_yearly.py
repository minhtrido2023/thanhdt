# -*- coding: utf-8 -*-
"""
compare_v3_4b_vs_live_yearly.py
================================
Side-by-side per-year + per-era success-rate comparison:
  • LIVE Tinh Tế  (vnindex_5state_history.csv = v2g_pe3c_s3)
  • v3.4b Định Tâm (vnindex_5state_tam_quan_v3_4b_full_history.csv)

For each variant computes:
  • n transitions per year
  • UP win rate T+20, edge vs base, mean
  • DOWN win rate T+20, edge vs base, mean
  • NET edge

Side-by-side reveals:
  • Era-level: which variant dominates which era
  • Win-rate stability: does v3.4b add value uniformly or only certain regimes?
  • Sample size warning where n is small
"""
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
ORDER = {"CRISIS":1,"BEAR":2,"NEUTRAL":3,"BULL":4,"EX-BULL":5}

# ── Load close ────────────────────────────────────────────────────────
dr = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_dual_v3_full.csv"))
dr["time"] = pd.to_datetime(dr["time"])
close_by_time = dict(zip(dr["time"], dr["Close"]))

def load_states(path):
    df = pd.read_csv(os.path.join(WORKDIR, path))
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    df["Close"] = df["time"].map(close_by_time)
    return df[df["Close"].notna()].reset_index(drop=True)

variants = {
    "LIVE Tinh Tế": load_states("vnindex_5state_history.csv"),
    "v3.4b Định Tâm": load_states("vnindex_5state_tam_quan_v3_4b_full_history.csv"),
}

def analyze(df, label):
    """Return per-year stats dict."""
    n = len(df); close = df["Close"].values; state = df["state"].values.astype(int)
    def fwd(i, h):
        if i+h >= n: return None
        return close[i+h]/close[i] - 1

    df["year"] = df["time"].dt.year
    # Base rate per year
    base = {}
    for yr in sorted(df["year"].unique()):
        idxs = df[df["year"]==yr].index
        rets = []
        for i in idxs:
            r = fwd(i, 20)
            if r is not None: rets.append(r)
        if rets:
            base[yr] = {
                "n": len(rets), "mean": np.mean(rets)*100,
                "pos": (np.array(rets)>0).mean()*100,
                "neg": (np.array(rets)<0).mean()*100,
            }

    # Collect transitions
    trans = []
    prev = state[0]
    for i in range(1, n):
        if state[i] != prev:
            f_n, t_n = STATE_NAMES[prev], STATE_NAMES[state[i]]
            step = ORDER[t_n] - ORDER[f_n]
            rec = dict(year=int(df["year"].iloc[i]), dir="up" if step>0 else "down",
                       r20=fwd(i, 20))
            trans.append(rec)
            prev = state[i]
    trans = [t for t in trans if t["r20"] is not None]

    # Per year
    stats = {}
    for yr in sorted({t["year"] for t in trans}):
        yt = [t for t in trans if t["year"]==yr]
        if yr not in base: continue
        b = base[yr]
        ups = [t for t in yt if t["dir"]=="up"]
        dns = [t for t in yt if t["dir"]=="down"]
        d = dict(year=yr, n=len(yt), n_up=len(ups), n_dn=len(dns), base_pos=b["pos"], base_neg=b["neg"])
        if ups:
            r = np.array([t["r20"] for t in ups])
            d["up_win"] = float((r>0).mean()*100); d["up_mean"] = float(r.mean()*100)
            d["up_edge"] = d["up_win"] - b["pos"]
        if dns:
            r = np.array([t["r20"] for t in dns])
            d["dn_win"] = float((r<0).mean()*100); d["dn_mean"] = float(r.mean()*100)
            d["dn_edge"] = d["dn_win"] - b["neg"]
        # NET edge
        ne, nu, nd = 0, 0, 0
        if "up_edge" in d:   ne += d["up_edge"] * len(ups); nu = len(ups)
        if "dn_edge" in d:   ne += d["dn_edge"] * len(dns); nd = len(dns)
        d["net"] = ne / max(nu+nd, 1)
        stats[yr] = d
    print(f"{label}: {len(trans)} transitions with r20")
    return stats

results = {label: analyze(df, label) for label, df in variants.items()}

# ── Era comparison ────────────────────────────────────────────────────
ERAS = [
    ("Pre-modern 2000-2007", 2000, 2007),
    ("Post-GFC 2008-2013",   2008, 2013),
    ("Modern 2014-2019",     2014, 2019),
    ("COVID+ 2020-2023",     2020, 2023),
    ("Recent 2024-2026",     2024, 2026),
]

print("\n" + "="*120)
print("ERA-LEVEL COMPARISON: LIVE Tinh Tế vs v3.4b Định Tâm")
print("="*120)
print(f"{'Era':<24}{'':<2}"
      f"{'LIVE n':>7}{'LIVE UP%':>10}{'LIVE DN%':>10}{'LIVE NET':>10}{'':<2}"
      f"{'v34b n':>7}{'v34b UP%':>10}{'v34b DN%':>10}{'v34b NET':>10}{'':<2}{'Δ NET':>9}")
print("-"*120)
era_compare = []
for label, y0, y1 in ERAS:
    row = {"label": label}
    for var_name, stats in results.items():
        sub = [s for s in stats.values() if y0 <= s["year"] <= y1]
        if not sub: continue
        n = sum(s["n"] for s in sub)
        nu = sum(s["n_up"] for s in sub); nd = sum(s["n_dn"] for s in sub)
        up_w = sum(s.get("up_win",0)*s["n_up"] for s in sub) / max(nu,1)
        up_e = sum(s.get("up_edge",0)*s["n_up"] for s in sub) / max(nu,1)
        dn_w = sum(s.get("dn_win",0)*s["n_dn"] for s in sub) / max(nd,1)
        dn_e = sum(s.get("dn_edge",0)*s["n_dn"] for s in sub) / max(nd,1)
        net = (up_e*nu + dn_e*nd) / max(n,1)
        key = "live" if "LIVE" in var_name else "v34b"
        row[key] = dict(n=n, up_w=up_w, dn_w=dn_w, net=net, up_e=up_e, dn_e=dn_e)
    if "live" in row and "v34b" in row:
        delta = row["v34b"]["net"] - row["live"]["net"]
        row["delta"] = delta
        era_compare.append(row)
        marker = "✓✓" if delta > 5 else ("✓" if delta > 0 else ("=" if abs(delta)<1 else "⚠"))
        print(f"{label:<24}  "
              f"{row['live']['n']:>6} {row['live']['up_w']:>8.0f}% {row['live']['dn_w']:>8.0f}% {row['live']['net']:>+8.1f}pp  "
              f"{row['v34b']['n']:>6} {row['v34b']['up_w']:>8.0f}% {row['v34b']['dn_w']:>8.0f}% {row['v34b']['net']:>+8.1f}pp  "
              f"{delta:>+7.1f}pp {marker}")

# ── Year-by-year side-by-side ──────────────────────────────────────────
print("\n" + "="*120)
print("YEAR-BY-YEAR COMPARISON")
print("="*120)
print(f"{'Year':<6}{'':<2}"
      f"{'LIVE n':>7}{'LIVE UP%':>10}{'LIVE DN%':>10}{'LIVE NET':>10}{'':<2}"
      f"{'v34b n':>7}{'v34b UP%':>10}{'v34b DN%':>10}{'v34b NET':>10}{'':<2}{'Δ NET':>9}")
print("-"*120)
all_years = sorted(set(list(results["LIVE Tinh Tế"].keys()) + list(results["v3.4b Định Tâm"].keys())))
yearly_compare = []
for yr in all_years:
    l = results["LIVE Tinh Tế"].get(yr); v = results["v3.4b Định Tâm"].get(yr)
    if not l or not v: continue
    delta = v["net"] - l["net"]
    marker = "✓✓" if delta>5 else ("✓" if delta>0 else ("=" if abs(delta)<1 else "⚠"))
    yearly_compare.append({"year": yr, "live": l, "v34b": v, "delta": delta})
    print(f"{yr:<6}  "
          f"{l['n']:>6} {l.get('up_win',0):>8.0f}% {l.get('dn_win',0):>8.0f}% {l['net']:>+8.1f}pp  "
          f"{v['n']:>6} {v.get('up_win',0):>8.0f}% {v.get('dn_win',0):>8.0f}% {v['net']:>+8.1f}pp  "
          f"{delta:>+7.1f}pp {marker}")

# Aggregate summary
print(f"\n{'='*120}")
print("OVERALL")
print(f"{'='*120}")
print(f"  {'Variant':<22}{'Total n':>10}{'UP win%':>10}{'UP edge':>10}{'DN win%':>10}{'DN edge':>10}{'NET edge':>11}")
for var_name in ["LIVE Tinh Tế", "v3.4b Định Tâm"]:
    stats = results[var_name]
    all_n = sum(s["n"] for s in stats.values())
    all_nu = sum(s["n_up"] for s in stats.values())
    all_nd = sum(s["n_dn"] for s in stats.values())
    up_w = sum(s.get("up_win",0)*s["n_up"] for s in stats.values()) / max(all_nu,1)
    up_e = sum(s.get("up_edge",0)*s["n_up"] for s in stats.values()) / max(all_nu,1)
    dn_w = sum(s.get("dn_win",0)*s["n_dn"] for s in stats.values()) / max(all_nd,1)
    dn_e = sum(s.get("dn_edge",0)*s["n_dn"] for s in stats.values()) / max(all_nd,1)
    net  = (up_e*all_nu + dn_e*all_nd) / max(all_n,1)
    print(f"  {var_name:<22}{all_n:>10}{up_w:>9.0f}%{up_e:>+9.1f}pp{dn_w:>9.0f}%{dn_e:>+9.1f}pp{net:>+10.1f}pp")

# Recent era detail
print(f"\n{'='*120}")
print("RECENT-ERA DETAIL (2024-2026)")
print(f"{'='*120}")
for var_name in ["LIVE Tinh Tế", "v3.4b Định Tâm"]:
    stats = results[var_name]
    recent_years = [y for y in stats if 2024 <= y <= 2026]
    print(f"\n  {var_name}:")
    for yr in recent_years:
        s = stats[yr]
        print(f"    {yr}: n={s['n']:>2} up={s['n_up']}/{s.get('up_win','?'):.0f}% dn={s['n_dn']}/{s.get('dn_win','?'):.0f}% NET={s['net']:+.1f}pp")

# ── HTML output ───────────────────────────────────────────────────────
era_data = {
    "labels": [e["label"] for e in era_compare],
    "live":   [e["live"]["net"]  for e in era_compare],
    "v34b":   [e["v34b"]["net"]  for e in era_compare],
}
year_data = {
    "labels": [y["year"] for y in yearly_compare],
    "live":   [y["live"]["net"]  for y in yearly_compare],
    "v34b":   [y["v34b"]["net"]  for y in yearly_compare],
    "delta":  [y["delta"]        for y in yearly_compare],
}

# Era table rows
era_rows = []
for e in era_compare:
    col = "#86efac" if e["delta"]>5 else ("#fbbf24" if e["delta"]>-1 else "#fca5a5")
    era_rows.append(f'''<tr style="border-bottom:1px solid #334155">
      <td style="padding:8px 10px;color:#e2e8f0;font-weight:700">{e['label']}</td>
      <td style="padding:8px 10px;text-align:right;color:#94a3b8">{e['live']['n']}</td>
      <td style="padding:8px 10px;text-align:right;color:#cbd5e1">{e['live']['up_w']:.0f}%</td>
      <td style="padding:8px 10px;text-align:right;color:#cbd5e1">{e['live']['dn_w']:.0f}%</td>
      <td style="padding:8px 10px;text-align:right;color:{'#86efac' if e['live']['net']>0 else '#fca5a5'};font-weight:600">{e['live']['net']:+.1f}pp</td>
      <td style="padding:8px 10px;text-align:right;color:#94a3b8">{e['v34b']['n']}</td>
      <td style="padding:8px 10px;text-align:right;color:#cbd5e1">{e['v34b']['up_w']:.0f}%</td>
      <td style="padding:8px 10px;text-align:right;color:#cbd5e1">{e['v34b']['dn_w']:.0f}%</td>
      <td style="padding:8px 10px;text-align:right;color:{'#86efac' if e['v34b']['net']>0 else '#fca5a5'};font-weight:600">{e['v34b']['net']:+.1f}pp</td>
      <td style="padding:8px 10px;text-align:right;background:{col};color:#0a0f1e;font-weight:800">{e['delta']:+.1f}pp</td>
    </tr>''')
era_tbody = "\n".join(era_rows)

year_rows = []
for y in yearly_compare:
    col = "#86efac" if y["delta"]>5 else ("#fbbf24" if y["delta"]>-1 else "#fca5a5")
    year_rows.append(f'''<tr style="border-bottom:1px solid #334155">
      <td style="padding:6px 10px;color:#cbd5e1;font-weight:600">{y['year']}</td>
      <td style="padding:6px 10px;text-align:right;color:#94a3b8">{y['live']['n']}</td>
      <td style="padding:6px 10px;text-align:right;color:#cbd5e1">{y['live'].get('up_win',0):.0f}%</td>
      <td style="padding:6px 10px;text-align:right;color:#cbd5e1">{y['live'].get('dn_win',0):.0f}%</td>
      <td style="padding:6px 10px;text-align:right;color:{'#86efac' if y['live']['net']>0 else '#fca5a5'}">{y['live']['net']:+.1f}pp</td>
      <td style="padding:6px 10px;text-align:right;color:#94a3b8">{y['v34b']['n']}</td>
      <td style="padding:6px 10px;text-align:right;color:#cbd5e1">{y['v34b'].get('up_win',0):.0f}%</td>
      <td style="padding:6px 10px;text-align:right;color:#cbd5e1">{y['v34b'].get('dn_win',0):.0f}%</td>
      <td style="padding:6px 10px;text-align:right;color:{'#86efac' if y['v34b']['net']>0 else '#fca5a5'}">{y['v34b']['net']:+.1f}pp</td>
      <td style="padding:6px 10px;text-align:right;background:{col};color:#0a0f1e;font-weight:800">{y['delta']:+.1f}pp</td>
    </tr>''')
year_tbody = "\n".join(year_rows)

html = f"""<!DOCTYPE html>
<html lang="vi"><head><meta charset="UTF-8">
<title>v3.4b vs LIVE Tinh Tế — Yearly success comparison</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* {{ box-sizing:border-box;margin:0;padding:0 }}
body {{ background:#0a0f1e;color:#e2e8f0;font-family:'Segoe UI',sans-serif;padding:20px }}
h1 {{ font-size:20px;color:#f8fafc;margin-bottom:4px }}
h2 {{ font-size:15px;color:#cbd5e1;margin:20px 0 10px }}
.subtitle {{ color:#64748b;font-size:13px;margin-bottom:16px }}
.panel {{ background:#0f172a;border:1px solid #334155;border-radius:8px;padding:14px;margin-bottom:16px }}
table {{ width:100%;border-collapse:collapse;font-size:12px }}
thead th {{ background:#0f172a;color:#64748b;font-size:10px;font-weight:700;
            text-transform:uppercase;letter-spacing:.5px;padding:8px 6px;
            border-bottom:2px solid #334155;text-align:left }}
.table-wrap {{ overflow-x:auto;border-radius:8px;border:1px solid #334155;background:#0f172a;margin-bottom:14px }}
.legend {{ background:#1e293b;border:1px solid #334155;border-radius:8px;padding:10px 14px;
           margin-bottom:14px;font-size:12px;color:#94a3b8 }}
.legend b {{ color:#e2e8f0 }}
canvas {{ background:#0a0f1e;border-radius:6px }}
</style></head><body>

<h1>⚖️ LIVE Tinh Tế vs v3.4b "Định Tâm" — Yearly success comparison</h1>
<p class="subtitle">Per-year + per-era NET edge T+20. Edge = win% − base rate VNINDEX cùng năm.</p>

<div class="legend">
  <b>Cách đọc</b>: NET edge dương = better than chance.
  Δ NET = v3.4b NET − LIVE NET. Δ &gt; +5pp = v3.4b vượt trội. Δ &lt; -1pp = LIVE tốt hơn.
</div>

<h2>🏛️ Era-level (5 kỷ nguyên)</h2>
<div class="table-wrap">
<table><thead><tr>
  <th>Era</th>
  <th colspan="4" style="border-left:2px solid #334155;text-align:center;color:#9ca3af">LIVE Tinh Tế</th>
  <th colspan="4" style="border-left:2px solid #334155;text-align:center;color:#a78bfa">v3.4b Định Tâm</th>
  <th rowspan="2" style="border-left:2px solid #334155;text-align:right">Δ NET</th>
</tr><tr>
  <th></th>
  <th style="border-left:2px solid #334155;text-align:right">n</th><th style="text-align:right">UP%</th><th style="text-align:right">DN%</th><th style="text-align:right">NET</th>
  <th style="border-left:2px solid #334155;text-align:right">n</th><th style="text-align:right">UP%</th><th style="text-align:right">DN%</th><th style="text-align:right">NET</th>
</tr></thead><tbody>{era_tbody}</tbody></table>
</div>

<h2>📊 Chart: NET edge per era</h2>
<div class="panel"><canvas id="chart_era" height="100"></canvas></div>

<h2>📅 Year-by-year side-by-side</h2>
<div class="table-wrap">
<table><thead><tr>
  <th>Năm</th>
  <th colspan="4" style="border-left:2px solid #334155;text-align:center;color:#9ca3af">LIVE Tinh Tế</th>
  <th colspan="4" style="border-left:2px solid #334155;text-align:center;color:#a78bfa">v3.4b Định Tâm</th>
  <th rowspan="2" style="border-left:2px solid #334155;text-align:right">Δ NET</th>
</tr><tr>
  <th></th>
  <th style="border-left:2px solid #334155;text-align:right">n</th><th style="text-align:right">UP%</th><th style="text-align:right">DN%</th><th style="text-align:right">NET</th>
  <th style="border-left:2px solid #334155;text-align:right">n</th><th style="text-align:right">UP%</th><th style="text-align:right">DN%</th><th style="text-align:right">NET</th>
</tr></thead><tbody>{year_tbody}</tbody></table>
</div>

<h2>📈 Chart: NET edge per year</h2>
<div class="panel"><canvas id="chart_year" height="140"></canvas></div>

<h2>📉 Chart: Δ NET per year (v3.4b - LIVE)</h2>
<div class="panel"><canvas id="chart_delta" height="100"></canvas></div>

<script>
const E = {json.dumps(era_data)};
const Y = {json.dumps(year_data)};
const baseOpt = {{
  responsive:true, maintainAspectRatio:false,
  plugins:{{ legend:{{ labels:{{ color:'#cbd5e1', font:{{size:11}} }} }} }},
  scales:{{
    x:{{ ticks:{{ color:'#64748b' }}, grid:{{color:'#1e293b'}} }},
    y:{{ ticks:{{ color:'#64748b', callback:v=>v+'pp' }}, grid:{{color:'#1e293b'}} }}
  }}
}};
new Chart(document.getElementById('chart_era'), {{
  type:'bar',
  data:{{ labels:E.labels, datasets:[
    {{label:'LIVE Tinh Tế', data:E.live, backgroundColor:'rgba(156,163,175,0.6)', borderColor:'#9ca3af', borderWidth:1}},
    {{label:'v3.4b Định Tâm', data:E.v34b, backgroundColor:'rgba(167,139,250,0.6)', borderColor:'#a78bfa', borderWidth:1}}
  ]}}, options: baseOpt
}});
new Chart(document.getElementById('chart_year'), {{
  type:'bar',
  data:{{ labels:Y.labels, datasets:[
    {{label:'LIVE Tinh Tế', data:Y.live, backgroundColor:'rgba(156,163,175,0.6)', borderColor:'#9ca3af', borderWidth:1}},
    {{label:'v3.4b Định Tâm', data:Y.v34b, backgroundColor:'rgba(167,139,250,0.6)', borderColor:'#a78bfa', borderWidth:1}}
  ]}}, options: baseOpt
}});
new Chart(document.getElementById('chart_delta'), {{
  type:'bar',
  data:{{ labels:Y.labels, datasets:[{{
    label:'Δ NET (v3.4b − LIVE)', data:Y.delta,
    backgroundColor: Y.delta.map(v => v>5?'rgba(34,197,94,0.7)':(v>-1?'rgba(251,191,36,0.6)':'rgba(239,68,68,0.7)')),
    borderColor:'#0a0f1e', borderWidth:1
  }}]}}, options: baseOpt
}});
</script>
</body></html>"""

out = os.path.join(WORKDIR, "vnindex_compare_v3_4b_vs_live_yearly.html")
with open(out, "w", encoding="utf-8") as f: f.write(html)
print(f"\n✓ Saved: {out}")
