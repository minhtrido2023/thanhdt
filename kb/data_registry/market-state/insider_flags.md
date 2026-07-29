---
kind: local-file
status: CANONICAL
source: data/insider_flags.json
group: market-state
role: KHÔNG money-path — WATCH-only shadow (chưa consumer nào)
writer: mike/agents/Taylor/insider_flags.py (2026-07-29, job Taylor_20260729_104614) — cron CHƯA cài, đề xuất 18:45 ICT T2-T6
selfcheck: mike/agents/Taylor/insider_flags_selfcheck.py + `insider_flags.py --selftest`
---

# data/insider_flags.json

**Status: CANONICAL** (nguồn duy nhất cho cờ "nội bộ bán mạnh") — nhưng **chưa ai tiêu thụ**.

## Là gì
Cờ per-ticker `{last_alert, tier, reasons, sell_pct_osh, n_sellers, window_end}` — cùng shape
`anomaly_flags.md`. Bắn khi trong 90 ngày: `sell_sh_90/OShares >= 1,0%` **VÀ** `nsell_90 > nbuy_90`
(số NGƯỜI phân biệt). Nguồn: `fundamentals/insider_transaction.md` (chỉ `DDIND`/`DDRP`,
`trade_status='Đã thực hiện xong'`, tự áp dấu theo `action_code`). `tier` luôn `W`.

## Ai ghi / cadence
`mike/agents/Taylor/insider_flags.py`, đọc **BQ LIVE** (bảng không có trong `bq_cache`).
**Cron chưa cài** tính đến 2026-07-29 — đề xuất `45 11 * * 1-5` (18:45 ICT), Mike quyết
(xem Phụ lục B.5 của `agents/Taylor/research/insider_transaction_scoping_20260729.md`).

## Bẫy
- **KHÔNG phải hard-exclude.** Reader là hàm RIÊNG `anomaly_gate.insider_sell_flagged(asof,
  ttl_days=90)` — **TTL 90 ngày, khác anomaly 30** — trả **dict** (không phải set) vì tiêu thụ là
  một dòng bằng chứng trong báo cáo due-diligence. **Đừng merge vào `anomaly_excluded()`**: ~80% mã
  bị bắt KHÔNG sập (§3.5 research file), merge sẽ âm thầm đổi hành vi loại mã của 4 sổ.
- **File chết âm thầm ≠ sạch.** Writer có cổng freshness: `MAX(public_date)` của bảng nguồn cũ hơn
  10 phiên → WARN + `exit 3`, KHÔNG ghi gì. Cờ cũ vẫn hết hạn theo TTL ở reader (cố ý không đóng
  băng). Nguồn hiện mới có **1 lần backfill 2026-07-27**, chưa quan sát được refresh thật ⇒ nếu
  bq_admin chưa fix bug, cron sẽ WARN + exit 3 hằng ngày từ khoảng **2026-08-07** — đó là hành vi
  ĐÚNG, không phải script hỏng.
- Writer merge có điều kiện: chỉ thay bản ghi cũ khi `last_alert` MỚI HƠN (tránh bản ghi lai
  ngày-này/số-kia khi cửa sổ 90d trượt). Ghi atomic `tmp` + `os.replace`.
