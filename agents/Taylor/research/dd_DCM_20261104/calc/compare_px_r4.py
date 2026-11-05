"""CHẠY SAU khoá r4 (calc/LOCK_r4_md5.txt). Giá đóng cửa 04/11/2026 = 33.000 (DNSE ATC 14:45:02 theo investor report r3). Giá đã thấy từ r1."""
import sys, json; sys.path.insert(0, 'calc'); import model_r4 as M
PX = 33000; b = M.ev_r4(); J = json.load(open('calc/model_r4_out.json'))
print(f"Giá {PX:,} vs kỳ vọng r4 {b['EV']:,.0f}: {PX/b['EV']-1:+.1%}; vs CYC {PX/b['CYC']-1:+.1%}; STRUCT {PX/b['STRUCT']-1:+.1%}")
lab = lambda p, G: ('RẺ' if p <= G['P10'] else 'RẺ CÓ ĐK' if p <= G['P25'] else 'HỢP LÝ' if p <= G['P75'] else 'NGHIÊNG ĐẮT' if p <= G['P90'] else 'ĐẮT')
for k, G in J['grids'].items(): print(f"  lưới {k} (n={G['n']}; P75 {G['P75']:,} · P90 {G['P90']:,}): {lab(PX, G)}")
def solve(f):
    lo, hi = 50, 700
    for _ in range(60):
        mid = (lo+hi)/2; lo, hi = (mid, hi) if f(mid) < PX else (lo, mid)
    return mid
for B in (M.BRENT_TC, 82, 90, 103):
    print(f"  Brent {B:.1f}: biên dài hạn hàm ý (kỳ vọng) {solve(lambda s: M.ev_r4(B=B, s_tc=s)['EV']):.0f} · (100% CYC) {solve(lambda s: M.ev_r4(B=B, s_tc=s)['CYC']):.0f} USD/t")
for s, row in J['margin_brent'].items(): print(f"  biên {s}: " + ' | '.join(f"Brent {B}: {PX/v-1:+.1%}" for B, v in row.items()))
