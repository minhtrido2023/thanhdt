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

**Đề xuất a-priori về MOMENTUM/MEGA generic (câu hỏi 1 của dispatch)** từng nghiêng về đóng cùng
(Scope B, lý do semantics sạch + N nhỏ tưởng là no-op) — **nhưng số đo §4 đã BÁC lean này**: Scope B
kém Scope A và kém control ở mọi cửa sổ kể cả live-era. Khuyến nghị cuối (§5): KHÔNG đóng
MOMENTUM/MEGA. Đây chính là lý do phải đo thật thay vì suy diễn từ CP1.

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

## 4. KẾT QUẢ ĐO (3 run cache-vintage cùng ngày 2026-07-12, self-check 0 VND cả 3, engine print == recompute độc lập từ CSV 100%)

### 4.1 Headline

| Run @50B | FULL CAGR | Sharpe | MaxDD | Calmar | IS 14–19 | OOS 20+ | OOS Calmar |
|---|---|---|---|---|---|---|---|
| **control (dropnone)** | **28.82%** | 1.90 | −15.7% | 1.83 | 25.86% | 31.59% | 2.01 |
| **Scope A** (−MOM_N,−MOM_S) | 27.84% | 1.84 | −18.2% | 1.53 | 23.15% | **32.30%** | 1.77 |
| **Scope B** (−cả family) | 26.62% | 1.78 | −18.2% | 1.46 | 23.31% | 29.71% | 1.63 |

Control tái lập pin R3 CHÍNH XÁC (28.82/1.90/−15.7/1.83) — 3 run contemporaneous, không có batch drift.

### 4.2 Per-year delta vs control (pp)

| | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Scope A | +0.7 | +0.4 | −0.9 | **−8.5** | **−7.7** | −0.5 | −4.3 | +6.6 | +2.7 | +0.1 | −0.2 | −3.8 | +3.9 |
| Scope B | +0.7 | +0.4 | −0.9 | **−8.5** | −6.7 | −0.4 | −4.8 | **−4.7** | +0.0 | +0.2 | −1.0 | **−7.7** | +2.4 |

### 4.3 Delta CAGR theo cửa sổ (ctrl → treatment)

| Cửa sổ | Scope A | Scope B |
|---|---|---|
| FULL 2014→ | −0.97pp | −2.20pp |
| IS 2014–19 | −2.71pp | −2.55pp |
| OOS 2020+ | **+0.74pp** | −1.85pp |
| OOS ex-2021 | +0.11pp | −1.25pp |
| 2022+ (hậu bùng nổ) | **+1.03pp** | −0.87pp |
| 2024+ (live-era) | +0.65pp | **−1.79pp** |

### 4.4 Risk / DD / LOO / DSR

- **MaxDD cả 3 run cùng 1 episode 2020-07-27** (COVID wave-2): đóng MOM làm episode này sâu thêm
  −15.7% → −18.2% (MOM_N recovery-entries giữa 2020 từng đệm được nhịp này). **Era gần KHÔNG đổi**:
  MaxDD 2022+ = −14.2/−14.3/−14.5%; 2024+ = −12.3/−11.8/−12.5% (ctrl/A/B) — chi phí DD của việc
  đóng là đặc thù kịch bản 2020, không phải suy giảm phòng thủ thường trực.
- **LOO trung-hòa từng năm (Scope A)**: full-delta −0.97pp giữ ÂM ở cả 13 phép trung-hòa
  (−0.30…−1.36) → chi phí lịch sử là broad-based, không phải 1 năm; carrier lớn nhất 2017
  (mang 0.64pp của 0.97pp). Ngược lại **OOS gain +0.74pp KHÔNG phải 2021-carry** (ex-2021 vẫn
  +0.11pp, 2022+ +1.03pp) — khác chữ ký R2/F12 đã bác.
- **DSR** (N=2 trials pre-registered, không tune): Scope A 1.0000 (z=6.37), Scope B 1.0000 (z=6.15)
  — book sau đóng vẫn là chiến lược Sharpe cao; DSR không phải yếu tố phân định ở đây. PBO không
  áp dụng (family 2 biến thể < 8) — thay bằng LOO như khai báo §3.

### 4.5 Cơ chế vốn giải phóng — xác nhận bằng TX ledger

- **LAG book byte-identical cả 3 run** (4.871 buy-TX y nguyên) → allocator w_LAG không bị đụng, đúng
  ranh giới dispatch.
- Vốn BAL giải phóng: DVR buys 710 → 780 (A) / 722 (B); NEUTRAL idle → custom30V parking ({3:0.7})
  hoạt động đúng thiết kế. KHÔNG cần đổi allocator.
- **Path-dependence đáng ghi**: dưới Scope A, MEGA fire 5 lần + MOMENTUM 32 lần (control: 0 + 43) —
  ticker không còn bị MOM_N giữ slot trước đó nên vào lại qua kênh generic còn mở. Ghi chú §1
  "MEGA chưa bao giờ fire" chỉ đúng trong control; đóng MEGA **không còn là no-op tuyệt đối** dưới
  Scope A (nhưng vẫn immaterial: 5 entry/12.5 năm).

## 5. Khuyến nghị

**1. Scope B (đóng cả family MEGA+MOMENTUM+MOM_N+MOM_S) — KHÔNG khuyến nghị, bị số đo bác:** kém
control ở MỌI cửa sổ, kể cả nơi Scope A dương (OOS −1.85pp, 2022+ −0.87pp, live-era 2024+ −1.79pp,
Calmar 1.83→1.46). MOMENTUM/MEGA generic (BULL-only) vẫn đang đóng góp thật — gap A-vs-B riêng 2021
≈ 11pp, 2025 ≈ 3.9pp. CP1/CP-DVR1 đo trên deal MOM_N/MOM_S — bằng chứng NO-GO đó KHÔNG phủ kênh
generic, và phép đo này cho thấy đóng lây sang generic là trả giá thật. → Trả lời câu 1 dispatch:
**không mở rộng phạm vi sang MOMENTUM/MEGA.**

**2. Scope A (đóng MOM_N+MOM_S) — khuyến nghị ĐÓNG, với giá đo được khai trung thực:** đây là
quyết định **risk-governance, KHÔNG phải return-enhancer**:
- Giá lịch sử: FULL −0.97pp, Sharpe −0.06, worst-case episode 2020 sâu thêm 2.5pp, Calmar full
  1.83→1.53. Chi phí dồn vào 2017–2020 — đúng era mà CP1 đã kết luận pattern không lặp lại được.
- Regime hiện hành: hậu-2021 đóng ≈ hoà-tới-dương (+0.11pp OOS ex-2021, +1.03pp 2022+, +0.65pp
  2024+), DD era gần không đổi. Tức là **giữ kênh không còn được trả công trong regime hiện tại**,
  trong khi lý do tồn tại của nó (edge lịch sử) đã bị bác là không dự đoán được (CP1 0/13 feature,
  AUC 0.472; CP-DVR1 NO-GO).
- Nhất quán nguyên tắc user: "không giữ 1 pattern chỉ vì quen thuộc/lịch sử nếu số liệu thật không
  ủng hộ" — số 2017–20 là quá khứ không tái tạo; số 2022+ nói đóng không tốn gì.
- Trung thực chiều ngược lại: 2025 đóng mất −3.8pp (MOM_N/S còn ăn trong bull 2025) và kịch bản
  crash-rồi-hồi kiểu 2020 sẽ thiếu kênh recovery-entry NEUTRAL (đệm DD 2.5pp). User cần chấp nhận
  2 điểm này khi duyệt.

**3. Cơ chế implement khi user duyệt (giữ nguyên §2):** bỏ 2 tier khỏi `TIER_BAL` ở 3 file
(`golive_recommend_v23.py:47` money-path, `pt_v22_dt5g.py:92`, `pt_v4_dt5g.py:61`), KHÔNG sửa
`signal_v11_sql.py` (label MOM giữ làm diagnostics). Rollback = revert 1 dòng/file. Vị thế MOM đang
mở (nếu có, hiện không) tự thoát theo exit rule — chỉ chặn entry mới.

**4. Hệ quả baseline nếu duyệt Scope A:** canonical R3 phải re-pin theo đúng §8 guidelines với
`BAL_DROP_TIERS=MOMENTUM_N,MOMENTUM_S` (hoặc đổi default TIER_BAL trong harness cùng commit với 3
file production để backtest == production) → **số tham chiếu V2.4 mới sẽ là ≈ 27.84/1.84/−18.2/1.53**
(vintage 2026-07-12). KB/CLAUDE.md cần cập nhật cùng đợt.

**5. Điều kiện trước khi sửa code sống (không đổi):** user duyệt phạm vi (A vs B vs giữ nguyên) +
quant-skeptic verify finding này + tuân multiple-testing discipline (N=2 đã khai, LOO/DSR ở §4.4).

---

## 6. BỔ SUNG (job Taylor_20260712_022816) — tách MOM_N vs MOM_S trước khi chốt phạm vi

**Bối cảnh (user chỉ đạo 2026-07-12):** MOM_N chỉ sống ở NEUTRAL, MOM_S chỉ sống ở BULL/EXB — CP1 đo
GỘP 2 tier thành 1 family (MOM_N một mình chỉ 87 episode). Kết luận NO-GO đó không tách bạch được
MOM_S. Trong khi MOMENTUM/MEGA generic (cùng điều kiện BULL/EXB như MOM_S) vừa đo là VẪN đóng góp
thật (§4/§5) → nghi vấn hợp lý: Scope A có đang đóng oan MOM_S không?

### 6.1 Pre-registration (khai TRƯỚC khi chạy, 2026-07-12)

**Phần 1 — Scope C backtest (trial MỚI thứ 3, N-ledger backtest mở rộng 2→3):**
- **Scope C = đóng CHỈ MOMENTUM_N** (giữ MOMENTUM_S + MOMENTUM + MEGA).
- Lệnh = ĐÚNG lệnh pin R3 §3 + `BAL_DROP_TIERS=MOMENTUM_N`. Cùng cache vintage với 3 run §4
  (cùng ngày 2026-07-12, sync BQ cache 23:45 hôm trước, chưa có sync mới xen giữa).
- Đánh giá đúng kỷ luật §3: FULL/IS/OOS CAGR·Sharpe·MaxDD·Calmar, per-year delta 13 năm, LOO,
  self-check 0 VND, recompute độc lập `extract_peryear.py`.
- **Tiêu chí quyết định (khai trước):** nếu Scope C ≈ Scope A (chênh OOS/2022+/2024+ không đáng kể)
  → giữ khuyến nghị Scope A. Nếu Scope C RÕ RÀNG tốt hơn Scope A trên các cửa sổ hậu-2021 (OOS,
  2022+, 2024+) VÀ không tệ hơn đáng kể về risk (MaxDD/Calmar) → Scope C thay Scope A làm khuyến nghị.

**Phần 2 — regime-split contrast trên dữ liệu Phase 1 CÓ SẴN (1 test bổ sung vào N-ledger phân
tích, KHÔNG build lại dataset):**
- Input: `data/momdeal_exp/momdeal_episodes_phase0.csv` nguyên trạng (Phase 0, đã CP0-verified).
- Chạy lại 13 contrast CP1 RIÊNG cho 2 tập con: MOM_N (play_type=MOMENTUM_N, đều state5=3) và
  MOM_S (play_type=MOMENTUM_S, state5∈{4,5}). Cùng gate CP1 (FDR-BH 10% + sign-stable + |δ|≥0.15),
  không nới. MOM_N dự kiến THIN ở nhiều cell (n nhỏ) — báo trung thực, không ép kết luận.
- Câu hỏi: MOM_S tách riêng có feature phân tách thắng/thua tốt hơn khi không bị pha loãng bởi MOM_N?

**Quy tắc mâu thuẫn (khai trước):** nếu Phần 1 và Phần 2 mâu thuẫn (backtest nói giữ MOM_S nhưng
feature nói MOM_S không có pattern riêng) → báo cả 2 kết quả thẳng, không hòa giải giả tạo.

### 6.2 KẾT QUẢ (2026-07-12, cùng cache vintage với §4; self-check 0 VND; recompute độc lập
`analyze_momclose_scopeC.py` khớp engine print 100% từng năm)

**Phần 1 — Scope C backtest** (`..._exp_dropMOMN.csv`, log `mike/agents/Taylor/momdeal/scopeC_run.log`):

| Run @50B | FULL CAGR | Sharpe | MaxDD | Calmar | IS | OOS | OOS ex-21 | 2022+ | 2024+ |
|---|---|---|---|---|---|---|---|---|---|
| control | 28.82% | 1.90 | −15.7% | 1.83 | 25.86% | 31.59% | 22.04% | 20.20% | 30.22% |
| **Scope A** (−N,−S) | 27.84% | 1.84 | −18.2% | 1.53 | 23.15% | **32.30%** | **22.17%** | **21.30%** | 30.87% |
| Scope B (−family) | 26.62% | 1.78 | −18.2% | 1.46 | 23.31% | 29.71% | 20.49% | 19.31% | 28.44% |
| **Scope C** (−N only) | 27.50% | 1.85 | −17.8% | 1.54 | 23.39% | 31.37% | 21.91% | 20.44% | **31.18%** |

**Scope C vs Scope A (C−A)**: FULL −0.34pp, OOS −0.93pp, OOS ex-2021 −0.26pp, 2022+ −0.86pp,
2024+ +0.31pp; Sharpe/Calmar ≈ bằng (1.85/1.54 vs 1.84/1.53), MaxDD full −17.8 vs −18.2 (C nông
hơn 0.4pp), MaxDD 2024+ −12.7 vs −11.8 (C sâu hơn 0.9pp). Per-year đáng chú ý: 2021 A +106.8 /
C +99.8 / ctrl +100.2 — **ngay trong năm bong bóng, đóng thêm MOM_S còn TỐT hơn giữ**; 2025 giữ
MOM_S vớt lại ~+0.9pp vs A (51.95 vs 51.01) nhưng vẫn dưới control 54.78. LOO Scope C: full-delta
−1.32pp giữ âm ở cả 13 phép trung-hòa (−0.64…−1.73) — cùng chữ ký broad-based như A. DSR (N=3):
A/B/C đều 1.0000 — không phân định.

**Cơ chế (TX ledger)**: dưới Scope C, MOM_S fire NHIỀU hơn control (167+25_W=192 buys vs 146+41_W
=187) — hấp thụ slot MOM_N nhả ra — mà kết quả vẫn ≤ Scope A hậu-2021. Tức là đóng góp biên của
MOM_S khi kênh generic còn mở ≈ 0-tới-âm: nó chiếm vốn của MOMENTUM/MEGA (chặt hơn: ta≥155 + tier
C/D) và custom30V parking. Trái ngược hẳn generic: gap A-vs-B (đóng generic) = −1.85pp OOS. **Giả
thuyết "MOM_S giống MOMENTUM/MEGA vì cùng sống BULL/EXB" bị bác trực tiếp bằng số**: cùng regime
nhưng giá trị biên khác nhau — generic là tập chọn lọc hơn, MOM_S là phần lỏng còn lại (ta≥140,
không tier gate).

**Phần 2 — regime-split contrast** (`phase1b_regime_split_report.txt`, gate CP1 nguyên trạng):
- **MOM_N riêng** (125 labeled, 64S/61F; IS n=53): **0 survivor, 0 FDR-pass**. Tín hiệu thô mạnh
  nhất: C3 days_since_release δ=−0.218 (p=0.035, sign-stable — vào sớm sau BCTC tốt hơn) và T3
  vol_ratio δ=−0.182 sign-stable — đều không qua FDR.
- **MOM_S riêng** (388 labeled, 205S/183F; **92% mẫu OOS20+, riêng 2021 = 47.7%**): **0 survivor,
  0 FDR-pass** — còn yếu hơn pooled (pooled có 2 near-miss FDR-pass ROIC/RevYoY; tách riêng thì
  RevYoY δ=+0.132 p=0.024 không qua nổi FDR trong subset). Không có trục chất lượng nào để chọn
  thắng/thua BÊN TRONG kênh MOM_S.
- Sanity: MOMENTUM_N 100% state5=3, MOMENTUM_S 100% state5∈{4,5} — split đúng thiết kế.

**2 phần ĐỒNG THUẬN (không có mâu thuẫn phải báo):** backtest nói giữ MOM_S không thắng Scope A ở
cửa sổ nào trọng yếu; feature contrast nói bên trong MOM_S không có pattern phân tách được. Câu
chuyện nhất quán: MOM_S "trông có vẻ tốt trong bull" chỉ vì bull-era beta + dồn mẫu 2021, không
phải selection edge — đúng chữ ký CP1 pooled.

### 6.3 Khuyến nghị CUỐI CÙNG (thay §5.2 nếu user duyệt)

**GIỮ NGUYÊN SCOPE A** (đóng MOMENTUM_N + MOMENTUM_S; giữ MOMENTUM + MEGA generic). Tiêu chí
pre-registered §6.1 không đạt cho Scope C: không "rõ ràng tốt hơn" ở cửa sổ hậu-2021 nào ngoài
2024+ (+0.31pp, đổi lại MaxDD 2024+ sâu hơn 0.9pp), và KÉM hơn ở OOS (−0.93pp), OOS ex-2021
(−0.26pp), 2022+ (−0.86pp). Nghi vấn của user là đúng để kiểm tra (generic cùng-regime vẫn đóng
góp thật) nhưng số đo trả lời dứt khoát: MOM_S không phải generic — cơ chế implement/re-pin/
điều kiện ở §5.3–5.5 giữ nguyên cho Scope A.

**N-ledger cập nhật**: backtest trials 2→**3** (A, B, C — DSR tính lại với N=3, đều 1.0000);
phân tích thêm **1 view** (Phase 1b regime-split, cùng 13 feature + gate CP1, không nới, không
feature mới). Không mở thêm trial nào khác.

---

## 7. THỰC THI (job Taylor_20260712_025715, 2026-07-12) — user duyệt CUỐI Scope A, ĐÃ SỬA CODE + RE-PIN

- **Code**: bỏ MOMENTUM_N/MOMENTUM_S khỏi `TIER_BAL` ở 3 file production (`golive_recommend_v23.py:47`,
  `pt_v22_dt5g.py:92`, `pt_v4_dt5g.py:61`) + default harness `pt_v23_audit_2014.py:499` cùng commit.
  `signal_v11_sql.py` KHÔNG sửa (đúng §2). Safety check trước khi sửa: BAL/LAG live rỗng, PSI MOM_N_W
  trong sổ paper = case §2 (exit theo rule, không force-sell).
- **Re-pin R3**: lệnh pin + `BQ_LOCAL_CACHE=1`, self-check 0 VND, **27.84/1.84/−18.2/1.53** khớp
  CHÍNH XÁC §4; CSV canonical byte-identical `_exp_dropMOMN-MOMS.csv` (đã skeptic-verify); recompute
  độc lập khớp (FULL 27.84/IS 23.15/OOS 32.30). Registry entry "2026-07-12 — RE-PIN BASELINE R3".
- **Sự cố bắt được**: run re-pin đầu thiếu `BQ_LOCAL_CACHE` → 28.28/1.89/−17.9/1.58 lệch → DỪNG,
  root-cause, re-run cache → khớp. `BQ_LOCAL_CACHE=1` từ nay là phần của lệnh pin.
- **⚠️ ĐÍNH CHÍNH §6.2 (vintage Scope C)**: run Scope C sáng (job _022816) thực tế chạy **live-BQ**,
  TRÁI khai báo "cùng cache vintage" §6.1 — số 27.50/1.85/−17.8/1.54 trong bảng §6.2 là vintage
  live-BQ, KHÔNG so được thẳng với control/A/B (cache). Re-run Scope C sạch (cache-vintage, 0 VND):
  **28.15/1.85/−18.1/1.56**; OOS 32.38 / ex-2021 21.30 / 2022+ 20.48 / 2024+ 30.34 — vs Scope A
  32.30 / 21.92 / 21.30 / 30.87. **Kết luận §6.3 KHÔNG đổi và vững hơn**: C kém A ở cả 3 cửa sổ
  hậu-2021 dưới vintage sạch (bản live-BQ từng cho C nhỉnh 2024+ +0.31pp — đảo lại thành −0.53pp);
  FULL-advantage của C là 2021-carry (C +112.65 vs A +106.81 riêng 2021). Phần 2 regime-split độc
  lập vintage. Tiêu chí pre-registered §6.1 fail rõ hơn → Scope A đứng.
