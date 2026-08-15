## Dự án đã đóng — 1 dòng/dự án, chi tiết `cat kb/projects/<file>.md`
<!-- Rút gọn 2026-08-10: mỗi dòng trước đây là 2-4 câu kể lại diễn biến. File này bơm vào MỌI
     dispatch có context_pack ⇒ tường thuật của việc ĐÃ ĐÓNG là chi phí trả lại mỗi phiên.
     Giữ đúng phần còn quyết định được hành vi sau này: TÊN · FILE · PHÁN QUYẾT (nhất là NO-GO,
     để không ai đề xuất lại). Diễn biến vẫn nguyên trong file chi tiết. -->
- 2026-08-13→14 corporate_action BQ integration + paper-report bug fix → `corporate-action-bq-integration-0813.md` — XONG, Việc A/B wire an toàn (6 vòng), SANITY_FACTOR WARN phương án C wire+CONFIRMED 08-14 (1 gap coverage nhẹ còn mở), vòng 6 rc=1/KeyError chủ động bỏ qua
- 2026-07-31 CAPIT sizing bug 07-21 → `capit-sizing-bug-0721.md` — ĐÓNG, đã fix; user chốt KHÔNG bù phần thiếu
- 2026-07-28 DGC + TV1 fear-buy due-diligence → `dgc-tv1-fearbuy-discretionary.md` — XONG, cả 2 QUALIFIED, theo dõi discretionary riêng
- 2026-07-21 LAG 07-24 (IVS/TMG/TRC) → `lag-0724-ivs-tmg-trc.md` — XONG, gate %ADV + lọc thanh khoản LAG đã wire
- 2026-07-20 Deposit-rate auto-crosscheck → `deposit-rate-autocheck.md` — XONG, tự động, không cần người
- 2026-07-17 DCF upgrade → `dcf-earning-power-upgrade.md` — earning-power **NO-GO** (giữ FCFE); refresh-gate cron LIVE
- 2026-07-13 World Cup + rổ lãi suất huy động → `wc-deposit-rate-gate.md` — **NO-GO** cả 2 hướng, N quá mỏng
- 2026-07-13 Plan-approval gate → `plan-approval-gate.md` — XONG, re-send 23:00 + code-gate `bot_execute.py`
- 2026-07-13 Plan ZaloPay transition 5/5 → `zalopay-transition-0713.md` — XONG
- 2026-07-13 DT5G BULL-giả → audit freshness → `dt5g-bull-fake-freshness-audit.md` — KHÉP KÍN, live không sai
- 2026-07-13 Báo cáo tuần 07-06→07-10 → `weekly-report-mechanism.md` — XONG, có WARN quá hạn
- 2026-07-13 Audit dữ liệu 8L (BCTC Q2) → `8l-data-audit.md` — XONG
- 2026-07-12 lag_edge_health.csv staleness → `lag-edge-health-staleness.md` — KHÔNG phải bug; check lại ~08-25
- 2026-07-12 fa_ratings/8L → `fa-ratings-rebuild.md` — re-tune 8L **NO-GO**; rebuild builder XONG
- 2026-07-12 V2.5 leverage → `v2.5-leverage-nogo.md` — **NO-GO**, giữ DISABLED (edge là IS-artifact)
- 2026-07-12 LAG-weight (tăng tỷ trọng PEAD) → `lag-weight.md` — ĐÓNG, KHÔNG tăng trần w_LAG
- 2026-07-12 Momentum-deals (MOM_N/MOM_S) → `momentum-deals.md` — KHÉP KÍN, production LIVE
- 2026-07-12 Q-sleeve → `q-sleeve.md` — **NO-GO** cả 2 trục
- 2026-07-12 Audit sẵn sàng BCTC Q2/2026 → `bctc-q2-readiness-audit.md` — KHÉP KÍN
- 2026-07-03 Usage-limit auto-resume → `usage-limit-auto-resume.md` — XONG
- 2026-07-02 Reliability hardening (AgentOps) → `reliability-hardening.md` — XONG

## Dự án ĐANG MỞ, chi tiết tách riêng (không inline `current_ops.md`)
- R&D pipeline (mọi thử nghiệm paper-only) → `rnd-pipeline-tracker.md`
- Migration `ticker_prune` → `universe_pit` (G5-G9) → `universe-pit-migration.md`
- LAG ADV>0 filter — đo edge vs hiện vật fill → `lag-adv-filter-tracking.md` — chủ Taylor, mở 2026-08-03.
  **KHÔNG kết luận gì** trước 2 mốc cứng: checkpoint **2026-12-15**, rà soát đầy đủ **2027-03-31**.
- CASH_VENDOR gate (số cổ tức từ `tav2_bq.corporate_action` khi broker không giải được) →
  `cash-vendor-gate-tracking.md` — user chốt 2026-08-15 **giữ ĐÓNG**; mở lại chỉ khi có ≥1 sự
  kiện ISS/hỗn hợp VÀ đã qua **2026-09-13**, và vẫn cần user xác nhận lần nữa lúc đó.
