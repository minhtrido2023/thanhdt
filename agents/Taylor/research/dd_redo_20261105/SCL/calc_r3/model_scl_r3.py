"""SCL — DD redo VÒNG 3 (08/11/2026, job Taylor_20261108_142022). Áp đính chính TOP5_CORRECTIONS_20261108.md §SCL.
Mô hình MÙ GIÁ ở phần lõi (scl_r3_core_5Ffix.py); giá chỉ vào ở bước CK thanh khoản / nhãn / giá ngụ ý.

Bridge r2 → r3 (mỗi bước đổi MỘT thứ, theo thứ tự):
  S0 r2 headline (lõi gốc, GPM sai)                         — đối chứng, phải = 22.769
  S1 lõi sửa GPM (GPM_P0 là TTM ⇒ năm = Q4)                 — đối chứng, phải = 21.813 (ADDENDUM_5F / skeptic)
  S2 giá + ADV tới 06/11 (px_scl_r3_20261106.csv)           — CK 5 tỷ tính lại
  S3 trục lỗ phải thu [UL] ra khỏi base (→ độ nhạy)         — base = sổ sách (BCTC: Vincons 67,89 tỷ, dự phòng 0)
  S4 bội số áp lên E1 = E0×(1+g) thay vì E0                 — (1−g/ROE)/(r−g) là P/E kỳ tới (Gordon V0 = D1/(r−g))
  S5 CK ở cỡ sleeve thật 40 triệu (trong vùng √) thay 5 tỷ (219% ADV, ngoài vùng) — headline; 5 tỷ báo song song
Chạy: /home/trido/thanhdt/wc_venv/bin/python -I model_scl_r3.py → model_scl_r3_out.json/.txt + LOCK_r3_md5.txt
"""
import contextlib, io, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, os.path.join(HERE, "..", "calc"))
sys.path.insert(0, os.path.join(ROOT, "_common_g2r2"))
sys.path.insert(0, WC)
import ddr2 as g  # noqa: E402
with contextlib.redirect_stdout(io.StringIO()):
    import scl_r3_core as c0          # lõi gốc — chỉ chân đối chứng S0
    import scl_r3_core_5Ffix as c     # lõi sửa GPM
import deposit_rate_vn as dep  # noqa: E402

B = 1e9
ASOF = "2026-11-06"
PX_OLD = g.PX_CSV
PX_NEW = os.path.join(HERE, "px_scl_r3_20261106.csv")

# r = 13,5% + 1,0×(lãi huy động 12T hiệu dụng − 7,40%)
_d = dep.effective_deposit_rate(ASOF)
R = dict(r=round(0.135 + 1.0 * (_d["rate_pct"] - 7.40) / 100, 6), dep_pct=_d["rate_pct"], dep_source=_d["rate_source"], asof=ASOF)
r0 = R["r"]

L_old = g.liquidity("SCL")
g.PX_CSV = PX_NEW
L = g.liquidity("SCL")
g.PX_CSV = PX_OLD
assert L["price_date"] == ASOF, L["price_date"]
PX = L["price"]
DISC_5TY = L["ref_discount"]
DISC_40TR = L["sleeve_discount"]["40tr"]
TERP = (PX + c.RATIO * c.SUB_PX) / (1 + c.RATIO)

RECV_CONC = 67.892070164          # BCTC HN Q3/2026 V.3: Vincons 67.892.070.164 / 115.969.828.921 = 58,54%; dự phòng 0
BR = {"CYCLICAL": 0.50, "ADMIN_GATED": 0.30, "STRUCTURAL": 0.20}
AX_CORE = dict(
    branch=[(b, b, w) for b, w in BR.items()],
    rev=[(x, x, 0.5) for x in c.GRID["rev"]],
    norm=[(x, x, 1 / 3) for x in c.GRID["norm"]],
    g=[(f"g{x:.0%}", x, 1 / 3) for x in c.GRID["g"]],
    roe=[(f"roe{x:.0%}", x, 0.5) for x in c.GRID["roe"]],
)
RECV_AX = [("0%", 0.0, 0.75), ("20%", 0.20, 0.20), ("50%", 0.50, 0.05)]
AX_R2 = dict(AX_CORE, recv=RECV_AX)
RECV_R2 = 116.0 * 0.585           # hằng số r2 (giữ cho chân đối chứng tái lập byte)


def fn(branch, rev, norm, g, roe, recv=0.0, irr=None, r=None, basis="cum", e1=True, core=None, par=False, recv_amt=RECV_CONC):
    cc = core or c
    rr = r0 if r is None else r
    gf = (1 + g) if e1 else 1.0
    if branch == "TROUGH":
        v = cc.value("CYCLICAL", rev, norm, g, roe, cc.GRID["i_cip"][0], rr)
        rv = cc.TTM[0] if rev == "TTM" else cc.E2026[0]
        m_now = cc.NPM_TTM if rev == "TTM" else cc.npm(*cc.E2026)
        m = cc.NPM_MEAN[norm] - 0.5 * (m_now - cc.NPM_MEAN[norm])
        e = rv * m + cc.CIP_TOTAL * cc.GRID["i_cip"][0] * (1 - cc.TAX)
        mult = v["mult"]
    else:
        v = cc.value(branch, rev, norm, g, roe, cc.GRID["i_cip"][0], rr)
        e, mult = v["e_exist"], v["mult"]
    if par:   # khung toàn bộ nợ theo mệnh giá (value_par của lõi): E không đòn bẩy × bội số − (nợ ngoài dự án − tiền)
        e_unlev = e + cc.DEBT_OTHER * cc.I_REAL * (1 - cc.TAX)
        tot = e_unlev * gf * mult - (cc.DEBT_OTHER - cc.CASH)
    else:
        tot = e * gf * mult
    tot -= recv * recv_amt * (1 - cc.TAX)
    if irr is not None:
        tot += cc.PHALAI_TOTAL * (irr / rr - 1)
    return tot * B / cc.SH_NOW if basis == "cum" else (tot + cc.PROCEEDS) * B / cc.SH_POST


def D(axes, disc, px=None, **kw):
    return g.dist(g.build_grid(axes, lambda **a: fn(**a, **kw)), PX if px is None else px, disc)


def brief(d):
    P = d["P_post"]
    return dict(center_pre=d["center_pre"], center_post=d["center_post"], p10=P["p10"], p50=P["p50"], p90=P["p90"],
                pct_below=d["pct_w_below_px"], n=d["n"], min_post=d["min_post"], max_post=d["max_post"])


# ---------- bridge ----------
S = {}
S["S0_r2_headline"] = brief(D(AX_R2, L_old["ref_discount"], px=L_old["price"], e1=False, core=c0, recv_amt=RECV_R2))
S["S1_gpm_fix"] = brief(D(AX_R2, L_old["ref_discount"], px=L_old["price"], e1=False, recv_amt=RECV_R2))
S["S2_px_0611"] = brief(D(AX_R2, DISC_5TY, e1=False, recv_amt=RECV_R2))
S["S2b_recv_amt_bctc"] = brief(D(AX_R2, DISC_5TY, e1=False))
S["S3_no_recv_axis"] = brief(D(AX_CORE, DISC_5TY, e1=False))
S["S4_E1"] = brief(D(AX_CORE, DISC_5TY, e1=True))
S["S5_ck_sleeve40"] = brief(D(AX_CORE, DISC_40TR, e1=True))
ctrl = dict(S0=round(S["S0_r2_headline"]["center_post"]), S0_expect=22769,
            S1=round(S["S1_gpm_fix"]["center_post"]), S1_expect=21813, S1_p90=round(S["S1_gpm_fix"]["p90"]), S1_p90_expect=26672)
ctrl["ok"] = ctrl["S0"] == 22769 and ctrl["S1"] == 21813 and ctrl["S1_p90"] == 26672

# ---------- headline + phân phối đầy đủ ----------
outs_H = g.build_grid(AX_CORE, fn)
H = g.dist(outs_H, PX, DISC_40TR)
H5 = g.dist(outs_H, PX, DISC_5TY)
Hp = g.dist(g.build_grid(AX_CORE, lambda **a: fn(**a, basis="post")), TERP, DISC_40TR)
Hp5 = g.dist(g.build_grid(AX_CORE, lambda **a: fn(**a, basis="post")), TERP, DISC_5TY)
lab = g.label(PX, H["P_post"]["p10"], H["P_post"]["p90"])
lab5 = g.label(PX, H5["P_post"]["p10"], H5["P_post"]["p90"])
labp = g.label(TERP, Hp["P_post"]["p10"], Hp["P_post"]["p90"])
central = fn("ADMIN_GATED", "TTM", "2023-TTM", 0.04, 0.175)
p10_br = g.branch_share(outs_H, "branch", 0.10); p90_br = g.branch_share(outs_H, "branch", 0.90)

# ---------- biến thể song song (cùng E1; báo ở cả 2 cỡ CK) ----------
def both(axes, **kw):
    return dict(ck40tr=brief(D(axes, DISC_40TR, **kw)), ck5ty=brief(D(axes, DISC_5TY, **kw)))


AX_IRR = dict(AX_CORE, irr=[("10%", 0.10, 0.25), ("13.5%", 0.135, 0.50), ("17%", 0.17, 0.25)])
AX_TR = dict(AX_CORE, branch=[("CYCLICAL", "CYCLICAL", 0.5 - 0.2 / 3), ("ADMIN_GATED", "ADMIN_GATED", 0.3 - 0.2 / 3),
                              ("STRUCTURAL", "STRUCTURAL", 0.2 - 0.2 / 3), ("TROUGH", "TROUGH", 0.2)])
ALT = dict(
    E0_instead_of_E1=both(AX_CORE, e1=False),
    with_recv_axis_UL=both(dict(AX_CORE, recv=RECV_AX)),
    with_phalai_irr=both(AX_IRR),
    symmetric_trough=both(AX_TR),
    par_debt=both(AX_CORE, par=True),
    trough_plus_par=both(AX_TR, par=True),
    skeptic_combo_check=dict(note="S3+S4+S5 cùng lúc = headline", ck40tr=brief(H)),
)

# ---------- độ nhạy r ----------
sens_r = {}
for key, rr in g.r_grid(r0).items():
    e = D(AX_CORE, DISC_40TR, r=rr)["center_post"]
    sens_r[key] = dict(r=rr, post=e, pct=e / H["center_post"] - 1)

# ---------- giá ngụ ý ----------
mult_c = (1 - 0.04 / 0.175) / (r0 - 0.04)
E_impl = PX / (1 - DISC_40TR) * c.SH_NOW / B / (1.04 * mult_c)       # E0 chuẩn hoá ngụ ý (tỷ), g4% ROE17,5% r 13,5%, E1
E_ttm = c.value("STRUCTURAL", "TTM", "2023-TTM", 0.04, 0.175, c.GRID["i_cip"][0], r0)["e_exist"]


def v_struct(rr):
    return fn("STRUCTURAL", "TTM", "2023-TTM", 0.04, 0.175, r=rr) * (1 - DISC_40TR)


lo, hi = 0.06, 0.20
for _ in range(100):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if v_struct(mid) > PX else (lo, mid)
r_impl = (lo + hi) / 2
roe_ttm = c.TTM[1] / c.EQ_PARENT
implied = dict(E0_norm_implied_ty=E_impl, E_ttm_with_cip_addback_ty=E_ttm, np_ttm_ty=c.TTM[1],
               hist_np_ty={str(k): v[1] for k, v in c.HIST.items()},
               r_implied_structural_ttm_g4_roe175=r_impl, deposit_implied_pct=7.40 + (r_impl - 0.135) * 100,
               note="E ngụ ý ở tham số giữa (g4%, ROE 17,5%, r 13,5%, bội số áp E1, CK 40tr); r ngụ ý nếu biên TTM giữ vĩnh viễn (STRUCTURAL, không quay về TB)")
gordon = c.EQ_PARENT * (roe_ttm - 0.04) / (r0 - 0.04) * 1.04 * B / c.SH_NOW

out = dict(ticker="SCL", round=3, asof_price_date=ASOF, price=PX, price_basis="CUM-quyền (ĐKCC 10/11/2026; GDKHQ 09/11)", terp=TERP,
           r_info=R, liq=dict(L, table=None), liq_old_price_date=L_old["price_date"], disc_40tr=DISC_40TR, disc_5ty=DISC_5TY,
           control=ctrl, bridge=S,
           headline=dict(ck="sleeve 40tr", dist=H, label=lab, center_param_post=central * (1 - DISC_40TR),
                         p10_branch=p10_br, p90_branch=p90_br),
           headline_ck5ty=dict(dist=H5, label=lab5),
           post_rights=dict(ck40tr=Hp, ck5ty=Hp5, label_terp=labp,
                            label_terp_5ty=g.label(TERP, Hp5["P_post"]["p10"], Hp5["P_post"]["p90"])),
           alternatives=ALT, sens_r=sens_r, implied=implied,
           gordon=dict(g=0.04, roe_ttm=roe_ttm, value_E1=gordon, note="một biến thể (không có lãi tiền gửi đáng kể: tiền 95,1 vs nợ 416,5)"))
json.dump(out, open(os.path.join(HERE, "model_scl_r3_out.json"), "w"), ensure_ascii=False, indent=1, default=float)

f = g.fmt
def line(name, d):
    return f"{name:<28} tâm {f(d['center_post'])} P10 {f(d['p10'])} P50 {f(d['p50'])} P90 {f(d['p90'])} dưới-giá {d['pct_below']:.1%}"


P = H["P_post"]; P5 = H5["P_post"]
lines = [f"SCL r3 giá {f(PX)} ({ASOF}, CUM) TERP {f(TERP)} | r {r0:.4f} ({R['dep_source']}) | n {H['n']}",
         f"ĐỐI CHỨNG: S0 {ctrl['S0']} (kỳ vọng 22769) S1 {ctrl['S1']} P90 {ctrl['S1_p90']} (kỳ vọng 21813/26672) ok={ctrl['ok']}",
         "BRIDGE:"] + [line("  " + k, v) for k, v in S.items()] + [
         f"HEADLINE (CK 40tr {DISC_40TR:.2%}): tâm trước CK {f(H['center_pre'])} sau {f(H['center_post'])} | P10 {f(P['p10'])} P50 {f(P['p50'])} P90 {f(P['p90'])} | min {f(H['min_post'])} max {f(H['max_post'])} | dưới giá {H['pct_w_below_px']:.1%} | {lab} | giá/tâm {PX/H['center_post']-1:+.1%} giá/P90 {PX/P['p90']-1:+.1%}",
         f"  tham số trung tâm sau CK {f(central*(1-DISC_40TR))} | nhánh quanh P10 {p10_br} | quanh P90 {p90_br}",
         f"CK 5 tỷ ({DISC_5TY:.2%}; ADV120 {L['adv120_med_ty']:.2f} tỷ; Q/ADV {L['ref_pct_adv120']:.0%}; vùng √ {L['ref_in_sqrt_zone']}): tâm {f(H5['center_post'])} P10 {f(P5['p10'])} P50 {f(P5['p50'])} P90 {f(P5['p90'])} dưới giá {H5['pct_w_below_px']:.1%} | {lab5}",
         f"  ADV250 {L['adv250_med_ty']:.2f} → {L['ref_discount_adv250']:.2%} | ADV60 {L['adv60_med_ty']:.2f} → {L['ref_discount_adv60']:.2%} | sleeve 10/20/40tr " + "/".join(f"{v:.2%}" for v in L['sleeve_discount'].values()),
         f"SAU QUYỀN (TERP {f(TERP)}): CK40tr tâm {f(Hp['center_post'])} P10 {f(Hp['P_post']['p10'])} P90 {f(Hp['P_post']['p90'])} ⇒ {labp} | CK5tỷ tâm {f(Hp5['center_post'])} P90 {f(Hp5['P_post']['p90'])} ⇒ {out['post_rights']['label_terp_5ty']}",
         "SONG SONG:"] + [line(f"  {k}[{ck}]", v) for k, d in ALT.items() for ck, v in d.items() if ck != "note"] + [
         "Độ nhạy r (tâm, CK40tr): " + " | ".join(f"{k} {f(v['post'])} ({v['pct']:+.1%})" for k, v in sens_r.items()),
         f"GIÁ NGỤ Ý: E0 chuẩn hoá {E_impl:.1f} tỷ/năm (TTM có cộng lãi dự án {E_ttm:.1f}; NP TTM {c.TTM[1]:.1f}; NP 2020–25 " + "/".join(f"{v[1]:.0f}" for v in c.HIST.values()) + f") | hoặc biên TTM vĩnh viễn + r {r_impl:.2%} (lãi huy động ~{implied['deposit_implied_pct']:.2f}%)",
         f"Gordon E1 g4% ROE TTM {roe_ttm:.1%} ⇒ {f(gordon)} (trước CK)"]
open(os.path.join(HERE, "model_scl_r3_out.txt"), "w").write("\n".join(lines) + "\n")
g.write_lock(os.path.join(HERE, "LOCK_r3_md5.txt"),
             [os.path.join(ROOT, "_common_g2r2", "ddr2.py"), os.path.join(ROOT, "_shared", "wpct.py"),
              os.path.join(ROOT, "_common_g2", "ddg2.py"), PX_OLD, PX_NEW, os.path.join(HERE, "px_scl_r3.sql"),
              os.path.join(WC, "deposit_rate_vn.py"), os.path.join(WC, "cctg_rate_vn.py"),
              os.path.join(WC, "data", "deposit_rate_vn_events.csv"), os.path.join(WC, "data", "cctg_rate_vn_events.csv"),
              os.path.abspath(__file__), os.path.join(HERE, "..", "calc", "scl_r3_core.py"),
              os.path.join(HERE, "..", "calc", "scl_r3_core_5Ffix.py")], "SCL r3")
print("\n".join(lines))
