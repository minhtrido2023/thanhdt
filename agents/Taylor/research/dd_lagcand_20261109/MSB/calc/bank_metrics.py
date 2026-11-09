"""Chi so ngan hang tu so doc anh (calc/notes_read.md). python3 -I calc/bank_metrics.py > calc/bank_metrics_out.txt (trieu dong -> ty)"""
t = lambda x: x / 1e3
L = {'26': (232946662, 3903964, 1233021, 1389493, 3662305), '25': (205208835, 2346755, 889398, 1461694, 3169256)}
P = {'26': (222925458, 3193248, 917310, 1029639, 3539579), '25': (201404014, 2019220, 739481, 1426379, 3007343)}
DP = {'26': 2964303, '25': 2850595}
for nm, D in (('HN', L), ('Rieng', P)):
    for y, (l, g2, g3, g4, g5) in D.items():
        npl = g3 + g4 + g5
        cov = f" | bao phu {DP[y]/npl:.1%}" if nm == 'HN' else ''
        print(f"{nm} 20{y}: du no {t(l):,.0f} | nhom2 {t(g2):,.0f} ({g2/l:.2%}) | NPL {t(npl):,.0f} ({npl/l:.2%}) | nhom2-5 {(g2+npl)/l:.2%}{cov}")
s = [L['26'][i] - P['26'][i] for i in range(5)]; s5 = [L['25'][i] - P['25'][i] for i in range(5)]
print(f"TNEX (HN - rieng) 30/09: du no {t(s[0]):,.0f} (31/12 {t(s5[0]):,.0f}, x{s[0]/s5[0]:.2f}) | nhom2 {t(s[1]):,.0f} ({s[1]/s[0]:.1%}) | NPL {t(sum(s[2:])):,.0f} ({sum(s[2:])/s[0]:.1%}); 31/12 NPL {sum(s5[2:])/s5[0]:.1%}")
npl26 = sum(L['26'][2:]); npl25 = sum(L['25'][2:]); wo = 1351437
avgL = (L['26'][0] + L['25'][0]) / 2
print(f"Hinh thanh NPL 9T = dNPL {t(npl26-npl25):,.0f} + xoa {t(wo):,.0f} = {t(npl26-npl25+wo):,.0f} ty = {(npl26-npl25+wo)*365/273/avgL:.2%}/nam du no BQ")
print(f"Chi phi tin dung 9T26 (DP 1.466) /du no BQ annualized {1466231*365/273/avgL:.2%}; Q3 {428706*365/92/avgL:.2%}; 9T25 1.572")
print(f"Bao phu 80%: thieu {t(0.8*npl26-DP['26']):,.0f} ty truoc thue; 100%: {t(npl26-DP['26']):,.0f}")
# CASA
k26, k25, d26, d25 = 44390526, 55328682, 217397520, 196671626
print(f"KKH/TG KH: 30/09 {k26/d26:.1%} | 31/12 {k25/d25:.1%}; KKH {t(k26-k25):+,.0f} ty ({k26/k25-1:+.1%}); TG KH {d26/d25-1:+.1%}; CV KH {L['26'][0]/L['25'][0]-1:+.1%} YTD")
# EA, NIM 9T
ea = lambda nhnn, tctd, cv, ck: nhnn + tctd + cv + ck
e26 = ea(5641338, 76935375, 232946662, 87844545); e25 = ea(9819956, 73968963, 205208835, 97307982)
print(f"NIM 9T26 tu tinh (NII 9.621 annualized / TSSL BQ 2 moc {t((e26+e25)/2):,.0f}): {9620781*365/273/((e26+e25)/2):.2%}; loi suat {22348762*365/273/((e26+e25)/2):.2%}; chi phi lai/TSSL {12727981*365/273/((e26+e25)/2):.2%}")
print(f"Q3 YoY: TN lai {8269325/5459904-1:+.1%} CP lai {4847289/2644588-1:+.1%} NII {3422036/2815316-1:+.1%}; 9T NII {9620781/7903940-1:+.1%}")
# LAG surprise
q = dict(nii=(3422036, 2815316), dv=(302277, 199632), fx=(130059, 284835), ckdt=(-25481, -36528), khac=(156199, 140381), opex=(-1539318, -1326265), dp=(-428706, -490078))
print("Phan ra dLNTT Q3 YoY (+{:,.0f} ty):".format(t(2017066 - 1587293)), ", ".join(f"{k} {t(a-b):+,.0f}" for k, (a, b) in q.items()))
print(f"LNST Q3 {1649203/1274181-1:+.1%} YoY, {1649203/1250603-1:+.1%} QoQ; 9T {4414028/3777274-1:+.1%}; TTM {(4414028+1851246)/(1616976+1265601+1237492+1274181)-1:+.1%}")
print(f"Neu DP Q3 giu muc Q3/25 (490): LNTT Q3 {t(2017066-(490078-428706)):,.0f} ({(2017066-(490078-428706))/1587293-1:+.1%})")
print(f"Lai phi phai thu / TTS 30/09: {12329388/439959891:.2%}; tin dung lai phai thu 30/06 8.103 vs 6.803 (+{8103328/6802719-1:.0%}) vs CVKH H1 +{0:.0%}")
print(f"LC mien truy doi 30/06 9.229 vs 2.383 (x{9229281/2382577:.1f}); = {9229281/232946662:.1%} du no; tang truong 'tin dung + LC' 6T vs CV")
print(f"Phai thu ban no 4.001 = {4001159/46857045:.1%} VCSH; dat coc thue VP 3.300 = {3299743/46857045:.1%} VCSH")
print(f"VCSH/TTS {46857045/439959891:.1%}; LDR (CV/TG KH) {L['26'][0]/d26:.1%}; CV/(TG KH+GTCG) {L['26'][0]/(d26+34102379):.1%}")
