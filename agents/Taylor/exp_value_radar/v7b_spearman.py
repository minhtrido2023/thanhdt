"""Bo sung: Spearman lien tuc radar3_roll vs ket cuc tren 26 su kien CAPIT + cong don da kiem dinh."""
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from scipy import stats
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_value_radar/'
m=pd.read_csv(EXP+'washout_radar.csv',parse_dates=['event'])
rd=pd.read_csv(EXP+'radar.csv',parse_dates=['time'])
idx=rd.time.values
need={'r3M':63,'r6M':126,'r12M':252,'mdd12M':252}
rows=[]
for col,nd in need.items():
    s=m[[ (idx>np.datetime64(e)).sum()>=nd for e in m.event]].dropna(subset=['radar3_roll',col])
    rho,p=stats.spearmanr(s.radar3_roll,s[col])
    rows.append(dict(test='Spearman radar_roll ~ %s'%col,N=len(s),rho=rho,p=p))
    # doi chieu: ban expanding (da bao cao) tren cung mau
    rho2,p2=stats.spearmanr(s.radar3,s[col])
    rows.append(dict(test='  (doi chieu) radar_expanding ~ %s'%col,N=len(s),rho=rho2,p=p2))
T=pd.DataFrame(rows); print(T.round(4).to_string(index=False))
T.to_csv(EXP+'washout_radar_spearman.csv',index=False)

print('\n--- cong don da kiem dinh trong CUNG mach nghien cuu 07-29/07-30 ---')
fam={'PhuLuc A (ROE, NO-GO)':12,'PhuLuc B (PB ex-VIC, 9 cach do)':9,
     'fundamental_valuation_framework Viec 2':56,'PhuLuc C (17 lang kinh + 4 bien the radar + 2 nguong)':23,
     'BAO CAO NAY (6 nhom + 4 Spearman)':10}
tot=sum(fam.values())
for k,v in fam.items(): print('  %-58s %3d'%(k,v))
print('  %-58s %3d'%('TONG N_trials tich luy',tot))
print('  nguong Bonferroni 5%%  = %.5f'%(0.05/tot))
print('  nguong BH(FDR 10%%) cho p NHO NHAT = %.5f'%(0.10/tot))
pmin_day=0.049  # hieu RE-DAT C.4.4, p nho nhat cua CA mach trong ngay
pmin_new=min([r['p'] for r in rows]+[0.2777])
print('  p nho nhat cua CA mach (C.4.4 RE-DAT)      = %.4f  -> qua BH? %s'%(pmin_day,'CO' if pmin_day<=0.10/tot else 'KHONG'))
print('  p nho nhat cua RIENG bao cao nay           = %.4f  -> qua BH? %s'%(pmin_new,'CO' if pmin_new<=0.10/tot else 'KHONG'))
