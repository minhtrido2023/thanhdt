# -*- coding: utf-8 -*-
"""
build_v3_1_transitions_html.py
==============================
Generate the FULL transition-review HTML for **Tam Quan v3.1 (STAGING)**.

Mirrors the layout of `vnindex_transitions_v2.html` (built from the old
Cổ Điển baseline) but uses v3.1 inputs:

  • state series  → vnindex_5state_tam_quan_v3_1_full_history.csv
  • drivers       → vnindex_5state_dual_v3_full.csv
                     (Close, r_score_raw, r_score_ew, alpha, concentration_smooth)
  • US overlay    → vnindex_5state_tam_quan_v3_1_diag.csv
                     (spx_dd_1y, vix, us_cap, override_fired)

NAV is recomputed in-script with the canonical 5-state allocation
(0/20/70/100/130%) + costs (TC 0.1% per side, deposit 6%/yr on idle cash,
borrow 10%/yr on margin), single-path T+1 ramp 3 sessions.

Output: vnindex_transitions_v3_1.html
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}
STATE_WEIGHT = {1:0.0, 2:0.2, 3:0.7, 4:1.0, 5:1.3}
TC, DEP, BOR = 0.001, 0.06, 0.10
RAMP = 3

# ─────────────────────────────── 1. Load ───────────────────────────────
print("Loading v3.1 state series + drivers ...")
st = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_1_full_history.csv"))
st["time"] = pd.to_datetime(st["time"])
st = st.sort_values("time").reset_index(drop=True)

dr = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_dual_v3_full.csv"))
dr["time"] = pd.to_datetime(dr["time"])
dr = dr[["time","Close","r_score_raw","r_score_ew","alpha","concentration_smooth"]]

diag = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_1_diag.csv"))
diag["time"] = pd.to_datetime(diag["time"])
diag = diag[["time","spx_dd_1y","vix","us_cap","override_fired"]]

df = st.merge(dr, on="time", how="left").merge(diag, on="time", how="left")
n = len(df)
print(f"  {n} rows | {df['time'].iloc[0].date()} → {df['time'].iloc[-1].date()}")

# Effective dual r_score
df["r_dual"] = df["alpha"]*df["r_score_raw"] + (1-df["alpha"])*df["r_score_ew"]

# ─────────────────────────────── 2. NAV sim ───────────────────────────────
print("Simulating NAV ...")
close = df["Close"].values
ret   = np.zeros(n); ret[1:] = close[1:]/close[:-1] - 1
state = df["state"].values.astype(int)
target_w = np.array([STATE_WEIGHT[s] for s in state])

w  = np.zeros(n)        # actual weight in cổ phiếu
pv = np.zeros(n); pv[0] = 1e9
w[0] = target_w[0]
DAILY_DEP = (1+DEP)**(1/252) - 1
DAILY_BOR = (1+BOR)**(1/252) - 1

for t in range(1, n):
    # ramp: 3 sessions to reach new target if diff ≥ 3%, else snap
    tgt = target_w[t]
    diff = tgt - w[t-1]
    if abs(diff) < 0.03:
        w_new = tgt
    else:
        w_new = w[t-1] + diff/RAMP
    cash_w   = max(0.0, 1 - w_new)
    margin_w = max(0.0, w_new - 1)
    trade    = abs(w_new - w[t-1])
    daily_ret = w_new * ret[t] + cash_w*DAILY_DEP - margin_w*DAILY_BOR - trade*TC
    pv[t] = pv[t-1] * (1 + daily_ret)
    w[t]  = w_new

df["pv"] = pv
print(f"  final NAV: {pv[-1]/1e9:.2f} tỷ (×{pv[-1]/pv[0]:.2f})")

# ─────────────────────────────── 3. Collect transitions ───────────────────────────────
print("Collecting transitions ...")
trans = []
prev_s = int(state[0]); prev_dt = df["time"].iloc[0]
for i in range(1, n):
    s = int(state[i])
    if s != prev_s:
        cur_dt = df["time"].iloc[i]
        dur = (cur_dt - prev_dt).days
        r = df.iloc[i]
        # was override active in the few sessions around transition?
        win_start = max(0, i-2); win_end = min(n, i+1)
        fired_window = bool(df["override_fired"].iloc[win_start:win_end].any())
        trans.append({
            "from": STATE_NAMES[prev_s],
            "to":   STATE_NAMES[s],
            "to_s": s,
            "date": cur_dt,
            "dur":  dur,
            "close": float(r["Close"]),
            "nav":  float(r["pv"]) / 1e9,
            "r_raw":  None if pd.isna(r["r_score_raw"]) else float(r["r_score_raw"]),
            "r_ew":   None if pd.isna(r["r_score_ew"])  else float(r["r_score_ew"]),
            "alpha":  None if pd.isna(r["alpha"])       else float(r["alpha"]),
            "conc":   None if pd.isna(r["concentration_smooth"]) else float(r["concentration_smooth"]),
            "r_dual": None if pd.isna(r["r_dual"])      else float(r["r_dual"]),
            "vix":    None if pd.isna(r["vix"])         else float(r["vix"]),
            "spx_dd": None if pd.isna(r["spx_dd_1y"])   else float(r["spx_dd_1y"]),
            "us_cap": None if pd.isna(r["us_cap"])      else int(r["us_cap"]),
            "fired":  fired_window,
        })
        prev_s = s; prev_dt = cur_dt

total_trans = len(trans)
n_by_state  = {s: sum(1 for t in trans if t["to"] == STATE_NAMES[s]) for s in range(1,6)}
n_fired     = sum(1 for t in trans if t["fired"])
nav_peak    = max((t["nav"] for t in trans), default=1.0)
print(f"  {total_trans} transitions | {n_fired} với US-override active gần transition")

# ─────────────────────────────── 4. HTML helpers ───────────────────────────────
STATE_BG = {
    "CRISIS":  ("#7f1d1d", "#fca5a5"),
    "BEAR":    ("#7c2d12", "#fdba74"),
    "NEUTRAL": ("#1e293b", "#94a3b8"),
    "BULL":    ("#14532d", "#86efac"),
    "EX-BULL": ("#3b0764", "#c4b5fd"),
}
ALLOC = {
    "CRISIS":  ("100:0",   "#7f1d1d", "#fca5a5", ""),
    "BEAR":    ("80:20",   "#7c2d12", "#fdba74", ""),
    "NEUTRAL": ("30:70",   "#1e293b", "#94a3b8", ";border:1px solid #334155"),
    "BULL":    ("0:100",   "#14532d", "#86efac", ""),
    "EX-BULL": ("−30:130", "#3b0764", "#c4b5fd", ""),
}

def badge(s):
    bg, fg = STATE_BG.get(s, ("#334155","#94a3b8"))
    return f'<span style="background:{bg};color:{fg};padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700;white-space:nowrap">{s}</span>'

def alloc_td(s):
    lbl, bg, fg, brd = ALLOC.get(s, ("?","#1e293b","#94a3b8",""))
    return f'<td style="background:{bg};color:{fg};text-align:center;font-weight:700;font-size:12px;padding:4px 8px;white-space:nowrap{brd}">{lbl}</td>'

def rank_cell(r, lo_red=0.30, lo_yel=0.50, lo_grn=0.70):
    """Color a 0–1 value (rank / r_score) by quintile."""
    if r is None:
        return '<td style="padding:4px 6px;text-align:center;color:#64748b;font-size:11px">N/A</td>'
    if   r >= lo_grn: bg, fg = "#bbf7d0","#166534"
    elif r >= lo_yel: bg, fg = "#d1fae5","#065f46"
    elif r >= lo_red: bg, fg = "#fef9c3","#713f12"
    else:             bg, fg = "#fecaca","#991b1b"
    return f'<td style="background:{bg};color:{fg};text-align:center;font-weight:600;padding:4px 6px;font-size:11px">{r:.0%}</td>'

def arrow_dir(from_s, to_s):
    o = {"CRISIS":1,"BEAR":2,"NEUTRAL":3,"BULL":4,"EX-BULL":5}
    f, t = o.get(from_s,3), o.get(to_s,3)
    if t > f: return "▲","#16a34a","up"
    if t < f: return "▼","#dc2626","down"
    return "→","#64748b","same"

def reason(t):
    """Compose driver narrative."""
    bits = []
    if t["r_dual"] is not None:
        # classification bands (state_raw thresholds from build_dual_v3)
        rs = t["r_dual"]
        bits.append(f"r<sub>dual</sub>={rs:.0%} → {t['to']}")
    if t["alpha"] is not None and t["conc"] is not None:
        bits.append(f"α={t['alpha']:.2f}  conc={t['conc']:.2f}")
    if t["fired"]:
        if t["us_cap"] is not None and t["us_cap"] < 5:
            cap_name = STATE_NAMES.get(t["us_cap"], "?")
            us_bits = []
            if t["spx_dd"] is not None: us_bits.append(f"SPX_DD={t['spx_dd']*100:+.0f}%")
            if t["vix"]    is not None: us_bits.append(f"VIX={t['vix']:.0f}")
            bits.append(f"<span style='color:#fb7185;font-weight:700'>US-override cap≤{cap_name}</span> ({', '.join(us_bits)})")
    elif t["us_cap"] is not None and t["us_cap"] < 5:
        bits.append(f"<span style='color:#94a3b8'>US calm cap={STATE_NAMES.get(t['us_cap'],'?')}</span>")
    return "<br>".join(bits) if bits else "—"

def fmt_pct(v, prec=0):
    if v is None: return "N/A"
    return f"{v*100:+.{prec}f}%" if prec else f"{v*100:+.0f}%"

# ─────────────────────────────── 5. Build rows ───────────────────────────────
rows = []
for idx, t in enumerate(trans):
    arrow, a_col, dir_cls = arrow_dir(t["from"], t["to"])
    row_bg = "#1e293b" if idx % 2 == 0 else "#0f172a"
    bar_w  = max(2, int(min(t["nav"]/nav_peak, 1.0) * 120))

    rs = t["r_dual"]
    if rs is None:   rs_bg, rs_fg, rs_str = "#374151","#e5e7eb","N/A"
    elif rs < 0.10:  rs_bg, rs_fg, rs_str = "#dc2626","#fff",f"{rs:.0%}"
    elif rs < 0.20:  rs_bg, rs_fg, rs_str = "#ea580c","#fff",f"{rs:.0%}"
    elif rs < 0.55:  rs_bg, rs_fg, rs_str = "#374151","#e5e7eb",f"{rs:.0%}"
    elif rs < 0.75:  rs_bg, rs_fg, rs_str = "#16a34a","#fff",f"{rs:.0%}"
    else:            rs_bg, rs_fg, rs_str = "#7c3aed","#fff",f"{rs:.0%}"

    # US cap badge
    if t["us_cap"] is None or t["us_cap"] >= 5:
        us_cap_html = '<td style="padding:4px 6px;text-align:center;color:#64748b;font-size:11px">—</td>'
    else:
        cap_name = STATE_NAMES.get(t["us_cap"], "?")
        bg, fg = STATE_BG.get(cap_name, ("#334155","#94a3b8"))
        us_cap_html = f'<td style="background:{bg};color:{fg};text-align:center;font-weight:700;padding:4px 6px;font-size:11px">≤{cap_name[:3]}</td>'

    fire_html = ('<td style="text-align:center;padding:4px 6px"><span style="background:#dc2626;color:#fff;padding:2px 6px;border-radius:8px;font-size:10px;font-weight:700">FIRED</span></td>'
                 if t["fired"] else
                 '<td style="text-align:center;padding:4px 6px;color:#475569;font-size:10px">—</td>')

    rows.append(f'''<tr style="background:{row_bg};border-bottom:1px solid #334155"
            data-from="{t['from']}" data-to="{t['to']}" data-date="{t['date'].strftime('%Y-%m-%d')}" data-dir="{dir_cls}" data-fired="{int(t['fired'])}">
      <td style="padding:5px 8px;font-size:12px;color:#94a3b8;white-space:nowrap">{t['date'].strftime('%Y-%m-%d')}</td>
      <td style="padding:5px 8px;text-align:center">{badge(t['from'])}</td>
      <td style="padding:5px 4px;text-align:center;font-size:16px;color:{a_col}">{arrow}</td>
      <td style="padding:5px 8px;text-align:center">{badge(t['to'])}</td>
      <td style="padding:5px 8px;text-align:center;color:#64748b;font-size:11px">{t['dur']}d</td>
      <td style="padding:5px 8px;text-align:right;color:#e2e8f0;font-size:12px">{t['close']:.1f}</td>
      <td style="padding:4px 8px;white-space:nowrap">
            <div style="font-size:12px;font-weight:700;color:#f8fafc">{t['nav']:.2f} t&#7927;</div>
            <div style="height:4px;width:{bar_w}px;background:#3b82f6;border-radius:2px;margin-top:2px"></div>
        </td>
      {alloc_td(t['to'])}
      {rank_cell(t['r_raw'])}
      {rank_cell(t['r_ew'])}
      <td style="padding:4px 6px;text-align:center;color:#cbd5e1;font-size:11px">{"N/A" if t['alpha'] is None else f"{t['alpha']:.2f}"}</td>
      <td style="padding:4px 6px;text-align:center;color:#cbd5e1;font-size:11px">{"N/A" if t['conc'] is None else f"{t['conc']:.2f}"}</td>
      <td style="background:{rs_bg};color:{rs_fg};text-align:center;font-weight:800;padding:4px 8px">{rs_str}</td>
      <td style="padding:4px 6px;text-align:center;color:#94a3b8;font-size:11px">{"N/A" if t['vix'] is None else f"{t['vix']:.0f}"}</td>
      <td style="padding:4px 6px;text-align:center;color:#94a3b8;font-size:11px">{"N/A" if t['spx_dd'] is None else f"{t['spx_dd']*100:+.0f}%"}</td>
      {us_cap_html}
      {fire_html}
      <td style="padding:4px 10px;color:#cbd5e1;font-size:11px;max-width:260px">{reason(t)}</td>
    </tr>''')

tbody_html = "\n".join(rows)

# ─────────────────────────────── 6. Stat cards + page ───────────────────────────────
stat_colors = {1:"#dc2626",2:"#f97316",3:"#9ca3af",4:"#16a34a",5:"#7c3aed"}
stat_cards = f'<div class="stat-card"><div class="num" style="color:#e2e8f0">{total_trans}</div><div class="lbl">T&#7893;ng chuy&#7875;n &#273;&#7893;i</div></div>'
for s in range(1, 6):
    stat_cards += f'<div class="stat-card"><div class="num" style="color:{stat_colors[s]}">{n_by_state[s]}</div><div class="lbl">&#8594; {STATE_NAMES[s]}</div></div>'
stat_cards += f'<div class="stat-card"><div class="num" style="color:#fb7185">{n_fired}</div><div class="lbl">US-override fired</div></div>'
stat_cards += f'<div class="stat-card"><div class="num" style="color:#3b82f6">{nav_peak:.1f} t&#7927;</div><div class="lbl">NAV &#273;&#7881;nh</div></div>'

year_range = f"{df['time'].iloc[0].year}&#8211;{df['time'].iloc[-1].year}"

html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Tam Quan v3.1 &middot; Chuy&#7875;n &#272;&#7893;i Tr&#7841;ng Th&#225;i (STAGING)</title>
<style>
* {{ box-sizing:border-box;margin:0;padding:0 }}
body {{ background:#0a0f1e;color:#e2e8f0;font-family:'Segoe UI',sans-serif;padding:20px }}
h1 {{ font-size:20px;color:#f8fafc;margin-bottom:4px }}
.subtitle {{ color:#64748b;font-size:13px;margin-bottom:16px }}
.staging-tag {{ background:#7c3aed;color:#fff;padding:2px 10px;border-radius:6px;font-size:11px;font-weight:700;margin-left:8px }}
.stats {{ display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px }}
.stat-card {{ background:#1e293b;border-radius:8px;padding:10px 16px;border:1px solid #334155 }}
.stat-card .num {{ font-size:22px;font-weight:800 }}
.stat-card .lbl {{ font-size:11px;color:#64748b }}
.controls {{ display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px;align-items:center }}
input[type=text] {{ background:#1e293b;border:1px solid #334155;color:#e2e8f0;
                    padding:6px 12px;border-radius:6px;font-size:13px;width:200px }}
.filter-btn {{ background:#1e293b;border:1px solid #334155;color:#94a3b8;
               padding:5px 12px;border-radius:6px;cursor:pointer;font-size:12px }}
.filter-btn.active {{ border-color:#60a5fa;color:#60a5fa;background:#1e3a5f }}
.filter-btn.crisis-btn.active  {{ border-color:#dc2626;color:#dc2626;background:#3b0d0d }}
.filter-btn.bear-btn.active    {{ border-color:#f97316;color:#f97316;background:#3b1a08 }}
.filter-btn.neutral-btn.active {{ border-color:#9ca3af;color:#d1d5db;background:#1f2937 }}
.filter-btn.bull-btn.active    {{ border-color:#16a34a;color:#16a34a;background:#052e16 }}
.filter-btn.exbull-btn.active  {{ border-color:#7c3aed;color:#a78bfa;background:#2e1065 }}
.filter-btn.down-btn.active    {{ border-color:#dc2626;color:#f87171;background:#3b0d0d }}
.filter-btn.up-btn.active      {{ border-color:#16a34a;color:#4ade80;background:#052e16 }}
.filter-btn.fired-btn.active   {{ border-color:#fb7185;color:#fb7185;background:#3b0d0d }}
.table-wrap {{ overflow-x:auto;max-height:76vh;overflow-y:auto;border-radius:8px;border:1px solid #334155 }}
table {{ width:100%;border-collapse:collapse;font-size:12px }}
thead th {{ background:#0f172a;color:#64748b;font-size:10px;font-weight:700;
            text-transform:uppercase;letter-spacing:.5px;padding:8px 6px;
            position:sticky;top:0;z-index:10;border-bottom:2px solid #334155;white-space:nowrap }}
tr:hover td {{ background:rgba(96,165,250,0.07)!important }}
.hidden {{ display:none!important }}
#count-info {{ color:#64748b;font-size:12px }}
.legend {{ background:#1e293b;border:1px solid #334155;border-radius:8px;padding:10px 14px;
           margin-bottom:14px;font-size:12px;color:#94a3b8 }}
.legend b {{ color:#e2e8f0 }}
.legend code {{ background:#0f172a;color:#86efac;padding:1px 6px;border-radius:4px;font-size:11px }}
</style>
</head>
<body>
<h1>&#128260; Tam Quan v3.1 &middot; Chuy&#7875;n &#272;&#7893;i Tr&#7841;ng Th&#225;i<span class="staging-tag">STAGING</span></h1>
<p class="subtitle">{total_trans} l&#7847;n chuy&#7875;n &#273;&#7893;i &middot; {year_range} &middot; V&#7889;n ban &#273;&#7847;u: 1 t&#7927; &#273;&#7891;ng &middot; {n_fired} transition c&#243; US-override active</p>

<div class="stats">
  {stat_cards}
</div>

<div class="legend">
  <b>Tam Quan v3.1 = v3 dual-blend + US shock override</b>. Dual r-score: <code>r_dual = &alpha;&middot;r_raw + (1-&alpha;)&middot;r_ew</code>,
  v&#7899;i <code>&alpha; = clip(1 - 2&middot;max(0, conc-0.5), [0.3, 1])</code>. Concentration cao &rArr; EW chi&#7871;m tr&#7885;ng s&#7889; l&#7899;n h&#417;n
  (b&#7843;o v&#7879; tr&#432;&#7899;c VIC-led illusion). US override cap state khi:
  Tier&nbsp;3 (&le;CRISIS) SPX_DD_1Y &lt; -25% ho&#7863;c VIX &gt; 35 &middot;
  Tier&nbsp;2 (&le;BEAR) -15% ho&#7863;c VIX &gt; 30 &middot;
  Tier&nbsp;1 (&le;NEUTRAL) -10% ho&#7863;c VIX &gt; 25. T&#7881; tr&#7885;ng m&#7909;c ti&#234;u:
  CRISIS 0% &middot; BEAR 20% &middot; NEUTRAL 70% &middot; BULL 100% &middot; EX-BULL 130%.
</div>

<div class="controls">
  <input type="text" id="search" placeholder="T&#236;m ng&#224;y / tr&#7841;ng th&#225;i&#8230;" oninput="applyFilters()">
  <button class="filter-btn active" id="btn-all" onclick="setFilter('all')">T&#7845;t c&#7843;</button>
  <button class="filter-btn down-btn" id="btn-down" onclick="setFilter('down')">&#9660; Xu&#7889;ng c&#7845;p</button>
  <button class="filter-btn up-btn" id="btn-up" onclick="setFilter('up')">&#9650; L&#234;n c&#7845;p</button>
  <button class="filter-btn crisis-btn" id="btn-crisis" onclick="setFilter('CRISIS')">CRISIS</button>
  <button class="filter-btn bear-btn" id="btn-bear" onclick="setFilter('BEAR')">BEAR</button>
  <button class="filter-btn neutral-btn" id="btn-neutral" onclick="setFilter('NEUTRAL')">NEUTRAL</button>
  <button class="filter-btn bull-btn" id="btn-bull" onclick="setFilter('BULL')">BULL</button>
  <button class="filter-btn exbull-btn" id="btn-exbull" onclick="setFilter('EX-BULL')">EX-BULL</button>
  <button class="filter-btn fired-btn" id="btn-fired" onclick="setFilter('fired')">&#128293; US-Override</button>
  <span id="count-info"></span>
</div>

<div class="table-wrap">
<table>
<thead>
<tr>
  <th>Ng&#224;y</th>
  <th>T&#7915;</th>
  <th></th>
  <th>Sang</th>
  <th title="S&#7889; ng&#224;y tr&#7841;ng th&#225;i tr&#432;&#7899;c t&#7891;n t&#7841;i">Dur</th>
  <th>VNINDEX</th>
  <th>NAV (t&#7927;)</th>
  <th>Ti&#7873;n:CP</th>
  <th title="r_score raw (concentrated)">r_raw</th>
  <th title="r_score equal-weight">r_ew</th>
  <th title="Tr&#7885;ng s&#7889; raw vs EW">&alpha;</th>
  <th title="Concentration score (smoothed)">conc</th>
  <th title="r_dual = &alpha;&middot;r_raw + (1-&alpha;)&middot;r_ew">r_dual &#9733;</th>
  <th title="VIX (US fear index)">VIX</th>
  <th title="SPX drawdown 1Y">SPX DD</th>
  <th title="US shock cap level">US cap</th>
  <th title="Override active g&#7847;n ng&#224;y chuy&#7875;n">Override</th>
  <th>L&yacute; do &amp; Drivers</th>
</tr>
</thead>
<tbody id="tbody">
{tbody_html}
</tbody>
</table>
</div>

<script>
let currentFilter = 'all';
function setFilter(f) {{
  currentFilter = f;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  const map = {{'all':'btn-all','down':'btn-down','up':'btn-up',
                'CRISIS':'btn-crisis','BEAR':'btn-bear','NEUTRAL':'btn-neutral',
                'BULL':'btn-bull','EX-BULL':'btn-exbull','fired':'btn-fired'}};
  if(map[f]) document.getElementById(map[f]).classList.add('active');
  applyFilters();
}}
function applyFilters() {{
  const q = document.getElementById('search').value.toLowerCase();
  let vis = 0;
  document.querySelectorAll('#tbody tr').forEach(r => {{
    const from = r.dataset.from || '', to = r.dataset.to || '',
          date = r.dataset.date || '', dir = r.dataset.dir || '',
          fired = r.dataset.fired === '1';
    let show = true;
    if(currentFilter === 'down')      show = dir === 'down';
    else if(currentFilter === 'up')   show = dir === 'up';
    else if(currentFilter === 'fired')show = fired;
    else if(currentFilter !== 'all')  show = (to === currentFilter);
    if(q) show = show && (date.includes(q) || from.toLowerCase().includes(q) || to.toLowerCase().includes(q));
    r.classList.toggle('hidden', !show);
    if(show) vis++;
  }});
  document.getElementById('count-info').textContent = vis + ' k&#7871;t qu&#7843;';
}}
applyFilters();
</script>
</body>
</html>"""

out_path = os.path.join(WORKDIR, "vnindex_transitions_v3_1.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"\n✓ Saved: {out_path}")
print(f"  {total_trans} transitions • {n_fired} với US-override • NAV ×{pv[-1]/pv[0]:.2f}")
