# R&D pipeline tracker — mọi mục PAPER-ONLY trừ khi ghi rõ LIVE

> Tách ra khỏi `kb/current_ops.md` 2026-08-01 (token-cost review, user mandate) — đây là backlog
> nghiên cứu đang chạy, KHÔNG phải trạng thái an toàn/live cần biết mỗi phiên. Không injected vào
> `context_pack.md` — đọc file này khi cần theo dõi/cập nhật tiến độ R&D, hoặc khi checkpoint tới
> hạn cần xác nhận. Cập nhật lần cuối khi tách: 2026-08-01 (nội dung y nguyên từ current_ops.md).

Chi tiết đầy đủ từng mục: bus finding của Taylor + `kb/incidents/index.md`.

- **Insider-sell WATCH shadow (`insider_flags.py`)** (WATCH-only, chưa wire due-diligence, từ
  2026-07-29): cờ bán ròng nội bộ ≥1% CP lưu hành/90 ngày (chỉ `event_code IN ('DDIND','DDRP')`,
  TTL 90d). Scoping (job Taylor_20260729_015830 + Phụ lục A `_032713`) kết luận GO: overlap thấp
  với `anomaly_scan`/`forensic_flags` (7,1-21,7%), lift phần riêng 2,08× (z=5,74), ổn định IS/OOS;
  hai cờ bắn ở hai thời điểm khác nhau (insider sớm hơn ~2 tháng so với anomaly). Đang dựng
  writer/reader (job Taylor_20260729_104614). **Sàn review ~2026-08-29 (≥1 tháng shadow), trần
  ~2026-09-15.** Điều kiện TIẾP TỤC (wire vào due-diligence report như dòng bằng chứng): cadence
  refresh bảng nguồn xác nhận chạy đều (bq_admin đang fix bug tính đến 07-29) + shadow log sạch
  (không false-trigger bất thường) + qua quant-skeptic trước khi vào due-diligence chính thức.
  Điều kiện NGỪNG: bq_admin không fix xong cadence (bảng đứng im, cờ đóng băng) hoặc shadow log
  noise quá tải (~>5 mã/tháng cần review tay, vượt xa ước tính ~3/tháng). **Tuyệt đối không hard-
  exclude ở bất kỳ giai đoạn nào** — 85% mã bị cờ không sập (§3.5 research file), chỉ là dòng bằng
  chứng WATCH cho người duyệt plan cân nhắc. Research đầy đủ:
  `mike/agents/Taylor/research/insider_transaction_scoping_20260729.md`.
- **EXTREME-regime gate** (paper `main` only, từ 07-01): stress PASS 24/24, target checkpoint
  ~2026-07-28 **ĐÃ QUA, CHƯA XÁC NHẬN trạng thái** (không tìm thấy sign-off/close nào — cần dispatch
  Taylor kiểm tra lại, không tự đoán). Điều kiện LIVE (chưa đổi): 0 false-trigger ~4 tuần benign +
  không can thiệp NORMAL-path + user sign-off. ⚠️ audit `Winston_20260712_142100` (M5, xem
  `kb/incidents/index.md`) từng nêu `executor.py` đọc `ticker_prune.parquet` monolith đông cứng từ 06-26
  khiến rvol/prior_close trial này tính trên giá cũ 2+ tuần — bug monolith đã **FIXED 07-13**
  (Winston_20260713_143546), câu hỏi mở CHỈ còn là evidence giai đoạn 06-26→07-13 có giá trị
  không, cần Taylor xác nhận cùng lúc. KHÔNG bật ở live cho tới khi có xác nhận.
- **Vol-scale buy chase-cap patch#3** (paper `main` only, từ 07-01, k=2.0/ceil=0.04): stress PASS
  15/15, target checkpoint ~2026-07-14 **ĐÃ QUA HƠN 2 TUẦN, CHƯA XÁC NHẬN**. Điều kiện LIVE (chưa
  đổi): paper sạch, không đụng NORMAL-path ngày non-gap, skeptic rerun REAL-fill, user sign-off.
  Cùng câu hỏi M5 (evidence 06-26→07-13) áp dụng. KHÔNG bật ở live cho tới khi có xác nhận.
- **Sector sweep #10+**: chờ Mike dispatch.
- **Fill-timing khung giờ** (BUY 11:15 / SELL open): edge thật đo được (+17.6bps BUY t=12.0,
  +11.8bps SELL), KHÔNG flip `fill_timing_live_gate` — cần ≥5 phiên paper có BUY fill trong cửa sổ
  + 0 reject + không lệnh treo → quant-skeptic → user sign-off (điều kiện chốt sau audit fill thật
  `Taylor_20260709_101602`, phát hiện `execution_quality_review.py` từng đếm nhầm lệnh LIVE làm
  "98% adherence" giả — evidence-rate thật ≈0 khi đó). Checkpoint tự nhiên ~cuối 07 **ĐÃ TỚI, CHƯA
  XÁC NHẬN đủ điều kiện chưa** — cần Taylor kiểm tra số phiên đã đạt. Option: pilot ZaloPay trước
  SpaceX — chưa quyết.
- **V2.5**: R&D-complete, DISABLED. Reminder 2026-07-07: Mike hỏi user go-ahead integration.
- **DC-book (ConvergePort) NEUTRAL idle-cash waterfall** (paper `main` only, từ 07-06): thứ tự ưu
  tiên giải ngân **BAL/LAG (full trước) → DC book (double-confirm sector-lens BUY ∧ 8L rating≤2,
  capacity ~10-15B ex-DHG) → custom30V**; reverse-unwind khi BAL/LAG có deal lại. Backtest: +5.0pp
  sleeve parking (~+3.5pp/năm SpaceX-now), nhưng DSR phần excess chỉ 0.775 (<0.95 ngưỡng an toàn) —
  bảo hiểm hợp lý, CHƯA phải alpha tin cậy cao → lý do bắt buộc paper trước. Trong EOD daily report.
  Review = EVENT-ANCHORED (khi chu kỳ reverse-unwind đầu tiên hoàn tất + settle 4-6 tuần), sàn
  ~2 tháng, trần ~2026-10-06 (trượt theo nếu LAG refill trượt lịch).
  ⚠️ **Bug đã biết, sửa TẠI mốc review (không sửa sớm — user chốt 07-13, muốn quan sát whipsaw thật
  trước)**: paper sleeve dùng trigger NHỊ PHÂN thay vì spec đúng (DC book chạy liên tục trên residual)
  → hiện TỆ HƠN baseline không-DC (CAGR 27.26%/DD−17.8%/Calmar 1.53/turnover 20.7× vs spec đúng
  27.56%/−15.5%/1.77/3.18×). 4 việc khi tới review, theo thứ tự: (1) đổi sang continuous-residual
  trigger — bug thực chất, ưu tiên nhất; (2) đồng bộ rebalance vào q2m5 (giảm whipsaw ~4 lần);
  (3) cap gộp 0.15/tên (chống trùng DC↔custom30V); (4) liquidity floor 3B thay hard-exclude DHG.
  4 góc khác đã kiểm tra kỹ, không còn dư địa cải thiện — không cần backtest thêm cho chúng.

## Checkpoint quá hạn chưa xác nhận (cần dispatch Taylor, đừng tự đoán trạng thái)
- EXTREME-regime gate: checkpoint 2026-07-28 đã qua.
- Vol-scale chase-cap patch#3: checkpoint 2026-07-14 đã qua hơn 2 tuần.
- Fill-timing: checkpoint cuối 07 đã tới.
