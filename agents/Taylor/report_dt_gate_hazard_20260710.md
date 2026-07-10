# DT 4-gate như một hazard function — "đồng hồ xác suất commit" (exploratory, giai đoạn 1)

**Job**: Taylor_20260710_122230 · **Ngày**: 2026-07-10 · **Tác giả**: Taylor
**Trạng thái**: EXPLORATORY RESEARCH — CHƯA qua quant-skeptic, KHÔNG dùng cho quyết định live/derivative
cho tới khi có bước phản biện tiếp theo. Không sửa code production, không tạo bảng BQ mới.

**Script**: `mike/agents/Taylor/dt_gate_hazard_research.py`
**Data artifacts**: `data_dt_gate_episodes.csv`, `data_dt_hazard_need10_other_*.csv`, `data_dt_hazard_need25_into_CRISIS_EXBULL_*.csv`

---

## 1. Cơ chế thật đang chi phối commit (đọc từ source, không phải từ trí nhớ)

`macro_state_live.py::_dt_4gate` (dòng 69–82, = `DT_10_25_25`) track **streak `pr`** = số phiên liên tiếp
base state (cột `state` của `vnindex_5state_tam_quan_v34b_clean`, warm-up 2014) khác với state đang
committed. Commit khi `pr >= need`:

| Chuyển | `need` (phiên) |
|---|---|
| → vào CRISIS (`enC`) | **25** |
| → vào EX-BULL (`enX`) | **25** |
| rời CRISIS (`exC`) / rời EX-BULL (`exX`) | **10** |
| mọi chuyển khác giữa NEUTRAL/BEAR/BULL (`default`) | **10** |

**Đính chính con số "7 phiên" của user**: không có ngưỡng 7 nào trong pipeline live. Chuyển sang
BEAR/BULL (từ NEUTRAL) bị chi phối bởi **default=10**. Con số 30 (`min_dur` BearDvg) thuộc tầng base
v3.4b bên dưới, không phải tầng DT-gate. Báo cáo này model **tầng DT-gate** (input = base state đã
smoothing của v3.4b; macro cap nằm trên DT4 nhưng lịch sử chỉ lệch 4 episode nên không đổi kết luận).

**Định nghĩa episode** (causal): bắt đầu phiên đầu tiên base state ≠ committed; kết thúc hoặc **COMMIT**
(streak đạt `need`) hoặc **REVERT** (base đổi state trước khi đạt ngưỡng — quay về committed hoặc nhảy
sang candidate khác). Mọi giá trị tại phiên t chỉ dùng thông tin tới hết phiên t (đúng cơ chế gate).
Lưu ý duy nhất về causality: **label** commit/revert của episode chỉ biết khi episode kết thúc — nên
hazard curve dùng live tại thời điểm t phải calibrate trên các episode đã kết thúc trước t; IS/OOS split
bên dưới chính là kiểm tra honest cho việc đó.

## 2. Self-check (bắt buộc trước khi tin số)

- Replicate `_dt_4gate` trên base 2014+ → so với bảng production `vnindex_5state_dt5g_live` (parquet
  cache sync 23:45): **0 diffs / 3.120 phiên overlap** (cả cột `state` lẫn `state_raw`).
- Base transitions 2014+: **154**; DT4 transitions: **51** (khớp KB "~153" / "~49–53").
- Số episode COMMIT (51) == số DT4 transitions (51) — extractor nhất quán với gate. ✅
- Tổng: **121 episodes** = 51 commit + 69 revert + 1 censored (đang chạy, xem §7).

## 3. Hazard curve chính — P(eventual commit | streak đã đạt k)

### Nhóm need=10 (mọi chuyển NEUTRAL/BEAR/BULL + thoát CRISIS/EX-BULL) — 87 episodes, 86 resolved, 40 commit

| k | n resolved | P(commit\|k) | bootstrap 95% CI | revert hazard tại k |
|---|---|---|---|---|
| 1 | 86 | 0.465 | [0.372, 0.570] | 0.000 |
| 2 | 86 | 0.465 | [0.372, 0.570] | 0.057 |
| 3 | 81 | 0.494 | [0.390, 0.602] | 0.134 |
| 4 | 70 | 0.571 | [0.464, 0.681] | 0.070 |
| 5 | 65 | 0.615 | [0.500, 0.731] | 0.091 |
| 6 | 59 | 0.678 | [0.561, 0.788] | 0.050 |
| 7 | 56 | 0.714 | [0.600, 0.821] | 0.158 |
| 8 | 47 | 0.851 | [0.750, 0.944] | 0.104 |
| 9 | 42 | 0.952 | [0.882, 1.000] | 0.047 |
| 10 | 40 | 1.000 | — | commit (cơ học) |

### Nhóm need=25 (vào CRISIS/EX-BULL) — 34 episodes, 11 commit

Curve thô: P(commit|k) từ 0.32 (k=1) → 0.48 (k=10) → 0.73 (k=14) → 0.85 (k=16–23) → 1.00 (k=24).
CI cực rộng ở đuôi: k=16–23 là **[0.60, 1.00]** với chỉ 13 episode at-risk; riêng candidate EX-BULL chỉ
có 12 episode/2 commit trong 12 năm. **Nhóm này chưa đủ mẫu để calibrate xác suất** — chỉ mang tính
minh họa. (Bảng đầy đủ k=1..25 + CI trong CSV đính kèm.)

## 4. Phát hiện quan trọng nhất: streak-length KHÔNG phải biến thông tin chính

**(a) Per-session revert hazard xấp xỉ PHẲNG (~9%/phiên), không giảm theo k.** Likelihood-ratio test
constant-hazard vs per-k hazard (nhóm need10, k=2..9): LR=8.71, df=7, **p=0.274 — không bác bỏ được
hazard hằng số**. Nghĩa là đường P(commit|k) đi lên chủ yếu là **survivorship cơ học** (một quá trình
chết-hình-học tiến dần tới ngưỡng tất định), KHÔNG phải bằng chứng "càng gần ngưỡng càng gia tốc".
Trực giác của user đúng ở tầng kết quả (P(commit) tại k=5–6 ≈ 0.62–0.68 > k=3 ≈ 0.49) nhưng cơ chế
đằng sau là đồng hồ đếm ngược + tỉ lệ rơi ~9%/phiên, không phải hazard tăng dần. Ngoại lệ đáng chú ý:
cụm revert tại k=7 (9 episodes, hazard 0.158 — cao nhất curve) — với mẫu này chưa phân biệt được noise.

**(b) CANDIDATE STATE là biến phân biệt lớn hơn nhiều so với streak length** (nhóm need10):

| Candidate | episodes | P(commit\|k=1) | P(commit\|k=5) | P(commit\|k=8) |
|---|---|---|---|---|
| NEUTRAL (mean-revert về giữa) | 26 | **0.81** | 0.88 | 0.96 |
| BULL (từ NEUTRAL lên) | 23 | 0.41 | 0.53 | 0.75 |
| BEAR (từ NEUTRAL xuống) | 38 | **0.26** | 0.42 | 0.77 |

Một candidate BEAR mới xuất hiện chỉ có ~26% xác suất đi tới commit; candidate NEUTRAL (hồi về giữa)
có ~81%. Chênh lệch 3x này lớn hơn toàn bộ độ dốc theo k ở vùng k≤7. **Bất kỳ "đồng hồ xác suất" nào
muốn dùng thật đều phải condition theo candidate state (và state gốc)** — nhưng khi chia ô như vậy,
mẫu rơi xuống 20–38 episode/ô, ~10 commit/ô → CI ±15–25pp: đủ để xếp hạng thô, **không đủ để định giá
xác suất cho derivative**.

## 5. Độ ổn định: IS/OOS + leave-one-out theo năm

- **IS 2014–19** (32 ep, 13 commit) vs **OOS 2020+** (55 ep, 27 commit), nhóm need10: shape gần trùng
  (k=1: 0.41 vs 0.50; k=5: 0.59 vs 0.63; k=8: 0.81 vs 0.87; k=9: 0.93 vs 0.96). CI hai giai đoạn chồng
  nhau ở mọi k → curve **không phải sản phẩm của một giai đoạn**.
- **LOO theo năm** (need10): P(commit|k≥5) full = 0.615, range bỏ-từng-năm [0.590, 0.655]; P(commit|k≥8)
  full = 0.851, range [0.829, 0.900] → **không có năm nào gánh pattern** (commits rải 1–6/năm, 13 năm).
- Nhóm need25: IS chỉ 13 ep/4 commit — IS/OOS split ở nhóm này vô nghĩa thống kê, chỉ in để tham khảo.

## 6. Kết luận thẳng thắn về độ tin cậy

1. **Ở mức mô tả (descriptive), curve nhóm need10 là THẬT và ổn định**: 86 episode resolved, đơn điệu,
   IS/OOS khớp, LOO sạch, không có tham số nào được tune (N trials = 1 spec — ngưỡng lấy nguyên từ
   production, không search).
2. **Ở mức tín hiệu giao dịch derivative/futures: CHƯA ĐỦ POWER.** Ba lý do độc lập:
   - Muốn trade thì phải condition theo candidate state (mục 4b) → ô dữ liệu chỉ ~10 commit; CI quá
     rộng để định cỡ vị thế có đòn bẩy. Riêng hướng "đánh sớm CRISIS/EX-BULL" (nhóm need25 — chính là
     kịch bản futures hấp dẫn nhất) chỉ có 11 commit/12 năm.
   - Hazard phẳng (mục 4a) nghĩa là thông tin gia tăng của "streak dài thêm 1 phiên" thấp — phần lớn
     giá trị của đồng hồ nằm ở việc **biết candidate state gì đang chạy và nó chưa chết**, điều mà
     bảng state công khai đã cho biết gần hết.
   - Gate ăn input là base v3.4b **đã smoothing** — "đánh sớm" DT-gate thực chất là front-run tầng
     smoothing của chính mình; tín hiệu sớm thật sự phải xuống tầng dưới (factor score / state_raw
     của base), đó là câu hỏi nghiên cứu khác, chưa làm ở đây.
3. **Dùng được ngay (không rủi ro)**: như một **chỉ báo tình huống (situational awareness)** — hiển thị
   "candidate X đang ở k/need, base-rate commit lịch sử ≈ p [CI]" trong dna_report/plan context để
   người đọc biết gate đang "nạp đạn" — thuần thông tin, không tự động hóa sizing.

## 7. Quan sát live tình cờ (2026-07-10, thuần thông tin — không phải khuyến nghị)

Episode censored duy nhất đang chạy: **candidate BULL từ NEUTRAL, streak k=9/10 tính tới 2026-07-09**
(base v3.4b giữ state=4 liên tục từ 2026-06-29). Nếu base 2026-07-10 vẫn BULL → DT4 commit
**NEUTRAL→BULL hôm nay** (phiên thứ 10). Base-rate lịch sử P(commit | BULL-candidate đạt k=9) = 9/9
(CI rule-of-3 ~[0.66, 1.00]). Lưu ý ngược chiều: `state_raw` (pre-smoothing) của base đã rơi về 3
trong 3 phiên gần nhất (07-07..07-09) — nếu smoothing của base flip về NEUTRAL hôm nay thì episode
revert. Ý nghĩa vận hành nếu commit: DT5G NEUTRAL(70%) → BULL(100%) target cho allocator. Mike/
DollarBill nên coi đây là heads-up để không bất ngờ với plan T+1, KHÔNG phải tín hiệu đi trước gate.

## 8. Next steps đề xuất (chờ duyệt, chưa làm)

1. Quant-skeptic pass trên chính báo cáo này (đúng quy trình trước mọi bước tiếp).
2. Nếu muốn đi tiếp hướng derivative: chuyển câu hỏi xuống tầng base (hazard trên factor score /
   state_raw, nơi có nhiều biến thiên hơn) thay vì tầng DT-gate; và gom thêm mẫu pre-2014 của base
   (breadth chỉ tin được từ ~2008) để nới n cho nhóm need25 — chấp nhận regime khác.
3. Nếu chỉ cần situational awareness: thêm 3 dòng "candidate streak clock" vào dna_report (read-only,
   không đụng sizing) — việc nhỏ, tách riêng, vẫn cần user duyệt vì chạm production report.
