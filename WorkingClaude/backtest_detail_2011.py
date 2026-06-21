# -*- coding: utf-8 -*-
"""
Bảng chi tiết chuyển trạng thái từ 2011: NAV 4 kịch bản tại mỗi transition.
Output: backtest_detail_2011.html
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ── Build full state pipeline (identical to backtest_full_report.py) ────────
vni = pd.read_csv(WORKDIR + "/VNINDEX.csv", low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
for col in ["Open","High","Low","Close","Volume","VNINDEX_PE",
            "D_RSI","D_RSI_T1W","D_RSI_Max1W","D_RSI_Max3M",
            "D_RSI_Min1W","D_RSI_Min3M","D_RSI_Max1W_Close",
            "D_RSI_Max3M_Close","D_RSI_Max3M_MACD","D_RSI_Max1W_MACD",
            "D_RSI_Min1W_Close","D_RSI_MinT3","D_MACDdiff","D_CMF","C_L1M","C_L1W"]:
    if col in vni.columns:
        vni[col] = pd.to_numeric(vni[col], errors="coerce")
if os.path.exists(WORKDIR+"/breadth_data.csv"):
    br = pd.read_csv(WORKDIR+"/breadth_data.csv"); br["time"]=pd.to_datetime(br["time"])
    vni = vni.merge(br, on="time", how="left")
else:
    vni["breadth"] = np.nan

close=vni["Close"].values.copy(); high=vni["High"].values.copy()
low=vni["Low"].values.copy(); vol=vni["Volume"].values.copy(); n=len(close)
cal_days=(vni["time"].iloc[-1]-vni["time"].iloc[0]).days
SPY=n/(cal_days/365.25)

def _ema(arr,k):
    out=np.full(len(arr),np.nan)
    for i in range(len(arr)):
        out[i]=arr[i] if (i==0 or np.isnan(out[i-1])) else out[i-1]*(1-k)+arr[i]*k
    return out
def _rank(arr,min_lb=252):
    out=np.full(len(arr),np.nan)
    for t in range(len(arr)):
        if np.isnan(arr[t]): continue
        v=arr[:t+1]; v=v[~np.isnan(v)]
        if len(v)>=min_lb: out[t]=np.sum(v<=arr[t])/len(v)
    return out

p3m=np.full(n,np.nan)
if "Change_3M" in vni.columns:
    cv=pd.to_numeric(vni["Change_3M"],errors="coerce").values
    for i in range(n):
        p3m[i]=cv[i] if not np.isnan(cv[i]) else (close[i]/close[i-60]-1 if i>=60 and close[i-60]>0 else np.nan)
else:
    for i in range(60,n):
        if close[i-60]>0: p3m[i]=close[i]/close[i-60]-1
p1m=np.full(n,np.nan)
if "Change_1M" in vni.columns:
    cv=pd.to_numeric(vni["Change_1M"],errors="coerce").values
    for i in range(n):
        p1m[i]=cv[i] if not np.isnan(cv[i]) else (close[i]/close[i-20]-1 if i>=20 and close[i-20]>0 else np.nan)
else:
    for i in range(20,n):
        if close[i-20]>0: p1m[i]=close[i]/close[i-20]-1
ma200=pd.Series(close).rolling(200,min_periods=200).mean().values
ma200_dev=np.where((ma200>0)&~np.isnan(ma200),close/ma200-1,np.nan)
rsi=np.full(n,np.nan); au=ad=np.nan
for i in range(1,n):
    d=close[i]-close[i-1]; u=max(d,0); dn=max(-d,0)
    if np.isnan(au):
        if i>=14:
            au=np.mean([max(close[j]-close[j-1],0) for j in range(1,15)])
            ad=np.mean([max(close[j-1]-close[j],0) for j in range(1,15)])
            if au+ad>0: rsi[i]=au/(au+ad)
    else:
        au=(au*13+u)/14; ad=(ad*13+dn)/14
        if au+ad>0: rsi[i]=au/(au+ad)
e12=_ema(close,2/13); e26=_ema(close,2/27)
macd_l=e12-e26; sig9=_ema(macd_l,2/10)
macd_hist=np.where(np.arange(n)>=33,macd_l-sig9,np.nan)
hl=high-low; mfm=np.where(hl>0,((close-low)-(high-close))/hl,0.0)
cmf=np.full(n,np.nan)
for i in range(14,n):
    vs=np.sum(vol[i-14:i])
    if vs>0: cmf[i]=np.sum(mfm[i-14:i]*vol[i-14:i])/vs
br_arr=vni["breadth"].values if "breadth" in vni.columns else np.full(n,np.nan)
W={"P3M":0.30,"P1M":0.10,"MA200":0.15,"RSI":0.15,"MACD":0.10,"CMF":0.08,"Breadth":0.12}
raw={"P3M":p3m,"P1M":p1m,"MA200":ma200_dev,"RSI":rsi,"MACD":macd_hist,"CMF":cmf,"Breadth":br_arr}
ranks={k:_rank(v) for k,v in raw.items()}
score=np.full(n,np.nan)
for t in range(n):
    av={k:ranks[k][t] for k in ranks if not np.isnan(ranks[k][t])}
    if len(av)>=3:
        ws=sum(W[k] for k in av); score[t]=sum(av[k]*W[k] for k in av)/ws
r_score=_rank(score)
r_ema=np.full(n,np.nan)
for t in range(n):
    v=r_score[t]; p=r_ema[t-1] if t>0 else np.nan
    r_ema[t]=v if np.isnan(p) else (p if np.isnan(v) else 0.40*v+0.60*p)
pe_arr=vni["VNINDEX_PE"].values.copy()
pe_p90=np.full(n,np.nan)
for t in range(n):
    h=pe_arr[:t+1]; h=h[~np.isnan(h)]
    if len(h)>=60: pe_p90[t]=np.nanpercentile(h,90)
rm_c=np.maximum.accumulate(np.where(np.isnan(close),0,close))
dd_raw=np.where(rm_c>0,close/rm_c-1,0.0)
dr=np.full(n,np.nan)
for i in range(1,n):
    if close[i-1]>0: dr[i]=close[i]/close[i-1]-1
v20_a=np.full(n,np.nan)
for i in range(20,n):
    w2=dr[i-20:i]; w2=w2[~np.isnan(w2)]
    if len(w2)>=15: v20_a[i]=np.std(w2)*np.sqrt(SPY)
avg_vol_a=np.full(n,np.nan)
for t in range(n):
    h=v20_a[:t+1]; h=h[~np.isnan(h)]
    if len(h)>=60: avg_vol_a[t]=np.mean(h)
def classify(rs):
    if np.isnan(rs): return 3
    if rs<0.10: return 1
    elif rs<0.20: return 2
    elif rs<0.70: return 3
    elif rs<0.90: return 4
    else: return 5
st=np.array([classify(r) for r in r_ema])
for i in range(n):
    s=st[i]
    if not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i]) and pe_arr[i]>pe_p90[i] and s==5: s=4
    if dd_raw[i]<-0.25 and s>=4: s=3
    if not np.isnan(avg_vol_a[i]) and not np.isnan(v20_a[i]) and v20_a[i]>1.5*avg_vol_a[i] and s==5: s=4
    st[i]=s
def _s(c): return vni[c] if c in vni.columns else pd.Series(np.nan,index=vni.index)
_mask=vni["time"]>="2011-01-01"
_DR=_s("D_RSI");_DRT=_s("D_RSI_T1W");_DM1W=_s("D_RSI_Max1W");_DM3M=_s("D_RSI_Max3M")
_DN1W=_s("D_RSI_Min1W");_DN3M=_s("D_RSI_Min3M");_DM1WC=_s("D_RSI_Max1W_Close")
_DM3MC=_s("D_RSI_Max3M_Close");_DM3MM=_s("D_RSI_Max3M_MACD");_DM1WM=_s("D_RSI_Max1W_MACD")
_DN1WC=_s("D_RSI_Min1W_Close");_DMT3=_s("D_RSI_MinT3");_DMACD=_s("D_MACDdiff")
_DCMF=_s("D_CMF");_CL1M=_s("C_L1M");_CL1W=_s("C_L1W")
bear_mask=(
 ((_DM1W/_DR>1.044)&(_DM3M>0.74)&(_DM1W<0.72)&(_DM1W>0.61)&
  (_DM1WC/_DM3MC>1.028)&(_DM3MM/_DM1WM>1.11)&(_DMACD<0)&
  (vni["Close"]/_DM3MC>0.96)&(_DMT3>0.43)&(_DCMF<0.13)&_mask)
 |((_DM1W/_DR>1.016)&(_DM3M>0.77)&(_DM1W<0.79)&(_DM1W>0.60)&
  (_DM1WC/_DM3MC>1.008)&(_DM3MM/_DM1WM>1.10)&(_DMACD<0)&
  (vni["Close"]/_DM3MC>0.97)&(_DMT3>0.50)&(_DCMF<0.15)&_mask)
).values.astype(bool)
bull_mask=(
 ((_DN1W/_DN3M>0.90)&(_DN1W<0.60)&(_DN3M<0.40)&(_DN1WC/_DM3MC<1.15)&
  (_DMACD>0)&(_DMT3<0.50)&(_DM1W<0.48)&(_DR/_DRT>1.12)&(_DCMF>0)&
  (_CL1M<1.21)&(_CL1W<1.05)&_mask)
 |((_DN1W/_DN3M>0.92)&(_DN1W<0.52)&(_DN3M<0.38)&(_DN1WC/_DM3MC<1.10)&
  (_DMACD>0)&(_DMT3<0.56)&(_DM1W<0.64)&(_DR/_DRT>1.10)&(_DCMF>0)&
  (_CL1M<1.20)&(_CL1W<1.025)&_mask)
).values.astype(bool)
pe_rank=np.full(n,np.nan)
for t in range(n):
    if np.isnan(pe_arr[t]): continue
    h=pe_arr[:t+1]; h=h[~np.isnan(h)]
    if len(h)>=60: pe_rank[t]=np.sum(h<=pe_arr[t])/len(h)
p3m_rank=ranks["P3M"]
streak=np.zeros(n,dtype=bool); _k=0
for i in range(n):
    if not np.isnan(r_ema[i]) and r_ema[i]>0.65: _k+=1
    else: _k=0
    if _k>=10: streak[i]=True
gate_active=False; gate_start=-1; st_dvg=st.copy()
for i in range(n):
    if bear_mask[i]: gate_active=True; gate_start=i
    if gate_active:
        if st_dvg[i]>1: st_dvg[i]=1
        if i-gate_start>=60:
            p3_ok=(not np.isnan(p3m_rank[i])) and p3m_rank[i]>0.45
            pe_ok=(not np.isnan(pe_rank[i])) and pe_rank[i]<0.80
            if bull_mask[i] or (p3_ok and pe_ok) or bool(streak[i]): gate_active=False
def rolling_mode(states,w=15):
    out=states.copy()
    for t in range(w-1,len(states)):
        ww=states[t-w+1:t+1]; vs,cs=np.unique(ww,return_counts=True)
        cands=vs[cs==cs.max()]
        for v in reversed(ww):
            if v in cands: out[t]=v; break
    return out
def min_stay_filter(states,m=7):
    out=states.copy(); changed=True
    while changed:
        changed=False; i=0
        while i<len(out):
            j=i+1
            while j<len(out) and out[j]==out[i]: j+=1
            if j-i<m:
                fill=out[i-1] if i>0 else (out[j] if j<len(out) else out[i])
                out[i:j]=fill; changed=True
            i=j
    return out
st_smooth=min_stay_filter(rolling_mode(st_dvg,15),7)
TARGET_W={1:0.00,2:0.20,3:0.70,4:1.00,5:1.30}
STATE_NAMES={1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

# ── Build recovery map ──────────────────────────────────────────────────────
REC_W=1.30; REC_D=20
rec_map={}
i=0
while i<n-1:
    if st_smooth[i]==1:
        start=i
        while i<n-1 and st_smooth[i]==1: i+=1
        end=i
        if end-start>=2 and end<n:
            for t in range(end, min(end+REC_D,n)):
                if st_smooth[t]!=1: rec_map[t]=REC_W
    else: i+=1

# ── Simulate ────────────────────────────────────────────────────────────────
def simulate(dep_annual, use_rec=False):
    DR=dep_annual/SPY; BR=0.10/SPY; TC=0.001
    pv=np.zeros(n); pv[0]=1e9; w=TARGET_W[3]
    ws=np.zeros(n); ws[0]=w
    for t in range(1,n):
        base=TARGET_W[st_smooth[t-1]]
        target=(max(base,rec_map[t-1]) if use_rec and (t-1) in rec_map else base)
        diff=target-w
        w_new=target if abs(diff)<0.03 else w+diff/3
        w_new=float(np.clip(w_new,0.0,1.50))
        rm=close[t]/close[t-1]-1 if close[t-1]>0 else 0.0
        pv[t]=pv[t-1]*(1.0+w_new*rm+max(0.0,1.0-w_new)*DR
                       -max(0.0,w_new-1.0)*BR-abs(w_new-w)*TC)
        w=w_new; ws[t]=w
    return pv, ws

pv_ht6,  ws_ht6  = simulate(0.06,  False)
pv_ht01, ws_ht01 = simulate(0.001, False)
pv_rec,  ws_rec  = simulate(0.001, True)
pv_bh=np.zeros(n); pv_bh[0]=1e9
for t in range(1,n): pv_bh[t]=pv_bh[t-1]*(close[t]/close[t-1] if close[t-1]>0 else 1.0)

# ── Find transitions from 2011 ───────────────────────────────────────────────
idx11 = vni[vni["time"]>="2011-01-01"].index[0]

transitions = []
prev_st = st_smooth[0]
seg_start = 0
for i in range(1, n):
    if st_smooth[i] != prev_st:
        transitions.append({
            "i": i,
            "date": vni["time"].iloc[i],
            "from": int(prev_st),
            "to":   int(st_smooth[i]),
            "dur_sessions": i - seg_start,
            "dur_days": (vni["time"].iloc[i] - vni["time"].iloc[seg_start]).days,
            "seg_start": seg_start,
        })
        prev_st = st_smooth[i]
        seg_start = i

# Add final row (current state)
transitions.append({
    "i": n-1,
    "date": vni["time"].iloc[n-1],
    "from": int(st_smooth[n-1]),
    "to": None,  # current
    "dur_sessions": n-1 - seg_start,
    "dur_days": (vni["time"].iloc[n-1] - vni["time"].iloc[seg_start]).days,
    "seg_start": seg_start,
    "is_current": True,
})

# Filter to 2011+
transitions_2011 = [t for t in transitions if t["date"] >= pd.Timestamp("2011-01-01")]

# ── State style helpers ──────────────────────────────────────────────────────
STATE_BG   = {1:"#7f1d1d", 2:"#7c2d12", 3:"#1e293b", 4:"#14532d", 5:"#3b0764"}
STATE_FG   = {1:"#fca5a5", 2:"#fdba74", 3:"#94a3b8", 4:"#86efac", 5:"#c4b5fd"}
STATE_CASH = {1:"100:0", 2:"80:20", 3:"30:70", 4:"0:100", 5:"-30:130"}
STATE_LABEL= {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}

def state_badge(s, small=False):
    if s is None: return '<span style="color:#64748b">—</span>'
    sz = "10px" if small else "11px"
    return (f'<span style="background:{STATE_BG[s]};color:{STATE_FG[s]};'
            f'padding:2px 7px;border-radius:10px;font-size:{sz};font-weight:700;white-space:nowrap">'
            f'{STATE_LABEL[s]}</span>')

def rank_cell(v, invert=False):
    """Color-code a rank 0-1: green=high, red=low (or inverted)."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return '<td style="padding:3px 5px;text-align:center;color:#475569;font-size:11px">—</td>'
    pct = v * 100
    if invert: pct = 100 - pct
    if pct >= 70: bg, fg = "#14532d", "#86efac"
    elif pct >= 45: bg, fg = "#1e293b", "#94a3b8"
    else: bg, fg = "#7f1d1d", "#fca5a5"
    return (f'<td style="background:{bg};color:{fg};text-align:center;'
            f'font-weight:600;padding:3px 5px;font-size:11px">{pct:.0f}%</td>')

def rscore_cell(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return '<td style="text-align:center;color:#475569">—</td>'
    pct = v * 100
    if v < 0.10: bg, fg = "#dc2626", "#fff"
    elif v < 0.20: bg, fg = "#ea580c", "#fff"
    elif v < 0.70: bg, fg = "#374151", "#e5e7eb"
    elif v < 0.90: bg, fg = "#15803d", "#fff"
    else: bg, fg = "#7c3aed", "#fff"
    return (f'<td style="background:{bg};color:{fg};text-align:center;'
            f'font-weight:800;padding:3px 6px;font-size:11px">{pct:.1f}%</td>')

def nav_cell(pv_val, prev_val=None, highlight=False):
    nav = pv_val / 1e9
    txt = f"{nav:.2f}t"
    if prev_val and prev_val > 0:
        chg = pv_val / prev_val - 1
        sign = "+" if chg >= 0 else ""
        clr = "#4ade80" if chg >= 0 else "#f87171"
        delta = f'<div style="font-size:10px;color:{clr}">{sign}{chg*100:.1f}%</div>'
    else:
        delta = ""
    style = "font-size:12px;font-weight:700;color:#f8fafc"
    if highlight:
        style += ";background:#1e3a5f"
    return f'<td style="padding:3px 6px;white-space:nowrap"><div style="{style}">{txt}</div>{delta}</td>'

def pct_chg(v):
    if v is None or (isinstance(v, float) and np.isnan(v)): return "—"
    s = "+" if v >= 0 else ""
    return f"{s}{v*100:.1f}%"

# ── Build table rows ─────────────────────────────────────────────────────────
rows_html = ""
prev_pvs = {k: None for k in ["ht6","ht01","rec","bh"]}
row_alt = True

for tr in transitions_2011:
    i = tr["i"]
    is_curr = tr.get("is_current", False)
    from_s = tr["from"]
    to_s   = tr["to"]

    date_str = tr["date"].strftime("%Y-%m-%d")
    dur_d    = tr["dur_days"]
    dur_sess = tr["dur_sessions"]

    # NAV values
    pvs = {
        "ht6":  pv_ht6[i],
        "ht01": pv_ht01[i],
        "rec":  pv_rec[i],
        "bh":   pv_bh[i],
    }
    navs = {k: v/1e9 for k,v in pvs.items()}

    # Episode returns (from previous transition to this one)
    seg_s = tr["seg_start"]
    ep_ret = {}
    for k, pv_arr in [("ht6",pv_ht6),("ht01",pv_ht01),("rec",pv_rec),("bh",pv_bh)]:
        v0 = pv_arr[seg_s]; v1 = pv_arr[i]
        ep_ret[k] = (v1/v0 - 1) if v0 > 0 else None

    # Factors at this date
    p3m_v   = p3m[i];   p3m_r  = ranks["P3M"][i]
    ma200_v = ma200_dev[i]; ma200_r = ranks["MA200"][i]
    rsi_v   = rsi[i];   rsi_r  = ranks["RSI"][i]
    macd_v  = macd_hist[i]; macd_r = ranks["MACD"][i]
    cmf_v   = cmf[i];   cmf_r  = ranks["CMF"][i]
    r_ema_v = r_ema[i]
    vni_val = close[i]

    # Recovery boost active?
    boost_active = i in rec_map

    # Direction arrow
    if is_curr:
        arrow = '<td style="padding:3px 4px;text-align:center;font-size:14px;color:#64748b">●</td>'
        to_cell = f'<td style="padding:3px 6px;text-align:center">{state_badge(from_s)}<div style="font-size:10px;color:#64748b;margin-top:2px">hiện tại</div></td>'
        from_cell = f'<td style="padding:3px 6px;text-align:center">{state_badge(from_s)}</td>'
        dir_attr = "current"
        row_bg = "#0a0f1e"
    else:
        is_up = to_s > from_s
        arrow_sym = "▲" if is_up else "▼"
        arrow_clr = "#22c55e" if is_up else "#ef4444"
        arrow = f'<td style="padding:3px 4px;text-align:center;font-size:15px;color:{arrow_clr}">{arrow_sym}</td>'
        from_cell = f'<td style="padding:3px 6px;text-align:center">{state_badge(from_s)}</td>'
        to_cell   = f'<td style="padding:3px 6px;text-align:center">{state_badge(to_s)}</td>'
        dir_attr  = "up" if is_up else "down"
        row_bg = "#1e293b" if row_alt else "#0f172a"
        row_alt = not row_alt

    # Cash ratio cell
    cash_str = STATE_CASH.get(to_s if not is_curr else from_s, "—")
    cash_bg  = STATE_BG.get(to_s if not is_curr else from_s, "#1e293b")
    cash_fg  = STATE_FG.get(to_s if not is_curr else from_s, "#94a3b8")
    cash_cell = (f'<td style="background:{cash_bg};color:{cash_fg};text-align:center;'
                 f'font-weight:700;font-size:11px;padding:3px 6px;white-space:nowrap">{cash_str}</td>')

    # Boost tag
    boost_tag = (' <span style="background:#1e3a5f;color:#60a5fa;font-size:10px;'
                 'padding:1px 5px;border-radius:4px;vertical-align:middle">+Boost</span>'
                 if boost_active else "")

    # Build reason text
    top3 = sorted([(k, ranks[k][i]) for k in ["P3M","RSI","MACD","MA200","CMF"]
                   if not np.isnan(ranks[k][i])], key=lambda x: abs(x[1]-0.5), reverse=True)[:3]
    reason_parts = []
    if not np.isnan(r_ema_v):
        thr = ("CRISIS" if r_ema_v<0.10 else "BEAR" if r_ema_v<0.20 else
               "NEUTRAL" if r_ema_v<0.70 else "BULL" if r_ema_v<0.90 else "EX-BULL")
        reason_parts.append(f"r_ema={r_ema_v*100:.1f}% → {thr}")
    drivers = ", ".join(f"{k}={v*100:.0f}%" for k,v in top3)
    if drivers: reason_parts.append(f"<span style='color:#64748b;font-size:10px'>{drivers}</span>")

    # NAV return color helper
    def ret_color(v):
        if v is None: return "#94a3b8"
        return "#4ade80" if v >= 0 else "#f87171"

    # Episode return cells
    def ep_cell(k):
        v = ep_ret[k]
        if v is None: return '<td style="padding:3px 5px;text-align:center;color:#475569">—</td>'
        s = "+" if v >= 0 else ""
        clr = "#4ade80" if v >= 0.0 else "#f87171"
        bold = " font-weight:700;" if abs(v) > 0.08 else ""
        return (f'<td style="padding:3px 5px;text-align:center;'
                f'color:{clr};font-size:11px;{bold}">{s}{v*100:.1f}%</td>')

    # Absolute NAV cells
    def abs_nav(k):
        v = pvs[k] / 1e9
        bg = "#132030" if k == "rec" else ""
        return (f'<td style="padding:3px 5px;text-align:center;font-size:11px;'
                f'color:#e2e8f0;background:{bg}">{v:.2f}t</td>')

    # from_state data attribute
    from_attr = STATE_LABEL.get(from_s, "")
    to_attr   = STATE_LABEL.get(to_s, "") if to_s else "current"

    rows_html += (
        f'<tr style="background:{row_bg};border-bottom:1px solid #1e293b" '
        f'data-from="{from_attr}" data-to="{to_attr}" data-date="{date_str}" data-dir="{dir_attr}">\n'
        f'  <td style="padding:4px 7px;font-size:12px;color:#94a3b8;white-space:nowrap">{date_str}</td>\n'
        f'  {from_cell}\n'
        f'  {arrow}\n'
        f'  {to_cell}\n'
        f'  <td style="padding:4px 6px;text-align:center;color:#64748b;font-size:11px;white-space:nowrap">'
        f'{dur_d}d / {dur_sess}p</td>\n'
        f'  <td style="padding:4px 6px;text-align:right;color:#e2e8f0;font-size:12px">{vni_val:.0f}</td>\n'
        f'  {cash_cell}\n'
        # Episode returns
        f'  {ep_cell("ht01")}\n'
        f'  {ep_cell("rec")}\n'
        f'  {ep_cell("bh")}\n'
        # Absolute NAVs
        f'  {abs_nav("ht01")}\n'
        f'  {abs_nav("rec")}\n'
        f'  {abs_nav("bh")}\n'
        # Factors
        f'  <td style="padding:3px 5px;text-align:center;color:#94a3b8;font-size:11px">'
        f'{"" if np.isnan(p3m_v) else f"{p3m_v*100:+.1f}%"}</td>\n'
        f'  {rank_cell(p3m_r)}\n'
        f'  <td style="padding:3px 5px;text-align:center;color:#94a3b8;font-size:11px">'
        f'{"" if np.isnan(ma200_v) else f"{ma200_v*100:+.1f}%"}</td>\n'
        f'  {rank_cell(ma200_r)}\n'
        f'  <td style="padding:3px 5px;text-align:center;color:#94a3b8;font-size:11px">'
        f'{"" if np.isnan(rsi_v) else f"{rsi_v:.2f}"}</td>\n'
        f'  {rank_cell(rsi_r)}\n'
        f'  <td style="padding:3px 5px;text-align:center;color:#94a3b8;font-size:11px">'
        f'{"" if np.isnan(macd_v) else f"{macd_v:.1f}"}</td>\n'
        f'  {rank_cell(macd_r)}\n'
        f'  {rscore_cell(r_ema_v)}\n'
        f'  <td style="padding:3px 8px;color:#94a3b8;font-size:11px;max-width:200px">'
        f'{"".join(reason_parts)}{boost_tag}</td>\n'
        f'</tr>\n'
    )

# ── Summary stats for header ─────────────────────────────────────────────────
n_tr_2011 = sum(1 for t in transitions_2011 if not t.get("is_current"))
n_crisis  = sum(1 for t in transitions_2011 if t["to"] == 1 and not t.get("is_current"))
n_bear    = sum(1 for t in transitions_2011 if t["to"] == 2 and not t.get("is_current"))
n_neutral = sum(1 for t in transitions_2011 if t["to"] == 3 and not t.get("is_current"))
n_bull    = sum(1 for t in transitions_2011 if t["to"] == 4 and not t.get("is_current"))
n_exbull  = sum(1 for t in transitions_2011 if t["to"] == 5 and not t.get("is_current"))

final_rec = pv_rec[n-1] / 1e9
final_bh  = pv_bh[n-1]  / 1e9

# Current state info
curr_st = int(st_smooth[n-1])
curr_name = STATE_LABEL[curr_st]
curr_color = STATE_FG[curr_st]

# ── HTML ─────────────────────────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Bảng chi tiết Backtest 2011–nay</title>
<style>
* {{ box-sizing:border-box;margin:0;padding:0 }}
body {{ background:#0a0f1e;color:#e2e8f0;font-family:'Segoe UI',sans-serif;padding:16px;font-size:13px }}
h1 {{ font-size:19px;color:#f8fafc;margin-bottom:3px }}
.subtitle {{ color:#64748b;font-size:12px;margin-bottom:14px }}
.stats {{ display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px }}
.stat-card {{ background:#1e293b;border-radius:8px;padding:8px 14px;border:1px solid #334155 }}
.stat-card .num {{ font-size:20px;font-weight:800 }}
.stat-card .lbl {{ font-size:10px;color:#64748b }}
.legend {{ background:#1e293b;border:1px solid #334155;border-radius:8px;padding:9px 13px;
           margin-bottom:12px;font-size:11px }}
.legend table td {{ padding:2px 8px;border:none;background:transparent!important }}
.controls {{ display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px;align-items:center }}
input[type=text] {{ background:#1e293b;border:1px solid #334155;color:#e2e8f0;
                    padding:5px 10px;border-radius:6px;font-size:12px;width:160px }}
.filter-btn {{ background:#1e293b;border:1px solid #334155;color:#94a3b8;
               padding:4px 10px;border-radius:6px;cursor:pointer;font-size:11px }}
.filter-btn.active {{ border-color:#60a5fa;color:#60a5fa;background:#1e3a5f }}
.filter-btn.crisis-btn.active  {{ border-color:#dc2626;color:#dc2626;background:#3b0d0d }}
.filter-btn.bear-btn.active    {{ border-color:#f97316;color:#f97316;background:#3b1a08 }}
.filter-btn.neutral-btn.active {{ border-color:#9ca3af;color:#d1d5db;background:#1f2937 }}
.filter-btn.bull-btn.active    {{ border-color:#16a34a;color:#16a34a;background:#052e16 }}
.filter-btn.exbull-btn.active  {{ border-color:#7c3aed;color:#a78bfa;background:#2e1065 }}
.filter-btn.down-btn.active    {{ border-color:#dc2626;color:#f87171;background:#3b0d0d }}
.filter-btn.up-btn.active      {{ border-color:#16a34a;color:#4ade80;background:#052e16 }}
.table-wrap {{ overflow-x:auto;max-height:75vh;overflow-y:auto;border-radius:8px;border:1px solid #334155 }}
table {{ width:100%;border-collapse:collapse;font-size:11px }}
thead th {{ background:#0f172a;color:#64748b;font-size:9px;font-weight:700;
            text-transform:uppercase;letter-spacing:.4px;padding:6px 5px;
            position:sticky;top:0;z-index:10;border-bottom:2px solid #334155;white-space:nowrap }}
thead th.grp {{ border-left:2px solid #1e293b }}
tr:hover td {{ background:rgba(96,165,250,0.06)!important }}
.hidden {{ display:none!important }}
#count-info {{ color:#64748b;font-size:11px }}
.note {{ background:#1e293b;border:1px solid #334155;border-radius:6px;padding:8px 12px;
         margin-top:12px;font-size:11px;color:#94a3b8 }}
</style>
</head>
<body>
<h1>📊 Bảng Chi Tiết Trạng Thái · Backtest 2011–nay</h1>
<p class="subtitle">NAV 4 kịch bản tại mỗi lần chuyển trạng thái · {n_tr_2011} transitions · Vốn ban đầu: 1 tỷ đồng</p>

<div class="stats">
  <div class="stat-card"><div class="num" style="color:#e2e8f0">{n_tr_2011}</div><div class="lbl">Tổng chuyển đổi</div></div>
  <div class="stat-card"><div class="num" style="color:#ef4444">{n_crisis}</div><div class="lbl">→ CRISIS</div></div>
  <div class="stat-card"><div class="num" style="color:#f97316">{n_bear}</div><div class="lbl">→ BEAR</div></div>
  <div class="stat-card"><div class="num" style="color:#9ca3af">{n_neutral}</div><div class="lbl">→ NEUTRAL</div></div>
  <div class="stat-card"><div class="num" style="color:#22c55e">{n_bull}</div><div class="lbl">→ BULL</div></div>
  <div class="stat-card"><div class="num" style="color:#a78bfa">{n_exbull}</div><div class="lbl">→ EX-BULL</div></div>
  <div class="stat-card"><div class="num" style="color:#60a5fa">{final_rec:.1f}t</div><div class="lbl">NAV HT+Rec (hiện tại)</div></div>
  <div class="stat-card"><div class="num" style="color:#94a3b8">{final_bh:.1f}t</div><div class="lbl">NAV B&H (hiện tại)</div></div>
  <div class="stat-card"><div class="num" style="color:{curr_color}">{curr_name}</div><div class="lbl">Trạng thái hiện tại</div></div>
</div>

<div class="legend">
  <b style="color:#e2e8f0">Các kịch bản so sánh</b>
  <table style="margin-top:5px">
    <tr>
      <td><span style="background:#1e293b;color:#94a3b8;padding:2px 8px;border-radius:5px;border:1px solid #475569">HT 0.1%</span></td>
      <td style="color:#94a3b8">Hệ thống thực tế: 0.1%/yr tiền gửi không kỳ hạn, không boost</td>
    </tr>
    <tr>
      <td><span style="background:#132030;color:#60a5fa;padding:2px 8px;border-radius:5px">HT+Rec</span></td>
      <td style="color:#94a3b8">HT thực tế + Boost 130% trong 20 phiên sau mỗi lần thoát CRISIS <span style="color:#60a5fa">+Boost</span></td>
    </tr>
    <tr>
      <td><span style="background:#1e293b;color:#60a5fa;padding:2px 8px;border-radius:5px">B&H</span></td>
      <td style="color:#94a3b8">Buy &amp; Hold: 100% cổ phiếu mọi lúc, không phí giao dịch</td>
    </tr>
  </table>
  <div style="margin-top:5px;color:#64748b">
    <b style="color:#94a3b8">Các cột "Kỳ"</b> = hiệu suất từ phiên đầu của trạng thái trước đến phiên chuyển hiện tại &nbsp;|&nbsp;
    <b style="color:#94a3b8">Cột "NAV"</b> = giá trị tuyệt đối tại thời điểm chuyển trạng thái
  </div>
</div>

<div class="controls">
  <input type="text" id="search" placeholder="Tìm ngày / trạng thái…" oninput="applyFilters()">
  <button class="filter-btn active" id="btn-all" onclick="setFilter('all')">Tất cả</button>
  <button class="filter-btn down-btn" id="btn-down" onclick="setFilter('down')">▼ Xuống cấp</button>
  <button class="filter-btn up-btn"   id="btn-up"   onclick="setFilter('up')">▲ Lên cấp</button>
  <button class="filter-btn crisis-btn"  id="btn-crisis"  onclick="setFilter('CRISIS')">CRISIS</button>
  <button class="filter-btn bear-btn"    id="btn-bear"    onclick="setFilter('BEAR')">BEAR</button>
  <button class="filter-btn neutral-btn" id="btn-neutral" onclick="setFilter('NEUTRAL')">NEUTRAL</button>
  <button class="filter-btn bull-btn"    id="btn-bull"    onclick="setFilter('BULL')">BULL</button>
  <button class="filter-btn exbull-btn"  id="btn-exbull"  onclick="setFilter('EX-BULL')">EX-BULL</button>
  <span id="count-info"></span>
</div>

<div class="table-wrap">
<table>
<thead>
<tr>
  <th rowspan="2">Ngày</th>
  <th rowspan="2">Từ</th>
  <th rowspan="2"></th>
  <th rowspan="2">Sang</th>
  <th rowspan="2">Thời gian</th>
  <th rowspan="2">VNINDEX</th>
  <th rowspan="2">Tiền:CP</th>
  <th class="grp" colspan="3" style="text-align:center;color:#60a5fa">Hiệu suất kỳ trước</th>
  <th class="grp" colspan="3" style="text-align:center;color:#a78bfa">NAV hiện tại (tỷ đ)</th>
  <th class="grp" colspan="2" style="text-align:center;color:#f97316">P3M</th>
  <th class="grp" colspan="2" style="text-align:center;color:#fbbf24">MA200</th>
  <th class="grp" colspan="2" style="text-align:center;color:#34d399">RSI</th>
  <th class="grp" colspan="2" style="text-align:center;color:#60a5fa">MACD</th>
  <th rowspan="2" class="grp" style="color:#f8fafc">r_ema ★</th>
  <th rowspan="2">Lý do</th>
</tr>
<tr>
  <th class="grp" style="color:#94a3b8">HT 0.1%</th>
  <th style="color:#60a5fa">HT+Rec</th>
  <th style="color:#60a5fa">B&H</th>
  <th class="grp" style="color:#94a3b8">HT 0.1%</th>
  <th style="color:#60a5fa">HT+Rec</th>
  <th style="color:#60a5fa">B&H</th>
  <th class="grp">%</th><th>Rank</th>
  <th class="grp">%</th><th>Rank</th>
  <th class="grp">Val</th><th>Rank</th>
  <th class="grp">Hist</th><th>Rank</th>
</tr>
</thead>
<tbody id="tbody">
{rows_html}
</tbody>
</table>
</div>

<div class="note">
  <b>Ghi chú:</b>
  Backtest: T+1 execution · ramp 3 phiên (snap nếu |diff|&lt;3%) · TC=0.1%/giao dịch · Tiền gửi=0.1%/yr · Borrow=10%/yr ·
  HT+Rec: sau mỗi lần thoát CRISIS → tăng lên 130% trong 20 phiên tiếp theo ·
  Màu <span style="color:#4ade80">xanh</span> = dương · <span style="color:#f87171">đỏ</span> = âm · Rank:
  <span style="background:#14532d;color:#86efac;padding:1px 5px;border-radius:3px">≥70%</span>
  <span style="background:#7f1d1d;color:#fca5a5;padding:1px 5px;border-radius:3px">&lt;45%</span>
</div>

<script>
let activeFilter = 'all';
function setFilter(f) {{
  activeFilter = f;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  const m = {{'all':'btn-all','down':'btn-down','up':'btn-up',
              'CRISIS':'btn-crisis','BEAR':'btn-bear','NEUTRAL':'btn-neutral',
              'BULL':'btn-bull','EX-BULL':'btn-exbull'}};
  if (m[f]) document.getElementById(m[f]).classList.add('active');
  applyFilters();
}}
function applyFilters() {{
  const q = document.getElementById('search').value.toLowerCase();
  const rows = document.querySelectorAll('#tbody tr');
  let vis = 0;
  rows.forEach(r => {{
    const from = (r.dataset.from||'').toLowerCase();
    const to   = (r.dataset.to||'').toLowerCase();
    const date = (r.dataset.date||'').toLowerCase();
    const dir  = (r.dataset.dir||'').toLowerCase();
    let show = true;
    if (activeFilter === 'down' && dir !== 'down') show = false;
    else if (activeFilter === 'up' && dir !== 'up') show = false;
    else if (activeFilter === 'CRISIS'  && to !== 'crisis'  && from !== 'crisis')  show = false;
    else if (activeFilter === 'BEAR'    && to !== 'bear'    && from !== 'bear')    show = false;
    else if (activeFilter === 'NEUTRAL' && to !== 'neutral' && from !== 'neutral') show = false;
    else if (activeFilter === 'BULL'    && to !== 'bull'    && from !== 'bull')    show = false;
    else if (activeFilter === 'EX-BULL' && to !== 'ex-bull' && from !== 'ex-bull') show = false;
    if (show && q && !(date.includes(q) || from.includes(q) || to.includes(q))) show = false;
    r.classList.toggle('hidden', !show);
    if (show) vis++;
  }});
  document.getElementById('count-info').textContent = `${{vis}} / ${{rows.length}} dòng`;
}}
applyFilters();
</script>
</body>
</html>"""

out_path = WORKDIR + "/backtest_detail_2011.html"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Saved: {out_path}")
print(f"\nTransitions 2011+: {n_tr_2011}")
print(f"CRISIS: {n_crisis} | BEAR: {n_bear} | NEUTRAL: {n_neutral} | BULL: {n_bull} | EX-BULL: {n_exbull}")
print(f"NAV cuối HT+Rec: {final_rec:.2f}t | B&H: {final_bh:.2f}t")
print(f"Trạng thái hiện tại: {curr_name}")
