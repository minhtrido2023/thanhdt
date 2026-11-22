# B2 — Kế hoạch xác nhận lại DD (CHỈ ĐỌC, sinh bởi bin/dd_reconfirm_plan.py)

Tổng 36 mã · FULL 4 · ? 12 · MECH 5 · OK 15
Nguồn giá/đáy vùng: /home/trido/thanhdt/WorkingClaude/data/dd_price_zone_watch_state.json, ngày watch gần nhất = 2026-11-20 (giá = close; "dưới đáy" = close < zone_low của entry cuối).
Luật: xem docstring bin/dd_reconfirm_plan.py. MECH = xác nhận cơ học, KHÔNG tự nâng nhãn CONFIRMED (chờ user chốt).

| P | Mã | Rev cuối | skeptic_final | Rev đã phản biện | Δtâm | Đổi nhãn | Lớp | Giá<đáy | close / zone_low |
|---|---|---|---|---|---|---|---|---|---|
| P1 | VGS | 2026-11-10#1 | FIXED_UNVERIFIED | không xác định | — | ? | **?** | có | 19200 / 19393 |
| P1 | FPT | 2026-11-01#3 | CONFIRMED | — | — | — | **OK** | có | 45000 / 45270 |
| P1 | NNC | 2026-11-03#5 | CONFIRMED | — | — | — | **OK** | không | 47450 / 30375 |
| P2 | TCH | 2026-10-31#3 | FIXED_UNVERIFIED | 2026-10-31#2 | +25.4% | có | **FULL** | có | 13900 / 14563 |
| P2 | HHS | 2026-11-01#4 | FIXED_UNVERIFIED | 2026-11-01#4 | +0.0% | không | **MECH** | có | 9700 / 12422 |
| P2 | DGC | 2026-10-30#2 | CONFIRMED | — | — | — | **OK** | có | 31000 / 33272 |
| P2 | DRI | 2026-11-03#3 | CONFIRMED | — | — | — | **OK** | có | 12600 / 12908 |
| P2 | SIP | 2026-11-01#3 | CONFIRMED | — | — | — | **OK** | có | 43000 / 43257 |
| P3 | DCM | 2026-11-04#2 | FIXED_UNVERIFIED | 2026-11-04#1 | -10.0% | không | **FULL** | không | 30400 / 21643 |
| P3 | PAT | 2026-11-17#2 | FIXED_UNVERIFIED | 2026-11-14#4 | -7.5% | ? | **FULL** | không | 70200 / 41000 |
| P3 | VLB | 2026-11-22#2 | FIXED_UNVERIFIED | 2026-11-22#1 | -4.7% | có | **FULL** | không | — / 33336 |
| P3 | BSR | 2026-11-09#1 | FIXED_UNVERIFIED | không xác định | — | ? | **?** | không | 23600 / 13093 |
| P3 | CST | 2026-11-11#1 | FIXED_UNVERIFIED | không xác định | — | ? | **?** | không | 14100 / 6316 |
| P3 | CSV | 2026-11-09#1 | FIXED_UNVERIFIED | không xác định | — | ? | **?** | không | 20300 / 15825 |
| P3 | DBC | 2026-11-18#1 | FIXED_UNVERIFIED | không xác định | — | ? | **?** | không | 16300 / 11314 |
| P3 | GAS | 2026-11-09#1 | FIXED_UNVERIFIED | không xác định | — | ? | **?** | không | 70500 / 43327 |
| P3 | LLM | 2026-11-18#1 | FIXED_UNVERIFIED | không xác định | — | ? | **?** | không | 33700 / 3630 |
| P3 | POW | 2026-11-18#1 | FIXED_UNVERIFIED | không xác định | — | ? | **?** | không | 13300 / 7166 |
| P3 | SZL | 2026-10-26#2 | FIXED_UNVERIFIED | không xác định | — | ? | **?** | không | 27050 / 22936 |
| P3 | TTA | 2026-11-20#1 | FIXED_UNVERIFIED | không xác định | — | ? | **?** | không | 10300 / 5235 |
| P3 | VCB | 2026-11-17#1 | FIXED_UNVERIFIED | không xác định | — | ? | **?** | không | — / 30800 |
| P3 | VCP | 2026-11-12#1 | FIXED_UNVERIFIED | không xác định | — | ? | **?** | không | 37400 / 20997 |
| P3 | MSB | 2026-11-09#1 | FIXED_UNVERIFIED | 2026-11-09#1 | +0.0% | không | **MECH** | không | 16550 / 9675 |
| P3 | PNJ | 2026-11-14#1 | FIXED_UNVERIFIED | 2026-11-14#1 | +0.0% | không | **MECH** | không | 13500 / 6370 |
| P3 | QTP | 2026-11-17#3 | FIXED_UNVERIFIED | 2026-11-17#3 | +0.0% | không | **MECH** | không | 10200 / 6300 |
| P3 | SCL | 2026-10-29#5 | FIXED_UNVERIFIED | 2026-10-29#5 | +0.0% | không | **MECH** | không | 25100 / 17445 |
| P3 | DDV | 2026-10-28#2 | CONFIRMED | — | — | — | **OK** | không | 14600 / 13315 |
| P3 | HPG | 2026-10-31#4 | CONFIRMED | — | — | — | **OK** | không | 20450 / 13316 |
| P3 | MBB | 2026-10-31#3 | CONFIRMED | — | — | — | **OK** | không | 18250 / 14729 |
| P3 | MVC | 2026-11-03#9 | CONFIRMED | — | — | — | **OK** | không | 13600 / 9940 |
| P3 | NT2 | 2026-10-26#2 | CONFIRMED | — | — | — | **OK** | không | 23850 / 18301 |
| P3 | PVP | 2026-10-29#2 | CONFIRMED | — | — | — | **OK** | không | 16750 / 13799 |
| P3 | PVT | 2026-10-29#2 | CONFIRMED | — | — | — | **OK** | không | 18650 / 13903 |
| P3 | SAS | 2026-10-26#2 | CONFIRMED | — | — | — | **OK** | không | 31300 / 25083 |
| P3 | TV1 | 2026-11-02#6 | CONFIRMED | — | — | — | **OK** | không | 24200 / 8823 |
| P3 | TV2 | 2026-11-01#2 | CONFIRMED | — | — | — | **OK** | không | 28400 / 7702 |

## Ghi chú đọc bảng
- **12 mã "?"** gần hết là mã chỉ có 1 rev trong sổ mà status ghi "đã áp sửa" (bản skeptic thực sự đọc không nằm trong sổ) ⇒ luật không suy được, KHÔNG đoán; Mike quyết có phản biện lại hay không.
- **5 mã MECH**: HHH (P2, dưới đáy), MSB, PNJ, QTP, SCL — status ghi CONFIRMED cho chính rev cuối nhưng `skeptic_final` còn FIXED_UNVERIFIED (backfill luật 22/11). Chưa nâng nhãn; chờ user chốt có chấp nhận "CONFIRMED-cơ-học" không.
- **VLB/VCB/TTA…** không có trong state watch 20/11 (DD mới) ⇒ cột close "—", không xét được P2.
- Nhãn "đổi" là suy từ chữ trong `verdict_label` (NON/RẺ/DƯỚI/TRONG/TRÊN) — heuristic, không phải trường có cấu trúc.
