import sys; sys.dont_write_bytecode=True
sys.path.insert(0,'/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/dd_MVC_20261103/calc')
import valuation as M, copy
W=M.W; SCN=M.SCN
def mid():
    return (sum(W[k]*M.value(k,'flat') for k in SCN)+sum(W[k]*M.value(k,'real') for k in SCN))/2
b=mid()
for lab,attr in [('LAND','LAND'),('BOT_YRS','BOT_YRS'),('END_A','END_A'),('ASSOC_K','ASSOC_K'),('ICD_K','ICD_K'),('D_EBIT','D_EBIT'),('UTIL','UTIL'),('VOL_A','VOL_A')]:
    d=getattr(M,attr); old=copy.deepcopy(d); d['tot']=d['co_so']; x=mid(); setattr(M,attr,old)
    if isinstance(d,dict): d.update(old)
    print(f'tot.{lab} = muc co_so: tam {x:,.0f} ({x-b:+,.0f})')
olds={a:copy.deepcopy(getattr(M,a)) for a in ['LAND','BOT_YRS','END_A','ASSOC_K','ICD_K','D_EBIT','UTIL','VOL_A']}
for a in olds: getattr(M,a)['tot']=getattr(M,a)['co_so']
x=mid(); print(f'TAT CA hang muc rieng MVC o tot = co_so (chi gia/san luong NNC-kb tot): tam {x:,.0f} ({x-b:+,.0f}); tot flat {M.value("tot","flat"):,.0f} real {M.value("tot","real"):,.0f}')
for a,v in olds.items(): setattr(M,a,v)
for wt in [(.15,.60,.20,.05),(.20,.55,.20,.05),(.25,.50,.20,.05)]:
    M.W=dict(zip(SCN,wt)); W=M.W
    print('W',wt,f'tam {mid():,.0f}')
