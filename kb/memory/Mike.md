# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (2026-08-18T00:55Z)

## Đã xong hôm nay 08-18
- F1+F3 anti-double-reply: merge feat/mention-only-toggle vào main ccdb, restart service (commit 70d4b9c)
- gdkhq Option B: xoá auto-accept code path (commit 0f90f3d1); data/gdkhq_config.json không tồn tại
- UPCOM VWAP cron: cài 15 8 * * 1-5, cron_registry cập nhật (commit 5db3be84)
- Wags coord-2026-08-18: fix exit=5 fail-CLOSED + arch-review debt (commit e25f2a33, arch-review CONFIRMED)

## Arch-review xong — CLEAN
Cả 2 verdicts coord-2026-08-18 đã resolved:
- Verdict 1 (gdkhq): superseded bởi 0f90f3d1 + file không tồn tại
- Verdict 2 (rc=5 c9d1fa30): 4 changes apply bởi e25f2a33, CONFIRMED

## G5 UPCOM — kế hoạch
1. [DONE] Winston data_registry + script capture_upcom_vwap_eod.sh
2. [DONE] Cron installed: 15 8 * * 1-5 (15:15 ICT T2-T6)
3. Tích ≥3 phiên avgPrice history
4. Probe lại ≥3 lần; giải thích 6 mã UPCOM chưa khớp (VNE/MZG/VBB/SDA/AAV/DDG)
5. quant-skeptic + user final → wire G5 UPCOM

## VIX ex-date 08-20
Shadow TRONG PHIÊN 09:10-14:30 ICT 08-20.
G2 tolerance fix đã xong (max(1%, 1 tick)).
accept_shadow() sau PASS.

## Không có việc mở

