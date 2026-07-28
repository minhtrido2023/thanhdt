---
kind: external-api
status: CANDIDATE-PARTIAL
source: Khối ngoại — cafef GDKhoiNgoai.ashx
group: feeds
note: chỉ dùng cross-check gần đây (~3 tháng rolling)
tested: 2026-07-23
---

# Khối ngoại — cafef `GDKhoiNgoai.ashx`

**Status: CANDIDATE-PARTIAL ⚠️** (chỉ dùng cross-check gần đây)

## Là gì
JSON `https://cafef.vn/du-lieu/ajax/pagenew/datahistory/gdkhoingoai.ashx?Symbol=VNM&PageIndex=1&PageSize=N`
(redirect 301 từ `s.cafef.vn/Ajax/...`, follow `-L`; cần browser UA). Có per-stock + VNINDEX market.

## Ai ghi / cadence
—

## Bẫy
**Chỉ ~62 phiên rolling (~3 tháng)** — `StartDate/EndDate` BỊ BỎ QUA, luôn trả ~3 tháng cuối. **KHÔNG
có phái sinh** (VN30F trả rỗng). Cash-only. Chỉ hợp cross-check số gần đây, KHÔNG dùng cho backtest
nhiều năm. Test thật 2026-07-23.
