"""DDV reweight 28/10/2026 - calibrate GM(S) tu BCTC quy, chay 3 kich ban. Moi so la ket qua in ra (out.txt)."""
import numpy as np
SH=146.1099   # trieu cp [BQ OShares]
# BCTC (ty VND): Q3/26, Q3/25, 9T/26, 9T/25
rev={'Q3_26':1290.292,'Q3_25':1396.632,'9T_26':4916.459,'9T_25':4153.842}
gp ={'Q3_26':47.653 ,'Q3_25':305.526 ,'9T_26':447.275 ,'9T_25':731.560}
gm={k:gp[k]/rev[k]*100 for k in rev}
gm['H1_26']=(gp['9T_26']-gp['Q3_26'])/(rev['9T_26']-rev['Q3_26'])*100
print('GM quy %:',{k:round(v,2) for k,v in gm.items()})
cogs_q3=1242.639; cogs_9t=4469.184
inv_tot=836.635; raw=617.3
print('ngay ton kho tong/COGS Q3 (92d): %.1f ; /COGS 9T (273d): %.1f ; NVL/COGS Q3: %.1f'%(inv_tot/(cogs_q3/92),inv_tot/(cogs_9t/273),raw/(cogs_q3/92)))
# hieu chuan: S_eff = gia S ME FOB tinh theo do tre ~53 ngay (Q3/25 ~175; Q3/26 ~920 = TB hop dong T7-T8 Bobby: dinh 947 T7, T9 880)
S25,S26=175,920
slope=(gm['Q3_25']-gm['Q3_26'])/((S26-S25)/100)
print('slope pp GM / 100USD S (confounded DAP/NH3): %.2f'%slope)
DAP_REF=800; dap_pp=0.067   # pp GM / USD DAP (~DAP chiem ~55% DT; 30USD=3.75% gia*0.55=2.1pp) [uoc luong]
def gm_q(S,dap,sl=slope): return gm['Q3_26']+sl*(S26-S)/100+dap_pp*(dap-DAP_REF)
REV_Q=5500/4; OPEX_Q=(21.51+30.52); TAX=0.2; INT_AT=59.8
paths={
 'Bear':dict(S=[850,800,740,700],dap=[740,700,680,670]),
 'Base':dict(S=[750,680,600,550],dap=[770,745,725,710]),
 'Bull':dict(S=[700,500,350,300],dap=[775,765,755,750]),
}
res={}
res_=res
for sl in (slope,2.0,3.0):
  for n,p in paths.items():
    g=[gm_q(s,d,sl) for s,d in zip(p['S'],p['dap'])]
    gpq=[x/100*REV_Q for x in g]
    ebit=sum(gpq)-4*OPEX_Q
    np_op=ebit*(1-TAX) if ebit>0 else ebit   # lo khong tinh thue
    res[(round(sl,2),n)]=(g,sum(gpq),ebit,np_op)
    print('slope %.2f %-4s GM q: %s  GP=%.0f EBIT=%.0f NPop=%.0f'%(sl,n,[round(x,1) for x in g],sum(gpq),ebit,np_op))

# ---- dinh gia ----
NC=7583; NC_WC=5950; BOOKOP=(2208.2-1108.0)/SH*1000   # d/cp
print('book van hanh/cp: %.0f'%BOOKOP)
MULT={'Bear':None,'Base':9.5,'Bull':7.0}
def val(n,npop,nc):
    if n=='Bear':
        burn=-npop/SH*1000
        return nc-burn+0.72*(BOOKOP-burn)
    return nc+npop*MULT[n]/SH*1000
W_old={'Bear':.30,'Base':.45,'Bull':.25}; W_new={'Bear':.45,'Base':.40,'Bull':.15}
for sl in (slope,2.0,3.0):
    out={}
    for n in paths:
        npop=res_[(round(sl,2),n)][3]
        out[n]=(val(n,npop,NC),val(n,npop,NC_WC),npop)
    for lab,W in (('w_old',W_old),('w_new',W_new)):
        e1=sum(W[n]*out[n][0] for n in W); e2=sum(W[n]*out[n][1] for n in W)
        print('slope %.2f %s: '%(sl,lab)+' | '.join('%s NPop=%.0f V(NC7583)=%.0f V(NC5950)=%.0f'%(n,out[n][2],out[n][0],out[n][1]) for n in out)+' => EV %.0f / %.0f'%(e1,e2))
