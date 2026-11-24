"""Tâm kỳ vọng điều chỉnh SIP — PREREG_adj.md (ef5157cb…) + PREREG_adj_v2.md (835dfc1e…). Job Taylor_20261124_110052 (g2).
Σ tuyến tính > 5% ⇒ v2 §5: CHẠY LẠI model_r3 (sổ rev4) theo TỔ HỢP: E[V] = Σ_S Π p_i Π(1−p_j) · V(S), 2^4 tập hạng mục.
Mù giá: chỉ lấy center_post (CK thanh khoản theo luật V3); không đọc/in giá, nhãn, 'dưới giá', 'giá ngụ ý'.
Model chạy trên BẢN SAO tạm của mirror (không ghi vào repo). Chạy: $DNA_PYEXE -I calc_adj.py"""
import json, hashlib, os, sys, io, contextlib, shutil, tempfile, itertools, csv
HERE = os.path.dirname(os.path.abspath(__file__))
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
assert md5(os.path.join(HERE, "..", "PREREG_adj.md")) == "ef5157cb3f762d58623ed550ebc214c7"
assert md5(os.path.join(HERE, "..", "PREREG_adj_v2.md")) == "835dfc1e07f9c67ac7f6c3028b529d13"
RC = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/dd_recheck_20261124/SIP"
MIR = RC + "/calc/mirror/dd_redo_20261105"
LOCK = {'SIP/calc_r3/assumptions_r3.json': '627a563f0133692f5889a344813716d4', 'SIP/calc_r3/model_r3.py': '343f4b438861012e335e849616aa1275',
        'SIP/calc_r3/px_sip_r3_20261106.csv': '6bffdef96b53d65916150b72b32a5cbb', '_common_g2r2/ddr2.py': '95d8fe38f5c17c3f723d6c175ffac49b',
        '_common_g2r2/px_g2r2_20261104.csv': '89b5306ea5c456f2f9adbdeec335277b', '_common_g2/ddg2.py': '81a87069f3f895a3a93d62d85b8fb5f0', '_shared/wpct.py': '4597bc083f0d64d8873141b12fbfb3a6'}
for f, h in LOCK.items():
    assert md5(os.path.join(MIR, f)) == h, f
assert md5(RC + "/skeptic/r1_raw.md") == "a24bad79c53a9c11d50a41cf4b3137fe"
tmp = tempfile.mkdtemp(prefix="adj_sip_"); T = os.path.join(tmp, "dd_redo_20261105")
for f in LOCK:
    os.makedirs(os.path.dirname(os.path.join(T, f)), exist_ok=True); shutil.copy(os.path.join(MIR, f), os.path.join(T, f))
SRC = os.path.join(T, "SIP/calc_r3/model_r3.py"); ns = {"__file__": SRC, "__name__": "__main__"}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(open(SRC).read(), SRC, "exec"), ns)
shutil.rmtree(tmp)
run, AX, R0, disc, PX, Sx = ns["run"], ns["AX"], ns["R0"], ns["disc"], ns["PX"], ns["S"]
cen = lambda ax=AX, **o: run(ax, R0, disc, PX, **o)[1]["center_post"]
H = cen(); C = 54466
assert round(H) == C, H                       # CONTROL: tái lập tâm sổ rev4
SH = ns["SH"]
# GPM từ BQ (sip_gpm_bq.csv): bình quân gia quyền doanh thu
rows = [r for r in csv.reader(open(os.path.join(HERE, "sip_gpm_bq.csv"))) if r and not r[0].startswith("#") and r[0] != "quarter"]
G = {q: (float(g), float(v)) for q, g, v in rows}
wavg = lambda qs: sum(G[q][0] * G[q][1] for q in qs) / sum(G[q][1] for q in qs)
ttm = wavg(["2025Q4", "2026Q1", "2026Q2", "2026Q3"]); fy25 = wavg([f"2025Q{i}" for i in range(1, 5)])
yrs = {y: wavg([f"{y}Q{i}" for i in range(1, 5)]) for y in range(2019, 2026)}
gpm_small = fy25 / ttm                        # cận nhỏ: chỉ về mức FY2025
P = {"A": (0.90, 0.75, 1.00), "B1": (0.50, 0.25, 0.75), "Bneg": (0.35, 0.15, 0.55)}
NCI_BS = Sx["nci_bs_9_9"]["value"]; VAT = Sx["vat_minus_dtl_ty"]["value"]
# mỗi hạng mục: opt(level) -> kwargs cho run(); level ∈ {"mid","small","big"} (độ lớn |m|)
ITEMS = [
 dict(key="VAT", name="Thuế GTGT khấu trừ 890,5 − DTL 123,7 (sổ sách; đối xứng với tạm ứng 643,7 đã vào base)", dir="up", tier="A", rung="A",
      lv={"small": 766.8, "mid": 766.8, "big": 890.5}, kw=lambda v: dict(extra=v),
      m_basis="mid/small = +766,8 tỷ theo sổ (VAT − DTL); big = +890,5 nếu DTL đã trùng taxdef (chưa đọc thuyết minh)",
      p_basis="A: số trực tiếp CĐKT; không hạ p (khoản thu hồi qua VAT đầu ra cho thuê đất); luật 'base = sổ sách' áp HAI chiều",
      source="assumptions_r3.json sensitivities.vat_minus_dtl_ty; notes_read.md (CĐKT); r1_raw.md:32"),
 dict(key="NCI", name="NCI công ty con: model 20% trung tâm → CĐKT 9,9%", dir="up", tier="B", rung="B1",
      lv={"small": NCI_BS, "mid": NCI_BS, "big": ns["nci_profit"]}, kw=lambda v: dict(ax=dict(AX, nci=[("fix", v, 1.0)])),
      m_basis="mid = 9,9% (NCI 568,4/VCSH 5.744,4); big = 8,5% (NCI/LNST 9T26 100,3/1.178,3)",
      p_basis="1 kỳ (30/9/2026; CĐKT và LN 9T cùng kỳ = 1 quan sát) ⇒ mặc định B; quy đổi tỷ lệ sổ → tỷ lệ giá trị là suy luận",
      source="assumptions_r3.json sensitivities.nci_bs_9_9; model_r3.py nci_profit; r1_raw.md:33"),
 dict(key="G12", name="Đất cho thuê 9T26 đếm đôi (đã vào DT chưa thực hiện, vẫn nằm trong 937,1 ha)", dir="down", tier="B", rung="B1",
      lv={"small": 28.6 * 0.75, "mid": 60.0, "big": 66.0}, kw=lambda v: dict(ha_less=v),
      m_basis="mid 60 ha (DT chưa thực hiện +1.701,8 tỷ 9T26 ÷ giá thuê gộp, skeptic); small 21,5 ha = tốc độ 2025 28,6 ha × 0,75 năm (cận bảo thủ); big 66 ha (≈ −1.000 đ/cp)",
      p_basis="1 kỳ (9T26) ⇒ mặc định B; dấu chắc (có cho thuê trong kỳ)",
      source="notes_read.md TM21:56; assumptions_r3.json ha_leased_9T26; r1_raw.md:23"),
 dict(key="GPM", name="Chuẩn hoá biên gộp vận hành về bình quân lịch sử", dir="down", tier="B", rung="Bneg",
      lv={"small": gpm_small, "mid": Sx["gpm_peak_normalisation"]["factor"], "big": Sx["gpm_peak_normalisation"]["factor"]}, kw=lambda v: dict(gpm_mult=v),
      m_basis="mid/big ×0,9457 (TB 2019–25 / TTM, skeptic r3); small ×FY25/TTM (BQ)",
      p_basis="6/7 năm 2019–25 < TTM 15,7% (cùng hướng) NHƯNG quan sát ngược có số: 2021 = 16,7% > TTM và xu hướng 2022→TTM đi lên 13,5→15,7% (BQ) ⇒ nhánh ngược",
      source="assumptions_r3.json gpm_peak_normalisation; sip_gpm_bq.csv; r1_raw.md:29"),
]
def kwargs(sel):
    o = {}
    for it, lev in sel:
        k = it["kw"](it["lv"][lev])
        if "ax" in k and "ax" in o: raise RuntimeError
        o.update(k)
    return o
def expect(choice):        # choice: list of (item, p, level)
    tot = 0.0
    for mask in itertools.product((0, 1), repeat=len(choice)):
        w = 1.0; sel = []
        for (it, p, lev), b in zip(choice, mask):
            w *= p if b else 1 - p
            if b: sel.append((it, lev))
        if w: tot += w * cen(**kwargs(sel))
    return tot
lin = 0.0
for it in ITEMS:
    p, plo, phi = P[it["rung"]]
    v = {lev: cen(**kwargs([(it, lev)])) / H - 1 for lev in ("small", "mid", "big")}
    it.update(p=p, p_low=plo, p_high=phi, mag_pct=round(v["mid"] * 100, 3), mag_range_pct=[round(v["small"] * 100, 3), round(v["big"] * 100, 3)],
              contrib_pct=round(p * v["mid"] * 100, 3), evidence_tier=it.pop("tier"), counted_in_center_bool=True)
    lin += p * v["mid"]
assert abs(lin) > 0.05                       # ⇒ v2 §5 bắt buộc tổ hợp
E_mid = expect([(it, it["p"], "mid") for it in ITEMS])
E_lo = expect([(it, it["p_low"] if it["dir"] == "up" else it["p_high"], "small" if it["dir"] == "up" else "big") for it in ITEMS])
E_hi = expect([(it, it["p_high"] if it["dir"] == "up" else it["p_low"], "big" if it["dir"] == "up" else "small") for it in ITEMS])
ca, lo, hi = round(E_mid), round(E_lo), round(E_hi)
assert 0 < lo <= ca <= hi
for it in ITEMS: it.pop("kw"); it.pop("lv"); it.pop("rung"); it.pop("key")
pv_even = ns["pv_even"]
rent = lambda bn_yr: round(cen(extra=-pv_even(bn_yr * 35, 35, R0)) - H)
r_ = lambda x: round(x)
sens = [
 dict(name="G16 tiền thuê đất trả Nhà nước (nếu trả hằng năm cho phần đã cho thuê lại)", dir="down", evidence_tier="C",
      sensitivity="mỗi 10 tỷ/năm × 35 năm: %d đ/cp (%.2f%%); 100 tỷ/năm: %d (%.2f%%); cận trên dữ liệu = toàn bộ giá vốn mảng đất 9T26 106,0 tỷ quy năm 141 tỷ/năm: %d (%.2f%%)" % (rent(10), rent(10) / H * 100, rent(100), rent(100) / H * 100, rent(141.3), rent(141.3) / H * 100),
      why="Trả một lần (thường gặp ở KCN, đã nằm trong chi phí đất/sổ) ⇒ 0; trả hằng năm ⇒ âm. Không biết hình thức ⇒ cận bảo thủ = 0 ⇒ C, không đủ C+", source="r1_raw.md:22,53; notes_read.md:40"),
 dict(name="Giá trị đất ròng 12 tỷ/ha (không nguồn, ~36% tâm)", dir="both", evidence_tier="C",
      sensitivity="trục ×0,75 cố định: %d; ×1,25: %d" % (r_(cen(dict(AX, perha_mult=[("x", 0.75, 1.0)])) - H), r_(cen(dict(AX, perha_mult=[("x", 1.25, 1.0)])) - H)),
      why="Không có giao dịch/biên cho thuê lại để định hướng", source="r1_raw.md:21,48"),
 dict(name="Tín dụng phi ngân hàng 6.016 tỷ, bên vay G1/G2 chưa định danh", dir="both", evidence_tier="C",
      sensitivity="trục tổn thất 0/10/30% (60/25/15) đã trong lưới (−1.255 ở điểm giữa); EY không trích dự phòng", why="Hai chiều, không có dữ liệu bên vay", source="r1_raw.md:24,54"),
 dict(name="Tạm ứng nội bộ 643,7 tỷ 'tìm hiểu và mua đất'", dir="down", evidence_tier="C", sensitivity="bỏ khỏi base: %d; mất trọn p0,15 (song song r3): −517" % r_(cen(adv=0.0) - H),
      why="Không có dữ liệu tổn thất; base = sổ sách (đối xứng với VAT #1)", source="model_r3_out.txt SONG SONG; r1_raw.md:27"),
 dict(name="Tài sản sổ sách 396,8 tỷ đọc từ ảnh scan", dir="both", evidence_tier="C", sensitivity="±1.616 (bước cầu #4)", why="Chưa đối chiếu text; không có hướng", source="model_r3_out.txt CẦU #4"),
 dict(name="D3 hạ tầng môi trường cho 937 ha", dir="down", evidence_tier="C", sensitivity="≈0 nếu 12 tỷ/ha đã ròng hạ tầng (định nghĩa)", why="r1_raw:53 (4): giảm nhẹ", source="REPORT_recheck_SIP.md:58"),
 dict(name="[LUẬT] r 13,5% vs dải Ke (E15)", dir="up", evidence_tier="rule", sensitivity="Ke 12,3%: 57.744 (+6,02%); 13,4%: 54.720 (+0,47%)", why="Tham số luật V1 (v2 §4)", source="REPORT_recheck_SIP.md:38-41"),
 dict(name="[LUẬT] RONIC = Ke cho mảng vận hành (skeptic: thu nhập dịch vụ trên 937 ha mới)", dir="up", evidence_tier="rule", sensitivity="RONIC = ROE5Y 29,7%: +3.389 (+6,22%)", why="Luật V5/D4", source="model_r3_out.txt ĐỘ NHẠY"),
 dict(name="Cổ tức", dir="none", evidence_tier="mech", sensitivity="Cổ tức 9T26 968,5 tỷ đã công bố & trả (TM24); nguồn không ghi cổ tức tiền đã công bố chưa GDKHQ ⇒ một dòng", why="PREREG v2 §6", source="notes_read.md:35"),
]
dv = lambda pct: round(C * pct / 100)
I = {it["name"][:3]: it for it in ITEMS}
vat, nci, g12, gpm = ITEMS
trig = [
 dict(event="BCTC năm 2026 (kiểm toán): thuyết minh thuê đất G16 — trả hằng năm", when="ước lượng 03/2027", direction="down", delta_vnd=rent(10), delta_pct=round(rent(10) / H * 100, 2), note="mỗi 10 tỷ/năm; trả một lần ⇒ 0 (đóng hạng mục)"),
 dict(event="Thuyết minh VAT/DTL: VAT khấu trừ được (hoặc DTL trùng taxdef)", when="ước lượng 03/2027", direction="up", delta_vnd=dv(0.1 * vat["mag_pct"]), delta_pct=round(0.1 * vat["mag_pct"], 2), note="p 0,9→1,0; DTL trùng ⇒ m lên %.2f%%" % vat["mag_range_pct"][1]),
 dict(event="Thuyết minh VAT: không hoàn/khấu trừ được trong tầm nhìn", when="ước lượng 03/2027", direction="down", delta_vnd=dv(-0.9 * vat["mag_pct"]), delta_pct=round(-0.9 * vat["mag_pct"], 2), note="p→0"),
 dict(event="NCI từng công ty con (G14) xác nhận ≈ tỷ lệ sổ", when="BCTC năm 2026", direction="up", delta_vnd=dv(0.4 * nci["mag_pct"]), delta_pct=round(0.4 * nci["mag_pct"], 2), note="p 0,5→0,9"),
 dict(event="Số ha cho thuê 9T26/FY26 công bố (G12)", when="CBTT/BCTN 2026", direction="down", delta_vnd=round((cen(ha_less=1.0) - H)), delta_pct=round((cen(ha_less=1.0) / H - 1) * 100, 3), note="mỗi 1 ha; số chính thức ⇒ A, p 0,9"),
 dict(event="GPM Q4/2026 ≥ 15,5% (giữ đà tăng)", when="ước lượng cuối 01/2027", direction="up", delta_vnd=dv(-0.2 * gpm["mag_pct"]), delta_pct=round(-0.2 * gpm["mag_pct"], 2), note="p GPM 0,35→0,15"),
 dict(event="GPM Q4/2026 < 14,6% (về TB 2019–25)", when="ước lượng cuối 01/2027", direction="down", delta_vnd=dv(0.3 * gpm["mag_pct"]), delta_pct=round(0.3 * gpm["mag_pct"], 2), note="p 0,35→0,65"),
 dict(event="Định danh bên vay G1/G2 = bên liên quan", when="khi có", direction="down", delta_vnd=None, delta_pct=None, note="trọng số tổn thất 0% (60%) giảm ⇒ C→B; WARNING quản trị"),
 dict(event="Giao dịch cho thuê lại gần đây (giá/biên ròng)", when="CBTT", direction="both", delta_vnd=None, delta_pct=None, note="thay 12 tỷ/ha; trục ×0,75/×1,25 ở §2"),
 dict(event="Lãi huy động 12T ±50bp (V1, β=1)", when="liên tục", direction="both", delta_vnd=-1222, delta_pct=-2.24, note="+50bp −1.222; −50bp +1.303"),
]
out = dict(ticker="SIP", dd_date="2026-11-01", rev=4, asof="2026-11-24", prereg_md5="ef5157cb3f762d58623ed550ebc214c7", prereg_v2_md5="835dfc1e07f9c67ac7f6c3028b529d13",
           blind_to_price=True, center_base=C, center_base_source="kb/dd_price_zones.json SIP rev4 (center sau CK 1,39% @5 tỷ)",
           items=ITEMS, sum_p_m_pct=round(lin * 100, 3), combination_rerun=True,
           center_adj_linear=round(C * (1 + lin)), center_adj=ca, range_low=lo, range_high=hi,
           gpm_bq=dict(ttm=round(ttm, 4), fy25=round(fy25, 4), annual={str(k): round(v, 4) for k, v in yrs.items()}),
           dividend_rights="không có quyền chưa chốt ghi nhận trong nguồn", sensitivity_only=sens, trigger_table=trig,
           caveat="tâm/dải = kỳ vọng tổ hợp 16 tập (hạng mục độc lập Bernoulli p) chạy lại model_r3; dải chọn (p,m) cực trị theo dấu từng hạng mục")
json.dump(out, open(os.path.join(HERE, "adj.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ["center_adj", "range_low", "range_high", "sum_p_m_pct", "center_adj_linear", "gpm_bq"]}, ensure_ascii=False))
for it in ITEMS: print(it["evidence_tier"], it["p"], it["mag_pct"], it["mag_range_pct"], it["contrib_pct"], it["name"])
for s in sens: print("S", s["sensitivity"][:150])
for t in trig: print(t["delta_vnd"], t["delta_pct"], t["event"])
