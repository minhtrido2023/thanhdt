"""DCF FCFE vòng đời hữu hạn TTA — DD 20/11/2026. Đơn vị: tỷ VND. Mọi giả định gắn (ước lượng) trong REPORT.
Nguồn neo: BCTC tổng hợp Q3/2026 (src/BCTC-quy-3.2026-TV.pdf), BCKT 2025.
"""
import itertools
SH = 178.559087  # triệu cp
NET_DEBT0 = 1554.5 - (34.9 + 128.5 + 3.5)   # vay 292.3+1262.3 − tiền − HTM ngắn − HTM dài (30/9/2026)
DEBT0 = 1554.5
FX = 25755
FIT1, FIT2 = 9.35*FX/100, 7.09*FX/100      # đ/kWh
TRAN = 1184.90                              # trần chuyển tiếp mặt đất QĐ21/2023
BN_GWH, NM_GWH = 98.0, 85.0                 # sản lượng thiết kế (web cty: 98; NM1 80-90)
POST_FIT = 1100.0                           # (ước lượng) giá sau FIT
def model(r=0.135, bn_px=FIT1, nm_px=FIT2, retro=0.0, hydro_shock=0.0, rate_add=0.0,
          hydro_post_cut=0.15, phuoc_hoa=0.0, ar_haircut=0.0, start=2027, hydro_scale=1.0, ar_excess=330.0):
    pv, debt, rows = 0.0, DEBT0, []
    # lịch trả gốc (ước lượng từ kỳ hạn vay BCTC V.15): 280 2027, rồi đều tới hết 2033
    sched = {2027: 280.0}
    rem = DEBT0 - 280.0
    for y in range(2028, 2034): sched[y] = rem/6
    for i, y in enumerate(range(start, 2061)):
        t = i + 0.5
        # --- hydro (NH2 48MW, NH2A 8.4MW, Pá Hu 26MW): DT nền 330 (ước lượng từ 9T 279.8 + Q4)
        hyd = 330.0 * hydro_scale * (1 - (hydro_shock if y == 2027 else 0)) * (1 - (hydro_post_cut if y >= 2037 else 0))
        hyd_cost = 80.0 * 1.03**i
        # --- solar: Bầu Ngứ FIT tới 11/2039, Núi Một 1 tới 12/2040, đời 25 năm (tới 2044/2045)
        deg = 0.995**(y-2026)
        bn = (BN_GWH*deg*(bn_px if y <= 2039 else POST_FIT)/1000) if y <= 2044 else 0
        nm = (NM_GWH*deg*(nm_px if y <= 2040 else POST_FIT)/1000) if y <= 2045 else 0
        sol_cost = (29.0*1.03**i) if y <= 2045 else 0
        ga = 22.0*1.03**i
        ebitda = hyd - hyd_cost + bn + nm - sol_cost - ga
        capex = 30.0 + (60.0 if y == 2032 else 0)            # (ước lượng)
        interest = debt * (0.084 + rate_add)
        dep = 205.0 if y <= 2040 else 110.0                  # (ước lượng)
        pbt = ebitda - dep - interest
        tr = 0.06 if y <= 2030 else (0.10 if y <= 2034 else 0.20)
        tax = max(pbt, 0)*tr
        bcc = 0.12*max(hyd - hyd_cost, 0)                    # chia LN HTKD (2025: 31,0 tỷ)
        funds = 0.06*max(pbt - tax, 0) + 2.0                 # quỹ KTPL + BĐH
        princ = sched.get(y, 0.0); debt -= princ
        ret = retro/5 if start <= y < start+5 else 0         # hoàn tiền FIT hồi tố trả 5 năm (ước lượng)
        fcfe = ebitda - capex - interest - tax - bcc - funds - princ - ret
        pv += fcfe/(1+r)**t
        rows.append((y, round(ebitda,1), round(fcfe,1)))
    other = 99.4 + phuoc_hoa + 15.0 + ar_excess - ar_haircut   # Phương Mai (giá gốc − DP), cho vay bên liên quan 15, ±
    eq = pv + 34.9 + 116.0 + other                  # + tiền + tiền gửi NH (nợ đã trừ qua lịch trả gốc)
    return eq, eq*1000/SH, rows
if __name__ == "__main__":
    base_ok = model()
    print("STATUS QUO (giữ FIT cả 2):", round(base_ok[1]))
    for nm_, kw in [("A_tốt: giữ FIT, PH=book", dict(phuoc_hoa=95.7)),
                    ("B_cơ sở: BN FIT1→FIT2 + hồi tố BN", dict(bn_px=FIT2, retro=(FIT1-FIT2)*BN_GWH/1000*6.9)),
                    ("C_xấu: cả 2 về trần chuyển tiếp + hồi tố + thuỷ văn −15% 2027 + lãi +1pp",
                     dict(bn_px=TRAN, nm_px=TRAN, retro=(FIT1-TRAN)*BN_GWH/1000*6.9+(FIT2-TRAN)*NM_GWH/1000*5.9,
                          hydro_shock=0.15, rate_add=0.01))]:
        e = model(**kw); print(nm_, "VCSH", round(e[0]), "đ/cp", round(e[1]), "retro", round(kw.get('retro',0)))
    print("Độ nhạy giá mặt trời (giảm đồng đều cả 2, không hồi tố / có hồi tố):")
    for cut in (0, 0.25, 0.51):
        a = model(bn_px=FIT1*(1-cut), nm_px=FIT2*(1-cut))[1]
        rt = cut*(FIT1*BN_GWH*6.9 + FIT2*NM_GWH*5.9)/1000
        b = model(bn_px=FIT1*(1-cut), nm_px=FIT2*(1-cut), retro=rt)[1]
        print(f"  −{int(cut*100)}%: {round(a)} / {round(b)} (hồi tố {round(rt)} tỷ)")
    print("Độ nhạy r (lãi huy động ±50/100bp, β=1; β=0.5 = nửa):")
    for d in (-0.01,-0.005,0,0.005,0.01):
        print(f"  {d*1e4:+.0f}bp: β1 {round(model(r=0.135+d, bn_px=FIT2, retro=(FIT1-FIT2)*BN_GWH/1000*6.9)[1])}  β0.5 {round(model(r=0.135+d/2, bn_px=FIT2, retro=(FIT1-FIT2)*BN_GWH/1000*6.9)[1])}")
    print("Hydro ±20% (cơ sở B):", [round(model(bn_px=FIT2, retro=(FIT1-FIT2)*BN_GWH/1000*6.9, hydro_scale=k)[1]) for k in (0.8,1.0,1.2)])
    print("Lãi vay +1pp (cơ sở B):", round(model(bn_px=FIT2, retro=(FIT1-FIT2)*BN_GWH/1000*6.9, rate_add=0.01)[1]))
    print("Không thu được phần phải thu vượt (cơ sở B, ar_excess=0):", round(model(bn_px=FIT2, retro=(FIT1-FIT2)*BN_GWH/1000*6.9, ar_excess=0)[1]))
    for y,e,f in base_ok[2][:8]: print(y,e,f)
