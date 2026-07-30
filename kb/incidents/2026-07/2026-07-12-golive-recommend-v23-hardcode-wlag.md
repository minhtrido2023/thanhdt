---
kind: incident
date: 2026-07-12
topic: golive-recommend-v23-hardcode-wlag
title: >-
  2026-07-12 — golive_recommend_v23 (money-path) hardcode w_LAG=65% vô điều kiện, lệch edge-conditional gate của pinned R3 — gây REBALANCE flag GIẢ trên output sống 07-11
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-12 — golive_recommend_v23 (money-path) hardcode w_LAG=65% vô điều kiện, lệch edge-conditional gate của pinned R3 — gây REBALANCE flag GIẢ trên output sống 07-11

**Hiện tượng:** trong lúc Taylor scoping đề xuất tăng tỷ trọng w_LAG (`Taylor_20260712_070206`,
việc user hỏi "có nên tăng tỷ trọng LAG"), phát hiện phụ: `golive_recommend_v23.py:206`
(recommender money-path, output đọc bởi `telegram_recommend.py` + `push_recommend_v23_to_bq`
của Mafee) hardcode `w_tgt = STATE_LAG_WEIGHT` = 65% vô điều kiện ở state 3/4/5 — trong khi
harness pinned R3 (`pt_v23_audit_2014.py:1738-1751`) đã có edge-conditional gate: 65% CHỈ khi
LAG edge-health trailing-12M (`mean12`) ≥4%, else 50%. `pt_v22_dt5g.py` đã có gate đúng từ
trước — chỉ recommender bị drift. Hậu quả sống: output 2026-07-11 in target 65% vs current
49% → cờ "REBALANCE band breached" GIẢ (đúng theo spec: 50% vs 49% = trong band, không cần
rebalance).

**Root cause:** recommender production ban đầu được port trực tiếp từ harness backtest —
đúng tại thời điểm port. Khi harness sau đó được thêm 1 lớp logic mới (edge-conditional gate,
lần thêm không rõ ngày trong lịch sử), không có bước đối chiếu định kỳ giữa recommender
production và harness pinned để bắt drift — chỉ phát hiện tình cờ khi Taylor so sánh trực
tiếp trong lúc làm việc khác (scoping w_LAG).

**Fix:** port `w_lag_target(state, asof)` mirror đúng harness (cùng
`data/lag_edge_health.csv`, cùng logic dedup+sort+`Series.asof`, `EDGE_THR=4.0`, fail-safe
50% khi CSV không đọc được) — commit `a776a9a` (repo WorkingClaude), 1 thay đổi surgical
(1 hàm + 1 dòng section 5), job `Taylor_20260712_072039`.

**Verify:** mirror khớp `0/3107` ngày lệch vs CSV canonical R3 (2014-01-02→2026-06-19);
production function (AST-extracted) `0/40` flip-days + `0/200` random days lệch; live run
(signal 2026-07-10): mean12=0.5%<4% → in đúng target 50%, hết cờ REBALANCE giả; selfcheck
`edge_wlag_gate_selfcheck.py` 13/13 PASS. **quant-skeptic CONFIRMED** (job xác nhận trong
ngày). Tác động thực tế đã kiểm tra (không giả định): BAL/LAG đang rỗng (NEUTRAL parking từ
~04/2026) nên plan T+1 kế tiếp KHÔNG đổi lệnh nào — hiệu lực ngay chỉ ở GUIDANCE (status
json/md báo đúng target, hết flag giả); hiệu lực sizing thật chỉ phát sinh khi LAG refill
(dự kiến cuối 07).

**Bài học:** 1 script "money-path" tồn tại song song với harness backtest gốc mà nó PORT từ
đó cần 1 cơ chế đối chiếu (mirror-check tự động, không chỉ tình cờ phát hiện) — nếu không,
mọi lần harness cập nhật logic (kể cả cải tiến đúng đắn như thêm edge-conditional gate) đều
có nguy cơ để lại 1 bản port cũ chạy sai lặng lẽ cho tới khi có người tình cờ so sánh trực
tiếp.
