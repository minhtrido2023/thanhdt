"""TV1 — bước 3c (5F tầng b) moat trong mô hình, r2 job Taylor_20261107_122443 (07/11/2026): thêm RONIC_ONLY, NARROW fade về trung vị 6,0%/trung bình 6,77% peer, CK 5 tỷ/1 tỷ/sleeve.
CHỈ đổi phần TERMINAL của DCF tư vấn (thứ moat chạm tới); thuỷ điện (PPA có thời hạn 2059), tiền ròng, lưới 5 trục, xác suất, CK thanh khoản GIỮ NGUYÊN r2.
Không import model_tv1_r2.py (nó ghi đè out/LOCK) — tái tạo fn() nguyên văn, chỉ thay consult().
Chế độ:
  WIDE_ngam = mô hình r2 hiện hành: biên kịch bản giữ VĨNH VIỄN, g_term 5%, tái đầu tư VLĐ 49%ΔDT ⇒ RONIC ngầm = m·0,8·0,8/0,49.
  NARROW    = giữ biên kịch bản 2027–30 (đường ống PDP8), fade tuyến tính 2031–32 về biên TB chu kỳ NGÀNH 6%, terminal RONIC = Ke.
  NONE      = fade nhanh: từ 2028 về 6% hết 2029, terminal RONIC = Ke.
  NONE_own  = (đối chiếu) như NONE nhưng về biên TB chu kỳ RIÊNG TV1 2022–9T26.
Biên ngành 6% = trung vị EBITM_P0 TV2/TV3/TV4 2016–2026 (33 năm-mã), BQ tav2_bq.ticker_financial (lệnh trong ADDENDUM_5F.md).
Chạy: $DNA_PYEXE -I moat_5f_tv1.py → moat_5f_tv1_r2_out.json/.txt"""
import contextlib, io, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "..", "_common_g2r2"))
import ddr2 as g
with contextlib.redirect_stdout(io.StringIO()):
    import tv1_v2_core as c

R = g.r_info(); r0 = R["r"]
L = g.liquidity("TV1"); PX = L["price"]; disc = L["ref_discount"]
P_NOW = 949.0
M_MED = 0.06; M_MEAN = 0.0677   # peer TV2-4 2016-26, 33 năm-mã: trung vị 5,96% (làm tròn 6,0%), trung bình 6,77% (BQ)
M_IND = M_MED
M_OWN = sum((c.MH[y][0] + c.MH[y][1]) / 2 for y in (2022, 2023, 2024, 2025))
M_OWN = (M_OWN + 0.11) / 5      # + 9T/26 biên 11% (cận A, mô hình dùng)

def margin_path(m, mode, m_t):
    yrs = list(range(2027, 2033))
    if mode in ("NARROW", "NARROW_MEAN"):
        return [m if y <= 2030 else m + (m_t - m) * (y - 2030) / 3 for y in yrs], m_t
    if mode == "RONIC_ONLY":
        return [m] * 6, m   # giữ biên từng kịch bản vĩnh viễn, chỉ đổi TV sang RONIC=Ke
    if mode in ("NONE", "NONE_own"):
        return [m if y == 2027 else (m + (m_t - m) / 2 if y == 2028 else m_t) for y in yrs], m_t
    return [m] * 6, m

def consult_m(s, mode, ke, wc, shock=None):
    if mode == "WIDE_ngam":
        return c.consult(s, ke=ke, wc=wc, shock=shock)[0]
    p = c.SCN[s]; m_t = M_OWN if mode == "NONE_own" else (M_MEAN if mode == "NARROW_MEAN" else M_IND)
    ms, mT = margin_path(p["m"], mode, m_t)
    rev = c.CON26; prev = c.CON26; out = []
    for i, y in enumerate(range(2027, 2033)):
        gg = p["g"] if y <= 2030 else (p["g"] + c.G_TERM) / 2
        rn = rev * (1 + gg); re_ = rn * (shock[i] if shock and i < len(shock) else 1.0)
        ebit = re_ * ms[i]
        if re_ < rn: ebit -= (rn - re_) * (1 - ms[i]) * 0.5
        out.append(ebit * (1 - c.TAX) * (1 - c.KTPL) - wc * (re_ - prev) - 5.0); rev = rn; prev = re_
    nopat_t = rev * (1 + c.G_TERM) * mT * (1 - c.TAX) * (1 - c.KTPL)
    tv = (nopat_t - 5.0) / ke            # RONIC = Ke ⇒ tăng trưởng không tạo giá trị: TV = NOPAT_{T+1}/Ke
    return c.pv_mid(out, ke) + tv / (1 + ke) ** (c.T0 + len(out))

def hydro(pk, q, timing, r):
    base = c.hydro_fcfe(c.PRICE[pk], q)
    cfs = c.hydro_fcfe(P_NOW, q)[:int(timing[-1])] + base[int(timing[-1]):] if timing.startswith("delay") else base
    v = c.pv_mid(cfs, r)
    return v - c.truy * (1 - c.TAX) / (1 + r) if timing == "retro" else v

def mk(mode):
    def fn(ppa, consult, q, timing, wc, ban=None):
        return max(c.ps(hydro(ppa, q, timing, r0) + consult_m(consult, mode, r0, wc, ban) + c.BS), 0.0)
    return fn

AXES = dict(ppa=[(k, k, c.PROB[k]) for k in c.PRICE], consult=[(k, k, c.P_CON[k]) for k in c.SCN],
            q=[(f"Q{x}", x, 1 / 3) for x in (175.0, c.Q_P50, 200.0)],
            timing=[("retro", "retro", 0.10), ("2027", "base", 0.70), ("delay1", "delay1", 0.15), ("delay2", "delay2", 0.05)],
            wc=[("45%", 0.45, 1 / 3), ("49%", 0.49, 1 / 3), ("53%", 0.53, 1 / 3)])
AX_BAN = dict(AXES, ban=[("khong", None, 0.65), ("cam3y", [0.5] * 3, 0.35)])
res = {}
DISCS = {"CK5ty": disc, "CK1ty": L["table"]["1000tr_adv120"]["discount"], "CKsleeve": L["sleeve_max_discount"]}
cells = {}
for mode in ("WIDE_ngam", "RONIC_ONLY", "NARROW", "NARROW_MEAN", "NONE", "NONE_own"):
    GR = g.build_grid(AXES, mk(mode))
    for dn, dv in DISCS.items():
        Dx = g.dist(GR, PX, dv)
        cells[f"{mode}|{dn}"] = dict(disc=dv, center_post=Dx["center_post"], p10=Dx["P_post"]["p10"], p50=Dx["P_post"]["p50"], p90=Dx["P_post"]["p90"],
                                     pct_below=Dx["pct_w_below_px"], label=g.label(PX, Dx["P_post"]["p10"], Dx["P_post"]["p90"]))
    D = g.dist(GR, PX, disc); Db = g.dist(g.build_grid(AX_BAN, mk(mode)), PX, disc)
    cw = sum(c.P_CON[s] * consult_m(s, mode, r0, 0.49) for s in c.SCN)
    res[mode] = dict(center_post=D["center_post"], p10=D["P_post"]["p10"], p50=D["P_post"]["p50"], p90=D["P_post"]["p90"],
                     pct_below=D["pct_w_below_px"], label=g.label(PX, D["P_post"]["p10"], D["P_post"]["p90"]),
                     consult_exp_dcp=c.ps(cw), consult_by_scn={s: c.ps(consult_m(s, mode, r0, 0.49)) for s in c.SCN},
                     ban_center_post=Db["center_post"], ban_p10=Db["P_post"]["p10"])
ronic = {s: c.SCN[s]["m"] * (1 - c.TAX) * (1 - c.KTPL) / c.WC_INT for s in c.SCN}
out = dict(r=r0, price=PX, disc=disc, discs=DISCS, cells=cells, m_med=M_MED, m_mean=M_MEAN, m_ind=M_IND, m_own=M_OWN, ronic_implied_r2=ronic, modes=res)
json.dump(out, open(os.path.join(HERE, "moat_5f_tv1_r2_out.json"), "w"), ensure_ascii=False, indent=1, default=float)
f = g.fmt
lines = [f"r {r0:.4f} | giá {f(PX)} | CK {disc:.2%} | biên ngành {M_IND:.0%} | biên TB riêng TV1 {M_OWN:.1%}",
         "RONIC ngầm r2 (m·0,64/0,49): " + " ".join(f"{s} {v:.1%}" for s, v in ronic.items())]
for k, v in res.items():
    lines.append(f"{k:10s} tâm {f(v['center_post'])} P10 {f(v['p10'])} P50 {f(v['p50'])} P90 {f(v['p90'])} | dưới giá {v['pct_below']:.1%} | {v['label']} | "
                 f"tư vấn kỳ vọng {f(v['consult_exp_dcp'])} ({' '.join(f'{s}:{f(x)}' for s, x in v['consult_by_scn'].items())}) | có cấm thầu: tâm {f(v['ban_center_post'])} P10 {f(v['ban_p10'])}")
for k, v in cells.items():
    lines.append(f"CELL {k:24s} CK {v['disc']:.2%} tâm {f(v['center_post'])} P10 {f(v['p10'])} P50 {f(v['p50'])} P90 {f(v['p90'])} | dưới giá {v['pct_below']:.1%} | {v['label']}")
open(os.path.join(HERE, "moat_5f_tv1_r2_out.txt"), "w").write("\n".join(lines) + "\n"); print("\n".join(lines))
