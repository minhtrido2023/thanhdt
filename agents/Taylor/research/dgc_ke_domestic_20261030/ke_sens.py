"""Độ nhạy định giá DGC (mô hình r12, nền A7/B7) theo Ke nội địa — job Taylor_20261030_094438.
Khung Ke (user chốt 30/10, erp_domestic_v2_20261030): β1,1, rf chuẩn hoá 6,75%, ERP nội địa 5,22–6,15%
⇒ khoảng 12,5–13,5% (dải rộng 10,5–14,0%); 15,8% Damodaran = góc nhìn nước ngoài (USD); 14,9% = Ke cũ r12 (đối chứng).
Không sửa model.py: đặt CFG['rf'] = Ke − 0,075 (model.ke() = rf + 1,0×7,5%). Ke vào: DCF (Gordon), P/B hợp lý
(ROE−g)/(Ke−g), chiết khấu 2 năm giá trị Nghi Sơn. P/E lịch sử/peer KHÔNG phụ thuộc Ke.
Chạy: /home/trido/thanhdt/wc_venv/bin/python ke_sens.py   (cwd = thư mục này)"""
import os, sys, io, contextlib, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
R12 = os.path.join(HERE, "..", "dgc_valuation_20261029_r12")
sys.path.insert(0, R12)
with contextlib.redirect_stdout(io.StringIO()):
    import model as M

A7, B7 = M.per_scn(M.CFG_A7)[0], M.per_scn(M.CFG_B7)[0]
assert (A7, B7) == (32182, 37060), (A7, B7)          # đối chứng: tái lập r12 ở Ke 14,9%
assert abs(M.ke() - 0.149) < 1e-12

KES = [("dải rộng – đầu dưới", 0.105), ("khoảng – đầu dưới", 0.125), ("khoảng – giữa", 0.130),
       ("khoảng – đầu trên", 0.135), ("dải rộng – đầu trên", 0.140), ("Ke cũ r12 (đối chứng)", 0.149),
       ("góc nhìn nước ngoài (Damodaran, USD)", 0.158)]


def dcf_parts(k, fc):
    """Bản sao dcf_core (model.py r12) trả thêm PV giai đoạn tường minh / PV terminal / tiền (đ/cp)."""
    s, k_e, g, CFG = M.SCN[k], M.ke(), M.G_BASE, M.CFG
    r = fc[(fc.scn == k) & (fc.year >= 2027)].set_index("year")
    ebit = [r.loc[2027, "ebit_core"], r.loc[2028, "ebit_core"]]
    ebit += [ebit[-1] * (1 + g) ** j for j in (1, 2, 3)]
    ns = [s["ns_np"][0], s["ns_np"][1]] + [s["ns_steady"] * (1 + g) ** j for j in (0, 1, 2)]
    wc = [CFG.get("wc27", 300) if k != "nghich" else 0, 0, 0, 0, 0]
    reinv = g / M.RONIC
    tt = [0.68 + j for j in range(5)] if CFG["mid"] else [j + 1.0 for j in range(5)]
    pv, fcff = 0.0, []
    for t in range(5):
        f = (ebit[t] * (1 - M.tax_core(2027 + t)) * (1 - CFG["mi_core"]) + ns[t]) * (1 - (reinv if t >= 2 else 0)) + wc[t]
        fcff.append(f); pv += f / (1 + k_e) ** tt[t]
    f_T = fcff[-1]
    if CFG["term_tax"] is not None:
        f_T = (ebit[-1] * (1 - CFG["term_tax"]) * (1 - CFG["mi_core"]) + ns[-1]) * (1 - reinv) + wc[-1]
    tv = f_T * (1 + g) / (k_e - g) / (1 + k_e) ** (tt[-1] if CFG["mid"] else 5)
    cash = M.cash_adj(k) - M.ns_left()
    tot = M.per_share(pv + tv + cash)
    assert abs(tot - M.dcf_core(k, k_e, g, fc=fc)) < 1e-6
    return M.per_share(pv), M.per_share(tv), M.per_share(cash), tot


def run(cfg, ke, ronic=None):
    old_ronic = M.RONIC
    if ronic is not None:
        M.RONIC = ronic
    try:
        c = dict(cfg, rf=ke - 0.075)
        ev, th, co, ng, r = M.per_scn(c)
        old = dict(M.CFG); M.CFG.clear(); M.CFG.update(dict(dict(fund=0.0, wc27=300), **c))
        try:
            parts = {k: dcf_parts(k, r["fc"]) for k in M.SCN}
        finally:
            M.CFG.clear(); M.CFG.update(old)
        sm = r["summ"].set_index("scn")
        return ev, th, co, ng, sm, parts
    finally:
        M.RONIC = old_ronic


rows = []
for lab, ke in KES:
    for ronic_lab, ronic in (("RONIC 12% (mô hình)", None), ("RONIC = Ke", ke)):
        for nm, cfg in (("A7", M.CFG_A7), ("B7", M.CFG_B7)):
            ev, th, co, ng, sm, parts = run(cfg, ke, ronic)
            p = parts["coso"]
            rows.append(dict(muc=lab, ke=round(ke * 100, 1), ronic=ronic_lab, nen=nm, ev=ev, thuan=th, coso=co, nghich=ng,
                             dcf_coso=int(sm.dcf["coso"]), sotp_coso=int(sm.sotp["coso"]), pb_coso=int(sm.v_pb["coso"]),
                             pe_dgc_coso=int(sm.v_pe_dgc10y["coso"]),
                             tv_share_op_coso=round(p[1] / (p[0] + p[1]), 3), tv_share_dcf_coso=round(p[1] / p[3], 3)))
df = pd.DataFrame(rows)
df.to_csv(os.path.join(HERE, "out_ke_sens.csv"), index=False)
pd.set_option("display.width", 250)
print(f"tái lập r12: A7={A7} B7={B7} ở Ke={M.ke():.3f}")
print(df.to_string(index=False))
main = df[(df.ronic == "RONIC 12% (mô hình)")].pivot(index="ke", columns="nen", values="ev")
print("\nEV A7/B7 theo Ke (RONIC mô hình):\n", main.to_string())
k = df[(df.ke.between(12.5, 13.5)) & (df.ronic == "RONIC 12% (mô hình)")]
print("\nKhoảng 12,5–13,5: A7", k[k.nen == 'A7'].ev.min(), "–", k[k.nen == 'A7'].ev.max(), "; B7", k[k.nen == 'B7'].ev.min(), "–", k[k.nen == 'B7'].ev.max())
print("g =", M.G_BASE, "; RONIC mô hình =", M.RONIC, "; GDP danh nghĩa dài hạn: xem REPORT")
