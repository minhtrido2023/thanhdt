"""Bước SAU khoá md5 (LOCK_md5_r2.txt): thanh khoản (phương pháp đăng ký trước trong model_r3_out.json) + so giá 03/11/2026.
Nguồn: px_scl.csv = tav2_bq.ticker SCL (time, OHLC, Price, Volume) từ 2025-10-01; đóng cửa 03/11/2026 cum-quyền."""
import csv, json, math, os, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(HERE, "model_r3_out.json")))
rows = [r for r in csv.DictReader(open(os.path.join(HERE, "px_scl.csv")))]
for r in rows:
    for k in ("Open", "High", "Low", "Close", "Price", "Volume"):
        r[k] = float(r[k])
N = 120
win = rows[-N:]
val = [r["Price"] * r["Volume"] for r in win]              # giá trị GD ≈ giá chưa điều chỉnh × KL (VND)
adv_med, adv_mean = st.median(val), st.mean(val)
adv60_med = st.median([r["Price"] * r["Volume"] for r in rows[-60:]])
rets = [math.log(win[i]["Close"] / win[i - 1]["Close"]) for i in range(1, len(win))]
sigma = st.pstdev(rets)
# Corwin-Schultz (2012) spread từ High/Low 2 ngày liên tiếp (giá điều chỉnh)
cs = []
for a, b in zip(win[:-1], win[1:]):
    beta = math.log(a["High"] / a["Low"]) ** 2 + math.log(b["High"] / b["Low"]) ** 2
    gam = math.log(max(a["High"], b["High"]) / min(a["Low"], b["Low"])) ** 2
    k = 3 - 2 * math.sqrt(2)
    alpha = (math.sqrt(2 * beta) - math.sqrt(beta)) / k - math.sqrt(gam / k)
    s = 2 * (math.exp(alpha) - 1) / (1 + math.exp(alpha))
    cs.append(max(s, 0.0))
spread = st.mean(cs)
amihud = st.mean([abs(r_) / v for r_, v in zip(rets, val[1:]) if v > 0])   # |r| trên 1 VND
zero_days = sum(1 for r in win if r["Volume"] == 0)

sizes = [1e9, 5e9, 10e9]
liq = []
for q in sizes:
    d = dict(size_ty=q / 1e9, pct_adv=q / adv_med,
             days_p10=q / (0.10 * adv_med), days_p20=q / (0.20 * adv_med),
             impact_y05=0.5 * sigma * math.sqrt(q / adv_med), impact_y10=1.0 * sigma * math.sqrt(q / adv_med),
             half_spread=spread / 2, amihud_linear=min(amihud * q, 1.0))
    d["discount"] = d["half_spread"] + d["impact_y10"]             # đăng ký trước: Y=1
    d["discount_low"] = d["half_spread"] + d["impact_y05"]
    liq.append(d)

PX_CUM = rows[-1]["Close"]; PX_DATE = rows[-1]["time"]
TERP = (PX_CUM + 0.154453 * 12_500) / 1.154453
ref = liq[1]["discount"]   # quy ước fleet: tham chiếu 5 tỷ
P = {k: v * (1 - ref) for k, v in M["pct_post"].items()}
PC = {k: v * (1 - ref) for k, v in M["pct_cum"].items()}
tam_post_liq = M["tam_post"] * (1 - ref); tam_cum_liq = M["tam_cum"] * (1 - ref)


def label(px, p):
    if px <= p["10"]:
        return "RẺ có biên an toàn (≤ P10)"
    if px < p["25"]:
        return "DƯỚI vùng hợp lý (P10–P25)"
    if px <= p["75"]:
        return "TRONG vùng hợp lý (P25–P75)"
    return "TRÊN vùng hợp lý (> P75)"


out = dict(px_cum=PX_CUM, px_date=PX_DATE, terp=TERP, right_value_per_old_share=(TERP - 12_500) * 0.154453,
           adv120_med=adv_med, adv120_mean=adv_mean, adv60_med=adv60_med, sigma_d=sigma, cs_spread=spread,
           amihud_per_ty=amihud * 1e9, zero_vol_days=zero_days, n_sessions=len(win), liq=liq, ref_discount=ref,
           tam_post=M["tam_post"], tam_cum=M["tam_cum"], tam_post_liq=tam_post_liq, tam_cum_liq=tam_cum_liq,
           pct_post_liq=P, pct_cum_liq=PC,
           label_cum=label(PX_CUM, PC), label_terp=label(TERP, P),
           label_cum_before_liq=label(PX_CUM, M["pct_cum"]), label_terp_before_liq=label(TERP, M["pct_post"]),
           px_vs_tam_cum_liq=PX_CUM / tam_cum_liq - 1, terp_vs_tam_post_liq=TERP / tam_post_liq - 1,
           old_center_post=25_500, new_vs_old=M["tam_post"] / 25_500 - 1,
           par_lower_post_liq=M["par_debt_lower_bound"]["v_post"] * (1 - ref), par_lower_cum_liq=M["par_debt_lower_bound"]["v_cum"] * (1 - ref),
           par_pct_post_liq={k: v * (1 - ref) for k, v in M["par_debt_lower_bound"]["pct_post"].items()})
json.dump(out, open(os.path.join(HERE, "compare_r3_out.json"), "w"), ensure_ascii=False, indent=1)
with open(os.path.join(HERE, "compare_r3_out.txt"), "w") as f:
    for k, v in out.items():
        f.write(f"{k}: {json.dumps(v, ensure_ascii=False) if not isinstance(v, float) else round(v, 4)}\n")
print(open(os.path.join(HERE, "compare_r3_out.txt")).read())
