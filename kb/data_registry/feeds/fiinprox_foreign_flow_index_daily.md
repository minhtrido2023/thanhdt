---
kind: derived-file
status: UNVERIFIED với nguồn ngoài (VNDirect chỉ từ 2018-08); nhất quán nội bộ 2 endpoint FiinPro 2014-2015 495/495 phiên ≤1 tỷ
source: data/fiinprox_foreign_flow_index_daily_20260914.csv (raw: data/fiinprox_investor_flow_raw/foreign_*.txt)
group: feeds
writer: Mike (thủ công qua FiinXMCP execute_api → client.Fetch_Trading_Data fb/fs/fn, by=1d)
upstream: FiinPro-X trial, hết hạn 2026-09-28
created: 2026-09-14
---

# `fiinprox_foreign_flow_index_daily` — khối ngoại mua/bán VNINDEX + ròng HNX theo ngày

2.313 phiên, 2009-06-01→2018-08-31. VNINDEX mua/bán/ròng tới 2015-12-31; 2016-01→2018-08 chỉ HNX (VNINDEX ròng lấy từ `fiinprox_vnindex_investor_flow_daily`, flag `vn_see_investor_flow_file`). Cột: `vnindex_foreign_buy_bn`, `vnindex_foreign_sell_bn`,
`vnindex_foreign_net_bn`, `hnx_foreign_net_bn`, `flags` (tỷ VND nguyên). Lấp khoảng VNDirect
(chỉ từ 2018-08-30). Từ 2014-01 dùng `fiinprox_vnindex_investor_flow_daily` (có tách thoả thuận).

## Bẫy
1. **fb/fs GỒM cả thoả thuận** (không tách) — lô lớn làm méo (vd 2010-12-10 mua 1.762 tỷ, 2012-01-09
   bán 1.869 tỷ, 2012-11-30 mua 1.629 tỷ).
2. HNX `fn`=0 liên tục 2009-06-16→06-23 và 2009-07-20→08-24 ⇒ đã để trống (`hnx_missing`).
3. VNINDEX 2009-07-22, 2009-11-20, 2009-11-23 = 0/0 ⇒ trống (`vn_missing`); 2009-12-07 trống.
4. Đối chiếu nội bộ: VNINDEX fb−fs (endpoint giao dịch) vs khớp lệnh+thoả thuận (endpoint nhóm NĐT) 2014-2015: 495/495 phiên lệch ≤1 tỷ (chỉ do làm tròn) — cùng nhà cung cấp, KHÔNG thay được đối chiếu nguồn ngoài.
5. Tổng năm VNINDEX ròng: 2009 +2.048 (từ 06/2009) · 2010 +14.915 · 2011 +1.135 · 2012 +3.173 · 2013 +5.504 · 2014 +2.881 · 2015 +2.036 tỷ. HNX: 2016 +1.053 · 2017 −304 · 2018 (tới 08) −758 tỷ.

↩ [Về nhóm feeds](index.md) · [Về index tổng](../index.md)
