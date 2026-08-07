# Mike fleet — context execution (Mafee only)
> Phần CHUYÊN BIỆT cho việc thực thi lệnh — không lặp lại safety core (đã import riêng ở
> CLAUDE.md), không có lịch sử R&D/backtest (việc của Taylor, không cần cho thực thi).
> Cần domain khác ngoài đây (chiến lược/backtest/pháp lý)? Đọc `kb/context_pack.md` qua
> Read tool nếu tự tin đúng chỗ, hoặc escalate Mike — đừng đoán.

## T+2 settlement — chỉ sellable từ phiên CHIỀU
DNSE nhả cổ phiếu mới mua sellable từ **phiên CHIỀU** của ngày T+2, KHÔNG phải đầu phiên sáng.
`step()` phải đọc `get_positions()` để lấy `sellable` thật, cap qty bán theo đó hoặc bỏ qua
(`WAIT_T2_SETTLEMENT`) — không để broker tự trả lỗi `Trade quantity not enough`.

## DNSE cash-account — sức mua T+0 từ tiền bán chờ về
Tiền bán settle T+2 nhưng `ppse` (pending settlement) CỘNG vào sức mua ngay sáng cùng ngày bán —
`availableCash` KHÔNG phản ánh việc này. Trước khi kết luận "thiếu tiền" phải check `ppse`.

## Idempotency / ghost-order guard (chi tiết cụ thể của nguyên tắc ở safety core)
`Executor._ghost_tickers()` (`trading_bot/executor.py`) — mỗi `step()` đối chiếu sổ lệnh broker
SỐNG với state nội bộ; mã nào có lệnh không rõ nguồn gốc trên broker → TẠM DỪNG đặt lệnh mã đó
(fail-safe-pause, không tự suy đoán gộp vào state) + báo bus. `_save_state()` chạy ngay sau MỖI
lần đặt lệnh thành công (không đợi hết `step()`) để thu hẹp cửa sổ crash. `poll_orders()` tự lỗi
→ fail-safe TOÀN BỘ mã trong plan (không fail-open).

## Domain-constraint layer P1 — order-tier LAG rating gate (LIVE từ 2026-07-29)
`filter_lag_rating_orders()` — lưới an toàn tầng ORDER cho gate 8L rating≤3 của LAG (vá lỗ hổng
gate cũ chỉ sống ở tầng sinh tín hiệu, không chặn được nếu plan/generator quên áp). Verify:
14/14 + 22/22 selfcheck, replay case thật (TRC/MST) bị chặn đúng, 0 lệnh khác đổi trên 21 plan
thật. Khác `excluded_tickers` ở trên (loại trừ theo TICKER cố định) — đây loại trừ theo RATING
tại thời điểm đặt lệnh. Chi tiết thiết kế: `agents/Taylor/research/ontology_constraint_layer_design_20260729.md`.

## Funding gate cấp PLAN — Σ lệnh MUA ≤ sức mua THẬT (`bot_execute.py`)
`check_plan_funding()` (`trading_bot/plan_funding_gate.py`), gọi trong `main()` của
`bot_execute.py` — sau `_log_plan_buying_power_shadow`, ngay TRƯỚC `Executor(...)`. Chặn cấp
PLAN: `Σ(lệnh mua qty × ref_price × 1,00075) > sức mua đo sống` ⇒ **KHÔNG đặt BẤT KỲ lệnh nào**
của account đó (exit 3), account khác cùng process vẫn chạy.

**Vì sao có gate này** — luật "Σ orders[] ≤ tiền thật, thiếu thì tự SHRINK" thủng **3 lần trong
15 ngày** (07-23, 07-27, 07-28) vì nó chỉ tồn tại dạng VĂN XUÔI ở tầng lập plan; tầng duy nhất
kiểm tra ở đường thực thi (`_log_plan_buying_power_shadow`) là **WARN_ONLY**, chỉ ghi 1 dòng CSV.

**3 điều DỄ HIỂU SAI, đọc trước khi sửa `bot_execute.py`/`executor.py`:**
1. **`executor.py` `WAIT_CASH` KHÔNG phải gate cấp plan.** Nó bỏ qua ĐÚNG lệnh thiếu tiền rồi
   **chạy tiếp lệnh sau** — tức plan vượt tiền vẫn khớp N lệnh đầu theo `priority`. Đó CHÍNH LÀ
   hành vi "list-rồi-đợi-tiền" mà luật cấm, không phải cơ chế chặn nó. Giữ nguyên `WAIT_CASH`
   (đúng vai trò lưới per-order khi tiền biến động TRONG phiên) — funding gate đứng TRƯỚC nó.
2. **Vế phải là `ppse.pp0Buy` (sức mua đo được), KHÔNG phải `availableCash`.** Hệ có dùng margin;
   user đã từ chối `Σ orders ≤ cash_vnd` (07-28). `pp0Buy` đã gồm hạn mức vay của **gói đang
   dùng** + tiền bán chờ về T+0.
3. **`pp0Buy` phải hỏi ĐÚNG gói vay của từng lệnh.** Ngày 07-29 shadow log báo `pp0Buy=0` cho TV1
   chỉ vì query dùng gói **default 1841** (gói mainboard, không hợp lệ cho TV1 trên UPCOM) trong
   khi `place_order` thực tế giải ra gói **1122** và DNSE NHẬN lệnh. Đó là **hiện vật đo đạc**,
   không phải hết tiền — gate naive 1-query-gói-default sẽ CHẶN OAN toàn bộ plan hôm đó. Gate
   nhóm lệnh theo gói vay hiệu lực, giải đúng cách `place_order` giải.

**Đo không được sức mua** (`pp0Buy` None/≤0) → so với cận ngoài
`(availableCash + Σ lệnh bán) × 3,0`: vượt ⇒ CHẶN; không vượt ⇒ **UNVERIFIED — không chặn nhưng
báo to** (bus + Discord + Telegram). Cố ý KHÔNG fail-closed máy móc: 1/1 điểm dữ liệu lịch sử của
nhánh này là báo động giả, mà chặn oan có phí thật (lỡ deadline vào lệnh LAG T+1/T+2).

Selfcheck: `plan_funding_gate_selfcheck.py`. Thiết kế + 3 replay sự cố thật:
`agents/Taylor/research/plan_funding_gate_20260804.md`.

**2 bug thật đã vá 2026-08-07 (đọc trước khi đụng lại `plan_funding_gate.py`/`executor.py`):**
(a) UPCOM (vd DRI) ra `loan_package_id=None` → rơi về gói mainboard-only → cả precheck lẫn
`place_order` reject → `WAIT_CASH` giả vô hạn dù thừa tiền, trông y hệt thiếu tiền thật. Fix:
luôn giải gói vay theo MÃ (tái dùng `_resolve_loan_package_id`), commit `c22bd1c`. (b) Gate không
cộng tiền lệnh BÁN cùng plan chạy trước (L2 JIT-unpark) → chặn oan plan tự cấp vốn đủ (ca thật
08-07: ZaloPay bị chặn sạch 0/9 lệnh dù 8 lệnh bán PARK 98,68tr thừa nuôi 1 lệnh mua 23,60tr).
Fix: cộng tín dụng JIT theo tỉ lệ nhu cầu từng nhóm gói vay, chỉ tính lệnh bán priority < min
priority mọi lệnh mua, commit `087a3d0`. Cả 2 quant-skeptic CONFIRMED. ⚠️ 2 dispatch (Mafee+Taylor)
sửa CÙNG file trong 1 phút không cách ly — lần sau tách file/chạy tuần tự khi trùng.

## excluded_tickers — enforcement
`trading_bot.plan.filter_excluded_tickers()`, gọi NGAY sau `load_plan()` trong `bot_execute.py`
— áp dụng bất kể plan generator có nhớ loại trừ hay không. Đọc từ
`secrets/trading_bot_accounts.json` field `excluded_tickers` theo account.

## Lịch giao dịch trong ngày (T2-T6, giờ ICT)
09:05 mở phiên sáng (`run_bot.sh --auto-otp`) → 11:30 nghỉ trưa (bot tự idle qua
`session_phase()`) → 13:00 resume phiên chiều → ~14:50 ATC đóng phiên, bot tự cancel lệnh treo,
ghi `exec_*_report.md`. `bot_heartbeat.sh` mỗi 5' giám sát liveness + digest fill mới.

## Plan file — chỉ đọc ĐÚNG tên chính thức
`load_plan()` chỉ đọc `plan_<account>_<date>.json` — file có suffix khác (vd `_v2`) VÔ HÌNH với
bot dù nội dung đúng hơn. Nếu nhận thấy có bản plan mới hơn dưới tên khác, đó là dấu hiệu quy
trình duyệt lại chưa promote đúng — báo lại, không tự đoán dùng bản nào.

## File sở hữu (đã có đầy đủ ở CLAUDE.md riêng của Mafee, không lặp lại ở đây)
`trading_bot/{brokers,executor,plan,vn_market,config}.py`, `dnse_api.py`, `phs_flex_api.py`,
`bot_execute.py`. PHS live đang BLOCKED (lỗi `-700003`, chờ credential) → PHS chạy paper only.
