# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 12/11 → 13/11
- Retro 12/11 ghi xong (kb/incidents/retro/retro-2026-11-12.md). Escalation đang chờ user, KHÔNG mở trùng: Wags/fleet-backup-gh001-history-rewrite (A filter-repo rewrite master + bundle backup / B khác; Wags khuyến nghị A) + wags-arch-review-round2-unresolved. Backup mike-fleet remote kẹt fc5bd02d (GH001 file >100MB, KHÔNG phải PAT); main workspace backup OK. Nhắc user trả lời A/B.
- Nghiên cứu live-gap BAL/LAG (kb/projects/bal-lag-live-gap-findings-20261112.md): GĐ0-GĐ2b xong, skeptic REFUTED các vòng nhưng null lõi đứng (0 đặc trưng qua FDR). GĐ3 Taylor_20261112_132954 xong, đang/đã skeptic → cập nhật KB mục GĐ3 + tổng kết cuối + báo user. Không dispatch vòng 3 nếu REFUTED.
- Chờ user quyết 3 việc: re-pin R3 / merge vá sort (pin vá 23,60% vs 23,37%, KHÔNG tự re-pin); dòng so sánh vs tiết kiệm trong báo cáo; merge LAG cache.
- DD VCP xong 12/11 (PDF đã đính, CHƯA gửi email — chờ user nói 'gửi email' → send_dd_report_email.py 1 lần).
- User duyệt KHÔNG bật cổng edge-health tháng BAL (NO-GO, đóng).
- Open cũ: đối soát fill VGS 11/11 (ATC oid 232411/232401 "New" sau 14:55); anomaly-flags-stale, bg-dispatch-wakeup-miss chờ user; lệnh đối ứng cùng mã chưa có guard.
- Wakeup MISS 0/9 hôm 12/11 (ngày thứ 2 liên tiếp) — theo dõi.

- [2026-11-12T17:49:42Z] [13/11 00:52] B xong (feat/savings-row-20261112 @9246cd93e, chưa merge); skeptic B job quant-skeptic_20261112_174928 đang chạy. Sau đó: tổng hợp 4 việc chờ user + đề xuất A vòng 2 (NULL Volume_3M_P50) + C chưa chạy.
- [2026-11-12T17:54:33Z] [13/11 00:57] Skeptic B CONFIRMED. Đã báo tổng hợp NT: chờ user quyết (1) merge A1 mergesort, (2) re-pin (đề xuất không), (3) LIQ_ZERO_BLOCK default (hoãn, A vòng 2), (4) neo sizing, (5) dòng tiết kiệm + Wendy thuế; C chưa chạy. Không còn job mở.
- [2026-11-12T18:12:24Z] [13/11 01:25] USER DUYỆT cả 5 đề xuất + luồng C. Xong: A1 mergesort merged main f210c726b (không re-pin, giữ neo -25,2%). Dispatch: A2 Taylor_20261112_181209 (opus), B2 Taylor_20261112_181211 (sonnet). Đang làm: Wendy (thuế + diễn đạt 'thua tiết kiệm'), C = arch-reviewer rồi quant-skeptic nhánh feat/lag-cache-adjusted-20261110 (+feat/repin-mirror-live-20261110; KHÔNG merge trước reviewer; apply LAG cache đổi 4 mã rời/7 mã vào). LIQ_ZERO_BLOCK default HOÃN chờ A2.
- [2026-11-12T18:21:55Z] [13/11 01:35] C: arch-reviewer = NEEDS_CHANGES; LAG cache ĐÃ merge main 97b2a7197 + đã apply cache từ 10-11 (tự kiểm: commit trên main, .pre_adj 11-10). Đã ghi đính chính vào kb/projects/lag-cache-adjusted-20261110.md. Chờ user: phê chuẩn hay rollback; nếu phê chuẩn → sửa validate Price/Volume_3M_P50 (lagged_cache_adjusted.py:126), runbook rollback, sửa cron_registry.md:89. Wendy: lãi tiền gửi miễn TNCN (Luật 109/2025 Đ4.6, hiệu lực 01/07/2026); thuế bán 0,1%/cổ tức 5% có thể đã nằm trong TWR cần kiểm; CCTG miễn thuế CHƯA xác minh; cờ cấp phép Đ12.4/Đ73 (SpaceX nhận vốn NĐT ngoài). Cần kiểm nav_period_returns đã tính thuế chưa trước khi chọn nhãn.
