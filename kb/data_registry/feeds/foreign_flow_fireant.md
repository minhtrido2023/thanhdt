---
kind: external-api
status: CANDIDATE-BLOCKED
source: Khối ngoại — fireant restv2
group: feeds
note: cần Bearer token (auth), chưa test sâu
---

# Khối ngoại — fireant `restv2`

**Status: CANDIDATE-BLOCKED (auth)**

## Là gì
`https://restv2.fireant.vn/symbols/VNM/historical-quotes` reportedly có foreign fields + history sâu.

## Ai ghi / cadence
—

## Bẫy
Trả HTTP 401 "Authorization has been denied" — cần Bearer token (đăng ký free). CHƯA test sâu vì rào
auth; nếu cần deeper-than-2018 history có thể đăng ký token free rồi đánh giá lại.
