"""Ghi TV1/SUMMARY.json vòng 3 từ calc/model_tv1_r3_out.json (r2 đã backup SUMMARY_r2.json). Chạy: python3 -I make_summary_r3.py"""
import json, os
H = os.path.dirname(os.path.abspath(__file__)); T = os.path.dirname(H)
o = json.load(open(os.path.join(H, "model_tv1_r3_out.json"))); r2 = json.load(open(os.path.join(T, "SUMMARY_r2.json")))
D = o["dist"]; P = D["P_post"]; L = o["liq"]; px = o["price"]; S = o["parallel"]
rd = lambda x: int(round(x))
def var(name, d, note):
    return dict(variant=name, center=rd(d["center_post"]), p10=rd(d["P_post"]["p10"]), p50=rd(d["P_post"]["p50"]), p90=rd(d["P_post"]["p90"]),
                pct_weight_below_price=round(d["pct_w_below_px"], 4), note=note)
s = dict(ticker="TV1", round=3, job="Taylor_20261108_142024", asof_price_date=o["asof_price_date"], price=px, r=o["r"], r_anchor=o["r_info"],
         center_pre_liq=rd(D["center_pre"]), center_post_liq=rd(D["center_post"]), p10_post=rd(P["p10"]), p50_post=rd(P["p50"]), p90_post=rd(P["p90"]),
         p10_out=rd(P["p10"]), p50_out=rd(P["p50"]), p90_out=rd(P["p90"]), p25_out=rd(P["p25"]), p75_out=rd(P["p75"]),
         min_out=rd(D["min_post"]), max_out=rd(D["max_post"]), pct_weight_below_price=round(D["pct_w_below_px"], 4), n_outcomes=D["n"],
         w_floor_zero=o["w_floor_zero"], center_param_post=rd(o["center_param_post"]),
         label=o["label"], label_note="Nhãn không đổi so r2 (TRONG); định nghĩa vùng P10–P90 không đổi. Giá cao hơn tâm {:+.1%}, {:.1%} trọng số kết cục dưới giá. Ngưỡng: DƯỚI khi giá < {:,} ; TRÊN khi giá > {:,}.".format(px / D["center_post"] - 1, D["pct_w_below_px"], rd(P["p10"]), rd(P["p90"])).replace(",", "."),
         pct_price_vs_center=round(px / D["center_post"] - 1, 4), pct_center_below_price=round(1 - D["center_post"] / px, 4),
         liq_discount_ref=round(L["ref_discount"], 4), liq_ref_size_ty=5.0,
         ck_ref_size=dict(size_ty=5.0, discount_adv120=round(L["ref_discount"], 4), discount_adv250=round(L["ref_discount_adv250"], 4), discount_adv60=round(L["ref_discount_adv60"], 4),
                          pct_adv120=round(L["ref_pct_adv120"], 3), in_sqrt_calibration_zone=L["ref_in_sqrt_zone"]),
         ck_real_sleeve={k: round(v, 4) for k, v in L["sleeve_discount"].items()},
         adv250_median_ty=round(L["adv250_med_ty"], 2), adv120_median_ty=round(L["adv120_med_ty"], 2), adv60_median_ty=round(L["adv60_med_ty"], 2),
         grid_desc="5 trục: giá PPA SB5 2027+ 949/600/520/440/340 (0,05/0,25/0,30/0,20/0,20) × biên tư vấn 5/8/11/14% (0,20/0,30/0,40/0,10) × sản lượng 175/187,5/200 GWh (đều) × thời điểm áp bậc thấp đúng 2027 / lùi 1 / lùi 2 năm (0,80/0,15/0,05) × VLĐ tư vấn 45/49/53% ΔDT (đều); KHÔNG truy thu hồi tố trong base (r3); sàn vốn chủ 0; wpct mức kết cục (n=540); r 13,5%; KTPL 20%",
         center_vs_p50_note="Tâm 16.740 > P50 16.150 (đuôi phải PPA 949/600 + tư vấn 14%); tham số trung tâm (520|11%|187,5|2027|49%) 19.126 cao hơn tâm vì 520 > PPA kỳ vọng 509 và 50% xác suất biên tư vấn ≤ 8%. P10 do PPA 340 (55% trọng số quanh P10) + 440 (32%) với tư vấn 5–8%; P90 do PPA 520 (43%) với tư vấn 14% (63%). Không kết cục nào chạm sàn 0 (r2: 5,5% — toàn bộ do nhánh truy thu).",
         axes_included=o["axes_included"], axes_excluded=o["axes_excluded"], base_adjustments=o["base_adjustments"],
         assumptions=[
            dict(item="r = 13,5% + 1,0×(lãi huy động 12T hiệu dụng − 7,40%)", value=o["r"], basis="deposit_rate_vn.effective_deposit_rate(2026-11-06) = 7,40% (cctg_12m 02/11) ⇒ r 13,50%"),
            dict(item="giá tham chiếu", value=px, basis="đóng cửa 06/11/2026 tav2_bq.ticker (Price=Close=20.400; r3data/px_tv1_20261106.csv)"),
            dict(item="phân bố giá PPA ròng 2027+", value="949/600/520/440/340 @0,05/0,25/0,30/0,20/0,20 (kỳ vọng 509)", basis="SKEPTIC_BLIND B1 [UL]; 340 = dự thảo HĐ 05/2018 được EVN NQ 286 + Cục ĐTĐL 1374 chấp thuận (chưa thấy bản ký); 500–600 = lời lãnh đạo qua KBSV 17/04/2026 (chưa kiểm bản gốc)"),
            dict(item="thời điểm hạ bậc", value="2027 0,80 / lùi 1 năm 0,15 / lùi 2 năm 0,05", basis="lãnh đạo 'từ 2027'; chiều lùi có dữ liệu: mốc 2022 của dự thảo 2018 đã trôi ≥5 năm; [UL] xác suất"),
            dict(item="truy thu hồi tố 2022–26", value="KHÔNG trong base", basis="không có văn bản đòi; EVN trả ~949 suốt 2022–25 đã kiểm toán; HĐ 2018 là dự thảo; → S1/S2"),
            dict(item="biên tư vấn", value="5/8/11/14% @0,20/0,30/0,40/0,10", basis="SKEPTIC_BLIND B3 [UL]; lịch sử (đo lại đúng cách r3): 2022 2–4%, 2023 4–7%, 2024 4–6%, 2025 8–10%, 9T26 11–17%"),
            dict(item="sản lượng", value="175/187,5/200 GWh đều", basis="BQ dài hạn 181–187 (2015–25 BQ 187)"),
            dict(item="KTPL", value=0.20, basis="đo FY23/24/25 = 40,9%/19,7%/20,0%; quỹ trích theo tháng lương (BCTC FY25 TM18c) ⇒ không có cơ sở hạ xuống 10–15%"),
            dict(item="VLĐ tư vấn", value="45/49/53% ΔDT", basis="đo 45–53% (SKEPTIC_BLIND N2)"),
            dict(item="tiền ròng điều chỉnh", value=rd(o["base_adjustments"][0]["effect_dong_per_share"]), basis="nợ trên sổ Q3/2026 + KTPL đo được; LNST Q4 50 tỷ [UL]"),
            dict(item="CK thanh khoản", value=round(L["ref_discount"], 4), basis="nửa spread CS + σ√(Q/ADV120) @5 tỷ — ngoài vùng hiệu chỉnh √ (797% ADV)"),
         ],
         headline_vs_alternatives=[
            var("HEADLINE r3: không truy thu, timing 0,80/0,15/0,05", D, "mô hình cơ sở sau đính chính"),
            var("S1 truy thu nhất quán chỉ trong nhánh 340, P(truy thu|340)=0,10", S["S1_nhatquan_p340_010"], "skeptic phương án 1; P chung 0,02"),
            var("S1k = S1 với timing nhánh khác 0,70/0,15/0,05 chuẩn hoá (khớp skeptic 16.570)", S["S1_skeptic_timing"], "đối chiếu số skeptic"),
            var("S2 truy thu P chung 0,10 dồn vào nhánh 340 (P|340=0,50)", S["S2_nhatquan_p340_050"], "skeptic phương án 2 (15.734 / P10 3.522)"),
            var("S2k = S2 với timing skeptic", S["S2_skeptic_timing"], "đối chiếu"),
            var("S3 r2 cơ học (truy thu nhân chéo độc lập) trên dữ liệu 06/11", S["S3_r2_cohoc"], "đã bác: kết cục tự mâu thuẫn (PPA 949/600 + truy thu bậc 340)"),
            var("S0 không trục thời điểm", S["S0_khong_thoi_diem"], ""),
            var("S4 có cấm thầu EVN 3 năm −50% p0,35", S["S4_cam_thau"], "vụ án — WARNING, ngoài tâm"),
            dict(variant="KTPL 10/15/25%", center={k: rd(v) for k, v in o["ktpl_sens"].items()}, note="10–15% không có cơ sở dữ liệu (đo ≥ 19,7%)"),
            dict(variant="độ nhạy r ±50/±100bp β1", center={k: rd(v["post"]) for k, v in o["sens_r"].items() if k.startswith("b1.0")}),
         ],
         implied_by_price=dict(price=px, ppa_flat_at_consult_expect=round(o["implied"]["ppa_at_consult_expect"]), ppa_flat_at_consult_11pct=round(o["implied"]["ppa_at_consult_11pct"]),
                               ppa_flat_at_consult_14pct=round(o["implied"]["ppa_at_consult_14pct"]), ppa_expect_grid=round(o["ppa_expect"]),
                               note="Giá 20.400 ngụ ý giá PPA ròng phẳng 2027+ ≈ 623 đ/kWh (tư vấn ở kỳ vọng) hoặc ≈ 547 (tư vấn 11% vĩnh viễn) — trên dải lãnh đạo 500–600 (tư vấn kỳ vọng) và xa mức văn bản duy nhất 340; hoặc tư vấn 14% vĩnh viễn với PPA ≈ 335. Không có truy thu, không cấm thầu."),
         bridge_r2_to_r3=[
            dict(step="r2 (giá 19.600 @04/11, CK 4,02%)", center=r2["center_post_liq"], p10=r2["p10_out"], p90=r2["p90_out"], why="bản r2"),
            dict(step="dữ liệu giá 06/11 (CK @5 tỷ 4,02% → {:.2%}), giữ cơ chế r2".format(L["ref_discount"]), center=rd(S["S3_r2_cohoc"]["center_post"]), p10=rd(S["S3_r2_cohoc"]["P_post"]["p10"]), p90=rd(S["S3_r2_cohoc"]["P_post"]["p90"]),
                 why="cửa sổ thanh khoản mới (σ, spread); r không đổi 13,5%"),
            dict(step="bỏ truy thu khỏi base, trọng số 0,10 → 'đúng 2027'", center=rd(D["center_post"]), p10=rd(P["p10"]), p90=rd(P["p90"]),
                 why="TOP5_CORRECTIONS §TV1 đ.1–3 đã kiểm: nhân chéo độc lập tự mâu thuẫn; không có văn bản đòi; HĐ 2018 là dự thảo ⇒ sang S1/S2"),
            dict(step="KTPL: giữ 20% (KHÔNG áp độ nhạy 15/10% vào base)", center=rd(D["center_post"]), why="đo FY23/24/25 = 40,9/19,7/20,0% ⇒ đ.5 bác phần 'hạ KTPL'; đ.5 phần biên lịch sử: đúng (core sai 2022–23) nhưng không đổi lưới"),
         ],
         corrections_check=[
            dict(n=1, verdict="ĐÚNG", evidence="S1k 16.571/P10 8.414; S2k 15.702/P10 3.515 (skeptic 16.570/8.420; 15.734/3.522 — lệch do CK 4,21% vs 4,02%)"),
            dict(n=2, verdict="ĐÚNG", evidence="không có văn bản đòi truy thu; core v2 dòng [N1] 'KHÔNG vào tâm'; r2 đưa vào không có thông tin mới"),
            dict(n=3, verdict="ĐÚNG — r2 §1 'đã ký' SAI", evidence="README tv1_sb5_ppa_price_20261013 dòng 17–31: 'Hợp đồng sửa đổi, bổ sung số 05' là DỰ THẢO được EVN NQ 286 + Cục ĐTĐL 1374 chấp thuận; 'phụ lục 05 hoặc không ký như dự thảo, hoặc mốc hạ bậc đã lùi'; phụ lục PPA hiện hành KHÔNG TÌM THẤY; LEGAL_PPA_20261102 dòng 6–7 'cần văn bản gốc'"),
            dict(n=4, verdict="ĐÚNG", evidence="dd_TV1_20261102/REPORT.md §7: VnExpress 02/07/2026 '13 công ty bị xác định có liên quan' gồm TV1; 'EVNNPT và nhà thầu đều có sai phạm' — thêm vào WARNING r3"),
            dict(n=5, verdict="MỘT PHẦN: KTPL — SAI hướng; biên lịch sử — ĐÚNG", evidence="KTPL FY23/24/25 = 40,9/19,7/20,0% (BCTC FY25 TM17-18, H1/26 TM22), trích theo tháng lương ⇒ 15/10% không có cơ sở, giữ 20%, báo độ nhạy. Biên: EBITM_P0 là TTM (dictionary 08/11) ⇒ core 2022 −19%…−17% sai, đúng +2%…+4%; 2023 +4…+7%; 2024–25 không đổi"),
            dict(n=6, verdict="ĐÚNG", evidence="TV1 là scandal cá nhân (nhóm a) ⇒ §2; giá ngụ ý calc 547–623 (skeptic 558–631)"),
         ],
         warnings_added=["VnExpress 02/07/2026: TV1 trong '13 công ty bị xác định có liên quan'; 'EVNNPT và nhà thầu đều có sai phạm' (nguồn REPORT 02/11 §7)",
                         "Thiên lệch xác nhận: TV1 đang trong plan SELL — định giá r3 KHÔNG neo vào quyết định bán; r3 tâm TĂNG (15.379→16.740) dù đi ngược chiều plan"],
         sleeve_eligibility="Không đủ điều kiện fear-buy theo calculated_fear_state_backstop §2 (nhóm (a) scandal cá nhân — r2 dẫn nhầm §2.5): giá > tâm, vụ án chưa kết luận",
         gordon=o["gordon"], sens_r=o["sens_r"], ktpl_hist=o["ktpl_hist"], margin_hist_check=o["margin_hist_check"],
         change_vs_r2=dict(center=rd(D["center_post"]) - r2["center_post_liq"], center_pct=round(D["center_post"] / r2["center_post_liq"] - 1, 4),
                           p10=rd(P["p10"]) - r2["p10_out"], p90=rd(P["p90"]) - r2["p90_out"], label_r2=r2["label"], label_r3=o["label"]),
         files=dict(report="REPORT_r3.md", calc="calc/model_tv1_r3.py", out="calc/model_tv1_r3_out.json|txt", lock="calc/LOCK_r3_md5.txt", summary_prev="SUMMARY_r2.json"))
json.dump(s, open(os.path.join(T, "SUMMARY.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(dict(center=s["center_post_liq"], p10=s["p10_out"], p90=s["p90_out"], label=s["label"], change=s["change_vs_r2"]), ensure_ascii=False))
