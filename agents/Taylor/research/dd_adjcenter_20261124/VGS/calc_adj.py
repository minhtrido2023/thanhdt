"""Tâm kỳ vọng điều chỉnh VGS — PREREG_adj.md + PREREG_adj_v2.md (fan-out g1, job Taylor_20261124_110049). Mù giá.
|Σ| tuyến tính > 5% ⇒ v2 §5: chạy lại mô hình SOTP r2 (tái hiện model_r2.py value(), CONTROL 26.778) với TỔ HỢP 2^k bật/tắt hạng mục, trọng số Π p."""
import json, hashlib, os, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
PRE1, PRE2 = (os.path.join(HERE, "..", f) for f in ("PREREG_adj.md", "PREREG_adj_v2.md"))
assert md5(PRE1) == "ef5157cb3f762d58623ed550ebc214c7" and md5(PRE2) == "835dfc1e07f9c67ac7f6c3028b529d13"
AF = os.path.join(HERE, "assumptions_r2.json")   # bản sao nguyên văn dd_recheck_20261124/VGS/calc/assumptions_r2.json
assert md5(AF) == "c13014360aa523a102e31b5699c44db9"
A = json.load(open(AF)); SH = A["shares_m"]; bs = A["bs_20260930"]; cs = A["core_scenarios"]; asn = A["associate_scenarios"]; pl = A["pl"]
C_LEDGER = 26526            # kb/dd_price_zones.json VGS rev3 center (sau CK ≤1 tỷ; dd_date 2026-11-10)
R = 0.135
TTM_ASSOC = pl["fy25"]["assoc"] - pl["9m25"]["assoc"] + pl["9m26"]["assoc"]
def center(ov):
    """Tái hiện model_r2.value() + điều chỉnh. ov: core_np_delta (tỷ/năm, mọi kịch bản), sga, base_gpm, base_rev, lgc_add, eq_add (tỷ)."""
    core = 0.0
    for s in ("bear", "base", "bull"):
        c = dict(cs[s])
        if s == "base":
            c["gpm"] = ov.get("base_gpm", c["gpm"]); c["rev"] = ov.get("base_rev", c["rev"])
        np_ = c["rev"] * (c["gpm"] - ov.get("sga", c["sga"])) * (1 - cs["tax"]) + ov.get("core_np_delta", 0.0)
        core += np_ / R * c["w"]
    assoc = bs["associate_carrying"] * asn["bear"]["factor"] * asn["bear"]["w"] + sum(asn["base"]["earn"]) / 3 / R * asn["base"]["w"] + TTM_ASSOC * asn["bull"]["pe"] * asn["bull"]["w"]
    lgc_net = bs["xdcb_legend_city"] + bs["xdcb_cc4_van_canh"] - bs["vinaconex_bcc_payable_lt"] + ov.get("lgc_add", 0.0)
    lgc = sum(lgc_net * f * w for f, w in A["legend_city"]["factors"].values())
    nc = bs["cash"] + bs["htm_deposits"] - bs["st_loans"]
    return (core + assoc + lgc + nc + ov.get("eq_add", 0.0)) / SH * 1000
C0 = center({}); assert round(C0) == 26778, C0            # CONTROL r2
FCK = C_LEDGER / C0                                        # hệ số CK thanh khoản cỡ ≤1 tỷ của sổ
# --- dữ liệu ---
SRC_BS = "src/BCTC-Q3-HN.pdf tr.2 (khôi phục từ git 30ca17444^, md5 e30e74ce; ảnh /tmp/vgs_src/p2.png)"
S2 = "agents/Taylor/research/dd_VGS_20261110/skeptic/r2_raw.md"
S1 = "agents/Taylor/research/dd_recheck_20261124/VGS/skeptic/r1_raw.md"
RP = "agents/Taylor/research/dd_VGS_20261110/REPORT.md"
KTPL_STOCK = 36.105301461                                  # mã 323, 30/09/2026 (01/01/2026: 36,663)
KTPL_SPEND = (36.663301461 - KTPL_STOCK) * 4 / 3           # chi quỹ năm hoá 9T26 (không có dòng trích: 420 tăng 137,76 = LNST 199,28 − cổ tức 61,52)
KTPL_2025_HI = pl["fy25"]["np_parent"] - 207.837621764     # LNST 2025 mẹ 217,02 − 420b cuối 2025 207,84 = 9,18 tỷ đã phân phối từ LN năm 2025 (cận trên KTPL)
DA9, CAPEX9, LGC9 = 9.11, 124.6, 90.9                      # S2:15 (LCTT 9T26 tr.5, skeptic đối chiếu bản gốc)
GAP = (CAPEX9 - LGC9 - DA9) * 4 / 3                        # capex ngoài LGC − khấu hao, năm hoá
P = {"A": (0.90, 0.75, 1.00), "B1": (0.50, 0.25, 0.75), "B3": (0.65, 0.40, 0.90), "Bneg": (0.35, 0.15, 0.55)}
# mỗi hạng mục: ov ở m điểm, ov_lo/ov_hi ở hai đầu khoảng m (None = m là số trực tiếp)
items = [
 dict(key="ktpl_stock", name="Tồn quỹ KTPL 36,1 tỷ chưa trừ khỏi nợ ròng", dir="down", evidence_tier="A", rung="A",
      ov={"eq_add": -KTPL_STOCK}, rng=None, source=f"{SRC_BS} mã 323", note="nợ phải trả; model_r2 nợ ròng = tiền + HTM − vay, không trừ quỹ"),
 dict(key="vinaconex_adv", name="Ứng trước Vinaconex 38,02 tỷ thiếu trong vốn ròng Legend City", dir="up", evidence_tier="A", rung="A",
      ov={"lgc_add": 38.02}, rng=None, source=f"{S2}:19,49", note="chi phí dự án đã trả ⇒ luật NPV=0 theo giá gốc; chịu cùng hệ số LGC 1,0/0,7"),
 dict(key="capex_maint", name="Capex duy trì > khấu hao (capex ngoài LGC 9T26 33,7 vs KH 9,1 tỷ)", dir="down", evidence_tier="B", rung="B1",
      ov={"core_np_delta": -GAP * 0.8}, rng=({"core_np_delta": -GAP * 0.8 * 0.5}, {"core_np_delta": -GAP}),
      source=f"{S2}:15,40", note="m điểm: toàn bộ khoảng chênh %.1f tỷ/năm là duy trì, sau lá chắn thuế 20%% (%.1f); khoảng: ½ khoảng chênh … không lá chắn. 1 kỳ (9T26) ⇒ B1" % (GAP, GAP * 0.8)),
 dict(key="ktpl_flow", name="Trích KTPL hằng năm từ LN lõi (C+ — cận bảo thủ)", dir="down", evidence_tier="C+", rung="B1",
      ov={"core_np_delta": -KTPL_SPEND}, rng=({"core_np_delta": -KTPL_SPEND}, {"core_np_delta": -KTPL_2025_HI}),
      source=f"{SRC_BS} mã 323, 420a/420b; {S2}:40", note="cận bảo thủ = tốc độ chi quỹ 9T26 năm hoá %.2f tỷ; cận trên = %.2f tỷ phân phối từ LN 2025 (4,2%% LNST). 1 kỳ ⇒ B1" % (KTPL_SPEND, KTPL_2025_HI)),
 dict(key="sga", name="SG&A base 1,5% → TTM 1,625%", dir="down", evidence_tier="B", rung="Bneg",
      ov={"sga": 0.01625}, rng=None, source=f"{S1}:15; assumptions core_scenarios._basis", note="1 kỳ (TTM, CPBH 9T +59%); ngược có số: FY25 1,28%"),
 dict(key="gpm", name="GPM base 3,6% → 4,0% (biên SP tự sản xuất 5,29% hai kỳ 9T; tỷ trọng thương mại giảm)", dir="up", evidence_tier="B", rung="Bneg",
      ov={"base_gpm": 0.040}, rng=({"base_gpm": 0.0395}, {"base_gpm": 0.040}), source=f"{S2}:40; {S1}:24; {RP}:69",
      note="2 kỳ cùng hướng (9T25, 9T26); ngược có số: GPM năm 2018/19/22/23/24 = 2,6/3,3/2,3/2,5/3,0% < 3,6%"),
 dict(key="rev", name="DT base 7.700 → TTM 7.849,6 tỷ", dir="up", evidence_tier="B", rung="Bneg",
      ov={"base_rev": 7849.6}, rng=None, source=f"{S1}:24", note="1 kỳ (TTM); ngược có số: FY25 7.318,6 < 7.700"),
]
def ev(sel):
    """Kỳ vọng trên tổ hợp 2^k: sel[i] = (p_i, ov_i)."""
    tot = 0.0
    for bits in itertools.product((0, 1), repeat=len(sel)):
        w = 1.0; ov = {}
        for b, (p, o) in zip(bits, sel):
            w *= p if b else (1 - p)
            if b:
                for k, v in o.items():
                    ov[k] = ov.get(k, 0.0) + v if k in ("core_np_delta", "lgc_add", "eq_add") else v
        tot += w * center(ov)
    return tot
for it in items:
    p, plo, phi = P[it.pop("rung")]
    it.update(p=p, p_low=plo, p_high=phi)
    mpt = center(it["ov"]) / C0 - 1
    ms = [mpt] + ([center(o) / C0 - 1 for o in it["rng"]] if it["rng"] else [])
    it.update(mag_pct=round(mpt * 100, 3), mag_range_pct=[round(min(ms) * 100, 3), round(max(ms) * 100, 3)], counted_in_center=True,
              contrib_pct_linear=round(p * mpt * 100, 3))
s_lin = sum(it["contrib_pct_linear"] for it in items) / 100
assert abs(s_lin) > 0.05  # ⇒ tổ hợp bắt buộc (v2 §5)
c_pre = ev([(it["p"], it["ov"]) for it in items])
def extreme(lowside):
    sel = []
    for it in items:
        cands = [(pp, o) for pp in (it["p_low"], it["p_high"]) for o in ([it["ov"]] + list(it["rng"] or []))]
        sel.append(min(cands, key=lambda x: ev([x])) if lowside else max(cands, key=lambda x: ev([x])))
    return ev(sel)
lo_pre, hi_pre = extreme(True), extreme(False)
ca, lo, hi = (round(x * FCK) for x in (c_pre, lo_pre, hi_pre))
for it in items:
    it["ov"] = {k: round(v, 4) for k, v in it["ov"].items()}; it["rng"] = [{k: round(v, 4) for k, v in o.items()} for o in it["rng"]] if it["rng"] else None
sens = [
 dict(name="Legend City NPV=0 vs trần lợi nhuận NOXH (miễn tiền SDĐ chiều ngược)", dir="both", evidence_tier="C",
      sensitivity="−2…−6%% (skeptic, ước lượng; chưa tra văn bản)", source=f"{S2}:40", why_not_center="dấu không chắc (miễn SDĐ bù); kịch bản xấu 0,7 đã có trong lưới"),
 dict(name="Cam kết vốn còn lại Legend City (tờ trình 05/2026 chưa có)", dir="down", evidence_tier="C", sensitivity="chưa định lượng", source=f"{S2}:48"),
 dict(name="Capex tuân thủ môi trường (mạ kẽm/xử lý nước thải)", dir="down", evidence_tier="C", sensitivity="chưa định lượng", source=f"{S1}:21"),
 dict(name="Hoàn nhập dự phòng 21,1 tỷ (dự phòng phải trả NH 31,37→10,02) làm phồng GPM TTM của kịch bản tốt", dir="down", evidence_tier="C",
      sensitivity="≈ −520 đ (−1,9%%) (skeptic r2)", source=f"{S2}:40; {SRC_BS} mã 322", why_not_center="bản chất dòng P&L chưa xác định"),
 dict(name="Cách đọc (b) lãi liên kết 2025 = 70,2 (cổ tức LK 26,6 đã trừ)", dir="up", evidence_tier="C", sensitivity="+535 đ (+2,0%%) ⇒ 27.313 trước CK", source=f"{RP}:222"),
 dict(name="Liên kết base = sổ / 0,75×sổ (P/B peer)", dir="down", evidence_tier="C", sensitivity="0,75×sổ ⇒ 24.911 (−7,0%%) trước CK", source=f"{RP}:19"),
 dict(name="[LUẬT] CK holding +20% lên liên kết + Legend City (số đúng theo skeptic)", dir="down", evidence_tier="rule", sensitivity="24.288 trước CK (−9,3%%)", source=f"{S1}:12"),
 dict(name="[LUẬT] CK thanh khoản theo ADV60 thay ADV250", dir="down", evidence_tier="rule", sensitivity="CK 1,57%% thay 0,94%% ở 1 tỷ ⇒ −0,64%%", source=f"{S1}:'liquidity'"),
 dict(name="[LUẬT] r 13,5% vs dải Ke (E15)", dir="up", evidence_tier="rule", sensitivity="Ke 12,3%% ⇒ 28.294 sau CK (+6,66%%); 13,4%% ⇒ +0,51%%", source="REPORT_recheck_VGS.md:35-38"),
]
def dpost(ov_pre_delta_pct): return round(C_LEDGER * ov_pre_delta_pct / 100)
cap = next(i for i in items if i["key"] == "capex_maint"); kf = next(i for i in items if i["key"] == "ktpl_flow")
gp = next(i for i in items if i["key"] == "gpm"); sg = next(i for i in items if i["key"] == "sga")
trig = [
 dict(event="BCTC năm 2026: thuyết minh TSCĐ/XDCB tách capex duy trì ≈ khấu hao (phần chênh là mở rộng)", when="ước lượng cuối 01–03/2027", direction="up",
      delta_vnd=dpost(-0.5 * cap["mag_pct"]), delta_pct=round(-0.5 * cap["mag_pct"], 2), note="p capex 0,50→0"),
 dict(event="BCTC năm 2026 / LCTT FY24–FY25: capex ngoài LGC ≫ khấu hao cả 3 kỳ, không có dự án mở rộng", when="ước lượng 01–03/2027", direction="down",
      delta_vnd=dpost(0.15 * cap["mag_pct"]), delta_pct=round(0.15 * cap["mag_pct"], 2), note="3 kỳ cùng hướng ⇒ p 0,65"),
 dict(event="NQ ĐHĐCĐ 2027: tỷ lệ trích KTPL (ví dụ 4,2% LNST ≈ 9,2 tỷ)", when="ước lượng 04/2027", direction="down",
      delta_vnd=dpost(0.9 * kf["mag_range_pct"][0] - 0.5 * kf["mag_pct"]), delta_pct=round(0.9 * kf["mag_range_pct"][0] - 0.5 * kf["mag_pct"], 2), note="C+→A p 0,9 ở cận trên"),
 dict(event="Q4/2026: GPM quý ≥4% và SG&A ≤1,5%", when="cuối 01/2027", direction="up",
      delta_vnd=dpost(0.15 * gp["mag_pct"] - 0.15 * sg["mag_pct"]), delta_pct=round(0.15 * gp["mag_pct"] - 0.15 * sg["mag_pct"], 2), note="p GPM 0,35→0,50, p SG&A 0,35→0,20 (ước lượng nhánh)"),
 dict(event="Q4/2026: GPM quý <3% hoặc SG&A >1,8%", when="cuối 01/2027", direction="down",
      delta_vnd=dpost(-0.2 * gp["mag_pct"] + 0.2 * sg["mag_pct"]), delta_pct=round(-0.2 * gp["mag_pct"] + 0.2 * sg["mag_pct"], 2), note="p GPM →0,15, p SG&A →0,55"),
 dict(event="Tờ trình 05/2026 / mức trần lợi nhuận NOXH Legend City", when="khi có", direction="both", delta_vnd=None, delta_pct=None, note="C→A: chạy lại NPV LGC ở r 13,5% (−2…−6%% ước lượng)"),
 dict(event="BCTC kiểm toán 2026 + giải trình cổ tức liên kết 2025 (mốc M5)", when="31/03/2027", direction="both", delta_vnd=dpost(2.0), delta_pct=2.0, note="cách đọc (b) đúng ⇒ +535 đ trước CK; sai ⇒ 0"),
 dict(event="Lãi huy động 12T ±50bp (luật V1, β=1)", when="liên tục", direction="both", delta_vnd=-647, delta_pct=-2.44, note="+50bp −647; −50bp +697 (REPORT_recheck §2)"),
 dict(event="User chốt CK holding +20% áp cho liên kết/LGC", when="khi user quyết", direction="down", delta_vnd=dpost(-9.3), delta_pct=-9.3, note="đổi luật ⇒ chạy lại"),
]
out = dict(ticker="VGS", dd_date="2026-11-10", rev=3, asof="2026-11-24", job="Taylor_20261124_110049",
           prereg_md5=dict(PREREG_adj="ef5157cb3f762d58623ed550ebc214c7", PREREG_adj_v2="835dfc1e07f9c67ac7f6c3028b529d13"), blind_to_price=True,
           center_base=C_LEDGER, center_base_source="kb/dd_price_zones.json VGS rev3 center (sau CK ≤1 tỷ); model_r2 trước CK 26.778",
           model_control_pre_ck=round(C0, 1), ck_factor=round(FCK, 6),
           items=items, sum_p_m_pct_linear=round(s_lin * 100, 3), aggregation="combinatorial 2^%d (v2 §5, |Σ tuyến tính|>5%%)" % len(items),
           sum_p_m_pct=round((c_pre / C0 - 1) * 100, 3),
           center_adj=ca, range_low=lo, range_high=hi,
           dividend_mech=dict(vnd=0, status="cổ tức tiền 2025 1.000 đ đã chi (61,5 tỷ); không có quyền chưa chốt trong nguồn"),
           sensitivity_only=sens, trigger_table=trig,
           caveat="m capex/SG&A/GPM/DT/Vinaconex chạy qua mô hình r2 tái hiện (CONTROL 26.778); m KTPL flow cận trên là suy luận (9,18 tỷ phân phối từ LN 2025, có thể gồm quỹ khác)")
assert 0 < lo <= ca <= hi
json.dump(out, open(os.path.join(HERE, "adj.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ["model_control_pre_ck", "ck_factor", "center_adj", "range_low", "range_high", "sum_p_m_pct", "sum_p_m_pct_linear"]}))
for it in items: print(it["evidence_tier"], it["p"], it["mag_pct"], it["mag_range_pct"], it["contrib_pct_linear"], it["name"][:60])
for t in trig: print(t["delta_vnd"], t["delta_pct"], t["event"][:70])
