# Framework ra quyết định margin ở khủng hoảng VNINDEX — ADAPTIVE, không phải statistical

> Job `Taylor_20260825_105028` · 2026-08-25 · **RESEARCH-ONLY, KHÔNG wire, KHÔNG sửa code production.**
> Mandate (anh John, 25/08/2026): thị trường mới nổi phản ứng thái quá vì NĐT cá nhân >90%; nhiệm vụ
> là **giúp thị trường điều chỉnh về mức hợp lý**, không phải áp cứng nhắc policy kiểu thị trường
> trưởng thành. Deliverable = framework quyết định **adaptive** cho N nhỏ (N_effective ≈ 3-4, không
> phải thống kê significance) — nhận diện cơ chế + observable indicators + quy trình escalate lên
> Mike/anh John, KHÔNG phải công thức auto-trade.

## Nguồn đã dùng (không chạy lại)

- Bobby (macro-strategist, đọc BLIND với forward-return): `kb/data_registry/market-state/vn_macro_regime_history.md` (last_full_analysis 2026-08-25) + `research/macro_monthly_august2026_bobby.md`.
- PIT filter CPI≥6.0%/deposit≥9.0%: `research/capit_margin_pit_filter_full_2007_2026_20260825.md`, `pit_filter_full_2007_2026_clusters.csv`, `pit_filter_full_2007_2026_test.py`.
- Engine tầng vị thế: `research/margin_valuation_spread_phase1_20260823/{README.md,PREREG.md,engine_p1.py,arm_conditions_events.csv}`.
- Cơ chế thu nhập/mã đơn: `research/extreme_bottom_mechanism_classifier_20260823/{README.md,classification.csv}` (job `Taylor_20260823_110750`, Phase-0, **không mù outcome** — tự khai ở đó).
- Panic-buy index-level: bus finding `cycle-fear-backtest-20260822` + `postshock-base-formation-20260823` (cả hai đã ĐÓNG SỔ, không mở lại).
- Chính sách rào chắn tái dùng: `kb/projects/discretionary-margin-policy-20260823.md`.
- BQ trực tiếp (forensic, không phải backtest): breadth oversold daily 08/2022-12/2022, VNINDEX daily giá 06-10/2022 (query trong job này, dùng để giải thích Phần 1).

---

## PHẦN 1 — Forensic: vì sao 11/2022 (đáy sâu nhất, dd52 −40,3%) không sinh washout event?

### Cơ chế engine (đọc trực tiếp `engine_p1.py`, dòng 1142-1253)

Washout event của CAPIT được định nghĩa qua **breadth RSI**, không phải index-level:
```
oversold(t) = tỷ lệ mã trong ticker_prune có D_RSI(t) < 0.30
ws = {ngày t : oversold(t) >= WASHOUT_GATE (0.30)}
```
Các ngày trong `ws` được **gộp cụm**: nếu khoảng cách LỊCH giữa 2 ngày oversold liên tiếp `< 30 ngày`
thì chúng thuộc **CÙNG MỘT cụm**. Mỗi cụm chỉ sinh **MỘT** sự kiện CAPIT duy nhất, neo tại **ngày ĐẦU
CỦA CỤM** (`d0 = grp.iloc[0]["time"]`) — không phải ngày oversold cao nhất, không phải ngày dd52 sâu
nhất. `state`, `dd52w`, và size đều tính **tại `d0`**, không phải tại đáy thật.

### Bằng chứng đo trực tiếp — breadth oversold hằng ngày 08→12/2022 (BQ, query trong job này)

| Khoảng | oversold min→max | Diễn giải |
|---|---|---|
| 09-07 → 09-16 | 0,02 → 0,08 | dưới ngưỡng 0,30, chưa vào `ws` |
| **09-19** | 0,289 | **suýt** chạm ngưỡng (0,289 < 0,30) — chưa tính |
| **09-28** | **0,3554** | **NGÀY ĐẦU** chạm ngưỡng ⇒ `d0` của cụm |
| 09-29 → 10-13 | 0,34-0,67 (dao động) | liên tục trong `ws`, cùng cụm (gap luôn <30 ngày) |
| 10-14 → 10-20 | 0,10-0,22 | RỚT dưới ngưỡng — nhưng gap lịch tới lần chạm tiếp theo (10-21) chỉ **7 ngày** < 30 ⇒ **KHÔNG tách cụm** |
| 10-21 → 10-26 | 0,26-0,59 | vẫn cùng cụm |
| 10-27 → 11-03 | 0,19-0,26 | rớt dưới ngưỡng, gap tới 11-04 chỉ **8 ngày** < 30 ⇒ **KHÔNG tách cụm** |
| 11-04 → 11-16 | 0,32-**0,769** | đỉnh oversold **11-15 = 0,7689** (đúng ngày dd52 chạm đáy −40,3%) — **VẪN CÙNG CỤM với 09-28** |

Toàn bộ khoảng 2022-09-28 → 2022-11-16 (7 tuần, gồm cả đỉnh hoảng loạn 11-15) là **MỘT cụm duy nhất**
vì khoảng gap lịch lớn nhất giữa hai lần chạm ngưỡng liên tiếp chỉ là **9 ngày** (10-26→11-04) —
không bao giờ đạt 30 ngày cần thiết để tách cụm mới. ⇒ Cụm này CHỈ sinh **một** sự kiện, neo tại
**2022-09-28** (đúng là **E11** trong bảng arm §3 của Phase1 PREREG, dd52 −25,2%) — không có sự kiện
riêng nào ở 11-15.

### Vì sao E11 (09-28) tự nó cũng bị chặn (`size=0`)

`capit_base(state, dd52w, vn_cooling)` (dòng 774-779): với state=**BEAR(2)**,
`size = 0,5 if (dd52w > -25% or vn_cooling) else 0,0`. Tại 09-28, dd52 = **−25,2% ≤ −25%**. Giá VNINDEX
rơi liên tục −1,5%…−3%/phiên từ 09-26 đến 10-11 (1174,35 → 1006,20 theo dữ liệu Close BQ đo trong job
này) — biến động thực (`rv10`) gần chắc chắn đang ở **đỉnh cục bộ**, nên `vn_cooling` (rv10 ≤ 85% đỉnh
30 ngày) **rất khó = True** ngay tại ngày bắt đầu một đợt bán tháo. Hai điều kiện `dd52w>-25%` và
`vn_cooling` đều fail ⇒ **size = 0**. Đây khớp đúng với dòng đã công bố ở Phase1 README: *"E9
2022-04-19 (postbull) và E11 2022-09-28 ... bị chính cổng CAPIT chặn (size=0)"*.

### Kết luận Phần 1 — hai lỗi cơ chế CHỒNG LÊN NHAU, không phải một

1. **Lỗi "first-touch anchor"**: cụm 7 tuần dùng NGÀY NÔNG NHẤT (đầu cụm) để định giá toàn bộ cụm.
   Đáy thật (dd52 −40,3%, oversold 0,77 — sâu và rộng hơn hẳn ngày anchor) **vô hình hoàn toàn** với
   logic sizing, dù chính engine ĐÃ "biết" oversold đạt đỉnh ở đó (dữ liệu breadth có, chỉ không được
   dùng vì đã bị "dùng hết" cho `d0` sớm hơn).
2. **Lỗi "gate cứng đúng lúc cần nó nhất"**: NGAY CẢ nếu anchor đúng lúc, gate BEAR
   `dd52w<=-25% and not cooling ⇒ 0` tắt CHÍNH XÁC khi thị trường vừa đủ sâu để đáng mua — nghịch
   lý cổ điển "mature the deeper it gets, but the engine reads deep+volatile as too-dangerous-to-buy"
   mà chưa có override maturity nào (MATURITY=ew2d/postbull đều OFF theo mặc định `R3`) chỉnh sửa nó.
3. Hai lỗi này **cộng hưởng**: kể cả sửa lỗi (1) (anchor đúng ngày 11-15), lỗi (2) vẫn tắt size vì
   dd52 lúc đó còn sâu hơn (−40,3% ≪ −25%) và vn_cooling gần chắc chắn vẫn False giữa đáy hoảng loạn.

**Không phải "trigger có bỏ sót đáy" theo nghĩa thiếu dữ liệu** — dữ liệu breadth+giá đều có, đúng và
đầy đủ. Đây là **thiết kế đã khai báo trong docstring** (dòng 100-119: gate MATURE-vs-first-leg là
CHỦ Ý, để tránh mua sớm vào một cú sập chưa đáy) nhưng đang chặn ĐÚNG episode mà `postshock-base-
formation-20260823` (job khác, đã REFUTED shape-based timing) và `cycle-fear-backtest-20260822`
(nhóm `group_c` — mua INDEX tại đáy 2022-11-15 cho VNINDEX fwd12m **+23,1%**) đều gợi ý là một trong
những đáy sinh lời tốt nhất mẫu 2014-2026 (xem Phần 2).

---

## PHẦN 2 — Bảng coverage: 5 episode Loại-2 (+ 1 hàng đối chứng Loại-1) × trigger hiện tại

Cấu trúc: 5 cửa sổ `dd52<=-20%` **sau 2018** (đủ dữ liệu engine từ 2014, PIT filter đầy đủ) + một
hàng đối chứng toàn bộ khối STRUCTURAL 2007-2012 (8 sub-cluster, gộp 1 hàng — engine KHÔNG có bằng
chứng ở đây, cửa sổ audit chỉ từ 2014).

| Episode (cửa sổ dd52≤−20%) | Nhãn Bobby (registry, real-time) | PIT filter (CPI≥6,0%/deposit≥9,0%) | Trigger hiện tại (dd52≤−20% + bear_washout) | Forward 12M median mã (trích Phase-0, KHÔNG chạy lại) |
|---|---|---|---|---|
| **2007-2012 (8 sub-cluster, gồm 2012-08 ACB/Bầu Kiên)** | `STRUCTURAL`/`MULTI_YEAR` (clean) | **BLOCKED cả 8/8** (CPI 6,9-28,3% hoặc deposit 7,5-14,0%, xem `pit_filter_full_2007_2026_clusters.csv`) | **KHÔNG có bằng chứng engine** — cửa sổ audit `engine_p1.py` chỉ từ 2014-01-02 | N/A trên trigger thật; mechanism-classifier (job khác, hindsight-aware) đo tại 2012-08→2012-11-02 (đáy): med12 cổ phiếu **+26,3%**, ΔROE **−45,0%** (AMBIGUOUS A≠B — bank-run nhưng nền vẫn cơ cấu) |
| 2018-05-28→2019-02-18 (dd52 min −27,1%) | `CONFIDENCE_LIQUIDITY`/`CONTAINABLE` — confidence **ambiguous** | **PASS** (CPI max 4,70%, deposit max 6,8-7,0%) | **ARMED**: E4 (2018-05-28, dd52−22,6%) + E5 (2018-07-05, dd52−25,3%), production size đầy đủ (cả 2 ở state≠2 hoặc dd52>−25%) | Từ đáy 2019-01-03: med12 cổ phiếu **+0,8%**; VNINDEX fwd12m từ arm **+4,3%** — episode NGƯỢC giả thuyết ("liquidity trigger" nhưng lợi suất kém) |
| 2020-03-11→2020-05-08 (dd52 min −35,7%) | `CONFIDENCE_LIQUIDITY`/`CONTAINABLE` — clean | **PASS** (CPI max 5,75%, deposit max 6,5%) | **ARMED**: E7 (2020-03-11, dd52−20,8%), production size đầy đủ | Từ đáy 2020-03-24: med12 cổ phiếu **+96,7%**; VNINDEX fwd12m **+44,2%** — episode ủng hộ mạnh nhất mẫu |
| 2020-07-27→2020-08-03 (dd52 min −23,4%) | cùng episode COVID (Delta-wave dư chấn) | **PASS** (CPI max 3,20%, deposit max 5,7%) | **ARMED**: E8 (2020-07-27), production size đầy đủ | Không tách riêng trong mechanism-classifier (thuộc cùng cụm COVID với dòng trên) |
| 2022-05-13→2022-07-29 (dd52 min −24,8%) | `CONFIDENCE_LIQUIDITY`/`CONTAINABLE` — clean | **PASS** (CPI max 3,40%, deposit max 5,5%) | **ARMED**: E10 (2022-06-15, dd52−20,6%), production size đầy đủ | Chung episode với dòng dưới (arm 2022-05-13→đáy 2022-11-15 mechanism-classifier coi là MỘT episode) |
| **2022-09-19→2023-05-09 (dd52 min −40,3%, chứa đáy 11-15)** | `CONFIDENCE_LIQUIDITY`/`CONTAINABLE` — clean | **PASS** (CPI max 4,90%, deposit max 7,5%) | **BLOCKED tại arm (E11, 09-28, size=0)** — xem Phần 1; đáy thật 11-15 **không sinh event riêng** | Từ đáy 2022-11-15: med12 cổ phiếu **+42,4%**; VNINDEX fwd12m **+23,1%** (`cycle-fear-backtest` group_c); nhưng ΔROE **−38,8%** đến **−42,6%** (AMBIGUOUS A≠B — earnings sụt THẬT, không chỉ giá bị ép) |

### Đọc bảng — 3 quan sát chính, không suy rộng quá N

1. **PIT filter tách đúng 13/13 cluster có dữ liệu** (8 Loại-1 BLOCKED, 5 Loại-2 PASS), 0 false-
   positive/false-negative trên tập đã quan sát — đây là kết quả đã kiểm chứng (`Taylor_20260825_052019`,
   quant-skeptic CONFIRMED trên finding liên quan `backtest-2008-v24-corrections-applied`), KHÔNG phải
   claim mới của job này.
2. **Trigger hiện tại (dd52+washout) PASS PIT nhưng KHÔNG BAO GIỜ tự nó phân biệt "đáng vào" khỏi
   "chưa đáng vào"** trong nhóm Loại-2: nó armed đầy đủ ở 2018 (episode NGƯỢC giả thuyết, +0,8%) và ở
   2020-03 (episode ủng hộ mạnh nhất, +96,7%) **bằng đúng cùng một cơ chế**, còn lại đúng episode có
   forward return tốt thứ nhì (+42,4%, sau khi đã PASS PIT) thì **bị mất hoàn toàn** vì lỗi cơ chế ở
   Phần 1. Ba kết quả (kém / tốt nhất / mất) từ CÙNG MỘT rule, không có tín hiệu nào phân biệt trước.
3. **2012-ACB (dòng đối chứng) là ca cảnh báo quan trọng nhất cho Phần 3**: nó là một trigger Loại-2
   kinh điển (bank-run, 1 cá nhân, 1 ngân hàng cụ thể) NHƯNG xảy ra **trong lúc CPI vẫn ở 6,9%** — nền
   Loại-1 chưa giải toả — nên PIT filter đúng đắn BLOCK nó dù forward return hoá ra dương (+26,3%,
   biết SAU). Đây là bằng chứng KHÔNG nên tự dùng nhãn "trigger có tên cụ thể = Loại 2 = an toàn" mà
   bỏ qua bối cảnh macro nền — đúng lý do Bobby phải đọc bối cảnh REAL-TIME trước khi bất kỳ ai xem
   giá, không suy nhãn ngược từ hình dạng giá.

---

## PHẦN 3 — Framework quyết định ADAPTIVE cho Loại-2 (escalate, không auto-trade)

### Vì sao KHÔNG dùng thống kê ở đây (đúng tinh thần mandate)

N_effective ≈ 3-4 (Bobby's registry: MEGA-2007-2012 = 1 cụm, COVID = 1, SCB/2022 = 1, 2018 ambiguous
≈0,5). Không DSR, không PBO, không p-value — **quy tắc §18 `coding_guidelines`** ("N là SỰ KIỆN ĐỘC
LẬP, không phải số dòng") áp dụng đúng ở đây: 5 dd52-cluster ở bảng Phần 2 chỉ là **3 sự kiện độc lập
thật** (2018 / COVID / SCB), 2020-03 và 2020-07 KHÔNG độc lập với nhau, 2022-05 và 2022-09 cũng vậy.
Bất kỳ ai báo cáo "5/5 Loại-2 PASS PIT" như bằng chứng thống kê là sai N — đây CHÍNH XÁC là lý do
mandate yêu cầu framework **quan sát-và-quyết-định-từng-lần**, không phải công thức đã calib.

### Điều kiện CẦN (tất cả TRUE) trước khi escalate — không đổi thứ tự

1. **Bobby xác nhận Loại-2 real-time**, đọc BLIND với forward-return (đúng vai trò
   `macro-strategist`, KHÔNG dùng phân loại hồi tố kiểu `extreme_bottom_mechanism_classifier` —
   chính file đó tự khai "N=7, người phân loại đã biết đáp án trước... KHÔNG thể dùng làm điều kiện
   live", dòng 128-137 của README job đó).
2. **PIT filter (CPI<6,0% VÀ deposit<9,0%) PASS tại NGÀY QUYẾT ĐỊNH** — không phải tại ngày trigger
   kỹ thuật đầu tiên; đọc lại MỖI phiên còn trong cửa sổ (đúng cách `golive_recommend_v23.py` đánh
   giá, không chỉ 1 lần lúc fire — bài học từ chính vụ 2012-08 ở trên).
3. **≥1 observable overreaction indicator** (danh sách dưới, KHÔNG đóng danh sách) đang ở vùng cực
   đoan — nếu 0 indicator xác nhận, đây là "Loại-2 trên giấy nhưng thị trường CHƯA overreact", không
   escalate.

### Observable indicators — causal, real-time, không look-ahead (đề xuất khởi điểm, mở)

| Indicator | Vì sao causal/real-time | Cảnh báo đã đo được |
|---|---|---|
| **Breadth panic ratio** (`oversold` = %mã D_RSI<0,3, đúng công thức engine) | Tính được cuối mỗi phiên, không cần dữ liệu tương lai | **KHÔNG dùng riêng theo cụm 30-ngày-gap của engine hiện tại** — Phần 1 đã chứng minh cách gộp cụm này tự làm mù chính chỉ báo. Dùng GIÁ TRỊ NGÀY (đỉnh oversold trong cửa sổ đang mở), không dùng ngày-đầu-cụm. |
| **Volume/thanh khoản hoảng loạn** | Volume_Max1Y_High, Trading_Value_Total_1W đã có trong `ticker`/`ticker_1m` | Chưa đo riêng trong job này — đề xuất mở, cần Winston/Taylor đo lại nếu muốn wire |
| **Valuation spread PIT** (EY thị trường − lãi vay, DY payer − deposit) | Đã dựng ở `margin_valuation_spread_phase1_20260823` — nhưng đã **NO-GO ở tầng engine** (tín hiệu 0,0086pp < nhiễu 0,3854pp harness, 45 lần). **Không dùng làm gate cứng**, chỉ dùng làm bối cảnh định tính (đã có sẵn `display-only` trong EOD report, §7 file Phase1) |
| **Policy response lag** (SBV đã hành động nhắm đúng mục tiêu chưa — vd bơm thanh khoản ngân hàng cụ thể, nới Nghị định TPDN) | Đây chính là Trục 2 (`CONTAINABLE`) của Bobby — quan sát được real-time qua tin chính sách, KHÔNG suy từ giá | 2022: SBV kiểm soát đặc biệt SCB **cùng ngày** bank-run (08/10) — độ trễ 0. 2012: SBV bơm 17.000 tỷ **cùng tuần** bắt Bầu Kiên — độ trễ ~1 tuần. Cả hai đã CONTAINABLE ngay tại thời điểm, không cần biết trước outcome giá |
| **US Pillar (VIX/SPX drawdown)** | Đã có sẵn trong `us_market_history.csv`, dùng lại nguyên (đã wire cho MGE_GATE="conviction" nghiên cứu, không production) | Phân biệt "VN-specific không lây từ Mỹ" (điều kiện conviction cao hơn) khỏi "đồng pha với risk-off toàn cầu" |
| **Index vs breadth divergence** | So `dd52` VNINDEX với breadth percentile — nếu index rơi mạnh mà breadth CHƯA rơi tương xứng ⇒ còn "đá tảng" lớn (megacap) đang gánh, chưa phải capitulation rộng | Chưa đo trong job này — đề xuất mở |

Taylor **KHÔNG tự giới hạn** ở danh sách này (đúng yêu cầu dispatch) — mỗi episode tương lai có thể
cần indicator riêng (vd episode do tỷ giá sẽ cần dự trữ ngoại hối SBV, chưa từng cần đo tới nay).

### Khi hội đủ 3 điều kiện CẦN — escalate lên Mike + anh John, KHÔNG auto-trade

Payload escalate bắt buộc 4 phần:
- **(a) Nhãn Bobby** — STRUCTURAL/CONFIDENCE_LIQUIDITY, trục 2 nếu áp dụng, confidence (clean/ambiguous), link entry registry.
- **(b) Indicators đang ở mức nào** — số thật ngày hôm đó (không suy diễn), kèm so sánh với 3 episode lịch sử ở bảng Phần 2 (không phải ngưỡng cứng calib — N quá nhỏ để calib).
- **(c) Đề xuất size** — cơ sở đã xác nhận qua risk-auditor (Spyros, 2026-08-25, CONDITIONAL-APPROVE):
  - Trần **≤5% NAV equity sleeve tổng** (vốn tự có, NOT exposure). Cơ sở: lỗ tối đa trước kỷ luật
    exit −20% ≤ 1% NAV/lần escalate ⇒ equity_cap = 1% / 20% = 5%. **Không dựa vào "2 case × 1%"**
    (lý luận cũ từ chính sách đơn mã, sai bối cảnh — đã thay thế).
  - Trần **exposure tương ứng: ≤6,5% NAV** (= 5% equity × f=1,3 của `capit_margin_lever` thật —
    KHÔNG phải ≤5% NAV exposure; 2 con số khác nhau vì f≠1).
  - Trần đơn mã (nếu chọn từng mã riêng trong basket): ≤1% NAV vốn tự có / ≤3% NAV exposure (giữ
    nguyên từ chính sách đơn mã 08-23 — lý do due-diligence-error risk không đổi theo bối cảnh).
  - **Không dựa vào margin call broker làm lưới an toàn** — DNSE netting cấp ACCOUNT: vị thế đơn
    lẻ về −50% vốn tự có không kích hoạt gọi ký quỹ account nếu tổng account lành mạnh.
  - ⚠️ **Điều kiện B (Spyros)**: Bobby classification phải là **"CONTAINABLE clean"**, không chỉ
    "Loại-2". Nếu Bobby gắn "ambiguous confidence" → **size giảm 50%** (≤2,5% NAV equity thay vì
    5%). Bắt case 2018-style (CONFIDENCE_LIQUIDITY nhưng ambiguous, forward +0,8%).
- **(d) Exit trigger đề xuất** — cùng kỷ luật đã duyệt: **de-lever bắt buộc tại −20% từ giá lúc arm**
  HOẶC rating 8L tụt quá ngưỡng chất lượng, mốc nào tới trước; **cấm average-down** không chạy lại
  due-diligence.
  - ⚠️ **Điều kiện A (Spyros)**: "−20%" là **trigger intent, không phải guaranteed exit price**.
    Basket CAPIT trong panic có thể ADV mỏng → market impact → realized exit tệ hơn −20%. Max loss
    1% NAV là mục tiêu thiết kế dưới điều kiện exit liquidity đủ, không phải đảm bảo tuyệt đối.
- **(e) Combined exposure — BẮT BUỘC trong payload** (Điều kiện C, Spyros): báo cáo tổng equity
  exposure **main V2.4 (BAL+LAG tại state hôm đó) + sleeve đề xuất** vs allocation bình thường của
  state đó. Người duyệt phải thấy combined number, không chỉ sleeve 5% NAV đơn lẻ. Format ví dụ:
  "Main book: 42% invested (BEAR state), sleeve đề xuất: +5% equity = tổng 47% vs bình thường 20%
  (BEAR) → delta +27pp, user xem xét."

### Vì sao human-in-the-loop ĐÚNG với N=3 (không phải né tránh tự động hoá)

1. **N=3 không đủ để calib bất kỳ ngưỡng số nào mà không overfit** — chính `margin_valuation_spread_
   phase1_20260823` đã đo trực tiếp: biên độ nhiễu path của harness (0,3854pp) lớn hơn 45 lần hiệu ứng
   cần đo (0,0086pp). Một công thức tự động calib trên N=3 sẽ KHÔNG THỂ phân biệt "quy luật thật" khỏi
   "path noise" — đúng bài học đã trả giá ở vòng đó.
2. **Cơ chế gộp-cụm/gate hiện tại đã CHỨNG MINH có thể tự làm mù chính nó** (Phần 1) — một rule cứng
   khác (dù thêm bao nhiêu điều kiện) vẫn có nguy cơ y hệt: đúng lúc thị trường cực đoan nhất là lúc
   RSI/volatility/gap-lịch dễ rơi vào những vùng biên mà không ai lường trước khi viết rule. Người
   quyết định real-time có thể NHÌN THẤY "đây rõ ràng là đáy sâu hơn, khác hẳn ngày anchor 7 tuần
   trước" — điều mà rule cố định không tự phát hiện được.
3. **Bối cảnh Việt Nam theo đúng mandate**: NĐT cá nhân >90% ⇒ phản ứng thái quá KHÔNG lặp lại đúng
   hình dạng mỗi lần (2018 là dòng vốn ngoại + margin call; 2020 là dịch bệnh thuần ngoại sinh; 2022 là
   bank-run + TPDN đóng băng + Fed — ba cơ chế hoàn toàn khác nhau, xem Bobby registry). Một công thức
   cố định calib trên cơ chế A sẽ áp sai cho cơ chế B đến C — "market mới nổi cần adapt" đúng nghĩa
   chữ, không phải meta-lý-do để tránh làm việc định lượng.
4. **Chi phí sai lầm bất đối xứng có chủ đích, không phải ngẫu nhiên**: escalate-rồi-từ-chối (Mike/user
   nói "chưa đủ tin") chỉ tốn thời gian; auto-trade-rồi-sai (kiểu gate BEAR đã tắt đúng lúc cần ở Phần
   1, hoặc lặp lại 2018 "trigger armed nhưng NGƯỢC giả thuyết") tốn vốn thật. Với N=3, sai số của một
   rule tự động chưa calib đủ là rủi ro LỚN HƠN chi phí của một bước duyệt người.

### Ranh giới rõ với hệ thống đang chạy

- **KHÔNG thay thế** `capit_margin_lever` (đã LIVE, dd52≤−20%, PIT filter CPI/deposit — hệ thống,
  N-lớn, đã production). Framework này là **TẦNG BỔ SUNG**: khi Loại-2 + PIT PASS + indicator xác
  nhận, đề xuất **NỚI RỘNG có kiểm soát** ngoài những gì trigger cơ học hiện tại tự làm (đặc biệt khi
  trigger cơ học bị mất như ca 2022-09→11 ở Phần 1) — không phải nới lỏng PIT filter hay CAPIT gate.
- **KHÔNG thay thế** `discretionary-margin-policy-20260823.md` (đơn mã, fear-buy DGC/TV1-style) —
  framework này áp cho **sleeve/portfolio-level** khi cả thị trường vào Loại-2, không phải một mã
  riêng lẻ.
- Việc code hoá (nếu Mike/user duyệt) phải qua đúng rigor `coding_guidelines` (`selfcheck`, arch-review
  vì chạm execution path) — **KHÔNG làm trong job này**.

---

## Việc CHƯA làm / giới hạn phải mang theo

1. **Không backtest số liệu framework này** — đúng mandate. Bảng Phần 2 là forensic/mô tả, không
   phải kiểm định thống kê.
2. **Danh sách indicator ở Phần 3 chưa đo hết** (volume panic ratio, index-breadth divergence) — chỉ
   valuation spread và breadth panic (dạng sửa) đã có sẵn hạ tầng đo. Cần job riêng nếu muốn hoàn
   thiện instrumentation trước khi dùng thật.
3. **Deposit rate 2007-2010 chưa wire production** (`capit_margin_pit_filter_full_2007_2026_20260825.md`
   đã ghi rõ — test-only). Không ảnh hưởng framework này (dùng dữ liệu 2011+ production thật).
4. **Trần đã được xác nhận** (risk-auditor Spyros 2026-08-25, user duyệt 2026-08-25): ≤5% NAV equity
   sleeve / ≤6,5% NAV exposure / size giảm 50% khi Bobby "ambiguous". Khai báo slippage exit (điều
   kiện A) và combined exposure field (điều kiện C) đã bổ sung vào §Phần 3(c)-(e) bên trên.
