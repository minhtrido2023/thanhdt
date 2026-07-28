---
kind: external-api
status: CANDIDATE-NOT-FEASIBLE
source: Khối ngoại — TCBS / vietstock / HOSE
group: feeds
note: không khả thi qua path đã dò — ưu tiên VNDirect finfo
---

# Khối ngoại — TCBS / vietstock / HOSE

**Status: CANDIDATE-NOT-FEASIBLE (qua path đã dò)**

## Là gì
—

## Ai ghi / cadence
—

## Bẫy
TCBS `apipubaws.../stock-insight/...foreign` = HTTP 404 mọi path đoán (kể cả price control 404 → base
path đã đổi). vietstock/HOSE HTML reachable (200) nhưng KHÔNG có JSON API foreign công khai xác nhận,
cần login/scrape HTML — task không đào sâu scrape. Ưu tiên VNDirect finfo trước.
