"""SUMMARY.json vòng 3 TV2 — sinh từ calc_r3/model_tv2_r3_out.json + SUMMARY_r2.json (giữ warnings). Chạy: $DNA_PYEXE -I make_summary_r3.py"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); TD = os.path.dirname(HERE)
o = json.load(open(os.path.join(HERE, "model_tv2_r3_out.json"))); s2 = json.load(open(os.path.join(TD, "SUMMARY_r2.json")))
D = o["dist"]; P = D["P_post"]; L = o["liq"]; px = o["price"]; dc = o["data_checks"]; par = o["parallel"]; imp = o["implied"]
R = lambda x: int(round(x))
vn = lambda x: f"{x:,.0f}".replace(",", ".")
def b(k):
    v = par[k]; return dict(center=R(v["center"]), p10=R(v["p10"]), p50=R(v["p50"]), p90=R(v["p90"]), pct_below=round(v["below"], 3), **({"label": v["label"]} if "label" in v else {}))
S = dict(
    ticker="TV2", round=3, job="Taylor_20261108_142016", asof_price_date=o["asof_price_date"], price=px, r=o["r"], r_anchor=o["r_info"]["r_anchor"],
    center_pre_liq=R(D["center_pre"]), center_post_liq=R(D["center_post"]),
    p10_post=R(P["p10"]), p50_post=R(P["p50"]), p90_post=R(P["p90"]), p10_out=R(P["p10"]), p50_out=R(P["p50"]), p90_out=R(P["p90"]),
    p10_pre=R(D["P_pre"]["p10"]), p90_pre=R(D["P_pre"]["p90"]), min_out=R(D["min_post"]), max_out=R(D["max_post"]),
    pct_weight_below_price=round(D["pct_w_below_px"], 3), n_outcomes=D["n"], center_param_post=R(o["center_param_post"]),
    liq_discount_ref=round(L["ref_discount"], 4), liq_ref_size_ty=5.0,
    ck_ref_size=dict(size_ty=5.0, discount_adv120=round(L["ref_discount"], 4), discount_adv250=round(L["ref_discount_adv250"], 4),
                     discount_adv60=round(L["ref_discount_adv60"], 4), pct_adv120=round(L["ref_pct_adv120"], 3), in_sqrt_calibration_zone=L["ref_in_sqrt_zone"]),
    ck_real_sleeve={k: round(v, 4) for k, v in L["sleeve_discount"].items()}, center_real_sleeve_40tr=R(o["sleeve_center"]),
    adv250_median_ty=round(L["adv250_med_ty"], 2), adv120_median_ty=round(L["adv120_med_ty"], 2), adv60_median_ty=round(L["adv60_med_ty"], 2),
    px_vs_center=round(px / D["center_post"] - 1, 3), px_vs_p10=round(px / P["p10"] - 1, 3), px_vs_p90=round(px / P["p90"] - 1, 3),
    pct_below_price_of_center=round(1 - D["center_post"] / px, 3),
    grid_desc="5 trục: LNST bền 2027–28 kịch bản 250/177,5/110 tỷ (0,25/0,5/0,25) × ×0,9/1/1,1 × g 3/4/5% × mất phơi nhiễm CMC 855,012 tỷ 0/15/30/50% sau thuế (0,45/0,30/0,15/0,10) × độ bền LN sau 2028: sập về MỨC đáy quan sát 64,3 tỷ (TB LNST TTM 2023Q1–25Q3) / bền / +30% (0,25/0,5/0,25); P/E nội tại (1−g/ROE)/(r−g) khi ROE ≥ r, = 1/r (trả hết) khi ROE < r; vốn chủ sàn 0; phân vị wpct mức kết cục (n=324)",
    label=o["label"],
    label_note=f"TRONG vùng (giá {vn(px)} < P90 {vn(P['p90'])}, {(px/P['p90']-1)*100:+.1f}%) — MONG MANH: P90 do nhánh tích cực (84% trọng số quanh P90, w 0,25); {D['pct_w_below_px']*100:.1f}% trọng số kết cục dưới giá; giá > P75 ({vn(P['p75'])}). Hai biến thể song song ra TRÊN vùng: C (P/E 1/r mọi nhánh, P90 {vn(par['C_pe_1_over_r_all']['p90'])}) và trần P/E 7,45x (P90 {vn(par['cap_pe_745']['p90'])}). Điều 7: theo định nghĩa vùng v3 01/11 (17.100–25.300) giá TRÊN vùng.".replace("10.7%", "10,7%").replace("84.1%", "84,1%"),
    center_vs_p50_note=f"Tâm {R(D['center_post'])} > P50 {R(P['p50'])} (lệch phải do nhánh tích cực/+30%); tham số trung tâm (177,5|g4|CMC0|bền) {R(o['center_param_post'])}. P10 do nhánh tiêu cực + sập (sập 85% quanh P10); P90 do nhánh tích cực.",
    assumptions=[
        dict(item="r = 13,5% + 1,0×(CCTG 12T hiệu dụng − 7,40%)", value=o["r"], basis=f"luật 03/11; hiện hành {o['r_info']['current']['rate']}% ({o['r_info']['current']['source']})"),
        dict(item="VCSH mẹ 1.330,8 tỷ; N 67,526 triệu cp", value=None, basis="BCTC HN Q3/2026 (BVPS 19.708)"),
        dict(item="Phơi nhiễm CMC 855,012 tỷ = phải thu 666,374 + đầu tư LK ghi sổ 188,638", value=855.012, basis="BCTC HN Q3/2026 TM32.c tr.36/38 & TM2a tr.16/38 — đọc lại bằng PyMuPDF render 08/11; TM3 tr.18/38 ghi 657,327 (lệch 9,0 tỷ chưa giải); không dự phòng"),
        dict(item="P/E = 1/r khi ROE < r (trả hết LN)", value=round(1 / o["r"], 2), basis=f"tỷ lệ chi trả DY/EY 2022Q4–25Q3 {min(dc['payout_2022Q4_2025Q3'].values()):.2f}–{max(dc['payout_2022Q4_2025Q3'].values()):.2f} (BQ ticker_financial); phải trả cổ tức 67,97 tỷ 30/09/2026 (TM14)"),
        dict(item="Nhánh sập neo mức 64,3 tỷ", value=round(dc["trough_mean"], 1), basis=f"TB LNST TTM 2023Q1–25Q3 (BQ), min {dc['trough_min']:.1f} max {dc['trough_max']:.1f}"),
        dict(item="Kịch bản LNST 250/177,5/110, trọng số 25/50/25", value=None, basis="[UL] DD v3 01/11 (không có dữ liệu mới); độ nhạy 30/50/20 & 20/50/30"),
        dict(item="Xác suất CMC 0/15/30/50% = 0,45/0,30/0,15/0,10", value=None, basis="[UL]; cơ sở chiều xuống: không dự phòng, thu tiền Q3≈0, Tân Thuận GĐ3 chưa COD"),
        dict(item="Độ bền sau 2028 sập/bền/+30% = 0,25/0,5/0,25", value=None, basis="[UL]; base rate đỉnh 2017–21 → đáy 2022–25 (SKEPTIC CAO-1)"),
        dict(item="g 3/4/5%", value=None, basis="ước lượng, đều"),
        dict(item="CK thanh khoản @5 tỷ", value=round(L["ref_discount"], 4), basis="nửa spread CS 120 phiên + σ√(Q/ADV120), Y=1; ngoài vùng hiệu chỉnh √ (Q/ADV 155%)"),
        dict(item="Không thưởng moat", value=None, basis="5F 07–08/11: moat NONE; user 08/11 10:50 — moat chỉ cộng khi bền, không trừ"),
    ],
    headline_vs_alternatives=dict(
        headline="B = r2 + Đ1 (P/E 1/r khi ROE<r) + Đ2 (sập neo mức đáy 64,3)",
        why="Đ1 và Đ2 đều có dòng cơ sở dữ liệu (chi trả 2022Q4–25Q3; đáy LNST TTM 2023–25). C (P/E 1/r mọi nhánh = RONIC=r) là bản chặt-3c mà user 08/11 chỉ cho làm độ nhạy (moat NONE ⇒ không thưởng, không trừ — nhưng giữ mô hình cơ sở). Trần P/E thị trường 2017–21 không vào base: P/E thị trường pha đỉnh đã chiết khấu kỳ vọng LN sập, mô hình đã có trục độ bền ⇒ áp trần là đếm hai lần; báo song song.",
        A_payout_only=b("A_payout_only"), C_pe_1_over_r_all=b("C_pe_1_over_r_all"), cap_pe_745=b("cap_pe_745"),
        cap_pe_peak_median_709=b("cap_pe_peak_median"), trough_53=b("trough_min"), trough_74_6=b("trough_max"),
        w_30_50_20=b("w_30_50_20"), w_20_50_30=b("w_20_50_30"), no_persist_axis=b("no_persist_axis"),
        sens_r={k: R(v["post"]) for k, v in o["sens_r"].items()}),
    implied_by_price=dict(np_perpetual_ty=round(imp["np_perp"], 1), roe=round(imp["roe"], 3), pe=round(imp["pe"], 2), float_interest_part_ty=round(imp["float_part"], 1),
                          np_with_expected_cmc_loss_ty=round(imp["np_perp_with_expected_cmc_loss"], 1), np_if_pe_1_over_r_ty=round(imp["np_perp_if_pe_1_over_r"], 1),
                          note="Giá 27.400 cần LNST ~234–256 tỷ VĨNH VIỄN (g 4%, ROE 17,5–19,3%), ~44% là lãi float trên tiền khách ứng, CMC không mất đồng nào (243 nếu tính mất CMC kỳ vọng). Đối chiếu: LNST TTM 2026Q3 211,1; đỉnh TTM 2017–21 317,8; TB đáy 2023–25 64,3."),
    bridge_r2_to_r3=[dict(step=x["step"], center=R(x["center"]), p10=R(x["p10"]), p90=R(x["p90"])) for x in o["bridge"]],
    bridge_history=[
        dict(round="v3 01/11", center=20700, note="tâm vùng cơ sở 21.000 (dải 17.100–25.300); kỳ vọng 25/50/25 = 20.700; P/E gán tay 7–9x neo P/E thị trường pha đỉnh 7,45x; chưa CK"),
        dict(round="r1 05/11", center=18784, note="P/E nội tại từ r 13,5% và ROE (tiêu cực 5,43x thay 7–8x ⇒ nhánh tiêu cực 11.000→7.665) + CK 2,52% (−486)"),
        dict(round="r2 05/11", center=15832, note="CMC thành trục độc lập mọi kịch bản (kỳ vọng mất 14% ⇒ ≈−1.418) + trục độ bền sập 70% (tỷ lệ) với sàn P/E 0 khi ROE<g"),
        dict(round="r3 08/11", center=R(D["center_post"]), note="bỏ sàn P/E 0 (Đ1, +1.436) + sập neo mức đáy quan sát (Đ2, +221); giá/CK 06/11 & CMC 188,638 ~0"),
    ],
    axes_included=["kịch bản LNST bền 2027–28", "hệ số LNST", "g", "mất phơi nhiễm CMC", "độ bền LN sau 2028 (sập neo mức đáy/bền/+30%)"],
    axes_excluded=s2["axes_excluded"],
    base_adjustments=[dict(item="không có điều chỉnh khỏi sổ sách ở tham số trung tâm", effect_dong_per_share=0.0, basis="CMC theo sổ (0%) ở tham số trung tâm; mọi lệch nằm ở trục có xác suất", source="BCTC HN Q3/2026"),
                      dict(item="P/E 1/r khi ROE<r (thay sàn 0)", effect_dong_per_share=R(o["bridge"][3]["center"] - o["bridge"][2]["center"]), basis="chi trả ~100% LN 2022Q4–25Q3", source="BQ ticker_financial DY/EPS; BCTC Q3 TM14"),
                      dict(item="nhánh sập neo mức đáy 64,3 tỷ", effect_dong_per_share=R(o["bridge"][4]["center"] - o["bridge"][3]["center"]), basis="TB LNST TTM 2023Q1–25Q3", source="BQ ticker_financial")],
    data_checks=dc, gordon=o["gordon"],
    zone_old=dict(round=2, center_post_liq=s2["center_post_liq"], p10_post=s2["p10_post"], p50_post=s2["p50_post"], p90_post=s2["p90_post"], label=s2["label"], price=s2["price"], asof=s2["asof_price_date"]),
    center_new_vs_old=round(D["center_post"] / s2["center_post_liq"] - 1, 3),
    change_reason="Áp đính chính skeptic 08/11 có cơ sở dữ liệu: Đ1 bỏ sàn P/E 0 (P10 artifact 2.726 → 6.319) và Đ2 neo nhánh sập ở mức đáy quan sát (P10 → 7.702). Tâm 15.832 → 17.491 (+10,5%). Nhãn giữ TRONG (mong manh). Đính chính 3 (trần P/E 7,45x) không vào base — báo song song (ra TRÊN vùng).",
    warnings=s2["warnings"],
    open_issues=["Lệch số dư phải thu CMC TM3 657,327 vs TM32.c 666,374 (9,0 tỷ) chưa giải", "Giá trị HĐ EPC không công bố", "Xác suất CMC/độ bền/trọng số [UL]", "Danh sách 13 pháp nhân (họp báo 02/07) chưa có", "P10 7.702 ứng P/B 0,39 — vẫn dưới P/B thấp nhất quan sát (0,92 từ 2014) do đuôi CMC mất 50% + sập"],
    fearbuy_sleeve_eligible="KHÔNG — giá cao hơn tâm 57%, không phải trạng thái sợ hãi; vụ án chưa kết luận",
    hard_abandon=["khởi tố pháp nhân TV2", "TV2 có tên trong 13 pháp nhân", "CMC trích lập > 30% phơi nhiễm", "kiểm toán FY2026 ngoại trừ"],
    source_calc="calc_r3/model_tv2_r3_out.json", lock="calc_r3/LOCK_r3_md5.txt", report="REPORT_r3.md",
)
json.dump(S, open(os.path.join(TD, "SUMMARY.json"), "w"), ensure_ascii=False, indent=1)
print("ok", S["center_post_liq"], S["p10_out"], S["p90_out"], S["label"])
