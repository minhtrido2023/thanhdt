"""SZL r3: SUMMARY.json tu model_r3_out.json (+ giu truong cu cua SUMMARY_r2.json). Chay: $DNA_PYEXE -I make_summary_r3.py"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); TK = os.path.dirname(HERE)
M = json.load(open(os.path.join(HERE, 'model_r3_out.json'))); A = json.load(open(os.path.join(HERE, 'assumptions_r3.json')))
old = json.load(open(os.path.join(TK, 'SUMMARY_r2.json')))
S, S40, P, PX = M['grid'], M['grid_sleeve40'], M['parallel'], M['price']
R = lambda x: int(round(x))  # noqa: E731
LQ = M['liq']


def brief(name):
    s = P[name]['ref5']; s40 = P[name]['sleeve40']
    lab = 'DUOI' if PX < s['p10_post'] else ('TREN' if PX > s['p90_post'] else 'TRONG')
    lab40 = 'DUOI' if PX < s40['p10_post'] else ('TREN' if PX > s40['p90_post'] else 'TRONG')
    return dict(variant=name, center=R(s['center_post']), p10=R(s['p10_post']), p50=R(s['p50_post']), p90=R(s['p90_post']),
                pct_w_below_px=round(s['pct_w_below_px'], 4), label_5bn=lab, label_sleeve40=lab40, p10_sleeve40=R(s40['p10_post']), delta_center=R(P[name]['delta_center']))


out = dict(old)
out.update(dict(
    round='r3', job='Taylor_20261108_164337', asof_price_date=M['asof_price'], price=PX, r=M['r'],
    center_pre_liq=S['center_pre'], center_post_liq=S['center_post'],
    p10_post=S['p10_post'], p50_post=S['p50_post'], p90_post=S['p90_post'], p10_pre=S['p10_pre'], p50_pre=S['p50_pre'], p90_pre=S['p90_pre'],
    p10_out=S['p10_post'], p50_out=S['p50_post'], p90_out=S['p90_post'], pct_weight_below_price=S['pct_w_below_px'], n_outcomes=S['n'], min_outcome_post=S['min_post'],
    liq_discount_ref=M['d_ref'], liq_ref_position_bn_vnd=5, adv_med_bn_vnd=LQ['adv250']['adv_bn'], adv60_med_bn_vnd=LQ['adv60']['adv_bn'],
    ck_ref_size=dict(q_bn=5, adv250=LQ['adv250']['sizes']['5'], adv60=LQ['adv60']['sizes']['5']),
    ck_real_sleeve={k: dict(adv250=LQ['adv250']['sizes'][k], adv60=LQ['adv60']['sizes'][k]) for k in ('0.01', '0.02', '0.04')},
    sleeve40=dict(center=S40['center_post'], p10=S40['p10_post'], p50=S40['p50_post'], p90=S40['p90_post'], pct_w_below_px=S40['pct_w_below_px'], label=M['label_sleeve40']),
    label=f"{M['label']} vung", label_sleeve40=M['label_sleeve40'],
    label_note=("Nhan theo co 5 ty/ADV250 (CK 4,12%; Q/ADV 1.084% NGOAI vung hieu chinh). DUOI -> TRONG so r2 do sua loi KTPL (khong do doi dinh nghia vung, van P10-P90). "
                "MONG MANH o co sleeve 40 tr: KTPL <= 8%, chi vinh vien, N0 = Q3x4, BDS dau tu moi theo gia von, ky quy PV hoac capex duy tri 0,5x KH deu cho DUOI; holdco >= 10%, RONIC=Ke, N0 2025 deu giu TRONG."),
    px_vs_center=PX / S['center_post'] - 1, px_vs_p10=PX / S['p10_post'] - 1, px_vs_p90=PX / S['p90_post'] - 1,
    center_change_vs_r2=S['center_post'] / old['center_post_liq'] - 1, center_r2=old['center_post_liq'],
    grid_n=S['n'],
    grid_desc=("5 truc, n=270 ket cuc tat dinh (giong r2): LN loi N0 131,1 {-12;-6;0;+6;+12}% (0,1/0,2/0,4/0,2/0,1) [UL] x g {2;3;4}% x r {12,5;13,5;14,5}% x LN phi tien mat {20;10;0}% [UL] (1/4-1/2-1/4) "
               "x thoi han {27 nam (2053); vinh vien} (3/4-1/4) [UL]. MOI r3: dong tien = N0 x (1 - nc - 11,2% KTPL); tru so du quy KTPL 23,96. Co dinh: SZC/SZB thi gia 06/11 - thue 20% lai von; chua niem yet so sach; "
               "XDCB 407,0 gia von (NPV 0); no rong 205,5; ky quy 157,4 + trich thue dat 44,3. Phan vi wpct; tam = ky vong luoi; CK 5 ty ADV250 ap dong loat."),
    narrow_band_note="Vung P10-P90 hep (~22% tam) do CAU TRUC mo hinh: ~1/3 gia tri co dinh khong bien dong (co phan SZC/SZB theo gia 1 ngay, XDCB 8.445 d/cp, no) — khong phai do it bat dinh. Truc lon nhat ngoai luoi: capex duy tri (+/-45 ty/nam => +/-8.100 d).",
    assumptions=[dict(name=k, value=v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk != 'basis'}, basis=v.get('basis') if isinstance(v, dict) else None) for k, v in A.items()],
    headline_vs_alternatives=[dict(variant='HEADLINE r3', center=R(S['center_post']), p10=R(S['p10_post']), p50=R(S['p50_post']), p90=R(S['p90_post']), pct_w_below_px=round(S['pct_w_below_px'], 4),
                                   label_5bn=M['label'], label_sleeve40=M['label_sleeve40'], p10_sleeve40=R(S40['p10_post']), delta_center=0)] + [brief(k) for k in P],
    implied_by_price=dict(M['implied_by_price'], note="Moi bien don le de tam sau CK 5 ty = 27.700: N0 120,1 ty (base KTPL) tuc 105,1 truoc KTPL (2025 nam hoa 115,3); hoac KTPL 17,8%; hoac holdco 17,5%; hoac r 14,60%"),
    bridge_r2_to_r3=[dict(b, center_post=R(b['center_post']), delta=None if b['delta'] is None else R(b['delta']), p10=R(b['p10']), p90=R(b['p90']),
                          reason={0: 'control: tai lap r2 trung tung dong (32.391; 28.966/32.162/36.075)', 1: 'gia SZC 20.550->20.350, SZB 45.600->46.500 (dong cua 06/11)',
                                  2: 'cua so ADV/sigma den 06/11: CK 5 ty 4,16% -> 4,12%', 3: 'skeptic #1: so du quy KTPL ma 323 la no phai tra nguoi lao dong, r2 bo sot',
                                  4: 'skeptic #1: KTPL 11,2% LNST (TM18 15,778/140,687) — ap tren N0 ke toan (skeptic ap tren phan tien mat => -2.383; ban nay -2.649, xem corrections_check)'}[i])
                     for i, b in enumerate(M['bridge_r2_to_r3'])],
    corrections_check=[
        dict(n=1, verdict='DUNG (sua so)', note='TM18 tr.23: trich 15,778; ma 420b dau nam 140,687 => 11,2%; so du 23,96 (ma 323) — da kiem tren anh trang. Skeptic ap 11,2% tren dong tien N0x(1-nc) => -2.383; KTPL trich tren LNST KE TOAN (gom phan phi tien mat) nen dung la N0x11,2% => -2.649. Tam 29.257 (skeptic 29.510; chenh -253 = do diem nay). Quy KTPL 5%: TRONG (5 ty)/DUOI (40 tr); 8%: TRONG/DUOI — khop skeptic o 5 ty. NQ DHDCD 2026 chua tra duoc (khong co trong thu muc), giu 11,2% = 1 nam quan sat.'),
        dict(n=2, verdict='DUNG (do nhay, khong vao base)', note='Khong co doanh thu tach theo KCN (BCTC scan, khong co bo phan) => khong tach dong ho duoc trong base; 1/2-1/2: +380 (skeptic +385), 40 tr P10 27.279 TRONG.'),
        dict(n=3, verdict='DUNG (do nhay)', note='SNZ P/B 0,66 vs SZC 1,20 / SZB 1,78 / SZL 1,70 (BQ 06/11) chung to holdco discount ton tai o SNZ nhung khong anh xa duoc sang co phan 10,08%/8,4% cua SZL. Holdco 25%: 27.039 (skeptic KTPL+holdco 25% ~28.052; o day KTPL 5%+holdco 25% = 28.507, KTPL 11,2%+holdco 25% = 27.039). Ghi vung hep do cau truc.'),
        dict(n=4, verdict='DUNG (do nhay hai chieu)', note='Do lai BQ 2019Q1-2026Q3: LNST 886,7, CF_OA 1.371,1, CF_Invest -1.703,9 (khop skeptic). LCTT 9T/26: KH 67,5 (=> 90/nam), capex 309,4 (chu yeu XDCB/BDS dau tu mo rong). Khong tach duoc capex duy tri tu BCTC => [UL] 0,5x/1,5x KH: 37.366 / 21.148 — truc rong nhat, khong vao base. Bien the RONIC=Ke (tang truong phai tai dau tu): 25.524 TRONG.'),
        dict(n=5, verdict='DUNG (do nhay chieu len)', note='BDS dau tu nguyen gia +166,9 (ma 241: 1.011,9 -> 1.178,8; skeptic 166,2): 32.577; N0 Q3x4 138,5: 30.310; ky quy DH PV den 2053: 32.084 (+2.827).'),
        dict(n=6, verdict='DONG Y', note='N0 131,1 giu.'),
        dict(n=7, verdict='DUNG', note='Gia 27.700 (06/11) xac nhan BQ. 40 tr: P10 27.234 TRONG (skeptic 27.514 voi KTPL tren dong tien); +diem 2: P10 27.279 TRONG (skeptic 27.745 DUOI) — chenh do cach ap KTPL. Co phieu quy: 48,961 tr phat hanh (von gop 291,1 + von khac 198,5 co tuc CP 70%) - 0,7625 tr quy = 48,199 tr = SH dung. Phap ly SNZ/Dong Nai sau 05/11 chua tra lai.')],
    ronic_note=("Base giu cau truc Gordon r2 (g khong tru tai dau tu): skeptic TOP5C khong neu RONIC cho SZL; tien le SAS r3 (NARROW). Quy tac chung TOP5C dong 2 (NARROW => RONIC=Ke) cho 25.524 TRONG (P10 23.296 / P90 28.070). "
                "Moat SZL = NARROW LOCATION, moat_durable=false (SUMMARY_5F.json). MIKE/USER CHON — neu ap RONIC=Ke vao headline thi tam 25.524, nhan van TRONG."),
    axes_included=["LN loi +-12%", "g 2/3/4%", "r +-100bp", "LN phi tien mat 0/10/20%", "thoi han 27 nam/vinh vien"],
    axes_excluded=[dict(axis="holdco discount SZC/SZB", reason="SNZ P/B 0,66 la bang chung dinh tinh, khong anh xa duoc; do nhay 10/25%"),
                   dict(axis="KTPL 5/8/11,2%", reason="11,2% la du lieu 1 nam (base); 5/8% do nhay"),
                   dict(axis="capex duy tri vs khau hao", reason="BCTC khong tach; do nhay hai chieu 0,5x/1,5x"),
                   dict(axis="RONIC=Ke", reason="quy uoc chua chot cho SZL; bao song song"),
                   dict(axis="BDS dau tu moi, ky quy PV, N0 Q3x4", reason="chieu len khong co du lieu xac nhan LN chua vao N0; do nhay (doi xung voi holdco/capex chieu xuong)"),
                   dict(axis="thanh tra SNZ lan sang SZL", reason="chua co quyet dinh neu ten SZL; WARNING")],
    base_adjustments=[dict(item="trich quy KTPL 11,2% LN loi (MOI r3)", effect_dong_per_share=M['bridge_r2_to_r3'][4]['delta'], basis="TM18 trich 15,778 / LNST 2025 140,687", source="src/Q3_2026_hopnhat.pdf tr.23 + tr.4 (PDF trang 27, 7)"),
                      dict(item="tru so du quy KTPL 23,96 (MOI r3)", effect_dong_per_share=M['bridge_r2_to_r3'][3]['delta'], basis="BS ma 323 / TM18", source="src/Q3_2026_hopnhat.pdf tr.3, 23")] + old.get('base_adjustments', []),
    center_vs_p50_note=f"tam (ky vong luoi) {R(S['center_post']):,} > P50 {R(S['p50_post']):,}; gia tri tai tham so trung tam (tron 3/4-1/4, truoc CK) {R(M['center_param_pre']['mix']):,}. Nhanh vinh vien (0,25) keo P90; khong nhanh trong so nho nao quyet dinh P10.",
    change_reason="r3: -2.649 KTPL hang nam, -477 so du quy KTPL, -22 gia SZC/SZB, +13 CK => 32.391 -> 29.257 (-9,7%); nhan DUOI -> TRONG.",
    sources=dict(model='calc_r3/model_r3.py -> calc_r3/model_r3_out.json/.txt (run1/run2 trung byte)', lock='calc_r3/LOCK_md5.txt', assumptions='calc_r3/assumptions_r3.json',
                 corrections='../TOP5C_CORRECTIONS_20261108.md muc SZL', pct='_shared/wpct.py', price='calc_r3/px_szl_r3_20261106.csv (BQ tav2_bq.ticker)')))
for k in ('center_change_vs_r1', 'center_change_vs_old'):
    out.pop(k, None)
json.dump(out, open(os.path.join(TK, 'SUMMARY.json'), 'w'), indent=1, ensure_ascii=False, default=float)
print(f"SUMMARY r3: tam {out['center_post_liq']:,.0f} P10/50/90 {out['p10_out']:,.0f}/{out['p50_out']:,.0f}/{out['p90_out']:,.0f} {out['label']} | vs r2 {out['center_change_vs_r2']:+.1%}")
