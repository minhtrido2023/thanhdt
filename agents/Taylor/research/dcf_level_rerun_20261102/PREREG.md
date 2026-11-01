# PREREG — dcf_level_rerun_20261102 (job Taylor_20261101_175734) — viết TRƯỚC khi chạy số
R&D thuần. Không sửa `dcf_valuation.py`, không wire. Mặc định production GIỮ `domestic_v2` (g_T cap 5,5%, s=0,5).
Tái dùng: `../dcf_vn_calibration_20261101/{engine.py,common.py,data/row_inputs.parquet,data/panel_monthly.parquet}`.

## Định nghĩa cố định
- Panel: `panel_monthly` (universe_pit, cuối tháng 2013-12 → 2026-10-30, không dùng `profit_*`), lọc `base_valid` + Price>0.
- FV(g_T, s): đúng `variants.fv` (g_T hiệu dụng = min(g_T_thô CPI5Y+GDP15Y, cap lưới); guard Gordon; N=5; r hằng 12,25%).
- Metric mức: median log(Price/FV) theo tháng → TB theo năm → TB các năm. g_T* = ô lưới làm |metric| nhỏ nhất.
  IS = năm ≤2019, OOS = ≥2020, LOYO = bỏ lần lượt từng năm (min–max g_T*). Lưới 3,00–8,00%, bước 0,25 (21 ô).
- Cấu trúc: s=0 (chính) và s=0,5 (đối chứng). Số trials ghi rõ: 2 cấu trúc × 21 ô × {fin, live} × {tất cả, ổn định, nhảy, post-step-excluded}.
- **Hội tụ** (định trước): g_T* được coi là "đáng tin" CHỈ NẾU phân cách giữa nhóm (a) ổn định và (b) nhảy trên đường LIVE ≤ 1,0pp
  VÀ LOYO min–max ≤ 1,0pp. Ngược lại KẾT LUẬN: "không có g_T duy nhất đáng tin, giữ domestic_v2 (5,5%)".
  Phân cách (b)−(a) = độ bất định THẬT của g_T. Không ép ra một con số.

## Việc 1 — đường live
OShares live(t, mã) = `oshares_pit.oshares_pit` (chính sách production: oshares_live PIT, rơi về số quý ở mọi ca từ chối,
cổng ×3) + luật R10 (live < quý×(1−0,005) ⇒ số quý), dùng cache MỘT lần BQ (`oshares_live._fetch`) cho mọi mã/ngày.
**Phạm vi KHÔNG tái lập được lịch sử**: khoá khung ex-date R5/R8/R9 (a–d: `price_date`, `unexecuted_events`, `_price_run_start`) —
cần trạng thái `event_status` tại thời điểm asof (BQ chỉ giữ trạng thái hôm nay). Hệ quả: tập "live" ở đây là CẬN "live thuần"
(những ca production rơi về số quý vì khoá khung không có hiệu lực ở đây). Ghi rõ trong REPORT.
FV live = FV tính lại với OShares live; base FCFE giữ nguyên. Tác động 30/10/2026: gọi thẳng `dcf_valuation.fair_value`
(OSHARES_SOURCE=live, `osd.prime`) cho 147 mã, so với engine live-ghép → SELFCHECK 0 VND (nếu BQ cho phép).

## Việc 2 — nhóm
Cờ ổn định = đúng `robust.py` (max/min OShares quý trong ±4 quý, tâm, >1,10 ⇒ nhảy). CẢNH BÁO: cờ dùng quý TƯƠNG LAI ⇒ chỉ để
CHẨN ĐOÁN thiên lệch, không phải bộ lọc dùng được live. (c) = loại dòng tháng nằm trong 3 tháng ngay sau bước OShares quý >10%
(PIT: chỉ dùng quá khứ). Báo n dòng + n tháng mỗi nhóm.

## Việc 3 — pha loãng vs restatement
Chọn 10 sự kiện: bước OShares quý >10% có |ΔlogP/FV| lớn nhất, 2 mã/ nhóm cap; tra `corporate_action` (BQ) ISS/AIS quanh ngày.
Phân loại: pha loãng = có ISS/AIS executed giải thích ≥ 80% bước (cp phát hành mới, base FCFE trailing /số cp hiện tại);
restatement = không có sự kiện / số quý đảo chiều. Ghi mã, ngày, số cp trước/sau, nguồn.

## Việc 4 — bootstrap
Chênh MAE K=5 (s=0 vs s=0,5) từ `growth.py` (panel tăng trưởng thực tế). Bootstrap khối THEO NĂM (nguồn gốc của cặp (ticker,năm)), 5000 lần,
CI 95% cho Δ = MAE(s0) − MAE(s0,5). Nếu CI chứa 0 ⇒ không phân biệt được.

## Việc 5
Nếu g_T* hội tụ (điều kiện trên) và s=0 còn ủng hộ: đề xuất nhãn "FCFE yield so với trung vị thị trường". Nếu không hội tụ: kết luận
rõ "không có g_T duy nhất đáng tin". Báo cả những gì KHÔNG chứng minh được.
