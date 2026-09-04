# Prereg — Regime-conditioned cash-dividend pre-ex gate (formal, Taylor)

**Job**: `Taylor_20260904_111503` · **Ngày**: 2026-09-04 · Kế tiếp Mike interactive
(`Taylor_20260904_111503` dispatch, đính chính mapping regime của
`regime_conditioned_gate_mike_20260904.md`).

Prereg này KHOÁ giả thuyết + ngưỡng + tiêu chí FAIL **trước khi chạy lại outcome**. Số liệu Mike
báo cáo (đã sửa mapping) dùng làm TARGET để đối chiếu tái lập độc lập — không phải để tune thêm.

## Mapping regime chuẩn (macro_state_live.py:42 + BQ `tav2_bq.vnindex_5state_dt5g_live`)
1=CRISIS, 2=BEAR, 3=NEUTRAL, 4=BULL, 5=EXBULL. Xác nhận trực tiếp bằng BQ
`SELECT state, COUNT(*) FROM tav2_bq.vnindex_5state_dt5g_live GROUP BY state` (2026-09-04):
state 1..5 tồn tại đủ 5, không có state 0.

## Mẫu
`cash_events_analyzed.csv` (đã có sẵn từ proxy sprint `Taylor_20260904_094347`), lọc thêm:
- `c14 >= 10000` (giá tối thiểu, loại penny cực mỏng)
- `raw_yield = div_vnd/c14 <= 0.50` (loại outlier/lỗi dữ liệu, ký hiệu "yield_pct<=50" trong dispatch)
- regime đo tại `t14` (PIT, as-of backward), deposit rate PIT cũng đo tại `t14` qua
  `deposit_rate_vn.merge_deposit(df, time_col='t14')`
- `prior_3y` = số sự kiện CASH của CÙNG ticker có `ex_date` trong (event.ex_date − 1095 ngày,
  event.ex_date) — đếm trên toàn bộ CASH events (không áp price/yield filter khi đếm lịch sử).
- `excess` = `raw_yield*100 − deposit_rate_pit` (điểm % — dose-response bucket 0-4/4-8/>8pp)

## Giả thuyết khoá

- **H1**: gate `regime∈{CRISIS,BEAR} & excess>0 & prior_3y>=3 & c14>=10000` có median
  ABNORMAL_RETURN > 0 (Wilcoxon vs 0, p<0.05).
- **H2**: subset `regime=BULL & excess>0 & prior_3y>=3` có median ABNORMAL_RETURN < 0 (tín hiệu
  tránh mua trước ex-date khi mania).
- **H3**: dose-response theo `excess` (0-4pp < 4-8pp < >8pp median AR, đơn điệu tăng) còn giữ
  TRONG gate.

## Tiêu chí FAIL (bất kỳ điều nào true ⇒ FAIL, không GO)
1. H1 rớt khi LOYO loại năm 2022 (median AR ≤ 0 hoặc mất ý nghĩa thống kê sau cluster-robust).
2. Cluster-robust (theo ticker) mất ý nghĩa thống kê so với 0.
3. KHÔNG tách được CASH khỏi STOCK_DIV cùng regime ở BẤT KỲ chiều nào (CRISIS hoặc BEAR riêng lẻ,
   MWU CASH>STOCK_DIV p≥0.05) — ghi nhận trước: phía dương hiện đã YẾU (p≈0.17-0.43 theo số Mike),
   đây là điểm yếu đã biết, không phải phát hiện mới.
4. Ticker hoặc sector concentration trong gate vượt ngưỡng bất thường (>15% N từ 1 ticker, hoặc
   >40% N từ 1 ngành) khiến kết luận thực chất là single-name/sector effect.
5. AR window thay thế [-10,-1] hoặc [-20,-1] đảo DẤU median trong gate (không cần giữ nguyên độ
   lớn, chỉ cần không đổi dấu và giữ ý nghĩa thống kê ở mức lỏng p<0.10).

## KHÔNG được làm sau khi thấy outcome
- Không đổi ngưỡng excess>0, prior_3y>=3, c14>=10000, raw_yield<=0.50.
- Không đổi regime gate CRISIS/BEAR sang tổ hợp khác để "cứu" kết luận.
- Không thêm bộ lọc mới hậu-hoc để loại bỏ observation gây FAIL.

## Trạng thái
Prereg khoá lúc bắt đầu chạy `reproduce_gate.py` — commit cùng lượt với báo cáo kết quả.
