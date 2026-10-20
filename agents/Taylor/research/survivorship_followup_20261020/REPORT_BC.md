# B/C — replay survivorship: bỏ TGG/GAB, cap khớp 5%/10% ADV pha bơm/xả, kiểm KL GAB (job Taylor_20261020_113646, EXPLORATORY)

Không sửa pin/registry/pin_ledger, không đề xuất đổi luật, không sửa engine. PREREG_BC.md md5 `d9a91be2…`, commit `8dc69a2a5`
(TRƯỚC khi tính). Số: `out_followup_results.csv` (từng chân) / `out_followup_table.csv` (dải 4 chân + nhãn) / `bc_summary.out`.
Cố định: Z, exit X-liq, MIX = BAL+LAG, tập M 14 mã. Δ = R3 có phantom − R3 pin (pp CAGR). Nhãn theo trọng số **fixA**
(sau sửa bug A). Ô gốc với w=orig khớp `out_replay_results.csv` gốc ở 72/72 dòng: sai số 0, số lô khớp.

## Kết luận
1. **Dấu "LỢI" của UB chính là giả tạo của TGG/GAB và giả định khớp 20% ADV.** Bỏ TGG+GAB ⇒ UB MIX **−1,88…−1,21** (vượt sàn
   chiều THIỆT). Siết khớp trong pha bơm/xả ⇒ UB trượt về âm: cap 10% −0,45…+0,66, cap 5% −0,58…−0,13 (cả hai "dải cắt sàn").
   Cả hai cùng lúc (M−TGG−GAB, cap 5%) ⇒ −1,04…−0,58 (vượt sàn chiều THIỆT).
2. **MID/LIVE: dấu không đổi, dưới sàn ở MỌI ô.** MID luôn dương (+0,08…+0,39), LIVE ≈ 0 (−0,03…+0,04). Kết luận chắc của replay
   giữ nguyên: dưới cổng BCTC thật của LAG, thiệt hại survivorship từ nhóm mã lớn đã mất nằm dưới sàn 0,46pp.
3. **ALLOC (không prereg): luôn vượt sàn chiều THIỆT ở UB** (−3,88…−1,24 tuỳ ô; 1–2 lô kẹt). MID_ALLOC/LIVE_ALLOC dưới sàn
   (−0,30…+0,21).
4. **C — KL GAB:** VNDirect ĐÚNG. "Lệch 7,7×" là do so khớp lệnh với khớp lệnh + thỏa thuận (chi tiết dưới). Bỏ GAB ⇒ UB MIX
   −0,60…+0,07 (cắt sàn). GAB một mình góp khoảng +0,5…+0,6pp vào UB MIX.

## B — UB MIX (dải 4 chân, w=fixA; cột "từng chân" = p30_pin0 / p30_pin1M / p0_pin0 / p0_pin1M)
| Ô | UB | từng chân | MID | LIVE | UB_ALLOC* |
|---|--:|---|--:|--:|--:|
| **Gốc** M, 20% | +0,03…+0,68 cắt sàn | +0,06 / +0,20 / +0,68 / +0,03 | +0,14…+0,32 | −0,03…+0,02 | −2,67…−1,85 |
| M−TGG−GAB, 20% | **−1,88…−1,21 THIỆT** | −1,66 / −1,65 / −1,21 / −1,88 | +0,22…+0,39 | +0,00…+0,04 | −3,88…−3,20 |
| M, 10% pha | −0,45…+0,66 cắt sàn | +0,26 / −0,31 / +0,66 / −0,45 | +0,08…+0,25 | −0,02…+0,02 | −2,52…−1,24 |
| M, 5% pha | −0,58…−0,13 cắt sàn | −0,46 / −0,57 / −0,13 / −0,58 | +0,08…+0,16 | −0,02…+0,03 | −2,17…−1,78 |
| M−TGG−GAB, 10% pha | −1,48…−0,82 THIỆT | −1,18 / −1,36 / −0,82 / −1,48 | +0,14…+0,32 | +0,00…+0,04 | −3,10…−2,40 |
| M−TGG−GAB, 5% pha | **−1,04…−0,58 THIỆT** | −0,92 / −1,02 / −0,58 / −1,04 | +0,11…+0,19 | −0,00…+0,04 | −2,47…−1,97 |
| M, 5% mọi ngày (cận) | −1,12…−0,84 THIỆT | −1,04 / −0,97 / −0,84 / −1,12 | +0,00…+0,10 | +0,06…+0,10 | −1,91…−1,62 |
| M−TGG−GAB, 5% mọi ngày | −1,58…−1,30 THIỆT | −1,50 / −1,43 / −1,30 / −1,58 | +0,03…+0,13 | +0,07…+0,12 | −2,21…−1,81 |
\* không prereg. Pha = Close ≥ 2×min250 ∨ Close ≤ 0,5×max250 ∨ [LT−365 ngày, DL] (PREREG_BC). Cap áp cho cả khớp vào và thoát X-liq.
Với w=orig (trọng số replay CONFIRMED) mọi dải UB/MID/LIVE gần như trùng (lệch ≤0,09pp ở cận; `bc_summary.out`), vì các cực trị
đến từ chân park 0, nơi bug A không ảnh hưởng. Số khớp kiểm độc lập của skeptic (bỏ TGG+GAB, w=orig): −1,88…−1,12.

## C — Khối lượng GAB, nguồn thứ hai (`c_gab_compare.py` → `c_gab_compare.out`; dữ liệu thô `c_gab_raw/`, tải 2026-10-20)
- **SSI iBoard** (`iboard-api.ssi.com.vn/statistics/charts/history`, dữ liệu ngày): 679/679 ngày trùng lịch, KL khớp lệnh trùng
  VNDirect **tuyệt đối ở 99,6% số ngày**; tỉ lệ SSI/VNDirect trung vị 1,000. Giá SSI = adClose VNDirect.
- **Simplize** (nến tháng) = **khớp lệnh + thỏa thuận**. Từ 2021-01 (VNDirect bắt đầu có cột `ptVolume`), Simplize = nm+pt
  tuyệt đối ở 13/15 tháng (2 tháng lệch −11% và −2%). Trước 2021 VNDirect không có cột thỏa thuận; phần dư bên Simplize là lô tròn
  (vd 2020-03: 22.384.000 CP; 2020-04: 8.422.000). Tổng 2019-07…2022-03: Simplize/khớp lệnh = 3,55×; Simplize/(nm+pt) = 1,39×,
  phần dư nằm hết ở trước 2021.
- ⇒ ADV khớp lệnh dùng cho khớp VÀO trong replay là đúng. Không nhân hệ số cho GAB (hệ số 1/7,7 bị bằng chứng bác bỏ).
- **Chỗ lạc quan thật:** thoát X-liq dùng `val = nmValue + ptValue`, mà thỏa thuận không phải thanh khoản khớp được. Biến thể
  `exit=nm` (chỉ khớp lệnh): UB MIX −0,05…+0,64 (cap 20%) / −0,57…−0,13 (cap 5% pha); MID +0,12…+0,30 / +0,04…+0,12; LIVE ≈ 0.
- GAB về sau thanh khoản cạn thật: từ 2020-12 khớp lệnh 100–300 CP/ngày (≈20–60 triệu VND/ngày) ở giá ~180–196 nghìn, và
  thỏa thuận 0,25–18 triệu CP/tháng. ADV ≥5 tỷ của GAB chỉ đúng cho giai đoạn 2019-07…2020-11.
- Hạn chế: SSI và VNDirect đều lấy từ feed sàn, nên độc lập về nhà cung cấp chứ không độc lập về nguồn gốc. Chưa đối chiếu
  văn bản HOSE/BCTN.

## Tái lập
```bash
O=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research; P=/home/trido/thanhdt/wc_venv/bin/python; R=$O/survivorship_sensitivity_v2_20261020/raw
cd $O/survivorship_followup_20261020
$P -I c_gab_compare.py c_gab_raw > c_gab_compare.out
$P svr_followup.py . p30_pin0=$R/pin_4707bcbe.csv p30_pin1M=$R/pin_bcd0469f.csv p0_pin0=$R/pin_537e349b.csv p0_pin1M=$R/pin_a6ba34d8.csv  # ~25 phút
$P bc_summary.py > bc_summary.out     # kiểm tái lập vs replay gốc trước, rồi bảng
```
