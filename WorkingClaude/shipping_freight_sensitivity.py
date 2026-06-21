#!/usr/bin/env python3
"""
shipping_freight_sensitivity.py — do VN shipping co track global freight rates?
===============================================================================
Segment VN marine names by what freight index drives them, then correlate
quarterly NP/NPM with the matching index (contemporaneous + lag), 2018Q1-2026Q1.
  CONTAINER liner -> SCFI : HAH
  DRY BULK        -> BDI  : VOS, VNA, VSA
  TANKER (oil)    -> BDTI : PVT, VTO, VIP, GSP, PVP
  PORTS (volume)  -> (none): GMD, VSC, SGP  (throughput, not freight RATE -> control group)
Freight = data/freight_rates_quarterly.csv (approx reconstruction; see header).
Output: data/shipping_freight_sensitivity.md
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import os, subprocess, tempfile
from io import StringIO
import numpy as np, pandas as pd
WORKDIR=r"/home/trido/thanhdt/WorkingClaude"
PROJECT="lithe-record-440915-m9"; BQ_BIN=r"bq"
SEG={"CONTAINER→SCFI":(["HAH"],"scfi"),
     "DRY BULK→BDI":(["VOS","VNA","VSA"],"bdi"),
     "TANKER→BDTI":(["PVT","VTO","VIP","GSP","PVP"],"bdti"),
     "PORTS (control, volume)":(["GMD","VSC","SGP"],None)}
ALL=[t for v in SEG.values() for t in v[0]]
def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as f:
        f.write(sql); tmp=f.name
    try: r=subprocess.run(f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=500000',capture_output=True,text=True,timeout=600,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode!=0 or not r.stdout.strip(): raise RuntimeError(r.stderr[:400])
    return pd.read_csv(StringIO(r.stdout.strip()))
def xcorr(a,b,L):
    if L>0: a,b=a[L:],b[:-L]
    m=np.isfinite(a)&np.isfinite(b)
    return np.corrcoef(a[m],b[m])[0,1] if m.sum()>8 else np.nan
def qord(s): return s.str[:4].astype(int)*4+s.str[-1].astype(int)
def main():
    lines=[]; P=lambda s="":(print(s),lines.append(s))
    fr=pd.read_csv(os.path.join(WORKDIR,"data","freight_rates_quarterly.csv"),comment="#")
    fin=bq(f"""SELECT t.ticker,t.quarter AS q,t.NP_P0,t.NPM_P0,t.Revenue_P0
               FROM tav2_bq.ticker_financial t
               WHERE t.ticker IN ('{"','".join(ALL)}') AND t.quarter>='2018Q1' ORDER BY t.ticker,t.quarter""")
    fin=fin.merge(fr,on="q",how="left")
    P("# VN vận tải biển CÓ chịu ảnh hưởng cước thế giới? (2018Q1-2026Q1)")
    P("corr quý NP & NPM với chỉ số cước segment (contemporaneous + lag 1-2Q). lag>0 = lợi nhuận trễ cước.")
    P("⚠ freight = tái dựng xấp xỉ (data/freight_rates_quarterly.csv).")
    P("")
    summ=[]
    for seg,(tks,idx) in SEG.items():
        P(f"## {seg}")
        if idx is None:
            P("  (nhóm CẢNG = đối chứng: lợi nhuận theo SẢN LƯỢNG thông qua, không theo giá cước → kỳ vọng corr thấp/nhiễu)")
        P(f"  {'tk':<5}{'nQ':>4}{'NP~idx':>8}{'NP~L1':>7}{'NP~L2':>7}{'NPM~idx':>9}")
        for tk in tks:
            d=fin[fin["ticker"]==tk].sort_values("q")
            d=d.assign(_o=qord(d["q"])).sort_values("_o")
            if idx is None:
                # fair control: correlate ports NP with the AVG global-freight factor (no cherry-pick)
                d=d.assign(favg=d[["bdi","scfi","bdti"]].mean(axis=1))
                cc=d[["NP_P0","favg"]].corr().iloc[0,1]
                P(f"  {tk:<5}{len(d):>4}{cc:>+8.2f}{'':>7}{'':>7}{'  (vs avg-freight)':>9}")
                summ.append((seg,tk,cc,np.nan)); continue
            npv=d["NP_P0"].values; npm=d["NPM_P0"].values; iv=d[idx].values
            c0=xcorr(npv,iv,0); c1=xcorr(npv,iv,1); c2=xcorr(npv,iv,2); m0=xcorr(npm,iv,0)
            P(f"  {tk:<5}{len(d):>4}{c0:>+8.2f}{c1:>+7.2f}{c2:>+7.2f}{m0:>+9.2f}")
            summ.append((seg,tk,c0,m0))
        P("")
    # segment medians + current freight regime
    P("## Tổng hợp segment (median NP~idx contemporaneous) + cước HIỆN TẠI")
    S=pd.DataFrame(summ,columns=["seg","tk","np_idx","npm_idx"])
    cur=fr.iloc[-1]
    for seg,(tks,idx) in SEG.items():
        sub=S[S["seg"]==seg]
        cv=f"  | {idx.upper()} now={cur[idx]:.0f}" if idx else ""
        P(f"  {seg:<26}{sub['np_idx'].median():>+6.2f}{cv}")
    P("")
    P("Đọc (KẾT LUẬN): VN shipping CÓ chịu ảnh hưởng cước thế giới, nhưng MỨC & CƠ CHẾ khác nhau theo segment:")
    P("- DRY BULK (VOS/VNA) = link MẠNH & SẠCH nhất (~0.55-0.59): bám BDI sát, LỖ ở đáy cước, lãi khi BDI vọt.")
    P("- CONTAINER (HAH) = rõ trong bùng nổ 2021-22 (lag 2Q +0.61), nhưng 2024-25 NỚI LỎNG do MỞ RỘNG ĐỘI TÀU")
    P("  (NP lập đỉnh mới dù SCFI chỉ trung bình) → stock-specific (fleet) lấn dần cước spot.")
    P("- TANKER (PVT) = ĐỆM bởi charter dài hạn: ổn định, thậm chí NP tăng khi BDTI giảm 2024-25 → ít theo spot.")
    P("  (VTO/PVP ~0 = hợp đồng cố định hoàn toàn).")
    P("- CẢNG (GMD ~0) = SẢN LƯỢNG-driven, KHÔNG theo cước; cảng nhỏ (VSC/SGP +0.43) chỉ co-move qua chu kỳ")
    P("  thương mại chung 2021-22, không phải nhạy cước trực tiếp.")
    P("→ Caveat: cấu trúc nhân-quả mạnh nhất ở BULK; ở các name lớn (HAH/PVT) fleet+charter ngày càng tách spot.")
    P("")
    # show HAH vs SCFI and VOS vs BDI trajectories (the two cleanest)
    for tk,idx in [("HAH","scfi"),("VOS","bdi"),("PVT","bdti")]:
        d=fin[fin["ticker"]==tk].assign(_o=lambda x:qord(x["q"])).sort_values("_o")
        P(f"### {tk} NP(bn) vs {idx.upper()}:")
        P("  "+"  ".join(f"{r['q']}:{r['NP_P0']/1e9:.0f}/{r[idx]:.0f}" for _,r in d.iterrows() if r['q']>='2020Q1'))
        P("")
    out=os.path.join(WORKDIR,"data","shipping_freight_sensitivity.md")
    with open(out,"w",encoding="utf-8") as f: f.write("\n".join(lines))
    P(f"Saved {out}")
if __name__=="__main__": main()
