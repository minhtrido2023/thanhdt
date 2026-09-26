---
kind: derived-file
status: UNVERIFIED-PIT — chuỗi ngày đổi số CP có nội tại hợp lý (đổi đúng ngày, không phải ngày BCTC) nhưng CHƯA nghiệm thu với `tav2_bq.corporate_action`; nâng DERIVED khi ≥90% sự kiện |delta|≥5% khớp ex-date/niêm yết bổ sung ±3 phiên
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

## Nghiệm thu PIT — CHƯA LÀM (giao Taylor, H3 trong `fiinprox-data-usage-proposal-20260926.md`)
1. Ghép mỗi sự kiện |delta| ≥ 5% với `tav2_bq.corporate_action` qua `corp_action_lib.pricing_events`
   (KHÔNG `events()` executed_only) ±3 phiên quanh ex-date / `effective_date` AIS: tỷ lệ khớp ngày
   + khớp tỷ lệ (`delta/shares_before` vs `exercise_ratio`).
2. Đối chiếu với 2.667 dòng restate đã biết: file này ở ngày dòng quý phải cho số CŨ (trước sự kiện).
3. Sự kiện không khớp corp-action nào ⇒ liệt kê, không đoán (ESOP/chuyển đổi TP/huỷ niêm yết…).
Đạt ≥90% (1) và 100% (2) trên mẫu ⇒ nâng DERIVED; ngược lại ghi rõ lớp nào lệch.

## Bẫy
1. **Mốc đầu `first_obs` KHÔNG phải sự kiện** — chỉ là ngày provider bắt đầu có số (2013-01-02 hoặc
   ngày niêm yết). Đừng đếm nó là "đổi số CP".
2. `n_obs` ≈ 3.410-3.424 cho mã đủ lịch sử — provider ghi mọi phiên kể cả ngày không giao dịch;
   mã `n_obs` thấp = niêm yết muộn hoặc gián đoạn.
3. Lọc nháy ≤5 phiên là quyết định lúc harvest (không phục hồi được raw phiên-theo-phiên) — sự kiện
   thật kéo dài ≤5 phiên rồi hoàn về (rất hiếm) đã bị gộp mất.
4. Tên mã theo FiinPro tại 2026-09; mã đổi tên/huỷ niêm yết trước đó có thể trống hoặc NA.
5. Chưa có cột treasury/free-float — `get_freefloat` có nhưng không lấy (chỉ `outstanding_share`).

## Consumer tiềm năng (CHƯA wire)
`oshares_live.py` (fallback lịch sử), nhánh `sales_yield` (1/PS) composite v3 khi backtest,
`treasury-buyback-oshares-overlay` (đóng, KHÔNG WIRE 09-08 — file này không đảo quyết định đó).

↩ [Về nhóm fundamentals](index.md) · [Về index tổng](../index.md)
