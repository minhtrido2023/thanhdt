"""Bien the skeptic 52.238: terminal SYM cho CO_SO/TOT, XAU terminal giu conv 0,40 (RONIC 5% < Ke, khong dich dconv). Chay: $DNA_PYEXE -I fpt_5f_r2_xau.py"""
import os
HERE='.'
src=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'fpt_r2.py')).read().split('RES = R2C.finalize')[0]
ns=dict(__file__=os.path.abspath('fpt_r2.py'),__name__='m'); exec(src,ns)
R2C,R,PX,SC,axes=ns['R2C'],ns['R'],ns['PX'],ns['SC'],ns['axes']; d=R2C.liq2('FPT')['d_ref']
def mk(xau_mode):
    def dcf(base,g1,conv,gT,ke,n=5):
        capT=1-gT/ke
        if g1==0.03:  # XAU
            cT={'unshift':0.40,'floor':max(min(conv,capT),0.40),'sym_noshift_dconv':min(0.4,capT)}[xau_mode]
        else: cT=capT
        pv,e=0.0,base
        for t in range(1,n+1):
            e*=1+g1; pv+=e*conv/(1+ke)**t
        return pv+e*(1+gT)*cT/(ke-gT)/(1+ke)**n,0
    return dcf
for m in ('unshift','floor'):
    ns['dcf']=mk(m); s=R2C.stats(R2C.outcomes(axes,lambda **kw:ns['fv2'](R,**kw)),PX,d); print(m,round(s['center']),round(s['p10']),round(s['p50']),round(s['p90']),f"{s['pct_below_px']:.1%}",R2C.label(PX,s))
