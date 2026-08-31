# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Margin đơn mã discretionary — LIVE, PB-adaptive WIRED (đóng hoàn toàn)
- Per-name 5% / sleeve 10% NAV, f≤1.3, %ADV≤10%, exit -20%. Commit 022c48e7.
- Phễu candidate WIRE (cutoff=70%, trần=1.2), commit 714b5889. TV1/DGC lọt nhưng marginable=NO
  qua DNSE hiện tại.

## Chuỗi khai thác DC alpha — 30/08 → 31/08, ĐÓNG HOÀN TOÀN
- 30/08: 4 hướng research (static book NO-GO, state-gated weak-GO N mỏng, EXBULL audit, LAG
  SUE NO-GO) — không mechanism nào wire.
- 31/08 sáng, 3 việc LENS-not-BOOK (user duyệt 08:41 ICT):
  1. **DC-tilt custom30V**: NO-GO bằng suy luận (không cần backtest) — DC_ann 22,83% ở NEUTRAL
     thấp hơn cả BAL/LAG/baseline, mà custom30V chỉ active NEUTRAL. Lần tilt thất bại thứ 5,
     nhưng có lý do cơ chế rõ. File: dc_tilt_custom30v_20260831.md.
  2. **Candidate feeder**: file mới `mike/bin/dc_candidate_feeder.py` (registry đứng riêng, RECON-
     only, idempotent). 9 mã qualify hôm nay (ACB/CTR/DHG/FPT/HAH/MBB/PVT/SSI/TCB). Commit mike
     `2272a502`.
  3. **Mở paper sang BULL/EXBULL**: gate `dc_book_waterfall_paper.py` mở rộng, cơ chế
     deploy/trigger/cadence KHÔNG đổi. Selfcheck +11 test (78/78 pass). Commit WorkingClaude
     `b9c585ab`.
  File: dc_candidate_feeder_and_bull_paper_20260831.md.
  **Phát hiện phụ + đã tự sửa**: `kb/projects/rnd-pipeline-tracker.md` mục DC-book bị LỖI THỜI
  (mô tả 4 fix "còn treo" trong khi code đã áp dụng từ 07-20, SLEEVE_VERSION="v2") — đã cập nhật
  lại cho khớp thực tế + thêm dòng 08-31 mở BULL/EXBULL. Commit mike `ee7200b8`.
- **Kết luận chung chuỗi DC alpha**: alpha có thật (BULL, xác nhận độc lập nhiều lần) nhưng
  KHÔNG có edge ở NEUTRAL; kiến trúc "book riêng" thất bại ở mọi biến thể đã thử; hướng khả thi
  nhất là LENS/feeder (đã implement) + tích luỹ bằng chứng BULL tự nhiên qua paper (đã mở rộng)
  cho tới mốc review ~06/10. KHÔNG còn việc treo trong chuỗi này.

## CAP_SIGNAL advisory + khủng hoảng cơ cấu 2007-2012 — KHÉP KÍN (30/08)
Wire cả 3 cadence, ngưỡng nâng cấp N≥10. kb/projects/cap-signal-advisory-20260830.md.
DT5G giữ nguyên fail-safe.

## Retro 2026-08-30 — XONG
kb/incidents/retro/retro-2026-08-30.md, Wags CONFIRMED. Sự cố #1 (quant-skeptic kẹt status
running dù verdict thật CONFIRMED) chưa đạt ngưỡng escalate (cần 2 retro liên tiếp).

## Vận hành — không có việc treo
Không circuit breaker trip, không pending_resumes, không bus question mới mở.
job quant-skeptic_20260830_085357: OVERDUE cosmetic đã biết, bỏ qua (verify substance qua log).

## Macro watch
Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Review quý next ~2026-11-26.

- [2026-08-31T04:13:36Z] 31/08: chuỗi Bobby(blind)+Taylor(data) cho 3 crisis episode XONG — 2009(MIXED,job Taylor_20260831_033154)+2020/2022(CONTAINABLE,job Taylor_20260831_040228). Finding chính: LEAD-1..4 rút từ N=1(2009) hầu hết KHÔNG generalize sang N=3 — 'targeted action luôn thắng blanket' bị bác bỏ (2022: SCB targeted lag dài hơn blanket rate-hike); mốc lag ngắn nhất = nhánh rủi ro CUỐI CÙNG được giải quyết, không phải nhánh gốc. Phát hiện phụ mới: healing speed (10/12/47 phiên) tương quan HÌNH DẠNG cú sốc (1 lần sắc nét vs nhiều đợt), KHÔNG map theo Loại-1/Loại-2 Bobby. Research-only, không wire. Report: agents/Taylor/research/vn_2009_recovery_trigger_20260831/ + vn_2020_2022_recovery_trigger_20260831/.
