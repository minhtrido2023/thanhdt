## 2026-10-09 — NHÁNH 4: CHẠY LẠI NHÓM B (Q-sleeve / sector-cap+fincap / L1 pool) TRÊN ENGINE ĐÃ SỬA double-count — job `Taylor_20261008_172556` ⚠️ PAPER-ONLY, `trading_rules.json` KHÔNG ĐỔI

no_ledger: nghiên cứu đóng sổ verdict cũ, dispatch cấm pin vào kho; 28 ledger + md5 ở `mike/agents/Taylor/research/rerun_groupB_fixed_20261009/dsr_family_manifest_n4.json` (md5 f765b125f7737022d5b5c19b95dfc787) + `results.json`.
- PREREG `PREREG.md` md5 `4d73b7e825b841225eacb188e7ec86da` (commit `b0fe4df4`), N_trials=12, knob park **0,7** (= knob các nhánh gốc).
- Control tái lập pin **BYTE-IDENTICAL**: park 0,3 pin0% `4707bcbe…`, pin1M `bcd0469f…`. Control 0,7 (mới): `f524c1a0…` (pin0%) / `c0084fae…` (pin1M) — CAGR 24,47 / 26,11, MaxDD −18,7 / −18,5. Self-check 0 VND 28/28.
- Nguồn số (mọi CAGR/Sharpe/MaxDD/Calmar dưới đây): `results.json` md5 7231e75aa2b0275850a3de7e8a6beb4b, sinh bởi `analyze.py`.
- **Verdict mới (pin0% / pin1M, Δ vs neo cũ):** Q8 +0,20/−0,63 · Q12 +0,18/−0,36 ⇒ **HẾT Ý NGHĨA** (cũ −2,9 NO-GO) · QF8 −0,46/−0,57 ĐỨNG ·
  secA/secB/secB×1,5 ±0,1 HẾT Ý NGHĨA · fincap 0,30 −0,43/−1,59 **ĐỨNG** · fincap 0,45/0,55 HẾT Ý NGHĨA ·
  L1a +0,87/+1,89, **L1b +2,86/+2,66** (CI95 pin0% [+0,24;+4,29], DSR 0,86/0,67, LOO dương 13/13) ⇒ vẫn **chưa chứng minh**.
- PBO (13 cấu hình, CSCV S=16): 0,039 (pin0%) / 0,044 (pin1M). corr(dịch Δ, Δbank tỷ trọng) = −0,52 ⇒ bug phạt chân de-bank có hướng (chiều; biên độ lẫn vintage).
- **Claim canonical 07-12 "custom30V thắng nhờ BREADTH" KHÔNG còn đứng như đã viết**: toàn kỳ ngang nhau; breadth chỉ thắng IS 2014-19 (−2,1…−3,9pp), đảo OOS (+1,4…+4,4pp). MaxDD Q-sleeve nay chỉ xấu hơn 0,4-0,9pp (cũ 3,9-6,5pp).
- So leg park=0 (tham khảo, khác ≥2 trục): ở pin1M không chân nào @0,7 vượt Calmar 1,84 của park 0; giữ park=0. Nếu trigger lãi hạ: đo c30 vs l1b@0,3, tiền đăng ký mới.
- Báo cáo: `mike/agents/Taylor/research/rerun_groupB_fixed_20261009/REPORT.md`.
