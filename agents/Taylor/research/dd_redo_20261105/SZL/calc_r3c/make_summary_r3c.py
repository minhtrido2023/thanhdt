"""SZL r3c: SUMMARY.json tu model_r3c_out.json + SUMMARY_r3b.json (backup r3b). Chay: $DNA_PYEXE -I make_summary_r3c.py"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); TK = os.path.dirname(HERE)
M = json.load(open(os.path.join(HERE, 'model_r3c_out.json'))); A = json.load(open(os.path.join(HERE, 'assumptions_r3c.json')))
old = json.load(open(os.path.join(TK, 'SUMMARY_r3b.json')))
S, S40, H, H40, P, PX = M['grid_ref5'], M['grid_sleeve40'], M['hold_ref5'], M['hold_sleeve40'], M['parallel'], M['price']
R = lambda x: int(round(x))  # noqa: E731
lab = lambda s: 'DUOI' if PX < s['p10_post'] else ('TREN' if PX > s['p90_post'] else 'TRONG')  # noqa: E731
T = M['label_thresholds']; st = M['stake']


def brief(name, s, s40, d):
    return dict(variant=name, center=R(s['center_post']), p10=R(s['p10_post']), p50=R(s['p50_post']), p90=R(s['p90_post']), pct_w_below_px=round(s['pct_w_below_px'], 4),
                label_5bn=lab(s), center_sleeve40=R(s40['center_post']), p10_sleeve40=R(s40['p10_post']), p90_sleeve40=R(s40['p90_post']),
                pct_w_below_px_sleeve40=round(s40['pct_w_below_px'], 4), label_sleeve40=lab(s40), delta_center=R(d))


def blk(s, disc):
    return dict(center=s['center_post'], p10=s['p10_post'], p50=s['p50_post'], p90=s['p90_post'], pct_w_below_px=s['pct_w_below_px'], label=lab(s), disc=disc)


out = dict(old)
out.update(dict(
    round='r3c', job='Taylor_20261108_180625', asof_price_date=M['asof_price'], price=PX, r=M['r'],
    center_pre_liq=S['center_pre'], center_post_liq=S['center_post'], p10_post=S['p10_post'], p50_post=S['p50_post'], p90_post=S['p90_post'],
    p10_pre=S['p10_pre'], p50_pre=S['p50_pre'], p90_pre=S['p90_pre'], p10_out=S['p10_post'], p50_out=S['p50_post'], p90_out=S['p90_post'],
    pct_weight_below_price=S['pct_w_below_px'], n_outcomes=S['n'], grid_n=S['n'], min_outcome_post=S['min_post'], liq_discount_ref=M['d_ref'],
    sleeve40=blk(S40, M['d_40']),
    hold_frame=dict(ref5=blk(H, M['d_ref']), sleeve40=blk(H40, M['d_40']), note="bien the song song khung GIU-NHAN-CO-TUC (khong thue lai von; co tuc giua DN mien TNDN — CHUA TRA dieu luat; KTPL tren PV co tuc ~ thi gia 54,5 ty)"),
    label=f"{M['label']} vung", label_sleeve40=M['label_sleeve40'], label_actionable=M['label_sleeve40'],
    label_note=("Nhan HANH DONG = co sleeve 40 tr (CK 0,37%, Q/ADV250 8,7%): TRONG (gia 27.700 duoi P90 28.793 3,8%; 76,2% trong so duoi gia). "
                "Co 5 ty (tham chieu, Q/ADV250 1.084% ngoai vung hieu chinh): TRONG SAT CANH — P90 27.710 chi tren gia 10 d (0,04%); khung GIU P90 27.786. "
                "Nguong N0 de 5 ty sang TREN = 131,0 vs base 131,08 => nhan 5 ty coi nhu ranh gioi. Doi so r3b: 5 ty TREN->TRONG, 40 tr TRONG (sat canh tren -1,5%) -> TRONG (-3,8%), do sua loi khung KTPL co phan (+635)."),
    px_vs_center=PX / S['center_post'] - 1, px_vs_p10=PX / S['p10_post'] - 1, px_vs_p90=PX / S['p90_post'] - 1,
    center_r3b=old['center_post_liq'], center_change_vs_r3b=S['center_post'] / old['center_post_liq'] - 1,
    center_change_vs_r3=S['center_post'] / old['center_r3'] - 1,
    center_change_vs_r2=S['center_post'] / old['center_r2'] - 1 if old.get('center_r2') else None,
    grid_desc=(old['grid_desc'] + " SUA r3c: co phan SZC/SZB khung BAN = thi gia - thue lai von 20% - KTPL x lai von sau thue (von goc 284,8 khong bi trich); r3b tron khung (KTPL ca tren von goc) da bo."),
    base_adjustments=[a for a in (old.get('base_adjustments') or []) if not (isinstance(a, str) and a.startswith('r3b B'))] +
                     ["r3c B (sua): KTPL 11,2% tren LAI VON SAU THUE co phan SZC/SZB (161,3 ty => 18,1 ty) o khung BAN; tong tru co phan 58,4 ty (r3b 90,3 SAI); khung GIU (54,5) la bien the song song; B 50% la do nhay"],
    stake_frames=dict(mkt_ty=st['mkt_total_ty'], book_ty=st['book_ty'], gain_ty=st['gain_ty'], tax_ty=st['tax_ty'], ktpl_sell_ty=st['ktpl_sell_ty'], ktpl_hold_ty=st['ktpl_hold_ty'],
                      total_deduction_ty=st['total_deduction_ty'], net_ty=st['net_ty']),
    assumptions=[dict(name=k, value=v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk != 'basis'}, basis=v.get('basis') if isinstance(v, dict) else 'xem assumptions_r3c.json')
                 for k, v in A.items() if k not in ('round', 'job')] + [a for a in old['assumptions'] if a['name'] not in ('ktpl_on_stake_income', 'ktpl_on_unlisted', 'asof_price', 'price_file', 'inherits', 'label_rule')],
    headline_vs_alternatives=[brief('HEADLINE r3c (A + B khung BAN)', S, S40, 0.0)] + [brief(k, v['ref5'], v['sleeve40'], v['delta_center']) for k, v in P.items()],
    implied_by_price=dict(M['implied_by_price'], note=("Moi bien don le de tam sau CK 5 ty = 27.700: N0 153,4 ty (KTPL 11,2%) hoac 131,5 khi KTPL 0%; hoac KTPL ~0% (-0,3%); hoac r 11,34%; hoac dong tien them +17,6 ty/nam.")),
    label_thresholds=T,
    bridge_r3b_to_r3c=[{k: (R(v) if isinstance(v, float) and abs(v) > 1 else v) for k, v in b.items()} for b in M['bridge_r3b_to_r3c']],
    skeptic_check_r3c=dict(skeptic_ranges=dict(center_5bn='25.165-25.241', p90_5bn='27.710-27.786', center_40='26.148-26.228', p90_40='28.793-28.872', pct_below='~76%'),
                           calc_sell=dict(center_5bn=R(S['center_post']), p90_5bn=R(S['p90_post']), center_40=R(S40['center_post']), p90_40=R(S40['p90_post']), pct_below_40=round(S40['pct_w_below_px'], 4)),
                           calc_hold=dict(center_5bn=R(H['center_post']), p90_5bn=R(H['p90_post']), center_40=R(H40['center_post']), p90_40=R(H40['p90_post']), pct_below_40=round(H40['pct_w_below_px'], 4)),
                           note="BAN = can duoi, GIU = can tren cua moi khoang skeptic — trung tung so."),
    errata_r3b=["REPORT_r3b.md:41 do nhay 'B ca co phan chua niem yet' (-253) KHONG co co so: phan nay ghi theo so sach, khong lai von => KTPL 0; da bo o r3c",
                "REPORT_r3b.md:90 + ADDENDUM_5F_SYNC_r3b.md:3 + SUMMARY_5F_SYNC_r3b.json: 'md5 nam trong LOCK cua DDV/PVT/NT2(/PVP)' SAI — md5 ADDENDUM_5F.md (83131c3e) va SUMMARY_5F.json (af090936) khong nam trong LOCK nao (grep -rl moi LOCK*) => r3c SUA TAI CHO ADDENDUM_5F.md:1 va SUMMARY_5F.json:32",
                "REPORT_r3b.md:91 REPORT_r3.md (b53be177) chi nam trong LOCK cua chinh SZL (SZL/calc_r3/LOCK_md5.txt:20), khong phai 'nhieu ma'",
                "model_r3b.py:76 (MKT-TAX)x(1-k) tron khung BAN/GIU => tru 90,3 ty thay vi 54,5-58,4; bi quan 663 d/cp (BAN) / 743 (GIU) truoc CK"],
    warnings=old.get('warnings') or [],
    sources=dict(old.get('sources') or {}, r3c_model='calc_r3c/model_r3c.py', r3c_out='calc_r3c/model_r3c_out.txt (md5 6a4cc7cd)', r3c_lock='calc_r3c/LOCK_r3c_prerun.txt (ghi 2026-11-09T01:09:21+07:00 truoc khi chay)', r3c_report='REPORT_r3c.md', r3b_backup='SUMMARY_r3b.json'),
))
json.dump(out, open(os.path.join(TK, 'SUMMARY.json'), 'w'), indent=1, ensure_ascii=False, sort_keys=False)
print('SUMMARY.json r3c: tam', R(S['center_post']), 'P10/P90', R(S['p10_post']), R(S['p90_post']), M['label'], '| 40tr', R(S40['center_post']), R(S40['p10_post']), R(S40['p90_post']), M['label_sleeve40'])
