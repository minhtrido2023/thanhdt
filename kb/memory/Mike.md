# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Margin đơn mã discretionary — LIVE, PB-adaptive WIRED (đóng hoàn toàn)
- Per-name 5% / sleeve 10% NAV, f≤1.3, %ADV≤10%, exit -20%. Commit 022c48e7.
- Phễu candidate WIRE (cutoff=70%, trần=1.2), commit 714b5889. TV1/DGC lọt nhưng marginable=NO qua DNSE hiện tại.

## Retro 2026-08-31 — XONG
kb/incidents/retro/retro-2026-08-31.md, Wags GAPS FOUND (off-by-one đếm event, đã sửa)
+ CONFIRMED phần còn lại. 1 sự cố: bus question giả từ dev-test buggy của
vn_realestate_monthly_check.py (mới wire 08-31, commit 8a01d08f) — đã đóng bằng
close_bus_question.py, decided_by=agent. 0 pattern xuyên suốt mới.

## Vận hành — không có việc treo
Không circuit breaker trip, không pending_resumes, không bus question mới mở.

## Macro watch
Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Interim monthly check
tự động hóa xong 08-31 (commit 8a01d08f), cron 20:00 ICT ngày 6 hàng tháng. Review quý
next ~2026-11-26.

## Chuỗi crisis-trigger research (30/08-31/08) — ĐÓNG HOÀN TOÀN
Research-only, không wire gì production. Framework 3-archetype margin-forced/fundamentals
+ rational-vs-overreaction (chỉ 1/11 case overreaction rõ). EP-2026-01 imbalance BĐS/tín dụng
xác nhận không-blind bằng Q2/2026 thật: độ tin cậy lặp mẫu 2011→2012 VỪA PHẢI (chuỗi nhân quả
đúng nhưng độ lớn nhỏ hơn 1 bậc, mới 2 quý data). KHÔNG đổi playbook margin/derisk đã chốt
26/08. Chi tiết: agents/Taylor/research/vn_*_20260831/, kb/projects/vn-realestate-structural-risk-20260826.md.

