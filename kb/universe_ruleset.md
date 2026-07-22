# `universe_pit` — changelog bộ tiêu chí

Bảng: **`lithe-record-440915-m9.tav2_mike.universe_pit`** (dataset `tav2_mike` — RIÊNG của đội Mike,
KHÔNG phải `tav2_bq`). Builder: `mike/bin/build_universe_pit.py`.
Thiết kế: `mike/agents/Taylor/research/ticker_prune_replacement_plan.md` §3.

**Nguyên tắc bất di bất dịch:** append-only, bất biến. `ruleset_version` **tăng** khi đổi rule —
KHÔNG BAO GIỜ sửa dòng quá khứ tại chỗ. Mọi backtest phải in `ruleset_version` + **SHA hash tập
membership** vào log và pin vào `data/results_registry.md`.

---

## v1 — 2026-07-22 (job `Taylor_20260722_044614`, G1)

Bộ tiêu chí khởi tạo. User duyệt Q1-Q9 cùng ngày.

| # | Điều kiện |
|---|---|
| B1 | `ICB_Code IS NOT NULL` (loại pseudo-ticker chỉ số) |
| B2 | Tuổi ≥ 60 phiên kể từ dòng đầu trong `tav2_bq.ticker` |
| B3 | **VÀO**: median trading value 60 phiên ≥ **1,0 tỷ VND thực** (neo 2026, khử lạm phát bằng cột `Inflation_7`) |
| B4 | **RA**: trading value < **0,5 tỷ** thực trong **20 phiên liên tiếp** (implement `MAX(tv,20) < 0,5e9`) |
| B5 | `Close ≥ 1.000 VND` |
| B6 | Loại cứng: vắng ≥ 10 phiên liên tiếp trong `ticker` (delist/đình chỉ) |
| B7 | Đã bị loại thì phải đủ điều kiện B3 lại từ đầu (chống nhấp nháy) |
| B8 | **Integrity gate** — từ chối append nếu: lệch >±15% số mã so trung vị 20 ngày · dòng thô `ticker` <90% trung vị 20 ngày · đã tồn tại dòng cho ngày đó |

**Quyết định gắn với v1 (không được đảo mà không có phiên duyệt mới):**
- Trading value **TỰ TÍNH** từ `COALESCE(Price, Close) × Volume`, **KHÔNG** dùng cột dựng sẵn
  `Volume_3M_P50` của ETL ngoài (§3.2b) — tự chủ, không phụ thuộc cột dẫn xuất ta không kiểm soát.
- Ngưỡng 1e9 = **hằng số production có sẵn** (`filter.json:18`), **KHÔNG hiệu chuẩn lại** theo CAGR
  (§8.4 — bẫy tự-tune). Kiểm định G2 xác nhận không cần đổi.
- **KHÔNG có lớp chất lượng (Q-B)** trong tầng universe. Q9 duyệt theo **Q-A + Q-C**: universe thuần
  "có giao dịch được không"; chất lượng để tầng chiến lược (`rating_8l` golden floor) lo.
- Đọc `tav2_bq.ticker` **LIVE**, `BQ_LOCAL_CACHE` bị pop process-local (guidelines §11).

**Backfill v1:** 2000-07-28 → 2026-07-21 · 4.089.541 dòng · 6.339 phiên · 0 trùng lặp.

**Kiểm định G2 (recall vs `ticker_prune` PIT, median-60 tự tính):** 98,6-99,1% tại 7 mốc — không tụt
so với bản dùng cột dựng sẵn. Chân `ENTER` khớp rule tĩnh ±5%; `CARRY_IN` (B4 hysteresis) chiếm
24-32% rổ ⇒ `universe_pit` rộng hơn `ticker_prune` PIT **~1,7×**. Số này cần cho re-pin R3 và hiệu
chuẩn lại mẫu số CAPIT breadth (`WASHOUT_GATE=0.30`, §4.4) — **cổng cứng: cấm cutover CAPIT trước
khi hiệu chuẩn lại.**

**Trạng thái consumer:** CHƯA có consumer nào đọc bảng này. G1 = thêm bảng mới, **không đổi hành vi
production nào**.
