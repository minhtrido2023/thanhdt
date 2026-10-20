# Stress test độ nhạy survivorship của R3 — job Taylor_20261020_082308 (EXPLORATORY)

Không sửa số pin R3/V2.4, không ghi registry, không `pin_ledger add`. PREREG: `PREREG.md` md5 `98835b50…`,
commit `5eb62208d` (trước khi chạy overlay). Đầu vào: báo cáo Winston `kb/projects/delisted-tickers-survivorship-20261020.md`.

## Kết luận
**Nhãn theo PREREG: "vượt sàn nhiễu ở kịch bản X".** X = số phantom THỰC SỰ NẮM ≥ λ* mã/năm, mỗi mã nắm trọn 12 tháng ở
tỉ trọng trung bình một mã rồi mất L. λ* để trung vị ΔCAGR = −0,5pp:

| L | park 0,3 pin0% | park 0,3 pin1M | park 0 pin0% | park 0 pin1M |
|---|--:|--:|--:|--:|
| −30% | 0,55 | 0,53 | 0,36 | 0,35 |
| −50% | 0,40 | 0,39 | 0,26 | 0,26 |
| −80% | 0,29 | 0,29 | 0,19 | 0,18 |
| −100% | 0,25 | 0,25 | 0,16 | 0,16 |

(mã/năm; park 0 nhạy hơn vì danh mục tập trung hơn: tỉ trọng/mã trung bình 3,6% so với 2,2%.)

Mức nắm thật ước từ dữ liệu thấp hơn λ* khoảng **16–56 lần**, nhưng neo đó không được đăng ký trước và có thiên lệch chọn mẫu (§3). Vì vậy đọc kết quả như sau:
**độ lệch survivorship chỉ vượt sàn 0,46pp nếu R3 nắm ≥ 0,16–0,55 mã mà sau đó biến mất mỗi năm, trọn 12 tháng.** Mẫu còn data cho thấy R3 nắm
các mã này ít hơn mức đó khoảng 2 bậc độ lớn. Tôi không tự kết luận lại số pin.

## 1. Control leg
Bốn chân chạy lại đúng lệnh pin (`run_leg.sh` = bản sao `rating_8l_eff_guard_20261020/run_leg.sh`, chỉ đổi OUT; cache
`data/bq_cache_asof20260729_postrestate`, `$DNA_PYEXE`, `BQ_CACHE_THREADS=1`, `AUDIT_END=2026-06-19`). Code: main cho pin0%,
worktree `f66dab18` cho pin1M:

| Chân | md5 chạy lại | = pin | self-check |
|---|---|---|---|
| park 0,3 pin0% (cặp dispatch) | `4707bcbeb7e801d49a4a851ffd91d5e7` | byte-identical | 0 VND BAL+LAG |
| park 0,3 pin1M (cặp dispatch) | `bcd0469f42c2f76937a6ebb10aae9b40` | byte-identical | 0 VND |
| park 0 pin0% (registry "2026-10-08", knob LIVE) | `537e349b5589408c994f8aceafeb9a39` | byte-identical | 0 VND |
| park 0 pin1M | `a6ba34d83a4d374a73293d897c0b43d9` | byte-identical | 0 VND |

Overlay đọc ledger qua `pin_ledger.py extract` (md5 khớp manifest). `calc_metrics` (chép từ engine) tái tạo METRIC
của cả 4 ledger với sai số < 1e-9. Giá control lấy từ cache 07-29 đúng như lệnh pin, không đọc `tav2_bq.ticker`
(hiện đang thiếu 243 mã). Bốn CSV chạy lại trong `data/` đã xoá sau khi so md5 vì trùng byte với kho pin.

Spot-check 5 mã ngẫu nhiên (seed 20261020): TGG, PX1, CVH (`in_data=False`) có 0 dòng ở `ticker_pin_202610`,
`ticker_financial` và `universe_pit`; DCS, IHK (`True`) có 4622/4025 dòng giá ⇒ phân loại của Winston khớp 5/5.

## 2. Kết quả Monte Carlo
2000 lần, seed 20261020, dùng chung số ngẫu nhiên cho mọi ô. ΔCAGR tính bằng pp, so với control; ngoặc vuông là khoảng 5–95%.
D = 74 mã bắt buộc / không rõ lý do / tự nguyện trên HOSE+HNX mất khỏi data, 2014–2025 ⇒ **6,17 mã/năm**.
D+ (thêm mã mất tư cách CTĐC trên HOSE/HNX và mã bắt buộc trên UPCOM) = 88 mã ⇒ 7,33 mã/năm.

| Kịch bản (PREREG) | λ/năm | L | p30 pin0% | p30 pin1M | p0 pin0% | p0 pin1M |
|---|--:|--:|--:|--:|--:|--:|
| trung vị = D×10%×p_hold | **0** | −50% | 0 | 0 | 0 | 0 |
| λ_emp = D×6/127 | 0,29 | −50% | −0,34 [−1,23; −0,04] | −0,36 [−1,26; −0,04] | **−0,56** [−1,52; 0] | **−0,57** [−1,57; 0] |
| D×5%, nắm chắc | 0,31 | −50% | −0,37 | −0,38 | −0,59 | −0,61 |
| D×10%, nắm chắc | 0,62 | −50% | −0,79 | −0,81 | −1,25 | −1,29 |
| D×20%, nắm chắc | 1,23 | −50% | −1,63 | −1,67 | −2,56 | −2,63 |
| xấu nhất hợp lý = D+×20%×1 | 1,47 | −100% | −3,30 [−5,79; −1,70] | −3,34 | −5,21 [−8,10; −2,86] | −5,26 |

Sharpe: −0,02 (λ_emp, p30) đến −0,44 (xấu nhất, p0). MaxDD: trung vị gần như không đổi ở λ ≤ 0,3. Ở kịch bản xấu nhất,
MaxDD sâu thêm −2,1pp (p30 pin0%) đến −3,1pp (p0 pin0%), với khoảng 5% tới −6,3/−8,1pp. Dạng rơi một lần ("vách") làm DD
sâu hơn dạng tuyến tính 0,3–0,6pp nhưng không đổi CAGR. Đầy đủ: `out_mc_results.csv` (cả lưới λ × L, có p05/p95);
`out_summary.json` (tỉ trọng, danh sách mã đã nắm, λ*).

**Theo đúng luật PREREG, kịch bản "trung vị" suy biến về 0.** Trong 10 mã "vùng mua" của Winston (PHH, ATA, PIV, ALV, IDC, LMH, PXS, PHP,
BII, DNM), không mã nào được ledger nắm trong 12 tháng trước thông báo (0/10, cả 4 chân). Tôi không thay luật sau khi đã thấy số.

## 3. Neo thực nghiệm — mức nắm thật (POST-HOC, không có trong PREREG)
Trong 127 mã bắt buộc hủy niêm yết mà vẫn còn data, ledger có nắm **6 mã** trong 12 tháng trước thông báo: S12, SRB, HKB, LM7, SDT, KSQ.
Cả 6 đều nắm qua sổ **LAG** khi rating = 4, tức là KHÔNG thuộc "vùng mua rating ≤3". Lý do: backtest BAL/LAG không áp gate 8L lên
mọi lệnh, nên giả định "rating ≤3 & in_universe" của PREREG không mô tả đúng tập rủi ro.
Thời gian nắm chỉ **4–26 phiên** (tổng 50 phiên), không phải 12 tháng. Lợi suất 12 tháng trước thông báo của các mã này (Winston):
−7%, −14%, −20%, −56%, +11%, −23% (trung vị −17%).
Quy về đơn vị của λ (mã-năm nắm trọn): λ_eff = 6,17 × 50 / (127 × 249,4 phiên/năm) ≈ **0,010 mã/năm**. Con số này thấp hơn λ* ở L = −100%
khoảng 16 lần (park 0) đến 25 lần (park 0,3), và thấp hơn λ* ở L = −30% khoảng 35–56 lần.

**Vì sao chưa dùng neo này để kết luận "nhỏ hơn sàn":**
1. Mẫu còn data thiên về các mã nhẹ. Các mã đã biến mất (FLC, ROS, HAI, AMD, GAB, ART…) là cổ phiếu thanh khoản cao và có momentum mạnh
   năm 2021, đúng loại mà sổ BAL (momentum) có thể nắm nhiều tuần với tỉ trọng đầy đủ. Không có giá thì không đo được.
2. Dữ liệu chỉ có 6 sự kiện nắm, mỗi sự kiện ngắn — không đủ ước một phân phối.
3. λ_eff bỏ qua việc vị thế bị kẹt: nếu ngừng giao dịch đột ngột, backtest giả định thoát ở giá đóng cửa, còn thực tế không bán được.

## 4. Giới hạn của mô hình
- Phantom vào ở tỉ trọng TRUNG BÌNH một mã ngày t0 (BAL+LAG+rổ / số vị thế). Mô hình giữ nguyên số lượng suốt 12 tháng, không
  rebalance và không có stop. Đây là giả định bảo thủ: thực tế LAG/BAL thoát sớm hơn nhiều (§3).
- Phần vốn của phantom lẽ ra hưởng lợi suất của danh mục, nên chi phí cơ hội đã được tính. Mô hình KHÔNG tính chi phí giao dịch
  của lệnh phantom, cũng KHÔNG tính việc phantom chiếm chỗ của một mã thật (giả định mã bị thay thế cho lợi suất bằng trung bình danh mục).
- `t1` phân bố đều trên cửa sổ backtest; cửa sổ nắm bị cắt ở 2014-01-02 (cú rơi L vẫn diễn ra đủ). Số sự kiện theo Poisson.
- Monte Carlo chỉ cho phân phối có điều kiện trên giả định (λ, L). Các con số λ, p_zone, L là GIẢ ĐỊNH; riêng D đo từ CSV của Winston.

## Tái lập
```bash
O=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/survivorship_sensitivity_20261020
M=/home/trido/thanhdt/WorkingClaude; W=/home/trido/thanhdt/wt-Taylor_20261020_045223_repin/WorkingClaude; C=data/bq_cache_asof20260729_postrestate
$O/run_leg.sh $M $C svs_ctl_p30_off BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3
$O/run_leg.sh $W $C svs_ctl_p30_1m  BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=dep1m
$O/run_leg.sh $M $C svs_ctl_p0_off  BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0 IDLE_CARRY_TIER=off
$O/run_leg.sh $W $C svs_ctl_p0_1m   BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0 IDLE_CARRY_TIER=dep1m
cd $M; for m in 4707bcbe… bcd0469f… 537e349b… a6ba34d8…; do python3 mike/bin/pin_ledger.py extract --out $O/raw/pin_<md5_8>.csv <md5>; done
cd $O; /home/trido/thanhdt/wc_venv/bin/python svs_overlay.py . p30_pin0=raw/pin_4707bcbe.csv p30_pin1M=raw/pin_bcd0469f.csv \
  p0_pin0=raw/pin_537e349b.csv p0_pin1M=raw/pin_a6ba34d8.csv     # ~8 phút
```
Đề xuất bước kế (chưa làm, cần Mike/user): (a) phương án B của Winston, chỉ cho khoảng 10 mã lớn đã biến mất (FLC, ROS, HAI, AMD…): lấy giá tới
ngày giao dịch cuối rồi chạy BAL thật trên đó, vì đó là lỗ hổng duy nhất có thể đẩy λ lên vùng λ*; (b) phương án D (`delist_flag` T-90),
đây là thay đổi luật LIVE nên cần user duyệt.
