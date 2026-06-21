# SESSION HANDOFF — custompitg parking deploy + 8L moat/earnings-quality audit (2026-06-14)

> Đọc file này + các memory ở §7 là đủ context tiếp tục. Mọi kết quả BQ-auditable (T+1 Open, tav2_bq.*,
> self-check 0 VND). Quy ước: chạy simulation = kèm audit; DT5G = state mặc định.
> **GO-LIVE dự kiến 2026-06-15** với config dưới đây.

---

## 1. TL;DR — session này làm gì (nối tiếp HANDOFF 2026-06-13 §5)
1. **§5 custom-basket parking XONG + DEPLOYED**: thay E1VFVN30 bằng rổ tự-quản **custompitg** trong production
   `pt_v22_dt5g.py`. Rổ = rule-based (KHÔNG hardcode VIC), 30 mã liquid ICB-not-null, rebal **05/Feb-May-Aug-Nov**,
   gate **8L rating≤3**, cap-weight, capacity ~20%×ADV (~500B/day = ~100x E1VFVN30). custom_basket.py.
2. **8L rating sửa TẬN GỐC** (user-driven, 3 bước): (B1) thêm **earnings-quality gate** (HAG-type lãi-phi-lõi →
   rating 5) + **moat governance "siết A-mềm"** (moat notch +1 CHỈ khi 5F-audit=WIDE); (B2) screener/bot mặc định =
   **giao 2-trục** (quality×value); (B3) reconcile bản copy + audit-queue rỗng. Republish `fa_ratings_8l`.
3. **Re-validate post-fix**: chạy lại custompitg sweep, KHÔNG bất thường (delta nhỏ, PIT-gated).

## 2. GO-LIVE state (verify 2026-06-14)
- **DT5G = state 3 (NEUTRAL)** (2026-06-10/11/12) → **parking ĐANG BẬT** ở go-live.
- `pt_v22_dt5g.py`: `PARK_VEHICLE` mặc định `custompitg` (rollback: env `PARK_VEHICLE=etf`). Cả 2 sổ BAL+LAG
  `cash_etf_states={3:0.7}` (park 70% tiền nhàn CHỈ khi NEUTRAL), `vn30_underlying`=rổ custompitg.
- Rổ parking quý hiện tại (rebal 2026-05-05, 30 mã): SHB,SSI,HPG,VIX,VHM,FPT,MBB,MWG,VPB,HDB,BSR,CTG,VCB,TCB,
  VNM,SHS,VRE,ACB,VND,VCI,DGC,GAS,BID,HCM,VSC,DXG,POW,HAG→**đã loại** (rating5),DIG,GVR,TPB. (VHM/VRE vào, VIC out by rule.)
- **Số custompitg post-fix (full 2014→nay, BQ-auditable, self-check 0)**: 50B **25.87%**/Sh1.79/DD−17.8/Cal1.45 ·
  100B 23.82/1.70/−17.2/1.39 · 200B 21.28/1.58/−15.8/1.35 · 500B 18.83/1.46/−17.9/1.05.

## 3. Parking dùng KHI NÀO + thời-điểm-đi-tiền (user đang cân nhắc đổi)
- **State-conditional**: CRISIS(1)/BEAR(2) → KHÔNG park (tiền nhàn = cash thật, phòng thủ); **NEUTRAL(3) → park 70%**
  tiền nhàn vào rổ, 30% giữ cash; BULL(4)/EXBULL(5) → không rule (sổ gần full cổ phiếu).
- **4 nhịp đi tiền**: (a) parking JIT (mua rổ SAU khi lệnh cổ phiếu khớp; bán TRƯỚC khi cần tiền/đổi state);
  (b) cap 20%×ADV → tự rải DCA nhiều phiên; (c) rebal rổ 05/m2; (d) cổ phiếu sổ T+1 Open, ramp 3 phiên.
- **⏳ USER ĐANG SUY NGHĨ (chưa quyết)**: có nên đổi thời-điểm-đi-tiền không. Cần-gạt: tỷ-lệ-park-theo-state
  (hiện NEUTRAL 70%); có park ở state khác không; **re-risk timing CRISIS/BEAR→NEUTRAL** (điểm đáng cân nhất —
  lúc tiền-phòng-thủ thành tiền-park-beta; hiện đã chậm nhờ DT5G price-confirmed + ADV-cap; có thể thêm điều kiện
  chờ washout); nhịp deploy JIT vs staged. → session mới có thể mô phỏng biến thể timing nếu user muốn.

## 4. 8L rating sửa tận gốc — chi tiết (xem [[rating_8l_credit_scale_2026]], [[moat_must_be_audited_2026]])
- **Earnings-quality gate** (`eq_flag` trong rating_8l.py + rating_8l_history.py + build_rating_8l_history.py):
  COMPOUNDER/CYCLICAL, **NP_TTM ≥ 0.9×GP_TTM (hoặc lãi trên gross-loss) + có nợ (real_lev≥0.25)** → cap 4; +CF_OA_5Y≤0
  → **5**. HAG 2→5. Sector/leverage-aware (tha broker, net-cash holdco VEA/PHR, growth-capex VJC/FRT). 16 mã fire/3 liquid.
- **Moat governance "siết A-mềm"**: moat notch +1 (đẩy prelim 2/3 lên đỉnh) **CHỈ khi `moat_tags.csv` moat_tier=WIDE**
  (3 mã: VNM/TLG/DHG). Registry NARROW/NONE → no notch. **Quant-fortress core≥10 giữ rating 1 độc-lập-moat** (notch chỉ
  áp prelim 2/3). Ngoài-registry → giữ quant (audit dần). LIVE: FPT/MCH/SCS/FOX/VCS...→2 (moat-lifted revoke),
  SAB/BMP/NNC core≥10 giữ 1, GMD→3, SGP→3. PIT-gated eff≥2025-06 (deep history nguyên).
- **STANDING RULE (codified trong rating_8l.py docstring header)**: moat upgrade ⇒ phải qua 5F audit
  (/competitive-analysis + /comps-analysis) ghi moat_tags.csv; ngoài-registry chỉ là placeholder tạm, khi thành
  screener-relevant PHẢI audit trước. Proxy GPM/ROE KHÔNG thay được audit.
- **Publisher**: `rating_8l_history.py` → `CREATE OR REPLACE tav2_bq.fa_ratings_8l` (PIT, 52,456 quý). Consumers:
  regime_size_overlay (BAL book weak-flag rating≥4, đọc fa_ratings_8l PIT merge_asof), custompitg parking gate,
  screener/bot. (D1/RE_BACKLOG đọc fa_ratings flat cũ — KHÔNG đụng.)

## 5. Screener 2-trục (B2) + reconcile (B3)
- `rating_8l.py` thêm output `data/rating_8l_screener.csv` = rating≤3 (moat-audited) × pb_z × liq, 3 zone:
  🟢 **BUY-NOW** (pb_z≤−0.3+book-OK, 26 mã: ACV/VNM/DGC/VGC/SCS/VHC/NT2/CTR/IDC...), 🟡 ACCUMULATE (38), 🔴
  **WATCH-RICH** (pb_z>0.6 chất-lượng-nhưng-đắt ĐỪNG ĐUỔI, 50: MCH/VTP/SAB/BMP/VCB...). bot `format_topn` repoint
  từ rank-composite → screener 2-trục (composite giữ ở `_format_rank_composite`).
- Reconcile: live=ROOT (pt_8l_daily.bat). `8l_package/rating_8l.py` đã SYNC identical root. `release_8l*/`=frozen archive.
  ⚠ **maintenance**: sửa root rating_8l.py sau này phải `cp` lại 8l_package (single-source root).

## 6. ⚠ Gotchas / known issues
- **bq transient crash 0xC0000142** (STATUS_DLL_INIT_FAILED): thỉnh thoảng ở run thứ 3-4 trong sweep dài (Windows
  subprocess spawn exhaustion). KHÔNG phải bug logic → chạy lại fresh-shell là OK. Sweep nên có timeout + retry.
- **45 mã non-registry rating-1**: 22 quant-fortress (core≥10, OK), 18 nhờ moat↑1 chưa-audit NHƯNG illiquid
  (liq<0.3B, ngoài screener) → defer audit dần đúng. 0 mã liquid dựa moat chưa-audit.
- Chạy nhiều pt_v23 song song = tranh bq → timeout + log nhiễu. Chạy TUẦN TỰ.

## 7. Memory files (load qua MEMORY.md)
- `moat_must_be_audited_2026.md` — RULE moat-phải-audit + wiring "siết A-mềm" + B2/B3 + re-validate.
- `rating_8l_credit_scale_2026.md` — methodology 8L + EQ-gate section.
- `capacity_ceiling_custom_vn30_2026.md` — trần công suất + custompit/custompitg + PIT de-hindsight + deploy.
- `audited_versions_tally_2026.md`, `simulation_always_audit_default.md`.

## 8. Files đụng lượt này
- `custom_basket.py` (build + build_pit rebal/gate_rating), `pt_v22_dt5g.py` (PARK_VEHICLE), `pt_v23_audit_2014.py`
  (ETF_LIQ=custom*|custompit*|custompitg), `rating_8l.py`+`8l_package/` (eq_flag+MOAT_TIER+screener), `rating_8l_history.py`
  (publisher), `build_rating_8l_history.py`, `bot_8l_commands.py` (format_topn 2-trục), `data/moat_tags.csv` (+moat_upgrade col),
  `data/rating_8l_screener.csv`, `data/basket_final_table.py`, `data/v23_audit_spotcheck.py` (scale+PIT-aware).

## 9. Quy ước cố định (standing)
1. Simulation/backtest → MẶC ĐỊNH kèm audit (1-file BQ-verifiable + spot-check; không báo "xong" nếu chưa pass).
2. DT5G (`tav2_bq.vnindex_5state_dt5g_live`) = state mặc định.
3. **Moat → phải 5F-audit (moat_tags.csv) mới được nâng-hạng/gate; proxy GPM/ROE không thay được.**
4. Panel curated/intraday/uncapped-ETF thổi phồng; chỉ delta cùng-harness + walk-forward + economic-prior đáng tin.
