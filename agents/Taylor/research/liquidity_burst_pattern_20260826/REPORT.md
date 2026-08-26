# Nghiên cứu: Pattern "Tích lũy thanh khoản thấp → Bùng nổ thanh khoản" (LBC)
dispatch `Taylor_20260826_120750` — 2026-08-26

## Tóm tắt điều hành

**Verdict: INCONCLUSIVE, nghiêng về DEAD-END cho production.** Pattern LBC là **có thật và đo
được** trong lịch sử (85 mã độc lập, 2010-2026), nhưng **không exploitable một cách hệ thống**:
(1) catalyst (BCTC tốt/corp-action) chỉ dẫn tới burst thật trong **~4,9%** trường hợp — quá nhiễu
để làm trigger vào lệnh sớm; (2) return SAU KHI burst đã xác nhận (thời điểm duy nhất một chiến
lược thật có thể hành động) có **median ≈ 0%, tỷ lệ thắng 48,3%** — thua đồng xu — trong khi phần
lớn lợi nhuận đã xảy ra TRONG giai đoạn tích lũy, TRƯỚC khi ai quan sát được burst. Đây chính xác
là bằng chứng chống lại khả năng khai thác hệ thống, không phải ủng hộ nó.

## Bước 1 — TRC profile
Xem `step1_trc_profile.md`. Kết luận chính: TRC có **2 episode LBC nối tiếp** — episode 1
(2022-07→2024-09 tích lũy, catalyst = BCTC Q3/Q4-2024 đột biến NP, burst ×24, giá +107% từ catalyst
đến đỉnh) đã hoàn thành đầy đủ; episode 2 (thông báo thưởng CP 1:3, 2026-08-18) **mới ở pha
catalyst, exright_date 2026-09-15 CHƯA THỰC HIỆN, burst thật CHƯA xảy ra**. Định nghĩa catalyst ở
Bước 2 phải bao gồm CẢ BCTC lẫn corp-action, vì chính episode sinh lời của seed case là BCTC-driven.

## Bước 2 — Định nghĩa & scan lịch sử

**Universe**: `tav2_mike.universe_pit` (CANONICAL), lọc `in_universe=True` tại thời điểm catalyst
HOẶC burst. **Nguồn**: `tav2_bq.ticker` (ADV_3M rolling 63 phiên = `AVG(Price*Volume)` window, month-
end snapshot), `tav2_bq.corporate_action` (ISS, "Cổ phiếu thưởng"/"Trả Cổ tức bằng Cổ phiếu",
executed, exercise_ratio≥0,5 ≈ "tỷ lệ ≥1:2"), `tav2_bq.ticker_financial` (earnings-surge = NP_P0>0
∧ NP_P0>1,5×max(NP_P1..P4) ∧ Revenue_YoY_P0>15%).

**Pipeline**: accumulation run (ADV_3M<2B, ≥6 tháng liên tục) → catalyst (corp-action HOẶC
earnings-surge) rơi trong [accum_start, accum_end+3 tháng] → burst xác nhận (ADV_3M đạt ≥3× mức
tại catalyst VÀ >2B, trong vòng catalyst→catalyst+3-4 tháng).

**Kết quả scan (2009→2026, dữ liệu ticker từ 2009-06 để đủ warm-up rolling)**:
- 2.175 accumulation run (≥6 tháng) trên 1.195 mã — tích lũy dài hạn dưới 2B là **phổ biến**, không
  hiếm (thị trường VN có đuôi thanh khoản rất dày, khớp `ticker_prune` breadth note).
- 2.976 catalyst candidate (563 corp-action, 2.413 earnings-surge) — earnings-surge áp đảo về số
  lượng vì đây gần như xảy ra mỗi quý ở một phần đáng kể universe nhỏ-vốn-hóa.
- **92 sự kiện LBC xác nhận đủ cả 3 pha, in_universe tại catalyst hoặc burst, trên 85 mã độc lập
  qua 16 năm** (N thống kê đúng = 85 mã, KHÔNG phải 92 dòng — nhiều mã có 2 episode như TRC).
  85/92 catalyst là earnings-surge, chỉ 7 là corp-action thuần — **corp-action đơn lẻ hiếm khi là
  catalyst đủ mạnh**; phần lớn burst thật đi theo BCTC đột biến, đúng như phát hiện Bước 1.
- Phân phối theo năm lệch mạnh: **2021 (19 sự kiện)** và **2025 (12 sự kiện)** — hai năm bull
  market bán lẻ VN mạnh nhất trong mẫu — chiếm 34% tổng số sự kiện dù chỉ là 2/16 năm. Đây là dấu
  hiệu **pattern phần lớn ăn theo BETA thị trường tăng tốc thanh khoản chung, không phải alpha
  idiosyncratic thuần túy** — cần trừ VNINDEX return mới đánh giá đúng (xem Bước 3).
- **Red flag đã cắn thật**: 3/85 mã (NKG, TOS, VVS) nằm trong danh sách BANNED VĨNH VIỄN của fleet
  (fraud/thao túng/hạn chế giao dịch đã xác nhận trước đó) — tỷ lệ 3,5% so với base rate toàn
  universe 1,2% (~3× enrichment). N=3 quá nhỏ để khẳng định thống kê, nhưng **hướng đi đúng với
  giả thuyết pump-and-dump** của user, không bác bỏ được.

## Bước 3 — Forward return

⚠️ **Bẫy tautology đã tránh (bài học từ `extreme-bottom-recognition` job trước)**: return đo từ
`cat_date` (T0) cộng dồn CHỒNG LẤN với cửa sổ dùng để XÁC NHẬN burst (catalyst→+3 tháng) — vì
ADV_VND = Price×Volume, burst ADV gần như chắc chắn đi kèm burst giá TRONG CÙNG cửa sổ đã dùng để
chọn mẫu. Số `ret_fwd_120` mean=+75,2%/median=+55,9% là **DESCRIPTIVE, không phải bằng chứng alpha**
— nó gần như đúng theo định nghĩa của chính pattern.

**Test thật (actionable) — vào lệnh TẠI thời điểm burst được xác nhận, giữ tới T+30/60/120 phiên
sau đó** (đây là thời điểm sớm nhất một nhà đầu tư thật CÓ THỂ hành động, vì burst chỉ quan sát
được sau khi nó đã xảy ra):

| Window | N | Mean | Median | Win rate | Std |
|---|---:|---:|---:|---:|---:|
| ret_post_burst_30 | 91 | +9,4% | +3,0% | 52,7% | 27,4% |
| ret_post_burst_60 | 91 | +9,9% | +8,3% | 53,8% | 35,2% |
| ret_post_burst_120 | 90 | +22,7% | **+0,6%** | **50,0%** | 86,7% |
| excess_ret_post_burst_120 (trừ VNINDEX) | 87 | +17,8% | **-3,5%** | **48,3%** | 83,0% |

**Median ≈ 0, win rate < 50%, std cực lớn (83-87%) — mean dương hoàn toàn do đuôi phải (vài mã
thắng đậm, ví dụ đúng kiểu TRC 2024-25) kéo lên, không phải một edge phân phối đều.** t=2,00
p=0,045 trên mean — **marginal và KHÔNG đáng tin**: N=91 sự kiện từ 85 mã, cụm mạnh ở 2 năm
(2021+2025 = 34% mẫu), rõ ràng KHÔNG phải 91 draw độc lập; p-value thô này chưa qua BH/Bonferroni
và chưa hiệu chỉnh clustering — coi là **không có ý nghĩa thống kê thật**.

**LOO theo năm**: mean dao động [+14,5%, +20,3%] khi bỏ từng năm — có vẻ ổn định, nhưng đây là ổn
định của một **con số trung bình bị kéo lệch bởi đuôi phải**, LOO không sửa được vấn đề median≈0/
win-rate<50%.

**Đối chiếu quan trọng**: excess return TRONG GIAI ĐOẠN TÍCH LŨY trước catalyst
(`excess_ret_accum_pre`, T-60→T0) đã là **median +8,9%, mean +36,9%, win rate 71,6%** — GẦN GẤP ĐÔI
win rate của giai đoạn sau-burst. Tức là: **phần lợi nhuận đáng tin nhất của toàn bộ pattern đã xảy
ra TRƯỚC KHI catalyst thậm chí được công bố** — chính là giai đoạn "smart money tích lũy âm thầm"
mà user giả thuyết, nhưng đây là giai đoạn **KHÔNG THỂ phát hiện systematic** (không có tín hiệu
quan sát được để phân biệt mã nào trong hàng trăm mã ADV<2B sẽ là "TRC tiếp theo" — catalyst chỉ
xác nhận ĐƯỢC SAU KHI nó đã xảy ra, và catalyst→burst hit rate chỉ 4,9%, xem dưới).

## Bước 4 — Đánh giá khả năng khai thác

**Catalyst → burst hit rate: 4,9%** (92/1.875 cặp accumulation-run×catalyst-candidate trong lịch
sử dẫn tới burst xác nhận). Dùng riêng "có catalyst trong giai đoạn tích lũy" làm trigger vào lệnh
sớm sẽ sai ~95% số lần — không khả thi làm bộ lọc entry.

**Fit vào sleeve hiện tại?**
- **KHÔNG fit LAG book** (PEAD/earnings drift) — LAG vốn đã reject những mã này TẠI signal time vì
  ADV quá mỏng (đúng như premise user nêu); mở rộng LAG để bắt các mã này sẽ vi phạm chính lý do
  LAG loại chúng ra (thanh khoản không đủ để thực thi, không phải vấn đề tín hiệu).
- **KHÔNG fit Discretionary fear-buy sleeve** — sleeve đó neo vào ĐỊNH GIÁ RẺ + catalyst phục hồi cụ
  thể đã qua due-diligence (`calculated_fear_state_backstop.md`), còn LBC neo vào HÀNH VI GIÁ/KHỐI
  LƯỢNG, không có gate định giá/chất lượng — sai bản chất sleeve.
- **Không đề xuất sleeve mới** ở mức bằng chứng hiện tại — post-burst actionable edge không đạt
  ngưỡng tối thiểu (§18 quant-research: DSR/PBO, quant-skeptic gate) để đi tới bước đó; số liệu
  trung tâm (median≈0, win rate<50%) đã tự loại trước khi cần chạy DSR/PBO chính thức.

**Điều kiện tiên quyết nếu muốn theo đuổi tiếp** (không khuyến nghị theo verdict dưới, nhưng ghi
lại cho đầy đủ theo yêu cầu Bước 4):
1. N=85 mã độc lập, cụm 34% ở 2 năm bull market retail mạnh nhất mẫu — cần N lớn hơn VÀ trải đều
   hơn qua các regime (đặc biệt cần case trong regime BEAR/CRISIS DT5G) trước khi tin bất kỳ con
   số alpha nào.
2. Nếu muốn khai thác phần "tích lũy" (nơi excess return thật sự tồn tại), cần một tín hiệu QUAN
   SÁT ĐƯỢC tại THỜI ĐIỂM TÍCH LŨY (không phải hồi tố) phân biệt được "mã sẽ catalyze" khỏi hàng
   trăm mã ADV thấp khác — nghiên cứu này KHÔNG tìm ra tín hiệu đó (out of scope Bước 2-3), và
   catalyst chỉ xác nhận SAU KHI accumulation đã kết thúc.
3. Poison-pill red flag (3/85 = NKG/TOS/VVS đã BANNED vĩnh viễn) cần điều tra riêng bởi Wendy/
   Spyros trước khi bất kỳ candidate LBC nào (kể cả TRC episode 2 đang mở) được đưa vào bất kỳ
   watchlist chính thức nào — KHÔNG nằm trong phạm vi quant thuần túy của báo cáo này.

**Verdict cuối: INCONCLUSIVE → nghiêng DEAD-END cho production sizing/entry rule.** Pattern có
tồn tại và mô tả đúng những gì đã xảy ra ở TRC episode 1, nhưng đo lường nghiêm ngặt (tách bạch
descriptive/actionable, đúng kỷ luật đã học từ vụ tautology trước) cho thấy **phần lợi nhuận quan
sát được không nằm ở chỗ có thể hành động, và hit rate của catalyst quá thấp để làm trigger**. Ghi
nhận làm tri thức tham khảo (đặc biệt cho TV1/DGC-style discretionary review khi có mã cụ thể), KHÔNG
wire thành rule hệ thống.

## Artifacts
`universe_adv_monthly.csv` (panel ADV_3M toàn universe) · `catalyst_corp_action.csv` ·
`quarterly_financials.csv` · `universe_pit_monthly.csv` · `lbc_events.csv` (92 sự kiện) ·
`lbc_ticker_prices.csv` · `lbc_forward_returns.csv` · `detect_lbc_pattern.py` /
`compute_forward_returns.py` (tái lập được, đọc lại CSV local, không cần chạy lại BQ).

## Caveat look-ahead (bắt buộc khai theo brief)
- `exright_date` (corp-action) là ngày GIÁ đã điều chỉnh, KHÔNG phải ngày thị trường biết tin —
  `public_date` bị vendor UPSERT tại chỗ (TRAP đã ghi ở `corporate_action_bq.md` Bẫy 2b), không
  dùng được làm ngày công bố thật. 7/92 sự kiện là corp-action nên ảnh hưởng nhỏ, nhưng return đo
  quanh corp-action có thể sớm hơn thực tế thị trường biết vài ngày-vài tuần.
- `Release_Date` (BCTC, 85/92 sự kiện) là ngày công bố THẬT, point-in-time sạch — không có bẫy này.
- Universe filter áp dụng TẠI catalyst/burst, KHÔNG áp trong suốt giai đoạn tích lũy (nhiều mã ADV
  thấp tự nhiên nằm ngoài `universe_pit` khi thanh khoản còn mỏng) — đúng tinh thần "mã này có
  investable được không tại thời điểm hành động", không phải trong suốt lịch sử.
