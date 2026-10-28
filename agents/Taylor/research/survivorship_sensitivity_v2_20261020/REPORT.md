# Survivorship stress test v2 — trọng số phantom theo book (job Taylor_20261020_091621, EXPLORATORY)

> ⚠️ **SUPERSEDED một phần (2026-10-20, job Taylor_20261020_113646):** bảng λ*, trọng số và tỉ lệ so v1 của 2 chân park 0,3 sai do bug book_counts (đếm rổ custom30). Xem `REPORT_A.md`.

Không ghi registry / pin_ledger, không kết luận lại số pin R3. PREREG `PREREG.md` md5 `f9092a9e…`, commit `2453de34c`
(trước khi tính MC). Thư mục v1 `../survivorship_sensitivity_20261020/` giữ nguyên.

## Kết luận
Skeptic đúng: trọng số trung bình mỗi mã (2,2%) làm λ* lạc quan. Với trọng số theo book, **λ* giảm 1,2–1,5×** ở cấu hình tổng hợp (cùng ngưỡng 0,50pp, cùng L=−50%);
nhãn không đổi: **"vượt sàn nhiễu 0,46pp ở kịch bản X"**, với X thấp hơn v1. Ở sàn 0,46pp, ΔCAGR trung vị thấp hơn −0,46pp khi R3 nắm trọn
12 tháng ≥ λ* mã/năm rồi mất L (mã/năm):

| Tổng hợp (MIX) | L=−30% | −50% | −80% | −100% |
|---|--:|--:|--:|--:|
| park 0,3 pin0% | 0,35 | 0,25 | 0,18 | 0,15 |
| park 0,3 pin1M | 0,35 | 0,25 | 0,18 | 0,15 |
| park 0 pin0% | 0,28 | 0,20 | 0,14 | 0,11 |
| park 0 pin1M | 0,25 | 0,19 | 0,13 | 0,11 |

Theo book (λ* tại 0,46pp, L=−50% / L=−100%, dải 4 chân): **BAL** 0,25–0,32 / 0,16–0,19 · **LAG** 0,17–0,22 / 0,11–0,14.
v1 (trọng số trung bình, ngưỡng giải 0,50pp) cho 0,26–0,40 / 0,16–0,25 ⇒ so cùng L, MIX thấp hơn 1,2–1,5×.
Ví dụ (park 0,3 pin0%, L=−50%): ΔCAGR trung vị tại λ=0,25 là BAL −0,35 / MIX −0,46 / LAG −0,52pp.

Sàn thực tế để sizing nên đọc ở **park 0 pin0% + LAG** (book mọi ca nắm thật đều thuộc về): λ* = 0,11 mã/năm ở L=−100%, 0,18 ở L=−50%.

## Đo trọng số (cách đo: PREREG §1; `out_summary.json`)
`w_b = median_d [ b_stocks_ref(d) / combined_nav(d) / n_b(d) ]` trên ngày có n_b ≥ 1; n_b dựng từ TX (net shares > 0 theo cột `book`).
Share book `s_b` = tỉ lệ số vị thế mở trung bình.

| Chân | w_BAL | w_LAG | n̄_BAL | n̄_LAG | s_BAL / s_LAG |
|---|--:|--:|--:|--:|--:|
| park 0,3 pin0% | 2,04% | 3,02% | 6,02 | 9,41 | 0,39 / 0,61 |
| park 0,3 pin1M | 2,04% | 2,92% | 6,14 | 9,52 | 0,39 / 0,61 |
| park 0 pin0% | 2,45% | 3,99% | 6,20 | 11,06 | 0,36 / 0,64 |
| park 0 pin1M | 2,56% | 4,07% | 6,27 | 11,15 | 0,36 / 0,64 |

Chân park 0,3 trùng số skeptic (BAL 2,0%, LAG 3,0%). Park 0 tập trung hơn nên trọng số/mã cao hơn ⇒ λ* thấp hơn. Rổ ETF/custom30 ngoài phạm vi phantom.

## Căn nhãn / ngưỡng
Nhãn và điểm giải λ* cùng dùng 0,46pp. Tại 0,50pp (so v1) λ* cao hơn nhẹ: MIX L=−50% 0,27 / 0,27 / 0,21 / 0,20 (4 chân theo thứ tự bảng) — chênh ≤ 0,02 mã/năm so với 0,46pp. Đầy đủ: `out_summary.json`.

## Control (chạy lại trước khi đọc MC)
4 chân chạy lại đúng lệnh pin (`run_leg.sh`, cache `data/bq_cache_asof20260729_postrestate`, `$DNA_PYEXE`, threads=1):
md5 `4707bcbe…` / `bcd0469f…` / `537e349b…` / `a6ba34d8…` **byte-identical** với kho pin (`logs/control_md5.txt`); self-check 0 VND
BAL+LAG ở cả 4 (8/8 dòng). Overlay tái tạo METRIC với sai số ≤ 3,6e−15. 4 CSV chạy lại đã xoá (trùng byte với kho pin).

## Còn mở / giới hạn
- λ_eff ≈ 0,010 mã/năm của v1 là post-hoc, từ mã còn data, không đăng ký trước; so với λ* mới (0,11–0,15 ở L=−100% MIX) cách ~11–15× thay vì 16–25×.
  Không dùng để nói survivorship nhỏ: FLC/ROS/HAI/AMD/GAB/ART vẫn chưa có giá ⇒ p_hold thật chưa đo (đề xuất phương án B của Winston vẫn mở).
- Cả 6 mã nắm thật ở v1 thuộc LAG ⇒ cột LAG là cột sát thực tế nhất. Phantom chỉ giữ nguyên số lượng 12 tháng (không thoát sớm), chưa mô hình hoá kẹt thanh khoản, không phí giao dịch.
- Trọng số median hằng số theo thời gian (không theo w(t0)); λ, L là giả định.

## Tái lập
```bash
O=…/research/survivorship_sensitivity_v2_20261020; M=/home/trido/thanhdt/WorkingClaude
# control: 4 lệnh như v1 với run_leg.sh của thư mục này; pin_ledger.py extract --out raw/pin_<md5_8>.csv <md5>
cd $O; /home/trido/thanhdt/wc_venv/bin/python svs_overlay_v2.py . p30_pin0=raw/pin_4707bcbe.csv p30_pin1M=raw/pin_bcd0469f.csv \
  p0_pin0=raw/pin_537e349b.csv p0_pin1M=raw/pin_a6ba34d8.csv   # ~32 phút
```
Đầu ra: `out_mc_results.csv` (leg, cfg BAL/LAG/MIX, λ, L, ΔCAGR med/p05/p95), `out_summary.json`.
