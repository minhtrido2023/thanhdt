"""Ghi SCL/SUMMARY.json vòng 3 từ model_scl_r3_out.json (tất định). Chạy sau model_scl_r3.py."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(HERE, "model_scl_r3_out.json")))
H = M["headline"]["dist"]; P = H["P_post"]; H5 = M["headline_ck5ty"]["dist"]; L = M["liq"]; S = M["bridge"]; A = M["alternatives"]
px = M["price"]
R = lambda x: int(round(x))


def b(d):
    return {k: (R(v) if k not in ("pct_below", "n") else (round(v, 4) if k == "pct_below" else v)) for k, v in d.items()}


steps = list(S)
bridge = []
for i, k in enumerate(steps):
    prev = S[steps[i - 1]]["center_post"] if i else None
    bridge.append(dict(step=k, center_post=R(S[k]["center_post"]), p10=R(S[k]["p10"]), p50=R(S[k]["p50"]), p90=R(S[k]["p90"]),
                       delta=None if prev is None else R(S[k]["center_post"] - prev)))
reasons = {
    "S0_r2_headline": "r2 headline (lõi gốc GPM_P0 lấy TB 4 số TTM chồng lấn) — đối chứng tái lập 22.769",
    "S1_gpm_fix": "GPM_P0 BQ là TTM (bigquery_dictionary.json) ⇒ GPM năm = Q4 — đối chứng 21.813 / P90 26.672 khớp skeptic",
    "S2_px_0611": "giá+ADV tới 06/11 (ADV120 2,28→2,35 tỷ; CK 5 tỷ 4,50%→4,45%)",
    "S2b_recv_amt_bctc": "phải thu Vincons lấy đúng số BCTC 67,892 tỷ thay 116,0×58,5% (lệch 0,01 tỷ) — 0 đ/cp",
    "S3_no_recv_axis": "trục lỗ phải thu [UL] ra khỏi base → độ nhạy (không có cơ sở dữ liệu cho xác suất lỗ; BCTC: dự phòng 0, kiểm toán 2025 chấp nhận toàn phần)",
    "S4_E1": "bội số (1−g/ROE)/(r−g) là P/E kỳ tới ⇒ áp lên E1 = E0×(1+g); E0 = TTM tới 30/09/2026",
    "S5_ck_sleeve40": "CK ở cỡ sleeve thật 40 triệu (1,7% ADV120, trong vùng √) thay 5 tỷ (213% ADV120, ngoài vùng ⇒ ngoại suy)",
}
for x in bridge:
    x["reason"] = reasons[x["step"]]

out = dict(
    ticker="SCL", round=3, job="Taylor_20261108_142022", asof_price_date=M["asof_price_date"], price=px,
    price_basis=M["price_basis"], terp=round(M["terp"]),
    r=M["r_info"]["r"], r_anchor=dict(rate=7.40, current_rate=M["r_info"]["dep_pct"], current_source=M["r_info"]["dep_source"],
                                      formula="r = 13,5% + 1,0×(lãi huy động 12T hiệu dụng − 7,40%)"),
    center_pre_liq=R(H["center_pre"]), center_post_liq=R(H["center_post"]),
    p10_post=R(P["p10"]), p50_post=R(P["p50"]), p90_post=R(P["p90"]),
    p10_out=R(P["p10"]), p50_out=R(P["p50"]), p90_out=R(P["p90"]),
    min_out=R(H["min_post"]), max_out=R(H["max_post"]),
    pct_weight_below_price=round(H["pct_w_below_px"], 4), n_outcomes=H["n"],
    center_param_post=R(M["headline"]["center_param_post"]),
    label=M["headline"]["label"],
    label_note=(f"TRÊN vùng (>P90) ở cỡ sleeve 40 triệu (CK {M['disc_40tr']:.2%}) — SÁT RANH GIỚI: giá cao hơn P90 chỉ "
                f"{px / P['p90'] - 1:+.1%}. Ở cỡ 5 tỷ (CK {M['disc_5ty']:.2%}, ngoại suy) cũng TRÊN, giá/P90 {px / H5['P_post']['p90'] - 1:+.1%}. "
                "Nhãn không đổi so r2; không do đổi định nghĩa vùng (r1–r3 đều P10–P90). TERP so giá trị sau quyền: TRÊN ở cả hai cỡ."),
    ck_headline="sleeve 40 triệu đ (ADV120)",
    ck_ref_size=dict(size_ty=5.0, discount_adv120=round(M["disc_5ty"], 4), discount_adv250=round(L["ref_discount_adv250"], 4),
                     discount_adv60=round(L["ref_discount_adv60"], 4), pct_adv120=round(L["ref_pct_adv120"], 3),
                     in_sqrt_calibration_zone=L["ref_in_sqrt_zone"],
                     center_post=R(H5["center_post"]), p10=R(H5["P_post"]["p10"]), p50=R(H5["P_post"]["p50"]), p90=R(H5["P_post"]["p90"]),
                     pct_below=round(H5["pct_w_below_px"], 4), label=M["headline_ck5ty"]["label"]),
    ck_real_sleeve={k: round(v, 4) for k, v in L["sleeve_discount"].items()},
    adv250_median_ty=round(L["adv250_med_ty"], 2), adv120_median_ty=round(L["adv120_med_ty"], 2), adv60_median_ty=round(L["adv60_med_ty"], 2),
    px_vs_center=round(px / H["center_post"] - 1, 4), px_vs_p10=round(px / P["p10"] - 1, 4), px_vs_p90=round(px / P["p90"] - 1, 4),
    grid_desc=("5 trục: chế độ ngành CYCLICAL/ADMIN_GATED/STRUCTURAL (0,5/0,3/0,2, Bobby; mức quay về TB 1/0,5/0 [UL]) × DT TTM/2026E × "
               "biên chuẩn hoá 3 cách (lõi sửa GPM) × g 3/4/5% × ROE 15/20%; bội số áp E1=E0×(1+g); giá trị CUM-quyền; "
               f"CK sleeve 40tr; phân vị wpct mức kết cục (n={H['n']})"),
    center_vs_p50_note=(f"Tâm (kỳ vọng) {R(H['center_post'])} > P50 {R(P['p50'])}: đuôi phải do nhánh STRUCTURAL (max {R(H['max_post'])}); "
                        f"tham số trung tâm (ADMIN_GATED, TTM, norm 2023–TTM, g4%, ROE 17,5%) {R(M['headline']['center_param_post'])}. "
                        f"P10 do riêng nhánh CYCLICAL {M['headline']['p10_branch']}; quanh P90 {M['headline']['p90_branch']}."),
    assumptions=[
        dict(item="r = 13,5%", basis="13,5% + 1,0×(7,40% − 7,40%); lãi huy động 12T hiệu dụng 06/11 = 7,40% (cctg_12m 02/11/2026, deposit_rate_vn.py)"),
        dict(item="Trọng số chế độ ngành 0,5/0,3/0,2", basis="sector read VLXD nhẹ của Bobby 29/10 (đọc mù) — nhận định, không phải dữ liệu"),
        dict(item="Mức quay về TB biên 1,0/0,5/0,0 theo nhánh", basis="[UL] thiết kế nhóm nghiên cứu"),
        dict(item="Biên ròng chuẩn hoá (TB 2020–TTM / 2023–TTM / lệch biên gộp)", basis="BQ ticker_financial Revenue_P0/NP_P0 (fin_bq_scl.csv); GPM năm = Q4 của GPM_P0 TTM (bigquery_dictionary.json)"),
        dict(item="g 3/4/5%, ROE dài hạn 15/20%", basis="ước lượng, hai chiều đều"),
        dict(item="Bội số áp E1 = E0×(1+g)", basis="(1−g/ROE)/(r−g) = P/E kỳ tới (Gordon V0 = D1/(r−g)); E0 = TTM tới 30/09/2026"),
        dict(item="Phải thu Vincons 67,892 tỷ theo sổ sách", basis="BCTC HN Q3/2026 V.3 (đọc PDF scan bằng fitz render): 67.892.070.164 / 115.969.828.921 = 58,54%; dự phòng 0 cho khoản này; lỗ [UL] chỉ ở độ nhạy"),
        dict(item="Dự án dở dang Phả Lại + Vĩnh Hảo GĐ2 = giá vốn − nợ tài trợ = 0; cộng lại lãi vay nợ dự án vào E (lãi P&L thực 4,96%)",
             basis="BCTC HN Q3/2026 V.9: Phả Lại 177,999 + 12,652 tỷ, tách tro GĐ2 14,817 tỷ; chi phí đi vay Q3 5,167 tỷ / nợ 416,5 tỷ ×4"),
        dict(item="CK thanh khoản headline ở sleeve 40 triệu", basis="phương pháp đăng ký trước (½ spread Corwin–Schultz 120 phiên + σ√(Q/ADV120)); 5 tỷ = 213% ADV120 ngoài vùng √ ⇒ chỉ song song"),
        dict(item="Số cp cum 38.836.815; sau quyền 44.836.815; 75 tỷ tiền thu", basis="BCĐKT 30/09 vốn góp 388,368 tỷ; NQ 1363/NQ-HĐQT 26/10/2026 (6,0tr cp @12.500, 100:15,4453, ĐKCC 10/11)"),
    ],
    headline_vs_alternatives={
        "headline_E1_ck40tr": b(S["S5_ck_sleeve40"]),
        **{f"{k}[{ck}]": b(v) for k, d in A.items() if k != "skeptic_combo_check" for ck, v in d.items() if ck != "note"},
    },
    headline_choice_reason=("E1: công thức P/E nội tại đòi E kỳ tới — E0 là sai quy ước, không phải thận trọng có cơ sở. "
                            "CK 40tr: cỡ 5 tỷ ngoài vùng hiệu chỉnh luật √ (213% ADV) nên 4,45% là ngoại suy, không có cơ sở dữ liệu ⇒ song song. "
                            "Phải thu: không có dữ liệu cho xác suất lỗ ⇒ độ nhạy. Các biến thể đối xứng (TROUGH, nợ mệnh giá) không vào headline vì "
                            "sector read không có lớp TROUGH và nợ mệnh giá là khung cận dưới — báo song song, nhãn TRÊN ở mọi bản."),
    implied_by_price=dict(
        E0_normalized_ty=round(M["implied"]["E0_norm_implied_ty"], 1),
        vs=dict(E_ttm_with_cip_addback_ty=round(M["implied"]["E_ttm_with_cip_addback_ty"], 1), np_ttm_ty=round(M["implied"]["np_ttm_ty"], 1),
                np_2020_2025_ty=M["implied"]["hist_np_ty"]),
        r_implied_if_ttm_margin_permanent=round(M["implied"]["r_implied_structural_ttm_g4_roe175"], 4),
        deposit_rate_implied_pct=round(M["implied"]["deposit_implied_pct"], 2),
        note=("Giá 29.400 ngụ ý LN chuẩn hoá ~136 tỷ/năm vĩnh viễn (g4%, ROE 17,5%, r 13,5%) — cao hơn TTM 117,7 và gấp ~4× TB 2020–25, "
              "hoặc biên TTM đỉnh 7 năm giữ vĩnh viễn kèm r 12,77% (lãi huy động ~6,67%). Skeptic nêu 140,6 tỷ / r 11,1% ở quy ước E0 + CK 5 tỷ; "
              "chênh do quy ước, cùng hướng. Phản chứng: CFO 9T 9,9 tỷ vs LNST 94,4 tỷ.")),
    bridge_r2_to_r3=bridge,
    corrections_check=[
        dict(id="1 GPM_P0=TTM", verdict="ĐÚNG — áp", evidence="bigquery_dictionary.json GPM_P0 'TTM tại quý'; S1 tái lập 21.813/P90 26.672 trùng skeptic"),
        dict(id="2a E0→E1", verdict="ĐÚNG — áp vào headline", evidence=f"S4−S3 = {R(S['S4_E1']['center_post'] - S['S3_no_recv_axis']['center_post'])} đ/cp (skeptic ~880)"),
        dict(id="2b CK 5 tỷ vs sleeve", verdict="ĐÚNG — headline sleeve 40tr, 5 tỷ song song", evidence=f"S5−S4 = {R(S['S5_ck_sleeve40']['center_post'] - S['S4_E1']['center_post'])} đ/cp (skeptic ~840; ADV cập nhật 06/11)"),
        dict(id="2c trục phải thu [UL]", verdict="ĐÚNG — ra độ nhạy", evidence=f"S3−S2b = {R(S['S3_no_recv_axis']['center_post'] - S['S2b_recv_amt_bctc']['center_post'])} đ/cp (skeptic ~90)"),
        dict(id="2 gộp P90 ~28.800", verdict="ĐÚNG", evidence=f"P90 {R(P['p90'])}"),
        dict(id="2 IRR Phả Lại P90 ~29.350", verdict="KHÔNG tái lập được số — giữ số của tôi",
             evidence=f"cùng headline + trục IRR 10/13,5/17% (0,25/0,5/0,25): P90 {R(A['with_phalai_irr']['ck40tr']['p90'])} (< giá); "
                      "khoản IRR cộng Phả Lại 262,9×(IRR/r−1) không nhân (1+g); skeptic có thể nhân E1/khác trọng số — không đổi nhãn"),
        dict(id="2 TROUGH + nợ mệnh giá kéo tâm ~1.100–1.200", verdict="ĐÚNG hướng; độ lớn theo khung r3",
             evidence=(f"TROUGH {R(A['symmetric_trough']['ck40tr']['center_post'] - H['center_post'])}, nợ mệnh giá "
                       f"{R(A['par_debt']['ck40tr']['center_post'] - H['center_post'])}, gộp {R(A['trough_plus_par']['ck40tr']['center_post'] - H['center_post'])} đ/cp")),
        dict(id="3 câu 'không sát ranh giới' 5F §5", verdict="ĐÚNG — đã sửa trong ADDENDUM_5F.md", evidence=f"giá/P90 headline {px / P['p90'] - 1:+.1%}"),
        dict(id="4 cùng cơ sở cum/TERP; lịch quyền", verdict="ĐÚNG — đã làm; lịch xác nhận",
             evidence="NQ 1363/NQ-HĐQT 26/10/2026 (bản gốc PDF công ty): ĐKCC 10/11, chuyển nhượng quyền 17/11–03/12, đăng ký+nộp tiền 17/11–08/12 — hai mốc báo chí là hai hạn khác nhau, không mâu thuẫn; NQ không có cổ phiếu thưởng"),
        dict(id="5 BCĐKT từ PDF scan", verdict="ĐÃ KIỂM bằng fitz render + đọc ảnh",
             evidence="trang 1–2, 17, 19 BCTC HN Q3/2026: VCSH 533,638 (CĐKKS 2,022), vay NH 259,737 + DH 156,724, tiền 95,103, phải thu KH 115,970, Vincons 67,892, XDCB 206,627 — khớp hằng số lõi; LCTT (CFO 9,9) chưa đọc lại ở r3"),
    ],
    axes_included=["branch", "rev", "norm", "g", "roe"],
    axes_excluded=[
        dict(axis="lỗ phải thu Vincons 0/20/50% [UL]", reason="không có cơ sở dữ liệu cho xác suất lỗ (dự phòng 0, kiểm toán chấp nhận) ⇒ độ nhạy; song song with_recv_axis_UL"),
        dict(axis="IRR Phả Lại 10/13,5/17%", reason="luật 03/11 NPV 0 — loại cả hai chiều; song song with_phalai_irr"),
        dict(axis="nhánh TROUGH", reason="sector read không có lớp; song song symmetric_trough"),
        dict(axis="khung nợ theo mệnh giá", reason="khung cận dưới; song song par_debt / trough_plus_par"),
        dict(axis="pha loãng ESOP tương lai, vay cổ đông lớn 26 tỷ @10%", reason="quản trị ⇒ WARNING"),
    ],
    base_adjustments=[
        dict(item="Phả Lại + tách tro GĐ2 (XDCB 205,5 tỷ)", effect_dong_per_share=0, basis="giá vốn − nợ tài trợ = 0 (NPV 0)", source="BCTC HN Q3/2026 V.9"),
        dict(item="cộng lại lãi vay nợ tài trợ dự án vào E (4,96%)", effect_dong_per_share="~+1.700 đ/cp cum (kỳ vọng lưới lõi r3, trước E1)",
             basis="không vừa trừ nợ theo mệnh giá vừa trừ lãi qua P/E", source="KQKD Q3/2026 mã 24; BCĐKT vay 416,5 tỷ"),
    ],
    post_rights=dict(terp=round(M["terp"]), ck40tr=dict(center_post=R(M["post_rights"]["ck40tr"]["center_post"]), p10=R(M["post_rights"]["ck40tr"]["P_post"]["p10"]),
                                                        p90=R(M["post_rights"]["ck40tr"]["P_post"]["p90"]), label=M["post_rights"]["label_terp"]),
                     ck5ty=dict(center_post=R(M["post_rights"]["ck5ty"]["center_post"]), p90=R(M["post_rights"]["ck5ty"]["P_post"]["p90"]),
                                label=M["post_rights"]["label_terp_5ty"])),
    sens_r={k: dict(r=v["r"], center_post=R(v["post"]), pct=round(v["pct"], 4)) for k, v in M["sens_r"].items()},
    gordon=dict(g=0.04, roe_ttm=round(M["gordon"]["roe_ttm"], 4), value_E1_pre_ck=R(M["gordon"]["value_E1"]), note=M["gordon"]["note"]),
    warnings=[
        "Pha loãng: 17,3tr cp (2023) → 44,84tr sau quyền 100:15,4453 @12.500 (ĐKCC 10/11/2026, GDKHQ 09/11; NQ 1363); ESOP 0,92tr @10.000",
        "Vay 26 tỷ từ cổ đông lớn lãi 10% (bên liên quan)",
        "Phải thu tập trung: Vincons 67,89 tỷ = 58,5% phải thu KH (BCTC V.3), chưa dự phòng",
        "CFO 9T 9,9 tỷ vs LNST 94,4; nợ ròng 321 tỷ; biên ròng TTM 12,7% đỉnh 7 năm",
        "Chưa thấy tin xử phạt/khởi tố SCL: WebSearch 05/11/2026 và 08/11/2026 (stockbiz, cafef, baophapluat) — WebSearch ≠ CBTT sàn",
    ],
    open_issues=[
        "Không có cơ cấu DT theo mảng, backlog, công suất từng dây chuyền",
        "Phả Lại: chưa có giá/sản lượng/hợp đồng đầu ra ⇒ NPV 0",
        "Trọng số chế độ ngành và mức quay về TB là nhận định/[UL]",
        "Số IRR P90 29.350 của skeptic chưa tái lập (tôi 28.902)",
        "LCTT Q3 (CFO 9,9) chưa đọc lại từ PDF ở r3",
    ],
    fearbuy_sleeve_eligible="KHÔNG — giá TRÊN vùng, không phải trạng thái sợ hãi",
    change_vs_r2=dict(center=R(H["center_post"] - 22769), center_pct=round(H["center_post"] / 22769 - 1, 4), label_changed=False),
    source_calc="SCL/calc_r3/model_scl_r3.py → model_scl_r3_out.json/.txt (chạy 2 lần trùng byte); make_summary_r3.py",
    lock="SCL/calc_r3/LOCK_r3_md5.txt",
)
json.dump(out, open(os.path.join(HERE, "..", "SUMMARY.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ("center_post_liq", "p10_out", "p50_out", "p90_out", "label", "change_vs_r2")}, ensure_ascii=False))
