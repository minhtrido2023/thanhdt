# Tái đánh giá V2.4 + margin policy dưới macro framework của Bobby (2026-08-25)

**Job** `Taylor_20260825_040602` · **Loại**: RESEARCH-ONLY, KHÔNG code, KHÔNG đổi config.
**Input**: `kb/data_registry/market-state/vn_macro_regime_history.md` (Bobby, last_full_analysis 2026-08-25).

## TÓM TẮT (đọc trước)

Phát hiện quan trọng nhất KHÔNG nằm trong Phần A (N_effective toàn mẫu 2000-2026) mà ở một hệ quả
sắc hơn: **toàn bộ track record thực nghiệm của V2.4/DT5G (backtest pin CAGR 28,86%/Sharpe 1,90, DSR,
PBO, bootstrap CI) chạy trên cửa sổ 2014+ (T=3106 obs ≈12,3 năm, warm-up DT5G từ 2014) — cửa sổ này
chứa ĐÚNG 0 episode Loại 1 (MULTI_YEAR_STRUCTURAL) của Bobby.** Toàn bộ episode trong mẫu backtest là
2018 (ambiguous CONTAINABLE)/2020 COVID (clean CONTAINABLE)/2022 SCB (clean CONTAINABLE) — 3 episode,
cả 3 đều Loại 2. Đây không phải suy diễn — verify bằng tính lại dd52 trực tiếp từ `VNINDEX.csv` dưới đây.

## Phần A — N_effective và độ dày backtest

**Tính lại dd52 = Close/rolling_252d_max − 1 toàn bộ lịch sử `VNINDEX.csv` (2000-2026), gộp cluster
gap≤30 phiên** (đúng quy ước cluster của `pt_v23_audit_2014.py` washout):

| Cluster | Cửa sổ | Số phiên dd52≤−20% | min dd52 | Phân loại Bobby |
|---|---|---:|---:|---|
| 1 | 2001-07→2003-11 | 522 | −68,5% | chưa phân loại (trước WTO) |
| 2-3 | 2004-08, 2004-11 | 6+4 | −23,6/−20,9% | chưa phân loại |
| 4 | 2006-06→2006-09 | 48 | −36,8% | chưa phân loại |
| 5-12 | 2007-04 → 2012-12 (8 cluster con) | **726** | −71,0% (đáy 2008-09) | **MEGA-2007-2012, TOÀN BỘ Loại 1 STRUCTURAL/MULTI_YEAR** |
| 13 | 2018-05→2019-02 | 118 | −27,1% | Loại 2 CONFIDENCE_LIQUIDITY/CONTAINABLE (ambiguous) |
| 14-15 | 2020-03, 2020-07 | 40+6 | −35,7% | Loại 2 CONTAINABLE (clean, COVID) |
| 16-17 | 2022-05, 2022-09→2023-05 | 35+158 | −40,3% | Loại 2 CONTAINABLE (clean, SCB/Fed) |

**Hệ quả trực tiếp:** cửa sổ backtest production (2014+) chỉ chạm 5 cluster con = 3 episode độc lập
đúng nghĩa Bobby (2018/2020/2022) — **cả 3 đều Loại 2**. Mega-crisis Loại 1 (726 phiên fired, 8
cluster con trải 5,5 năm 2007-2012) nằm HOÀN TOÀN trước warm-up 2014 → **không một ngày nào của
V2.4/DT5G backtest từng "sống" qua một khủng hoảng cơ cấu multi-year kiểu 2007-2012.**

**Trả lời 3 câu hỏi của dispatch:**
1. Kết luận CAGR/Sharpe/Calmar không "sai" — nhưng chúng mô tả một chế độ đã chọn lọc sẵn (post-mega-
   crisis, chỉ chứa cú sốc CONTAINABLE). Không phải overfit theo nghĩa multiple-testing (DSR ở dưới vẫn
   PASS đúng câu hỏi nó trả lời) mà là **coverage gap theo REGIME** — một trục DSR/PBO không đo được.
2. Đúng, edge V2.4 tập trung phần lớn ở giai đoạn CRISIS→RECOVERY (siết 2023 theo `context_taylor_mini.md`:
   "Toàn bộ edge ròng đến từ một lần siết 2023"), và giai đoạn đó là **1 phần của episode 2022 SCB**
   — chỉ 1 trong 3 episode độc lập của cửa sổ backtest. Với N=3 episode độc lập (không phải "nhiều năm
   dữ liệu" — resample theo NGÀY không tạo thêm episode độc lập), câu "edge được test trên đủ mẫu độc
   lập" phải trả lời KHÔNG — 1/3 dominant-episode structure đúng như DSR/PBO annex tự thừa nhận
   ("core edge... T=3106 dominates" — dominance đến từ ĐỘ DÀI đường đi, không phải SỐ episode).
3. **Bootstrap 5th-pct CI (circular block L=21, B=4000) resample TỪ ĐÚNG con đường lịch sử đã có** —
   nó đo phương sai do LUCK trong việc xáo trộn thứ tự block của MỘT chế độ đã quan sát, KHÔNG tạo ra
   một kịch bản chế độ chưa từng xuất hiện trong mẫu. Vì mẫu 2014+ có N=0 episode Loại 1, bootstrap CI
   (CAGR 5th-pct 18,6-21,1%/DD 5th-pct −26 đến −30% tùy pin, xem `results_registry.md` §DSR/PBO annex)
   **về cấu trúc không thể phản ánh rủi ro đuôi kiểu Loại 1** — nó cho biết "trong chế độ đã sống qua,
   xui đến đâu", không phải "nếu Loại 1 quay lại thì sao". Khoảng tin cậy thật RỘNG HƠN những gì bootstrap
   báo, theo hướng không thể lượng hóa bằng chính công cụ đang có (cần một phương pháp khác — mô phỏng
   kịch bản/scenario-based, không phải resampling — nếu muốn con số).

## Phần B — dd52≤−20% gate qua lăng kính 2 loại khủng hoảng

**Full-sample 2000-2026** (17 cluster con ở trên): 726 phiên fired thuộc Loại 1 (8 cluster con,
2007-2012) so với 357 phiên Loại 2 (5 cluster con: 2018/2020/2022) trong phần đã phân loại được —
Loại 1 chiếm ~67% số phiên gate từng fire trong lịch sử VN.

**Nhưng cửa sổ VALIDATION THẬT của `capit_margin_lever`** (job `Taylor_20260803_070954`, N=17 washout
events, kết quả TB +9,75% trên `universe_pit`, dd52≤−20% avg +17,62% p=0,037) **là 2014+, era DT5G**
— đúng cửa sổ 100% Loại 2 vừa xác nhận ở Phần A. Nói thẳng: **bằng chứng thống kê đứng sau gate hiện
tại (+17,62% p=0,037) KHÔNG hề bị bác bỏ bởi lo ngại của Bobby — nhưng cũng KHÔNG hề trả lời được câu
hỏi đó, vì nó chưa bao giờ được kiểm trên một mẫu Loại 1.** Đây là "chưa test", không phải "test rồi
thấy an toàn".

**Điểm cụ thể khiến rủi ro Loại 1 nghiêm trọng hơn mô tả trong dispatch**: 8 cluster con trong
2007-2012 nghĩa là dd52≤−20% **arm/disarm lặp lại ít nhất 8 lần** trong 5,5 năm (04/2007, 07/2007,
12/2007→07/2009 khối lớn, 11/2009, 05/2010, 05/2011, 07/2011→02/2012, 08/2012). Một vị thế margin mở
ở BẤT KỲ lần fire nào trong 7 lần đầu đều có khả năng gặp thêm ít nhất 1 sóng giảm nữa trước khi hệ
thống ngân hàng thực sự lành (NPL về an toàn 2015-2016, Decision 254/VAMC). Đây khác căn bản với 2018/
2020/2022: mỗi episode đó fire 1-2 cluster con RỒI XONG (recovery xác nhận trong 2-4 quý, không tái
phát).

**PIT indicator để phân biệt — candidate cụ thể (chưa build, chỉ đề xuất):**
1. **CPI YoY tại thời điểm gate fire** — GSO công bố hàng tháng, có độ trễ ~2-4 tuần nhưng vẫn PIT
   thật (không nhìn trước so với thời hạn nắm giữ vài tuần-tháng của vị thế margin). Bằng chứng của
   Bobby tự nó là ranh giới rõ: 2007-2012 CPI 8-23% (đã xấu đi NHIỀU QUÝ trước khi dd52 fire) vs
   2018/2020/2022 CPI 2,8-3,5% suốt episode. Ngưỡng thô: CPI YoY >7-8% tại/trước thời điểm fire ⇒
   nghiêng Loại 1 → chặn margin; <5% ⇒ tương thích Loại 2.
2. **Hướng lãi suất điều hành SBV (refi rate) 6-12 tháng trước fire** — đã có sẵn nguồn dùng trong
   registry (`deposit_rate_vn.py`, dùng ở EP-2022-05). Đang HIKE nhiều quý liên tiếp trước fire (như
   04/2008: 7,5%→13% trong 1 tháng; 11/2011: đỉnh 15%) = dấu hiệu Loại 1. Đang CẮT hoặc ổn định = Loại 2.
3. **KHÔNG dùng VIX/SPX làm trục chính** (đúng như dispatch gợi ý) — không phải vì thiếu PIT (VIX
   PIT hoàn toàn) mà vì nó không phân biệt được: một cú sốc niềm tin bên ngoài (Loại 2, ví dụ 2018)
   cũng có thể kèm VIX cao. Trục phân biệt đúng của Bobby là NỘI ĐỊA (CPI/tín dụng/lãi suất), không
   phải panic-gauge ngoại. VIX/SPX đã có vai trò riêng ở macro_gate DT5G (US panic cap) — đừng lẫn 2 vai trò.
4. **Credit growth YoY vs trần SBV** — về mặt khái niệm là trục sạch nhất (SBV công bố mục tiêu hàng
   năm, vượt trần rõ ràng năm 2007/2009/2010 nhưng đúng/dưới trần 2018/2020/2022) nhưng **hiện KHÔNG
   thấy nguồn PIT series sẵn có trong `mike/kb/data_registry/`** — cần Winston xác nhận có nguồn nào
   khả dụng trước khi coi đây là candidate khả thi, không tự giả định.

## Phần C — Discretionary margin sleeve (DGC/TV1-style)

Framework của Bobby áp dụng được ở mức TƯƠNG TỰ (analogy), không trực tiếp (Bobby phân loại
market-wide episode, fear-buy là single-name). Câu hỏi tương đương ở cấp công ty: **"cú sốc giá của
mã này là scandal/niềm tin có cơ chế giải quyết rõ (Loại-2-like — quản lý thay đổi, pháp lý minh oan,
sự kiện 1 lần) hay là dấu hiệu suy yếu cơ cấu tích lũy nhiều quý (Loại-1-like — công ty thật sự xấu
đi, chưa có mốc giải quyết)?"**

DGC hiện có **ý kiến NGOẠI TRỪ trên BCTC 2025** (ghi trong working memory 2026-08-24, chưa từng đưa
vào §6 quy trình due-diligence chính thức) — đây LÀ loại tín hiệu nghiêng về Loại-1-like ở cấp công ty
(kiểm toán không xác nhận được số liệu là dấu hiệu nặng hơn "giá giảm vì tin đồn"), khác về chất với
TV1 (chậm công bố kiểm toán + cổ tức quá hạn — chưa rõ là thao tác hành chính hay tín hiệu xấu thật).
**Đề xuất cụ thể cho quy trình discretionary margin policy (`discretionary-margin-policy-20260823.md`,
CHƯA code):** thêm một bước due-diligence tường minh — "kiểm toán/BCTC có bị ngoại trừ/từ chối không,
nếu có thì KHÔNG cho margin bất kể rating 8L hay giá rẻ đến đâu" — vì rating 8L (ROE/ROIC/FSCORE)
tính từ chính BCTC có thể đã bị vấy bẩn bởi cùng vấn đề khiến kiểm toán ngoại trừ. Đây khác 4 rào chắn
số hiện có (trần vị thế, exit −20%, marginable check) — nó là một GATE ĐỊNH TÍNH thêm vào TRƯỚC các
rào chắn số, không thay thế chúng.

## Phần D — Kết luận thẳng

1. **Backtest V2.4 "mỏng hơn" — đúng, và cụ thể hơn mô tả trong dispatch.** Không phải vì
   N_effective 3-4 áp lên "toàn mẫu 2000-2026" (con số đó đúng nhưng gián tiếp) — mà vì **track record
   THỰC của V2.4/DT5G (2014+) có N=0 Loại 1, N=3 Loại 2**. DSR (1,0000) và PBO (0,20) đều PASS đúng câu
   hỏi chúng được thiết kế để trả lời (search-overfit, config selection) — chúng KHÔNG hề nói gì về câu
   hỏi Bobby đặt ra. Đừng trích DSR/PBO như bằng chứng "đã kiểm chứng đủ" khi bàn tới rủi ro chế độ Loại 1.
2. **`capit_margin_lever` (dd52≤−20%, LIVE, f=1,3) có lỗ hổng rủi ro CHƯA ĐƯỢC TEST, không phải ĐÃ TEST
   VÀ AN TOÀN.** Bằng chứng dương (+17,62% p=0,037, N=17) 100% đến từ mẫu Loại 2. Full-sample lịch sử
   (2000-2026) cho thấy dd52≤−20% fire NHIỀU HƠN (726 vs 357 phiên) và LẶP LẠI 8 lần trong đúng kiểu
   chế độ (Loại 1) mà gate chưa từng gặp khi live.
3. **Có, nên có filter phân biệt trước khi cho margin** — nhưng đây là ĐỀ XUẤT NGHIÊN CỨU, chưa phải
   khuyến nghị wire. Candidate tốt nhất theo PIT-tính và tính sẵn-có dữ liệu: **CPI YoY trend** (rõ
   nhất, đã có bằng chứng phân biệt sạch trong chính registry Bobby) + **hướng refi rate SBV** (nguồn
   `deposit_rate_vn.py` đã có), dùng làm CẶP xác nhận (cả 2 đồng thuận Loại 1 mới chặn, tránh 1 tín hiệu
   nhiễu). Credit growth YoY là trục sạch nhất về lý thuyết nhưng nguồn PIT chưa xác nhận có sẵn.
4. **Chính sách margin discretionary sleeve**: giữ nguyên 4 rào chắn số đã duyệt (trần 3%/5%, exit
   −20%, marginable-check) — KHÔNG đề xuất nới hay siết số. Đề xuất THÊM 1 bước định tính vào due-
   diligence: audit opinion/BCTC bị ngoại trừ ⇒ chặn margin cứng, không phụ thuộc rating hay giá. Case
   DGC hiện tại đang mang đúng dấu hiệu này — cần fundamental-skeptic xác nhận lại tiêu chí này trước
   khi DGC đủ điều kiện margin (nếu marginable), không chỉ dựa rating≤2.

## Verify / auditable

- dd52 tính lại độc lập từ `data/VNINDEX.csv` (Close/rolling(252,min_periods=1).max−1), cluster gộp
  gap≤30 phiên — khớp đúng quy ước washout cluster của `pt_v23_audit_2014.py:1133-1140`. Script inline,
  không lưu file (một lần, không phải backtest cần pin).
- Nguồn khác đối chiếu: `results_registry.md` §DSR/PBO Robustness Annex (2026-07), job `Taylor_20260803_070954`
  (`margin_kelly_feardriven_washout_20260803.md`), `discretionary-margin-policy-20260823.md`,
  `CLAUDE.md` (DT5G warm-up 2014), `context_taylor_mini.md` ("edge ròng đến từ 1 lần siết 2023").
- **KHÔNG chạy backtest mới, KHÔNG đổi `trading_rules.json`, KHÔNG đổi `discretionary-margin-policy-20260823.md`.**
