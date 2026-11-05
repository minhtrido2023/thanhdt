"""SUMMARY.json = model_*_out.json (số) + meta.json (văn bản: grid_desc, change_reason, warnings, open_issues). 0 số gõ tay.
Chạy: $DNA_PYEXE -I make_summary.py <MÃ>"""
import json, os, sys, glob
T = sys.argv[1]
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", T)
M = json.load(open(os.path.join(D, "calc", f"model_{T.lower()}_out.json")))
meta = json.load(open(os.path.join(D, "meta.json")))
S = dict(ticker=T, asof_price_date=M["asof_price_date"], price=M["price"], r=M["r"],
         r_anchor=dict(rate=M["r_info"]["anchor"]["rate"], date=M["r_info"]["anchor"]["date"],
                       current_rate=M["r_info"]["current"]["rate"], current_source=M["r_info"]["current"]["source"]),
         center_pre_liq=round(M["center_pre_liq"]), center_post_liq=round(M["center_post_liq"]),
         p10_post=round(M["P_post"]["p10"]), p50_post=round(M["P_post"]["p50"]), p90_post=round(M["P_post"]["p90"]),
         p10_pre=round(M["P_pre"]["p10"]), p90_pre=round(M["P_pre"]["p90"]),
         liq_discount_ref=round(M["liq"]["ref_discount"], 4), liq_ref_size_ty=M["liq"]["ref_size_ty"],
         adv120_median_ty=round(M["liq"]["adv120_med_ty"], 2),
         px_vs_center=round(M["px_vs_center"], 4), px_vs_p10=round(M["px_vs_p10"], 4), px_vs_p90=round(M["px_vs_p90"], 4),
         grid_desc=meta["grid_desc"] + f" (n={M['grid_n']})", label=M["label"],
         zone_old=M["zone_old"], center_new_vs_old=round(M["center_vs_old"], 4),
         change_reason=meta["change_reason"], warnings=meta["warnings"], open_issues=meta["open_issues"],
         source_calc=os.path.relpath(os.path.join(D, "calc", f"model_{T.lower()}_out.json"), D))
if "post_rights" in M:
    pr = M["post_rights"]
    S["post_rights"] = dict(terp=round(M["terp"]), center_post_liq=round(pr["center_post_liq"]),
                            p10_post=round(pr["P_post"]["p10"]), p90_post=round(pr["P_post"]["p90"]),
                            terp_vs_center=round(pr["terp_vs_center"], 4), label_terp=pr["label_terp"])
    S["price_basis"] = M["price_basis"]
json.dump(S, open(os.path.join(D, "SUMMARY.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(S, ensure_ascii=False)[:600])
