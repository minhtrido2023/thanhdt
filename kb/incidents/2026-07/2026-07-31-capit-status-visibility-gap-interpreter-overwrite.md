---
kind: incident
date: 2026-07-31
topic: capit-status-visibility-gap-interpreter-overwrite
title: >-
  2026-07-31 — `capit_fired` bị hiểu nhầm là "đang giữ vị thế" (thực ra chỉ là điều kiện của
  ngày chạy) khiến mọi kênh báo cáo im lặng về CAPIT từ 07-29 dù vẫn giữ đủ 5 mã; phát hiện thêm
  1 lần artifact 07-30 bị ghi đè bởi sai interpreter (pandas 2 thay vì venv pandas 3 đã pin)
status: open-items
source: >-
  job Taylor_20260731_025222, report mike/agents/Taylor/research/capit_state_visibility_gap_20260731.md
---

# 2026-07-31 — CAPIT status visibility gap + interpreter-mismatch artifact overwrite

**What happened:** Trong lúc trả lời câu hỏi P(BEAR 1 tuần) (job `Taylor_20260731_023251`), Taylor
đọc `data/golive_v23_status.json` (07-30) thấy `capit_fired=False`, `capit_size=0.0`,
`n_capit_basket=0` và báo cáo "CAPIT hiện KHÔNG fire". User (biết rõ CAPIT đã giải ngân thật
07-20/21 và vẫn đang giữ) chỉ ra: "team không có quản lý tốt thông tin". Dispatch điều tra
(`Taylor_20260731_025222`) xác nhận **2 vấn đề riêng biệt**:

1. **Lỗ hổng ngữ nghĩa (root cause chính)** — `capit_fired` trong
   `golive_recommend_v23.py:633` là `breadth_today >= WASHOUT_GATE and not stale`, tính lại HOÀN
   TOÀN MỚI mỗi phiên, KHÔNG đọc bất kỳ state nào. `capit_size`/`n_capit_basket`/`capit_adv_caps`
   đều nằm trong nhánh `if capit_fired:` nên tự về 0/rỗng ngay khi breadth rớt dưới gate — dù vị
   thế thật (đã mua 07-21) vẫn còn nguyên trong sổ. Timeline: fire 07-20→07-28 (7 phiên, size
   0,75), tắt 07-29 (breadth 29,2% < gate 31%), 07-30 breadth 10,0%. **Không có file/bảng nào
   ghi lại "1 episode CAPIT đang mở"** — mọi kênh báo cáo (Telegram `telegram_recommend.py:463`,
   `bq_freshness_check.sh` bơm prompt DollarBill, EOD report) đều gate theo `capit_fired` ⇒ **im
   lặng hoàn toàn về CAPIT từ 07-29 tới 07-31**, dù verify DNSE API trực tiếp 07-31 03:00 ICT xác
   nhận **còn giữ đủ 5/5 mã** (SAB/SIP/VNM/PVT/**NCT** — rổ đúng gồm NCT, `current_ops.md` bản
   trước ghi thiếu chỉ 4 mã, đã sửa cùng lúc với entry này) ở cả SpaceX lẫn ZaloPay, chưa bán mã
   nào.

2. **Sự cố kỹ thuật riêng, phát hiện thêm khi điều tra (1)** — artifact
   `golive_v23_status.json`/`golive_v23_recommendations_2026-07-30.{csv,md}` bị **ghi đè lần 2**
   trong ngày 07-30: pipeline 19:00-19:03 chạy đúng `$DNA_PYEXE` (venv 3.12.13/pandas 3.0.2), ghi
   đúng (LAG 5 upcoming, push BQ 60 dòng — bảng BQ vẫn giữ đúng). Nhưng 19:04-19:08 có 1 lần chạy
   lại bằng `python3` hệ thống (3.10.12/pandas 2.3.3 — bằng chứng
   `__pycache__/lag_live_schedule.cpython-310.pyc` cạnh bản `cpython-312` của venv) — pandas 2
   không unpickle được `earnings_surprise_data.pkl` → `NotImplementedError` → except nhanh → **ghi
   đè** file trên đĩa: `n_lag_upcoming` 5→0 (giả), CSV 60→31 dòng (mất 29 dòng LAG). Vi phạm quy
   tắc interpreter-pinned đã có ở coding_guidelines §8. Cảnh báo `bq_freshness_check.sh:426`
   (LAG-PKL WARN) không bắt được vì nó chạy TRƯỚC bước lỗi này.

**Tác động thực tế:** Đối chiếu độc lập với BQ `recommend_v23.recommendations` 07-30 (nguồn không
bị ghi đè) xác nhận **KHÔNG có thiệt hại** — LAG upcoming sớm nhất DHD T+2 (=08-01), 4 mã còn lại
T+3, không mã nào lẽ ra vào lệnh 07-31 bị bỏ sót; plan DollarBill 07-31 đúng.

**Điểm phụ đã kiểm tra, KHÔNG phải bug**: `w_lag_target=0,50` trong file 07-30 (khác bảng tài liệu
NEUTRAL=0,65) là ĐÚNG THIẾT KẾ — edge-conditional từ 07-12 (`golive_recommend_v23.py:252-271`),
mean12 as-of 07-30 = 0,48% < ngưỡng `EDGE_THR=4,0%` nên hạ tỷ trọng. Bảng NEUTRAL=0,65 trong
CLAUDE.md/`context_pack.md` là **tài liệu cũ chưa cập nhật**, không phải code sai — cần sửa riêng.

**Fix — user duyệt 07-31, đang triển khai (dispatch Taylor, additive-only, không đổi logic mua/
sizing hiện có):**
1. `data/capit_episode.json` — ghi 1 episode khi fire lần đầu, đóng khi exit thật (entry_date/
   basket/size/qty per account/hold_until/status).
2. Đổi mọi kênh báo cáo từ gate `capit_fired` sang `capit_fired OR capit_episode_open`.
3. Fail-closed interpreter trong `golive_recommend_v23.py` (pandas major ≠ 3 → exit, KHÔNG ghi đè
   artifact) — chặn tận gốc sự cố (2).
4. Đổi tên `capit_fired` → `capit_signal_today` cho đúng ngữ nghĩa.
5. Cập nhật `kb/data_registry/market-state/golive_v23_recommendations.md`: `status.json` là
   snapshot ngày bị ghi đè mỗi phiên (KHÔNG phải số vị thế); nguồn lịch sử chuẩn = BQ
   `recommend_v23.status`/`.recommendations` (chưa có entry registry — bổ sung).

**Lesson:** (1) Một field tên gợi ý trạng thái liên tục ("fired") nhưng thực chất chỉ là điều
kiện-của-ngày-hôm-nay là cái bẫy dễ đọc nhầm — kể cả người trong đội (Taylor tự đọc nhầm hôm nay).
Đặt tên field phải phản ánh đúng bản chất (`_today`/`_signal` khác `_state`/`_open`). (2) Interpreter-
pinned không đủ nếu không có guard CƠ KHÍ chặn — quy tắc bằng văn bản (coding_guidelines §8) không
ngăn được 1 lần gõ nhầm `python3` thay vì `$DNA_PYEXE`; cần fail-closed trong chính code. (3) Đúng
kỷ luật "verify artifact, không tin self-report" đã áp dụng cả tuần — lần này áp cho chính đội
mình: đối chiếu DNSE API + BQ độc lập mới lộ ra cả 2 lớp vấn đề, đọc riêng `status.json` sẽ bỏ sót.
