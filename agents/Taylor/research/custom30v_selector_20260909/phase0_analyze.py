# -*- coding: utf-8 -*-
"""Phase 0 phan tich — doc daily_contrib.parquet do phase0_describe.py sinh ra."""
import os, sys
import numpy as np, pandas as pd
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
OUT = os.path.join(WORKDIR, "mike/agents/Taylor/research/custom30v_selector_20260909")
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
os.environ.setdefault("BQ_CACHE_THREADS", "1")
from simulate_holistic_nav import bq
pd.set_option("display.width", 200)

D = pd.read_parquet(f"{OUT}/daily_contrib.parquet")
ret = pd.read_csv(f"{OUT}/basket_daily_return.csv", index_col=0, parse_dates=[0])["ret"]; ret.index.name="time"
mem = pd.read_csv(f"{OUT}/members.csv", parse_dates=["rebal_date"])
lv = (1 + ret).cumprod()

def rep(t): print(t); LOG.append(t)
LOG = []

# ---------- 1. loi suat theo nam ----------
rep("\n## 1. LOI SUAT RO THEO NAM (gross, khong phi, khong tien mat)")
yr = ret.groupby(ret.index.year).apply(lambda s: (1+s).prod()-1)
vni = bq("""SELECT time, Close FROM tav2_bq.ticker WHERE ticker='VNINDEX'
AND time BETWEEN DATE '2013-12-25' AND DATE '2026-06-19' ORDER BY time""")
vni["time"] = pd.to_datetime(vni["time"]); vni = vni.set_index("time")["Close"]
vni = vni.reindex(ret.index).ffill()
vr = vni.pct_change().fillna(0)
vyr = vr.groupby(vr.index.year).apply(lambda s: (1+s).prod()-1)
tab = pd.DataFrame({"basket_%": yr*100, "vnindex_%": vyr*100})
tab["excess_pp"] = tab["basket_%"] - tab["vnindex_%"]
tab["n_phien"] = ret.groupby(ret.index.year).size()
rep(tab.round(2).to_string())
_ann = (1+ret).prod()**(365.25/((ret.index[-1]-ret.index[0]).days))-1
rep(f"\nCAGR ro (lich) = {_ann*100:.2f}%  |  level cuoi {lv.iloc[-1]:.3f}x  |  "
    f"vol nam hoa {ret.std()*np.sqrt(252)*100:.1f}%  |  Sharpe(rf=0) {ret.mean()/ret.std()*np.sqrt(252):.2f}")
_dd = (lv/lv.cummax()-1)
rep(f"MaxDD ro = {_dd.min()*100:.2f}% ngay {_dd.idxmin().date()}")

# ---------- 2. theo state DT5G ----------
rep("\n## 2. LOI SUAT THEO STATE DT5G (vnindex_5state_dt5g_live)")
st = bq("""SELECT time, state FROM tav2_bq.vnindex_5state_dt5g_live
WHERE time BETWEEN DATE '2014-01-02' AND DATE '2026-06-19' ORDER BY time""")
st["time"] = pd.to_datetime(st["time"]); st = st.set_index("time")["state"].reindex(ret.index).ffill()
NM = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EXBULL"}
rr = []
for s, g in ret.groupby(st):
    gv = vr[g.index]
    rr.append(dict(state=f"{int(s)} {NM.get(int(s),'?')}", n_phien=len(g),
                   pct_thoigian=100*len(g)/len(ret),
                   ann_basket=100*((1+g).prod()**(252/len(g))-1),
                   ann_vni=100*((1+gv).prod()**(252/len(gv))-1),
                   tong_gop_diem=float(D[D.time.isin(g.index)].contrib.sum())))
S = pd.DataFrame(rr); S["excess_pp"] = S.ann_basket - S.ann_vni
S["pct_tong_lai"] = 100*S.tong_gop_diem/S.tong_gop_diem.sum()
rep(S.round(2).to_string(index=False))

# ---------- 3. dong gop theo TEN ----------
rep("\n## 3. DONG GOP THEO TEN (diem chi so; tong = level_cuoi - 1)")
byname = D.groupby("ticker").agg(gop=("contrib","sum"), n_ngay=("time","size"),
                                 w_tb=("w","mean")).sort_values("gop", ascending=False)
byname["pct_tong"] = 100*byname.gop/byname.gop.sum()
tot = byname.gop.sum()
rep(f"tong ten tung nam trong ro: {len(byname)}  |  tong gop {tot:.3f} diem")
rep("\nTOP 15:"); rep(byname.head(15).round(3).to_string())
rep("\nBOTTOM 10:"); rep(byname.tail(10).round(3).to_string())
pos = byname[byname.gop>0].gop.sort_values(ascending=False)
rep(f"\nSo ten dong gop DUONG: {len(pos)}/{len(byname)} ({100*len(pos)/len(byname):.1f}%)")
for k in (1,3,5,10,20):
    rep(f"  top-{k:<2d} ten = {100*pos.head(k).sum()/tot:6.2f}% tong lai ro")
rep(f"  top-decile ten ({max(1,len(byname)//10)} ten) = {100*pos.head(max(1,len(byname)//10)).sum()/tot:.2f}% tong lai")
byname.to_csv(f"{OUT}/contrib_by_name.csv")

# ---------- 4. NGANH ----------
rep("\n## 4. TAP TRUNG NGANH (route PIT tu value_panel_2014.csv, trong so THAT theo ngay)")
vp = pd.read_csv(f"{WORKDIR}/data/value_panel_2014.csv", parse_dates=["time"],
                 usecols=["ticker","time","route","ICB_Code"])
vp["qstart"] = vp["time"].dt.to_period("Q").dt.start_time
rt = vp.dropna(subset=["route"]).sort_values("time").groupby(["ticker","qstart"])["route"].last()
rt_hist = {tk: (list(g.index.get_level_values(1)), list(g.values)) for tk, g in rt.groupby(level=0)}
import bisect as _b
def route_asof(tk, q):
    e = rt_hist.get(tk)
    if not e: return "UNKNOWN"
    i = _b.bisect_right(e[0], pd.Timestamp(q)) - 1
    return e[1][i] if i >= 0 else e[1][0]
D["q"] = D["time"].dt.to_period("Q").dt.start_time
_key = D[["ticker","q"]].drop_duplicates()
_key["route"] = [route_asof(t, q) for t, q in zip(_key.ticker, _key.q)]
D = D.merge(_key, on=["ticker","q"], how="left")
FIN = {"BANK","INSURANCE","SECURITIES"}
D["is_fin"] = D.route.isin(FIN)
daily_fin = D.groupby("time").apply(lambda g: (g.w*g.is_fin).sum()/g.w.sum())
rep(f"Ty trong TAI CHINH (BANK+INS+SEC) theo NGAY: TB {daily_fin.mean()*100:.1f}% | "
    f"trung vi {daily_fin.median()*100:.1f}% | max {daily_fin.max()*100:.1f}% ({daily_fin.idxmax().date()})")
_is = daily_fin[daily_fin.index < "2020-01-01"]; _oos = daily_fin[daily_fin.index >= "2020-01-01"]
rep(f"  IS 2014-19 TB {_is.mean()*100:.1f}%   |   OOS 2020+ TB {_oos.mean()*100:.1f}%")
bankonly = D.assign(b=D.route=="BANK").groupby("time").apply(lambda g:(g.w*g.b).sum()/g.w.sum())
rep(f"  Rieng BANK: TB {bankonly.mean()*100:.1f}% | OOS 2020+ {bankonly[bankonly.index>='2020-01-01'].mean()*100:.1f}%")
rep("\nTy trong TB + dong gop theo ROUTE:")
rw = D.groupby("route").apply(lambda g: pd.Series({
    "w_share_%": 100*g.w.sum()/D.w.sum(), "gop_diem": g.contrib.sum(),
    "pct_tong_lai": 100*g.contrib.sum()/tot, "n_ten": g.ticker.nunique()}))
rep(rw.sort_values("w_share_%", ascending=False).round(2).to_string())
daily_fin.to_csv(f"{OUT}/daily_fin_weight.csv", header=["fin_w"])

# ---------- 5. VI THE (khung B0 giong vong 3 BAL) ----------
rep("\n## 5. PHAN PHOI VI THE (1 vi the = 1 ten x 1 ky rebal; vao gia dong cua ngay rebal)")
P = D.groupby(["rebal_date","ticker"]).apply(lambda g: pd.Series({
    "ret": float((1+g.sort_values("time").r).prod()-1),
    "w0": float(g.sort_values("time").w.iloc[0]),
    "gop": float(g.contrib.sum()), "n_ngay": len(g)})).reset_index()
P["year"] = P.rebal_date.dt.year
P.to_csv(f"{OUT}/positions.csv", index=False)
def frame(g):
    r = g.ret.values; gp = g.gop.values
    win = gp[gp>0]
    return pd.Series({"n":len(g), "mean_%":100*r.mean(), "median_%":100*np.median(r),
        "hit_%":100*(r>0).mean(), "skew":float(pd.Series(r).skew()),
        "top3_share_gain_%":100*np.sort(win)[::-1][:3].sum()/win.sum() if len(win) else np.nan,
        "topdec_share_gain_%":100*np.sort(win)[::-1][:max(1,len(g)//10)].sum()/win.sum() if len(win) else np.nan})
rep("\nTheo nam:"); rep(P.groupby("year").apply(frame).round(2).to_string())
rep("\nTOAN KY:"); rep(frame(P).round(2).to_string())

# ---------- 6. TURNOVER ----------
rep("\n## 6. TURNOVER / THAY MA")
mm = {d: set(g.ticker) for d, g in mem.groupby("rebal_date")}
ds = sorted(mm)
tv = []
for a, b in zip(ds, ds[1:]):
    tv.append(dict(rebal=b.date(), moi=len(mm[b]-mm[a]), giu=len(mm[b]&mm[a]),
                   turnover_pct=100*len(mm[b]-mm[a])/len(mm[b])))
T = pd.DataFrame(tv)
rep(f"48 rebal, {len(T)} lan doi. Ten MOI moi ky: TB {T.moi.mean():.1f}/30 "
    f"(trung vi {T.moi.median():.0f}, min {T.moi.min()}, max {T.moi.max()}) "
    f"= turnover TB {T.turnover_pct.mean():.1f}%/quy (~{T.turnover_pct.mean()*4:.0f}%/nam mot chieu)")
rep(f"So ky mot ten nam trong ro (tuoi tho): TB {mem.groupby('ticker').size().mean():.1f} ky, "
    f"trung vi {mem.groupby('ticker').size().median():.0f}, max {mem.groupby('ticker').size().max()}")
T.to_csv(f"{OUT}/turnover.csv", index=False)

# ---------- 7. PHU THUOC DUOI PHAI ----------
rep("\n## 7. PHU THUOC DUOI PHAI — ro co giong BAL khong?")
rep(f"  BAL (vong 3, 268 lenh):  median 4.15% | hit 58.2% | skew 1.31 | top-decile 57.2% tong lai")
f = frame(P)
rep(f"  custom30V ({len(P)} vi the): median {f['median_%']:.2f}% | hit {f['hit_%']:.1f}% | "
    f"skew {f['skew']:.2f} | top-decile {f['topdec_share_gain_%']:.1f}% tong lai")
# do o cap TEN (money-weighted) -- cau hoi that su la 'tien co trai deu khong'
rep(f"  Cap TEN (money-weighted): top-decile ten = {100*pos.head(max(1,len(byname)//10)).sum()/tot:.1f}% tong lai ro")
# neu bo top-k ten thi CAGR con bao nhieu
for k in (1,3,5):
    dd = D[~D.ticker.isin(list(pos.head(k).index))]
    rr2 = dd.groupby("time").apply(lambda g:(g.w*g.r).sum()/max(g.w.sum(),1e-12))
    rr2 = rr2.reindex(ret.index).fillna(0)
    a = (1+rr2).prod()**(365.25/((ret.index[-1]-ret.index[0]).days))-1
    rep(f"  Bo {k} ten dong gop lon nhat (tai chuan hoa trong so): CAGR {a*100:.2f}% vs {_ann*100:.2f}% goc "
        f"(-{(_ann-a)*100:.2f}pp)")

open(f"{OUT}/phase0_report_raw.txt","w").write("\n".join(LOG))
print("\n[done] ->", OUT)
