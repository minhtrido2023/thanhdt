# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Margin đơn mã discretionary — LIVE, PB-adaptive WIRED (đóng hoàn toàn)
- Per-name 5% / sleeve 10% NAV, f≤1.3, %ADV≤10%, exit -20%. Commit 022c48e7.
- Phễu candidate WIRE (cutoff=70%, trần=1.2), commit 714b5889. TV1/DGC lọt nhưng marginable=NO qua DNSE hiện tại.

## Retro 2026-09-03 — XONG, có việc cần theo dõi
kb/incidents/retro/retro-2026-09-03.md, commit d9589e2e. 3 sự cố: (1)+(2) `preflight_check.sh`
§5 rồi §3 false-warn "dữ liệu cũ" trong kỳ nghỉ Quốc khánh 31/08-02/09 — cả 2 cùng lỗi đo ngày
lịch không biết lễ, vá cách nhau vài giờ CÙNG buổi sáng 09-03 (đã fix cả 2, commit 0b83f507 +
81cc0428). Pattern 1 mới: 1 file checker có nhiều nhánh cảnh báo có thể lặp cùng lỗi thiết kế —
CHƯA đủ 2 lần retro để escalate, chỉ đề xuất quét `mike/bin/*.sh` tìm ngưỡng ngày-lịch tương tự.
(3) arch-reviewer NEEDS_CHANGES (05:57Z) cho Wags: Wags đã báo SAI cho user rằng ack deposit-rate
sẽ "tự nổi lại trước cron DCF 09-11" (cơ chế thật: ack vĩnh viễn, suppress_days trơ vì cron tháng).
**CẦN LÀM: kiểm tra Discord Trading Daily xem đã đính chính với user chưa** — chưa thấy bus event
xác nhận tính đến 2026-09-04 00:30 ICT. Nếu chưa đính chính, phải làm trước 2026-09-11 (cron DCF
kế tiếp) kẻo claim sai bị lộ bằng thực tế. Bus question `Wags/wags-fix-not-confirmed:
coord-2026-09-03` (0d tuổi, chưa overdue) đang theo dõi việc này — đừng mở question thứ 2.
Wags CONFIRMED (không gap) khi verify draft.

## Vận hành — không có việc treo khác
Không circuit breaker trip, không pending_resumes. 2 bus question mở (cả 2 mở trong ngày 09-03,
0d tuổi, không overdue): Wags/wags-fix-not-confirmed (xem trên), Winston/deposit-rate-refresh-question.

## Macro watch
Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Review quý next ~2026-11-26.

## Mania research (Taylor, chuỗi đang mở)
2026-09-03: top-detection-technical-signals, mania-exit-reentry-roundtrip-verdict,
mania-quality-tilt-verdict — 3 finding mới ghi bus, chưa tổng hợp thành kết luận wire/no-wire.
Research-only, chưa đổi gì production.

- [2026-09-03T10:32:16Z] ARIA (Automated Research & Intelligence Analytics) = tên vận hành chính thức của hệ thống, duyệt 2026-09-03. Dùng trong email gửi nhà đầu tư bên ngoài. Wire: render_report_html.py header + footer (commit fb5caaba worktree session/1522576692638388364).
- [2026-09-03T18:03:54Z] Value-trap follow-up ĐÓNG (job Taylor_20260903_174422, 2026-09-04). Khoảng trống CÓ THẬT: custom_basket.py:945 gate chỉ đọc fa_ratings_8l.rating<=3, KHÔNG đọc ROE_Min3Y/CF_OA_3Y (golden floor); call site lag_dnpr_harness.py:663/686/707. rating_8l.py:398 tác giả CỐ Ý không hard-gate ROE_Min (quyết định user 2026-06-02). NHƯNG thêm golden floor = NULL: FULL −0,44pp, OOS −2,08pp, DSR 0,361 (RED FLAG), LOO dao động −34..+4pp. Cơ chế: gate rating<=3 đã loại sẵn phần lớn value-trap thật (TLH/HSG/MHC/TVB/PLP/HHG hầu hết rating 4-5; HSG còn nằm BANNED list). Capacity KHÔNG phải nút thắt (median 397 tên vs cần 30). KHÔNG wire. Củng cố tiền lệ QF8-NEU NO-GO 2026-07-12 nhưng sạch hơn (giữ nguyên bề rộng rổ).
- [2026-09-04T05:07:29Z] Adaptive-exclusion architecture (job Taylor_20260904_043943, 2026-09-04) — ĐỀ XUẤT THIẾT KẾ, chưa wire, chờ user + quant-skeptic. Phát hiện kiến trúc LỚN: BANNED KHÔNG nằm trong custom_basket.py (engine backtest) — chỉ bind ở compute_park_trim.py:427-434 (LIVE-only patch Mike thêm 2026-08-07) + lag_forensic_filter.py (LAG). ⇒ R3 pin 28,86% ĐÃ bao gồm mã BANNED khi chúng lọt gate ⇒ gỡ BANNED KHÔNG đổi số pin. Audit: 9/16 mã (KSF,NVL,VJC,VVS,GEG,IMP,TRA,TOS,VTP) chưa từng lọt top-30 dù bỏ ban ⇒ ban thừa. HSG bind THẬT 13/48 kỳ (27%), 10-11/13 lần lành mạnh ⇒ bị chặn OAN. Backtest: B(banned) −0,66pp vs A(không ban); C(gate động) −1,92pp FULL / −5,81pp IS / +2,32pp OOS, MaxDD tốt hơn (−37,1% vs −40,0%). Must-catch: gate động bắt ĐÚNG HVN equity âm 2025 + BAF dilution, tự cho HVN vào lại 2026-02 sau 2 quý sạch; KHÔNG bắt PC1 (gian lận, sạch trên mọi tỷ số tới ngày bị bắt 2026-05-15) và SBA (đòn bẩy thấp + IntCov âm). Bẫy kỹ thuật: BVPS≤0 phải check TRỰC TIẾP, KHÔNG dùng Debt/Eq>X (D/E đổi dấu ÂM khi equity âm — HVN D/E=−11,2). File: agents/Taylor/research/adaptive_exclusion_architecture_20260904.md
- [2026-09-04T05:57:55Z] Adaptive-exclusion v2 (job Taylor_20260904_054209, 2026-09-04) — user duyệt BANNED RỖNG HOÀN TOÀN (cả PC1: án cá nhân không ảnh hưởng công ty thì DD kỹ hơn, không ban). SBA catch của user ĐÚNG và lớn hơn tưởng: IntCov_P0 có mẫu số là chi phí tài chính RÒNG nên âm khi thu lãi > trả lãi ⇒ luật cũ (Debt_Eq>3,5 AND IntCov<1,5) gắn cờ SAI 67,6% (có lãi ròng dương). Đã sửa rule2 → EBITDA_P0<0, flag rate 15,64%→12,86%. Kịch bản D (BANNED rỗng + gate v2): CAGR 30,20% / Sharpe 1,30 / MaxDD −38,6% vs A(không lọc) 32,07%/1,29/−40,0%. Must-catch vẫn đúng HVN+BAF. Chi phí thả PC1 ≈ −0,84pp NAV sleeve (1 lần giữ, −25,34% giá, ước THÔ). Thiết kế: review_by=date+12th (leadership_investigation=3th), gắn ops_health_check.sh, FAIL-CLOSED khi quá hạn. DD kỹ hơn = fearbuy_weekly_scan WebSearch → forensic_flags severity=watch → dispatch fundamental-skeptic. CHƯA WIRE — cần quant-skeptic (đặc biệt verify ngữ nghĩa IntCov) + user duyệt. 7 điểm sửa liệt kê ở §5 v2 (gồm KNOWLEDGE.md:247 phải sửa đồng thời). File: agents/Taylor/research/adaptive_exclusion_v2_20260904.md
