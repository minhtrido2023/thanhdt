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
  qua DNSE hiện tại. Hard cap concentration risk KHÔNG implement (user chốt: DD workflow đủ).

## CAP_SIGNAL advisory — KHÉP KÍN HOÀN TOÀN 2026-08-30
- Chuỗi đầy đủ: nghiên cứu (DIVERGE-only NO-GO, CAP_SIGNAL composite dương) → quant-skeptic
  round 1 REFUTED (grid không tái lập, nhãn FP sai, cluster mỏng) → round 2 sửa đủ 4 điểm →
  quant-skeptic CONFIRMED medium (N=6 cụm macro độc lập/15 năm, quá mỏng để wire kỹ thuật) →
  user duyệt dùng advisory tham khảo, tự tích luỹ case, tự đề xuất nâng cấp khi N≥10 → implement
  script `agents/Taylor/cap_signal_advisory_check.py` (nguồn sống: VNI/BQ + EEM/DXY/TNX/yfinance
  qua $DNA_PYEXE) → wire hiển thị:
  - Daily (tự động): `dna_report.py::build_cap_signal_advisory_line()` → `mike/bin/
    eod_trading_report.sh` (dòng 136-139, prefix 🧲). Verify trực tiếp trong file — CÓ THẬT.
  - Weekly/monthly: không pipeline tự động, checklist tường minh trong project doc cho Taylor.
  - Bug bắt được trước khi ship: python3 hệ thống thiếu yfinance, phải chạy riêng qua $DNA_PYEXE
    subprocess (nếu chung khối python3 -c với DT-gate/Value-Radar sẽ lỗi âm thầm mãi mãi).
  - Ngưỡng nâng cấp N≥10 cụm — đạt thì script tự bus question đề xuất quant-skeptic+user review,
    KHÔNG bao giờ tự wire vào production thật.
  - Không đụng file trading production nào (xác nhận qua git status).
  Toàn bộ quyết định: `kb/projects/cap-signal-advisory-20260830.md` (đủ §1-4).
- **KHÔNG còn việc gì treo lại ở chuỗi này.**

## Chuỗi khủng hoảng cơ cấu 2007-2012 + điểm mù 2018 — ĐÓNG HOÀN TOÀN
- Hướng 1 (valuation-gated tier-unlock): NO-GO, capacity chặn (60-79% episode thiếu ADV, edge đảo
  âm ở ngưỡng ≥10B/ngày). File: valuation_gated_tier_unlock_round2_20260830.md.
- Hướng 2 (DIVERGE CAP_SIGNAL): xem mục CAP_SIGNAL advisory trên — đã khép kín hoàn toàn.
- Episode clustering N=7->N=5, stress-test DT5G Phase A/B, Bobby BLIND read 2009/2018 — tài liệu
  tham khảo, không đổi production. DT5G giữ nguyên "bảo hiểm fail-safe", không re-tune lịch sử.

## Chuỗi R&D 30/08 khác — đóng
- custom30V accrual-quality: 3/3 phép thử NO-GO. Sector sweep: đóng, coverage 20/20.
- C1 (DC-swap): củng cố REFUTED. Insider cluster-buy: NO-GO.
- Audit 8L thresholds: KHÔNG cần adaptive mới. NPL/CAR: giữ proxy ROE_Min3Y/Gordon-PB.

## Vận hành — dọn sạch 30/08, không còn việc treo cũ
- job quant-skeptic_20260830_085357: OVERDUE cosmetic (không sửa được), đã verify substance qua
  log trực tiếp — biết, bỏ qua.
- capit-lever selfcheck 2, retro-pattern checker hardcode: đã CLOSED từ 08-28.
- dt5g-writer-la-1931: điều tra ra + đóng.

## Macro watch
- Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Review quý next ~2026-11-26.

