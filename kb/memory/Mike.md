# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Margin đơn mã discretionary — LIVE, PB-adaptive WIRED (đóng hoàn toàn)
- Per-name 5% / sleeve 10% NAV, f≤1.3, %ADV≤10%, exit -20%. Commit 022c48e7.
- Phễu candidate WIRE (cutoff=70%, trần=1.2), commit 714b5889. TV1/DGC lọt nhưng marginable=NO qua DNSE hiện tại.

## Chuỗi khai thác DC alpha — 30/08 → 31/08, ĐÓNG HOÀN TOÀN
Không mechanism nào wire. Kết luận: alpha có thật ở BULL nhưng không NEUTRAL; hướng khả thi = LENS/feeder (đã implement, mike/bin/dc_candidate_feeder.py) + paper mở rộng BULL/EXBULL. Review ~06/10.

## CAP_SIGNAL advisory + khủng hoảng cơ cấu 2007-2012 — KHÉP KÍN (30/08)
Wire cả 3 cadence, ngưỡng nâng cấp N≥10. kb/projects/cap-signal-advisory-20260830.md.

## Retro 2026-08-30 — XONG
kb/incidents/retro/retro-2026-08-30.md, Wags CONFIRMED.

## Vận hành — không có việc treo
Không circuit breaker trip, không pending_resumes, không bus question mới mở.

## Macro watch
Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Review quý next ~2026-11-26.

## Chuỗi nghiên cứu crisis-trigger 31/08 — ĐÓNG HOÀN TOÀN, 8 job Taylor + Bobby blind 11 episode
Research-only, không wire gì vào production. Kết luận cuối (job Taylor_20260831_070702,
vn_rational_vs_overreaction_framework_20260831/REPORT.md):
- **KHÔNG phải "thị trường luôn overreact"** — chỉ 1/11 case overreaction rõ (EP-2025-03 tariff
  Liberation Day: breadth panic 80,05% CAO NHẤT 11 case dù Bobby xếp KHÔNG nặng), 1 nhóm
  underreaction cường độ (Wave2/3 STRUCTURAL 2009-2012: case nặng nhất nhưng breadth panic đỉnh
  THẤP vì xói mòn dần không capitulate 1 lần — washout-gate chỉ dựa %oversold sẽ BỎ LỠ dạng này),
  case chuẩn "rational" = EP-2014-09 (giá dầu OPEC, cả 3 trục đồng thuận nhẹ).
- 3-archetype framework margin-forced/fundamentals (job vn_2022_2018_margin_signature_recheck):
  pure-margin-contained(07/2026) / front-loaded-then-grind(2018) / cascade-nested-in-crisis(2022).
  Phải kết hợp external_flag TẠI THỜI ĐIỂM + ĐIỀU GÌ XẢY RA SAU cluster, không chỉ nhìn có cluster.
- Giả thuyết mean-reversion-theo-prior-trend BỊ BÁC BỎ (07/2026 và 2018 giống hệt input, outcome
  đối lập). Giả thuyết breadth-of-rally CÓ 1 phần đúng (participation 2026 hẹp, 57,1% mã âm YTD)
  nhưng cơ chế cụ thể "nhóm đầu tư công kéo chỉ số" BỊ BÁC BỎ bằng ICB_Code thật (nhóm này thực ra
  KÉM hơn thị trường 2026; nhóm này dẫn dắt thật là 2022). Thủ phạm thật kéo VNINDEX 2026 nghiêng
  dầu khí PVN + mega-cap — quan sát phụ chưa kiểm định.
- EP-2026-01 (mới, Bobby blind) là episode MIXED duy nhất — imbalance tín dụng/BĐS thật tích luỹ
  12+ tháng, breadth panic đi TRƯỚC đáy giá 14 ngày (giống mẫu STRUCTURAL). Nối với 07/2026: panic-
  oversold cho thấy 2 episode TÁCH BIỆT thật (7-8 tuần calm thật ở giữa), nhưng participation-breadth
  cho thấy nhịp hồi 03-05/2026 HẸP — giả thuyết mở, cần dispatch macro-strategist KHÔNG-BLIND riêng
  mới xác nhận được liệu imbalance BĐS/tín dụng có đang ẩn dưới rally hẹp không.
- Không đề xuất chỉ báo mới vào production. Muốn dùng "đỉnh breadth panic %" chính thức cần dispatch
  riêng formalize + quant-skeptic review.
- Toàn bộ 8 report: agents/Taylor/research/vn_{2009,2012,2020_2022,top_divergence_and_margin_selloff,
  2022_2018_margin_signature_recheck,prior_trend_meanreversion_hypothesis,breadth_of_prior_rally,
  all_corrections_inventory,rational_vs_overreaction_framework}_20260831/

- [2026-08-31T07:45:56Z] 31/08 (cuối): xác minh KHÔNG-BLIND imbalance EP-2026-01 bằng dữ liệu Q2/2026 thật (theo yêu cầu user sau chuỗi crisis-trigger research) - CHƯA xử lý căn cơ. BĐS tăng tốc không hạ nhiệt (Q1 +11,7% QoQ -> Q2 +12,71% QoQ), SBV 30/05/2026 ra biện pháp NỚI (loại NOXH/KCN khỏi công thức tính) chứ không siết thêm - không có Nghị quyết 11/2011-style hay Quyết định 254/2012-style nào ban hành sau Q1. NPL xấu đi rõ nhất: 1,72%(2025)->1,85%(Q1)->1,93-1,97%(Q2, cao nhất từ 2020), coverage ratio rơi 91,65%->84,5%. CPI là điểm sáng duy nhất: đỉnh 5,60%(T5)->4,69%(T6) đã đảo chiều. Độ tin cậy giả thuyết lặp mẫu 2011->2012: VỪA PHẢI (đúng chuỗi nhân quả định tính nhưng độ lớn tuyệt đối nhỏ hơn 1 bậc - NPL 1,97% vs 17,21%; CPI đỉnh 5,6% vs 23% - và mới 2 quý data, quá ngắn xác nhận mẫu đa năm). Khuyến nghị Bobby: KHÔNG đổi playbook margin/derisk đã chốt 26/08, đây là cập nhật giữa kỳ theo dõi (review quý gốc vẫn 26/11, đẩy sớm nếu Q3 xấu thêm). File cập nhật: kb/projects/vn-realestate-structural-risk-20260826.md (mục Interim status check mới, KHÔNG sửa entry BLIND gốc trong vn_macro_regime_history.md). Kế hoạch dự phòng Mike đề xuất: giữ nguyên CAP_SIGNAL tripwire đã wire, không mở rộng margin cho đợt giảm mới nếu xuất phát từ đúng nguồn gốc này (vẫn MIXED/ambiguous, escalate không tự quyết).
- [2026-08-31T07:57:59Z] 31/08: đã chốt + ghi vào kb/projects/vn-realestate-structural-risk-20260826.md (commit 3c03ea57) cadence review MỚI theo yêu cầu user: (1) review quý neo theo mùa BCTC đã công bố xong (không ngày cố định) - Q3->cuối 10/đầu 11, next 2026-11-26 vẫn khớp; (2) review THÁNG interim MỚI - CPI + lãi suất huy động Big-4 + tin chính sách, escalate ngay nếu CPI relapse qua 4,5% / lãi suất +0,3pp trong 1 tháng / có thông tư SIẾT mới / NPL-bankrun tin ngoài chu kỳ. Hiện CHƯA có cron tự động (thủ công qua Mike nhắc mỗi đầu tháng) - đề xuất dispatch riêng để build+test cron+escalation cơ học nếu user muốn tự động hoá. NHỚ TỰ NHẮC kiểm tra đầu mỗi tháng (dispatch Bobby non-blind, mẫu prompt xem interim check 31/08).
