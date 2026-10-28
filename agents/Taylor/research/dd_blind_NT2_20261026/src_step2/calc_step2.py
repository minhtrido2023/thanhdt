# Buoc 2: percentile bien LNST TTM sau dinh chinh soat xet H1/26 + Q3 BCTC; ADV20
import pandas as pd
s=pd.read_csv('src_step1/nt2_ttm_series.csv')
hist=s[s.quarter<'2026Q2'].npm_ttm.dropna()   # lich su truoc diem dang xet
def pct(x,v): return 100*(x<v).mean()
cases={'blind_Q2_BQ':1350.0/9446.0,
       'Q2_reviewed':(214.233+552.840+487.743)/(1928.237+2522.019+4996.203),
       'Q3_BCTC':(552.840+906.356)/(2522.019+7803.426)}
for k,v in cases.items(): print(k, round(100*v,2),'% pct',round(pct(hist,v),1),'N',len(hist))
# cash gross margin Q3 (GP + khau hao quy)
for y,gp,rev,dep in [(2026,489.869,2807.223,114.825-76.5),(2025,204.588,1928.237,515.807-343.5)]:
    print(y,'GM',round(100*gp/rev,2),'cashGM',round(100*(gp+dep)/rev,2),'dep',round(dep,1))
px=pd.read_csv('src_step2/nt2_px.csv'); t=px.tail(20)
print('ADV20 mean',round(t.tv_bn.mean(),1),'median',round(t.tv_bn.median(),1))
