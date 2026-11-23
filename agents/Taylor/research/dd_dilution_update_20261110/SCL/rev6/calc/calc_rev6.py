"""SCL — DD rev6 (23/11/2026, job Taylor_20261123_063646). MÙ GIÁ: script KHÔNG đọc giá của mã.
Lõi kinh doanh tái dùng nguyên `dd_redo_20261105/SCL/calc/scl_r3_core_5Ffix.py` (doanh thu, biên chuẩn hoá, trọng số nhánh,
lưới g/ROE, thuế) — KHÔNG re-tune. CK thanh khoản lấy nguyên từ `inputs/model_scl_r3_out.json` (md5 73a84983…, khôi phục từ
/tmp/fpt_r3, khớp md5 r3 công bố).

Thay đổi so với r4 (mỗi bước đổi MỘT thứ, bridge ở cơ sở SAU QUYỀN, CK 5 tỷ):
  B0 đối chứng r4: khung r3 (cộng lại lãi dự án, nợ dự án = giá vốn), k=0, 44.836.815 cp      ⇒ phải = 21.339
  B1 khung NỢ MỆNH GIÁ: E không đòn bẩy (cộng lại lãi sau thuế của TOÀN BỘ nợ, lãi P&L thực) × bội số
     − toàn bộ vay + tiền + XDCB theo giá vốn (V4a, NPV=0) — bỏ giả định 'nợ dự án = giá vốn' (trái dữ liệu, skeptic r1);
     tiền thu quyền 75 tỷ dùng trả nợ BIDV (NQ 1191 Điều 2) ⇒ tiền và nợ cùng mệnh giá, nhất quán.
  B2 quỹ KTPL: (a) trích 10% LNST hằng năm (NQ 486/NQ-ĐHĐCĐ 24/04/2026 qua BCTC soát xét 6T/2026 V.19.1: phúc lợi 3,214 +
     khen thưởng 3,214 = 6,428 tỷ / LNST 2025 64,30 tỷ); (b) trừ số dư quỹ KTPL 30/9 6,330 tỷ (BCTC Q3 mã 323, nợ phải trả);
     (c) trừ phần trích tạm trên LNST 9T/2026 chưa phân phối: 10% × 94,362 tỷ.
  B3 ESOP-2: 680.000 cp phát hành từ LNST (6,8 tỷ / mệnh giá 10.000; BCTC soát xét 6T/2026 V.19.1 'Phát hành ESOP từ LNST'),
     chưa phát hành tới 21/09 (NQ 1191: đang lưu hành 38.836.815) ⇒ cộng vào mẫu số, không thu tiền.
  B4 terminal NONE ⇒ RONIC = Ke (D4 user 22/11): 5 năm tái đầu tư theo lưới ROE hiện hành rồi terminal E/r (không ép ROE
     ở giai đoạn dự báo — luật 08/11). Bội số một tầng r3 giữ làm biến thể.
Chạy: /home/trido/thanhdt/wc_venv/bin/python -I calc_rev6.py  (threads=1, tất định)
"""
import contextlib, hashlib, io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research"
CORE_DIR = os.path.join(RES, "dd_redo_20261105/SCL/calc")
G_DIR = os.path.join(RES, "dd_redo_20261105/_common_g2r2")
sys.path.insert(0, CORE_DIR); sys.path.insert(0, G_DIR)
with contextlib.redirect_stdout(io.StringIO()):
    import scl_r3_core_5Ffix as c   # noqa: E402
    import ddr2 as g               # noqa: E402

B = 1e9
R3 = json.load(open(os.path.join(HERE, "..", "inputs", "model_scl_r3_out.json")))
DISC = {"ck5ty": R3["disc_5ty"], "ck40tr": R3["disc_40tr"]}
R0 = R3["r_info"]["r"] if isinstance(R3["r_info"], dict) and "r" in R3["r_info"] else 0.135
assert abs(R0 - 0.135) < 1e-9, R0          # lãi huy động 12T hiệu dụng 7,40% (cctg_12m 02/11) không đổi tới 23/11

# ---- hằng số mới, có nguồn ----
K_KTPL = (3.214231371 + 3.214231371) / 64.299896444   # NQ 486 qua BCTC 6T/2026 V.19.1 / LNST 2025 (420b 01/01/2026, BCTC Q3)
K_KTPL_3Y = None                                      # tính dưới: TB 3 lần phân phối gần nhất (độ nhạy)
DIST = {  # năm phân phối: (phúc lợi + khen thưởng + thưởng BĐH, LNST năm trước) — tỷ đồng
    2024: (4.388 + 2.194 + 3.072, 45.27),     # BCTC KT2025 V.16 'Phân phối lợi nhuận' cột 2024 (NQ 2024) / NP 2023
    2025: (2.656615120 + 1.328307560 + 0.531323024, 26.57),   # cột 2025 (NQ 523 22/4/2025) / NP 2024
    2026: (3.214231371 + 3.214231371, 64.299896444),          # NQ 486 24/4/2026 / NP 2025
}
K_KTPL_3Y = sum(a / b for a, b in DIST.values()) / 3
KTPL_BAL = 6.329533229        # BCTC Q3 HN mã 323
NP_9M = 94.362206195          # BCTC Q3 HN mã 61
ESOP2 = 680_000               # 6.800.000.000 / 10.000
CASH = 95.103078587           # BCTC Q3 mã 70 (LCTT) = V.1
DEBT = c.DEBT                 # 259,737 + 156,724 (BCTC Q3 mã 321+339)
I_REAL = c.INT_Q3 * 4 / DEBT  # 5,167 ×4 / 416,46
CIP = c.CIP_TOTAL             # XDCB đang ghi theo lõi (Phả Lại 178,0+12,7 + Vĩnh Hảo 14,8) = 205,5
RECV = 67.892070164          # BCTC HN Q3/2026 V.3 Vincons
ONEOFF = 4.763424391         # BCTC Q3 mã 31 thu nhập khác 9T (6T: thu hồi nợ đã xoá 4,65)
SH_PRE = c.SH_NOW; SH_POST = c.SH_POST; PROCEEDS = c.PROCEEDS


def mult_1stage(g_, roe, r):
    return (1 - g_ / roe) / (r - g_)


def mult_2stage(g_, roe, r, n=5):
    """Giá trị / E1: n năm tái đầu tư (1−g/ROE) tăng g, rồi terminal RONIC = Ke ⇒ giá trị tại năm n = E_{n+1}/r."""
    pv = sum((1 - g_ / roe) * (1 + g_) ** (t - 1) / (1 + r) ** t for t in range(1, n + 1))
    return pv + (1 + g_) ** n / r / (1 + r) ** n


def e_lev(branch, rev, norm):
    """LN ròng chuẩn hoá (đã trừ lãi vay thực) — KHÔNG cộng lại lãi dự án."""
    rv = c.TTM[0] if rev == "TTM" else c.E2026[0]
    m_now = c.NPM_TTM if rev == "TTM" else c.npm(*c.E2026)
    if branch == "TROUGH":
        m = c.NPM_MEAN[norm] - 0.5 * (m_now - c.NPM_MEAN[norm])
    else:
        m = m_now - c.REVERT[branch] * (m_now - c.NPM_MEAN[norm])
    return rv * m


def fn(branch, rev, norm, g, roe, r=None, frame="par", k=None, stage=2, esop2=True, cover=1.0,
       phalai_haircut=0.0, basis="post", ktpl_stock=True, recv_loss=0.0, strip_oneoff=False, debt_cancel=False,
       npm_cut=0.0, addback_perp=False):
    rr = R0 if r is None else r
    kk = K_KTPL if k is None else k
    el = e_lev(branch, rev, norm)
    rv = c.TTM[0] if rev == "TTM" else c.E2026[0]
    el -= npm_cut * rv                      # kịch bản tái đấu giá nguồn tro: biên ròng lõi giảm npm_cut điểm (ước lượng)
    if strip_oneoff:
        el -= ONEOFF * (1 - c.TAX)           # bỏ thu nhập khác 9T 4,763 tỷ khỏi E
    m = mult_2stage(g, roe, rr) if stage == 2 else mult_1stage(g, roe, rr)
    if frame in ("r3", "noadd"):   # r3: cộng lại lãi dự án, dự án ròng 0; noadd: bỏ cộng lại (skeptic r1 21.901 cum)
        add = CIP * I_REAL * (1 - c.TAX) if frame == "r3" else 0.0
        tot = (el * (1 - kk) + add) * (1 + g) * m
        if ktpl_stock:
            tot -= KTPL_BAL + kk * NP_9M
    else:                   # nợ mệnh giá
        if debt_cancel:   # cận trên: dòng cộng lại lãi chiết khấu ở chi phí nợ ⇒ đúng bằng mệnh giá nợ (nợ triệt tiêu)
            tot = el * (1 - kk) * (1 + g) * m + CASH + CIP
        else:
            if addback_perp:   # dòng cộng lại lãi: niên kim vĩnh viễn ở Ke, không tái đầu tư/không tăng trưởng
                tot = el * (1 - kk) * (1 + g) * m + DEBT * I_REAL * (1 - c.TAX) / rr - DEBT + CASH + CIP
            else:
                e_sh = el * (1 - kk) + DEBT * I_REAL * (1 - c.TAX)
                tot = e_sh * (1 + g) * m - DEBT + CASH + CIP
        if ktpl_stock:
            tot -= KTPL_BAL + kk * NP_9M
    tot -= recv_loss * RECV * (1 - c.TAX)   # lỗ phải thu Vincons (BCTC Q3 V.3 67,892 tỷ, dự phòng 0)
    tot -= phalai_haircut * c.CIP[list(c.CIP)[0]]    # kịch bản: suy giảm giá trị phần Phả Lại đã chi (190,7 tỷ)
    if basis == "cum":
        return tot * B / SH_PRE
    sh = SH_PRE + cover * c.SH_NEW + (ESOP2 if esop2 else 0)
    return (tot + cover * PROCEEDS) * B / sh


BR = {"CYCLICAL": 0.50, "ADMIN_GATED": 0.30, "STRUCTURAL": 0.20}
AX = dict(branch=[(b, b, w) for b, w in BR.items()],
          rev=[(x, x, 0.5) for x in c.GRID["rev"]],
          norm=[(x, x, 1 / 3) for x in c.GRID["norm"]],
          g=[(f"g{x:.0%}", x, 1 / 3) for x in c.GRID["g"]],
          roe=[(f"roe{x:.0%}", x, 0.5) for x in c.GRID["roe"]])
AX_TR = dict(AX, branch=[("CYCLICAL", "CYCLICAL", 0.5 - 0.2 / 3), ("ADMIN_GATED", "ADMIN_GATED", 0.3 - 0.2 / 3),
                         ("STRUCTURAL", "STRUCTURAL", 0.2 - 0.2 / 3), ("TROUGH", "TROUGH", 0.2)])


def D(axes=AX, disc="ck5ty", **kw):
    d = g.dist(g.build_grid(axes, lambda **a: fn(**a, **kw)), 0, DISC[disc])   # px=0: mù giá
    P = d["P_post"]
    return dict(center_pre=round(d["center_pre"], 1), center=round(d["center_post"], 1), p10=round(P["p10"], 1),
                p50=round(P["p50"], 1), p90=round(P["p90"], 1), n=d["n"],
                min=round(d["min_post"], 1), max=round(d["max_post"], 1))


def both(**kw):
    return {k: D(disc=k, **kw) for k in ("ck5ty", "ck40tr")}


out = dict(ticker="SCL", rev=6, blind=True, r=R0, disc=DISC,
           consts=dict(k_ktpl=K_KTPL, k_ktpl_3y=K_KTPL_3Y, dist=DIST, ktpl_bal=KTPL_BAL, np_9m=NP_9M, esop2=ESOP2,
                       cash=CASH, debt=DEBT, i_real=I_REAL, cip=CIP, tax=c.TAX, sh_pre=SH_PRE, sh_post=SH_POST,
                       sh_post_esop2=SH_POST + ESOP2, proceeds=PROCEEDS))

# ---- bridge (cơ sở sau quyền, CK 5 tỷ) ----
br = {}
br["B0_r4_control"] = D(frame="r3", k=0, stage=1, esop2=False, ktpl_stock=False)
br["B1_par_debt"] = D(frame="par", k=0, stage=1, esop2=False, ktpl_stock=False)
br["B2_ktpl"] = D(frame="par", stage=1, esop2=False)
br["B3_esop2"] = D(frame="par", stage=1, esop2=True)
br["B4_ronic_eq_ke_HEADLINE"] = D()
out["bridge_post_ck5ty"] = br
out["control_ok"] = abs(br["B0_r4_control"]["center"] - 21339.47) < 1
# chân đối chứng 2: khung nợ mệnh giá cum, k=0, một tầng phải tái lập biến thể par_debt r3 (21.673 @5 tỷ / 22.492 @40tr)
cc = dict(ck5ty=D(frame="par", k=0, stage=1, ktpl_stock=False, basis="cum", disc="ck5ty")["center"],
          ck40tr=D(frame="par", k=0, stage=1, ktpl_stock=False, basis="cum", disc="ck40tr")["center"])
out["control_par_cum"] = dict(got=cc, expect=dict(ck5ty=21673, ck40tr=22492),
                              ok=round(cc["ck5ty"]) == round(R3["alternatives"]["par_debt"]["ck5ty"]["center_post"])
                              and round(cc["ck40tr"]) == round(R3["alternatives"]["par_debt"]["ck40tr"]["center_post"]))

out["headline"] = both()
out["headline_cum"] = both(basis="cum")
out["central_param_post_ck5ty"] = fn("ADMIN_GATED", "TTM", "2023-TTM", 0.04, 0.175) * (1 - DISC["ck5ty"])

# ---- biến thể / độ nhạy (không vào base) ----
out["variants"] = dict(
    one_stage_mult=both(stage=1),
    ktpl_3y_avg=both(k=K_KTPL_3Y),
    ktpl_zero=both(k=0),
    esop2_already_in_count=both(esop2=False),
    frame_r3_addback=both(frame="r3"),
    frame_no_addback=both(frame="noadd"),
    control_skeptic_noadd_cum_r3basis=both(frame="noadd", k=0, stage=1, ktpl_stock=False, basis="cum"),
    symmetric_trough=both(axes=AX_TR),
    cover_50=both(cover=0.5),
    cover_0=both(cover=0.0),
    phalai_impair_50=both(phalai_haircut=0.5),
    phalai_impair_100=both(phalai_haircut=1.0),
    recv_loss_20=both(recv_loss=0.2), recv_loss_50=both(recv_loss=0.5), recv_loss_100=both(recv_loss=1.0),
    recv_axis_r3_UL=both(axes=dict(AX, recv_loss=[("0%", 0.0, 0.75), ("20%", 0.2, 0.2), ("50%", 0.5, 0.05)])),
    strip_oneoff=both(strip_oneoff=True),
    debt_at_cost_of_debt_upper=both(debt_cancel=True),
    addback_perpetuity_no_retention=both(addback_perp=True),
    ash_rebid_npm_minus2pt=both(npm_cut=0.02),
    ash_rebid_npm_minus4pt=both(npm_cut=0.04),
    ash_stress_trough_npm4_phalai100=both(axes=AX_TR, npm_cut=0.04, phalai_haircut=1.0),
)
out["npm_ref"] = dict(npm_ttm=c.NPM_TTM, npm_mean=c.NPM_MEAN, hist_npm={y: c.npm(*c.HIST[y]) for y in c.HIST})
out["sens_r"] = {f"{bp:+d}bp": D(r=R0 + bp / 1e4)["center"] for bp in (-100, -50, 50, 100)}
out["sens_r_beta05"] = {f"{bp:+d}bp": D(r=R0 + 0.5 * bp / 1e4)["center"] for bp in (-100, 100)}
out["ke_band_ends"] = {f"{x:.3f}": D(r=x)["center"] for x in (0.123, 0.134)}
# offering cost — không có số công bố; mỗi 0,1 tỷ chi phí = đ/cp:
out["offering_cost_per_0_1bn"] = 0.1 * B / (SH_POST + ESOP2) * (1 - DISC["ck5ty"])
# V6 hai nền (hiển thị): FCFE 9T = CFO 9,862 − capex 198,129 + vay ròng (572,894 − 486,794) — BCTC Q3 LCTT
out["v6"] = dict(cfo_9m=9.861515985, capex_9m=198.129387402, net_borrow_9m=572.893886410 - 486.794118983,
                 fcfe_9m=9.861515985 - 198.129387402 + (572.893886410 - 486.794118983))

s = json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True, default=str)
open(os.path.join(HERE, "calc_rev6_out.json"), "w").write(s)
print(s[:200]); print("md5", hashlib.md5(s.encode()).hexdigest())
