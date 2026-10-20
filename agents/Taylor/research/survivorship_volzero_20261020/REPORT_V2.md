# REPORT V2 — Enumerate có hệ thống mã hủy niêm yết từ 2014 (EXPLORATORY)
Job Taylor_20261020_122917 → tiếp tục Taylor_20261020_153324. PREREG_V2.md md5 e04ceac3 (commit 102e40f12), verify khớp.
Không sửa pin/registry/pin_ledger/engine; không đề xuất đổi luật.

## Tập (data/v2_sets.json, rule-based)
U230 = 230 mã (1 thiếu file giá). Lỗi dựng: FPC (EmptyDataError) → loại. A = 151; M∩A = 14; **N = 136** mã mới; N_bat_buoc = 53.
BCTC: 93/136 mã N có `npat_parent` ≥1 quý; **43 mã không dựng được BCTC = GIỚI HẠN** (MID/LIVE không có lô ở các mã này).

## Kết quả MIX, cấu hình CHÍNH (cap 5% pha bơm/xả, exitval=nm) — ΔCAGR pp dải 4 chân (out_v2_summary.csv)
| Tập | UB | MID | LIVE | UB_ALLOC* | MID_ALLOC* | LIVE_ALLOC* |
|---|---|---|---|---|---|---|
| N | −0,40…−0,22 dưới sàn | −0,02…+0,04 dưới sàn | −0,02…+0,02 dưới sàn | −0,94…−0,81 | −0,10…−0,07 | −0,08…−0,07 |
| M∪N | −0,59…−0,04 cắt sàn 2/4 | +0,11…+0,23 dưới sàn | +0,05…+0,11 dưới sàn | −2,68…−2,29 | −0,31…−0,12 | −0,11…−0,01 |
| N_bat_buoc | −0,45…−0,27 | −0,03…+0,01 | +0,03…+0,06 | −0,87…−0,70 | | |

**Nhãn chính (N, cấu hình chính, MID & LIVE): DƯỚI SÀN NHIỄU 0,46pp ở cả 4 chân.** UB (cận) cũng dưới sàn cho N.
\* ALLOC = overlay_alloc, không phải nhãn chính.

Độ nhạy (cap 20% mọi ngày, exitval=ptin = cấu hình replay gốc): N UB −1,49…−1,38 (vượt sàn), MID/LIVE vẫn dưới sàn
(−0,07…+0,02). UB nhạy mạnh với giả định thanh khoản thoát; MID/LIVE thì không.

## "Có thêm mã nào vượt sàn không"
Solo từng mã N, cấu hình chính: **KHÔNG mã nào |Δ| ≥ 0,46 ở bất kỳ chân nào.** Lớn nhất: UB IBC −0,17, GTT −0,16, PPI −0,16;
MID TNA +0,09; LIVE TNA +0,09. Số mã N sinh ≥1 lô: UB 22–24, MID 8–9, LIVE 4 (theo chân). Lô kẹt (stuck) cấu hình chính: 0 ở N.

## Giới hạn
Như PREREG_V2 §6: release date ước lượng; BCTC VNDirect chưa đối chiếu gốc; 43/136 mã N không BCTC; UB bỏ qua cạnh tranh slot;
giá prices_all chưa đối chiếu nguồn hai; tập Winston = SUSP, sáp nhập/đổi mã có thể thiếu.
Tái lập: `$DNA_PYEXE v2_replay.py <leg>=raw/pin_<md5>.csv ...` → `python3 v2_summary.py`.
