---
kind: derived-file
status: UNVERIFIED-PIT — ĐÃ nghiệm thu 2026-09-27 (Taylor, job Taylor_20260926_164113) và **TRƯỢT** ngưỡng nâng DERIVED: khớp ex-date ±3 phiên đạt 85,7% toàn bộ / 89,2% nhánh delta>0 (cần ≥90%). Không có ca vi phạm PIT nào; khớp tỷ lệ 98,5%. Nâng DERIVED khi có nguồn thứ ba đối chiếu được 345 sự kiện chưa khớp — KHÔNG nới cửa sổ
source: data/fiinprox_oshares_pit_20260926.csv (raw: data/fiinprox_oshares_raw/b*.txt, builder bin/fiinprox_consolidate.py)
group: fundamentals
writer: cron bin/fiinprox_harvest_tick.sh (headless claude -p → FiinXMCP execute_api → client.PriceStatistics().get_freefloat) 2026-09-14→26; hợp nhất bởi Mike 2026-09-26. ĐÃ DỪNG — không có refresh
upstream: FiinPro-X trial, HẾT HẠN 2026-09-28 — snapshot một lần, KHÔNG có nguồn nối tiếp (live dùng oshares_live.py / AIS như hiện nay)
created: 2026-09-26
---

# `fiinprox_oshares_pit` — số CP lưu hành theo NGÀY ĐỔI SỐ, 647 mã, 2013-01-02→2026-09-25

6.404 dòng = 647 mã × (1 mốc đầu + các ngày số CP đổi). Universe: 655 mã `universe_pit`
(`in_universe` từ 2013, ≥250 phiên) — 8 mã provider trả rỗng (LTG BCR BCG VOC BII SSN C21 BBC).
Cột: `ticker, date, shares` (mức SAU đổi), `delta` (rỗng ở mốc đầu), `n_obs` (số phiên provider
có số), `blips` (số 'nháy' ≤5 phiên đã gộp lại), `flags` (`first_obs` · `tiny_delta` = |delta| <
0,001% · `nonpositive_level`).

Thống kê: median 6 lần đổi/mã, max 101; 76 mã không đổi lần nào từ 2013; 349 mã có số từ đúng
2013-01-02, 298 mã bắt đầu muộn hơn (niêm yết sau); **2.434 sự kiện |delta| ≥ 5%** (ứng viên
phát hành/thưởng/tách — tập cần đối chiếu corp-action); 1.226 sự kiện `tiny_delta` (mua lại
cổ phiếu quỹ lô nhỏ / huỷ lô lẻ — không phải lỗi, nhưng không đối chiếu được với corp-action).

## Vì sao cần (lỗ hổng #3 trong `fiinprox-trial-harvest-plan-20260914.md`)
`ticker_financial.OShares` là **TRAP** (RESTATE, 2.667 dòng/576 mã mang số tương lai — xem
`ticker_financial_oshares.md`). File này là chuỗi theo NGÀY, số đổi đúng ngày sự kiện (MBB
1,600→1,631 tỷ cp 2016-03-21 đã kiểm tay 09-14) ⇒ ứng viên thay thế cho cửa sổ lịch sử 2013+.

## Nghiệm thu PIT — ĐÃ LÀM 2026-09-27, kết quả TRƯỢT ngưỡng (Taylor, job `Taylor_20260926_164113`)

Báo cáo đầy đủ + mọi CSV lớp lệch: `agents/Taylor/research/fiinprox_h3_h1_h2_20260927/buoc1_h3_oshares_pit.md`.
Đối chiếu: `tav2_bq.corporate_action` qua semantics `corp_action_lib.pricing_events`
(`event_status != "not_executed"`, KHÔNG `executed_only`), codes `ISS`+`AIS`, 10.468 dòng;
lịch phiên VNINDEX 3.674 phiên.

1. **Khớp NGÀY** — 2.434 sự kiện `|delta/shares_before| ≥ 5%` (tái lập đúng con số đã pin):
   ±0 75,8% · ±1 80,5% · **±3 85,7%** · ±5 87,8% · ±10 90,8%.
   Nhánh `delta>0` (2.337 sự kiện): **±3 89,2%** · ±5 91,4%. Nhánh `delta<0` (97): ±3 chỉ 4,1%.
   ⇒ **FAIL tiêu chí ≥90% ở ±3** theo cả hai cách đọc. Không nới cửa sổ hậu nghiệm.
2. **Khớp TỶ LỆ** — `exercise_ratio` đọc là PHÂN SỐ (1,0 = 100%): **1.846/1.874 = 98,5%** khớp
   `delta/shares_before` trong 2% + 0,2pp. 28 ca lệch (đa số `Phát hành riêng lẻ` / nhiều tranche
   cùng ngày) ở `h3_exratio_mismatch.csv`.
3. **Đối chiếu restate (tiêu chí 2)** — tái lập bằng đúng định nghĩa registry: **2.730 dòng**
   (pin 08-13 là 2.667; bảng đã lớn thêm). Trên 2.135 dòng kiểm được: **0 vi phạm PIT**,
   1.673 (78,4%) nhất quán tích cực, 462 (21,6%) `corporate_action` không kết luận được.
   Tiêu chí "100%" vì vậy **không chứng minh được 100%**, nhưng không có một ca ngược nào.
4. **345 sự kiện không khớp** — phân lớp bằng khoảng cách tới CA gần nhất + dấu delta, KHÔNG gán
   nguyên nhân (§29): `h3_unmatched_classified.csv`. Lớp lớn nhất: `delta>0` có CA cách 4-10 phiên
   (122) và 11-60 phiên (83).

**Điều kiện đóng khoảng cách**: một nguồn thứ ba (bản cáo bạch / thông báo HOSE) cho 345 sự kiện
đó. Dữ liệu đang có KHÔNG có bit nào phân biệt "provider ghi sai ngày" với "`corporate_action`
thiếu dòng".

**Nghiệm thu HẠ NGUỒN (A/B trên R3, 5 chân, `self-check 0 VND` cả 5)**: thay `ticker_financial.OShares`
bằng file này trong `custom_basket` → CAGR 28,86% → 29,78% (**+0,92pp**) nhưng IS/OOS TRÁI DẤU
(−1,21 / +2,98pp). Phân rã bằng chân đối chứng cơ học (`OSHARES_PIT_SCOPE=flat`, bỏ bước nhảy số CP
khỏi chuỗi return): PIT − control chỉ còn **+0,04pp** ⇒ +0,92pp là **artifact của việc chuyển NGÀY
bước nhảy trong một chuỗi return dùng `Close` đã điều chỉnh**, KHÔNG phải dữ liệu tốt hơn. File này
vì vậy **không được bán như một cải thiện lợi nhuận**.

## Bẫy
1. **Mốc đầu `first_obs` KHÔNG phải sự kiện** — chỉ là ngày provider bắt đầu có số (2013-01-02 hoặc
   ngày niêm yết). Đừng đếm nó là "đổi số CP".
2. `n_obs` ≈ 3.410-3.424 cho mã đủ lịch sử — provider ghi mọi phiên kể cả ngày không giao dịch;
   mã `n_obs` thấp = niêm yết muộn hoặc gián đoạn.
3. Lọc nháy ≤5 phiên là quyết định lúc harvest (không phục hồi được raw phiên-theo-phiên) — sự kiện
   thật kéo dài ≤5 phiên rồi hoàn về (rất hiếm) đã bị gộp mất.
4. Tên mã theo FiinPro tại 2026-09; mã đổi tên/huỷ niêm yết trước đó có thể trống hoặc NA.
5. Chưa có cột treasury/free-float — `get_freefloat` có nhưng không lấy (chỉ `outstanding_share`).
6. **Chuỗi này neo theo EX-RIGHT, KHÔNG theo ngày niêm yết bổ sung** (đo 2026-09-27): trong 2.085
   sự kiện `delta>0` khớp ngày, **2.059 khớp `ISS.exright_date`**, chỉ 26 khớp `AIS.effective_date`.
   Khoảng cách `ISS exright → AIS effective` kế tiếp (N=5.558): median **69 ngày** (p25 47, p75 314).
   Ca kiểm tay MBB 2016-10-24: PIT delta 81.559.091 / nền 1.631.181.818 = 5,0000% = đúng
   `exercise_ratio` 0,05 tại ex-right 2016-10-24, trong khi `AIS.effective_date` là 2016-12-05
   (**42 ngày sau**). ⇒ Dùng file này cho "vốn hoá tại ngày t" thì ĐÚNG (giá đã điều chỉnh tại
   ex-right thì số CP phải đổi cùng ngày); hỏi "ngày t có bao nhiêu CP đã NIÊM YẾT hợp pháp" thì
   PHẢI dùng `AIS.shares_total_after`, muộn hơn ~69 ngày.
7. **97 sự kiện `delta < 0` không thể khớp về cấu trúc** — `ISS`/`AIS` chỉ mô tả CP TĂNG; mua lại/
   huỷ không có event_code nào trong `corporate_action`. Đừng đọc 4,1% khớp của nhánh này là "file
   sai"; đó là giới hạn của bảng đối chiếu.
8. **Cột số lượng của `corporate_action` gần như trống cho `ISS`**: `shares_delta` phủ 0% dòng `ISS`
   (98% dòng `AIS`), `shares_total_after` 0%/89% ⇒ chỉ 44/2.085 sự kiện khớp-ngày có số lượng để
   đối chiếu. Phải đối chiếu bằng TỶ LỆ, không bằng số lượng.

## Consumer tiềm năng (CHƯA wire)
`oshares_live.py` (fallback lịch sử), nhánh `sales_yield` (1/PS) composite v3 khi backtest,
`treasury-buyback-oshares-overlay` (đóng, KHÔNG WIRE 09-08 — file này không đảo quyết định đó).

↩ [Về nhóm fundamentals](index.md) · [Về index tổng](../index.md)
