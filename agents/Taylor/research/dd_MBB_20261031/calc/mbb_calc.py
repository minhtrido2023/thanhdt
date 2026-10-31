"""MBB DD 31/10/2026 — tái lập: python3 -I calc/mbb_calc.py > calc/mbb_calc_out.txt
Mọi số đầu vào (triệu đồng → quy ra tỷ) chép từ calc/notes_read.md (đọc ảnh BCTC gốc). Giả định gắn (ước lượng)."""
B=1e3  # triệu -> tỷ
def t(x): return x/B
# ---- earning assets (gross loans + interbank + NHNN + securities + mua nợ) ----
EA={ # date: (NHNN, TCTD, CKKD, CVKH, muano, AFS, HTM, TONG)
 '2024-12-31':(29825253,76785622,7931834,776657846,1041362,205507956,4612504,1128801062),
 '2025-06-30':(15251535,96081337,4618286,879888513,2660325,258676335,4255592,1289644328),
 '2025-09-30':(17507511,108324759,3195873,931498596,2548681,232242770,4497417,1328560306),
 '2025-12-31':(68494426,182923726,4692622,1084019370,2465314,221512464,4295125,1615763927),
 '2026-03-31':(15156039,165297962,5093432,1120562481,2287269,259054739,4336559,1611222764),
 '2026-06-30':(27417370,174745578,8888529,1227554477,2247703,242744694,4573649,1733012662),
 '2026-09-30':(15822936,183829058,41494707,1288128443,6489462,252453626,4758333,1837857452),
}
ea={d:t(sum(v[:7])) for d,v in EA.items()}
loans={d:t(v[3]) for d,v in EA.items()}
TA={d:t(v[7]) for d,v in EA.items()}
# quarterly NII / TN lãi / CP lãi (HN)
Q={ # q: (TNlai, CPlai, NII, days, start, end)
 'Q3/25':(22265897,9275373,12990524,92,'2025-06-30','2025-09-30'),
 'Q4/25':(26132781,11577489,14555292,92,'2025-09-30','2025-12-31'),
 'Q1/26':(62988909-34006838,31182138-17113184,31806771-16893654,90,'2025-12-31','2026-03-31'),
 'Q2/26':(34006838,17113184,16893654,91,'2026-03-31','2026-06-30'),
 'Q3/26':(37792619,19956645,17835974,92,'2026-06-30','2026-09-30'),
}
print("== 1. NIM hợp nhất theo quý (NII annualized / TS sinh lãi BQ đầu-cuối quý; TS sinh lãi = TG NHNN+TCTD+CKKD+CVKH gộp+mua nợ+CKĐT; tự tính, định nghĩa khác MB công bố)")
for q,(ti,ce,nii,dd,s,e) in Q.items():
    avg=(ea[s]+ea[e])/2; f=365/dd
    print(f"{q}: NII {t(nii):,.0f} tỷ | EA BQ {avg:,.0f} | NIM {t(nii)*f/avg*100:.2f}% | lợi suất TS {t(ti)*f/avg*100:.2f}% | chi phí lãi/EA {t(ce)*f/avg*100:.2f}% | TN lãi YoY/CP lãi YoY xem dưới")
print("NIM BỎ TG NHNN khỏi mẫu số (v2, theo phản biện; TG NHNN cuối năm tăng vọt 68,5k cuối 2025):")
ea_x={d:ea[d]-t(v[0]) for d,v in EA.items()}
for q,(ti,ce,nii,dd,s_,e_) in Q.items():
    print(f"  {q}: NIM ex-NHNN {t(nii)*365/dd/((ea_x[s_]+ea_x[e_])/2)*100:.2f}%")
print(f"Q3/26 vs Q3/25: TN lãi {37792619/22265897-1:+.1%} ; CP lãi {19956645/9275373-1:+.1%} ; NII {17835974/12990524-1:+.1%}")
print(f"9T26 vs 9T25: TN lãi {100781528/62955335-1:+.1%} ; CP lãi {51138783/25900510-1:+.1%} ; NII {49642745/37054825-1:+.1%}")
# 9T NIM
ea9=(ea['2025-12-31']+ea['2026-03-31']+ea['2026-06-30']+ea['2026-09-30'])/4
print(f"NIM 9T26 (EA BQ 4 mốc {ea9:,.0f}): {t(49642745)*365/273/ea9*100:.2f}%")
# parent-only NIM Q3 approx using parent EA end-points not all available -> parent 30/09 vs 31/12 only
pea_e=t(13998677+174365912+39874638+1231775508+6489462+247191405+477200); pea_s=t(66404931+168866071+3050285+1031103706+2465314+211971942+537000)
print(f"NIM riêng lẻ 9T26 (EA BQ 2 mốc 31/12-30/09 = {(pea_e+pea_s)/2:,.0f}; thô, (ước lượng) vì thiếu mốc giữa): {t(42291057)*365/273/((pea_e+pea_s)/2)*100:.2f}%")
print(f"NII riêng lẻ Q3 YoY {15414748/10669167-1:+.1%} ; CP lãi riêng lẻ Q3 YoY {19312612/9073942-1:+.1%}")
print("\n== 2. Huy động / CASA / LDR (HN)")
dep={'2025-12-31':921368132,'2026-09-30':993988042}; kkh={'2025-12-31':339352789,'2026-09-30':326388841}
gtcg={'2025-12-31':187236104,'2026-09-30':302399200}; tctd={'2025-12-31':248017489,'2026-09-30':265848000}
for d in dep:
    print(f"{d}: TG KH {t(dep[d]):,.0f} | KKH {t(kkh[d]):,.0f} ({kkh[d]/dep[d]*100:.1f}%) | GTCG {t(gtcg[d]):,.0f} | TG+vay TCTD {t(tctd[d]):,.0f} | CV KH/TG KH {loans[d]/t(dep[d])*100:.1f}% | CV/(TG KH+GTCG) {loans[d]/t(dep[d]+gtcg[d])*100:.1f}%")
print(f"Δ YTD: CV KH {loans['2026-09-30']/loans['2025-12-31']-1:+.1%} ({loans['2026-09-30']-loans['2025-12-31']:,.0f} tỷ) ; TG KH {dep['2026-09-30']/dep['2025-12-31']-1:+.1%} ({t(dep['2026-09-30']-dep['2025-12-31']):,.0f}) ; GTCG {gtcg['2026-09-30']/gtcg['2025-12-31']-1:+.1%} ({t(gtcg['2026-09-30']-gtcg['2025-12-31']):,.0f}) ; vay TCTD (dòng tiền vay) 64.382→102.412 {102411991/64382164-1:+.1%}")
inc=loans['2026-09-30']-loans['2025-12-31']; print(f"Nguồn tài trợ cho {inc:,.0f} tỷ tăng CV: TG KH {t(dep['2026-09-30']-dep['2025-12-31'])/inc:.0%}, GTCG {t(gtcg['2026-09-30']-gtcg['2025-12-31'])/inc:.0%}, TG NHNN rút {t(68494426-15822936)/inc:.0%}, VCSH {t(164141608-142022525)/inc:.0%}")
print(f"KKH cá nhân/DN: BCTC không tách KKH theo đối tượng (chỉ TG theo đối tượng: TCKT {t(429766844):,.0f} | cá nhân {t(564221198):,.0f}) -> CASA tách cá nhân/DN: CHƯA KIỂM ĐƯỢC")
print(f"KKH ngoại tệ 42.370 vs 34.899 (+21%) ; KKH VND 284.018 vs 304.454 ({284018447/304453535-1:+.1%})")
print(f"Lãi suất CP lãi tiền gửi 9T annualized / TG KH BQ: {t(35204301)*365/273/((t(dep['2025-12-31'])+t(dep['2026-09-30']))/2)*100:.2f}% (9T25 thô: {t(17814255)*365/273/((805647*0.85+t(dep['2025-12-31']))/2)*100:.2f}% — mẫu số 9T25 (ước lượng))")
print(f"CP lãi GTCG 9T annualized / GTCG BQ: {t(11381578)*365/273/((t(gtcg['2025-12-31'])+t(gtcg['2026-09-30']))/2)*100:.2f}%")
print("\n== 3. Chất lượng tài sản (HN | NH mẹ)")
hn={'25':(1084019370,10210040,3276216,4330016,6421264,13150593),'26':(1288128443,17013532,7230947,4778315,9465064,18181887)}
me={'25':(1031103706,5556322,1928698,3554034,6207288,11632139),'26':(1231775508,12898585,6167000,3562340,9185921,16430079)}
for nm,dct in (('HN',hn),('Mẹ',me)):
    for y,(L,g2,g3,g4,g5,dp) in dct.items():
        npl=g3+g4+g5; print(f"{nm} 20{y}: dư nợ {t(L):,.0f} | nhóm2 {t(g2):,.0f} ({g2/L*100:.2f}%) | NPL {t(npl):,.0f} ({npl/L*100:.2f}%) | nhóm 2-5 {(g2+npl)/L*100:.2f}% | DP {t(dp):,.0f} | bao phủ {dp/npl*100:.1f}%")
s=[hn['26'][i]-me['26'][i] for i in range(6)]; s25=[hn['25'][i]-me['25'][i] for i in range(6)]
print(f"Công ty con (HN−mẹ; gồm MCredit, MB Cambodia, MBS margin 16.696 nhóm 1; KHÔNG gồm MBV — BCTC HN-Q3 tr.2: MBV không hợp nhất theo điểm c k.1 Đ.185 Luật TCTD 2024): dư nợ {t(s[0]):,.0f} | nhóm2 {t(s[1]):,.0f} (đầu năm {t(s25[1]):,.0f}) | NPL {t(s[2]+s[3]+s[4]):,.0f} (đầu năm {t(s25[2]+s25[3]+s25[4]):,.0f}) | NPL/dư nợ trừ margin {(s[2]+s[3]+s[4])/(s[0]-16695619)*100:.1f}% | DP {t(s[5]):,.0f}")
print(f"Nhóm 2 mẹ YTD {12898585/5556322-1:+.0%} ; nhóm 3 mẹ {6167000/1928698-1:+.0%} ; HN nhóm2 {17013532/10210040-1:+.0%}")
wo=7877179; form=(21474326-14027496)+wo
avgL=(loans['2025-12-31']+loans['2026-09-30'])/2
print(f"Xoá nợ (sử dụng DP) 9T26 {t(wo):,.0f} tỷ ; hình thành NPL mới 9T = ΔNPL + xoá = {t(form):,.0f} tỷ = {t(form)*365/273/avgL*100:.2f}%/năm dư nợ BQ")
print(f"Trích DP cho vay 9T {t(12909248):,.0f} ; chi phí tín dụng (DP KQKD 12.943) annualized/dư nợ BQ: {t(12943191)*365/273/avgL*100:.2f}% ; Q3: {t(5241290)*365/92/((loans['2026-06-30']+loans['2026-09-30'])/2)*100:.2f}% ; 2025: {13743.504/((776657.846+1084019.370)/2)*100:.2f}%")
print(f"Nếu giữ bao phủ 93,7% như đầu năm: thiếu {0.937*t(21474326)-t(18181887):,.0f} tỷ DP (≈ {(0.937*t(21474326)-t(18181887))/t(10330100)*100:.0f}% LNTT Q3)")
print(f"Lãi dự thu (lãi phí phải thu): 31/12/25 {t(13549018):,.0f} → 30/09/26 {t(19827834):,.0f} ({19827834/13549018-1:+.0%}; dư nợ {loans['2026-09-30']/loans['2025-12-31']-1:+.0%}); /TTS {19827834/1837857452*100:.2f}% (ngưỡng Bobby 2%)")
print(f"Phải thu miễn truy đòi bộ chứng từ (LC, CV 9608): {t(8046079):,.0f} → {t(13596584):,.0f} ({13596584/8046079-1:+.0%}) = {13596584/1288128443*100:.2f}% dư nợ")
print(f"BĐS: KD BĐS {t(121188714):,.0f} → {t(179755906):,.0f} ({179755906/121188714-1:+.1%}) ; tỷ trọng 11,18% → 13,95% ; xây dựng 3,98% ; hộ gia đình (gồm vay mua nhà, không tách) 22,82%")
print(f"Cho vay trung dài hạn: {(175109533+474997102)/1288128443*100:.1f}% (31/12/25 {(127883727+353958134)/1084019370*100:.1f}%) ; dài hạn +{474997102/353958134-1:.0%}")
print("\n== 4. Thu nhập, chất lượng LN (HN, tỷ)")
TOI9=58955.963; PP9=43461.549; LT9=30518.358
one={'thu nợ đã xử lý':2079.601,'CK đầu tư':11.723,'CK kinh doanh':529.511,'góp vốn':25.203}
print(f"CIR 9T26 {15494.414/TOI9*100:.1f}% (9T25 {13451.694/48165.069*100:.1f}%) ; Q3 {5520.053/21091.443*100:.1f}% ; NII/TOI 9T {49642.745/TOI9*100:.1f}%")
print(f"Thu nợ đã xử lý + CK (KD+ĐT) = {2079.601+529.511+11.723:,.0f} tỷ = {(2079.601+529.511+11.723)/LT9*100:.1f}% LNTT 9T (ngưỡng Bobby 25%)")
print(f"FX: giao ngay+vàng thuần 1.533 (9T25 2.329) ; phái sinh tiền tệ thuần −1.066 (9T25 −832) ; vay TCTD ngoại tệ 50.308→71.432 => phái sinh lỗ là chi phí swap tài trợ ngoại tệ (suy luận)")
print(f"Bảo hiểm (DV): thu 7.422,6 − chi KD BH 5.264,2 = {7422.617-5264.209:,.0f} (9T25 {6589.983-4392.831:,.0f})")
print(f"Thuế hiệu dụng 9T {6118.292/LT9*100:.1f}%")
# DuPont / ROE
eq_s=142022.525-5886.495; eq_e=164141.608-7124.845
roe9=23784.072*365/273/((eq_s+eq_e)/2)
roa9=24400.066*365/273/((TA['2025-12-31']+TA['2026-09-30'])/2)
print(f"ROE 9T annualized (LNST NH / VCSH mẹ BQ 2 mốc) {roe9*100:.1f}% ; ROA {roa9*100:.2f}% ; đòn bẩy TTS/VCSH {TA['2026-09-30']/164141.608:.1f}x")
avgTA=(TA['2025-12-31']+TA['2026-09-30'])/2; k=365/273
print("DuPont 9T26 (/TTS BQ, annualized): NII {:.2f}% + ngoài lãi {:.2f}% − OPEX {:.2f}% − DP {:.2f}% = LNTT {:.2f}% ; ×(1−thuế) = ROA {:.2f}%".format(
 49642.745*k/avgTA*100,(TOI9-49642.745)*k/avgTA*100,15494.414*k/avgTA*100,12943.191*k/avgTA*100,LT9*k/avgTA*100,24400.066*k/avgTA*100))
print(f"PPOP/VCSH BQ (ROE trước DP, trước thuế) {PP9*k/((eq_s+eq_e)/2)*100:.1f}%")
print("\n== 5. Định giá (giá 19.300 đóng cửa 30/10/2026 [BQ]); mọi giả định tương lai = (ước lượng)")
SH=10068.749885  # triệu CP (VĐL 100.687,5 tỷ / 10.000)
P=19300
BV=164141.608-7124.845
bvps=BV/SH*1e3
ttm=23784.072+8762.570
print(f"VCSH mẹ 30/09 {BV:,.0f} tỷ ; BVPS {bvps:,.0f} đ ; P/B {P/bvps:.2f}x ; LNST NH TTM (Q4/25+9T26) {ttm:,.0f} tỷ ; EPS TTM {ttm/SH*1e3:,.0f} ; P/E TTM {P/(ttm/SH*1e3):.2f}x")
print("Chưa tính 200 triệu CP phát hành riêng lẻ (đã duyệt ĐHCĐ, chưa phát hành theo web_facts) => pha loãng tối đa ~2,0% số CP")
# Q4/26 + 2027 scenarios
sc={ # name: w, Q4 PPOP, Q4 DP, g_loan27, NIM27, cc27 (/dư nợ BQ), nonII/TA, CIR27
 'XẤU':  (0.35,16000,7500,0.12,0.036,0.022,0.0065,0.28),
 'CƠ SỞ':(0.45,17500,5500,0.18,0.039,0.017,0.0070,0.27),
 'TỐT':  (0.20,18700,4200,0.24,0.041,0.013,0.0075,0.26),
}
# v2: Q4 thường PPOP cao/DP thấp theo mùa: Q4/25 PPOP 13.298 (+20% QoQ từ Q3/25 11.051), DP 2.169. Q3/26 PPOP 15.571.
# Xấu: PPOP +3% QoQ, DP 7.500 (xây lại bao phủ) -> LNTT Q4 8.500; Cơ sở: PPOP +12% QoQ, DP 5.500 ~ Q3 -> 12.000 (+8% YoY);
# Tốt: PPOP +20% QoQ (như Q4/25), DP 4.200 -> 14.500. (ước lượng)
print(f"PPOP Q3/26 {10330.1+5241.29:,.0f} ; Q4/25 {11129+2169:,.0f} ; Q3/25 {7249.9+3801.5:,.0f} -> Q4/25 PPOP QoQ {(11129+2169)/(7249.9+3801.5)-1:+.0%}")
L26=1288128*1.035  # dư nợ cuối 2026 (ước lượng +3,5% Q4)
EA26=1740574*1.06  # EA cuối 2026 (ước lượng)
TA26=1837857*1.04
tax=0.20; nci=0.025
res={}
for n,(w,pp4,dp4,g,nim,cc,nonii,cir) in sc.items():
    lt26=30518.358+pp4-dp4
    ni26=lt26*(1-tax)*(1-nci)
    ea_avg=EA26*(1+g/2); ta_avg=TA26*(1+g/2); l_avg=L26*(1+g/2)
    nii=nim*ea_avg; non=nonii*ta_avg; toi=nii+non; opex=cir*toi; prov=cc*l_avg
    lt27=toi-opex-prov; ni27=lt27*(1-tax)*(1-nci)
    bv26=BV+ni26-23784.072  # VCSH mẹ cuối 2026 ≈ 30/09 + LN Q4
    bv26=BV+(ni26-23784.072)
    roe27=ni27/(bv26+ (ni27-0.10*SH*1.0)/2)
    res[n]=(w,lt26,lt27,ni27,roe27,bv26)
    print(f"{n} (w={w}): LNTT 2026 {lt26:,.0f} ({lt26/34268.358-1:+.1%} YoY; {lt26/39408:.0%} KH) | 2027: NII {nii:,.0f} TOI {toi:,.0f} OPEX {opex:,.0f} DP {prov:,.0f} LNTT {lt27:,.0f} ({lt27/lt26-1:+.1%}) LNST NH {ni27:,.0f} | ROE27 {roe27*100:.1f}% | P/E27 {P/(ni27/SH*1e3):.1f}x")
ew=sum(v[0]*v[2] for v in res.values()); print(f"LNTT 2027 kỳ vọng có trọng số {ew:,.0f} tỷ")
# capital: sustainable growth
print("Vốn: CAR HN 30/06/26 10,7% (Tier1 9,9%), CAR riêng 10,28% (Tier1 9,02%) [web_facts, thứ cấp]. Tăng trưởng tự tài trợ ≈ ROE×(1−tỷ lệ chi cổ tức tiền):")
for roe in (0.18,0.20,0.22):
    for po in (0.25,0.35):
        print(f"  ROE {roe:.0%} trả tiền {po:.0%} -> VCSH/RWA tự tăng ~{roe*(1-po):.1%}/năm")
# Residual income: value at 31/12/2026, then discount 2 tháng
def ri_value(roe_path, roeT, gT, ke, bv0, payout=0.30):
    v=bv0; bv=bv0; pv=0
    for i,r in enumerate(roe_path,1):
        ni=r*bv; ri=(r-ke)*bv; pv+=ri/(1+ke)**i; bv=bv+ni*(1-payout)
    n=len(roe_path); tv=(roeT-ke)*bv/(ke-gT)/(1+ke)**n
    return (bv0+pv+tv), tv, pv
print("\nRI 3 giai đoạn: 2027-2029 tường minh + terminal Gordon RI; BV0 = VCSH mẹ cuối 2026 theo kịch bản; payout tiền 30% (ước lượng); giá trị/CP chiết khấu 2 tháng về 31/10/2026")
paths={'XẤU':([0.13,0.14,0.15],0.14,0.06),'CƠ SỞ':([0.185,0.18,0.17],0.16,0.07),'TỐT':([0.22,0.21,0.20],0.18,0.08)}  # ROE path gắn với ROE27 từng kịch bản; ROE_T thấp hơn lịch sử vì Basel III/TT14 (ước lượng)
RIW={}
for ke in (0.123,0.128,0.134,0.15):
    tot=0; line=[]; vals={}
    for n,(path,roeT,gT) in paths.items():
        w=res[n][0]; bv0=res[n][5]
        v,tv,pv=ri_value(path,roeT,gT,ke,bv0)
        ps=v/SH*1e3/(1+ke)**(2/12); tot+=w*ps; vals[n]=ps
        line.append(f"{n} {ps:,.0f} (P/B ngụ ý {ps/bvps:.2f}x; TV {tv/v:.0%} giá trị)")
    alt=0.45*vals['XẤU']+0.35*vals['CƠ SỞ']+0.20*vals['TỐT']; RIW[ke]=(tot,alt,vals)
    lab=" [thị trường ngụ ý]" if ke==0.15 else ""
    print(f"Ke {ke:.1%}{lab}: "+" | ".join(line)+f" | có trọng số (0,35/0,45/0,20) {tot:,.0f} đ ({tot/P-1:+.0%} vs giá) | độ nhạy w xấu 0,45 (0,45/0,35/0,20) {alt:,.0f} đ")
print("\nGordon P/B=(ROE−g)/(Ke−g) — độ nhạy (P/B; × BVPS cuối 2026 cơ sở ≈ giá):")
bv26b=res['CƠ SỞ'][5]/SH*1e3
for g in (0.07,0.08,0.09):
    print(f" g={g:.0%}: "+" ".join(f"ROE{roe:.0%}/Ke{ke:.1%}={(roe-g)/(ke-g):.2f}x({(roe-g)/(ke-g)*bv26b/(1+ke)**(2/12):,.0f})" for roe in (0.16,0.18,0.20) for ke in (0.123,0.134)))
print(f"Giá 19.300 ngụ ý (Ke 12,3–13,4%, g 8%): ROE bền vững = g + P/B×(Ke−g) = {(0.08+P/bvps*(0.123-0.08))*100:.1f}% – {(0.08+P/bvps*(0.134-0.08))*100:.1f}%")

print("\n== 6. Định giá tương đối (BQ 30/10/2026: P/B vs ROE5Y của 13 NH) + Ke ngụ ý thị trường")
import csv
rows=[r for r in csv.DictReader(open('calc/bq_peers_20261030.csv'))]
# v2: TCB 30/10 = ngày GDKHQ, BQ chia giá đã điều chỉnh cho BVPS chưa điều chỉnh -> P/B 0,78x là artifact.
# Sửa: P/B 29/10 (giá thô 33.500, BVPS cũ) 1,2030 × Close đ/c 21.600/22.350 = 1,163x
for r in rows:
    if r['ticker']=='TCB': r['PB']=str(1.20303817872764*21600/22350)
xs=[float(r['ROE5Y']) for r in rows if r['ticker'] not in ('STB',)]; ys=[float(r['PB']) for r in rows if r['ticker'] not in ('STB',)]
n=len(xs); mx=sum(xs)/n; my=sum(ys)/n; b=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs); a=my-b*mx
r2=(sum((x-mx)*(y-my) for x,y in zip(xs,ys))**2)/(sum((x-mx)**2 for x in xs)*sum((y-my)**2 for y in ys))
for r in sorted(rows,key=lambda r:-float(r['PB'])): print(f"  {r['ticker']}: P/B {float(r['PB']):.2f} | P/E {float(r['PE']):.1f} | ROE5Y {float(r['ROE5Y'])*100:.1f}% | ADV1M {r['adv_bn']} tỷ")
ysx=sorted(float(r['PB']) for r in rows if r['ticker'] not in ('STB','MBB')); m=len(ysx)
med=(ysx[m//2-1]+ysx[m//2])/2 if m%2==0 else ysx[m//2]  # trung vị 11 NH KHÔNG gồm MBB, bỏ STB
print(f"Hồi quy P/B~ROE5Y (bỏ STB, n={n}): P/B = {a:.2f} + {b:.2f}×ROE ; R²={r2:.2f} (yếu) ; MBB ROE5Y 22,7% -> P/B dự báo {a+b*0.2269:.2f}x ({(a+b*0.2269)*bvps:,.0f} đ) ; trung vị P/B (11 NH, loại MBB+STB) {med:.2f}x ({med*bvps:,.0f} đ)")
reg=(a+b*0.2269)*bvps; hist=1.25*bvps
riw134=RIW[0.134][0]; riw128=RIW[0.128][0]
c=0.5*riw134+0.25*reg+0.25*hist
print(f"Tâm vùng v2 = 0,5×RI có trọng số @Ke13,4% ({riw134:,.0f}) + 0,25×hồi quy ({reg:,.0f}) + 0,25×P/B lịch sử 1,25x ({hist:,.0f}) = {c:,.0f} đ ; v1 (1/3 mỗi phần, RI w xấu 0,30) = 22.000")
print(f"Biên dưới tham chiếu: RI xấu @13,4% {RIW[0.134][2]['XẤU']:,.0f} / trung vị comp {med*bvps:,.0f} ; biên trên: RI có trọng số @12,8% {riw128:,.0f} ; RI có trọng số @15% (thị trường ngụ ý) {RIW[0.15][0]:,.0f}")
for roe in (0.16,0.18,0.20):
    for g in (0.06,0.07):
        print(f"  Ke ngụ ý tại P/B {P/bvps:.2f}x với ROE bền vững {roe:.0%}, g {g:.0%}: {(g+(roe-g)/(P/bvps))*100:.1f}%")

print("\n== 7. Giá & thanh khoản (BQ ticker, Close điều chỉnh)")
px=[(r['time'],float(r['Close']),float(r['val_bn'])) for r in csv.DictReader(open('calc/bq_mbb_px_1y.csv'))]
d={a:b for a,b,c in px}
def ret(a,b): return d[b]/d[a]-1
hi=max(px,key=lambda x:x[1]); lo=min(px,key=lambda x:x[1])
print(f"1 năm (từ 01/10/2025): đỉnh {hi[1]:,.0f} ({hi[0]}), đáy {lo[1]:,.0f} ({lo[0]}); giá 30/10 cách đỉnh {d['2026-10-30']/hi[1]-1:+.1%}")
for a,b,lab in (('2026-10-16','2026-10-21','quanh CV 9608 (18/10, CN) + KQ Q3 sơ bộ'),('2026-10-16','2026-10-30','16/10→30/10'),('2026-09-30','2026-10-30','tháng 10'),('2025-12-31','2026-10-30','YTD')):
    try: print(f"  {lab}: {ret(a,b):+.1%}")
    except KeyError as e: print('  thiếu ngày',e)
v20=[c for a,b,c in px][-20:]; v60=[c for a,b,c in px][-60:]
print(f"ADV giá trị 20 phiên {sum(v20)/20:,.0f} tỷ ; 60 phiên {sum(v60)/60:,.0f} tỷ")
for nav in (50e3,100e3,200e3):
    for w in (0.005,0.01):
        pos=nav*w/1e3  # tỷ (NAV tính bằng triệu? -> nav tỷ)
print("Sizing: vị thế 0,5–1,0% NAV của quỹ 50–200 tỷ = 0,25–2 tỷ ≈ <1% ADV 1 phiên — không ràng buộc thanh khoản")

print("\n== 8. Xu hướng theo QUÝ chất lượng nợ (31/12/25 → 30/06/26 → 30/09/26)")
for nm,ser in (('HN',[(1084019370,10210040,14027496,13150593),(1227554477,11989743,4622128+4428065+8747009,16662881),(1288128443,17013532,21474326,18181887)]),
               ('Mẹ',[(1031103706,5556322,11690020,11632139),(1172763521,7720289,3588111+3359417+8464679,None),(1231775508,12898585,18915261,16430079)])):
    for lab,(L,g2,npl,dp) in zip(('31/12/25','30/06/26','30/09/26'),ser):
        cov=f"{dp/npl*100:.1f}%" if dp else "n/a"
        print(f"  {nm} {lab}: nhóm2 {g2/1e3:,.0f} ({g2/L*100:.2f}%) | NPL {npl/1e3:,.0f} ({npl/L*100:.2f}%) | bao phủ {cov}")
print(f"  QoQ Q3: HN nhóm2 {17013532/11989743-1:+.0%}, NPL {21474326/17797202-1:+.0%} ; mẹ nhóm2 {12898585/7720289-1:+.0%}, NPL {18915261/15412207-1:+.0%} ; dư nợ HN QoQ {1288128443/1227554477-1:+.1%}")
print(f"  H1 (6 tháng): HN nhóm2 {11989743/10210040-1:+.0%} ; NPL {17797202/14027496-1:+.0%} => Q3 là quý tăng tốc")

print("\n== 9. MBV — rủi ro NGOÀI BẢNG (không hợp nhất; tới 30/09/2026 MB chưa góp vốn) — (ước lượng)")
print("Sự kiện: BCTC HN-Q3 tr.2: không hợp nhất (điểm c k.1 Đ.185 Luật TCTD 2024), chưa góp vốn tại 30/09/2026.")
print("BCTN25 thuyết minh bên liên quan: MB phải thu bán nợ từ MBV 11.248 tỷ (31/12/2025) vs 5.853 (31/12/2024).")
print("WEB thứ cấp: lỗ luỹ kế MBV 15.688 (31/12/2024, Baodautu 11/04/2025); MB QĐ 14328/QĐ-MB-HS 01/10/2026 góp 3.500 tỷ (thitruongtaichinhtiente 03/10/2026); dự kiến tới 5.000.")
for nm,x in (("góp 3.500, mất trắng",3500),("góp 5.000, mất trắng",5000),("bù toàn bộ lỗ luỹ kế 2024 15.688 (cận trên thô)",15688),("phải thu bán nợ 11.248 mất 30%",11248*0.3)):
    print(f"  {nm}: −{x:,.0f} tỷ = {x/BV*100:.1f}% VCSH mẹ 30/09 ; BVPS −{x/SH*1e3:,.0f} đ ; P/B tại 19.300 → {P/((BV-x)/SH*1e3):.2f}x")
print("  Góp vốn là chuyển tài sản (tiền → khoản đầu tư), KHÔNG tự động giảm BV; chỉ giảm khi phải trích lập/giảm giá. Khoản góp vào TCTD khác có thể bị trừ khi tính vốn tự có (chưa kiểm).")
