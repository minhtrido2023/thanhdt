# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.
- Thứ Bảy 2026-08-29: implement code chính sách margin đơn mã discretionary.

## DC state-adaptive — CHỐT 26/08 (không còn job chạy)
- Tầng 1 XONG: dc_book_waterfall_paper.py v2.1 (DHG/MSH excluded, per-name caps 10 mã) + c1_shadow_paper.py (cron 00:20 ICT T3-T7 ĐÃ CÀI, commit 82548b82).
- C1 live-25% REFUTED bởi quant-skeptic (high) — BLOCKED. Mở lại chỉ khi: rolling 3-4 IS/OOS windows + shadow đủ dài (mục tiêu ≥60 phiên BULL forward) + caps cưỡng chế trong allocator + skeptic pass MỚI. Checkpoint 2027-03-31.
- CRISIS: DC universe (hygiened) = candidate basket cho crisis sleeve Loại-2 (escalation-based).

## KHẨN — security leak CHƯA đóng hẳn (>18h)
- Số tài khoản DNSE THẬT lộ public GitHub minhtrido2023/thanhdt. Phần push fix (commit c1303a96, 3d358b14) ĐÃ lên origin/main (xác nhận 08-25 retro) — nhưng bus question `retro-2026-08-24-security-leak-github-public-repo-and-sudo` (mở 06:10:59Z 08-25) vẫn CHƯA có answer.
- 2 hạng mục còn cần user quyết: (1) làm repo private/rewrite-history, (2) thu hồi sudo của hainguyen/hungle/namiq — CHƯA verify được (bị tool-classifier chặn đọc /etc/sudoers.d).
- Đừng mở question thứ 2 trùng — nhắc lại đúng topic cũ.

## Retro 2026-08-25 — đã đóng
- kb/incidents/retro/retro-2026-08-25.md: 3 sự cố (host-downtime checker — đã sửa cùng ngày; job "cancelled" sai nhãn dù verdict đã lên bus qua job song song — MỚI, chưa điều tra vì sao dispatch trùng; bus question security-leak treo). Wags verify GAPS FOUND → đã sửa đúng cơ chế trước khi ghi.

- [2026-08-26T05:24:22Z] 2026-08-26: Bobby report rủi ro BĐS VN xong (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Thesis+playbook chốt ở kb/projects/vn-realestate-structural-risk-20260826.md. Review quý next ~2026-11-26 (dispatch Bobby refresh lead indicators). Đang audit RE-exposure bank trong danh mục (MBB/ACB/HDB).
