# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (2026-08-17T19:04Z)

## G5 UPCOM — implementation plan (user đã duyệt)
Thứ tự bắt buộc theo Taylor roadmap:
1. [RUNNING] Winston (job Winston_20260817_190446): data_registry entry + EOD capture script
2. Tích ≥3 phiên avgPrice history (tự động sau khi cron wire)
3. Lặp lại probe ≥3 lần (rẻ, chỉ chạy lại script Taylor)
4. Giải thích nhóm 6 mã UPCOM chưa rõ (VNE/MZG/VBB/SDA/AAV/DDG) hoặc gate tường minh
5. quant-skeptic + user final approval → wire G5 activate cho UPCOM

## Wags audit (đã xong, đã replied)
Double-answer root cause THẬT: không phải 2 push độc lập (ccdb đã bỏ idempotency) — mà là:
(a) compaction/interrupt replay — is-replied PHÒNG ĐƯỢC nếu prompt encode Bước B
(b) restart giữa lượt (ccdb restart 4 lần 08-17) → _running set mất, row still due → replay
F1 (tầng ccdb, 1 dòng): cần user duyệt (repo claude-code-discord-bridge)
F2 (claim-reply atomic): Wags tự làm được
F3 (dedup_key ccdb): cần user duyệt
F4 (sửa MIKE.md §8 item 4): có thể làm ngay
F5 (fix wakeup_audit.py): Wags làm
F6 (log push success): Wags làm

## Đang chờ Winston xong → deploy cron → bắt đầu thu thập data
## VIX ex-date 08-20: shadow trong phiên 09:10-14:30 ICT, accept_shadow() sau đó

