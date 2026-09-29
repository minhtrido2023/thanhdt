# GDKHQ D1-D3 — shadow 2026-08-17 FAIL: root cause + fix (job Taylor_20260817_171334)

> Kết luận một dòng: **G5 không sai, công thức sở đúng tới từng đồng. Sai là GIỜ CHẠY** —
> shadow chạy 21:41 ICT, lúc đó bản ghi `secdef` của DNSE đã lật sang phiên **08-18**, nên
> cổng đối soát so tham chiếu phiên 08-18 với công thức dựng cho phiên GDKHQ 08-17.

## 1. Bằng chứng root cause (đo, không suy đoán)

`DNSEClient.secdef("BID")` đọc lúc 2026-08-18 00:17 ICT — chép nguyên văn:

```json
{"symbol":"BID","basicPrice":35.9,"ceilingPrice":38.4,"floorPrice":33.4,
 "time":"2026-08-17 19:23:45.110"}
```

Bản ghi **tự khai** giờ sinh là 19:23:45 ngày 08-17 — tức 4h38' SAU khi phiên 08-17 đóng
(khớp ATC 14:45:01, theo `latest_trade`). `basicPrice 35,9` cùng trần 38,4 / sàn 33,4 là bộ
tham số của phiên **08-18** (35.900 = giá ĐÓNG CỬA 08-17; 35.900×1,07 → tick → 38.400).

Ba đường dữ liệu ĐỘC LẬP đều nói tham chiếu THẬT của phiên GDKHQ 08-17 là **35.800đ**:

| Đường | Số | Ghi chú |
|---|---|---|
| Công thức sở từ `corporate_action` | 38.250 / 1,068433 = **35.800,1** → tick → 35.800 | P_cum = `tav2_bq.ticker.Price` 08-14, xác nhận lại bằng BQ trong job này |
| DNSE `positions.marketPrice`, cả 3 lô BID, 04:44→08:13 ICT ngày 08-17 | **35.800** | đổi thành 35.900 chỉ từ 19:05 (= giá đóng cửa) |
| `tav2_bq.ticker.Close` 08-14 (đã điều chỉnh hồi tố) | **35.800** | vendor tự tính, cùng kết quả |

⇒ Sai lệch 100đ không phải sai công thức, sai làm tròn, hay sai `P_cum`. Cả 3 giả thuyết
trong dispatch (a/b/c: query BQ sai · rounding khác sở · phải nới dung sai) đều **BỊ BÁC BỎ**.

## 2. Sửa gì

### 2.1 Cổng G6 mới — "bản đọc này thuộc PHIÊN NÀO"

`price_frame.check_snapshot_session(secdef_time, session_date)` (hàm THUẦN), chạy **TRƯỚC G5**
khi `ex_today` — vì G5 chỉ có nghĩa khi hai vế cùng nói về một phiên.

Không đoán theo đồng hồ máy chạy — đọc dấu thời gian **feed tự khai**:
- giờ < 15:00 ⇒ bản ghi mô tả phiên của CHÍNH NGÀY đó ⇒ phải trùng `session_date`;
- giờ ≥ 15:00 ⇒ đã lật, mô tả phiên KẾ ⇒ `session_date` phải LỚN HƠN ngày bản ghi
  (phủ đúng khe cuối tuần mà không cần lịch phiên);
- trần cũ 5 ngày lịch; thiếu trường ⇒ không phát biểu (tiền lệ G4 thiếu `marketPrice`);
  có trường mà parse không nổi ⇒ **fail-closed** (feed đổi định dạng ≠ chuyện bỏ qua im lặng).

Trường `secdef.time` trước đây **bị ghi đè** trong `DNSEBroker.get_quote`: `raw.update(sd)` rồi
`latest_trade` ghi đè khoá `time` bằng giờ khớp lệnh. Đã chụp riêng thành `raw["secdefTime"]`
→ `Quote.secdef_time`. Đây là thay đổi DUY NHẤT ở `brokers.py`, thuần THÊM trường.

### 2.2 G2 — dung sai phải nuốt việc sở làm tròn trần về bước giá (blocker THỨ HAI, mới phát hiện)

Đo live 8 mã (feed 2026-08-18): **8/8 có trần nằm trong ĐÚNG 1 bước giá** so với biên lý
thuyết, nhưng dung sai cũ (`band_tol=0.01` = 1% *tương đối trên biên* = ±0,07pp với HOSE)
**chặn oan 4/8** — trong đó có **VIX, đúng mã GDKHQ 2026-08-20**:

| Mã | ref | trần thật | trần lý thuyết | lệch | biên đo | dung sai CŨ |
|---|---:|---:|---:|---:|---:|:--|
| **VIX** | 13.350 | 14.250 | 14.284,5 | −34,5 | +6,742% | ❌ CHẶN OAN |
| HHP | 14.250 | 15.200 | 15.247,5 | −47,5 | +6,667% | ❌ CHẶN OAN |
| MBB | 19.900 | 21.250 | 21.293,0 | −43,0 | +6,784% | ❌ CHẶN OAN |
| VGT (UPCOM) | 11.600 | 13.300 | 13.340,0 | −40,0 | +14,655% | ❌ CHẶN OAN |
| BID | 35.900 | 38.400 | 38.413,0 | −13,0 | +6,964% | ✅ |
| RAL | 77.800 | 83.200 | 83.246,0 | −46,0 | +6,941% | ✅ |
| FPT | 68.800 | 73.600 | 73.616,0 | −16,0 | +6,977% | ✅ |
| QNS (UPCOM) | 45.600 | 52.400 | 52.440,0 | −40,0 | +14,912% | ✅ |

Mã giá càng thấp thì một bước giá càng đáng nhiều pp — thuần cơ học, không phải bất thường thị
trường. Chính docstring `check_reference_snapshot` đã ghi dải đo được là "HOSE 6,69–7,00%",
rộng hơn hẳn dung sai nó tự đặt: **mâu thuẫn nội bộ, không phải phát hiện mới về sở**.

Sửa: `price_frame.band_tol_one_tick()` → `max(0.01, tick/(ref×band))`, **CHỈ NỚI không bao giờ
SIẾT**, và **chỉ truyền từ đường D1-D3** (`resolve_reference`). **KHÔNG đổi mặc định của
`check_reference_snapshot`** — luật A (`no_chase_ceiling`) đang chạy LIVE với dung sai đó; đổi
mặc định là đổi hành vi live, việc khác, cổng khác, cần quant-skeptic + user riêng.

### 2.3 Shadow runner — tách INDETERMINATE khỏi FAIL

`bot_execute._run_gdkhq_shadow` gom `stale_frames` (gate G6) và phát verdict "KHÔNG KẾT LUẬN
ĐƯỢC — chạy lại TRONG phiên", thay vì "FAIL" nói sai nguyên nhân. Vẫn `passed=False`, vẫn
không promote.

## 3. Kết quả live shadow 2026-08-18 — **PASS**

`python3 bot_execute.py --gdkhq-shadow --gdkhq-watch HHP,RAL,QNS,VGT --date 2026-08-18
--account SpaceX --account ZaloPay` → **PASS 4 mã × 2 account, 6/6 cổng, 0 lỗi.**

| Mã | Sàn | Sự kiện | q.ref sống | Công thức | Lệch |
|---|---|---|---:|---:|---:|
| RAL | HOSE | DIV 2.500đ | 77.800 | 77.800,0 | **0đ (khớp tuyệt đối)** |
| QNS | UPCOM | DIV 1.000đ | 45.600 | 45.600,0 | **0đ (khớp tuyệt đối)** |
| HHP | HOSE | ISS cổ tức CP 6,5% | 14.250 | 14.272,3 | −22,3đ (<1 tick) |
| VGT | UPCOM | DIV 300đ | 11.600 | 11.700,0 | −100đ (= đúng 1 tick, MÉP dung sai) |

`data/gdkhq_shadow_acceptance.json` → `trace_passed=true`, `acceptance_status=PENDING_ACCEPTANCE`,
`errors=[]`. `data/gdkhq_d1d3_rollout.json` đã tạo (`status=shadow_passed`,
`acceptance_status=PENDING_ACCEPTANCE`). **`gdkhq_rollout.enabled()` vẫn trả `False`** — lệnh mã
GDKHQ vẫn bị chặn riêng cho tới khi user nghiệm thu. Không có gì được bật.

## 4. Hạn chế phải công bố cùng số

1. **G4 không được kiểm trong lần PASS này** — không account nào giữ HHP/RAL/QNS/VGT nên G4 trả
   "không áp dụng". Bằng chứng G4 vẫn là artifact đóng băng BID 2026-08-14T19:10:23 trong
   selfcheck, không phải lần chạy live này.
2. **UPCOM: G5 đứng trên cơ sở giá có thể SAI BẢN CHẤT.** VGT lệch đúng −100đ (không phải làm
   tròn: 11.700 vốn đã nằm trên bước giá) trong khi QNS khớp tuyệt đối. Giả thuyết hợp với dữ
   liệu: tham chiếu UPCOM là **bình quân gia quyền** phiên trước chứ không phải giá đóng cửa,
   còn `P_cum` ta dùng là `ticker.Price` (đóng cửa). **CHƯA kiểm chứng độc lập** — chỉ có n=2.
   ⇒ Đừng coi một lần G5 PASS trên UPCOM là bằng chứng mạnh; VIX 08-20 là HOSE nên không dính.
3. **Chưa có ca ISS trên mã ta ĐANG GIỮ chạy trong phiên** — BID là ca đó nhưng đã lỡ giờ.
   VIX 08-20 (ISS 5%, HOSE) là cơ hội tiếp theo, và giờ đã hết cả 2 blocker.
4. `capit_lever_selfcheck.py` FAIL 1 assertion (K3) — **có sẵn TRƯỚC thay đổi này**, xác nhận
   bằng `git stash` chạy lại baseline ra đúng 1 FAIL đó. Không thuộc phạm vi job này.
5. Lần chạy shadow đầu (không `--account`) kéo cả account PAPER vào và FAIL vì paper broker
   không có `positions_raw()` → đã bắn 1 notify FAIL 2026-08-18 lên Discord trước khi chạy lại
   đúng scope. Đáng vá: shadow nên tự bỏ qua account không phải DNSE thay vì FAIL cả run.

## 5. Việc còn mở

- **Nghiệm thu**: user duyệt → `bot_execute.py --accept-gdkhq-shadow 2026-08-18`.
- **VIX 2026-08-20 (ISS 5%, HOSE)**: chạy shadow **TRONG phiên** (09:10–14:30 ICT) để có ca ISS
  live. Nếu chạy sau 15:00 sẽ ra G6 INDETERMINATE — đúng thiết kế, không phải lỗi.
- **G2 dung sai một-bước-giá cho luật A LIVE**: chưa đụng. Nếu muốn đồng bộ hai đường thì cần
  job riêng + quant-skeptic (dữ liệu ở §2.2 dùng lại được).
- `apply_exdate_gate()` vẫn CHƯA wire vào executor — không đổi trong job này.
