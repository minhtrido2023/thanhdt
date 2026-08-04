---
kind: incident
status: fixed (monitoring); production-code fix in progress (Taylor job Taylor_20260804_094514)
severity: medium — no real capital, but 8 trading days of R&D evidence lost + a monitoring fix
  regressed into the exact failure class it was built to prevent
date: 2026-08-04
---

# `net_offsetting_orders()` silently zeroed paper-main evidence for 8 days — a monitoring fix I
# shipped 2026-08-03 is what suppressed the alert

## Chuyện gì xảy ra

Account paper `main` tồn tại DUY NHẤT để sinh evidence cho 3 chương trình paper (EXTREME-regime
gate, vol-scale chase-cap, fill-timing) — mỗi ngày SELL toàn bộ vị thế hôm qua + BUY LẠI đúng
basket 6 mã (FPT/MBB/ACB/HDB/VNM/HPG). Khi `net_offsetting_orders()` được wire LIVE vào
`bot_execute.py` (commit `ab20a77`, 2026-07-27), nó gộp lệnh SELL+BUY đối chiều CÙNG mã thành 1
lệnh NET — và vì probe basket luôn SELL rồi BUY LẠI đúng cùng mã cùng giá trị, net gần như luôn
về **0**, tức 0 lệnh thật ra broker từ **2026-07-28**. Evidence cho cả 3 chương trình đứng yên
**8 ngày liên tiếp** (07-28 → 08-04) mà không ai biết, cho tới khi Taylor tự đào sâu lúc làm
checkpoint review hôm nay (job `Taylor_20260804_091700`/`091703`, dispatch từ
`paper_checkpoint_escalation.sh`).

## Vì sao không ai biết — chính là root cause user hỏi ("chết lỗi không ai biết")

`paper_main_early_check.sh` (cron 3 lần/ngày, chạy 30' sau mỗi cron executor) được XÂY CHÍNH ĐỂ
bắt đúng loại lỗi này (root sự cố gốc 07-08/09: ghost-guard/TZ bug, 0 lệnh 2 ngày liền không ai
biết). Nhưng **2026-08-03**, tôi (Mike) sửa nó theo đúng feedback của user hôm đó ("hôm nay
paper-trading đều báo cáo lỗi không có giao dịch. Tại sao?") — phát hiện netting khiến journal
không tồn tại một số ngày, kết luận đó là **hành vi ĐÚNG thiết kế** (run_bot's own log tự xác nhận
"không phải lỗi, chỉ là ngày không giao dịch") và cho script **im lặng hoàn toàn** khi gặp case
đó.

Kết luận "đúng thiết kế" đó **đúng cho một tài khoản THẬT** (SpaceX/ZaloPay có thể hợp lệ có ngày
0 lệnh — không phải mọi ngày đều có deal). Nhưng **SAI cho account `main`** — nó không phải tài
khoản thật, mục đích DUY NHẤT của nó là sinh evidence mỗi ngày; "netted về 0" với account này
LUÔN có nghĩa "hôm nay 0 evidence", không bao giờ là chuyện bình thường. Bản sửa 08-03 đã khiến
chính cơ chế được xây để bắt "lỗi im lặng" trở thành công cụ IM LẶNG cho đúng loại lỗi đó — một
bug mới đội lốt bug fix, cùng thời điểm với gốc sự cố netting (07-27→07-28) nên có cửa sổ ngắn
lỗi cũ (RED giả) chồng lấp lỗi mới (im lặng thật) — dễ nhầm là "đã xử lý xong".

## Phát hiện + đo tác động thật

- Taylor (checkpoint review job, không phải do early-check báo): `grep` journal thực tế —
  07-28/07-29/08-03 KHÔNG TỒN TẠI; 08-04 chỉ 1 lệnh dư 100cp MBB do làm tròn (không phải basket
  đầy đủ). Số "155 placement"/"18 phiên journal" mà `paper_programs_daily_report.py` hiển thị mỗi
  ngày là số ĐÔNG BĂNG tới 2026-07-27, không phải evidence mới — báo cáo daily không tự phát hiện
  vì nó chỉ hiển thị trạng thái tích lũy, không so sánh với ngày hôm trước.
- Ảnh hưởng: EXTREME-regime (15/20 phiên, lẽ ra đã gần 23/20 nếu không đứng yên), vol_scale_chase_cap
  (13/10 — đủ ngưỡng nhờ tích lũy TRƯỚC 07-28, may mắn không phải nhờ theo dõi đúng), fill_timing
  (checkpoint 07-31 đã trôi qua trong lúc evidence đứng yên — góp phần trực tiếp vào lý do user hỏi
  "sao vẫn treo mà không có đánh giá gì" sáng nay).

## Fix

1. **`paper_main_early_check.sh`** (commit theo sau) — bỏ nhánh im lặng hoàn toàn cho case
   netted-về-0 của account `main`. Thay bằng streak-aware: ngày đầu = ⚠️ WARN (không đủ để gây mệt
   mỏi cảnh báo giả 1 lần — user vừa phàn nàn về false RED 08-03), streak ≥2 ngày liên tiếp = 🔴
   RED (không còn là ngẫu nhiên). Streak lưu `state/paper_main_zero_evidence_streak.json`, reset
   khi evidence chảy lại. Verify: simulate streak logic cô lập (idempotent trong ngày, tăng đúng
   qua nhiều ngày, reset đúng) + chạy thật trên dữ liệu hôm nay (exit 0, healthy path đúng vì
   08-04 có 1 fill thật).
2. **Gốc netting** — dispatch Taylor (job `Taylor_20260804_094514`) sửa `paper_main_probe_plan.py`
   (KHÔNG đụng `trading_bot/plan.py`/`bot_execute.py` — netting production giữ nguyên, đúng cho
   tài khoản thật) để basket hàng ngày luôn còn ≥1 lệnh thật sau khi qua `net_offsetting_orders()`.

## Bài học tổng quát (quan trọng hơn vụ việc cụ thể)

**Một check phân biệt "lỗi thật" vs "hành vi đúng thiết kế" phải phân biệt ĐÚNG THEO TỪNG LOẠI TÀI
KHOẢN, không dùng chung 1 kết luận cho mọi account chỉ vì cùng cơ chế kỹ thuật (netting) gây ra
cùng triệu chứng (journal thiếu).** "Đúng thiết kế" là một câu hỏi phụ thuộc NGỮ CẢNH của account
(tài khoản thật có thể hợp lệ 0 lệnh; tài khoản evidence-only thì không) — không phải một thuộc
tính của riêng cơ chế kỹ thuật đang được quan sát. Khi sửa 1 false-positive, luôn tự hỏi: "điều
kiện tôi vừa thêm để im lặng có ĐÚNG CHO MỌI NGỮ CẢNH sẽ gặp case này không, hay chỉ đúng cho case
tôi vừa thấy?" — nếu không chắc, thiên về WARN/streak thay vì im lặng hoàn toàn (giữ được tín hiệu
mà không gây mệt mỏi cảnh báo).

## Tham chiếu

- Sự cố gốc (RED giả 08-03): bản sửa cũ trong `git log -p -- mike/bin/paper_main_early_check.sh`
  (commit ngày 2026-08-03).
- Checkpoint review phát hiện: bus finding `fill-timing-checkpoint-2/5-PASS-BLOCKER-netting-giet-evidence`,
  `checkpoint-vol-scale-chase-cap-gate4-BI-CHAN-CAU-TRUC` (job `Taylor_20260804_091700`/`091703`).
- Netting commit: `ab20a773b978d8c280399ed6f12c645f6b14b235` (2026-07-27).
- Fix netting-exemption: job `Taylor_20260804_094514`.
