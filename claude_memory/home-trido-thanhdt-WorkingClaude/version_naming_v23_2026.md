---
name: version-naming-v23-2026
description: Quy ước tên chốt [REDACTED]11 — V2.3C = champion plain-sum (base mọi backtest); V2.3A = V2.3C + LAG-allocator = bản LIVE pt_v22_dt5g.py; luôn ghi nhãn baseline + loại cửa sổ trong output
metadata: 
  node_type: memory
  type: project
  originSessionId: f1529c7a-f12f-478e-8f9f-57863e07b898
---

**Quy ước tên (user chốt [REDACTED]11), dùng trong MỌI bảng kết quả từ nay:**

- **V2.3C** (Champion/Core) = plain-sum TĨNH: BAL (V11, 25B) + LAG (PEAD, 25B) cộng 2 sổ 50/50 độc lập + CAPIT v2.1 (elig hybrid v21c) + gating DT5G. **Đây là BASELINE chuẩn cho mọi backtest/ablation** (host của exbull-test, breadth-gate test...). Tham chiếu: FULL 25.77%/DD−20.1/Sh1.65, 2025+ 18.30%/Sh1.04 (harness session allocator). Snapshot variance ±0.3pp giữa các harness (25.48 file pt_v22fix cũ / 25.67 harness bgate) = nhiễu chi tiết (ETF history, elig version), KHÔNG phải khác config.
- **V2.3A** (Allocator) = **V2.3C + lớp phân bổ vốn động, không khác gì khác** = bản **LIVE** trong pt_v22_dt5g.py (wired [REDACTED]11): một-ví-chung, w_LAG theo state {CRISIS .50 / BEAR 0 / NEU·BULL·EXBULL .65} + rebalance band-only ±10pp. Tham chiếu: FULL 26.29%/DD−18.3/Sh1.80/Cal1.43. Khác biệt hành vi duy nhất vs V2.3C: BEAR rút LAG về 0 (chủ đích — LAG lỗ −14%/yr in bear).

- **V2.4** (đặt tên user [REDACTED]20) = **V2.3A + custom30V parking + gated-overflow + HAG eq_flag fix** = cấu hình DEPLOY LÕI tốt nhất (go-live [REDACTED]30). Chi tiết: engine V2.3A (`v23a none postbull 0 edge`); parking = custom30V (custompitg/namecap/yieldcombo, NEUTRAL-only <150B, +3.7pp vs rổ blend cũ); insurance = gated-overflow (bear-washout, IS+0.00/OOS+1.17); eq_flag dual-leg (HAG ổn rating 5); conditional bull-park = tùy chọn DORMANT (`BULL_PARK_COND` default OFF). Tham chiếu pinned @50B NEUTRAL-only (registry R3, snapshot [REDACTED]19): **CAGR 28.26% / Sharpe 1.87 / DD−18.8 / Cal1.50**, self-check 0 VND; @20B (R1) 31.69%. **Tên gọi production từ [REDACTED]30.** Số pin: `data/results_registry.md` (R1-R5). [[repro_results_registry_2026]]

**Quy tắc trình bày kết quả** (user yêu cầu sau vụ nhầm +30.8%-calendar-2025 vs 18.3%-annualized-2025+): mỗi bảng phải ghi rõ (1) nhãn baseline V2.3C hay V2.3A, (2) loại cửa sổ: calendar-year (01/01→31/12) vs annualized-window ("2025+" = CAGR 2025-01→now, trộn cả 2026). Hai số cùng thực tế: 2025 calendar +30.9% × 2026 YTD −4.0% ⇒ "2025+" ≈ 17.3%/yr.

Ablation/test mới: host trên V2.3C (cô lập hiệu ứng, tránh lẫn với allocator band phản ứng cash). Deploy lên live = thêm vào V2.3A. Chi tiết hai bản: [[v4-faithful-reproduction-2026]], [[lag-bal-state-conditional-allocator-2026]].
