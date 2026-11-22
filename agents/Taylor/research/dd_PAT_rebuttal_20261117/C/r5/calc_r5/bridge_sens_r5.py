"""Bắc cầu r4→r5 + độ nhạy + chiết khấu thanh khoản (chạy SAU lock_r5)."""
import math, json
import model_r5 as M
out = {}
def C(**kw): return M.run(**kw)['center']
def MX(**kw): return M.run_mix(**kw)['center']
# --- kiểm hồi quy: khung r5 với tham số r4 (q=0, inv=44,44, cell D) = r4 66.318,4
r4 = C(inv=M.INV_EXCESS, cell='D'); print(f"kiem r4 {r4:,.2f} (r4 = 66.318,42)")
s1 = C(inv=0.0, cell='D');          # (2) bo ton kho
s2 = C(inv=0.0, cell='O2')          # (3) cach doc H1 sach (q=0)
s3 = MX()                           # (1) tron q_B
br = [('r4', r4, None), ('(2) bỏ giải phóng tồn kho (về r2)', s1, s1 - r4), ('(3) ô (A tắt,B bật) → O2 (H1/26 đọc sạch)', s2, s2 - s1), ('(1) trộn q_B {0;.25;.40}', s3, s3 - s2)]
for k, v, d in br: print(f"{k:55s} {v:>10,.0f} {'' if d is None else f'{d:+,.0f}'}")
print(f"tổng r4→r5 {s3 - r4:+,.0f}")
out['bridge'] = br
oat = {'gỡ trộn q_B (q=0)': MX(qs=(0.0,)), 'gỡ cell O2 (về D)': MX(cell='D'), 'thêm lại tồn kho r4': MX(inv=M.INV_EXCESS)}
for k, v in oat.items(): print(f"OAT {k:28s} {v:,.0f} (đóng góp của thay đổi {s3 - v:+,.0f})")
out['oat'] = oat; out['center'] = s3
S = {}
for q in M.QS: S[f'q_B={q} riêng (cell O2)'] = C(q_perm=q, lam=M.lam_q(q))
for q in M.QS: S[f'q_B={q} riêng (cell D = r4)'] = C(q_perm=q, lam=M.lam_q(q), cell='D')
S['mix, ô (A tắt,B bật) 50/50 (cell D)'] = MX(cell='D')
S['mix, ô → opt75'] = MX(cell='opt75')
S['mix, tồn kho r4 nguyên 44,44'] = MX(inv=M.INV_EXCESS)
S['mix, tồn kho haircut 39,4×50%'] = MX(inv=39.4 * 0.5)
S['mix, cắt 2028 kiểu r2 (q=0)'] = C(cut_month=13.5)
S['mix, cước 3,85%'] = MX(freight=M.FREIGHT_R3); S['mix, cước 4,03%'] = MX(freight=0.040304)
S['mix, P r3 (giữa 1,0)'] = MX(PPd=M.PP_R3)
S['mix, P(A)=0,30'] = MX(pA=0.30); S['mix, P(A)=0,35'] = MX(pA=0.35); S['mix, P(A)=0,70'] = MX(pA=0.70)
S['mix, D(A)=0,7'] = MX(pD=0.7); S['mix, A muộn τ_A 25,5'] = MX(tau_a=25.5)
T80 = {'Ta': (1.0, 0.35, 0.80), 'Tb': (0.35, 0.35, 0.15), 'Tc': (0.135, 0.135, 0.05)}
T55 = {'Ta': (1.0, 0.35, 0.55), 'Tb': (0.35, 0.35, 0.35), 'Tc': (0.135, 0.135, 0.10)}
S['mix, T 0,80/0,15/0,05'] = MX(PTd=T80); S['mix, T 0,55/0,35/0,10'] = MX(PTd=T55)
S['mix, điện 0,98'] = MX(cut=0.98); S['mix, φ 0,91'] = MX(phi=0.91); S['mix, φ 0,6'] = MX(phi=0.6)
S['mix, cốc 2100'] = MX(coke_lr=2100.0); S['mix, cốc 2108'] = MX(coke_lr=2108.0)
S['mix, sản lượng một chiều 0,927/1,0'] = MX(vol=(0.927, 1.0)); S['mix, sản lượng hai chiều 0,927/1,037'] = MX(vol=(0.927, 1.037))
S['mix, H2/27 −15%'] = MX(vol27=0.85); S['mix, H2/27 −30%'] = MX(vol27=0.70)
S['mix, TX 0,90'] = MX(PX15=0.90)
for m in (.8, .9, 1.1, 1.2): S[f'mix, EBIT dài hạn ×{m}'] = MX(lr_mult=m)
for p in (.90, .95, 1.05, 1.10): S[f'mix, giá ×{p}'] = MX(PPd={k * p: v for k, v in M.PP_R4.items()})
S['mix, DLC dưới netback −5%'] = MX(transfer=0.05)
S['mix, một lần −50'] = MX(oneoff=-50); S['mix, mất cầm cố −42,6'] = MX(oneoff=-42.6); S['mix, 70 tỷ theo mệnh giá'] = MX(oneoff=M.LOCKED70)
grid = {r: {g: round(MX(r=r, g=g)) for g in (0, .01, .02, .03)} for r in (.125, .13, .135, .14, .145)}
S['grid'] = grid
# --- xếp chồng bi quan CÙNG cơ sở skeptic (q_B 0,25 + P(A) 0,35 + sản lượng một chiều, không T)
l25 = M.lam_q(0.25)
stack_r4 = C(q_perm=0.25, lam=l25, pA=0.35, vol=(0.927, 1.0), inv=M.INV_EXCESS, cell='D')
stack_r5 = C(q_perm=0.25, lam=l25, pA=0.35, vol=(0.927, 1.0))
stack_r5T = C(q_perm=0.25, lam=l25, pA=0.35, vol=(0.927, 1.0), PTd=T80)
stack_r4T = C(q_perm=0.25, lam=l25, pA=0.35, vol=(0.927, 1.0), PTd=T80, inv=M.INV_EXCESS, cell='D')
S['STACK bi quan (q_B .25 + P(A) .35 + vol một chiều) MÔ HÌNH r4 (kiểm 60.354)'] = stack_r4
S['STACK bi quan cùng cơ sở, MÔ HÌNH r5 (cell O2, không tồn kho)'] = stack_r5
S['STACK + T .80/.15/.05, mô hình r4 (r4 cũ 57.200)'] = stack_r4T
S['STACK + T .80/.15/.05, mô hình r5'] = stack_r5T
for k, v in S.items():
    if k != 'grid': print(f"{k:70s} {v:>9,.0f} ({v - s3:+,.0f} vs tâm)")
print('grid', grid)
out['sens'] = S
# --- thanh khoan
liq = 0.10
out['liquidity'] = dict(center_before=s3, center_after=s3 * (1 - liq), gate_085_after=0.85 * s3 * (1 - liq), gate_085_before_ref=0.85 * s3)
print(out['liquidity'])
json.dump(out, open('bridge_sens_r5_out.json', 'w'), indent=1, default=float, ensure_ascii=False)
