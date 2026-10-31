# Độ nhạy RI vòng-1 theo (a) β đo được (Ke thấp hơn) và (b) ETR về 20% từ năm X. Tái dùng hpg_valuation.py (ước lượng).
import importlib.util, io, contextlib
spec=importlib.util.spec_from_file_location('v','hpg_valuation.py'); v=importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(v)
SC,ri=v.SC,v.ri_value
def wavg(ke,g=0.05,tax_from=None,etr0=0.12):
    tot=0
    for s in SC.values():
        e=list(s['e']); roe=s['roe_T']
        if tax_from is not None:
            f=0.80/(1-etr0)
            yrs=[2026.75,2027,2028,2029]
            e=[x*f if y>=tax_from else x for x,y in zip(e,yrs)]
            roe=roe*f   # terminal sau 2029 luôn chịu 20%
        tot+=s['w']*ri(e,roe,ke,g)[0]
    return tot
print('(a) Ke theo beta (rf 6,75%; ERP 5,0/5,55/6,1%), g 5%:')
for b in (0.84,0.90,0.93,1.10):
    row=[]
    for erp in (0.05,0.0555,0.061):
        ke=0.0675+b*erp; row.append(f'Ke {ke*100:.2f}% -> {wavg(ke):,.0f}')
    print(f' beta {b}: '+' | '.join(row))
print('\n(b) ETR -> 20% (ETR gốc 12%; tỉ lệ LN x0,909), Ke 12,3/13,0/13,4%, g 5%:')
print(' baseline (chỉ terminal 2030+ chịu 20%): ', [f'{wavg(k,tax_from=2030):,.0f}' for k in (0.123,0.13,0.134)])
for y in (2027,2028,2029):
    print(f' từ {y}: ', [f'{wavg(k,tax_from=y):,.0f}' for k in (0.123,0.13,0.134)])
print(' không đổi thuế (vòng 1): ', [f'{wavg(k):,.0f}' for k in (0.123,0.13,0.134)])
print('\nLNST lõi TTM 22.943 tỷ, ETR 12% -> 20%: ΔLNST = ', round(22943*(1-0.8/0.88)), 'tỷ/năm; ETR 9,3% (Q3) -> 20%:', round(22943*(1-0.8/0.907)))
