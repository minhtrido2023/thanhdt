# DC state-gated (active CHỈ BULL/EXBULL) — backtest đầy đủ + DSR proxy + transition risk

Job `Taylor_20260830_162358` (dispatch Mike, user duyệt 2026-08-30 23:23 ICT, decided_by user).
Tiếp nối `dc_3book_factor_neutral_20260830.md` (job `Taylor_20260830_153823`, quant-skeptic
CONFIRMED medium) — mở rộng "phát hiện phụ" cuối file đó (overlay w_DC=0,20/0,33 chỉ BULL/EXBULL,
chưa qua DSR/PBO/quant-skeptic) thành 1 nghiên cứu đầy đủ theo khung `quant-research`. Đã đọc kỹ
file trước, không lặp lại: Việc 2 (factor-neutral, alpha thật ≥54-70%) và Việc 3 (capacity, không
phải rào cản) của job trước GIỮ NGUYÊN kết luận, không test lại ở đây.

RESEARCH ONLY — không đụng `custom_basket.py`/`signal_v11_sql.py`/`macro_state_live.py`/
`trading_rules.json`/`plan.py`/`executor.py`.

## Cách tài trợ vốn (quyết định, có giải thích)

`blend_ret = (1 − w_dc_t)·baseline_ret + w_dc_t·dc_ret`, với `w_dc_t = w_DC` khi
`state ∈ {BULL, EXBULL}` và `0` ở CRISIS/BEAR/NEUTRAL. Khi DC active, nó thay thế **một phần đều
của `combined_nav` production THẬT** (BAL+LAG+CAPIT đã hoàn chỉnh) — không tách riêng
`w_BAL`/`w_LAG`, không đụng custom30V parking. Lý do:
1. **Parking chỉ xảy ra ở NEUTRAL** (`PARK_STATES="3:0.7"`), DC gate chỉ active BULL/EXBULL →
   hai điều kiện không bao giờ overlap, "thay parking" vô nghĩa ở đây.
2. Thay riêng `w_BAL`/`w_LAG` đòi hỏi vi lại toàn bộ allocator state-conditional bên trong
   `pt_v23_audit_2014.py` — rủi ro cao, không đủ để verify kỹ trong 1 job (đúng cảnh báo Q3 file
   08-25, đã né ở job trước).
3. Overlay tuyến tính ở mức return trên `combined_nav` là **ít xáo trộn nhất**: `w_DC=0` trả về
   đúng baseline; không đụng logic allocator bên trong. Đây đúng là cách "phát hiện phụ" 08-30 đã
   làm, job này mở rộng thành: grid 4 mức `w_DC` (0,15/0,20/0,25/0,33), transition cost, IS/OOS
   riêng, per-episode consistency, bootstrap theo EPISODE (không phải theo ngày).

## Dữ liệu (thật, không tự tạo)

- `baseline_ret` = `combined_nav` (CSV audit fresh EXP_TAG, cùng nguồn job trước).
- `dc_ret` = cột `ConvergePort (equal-weight)` (`converge_portfolio_backtest_nav.csv`, đã T+1 +
  TC 0,1% + tự park cash dư).
- `state` = cột `state` cùng CSV (1..5, đã qua pipeline DT5G thật — không tự vẽ lại
  smoothing/hysteresis, dùng đúng cam kết bất đối xứng 10/25 phiên built-in trong chính cột này).
- Calendar giao nhau: 2014-08-05 → 2026-06-26 (2.970 phiên).

Script: `exp_insider/dc_state_gated_bull_only.py` → `dc_state_gated_bull_only_metrics.csv` +
`dc_state_gated_bull_only_episodes.csv`.

## N độc lập thật: 10 episode, không phải 482 ngày

DC-active = 482/2.970 ngày (16,2%), nhưng đó là **10 chuỗi liên tục** (episode), không phải 482
sự kiện độc lập — ngày trong cùng 1 episode tương quan cao (state không đổi trong episode). Toàn
bộ DSR/bootstrap dưới đây dùng N=10, đúng tinh thần §18 (N = independent events, không phải row
count):

| # | Giai đoạn | State | Số ngày calendar |
|---|---|---|---:|
| 1 | 2017-12-26 → 2018-02-26 | BULL | 62 |
| 2 | 2018-03-22 → 2018-05-08 | BULL | 47 |
| 3 | 2020-10-06 → 2021-02-18 | EXBULL | 135 |
| 4 | 2021-03-05 → 2021-07-23 | BULL | 140 |
| 5 | 2021-08-23 → 2021-09-09 | BULL | 17 |
| 6 | 2021-10-26 → 2021-12-24 | BULL | 59 |
| 7 | 2024-01-24 → 2024-05-13 | BULL | 110 |
| 8 | 2025-03-07 → 2025-05-16 | BULL | 70 |
| 9 | 2025-08-12 → 2025-10-03 | EXBULL | 52 |
| 10 | 2026-01-28 → 2026-02-12 | BULL | 15 |

⚠️ **Chỉ 2/10 episode nằm trong IS (2017-2019)**, 8/10 nằm trong OOS (2020+) — walk-forward
IS/OOS ở đây gần như KHÔNG mang ý nghĩa "train rồi test độc lập" thông thường vì IS gần như không
có công suất thống kê (2 episode, +3,42pp và −2,50pp, gần như triệt tiêu nhau). Phần lớn bằng
chứng của kết luận này đến từ giai đoạn **sau** 2020 — cần nêu rõ, không phải một walk-forward cân
bằng.

## Kết quả backtest — grid `w_DC` (net-of-transition-cost)

| w_DC | n_transitions | ΔCAGR FULL | ΔSharpe FULL | ΔMaxDD FULL | ΔCalmar FULL | ΔCAGR OOS | ΔSharpe OOS | ΔCalmar OOS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0,15 | 20 | +0,54pp | +0,02 | −0,8pp | −0,04 | +0,93pp | +0,03 | +0,05 |
| 0,20 | 20 | +0,72pp | +0,02 | −1,1pp | −0,05 | +1,24pp | +0,04 | +0,07 |
| 0,25 | 20 | +0,89pp | +0,02 | −1,4pp | −0,07 | +1,55pp | +0,04 | +0,09 |
| 0,33 | 20 | +1,17pp | +0,02 | −1,9pp | −0,10 | +2,03pp | +0,04 | +0,12 |

(MaxDD FULL baseline = −17,8%; MaxDD OOS **không đổi** ở mọi mức w_DC = −17,2% — điểm rút vốn tối
đa OOS nằm ngoài giai đoạn BULL/EXBULL nên overlay không chạm tới, khớp quan sát đã có ở "phát
hiện phụ" job trước.)

**Chi phí transition gần như không đáng kể**: 20 lần chuyển trạng thái trong 11,9 năm (vào/ra
BULL/EXBULL), mỗi lần trả `w_DC × 0,1%` — raw vs net-of-TC lệch nhau <0,05pp CAGR ở mọi mức. Không
phải rào cản thực thi.

**Monotonic đều theo w_DC** — càng tăng `w_DC` càng cải thiện CAGR/Sharpe (cả FULL lẫn OOS), đổi
lại MaxDD FULL xấu thêm tuyến tính. Không có điểm "tối ưu cục bộ" nào giữa grid — dấu hiệu TỐT
(không phải 1 mức bị chọn vì tình cờ khớp nhiễu IS, xem mục robustness dưới).

## Robustness — grid monotonicity (thay PBO hình thức)

Grid chỉ 4 mức, không đủ để chạy PBO tổ hợp hình thức (Bailey-López-de-Prado cần nhiều split hơn
N=4 permit) — thay bằng câu hỏi thực chất hơn: **"IS-best có làm OOS tệ đi không?"** (dấu hiệu
overfit kinh điển).

| w_DC | IS Sharpe | OOS Sharpe |
|---|---:|---:|
| 0,15 | 1,68 (IS-best) | 2,02 |
| 0,20 | 1,67 | 2,03 |
| 0,25 | 1,67 | 2,03 |
| 0,33 | 1,67 | **2,04 (OOS-best)** |

IS gần như PHẲNG (1,67-1,68, chênh 0,01 — trong biên độ làm tròn) — không có tín hiệu "IS thích 1
mức cụ thể" để overfit vào. OOS đơn điệu tăng theo `w_DC`. Đây là hình dạng NGƯỢC với overfit
(IS-best không làm OOS xấu đi, mà OOS còn tốt hơn ở đúng mức w_DC cao nhất) — nhưng vì IS gần
phẳng, kết luận thực sự là "IS không phân biệt được các mức `w_DC`", không phải "mọi mức đều tốt
như nhau về mặt thống kê".

## Per-episode consistency (w_DC=0,20)

| # | State | Base | Blend | Delta |
|---|---|---:|---:|---:|
| 1 | BULL | +8,36% | +11,78% | **+3,42pp** |
| 2 | BULL | −0,73% | −3,23% | **−2,50pp** |
| 3 | EXBULL | +34,36% | +38,89% | **+4,53pp** |
| 4 | BULL | +19,07% | +21,56% | **+2,49pp** |
| 5 | BULL | +3,93% | +4,42% | +0,48pp |
| 6 | BULL | +14,80% | +13,65% | −1,15pp |
| 7 | BULL | +3,92% | +5,65% | +1,73pp |
| 8 | BULL | +6,78% | +6,55% | −0,23pp |
| 9 | EXBULL | +2,03% | +1,19% | −0,84pp |
| 10 | BULL | −2,23% | −1,42% | +0,81pp |

**6/10 episode blend thắng baseline**, mean delta +0,87pp/episode (median +0,65pp). Không phải
"thắng mọi lúc" — 4/10 episode âm, biên độ thua lớn nhất (ep2, −2,50pp) xảy ra ngay trong IS (đúng
giai đoạn phẳng nêu trên).

## Block bootstrap theo episode (N=10, không phải theo ngày)

3.000 lần resample 10 episode delta (w_DC=0,20) có hoàn lại:
- p5 = **−0,17pp**, p50 = +0,89pp, **P(mean delta > 0) = 0,916**.
- p5 vẫn cận 0 (âm nhẹ) — với N=10 episode, khoảng tin cậy 90% không loại trừ hoàn toàn khả năng
  "về lâu dài có thể huề hoặc thua nhẹ". Đây KHÔNG phải một cạnh biên rõ ràng như các phát hiện
  GO khác trong lịch sử research (VD alpha 8L 1/PE IC +0,125, 94% hit) — biên độ mỏng hơn nhiều.
- **Ghi chú trung thực**: đây là proxy hướng-nào-nhiều-khả-năng-hơn (giống DSR về tinh thần: dùng
  phân phối resample thay vì 1 con số điểm), KHÔNG PHẢI DSR chính thức Bailey-López-de-Prado (đòi
  hỏi chuỗi trial return, không áp dụng sạch cho 1 overlay state-gated nhị phân). Không thổi phồng
  N=482 ngày thành N=482 sự kiện độc lập — đã dùng đúng N=10.

## Transition risk — không cần thêm hysteresis

Cột `state` đã qua pipeline DT5G production thật (DT 4-gate: 25 phiên xác nhận VÀO
CRISIS/EXBULL, chỉ 10 phiên để RA — cam kết bất đối xứng built-in). Overlay này KHÔNG dựng lại
smoothing riêng, dùng thẳng tín hiệu đã mượt sẵn — đúng nguyên tắc "đừng re-tune DT5G"
(CLAUDE.md). 20 lần chuyển trạng thái/11,9 năm (~1,7 lần/năm) là tần suất thấp, chi phí đã đo
không đáng kể (mục trên). Không phát hiện nhu cầu buffer/hysteresis bổ sung riêng cho overlay này.

## Kết luận: **WEAK-GO có điều kiện** — không phải NO-GO, không phải GO mạnh

Khác hẳn Việc 1 job trước (static 1/3, NO-GO rõ ràng vì Sharpe/Calmar/MaxDD xấu đi ở FULL+IS):
kiến trúc state-gated **cải thiện nhất quán CAGR/Sharpe ở FULL và OOS tại MỌI mức `w_DC` trong
grid**, chi phí transition không đáng kể, không có dấu hiệu overfit lưới tham số (IS phẳng, OOS
đơn điệu). Nhưng biên độ mỏng và N nhỏ:
- Cải thiện tuyệt đối khiêm tốn: ΔSharpe FULL chỉ +0,02, ΔCAGR FULL +0,5 đến +1,2pp tuỳ `w_DC`.
- N=10 episode, bootstrap p5 vẫn cận 0 (−0,17pp) — không phải "chắc chắn dương".
- MaxDD FULL xấu thêm tuyến tính theo `w_DC` (−0,8 đến −1,9pp) — đánh đổi thật, không miễn phí.
- 8/10 bằng chứng đến từ giai đoạn OOS (sau 2020) — không phải walk-forward cân bằng IS/OOS thông
  thường, phần lớn là ngoài mẫu theo đúng nghĩa nhưng đè nặng vào 5-6 năm gần nhất.

→ **Đề xuất mức `w_DC=0,20`** nếu tiếp tục theo đuổi (điểm giữa grid, không phải điểm cực trị nào
— tránh chọn biên grid trông như cherry-pick).

## quant-skeptic verify

**Verdict: CONFIRMED (medium confidence)** — reproducibility (re-run byte-for-byte khớp mọi bảng),
không look-ahead (`state` = `tav2_bq.vnindex_5state_dt5g_live` đúng bảng production, DC leg đã
T+1), cơ chế overlay đúng (verify độc lập `w_DC=0` trả về đúng baseline, max abs diff = 0.0 —
script tự nó chỉ test partition identity, KHÔNG test riêng identity này, quant-skeptic bổ sung),
grid không có dấu hiệu overfit (IS gần phẳng, IS-best không làm OOS xấu đi).

**1 lỗi thật tìm thấy — N=10 "episode độc lập" bị THỔI PHỒNG**: quant-skeptic đo khoảng cách giữa
các episode và phát hiện ep1↔ep2 cách nhau 24 ngày, ep3↔ep4↔ep5↔ep6 cách nhau 15/31/47 ngày — quá
gần để coi là các đợt bull độc lập; nhiều khả năng đây là **2 đợt rally liên tục bị cắt vụn bởi
DT5G whipsaw ngắn quanh biên BULL/NEUTRAL** (rally 2018 và rally hồi phục COVID 2020-2021), không
phải 6 sự kiện vĩ mô tách biệt. N thật gần **6**, không phải 10.

**Tự kiểm lại theo đúng gợi ý quant-skeptic** (gộp ep1+ep2 → cluster A, ep3-6 → cluster B, giữ
nguyên ep7-10), bootstrap lại N=6:

| Cluster | Khoảng thời gian | Base cum | Blend cum | Delta |
|---|---|---:|---:|---:|
| A (ep1+2) | 2017-12-26 → 2018-05-08 | +15,66% | +16,27% | +0,62pp |
| B (ep3-6) | 2020-10-06 → 2021-12-24 | +148,58% | +160,78% | **+12,20pp** |
| 7 | 2024-01-24 → 2024-05-13 | +3,92% | +5,65% | +1,73pp |
| 8 | 2025-03-07 → 2025-05-16 | +6,78% | +6,55% | −0,23pp |
| 9 | 2025-08-12 → 2025-10-03 | +2,03% | +1,19% | −0,84pp |
| 10 | 2026-01-28 → 2026-02-12 | −2,23% | −1,42% | +0,81pp |

Bootstrap N=6, 3.000 resample: p5 = **+0,06pp**, p50 = +2,33pp, P(mean>0) = **0,960**.

⚠️ **Con số này KHÔNG nên đọc là "vững hơn"** dù p5 chuyển dương và P(mean>0) tăng — đó là ảo giác
thống kê: **cluster B (2020-2021, EXBULL COVID recovery) một mình đóng góp 12,20pp/14,29pp tổng
delta = 85% toàn bộ edge**. Bootstrap N=6 với 1 quan sát áp đảo sẽ hầu như luôn resample trúng nó
(P(không trúng B trong 6 lần rút có hoàn lại) = (5/6)^6 ≈ 33,5%, tức 66,5% lần resample có ít nhất
1 bản sao B) → p5/P(mean>0) "đẹp hơn" chỉ vì mẫu bé bị 1 điểm chi phối, không phải vì bằng chứng
mạnh hơn. **Kết luận đúng: toàn bộ edge của kiến trúc này gần như phụ thuộc vào ĐÚNG 1 giai đoạn
lịch sử (EXBULL 2020-2021)** — nếu loại cluster B, 5 cluster còn lại cho delta trung bình
(0,62+1,73−0,23−0,84+0,81)/5 = **+0,42pp/episode**, gần với 0, không có bằng chứng edge rõ ràng.
Đây là rủi ro TẬP TRUNG (concentration risk), không phải chỉ là "N nhỏ" như ghi nhận ban đầu.

## Tổng kết & khuyến nghị (đã cập nhật sau quant-skeptic)

- Kiến trúc **state-gated (chỉ BULL/EXBULL)** tốt hơn hẳn kiến trúc static 1/3 đã bị loại ở job
  trước — xác nhận đúng chẩn đoán "DC cần state-gate cho chính nó, không phải vấn đề của LAG".
  Cơ chế đúng (verify độc lập), không look-ahead, không overfit lưới tham số.
- **Nhưng bằng chứng mỏng hơn cả đánh giá ban đầu**: quant-skeptic + tự kiểm lại lộ ra **~85% toàn
  bộ edge dương đến từ ĐÚNG 1 cluster lịch sử (EXBULL COVID recovery 2020-2021)** — 5 cluster còn
  lại chỉ cho delta trung bình +0,42pp/episode, gần 0. Đây là rủi ro tập trung, không phải một edge
  dàn trải qua nhiều chu kỳ độc lập.
- **Khuyến nghị: KHÔNG wire, KHÔNG coi đây là GO** — hạ từ "WEAK-GO có điều kiện" xuống **"quan sát
  đáng theo dõi, chưa đủ bằng chứng độc lập để hành động"**. Cần ít nhất 1-2 episode BULL/EXBULL
  lớn nữa KHÔNG phải 2020-2021 để xác nhận edge có lặp lại ở chu kỳ khác hay chỉ là đặc thù 1 giai
  đoạn lịch sử. Quyết định cuối là của Mike/user, nhưng khuyến nghị kỹ thuật là chờ thêm dữ liệu.
- **KHÔNG đóng hẳn nhánh nghiên cứu DC 3-book** — kiến trúc state-gated vẫn khả thi hơn static và
  cơ chế đúng, chỉ là "chưa đủ N để kết luận", không phải "đã bị bác bỏ". Giữ mở, không action ngay.
