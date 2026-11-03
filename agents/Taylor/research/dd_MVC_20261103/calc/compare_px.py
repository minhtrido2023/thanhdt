"""So voi gia — CHAY SAU khi khoa md5 (LOCK_md5.txt). Gia dong cua 02/11/2026 = 13.700 (tav2_bq.ticker, px_stats_out.txt)."""
import valuation as M
PX=13700
for mode in ('flat','real'):
    v={k:M.value(k,mode=mode) for k in M.SCN}
    pos,base,neg=v['tot'],v['co_so'],(0.20*v['xau']+0.05*v['rat_xau'])/0.25
    up=(pos+2*base)/3          # giu ti le tich cuc:co so = 1:2 nhu trong so 25/50
    for px in (12500,13700,15000):
        p=(up-px)/(up-neg); print(f'{mode}: gia {px:,} -> P(tieu cuc) ham y {p:.0%} (mo hinh 25%)')
lo=sum(M.W[k]*M.value(k,'flat') for k in M.SCN); hi=sum(M.W[k]*M.value(k,'real') for k in M.SCN); mid=(lo+hi)/2
print(f'tam {mid:,.0f}: gia/tam = {PX/mid-1:+.0%}; vs phang {PX/lo-1:+.0%}; vs thuc {PX/hi-1:+.0%}')
print(f'P/E TTM {PX/3068:.1f}x ; P/B {PX/15460:.2f}x ; von hoa {PX*100e6/1e9:,.0f} ty')
# gia tri co phan NNC tinh theo gia thi truong NNC 47.100 (30/10) — chi doi chieu
print(f'Doi chieu: 9,66 tr cp NNC x 47.100 = {9.659170*47100/1e3:,.0f} ty = {9.659170*47100/1e3/(PX*100e6/1e9):.0%} von hoa MVC')
