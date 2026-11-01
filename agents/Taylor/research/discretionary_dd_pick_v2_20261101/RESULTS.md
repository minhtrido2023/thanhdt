# Funnel 8L v2 — kết quả dựng + thử mô tả (job Taylor_20261101_130719)

PREREG: `PREREG.md` (md5 12d35014cec24767904c23dfea0a2ce5, commit cf37e8fa7 — commit TRƯỚC lần chạy đầu; file gốc, KHÔNG sửa). Bổ sung vòng 2: `PREREG_ADDENDUM_vong2.md`.

## 1. Chạy sandbox trên dữ liệu thật (asof 30/10, `--out-dir /tmp/pick_sbx`, KHÔNG ghi data/)
- Pool sau loại trừ: **120 mã**; loại 26 (gồm đang giữ / DD < 90 ngày: DDV DGC DRI FPT HPG HT1 MBB MCH NNC NT2 PVP PVT SAS SCL SIP SZL TPB TV1 TV2 VIB VPB).
- Top-8: QTP 0,885 · PAN 0,757 · FMC 0,711 · AAA 0,711 · PGC 0,678 · TCB 0,673 (dcf_na) · HGM 0,661 · DCM 0,661 (dcf_na).
  ⇒ đề xuất **QTP** (MoS DCF +82%, rating 2, BCTC 21/10 YoY +129%), lên tầng đầy đủ nếu tầng nhẹ sạch.
- Thời gian toàn funnel + bộ chọn (python3 hệ thống, như cron): **12 s** (trần cron 120 s).
- Lỗi bắt được khi chạy thật: HPG DD ngày 31/10 vẫn lọt top vì cooldown cắt tại asof 30/10 ⇒ sửa: cận trên = ngày CHẠY (có test).

## 2. Thử mô tả 3 biến thể trên PIT tháng 2016-01→2026-07 (`quick_pit_variants.py`, $DNA_PYEXE, threads=1)
Pool PIT KHÁC production (bỏ thanh khoản/redflag/BANNED/forensic/đang giữ/cooldown/DCF-NA) — chỉ mô tả.
Forward = Close đ/c 63 phiên. 126 tháng, 13.400 dòng. Thước đo = (top-1 − trung vị rank 2-8) fwd 3M, trung vị theo
mẫu không chồng 3M, CI95 bootstrap trung vị (2000 lần, seed 0).

**⚠️ Đính chính (vòng 3): mẫu "theo quý" 1/4/7/10 KHÔNG kiểm được thành phần E.** Ngày giao dịch đầu các tháng 1/4/7/10
rơi TRƯỚC mùa BCTC ⇒ tỉ lệ mã có BCTC "tươi" (≤45 ngày) chỉ **0,3%** (4.575 dòng) ⇒ E≡0 ⇒ điểm prereg ≈ 0,5V+0,2R.
Headline "+1,35pp [−2,80; +3,32]" ở bản trước đến từ chính mẫu này nên KHÔNG nói gì về E. Báo cả 3 pha:

| Pha (tháng asof) | N | BCTC tươi | Biến thể | trung vị (top-1 − rank 2-8) | hit | CI95 |
|---|---|---|---|---|---|---|
| 1/4/7/10 (E≡0) | 43 | 0,3% | prereg | +1,35pp | 0,51 | [−2,80; +3,32] |
| | | | V_only | −4,40pp | 0,42 | [−8,54; +2,28] |
| | | | E_heavy | −0,34pp | 0,47 | [−3,97; +2,79] |
| **2/5/8/11 (E hoạt động)** | 41 | 97,2% | **prereg** | **−4,30pp** | 0,37 | **[−14,95; +0,07]** |
| | | | **V_only** | **−5,85pp** | 0,32 | **[−8,99; −0,25]** |
| | | | E_heavy | −1,36pp | 0,49 | [−5,77; +4,73] |
| 3/6/9/12 (E hoạt động) | 42 | 92,5% | prereg | −2,19pp | 0,40 | [−4,48; +0,61] |
| | | | V_only | −3,92pp | 0,43 | [−8,22; +5,13] |
| | | | **E_heavy** | **−3,24pp** | 0,31 | **[−6,30; −1,12]** |

Tái tính (job Taylor_20261101_135046): `phase_recompute.py` (đọc CSV, `/home/trido/thanhdt/wc_venv/bin/python -I phase_recompute.py`)
→ `phase_recompute_out.txt` (md5 0067444201a2da9fb7907798572931a8). Đầu vào: `quick_pit_variants_out.csv` md5 157b260c06485172051d8dd23f80728e,
`quick_pit_panel.csv` md5 d057da3dbb3d8bac193c7529f1c0ced2. Khớp các số điều phối đưa ra, lệch làm tròn duy nhất: CI prereg pha 3/6/9/12
cận dưới −4,48 (đưa −4,47), E_heavy cận trên −6,30 (đưa −6,31). Bảng gộp tháng cũ (126 tháng): `quick_pit_variants_summary.txt`.

**Đọc (trung thực)**: ở các pha E hoạt động, **cả 3 biến thể đều có trung vị ÂM** (−1,4 … −5,9pp), 2 trong 9 ô có CI95 hoàn toàn < 0
(V_only 2/5/8/11; E_heavy 3/6/9/12), prereg sát biên (+0,07). Không ô nào dương có nghĩa. Mỗi pha chỉ N≈41-43 và 9 ô × 3 CI
chưa hiệu chỉnh đa so sánh ⇒ KHÔNG phải bằng chứng chắc rằng bộ chọn có hại, nhưng chắc chắn không có bằng chứng nó có edge.
**Kết luận: top-1 theo điểm có xu hướng KÉM hơn rank 2-8; bộ chọn chỉ để xếp việc DD, không phải tín hiệu.** Phù hợp
kết luận cũ "composite/value làm entry-selector = NO" và "IC MoS phẳng". Không re-tune (PREREG khoá).
Ngưỡng tầng đầy đủ MoS≥25%: trung vị **44%** pool PIT vượt (hôm nay 6/8 top) ⇒ ngưỡng gần như không lọc; ràng buộc thật là
trần suất + phán quyết tầng nhẹ. Nêu cho user, không tự đổi.

## 3. Hướng R&D đề xuất (không chạy lớn)
**Câu hỏi**: tiêu chí nào trong (V, E, R) giúp DD chọn mã tốt hơn — đo trên ĐÚNG quyết định thật, không trên screen.
- Dữ liệu PIT có thật: `fa_ratings_8l` 2014-07→2026-06 (48 quý, 1.281 mã; republish ⇒ dùng pin tháng `tav2_pin.fa_ratings_8l_pin_YYYYMM` cho vintage), `ticker_financial` (time=ngày công bố), `universe_pit` ruleset 1, cache giá; **`data/rating_8l_daily/` chỉ 20 phiên (05/10→30/10)** ⇒ pb_z/value_score PIT chưa đủ dài; `dcf_lens_history.csv` trộn 2 khung (cắt mốc 30/10 12:48).
- **Thiết kế**: (a) nhật ký chọn `data/discretionary_pick_log.csv` từ 02/11 là mẫu forward sạch duy nhất không bị panel-curation (top-8 ghi TRƯỚC, kể cả mã bỏ). (b) Lịch sử: tái dựng pool PIT tháng như §2 nhưng đủ lọc production (liq từ Trading_Value PIT, BANNED/forensic theo ngày cờ) — panel 2016+ để tránh thị trường mỏng.
- **Pre-registration cho (b)** (chưa khoá — khoá khi chạy): 1 thước đo duy nhất = trung vị (top-1 − trung vị rank 2-8) fwd 3M **trên pha có E hoạt động** (tháng 2/5/8/11 và 3/6/9/12, mỗi pha N≈41-42; KHÔNG dùng mẫu 1/4/7/10 vì E≡0); N = 41-42 mỗi pha; luật: CI95 khối-quý loại 0 mới gọi là có tín hiệu; so 3 biến thể ĐÃ GHI ở §2, không thêm biến thể sau khi nhìn; Bonferroni ×3 biến thể ×2 pha = ×6.
- **Tránh look-ahead**: rating as-of rt_time; tài chính time ≤ asof; giá vào Price phiên ≤ asof; KHÔNG dùng `profit_*`; universe_pit thay ticker_prune; DCF fin-path (số CP live cần lịch sự kiện PIT — chưa có cho lịch sử).
- **Power**: 43 quý, sd chênh lệch (prereg, mẫu 1/4/7/10, N=43) đo được **15,4pp** (bản trước; chưa đo lại cho pha 2/5/8/11) ⇒ hiệu ứng nhỏ nhất phát hiện với power 80% ≈ 2,8·sd/√N ≈ **6,6pp/quý** (xấp xỉ chuẩn, two-sided 5%; ước lượng). Edge thực tế của một bộ chọn hiếm khi lớn vậy ⇒ lịch sử chỉ đủ loại bỏ biến thể TỆ rõ rệt, không đủ xác nhận biến thể tốt. Forward pick log (mốc 2027-04-06, N ước lượng 40-60 pick) càng kém power hơn ⇒ chỉ mô tả + futility như PREREG §6.
