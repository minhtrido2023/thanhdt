# SESSION HANDOFF — V2.3 BQ-audit, gates, capacity & scale strategy (2026-06-13)

> Đọc file này + các memory file liệt kê ở §7 là có đủ context để tiếp tục. Mọi kết quả đều
> BQ-auditable (T+1 Open, dữ liệu `tav2_bq.*`, self-check 0 VND). Quy ước: **chạy simulation =
> mặc định kèm audit**; **DT5G là state mặc định** mọi chiến lược.

---

## 1. TL;DR — đang ở đâu
- Đã re-audit toàn bộ family V2.3 + V11 + V12.1 từ 2014→nay trên harness BQ-thuần (T+1 Open, KHÔNG intraday, KHÔNG panel curated). Phơi bày: số công bố cũ (26.3%) lạc quan; auditable thật ~21-22%.
- Qua nhiều vòng (driven bởi user), chốt **bản deploy = V2.3A + postbull-gate + edge-conditional-allocator + strict-ETF-cap**, đã WIRE vào production `pt_v22_dt5g.py`.
- Định lượng **trần công suất ~200B** (alpha erode vì tiền nhàn không deploy được, KHÔNG phải hết mã).
- **TASK ĐANG DỞ (user vừa duyệt, bị interrupt trước khi chạy):** backtest **rổ VN30-custom-ex-VIC** thay E1VFVN30 trong parking (creation-capacity) ở NAV 200B/500B — xem gỡ được bao nhiêu alpha-mất. Xem §5.

## 2. Bản deploy (đã wire vào production pt_v22_dt5g.py)
3 thành phần thêm lượt này (changelog ở docstring pt_v22_dt5g.py):
1. **postbull gate** (`postbull_block`): hard-block CAPIT washout nếu (VNINDEX trailing-2yr ret ≥60%) AND (dd-từ-đỉnh-1y > −15%). = "đừng bắt dao hậu-bull-mạnh chưa điều chỉnh". Generalize 2007/2018/2022.
2. **edge-conditional allocator** (`w_lag_target`): tilt LAG→0.65 ở NEUTRAL/BULL/EXBULL CHỈ khi LAG edge-health `mean12` (data/lag_edge_health.csv, trailing-12M LAG post-ret) ≥ 4%; else 0.50. BEAR=0/CRISIS=0.50.
3. **strict ETF cap** (`ETF_LIQ_KW`): E1VFVN30 parking cap 20% × ADV-thứ-cấp-60d/ngày, fill nhiều ngày.

**Số bản deploy (FULL 2014→now, BQ-auditable):**
| config | CAGR | Sharpe | MaxDD | Calmar | file data/ |
|---|---|---|---|---|---|
| V2.3A+postbull+edge (creation/uncapped ETF) | 24.64 | 1.82 | −20.3 | 1.22 | v23_golive_audit_2014_now_matpostbull_shrink0_edge[_etfliqcreation].csv |
| **V2.3A+postbull+edge+STRICT ETF (PRODUCTION)** | **23.68** | **1.96** | **−17.2** | **1.37** | v23_..._edge_etfliqstrict.csv |
| V2.3C+postbull (no allocator, min-DD alt) | 23.35 | 1.72 | −19.0 | 1.23 | v23c_..._matpostbull_shrink0.csv |
| V2.2-base (no CAPIT, robust floor) | 21.23 | 1.58 | −18.5 | 1.14 | v22base_audit_2014_now.csv |
VNINDEX B&H 10.7%/0.65/−45.3. Bracket số thật theo ETF-liquidity: **strict 23.68 ↔ creation 24.64** (creation = dùng primary-creation, khả thi quy mô tổ chức).

**Window thực tế 2025-06-09→nay (strict):** +10.68% vs VNINDEX +36.4% — TỤT vì sóng VIC-led narrow (điểm yếu cấu hữu, không phải bug). File `..._edge_etfliqstrict_from20250609.csv`.

## 3. Audit infrastructure — chạy & verify
**Engine**: `simulate_holistic_nav.py` (KHÔNG sửa logic core; chỉ THÊM param tùy chọn `etf_adv_lookup`/`etf_liquidity_pct` default off; cột carry cho lãi-vay-cash-âm).
**Harness chính**: `pt_v23_audit_2014.py` — args + env:
```
python pt_v23_audit_2014.py <MODE> <cap> <maturity> <ew2d_shrink> <edge>
  MODE: v23a (allocator+CAPIT) | v23c (static 50/50+CAPIT) | v22base (no CAPIT)
  cap: none | 0.15 ...  (per-event CAPIT cap)
  maturity: off | smooth | gate15 | ew2d | postbull
  ew2d_shrink (argv4): 0.0 = hard-block; default 0.30
  edge (argv5): "edge" = edge-conditional allocator
  ENV: AUDIT_START=YYYY-MM-DD (windowed) | NAV_TOTAL_B=200 (capacity) | ETF_LIQ=off|strict|creation
DEPLOY run: python pt_v23_audit_2014.py v23a none postbull 0.0 edge   (+ ETF_LIQ=strict)
```
**Verifier (đóng vai bot ngoài)**: `data/v23_audit_spotcheck.py N <file>` (allocator files) hoặc `data/audit_spotcheck_generic.py N <file>` (V11/V12.1, đọc nhãn sổ từ META). Kiểm: giá vs BQ 0 mismatch, cash-flow identity 0 VND, allocator-replay (qua cột w_lag_tgt) 0 VND, metric dựng-lại khớp.
**Emitter dùng chung**: `audit_lib.py` (N-sổ; combined_override cho ensemble; cột cash_carry).
**Scripts khác**: `pt_v11_audit_2014.py`, `pt_v121_audit_2014.py`, `pt_lagvn30_audit_2014.py` (argv full/vn30).
**Output 1-file**: record_type META(quy trình verify)/TX/DAILY/METRIC/EVENT_CAPIT/REBAL/ANNUAL.

## 4. Tally tất cả bản đã audit (FULL 2014→now, BQ-thuần T+1 Open) — xem [[audited_versions_tally_2026]]
V2.3 family 21-24% > V11 (momentum-only) 19.80 > V12.1 (ensemble switch) 16.85. One-wallet LAGGED+VN30/full-BAL (17-18%) THUA two-book silo (silo = feature). CAPIT-gate journey: uncapped risk-neg → ew2d → postbull-hardblock thắng base mọi trục.

## 5. ✅ DONE + DEPLOYED (2026-06-14) — rổ custom parking, PIT + gate, LIVE trong pt_v22_dt5g.py
> **DEPLOYED**: parking E1VFVN30 → rổ **custompitg** (LUẬT THUẦN, không hardcode VIC): universe=ticker_prune∩ICB-not-null,
> rebal 05/Feb-May-Aug-Nov (post-earnings), top-30 PIT prior-quarter liq, **gate 8L≤3** (an toàn vốn, tránh ROS/FLC).
> VIC vào BY RULE 2014-18 (rating3), gate loại 2020+ (rating4-5, gồm sóng 2025). Wired `pt_v22_dt5g.py` (toggle
> PARK_VEHICLE=etf rollback); không phí quản lý quỹ. Honest @500B 18.93%/Cal1.06, @200B 21.0%/DD−15.8 (BQ-audit,
> spotcheck 0 VND + members rebuild khớp). Fix live ADV lookback (eff_start floor). custom_basket.build_pit.
> Chi tiết [[capacity-ceiling-custom-vn30-2026]].

### (lịch sử) đề bài gốc — backtest rổ VN30-custom-ex-VIC parking ở NAV lớn
> **KẾT QUẢ** (BQ-auditable, spotcheck 0 VND mọi NAV — chi tiết [[capacity-ceiling-custom-vn30-2026]]):
> custom ex-VIC basket (creation-cap ~418B/day) gỡ alpha-mất rõ ở NAV lớn. Bảng CAGR 3 vehicle × 4 NAV:
> 500B: strict 13.11 → creation(VN30 thật) 16.58 → **custom 21.22%** (Sh1.49/DD−18.0/Cal1.18).
> Decompose: **cap-thuần (creation−strict) = +0.7→+3.5pp** (deployable-honest, beta VN30 thật, no hindsight);
> exVIC-leg (custom−creation) = +2.3→+4.6pp NHƯNG ~½ là survivorship-beta của rổ (custom@50 thắng cả khi
> chưa nghẽn). Production rule §8.3 (>200B → VN30 custom) VALIDATED, nhưng quảng cáo số honest = cap-leg +
> beta-thật-của-rổ-PIT, đừng claim nguyên +8.1pp. Files: custom_basket.py, ETF_LIQ=custom, basket_capacity_compare.py.

### (lịch sử) đề bài gốc — đề xuất ban đầu (đã thực hiện + tiến hóa thành custompitg ở trên)
**Mục tiêu**: ở 200B/500B, deploy config mất alpha vì tiền-nhàn-phình (58-65% NAV) chỉ park được ít vào E1VFVN30 (strict cap ~2-4B/day). Thay E1VFVN30 bằng **rổ VN30-custom (ex-VIC, có thể quality-tilt 8L)** có **creation-capacity** (~2320B/day = ~100x ETF) → xem gỡ được bao nhiêu CAGR ở 200-500B.
**Cách làm đề xuất**:
1. Tạo chuỗi giá tổng hợp "custom-basket" = return rổ VN30-ex-VIC (cap-weight hoặc quality-tilt) hàng ngày từ tav2_bq.ticker. Dùng nó thay `vn30_underlying` (vehicle parking).
2. ETF ADV cap = 20% × tổng trading-value rổ (creation-capacity), truyền qua `etf_adv_lookup`/`etf_liquidity_pct` (= mode "creation" nhưng vehicle là rổ custom thay ETF).
3. Chạy ở NAV_TOTAL_B=50/100/200/500, so vs strict-E1VFVN30 (bảng §6) → đo alpha gỡ lại.
**Kỳ vọng**: ở 200-500B, custom-basket-creation sẽ kéo CAGR lên gần mức 50B (vì tiền nhàn có chỗ deploy công-suất-lớn), nhưng là BETA có-kiểm-soát (ex-VIC). Lưu ý: cần kiểm rổ-ex-VIC có làm xấu/đẹp beta so VN30 đầy đủ không (2025 VIC kéo index → ex-VIC sẽ bắt ít sóng VIC hơn — đó là CHỦ ĐÍCH, đổi lấy justify-được).
**Caveat**: đây là execution-evolution, không đổi signal. Backtest-tương-đương mode "creation".

## 6. Bảng trần công suất (deploy config, strict ETF, full-history) — xem [[capacity-ceiling-custom-vn30-2026]]
| NAV | CAGR | Sharpe | DD | Calmar | cổ phiếu% | tiền-nhàn% | ETF% |
|---|---|---|---|---|---|---|---|
| 50B | 23.68 | 1.96 | −17.2 | 1.37 | 35 | 46 | 12 |
| 100B | 20.17 | 1.78 | −15.2 | 1.33 | 35 | 51 | 9 |
| 200B | 17.86 | 1.69 | −14.4 | 1.24 | 34 | 58 | 6 |
| 500B | 13.11 | 1.35 | −15.7 | 0.83 | 35 | 65 | 3 |
Cơ chế: cổ-phiếu% đứng ~35% mọi NAV → nút thắt = ETF parking không hấp thụ tiền nhàn (tiền-nhàn phình 46→65%). Ngưỡng ~200B (mất ¼ alpha). → đó là lý do cần rổ custom (§5).

## 7. Memory files đã ghi lượt này (load tự động qua MEMORY.md)
- `audited_versions_tally_2026.md` — bảng tổng mọi bản + ETF-cap + postbull + edge-alloc.
- `v23_audit_2014_now_deliverable.md` — chi tiết hành trình CAPIT gate (cap/maturity/ew2d/postbull/hard-block), cơ chế DD, walk-forward.
- `capacity_ceiling_custom_vn30_2026.md` — trần ~200B + thiết kế rổ custom.
- `simulation_always_audit_default.md` — quy ước audit + DT5G default.
- `capit_selection_study_2026.md` — chọn-mã CAPIT (chỉ golden PB_z robust).

## 8. Quy ước cố định (standing)
1. Chạy simulation/backtest → MẶC ĐỊNH kèm audit (1-file BQ-verifiable + spot-check; không báo "xong" nếu chưa pass).
2. DT5G (`tav2_bq.vnindex_5state_dt5g_live`) = state mặc định mọi chiến lược mới.
3. Production parking = strict ETF cap; >200B chuyển dần sang rổ VN30 custom.
4. Bài học xuyên suốt: panel curated/intraday/uncapped-ETF đều thổi phồng; chỉ delta cùng-harness + walk-forward + economic-prior (không tối-ưu-IS) đáng tin.
