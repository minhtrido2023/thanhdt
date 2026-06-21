---
name: v23-audit-2014-now-deliverable
description: V2.3 go-live re-simulated 2014→now into ONE BQ-auditable file; auditable CAGR 21.94% < published 26.3% (intraday fills dropped)
metadata: 
  node_type: memory
  type: project
  originSessionId: 2ef717ab-5c78-4933-9acd-888a2ecf9450
---

User ([REDACTED]12) muốn re-verify mọi con số V2.3 bằng cách chạy lại go-live config từ 2014→nay và xuất MỘT file để một bot khác (chỉ đọc file + BQ thô) dò lại từng VND → tự xác nhận CAGR/Sharpe/MaxDD.

**Script**: `pt_v23_audit_2014.py` — sao chép NGUYÊN cấu hình go-live `pt_v22_dt5g.py` (BAL 25B + LAG 25B + CAPIT v2 + LAG-allocator band ±10pp + DT5G state) nhưng START=2014-01-02, mọi giá đọc trực tiếp từ `tav2_bq.*`.

**Output (1 file)**: `data/v23_golive_audit_2014_now.csv` (~13.3k dòng), chia `record_type`: META (quy trình verify), EVENT_CAPIT (18 washout), TX (10,074 gd: cổ phiếu+ETF+MTM), REBAL (33 lần), DAILY (3,101 phiên, ledger+allocator+VNI), ANNUAL, METRIC (+self-check).

**Verifier**: `data/v23_audit_spotcheck.py` (đóng vai bot ngoài) — PASS: 660 giá vs BQ 0 mismatch; đẳng thức số tiền ~1e-16; **cash-flow identity mỗi sổ/ngày = 0 VND**; allocator replay 0 VND; CAGR/Sharpe/MaxDD dựng lại từ DAILY khớp tuyệt đối.

**KẾT QUẢ auditable 2014→[REDACTED]11 (12.44y)**: Final 589.63B từ 50B, **CAGR 21.94% / Sharpe(252) 1.59 / MaxDD −23.7% / Calmar 0.92** (VNINDEX B&H 10.76%/0.65/−45.3%). MaxDD episode −23.7% tại 2023-05-11. Annual: 2021 +104%, 2022 −18.6%, 2025 +44.6%, 2026 YTD −5.4%.

⚠️ **Gap quan trọng**: auditable CAGR 21.94% < mốc công bố V2.3A ~26.3% (Sharpe 1.80/DD−18.3%). Lý do = **bỏ alt-fill nội phiên (ATC/11:15 từ pkl cục bộ, KHÔNG có trên BQ → không kiểm toán được)**; audit chỉ khớp T+1 Open. Logic chiến lược giữ nguyên 100%. Tức bản auditable bảo thủ hơn ~4pp CAGR + DD xấu hơn (−23.7 vs −18.3) nhưng mỗi VND truy vết được. Khác biệt thứ yếu: audit đọc BQ live thay panel `v4f_panel_2014.csv`.

**⚠️ ĐÍNH CHÍNH fill ([REDACTED]12)**: gap 26.29→21.94 KHÔNG phải do intraday fill (tôi quy sai lượt đầu). Verified: champion V2.3C (pt_v22_capit_v21.py) + allocator V2.3A (pt_onewallet_allocator.py) cho số công bố 25.77/26.29 ĐỀU dùng `t1_open_exec=True, KHÔNG entry_alt_prices` = T+1 Open thuần. Intraday `v4_hybrid` CHỈ trong live-forward pt_v22_dt5g.py (data ~2023+, ảnh hưởng cả-kỳ nhỏ). → Gap thật = **panel curated `v4f_panel_2014.csv` + hardcoded CAPIT events vs BQ-live + live-washout**, KHÔNG phải execution.

**Script tham số hóa MODE** (`python pt_v23_audit_2014.py v23a|v23c`): v23a=allocator, v23c=static 50/50 plain-sum. Khác biệt DUY NHẤT giữa 2 file = quy tắc gộp sổ → cô lập đóng góp allocator. Spot-check nhận file qua argv2 + tự detect mode từ META.

**BẢNG SO SÁNH cùng harness audit (T+1 Open, BQ-thuần, FULL 2014→now)**:
| | published (curated panel) | AUDIT (BQ-live) | gap |
|---|---|---|---|
| V2.3C CAGR/Sh/DD | 25.77%/1.65/~−20% | **21.38%/1.52/−23.5%** | −4.39pp |
| V2.3A CAGR/Sh/DD | 26.29%/1.80/−18.3% | **21.94%/1.59/−23.7%** | −4.35pp |
(V2.3C file `data/v23c_golive_audit_2014_now.csv` 556.59B; V2.3A `data/v23_golive_audit_2014_now.csv` 589.63B; VNINDEX 10.76%/0.65/−45.3%)

**BẢNG 3 BẢN cùng harness audit (BQ-live, T+1 Open, FULL 2014→now)**:
| bản | CAGR | Sharpe | MaxDD | Calmar | Final |
|---|---|---|---|---|---|
| **V2.2-base** (no CAPIT) | 21.23% | 1.58 | **−18.5%** | **1.14** | 548.05B |
| **V2.3C** (+CAPIT static) | 21.38% | 1.52 | −23.5% | 0.91 | 556.59B |
| **V2.3A** (+CAPIT +alloc) | 21.94% | 1.59 | −23.7% | 0.92 | 589.63B |
(`data/v22base_audit_2014_now.csv` / `v23c_…` / `v23_golive_…`; VNINDEX 10.76/0.65/−45.3)

**4 phát hiện cốt lõi**:
1. **Data-source penalty ≈ −4.4pp CAGR gần KHÔNG ĐỔI** giữa A và C → phép DỜI MỨC, không đảo ranking. Panel curated lạc quan ~4pp CAGR + ~5pp DD.
2. **Edge allocator +0.56pp CAGR SỐNG SÓT** (v23a−v23c; published +0.52pp ≈ khớp); allocator gỡ lại Sharpe CAPIT làm mất (1.52→1.59).
3. **CAPIT: tín hiệu TỐT, nhưng MỘT cú đuôi phá tổng** (đào sâu per-event [REDACTED]12, `data/capit_event_diagnostic.py`): gộp CAPIT chỉ +0.15pp CAGR & DD −18.5→−23.5 LÀ DO **một sự kiện 2022-04-19** (CRISIS sz1.0) giải ngân **245B (lớn nhất, gấp nhiều lần)** vào ĐẦU gấu-grinding 2022 → −19% = **−47B**, nuốt gần hết +55B của các event tốt. **Per-event: win 67-73%, ret +14-66%** (2014 +32, 2018-07 +66, 2025-04 +20, 2025-10 +19...). RAW VNINDEX fwd60 sau washout dương hầu hết (+13/+16/+20/+13%); CHỈ 2 cú âm: E9 2022-04-19 (fwd120 −26%, falling knife) & E6 2020-02-03 (ngay trước COVID, fwd60 −17%). **COUNTERFACTUAL bỏ riêng E9: deploy 393B net +54.8B = +14.0%, win 73%** (vs all-events +1.2%). → CAPIT là CƠ HỘI MUA THẬT; lỗi là **SIZING**: CRISIS→size 1.0→sized trên free-cash, mà CRISIS = books đã về tiền mặt nên free-cash TỐI ĐA → đặt cược LỚN NHẤT đúng lúc nguy hiểm nhất (cú knife đầu gấu-grinding, dd52w còn nông −8% nên guard không bắt). Fix có nguyên tắc (không curve-fit ngày): **cap deploy mỗi event** (vd ≤15-20% book) hoặc anti-martingale (giảm size khi free-cash tối đa), KHÔNG re-tune né riêng 2022-04-19. ⚠️ v23c dùng live-washout 18 events (published hardcoded 14); nhưng kết luận signal-tốt/sizing-lỗi vững trong harness.
4. **Champion risk-adjusted trên data thật = V2.2-base** (Calmar 1.14, DD −18.5%, Sharpe 1.58 ≈ V2.3A). V2.3A chỉ thắng ở CAGR tuyệt đối (+0.71pp) nhưng phải nuốt DD −23.7%. → "version tốt nhất" tuỳ mục tiêu: tối đa CAGR=V2.3A; tối ưu rủi ro=V2.2-base.

**CAPIT per-event cap test ([REDACTED]12, harness audit, FULL/2022+/2025+)** — `pt_v23_audit_2014.py v23c [cap]`:
| bản | FULL CAGR/Sh/DD/Cal | 2022+ Cal | 2025+ CAGR/Cal |
|---|---|---|---|
| V2.2-base | 21.23/1.58/−18.5/**1.14** | **0.88** | 17.44/1.07 |
| cap15% | 21.51/1.56/−22.2/0.97 | 0.58 | 18.54/1.22 |
| cap20% | 21.31/1.54/−22.8/0.93 | 0.56 | 18.80/1.23 |
| uncapped | 21.38/1.52/−23.5/0.91 | 0.52 | **20.38/1.33** |

**KẾT LUẬN CUỐI về CAPIT = edge PHỤ THUỘC REGIME, KHÔNG phải vô giá trị** (sửa kết luận vội trước đó): (1) **2025+ CAPIT THẮNG base mọi trục** (uncapped 20.38/Cal1.33 vs base 17.44/1.07) — càng deploy NHIỀU càng tốt trong bull/neutral → trực giác user ĐÚNG, CAPIT là cơ hội mua thật. (2) **2022+ CAPIT HẠI** (mọi bản Cal 0.52-0.58 vs base 0.88) — cú knife 2022-04-19 đầu gấu-grinding. (3) **cap = núm tradeoff**: chặt hơn→tốt hơn ở gấu, tệ hơn ở bull; cap15 = compromise FULL Calmar tốt nhất của nhóm CAPIT (0.97) nhưng vẫn < base 1.14. (4) Cú 2022-04-19 = CRISIS dd52w mới −8% (đầu dốc, gia tốc) full-size; các cú tốt = correction trong uptrend xác nhận. → **Fix đúng KHÔNG phải cap mù mà là REGIME/TREND filter** (deploy to khi correction-trong-uptrend; nhỏ/bỏ khi leg đầu gấu-grinding); DT5G state + dd-trend đủ tách. cap15 chỉ giảm tail thô, đánh đổi upside bull. Files: data/v22base + v23c[_cap15/_cap20]_audit + capit_event_diagnostic.py.

**CAPIT MATURITY rule test ([REDACTED]12, user hypothesis: rũ ngay sau EX-BULL chưa điều chỉnh = mean-reversion risk cao)** — `pt_v23_audit_2014.py v23c none smooth|gate15`: scale CAPIT size TRONG CRISIS theo độ sâu dd52w (smooth=clip(|dd|/20,.25,1); gate15=full nếu dd≤−15% else ×0.30). NEUTRAL/BULL giữ nguyên.
| bản | FULL CAGR/Sh/DD/Cal | 2022+ Cal | 2025+ Cal |
|---|---|---|---|
| V2.2-base | 21.23/1.58/−18.5/**1.14** | **0.88** | 1.07 |
| uncapped | 21.38/1.52/−23.5/0.91 | 0.52 | 1.33 |
| cap15% | 21.51/1.56/−22.2/0.97 | 0.58 | 1.22 |
| mat-smooth | 21.66/1.55/−21.2/1.02 | 0.65 | 1.36 |
| **mat-gate15** | **21.86/1.57/−20.9/1.04** | **0.68** | **1.37** |

**KẾT LUẬN: giả thuyết user ĐÚNG, maturity-gate >> cap mù**: (1) gate15 = bản CAPIT tốt nhất mọi trục, CAGR 21.86% (cao nhất tất cả), Calmar 1.04 vs uncapped 0.91. (2) **DOMINATES cap**: cap đánh đổi 2025-upside để vá 2022 (cap15 2025+ Cal 1.22); maturity **vá 2022 (Cal 0.52→0.68) mà GIỮ NGUYÊN 2025-upside (1.37≈uncapped 1.33)** — vì chỉ chạm CRISIS, để yên pullback bull lành mạnh. Đây là bằng chứng cấu trúc nó bắt đúng cơ chế regime, không phải xóa 1 event may rủi. (3) NHƯNG kể cả bản tốt nhất, CAPIT vẫn **hơi thua V2.2-base full-period risk-adj** (Cal 1.04<1.14, DD −20.9<−18.5): CAPIT = bull/return-enhancer còn tốn chút DD ở gấu-grinding. 2025+ gate15 (1.37) >> base (1.07); 2022+ base (0.88) > gate15 (0.68). ⚠️**IN-SAMPLE**: ngưỡng −15%/scope-CRISIS rút từ chính 2 cú thua (gate15 còn co nhầm 2014-05 winner); n=2 loss → confirm-hypothesis, CHƯA walk-forward. Files data/v23c_…_matsmooth/_matgate15 + capit_regime_context.py. → Deploy: nếu tối đa return/bull-capture dùng CAPIT+maturity-gate; nếu tối ưu robust risk-adj giữ V2.2-base (0 param, bền nhất). Validate OOS trước khi tin gate15 live.

**EW-lens + gate 2-chiều ew2d ([REDACTED]12, user refinement)** — index cap-weighted bị megacap che (VIC-led 2025); thay bằng equal-weight. `capit_ew_maturity.py`: **corr(fwd60, index_dd52w)=−0.17 SAI DẤU; corr(EW_p25_dd)=+0.38; corr(EW_median_dd)=+0.32** → EW = lăng kính đúng, index gần như vô dụng (xác nhận user). NHƯNG ví dụ cụ thể user (2025-10 sâu hơn 2022-04) KHÔNG đúng trên EW-depth: 2022-04 EW_med −22.6% SÂU HƠN 2025-10 −17.8%. Cái tách đúng 2 cú = **breadth-below-MA200** (2022-04 chỉ 43% dưới MA200 = trend CHƯA gãy/còn treo trên mean = ý "MA200 vs đỉnh" của user; 2025-10 51% = đã gãy). Gate `ew2d` wired (all-state, full nếu EW_p25≤−20% AND breadth≥48% else ×0.30): fire đúng (2022-04/2014-05/2016-01 shrink, 2024-08/2025-10 keep).
| bản | FULL Cal | 2022+ Cal | 2025+ Cal |
|---|---|---|---|
| V2.2-base | **1.14** | **0.88** | 1.07 |
| gate15 (index-dd) | 1.04 | 0.68 | 1.37 |
| **ew2d (EW 2-D)** | 1.04 | 0.67 | 1.36 |

**META-FINDING quan trọng: ew2d ≈ gate15 KHỚP TỪNG WINDOW** (FULL Cal cả hai 1.04; 2022+ 0.67≈0.68; 2025+ 1.36≈1.37). Lăng kính EW tốt hơn ở TẦNG TÍN HIỆU (corr) NHƯNG KHÔNG cải thiện backtest, vì backtest CAPIT = **bài toán 1-sự-kiện (2022-04)** — cả gate thô (index-dd) lẫn gate tinh (EW 2-D) đều bắt được cú đó, phần còn lại là noise smallcap. Với chỉ 2 loss/18 (1 là COVID không bắt được), backtest KHÔNG phân biệt nổi gate tốt vs gate may. → **Deploy: nếu dùng CAPIT thì chọn ew2d (đo đúng hiện tượng kinh tế "thị trường rộng về mean", generalize tốt hơn cho cú knife TƯƠNG LAI ≠ 2022) dù in-sample hòa gate index**. Vẫn KHÔNG bản nào vượt V2.2-base full-period risk-adj (Cal 1.14); CAPIT-gated = cỗ máy bắt upside bull (2025+ Cal 1.36-1.37 >> base 1.07) đổi lấy chút DD full-period. Files data/v23c_…_matew2d + capit_ew_maturity.py.

**🎯 WALK-FORWARD ew2d (IS=2014-19 calibrate, OOS=2020+ test) — CAPSTONE [REDACTED]12**:
- IS có **6 events TẤT CẢ thắng** (xấu nhất +4.1%, 0 loser); mọi cú knife (COVID, 2022-04, 2022-09) ở OOS. Hai IS-event breadth-thấp (2014-05 @37%, 2016-01 @40%) đều THẮNG → breadth-below-MA200 **KHÔNG có sức phân biệt trong IS, thậm chí dạy NGƯỢC** ("breadth thấp vẫn an toàn"). → **không thể calibrate gate tail-risk trên giai đoạn lành**.
- Backtest window (Calmar): **IS** uncapped **1.87** > ew2d 1.84 > base 1.66 | **OOS** base **1.39** > ew2d 1.20 > uncapped **1.03**. **RANKING ĐẢO HOÀN TOÀN IS↔OOS**: thứ IS bảo tốt nhất (uncapped CAPIT) là thứ TỆ NHẤT OOS; thứ IS xếp bét (base no-CAPIT) THẮNG OOS. Gate ew2d mà IS-opt sẽ TỪ CHỐI (1.84<1.87) lại là thứ CỨU OOS (1.20>1.03).
- **KẾT LUẬN**: (1) sức hấp dẫn của CAPIT phần lớn là **artifact in-sample** — IS nó áp đảo, OOS nó tệ nhất. (2) ew2d (giả thuyết user) **KHÔNG learn được từ IS** nhưng như prior kinh tế áp OOS thì **gỡ ~½ thiệt hại** (Cal 1.03→1.20) — logic generalize, dù không calibrate được. (3) **Kể cả có gate, CAPIT vẫn KHÔNG vượt no-CAPIT OOS** (ew2d 1.20 < base 1.39). (4) Đây là minh chứng kinh điển vì sao audit này cần thiết: IS-ranking lừa, follow IS → chọn đúng thứ nổ OOS. → **Khuyến nghị: V2.2-base là lựa chọn OOS-robust nhất; nếu muốn upside-bull của CAPIT thì BẮT BUỘC kèm ew2d-gate, và hiểu nó là bull-enhancer regime-dependent KHÔNG phải all-weather.** Mọi số IS/OOS từ data/*_audit_2014_now*.csv (0-VND self-check).

**🏆 ew2d HARD-BLOCK (size 0, user [REDACTED]13: "nguy hiểm thì đừng mua") — BẢN CAPIT ĐẦU TIÊN THẮNG no-CAPIT MỌI TRỤC**: `pt_v23_audit_2014.py v23c none ew2d 0.0` (argv[4]=EW2D_SHRINK). Chặn HẲN washout trend-chưa-gãy (breadth<48%: 2014-05/2016-01/2022-04) thay vì ×0.30. KQ: **CAGR 22.16 / Sh 1.63 / DD −19.1 / Cal 1.16** — thắng base (21.23/1.58/−18.5/1.14) MỌI trục (CAGR +0.93pp, Calmar 1.16>1.14, DD ≈base). vs ew2d×0.30 (21.75/−21.0/1.04) và uncapped (21.38/−23.5/0.91). → ×0.30 để lại tiền trên bàn (30% residual vào 2022-04 vẫn lỗ thuần); **gate thấy nguy hiểm thì size=0 STRICTLY tốt hơn shrink**. ⚠️ vẫn IN-SAMPLE (chặn cả 2014-05/2016-01 winner nhỏ; ngưỡng 48% fit từ events; walk-forward không learn được từ IS lành) — sound nhưng cần OOS. File data/v23c_…_matew2d_shrink0.csv.

**🏆🏆 GATE POSTBULL (user thesis [REDACTED]13: "tránh CAPIT sau EX-BULL/bull kéo dài — điều chỉnh về mean còn sâu; càng lâu càng rủi ro; 2007/2017-18/2021-22") — KẾT QUẢ TỐT NHẤT TOÀN PHIÊN**: `pt_v23_audit_2014.py v23c none postbull 0.0`. Rule: CHẶN washout nếu (VNINDEX trailing-2yr return ≥60%) VÀ (dd-từ-đỉnh-1y > −15% = giảm còn NÔNG). Diagnostic (`data/capit_*` + VNINDEX.csv lịch sử dài): 2007-10 (ret2y+287%/ext500 1.64/dd−7%→fwd120 **−53%**), 2018-04 (+97%/1.43/−7%→−16%), 2022-04 (+83%/1.18/−8%→−26%) CÙNG chữ ký = bull-mạnh + treo-trên-mean + giảm-nông. Rule chặn ĐÚNG mỗi 2022-04 (NET, ngoài BEAR-guard 2022-09 sẵn có), GIỮ 2025-10 (ret2y+42%<60→thắng+16%) + 2018-05/07 (dd sâu −23/−25%, đã chiết khấu) + 2014-05/2016-01 (low ret2y, winner).
| bản | CAGR | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|
| V2.2-base (no CAPIT) | 21.23 | 1.58 | −18.5 | 1.14 |
| V2.3C uncapped | 21.38 | 1.52 | −23.5 | 0.91 |
| V2.3C ew2d hard-block | 22.16 | 1.63 | −19.1 | 1.16 |
| **V2.3C postbull hard-block** | **23.35** | **1.72** | **−19.0** | **1.23** |
Postbull THẮNG MỌI bản mọi trục (CAGR +2.12pp vs base!). > ew2d-hardblock vì ew2d chặn nhầm 2014-05(+13%)/2016-01(+8%) winner; postbull surgical chỉ chặn 2022-04. **Ưu thế robustness: (1) MỘT khái niệm kinh tế rõ; (2) GENERALIZE out-of-window tới 2007/2018 — KHÔNG nằm trong event set fit rule = OOS-validation thật; (3) margin rộng (52% giữ ↔ 83% chặn).** ⚠️ vẫn in-sample phần ngưỡng (1 loser 2022-04 để tune) nhưng 2007/2018 generalization là bằng chứng OOS mạnh nhất trong các gate. File data/v23c_…_matpostbull_shrink0.csv. **→ Nếu deploy CAPIT: dùng postbull-hard-block, không phải ew2d/cap.**

**CƠ CHẾ DD đính chính (user bắt lỗi [REDACTED]13)**: CAPIT giữ ĐÚNG 60 ngày (cohort 2022-04 vào 04-20 thoát 07-18; 0 vị thế CAPIT trong 2023). Drawdown đáy 2023-04 KHÔNG do giữ vị thế. Thật ra ratio V2.3C/base = **1.18 (đầu 2022 = CAPIT +18% lãi 8 năm) → 1.00 (07/2022, trả gần hết 1 cú)**: cú 2022-04 full-size ~245B≈cả sổ (sizing flaw CRISIS=max-free-cash) lỗ ~19% NAV = xóa 8 năm edge. MaxDD sâu vì CAPIT THỔI ĐỈNH đầu-2022 +18%, drawdown đo từ đỉnh đó; "kéo qua 2023"=phép-đo-từ-đỉnh-thổi-phồng KHÔNG phải vị thế (giải thích "giữ xuyên gấu" trước đó SAI).

**Note kỹ thuật**: (1) đã vá lỗ hổng pending partial-fill (1.59B BAL) bằng MTM phantom `MTM_PENDING_PARTIAL` per book → file tự khớp 100%. (2) MTM mark = last Close forward-[REDACTED] (ticker halt như PXI mark tại Close cũ). (3) engine `simulate_holistic_nav.py` KHÔNG sửa (prod dùng chung). Liên quan [[v4_faithful_reproduction_2026]], [[version_naming_v23_2026]].

## UPDATE [REDACTED]20 — audit PHẢI dùng custom30V selector (đừng default blend)
`pt_v23_audit_2014.py` parking default = ETF_LIQ `off`; và build_pit BASKET_SELECT default = `blend`. **Production = V2.3 + custom30V + gated-overflow** → phải set **`ETF_LIQ=custompitg BASKET_SELECT=yieldcombo`** (custom30V). Quên = chạy nhầm blend, THẤP hơn nhiều.
- **2018→nay @50B, V2.3A + custom30V (yieldcombo) + gated-overflow + LAG forensic gate ON:** CAGR **25.07%** / Sharpe **1.52** / MaxDD **−29.9%** / Calmar **0.84** / NAV 50B→331.7B. Self-check 0 VND (BAL+LAG cash-flow + final-NAV identity). vs VNINDEX 7.42%/0.46/−45.3.
- So sánh selector (cùng config, 2018→nay): parking-off 20.07% < blend 21.40% < **custom30V (yieldcombo) 25.07%** → selector rổ parking đáng +3.67pp (NEUTRAL chiếm đa số 2018→nay → parking active nhiều). Cảnh báo: ĐỪNG đoán "delta selector nhỏ" — ở basket-level nhỏ nhưng V2.3-level lớn do compound qua parked-fraction.
- custom30V go-live 30/06 (BASKET_SELECT yieldcombo khi END_DATE≥CUSTOM30V_GOLIVE); live <30/06 đang chạy blend = để ~3.67pp/năm trên bàn. Cân nhắc đẩy sớm. ⚠️ basket-table ablation (yieldcombo 36.48 < ps3 39.43 < v3comp 38.05) là BASKET-level; nhưng giữ yieldcombo=custom30V vì robust ([[custom30v_selector_keep_yieldcombo_2026]]).
