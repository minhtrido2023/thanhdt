# GDKHQ và toàn bộ đường đặt lệnh — điều tra + thiết kế

Job `Taylor_20260815_050425` · 2026-08-15 · **R&D THUẦN — KHÔNG sửa một dòng production nào**

Nối tiếp `Taylor_20260815_034407` (`../upcom_ref_anchor_20260815/`), mục **FIX.md §5.1** tự công
bố phần chưa làm: *"Ngày GDKHQ hiện chỉ BỎ QUA luật A, chưa xử lý trọn: `ref_price`/`qty` của lệnh
hôm đó cũng dựng trên giá chưa điều chỉnh."* Job này mở rộng phạm vi ra **toàn bộ pipeline đặt
lệnh**, không riêng luật A, không riêng UPCOM.

---

## 0. Kết luận trước, chứng cứ sau

1. **Tác động tiền thật từ đầu LIVE (2026-07-01 → 2026-08-14) = 0đ.** Quét 745 lệnh THẬT trong
   `dnse_raw_*.jsonl`: đúng **2 lệnh** từng đặt vào ĐÚNG ngày GDKHQ của chính mã đó (MBB
   2026-08-11, cả 2 tài khoản) — và **cả 2 đều dùng giá ĐÃ điều chỉnh** (plan 20.200, đặt 20.550,
   giá tham chiếu sở công bố 20.200). Không sai.
2. **Nhưng "không sai" đó là do MAY VỀ GIỜ, không phải do thiết kế.** Cả hai lệnh đó đến từ một
   lần chạy `compute_park_add.py` thủ công **sáng 08-11 (sau nửa đêm)**; dây chuyền cron ban đêm
   chuẩn chạy **tối T-1** và tối hôm đó (08-10 19:12) broker còn ở hệ quy chiếu CŨ.
3. **Phát hiện lớn nhất — DNSE lật hệ quy chiếu lúc ~19:10 ICT tối T-1, và cú lật KHÔNG NGUYÊN
   TỬ.** Đo được đến từng giây trên BID (ex 2026-08-17), xem §3. Cùng một tài khoản, cùng một mã,
   cùng MỘT bản đọc `positions`: một lô đã điều chỉnh, một lô chưa.
4. ⇒ **Cách hỏng thật không phải "dùng nguồn giá sai" mà là "TRỘN HAI HỆ QUY CHIẾU"**: khối lượng
   ở hệ mới × giá ở hệ cũ (hoặc ngược lại). Đây đúng là cơ chế của sự cố NAV MBB 08-11 (+5,01tr,
   §5) — sự cố đó đã vá ở **tầng NAV** (`verify_account_snapshot`) nhưng **tầng ĐẶT LỆNH thì
   chưa**.
5. Dây chuyền tối hiện tại **nằm vắt ngang đúng cửa sổ lật**: `eod_trading_report` 19:10,
   `park_trim` (L1) chạy thật lúc **19:04:15**, `jit_unpark` (L2) 19:40, `merge_park` 20:20,
   `inject_discretionary` 20:30. Ngày 2026-08-14 **L1 chạy TRƯỚC cú lật, L2/merge/inject chạy SAU**
   — đã xảy ra thật, chỉ không gây thiệt hại vì L1 hôm đó ra 0 lệnh.
6. Độ lớn nếu cắn: **median dịch chuyển giá tham chiếu 5,46%**, max **50,0%** (VHM 08-06), đo trên
   **22 ngày-mã** GDKHQ (25 bản ghi sự kiện, gộp các sự kiện rơi cùng ngày cùng mã) của chính các
   mã ta đã đặt lệnh thật trong 3 tháng qua (§4).

---

## 1. Bản đồ nguồn giá — MỌI đường có thể sai vào ngày GDKHQ

Ký hiệu: **LIVE** = hỏi DNSE lúc chạy · **HIST** = dữ liệu lịch sử (BQ / cache parquet) ·
**BROKER** = đọc từ bản ghi `positions` của DNSE.

| # | Nơi | Đại lượng | Nguồn | Ngày GDKHQ có sai? |
|---|---|---|---|---|
| A | `trading_bot/strategies.py:288` `_price()` | `ref_price`, và `qty = book_nav·w/px` | LIVE quote → **fallback #2 = `recs_close` (BQ `Close` ngày signal)** → fallback #3 = giá giao dịch paper | ⚠️ **CÓ** khi quote câm: rơi về `Close` = hệ quy chiếu KHÁC |
| B | `trading_bot/strategies.py:337-344` mirror paper | `target[t] = shares_paper × scale` so với `have` = **BROKER** | HIST (sổ paper) vs BROKER | 🔴 **CÓ, nặng nhất về cấu trúc** — xem §2 |
| C | `mike/bin/paper_main_probe_plan.py:65` `latest_closes()` | `ref_price` + `qty = target/px` | HIST — `Close` trong `bq_cache/ticker/2026.parquet` | 🔴 **ĐÃ SAI THẬT** — xem §5.2 |
| D | `mike/bin/lag_entry_anchor.py:105` | `entry_anchor_price` (TRẦN so với giá live) | HIST — `tav2_bq.ticker.**Price**` phiên quá khứ | 🔴 **CÓ** — xem §6.1 |
| E | `mike/bin/compute_park_trim.py:201` `live_price_fn` + `market_price` | `ref_price`, mẫu số trọng số | LIVE + BROKER | ⚠️ đúng nguồn, nhưng **giờ chạy nằm ngay mép cú lật** |
| F | `DollarBill/tools/compute_park_add.py:231-235` | `ref_price`, `qty` | BROKER `market_price` → LIVE quote | ⚠️ như E |
| G | `mike/bin/compute_jit_unpark.py` | `ref_price`, tiền bán ước tính | BROKER `marketPrice` | ⚠️ như E |
| H | `mike/bin/merge_park_orders.py:345-354` | hoà giải `ref_price` L1 vs L2 | — | 🔴 **CÓ**: lệch L1≠L2 chỉ **cảnh báo rồi lấy giá THẤP HƠN**. Một cú lật hệ quy chiếu (BID −6,4%, VHM −50%) sẽ bị **nuốt như nhiễu giá thường** |
| I | `mike/bin/discretionary_accumulation_inject.py` | anchors luật A | LIVE `q.ref` | ✅ đã vá job trước (luật A). **Nhánh luật B (trung bình 5 giá ĐÓNG) chưa** — §6.2 |
| J | `mike/bin/compute_park_trim.py:170` `etf_day_cap_live` | trần VND/phiên của rổ | HIST `Price × Volume`, 60 phiên | ⚠️ nhẹ (trung bình 60 phiên), nhưng là trần **ràng buộc**, không phải chú thích |
| K | `trading_bot/executor.py` `_limit_price` / no-chase | giá đặt cuối cùng | LIVE quote + `ref_price` của plan | ✅ giá live đúng, **nhưng neo `ref_price` thừa hưởng sai của A-D nếu có** |
| L | `annotate_pacing_horizon` (ADV), `due_diligence.py` | chú thích | HIST | ✅ thuần thông tin, không đổi sizing |

### 1.1 Hai loại dữ liệu — kiểm bằng số thật, không suy đoán

Yêu cầu của dispatch là **kiểm chứ đừng đoán**. Đo trên `data/bq_cache/ticker/2026.parquet`:

| Ngày | VHM `Price` | VHM `Close` | `Close/Price` |
|---|---:|---:|---:|
| 2026-08-03 | 148.000 | 74.000 | 0,5000 |
| 2026-08-05 (phiên cum cuối) | 153.000 | 76.500 | 0,5000 |
| **2026-08-06 (GDKHQ)** | **153.000** | **77.100** | **0,5039** |
| 2026-08-07 | 73.000 | 73.000 | 1,0000 |

⇒ Xác nhận đúng "Bẫy (2)" của `kb/data_registry/price-volume/ticker_close_vs_price_dividend_adj.md`:
`Close` **điều chỉnh hồi tố theo vintage hôm nay**, `Price` **không hồi tố**.

🔴 **BẪY MỚI, chưa có trong data_registry — `Price` của CHÍNH DÒNG NGÀY GDKHQ không nhất quán
giữa các sự kiện:**
- **VHM 2026-08-06**: `Price = 153.000` — nhưng giá thật khớp hôm đó ≈ 77.100 (chính `Close` của
  dòng đó), và broker báo `marketPrice = 76.500` suốt phiên. `Price` ở đây là giá phiên TRƯỚC,
  **trễ một phiên**, sai hệ số 2.
- **MBB 2026-08-11**: `Price = 20.350 = Close` — đúng, đã ở hệ mới.

⇒ **Không được giả định `ticker.Price` của ngày GDKHQ là giá thật của ngày đó.** Ca VHM sai đúng
bằng toàn bộ hệ số quyền. Đây là phát hiện mới của job này; đề nghị Winston bổ sung vào
`data_registry` và hỏi bq_admin (một dòng bị bỏ sót lúc ingest, hay quy ước cố ý?).

### 1.2 Giá SỐNG `q.ref` — kiểm lại, không giả định lặp lại

Job trước đo SSI: `q.ref = 19.600` vs giá đóng cum 24.500. Kiểm bằng công thức sở giao dịch với
CẢ HAI sự kiện SSI ngày 08-17 (cổ tức tiền 1.000đ + cổ phiếu thưởng 20%):

```
(24.500 − 1.000) / (1 + 0,20) = 19.583,3  → làm tròn bước giá 100 → 19.600 ✓ KHỚP
```

Kiểm chéo trên MBB 08-11 (cổ tức CP 15% + quyền mua 10:1 giá phát hành 10.000đ):

```
(24.250 + 0,10 × 10.000) / (1 + 0,15 + 0,10) = 25.250 / 1,25 = 20.200 ✓ KHỚP TUYỆT ĐỐI
```

20.200 chính là con số user chụp màn hình app DNSE ngày 08-11 (nguồn: docstring
`mike/bin/exrights_price_basis_selfcheck.py`). ⇒ **`q.ref` gộp ĐÚNG nhiều sự kiện cùng ngày và
làm tròn đúng bước giá.** Hai ca độc lập, hai loại sự kiện khác nhau, khớp tuyệt đối cả hai.
Đây là nguồn duy nhất trong hệ có tính chất đó.

---

## 2. Lỗ cấu trúc nặng nhất — mirror sổ paper vs vị thế BROKER (dòng B)

`strategies.py:337-344` đặt `target[t] = shares_paper × scale`, rồi `:398-440` sinh lệnh từ
`diff = target − have` với `have` = **số CP THẬT ở broker**.

Sổ paper (`pt_v23_audit_2014.py`) mô phỏng trên chuỗi `Close` **đã điều chỉnh** ⇒ ngày một mã trả
cổ tức CP, **số CP trong sổ paper KHÔNG nhân lên** (chuỗi giá điều chỉnh đã tự giữ liên tục giá
trị). Nhưng số CP THẬT ở broker **thì nhân lên**.

⇒ Với VHM ex 08-06 (×2,0): `have` nhảy 500 → 1.000 trong khi `target` giữ nguyên ⇒
`diff = −500` ⇒ **sinh một lệnh BÁN 500cp hoàn toàn ảo**, đúng bằng phần cổ phiếu thưởng vừa nhận.
Với BID ex 08-17 (×1,068) ⇒ bán ảo ~6,8% vị thế.

**Vì sao chưa cắn**: 2 account LIVE hiện không đi qua nhánh mirror này (plan SpaceX/ZaloPay do
DollarBill dựng từ `golive_recommend_v23` + bộ công cụ PARK; `bot_prepare_plan.py` chỉ phục vụ
account paper `main`). Nhưng **`build_plan` là code production**, không phải script nghiên cứu, và
bất kỳ account nào chuyển sang chạy nó là cắn ngay. Ghi ra đây để lần sau không ai phải phát hiện
lại từ đầu.

---

## 3. Cú lật hệ quy chiếu của DNSE — đo đến từng giây, và nó KHÔNG NGUYÊN TỬ

Nguồn: `data/execution_logs/dnse_raw_2026-08-14.jsonl`, mã **BID**, GDKHQ **2026-08-17** (cổ phiếu
thưởng tỉ lệ 0,068433). Giá đóng phiên cum cuối (08-14) = 38.250 ⇒ tham chiếu 08-17 = 38.250 /
1,068433 = **35.800**.

| Thời điểm (ICT) | Tài khoản | `marketPrice` | `openQuantity` | Hệ quy chiếu |
|---|---|---:|---:|---|
| 08-14 04:41:59 | SpaceX | 38.850 | 1.100 | CŨ |
| **08-14 19:04:15** | SpaceX | **38.850** | **1.100** | **CŨ** ← `park_trim` (L1) ghi artifact ĐÚNG giây này |
| **08-14 19:10:23** | ZaloPay | **35.800** / **38.850** | **107** / **300** | 🔴 **TRỘN — xem dưới** |
| 08-14 19:11:05 | SpaceX | 35.800 | 1.175 | MỚI |
| 08-14 20:15:02 → 21:52 | cả hai | 35.800 | 107 + 320 | MỚI |

Bản ghi thô lúc 19:10:23, **một tài khoản, một mã, một bản đọc `positions`**:

```json
{"symbol":"BID","openQuantity":107,"tradeQuantity":100,"marketPrice":35800,"loanPackageId":1826}
{"symbol":"BID","openQuantity":300,"tradeQuantity":300,"marketPrice":38850,"loanPackageId":1258}
```

**DNSE điều chỉnh THEO TỪNG GÓI VAY (`loanPackageId`), không phải theo mã, và không đồng thời.**
Lô 1826 đã sang hệ mới (100 × 1,068433 = 106,8 → 107 @ 35.800); lô 1258 còn hệ cũ (300 @ 38.850).
Bất kỳ code nào cộng dồn qua các gói vay trong bản đọc đó đều **cộng hai hệ quy chiếu vào một số**.

Cộng sai ở bản đọc cụ thể này: `107×35.800 + 300×38.850 = 15.485.600` so với đúng
`427×35.800 = 15.286.600` ⇒ **thổi +199.000đ (+1,30%)** chỉ trên một mã. Hệ số ở đây nhỏ vì BID
chỉ 6,8%; cùng cơ chế trên VHM (×2,0) cho sai số tới **~50%** của vị thế.

**19:10 ICT là giờ cron của `eod_trading_report.sh`** — đường báo cáo client-facing (§6
`coding_guidelines`). Không phải đường đặt lệnh, nhưng cùng một bản đọc, cùng một cách hỏng.

### 3.1 Thời điểm lật KHÔNG ổn định giữa các sự kiện

| Mã | GDKHQ | Trạng thái broker tối T-1 | Ghi chú |
|---|---|---|---|
| VHM | 2026-08-06 | **ĐÃ điều chỉnh lúc 08-05 19:04** (76.500, qty ×2) | `corp_actions.json` ghi `broker_effective_ts = 08-05T12:00` — sớm hơn nữa |
| MBB | 2026-08-11 | **CHƯA** lúc 08-10 19:12 (24.150, qty 1.100) → đã điều chỉnh lúc 08-11 00:41 (20.200, 1.265) | lật QUA ĐÊM |
| BID | 2026-08-17 | **CHƯA** lúc 08-14 19:04 → **ĐÃ** lúc 19:11 | lật lúc ~19:10 |

⇒ Ba sự kiện, **ba thời điểm lật khác nhau** (T-1 trưa / T-1 19:10 / qua đêm). **Không có quy tắc
giờ nào an toàn để chờ.** Mọi thiết kế dạng "chạy sau giờ X là an toàn" đều sai — phải **kiểm tra
hệ quy chiếu tại chỗ**, không suy từ đồng hồ.

---

## 4. Độ lớn — 22 ngày-mã GDKHQ của chính các mã ta giao dịch

Nguồn: `tav2_bq.corporate_action`, lọc bằng `corp_action_lib.is_price_adjusting()`, giao với 40 mã
từng xuất hiện trong `place_order` thật. Giá nền = `Price` phiên cum cuối (cache parquet).
**Gộp mọi sự kiện rơi cùng ngày cùng mã** (25 bản ghi → 22 ngày-mã): sở giao dịch tính MỘT giá
tham chiếu cho cả cụm, nên tách ra tính riêng là sai về bản chất — ca ACB 06-15 và MBB 08-11 lệch
rõ giữa hai cách tính.

| GDKHQ | Mã | Sự kiện | Giá cum | Tham chiếu | Dịch |
|---|---|---|---:|---:|---:|
| 2026-06-05 | PVT | cổ tức CP 10% | 22.250 | 20.227 | −9,1% |
| 2026-06-09 | SCL | cổ tức CP 17% | 20.400 | 17.436 | −14,5% |
| 2026-06-15 | ACB | tiền 700 **+** CP 13% | 26.500 | 22.832 | −13,8% |
| 2026-06-26 | VNM | tiền 1.850 | 56.450 | 54.600 | −3,3% |
| 2026-06-29 | VHM | tiền 6.000 | 162.000 | 156.000 | −3,7% |
| 2026-06-30 | VRE | tiền 1.000 | 29.200 | 28.200 | −3,4% |
| 2026-07-09 | DCM | tiền 2.000 | 36.650 | 34.650 | −5,5% |
| 2026-07-09 | MBB | tiền 1.000 | 26.000 | 25.000 | −3,8% |
| 2026-07-14 | HAH | tiền 2.000 | 50.800 | 48.800 | −3,9% |
| 2026-07-14 | TLG | tiền 1.000 | 49.050 | 48.050 | −2,0% |
| 2026-07-17 | BID | tiền 450 | 39.300 | 38.850 | −1,1% |
| 2026-07-23 | CTG | tiền 450 | 29.700 | 29.250 | −1,5% |
| 2026-07-23 | VCB | tiền 450 | 54.500 | 54.050 | −0,8% |
| 2026-07-27 | NCT | tiền 8.000 | 92.800 | 84.800 | −8,6% |
| 2026-07-28 | SAB | tiền 3.000 | 46.600 | 43.600 | −6,4% |
| 2026-07-28 | VGC | tiền 2.200 | 37.100 | 34.900 | −5,9% |
| **2026-08-06** | **VHM** | **cổ tức CP 100%** | **153.000** | **76.500** | **−50,0%** |
| **2026-08-11** | **MBB** | **CP 15% + quyền mua 10:1 @10.000** | **24.250** | **20.200** | **−16,7%** |
| **2026-08-17** | **BID** | **CP thưởng 6,84%** | **38.250** | **35.800** | **−6,4%** |
| **2026-08-17** | **MBS** | **tiền 1.000** | **18.400** | **17.400** | **−5,4%** |
| **2026-08-17** | **SSI** | **tiền 1.000 + CP thưởng 20%** | **24.500** | **19.583** → tick **19.600** | **−20,1%** |
| **2026-08-20** | **VIX** | **cổ tức CP 5%** | **13.450** | **12.810** | **−4,8%** |

**n = 22 ngày-mã · median |dịch| = 5,46% · max 50,0% · 12/22 vượt 5% · 5/22 vượt 10%.**

So sánh: trần đuổi giá của hệ (`no_chase`) làm việc ở thang **1–4%**. ⇒ **quá nửa số ngày-mã dịch
giá LỚN HƠN toàn bộ dải mà cơ chế chống-đuổi-giá được thiết kế để kiểm soát.** Sai hệ quy chiếu
không phải nhiễu — nó nuốt trọn cơ chế bảo vệ.

**Tần suất**: 22 ngày-mã trong ~53 phiên (2026-06-05 → 2026-08-20), chỉ tính 40 mã ta đã chạm ⇒
**≈1 sự kiện mỗi 2,4 phiên**. Không phải ca hiếm.

⚠️ **Một tham số phải nhập tay**: `corporate_action` có `exercise_ratio` nhưng **không có giá phát
hành quyền mua**. Số 10.000đ của MBB lấy từ công bố của MBB và được xác nhận ngược bằng chính kết
quả (20.200 khớp tuyệt đối ảnh chụp app). Script giữ nó trong `RIGHTS_ISSUE_PRICE` và **in cảnh
báo** cho mã thiếu, không lặng lẽ coi như 0. Bản vá thật sẽ cần nguồn cho tham số này (hoặc
fail-closed khi thiếu) — ghi ra đây để không bị bỏ quên.

---

## 5. Bằng chứng THỰC TẾ — đã sai ở đâu, chưa sai ở đâu

### 5.1 Tiền THẬT: 0 thiệt hại, và biết chính xác vì sao

Quét toàn bộ `data/execution_logs/dnse_raw_*.jsonl` (43 file, 2026-06-15 → 2026-08-14),
**745 bản ghi `place_order`** (SpaceX 546, ZaloPay 199), 40 mã. Giao với 25 sự kiện làm-đổi-giá:

```
2026-08-11T09:15:06  ZaloPay  buy MBB  400cp @ 20.550
2026-08-11T09:15:08  SpaceX   buy MBB  300cp @ 20.550
```

Đúng **2 lệnh**, cùng một mã, cùng một ngày. Tham chiếu sở công bố hôm đó = 20.200; cả
`park_add_{SpaceX,ZaloPay}_2026-08-11.json` lẫn `plan_{SpaceX,ZaloPay}_2026-08-11.json` đều ghi
`ref_price = 20.200`; đặt 20.550 (đuổi trong biên). **Đúng hệ quy chiếu mới ⇒ không sai đồng nào.**

**Nhưng lý do đúng là ngẫu nhiên**: hai lệnh này đến từ `compute_park_add.py` (P2 park-sync) chạy
trong lượt `apply_cash_redesign_20260811.py` **sáng 08-11**, tức SAU cú lật 00:41. Artifact
`park_trim_SpaceX_2026-08-11.json` cũng có `mtime 08-11 02:11` (không phải 08-10 tối). Nếu chúng
đi qua dây chuyền cron tối 08-10 (19:04-20:30) như mọi ngày khác, chúng đã đứng ở hệ quy chiếu CŨ
24.150 — lệch **+19,6%** so với 20.200.

### 5.2 Paper: ĐÃ SAI THẬT, hai lần, cùng một chỗ

`plan_main_*.json` (account paper `main`, sinh bởi `paper_main_probe_plan.py` cron 08:52 ICT):

| Plan | Ngày = GDKHQ của | `ref_price` dùng | Tham chiếu đúng | Lệch |
|---|---|---:|---:|---:|
| `plan_main_2026-07-09.json` | MBB (tiền 1.000) | 26.000 | 25.000 | **+4,0%** |
| `plan_main_2026-08-11.json` | MBB (CP 15% + quyền mua) | 24.250 | 20.200 | **+20,0%** |

`plan_main_2026-08-11.json` có `created_at = 2026-08-11T08:52:01` — **sinh ĐÚNG SÁNG ngày GDKHQ**
mà vẫn mang giá 24.250, vì nguồn của nó là `Close` trong cache parquet (dòng C ở §1), một hệ quy
chiếu hoàn toàn khác. Đây là **bằng chứng đang tồn tại rằng cơ chế hỏng đúng như mô tả** — chỉ
tình cờ nằm ở account paper nên không mất tiền.

### 5.3 Sự cố ĐÃ CÓ, chứng minh cùng một gốc

MBB 2026-08-11, `verify_account_snapshot.dnse_close_prices`: `close_price` boardId=G1 trả 24.250
(phiên 08-10, hệ CŨ) trong khi `openQuantity` broker đã là hệ MỚI ⇒ **SpaceX +5.013.250đ (~0,5%
NAV)**. **User bắt được bằng ảnh chụp app DNSE, không phải bằng cảnh báo của hệ thống.**
(`mike/bin/exrights_price_basis_selfcheck.py`, commit `197404ea`/`4367b0ef`.)

⇒ Bản vá đó đã đóng **tầng NAV**. Nó **không** đóng tầng đặt lệnh, và nó vá **một call-site**, đúng
kiểu §28 `coding_guidelines` cảnh báo là chặn được ca đó nhưng không chặn được ca thứ 7 ở chỗ khác.

---

## 6. Hai lỗ tôi cho là dễ bị bỏ qua nhất

### 6.1 `lag_entry_anchor.py` — đúng bẫy cũ, hở bẫy mới

File này **cố ý** dùng `Price` (thô) và cấm `Close`, với lý do viết rõ 20 dòng ở docstring: `Close`
hồi tố nên trộn hệ quy chiếu với giá live. **Lý do đó đúng.** Nhưng nó chỉ miễn nhiễm với *hiện
vật hồi tố*, **không** miễn nhiễm với *lệch hệ quy chiếu qua một ngày GDKHQ*:

> anchor lấy từ phiên chuẩn (cum, hệ CŨ) → đem so với giá live của phiên sau GDKHQ (hệ MỚI).

Anchor là **TRẦN** ⇒ anchor ở hệ cũ **CAO hơn** ⇒ **trần nới lỏng, không siết**. Với SSI (−20,0%)
một anchor phiên 08-14 đem dùng cho phiên 08-17 sẽ nới trần **+25%** — tức cơ chế trần coi như tắt.
Docstring khẳng định *"`Price` không hồi tố nên miễn nhiễm"*; câu đó đúng cho bẫy nó đang nói tới
và **sai cho bẫy này** — cần sửa cả câu chữ lẫn code.

Cộng thêm bẫy §1.1: nếu phiên chuẩn rơi ĐÚNG vào ngày GDKHQ, `Price` của dòng đó có thể là giá
phiên trước (ca VHM 08-06 lệch hệ số 2,0).

### 6.2 `merge_park_orders.py` — cú lật bị nuốt như nhiễu giá

`merge_park_orders.py:345-354`: khi `ref_price` của L1 (`park_trim`) khác L2 (`jit_unpark`), code
**cảnh báo rồi lấy giá THẤP HƠN** và đi tiếp — quyết định hợp lý cho nhiễu giá thường (bài học
08-06: lệch nhỏ không đáng dừng cả plan). Nhưng §3 cho thấy L1 chạy 19:04 và L2 chạy 19:40 có thể
**đứng hai bên cú lật**. Lúc đó chênh L1/L2 **không phải nhiễu** — nó là hai hệ quy chiếu, và
"lấy giá thấp hơn" chọn đúng giá hệ MỚI (may) trong khi `qty` vẫn là của L1 hệ CŨ (rủi).

**Điều này đã xảy ra ngày 2026-08-14** với BID (L1 lúc 19:04:15 hệ cũ, cú lật 19:10, L2/merge sau
đó). Không gây hại vì L1 hôm đó ra 0 lệnh — nhưng cơ chế đã kích hoạt thật, không phải giả thuyết.

### 6.3 Nhánh luật B của TV1 (`discretionary_accumulation_inject.py`)

Job trước vá **luật A** sang `q.ref` và **cố ý không chạm luật B** (trung bình 5 giá ĐÓNG) — đúng,
vì đó là đại lượng khác. Nhưng luật B lấy 5 giá đóng quá khứ (hệ CŨ) làm neo cho phiên sau GDKHQ
(hệ MỚI) ⇒ **cùng lỗi hệ quy chiếu như §6.1**. TV1 không có sự kiện sắp tới, nên đây là rủi ro
tiềm ẩn chứ không cấp bách — nhưng nó nằm trong cùng một bản vá, không nên tách.

---

## 7. Cơ chế phát hiện GDKHQ đang có — đủ tổng quát để tái dùng không?

| Cơ chế | Là gì | Đủ dùng làm cổng cho đặt lệnh? |
|---|---|---|
| `data/corp_actions.json` | **Sổ tay 3 record** (VHM/MBB/BID), phải có ≥2 nguồn độc lập + user ký duyệt; chỉ mô tả sự kiện **làm ĐỔI SỐ LƯỢNG CP** | ❌ **Không.** Cố ý hẹp: cổ tức TIỀN MẶT không thuộc file này, mà tiền mặt chiếm **16/25** sự kiện §4. Lại là quy trình thủ công có người ký ⇒ không thể là cổng chạy mỗi đêm |
| `tav2_bq.corporate_action` + `corp_action_lib.is_price_adjusting()` | Bảng vendor, có `exright_date`, `event_code`, `issue_method_name_vi`, `exercise_ratio`, `value_per_share`; hàm phân loại sẵn | ✅ **CÓ — đây là thứ cần tái dùng.** Phủ CẢ tiền mặt lẫn cổ phiếu, có sẵn lịch tương lai (BID/MBS/SSI 08-17, VIX 08-20 đều đã ở trạng thái `announced`) |
| `corp_action_daily.py` / `.sh` | Cron cảnh báo T-N, đối soát, backfill phiên lỡ, snapshot | ⚠️ **CẢNH BÁO SUÔNG.** Đọc hết 1.736 dòng: nó phát hiện/đối soát/thông báo, **không điều chỉnh một con số nào dùng cho đặt lệnh**, và không có consumer nào ở đường sizing đọc output của nó |
| `mike/bin/exrights_price_basis_selfcheck.py` | Regression cho **tầng NAV** | ⚠️ đúng nguyên lý (*"không cần biết mã nào có sự kiện gì, chỉ cần biết giá đang cầm thuộc phiên nào"*) nhưng chỉ phủ 1 hàm |

⚠️ Cảnh báo dùng `corporate_action`: `event_status` của sự kiện tương lai là **`announced`**, chỉ
đổi sang `executed` trong lần reload ~22:2x ICT **của chính ngày sự kiện** (bug thật, quant-skeptic
REFUTED vòng 1, ghi ở `corp_action_daily.py:422-437`). ⇒ Cổng mới **PHẢI** lọc `!= "not_executed"`,
**tuyệt đối không** lọc `== "executed"`, nếu không nó trả rỗng mỗi ngày và im lặng.

---

## 8. THIẾT KẾ ĐỀ XUẤT — tối thiểu, tái dùng, fail-closed

> Nguyên tắc dẫn đường, rút từ §3: **đừng đi tìm "nguồn giá đúng" — hãy cưỡng chế "một hệ quy
> chiếu duy nhất".** Sai không nằm ở nguồn nào xấu, mà ở chỗ hai số trong cùng một phép tính đến
> từ hai phiên khác nhau. Đây cũng đúng nguyên lý bản vá NAV 08-11 đã dùng, chỉ nâng từ 1 hàm lên
> cả tầng.

### D1 · `price_frame.py` — MỘT hàm thuần, trả về "số này thuộc phiên nào"

Tái dùng thẳng `check_reference_snapshot()` + `official_reference_price()` đã build ở job trước
(`trading_bot/no_chase_ceiling.py`, `mike/bin/discretionary_accumulation_inject.py`).

```
resolve_reference(ticker, session_date) -> {
    ref_price,            # q.ref của DNSE — nguồn ĐÚNG DUY NHẤT cho phiên có sự kiện
    frame_session,        # phiên mà con số này thuộc về
    ex_today: bool,       # từ tav2_bq.corporate_action + is_price_adjusting()
    ok: bool, reason: str
}
```

Ba cổng G1/G2/G3 của job trước **áp nguyên** (sàn xác định được / biên độ khớp sàn / tham chiếu ∈
[Low,High] phiên trước). Bổ sung **G4 mới, sinh ra từ §3**:

> **G4 — bất biến ĐỒNG-HỆ.** Với mã có `ex_date` ∈ {hôm nay, phiên kế tiếp}: mọi lô của cùng một
> mã trong CÙNG bản đọc `positions` phải có **cùng một `marketPrice`**. Khác nhau ⇒ đang bắt được
> DNSE giữa cú lật ⇒ **fail-closed, không sinh lệnh cho mã đó**.

G4 rẻ (một phép so trên dữ liệu đã đọc sẵn), và nó là **cổng DUY NHẤT** bắt được ca 19:10:23 —
G1/G2/G3 đều mù với nó vì mỗi lô riêng lẻ đều tự nhất quán.

Bổ sung **G5**: `q.ref` phải khớp công thức sở giao dịch dựng lại từ `corporate_action`
(`(P_cum − tiền_mặt + r×giá_phát_hành)/(1+r)`, làm tròn bước giá) trong dung sai 1 bước giá. §1.2
cho thấy công thức này khớp **tuyệt đối 2/2 ca** (MBB 20.200, SSI 19.600) ⇒ đây là phép **đối soát
chéo hai đường dữ liệu độc lập** (feed DNSE vs bảng vendor BQ), không phải tự tính lại rồi tin.

### D2 · Cổng ở tầng SINH PLAN, không rải khắp nơi

Chèn **một** cổng vào dây chuyền tối, đọc `corporate_action` một lần cho toàn bộ mã ứng viên:

- Mã có `exright_date == plan_date` (hoặc `== today` khi chạy trong phiên) ⇒
  1. `ref_price` **BẮT BUỘC** lấy từ `resolve_reference()` (`q.ref`), cấm mọi nguồn HIST;
  2. `qty` tính lại trên chính `ref_price` đó (không tái dùng qty tính ở giá cũ);
  3. `hard_no_chase_ceiling_vnd` dựng lại trên `ref_price` đó;
  4. mọi anchor lịch sử (`lag_entry_anchor`, luật B của TV1) **quy đổi về hệ mới** bằng hệ số từ
     `corporate_action`, **hoặc** — nếu không quy đổi được chắc chắn — **bỏ mã đó khỏi plan**.
- Không xác định được `exright_date`, hoặc `resolve_reference` fail bất kỳ cổng nào ⇒
  **KHÔNG sinh lệnh cho mã đó**, ghi lý do vào `notes[]`. (Giữ đúng triết lý job trước: không
  đoán, không rơi về mặc định.)

### D3 · Đóng lại 3 chỗ cụ thể

| # | Chỗ | Sửa |
|---|---|---|
| 1 | `strategies.py:_price()` fallback #2 (`recs_close`) | Chặn fallback HIST khi `ex_today` — thà không có giá còn hơn giá sai hệ |
| 2 | `merge_park_orders.py:345-354` | Lệch L1/L2 vượt ngưỡng **VÀ** mã có sự kiện trong cửa sổ ⇒ **CHẶN mã đó** thay vì "lấy giá thấp hơn + cảnh báo". Nhiễu giá thường giữ nguyên hành vi cũ |
| 3 | `paper_main_probe_plan.py:latest_closes()` | Paper, nhưng là **bằng chứng đang sai** (§5.2) và là harness sinh evidence cho R&D ⇒ sửa để evidence không nhiễm |

### D4 · Đổi giờ cron? **KHÔNG** — và đây là điểm dễ chọn sai

Cám dỗ tự nhiên là "dời `park_trim` từ 19:04 xuống sau 19:30 cho qua cú lật". §3.1 bác bỏ: ba sự
kiện lật ở **ba giờ khác nhau** (T-1 trưa / T-1 19:10 / qua đêm 00:41). Không có giờ nào an toàn.
Dời giờ = đổi xác suất trúng, không đổi cơ chế — và tệ hơn, nó **giấu** vấn đề đi. Cổng G4 kiểm
hệ quy chiếu **tại chỗ** mới là thứ đúng.

### D5 · Điều KHÔNG làm trong bản vá này

- **Không** tự tính lại giá tham chiếu để thay `q.ref`. Công thức chỉ dùng để **đối soát** (G5),
  đúng vai như job trước đã chốt (phương án B là vật đối soát, không phải nguồn).
- **Không** đụng `pt_v23_audit_2014.py` / nền backtest. Lỗ §2 là lỗ của tầng ĐỐI CHIẾU
  paper↔broker, sửa ở `build_plan`, không phải sửa mô phỏng.
- **Không** mở rộng `data/corp_actions.json`. Nó là sổ có-người-ký cho sự kiện đổi SỐ LƯỢNG; ép
  nó gánh thêm vai lịch giá là phá đúng cái tính chất làm nó đáng tin.

---

## 9. Việc cần làm tiếp (lượt dispatch sau, sau khi Mike/user xem thiết kế)

1. Code hoá D1-D3 + selfcheck, có **ca chứng minh ngược**: dựng lại đúng bản đọc 19:10:23 của BID
   và yêu cầu G4 chặn; dựng lại `plan_main_2026-08-11` và yêu cầu cổng bắt 24.250.
2. Chạy scope map `bin/selfcheck_scope_map.sh` — D3#1 chạm `strategies.py`, có thể là module lõi.
3. Hồi quy trên kho plan thật: xác nhận **0 lệnh đổi giá trị** ở ngày KHÔNG có sự kiện (bất biến
   "không đổi hành vi ngày thường"), đúng cách job trước đã làm.
4. Báo Winston 2 việc dữ liệu: (a) bẫy `ticker.Price` ở dòng ngày GDKHQ (§1.1, ca VHM 08-06) — bổ
   sung `kb/data_registry/price-volume/`; (b) hỏi bq_admin đây là lỗi ingest hay quy ước.
5. Mốc gần nhất để quan sát tự nhiên: **2026-08-17** (BID ×1,068 — ĐANG GIỮ cả 2 account; MBS
   −5,4%; SSI −20,0%) và **2026-08-20** (VIX −4,8%). Plan 08-17 hiện chỉ có 1 lệnh TV1, không chạm
   mã nào trong số đó ⇒ **không cần hành động khẩn cấp**, nhưng đây là dịp đo cú lật lần thứ tư.

---

## Tái lập

```bash
cd /home/trido/thanhdt/WorkingClaude
python3 mike/agents/Taylor/research/exdate_order_pipeline_20260815/scan_exdate_orders.py
```

Dữ liệu trung gian: `data/real_orders.json` (745 lệnh thật), `data/corp_events.csv` (30 sự kiện,
25 làm-đổi-giá).
