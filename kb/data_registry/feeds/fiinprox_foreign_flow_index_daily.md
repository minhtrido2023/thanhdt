---
kind: derived-file
status: UNVERIFIED — chưa có nguồn chồng lấn (VNDirect chỉ từ 2018-08); PHẦN MỚI tải 2009-06→2012-12, 2013→2018-08 CHƯA tải xong (sandbox lỗi)
source: data/fiinprox_foreign_flow_index_daily_20260914.csv (raw: data/fiinprox_investor_flow_raw/foreign_*.txt)
group: feeds
writer: Mike (thủ công qua FiinXMCP execute_api → client.Fetch_Trading_Data fb/fs/fn, by=1d)
upstream: FiinPro-X trial, hết hạn 2026-09-28
created: 2026-09-14
---

# `fiinprox_foreign_flow_index_daily` — khối ngoại mua/bán VNINDEX + ròng HNX theo ngày

Hiện 901 phiên, 2009-06-01→2012-12-28. Cột: `vnindex_foreign_buy_bn`, `vnindex_foreign_sell_bn`,
`vnindex_foreign_net_bn`, `hnx_foreign_net_bn`, `flags` (tỷ VND nguyên). Lấp khoảng VNDirect
(chỉ từ 2018-08-30). Từ 2014-01 dùng `fiinprox_vnindex_investor_flow_daily` (có tách thoả thuận).

## Bẫy
1. **fb/fs GỒM cả thoả thuận** (không tách) — lô lớn làm méo (vd 2010-12-10 mua 1.762 tỷ, 2012-01-09
   bán 1.869 tỷ, 2012-11-30 mua 1.629 tỷ).
2. HNX `fn`=0 liên tục 2009-06-16→06-23 và 2009-07-20→08-24 ⇒ đã để trống (`hnx_missing`).
3. VNINDEX 2009-07-22, 2009-11-20, 2009-11-23 = 0/0 ⇒ trống (`vn_missing`); 2009-12-07 trống.
4. 2013-01→2014-01 CHƯA có (xem nhật ký plan P3).

↩ [Về nhóm feeds](index.md) · [Về index tổng](../index.md)
