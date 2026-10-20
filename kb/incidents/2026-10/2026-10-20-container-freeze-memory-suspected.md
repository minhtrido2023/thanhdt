# 2026-10-20 — Container treo ~2,5h rồi reboot 22:23 ICT (nghi cạn RAM, CHƯA xác nhận kernel)

**Sự thật đo được**
- Môi trường: container LXC, 40000MB, KHÔNG swap, 34 core; `trido` không đọc được kern.log/dmesg/journal hệ thống ⇒ KHÔNG có dòng OOM-killer để trích.
- Log journald user dừng 19:55:42 ICT (12:55Z); Paseo daemon kẹt event-loop 16,4s ngay lúc đó; job `Taylor_20261020_122917` mất heartbeat 19:54; reboot 22:23.
- Lúc 19:47 ICT job đó mở 8 engine `pt_v23_audit_2014.py` song song (V1B+V1C) + `v2_replay.py`.
- Đo lại 4 engine cùng loại (20/10 22:54-23:02 ICT): đỉnh **3,23GB/engine** (cuối pha, tăng từ 1,3GB lên 3,2GB trong ~30s), tổng 4 engine 10,8GB, `used` hệ thống đỉnh 17,0GB; nền không có engine ~6,3GB.
- Ngoại suy 8 engine: 6,3 + 8×3,23 ≈ **32GB + page cache** trên trần 40GB, không swap ⇒ gần như không còn biên.

**Chưa xác nhận / không loại trừ**: container còn chạy dịch vụ của user khác (`hainguy+`: celery 36 tiến trình, mongod, grafana); host Proxmox có thể thiếu RAM do guest khác. Lần chạy lại 8 engine V1B/V1C lúc 22:34 vẫn sống ⇒ 8 engine MỘT MÌNH không chắc gây treo; cần log host.

**Phòng ngừa (tay Mike làm được)**: `bin/memcap.sh <GB> <cmd>` (cgroup MemoryMax cứng, không swap, vượt trần chỉ giết riêng lệnh đó — selfcheck `bin/memcap_selfcheck.sh`) và `bin/mem_slots.sh <GB/proc>` (số song song an toàn theo MemAvailable). **Cần root/host**: bật `earlyoom` (đã cài, inactive), cấp swap cho container, đọc `journalctl -k` trên host Proxmox quanh 19:55 ICT.
