# PENDING — sàn ADV3T **2 tỷ/phiên** thành **GATE CỨNG** cho book LAG + BAL

- **Job**: `Taylor_20260810_081207` · **Ngày**: 2026-08-10 · **Owner**: Taylor
- **Trạng thái**: **CHƯA ÁP DỤNG, CHỜ DUYỆT.** Production **sạch 0 dòng** — patch đã được test
  trên cây thật rồi `git checkout` trả về nguyên trạng (`git status` rỗng trên cả 5 file).
- **Báo cáo đầy đủ**: `mike/agents/Taylor/research/adv3t_hard_gate_wire_20260810.md`
- **Căn cứ quyết định**: finding `Taylor_20260810_073541` + user chốt — **hiệu quả vốn**, KHÔNG
  phải edge.

## Patch này làm gì — và KHÔNG làm gì

| | |
|---|---|
| ✅ Làm | `ADV_MIN_VND = 2e9` loại ứng viên **LAG** và dòng tín hiệu **BAL** có ADV3T < 2 tỷ, **ở tầng chọn mã** (trước due-diligence, trước plan) |
| ❌ **KHÔNG** làm | chặn ở `executor.py` (không đụng 1 dòng nào) |
| ❌ **KHÔNG** làm | đụng `signal_v11_sql.py` — SQL DÙNG CHUNG với engine backtest đã pin (`pt_v23_audit_2014.py:48`); sửa `liq>=1e9` ở đó sẽ **lặng lẽ đổi nền R3 28,86%** |
| ❌ **KHÔNG** làm | đụng `trading_bot/plan.py` (module lõi, 21 selfcheck) — `git diff --stat` rỗng |
| ❌ **KHÔNG** làm | đụng sleeve discretionary/fear-buy (TV1/DGC) — grep `discretionary_accumulation.py` = **0 hit** |
| ❌ **KHÔNG** làm | thêm logic dồn vốn/tăng size (dispatch cấm — chỉ báo cáo hiện trạng) |

## ⚠️ ĐỌC TRƯỚC KHI DUYỆT — 3 điều đã đo, không phải giả định

**1. Backtest nói NGƯỢC với patch này. Đó là quyết định chính sách, đã biết trước.**
Phần gia tăng của sàn 2 tỷ trên nền gate `ADV>0` sẵn có: **−0,26pp CAGR / −0,02 Sharpe /
−0,92pp OOS**; thang liều **phẳng** 0,5→5 tỷ; **PBO 0,916** (`Taylor_20260804_080547`,
quant-skeptic CONFIRMED cao). Lý do wire = 1,6% vốn / 93,4% bỏ dở của băng mỏng
(`Taylor_20260810_073541`). Ghi rõ trong comment code để không ai trích ngược lại như edge.

**2. Cái giá cụ thể hôm nay: rổ LAG 176 → 58 ứng viên (−67%), và TRC nằm trong nhóm bị chặn.**
TRC ADV3T = **1,44 tỷ** (đo BQ 2026-08-07) — đúng mã user duyệt mua 07-24 (phương án C). Muốn
TRC-like qua được thì sàn phải < 1,44 tỷ. **Đây là câu hỏi cho user, không phải cho tôi.**

**3. "Dồn vốn sang deal to hơn" KHÔNG tự xảy ra — trọng số/vị thế là HẰNG SỐ ở cả 2 book.**
- BAL: `select_book` là hàng đợi có trần 12 ⇒ **có** mã xếp sau lấp chỗ, nhưng chỉ ở
  **26/47 phiên (55%)** có hàng đợi >12; trọng số vẫn `POS_PCT=0.10` cố định.
- LAG: **không có hàng đợi nào** (mọi event qualify đều thành mục tiêu, `LAG_TW` cố định) ⇒
  loại 1 ứng viên = 1 slot biến mất.
- Vốn dôi ra rơi về cash → bị `compute_park_trim.py` hút vào **rổ parking custom30V** (80% cash
  nhàn rỗi ở NEUTRAL). Đó là chuyển dịch có thật, nhưng **không phải "deal to hơn"**.

## Cổng đã qua / chưa qua

| Cổng | Kết quả |
|---|---|
| Selfcheck `lag_liq_signal_filter_selfcheck.py` (40 → 50 ca) | ✅ **40/40 unit**, **50/50 với `--live`** |
| Ca **chứng minh ngược** cho mọi ca chặn (B1', C1') | ✅ bỏ sàn ⇒ TRC/SJS/TCI **thật sự lọt qua** |
| Biến thể môi trường (§16) | ✅ `env -u TZ` · `TZ=America/New_York` · `TZ=UTC` × `$DNA_PYEXE` + `python3` (pandas 2.3) ⇒ 40/40 cả 5 tổ hợp |
| Quét theo phạm vi §23 (`due_diligence.py`, 2 selfcheck phụ thuộc) | ✅ `due_diligence_selfcheck.py` **35/35 OK**, `lag_adv_cap_selfcheck.py` **29/29 PASS** |
| `golive_recommend_v23.py` | ✅ `py_compile` + AST; ❌ **CỐ Ý không chạy thật** (ghi đè artifact canonical — §8) |
| Regex ledger không nuốt nhánh cũ (khối D) | ✅ `adv_thin` tách khỏi `adv_zero`/`stale_adv`/`no_price_row` |
| `patch -p1 --dry-run` trên cây sạch | ✅ 5/5 file OK |
| quant-skeptic | ⏳ đang chạy — kết quả ghi lên bus |
| **User/Mike duyệt** | ❌ **CHƯA** |

## File trong thư mục này

| File | Là gì |
|---|---|
| `adv3t_hard_gate.patch` | patch chuẩn tắc — áp bằng `patch -p1` từ `WorkingClaude/` |
| `lag_liquidity_filter.py`, `golive_recommend_v23.py`, `lag_liq_ledger.py`, `due_diligence.py`, `lag_liq_signal_filter_selfcheck.py` | **BẢN SAO đã vá** để đọc/review — **KHÔNG PHẢI production**, đừng copy đè |

## Áp / rollback

```bash
cd /home/trido/thanhdt/WorkingClaude
patch -p1 --forward < mike/agents/Taylor/pending_adv3t_hard_gate_20260810/adv3t_hard_gate.patch
$DNA_PYEXE lag_liq_signal_filter_selfcheck.py --live    # kỳ vọng 50/50
# rollback nhanh KHÔNG cần git: đặt ADV_MIN_VND = 0 trong lag_liquidity_filter.py
#   → tái lập hành vi trước 2026-08-10 bit-for-bit (chân control của selfcheck chạy đúng đường này)
git checkout -- lag_liquidity_filter.py lag_liq_ledger.py lag_liq_signal_filter_selfcheck.py \
                deploy_golive_dt5g_v4/golive_recommend_v23.py trading_bot/due_diligence.py
```

**Sau phiên chạy thật ĐẦU TIÊN** cần soát: log `[bal-liq]`/`[lag-liq]` trong output recommender,
và `n_bal_liq_excluded` / `n_lag_liq_excluded` / `adv_min_vnd` trong `data/golive_v23_status.json`.
