"""Pha SAU KHOÁ rev5: so giá. Giá BQ tav2_bq.ticker HHS 2026-11-20 Price=9.700 (ADV60 trung vị 10,35 tỷ; ADV250 TB 21,34 tỷ)."""
import json, os
H = os.path.dirname(os.path.abspath(__file__)); o = json.load(open(f"{H}/calc_rev5_out.json"))
PX = 9700; OFF = 10000
terp = (PX + 0.6 * OFF) / 1.6; terp_div = terp / 1.07; div_only = PX / 1.07
R = o["rows"]; P = o["pre"]
res = dict(px=PX, px_date="2026-11-20", terp_rights=round(terp), terp_div=round(terp_div), px_div_only=round(div_only), right_value_per_new=PX - OFF,
           adv60_med_bn=10.35, adv250_mean_bn=21.34, size5bn_pct_adv60=round(5/10.35, 3), size5bn_pct_adv250=round(5/21.34, 3))
def lab(px, z): return "DƯỚI vùng" if px < z["p10"] else ("TRÊN vùng" if px > z["p90"] else "TRONG vùng")
res["cum_headline"] = dict(**P["HEADLINE_CK0"], label=lab(PX, P["HEADLINE_CK0"]), rule4=PX <= 0.85 * P["HEADLINE_CK0"]["center"], px_vs_center=round(PX / P["HEADLINE_CK0"]["center"] - 1, 4))
res["cum_ck27"] = dict(**P["SONGSONG_CK27"], label=lab(PX, P["SONGSONG_CK27"]), rule4=PX <= 0.85 * P["SONGSONG_CK27"]["center"], px_vs_center=round(PX / P["SONGSONG_CK27"]["center"] - 1, 4))
for k in ("HEADLINE_CK0|du_100|k=1.0", "HEADLINE_CK0|du_100|k=0.8", "HEADLINE_CK0|chi_TCH|k=1.0", "HEADLINE_CK0|chi_TCH|k=0.8", "SONGSONG_CK27|du_100|k=0.73"):
    z = R[k]; res[k] = dict(center=z["center"], p10=z["p10"], p90=z["p90"], label_vs_terp=lab(terp_div, z), rule4=terp_div <= z["rule4_thr"], terp_vs_center=round(terp_div / z["center"] - 1, 4))
z = R["HEADLINE_CK0|khong_phat_hanh|k=1.0"]; res["no_rights"] = dict(center=z["center"], label=lab(div_only, z))
# điểm hoà vốn k luật 4 (EX đủ): tuyến tính giữa k=0,8 và 1,0
c08, c10 = R["HEADLINE_CK0|du_100|k=0.8"]["center"], R["HEADLINE_CK0|du_100|k=1.0"]["center"]
need = terp_div / 0.85; res["rule4_breakeven_k_ex"] = round(0.8 + (need - c08) / (c10 - c08) * 0.2, 3)
json.dump(res, open(f"{H}/post_lock_out.json", "w"), ensure_ascii=False, indent=1); print(json.dumps(res, ensure_ascii=False, indent=1))
