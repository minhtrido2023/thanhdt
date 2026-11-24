# E — nhãn "so với lịch sử CỦA CHÍNH MÃ" cho DD (CHỈ HIỂN THỊ) — job Taylor_20261124_031942

User duyệt 24/11/2026 (topic 1574625384438308914). Thiết kế theo quant-skeptic R2/D2 mục (b). Nhánh
`session/Taylor_20261124_031942`, **chưa merge, chưa wire**. Không vào luật 4 (cổng giá ≤0,85×tâm giữ nguyên),
không đổi tâm/sổ/schema, không email.

## Kết luận
1. **Nhãn mới không phụ thuộc tâm DD, và đây là hệ quả toán học của thiết kế, không phải lỗi.** Hôm nay = giá/tâm
   = giá/(k·proxy hôm nay), lịch sử = giá_t/(k·proxy_t), với cùng một k cố định cho mỗi mã ⇒ k triệt tiêu khi
   xếp phân vị. Nhãn thực chất là "giá/proxy RI-ROE5Y hôm nay của mã so với 10 năm của chính mã". Tâm DD chỉ đổi
   THANG hiển thị (trung vị lịch sử tính theo bội số tâm). Selfcheck (4d): nhân mọi tâm ×1,3 thì nhãn và phân vị
   giữ nguyên 36/36 mã. Spearman giữa giá/tâm và p_hold: **−0,006** với nhãn mới, **0,988** với nhãn cũ.
   Nhãn cũ gần như chỉ là giá/tâm xếp lại trên trung vị universe, đúng chẩn đoán skeptic (b).
2. **Phân bố (36 mã, asof 2026-11-20):** RẺ 17 · TRUNG TÍNH 5 · ĐẮT 3 · KHÔNG CHẮC 11 (rẻ…trung tính 6,
   trung tính…đắt 4, rẻ…đắt 1) · KHÔNG ĐỦ LỊCH SỬ **0**. Mã ít lịch sử nhất là PAT với 53 tháng, vẫn trên ngưỡng 36.
   Nhãn cũ (universe): RẺ 20 · ĐẮT 7 · KHÔNG CHẮC 9 · TRUNG TÍNH 0. **Trùng nhãn cũ ở 12/36 mã.**
3. **Mức độ tin cậy thấp.** N hiệu dụng AR(1) của chuỗi hold có trung vị **3,07**, dải 1,0–14,0. Con số này khớp
   ước lượng 3–5 chu kỳ/10 năm, nên phân vị chỉ là MÔ TẢ, không phải kiểm định. **14/36 mã** có cảnh báo đỉnh lợi
   nhuận (ROE TTM/ROE5Y ≥ 1,3). Với các mã này, ROE5Y đi sau lợi nhuận hiện tại, nên nhãn "rẻ" dễ là ảo.
4. **Có 8 mã đạt giá/tâm ≤ 0,85, nhưng nhãn lịch sử của chúng KHÔNG đồng chiều với cổng luật 4.** Gồm DGC/FPT/SIP
   (RẺ), DRI/VGS (KHÔNG CHẮC), PVP (TRUNG TÍNH), MVC/NNC (ĐẮT ⚠ đỉnh lợi nhuận). Hai thước đo trả lời hai câu hỏi
   khác nhau: luật 4 hỏi "giá so với DD", nhãn hỏi "giá so với proxy cơ học của chính mã theo thời gian". **Không**
   gộp hai thước đo này làm một cổng.
5. **k_mã dao động rất rộng:** k_hold 0,15–2,81, k_fade 0,22–1,80. Có những mã DD khác xa proxy, ví dụ PNJ, CST, HHS
   có k < 0,3. Ở những mã đó proxy là một đại diện yếu của DD, và giả định "k bất biến theo thời gian" (vốn **không
   kiểm được** khi chưa có sổ DD lịch sử) càng đáng ngờ. Đề xuất, CHƯA làm: gắn thêm cờ "proxy lệch DD" khi k nằm
   ngoài [0,5; 2].

## Thiết kế đã cài (`bin/dd_history_label.py`)
- proxy_mã(t) = BV_t × V/BV(ROE5Y_t, r_t) với V/BV ∈ {vbv_fade (fade 10 năm), vbv_dd/hold (giữ ROE5Y 5 năm rồi RI
  phẳng)}. Hàm V/BV trùng D1 `proxy.py` (selfcheck 1). r_t = 13,5% + (Big-4 12T_t − Big-4 tại asof), β = 1. Kết quả
  ≡ `pv_avg5_b4_{fade,hold}` của D2.
- k_mã = tâm / proxy_mã(asof). Giá trị hôm nay = Price_asof/tâm. Phân vị = % tháng trong (asof−10 năm, asof) có
  giá/(k·proxy) nhỏ hơn hôm nay, cùng quy ước `pct_rank` của D2. Chỉ dùng quá khứ.
- Yêu cầu ≥36 tháng hợp lệ ở CẢ HAI biến thể. Tercile <33 / 33–67 / >67. Chỉ gán nhãn khi hai đầu dải cùng một
  tercile, nếu không thì trả `KHÔNG CHẮC (a…b)`.
- Tâm lấy theo bản cuối (dd_date, rev) có tâm trong `kb/dd_price_zones.json`, giống quy tắc D2. Giá chỉ dùng sau khi
  tâm đã khoá, không đi vào giá trị nội tại. Công cụ không đọc đồng hồ: asof = ngày cuối của panel.
- Đầu vào (md5 nằm trong `out/*.meta.json`): panel D1 `panel_all.parquet` b64b0015…, lãi Big-4 R2 8821f62c…, sổ
  9e4cab03… (= bản đóng băng e547cd7fc mà D2 dùng). Panel không nằm trong git, công cụ fallback về cây mike chính.
  **Muốn có giá mới hơn 2026-11-20 thì phải kéo lại panel** (`D1/calc/pull_panel.py --all`). Bước này chưa tự động.

## Bảng 36 mã (asof 2026-11-20; `out/dd_history_label_all_2026-11-20.csv`, `out/compare_vs_universe_2026-11-20.csv`)
⚠ = ROE TTM/ROE5Y ≥ 1,3 (có thể đang ở đỉnh lợi nhuận). "trung vị 10Y giá/thước": với tâm = 1, giá lịch sử thường
nằm ở mức này. Ví dụ PNJ có giá trung vị 10Y gấp 8–10 lần thước-DD-tương-đương, tức k của PNJ rất nhỏ (xem kết luận 5).

| Mã | skeptic | giá/tâm | nhãn lịch sử mã | p[fade, hold] | trung vị 10Y giá/thước, ×tâm (fade–hold) | N tháng | N hiệu dụng (hold) | k [fade, hold] | ROE TTM/5Y | nhãn cũ (universe) |
|---|---|---|---|---|---|---|---|---|---|---|
| BSR | REFUTED_OPEN | 1,43 | TRUNG TÍNH | [57, 45] | 1,29–1,47 | 101 | 3,04 | [0,93, 0,85] | 2,19 ⚠ | KHÔNG CHẮC (trung tính…đắt) |
| CST | REFUTED_OPEN | 2,42 | KHÔNG CHẮC (rẻ…trung tính) | [26, 33] | 3,08–2,87 | 66 | 1,88 | [0,22, 0,16] | 0,41 | ĐẮT |
| CSV | REFUTED_OPEN | 1,94 | TRUNG TÍNH | [36, 48] | 2,32–2,02 | 120 | 2,37 | [0,53, 0,41] | 0,86 | ĐẮT |
| DBC | REFUTED_OPEN | 0,92 | KHÔNG CHẮC (rẻ…đắt) | [30, 68] | 1,10–0,81 | 120 | 14,02 | [0,95, 1,10] | 1,04 | RẺ |
| DCM | REFUTED_OPEN | 1,11 | RẺ | [30, 1] | 1,32–1,63 | 120 | 4,36 | [0,92, 0,61] | 1,01 | RẺ |
| DDV | CONFIRMED | 0,92 | RẺ | [6, 0] | 1,82–2,18 | 60 | 2,93 | [0,96, 0,83] | 1,10 | RẺ |
| DGC | CONFIRMED | 0,74 | RẺ | [1, 1] | 1,89–1,98 | 120 | 4,99 | [0,59, 0,27] | 0,38 | RẺ |
| DRI | CONFIRMED | 0,83 | KHÔNG CHẮC (rẻ…trung tính) | [40, 11] | 0,89–1,35 | 114 | 3,91 | [1,41, 1,24] | 1,80 ⚠ | RẺ |
| FPT | CONFIRMED | 0,79 | RẺ | [3, 2] | 1,44–1,39 | 120 | 2,46 | [1,64, 0,97] | 0,88 | RẺ |
| GAS | CONFIRMED | 1,36 | KHÔNG CHẮC (rẻ…trung tính) | [18, 46] | 1,65–1,41 | 120 | 11,26 | [1,38, 1,04] | 1,02 | KHÔNG CHẮC (trung tính…đắt) |
| HHS | REFUTED_OPEN | 0,90 | RẺ | [2, 4] | 1,59–2,67 | 120 | 2,09 | [0,26, 0,23] | 0,05 | RẺ |
| HPG | CONFIRMED | 0,96 | KHÔNG CHẮC (rẻ…trung tính) | [21, 60] | 1,12–0,87 | 120 | 5,40 | [1,08, 0,90] | 1,09 | RẺ |
| LLM | REFUTED_OPEN | 1,61 | TRUNG TÍNH | [42, 41] | 1,70–2,08 | 63 | 2,09 | [0,91, 1,18] | 4,92 ⚠ | ĐẮT |
| MBB | CONFIRMED | 0,87 | RẺ | [17, 21] | 1,13–1,19 | 120 | 1,93 | [0,97, 0,64] | 0,87 | RẺ |
| MSB | CONFIRMED | 1,27 | KHÔNG CHẮC (trung tính…đắt) | [70, 59] | 1,02–1,12 | 71 | 1,00 | [0,92, 0,76] | 0,78 | KHÔNG CHẮC (rẻ…đắt) |
| MVC | CONFIRMED | 0,84 | ĐẮT | [70, 79] | 0,76–0,55 | 112 | 6,34 | [1,33, 2,33] | 2,86 ⚠ | RẺ |
| NNC | CONFIRMED | 0,77 | ĐẮT | [85, 92] | 0,61–0,30 | 120 | 1,81 | [1,79, 1,46] | 1,86 ⚠ | RẺ |
| NT2 | CONFIRMED | 0,99 | KHÔNG CHẮC (rẻ…trung tính) | [27, 67] | 1,09–0,91 | 120 | 6,03 | [1,24, 1,19] | 1,89 ⚠ | RẺ |
| PAT | REFUTED_OPEN | 1,17 | RẺ | [8, 9] | 1,58–1,44 | 53 | 9,28 | [0,88, 0,35] | 0,57 (ROE5Y kẹp 45%) | KHÔNG CHẮC (rẻ…trung tính) |
| PNJ | REFUTED_OPEN | 1,83 | RẺ | [0, 0] | 10,29–8,25 | 120 | 3,42 | [0,22, 0,15] | 0,59 | ĐẮT |
| POW | REFUTED_OPEN | 1,42 | KHÔNG CHẮC (trung tính…đắt) | [58, 87] | 1,37–1,04 | 103 | 6,60 | [0,83, 1,75] | 2,70 ⚠ | KHÔNG CHẮC (trung tính…đắt) |
| PVP | CONFIRMED | 0,73 | TRUNG TÍNH | [66, 56] | 0,67–0,65 | 105 | 2,97 | [1,20, 1,33] | 1,29 | RẺ |
| PVT | CONFIRMED | 0,99 | RẺ | [16, 18] | 1,22–1,16 | 120 | 4,47 | [0,76, 0,75] | 0,88 | RẺ |
| QTP | REFUTED_OPEN | 1,62 | RẺ | [0, 2] | 2,45–2,21 | 105 | 2,58 | [0,47, 0,47] | 1,51 ⚠ | ĐẮT |
| SAS | CONFIRMED | 0,99 | RẺ | [2, 2] | 1,30–1,60 | 118 | 1,99 | [1,80, 1,30] | 2,36 ⚠ | RẺ |
| SCL | REFUTED_OPEN | 1,55 | KHÔNG CHẮC (trung tính…đắt) | [86, 58] | 1,01–1,43 | 85 | 3,10 | [1,35, 1,32] | 1,59 ⚠ | ĐẮT |
| SIP | CONFIRMED | 0,79 | RẺ | [2, 13] | 1,29–1,04 | 89 | 1,88 | [1,41, 0,77] | 0,82 | RẺ |
| SZL | REFUTED_OPEN | 1,03 | TRUNG TÍNH | [52, 43] | 1,02–1,05 | 120 | 13,20 | [1,38, 1,10] | 1,27 | RẺ |
| TCH | REFUTED_OPEN | 0,88 | KHÔNG CHẮC (trung tính…đắt) | [47, 90] | 0,90–0,55 | 120 | 5,16 | [1,38, 2,81] | 0,90 | RẺ |
| TTA | REFUTED_OPEN | 1,36 | RẺ | [14, 15] | 1,62–1,63 | 74 | 3,47 | [0,62, 0,85] | 1,07 | KHÔNG CHẮC (trung tính…đắt) |
| TV1 | CONFIRMED | 1,45 | RẺ | [4, 4] | 2,41–5,17 | 120 | 2,56 | [0,57, 0,37] | 1,41 ⚠ | KHÔNG CHẮC (trung tính…đắt) |
| TV2 | CONFIRMED | 1,62 | ĐẮT | [75, 97] | 1,14–0,39 | 119 | 2,33 | [1,04, 1,46] | 1,77 ⚠ | ĐẮT |
| VCB | REFUTED_OPEN | 1,41 | RẺ | [0, 0] | 2,77–2,52 | 120 | 1,33 | [0,94, 0,68] | 0,80 | KHÔNG CHẮC (trung tính…đắt) |
| VCP | REFUTED_OPEN | 1,26 | RẺ | [9, 17] | 2,09–2,02 | 114 | 1,99 | [0,66, 0,52] | 1,19 | KHÔNG CHẮC (rẻ…đắt) |
| VGS | REFUTED_OPEN | 0,72 | KHÔNG CHẮC (rẻ…trung tính) | [45, 27] | 0,77–0,93 | 120 | 6,97 | [1,16, 1,21] | 1,50 ⚠ | RẺ |
| VLB | REFUTED_OPEN | 1,07 | RẺ | [0, 0] | 1,60–1,66 | 120 | 9,68 | [1,27, 0,80] | 2,31 ⚠ | RẺ |

## Selfcheck (`bin/dd_history_label_selfcheck.py`, 18 kiểm, ALL PASS dưới `env -u TZ` và `TZ=Asia/Ho_Chi_Minh`, exit 0)
- (1) V/BV trùng D1 tới atol 1e-12. (2) Parity D2 trên FPT (k_hold 0,96637, k_fade 1,6396, giá/tâm 0,78518) và
  VCB (0,67765 / 0,93869 / 1,4101). Toàn sổ lệch tối đa 4,1e-5, vì CSV D2 chỉ ghi 5 chữ số.
- (3) Nhân quả: kết quả asof 2025-06-30 trên panel đầy đủ ≡ trên panel cắt tại T. Nhân ×7 dữ liệu sau T không đổi
  kết quả. Cửa sổ có tối đa 119 tháng (đã loại tháng T).
- (4) Mutation: ROE5Y lịch sử +5 điểm % làm đổi nhãn ở 24/36 mã. Dùng k lệch (1,2k cho lịch sử, k cho hôm nay) làm
  đổi tercile hold ở 12/36 mã. Đổi k nhất quán (tâm ×1,3) không đổi nhãn nào (tính chất ở kết luận 1).
- (5) Luật nhãn: ranh giới tercile, vắt ngưỡng, chuỗi tổng hợp 36 tháng cho p100 ĐẮT, 35 tháng cho KHÔNG ĐỦ.
- (6) Tất định: 2 lần chạy cho cùng md5 CSV `76e278b44d68d57674327ae0d142b4a3`. CLI chạy 2 lần cũng trùng.
  `compare_universe.py` chạy 2 lần trùng (CSV 37183166…, summary f407ce26…). threads = 1.

## Caveat (mang theo khi trình)
- k bất biến theo thời gian: **giả định KHÔNG kiểm được**.
- Lãi Big-4 có 26 mốc neo hồi tố (2026-06-19), nên không PIT thật cho quá khứ.
- ROE5Y: registry ghi CANONICAL, đã verify không hồi tố (07/2026), nhưng chưa có kiểm PIT độc lập cho đoạn trước
  2020. Có giá trị outlier, và PAT bị kẹp ở 45%.
- OShares/BVPS lệch ex-date (ticket F) đi vào PB.
- Proxy là giá trị "THÔ" kiểu DD trước các haircut như kịch bản xấu, chiết khấu thanh khoản.
- Mẫu chỉ là 36 mã của MỘT mặt cắt.

## Đề xuất vị trí hiển thị (CHỈ đề xuất, KHÔNG sửa skill)
Một dòng ở khối kết luận định giá của `dd-investor-report` (và ở phần tóm tắt của `due-diligence`), đặt **sau**
dòng tâm/vùng/cổng 0,85 và gắn nhãn rõ là hiển thị:
> *So với lịch sử 10 năm của chính mã (thước RI-ROE5Y, chỉ hiển thị, không phải tín hiệu): **RẺ** — phân vị
> [fade 3, hold 2], 120 tháng, N hiệu dụng ≈ 2–3; giá hiện = 0,79× tâm, trung vị 10Y ≈ 1,39–1,44× tâm.*

Thêm "⚠ ROE hiện cao hơn TB5Y X lần" khi có cảnh báo đỉnh lợi nhuận. Thêm "proxy lệch DD" nếu cờ k ở kết luận 5
được duyệt. Lệnh: `$DNA_PYEXE bin/dd_history_label.py --ticker <MÃ>`.

## Tái lập
```
cd <mike>; PY=/home/trido/thanhdt/wc_venv/bin/python
$PY bin/dd_history_label.py --all-ledger
$PY agents/Taylor/research/dd_label_20261124/compare_universe.py
env -u TZ $PY bin/dd_history_label_selfcheck.py; TZ=Asia/Ho_Chi_Minh $PY bin/dd_history_label_selfcheck.py
```
