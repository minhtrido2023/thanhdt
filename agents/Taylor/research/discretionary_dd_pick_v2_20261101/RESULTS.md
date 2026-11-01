# Funnel 8L v2 — kết quả dựng + thử mô tả (job Taylor_20261101_130719)

PREREG: `PREREG.md` (md5 12d35014cec24767904c23dfea0a2ce5, commit cf37e8fa7 — commit TRƯỚC lần chạy đầu).

## 1. Chạy sandbox trên dữ liệu thật (asof 30/10, `--out-dir /tmp/pick_sbx`, KHÔNG ghi data/)
- Pool sau loại trừ: **120 mã**; loại 26 (gồm đang giữ / DD < 90 ngày: DDV DGC DRI FPT HPG HT1 MBB MCH NNC NT2 PVP PVT SAS SCL SIP SZL TPB TV1 TV2 VIB VPB).
- Top-8: QTP 0,885 · PAN 0,757 · FMC 0,711 · AAA 0,711 · PGC 0,678 · TCB 0,673 (dcf_na) · HGM 0,661 · DCM 0,661 (dcf_na).
  ⇒ đề xuất **QTP** (MoS DCF +82%, rating 2, BCTC 21/10 YoY +129%), lên tầng đầy đủ nếu tầng nhẹ sạch.
- Thời gian toàn funnel + bộ chọn (python3 hệ thống, như cron): **12 s** (trần cron 120 s).
- Lỗi bắt được khi chạy thật: HPG DD ngày 31/10 vẫn lọt top vì cooldown cắt tại asof 30/10 ⇒ sửa: cận trên = ngày CHẠY (có test).

## 2. Thử mô tả 3 biến thể trên PIT tháng 2016-01→2026-07 (`quick_pit_variants.py`, $DNA_PYEXE, threads=1)
Pool PIT KHÁC production (bỏ thanh khoản/redflag/BANNED/forensic/đang giữ/cooldown/DCF-NA) — chỉ mô tả.
Forward = Close đ/c 63 phiên. 126 tháng, 13.400 dòng; N độc lập ≈ **43 quý** (mẫu tháng 1/4/7/10, không chồng 3M).

| Biến thể | top-1 − trung vị rank 2-8 (tháng, trung vị / hit) | theo quý, trung vị [CI95 bootstrap] |
|---|---|---|
| prereg (0,5V+0,3E+0,2R) | −2,25pp / 0,43 | +1,35pp [−2,80; +3,32] |
| V_only (MoS DCF) | −4,29pp / 0,39 | −4,40pp [−8,54; +2,28] |
| E_heavy (0,3V+0,5E+0,2R) | −1,70pp / 0,42 | −0,34pp [−3,97; +2,79] |

Nguồn: `quick_pit_variants_summary.txt`, `quick_pit_variants_out.csv` (md5 157b260c…), panel `quick_pit_panel.csv` (md5 d057da3d…).

**Đọc**: không biến thể nào có edge; CI chứa 0 cả 3. Chọn đúng mã MoS cao nhất (V_only) còn có xu hướng KÉM
các mã kế cận — đúng với kết luận cũ "composite/value làm entry-selector = NO" và "IC MoS phẳng". ⇒ Bộ chọn là
công cụ **xếp việc cho DD** (ai đáng tốn tiền đọc trước), KHÔNG phải tín hiệu; giá trị (nếu có) phải đến từ DD.
Không re-tune (PREREG khoá). Ngưỡng tầng đầy đủ MoS≥25%: trung vị **44%** pool PIT vượt (hôm nay 6/8 top) ⇒
ngưỡng gần như không lọc; ràng buộc thật là trần suất + phán quyết tầng nhẹ. Nêu cho user, không tự đổi.

## 3. Hướng R&D đề xuất (không chạy lớn)
**Câu hỏi**: tiêu chí nào trong (V, E, R) giúp DD chọn mã tốt hơn — đo trên ĐÚNG quyết định thật, không trên screen.
- Dữ liệu PIT có thật: `fa_ratings_8l` 2014-07→2026-06 (48 quý, 1.281 mã; republish ⇒ dùng pin tháng `tav2_pin.fa_ratings_8l_pin_YYYYMM` cho vintage), `ticker_financial` (time=ngày công bố), `universe_pit` ruleset 1, cache giá; **`data/rating_8l_daily/` chỉ 20 phiên (05/10→30/10)** ⇒ pb_z/value_score PIT chưa đủ dài; `dcf_lens_history.csv` trộn 2 khung (cắt mốc 30/10 12:48).
- **Thiết kế**: (a) nhật ký chọn `data/discretionary_pick_log.csv` từ 02/11 là mẫu forward sạch duy nhất không bị panel-curation (top-8 ghi TRƯỚC, kể cả mã bỏ). (b) Lịch sử: tái dựng pool PIT tháng như §2 nhưng đủ lọc production (liq từ Trading_Value PIT, BANNED/forensic theo ngày cờ) — panel 2016+ để tránh thị trường mỏng.
- **Pre-registration cho (b)**: 1 thước đo duy nhất = trung vị theo quý (top-1 − trung vị rank 2-8) fwd 3M; N = 43 quý; luật: CI95 khối-quý loại 0 mới gọi là có tín hiệu; so 3 biến thể ĐÃ GHI ở §2, không thêm biến thể sau khi nhìn; Bonferroni ×3.
- **Tránh look-ahead**: rating as-of rt_time; tài chính time ≤ asof; giá vào Price phiên ≤ asof; KHÔNG dùng `profit_*`; universe_pit thay ticker_prune; DCF fin-path (số CP live cần lịch sự kiện PIT — chưa có cho lịch sử).
- **Power**: 43 quý, sd chênh lệch (prereg, theo quý) đo được **15,4pp** ⇒ hiệu ứng nhỏ nhất phát hiện với power 80% ≈ 2,8·sd/√N ≈ **6,6pp/quý** (xấp xỉ chuẩn, two-sided 5%). Edge thực tế của một bộ chọn hiếm khi lớn vậy ⇒ lịch sử chỉ đủ loại bỏ biến thể TỆ rõ rệt, không đủ xác nhận biến thể tốt. Forward pick log (mốc 2027-04-06, N ước lượng 40-60 pick) càng kém power hơn ⇒ chỉ mô tả + futility như PREREG §6.
