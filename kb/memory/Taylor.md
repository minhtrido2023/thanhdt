# Working memory — Taylor
> Cập nhật mỗi khi đổi mạch việc. Chỉ giữ trạng thái hiện tại + open items.

## Trạng thái hiện tại (2026-06-30)
- Go-live 2026-07-01 V2.4 leverage-free — CONFIRMED, không đổi. SpaceX 0002023347, 1B VND.
- V2.4 @50B R3 chốt: CAGR 28.05% / Sharpe 1.87 / DD −18.8% / Calmar 1.50. threads=1 (commit 1325bf2).
- Bootstrap DD anchor: 5th-pct = −28.6% (KHÔNG phải −18%). P(DD<−30%)=3.3%. Plan sizing dựa −29%.

## V2.5 (post-go-live, chưa live)
- V2.5 = V2.4 + lever MGE=1.5 (HARD=1.65, breaker−15%, NAV-cap 100B). Account = 0002023347 (margin RocketX id=1840, borrow 12.5%). @50B: 30.05/1.82/−20.1/Cal1.49.
- Blockers B1-B4: DONE. trading_rules v1.9 v25_leverage DISABLED.
- **Reminder lên Mike 2026-07-07** (trigger trig_015A): hỏi user go-ahead build V2.5 live-recommend integration.
- Cần: port lever/recovery harness → recommend_tomorrow.py → paper vài tuần → flip live.

## Open tasks
- **#14 fill-timing review** — `execution_quality_review.py` schedule chạy 2026-06-30 18:30Z. Gate: CƠ CHẾ (window-adherence, 0 reject), KHÔNG gate bps (4 phiên quá ngắn). PASS → flip `fill_timing_live_gate=True`; FAIL → PENDING+report.
- **Sector sweeps** — đã xong #1–9 (retail/bank/RE/logistics/telecom/fertchem/rubber/steel/energy). Tất cả landing = lens/tilt, không phải standalone book (ngoại trừ banking có OOS edge nhưng 74% redundant với custom30V). **Await Mike dispatch** cho #10 hoặc synthesis.
- **New-listing feed** — 5 IPOs queued (DCV/VCK/RGG/TCX/SLD): thiếu lịch sử → parked post-go-live cho manual 8L research.

## Đã đóng (KHÔNG cần nhớ lại)
- Margin engine rebuild (S2/S4/S5/FIX4): DONE, committed 88fbbe5. Gated OFF byte-identical.
- Fresh-high-SUE / d_NPR / SUE-tilt / pbcombo / hold-neutral / MGE2.0 / liq-tilt / deep-discount / stability-floor / gq_score / fair-value: TẤT CẢ REJECTED. Giữ LAG binary as-is.
- Rating audit: HVN documented exception, stability floor REJECTED (−0.45pp). Giữ nguyên production.
- Bootstrap robustness: tool = `bootstrap_nav.py`; chạy SAU walk-forward TRƯỚC wire, KHÔNG screen mọi biến thể.
- [2026-07-01T06:12:21Z] EXTREME-regime exec gate: 3-step DONE (backtest CONFIRMED, coded default-OFF, self-check 14/14). NEXT: paper-test 4wk flag-ON in PAPER only + week-1 synthetic injection; LIVE enable needs USER duyet. Code: config.py+executor.py (extreme_regime_enabled=False). Files: extreme_regime_selfcheck.py, extreme_replay.py, data/extreme_regime_backtest.md.
- [2026-07-01T08:39:01Z] EXTREME-regime gate: PAPER-TRADING LIVE từ 2026-07-01 (user duyệt). extreme_regime_enabled=True CHỈ paper main (override trong secrets/trading_bot_accounts.json), SpaceX/live+global=False. Stress-injection 24/24 PASS (stress_extreme_regime.py). Target end ~2026-07-28 (~20 phiên). CHỜ: (a) zero false-trigger 4 tuần, (b) không can thiệp NORMAL, (c) user sign-off → mới bàn LIVE. NEXT: theo dõi paper sessions cho false-trigger.
- [2026-07-01T10:32:57Z] ĐANG DỞ: vol-scale chase-cap patch#3 (job Taylor_20260701_102950). Backtest NET entry-quality trên intraday_1m 16 names. NEXT: viết chase_cap_backtest.py, chạy, verify_finding.sh, nếu CONFIRMED code default-OFF flag chase_cap_vol_scale_enabled vào config.py+executor.py _limit_price. KHÔNG bật live.
