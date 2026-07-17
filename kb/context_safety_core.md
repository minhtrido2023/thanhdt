# Mike fleet — safety core (bắt buộc với MỌI agent chạm surface tiền thật)
> File nhỏ, cố ý KHÔNG trùng nội dung với context_execution_mini.md / context_planning_mini.md /
> context_dataops_mini.md — 3 file đó chứa phần chuyên biệt theo vai trò; file này chứa phần
> AI CŨNG PHẢI biết bất kể vai trò, để tránh lệch/thiếu khi có nhiều bản sao. Sửa 1 fact ở đây =
> sửa đúng 1 chỗ cho mọi agent import nó (Mafee, DollarBill, Taylor qua context_pack.md).

## Kill-switch
- **`data/BOT_STOP`** (tạo file, ở root `WorkingClaude`) = dừng MỌI giao dịch tức thì, mọi account.
- **`mike/state/NOTIFY_OFF`** = tắt Telegram push tạm thời (không ảnh hưởng giao dịch).

## BANNED tickers vĩnh viễn (không bao giờ mua, bất kể signal)
PC1, VVS, KSF, NKG, HSG, HVN, VJC, NVL, GEG, SBA, DMC/IMP/TRA, TOS, VTP.

## Human-in-the-loop — không đảo thứ tự
Taylor (đặt rule/`trading_rules.json`) → DollarBill (lập plan, **user duyệt**) → Mafee (chỉ thực thi
đúng plan đã duyệt, KHÔNG tự nghĩ/chế lệnh). Thay đổi rule áp vào LIVE luôn cần user duyệt.

## 2 tài khoản LIVE hiện tại (2026-07-17)
- **SpaceX** — DNSE `0002023347`, có margin, live từ 2026-07-01.
- **ZaloPay** — DNSE `0001743768` (tên cũ `dnse_main`), **cash-only** (không margin), live từ
  2026-07-06. Có `excluded_tickers: ["DGC"]` (vị thế legacy, hạn chế giao dịch HOSE + vụ án hình
  sự lãnh đạo — Taylor giữ vì lý do đầu tư, KHÔNG rebalance qua bot). Sizing chiến lược phải dùng
  `active_nav` (loại trừ excluded), không dùng total NAV — `bin/compute_active_nav.py --account X`.

## Idempotent side-effects (nguyên tắc, không phải chi tiết implementation)
Bất kỳ script nào gọi hệ thống ngoài có side-effect thật (đặt lệnh, gửi tin) phải chịu được bị
kill giữa chừng rồi chạy lại mà KHÔNG lặp hành động đó. Không chắc hành động đã xảy ra chưa →
fail-safe dừng + báo người, không tự đoán-rồi-gộp. Chi tiết đầy đủ: `kb/coding_guidelines.md` §5.
