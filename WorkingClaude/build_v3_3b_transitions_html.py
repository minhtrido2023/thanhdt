# -*- coding: utf-8 -*-
"""
build_v3_3b_transitions_html.py
===============================
Transitions table for Tam Quan v3.3b "Cẩn Thận" (STAGING NEXT candidate).

Same layout as v3.1 version + 3 new columns specific to v3.3b:
  • RSI(14) at trigger
  • Concentration at trigger
  • Gate status: 🛡 GATE-BLOCKED (v3.1 wanted downgrade, v3.3b held)
                 ✓ ALLOWED  (downgrade passed conc filter or no fire)

Output: vnindex_transitions_v3_3b.html
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}
STATE_WEIGHT = {1:0.0, 2:0.2, 3:0.7, 4:1.0, 5:1.3}
TC, DEP, BOR = 0.001, 0.06, 0.10
RAMP = 3
RSI_THR = 55
CONC_THR = 0.55

# ── Load ────────────────────────────────────────────────────────────────
st = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_3b_full_history.csv"))
st["time"] = pd.to_datetime(st["time"]); st = st.sort_values("time").reset_index(drop=True)

v31 = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_1_full_history.csv"))
v31["time"] = pd.to_datetime(v31["time"])
v31 = v31[["time","state"]].rename(columns={"state":"state_v31"})

dr = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_dual_v3_full.csv"))
dr["time"] = pd.to_datetime(dr["time"])
dr = dr[["time","Close","r_score_raw","r_score_ew","alpha","concentration_smooth"]]

diag = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_1_diag.csv"))
diag["time"] = pd.to_datetime(diag["time"])
diag = diag[["time","spx_dd_1y","vix","us_cap","override_fired"]]

df = st.merge(v31, on="time", how="left").merge(dr, on="time", how="left").merge(diag, on="time", how="left")

# RSI(14)
def rsi14(c):
    delta = np.diff(c, prepend=c[0])
    up   = np.where(delta>0, delta, 0.0); down = np.where(delta<0, -delta, 0.0)
    out = np.full(len(c), np.nan)
    for i in range(14, len(c)):
        gain = up[i-13:i+1].mean(); loss = down[i-13:i+1].mean()
        rs = gain/loss if loss>0 else 100; out[i] = 100 - 100/(1+rs)
    return out
df["rsi14"] = rsi14(df["Close"].values)
df["r_dual"] = df["alpha"]*df["r_score_raw"] + (1-df["alpha"])*df["r_score_ew"]

n = len(df); close = df["Close"].values
state    = df["state"].values.astype(int)
state_v31 = df["state_v31"].values.astype(int)
rsi      = df["rsi14"].values
conc     = df["concentration_smooth"].values

print(f"Loaded {n} rows | {df['time'].iloc[0].date()} → {df['time'].iloc[-1].date()}")

# ── NAV sim (same as v3.1 transitions script) ───────────────────────────
ret = np.zeros(n); ret[1:] = close[1:]/close[:-1] - 1
target_w = np.array([STATE_WEIGHT[s] for s in state])
w = np.zeros(n); pv = np.zeros(n); pv[0] = 1e9; w[0] = target_w[0]
DAILY_DEP = (1+DEP)**(1/252)-1; DAILY_BOR = (1+BOR)**(1/252)-1
for t in range(1, n):
    tgt = target_w[t]; diff = tgt - w[t-1]
    w_new = tgt if abs(diff)<0.03 else w[t-1] + diff/RAMP
    cash_w = max(0.0, 1-w_new); margin_w = max(0.0, w_new-1)
    trade = abs(w_new - w[t-1])
    daily_ret = w_new*ret[t] + cash_w*DAILY_DEP - margin_w*DAILY_BOR - trade*TC
    pv[t] = pv[t-1]*(1+daily_ret); w[t] = w_new
df["pv"] = pv

# ── Collect transitions + classify gate behavior ────────────────────────
trans = []
prev_s = state[0]; prev_dt = df["time"].iloc[0]
for i in range(1, n):
    s = state[i]
    if s != prev_s:
        cur_dt = df["time"].iloc[i]; r = df.iloc[i]
        # Gate behavior: did v3.1 want a different state here?
        v31_step = state_v31[i] - state_v31[i-1]  # what v3.1 did
        our_step = s - prev_s
        gate_status = "allowed"
        if our_step != v31_step:
            # v3.3b diverged from v3.1
            if v31_step < 0 and our_step >= 0:
                gate_status = "blocked_dn"   # v3.3b held when v3.1 wanted down
            elif our_step < 0 and v31_step >= 0:
                gate_status = "release"      # gate released — caught up to v3.1
        trans.append({
            "from":  STATE_NAMES[prev_s], "to": STATE_NAMES[s], "to_s": s,
            "date":  cur_dt, "dur": (cur_dt - prev_dt).days,
            "close": float(close[i]), "nav": float(pv[i])/1e9,
            "r_raw":  None if pd.isna(r["r_score_raw"]) else float(r["r_score_raw"]),
            "r_ew":   None if pd.isna(r["r_score_ew"])  else float(r["r_score_ew"]),
            "alpha":  None if pd.isna(r["alpha"])       else float(r["alpha"]),
            "conc":   None if pd.isna(r["concentration_smooth"]) else float(r["concentration_smooth"]),
            "r_dual": None if pd.isna(r["r_dual"])      else float(r["r_dual"]),
            "rsi":    None if pd.isna(r["rsi14"])       else float(r["rsi14"]),
            "vix":    None if pd.isna(r["vix"])         else float(r["vix"]),
            "spx_dd": None if pd.isna(r["spx_dd_1y"])   else float(r["spx_dd_1y"]),
            "us_cap": None if pd.isna(r["us_cap"])      else int(r["us_cap"]),
            "fired_window": bool(df["override_fired"].iloc[max(0,i-2):i+1].any()),
            "gate_status": gate_status,
        })
        prev_s = s; prev_dt = cur_dt

# Count "gate-fire" days: where state > state_v31 (we are higher than v3.1 today)
gate_days = int((state > state_v31).sum())
n_blocks = sum(1 for t in trans if t["gate_status"] == "blocked_dn")
n_releases = sum(1 for t in trans if t["gate_status"] == "release")

total_trans = len(trans)
n_by_state  = {s: sum(1 for t in trans if t["to"] == STATE_NAMES[s]) for s in range(1,6)}
n_fired_us  = sum(1 for t in trans if t["fired_window"])
nav_peak    = max((t["nav"] for t in trans), default=1.0)
print(f"  {total_trans} transitions | {gate_days} elevated-state days | {n_blocks} gate blocks | {n_releases} gate releases")

# ── HTML helpers ────────────────────────────────────────────────────────
STATE_BG = {
    "CRISIS":  ("#7f1d1d","#fca5a5"), "BEAR": ("#7c2d12","#fdba74"),
    "NEUTRAL": ("#1e293b","#94a3b8"), "BULL": ("#14532d","#86efac"),
    "EX-BULL": ("#3b0764","#c4b5fd"),
}
ALLOC = {
    "CRISIS":  ("100:0",   "#7f1d1d","#fca5a5",""),
    "BEAR":    ("80:20",   "#7c2d12","#fdba74",""),
    "NEUTRAL": ("30:70",   "#1e293b","#94a3b8",";border:1px solid #334155"),
    "BULL":    ("0:100",   "#14532d","#86efac",""),
    "EX-BULL": ("−30:130", "#3b0764","#c4b5fd",""),
}
def badge(s):
    bg,fg = STATE_BG.get(s,("#334155","#94a3b8"))
    return f'<span style="background:{bg};color:{fg};padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700;white-space:nowrap">{s}</span>'
def alloc_td(s):
    lbl, bg, fg, brd = ALLOC.get(s, ("?","#1e293b","#94a3b8",""))
    return f'<td style="background:{bg};color:{fg};text-align:center;font-weight:700;font-size:12px;padding:4px 8px;white-space:nowrap{brd}">{lbl}</td>'
def rank_cell(r, lo_red=0.30, lo_yel=0.50, lo_grn=0.70):
    if r is None: return '<td style="padding:4px 6px;text-align:center;color:#64748b;font-size:11px">N/A</td>'
    if   r >= lo_grn: bg, fg = "#bbf7d0","#166534"
    elif r >= 0.55:   bg, fg = "#d1fae5","#065f46"
    elif r >= lo_red: bg, fg = "#fef9c3","#713f12"
    else:             bg, fg = "#fecaca","#991b1b"
    return f'<td style="background:{bg};color:{fg};text-align:center;font-weight:600;padding:4px 6px;font-size:11px">{r:.0%}</td>'
def arrow_dir(from_s, to_s):
    o = {"CRISIS":1,"BEAR":2,"NEUTRAL":3,"BULL":4,"EX-BULL":5}
    f, t = o.get(from_s,3), o.get(to_s,3)
    if t > f: return "▲","#16a34a","up"
    if t < f: return "▼","#dc2626","down"
    return "→","#64748b","same"

def gate_cell(s):
    if s == "blocked_dn":
        return '<td style="background:#7c3aed;color:#fff;text-align:center;padding:4px 6px;font-size:10px;font-weight:700">🛡 BLOCK</td>'
    elif s == "release":
        return '<td style="background:#0ea5e9;color:#fff;text-align:center;padding:4px 6px;font-size:10px;font-weight:700">⤓ RELEASE</td>'
    else:
        return '<td style="color:#475569;text-align:center;font-size:10px">—</td>'

def reason(t):
    bits = []
    if t["r_dual"] is not None:
        bits.append(f"r<sub>dual</sub>={t['r_dual']:.0%}")
    if t["rsi"] is not None:
        col = "#fca5a5" if t["rsi"] >= RSI_THR else "#86efac"
        bits.append(f"<span style='color:{col}'>RSI={t['rsi']:.0f}</span>")
    if t["conc"] is not None:
        col = "#fca5a5" if t["conc"] > CONC_THR else "#86efac"
        bits.append(f"<span style='color:{col}'>conc={t['conc']:.2f}</span>")
    if t["fired_window"] and t["us_cap"] is not None and t["us_cap"] < 5:
        cap_name = STATE_NAMES.get(t["us_cap"], "?")
        bits.append(f"<span style='color:#fb7185;font-weight:700'>US-cap≤{cap_name}</span>")
    if t["gate_status"] == "blocked_dn":
        bits.append("<span style='color:#a78bfa;font-weight:700'>Gate blocked v3.1 downgrade</span>")
    elif t["gate_status"] == "release":
        bits.append("<span style='color:#0ea5e9;font-weight:700'>Gate released → catch up</span>")
    return "<br>".join(bits) if bits else "—"

# ── Build rows ──────────────────────────────────────────────────────────
rows = []
for idx, t in enumerate(trans):
    arrow, a_col, dir_cls = arrow_dir(t["from"], t["to"])
    row_bg = "#1e293b" if idx % 2 == 0 else "#0f172a"
    if t["gate_status"] != "allowed":
        row_bg = "#2e1065" if t["gate_status"] == "blocked_dn" else "#082f49"
    bar_w  = max(2, int(min(t["nav"]/nav_peak, 1.0) * 120))

    rs = t["r_dual"]
    if rs is None:   rs_bg, rs_fg, rs_str = "#374151","#e5e7eb","N/A"
    elif rs < 0.10:  rs_bg, rs_fg, rs_str = "#dc2626","#fff",f"{rs:.0%}"
    elif rs < 0.20:  rs_bg, rs_fg, rs_str = "#ea580c","#fff",f"{rs:.0%}"
    elif rs < 0.55:  rs_bg, rs_fg, rs_str = "#374151","#e5e7eb",f"{rs:.0%}"
    elif rs < 0.75:  rs_bg, rs_fg, rs_str = "#16a34a","#fff",f"{rs:.0%}"
    else:            rs_bg, rs_fg, rs_str = "#7c3aed","#fff",f"{rs:.0%}"

    rsi_cell = ('<td style="padding:4px 6px;text-align:center;color:#64748b;font-size:11px">N/A</td>'
                if t["rsi"] is None else
                f'<td style="padding:4px 6px;text-align:center;font-size:11px;'
                f'color:{"#fca5a5" if t["rsi"]>=RSI_THR else "#86efac"};font-weight:600">{t["rsi"]:.0f}</td>')

    conc_cell = ('<td style="padding:4px 6px;text-align:center;color:#64748b;font-size:11px">N/A</td>'
                 if t["conc"] is None else
                 f'<td style="padding:4px 6px;text-align:center;font-size:11px;'
                 f'color:{"#fca5a5" if t["conc"]>CONC_THR else "#cbd5e1"};font-weight:600">{t["conc"]:.2f}</td>')

    rows.append(f'''<tr style="background:{row_bg};border-bottom:1px solid #334155"
            data-from="{t['from']}" data-to="{t['to']}" data-date="{t['date'].strftime('%Y-%m-%d')}" data-dir="{dir_cls}" data-gate="{t['gate_status']}">
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
      {rsi_cell}
      {conc_cell}
      <td style="background:{rs_bg};color:{rs_fg};text-align:center;font-weight:800;padding:4px 8px">{rs_str}</td>
      {gate_cell(t['gate_status'])}
      <td style="padding:4px 10px;color:#cbd5e1;font-size:11px;max-width:280px">{reason(t)}</td>
    </tr>''')
tbody_html = "\n".join(rows)

# Stat cards
stat_colors = {1:"#dc2626",2:"#f97316",3:"#9ca3af",4:"#16a34a",5:"#7c3aed"}
stat_cards = f'<div class="stat-card"><div class="num" style="color:#e2e8f0">{total_trans}</div><div class="lbl">T&#7893;ng chuy&#7875;n &#273;&#7893;i</div></div>'
for s in range(1, 6):
    stat_cards += f'<div class="stat-card"><div class="num" style="color:{stat_colors[s]}">{n_by_state[s]}</div><div class="lbl">&#8594; {STATE_NAMES[s]}</div></div>'
stat_cards += f'<div class="stat-card"><div class="num" style="color:#a78bfa">{n_blocks}</div><div class="lbl">🛡 Gate BLOCK</div></div>'
stat_cards += f'<div class="stat-card"><div class="num" style="color:#0ea5e9">{n_releases}</div><div class="lbl">⤓ Gate RELEASE</div></div>'
stat_cards += f'<div class="stat-card"><div class="num" style="color:#3b82f6">{nav_peak:.1f} t&#7927;</div><div class="lbl">NAV &#273;&#7881;nh</div></div>'

year_range = f"{df['time'].iloc[0].year}&#8211;{df['time'].iloc[-1].year}"

html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Tam Quan v3.3b &middot; Chuy&#7875;n &#272;&#7893;i Tr&#7841;ng Th&#225;i (STAGING NEXT)</title>
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
.filter-btn.gate-btn.active   {{ border-color:#a78bfa;color:#a78bfa;background:#2e1065 }}
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
<h1>&#129534; Tam Quan v3.3b &middot; "C&#7849;n Th&#7853;n"<span class="staging-tag">STAGING NEXT</span></h1>
<p class="subtitle">{total_trans} l&#7847;n chuy&#7875;n &#273;&#7893;i &middot; {year_range} &middot; V&#7889;n ban &#273;&#7847;u: 1 t&#7927; &#273;&#7891;ng
&middot; Gate fire {n_blocks} l&#7847;n &middot; {gate_days} ng&#224;y elevated state vs v3.1</p>

<div class="stats">{stat_cards}</div>

<div class="legend">
  <b>v3.3b = v3.1 + RSI gate + Concentration filter.</b><br>
  <b>RSI gate</b>: khi v3.1 fire 1-step downgrade v&#224; RSI(14) &ge; 55 (momentum v&#7851;n l&#234;n), gi&#7919; state cao h&#417;n.<br>
  <b>Conc filter</b>: ch&#7881; fire gate khi concentration &le; 0.55 (broad market). N&#7871;u narrow/VIC-led &rArr; cho downgrade qua (b&#7843;o v&#7879;).<br>
  <b>Release conditions</b>: RSI &lt; 55, ho&#7863;c state h&#7891;i ph&#7909;c v&#7873; m&#7913;c bi&#7873;u block, ho&#7863;c v3.1 fire 2-step downgrade (real bear signal).<br>
  <b>Backtest V11 12y</b>: <code>CAGR +1.04pp / Sharpe +0.09 / MaxDD -3.77pp / Calmar +0.24 / Wealth +0.85x</code>
  vs v3.1. OOS 2022-26: <code>+0.85pp CAGR</code>. Walk-forward validated (plateau threshold [0.40-0.70]).
</div>

<div class="controls">
  <input type="text" id="search" placeholder="T&#236;m ng&#224;y / tr&#7841;ng th&#225;i&#8230;" oninput="applyFilters()">
  <button class="filter-btn active" id="btn-all" onclick="setFilter('all')">T&#7845;t c&#7843;</button>
  <button class="filter-btn" id="btn-down" onclick="setFilter('down')">&#9660; Xu&#7889;ng c&#7845;p</button>
  <button class="filter-btn" id="btn-up"   onclick="setFilter('up')">&#9650; L&#234;n c&#7845;p</button>
  <button class="filter-btn gate-btn" id="btn-gate" onclick="setFilter('gate')">&#128737; Gate BLOCK</button>
  <button class="filter-btn" id="btn-release" onclick="setFilter('release')">&#8675; Gate RELEASE</button>
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
  <th>Dur</th>
  <th>VNINDEX</th>
  <th>NAV (t&#7927;)</th>
  <th>Ti&#7873;n:CP</th>
  <th title="RSI(14) Wilder, &ge;55 b&#7853;t gate">RSI</th>
  <th title="Concentration smoothed, &gt;0.55 v&#244; hi&#7879;u gate">conc</th>
  <th title="r_dual = α·r_raw + (1-α)·r_ew">r_dual &#9733;</th>
  <th>Gate</th>
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
  const map = {{'all':'btn-all','down':'btn-down','up':'btn-up','gate':'btn-gate','release':'btn-release'}};
  if(map[f]) document.getElementById(map[f]).classList.add('active');
  applyFilters();
}}
function applyFilters() {{
  const q = document.getElementById('search').value.toLowerCase();
  let vis = 0;
  document.querySelectorAll('#tbody tr').forEach(r => {{
    const from = r.dataset.from || '', to = r.dataset.to || '',
          date = r.dataset.date || '', dir = r.dataset.dir || '',
          gate = r.dataset.gate || '';
    let show = true;
    if(currentFilter === 'down') show = dir === 'down';
    else if(currentFilter === 'up') show = dir === 'up';
    else if(currentFilter === 'gate') show = gate === 'blocked_dn';
    else if(currentFilter === 'release') show = gate === 'release';
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

out_path = os.path.join(WORKDIR, "vnindex_transitions_v3_3b.html")
with open(out_path, "w", encoding="utf-8") as f: f.write(html)
print(f"\n✓ Saved: {out_path}")
print(f"  {total_trans} transitions • {n_blocks} gate blocks • {n_releases} gate releases • NAV ×{pv[-1]/pv[0]:.2f}")
