"""Bước SAU khoá (LOCK_prerun.txt): gắn nhãn theo giá 10/11 + độ nhạy phụ + SUMMARY.json."""
import json, hashlib, os, subprocess, sys
H = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(H, "model_out_r2.json")))
A = json.load(open(os.path.join(H, "assumptions_r2.json")))
PX, PX_DATE = 19300.0, "2026-11-10"   # px_vgs.csv (tav2_bq.ticker Price), lấy SAU khoá
SH = A["shares_m"]

def label(px, p10, p90):
    return "DUOI vung" if px < p10 else ("TREN vung" if px > p90 else "TRONG vung")

by_size = {}
for k, v in M["liq"].items():
    thr = v["center_post"] * 0.85
    by_size[k] = dict(center=round(v["center_post"]), p10=round(v["p10_post"]), p90=round(v["p90_post"]),
                      label=label(PX, v["p10_post"], v["p90_post"]), ck=v["ck_adv250"], ck_adv60=v["ck_adv60"],
                      rule4_threshold=round(thr), rule4_pass=PX <= thr)

# độ nhạy phụ (không đổi headline)
core_b, as_b, lg_b = M["core"]["base"]["val_bn"], M["assoc"]["base"]["val_bn"], M["lgc"]["base"]["val_bn"]
nc = M["net_cash_bn"]
holding30 = M["center"] - 0.30 * (as_b + lg_b) / SH * 1000 * 1.0
core_only = (core_b + nc) / SH * 1000
# r ngầm định bởi giá (base-case cả 3 khối, CK 5 tỷ bỏ qua): giải PX = (NPcore/r + assoc_avg/r + lgc + nc)/SH
npc = M["core"]["base"]["np_bn"]; asavg = sum(A["associate_scenarios"]["base"]["earn"]) / 3
r_impl = (npc + asavg) / (PX * SH / 1000 - lg_b - nc)
norm_np = npc + asavg
S = dict(
    ticker="VGS", asof_price_date=PX_DATE, price=PX, r=M["r"],
    r_anchor=dict(r=0.135, rate=0.074, source="cctg_12m(2026-11-02)", rule="r = 13,5% + 1,0 x (dep_12T - 7,40%)"),
    kind="expected_weighted_sotp", center_pre_liq=round(M["center"]), center_post_liq=by_size["1.0ty"]["center"],
    p10_post=by_size["1.0ty"]["p10"], p90_post=by_size["1.0ty"]["p90"],
    p10_pre=round(M["p10"]), p50_pre=round(M["p50"]), p90_pre=round(M["p90"]),
    px_vs_center_post=PX / by_size["1.0ty"]["center"] - 1, px_vs_p10_post=PX / by_size["1.0ty"]["p10"] - 1,
    label=by_size["1.0ty"]["label"], label_by_size=by_size,
    sens_r2={k: round(v) for k, v in M["sens_r2"].items()}, sens_r_center_pre={k: round(v) for k, v in M["sens_r"].items()},
    sens_r_beta05_center_pre={k: round(v) for k, v in M["sens_beta05"].items()},
    sens_other=dict(holding_discount_30pct_on_assoc_lgc=round(holding30), core_only_plus_netcash=round(core_only),
                    moat="NONE -> khong co tham so moat; NARROW/WIDE khong doi headline (khong thuong khi chua ben)"),
    implied_by_price=dict(r_all_base=round(r_impl, 4), note="r lam tam base (khong CK) = gia 19.300"),
    normalized=dict(np_core_base=round(npc, 1), np_assoc_avg3=round(asavg, 1), np_total=round(norm_np, 1),
                    eps_norm=round(norm_np / SH * 1000), pe_center_norm=round(M["center"] / (norm_np / SH * 1000), 1),
                    pe_price_norm=round(PX / (norm_np / SH * 1000), 1), pe_price_ttm=round(PX / M["ttm"]["eps"], 2),
                    pb_price=round(PX / M["bvps"], 2), bvps=round(M["bvps"])),
    sotp_base_vps=dict(core=round(M["core"]["base"]["vps"]), assoc=round(M["assoc"]["base"]["vps"]),
                       legend_city=round(M["lgc"]["base"]["vps"]), net_cash=round(M["net_cash_vps"])),
    grid_desc="r2: 18 ket cuc = LN loi XAU/CO_SO/TOT 56,0/129,4/179,2 ty (0,25/0,5/0,25) x lien ket 0,7xso sach/EPV TB3/TTMx5 (0,25/0,5/0,25) x Legend City gia goc x0,7/x1,0 (0,3/0,7); RONIC=Ke g=0; + no rong -33,3 ty",
    moat=dict(tier="NONE", type="SCALE/DISTRIBUTION (khong ben)", source="lam moi 10/11/2026 (moat_tags.csv chua co VGS)", durable=False,
              roic5y=0.087, roic_min5y=0.057, roe_min3y=0.061),
    warnings=["Ca BKS 3 nguoi tu nhiem 15/09/2025 (NQ DHDCD bat thuong 07/11/2025)",
              "Co tuc tu lien ket 26,6 ty ghi DT tai chinh 2025 trong khi gia tri lien ket van cong du phan lai 43,6 ty -> nghi dem 2 lan (chi 2025)",
              "Phai thu 2 khach 481 ty = 74% phai thu KH 30/09 (01/01: 77 ty); Dien Xanh Chau A vua la khach (196,7) vua la NCC (198,5)",
              "TM 33 ben lien quan khong ke giao dich mua/ban voi lien ket Tap doan SX thep Viet Duc",
              "Legend City: QD chu truong 2010, GPMB GD1 chua xong; BCC 50:50 Vinaconex 498,7 ty"],
    assumptions_file="calc/assumptions_r2.json", round=2, headline_size_bn=1.0, label_fragile=True,
    assumptions_md5=hashlib.md5(open(os.path.join(H, "assumptions_r2.json"), "rb").read()).hexdigest(),
    model_md5=hashlib.md5(open(os.path.join(H, "model_r2.py"), "rb").read()).hexdigest(),
    source_file="src/BCTC-Q3-HN.pdf", source_md5=hashlib.md5(open(os.path.join(H, "..", "src", "BCTC-Q3-HN.pdf"), "rb").read()).hexdigest(),
    lock="calc/LOCK_r2_prerun.txt (khoa truoc khi chay lai; gia chi dung sau khoa)",
    sector_read="kb/data_registry/market-state/sector_read_thep_20261031.md", job="Taylor_20261110_131720",
    fear_buy_eligible_2_5=None)
json.dump(S, open(os.path.join(H, "..", "SUMMARY.json"), "w"), indent=1, ensure_ascii=False)
# bo sung: lien ket moi kich ban = 0,75 x so sach
import math
asc = A["bs_20260930"]["associate_carrying"]; w=A["associate_scenarios"]
allpb = M["center"] - (sum(M["assoc"][k]["val_bn"]*wt for k, wt in (("bear",.25),("base",.5),("bull",.25))) - asc*0.75)/SH*1000
S["sens_r2"]["assoc_all_scen_pb075"] = round(allpb)
S["sens_r2_post_ck_1ty"] = {k: round(v*(1-M["liq"]["1.0ty"]["ck_adv250"])) for k, v in M["sens_r2"].items()}
S["sens_r2_post_ck_1ty"]["assoc_all_scen_pb075"] = round(allpb*(1-M["liq"]["1.0ty"]["ck_adv250"]))
S["px_vs_center_post"] = PX / by_size["1.0ty"]["center"] - 1
json.dump(S, open(os.path.join(H, "..", "SUMMARY.json"), "w"), indent=1, ensure_ascii=False)
print(S["sens_r2"], S["sens_r2_post_ck_1ty"], S["px_vs_center_post"], S["px_vs_p10_post"])
print(json.dumps({k: S[k] for k in ["center_pre_liq", "center_post_liq", "p10_post", "p90_post", "label", "sens_other", "implied_by_price", "normalized", "sotp_base_vps", "assumptions_md5", "source_md5"]}, indent=1, ensure_ascii=False))
print({k: (v["label"], v["rule4_threshold"], v["rule4_pass"]) for k, v in by_size.items()})
