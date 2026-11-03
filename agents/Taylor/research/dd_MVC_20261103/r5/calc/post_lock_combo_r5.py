"""SAU KHOA — to hop 4 moc (cung mo hinh, khong doi tham so goc)."""
import sys; sys.dont_write_bytecode = True
import model_r5 as R, valuation_base as M
def run(lab, endA, **kw):
    old = dict(M.END_A); M.END_A.update({k: endA for k in R.SCN}) if endA else None
    print(f'{lab:60s} {R.EV(kw):,.0f}'); M.END_A.update(old)
run('4 moc tieu cuc (W15/60, capex+30%, GP TL 2035, PW 70/30, tre giu)', 2035, W={'tot': .15, 'co_so': .6, 'xau': .2, 'rat_xau': .05}, capex=1.3, PW={'g2031': .7, 'real': .3})
run('4 moc tieu cuc + holding 30%', 2035, W={'tot': .15, 'co_so': .6, 'xau': .2, 'rat_xau': .05}, capex=1.3, PW={'g2031': .7, 'real': .3}, hold=0.3)
run('4 moc tieu cuc + holding 30% + mo moi DCF r13 moi kb', 2035, W={'tot': .15, 'co_so': .6, 'xau': .2, 'rat_xau': .05}, capex=1.3, PW={'g2031': .7, 'real': .3}, hold=0.3, mine_r3=True)
run('4 moc tich cuc (W35/50/10, capex-30%, GP TL 2045, PW 30/70, khong tre)', 2045, W={'tot': .35, 'co_so': .5, 'xau': .1, 'rat_xau': .05}, capex=0.7, PW={'g2031': .3, 'real': .7}, delay=False)
run('rat_xau 100% x g2031 (khong phang)', None, W={'tot': 0, 'co_so': 0, 'xau': 0, 'rat_xau': 1}, PW={'g2031': 1.0})
