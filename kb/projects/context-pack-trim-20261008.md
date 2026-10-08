# Trim context_pack 2026-10-08 (job Wags_20261008_133659) — mục lục di chuyển
> Quy tắc: CHỈ DI CHUYỂN nguyên văn, không viết lại sự thật. Mỗi khối dưới đây/ở file đích
> mang tiêu đề `Chuyển từ kb/<file> L<a>-<b>` (số dòng theo master ea5c066d).
> Kiểm: `python3 bin/kb_move_verify.py --base ea5c066d`.

## Chuyển từ kb/current_ops.md L3-4 (trim 2026-10-08, Wags_20261008_133659) — header current_ops cũ
> Cập nhật lần cuối: 2026-08-21 (token-cost trim #4 — warm sections → `kb/current_ops_ext.md`;
> giữ lại hot path: kill-switch, trading status, signal holds, routing rules).


## Bảng di chuyển
- kb/current_ops.md L3-4 → `kb/projects/context-pack-trim-20261008.md` — header current_ops cũ
- kb/current_ops.md L16-16 → `kb/projects/rnd-pipeline-tracker.md` — AlphaLens Paper (đã đóng)
- kb/current_ops.md L17-30 → `kb/projects/dnse-trung-vang-legal-review-20260927.md` — Trứng vàng — dòng trạng thái đầy đủ + đính chính bản chất 2026-09-27
- kb/current_ops.md L34-35 → `kb/projects/dnse-trung-vang-legal-review-20260927.md` — Trần đề xuất (chưa user chốt) — đã bị user chốt 2026-10-05 thay thế (dòng ✅ ở current_ops)
- kb/current_ops.md L44-44 → `kb/projects/deposit-rate-effective-rate-20261001.md` — rating_8l/DCF effective rate — dòng đầy đủ
- kb/current_ops.md L68-68 → `kb/projects/corp-action-nav-chain-20260922.md` — close_repair.py Layer 2 — dòng đầy đủ
- kb/current_ops.md L71-71 → `kb/projects/corp-action-nav-chain-20260922.md` — NAV corp-action gate v2 — nhánh cổ tức tiền
- kb/current_ops.md L73-74 → `kb/projects/corp-action-nav-chain-20260922.md` — NAV corp-action gate v2 — nhánh --from-raw / không giải thích được
- kb/current_ops.md L75-75 → `kb/projects/corp-action-nav-chain-20260922.md` — Ex-date price-frame — dòng đầy đủ (sự cố gốc VPB)
- kb/current_ops.md L76-76 → `kb/projects/corp-action-nav-chain-20260922.md` — Ex-date price-frame — nhánh marketPrice
- kb/current_ops.md L78-78 → `kb/projects/corp-action-nav-chain-20260922.md` — Ex-date price-frame — rc=7
- kb/current_ops.md L80-80 → `kb/projects/corp-action-nav-chain-20260922.md` — Ex-date price-frame — selfcheck/replay
- kb/current_ops.md L85-90 → `kb/projects/corp-action-nav-chain-20260922.md` — dividend_adjusted_return qty_entitled — chi tiết vá, Q1, broker_qty (sau đã LIVE 4b59c6d1)
- kb/current_ops.md L92-92 → `kb/projects/corp-action-nav-chain-20260922.md` — Vendor mismatch ⇒ UNVERIFIED — dòng đầy đủ
- kb/current_ops.md L94-99 → `kb/projects/corp-action-nav-chain-20260922.md` — Vendor mismatch — D1, SANITY_REL, hợp đồng 7 trường, alert, đường phát lại, selfcheck
- kb/current_ops.md L100-105 → `kb/projects/corp-action-nav-chain-20260922.md` — lookup_failed (206dd348) — dòng đầy đủ + chi tiết
- kb/current_ops.md L106-107 → `kb/projects/corp-action-nav-chain-20260922.md` — broker_qty gộp TỔNG lô + vá a56203f2 — dòng đầy đủ
- kb/current_ops.md L109-109 → `kb/projects/corp-action-nav-chain-20260922.md` — Bẫy đường dẫn selfcheck — dòng đầy đủ
- kb/current_ops.md L113-116 → `kb/projects/corp-action-nav-chain-20260922.md` — 4 call-site còn lại — chi tiết Việc 4/3/1/2
- kb/current_ops.md L117-117 → `kb/projects/corp-action-nav-chain-20260922.md` — Sự cố phụ arm giả VPB — dòng đầy đủ
- kb/canonical.md L317-324 → `kb/projects/corp-action-nav-chain-20260922.md` — QUY TẮC DNSE ex-date — bản nháp expected_exdate_adjustment bị gỡ 09-12
- kb/current_ops.md L123-128 → `kb/projects/measurement-integrity-audit-20260927.md` — Lý do mở cadence
- kb/canonical.md L18-36 → `kb/projects/r3-pin-history.md` — Dải pin — điểm thận trọng 25,24%, chân maturity 25,34%, min_age, giới hạn pin1M
- kb/canonical.md L42-89 → `kb/projects/r3-pin-history.md` — Pin quinquies SUPERSEDED, đính chính 24,42%, ba rail park 0,30, bối cảnh 24,42%, sửa lỗi đo 09-27, LAG_ADV_BASIS, số lịch sử khác vintage, MIXED-universe, fidelity liq<=0
- kb/canonical.md L93-99 → `kb/projects/r3-pin-history.md` — Bootstrap 5th-pct (quinquies) + chuỗi SUPERSEDED
- kb/canonical.md L102-105 → `kb/projects/r3-pin-history.md` — DSR/PBO — họ gốc 68 file + caveat mtime
- kb/canonical.md L116-118 → `kb/projects/r3-pin-history.md` — FAIL-C đóng — A/B
- kb/canonical.md L123-124 → `kb/projects/r3-pin-history.md` — Ghi chú bootstrap/FAIL-F branch/PBO 2 cây (viết trước merge 3c944443/f2cfb124)
- kb/canonical.md L129-135 → `kb/projects/r3-pin-history.md` — Parking @0,7 SUPERSEDED + +7.4pp Full SUPERSEDED
- kb/canonical.md L212-216 → `kb/projects/r3-pin-history.md` — Quy chuẩn #5 — cập nhật DSR/PBO 2026-09-27 (bis), trước manifest
- kb/canonical.md L140-158 → `kb/projects/screen-sort-direction-bug-20260927.md` — Lỗi + mức độ sai + hệ quả nghiên cứu
- kb/canonical.md L257-262 → `kb/projects/breadth-tercile-axis-20260822.md` — Bằng chứng 0/27 ô, job E 0/4
- kb/canonical.md L266-289 → `kb/projects/breadth-tercile-axis-20260822.md` — Trục khác 0/12, lý do 08-22, cách tính breadth chuẩn
- kb/canonical.md L292-294 → `kb/projects/breadth-tercile-axis-20260822.md` — Nguồn quyết định + tái kiểm

## Vòng 2 (job Wags_20261008_143309) — dòng bị SỬA/đóng, bản CŨ nguyên văn
> 4 dòng dưới đây đã được SỬA tại chỗ (không chỉ chuyển): rc=5 runbook đã LIVE; park live nay 0% (canonical từng ghi 0,30 là production). Bản cũ giữ ở đây để `kb_move_verify.py` vẫn sạch.
<!-- từ kb/current_ops.md -->
  Selfcheck 38/0 + 64/0 + 8/0 qua 3 TZ. rc=5 là mã MỚI: `eod_trading_report.sh` không ghi marker, `nav_sync_retry.sh` không retry 2h, `nav_snapshot_daily.sh` escalate ngay. Runbook rc=5 ở `kb/ops_runbook.md.proposed` — **CHỜ MIKE DUYỆT ĐỂ ĐƯA LIVE (§13)**.
<!-- từ kb/canonical.md -->
  R3 @park 0,30 = **23,37% (`pin0%`, NGƯỠNG SÀN — tiền nhàn rỗi 0%/năm) … 25,71% (`pin1M`, NGƯỠNG
<!-- từ kb/canonical.md -->
  FAIL-C đã đóng) **và** đúng knob park live 0,30. Neo sizing DD (bootstrap 5th) = **−25,2%**;
<!-- từ kb/canonical.md -->
- **NEUTRAL parking custom30V @0,30 (production) = +1.06pp CAGR** (23.43% vs 22.37% park=0) — và ở

## Chuyển/sửa tại chỗ — vòng Mike tự sửa (2026-10-08 22:2x ICT, user duyệt 22:14) — bản CŨ nguyên văn
- **V2.5** (future) = V2.4 + lever MGE=1.5, account sẵn sàng, DISABLED, reminder 2026-07-07.
⚠️ R3 vẫn CHƯA có code path nào đọc (văn bản chính sách); việc wire R2 đọc R3 chờ arch-review.
