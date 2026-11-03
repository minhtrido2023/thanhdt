import sys, itertools, numpy as np
sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/dd_MVC_20261103/r3/calc'); sys.dont_write_bytecode=True
import model_r3 as R
B=R.BASE
Ws=[{'tot':.15,'co_so':.60,'xau':.20,'rat_xau':.05},R.W0,{'tot':.35,'co_so':.50,'xau':.10,'rat_xau':.05}]
PWs=[{'flat':.25,'g2031':.5,'real':.25},R.PW0,{'flat':.05,'g2031':.35,'real':.60}]
out=[]
for r,h,cx,ca,rel,W,PW in itertools.product((0.11,0.13,0.15),(0.0,0.15,0.30),(0.7,1.0,1.3),(0.85,1.0,1.15),(0.80,0.87,0.95),Ws,PWs):
    cost_a=(rel*380-R.GP26)*ca
    out.append(R.EV({'r':r,'hold':h,'CAPEX_LEFT':B['CAPEX_LEFT']*cx,'REL':rel,'COST_A':cost_a,'COST_B':cost_a+5,'W':W,'PW':PW}))
e=np.array(out)
print('n',len(e),' '.join(f'P{q} {np.percentile(e,q):,.0f}' for q in (5,10,25,50,75,90)))
for px in (13300,13700,15261):
    print(f'share EV<{px}: {np.mean(e<px):.1%}')
# W only grid (W x PW) at base params
for W in Ws:
  for PW in PWs:
    print(W['tot'],PW['flat'],f"{R.EV({'W':W,'PW':PW}):,.0f}")
# industrial cluster -1300 applied
print('GRID_ALL', ' '.join(f'P{q} {np.percentile(e,q):,.0f}' for q in (10,25,50,75,90)))
print('with cluster 70% recovery: P10', f'{np.percentile(e-1300,10):,.0f}', 'share<13700', f'{np.mean(e-1300<13700):.1%}')
# tot x real and co_so x g2031 cells removed (no-precedent cells) -> reweight
ev,bp,res=R.EV(by_path=True)
cells={(k,p):res[(k,p)]['ps'] for k in R.SCN for p in R.PATHS}
w={(k,p):R.W0[k]*R.PW0[p] for k in R.SCN for p in R.PATHS}
print('tot|real share of EV', f"{w[('tot','real')]*cells[('tot','real')]/ev:.1%}", 'tot total share', f"{sum(w[('tot',p)]*cells[('tot',p)] for p in R.PATHS)/ev:.1%}")

# P(tot) implied & EV share
for c in (1300,2100):
    print('cluster',c,'P10',f'{np.percentile(e-c,10):,.0f}','P25',f'{np.percentile(e-c,25):,.0f}','share<13700',f'{np.mean(e-c<13700):.1%}')
