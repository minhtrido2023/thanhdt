# Dinh gia HPG — residual income 3 kich ban + do nhay g x Ke + EV/EBITDA cross-check. Gia dinh = (uoc luong) tru khi ghi nguon.
sh=8442.96452; BV0=148795.5   # VCSH me 30/09/2026 [HN-Q3]
px=21000
# LNST me (ty) Q4/26, 2027, 2028, 2029 ; ROE dai han (terminal) ; payout tien mat
SC={
 'xau':  dict(w=0.25, e=[6000,15000,13000,14000], roe_T=0.10, note='spread HRC 150-200 USD/t, AD bi go/giam, TQ noi XK; ~ muc 2023-24'),
 'co_so':dict(w=0.50, e=[7500,26000,23000,22000], roe_T=0.125,note='spread ~200-240, AD giu, KL DQ2 day, gia ban giam nhe'),
 'tot':  dict(w=0.25, e=[8500,32000,30000,28000], roe_T=0.15, note='spread >=250, KL ~15tr t, them AD voi ASEAN'),
}
payout=0.20   # co tuc tien ~ 20% LN (uoc luong; 2025: 5% tien + 10% CP)
def ri_value(e,roe_T,ke,g):
    bv=BV0; pv=0.0; t=0.0
    for i,ni in enumerate(e):
        dt=0.25 if i==0 else 1.0
        t+=dt
        ri=ni-ke*dt*bv
        pv+=ri/((1+ke)**t)
        bv=bv+ni*(1-payout)
    # terminal: RI_{T+1} = (roe_T-ke)*bv, growing g
    tv=(roe_T-ke)*bv/(ke-g)
    pv_tv=tv/((1+ke)**t)
    val=BV0+pv+pv_tv
    return val/sh*1000, pv_tv/(val)*100, bv
for ke in (0.123,0.13,0.134):
    tot=0
    for k,s in SC.items():
        v,tw,bvT=ri_value(s['e'],s['roe_T'],ke,0.05)
        tot+=s['w']*v
        print(f'Ke {ke:.3f} {k:6s} {v:8.0f} d/cp  terminal {tw:5.1f}% gia tri (BV0 da tinh rieng)  BV2029 {bvT:,.0f}')
    print(f'  -> trong so: {tot:,.0f} d/cp  ({(tot/px-1)*100:+.1f}% vs {px})')
print('\nDo nhay kich ban co so: g x Ke (d/cp)')
print('g\\Ke ', ' '.join(f'{k:>7.3f}' for k in (0.115,0.123,0.13,0.134,0.14)))
for g in (0.03,0.04,0.05,0.06):
    print(f'{g:.2f} ', ' '.join(f'{ri_value(SC["co_so"]["e"],SC["co_so"]["roe_T"],k,g)[0]:7.0f}' for k in (0.115,0.123,0.13,0.134,0.14)))
print('\nDo nhay ROE dai han (Ke 13%, g 5%) kich ban co so:')
for r in (0.09,0.10,0.11,0.12,0.125,0.13,0.14,0.15,0.16):
    print(r, round(ri_value(SC['co_so']['e'],r,0.13,0.05)[0]))
# Justified P/B = (ROE-g)/(Ke-g)
print('\nP/B hop ly (ROE-g)/(Ke-g), g 5%:')
for r in (0.10,0.125,0.15):
    print(r,[round((r-0.05)/(k-0.05),2) for k in (0.123,0.13,0.134)])
# EV/EBITDA cross-check
nd=59607.6; inv_lk=12664.1; mi=772.9
for name,ebitda in (('xau',28000),('co_so',40000),('tot',48000)):
    for m in (5,6,7):
        eq=m*ebitda-nd-mi+inv_lk
        print(f'EV/EBITDA {name} EBITDA {ebitda} x{m}: {eq/sh*1000:,.0f} d/cp')
