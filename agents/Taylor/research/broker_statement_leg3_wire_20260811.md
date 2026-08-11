# Wire statement khớp lệnh DNSE thành LEG 3 của đối soát EOD — thiết kế + patch

**Job**: `Taylor_20260811_162828` · **Ngày**: 2026-08-11 · **Trạng thái**: patch xong, **CHƯA áp
production** (chờ quant-skeptic theo kỷ luật §6).

## 0. Kết luận ngắn

- Wire vào **đúng 1 điểm**: `mike/bin/eod_trading_report.sh` (cron 19:10 ICT — email tới ~16:30
  nên kịp). Thêm module mới `mike/bin/broker_fill_confirm.py` + selfcheck **51/51 PASS**.
- **KHÔNG wire vào `send_plan_report.sh`** — có bằng chứng cơ chế hiện có đã đúng và tốt hơn
  (mục 4). Thêm vào sẽ tạo nguồn sự thật thứ hai mâu thuẫn với plan.
- 2 phát hiện phụ đáng giá, **độc lập với việc có wire hay không**: phí giao dịch thật
  **0,094%** ≠ 0,075% đang giả định trong `reconcile_equity.py` (mục 5); và DNSE **chỉ gửi email
  vào phiên CÓ khớp** (mục 3.3).

## 1. Việc đã có, đừng làm lại

`eod_trading_report.sh` **đã có sẵn đối soát 2 leg** (dòng ~209-280 bản cũ): `state.json` nội bộ
vs `dnse_raw_<date>.jsonl`. Nó cũng đã in `filled/qty_plan (pct)` từng mã và đếm "Khớp đủ / một
phần / chưa khớp". Kiểm chứng trên ca TV1 hôm nay: report cũ **đã** in `Chưa khớp: 1` cho ZaloPay
và `Khớp một phần: 1` cho SpaceX.

⇒ **Sự cố hôm nay KHÔNG phải do report thiếu thông tin.** Nó do một tuyên bố được suy ra từ
`orders[]` của plan (số ĐẶT) ngoài luồng report. Vì vậy tôi KHÔNG viết lại phần planned-vs-filled
đã có; giá trị thêm vào phải nằm ở chỗ khác — mục 2.

## 2. Leg 3 thêm được gì mà 2 leg cũ không có

Cả `state.json` lẫn `dnse_raw` **đều do chính tiến trình bot của mình ghi**. Một lỗi hệ thống làm
sai CẢ HAI cùng lúc mà không leg nào phát hiện được. Statement đi qua đường khác hẳn (backend DNSE
tự phát hành). Ba lỗ hổng cụ thể nó bịt:

| # | Lỗ hổng của 2 leg cũ | Bằng chứng |
|---|---|---|
| 1 | **Fill trên mã NGOÀI plan là vô hình.** Leg `dnse_raw` lọc thẳng `if sym not in plan_tickers: continue` ⇒ lệnh đặt tay trong app DNSE / lệnh sót phiên trước không tồn tại với cả 2 leg | đọc code dòng 258 bản cũ |
| 2 | **Bot chết trước khi ghi state** ⇒ case 3 của report ("có plan, không có state") hiện KHÔNG biết thực tế đã khớp gì chưa | code dòng 125-134 |
| 3 | **Phí/thuế thật** theo từng dòng khớp — không nguồn nào khác trong pipeline có | mục 5 |

Sweep 6 phiên (04→11/08): off-plan fill = **0 ca**. Guard sạch, không nhiễu — nhưng đó là giá trị
bảo hiểm, chưa phải đã bắt được lỗi.

## 3. Thiết kế

### 3.1 `mike/bin/broker_fill_confirm.py` (mới)
`load_broker_fills(date, account, wc_root)` → `BrokerFills(available, reason, by_key, fees, tax,
value)`; `reconcile_lines(broker, plan_by_key, state_by_key)` → list dòng báo cáo. Có CLI
(`--account --date [--json]`) để tra tay.

**Fail-safe tuyệt đối — không bao giờ raise.** Thiếu CSV → tự gọi `fetch_dnse_khoplenh_email.py`
1 lần (đo thật: **3,0s**), vẫn thiếu ⇒ `available=False` + 1 dòng thông tin. Báo cáo
client-facing không được chết vì 1 email chưa tới.

### 3.2 Ba cái bẫy đã mã hoá thành guard (đều bắt được bằng dữ liệu thật)

1. **Mất số 0 dẫn đầu.** CSV giữ đúng `0002023347`, nhưng `pd.read_csv` KHÔNG có `dtype=str` parse
   thành `int 2023347` ⇒ so với `account_id` trong secrets **luôn sai, và sai IM LẶNG** (mọi
   account trông như "broker báo 0 fill"). Fix 2 lớp: đọc `dtype=str` **và** so sánh qua
   `_norm_acct()` (bỏ 0 dẫn đầu cả hai phía) để không phụ thuộc vào việc ai đó nhớ truyền dtype.
   Selfcheck có ca chứng minh ngược.
2. **Vắng mặt tiểu khoản có 2 nghĩa TRÁI NGƯỢC** — phát hiện khi chạy trên lịch sử thật, không
   phải suy diễn: (a) hôm nay account đó khớp 0 (ca thật **ZaloPay 2026-08-07**, plan bị gate P0
   chặn sạch 0/9 lệnh); (b) ánh xạ tiểu khoản hỏng. Bản đầu tôi fail-closed cả hai ⇒ mất khả năng
   đối soát ngày khớp 0. Bản cuối phân biệt **bằng bằng chứng trong chính file**: nếu một account
   KHÁC mà mình biết số có mặt ⇒ ánh xạ đang chạy đúng ⇒ vắng mặt là (a). Không account nào khớp
   ⇒ fail-closed (§25).
3. **File gộp 2 tiểu khoản** (§12) — `groupby` theo `(tieu_khoan, ma, chiều)`; selfcheck khẳng
   định 2 account cho kết quả KHÁC nhau (158,9M vs 82,7M ngày 11/08).

Thêm: so theo `(mã, chiều)` chứ không chỉ mã — cùng mã vừa mua vừa bán trong ngày không lẫn nhau
(leg `dnse_raw` cũ cộng gộp bất kể chiều; tôi **không sửa** nó — ngoài phạm vi, §3).

### 3.3 "Không có statement" ≠ sự cố
Verify Gmail: các ngày 04, 05, 06/08 **không hề có email** — đúng những ngày khớp 0. DNSE chỉ gửi
vào phiên CÓ khớp. Không phân biệt được "chưa tới giờ" với "sẽ không bao giờ tới" từ Gmail ⇒ câu
chữ nêu đủ cả hai khả năng, không để người đọc tưởng là hỏng.

### 3.4 Điểm chèn vào `eod_trading_report.sh` (49 dòng thêm, 2 sửa)
Chèn TRONG heredoc python sẵn có (không tạo đường render thứ hai): tính `plan_by_key`/
`state_by_key` theo `(mã, chiều)` → gọi leg 3 → append dòng vào `lines` ngay sau khối đối soát
cũ. Bọc `try/except` bao trọn: mọi lỗi ⇒ 1 dòng "bỏ qua", report vẫn nguyên vẹn.

**Escalate: dùng LẠI đường sẵn có**, không dựng cơ chế thứ hai — ghi thêm khoá
`broker_statement_mismatches` vào chính file cờ `eod_mismatch_<account>_<date>.json` đã có, nên
dispatch risk-auditor phía dưới tự nhận. **Chỉ escalate khi 2 nguồn độc lập bất đồng hoặc có fill
ngoài plan; KHÔNG escalate khi chỉ khớp thiếu** — khớp thiếu là thanh khoản mỏng (ca TV1), bình
thường; escalate sẽ thành báo động giả gần như mỗi phiên.

### 3.5 Output thật (render lại từ dữ liệu 11/08, không phải mô phỏng)
```
✅ Đối soát broker: fill thật khớp đúng state nội bộ, không lệch.
✅ Leg 3 (statement DNSE, độc lập với state/dnse_raw): số khớp trùng khớp state nội bộ,
   không có fill ngoài kế hoạch.
📉 Broker xác nhận KHỚP THIẾU so với kế hoạch — chưa đạt mục tiêu, KHÔNG được đọc là "đã mua đủ":
  • TV1 (mua): chỉ khớp 100/2,000 đặt (5%) — phần thiếu 1,900cp
💸 Phí/thuế THẬT theo statement: 149,577đ phí + 0đ thuế trên 158.9M (= 0.0941% giá trị).
```

## 4. Vì sao **KHÔNG** wire vào `send_plan_report.sh` (câu hỏi 3 của dispatch)

Kiểm chứng thật, không suy đoán — plan 08-12 do DollarBill lập:

| Account | Thiếu 11/08 | Plan 08-12 đề xuất | |
|---|---:|---:|---|
| SpaceX | 1.900cp | **1.900cp** | khớp chính xác |
| ZaloPay | 1.300cp | **1.200cp** | **KHÁC** — re-size độc lập |

Con số ZaloPay lệch chính là bằng chứng mạnh nhất: DollarBill **không** phát lại phần thiếu hôm
trước, nó **suy lại mục tiêu từ vị thế thật** (`dnse_raw` positions) + vốn khả dụng. Cơ chế
target-based đó **tốt hơn** replay-shortfall ở 3 điểm: tự đúng khi fill về muộn, tự đúng khi mục
tiêu đổi, và không double-count. Thêm một dòng "nhắc phần thiếu 1.300cp" vào báo cáo plan sẽ
**mâu thuẫn ngay với chính lệnh 1.200cp in bên dưới nó** — tạo nguồn sự thật thứ hai, đúng thứ
§2/§3 cấm. Ngoài ra thông tin thiếu-khớp đã có ở EOD 19:10, **trước** plan report 21:00 cùng ngày.

**Rủi ro tồn dư đã cân nhắc**: nếu EOD 19:10 chết thì không ai thấy dòng khớp thiếu. Tác động vốn
= 0 vì plan tự sửa; nên không đáng đổi lấy một cơ chế trùng lặp.

## 5. Phát hiện phụ — phí thật 0,094%, KHÔNG phải 0,075%

Đo từ statement (VND thật, không phải tỉ lệ khai báo):

| | 11/08 SpaceX | 11/08 ZaloPay | 10/08 SpaceX |
|---|---:|---:|---:|
| Phí / giá trị khớp | **0,0941%** | **0,0943%** | **0,0952%** |

Tách cấu phần: phí trả sở **0,027% HOSE / 0,018% UPCOM** + phí DNSE **0,070%** ⇒ 0,097% (HOSE),
0,088% (UPCOM). Thuế bán 0,1% ghi riêng cột `thue`.

`mike/bin/reconcile_equity.py` đang dùng mặc định **`--fee-rate-pct 0.075`** (dòng 73). ⇒ Phí bị
khai thiếu ~**25% tương đối**, đẩy phần chênh sang mục "residual chưa giải thích" của identity
check. Ghi chú: quy ước backtest TC 0,1%/chiều (CLAUDE.md) thì **vẫn đúng** — 0,097% ≈ 0,1%.

**Chưa sửa** — chạm pipeline §6, cần Mike quyết + quant-skeptic, và nên đo thêm vài phiên có bán
để chốt con số dùng chung thay vì lấy 1 ngày.

## 6. Kiểm chứng đã chạy

- `mike/bin/broker_fill_confirm_selfcheck.py`: **51 PASS / 0 FAIL**. Fixture tự dựng trong tmpdir
  (§23: không assert lên trạng thái sống); 2 ca dữ liệu thật (11/08, 08-07) **tự SKIP** nếu file
  bị dọn. Mọi guard đều có **ca chứng minh ngược** (§24).
- Render thật `eod_trading_report.sh` (tách heredoc, state copy sang `/tmp` để **không** ghi cờ
  mismatch/dispatch/post Discord vào production): SpaceX + ZaloPay 11/08 (mua) và SpaceX 10/08
  (bán, có thuế) — đều đúng.
- `bin/shellcheck_gate.sh mike/bin/eod_trading_report.sh` → **exit 0**.
- Auto-fetch live: 3,0s.
- Chạy được khi không có biến `TZ` (§16 — ngày luôn truyền tường minh, không gọi `now()`).

## 7. Hạn chế còn lại (công bố, không tự mở rộng phạm vi)

1. **Case 1/2/3 của report thoát sớm ⇒ leg 3 không chạy.** Đáng chú ý nhất là **case 3** (có plan,
   không có state — bot chết): đó lại đúng lúc leg 3 có giá trị NHẤT ("thực tế đã khớp gì chưa?").
   Case 2 (HOLD 0 lệnh) cũng bỏ lọt fill ngoài kế hoạch. Sửa được nhưng chạm nhánh cảnh báo lỗi —
   đề xuất để Mike quyết riêng, không gộp vào patch này.
2. Chỉ đối soát **số lượng**, chưa đối soát **giá khớp TB** giữa statement và state.
3. Statement chỉ lùi được tới ~15/06/2026 trong hộp thư (20 email gần nhất theo query hiện tại).

## 8. File đụng tới

| File | Trạng thái |
|---|---|
| `mike/bin/broker_fill_confirm.py` | **MỚI** |
| `mike/bin/broker_fill_confirm_selfcheck.py` | **MỚI** (51 ca) |
| `mike/bin/eod_trading_report.sh` | **SỬA** +49/−2 |
| `mike/kb/data_registry/trading-bot/dnse_khoplenh_broker_email.md.proposed` | chờ Mike duyệt (§13) |

Chưa commit, chưa áp production.
