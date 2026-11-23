"""Moc §9 rev2: them Q4/26 gia dinh, cua so TRUOT (12/15/20q ket thuc Q4/26); von chu Q4/26 = Q3 + LNST; XDCB Q4/26 = Q3. Khong doi file khoa."""
import runpy, io, contextlib
with contextlib.redirect_stdout(io.StringIO()): g = runpy.run_path('calc_rev2.py')
q, EQ, cip_lin, scen, c = g['q'], g['EQ'], g['cip_lin'], g['scen'], g['c']
def shift(k, n):
    x = int(k[:4]) * 4 + int(k[-1]) - 1 - n; return f'{x//4}Q{x%4+1}'
for npq in (-50, 35, 120):
    ks = sorted(q) + ['2026Q4']; Q = dict(q, **{'2026Q4': npq}); E2 = dict(EQ, **{'2026Q4': EQ['2026Q3'] + npq})
    cf = lambda k: g['CIP'] if k == '2026Q4' else cip_lin(k)
    ros = []
    for n in (12, 15, 20):
        w = ks[-n:]; ros.append(sum(4 * Q[k] / (E2[k] - cf(k)) for k in w) / n)
    ro = sum(ros) / 3; cc = scen(ro)[0]
    print(f'Q4/26 LNST={npq:+d}: ROE_op 12/15/20q={[round(x,4) for x in ros]} TB={ro:.4f} tam={cc:.0f} ({cc/c-1:+.1%})')
