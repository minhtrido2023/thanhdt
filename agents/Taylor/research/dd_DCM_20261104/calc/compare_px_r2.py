"""CHẠY SAU khoá r2 (calc/LOCK_r2_md5.txt). Giá đóng cửa 04/11/2026 = 33.000 (BQ, calc/px_liq_out.csv; chưa đối chiếu DNSE). LƯU Ý: giá đã được thấy từ r1."""
import sys, json; sys.path.insert(0,'calc'); import model_r2 as M
PX=33000; b=M.ev_r2(); J=json.load(open('calc/model_r2_out.json'))
print(f"Giá {PX:,} vs kỳ vọng r2 {b['EV']:,.0f}: {PX/b['EV']-1:+.1%}; vs CYC {PX/b['CYC']-1:+.1%}; STRUCT {PX/b['STRUCT']-1:+.1%}")
g,gw=J['grid'],J['grid_wide']
lab=lambda p,G:('RẺ' if p<=G['P10'] else 'RẺ CÓ ĐK' if p<=G['P25'] else 'HỢP LÝ' if p<=G['P75'] else 'NGHIÊNG ĐẮT' if p<=G['P90'] else 'ĐẮT')
print(f"Nhãn theo lưới 270 (P75 {g['P75']:,.0f} · P90 {g['P90']:,.0f}): {lab(PX,g)} | theo lưới mở rộng 360 (P75 {gw['P75']:,.0f} · P90 {gw['P90']:,.0f}): {lab(PX,gw)}")
def solve(f):
    lo,hi=50,500
    for _ in range(60):
        mid=(lo+hi)/2; v=f(mid); lo,hi=(mid,hi) if v<PX else (lo,mid)
    return mid
print(f"Biên dài hạn hàm ý của giá 33.000: nhánh 0,8×biên+0,2×STRUCT125 -> {solve(lambda s:M.ev_r2(s_tc=s)['EV']):.0f} USD/t; 100% CYC -> {solve(lambda s:M.ev_r2(s_tc=s)['CYC']):.0f} USD/t (TB 2016-25 {M.spread_tc:.0f}; dải bền Bobby 180-260; 2025 {M.m.proxy[2025]:.0f})")
for s in (150,179,220,242,260): e=M.ev_r2(s_tc=s)['EV']; print(f"  biên {s}: EV {e:,.0f} => giá 33.000 {PX/e-1:+.1%}")
