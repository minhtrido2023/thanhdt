# Survivorship v2 — sửa bug book_counts (fix A, job Taylor_20261020_113646, EXPLORATORY)

Không sửa pin/registry/pin_ledger. PREREG_A.md md5 `00e6f9bf…`, commit `bebce8e72` (cùng bản sửa, TRƯỚC khi chạy MC).
**SUPERSEDED:** bảng λ*, trọng số và tỉ lệ so v1 của 2 chân park 0,3 trong `REPORT.md` + `out_*_SUPERSEDED_bookcount_bug.*`.

## Sửa
`book_counts()` không đếm TX play_type ETF_PARK (≡ `CUSTOM_VN30EXVIC_PITG`, giá trị nằm ở `*_etf_ref`). Thêm assert: mọi ngày trừ
ngày cuối 2026-06-19 (thanh lý kết thúc audit), n_b>0 ⇔ b_stocks_ref>0 và rổ mở ⇔ b_etf_ref>0 — đạt ở 4 chân.

## Dự đoán prereg → kết quả
- 2 chân park 0: MC trùng bản cũ, max |Δ trung vị| = **0,0** (không có rổ) ✔
- p30_pin0: w_BAL **2,566%** / w_LAG **3,731%**; MIX λ*@0,46 L−50 **0,202**, L−100 **0,120**, trùng số skeptic (0,202 / 0,120) ✔

## λ* mới tại 0,46pp (mã/năm, MC trung vị; `out_summary.json`)
| MIX | L=−30% | −50% | −80% | −100% |
|---|--:|--:|--:|--:|
| park 0,3 pin0% | 0,28 | 0,20 | 0,14 | 0,12 |
| park 0,3 pin1M | 0,28 | 0,20 | 0,14 | 0,12 |
| park 0 pin0% | 0,28 | 0,20 | 0,14 | 0,11 |
| park 0 pin1M | 0,25 | 0,19 | 0,13 | 0,11 |

Theo book, L−50 / L−100, dải 4 chân: **BAL** 0,25–0,27 / 0,16–0,17 · **LAG** 0,17–0,18 / 0,11–0,12.
(Số cũ SUPERSEDED: MIX park 0,3 0,35/0,25/0,18/0,15; BAL 0,25–0,32/0,16–0,19; LAG 0,17–0,22/0,11–0,14.)

## Trọng số mới
| Chân | w_BAL | w_LAG | s_BAL / s_LAG | (cũ, SUPERSEDED) |
|---|--:|--:|--:|---|
| park 0,3 pin0% | 2,57% | 3,73% | 0,355 / 0,645 | 2,04% / 3,02% |
| park 0,3 pin1M | 2,61% | 3,62% | 0,365 / 0,635 | 2,05% / 2,92% |
| park 0 pin0% | 2,45% | 3,99% | 0,359 / 0,641 | không đổi |
| park 0 pin1M | 2,56% | 4,07% | 0,360 / 0,640 | không đổi |

## So v1 (cùng ngưỡng 0,50pp, MIX; `logs/ratio_v1_A.txt`)
λ*_v1 / λ*_mới: park 0,3 **1,77–1,94×**; park 0 **1,20–1,34×** (không đổi). Bản cũ ghi "1,2–1,5×", SUPERSEDED.
Nhãn không đổi và mạnh hơn: **"vượt sàn nhiễu 0,46pp ở kịch bản X"** với X ≈ 0,19–0,20 mã/năm nắm trọn 12 tháng rồi mất 50%
(0,11–0,12 nếu mất 100%). Sàn sizing đề xuất cũ (park 0 pin0% + LAG: 0,11 / 0,18) không đổi.

## Control
4 chân chạy lại đúng lệnh pin: md5 4707bcbe / bcd0469f / 537e349b / a6ba34d8 byte-identical (`logs/control_md5_A.txt`);
self-check 0 VND BAL+LAG 8/8 dòng (`logs/svsA_ctl_*.log`). 4 CSV chạy lại đã xoá (trùng byte kho pin).

## Ảnh hưởng chéo
`../survivorship_replay_20261020/svr_replay.py` dùng w v2 cũ và `book_fraction()` mang cùng bug ⇒ replay CONFIRMED đã dùng trọng số
park 0,3 thấp ~20%. Đường dẫn được ghim về file SUPERSEDED để replay vẫn tái lập; số với trọng số fixA ở `../survivorship_followup_20261020/`.
