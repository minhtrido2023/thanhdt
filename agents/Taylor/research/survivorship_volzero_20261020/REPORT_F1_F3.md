# REPORT F1 / F2 / F3 — tách nguồn mức tăng V1D + trần tham gia nhân quả (EXPLORATORY)
Job Taylor_20261021_012028 (khuyến nghị skeptic `logs/verify_20261020_180301_118003.log`). PREREG: F1 070429b5, F2 1183f815,
F3 c59cf88c (commit 773705cc6, TRƯỚC khi tính). Bản sao engine `eng/` (knob `F1_N/F1_H`, `F2_DUMP/F2_WL`, `F3_MODE/F3_MULT`).
Không sửa pin/registry/pin_ledger/engine thật; **không đề xuất đổi luật**. Chân: p30_pin0 / p30_pin1M / p0_pin0 / p0_pin1M.
Nguồn: cache pin `data/bq_cache_asof20260729_postrestate/ticker` (registry `price-volume/ticker_ohlcv_tables.md`, CANONICAL lịch sử).

## Control + self-check
Control đầu `vz_ctlD_*` (kèm dump whitelist F2) và control cuối `vz_ctlZ_*`: md5 = 4707bcbe / bcd0469f / 537e349b / a6ba34d8 —
**8/8 byte-identical**. 44/44 run biến thể EXIT=0, `[selfcheck BAL/LAG] = 0 VND`; METRIC max err ≤ 0,0003 VND (`out_metrics_*.csv`).

## Bảng Δ (pp) — `out_f_summary.csv`
| Biến thể | ΔCAGR so pin theo chân | ΔCAGR so V1D | ΔSharpe | ΔMaxDD | ΔIS 14-19 | ΔOOS 20+ | sàn 0,46 |
|---|---|---|---|---|---|---|---|
| V1D (job trước) | +1,79 / +2,03 / +1,81 / +1,25 | 0 | −0,11…−0,06 | −2,58…+0,87 | −2,64…−2,39 | +4,86…+6,49 | 4/4 (+) |
| **F1** N5 H10 | +1,53 / +1,72 / +1,61 / +1,43 | −0,32…+0,18 | −0,12…−0,08 | −3,79…+0,33 | −2,70…−2,63 | +5,52…+6,12 | 4/4 (+) |
| F1 N5 H30 | +0,98 / +1,33 / +0,88 / +0,55 | −0,93…−0,70 | −0,19…−0,13 | −3,98…−0,31 | −3,94…−3,32 | +5,01…+6,43 | 4/4 (+) |
| F1 N20 H10 | +1,52 / +1,68 / +1,51 / +1,39 | −0,35…+0,14 | −0,12…−0,08 | −3,76…+0,16 | −2,77…−2,65 | +5,43…+6,12 | 4/4 (+) |
| F1 N20 H30 | +0,89 / +1,36 / +0,86 / +0,54 | −0,95…−0,68 | −0,19…−0,13 | −3,98…−0,29 | −3,97…−3,37 | +5,02…+6,39 | 4/4 (+) |
| **F2** V1D + whitelist pin | +0,61 / +0,49 / +0,63 / −0,28 | −1,54…−1,17 | −0,07…+0,02 | +0,78…+1,24 | −3,05…−2,59 | +2,44…+4,06 | 3/4 (+) sát sàn |
| F2+F1 N20H10 *(hậu kỳ, KHÔNG prereg)* | +0,46 / +0,42 / +0,50 / −0,28 | −1,61…−1,31 | −0,07…+0,01 | +0,57…+1,23 | −3,06…−2,74 | +2,43…+3,91 | 1/4 |
| F2+F1 N5H30 *(hậu kỳ, KHÔNG prereg)* | +0,13 / +0,21 / +0,33 / −0,71 | −1,96…−1,48 | −0,11…−0,02 | +0,62…+1,20 | −3,33…−3,13 | +1,75…+3,95 | 1/4 (−) |
| F2C whitelist, knob khác off | +0,00 (≤0,003) ×4 | | 0 | 0 | 0 | 0 | 0/4 |
| **F3L** trần 20%×F×m_Y chỉ LAG | +1,71 / +1,84 / +1,60 / +0,94 | −0,31…−0,08 | −0,16…−0,07 | −3,95…−0,88 | −2,17…−1,58 | +3,73…+5,33 | 4/4 (+) |
| F3B như F3L + BAL trần 20%×F | −0,59 / −0,10 / +0,12 / −0,71 | −2,37…−1,69 | −0,24…−0,19 | −5,82…−0,36 | −2,27…−1,90 | +0,79…+2,39 | 2/4 (−) |

## F1 — trần thời gian hoãn bán (`out_f1_adjust_*.csv`)
- Lô ép bán: LAG 29–31 (N5) / 23–25 (N20), BAL 1 (ZVF). Lô giữ >45 phiên: 0 (V1D: 6). **Lô kẹt cuối kỳ: 0 ở 16/16 run** ⇒ hạch toán
  (a) giá 0 và (b) chiết khấu H cho cùng CAGR như engine (không có gì để điều chỉnh).
- Chặn giá cũ của hoãn bán vô hạn lấy đi **0,2–0,95pp** của V1D; phụ thuộc H (H30: −0,68…−0,95), gần như không phụ thuộc N.
  CAGR vẫn > pin 4/4 chân (+0,54…+1,72), nhưng ΔIS ÂM mọi cấu hình (−2,6…−4,0), ΔOOS dương ⇒ không đồng nhất IS/OOS.

## F2 — tách tái phân bổ (`out_f2_decomp_*.csv`, PnL LAG book ref, tỷ)
- F2C tái lập pin (Δ ≤ 0,003pp; md5 khác pin do thứ tự danh sách pending) ⇒ cơ chế whitelist sạch.
- **Tái phân bổ = V1D − F2 = +1,17 / +1,54 / +1,18 / +1,53pp** — phần lớn (≈65–122%) mức tăng V1D là vốn chảy sang sự kiện LAG khác.
- Lô pin bị chặn trong F2: 284–296 / 1503–1553; PnL PIN của chúng **DƯƠNG +44,1 / +59,0 / +49,9 / +67,1** ⇒ tự việc chặn làm MẤT lãi.
- Phần dư +0,49…+0,63pp (3/4 chân) đến từ lô khớp được kiếm thêm ở OOS (+39…+64 tỷ; IS −0,8…−2,9). Thêm trần hoãn bán (hậu kỳ,
  không prereg) ⇒ +0,13…+0,50 ở 3 chân (≤ sàn 0,46 trừ 1 ô 0,50), chân p0_pin1M −0,28…−0,71. Nguyên nhân phần dư OOS (dịch ngày khớp
  trong cửa sổ 5 phiên / kích thước lệnh) **chưa phân rã được**.
- Theo quy tắc khai trước: F2 = "dương sát sàn" ở 3/4 chân; sau khi chặn thêm giá cũ thì phần còn lại không phân biệt được với nhiễu.
  ⇒ **Chặn ngày không giao dịch KHÔNG tự tạo lợi nhuận đáng tin**; mức tăng V1D là tái phân bổ + giá cũ hoãn bán.

## F3 — trần tham gia nhân quả theo phiên (`out_f3_accuracy*.csv`, `out_f3_particip.csv`)
- Dự báo F = trung vị dv 20 dòng trước (Volume=0 tính 0). m_Y (PIT, năm trước, từ lệnh pin p30_pin0) = 1,00 (2014), 1,31 (2015),
  1,02–1,11 (2016–2026): ngày sự kiện LAG chỉ có KL cao hơn dự báo ~2–11%.
- Độ chính xác trên lệnh mua LAG pin (n=3767 ngày Volume>0): dv thực < dự báo ở **45,2% (ADV3M pin) / 50,8% (V1E20) / 48,1% (F) /
  51,1% (F×m)**; median log(thực/dự báo) +0,070 / −0,016 / +0,042 / −0,039. Theo năm dao động 33–68% (2022: 66–68%). Dự báo trước
  phiên ≈ tung đồng xu quanh thực tế — **không dự báo nào ràng buộc được tham gia thực**.
- Sau khi áp trần F3L: giá trị mua LAG >20% khớp thực cùng ngày **45,2–48,0%** (pin 66,5–68,9% gồm 31% ngày Volume=0; V1D 41,8–44,4),
  >50%: 6,7–7,3%, >100% (không thể khớp): 1,3–1,4%. Ngày Volume=0: 0%.
- F3B: trần dự báo cho BAL làm book ref BAL giảm mạnh (229→124 / 322→194 / 182→131 / 288→177 tỷ) ⇒ ΔCAGR âm 3/4 chân.
- **Pin LAG có thực thi được ở NAV 50 tỷ không? KHÔNG KẾT LUẬN ĐƯỢC** (quy tắc PREREG_F3 §4): (ii) ΔCAGR(F3L−pin) ≥ −0,46 ở 4/4 chân
  ĐÚNG, nhưng (i) % vượt 20% thực ≤10% SAI (45–48%). Mọi trần nhân quả đã đo (ADV3M, V1E, F, F×m) đều để ~45% giá trị mua LAG vượt
  20% khớp thực; con số CAGR của pin ở 50 tỷ do đó chưa được chứng minh là thực thi được với tham gia ≤20%.

## Trả lời lỗ hổng skeptic
(a) Vốn giải phóng → sự kiện LAG khác: ĐÚNG, là phần lớn mức tăng V1D (1,2–1,5pp). (b) Hoãn bán vô hạn giữ giá cũ: đóng góp 0,2–0,95pp
tuỳ chiết khấu. Gỡ cả hai, phần còn lại ≈ sàn nhiễu, IS âm. Luận điểm "Volume=0 không phải nguồn lợi nhuận của pin" đứng được ở dạng yếu
hơn: lô Z có PnL dương (+44…+67 tỷ) nhưng nhỏ so với giá trị mua (V4: 31% giá trị / 9–11% PnL) — chặn chúng không cải thiện, cũng không
làm pin sụp.

## Giới hạn
Giá ép bán = giá cũ × (1−H) là giả định; F2F1 là hậu kỳ không prereg (2 đầu lưới F1, chọn trước khi xem kết quả F2F1); m_Y ước từ chính
tập pin; khớp lô F2↔pin theo (mã, ±5 phiên); không slippage/tác động giá; DSR/PBO không tính (exploratory, không đề xuất luật).
Script: `f3_forecast.py`, `f1_adjust.py`, `f2_decomp.py`, `f3_particip.py`, `f_summary.py`, `run_batch_012028*.sh`.
