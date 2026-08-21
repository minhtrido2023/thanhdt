# Current Operations EXT — warm/reference sections
> Tách từ current_ops.md (2026-08-21, token-cost trim #4). Đọc khi cần, KHÔNG auto-load.
> Hot path (đọc mỗi phiên): `kb/current_ops.md`

## CAPIT — chi tiết đầy đủ

**Cơ chế:** `capit_fired` trong `data/golive_v23_status.json` là điều kiện NGÀY CHẠY, không phải cờ vị thế. Rổ đọc `n_capit_basket`/`capit_adv_caps`/`capit_dd_excluded` — ĐỪNG chép cứng mã. Nguồn vốn: `NAV_book_LAG × capit_size` (user chốt 07-20). Verify DNSE 07-31: **5 mã** SAB/SIP/VNM/PVT/NCT.

**PNJ EXCLUDED** (due-diligence gate, 2026-07-20, quant-skeptic CONFIRMED cao). Lãnh đạo bị bắt buôn lậu kim cương, giá sập ~-32%. `anomaly_flags.json` TTL 30 ngày (~hết hạn 08-23 nếu không có alert mới). Cổng xác nhận thật: BCTC Q3/2026 ~cuối tháng 10. Gate KHÔNG backtest được (n=1).

**universe_pit:** R3/CAPIT-breadth cutover production. CAPIT pool + ADV cap CỐ Ý còn ghim `ticker_prune` (đổi rổ đang giải ngân rủi ro cao, cấm cutover khi `capit_fired=true`). Checklist G5-G9: `kb/projects/universe-pit-migration.md`.

**Sizing bug 07-21** (thiếu 87,1tr SpaceX): đã đóng, user chốt KHÔNG bù. Chi tiết: `kb/projects/capit-sizing-bug-0721.md`.

---

## Domain-constraint layer — chi tiết đầy đủ

**P1 LIVE** (từ 2026-07-29, `d64717f`): `filter_lag_rating_orders()` — gate 8L rating≤3 tầng ORDER. Verify: 14/14 + 22/22 selfcheck, replay TRC/MST bị chặn, 0 lệnh khác đổi/21 plan thật.

**P0 ACTIVE HARD BLOCK** (từ 2026-08-04, `bb8583c`): `check_plan_funding()` trong `bot_execute.py:536`. Vượt ⇒ KHÔNG đặt bất kỳ lệnh nào của account đó. Shadow log: `data/plan_buying_power_shadow_log.csv`.

**2 bug đã vá (08-07):**
1. UPCOM (DRI): `loan_package_id=None` → WAIT_CASH vô hạn dù thừa tiền. Fix: luôn resolve gói vay theo MÃ (`_resolve_loan_package_id`), commit `c22bd1c`.
2. L2 JIT-unpark không cộng tiền bán cùng plan → chặn oan plan tự cấp vốn đủ (ZaloPay 08-07: 0/9 lệnh dù 8 lệnh bán PARK ~98,68tr). Fix: tín dụng JIT theo nhóm gói vay, commit `087a3d0`. Rủi ro tồn dư: lệnh bán chỉ đảm bảo THỬ trước, không đảm bảo KHỚP trước.

⚠️ SpaceX (margin) chưa có bản ghi `pp0Buy` thật — replay dùng PROXY `availableCash`. Thiết kế gốc: `agents/Taylor/research/ontology_constraint_layer_design_20260729.md`.

---

## Due-diligence và ADV gate

**Due-diligence MẶC ĐỊNH** (ship 2026-07-21): `trading_bot/due_diligence.py` — 5 trục (thanh khoản/valuation/PEAD/anomaly/FA thô), wire tại `golive_recommend_v23.py`/`send_plan_report.sh`/`eod_trading_report.sh`/`dc_book_waterfall_paper.py`. Thuần thông tin, không chặn/đổi sizing.

**ADV3T ≥ 2 tỷ/phiên — GATE CỨNG tầng CHỌN MÃ** (LIVE 2026-08-10, `c4ca90f`). `lag_liquidity_filter.py` (LAG) + `bal_filter_thin()` (BAL) loại thẳng <2 tỷ TRƯỚC due-diligence. Quyết định hiệu quả vốn (user chốt), không phải edge (backtest nói ngược: −0,26pp CAGR/PBO 0,916). Rollback: `ADV_MIN_VND = 0` trong `lag_liquidity_filter.py`. Chi tiết: `agents/Taylor/research/adv3t_hard_gate_wire_20260810.md`.

---

## Cron quan trọng (ICT)
| Giờ | Lịch | Việc |
|---|---|---|
| 08:25 | T2-T6 | cron_health_check_daily.sh — audit toàn bộ crontab |
| 08:30 | T2-T6 | check_report_cadence.sh — báo cáo quá hạn → dispatch Taylor + gửi email |
| 23:45 | T2-T6 | sync_bq_cache_daily.sh |
| 02:00 | Daily | kb_nightly.sh — archive events, trim memory, check ngưỡng KB |
| 02:00 UTC Fri | Weekly | kb_nightly.sh → editorial KB review |
| 03:30 Sat | Weekly | weekly_ops_audit.sh |
| 00:00 | Daily | backup.sh → GitHub |

---

## Vận hành/kiến trúc daemon
Remote-control daemon `mike@Mike.service` tắt hẳn từ 07-07 (user chỉ dùng Discord qua `ccdb-mike.service`). Model mặc định Mike = Sonnet 5, đồng bộ 3 tầng config (DB ưu tiên cao nhất). Chi tiết: [[reference-ccdb-model-config-layers]] + [[project-discord-only-workflow-remote-control-disabled]].

---

## Sự cố đã đóng
Audit cron C1/H2 (07-12), BQ cache monolith (07-13), cross-account contamination (07-19), 3 bug quoting silent-fail + full crontab audit (08-01) — tất cả FIXED+VERIFIED. Chi tiết: `kb/incidents/index.md`.
**Còn treo** (ưu tiên thấp): dọn crontab paper-trading lạc hậu (`Winston_20260712_151206`).
