# L2 — JIT unpark: build + selfcheck + replay (job `Taylor_20260806_015739`)

**Trạng thái: XÂY XONG, CHƯA WIRE.** Chỉ 3 file MỚI, **0 file production bị sửa**
(`git status`: 2 file `M` còn lại là `data/gmail_otp_last_id.txt` — cron run_bot 09:05 ICT hôm nay
— và `.verify_a4_worktree` mtime 08-04, cả hai không phải của job này).

| File | Vai trò |
|---|---|
| `mike/bin/compute_jit_unpark.py` | L2 — CHỈ ĐỌC, đề xuất lệnh bán PARK tài trợ lệnh mua BAL/LAG |
| `mike/bin/compute_jit_unpark_selfcheck.py` | 47 assert + ma trận 4 TZ |
| `mike/agents/Taylor/jit_unpark_replay_20260806.py` (+2 JSON) | replay trên sổ THẬT SpaceX/ZaloPay |

Lý do wire (nhắc lại để không trôi): **TRUNG THÀNH THIẾT KẾ** — live phải chạy đúng cơ chế đã tạo
ra số pin R3 28,86%. **KHÔNG PHẢI** lý do lợi nhuận: ablation 08-03 cho thấy thiếu L2 không rớt
OOS đủ mạnh để coi là mất tiền thật.

## 1. Đã port đúng cái gì (mọi hằng số có file:dòng trong code)

| Thành phần | Nguồn | Giá trị |
|---|---|---|
| Trigger | `simulate_holistic_nav.py:1134` | `cash < target_value × 0,99` |
| `needed` | `simulate_holistic_nav.py:1137` | `min(target_value − max(cash,0), etf_day_cap_remaining)` |
| Friction | `pt_v23_audit_2014.py:1946` | `0,0015` (cấu hình R3) |
| Fallback co lệnh | `simulate_holistic_nav.py:1189-1194` | `(cash + margin_room) × 0,95` |
| Ngưỡng bỏ lệnh | `simulate_holistic_nav.py:1195` | `< 1.000.000đ` |
| `margin_room` | `pt_v23_audit_2014.py:1959-1961` | **0** — `max_gross_exposure` chỉ bật khi env `_mge` (V2.5, đang DISABLED) và khi bật thì `margin_tiers` giới hạn CAPIT-only ⇒ lệnh BAL/LAG không có dư địa margin |
| Trần TỔNG/phiên | dùng lại `etf_day_cap_live()` của L1 | không đặt trần mới |
| Trần per-name | dùng lại gate LAG live | `LAG_ADV_PCT × ADV_mã × share` |
| FIFO / pro-rata | `LotBook` trong `park_holdings.py` | không viết lại sổ lô |

Không thêm gate phụ nào: L2 chạy **khi và chỉ khi** có lệnh MUA book BAL/LAG trong plan.
Lệnh mua PARK (`custom30V_parking`), CAPIT, và mọi lệnh BÁN đều không phải trigger.

## 2. Hai chỗ live BẮT BUỘC khác engine — đã ghi rõ trong code, không giấu

1. **Rời rạc hoá theo lô chẵn.** Engine bán cổ phần LẺ của MỘT quỹ ETF; live phải bán bội số
   100cp của 15-30 mã. Chia pro-rata theo trọng số → làm tròn XUỐNG lô → phần dư phân bổ tiếp theo
   **largest-remainder** (mã thiếu nhiều nhất so với phần pro-rata của nó được +1 lô trước), dừng
   khi 1 lô nữa sẽ VƯỢT `needed`. Đây là quy tắc LÀM TRÒN, không phải tham số mới — bỏ nó thì mọi
   `needed` nhỏ ra 0 lệnh và L2 im lặng không làm gì (đúng dạng lỗi im lặng §14 muốn tránh).
   Tie-break xác định ⇒ chạy lại y hệt (T14d, T15).
2. **Không đặt lệnh vượt sức mua thật.** Engine giữ `target_value` rồi fill dần nhiều phiên
   (`buy_value = min(remaining, daily_max, _bp)`, dòng 1216); một lệnh live chỉ có MỘT phiên, và
   DNSE từ chối lệnh vượt sức mua ⇒ qty chốt lại = `round_lot(min(tv, cash+margin_room) / ref_price)`.
   Chỉ đi theo hướng thận trọng.

## 3. 🔴 MỘT ĐIỂM CẦN NGƯỜI QUYẾT — công thức engine làm lệnh mua luôn HỤT ĐÚNG 1 LÔ

`needed` **không** gross-up friction: bán đúng `needed` thì tiền về là `needed × (1 − 0,0015)`,
tức luôn thiếu đúng phần friction (+ phần lẻ do làm tròn lô ở chân bán). Engine nuốt chỗ thiếu đó
bằng fill nhiều phiên; live 1 phiên ⇒ **mất trọn 1 lô**. Đo trên sổ THẬT SpaceX 08-05, cùng một
lệnh 80tr, chỉ đổi giá tham chiếu:

| ref_price | qty plan → chốt | mất | % lệnh |
|---|---|---|---|
| 100.000 | 800 → 700 | 10,00tr | 12,5% |
| 30.000 | 2.600 → 2.500 | 3,00tr | 3,8% |
| 12.000 | 6.600 → 6.500 | 1,20tr | 1,5% |

Luôn đúng 1 lô — biên độ thiệt hại tỉ lệ thuận với giá cổ phiếu.

**Tôi ship phương án (A) — giữ NGUYÊN công thức engine**, đúng chỉ đạo dispatch ("dùng đúng §B3,
đừng thiết kế lại"). Phương án (B) là đổi **một** biểu thức: `needed = (target − cash)/(1 − friction)`
— vẫn dùng đúng hằng số friction đã có, làm live khớp Ý ĐỊNH của engine ("bán đúng bằng lượng cần",
user 2026-05-23, chính là comment tại dòng 1134). **Tôi KHÔNG tự đổi** — đây là quyết định chính
sách, cần Mike/user chốt. Nếu chốt (B), sửa 1 dòng + 1 test, không đụng gì khác.

> **[CẬP NHẬT 2026-08-06, job `Taylor_20260806_025613`]** User John đã chốt **(B)** và (B) đã áp.
> ⚠️ Nhưng **giả định "sửa 1 dòng là hết hụt" ở đoạn trên là SAI** — đo lại trên sổ thật cho thấy
> **0/6 ca hết hụt, 5/6 ca gross-up là no-op đúng 0đ, 6/6 ca lệnh mua vẫn co 1 lô**: phí ma sát
> chỉ là 1 trong 2 nguồn gây hụt, nguồn còn lại (rời rạc lô bán) (B) không chạm tới. Bảng số,
> chứng minh đại số và đề xuất (C) — cho `allocate()` làm tròn LÊN 1 lô — ở
> **`jit_unpark_grossup_20260806.md`**. Đọc file đó thay cho mục này.

## 4. Selfcheck — 47/47 PASS, digest ĐỒNG NHẤT trên 4 môi trường TZ

`python3 mike/bin/compute_jit_unpark_selfcheck.py` (0,25s, offline hoàn toàn — không chạm DNSE/BQ,
tự động được `run_selfchecks.sh` nhặt qua glob). File tự spawn lại chính nó dưới
`env -u TZ` / `Asia/Ho_Chi_Minh` / `UTC` / `America/New_York` rồi so DIGEST:

```
TZ=<unset>          exit=0 digest=ab132dbe41213d29 [47 PASS / 0 FAIL]
TZ=Asia/Ho_Chi_Minh exit=0 digest=ab132dbe41213d29 [47 PASS / 0 FAIL]
TZ=UTC              exit=0 digest=ab132dbe41213d29 [47 PASS / 0 FAIL]
TZ=America/New_York exit=0 digest=ab132dbe41213d29 [47 PASS / 0 FAIL]
✅ MA TRẬN TZ: mọi môi trường PASS và digest ĐỒNG NHẤT
```

Phủ đủ các ca dispatch yêu cầu + hơn: cash đủ (no-op) · biên 0,99 hai phía · cash thiếu một phần
(bán đúng `needed`, pro-rata ≥2 mã, không bán sạch mã nào, FIFO theo `entry_date`) · thiếu hơn
`etf_day_cap` (carry-over + co lệnh) · `excluded_tickers` · CAPIT/LAG/BAL không đụng **+ bất biến
fail-closed nếu lô không-PARK lọt vào `park_lots`** · UNVERIFIED · đối soát lệch ⇒ chặn hết ·
NO_TRIGGER · DROP <1tr · chia trần với L1 (trần tổng, trần per-name, cp vật lý) · trần per-name +
T+2 `sellable` · fail-closed khi ADV lỗi/cũ/≤0 · nhiều lệnh theo priority dùng chung trần ·
**bảo toàn tiền mặt** · làm tròn lô (7 giá trị `needed`) · xác định · `today_ict()` neo ICT ·
script không ghi file nào ngoài `--out`.

**2 bug thật do selfcheck bắt được** (đúng tinh thần skill `verify-before-done` — không phải test
"xanh sẵn"):
1. **Tiền mặt âm.** Bản đầu trừ `cash -= target_value` khi lệnh được tài trợ đủ; do trigger ở
   mốc 0,99 nên cash tụt xuống ÂM (T13 đo `−225.000đ`). Sửa: chốt qty theo sức mua thật.
2. **Nhãn quyết định sai.** `BLOCKED_ALL_NAMES` ("không mã nào bán được") bị trả cả khi rổ PARK
   hoàn toàn bán được nhưng `needed` nhỏ hơn 1 lô — đúng dạng thông điệp làm người đọc đi chẩn
   đoán nhầm chỗ. Tách thành `NO_SELL_POSSIBLE`.

## 5. Replay trên dữ liệu THẬT — `jit_unpark_replay_20260806.py`

Trong cửa sổ replay được (bootstrap ngày 0 = 2026-08-04), **plan thật của cả 2 account đều 0
lệnh** (08-04/05/06) ⇒ **không tồn tại case trigger thật**. Nên: mọi thứ khác đều thật — sổ lô
theo book (`park_holdings`, đối soát broker ✅ KHỚP), vị thế/giá/`availableCash` từ bản ghi DNSE
thật của phiên, ADV thật, trần rổ thật (1.322,44 tỷ), share thật (0,5) — **chỉ lệnh mua LAG là
tiêm vào**. Đây KHÔNG phải bằng chứng lợi nhuận; nó trả lời đúng một câu: L2 đề xuất bán gì và có
tôn trọng mọi ranh giới cứng không.

- **SpaceX** (PARK 644,10tr/15 mã, cash 4,82tr): `JIT` — needed 75,18tr, đề xuất bán **75,00tr
  trải 11 mã** (ACB/BID/CTG/HDB/LPB/MBB/SHB/TCB/VCB/VHM/VPB), lệnh mua 800→700cp.
- **ZaloPay** (PARK 280,31tr/9 mã, cash 5,82tr, DGC excluded): `JIT` — needed 74,18tr, bán
  **73,14tr trải 9 mã**, lệnh mua 800→700cp.

10/10 bất biến GIỮ trên cả hai account: chỉ bán mã sổ PARK · không đụng CAPIT/LAG/BAL/
DISCRETIONARY · không đụng `excluded_tickers` · không đụng UNVERIFIED · không bán quá số đang giữ ·
không bán quá `sellable` (T+2) · Σ ≤ trần TỔNG/phiên · Σ ≤ `needed` (không bán thừa) · mọi qty bội
số lô · **không bán sạch mã nào** (giữ cấu trúc rổ).

## 6. Chưa làm (đúng yêu cầu dispatch)

- KHÔNG wire vào `bot_execute.py` / `golive_recommend_v23.py` / `context_planning_mini.md`.
- KHÔNG tự gọi `verify_finding.sh` — Mike dispatch quant-skeptic riêng.
- **Việc phải quyết trước khi wire**: (a) phương án (A) hay (B) ở §3; (b) L1 và L2 tiêu CHUNG trần
  thanh khoản/phiên và chung số cp vật lý — khi wire phải nối `--l1-json` (đã hỗ trợ, có test
  T10/T10c/T10d), chạy hai lớp rời nhau sẽ đề xuất bán TRÙNG cùng số cp.
