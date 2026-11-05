"""CHẠY SAU khoá r5 (calc/LOCK_r5_md5.txt). Giá đóng cửa 04/11/2026 = 33.000. Giá ĐÃ THẤY từ r1; model_r5 không nhận giá."""
import sys, json; sys.path.insert(0, 'calc'); import model_r5 as M, model_r4 as M4
from model_r5 import r2, R0, rdep, DEP0
PX = 33000; J = json.load(open('calc/model_r5_out.json')); b = M.ev_r5()
print(f"Giá {PX:,} vs TÂM {b['EV']:,.0f}: {PX/b['EV']-1:+.1%} · vs A {b['A']:,.0f}: {PX/b['A']-1:+.1%} · vs B {b['B']:,.0f}: {PX/b['B']-1:+.1%} · vs CYC {PX/b['CYC']-1:+.1%}")
lab = lambda p, G: ('RẺ' if p <= G['P10'] else 'RẺ CÓ ĐK' if p <= G['P25'] else 'HỢP LÝ' if p <= G['P75'] else 'NGHIÊNG ĐẮT' if p <= G['P90'] else 'ĐẮT')
for k, G in J['grids'].items(): print(f"  lưới {k} (n={G['n']}; P75 {G['P75']:,} · P90 {G['P90']:,}): {lab(PX, G)}")
def solve(f):
    lo, hi = 50, 900
    for _ in range(80):
        mid = (lo+hi)/2; lo, hi = (mid, hi) if f(mid) < PX else (lo, mid)
    return mid
print('Biên dài hạn (USD/t) mà tại đó giá trị kỳ vọng = 33.000 (Brent 67,8 trừ khi ghi):')
for B in (M.BRENT_TC, 82, 90, 103):
    print(f"  Brent {B:.1f}: TÂM {solve(lambda s: M.ev_r5(B=B, s_tc=s)['EV']):.0f} · A {solve(lambda s: M.ev_r5(B=B, s_tc=s)['A']):.0f} · B {solve(lambda s: M.ev_r5(B=B, s_tc=s)['B']):.0f} · 100%CYC(tâm) {solve(lambda s: M.ev_r5(B=B, s_tc=s)['CYC']):.0f}")
ndA = M.nd_share_bao_tieu(); sm3 = M.PROD_KT*1e3*M.I_C/M.SM3_TO_MMBTU/1e6
def thr(pl, v, B=M.BRENT_TC, r=R0): return solve(lambda s: r2.ev_r2(r=r, s_tc=s)['EV'] + M.pv_gas(B, v, r=r, plateau=pl))
print('Ngưỡng đảo (biên mà EV kịch bản = 33.000) theo kịch bản (sau sửa S2/S3):')
for tag, pl in (('ND 30%', .30), ('ND 44,8% (A)', ndA), ('ND 49,1%', .81*365/sm3), ('ND 54% (B)', M.ND_CAP)):
    print(f"  {tag}: V1 {thr(pl,'V1'):.0f} · V2 {thr(pl,'V2'):.0f} · V1 r−100bp {thr(pl,'V1',r=rdep(DEP0-1)):.0f}")
# kiểm câu r4: "ND30%+V1 đảo ở ≈224" trên chính model_r4 (2028 theo V1 cũ, ND30 phẳng)
def thr4(sh, v, r=R0):
    bak = dict(M4.ND_SHARE); M4.ND_SHARE.update({y: (0.25*sh if y == 2028 else (0.5*sh if y == 2034 else sh)) for y in bak})
    out = solve(lambda s: M4.r2.ev_r2(r=r, s_tc=s)['EV'] + M4.pv_gas(M4.BRENT_TC, v, r=r))
    M4.ND_SHARE.clear(); M4.ND_SHARE.update(bak); return out
print(f"Kiểm r4: ND30%+V1 đảo ở biên {thr4(.30,'V1'):.0f} (r−100bp {thr4(.30,'V1',rdep(DEP0-1)):.0f}); V1 với ND54%: {thr4(M4.ND_PLATEAU,'V1'):.0f}")
print('Bảng biên -> (tâm | A | B) đ/cp và giá cao hơn tâm (%), Brent 67,8:')
for s in (98, 138, 179, 220, 260):
    e = M.ev_r5(s_tc=s); print(f"  {s}: tâm {e['EV']:,.0f} ({PX/e['EV']-1:+.1%}) | A {e['A']:,.0f} ({PX/e['A']-1:+.1%}) | B {e['B']:,.0f} ({PX/e['B']-1:+.1%})")
