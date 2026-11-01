# HHS valuation — mọi số đầu vào từ notes_read.md (BCTC) hoặc gắn (ước lượng)
import json, datetime as dt, statistics as st
o=json.load(open('dnse_ohlc_HHS.json'))
c,v,t=o['c'],o['v'],o['t']
d=[dt.datetime.utcfromtimestamp(x+7*3600).date() for x in t]
px=9450; sh=431.985968  # tr cp
print('last bar',d[-1],c[-1]*1000,'bars',len(c))
def adv(n): return st.mean([c[i]*1000*v[i] for i in range(-n,0)])/1e9
print('ADV20 %.1f ty, ADV60 %.1f ty'%(adv(20),adv(60)))
y=[i for i in range(len(d)) if d[i]>=d[-1]-dt.timedelta(days=365)]
print('52w hi %.0f lo %.0f'%(max(c[i] for i in y)*1000,min(c[i] for i in y)*1000))
for lab,dd in [('2026-07-29 (Q2)',dt.date(2026,7,29)),('2026-08-28 (6T)',dt.date(2026,8,28)),('2026-10-29 (Q3)',dt.date(2026,10,29))]:
    i=max(k for k in range(len(d)) if d[k]<=dd); j=min(len(c)-1,i+1)
    print(lab,'close',c[i]*1000,'next',c[j]*1000, 'ret5d %.1f%%'%((c[min(len(c)-1,i+5)]/c[i]-1)*100) if i+5<len(c) else '')
mcap=px*sh/1e3
print('mcap %.1f ty'%mcap)
# --- BCTC
eq_parent=9152.94; nci=7726.98; tot_eq=16879.91
bv=eq_parent/sh*1e3; print('BVPS mẹ %.0f, P/B %.3f; BQ-PB basis tot_eq/sh=%.0f -> %.2f'%(bv,px/bv,tot_eq/sh*1e3,px/(tot_eq/sh*1e3)))
dtl_fv=2020.76; stepup_pre=dtl_fv/0.20; stepup_at=stepup_pre*0.8; hhs_int=0.5115
hhs_step=stepup_at*hhs_int
print('step-up còn lại trước thuế %.0f, sau thuế %.0f, phần HHS %.0f (ước lượng, thuế 20%%)'%(stepup_pre,stepup_at,hhs_step))
hist_bv=eq_parent-hhs_step; print('BV tương đương giá gốc %.0f = %.0f đ/cp, P/B %.2f'%(hist_bv,hist_bv/sh*1e3,px/(hist_bv/sh*1e3)))
print('9T PPA qua giá vốn ~ %.0f (=(2164.36-2020.76)/0.2)'%((2164.36-2020.76)/0.2))
# BĐS gross ex-PPA
print('Biên gộp BĐS 9T ex-PPA ~ %.1f%%'%((296.42+(2164.36-2020.76)/0.2)/1875.89*100))
# CRV look-through FV-basis via NCI (gần đúng; NCI gồm Pruksa VN 9,83% nhỏ)
crv_fv=nci/(1-hhs_int); print('CRV GTHL-basis ngầm định từ NCI ~ %.0f (ước lượng)'%crv_fv)
auto_book=694.84-310.74; parent_fin_cash=12.89+158.49
# --- scenarios
sc={'Tiêu cực':dict(p=0.30,h=0.60,auto_np=25,pe=6,hd=0.35,g=0.15),
    'Cơ sở':  dict(p=0.50,h=0.40,auto_np=40,pe=8,hd=0.25,g=0.10),
    'Tích cực':dict(p=0.20,h=0.25,auto_np=55,pe=10,hd=0.15,g=0.05)}
res={}
for k,s in sc.items():
    crv_part=hhs_int*crv_fv - s['h']*hhs_step          # phần HHS trong CRV sau haircut step-up
    crv_part*=(1-s['hd'])                               # CK holding (tiền kẹt ở CRV, 48,85% thiểu số)
    other=eq_parent-hhs_int*crv_fv-auto_book            # phần còn lại ngoài CRV & ô tô (tiền mẹ, Pruksa, HG...)
    auto=s['auto_np']*s['pe']
    nav=(crv_part+other+auto)*(1-s['g'])
    res[k]=nav/sh*1e3
    print(f"{k}: CRV {crv_part:.0f} + khác {other:.0f} + ô tô {auto:.0f} -> x(1-{s['g']}) = {nav:.0f} ty = {res[k]:.0f} đ/cp")
w=sum(sc[k]['p']*res[k] for k in sc); print('Trọng số %.0f đ/cp; giá/trọng số %.2f'%(w,px/w))
# market-implied
print('Giá hàm ý CK so NAV GTHL-basis: %.0f%%'%((1-mcap/eq_parent)*100))
# Cross-check: P/B lịch sử-tương đương x peers
for pb in (0.6,0.72,0.9): print('P/B %.2f x BV giá gốc -> %.0f'%(pb,pb*hist_bv/sh*1e3))
# TCH CRV own-book cross
crv_own=7579; print('51,15%% x VCSH CRV sổ riêng 31/03/26 7.579 = %.0f ty = %.0f đ/cp HHS'%(hhs_int*crv_own,hhs_int*crv_own/sh*1e3))
