"""Tâm kỳ vọng điều chỉnh HHS — DẠNG HIỂN THỊ theo dải CK holding 0…+20% user chốt 24/11 (kb/projects/ck-hhs-reference-range-20261124.md).
KHÔNG phải rev mới, KHÔNG ghi sổ. PREREG_adj.md (ef5157cb…) + v2 (835dfc1e…). Job Taylor_20261124_110052 (g2). Mù giá: lưới không đọc giá. Chạy: $DNA_PYEXE -I calc_adj.py (cần numpy).
Tái dùng lõi hhs_r3.py + d5 (dilution_out.json) y như dd_recheck_20261124/HHS/calc/calc_recheck.py (md5 khoá); CONTROL: h=0,2663 ⇒ 10.805."""
import os, json, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
assert md5(os.path.join(HERE, "..", "PREREG_adj.md")) == "ef5157cb3f762d58623ed550ebc214c7"
assert md5(os.path.join(HERE, "..", "PREREG_adj_v2.md")) == "835dfc1e07f9c67ac7f6c3028b529d13"
M = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research"
R3 = M + "/dd_redo_20261105/HHS/calc_r3/hhs_r3.py"; DIL = M + "/dd_dilution_update_20261110/calc/dilution_out.json"
A7 = M + "/dd_dilution_update_20261110/HHS/rev7/calc/assumptions.json"
assert md5(R3) == "cf5420d86989f25b4070697b38347c52" and md5(DIL) == "0450ba0aee972c6c4ec97847fe2de68c" and md5(A7) == "3afcd113013fad82acfa5ea35c5bce1d"
assert md5(M + "/dd_recheck_20261124/HHS/skeptic/r1_raw.md") == "ef6ccc76a430d3d8e7573e66472250d5"
ns = {"__file__": R3, "__name__": "r3core"}
exec(compile(open(R3).read().split("# ---- CONTROL")[0], R3, "exec"), ns)
R2C, make, HEAD, R = ns["R2C"], ns["make"], ns["HEAD"], ns["R"]
d5 = json.load(open(DIL))["HHS"]["inputs"]["d5"]
N0, NR, CASH, DIV = 431_985_968, 259_191_580, 259_191_580 * 10_000, 0.07
A = json.load(open(A7)); H7 = A["holding_discount"]["base"]; assert H7 == 0.2663
def grid(h, r=0.135):
    ax, fn = make(HEAD)
    res = R2C.outcomes(ax, lambda **a: fn(**a, hd_fix=h, r=r))
    s = R2C.stats(res, 0.0, d5)
    return {q: round(s[q]) for q in ("center", "p10", "p90")}
ex = lambda V, k: round((V * N0 + (1 - d5) * k * CASH) / (N0 + NR) / (1 + DIV))
C = 10805
base = grid(H7); assert base["center"] == C, base            # CONTROL sổ rev8 (= rev7 recheck)
g20, g0 = grid(0.20), grid(0.0)
slope = (g20["center"] - g0["center"]) / 20                  # đ/cp mỗi +1pp CK (tuyến tính trong dải)
ca, lo, hi = g20["center"], g20["center"], g0["center"]
assert 0 < lo <= ca <= hi
EX = {f"h{h}": {"k1": ex(v["center"], 1.0), f"k{1 - h:.2f}": ex(v["center"], 1 - h)} for h, v in ((0.20, g20), (0.0, g0), (H7, base))}
rs = {f"r{r}": grid(0.20, r)["center"] for r in (0.123, 0.130, 0.134, 0.140)}
sens = [
 dict(name="[USER CHỐT] CK holding: base sổ 26,63% (N=6) → dải 0…+20%", dir="up", evidence_tier="user_param",
      sensitivity="+20%% (mốc hiện tại): %d (%+.2f%%); 0%% (đầu lạc quan): %d (%+.2f%%); %d đ/cp mỗi +1pp CK" % (g20["center"], (g20["center"] / C - 1) * 100, g0["center"], (g0["center"] / C - 1) * 100, round(slope)),
      why="Tham số do user chốt (display-only), không phải hạng mục bằng chứng ⇒ đổi NỀN tính, không vào Σ", source="kb/projects/ck-hhs-reference-range-20261124.md; ck_holding_vn_20261124_v5"),
 dict(name="EX k_base: rev7 dùng k=0,734 trái assumptions k_base=1,0 (skeptic r5/r1)", dir="up", evidence_tier="A_mech",
      sensitivity="sửa cơ học theo file giả định khoá; dòng EX dùng k=1, k=1−h chỉ hiển thị", why="Chỉ đổi dòng EX, không đổi CUM", source=A7.split("mike/")[1] + " ; r1_raw.md:10"),
 dict(name="Chi phí hoàn thiện NC-II (G10) không sinh biên", dir="down", evidence_tier="C",
      sensitivity="rev5 @CK 0%: 5% giá gốc HTK −351, 10% −702, 20% −1.403; quy đổi @CK 20% (×0,8, ước lượng): −281 / −562 / −1.122",
      why="Chi phí phải trả 30/9 chỉ 28,1 tỷ; errata r3: nếu biên 52% trên tổng chi phí thì hoàn thiện sinh biên ⇒ dấu không chắc ⇒ C", source="dd_dilution_update_20261110/HHS/REPORT_rev5.md:54; dd_redo_20261105/HHS/ERRATA_final_skeptic_20261109.md:5"),
 dict(name="Nghĩa vụ NƠXH/quỹ đất NC-II, I.14 + KL 08/KL-TTTP", dir="down", evidence_tier="C", sensitivity="chưa có số; thường đã nằm trong tổng mức đầu tư ⇒ cận = 0",
      why="Không có dấu chắc + cận", source="REPORT_recheck_HHS.md §3 D3; r1_raw.md:16"),
 dict(name="Cơ cấu cao tầng HH1–HH4", dir="down", evidence_tier="C", sensitivity="−2,3…−9,0% (kịch bản rev7)", why="Đã nằm trong trục ds ±15pp của lưới ⇒ thêm là đếm hai lần", source="dd_redo_20261105/HHS/REPORT_r3.md:76"),
 dict(name="CK thanh khoản 1,41% @5 tỷ = 48% ADV60", dir="down", evidence_tier="rule", sensitivity="có thể thấp", why="Luật V3 (tham số luật)", source="r1_raw.md:18"),
 dict(name="[LUẬT] r vs dải Ke (E15) @CK 20%", dir="up", evidence_tier="rule",
      sensitivity="Ke 12,3%%: %d; 13,4%%: %d; +50bp: %d" % (rs["r0.123"], rs["r0.134"], rs["r0.14"]), why="Tham số luật V1", source="calc này"),
 dict(name="[LUẬT] P/E ô tô 6 < 1/Ke 7,4", dir="up", evidence_tier="rule", sensitivity="≈ +1% (skeptic)", why="Luật RONIC=Ke", source="r1_raw.md:42"),
 dict(name="TB 2124/TB-TTCP thu hồi 7,87 tỷ; KL 08", dir="down", evidence_tier="legal", sensitivity="≤0,2% (7,87 tỷ / 432 tr cp)", why="Pháp lý chỉ WARNING", source="REPORT_recheck_HHS.md §4"),
]
trig = [
 dict(event="Kết quả lấy ý kiến cổ đông NQ 10/NQ-HĐQT (14–25/12/2026): giữ quyền 5:3 @10.000 + CP 7%", when="cuối 12/2026", direction="down", delta_vnd=EX["h0.2"]["k1"] - ca, delta_pct=round((EX["h0.2"]["k1"] / ca - 1) * 100, 2), note="sau GDKHQ dùng dòng EX (k=1) @CK 20%; đổi giá chào/quy mô ⇒ tính lại EX"),
 dict(event="NQ 10 huỷ / hoãn phát hành", when="cuối 12/2026", direction="none", delta_vnd=0, delta_pct=0.0, note="giữ dòng CUM"),
 dict(event="Đo lại CK holding (quét v5 định kỳ)", when="hằng quý", direction="both", delta_vnd=round(slope), delta_pct=round(slope / C * 100, 2), note="mỗi +1pp CK; dải user chốt chỉ đổi khi user chốt lại"),
 dict(event="Cổ tức tiền CRV về HHS", when="khi công bố", direction="up", delta_vnd=None, delta_pct=None, note="bằng chứng chống CK cao ⇒ nghiêng về đầu 0%% (tối đa +%d)" % (hi - ca)),
 dict(event="Dự toán hoàn thiện NC-II/HH1–HH4 công bố (G10)", when="BCTN 2026 / CBTT", direction="down", delta_vnd=-562, delta_pct=round(-562 / C * 100, 2), note="mỗi 10% giá gốc HTK không sinh biên (quy đổi @CK 20%, ước lượng)"),
 dict(event="BCTC kiểm toán NĐL (BV < 10.000)", when="ước lượng 03/2027", direction="down", delta_vnd=None, delta_pct=None, note="k<1 có cơ sở ⇒ dòng EX dùng k đo được"),
 dict(event="Số liệu NƠXH / KL 08 thu hồi", when="khi có", direction="down", delta_vnd=None, delta_pct=None, note="C→A, trừ theo đ/cp; pháp lý chỉ WARNING"),
 dict(event="Lãi huy động 12T ±50bp (V1)", when="liên tục", direction="both", delta_vnd=rs["r0.14"] - ca, delta_pct=round((rs["r0.14"] / ca - 1) * 100, 2), note="+50bp; −50bp %+d" % (rs["r0.13"] - ca)),
]
out = dict(ticker="HHS", dd_date="2026-11-01", rev=8, asof="2026-11-24", display_only=True, prereg_md5="ef5157cb3f762d58623ed550ebc214c7", prereg_v2_md5="835dfc1e07f9c67ac7f6c3028b529d13",
           blind_to_price=True, center_base=C, center_base_source="kb/dd_price_zones.json HHS rev8 (CUM, CK holding 26,63%)",
           ck_range_user=[0.0, 0.20], center_rebased_ck20=g20, center_ck0=g0, items=[], sum_p_m_pct=0.0, combination_rerun=False,
           center_adj=ca, range_low=lo, range_high=hi, ex_after_rights=EX, dividend_rights="CÒN QUYỀN: quyền mua 5:3 @10.000 + CP 7% chờ lấy ý kiến 14–25/12/2026 ⇒ 2 dòng CUM/EX",
           sensitivity_only=sens, trigger_table=trig,
           caveat="Σ bằng chứng = 0 (không hạng mục A/B/C+); tâm adj = lưới rev7 @CK +20% (mốc hiện tại user chốt), đầu cao = @CK 0%; KHÔNG ghi sổ, KHÔNG rev8 mới")
json.dump(out, open(os.path.join(HERE, "adj.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ["center_adj", "range_low", "range_high", "center_rebased_ck20", "center_ck0", "ex_after_rights"]}))
print("slope", round(slope, 1), rs)
for t in trig: print(t["delta_vnd"], t["delta_pct"], t["event"])
