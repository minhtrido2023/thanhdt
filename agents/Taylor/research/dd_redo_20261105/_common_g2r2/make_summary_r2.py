"""SUMMARY.json vòng 2 = model_<t>_r2_out.json (số) + meta_r2.json (văn bản) + SUMMARY_r1.json (mốc so sánh). 0 số gõ tay.
Lần đầu chạy: sao lưu SUMMARY.json vòng 1 thành SUMMARY_r1.json (không ghi đè nếu đã có).
Chạy: $DNA_PYEXE -I make_summary_r2.py <MÃ>"""
import json, os, shutil, sys
T = sys.argv[1]
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", T)
r1p = os.path.join(D, "SUMMARY_r1.json")
if not os.path.exists(r1p):
    shutil.copyfile(os.path.join(D, "SUMMARY.json"), r1p)
R1 = json.load(open(r1p))
M = json.load(open(os.path.join(D, "calc", f"model_{T.lower()}_r2_out.json")))
meta = json.load(open(os.path.join(D, "meta_r2.json")))
Dd, L = M["dist"], M["liq"]
P, Pp = Dd["P_post"], Dd["P_pre"]
px = M["price"]
S = dict(ticker=T, round=2, job="Taylor_20261105_020018", asof_price_date=M["asof_price_date"], price=px, r=M["r"],
         r_anchor=dict(rate=M["r_info"]["anchor"]["rate"], date=M["r_info"]["anchor"]["date"],
                       current_rate=M["r_info"]["current"]["rate"], current_source=M["r_info"]["current"]["source"]),
         center_pre_liq=round(Dd["center_pre"]), center_post_liq=round(Dd["center_post"]),
         p10_post=round(P["p10"]), p50_post=round(P["p50"]), p90_post=round(P["p90"]),
         p10_pre=round(Pp["p10"]), p90_pre=round(Pp["p90"]),
         p10_out=round(P["p10"]), p50_out=round(P["p50"]), p90_out=round(P["p90"]),
         min_out=round(Dd["min_post"]), max_out=round(Dd["max_post"]),
         pct_weight_below_price=round(Dd["pct_w_below_px"], 4), n_outcomes=Dd["n"],
         center_param_post=round(M["center_param_post"]),
         liq_discount_ref=round(L["ref_discount"], 4), liq_ref_size_ty=L["ref_size_ty"],
         ck_ref_size=dict(size_ty=L["ref_size_ty"], discount_adv120=round(L["ref_discount"], 4),
                          discount_adv250=round(L["ref_discount_adv250"], 4), discount_adv60=round(L["ref_discount_adv60"], 4),
                          pct_adv120=round(L["ref_pct_adv120"], 3), in_sqrt_calibration_zone=L["ref_in_sqrt_zone"]),
         ck_real_sleeve={k: round(v, 4) for k, v in L["sleeve_discount"].items()},
         adv250_median_ty=round(L["adv250_med_ty"], 2), adv120_median_ty=round(L["adv120_med_ty"], 2), adv60_median_ty=round(L["adv60_med_ty"], 2),
         px_vs_center=round(px / Dd["center_post"] - 1, 4), px_vs_p10=round(px / P["p10"] - 1, 4), px_vs_p90=round(px / P["p90"] - 1, 4),
         grid_desc=meta["grid_desc"] + f" (n={Dd['n']})", label=M["label"], label_note=meta["label_note"],
         center_vs_p50_note=meta["center_vs_p50_note"],
         axes_included=M["axes_included"], axes_excluded=M["axes_excluded"], base_adjustments=M["base_adjustments"],
         parallel={k: dict(center_post=round(v["center_post"]), p10_post=round(v["P_post"]["p10"]), p50_post=round(v["P_post"]["p50"]),
                           p90_post=round(v["P_post"]["p90"]), pct_weight_below_price=round(v["pct_w_below_px"], 4)) for k, v in M["parallel"].items()},
         gordon=M["gordon"],
         zone_old=dict(round=1, center_post_liq=R1["center_post_liq"], p10_post=R1["p10_post"], p50_post=R1.get("p50_post"),
                       p90_post=R1["p90_post"], label=R1["label"], grid=R1["grid_desc"]),
         center_new_vs_old=round(Dd["center_post"] / R1["center_post_liq"] - 1, 4),
         change_reason=meta["change_reason"], warnings=meta["warnings"], open_issues=meta["open_issues"],
         fearbuy_sleeve_eligible=meta["fearbuy_sleeve_eligible"],
         source_calc=f"calc/model_{T.lower()}_r2_out.json", lock=f"calc/LOCK_r2_md5.txt")
if "dist_post_rights" in M:
    Dp = M["dist_post_rights"]
    S["price_basis"] = M["price_basis"]
    S["post_rights"] = dict(terp=round(M["terp"]), center_post_liq=round(Dp["center_post"]), p10_post=round(Dp["P_post"]["p10"]),
                            p50_post=round(Dp["P_post"]["p50"]), p90_post=round(Dp["P_post"]["p90"]),
                            terp_vs_center=round(M["terp"] / Dp["center_post"] - 1, 4), label_terp=M["label_terp"])
json.dump(S, open(os.path.join(D, "SUMMARY.json"), "w"), ensure_ascii=False, indent=1)
print(T, S["center_post_liq"], S["p10_out"], S["p50_out"], S["p90_out"], S["label"], S["center_new_vs_old"])
