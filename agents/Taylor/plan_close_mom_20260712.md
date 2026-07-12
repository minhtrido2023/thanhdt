# Plan: Đóng kênh MOM trong SIGNAL_V11 — scope + đo tác động thật (job Taylor_20260712_012515)

> Trạng thái: **ĐO XONG, CHỜ USER DUYỆT PHẠM VI + CƠ CHẾ. CHƯA sửa code sống.**
> Bối cảnh: chuỗi momentum-deals CP1 NO-GO (0/13 feature qua gate, thành công MOM = dồn mẫu 2020-21)
> + CP-DVR1 NO-GO (nhánh b đóng) — cả 2 quant-skeptic CONFIRMED. User duyệt chủ trương đóng kênh MOM;
> dispatch này đo tác động THẬT của việc đóng lên toàn book V2.4/R3 trước khi chạm production.

## 1. Phạm vi "kênh MOM" trong SIGNAL_V11 — kiểm kê thật

SIGNAL_V11 gán 8 play_type nhánh momentum, nhưng **entry set thật của book BAL chỉ là `TIER_BAL`**
(`golive_recommend_v23.py:47`, `pt_v4_dt5g.py:61`, `pt_v22_dt5g.py:92`, `pt_v23_audit_2014.py:488`):

```
TIER_BAL = [MEGA, MOMENTUM, MOMENTUM_N, MOMENTUM_S, DEEP_VALUE_RECOVERY, RE_BACKLOG_BUY]
```

| play_type | Điều kiện (rút gọn) | Trong TIER_BAL? | Entry thật trong R3 pin 2014→2026-06 |
|---|---|---|---|
| MOMENTUM_N | ta≥155, NEUTRAL, tier C/D, ≤60d release | ✅ | **303** (869 tỷ notional) |
| MOMENTUM_S | ta≥140, BULL/EXB | ✅ | **141** (488 tỷ) |
| MOMENTUM | ta≥155, BULL/EXB, tier C/D | ✅ | **43** (151 tỷ) |
| MEGA | ta≥170, BULL/EXB, tier C/D | ✅ | **0** — chưa bao giờ fire |
| MOMENTUM_QUALITY / MOMENTUM_A / MOMENTUM_S_N / S_PRO | — | ❌ KHÔNG | 0 (chỉ là label diagnostic, không bao giờ mở vị thế BAL) |

→ "Đóng kênh MOM" chỉ có nghĩa trên 4 tier đầu. MOMENTUM_QUALITY/A/S_N/S_PRO **ngoài phạm vi tự
nhiên** (không cần quyết định gì — chúng chưa từng là entry). MEGA đóng = **no-op thực nghiệm**
(0 entry 12.5 năm) nhưng nên đóng cùng cho sạch semantics (cùng logic ta-threshold momentum).

**2 phạm vi đo (pre-registered trong dispatch):**
- **Scope A** — đóng MOMENTUM_N + MOMENTUM_S (2 kênh đã đo NO-GO trực tiếp ở CP1).
- **Scope B** — đóng cả family: MEGA + MOMENTUM + MOMENTUM_N + MOMENTUM_S → BAL chỉ còn
  DEEP_VALUE_RECOVERY + RE_BACKLOG_BUY (+ CAPIT arm, không đổi).

**Đề xuất về MOMENTUM/MEGA generic (câu hỏi 1 của dispatch):** đóng cùng (Scope B) — lý do:
(i) cùng logic entry ta-threshold momentum thuần, chỉ khác ngưỡng/state, không có thesis riêng;
(ii) N nhỏ (43+0 entry) nghĩa là đóng gần như không mất gì NẾU backtest xác nhận (xem §4);
(iii) giữ lại 1 kênh momentum "còi" sau khi đã kết luận pattern không lặp lại được = phức tạp
không công (thêm 1 nhánh phải giải thích mãi về sau). Nhưng đây là đề xuất — số đo cả 2 scope
ở §4 để user chọn.

## 2. Cơ chế đóng (câu hỏi 2 của dispatch): đóng tại TIER_BAL, KHÔNG sửa SQL

**Đề xuất: bỏ tier khỏi `TIER_BAL` ở consumer (giữ nguyên CASE ladder trong `signal_v11_sql.py`).**
Đây chính là biến thể "rate=0 giữ code path": SIGNAL_V11 vẫn chấm điểm và gán label MOM như cũ,
các dòng đó chỉ không bao giờ mở vị thế BAL nữa.

Lý do chọn (so với sửa CASE ladder trong SQL):
1. **Blast radius nhỏ nhất.** SQL SIGNAL_V11 được copy inline ở 6 file khác (phát hiện Phase 0
   momdeal — D1/T8 copies) + hàng chục script nghiên cứu đọc label MOM. Sửa SQL = phải sửa/kiểm
   6+ chỗ, lệch bản là bug kiểu F3 lặp lại. Sửa TIER_BAL = 3 file production, mỗi file 1 dòng.
2. **Rollback = revert 1 dòng/file.** Tắt hẳn bucket trong SQL thì rollback phải khôi phục đúng
   thứ tự CASE (dễ sai — DVR đứng TRƯỚC MOMENTUM_S trong ladder, đổi thứ tự là đổi kết quả).
3. **Diagnostics giữ nguyên.** Label MOM vẫn xuất hiện trong recommend report (mục "info") →
   theo dõi được "nếu còn mở kênh MOM thì hôm nay nó đã mua gì" — bằng chứng sống cho lần review
   sau, miễn phí.
4. Khớp chính xác cách backtest đo ở §4 (knob `BAL_DROP_TIERS` lọc TIER_BAL) — cái được đo =
   cái sẽ deploy, không có khoảng cách implement.

**File phải sửa khi user duyệt (3 file, mỗi file 1 dòng TIER_BAL):**
| File | Vai trò | Dòng |
|---|---|---|
| `deploy_golive_dt5g_v4/golive_recommend_v23.py` | **money-path** (input plan DollarBill → SpaceX/ZaloPay) | 47 |
| `pt_v22_dt5g.py` | sổ tín hiệu production (strategies.py đọc open_positions) | 92 |
| `pt_v4_dt5g.py` | paper tracker (mirror) | 61 |

KHÔNG sửa: `signal_v11_sql.py` (label giữ nguyên), `regime_size_overlay.py` (DEFAULT_BASE_TIERS
chỉ là default — mọi caller production đều truyền base_tiers tường minh), `trading_bot/*` (đọc
output recommend, không có tier list riêng), các script nghiên cứu/archive (inert). Baseline
canonical `pt_v23_audit_2014.py` giữ TIER_BAL đầy đủ + knob env `BAL_DROP_TIERS` (đã thêm job
này, default no-op byte-identical) — nếu duyệt đóng, lệnh pin mới thêm `BAL_DROP_TIERS=...` và
re-pin theo đúng §8.

Lưu ý ranh giới: sổ pt_v22 đang giữ vị thế MOM mở (nếu có) sẽ tự thoát theo exit rule hiện hành
(hold_days/stop) — đóng kênh chỉ chặn entry MỚI, không force-sell vị thế cũ; SpaceX/ZaloPay thật
hiện không giữ vị thế BAL-MOM nào (book BAL/LAG rỗng từ ~04/2026, NEUTRAL parking).

## 3. Thiết kế đo (harness + kỷ luật)

- Harness: `pt_v23_audit_2014.py` + knob mới `BAL_DROP_TIERS` (env, unset = byte-identical
  baseline; tag filename `_exp_drop*` theo guidelines §8, không thể đè canonical).
- Lệnh = ĐÚNG lệnh pin R3 (`BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg
  BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" AUDIT_END=2026-06-19
  $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge`) + `BAL_DROP_TIERS`.
- 3 run contemporaneous cùng ngày (tránh batch drift đã biết −1.2pp):
  1. `BAL_DROP_TIERS=none` — control, kỳ vọng tái lập ĐÚNG pin 28.82/1.90/−15.7/1.83;
  2. `BAL_DROP_TIERS=MOMENTUM_N,MOMENTUM_S` — Scope A;
  3. `BAL_DROP_TIERS=MEGA,MOMENTUM,MOMENTUM_N,MOMENTUM_S` — Scope B.
- Đánh giá: FULL/IS(2014-19)/OOS(2020+) CAGR·Sharpe·MaxDD·Calmar, per-year LOO (đặc biệt các
  năm MOM đóng góp dương: 2017/2020/2021/2025), DSR trên NAV daily của scope khuyến nghị,
  self-check 0 VND bắt buộc từng run, recompute độc lập `extract_peryear.py` từ CSV.
- **N trials = 2** (đúng 2 scope pre-registered, không tune thêm knob nào). PBO/CSCV không áp
  dụng được với family 2 biến thể (cần ≥~8) — thay bằng LOO per-year + DSR.
- Cơ chế "vốn giải phóng tự chảy": xác nhận bằng chính engine — BAL idle cash trong NEUTRAL đi
  vào custom30V parking ({3:0.7}), slot trống trong BULL đi vào DVR nếu có candidate; allocator
  BAL/LAG **không đổi** (w_LAG giữ nguyên — đúng ranh giới dispatch, không đụng).

## 4. KẾT QUẢ ĐO (điền sau khi 3 run hoàn tất)

_(đang chạy — sẽ điền)_

## 5. Khuyến nghị (điền sau §4)

_(chờ số)_
