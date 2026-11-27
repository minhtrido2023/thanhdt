---
kind: incident-index
title: Incidents — Mike fleet (sổ postmortem, cấu trúc OKF)
owner: Mike
status: active
updated: 2026-11-27
format: OKF — 1 sự cố = 1 file, index tự đồng bộ bởi bin/incidents_index_sync.py
entries: 253 file (115 sự cố + 137 RETRO + 1 mục open-items chung)
---

# Incidents — Mike fleet

Blameless postmortem log (Google SRE convention): what broke, why, the fix, the lesson.
Every entry traces to a verifiable artifact (commit hash, bus event, memory file) — no incident is recorded from memory alone. Newest first.

**When to add an entry:** anything that broke a live workflow, cost real money/time, or required a human to intervene outside the normal happy path.

## Cấu trúc thư mục

| Thư mục / File | Nội dung |
|---|---|
| `2026-10/` .. `2026-11/` | Sự cố gần đây — tên file `YYYY-MM-DD-<topic>.md` |
| [`archive-2026-Q2-Q3.md`](archive-2026-Q2-Q3.md) | Bảng sự cố đã lưu trữ (`2026-06/` .. `2026-09/`) |
| [`retro/index.md`](retro/index.md) | Kho RETRO hằng ngày (`retro/retro-YYYY-MM-DD.md`) |
| [`_open-not-yet-hardened.md`](_open-not-yet-hardened.md) | Mục "Open / not-yet-hardened" |

## Cách tra & ghi mới

```bash
grep -rn "<từ khoá>" mike/kb/incidents/
python3 mike/bin/incident_lookup.py "<label>" "<details>"
python3 mike/bin/incidents_index_sync.py --check   # --fix để tự đồng bộ
```

- Sự cố mới → tạo `incidents/<YYYY-MM>/<YYYY-MM-DD>-<topic>.md` với frontmatter (`kind: incident`, `date`, `topic`, `title`, `owner`, `status`, `updated`), rồi chạy `bin/incidents_index_sync.py --fix`.
- RETRO hằng ngày → `incidents/retro/retro-<YYYY-MM-DD>.md` (`bin/daily_retro.sh`), rồi đồng bộ vào `retro/index.md`.

## Sự cố (2 tháng gần nhất — mới nhất trước)

### 2026-11

| Ngày | Sự cố | status |
|---|---|---|
| 2026-11-21 | [2026-11-21 — `fleet_backup.sh`: commit mike-fleet bị discord-id-gate chặn 2 đêm (19+20/11), log vẫn có dòng \"✅ Backup pushed\"](2026-11/2026-11-21-fleet-backup-blocked-discord-id-gate-2-nights.md) | fixed |
| 2026-11-14 | [2026-11-14 — `production_manifest_selfcheck.sh` FAIL giả dưới cron/headless: file chỉ có gốc systemd bị coi \"rời production\"](2026-11/2026-11-14-production-manifest-selfcheck-dbus-false-drift.md) | logged |
| 2026-11-14 | [2026-11-14 — `cron_health_check.py` resolve log tương đối theo CWD của chính nó ⇒ 10 job báo LOG_MISSING giả VÀ không bao giờ được quét lỗi](2026-11/2026-11-14-cron-health-check-relative-log-path-blindspot.md) | logged |
| 2026-11-13 | [2026-11-13 — `tav2_bq.ticker` mất dải mã U*..Y* + VNINDEX 5 phiên (09-13/11) ⇒ DT5G publish abort, không có plan 16/11](2026-11/2026-11-13-ticker-raw-lost-U-Y-block-5-sessions.md) | fixed |
| 2026-11-11 | [2026-11-11 — Newline trong `approved_by` ⇒ preflight SpaceX RED giả + decision duyệt plan không lên bus](2026-11/2026-11-11-approved-by-newline-preflight-red-and-lost-decision.md) | fixed |

### 2026-10

| Ngày | Sự cố | status |
|---|---|---|
| 2026-10-29 | [2026-10-29 — auto-exit LAG/BAL quyết định theo mã (ngày vào = MIN) thay vì theo LÔ; dòng EOD lấy FILL đầu tiên](2026-10/2026-10-29-auto-exit-lot-level-entry-date.md) | fixed |
| 2026-10-24 | [memcap.sh không chạy được trong cron/headless (thiếu XDG_RUNTIME_DIR) — selfcheck PASS giả 1/4](2026-10/2026-10-24-memcap-no-user-bus-in-cron.md) | fixed |
| 2026-10-24 | [incidents_index_sync.py chèn lại cùng 1 dòng MỖI NGÀY — index.md nhân 59 bản trùng](2026-10/2026-10-24-incidents-index-sync-duplicate-row-daily.md) | fixed |
| 2026-10-24 | [Tóm tắt RETRO hằng ngày thỉnh thoảng không tới Trading Daily — finalize dispatch không ghim topic](2026-10/2026-10-24-daily-retro-finalize-summary-dropped-no-topic.md) | fixed |
| 2026-10-20 | [2026-10-20 — Container treo ~2,5h rồi reboot 22:23 ICT (nghi cạn RAM, CHƯA xác nhận kernel)](2026-10/2026-10-20-container-freeze-memory-suspected.md) | logged |
| 2026-10-16 | [EOD daily report 16/10 mất toàn bộ phần giao dịch — lệnh ATC khớp có `price=None`](2026-10/2026-10-16-eod-report-atc-fill-null-price-crash.md) | fixed |
| 2026-10-06 | [2026-10-06 — `zalopay-bid-sell-split-across-loan-packages`: lệnh BÁN 27 BID bị DNSE từ chối `HTTP 400: Trade quantity not enough` vì vị thế nằm ở 2 gói vay (1258:20 · 1826:7), không gói nào đủ 27](2026-10/2026-10-06-zalopay-bid-sell-split-across-loan-packages.md) | open-items |

## RETRO hằng ngày (14 bản mới nhất)

> Kho đầy đủ (137 bản): [`retro/index.md`](retro/index.md) — tự đồng bộ bởi `bin/incidents_index_sync.py`.

| Ngày | Tóm tắt RETRO |
|---|---|
| 2026-11-26 | [RETRO — 2026-11-26: 8 sự cố, 2 pattern xuyên suốt](retro/retro-2026-11-26.md) |
| 2026-11-25 | [RETRO — 2026-11-25: 4 sự cố (3 đã đóng, 1 nguyên nhân chưa rõ), 1 pattern xuyên suốt](retro/retro-2026-11-25.md) |
| 2026-11-24 | [RETRO — 2026-11-24 (viết bù bởi Winston): draft tự động mất vì usage-limit; ticker_prune 197 = hao mòn thành viên, không phải ghi thiếu](retro/retro-2026-11-24.md) |
| 2026-11-23 | [RETRO — 2026-11-23: 3 sự cố (cùng 1 gốc: plan 24/11 chưa có), 1 pattern xuyên suốt](retro/retro-2026-11-23.md) |
| 2026-11-22 | [RETRO — 2026-11-22: 2 sự cố (cả 2 đã đóng có bằng chứng), 1 pattern xuyên suốt, 1 vi phạm wakeup](retro/retro-2026-11-22.md) |
| 2026-11-21 | [RETRO — 2026-11-21: 1 sự cố (backup mike-fleet, đã đóng), 1 pattern xuyên suốt, 1 mục mở (báo cáo tuần INCOMPLETE)](retro/retro-2026-11-21.md) |
| 2026-11-20 | [RETRO — 2026-11-20: 2 sự cố, 1 pattern xuyên suốt](retro/retro-2026-11-20.md) |
| 2026-11-19 | [RETRO — 2026-11-19: 0 sự cố, 0 pattern xuyên suốt](retro/retro-2026-11-19.md) |
| 2026-11-18 | [RETRO — 2026-11-18: 1 sự cố (đóng sớm câu hỏi bus DD VCB, arch-reviewer REFUTED), 0 pattern mới escalate](retro/retro-2026-11-18.md) |
| 2026-11-17 | [RETRO — 2026-11-17: 1 sự cố (2 job DollarBill chạm usage limit, tự resume), 0 pattern xuyên suốt (1 pattern cũ ĐÃ ĐÓNG)](retro/retro-2026-11-17.md) |
| 2026-11-16 | [RETRO — 2026-11-16: 3 sự cố, 1 pattern xuyên suốt](retro/retro-2026-11-16.md) |
| 2026-11-15 | [RETRO — 2026-11-15: 4 sự cố, 2 pattern xuyên suốt](retro/retro-2026-11-15.md) |
| 2026-11-14 | [RETRO — 2026-11-14: 4 sự cố + 1 nhóm tooling nhỏ (cron_health_check đọc log theo CWD sai; manifest selfcheck FAIL giả thiếu D-Bus; weekly report 09–13/11 build fail do raw ticker…](retro/retro-2026-11-14.md) |
| 2026-11-13 | [RETRO — 2026-11-13: 4 sự cố (backup mike-fleet kẹt GH001 ngày thứ 4 — đã đóng; APPROVAL_GATE_BLOCK plan SpaceX — gate chạy đúng; classifier chặn 12 lần; plan T+1 16/11 chưa sẵn sà…](retro/retro-2026-11-13.md) |
