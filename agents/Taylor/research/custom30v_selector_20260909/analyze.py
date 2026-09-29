"""VONG 4 custom30V selector — cham theo 7 tieu chi tien dang ky (PREREG §5) + doi chung §6.
job Taylor_20260909_153631, PAPER-ONLY. Chi doc CSV do run_leg.sh sinh ra."""
import hashlib, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dsr_pbo_annex import load_nav, daily_logret, moments, dsr, expected_max_sr, cscv_pbo  # noqa

_D = "/home/trido/thanhdt/WorkingClaude/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_univpit"
# BASKET_SELECT=eycfq them _sel_tag rieng vao ten file (coding_guidelines §8) -> map tuong minh
_PATH = {"ctrl": f"{_D}_exp_c30vselctrl.csv", "L1a": f"{_D}_exp_c30vsell1a.csv",
         "L1b": f"{_D}_exp_c30vsell1b.csv", "L2": f"{_D}_exp_seleycfq_exp_c30vsell2.csv",
         "L3": f"{_D}_exp_c30vsell3.csv"}
class _B:
    def __mod__(self, t): return _PATH[t]
B = _B()
LEGS = ["ctrl", "L1a", "L1b", "L2", "L3"]; CTRL = "ctrl"
N_TRIALS = 4                       # L1a, L1b, L2, L3 — toan bo be rong tim kiem cua job nay
BLOCK = 63                         # PREREG §2: 1 quy = 1 chu ky rebal (KHONG phai 21 nhu vong 3)
PIN = dict(cagr=28.8627, final_B=1178.0099, calmar=1.6229, maxdd=-17.785,
           md5="7d053e6201c9d107685ff4d1dd9d2d2a")
pd.set_option("display.width", 250)

nav, raw = {}, {}
for t in LEGS:
    p = B % t
    if not os.path.exists(p): print("MISSING", p); continue
    nav[t] = load_nav(p); raw[t] = pd.read_csv(p, low_memory=False)

md5 = hashlib.md5(open(B % CTRL, "rb").read()).hexdigest()
print("=== C7: CONTROL vs PIN R3 ===")
print(f"  control md5 = {md5}  pin = {PIN['md5']}  -> "
      f"{'MATCH' if md5 == PIN['md5'] else '*** MISMATCH — DUNG, khong doc so treatment ***'}")

def metrics(s):
    r = daily_logret(s); yrs = (s.index[-1]-s.index[0]).days/365.25
    cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs)-1; dd = (s/s.cummax()-1).min()
    return dict(cagr=cagr*100, maxdd=dd*100, calmar=cagr/abs(dd),
                sharpe=r.mean()/r.std(ddof=1)*np.sqrt(252), final_B=s.iloc[-1]/1e9)
def sub(s,a,b): return s[(s.index>=a)&(s.index<=b)]

rows=[]
for t in LEGS:
    if t not in nav: continue
    s=nav[t]; rows.append(dict(leg=t, **metrics(s),
        cagr_IS=metrics(sub(s,"2014-01-01","2019-12-31"))["cagr"],
        cagr_OOS=metrics(sub(s,"2020-01-01","2026-06-19"))["cagr"]))
T=pd.DataFrame(rows); c=T[T.leg==CTRL].iloc[0]
for k in ["cagr","cagr_IS","cagr_OOS","calmar","sharpe","maxdd"]: T["d_"+k]=T[k]-c[k]
print(f"  ctrl CAGR {c['cagr']:.4f} (pin {PIN['cagr']}) | NAV {c['final_B']:.4f}B (pin {PIN['final_B']}) "
      f"| Calmar {c['calmar']:.4f} | MaxDD {c['maxdd']:.3f}")
print("\n=== A/B metrics (C1 nguong +0.385pp / C2 Calmar>=ctrl / C3 IS&OOS cung duong) ===")
print(T.round(4).to_string(index=False)); T.to_csv("ab_metrics.csv", index=False)
print("\n  C1/C2/C3:")
for _,r in T[T.leg!=CTRL].iterrows():
    print(f"   {r.leg:4s} C1 dCAGR={r.d_cagr:+.3f}pp {'PASS' if r.d_cagr>0.385 else 'FAIL'} | "
          f"C2 Calmar={r.calmar:.4f} {'PASS' if r.calmar>=c['calmar'] else 'FAIL'} | "
          f"C3 IS={r.d_cagr_IS:+.2f} OOS={r.d_cagr_OOS:+.2f} "
          f"{'PASS' if (r.d_cagr_IS>0 and r.d_cagr_OOS>0) else 'FAIL'}")

# ---- C4a per-year ----
yr={}
for t in LEGS:
    if t not in nav: continue
    s=nav[t]; out={}
    for y,g in s.groupby(s.index.year):
        prev=s[s.index<g.index[0]]; s0=prev.iloc[-1] if len(prev) else g.iloc[0]
        out[y]=(g.iloc[-1]/s0-1)*100
    yr[t]=pd.Series(out)
Y=pd.DataFrame(yr)
for t in list(Y.columns):
    if t!=CTRL: Y["d_"+t]=Y[t]-Y[CTRL]
print("\n=== loi suat theo nam + delta vs ctrl (C4a) ==="); print(Y.round(2).to_string()); Y.to_csv("peryear.csv")

# ---- C4b per-window ----
W=pd.read_csv("../bal_2025_diagnosis_20260909/p1_bull_windows.csv", parse_dates=["start","end"])
starts=list(W["start"])+[pd.Timestamp("2100-01-01")]
def lr(t):
    v=daily_logret(nav[t]); return pd.Series(v, index=nav[t].index[1:])
rc_s=lr(CTRL); rc=daily_logret(nav[CTRL])
pw=[]
for t in LEGS:
    if t==CTRL or t not in nav: continue
    d=(lr(t)-rc_s).dropna()
    rec={"leg":t,"total_dlogret_pp":d.sum()*100,"pre_first_window_pp":d[d.index<starts[0]].sum()*100}
    for i in range(len(W)):
        rec[f"W{i+1}_{W['start'].iloc[i].date()}"]=d[(d.index>=starts[i])&(d.index<starts[i+1])].sum()*100
    pw.append(rec)
PW=pd.DataFrame(pw).set_index("leg")
print("\n=== delta theo CUA SO regime (C4b) ==="); print(PW.round(3).T.to_string()); PW.to_csv("perwindow.csv")
def conc(v,tot): return np.nan if abs(tot)<1e-12 else float(np.max(np.abs(v))/abs(tot))
print("\n=== C4a/C4b tap trung (FAIL neu > 0.50) ===")
for t in [x for x in LEGS if x!=CTRL and x in nav]:
    ca=conc(Y["d_"+t].values, Y["d_"+t].sum())
    cb=conc(PW.loc[t].drop("total_dlogret_pp").values, PW.loc[t,"total_dlogret_pp"])
    print(f"  {t:4s} C4a_nam={ca:7.2f}  C4b_cuaso={cb:7.2f}   {'PASS' if (ca<=0.5 and cb<=0.5) else 'FAIL'}")

# ---- C5 DSR / PBO ----
treat=[t for t in LEGS if t!=CTRL and t in nav]
sr_c=rc.mean()/rc.std(ddof=1)
srs=[daily_logret(nav[t]).mean()/daily_logret(nav[t]).std(ddof=1) for t in treat]
var_sr=np.var(srs,ddof=1) if len(srs)>1 else 0.0
sr0=expected_max_sr(var_sr,N_TRIALS) if var_sr>0 else 0.0
print(f"\n=== C5a DSR (null = SR ctrl {sr_c:.5f}/obs; SR0(N={N_TRIALS})={sr0:.5f}) ===")
for t in treat:
    rb=daily_logret(nav[t]); sh,g3,g4=moments(rb)
    v=dsr(sh,sr_c,g3,g4,len(rb))[0]
    print(f"  {t:4s} DSR_vs_SRctrl={v:.6f}  DSR_vs_SR0={dsr(sh,sr0,g3,g4,len(rb))[0]:.6f}  {'PASS' if v>0.95 else 'FAIL'}")
M=np.column_stack([daily_logret(nav[t]) for t in LEGS if t in nav])
pbo=cscv_pbo(M,S=16)[0]
print(f"\n=== C5b PBO (CSCV S=16, {M.shape[1]} config) = {pbo:.4f}  {'PASS' if pbo<0.5 else 'FAIL'} ===")

# ---- C6 block bootstrap L=63 ----
def cbb(r,L=BLOCK,Bn=4000,seed=12345):
    rng=np.random.default_rng(seed); n=len(r); nb=int(np.ceil(n/L)); out=np.empty(Bn)
    for b in range(Bn):
        st=rng.integers(0,n,nb)
        idx=np.concatenate([(np.arange(s,s+L)%n) for s in st])[:n]
        out[b]=r[idx].sum()
    return out
yrs=(nav[CTRL].index[-1]-nav[CTRL].index[0]).days/365.25
print(f"\n=== C6 block bootstrap L={BLOCK} B=4000 tren chuoi delta log-return ===")
for t in treat:
    d=(lr(t)-rc_s).dropna().values; bs=cbb(d)/yrs*100
    lo,hi=np.percentile(bs,2.5),np.percentile(bs,97.5)
    print("  %-4s point=%+.3f pp/yr  CI95=[%+.3f, %+.3f]  P(d>0)=%.3f  %s"
          %(t,d.sum()/yrs*100,lo,hi,(bs>0).mean(),"LOAI TRU 0 -> PASS" if (lo>0 or hi<0) else "om 0 -> FAIL"))

# ---- §6 doi chung bat buoc ----
print("\n=== §6.1 EXPOSURE tren phien NEUTRAL (state=3) ===")
dec=[]
for t in LEGS:
    if t not in raw: continue
    D=raw[t]; D=D[D.record_type.astype(str).str.lower().str.startswith("daily")]
    D=D[D["nav_bal_ref"].notna()].copy(); D["ymd"]=pd.to_datetime(D["ymd"])
    D=D.drop_duplicates("ymd").set_index("ymd").sort_index()
    n3=D["state"]==3
    ws=(D["bal_stocks_ref"]/D["nav_bal_ref"])[n3]; wp=(D["bal_etf_ref"]/D["nav_bal_ref"])[n3]
    dec.append(dict(leg=t,n_neutral=int(n3.sum()),w_stock=ws.mean()*100,w_park=wp.mean()*100,
                    w_equity=(ws+wp).mean()*100))
DEC=pd.DataFrame(dec).set_index("leg")
for k in ["w_stock","w_park","w_equity"]: DEC["d_"+k]=DEC[k]-DEC.loc[CTRL,k]
print(DEC.round(3).to_string()); DEC.to_csv("exposure_decomp.csv")

print("\n=== §6.2 TY LE TEN TAI CHINH trong ro + §6.4 TURNOVER (tu CUSTOM_MEMBERS) ===")
vp=pd.read_csv("/home/trido/thanhdt/WorkingClaude/data/value_panel_2014.csv",parse_dates=["time"],
               usecols=["ticker","time","route"])
vp["q"]=vp["time"].dt.to_period("Q").dt.start_time
rt=vp.dropna(subset=["route"]).sort_values("time").groupby(["ticker","q"])["route"].last()
import bisect as _b
rh={tk:(list(g.index.get_level_values(1)),list(g.values)) for tk,g in rt.groupby(level=0)}
def route_asof(tk,q):
    e=rh.get(tk)
    if not e: return "UNKNOWN"
    i=_b.bisect_right(e[0],pd.Timestamp(q))-1
    return e[1][i] if i>=0 else e[1][0]
FIN={"BANK","INSURANCE","SECURITIES"}
mrows=[]
for t in LEGS:
    if t not in raw: continue
    M2=raw[t]; M2=M2[M2.record_type=="CUSTOM_MEMBERS"].copy()
    M2["ymd"]=pd.to_datetime(M2["ymd"])
    mm={d:list(g.ticker) for d,g in M2.groupby("ymd")}
    ds=sorted(mm)
    fin=[]; bank=[]
    for d in ds:
        q=pd.Timestamp(d).to_period("Q").start_time
        fin.append(np.mean([route_asof(x,q) in FIN for x in mm[d]]))
        bank.append(np.mean([route_asof(x,q)=="BANK" for x in mm[d]]))
    tovr=[len(set(mm[b])-set(mm[a]))/len(mm[b]) for a,b in zip(ds,ds[1:])]
    mrows.append(dict(leg=t,n_rebal=len(ds),fin_name_share=100*np.mean(fin),
                      bank_name_share=100*np.mean(bank),turnover_pct_q=100*np.mean(tovr)))
MM=pd.DataFrame(mrows).set_index("leg")
for k in ["fin_name_share","bank_name_share","turnover_pct_q"]: MM["d_"+k]=MM[k]-MM.loc[CTRL,k]
print(MM.round(2).to_string()); MM.to_csv("members_decomp.csv")
print("\nLuat doc chot truoc (PREREG §6): |d_w_equity|>2pp => doi rui ro chu khong phai chon ma;"
      "\n  |d_fin_name_share|>5pp => cuoc nganh, phai bao nhu cuoc nganh; turnover>1.5x ctrl => tru chi phi that.")
