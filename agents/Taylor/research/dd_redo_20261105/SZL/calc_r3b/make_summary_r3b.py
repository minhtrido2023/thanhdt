"""SZL r3b: SUMMARY.json tu model_r3b_out.json + SUMMARY_r3.json (backup r3). Chay: $DNA_PYEXE -I make_summary_r3b.py"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); TK = os.path.dirname(HERE)
M = json.load(open(os.path.join(HERE, 'model_r3b_out.json'))); A = json.load(open(os.path.join(HERE, 'assumptions_r3b.json')))
old = json.load(open(os.path.join(TK, 'SUMMARY_r3.json')))
S, S40, P, PX = M['grid_ref5'], M['grid_sleeve40'], M['parallel'], M['price']
R = lambda x: int(round(x))  # noqa: E731
lab = lambda s: 'DUOI' if PX < s['p10_post'] else ('TREN' if PX > s['p90_post'] else 'TRONG')  # noqa: E731


def brief(name, s, s40, d):
    return dict(variant=name, center=R(s['center_post']), p10=R(s['p10_post']), p50=R(s['p50_post']), p90=R(s['p90_post']), pct_w_below_px=round(s['pct_w_below_px'], 4),
                label_5bn=lab(s), center_sleeve40=R(s40['center_post']), p10_sleeve40=R(s40['p10_post']), p90_sleeve40=R(s40['p90_post']), label_sleeve40=lab(s40), delta_center=R(d))


out = dict(old)
out.update(dict(
    round='r3b', job='Taylor_20261108_175123', asof_price_date=M['asof_price'], price=PX, r=M['r'],
    center_pre_liq=S['center_pre'], center_post_liq=S['center_post'], p10_post=S['p10_post'], p50_post=S['p50_post'], p90_post=S['p90_post'],
    p10_pre=S['p10_pre'], p50_pre=S['p50_pre'], p90_pre=S['p90_pre'], p10_out=S['p10_post'], p50_out=S['p50_post'], p90_out=S['p90_post'],
    pct_weight_below_price=S['pct_w_below_px'], n_outcomes=S['n'], grid_n=S['n'], min_outcome_post=S['min_post'], liq_discount_ref=M['d_ref'],
    sleeve40=dict(center=S40['center_post'], p10=S40['p10_post'], p50=S40['p50_post'], p90=S40['p90_post'], pct_w_below_px=S40['pct_w_below_px'], label=M['label_sleeve40'], disc=M['d_40']),
    label=f"{M['label']} vung", label_sleeve40=M['label_sleeve40'], label_actionable=M['label_sleeve40'],
    label_note=("Nhan CO THE HANH DONG = co sleeve 40 tr (CK 0,37%, Q/ADV250 8,7% — trong vung hieu chinh): TRONG nhung sat canh tren (gia 27.700 duoi P90 28.133 1,5%; 87,2% trong so ket cuc duoi gia). "
                "Co 5 ty (CK 4,12%) chi la THAM CHIEU: Q/ADV250 1.084% NGOAI vung hieu chinh sqrt-impact => TREN vung (gia tren P90 27.074 2,3%). "
                "Thay doi so r3 (TRONG/TRONG) do 2 de nghi skeptic cuoi user duyet 09/11: A RONIC=Ke (-3.733), B KTPL tren co phan SZC/SZB (-995)."),
    px_vs_center=PX / S['center_post'] - 1, px_vs_p10=PX / S['p10_post'] - 1, px_vs_p90=PX / S['p90_post'] - 1,
    center_r3=old['center_post_liq'], center_change_vs_r3=S['center_post'] / old['center_post_liq'] - 1,
    center_r2=old.get('center_r2'), center_change_vs_r2=S['center_post'] / old['center_r2'] - 1 if old.get('center_r2') else None,
    grid_desc=(old['grid_desc'] + " MOI r3b: RONIC=Ke (vinh vien cf/r; 27 nam annuity khong tang truong) => truc g khong con tac dung (giu trong so, gia tri trung); "
               "co phan SZC/SZB rong (mkt - thue lai von) x (1 - 11,2% KTPL)."),
    base_adjustments=(old.get('base_adjustments') or []) + ["r3b A: RONIC = Ke o base (user duyet 09/11)", "r3b B: KTPL 11,2% tru tren gia tri co phan SZC/SZB 446,1 ty (100%; 50% la do nhay)"],
    ronic_note="r3b: RONIC=Ke la BASE (user duyet 09/11/2026). Nhanh huu han dung annuity khong tang truong (khong nhan (1-g/r); cong thuc da sua o ADDENDUM_5F r3).",
    assumptions=[dict(name=k, value=v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk != 'basis'}, basis=v.get('basis') if isinstance(v, dict) else 'xem assumptions_r3b.json')
                 for k, v in A.items() if k not in ('round', 'job')] + [a for a in old['assumptions'] if a['name'] not in ('ronic', 'asof_price', 'price_file')],
    headline_vs_alternatives=[brief('HEADLINE r3b (A+B)', S, S40, 0.0)] + [brief(k, v['ref5'], v['sleeve40'], v['delta_center']) for k, v in P.items()],
    implied_by_price=dict(M['implied_by_price'], note=("Moi bien don le de tam sau CK 5 ty = 27.700: N0 159,0 ty (KTPL 11,2%; Q3x4 chi 138,5; 2025 115,3) hoac 131,5 khi KTPL 0%; "
                                                       "hoac KTPL ~0% (-0,2%); hoac r 10,89%; hoac dong tien them +22,0 ty/nam. P90 = gia khi N0 135,8 (5 ty) / 127,9 (40 tr) => nhan 40 tr doi sang TREN neu N0 < 127,9 (base 131,1).")),
    bridge_r3_to_r3b=[{k: (R(v) if isinstance(v, float) else v) for k, v in b.items()} for b in M['bridge_r3_to_r3b']],
    skeptic_check=dict(
        A=dict(skeptic=-3733, calc=R(M['bridge_r3_to_r3b'][1]['delta']), note='khop'),
        B=dict(skeptic='-624..-1.248 (co so 559 ty)', calc=R(M['bridge_r3_to_r3b'][2]['delta']),
               note=("559 ty cua skeptic = co phan SZC/SZB rong 446,1 + chua niem yet 113,25 theo so sach. Base r3b ap B chi tren SZC/SZB (dung chu dispatch) => -995; "
                     "ap ca chua niem yet => -1.248 (tam 24.276, P90 26.822 — trung so skeptic). Ca hai cach nhan khong doi: 5 ty TREN, 40 tr TRONG (P90 28.133 / 27.870).")),
        combined=dict(skeptic='24.276-24.900', calc=R(S['center_post']), p90_5bn=R(S['p90_post']), p90_40=R(S40['p90_post']))),
    skeptic_28052_recon=dict(r3_reported=28507, recon={k: R(v) for k, v in M['skeptic_recon'].items()},
                             note=("Chenh 455 tai lap duoc (+10): skeptic (i) ap holdco 25% CA co phan chua niem yet 113,25 ty (-564) va (ii) tru KTPL 5% tren N0x(1-nc) thay vi N0 (+118). "
                                   "Ca hai quy uoc khac r3 chu khong phai loi so; r3 dung KTPL tren N0 (LNST ke toan) va holdco chi tren co phan niem yet.")),
    holdco_snz=dict(pb=dict(SNZ=0.658, SZC=1.200, SZB=1.780, SZL=1.703), implied=M['hold_snz_implied'],
                    note="1 - PB_SNZ/PB_SZC = 45% la CAN TREN THO (SNZ giu ca tai san khac); chi do nhay: tam 20.970 TREN o ca 2 co"),
    narrow_band_note=old.get('narrow_band_note', '') + " r3b: vung con hep hon (P10-P90 ~19% tam) vi RONIC=Ke lam truc g vo hieu.",
    warnings=(old.get('warnings') or []) + ["Phap ly SNZ/Dong Nai: chi WARNING, khong vao base (chua tra lai sau 05/11)."],
    sources=dict(old.get('sources') or {}, r3b_model='calc_r3b/model_r3b.py', r3b_out='calc_r3b/model_r3b_out.txt (md5 47373344)', r3b_lock='calc_r3b/LOCK_r3b_prerun.txt (ghi 2026-11-09T00:53:59+07:00 truoc khi chay)', r3b_report='REPORT_r3b.md'),
))
json.dump(out, open(os.path.join(TK, 'SUMMARY.json'), 'w'), indent=1, ensure_ascii=False, sort_keys=False)
print('SUMMARY.json r3b: tam', R(S['center_post']), 'P10/P90', R(S['p10_post']), R(S['p90_post']), M['label'], '| 40tr', R(S40['center_post']), R(S40['p10_post']), R(S40['p90_post']), M['label_sleeve40'])
