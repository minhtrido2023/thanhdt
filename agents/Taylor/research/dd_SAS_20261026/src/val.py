# Dinh gia kich ban SAS - so dau vao: BQ ticker_financial + bao chi trich BCTC; gia dinh = uoc luong
SH=133.45191e6; PX=37000
np_q={'25Q4':367.4,'26Q1':155.1,'26Q2':215.7,'26Q3':168.7}   # BQ NP_P0, ty
ttm=sum(np_q.values()); mcap=PX*SH/1e9
print(f"TTM NP {ttm:.1f} ty, mcap {mcap:.0f} ty, PE_ttm {mcap/ttm:.2f}")
# loai co tuc dau tu (Q2 88 + Q3 47.8, bao chi trich BCTC) sau thue 20% -> thu nhap tai chinh lumpy
div_9m=88+47.8
print(f"Q2-Q3 co tuc nhan {div_9m:.1f} ty; Q2 vs Q3 NP chenh {215.7-168.7:.1f}")
# chuan hoa: FY26 = 9M 539.5 + Q4 (uoc luong 150-180, Q4/25 co bu DFS mot lan)
for q4 in (150,180):
    fy=539.5+q4; core=fy-div_9m*0.8
    print(f"FY26e NP {fy:.0f} (PE {mcap/fy:.2f}); tru co tuc dau tu ~{core:.0f} (PE {mcap/core:.2f})")
ret=0.883  # EPS 2025 4602 / (NP2025 695.6/SH) -> ty le giu lai sau trich quy
print("ty le EPS/NP 2025:", round(4602/(695.6e9/SH),3))
r=0.14; xcash=3500  # tien thua/cp (uoc luong ~50% cua 945 ty tien+TG ngan han)
def val(eps27,eps28,g): return eps27/(1+r)+ (eps28/(r-g))/(1+r)+xcash
base_eps=650e9*ret/SH
print("EPS chuan hoa (NP 650):", round(base_eps))
sc={'bull (thang thau LT, giu TSN)':(base_eps,base_eps*1.05,0.03,0.25),
    'base (LT share nho, -25%)':(base_eps,base_eps*0.75,0.03,0.45),
    'bear (truot thau LT, -50%)':(base_eps,base_eps*0.50,0.02,0.30)}
ev=0
for k,(a,b,g,p) in sc.items():
    v=val(a,b,g); ev+=p*v; print(f"{k}: {v:,.0f} d (p={p})")
print(f"Ky vong co trong so: {ev:,.0f} d vs gia {PX:,} -> {ev/PX-1:+.1%}")
for rr in (0.12,0.16):
    r=rr; print(f"r={rr}: base {val(base_eps,base_eps*0.75,0.03):,.0f}")
