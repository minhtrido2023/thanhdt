---
kind: registry
status: CANONICAL
source: macro-strategist (native agent) — độc lập với Taylor/backtest, đọc BLIND đến forward-return
group: market-state
writer: macro-strategist, dispatch từng episode, một entry/episode
role: Sổ phân loại NGUYÊN NHÂN VĨ MÔ của mỗi episode khủng hoảng VNINDEX (2 trục: STRUCTURAL vs
  CONFIDENCE/LIQUIDITY; nếu CONFIDENCE — CONTAINABLE vs EXTERNAL-CYCLE) — tách biệt khỏi việc chạy
  backtest để không bị "outcome shape the read" (xem MIKE.md routing table, sự cố 2026-08-24)
---

# VN Macro Regime History — sổ phân loại nguyên nhân vĩ mô từng episode khủng hoảng

**Status: CANONICAL.** Đây là sổ DUY NHẤT ghi lại kết luận đọc-vĩ-mô-độc-lập cho từng episode
khủng hoảng VNINDEX dùng trong backtest/margin-timing của Taylor. Quy tắc nền tảng (xem
`~/.claude/agents/macro-strategist.md`): **agent phân loại KHÔNG BAO GIỜ được biết forward-
return/kết quả backtest của episode đang đọc** — chỉ biết ngày + hành động giá đã kích hoạt
episode đó (arm/trigger date, dd52 threshold). Vi phạm quy tắc này (một người vừa đọc vĩ mô vừa
chạy backtest) là chính sự cố 2026-08-24 khiến vai trò này ra đời: phân loại
LIQUIDITY_POLICY/FUNDAMENTAL_REAL quá thô, không tách được khủng hoảng lạm phát cơ cấu (2007-2012,
mất nhiều năm) khỏi cú sốc niềm tin có mục tiêu (2020 COVID, 2022 SCB — hết trong vài tháng).

## Khung phân loại (tóm tắt, đầy đủ ở agent definition)
- **Trục 1 — Root cause**: `STRUCTURAL` (CPI/tín dụng nội địa đã xấu đi NHIỀU QUÝ trước episode,
  cần 1.5-3+ năm siết chính sách để giải quyết) hay `CONFIDENCE_LIQUIDITY` (trigger cụ thể — bank
  run, scandal 1 công ty, dòng vốn ngoại rút, đại dịch, hoảng loạn thị trường ngoài VN — KHÔNG tự
  nó là bằng chứng mất cân đối vĩ mô nội địa)?
- **Trục 2** (chỉ áp dụng nếu trục 1 = `CONFIDENCE_LIQUIDITY`): `CONTAINABLE` (giải quyết bằng
  MỘT hành động chính sách nhắm đúng mục tiêu, tuần-tháng) hay `EXTERNAL_CYCLE` (gắn xu hướng bên
  ngoài VN không kiểm soát được, không có mốc VN tự quyết được thời điểm kết thúc)?
- **Confidence**: `clean` (bằng chứng đồng thuận nhiều chỉ tiêu độc lập) hay `ambiguous` (bằng
  chứng trộn lẫn — vẫn là câu trả lời hợp lệ, không phải thất bại).

---

## EP-2022-05 — Tan Hoang Minh / SCB bank-run / Fed-hiking FX pressure

**Cửa sổ episode (do caller cung cấp, giá đã biết công khai tại thời điểm đó):** VNINDEX dd52
chạm ≤−20% khoảng tháng 05/2022, kéo dài tới giữa tháng 11/2022.

**Trigger đã biết PIT tại thời điểm episode** (công khai, không phải hindsight): vụ Tân Hoàng
Minh hủy 9 lô trái phiếu (04/2022); Trương Mỹ Lan/Vạn Thịnh Phát bị bắt (08/10/2022) → bank-run
SCB; SBV nâng lãi suất điều hành 2 lần liên tiếp 09-10/2022 (+100bp mỗi lần); Fed tăng lãi suất
mạnh gây áp lực VND; thị trường TPDN đóng băng sau Nghị định 65/2022.

### Trục 1: `CONFIDENCE_LIQUIDITY` — confidence: **clean**

Bằng chứng (đồng thuận, không mâu thuẫn nhau):
- **CPI KHÔNG vượt trần mục tiêu.** GSO: CPI bình quân cả năm 2022 = **3,16%** (trần Quốc hội
  giao là ~4%) — [Vietnam Inflation Rate — Trading Economics/GSO](https://tradingeconomics.com/vietnam/inflation-cpi).
  Chuỗi nội bộ `cpi_vn.py` (proxy, `is_real_nso=False` cho toàn bộ cửa sổ này — đọc caveat ở
  `mike/kb/data_registry/macro/cpi_vn.md`, KHÔNG dùng làm bằng chứng chính, chỉ đối chiếu hình
  dạng) khớp hướng: CPI YoY leo dần từ **1,9% (01/2022) → 3,4% (06/2022) → 4,55% (12/2022)** rồi
  **rơi nhanh về 2,0% (06/2023)** — hình chữ V nhọn, không phải xu hướng cơ cấu dai dẳng.
- **Tín dụng KHÔNG vượt trần đáng kể.** SBV đặt mục tiêu tăng trưởng tín dụng 14% cho 2022, thực
  tế đạt **14,5%** — sát mục tiêu, không phải bùng nổ mất kiểm soát —
  [SBV sets credit growth target to 14 per cent in 2022 — VIR](https://vir.com.vn/sbv-sets-credit-growth-target-to-14-per-cent-in-2022-90311.html).
- **Lãi suất huy động KHÔNG leo thang TRƯỚC episode.** `deposit_rate_vn.py` (Big-4, DEPOSIT_EVENTS
  frozen — xem caveat point-in-time ở registry, nhưng mốc 2022 nằm SAU ngày calibrate 2026-06-19
  nên không mang hindsight bias của chính episode này): lãi suất 12M đứng yên **5,5%** suốt
  01/2021→01/2022, chỉ nhảy lên **6,8%** từ **10/2022** — TỨC LÀ lãi suất huy động nhảy vọt XẢY RA
  SAU khi episode giá đã bắt đầu (05/2022) 5 tháng, không phải NGUYÊN NHÂN đi trước nhiều quý như
  mẫu hình STRUCTURAL đòi hỏi. Đây là phản ứng chính sách với cú sốc, không phải bằng chứng mất
  cân đối tích lũy từ trước.
- **Bản thân 2 đợt nâng lãi suất điều hành (09-10/2022) được công bố và diễn giải LÀ để BẢO VỆ TỶ
  GIÁ, không phải kiềm chế lạm phát nội địa cầu-kéo** — "SBV had to increase its policy rates ...
  due to the weakening of the đồng after the Fed's sharp rate hike" —
  [Vietnam Central Bank to Raise Policy Rates by 100 Bps to Fight Inflation — US News/Reuters, 2022-10-24](https://money.usnews.com/investing/news/articles/2022-10-24/vietnam-cenbank-raises-policy-rates-by-100-bps).
  SBV bán ra **>20 tỷ USD** dự trữ ngoại hối trong năm 2022 để bảo vệ VND (VND mất giá ~8% so với
  USD) — [Vietnam central bank buys dollars to shore up reserves after sell-off — BusinessWorld, 2022-12-28](https://www.bworldonline.com/banking-finance/2022/12/28/495462/vietnam-central-bank-buys-dollars-to-shore-up-reserves-after-sell-off/).
- Trigger có TÊN CỤ THỂ, không mơ hồ: 1 công ty bất động sản (Tân Hoàng Minh) + 1 ngân hàng cụ thể
  (SCB) + 1 cá nhân (Trương Mỹ Lan) — đúng mẫu hình "confidence shock với trigger định danh được"
  theo khung phân loại, KHÔNG phải hệ quả lan tỏa của cung tiền/tín dụng toàn hệ thống.

**Kết luận trục 1:** không tìm thấy bằng chứng CPI/tín dụng nội địa xấu đi nhiều quý trước
episode — ngược lại, CPI/tín dụng bám sát/đúng mục tiêu trong khi episode giá đã nổ ra. ⇒
`CONFIDENCE_LIQUIDITY`, không phải `STRUCTURAL`.

### Trục 2: `CONTAINABLE` — confidence: **clean**

Ba nhánh trigger, MỖI nhánh có MỘT hành động chính sách nhắm đúng mục tiêu, có mốc thời gian rõ:

1. **SCB bank-run (từ 08/10/2022)** → SBV đặt SCB vào diện **"kiểm soát đặc biệt"** ngay khi bank-
   run nổ ra, bơm thanh khoản riêng cho NGÂN HÀNG ĐÓ (không phải gói macro toàn hệ thống) — "The
   central bank placed SCB under its supervision to stem a run ... SCB used the central bank funds
   to help it settle withdrawals" — [Vietnam's Massive Saigon Bank Bailout — AsiaFinancial/CNBC](https://www.cnbc.com/2024/04/17/vietnam-mounts-unprecedented-24-billion-rescue-for-bank-engulfed-in-giant-fraud-documents-show.html).
   Đây đúng mẫu "recapitalize/backstop MỘT ngân hàng" của khung `CONTAINABLE`.
2. **Đóng băng TPDN (sau Nghị định 65, 09/2022 + vụ Tân Hoàng Minh)** → Chính phủ ban hành **Nghị
   định 08/2023** (05/03/2023, ~5 tháng sau) nới lỏng điều kiện gia hạn/tái cơ cấu trái phiếu cho
   tổ chức phát hành — hành động pháp quy nhắm đúng 1 thị trường cụ thể —
   [New regulations on corporate bonds — Allens/KPMG technical update](https://www.allens.com.au/insights-news/insights/2023/03/Vietnams-new-regulations-on-corporate-bonds).
3. **Áp lực tỷ giá/Fed-hiking** → dù trigger gắn với chu kỳ Fed (yếu tố VN không kiểm soát), phản
   ứng của SBV KHÔNG kéo dài nhiều năm theo Fed: SBV nâng 09-10/2022 rồi **CẮT lãi suất điều hành
   ngay 15/03/2023** (lần đầu tiên từ 2020) — "the first rate cut since October 2020 ... Vietnam
   was one of the first countries in the world to cut policy rates while many other central banks
   were still tightening" — [Central bank cuts rates for first time in two years — Focus Economics/Bao Chinh Phu](https://en.baochinhphu.vn/central-bank-cuts-rates-for-first-time-in-two-years-111230315105215919.htm).
   SBV cũng đã quay lại **MUA VÀO** USD để bổ sung dự trữ từ 12/2022 — [BusinessWorld, 2022-12-28](https://www.bworldonline.com/banking-finance/2022/12/28/495462/vietnam-central-bank-buys-dollars-to-shore-up-reserves-after-sell-off/).
   ⇒ VN tự tách khỏi lịch trình Fed trong vòng ~5 tháng — bằng chứng RÕ đây KHÔNG phải "gắn xu
   hướng bên ngoài VN không kiểm soát được" theo đúng nghĩa của nhánh `EXTERNAL_CYCLE`.

**Cùng một chỉ báo stress quay đầu trong vài tháng sau hành động chính sách** — đúng phép thử của
khung: interbank/refi rate đạt đỉnh 09-10/2022 → SBV cắt lãi suất 03/2023 (~5 tháng); CPI đạt đỉnh
cục bộ 01/2023 (~4,9% theo chuỗi proxy nội bộ) → rơi về 2,0% giữa 2023 (~5 tháng).

**Kết luận trục 2:** cả 3 nhánh trigger đều được xử lý bằng hành động chính sách CÓ MỤC TIÊU, có
tên cụ thể (1 ngân hàng, 1 nghị định thị trường TPDN, 1 chu kỳ lãi suất tự tách khỏi Fed) trong
khung thời gian tuần-tháng, không phải năm. ⇒ `CONTAINABLE`.

### Tổng kết EP-2022-05
| Trục | Kết luận | Confidence |
|---|---|---|
| 1. Root cause | `CONFIDENCE_LIQUIDITY` | clean |
| 2. Containability | `CONTAINABLE` | clean |

**Không dùng bất kỳ dữ liệu forward-return/backtest nào để ra kết luận trên** — chỉ dùng CPI/tín
dụng/lãi suất/hành động chính sách có ngày công bố PIT, tất cả đều nằm TRONG hoặc TRƯỚC cửa sổ
episode được giao (05/2022→11/2022) hoặc là hành động chính sách công khai theo sau đó (đến
03/2023) — không phải giá cổ phiếu/VNINDEX sau ngày đó.

---

## Chưa phân loại độc lập — cần dispatch macro-strategist riêng, KHÔNG suy diễn từ episode trên

Các episode khủng hoảng VNINDEX khác đã biết tồn tại (từ lịch sử công khai VN, KHÔNG phải đã qua
quy trình đọc-blind của vai trò này) — liệt kê để không ai lầm tưởng đã có kết luận độc lập:

- **2007–2008**: bong bóng tín dụng/chứng khoán VN vỡ + khủng hoảng tài chính toàn cầu. CPI VN
  từng lên tới ~23% (08/2008) — nghi ngờ mạnh là `STRUCTURAL` nhưng **CHƯA có entry độc lập ở
  đây** — không trích dẫn như đã kết luận.
- **2009–2012 (đặc biệt 2011)**: lạm phát cao kéo dài (CPI ~18-23%), Nghị quyết 11/2011 thắt chặt
  tiền tệ — đây chính là ví dụ "khủng hoảng lạm phát cơ cấu, mất nhiều năm" nêu trong mô tả vai
  trò này, nhưng **CHƯA có entry độc lập ở đây** với trích dẫn PIT đầy đủ.
- **2018 (Q1–Q4)**: VNINDEX đạt đỉnh ~1.200 (04/2018) rồi điều chỉnh mạnh giữa lo ngại chiến tranh
  thương mại Mỹ-Trung + Fed thắt chặt — **CHƯA phân loại**.
- **2020 (COVID, 02-03/2020)**: mô tả vai trò này DÙNG episode này làm VÍ DỤ minh họa khung phân
  loại ("cú sốc niềm tin có mục tiêu ... resolved in months") — đây là narrative NGUỒN GỐC của
  vai trò (từ phân loại thô cũ của Taylor), **KHÔNG PHẢI** kết luận đã qua quy trình đọc-blind độc
  lập của macro-strategist. Cần dispatch riêng để có entry chính thức với trích dẫn PIT.

**Nguyên tắc cho người bổ sung entry mới**: mỗi episode phải qua đúng quy trình — dispatch
macro-strategist với ngày + hành động giá, KHÔNG kèm forward-return/giả thuyết backtest — trước
khi ghi vào bảng trên.
