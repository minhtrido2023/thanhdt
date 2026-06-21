---
name: capacity-ceiling-custom-vn30-2026
description: Định lượng trần công suất deploy config theo NAV (~200B) + thiết kế rổ VN30 custom cho scale
metadata: 
  node_type: memory
  type: project
  originSessionId: 2ef717ab-5c78-4933-9acd-888a2ecf9450
---

User ([REDACTED]13): nhớ ngưỡng ~200B các strategy stock-picking đuối; trên đó cần dựng VN30 custom. ĐÃ định lượng (deploy config V2.3A+postbull+edge, strict ETF cap, full-history 2014-now, 4 mức NAV, BQ-auditable).

**BẢNG TRẦN CÔNG SUẤT** (`pt_v23_audit_2014.py` env NAV_TOTAL_B + ETF_LIQ=strict):
| NAV | CAGR | Sharpe | MaxDD | Calmar | stk% | cash% nhàn | etf% |
|---|---|---|---|---|---|---|---|
| 50B | 23.68 | 1.96 | −17.2 | 1.37 | 35 | 46 | 12 |
| 100B | 20.17 | 1.78 | −15.2 | 1.33 | 35 | 51 | 9 |
| **200B** | **17.86** | 1.69 | −14.4 | 1.24 | 34 | **58** | 6 |
| 500B | 13.11 | 1.35 | −15.7 | 0.83 | 35 | **65** | 3 |
(VNINDEX 10.72%/0.65/−45.3 cùng kỳ)

**CƠ CHẾ (quan trọng)**: stk% **đứng ~35% mọi mức NAV** → KHÔNG phải stock-picking là binding chính. Binding = **ETF parking strict-cap không hấp thụ nổi tiền nhàn ở NAV lớn** (etf% 12→3%), nên **cash nhàn earn-0 phình 46→65%** → CAGR sụp. Tức trần do **tiền nhàn không có chỗ deploy có-công-suất**, không phải do hết mã alpha. CAGR: 50B 23.68 → 200B 17.86 (−5.8pp) → 500B 13.11 (−10.6pp). **Ngưỡng ~200B xác nhận**: mất ~¼ alpha, vẫn > VNINDEX nhưng erode rõ; >200B buộc phải có vehicle beta công-suất-lớn.

**→ RỔ VN30 CUSTOM giải đúng cái này**: cho tiền-nhàn-phình một chỗ beta công suất (~2088B/day basket → **~418B/day parkable** = ~100x ETF thứ cấp). Vehicle = rổ ex-VIC cap-weight (30 mã thanh khoản nhất ticker_prune ex-VIC/ex-index: STB,HPG,SSI,VHM,DIG,NVL,VPB,VND,MWG,KBC,VNM,FPT,TCB,MSN,MBB,CTG...; loại VIC; chained cap-weight = adj Close × OShares).

## ★ BACKTEST XONG ([REDACTED]14, BQ-auditable, spot-check 0 VND mọi NAV)
Wire `ETF_LIQ=custom` vào `pt_v23_audit_2014.py` (vehicle = rổ thay E1VFVN30); builder `custom_basket.py` dùng chung sim + spotcheck → rổ tái dựng từ BQ thô **0 sai số/3243 phiên**. So 3 vehicle × 4 NAV (deploy config V2.3A+postbull+edge, full 2014→nay):

| NAV | strict(prod) | creation(VN30 thật) | custom(ex-VIC) | **cap(cr−st)** | **exVIC(cu−cr)** | **total(cu−st)** |
|---|---|---|---|---|---|---|
| 50B | 23.68 | 24.39 | 26.65 | +0.72 | +2.26 | +2.97 |
| 100B | 20.17 | 21.62 | 24.49 | +1.45 | +2.87 | +4.32 |
| 200B | 17.86 | 18.66 | 22.27 | +0.79 | +3.62 | +4.41 |
| 500B | 13.11 | 16.58 | **21.22** | **+3.47** | +4.64 | **+8.11** |
(Sharpe/DD/Calmar@500B: strict 1.35/−15.7/0.83 → creation 1.40/−18.2/0.91 → custom **1.49/−18.0/1.18**. VNINDEX 10.72/−45.3.)

**Cơ chế xác nhận** (cột composition): park% hấp thụ tiền nhàn → cash-nhàn KHÔNG phình. cash%: strict 49→**63** vs creation 40→45 vs custom 34→**38**. park%: strict 13→**3** vs custom 27→**32**. Tức custom@500 chỉ để 38% tiền nhàn earn-0 (strict 63%) → giữ CAGR 26.65→21.22 (chỉ −5.4pp) thay vì strict 23.68→13.11 (−10.6pp).

**Decompose THẬT THÀ (quan trọng):**
- **Công suất THUẦN = creation−strict = +0.7→+3.5pp** (tăng theo NAV, đỉnh ở 500B). Đây là số SẠCH, deployable-live: dùng E1VFVN30 beta VN30 THẬT (không hindsight), chỉ nới cap parking từ secondary→creation. = câu trả lời gốc §5.
- **exVIC vehicle = custom−creation = +2.3→+4.6pp** thêm NHƯNG ~một nửa là **beta/hindsight của rổ** (chọn 30 mã liquid 2020-2025 = lọc kẻ thắng sống sót; rổ CAGR ~19.9% >> VNINDEX 10.7%). Bằng chứng: custom@50 đã thắng strict@50 +3pp **khi capacity CHƯA nghẽn** → +3pp đó là vehicle-beta, không phải gỡ-capacity.
- **Đánh đổi rủi ro**: park tiền nhàn vào beta → MaxDD xấu nhẹ (strict −15/−17 → −18%) nhưng return-recovery áp đảo → Calmar@500B 0.83→1.18 vẫn TỐT HƠN. ex-VIC = beta CÓ KIỂM SOÁT (cố ý bắt ít sóng VIC-narrow 2025; đổi lấy rổ mình thật sự muốn nắm).

**VERDICT (bản hindsight)**: production rule §8.3 ">200B chuyển dần sang VN30 custom" = **VALIDATED**. NHƯNG số custom static = hindsight (membership cố định 2020-2025 = survivorship) → đo lại bằng PIT bên dưới.

## ★★ PIT DE-HINDSIGHT ([REDACTED]14) — bóc survivorship, đo biên THẬT
User: dựng membership **Point-In-Time theo quý** + **quality-tilt 8L**, đo lại bỏ hindsight. Làm: `custom_basket.build_pit()` — mỗi quý chọn lại top-30 ex-VIC bằng **thanh khoản quý TRƯỚC** (no look-ahead) + tilt cap-weight × QTILT[as-of `fa_ratings_8l.rating`] {1:1.5..5:0.4}. Wire `ETF_LIQ=custompit` (cap-wt) / `custompitq` (+quality). Spot-check PASS mọi NAV: **members_match=True** (membership/quý tái dựng từ BQ khớp), level rebuild **0.00 err/3109 phiên**, identity 0 VND. Rổ tự thân: hindsight 19.9% → **PIT 15.5%** (−4.4pp = survivorship).

**Bảng CAGR đầy đủ (5 vehicle × 4 NAV, BQ-auditable):**
| NAV | strict | creation | **custompit** | custompitq | custom(hindsight) |
|---|---|---|---|---|---|
| 50B | 23.68 | 24.39 | 24.12 | 24.19 | 26.65 |
| 100B | 20.17 | 21.62 | 22.93 | 23.06 | 24.49 |
| 200B | 17.86 | 18.66 | 20.16 | 20.82 | 22.27 |
| 500B | 13.11 | 16.58 | **18.92** | 18.27 | 21.22 |
(Calmar@500B: strict 0.83 / creation 0.91 / **custompit 1.09** / custom 1.18. DD custompit −17.4 ~ strict.)

**DECOMPOSITION TRUNG THỰC (pp vs strict, tại 500B):**
- **capacity thuần** (creation−strict) = **+3.47** (deployable, beta VN30 thật)
- **ex-VIC PIT vehicle** (custompit−creation) = **+2.34** (deployable THẬT, no hindsight: rổ ex-VIC liquid vẫn > VN30-ETF + tránh VIC)
- **hindsight đã BÓC** (custom−custompit) = **+2.30** ← survivorship của bản static, KHÔNG deployable
- **quality-tilt 8L** (custompitq−custompit) = marginal: +0.07/+0.13/+0.67 ở 50/100/200B nhưng **−0.65 @500B** (DD xấu hơn −17.4→−19.5); giúp DD ở mid-NAV nhưng NOISY ở 500B → **không phải add đáng tin, để OPTIONAL**.
- **HONEST total deployable** (custompit−strict) = **+5.81pp @500B** (vs hindsight +8.11) → ~2.3pp của con số cũ là ẢO.

**KẾT LUẬN deployable (sửa lại từ bản hindsight):**
1. **NAV lớn (200-500B)**: custompit gỡ **+3.0→+5.8pp** vs strict (Calmar 0.83→1.09 @500B), và **VẪN > creation +1.5/+2.3pp** → rổ ex-VIC PIT thật sự là vehicle parking TỐT HƠN VN30-ETF (không chỉ capacity, không hindsight). Đây là vehicle nên deploy ở scale.
2. **NAV nhỏ (50-100B)**: custompit ≈ creation ≈ strict về return, **kém Sharpe** (1.65 vs strict 1.96) → đừng nhồi parking-beta khi chưa cần; giá trị nằm ở SCALE.
3. **Quality-tilt 8L**: để optional (giảm DD nhẹ mid-NAV, không add return tin cậy).
4. **Production**: nếu chọn [REDACTED]-on vehicle → **custompit (PIT, no hindsight)** là số honest để công bố; custom static chỉ dùng tham khảo (thổi ~2.3pp).

## ★★★ GATE + TIMING ([REDACTED]14, user góp ý — quan trọng cho AN TOÀN VỐN)
User: (1) chốt rổ vào **05/02, 05/05, 05/08, 05/11** (đầu tháng 2 mỗi quý = sau khi BCTC quý vừa rồi công bố → fundamentals/gate tươi, không stale); (2) lịch sử VN30 từng dính mã thanh khoản-ảo chất lượng kém (ROS/FLC → sau bị cấm GD); pure-liquidity rất rủi ro → cần **gate chất lượng**. Wire vào `build_pit(rebal='q2m5', gate_rating=3)`:
- **HARD GATE rating 8L ≤3** (investment-grade floor): chỉ mã as-of `fa_ratings_8l.rating≤3` được vào rổ → **junk-slots 95→17-19 (giảm ~80%)**; rổ 2015 hết PVX(r4)/OGC(r4)/SCR(r4) (chỉ còn FIT khi tạm r3). Capacity & 30-slot không đổi. (ROS/FLC vốn đã ngoài ticker_prune.)
- ETF_LIQ=**custompitg** (gate+timing, cap-wt) / **custompitgq** (+tilt). Spot-check PASS mọi NAV (members_match=True qua build_pit rebal+gate, rebuild 0.00 err, identity 0 VND).

**Gate+timing CẢI THIỆN cả return LẪN rủi ro vs ungated** (custompitg vs custompit):
| NAV | custompit (no gate) | **custompitg (GATE+timing)** | Δ |
|---|---|---|---|
| 50B | 24.12/Sh1.65/DD−18.1/Cal1.33 | **25.36/1.76/−17.8/1.42** | +1.24pp, DD↑, Cal↑ |
| 100B | 22.93/1.61/−17.7/1.29 | **23.45/1.68/−17.2/1.36** | +0.52pp |
| 200B | 20.16/1.47/−17.2/1.17 | **21.32/1.57/−15.8/1.35** | +1.16pp, **DD−15.8 (tốt nhất nhóm honest)** |
| 500B | 18.92/1.43/−17.4/1.09 | 18.88/1.45/−19.1/0.99 | ~flat (500B noisy) |
→ Gate loại junk vừa bớt drag return vừa giảm DD ở 50-200B; @500B return-neutral nhưng **giá trị chính = AN TOÀN VỐN** (tránh case ROS/FLC). custompitgq (+8L tilt) ≈ custompitg (tilt vẫn marginal; 200B DD−15.5/Cal1.37 nhỉnh tí).

**CHỐT vehicle production = `custompitg`** (PIT + timing 05/m2 + gate≤3): honest (no hindsight) + AN TOÀN (gate) + risk-adj tốt nhất nhóm honest ở mid-NAV. Quality-tilt 8L = optional (marginal). Số honest công bố @200B: **21.3%/Sh1.57/DD−15.8/Cal1.35** (vs strict 17.9/1.69/−14.4/1.24; vs hindsight-custom 22.3 thổi phồng).

## ★★★★ DEPLOYED vào PRODUCTION ([REDACTED]14) — luật thuần, không ngoại lệ
User ([REDACTED]14): áp dụng custompitg vào production thay block E1VFVN30; **bỏ hardcode ex-VIC** — "VIC đạt chuẩn 8L thì vào như mọi mã; hệ thống vận hành từ LUẬT bài bản không từ NGOẠI LỆ".
1. **Refactor luật thuần** (`custom_basket.py`): XÓA hết hardcode (gồm VIC + index list). Universe = `ticker_prune ∩ ICB_Code IS NOT NULL` (1 luật: công ty niêm yết thật; index VN30/VNINDEX + ETF E1VFVN30 đều có ICB **NULL** → tự loại — verified). VIC cạnh tranh bình thường, gate 8L≤3 quyết định. **Kết quả ĐÚNG kinh tế từ luật**: VIC được nhận 11 quý **2014-2018 khi rating=3** (Vingroup blue-chip giai đoạn đó), **bị loại từ 2020+ khi rating tụt 4-5** (gồm sóng VIC-led 2025). "Ex-VIC" = HỆ QUẢ của gate, không phải carve-out.
2. **Số rule-based custompitg** (audit BQ-verifiable, spot-check 0 VND + members_match=True mọi NAV; ≈ bản ex-VIC-hardcode, chênh <0.4pp): **50B 25.66/Sh1.79/DD−17.8/Cal1.44 · 100B 23.07/1.66/−17.3/1.33 · 200B 21.02/1.56/−15.8/1.33 · 500B 18.93/1.47/−17.9/1.06**.
3. **WIRED LIVE** trong `pt_v22_dt5g.py`: block E1VFVN30 → `cb.build_pit(rebal='q2m5', gate_rating=3)`. Toggle `PARK_VEHICLE=etf` để rollback. **Không phí quản lý quỹ** (nắm cổ phiếu trực tiếp, chỉ rebalance friction). Script in 30 mã parking quý hiện tại. Run prod xác nhận: ~2459B/day parkable; VHM/VRE vào, **VIC bị gate loại** — đúng luật. ⚠️ **UPDATE [REDACTED]14: HAG đã bị loại khỏi rổ** sau khi sửa earnings-quality gate trong 8L rating (HAG rating 2→5 vì NP≈GP+levered+CFO5Y≤0 = lãi-phi-lõi; xem [[rating_8l_credit_scale_2026]] §EQ-gate + [[hag_earnings_forensic_2026]]); slot 30 giờ là TPB. Đây là minh chứng cơ chế "luật tận gốc": sửa rating 8L → parking gate tự loại HAG, không patch riêng.
4. **BUG live-mode đã fix**: `pt_v22_dt5g.py` chạy cửa sổ ngắn (2 ngày) → build_pit cũ chỉ lấy ~10 ngày lịch sử → ADV-60d ≈0 → parking tê liệt. Sửa: build_pit tự lùi `eff_start = min(start, end−600d)` → luôn đủ ≥1.5y lịch sử cho ADV + rebal gần nhất, BẤT KỂ cửa sổ ngắn. Audit (start=2014) eff_start=2014 → KHÔNG đổi (số cũ giữ nguyên).
**Mô hình [REDACTED]-on**: MỘT vehicle custompitg cho MỌI NAV, cap=20%×ADV tự co giãn theo thanh khoản (không gate theo NAV) → đơn giản, portfolio lớn lên không cần đổi gì. NAV nhỏ kém Sharpe strict tí (nhiều beta hơn) nhưng Calmar/CAGR hơn; giá trị chính ở SCALE + AN TOÀN.

Files: `custom_basket.py` (build + build_pit có rebal/gate_rating), `pt_v23_audit_2014.py` (ETF_LIQ=custom|custompit|custompitq|**custompitg|custompitgq**), `data/basket_final_table.py` (bảng 7-vehicle×4-NAV×5-metric), `data/v23_..._etfliq{...}_nav{100,200,500}B.csv` (+50B no-tag). spotcheck `data/v23_audit_spotcheck.py` (scale-aware + PIT-aware đọc custom_basket_pit_params, rebuild qua build_pit khớp rebal+gate). Liên quan [[audited_versions_tally_2026]], [[simulation_[REDACTED]_audit_default]], [[v23_audit_2014_now_deliverable]], [[rating_8l_credit_scale_2026]].

## ★★★★★ DE-CONCENTRATION REVIEW + PUBLISHED TABLE `custom30_8l` ([REDACTED]15)
User: review cách dựng rổ trước khi publish + có nên tránh tập trung 1 nhóm? Đo concentration rổ hiện hành (cap-weight): **NH 51.5%, tài chính+BĐS ICB-8 72.9%, VHM 13.9%+VCB 12.8% (top-2 26.7%), HHI 666, số mã hiệu dụng ~15/30** = tập trung CAO hơn cả VN30 (rổ KHÔNG phải equal-weight — là cap-weight `mcap=Close×OShares`).

**Backtest 4 sơ đồ trọng số (V0 policy {3:0.7}, custompitg, BQ-audited self-check 0):** capwt(legacy) TỆ NHẤT ở scale. **@500B**: capwt 18.83/Cal1.05/DD−17.9 → **namecap10 20.09/1.32/−15.2 (+1.27pp)** > sectorcap50 19.51/1.29 (+0.68) > ew 19.24/−14.9/1.29 (+0.41). **@200B** nhỏ hơn (namecap +0.12, ew −0.06, sectorcap −0.34). **Lợi ích giảm-tập-trung TĂNG theo NAV** (rõ ≥300-500 tỷ; mờ ở 200B). De-concentration efficacy (`basket_scheme_concentration.py`): namecap→NH 52%/top1 10% (chỉ chặn đơn-mã), sectorcap→NH 35%/ICB-8 50%, ew→NH 33%/ICB-8 67%.

**CHỐT = namecap (cap mỗi mã ≤10%)** — user data-driven: tập trung NGÀNH = rủi ro HỆ THỐNG/cấu trúc nền KT (VN30 cũng ~tài chính-heavy) → giữ để follow beta; chỉ chặn rủi ro ĐƠN-MÃ (idiosyncratic VHM/VCB) = cap 10%. namecap = return cao nhất + DD tốt hơn capwt → **nâng cấp THUẦN, không đánh đổi**. sectorcap (hạ NH→35%) **REJECTED**: cùng ý nhưng mất ~0.5pp return, user coi concentration-ngành là systematic không cần cắt.

**WIRED LIVE [REDACTED]15:** `pt_v22_dt5g.py` build_pit `weight_scheme="namecap"`; `custom_basket.build_pit` thêm `weight_scheme` (capwt default = byte-identical legacy) + helpers `_cap_names`/`_cap_sector`; `pt_v23_audit_2014.py` env `BASKET_WT`; `v23_audit_spotcheck.py` đọc weight_scheme từ META (audit vẫn reconcile).

## ★★★★★★ C+D SWEEP: size (top_n) × single-name cap ([REDACTED], BQ-audited)
User: sweep số mã × cap level. Wired env `BASKET_TOPN`/`BASKET_NAMECAP` vào `pt_v23_audit_2014.py`→`build_pit` (+META log + `_sz_tag` filename); spotcheck đọc `top_n=`/`name_cap=` từ META, rebuild khớp. Driver `sweep_basket_size_cap.py` (ThreadPool 6, parse CAGR/Sh/DD/Cal). ⚠️ FIX môi trường Linux: `earnings_surprise_data.pkl` cũ pickled bằng pandas StringDtype → pandas 2.3.3 KHÔNG load được; re-pull từ BQ object-dtype (backup `.bak_strdtype`). Mỗi cell full backtest ~500s.

**Grid 500B (5 top_n × 4 cap) + confirm 200B (3×3), config `v23a none postbull 0.0 edge`, custompitg, namecap, V0 {3:0.7}.** Cấu trúc biên (đọc theo MARGINAL, cell-noise ~0.5pp):
- **top_n: NHIỀU HƠN TỐT HƠN, plateau 30-40** (40≈30 > 25≈20 > 15). 15 mã LUÔN tệ nhất. → bác bỏ giả thuyết "đuôi rank 20-30 vô nghĩa": 10 mã thêm mang ~6-10% weight + capacity + diversification thật (effN 17.6→19.3), Sharpe tăng rõ. CƠ CHẾ: ở NAV lớn parking-capacity = Σ ADV member; thêm mã liquid (qua gate 8L≤3) = thêm tiền-nhàn deploy được + breadth.
- **cap: 0.12-0.15 ≈ nhau > 0.10 > 0.08; cap=0.08 TỆ RÕ** (ép weight xuống đuôi kém-liquid + rời mega-cap → GIẢM capacity, không bõ chống idiosyncratic). 0.10 round-choice ổn nhưng hơi chặt.
- **Robust 2 NAV**: ranking GIỐNG HỆT ở 200B & 500B (không phải artifact 1 cửa sổ).

**Winner = (top_n=40, cap=0.12)**: @500B 20.48%/Sh1.62/DD−15.5/Cal1.32; @200B 21.93%/Sh1.65/DD−15.8/Cal1.39. **Δ vs prod (30,0.10): +0.46pp/+0.06Sh @500B, +0.56pp/+0.06Sh @200B** (Calmar ~flat/nhỉnh). (40,0.15) ≈ ngang (200B nhỉnh tí 21.96/Cal1.40); (30,0.15) = +0.24/+0.45pp (DD tốt nhất −15.0 @500B). Spotcheck (40,0.12)@500B PASS toàn bộ: identity 5e-16, 0 price-mismatch, members_match=True, level rebuild 0.00 err/3110d, cashflow 0 VND, allocator replay 0 VND.

**WALK-FORWARD ([REDACTED], `wf_basket_size_cap.py` đọc DAILY combined_nav, KHÔNG chạy lại) = GIẾT cả 2 ứng viên.** IS 2014-19 / OOS 2020-now + per-year + OOS-ex-2025:
- **(30,0.15) FAIL**: full-edge +0.24/+0.45pp toàn từ IS (2015 +5pp, 2016 +2pp = năm SỚM/mỏng); **OOS 2020-now ≈ FLAT** (−0.27pp@500B, +0.07pp@200B). Nới cap 0.10→0.15 giữ N=30 = IS-fit thuần.
- **(40,0.12) "qua" OOS biểu kiến (+0.42/+0.54pp, +0.05 Sharpe) NHƯNG edge ≈ TOÀN BỘ 2025** (VIC-led narrow bull, Δ +3.9/+3.5pp riêng năm đó). **OOS-EX-2025: edge BỐC HƠI** — @500B prod 20.64% vs (40,0.12) 20.50% (−0.14pp); @200B 21.42 vs 21.44 (+0.02pp). Cả 3 config GIỐNG NHAU trong ±0.3pp/±0.02 Sharpe khi bỏ 2025.
- **VERDICT CHỐT: KHÔNG wire đổi (top_n,cap).** Khác biệt full-window = noise in-sample/2025-driven trên plateau phẳng. Giống bài học DT5G ("toàn bộ edge = 1 năm 2023"). User pre-commit "wire (30,0.15) nếu walk-forward qua" → KHÔNG qua → giữ nguyên.
- **2 điều ROBUST (generalize IS+OOS+2 NAV) — actionable:** (1) **cap ≤ 0.08 = loser nhất quán, KHÔNG bao giờ siết dưới ~0.10**; (2) **N≥30 đúng cấu trúc** (capacity/breadth; N=15-20 yếu hơn IS rõ + cơ chế đúng), 30 vs 40 không phân biệt được OOS-ex-2025 → **giữ prod (30, 0.10)**, nó nằm đúng efficient plateau. Files: `sweep_basket_size_cap.py`, `wf_basket_size_cap.py`, `data/basket_size_cap_sweep_nav{200,500}B.csv`.

## ★★★★★★★ DIR B: quality-TILT strength sweep ([REDACTED]) — DEAD END, hiểu được VÌ SAO
User: khai thác hết quality-tilt 8L (đang OPTIONAL). Parametrize `qtilt` (env `BASKET_QTILT`: off/gentle/default/strong/custom) vào `build_pit`+audit+spotcheck (META `qtilt=k:v;...`, additive). Sweep dưới WEIGHT production (custompitgq + namecap, 30, 0.10) ở 200B+500B. `sweep_tilt.py` → `data/basket_tilt_sweep_nav{200,500}B.csv`.
- **Sanity PASS**: tilt=off (multiplier all 1.0) ≡ custompitg baseline CHÍNH XÁC (500B 20.02/1.56/−15.2/1.32; 200B 21.37/1.59/−15.6/1.37) → plumbing đúng.
- **Kết quả: tilt KHÔNG thêm return, LÀM XẤU DD/Calmar.** @500B Calmar: off **1.32** > gentle 1.29 > default/strong 1.26; DD off −15.2 vs tilts −15.6..−15.8; CAGR ~phẳng (19.81-20.05). @200B tilt thêm CAGR tí hon (+0.05..+0.15pp) NHƯNG DD xấu (−15.6→−16.0/−16.1), Calmar 1.37→1.34-1.36. Mạnh hơn KHÔNG tốt hơn (gentle≈off, default/strong tệ hơn).
- **CƠ CHẾ (quan trọng): rating-1 trong rổ ≈ TOÀN NGÂN HÀNG** (BID/CTG/MBB/HDB/SHB + VNM = 5/6 bank). Quality-tilt nâng rating-1 = **RE-CONCENTRATE vào ngành NH** — đúng cái namecap vừa thiết kế để KHÔNG tập trung. → tilt hoàn tác diversification, tăng DD. Không phải "chưa khai thác hết" mà là **tilt-chất-lượng = đặt cược ngành trá hình** trong rổ này.
- **VERDICT: KHÔNG tilt (giữ quality='none' = custompitg).** Không cần walk-forward (off đã DOMINATE in-sample Calmar/Sharpe; walk-forward chỉ để xác nhận winner, ở đây không có winner). Khớp đánh giá cũ (tilt "marginal/optional/noisy" dưới capwt) — dưới namecap còn rõ hơn là net-negative. custompitgq nên BỎ khỏi danh mục ứng viên deploy.

## 8L v2 ([REDACTED]) — KHÔNG ảnh hưởng backtest BAL / custom30 (verified 4 lớp)
User hỏi 8L v2 có ảnh hưởng tương thích backtest BAL/custom30 không. 8L v2 (`rating_8l.py`, sửa hôm nay) = **nâng cấp AXIS-2 (valuation/screener) THÔI**: composite value_score = 0.35·pb_z + 0.65·(1/PE sector-neutral) + CFO-3Y + track-record; percentile zones; ROE_Min3Y<0 trap. **Axis-1 rating 1-5 KHÔNG đổi.** Verified:
1. **Source diff** v1(`8l_package/rating_8l.py` Jun15) vs v2(root): rating scorecard (dòng ~92-400) BYTE-IDENTICAL; chỉ +2 cột SQL (PCF, CF_OA_3Y) + toàn bộ value axis (dòng 400+). value_score ghi ra `rating_8l_buynow/screener.csv`, KHÔNG feed lại cột `rating`.
2. **Live-run** v1 vs v2 trên CÙNG data: 809 ticker, **0 khác biệt rating**; gate rating≤3 = 434=434 y hệt.
3. **Data source**: bảng backtest `tav2_bq.fa_ratings_8l` schema = [ticker,time,route,rating,tier] — KHÔNG có value axis (backtest không thấy được axis-2).
4. **Publisher** `rating_8l_history.py`/`build_rating_8l_history.py` (build bảng backtest) KHÔNG bị sửa (Jun15), 0 dòng code v2.
**Dependency**: custom30 gate = `fa_ratings_8l.rating≤3`; BAL core signal = `fa_ratings.tier` (BẢNG KHÁC, 8L không đụng); BAL regime_size = `fa_ratings_8l.rating≥4`. Tất cả key trên RATING (đổi=0) → **backtest BAL & custom30 IDENTICAL, không cần chạy lại.** custom30 hôm nay (30 mã) dưới v1 vs v2: 0 rating-diff, 0 gate-flip → **danh sách Y HỆT**.
**v2 thực sự đổi cái gì = SCREENER buy-list** (axis-2): 58/113 mã đổi zone vs v1 (pb_z-only), 18 mã mới vào BUY-NOW (SHB/TPB/NAB/VND/DRI/DDV... rẻ theo earnings-yield dù pb_z "rich"); demote hợp lý (CTF/DGW/CTR rẻ-theo-book nhưng PE đắt → kéo lại; HVN→TRAP qua gate ROE_Min3Y<0). Đây là decision-support, KHÔNG đụng backtest/custom30.

## Bank-rating 2 pipeline (làm rõ [REDACTED]) — KHÔNG phải bug/stale
Bank trong bảng `fa_ratings_8l` (publisher `rating_8l_history.py` line 281 `CREATE OR REPLACE`) = `rate_bank_proxy` **ROE-only** (ROE≥.18→1, ≥.14→2, ≥.12→3, <.08→5; KHÔNG NPL/coverage vì không có lịch sử AQ → no look-ahead, CỐ Ý cho backtest). Live `rating_8l.py` = `rate_bank` đọc `data/bank_lens_v3.csv` (NPL/coverage hiện hành) → BID/SHB/HDB/LPB/VPB tụt xuống 3 (coverage<0.9 hoặc NPL cao), VCB/CTG=1, MBB/TCB/ACB=2. → bảng vs live **lệch theo THIẾT KẾ** (proxy vs AQ-thật), KHÔNG phải table cũ: bảng CURRENT (BANK tới 2026-05-04 = quý 2026Q1 vừa ra; history CSV rebuild [REDACTED]14) → re-run = no-op. Lệch này **KHÔNG ảnh hưởng custom30/BAL** (bank đều ≤3; biên ≥4 = ROE<8% giống nhau 2 pipeline). Chỉ ảnh hưởng GRADE bank mà live consumer hiển thị (custom30_8l.rating_8l show BID=1 trong khi live=3).
**FIX ĐÃ DEPLOY ([REDACTED], user chọn "override snapshot hiện tại"):** thêm `override_current_bank_aq(out)` vào `rating_8l_history.py` (gọi trước khi ghi CSV) — ghi đè rating của HÀNG MỚI NHẤT mỗi bank bằng giá trị AQ-thật từ `data/rating_8l.csv` (rate_bank live, đọc bank_lens_v3); **mọi hàng lịch sử giữ proxy → KHÔNG look-ahead**. Fail-safe: thiếu rating_8l.csv → giữ proxy. Đã republish (cần `source wc_env.sh`, creds dtienthanh — default SA read-only, write FAIL SILENT vì refresh_bq_table không check returncode): `tav2_bq.fa_ratings_8l` latest bank giờ BID/SHB/HDB/TPB/VPB=3, CTG/VCB=1, ACB/MBB=2, EIB/STB=5 (khớp live); verified history BID/SHB các quý trước NGUYÊN proxy, chỉ latest đổi. Re-run `custom30_history.py` → `custom30_8l.rating_8l` hiển thị đúng; **membership 30 mã + weights IDENTICAL (diff rỗng)** → custom30 & BAL backtest KHÔNG đổi (bank vẫn ≤3, không cross biên ≥4). rating_8l_history.py chạy THỦ CÔNG (không trong batch nào) → override áp mỗi lần publish. ⚠️ bank_lens_v3.csv là file TĨNH (2026-05-31, nhập tay) → "live AQ" chỉ tươi bằng file này. Liên quan [[rating_8l_credit_scale_2026]].

## DIR E + ADV-vs-profit study ([REDACTED])
**(1) ADV → forward profit (illiquidity premium VN, ticker_prune 2015-24, decile cross-sectional, profit_1M đơn vị %):** ret/risk (mean/std winsor ±50%) GIẢM ĐƠN ĐIỆU theo thanh khoản: decile1 (~0.5B/d) wmean 2.09%/Sh0.174 → decile10 (~102B/d) 0.45%/Sh0.037. XÁC NHẬN trực giác user (ADV cao = định giá hiệu quả = return thấp). NHƯNG: (a) premium tập trung ở decile-1 vi-mô (<~1B/d), decile 2-8 plateau ~1%/Sh0.07-0.12; (b) RỦI RO thật ở đuôi — winsor-std decile1 thấp nhất (12.0) là ARTIFACT của clipping (raw std 1342%); decile1 = return cao + đuôi cực béo (lottery), winsor che rủi ro. → ADV cao = return thấp + đuôi mỏng (đúng tài-sản parking muốn); illiquidity premium chỉ ở vi-mô + đi kèm tail-risk uninvestable.
**(2) DIR E — capacity stack hôm nay (Σ 20%×ADV, ADV=Vol_3M_P50×Close):** custom30 = **~1880 B/day parkable**; mã đuôi rank 21-30 vẫn liquid (DGC 99/VSC 82/GVR 110/TPB 124 B/d → parkable 16-25B/d mỗi mã), KHÔNG dead-weight. Need/day = NAV×idle(~0.4)×park(0.7)/3-ramp ≈ 0.093×NAV → capacity 1880B/d đỡ tới **NAV ~20 NGHÌN TỶ** trước khi bind (xa ngoài tầm 200-500B). **→ KHÔNG có ADV bottleneck; ADV-floor chỉ CẮT capacity vô ích; mã đuôi liquid + additive (khớp C+D: nhiều mã hơn tốt hơn).** custom30 ở đỉnh ladder (return thấp/đuôi mỏng) = ĐÚNG cho parking; không có lý do capacity để với xuống mã illiquid. VERDICT E: no-action (vehicle đã thừa capacity). Files: query inline (chưa lưu script).

**SERVICE published:** `custom30_history.py` → **BQ table `tav2_bq.custom30_8l`** (1440 dòng, 48 rebal 2014→nay; cột rebal_date/effective_from/to/ticker/liq_rank/rating_8l/weight/quarter; weight=namecap ref, VHM/VCB capped 10%). Lookup rổ hôm nay: `SELECT t.ticker,t.weight FROM tav2_bq.custom30_8l t WHERE t.rebal_date=(SELECT MAX(s.rebal_date) FROM tav2_bq.custom30_8l s WHERE s.rebal_date<=CURRENT_DATE())`. Consumers đọc bảng này thay vì chạy lại build_pit runtime (1 nguồn, nhanh, hết drift). **ĐÃ WIRE FULL ([REDACTED]15):** (a) **auto-refresh** — `custom30_history.py` cắm `papertrade_daily.bat` **[0e]** (chạy 15:30/ngày sau publish-state); (b) **service helper `custom30.py`** — `from custom30 import current; current(bq[, asof])` (CLI `python custom30.py [date]`) = 1-lời-gọi đọc table; (c) **consumer repoint** — `golive_recommend_v23.py` (báo cáo 18:00) đọc custom30 thay E1VFVN30-cũ (SỬA LỖI: report trước bảo mua ETF cũ trong khi prod park custom30). dna_report/screener KHÔNG hiển thị rổ parking → không cần repoint; bot V4 telegram giữ E1VFVN30 (V4=benchmark, ngoài phạm vi). Verified: live pt_v22_dt5g in `[PARK custompitg/namecap10]` + báo cáo [REDACTED]15 hiện custom30. Viewer cũ (đọc audit CSV): `show_custom30.py`.
