# DIVERGE indicator ở cấp CHIẾN LƯỢC — ROUND 2, sửa 4 điểm quant-skeptic REFUTED

Job `Taylor_20260830_135407`. User duyệt (2026-08-30 20:53 ICT, decided_by user) làm lại hướng
CAP_SIGNAL composite sau khi quant-skeptic REFUTED medium round1 (job
`quant-skeptic_20260830_132949`). File này SỬA ĐÚNG 4 điểm bị REFUTED trên nền round1
(`diverge_indicator_strategy_backtest_20260830.md`, giữ nguyên không sửa, làm lịch sử) — không đổi
ý tưởng gốc, không wire, không sửa `macro_state_live.py`/`custom_basket.py`/production.

## Tóm tắt 4 điểm sửa

| # | Quant-skeptic REFUTED | Round2 xử lý |
|---|---|---|
| 1 | Grid CAP_SIGNAL (N∈{10,20}×H∈{30,50,70%}) không có script/CSV persist trong repo | Script mới `exp_insider/cap_signal_grid_test_round2.py` (persisted), output `exp_insider/cap_signal_impact_grid_round2.csv` — cùng phương pháp full-path compounding với script DIVERGE-only đã có sẵn |
| 2 | Nhãn false-positive sai: report cũ gán 2016-11/2016-12 là FP, thực ra là TP | Đối chiếu lại per-episode CSV, sửa đúng: FP thật = 2014-10-09, 2023-08-16 |
| 3 | Bảng CAP_SIGNAL thiếu split IS(2014-19)/OOS(2020+) | Thêm 2 cột vào grid mới (§1) |
| 4 | 94% hiệu ứng dồn vào 3/8 episode, nghi giả-độc-lập cặp 2023-08/2023-09 (~5 tuần) | Leave-one-episode-out tại N=20,H=50% (điểm chẩn đoán gốc) + N=10,H=30% (cross-check) — §3 |

## 1. Grid CAP_SIGNAL persisted — điểm 1 + điểm 3

**Script**: `exp_insider/cap_signal_grid_test_round2.py`. **Self-check 0 VND** (giống hệt round1):
reconstruct `combined_nav` từ `ret=pct_change` rồi cumprod, lệch tối đa **0,00293 VND** trên NAV
~50-1.238 tỷ. 8 episode composite tái lập đúng (`cap_signal_episodes_recheck.csv`, khớp round1
từng ngày fire). Baseline (không cap): CAGR 18,79%, final NAV 1.237,6 tỷ, 18,63 năm.

| N | H | Δ CAGR (pp) | Final NAV (B) | IS 2014-19 (pp) | OOS 2020-nay (pp) |
|---|---|---|---|---|---|
| 10 | 30% | +0,26 | 1.289,5 | +7,4 | +13,9 |
| 10 | 50% | +0,43 | 1.324,7 | +12,3 | +23,1 |
| 10 | 70% | +0,60 | 1.360,3 | +17,2 | +32,3 |
| 20 | 30% | +0,40 | 1.317,8 | +9,1 | +24,5 |
| 20 | 50% | +0,66 | 1.372,9 | +15,1 | +41,1 |
| 20 | 70% | +0,92 | 1.429,2 | +21,0 | +57,8 |

Δ CAGR khớp round1 (làm tròn: +0,26/+0,44/+0,60/+0,40/+0,66/+0,92 → +0,26/+0,43/+0,60/+0,40/
+0,66/+0,92 — sai số làm tròn <0,01pp), xác nhận round1 tính đúng dù không lưu script.
**Mới**: cả 6/6 biến thể **IS và OOS đều dương**, đơn điệu theo N/H — không đảo chiều giữa 2 giai
đoạn walk-forward (khác DIVERGE-only, nơi cả IS lẫn OOS đều âm). OOS thực ra lớn hơn IS ở mọi ô
(vd N=20,H=50: OOS +41,1pp > IS +15,1pp) — phần lớn giá trị composite đến từ episode 2018 trở đi
(3 trong 6 episode true-positive nằm ở OOS: 2022-08-30, 2023-09-21, 2024-12-17).

## 2. Sửa nhãn false-positive §3 round1 — điểm 2

Round1 viết: *"chỉ 2/8 (2016-11, 2016-12, cả hai đều nhỏ) cắt oan (−3,41pp gộp)"* — **SAI episode**,
dù tổng −3,41pp là ĐÚNG số (chỉ gán nhầm ngày). Đối chiếu lại `cap_signal_per_episode_impact.csv`
(N=20,H=50%, baseline_ret = lợi nhuận V2.4 tự nó trong đúng cửa sổ N phiên sau fire):

| fire_date | baseline_ret (%) | impact (pp) | Phân loại ĐÚNG |
|---|---|---|---|
| 2014-10-09 | +2,60 | **−1,27** | **FALSE-POSITIVE** (V2.4 đang lãi, cap cắt oan) |
| 2016-11-14 | −0,16 | +0,08 | true-positive (nhỏ) |
| 2016-12-19 | −0,53 | +0,27 | true-positive (nhỏ) |
| 2018-10-04 | −8,47 | +4,19 | true-positive (lớn) |
| 2022-08-30 | −6,32 | +3,13 | true-positive (lớn) |
| **2023-08-16** | **+4,37** | **−2,14** | **FALSE-POSITIVE** (V2.4 đang lãi, cap cắt oan) |
| 2023-09-21 | −9,63 | +4,73 | true-positive (lớn) |
| 2024-12-17 | −0,93 | +0,47 | true-positive (nhỏ) |

**FP thật = 2014-10-09 + 2023-08-16, sum −3,41pp** (khớp đúng con số round1 đã in, chỉ sai tên
episode gán vào). **TP = 6 episode còn lại, sum +12,87pp** (số này round1 cũng đã đúng). Không đổi
kết luận hướng (CAP_SIGNAL vẫn ròng dương +9,46pp additive, chưa compound) — chỉ sửa quy kết
episode nào là FP/TP cho đúng, tránh trích dẫn sai nếu ai đọc lại report cũ.

## 3. Leave-one-episode-out — điểm 4

Chạy tại **N=20,H=50%** (điểm chẩn đoán per-episode gốc) và **N=10,H=30%** (cross-check biến thể
grid khác), full-path compounding thật (không phải additive per-episode). File:
`exp_insider/cap_signal_leave_one_out_round2.csv`.

**N=20, H=50% (full 8-episode Δ CAGR = +0,663pp)**

| Loại bỏ | Δ CAGR (pp) | % còn lại so full |
|---|---|---|
| (không loại — full) | +0,663 | 100% |
| 2014-10-09 (FP) | +0,743 | 112% (loại FP → tăng, đúng hướng) |
| 2016-11-14 | +0,658 | 99% |
| 2016-12-19 | +0,646 | 97% |
| **2018-10-04** | **+0,376** | **57%** |
| 2022-08-30 | +0,453 | 68% |
| 2023-08-16 (FP) | +0,796 | 120% (loại FP → tăng) |
| **2023-09-21** | **+0,337** | **51%** |
| 2024-12-17 | +0,633 | 95% |
| **Cặp 2023-08-16 + 2023-09-21 cùng lúc** | **+0,469** | **71%** |

**N=10, H=30% (full 8-episode Δ CAGR = +0,263pp)** — cross-check: cùng pattern, loại 2023-09-21
xuống thấp nhất (+0,122pp, 46%), loại 2018-10-04 xuống +0,191pp (73%), loại cặp 2023-08+09 → giống
hệt loại riêng 2023-09-21 (+0,122pp) vì ở N ngắn 2023-08-16 gần như không đóng góp (0,2627 vs
0,2625 khi có/không có nó — cap FP quá ngắn để cắt được nhiều ở N=10).

**Kết luận robustness**: dấu **KHÔNG đảo** ở BẤT KỲ phép loại-trừ nào (đơn hoặc cặp), ở CẢ 2 điểm
grid test — 18/18 phép loại-trừ vẫn dương (sau khi bổ sung 1 cặp theo yêu cầu quant-skeptic verify
round2, xem dưới). Nhưng biên độ nhạy thật: loại riêng 2018-10-04 hoặc 2023-09-21 (2 trong 3
episode lớn nhất) làm Δ CAGR co lại còn ~46-57% giá trị gốc — xác nhận định tính claim của
quant-skeptic ("hiệu ứng dồn vào ít episode") đúng hướng.

**Sửa số "94%"** (quant-skeptic round2-verify chỉ ra công thức đối chiếu round2 ban đầu dùng sai
mẫu số): top-3-TP (4,19+3,13+4,73=12,05pp) / **TP GỘP** (không trừ FP, =12,87pp) = **93,6% ≈ 94%**
— khớp gần đúng con số gốc. Round2 bản đầu dùng nhầm mẫu số ròng (TP+FP=9,46pp) nên tính ra 128%
và kết luận nhầm "không tái lập được" — SỬA LẠI: con số 94% của quant-skeptic round1 **tái lập
được**, chỉ khác công thức mẫu số.

**Nghi ngờ giả-độc-lập cặp 2023-08/2023-09 (~5 tuần)**: loại cả cặp cùng lúc (N→6 episode hiệu
lực) vẫn dương ở cả 2 grid point (71% và 46% giá trị gốc). **Kiểm tra đối xứng bổ sung** (quant-
skeptic round2-verify chỉ ra round2 bản đầu chỉ test cặp 2023 mà bỏ sót cặp 2016-11-14/2016-12-19
— cách nhau 35 ngày, cấu trúc giống hệt cặp 2023 cách 36 ngày): loại cặp 2016 gần như KHÔNG đổi
kết quả (N=20,H=50: 0,641/96,7%; N=10,H=30: 0,260/99,1%) — vì cả 2 episode 2016 đều nhỏ (+0,08 và
+0,27pp). Không phải 1 episode đơn lẻ đang gánh hết kết luận, nhưng N=6-7 hiệu lực (sau khi coi
CẢ 2 cặp gần nhau là 1 cụm mỗi cặp — tổng chỉ còn **6 cụm macro độc lập thật** trong 15 năm: 2014,
2016, 2018, 2022, 2023, 2024) là RẤT mỏng cho một kết luận "6/6 biến thể grid dương" — cùng lớp
rủi ro N nhỏ đã gặp ở hướng insider-cluster-buy cùng ngày (REFUTED do N thổi phồng/giả-độc-lập).

## 4. Kết luận cho user — trung thực, không giữ kết luận cũ nếu không sống sót

**CAP_SIGNAL composite VẪN dương sau khi sửa cả 4 điểm và qua leave-one-out** (16/16 phép loại-trừ
không đảo dấu, IS/OOS đều dương ở cả 6 biến thể grid) — kết quả round2 đáng tin hơn round1 vì:
(a) grid giờ có script+CSV persist tái lập được, (b) nhãn FP/TP đã đúng, (c) IS/OOS không còn
thiếu, (d) đã test robustness episode-level thay vì chỉ nhìn tổng.

**Nhưng KHÔNG phải GO thẳng** — 3 lý do giữ nguyên mức thận trọng của round1, cộng 1 lý do mới từ
round2:
1. Biên độ Δ CAGR (+0,26 đến +0,92pp) **nhạy episode-level thật** — mất ~half giá trị nếu thiếu 1
   trong 2 episode lớn nhất tương lai không xảy ra đúng kiểu 2018-10-04/2023-09-21.
2. N hiệu lực sau khi coi cặp 2023-08/09 là 1 cụm chỉ còn **~6-7 episode độc lập thật** — quá mỏng
   để tách signal khỏi may mắn bằng phương pháp thống kê chính thức (DSR/PBO cần N lớn hơn nhiều).
3. Hạn chế phương pháp round1 vẫn còn nguyên: haircut tỷ lệ trên NAV thật là XẤP XỈ, không phải
   re-run cơ chế cap rời rạc qua engine V2.4 thật.
4. **Mới**: composite MISS early-warning 2018-03-22 (đã nêu round1) — giá trị dương đến từ lọc
   false-positive tốt hơn DIVERGE-only, KHÔNG phải từ bắt sớm khủng hoảng; nếu mục tiêu là early-
   warning thì CAP_SIGNAL không giải quyết được vấn đề gốc.

## 5. Quant-skeptic verify round2 — CONFIRMED (medium confidence)

Dispatch riêng, độc lập rerun script từ source data (không dựa vào CSV đã lưu), khớp từng số đến
full float precision. Xác nhận cả 4 điểm sửa đều THẬT (không phải chỉ báo cáo suông). 2 vấn đề MỚI
phát hiện, đã xử lý ngay trong file này:
1. **Mẫu số "94%" sai** — round2 bản đầu dùng nhầm mẫu số, đã sửa ở §3 (94% TÁI LẬP ĐƯỢC).
2. **Robustness sweep không đối xứng** — chỉ test cặp 2023-08/09, bỏ sót cặp 2016-11/12 cấu trúc
   giống hệt — đã bổ sung test + cập nhật §3 (kết luận không đổi, cặp 2016 impact quá nhỏ để ảnh
   hưởng).
3. **Lookahead T+0 nhỏ, không trọng yếu** (quant-skeptic tự test thêm, không phải điểm dispatch
   yêu cầu): `build_cap_mask` bắt đầu cap ngay ngày fire, dùng return CHÍNH ngày đó dù composite
   chỉ biết được sau EOD — vi phạm quy ước T+1. Quant-skeptic tự chạy biến thể lag T+1: hiệu ứng
   **tăng nhẹ** (0,6632→0,6662pp và 0,2625→0,3006pp ở 2 điểm test), tức lookahead KHÔNG phải
   nguồn tạo ra kết luận — nhưng nếu triển khai thật phải sửa thành T+1.
4. **Killer objection của quant-skeptic**: N thật chỉ ~6 cụm macro độc lập trong 15 năm (2014,
   2016, 2018, 2022, 2023, 2024) sau khi gộp cả 2 cặp gần nhau — không đủ cho DSR/PBO hình thức,
   và kết luận "không GO, chỉ advisory" của round2 là ĐÚNG với chính bằng chứng của nó.

**Kết luận cuối (đã qua 2 lớp kiểm chứng)**: CAP_SIGNAL composite là ghi nhận nghiên cứu trung
thực, dấu dương sống sót mọi robustness test đã chạy, nhưng KHÔNG đủ điều kiện wire — N=6 cụm độc
lập quá mỏng. **Đề xuất next step nếu tiếp tục**: sửa T+1 lag trước khi coi là "phiên bản chuẩn"
nếu triển khai thật; N=6 không tăng được (composite dựa trên toàn bộ lịch sử macro panel
2011-2026 sẵn có, hết dữ liệu để test thêm) → chỉ hợp lý làm tín hiệu bổ sung mềm (advisory,
không auto-cap) nếu user muốn giữ theo dõi, không phải ứng viên wire cứng.

## File liên quan

- Round1 (lịch sử, không sửa): `research/diverge_indicator_strategy_backtest_20260830.md`
- Script mới (persisted): `exp_insider/cap_signal_grid_test_round2.py`
- Output mới: `exp_insider/cap_signal_episodes_recheck.csv`,
  `exp_insider/cap_signal_impact_grid_round2.csv`, `exp_insider/cap_signal_leave_one_out_round2.csv`
  (18 hàng — 8 full-set/single-drop × 2 grid point + 2 pair-drop × 2 grid point)
- Per-episode CSV tái dùng từ round1 (không đổi số, chỉ sửa nhãn ở report): `exp_insider/cap_signal_per_episode_impact.csv`
