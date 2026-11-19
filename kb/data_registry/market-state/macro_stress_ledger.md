---
kind: script-output
status: DISPLAY-ONLY (giả thuyết chưa kiểm — KHÔNG có consumer quyết định)
source: kb/data_registry/market-state/macro_stress_ledger.csv (append-only)
group: market-state
writer: mike/agents/Taylor/macro_stress_ledger.py — KHÔNG có cron mặc định; chỉ ĐỀ XUẤT wire vào báo cáo regime
role: sổ cụm căng thẳng vĩ mô độc lập (C1, Làn 3/F1 kế hoạch TE 04/11)
---

# `macro_stress_ledger.csv` — sổ cảnh báo căng thẳng vĩ mô

User duyệt 2026-11-19 (REPORT `agents/Taylor/research/arch_8l_dt5g_data_leverage_20261119/REPORT.md` §5 C1).
**Không cap, không sizing, không gate, không đụng `macro_state_live.py`, không đổi `w_LAG`.**

## PREREG (khoá 2026-11-19, ngưỡng đúng REPORT §3.2 — KHÔNG dò, KHÔNG đổi)
| Trigger | Điều kiện | Series (`tav2_bq.macro_indicator`) |
|---|---|---|
| `USDVND_60d` | USD/VND tăng >= +2,5% / 60 quan sát | vn_usdvnd |
| `TPCP10Y_d60` | TPCP 10Y tăng >= +0,75pp (75bp) / 60 quan sát; chỉ Δ (mức lệch VBMA +0,13…+0,21pp) | vn_bond_10y |
| `INTERBANK_MINUS_POLICY` | liên NH 3T − lãi điều hành >= 2,5pp (policy = quan sát tháng gần nhất <= ngày) | vn_interbank_3m, vn_policy_rate |
| `DXY_60d` | DXY tăng >= +5% / 60 quan sát | us_dxy |

Episode = lần kích hoạt đầu, rồi chết **126 quan sát** (`dead_until_approx` = +126 ngày làm việc, xấp xỉ).
**Fail-closed:** series ngày có quan sát cuối cũ hơn 7 ngày lịch ⇒ trigger `n/a(stale)`, không ghi sổ, không điền số cũ; `vn_policy_rate` (tháng) cũ hơn 100 ngày ⇒ T3 `n/a`.
Quan sát TE (`observation_date`), series ngày ⇒ không vướng độ trễ công bố; nguồn UNVERIFIED (`kb/data_registry/macro/macro_indicator.md`).

## Cột
`fire_date, trigger, value, threshold, dt5g_state, state_source, cluster_id, dead_until_approx, checked_at_ict`.
`dt5g_state` lấy qua `macro_state_live.get_gated_state` (1=CRISIS 2=BEAR 3=NEUTRAL 4=BULL 5=EX-BULL ⇒ ghi tên); lỗi ⇒ `UNAVAILABLE` (không chặn sổ, nhưng không tính vào cụm ≥NEUTRAL). `cluster_id`: dòng cách dòng trước > 60 ngày lịch ⇒ cụm mới (khuôn `cap_signal_advisory_log`). Đơn vị N = CỤM độc lập, không phải số dòng/trigger.

## Ngưỡng ĐƯỢC ĐỀ XUẤT cap (khai trước, REPORT §5 C1.5)
Tổng cụm độc lập **>= 10 VÀ >= 5 cụm khi DT5G >= NEUTRAL VÀ quant-skeptic CONFIRMED VÀ user duyệt riêng.** Đạt số cụm chưa phải điều kiện đủ. Chấp nhận trước rằng sổ có thể mãi chỉ là hiển thị. Bobby phân loại mù từng episode (cơ cấu tự cộng dồn vs cú sốc có mục tiêu) TRƯỚC khi ai xem lợi suất sau đó.

## Bẫy
- Đối chiếu lịch sử (`--replay`, 2014-01-02→2026-11-18, lịch quan sát từng series): 6/4/3/10 episode cho 4 trigger so với 5/4/3/11 của REPORT §3.2 (REPORT gióng lên lịch DT5G + ffill) — lệch ±1, cùng bậc N; sổ sống dùng lịch quan sát riêng từng series.
- Sổ chỉ ghi tiến, không backfill lịch sử (lịch sử chỉ là `--replay` in ra).
- Dòng hiển thị luôn có nhãn "GIẢ THUYẾT CHƯA KIỂM"; không diễn giải như tín hiệu mua/bán.
- Rollback: tắt dòng hiển thị; sổ để nguyên.
