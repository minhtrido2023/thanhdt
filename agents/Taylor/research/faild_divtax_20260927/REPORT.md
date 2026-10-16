# FAIL-D — haircut THUẾ CỔ TỨC, đo lại trên anchor R3 hiện hành (park = 0,30)

Job `Taylor_20260927_145513` · 2026-09-27 · Taylor · **paper-only, KHÔNG re-pin, KHÔNG wire**

## 0. Kết luận một dòng

Ở mức park **0,30** (knob live), haircut thuế cổ tức 5% làm CAGR **23,37% → 23,35%**
(**−0,02pp/năm**), Sharpe **không đổi 1,88**, MaxDD −14,6% → −14,7%, Calmar 1,60 → 1,59,
Final NAV 684,52B → 683,06B. **Không đổi bất kỳ quyết định nào** — nó nhỏ hơn khoảng cách
30% vs 80% (E[Calmar] 1,476 vs 1,216) khoảng **hai bậc độ lớn**. So với lần đo ở knob cũ
(−0,055pp/năm, park_share NAV 0,2453) độ lớn **co lại 2,4×** vì knob 0,30 chỉ giữ rổ ở
**10,50% NAV** trung bình toàn kỳ.

## 1. Thuế suất — tra `mike/kb/data_registry/` TRƯỚC khi chọn (§9)

Nguồn chuẩn tắc: **`mike/kb/data_registry/price-volume/ticker_close_vs_price_dividend_adj.md`**
§ "Bẫy (5) — số broker là GỘP; thuế TNCN 5% trừ lúc CHI TRẢ".

- **5%** — cổ tức tiền mặt của **cá nhân cư trú**, khấu trừ **tại nguồn**. Căn cứ
  **TT 111/2013/TT-BTC Đ.10** (thuế suất) + **Đ.25** (khấu trừ tại nguồn); **Luật TNCN
  109/2025/QH15** hiệu lực **01/07/2026** **GIỮ NGUYÊN 5%** cho thu nhập từ đầu tư vốn.
- SpaceX + ZaloPay đều là **tài khoản CÁ NHÂN ⇒ 5%** (registry nói thẳng).
- Đo được bằng **tiền thật**, không phải thông lệ: ca chi trả MBB của SpaceX 17/07/2026 —
  `cashDividendReceiving` giảm 2.400.000 (GỘP, đúng mệnh giá) trong khi `availableCash` chỉ
  tăng 2.280.000 ⇒ chênh **120.000 = 5,00% chính xác**.
- ⚠️ Registry tự khai **cơ sở thực nghiệm n=1** (tới 02/08/2026 mới đúng 1 sự kiện chi trả
  thật). Mức 5% có căn cứ pháp lý vững, nhưng đây là giới hạn phải mang theo.
- Ngoại lệ đã biết (KHÔNG áp cho 2 account này): Luật 109/2025 **giảm 50%** thuế cho lợi tức
  chia từ quỹ đầu tư chứng khoán/BĐS; miễn thuế chuyển nhượng CCQ mở giữ ≥2 năm.

### Backtest hiện đang giả định gì? — **GỘP (gross), thuế 0%, phí tái đầu tư 0**

Chuỗi level custom30V dùng `Close` **đã điều chỉnh** ⇒ theo định nghĩa là *total return với cổ
tức tái đầu tư tức thì, GỘP, không thuế, không phí*. Live thì đây là rổ 30 cổ phiếu **tự quản**
(`PARK_TICKER = "CUSTOM_VN30G"`): cổ tức TIỀN về tài khoản → chịu thuế 5% → rồi mới mua lại (có
phí). `simulate_holistic_nav.py:888-890` chỉ trừ `etf_mgmt_fee_annual` / `etf_tracking_drag_annual`,
và **cả hai = 0** cho nhánh basket tự quản (đúng — không có phí quản lý quỹ) ⇒ **không có gì
thay chỗ thuế cổ tức**. Đó chính là FAIL-D của `measurement_integrity_audit_20260927/REPORT.md`.

## 2. A/B MỘT BIẾN — cách dựng và vì sao nó đúng một biến

`k = thuế + (1 − thuế) × phí 0,1%` (phí = TC một chiều, CLAUDE.md) ⇒ `k = 5,095%` ở thuế 5%.

Hiệu chuẩn sang **một hằng số drag/năm trên SỔ PARK** tái lập ĐÚNG tích luỹ haircut của rổ:

```
PROD_p (1 − k·DY_p)  over 49 kỳ rebal  = 0,98248044          (DY_p nguyên văn part2/dy_by_rebal.csv)
d = 252 × (1 − PROD^(1/(252·12,460)))  = 0,00141852 /năm      (= 0,1419%/năm trên SỔ PARK)
```

Bơm vào engine qua **hook ĐÃ CÓ SẴN** `etf_tracking_drag_annual` (shrink `lot["shares"]` mỗi
phiên) — không thêm đường tính mới. Knob env `PARK_DIV_TAX_DRAG_ANNUAL`, **mặc định "" = 0,0**.

**Env còn lại copy NGUYÊN VĂN lệnh pin canonical** (`research/repin_park030_20260927/run_pin.sh`):
`$DNA_PYEXE` · `BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate` · `BQ_CACHE_THREADS=1` ·
`BASKET_CA_SNAPSHOT=data/snapshots/corp_action_share_20260927.parquet` · `NAV_TOTAL_B=50`
`ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3
AUDIT_END=2026-06-19` · `v23a none postbull 0 edge`. Runner: `run_leg.sh`.

### ✅ CỔNG BẮT BUỘC — chân control tái lập pin BYTE-IDENTICAL

```
data/…_advprice_univpit.csv                    md5 4707bcbeb7e801d49a4a851ffd91d5e7   (pin canonical)
data/…_advprice_exp_faild_ctrl_univpit.csv     md5 4707bcbeb7e801d49a4a851ffd91d5e7   (chân CONTROL)
cmp → SẠCH · 16.633 dòng · 39 band rebalance · label_col=known_date rows=583
Final NAV 684,52B  CAGR 23,37%  Sharpe 1,88  MaxDD −14,6%  Calmar 1,60
self-check 0 VND (BAL + LAG, cash-flow + final-NAV) · borrow-audit 0 VND
```

⇒ cổng qua. Mọi Δ dưới đây là chênh thật do đúng biến can thiệp.

## 3. Δ TÁC ĐỘNG — thuế 5% (số cần trả lời)

| Metric | CONTROL (GỘP, = pin) | **NEW (thuế 5%)** | Δ |
|---|---|---|---|
| CAGR | 23,37% | **23,35%** | **−0,02pp** |
| Sharpe(252) | 1,88 | **1,88** | **0,00** |
| MaxDD | −14,6% | **−14,7%** | −0,1pp (xấu hơn) |
| Calmar | 1,60 | **1,59** | −0,01 |
| Final NAV | 684,52B | **683,06B** | **−1,46B** (−0,213%) |
| IS 2014-19 | 20,00% | **19,98%** | −0,02pp |
| OOS 2020+ | 26,50% | **26,48%** | −0,02pp |
| band rebalances | 39 | 39 | 0 |

- `self-check 0 VND` **cả 2 chân** (BAL + LAG, cash-flow identity + final-NAV identity).
- Recompute độc lập `extract_peryear.py`: FULL 23,35 · IS 19,98 · OOS 26,48 (khớp print engine).
- **Δ đồng đều IS và OOS** (−0,02/−0,02pp) ⇒ không phải hiệu ứng một giai đoạn.
- Ledger NEW md5 `b79da8e215238bb0ce505523bac14e8c`.

### Đối chứng SỐ HỌC độc lập (không qua engine) — khớp

`arith_crosscheck.py` áp `drag = 1 − Π_p(1 − k·DY_p·park_share_p)^(1/yrs)` **trên chính ledger
control**, `park_share_p` ĐO THẬT (`(bal_etf_ref+lag_etf_ref)/combined_nav`):

```
park_share trung bình toàn kỳ = 0,1050      ← knob 30% ⇒ rổ chỉ chiếm 10,5% NAV
PROD over 49 kỳ = 0,997640  →  drag = 0,0234 pp/năm  (23,3700% → 23,3466%)
```

⇒ **engine −0,02pp ≈ số học −0,0234pp**. Hai đường đo độc lập khớp ở bậc nhất; bản dựng lại này
cũng tái lập đúng con số 0,023pp của `park_fraction_grid_20260927/REPORT_v2.md` §5.

## 4. Độ nhạy thuế + NỀN NHIỄU — và một cảnh báo phải đọc

| Chân | drag/năm trên sổ PARK | CAGR | Sharpe | MaxDD | Calmar | NAV | IS | OOS | Δ CAGR |
|---|---|---|---|---|---|---|---|---|---|
| ctrl (GỘP) | 0 | 23,37% | 1,88 | −14,6% | 1,60 | 684,52B | 20,00% | 26,50% | — |
| thuế **0%** (chỉ phí 0,1%) | 2,783e-5 | 23,37% | 1,88 | −14,6% | 1,60 | 684,49B | 20,00% | 26,50% | 0,00pp |
| thuế **5%** ⭐ | 1,4185e-3 | 23,35% | 1,88 | −14,7% | 1,59 | 683,06B | 19,98% | 26,48% | −0,02pp |
| thuế **10%** | 2,8101e-3 | 23,13% | 1,86 | −14,7% | 1,57 | 668,26B | 19,95% | 26,08% | −0,24pp |

**Chân thuế 0% = phép đo NỀN NHIỄU**: drag gần như bằng 0 ⇒ ΔNAV chỉ −0,029B (−0,0042%), không
ngày nào lệch >0,05%. Engine theo được biến can thiệp nhỏ một cách trơn ⇒ số −0,02pp ở thuế 5%
là **đọc được thật**, không phải nhiễu làm tròn.

⚠️ **KHÔNG được đọc bảng này như một đường dose-response.** Chân 10% lệch **−0,24pp** trong khi số
học chỉ dự đoán −0,046pp. Bóc theo năm cho thấy lý do: Δ của chân 10% là **−0,04pp ở 10/13 năm**
(đúng gấp đôi chân 5%, như kỳ vọng) **cộng BA lần phân kỳ ĐƯỜNG ĐI cục bộ** — 2021 **−3,22pp**,
2022 **−1,05pp**, 2025 **+0,66pp** (đổi DẤU). Đó là hiệu ứng rời rạc (lô/fill/JIT-unpark lật),
không phải liều thuế; `borrow-days LAG` cũng nhảy 22 → 25 → 40. Chân 5% **không** có hiện tượng
này: Δ theo năm nằm gọn trong −0,003 … −0,047pp ở **cả 13 năm**.

⇒ Với haircut cỡ này, **số học là công cụ ước liều đúng**; chân engine dùng để xác nhận bậc nhất
và để kiểm self-check, không dùng để dựng đường cong.

## 5. Có đổi quyết định không? — KHÔNG

- Quyết định park 0,30 dựa trên **Calmar/đuôi DD**, không phải CAGR tuyệt đối: E[Calmar] paired
  block bootstrap 30% = **1,476** vs 80% = **1,216**; 0,80 fail cổng bootstrap 5th-pct MaxDD ở cả
  3 ngưỡng. Haircut lấy đi **0,01 Calmar** — nhỏ hơn khoảng cách đó ~26×.
- Haircut **đơn điệu theo knob park** (park_share càng lớn, drag càng lớn) ⇒ nó chỉ làm các mức
  park CAO xấu thêm. Tức nó **củng cố** lựa chọn 0,30, không đe doạ nó.
- Số đóng góp parking: lần đo ở knob cũ là **+2,01pp → +1,95pp**. Ở knob 0,30 độ lớn haircut
  là **−0,023pp/năm** (thay vì −0,055pp) vì park_share NAV giảm 0,2453 → 0,1050.

## 6. §21 — RANH GIỚI với SỐ CÔNG BỐ nhà đầu tư: **HAI ĐƯỜNG KHÁC NHAU, đừng lẫn**

**Số công bố KHÔNG bị ảnh hưởng bởi phát hiện này, và KHÔNG cần sửa gì.**

| | Đường BACKTEST (việc này) | Đường SỐ CÔNG BỐ (§21) |
|---|---|---|
| Ai tính | `pt_v23_audit_2014.py` / `simulate_holistic_nav.py` | `mike/bin/dividend_adjusted_return.py` |
| Cổ tức tính thế nào | ngầm trong `Close` đã điều chỉnh — **GỘP** | 4 tầng tường minh, **TẦNG 4 = thuế TNCN 5%** |
| Thuế | **0%** (đây là FAIL-D) | `PIT_DIVIDEND_RATE = 0.05`, tham số `--div-tax-rate` |
| Con số ra | CAGR mô phỏng, NAV 50B giả lập | tỉ suất per-position của tài khoản THẬT |

- Đường công bố **đã** trừ 5% từ 2026-08-02 và in kèm GỘP + số thuế. Haircut backtest **không**
  chạm vào nó.
- Cấm lẫn theo chiều ngược lại: **không** được lấy −0,02pp này đi trừ thêm vào tỉ suất công bố
  (sẽ trừ thuế hai lần), và **không** được coi việc đường công bố đã trừ 5% là bằng chứng
  backtest cũng đã trừ.
- Quy ước chung "CAGR thật ≈ CAGR backtest − 1,5%" (CLAUDE.md) là haircut **TỔNG**, không phải
  mô hình, và nó **không** được áp khi so chân park vs chân không-park — chính là cách +2,01pp
  được đo. −0,02pp ở đây là phần thuế cổ tức **đo riêng**, nằm bên trong 1,5% đó.

## 7. Giới hạn (bắt buộc công bố)

1. **Haircut là drag HẰNG SỐ/năm**, hiệu chuẩn để tái lập đúng TÍCH LUỸ của chuỗi DY thay đổi
   theo kỳ. Nó không tái hiện đúng THỜI ĐIỂM từng đợt cổ tức. Đối chứng số học ở §3 mới là bản
   time-varying; hai bản khớp ở bậc nhất.
2. **`DY_p` thừa hưởng nguyên** từ `measurement_integrity_audit_20260927/part2/dy_by_rebal.csv`
   (49 kỳ, 2014-08-05 → 2026-06-15, `w_cov ≈ 1,000`) — job này KHÔNG đo lại DY.
3. **Phí tái đầu tư 0,1%** là TC một chiều theo CLAUDE.md; **không** mô hình slippage lẫn thuế
   chuyển nhượng 0,1% khi BÁN. Vậy haircut này vẫn là **chặn DƯỚI** của tổng ma sát cổ tức.
4. **n=1** cho bằng chứng thực nghiệm mức 5% (registry tự khai) — xem §1.
5. Cùng một vintage `bq_cache_asof20260729_postrestate`, cùng snapshot corp-action ghim; một
   đường đi lịch sử duy nhất.
6. Chân 10% **không dùng được** làm điểm dose-response — xem cảnh báo §4.

## 8. §8 — mọi output đều mang tên NON-CANONICAL

Trục `PARK_DIV_TAX_DRAG_ANNUAL` tự thêm hậu tố `_divtax<drag×1e6>` vào tên file (chỉ khi > 0), và
mọi chân đều đi qua `EXP_TAG` ⇒ `_exp_faild_*`. **Không chân nào có thể ghi vào tên pin canonical.**

| Chân | Ledger | md5 |
|---|---|---|
| ctrl | `…_advprice_exp_faild_ctrl_univpit.csv` | `4707bcbeb7e801d49a4a851ffd91d5e7` (= pin) |
| thuế 0% | `…_advprice_exp_faild_tax00_divtax28_univpit.csv` | — |
| thuế 5% | `…_advprice_exp_faild_tax05_divtax1419_univpit.csv` | `b79da8e215238bb0ce505523bac14e8c` |
| thuế 10% | `…_advprice_exp_faild_tax10_divtax2810_univpit.csv` | `922442a4f17c7576510c77b550dbe6fe` |

## 9. Đề xuất (KHÔNG tự làm)

1. **KHÔNG re-pin** anchor R3 theo chân 5%. Lý do: −0,02pp nhỏ hơn mọi biên bất định đã công bố
   của chính anchor đó, và re-pin sẽ trộn một mô hình ma sát MỚI vào một số đang được dùng làm
   baseline so sánh. Nếu user muốn anchor "ròng thuế" thì đó là một **quyết định về quy ước**,
   phải ghi vào registry như một trục riêng, không sửa số cũ.
2. **KHÔNG wire** `PARK_DIV_TAX_DRAG_ANNUAL` vào production. Nó là knob ĐO LƯỜNG; mặc định 0 giữ
   byte-identical. Muốn wire thì phải đo lại toàn bộ lưới park (haircut đơn điệu theo knob ⇒ đổi
   nhẹ hình dạng lưới), và đó là việc khác.
3. **Cập nhật FAIL-D trong `measurement_integrity_audit_20260927/REPORT.md`** từ "chưa đo chính
   xác" → đã đo, với 2 số: −0,055pp/năm ở knob cũ, **−0,023pp/năm ở knob live 0,30**.
4. Nếu sau này đo lại `DY_p`: giữ nguyên hình dạng A/B này, đổi đúng file DY.
