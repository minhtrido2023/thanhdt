"""V6 hiển thị: V_ngắn = trung vị LNST TTM 3 mốc (Q3/24,Q3/25,Q3/26; BQ NP tổng, chưa tách CĐKKS) / r (RONIC=Ke ⇒ g không đổi giá trị);
V_dài = FCFE TTM Q3/26 (CF_OA + CF_Invest, BQ, chưa trừ/ cộng vay ròng) / r. Chỉ hiển thị (V6), KHÔNG vào tâm.
Dùng: v6_display.py <csv> <shares_m> [r=0.135]"""
import csv, sys, statistics, math, json
f, sh = sys.argv[1], float(sys.argv[2]); r = float(sys.argv[3]) if len(sys.argv) > 3 else 0.135
rows = {x["quarter"]: x for x in csv.DictReader(l for l in open(f) if not l.startswith("#"))}
num = lambda v: float(v) if v not in ("", None) else None
ttm = {q: sum(num(rows[q][f"NP_P{i}"]) for i in range(4)) / 1e9 for q in rows}
ni = statistics.median(ttm.values())
cur = rows["2026Q3"]
cfo = [num(cur[f"CF_OA_P{i}"]) for i in range(4)]; cfi = [num(cur[f"CF_Invest_P{i}"]) for i in range(4)]
out = {"ttm_np_bn": {k: round(v, 1) for k, v in ttm.items()}, "ni_norm_bn": round(ni, 1), "r": r,
       "v_short_vps": round(ni / r / sh * 1000)}
if None in cfo or None in cfi:
    out["v_long"] = "cần kiểm chứng: BQ thiếu CF_OA/CF_Invest quý (NULL)"
else:
    fcfe = (sum(cfo) + sum(cfi)) / 1e9
    out["fcfe_ttm_bn"] = round(fcfe, 1)
    if fcfe <= 0:
        out["v_long"] = "FCFE TTM <= 0 ⇒ chỉ V_ngắn"
    else:
        vl = fcfe / r / sh * 1000; out["v_long_vps"] = round(vl)
        out["D"] = round(abs(math.log(out["v_short_vps"] / vl)), 3)
        out["flag"] = "D>ln3" if out["D"] > math.log(3) else ("D>ln2" if out["D"] > math.log(2) else "không cờ")
print(json.dumps(out, ensure_ascii=False))
