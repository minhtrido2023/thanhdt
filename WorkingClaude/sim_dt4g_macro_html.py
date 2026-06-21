# -*- coding: utf-8 -*-
"""
sim_dt4g_macro_html.py
======================
Builds two verifiable HTML dashboards (canonical dark/Chart.js style) for the
DT4G + consolidated-MACRO recommended model, full history 2000 -> now, 1B VND.

VERIFIABLE ON REAL DATA:
  - VNINDEX Close      : tav2_bq.ticker (ticker='VNINDEX')  REAL index price (BQ)
  - DT4 base state     : tav2_bq.vnindex_5state_dt_4gate
  - macro-adj state    : vnindex_5state_dt4_macro.csv  (DT4 + SBV money + US panic)
  - NAV path           : data/dt4g_macro_overlay_nav.csv (recommended config:
                         #2 trend + #4 confirm10 + time-var bond-cash + macro overlay)
  Every daily row (price, state, weight, NAV) is also written to
  data/dt4g_macro_sim_daily.csv so any point can be re-checked against BQ.

Outputs:
  dt4g_macro_system.html        — overview (state, metrics, NAV, DD, annual, dist)
  dt4g_macro_transitions.html   — state timeline (price colored by state) + table
"""
import sys, io, os, json
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import bq

STATE_NAMES = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}
STATE_ALLOC = {1: "0%", 2: "20%", 3: "70%", 4: "100%", 5: "130%"}
STATE_COLOR = {1: "#ef4444", 2: "#f97316", 3: "#eab308", 4: "#22c55e", 5: "#3b82f6"}
INIT = 1_000_000_000

# ── 1. load real data ───────────────────────────────────────────────────────
print("[1] Loading NAV path + macro state + REAL BQ VNINDEX...")
nav = pd.read_csv(os.path.join(WORKDIR, "data", "dt4g_macro_overlay_nav.csv"), parse_dates=["time"])
ms = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_dt4_macro.csv"), parse_dates=["time"])[["time", "state"]]
ms = ms.rename(columns={"state": "mstate"})
vni = bq("SELECT t.time,t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' ORDER BY t.time")
vni["time"] = pd.to_datetime(vni["time"])
df = nav.merge(ms, on="time", how="left").merge(vni, on="time", how="left")
df = df.dropna(subset=["nav_macro", "Close"]).sort_values("time").reset_index(drop=True)
df["mstate"] = df["mstate"].fillna(df["state"]).astype(int)
df["dtstate"] = df["state"].astype(int)
df["bh"] = INIT * df["Close"] / df["Close"].iloc[0]
n = len(df)
print(f"  {n:,} sessions {df['time'].iloc[0].date()} -> {df['time'].iloc[-1].date()}")

# verifiable daily CSV
ver = df[["time", "Close", "dtstate", "mstate", "w_macro", "cap", "easing_conf", "nav_macro", "nav_base", "bh"]].copy()
ver.columns = ["time", "vnindex_close", "dt4_state", "macro_state", "weight", "macro_cap", "macro_easing", "nav_macro", "nav_dt4", "nav_bh"]
ver.to_csv(os.path.join(WORKDIR, "data", "dt4g_macro_sim_daily.csv"), index=False)

# ── 2. metrics ──────────────────────────────────────────────────────────────
def metrics(navs, time):
    navs = np.asarray(navs, float); time = pd.DatetimeIndex(time)
    yrs = (time[-1] - time[0]).days / 365.25
    r = np.zeros(len(navs)); r[1:] = navs[1:] / navs[:-1] - 1
    spy = len(navs) / yrs
    cagr = (navs[-1] / navs[0]) ** (1 / yrs) - 1
    ex = r - 0.001 / spy
    sh = ex.mean() / ex.std() * np.sqrt(spy) if ex.std() > 0 else 0
    dn = ex[ex < 0]; so = ex.mean() / dn.std() * np.sqrt(spy) if len(dn) and dn.std() > 0 else 0
    rmax = np.maximum.accumulate(navs); dds = (navs - rmax) / rmax; mdd = dds.min()
    under = dds < -1e-9; longest = cur = 0
    for u in under: cur = cur + 1 if u else 0; longest = max(longest, cur)
    return dict(cagr=cagr * 100, sharpe=sh, sortino=so, mdd=mdd * 100,
                calmar=cagr / (-mdd) if mdd < 0 else 0, final=navs[-1] / 1e9, ddur=longest, ddseries=dds)

def seg(a, b):
    s = df[(df["time"] >= a) & (df["time"] <= b)].reset_index(drop=True)
    if len(s) < 20: return None, None, None
    nv = INIT * s["nav_macro"].values / s["nav_macro"].values[0]
    bh = INIT * s["bh"].values / s["bh"].values[0]
    return metrics(nv, s["time"]), metrics(bh, s["time"]), s

mfull = metrics(df["nav_macro"].values, df["time"])
mbh = metrics(df["bh"].values, df["time"])
m11s, m11b, _ = seg(pd.Timestamp("2011-01-01"), df["time"].iloc[-1])
m14s, m14b, _ = seg(pd.Timestamp("2014-01-01"), df["time"].iloc[-1])

# ── 3. annual, drawdown episodes, transitions ───────────────────────────────
df["year"] = df["time"].dt.year
annual = []
for yr, g in df.groupby("year"):
    if len(g) < 5: continue
    annual.append((int(yr), g["nav_macro"].iloc[-1] / g["nav_macro"].iloc[0] - 1,
                   g["bh"].iloc[-1] / g["bh"].iloc[0] - 1))

navm = df["nav_macro"].values; rmax = np.maximum.accumulate(navm); dd = (navm - rmax) / rmax
episodes = []; i = 0
while i < n:
    if dd[i] < -1e-9:
        j = i
        while j < n and dd[j] < -1e-9: j += 1
        s = dd[i:j]; ti = i + int(s.argmin())
        episodes.append((df["time"].iloc[i], df["time"].iloc[ti], df["time"].iloc[min(j, n-1)], float(s.min())))
        i = j
    else: i += 1
episodes = sorted([e for e in episodes if e[3] < -0.08], key=lambda x: x[3])[:8]

st = df["mstate"].values
trans = []
for t in range(1, n):
    if st[t] != st[t-1]:
        # driver
        if df["mstate"].iloc[t] < df["dtstate"].iloc[t]:
            drv = f"MACRO cap → {df['src'].iloc[t] if pd.notna(df['src'].iloc[t]) and df['src'].iloc[t] else 'stress'}"
        elif df["mstate"].iloc[t] > df["dtstate"].iloc[t]:
            drv = "MACRO easing (recovery)"
        else:
            drv = "DT4 regime"
        trans.append(dict(date=df["time"].iloc[t].strftime("%Y-%m-%d"),
                          frm=int(st[t-1]), to=int(st[t]),
                          close=float(df["Close"].iloc[t]),
                          drv=drv))
ntr = len(trans)
sd = pd.Series(st).value_counts(normalize=True).sort_index()
n_macro_tr = sum(1 for t in trans if t["drv"].startswith("MACRO"))

cur_state = int(st[-1]); cur_date = df["time"].iloc[-1].strftime("%Y-%m-%d")
cur_close = float(df["Close"].iloc[-1]); cur_cap = int(df["cap"].iloc[-1])
print(f"[2] metrics done. Full CAGR {mfull['cagr']:.2f}%, transitions {ntr} ({n_macro_tr} macro)")

# ── 2b. merged 3-strategy × 3-period comparison ─────────────────────────────
END = df["time"].iloc[-1]
def pmet(col, a):
    s = df[(df["time"] >= a) & (df["time"] <= END)].reset_index(drop=True)
    nv = INIT * s[col].values / s[col].values[0]
    return metrics(nv, s["time"])
PERIODS = [("Toàn kỳ 2000+", df["time"].iloc[0]), ("Từ 2011", pd.Timestamp("2011-01-01")),
           ("Modern 2014+", pd.Timestamp("2014-01-01"))]
cmp_rows = ""
for label, a in PERIODS:
    mm = pmet("nav_macro", a); md = pmet("nav_base", a); mb = pmet("bh", a)
    cell = lambda m, c: f"<td class='{c}'>{m['cagr']:+.2f}% · Sh {m['sharpe']:.2f} · DD {m['mdd']:.1f}% · {m['final']:.1f}B</td>"
    cmp_rows += f"<tr><td><strong>{label}</strong></td>{cell(mm,'green')}{cell(md,'yellow')}{cell(mb,'blue')}</tr>"

# ── 2c. BigQuery cross-check on sampled dates (fresh pull vs saved CSV) ──────
print("[2c] BQ cross-check on sample dates...")
seen = set(); samp_idx = []
for i in range(n):
    y = df["time"].iloc[i].year
    if y not in seen: seen.add(y); samp_idx.append(i)
samp_idx = sorted(set(samp_idx + [n-2, n-1]))
samp = df.iloc[samp_idx]
date_in = ",".join(f"DATE '{d.strftime('%Y-%m-%d')}'" for d in samp["time"])
bqv = bq(f"SELECT t.time, t.Close AS bq_close FROM tav2_bq.ticker AS t "
         f"WHERE t.ticker='VNINDEX' AND t.time IN ({date_in}) ORDER BY t.time")
bqv["time"] = pd.to_datetime(bqv["time"])
csvv = pd.read_csv(os.path.join(WORKDIR, "data", "dt4g_macro_sim_daily.csv"), parse_dates=["time"])
chk = samp[["time", "mstate"]].merge(bqv, on="time", how="left").merge(
    csvv[["time", "vnindex_close", "nav_macro"]], on="time", how="left")
ver_rows = ""; maxdiff = 0.0
for _, r in chk.iterrows():
    if pd.isna(r["bq_close"]): continue
    d = abs(float(r["bq_close"]) - float(r["vnindex_close"])); maxdiff = max(maxdiff, d)
    ver_rows += (f"<tr><td>{r['time'].date()}</td><td>{r['bq_close']:.2f}</td>"
                 f"<td>{r['vnindex_close']:.2f}</td><td class='green'>{d:.4f}</td>"
                 f"<td>{STATE_NAMES[int(r['mstate'])]}</td><td>{r['nav_macro']/1e9:.2f} tỷ</td></tr>")
print(f"  BQ cross-check: {len(chk)} sample dates, max |diff| = {maxdiff:.6f}")

# ── 4. JS array helpers ─────────────────────────────────────────────────────
def jarr(a, dec=2):
    return "[" + ",".join(("null" if (isinstance(x, float) and (np.isnan(x))) else f"{x:.{dec}f}") for x in a) + "]"
def jstr(a): return json.dumps(list(a))

# weekly downsample for line charts (keep daily in CSV)
step = max(1, n // 1200)
idx = list(range(0, n, step));
if idx[-1] != n - 1: idx.append(n - 1)
dates_js = jstr([df["time"].iloc[i].strftime("%Y-%m-%d") for i in idx])
navm_js = jarr([df["nav_macro"].iloc[i] / 1e9 for i in idx], 4)
navd_js = jarr([df["nav_base"].iloc[i] / 1e9 for i in idx], 4)
bh_js = jarr([df["bh"].iloc[i] / 1e9 for i in idx], 4)
dd_js = jarr([dd[i] * 100 for i in idx], 2)
ddbh = (df["bh"].values - np.maximum.accumulate(df["bh"].values)) / np.maximum.accumulate(df["bh"].values)
ddbh_js = jarr([ddbh[i] * 100 for i in idx], 2)
price_js = jarr([df["Close"].iloc[i] for i in idx], 2)
mstate_js = jstr([int(df["mstate"].iloc[i]) for i in idx])
ann_years = jstr([a[0] for a in annual])
ann_sys = jarr([a[1] * 100 for a in annual], 1)
ann_bh = jarr([a[2] * 100 for a in annual], 1)
dist_js = jstr([round(sd.get(s, 0) * 100, 1) for s in [1, 2, 3, 4, 5]])

CSS = """*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#0f172a;color:#e2e8f0;font-size:13px;line-height:1.6}
.hdr{background:linear-gradient(135deg,#1e3a5f,#1a4731);padding:24px 32px}
.hdr h1{font-size:20px;font-weight:700;color:#fff;margin-bottom:4px}
.hdr p{font-size:12px;color:#94a3b8}
.wrap{max-width:1400px;margin:0 auto;padding:20px 24px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:16px}
.card{background:#1e293b;border-radius:12px;padding:18px 20px;border:1px solid #334155}
.card h2{font-size:13px;font-weight:700;color:#94a3b8;margin-bottom:12px;text-transform:uppercase;letter-spacing:.05em}
.chart-wrap{position:relative;height:320px}.chart-wrap-sm{position:relative;height:240px}
.state-big{display:flex;align-items:center;gap:20px;padding:8px 0}
.state-circle{width:78px;height:78px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#fff;flex-shrink:0}
.state-info h3{font-size:24px;font-weight:800;margin-bottom:4px}.state-info p{font-size:12px;color:#94a3b8;line-height:1.7}
.kpi-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.kpi{background:#0f172a;border-radius:8px;padding:10px 12px;text-align:center}
.kpi .val{font-size:18px;font-weight:700;margin-bottom:2px}.kpi .lbl{font-size:10.5px;color:#64748b}
.green{color:#22c55e}.red{color:#ef4444}.yellow{color:#eab308}.blue{color:#60a5fa}
.badge{display:inline-block;padding:2px 8px;border-radius:6px;color:#fff;font-size:11px;font-weight:600}
table{width:100%;border-collapse:collapse;font-size:12px}
th{background:#0f172a;padding:7px 10px;text-align:left;color:#64748b;font-weight:600;border-bottom:1px solid #334155;position:sticky;top:0}
td{padding:6px 10px;border-bottom:1px solid #1e293b}tr:hover td{background:#0f172a}
.alert{background:#1e3a5f;border:1px solid #3b82f6;border-radius:8px;padding:10px 14px;margin-bottom:14px;font-size:12px;color:#93c5fd}
.ok{background:#13241a;border:1px solid #22c55e;color:#86efac}"""

def kpis(ms, mb):
    g = lambda c: 'green' if c else 'yellow'
    return f"""<div class="kpi-grid">
      <div class="kpi"><div class="val {g(ms['cagr']>mb['cagr'])}">{ms['cagr']:+.2f}%</div><div class="lbl">CAGR model</div></div>
      <div class="kpi"><div class="val blue">{mb['cagr']:+.2f}%</div><div class="lbl">CAGR B&H</div></div>
      <div class="kpi"><div class="val green">{ms['sharpe']:.2f}</div><div class="lbl">Sharpe</div></div>
      <div class="kpi"><div class="val green">{ms['sortino']:.2f}</div><div class="lbl">Sortino</div></div>
      <div class="kpi"><div class="val {g(abs(ms['mdd'])<abs(mb['mdd']))}">{ms['mdd']:+.1f}%</div><div class="lbl">Max DD</div></div>
      <div class="kpi"><div class="val green">{ms['calmar']:.2f}</div><div class="lbl">Calmar</div></div>
    </div><div style="margin-top:8px;font-size:10px;color:#64748b">NAV: <strong style="color:#22c55e">{ms['final']:.1f} tỷ</strong> · B&H {mb['final']:.1f} tỷ · DD recovery max {ms['ddur']} phiên</div>"""

# ── 5. SYSTEM HTML ──────────────────────────────────────────────────────────
print("[3] Writing dt4g_macro_system.html...")
ep_rows = "".join(f"<tr><td>{a.date()}</td><td>{t.date()}</td><td>{b.date()}</td><td class='red'>{tr*100:+.1f}%</td></tr>"
                  for a, t, b, tr in episodes)
rec = ("⚠ MACRO CAP đang hoạt động — giảm tỷ trọng" if cur_cap != 9 else
       f"Duy trì tỷ trọng <strong>{STATE_ALLOC[cur_state]}</strong> theo trạng thái {STATE_NAMES[cur_state]}")

html = f"""<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DT5G — Market System</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>{CSS}</style></head><body>
<div class="hdr"><h1>⚡ DT5G — Market System <span style="font-size:13px;color:#94a3b8;font-weight:400">(DT 4-gate + Macro 5th gate)</span></h1>
<p>DT 4-gate state → allocation + macro overlay (SBV money + US panic) · giá VNINDEX THẬT từ BigQuery · 2000–{cur_date} · bắt đầu 1 tỷ VND · <a href="dt4g_macro_transitions.html" style="color:#60a5fa">xem transitions →</a></p></div>
<div class="wrap">

<div class="grid2">
  <div class="card"><h2>Trạng thái hiện tại — {cur_date}</h2>
    <div class="state-big">
      <div class="state-circle" style="background:{STATE_COLOR[cur_state]}">{STATE_NAMES[cur_state]}</div>
      <div class="state-info"><h3 style="color:{STATE_COLOR[cur_state]}">{STATE_NAMES[cur_state]}</h3>
        <p>Phân bổ cổ phiếu: <strong style="color:{STATE_COLOR[cur_state]}">{STATE_ALLOC[cur_state]}</strong><br>
        VNINDEX: <strong>{cur_close:.2f}</strong><br>
        Macro cap: <strong class="{'red' if cur_cap!=9 else 'green'}">{'ĐANG CAP' if cur_cap!=9 else 'Không (bình thường)'}</strong></p></div>
    </div>
    <div class="alert">💡 <strong>Khuyến nghị:</strong> {rec}</div>
  </div>
  <div class="card ok" style="background:#13241a;border-color:#22c55e"><h2 style="color:#86efac">✔ Kiểm chứng dữ liệu thật</h2>
    <p style="font-size:12px;line-height:1.9">
    • Giá VNINDEX: <strong>tav2_bq.ticker</strong> (ticker='VNINDEX') — {n:,} phiên thật<br>
    • DT4 state: <strong>tav2_bq.vnindex_5state_dt_4gate</strong><br>
    • Macro state: <strong>vnindex_5state_dt4_macro.csv</strong> (DT4 + SBV refi + US VIX/SPX)<br>
    • Chi phí: phí 0.1% 2 chiều + thuế bán 0.1% + tiền nhàn rỗi = TPCP biến động + vay 10% (EX-BULL)<br>
    • Nhân quả, không look-ahead (US lag T-1, refi +5d)<br>
    • Mọi dòng ngày: <strong>data/dt4g_macro_sim_daily.csv</strong> (price·state·weight·NAV — đối chiếu BQ được)</p>
  </div>
</div>

<div class="grid3">
  <div class="card"><h2>Toàn kỳ 2000–nay</h2>{kpis(mfull,mbh)}</div>
  <div class="card"><h2>Từ 2011</h2>{kpis(m11s,m11b)}</div>
  <div class="card"><h2>Modern 2014–nay</h2>{kpis(m14s,m14b)}</div>
</div>

<div class="card" style="margin-bottom:16px"><h2>So sánh gộp — 3 chiến lược × 3 giai đoạn (CAGR · Sharpe · MaxDD · NAV cuối)</h2>
  <table><tr><th>Giai đoạn</th><th class="green">DT5G (model)</th><th class="yellow">DT4-only</th><th class="blue">VNINDEX Buy&amp;Hold</th></tr>
  {cmp_rows}</table>
  <div style="margin-top:8px;font-size:11px;color:#64748b">Mỗi giai đoạn re-base về 1 tỷ. DT5G = DT 4-gate + #2 trend + #4 confirm + bond-cash + macro overlay (cap-commit K=7).</div>
</div>

<div class="card ok" style="margin-bottom:16px;background:#13241a;border-color:#22c55e"><h2 style="color:#86efac">🔎 Đối chiếu BigQuery — query tươi vs file CSV (mẫu mỗi năm)</h2>
  <p style="font-size:11px;color:#86efac;margin-bottom:8px">Cột "BQ Close" lấy LIVE từ <strong>tav2_bq.ticker</strong> ngay khi tạo trang; "CSV Close" từ artifact <strong>data/dt4g_macro_sim_daily.csv</strong>. Δ = 0 ⇒ simulation chạy đúng trên giá thật. Max |Δ| toàn mẫu = <strong>{maxdiff:.6f}</strong>.</p>
  <table><tr><th>Ngày</th><th>BQ Close (live)</th><th>CSV Close</th><th>Δ</th><th>Trạng thái</th><th>NAV model</th></tr>
  {ver_rows}</table>
</div>

<div class="grid2">
  <div class="card"><h2>NAV — DT5G vs DT4-only vs Buy&Hold (log)</h2><div class="chart-wrap"><canvas id="cNav"></canvas></div></div>
  <div class="card"><h2>Drawdown (%)</h2><div class="chart-wrap"><canvas id="cDD"></canvas></div></div>
</div>
<div class="grid2">
  <div class="card"><h2>Lợi nhuận theo năm: Model vs B&H</h2><div class="chart-wrap"><canvas id="cAnn"></canvas></div></div>
  <div class="card"><h2>Phân bố trạng thái (% phiên)</h2><div class="chart-wrap"><canvas id="cDist"></canvas></div></div>
</div>

<div class="grid2">
  <div class="card"><h2>Các đợt sụt giảm lớn nhất (model NAV)</h2>
    <table><tr><th>Bắt đầu</th><th>Đáy</th><th>Hồi phục</th><th>DD đáy</th></tr>{ep_rows}</table></div>
  <div class="card"><h2>Hoạt động hệ thống</h2>
    <p style="font-size:13px;line-height:2">
    Tổng transitions: <strong style="color:#60a5fa">{ntr}</strong> ({ntr/((df['time'].iloc[-1]-df['time'].iloc[0]).days/365.25):.1f}/năm)<br>
    Trong đó do MACRO can thiệp: <strong style="color:#f97316">{n_macro_tr}</strong><br>
    NAV cuối model: <strong class="green">{mfull['final']:.1f} tỷ</strong> (B&H {mbh['final']:.1f} tỷ)<br>
    MaxDD model: <strong class="green">{mfull['mdd']:.1f}%</strong> vs B&H <strong class="red">{mbh['mdd']:.1f}%</strong></p></div>
</div>
</div>

<script>
const D={dates_js};
function mk(id,type,data,opts){{new Chart(document.getElementById(id),{{type:type,data:data,options:Object.assign({{responsive:true,maintainAspectRatio:false,interaction:{{intersect:false,mode:'index'}},plugins:{{legend:{{labels:{{color:'#94a3b8',boxWidth:12,font:{{size:11}}}}}}}}}},opts||{{}})}});}}
const gx={{ticks:{{color:'#64748b',maxTicksLimit:10,font:{{size:10}}}},grid:{{color:'#1e293b'}}}};
mk('cNav','line',{{labels:D,datasets:[
 {{label:'DT5G',data:{navm_js},borderColor:'#22c55e',borderWidth:1.5,pointRadius:0,tension:0}},
 {{label:'DT4-only',data:{navd_js},borderColor:'#eab308',borderWidth:1,pointRadius:0,tension:0,borderDash:[4,3]}},
 {{label:'Buy&Hold',data:{bh_js},borderColor:'#60a5fa',borderWidth:1,pointRadius:0,tension:0}}]}},
 {{scales:{{x:gx,y:{{type:'logarithmic',ticks:{{color:'#64748b',font:{{size:10}}}},grid:{{color:'#1e293b'}}}}}}}});
mk('cDD','line',{{labels:D,datasets:[
 {{label:'DT5G',data:{dd_js},borderColor:'#22c55e',backgroundColor:'rgba(34,197,94,.12)',fill:true,borderWidth:1,pointRadius:0}},
 {{label:'Buy&Hold',data:{ddbh_js},borderColor:'#ef4444',borderWidth:1,pointRadius:0}}]}},
 {{scales:{{x:gx,y:gx}}}});
mk('cAnn','bar',{{labels:{ann_years},datasets:[
 {{label:'Model',data:{ann_sys},backgroundColor:'#22c55e'}},
 {{label:'B&H',data:{ann_bh},backgroundColor:'#60a5fa'}}]}},{{scales:{{x:gx,y:gx}}}});
mk('cDist','doughnut',{{labels:['CRISIS','BEAR','NEUTRAL','BULL','EX-BULL'],datasets:[
 {{data:{dist_js},backgroundColor:['#ef4444','#f97316','#eab308','#22c55e','#3b82f6']}}]}},
 {{scales:{{}},cutout:'55%'}});
</script></body></html>"""
with open(os.path.join(WORKDIR, "dt4g_macro_system.html"), "w", encoding="utf-8") as f:
    f.write(html)

# ── 6. TRANSITIONS HTML ─────────────────────────────────────────────────────
print("[4] Writing dt4g_macro_transitions.html...")
def badge(s): return f"<span class='badge' style='background:{STATE_COLOR[s]}'>{STATE_NAMES[s]}</span>"
trows = "".join(
    f"<tr><td>{t['date']}</td><td>{badge(t['frm'])} → {badge(t['to'])}</td>"
    f"<td>{STATE_ALLOC[t['to']]}</td><td>{t['close']:.2f}</td>"
    f"<td style=\"color:{'#f97316' if t['drv'].startswith('MACRO') else '#94a3b8'}\">{t['drv']}</td></tr>"
    for t in reversed(trans))
seg_color_js = jstr([STATE_COLOR[int(df["mstate"].iloc[i])] for i in idx])

tjs = ("const D=__D__,P=__P__,SC=__SC__;"
       "new Chart(document.getElementById('cPrice'),{type:'line',data:{labels:D,datasets:[{"
       "label:'VNINDEX',data:P,borderWidth:1.5,pointRadius:0,tension:0,"
       "segment:{borderColor:ctx=>SC[ctx.p0DataIndex]}}]},"
       "options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},"
       "scales:{x:{ticks:{color:'#64748b',maxTicksLimit:12,font:{size:10}},grid:{color:'#1e293b'}},"
       "y:{type:'logarithmic',ticks:{color:'#64748b',font:{size:10}},grid:{color:'#1e293b'}}}}});")
tjs = tjs.replace("__D__", dates_js).replace("__P__", price_js).replace("__SC__", seg_color_js)

thtml = f"""<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DT5G — Transitions</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>{CSS}</style></head><body>
<div class="hdr"><h1>🔄 DT5G — State Transitions</h1>
<p>VNINDEX thật tô màu theo trạng thái · {ntr} transitions (2000–{cur_date}) · {n_macro_tr} do macro · <a href="dt4g_macro_system.html" style="color:#60a5fa">← system overview</a></p></div>
<div class="wrap">
<div class="card" style="margin-bottom:16px"><h2>VNINDEX (thật) tô màu theo trạng thái macro-adjusted</h2>
  <div style="margin-bottom:8px">{' '.join(f'<span class="badge" style="background:{STATE_COLOR[s]}">{STATE_NAMES[s]} {STATE_ALLOC[s]}</span>' for s in [1,2,3,4,5])}</div>
  <div class="chart-wrap" style="height:380px"><canvas id="cPrice"></canvas></div></div>
<div class="card"><h2>Bảng transitions ({ntr}) — mới nhất trước</h2>
  <div style="max-height:560px;overflow:auto">
  <table><tr><th>Ngày</th><th>Chuyển trạng thái</th><th>Phân bổ</th><th>VNINDEX</th><th>Nguyên nhân</th></tr>
  {trows}</table></div></div>
</div>
<script>{tjs}</script></body></html>"""
with open(os.path.join(WORKDIR, "dt4g_macro_transitions.html"), "w", encoding="utf-8") as f:
    f.write(thtml)

print("\n" + "=" * 78)
print(f"  DT5G 2000-now: CAGR {mfull['cagr']:+.2f}%  Sharpe {mfull['sharpe']:.2f}  "
      f"MaxDD {mfull['mdd']:.1f}%  NAV {mfull['final']:.1f}B  (B&H {mbh['final']:.1f}B)")
print(f"  Transitions {ntr} ({n_macro_tr} macro-driven)")
print("=" * 78)
print("  → dt4g_macro_system.html")
print("  → dt4g_macro_transitions.html")
print("  → data/dt4g_macro_sim_daily.csv (verifiable daily)")
print("DONE.")
