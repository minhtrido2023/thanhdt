# Làn C — tính mùa vụ (job Taylor_20261006_052500, 2026-10-06)

Nguồn ý tưởng, không wire/size ⇒ không qua quant-skeptic (theo dispatch). Code: branch
`feat/funnel-lane-c-season-20261006` (worktree `agents/Taylor/wt-season-1006`), CHƯA merge.
Artifact: `season_variants.py` (backtest), `summary_season.csv`, `monthly_season.csv`, `panel_season.csv`,
`meta_season.json`. Interpreter `/home/trido/thanhdt/wc_venv/bin/python`; dữ liệu `data/bq_cache`.

## TL;DR
1. **Đã thêm phân biệt mùa vụ**, nhưng **DRI KHÔNG lọt — vì theo dữ liệu, DRI không phải mã mùa vụ.**
   η² (tỉ trọng phương sai log-QoQ do cặp quý) của DRI = **0,10** (ngưỡng 0,6). Riêng cặp Q1→Q2, DRI tăng ở
   4/8 năm 2017-2025 (+215%, +228%, +84%, +15% … −22%, −55%, −61%). QoQ −19% của Q2/2026 vì thế không
   được giải thích bằng một mùa vụ lặp lại; nó là biến động thật (giá mủ/lãi thanh lý vườn cây không đều).
   Tôi **không hạ ngưỡng để ép DRI vào** — đó là tune một tham số theo đúng một mã.
2. **Biến thể đã ship (C1S) không làm xấu edge rổ**: +1,14%/tháng so với BASE, t=5,5 (C1 gốc +1,13%, t=5,3);
   IS t=3,4, OOS t=4,5. Khác biệt so với C1: +0,01pp/tháng (t=0,14), tức là trung tính.
3. **Hôm nay làn C không đổi: 37 mã, không thêm/bớt mã nào.** Chỉ VLB được gắn mùa vụ (η² 0,63; đằng nào cũng
   lọt). PVT vẫn lọt (không mùa vụ, η² 0,29; QoQ +73%).
4. **Nếu user vẫn muốn DRI lọt** thì cần đổi định nghĩa cho MỌI mã (biến thể **C1A**: QoQ so với trung vị
   cùng cặp quý cho mọi mã có ≥3 năm lịch sử, bỏ bước nhận diện mùa vụ). Bằng chứng **lẫn lộn**: FULL
   +1,17%/tháng t=5,4, nhưng IS xấu hơn C1 (−0,10pp, t=−0,66) còn OOS tốt hơn (+0,16pp, t=+1,07). Dấu
   ngược nhau giữa IS và OOS ⇒ không đủ để chọn. Hôm nay C1A: **29 mã — thêm DRI, bớt 9**
   (DC4, DCM, DXP, IDC, KSV, NCT, NNC, SAS, VGT: QoQ dương nhưng THẤP hơn mức mùa vụ thường lệ của chúng).
   Cần user quyết định; tôi không tự ship.
5. **Loại bỏ**: "YoY quý trước > 0 thay cho QoQ > 0" (C1Y) **làm xấu edge rõ**: −0,43pp/tháng so với C1,
   t=−2,5, và xấu ở cả IS lẫn OOS. Điều kiện QoQ đang mang thông tin "lợi nhuận còn tăng tốc" — không bỏ được.

## Thước đo mùa vụ (đã ship)
- Dữ liệu: NP_P0 từng quý trong `ticker_financial`, chỉ quý có ngày biết < asof (PIT), 1 bản/kỳ (bản biết muộn
  nhất thắng). Log-QoQ = ln(NP_q / NP_{q−1}), chỉ khi 2 quý liền kề và cả 2 vế > 0.
- Cửa sổ: 20 quan sát QoQ TRƯỚC quý hiện tại (5 năm). Gom theo cặp quý (Q4→Q1, Q1→Q2, Q2→Q3, Q3→Q4).
- **Mã mùa vụ ⇔ đủ 4 cặp, mỗi cặp ≥ 3 năm, η² = SS_giữa-cặp / SS_tổng ≥ 0,6.** Với 3 năm/cặp, η² 0,6 tương
  đương F(3,8)=4, p≈0,05 dưới giả thuyết "không mùa vụ"; với 5 năm/cặp, p≈0,002. Thiếu lịch sử ⇒ KHÔNG mùa vụ
  (giữ luật cũ QoQ > 0).
- Vì sao dùng log-QoQ chứ không dùng tỉ trọng-trong-năm: xu hướng tăng trưởng cộng ĐỀU vào mọi cặp quý nên
  không tạo ra mùa vụ giả. Tỉ trọng-trong-năm của một mã đang tăng trưởng sẽ tự nghiêng về Q4. Kiểm tay DRI
  theo tỉ trọng-trong-năm 2021-25 cũng chỉ ra η²≈0,24, tức là không đổi kết luận.
- **Điều chỉnh** (mã mùa vụ): QoQ > 0 thay bằng **QoQ đ/c mùa = (P0/P1) ÷ exp(trung vị log-QoQ cùng cặp
  trong cửa sổ) − 1 > 0**, tức "QoQ tốt hơn mức mùa vụ thường lệ". Áp **cả hai chiều**: mã có cặp quý
  thường tăng mạnh thì QoQ dương nhưng thấp hơn mức thường lệ sẽ bị loại (ví dụ selfcheck SUP).
- Trên toàn panel 2014-2026 (dòng YoY ≥30% ∧ 0<PE≤12): 13% là mùa vụ (98 mã, nhiều nhất SJD, NDN, HDG, NSC,
  TNG, TV2, FMC — thuỷ điện/xây dựng/dệt/đường đúng như kỳ vọng). Đ/c mùa thêm 154 dòng, bớt 90 dòng.

## Backtest (`season_variants.py`, khung y hệt `lane_c_backtest.py`)
CONTROL: C1_KNOWN tái lập đúng chuỗi C1_GARP đã ghi ở `../monthly.csv` (max|diff| 9,7e-17, có assert).
C1 theo quý mới nhất THEO KỲ (luật chọn quý mới ở mục 3 dispatch) = C1_KNOWN y hệt trên toàn lịch sử.

| Chân | FULL vượt BASE %/th (t) | IS t | OOS t | OOS bỏ 2020-21 t | vs C1 FULL (t) | TB số mã |
|---|---:|---:|---:|---:|---:|---:|
| C1 (gốc) | +1,13 (5,34) | 3,22 | 4,49 | 4,01 | — | 20,4 |
| **C1S (ship)** | +1,14 (5,54) | 3,44 | 4,45 | 4,22 | +0,01 (0,14) | 20,8 |
| C1A (mọi mã đủ lịch sử) | +1,17 (5,39) | 3,04 | 4,62 | 4,48 | +0,04 (0,34); IS −0,10 (−0,66) / OOS +0,16 (1,07) | 20,9 |
| C1Y (YoY quý trước>0) | +0,70 (3,94) | 2,69 | 2,86 | 1,80 | **−0,43 (−2,45)** | 22,8 |

Ghi chú: 3 biến thể mới ⇒ tổng số phép thử của làn C tăng từ 4 lên 7. Chênh lệch giữa C1S/C1A và C1 đều
không có ý nghĩa thống kê. Kết luận ở đây chỉ là "không làm xấu", KHÔNG phải "tốt hơn".

## Các thay đổi khác trong cùng branch (mục 2-4 dispatch)
- FIFO hàng đợi: ưu tiên chờ lâu nhất (`queued_since`), rồi YoY ≤300% trước, rồi YoY giảm dần. Mã >300% chỉ
  thua mã CÙNG ngày chờ, nên không bị dồn cuối mãi.
- Quý mới nhất THEO KỲ. Quý đó thiếu NP_P0 ⇒ bỏ khỏi làn C hôm đó + cảnh báo khối 08:00 + `excluded`
  (`np_missing(<quý>)`), không lùi về quý cũ. Hôm nay: 0 mã trong vùng làn C bị ảnh hưởng (167 mã toàn bảng có
  quý mới nhất thiếu NP, đều ngoài vũ trụ chất lượng/PE).
- Dọn state: mã không còn ở làn nào + đã quá cooldown 30 ngày ⇒ xoá (STALE). Hàng chờ ≥30 ngày ⇒ xoá
  (QUEUE_EXPIRED) + cảnh báo. Có `prune_log` trong state và `state_pruned` trong kết quả. Phiên có làn lỗi ⇒
  không dọn.
