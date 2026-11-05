"""Cau noi tam cu (trung diem zone A7-B7 Ke 13%, 36.173) -> tam moi truoc CK thanh khoan. Chay sau model.py. Moi buoc do bang ham model."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model as M
o = json.load(open('model_out.json'))
w0 = o['ore_weight_sens_pre']['w_molai0.0']
ns_ps = M.NS_CIP * (1 - M.S_EQ) * 1e9 / M.SH
ns_bad = 0.3 * (-500) * (1 - M.S_EQ) * 1e9 / M.SH
hc_old = (0.2 * 0.03 + 0.5 * 0.09 + 0.3 * 0.29)            # haircut phap ly tien rong r12 HC_LEGAL, trong so w r12
hc_ps = hc_old * (M.CASH_DEP - M.DEBT) * (1 - M.S_EQ) * 1e9 / M.SH
res = dict(center_pre=o['center_pre'], ore_weight_0p5_contrib=o['center_pre'] - w0, ns_book_ps=ns_ps, ns_bad_overrun_weighted_ps=ns_bad,
           ns_old_net_ps=-447, ns_delta_vs_old=ns_ps + ns_bad + 447, legal_haircut_old_weighted_rate=hc_old, legal_haircut_removed_ps=hc_ps)
res['residual_method_r_core'] = o['center_pre'] - 36173 - res['ore_weight_0p5_contrib'] - res['ns_delta_vs_old'] - hc_ps
json.dump(res, open('bridge_out.json', 'w'), indent=1); print(json.dumps({k: round(v, 3) if isinstance(v, float) else v for k, v in res.items()}, indent=1))
# Do vung nhan khi KHONG gan trong so mo lai khai truong (w_molai = 0): luoi 3 kb x 5 he so EBIT
import itertools, common as C
v, w = [], []
for s, m in itertools.product(M.SCN, M.MULTS):
    v.append(M.value_ps(s, 'dung', m)); w.append(M.SCN[s]['w'] / len(M.MULTS))
q = C.wq(v, w); d = json.load(open('../SUMMARY.json'))['liq_disc_5ty']
rob = dict(center_pre=sum(M.SCN[s]['w'] * M.value_ps(s, 'dung') for s in M.SCN), q_pre={k: round(x) for k, x in q.items()},
           q_post={k: round(x * (1 - d)) for k, x in q.items()})
rob['center_post'] = round(rob['center_pre'] * (1 - d)); rob['center_pre'] = round(rob['center_pre'])
json.dump(dict(res, ore_closed_only=rob), open('bridge_out.json', 'w'), indent=1); print(json.dumps(rob))
