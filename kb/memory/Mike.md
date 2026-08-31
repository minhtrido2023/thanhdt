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
- [2026-08-31T04:55:38Z] 31/08 (tiếp): +2 job nữa đóng chuỗi crisis-trigger research — 2012(job 042736, W-shape 2 đáy, đáy giả 01/2012 rồi đáy thật 11/2012, cơ chế MỚI 'peak-stressor-exhaustion'+'uncertainty-resolution-qua-công-bố-tin-xấu', LEAD-1 breadth-trùng-đáy BỊ BÁC BỎ cho STRUCTURAL nhưng LEAD-1b healing-speed >50 phiên XÁC NHẬN MẠNH là dấu hiệu STRUCTURAL) + top-divergence/margin-selloff(job 042737, giả thuyết breadth-euphoria-tại-đỉnh CHỈ đúng 1/4 case=2022-01, volume-divergence 0/4 xác nhận — KHÔNG dùng làm gate độc lập; case 07/2026 xác nhận MẠNH margin-forced qua tin tức thật độc lập, dư nợ margin kỷ lục ~440k tỷ, BCTC Q2 thực ra TỐT hơn TB nên loại trừ fundamentals, hồi V-shape breadth lành ~1 tuần). Toàn chuỗi 4 job (2009/2020-2022/2012/top+margin) research-only ĐÓNG HẲN, không wire gì. Framework (B) phân biệt margin-forced vs fundamentals có thể feed vào crisis_margin_framework_adaptive_20260825.md nếu user muốn mở lại sau.
- [2026-08-31T05:19:39Z] 31/08 (tiếp 2): job Taylor_20260831_050908 áp lại framework margin-forced vào 2022+2018 XONG. Cả 2 giả thuyết user đúng MỘT PHẦN: 2022 = margin-cascade LỒNG trong khủng hoảng niềm tin rộng hơn (4 cụm quanh Tân Hoàng Minh/SCB/rate-hike/call-margin, breadth jump 33-40pp MẠNH HƠN 07/2026, nhưng external_flag FAIL cả 4/4 — VIX 22-35, SPX dd tới -25%); 2018 = front-loaded acute leg (23/04-22/06, ĐỦ 3/3 flag y hệt 07/2026, biến động còn MẠNH HƠN) rồi grind gradual 76% thời lượng còn lại KHÔNG có cluster nào. Phát hiện mấu chốt: bản thân 'có cluster margin-cascade' KHÔNG phân biệt được case an toàn vs khủng hoảng sâu — phải kết hợp external_flag TẠI THỜI ĐIỂM + ĐIỀU GÌ XẢY RA SAU cluster (V-recover vs tiếp tục suy yếu). Framework cập nhật 3 archetype: pure-margin-contained(07/2026)/front-loaded-then-grind(2018)/cascade-nested-in-crisis(2022). Research-only, đóng hẳn. Report: agents/Taylor/research/vn_2022_2018_margin_signature_recheck_20260831/.
- [2026-08-31T05:41:37Z] 31/08 (tiếp 3): job Taylor_20260831_053055 kiểm định giả thuyết mean-reversion-theo-prior-trend user đề xuất — BÁC BỎ như quy luật chung. 07/2026 và 2018 GIỐNG HỆT NHAU trên mọi thước đo prior-trend (12mo return 48%/65%, uptrend liên tục 1,3/1,8 tháng) nhưng outcome ĐỐI LẬP (07/2026 hồi nhanh nhất, 2018 không hồi được) — bác bỏ trực tiếp claim user về 2026='nền bình thường' (thực ra prior-trend CAO tương đương 2018, không hề yếu). Claim về 2020 COVID='đã đè nén từ 2018' thì ĐÚNG, thậm chí đúng rõ hơn (từ đỉnh 2018 tới đỉnh trước COVID: -17,68%, yếu nhất 6 case). Correlation N=6 vẻ ngoài ủng hộ (Pearson -0,805) sụp đổ khi bỏ 1 outlier (2007-2009) về +0,019 — driven-by-one-point, không phải bằng chứng thật. Giả thuyết chỉ đúng ở 2 đầu cực trị phân phối (đã có lời giải thích tốt hơn: external-shock-sạch, STRUCTURAL-credit, cascade-nested), MÙ hoàn toàn ở vùng giữa (nơi cần phân biệt nhất, chứa cả case tốt 07/2026 lẫn xấu 2018). LEAD-6 đề xuất (ngưỡng ~120-130% cumulative-từ-đáy-trước) chỉ N=2, yếu, KHÔNG thay 3-archetype framework. TOÀN BỘ chuỗi 6 job research crisis-trigger (2009/2012/2020-2022/top-margin/2022-2018-recheck/prior-trend) ĐÓNG HẲN 31/08, research-only, không wire gì vào production.
