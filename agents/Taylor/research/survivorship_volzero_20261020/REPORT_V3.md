# REPORT V3 — Cổng state cho LAG (bản sao engine, EXPLORATORY)
Job Taylor_20261020_122917 → tiếp tục Taylor_20261020_153324. PREREG_V3.md md5 6b8fbdc2 (c3a7b8ad5). Không sửa engine thật/pin/registry;
**không kết luận đổi luật**.

## Δ so pin (pp), 4 chân — out_metrics_V3A_V3B.csv
| Biến thể | ΔCAGR theo chân (p30_pin0 / p30_pin1M / p0_pin0 / p0_pin1M) | ΔSharpe | ΔMaxDD | ΔIS 14-19 | ΔOOS 20+ | Nhãn |
|---|---|---|---|---|---|---|
| V3A noentry_bear | +0,32 / +0,41 / +0,48 / +0,52 | +0,006…+0,018 | −0,91…+0,61 | +0,07…+0,30 | +0,56…+0,74 | vượt sàn ở 2/4 chân |
| V3B close_reopen | +0,38 / +0,45 / +0,52 / +0,46 | +0,014…+0,028 | −0,11…+0,03 | +0,10…+0,23 | +0,66…+0,80 | vượt sàn ở 2/4 chân |

Diễn giải theo PREREG §3 (mô tả, không phải edge): việc MỞ lô LAG trong BEAR đóng góp ròng ≈ **−0,32…−0,52pp CAGR** (−ΔV3A); phần GIỮ
các lô đó sau khi cap mở lại ≈ **−0,38…−0,52pp** (−ΔV3B). Hai số không cộng được. Cả hai gần sàn nhiễu 0,46 (cắt sàn 2/4).
Phần lớn Δ đến từ OOS (2020+), khớp việc lô BEAR dồn vào 2020/2022/2023; N giai đoạn BEAR nhỏ.

## Đếm
- `[V3]` lượt LAG chính (trừ lượt base): V3A huỷ 227–229 lệnh vào; V3B đóng 32 lô ở cả 4 chân (`V3_REOPEN`).
- `d_bear_lag.py` (v3_count/): lô LAG mở lúc BEAR — pin 107–110 / V3A **0** / V3B 107–113 (vẫn mở, đúng thiết kế); lô chạm phiên
  cap>0: pin 42–43, V3B 41–43 (1 phiên phơi nhiễm T+1 cơ học → còn đếm). Số lô tổng V3B tăng (vd 1503→1563) vì giải phóng slot/tiền sớm.
- Chưa đối chiếu: V3B đóng 32 lô ở lượt chính < 42–43 lô "chạm cap" theo d_bear_lag — khác định nghĩa (state==2 tại ngày vào vs
  w_lag_tgt==0; lô hết hạn trước phiên mở lại). Không ảnh hưởng nhãn.

## Self-check
Mọi run V3A/V3B: `[selfcheck BAL/LAG] ... = 0 VND` (2/2 dòng), METRIC max err 0 VND. Control cuối: REPORT tổng.

## Giới hạn
Như PREREG_V3 §5. Δ là mô tả 1 giai đoạn (BEAR dồn 2022), không phải bằng chứng đổi luật; không có DSR/PBO.
