"""TCH redo 05/11/2026 (job Taylor_20261105_014133). Chay: $DNA_PYEXE -B model.py > model_out.txt
Dau vao BCTC: doc tu anh BCTC hop nhat/rieng 01/04-30/09/2026 (Q2FY26 = quy lich 7-9/2026, chua soat xet) trong
dd_TCH_20261031/calc/notes_read.md + REPORT.md v2 (skeptic REFUTED-da-ap). KHONG tai lai (da co src/).
Thay doi khung so v2: (1) r 12,85% -> r(dep) neo 13,5% @7,40%; (2) quy dat moi 150 To Hieu + I.14 = NPV 0 (gia so) o MOI diem
(luat 03/11), v2 gop vao thang du 40%; (3) chiet khau quan tri = WARNING, bo khoi base/luoi, chi do nhay; (4) gia 04/11/2026;
(5) chiet khau thanh khoan sqrt-law; (6) luoi P10/P50/P90."""
import sys, os, json, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', '_common'))
import liq as L
SH = 1003.312808                                   # tr cp (TM21d)
dep, dep_src = L.current_dep()
R = L.r_of(dep)
LQ = L.liq('TCH'); PX = LQ['price']; LD = LQ['disc_ref']
VAT, GM = 1.08, 0.519                               # VAT bq (uoc luong); bien gop BDS 6T FY26 [TM23/25]
EQ_ME = 15279.65 - 3120.54                          # VCSH co dong me 30/09/2026
EQ_DIRECT = 10530.2 - 4571.6                        # rieng: VCSH - dau tu con thuan
EQ_SUBS = EQ_ME - EQ_DIRECT
proj = {"NC-II": (3099.20, 0.6802, 1.0, "crv"), "Green River": (1837.75, 1.0, 1.5, "me"),
        "H2": (617.83, 1.0, 2.0, "me"), "H1+khac": (38.15 + 6.88, 0.80, 1.0, "khac")}
HTK = {"me": 759.57 + 2557.50 + 555.53 + 1677.51 + 1.71, "crv": 7390.37 + 1328.75}
HTK["khac"] = 14630.92 - HTK["me"] - HTK["crv"]
NEW = {"me": 1677.51, "crv": 1328.75}               # 150 To Hieu (me), I.14 (Dai Loc qua CRV): mua dat 6T FY26 [TM17]
SHARE = {"me": 1.0, "crv": 0.6802, "khac": 0.80}
cost_bl = {"me": 0.0, "crv": 0.0, "khac": 0.0}
for k, (n, sh, y, g) in proj.items():
    cost_bl[g] += n / VAT * (1 - GM)
rest_old = {k: HTK[k] - cost_bl[k] - NEW.get(k, 0.0) for k in HTK}

def nav(m, s_old, hold, r=R, gov=0.0, s_new=0.0):
    pv = lambda y: 1 / (1 + r) ** y
    bl = {"me": 0.0, "sub": 0.0}
    for k, (n, sh, y, g) in proj.items():
        bl["me" if g == "me" else "sub"] += n / VAT * m * sh * pv(y)
    sur_me = (rest_old["me"] * s_old + NEW["me"] * s_new) * pv(4)
    sur_sub = ((rest_old["crv"] * s_old + NEW["crv"] * s_new) * SHARE["crv"] + rest_old["khac"] * s_old * SHARE["khac"]) * pv(4)
    direct = EQ_DIRECT + bl["me"] + sur_me; subs = EQ_SUBS + bl["sub"] + sur_sub
    return (direct + subs * (1 - hold)) * (1 - gov) / SH * 1000

SC = {"xau": dict(m=0.30, s_old=0.25, hold=0.30, p=0.25), "co so": dict(m=0.335, s_old=0.40, hold=0.20, p=0.50),
      "tot": dict(m=0.36, s_old=0.55, hold=0.10, p=0.25)}
out = dict(ticker='TCH', price=PX, price_date=LQ['price_date'], r=R, dep=dep, dep_src=dep_src, liq=LQ, scen={})
print(f"r = {R:.2%} (dep hieu dung {dep:.2%} [{dep_src}] vs neo {L.DEP_ANCHOR:.2%} {L.DEP_ANCHOR_DATE}); gia {PX:,.0f} ({LQ['price_date']})")
print(f"HTK con lai sau backlog, TRU quy dat moi (NPV 0): {{k: round(v,1) for k,v in rest_old.items()}} = {rest_old}; quy dat moi {NEW}")
for k, p in SC.items():
    v = nav(p['m'], p['s_old'], p['hold']); out['scen'][k] = dict(pre=v, post=v * (1 - LD), **p)
    print(f"{k:7s} p={p['p']:.2f} m={p['m']:.1%} s_old={p['s_old']:.0%} hold={p['hold']:.0%}: {v:,.0f} -> sau CK thanh khoan {v*(1-LD):,.0f}")
cpre = sum(SC[k]['p'] * out['scen'][k]['pre'] for k in SC); out['center_pre'] = cpre; out['center_post'] = cpre * (1 - LD)
print(f"TAM (ky vong trong so) truoc CK {cpre:,.0f} | CK thanh khoan {LD:.2%} (5 ty, Y=1) | sau {cpre*(1-LD):,.0f} | gia/tam {PX/(cpre*(1-LD))-1:+.1%}")
# LUOI: m {30,33.5,36} x s_old {25,40,55} x hold {10,20,30} x r {R-1%,R,R+1%}; trong so 1/4,1/2,1/4 moi bien (doi xung)
wv = (0.25, 0.5, 0.25); vals, ws = [], []
for (m, wm), (s, wsv), (h, wh), (rr, wr) in itertools.product(zip((0.30, 0.335, 0.36), wv), zip((0.25, 0.40, 0.55), wv), zip((0.30, 0.20, 0.10), wv), zip((R - 0.01, R, R + 0.01), wv)):
    vals.append(nav(m, s, h, rr)); ws.append(wm * wsv * wh * wr)
qp = L.wq(vals, ws); qq = {k: v * (1 - LD) for k, v in qp.items()}
out.update(grid_pre=qp, grid_post=qq, grid_n=len(vals))
print(f"LUOI n={len(vals)} (m x s_old x hold x r±100bp, trong so 1/4-1/2-1/4 moi bien): truoc {', '.join(f'{k} {v:,.0f}' for k,v in qp.items())} | sau {', '.join(f'{k} {v:,.0f}' for k,v in qq.items())}")
lab = L.label(PX, qq['P10'], qq['P90']); out['label'] = lab
print(f"Gia {PX:,.0f}: vs tam {PX/out['center_post']-1:+.1%}, vs P10 {PX/qq['P10']-1:+.1%}, vs P90 {PX/qq['P90']-1:+.1%} => {lab}")
# do nhay lai huy dong (tam truoc CK)
sens = {}
for b in (0.5, 1.0):
    for d in (-0.01, -0.005, 0.005, 0.01):
        rr = L.r_of(dep + d, b); c = sum(SC[k]['p'] * nav(SC[k]['m'], SC[k]['s_old'], SC[k]['hold'], rr) for k in SC)
        sens[f"b{b}_d{int(d*1e4)}bp"] = dict(r=rr, center_pre=c, d_vnd=c - cpre, d_pct=c / cpre - 1)
out['sens_dep'] = sens
print("Do nhay lai huy dong (tam truoc CK): " + "; ".join(f"{k}: r {v['r']:.2%} -> {v['center_pre']:,.0f} ({v['d_vnd']:+,.0f} d, {v['d_pct']:+.1%})" for k, v in sens.items()))
g = {f"gov{int(x*100)}": sum(SC[k]['p'] * nav(SC[k]['m'], SC[k]['s_old'], SC[k]['hold'], gov=x) for k in SC) * (1 - LD) for k_ in [0] for x in (0.05, 0.10, 0.15)}
nl = {f"s_new{int(x*100)}": sum(SC[k]['p'] * nav(SC[k]['m'], SC[k]['s_old'], SC[k]['hold'], s_new=x) for k in SC) * (1 - LD) for x in (-0.10, 0.10, 0.25)}
out['sens_gov_post'] = g; out['sens_newland_post'] = nl
print("Do nhay CK quan tri (WARNING, KHONG trong base), tam sau CK: " + ", ".join(f"{k} {v:,.0f}" for k, v in g.items()))
print("Do nhay thang du quy dat moi (base 0): " + ", ".join(f"{k} {v:,.0f}" for k, v in nl.items()))
print(f"Thanh khoan: ADV trung vi {LQ['adv_med_vnd']/1e9:.1f} ty/phien ({LQ['window']}), sigma {LQ['sigma_d']:.2%}; CK 1/5/10 ty = " +
      "/".join(f"{LQ['pos'][q]['disc_Y1']:.1%}" for q in ('1','5','10')) + f"; 5 ty can {LQ['pos']['5']['days_at20']:.1f}-{LQ['pos']['5']['days_at10']:.1f} phien @20-10%")
json.dump(out, open(os.path.join(HERE, 'model_out.json'), 'w'), indent=1, default=float)
