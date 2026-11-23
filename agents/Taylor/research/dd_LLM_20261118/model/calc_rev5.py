# LLM DD rev5 — MU GIA (khong doc gia). Dau vao: model_rev5_inputs.json. threads=1 (thuan python).
import json, os, math
H = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(H, 'model_rev5_inputs.json')))
S = M['shares_m']; r0 = M['r_ke']; B = M['bs_q3_bn']; W = M['warranty']; w = M['weights']; L = M['liquidity_discount']
nc = B['cash_TM3'] + B['htm_st_net_TM4'] + B['htm_lt_TM4'] - B['borrow_st'] - B['borrow_lt']
nwc = sum(B['op_assets'].values()) - sum(B['op_liabs'].values()); nfp = nc + nwc
wb = W['close_st'] + W['close_lt']
WF = M['welfare']; wf_stock = WF['pct_npat'] * WF['npat_parent_9m26_unappropriated']
y_cash_at = M['cash_yield']['gross_yield_used'] * 0.8          # lai tien gui sau thue 20%
y_inv = M['lt_invest_yield']['yield_used']                     # co tuc nhan, khong chiu thue
P0 = M['unlock_hazard']['p_base']; NCI = M['nci']['share_of_npat']
T_def = W['addback_deferral']['T_years']
REV4_F = M['trapped']['_superseded_rev4']

def fcash(p, r): return (y_cash_at + p) / (r + p)
def finv(p, r): return (y_inv + p) / (r + p)

def val(k, r=r0, p=P0, cs=None, rev=None, gpm=None, a=None, nci=NCI, defer=True, inv_trap=True,
        extra=0.0, hamon=None, ctrl=False, retain_trap=None, fover=None):
    """Gia tri kich ban k (d/cp, truoc chiet khau thanh khoan).
    ctrl=True: tai lap dung cong thuc rev4 (control leg)."""
    c = W['cash_share'][k] if cs is None else cs
    addw = wb * (1 - c) * (1 - W['tax_on_reversal'])
    hm = (M['hamon']['after_tax_if_recognised'] if k == 'good' else 0) if hamon is None else hamon
    imp = M['bad_impairment'] if k == 'bad' else 0
    wfs = wf_stock if k != 'bad' else 0
    if k == 'bad':
        core = M['nopat_bad']; ab = 0.0
    else:
        R = rev if rev is not None else (M['rev_base'] if k == 'base' else M['rev_good'])
        g = gpm if gpm is not None else M['gpm'][k]
        aa = W['flow_noncash_addback_pct_rev'][k] if a is None else a
        core = 0.8 * (R * g - M['opex_ga'][k]); ab = 0.8 * aa * R
    if ctrl:   # rev4 nguyen ban
        n = core + ab; n = n * (1 - WF['pct_npat']) if n > 0 else n
        v = n / r + (nfp + addw - wfs) * REV4_F[k] - imp + M['lt_fin_invest_book'] + M['hna_after_tax'] + hm - extra
        return v / S * 1000
    fc = fcash(p, r) if fover is None else fover; fi = finv(p, r) if inv_trap else 1.0
    adj = (1 - WF['pct_npat']) * (1 - nci)
    core_n = core * adj if core > 0 else core * (1 - nci)
    ab_n = ab * adj
    op = core_n / r + (ab_n / r) * ((1 + r) ** (-T_def) if defer else 1.0)
    if retain_trap is not None and op > 0:   # do nhay: phan LN giu lai cung bi ket nhu tien ton
        op = op * (retain_trap + (1 - retain_trap) * fc)
    pile = (nfp + addw - wfs - imp + hm - extra) * fc   # khoan tru (ngoai tru/CPH/bao lanh) ra tu khoi tien => cung he so f
    nonop = (M['lt_fin_invest_book'] + M['hna_after_tax']) * fi
    return (op + pile + nonop) / S * 1000

def ctr(LL=L, ww=None, **kw):
    ww = ww or w; return sum(ww[k] * val(k, **kw) for k in ww) * (1 - LL)

if __name__ == '__main__':
    C4 = ctr(ctrl=True)
    print(f'CONTROL rev4 tai lap: {C4:.0f} (ky vong 32376) -> {"OK" if round(C4)==32376 else "LECH"}')
    print(f'NFP={nfp:.2f}; y_cash_sau_thue={y_cash_at:.4%}; y_inv={y_inv:.2%}; p_base={P0:.4f}; f_cash={fcash(P0,r0):.4f}; f_inv={finv(P0,r0):.4f}; NCI={NCI:.4%}; T_hoan={T_def:.3f} nam, he so PV={(1+r0)**(-T_def):.4f}')
    sv = {k: val(k) for k in w}; C = ctr()
    print('kich ban truoc/sau CKTK:', {k: (round(v), round(v * (1 - L))) for k, v in sv.items()})
    print(f'TAM pre={C/(1-L):.0f} post={C:.0f} vung_post=[{sv["bad"]*(1-L):.0f};{sv["good"]*(1-L):.0f}] 0.85xtam={0.85*C:.0f}')
    # cau cau buoc: tu rev4 -> rev5
    steps = [('rev4 (control)', dict(ctrl=True)),
             ('+ bo f rieng cua kich ban xau (f=1 ca 3 kich ban; = tinh toan skeptic r3 +10,5%)', dict(fover=1.0, inv_trap=False, nci=0, defer=False)),
             ('+ NCI 3,28%', dict(fover=1.0, inv_trap=False, defer=False)),
             ('+ hoan cong lai bao hanh T=1,48 nam', dict(fover=1.0, inv_trap=False)),
             ('+ f_cash theo p Laplace', dict(inv_trap=False)),
             ('+ f_inv dau tu dai han (= rev5)', dict())]
    for lab, kw in steps: print(f'   cau: {lab}: {ctr(**kw):.0f}')
    print('-- luoi hazard p (f_cash, f_inv, tam):')
    for p in M['unlock_hazard']['grid']: print(f'   p={p:.4f}: f_cash={fcash(p,r0):.3f} f_inv={finv(p,r0):.3f} tam={ctr(p=p):.0f}')
    print('-- f_cash=1 nhung giu cac sua khac:', round(ctr(fover=1.0, inv_trap=False)))
    print('-- yield tien gui 1,18%/1,45%:', {yy: round(sum(w[k]*((lambda yy: val(k, fover=(yy*0.8+P0)/(r0+P0)))(yy)) for k in w)*(1-L)) for yy in (0.0118, 0.0145)})
    print('-- LN giu lai cung bi ket (payout 38%/0%):', {pp: round(ctr(retain_trap=pp)) for pp in (0.38, 0.0)})
    print('-- DT co so:', {R: round(sum(w[k]*val(k, rev=(R if k=='base' else None)) for k in w)*(1-L)) for R in (3234, 3378, 3490, 4150, 5433)})
    print('-- GPM co so:', {g: round(sum(w[k]*val(k, gpm=(g if k=='base' else None)) for k in w)*(1-L)) for g in (0.03, 0.04, 0.045, 0.05, 0.06, 0.07)})
    print('-- cong lai bao hanh %DT:', {a: round(sum(w[k]*val(k, a=(a if k!='bad' else None)) for k in w)*(1-L)) for a in (0.0, 0.01, 0.0168, 0.03, 0.041)})
    print('-- khong hoan cong lai:', round(ctr(defer=False)), ' NCI=0:', round(ctr(nci=0)))
    print('-- ty le chi tien so du bao hanh:', {c: round(ctr(cs=c)) for c in (0.009, 0.25, 0.5, 1.0)})
    print('-- r beta1:', {d: f'{ctr(r=r0+d/1e4):.0f} ({ctr(r=r0+d/1e4)/C-1:+.1%})' for d in (-100, -50, 50, 100)})
    print('-- r beta0.5:', {d: f'{ctr(r=r0+d/1e4*0.5):.0f}' for d in (-100, -50, 50, 100)})
    print('-- Ke band 12.3/13.4:', {rr: round(ctr(r=rr)) for rr in (0.123, 0.134)})
    print('-- thanh khoan:', {LL: round(ctr(LL=LL)) for LL in (0, 0.05, 0.1, 0.2)})
    print('-- trong so 25/50/25:', round(ctr(ww={'bad':0.25,'base':0.5,'good':0.25})), ' 40/45/15:', round(ctr(ww={'bad':0.4,'base':0.45,'good':0.15})))
    SQ = M['sens']
    print('-- ngoai tru: xoa con =>', round(ctr(extra=SQ['qualified_subs'])), '; + lien ket =>', round(ctr(extra=SQ['qualified_subs']+SQ['qualified_assoc'])))
    print('-- CPH (uoc luong khung):', {x: round(ctr(extra=x)) for x in SQ['cph_bracket']})
    print('-- bao lanh 69-1 25/50/100%:', {fr: round(ctr(extra=fr*SQ['guarantee_6901_overdue_debt'])) for fr in (0.25, 0.5, 1.0)})
    print('-- HNA=0 (bo lai an):', round(sum(w[k]*val(k, extra=M['hna_after_tax']*finv(P0,r0)/fcash(P0,r0)) for k in w)*(1-L)))
    print('-- khoan tru o MENH GIA (khong nhan f) xoa con / CPH 300 / bao lanh 100%:', round(ctr(extra=SQ['qualified_subs']/fcash(P0,r0))), round(ctr(extra=300/fcash(P0,r0))), round(ctr(extra=SQ['guarantee_6901_overdue_debt']/fcash(P0,r0))))
    print(f'-- sau co tuc CP 31,7%: tam/1,317={C/1.317:.0f} vung=[{sv["bad"]*(1-L)/1.317:.0f};{sv["good"]*(1-L)/1.317:.0f}]')
    Vtot = C * S / 1000; ns = SQ['capraise_new_shares_m']; px = SQ['capraise_price']
    print(f'-- tang von {ns}tr cp @ {px}: {(Vtot+ns*px/1000*(1-L))/(S+ns)*1000:.0f} (V4a: von moi cho du an = NPV0, tinh theo menh gia thu ve); phat hanh bang tam => khong doi')
    json.dump({'center_post': round(C), 'center_pre': round(C/(1-L)), 'scen_post': {k: round(v*(1-L)) for k, v in sv.items()},
               'zone': [round(sv['bad']*(1-L)), round(sv['good']*(1-L))], 'control_rev4': round(C4),
               'f_cash': round(fcash(P0, r0), 4), 'f_inv': round(finv(P0, r0), 4)}, open(os.path.join(H, 'calc_rev5_out.json'), 'w'))
