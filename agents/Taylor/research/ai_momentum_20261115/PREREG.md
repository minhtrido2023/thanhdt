# PREREG — AI giải thích momentum + phản biện chéo 2 họ model (paper-forward)

Phiên bản: v1 · 2026-11-15 · tác giả Taylor (job `Taylor_20261115_150627`) · kế hoạch gốc
`kb/projects/ai-momentum-research-plan-20261115.md`. **File này khoá md5 + commit TRƯỚC lần chạy
paper-forward đầu tiên.** Mọi thay đổi sau đó = file `PREREG_v2.md` mới + lý do, không sửa tại chỗ;
sự kiện đã chấm trước v2 vẫn chấm theo v1.

User chốt 15/11 22:05 ICT: (1) cổng CHÍNH = **G-fcst** (edge dự báo), **G-proc** là cổng phụ;
(2) vũ trụ = `universe_pit` ∧ `rating_8l ≤ 4`; (3) M2 = deepseek qua `bin/second_opinion.sh` chạy MÙ
trước; `fundamental-skeptic` là cổng nội dung cho tập ưu tiên ở P1; (4) topic Momentum Lab.

## 1. Đơn vị phân tích = SỰ KIỆN (không phải dòng)
Sự kiện momentum tại ngày T (đóng cửa T, cột `tav2_bq.ticker`, mọi giá trị ≤ T):
- `mom20 = Close_T/Close_{T−20} − 1 ≥ 0,20`; `idio20 = mom20 − (VNINDEX_T/VNINDEX_{T−20} − 1) ≥ 0,15`;
  `Volume_1M/Volume_3M_P50 ≥ 1,5`; `Close ≥ HI_3M_T1`; `Price×Volume_1M ≥ 3 tỷ`.
- Vũ trụ: `tav2_mike.universe_pit` (`ruleset_version=1`, `in_universe`) tại T — KHÔNG `ticker_prune`.
- Rating: `tav2_bq.fa_ratings_8l` **as-of** (dòng có `time ≤ T` mới nhất của mã) `rating ≤ 4`; `route`
  as-of cùng dòng. Mã không có rating as-of ⇒ loại. (Caveat: bảng được republish định kỳ, lịch sử
  as-of có thể lệch nhẹ — với paper-forward thì ta GHI rating đọc được ngày T vào JSONL, đó là PIT thật.)
- Độc lập: greedy theo thời gian, sự kiện mới của cùng mã chỉ khi > 90 ngày lịch kể từ sự kiện
  trước ĐÃ PHÁT **và** khác quý dương lịch.
- Mã có cờ DD (BANNED list KB, `data/forensic_flags.csv` severity=exclude với date ≤ T, RED_FLAG
  sổ DD) vẫn chạy pipeline + chấm, nhưng nhãn `LOẠI khỏi mọi candidate` (luật 02/11).
- Hàng đợi: tối đa 10 sự kiện/tuần, ưu tiên `liq_bn` giảm dần; sự kiện bị cắt vẫn ghi
  `skipped_capacity` (để kiểm tra chọn lọc).
- SQL: `events_sql.sql`; cooldown: `build_events.py`.

## 2. Kết quả (outcome) — chỉ dùng để CHẤM, không bao giờ làm filter
- `ex20` / `ex60` = `Close_{T+1+h}/Close_{T+1} − 1` (vào lệnh giả định đóng cửa T+1, h=20/60 phiên)
  trừ **trung vị cùng ngày của route 8L** trên universe_pit. Winsor 1%/99% trên toàn mẫu cuối.
- Nhị phân: `hit = 1{ex_h > 0}` cho view CONT; `1{ex_h < 0}` cho view REV.

## 3. Pipeline (prompt + schema: `prompt_M1.md`, `prompt_M2_blind.md`, `prompt_M2_challenge.md`, `schema_*.json`)
M1 (Claude Sonnet, medium) điều tra → JSON `schema_M1.json`. M2 (deepseek, `second_opinion.sh`) chạy
**MÙ** trên cùng gói → `blind_driver`, `blind_view`; SAU ĐÓ nhận JSON M1 → `missed[]`, `disagree[]`.
M1 trả lời phản biện tối đa 1 vòng (tổng ≤2 vòng) → `final_view_*`. Live: M1 được WebSearch (PIT theo
cấu trúc); mọi bằng chứng phải có ngày ≤ T. Kết quả M2 không chạy ⇒ ghi `m2_status=FAIL`, sự kiện vẫn
chấm cho T1/T2 (fail-open), loại khỏi T3.

## 4. G-fcst — CỔNG CHÍNH. Ba phép thử, khai trước, một phía
| # | H0 | H1 | Thống kê |
|---|---|---|---|
| **T1** | view_20s cuối không phân biệt được ex20 | `mean ex20[final_view_20s=CONT] − mean ex20[final_view_20s ∈ {REV, NO_VIEW}] > 0` | chênh trung bình (winsor) |
| **T2** | driver_class không phân biệt được ex60 | `mean ex60[driver ∈ {EARNINGS, CORP_ACTION}] − mean ex60[driver ∈ {NARRATIVE_ONLY, UNKNOWN}] > 0` | chênh trung bình (winsor) |
| **T3** | phản biện M2 không thêm giá trị | `hit20(final_view) − hit20(B1 = view M1 trước phản biện) > 0` trên sự kiện có view có hướng ở ít nhất 1 bên | chênh hit-rate cặp |
- **p-value**: hoán vị **KHỐI THÁNG** (giữ nguyên chuỗi nhãn của từng tháng dương lịch, đổi thứ tự
  tháng, ghép lại theo thời gian), 10.000 hoán vị, seed 20261115, threads=1. CẤM hoán vị trong năm/
  trong tháng (luật 12/11). Cần ≥ 6 tháng có sự kiện thì mới tính p (dưới đó độ phân giải hoán vị không
  tới được α).
- **Đa phép thử**: BH-FDR q = 0,05 trên đúng 3 p-value T1–T3. Không thêm phép thử nào khác vào họ này;
  mọi phân tích khác là MÔ TẢ.
- **Baseline**: B0 = tiếp diễn cơ học (CONT mọi sự kiện, hit20 B0 = P(ex20>0)); B1 = M1 không phản biện.
  T1 thắng ⇔ pipeline chia được nhóm, điều B0 không làm được. Báo cả hit20 pipeline vs B0 (mô tả).
- **Ngưỡng kinh tế tối thiểu** (cùng với thống kê): T1 chênh ≥ 5pp ex20; T2 chênh ≥ 8pp ex60. Đạt
  thống kê nhưng dưới ngưỡng kinh tế ⇒ "có ý nghĩa thống kê, không đáng giá", không GO.
- **Ổn định**: dấu hiệu ứng phải cùng chiều ở 2 nửa thời gian (cắt theo trung vị ngày sự kiện).

### 4.1 Lịch nhìn (look) — ĐỊNH SẴN, không peek
Sự kiện chỉ được "chấm" khi đã qua đủ 61 phiên (ex60). Scorer chỉ in kết quả T1–T3 ở 3 mốc dưới đây;
giữa các mốc scorer chỉ in N và G-proc (không in hiệu ứng).
| Look | Khi nào | Quy tắc (Haybittle–Peto) |
|---|---|---|
| L1 | N_scored ≥ 80 | Dừng **GO sớm** chỉ khi p_raw < 0,001 và đạt ngưỡng kinh tế; **dừng vô ích** nếu cả T1 và T2 có hiệu ứng ≤ 0 |
| L2 | N_scored ≥ 150 | như L1 |
| FINAL | N_scored ≥ 250 **hoặc** 24 tháng lịch sau sự kiện đầu (cái nào trước) | BH q=0,05 + ngưỡng kinh tế + ổn định ⇒ GO; ngược lại NO-GO |
Hai look trung gian tiêu α không đáng kể (Haybittle–Peto) ⇒ FINAL dùng α đầy đủ.

### 4.2 Power đo được (`power_sim.py`, phân phối ex THẬT của 330/319 sự kiện R4 2024-10→2026-11, nhãn cụm theo tháng, p hoán vị khối tháng, α = 0,05/3 một phía)
| N_scored | ex20 chênh 5pp | 8pp | 12pp | ex60 chênh 8pp | 12pp | 20pp |
|---|---|---|---|---|---|---|
| 40 | 0,04 | 0,05 | 0,14 | 0,01 | 0,07 | 0,18 |
| 80 | 0,18 | 0,41 | 0,61 | 0,22 | 0,50 | 0,78 |
| 150 | 0,41 | 0,87 | 0,98 | 0,43 | 0,85 | 1,00 |
| 250 | 0,69 | 0,95 | 1,00 | 0,73 | 0,98 | 1,00 |
(200 mô phỏng/ô × 400 hoán vị ⇒ sai số Monte Carlo ±0,03–0,07.) Nhị phân (hit-rate vs 50%, xấp xỉ
chuẩn, power 0,8): MDE +23,5pp @N=40, +16,6 @80, +12,1 @150, +9,4 @250. ICC theo tháng đo được
0,007 (ex20) / 0,003 (ex60) — cụm tháng của outcome yếu sau khi trừ trung vị route.
**Đọc thẳng**: N=40 không phát hiện nổi gì; N=150 chỉ bắt được chênh ≥ 8pp ex20 / ≥ 12pp ex60 —
hiệu ứng LỚN. Edge thật của LLM nếu có nhiều khả năng nhỏ hơn (giả định) ⇒ kết cục có xác suất cao
là "không kết luận được". Đó là kết quả hợp lệ, phải báo đúng như vậy.

### 4.3 Tốc độ N (đo, `build_events.py`)
R4 2024-10→2026-11-13: 341 sự kiện / 26 tháng (TB 13,1, trung vị 8/tháng, rất cụm: 2025-07/08 = 40/48,
2026-04/05 = 2/3). **6 tháng đủ gần nhất (05→10/2026): TB 6,3/tháng.** ⇒ N_scored=150 cần ~24 tháng ở
nhịp gần đây (~11 tháng ở nhịp TB) + 3 tháng chờ ex60. Đây là lý do có trần FINAL 24 tháng.

## 5. G-proc — cổng PHỤ (an toàn quy trình; trượt ⇒ dừng sớm, không cần chờ G-fcst)
Đo trên 40 sự kiện paper-forward đầu: (a) ≥ 80% sự kiện có ≥ 1 bằng chứng ngày ≤ T kiểm được;
(b) tỉ lệ UNKNOWN+NARRATIVE_ONLY ≥ 10% (dưới = nghi narrative fallacy); (c) bất đồng có bằng chứng
M1–M2 trong 20–60%; (d) flip_rate M1 sau phản biện ≤ 50%; (e) chi phí ≤ $15/ngày. Trượt (a) hoặc (e)
⇒ dừng sửa quy trình; trượt (b)–(d) ⇒ ghi cảnh báo, tiếp tục.

## 6. Leakage & hồi tố
- Bằng chứng GO/NO-GO **duy nhất** = paper-forward (chạy tại T, ghi JSONL append-only có md5, trước khi
  có outcome).
- Hồi tố (sự kiện ≥ 2026-07) chỉ để gỡ prompt; **không** gộp vào N chính. Cấm WebSearch; chỉ
  `stock_news` `public_date ≤ T` + BQ ≤ T. Canary rò rỉ: hỏi model riêng (không gói) hướng/biên độ giá
  20 phiên sau T; trả lời có hướng đúng + biên độ trong ±5pp ⇒ đánh dấu rò.
- `stock_news.ingested_at` trễ ⇒ live phải ghi `ingested` của từng tin; tin có `public_date ≤ T` nhưng
  nạp sau T **không** được dùng trong paper-forward (không có ở thời điểm T theo cấu trúc).

## 7. Không làm
Không tín hiệu mua, không override SIGNAL_V11, không ghi `state_*.json`/plan, không trường "mua" trong
output. Mọi báo cáo có dòng cố định "KHÔNG phải khuyến nghị mua; sleeve chỉ qua DD + user duyệt".
quant-skeptic CONFIRMED là điều kiện cần trước khi diễn giải GO.
