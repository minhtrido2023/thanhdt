"""CHAY SAU KHOA (LOCK_md5_r3.txt). Doc gia dong cua MVC 02/11/2026 (tav2_bq.ticker, file px_0211.csv) -> vi tri so vung + xac suat ham y."""
import sys, csv, numpy as np; sys.dont_write_bytecode=True
import model_r3 as R
px=float(list(csv.DictReader(open('px_0211.csv')))[0]['Close'])
ev=R.EV(); z=R.json.load(open('model_r3_out.json'))['grid_pct']
print(f'Gia dong cua MVC 02/11/2026 = {px:,.0f} | tam {ev:,.0f} | gia/tam = {px/ev:.2f} (chiet khau {1-px/ev:.0%})')
lab='RE RO' if px<=z['10'] else ('nghieng re' if px<z['25'] else ('HOP LY' if px<=z['75'] else ('nghieng dat' if px<z['90'] else 'DAT')))
print(f'Vi tri: {lab} (RE RO <= {z["10"]:,.0f})')
v,w=R.scen_dist(); print(f'Xac suat (theo trong so kich ban) gia tri < gia: {w[v<px].sum()/w.sum():.0%}')
def solve(f,lo,hi):
    for _ in range(60):
        m=(lo+hi)/2
        if f(m)>px: lo=m
        else: hi=m
    return m
# (a) trong so duong STRESS can de KV = gia (g2031:real giu ti le 50:40)
a=solve(lambda s: R.EV({'PW':{'flat':s,'g2031':(1-s)*5/9,'real':(1-s)*4/9}}),0,1)
print('(a) KHONG DAT: ngay ca 100 pct phang = '+format(R.EV({'PW':{'flat':1,'g2031':0,'real':0}}),',.0f')+' > gia') if a>0.999 else print(f'(a) trong so duong gia PHANG can de tam = gia: {a:.0%} (dang dung 10%)')
# (b) chuyen trong so tu 'tot' sang 'xau' (co_so 50, rat_xau 5 giu)
def wb(t): return {'tot':t,'co_so':.5,'xau':.45-t,'rat_xau':.05}
b=solve(lambda x: R.EV({'W':wb(.45-x)}),0,.45)
print(f'(b) giu co_so 50/rat_xau 5: tot = {.45-b:.0%}, xau = {b:.0%} thi tam = gia  (dang 25/20)')
# (c) chi kich ban co_so + xau (khong co tot)
print(f'(c) xem (e)')
# (d) r ham y
d=solve(lambda r: R.EV({'r':r}),0.08,0.30); print(f'(d) suat chiet khau ham y (giu moi thu khac): {d:.1%}')
print('\n--- kiem bien (bisection cham bien => khong dat trong bien) ---')
print(f'PW flat 100%: {R.EV({"PW":{"flat":1,"g2031":0,"real":0}}):,.0f}')
print(f'W tot 0/co_so 50/xau 45/rat_xau 5: {R.EV({"W":wb(0)}):,.0f}')
print(f'W tot 0/co_so 0/xau 95/rat_xau 5: {R.EV({"W":{"tot":0,"co_so":0,"xau":.95,"rat_xau":.05}}):,.0f}')
print(f'r 20%: {R.EV({"r":0.20}):,.0f}')
# (e) ket hop: bo tot, can bao nhieu xau (co_so con lai) o duong gia r3
e=solve(lambda x: R.EV({'W':{'tot':0,'co_so':.95-x,'xau':x,'rat_xau':.05}}),0,.95)
print(f'(e) khong co kich ban tot: xau can {e:.0%} (co_so {.95-e:.0%}, rat_xau 5%) de tam = gia')
f=solve(lambda x: R.EV({'W':{'tot':0,'co_so':.95-x,'xau':x,'rat_xau':.05},'PW':{'flat':.25,'g2031':.5,'real':.25}}),0,.95)
print(f'(f) khong co tot + PW 25/50/25: xau can {f:.0%}')
