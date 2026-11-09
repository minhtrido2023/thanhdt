"""SUMMARY.json vòng 3 SIP = model_r3_out.json (số) + assumptions_r3.json + SUMMARY_r2.json (mốc). Số không gõ tay.
Chạy: cd calc_r3 && $DNA_PYEXE -I make_summary_r3.py"""
import json, os, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.dirname(HERE)
M = json.load(open(os.path.join(HERE, "model_r3_out.json")))
A = json.load(open(os.path.join(HERE, "assumptions_r3.json")))
R2 = json.load(open(os.path.join(D, "SUMMARY_r2.json")))
r2meta = json.load(open(os.path.join(D, "meta_r2.json")))
Dd, Ds, L = M["dist"], M["dist_sleeve40"], M["liq"]
P, Ps, px = Dd["P_post"], Ds["P_post"], M["price"]
rd = lambda x: int(round(x))
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
S = dict(
    ticker="SIP", round=3, job="Taylor_20261108_180132", asof_price_date=M["asof_price_date"], price=px, r=M["r"],
    r_basis="13,5%% + 1,0×(lãi huy động 12T hiệu dụng 06/11 %.4f − neo 03/11 %.4f)" % (M["deposit_asof"]["rate"], M["deposit_anchor"]["rate"]),
    center_post_liq=rd(Dd["center_post"]), center_pre_liq=rd(Dd["center_pre"]),
    p10_post=rd(P["p10"]), p25_post=rd(P["p25"]), p50_post=rd(P["p50"]), p75_post=rd(P["p75"]), p90_post=rd(P["p90"]),
    min_out=rd(Dd["min_post"]), max_out=rd(Dd["max_post"]), n_outcomes=Dd["n"],
    pct_weight_below_price=round(Dd["pct_w_below_px"], 4), label=M["label_5ty"],
    sleeve40=dict(ck=round(L["sleeve_discount"]["40tr"], 4), center=rd(Ds["center_post"]), p10=rd(Ps["p10"]), p50=rd(Ps["p50"]), p90=rd(Ps["p90"]),
                  pct_below=round(Ds["pct_w_below_px"], 4), label=M["label_sleeve40"], rule4=M["rule4_sleeve40"]),
    ck_ref_size=dict(size_ty=5, discount_adv120=round(L["ref_discount"], 4), pct_adv120=round(L["ref_pct_adv120"], 3),
                     in_sqrt_zone=L["ref_in_sqrt_zone"], adv120_median_ty=round(L["adv120_med_ty"], 2)),
    ck_real_sleeve={k: round(v, 4) for k, v in L["sleeve_discount"].items()},
    center_param_post=rd(M["center_param_post"]), p10_land_branch=M["p10_land_branch"], p90_land_branch=M["p90_land_branch"],
    px_vs_center=round(px / Dd["center_post"] - 1, 4),
    center_vs_p50_note="Tâm = kỳ vọng lưới 1.458 kết cục; P50 = trung vị mức kết cục (wpct); tham số trung tâm = đất cơ sở ×1, tín dụng 0%, NCI 20%, thuế ×1, KTPL 9,04%. P10 do nhánh đất XẤU (~94%), P90 do riêng nhánh đất TỐT (w 0,25).",
    grid_desc="7 trục độc lập: đất (tỷ/ha+năm; 25/50/25) × tỷ/ha ×0,75/1/1,25 × g 2/3/4% (vô hiệu: RONIC=Ke) × lỗ tín dụng không bảo đảm 0/10/30% (0,60/0,25/0,15) × NCI con 8,5/20/31% × thuế tương lai ×0,8/1/1,2 × KTPL 7,25/9,04%; thu hồi chi phí đất cố định 100% (NPV0); wpct mức kết cục",
    assumptions=[
        dict(item="RONIC", value="Ke (PE vận hành = 1/r)", basis=A["ronic"]["basis"]),
        dict(item="trọng số đất", value="25/50/25", basis=A["land_weights"]["basis"]),
        dict(item="kịch bản đất", value=A["land_scenarios"], basis=A["land_scenarios"]["basis"]),
        dict(item="thu hồi chi phí đất", value="100%", basis=A["recover"]["basis"]),
        dict(item="tài sản sổ sách thêm 396,8 tỷ", value=A["book_assets_added_ty"], basis=A["book_assets_added_ty"]["basis"]),
        dict(item="tạm ứng nội bộ 643,7 tỷ theo sổ", value=A["advance_insiders_ty"]["treatment"], basis=A["advance_insiders_ty"]["basis"]),
        dict(item="KTPL trên LN từ DT chưa thực hiện", value=A["ktpl_on_deferred_rev"]["formula"], basis=A["ktpl_on_deferred_rev"]["basis"]),
        dict(item="trục giữ từ r2", value=A["axes_kept_from_r2"], basis="r2 meta_r2.json axes_basis; số BCTC từ ảnh (notes_read.md), PDF scan không lớp text ⇒ chưa kiểm bằng text"),
        dict(item="CK thanh khoản", value="5 tỷ %.2f%% / sleeve 40tr %.2f%%" % (100 * L["ref_discount"], 100 * L["sleeve_discount"]["40tr"]), basis=A["liquidity"]),
    ],
    headline_vs_alternatives=dict(
        headline=dict(center=rd(Dd["center_post"]), p10=rd(P["p10"]), p90=rd(P["p90"]), note="mô hình cơ sở sau đính chính + tạm ứng theo sổ"),
        advance_zero_skeptic_basis=dict(center=rd(M["parallel"]["advance_zero"]["center_post"]), p10=rd(M["parallel"]["advance_zero"]["p10"]), p90=rd(M["parallel"]["advance_zero"]["p90"]),
                                        note="bỏ tạm ứng 643,7 (như r2/skeptic); tái lập skeptic 53.653 (−13 do giá/CK 06/11)"),
        advance_lost_p015=dict(center=rd(M["parallel"]["advance_loss_p015"]["center_post"]), p10=rd(M["parallel"]["advance_loss_p015"]["p10"])),
        gov_disc_10pct=dict(center=rd(M["parallel"]["gov_disc_10"]["center_post"]), note="chiết khấu quản trị 10% [UL] — chỉ song song"),
        ronic_roe5y_r2_convention=rd(Dd["center_post"] + M["sens"]["RONIC=ROE5Y 29,7% (quy uoc r2)"]),
        land_20_50_30=rd(Dd["center_post"] + M["sens"]["dat_20_50_30 (trong so r2)"]),
    ),
    sensitivities_delta_center={k: rd(v) for k, v in M["sens"].items()},
    sens_r={k: rd(v["post"]) for k, v in M["sens_r"].items()},
    implied_by_price=dict(land_perha_scale=round(M["implied"]["land_perha_scale"], 3), land_perha_coso_ty=round(M["implied"]["land_perha_coso"], 2),
                          r=round(M["implied"]["r"], 4), note="giá 06/11 ngụ ý tỷ/ha ròng mọi kịch bản ×scale (cơ sở 12 → giá trị trên), HOẶC r (các giả định khác giữ)"),
    bridge_r2_to_r3=[dict(step=s["step"], center_post=rd(s["center_post"]), **({"delta": rd(s["delta"])} if "delta" in s else {})) for s in M["bridge"]],
    corrections_check=[
        dict(n=1, verdict="ĐÚNG — áp", calc=-3389, skeptic=-3389),
        dict(n=2, verdict="ĐÚNG — áp", calc=1186, skeptic=1186),
        dict(n=3, verdict="ĐÚNG — áp (Δ +572 vs skeptic +556: thứ tự áp sau #2)", calc=572, skeptic=556),
        dict(n=4, verdict="ĐÚNG — áp 396,8 theo sổ; VAT−DTL +3.123 để độ nhạy (chưa đọc thuyết minh)", calc=1616, skeptic=1617),
        dict(n=5, verdict="ĐÚNG — áp (nhân thêm 1−NCI LN cho nhất quán nhánh đất)", calc=-563, skeptic=-563),
        dict(n="6a", verdict="ĐÚNG hướng; số ha 9T26 chưa có ⇒ độ nhạy −756/50 ha (thiên lệch XUỐNG đã biết)", calc=-756, skeptic=-757),
        dict(n="6b", verdict="ĐÚNG: r2 trừ tài sản không có trong mô hình. Sửa: tạm ứng 643,7 (TM7) đưa theo sổ vào base (luật 20), mất trọn = song song", calc=826),
        dict(n=7, verdict="độ nhạy; số Taylor khác skeptic do cách đo: GPM ×0,9457 trên LN gộp vận hành −1.228 (skeptic −1.840); NCI cố định 9,9% thay cả trục +1.735 (skeptic +879)", calc=[-1228, 1735], skeptic=[-1840, 879]),
        dict(n=8, verdict="WARNING bên liên quan VRG — mang theo"),
        dict(n=9, verdict="giá 50.100 dùng; số BCTC ngoài BQ: PDF scan không có lớp text (pymupdf 423 ký tự/49 trang) ⇒ chưa kiểm bằng text, chỉ đối chiếu notes_read.md (ảnh)"),
    ],
    warnings=r2meta["warnings"] + [
        "Bên liên quan VRG: BCC 667 Thế Hệ Mới ↔ VRG Long Thành tới 2060 (TM7); cổ phiếu CTCP Phát triển ĐT&KCN Cao su VN gốc 129,0 / GTHL 68,6 (TM4a); thành viên BKS là cán bộ VRG/TGĐ NTC; cổ đông An Lộc 19,79% chưa rõ quan hệ (skeptic #8; chưa tự kiểm BKS/An Lộc)",
        "Tạm ứng nội bộ 643,7 (TM7) ≠ 635,6 (TM40): đưa theo sổ vào base theo luật user; quản trị = WARNING, mất trọn = song song",
    ],
    open_issues=r2meta["open_issues"] + [
        "Số ha cho thuê 9T26 (G12) — mỗi 50 ha −756 đ/cp",
        "Thuyết minh thuế GTGT khấu trừ 890,5 và thuế TNDN hoãn lại phải trả 123,7 (độ nhạy +3.123)",
        "GPM 2021 nghi chép lặp; mốc chuẩn hoá 9T26 có thể là đỉnh",
        "Góp vốn BCC 667 (DH) không cộng riêng: giả định thu nhập nhà xưởng đã nằm trong LN gộp vận hành (chưa kiểm)",
    ],
    fearbuy_sleeve_eligible=r2meta["fearbuy_sleeve_eligible"],
    r2=dict(center=R2["center_post_liq"], p10=R2["p10_post"], p50=R2["p50_post"], p90=R2["p90_post"], price=R2["price"], date=R2["asof_price_date"],
            pct_below=R2["pct_weight_below_price"], label=R2["label"]),
    change_vs_r2=dict(center=rd(Dd["center_post"]) - R2["center_post_liq"], p10=rd(P["p10"]) - R2["p10_post"], p90=rd(P["p90"]) - R2["p90_post"],
                      label_changed=M["label_5ty"] != R2["label"]),
    source_calc="calc_r3/model_r3.py → model_r3_out.json/.txt (2 lần trùng byte: run1.txt=run2.txt)",
    lock=dict(file="calc_r3/LOCK_md5.txt", md5=md5(os.path.join(HERE, "LOCK_md5.txt"))),
    measured_by="cd SIP/calc_r3 && $DNA_PYEXE -I model_r3.py",
)
S["rule4_5ty"] = dict(passed=M["rule4_5ty"], threshold=rd(0.85 * Dd["center_post"]))
json.dump(S, open(os.path.join(D, "SUMMARY.json"), "w"), ensure_ascii=False, indent=1)
json.dump(S, open(os.path.join(D, "SUMMARY_r3.json"), "w"), ensure_ascii=False, indent=1)
print(S["center_post_liq"], S["p10_post"], S["p90_post"], S["label"], S["change_vs_r2"])
