"""VGS SOTP — mù giá thị trường. Đọc assumptions.json, in model_out.json.
Chạy: python3 model.py [r_override]"""
import json, sys, itertools, math
from pathlib import Path

A = json.load(open(Path(__file__).with_name("assumptions_r2.json")))
SH = A["shares_m"]
bs, pl = A["bs_20260930"], A["pl"]


def ttm(k):
    return pl["fy25"][k] - pl["9m25"][k] + pl["9m26"][k]


TTM = {k: ttm(k) for k in ["net_rev", "gp", "fin_inc", "fin_exp", "assoc", "sell", "ga", "other", "pbt", "tax", "np_parent"]}
TTM["core_ebit"] = TTM["gp"] - TTM["sell"] - TTM["ga"]
TTM["core_np_proxy"] = (TTM["pbt"] - TTM["assoc"]) * (1 - TTM["tax"] / (TTM["pbt"] - TTM["assoc"]))
TTM["eps"] = TTM["np_parent"] / SH * 1000


def value(r, ov=None):
    cs, asn, lg = A["core_scenarios"], A["associate_scenarios"], A["legend_city"]
    core = {}
    for s in ["bear", "base", "bull"]:
        c = cs[s]
        np_ = c["rev"] * (c["gpm"] - c["sga"]) * (1 - cs["tax"])
        core[s] = (np_ / r, cs[s]["w"], np_)
    ov = ov or {}
    assoc = {
        "bear": (bs["associate_carrying"] * asn["bear"].get("factor", 1.0), asn["bear"]["w"]),
        "base": (sum(asn["base"]["earn"]) / 3 / r, asn["base"]["w"]),
        "bull": (TTM["assoc"] * asn["bull"]["pe"], asn["bull"]["w"]),
    }
    if "assoc_base_val" in ov:
        assoc["base"] = (ov["assoc_base_val"], assoc["base"][1])
    if "assoc_w" in ov:
        assoc = {k: (assoc[k][0], ov["assoc_w"][k]) for k in assoc}
    lgc_net = bs["xdcb_legend_city"] + bs["xdcb_cc4_van_canh"] - bs["vinaconex_bcc_payable_lt"]
    lgc = {k: (lgc_net * f, w) for k, (f, w) in lg["factors"].items()}
    net_cash = bs["cash"] + bs["htm_deposits"] - bs["st_loans"]
    out = []
    for (ck, (cv, cw, _)), (ak, (av, aw)), (lk, (lv, lw)) in itertools.product(core.items(), assoc.items(), lgc.items()):
        eq = cv + av + lv + net_cash
        out.append({"core": ck, "assoc": ak, "lgc": lk, "eq_bn": eq, "vps": eq / SH * 1000, "w": cw * aw * lw})
    return out, core, assoc, lgc, net_cash, lgc_net


def wq(rows, q):
    rows = sorted(rows, key=lambda x: x["vps"])
    cum = 0
    for x in rows:
        mid = cum + x["w"] / 2
        if mid >= q:
            return x["vps"]
        cum += x["w"]
    return rows[-1]["vps"]


def summarize(r, ov=None):
    rows, core, assoc, lgc, nc, lgc_net = value(r, ov)
    center = sum(x["vps"] * x["w"] for x in rows)
    return {"r": r, "center": center, "p10": wq(rows, .10), "p25": wq(rows, .25), "p50": wq(rows, .50),
            "p75": wq(rows, .75), "p90": wq(rows, .90), "min": min(x["vps"] for x in rows), "max": max(x["vps"] for x in rows),
            "core": {k: {"val_bn": v[0], "np_bn": v[2], "vps": v[0] / SH * 1000} for k, v in core.items()},
            "assoc": {k: {"val_bn": v[0], "vps": v[0] / SH * 1000} for k, v in assoc.items()},
            "lgc": {k: {"val_bn": v[0], "vps": v[0] / SH * 1000} for k, v in lgc.items()},
            "net_cash_bn": nc, "net_cash_vps": nc / SH * 1000, "lgc_net_bn": lgc_net, "n_outcomes": len(rows)}


r0 = A["r"]["anchor_r"] + A["r"]["beta"] * (A["r"]["dep_now"] - A["r"]["anchor_dep"])
if len(sys.argv) > 1:
    r0 = float(sys.argv[1])
res = summarize(r0)
S2 = A["sens_r2"]
res["sens_r2"] = {
    "assoc_base_book": summarize(r0, {"assoc_base_val": bs["associate_carrying"]})["center"],
    "assoc_base_pb_peer": summarize(r0, {"assoc_base_val": bs["associate_carrying"] * S2["assoc_base_pb_peer"]})["center"],
    "assoc_w2_reading_b": summarize(r0, {"assoc_base_val": (A["associate_scenarios"]["base"]["earn"][0] + S2["assoc_w2_reading_b_2025"] + A["associate_scenarios"]["base"]["earn"][2]) / 3 / r0})["center"],
    "m1_mid_weights": summarize(r0, {"assoc_w": S2["m1_mid_weights"]})["center"],
}
res["assoc_base_avg3_w2b_bn"] = (A["associate_scenarios"]["base"]["earn"][0] + S2["assoc_w2_reading_b_2025"] + A["associate_scenarios"]["base"]["earn"][2]) / 3
res["sens_r"] = {f"{bp:+d}bp": summarize(r0 + bp / 1e4)["center"] for bp in (-100, -50, 50, 100)}
res["sens_beta05"] = {f"{bp:+d}bp": summarize(r0 + 0.5 * bp / 1e4)["center"] for bp in (-100, -50, 50, 100)}
L = A["liquidity"]
res["liq"] = {}
for q in L["sizes_bn"]:
    ck = L["sigma_d"] * math.sqrt(q / L["adv250_bn"])
    ck60 = L["sigma_d"] * math.sqrt(q / L["adv60_bn"])
    res["liq"][f"{q}ty"] = {"ck_adv250": ck, "ck_adv60": ck60, "center_post": res["center"] * (1 - ck),
                            "p10_post": res["p10"] * (1 - ck), "p90_post": res["p90"] * (1 - ck),
                            "sessions_10pct_adv250": q / (0.1 * L["adv250_bn"]), "sessions_10pct_adv60": q / (0.1 * L["adv60_bn"])}
res["ttm"] = TTM
res["bvps"] = bs["equity_parent"] / SH * 1000
res["center_vs_bvps"] = res["center"] / res["bvps"]
res["center_pe_ttm"] = res["center"] / TTM["eps"]
json.dump(res, open(Path(__file__).with_name("model_out_r2.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: (round(v) if isinstance(v, float) and abs(v) > 50 else v) for k, v in res.items() if k not in ("core", "assoc", "lgc", "liq", "ttm")}, indent=1))
print("core", {k: (round(v["np_bn"], 1), round(v["vps"])) for k, v in res["core"].items()})
print("assoc", {k: round(v["vps"]) for k, v in res["assoc"].items()}, "lgc", {k: round(v["vps"]) for k, v in res["lgc"].items()}, "netcash_vps", round(res["net_cash_vps"]))
print("liq", {k: (round(v["ck_adv250"] * 100, 2), round(v["ck_adv60"] * 100, 2), round(v["center_post"]), round(v["p10_post"]), round(v["p90_post"]), round(v["sessions_10pct_adv250"], 1), round(v["sessions_10pct_adv60"], 1)) for k, v in res["liq"].items()})
print("ttm", {k: round(v, 1) for k, v in TTM.items()})
