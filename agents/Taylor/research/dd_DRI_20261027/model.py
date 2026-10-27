"""DD DRI 27/10/2026 — model độ nhạy + định giá chu kỳ. Mọi input có nhãn nguồn. Chạy: python3 model.py"""
import csv, statistics as st
SH = 73.2e6                      # [BCTN] số CP
PX = 14700                       # [BQ ticker] đóng cửa 26/10/2026
MCAP = SH*PX/1e9
# --- calibration: run-rate hiện tại ---
V = 14000                        # t/năm [UL]: 2025 bán 14.007,76 [BCTN]; KH 2026 khai thác 13.800 [BCTN]
P0 = 47.24*1.18                  # tr/t [UL]: giá 2025 47,24 [BCTN] × (1+18%) giá Q2/26 YoY (blind block, từ GT +85,45% DT/+59,82% SL)
C0 = 33.11                       # tr/t [BCTN] giá vốn cao su 2025
OTHER_GP = 10                    # tỷ/năm [UL] sầu riêng/điều/khác (2025: cao su 96,77% LN gộp)
SGA = (14.822+23.609)*2          # tỷ/năm [BCTC] BH+QLDN H1/26 ×2
FIN = (19.838-4.710)*2*0.83      # tỷ/năm [BCTC] TC thu−chi H1/26 ×2, trừ ~17% phần LCTG [UL]
TAX = (34.567+0.774)/181.851     # [BCTC] thuế hiệu dụng H1/26
def lnst(P, C=C0, v=V, sga=SGA):
    return (v*(P-C)/1e3 + OTHER_GP - sga + FIN)*(1-TAX)   # v*(tr/t)/1e3 = tỷ
base = lnst(P0)
print(f"MCAP {MCAP:.1f} tỷ | P0 {P0:.2f} tr/t | SGA {SGA:.1f} FIN {FIN:.1f} TAX {TAX:.3f}")
print(f"LNST run-rate (calib) {base:.1f} tỷ  [đối chiếu: LN lõi TTM 221 (blind block E3)]")
print("\nĐộ nhạy LNST năm theo giá bán (V=14.000t):")
print("  dP    | (a) giá vốn cố định | (b) 30% DT tăng thêm chảy vào lương/thưởng")
for x in (-.3,-.2,-.1,.1,.2,.3):
    P=P0*(1+x); a=lnst(P); b=lnst(P, C=C0+0.30*(P-P0))
    print(f"  {x:+.0%} | {a:6.1f} ({a/base-1:+.0%}) | {b:6.1f} ({b/base-1:+.0%})")
print(f"  hoà vốn LNTT (a): P = {C0+ (SGA-OTHER_GP-FIN)*1e3/V:.1f} tr/t")
# quý: LNST Q3 theo sản lượng bán quý
print("\nLNST QUÝ theo sản lượng bán (P0, C0; SGA/FIN/4):")
for vq in (2500,3500,4500,5500):
    q=(vq*(P0-C0)/1e3 + OTHER_GP/4 - SGA/4 + FIN/4)*(1-TAX); print(f"  {vq} t -> {q:.1f} tỷ")
# --- chuẩn hoá chu kỳ ---
r=[(m,float(p)) for m,p in csv.reader(open('/home/trido/thanhdt/WorkingClaude/data/rubber_monthly.csv')) if m!='month']
med10=st.median([p for m,p in r if m>='2016-10']); med5=st.median([p for m,p in r if m>='2021-10'])
rss25=st.mean([p for m,p in r if m.startswith('2025')]); q3=st.mean([p for m,p in r if m in('2026-07','2026-08','2026-09')])
print(f"\nRSS3 WB: 2025 {rss25:.3f} | Q3/26 {q3:.3f} | med5y {med5:.3f} | med10y {med10:.3f}")
CASH=264.7; DIV=73.2; NETC=CASH-DIV          # [BCTC] net cash 30/06 − cổ tức 10% (ex ~22/09, [BQ] Price gap) [UL]
DKR=40*0.5                                   # khoản cho Dakruco vay, haircut 50% [UL]
def scen(name, rss, c, r_, peak_yrs, w):
    P=47.24*rss/rss25                       # [UL] neo giá 2025, bỏ qua trôi tỷ giá
    C=c; ni=lnst(P,C=C, sga=SGA*0.9)        # SGA giảm 10% khi thưởng giảm [UL]
    core=ni-NETC*0.05*0.8                    # trừ lãi tiền gửi sau thuế (5%/năm) [UL]
    ann=(1-(1+r_)**-28)/r_                   # quyền đất Lào tới ~2054 (ước lượng) => 28 năm
    excess=sum((base-ni)*0.9/(1+r_)**(t+0.5) for t in range(int(peak_yrs)))+ (peak_yrs%1)*(base-ni)*0.9/(1+r_)**(int(peak_yrs)+0.5)
    ev=core*0.9*ann                          # FCF≈90% LN (capex>KH do sầu riêng/tái canh) [UL]
    eq=ev+excess+NETC+DKR; fv=eq*1e9/SH
    print(f"  {name:5s} P={P:5.1f} C={C:4.1f} NI_norm={ni:6.1f} core={core:6.1f} PEcore@px={(MCAP-NETC)/core:5.1f}x "
          f"r={r_:.0%} ann={ann:.2f} EV_norm={ev:6.1f} excess={excess:6.1f} FV={fv:,.0f} đ  w={w}")
    return fv,w
print("\nKịch bản (FV/cp):")
S=[scen("Bear",med10,32.0,0.14,0.5,0.25), scen("Base",(med10+med5)/2,32.5,0.13,1.0,0.50), scen("Bull",med5,33.0,0.12,2.0,0.25)]
print(f"  Kỳ vọng có trọng số: {sum(f*w for f,w in S):,.0f} đ vs giá {PX:,} đ")
