# Kế hoạch nghiên cứu — tái thẩm định custom30V sau lỗi đo lường 2026-09-27

> Trạng thái: **ĐỀ XUẤT, chờ user duyệt** (soạn 2026-09-27 16:5x ICT, Mike).
> Phạm vi: PAPER-ONLY. Không đổi `trading_rules.json`, không đổi rail, không đặt lệnh cho tới khi
> quant-skeptic CONFIRMED + user ký từng bước.

## 0. Ba câu hỏi phải trả lời

| # | Câu hỏi | Vì sao chưa trả lời được bằng số đang có |
|---|---|---|
| Q1 | Backtest nên dùng **proxy nào cho lãi tiền nhàn rỗi** (Trứng vàng)? | Mọi số pin tới nay giả định **0%/năm**. Job U đo carry thật **8,55%/năm** nhưng chính báo cáo đó cảnh báo áp 8,55% (spot 09/2026) cho 2014-2026 là **ngược thời gian**. |
| Q2 | custom30V vs custom30 vs biến thể kiểu AlphaLens — cái nào **hiệu quả hơn**? | Sau sửa lỗi, parking custom30V chỉ còn +2,05pp CAGR **và làm xấu mọi chỉ tiêu risk-adjusted** (Sharpe 1,95→1,69, DD −16,1→−18,8, Calmar 1,39→1,30). Chưa ai so 3 ứng viên **cùng khuôn, cùng proxy tiền**. |
| Q3 | Có nên **tiếp tục dùng custom30V** trong production không? | Chỉ trả lời được SAU Q1+Q2 — vì "parking có lời không" phụ thuộc trực tiếp vào tiền nhàn rỗi được trả bao nhiêu nếu KHÔNG park. |

Thứ tự **bắt buộc**: Q1 → Q2 → Q3. Làm Q2/Q3 trước Q1 là lặp lại đúng lỗi cũ (so sánh trên giả định 0% không có thật).

## 1. Điểm xuất phát (đã kiểm chứng, không cần đo lại)

- Pin R3 sau sửa double-count: **24,42%** CAGR @park 0,7 (cũ 28,86%); @park **0,30** (knob live từ 15:48 ICT hôm nay): **23,43% / Sharpe 1,88 / DD −14,4% / Calmar 1,63** (`results_registry.md` mục quinquies). Tất cả ở giả định tiền nhàn rỗi = 0%.
- Job U (`idle-pool-redeploy-huong-di-2709`): carry egg đo thật **8,543%/năm**, phẳng theo gốc (7,8tr→102tr), cộng dồn mỗi ngày lịch, không thấy bậc. **Break-even carry để park 0,30 thắng 0,80 = 7,00%/năm.** Mafee: điều khoản công khai KHÔNG có trần, KHÔNG có bậc, nhưng cũng KHÔNG cam kết mức lãi — đây là lãi **sản phẩm**, không phải lãi thị trường.
- Track live 07-01→09-25: custom30V trọng số PIT thật **−7,42%**, VNINDEX **−4,03%**, AlphaLens EW **≥ +0,51%**. ⚠️ AlphaLens là 4 tên chọn tay ⇒ **N hiệu dụng = 1**, không phải chiến lược kiểm chứng được — chỉ là gợi ý hướng, không phải bằng chứng.
- Chương trình AlphaLens paper **hết hạn 2026-09-30** (3 ngày nữa). FiinPro-X trial **hết hạn 2026-09-28** (mai).

## 2. Q1 — Proxy lãi tiền nhàn rỗi: dữ liệu đang có và đề xuất

### 2.1 Kiểm kê (làm hôm nay, 16:4x ICT)

| Nguồn | Phủ | Point-in-time thật? | Dùng được làm proxy lịch sử? |
|---|---|---|---|
| `deposit_rate_vn.py` 26 mốc Big-4 12M (CANONICAL-PROXY) | 2011→nay | **KHÔNG** — 26 mốc neo hồi tố cùng 1 lần 2026-06-19 (registry caveat b) | **Không** cho backtest 2014-2026; chỉ mốc thêm từ 06/2026 là PIT |
| Carry egg đo thật (dnse_raw) | 2026-08-18→nay, 6 kỳ sạch | Có, nhưng chỉ 6 tuần | **Không** cho lịch sử; là **điểm neo hiện tại** |
| **FiinPro: SBV lãi suất huy động bình quân >12T (cao nhất/thấp nhất), tháng** | **01/2011 → 08/2026, 179 tháng, đủ** | **CÓ** — thống kê NHNN công bố theo tháng | **CÓ** — ứng viên chính |
| **FiinPro: lãi suất BQ liên ngân hàng O/N, 1W, 2W, 1M, 3M, 6M, 9M, tháng** | **01/2014 → 09/2026, 153 tháng, đủ** | **CÓ** | **CÓ** — ứng viên cho tầng "tiền ngắn hạn thanh khoản" |
| SBV refi-rate (`sbv_macro_overlay`) | có | có | Là lãi chính sách, không phải lãi người gửi nhận — chỉ dùng đối chiếu |

**Đã snapshot 2 chuỗi FiinPro vào đĩa trước khi trial hết hạn:**
`mike/agents/Taylor/research/idle_cash_proxy_20260927/fiinprox_sbv_avg_deposit_rate_monthly_2011_2026.csv`
(358 dòng) và `fiinprox_interbank_avg_rate_monthly_2014_2026.csv` (2.142 dòng, gồm cả doanh số).
Registry: `kb/data_registry/macro/fiinprox_rates_snapshot_20260927.md` (UNVERIFIED-PIT-CANDIDATE
cho tới khi Taylor đối chiếu chéo ≥3 mốc với nguồn NHNN gốc).

Vài mốc đọc nhanh (để thấy vì sao 0% và 8,55% đều sai):

| Kỳ | SBV avg 12M thấp/cao | Liên NH O/N | Ghi chú |
|---|---|---|---|
| 01/2014 | 7,5 / 8,5 | 4,70 | |
| 11/2022 | 5,7 / 7,0 | 5,32 | đỉnh siết tiền tệ |
| 08/2026 | 6,1 / 7,6 | 1,19 | **egg 8,55% > cả mức "cao nhất" 7,6%** |

⇒ Egg hôm nay trả **cao hơn trần thống kê 12M ~1pp và cao hơn liên NH O/N ~7pp**. Đó là **spread sản phẩm/khuyến mãi**, không phải lãi thị trường — không được coi là hằng số lịch sử.

### 2.2 Đề xuất proxy — 3 tầng, không phải 1 số

Bản chất kinh tế của egg: **thanh khoản T+1, cộng lãi hàng ngày, không kỳ hạn** ⇒ gần với tiền gửi ngắn hạn/money-market hơn là tiền gửi 12 tháng. Nên:

1. **Baseline (dùng cho MỌI số pin/so sánh):** `r_idle(t) = SBV avg 12M THẤP NHẤT(t) − haircut`, haircut = **1,0pp** (khoảng cách kỳ hạn 12M ↔ không kỳ hạn/T+1, quy ước — Taylor phải hiệu chỉnh haircut bằng chính khoảng cách "12M thấp nhất − liên NH 3M" đo trên 2014-2026 thay vì đoán). Thay đổi theo tháng, PIT thật.
2. **Sàn (stress):** `max(0, liên NH 1M(t))` — kịch bản tiền chỉ được lãi qua đêm/money-market, mất hết spread sản phẩm.
3. **Trần (spot, KHÔNG dùng cho lịch sử):** carry egg đo thật 8,55% — chỉ dùng cho **kỳ nhìn trước ngắn** (≤ 6 tháng tới) và phải **kèm sensitivity** vì DNSE không cam kết mức lãi.

Nguyên tắc: mọi kết luận Q2/Q3 phải **đứng trên tầng 1 VÀ không đảo dấu ở tầng 2**. Nếu chỉ thắng ở tầng 3 thì kết luận là "thắng nhờ khuyến mãi DNSE", phải ghi rõ như vậy.

### 2.3 Gate Q1

- Taylor đối chiếu ≥3 mốc SBV với nguồn gốc NHNN/Trading Economics; ≥3 mốc liên NH với báo cáo SBV tuần tương ứng. Lệch >0,2pp ở bất kỳ mốc nào ⇒ chuỗi hạ xuống UNVERIFIED, không dùng.
- Đo lại **break-even carry** của Job U trên chuỗi tầng 1 (theo tháng) thay cho 8,55% phẳng — đây là con số quyết định Q3.

## 3. Q2 — So 3 ứng viên CÙNG KHUÔN

### 3.1 Ứng viên

| Nhãn | Định nghĩa vận hành | Code đã có? |
|---|---|---|
| **A. custom30V** (production) | `BASKET_SELECT=yieldcombo`: thanh khoản là GATE, xếp thuần rank(1/PE)+rank(1/PCF), 30 mã, cap 0,10, rebal quý | Có, `custom_basket.py` |
| **B. custom30** | `BASKET_SELECT=blend`: rank(liq)+λ·rank(yield) | Có, `custom_basket.py` |
| **C. "AlphaLens-style" — PHẢI ĐỊNH NGHĨA LẠI thành QUY TẮC** | KHÔNG dùng 4 tên FPT/ACB/MBB/HDB (hindsight, N=1). Định nghĩa ứng viên: **rổ tập trung k∈{6,10} tên** chọn từ ĐÚNG pool custom30V (in_universe ∧ golden_floor ∧ rating≤3 ∧ !banned) theo **composite v3 + tier A/B của route**, EW, rebal quý — tức là "chất lượng cao, tập trung" thay cho "rẻ, rộng". | Chưa; Job U đã có khuôn `conc_tail.py` (rút ngẫu nhiên k tên) làm **đối chứng null** |
| **D. Không park** (tiền ở egg theo proxy tầng 1) | park=0 | Có (`PARK_STATES=3:0.0`) |

**Đối chứng null bắt buộc cho C:** phân phối 300 draw ngẫu nhiên k tên từ cùng pool (Job U đã đo: k=6 CAGR trung vị 14,96%, 5th 7,94%, MaxDD trung vị −51%). C chỉ được gọi là "có edge" nếu vượt **phân vị 90** của null — không phải chỉ vượt trung vị.

### 3.2 Khuôn đo (giống hệt cho A/B/C/D)

- Cửa sổ 2014-08→2026-06, universe_pit, T+1, phí 0,1%/chiều — y nguyên pin R3.
- **Tiền nhàn rỗi = proxy tầng 1**, chạy thêm tầng 2 làm stress.
- Đo ở park fraction **0,30** (knob live) VÀ 0,0 (để tách "rổ" khỏi "mức park").
- Metric: CAGR / Sharpe / MaxDD / Calmar + **bootstrap ghép cặp** L=21 B=4000 seed 12345 (đúng `paired_v2.py` đã bác "đỉnh 30%") cho E[Calmar], P(X > D), DD 5th-pct.
- Cổng DD giữ nguyên prereg v2: DD5th ≥ DD5th(park=0) − 2,0pp.
- IS 2014-19 / OOS 2020+; leave-one-year-out; DSR + PBO với `DSR_FAMILY_MANIFEST` ghim.
- **Selfcheck bắt buộc mới:** mỗi chuỗi return rổ phải qua `basket_return_leg_oshares_selfcheck.py` + kiểm đòn 8 quant-skeptic (double-count) TRƯỚC khi đọc số.

### 3.3 Gate Q2

Prereg trước khi chạy (file `PREREG.md`, commit trước log đầu tiên): tiêu chí chọn = **E[Calmar] paired**, tie-break = ứng viên ít tập trung hơn. Không đổi tiêu chí sau khi thấy số.

## 4. Q3 — Quyết định giữ/bỏ/đổi custom30V

Cây quyết định (điền số từ Q1/Q2, không quyết trước):

1. Nếu **D (không park, tiền ở proxy tầng 1) ≥ A** trên E[Calmar] paired VÀ không thua ở tầng 2 ⇒ **BỎ parking**; câu hỏi còn lại chỉ là vận hành tiền trong egg (trần/bậc — Mafee đã kiểm: không có bằng chứng trần).
2. Nếu A > D nhưng **B hoặc C vượt A với P(>A) ≥ 0,60 và vượt null-90** ⇒ **đổi rổ**, wire theo quy trình chuẩn (quant-skeptic CONFIRMED → user → sau đó mới đụng `golive_recommend_v23.py`).
3. Nếu A vẫn tốt nhất ⇒ **giữ custom30V**, nhưng pin lại con số **trên proxy tầng 1** và ghi rõ "parking mua X pp CAGR bằng Y pp DD" — không còn dùng số 0%.
4. Bất kỳ nhánh nào chỉ thắng ở tầng 3 (8,55%) ⇒ ghi là **phụ thuộc khuyến mãi DNSE**, không wire theo.

## 5. Các bước, ai làm, gate

| Bước | Việc | Ai | Gate để sang bước sau | Ước lượng |
|---|---|---|---|---|
| **W0 (đã làm 27/09)** | Snapshot 2 chuỗi FiinPro trước hết hạn trial; registry UNVERIFIED-PIT-CANDIDATE | Mike | — | xong |
| **W1** | Q1: đối chiếu ≥3 mốc/chuỗi với nguồn gốc; dựng `idle_rate_proxy.py` (3 tầng, PIT, forward-fill trong tháng); hiệu chỉnh haircut; đo lại break-even Job U theo tháng | Taylor | quant-skeptic CONFIRMED trên chuỗi proxy (đòn 1 look-ahead + đòn 7 số học); Mike duyệt registry §13 | ~1 phiên dispatch |
| **W2** | Q2: prereg → chạy A/B/C/D + null-300 cùng khuôn ở park 0,30 và 0,0, proxy tầng 1 + stress tầng 2 | Taylor | selfcheck 0 VND + `basket_return_leg_oshares_selfcheck` PASS cả 4 chân; quant-skeptic 8 đòn | ~2 phiên (engine chạy dài) |
| **W3** | Q3: điền cây quyết định, trình user MỘT trang | Mike | user quyết | — |
| **W4** | Nếu đổi rổ/bỏ park: A/B đường tiền live (`park_holdings.py`, `compute_park_trim.py`) đo lệnh PARK_TRIM/PARK_BUY sẽ sinh **trước** khi đổi rail; đổi CẢ 2 rail cùng lúc (bài học `PARK_TARGET_F1` hôm nay) | Taylor + Mike | user ký; hậu kiểm 5 phiên | — |
| **W5** | Ghi carry proxy tầng 1 vào `results_registry.md` như **tham số môi trường**; mọi so sánh tiền-vs-equity về sau bắt buộc dùng nó (không còn 0%) | Mike | — | — |

## 6. Bẫy phương pháp phải tránh (từng cắn thật)

- **Áp spot cho lịch sử** (8,55% cho 2014): Job U tự cảnh báo. ⇒ tầng 1 theo tháng, tầng 3 chỉ nhìn trước.
- **N=1 đội lốt bằng chứng** (AlphaLens 4 tên): ⇒ C phải là QUY TẮC + null-300.
- **Calmar theo 1 đường lịch sử** (đã bác "đỉnh 30%" và quyết định 80% cũ): ⇒ paired bootstrap, không đọc điểm.
- **Double-count giá×khối lượng**: ⇒ selfcheck return-leg + đòn 8 trước khi đọc số, không sau.
- **Registry ≠ production** (pin 3:0.7 gắn nhãn production khi live là 0,8 suốt 54 ngày): ⇒ W4 đổi 2 rail cùng lúc, W5 pin đúng knob live.
- **Họ trial nở làm PBO trôi**: ⇒ `DSR_FAMILY_MANIFEST` ghim ngay từ W2.

## 7. Cần user quyết NGAY (trước khi dispatch W1)

1. **Duyệt proxy 3 tầng** ở §2.2 làm chuẩn cho toàn bộ so sánh tiền-vs-equity (thay hẳn giả định 0%).
2. **Duyệt định nghĩa ứng viên C** ở §3.1 (rổ tập trung theo quy tắc, không dùng 4 tên AlphaLens).
3. **AlphaLens paper hết hạn 30/09**: đề xuất **không gia hạn** như chương trình riêng (N=1, không kiểm chứng được) — kết quả track được giữ làm 1 dòng tham chiếu trong W2, không hơn.
4. Cho phép dispatch W1 ngay sau khi duyệt (Taylor, opus/high, ~1 phiên).
